# Zzzcms 1.61 后台远程命令执行漏洞

### 一、漏洞简介

zzzphp cms ，远程代码执行漏洞存在的主要原因是页面对模块的php代码过滤不严谨，导致在后台可以写入php代码从而造成代码执行。

### 二、漏洞影响

Zzzcms 1.61

### 三、复现过程

漏洞分析

打开/search/index.php


```
require dirname(dirname(__FILE__)). '/inc/zzz_client.php';
```

发现是跳到/inc/zzz_client.php，那么我们就来到/inc/zzz_client.php

![](images/15896921040960.png)


发现解析模块是通过ParsetTemplate来解析的，那么我们找到ParserTemplate类的php文件zzz_template.php。在zzz_template.php中我们发现一个IF语句


```php
$zcontent = $this->parserIfLabel( $zcontent ); // IF语句
```

那么我们来到zzz_template.php中对parserIfLabel的定义

![](images/15896921219849.png)


发现$ifstr 经过一连串的花里胡哨的过滤最后进了evel函数，然后使用了evel函数执行，最后造成了本次远程代码执行漏洞。

#### 漏洞复现

在后台模块管理中的电脑模块找到cn2016

![](images/15896921324829.png)


然后在cn2016文件中到html文件，然后在html文件中找到search.html，然后将其的代码修改为


```php
{if:assert($_request[phpinfo()])}phpinfo();{end if}
```

![](images/15896921495838.png)


然后打开`http://xxxx.com/zzzcms/search/`就可以看到我们刚刚输入的phpinfo()执行了。

参考链接

https://xz.aliyun.com/t/4471