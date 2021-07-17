# 浏览器安全策略说之内容安全策略CSP

目录

```
0x00         前言
0x01         CSP概念
0x02         CSP发展时间轴
0x03         CSP语法
0x04         CSP默认特性
0x05         CSP例子
0x06         CSP的错误使用
0x07         CSP分析报告
0x08         CSP的使用率统计
0x09         CSP Bypass
0x0a         CSP总结
0x0b         参考

```

0x00 前言
-------

* * *

一直说要去写个浏览器安全策略系列，10篇安全策略的内容虽早已成竹在胸，但写出来却要花费好多时间。CSP这篇已于一个月前写出来，而后筹备Blog上线用了一段时间，不容易。FirstBlood，第一篇文章就献给阿尔法实验室和浏览器中一个伟大而又被忽略的安全策略CSP吧。好酒值得细细去品，好的安全策略也一样。废话少说，下面正式进入文章主题。

2013年11月Veracode给出的报告指出，全球前1000000网站中仅有269个网站使用了W3C规范的CSP策略头Content-Security-Policy。而在2014年2月ZoomEye给出的测试报告中，国内排名前7000的域名没有使用CSP，国内1千万的域名（含子域名）中仅发现7个使用了CSP策略，其中还有3个网站CSP语法使用错误。

如果说CSP是一个伟大的安全策略，为何全球范围内网站使用率如此之低？是CSP自身的设计存在问题，还是网站管理员们没有去充分了解和利用它。CSP到底是一个什么样的安全策略，是像人们普遍说的它是XSS攻击的终结者吗？

带着以上的疑问，本文将从CSP的概念、发展时间轴、语法使用、如何正确部署CSP、CSP的自有特性、如何利用CSP产生攻击报告、CSP当前使用率、Bypass CSP等众多方面，来给大家全面介绍CSP这个伟大而又被忽视的安全策略。

0x01 CSP概念
----------

* * *

内容安全策略（Content Security Policy，简称CSP）是一种以可信白名单作机制，来限制网站中是否可以包含某来源内容。默认配置下不允许执行内联代码（`<script>`块内容，内联事件，内联样式），以及禁止执行eval() , newFunction() , setTimeout([string], …) 和setInterval([string], …) 。

0x02 CSP发展时间轴
-------------

* * *

毋容置疑CSP是一个伟大的策略，但CSP从最初设计到被W3C认可制定成通用标准，却经历了一个漫长而曲折的过程。

### CSP模型首次被提出

这要从2007年说起，当时XSS攻击已经在OWASP TOP10攻击中排名第一位，CSP的最初的设想就在这一年被Mozilla项目组的Gervase Markham和WEB安全界大牛Robert Hansen ‘rsnake’两人共同提出的。

### 浏览器首次使用CSP

2011年3月Firefox 4.0发布，首次把CSP当作一种正式的安全策略规范使用到浏览器中。当时火狐使用的是自己定义的X-Content-Security-Policy头。单从CSP推广上来看，Firefox4.0的发布是划时代的，虽然此时的CSP只是Firefox自己定义的一个内部标准。但在此之后，CSP的概念被全球迅速推广。

### Chrome使用CSP

随后在2011年9月，谷歌在Chrome浏览器14.0版本发布时加入CSP，而Chrome浏览器使用的也是自己的CSP标准，它使用X-Webkit-CSP头进行对CSP的解析，这个头从字面上更能看出来Chrome浏览器使用的是Webkit内核。此时世界主流的2大浏览器Chrome、Firefox都已经支持了CSP。

### W3C起草CSP标准

作为标准发布的W3C组织顺其自然在2011年11月在官网上发布了CSP1.0草案。W3C的CSP1.0草案的语法和Firefox和Chrome中截然不同，随着时间的推移1年后，W3C的CSP1.0草案已经到了推选阶段，基本可以正式发布。

### 全面支持W3C标准的CSP

在2012年2月Chrome25版本发布时，宣布支持W3C标准的CSP1.0。2013年6月Firefox宣布在23版本中全面支持W3C的CSP1.0标准。同样是在2013年6月，W3C发布CSP1.1标准，里面又加入了不少语法，现在大多浏览器还都不支持。IE10中开始支持CSP中的’sandbox’语法，其他语法暂不支持。

