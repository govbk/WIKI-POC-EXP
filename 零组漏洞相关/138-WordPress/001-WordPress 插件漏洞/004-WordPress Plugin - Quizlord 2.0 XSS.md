# WordPress Plugin - Quizlord 2.0 XSS

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

首先搭建worepress，我的版本是4.4。然后进入后台下载插件Quizlord，版本是2.0。

![](images/15894211880169.png)


![](images/15894211917682.png)


下载、安装完成后，需要点击启用插件。

![](images/15894211993694.png)


根据exploit-db给出的漏洞详情，找到触发漏洞的位置。

![](images/15894212144966.png)


进入后台选择Quizlord插件

![](images/15894212225174.png)


此时浏览器的地址栏正好对应poc中的referer内容，现在只要使用火狐插件hackbar并根据POC构造POST请求

![](images/15894212307740.png)


点击execute即可发送该POST请求。

![](images/15894212388822.png)


请求成功后，返回是一个空白页。

![](images/15894212450928.png)
