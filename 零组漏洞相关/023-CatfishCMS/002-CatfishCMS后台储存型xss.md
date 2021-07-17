# CatfishCMS后台储存型xss

### 漏洞简介

网站背景中的管理员可以发布包含存储XSS漏洞的文章 提交标题以抓取数据包 使用burp修改参数 浏览文章可以触发XSS

### 复现过程

![](images/15889447054806.png)



```
neiron=<img src=x onerror=alert(123)>
```

![](images/15889447225712.png)


![](images/15889447263631.png)
