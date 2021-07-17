# 当Bcrypt与其他Hash函数同时使用时造成的安全问题

0x00 前言
=======

* * *

php在5.5版本中引入了以bcrypt为基础的哈希函数password_hash，和其对应的验证函数password_verify，让开发者轻松实现加盐的安全密码。本文就是围绕着password_hash函数讲述作者发现的安全问题。

有一次，我在StackOverflow上看到个有趣的问题：当密码位数过长的时候，password_verify()函数是否会被DOS攻击？很多哈希算法的速度都受到数据的量的影响，这将导致DOS攻击：攻击者可以传入一个非常长的密码，来消耗服务器资源。这个问题对于Bcrypt和PasswordHash也很有意义。我们都知道，Bcrypt限制密码的长度在72个字符以内，所以在这点上它不会被影响的。但我选择进行深入挖掘的时候，却发现了其他令我惊讶的问题。

0x01 crypt.c分析
==============

* * *

首先我们看看php是怎么实现crypt()函数的，这个我们感兴趣的函数在源码中对应“php_crypt()”，声明如下：

```
PHPAPI zend_string *php_crypt(const char *password, const int pass_len, const char *salt, int salt_len)

```

我们看看进行加密的部分

```
} else if (
        salt[0] == '$' &&
        salt[1] == '2' &&
        salt[3] == '$') {
    char output[PHP_MAX_SALT_LEN + 1];

    memset(output, 0, PHP_MAX_SALT_LEN + 1);

    crypt_res = php_crypt_blowfish_rn(password, salt, output, sizeof(output));
    if (!crypt_res) {
        ZEND_SECURE_ZERO(output, PHP_MAX_SALT_LEN + 1);
        return NULL;
    } else {
        result = zend_string_init(output, strlen(output), 0);
        ZEND_SECURE_ZERO(output, PHP_MAX_SALT_LEN + 1);
        return result;
    }
}

```

注意到了吗？由于password变量一个是char指针（char *)，所以php_crypt_blowfish_rn()并不能知道参数password的长度。我想看看他是怎么获得长度的。

跟进php_crypt_blowfish_rn()，我发现唯一使用password变量（函数里叫key）的地方，是把它传给了 BF_set_key()函数。这个函数的注释中说明了一些设置和安全使用事项，实际上总结起来就是下面这个循环（去除了注释）：

```
const char *ptr = key;
/* ...snip... */
for (i = 0; i < BF_N + 2; i++) {
    tmp[0] = tmp[1] = 0;
    for (j = 0; j < 4; j++) {
        tmp[0] <<= 8;
        tmp[0] |= (unsigned char)*ptr; /* correct */
        tmp[1] <<= 8;
        tmp[1] |= (BF_word_signed)(signed char)*ptr; /* bug */
        if (j)
            sign |= tmp[1] & 0x80;
        if (!*ptr)
            ptr = key;
        else
            ptr++;
    }
    diff |= tmp[0] ^ tmp[1]; /* Non-zero on any differences */

    expanded[i] = tmp[bug];
    initial[i] = BF_init_state.P[i] ^ tmp[bug];
}

```

给不懂C语言的人：_用来解引用指针，也就是返回这个指针指向的值。所以我们定义char *abc = ”abc”，那么_abc的值就是’a’（事实上是’a’的ascii码值）。当你执行了abc++以后*abc的值就等于’b’。这就是C语言中字符串string的工作原理。

接着看，这个循环会迭代72次（因为BF_N等于16），每次迭代会“吃掉”字符串的一个字符。

那么看以下代码：

```
if (!*ptr)
    ptr = key;
else
    ptr++;

```

如果*ptr的值为0，那么重新让它指向字符串的首字符，依此规则循环，执行72次。这就是为什么传入的字符串要小于72个字符（因为C语言字符串是以NUL结尾，所以要占用一个字节）。

那我们来想想，以上代码意味着”test\0abc”将会被处理成”test\0test\0test\0test\0test\0test\0test\0test\0test\0test\0test\0test\0test\0test\0te”。实际上，所有以”test\0”开头的字符串都会被处理成这样。

结果就是，它忽略了第一个NUL以后的所有内容（test\0abc中的abc）。

这样会产生什么问题呢？很明显，你的密码变短了（从test\0abc变成test\0）。但因为没有人会在密码中使用“\0”，那么它是不是不算问题了？

事实上，的确没人会在密码中使用“\0”，所以如果你单独使用password_hash()或crypt()的时候，你是100%安全的。 但如果你不是直接使用他们，而是进行了“预哈希”（pre-hash），那你就会遇到本文中说的主要问题。

0x02 主要问题
=========

* * *

有些同学觉得单独使用bcrypt不够，而是选择去”预哈希（pre-hash）”，也就是预先计算一次哈希，再把返回结果传入正式的哈希函数进行计算。

这样可以让用户去使用“更长”的密码（超过72个字符），如：

```
password_hash(hash('sha256', $password, true), PASSWORD_DEFAULT)

```

另外，也有些同学想给哈希加点“salt”，所以配合私钥使用HMAC：

```
password_hash(hash_hmac('sha256', $password, $key, true), PASSWORD_DEFAULT)

```

问题在于，以上用法中hash和hash_hmac函数的最后一个参数传入的都是true，它强制函数返回原始（二进制）数据。使用原始数据而非编码后的数据，再次计算哈希，这种做法在加密函数中是很常见的。这样做可以在你把sha512加密后128位的数据截断成72位而失去熵的同时，也还能多留一些熵。

