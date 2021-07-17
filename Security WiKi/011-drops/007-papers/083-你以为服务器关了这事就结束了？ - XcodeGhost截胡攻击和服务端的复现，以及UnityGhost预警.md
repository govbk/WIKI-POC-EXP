# 你以为服务器关了这事就结束了？ - XcodeGhost截胡攻击和服务端的复现，以及UnityGhost预警

作者：没羽，蒸米，阿刻，迅迪 @ 阿里移动安全

0x00 序
======

* * *

截胡，麻将术语，指的是某一位玩家打出一张牌后，此时如果多人要胡这张牌，那么按照逆时针顺序只有最近的人算胡，其他的不能算胡。现也引申意为断别人财路，在别人快成功的时候抢走了别人的胜利果实。

虽然XcodeGhost作者的服务器关闭了，但是受感染的app的行为还在，这些app依然孜孜不倦的向服务器（比如init.icloud-analysis.com，init.icloud-diagnostics.com等）发送着请求。这时候黑客只要使用DNS劫持或者污染技术，声称自己的服务器就是”init.icloud-analysis.com”，就可以成功的控制这些受感染的app。具体能干什么能，请看我们的详细分析。

另外，有证据表明unity 4.6.4 – unity 5.1.1的开发工具也受到了污染，并且行为与XcodeGhost一致，更恐怖的是，还有证据证明XcodeGhost作者依然逍遥法外，具体内容请查看第三节。

