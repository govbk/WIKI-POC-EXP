# Android应用安全开发之浅谈网页打开APP

**Author:伊樵，呆狐，舟海@阿里移动安全**

0x00 网页打开APP简介
==============

* * *

Android有一个特性，可以通过点击网页内的某个链接打开APP，或者在其他APP中通过点击某个链接打开另外一个APP（AppLink），一些用户量比较大的APP，已经通过发布其AppLink SDK，开发者需要申请相应的资格，配置相关内容才能使用。这些都是通过用户自定义的URI scheme实现的，不过背后还是Android的Intent机制。Google的官方文档[《Android Intents with Chrome》](https://developer.chrome.com/multidevice/android/intents)一文，介绍了在Android Chrome浏览器中网页打开APP的两种方法，一种是用户自定义的URI scheme（Custom URI scheme），另一种是“intent:”语法（Intent-based URI）。

第一种用户自定义的URI scheme形式如下：

![p1](http://drops.javaweb.org/uploads/images/5ca2a855793ef842d9cec75d087a2cfebc07c7d7.jpg)

第二种的Intent-based URI的语法形式如下：

![p2](http://drops.javaweb.org/uploads/images/0b9e71e9b9d36c2e5ffb7e72731258616f74e2d7.jpg)

因为第二种形式大体是第一种形式的特例，所以很多文章又将第二种形式叫Intent Scheme URL，但是在Google的官方文档并没有这样的说法。

**注意：**使用Custom URI scheme给APP传递数据，只能使用相关参数来传递数据，不能想当然的使用scheme://host#intent;参数;end的形式来构造传给APP的intent数据。详见3.1节的说明。

此外，还必须在APP的Androidmanifest文件中配置相关的选项才能产生网页打开APP的效果，具体在下面讲。

0x01 Custom Scheme URI打开APP
===========================

* * *

### 1.1 基本用法

需求：使用网页打开一个APP，并通过URL的参数给APP传递一些数据。 

如自定义的Scheme为：

![p3](http://drops.javaweb.org/uploads/images/57141df39c6c4177d53e0ff1a5dfaffe57d009ee.jpg)

**注意：**uri要用UTF-8编码和URI编码。

网页端的写法如下：

![p4](http://drops.javaweb.org/uploads/images/f8228d2e3b243000f3249a21f14b1e2326df41b9.jpg)

APP端接收来自网页信息的Activity，要在Androidmanifest.xml文件中Activity的intent-filter中声明相应action、category和data的scheme等。 

如在MainActivity中接收从网页来的信息，其在AndroidManifest.xml中的内容如下：

![p5](http://drops.javaweb.org/uploads/images/8d6fbdcf5bd1285ac37c5b6fe2e4d20c98b48df9.jpg)

在MainActivity中接收intent并且获取相应参数的代码：

![p6](http://drops.javaweb.org/uploads/images/6ccd152ac4022cfe004a16468ba3cbd049e49010.jpg)

另外还有以下几个API来获取相关信息： 

```
getIntent().getScheme(); //获得Scheme名称 
getIntent().getDataString(); //获得Uri全部路径 
getIntent().getHost(); //获得host

```

### 1.2 风险示例

常见的用法是在APP获取到来自网页的数据后，重新生成一个intent，然后发送给别的组件使用这些数据。比如使用Webview相关的Activity来加载一个来自网页的url，如果此url来自url scheme中的参数，如：`jaq://jaq.alibaba.com?load_url=http://www.taobao.com`。

如果在APP中，没有检查获取到的load_url的值，攻击者可以构造钓鱼网站，诱导用户点击加载，就可以盗取用户信息。

接2.1的示例，新建一个WebviewActivity组件，从intent里面获取load_url，然后使用Webview加载url：

![p7](http://drops.javaweb.org/uploads/images/1cc2c28751cd640414dbe1b34d16bcde3c79a552.jpg)

修改MainActivity组件，从网页端的URL中获取load_url参数的值，生成新的intent，并传给WebviewActivity：

![p8](http://drops.javaweb.org/uploads/images/e593b2858321faf1054f502800d21b51a3d8d58d.jpg)

网页端：

![p9](http://drops.javaweb.org/uploads/images/163b3769184a69dff56ad23f2ce7fcaa4a123efe.jpg)

钓鱼页面：

![p10](http://drops.javaweb.org/uploads/images/80b203f2f130aa6fae51be996e0977651a3eea56.jpg)

点击“打开钓鱼网站”，进入APP，并且APP加载了钓鱼网站：

![p11](http://drops.javaweb.org/uploads/images/c1e48d6cdc9a090171ede04939253a78b03377db.jpg)

**本例建议：**  
在Webview加载load_url时，结合APP的自身业务采用白名单机制过滤网页端传过来的数据，黑名单容易被绕过。

### 1.3 阿里聚安全对开发者建议

1.  APP中任何接收外部输入数据的地方都是潜在的攻击点，过滤检查来自网页的参数。
2.  不要通过网页传输敏感信息，有的网站为了引导已经登录的用户到APP上使用，会使用脚本动态的生成URL Scheme的参数，其中包括了用户名、密码或者登录态token等敏感信息，让用户打开APP直接就登录了。恶意应用也可以注册相同的URL Sechme来截取这些敏感信息。Android系统会让用户选择使用哪个应用打开链接，但是如果用户不注意，就会使用恶意应用打开，导致敏感信息泄露或者其他风险。

0x02 Intent-based URI打开APP
==========================

* * *

### 2.1基本用法

Intent-based URI语法：

![p12](http://drops.javaweb.org/uploads/images/344fd52de4b04fe89d878c5e00e029fd2c574d2d.jpg)

**注意：**第二个Intent的第一个字母一定要大写，不然不会成功调用APP。

**如何正确快速的构造网页端的intent？**

可以先建个Android demo app，按正常的方法构造自己想打开某个组件的Intent对象，然后使用Intent的toUri()方法，会得到Intent对象的Uri字符串表示，并且已经用UTF-8和Uri编码好，直接复制放到网页端即可，切记前面要加上“intent:”。 

如：

![p13](http://drops.javaweb.org/uploads/images/30629c5906b9fda6730c6f77f609d4723472990d.jpg)

结果：

![p14](http://drops.javaweb.org/uploads/images/2162c061a0c8398f7dae4ae2429bf3bec2e97dde.jpg)

S.load_url是跟的是intent对象的putExtra()方法中的数据。其他类型的数据可以一个个试。

如果在demo中的Intent对象不能传递给目标APP的Activity或其他组件，则其Uri形式放在网页端也不可能打开APP的，这样写个demo容易排查错误。

APP端中的Androidmanifest.xml的声明写法同2.1节中的APP端写法完全一样。对于接收到的uri形式的intent，一般使用Intent的parseUri()方法来解析产生新的intent对象，如果处理不当会产生Intent Scheme URL攻击。

**为何不能用scheme://host#intent;参数;end的形式来构造传给APP的intent数据？**

这种形式的intent不会直接被Android正确解析为intent，整个scheme字符串数据可以使用Intent的getDataSting()方法获取到。 

如对于：

![p15](http://drops.javaweb.org/uploads/images/16e62a2d4f411c4c14cf60a3600ab45592d5aef1.jpg)

在APP中获取数据：

![p16](http://drops.javaweb.org/uploads/images/383c5bcf92876d8b1b8e6d5ddc1041c2a9de4f42.jpg)

结果是：

![p17](http://drops.javaweb.org/uploads/images/4b23e46574f9d4fe8bb1b7f22cfdbcc22d409385.jpg)

由上图可知Android系统自动为Custom URI scheme添加了默认的intent。 

要想正确的解析，还需使用Intent的parseUri()方法对getDataString()获取到的数据进行解析，如：

![p18](http://drops.javaweb.org/uploads/images/f2bf46be5c032850a560cb4881fa5cb78133d8cc.jpg)

### 2.2 风险示例

关于Intent-based URI的风险我觉得[《Android Intent Scheme URLs攻击》](http://blog.csdn.net/l173864930/article/details/36951805)和[《Intent Scheme URL attack》](http://drops.wooyun.org/papers/2893)这两篇文章写的非常好，基本把该说的都都说了，我就不多说了，大家看这两篇文章吧。

### 2.3 阿里聚安全对开发者建议

上面两篇文章中都给出了安全使用Intent Scheme URL的方法：

![p19](http://drops.javaweb.org/uploads/images/5655d490e635ced2ccc746659b38dbb21a77cd1e.jpg)

除了以上的做法，还是不要信任来自网页端的任何intent，为了安全起见，使用网页传过来的intent时，还是要进行过滤和检查。

0x03 参考
=======

* * *

1.  [Android Intents with Chrome](https://developer.chrome.com/multidevice/android/intents)
2.  [Intent scheme URL attack](http://drops.wooyun.org/papers/2893) 
3.  [Android Appliaction Secure Design/Secure Coding Guidebook](http://www.jssec.org/dl/android_securecoding_en.pdf)
4.  [Handling App Links](http://developer.android.com/intl/zh-cn/training/app-links/index.html)
5.  [Android M App Links: 实现, 缺陷以及解决办法](http://www.jcodecraeer.com/a/anzhuokaifa/androidkaifa/2015/0718/3200.html)
6.  [Android Intent Scheme URLs攻击](http://blog.csdn.net/l173864930/article/details/36951805)