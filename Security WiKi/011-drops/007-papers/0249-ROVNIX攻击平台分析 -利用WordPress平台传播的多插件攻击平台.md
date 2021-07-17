# ROVNIX攻击平台分析 -利用WordPress平台传播的多插件攻击平台

微信公众号:Antiylab

0x00 背景
=======

* * *

近期，安天安全研究与应急处理中心（安天CERT）的安全研究人员在跟踪分析HaveX家族样本的过程中，意外地发现了Rovnix家族（Trojan/Win32.Rovnix）在建立其恶意代码下载服务器时，也开始使用类似HaveX的方式，即：使用WordPress搭建的网站，或入侵第三方由WordPress搭建的正常网站（HaveX的C&C服务器地址都是通过入侵由WrdPress搭建的网站得到的）。因此，安天CERT 的研究人员对Rovnix家族展开分析。

0x01 威胁概述
=========

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/7eefaca0c33c43005fcae745f44d9e8c595dbb41.jpg)

图 1 威胁图示

Rovnix 家族于2011年首次被发现，至今依然十分活跃。该家族恶意代码插件众多，具有反调试、反虚拟机、反沙箱、安装VBR-BootKit（VBR全称Volume Boot Record，卷引导记录）等技术手段，同时具有收集用户信息、盗取比特币、盗取银行密码、远程控制等功能。

该家族主要通过电子邮件传播，通过诱使用户点击邮件正文中的链接地址下载Rovnix主程序（安天CERT迄今共发现了300多个恶意代码下载地址）。主程序在执行后会搜集、回传用户系统信息，其中，信息回传地址以硬编码形式加密保存在主程序内部。随后，主程序根据GDA（Domain Generation Algorithm）计算出配置文件的下载地址。配置文件使用RC2算法加密，每个配置文件功能各不相同。例如：配置文件Host.dat存放插件下载服务器地址。主程序根据当前系统版本下载对应的插件列表，再下载该插件列表中的恶意插件，这些插件即是上述具有安装洋葱（Tor）客户端、盗取比特币、盗取银行密码、远程控制等功能的插件。

0x02. 样本功能分析
============

* * *

**2.1 主程序分析**

样本标签

```
病毒名称 Trojan/Win32.Rovnix

MD5 6EB761EA46A40AD72018D3CEE915C4CD

处理器架构 X86-32

文件大小 207960  字节

文件格式 BinExecute/Microsoft.EXE[:X86]

时间戳 2015-05-11 10:40:37

数字签名 NO

加壳类型 无

编译语言 Microsoft Visual C++

VT首次上传时间 2015-05-11 14:33:00

VT检测结果 32 / 56

```

Rovnix主程序的主要功能是回传用户系统信息、释放其他插件、安装Bootkit以及加载插件。

