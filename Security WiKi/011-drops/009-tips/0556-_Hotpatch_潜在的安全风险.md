# "Hotpatch"潜在的安全风险

author:屎蛋@平安产品安全团队

0x00 “Hotpatch”简介
=================

* * *

IOS App的开发者们经常会出现这类问题：当一个新版本上线后发现存在一个严重的bug，有可能因为一个逻辑问题导致支付接口存在被薅羊毛的风险，这个时候能做的只能是赶快修复完安全问题并提交到appstore审核，在急忙推送用户尽快更新，避免为此导致的严重安全后果买单。为了解决此类问题遍有了实现给App应用”实时打补丁”这类方案，目前大致有两种主流的“热修复”的项目。

根据基本原理可以分为下面两种，

原理同为构建JS脚本与Object-C语言之间转换的桥梁。

1.  WaxPatch(Lua调用OC)
    
2.  JSPatch(Javascript调用OC)
    

”热修复” 技术虽然极大的减少了开发者更新补丁的时间与商业成本，但却将Apple努力构建的安全生态系统——Apple Store对上架App的严格审查规则置于高风险下。通过这种技术可以在上线以后直接更新App原生代码，从而从某种意义上绕过了Apple Store的审查规则。

0x01 原理分析
=========

* * *

这种手段是通过IOS内置的JavaScriptCore.framework 微型框架来实现的，它是Apple官方在IOS7以后推出的主要是用来提供一个在Objective-C中执行Javascript环境的一个框架。

JSPatch并没有使用JSExport协议与OC代码进行互调，而是使用了JSBinding(Javascript与OC代码交互的接口)与Objective-C中的runtime(运行时)，采用了JavaScriptCore.framework框架作为解析javascript的引擎，与客户端的代码实时交互动态修改OC方法的一种方案。

对客户端整个对象的转换流程如下：

> 使用JavaScriptCore.framework作为Javascript引擎解析JavaScript脚本，执行JavaSript代码并与Objective-C端的代码进行桥接。另一方面则是使用Objective-C runtime中的method swizzling的方式和ForwardInvocation消息转发机制使得在JavaScript脚本中可以调用任意Objective-C方法。

![](http://drops.javaweb.org/uploads/images/ffe66278f8231613eb7287ee15f5344d37002676.jpg)

总的执行过程：

> Javascript-> JavaScriptCore Framework-> Objective-C->runtime->动态修改IMP
> 
> (更像与Android的Webview代码执行？)

下图展示了在客户端代码中如何嵌入JSPatch。

![](http://drops.javaweb.org/uploads/images/ec76015a65c488171faf537eadf5456be20e211e.jpg)

在此之后客户端每次启动时都会下载请求这段js脚本来更新客户端代码。

0x02 存在的安全隐患
============

* * *

JSPatch的确给IOS开发者们带来了很多好处，但是这么高的权限如果使用不当往往会有恶意用户会用它来做一些坏事。

可以预见的风险主要来自以下方面：

一 传输过程安全问题
----------

服务端在下发JS的更新补丁时如果传输过程中如果没有使用Https或者对Https的证书未做严格校验，又或者没有做数据防篡改的方案，更新的补丁在传输过程中被恶意攻击者劫持篡改了传输补丁数据，就可以导致非常大的危害，比如命令执行什么的。。

实践出真知，由于没有找到合适的App做演示，我们使用虚拟机做跳板机来简单搭建一个中间人的场景：

虚拟机ip: 10.180.145.17 这台机器充当中间人的角色。

本机搭建一个简单的服务器，用于App的更新脚本服务器，用于下发jspatch脚本。

![](http://drops.javaweb.org/uploads/images/10f8733c22dfd0dbe8f0b8e5dbd63f927b53d1de.jpg)

在测试App中的Object-C加入要更新补丁的url(嵌入到JPEngine中)：

![](http://drops.javaweb.org/uploads/images/8979dc2ae13d8edd3af940cfeee7c85777ef74cf.jpg)

url:`http://10.180.144.1:8081/static/js/test.js`

![](http://drops.javaweb.org/uploads/images/043a19f182dae8a018c9f2eb6ed668400a85e359.jpg)

这段js补丁本来是要在屏幕打印222 这几个数字,但是App在更新补丁时并没有使用Https安全传输，也没有对传输数据进行防篡改，如以下几种场景：

1.  传输过程没有使用Https
    
2.  传输过程使用了Https，但是对Https的证书没有做正确校验。
    
3.  传输过程没有使用Https，也没有对数据做防篡改。
    

整个传输过程是明文可见的:

![](http://drops.javaweb.org/uploads/images/159d5c4142f2e7841358b1818d06c21c378b9802.jpg)

加载补丁后正常显示：

![](http://drops.javaweb.org/uploads/images/e87d77c9197ee55ae5ca67d3e0fb2c4fbd8ff42f.jpg)

之后我们新建一个下发的更新补丁：

![](http://drops.javaweb.org/uploads/images/34189ce69e0586f9482518b8f24c7b82aa16617a.jpg)

Apple默认是不允许调用私有api的(在App上线时会经过App Store的审查)，但是在使用了JSPatch引擎后，可以直接调用私有的Api来获取设备私密信息。

这里加载了一个Accounts.framework, 用来获取设备中的帐号信息。

替换远程加载的Js：

![](http://drops.javaweb.org/uploads/images/35110d6d514898fc71f849cc4670550e4f458c80.jpg)

之后成功利用JSPatch更新了客户端的代码，读取出设备的帐号信息:46个

![](http://drops.javaweb.org/uploads/images/456fd7d6e1b73664b4faaf030fde5563582bfffa.jpg)

46个帐号被显示在App中。

此外还有很多private frameworks 可以拿来调用，当然这只适合越狱手机了，这种权限是很可怕的。

![](http://drops.javaweb.org/uploads/images/6ffa8bc8c75748f3509add1c9457786bdfd2aa8b.jpg)

二 恶意的第三方SDK
-----------

同传输过程安全一样，第三方的SDK极大的扩展了App的功能，但是不能保证这些SDK的开发者不存在恶意的开发者，恶意的SDK可以利用JSPatch下发恶意脚本，利用App的权限窃取敏感数据或者对系统做一些敏感操作。

三 本地篡改下载更新的javascript脚本
-----------------------

如果下载到了本地更新脚本没有做加密，通过篡改本地的更新补丁，可以修改为执行任意OC代码的js脚本，同样可以执行任意代码。

0x03 其他面临的风险
============

* * *

补丁传输安全
------

在使用JSPatch时一定要注意传输过程的安全，使用Https传输，或使用作者推荐的RSA检查下发的JS补丁，或者使用作者提供的Loader。

第三方SDK
------

在使用第三方的SDK时需要注意检查是否嵌入了JSPatch，防止利用App的权限来对系统做一些坏事，或者窃取App的用户信息。

本地存储
----

更新补丁在本地存储时需要对存储的补丁做加密，防止数据被篡改造成代码执行。

参考文献

*   [https://www.fireeye.com/blog/threat-research/2016/01/hot_or_not_the_bene.html](https://www.fireeye.com/blog/threat-research/2016/01/hot_or_not_the_bene.html)
*   [https://github.com/bang590/JSPatch/](https://github.com/bang590/JSPatch/)