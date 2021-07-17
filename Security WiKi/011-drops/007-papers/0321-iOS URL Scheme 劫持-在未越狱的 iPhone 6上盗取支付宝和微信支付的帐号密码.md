# iOS URL Scheme 劫持-在未越狱的 iPhone 6上盗取支付宝和微信支付的帐号密码


0x00 前言
=======

* * *

微博:weibo.com/zhengmin1989

*   该漏洞是 iOS 系统漏洞,和支付宝,微信 app 无关。本文只是拿支付宝和微 信作为演示漏洞的应用,其他应用同样可以中招,转发者请勿断章取义。
    
*   此漏洞是另一 个漏洞,和“在非越狱的 iPhone 6 (iOS 8.1.3) 上进行钓鱼攻击 (盗取 App Store 密码)”上利 用的漏洞无关,本人不会干用一个漏洞写两个文章灌水的事情。
    

该漏洞最早是由我在 FireEye 的同事 hui, Song jin 和 lenx 发现的,因为该漏洞利用简单,修 复却非常复杂,所以在 iOS 8.2 上还是未能修复。虽然 iOS 尚未修复,但 app 本身还是可以 有防护的方法,本人在文章最后会提出一些应急的解决方案以供开发人员参考。

0x01 DEMO
=========

* * *