但这意味着第一次哈希函数输出的内容中，可以含有“\0”。而且有高达近1/256（0.39%）的可能性第一位是”\0”（这时候你的密码等于变成了一个空字符串）。那么我们只需要去尝试大概177次密码，就有50%的机会获得一个第一位是NULL字符的密码，等于大概177个用户就有50%的概率使用了一个NULL开头的密码。所以我们尝试31329（177 * 177）个账号和密码的组合就有25%的概率成功登录一个账户。这给在线碰撞哈希提供了可能（如：通过分布式的方式）。

这真是糟糕透了。

我们来看一个利用上述方法碰撞账号密码的例子：

```
$key = "algjhsdiouahwergoiuawhgiouaehnrgzdfgb23523";
$hash_function = "sha256";
$i = 0;
$found = [];

while (count($found) < 2) {
    $pw = base64_encode(str_repeat($i, 5));
    $hash = hash_hmac($hash_function, $pw, $key, true);
    if ($hash[0] === "\0") {
        $found[] = $pw;
    }
    $i++;
}

var_dump($i, $found);

```

我选择了一个随机的$key，然后我用一个看似“随机”的密码$pw（其实是5个重复字符进行base64编码后的值），然后开始跑。这段傻傻的代码开始进行碰撞（效率比较低）。最后获得了如下结果：

```
int(523)
array(2) {
  [0]=>
  string(16) "MzEzMTMxMzEzMQ=="
  [1]=>
  string(20) "NTIyNTIyNTIyNTIyNTIy"
}

```

我们在523次尝试中碰撞出了2个密码“MzEzMTMxMzEzMQ==”和“NTIyNTIyNTIyNTIyNTIy”，尝试的次数将会随着密钥的改变而改变。 然后我们做以下实验：

```
$hash = password_hash(hash_hmac("sha256", $found[0], $key, true), PASSWORD_BCRYPT);
var_dump(password_verify(hash_hmac("sha256", $found[1], $key, true), $hash));

```

得到如下输出：

```
bool(true)

```

十分有趣。两个不同的密码却被认为是同一个hash，我们的哈希碰撞奏效了。

0x03 检测有问题的哈希值
==============

* * *

我们可以用如下方法简单地测试我们的哈希值是否是NULL字符开头的：

```
password_verify("\0", $hash)

```

比如，我们测试下面的哈希：

```
$2y$10$2ECy/U3F/NSvAjMcuBeI6uMDmJlI8t8ux0pXOAoajpv2hSH0veOMi

```

返回结果为bool(true)，说明它是由首字符为NULL的字符串加密得到的。

所以，在离线情况下，只用一行的代码即可检测这个问题。

另外，就算你计算二次哈希值的字符串不是以NULL字符开头，也不代表你绝对的安全（假设你使用了上述有缺陷的加密算法）。当第二个字符是NUL的时候，同样的事情也可能发生：

```
a\0bc
a\0cd
a\0ef

```

这些都是可以碰撞的，你将会有0.39%的概率碰撞到第二个字符是\0的结果。在所有首字母为a的字符串中，你也将有0.39%的概率获得一个第二个字符是\0的结果。这意味着我们的破解密码的工作量从碰撞整个字符串哈希变成了只用碰撞以上很短的字符串。 这个问题将一直延续下去（第3个字符是\0、第4个、第5个……）。

有些人说我并未使用password_hash，我用了CRYPT_SHA256！

看到源码中的php_crypt()函数，我们可以发现crypt()中所有加密方式都有这样的行为，它并不仅存在于bcrypt，也不仅集中于php，整个crypt(3) C语言库都有这个问题。

我在文中主要使用bcrypt来说明问题的原因是password_hash()调用了它，而password_hash是当前PHP推荐的加密算法。

值得注意的是，如果你使用了hash_pbkdf2()，就不容易被影响，而使用的是scrypt库会更好。

0x04 修复方法
=========

* * *

这个问题不是出在bcrypt，而是同时使用了bcrypt与其他加密方式造成的。事实证明，也并不是所有组合都是不安全的。《Mozilla's system》里提到的方式password_hash(base64_encode(hash_hmac("sha512", $password, $key, true)), PASSWORD_BCRYPT) 是安全的，因为它在获得了hash_hmac的返回值后进行了base64编码。另外，如果hash/hmac返回值是hex形式的话你也是安全的（最后一个参数是默认的false）。

如果你按以下说明去做，你就是100%安全的：

*   1.直接使用bcrypt加密（而不去pre_hash）
*   2.使用hex形式的值作为pre_hash的参数
*   3.使用base64编码后的值作为pre_hash的参数

总之，要不就不要pre_hash，要不就编码后再进行pre_hash。

0x04 根本问题
=========

* * *

根本问题就是加密算法最初就不是为同时使用而设计的。同时使用多个加密算法会让开发者觉得安全，但实际上并不是，上述问题只是这种错误做法的一个体现。

所以，我们应该按照算法设计者预想的方式去使用他们。如果你想在bcrypt上再加强防御，那就加密它的输出结果：

```
encrypt(password_hash(...), $key)。

```

最后，也是最最重要的是：绝不要发明自己的加密算法，否则会导致致命后果。

原文：http://blog.ircmaxell.com/2015/03/security-issue-combining-bcrypt-with.html?m=1