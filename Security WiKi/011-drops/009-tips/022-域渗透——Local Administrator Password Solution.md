# 域渗透——Local Administrator Password Solution

0x00 前言
=======

* * *

在域渗透中，有关域内主机的本地管理员的安全介绍还很少，对于LAPS大都比较陌生，所以这次就和我一起学习一下吧。

![这里写图片描述](http://drops.javaweb.org/uploads/images/443f6ec43cc938ded38bfca4a5848cc913214c94.jpg)

0x01 简介
=======

* * *

在实际的域环境中，域内主机的本地管理员账户往往被忽视，再加上统一的配置，域内主机的本地管理员密码往往相同，这就带来了一个问题，如果获得一台域内主机的本地管理员密码，其他域内主机的本地管理员密码自然就知道了，解决这个问题最好的办法就是确保每台域内主机有不同的密码，并且定期更换。

所以微软在今年3月1号发布了LAPS（Local Administrator Password Solution）协议。

0x02 学习目标
=========

* * *

站在渗透的角度，在研究之初设立了以下目标：

```
>     1、如果域内主机本地管理员账户密码相同，如何利用？
>     2、LAPS是如何配置使用的？
>     3、如果安装了LAPS,有没有利用方法？

```

**注**：

```
对于问题1，如果账户权限配置不当，可以利用pass-the-hash尝试获取其他域内主机权限，mimikatz的操作命令之前有介绍，本文不做重点介绍，暂时忽略。
链接：
http://drops.wooyun.org/tips/7547

```

0x03 测试环境
=========

* * *

```
域控：server 2008 r2 x64
域内主机： win7 x64

```

0x04 配置LAPS
===========

* * *

1、安装LAPS
--------

**域控：**

**-1）下载LAPS**

[https://www.microsoft.com/en-us/download/details.aspx?id=46899](https://www.microsoft.com/en-us/download/details.aspx?id=46899)

**-2）安装**

选择全部功能

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/cfe4bc0509671adea7a17e94e544fd1926d3b97b.jpg)

**域内主机：**

下载安装，方法同上

**_Tips:_**

```
域内主机批量安装可使用组策略安装的方法
参考链接如下：
https://4sysops.com/archives/install-32-bit-and-64-bit-applications-with-group-policy-and-sccm/

```

2、域控LAPS配置
----------

对于这部分可以理解为域的配置以LDAP（Lightweight Directory Access Protocol）协议存储，现在需要添加两个属性来存储LAPS信息：

```
ms-MCS-AdmPwd：存储密码
ms-MCS-AdmPwdExpirationTime：存储过期时间

```

我们可以打开`C:\Program Files\LAPS\AdmPwd.Utils`看到LAPS的安装配置：

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/9fd3f7b74da7b8a7ac55322a9ea98b9094d4035e.jpg)

**-1）在域控上执行以下Powershell命令（需要使用域管权限登录）**

```
import-module AdmPwd.PS
Get-Command -Module AdmPwd.PS
Update-AdmPwdADSchema

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/ee380a34f98ce8785fad30019447112f82cd4557.jpg)

**注**：

```
server2008 默认Powershell 版本2.0
执行import-module AdmPwd.PS会出现如下错误：
下载powershell3.0,安装后重启再次执行即可

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/c02ef6846ecfaa819ca747a144fe9ef0c129efb9.jpg)

**-2）配置活动目录权限**

**（1）**查看可以访问存储密码的用户组：

powershell执行：

```
import-module AdmPwd.PS
Find-AdmPwdExtendedRights -OrgUnit "CN=Computers,DC=test,DC=local"

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/182db32e1e4c1462bdd486c668b7412bc8ab2abe.jpg)

**（2）**取消用户组访问存储密码的权限：

打开ADSIEdit.msc，右键连接，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/7fea9f3195c7ffd5bbadb4d3799d15e048da8d01.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/4f43a83557a35ea9039da08c547cb785f2819a42.jpg)

选择对应的组，右键-属性，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/a96dd1915303797349d13663bf25f980993fde0a.jpg)

选择安全-高级，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/f5c2df9c39cb9da71307c32ee43acc0310af3642.jpg)

选中取消权限的用户-编辑-勾中拒绝所有扩展权限，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/625cba29cc0ef8b21d136df01ca7d3094528c63f.jpg)

**（3）**增加用户组读取和重置存储密码的权限：

powershell执行：

```
import-module AdmPwd.PS
Set-AdmPwdReadPasswordPermission -OrgUnit "CN=Computers,DC=test,DC=local" -AllowedPrincipals test\administrator
Set-AdmPwdResetPasswordPermission -OrgUnit "CN=Computers,DC=test,DC=local" -AllowedPrincipals test\administrator

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/b1c15b1ccd291245cf26cef14f5cfe096e534772.jpg)

