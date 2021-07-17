# 安全科普：Waf实现扫描器识别 彻底抵挡黑客扫描

0x00 背景
-------

* * *

目前安全测试的软件越来越多，也越来越强大，越来越多的人成为[黑客]，今天在网上看到一个文章说拦截wvs的扫描，勾起了我写这篇文章的欲望。

因为公司的三大业务之一就有一个云waf，每天拦截的日志里面，有将近90%的请求是扫描器发出，waf接收到请求会解析数据包，然后过一遍规则，过完成百上千条规则必定对性能有一定的影响。如果能识别出来是人还是扫描器的请求，就可以在这方面节省很大的资源。

下面的分析介绍只针对web安全扫描器。

0x01 分析特征
---------

* * *

目前全能型的扫描器主要是wvs（Acunetix Web Vulnerability Scanner）、AppScan、WebInspect，国内的像aisec、bugscan等等…还有国内那些老安全厂商的扫描器就不说了，主要提一下像wvs这种使用率比较高的。另外还有目录文件型的扫描器、注入工具(类似sqlmap、Havij)等等。

扫描器识别主要从以下几点来做：

```
一、 扫描器指纹(head字段/请求参数值等) 
二、 单IP+ cookie某时间段内触发规则次数 
三、 隐藏的链接标签(<a>) 
四、 Cookie植入 
五、 验证码验证 
六、 单IP请求时间段内Webserver返回http状态404比例 

```

### 一、扫描器指纹(head字段/请求参数值等)

目前最常见的手法就是收集扫描器的指纹特征来做识别，不同的扫描器都有自己的一些特征，比如发出的请求会加一些特定的head 字段，测试漏洞的请求参数的值会带上自己扫描器的名称等。

下面通过抓网络数据包来看常见扫描器的指纹特征：

wvs（Acunetix Web Vulnerability Scanner）：

下面是我抓到的一个wvs的请求