PS：虽然涅槃团队已经发出过攻击的demo了[2](http://drops.javaweb.org/uploads/images/91511ef68becbfa79671d89c46955bd2b231c280.jpg)，但很多细节并没有公布。所以我们打算在这篇文章中给出更加详细的分析过程供大家参考。

0x01通信协议分析
==========

* * *

在受感染的客户端App代码中，有个Response方法用于接收和处理远程服务器指令。

![enter image description here](http://drops.javaweb.org/uploads/images/eb40f7029ab50e3f3acf83e57bb3b37862949b76.jpg)

Response方法中根据服务器下发的不同数据，解析成不同的命令执行，根据我们分析，此样本大致支持4种远程命令，分别是：设置sleep时长、窗口消息、url scheme、appStore窗口。

通过4种远程命令的单独或组合使用可以产生多种攻击方式：比如下载安装企业证书的App；弹AppStore的应用进行应用推广；弹钓鱼页面进一步窃取用户信息；如果用户手机中存在某url scheme漏洞，还可以进行url scheme攻击等。

![enter image description here](http://drops.javaweb.org/uploads/images/91511ef68becbfa79671d89c46955bd2b231c280.jpg)

其通信协议是基于http协议的，在传输前用DES算法加密http body。Response方法拿到服务器下发送的数据后，调用Decrypt方法进行解密：

![enter image description here](http://drops.javaweb.org/uploads/images/5c50c03fe35561affa4cecbc14eab821c2560d91.jpg)

如果解密成功，将解密后的数据转换成JSON格式数据：

![enter image description here](http://drops.javaweb.org/uploads/images/dfce02a526b68100a668ea692f6abbb19b9d9c9c.jpg)

然后判断服务器端下发的数据，执行不同的操作。如下面截图是设置客户端请求服务端器sleep时长的操作：

![enter image description here](http://drops.javaweb.org/uploads/images/6b8358ca9f8b85557b55051f3333b52218771100.jpg)

0x2恶意行为分析及还原
============

* * *

在逆向了该样本的远程控制代码后，我们还原了其服务端代码，进一步分析其潜在的危害。

首先我们在服务端可以打印出Request的数据，如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/34778e5d76b0d85ad9c1c114ec06966253814e87.jpg)

红色框标记的协议的头部部分，前4字节为报文长度，第二个2字节为命令长度，最后一个2字节为版本信息，紧跟着头部的为DES的加密数据。我们在服务端将数据解密后显示为：

![enter image description here](http://drops.javaweb.org/uploads/images/dc26aa1624b359377a9450d64f5f2275b23e68af.jpg)

这里有收集客户端信息上传到控制服务器。

同样我们返回加密数据给客户端：

![enter image description here](http://drops.javaweb.org/uploads/images/f762583ce149f7f106037ca2a891f7f0d2d1a4a9.jpg)

明文信息为：

![enter image description here](http://drops.javaweb.org/uploads/images/e2017336ec9ff699ed05ee5c64638b99796e95f0.jpg)

客户端根据App的运行状态向服务端提供用户信息，然后控制服务器根据不同的状态返回控制数据：

![enter image description here](http://drops.javaweb.org/uploads/images/5c7e00d68764307ba4aa9d80b0b8ebf647c54f4f.jpg)

恶意行为一 定向在客户端弹（诈骗）消息
-------------------

该样本先判断服务端下发的数据，如果同时在在“alertHeader”、“alertBody”、“appID”、“cancelTitle”、“confirmTitle”、“scheme”字段，则调用UIAlertView在客户端弹框显示消息窗口：

![enter image description here](http://drops.javaweb.org/uploads/images/72e4b148da42e4bcf481931fc09da3f18be2da4b.jpg)

消息的标题、内容由服务端控制

![enter image description here](http://drops.javaweb.org/uploads/images/e5a6c9fc8cad3766f7b0de8640eda798bed40e2d.jpg)

客户端启动受感染的App后，弹出如下页面：

![null](http://drops.javaweb.org/uploads/images/eb8753a800bf6eb2065940439a48fcbc40c6f4ad.jpg)

恶意行为二 下载企业证书签名的App
------------------

当服务端下发的数据同时包含“configUrl”、“scheme”字段时，客户端调用Show()方法，Show()方法中调用UIApplication.openURL()方法访问configUrl：

![enter image description here](http://drops.javaweb.org/uploads/images/bd9ec8e167d4bd3b9fc447aad4c7b8242c73efab.jpg)

通过在服务端配置configUrl，达到下载安装企业证书App的目的：

![enter image description here](http://drops.javaweb.org/uploads/images/eba5365095e2056a30964b197cf685c9200eac7f.jpg)

客户端启动受感染的App后，目标App将被安装(注意:演示应用为测试应用，不代表恶意软件推广该应用)：

![null](http://drops.javaweb.org/uploads/images/ead5cd0dffaefa605dbb2bb853b7c23ee02a0a3b.jpg)

![null](http://drops.javaweb.org/uploads/images/eb928db2c5c22ec1e4a07c8f30c1bea2e78881e8.jpg)

demo地址：http://v.youku.com/v_show/id_XMTM0Mjg0MDc4OA==.html

恶意行为三 推送钓鱼页面
------------

通过在服务端配置configUrl，达到推送钓鱼页面的目的：

![enter image description here](http://drops.javaweb.org/uploads/images/0ef2d4052212c3c78f7921898cf295887ca06dc4.jpg)

客户端启动受感染的App后，钓鱼页面被显示：

![null](http://drops.javaweb.org/uploads/images/0a3ffe01b24fb02f57e907d3640c24211aeea57b.jpg)

demo地址：http://v.youku.com/v_show/id_XMTM0Mjg0NTM2NA==.html

恶意行为四 推广AppStore中的应用
--------------------

通过在服务端配置configUrl，达到推广AppStore中的某些应用的目的：

![enter image description here](http://drops.javaweb.org/uploads/images/a151e3cc9de7190022ab6524a8f5bbfb6d361596.jpg)

phishing1.html页面内容：

![enter image description here](http://drops.javaweb.org/uploads/images/0d3bc7a4745a67ad242bb0b6a053abb4a8688bd5.jpg)

客户端启动受感染的App后，自动启动AppStore，并显示目标App的下载页面：

![null](http://drops.javaweb.org/uploads/images/e4296fc0d4cbd87570660f5ff48094619e684aca.jpg)

demo地址：http://v.youku.com/v_show/id_XMTM0Mjg0NDA4MA==.html

0x03 UnityGhost?
================

* * *

在大家以为一切都完结的时候，百度安全实验室称已经确认”Unity-4.X的感染样本”。并且逻辑行为和XcodeGhost一致，只是上线域名变成了init.icloud-diagnostics.com。这意味，凡是用过被感染的Unity的app都有窃取隐私和推送广告等恶意行为。

![enter image description here](http://drops.javaweb.org/uploads/images/42dca42cad871b0d41f674db41bb7bdaa555e32b.jpg)

Unity是由Unity Technologies开发的一个让玩家创建诸如三维视频游戏、实时三维动画等类型互动内容的多平台的综合型游戏开发工具，是一个全面整合的专业游戏引擎。很多有名的手机游戏比如神庙逃亡，纪念碑谷，炉石传说都是用unity进行开发的。

更令人恐怖的是，在百度安全实验室确认后没多久，大家就开始在网上寻找被感染的Unity工具，结果在我搜到一个Unity3D下载帖子的时候发现”codeFun与2015-09-22 01:18编辑了帖子”！？要知道codeFun就是那个自称XcodeGhost作者的人啊。他竟然也一直没睡，大半夜里一直在看大家发微博观察动静？随后发现大家知道了Unity也中毒的事情，赶紧去把自己曾经投毒的帖子删了？

![enter image description here](http://drops.javaweb.org/uploads/images/a6d7c090091d26199e43bdb45f8d7cd72addcb26.jpg)

现在再去看那个帖子已经被作者删的没有任何内容了。。。 http://game.ceeger.com/forum/read.php?tid=21630&fid=8

![enter image description here](http://drops.javaweb.org/uploads/images/9a513e4857967476039f32e27bd5dac55e8a8d2b.jpg)

但根据XcodeGhost作者没删之前的截图表明，从unity 4.6.4 – unity 5.1.1的开发工具都有可能被投毒了！

0x04 总结
=======

* * *

虽然病毒作者声称并没有进行任何广告或者欺诈行为，但不代表别人不会代替病毒作者进行这些恶意行为。并且作者依然还在逍遥法外！所以立刻！马上！删掉那些中毒的app吧！

0x05 参考资料
=========

* * *

1.  涅槃团队：Xcode幽灵病毒存在恶意下发木马行为 http://drops.wooyun.org/papers/8973
2.  XcodeGhost 源码 https://github.com/XcodeGhostSource/XcodeGhost

0x06 更新
=======

* * *

1 在百度安全实验室的帮助下，我们已经拿到了UnityGhost的样本。基本信息如下：

```
$shasum libiPhone-lib-il2cpp.a-armv7-master.o
625ad3824ea59db2f3a8cd124fb671e47740d3bd  libiPhone-lib-il2cpp.a-armv7-master.o

$ file libiPhone-lib-il2cpp.a-armv7-master.o
libiPhone-lib-il2cpp.a-armv7-master.o: Mach-O object arm

```

UnityGhost样本的行为和XcodeGhost非常相似，基本函数如下：

![enter image description here](http://drops.javaweb.org/uploads/images/e6c90a226ac3a64b3b2aaed61a4debfd6552743e.jpg)

UnityGhost在启动时会检测是否是在虚拟机和调试器中运行，如果是则不产生恶意行为：

![enter image description here](http://drops.javaweb.org/uploads/images/93522e58480b03347ed99f93a9cd60b6008bdfa0.jpg)

UnityGhost同样也会收集用户手机的各种信息（时间，bundle id(包名)，应用名称，系统版本，语言，国家等）并上传到一个新的服务器”http://init.icloud-diagnostics.com”：

![null](http://drops.javaweb.org/uploads/images/5e7edb5877640b0ba0227ecdc080f3e9d023e455.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/d14bfcc4d5dea600321b185265b786071d68e09f.jpg)

在接收到服务器返回的指令后，UnityGhost同样也可以进行多种恶意行为：下载安装企业证书的App；弹AppStore的应用进行应用推广；弹钓鱼页面进一步窃取用户信息；如果用户手机中存在某url scheme漏洞，还可以进行url scheme攻击等。 弹出诈骗对话框用到的函数：

![enter image description here](http://drops.javaweb.org/uploads/images/74d799918b7fd718451b84d96e96f8aaad3edbfd.jpg)

弹出网页或者推广应用用到的函数：

![enter image description here](http://drops.javaweb.org/uploads/images/471dde5e20b8ba4c5bac218c8d9e01f5af5e386d.jpg)