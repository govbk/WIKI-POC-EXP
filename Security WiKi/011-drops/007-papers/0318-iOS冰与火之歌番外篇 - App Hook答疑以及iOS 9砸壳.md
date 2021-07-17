# iOS冰与火之歌番外篇 - App Hook答疑以及iOS 9砸壳

0x00 序
======

* * *

上一章我们讲到了在非越狱的iOS上进行App Hook。利用这个技术，你可以在非越狱的iOS系统上实现各种hook功能（e.g., 微信自动抢红包，自动聊天机器人，游戏外挂等）。但因为篇幅原因，有一些细节并没有讲的非常清楚。没想到阅读量非常大，很多人都来私信问我一些hook中遇到的问题，并且问的问题都很类似。于是我专门写了一篇答疑的文章来帮助大家解决一些常见的问题，顺便介绍一下如何在iOS 9上进行app 砸壳 (Dumpdecrypted)。另外想看主线剧情的读者也不要着急，下一篇就会给大家带来如何过沙盒的文章。

《iOS冰与火之歌》系列的目录如下：

1.  Objective-C Pwn and iOS arm64 ROP
2.  在非越狱的iOS上进行App Hook（番外篇）
3.  App Hook答疑以及iOS 9砸壳（番外篇）
4.  █████████████
5.  █████████████

