# Android应用方法隐藏及反调试技术浅析

0x00 前言
=======

* * *

Android应用的加固和对抗不断升级，单纯的静态加固效果已无法满足需求，所以出现了隐藏方法加固，运行时动态恢复和反调试等方法来对抗，本文通过实例来分析有哪些对抗和反调试手段。

0x01 对抗反编译
==========

* * *

首先使用apktool进行反编译，发现该应用使用的加固方式会让apktool卡死，通过调试apktool源码（如何调试apktool可参见前文《Android应用资源文件格式解析与保护对抗研究》），发现解析时抛出异常，如下图：

![](http://drops.javaweb.org/uploads/images/534e1f1f807d0d15e8b4dbe4e08f602b2841dc4b.jpg)

根据异常信息可知是readSmallUint出错，调用者是getDebugInfo，查看源码如下：

![](http://drops.javaweb.org/uploads/images/6d5a8c82528d9cdadfd044bd432a7c7222f95a41.jpg)

可见其在计算该偏移处的uleb值时得到的结果小于0，从而抛出异常。 在前文《Android程序的反编译对抗研究》中介绍了DEX的文件格式，其中提到与DebugInfo相关的字段为DexCode结构的debugInfoOff字段。猜测应该是在此处做了手脚，在010editor中打开dex文件，运行模板DEXTemplate.bt，找到debugInfoOff字段。果然，该值被设置为了0xFEEEEEEE。

![](http://drops.javaweb.org/uploads/images/f21d56fb73794ca0795d79f33256d59e85aed164.jpg)

接下来修复就比较简单了，由于debugInfoOff一般情况下是无关紧要的字段，所以只要关闭异常就行了。

为了保险起见，在readSmallUint方法后面添加一个新方法readSmallUint_DebugInfo，复制readSmallUint的代码,if语句内result赋值为0并注释掉抛异常代码。

![](http://drops.javaweb.org/uploads/images/e773cc6ef5951d4cf65ea95007ed0fec2d6e4c1a.jpg)

然后在getDebugInfo中调用readSmallUint_DebugInfo即可。

![](http://drops.javaweb.org/uploads/images/d7c0996e59e52c3becea33db923f817f2808223f.jpg)

重新编译apktool，对apk进行反编译，一切正常。

然而以上只是开胃菜，虽然apktool可以正常反编译了，但查看反编译后的smali代码，发现所有的虚方法都是native方法，而且类的初始化方法中开头多了2行代码，如下图：

![](http://drops.javaweb.org/uploads/images/683a7c23fcf395c35894ff7297960e428c245d05.jpg)

其基本原理是在dex文件中隐藏虚方法，运行后在第一次加载类时通过在方法（如果没有方法，则会自动添加该方法）中调用ProxyApplication的init方法来恢复被隐藏的虚方法，其中字符串"aHcuaGVsbG93b3JsZC5NYWluQWN0aXZpdHk="是当前类名的base64编码。

ProxyApplication类只有2个方法，clinit和init，clinit主要是判断系统版本和架构，加载指定版本的so保护模块（X86或ARM）；而init方法也是native方法，调用时直接进入了so模块。

![](http://drops.javaweb.org/uploads/images/de6deabd4c98e4e92b1c5d8d3dbf4a107afff59a.jpg)

那么它是如何恢复被隐藏的方法的呢？这就要深入SO模块内部一探究竟了。

0x02 动态调试so模块
=============

如何使用IDA调试android的SO模块，网上有很多教程，这里简单说明一下。

1. 准备工作
-------

### 1.1准备好模拟器并安装目标APP。

### 1.2 将IDA\dbgsrv\目录下的android_server复制到模拟器里，并赋予可执行权限。

```
adb push d:\IDA\dbgsrv\android_server /data/data/sv
adb shell chmod 755 /data/data/sv

```

### 1.3 运行android_server，默认监听23946端口。

```
adb shell /data/data/sv

```

### 1.4 端口转发。

```
adb forward tcp:23946 tcp:23946

```

2 以调试模式启动APP，模拟器将出现等待调试器的对话框。
-----------------------------

```
adb shell am start -D -n hw.helloworld/hw.helloworld.MainActivity

```

![](http://drops.javaweb.org/uploads/images/739cef3f43e3ea11f705fbff4dfeeed746515cac.jpg)

3 启动IDA，打开debugger->attach->remote Armlinux/andoid debugger，设置hostname为localhost，port为23946，点击OK；然后选择要调试的APP并点击OK。
------------------------------------------------------------------------------------------------------------------

![](http://drops.javaweb.org/uploads/images/0fc17bfcaa147172cb12c9a2b001380292ede0aa.jpg)

这时，正常状态下会断下来：

![](http://drops.javaweb.org/uploads/images/a84a5a2c961d408514d32c148d1beceb46aa0d55.jpg)

然后设置在模块加载时中断：

![](http://drops.javaweb.org/uploads/images/3d56708faf3595dc59b2c162f69913db05f125b7.jpg)

点击OK，按F9运行。

然后打开DDMS并执行以下命令，模拟器就会自动断下来：

`jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700`

（如果出现如下无法附加到目标VM的错误，可尝试端口8600）

![](http://drops.javaweb.org/uploads/images/ed8cf48dbd1726076a0e8d888220be8a4d2ca044.jpg)

此时，可在IDA中正常下断点调试，这里我们断JNI_OnLoad和init函数。

![](http://drops.javaweb.org/uploads/images/60dc882cda1da81008335eba695aef972422e3d9.jpg)

![](http://drops.javaweb.org/uploads/images/88a463c060e61c5de7b42fd2cbc55aafd68559b3.jpg)

由于IDA调试器还不够完善，单步调试的时候经常报错，最好先做一个内存快照，然后分析关键点的函数调用，在关键点下断而不是单步调试。

0x03 反调试初探
==========

* * *

一般反调试在JNI_OnLoad中执行，也有的是在INIT_ARRAY段和INIT段中早于JNI_OnLoad执行。可通过readelf工具查看INIT_ARRAY段和INIT段的信息，定位到对应代码进行分析。

![](http://drops.javaweb.org/uploads/images/7b0f57e5d2ac64d30509102fd46835312279c2c3.jpg)

INIT_ARRAY如下：

![](http://drops.javaweb.org/uploads/images/da131924ec81deeb063c392e39f34f1f86d3b723.jpg)

其中函数sub_80407A88的代码如下，通过检测时间差来检测是否中间有被单步调试执行：

![](http://drops.javaweb.org/uploads/images/9b337b61ad4ea8741c5efb5f0c2d3357932ddbc0.jpg)

sub_8040903C函数里就是脱壳了，首先读取/proc/self/maps找到自身模块基址，然后解析ELF文件格式，从程序头部表中找到类型为PT_LOAD，p_offset!=0的程序头部表项，并从该程序段末尾读取自定义的数组，该数组保存了被加密的代码的偏移和大小，然后逐项解密。

![](http://drops.javaweb.org/uploads/images/c3b4c2594104203bd7e653e64c6f590312051216.jpg)

函数check_com_android_reverse里检测是否加载了com.android.reverse，检测到则直接退出。

![](http://drops.javaweb.org/uploads/images/7845175ec3d3a00389b634039d7c937f8e416877.jpg)

JNI_OnLoad函数中有几个关键的函数调用：

![](http://drops.javaweb.org/uploads/images/a5f7686d803e8f7cb37dc0bc30ba8192929afaf5.jpg)

call_system_property_get检测手机上的一些硬件信息，判断是否在调试器中。

![](http://drops.javaweb.org/uploads/images/de234943a50b731ec04b27627177d55f355f7d6e.jpg)

checkProcStatus函数检测进程的状态，打开/proc/$PID/status，读取第6行得到TracerPid，发现被跟踪调试则直接退出。

![](http://drops.javaweb.org/uploads/images/3eeba4157c5c5a69a73acf84c834198380c64767.jpg)

通过命令行查询进程信息，一共有3个同名进程，创建顺序为33->415->430->431。其中415和431处于调试状态：

![](http://drops.javaweb.org/uploads/images/c319745a03dfe0cf1175a8dd751c0aaaf38326e9.jpg)

进程415被进程405（即IDA的android_server）调试：

![](http://drops.javaweb.org/uploads/images/3678a7cbf912b29c5a809b42e799532674f37389.jpg)

进程431被其父进程430调试：

![](http://drops.javaweb.org/uploads/images/2a157996d4a2096b846570efa00e65d0fb11d416.jpg)

要过这种反调试可在调用点直接修改跳转指令，让代码在检测到被调试后继续正常的执行路径，或者干脆nop掉整个函数即可。 检测调试之后，就是调用ptrace附加自身，防止其他进程再一次附加，起到反调试作用。

![](http://drops.javaweb.org/uploads/images/e39a266d93998dfa2e37d8a63e2af5b67e707b5f.jpg)

修改跳转指令BNE（0xD1）为B(0xE0)，直接返回即可。

![](http://drops.javaweb.org/uploads/images/a3ee3ed88e590ae02a854dc8366624f7fa713f74.jpg)

当然，更加彻底的方法是修改android源码中bionic中的libc中的ptrace系统调用。检测到一个进程试图附加自身时直接返回0即可。

上面几处反调试点在检测到调试器后都直接调用exit()退出进程了，所以直接nop掉后按F9执行。然后就断在了init函数入口，顺利过掉反调试:

![](http://drops.javaweb.org/uploads/images/79fbfe0fe83b5342357434fb9e061d8405d42892.jpg)

init函数在每个类加载的时候被调用，用于恢复当前类的被隐藏方法.首次调用时解密dex文件末尾的附加数据，得到事先保存的所有类的方法属性，然后根据传入的类名查找该类的被隐藏方法，并恢复对应属性字段。 执行完init函数，当前类的方法已经恢复了。然后转到dex文件的内存地址

![](http://drops.javaweb.org/uploads/images/f760821817aae612dceb115797da71bc8c5d4b14.jpg)

dump出dex文件，保存为dump.dex。

![](http://drops.javaweb.org/uploads/images/c2484b094ce2f41f94609c5b302c291a9e22b95e.jpg)

0x04 恢复隐藏方法
===========

* * *

对比一下原始dex文件，发现dex文件末尾的附加数据被解密出来了：

![](http://drops.javaweb.org/uploads/images/b2c1cbd86281e9e250b78362a27d1d61a22cf6be.jpg)

仔细分析一下附加数据的数据结构可以发现，它是一个数组，保存了所有类的所有方法的method_idx、access_flags、code_off、debug_info_off属性，解密后的这些属性都是uint类型的,如下图：

![](http://drops.javaweb.org/uploads/images/06262bba5e9eab38669a0e11b2daf107d0839fcb.jpg)

其中黄色框里的就是MainActivity的各方法的属性，知道这些就可以修复dex文件，恢复出被隐藏的方法了。下图就是恢复后的MainActivity类：

![](http://drops.javaweb.org/uploads/images/8cd8a5443d113e18bf8b30deaaba42e7fe965cf6.jpg)

0x05 总结
=======

* * *

以上就是通过实例分析展示出来的对抗和反调试手段。so模块中的反调试手段比较初级，可以非常简单的手工patch内存指令过掉，而隐藏方法的这种手段对art模式不兼容，不推荐使用这种方法加固应用。总的来说还是过于简单。预计未来通过虚拟机来加固应用将是一大发展方向。