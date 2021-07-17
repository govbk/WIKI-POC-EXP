# linux ddos恶意软件分析

0x00
====

* * *

好久没写文章了,正好吃完饭回来习惯性的翻翻twitter,一篇文章写的真是行云流水不翻译来真是可惜。  
废话不多说，这篇文章是一个针对恶意软件"Linux/XOR.DDoS" 感染事件分析，该恶意软件试图感染真正的linux服务器。原文：http://blog.malwaremustdie.org/2015/06/mmd-0033-2015-linuxxorddos-infection_23.html  

0x01 背景：
========

* * *

事件细节：

攻击源：通过某种方式监控来到攻击来源107.182.141.40，可以看到这个ip的一些具体信息。

```
"ip": "107.182.141.40",
"hostname": "40-141-182-107-static.reverse.queryfoundry.net",
"city": "Los Angeles",
"region": "California",
"country": "US",
"loc": "34.0530,-118.2642",
"org": "AS62638 Query Foundry, LLC",
"postal": "90017",
"phone": "213"

```

攻击者登录通过ssh密码登录一台linux：

```
[2015-06-23 01:29:42]: New connection: 107.182.141.40:41625
[2015-06-23 01:29:42]: Client version: [SSH-2.0-PUTTY]
[2015-06-23 01:29:43]: Login succeeded [***/***]

```

然后通过shell执行了如下命令：

