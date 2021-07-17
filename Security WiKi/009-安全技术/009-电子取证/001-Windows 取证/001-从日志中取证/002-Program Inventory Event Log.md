## Program Inventory Event Log

> `Program Inventory`win7及以上存在，主要用于记录软件活动摘要、安装的程序、安装的Internet Explorer加载项、更新的应用程序、已删除的应用程序

文件夹中的位置：`C:\Windows\System32\winevt\Logs\Microsoft-Windows-Application-Experience%4Program-Inventory.evtx`，如图

![](images/security_wiki/15906446983150.png)


在Windows事件查看器的位置：`Applications and Services Logs\Microsoft\Application-Experience\Program-Inventory`，如图

![](images/security_wiki/15906447060328.png)


日志获取：

```bash
wevtutil qe /f:text Microsoft-Windows-Application-Experience/Program-Inventory

```

Envent IDs：

1. 800 (`summary of software activities`)
2. 900 & 901 (`new Internet Explorer add-on`)
3. 903 & 904 (`new application installation`)
4. 905 (`updated application`)
5. 907 & 908 (`removed application`)

![](images/security_wiki/15906447172648.png)


