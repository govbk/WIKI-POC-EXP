# Anydesk

Anydesk是一款类似于Teamviewer的远控软件，可以采用免安装打开,除了覆盖配置以外,还提供了很便捷的API。

在文件目录下执行以下代码便可以安装并设置远程连接密码(高权)

```
AnyDesk.exe --install "C:\Install\AnyDesk\Here" --start-with-win --silent --create-shortcuts --create-desktop-icon

echo licence_keyABC | "C:\Install\AnyDesk\Here\AnyDesk.exe" --register-licence

echo password123 | "C:\Install\AnyDesk\Here\AnyDesk.exe" --set-password

```

同时也可以通过如下命令获取正在运行种的Anydesk连接用户名：

```
@echo off 
for /f "delims=" %%i in ('anydesk --get-id') do set CID=%%i
echo AnyDesk password is: %CID%
pause

```

