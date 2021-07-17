# DUQ U2.0 技术分析

from:https://securelist.com/files/2015/06/The_Mystery_of_Duqu_2_0_a_sophisticated_cyberespionage_actor_returns.pdf

0x00 前言
=======

* * *

今年年初，卡巴斯基实验室在安全扫描过程中，检测到了几个影响了自家内部系统的网络入侵行为。

接着我们大范围调查了这些入侵事件。我们分析发现了一个全新的木马平台，这个平台出自Duqu APT小组之手。Duqu APT小组是世界上最神秘，水平最高的APT小组。这个小组从2012年开始销声匿迹，直到今天又卷土重来。我们分析了这新一轮攻击，结果表明这是2011年Duqu木马的升级版，怀疑与Stuxnet木马有关。我们把这个新木马和相关的平台命名为"Duqu 2.0"。

Duqu利用了0-day漏洞CVE-2015-2360（WindowsKernel中的漏洞）和另外两个0-day漏洞，攻击了卡巴斯基实验室。微软在2015年6月9日修复了第一个漏洞，另两个漏洞在近期也得到了修复。

0x01 木马剖析
=========

* * *

```
Filename:随机 / 根据具体样本而定
MD5 (根据具体样本而定): 14712103ddf9f6e77fa5c9a3288bd5ee
Size: 503,296 bytes

```

文件属性
----

MSI文件具有一下属性

*   Composite Document File V2 Document
*   Little Endian
*   OS: Windows, Version 6.1
*   Code page: 1252
*   Title: {7080A304-67F9-4363-BBEB-4CD7DB43E19D} (randomly generated GUIDs)
*   Subject: {7080A304-67F9-4363-BBEB-4CD7DB43E19D}
*   Author: {7080A304-67F9-4363-BBEB-4CD7DB43E19D}
*   Keywords: {7080A304-67F9-4363-BBEB-4CD7DB43E19D}
*   Comments: {7080A304-67F9-4363-BBEB-4CD7DB43E19D}
*   Template: Intel;1033
*   Last Saved By: {7080A304-67F9-4363-BBEB-4CD7DB43E19D}
*   Revision Number: {4ADA4205-2E5B-45B8-AAC2-D11CFD1B7266}
*   Number of Pages: 100
*   Number of Words: 8
*   Name of Creating Application: Windows Installer XML (3.0.5419.0)
*   Security: 4

其他攻击中使用的MSI文件可能具有另外一些属性。例如，我们还发现了另外几个字段：

*   Vendor: Microsoft or InstallShield
*   Version: 1.0.0.0 or 1.1.2.0 or 2.0.0.0

在Windows资源管理器的文件属性对话框中，可以查看某些字段。

