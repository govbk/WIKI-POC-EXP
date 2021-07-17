# MKCMS v6.2 验证码重用

### 一、漏洞简介

### 二、漏洞影响

MKCMS v6.2

### 三、复现过程

/admin/cms_login.php验证码处的逻辑如下，比较session中的验证码和输入的是否一致，不一致就进入alert_href，这个js跳转，实际是在刷新页面


```php
/admin/cms_login.php:
<?php 
 6   ...
 7  if(isset($_POST['submit'])){
 8:     if ($_SESSION['verifycode'] != $_POST['verifycode']) {
 9          alert_href('验证码错误','cms_login.php');
10      }
```

![](images/15891863825098.png)


跳转后就会刷新验证码，然而我用的是burp，默认是不解析js的

全局搜索这个`$_SESSION['verifycode']`，发现只在/system/verifycode.php有赋值，也就是说，如果使用验证码后，我们不跟随js跳转，就不会重置验证码，验证码也就能被重复使用了

![](images/15891864469230.png)


**参考链接**

https://xz.aliyun.com/t/7580#toc-4