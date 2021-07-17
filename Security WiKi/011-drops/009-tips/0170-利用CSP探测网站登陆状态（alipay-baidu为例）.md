# 利用CSP探测网站登陆状态（alipay/baidu为例）

0x00 背景
=======

* * *

今天看到zone里有同学发帖说了探测支付宝登录状态的帖子：http://zone.wooyun.org/content/17665

由此我想到了我们parsec的@/fd 半年前提到的一个思路，当时他给出了一个探测twitter是否登录的页面，可是我那个时候才疏学浅，好像一直没理解。这时候返回去看看，就有了这篇文章。

0x01 CSP简介
==========

* * *

内容安全策略（Content Security Policy，简称CSP）是一种以可信白名单作机制，来限制网站中是否可以包含某来源内容。默认配置下不允许执行内联代码`<script>`块内容，内联事件，内联样式 ，以及禁止执行eval() , newFunction() , setTimeout([string], …) 和setInterval([string], …) 。

CSP更详尽的介绍可以在drops看到：http://drops.wooyun.org/tips/1439

0x02 大环境介绍与原理
=============

* * *

简单了解一下CSP，我们知道CSP可以限制网站中可否包含某来源的内容。同时，csp还可以在页面违反规则的时候发送一个数据包，将具体细节通知给服务端。

我们再来想想像支付宝这种集成度很高的网站服务，当我们在未登录的情况下访问alipay的某个子域名（如test.alipay.com），很可能是会302跳转到一个用户登陆专用的域名（如login.alipay.com）下要求用户登录。而在已登录的情况下是不会跳转的。

这就造成了一个登录/未登录的一个差别，主要差别如下：

1.  HTTP状态码（302和200）
    
2.  最终访问的域名（test.alipay.com和login.alipay.com）
    

因为浏览器SOP（同源策略）的限制，正常情况下我们是无法获取到alipay域名下HTTP状态码的。

但结合CSP安全策略，我们却可以简单获得第2个，也就是最终访问域名。为什么？

我前面说了CSP是可以限制页面中允许加载哪些来源的内容的。所以，当我们将CSP设置为只接受来源为test.alipay.com的内容，那么当加载来源为login.alipay.com的请求时就会被CSP策略拒绝，并可以将这个访问report给服务端，我们通过report的内容就能判断用户访问的是test还是login。 过程如下：

