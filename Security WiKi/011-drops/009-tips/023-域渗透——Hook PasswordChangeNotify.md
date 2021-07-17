# 域渗透——Hook PasswordChangeNotify

0x00 前言
=======

* * *

在之前的文章中介绍了两种维持域控权限的方法——`SSP`和`Skeleton Key`，这两种方法均需要借助Mimikatz来实现，或多或少存在一些不足，所以这次接着介绍一个更加隐蔽且不需要使用Mimikatz的后门方法——`Hook PasswordChangeNotify`.

![Alt text](http://drops.javaweb.org/uploads/images/4d171de776e949e8c085b6dfb7345daae46c924d.jpg)

0x01 简介
=======

* * *

Hook PasswordChangeNotify这个概念最早是在2013年9月15日由clymb3r提出，通过Hook PasswordChangeNotify拦截修改的帐户密码。

需要了解的相关背景知识如下：

1.  在修改域控密码时会进行如下同步操作：
    
    a. 当修改域控密码时，LSA首先调用PasswordFileter来判断新密码是否符合密码复杂度要求 b. 如果符合，LSA接着调用PasswordChangeNotify在系统上同步更新密码
    
2.  函数PasswordChangeNotify存在于rassfm.dll
    
3.  rassfm.dll可理解为Remote Access Subauthentication dll，只存在于在Server系统下，xp、win7、win8等均不存在
    
4.  可以使用dumpbin查看rassfm.dll导出函数来验证结论2：
    
    ```
    dumpbin /exports c:\windows\system32\rassfm.dll
    
    ```

如图![Alt text](http://drops.javaweb.org/uploads/images/1cc024d7693aa688650edde7f3c7a6b818ca8219.jpg)

0x02 特点
=======

* * *

对于之前介绍过的Security Support Provider，在实际使用过程中不可避免的会有以下不足：

1.  安装后需要重启系统
2.  需要在System32文件夹下放置dll
3.  需要修改注册表

而使用Hook PasswordChangeNotify却有如下优点：

1.  不需要重启
2.  不需要修改注册表
3.  甚至不需要在系统放置dll

可以说在隐蔽性上，使用Hook PasswordChangeNotify优于Security Support Provider

0x03 技术实现
=========

* * *

根据clymb3r提供的poc，实现Hook PasswordChangeNotify共包含两部分：

### 1、Hook dll

下载链接：  
[https://github.com/clymb3r/Misc-Windows-Hacking](https://github.com/clymb3r/Misc-Windows-Hacking)  
**（1）**为PasswordChangeNotify创建一个inline Hook，将初始函数重定向到PasswordChangeNotifyHook  
**（2）**在PasswordChangeNotifyHook中实现记录密码的操作，然后重新将控制权交给PasswordChangeNotify

### 2、dll注入

可以利用 Powershell tricks中的Process Injection将我们自己编写的dll注入到lsass进程，实现Hook功能

0x04 实际测试
=========

* * *

**测试环境：**

```
Server 2008 R2 x64
Server 2012 R2 x64

```

**测试步骤：**

### 1、生成Hook dll

poc下载地址：  
[https://github.com/clymb3r/Misc-Windows-Hacking](https://github.com/clymb3r/Misc-Windows-Hacking)

使用VS2015开发环境，MFC设置为在静态库中使用MFC  
编译工程，生成HookPasswordChange.dll

![Alt text](http://drops.javaweb.org/uploads/images/5b3ee1af421ee2fc3cf83160837ed3fc525c25f1.jpg)

### 2、生成dll注入的powershell脚本

下载Powershell的dll注入脚本  
[https://github.com/clymb3r/PowerShell/blob/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1](https://github.com/clymb3r/PowerShell/blob/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1)

在代码尾部添加如下代码：

`Invoke-ReflectivePEInjection -PEPath HookPasswordChange.dll –procname lsass`

并命名为HookPasswordChangeNotify.ps1

### 3、Hook PasswordChangeNotify

上传HookPasswordChangeNotify.ps1和HookPasswordChange.dll

管理员权限执行：

```
PowerShell.exe -ExecutionPolicy Bypass -File HookPasswordChangeNotify.ps1

```

如图![Alt text](http://drops.javaweb.org/uploads/images/9e3d205f9ec85608b18092700e2864d0a94e2f7a.jpg)

### 4、自动记录新密码

在Server 2012 R2 x64下，手动修改域控密码后  
在C:\Windows\Temp下可以找到passwords.txt，其中记录了新修改的密码

如图![Alt text](http://drops.javaweb.org/uploads/images/a96efddb6911b2b98383d09526c74cfaeddc7ec1.jpg)

在Server 2008 R2 x64下，同样成功

如图![Alt text](http://drops.javaweb.org/uploads/images/692d75de19ee524fc09d5bdc3e0e56681ef64f37.jpg)

0x05 小结
=======

* * *

本文依旧是对常规功能做了演示，后续可自定义dll代码实现更多高级功能，如自动上传新密码。

以下链接中的代码可作为参考，其中实现了将获取的新密码上传至Http服务器

[http://carnal0wnage.attackresearch.com/2013/09/stealing-passwords-every-time-they.html](http://carnal0wnage.attackresearch.com/2013/09/stealing-passwords-every-time-they.html)

使用Hook PasswordChangeNotify来记录新密码，如果放在以前，进程注入的操作很容易被检测，但是得益于Powershell应用的发展，通过Powershell来进程注入可以绕过常规的拦截。

当然，Hook PasswordChangeNotify仅仅是众多Hook方法中的一个。

我已经Fork了clymb3r的代码，并结合本文需要的代码做了更新，下载地址如下：

[https://github.com/3gstudent/Hook-PasswordChangeNotify](https://github.com/3gstudent/Hook-PasswordChangeNotify)

0x06 参考资料
=========

* * *

*   [https://clymb3r.wordpress.com/2013/09/15/intercepting-password-changes-with-function-hooking/](https://clymb3r.wordpress.com/2013/09/15/intercepting-password-changes-with-function-hooking/)
*   [http://carnal0wnage.attackresearch.com/2013/09/stealing-passwords-every-time-they.html](http://carnal0wnage.attackresearch.com/2013/09/stealing-passwords-every-time-they.html)
*   [http://www.processlibrary.com/en/directory/files/rassfm/305529/](http://www.processlibrary.com/en/directory/files/rassfm/305529/)
*   [https://github.com/clymb3r/Misc-Windows-Hacking/tree/master/HookPasswordChange](https://github.com/clymb3r/Misc-Windows-Hacking/tree/master/HookPasswordChange)
*   [http://www.slideshare.net/nFrontSecurity/how-do-password-filters-work](http://www.slideshare.net/nFrontSecurity/how-do-password-filters-work)

**本文由三好学生原创并首发于乌云drops，转载请注明**