![20131107114510_20989.jpg](http://drops.javaweb.org/uploads/images/a146cff6ffac5ab50781078f2481d0fbe2a68e07.jpg)

```
GET /help/website-performance-settings/x HTTP/1.1
Pragma: no-cache
Cache-Control: no-cache
Referer: http://www.anquanbao.com/help
Acunetix-Aspect: enabled
Acunetix-Aspect-Password: 082119f75623eb7abd7bf357698ff66c
Acunetix-Aspect-Queries: filelist;aspectalerts
Cookie: xxxxxxxxxxxx
Host: www.anquanbao.com
Connection: Keep-alive
Accept-Encoding: gzip,deflate
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.63 Safari/537.36
Accept: */*

```

请求头里面有三个很明显的标志：

```
Acunetix-Aspect: enabled
Acunetix-Aspect-Password: 082119f75623eb7abd7bf357698ff66c
Acunetix-Aspect-Queries: filelist;aspectalerts

```

另外在请求的参数值，比如URL跟POST数据中都有很明显的acunetix_wvs_security_test特征，下图是我从waf拦截中调取到的结果。

![20131107114759_54681.jpg](http://drops.javaweb.org/uploads/images/18fa6281da653da2573a9a807aebdba3696a9ab0.jpg)

根据以上抓取到的特征，我们可以把这个作为wvs的一个指纹，在waf中进行过滤。

#### Appscan

同样的，appscan也有自己的一些特征，如下

![20131107114839_35125.jpg](http://drops.javaweb.org/uploads/images/c78302b199cfb4ac46d0cc323e5c8e6e78508b27.jpg)

#### Bugscan

关于Bugscan，我咨询了一下作者，作者给了XSS模块的扫描源码我看了下，主要特征是：

```
–>’”><H1>XSS@HERE</H1>

```

另外还有一些特征就不一一列举。

![20131107114919_40006.jpg](http://drops.javaweb.org/uploads/images/69aae25820337e1957de822dcdd994eda3ac3742.jpg)

注意：并不是所有的请求都会带有扫描器的特征，比如下面的一个包也是wvs发出的，但是没有带上面我们说的特征，扫描器指纹特征只能抵挡住一部分的扫描，但是我们可以利用这些信息识别出扫描器然后干掉IP等。

![20131107114955_31758.jpg](http://drops.javaweb.org/uploads/images/5a00923a5f5ea95ff74a9fb1f6336a8490d47faa.jpg)

### 二、单IP+ cookie某时间段内触发规则次数

根据某个IP+ cookie某时间段内触发waf拦截规则的次数大于设定的某个阀值，比如在20秒内，某个IP+cookie触发waf拦截规则10次。

数据证明如下图：

![20131107115034_38569.jpg](http://drops.javaweb.org/uploads/images/8043ba96008a61d7016db854ed76d27dc8c432b9.jpg)

另外还可以根据IP+user angent等，或者更多维度。

### 三、隐藏的链接标签等(<a>)

扫描器的爬虫会把页面里面的所有链接都抓出来去做漏洞探测，特别是现在基于webkit一类的扫描器，能够渲染css跟js，可以爬出更多的链接测试。

下面贴出一个百度百科关于webkit的介绍

```
WebKit 是一个开源的浏览器引擎，与之相对应的引擎有Gecko（Mozilla Firefox 等使用）和Trident（也称MSHTML，IE 使用）。同时WebKit 也是苹果Mac OS X 系统引擎框架版本的名称，主要用于Safari，Dashboard，Mail 和其他一些Mac OS X 程序。WebKit 前身是 KDE 小组的 KHTML，WebKit 所包含的 WebCore 排版引擎和 JSCore 引擎来自于 KDE 的 KHTML 和 KJS，当年苹果比较了 Gecko 和 KHTML 后，仍然选择了后者，就因为它拥有清晰的源码结构、极快的渲染速度。Apple将 KHTML 发扬光大，推出了装备 KHTML 改进型 WebKit 引擎的浏览器 Safari。

```

隐藏的标签链接是指人看不见的链接，如

```
<a href="http://www.cnseay.com/"></a>

```

形式，人是点击不到的，只有软件能够匹配出这个地址，我们新建一个网页，抓扫描器数据包测试。

```
<html>
 <head>
  <title>test</title>
 </head>
 <body>
  <a href="http://localhost/1.php?id=1"></a>
 </body>
</html>

```

通过抓取wvs的数据包可以看到，扫描器很快的捕获了http://localhost/1.php?id=1这个链接，并进行漏洞测试。

![20131107115118_39599.jpg](http://drops.javaweb.org/uploads/images/4aaeda902176c8cf7f3b343459a670d0233dbd29.jpg)

当然如果在正常情况下也给所有用户植入这种代码是非常令人反感的，用户体验也会大打折扣，可以在前期先做一些条件限制，比如固定时间段内触发waf拦截规则到达预定阀值，再给这个用户单独植入一个隐藏链接。

### 四、Cookie植入

Cookie植入的方式跟上面讲的隐藏链接植入大同小异，实现原理是：当一个IP+user angent在固定时间段内触发规则的次数到达一定阀值，给发起请求的这个人植入一个cookie，如果下次再请求没有携带这个cookie，则说明是扫描器。 cookie植入有利有弊，优点是更直接，种下cookie马上就能根据下一个请求判断。缺点是这个方式在基于webkit的扫描器上面行不通。

### 五、验证码验证

验证码验证的方式跟上面的cookie植入也大同小异，不过是把cookie换成了验证码的方式，这种方法也被用于防CC攻击。

### 六、单IP请求时间段内Webserver返回http状态404比例

这种方法主要用来应对探测敏感目录和文件的扫描器，这类的扫描器都是基于字典文件，通过对字典内的url进行请求获得的返回信息来进行判断目录或者文件的是否存在。 如果某个IP在一段时间内请求频率过快，这时候waf可以进行收集一段时间内webserver返回404状态数目，到达一定阀值后进行封杀。

![20131107115147_87082.jpg](http://drops.javaweb.org/uploads/images/a9114b9182ec207b0578e1fd9048a321d2b5efe6.jpg)

0x02 思考
-------

* * *

看过上面几种方法的介绍，应该大部分人都会想到两个问题，

```
  1.  一大拨人使用同一个公网IP，怎么判断谁是攻击者？
  2.  一大拨人使用同一个公网IP，怎么才能保证不误杀？

```

第一，对于怎么判断攻击者，当然不能单纯的从一个IP判断，一般一个完整的http请求都会带有user angent、cookie等信息，我们可以结合ip+user angent来判断请求的人，或者再加一个cookie的维度，当然在给这个攻击者植隐藏链接、cookie或者验证码之前，需要它触发一些规则阀值，以免影响用户体验。

第二，说到怎么保证不误杀，也就是怎么去封杀的问题，关键在于怎么二次判断攻击者，目前最好的方法也是利用ip+user angent，在判断是扫描器请求后，根据IP+user angent进行封杀，另外也是靠cookie封杀，关键在于是携带某个cookie键的封杀掉还是不带的封杀掉。

PS：如果误杀太大，如果刚好哪个妹纸在线看小电影到激情片段，这是多伤人妹纸的心啊。

出自：[http://www.cnseay.com/3469/](http://www.cnseay.com/3469/)