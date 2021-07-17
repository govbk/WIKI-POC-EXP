# phpstudy nginx 解析漏洞

### 一、漏洞简介

phpStudy 存在 nginx 解析漏洞，攻击者能够利用上传功能，将包含恶意代码的合法文件类型上传至服务器，从而造成任意代码执行的影响。

该漏洞仅存在于phpStudy Windows版，Linux版不受影响。

影响版本：phpstudy <= 8.1.0.7

### 二、漏洞复现

将图片马放到phpstudy安装路径的WWW文件夹下

访问`http://127.0.0.1/nginx.png`，正常显示，如下图所示。

![](media/202009/15995311061205.jpg)

然后增加/qwerty.php后缀，被解析成php文件，如下图所示。

![](media/202009/15995311205798.jpg)


### 漏洞分析

该漏洞属于安全配置错误漏洞。

漏洞产生的原因为：

1、由于配置错误，导致 nginx 把以 .php 结尾的文件交给 fastcgi 处理，因此可以构造 `http://www.xxx.com/test.png/xx.php` （任何服务器端不存在的php文件均可，比如a.php）

2、但是 fastcgi 在处理 xx.php 文件时发现文件并不存在，这时 php.ini 配置文件中 cgi.fix_pathinfo=1 发挥作用，这项配置用于修复路径，如果当前路径不存在则采用上层路径。因此这里交由 fastcgi 处理的文件就变成了 /test.png 。

3、最重要的一点是 php-fpm.conf 中的 security.limit_extensions 配置项限制了 fastcgi 解析文件的类型（即指定什么类型的文件当做代码解析），此项设置为空的时候才允许 fastcgi 将 .png 等文件当做代码解析。

参考链接

https://www.anquanke.com/post/id/216473

https://mrxn.net/news/675.html

https://mp.weixin.qq.com/s?__biz=MzAxMjE3ODU3MQ==&mid=2650480468&idx=3&sn=709ffded8ed465ee03f91f2478aaba69