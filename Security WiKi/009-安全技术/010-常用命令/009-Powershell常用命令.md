# Powershell常用命令

```bash
get-host或$host.version或$PSVersionTable.PSVERSION    查看powershell版本

New-Item test -type Directory    新建目录

New-Item test -type File         新建文件

Remove-Item 文件或目录            删除文件或目录

get-content 1.txt                显示文本内容

set-content 1.txt -value "helloword" 设置文件内容

add-content 1.txt -value "love"  追加文本内容

Get-ExecutionPolicy              查看powershell执行策略

Set-ExecutionPolicy Unrestricted 设置powershell执行策略

    Restricted 为脚本不能运行，是默认设置

    Unrestricted 为允许所有的脚本运行

    RemoteSigned 为只能运行本地创建的脚本，不能运行从网上下载的脚本，除了有数字签名证书

    Allsigned 为只运行有受信任的发布者签名的脚本

get-process                        获取所有进程

Set-Alias  例如Set-Alias aaa get-process     给命令起别名

Get-Command                        查看当前作用域支持的所有命令

```

