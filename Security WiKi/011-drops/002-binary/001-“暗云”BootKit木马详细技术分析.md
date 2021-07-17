# “暗云”BootKit木马详细技术分析

0x00 “暗云”木马简介：
==============

* * *

“暗云”是一个迄今为止最复杂的木马之一，感染了数以百万的计算机， 暗云木马使用了很多复杂的、新颖的技术来实现长期地潜伏在用户的计算机系统中。其使用了BootKit技术，直接感染磁盘的引导区，感染后即使重装系统格式化硬盘也无法清除该木马。该木马使用了很多创新的技术，有以下特点：

第一、隐蔽性非常高，通过Hook磁盘驱动实现对已感染的MBR进行保护，防止被安全软件检测和清除，并且使用对象劫持技术躲避安全人员的手工检测。隐蔽性极高，截至目前为止，几乎所有的安全软件都无法检测和查杀该木马。

第二、云思想在暗云木马中的使用：木马以轻量级的身躯隐藏于磁盘最前端的30个扇区中，这些常驻与系统中代码并没有传统木马的功能，这些代码的功能仅仅是到执行的服务器（云端）下载其他功能代码到内存中直接执行，这些功能模块每次开机都由隐藏的模块从云端下载。因此木马体积小巧，且云端控制性强。

第三，Ring 3与Ring 0的通信方式：微软正统的通信方式是Ring 0代码创建驱动设备，Ring 3代码通过打开Ring 0创建的设备开实现相互之间的通信。常见的木马使用的通信方式则是在Ring 0对指定的API函数进行Hook，而暗云木马是通过注册回调的方式来实现。

第四，操作系统全量兼容：一份BootKit同时兼容x86、x64两种版本的操作系统，且能够兼容xp、win7等当前主流的操作系统版本，因此影响范围十分广泛。在推广获利方面，该木马也是涵盖当前主流的推广获利渠道——推广小网站、推广手机应用、推广游戏、大网站加推广ID。

第五，有效对抗杀软：有于木马的主体在内核中运行，且启动时间比所有的安全软件都早，因此大部分的安全软件无法拦截和检测该木马的恶意行为。木马能够在内核中直接结束部分安全软件进程，同时可以向任意安全软件进程插入APC执行。插入的APC代码不稳定，且会关闭安全软件的设备句柄，会导致安全软件崩溃或退出，大大减少了被检测的机率。

