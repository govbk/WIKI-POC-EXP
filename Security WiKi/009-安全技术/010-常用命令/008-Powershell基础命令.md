# Powershell基础命令

#powershell递归寻址注册表

```bash
$key = Get-Item HKLM:\Software\Microsoft\PowerShell\1
$key.Name
HKEY_LOCAL_MACHINE\Software\Microsoft\PowerShell\1

$key | Format-List ps*

```

