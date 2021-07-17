# 内网渗透应用 跨vlan渗透的一种思路

0x00 前言
-------

* * *

随着日益发展的网络技术，网络线路也变的越来越复杂。渗透测试人员在web中通过注入，上传等基本或高级脚本渗透方法到达了边界服务器。再深入时则会面对更复杂的网络,比如乱七八糟的vlan环境。

什么是vlan:[http://baike.baidu.com/history/id=9328829](http://baike.baidu.com/history/id=9328829)

测试拓扑图

![2013092815410369840.jpg](http://drops.javaweb.org/uploads/images/d07de0b50be509ce954202799520fefb3dee4698.jpg)

0x01 测试基本状况概述
-------------

* * *

一共选取了三台服务器和一个H3C s3610三层交换机.顺带笔者的一台笔记本(Kali Linux).

三台服务器代表了tec503的基本业务划分。攻击者处在和webserver相同的vlan200中。并且攻击者已控制到webserver。

在交换机上划分了三个vlan 将Tec503(假想的目标公司)的数据服务器（dataserver.tec503.com）和web服务器（webserver.tec503.com）及域控分别划分在三个vlan（vlan100，vlan200，vlan300）下。vlan100和vlan200不能相互访问。但是都可以访问到vlan300.

交换机开启snmp和telnet(snmp一般用来监控交换机流量等,telnet用于管理三层交换机)。

测试目标:在尽可能少留下痕迹的前提下，接触到dataserver的数据。

0x02 前期基本渗透过程
-------------

* * *

在前期信息搜集时发现tec503.com存在域传送漏洞.由此确定了此次测试的目标ip(5.5.6.4).

![2013092815433350243.png](http://drops.javaweb.org/uploads/images/db2861b4a6bff23c133e69d61fa118e93313c6f5.jpg)

并且webserver对外开放.在基本探测后发现存在web漏洞。并且在获得webshell之后成功获取到了管理权限。

之后在webserver上查看到网关ip为172.10.0.1,试着ping一下.

![2013092815441991664.png](http://drops.javaweb.org/uploads/images/5ff71ff47a03e74a7a1c10f552926496acc407cd.jpg)

telnet上去看到是一台H3C设备。

![2013092815454135157.png](http://drops.javaweb.org/uploads/images/861b82303cd70ba2139332439c1dd7e77c4d3236.jpg)

尝试123456，password，manager等简单弱口令登陆，结果都失败。

尝试snmp弱口令探测(这里的弱口令是指snmp管理时用到的团体字符串。一般可读权限的为public,可读可写的默认为private).

![2013092815464552986.png](http://drops.javaweb.org/uploads/images/04c1619690126a49743982cd7fde1743d2daa9cd.jpg)

发现果真使用默认的可读团体字符串public.继续尝试使用snmp获取到H3C设备密码

![2013092815480084360.png](http://drops.javaweb.org/uploads/images/25874f08868badb9751e28be6dc9f7dde7aec64b.jpg)

成功的获取到密码”admin”(忘了说 我前面是故意没有试admin的)

之后便可以通过这个密码telnet登陆到交换机中.

![2013092815482781780.png](http://drops.javaweb.org/uploads/images/6f0aa2a5e92a568695b936270dd1f6eca0943520.jpg)

并成功的进入到system-view状态.

0x03 交换机下的渗透过程
--------------

* * *

在成功通过telnet登陆到交换机后我们便可以开始收集交换机的各种配置信息（vlan划分，super密码，路由表信息。Ip池划分等等）并且这些信息除了super密码以外基本都可以通过snmp的一个可读字符串获取到。而且对于思科设备来讲，如果有个可读可写的团体字符串，那么直接就可以下载到cisco的核心配置文件(含密码字符串等).

这里需要简单的说说三层交换机的两个功能,vlan划分以及端口镜像。端口指的是交换机上的端口,而不是计算机的服务端口。

端口镜像则是指将交换机某个端口下的数据镜像到另一个端口的技术，并且可以选择镜像流入或流出的数据包。这一技术通常应用在企业监控，流量分析中。在端口镜像时也应注意流量过高引发监视端口流量负载的问题。

这次测试便是通过端口镜像技术获取到dataserver发送和接受到的数据包。

我们先来分析下这台交换机的配置文件。

![2013092815514518027.png](http://drops.javaweb.org/uploads/images/908c74e6ebdc6b6ee5cf1b055e09de747d4c4486.jpg)

在这里我们可以看到super密码 这个密码通过H3C ciper加密。加密的字符串可以通过[https://github.com/grutz/h3c-pt-tools/blob/master/hh3c_cipher.py](https://github.com/grutz/h3c-pt-tools/blob/master/hh3c_cipher.py)这个脚本解密。

接下来看看ip-pool的划分,配合前期nslookup收集到的信息可以进一步清晰的逼近目标.

![2013092815534085900.png](http://drops.javaweb.org/uploads/images/4598c8a69cd7f38a11b845f7fd4a0144fc88da94.jpg)

根据上图可以发现我们现在处于vlan200中，目标处于vlan100,域控在300.

那么我们继续看看每个正在使用的接口被划分到了哪个vlan中。

![2013092815540635443.png](http://drops.javaweb.org/uploads/images/ccba3c30342f7029d4e8545babaf628457f12732.jpg)

这里可以看到 Ethernet 1/0/3在vlan100中.而Ethernet 1/0/4在vlan200中，也就是我们所处的vlan。

清楚接口划分之后我们开始建立一个本地镜像组1。

![2013092815543244451.png](http://drops.javaweb.org/uploads/images/c31772f15fd9b399762b2d8fa69d5076fa8e4726.jpg)

然后制定被镜像的端口号。

![2013092815545210434.png](http://drops.javaweb.org/uploads/images/1d8170007d00e2488110f7f2b28e6ec250cc4cf3.jpg)

接着制定监控端口号。

![2013092815552853736.png](http://drops.javaweb.org/uploads/images/dcd65792b0ebaa239f069942479657dadbfdb043.jpg)

最后登陆到我们控制的webserver.使用抓包软件分析目标（dataserver.tec503.com）的数据包.

这是捕获到目标（dataserver.tec503.com）ICMP数据包的示意图。

![2013092815555229947.png](http://drops.javaweb.org/uploads/images/70783956f8f0f9fca960ee75e5b7d1b7a130683c.jpg)

这是捕获HTTP数据包的示意图。

![2013092815561251295.png](http://drops.javaweb.org/uploads/images/4a007fddbfa60e17ed05f16d25a25271f9141109.jpg)

同理其他协议的包也应如此,具体的后续分析过程就不在这里演示了。

0x04 后记
-------

* * *

路由和交换机在渗透过程中越来越常见，并且由于管理员配置经验欠当。经常出现默认配置,弱口令等配置不当的问题。而且路由和交换机在网络中所处的位置也更加体现了它在一次渗透过程中的重要性.在写文章的时候也发现freebuf上的一篇关于跨vlan进行ARP嗅探的文章。([http://www.freebuf.com/articles/system/13322.html](http://www.freebuf.com/articles/system/13322.html)).也更希望通过这篇文章引出更多的好文章.

### 参考

H3C以太网交换机配置指南

wireshark抓包实战分析指南 第二版

[WooYun: 中国移动H3C防火墙侧漏利用snmp获取管理员密码成功登录设备](http://www.wooyun.org/bugs/wooyun-2013-032456)