![Alt text](http://drops.javaweb.org/uploads/images/aa4130fe931f528e614fb366ae737653557fcf16.jpg)

然后恶意软件启动命令在受感染机器上执行。

![Alt text](http://drops.javaweb.org/uploads/images/ec29af023a27221f01cfc9e151fd5d26e4a7968f.jpg)

攻击者使用的Web服务器（域：44ro4.cn）面板截图，当时采取的攻击执行步骤。

![Alt text](http://drops.javaweb.org/uploads/images/bf373f0d333227cbdc7fc068a3a9c0b955ca432b.jpg)

这个web上的ip信息：

```
"ip": "198.15.234.66",
"hostname": "No Hostname",
"city": "Nanjing",
"region": "Jiangsu",
"country": "CN",
"loc": "32.0617,118.7778",
"org": "AS11282 SERVERYOU INC",
"postal": "210004"

```

通过dig 发现该ip的一些附加域信息：

```
;; QUESTION SECTION:
;44ro4.cn.                      IN      A

;; ANSWER SECTION:
44ro4.cn.               600     IN      A       23.228.238.131
44ro4.cn.               600     IN      A       198.15.234.66

;; AUTHORITY SECTION:
44ro4.cn.               3596    IN      NS      ns2.51dns.com.
44ro4.cn.               3596    IN      NS      ns1.51dns.com.

```

下边是更多的证据：

![Alt text](http://drops.javaweb.org/uploads/images/634ee700ccc5ac73b223bb5c6e6b68805b8f61f0.jpg)

0x02 感染的方法，伪装和总结
================

* * *

通过进一步研究恶意软件，该软件看起来像是ZIP压缩文件的恶意软件，从文件格式上看出像是一个shell脚本的恶意软件安装程序见下图：

![Alt text](http://drops.javaweb.org/uploads/images/00c55f2ddd239cd3269ab0b7de10d6a63374fdad.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/e0c7e1830738e6ce30a2aac51751d495bb920cc8.jpg)

这是Linux/XorDDOSs，这种恶意软件的感染后使作为BOT被感染的机器，远程控制的恶意程序，配置，拒绝IP，程序和配置。他们使用的是XOR'ed加密通信，发送预先与MD5编码过程。该恶意软件的精灵的主要功能是为一个隐形的DDoS攻击的僵尸网络。

这一事件的重要亮点和恶意软件使用：

1.  我们使用用于此恶意软件感染的基础设施 (攻击者的IP来自美国主机，一个IP用于感染)
2.  总在Linux/XorDDOSs，多个主机的使用：四数控系统。三的人建议是硬编码在主机名（有相关的领域），从被感染的机器接收回调，而其中的主机充当下载服务器被感染的机器要求后门下载可疑的恶意文件。
3.  异或加密功能是用现在解密滴，读取配置文件从远程主机下载（是的，它似乎被下载的配置文件），并发送通信数据。

这里是poc：

这些是cnc 与kernel的交互信息，这里用到了调试神器strace.

![Alt text](http://drops.javaweb.org/uploads/images/495e2550d2bd31625ffbefc93a9445a084d7ce67.jpg)

通过恶意软件交互分析到的dns请求：

![Alt text](http://drops.javaweb.org/uploads/images/cc48662d1f1032decc39eb768993cf9f6ef06344.jpg)

tcpdump中的timestamp时间戳。

```
08:21:20.078878 IP mmd.bangs.xorddos.40274 > 8.8.8.8: 27458+ A? aa.hostasa.org. (32)
08:21:20.080602 IP mmd.bangs.xorddos.38988 > 8.8.8.8: 44387+ A? ns4.hostasa.org. (33)
08:21:25.092061 IP mmd.bangs.xorddos.45477 > 8.8.8.8: 58191+ A? ns3.hostasa.org. (33)
08:21:25.269790 IP mmd.bangs.xorddos.51687 > 8.8.8.8: 22201+ A? ns2.hostasa.org. (33)

```

和cnc(hostasa.org)建立连接，注意它使用google dns的方式：

![Alt text](http://drops.javaweb.org/uploads/images/f503208a4d889560930591999e98f8cbf5675789.jpg)

cnc（hostasa.org）回调都是加密的，这是在2个独立的地方初步回调。

![Alt text](http://drops.javaweb.org/uploads/images/2246926211bd5ab98724be726861a1cf8a205e37.jpg)

通过解密它的请求，这里记录了一些解密图：

![Alt text](http://drops.javaweb.org/uploads/images/de4e3b6cfe48e3310733c9a4d728d88ffa44bab9.jpg)

这里是代码中通讯二进制编码部分：

![Alt text](http://drops.javaweb.org/uploads/images/1fdb8496868960892715326af9ba129a7e77ade5.jpg)

下载者：

![Alt text](http://drops.javaweb.org/uploads/images/be51742f4ccb4ea45e19df5fb2ee4e8108553ab0.jpg)

这里是下载函数硬编码在二进制里

![Alt text](http://drops.javaweb.org/uploads/images/c9c6c6699f69347dd5177782831fcae68ffd602d.jpg)

也有确凿的证据在wireshark抓包通信中，如图：

![Alt text](http://drops.javaweb.org/uploads/images/6bf29b9bf3e92936fed0fb174ee73f369e33682b.jpg)

0x03 有趣的事实
==========

* * *

这些都是用恶意软件项目的源代码文件，它是Linux/xor.ddos集编译设置（在C语言中，没有"+"。）作者很无耻的收藏了，这里我帮他翻译下。

![Alt text](http://drops.javaweb.org/uploads/images/c25a5e16edc3c59b9a5a02c7ef37b9da393f55fc.jpg)

恶意软件的脚本在二进制中编码，这是通用的很多恶意软件在中国制造。

![Alt text](http://drops.javaweb.org/uploads/images/039e8d2e71f12fab2cb797b0ecbdbfa46d997bc5.jpg)

发现XOR加密运行安装程序和"据说"用于解密的配置数据，在样本我破解的关键是BB2FA36AAA9541F0

![Alt text](http://drops.javaweb.org/uploads/images/6c0ee0bf71a68db180041bd83f41b2ef87e47314.jpg)

这是自我复制的恶意软件的安装文件，使用逆向工具追踪代码，可以看到这里：

![Alt text](http://drops.javaweb.org/uploads/images/dba0f16290f398a7a463694ccccb5d0f8b944a27.jpg)

和这里：

![Alt text](http://drops.javaweb.org/uploads/images/e0e7f1f5e27dbb13971723d3ae2a5ca238067a93.jpg)

acl功能，拒绝访问的ip，来保护受感染的主机。

![Alt text](http://drops.javaweb.org/uploads/images/e5e3ad62a6c2de9614c85b98614df87c478072ee.jpg)

0x04 对于恶意软件作者追踪
===============

* * *

通过逆向分析得到的数据，cnc使用的dns记录在下边：

```
;; ANSWER SECTION:
aa.hostasa.org. 300 IN  A   23.234.60.143
ns2.hostasa.org.300 IN  A   103.240.140.152
ns3.hostasa.org.300 IN  A   103.240.141.54
ns4.hostasa.org.300 IN  A   192.126.126.64

;; AUTHORITY SECTION:
hostasa.org.3600IN  NS  ns4lny.domain-resolution.net.
hostasa.org.3600IN  NS  ns1cnb.domain-resolution.net.
hostasa.org.3600IN  NS  ns3cna.domain-resolution.net.
hostasa.org.3600IN  NS  ns2dky.domain-resolution.net.

;; ADDITIONAL SECTION:
ns3cna.domain-resolution.net. 2669 IN   A   98.124.246.2
ns2dky.domain-resolution.net. 649 INA   98.124.246.1
ns1cnb.domain-resolution.net. 159 INA   50.23.84.77
ns4lny.domain-resolution.net. 2772 IN   A   98.124.217.1

```

经过分析，活着的cnc（hostasa.org）服务器在美国。

```
"ip": "23.234.60.143",
"hostname": "No Hostname",
"city": "Newark",
"region": "Delaware",
"country": "US",
"loc": "39.7151,-75.7306",
"org": "AS26484 HOSTSPACE NETWORKS LLC",
"postal": "19711"

"ip": "192.126.126.64",
"hostname": "No Hostname",
"city": "Los Angeles",
"region": "California",
"country": "US",
"loc": "34.0530,-118.2642",
"org": "AS26484 HOSTSPACE NETWORKS LLC",
"postal": "90017"

```

其他的cnc（hostasa.org）服务器在香港。

```
"ip": "103.240.140.152",
"hostname": "No Hostname",
"city": "Central District",
"country": "HK",
"loc": "22.2833,114.1500",
"org": "AS62466 ClearDDoS Technologies"

"ip": "103.240.141.54",
"hostname": "No Hostname",
"city": "Central District",
"country": "HK",
"loc": "22.2833,114.1500",
"org": "AS62466 ClearDDoS Technologies"

```

域名hostasa.org无法证明是用于恶意目的的怀疑，3台主机看起来像一个DNS服务器，下面是注册的数据来自Name.com那里注册.org，与隐私保护：

```
Domain Name:"HOSTASA.ORG"
Domain ID: 2D175880649-LROR"
"Creation Date: 2015-03-31T06:56:01Z
Updated Date: 2015-05-31T03:45:36Z"
Registry Expiry Date: 2016-03-31T06:56:01Z
Sponsoring Registrar:"Name.com, LLC (R1288-LROR)"
Sponsoring Registrar IANA ID: 625
WHOIS Server:
Referral URL:
Domain Status: clientTransferProhibited -- http://www.icann.org/epp#clientTransferProhibited
Registrant ID:necwp72276k4nva0
Registrant Name:Whois Agent
Registrant Organization:Whois Privacy Protection Service, Inc.
Registrant Street: PO Box 639
Registrant City:Kirkland
Registrant State/Province:WA
Registrant Postal Code:98083
Registrant Country:US
Registrant Phone:+1.4252740657
Registrant Phone Ext:
Registrant Fax: +1.4259744730
Registrant Fax Ext:
Registrant Email:hostasa.org@protecteddomainservices.com
Tech Email:hostasa.org@protecteddomainservices.com
Name Server:NS3CNA.DOMAIN-RESOLUTION.NET
Name Server:NS1CNB.DOMAIN-RESOLUTION.NET
Name Server:NS2DKY.DOMAIN-RESOLUTION.NET
Name Server:NS4LNY.DOMAIN-RESOLUTION.NET
DNSSEC:Unsigned

```

此外，所使用的44ro4.cn域，这是DNS指向恶意的payload的Web页面，这不是巧合，这是注册在下面的QQ ID和名称（可能是假的）：

```
Domain Name: 44ro4.cn
ROID: 20141229s10001s73492202-cn
Domain Status: ok
Registrant ID: ji27ikgt6kc203
Registrant: "蔡厚泉 (Cai Hou Sien/Quan)"
Registrant Contact Email: "2511916764@qq.com"
Sponsoring Registrar: 北京新网数码信息技术有限公司
Name Server: ns1.51dns.com
Name Server: ns2.51dns.com
Registration Time: 2014-12-29 10:13:43
Expiration Time: 2015-12-29 10:13:43
DNSSEC: unsigned

```

PS：CNNIC有更多这样的注册信息，我把自由查询他们找到这个骗子用的和其他身份的几个可怜的cn域名，相同和不同的名字下，在同一个QQ：

```
Domain   RegistrantID     Name
------------------------------
n1o9n.cn ej55v35357p95m   沈涛
u7ju0.cn ej55v35357p95m   沈涛
568b5.cn ej55v35357p95m   沈涛
93t9i.cn ej55v35357p95m   沈涛
5ntdu.cn ej55v35357p95m   沈涛
v90b8.cn ej55v35357p95m   沈涛
av732.cn ej55v35357p95m   沈涛
iqny7.cn ej55v35357p95m   沈涛
ewkp7.cn ej55v35357p95m   沈涛
8vu55.cn ji27ikgt6kc203   蔡厚泉
tj17e.cn ej55v35357p95m   沈涛
o88pn.cn ji27ikgt6kc203   蔡厚泉

```

通过进一步的分析，发现如下信息和域名所有者信息相吻合。

![Alt text](http://drops.javaweb.org/uploads/images/5c4fa30d41266cffd932e637878bd9f1aa8393c6.jpg)

看起来这个域名所有者是住在，住在附近的潭溪公交站在三元里街头，白云区，广州地区，中华人民共和国，按照该地图描述：

![Alt text](http://drops.javaweb.org/uploads/images/4bec731acf1cee03facb19b1b6485bf11b30ee5c.jpg)

###### ####注：文中的cnc处(就是HOSTASA.ORG)