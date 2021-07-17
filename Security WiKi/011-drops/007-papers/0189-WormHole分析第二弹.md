# WormHole分析第二弹

0x00 背景
=======

* * *

最近WormHole这个洞炒的比较火，今天看了几篇漏洞分析文章，都很详尽，笔者在这里再补充一些发现。

笔者在10月初就发现了百度地图的这个漏洞，并报给了BSRC得到确认，但与**瘦蛟舞，蒸米等研究人员**出发点不同，笔者并没有从SDK的角度出发去发掘出更多的使用moplus这个库的app，而是从功能性的角度出发，以地图类应用作为切入点，尝试去发现一些问题。虽说没有发现那么多存在漏洞的app，但好在也有一些发现。

0x01 百度地图
=========

* * *

Wormhole的漏洞报告出来后，很多圈内人士针对“后门还是漏洞”的问题产生了激烈的讨论，微博、知乎上各种声音。

一个事物的出现必然有他的原因，一个应用为什么要在手机上开放一个端口呢？百度地图为什么在修复漏洞依然还开着40310这个端口？可见这个端口存在自然有其存在道理，于是开始进一步分析。

用Chrome模拟手机（Nexus 5）访问`www.baidu.com`，在请求包里明显看到有访问`http://127.0.0.1:40310/getsearchboxinfo?xxxxxxx`的数据包，心中一惊，这不就是wormhole的一个利用么？

![](http://drops.javaweb.org/uploads/images/6610c2cc0db90cc790cf816fe0c9c90a153e952a.jpg)

难道百度开放一个端口就是为了能在web网页里访问一下？一次偶然的发现，访问搜狗网址导航也出现了`http://127.0.0.1:40310/getcuid?xxxxxxx`之类的数据包，看来除了百度还有其他的地方在“利用这个漏洞”。

![](http://drops.javaweb.org/uploads/images/a54b7d1f5c68a331b15fe2e83cdbfe81fddc716e.jpg)

几番试验，笔者又在模拟手机在其他几个网站发现了同样现象，莫非这些网站都知道这个漏洞？几番研究后，最终锁定了源头——百度统计。

百度统计的脚本是hm.js，而hm.js加载了一个html:`http://boscdn.bpc.baidu.com/v1/holmes-moplus/mp-cdn.html`

这个html又加载了一个js:`http://static1.searchbox.baidu.com/static/searchbox/openjs/mp.js`

就是这个js中一段代码发出了对本地端口的请求，查看代码不难发现，该脚本对6259和40310这两个端口都发出了请求，这也正好印证了wormhole漏洞为啥固定开辟了这两个端口。

![](http://drops.javaweb.org/uploads/images/8325376c47d7cff9238658a1c66a68cac00db314.jpg)

综上，不难发现百度开放6259和40310是为了百度统计服务的，但目前发现的情况也只是getcuid、getsearchboxinfo之类一些简单的信息，至于为什么在这个接口上实现获取所有安装包信息、写通讯录、任意上传下载文件等就不得而知了。但毋庸置疑，想要利用这些接口只需在百度统计脚本里加几行代码就可以了，只是现在未发现利用的证据。所以，至于是漏洞还是后门，笔者不作评价。

0x02 高德地图
=========

* * *

仔细看上边百度的分析，不难得出结论，一个应用开放一个端口，本质上是为了web页面和app本身达到某种交互。既然百度地图有问题，那么其他地图类应用呢？

笔者先前看到乌云上有一个关于高德地图的漏洞[http://wooyun.org/bugs/wooyun-2015-0114241](http://wooyun.org/bugs/wooyun-2015-0114241)，原理和百度这个漏洞类似，也是开放了一个6677端口，那么高德是怎么修复这个洞的呢？

研究发现高德采用验证http_referer的方法，对比之前的漏洞发现高德把http_referer白名单由java层放到了native层

![](http://drops.javaweb.org/uploads/images/d13702c612ecdc49daa6e3934918601f94ab4d85.jpg)

在验证http_referer时，高德竟然用了contains()这个函数去遍历，简直暴力啊

![](http://drops.javaweb.org/uploads/images/1d7802919da424090b6d3b5dc6aebbc7627d5375.jpg)

由此可见高德的修复并不彻底，一是contains()很容易被逻辑绕过，二是http_referer很容易伪造，当然高德地图的最新版本又做了一些改动，但不管怎么样修复，高德还是保留着6677这个端口。

这不禁令人生疑，究竟这个端口有什么用？在高德未修复漏洞时，笔者开发了一个exp，发现这个漏洞可以得到用户的位置信息。

![](http://drops.javaweb.org/uploads/images/4ef4f2ff176868b2541df3eda32d058fc5743a4e.jpg)

我们仍然用Chrome模拟手机进行测试，访问`http://amap.com`，发现了对本地6677端口的请求，其目的是为了获取用户的地理位置信息。

![](http://drops.javaweb.org/uploads/images/be93839f0e52d4183e258b155c0a4b62309faf8d.jpg)

0x03 思考
=======

* * *

1.  Wormhole究竟该如何定义？
    
    显然出现这种类型漏洞的不仅仅是百度系app，也不止是moplus这个SDK，笔者认为wormhole应重新定义为那些因开放端口导致的漏洞。
    
    另外，目前列出的一些wormhole影响列表只是用了简单的静态扫描去匹配moplus的特征，事实上部分app仅仅是包含了这个库但没有实现，需要动态运行验证。
    
2.  怎样做到安全的开放端口？
    
    验证http_referer、remote-addr等显然不可靠
    
    端口随机？如何保证web页能确切访问？（facebook安卓版）
    
    SSLSocket?
    
3.  Web页面和app之间有必要通信么？
    
    开放端口不同于传统的client-server结构，传统的server端是透明的，但app上实现的server容易被逆向出关键逻辑，最终通信机制还是会被破解。
    
    Web页用一个token去访问app，app拿这个token进行服务器验证，然后再判断是否把敏感数据返回给web页？
    
4.  如何批量的检测这种开放端口的漏洞？
    
    静态检测ServerSocket等API? 部分app只是包含了一些API，但是没有到该部分代码的执行路径。
    
    动态检测？部分app在特定情况下才会开放端口，如豌豆荚在插入USB后才会开放端口。
    

Wormhole之后还有很多地方值得我们挖掘和研究，微博：m4bln，欢迎交流探讨！