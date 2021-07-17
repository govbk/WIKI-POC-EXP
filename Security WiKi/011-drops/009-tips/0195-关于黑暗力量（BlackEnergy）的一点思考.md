# 关于黑暗力量（BlackEnergy）的一点思考

0x00 背景
=======

* * *

在乌克兰电力系统被攻击之后，最近又爆出该国机场也遭受网络袭击。罪魁祸首都是黑暗力量（BlackEnergy），BlackEnergy是何方神圣？为何有如此神通？BlackEnergy是最早出现在2007年的一套恶意软件，后来出现了专门针对乌克兰政府机构打造的分支。BlackEnergy并不是最近兴起的新型恶意软件，但时至今日仍然站在潮头兴风作浪，这点值得我们关注。

0x01 攻击简述
=========

* * *

下边简要描述一下BlackEnergy的攻击过程。XLS文档通过邮件可以方便传播，文档中包含的宏代码会dropper一个vba_macro.exe，这个exe又会dropper两个东西。其一.dat结尾的文件是一个dll，而启动目录下的快捷方式是使用rundll32来运行dll中序号为1的导出函数。

rundll32拉起恶意dll之后，会使用进程外com的方式的去启动IE进程，然后使用IE进程去连接远程服务器，下载恶意软件组件。然后又通过安装驱动和apc注入，在系统模块中执行恶意代码，与远程服务器通信，根据远程服务器的指令以及拉取下来的恶意程序执行相应攻击。

