# Powershell tricks::Powershell Remoting

0x01 简介
-------

* * *

Powershell Remoting建立在windows WinRM服务之上，可以一对一或一对多远程控制，也可以建立HTTP 或 HTTPS的“listeners”，使用WS-MAM协议接收远程传递的命令。

Windows 远程管理(WinRM)是 WS-Management 协议的 Microsoft 实现，该协议为使用 Web 服务的本地计算机和远程计算机之间的通信提供了一种安全的方式。 也就是说在WS-MAN协议基础上，客户端运行环境可以多样化。 比如[openwsman](https://github.com/Openwsman/openwsman)。

![enter image description here](http://drops.javaweb.org/uploads/images/d128a7364fd5adb95c880f5888274a64860d7bd3.jpg)

图片来源：v3 Secrets of PowerShell Remoting

0x02 远程管理
---------

* * *

Powershell Remoting在windows server 2008以前默认是不开启的，需要通过administrator用户执行Enable-PSRemoting命令开启。

![enter image description here](http://drops.javaweb.org/uploads/images/0c88e1c81ee0fed6487f307c93362f45094c359f.jpg)

在windows server 2012中，Powershell Remoting默认开启。

在windows下，powershell默认使用winrm进行远程管理，winrm版本不同默认的监听端口也不同。如下：

> The default ports for winrm 1.1 are http port 80 and https port 443
> 
> The default ports for winrm 2.x are http port 5985 and https port 5986

可以在参考[这里](http://technet.microsoft.com/en-us/library/ff520073(WS.10).aspx)判断winrm版本。

通过`Enable-PSRemoting`命令打开PS远程，默认是启动了Kerberos认证。这个方法只适合两台电脑在相同域或信任域内的指定电脑（名字可以带后缀）.但它不支持跨域、域外或IP地址。

如果要跨域、或指定IP地址执行时我们可以在客户端这里执行下面的代码，需要将所有或单一远程主机添加在信任表中。

```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value * -Force

```

删除所有远程信任主机

```
Clear-Item WSMan:\localhost\Client\TrustedHosts

```

如果要删除单一远程主机，则可以执行：

```
$newvalue = ((Get-ChildItem WSMan:\localhost\Client\TrustedHosts).Value).Replace("computer01,","")
Set-Item WSMan:\localhost\Client\TrustedHosts $newvalue

```

更改computer01。

列出所有远程信任主机

```
Get-Item WSMan:\localhost\Client\TrustedHosts

```

在使用远程执行时如果只提供用户名，那么则会弹窗输入密码。此时我们可以建立PSCredential对象将用户名和密码保存在里面。然后再传递给`-Credential`参数。`-ScriptBlock`参数后跟要执行的代码。

```
$UserName = "admin3"
$serverpass = "admin123!@"

$Password = ConvertTo-SecureString $serverpass -AsPlainText –Force
$cred = New-Object System.Management.Automation.PSCredential($UserName,$Password)

invoke-command -ComputerName localhost -Credential $cred -ScriptBlock { ipconfig }

```

![enter image description here](http://drops.javaweb.org/uploads/images/923244f7c9c2d191ddec75dbc28ea8873528d717.jpg)

使用`help * -Parameter computername`命令可以列出所有默认可以远程使用的命令。并且认证过程都可以像上面的代码一样传递$cred。

之后写个for循环就可以一对多的执行了。

![enter image description here](http://drops.javaweb.org/uploads/images/1b62fed0321bbb2974bf03184bea4870da3d29ce.jpg)

如果输出内容过于冗杂，还可以使用`ConvertTo-Csv`或者`ConvertTo-Html`将powershell对象的输出转换为html或者csv。

如果想一对一获取交互式powershell，可以像这样执行`Enter-PSSession`：

```
Enter-PSSession -ComputerName 192.168.200.161 -Credential $cred

```

![enter image description here](http://drops.javaweb.org/uploads/images/7546b825e97b0294c8079a8456651c56b5281e9c.jpg)

0x03 多任务分发
----------

* * *

在使用`invoke-command`的时候，`computername`可为多个参数。在执行的时候可以使用`-Asjob`参数将执行过程放在后台。 接收回显的时候可以使用`get-job`查看`job id`，然后用`receive-job`接收全部回显结果。 但是如果我只是想查看某个远程主机的执行结果呢？ 那么就可以像下面这样做：

```
Get-Job -Id 1 | select -ExpandProperty childjobs

```

得到`child job id`之后，再用`receive-job`接收回显结果。

![enter image description here](http://drops.javaweb.org/uploads/images/683959b017684b26f9149d217e14a68eaf85c825.jpg)

0x04 域内信息搜集
-----------

* * *

基本的信息搜集(日志、进程、服务等)可以靠上面列出的命令来收集，但是远程执行`invoke-command`是需要凭证的，如果是在域内我们是不是可以先用`nltest`搜集下信任域？

在windows中有个`System.DirectoryServices.ActiveDirectory`命名空间，和windows域有关。 其下有个类Domain，其中`GetAllTrustRelationships()`方法可以获得信任域。

那么在powershell就可以这样执行：

```
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).GetAllTrustRelationships()

```

获得域之前的信任关系。 如果需要自行开发脚本，也可以参考下面的文档。

除此之外，还记得之前metasploit笔记中那个`local_admin_search`模块吗？`veil-powerview`中也有通过相同的方式实现了这一过程。

两种不同的脚本都通过调用OpenSCManagerA API连接远程主机测试是否成功。

![enter image description here](http://drops.javaweb.org/uploads/images/7caedc3ad89886666f4a5e72f803c3107f52e89d.jpg)

Local_admin_search.rb

![enter image description here](http://drops.javaweb.org/uploads/images/2f82c6d972c103831f97a4eee3c06de386b95420.jpg)

Invoke-CheckLocalAdminAccess

附[veil-powerview作者博客中](http://www.harmj0y.net/blog/penetesting/finding-local-admin-with-the-veil-framework/)的测试截图：

![enter image description here](http://drops.javaweb.org/uploads/images/7c1735d22cc06778cabc085820c9ec4ed331f6e3.jpg)

0x05 参考
-------

* * *

*   [http://www.harmj0y.net/blog/redteaming/trusts-you-might-have-missed/](http://www.harmj0y.net/blog/redteaming/trusts-you-might-have-missed/)
*   [http://msdn.microsoft.com/en-us/library/system.directoryservices.activedirectory.domain(v=vs.110).aspx](http://msdn.microsoft.com/en-us/library/system.directoryservices.activedirectory.domain(v=vs.110).aspx)
    
*   [https://www.blackhat.com/docs/us-14/materials/arsenal/us-14-Schroeder-The-Veil-Framework-Slides.pdf](https://www.blackhat.com/docs/us-14/materials/arsenal/us-14-Schroeder-The-Veil-Framework-Slides.pdf)
    
*   [https://www.blackhat.com/docs/us-14/materials/arsenal/us-14-Schroeder-The-Veil-Framework-Slides.pdf](https://www.blackhat.com/docs/us-14/materials/arsenal/us-14-Schroeder-The-Veil-Framework-Slides.pdf)
    
*   [v3 Secrets of PowerShell Remoting.pdf](http://powershell.org/wp/2012/08/06/ebook-secrets-of-powershell-remoting/)
    

0x06 powershell pentest project 学习推荐
------------------------------------

* * *

整理的过程发现了很多牛人的博客和项目，在这里分享一下。

**Powershell HID attack toolkit**：[https://github.com/samratashok/Kautilya](https://github.com/samratashok/Kautilya)

**post exploitation**：[https://github.com/samratashok/nishang](https://github.com/samratashok/nishang)

**Remote DLL inject**：[https://github.com/clymb3r](https://github.com/clymb3r)

**aspx的Powershell webshell**：[https://github.com/samratashok/nishang/tree/master/Antak- WebShell](https://github.com/samratashok/nishang/tree/master/Antak-WebShell)

**Veil Post exploitation**：[https://github.com/Veil-Framework/Veil-PowerView](https://github.com/Veil-Framework/Veil-PowerView)

**A PowerShell Post-Exploitation Framework**：[https://github.com/mattifestation/PowerSploit](https://github.com/mattifestation/PowerSploit)

**local privilege escalation**:[https://github.com/HarmJ0y/PowerUp](https://github.com/HarmJ0y/PowerUp)