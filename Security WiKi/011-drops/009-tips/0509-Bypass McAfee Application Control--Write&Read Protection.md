# Bypass McAfee Application Control--Write&Read Protection

0x00 前言
=======

* * *

上篇我们成功在McAfee Application Control保护的系统上实现了代码执行，而McAfee Application Control的其他保护功能同样很强大，其中对文件读写操作的拦截很有特色，这一次我们接着试试能不能绕过：D

![这里写图片描述](http://drops.javaweb.org/uploads/images/c08612de2e8eb491b30984a0ddd1a2de637b34c7.jpg)

0x01 简介
=======

* * *

当McAfee Application Control开启了文件写入保护和读取保护，可以阻止任何对受保护文件的修改，具体保护细节如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/c289468ae955fdb3606046cba5e46fcfca551657.jpg)

简单的说，如果开启了写入保护，那么对文件的任何修改操作都会被阻止并被日志记录。

如果开启了读取保护，那么无法读取受保护文件的内容。

可是深入了解之后，有趣的事情发生了。

0x02 配置Write Protection
=======================

* * *

操作系统：`win7x86`

首先学习一下如何设置以及使用文件写入保护。

写入保护可以指定文件夹、文件或者是驱动文件

测试使用指定文件夹`c：\test\write`

里面包含`test.txt`

### 1.指定保护路径

```
sadmin write-protect -i c:\test\write

```

### 2.查看保护路径

```
sadmin write-protect -l

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/43fa1a6a3b2dd9417866a0f54f59ecd0e53767c1.jpg)

随后我们尝试`在c：\test\write`下新建文件、删除文件、修改文件，均失败

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/f6b357224fae8b531f8d2ad039dae2dce8300eda.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/7365f66ed741a71654f8558c7a2006ec41a6c91e.jpg)

### 3.删除保护路径

```
sadmin write-protect -r c:\test\write

```

0x03 配置Read Protection
======================

* * *

接着测试读取保护

测试使用指定文件夹`c：\test\read`

下面包含`test.txt`，里面保存有加密信息

> 注：  
> 写入保护默认开启，而读取保护默认关闭，所以先要开启读取保护功能

### 1.开启读取保护功能

```
sadmin features enable deny-read

```

### 2.指定读取保护路径：

```
sadmin read-protect –i c:\test\read

```

### 3.查看读取保护路径：

```
sadmin read-protect -l

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/3ca7066ee73889c41728bd195b2d38f3e1d65563.jpg)

尝试读取文件内容，失败，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/6134bcb9b7a11de0bcf50781e7e4accd62c13d96.jpg)

0x04 权限分配漏洞
===========

* * *

通过以上的测试可以发现：

*   写入保护阻止用户对文件进行写入操作
*   读取保护阻止用户对文件进行读取操作

但是:

McAfee Application Control会默认设定白名单进程用来为系统进行更新

所以这些进程都具有操作文件的权限

如果你仔细阅读了上一篇文章并能加以思考

那么其中的漏洞也显而易见

**如果能够利用白名单进程执行文件读写操作，那么自然能够绕过防护**

0x05 漏洞利用
=========

* * *

**利用思路：**

*   查找默认白名单进程
*   找到可利用进程
*   使用进程注入
*   操作文件

### 1.查看白名单进程列表

执行

