# 变种XSS：持久控制

0x00 引言
=======

* * *

首先声明，这不是一个新洞，看过 Homakov 文章（最后附）以及译文的人想必对这种漏洞有所了解。

但原文写的太过简单（没有说明利用条件、情景和特性），且译文和我的理解略有偏差，于是就有了这篇文章。

这种漏洞已经存在一段时间了，有没有被利用过尚不得知，虽然利用条件较苛刻，但是当符合条件的站点被攻击后， 影响面和影响程度巨大，并且普通用户不知如何清除, 可导致长期持续攻击。

2014年底的时候，这种漏洞的利用条件没有现在苛刻（比如没有`Service-Worker-Allowed`头），一年过来 W3C 对规范优化了不少（包括安全方面）， 相信不久的将来，很快会被标准更新所扼杀了。

弥留之际，让这个漏洞放点异彩吧。

0x01 一切都从 serviceWorker 说起
==========================

* * *

> Service Worker是基于Web Worker的事件驱动的，他们执行的机制都是新开一个线程去处理一些额外的，以前不能直接处理的任务。对于Web Worker，我们可以使用它来进行复杂的计算，因为它并不阻塞浏览器主线程的渲染。而Service Worker，我们可以用它来进行本地缓存，相当于一个本地的proxy。说起缓存，我们会想起我们常用的一些缓存技术来缓存我们的静态资源，但是老的方式是不支持调试的，灵活性不高。使用Service Worker来进行缓存，我们可以用javascript代码来拦截浏览器的http请求，并设置缓存的文件，直接返回，不经过web服务器，然后，做更多你想做的事情。

*   我们可以用 javascript 代码来拦截浏览器的 http 请求，并设置缓存的文件，直接返回

相信很多人看到这句已经明白了，通过 js 来代理浏览器 http 请求，也就是说通过执行 js 代码来控制浏览器的请求， 很容易想到，利用 xss 来修改浏览器请求的返回内容。

可怕的是，即便 xss 漏洞被修复了，攻击仍然持续，并且渗透到攻击范围内的每一个 url。

并且，当用户察觉到攻击，并且理解这种攻击，进入chrome后台（chrome://appcache-internals）， 进行手动清除攻击缓存，攻击仍未失效！当然了，还是有办法清除的，且无须用户手工操作（下文会演示）。

0x02 漏洞原理和演示
============

* * *

