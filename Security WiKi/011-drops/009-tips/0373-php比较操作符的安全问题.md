# php比较操作符的安全问题

0x00 比较操作符
==========

* * *

php的比较操作符有==（等于）松散比较，===（完全等于）严格比较，这里面就会引入很多有意思的问题。

在松散比较的时候，php会将他们的类型统一，比如说**字符到数字，非bool类型转换成bool类型**，为了避免意想不到的运行效果，应该使用严格比较。如下是php manual上的比较运算符表：

```
例子        名称         结果
$a == $b    等于      TRUE，如果类型转换后 $a 等于 $b。
$a === $b   全等      TRUE，如果 $a 等于 $b，并且它们的类型也相同。
$a != $b    不等      TRUE，如果类型转换后 $a 不等于 $b。
$a <> $b    不等      TRUE，如果类型转换后 $a 不等于 $b。
$a !== $b   不全等     TRUE，如果 $a 不等于 $b，或者它们的类型不同。
$a < $b     小与      TRUE，如果 $a 严格小于 $b。
$a > $b     大于      TRUE，如果 $a 严格大于 $b。
$a <= $b    小于等于     TRUE，如果 $a 小于或者等于 $b。
$a >= $b    大于等于     TRUE，如果 $a 大于或者等于 $b。

```

0x01 安全问题
=========

* * *

1 hash比较缺陷
----------

php在处理hash字符串的时候会用到`!=,==`来进行hash比较，如果hash值以0e开头，后边都是数字，再与数字比较，就会被解释成0*10^n还是为0，就会被判断相等，绕过登录环节。

```
root@kali:~/tool# php -r 'var_dump("00e0345" == "0");var_dump("0e123456789"=="0");var_dump("0e1234abc"=="0");'
bool(true)
bool(true)
bool(false)

```

当全是数字的时候，宽松的比较会执行尽力模式，如0e12345678会被解释成`0*10^12345678`,除了e不全是数字的时候就不会相等，这能从`var_dump("0e1234abc"=="0")`可以看出来。

2 bool 欺骗
---------

当存在json_decode和unserialize的时候，部分结构会被解释成bool类型，也会造成欺骗。json_decode示例代码：

```
$json_str = '{"user":true,"pass":true}';
$data = json_decode($json_str,true);
if ($data['user'] == 'admin' && $data['pass']=='secirity')
{
    print_r('logined in as bool'."\n");
}

```

运行结果：

```
root@kali:/var/www# php /root/php/hash.php
logined in as bool

```

unserialize示例代码：

```
$unserialize_str = 'a:2:{s:4:"user";b:1;s:4:"pass";b:1;}';
$data_unserialize = unserialize($unserialize_str);
if ($data_unserialize['user'] == 'admin' && $data_unserialize['pass']=='secirity')
{
    print_r('logined in unserialize'."\n");
}

```

运行结果如下：

```
root@kali:/var/www# php /root/php/hash.php
logined in unserialize

```

3 数字转换欺骗
--------

```
$user_id = ($_POST['user_id']);
if ($user_id == "1")
{
    $user_id = (int)($user_id);
    #$user_id = intval($user_id);
    $qry = "SELECT * FROM `users` WHERE user_id='$user_id';";
}
$result = mysql_query($qry) or die('<pre>' . mysql_error() . '</pre>' );
print_r(mysql_fetch_row($result));

```

将user_id=0.999999999999999999999发送出去得到结果如下：

```
Array
(
    [0] => 0
    [1] => lxx'
    [2] => 
    [3] => 
    [4] => 
    [5] => 
)

```

本来是要查询user_id的数据，结果却是user_id=0的数据。int和intval在转换数字的时候都是就低的，再如下代码:

```
if ($_POST['uid'] != 1) {
 $res = $db->query("SELECT * FROM user WHERE uid=%d", (int)$_POST['uid']);
 mail(...);
} else {
 die("Cannot reset password of admin");
}

```

假如传入1.1，就绕过了`$_POST['uid']！=1`的判断，就能对`uid=1`的用户进行操作了。另外`intval`还有个尽力模式，就是转换所有数字直到遇到非数字为止，如果采用:

```
if (intval($qq) === '123456')
{
    $db->query("select * from user where qq = $qq")
}

```

攻击者传入`123456 union select version()`进行攻击。

4 PHP5.4.4 特殊情况
---------------

这个版本的php的一个修改导致两个数字型字符溢出导致比较相等

```
$ php -r 'var_dump("61529519452809720693702583126814" == "61529519452809720000000000000000");'
bool(true)

```

3 题外话：
======

同样有类似问题的还有php strcmp函数,manual上是这么解释的，`int strcmp ( string $str1 , string $str2 )`,str1是第一个字符串，str2是第二个字符串，如果str1小于str2，返回<0,如果str1>str2,返回>0,两者相等返回0，假如str2为一个array呢？

```
$_GET['key'] = array();
$key = "llocdpocuzion5dcp2bindhspiccy";
$flag = strcmp($key, $_GET['key']);
if ($flag == 0) {
    print "Welcome!";
} else {
    print "Bad key!";
}

```

运行结果：

```
root@kali:~/php# php strcmp.php
PHP Warning:  strcmp() expects parameter 2 to be string, array given in /root/php/strcmp.php on line 13
Welcome!

```

参考： 1，http://phpsadness.com/sad/47  
2，http://php.net/language.operators.comparison  
3，http://indico.cern.ch/event/241705/material/slides/0.pdf