![enter image description here](http://drops.javaweb.org/uploads/images/daaff3806f979209968a7da04e154ef7b6284671.jpg)

这个MSI数据包中有两个二进制文件：

![enter image description here](http://drops.javaweb.org/uploads/images/d02d15f60a1dc7601cd27953e06d0e5c83debbf5.jpg)

ActionDll是一个dll文件，ActionData0是一个经过Camellia加密，LZJB压缩的数据payload（不同情况下的加密算法和压缩算法也不同）。实际上，经过加密或压缩的二进制数据块中，会有好几层可执行代码。

![enter image description here](http://static.wooyun.org//drops/20150726/2015072623002487653.com/blob/tdyaaada8nk/opmw_xi87y0cts9q7o4phw?s=uvzhap5mzrbr)

在后面的文章中，我们详细地说明了这些组件。

第一层：ActionDLL（msi.dll）
----------------------

* * *

```
原文件名: msi.dll
MD5: e8eaec1f021a564b82b824af1dbe6c4d
Size: 17’920 bytes
Link时间: 2004.02.12 02:04:50 (GMT)
类型: 64-bit PE32+ executable DLL for MS Windows

```

这个DLL只有一个StartAction导出函数，msiexec.exe进程的上下文会调用这个函数。当这个函数被调用时，这个函数就会获取一个MSI属性-PROP，并用这个值来解密actionData0包。

![enter image description here](http://drops.javaweb.org/uploads/images/3ae50b00f8b77177b01619f3d50506dfd412f226.jpg)

接下来，这段代码会遍历12个需要解密并启动的payload。这些payload是MSI的一部分，可能会包含以下名称：ActionData0, ActionData1, ActionData2。

我们的这个数据包中只包含一个paylioad-“ActionData0”。

第二层：ActionData0
---------------

* * *

主代码会被压缩和加密到这个二进制数据包中。这个二进制的组成包括可执行程序，位置无关代码块，和内嵌的数据对象。这些代码似乎遵循着某种框架，使用了很多辅助结构。辅助结构中包含了一些系统API的指针和内部数据块的偏移量。这些结构能反映出开发者的风格。当代码初始化时，一个字段（一般是前四个字节）中的magic值就会识别结构的状态和类型。

这名编码员还喜欢根据模块和输出名称的哈希来导入系统API。在可执行代码的很多层上都使用了这个哈希算法。通过两个DWORD常量就能识别：0x8A20C27和0x67F84FC6。

一般情况下，ActionData0中的代码会在一个内嵌的可执行程序-“klif.dll”上运行，由这个DLL文件的导出函数表上的第二个函数执行。也就是说，函数名称无所谓，就是要按照函数表上的顺序。当调用这个导出函数时，下一阶段的辅助结构指针就会传递到这个函数上，这样指针就能使用上一层中设置的一些值。

![enter image description here](http://drops.javaweb.org/uploads/images/8620847ea15d37e0a50c12477e6d8c5148116f23.jpg)

但是，在klif.dll执行之前，代码会尝试另一条路径。首先，代码会查找“api-ms-win-shell-XXXX.dll”，其中X可以是任意的十进制数。如果当前进程中没有这种名称形式的模块，名称就是无效的。这样的话，代码就会遍历查找任何符合名称形式的模块，首先从api-ms-win-shell-0000.dll, api-ms-win-shell-0001.dll, api-ms-winshell-0002.dll开始。这应该是Duqu平台组件的一个依赖选项。

在找到名称后，代码会尝试按照名称来映射内核(section kernel object)对象，这些名称是使用PRNG算法生成的。节名称的格式“\BaseNamedObjects{XXXXXXXX-XXXX-XXXX-XXXXXXXXXXXX}”，其中X是根据当前系统的启动时间生成的十六进制数字。到目前为止，节名称都是根据“machine/boot time” 来确定的，这样每个节名称都不一样，但是如果有其他模块的进程也使用了相同的名称生成算法，进程就能定位这样的节。以OSBoot节为例，一旦生成了节名称，代码就会打开节，如果能找到节，代码就会从节中选取几个值，然后尝试打开特定的设备，并把ICTL代码发送到驱动上。驱动设备的名称和IOC代码都在KMART.dll 内的一个节中。

这名编码员非常喜欢用节来访问数据。在映射klif.dll的代码/数据时，还是要用节。另外也可以通过硬编码magic QWORD数: 0xA1B5F8FC0C2E1064来找到这个节。一旦在当前进程的地址空间中找到了节，就由这个节来运行代码。当前的MSI文件数据包并不能应用这种执行路径，但是这种执行路径出现在了代码中，我们猜测这可能是为了使用通用代码模版来创建当前的MSI数据包。当然，这也说明，其他的Duqu平台组件还具有另外的特征。

第三层：klif.dll
------------

* * *

```
Original filename: klif.dll
MD5: 3fde1bbf3330e0bd0952077a390cef72
Size: 196’096 bytes
Link time: 2014.07.06 08:36:50 (GMT)
Type: 64-bit PE32+ executable DLL for MS Windows

```

很显然，这个文件伪装成了卡巴斯基产品的名称-“klif.sys”。虽然代码和文件信息与卡巴斯基产品完全不同，但是，这个模块的导出函数名称使用了卡巴斯基实验室的缩写：KLInit 和KLDone。

当这个DLL加载到一个新进程中时，DLL的内部结构就会初始化，比如给系统API提供指针的结构。

这个模块的payload位于KLDone导出函数上，是导出函数列表上的第二个函数。这个导出函数是从上一层代码中调用的。 首先，模块会确保全局应用结构和关键函数ntdll.dll, kernel32.dll and user32.dll，已经初始化。在调用系统API函数时，需要使用导出函数名称的哈希。哈希算法与前文提到的算法相同，并且也使用了相同的magic常量：0x8A20C27 和0x67F84FC6。

接下来，代码会遍历正在运行的进程列表，并且获取每个进程的小写名称哈希。这个哈希可以是0x3E3021CB 的硬编码值，也就是“avp.exe”字符串的哈希。

攻击 AVP.EXE
----------

* * *

如果“avp.exe”进程正在运行，模块就会尝试打开OSBoot-section，并且尝试攻击avp.exe进程。攻击开始时，首先遍历下列产品的硬编码注册表项和注册表值，来识别卡巴斯基产品的安装路径：

![enter image description here](http://drops.javaweb.org/uploads/images/114d85576da46b2c6724d165638c0a02b85c8117.jpg)

在模块所查询的注册表值中包含了卡巴斯基产品的根目录路径，如“C:\Program Files\KasperskyLab\Kaspersky Internet Security 15.0.0\”

一旦找到了注册表项和注册值，模块就会确认avp.exe是不是在那个路径下面。另外它还会对文件执行一些额外的检查:环境变量的检查,文件能否被读取的检查,是否是一个PE文件的检查.

之后这个模块执行如下动作:1.把avp.exe映射到它内部2.改变内存区域的属性让代码执行3.改变avp.exe内的字符4.使用SSE2 CPU扩展对avp.exe打补丁.

接着，模块会尝试启动一个新的线程，线程的开始位置就是其中一个补丁的位置。到目前为止，新的线程会首先调用avp.exe模块，这个模块会执行其他的一些调用，比如，跳回到klif.dll。很显然，这次攻击是为了让avp.exe相信后续的调用是安全的，相信调用堆栈是来自一个合法的avp.exe模块。继续研究代码，发现：新线程会立刻从avp.exe跳转会klif.dll，并且会尝试与卡巴斯基产品的微过滤器，也就是klif.sys通信。

事实上，在与klif.sys通信之前，新线程会打开OSBoot-section，并获取一个IOCTL代码和驱动设备的名称，然后把这个IOCTL代码发送给设备。这个节和相应的驱动（KMART.dll）会给当前模块提供一定的支持。代码会获取当前进程名称的哈希，并且验证哈希是不是下列三个哈希之一：0x3E3021CB (avp.exe), 0xDE6D4DA0 (msiexec.exe), 0xB915B2D8 (rundll32.exe)。

如果能识别当前进程名称的哈希，模块就会打开\KlifComm微过滤器的通信端口，并且发送一些驱动通信信息，来和klif.sys通信。通过分析这些信息，我们发现这项技术能让klif发现不了进程或线程操作。所有的杀毒产品都会认为这个注册过的项目是受信任的，所以不会扫描其活动，也不会检测或拦截其进程。另外，这个模块会要求卡巴斯基产品的自我防御支持，这个功能是防止木马利用系统技术来杀掉安全产品的进程。这样的话，即使是管理员用户也无法终止模块的进程。

我们测试了卡巴斯基的其他一些产品，结果发现，这些产品都会检查进程的自定义数字签名来验证caller进程。截至目前，如果没有额外的驱动支持，这项技术不会成功。从2010年开始，如果有进程尝试打开\KlifComm微过滤器的通信端口，卡巴斯基的产品就会验证这些进程的数字签名。这种攻击只能影响旧版的卡巴斯基产品，比如在2009年发布的KIS2010。

![ima](http://drops.javaweb.org/uploads/images/714e5745b5c35f2288a71f65ab657542fcf3f80e.jpg)

一般来说，攻击者现在不会攻击卡巴斯基在2009年之前发布的产品。所以，我们有分析了另一种比较合理的解释。

通常来说，这类攻击不会攻击我们的产品，因为我们的产品会检查进程的自定义数字签名，来验证进程的合法性。为了绕过这种检测，Duqu 2.0的一个“KMART.dll”模块给内存中的“klif.sys”打了补丁。因为 “KMART.dll”已经利用Windows内核漏洞在内核模式下运行了，所以这种攻击才能发挥作用。

![enter image description here](http://drops.javaweb.org/uploads/images/714e5745b5c35f2288a71f65ab657542fcf3f80e.jpg)

在发送完代码后，模块会继续下一阶段，也就是进程迁移。

CTwoPENC.dll zero-day and KMART.dll
-----------------------------------

* * *

第三层-klif.dll会执行多个函数，来保证木马能驻进内存，并且绕过杀毒检测。

很重要的一点就是获取内核权限。在64位系统上，如果驱动没有签名，用户就不能加载和运行它。虽然其他攻击者，例如Equation 或 Turla，他们会选择利用第三方签名的驱动，但是Duqu 2.0平台使用的手段要高明很多。

其中一个payload-“CTwoPENC.dll”捆绑了“klif.dll”。这是一个Windows内核漏洞(CVE-2015-2360)。利用这个漏洞，payload就能使用最高权限来运行代码。我们恢复了几个版本的“CTwoPENC.dll”，存在32位和64位版本，编译时间戳如下：

*   2014.08.25 01:20:04 (GMT)
*   2014.08.25 01:19:03 (GMT)
*   2014.07.06 09:17:03 (GMT)

不同于Duqu 2.0的其他模块，这些时间戳看起来都是合法的。至于为什么会这样，我们还不清楚-可能Duqu平台的开发者使用的是其他人编写的模块，而开发者忘了修改编译时间戳。

“CTwoPENC.DLL”是 “win32k.sys” 中存在的一个0-day漏洞，利用这个漏洞，非权限用户也能获取到内核权限。这个模块会利用漏洞来创建窗口，线程的类别名称分别是“CPer”, “Zero”, “CTwo”, “Vero” ，并且模块还能操控回调指针。

![enter image description here](http://drops.javaweb.org/uploads/images/c0b42f83a1ee28994a3028867cfc2d5f85169b65.jpg)

部分漏洞代码会注册窗口类并创建新的窗口

这个漏洞的目的是加载一个“KMART.dll”驱动。如果漏洞攻击成功，“KMART.dll”就会从模块中解压缩，然后在内核模式下发动攻击。“KMART.dll”既有32位也有64位版本。然后，这个驱动会执行一个内核模式攻击，攻击目标就是卡巴斯基产品的过滤器“klif.sys”。“KMART.dll”会给系统API函数-PsGetCurrentProcessId, PsLookupProcessByProcessId的导入表地址打补丁，也会给杀毒驱动-klflt.sys的输出函数KlGetStringRef 打补丁。在函数被拦截之前，恶意代码已经把恶意模块伪装成来自进程/文件“avp.exe”（使用杀毒组件的真实位置），这样就能绕过杀毒软件的监视。

在测试期间，所有的Windows版本(32位和64位的XP, Vista, 7, 8, 8.1)上都受这个漏洞的影响。微软于2015年6月9日修复了这个漏洞。

0x02 PAYLOAD容器和迁移
=================

* * *

payload容器中包含一个短代码节，用于描述目标CPU的架构，payload类型和目标进程的名称或哈希。当模块使用某些内嵌代码或文件时，代码中一般会有两个代码变量：32位和64位。每个payload的运行类型都是根据单一字符来识别。当前模块支持这5种payload 运行类型：g,i,k,l,q。开发者使用的字符按照字母表顺序排列，也就是说，代码中原来可能还有其他的payload类型，只不过被移除了。

**运行类型为“L”的payload**

首先，代码会在其他进程中查找权限。进程句柄是硬编码的，或者是通过查找当前运行进程，获取进程的名称，然后对比已知哈希来获得的。模块中包括下列硬编码进程的哈希： 0x31283314 (services.exe), 0x1026D1BA (lsass.exe), 0x3BD2498C (svchost.exe)。

如果发现了任何识别出的进程，模块就会打开进程标记，并验证下列的权限是否可用：

*   SeDebugPrivilege
*   SeTcbPrivilege
*   SeAssignPrimaryTokenPrivilege
*   SeIncreaseQuotaPrivilege
*   SeImpersonatePrivilege
*   SeRestorePrivilege

如果这些权限可用，模块就会复制进程标记并保存到内部结构中，以便日后使用。

模块在当前系统中，查找一个可用的杀毒软件和一些通用进程。如果什么都没有发现，模块就会尝试查找下列软件的可执行文件：

*   20多个卡巴斯基的产品
*   McAfee VSCore, SystemCore, HIP
*   Symantec Internet Security •
*   Bitdefender
*   ESET •
*   H+BEDV •
*   TrendMicro Network Security Component •
*   Rising AV •
*   Avast •
*   AVG 2012/2013/2014/2015 •
*   F-Secure •
*   Qihoo 360 Security •
*   通用Windows 进程：
*   o %programfiles(x86)%\windows Defender\msmpEng.exe
*   o %systemroot%\syswow64\svchost.exe
*   o %systemroot%\system32\lsass.exe
*   o %systemroot%\system32\svchost.exe

当模块发现了一个这样的可执行程序后，模块会从发现的位置上运行一个新的进程，并使用自己的代码替换当前可执行文件中的可执行代码，代码会经过加密和压缩。

如果代码能从具有安全权限的进程中，找到一个安全标记，代码就会使用CreateProcessAsUser API来创建一个新的进程，在这时，代码就会使用得到的安全标记。否则，代码只会简单地生成一个新的进程。

这个新进程在启动时，处于挂起和调试状态。在新进程启动前，为了简化代码注入和数据操控，子进程的DEP是禁用的。这样，从外表上看，这个进程就像是一个杀毒程序的进程，但是它的内部代码可完全不是合法的模块。

**运行模式为“G”的payload**

这种payload与上面的payload几乎一样，但是这个payload的载入程序更简单-这个Loader不进行hijack和提权步骤。注入进程的选择是自动的，只要是可用进程就可以。

**运行模式为“I”的payload**

这种payload类似于G类 payload，但是它的载入程序在解析payload的标头时有区别：这个载入程序只会选取4个字节来作为进程的哈希，而是不是进程名称字符串。这种方法可能是为了隐藏目标进程的名称，但是，并不是整个模块都应用了这种方法。

**运行模式为“K”的payload**

这种payload会在当前进程的上下文中运行。代码仅仅会复制需要在独立内存中执行的代码，然后在单独的线程中运行这些代码。在线程完成执行后，执行就会被拦截。

**运行模式为“Q”的payload**

这种payload与 Q类 payload一样，但是这种payload不会拦截新线程的执行。目前来看，新代码是异步运行的。

在payload容器打开后，代码就会迁移到另一个进程，安全软件会保护这个进程，这样真正的恶意代码就启动了。在多数情况下，我们称其为后门通道，能监听协调器的通信。在很少的情况下，某些设备上的协调器模块才能与C2通信，这是才可以作为一个双向代理，来提供大量的二级插件。

**插件化模块平台**

除了基本的远程后门，攻击者还在域控制器上和受害者的设备上，部署了更复杂的数据包。这些MSI软件包包括很多模块，各自的作用也不同。

具备完整功能的软件包很大-18MB，基本的远程后门只有500KB。这两者的结构相同，都有ActionDll和加载程序，但是软件还有用于载入和运行的插件。

分析中，我们识别了100多种插件的变种。关于插件的描述如下。我们使用MD5的前两个字节创建了虚拟标识符，来区分插件。

**03B7-Duqu2.0的主要模块，大师手笔**

1.  与cc的通信可以以多种协议进行
2.  可以创建一个自签名证书的中间cc代理程序
3.  可以启动插件框架,加载管理所有的附加插件

可以使用HTTP HTTPS SMB网络管道 或者加密的TCP直连的方式通信.跟2011duqu一样它可以把交互隐藏在Jpeg或者gif图片中通过http的方式来进行.请求名字,url,和user-agent在不同的攻击中可能是不同的.

已知其他变种：3026, 4F11。

**0682 –收集基本系统信息：**

*   当前运行进程的列表
*   活动桌面和终端会话

收集到的信息会通过caller提供的命名管道来传输。

已知其他变种：C0B7

**073C **–在客户端和服务器上应用**完整的Windows Socket传输**。提供工厂类来封装网络函数。

**0872**-当Windows安装程序启动了恶意软件安装包时，**MSI CustomAction library就**会被激活。然后，加载包含payload的加密二进制，接着解密，并在内存中执行。

版本信息中的名称有好几个：**svcmsi_32.dll, msi3_32.dll, MSI.dll, msi4_32.dll。**

加密算法也不同：**Camellia 256, AES, XXTEA。**

从MSI参数中提取出的解密密钥可能是：**PROP,HASHVA, CKEY。**

通过前缀（根据具体情况）来搜索加密的二进制对象：ActionData, CryptHashs, CAData。

已知存在32位和64位版本。其他已知变体：8D7C, 16EF, E6E5,434C, 44BD, F708。

09A0-64位变体，能窃取文件内容。搜索符合下列规则的文件：

*   *.inuse, *.hml
*   包括“data.hmi” 或 “val.dat”的文件名
*   /Int/HMI/ 或/LG/HM/文件夹的文件

![enter image description here](http://drops.javaweb.org/uploads/images/746e729c4974fd3490ed834ed62fdc315e6705ca.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/746e729c4974fd3490ed834ed62fdc315e6705ca.jpg)

```
09A0 插件感兴趣的文件名称和目录名称

```

已知其他变体：8858

0AB8 –提供25个函数，这些函数能操控文件和目录：

*   列出目录下的文件
*   上传或下载任意文件
*   读/写文件内容

在某些情况中，模块会搜索目录-“\int”, “\lg”, “\of\md”, “\tl”, “\ak”，以及扩展名-“.part”, “.manual”, “.inuse”。

![enter image description here](http://drops.javaweb.org/uploads/images/286929998b661fa212a4867167477315521822e0.jpg)

0AB8 插件感兴趣的文件目录名称

其他已知变体：A69E

0B97-网络传输。利用API来连接socket和caller提供的管道。其他变体：56A2。

152B-网络和域发现。

*   枚举域中所有的服务器
*   尝试链接远程注册表并枚举“HKEY_USERS”中所有的用户。然后把用户名转换成SID。
*   枚举所有可见的网络共享

其他已知样本：A987

1C71-把文件数据放到内存中。

2125-网络感染模块。尝试从正在运行的进程中，获取管理凭证。然后使用Windows共享来连接到一个目标设备。接着，恶意DLL后门成功感染设备；目标目录是变化的，可能在UPDROOT$, ADMIN$ 或 C$。使用自定义SMB数据包来识别目标OS的版本。然后使用新创建的服务“svcmsi_32@”，[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)后门通信。其他变体：DB65。除了恶意DLL，模块还会上传一个新的MSI数据包，并且依赖MSIEXEC.EXE 通过新创建的服务“msisvc_32@”来启动MSI，目标MSI的名称是随机生成的，名称模版是“tmp%x.tmp”。

![enter image description here](http://drops.javaweb.org/uploads/images/6594102debafd048a53149b2bf7c0730b0e8975a.jpg)

在被感染时，Windows创建的事件日志（系统）项目

模块通过窃取当前运行进程的token来获取管理凭证。这些进程需要是管理员权限用户启动的。所以，模块首先会直接在域控制器中，查询当前域中的100个管理员用户名。

![enter image description here](http://drops.javaweb.org/uploads/images/b7f8bff44a3c865dee7b7a462eb0116ea0e54c21.jpg)

网络感染模块使用的远程位置

24B7-远程桌面管理。获取屏幕截图，同时可以发送输入到桌面，移动鼠标光标。存在32位和64位版本的变体。其他的已知变体：65BE, 7795, BDC8, DEE2

26D6-检测正在运行的网络嗅探器（wireshark, tcpview, netstat, dumpcap, perfmon)，设置一个TCP服务器，并通过网络管道通信。内部名称：“P.dll。

2829-收集系统信息

*   监控USB设备连接
*   收集USB驱动器的历史记录
*   枚举网络共享，窗口标题，系统路由表
*   读写加密文件

2913-WMI数据收集

*   枚举具有SID的配置文件
*   提取每个配置文件目录下lnk文件的信息
*   通过WMI（CIMV2）来枚举进程，包括已结束进程
*   从可用的远程注册表中提取用户信息

其他已知变体：C776

29D4-模块2125利用服务msisvc_32@; DLL backdoor来感染网络，通过管道“Global{B54E3268-DE1E-4c1e-A667- 2596751403AD}”来接收命令。存在32位和64位变体。

其他已知变体：6F92, A505, D242

2B46-收集系统和用户信息

*   域控制器名称
*   域中的用户列表
*   管理员的域名
*   枚举域信任
*   TCP表
*   UDP表
*   SNMP发现（OS，解析所有的回复）
*   USB驱动器的历史记录，已挂载设备
*   安装的程序
*   时区
*   OS安装日期
*   ODBC.ini,SQL服务器的S instance info,Oracle ALL_HOMES, SyBase, DB2, MS SQL,MySQL 的最后连接
*   DHCP/routing
*   网络配置
*   零配置参数
*   已连接的打印机
*   WinRAR, WinZip, Office使用的MRU列表，IE类URL，已映射的网络设备，Visual Studio MRU
*   终端服务客户端的默认用户名提示
*   用户协助历史记录
*   PuTTY主机密钥和会话
*   已登录用户
*   网络适配器配置
*   VNC客户端密码
*   使用SMB数据包来扫描网络并识别OS

![enter image description here](http://drops.javaweb.org/uploads/images/86828baaed55732f70c852963c5edcdbd568ad74.jpg)

模块收集到的一些注册位置

已知变体：A7F8

2BF7-实用工具DLL。提供基本的API来创建新的MSI数据包，加载并注入任意PE模块。同时负责加载恶意MSI文件中，VFS的第一层。存在32位和64位变体。

已知名称：“ntdll.dll”, “klif.dll”, “apiset.dll”.

其他已知变体：6DA1, 32DB, 8304, 9931, 9E60, A2D4, ABA9, B3BB, DC5F, DD32, F7BB

3395-MS SQL发现模块。这个模块能向网络发送ARP数据包，同时发现MS SQL Server端口。其他函数负责连接额读取远程注册表内容。

35E9-文件系统发现。

*   枚举网络共享
*   枚举本地驱动器
*   遍历文件系统的层级结构并枚举文件；识别重分析点

3F45-管道后门。打开一个新的全局可见的Windows管道，接收并执行加密的命令。“magic”字符串说明加密的协议是“tttttttt”。

*   枚举正在运行的进程
*   加载并执行任意PE文件

存在32位和64位版本。

已知的管道名称：

*   .\pipe{AAFFC4F0-E04B-4C7C-B40A-B45DE971E81E} .\pipe{AB6172ED-8105- 4996-9D2A-597B5F827501}
*   .\pipe{0710880F-3A55-4A2D-AA67-1123384FD859} .\pipe{6C51A4DB-E3DE- 4FEB-86A4-32F7F8E73B99}
*   .\pipe{7F9BCFC0-B36B-45EC-B377-D88597BE5D78}, .\pipe{57D2DE92-CE17- 4A57-BFD7-CD3C6E965C6A}

其他已知变体：6364, 3F8B, 5926, A90A, DDF0, A717, A36F, 8816, E85E, E927

4160-密码窃取程序
-----------

*   提取Google Chrome 和 Firefox的登录数据
*   LSA证书

![enter image description here](http://drops.javaweb.org/uploads/images/41058dcc4606b5e9ccfcc0a85f28e8a4740665d8.jpg)

使用这些数据来定位Chrome保存的登录信息

其他已知 变体：B656

41E2-密码窃取程序。64位模块。提取：
---------------------

*   IE IntelliForms 历史
*   POP3/HTTP/IMAP 密码
*   TightVNC,RealVNC,WinVNC3/4密码
*   Outlook设置
*   SAM,LSASS缓存
*   Windows Live，Net Passport密码

![enter image description here](http://drops.javaweb.org/uploads/images/3867244748181e5c405a782ac7153f02d74f471c.jpg)

```
该模块收集的信息

```

其他已知变体：992E，AF68，D49F

482F-收集系统信息
-----------

*   枚举驱动器
*   获取正在运行进程的列表
*   大范围收集进程信息包括进程运行了多长时间
*   内存信息
*   SID信息

其他已知变体：F3F4

559B-调查Active Directory
-----------------------

*   用ADSI连接Active Directory GC
*   枚举AD中所有对象
*   用人类可读的格式来显示所有条目

![sss](http://drops.javaweb.org/uploads/images/b32d6d8edc9892fa477c1a4005dfd548161b2f6d.jpg)

ActiveDirectory详细路径

580C-收集系统和网络信息
--------------

*   检索域控制器名称
*   枚举域中所有的用户和小组
*   收集计划任务日志
*   收集硬盘信息，可移动硬盘的历史记录
*   检索防火墙策略
*   枚举所有命名系统对象
*   枚举所有系统服务

5B78-收集系统信息及实用工具。
-----------------

它有两个导出函数其中一个的名字是"Getreport"

*   枚举正在运行的进程，提取tokens和SID，收集时间信息
*   explicit credentials 登陆用户
*   以当前进程来模拟用户权限
*   用硬编码模版创建新32位和64位shellcode

存在32位和64位版本。

其他已知变体：E8C7，EE6E

5C66-经过加密的文件I/O，实用工具
--------------------

*   文件I/O操作：打开/查询/读取/编写
*   管理经过压缩和加密的临时文件

622B-生成非常规格式的XML
----------------

*   计算机名称
*   Windows目录
*   枚举所有逻辑驱动器
*   列举所有文件
*   OS序列号
*   域名
*   网络适配器配置：IP地址，MAC，MTU，适配器列表

![enter image description here](http://drops.javaweb.org/uploads/images/da1b3453eb3221c03893a19641c27acfc31481db.jpg)

生成系统报告的XML标签

6302-实用工具。
----------

内部名称“d3dx9_27.dll”。执行基于时间的事件。

其他已知变体：FA84

669D-实用工具。
----------

列举文件名称和目录，检查它们是否存在。

其他已知变体：880B

6914-Sniffer网络攻击。
-----------------

使用合法WinPcap驱动器“npf.sys”。检测NBNS（NetBIOS协议）感兴趣的请求并发送响应

*   响应WPAD请求（NBNS数据包中的“FHFAEBE”）
*   向HTTP GET请求发送响应

网络过滤器基于BPF库。HTTP和WPAD的payload由外部提供.

![enter image description here](http://drops.javaweb.org/uploads/images/92bf20fd3db0c07fbd034dd1414071af2b7ca73b.jpg)

虚假HTTP响应及相关状态信息

6FAC-文件API
----------

*   获取文件大小，属性
*   安全删除文件
*   打开/关闭/读写/文件内容

其他已知变体：A7EE

7BDA-收集系统信息
-----------

*   使用wscapi.dll api的防火墙状态 当前杀毒软件状态
*   检查sqlservr.exe是否运行中
*   计算机名称
*   工作小组信息
*   域控制器名称
*   网络适配器配置
*   时间及时区信息
*   CPU频率

其他已知变体：EF2E

7C23-从文件中提取元数据并收集系统信息
---------------------

*   计算机名称
*   系统卷标序列号
*   完整的文件API，如6FAC中提到的

搜索文件、档案及implements routines中的信息并提取：

*   电子邮件信息：eml,msg
*   图片文件：jpg,jpe,jpeg,tif,tiff,bmp,png
*   多媒体文件：wmv,avi,mpeg,mpg,m4a,mkv,wav,aac,ac3,dv,flac,flv,h264,mov,3gp,3g2,mj2,mp3,mpegts,ogg,asf.上述文件都经libffmpeg重加密。
*   PDF文件内容
*   微软Office:doc,docx,xlsx,pptx.专用路径为：“OfficeRipDoc”,“OfficeRipDocx”,“OfficeRipXlsx”,“OfficeRipPptx”。提取PPT幻灯片，将其转换成HTML摘要
*   档案：gz,gzip,gzX3,zip,rar

创建扩展名为“.fg4”的临时文件。

其他已知变体：EB18，C091

![enter image description here](http://drops.javaweb.org/uploads/images/6dbf7f264311c2b08c720a471385d1b98efa2f67.jpg)

感兴趣的文件扩展名及其对应的状态信息列表

**8172——嗅探攻击。**执行 NBNS（NetBIOS协议）名称解析来欺骗：

*   WPAD请求
*   以“SHR”开头的名字
*   以“3142”（只限日志）开头的名字

![enter image description here](http://drops.javaweb.org/uploads/images/53f6028563513e45919e8866e41633ff5fbf3653.jpg)

附加功能：该组件能够在硬编码模板中新建shellcode blob。

**81B7——驱动程序管理**

*   把驱动程序写入磁盘
*   启动/关闭驱动程序
*   从磁盘中安全删除驱动程序文件

其他已知变体： C1B9

**8446——Oracle DB和ADOdb客户端**

*   使用 “oci.dll” API访问Oracle数据库
*   从数据库中获取所有可用信息
*   还会连接到 ADOdb pviders

![enter image description here](http://drops.javaweb.org/uploads/images/edc4f2921e7bd19b8aa449e89298321db40cf5bd.jpg)

**8912——处理加密文件，收集系统信息**

*   shared file mapping communication
*   将加密数据写入文件
*   枚举窗口
*   枚举网络共享和本地磁盘
*   检索USB设备历史记录
*   收集网络路由表

已知互斥体和映射名：

*   Global{DD0FF599-FA1B-4DED-AC70-C0451F4B98F0} Global{B12F87CA-1EBA- 4365-B90C-E2A1D8911CA9},
*   Global{B03A79AD-BA3A-4BF1-9A59-A9A1C57A3034} Global{6D2104E6-7310- 4A65-9EDD-F06E91747790},
*   Global{DD0FF599-FA1B-4DED-AC70-C0451F4B98F0} Global{B12F87CA-1EBA- 4365-B90C-E2A1D8911CA9}

其他已知变体： D19F, D2EE

**9224——运行控制台应用程序。**使用桌面"default"创建进程,附加到命令行窗口,把i/o重定向到命名管道.

**92DB**——修改cmd.exe shell。

![enter image description here](http://drops.javaweb.org/uploads/images/16e4bca43b7f3cd589a22733eb5565782a0aad9d.jpg)

**9F0D**（64位），**D1A3**（32位）——NPF.SYS这个驱动是伴随着VFS插件一起分发的,它有合法的签名.。它被用来执行嗅探攻击。

**A4B0——网络调查**

*   用DHCP Server Management API (DHCPSAPI.DLL)来枚举所有DHCP服务器的客户端
*   查询所有已知的DHCP子网
*   搜索开放了udp1434 udp137端口的电脑
*   枚举所有网络服务器
*   枚举网络共享
*   尝试连接到远程注册表以枚举HKEY_USERS下的所有用户，将这些用户名转换成SID。

**B6C1 - WNet API。**为WnetAddConnection2和WNetOpenEnum函数提供wrappers

其他已知变体：BC4A

**C25B——嗅探攻击**。运行一个**伪造SMB服务器**来诱骗其他电脑用NTLM进行验证。

*   执行SMB v1命令

![enter image description here](http://drops.javaweb.org/uploads/images/9ed35dc5ba145790f64401bee6931867bcd2da05.jpg)

*   开放虚假ipc$ A:share
*   接受用户身份验证请求
*   处理HTTP “GET /”请求

![enter image description here](http://drops.javaweb.org/uploads/images/5eb9e18ae4655016a0424f3a4c6b91c505f20f7b.jpg)

**ED92——文件系统调查**

*   枚举所有本地驱动器，并连接到网络共享
*   列出文件

**EF97——文件操作动作**

*   枚举文件
*   创建和删除目录
*   复制/移动/删除文件和目录
*   从文件中获取版本信息
*   计算文件的哈希函数

其他已知变体：F71E

0x03 结束语
========

* * *

一般来说,刻画黑客的犯罪过程是一件很困难的事情,duqu2.0尤甚.

duqu除了使用大量的代理来隐蔽自身的犯罪行为外,还额外使用了一些小伎俩:比如它会在代码中植入几个虚假的标记,ugly.gorilla&romanian.antihacker, LZJB算法,前者会让我们错误的认为此次攻击事件是由中国人干的或者这是一次来自罗马尼亚的黑客攻击,后者会让我们错误的认为这个木马来源于miniduke家族.

duqu的攻击具有多地域特征,受害者既有西方国家,也有中东和亚洲国家.关于duqu背后的黑客我们发现了很有趣的一点,那就是他们不仅会盗窃,还会偷方便盗窃用的工具.比如为了投放木马他们在2011年攻击了匈牙利的一家管理数字证书的企业.

duqu2.0的攻击目标和duqu1.0的攻击目标有很多重合的地方.伊朗核设施和一些工控企业始终是他们觊觎的目标.

对一家网络安全公司来说,承认系统被入侵是一件不可想象的事情,但是对卡巴斯基来说不是这样的,因为我们秉承公开透明的原则,基于对用户安全的考量,我们选择公布了此次事件的调查结果.---|||||||||---|||||||||为了用户的信任 我们会战斗到底。