```
sadmin updaters list

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/a63eb06b60cb1cbb4a2e027e1589f9d70d5ca9fe.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/1b6320600f42f98c44cefa59d58cef8e6ac67473.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/294c452b87d276edbc9131805a5f222ea8a5af2d.jpg)

### 2.找到可被利用进程

以下是我找到的比较通用并能被利用的进程：

*   GoogleUpdate.exe
*   scsrvc.exe
*   spoolsv.exe

### 3.进程注入

选取`GoogleUpdate.exe`

使用《Powershell tricks::Code Execution & Process Injection》提到的Process Injection-Meterpreter.ps1

可以在powershell的环境下粘贴代码执行

向GoogleUpdate.exe进程注入meterpreter

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/2bb41615cf0c4bb0f8194004116fa18c19f81418.jpg)

> 注：  
> 注入系统权限的进程需要管理员权限

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/1a8b8c114fb57f6dc5e33fa8ec32313434338fbe.jpg)

弹回meterpreter

发现没有直接注入到GoogleUpdate.exe

接着进程注入，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/3c5b77af98f4503d5edbb2628fc080d2543f06d2.jpg)

成功注入到GoogleUpdate.exe，理论上已经有了权限可以操作受保护的文件

我们接着测试，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/665ac2064a9890d98a868bc1b0ac0ad87b94ced3.jpg)

成功修改文件和删除文件

接着测试读取文件，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/ecba780e2d885655b337e26b50ba85c6667ebe37.jpg)

成功读取被保护的内容

> 注： 通过进程注入获得的权限可以用来执行脚本

0x06 补充
=======

* * *

### 1.设置密码

McAfee Application Control可对操作设置密码，增强其安全

设置密码：

```
sadmin passwd 

```

去掉密码：

```
sadmin passwd -d

```

密码文件保存在`C:\Program Files\McAfee\Solidcore\passwd`

### 2.获取密码文件

正常情况下`C:\Program Files\McAfee\Solidcore\passwd`无法被读取、无法被复制，即使进程注入到白名单进程内也无法实现，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/ee7cbc087b78f747d26ac5ee726341b02d53c768.jpg)

但是我们依然有办法：D

这里可以借鉴导出域控ntds.dit文件的方法，使用`NinjaCopy.ps1`

下载链接：  
[https://github.com/3gstudent/NinjaCopy](https://github.com/3gstudent/NinjaCopy)

指定路径为：

```
Invoke-NinjaCopy -Path "C:\Program Files\McAfee\Solidcore\passwd" -LocalDestination "C:\test\trust\passwd"

```

管理员权限运行`NinjaCopy.ps1`，成功复制passwd文件

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/bcc7b579b78ebdba95c08959501ae2561fc60cae.jpg)

### 3.解析密码文件

![这里写图片描述](http://drops.javaweb.org/uploads/images/f9a9303e285029571692a71394995a0d9ad93176.jpg)上图为passwd的内容

查看资料得知此处使用的是sha-512加密（mcafee-application-control-product-guide/Page68）

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/a19bf86f72a92112759bca794a91a005a7443669.jpg)

推断`cryptographic salt`为`88daf0b4-790e-4eae-a926-b08788fbd1cb`

在[http://www.convertstring.com/Hash/SHA512](http://www.convertstring.com/Hash/SHA512)验证推断

输入`cryptographic salt`和明文对比测试

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/29c8940db031e0437a7a5733861149b1bc19d4ef.jpg)

passwd中的内容和我们自己加密的密文相同，判断正确

### 4.信任路径

McAfee Application Control为方便使用，可以指定信任路径，在里面的所有操作均不会被拦截

如果McAfee Application Control未设置密码或者密码被获得，可以建立一个信任路径，里面的操作均不会被拦截

建立：

```
sadmin trusted -i c:\test\trusted

```

查看：

```
sadmin trusted -l

```

如图程序成功执行![这里写图片描述](http://drops.javaweb.org/uploads/images/df7cb6b781bc425f0283ed143248c89e946e8ed7.jpg)

### 5.日志

日志默认被保存在`C:\ProgramData\McAfee\Solidcore\Logs`

通过进程注入获得的权限可以修改此文件

### 6.防护建议

*   为McAfee Application Control设置强密码
*   禁用powershell
*   禁用hta、js
*   禁用信任路径
*   白名单+黑名单结合使用

0x07 小结
=======

* * *

“未知攻 焉知防”，即使做到以上几点，我相信依然有绕过的方法：）

本文由三好学生原创并首发于乌云drops，转载请注明