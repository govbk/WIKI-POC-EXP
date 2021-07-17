# TCP安全测试指南-魔兽3找联机0day

在安全测试的过程中，我们通常使用应用层工具直接测试待测目标，比如一个HTTP网站应用程序，我们可以直接发送HTTP请求来对其进行模糊测试，而对于HTTPS，也可以建立SSL连接后直接发送HTTP请求对其进行模糊测试

然而在某些黑盒测试中，由于信息不对称，我们无法获悉应用层协议的具体格式，因此难以直接在应用层进行安全测试，这时我们需要对应用层协议本身进行FUZZ，这就需要使用更底层协议来进行安全测试

本文以著名的RTS游戏魔兽争霸3为例，介绍在网络层对TCP连接进行安全测试的基本工具、方法、以及漏洞挖掘思路

0x00 概述
=======

* * *

我想测试魔兽争霸3联机游戏的安全问题

然而魔兽争霸3并没有使用HTTP协议来进行通信，因此我既不能用burp来proxy拦截，也不能直接用curl等常用工具来进行FUZZ

魔兽争霸3联机对战使用了TCP连接，自己定义了一套数据包格式（已经有人分析过了，但在本文中我们假设数据包格式未知）

所以我要在传输层对魔兽争霸3的TCP连接进行安全测试，重点测试以下内容：

1.  断线重连
2.  网络的延迟与丢包
3.  TCP原始数据的嗅探/修改
4.  TCP连接的重放与交互式测试

0x01 断线测试
=========

* * *

由于魔兽争霸3并没有断线重连机制，所以TCP连接断开后会直接导致游戏断开，而在许多第三方对战平台上，玩家的离线等同于战败，因此也诞生了许多游戏“踢人”外挂

下面使用WooyunWifi路由器上的dsniff工具包中的tcpkill工具为例进行测试：

```
root@OpenWrt:~# tcpkill -i br-lan port 6112
tcpkill: listening on br-lan [port 6112]
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503812:2875503812(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504063:2875504063(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504565:2875504565(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503812:2875503812(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504063:2875504063(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504565:2875504565(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970133:2041970133(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970389:2041970389(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970901:2041970901(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503818:2875503818(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504069:2875504069(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504571:2875504571(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970133:2041970133(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970389:2041970389(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970901:2041970901(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503824:2875503824(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504075:2875504075(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504577:2875504577(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970142:2041970142(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970398:2041970398(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970910:2041970910(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503824:2875503824(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504075:2875504075(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504577:2875504577(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970151:2041970151(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970407:2041970407(0) win 0
192.168.1.163:6112 > 192.168.1.143:59892: R 2041970919:2041970919(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503830:2875503830(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504081:2875504081(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875504583:2875504583(0) win 0
192.168.1.143:59892 > 192.168.1.163:6112: R 2875503830:2875503830(0) win 0

```