另外文中涉及代码可在我的github下载:  
[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x01 如何编译hook.dylib
===================

* * *

很多人私信给我提到hook.dylib无法编译成功，这个问题大多是因为没有安装Command Line Tools和越狱开发环境iOSOpenDev造成的，这两个工具都是搞iOS安全必备的环境，可以按照以下步骤进行安装：

Command Line Tools 是Xcode的一个命令行工具插件，安装方法有两种：

**(1) 打开终端，输入：**

```
xcode-select --install

```

**(2) 去苹果官网下载安装包**

[https://developer.apple.com/downloads/](https://developer.apple.com/downloads/)

![p1](http://drops.javaweb.org/uploads/images/184737854a166b358daaf059afa9dae34041d413.jpg)

iOSOpenDev里提供了很多越狱开发的模板，可以在[http://iosopendev.com/download/](http://iosopendev.com/download/)下载到。安装完iOSOpenDev后就可以在Xcode里通过新建一个project看到我们进行非越狱Hook的时候需要用的CaptainHook了。

![p2](http://drops.javaweb.org/uploads/images/19b1c6723e9a603b6d9f644865ca22f58774f2e3.jpg)

0x02 如何得到App Store上解密后的ipa
==========================

* * *

我们开发时的app默认是没有加密的，但App Store上下载的app却被加了密。如果我们想要进行hook以及重打包的话，我们需要拿到解密后的app才行，否则的话，就算hook成功，签名成功，安装成功，app还是会闪退。

**(1) 查看app是否加密：**

首先用file来看一下ipa解压后的二进制文件包含哪些架构（e.g., armv7, arm64）。如果有多个架构的话，最好是把所有的架构都解密了。但理论上只要把最老的架构解密就可以了，因为新的cpu会兼容老的架构。比如我们拿微博作为例子，可以看到weibo的客户端包含了armv7和arm64这两个架构。

![p3](http://drops.javaweb.org/uploads/images/b5b47a3e62700f90a4f6a341d553d7ade3ae1f86.jpg)

随后我们可以通过”`otool –l`”来输出app的load commands，随后再查看cryptid这个标志位来判断app是否被加密了。如果是1的话代表加密了，如果是0的话代表解密了。

![p4](http://drops.javaweb.org/uploads/images/9b865d9604298ed17fe5c695108d2aab02d8a576.jpg)

从上图可以看到，weibo的armv7架构的代码被加密了，arm64架构却是解密的，原因是我已经通过dumpdecrypted对arm64架构的代码砸过壳了。如果没有解密的话，用ida打开app会看到加密的提示：

![p5](http://drops.javaweb.org/uploads/images/db1944c3d7b2bb849e6c5322b03370c001c7356d.jpg)

**(2) dumpdecrypted砸壳：**

如果需要解密的话，我们就需要用工具进行砸壳。最有名的砸壳工具就是dumpdecrypted了。他的原理是让app预先加载一个解密的dumpdecrypted.dylib，然后在程序运行后，将代码动态解密，最后在内存中dump出来整个程序。这个工具可以在:[https://github.com/stefanesser/dumpdecrypted](https://github.com/stefanesser/dumpdecrypted)下载到。但下载完的只是源码，我们还需要编译一下，这里我会放一份编译好后的dumpdecrypted.dylib到我的github上。

虽然hook可以在越狱的环境下实现，但是想要砸壳的话，必须具备越狱的环境，比如这篇文就使用的越狱后的iOS 9。用ssh连接上iOS设备后，我们打开想要砸壳的app。然后输入`ps ax`，就可以在进程中找到这个app的二进制文件的地址：

![p6](http://drops.javaweb.org/uploads/images/74741a928c081c05379eba677b4b19b68f0b858d.jpg)

因为每个app目录下都有一个Info.plist。我们可以通过这个Info.plist得到app的Bundle ID：

```
cat /var/mobile/Containers/Bundle/Application/19A9AE5E-22DC-449A-A530-C793D88ACB24/Weibo.app/Info.plist

```

![p7](http://drops.javaweb.org/uploads/images/2fb2495e71a8293426ce425dabb51c5fa1a49675.jpg)

比如Weibo的Bundle ID就是：com.sina.weibo。得到BundleID后我们下一步要知道app的data目录，原因是app的运行会受到沙盒的限制，因此dump出来的app只能保存在自己的data目录下，这里我们可以通过Bundle ID和一个private API得到data目录的位置：

![p8](http://drops.javaweb.org/uploads/images/86af6f75a4fdcc7d1e3899b1a466cf811947b730.jpg)

代码如下：

```
NSString* bundleID = [[NSString alloc] init];
bundleID = @"com.sina.weibo";
id dataID = [[NSClassFromString(@"LSApplicationProxy") applicationProxyForIdentifier:bundleID] dataContainerURL];
NSLog(@"%@",dataID);

```

得到data目录的地址后，我们将dumpdecrypted.dylib 拷贝到data的tmp目录下，然后在tmp目录下执行`DYLD_INSERT_LIBRARIES=dumpdecrypted.dylib /var/mobile/Containers/Bundle/Application/19A9AE5E-22DC-449A-A530-C793D88ACB24/Weibo.app/Weibo`进行砸壳。

![p9](http://drops.javaweb.org/uploads/images/a0bf413d1fdd4156735061a1c3e05b9dfc5b00c0.jpg)

然后在目录下就可以得到砸壳后的二进制文件了，要注意的是我们砸壳后的app只能解密砸壳运行时的架构，所以我建议找个armv7架构的iOS设备进行砸壳，然后执行：

```
lipo app -thin armv7 -output app_armv7

```

就可以把app的armv7架构抽取出来。这样的话，就可以保证app只在armv7的模式下运行了。

(3) 越狱市场下载：

当然，除了利用dumpdecrypted获取解密后的app还可以直接在PP助手的越狱市场上下载到，这些越狱应用都是解密后的app。但不能保证下载到AppStore上所有的app。

![p10](http://drops.javaweb.org/uploads/images/7189051866bafa7624166e8bdb0e85f848f075e2.jpg)

0x03 获取embedded.mobileprovision的技巧
==================================

* * *

有人会问如何获取embedded.mobileprovision这个文件，因为自己开发的app默认会有embedded.mobileprovision，但从AppStore上下载app并没有。其实，除了在developer center上通过录入device的UDID，然后下载embedded.mobileprovision之外，我们还可以利用xcode自动生成embedded.mobileprovision。比如我们想要重打包微博这个app，只要新建一个app（为了确保万无一失，可以把app的Bundle ID也起为com.sina.weibo），然后把手机连接上电脑，编译并在手机上运行这个app。然后只要去app的目录下拷贝embedded.mobileprovision就可以了。这样获取的embedded.mobileprovision可以保证能够适配重打包的app。如下图所示：

![p11](http://drops.javaweb.org/uploads/images/50cebb0b2c9b3dadf03775ae64e4114ac8d785b7.jpg)

0x04 签名的技巧
==========

* * *

签名的时候我们需要提供entitlement的信息，这个entitlement是什么呢？其实这个entitlement是用来做iOS权限管理的，通过声明不同的entitlement就能得到不同的权限。并且这个信息已经保存到了二进制文件里。比如我们可以通过”`ldid –e`”来查看一个二进制文件的entitlement。比如Weibo的entitlement为：

![p12](http://drops.javaweb.org/uploads/images/9f1541a393effd514d58052d7e7ef48678e545df.jpg)

理论上需要给app签上原app对应的所有entitlement才行。

另外，除了app本身需要签名以外，app的PlugIn，WatchNative App，WatchNative App的PlugIn如果有的话，都需要签名才行，拿WeChat举例，我们要对如下的内容都签名才可以：

```
codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (**********)" WeChat.app/Watch/WeChatWatchNative.app/PlugIns/WeChatWatchNativeExtension.appex
codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (**********)" WeChat.app/Watch/WeChatWatchNative.app
codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (**********)" WeChat.app/PlugIns/WeChatShareExtensionNew.appex
codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (**********)" WeChat.app/hook2.dylib
codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (**********)" --entitlements Entitlements.plist WeChat.app

```

0x05 安装大ipa的方法
==============

* * *

上一篇中介绍了一种利用libimobiledevice来安装ipa的方法。但我在尝试安装特别大的ipa的时候（大于50M），经常会失败，需要尝试多次才行。这里有个小技巧，如果有条件的话，可以使用windows下的itools来辅助我们安装，基本上一次就能搞定了。

![p13](http://drops.javaweb.org/uploads/images/6b9ef5974197b339773cdd64908dc8789675147b.jpg)

0x06 总结
=======

* * *

这篇文章基本上解决了app hook过程中遇到的常见问题，还介绍了iOS 9上砸壳的技术。如果还遇到问题的话，大家可以通过xcode里的log来分析原因，然后尝试解决问题。至此，iOS app的安全（番外篇）就告一段落了。下一章将会进入主线剧情，给大家带来app过沙盒的技术，敬请期待。