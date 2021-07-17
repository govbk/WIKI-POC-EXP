# WireShark黑客发现之旅—肉鸡邮件服务器

0x00 背景
=======

* * *

肉鸡也称傀儡机，是指可以被黑客远程控制的机器。一旦成为肉鸡，就可以被攻击者随意利用，如：窃取资料、再次发起攻击、破坏等等。下面将利用WireShark一起学习一种肉鸡的用途：广告垃圾邮件发送站。

0x01 发现问题
=========

* * *

在对某企业服务器群进行安全检测时发现客户一台服务器（10.190.214.130）存在异常，从其通信行为来看应该为一台空闲服务器。 经过一段时间的抓包采集，对数据进行协议统计发现，基本均为SMTP协议。

![enter image description here](http://drops.javaweb.org/uploads/images/6b646e05638647ac47831a0a255965735acac04c.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/69ce8f0293b58bc73c38759ed23e6b3ff4b4db2b.jpg)

SMTP协议为邮件为邮件传输协议。正常情况下出现此协议有两种情况：

```
1、用户发送邮件产生。
2、邮件服务器正常通信产生。

```

该IP地址属于服务器，所以肯定非个人用户利用PC机发送邮件。

那这是一台邮件服务器？如果是，为什么仅有SMTP协议，POP3、HTTP、IMAP等等呢？

带着疑问我们统计了一下数据的IP、端口等信息：

![enter image description here](http://drops.javaweb.org/uploads/images/bb5ab67b510398d850b8f944903e2aca4f2684f7.jpg)

统计信息表明：所有通信均是与61.158.163.126（河南三门峡）产生的SMTP协议，且服务器（10.190.214.130）开放了TCP25端口，它的的确确是一台邮件服务器。

到这，很多安全分析人员或监控分析软件就止步了。原因是IP合理、逻辑也合理、SMTP协议很少有攻击行为，以为是一次正常的邮件通信行为。那么很可惜，你将错过一次不大不小的安全威胁事件。

职业的敏感告诉我，它不是一台合理的邮件服务器。这个时候需要用到应用层的分析，看一看它的通信行为。继续看看SMTP登陆过程的数据。

![enter image description here](http://drops.javaweb.org/uploads/images/a6938a671fe8c2c93ae41e86ee30c33989371dda.jpg)

从数据看出，邮箱登陆成功，右键Follow TCPStream可以看见完整登陆信息。

![enter image description here](http://drops.javaweb.org/uploads/images/cfb0d9862f8255188a4703501ebacfead6c57ed0.jpg)

```
334 VXNlcm5hbWU6          // Base64解码为：“Username:”
YWRtaW4=  //用户输入的用户名，Base Base64解码为：“admin”
334 UGFzc3dvcmQ6         //Base64解码为：“Password:”
YWRtaW4=  //用户输入的密码，Base Base64解码为：“admin”
235 Authentication successful.  //认证成功
MAIL FROM:<admin@system.mail>  //邮件发送自……

```

这段数据表明：61.158.163.126通过SMTP协议，使用用户名admin、密码admin，成功登陆邮件服务器10.190.214.30，邮件服务器的域名为@system.mail，且利用admin@system.mail发送邮件。

一看用户名、密码、邮箱，就发现问题了：

> 1、admin账号一般不会通过互联网登陆进行管理。
> 
> 2、“二货”管理员才会把admin账号设为密码。
> 
> 3、域名@system.mail与客户无任何关系。

很显然，这是一台被控制的邮件服务器—“肉鸡邮件服务器”。

0x02 行为跟踪
=========

* * *

发现问题了，下一步跟踪其行为，这个肉鸡服务器到底是干什么的。查看Follow TCPStream完整信息可发现：这是一封由admin@system.mail群发的邮件，收件人包括：www651419067@126.com、wyq0204@yahoo.com.cn、zhaocl1@163.com等10个人（带QQ的邮箱暂时抹掉，原因见最后），邮件内容不多。

![enter image description here](http://drops.javaweb.org/uploads/images/b4cb64c0346d92ef59ca8a2a2a1e7057a411045e.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/d1182a3f6e77aa3f9b12e78723e0d3f4c8abdb27.jpg)

为看到完整邮件内容，我们可以点击Save As存为X.eml，用outlook等邮件客户端打开。

![enter image description here](http://drops.javaweb.org/uploads/images/d484829fa9f06826050549e552d6d0bafb9e5409.jpg)

一看邮件，所有谜团都解开了。邮件内容就是一封“巧虎”的广告垃圾邮件，该服务器被攻击者控制创建了邮件服务器，用于垃圾邮件发送站。再用同样的方法还原部分其它邮件：

![enter image description here](http://drops.javaweb.org/uploads/images/38df7a54494fbd65b619d82e1e14acbceabe6c70.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/24193bc03edb6a3e29fe4955e45b918135155a76.jpg)

可以看出邮件内容完全一样，从前面图中可看出短时间的监控中SMTP协议有几十次会话，也就说发送了几十次邮件，涉及邮箱几百人。邮件中的域名http://url7.me/HnhV1打开后会跳转至巧虎商品的广告页面。

![enter image description here](http://drops.javaweb.org/uploads/images/61fa8fcbefebb21166a4b83d15c987d433b527fe.jpg)

0x03 分析结论
=========

* * *

> 1、该服务器经简单探测，开放了TCP25/110/445/135/3389/139等大量高危端口，所以被攻击控制是必然。
> 
> 2、该服务器已被控制创建了肉鸡邮件服务器（WinWebMail），邮件服务器域名为@system.mail，由61.158.163.126（河南省三门峡市）使用admin@system.mail用户登录，通过邮件客户端或专用软件往外发送垃圾邮件。
> 
> 3、简单百度一下，很多人会经常收到来自admin@system.mail的垃圾邮件，今天终于弄清了它的来龙去脉。
> 
> 4、垃圾邮件发送不是随便发的，是很有针对性的。巧虎是幼儿产品，从接受邮件的QQ号码中随便选取4位查询资料发现发送对象可能都为年轻的爸爸妈妈。

![enter image description here](http://drops.javaweb.org/uploads/images/6a90e525e55491feb13f2d8c3485ac35a5d8db90.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0703fa0f4c3c542044323e51488207685a0ebb0f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/dacf169d1ba947e1227981e55ce2e33ecb31c0f8.jpg)

申明：文章中出现IP、邮箱地址等信息均为安全监控、攻击防范学习交流所用，切勿用于其它用途，否则责任自负。

0x04 后续文章初步设计
=============

* * *

对于后续文章内容，初步设计WireShark黑客发现之旅--暴力破解、端口扫描、Web漏洞扫描、Web漏洞利用、仿冒登陆、钓鱼邮件、数据库攻击、邮件系统攻击、基于Web的内网渗透等。但可能会根据时间、搭建实验环境等情况进行略微调整。 （By：Mr.Right、K0r4dji）