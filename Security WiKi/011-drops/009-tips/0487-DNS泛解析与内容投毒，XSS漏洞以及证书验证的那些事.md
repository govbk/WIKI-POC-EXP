# DNS泛解析与内容投毒，XSS漏洞以及证书验证的那些事

from:[http://w00tsec.blogspot.com/2014/03/wilcard-dns-content-poisoning-xss-and.html](http://w00tsec.blogspot.com/2014/03/wilcard-dns-content-poisoning-xss-and.html)

0x00 背景
-------

* * *

今天来讨论一下之前几个月我上报给Google和Facebook的一个有趣的漏洞，我在去年十月份利用一些空闲的时间在几家悬赏漏洞的公司当中测试，这个bug Google奖励了我5000美元，Facebook奖励了我500美元。

我知道你可能非常关心是如何做到[上传任意文件](http://seclists.org/fulldisclosure/2014/Mar/123)的，文件包含的payload可能会导致预料之外的行为例如关闭白名单，希望这类bug已经已经被[Fyodor修复](http://seclists.org/fulldisclosure/2014/Mar/333)。

（经/fd提醒：这里其实想要讽刺全披露安全社区关闭的事件事源一个叫尼古拉Lemonias的人提交了一个很无聊的「任意文件上传漏洞」使约翰·卡特赖特（FD的管理员）无法忍受而关闭服务）

标题可能会有点混乱，但我将要把这些技术结合起来，将会形成漏洞。

0x01 Wilcard DNS 和 Content Poisoning
------------------------------------

* * *

应用程序从HTTP Host头与domain name中不验证产生完整的 URL 会造成主机名中毒。近日，Django框架修复了一些漏洞，与James Kettle发表的[host header攻击](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)相关。

在测试这个问题时，我发现了一个不一样的主机头攻击方式，可能会绕过浏览器的通配符。

我们快速浏览一下关于Hostnames的维基百科条目：

> “互联网标准（RFC）的协议，授权该组件的主机名称标签可能只包含ASCII字母'a '到'z ' （不区分大小写），数字'0'到'9'，而连字符（ “ - ” ）在RFC 952主机名的原始规范，规定了不能以数字或连字符开始，并且不能以连字符结尾，然而，随后的规范（RFC 1123）允许以数字开头的主机名称。不能有其他符号，点与空格是允许的。 “

最有趣的部分在这里：从Windows，Linux和Mac OS X当中认为

```
-www.plus.google.com
www-.plus.google.com
www.-.plus.google.com

```

是有效的。但是Android不是这么认为的：

![enter image description here](http://drops.javaweb.org/uploads/images/5c159098e748050014fe233df27e25347dba0f85.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/bcd9b688977857715c2b095201b28278b3e67a96.jpg)

举个例子，下面的URL：

```
https://www.example.com.-.www.sites.google.com

```

如果我们在邮件当中写如上URL，Gmail会分割他，收到的邮件将含有两个部分：

```
https://www.example.com
sites.google.com

```

![enter image description here](http://drops.javaweb.org/uploads/images/1aa8205ec6a888619384667bcfecc83084ce74e9.jpg)

Facebook在zero.facebook.com域名下有一个泛解析。为了利用这个漏洞，我们有使用中毒的URL来浏览服务，并执行可能需要电子邮件确认动作，检查Facebook是否会把精心构造URL的电子邮件发送给用户。

![enter image description here](http://drops.javaweb.org/uploads/images/5ae79fbddd720206f8c70b77ae487719aa67a1d2.jpg)

我发现这个问题产生的唯一漏洞就是注册邮件确认流程中，你可能会问一个人如何利用这个来攻击一个正常的用户呢？

假设我想利用`goodguy@example.com`攻击Facebook帐户。

如果我使用

```
https://www.example.com.-.zero.facebook.com

```

浏览Facebook，我所需要做的就是创建两个账户

```
goodguy+DUPLICATE@example.com

```

[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)后面的字符，会把它转发到原始的账户中。

在这个例子当中，Facebook发送的所有确认的email有污染过的连接：

![enter image description here](http://drops.javaweb.org/uploads/images/8fcf0bc22fe802d85089f6a46257d657b3696823.jpg)

这也可以用来攻击密码重置电子邮件，但Facebook并没有受到影响。他们很快通过编码修复了电子邮件确认系统。它也可以（但不推荐）通过相对链接，而不是完整的URL （请点击[这里](http://zero.facebook.com/)，而不是一个具体的URL`www.example.com.-.zero.facebook.com`） 。

0x02 XSS和Wildcard DNS
---------------------

* * *

在Google上寻找此类问题的时候，我很快就发现了泛解析的域名，如：

```
- https://w00t.drive.google.com
- https://w00t.script.google.com
- https://w00t.sites.google.com

```

如果你想知道如何快速地找到这些泛解析的域名，你可以下载[scans.io](https://scans.io/)从中寻找。你可以找到有关反向DNS记录或通过搜索发给通配符域的SSL证书，如

```
*.sites.google.com

```

刚开始测试时，在drive.google.com域内我无法在URL当中使用`.-.`（得到500错误消息）

我能创造的URL是这样的：

```
https://www.example.com-----www.drive.google.com

```

当你使用那个URL使用Google Drive时，上传一个文件到一个文件夹，并尝试`压缩/下载`它，会要求电子邮件确认，电子邮件的确认消息是这样的：

![enter image description here](http://drops.javaweb.org/uploads/images/e96bc1263e93c36c0826af3c8a35206d9f72dde2.jpg)

“ready for downloading”链接指向

```
https://www.example.com-----www.drive.google.com/export-result?archiveId=REDACTED

```

到目前为止，没有什么大不了的，我仍然无法伪造该链接...钓鱼自己也是没有多大用处= ）

我不停地测试不同的URL ，直到我发现了一个谷歌DNS服务器怪异的行为。当输入的URL中包含一定数量的“-”之后，解析的IP地址将会是你前面所可控部分域名的IP地址：

![enter image description here](http://drops.javaweb.org/uploads/images/92481fa214b04bd796b85fd199c2dde65cc3ffe9.jpg)

出于某种原因，他们的DNS服务器有这样的小问题，更具体地说在剥离了正则表达式“--”的前缀。我不知道他们为什么进行这些检查，但可能有些事情与[国际化域名](https://en.wikipedia.org/wiki/Internationalized_domain_name)相关。

![enter image description here](http://drops.javaweb.org/uploads/images/9fac677728ec575b89ed30ca7775a250ebb13fa7.jpg)

受此问题影响的一些谷歌的域名（ 2013年10月） ：

```
- docs.google.com
- docs.sandbox.google.com
- drive.google.com
- drive.sandbox.google.com
- glass.ext.google.com
- prom-qa.sandbox.google.com
- prom-test.sandbox.google.com
- sandbox.google.com
- script.google.com
- script.sandbox.google.com
- sites.google.com
- sites.sandbox.google.com

```

现在，我可以冒充谷歌的域名，很可能绕过同源策略，

滥用代表一个登录用户的同源策略和发出请求。[lcamtuf](http://twitter.com/lcamtuf)已经告诉我们[HTTP cookies, or how not to design protocols](http://lcamtuf.blogspot.com.br/2010/10/http-cookies-or-how-not-to-design.html)。

如果我们控制

```
www.example.com

```

从drive.google.com登录用户然后访问URL

```
http://www.example.com---.drive.google.com

```

会发生什么？

请求发送到合法的网站：

![enter image description here](http://drops.javaweb.org/uploads/images/6331da4464039707acfb7b186065e709043a7144.jpg)

请求转向到用户可控的网站中，这个例子当中，我自己的服务器运行着nginx：

![enter image description here](http://drops.javaweb.org/uploads/images/26c504caf665ab4d0694500e2564f0244affb120.jpg)

这可以导致xss，你已经绕过了同源策略，可以偷取cookie，执行脚本了。

0x03 Certificate Pinning 和 Wildcard DNS
---------------------------------------

* * *

到目前为止，一切都很好，但如果我们在Google Chrome当中做同样的测试，它会强制执行证书验证码？

我一开始没有注意，但我无意中也发现了Chrome浏览器的问题：这些非RFC兼容的域他并不能做HSTS检查。

网络堆栈的其他部分进行了处理，并提取从这些“无效”的DNS名称的结果，但TransportSecurityState否决了，因此HSTS政策并不适用。他们只是删除了完整性检查，这使TransportSecurityState的过程更加复杂。

![enter image description here](http://drops.javaweb.org/uploads/images/eef165b5fc0a3acff676182f9e3b60eafc51c6da.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/854b93015492f7b709c04e83373947157861836a.jpg)

你可以在Chrome V31版本之前容易重现此问题：通过OWASP ZAP代理铬（接受其证书），请访问网址

```
https://sites.google.com

```

Chrome会显示一个“heightened security”的错误消息。

如果你输入键入的URL为：

```
https://www-.sites.google.com

```

或

```
https://www-.plus.google.com

```

Chrome浏览器提供了“Proceed anyway”的选项。

![enter image description here](http://drops.javaweb.org/uploads/images/1925eb1ab0fc36d0cba725598fa925b2ecf2719d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/5777fc2a95d943b36f133437f41e1eb91a4dadb2.jpg)

值得注意的是,根据 RFC 2818 当你在你的网站上使用通配证书(wildcard certificate)的时候，比如_.google.com，通配证书只在单层域名可用，比如如果你把匹配_.google.com的证书放到abc.def.google.com上，浏览器会提示证书错误。

Chrome浏览器中锁定的证书(pinned certificates)可以在这里找到：

[https://src.chromium.org/viewvc/chrome/trunk/src/net/http/transport_security_state_static.json](https://src.chromium.org/viewvc/chrome/trunk/src/net/http/transport_security_state_static.json)

在我分析的过程中，我发现在使用SSL的397个域名里的55个都在他们的DNS中有泛解析。一个国家级大黑客，如果获得了任意一个可信CA签发的证书都可以用这种方法对存在泛解析的域名使用中间人攻击， 注入数据包等等，绕过HSTS规则并且偷得cookie。

Google没把这个bug发CVE，但是几周后他们悄悄的修复了。Chrome 32和 33以上的版本不会受此影响。

在Apple还在为Goto fail的问题纠结的时候，如果你围观了Chromium的tracker和内部交流和测试等等，你会发现这个洞就是在那个时候补的。

0x04 结论
-------

* * *

Google和Facebook的安全团队处理的都很好。这个bug是非常好玩的，它与OWASP的Top 10的内容都不相同。

这个bug需要一个新的名词，有人愿意称这些攻击将命名为 Advanced Persistent Cross Site Wildcard Domain Header Poisoning （或简称APCSWDHP ） 。

如果你来自NSA，并希望使用此技术来植入我们的DNS，请使用代号 CRAZY KOALA 这样斯诺登泄漏你的文件时，我们就可以更好地跟踪他们了。