![p1](http://drops.javaweb.org/uploads/images/7a935d1a08a5346d1361c3f8d57b8438dbbac26e.jpg)

0x02 样本危害
=========

* * *

通过宏病毒入侵系统，留有后门，后续攻击组件清空关键系统文件，使得计算机无法正常工作，达到破坏目的。

0x03 重点分析
=========

* * *

### 1. FONTCACHE.DATA文件分析

FONTACACHE.DATA是由之前的`vba_macro.exe`来释放，FONTACACHE.DATA是一个dll文件，通过下面这条命令运行起来。`C:\WINDOWS\system32\rundll32.exe "C:\Documents and Settings\Administrator\Local Settings\Application Data\FONTCACHE.DAT",#1`可以看到调用dll导出的序号为1的函数。下图为导出函数表。

![p2](http://drops.javaweb.org/uploads/images/ac1bfca4b2f54a1ed3c8a20edc5f34495e79b0a3.jpg)

运行后，通过virtualAlloc函数以及拷贝指令脱壳，在0x10010000地址处，写入了一个另外一个dll，暂称为primarydll。

![p3](http://drops.javaweb.org/uploads/images/46113d2b82d21476e780818e015c7925ba247b9d.jpg)

程序最终会执行到primarydll的入口处，primarydll的入口处代码，会执行`sub_100122B6()`函数，查看此函数的代码。

![p4](http://drops.javaweb.org/uploads/images/c05164fa9256626407b273a236198772d91a7ee1.jpg)

首先会设置一系列IE注册表相关的值，然后启动一个线程。查看线程函数地址。

![p5](http://drops.javaweb.org/uploads/images/4895b095f6cfe5c6dbec9cc028ec4612caee104a.jpg)

通过三个函数注册RPC服务，开启监听。这样中毒电脑就可以接受黑客的控制。接着往下走，样本会对NTUSER.LOG文件进行操作。随后便来到一个while true中。

![p6](http://drops.javaweb.org/uploads/images/0a61c3156505cff631788eba21578c3b7df36e55.jpg)

在循环中，会调用`sub_10012740()`函数，静态分析此函数，可以看到样本在构造了http请求相关的字段后，通过CoCreateInstance来启动IE，去下载可执行文件。具体的url为：`http://5.149.254.114/Microsoft/Update/KC074913.php(已经失效)`

![p7](http://drops.javaweb.org/uploads/images/e6c85a7df8478dce1a08ee39c04cd03a2ef14dce.jpg)

### 2. xxx.sys驱动分析

恶意样本实际运行时创建的是一个随机名字的驱动文件，在此以xxx.sys代替。由于驱动加了壳所以主要通过动态调试来分析。首先进入svchost的进程的上下文，以便把分配好的内存映射到ring3的地址空间。

![p8](http://drops.javaweb.org/uploads/images/d972b9554dac08e227ba7a5ed871db40150a067d.jpg)

初始化APC，从下图中可以看到 KeInitializeApc的NormalRoutine被设置为0x00c453cc

![p9](http://drops.javaweb.org/uploads/images/32fb709bd2dbfe2ed212d05dbe7c1c909bcab181.jpg)

插入刚才初始化的APC

![p10](http://drops.javaweb.org/uploads/images/6bf7b3aaf77f99d6a8be622ecd2d89c53e820eac.jpg)

svchost执行到0x00c453cc的情况

![p11](http://drops.javaweb.org/uploads/images/f0e33bd08d7b6e7531573c8550eec49acd1bd07d.jpg)

从该地址向回查找可以看到这是实际上是一个PE

![p12](http://drops.javaweb.org/uploads/images/556184cfdf2a9c71c3b2815c54d6f5e05944590e.jpg)

而偏移0x53cc就是这个dll的入口点

![p13](http://drops.javaweb.org/uploads/images/23e0e995c23b2e0eaa55ea01deadc43a0d0cdea1.jpg)

至此可以看出xxx.sys先将自己的dll写入svchost的地址空间，然后通过插入apc使自己的代码执行起来。

### 3. Killdisk样本分析

将自身复制到系统盘windows目录下,重命名为svchost.exe文件，BlackEnergy的作者还真是对svchost情有独钟。

![p14](http://drops.javaweb.org/uploads/images/93fa5389da21ecbaa34af663ce8b30eca4351e63.jpg)

病毒创建一个名为Microsoft Defender Service的服务，使用该名称用来欺骗用户，看似正常的系统安全服务程序，通过该服务，启动病毒拷贝自身到Windows目录下的svchost.exe文件,启动命令行是`svchost.exe -service`。

拷贝自身到windows目录下的代码:

![p15](http://drops.javaweb.org/uploads/images/04fef0f7af5887947e8611a6d951db5735861ed9.jpg)

创建服务代码:

![p16](http://drops.javaweb.org/uploads/images/5d84a0a79d0d3528a4361da845979ea4a29c1524.jpg)

创建并启动服务成功：

![p17](http://drops.javaweb.org/uploads/images/8a279f85b6558beeb9360f12d768513352171d3e.jpg)

调整进程令牌，提升进程权限，使病毒程序具有关机和修改系统目录文件的权限。

![p18](http://drops.javaweb.org/uploads/images/f83180f0d04bfdaebceb5ed6f46363837e0e033a.jpg)

![p19](http://drops.javaweb.org/uploads/images/d426323bfb02f1c3b887a741ee20b7e550d66488.jpg)

执行病毒服务函数:

![p20](http://drops.javaweb.org/uploads/images/5f89b8a9ac7706535cee7f055a6c53e7af769911.jpg)

打开主硬盘PhysicalDrive0，将硬盘前2560个扇区的数据全部清零，破坏硬盘MBR和文件分配表等系统启动的核心数据。

打开主硬盘设备:

![p21](http://drops.javaweb.org/uploads/images/6d32a070360f62ce5c97a45cd16864f87ca63a9c.jpg)

从MBR扇区开始，循环执行256次，清除256个扇区的数据:

![p22](http://drops.javaweb.org/uploads/images/a993e27bdda3add6012ae977f7497ea12aa4cc0e.jpg)

以上操作一共执行了10次，`10*256`共计2560个扇区的数据

从根目录开始遍历磁盘目录下的指定类型的文件,创建多个线程,将遍历到的指定类型的文件内容全部清0。

病毒主要清除的文件类型列表:

![p23](http://drops.javaweb.org/uploads/images/e4eb15abbf849bf1746e02d08ea2540525fcf84b.jpg)

创建新线程,开始遍历文件:

![p24](http://drops.javaweb.org/uploads/images/d8d4b1a57e305e6aa7b066ca1726eb63e3160475.jpg)

扫描所有指定类型的文件:

![p25](http://drops.javaweb.org/uploads/images/9d60f5646f7acf35dbed640ec930e5355b6231f6.jpg)

![p26](http://drops.javaweb.org/uploads/images/c031f9a1e723dc26c429000fda9dc338c3f2eaff.jpg)

![p27](http://drops.javaweb.org/uploads/images/fe440492c237a675b690fd0e9535df38374c3879.jpg)

打开文件，将文件内容全部填充为0:

![p28](http://drops.javaweb.org/uploads/images/144f8a97643c0e82c58929a15d34d67f0c23434c.jpg)

WriteFileZeroByte函数内容:

![p29](http://drops.javaweb.org/uploads/images/5fe7d889262eef2ea852f969e71d2cd67b8b26ff.jpg)

终止系统进程lsass.exe和wininit.exe,并且记录日志，通过执行shutdown命令，重启电脑，由于系统MBR、文件分配表等信息都被破坏，系统重启后奔溃，无法修复

终止lsass.exe进程:

![p30](http://drops.javaweb.org/uploads/images/3cbbd26bf765187e9d872be4d25affcc66063146.jpg)

终止wininit.exe进程:

![p31](http://drops.javaweb.org/uploads/images/150b85e159089ae63bce8db303bebe1e6bfc8c5b.jpg)

执行shutdown命令，重启系统

![p32](http://drops.javaweb.org/uploads/images/18d79fa8e2051960a26f3171c1312f88993ea06d.jpg)

由于系统关键文件被清空，导致重启后无法正常工作，整个攻击流程攻击完成。

0x04 防御思考
=========

* * *

云端拉黑md5，杀毒引擎增加静态特征，IDS、IPS等系统上封住已知的远程服务器ip或者url，如果这些就是我们全部防御策略的话，那么下一次当我们的安全产品面临类似于BlackEnergy这样的攻击的时候，注定是脆弱的。

以攻击的第一步XLS为例，即使不使用office 0day，简简单单的宏病毒就可以达成目的。在这个入口点的防御上，使用动态分析要比静态扫描合适一些的。对于宏脚本加密的样本来说，不停地变换加密算法对静态扫描造成了太大的干扰，而动态分析技术则无惧加密变形等对抗手段。

这是哈勃文件分析系统（[http://habo.qq.com/](http://habo.qq.com/)）对攻击源头的xls文件的分析结果。

![p33](http://drops.javaweb.org/uploads/images/89fe026521879a4c46939f8782d69de11004a0ed.jpg)

![p34](http://drops.javaweb.org/uploads/images/ab7a581eb7e35fe38c1ebede07a008700af93e8c.jpg)

这是哈勃对第一个dropper文件`vba_macro.exe`的分析结果。

![p35](http://drops.javaweb.org/uploads/images/9689533af4550c2f8146a999c9ab851c82fc88a9.jpg)

这是哈勃对伪装wordpad释放并加载驱动样本的分析结果。

![p36](http://drops.javaweb.org/uploads/images/77ef5f77280be156d678af09c49f578df3ed5c82.jpg)

这是哈勃对killdisk恶意样本的分析报告

![p37](http://drops.javaweb.org/uploads/images/3556937941070fa7cfc10e77a84d6502c8529d4d.jpg)

样本加壳，数据加密已经成为黑客和木马作者的必修功课，在这种情况下传统的静态扫描越来越难以独自扛起系统防护的大旗。动态行为分析很可能成为一个备选的解决方案，即使是因为用户体验的因素而采取异步分析，也能为威胁感知和威胁情报提取提供重要帮助。

哈勃动态分析系统还在摸索中前进，但在不久的将来，类似的动态分析系统很有可能成为企业安全防护系统中一个重要的环节。