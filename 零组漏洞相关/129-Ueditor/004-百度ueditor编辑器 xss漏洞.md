# 百度ueditor编辑器 xss漏洞

### 一、漏洞简介

产品官网下载地址：

https://ueditor.baidu.com/website/download.html#mini

涉及版本：php , asp, jsp, net

### 二、漏洞影响

### 三、复现过程

漏洞分析

存在漏洞的文件：


```bash
/php/getContent.php
/asp/getContent.asp
/jsp/getContent.jsp
/net/getContent.ashx
```

/php/getContent.php

![](images/15893731532774.png)


入进行了过滤，但是在14行输出时却使用了htmlspecialchars_decode，造成XSS漏洞。

/asp/getContent.asp

![](images/15893731590964.png)


获取myEditor参数无过滤，直接输出。

/jsp/getContent.jsp

![](images/15893731654876.png)


获取myEditor参数无过滤，直接输出。

/net/getContent.ashx

![](images/15893731715671.png)


获取myEditor参数无过滤，直接输出。

### 漏洞复现

php版本测试，其他版本一样。

![](images/15893731800583.png)


url:


```bash
http://url/php/getcontent.php
```

payload:


```bash
myEditor=<script>alert(document.cookie)</script>
// myEditor中的’ E ’必须大写，小写无效。
```

由于只是个反弹XSS，单独这个漏洞影响小。若能结合使用该编辑器的网站的其他漏洞使用，则可能产生不错的效果。

**四、参考链接**

https://blog.csdn.net/yun2diao/article/details/91381846