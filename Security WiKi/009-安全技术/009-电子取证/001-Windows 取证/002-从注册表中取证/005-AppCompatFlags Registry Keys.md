## AppCompatFlags Registry Keys

保存所有以兼容模式启动的程序（包括以管理员身份运行的程序）：

**注**：无加密，数据实时更新

```
HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers

```

查询方式直接查询注册表即可：

```
reg query "HKLM\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"

```

![](images/security_wiki/15906452193321.png)


保存所有执行过的程序：

解析工具：https://nirsoft.net/utils/executed_programs_list.html

这个工具会解析如下路径（包含了上面我们说过的`MUICache`，也包含了我们后面说的`Prefetch`）

**注**：1 ~ 4无加密，5加密，1 ~ 5数据实时更新

```bash
1\. Registry Key: HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache
2\. Registry Key: HKEY_CURRENT_USER\Software\Microsoft\Windows\ShellNoRoam\MUICache
3\. Registry Key: HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted
4\. Registry Key: HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store
5\. Windows Prefetch folder (C:\Windows\Prefetch)

```

图形化界面：

![](images/security_wiki/15906452283433.png)


命令行解析：

```
ExecutedProgramsList.exe  /stext out.txt //保存文本格式
ExecutedProgramsList.exe  /shtml out.txt //保存html格式
ExecutedProgramsList.exe  /sxml out.txt  //保存xml格式

```

