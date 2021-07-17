# DNS隧道技术绕防火墙

0x01 概念
=======

* * *

隧道技术（Tunneling）是一种通过使用互联网络的基础设施在网络之间传递数据的方式。使用隧道传递的数据（或负载）可以是不同协议的数据帧或包。隧道协议将其它协议的数据帧或包重新封装然后通过隧道发送。新的帧头提供路由信息，以便通过互联网传递被封装的负载数据。

0x02 实例分析- DNS隧道技术
==================

* * *

环境：客户机（Kali）+DNS服务器（window2003）+目标机（redhat7）

DNS服务器：192.168.10.132
---------------------

1、新建一个名字为”bloodzero.com”的正向解析域

![](http://drops.javaweb.org/uploads/images/dc4c5b134893c1ecc7e7e3567d2e6c179f7c4be0.jpg)

2、新建一个主机：IP为攻击者kali的IP

![](http://drops.javaweb.org/uploads/images/96168bd36aa8461bd9ec1b6af3608897c3d4da2d.jpg)

3、新建一个委托

![](http://drops.javaweb.org/uploads/images/eb92d4b93d8e80810528c208f182007864d2a094.jpg)

此时我们的DNS服务器就配置好了！

Kali：攻击者&&客户端 192.168.10.135
----------------------------

1、攻击端配置：

修改dns2tcpd配置文件：

![](http://drops.javaweb.org/uploads/images/a38873da6203ee0cca090485ccd287f27540db09.jpg)

resources的IP为目标机的IP

![](http://drops.javaweb.org/uploads/images/2e7402f4a50eb926122ba36f7fb2a4e1604a5f37.jpg)

启动dns隧道的服务端

![](http://drops.javaweb.org/uploads/images/8a0f92bd5c11fe9cf8ee8ae5c46ff9e26e2621da.jpg)

2、客户端配置

删除ssh连接的known_hosts文件

![](http://drops.javaweb.org/uploads/images/6382a7e999c30c5c2c5883d062677ab487c9416e.jpg)

修改DNS解析文件:`vim /etc/resolv.conf`

![](http://drops.javaweb.org/uploads/images/ba9361646fb29fab6e4a94f4351e87585a55829c.jpg)

![](http://drops.javaweb.org/uploads/images/1df490726b0f60ff8b931ea8bf76dbdb59b68252.jpg)

![](http://drops.javaweb.org/uploads/images/d4704e855afb07945d5fbedc9489d160187e5828.jpg)

配置dns隧道客户端程序

在kali2.0中，没有配置文件，需要自己写配置文件

`vim /etc/dns2tcpc.conf`

![](http://drops.javaweb.org/uploads/images/29adee429973fcffdf94811d6d294e8be56409fd.jpg)

测试是否可以提供服务

![](http://drops.javaweb.org/uploads/images/88da3fc5ab965b60f162792435b231e473a6cd74.jpg)

这个时候我们就已经配置成功了！

成功效果
----

![](http://drops.javaweb.org/uploads/images/44c391c3a799af1b0124bf31e4c63cb8b5242d07.jpg)

![](http://drops.javaweb.org/uploads/images/2bd96043c9897d767133cfaa7d625051471d8c83.jpg)

![](http://drops.javaweb.org/uploads/images/5eb3a73ff84d8c6e04ad376a0837978c14a342b4.jpg)

0x03 分析结论
=========

* * *

这个时候的流量走向：

![](http://drops.javaweb.org/uploads/images/cc6e03abbb8376b3fc54efdaf15a21b592a2e9b0.jpg)

本文中介绍的是DNS隧道服务器，和DNS隧道客户端是同一台机器，并不能说明问题，当DNS隧道服务器存在于防火墙之后，这个时候我们就可以利用此种技术来绕过大部分的防火墙。并且可绕过不开端口，隐蔽性好等；

![](http://drops.javaweb.org/uploads/images/3af0f767214d04b8fbd8a532d8f616575de92201.jpg)

这里我使用另外一台客户机去连接目标机时，服务端监听的数据如下：

*   目标机：192.168.10.133
*   DNS隧道服务端：192.168.10.135
*   DNS隧道客户端：192.168.10.134
*   DNS服务器：192.168.10.132

![](http://drops.javaweb.org/uploads/images/3f3018145586d6f1e30a5688f387f15560d907ca.jpg)

客户端监听数据如下：

![](http://drops.javaweb.org/uploads/images/9b534f58f4697c3ad5ea691f61114814df7664c5.jpg)

发现能够监听到的ssh数据包是DNS隧道服务端与目标机之间的通信；

而客户端与目标机之间的通信是DNS数据；

这就是简单的配置DNS隧道；