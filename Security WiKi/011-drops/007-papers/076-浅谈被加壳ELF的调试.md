# 浅谈被加壳ELF的调试

0x00 ELF格式简介：
=============

* * *

注：本文只讨论如何调试被加壳的ELF文件，包括调试中的技巧运用及调试过程中可能遇到的问题的解决方法，不包含如何还原加固的DEX

本文将以某加壳程序和某加固为目标

ELF全称：Executable and Linkable Format，是Linux下的一种可执行文件格式。 此种文件格式和WINDOWS一样，常见分为两种类型：

1.  可执行文件(Executable File)，对应PE子类型：EXE
    
2.  共享目标文件(Shared Object File)，后缀名：.so，对应PE子类型：DLL
    

0x01 ELF文件加载大概流程：
=================

* * *

1.  通过Section Header或者Program Header加载需要的镜像数据 和WINDOWS PE加载机制不同，ELF有些文件数据是不会加载到内存镜像中
2.  加载SO NEED LIB和SYM 类似PE的Import_table
3.  执行重定位(如果有) 类似PE的Reloc_table
4.  执行INIT_ARRAY段或者INIT段（如果有，数组中的地址不等于0xffffffff，0表示结束）
    
    类似PE的TLS，已知的被加壳的ELF，壳代码都出现在这两个段里 PE中的TLS也常常出现在壳中，例如Vmprotect, Execryptor等
    
5.  执行入口点代码（如果有）
    

所有的上述加载流程代码全部包含在linker.so里，可参看安卓源码或逆向linker.so

0x03 ARM CPU简介： 1.指令集简介：
========================

* * *

ARMCPU采用RISC（精简指令集）架构（X86是CISC，复杂指令集），指令等长，相对CISC架构更加省电，执行效率更高

**_2. ARM指令集三种类型：_**

ARM(4字节等长)，THUMB(2字节等长)，THUMB2(4字节等长)。这三种指令集可以在同一执行程序中切换，切换原则为：

ARM <-->THUMB，THUMB<-->ARM（PC的最高位确定指令集类型：1为THUMB；0为ARM）

THUMB<-->THUMB2（由27-31位决定）

thumb2其实就是thumb的扩展，其目的是为了一条4字节指令完成多条2字节指令

***|3.寄存器: ***|

通用寄存器：r0-r15

特殊寄存器：r13 = SP（栈地址）, r14 = LR（函数返回地址）, r15 = PC（当前指令流地址）

还包括CPSR，APSR，浮点等寄存器，具体可参照ARM指令集手册

0x04 加壳SO的调试
============

* * *

**_1.ELF代码执行顺序_**

上面介绍了，加壳的SO的壳代码都在INIT_ARRAY段和INIT段

那我们先看下一个被加壳以后的SO，在linux下面用readelf -a命令查看ELF信息

