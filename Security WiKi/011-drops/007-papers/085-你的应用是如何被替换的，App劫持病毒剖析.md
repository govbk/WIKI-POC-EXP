# 你的应用是如何被替换的，App劫持病毒剖析

**Author：逆巴@阿里移动安全**

0x00 App劫持病毒介绍
==============

* * *

App劫持是指执行流程被重定向，又可分为Activity劫持、安装劫持、流量劫持、函数执行劫持等。本文将对近期利用Acticity劫持和安装劫持的病毒进行分析。

0x01 Activity劫持病毒分析
===================

* * *

### 1.1 Activity劫持病毒介绍

Activity劫持是指当启动某个窗口组件时，被恶意应用探知，若该窗口界面是恶意程序预设的攻击对象，恶意应用将启动自己仿冒的界面覆盖原界面，用户在毫无察觉的情况下输入登录信息，恶意程序在把获取的数据返回给服务端。

![p1](http://drops.javaweb.org/uploads/images/22c4db7e4eac4ea846021aa51d4356c9b182a377.jpg)

![p2](http://drops.javaweb.org/uploads/images/2f1eba46af2366d20b1a28716d3c8b4e15eac16d.jpg)

以MazarBOT间谍木马为例，该类木马有一下几个特点：

*   伪装成系统短信应用，启动后请求激活设备管理权限，随后隐藏图标；
*   利用Tor与C&C控制中心进行匿名通信，抵御流量分析；
*   C&C控制中心下发指令进行手机控制、update html、以及信息收集；
*   通过服务器动态获取htmlData，然后实施界面劫持，获取用户账号信息；

以下是C&C控制中心指令列表：

![p3](http://drops.javaweb.org/uploads/images/181dfbb74040e1a003336900e2efa502cbd91b3d.jpg)

我们发现该木马能接受并处理一套完整的C&C控制指令，并且使用Tor进行匿名网络通信，使得流量数据的来源和目的地不是一条路径直接相连，增加对攻击者身份反溯的难度。结下来我们将详细分析该木马界面劫持过程。

### 1.2 界面劫持过程分析

入口梳理首先看到axml文件。WorkerService服务处理C&C控制中心下发的”update html”指令，同时后台监控顶层运行的Activity，若是待劫持的应用将会启动InjDialog Acticity进行页面劫持。

![p4](http://drops.javaweb.org/uploads/images/007c9f1bea55a0a54ddc865a3a3f58c077e092a1.jpg)图 axml信息

下图是后台服务对顶层Acticity监控过程，若是待劫持应用则启动InjDialog进行劫持。getTop函数做了代码兼容性处理，5.0以上的设备木马也可以获取顶层Acticity的包名。

![p5](http://drops.javaweb.org/uploads/images/6d4c65db20391cbc6cb9a68ef787c8a96e0cde50.jpg)图 后台监控

InjDialog Activity通过webView加载伪造的html应用界面,调用webView.setWebChromeClient(new HookChromeClient())设置html页面与Java交互，在伪造的Html页面里调用prompt把JS中的用户输入信息传递到Java，HookChromeClient类重写onJsPrompt方法，处理用户输入信息，最后将劫持的用户信息通过Tor匿名上传到指定域名。

![p6](http://drops.javaweb.org/uploads/images/2cc7cab8378da4a11c3c8141ea0a4ed1b45cbd30.jpg)图 劫持用户信息

![p7](http://drops.javaweb.org/uploads/images/dace5f3f2c89bb0e594f9cffc266e70c02fea618.jpg)图 上传劫持信息

0x02 应用安装劫持病毒分析
===============

* * *

### 2.1安装劫持病毒介绍

安装劫持病毒通过监听android.intent.action.PACKAGE_ADDED和android.intent.action.PACKAGE_REPLACED intent实施攻击，包括两种手段，一种是卸载删除掉真正安装的apk，替换为攻击者伪造的应用；另外一种是借用用户正在安装的这个消息，悄悄的安装自己推广的其他应用。这个过程就像你平时喝的“六个核桃”，某天你居然喝到“七个核桃”。

### 2.2应用相关信息

该应用是一款名为”FlashLight”的应用，程序包名：com.gouq.light,应用图标如下：

![p8](http://drops.javaweb.org/uploads/images/5f891872b35daa31a5a3f0376cd87e6319100df1.jpg)

### 2.3主要组件分析

*   `.App`:应用Application类，加载Assest目录下加密jar包，获取接口ExchangeImpl对象，在jar里实现接口函数onApplicationCreate、triggerReceiver、triggerTimerService；启动核心服务LightService；
*   `.LightService`:应用核心服务，可外部调用启动LightTiService，达到替换进程名，以及am启动服务以自身保活；
*   `.LightTiService`:由LightService启动，该服务会调用动态加载包里的triggerTimerService接口方法，完成对以安装应用的删除、当前设备信息上传、从服务器下载待安装应用；
*   `.AppReceiver`:广播接收器，通过加载的jar包里triggerReceiver接口方法实现，处理android.intent.action.PACKAGE_ADDED和android.intent.action.PACKAGE_REPLACED intent查看安装跟新应用是否是劫持应用，若是通过execCmd进行安装劫持。

下图安装劫持过程，通过监听应用的安装和更新，实施关联的其他应用的静默安装。

![p9](http://drops.javaweb.org/uploads/images/e4bb00e179ca5de7331841e051dbd0542501a707.jpg)图 安装劫持

上图可以知道此恶意应用借用安装或更新intent，安装预设的关联应用，这样在安装完毕后用户并不清楚哪个是刚真正安装的应用，这样增加了推广应用点击运行的几率。

0x03 怎么有效防治App劫持或安全防护建议
=======================

* * *

针对企业用户：

作为一名移动应用开发者，要防御APP被界面劫持，最简单的方法是在登录窗口等关键Activity的onPause方法中检测最前端Activity应用是不是自身或者是系统应用。

当然，术业有专攻，专业的事情交给专业的人来做。阿里聚安全旗下产品安全组件SDK具有安全签名、安全加密、安全存储、模拟器检测、反调试、反注入、反Activity劫持等功能。 开发者只需要简单集成安全组件SDK就可以有效解决上述登录窗口被木马病毒劫持的问题，从而帮助用户和企业减少损失。

针对个人用户：

安装阿里钱盾保护应用免受App劫持木马威胁。

更多技术文章，请点击[阿里聚安全博客](http://jaq.alibaba.com/community/index)