首先来看 demo: 在未越狱的 iPhone6(iOS 8.2)上盗取支付宝帐号密码。[Youtube](https://www.youtube.com/watch?v=p86Kv1uHO-s)(需翻墙):[腾讯视频](http://v.qq.com/page/p/d/s/p0149z3tgds.html)

在未越狱的 iPhone6(iOS 8.2)上盗取微信支付密码。[Youtube](https://www.youtube.com/watch?v=4SfCVGReyKI)(需翻墙)[ku6视频](http://v.ku6.com/show/yKdd4P9tTaznQUK6fQFPIA...html?from=my)

0x02 DEMO 细节分析(支付宝)
===================

* * *

在 iOS 上,一个应用可以将其自身”绑定”到一个自定义 URL Scheme 上,该 scheme 用于 从浏览器或其他应用中启动该应用。这个设计非常类似于 android 上的 broadcast 和 broadcast receiver,但远远没有 android 上的复杂。美团利用支付宝付款的整个过程如图一所示:美团 首先将订单信息通过 URL Scheme 发送给 Alipay,Alipay 收到订单信息,调用支付界面,用户 在 Alipay 上完成支付后,Alipay 再发送一个 URL Scheme 给美团,美团收到付款信息后,显 示团购成功的界面。

![enter image description here](http://drops.javaweb.org/uploads/images/d2bd4ca1766355620dd25d12c2af9d9a25af8519.jpg)

图一、正常支付流程

但因为 URL scheme 这个机制太简单了,完全没有考虑有多个 app 声明同一个 URL Scheme 的情况,也没有权限管理之类的方案。在 iOS 官方说明中:“在多个应用程序注册了同一种 URLScheme 的时候,iOS 系统程序的优先级高于第三方开发程序。但是如果一种URLScheme 的注册应用程序都是第三方开发的,那么这些程序的优先级关系是不确定的。”实际上,经 过我们的测试,这个顺序是和 Bundle ID 有关的,如果精心构造 Bundle ID,iOS 总是会调用 我们 app 的 URL Scheme 去接收相应的 URL Scheme 请求。那么问题来了,如果我们精心构 造一个 app 并声明“alipay”这个 URL Scheme 会怎么样呢?

结果就如 demo 中所演示的那样,后安装的 FakeAlipay 应用劫持了美团与支付宝之间的支付 流程,并且可以在用户毫无意识情况下获取用户的帐号,支付密码,以及帮用户完成支付。 整个过程如图二所示:FakeAlipay 在收到美团发来的订单信息后,构造了一个和支付宝一样 的登陆界面,用户在输入了帐号密码后,FakeAlipay 会把帐号密码以及订单信息发送到黑客 的服务器上,黑客在获得了这些信息后,可以在自己的 iOS 设备上完成支付,并把支付成功 的 URL Scheme 信息发回给 FakeAlipay,FakeAlipay 再把支付成功的 URL Scheme 信息转发给 美团。因为时间原因,demo 做得比较粗糙,没有做转发信息给美团这一部分的演示,但绝 对是可行的。

![enter image description here](http://drops.javaweb.org/uploads/images/3120ae5754225d8f2f444043ebcbd0937928bebf.jpg)

图二、劫持后的支付流程

这种攻击可以成功的原因除了 iOS 本身的漏洞外,支付宝也有一定的责任。那就是发给支付 宝的订单信息并不是绑定当前设备的。因为这个原因,黑客可以在其他的 iOS 设备上完成支 付。 同样是因为不绑定当前设备的问题,黑客甚至可以先在自己的设备上生成好订单,然 后在用户打开支付宝支付的时候把订单替换掉,让用户给黑客的订单买单。

0x03 DEMO 细节分析(微信)
==================

* * *

基本上和支付宝一样,不过支付时只需要提供 6 位支付密码,如 果想要得到微信帐号密码的话,还需要构造一个假的登陆界面。当然了,你可能会说有短信 验证,但是如果整个登录界面都是伪造的话,用户也会乖乖的帮你输入短信验证码的。并且, 在 iOS 8.1 之前,iOS 的短信也存在监控漏洞,具体请参考我们 ASIACCS 的论文。

好吧,讲到这里肯定又有人说:你的漏洞是挺严重的,但还是得往我机器上装 app 啊。我从 来不用什么 pp 助手,同步推之类的,也不装什么企业应用,平时只在 AppStore 上下载,因 为有苹果的审核,所以我肯定不会中招的。呵呵,苹果的审核真的信得过么?请看第二个 demo: Google Chrome URL Scheme 劫持

[Youtube](https://www.youtube.com/watch?v=uqZPelheVdM)(需翻墙)[腾讯视频](http://v.qq.com/page/x/d/4/x0149k4red4.html)

![enter image description here](http://drops.javaweb.org/uploads/images/9ff0e5beda26633994002fce528ad87c64090eb1.jpg)

图三、Google Chrome URL Scheme 劫持

Google 公司不比阿里差吧?Google Chrome 可以算是 Google 在 iOS 上最重要的应用之一了吧? 可惜的是,在该 demo 中 Google 公司的 Chrome 应用已经非常不幸的被 App Store 下载的 app 劫持掉了。如图三所示:演示用的 app 会利用 Google Chrome 的 URL Scheme 去打开 Google.com 这个网站。在机器上只安装 Chrome 的情况下,app 会跳转到 Chrome 打开 Google.com。但是当我们在 App Store 下载完一个叫 BASCOM Browser 的 app 之后,app 却会 跳转到 BASCOM Browser 打开 Google.com。经过统计,App Store 上有大量的应用声明了 Chrome 以及 FaceBook 的 URL scheme,并且他们的开发者并不属于 Google 和 Facebook。这 说明 Apple 根本就没有保护那些热门应用的 URL Scheme 的想法,上传的 App 无论声明什么样的 URL Scheme,苹果都会通过审核的。所以说,不光 Chrome,Facebook 有危险,支付宝, 微信啥的也逃不过这一劫。

0x04 解决方案
=========

* * *

1. 针对 iOS 系统。
-------------

* * *

因为 Bundle ID 在 App Store 上是唯一的(类似 Android 上的 package name)苹果可以限制 iOS 应用不能注册别的应用的 Bundle ID 作为 URL Scheme。这 样的话,使用自己的 Bundle ID 作为 URL Scheme 的接收器就会变的安全很多。

2. 针对第三方应用
----------

* * *

既然苹果不发布补丁保护第三方应用。第三方应用就没有办法了么? 不是的,这里至少有两种方法可以检测自己应用的 URL Scheme 是否被 Hijack:

(1)、应用本 身可以发送一条 URL Scheme 请求给自己,如果自己可以接收到的话,说明 URL Scheme 没 有被劫持,如果不能收到的话,就说明被劫持了,这时候可以提醒用户卸载有冲突的 app。

代码如下:

```
[[UIApplication sharedApplication] openURL:[NSURL URLWithString:@“alipay://test“]];

```

(2)、利用 MobileCoreServices 服务中的 applicationsAvailableForHandlingURLScheme()方法可以 所有注册了该 URL Schemes 的应用和处理顺序,随后应用就可以检测自己,或者别人的 URL Scheme 是否被劫持了。代码如下:

```
Class LSApplicationWorkspace_class = objc_getClass("LSApplicationWorkspace");
NSObject* workspace =
[LSApplicationWorkspace_class performSelector:@selector(defaultWorkspace)]; NSLog(@"openURL: %@",[workspace performSelector:@selector(applicationsAvailableForHandli ngURLScheme:)withObject:@"alipay"]);

```

在任意 app 下运行这个函数,可以返回 URL 处理的顺序,比如运行结果是:

```
2015-03-18 15:34:37.695 GetAllApp[13719:1796928] openURL: (
"<LSApplicationProxy: 0x156610010> com.mzheng.GetAllApp", "<LSApplicationProxy: 0x1566101f0> com.mzheng.Alipay", "<LSApplicationProxy: 0x15660fc30> com.alipay.iphoneclient"
)

```

说明有三个 app 都声名了 alipay 这个 URL shceme,并且会处理这个请求的是 "com.mzheng.GetAllApp",而不是支付宝。

0x05 文章更新
=========

* * *

刚说完支付宝,微信逃不过这一劫,我们已经在 App Store 上发现了 劫持了支付宝的真实案例。

来看 demo: 战旗 TV 劫持支付宝 URL Scheme Youku:

当用户想要使用支付宝支付的时候,却跳转到了战旗 TV。这里想问一下战旗 TV,你到底想 要干些什么呢?:-)

PS:各大公司是不是要开始推送 iOS 手机安全助手了?

2015/03/23文章更新:战旗tv已经得到反馈，正在紧急修复bug。

0x06 参考文献:
==========

* * *

1.iOS Masque Attack:[LINK](https://www.fireeye.com/blog/threat-research/2015/02/ios_masque_attackre.html)

￼ 2.Min Zheng, Hui Xue, Yulong Zhang, Tao Wei, John C.S. Lui "Enpublic Apps: Security Threats Using iOS Enterprise and Developer Certificates", ACM Symposium on Information, Computer and Communications Security (ASIACCS'15), Singapore, April 2015

3.在非越狱的 iPhone 6 (iOS 8.1.3) 上进行钓鱼攻击 (盗取 App Store 密码):[LINK](http://blog.csdn.net/zhengminwudi/article/details/43916791)