**（4）**为域内主机添加可以更新密码的权限：

```
import-module AdmPwd.PS
Set-AdmPwdComputerSelfPermission -OrgUnit "CN=Computers,DC=test,DC=local"

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/d4f2422e4aa97331e5631ad92f731c7ef247e72e.jpg)

**-3）配置LAPS密码组策略**

gpedit.msc-管理模板-LAPS，设置对应的密码策略

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/54712ce6e95a261335beb494e2ab8479cc0c12a5.jpg)

0x05 查看LAPS存储的密码
================

* * *

共有以下三种方法

1、属性编辑器
-------

打开Active Directory 用户和计算机

查看-选中高级功能，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/b32d314a3c45f9adb896eaf24f240075681137f9.jpg)

选中对应计算机-右键-属性-属性编辑器-找到

```
ms-Mcs-AdmPwd：存储密码
ms-Mcs-AdmPwdExpirationTime：存储过期时间

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/832e56041262ec4b326d7f1b988559abd92de75a.jpg)

2、LAPS UI
---------

安装LAPS时可以选择安装LAPS UI,启动后输入计算机名，查询，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e43eed4e9f39488c199069dfb16e9ea50d3b703d.jpg)

3、Powershell
------------

**（1）**查询某主机

```
Import-Module AdmPwd.PS 
Get-AdmPwdPassword –ComputerName testf

```

或者

```
Get-ADComputer testf -Properties ms-Mcs-AdmPwd | select name, ms-Mcs-AdmPwd

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e02be31b929c3c65af46b24985b1bbecfc31523d.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/dfdd3058fa22bab328aa9977854aa2bd682ad5f1.jpg)

**（2）**查询所有主机

```
function Get-LAPSPasswords
{

    [CmdletBinding()]
    Param(
        [Parameter(Mandatory=$false,
        HelpMessage="Credentials to use when connecting to a Domain Controller.")]
        [System.Management.Automation.PSCredential]
        [System.Management.Automation.Credential()]$Credential = [System.Management.Automation.PSCredential]::Empty,

        [Parameter(Mandatory=$false,
        HelpMessage="Domain controller for Domain and Site that you want to query against.")]
        [string]$DomainController,

        [Parameter(Mandatory=$false,
        HelpMessage="Maximum number of Objects to pull from AD, limit is 1,000.")]
        [int]$Limit = 1000,

        [Parameter(Mandatory=$false,
        HelpMessage="scope of a search as either a base, one-level, or subtree search, default is subtree.")]
        [ValidateSet("Subtree","OneLevel","Base")]
        [string]$SearchScope = "Subtree",

        [Parameter(Mandatory=$false,
        HelpMessage="Distinguished Name Path to limit search to.")]

        [string]$SearchDN
    )
    Begin
    {
        if ($DomainController -and $Credential.GetNetworkCredential().Password)
        {
            $objDomain = New-Object System.DirectoryServices.DirectoryEntry "LDAP://$($DomainController)", $Credential.UserName,$Credential.GetNetworkCredential().Password
            $objSearcher = New-Object System.DirectoryServices.DirectorySearcher $objDomain
        }
        else
        {
            $objDomain = [ADSI]""  
            $objSearcher = New-Object System.DirectoryServices.DirectorySearcher $objDomain
        }
    }

    Process
    {
        # Status user
        Write-Verbose "[*] Grabbing computer accounts from Active Directory..."

        # Create data table for hostnames, and passwords from LDAP
        $TableAdsComputers = New-Object System.Data.DataTable 
        $TableAdsComputers.Columns.Add('Hostname') | Out-Null
        $TableAdsComputers.Columns.Add('Stored') | Out-Null
        $TableAdsComputers.Columns.Add('Readable') | Out-Null
        $TableAdsComputers.Columns.Add('Password') | Out-Null
        $TableAdsComputers.Columns.Add('Expiration') | Out-Null

        # ------------------------------------------------
        # Grab computer account information from Active Directory via LDAP
        # ------------------------------------------------
        $CompFilter = "(&(objectCategory=Computer))"
        $ObjSearcher.PageSize = $Limit
        $ObjSearcher.Filter = $CompFilter
        $ObjSearcher.SearchScope = "Subtree"

        if ($SearchDN)
        {
            $objSearcher.SearchDN = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$($SearchDN)")
        }

        $ObjSearcher.FindAll() | ForEach-Object {

            # Setup fields
            $CurrentHost = $($_.properties['dnshostname'])
            $CurrentUac = $($_.properties['useraccountcontrol'])
            $CurrentPassword = $($_.properties['ms-MCS-AdmPwd'])
            if ($_.properties['ms-MCS-AdmPwdExpirationTime'] -ge 0){$CurrentExpiration = $([datetime]::FromFileTime([convert]::ToInt64($_.properties['ms-MCS-AdmPwdExpirationTime'],10)))}
            else{$CurrentExpiration = "NA"}

            $PasswordAvailable = 0
            $PasswordStored = 1

            $CurrentUacBin = [convert]::ToString($CurrentUac,2)

            # Check the 2nd to last value to determine if its disabled
            $DisableOffset = $CurrentUacBin.Length - 2
            $CurrentDisabled = $CurrentUacBin.Substring($DisableOffset,1)

            # Set flag if stored password is not available
            if ($CurrentExpiration -eq "NA"){$PasswordStored = 0}


            if ($CurrentPassword.length -ge 1){$PasswordAvailable = 1}


            # Add computer to list if it's enabled
            if ($CurrentDisabled  -eq 0){
                # Add domain computer to data table
                $TableAdsComputers.Rows.Add($CurrentHost,$PasswordStored,$PasswordAvailable,$CurrentPassword, $CurrentExpiration) | Out-Null
            }

            # Display results
            $TableAdsComputers | Sort-Object {$_.Hostname} -Descending
         }
    }
    End
    {
    }
}
Get-LAPSPasswords -DomainController 192.168.40.132 -Credential test.local\Administrator | Format-Table -AutoSize

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/ac4f3d1a7a3ccaf680efe677373b1798b344e3b7.jpg)

