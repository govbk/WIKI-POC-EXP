# 无处不在的监控: Hacking Team:WP8 监控代码分析

0x00 背景
=======

* * *

最近Hacking Team被黑客入侵,近400GB的资料泄漏,在安全界炒的沸沸扬扬.其中泄漏的资料包括:源代码，0day，资料入侵项目相关信息，相关的账户密码，数据及音像资料，办公文档，邮件及图片。

Hacking Team在意大利米兰注册了一家软件公司，主要销售入侵及监视功能的软件。其远程控制系统可以监测互联网用户的通讯，解密用户的加密，文件及电子邮件，记录各种通信信息，也可以远程激活用户的麦克风及摄像头。其产品在几十个国家使用

![enter image description here](http://drops.javaweb.org/uploads/images/c2d8149a66a7971f17db3b9a0a87cac5c9047fcf.jpg)

在源代码中有各个操作系统平台的远程控制软件源码,`RCS（Remote Control System）`。经过我们的分析，发现其监控内容不可谓不详尽。`Android,blackberry，ios，windows，window phone，symbian`均有与之对应的监控代码。

在源码中，rcs为前缀的源码文件是其远控功能，包括代理 控制 监控数据库 隐藏ip 等，而针对特定平台架构的是以core前缀命名。其中和相关window phone监控代码在`core-winphone-master.zip`文件中。其主要用于实时手机系统的系统状态信息如（电池状态，设备信息，GPS地址位置），联系人，短信记录，日历日程安排，照片；同时还能录音，截取手机屏幕，开启摄像头，话筒等功能，由此可见监控信息的详细程度令人害怕。

![enter image description here](http://drops.javaweb.org/uploads/images/30c33d044f091a0f3999d2bfd9a57906f359e2fe.jpg)

0x01 WP8监控源码分析
==============

* * *

`core-winphone-master\MornellaWp8\MornellaWp8`下是其主要核心代码,主要文件如下:

![enter image description here](http://drops.javaweb.org/uploads/images/a8fce047a2bc00193497791a5040f7fd92ee11c4.jpg)

通过观察源码流程图可以看出,整个监控项目源码的逻辑还是比较复杂的,但是深入之后,发现其还是设计的比较巧妙

![enter image description here](http://drops.javaweb.org/uploads/images/cb14cbe176a6895c40468983d11f5ee2de9f5c84.jpg)

0x01-1 程序框架分析
-------------

1.项目主要分为3大块`Modules,Events,Actions`,主要的功能Modules核心监控代码在此处,Event等待监控事件的到来并调用对应的监控模块,Action主要负责一些行为的启动和停止

程序启动流程如下:

```
main->mornellaStart->BTC_Init->CoreProc->Core->Task

```

`setLoadLibraryExW`分支主要负责加载一些API函数的地址,做一些初始化工作

![enter image description here](http://drops.javaweb.org/uploads/images/90f7a6abad920888b364f934b382d2d9472a93eb.jpg)

最后Task创建了3大模块的管理对象`ModulesManager,EventsManager,ActionsManager`

并在`Task::TaskInit()`中启动了events

![enter image description here](http://drops.javaweb.org/uploads/images/f1eda7c860ad1564444940229f6fcf0bf44bdfdd.jpg)

0x01-2 Event模块分析
----------------

Event主要负责以下事件的监控,例如短信,日历日程安排,联系人,地址位置,电池状态,进程信息,计时器状态等信息

![enter image description here](http://drops.javaweb.org/uploads/images/45b0746ae6f4739a7fafc48f3d4cec26e6854f0a.jpg)

所有的event均以json格式发送,并调用`conf.cpp下`的`ParseEvent`进行解析,源码部分逻辑被注释上了,经过搜索发现被注释上的功能最后没有相关的实现代码.

![enter image description here](http://drops.javaweb.org/uploads/images/370cf4252017c97c4b99351f950c93e4f8a73340.jpg)

我们选择电池状态监控为例,在`OnBatteryLevel`函数中,首先通过`RefreshBatteryStatus`刷新了电池的状态,`deviceObj->GetBatteryStatus()`得到当前的电池状态,最后`me->triggerStart()`添加到`ActionManage`中的`Action`队列中

![enter image description here](http://drops.javaweb.org/uploads/images/7b21a5802285fc8054f81c8091fc3c552ee94081.jpg)

0x01-3 Action模块分析
-----------------

Action模块主要是3个类`ActionManage,Action,SubAction`其中`ActionManage`主要维护一个Action队列,Action是抽象的接口,而执行的实体主要是`SubAction`。

`SubAction`主要处理`synchronize,execute,uninstall,module,event,sms,log,destroy`等行为的执行

![enter image description here](http://drops.javaweb.org/uploads/images/6883258516821bef728b92b2dc0ca7f08fc0e882.jpg)

而在处理module时用了start类进行启动,Start首先初始化了一个`ModulesManager`对象,然后在调用conf对获取对应的module信息,并调用`ModulesManager->start()`启动对应的模块。

![enter image description here](http://drops.javaweb.org/uploads/images/a71f6c7f4b2d442b1c5ff78cf353ff66bbb19765.jpg)

0x01-4 Module模块分析
=================

Module模块同上面的模块结构保持一致，也是一个ModuleManage负责维护一个Modules队列。

进行外层调度，Module类是一个抽象的接口，负责统一调用接口,主要的模块接口如下.

这些模块,完成了获取设备信息(如:操作系统版本,设备ID,电量,应用程序列表,进程列表,可用磁盘空间,内存信息,处理器架构),联系人,一些社交帐号信息,同时还能开启摄像头,话筒,截取手机屏幕等功能

![enter image description here](http://drops.javaweb.org/uploads/images/67ac25a2125bb11e7b142e394eb9fd7ae54c7101.jpg)

1.获取的设备信息,代码主要在DeviceInfo.cpp中

![enter image description here](http://drops.javaweb.org/uploads/images/4bc8ee19b1663c07e36a8b2dd7cd100831f665fc.jpg)

2.获取联系人的以及社交网站的帐号密码,代码主要在PoomAddressBook.cpp中

![enter image description here](http://drops.javaweb.org/uploads/images/2a44b8e41a3cbf25ab60170afca265a7cd8d20d2.jpg)

3.日历日程安排,代码主要在PoomCalendar.cpp中

![enter image description here](http://drops.javaweb.org/uploads/images/6e29a39d9ecf32a9e06634f5a5a48c19591126ab.jpg)

4.截图功能(代码在SnapshotGrabber.cpp中,但是该部分代码已经被注释)

![enter image description here](http://drops.javaweb.org/uploads/images/c589b31ea024e2332bf1bb165408e875e8af1825.jpg)

5.开启摄像头(代码在NativePhotoCaptureInterface.cpp中)

![enter image description here](http://drops.javaweb.org/uploads/images/82895d35793409310a021e423ed96abbef10a15b.jpg)

其主要通过WP的PhotoCaptureDevice API接口来实现,当你在啪啪啪的时候,你的摄像头被开启,那是种什么样的感觉呢?

![enter image description here](http://drops.javaweb.org/uploads/images/53a4cfda04ce8989f482257f844365fdb6803fe1.jpg)

其他的一些监控行为就不一一叙述了,大多都可以通过调用WP的接口来实现。

0x02 感染途径
=========

* * *

Window在新推出的WP8上做了很多对非越狱用户的保护,只能安装应用商店中的软件,但是WP8可以通过一个链接访问应用商店中的某个APP,当被攻击者被欺骗的安装了该APP应用,该APP遍可以通过WP提权的漏洞来提升运行权限,即可执行高权限代码,带来的后果非常严重,所以我们要警惕一些钓鱼欺诈的应用。

而对于越狱用户,别人可以直接把应用捆绑在越狱工具,在越狱的过程中,即可捆绑安装他们的APP应用,如果这个应用是恶意的,那么后果可想而知,然而在越狱后的WP系统安全性也将大打折扣.所以我们最好不要轻易的越狱。

Hacking Team是拥有微软的企业证书的,而具有企业证书的公司可以将自己的应用提交到商店供人下载,不用授权即可安装,不论是否越狱都可以安装上去,然而从应用商店下载的程序,用户一般都会认为是安全的。

由于Window Phone用户较少,反馈的问题可能也比较少,相关的开发维护人员也相应的比较少,可能会存在一些不为人知的安全漏洞,可以突破Window Phone8的安全限制,将恶意程序安装上去,还可能存在某些已经安装的应用存在漏洞,利用这些具有漏洞应用结合提权漏洞,将恶意的应用安装到设备上。

0x03 小结
=======

* * *

通过Hacking Team泄漏的这些资料来看,Hacking Team团队还是具备非常专业的水平,但是强如Hacking Team的公司都被入侵了,你手机里面的那些私密照片还保险么?

建议:

```
1.不要随意安装不知名的应用
2.及时更新系统的安全补丁
3.社交帐号设置复杂的密码
4.给私密的照片加密
```