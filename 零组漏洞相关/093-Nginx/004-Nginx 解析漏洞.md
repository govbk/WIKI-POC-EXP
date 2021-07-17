# Nginx 解析漏洞

### 一、漏洞简介

### 二、漏洞影响

* Nginx 1.x 最新版
* PHP 7.x最新版

### 三、复现过程

直接执行`docker-compose up -d`启动容器，无需编译。

访问`http://url/uploadfiles/nginx.png和http://your-ip/uploadfiles/nginx.png/.php`即可查看效果。

正常显示：

![](images/15891957815463.jpg)


增加/.php后缀，被解析成PHP文件：

![](images/15891957878433.jpg)


