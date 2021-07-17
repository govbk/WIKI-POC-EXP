# WordPress < 3.6.1 PHP 对象注入漏洞

From:[WordPress < 3.6.1 PHP Object Injection](http://vagosec.org/2013/09/wordpress-php-object-injection/)

0x00 背景
-------

* * *

当我读到一篇关于Joomla的“PHP对象注射”的漏洞blog后，我挖深了一点就发现Stefan Esser大神在2010年黑帽大会的文章：

[http://media.blackhat.com/bh-us-10/presentations/Esser/BlackHat-USA-2010-Esser-Utilizing-Code-Reuse-Or-Return-Oriented-Programming-In-PHP-Application-Exploits-slides.pdf](http://media.blackhat.com/bh-us-10/presentations/Esser/BlackHat-USA-2010-Esser-Utilizing-Code-Reuse-Or-Return-Oriented-Programming-In-PHP-Application-Exploits-slides.pdf)

这篇文章提到了PHP中的unserialize函数当操作用户生成的数据的时候会产生安全漏洞。

所以呢，基本来说，unserialize函数拿到表现为序列化的数据，然后就解序列化它（unserialize嘛，当然就干这个啊~）为php的值。这个值它可以是resource之外的任何类型，可为（integer, double, string, array, boolean, object, NULL），当这个函数操作一个用户生成的字符串的时候，在低版本的PHP中可能会产生内存泄露的漏洞，当然这也不是这篇blog要关注的问题。如果你对这个问题感兴趣，你可以再去看看我上面说的大神的文章。

另外一种攻击方式发生在当攻击者的输入被unserialize函数操作的时候，这种就是我说到的“PHP对象注入”。在这种方式中，对象类型的被unserialize的话，允许攻击者设置他选择对象的属性。当这些对象中的方法被调用的时候，会出现一些效果（例如：删除一些文件），当攻击者可以去选择对象里的一些属性的时候，他就能够删除一个他所提交的文件。

让我们举个例子吧，想象以下的代码中的class是用户自己生成的内容被unserialize时载入的：

（ps:老外贴出的代码语法有问题，改了一下测试成功……）

```
<?php
class Foo {
    private $bar; 
    public  $file;

    public function __construct($fileName) {
        $this->bar = 'foobar';
        $this->file = $fileName;
    }

    // 一些其他的代码……

    public function __toString() {
        return file_get_contents($this->file);
    }
} 
?>

```

如果受害的缺陷代码同时还存在以下的代码：

```
echo unserialize($_GET['in']);

```

这攻击者就可以读取任意文件，攻击者可以如下去构造它的对象。

```
<?php
class Foo {
    public $file;
}
$foo = new Foo();
$foo->file = '/etc/passwd';
echo serialize($foo); 
?>

```

上面这段代码的结果是：O:3:"Foo":1:{s:4:"file";s:11:"/etc/passwd";} ，攻击者现在要做的事情就事通过提交get请求到存在漏洞的页面触发他的攻击代码。这个页面会吐出/etc/passwd的内容来。能读到这些文件的内容怎么看都不是一个好事情，你就想象一下，万一缺陷代码中的函数不是file_get_contents而是eval呢？

我相信上面这部分已经能让人明白允许用户输入进入unserialize这个函数危害有多大了。就连PHP手册里也说了不要把用户生成的内容交给unserialize函数。

### 警告：

不要把不可信的用户输入交给unserialize，使用该函数解序列化内容能导致访问且自动载入对象，恶意用户可以利用这一点，从安全的角度，如果你想让用户可以标准的传递数据，可以使用json （json_encode json_decode）。

好，让我们继续说这些问题怎么影响到Wordpress。

0x01 wordpress的安全问题
-------------------

* * *

Stefan Esser's的黑帽演讲中，他提到Wordpress是一款使用了serialize和unserialize函数的知名应用。在他的幻灯片中，unserialize用来接收来自Wordpress站点上的数据。所以攻击者可以在受害站点上发起一次中间人攻击。他可以修改来自Wordpress站点的返回数据，把他的代码加进去。有趣的是就在我编写这篇文章的时候，Wordpress最新的版本也包含这个问题（距离那演讲似乎过去三年了），想象一下，如果有黑客可以劫持WordPress.org的DNS会发生什么事情吧。

然而，这也不是Wordpress使用这个unserialize的唯一地方，它还用于用于在数据库中数据。举例来说，用户的metadata就被序列化后存储在数据库中，metadata的取回方式在wp-includes/meta.php的272行的get_metadata()，我在这里引用一下该函数的部分代码（292-297行）

```
if ( isset($meta_cache[$meta_key]) ) {
    if ( $single )
        return maybe_unserialize( $meta_cache[$meta_key][0] );
    else
        return array_map('maybe_unserialize', $meta_cache[$meta_key]); 
}

```

基本上，这个函数所干的事情就是取回数据库里的metadata（它来自每篇文章或用户输入），数据在数据库中的wp_postmeta和wp_usermeta表中，有些数据是被序列化的而有些没有被序列化，所以maybe_unserialize()函数替代了unserialize()在这里操作，这个函数在wp-includes/functions.php的230到234行之间被定义。

```
function maybe_unserialize( $original ) {
    if ( is_serialized( $original ) ) //序列化的数据才会走到这里面
        return @unserialize( $original );
    return $original; 
}

```

所以，这个函数干的事情是检查给予它的值是不是一个序列化的数据，如果是的话，就解序列化。这里用来判断是否是序列化所使用的函数是is_serialized()，它的定义在同文件的247到276行之间。

```
function is_serialized( $data ) {
    // 如果连字符串都不是，那就不是序列化的数据了
    if ( ! is_string( $data ) )
        return false;
    $data = trim( $data );
     if ( 'N;' == $data )
        return true;
    $length = strlen( $data );
    if ( $length < 4 )
        return false;
    if ( ':' !== $data[1] )
        return false;
    $lastc = $data[$length-1];
    if ( ';' !== $lastc && '}' !== $lastc )
        return false;
    $token = $data[0];
    switch ( $token ) {
        case 's' :
            if ( '"' !== $data[$length-2] )
                return false;
        case 'a' :
        case 'O' :
            return (bool) preg_match( "/^{$token}:[0-9]+:/s", $data );
        case 'b' :
        case 'i' :
        case 'd' :
            return (bool) preg_match( "/^{$token}:[0-9.E-]+;\$/", $data );
    }
    return false;
}

```

WordPress检查一个值是否是序列化的字符串为什么那么重要的原因马上要变得清晰了。首先，我们看一下一个攻击者如何把他的内容最终加入到metadata表中的。每个用户的姓名，雅虎IM都存储在wp_usermeta表里。所以我们把自己的恶意代码加在那我们就可以搞掂掉WordPress，对不对？你可以试试在你该写名字的地方写个i:1试试，如果这个没有被解序列化那这里只会返回一个我们输入的i:1。

麻痹的，看来要发几个大招才可以搞掂WordPress啊。让我们挖得再深一点，看看为什么这个东西就没有给解序列化。在 wp-includes/meta.php 中，这个update_metadata() 函数定义在101-164行，这里有这个函数的部分代码。

```
// …
    $meta_value = wp_unslash($meta_value);
    $meta_value = sanitize_meta( $meta_key, $meta_value, $meta_type );
// …
    $meta_value = maybe_serialize( $meta_value );

    $data  = compact( 'meta_value' );
// …
    $wpdb->update( $table, $data, $where );
// …

```

这里maybe_serialize函数可能能解释为什么我们刚才的操作没成功，我们再跟进去看看这个函数，它定义在wp-includes/functions.php的314-324行。

```
function maybe_serialize( $data ) {
    if ( is_array( $data ) || is_object( $data ) )
        return serialize( $data );
    // 二次序列化是为了向下支持
    // 详见 http://core.trac.wordpress.org/ticket/12930
    if ( is_serialized( $data ) )
        return serialize( $data );

    return $data; 
}

```

所以当我们传入一个序列化的值的话，它就会再序列化一下，这就是现在发生的情况，你看，数据库里的东西不是i:1;而是s:4:"i:1;";，当解序列化的时候它就显示为一个字符串，那现在该怎么办呢？

你懂的，这帖子的内容也存在数据库里，上面这就说明了为什么我们失败了。如果我们现在想往数据库插一个序列化后的东西，我们就需要在我们插入数据的时候让is_serialized()这个函数返回一个false，而当我们再从数据里取它的时候，它就应该返回个true了。

你懂的，Mysql数据库，表和字段都有他们自己的charset和collation(字符集和定序）。WordPress呢，默认的字符集是UTF-8。从这个名字就看的出来，这个字符集它不支持全部的Unicode字符，你要是对这个感兴趣，你可以看看Mathias Bynens的这篇文章：http://mathiasbynens.be/notes/mysql-utf8mb4，这文章教了我UTF-8的表储存不了Unicode编码区间是U+010000到U+10FFFF的字符。所以当我们在这个情况下尝试保存这些字符呢？显而易见，包括这个字符和这个字符之后的内容都会被忽略掉。所以在我们尝试插入`foo{0xf09d8c86}bar`的时候，Mysql会忽略`{0xf09d8c86}bar`而保存为foo。

这个迷题的最后一部分就是我们需要插入一个用以一会儿解序列化的内容，为了测试这个，你可以插入`1:i{0xf09d8c86}`为你的名字。正如所见到的，结果是1，意味着你的输入被解序列化了，如果你还不相信我，你试着输入一个空数组的序列化并且以该字符结尾：`a:0:{}{0xf09d8c86}`。这个结果是Array。

让我们继续`maybe_serialized('i:1;{0xf09d8c86}')`插入了数据库。WordPress不认为这是一个已序列化的数据，因为它不是;或者}结尾的。它会返回`i:1;{0xf09d8c86}`，当插入数据库的时候，它的值是i:1，当它从数据库取回的时候，它有了;最为最后一个字符，所以它可以解序列化成功。碉堡了。漏洞。

0x02 WordPress 利用
-----------------

* * *

现在我们展示了WordPress存在PHP对象注入漏洞。让我们尝试利用它。所以为了利用该漏洞（通过注入对象的方法），我们需要找到一个符合以下条件的class：

1，内有“有用”的方法可被调用。 2，存在该对象的类已经被包含了。

当一个对象被解序列化的时候，__wakeup函数会被调用，这被称作PHP的魔术方法，这也是我们确定会被调用的方法，实际上这些函数会更多写些，我写了一个以下的class来获取被调用的class到/tmp/fumc.log。

```
<?php
class Foo {
    public static function logFuncCall($funcName) {
        $fh = fopen('/tmp/func.log', 'a');
        fwrite($fh, $funcName."\n");
        fclose($fh);
    }
    public function __construct() { Foo::logFuncCall('__construct('.json_encode(func_get_args()).')');}
    public function __destruct() { Foo::logFuncCall('__destruct()');}
    public function __get($name) { Foo::logFuncCall("__get($name)"); return "Foo";}
    public function __set($name, $value) { Foo::logFuncCall("__set($name, value)");} 
    public function __isset($name) { Foo::logFuncCall("__isset($name)"); return true;} 
    public function __unset($name) { Foo::logFuncCall("__unset($name)");} 
    public function __sleep() { Foo::logFuncCall("__sleep()"); return array();} 
    public function __wakeup() { Foo::logFuncCall("__wakeup()");} 
    public function __toString() { Foo::logFuncCall("__toString()"); return "Foo";} 
    public function __invoke($a) { Foo::logFuncCall("__invoke(". json_encode(func_get_args()).")");}
    public function __call($a, $b) { Foo::logFuncCall("__call(". json_encode(func_get_args()).")");}
    public static function __callStatic($a, $b) { Foo::logFuncCall("__callStatic(". json_encode(func_get_args()).")");}
    public static function __set_state($a) { Foo::logFuncCall("__set_state(". json_encode(func_get_args()).")"); return null;}
    public function __clone() { Foo::logFuncCall("__clone()");} 
} 
?>

```

为了列出这些被调用的函数，首先要确认这个函数在解序列化发生的时候是被引入被包含过的（php中的include require等）。你可以把require_once('foo.php')加到functions.php的顶端。接下来，把名字改为O:3:"Foo":0:{}{0xf09d8c86}来尝试利用这个PHP对象注入漏洞，当刷新页面后，你回看到你的名字变成了Foo，这也就是意味着这是上面那class中__toString()函数的返回，然后让我们看看都有哪些函数被调用了。

```
$ sort -u /tmp/func.log
__destruct()
__toString() 
__wakeup()

```

给出了我们三个函数：__wakeup(), __destruct() 和 __toString()

很不幸的是我不能再WordPress中找到一个载入了并且解序列化时能被利用造成影响的类。所以不是一个WordPress的安全问题，而是一个可能利用的地方。

所以是不是WordPress是有安全隐患的，但是无法被利用？不一定，如果你熟悉WordPress，你可能会觉察到可能有一堆插件存在漏洞。这些插件有他们自己的类并且可能暴露出可被利用的安全漏洞。我想到这个后，已经发现了一款著名的插件存在漏洞并且可以导致远程任意代码执行。

由于道德考虑，这个时候我不会发布PoC的，有太多存在安全漏洞的WordPress了。

0x03 修复WordPress
----------------

* * *

这个修复方式是修改is_serialized函数，我简单的说说：

```
function is_serialized( $data, $strict = true ) {
     // 如果不是字符串就不会是序列化后的数据
     if ( ! is_string( $data ) )
         return false;
     if ( ':' !== $data[1] )
         return false;
    if ( $strict ) {
        $lastc = $data[ $length - 1 ];
        if ( ';' !== $lastc && '}' !== $lastc )
            return false;
    } else {
         //确认存在;或}但不是在第一个字符
        if ( strpos( $data, ';' ) < 3 && strpos( $data, '}' ) < 4 )
            return false;
    }
     $token = $data[0];
     switch ( $token ) {
         case 's' :
            if ( $strict ) {
                if ( '"' !== $data[ $length - 2 ] )
                    return false;
            } elseif ( false === strpos( $data, '"' ) ) {
                 return false;
            }
         case 'a' :
         case 'O' :
             return (bool) preg_match( "/^{$token}:[0-9]+:/s", $data );
         case 'b' :
         case 'i' :
         case 'd' :
            $end = $strict ? '$' : '';
            return (bool) preg_match( "/^{$token}:[0-9.E-]+;$end/", $data );
     }
     return false; 
 }

```

这主要的区别是当$strict参数设置为false的时候，会有一些强制操作导致一个字符串被标记为已序列化。举例说明，最后一个字符不需要必须是;或者{（译者注：作者此处应该笔误了，应该是;或者}),修复了我所提交的漏洞。现在大家有没有相似的内容可以拿出来做个讨论的？

WordPress依旧使用着不安全的unserialize()而非安全的json_decode。它的安全性全在判断规则或者Mysql的规则实现上。我在上面揭露的漏洞实际上是使用Mysql的规则去掉我跟在特殊符号后的所有字符。

有一个很简洁的修复方案，修改一下数据库编码不被截断就好：

```
ALTER TABLE wp_commentmeta CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE wp_postmeta CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE wp_usermeta CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

```