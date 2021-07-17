# sql server常用操作远程桌面命令

## 1.是否开启远程桌面，1表示关闭，0表示开启

```sql
EXEC master..xp_regread 'HKEY_LOCAL_MACHINE','SYSTEM\CurrentControlSet\Control\Terminal Server'  ,'fDenyTSConnections'

```

## 2.读取远程桌面端口

```sql
EXEC master..xp_regread 'HKEY_LOCAL_MACHINE','SYSTEM\CurrentControlSet\Control\Terminal  Server\WinStations\RDP-Tcp','PortNumber' 

```

## 3.开启远程桌面

```sql
EXEC master.dbo.xp_regwrite'HKEY_LOCAL_MACHINE','SYSTEM\CurrentControlSet\Control\Terminal  Server','fDenyTSConnections','REG_DWORD',0;

```

reg文件开启远程桌面：

```bash
Windows Registry Editor Version 5.00HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal  Server]"fDenyTSConnections"=dword:00000000[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal  Server\WinStations\RDP-Tcp]"PortNumber"=dword:00000d3d ////

保存micropoor.reg，并执行regedit /s micropoor.reg

 注：如果第一次开启远程桌面，部分需要配置防火墙规则允许远程端口。

 netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow

```

## 4.关闭远程桌面

```bash
EXEC master.dbo.xp_regwrite'HKEY_LOCAL_MACHINE','SYSTEM\CurrentControlSet\Control\Terminal  Server','fDenyTSConnections','REG_DWORD',1;
Micropoor

```

