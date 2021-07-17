# Powershell注册表操作

#注册表操作命令

```bash
Get-PSProvider          获取安装的提供程序列表

Dir, Get-ChildItem  列出键的内容

Cd, Set-Location    更改当前（键）目录

HKCU:, HKLM:            预定义的两个重要注册表根目录虚拟驱动器

Get-ItemProperty    读取键的值

Set-ItemProperty    设置键的值

New-ItemProperty    给键创建一个新值

Clear-ItemProperty  删除键的值内容

Remove-ItemProperty     删除键的值

New-Item, md            创建一个新键

Remove-Item, Del    删除一个键

Test-Path           验证键是否存在

Get-PSDrive -PSProvider Registry    查看那些注册表驱动器已经被注册表提供程序使用

New-PSDrive job1 registry "HKLM:\Software\Microsoft\Windows NT\CurrentVersion" 
dir job1:                        自由地创建任何额外的驱动器

```

