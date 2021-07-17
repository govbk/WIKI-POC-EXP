# CatfishCMS 4.6.15 前台xss

## 漏洞影响

CatfishCMS 4.6

## 复现过程

代码分析

url：


```
http://url/cms/CatfishCMS-4.6.12/index.php/index/Index/pinglun
```

文件：application/index/controller/Index.php

方法：pinglun(

![](images/15889452703657.png)


文件：application\index\controller\Common.php

过滤函数：filterJs()

![](images/15889452773859.png)


**漏洞复现**

首先注册一个用户

![](images/15889452902262.png)


![](images/15889452941806.png)


![](images/15889452984716.png)


![](images/15889453040888.png)




