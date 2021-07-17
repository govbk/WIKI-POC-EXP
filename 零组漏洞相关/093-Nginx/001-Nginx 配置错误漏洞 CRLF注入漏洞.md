# Nginx 配置错误漏洞 CRLF注入漏洞

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

下面两种情景十分常见：

* 用户访问http://url/aabbcc，自动跳转到https://url/aabbcc
* 用户访问http://url/aabbcc，自动跳转到http://url/aabbcc

比如我的博客，访问http://url/other/tinger.html，将会301跳转到https://url/other/tinger.html。随着现在https的普及，很多站点都强制使用https访问，这样的跳转非常常见。

第二个场景主要是为了统一用户访问的域名，更加有益于SEO优化。

在跳转的过程中，我们需要保证用户访问的页面不变，所以需要从Nginx获取用户请求的文件路径。查看Nginx文档，可以发现有三个表示uri的变量：

* $uri
* $document_uri
* $request_uri

解释一下，1和2表示的是解码以后的请求路径，不带参数；3表示的是完整的URI（没有解码）。Nginx会将$uri进行解码，导致传入%0a%0d即可引入换行符，造成CRLF注入漏洞。那么，如果运维配置了下列的代码：

// 错误的配置文件示例（原本的目的是为了让http的请求跳转到https上）：


```bash
location / {
    return 302 https://$host$uri;
}
```

**Payload: **`http://url:8080/%0a%0dSet-Cookie:%20a=1`，可注入Set-Cookie头。

![](images/15891955581819.png)


### 参考链接

https://www.leavesongs.com/PENETRATION/nginx-insecure-configuration.html

https://vulhub.org/#/environments/nginx/insecure-configuration/