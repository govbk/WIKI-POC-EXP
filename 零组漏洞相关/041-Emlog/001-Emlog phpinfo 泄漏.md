# Emlog phpinfo 泄漏

### 一、漏洞简介

需要登陆（至少是网站的会员/作者权限）

### 二、漏洞影响

### 三、复现过程

首先看看漏洞出现的位置：

![](images/15890068394144.png)


如上图，我们只要构造如下的URL：


```
http://url:81/admin/index.php?action=phpinfo
```

直接访问：

![](images/15890068601207.png)


**四、参考链接**

http://www.jeepxie.net/article/687123.html