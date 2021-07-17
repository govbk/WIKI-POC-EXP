# 我是HDRoot！

原文：

*   [https://securelist.com/analysis/publications/72275/i-am-hdroot-part-1/](https://securelist.com/analysis/publications/72275/i-am-hdroot-part-1/)
*   [https://securelist.com/analysis/publications/72356/i-am-hdroot-part-2/](https://securelist.com/analysis/publications/72356/i-am-hdroot-part-2/)

之前，我们在追踪Winnti小组的活动期间，偶然遇到了一个非常有趣的样本。

![](http://drops.javaweb.org/uploads/images/19cbce81456554eeb78d799185b96492a0909f5f.jpg)

这个样本使用了VMProtect强壳，是一个Win64可执行程序，使用了一个来自中国广州YuanLuo科技的未知签名。并且，这个可执行文件的属性与微软的Net命令-`net.exe`很类似，甚至我们在运行样本时得到了与原版`net.exe`工具类似的输出：

![](http://drops.javaweb.org/uploads/images/8886284c46977adfed757a6fa934f23a1306543a.jpg)

伪装成`net.exe`

所有这些证据表明这个样本很可疑

0x01 Bootkit
============

* * *

此程序的代码隐秘性极强,很难对其进行庖丁解牛式的模块分析.但幸运的是，我们在一份dump中发现了一些特殊且重要的字符串:隐藏在其中的另外四个样本,win32版本win64版本,其分别各有一个libray和一个driver.

![](http://drops.javaweb.org/uploads/images/59e23ae1f97497fcb206ed865315c1e9fb90b262.jpg)

木马主体中的字符串

这些字符串让我们怀疑这个样本实际上是一个bootkit安装器。多亏了一些更明确人工痕迹，我们发现了一个类似但是没有代码保护的样本，并证实了我们的猜测。

首先运行这个工具：

![](http://drops.javaweb.org/uploads/images/32d4f75d390f6b7a268494d1a26c8bd8921c607f.jpg)

原始的HDD Rootkit输出

简单看一眼`hdroot.exe`的参数，我们就知道这个程序是干什么的-给它提供一个后门当做参数,这个工具就会在系统boot阶段帮你安装它,安装的后门必须是一个Win32可执行程序或动态链接库。

这个工具叫做 “HDD Rootkit”，于是我们就用HDRoot来命名这个样本。在2006年8月22日，版本号是1.2。

所以,上文中提到的那个隐蔽性极强的工具可能就是`hdroot.exe`,只是经过修改，在受害者设备上使用，以避免暴露工具的意图.

从Hdroot的这些资源的名称上我们能看出很多有趣的东西：

![](http://drops.javaweb.org/uploads/images/f903494a37075dd33a3e61d39994f35a2fcec943.jpg)

HDD Rootkit的资源

*   “MBR”中保存着第一部分恶意代码，这些代码会注入到受感染计算机的MBR；
*   “BOOT” – 第二部分恶意启动代码；
*   “RKIMAGE” – 第三部分恶意启动代码
*   “DLLLOAD” – 动态链接库，恶意启动代码会把这个库注入到文件系统和 autorun。

我们尝试在一个bootkit的帮助下运行一些可执行程序。在我们的试验中，这个可执行程序的角色是扮演一个良性程序，仅仅是在C盘根目录中创建一个文件。我会通过HDD Rootkit使用下面的代码来运行这个可执行程序：`hdroot.exe inst write_to_c.exe c`:

告诉它我想要在C盘中安装一个bootkit，让程序`write_to_c.exe`在系统启动时运行。

![](http://drops.javaweb.org/uploads/images/7c19a9a915b2357ae61d52f94aeb5d2f1f6ad929.jpg)

HDRoot bootkit的安装

这个工具会检查指定磁盘上的可用空间，当可用容量小于总容量30%时，会拒绝安装bootkit。

![](http://drops.javaweb.org/uploads/images/ddcf10107df13488239c6ee09935712bc2730760.jpg)

检查可用空间

所以，现在bootkit已经安装了。我们看看都发生了什么。首先，MBR中的部分代码替换成了 “MBR”资源中的恶意代码。

![](http://drops.javaweb.org/uploads/images/5d2341bbafefff44288b1cc140f7fcd26ec11f85.jpg)

“MBR”资源

前两个字节EB 70指的是跳转到第72个偏移，其他的第一部分启动代码就在这。0x70前和0xB0后的0指的是保持这些位置上的原始MBR代码不变。下图是在安装了bootkit后，一个打了补丁的MBR。

![](http://drops.javaweb.org/uploads/images/4c65ac148f39e0ee0b719327c74603986f0614c5.jpg)

在MBR中注入的恶意代码

第一部分会加载下一部分的启动代码，bootkit安装器已经把这些代码放到了第11个扇区（偏移0x1400字节）。第二部分代码会从资源“BOOT”中获取。

![](http://drops.javaweb.org/uploads/images/0cf29c01b5555cbe1a98b59362f14358caaa17c7.jpg)

第二部分启动代码

在第二部分代码中，第八个偏移上的字节是一个驱动号，下一个DWORD是一个扇区偏移，在这个位置上有下一部分启动代码。这个例子的值是0x80，指的是磁盘0和偏移0x5FD9A0，如果乘以0x200字节（扇区大小）得到的结果是0xBFB34000。这是从磁盘开始的偏移字节数，在这里放置着bootkit安装器从资源 “RKIMAGE”中获取的第三部分启动代码。

“RKIMAGE”资源中有大量的代码，会实现一个DLL（DLL是从资源 “DLLLOAD”中获取的）注入到文件系统并修改注册表，这样就能加载DLL并在系统启动时运行。因为bootkit是在较早的启动阶段执行的，这个时候还没有访问文件的api可以使用,这个bootkit是自己解析文件系统的（FAT32和NTFS）。

![](http://drops.javaweb.org/uploads/images/5b37367f4e6edd05bf761bf50c88f7fed271a094.jpg)

支持的文件系统

搜索硬编码的特殊文件，其内容已经替换成了从磁盘指定位置获取的DLL。我们发现多数版本的HDRoot使用了文件_%windir%\WMSysPr9.prx_来实现这些目的。有时候DLL会覆盖一些系统库文件，对于木马来说这绝不是一种安全的工作方式，因为这样可能会造成系统崩溃，并警告用户出现感染。在能够用于覆盖的其他文件中，我们还注意到了如下这些：

```
%windir%\twain.dll
%windir%\msvidc32.dll
%windir%\help\access.hlp
%windir%\help\winssnap.hlp
%windir%\system\olesvr.dll
%windir%\syswow64\C_932.NLS
%windir%\syswow64\C_20949.NLS
%windir%\syswow64\dssec.dat
%windir%\syswow64\irclass.dll
%windir%\syswow64\msvidc32.dll
%windir%\syswow64\kmddsp.tsp

```

然后，代码读取文件`%windir%\system32\config\system`的内容，维持`HKEY_LOCAL_MACHINE\SYSTEM`的内容。在其他字符串中，注册表实体文件中都是包含关于安装服务的信息。在OS启动时，会有大量的系统服务启动。比如，通过`svchost.exe`启动的`ServiceDll`，要运行的函数库路径就指定在`ServiceDll`的注册值中。恶意启动代码会在 “system”文件中搜索与系统服务关联的系统库路径，并将值替换成注入DLL的路径（比如，`%windir%\WMSysPr9.prx`）。在所有版本中，我们发现HDRoot利用了下面的服务：

![](http://drops.javaweb.org/uploads/images/c0d76b612c05ece60f42376df6511dba9f4ccd49.jpg)

所以，当操作系统开始运行服务时，没有加载原始服务`svchost.exe`，而是加载了恶意代码。这个恶意库只是加载和运行了从指定偏移上获取的后门，在这个位置上有HDD Rootkit。我们发现两个版本的HDRoot使用了不同的方法来完成这一操作。第一个只是把后门保存成文件`%windir%\temp\svchost.exe`，并在WinExec API函数的帮助下执行。所有迹象表明，木马作者之后觉着这个方法不是运行后门的最好办法，因为AV产品能检测到，并且启动的应用可能在检查事件时注意到并记录到系统日志。另一版的DLL并没有投放文件，而是分配了内存来读取后门，或许是为了正常执行（根据导入表来加载二进制并修复重定位）和自己运行。这种方法更隐秘，因为减少了后门被发现的几率，即使是检测到了DLL和受感染的MBR。

返回到我们的实验，当命令`hdroot.exe inst write_to_c.exe c:`运行时，我们重启了操作系统。在OS加载后，我们能看到运行程序`write_to_c.exe`的结果，虽然是一个后门，但是表现的很好。

![](http://drops.javaweb.org/uploads/images/72fc33c127a6fed0d8f4e3b0347fc943092c8126.jpg)

创建测试文件zzz.bin

在加载了Windows后，立刻能看到文件`C:\zzz.bin`，这证明程序`write_to_c.exe`已经成功执行了。

HDRoot的整个感染过程如下：

![](http://drops.javaweb.org/uploads/images/82382f6e3799716286cbe08a6b5a7d0020a90bb7.jpg)

HDRoot操作方案

有趣的是，恶意软件没有功能可以恢复在启动过程中被替换掉的原始服务。因为受影响的服务是操作系统的一部分，忽视这一做法可能会导致 Windows 故障并且造成感染被发现。这就更奇怪了，考虑到恶意软件在试图掩盖其踪迹。也只能说是 “试图”，因为恶意软件没能成功。投放的 DLL 有一个函数会储存注册表中 ServiceDll 的原始值，存储与该服务相关的 DLL 路径。但是由于第三部分的启动代码 (从”RKIMAGE"中获取)有缺陷，代码会在注入前修复"DLLLOAD"的内容，DLL开始从硬编码偏移上获取错误的数据，并阻止DLL找到正确的ServiceDll路径来重新恢复原始值.

![](http://drops.javaweb.org/uploads/images/93be6c5aab5d0be90b40a093f30c2d75d20fb5a6.jpg)

路径保留在了注册表中的注入恶意DLL

![](http://drops.javaweb.org/uploads/images/41593fd11abdc684a2114a79cc9d194736357472.jpg)

错误的注册表路径和值名称

![](http://drops.javaweb.org/uploads/images/0824f5b84b238be8581334689a3bb50caaa12834.jpg)

用ServiceDll的原始值错误地覆盖了注册表SubKey

所以，我们必须要说，这个木马并不细心，你不会认为这个木马来自严谨的APT小组 Winnti。但是，我们注意到这个木马的作者在努力地让这个bootkit能在启动阶段正常运行，避免在OS加载时被完全拦截。但是，上面提到的一些失误导致感染在受害者计算机上留下了一些可疑的迹象。例如，原始服务，比如Windows Update和Task Scheduler无法运行了，但是看来没人注意到。

0x02 后门
=======

* * *

因为配合HDRoot安装的后门可能是任意的，所以我们无法描述每个案例中HDRoot bootkit会运行什么木马。但是，在跟踪HDRoot时。至少我们已经收集到了两类木马。第一种是手动从感染了HDRoot的受害者硬盘中提取的。另一种是在一个独立的投放程序中找到的，这里面包含了HDRoot和安装的后门。

第一类后门
-----

![](http://drops.javaweb.org/uploads/images/03d2ee688d1bc09a37a2dbac5da6ab340b95a437.jpg)

这个木马系列是服务器端的Derusbi，我们曾在几次与Winnti相关的事件中观察到。通常这个DLL的内部名`OfficeUt32.dll`是并且会具有下面的导出函数：

```
DllRegisterServer
DllUnregisterServer
ServiceMain
SvchostPushServiceGlobals
WUServiceMain
__crt_debugger_hook

```

不同版本的函数也不同。主要的DLL在主体中还包括其他的木马组件，通常都是`xor-cipher`.

![](http://drops.javaweb.org/uploads/images/165274f87f4e9b1b80b0fef8ee147ed68a5b1ea6.jpg)

保留额外模块的结构

HDRoot bootkit安装的Derusbi样本包含了一个远程shell模块和网络驱动模块。

安装例程是在导出函数“`DllRegisterServer`“中实现的。当调用时，这个函数会执行下列操作：

*   把自身复制到文件夹 “`%System32%\wbem\`“，名称由“ntfs”+三个随机字母组成，扩展名是 “.mof”，比如“`ntfsqwe.mof`“，并把年份设置到文件属性中的2015年。
*   将包含了自身路径的字符串放到注册表中的“`ServiceDll`”值，与系统服务 “`iphlpsvc`” 或 “`wuauserv`” 关联，具体取决于Windows系统版本，并把“`ServiceDll`”的原始值以加密形式保存到同一个注册表键值的“`Security`”参数。在系统启动时执行木马。
*   在启动了木马服务后，启动被替换的原始服务，运行在木马安装时，运行与“`Security`”参数中指定的服务管理的动态链接库。

木马会将配置数据以加密的形式储存在`HKLM\SOFTWARE\Microsoft\Rpc`注册表键值的“`Security`”参数中。这里面包含了独特的计算机标识符，以及用于匹配输入的CC服务器数据包的签名。

木马可以直接连接到CC服务器，如果在设置中指定了CC；如果没有定义CC服务器，也可以进入监听模式。我们发现的与HDRoot bootkit相关的样本是在监听模式下工作。

第一类后门：驱动
--------

![](http://drops.javaweb.org/uploads/images/f9082c9d1bcf5ad76c57696faaa62deaa57051dd.jpg)

（驱动是在2012年11月19日 17:11:14签发的，使用了韩国在线游戏厂商XL Games的证书。这个证书在2013年6月21日撤销了。其序列号是**7b:d5:58:18:c5:97:1b:63:dc:45:cf:57:cb:eb:95:0b）**

主木马DLL会解密，投放并运行rootkit作为一个文件 “`%System32%\Drivers\Lst_Update.sys`”。在过程开始，驱动就会移除所有在启动过程中创建的注册表键值和真正的驱动文件。rootkit中包含了恶意网路活动，是监控工具通过hook “`\Device\Tcp`” 或 “`\Driver\nsiproxy`”系统对象的`IRP_MJ_DIRECTORY_CONTROL`服务例程。另外，驱动还通过hook文件系统驱动 “`\FileSystem\Ntfs`”的`IRP_MJ_DIRECTORY_CONTROL`服务例程，从用户模式中隐藏了文件“`\windows\system32\wiarpc.dll`”。

如果木马在监听模式下工作，rootkit还会参与通讯例程。木马会嗅探所有输入的网络数据包并在其中搜索特制的签名。如果找到，木马会重定向这些数据包来监听主木马模块打开的数据包。主模块会在所有的网络接口上随机选择一个端口，在上面创建一个网络socket。如果rootkit推送了一个与签名匹配的网络数据包，主模块就会处理。这个网络数据包中包含有命令代码和必须执行这个命令的模块ID。已知的木马版本会识别5种不同命令的模块：

![](http://drops.javaweb.org/uploads/images/7e8dadcf4a1ea23379902219738efb017ceeafb4.jpg)

第一类后门：远程shell
-------------

![](http://drops.javaweb.org/uploads/images/3fee55c0a2092b899cd3b0c5476dad4148147f28.jpg)

正如前面提到的，除了网路驱动，在Dersubi样本中还发现了唯一的一个额外模块-远程Shell。主木马模块会解密，投放并运行这个远程shell作为文件“`%Systemroot%\Help\perfc009.dat`”。这个DLL的内部名称是`Office.dll`，一个导出函数是R32。这个库是通过执行下面的命令行运行的：

`rundll32.exe %Systemroot%\Help\perfc009.dat R32 <random_number>`

其中`<random_number>`是一个由主模块生成的预共享值。

远程shell库会创建两个名称管道，用于与主模块通讯：

```
\pipe\usb<random_number>i
\pipe\usb<random_number>o

```

攻击者发送的执行命令预计就是通过管道`\pipe\usb<random_number>o`来的。当这个命令要在工作目录`%SystemDrive%`中创建一个新的进程是时，已经创建的进程标准输入就会设置从管道`\pipe\usb<rando_number>i`中获取命令。也就是说，执行程序的输入是来自攻击者，程序输出会返回到攻击者，构成了一个高效的后门通道。

第二类后门：投放程序
----------

![](http://drops.javaweb.org/uploads/images/3d1bf74f6c50f0e0c49dae80cd24419bf53b0fc5.jpg)

我们发现的一个样本结果是HDRoot使用的一个一键后门安装器。这是一个Win32可执行程序，根据标头的数据戳显示，其编译日期是2013年11月18日。这个可执行程序中包括了自定义类型 “MHM”的资源 “102”和 “103”。这些就是HDRoot安装器的可执行程序和安装的后门。

已安装后门的角色是由可执行程序中的资源 “102”扮演的，会投放为文件`%windir%\bootmgr.exe`。（运行几步，我们必须要说这不是一个后门而是一个下载器。） “HDRoot”工具，也就是资源 “103”会投放为`%windir%\hall32.exe`。然后，投放器会运行下面的命令行：

`%windir%\hall32.exe inst %windir%\bootmgr.exe c:`

指令HDRoot安装器`hall32.exe`来安装HDRoot bootkit到硬盘C盘，接下来在系统启动时运行下载器`bootmgr.exe`。

0x02 下载器
========

* * *

![](http://drops.javaweb.org/uploads/images/34aee5c98145c105239170b9155cff5d2a9cd91f.jpg)

下载器bootmgr.exe和投放器类似也是在2013年11月18日编译的。根据其主体中指定的列表，这个下载器会通过URL下载文件并运行：

```
http://www.gbutterfly.com/bbs/data/boot1.gif
http://www.btdot.com/bbs/data/boot1.gif
http://boot.ncook.net/bbs/data/boot1.gif
http://www.funzone.co.kr/bbs/data/boot1.gif
http://www.srsr.co.kr/bbs2/data/boot1.gif

```

如果这些URL都可用，下载器会将下面的某个文件投放到磁盘上并运行：

```
%windir%\v3update000.exe
%windir%\v3update001.exe
%windir%\v3update002.exe

```

下载器会检查投放的文件大小，只运行大于20896字节的文件。

结果表明这是一个双重下载器：在其主体中还有具备下载功能的另一个样本。木马会把文件投放为`%windir%\svchost.exe`，并接着使用参数“`install`”来运行。出于某种原因，在运行了第二个下载器之后，木马会使用下面的命令行立即停止网络连接共享服务：

`cmd.exe /c net stop sharedaccess`

下载器主体中还指定了其他的文件，用于检查文件系统：

```
%windir%\system32\midimapbits.dll
%windir%\system32\mpeg4c32.dll
%windir%\winurl.dat

```

第二个下载器
------

![](http://drops.javaweb.org/uploads/images/7dbb69807fcda7a163fcb99944996db12acc623d.jpg)

这个木马能够识别两个参数：“`install`”* 和 “`remove`”。在安装过程中，会创建一个自启动 “`Winlogon`”服务，其描述是“`Provides automatic configuration for the 802.11 adapters`”，会调整为运行自己的可执行程序。“`remove`”参数的意思是删除自身. 在运行时，服务会解密主体中的URL，并尝试在地址上附上“`default.gif`”来下载内容。下面是解密后完整的URL：

```
http://www.netmarble.net/
http://www.nexon.com/
http://www.tistory.com/start/
http://m.ahnlab.com/
http://www.joinsmsn.com/
http://fcst.co.kr/board/data/media/
http://www.hangame.com/
http://www.msn.com/
http://adw.naver.com/
http://www1.designrg.com/
http://www.topani.com/
http://www.nate.com/
http://www.v3lite.com/
http://www1.webschool.or.kr/
http://snsdate.gndot.com/
http://www.srsr.co.kr/bbs2/data/
http://funzone.co.kr/bbs/data/
http://www.moreuc.com/
http://www1.ncook.net/

```

如上的url列表中包括了一些合法网站,正常情况来说,这些合法网站是不可能寄存木马的. 如果寄存了木马那么只有一个可能:它被入侵了.

这个url列表会下载到如下路径`%windir%\image.jpg`。但是，这只是一个中间过程。木马解析的应该是一个文本文件。这个文件的第一行应该包含只比139大的数；如果不是，木马就会跳过内容处理。第二行是URL。木马会使用这些URL来下载可执行程序，第三行指定了可执行程序的文件名称。在下载了木马后，重置文件的前两个字节 为“MZ”，并运行。

同时，在下载过程中，木马会尝试移除特定的杀毒软件。在注册表中发现了卸载命令后，木马会运行这个命令并通过操作应用上的用户界面按键；来移除3个AV产品： AhnLab的V3 Lite, AhnLab的V3 365 Clinic 和 ESTsoft的 ALYac。虽然，这些产品有自己的进程，但是木马还包括了交互函数来禁用Naver Vaccine和McAfee安全中心。这些厂商都说这个木马是用来攻击韩国的目标。

因为这个木马已经很久了，我们无法根据下载器中指定的URL下载到相关的材料。服务器也没有响应，页面上也没有内容。

0x03 早期发现
=========

* * *

实际上，我们并不是首家遇到HDRoot木马的AV公司。在2013年末。韩国公司AhnLab就发表了关于ETSO入侵小组的[详细报告](http://global.ahnlab.com/global/upload/download/documents/1401223631603288.pdf)。ETSO木马，根据AhnLab的分类，对应的就是我们检测到的Winnti木马。在他们的分析过程中，AhnLab的工程师发现了遭到感染的MBR，根据他们的描述（14-15页，“2.5维持网络迹象”），像是HDRoot bootkit 安装器的作用结果：

![](http://drops.javaweb.org/uploads/images/7851b884927de7b3963c8356cd600bcd9ff76570.jpg)

AhnLab的HDRoot工作方案

另外，我们还知道熟悉HDD Rootkit工具的事件处理人员并不一定是来AV公司。但是，当谈到检测时，尽管这个危险的威胁比较老了，杀毒产品还是不能很好地检测到。

0x04 统计数据
=========

* * *

不出所料，据KSN称，HDRoot感染主要分布在Winnti感兴趣的区域-东南亚，尤其是韩国。但是其他的地区也出现了感染，并且这一威胁的程度和作用是巨大的。

![](http://drops.javaweb.org/uploads/images/f2831d13f605238fd72b577d66c752f3313110e3.jpg)

与HDRoot相关的木马活动

需要重点指出的是，这个数量并不能代表目标的性质。看起来通过简单地观察数量，我们无法知道哪些类型的公司遭到了攻击。所以，从对某个国家造成的损害来看，这幅图讲了一个不同的故事。

例如，我们现在正在解决俄罗斯和英国两家公司中的HDRoot感染，在这里，多个使用了我们产品的服务器上都检测到了这个木马。在这两个案例中，感染造成的损失都很大，尤其是俄罗斯的公司，很多公司客户都受到了影响。但是，在图上，俄罗斯只遭到了一次攻击，而UK遭到了23次攻击。

虽然，我们还没有发现HDRoot使用了很多木马系列，目前已知HDRoot的活动就是与Winnti存在关系，我们继续假设这个bootkit可能用在了多次APT攻击中。我们已经知道了Winnti活动和其他先前的APT活动都出现了重合。在考虑了HDRoot安装器的特性是一个独立的工具，很可能其他的威胁小组已经掌握了这个bootkit。

我们识别HDRoot木马为：

*   **Hacktool.Win32.HDRoot**
*   **Hacktool.Win64.HDRoot**
*   **Rootkit.Win32.HDRoot**
*   **Rootkit.Win64.HDRoot**
*   **Trojan.Boot.HDRoot**

与HDRoot bootkit相关的后门和下载器：

*   **Backdoor.Win64.Winnti**
*   **Trojan.Win32.Agentb.aemr**
*   **Trojan.Win32.Genome.amvgd**

0x05 入侵标志
=========

* * *

样本哈希
----

```
2c85404fe7d1891fd41fcee4c92ad305
4dc2fc6ad7d9ed9fcf13d914660764cd
8062cbccb2895fb9215b3423cdefa396
c7fee0e094ee43f22882fb141c089cea
d0cb0eb5588eb3b14c9b9a3fa7551c28
a28fe3387ea5352b8c26de6b56ec88f0
2b081914293f415e6c8bc9c2172f7e2a
6ac4db5dcb874da2f61550dc950d08ff
6ae7a087ef4185296c377b4eadf956a4
e171d9e3fcb2eeccdc841cca9ef53fb8
ae7f93325ca8b1965502b18059f6e46a
e07b5de475bbd11aab0719f9b5ba5654
d200f9a9d2b7a44d20c31edb4384e62f
cc7af071098d3c00fdd725457ab00b65
c0118c58b6cd012467b3e35f7d7006ed
c8daf9821ebc4f1923d6ddb5477a8bbd
755351395aa920bc212dbf1d990809ab
11e461ed6250b50afb70fbee93320131
acc4d57a98256dfaa5e2b7792948aaae
1c30032dc5435070466b9dc96f466f95
7d1309ce050f32581b60841f82fc3399
b10908408b153ce9fb34c2f0164b6a85
eb3fbfc79a37441590d9509b085aaaca
3ad35274cf09a24c4ec44d547f1673e7
f6004cfaa6dc53fd5bf32f7069f60e7a
c5d59acb616dc8bac47b0ebd0244f686
e19793ff58c04c2d439707ac65703410
4dc2fc6ad7d9ed9fcf13d914660764cd
8062cbccb2895fb9215b3423cdefa396
c7fee0e094ee43f22882fb141c089cea
d0cb0eb5588eb3b14c9b9a3fa7551c28

```

文件
--

```
%windir%\twain.dll
%windir%\system\olesvr.dll
%windir%\msvidc32.dll
%windir%\help\access.hlp
%windir%\syswow64\C_932.NLS
%windir%\syswow64\C_20949.NLS
%windir%\syswow64\irclass.dll
%windir%\syswow64\msvidc32.dll
%windir%\syswow64\kmddsp.tsp
%windir%\temp\svchost.exe
%System32%\wbem\ntfs<3 random chars>.mof
%System32%\Drivers\Lst_Update.sys
%Systemroot%\Help\perfc009.dat
%windir%\bootmgr.exe
%windir%\hall32.exe
%windir%\system32\midimapbits.dll
%windir%\system32\mpeg4c32.dll
%windir%\bootmgr.dat
%windir%\v3update000.exe
%windir%\v3update001.exe
%windir%\v3update002.exe
%windir%\svchost.exe
%windir%\winurl.dat
%windir%\image.jpg

```