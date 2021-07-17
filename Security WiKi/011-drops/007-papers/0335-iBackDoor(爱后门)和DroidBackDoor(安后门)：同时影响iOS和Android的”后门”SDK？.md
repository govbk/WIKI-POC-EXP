# iBackDoor(爱后门)和DroidBackDoor(安后门)：同时影响iOS和Android的”后门”SDK？


**作者：蒸米@阿里移动安全，楚安@阿里威胁感知，迅迪@阿里移动安全**

0x00 FireEye报告
==============

* * *

iOS被XcodeGhost血洗一把之后，Android又被WormHole暴揍一顿。正当大家打算歇一歇的时候，FireEye的Zhaofeng等人又发表了一篇报告叫《iBackDoor: High-Risk Code Hits iOS Apps》。报告中指出FireEye的研究员发现了疑似”后门”行为的广告库mobiSage在上千个app中，并且这些app都是在苹果官方App Store上架的应用。通过服务端的控制，这些广告库可以做到：

1.  录音和截屏
2.  上传GPS信息
3.  增删改查app数据
4.  读写app的钥匙链
5.  发送数据到服务器
6.  利用URL schemes打开其他app或者网页
7.  安装企业应用

FireEye的研究员一共在App Store上发现了2,846个app包含具有“后门”特征的mobiSage广告库。并且这些广告库会不断的向服务器端发送请求，并获取执行指令的JavaScript脚本。FireEye的研究员还发现mobiSage广告库一共有17 不同的版本从5.3.3到6.4.4。然而在最新的mobiSage SDK 7.0.5版本中已经将这些”后门”特征删掉了。

0x01 iOS样本 - iBackDoor分析
========================

* * *

看到FireEye的报告后，我们第一时间拿到了iOS上的app样本进行分析（注：在我们分析时，该样本还没有下架）。在广告库的类MSageCoreUIManagerPlugin中，我们的确发现了报告中所提到的各种控制功能。其中包括非常高危的获取录音、截屏功能以及读取修改字符串的函数。