![enter image description here](http://drops.javaweb.org/uploads/images/e75424d0607d181e1885e74b82e976a66f1c7924.jpg)

图 2 主程序流程图

1、样本运行后首先解密出自身代码，将地址401000处的数据清0，再重新写入解密后的代码。

![enter image description here](http://drops.javaweb.org/uploads/images/7b03bf86d37fe20128d10ef84a9416205bbad435.jpg)

图3 解密自身代码

2、进入代码空间后，使用Xor 0x14h解密对应的字符串。

![enter image description here](http://drops.javaweb.org/uploads/images/2cafe77d3ad507fb33d6a72628c26a5d38f8e787.jpg)

3、随后检测样本运行环境，包括是否运行于虚拟机环境、沙箱环境。样本使用的异常处理机制并非常见的SHE（Structure Exception Handler，结构化异常处理），而且采用了VEH（Vectored Exception Handler，向量化异常处理）。样本检测当前运行环境是否支持脚本语言（如：Python、perl等），并检查样本执行路径及文件名中，是否包含sample、virus等字样（这通常是反病毒厂商在其动态分析平台所使用的文件名），从而判断是否运行于恶意代码分析环境。同时，这些环境信息也会上传到C&C服务器。

![enter image description here](http://drops.javaweb.org/uploads/images/d7a0ec22e1a0cc522eed30dfd62457e7327ed282.jpg)

4、该样本随后执行提权（WIN7利用漏洞提权、XP利用普通提权）、复制自身到其他目录、修改文件时间、自删除、检测反病毒软件、回传系统信息、安装VBR-BootKit等一系列操作。

5、样本运行后会释放4个文件：

```
%Application Data%\Microsoft\Crypto\RSA\RSA1342183348.dll payload文件

%Temp%\tmp1.tmp.exe 正常文件contig.exe

%system32%\BOOT.dat BOOT加密引导数据

%Temp%\NTFS.sys 正常引导文件

```

RSA1342183348.dll是payload程序。样本会将文件时间修改为系统文件svchost.exe的时间（即系统安装时间），添加注册表启动项，利用rundll32.exe加载并启动，而它的启动参数是利用内核驱动模式加载的“DllInitialize”参数。

```
RSA1342183348"="C:\\WINDOWS\\system32\\rundll32.exe \"C:\\Documents and Settings\\”用户目录”\\Application Data\\Microsoft\\Crypto\\RSA\\RSA1342183348.dll\",DllInitialize"

```

tmp1.tmp.exe是微软Contig程序，当样本因为卷没有足够的自由空间导致安装VBR-BootKit失败时，它将运行Contig.exe程序来调整文件数据。

注：Contig是一个单个文件碎片整理程序，其目的是使磁盘上的文件保持连续。对于持续被碎片化的文件，或者如果您希望确保碎片数量尽量少，它可以完美地迅速优化文件。

恶意代码释放Contig V1.7版本使用如下静默方式运行，整理%system32%\BOOT.dat文件碎片，执行命令为：

```
Tmp1.tmp.exe -q -n "C:\WINDOWS\system32\BOOT.dat" 256000

```

Rovnix的关键功能是安装内核模式文件VBR-BootKit。样本判断系统是否存在加密软件，决定是否安装BootKit并执行，检查系统是否使用BitLocker加密，遍历进程查看是否有TrueCrypt.exe和VeraCrypt.exe（这两个进程都是加密软件），如果Rovnix发现系统使用上述加密，它将不安装BootKit，未发现则安装VBR-BootKit。如果Rovnix成功安装VBR-BootKit，会产生蓝屏，并导致系统重新启动；安装VRB-BootKit失败，则加载Payload程序。

6、Rovnix连接网络，下载文件，下载地址已经失效：

http://heckwassleftran.ru/R3_QACBABON/up.bin

C&C：

http://heckwassleftran.ru/cgi-bin/050515/post.cgi

3.2 插件分析
========

* * *

安天CERT研究人员对Rovnix的插件进行分析，发现若干其他插件，这些插件均从相关恶意服务器下载执行，其中包括具有TOR功能的洋葱匿名网络服务的客户端程序、后门程序、驱动程序、虚拟网络等，详情见如下列表：

插件名称 插件功能

```
PLTOR 洋葱（Tor）客户端，可以用来进行匿名访问网络，更好的隐藏自身。

ReactorDll 该模块具有后门功能，收集系统信息进行回传，使用POST方式与服务器进行通信，接收指令并执行。如：cookie删除、开启VNC、开启socket通信等等。

BkSetup.dll 获取系统版本，提升进程权限，然后在系统中安装后门模块，并设置自启动，当所有操作完成后，进行自删除。

XX++.dll 该模块与Payload功能相同，是Rovnix早期版本的Payload文件。

LdrLoadDll 该模块为64位驱动程序。用来检测系统中是否存在杀毒软件，主要功能是加载DLL模块，并调用其导出函数。

PROXY_BOT BOT后门模块，获取系统详细版本信息，使用HTTP、FTP多种方式与服务器进行通信，可用来执行多种命令。

PLVNC 该模块可以用来对机器进行远程控制，可以获取屏幕截图、系统信息，并对系统进程多种操作。

Payload 该模块在前面有比较详细的分析，主要功能是下载其它模块，并在内存中进行加载执行，添加自启动项等。

loader32.bin 收集系统信息，使用HTTP POST的方式与服务器进行通信，加载配置文件，根据配置文件，执行相应的操作。

```

Rovnix的插件较多，目前安天CERT研究人员仅对以上9个重要插件进行了初步的定性分析。并对Payload进行了较详细的分析。

**2.3 Payload插件分析**

样本标签

```
病毒名称     Trojan[Downloader]/Win32.Rovnix

原始文件名 RSA2095805845.dll

MD5 DED8BB2AD12B2317F1DB3265B003DCB5

处理器架构 X86-32

文件大小 79872 字节

文件格式 BinExecute/Microsoft.EXE[:X86]

时间戳 2015-06-19 10:50:15

数字签名 NO

加壳类型 无

编译语言 Microsoft Visual C++

VT首次上传时间 2015-06-25 15:02:31

VT检测结果 31 / 55

```

该插件为主程序释放的DLL插件，该DLL将大量字符串与API进行加密处理，解密后的主要功能包括更新C&C地址、创建命名管道、下载更多插件等。详细分析流程图与描述如

![enter image description here](http://drops.javaweb.org/uploads/images/57d003eb51c8f37b9365a9e8ed82e19f15606032.jpg)

1、解密字符串：样本运行后首先将该样本中所使用到的系统中的DLL、要操作的注册表键值、进程名称均使用异或0x14的方式进行了加密。其中，对于窄字节形式字符串，将以BYTE为单位异或0x14，对于宽字节形式字符串将以WORD为单位异或0x14。

![enter image description here](http://drops.javaweb.org/uploads/images/5c392951975915c6503a6cfe036e237f7cca4e54.jpg)

2、随后样本创建线程，进行加载样本进程的判断，并置位对应的内存标志，样本判断如下4个加载自身的程序。

```
进程名称     标志位 

winlogon.exe 0x7601634C 

svchost.exe 0x76016348

explorer.exe 0x76016350

rundll32.exe 0x76016354

```

对不同的加载程序，做相应的处理，如：在线程1中，若样本运行在svchost.exe或rundll32.exe进程中，会调用SetErrorMode(0x8003)设置系统不显示Windows的多种错误对话框，隐藏运行。如果不是上述4种中的一种加载自身，则进程退出。

3、样本获取系统文件路径并提取卷标、磁盘类型等信息。如果样本是NTFS类型，则置位76016344内存为1

![enter image description here](http://drops.javaweb.org/uploads/images/57b74484bd8d8c891f8d26281f5dcc0a1d6125a4.jpg)

并根据磁盘信息创建互斥量字符串

![enter image description here](http://drops.javaweb.org/uploads/images/fffcd78f03390423fa67f7eb6e8063d8d957ad6e.jpg)

互斥量的组成Global\BD（文件系统类型\卷序列号），如：Global\BDNTFS816090805。

4、样本创建线程2，进行临时文件夹下的文件删除操作。目的是删除主程序释放的盗取系统信息的临时文件。

5、随后样本进入主要功能阶段，创建了三个线程：

线程3：

样本会遍历注册表HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run中的所有模块，查看当前模块是否存在，如果不存在，则会添加到启动项中。

线程4： 通过创建命名管道的方式与其他恶意进程进行通信。

![enter image description here](http://drops.javaweb.org/uploads/images/5757acad26127563316f222f5eb5667473f0dd7b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/7c349796dff8450edc7125c16e78d15eed6b3af6.jpg)

管道的命名也与卷序列号有关，.\pipe\vhost（卷序列号），如：.\pipe\vhost816090805

线程5：

线程5的主要作用是更新C&C服务器并下载插件执行。

在样本中C&C域名有3个，均经过异或0x14后，键名称分别为：SH1、SH2、SH3，保存到注册表中，地址为：HKCU（或HKLM）\Software\Microsoft\Product\B（卷序列号）。样本读取该键值，判断是否有数据，如果有，则更新到样本中；如果没有，则使用样本中硬编码的三个C&C域名。当连网获取到新的C&C后，会更新到注册表中。

![enter image description here](http://drops.javaweb.org/uploads/images/79144dbfce468878d3f3b0ea058df7f7efb33a35.jpg)

根据GDA解密后的域名：

```
cloud58.eu
aszjhqhsbgsvcse4.onion
cloud59.eu

```

2.4 Yara规则提取（payload）
=====================

通过安天CERT提取的Payload插件相应特征，编写Payload Yara规则如下：

```
rule Rovnix_Payload_Plugins 
{
meta:
author = " AntiyCert"
date = "2015/07/20"
ref = "http://www.antiy.com"
maltype = "Rovnix_Payload_Plugins"
filetype = "dll"
         strings:
$PE32 = {55 8B EC 83 EC 08 C7 45 FC 00 00 00 00 8B 45 08 0F BE 08 89 4D F8 8B 55 08 83 C2 01 89 55 08 83 7D F8 00 74 0B 8B 45 FC 83 C0 01 89 45 FC EB DD 8B 45 FC 8B E5 5D C3}
$PE64 = {48 89 4c 24 08 48 83 ec 18 48 c7 44 24 08 00 00 00 00 48 8b 44 24 20 0f be 00 89 04 24 48 8b 44 24 20 48 ff c0 48 89 44 24 20 83 3c 24 00 74 0f 48 8b 44 24 08 48 ff c0 48 89 44 24 08 eb d3 48 8b 44 24 08 48 83 c4 18 c3}
condition:
1 of them
}

```

0x03 传播URL分析
============

* * *

2015年，安天CERT共发现了300多个恶意代码下载地址，URL对应的IP地理位置涉及34个国家，其中数量最多的国家是美国，占总数量的一半以上。这些URL有一个共同的特点，如下图所示

![enter image description here](http://drops.javaweb.org/uploads/images/107eab0bc44614bccfea6a0605a7d5e01615f48b.jpg)

图 7 Rovnix下载地址结构

与此同时，安天CERT又发现了另一个家族的样本也是使用类试的URL结构形式如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/5799603b81db1cd6b0a43991607343f0da96b254.jpg)

图8 另一个家族的地址结构

从URL结构上来看，两个家族之间是有一定联系的，都是通过邮件正文中的链接点击下载并执行，并且从传播时间上看也都是在2015年开始出现。

通过以上统计出的URL地址，安天CERT联想到了2014年出现的APT事件Havex，Havex的C&C服务器都是通过入侵由WordPress搭建的正常网站得到的。Rovnix中也有一部分的URL下载地址是入侵WordPress 搭建的正常网站得到的。Rovnix在后期回传数据时用使用了其它的C&C服务地址。

注：WordPress是一种使用PHP语言开发的博客平台，用户可以在支持PHP和MySQL数据库的服务器上架设属于自己的网站，也可以把 WordPress当作一个内容管理系统（CMS）来使用。

0x04 总结
=======

* * *

Rovnix是一个喜欢使用冷门技术的恶意代码家族，具有如下特性：它喜欢使用VEH异常处理机制，BootKit使用的是VBR-BootKit；支持众多的Windows版本，根据环境投放32位或64位的插件；定制化的插件支持多种恶意功能。这些特性让安天CERT的研究人员将其归类为专业化的攻击平台，是有可能被用来进行定向攻击的武器之一。

PS:插件Hash列表见原文

博文地址: http://www.antiy.com/response/ROVNIX.html