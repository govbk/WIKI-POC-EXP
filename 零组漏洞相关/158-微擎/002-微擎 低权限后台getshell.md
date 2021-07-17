# 微擎 低权限后台getshell

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

/web/index.php?c=site&a=editor

这个文件可以编辑html，然后前台会解析成php

没测试最新版

比如编辑专题：`/web/index.php?c=site&a=editor&do=page&multiid=0`

上架抓包

![](images/15897256219349.png)


改html内容为php

![](images/15897256287793.png)


复制前台url

![](images/15897256362036.png)


访问之

![](images/15897256429007.png)
