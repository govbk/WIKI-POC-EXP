# snmp弱口令引起的信息泄漏

0x00 snmp协议简介
-------------

* * *

snmp协议即简单网络管理协议（SNMP，Simple Network Management Protocol）。目前一共有3个版本：V1,V2c，V3。V3是最新的版本，在安全的设计上有了很大改进。不过目前广泛应用的还是存在较多安全问题的V1和V2c版本，本文讨论的内容也是基于这两个版本。

了解更多[snmp协议内容可以参考维基百科](http://zh.wikipedia.org/wiki/SNMP)

顾名思义，snmp是用来进行网络管理的。cacti和mrtg等监控工具都是基于snmp协议。snmp协议工作的原理简单点来说就是管理主机向被管理的主机或设备发送一个请求，这个请求包含一个community和一个oid。oid就是一个代号，代表管理主机这个请求想要的信息。比如cpu的使用率的oid可能是112,内存的使用率的oid可能是113.这个oid是约定好的。被管理的主机收到这个请求后，先看请求的community是否和自己保存的一致，如果一致，则把112代表的cpu使用率，或者113代表的内存使用率返回给管理主机。如果不一致，就不会返回任何信息。所以community相当与一个认证的口令。需要提一句的是V1和V2c版本的snmp协议都是明文传输数据的，所以可以通过抓包嗅探等手段获取认证需要的community。

管理主机通过snmp协议除了可以获取被管理主机的信息，还可以修改被管理主机的一些配置信息（通常是路由器等设备）。

通过上面提到的snmp的应用可以总结出snmp弱口令或者口令泄漏引起的安全问题：一是信息泄漏，二是设备的配置可能被修改从而被他人控制。本文讨论第一种情况。

0x01 通用的信息泄漏
------------

* * *

看一下乌云的几个案例，热热身：

[优酷后台访问未设置权限+snmp弱口令](http://www.wooyun.org/bugs/wooyun-2010-06953)

[蘑菇街SNMP弱口令一枚](http://www.wooyun.org/bugs/wooyun-2010-015165)

[CactiEZ 中文版snmp默认团体名](http://www.wooyun.org/bugs/wooyun-2010-07862)

[kingsoft SNMP弱口令](http://www.wooyun.org/bugs/wooyun-2010-03488)

既然大家都说snmp引起信息泄漏，导致服务器可能被入侵。那我们就看看snmp到底可以泄漏那些信息吧。下面是我总结的一些泄漏敏感信息的节点oid（使用snmpwalk指令来获取信息）。欢迎补充指正。

```
系统信息 1.3.6.1.2.1.1

```

样例：

```
SNMPv2-MIB::sysDescr.0 = STRING: Linux xxoo.zwt.qihoo.net 2.6.18-164.el5xen #1 SMP Thu Sep 3 04:03:03 EDT 2009 x86_64
SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (1876050197) 217 days, 3:15:01.97
SNMPv2-MIB::sysContact.0 = STRING: Root <root@localhost> (configure /etc/snmp/snmp.local.conf)
SNMPv2-MIB::sysName.0 = STRING: xxoo.zwt.qihoo.net
SNMPv2-MIB::sysLocation.0 = STRING: Unknown (edit /etc/snmp/snmpd.conf)
SNMPv2-MIB::sysORLastChange.0 = Timeticks: (0) 0:00:00.00

```

显然，这个sysDescr是系统的描述信息，这里我们看到这台机器的域名很可能是xxoo.zwt.qihoo.net,内核的版本是2.6.18-164.el5xen，系统是64位的。sysUpTimeInstance就是系统运行时间了。sysContact这里显示的是管理员的联系方式，这个例子中管理员没有配置。

```
系统进程列表 1.3.6.1.2.1.25.4.2.1.2

```

样例：

```
HOST-RESOURCES-MIB::hrSWRunName.11855 = STRING: "httpd"
HOST-RESOURCES-MIB::hrSWRunName.12579 = STRING: "vsftpd"
HOST-RESOURCES-MIB::hrSWRunName.14653 = STRING: "xinetd"
HOST-RESOURCES-MIB::hrSWRunName.32561 = STRING: "sshd"

```

这里省略N多。从进程列表我们可以知道服务器上开了那些服务，有哪些有意思的进程在跑。比如这个就可以看出来，它是开了ssh的。

```
系统安装软件列表 1.3.6.1.2.1.25.6.3.1.2

```

样例：

```
HOST-RESOURCES-MIB::hrSWInstalledName.595 = STRING: "xorg-x11-xfs-1.0.2-4"
HOST-RESOURCES-MIB::hrSWInstalledName.598 = STRING: "openssh-server-4.3p2-36.el5"
HOST-RESOURCES-MIB::hrSWInstalledName.140 = STRING: "NetworkManager-glib-0.7.0-9.el5"
HOST-RESOURCES-MIB::hrSWInstalledName.141 = STRING: "gnome-mount-0.5-3.el5"
HOST-RESOURCES-MIB::hrSWInstalledName.143 = STRING: "MySQL-devel-community-5.0.81-0.rhel5"

```

同样省略N多。有耐心慢慢分析的话是可以获取很多信息的。比如这里我看可以到它的ssh是4.3p2版本的，这个版本貌似是存在缺陷的。还有装了mysql，是5.0的

```
网口的数量，类型，物理地址和流量信息等 1.3.6.1.2.1.2

```

样例：

```
IF-MIB::ifNumber.0 = INTEGER: 3
IF-MIB::ifIndex.1 = INTEGER: 1
IF-MIB::ifIndex.2 = INTEGER: 2
IF-MIB::ifIndex.3 = INTEGER: 3
IF-MIB::ifDescr.1 = STRING: lo
IF-MIB::ifDescr.2 = STRING: eth0
IF-MIB::ifDescr.3 = STRING: sit0
IF-MIB::ifType.1 = INTEGER: softwareLoopback(24)
IF-MIB::ifType.2 = INTEGER: ethernetCsmacd(6)
IF-MIB::ifType.3 = INTEGER: tunnel(131)
IF-MIB::ifPhysAddress.1 = STRING: 
IF-MIB::ifPhysAddress.2 = STRING: aa:0:0:dc:5f:58
IF-MIB::ifPhysAddress.3 = STRING: 
IF-MIB::ifInOctets.1 = Counter32: 19030140
IF-MIB::ifInOctets.2 = Counter32: 4072910622
IF-MIB::ifInOctets.3 = Counter32: 0
IF-MIB::ifOutOctets.1 = Counter32: 19030140
IF-MIB::ifOutOctets.2 = Counter32: 2001152942
IF-MIB::ifOutOctets.3 = Counter32: 0

```

cacti等系统就是通过获取这些数据监控流量的。ifNumber是网口数量，ifType是网口类型，ifPhysAddress是mac地址，ifInOctets是流入的总流量，ifOutOctets是流出的总流量。等等。

```
IP-MAC地址转换表 1.3.6.1.2.1.3.1

```

样例：

```
RFC1213-MIB::atIfIndex.2.1.x.x.o.o = INTEGER: 2
RFC1213-MIB::atPhysAddress.2.1.x.x.o.o = Hex-STRING: 28 C0 DA 05 20 00 
RFC1213-MIB::atNetAddress.2.1.x.x.o.o = Network Address: DC:B5:37:81

```

我的理解应该跟执行arp -a命令的输出一样吧。

```
网口的ip地址和子网掩码 1.3.6.1.2.1.4.20

```

样例：

```
IP-MIB::ipAdEntAddr.127.0.0.1 = IpAddress: 127.0.0.1
IP-MIB::ipAdEntAddr.x.x.o.o = IpAddress: x.x.o.o
IP-MIB::ipAdEntIfIndex.127.0.0.1 = INTEGER: 1
IP-MIB::ipAdEntIfIndex.x.x.o.o = INTEGER: 2
IP-MIB::ipAdEntNetMask.127.0.0.1 = IpAddress: 255.0.0.0
IP-MIB::ipAdEntNetMask.x.x.o.o = IpAddress: 255.255.255.128
IP-MIB::ipAdEntBcastAddr.127.0.0.1 = INTEGER: 0
IP-MIB::ipAdEntBcastAddr.x.x.o.o = INTEGER: 1


路由表 1.3.6.1.2.1.4.21 鉴于打码太复杂，就不提供样例，可自己测试。
tcp connection table  1.3.6.1.2.1.6.13 相当与netstat -t 命令
开放的udp端口 1.3.6.1.2.1.7.5

```

此外在互联网上有两个oid被很多文章转载：

```
1.3.6.1.4.77.1.2.25.1.1 //**用户列表
1.3.6.1.4.77.1.4.1.0 //**域名

```

这两个oid都是存在的。不过测试了几台机器都没有返回任何信息。如果大家有更准确的测试结果欢迎反馈。

0x02 能不能更给力一点
-------------

* * *

耐着性子看完了上文形形色色的oid，你肯定已经知道，有了snmp的community之后，从系统内核到mac地址，路由表，到tcp connection都被我们看光光了。可是，仅仅就这个程度么？我们掌握了这么多的信息，这么多的信息，可是只靠snmp却依然无法控制这台设备。这是多么忧伤的一件事情。

如果snmp不仅仅可以读system up time，如果有个oid可以读到/etc/passwd甚至可以读到/etc/shadow那该多好啊。虽然目前这仅仅是YY，但是下面将要介绍一个类似的漏洞。那就是

[CVE-2012-3268](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2012-3268)

先看一下乌云案例：

[中国移动H3C防火墙侧漏，利用snmp获取管理员密码，成功登录设备！](http://www.wooyun.org/bugs/wooyun-2013-021877)

[中国移动集团华为三层交换SNMP漏洞，可获取管理帐号密码，已成功登录](http://www.wooyun.org/bugs/wooyun-2013-021964)

[通过snmp获取中国移动华为防火墙交换机等设备的登录密码](http://www.wooyun.org/bugs/wooyun-2010-032312)

看到没，通过特定的oid读到了设备中存储的用户名和密码，可以成功登录。

关于这个cve的来龙去脉可以参考Kurt Grutzmacher发表的文章

[HP/H3C and Huawei SNMP Weak Access to Critical Data](http://grutztopia.jingojango.net/2012/10/hph3c-and-huawei-snmp-weak-access-to.html)

同时Kurt Grutzmacher也提供了

[nmap和msf扫描这个漏洞的插件和破解加密密码的工具](https://github.com/grutz/h3c-pt-tools)

长话短说，本质上这依然是snmp引起的信息泄漏，只不过这里露的过于性感，用一个只读权限的community就可以读取到登录需要的用户名和密码。目前已知可以获取帐号的oid有一下三个:

```
1.3.6.1.4.1.2011.5.2.1.10.1
1.3.6.1.4.1.2011.10.2.12.1.1.1
1.3.6.1.4.1.25506.2.12.1.1.1

```

对于存在该漏洞的设备，只需要以此walk上面3个oid就可以了。虽然厂商都发布补丁修复了这个漏洞。但是由于某些你懂的原因，存在这个漏洞的设备依然有很多很多很多很多。so：请不要将本文提供的信息用于非法用途，后果自负～～。

需要说一下的是，发布这个漏洞的Kurt Grutzmacher在文章和扫描插件中只提到了后面两个oid，[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)的。感谢@s3cur1ty。