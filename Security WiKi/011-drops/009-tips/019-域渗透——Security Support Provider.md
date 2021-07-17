# 域渗透——Security Support Provider

0x00 前言
=======

* * *

在之前的文章中介绍了一些域环境中的渗透方法和技巧，所以这次接着介绍一个用来维持域控权限的方法——SSP.

![Alt text](http://drops.javaweb.org/uploads/images/376d1de312b12de24e2269d065ba6894ccb545e4.jpg)

0x01 简介
=======

* * *

**SSP：**

Security Support Provider，直译为安全支持提供者，又名Security Package.

简单的理解为SSP就是一个DLL，用来实现身份认证，例如：

```
NTLM
Kerberos
Negotiate
Secure Channel (Schannel)
Digest
Credential (CredSSP)

```

**SSPI：**

Security Support Provider Interface，直译为安全支持提供程序接口，是Windows系统在执行认证操作所使用的API。

简单的理解为SSPI是SSP的API接口

**LSA：**

Local Security Authority，用于身份认证，常见进程为lsass.exe

特别的地方在于LSA是可扩展的，在系统启动的时候SSP会被加载到进程lsass.exe中.

这相当于我们可以自定义一个dll，在系统启动的时候被加载到进程lsass.exe！

![Alt text](http://drops.javaweb.org/uploads/images/bfea4fc7e262e4f9acb95447d4b5cfd018d63d74.jpg)

此图片来自于https://dl.mandiant.com/EE/library/MIRcon2014/MIRcon_2014_IR_Track_Analysis_of_Malicious_SSP.pdf

如图，这是正常的SSPI结构图，Client APP是我们自定义的dll，通过Secur32.dll可以调用 "`credential capture API`"来获取LSA的信息

![Alt text](http://drops.javaweb.org/uploads/images/034aa8380a54d60e229e6a73a66fffbf74be0d0f.jpg)

此图片来自于https://dl.mandiant.com/EE/library/MIRcon2014/MIRcon_2014_IR_Track_Analysis_of_Malicious_SSP.pdf

上图展示了攻击思路，既然可以自定义dll,那么我们就可以定制dll的功能，通过`Named Pipe`和`Shared Memory`直接获取`lsass.exe`中的明文密码，并且能够在其更改密码时立即获得新密码！

0x02 mimilib SSP
================

* * *

mimikatz早已支持这个功能，而这个文件就是我们使用的时候常常忽略的mimilib.dll

![Alt text](http://drops.javaweb.org/uploads/images/6beca4935f489db0fbc12cbc03ad3bc2ff9fe626.jpg)

下面就实际测试一下如何通过mimilib伪造SSP记录明文密码.

**mimikatz poc地址：**  
[https://github.com/gentilkiwi/mimikatz/blob/bb371c2acba397b4006a6cddc0f9ce2b5958017b/mimilib/kssp.c](https://github.com/gentilkiwi/mimikatz/blob/bb371c2acba397b4006a6cddc0f9ce2b5958017b/mimilib/kssp.c)

0x03 实际测试
=========

* * *

**测试环境**

```
域控：server 2008 r2 x64
域内主机： win7 x64

```

**测试步骤：**

### 1、添加SSP

将mimilib.dll复制到域控`c:\windows\system32`下

> **注：**
> 
> 64位系统要用64位的mimilib.dll，32位的会失败

### 2、设置SSP

修改域控注册表位置：

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa\Security Packages\

```

如图![Alt text](http://drops.javaweb.org/uploads/images/758325ec1166eab6e7903573c484fd59b2140fcb.jpg)

在Security Packages下添加mimilib.dll

如图![Alt text](http://drops.javaweb.org/uploads/images/6d7ff324f89a81cf349844514023986d94b6f868.jpg)

点击确认，Security Packages已被添加mimilib.dll

如图![Alt text](http://drops.javaweb.org/uploads/images/fd4edb79635c31ef4d0147db03211764cc2fbcd1.jpg)

### 3、重启系统

域控重启后在`c:\windows\system32`可看到新生成的文件kiwissp.log

如图![Alt text](http://drops.javaweb.org/uploads/images/0d73cd7e03bca290f393ca1696b6696c1e11fd8c.jpg)

kiwissp.log记录了登录账户和密码，如图![Alt text](http://drops.javaweb.org/uploads/images/fcb7603c2fd7ff85d4fea286ae132a16e5239782.jpg)

> **Tips：**
> 
> mimilib只实现了将密码保存到本地，如果把密码发送到远程服务器岂不是威力无穷？

0x04 补充
=======

* * *

### 1、Memory Updating of SSPs

mimikatz同时还支持通过内存更新ssp，这样就不需要重启再获取账户信息

需要使用mimikatz.exe，命令如下：

```
privilege::debug
misc::memssp

```

**注：**

**1、**64系统需要64位的mimikatz，如图

32位mimikatz失败![Alt text](http://drops.javaweb.org/uploads/images/2034fd6feb1f73b5cf9b3994a33e8b305251df4f.jpg)

64位mimikatz成功![Alt text](http://drops.javaweb.org/uploads/images/e29043cc4597f4d76888ee7bcf4711ac05247880.jpg)

**2、**内存更新的方法在重启后会失效.

0x05 检测
=======

* * *

### 1、注册表

检测注册表位置：

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa\Security Packages\

```

### 2、dll

检测`%windir%\System32`是否有可疑dll

### 3、Autoruns

使用工具Autoruns检测LSA

如图，可以发现添加dll的位置![Alt text](http://drops.javaweb.org/uploads/images/68370d3b9e7423c3f2c2524bf46d828f17a0fc62.jpg)

0x06 小结
=======

* * *

本文仅对SSP的常规用法做了演示，实现了在本地保存域控的账户和密码，而且基于这个思路，可以开发出更多高级的利用方法。

如果站在防御的角度，常规方法已经力不从心，只有更多的了解攻击才能更好的防御。

0x07 参考资料
=========

* * *

*   [https://en.wikipedia.org/wiki/Security_Support_Provider_Interface](https://en.wikipedia.org/wiki/Security_Support_Provider_Interface)
*   [https://dl.mandiant.com/EE/library/MIRcon2014/MIRcon_2014_IR_Track_Analysis_of_Malicious_SSP.pdf](https://dl.mandiant.com/EE/library/MIRcon2014/MIRcon_2014_IR_Track_Analysis_of_Malicious_SSP.pdf)
*   [https://msdn.microsoft.com/en-us/library/bb742535.aspx](https://msdn.microsoft.com/en-us/library/bb742535.aspx)
*   [https://msdn.microsoft.com/en-us/library/windows/desktop/ms721625(v=vs.85).aspx#_security_security_support_provider_gly](https://msdn.microsoft.com/en-us/library/windows/desktop/ms721625(v=vs.85).aspx#_security_security_support_provider_gly)
*   [https://adsecurity.org/?p=1760](https://adsecurity.org/?p=1760)
*   [https://technet.microsoft.com/en-us/library/dn408187.aspx](https://technet.microsoft.com/en-us/library/dn408187.aspx)

**本文由三好学生原创并首发于乌云drops，转载请注明**