目前CSP各个浏览器支持情况可以去[http://caniuse.com/#feat=contentsecuritypolicy](http://caniuse.com/#feat=contentsecuritypolicy)查看

![NewImage](http://drops.javaweb.org/uploads/images/a1f120fc24a760eed3af5b3ab033ff8be3a350fe.jpg)cspuse  

0x03 CSP语法
----------

* * *

### CSP1.0指令

![NewImage](http://drops.javaweb.org/uploads/images/aa6ba014113fe1ed758d69c2415fd28e17962bfc.jpg)

### CSP1.1新增指令

![NewImage](http://drops.javaweb.org/uploads/images/dbc17bdc6e40c6291ebd5d126928c6cd48bcfb00.jpg)

### CSP语法

![NewImage](http://drops.javaweb.org/uploads/images/061144b872d348dc1e416c3e3dc72afe581946c2.jpg)

0x04 CSP默认特性
------------

* * *

### 阻止内联代码执行

CSP除了使用白名单机制外，默认配置下阻止内联代码执行是防止内容注入的最大安全保障。这里的内联代码包括：`<script>`块内容，内联事件，内联样式。

### (1) script代码，`<script>……<scritp>`

对于`<script>`块内容是完全不能执行的。例如：

```
<script>getyourcookie()</script>

```

### (2) 内联事件

```
<a href="" onclick="handleClick();"></a>
<a href="javascript:handleClick();"></a>

```

### (3) 内联样式

```
<div style="display:none"></div>

```

虽然CSP中已经对script-src和style-src提供了使用”unsafe-inline”指令来开启执行内联代码，但为了安全起见还是慎用”unsafe-inline”。

### EVAL相关功能被禁用

用户输入字符串，然后经过eval()等函数转义进而被当作脚本去执行。这样的攻击方式比较常见。于是乎CSP默认配置下，eval() , newFunction() , setTimeout([string], …) 和setInterval([string], …)都被禁止运行。

比如：

```
alert(eval("foo.bar.baz"));
window.setTimeout("alert('hi')", 10);
window.setInterval("alert('hi')", 10);
new Function("return foo.bar.baz");

```

如果想执行可以把字符串转换为内联函数去执行。

```
alert(foo && foo.bar && foo.bar.baz); 
window.setTimeout(function() { alert('hi'); }, 10); 
window.setInterval(function() { alert('hi'); }, 10); 
function() { return foo && foo.bar && foo.bar.baz };

```

同样CSP也提供了”unsafe-eval”去开启执行eval()等函数，但强烈不建议去使用”unsafe-eval”这个指令。

0x05 CSP例子
----------

### 例子1

网站管理员想要所有的内容均来自网站自己的域，不包括子域。

```
Content-Security-Policy: default-src 'self'

```

### 例子2

网站管理员想要所有的内容来自网站自己的域，还有其他子域的内容。

```
Content-Security-Policy: default-src 'self' *.mydomain.com

```

### 例子3

网站管理员想要网站接受信任任意域的图像，指定域的音频视频和指定域的脚本。

```
Content-Security-Policy: default-src 'self'; img-src *; media-src media1.com media2.com; script-src userscripts.example.com

```

在这条策略中，默认情况下，网站只允许加载自己域的内容。但也有例外：

```
img-src * 使用*通配符可以加载任意域的图片。
media-src media1.com media2.com 视频音频只允许加载这两个域的
script-src userscripts.example.com 脚本只能加载userscripts.example.com域的

```

### 例子4

网站管理员确保在线银行所有内容都通过SSL加载，确保信息不会被截获。

```
Content-Security-Policy: default-src https://onlinebanking.jumbobank.com

```

### 例子5

看github.com的真实CSP例子。Github允许加载任何域的内容，但只能加载指定域的脚本，只能加载指定域的样式并可以执行内联样式，只能通过SSL加载指定域的flash插件。

```
Content-Security-Policy:default-src *; script-src 'self' https://github.global.ssl.fastly.net  https://ssl.google-analytics.com https://collector-cdn.github.com  https://embed.github.com https://raw.github.com; style-src 'self' 'unsafe-inline' https://github.global.ssl.fastly.net; object-src https://github.global.ssl.fastly.net

```

### 在线CSP编写

在线CSP编写，可以协助和帮助网站管理员编写出适合自己站点的CSP。http://cspisawesome.com/

![NewImage](http://drops.javaweb.org/uploads/images/a93e8f2f53171298ff09e7cf7d181c684c1f891b.jpg)

0x06 CSP的错误使用
-------------

* * *

CSP的语法和指令并不复杂，但如果没有充分了解网站业务和安全需求，错误的使用CSP则会适得其反。

（1）我在2013年底访问http://www.grosshandel-hahn.de/，发现CSP策略明显使用错误。

![NewImage](http://drops.javaweb.org/uploads/images/82aeb9298a9fe3b44c3db8320518a7203a51f8d8.jpg)

可以看到使用X-Content-Security-Policy-Report-Only。此头的意思是让浏览器只汇报日志，不阻止任何内容。但这条策略里却没有给出接收信息日志的地址。

（2）Content-Security-Policy: default-src https:; frame-src test.com;。这个策略方案是有问题的，此头限制https以外的所有资源，但又允许iframe通过http进行加载。现实中，这样的场景应该很难出现。

0x07 CSP分析报告
------------

* * *

对于网站管理员来说CSP的一个强大功能是它可以产生试图攻击你网站的分析报告。你可以用report-uri指令使浏览器发送HTTP POST请求把攻击报告以JSON格式传送到你指定的地址。接下来给大家介绍你的站点如何配置来接收攻击报告。

### 启用报告

默认情况下，违规报告不会发送。为了能使用违规报告，你必须使用report-uri指令，并至少提供一个接收地址。

```
Content-Security-Policy: default-src self; report-uri http://reportcollector.example.com/collector.cgi

```

如果想让浏览器只汇报报告，不阻止任何内容，可以改用Content-Security-Policy-Report-Only头。

### 违规报告语法

该报告JSON对象包含以下数据：

```
blocked-uri：被阻止的违规资源
document-uri：拦截违规行为发生的页面
original-policy：Content-Security-Policy头策略的所有内容
referrer：页面的referrer
status-code：HTTP响应状态
violated-directive：违规的指令

```

### 违规报告例子

http://example.com/signup.html 中CSP 规定只能加载cdn.example.com的CSS样式。

```
Content-Security-Policy: default-src 'none'; style-src cdn.example.com; report-uri /test/csp-report.php

```

signup.html中的代码类似与这样：

```
<!DOCTYPE html>
<html>
  <head>
    <title>Sign Up</title>
    <link rel="stylesheet" href="css/style.css">
  </head>
  <body>
    ... Content ...
  </body>
</html>

```

你能从上面的代码找出错误吗？策略是只允许加载cdn.example.com中的CSS样式。但signup.html试图加载自己域的style.css样式。这样违反了策略，浏览器会向http://example.com/test/csp-report.php 发送POST请求提交报告，发送格式为JSON格式。

```
{
  "csp-report": {
    "document-uri": "http://example.com/signup.html",
    "referrer": "",
    "blocked-uri": "http://example.com/css/style.css",
    "violated-directive": "style-src cdn.example.com",
    "original-policy": "default-src 'none'; style-src cdn.example.com; report-uri /_/csp-reports",
  }
}

```

你从上面可以看到blocked-uri给出了详细的阻断地址http://example.com/css/style.css，但也并不是每次都是这样。比如试图从http://anothercdn.example.com/stylesheet.css 加载CSS样式时，浏览器将不会传送完整的路径，只会给出http://anothercdn.example.com/这个地址。这样做是为了防止泄漏跨域的敏感信息。

服务端csp-report.php代码可以这样写：

```
<?php 
$file = fopen('csp-report.txt', 'a');
$json = file_get_contents('php://input');
$csp = json_decode($json, true);
foreach ($csp['csp-report'] as $key => $val) {
    fwrite($file, $key . ': ' . $val . "
");
}
fwrite($file, 'End of report.' . "
");
fclose($file);
?>

```

0x08 CSP的使用率统计
--------------

* * *

CSP的全球范围使用率非常低，而且增加的也非常缓慢。根据Veracode在2013年11月给出的报告指出，全球前1000000网站中仅有269个网站使用了W3C规范的CSP 策略头Content-Security-Policy。584个网站在使用X-Content-Security-Policy策略头和487个网站在使用X-Webkit-CSP策略头，这两个协议头已经被废弃，但还没有被禁用。

而使用Content-Security-Policy-Report-Only进行单独接收攻击报告的网站只有24个。而统计中也指出，发现大量网站使用unsafe-inline这个指令，分析其原因可能是由于开发人员很难在页面中彻底消除内联脚本，这很让人失望，所有只能要求制定的CSP策略更加严谨。

![NewImage](http://drops.javaweb.org/uploads/images/ec098870907d0a476e366a87b1b329b2ac7c1469.jpg)

[http://blog.veracode.com/2013/11/security-headers-on-the-top-1000000-websites-november-2013-report/](http://blog.veracode.com/2013/11/security-headers-on-the-top-1000000-websites-november-2013-report/)

对于国内网站使用CSP的情况，我给余弦打了个招呼，ZoomEye对此进行了统计。2014年2月发来的统计结果在非常不乐观。根据ZoomEye的统计：国内排名前7000的域名没有使用CSP，国内1千万的域名（含子域名）中发现7个使用了CSP策略，其中还有3个网站CSP语法使用错误。7个网站中3个网站是知乎，知乎网站值得表扬。列表如下：

```
www.zhihu.com
www.zhi.hu
zhimg.com
www.applysquare.com
www.pipapai.com CSP语法错误
www.icyprus.cn  CSP语法错误
www.uyitec.cn  CSP语法错误

```

在网站安全防御方面，我们还要有很长的路要走。虽然CSP安全策略头只是网站安全整体防御中的一小部分，但合理的利用还是可以起到很好的防护作用。然而在我们分析的百万网站中，CSP的使用率是极其的低，从这一点来说CSP在国内就应该广泛的给网站管理员进行科普。

0x09 CSP Bypass
---------------

* * *

一个安全策略从诞生开始将会时不时的有一个叫“Bypass”的小伙伴跟随左右。而从辩证角度来讲，多加载一种安全策略，就多了一种Bypass的维度。一旦Bypass出现，就意味着将有一种设计者没有考虑到的方法或技巧，将破坏策略的原有规则。

CSP也亦是如此，在一次次被绕过然后在一次次修复过程中，来完善自己的语法和指令。

### bypass AngularJS系列绕过

AngularJS是为数不多的支持CSP模式的MVC框架，在早起版本中可以构造多种方式绕过CSP防御。

CSP Bypasses with AngularJS 1.0.8 and 1.1.5

例如：XSS via Click & Hover (ng-click & ng-mouseover attribute)

```
<?php
header('X-Content-Security-Policy: default-src \'self\' ajax.googleapis.com');
header('Content-Security-Policy: default-src \'self\' ajax.googleapis.com');
header('X-Webkit-CSP: default-src \'self\' ajax.googleapis.com');
header('Set-Cookie: abc=123');
?><!doctype html>
<html ng-app ng-csp>
<head>
<script src="http://ajax.googleapis.com/ajax/libs/angularjs/1.1.5/angular.min.js"></script>
</head>
<body ng-click="$event.view.alert(1)">
        Click me
        <h1 ng-mouseover="$event.target.ownerDocument.defaultView.alert(2)">Hover me</h1>
</body>

```

更多的可以看[https://code.google.com/p/mustache-security/wiki/AngularJS](https://code.google.com/p/mustache-security/wiki/AngularJS)

### 策略优先级绕过

在浏览器的保护策略中，有很多是重复的。比如A策略可以抵御C攻击，B策略也可以抵御C攻击。此处的抵御可以是阻断也可以是放行。于是当AB同时作用于C攻击上时，Bypass就可能发生。

（1）Iframe sandbox 和 CSP sandbox

当iframe sandbox允许执行JS，而CSP不允许执行JS，问题就发生了，CSP就被bypass了。

```
//evil.com
<iframe sandbox="allow-scripts" src="//victim.com/csp.html">
//victim.com
<?php
header('X-Content-Security-Policy: default-src \'self\'');
header('Content-Security-Policy: default-src \'self\'');
header('X-Webkit-CSP: default-src \'self\'');
header('Set-Cookie: abc=123');
?><!doctype html>
<body onclick="alert(1)">
Click me
</body>

```

详细的讨论可以看这里：[https://bugzilla.mozilla.org/show_bug.cgi?id=886164](https://bugzilla.mozilla.org/show_bug.cgi?id=886164)

（2）XSS Auditor和CSP

关于XSS Auditor和CSP，这里我想进行一次更开放式的讨论。以Chrome中测试为例，当XSS Auditor和CSP同时作用到一段JS代码上，会有怎样一个效果呢。比如XSS Auditor设置的是阻断，CSP里设置unsafe-inline放行，结果还是被阻断。这是由于浏览器解析JS脚本的时候先使用了XSS auditor这层安全防御策略，所以CSP中的unsafe-inline这个指令并没有起作用，从广义的角度来看，CSP中的策略被Bypass了。浏览器的策略中，类似与这样的情况还有很多。比如下面介绍的这个。

（3） X-Frame-Options和CSP frame

当a.com设置X-Frame-Options:deny，b.com设置CSP frame-src a.com，那么b.com是否可以iframe a.com呢。测试中发现a.com还是不能被b.com包含的。你可以认为浏览器解析中，X-Frame-Options优先级大于CSP frame。

0x0a CSP总结
----------

* * *

充分了解CSP安全策略的语法和指令，并最大程度的合理的去利用和部署这些策略，努力把安全策略发挥到极致，使其最终把危害降低到最低。

CSP并不能消除内容注入攻击，但可以有效的检测并缓解跨站攻击和内容注入攻击带来的危害。

CSP不是做为防御内容注入(如XSS)的第一道防线而设计，而最适合部署在纵深防御体系中。

关于为什么CSP的使用率如此之低。究其原因，CSP虽然提供了强大的安全保护，但是他也造成了如下问题：Eval及相关函数被禁用、内嵌的JavaScript代码将不会执行、只能通过白名单来加载远程脚本。这些问题阻碍CSP的普及，如果要使用CSP技术保护自己的网站，开发者就不得不花费大量时间分离内联的JavaScript代码和做一些调整。

没有被绕过的策略不是好的策略，而从辩证角度来讲，多加载一种安全策略，就多了一种Bypass的维度。在安全领域“Bypass”始终是一个曼妙而鬼魅的名字。

应该把CSP安全策略视为是一把可以直插心脏的锋利的尖刀，而不是一根电线杆子杵在那。

0x0b 参考
-------

* * *

[http://www.w3.org/TR/CSP11/](http://www.w3.org/TR/CSP11/)[http://www.w3.org/TR/CSP/](http://www.w3.org/TR/CSP/)[http://www.html5rocks.com/en/tutorials/security/content-security-policy/](http://www.html5rocks.com/en/tutorials/security/content-security-policy/)[http://ruxcon.org.au/assets/slides/CSP-kuza55.pptx](http://ruxcon.org.au/assets/slides/CSP-kuza55.pptx)[https://code.google.com/p/mustache-security/wiki/AngularJS](https://code.google.com/p/mustache-security/wiki/AngularJS)[http://content-security-policy.com/](http://content-security-policy.com/)[https://github.com/blog/1477-content-security-policy](https://github.com/blog/1477-content-security-policy)[http://cspisawesome.com/](http://cspisawesome.com/)[https://developer.mozilla.org/en-US/docs/Security/CSP/Using_Content_Security_Policy](https://developer.mozilla.org/en-US/docs/Security/CSP/Using_Content_Security_Policy)[http://benvinegar.github.io/csp-talk-2013/#1](http://benvinegar.github.io/csp-talk-2013/#1)[http://caniuse.com/#feat=contentsecuritypolicy](http://caniuse.com/#feat=contentsecuritypolicy)[https://www.imququ.com/post/content-security-policy-reference.html](https://www.imququ.com/post/content-security-policy-reference.html)[http://docs.angularjs.org/api/ng.directive:ngCsp](http://docs.angularjs.org/api/ng.directive:ngCsp)[https://developer.mozilla.org/en-US/docs/Security/CSP/Using_CSP_violation_reports](https://developer.mozilla.org/en-US/docs/Security/CSP/Using_CSP_violation_reports)[http://stackoverflow.com/questions/14629534/json-post-in-php-csp-report](http://stackoverflow.com/questions/14629534/json-post-in-php-csp-report)[http://mathiasbynens.be/notes/csp-reports](http://mathiasbynens.be/notes/csp-reports)[http://www.madirish.net/556](http://www.madirish.net/556)[http://www.veracode.com/blog/2013/11/security-headers-on-the-top-1000000-websites-november-2013-report/](http://www.veracode.com/blog/2013/11/security-headers-on-the-top-1000000-websites-november-2013-report/)[https://github.com/google/CSP-Validator](https://github.com/google/CSP-Validator)[http://www.benmarshall.me/content-security-policy/](http://www.benmarshall.me/content-security-policy/)[http://www.slideshare.net/x00mario/jsmvcomfg-to-sternly-look-at-javascript-mvc-and-templating-frameworks](http://www.slideshare.net/x00mario/jsmvcomfg-to-sternly-look-at-javascript-mvc-and-templating-frameworks)[http://trends.builtwith.com/javascript/Angular-JS](http://trends.builtwith.com/javascript/Angular-JS)[http://developer.chrome.com/extensions/contentSecurityPolicy](http://developer.chrome.com/extensions/contentSecurityPolicy)[http://cs.ucsb.edu/~adoupe/static/dedacota-ccs2013.pdf](http://cs.ucsb.edu/~adoupe/static/dedacota-ccs2013.pdf)