![enter image description here](http://drops.javaweb.org/uploads/images/424c05b98e6a8f11fb382be25e5a225d29d24ac2.jpg)

根据反编译的代码可以看到，iBackDoor在获取到服务器命令后会启动录音功能并将录音保存为audio_[编号].wav，并且可以通过sendHttpUpload函数将文件发送到服务器上。

![enter image description here](http://drops.javaweb.org/uploads/images/3f88ddf2eda72b20b4a2446a1993bb953cbff8d2.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/32f53c59b616c11d287943f082550a0bd779c99f.jpg)

iBackDoor还可以截取当前屏幕的内容，反编译代码如下：

![enter image description here](http://drops.javaweb.org/uploads/images/56cc4804f51ae4fbe36cd7dbc502acb49db953aa.jpg)

iBackDoor还可以读取keychain的数据，也就是iOS上的app用来保存密码信息的容器：

![enter image description here](http://drops.javaweb.org/uploads/images/52f1c24a44b84d594d1a593a671a294cb1caa948.jpg)

一个广告sdk，为什么需要录音，截屏和读取密码等功能呢？的确非常可疑。

![enter image description here](http://drops.javaweb.org/uploads/images/48c7ef30008cdf38f264ff7882fc5ff1b5d43641.jpg)

除此之外，iBackDoor还可以根据服务器的指令调用任意的URL Schemes，也就是说XcodeGhost可以干的事情（打开钓鱼网页，安装企业应用等）iBackDoor也都可以干。比如如下是安装企业应用的反编译代码：

![enter image description here](http://drops.javaweb.org/uploads/images/883e2980200b09e19ca7cfd8177969c5834b6764.jpg)

0x02 数据流量分析
===========

* * *

通过分析反汇编代码我们发现中了iBackDoor的app会根据本地的msageJS脚本执行相应的指令。除此之外，iBackDoor还会发送post请求到entry.adsage.com去检查更新，如果有新的JS命令脚本就会到mws.adsage.com下载。

于是我们分析了一下entry.adsage.com和mws.adsage.com的DNS解析和流量数据：

![enter image description here](http://drops.javaweb.org/uploads/images/d7c0cde3caa927f01b68f1f19bb5b6152e236db9.jpg)

根据DNS解析趋势，可以看到每天请求的数据并没有太大的浮动。但有意思的是，在对流量的分析中，除了adv-ios-*-min.zip外我们还发现了很多机器对adv-android-*-min.zip的下载请求。难道除了iOS的app，android上的app也难逃魔爪？

![enter image description here](http://drops.javaweb.org/uploads/images/951665278f9f4743f4b92fba2051f8fc4161badd.jpg)

并且这个请求的数量还不小，在我们有限的监测流量中，光九月份就有4亿多次对adsage.com的数据发送。并且，最近半年内至少有超过50000次对更新脚本adv-ios-*-min.zip或adv-android-*-min.zip的下载请求。

0x03 Android样本 - DroidBackDoor分析
================================

* * *

上文讲到了我们除了iOS的payload还发现了Android的payload，我们把这个payload下载下来一看，发现原来就是个动态加载的dex文件。这个dex文件包含了非常多的高危代码，我们把它称为DroidBackDoor。DroidBackDoor除了广告sdk都会做的获取手机各种信息，下载和安装任意apk外，还可以获取用户的坐标、打开任意网页、打电话、发短信等。

收集用户的imei，root信息，地理位置，wifi信息等几十种信息：

![in1](http://drops.javaweb.org/uploads/images/aee9102d83e65f2fbda9cc8190a4dae6d817e09b.jpg)

![in2](http://drops.javaweb.org/uploads/images/24533646293c7c42ea007b866aa47b45648a1ccd.jpg)

![in3](http://drops.javaweb.org/uploads/images/e7cf847a0c6360d31a7fc901a8f402617c088188.jpg)

![in4](http://drops.javaweb.org/uploads/images/f5497cdc43face016fe4425ea7301dbf9c76177e.jpg)

![in5](http://drops.javaweb.org/uploads/images/cd61793de7cb9dbf1ce2e79e70e57e53efef0ef7.jpg)

![in6](http://drops.javaweb.org/uploads/images/7b4ccd5da1a2e2e67b3d81d92772659fa46b1d67.jpg)

![in7](http://drops.javaweb.org/uploads/images/10ad6ee2341ad8d33b97a5eaf1726dff0265ad32.jpg)

获取用户坐标的反汇编代码：

![enter image description here](http://drops.javaweb.org/uploads/images/a453188955906ecdc6d5f75ebc5216d077c573da.jpg)

打开任意网页的反汇编代码：

![enter image description here](http://drops.javaweb.org/uploads/images/e151f7678819f5f9f3b417d65437dc5e656d28e0.jpg)

打电话的反汇编代码：

![enter image description here](http://drops.javaweb.org/uploads/images/8f7d827c1f6f0ba31a9fb1d5680f776826f8ab62.jpg)

发短信的反汇编代码：

![enter image description here](http://drops.javaweb.org/uploads/images/7c96319c4b43b57a5ee9824872ccf9c79d863d64.jpg)

我们将提取的mobisage的特征去后台数据库查询，发现Android上也有超过2000款的app使用了mobisage的sdk。

0x04 网站分析
=========

* * *

通过相关域名网站(http://www.adsage.cn/index.html)，可以知道这家公司的名字叫艾德思奇，并且有很多知名的合作伙伴和案列。我们建议所有使用了这个SDK的厂商应立刻检查自己产品中是否被插入了高危风险的代码，以免被苹果下架。

0x05 总结
=======

* * *

虽然这次”后门”SDK同时影响了iOS和Android，但根据我们的数据分析结果发现影响力是远远不及XcodeGhost和WormHole的。所以用户不用太过担心，在受影响的app下架之前尽量不要安装不知名应用，并记得及时更新自己的app。

0x06 参考资料
=========

* * *

1.  https://www.fireeye.com/blog/threat-research/2015/11/ibackdoor_high-risk.html