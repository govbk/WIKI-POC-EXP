## RecentApps

> win10之后特有，RecentApps包含了系统上已访问的多个应用程序和文件的引用。除了应用程序和文件名之外，RecentApps还提供了应用程序的路径，启动计数，文件的完整路径以及上次访问文件的时间。

注册表位置为：
**注**：记录实时更新，数据无加密

```
HKCU\Software\Microsoft\Windows\Current Version\Search\RecentApps

```

`RecentApps`键的下面是一系列由GUID命名的子项，在RecentApps下的每个`GUID`子项都对应一个应用程序。一些GUID子项也具有其他子项，它们与应用程序访问的特定文件相对应。

![](images/security_wiki/15906453450684.png)


**注**：`LastAccessedTime`是采用64位的`FILETIME`格式，转化为`datetime`也比较简单，用系统自带的`w32tm.exe`就行

```bash
w32tm.exe /ntte 131781889970180000

output: 152525 08:03:17.0180000 - 2018/8/8 16:03:17

```

或者用powershell

```bash
powershell -c "[datetime]::FromFileTime(0x1d42eee43808fa0)"

output: 2018年8月8日 16:03:17

```