![](http://drops.javaweb.org/uploads/images/b81249e3d21544519d251053998c93afaa599ac4.jpg)

这里演示的是全局切断，在实际应用场景中也可以使用包过滤表达式切断特定IP的连接

0x02 网络的延迟与丢包
=============

* * *

由于魔兽争霸3是一个实时对战的游戏，因此网络状态也会影响游戏的进行，魔兽争霸3本身对于实时操作的要求并不高，但是形如DOTA之类的自定义游戏模式对网络的延迟极为敏感，如果玩家在DOTA游戏中有很大延迟，可能会直接导致团灭并且游戏失败

下面使用WooyunWifi路由器上的tc工具中的netem内核模块为例进行测试：

```
tc qdisc add dev wlan0 root netem delay 1s

```

![](http://drops.javaweb.org/uploads/images/18fbcb96ecb51a6e75c4b1ee07ed9cc511819c31.jpg)

由于网络延迟，玩家控制的英雄在延时时间内无法响应玩家的操作

![](http://drops.javaweb.org/uploads/images/52020467a6b21e03309d8da2488fb32f6bb42191.jpg)

当然，您也可以用包过滤表达式指定任意ip的延时规则，包括随机浮动的延时时间

0x03 TCP原始数据的嗅探/修改
==================

* * *

如何嗅探TCP数据包已经是妇孺皆知的常识了，用wireshark或者tcpdump之类的都可以

至于如何修改TCP数据包，我推荐使用TCP透明代理模式来进行操作，原理其实和HTTP透明代理相似

至于工具我测试了3款，各有千秋：netsed简单实用少依赖，mitmproxy无比强大有扩展，bettercap则是替代ettercap的ruby工具

首先，我们在11对战平台上新建一个房间，然后打开wireshark，抓取war3的服务器端口（11对战平台使用的是服务器建主策略，并不是玩家建立主机，而是在服务器上有一个proxy专门用来与各个客户端通信）

![](http://drops.javaweb.org/uploads/images/fc9d83bb6bcc2acdb6647ca3006e4eb5bfa8c11e.jpg)

我们可以看到建主服务器ip为119.188.39.137，端口为2012，而聊天数据以及最开始交换用户名的数据都是明文的，而且后来测试发现也没有数据完整性验证

下面使用WooyunWifi路由器上的netsed工具为例进行测试：

```
iptables -t nat -A PREROUTING -p tcp --dport 2012 -j REDIRECT --to 10101

netsed tcp 10101 119.188.39.137 2012 s/lxj616/wooyun



netsed 1.2 by Julien VdG <julien@silicone.homelinux.org>
  based on 0.01c from Michal Zalewski <lcamtuf@ids.pl>
[*] Parsing rule s/lxj616/wooyun...
[+] Loaded 1 rule...
[+] Using fixed forwarding to 119.188.39.137,2012.
[+] Listening on port 10101/tcp.
[+] Got incoming connection from 192.168.1.163,53956 to 119.188.39.137,2012
[*] Forwarding connection to 119.188.39.137,2012
[+] Got incoming connection from 192.168.1.143,50527 to 119.188.39.137,2012
[*] Forwarding connection to 119.188.39.137,2012
[+] Caught client -> server packet.
[*] Forwarding untouched packet of size 771.
[+] Caught client -> server packet.
[*] Forwarding untouched packet of size 791.
[+] Caught server -> client packet.
[*] Forwarding untouched packet of size 24.
[+] Caught server -> client packet.
[*] Forwarding untouched packet of size 24.
[+] Caught client -> server packet.

```

于是整局游戏里lxj616都在其他用户眼里变成了wooyun，包括聊天和玩家列表

![](http://drops.javaweb.org/uploads/images/25eee29acd099be721cda1fa388ead19298cf968.jpg)![](http://drops.javaweb.org/uploads/images/398f06e7fe498445a44524d23aae2b8db925bbf6.jpg)

当然，netsed只有简单的替换功能，下面介绍一些更灵活的解决方案（不再以war3为例）

mitmproxy的官方示例介绍了如何修改TCP数据

```
https://github.com/mitmproxy/mitmproxy/blob/master/examples/tcp_message.py

```

下面使用Woobuntu系统上的mitmproxy工具为例进行测试：

![](http://drops.javaweb.org/uploads/images/1ef5349b3040997ac0ba2f142c7b4d786d5d4df4.jpg)

bettercap的官方示例介绍了如何修改TCP数据：

```
https://www.bettercap.org/docs/proxying/tcp.html#sample-module

```

下面使用Woobuntu系统上的bettercap工具为例进行测试：

注：tcp-proxy刚开始时显示未启动，后面在输出信息中后续启动的tcp-proxy

![](http://drops.javaweb.org/uploads/images/d58a3daba418690edd76169c811e86d5ce246120.jpg)

0x04 TCP连接的重放与交互式测试
===================

* * *

如果只是想要重放TCP的数据包本身而非TCP连接，使用tcpreplay工具直接重放即可，这种方式确实可以把之前抓取的pcap数据包全部重放到指定的interface上，这在测试一些IDS设备或者有抓包业务逻辑的应用时能起到预期的效果

下面使用Woobuntu系统上的tcpreplay工具为例进行测试：

```
tcpreplay -i enp0s3 test.pcap

```

![](http://drops.javaweb.org/uploads/images/4448a28e5563c6c3fd25e89be4616fc43975cf36.jpg)

然而仅仅重放抓取的数据包并不能建立有效的tcp连接，因此也不会被服务端正确的响应，这样就起不到FUZZ服务端应用的作用了，我们如果想要和服务端模拟一次真正的TCP会话，就必须在建立新连接后重新填写数据包对应的TCP序列号。形象的比喻一下就是你在重放HTTP请求时要修改你自己cookie里面的session-id

如果要重放tcp连接，可以使用tcpreplay系列工具中的tcpliveplay工具：

```
http://tcpreplay.appneta.com/wiki/tcpliveplay.html

```

不过我必须说这工具兼容性太差了，必须要按照官方文档中的Fresh Install Guide来配置特殊依赖，而且内核不可以用新版本，因此在Woobuntu 16.04上根本无法正常运行该工具

不过使用tcpliveplay并不是最好的办法，因为它的原理是解析并修改tcp协议包，而实际上我们的目标并不是解析并修改传输层的tcp协议包，我们只是要FUZZ上层应用，因此我们直接新建一个tcp连接，然后重放tcp承载的数据就可以了

下面以基于Ubuntu的Woobuntu系统为例进行测试，首先安装所需的tcptrace，以及可能需要的tcpslice

```
apt install tcptrace tcpslice

```

之后我们抓取我们想要重放的tcp数据包，这里我们用wireshark进行抓取，抓取的是玩家lxj616加入房间然后在聊天栏里面说了两句话整个过程

![](http://drops.javaweb.org/uploads/images/9aa3fd6b958e771a1f0b37f8cd24faba5f07b7b3.jpg)

您也可以在WooyunWifi路由器上通过tcpdump工具进行抓包

```
tcpdump -i br-lan dst port 6112 -C 100 -z "gzip" -w lxj616.pcap

```

抓完的包可能会很大，而路由器存储空间较小，所以设置了文件分段，分段的文件形如：

lxj616.pcap

lxj616.pcap1.gz

lxj616.pcap2.gz

（可选）我们可以把他们通过以下命令合在一起：

```
tcpslice -w full.pcap lxj616.pcap*

```

在抓到足够的数据包后，我们从中解析出各条tcp连接的数据：

```
tcptrace -e lxj616.pcap

1 arg remaining, starting with 'lxj616.pcap'
Ostermann's tcptrace -- version 6.6.7 -- Thu Nov  4, 2004

18 packets seen, 18 TCP packets traced
elapsed wallclock time: 0:00:00.027297, 659 pkts/sec analyzed
trace file elapsed time: 0:00:10.018743
TCP connection info:
  1: FullMatelErLuLu.lan:51416 - alkaid-PC.lan:6112 (a2b)   10>    8<

Warning : some extracted files are incomplete!
          Please see -l output for more detail.

```

这个警告是发现了不完整的TCP数据流，因为我测试时没点退出游戏就关闭抓包了

然后在当前目录下会生成形如a2b_contents.dat或者b2a_contents.dat的文件，找到哪一个是我们需要重放的流数据（同时注意数据方向）

最后我们来重放TCP连接请求测试：

```
cat a2b_contents.dat | nc 192.168.1.163 6112

```

![](http://drops.javaweb.org/uploads/images/ed483f4b7f422884afd4376fd822a4593c452954.jpg)

而对于游戏主机来说，确实看起来有玩家跑进来说了两句话

![](http://drops.javaweb.org/uploads/images/3007d4dbeb8879cb47536f8e4b0516c09498da16.jpg)

0x05 总结
=======

* * *

虽然在本文中对魔兽争霸3测试时发现了一些潜在问题，但都只是程序逻辑的小问题，而非安全性bug，因此在不会影响游戏平衡性的条件下，不需要把它们当做漏洞进行报送（虽然对于11对战平台而言，用户名是不可以修改的，但是你改了又能怎样，并没有用），写出本文来分享思路，供同道中人一起学习讨论