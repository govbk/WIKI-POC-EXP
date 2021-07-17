## RunMRU

> 保存Win+R启动程序的历史记录

注册表位置：

**注**：数据无加密，记录实时更新

```bash
当前用户：
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU

所有用户：
HKEY_USERS\<sid>\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU

```

命令行查询注册表

```bash
reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"

```

![](images/security_wiki/15906451710675.png)