![enter image description here](http://drops.javaweb.org/uploads/images/c901fc20bae9e6f9f22e65b89bf5d253e042f553.jpg)

这就是原理，很赞的一个思路，再次崇拜一次@/fd。

0x03 以支付宝为例编写探测代码
=================

* * *

所以，根据上面的思路，我们第一步就是找到一个这样的页面：登录、未登录用户访问时到达的“域名”不相同。这里的“域名”包括protocol和hostname，也就是说http://test.alipay.com和https://test.alipay.com是不同的域名。

像支付宝这种网站有很多这样的页面，因为支付宝的很多服务是登录用户才能查看的，而登录入口又只有那么一个。

比如这个URL：https://my.alipay.com/portal/i.htm，当未登录用户访问的时候会跳转到https://auth.alipay.com/login/index.htm，已登录用户访问时不会跳转。

这时候我们将CSP的img-src限制为https://my.alipay.com，再将https://my.alipay.com/portal/i.htm作为img的src，这个时候就会出现一个有趣的现象：未登录的用户访问时，会触发CSP规则。

因为未登录的用户访问时实际img加载的src是https://auth.alipay.com/login/index.htm，不符合CSP限制的img-src，自然就触发规则了。 这时候我们在设置CSP的report-uri为report.php，不符合规则的请求会被记录下作为日志发送到report.php里：

![enter image description here](http://drops.javaweb.org/uploads/images/c6a4fa0607387ec5d8c79387b47f14e06fad64cd.jpg)

不过浏览器在发送这个report包的时候是不带cookie的，所以服务器那边并不能直接判断是哪个用户发送的report包，所以我们在report的GET参数里带上用户的session id。

示例代码如下：

```
<?php
session_start();
$ssid = session_id();
header("Content-Security-Policy:img-src https://my.alipay.com; report-uri report.php?ssid={$ssid}");
?>
<html>
<head>
<meta charset="utf-8" />
<title>支付宝登陆检测</title>
</head>
<body onload="return check();">
<img src="https://my.alipay.com/portal/i.htm">
<b id="result"></b>
<script type="text/javascript">
function check()
{
    with(new XMLHttpRequest) {
        open('GET', 'alipay.php');
        send();
        onreadystatechange = function() {
            if (readyState ^ 4) return;
            result.innerHTML = parseInt(responseText) > 0 ? '未登录' : '已登录';
        }
    }
}
</script>
</body>

```

report.php用来记录：

```
<?php
session_start();
if (preg_match('/^[a-z0-9]*$/i', $_GET['ssid'])) {
    session_id($_GET['ssid']);
}else{
    exit;
}
$report = file_get_contents("php://input");
if (!empty($report)) {
    $_SESSION['nologin'] = 1;
}else{
    $_SESSION['nologin'] = 0;
}
?>

```

当接收到php://input的时候说明CSP发送报告了，说明请求违反的CSP规则了，也就意味着用户没有登录，所以将session中的nologin设置为1。 然后在index.php里用一个ajax来向alipay.php请求，实际上就是获得$_SESSION[nologin]的值：

```
<?php
session_start();
echo isset($_SESSION['nologin']) ? $_SESSION['nologin'] : 0;
setcookie('PHPSESSID', '', time() - 10);
session_destroy();
?>

```

如上，获取完后将session清除一下，以免影响下一次的判断。

获得值如果为1的话，说明没有登录，如果为0说明已登录，就可以显示出来或做任何其他操作了。

来个演示：http://mhz.pw/game/detect/alipay/

登录支付宝以后访问，显示“已登录”

![enter image description here](http://drops.javaweb.org/uploads/images/85e67e0bcb55220bb51f94770d93c9a6a6281c03.jpg)

换个浏览器，直接访问则显示“未登录”：

![enter image description here](http://drops.javaweb.org/uploads/images/faa6056c2b16b034cee3e2c52f2775572c597fd7.jpg)

0x04 由http/https混用造成的问题（百度为例）
=============================

* * *

同样的问题，不仅仅是支付宝存在，只要有“统一登录入口”的网站都可能出现这个问题，因为统一登录入口通常是一个单独的域名。

还有一种情况，是http和https混用造成的。有些网站的登录页面是https加密传输的，但登陆以后实际的操作页面是走http。

这之间一样存在一个跳转的问题，当我们访问一个登陆后才能看到的页面如http://xxx.com/index，未登录的用户就会跳转到登录页面，如https://xxx.com/login。

在CSP里http和https是完全不同的两个来源，所以也能触发CSP规则。

比如https://passport.baidu.com，这是百度的安全中心。当已登录用户访问的时候会跳转到“安全中心”首页http://passport.baidu.com/center（注意，此处是http）：

![enter image description here](http://drops.javaweb.org/uploads/images/f281fb0b81f023bc01ad8764b6023a30fded5e11.jpg)

而未登录用户访问则会跳转到https://passport.baidu.com/v2/?login（这时候是https）：

![enter image description here](http://drops.javaweb.org/uploads/images/560f2629c5f61a465dfd41e3f1bcaf8bac8d01cb.jpg)

虽然两个域名都是passport.baidu.com，但因为protocol不同，混用的http和https就能够影响CSP的拦截情况。

我们将CSP设置为img-src https://passport.baidu.com ，那么img的src就只接受来源为https://passport.baidu.com的img，那么已登录用户访问的http://passport.baidu.com/center就会被阻止，产生一个CSP报告。记录下这个报告，一样能判断访客是否已登录百度。

测试你是否登录百度：http://mhz.pw/game/detect/baidu/

0x05 影响及防范方法
============

* * *

严格来论，只是判断用户是否登录，这个问题并不算一个漏洞。当时@/fd将问题提交到推特之后推特的回应也是不算漏洞，但确实如果与其他一些漏洞结合使用，会让某些漏洞的成功率提高一大截。所以我们可以将之归为一个“奇技淫巧”。

这个问题更容易出现在一些大型网站、企业网络之中，往往这些网站的统一性和重用性都做的很好，所以往往登录入口只有一个（现在流行一个user center的概念），所以难免会出现一些跳转的问题。有这些跳转，就是探测用户登录的基础。

这个方法还有一个限制，就是用户使用的浏览器需要是现代浏览器，需要支持CSP安全策略。如果你要探测的用户还在用IE6~IE10，那么是肯定不行的。 如何解决这个问题？如果你真的觉得这是个安全问题的话，那么尽量避免跳转，或者使用javascript进行页面的跳转。