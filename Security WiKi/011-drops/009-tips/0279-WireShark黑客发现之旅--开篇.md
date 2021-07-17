# WireShark黑客发现之旅--开篇

0x00 先说几句
=========

* * *

一看题目，很多朋友就会有疑问：市面上那么多的安全监控分析设备、软件，为什么要用WireShark来发现黑客和攻击行为？我想说的是WireShark目前作为最优秀的网络分析软件，如果用好了，比任何设备、软件都Nice。首先，它识别的协议很多；其次，WireShark其实具备很多分析功能；最主要的，它免费，既能采集又能分析，不丢包、不弃包。

我们虽然也接触了很多监控分析设备，但在分析中始终离不开WireShark的辅助，喜欢它的“诚实”，不忽悠、不遗漏，完完全全从原理上去认识数据。

本系列就是要抛开了各种所谓分析“神器”和检测设备，完全依靠WireShark从通信原理去发现和解密黑客的各种攻击行为。当然，仅是交流学习贴，不当之处请各位大神“轻喷”。

0x01 WireShark的常用功能
===================

* * *

介绍WireShark的书籍和文章比较多，本文就不献丑细讲了，一起了解一下部分常用的分析功能。

1、抓包捕获

菜单中选择Capture，选择Interface，然后选择需抓包的网卡。

![enter image description here](http://drops.javaweb.org/uploads/images/6f929ca3ca81b9a0c6e5db9286ee61dbb7881bea.jpg)

可以勾选网卡，点击Start开始抓包。如想连续抓包设置文件大小、定义存放位置、过滤性抓包，点击Options进行设置。

![enter image description here](http://drops.javaweb.org/uploads/images/6048868c090107f056d037172f8062a4f551c6df.jpg)

2、数据过滤

由于抓包是包含网卡所有业务通信数据，看起来比较杂乱，我们可以根据需求在Filter对话框中输入命令进行过滤。常用过滤包括IP过滤（如：ip.addr==x.x.x.x，ip.src== x.x.x.x,ip.dst== x.x.x.x）、协议过滤（如：HTTP、HTTPS、SMTP、ARP等）、端口过滤（如：tcp.port==21、udp.port==53）、组合过滤（如：ip.addr==x.x.x.x && tcp.port==21、tcp.port==21 or udp.port==53）。更多过滤规则可以在Expression中进行学习查询。

![enter image description here](http://drops.javaweb.org/uploads/images/2f927ee2035c39a04757940b521e27c761ec6490.jpg)

3、协议统计、IP统计、端口统计

协议统计：在菜单中选择Statistics，然后选择Protocol Hierarchy，就可以统计出所在数据包中所含的IP协议、应用层协议。

![enter image description here](http://drops.javaweb.org/uploads/images/65dd81cff6bd6bf84d3338f9f7ba898515632d88.jpg)

IP统计：在菜单中选择Statistics，然后选择Conversation，就可以统计出所在数据包中所有通信IP地址，包括IPV4和IPV6。

![enter image description here](http://drops.javaweb.org/uploads/images/2fa232bb3ff4182b44cea432980cd4e080607c19.jpg)

端口统计：同IP统计，点击TCP可以看到所有TCP会话的IP、端口包括数据包数等信息，且可以根据需求排序、过滤数据。UDP同理。

![enter image description here](http://drops.javaweb.org/uploads/images/b91025a01863273b680281f2ba2a49f17fd1bc5b.jpg)

4、搜索功能

WireShark具备强大的搜索功能，在分析中可快速识别出攻击指纹。Ctrl+F弹出搜索对话框。

Display Filter：显示过滤器，用于查找指定协议所对应的帧。

Hex Value：搜索数据中十六进制字符位置。

String：字符串搜索。Packet list：搜索关键字匹配的Info所在帧的位置。Packet details：搜索关键字匹配的Info所包括数据的位置。Packet bytes：搜索关键字匹配的内容位置。

![enter image description here](http://drops.javaweb.org/uploads/images/72072acbc8c16b29142b7764ae16373b477bc991.jpg)

5、Follow TCP Stream

对于TCP协议，可提取一次会话的TCP流进行分析。点击某帧TCP数据，右键选择Follow TCP Stream，就可以看到本次会话的文本信息，还具备搜索、另存等功能。

![enter image description here](http://drops.javaweb.org/uploads/images/7ab9d6336b6215553479fcc55b676073431dc7f0.jpg)

6、HTTP头部分析

对于HTTP协议，WireShark可以提取其URL地址信息。

在菜单中选择Statistics，选择HTTP，然后选择Packet Counter（可以过滤IP）,就可以统计出HTTP会话中请求、应答包数量。

![enter image description here](http://drops.javaweb.org/uploads/images/e14d83b447da4c45c7b4691300586a865307a3b4.jpg)

在菜单中选择Statistics，选择HTTP，然后选择Requests（可以过滤IP）,就可以统计出HTTP会话中Request的域名，包括子域名。

![enter image description here](http://drops.javaweb.org/uploads/images/9517daab945af675f409ec9dc9ef0a46880458fa.jpg)

在菜单中选择Statistics，选择HTTP，然后选择Load Distribution（可以过滤IP）,就可以统计出HTTP会话的IP、域名分布情况，包括返回值。

![enter image description here](http://drops.javaweb.org/uploads/images/fd6bbe9becfbdf8a327d062344e91d2762e0255e.jpg)

0x02 WireShark分析攻击行为步骤
======================

* * *

利用WireShark分析攻击行为数据，首先得具备一定的网络协议

知识，熟悉常见协议，对协议进行分层（最好分七层）识别分析。（如果不熟悉也没关系，现学现用也足够）。然后，需熟悉常见的攻击行为步骤、意图等等。画了张图，不太完善，仅作参考。

![enter image description here](http://drops.javaweb.org/uploads/images/4f42988858ee66c2417b63836f5d41668e38988d.jpg)

0x03 后续文章初步设计
=============

* * *

对于后续文章内容，初步设计WireShark黑客发现之旅--暴力破解、端口扫描、Web漏洞扫描、Web漏洞利用、仿冒登陆、钓鱼邮件、数据库攻击、邮件系统攻击、基于Web的内网渗透等。但可能会根据时间、搭建实验环境等情况进行略微调整。 （By：Mr.Right、K0r4dji）