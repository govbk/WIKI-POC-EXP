## MUICache

> 每次开始使用新的应用程序时，Windows都会自动从exe文件的版本资源中提取应用程序名，并将其存储在名为`MuiCache`的注册表项中，供以后使用。

**注**：无加密，记录实时更新

注册表位置：
windows server 2003及以前的

```bash
当前用户：
HKEY_CURRENT_USER/Software/Microsoft/Windows/ShellNoRoam/MUICache

所有用户：
HKEY_USERS\<sid>\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache

```

windows server 2003及以后的

```bash
当前用户：
HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache

所有用户：
HKEY_USERS\<sid>\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache

```

![](images/security_wiki/15906451023728.png)


图形化界面：

解析工具：http://www.nirsoft.net/utils/muicache_view.html

![](images/security_wiki/15906451102464.png)


命令行使用

```bash
MUICache.exe  /stext out.txt //保存文本格式
MUICache.exe  /shtml out.txt //保存html格式
MUICache.exe  /sxml out.txt  //保存xml格式

```

或者命令行直接查询注册表也可以

```
reg query "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"

```

![](images/security_wiki/15906451199101.png)


