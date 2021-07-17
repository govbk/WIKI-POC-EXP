# iOS冰与火之歌番外篇 - 在非越狱手机上进行App Hook

0x00 序
======

* * *

冰指的是用户态，火指的是内核态。如何突破像冰箱一样的用户态沙盒最终到达并控制如火焰一般燃烧的内核就是《iOS冰与火之歌》这一系列文章将要讲述的内容。但在讲主线剧情前，我们今天先聊一聊分支剧情 - 在非越狱的iOS上进行App Hook。利用这个技术，你可以在非越狱的iOS系统上实现各种hook功能（e.g., 微信自动抢红包，自动聊天机器人，游戏外挂等），但写这篇文章的目的并不是鼓励大家使用外挂，更不是鼓励大家去卖外挂，所以千万不要用这个技术去做一些违法的事情。

《iOS冰与火之歌》系列的目录如下：

1.  Objective-C Pwn and iOS arm64 ROP
2.  在非越狱的iOS上进行App Hook（番外篇）
3.  █████████████
4.  █████████████
5.  █████████████

另外文中涉及代码可在我的github下载:  
[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x01 Mach-O LC_LOAD_DYLIB Hook
==============================

* * *

要是看过我写的安卓动态调试七种武器之离别钩 – Hooking（上）[http://drops.wooyun.org/tips/9300](http://drops.wooyun.org/tips/9300)和 安卓动态调试七种武器之离别钩 – Hooking（下）[http://drops.wooyun.org/papers/10156](http://drops.wooyun.org/papers/10156)的同学应该知道在android进行hook的方法可以是五花八本的。其实在iOS上进行hook的方式也有很多，但是大多数都需要越狱后才能实现（比如大家最常用的Cydia Substrate），今天我就来介绍一种不需要越狱就能hook iOS app方法，也就是`Mach-O LC_LOAD_DYLIB Hook`。这种方法是通过修改binary本身来加载第三方dylib并实现hook，具体思路是：

提取ipa中的二进制文件 -> 修改二进制文件的Load Commands列表，加入要hook的dylib –> hook.dylib在函数constructor函数中完成对特定函数的hook->对修改后的ipa进行签名，打包和安装。

首先我们先来看一下我们将要进行注入的目标app，这个app非常简单，就是调用上一章讲过的talker这个类输出一句”Hello, iOS!”。

![p1](http://drops.javaweb.org/uploads/images/8f3d1fc47590386109f07b4f4a8e3872005825b6.jpg)

在Products文件夹中我们能够看到IceAndFire.app这个文件，也就是编译完后的app：

![p2](http://drops.javaweb.org/uploads/images/82dd09693288b233a4df703be885cd0382ae0364.jpg)

IceAndFire.app其实就是个文件夹，里面可以看到很多的资源文件（签名信息，图片等），但最重要的东西就是与文件夹同名的IceAndFire这个二进制文件了。我们可以用xxd命令来看一下里面的内容：

![p3](http://drops.javaweb.org/uploads/images/41309a3773cf9f353f621f2dec813a9df499a680.jpg)

这个二进制文件里保存了IceAndFire这个app的所有逻辑，但是直接看二进制编码太辛苦了，这里我推荐一个叫做MachOView的软件（可以在我的github里下载），通过这个软件就可以看到整个MachO文件的结构了：

![p4](http://drops.javaweb.org/uploads/images/88c9369c55a76172218120c17b607af8aaa57625.jpg)

在Load Commands这个数据段里，我们可以看到IceAndFire这个二进制文件会在启动的时候自动加载Foundation, libobjc.A.dylib等动态库。如果我们对MachO这个文件的Load Commands结构体进行修改，是不是就可以让IceAndFire这个app在启动的时候加载我们自定义的用来hook的dylib呢？没错，这个想法是可行的。并且我们只要在dylib的构造函数里完成相应的hook逻辑，就可以在app启动的时候对指定函数进行hook操作了。

那么如何修改MachO的结构体呢？用010 editor等二进制编辑器的确是一种方法，但实在是麻烦了点。好消息是金正日小分队已经把自动注入dylib的工具帮我们写好了。这个叫yololib的工具可以帮我们直接进行dylib的注入：[https://github.com/KJCracks/yololib](https://github.com/KJCracks/yololib)。但作者只放出了源码没有放出binary，我帮大家编译了一份扔到了我的github上([https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE))。

编译好yololib后，我们只需要在mac上执行:

```
./yololib [binary] [dylib file]
./yololib [被插入dylib的二进制文件] [要插入的dylib]

```

命令即可完成dylib的注入，如图所示：

![p5](http://drops.javaweb.org/uploads/images/cbae292078f69ae92e5232c950ebfa079b41016d.jpg)

现在我们再用MachOView看一下IceAndFire这个二进制文件就会看到hook1.dylib已经被我们成功注入进去了：

![p6](http://drops.javaweb.org/uploads/images/e59cf7d6390c377b9a3368f41ad94fdbab227efc.jpg)

“`@executable_path/hook1.dylib`”的意思是二进制文件会在当前目录下对hook1.dylib进行加载，所以我们编译好的hook1.dylib要和二进制文件一起放到IceAndFire.app文件夹里，这样才能保证我们在运行app的时候hook1.dylib能够被正确的加载。

0x02 CaptainHook for Dylib
==========================

* * *

修改好了app二进制文件的Load Commands结构体后，我们再来看看如何构造进行hook的第三方dylib。因为app自己肯定不会主动调用第三方dylib中的函数，所以如果我们想要让第三方dylib进行hook操作就要把hook的逻辑写到构造函数里。实现构造函数很简单，只要在函数前声明 ”`__attribute__((constructor)) static`” 即可，我们先写个”Hello, Ice and Fire!”测试一下：

![p7](http://drops.javaweb.org/uploads/images/d2e8e9abb3f8f56bf1b3780d44e0fd8683e03940.jpg)

编译好dylib文件后，我们将这个dylib文件与app一起签名、打包、安装。然后我们运行一下程序就可以看到我们注入的dylib库已经在程序启动的时候成功加载并执行了。

![p8](http://drops.javaweb.org/uploads/images/ca671a13d048c2d37765cd4ead92fa7d6629fbc5.jpg)

下一步就是要实现对特定函数的hook。在这里我推荐使用CaptainHook这个framework。作者已经帮我们实现了hook所需要的各种宏，只要按照如下步骤就可以完成针对特定函数的hook：

1.  使用 CHDeclareClass() 声明想要hook的class
2.  在构造函数中用 CHLoadClass() 或 CHLoadLateClass() 加载声明过的class
3.  使用CHMethod() hook相应的method
4.  在CHMethod()中可以使用CHSuper()来调用原函数
5.  在构造函数中使用CHClassHook()来注册将要hook的method

比如我们想要hook Talker这个class里的say method，让app在调用say的时候修改method的参数，让say的话都变成”Hello, Android!”，我们只需要这样编写dylib的源码：

```
#import <CaptainHook/CaptainHook.h>

CHDeclareClass(Talker);

CHMethod(1, void, Talker, say, id, arg1)
{
    NSString* tmp=@"Hello, Android!";
    CHSuper(1, Talker, say, tmp);
}

__attribute__((constructor)) static void entry()
{
    NSLog(@"Hello, Ice And Fire!");
    CHLoadLateClass(Talker);
    CHClassHook(1, Talker,say);
}

```

CHMethod()这个宏的格式是：参数的个数，返回值的类型，类的名称，selector的名称，selector的类型，selector对应的参数的变量名。

CHClassHook()这个宏的格式是：参数的个数，返回值的类型，类的名称，selector的名称。

编写完代码后，我们对源码进行编译，将生成的dylib文件与app一起签名、打包、安装。然后我们运行一下程序就可以看到我们注入的dylib库已经成功的hook了say method了，原本应该输出”Hello, iOS!”，已经被我们成功的变成了”Hello, Android!”：

![p9](http://drops.javaweb.org/uploads/images/730738fa08a14dce8205552216cc564dbdea2d0a.jpg)

0x03 签名、打包和安装
=============

* * *

我们知道越狱后的iPhone有一个很重要的特性就是可以关闭app的签名校验，关掉签名校验后，App Store上的app（无论是收费的还是免费的）就可以随意盗版并且免费安装了。但是在非越狱的iPhone上，系统要求app必须要有合法的签名，负责无法进行安装。其实除了AppStore上的app有合法的签名外，我们还可以使用开发者证书或者企业证书来让没有合法签名的app拥有合法的签名。

当我们拥有开发者帐号并且在机器上安装了证书的话，就可以在Keychain Access这个工具中看到我们的签名信息：

![p10](http://drops.javaweb.org/uploads/images/68fa7d302b87b74d0629300ff22c85f38a72c345.jpg)

我们接下来要干的事情就是使用这个开发者证书来对我们修改后的IceAndFire .app进行签名。步骤如下：

1.  首先先保证IceAndFire.app文件夹下有正确的embedded.mobileprovision文件：
    
    如果没有的话，可以去苹果的开发者中心（developer.apple.com）生成。如果是个人开发者要注意将iOS设备的UDID加到开发者的设备列表中再生成embedded.mobileprovision文件，如果是企业证书则没有设备数量的限制。
    
2.  正确的编写签名时使用的Entitlements.plist：
    
    这里最需要注意的就是application-identifier要包含正确的Team ID (可以在开发者中心查看) 和对应的Bundle ID。
    
    ![p11](http://drops.javaweb.org/uploads/images/6edb5c3e7048bb4ac89a1f7705b9d8bf579beab9.jpg)
    
3.  使用codesign对hook的dylib进行签名：
    
    ```
    codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (XXXXXXXXX)" IceAndFire.app/hook1.dylib
    
    ```
4.  使用codesign对app进行签名：
    
    ```
    codesign -f -s "iPhone Developer: zhengmin1989@gmail.com (XXXXXXXXX)" --entitlements Entitlements.plist IceAndFire.app
    
    ```
5.  使用xcrun将IceAndFire.app打包成IceAndFire.ipa：
    
    ```
    xcrun -sdk iphoneos PackageApplication -v IceAndFire.app  -o ~/iOSPwn/hook/github/IceAndFire.ipa
    
    ```
6.  使用itunes或者mobiledevice进行安装。
    

![enter image description here](http://drops.javaweb.org/uploads/images/e65cc57fb482263cf61c6368524555907fc4dc3c.jpg)

成功的话会显示”OK”。然后就可以在非越狱的手机上使用我修改后的app了。

0x04 Class-dump 和 ida
=====================

* * *

通过上面几节的介绍，我们已经将非越狱app hook的流程走过一遍了，但这时候有人会问：”你hook的app是自己写的，你当然知道应该hook哪个函数了，我想hook的app都是App Store上的，并没有源码，我该怎么办？”其实这个问题也不难解决。只要用好class-dump和ida即可。

Class-dump是一款可以用来dump头文件工具：

![p13](http://drops.javaweb.org/uploads/images/523b60a75a2a71fac66790d3218c6779addfe16d.jpg)

比如我们想要dump XXX的头文件，只需要执行：

```
./class-dump -H -o header XXX

```

经过dump后，所有的头文件都会保存在”header”这个文件夹中：

![p14](http://drops.javaweb.org/uploads/images/be243d0beceae07ad5836a1a81a2703da0c01ca1.jpg)

每个头文件中都包含了类和方法的声明：

![p15](http://drops.javaweb.org/uploads/images/049753c7e030bb6371e8e029fa498eb291e0f85d.jpg)

可以看到，利用class-dump能够很好的帮助我们了解app的内部结构。但是class-dump只能获取app的头文件，并不能知道每个方法具体的逻辑，这时候我们就需要用到ida了。

利用ida我们可以获取到一个方法具体的逻辑，不过这需要你对arm汇编有一定的了解：

![p16](http://drops.javaweb.org/uploads/images/a12dc8b311dff472d838289c96dba7cbfb9ed795.jpg)

比如上图所示的函数就是调用`NSLog(@”%@\n”)`来向控制台输出参数的内容。只有了解了某个函数具体是做什么的，我们能才知道如何hook这个函数。

0x05 微信自动抢红包的原理
===============

* * *

至于微信自动抢红包的插件无非就是hook了接收微信消息的函数，然后判断消息中有没有红包，有的话就直接调用打开红包的函数即可。但因为这篇文章的主要目的是介绍非越狱手机的app hook，而不是鼓励大家使用外挂，所以具体实现的细节就不公布了，有兴趣的同学可以自己尝试写一个。虽然效果没有机械流那么酷炫，但的确省时省力啊。

![p17](http://drops.javaweb.org/uploads/images/2de1b21c7bd1f4b4a58794235c15c84977a314ca.jpg)

![p18](http://drops.javaweb.org/uploads/images/de958d582d66b17786f5111640d7f2b6cb0d986c.jpg)

0x06 总结
=======

* * *

通过这篇文章我们可以看到，即使是在非越狱的iOS系统上依然可以玩出很多的花样，因此各大it厂商不要盲目的相信非越狱iOS系统的安全性。针对红包和支付等比较重要的逻辑一定要有混淆和加固，针对app本身一定要有完整性校验。不然好心的白帽子可能只是写个自动抢红包的外挂玩玩，但是黑客就可能利用这种技术开发各种外挂来牟取暴利或者让用户在无意当中安装上带有后门的app，随后会发生什么就只有天知道了。

最后感谢我的同事黑雪和耀刺对这篇文章的帮助和指导。

PS: 文中涉及代码可在我的github下载:

[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)