![enter image description here](http://drops.javaweb.org/uploads/images/ca3f5bcff32e75df9896f4b158e063e31c83ff63.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/5485ba63dfb9d49e8cf7cf7e3d3d448c2f1b2189.jpg)

在ELF-HEADER里我们看到有Entry，地址为0x22a8

在动态段里看到了INIT_ARRAY数组，数组地址为0x21000，大小是12 BYTES

用IDA看看数组的内容

![enter image description here](http://drops.javaweb.org/uploads/images/e96aad9a8a0303ffb29f2c9b691417a2959f5aca.jpg)

上面说了，-1为无效，0代表结束，那INIT有效地址仅是0x2418这个地址

也就是说，这个SO加载起来以后，会先从0x2418这个地址开始执行，执行完成后再去执行Entry

我们再来看下某加固的ELF信息

![enter image description here](http://drops.javaweb.org/uploads/images/93ee883c923ca46d7e507bf46bbb1df8e69ac589.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/6828f09c788451d73f169ff3a97e73700fe1d71a.jpg)

在ELF-HEADER里我们看到有Entry，地址为0x3860

![enter image description here](http://drops.javaweb.org/uploads/images/b80f017bb017d9877bd19bf86c4d32def25f3d44.jpg)

DA打开某加固的文件时，会提示错误，不能打开，后面在Anti Anti Debugger中会讲到为什么

在动态段里看到了INIT_ARRAY数组，数组地址为0x28CA4，大小是8 BYTES

我们还看到了INIT段，地址是0x11401

我们在这里，总结下执行的顺序：

根据linker的代码，当INIT段和INIT_ARRAY段都存在的情况下，先运行INIT段，再运行INIT_ARRAY段，否则单独运行对应指向的函数，最后执行ENTRY

![enter image description here](http://drops.javaweb.org/uploads/images/45ce196fdd531c2834e46ac7ad2e2687d9a51137.jpg)

**_2. 自己准备SO_LOADER_**

调试SO和PE_DLL其实道理是一样的，都需要一个宿主进程，这里要写一个SO_LOADER，参看代码如下，可通过NDK编译。（代码是王晨同学早期提供的）

![enter image description here](http://drops.javaweb.org/uploads/images/b8a78914befc33c0c1d229d2866ebab5b1661d98.jpg)

**_3.环境准备：_**

我这里选用IDA6.6做为调试器。

第一步：拷贝调试器到安卓手机上

![enter image description here](http://drops.javaweb.org/uploads/images/7581a9ab333c0fe82e657c50e03a600af331ff70.jpg)

命令：adb push android_server /data/local/tmp/and

这里为什么把android_server 改名成and呢~~~，其实就是为了避免被检测出调试器，后面我在Anti Anti Debugger中会详细说一下关于这部分的内容

第二步：启动调试器

adb shell回车，进入/data/local/tmp/目录，启动调试器，启动后画面

![enter image description here](http://drops.javaweb.org/uploads/images/d0ed77a8e36eaf00f4e3a5e383363e78eb927c65.jpg)

第三步：重定向调试端口

adb forward tcp:23946 tcp:23946

至此手机端设置完毕，下面来看看IDA里如何设置

IDA加载我们自己写的so_loader，在854C处，按F2下断点

![enter image description here](http://drops.javaweb.org/uploads/images/74cb9e324c2b0876d8e8e600a52608fe5255f12f.jpg)

选择菜单栏里面的Debuger-Select Debugger，选择Remote Arm linux/Andoid debugger

![enter image description here](http://drops.javaweb.org/uploads/images/e927eb275a82ee4961dcff65a64fa6d596942beb.jpg)

点击OK，然后F9运行

![enter image description here](http://drops.javaweb.org/uploads/images/4be128fa707af8a42b89ed06ce6152d0b03ad46b.jpg)

在配置里面，Hostname里面填入127.0.0.1，点击OK

如果你的手机里面没有这个文件，会提示你COPY，点击确定即可，如果有这个文件，会出现下面的选择，一般选择USE FOUND就可以了，如果你要调试的程序有修改，选择COPY NEW覆盖一个新的进去

![enter image description here](http://drops.javaweb.org/uploads/images/dd06936440c17b444bc3a8edeaef5ec97e6883f5.jpg)

然后一路OK，就出现调试状态了~~，当前PC就是刚才我们F2设置的断点

![enter image description here](http://drops.javaweb.org/uploads/images/4ab0c975e4bda9035f3788ee529fc14514c8ecc8.jpg)

**_4.如何断住SO的INIT_ARRAY段和INIT段_**

上面说了，SO的加载在linker.so里完成，我们要做的，就是把断点设置在linker.so里面

先找代码，IDA打开linker.so，在string窗口里找

call_constructors_recursive,双击并查看引用

![enter image description here](http://drops.javaweb.org/uploads/images/4b8d3db54e811b2e1d0630c0a6b0e23baf8c51aa.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/5e57f68ffaaa5a0d46219a5519d50ab5f1729922.jpg)

双击第二个引用处，然后往上找blx r3(init段的调用)，b.w xxxxxxxx(init_array段的调用)

![enter image description here](http://drops.javaweb.org/uploads/images/12bd32128900e16592ad1d3b0067c87a3d7001b1.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/df9eebc29cbdb6dd7555756261a7905b0ec6c6ac.jpg)

好了，现在我们找到了地址0x54d0, 0x3af0这两个地方，回到刚才调试的IDA里面，

选择菜单栏debugger-Debugger windows-module list打开进程模块列表

![enter image description here](http://drops.javaweb.org/uploads/images/1f04b16d71040094e4fb88fa23e420bbbfabf7f5.jpg)

linker.so的base是40002000,分别对应的两个地址就是

```
0x40002000+0x54d0 = 0x400074d0
0x40002000+0x3af0 = 0x40005af0

```

我们在IDA View-PC窗口GO 过去

![enter image description here](http://drops.javaweb.org/uploads/images/d5f707bb4ebbba603c4932b68554aa3f03f2b57c.jpg)

在0x74d0处，按C键，变成代码.奇怪，为什么没有反应！！而且在最下面的output window有如下提示

![enter image description here](http://drops.javaweb.org/uploads/images/8f711a488bc8ef4a8dd1854b879e3b2ba6db7548.jpg)

这里就是我说的很重要的问题了，上面我提到了，被调试的程序可以在3种指令集之间切换，这时的IDA并不知道当前要变成代码的地址是ARM还是THUMB，这时我们需要对照静态的来看，或者你对指令集绝对的熟悉，看到BYTE CODE就知道是哪种指令集

![enter image description here](http://drops.javaweb.org/uploads/images/0033f4d8730dc18cd891c9621512b524a659206a.jpg)

静态中，显然IDA给的是2字节指令，那必然是THUMB，我们需要把当前地址改成THUMB

方法：按键盘的ALT+G，呼唤出窗口

![enter image description here](http://drops.javaweb.org/uploads/images/66adbe7d422563766d84ec639be5644ff17b3875.jpg)

T,DS不用管，我们只需要把VALUE改成1就是THUMB指令集了，变成1点击OK以后

在原来的地址上出现了CODE16，这时我们再去C一次

![enter image description here](http://drops.javaweb.org/uploads/images/043b5624844d19df109929158775d84eced21643.jpg)

C完以后，就出现代码了！！！ARM和THUMB就是这么切换的，切记，切记

![enter image description here](http://drops.javaweb.org/uploads/images/04861a34d59eb7497e885154ba3c29220d927c2c.jpg)

再看另外一个地址,0x400a5af0,按照同样的方法再来一次

![enter image description here](http://drops.javaweb.org/uploads/images/1cb051e6956d5eb65a120176a400df689067400d.jpg)

问题又来了，奇怪了，为什么下面不是指令？！这个是IDA的BUG，6.6版本对THUMB2指令在调试状态的解析就是有问题。。。。，不过没关系，我们往下看

![enter image description here](http://drops.javaweb.org/uploads/images/acacb939881a91a000f63f4f8da5dd7bbaea86a4.jpg)

这段代码才是最重要的，执行每一个init_array中地址的函数，就在blx r2这句。 至此，如何断住INIT段和INIT_ARRAY段，就讲完了，剩下的大家就自己调试吧

0x05 Anti Anti Debugger
=======================

* * *

**_1.Anti IDA_**

其实这种问题，是IDA解析ELF和linker解析ELF不一致造成的，IDA更加严格

用ida打开某加固的so,提示

![enter image description here](http://drops.javaweb.org/uploads/images/7f568f27cae248d4ac0dee6a4dcdd3bf8b183a80.jpg)

这个提示就是说，有个数据描述是无效的，我们来看看，是哪个。

SHT说的就是Section Table，来看看ELF头部数据如下

![enter image description here](http://drops.javaweb.org/uploads/images/b5998d513a2482e7fafb2451b92762f7611a0d6b.jpg)

shoff就是这个值，我们用16进制编辑器过去看看

![enter image description here](http://drops.javaweb.org/uploads/images/03fd1532aef7b669d1d13fdb8ba5737c68baf222.jpg)

全是0，显然这里有问题，我们首先要把这个值清0，保存文件。

再次加载，还有问题，提示如下：

![enter image description here](http://drops.javaweb.org/uploads/images/e996f870cba553027c9447b4f1821f12a341e018.jpg)

这次通过调试IDA的ELF插件，发现当PROGRAM HEADER中的物理偏移大于文件大小时，就会出现该错误。

![enter image description here](http://drops.javaweb.org/uploads/images/1ac1ccbd75f3f67c79625dbe1252b8d68b267263.jpg)

显然，Program Header中的第一组数据，p_offset超过了文件大小，根据ELF结构，定位到该数据偏移，改成0，IDA加载成功

**_2.Anti Debugger_**

通过调试该加壳程序，总结他用到的方法：

方法1：检测父进程的文件名

调用getppid，获取父进程的id, open("/proc/ppid/cmdline")获取父进程名称，检测常用调试器的名字，这就是上面我COPY文件时，为啥要把android_server变成随意一个文件名的原因了

对策：修改getppid的返回值，随便给一个可以用的就行了

其实还有其他方法可以获取ppid，比如open("/proc/pid/status")，read这个handle的内容，在里面寻找ppid也行

方法2：异常陷阱

和WINDOWS的方法类似，设置一个trap，检测调试器

对策：IDA默认所有的trap都交给调试器处理，所以我们需要修改对应的设置。菜单选择debugger-debugger options,点击edit exceptions按钮

![enter image description here](http://drops.javaweb.org/uploads/images/46ca5bfc61c8080608e4f9b74ed88545837c09a7.jpg)

在trap上，右键编辑改成如下即可

![enter image description here](http://drops.javaweb.org/uploads/images/d4a1bfb05f5ac727b97d7e48a81870c019ccd021.jpg)

当然，检测调试器，还有很多方法，见招拆招就可以，这里就不详述了