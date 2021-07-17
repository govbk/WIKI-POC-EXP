# OAuth 安全指南

from:http://www.oauthsecurity.com/

0x00 前言
-------

* * *

这篇文章讲了OAuth 和 OpenID容易出现漏洞的一些地方。不管是程序员还是黑客，阅读它都会对你大有裨益。

就OAuth本身而言有一套很严谨的结构，但是很多开发者在部署AOuth的时候因为疏忽产生很多安全隐患，这些隐患如果被攻击者利用，是很难防御的。

现在很多大网站，都存在OAuth安全隐患，我写这篇文章的原因也是希望大家意识到由OAuth配置不当所引发的安全问题，和警示开发人员要小心处理关于OAuth的问题。

这篇文章并没有阐释OAuth的具体工作流程，想了解的话可以看他们的官网。

此文建议配合另外一个文章来看，包括乌云上很多实际案例：[《OAuth 2.0安全案例回顾》](http://drops.wooyun.org/papers/598)

0x01 Authorization Code flow
----------------------------

* * *

### 1. 通过绑定攻击者的账号进行账户劫持

这是一种比较常见的攻击手法，其实就是一种CSRF攻击。

平台返回code到事先设定好的回调url，`SITE/oauth/callback?code=CODE`，之后客户端把code连同client credentials 和 redirect_uri一起提交换取access_token。

如果客户端没有部署 state这个参数来防止CSRF攻击，那么我们就可以通过CSRF轻易地把我们提供的账号和受害者的账号绑定。

![enter image description here](http://drops.javaweb.org/uploads/images/b571006b904eeceffe8a39ca09eb4054ba9c87c7.jpg)

如下图所示，很多网站都提供使用社交账户登录的功能。

![enter image description here](http://drops.javaweb.org/uploads/images/e8d88424d8e160d8e9813865ec8e0e477ccdc274.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/be957c1fbf8175b068a25f845035ac5455a2ba9c.jpg)

**防范方法**：在把用户的数据提交给提供者网站的时候，附带一个随机数，在连接返回时，沿着这个随机数是否改变。

**State fixation bug:(state可变漏洞)**：在omniauth中一些遗留代码会导致state被修改，它使用 /connect?state=user_supplied代替了随机数。 一些开发者把state拿来做其他的用途，导致他失去了防止CSRF的功能，一个工整的解决方式可以用JSON Web Token as state。

### 2. 使用会话固化攻击进行账户劫持

在会话固化攻击中，攻击者会初始化一个合法的会话，然后诱使用户在这个会话上完成后续操作，从而达到攻击的目的。

如果我们访问一个用户绑定的链接，比如/user/auth/facebook，这个链接通常会返回 一个附带用户信息的url，其中uid代表了攻击者的id最终这个id将和受害者用户绑定。

**修复**: 确认每一条绑定社交用户的链接都拥有合法的csrf_token,最好使用post代替get。

Facebook驳回了这个CSRF漏洞的修复建议，很多库中仍包含这一漏洞。所以不要奢望平台方总是能给与你可靠的数据。

### 3. 通过authorization code泄露来劫持数据

OAuth 的文档清楚的写出了，平台方应该检查redirect_uri是否被篡改。但我们通常懒得去检查它。

这使得很多平台方在这里产生了安全隐患，Foursquare (reported), VK (report, in Russian), Github (could be used to leak tokens to private repos)

攻击的方式很简单，寻找一个XSS漏洞，搞糟一个链接把redirect_uri修改为你自己的地址。当受害者访问这个链接时，就会把leaking_page?code=CODE发送到你的指定地址。

![enter image description here](http://drops.javaweb.org/uploads/images/db26795179c39681cfcd8cde74aaa02503b49998.jpg)

这样你就可以使用这个泄露的授权码，在真实的redirect_uri上面登录受害者的用户了。

**修复方法：**可变的redirect_uri的确会产生风险，如果你非要用它，在access_token创建的时候验证它是否被篡改。

0x02 Implicit flow
------------------

* * *

### 1. redirect可控引起的access_token/signed_request泄露

这个漏洞被媒体称之为"covert redirect" ，但是这并不是一个新的漏洞。

利用它的前提是需要有一个可以修改的redirect，之后吧response_type替换为token或者是signed_request。302重定向会附带#后的信息，而攻击者只需要通过js截取即可。

**修补方式：**在app setting中建立redirect_uri白名单。

![enter image description here](http://drops.javaweb.org/uploads/images/ca7904196dfc010d2e5f6c04bd8dd0fa1994d195.jpg)

### 2. 通过收集用户access_token进行账户劫持

这个漏洞也被称为 One Token to Rule Them All.它通常发生在，手机和客户端app上。

当用户吧一个ring提交到一个他想登陆的网站时，一个恶意的网站管理员就可以通过这个ring登陆这个用户正在使用的其他网站。

![enter image description here](http://drops.javaweb.org/uploads/images/684a11d06a8b3213eefbd2a041f2a3263a6da6b7.jpg)

**修补方式：**在接受用户提交的access_token之前，检查他是否符合client_id。

0x03 Extra
----------

* * *

### 1. client credentials 泄露

client credentials其实并没有那么重要，你所能做的就是取得auth code，然后手动得到一个access_token。

使用静态redirect_uri，可以防止这种安全隐患。

### 2. 会话固化攻击 (OAuth1.0)

OAuth1.0和OAuth2.0的主要区别就是向平台传输参数的方式不同。在1.0中，客户把所有参数传递给平台，然后直接得到access_token。所以你可以诱使用户访问provider?request_token=TOKEN在授权完成后用户会被重定向到client/callback?request_token=SAME_TOKEN如果这个TOKEN是我们事先生成的，那么我们就可以复用这个TOKEN.

这不是一个服务端的bug，通常它被用来钓鱼，比如这个案例([FYI, Paypal express checkout has this bug](http://homakov.blogspot.com/2014/01/token-fixation-in-paypal.html))

### 3. 中继平台

有些平台本身在其他平台获取账号，同时也为其他用户提供服务。通常他们都需要将url重定向到第三方网站，token在这样的链条中很容易泄露

```
Facebook -> Middleware Provider -> Client's callback

```

而且这个问题基本无法修复。

facebook的解决方法是在callback url后面加上#_=_防止其夹带数据。

### 4. 绕过redirect_uri认证的一些技巧

如果允许设置子目录，下面是一些目录遍历的技巧

```
/old/path/../../new/path
/old/path/%2e%2e/%2e%2e/new/path
/old/path/%252e%252e/%252e%252e/new/path
/new/path///../../old/path/
/old/path/.%0a./.%0d./new/path (For Rails, because it strips \n\d\0)

```

### 5. 重放攻击

code经过get传输的时候会存在于log文件中，平台应该在使用或者过期之后删除它们。