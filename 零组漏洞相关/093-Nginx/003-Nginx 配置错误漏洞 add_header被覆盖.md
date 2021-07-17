# Nginx 配置错误漏洞 add_header被覆盖

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

Nginx配置文件子块（server、location、if）中的add_header，将会覆盖父块中的add_header添加的HTTP头，造成一些安全隐患。

如下列代码，整站（父块中）添加了CSP头：


```bash
add_header Content-Security-Policy "default-src 'self'";
add_header X-Frame-Options DENY;

location = /test1 {
    rewrite ^(.*)$ /xss.html break;
}

location = /test2 {
    add_header X-Content-Type-Options nosniff;
    rewrite ^(.*)$ /xss.html break;
}
```

但/test2的location中又添加了X-Content-Type-Options头，导致父块中的add_header全部失效：

![](images/15891957078525.png)


XSS可被触发：

![](images/15891957145032.png)