![enter image description here](http://drops.javaweb.org/uploads/images/4034fc50dde46e269962585df634fadeead97ce1.jpg)

图1. 暗云 木马启动流程图（图中按红紫绿黑分四个模块）

![enter image description here](http://drops.javaweb.org/uploads/images/ed30feac0c0697de468069f9ae02fd0e5f61c763.jpg)

图2 . 暗云木马模块功能分工示意图

0x01 常驻计算机模块（MBR）行为
===================

* * *

1. 概述：
------

* * *

电脑开机后，受感染的磁盘MBR第一时间获得CPU的控制权，其功能是将磁盘3-63扇区的木马主体加载到内存中解密执行，木马主体获得执行后通过挂钩int 15中断来获取第二次执行的机会，随后读取第二扇区中的备份MBR正常地引导系统启动。

系统引导启动时会通过int 15中断查询内存信息，此时挂钩15号中断的木马便得以第二次获得CPU控制权，获得控制权后木马挂钩BILoadImageEx函数，调用原始15号中断并将控制权交回给系统继续引导。

当系统引导代码调用BILoadImageEx加载ntoskrnl.exe时，木马便第三次获得控制权，获得控制权后木马再一次执行挂钩操作，此次挂钩的位置是ntoskrnl.exe的入口点，随后将控制权交给系统继续引导。

当引导完毕进入windows内核时，挂钩ntoskrnl入口点的木马代码第四次获得CPU控制权，此时木马已真正进入windows内核中，获得控制权后，分配一块内存空间，将木马内核的主功能代码拷贝到分配的空间中，并通过创建PsSetCreateThreadNotifyRoutine回调的方式使主功能代码得以执行。至此完成木马由MBR到windows内核的加载过程。

木马主功能代码的主要实现以下三个功能：1、劫持磁盘驱动实现隐藏和保护被感染的MBR；2、向ring3的一个svchost进程插入APC；3、通过设置注册表回调来接收ring3返回。

插入到svchost代码只实现一个简单的功能：判断操作系统类型，从云端下载相应的Addata.dat模块到本地，解密执行，云端模块的URL硬编码在Shellcode中。

![enter image description here](http://drops.javaweb.org/uploads/images/fda335fb745b863a822f8031c8f9047b9ef6ebb6.jpg)

图3. BootKit 启动过程示意图

2. 代码细节：
--------

* * *

感染后的MBR（黑）与原始MBR（红）对比图

![enter image description here](http://drops.javaweb.org/uploads/images/1fdeb9e1aae0facbd706b17dd4141b57465bc65d.jpg)

0x02 云端模块一（Addata.dat）行为
========================

* * *

1. 概述
-----

* * *

此模块为木马云端配置的第一个模块，其格式固定，以简单的循环移位的方式进行加密，解密后的模块数据结构如下：

![enter image description here](http://drops.javaweb.org/uploads/images/5e1b5732a6efdb8197ad73cb65b2bf56e68bed02.jpg)

云端模块1解密后的数据结构

该模块的前4字节为标志“CODE”，仅作为数据合法性校验，校验成功后直接执行其后的Shellcode，而Shellcode的功能则是负责将Addata.dll在内存中加载，最终从其入口点处开始执行之。

Addata.dll的主要功能是下载者，其具体的行为仍然依赖于云端配置，其运行后首先会从云端下载配置文件，配置文件所在的URL为：http://ad.sqc3.com/update/config.db，该URL硬编码在文件中。下载后解析配置文件，由配置文件来决定代码中的功能是否执行，以及具体的参数信息，能够实现的功能以及实际配置文件信息如下表所示：

| 能实现的功能 | 开关 | 参数信息 |
| --- | --- | --- |
| 设置浏览器主页 | 关 | none |
| 检测指定杀软 | 关 | none |
| 下载Dll并Load | 关 | none |
| 下载Exe并运行 | 关 | none |
| 下载Shellcode执行 | 关 | http://jm.sqc3.com/cn/jmdm.db，解密后传入内核 http://jm.sqc3.com/cn/jmdmx64.db（如果是64位系统） |

2. 代码细节：
--------

* * *

Addata.dll中硬编码的配置文件URL信息

![enter image description here](http://drops.javaweb.org/uploads/images/5cd0ce0bfb35a8b84f8cf7acf6cea7c57ef4ba89.jpg)

设置浏览器主页的相关代码

![enter image description here](http://drops.javaweb.org/uploads/images/dffd4bc0805d4ec4c0489a6e629204f7eeb601d9.jpg)

对下载的文件可进行不同的处理（LoadLibrary、CreateProcess、加载到内核执行），这里还有一个很有意思的代码：DeleFileA(“我真的凌乱了…….”)，作者都凌乱了，真的很复杂！

![enter image description here](http://drops.javaweb.org/uploads/images/8437c979112ca76ea4c518134b9da772624c9a80.jpg)

Shellcode是通过NtSetInformationKey代入内核的（内核注册了cmpCallBack）

![enter image description here](http://drops.javaweb.org/uploads/images/d3352bbd26515787fa481dbe370d47b664ea1f61.jpg)

0x03 云端模块二（jmdm.db）行为
=====================

* * *

1. 概述
-----

* * *

此模块为木马云端配置的第二个模块，由云端模块一下载后传递到内核执行，已相对较为复杂的加密算法进行加密，其中文件的前0x32字节为解密key，解密后的模块数据结构如下：

![enter image description here](http://drops.javaweb.org/uploads/images/1dbc6707858b5ade9be86fe74e5d13b6c6d5ace7.jpg)

云端模块2解密后的数据结构

由于此木马同时兼容32位操作系统和64位操作系统，因此这个此模块包含两个版本，内核模块会根据操作系统的类型执行相应的Shellcode，因为两套代码功能完全一致，以下仅分析x86部分。

该模块首先被NtSetInformationKey传入内核，由内核模块从内核Shellcode开始执行，内核Shellcode的功能有如下两个：

```
1）结束指定杀软进程，包括kxetray.exe、kxescore.exe、QQPcTray.exe，由于管家的进程有object钩子防护，因此不会被干掉。

2）遍历进程，如果进程名为以下之一，则将尾部的应用层Shellcode 以apc的方式插入到该进程中，插入一个进程后便退出遍历，不再插其他进程。具体进程列表如下：360tray.exe、360safe.exe、360sd.exe、360rp.exe、zhudongfangyu.exe、QQPcRtp.exe、KSafeSvc.exe、KSafeTray.exe、BaiduSdTray.exe、BaiduAnTray.exe、BadduAnSvc.exe、BaiduHips.exe、BaiduProtect.exe、wscntfy.exe、spoolsv.exe、alg.exe，以上进程名均硬编码于Shellcode中。

```

应用层Shellcode被插入指定进程后开始执行，其功能是在内存中动态加载jmdm.dll文件并跳到其入口点执行。

jmdm.dll的主要功能依然是下载者，其代码与Addata.dll有60%以上的相似性，可以确定为同一份源码修改而来，其具体的行为仍然依赖于云端配置，其运行后首先会从云端下载配置文件，配置文件所在的URL为：http://jm.sqc3.com/cn/jmdmpz.db，该URL硬编码在文件中。下载后解析配置文件，由配置文件来决定代码中的功能是否执行，以及具体的参数信息，能够实现的功能以及实际配置文件信息如下表所示：

| 能实现的功能 | 开关 | 参数信息 |
| --- | --- | --- |
| 设置浏览器主页 | 关 | none |
| 关闭指定杀软句柄 | 开 | \Device\360SelfProtection \Device\360SpShadow0 \Device\qutmipc \FileSystem\Filters\FltMgrMsg \FileSystem\Filters\qutmdrv |
| 检测杀软进程 | 关 | none |
| 下载Dll并Load | 关 | none |
| 下载Exe并运行 | 开 | http://tg.sqc3.com/tg/inst.exe http://tg.sqc3.com/tg/update.exe |

以上行为执行完毕后，木马会等待下载的inst.exe、update.exe运行完毕后重新创建一个新的宿主进程，随后调用ExitProcess退出原始宿主进程。

2. 代码细节
-------

* * *

调用ZwTerminateProcess结束安全软件进程kxetray.exe、kxescore.exe、QQPcTray.exe，由于管家的进程有object钩子防护，因此不会被干掉。

![enter image description here](http://drops.javaweb.org/uploads/images/a010c77e4c240e8fd15cfaca5a5af39a5e99c7ff.jpg)

遍历进程，看进程是否在硬编码的进程列表中，如果是，则插入apc，找到一个进程之后跳出循环，即只向一个进程插入apc

![enter image description here](http://drops.javaweb.org/uploads/images/8cb3ee05ddc676aaa5e8b015b16a4a9c8af3ac96.jpg)

插apc的具体代码

![enter image description here](http://drops.javaweb.org/uploads/images/3443cdd2abd0766766fdad3ffe7f3b3e5d659c8b.jpg)

关闭名为\Device\qutmipc等的设备句柄，名称字符串硬编码于文件中

![enter image description here](http://drops.javaweb.org/uploads/images/6e364d2a52db1b3da32ae126b890f6e649c1fbd9.jpg)

配置文件http://jm.sqc3.com/cn/jmdmpz.db 的URL硬编码在文件中

![enter image description here](http://drops.javaweb.org/uploads/images/58fb226ee8f1d4499f536f723f3669e5d3cf7973.jpg)

下载指定URL的文件到本地，加载或者运行

![enter image description here](http://drops.javaweb.org/uploads/images/536c96eaa169c3be7c4649e84e8a7919f93fcd6d.jpg)

0x04 木马的盈利推广部分（inst .exe、update.exe）行为
======================================

* * *

1. 概述：
------

* * *

木马的最终目的只有一个——盈利，而inst.exe和update.exe，这连个落地的PE文件，则是真正能够使作者获得丰厚收益的模块，也是木马开始执行真正恶意的行为。

Inst.exe运行后首先在桌面上释放一个名为“美女视频聊天”的快捷方式，该快捷方式指向一个http://haomm.com，并带了一个推广id，实现推广网站盈利。 Inst.exe还会释放XnfBase.dll、thpro32.dll两个dll到%appdata%目录下，并通过注册服务的方式加载这两个dll。 XnfBase.dll实现的功能是LSP劫持，当用户使用浏览器浏览www.hao123.com、www.baidu.com等网站的时候在其网址尾部添加推广ID，从而实现获利。thpro32.dll实现的功能是：不断地删除系统中指定提供者的LSP，防止其他木马或安全软件通过LSP再次修改推广ID。

Update.exe运行后会创建两个svchost.exe傀儡进程，并将解密出的功能模块分别注入到两个进程中，一个负责向安卓手机安装推广app、另一个实现向含有“私服”等关键词的QQ群上传共享文件，用来推广私服游戏获利。

![enter image description here](http://drops.javaweb.org/uploads/images/6a94fc3c3cb9b88505a99268021b69b7fb419ff0.jpg)木马通过各种推广来实现盈利

2. 代码细节：
--------

当用户用浏览器访问www.baidu.com等网站时，为其添加推广id，实现推广获利

![enter image description here](http://drops.javaweb.org/uploads/images/8f024a02e0266ea084e865250cdedd02bc3e7308.jpg)

在桌面上创建的美女视频聊天快捷方式，推广haomm.com这个网站

![enter image description here](http://drops.javaweb.org/uploads/images/fccb74dbd49809d625dc455e187f20b23417f97e.jpg)

不断检测是否有LSP模块，有则删除，保护自己的推广ID不被修改

![enter image description here](http://drops.javaweb.org/uploads/images/e1238c7d53010923fbfa2df374d70aaddd76b143.jpg)

向指定名称的QQ群上传私服游戏，进行私服游戏的推广

![enter image description here](http://drops.javaweb.org/uploads/images/35697cc2598e057607f7080611aa02920f28b923.jpg)