`serviceWorker`的官方标准文档：[http://www.w3.org/TR/service-workers/](http://www.w3.org/TR/service-workers/)

其操作可以参考：[https://github.com/w3c-webmob/ServiceWorkersDemos](https://github.com/w3c-webmob/ServiceWorkersDemos)

首先 serviceWorker 只有在 https 页面中才可以调用 regist。

而 serviceWorker 需要 Promise 支撑，目前支持的浏览器如下：

![](http://drops.javaweb.org/uploads/images/a5fed1d79fc2db5b95fcb0943bcd3166e6f24b0a.jpg)

支持 serviceWorker 的浏览器：

![](http://drops.javaweb.org/uploads/images/bd3c7a28fbb3a09dd13553c2780d858944c5f32e.jpg)

firefox 默认关闭 serviceWorker，可以通过 about:config 打开开关：

![](http://drops.javaweb.org/uploads/images/a0afe53992d9aef77a919a1f3731d1d5e0c69e13.jpg)

支持 fetch 方法（抓包）的浏览器：

![](http://drops.javaweb.org/uploads/images/e4bc3579d08ddcf4b443ba14dc3d2db829eaf3f5.jpg)

* * *

开始尝试攻击：
-------

首先在 https 站点中找到一个 Xss，利用 Xss 注册一个`serviceWorker.registration`实例：

```
navigator.serviceWorker.register(url).then(function(registration) {
  console.log(registration);
});

```

注意到有个未知参数 url，这个 url 就是拿来放我们的攻击代码（假设我们能上传一个js到根目录）：

```
var url = '//victim.com/evil.js'

```

有人说这太难了，往根目录上传 js 文件不可能，那么可以尝试在子目录/任何一个可能的目录上传js文件， 或者和 Homakov 一样，利用 jsonp 接口来代替这个恶意 js 文件。

serviceWorker.register 只支持请求文件返回头的MIME类型为：`text/javascript, application/x-javascript, application/javascript`。

我们知道，jsonp 的 callback 经常是可控的，那么找到一个这样可以写代码的 jsonp 难不难？

Google it !

![](http://drops.javaweb.org/uploads/images/7d1bffd1002aa439ec3502d8eb9e759f9e23683b.jpg)

点击第一个链接：

![](http://drops.javaweb.org/uploads/images/828070948f87e9f59fd437a8204f2bb158485833.jpg)

可以看到，以 taobao.com 为例，第一个 jsonp 接口就存在这样的弱点：callback 可以写入任意代码。

退一步说，只要能输入 []!() 等几个符号，就能构造任意代码了。

以往安全工程师修复 jsonp 接口的 xss 漏洞，都是将页面的`mime`修改为`application/javascript`， 或者将 callback 的参数中的html符号实体转义，就觉得杜绝 xss 了，看来以后得换个修法了

若 callback 仅仅代表一个函数名，何不只允许数字、字母和下划线呢？

往 “js/jsonp接口” 里写入恶意代码：
-----------------------

```
onfetch = function(e) {
  e.respondWith(new Response('任意内容',{
      headers
      ...
    });
  );
}

```

通过 onfetch 方法拦截 http 请求，并构造返回内容，比如返回：`<script>alert(/xss/)</script>`

所有在 evil 路径下的请求的内容都被篡改。

* * *

让我们本地测试还原一遍场景（注意：本地测试不需要 https）：

首先打开网站：

![](http://drops.javaweb.org/uploads/images/979b06aefb849b054501f6779a7bda91cdd4b479.jpg)

打开正常页面：

![](http://drops.javaweb.org/uploads/images/28038f77e923e093d938f9a311c89fe0a8b199a9.jpg)

这时候点击被攻击页面，此页面事先被注入了 XSS 脚本：

![](http://drops.javaweb.org/uploads/images/43fa5b79484fbd91f13a1db9bb61efd0aa357e08.jpg)

可以看到，这时候 serviceWorker 已经成功注册了

刷新页面，此时返回内容以及被修改了：

![](http://drops.javaweb.org/uploads/images/1000b3dbb7c1c78bb856fa0fd9a1c76d557e6035.jpg)

这时候再看正常页面，也被攻击了：

![](http://drops.javaweb.org/uploads/images/609ad2447def5ab2ac4327613424e417f0faa69f.jpg)

首页也是相同的情况：

![](http://drops.javaweb.org/uploads/images/4667fcbcf789ca8fac45c9bf1a100ddc1132dcb4.jpg)

关闭浏览器，再打开，依旧如此：

![](http://drops.javaweb.org/uploads/images/025694e3f17319886215fd201de6d5c143c20cbd.jpg)

### 0x03 优势、局限性

*   优势
    *   生存周期久（即便浏览器重启还在）
    *   一旦中招不易清除，包括用户和网站业务方
*   局限性
    *   需要同域中同时存在 XSS 和弱点 JSONP（或可控js文件）
    *   感染路径受弱点 js 路径的限制
    *   被攻击站点必须是 https

实际利用中，若弱点JSONP路径中不存在网站业务，这个漏洞依然能发挥一定价值。

比如：杀死该JSONP路径以及其子目录的全部接口，从而导致网站无法正常使用。

0x04 中止及防范攻击
============

* * *

1. 如何中止攻击
---------

从上文可以知道，即便 xss 被修复了或者消失了，攻击依然生效，那么如何中止攻击呢？

作为一个普通用户，首先尝试打开 chrome://inspect/#service-workers 查看存活：

![](http://drops.javaweb.org/uploads/images/ef67fc56c0ed943d2f4c68875aa770e4c30fd4c7.jpg)

的确可以看到被用作攻击的 Worker，点击 terminate 尝试中止：

![](http://drops.javaweb.org/uploads/images/f609bf32658440da3bf84c75ce370cd28af91300.jpg)

![](http://drops.javaweb.org/uploads/images/b6f78475b6542468d1d9dd281339a90934d4b143.jpg)

可以看到以及被清理了，但是打开页面，攻击仍然存在！

![](http://drops.javaweb.org/uploads/images/cc9274a729cec062f518572b8ef07afa51fd53df.jpg)

浏览器中打开`F12`，在`console`中输入：`navigator.serviceWorker.`， 可以看到有 getRegistration 和 getRegistrations 这两种属性。

查询文档：[https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/getRegistration](https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/getRegistration)

尝试获取注册器，并且调用注销（由于用到 Promise，需要使用 then 调取结果）：

```
navigator.serviceWorker.getRegistration()
  .then(function(registration) {
  registration.unregister();
});

```

![](http://drops.javaweb.org/uploads/images/6557af9c07d62c3e4bc264c2d36008c26ed4c288.jpg)

![](http://drops.javaweb.org/uploads/images/f487d7693aa0d68177d1e7c8f6530ffa01740bb7.jpg)

这一次终于清除了。

而对于网站方，如何清除所有攻击呢？

只要将“清除代码”部署在一个未受感染的同域的页面里，当用户访问过后，自然就清除了。

2. 防范方法：
--------

1.  Jsonp 接口的 callback 可以做白名单，或者只允许特定字符（比如数字、字母和下划线）。
2.  Jsonp所在域不应该存在 XSS（一切类型），至少不应该存在业务页面。
3.  如果做不到2，Jsonp 所在 url 路径下不应该存在网站业务。
4.  域名内不应存在用户可控的 js 文件。

### reference:

*   [http://www.w3.org/TR/service-workers/](http://www.w3.org/TR/service-workers/)
*   [https://github.com/w3c-webmob/ServiceWorkersDemos](https://github.com/w3c-webmob/ServiceWorkersDemos)
*   [http://sakurity.com/blog/2015/08/13/middlekit.html](http://sakurity.com/blog/2015/08/13/middlekit.html)
*   [https://jakearchibald.github.io/isserviceworkerready/](https://jakearchibald.github.io/isserviceworkerready/)
*   [https://developer.mozilla.org/en-US/docs/Web/API/](https://developer.mozilla.org/en-US/docs/Web/API/)