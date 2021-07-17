# 管中窥豹---分析一个只抓中国肉鸡的DDOS团伙

source：https://blog.malwarebytes.org/intelligence/2015/06/unusual-exploit-kit-targets-chinese-users-part-2/

最近，我们的研究人员发现了一个非常奇怪的exploit kit正在攻击中国的域名。在上一篇[文章](https://blog.malwarebytes.org/exploits-2/2015/05/unusual-exploit-kit-targets-chinese-users-part-1/)中，我们详细地讨论了这个exploit kit的运作方式，包括其感染途径，payload可执行文件，以及这个攻击工具检测到奇虎360会停止攻击。

在这篇文章中，我们会讨论这个exploit kit的木马。在VirusTotal 上，有很多关于这个木马的查杀记录。我们的研究员把这个木马命名为 “Trojan.Chinad” 或"Chinad"。

Chinad的木马文件:

notepad.exe (MD5:[5a454c795eccf94bf6213fcc4ee65e6d](https://www.virustotal.com/en/file/cfb94506f4816034410ecd86a378b9f29b912ecb68c88c8ae0bcad748968cb6c/analysis/1430987954/))

pic.jpg (MD5:[4e8639378d7a302c7474b5e4406dd7b4](https://www.virustotal.com/en/file/94f5481684cfc05b68f56ec53e6730de27fc1e9b0c3bebaf10d22f293cf154fa/analysis/1431552695/))

image.png (MD5:[55c447191d9566c7442e25c4caf0d2fe](https://www.virustotal.com/en/file/5b7e022f5009004985b34cf091d06752c765a25b445a46050eef51a17be8267d/analysis/1432196740/))

5003.tmp (MD5:[d6ce4b6db8407ca80193ede96d812bb7](https://www.virustotal.com/en/file/7127ea6a185af63fc77fa2a7f87605d981a15c90277eaa3e9899d333e2e108e2/analysis/1434028210/)) – 真实名称, “Module_UacBypass.dll”

**Notepad.exe (Chinad)**

摘要

Notepad.exe ("Chinad") 是一个bot客户端。 这个二进制文件和image.png是 Chinad 木马的两个主要组成部分。

Chinad bot首先会请求远程服务器，然后根据接收到的命令在受害者的计算机上执行任务。虽然这个bot的主要目的是DDoS攻击，但是bot也能向自身注入任意shellcode。

Chinad木马的植入方式：CVE-2014-6332利用成功以后用FTP下载的方式植入

技术分析

可执行文件使用了UPX壳来减小体积，以便提升网络传输的效率。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502395974953.com/blob/iabaaasiisv/koecfnjqn_ewhdv7-i_x6a?s=lrclaxxs1dly)

UPX压缩的是一个纯净的Microsoft Visual C++可执行程序。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502400039395.com/blob/iabaaasiisv/wl_e_llplfxg0lsm2upoza?s=lrclaxxs1dly)

Chinad 首先会创建一个硬编码名称为"Global\3672a9586a5f342b2ca070851e425db6″的互斥量。接着，如果木马发现用户具有管理员权限，木马就会复制到System文件夹；否则，木马就复制到Appdata文件夹：

```
%windir%\System\Init\wininit.exe ("C:\Windows" being a typical value for %windir%) %appdata%\Microsoft\System\wininit.exe ("C:\Users\\Roaming" being a typical value for %appdata%)

```

木马的维持方法:注册表启动项或者schtask.exe .比如:

```
C:\Windows\system32\schtasks.exe /create /F /sc onstart /tn Microsoft\Windows\Shell\Init /tr \C:\Windows\System\Init\wininit.exe\ /ru system

```

通过这样的操作，Chinad就能以系统权限启动，并且获取到系统的最高权限。

在与木马服务器通信之前，Chinad首先会通过联系 www.baidu.com来测试网络连接是否畅通。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502400383539.com/blob/iabaaasiisv/2_rawiwestycopwveqljxg?s=lrclaxxs1dly)

如果没有网络连接，Chinad就会进入休眠模式;否则，木马就会继续从服务器上获取命令。

**_接收命令_**木马通过获取远程服务器 (默认的硬编码 IP 地址) 上的"bootstrap.min.css"文件，来获取需要执行的命令。下图中就是一个请求。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502400410562.com/blob/iabaaasiisv/wnajs6ujyomyr-2yzkgriw?s=lrclaxxs1dly)

但是，在Chinad 读取命令之前，Chinad首先需要解密从CC上取得的文件。这个文件的加密算法是Salsa20.你可以通过反编译工具的字符串参考搜索”expand 32-byte k”来识别这个算法.

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502400588757.com/blob/iabaaasiisv/elfg1ea4bhgchk5eg8u2cw?s=lrclaxxs1dly)

Chinad 可以接受的命令包括:

**update**-存储当前的cnc到一个加密文件，并报告给服务器。然后，下载并执行最新版的木马，接着删除旧版木马。_syntax_:,,,,;

**cnc**- 指定cnc服务器的位置，木马会联系这个服务器来获取命令_syntax_:,;

**cnc_reset**- 重置CNC服务器地址为默认值._syntax_:;

**report**- 指定报告服务器的地址._syntax_:,;

**report_reset**- 重置报告服务器的地址为默认值._syntax_:;

**attack**- 利用生成的数据，通过TCP或UDP socket来攻击目标IP._syntax_:,<udp|tcp>,,,,;

**attack_reset**- 重置攻击目标的地址_syntax_:;

**url_exec**- 从指定的URL上下载文件，并使用WinExec来执行这个文件_ssyntax_:,,;**shellcode_exec**- 创建一个挂起进程，并把shellcode注入到这个进程然后，恢复进程。_ssyntax_:,;

通常情况下， Chinad从C2服务器上获取到的第一条命令是 “update”。这个命令中包含一个URL, Chinad会从这个URL上下载最新的木马二进制文件。在这个例子中，下载到的是image.png，一个更强大的bot版本。

木马使用了分号来分割每条命令，诸如C语言等现代的编程语言都使用了这种语法。这样就能在同一时间发出多条命令。比如接下来发出的命令“attack_reset”。下面就是一个完整的命令:

```
timestamp,1431270567; update,http:///image.png?13572v44,44,1,5b7e022f5009004985b34cf091d06752c765a25b445a46050eef51a17be8267d; attack_reset;

```

关键字“timestamp”实际上并不是一个命令。但是在这个关键字中的一个值是一个十进制格式的[FILETIME](https://msdn.microsoft.com/en-us/library/windows/desktop/ms724284%28v=vs.85%29.aspx)结构，这个值对应着系统时间。这样的话，木马就只能在攻击者规定的时间中执行命令，并且攻击者也能控制木马的生命周期。

在接收到update命令后，Chinad 首先会把当前的配置信息储存到一个使用Salsa20加密的文件中，然后才会更新木马。如果用户具有管理员权限，这个文件会存储在:

```
%windir%\Logs\WMI\Event\SystemEvent.evt

```

如果用户没有管理员权限，这个文件会存储在:

```
%appdata%\Microsoft\System\wow64.dll

```

更新完成后，木马在第一次执行时会打开这个文件，然后解密文件中的内容来恢复C2服务器和报告服务器的最后已知地址。

**_报告信息_**

Chinad的另一个功能就是发送报告信息，但是我们现在还不清楚木马这样做的目的。 Chinad 首先会调用[GetAdaptersInfo](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365917%28v=vs.85%29.aspx)来检索关于受害者电脑上网络适配器的信息，比如名称和 IP 地址信息。 接下来，木马会通过算法来生成一个特殊值。

在写这篇文章的时候，我们尚不能确定这个值的含义。另外，报告服务器总是会响应请求“AAA”。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502400730279.com/blob/iabaaasiisv/69b95rnqo2iqjp7sswnbiq?s=lrclaxxs1dly)

一种可能的解释是，我们的 Chinad 的样本已经"过期了"(无效的时间戳值)，所以说报告函数不能正常运行。当然也有可能是在分析期间，报告服务器不能正常使用了。

不管怎么说，请求中的值一定包含有特殊的含义，而只有报告服务器能理解这些值的含义。如果能找到更多信息，我们会更新这一部分。

**_攻击目标_**

我们前面提到过，Chinad 可以接收攻击命令。根据这些命令，Chinad就能攻击指定的 IP 地址。 攻击方式一般是TCP或UCP socket。这就是分布式拒绝服务攻击，也是我们所说的[DDoS](http://en.wikipedia.org/wiki/Denial-of-service_attack)攻击。

![enter link description here](http://static.wooyun.org//drops/20150625/2015062502400935627.com/blob/iabaaasiisv/i-o3uujbprctvtys-jpm2a?s=lrclaxxs1dly)

一旦创建了攻击线程，Chinad 会不断地向目标发送数据。在指定的时间内发送完数据后，China就会进入休眠模式。

在接收到另一个攻击命令（attack）或攻击重置命令（attack_reset）之前，Chinad会一直攻击目标。下面就是Chinad通过UDP socket发送给目标的数据

![enter link description here](http://static.wooyun.org//drops/20150625/2015062502401132885.com/blob/iabaaasiisv/al0r72l2w7lnsrvlymlnuw?s=lrclaxxs1dly)

为了生成这些数据，Chinad会使用CRT函数__getptd来获取线程的数据块（tiddata）地址。然后，木马会破坏返回的数据。接着再把数据发送给用户。

**Pic.jpg**

摘要

我们在之前的博客中提到过， Chinad 木马是利用Flash 和 Java 中存在的漏洞安装的。

Pic.jpg 是一个 Dll文件，需要一个载体(loader)来运行,这个载体可以是浏览器也可以是java.与Chinad木马的其他组件一样，pic.jpg大概是起到一个下载者的作用, 它会下载image.png。而image.png是执行bot的主要程序.。其实现方式有很多，其中一种就是再次利用受害者电脑上的漏洞。

技术分析

从外表上看，pic.jpg 平淡无奇。 这个文件没有使用混淆处理，也没有其他导出函数。

![enter link description here](http://static.wooyun.org//drops/20150625/2015062502401310431.com/blob/iabaaasiisv/9rcr7oonhfvpp_cnp_ms3g?s=lrclaxxs1dly)

首先，pic.jpg 会简单地检查磁盘上loader进程的完整路径。例如，如果是浏览器的Flash组件存在漏洞，那么loader的位置可能就在 C:\Program Files (x86)\Internet Explorer\iexplore.exe，因为这是Microsoft IE浏览器的标准路径。Pic.jpg 会在loader的路径中查找下列字符串:

```
\java \iexplore.exe \mshtml.dll (检查是不是加载到内存中) \chrome.exe \firefox.exe \safari.exe \opera.exe

```

如果 pic.jpg 没有在loader进程中发现任何上述的字符串，pic.jpg就会认定自己在被分析，而终止运行。这样在某些情况下，pic.jpg 就能绕过沙盒等自动分析系统。

Pic.jpg 然后会将尝试攻击 TS WebProxy组件的一个漏洞[cve-2015-0016](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-0016)。通过利用这个权限提升漏洞( Trend Micro对此进行了详细的说明，点击[这里查看](http://blog.trendmicro.com/trendlabs-security-intelligence/cve-2015-0016-escaping-the-internet-explorer-sandbox/)) ，攻击者就能启动任意进程。 在获取到最高权限后，pic.jpg 就能在隐藏的窗口中执行 powershell 命令。下面是powershell命令的参数，首先解压缩的是一个base64编码的gzip文档。接下来就会执行这个文档中的一个脚本（在变量 $s上）。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502401491014.com/blob/iabaaasiisv/1-yrcvyany9cdb2rfmu4rw?s=lrclaxxs1dly)

在这个脚本中包含有shellcode（同样是base64编码）。而这个shellcode会在新内存 (VirtualAlloc) 中作为一个线程执行。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502401676476.com/blob/iabaaasiisv/xcgb6dqc7p-lpeok26hczw?s=lrclaxxs1dly)

shellcode在执行时，会获取远程服务器上的 image.png，然后把文件的名称更改为desktop.ini.exe，并执行。

如果攻击TS WebProxy漏洞没有生效，pic.jpg 仍然会尝试从远程服务器上下载image.png 。一般是直接使用[UrlDownloadToFile](https://msdn.microsoft.com/en-us/library/ms775123%28v=vs.85%29.aspx)下载，或者是通过Temp 目录中的一个Visual Basic 脚本来完成。

**Image.png (受保护的Chinad)**

摘要

这个Chinad木马在成功利用漏洞微软IE浏览器漏洞 CVE-2014-6332 (https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-6332)后，通过FTP安装。

Image.png 是 Chinad bot 的另一个变体，它的功能与notepad.exe 几乎完全相同。但是，Image.png有几个额外的功能，并且具有更强的反分析能力。

技术分析

不同于 notepad.exe，攻击者使用了[Themida](http://www.oreans.com/themida.php)（Oreans的一个产品）来保护image.png。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502401995259.com/blob/iabaaasiisv/uvdalpsrmcvsctmonhwgcq?s=lrclaxxs1dly)

Themida 很强大，它具备很多功能，比如可以检测被加壳的木马是否在虚拟机执行,是否正在受病毒分析员的分析.

此外，Themida 还提供了不同的 (可变) 保护代码。如果启用了不同的功能，保护代码也都不同。这样就再次加大脱壳的难度.

有趣的是，攻击者只混淆处理了image.png，而没有混淆notepad.exe。notepad.exe和image.png从本质上来说是相同的bot，但是要想分析前者就容易很多。

这两者的主要区别在于：image.png在从C2服务器上获取命令之前，会首先在用户的 Temp 目录中投放一个特殊的DLL文件。

这个Dll文件的真正名称是"Module_UacBypass.dll"(这是一个临时文件) ，它的作用是维持木马，并绕过非XP系统上的用户UAC。我们在下图中详细的说明了这个DLL文件。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502402143584.com/blob/iabaaasiisv/0xcue6vguuincndnznryfw?s=lrclaxxs1dly)

除此之外，image.png和notepad.exe并没有别的明显区别了。notepad.exe同样具备所有的功能及其相关的二进制文件。随着 bot 版本的开发，bot还会以受保护的形式安装，也可能仍然会使用 Themida。

**5003.tmp ("Module_UacBypass.dll")**

摘要

一个受保护的Chinad bot (image.png)曾经使用过模块Module_UacBypass.dll ("Uac_bypass.dll") 。这个模块的主要目的是在Windows Vista及更高版本的系统上维持木马。但是这个模块使用的木马维持方法很特殊，包括劫持一个Windows SQL server Dll 来绕过UAC。

技术分析

Uac_Bypass.dll 具有两个导出函数，Func1 和 Func2；以及一些有趣的字符串，包括 Dll 文件的真实名称"Module_UacBypass.dll"。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502402358584.com/blob/iabaaasiisv/m7sbt8qrgvcur9p_ziwxmq?s=lrclaxxs1dly)

有意思的是，作者把“Module”设置为了文件名称的前缀，也就是说Chinad bot还计划有很多模块，有的甚至已经投入使用了。

Uac_Bypass.dll 主要针对非管理员用户来创建Chinad bot的维持机制(对管理员用户来说，使用schtasks.exe方法来维持bot；参考下面的notepad.exe分析）。这个模块也会绕过 UAC。UAC是 Windows Vista 中新增的一种安全功能，能阻止恶意程序在系统上执行。由于Windows XP 上没有UAC功能，所以这个 Dll 不会在XP系统上执行。

首先，Uac_bypass.dll 会把自己复制到临时目录，并把文件名称修改为NTWDBLIB.dll，然后再把文件添加到cabinet archieve。NTWDBLIB.dll 是Microsoft SQL server使用的一个库文件。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502402423669.com/blob/iabaaasiisv/fv8ehw58f2cjry5waau2ug?s=lrclaxxs1dly)

这样做的主要目的是为了利用这个cabinet和wusa.exe 来更新NTWDBLIB.dll （由Uac_Bypass.dll假冒的） ，从而劫持 Dll 。Wusa.exe 是Windows Update Standalone Installer，这样就能通过提供一个cabinet来启用Windows update。

![enter image description here](http://static.wooyun.org//drops/20150625/2015062502402663282.com/blob/iabaaasiisv/vyrwwngfi2vyrwv_stogdq?s=lrclaxxs1dly)

Uac_Bypass.dll 还会写入一个特殊的注册表项:

```
HKCU\Software\Microsoft\Windows NT\CurrentVersion\UacCompat

```

这个键值中包含有Chinad bot的路径。

然后，Uac_Bypass.dll 执行 cliconfig.exe，把新的恶意 NTWDBLIB.dll 加载到内存中，并指向 DllMain 函数。

![enter link description here](http://static.wooyun.org//drops/20150625/2015062502402829426.com/blob/iabaaasiisv/3m3kjajulc1rs9n85n49mg?s=lrclaxxs1dly)

在DllMain中，Uac_Bypass.dll 会检查字符串"\cliconfig.dll"是否在正调用进程列表。如果是，Uac_Bypass.dll就会获取上述注册表项中的Chinad bot路径，并使用 CreateProcess (https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425%28v=vs.85%29.aspx)来运行 Chinad bot。

我们在 先前的文章中 (http://www.greyhathacker.net/?p=796)讨论过这种绕过方法。在2013年的时候，有木马率先使用了这种技术。

**结论**

很显然,chinad就是一个利用中国的受害者来执行DDOS攻击的一个木马.

到目前为止,我们只发现在中国的域名上被植入了exp程序.Exploit kit的ip则分布于马来西亚,新加坡.

我们的研究团队尚未在亚洲之外的区域发现Chinad。

从诸如使用baidu.com和qq.con来测试网络连接性的行为来看，几乎可以肯定这个bot就是只活跃在亚洲的.

但是，Chinad bot并没有使用任何革命性的技术，我们也认为 Chinad bot 还不够成熟，同时木马作者还犯了很多错误。比如，没有对-notepad.exe加壳，也留下许多可作为分析线索的字符串，包括"Module_UacBypass.dll"的名称（明文）。

根据上述的原因，我们推测Chinad木马的作者既非经验丰富的专业人士，也不像是由国家授意的间谍组织.到底这个木马后续发展会是怎样,让我们一起拭目以待吧.