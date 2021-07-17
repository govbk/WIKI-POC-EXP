# 攻击者利用Google Docs传播Trojan.Laziok

攻击者通过 Google Docs 传播 Trojan.Laziok 木马，过程中使用 PowerShell，从 Google Docs 下载木马、绕过反病毒软件

**links:https://www.fireeye.com/blog/threat-research/2016/04/powershell_used_for.html**

0x00 介绍
=======

* * *

通过我们的多流检测技术，我们最近发现了恶意的活动者在通过Google Docs传播Trojan.Laziok恶意软件。我们发现攻击者试图在2016年三月份把payload上传到Google docs上去。在它存活的短短的时间内，从IE（从第3到第11版本）接触到恶意页面的用户可能会在没有任何安全警告的情况下被动的成为恶意payload的主机。在我们向谷歌警示这个恶意程序存在之后，谷歌快速的清除了这个恶意程序和原始的URL，传播的情况也被遏制住了。

0x01 Payload
============

* * *

这个Trojan.Laziok恶意软件充当一个攻击者用来收集他们所要攻击的系统的信息的侦察工具。它之前在针对能源领域的网络间谍活动中被发现过，尤其是在中东地区[[1]](http://www.symantec.com/connect/blogs/new-reconnaissance-threat-trojanlaziok-targets-energy-sector)。在那些活动中，这个恶意软件是通过带有恶意附件的垃圾邮件来传播的，而这些恶意的附件利用的主要是CVE-2012-0158漏洞。

本文的这个例子中提到的传播恶意软件的技术涉及到了利用用户运行的支持VBScirpt的IE的方面。

0x02 Attack Delivery Point
==========================

* * *

攻击者在波兰域名的主机地址存放了攻击的第一阶段。正如下图所示，第一阶段通过从这个主机地址运行混淆后的JavaScript代码来启动攻击。

![](http://drops.javaweb.org/uploads/images/0e05efb1e3801e71afe6e34ea6b39ab6d30022e2.jpg)

图1 response中的被混淆的代码

一旦被解码，JavaScript代码就会打开并通过VBScript在IE（从第3到第11版本）内运行的时候执行CVE-2014-6332漏洞，利用windows OLE的内存崩溃漏洞来自动化的bypass操作系统安全设施以及其他的保护措施，这样就会确保攻击者进入“上帝”模式。CVE-2014-6332的使用，以及被滥用的“上帝”模式，早在2014年底就借助一个已知的PoC[[2]](http://blog.trendmicro.com/trendlabs-security-intelligence/a-killer-combo-critical-vulnerability-and-godmode-exploitation-on-cve-2014-6332/)作为一个组合技被使用，如下图所示：

![](http://drops.javaweb.org/uploads/images/e336accceadb4e7f5ead1a4ce6dadd6b639be361.jpg)

图2a CVE-2014-6332的使用

![](http://drops.javaweb.org/uploads/images/122fc8708412e5faa7a3de6e99181e64dcec39c1.jpg)

图2b 在“上帝模式”改变了安全模式标志之后的runmumaa()函数调用。

接下来，runmumaa()函数会通过PowerShell从Google Docs上下载恶意的payload。PowerShell是通过DownloadFile和ShellExcute命令来下载恶意软件并在定义好的%APPDATA%环境变量路径内执行的。所有的VBScript指令和PowerShell脚本都作为被混淆的脚本的一部分，在document.write(unescape)中，如图1所示。

PowerShell在bypass反病毒软件方面也很有用，因为它可以直接在内存中注入payloads。我们之前讨论过俄罗斯的活跃的数据窃取活动[[3]](https://www.fireeye.com/blog/threat-research/2015/12/uncovering_activepower.html)。看起来这个技术在牵涉到恶意程序的时候仍然很流行，并且这个技术可以逃避Google Docs的安全检查。这个payload会从Google Docs上下载链接——如图3中去混淆后的代码所示——最终会从上述的波兰网站上获取活动的恶意软件。

![](http://drops.javaweb.org/uploads/images/cc8c43bc0b6f7fea1d85b1535f4a0ed2145778e1.jpg)

图3 使用Powershell获得在Google Docs链接上的payload

0x03 Payload细节
==============

* * *

被下载下来的payload是恶意程序Trojan.Laziok，它的回调函数和以下的数据可以作为证明：

```
00406471 PUSH 21279964.00414EED ASCII "open"
0040649C MOV EDX,21279964.004166A8 ASCII "idcontact.php?COMPUTER="
004064B1 MOV EDX,21279964.00415D6D ASCII "&steam="
004064D2 MOV EDX,21279964.00416D96 ASCII "&origin="
004064F3 MOV EDX,21279964.00416659 ASCII "&webnavig="
00406514 MOV EDX,21279964.00416B17 ASCII "&java="
00406535 MOV EDX,21279964.00415601 ASCII "&net="
00406556 MOV EDX,21279964.00414F76 ASCII "&memoireRAMbytes="
0040656B MOV EDX,21279964.0041628C ASCII "&diskhard="
0040658E MOV EDX,21279964.00414277 ASCII "&avname="
004065AF MOV EDX,21279964.00416BFC ASCII "&parefire="
004065D0 MOV EDX,21279964.0041474A ASCII "&install="
004065E5 MOV EDX,21279964.00414E12 ASCII "&gpu="
00406606 MOV EDX,21279964.004164B7 ASCII "&cpu="
00406659 MOV EDX,21279964.004170F9 ASCII "bkill.php"
004066B9 MOV EDX,21279964.00415B79 ASCII "0000025C00000C6B000008BB000006ED0000088900000453000004CE0000054100000B75"
004066ED MOV EDX,21279964.004149CD ASCII "install_info.php"
00406735 MOV EDX,21279964.00415951 ASCII "pinginfo.php"
00406772 MOV EDX,21279964.00416B6B ASCII "get.php?IP="
00406787 MOV EDX,21279964.0041463F ASCII "&COMPUTER="
0040679C MOV EDX,21279964.00416DF5 ASCII "&OS="
004067B1 MOV EDX,21279964.00415CB8 ASCII "&COUNTRY="
004067C6 MOV EDX,21279964.00416069 ASCII "&HWID="
004067DB MOV EDX,21279964.00414740 ASCII "&INSTALL="
004067F0 MOV EDX,21279964.00415BE3 ASCII "&PING="
00406805 MOV EDX,21279964.004158E2 ASCII "&INSTAL="
0040681A MOV EDX,21279964.00414D3E ASCII "&V="
0040682F MOV EDX,21279964.00414E5D ASCII "&Arch="
00406872 MOV EDX,21279964.00414166 ASCII "post.php"
00406899 MOV EDX,21279964.00414EB0 ASCII "*0"

```

上面的Payload的指令一旦被解压，就会突出Trojan.Laziok的显著特性。**这个恶意程序试图收集关于计算机名称、CPU细节、RAM大小、位置（国家）以及安装的软件和防病毒程序**的信息。我们的MVX引擎也显示这个恶意程序尝试访问流行的防病毒软件的文件，比如Kaspersky、McAfee、Symantec以及Bitdefender的安装文件。它同时也通过把自己copy到已知的文件夹和进程中来进行混淆，比如：

`C:\Documents and Settings\admin\Application Data\System\Oracle\smss.exe`

这个Payload也尝试回调到一个著名的做坏事的波兰服务器：http://193.189.117.36。

我们在2016年3月份发现了这种攻击的第一个例子。这个恶意软件知道我们通知了Google它的存在之后才被Google清理掉。用户在一般情况下并不能从Google Docs上下载到恶意的内容，因为Google做了一些主动扫描并且对恶意内容作了过滤。然而这个样本在Google Docs上是存在的并且是可以下载的，这也证明它绕过了Google的安全检查。在接到我们的通知以后，Google迅速的清除掉了恶意的文件，这个恶意的文件也再也不能被获取到了。

0x04 结论
=======

* * *

FireEye的多流检测技术捕获了这次活动的所有细节，从入口点到回调哈数，并且这个恶意软件不能bypass FireEye沙箱的安全措施。PowerShell的数据窃取活动也被观察到通过带有嵌入宏命令的文件进行传播，所以企业环境需要格外的重视使用PowerShell的政策和规定。

1.  http://www.symantec.com/connect/blogs/new-reconnaissance-threat-trojanlazioktargets- energy-sector
2.  http://blog.trendmicro.com/trendlabs-security-intelligence/a-killer-combocritical- vulnerability-and-godmode-exploitation-on-cve-2014-6332/
3.  https://www.fireeye.com/blog/threatresearch/2015/12/uncovering_activepower.html