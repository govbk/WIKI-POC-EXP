# ShopXO v1.8.0 后台getshell

### 一、漏洞简介

### 二、漏洞影响

ShopXO 小于v1.8.0

### 三、复现过程

默认后台密码

admin shopxo

![](images/15893401490671.png)


![](images/15893401527765.png)


登入后台-》应用中心-》应用商店-》主题

随便下载一个主题

![](images/15893401595660.png)


![](images/15893401632987.png)


然后把下载下来的压缩包解压出来 把shell放入static目录

![](images/15893401703969.png)


回到网站后台

网站管理-》主题管理-》安装主题

![](images/15893401795579.png)


shell地址


```
http://url/static/index/default/shell.php
```

public是运行目录！！！