# Google DNS劫持背后的技术分析

0x00 背景
-------

* * *

最近世界真是越来越不太平了，尤其是对于大部分普通人而言。昨天又传来噩耗，根据网络监测公司BGPMon，Google的公开DNS服务器 IP 8.8.8.8被劫持到了委内瑞拉和巴西超过22分钟。

Google DNS 服务器平均每天处理超过1500亿个查询，在被劫持的22分钟里起码几百万个查询包括金融系统，政府和个大商业网站的DNS查询流量都被劫持走了。

![enter image description here](http://drops.javaweb.org/uploads/images/eaace8de677fbf8745d0e25a67ea15c7fc7835bd.jpg)

根据砖家们的推测，这次劫持可能是黑客利用了Border Gateway Protocol(BGP) 协议中一个众所周知的漏洞来实现的，BGP协议为ISP级的路由协议，一般用来协调大型ISP之间的路由走向。这次劫持可以让黑客把网上的部分流量劫持从而经过他们所控制的路由。

![enter image description here](http://drops.javaweb.org/uploads/images/cd7c5c80df6bb1ca44b86d28ce44d2b3620e51ca.jpg)

这已经不是Google DNS服务器被第一次劫持了，在2010年也Google DNS的流量也曾经被劫持到了罗马尼亚和奥地利境内。

BGP劫持攻击是一种大规模的中间人攻击，并且较难发现，因为数据包的最终目的地并没有变，只是绕了下路而已。

0x01 BGP劫持详解
------------

* * *

本部分来源于Tony Kapela 和 Alex Pilosov在2008年 Defcon会议上的演讲。

### 什么是BGP

首先互联网整体上来说是一个分布式的网络，并没有整个网络的中心。但是整个互联网实际上是由成百上千个不同的ISP的子网络组成的。

这些子网络互相连接，通过BGP协议告诉对方自己子网络里都包括哪些IP地址段，自己的AS编号（AS Number）以及一些其他的信息。

这里又要扯到互联网的IP地址分配方式。互联网的IP地址分配是中心化的，ICANN这个机构把IP地址大段分给Regional Internet Registries（RIR），区域互联网注册管理机构。RIR再把IP地址段细分后分给ISP们。

大部分情况下，AS Number和分给该AS什么IP段是没有任何关系的。

下面问题来了，BGP协议里虽然有一些简单的安全认证的部分，但是对于两个已经成功建立BGP连接的AS来说，基本会无条件的相信对方AS所传来的信息，包括对方声称所拥有的IP地址范围。

对于ISP分配给大公司客户的地址段，ISP往往会对BGP做一些有限的过滤。但是对于大型ISP来说，因为对方所拥有的IP地址段可能过于分散，所以一般是按最大范围设置BGP prefix 地址过滤。比如假设ISP A拥有地址段20.1.0.0/16和20.200.0.0/16，那么ISP B可能会设置过滤对方传来的20.0.0.0/8以外的路由。

当然这种情况比较极端，一般ISP分配到的IP地址段都是连续的，但是基本也都有可操作的空间，可以把数百到几万个不属于自己的IP合法加到自己的BGP信息里。

多数ISP甚至都没有把自己本身的IP段过滤掉，也就是说如果其他AS声称拥有该ISP自己的IP段，这个ISP的BGP路由也会相信。

为了解决这个问题，有人发明了一个叫Internet Routing Registry (IRR)的东西，相当于一个开放式的数据库，像DNS 根服务器一样采用分布式镜像服务器放在世界各地。

ISP可以向IRR注册自己的IP地址段和路由策略，其他ISP就可以查询IRR从而对自己的BGP路由器做过滤。这样做的确防止了一些由于无意而导致的路由劫持。

但是IRR这个东西本身也是不靠谱的。IRR里存了大约10万条记录，如果全部加载进路由器的话是个不小的负担。另外IRR基本没人管，任何人可以可以往里面注册任何路由记录。

所以在大部分ISP都无条件相信IRR的时代，IRR也带来了不少的麻烦。

最简单的方式就是通过Whois找到目标IP段的 管理员邮箱，如果该邮箱或者邮箱所在的域名已经过期，那么就自己注册一个，然后就可以随便通过邮件向IRR修改记录了。

或者直接通过BGP路由向ISP发送，反正大家都不care……

### 实际案例

现在我们来看一个Youtube被劫持的案例:

youtube有5个网段，其中一个是

```
208.65.152.0/22  

```

因为觉得Youtube不和谐，于是巴基斯坦政府决定封锁Youtube。

巴基斯坦电信在路由器上加了条static route把

```
208.65.153.0/24

```

弄到了null0接口（GFW之黑洞路由大法）

巴电信的工程师手抖把static route redistribute到BGP了(Cisco路由器上同步不同协议路由表的方法)，也就是说把该路由器上的静态路由表添加到BGP的路由表了，静态路由同步到其他路由表里的优先值最高。

BGP把这条路由向其他AS的路由器同步了，最先中枪的是香港的电讯盈科（PCCW），然后接着被逐渐同步到了全世界。

这时互联网的大部分用户想上Youtube的时候数据包都跑到巴基斯坦了，结果当然是打不开了（因为进来就被弄到null0了）。

Youtube发现后重新用BGP声明了对该IP段和其他IP段的所有权，成功刷新了部分ISP路由器的路由表。

两小时后PCCW断开了和巴基斯坦电信路由器的BGP连接。3-5分钟后，一切恢复正常，除了苦逼的巴基斯坦用户们。

这意味着只要控制了任何一个ISP的任何一个BGP路由，都将具备影响全世界互联网的能力。

BGP劫持很难被发现，如果不是因为巴基斯坦电信把youtube的IP段转发到了null0接口，数据包就只会在巴基斯坦网络里绕一圈然后再到达Youtube。

如果攻击者的路由器具备篡改TTL的功能，那么即使通过traceroute也很难发现数据包被劫持，唯一的方法就是像前面所说的BGPmon那样检测全世界范围内的AS路由表和BGP信息。

### BGP劫持理论

当我们控制了ISP的BGP路由后，像平常一样发送路由信息。通过修改AS Path等BGP信息，让其他AS认为你到目标网络的距离最短。

为了让回来的数据包也经过你的路由器，你需要记录trace route到目标网络的时候都会经过哪些AS。

使用AS-PATH prepend list包括这些AS Number

设置static route到traceroute出现的第一个ASN

#### 详解：

目标IP段

```
10.10.220.0/22

```

在AS 200中  
ASN 200向相邻的AS 20和30发送BGP通告。  
此时为正常的状态。

![2014031815415353677.png](http://drops.javaweb.org/uploads/images/fec958ccaac296e935e43369bbcb95f6c8cce3f9.jpg)

攻击者控制了AS 100的BGP路由。

AS 100的路由表和BGP表显示到达

```
10.10.200.0/22

```

需要经过 AS 10.

于是我们把AS10，20和200加入我们的AS PATH prepend list

![2014031815423285580.png](http://drops.javaweb.org/uploads/images/7f40577604459a6af54da3351396ecda256428cf.jpg)

通过route-map把目标IP段加入BGP路由表

```
10.10.220.0/24 is announced with a route-map:  
route-map hijacked permit 10  
match ip address prefix-list jacked  
set as-path prepend 10 20 200  

```

然后在AS100的路由器中加入static route，把流向目标IP段的数据包指向AS10

```
ip route 10.10.220.0 255.255.255.0 4.3.2.1 

```

![2014031815431276804.png](http://drops.javaweb.org/uploads/images/d6a19a966a896f56345b0606240efb6b1df9edfa.jpg)

完成后可以看出，AS30 40 50 60的数据包如果想要到AS 200去，都会先经过AS 100.

到了这里我们已经可以分析出，BGP劫持的本质再次回到安全的本质既是信任这一点，因为BGP直接无条件信任对方AS发来的路由信息，并且缺乏有效的认证和过滤手段，导致BGP劫持屡次得手。