**注：**

```
如果配置不当，我们可以在域内一台普通主机，查看域内其他主机本地管理员账号

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/7a47bab8a9b527b358e607ccf4ef3a9267b7dc61.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/91f3cd501ee58182c10f731507d18166113cac36.jpg)

0x06 防御
=======

* * *

1、如果未使用LAPS
-----------

一定要留意域内主机的本地管理员账号

对于域内本地管理员尝试pass-the-hash虽未做详细介绍，但如果满足条件，操作简单、威力无穷

2、使用LAPS
--------

**（1）**注意用户权限配置是否存在问题，是否普通用户可以读取域内其他主机的本地管理员密码  
**（2）**为了便于管理域内主机本地管理员账号，一般大规模的域都会使用LAPS  
这种情况下在安装程序列表里面会出现Local Administrator Password Solution  
**（3）**如果域控被入侵过，记得更新所有LAPS配置

0x07 小结
=======

* * *

在域渗透中，对域内主机的本地管理员的尝试利用，往往会有出其不意的效果。 我们知道，LAPS是在LDAP中存储，那么LDAP在域渗透中有多大作用呢？值得研究。

参考资料：

*   [https://technet.microsoft.com/library/security/3062591](https://technet.microsoft.com/library/security/3062591)
*   [https://support.microsoft.com/en-us/kb/3062591](https://support.microsoft.com/en-us/kb/3062591)
*   [https://github.com/kfosaaen/Get-LAPSPasswords](https://github.com/kfosaaen/Get-LAPSPasswords)
*   [https://www.praetorian.com/blog/microsofts-local-administrator-password-solution-laps](https://www.praetorian.com/blog/microsofts-local-administrator-password-solution-laps)
*   [https://flamingkeys.com/2015/05/deploying-the-local-administrator-password-solution-part-1/](https://flamingkeys.com/2015/05/deploying-the-local-administrator-password-solution-part-1/)
*   [https://4sysops.com/archives/introduction-to-microsoft-laps-local-administrator-password-solution/](https://4sysops.com/archives/introduction-to-microsoft-laps-local-administrator-password-solution/)
*   [https://blog.netspi.com/running-laps-around-cleartext-passwords/](https://blog.netspi.com/running-laps-around-cleartext-passwords/)
*   [https://adsecurity.org/?p=501](https://adsecurity.org/?p=501)

本文由三好学生原创并首发于乌云drops，转载请注明