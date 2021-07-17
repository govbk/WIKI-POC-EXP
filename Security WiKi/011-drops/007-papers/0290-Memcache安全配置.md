# Memcache安全配置

0x00 Memcache简介
---------------

* * *

Memcache是一个高性能的分布式的内存对象缓存系统，通过在内存里维护一个统一的巨大的hash表，它能够用来存储各种格式的数据，包括图像、视频、文件以及数据库检索的结果等。简单的说就是将数据调用到内存中，然后从内存中读取，从而大大提高读取速度。

Memcache是danga的一个项目，最早是LiveJournal 服务的，最初为了加速 LiveJournal 访问速度而开发的，后来被很多大型的网站采用。

Memcached是以守护程序方式运行于一个或多个服务器中，随时会接收客户端的连接和操作。

0x01 搭建Memcache服务
-----------------

* * *

```
yum install memcached 

```

安装memcache服务端

```
yum -y install php-pecl-memcache 

```

安装php扩展操作memcache

```
php -m | grep memcache 

```

查看php扩展是否安装成功

```
memcached -d -m 100 -u root -l x.x.x.x -p 11211 -c 512 -P /tmp/memcached.pid

```

参数说明：

```
-d选项是启动一个守护进程；
-m是分配给Memcache使用的内存数量，单位是MB，我这里是100MB；
-u是运行Memcache的用户，我这里是root；
-l是监听的服务器IP地址我这里指定了服务器的IP地址x.x.x.x；
-p是设置Memcache监听的端口，我这里设置了11211，最好是1024以上的端口；
-c选项是最大运行的并发连接数，默认是1024，我这里设置了512，按照你服务器的负载量来设定；
-P是设置保存Memcache的pid文件，我这里是保存在 /tmp/memcached.pid；

```

想要结束memcache进程

```
kill `cat /tmp/memcached.pid` 

```

设置开机启动

```
chkconfig memcached on 

```

phpMemcachedAdmin图形化界面，操作memcache，类似phpmyadmin

[http://blog.elijaa.org/index.php?pages/phpMemcachedAdmin-Installation-Guide](http://blog.elijaa.org/index.php?pages/phpMemcachedAdmin-Installation-Guide)

最新版默认界面

![enter image description here](http://drops.javaweb.org/uploads/images/90a78a973f93650c2cafd5ba777369f57888a409.jpg)

Execute Commands on Servers那里可以执行命令。

当然了用telnet其实是一样的。

0x02 memcache匿名访问危害
-------------------

* * *

在乌云提交的漏洞当中，有很多因为memecache限制不严格，导致信息泄露的问题：

[WooYun: memcached未作IP限制导致缓存数据可被攻击者控制](http://www.wooyun.org/bugs/wooyun-2010-0790)

[WooYun: 通过Memcache缓存直接获取某物流网用户密码等敏感数据](http://www.wooyun.org/bugs/wooyun-2013-037301)

[WooYun: 56.com memcached端口可以远程使用](http://www.wooyun.org/bugs/wooyun-2013-023891)

从memcache中获取信息通常是先查看items信息：

stats items

![enter image description here](http://drops.javaweb.org/uploads/images/ac2d6fd52907d2cba6d7eeefb29dd25bdc379257.jpg)

```
stats cachedump <item: id> <返回结果数量,0代表返回全部>

```

![enter image description here](http://drops.javaweb.org/uploads/images/fec70fea74060a178cde99458e982f8dc7a31795.jpg)

除了查看信息，通用可以修改删除信息。

phpMemcachedAdmin执行命令那里也有个可以搜索key的脚本，并且支持正则匹配。

0x03 查找可匿名访问memcache的方式
-----------------------

* * *

memcache默认是11211端口，可使用nmap扫描有开11211端口的服务器。

```
nmap -n --open -p 11211 X.X.X.X/24

```

然后telnet上，执行下

```
stats items

```

看看是否有返回结果。

0x04安全配置
--------

* * *

Memcache服务器端都是直接通过客户端连接后直接操作，没有任何的验证过程，这样如果服务器是直接暴露在互联网上的话是比较危险，轻则数据泄露被其他无关人员查看，重则服务器被入侵，因为Mecache是以root权限运行的，况且里面可能存在一些我们未知的bug或者是缓冲区溢出的情况，这些都是我们未知的，所以危险性是可以预见的。

### 内网访问

最好把两台服务器之间的访问是内网形态的，一般是Web服务器跟Memcache服务器之间。普遍的服务器都是有两块网卡，一块指向互联网，一块指向内网，那么就让Web服务器通过内网的网卡来访问Memcache服务器，我们Memcache的服务器上启动的时候就监听内网的IP地址和端口，内网间的访问能够有效阻止其他非法的访问。

```
# memcached -d -m 1024 -u root -l 192.168.0.200 -p 11211 -c 1024 -P /tmp/memcached.pid

```

Memcache服务器端设置监听通过内网的192.168.0.200的ip的11211端口，占用1024MB内存，并且允许最大1024个并发连接

### 设置防火墙

防火墙是简单有效的方式，如果却是两台服务器都是挂在网的，并且需要通过外网IP来访问Memcache的话，那么可以考虑使用防火墙或者代理程序来过滤非法访问。 一般我们在Linux下可以使用iptables或者FreeBSD下的ipfw来指定一些规则防止一些非法的访问，比如我们可以设置只允许我们的Web服务器来访问我们Memcache服务器，同时阻止其他的访问。

```
# iptables -F
# iptables -P INPUT DROP
# iptables -A INPUT -p tcp -s 192.168.0.2 --dport 11211 -j ACCEPT
# iptables -A INPUT -p udp -s 192.168.0.2 --dport 11211 -j ACCEPT

```

上面的iptables规则就是只允许192.168.0.2这台Web服务器对Memcache服务器的访问，能够有效的阻止一些非法访问，相应的也可以增加一些其他的规则来加强安全性，这个可以根据自己的需要来做。