# powershell操作注册表权限

```bash
Get-Acl            

```

*查看键的当前权限*

```bash
$acl = Get-Acl HKCU:\Software\Testkey
$acl.Owner
mosser
$me = [System.Security.Principal.NTAccount]"$env:userdomain\$env:username"
$acl.SetOwner($me)        

```

*接管一个注册表键（先有权限访问）的所有权限*

```bash
del HKCU:\Software\Testkey2
md HKCU:\Software\Testkey2
$acl = Get-Acl HKCU:\Software\Testkey2
$person = [System.Security.Principal.NTAccount]"Administrators"
$access = [System.Security.AccessControl.RegistryRights]"FullControl"
$inheritance = [System.Security.AccessControl.InheritanceFlags]`
"ObjectInherit,ContainerInherit"
$propagation = [System.Security.AccessControl.PropagationFlags]"None"
$type = [System.Security.AccessControl.AccessControlType]"Allow"
$rule = New-Object System.Security.AccessControl.RegistryAccessRule( `
$person,$access,$inheritance,$propagation,$type)

$acl.ResetAccessRule($rule) 
$person = [System.Security.Principal.NTAccount]"Everyone"
$access = [System.Security.AccessControl.RegistryRights]"ReadKey"
$inheritance = [System.Security.AccessControl.InheritanceFlags]`
"ObjectInherit,ContainerInherit"
$propagation = [System.Security.AccessControl.PropagationFlags]"None"
$type = [System.Security.AccessControl.AccessControlType]"Allow"
$rule = New-Object System.Security.AccessControl.RegistryAccessRule( `
$person,$access,$inheritance,$propagation,$type)
$acl.ResetAccessRule($rule)
Set-Acl HKCU:\Software\Testkey2 $acl

```

*管理员拥有更改权限普通用户只有读取的新键的权限*

