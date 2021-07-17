# WireShark黑客发现之旅（3）—Bodisparking恶意代码

作者：Mr.Right、Evancss、K0r4dji

申明：文中提到的攻击方式仅为曝光、打击恶意网络攻击行为，切勿模仿，否则后果自负。

0x00 发现
=======

* * *

接到客户需求，对其互联网办公区域主机安全分析。在对某一台主机通信数据进行分析时，过滤了一下HTTP协议。

![enter image description here](http://drops.javaweb.org/uploads/images/1945f1a18dfefa1a773173471c53a9a8d6f91c05.jpg)

一看数据，就发现异常，这台主机HTTP数据不多，但大量HTTP请求均为“Get heikewww/www.txt”，问题的发现当然不是因为拼音“heike”。点击“Info”排列一下，可以看得更清楚，还可以看出请求间隔约50秒。

![enter image description here](http://drops.javaweb.org/uploads/images/445cac0be5c1792982171f4de8fe1d06df506c99.jpg)

为更加准确地分析其请求URL地址情况，在菜单中选择Statistics，选择HTTP，然后选择Requests。可以看到其请求的URL地址只有1个：“d.99081.com/heikewww/www.txt”，在短时间内就请求了82次。

![enter image description here](http://drops.javaweb.org/uploads/images/be9af5ae41e918623ef4eab7c7e4db4b6def0af2.jpg)

这种有规律、长期请求同一域名的HTTP通信行为一般来说“非奸即盗”。

1.  奸：很多杀毒软件、APP、商用软件，为保持长连接状态，所装软件会定期通过HTTP或其它协议去连接它的服务器。这样做的目的可以提供在线服务、监控升级版本等等，但同时也可以监控你的电脑、手机，窃取你的信息。
2.  盗：木马、病毒等恶意软件为监控傀儡主机是否在线，会有心跳机制，那就是通过HTTP或其它协议去连接它的僵尸服务器，一旦你在线，就可以随时控制你。

我们再过滤一下DNS协议看看。

![enter image description here](http://drops.javaweb.org/uploads/images/21c54282772e46df8710dd64bad5f03089b9f373.jpg)

可以看出，DNS请求中没有域名“d.99081.com”的相关请求，木马病毒通信不通过DNS解析的方法和技术很多，读者有兴趣可以自行查询学习。所以作为安全监控设备，仅基于DNS的监控是完全不够的。

接下来，我们看看HTTP请求的具体内容。点击HTTP GET的一包数据，可以看到请求完整域名为“d.99081.com/heikewww/www.txt”，且不断去获得www.txt文件。

![enter image description here](http://drops.javaweb.org/uploads/images/9d0c02553ac5eb663ca370dd330d4f0b7b420915.jpg)

Follow TCPStream，可以看到去获得www.txt中的所有恶意代码。

![enter image description here](http://drops.javaweb.org/uploads/images/34ddd5f28d27049ed730222a7723f18337c8f889.jpg)

0x01 关联
=======

* * *

到这儿，基本确认主机10.190.16.143上面运行了恶意代码，它会固定时间同199.59.243.120这个IP地址（域名为d.99081.com）通过HTTP协议进行通信，并下载运行上面的/heikewww/www.txt。

那么，是否还有其它主机也中招了呢？

这个问题很好解决，前提条件是得有一段时间全网的监控流量，然后看看还有哪些主机与IP(199.59.243.120)进行通信，如果域名是动态IP，那就需要再解析。

1.  如果抓包文件仅为一个PCAP文件，直接过滤“ip.addr==199.59.243.120”即可。
2.  全网流量一般速率较高，想存为一个包的可能性不大。假如有大量PCAP文件，一样通过WireShark可以实现批量过滤。

下面我们就根据这个案例，一起了解一下WireShark中“tshark.exe”的用法，用它来实现批量过滤。

![enter image description here](http://drops.javaweb.org/uploads/images/b6af081e69f63857799111f1f0d3c03b2b71ec05.jpg)

Tshark的使用需要在命令行环境下，单条过滤命令如下：

```
cd C:\Program Files\Wireshark
tshark -r D:\DATA\1.cap -Y "ip.addr==199.59.243.120" -w E:\DATA\out\1.cap

```

解释：先进到WireShark目录，调用tshark程序，-r后紧跟源目录地址，-Y后紧跟过滤命令（跟Wireshrk中的Filter规则一致），-w后紧跟目的地址。

有了这条命令，就可以编写批处理对文件夹内大量PCAP包进行过滤。

通过这种办法，过滤了IP地址199.59.243.120所有的通信数据。

![enter image description here](http://drops.javaweb.org/uploads/images/2460d46d49d2fb2df99c0824a89bd5d27423704d.jpg)

统计一下通信IP情况。

![enter image description here](http://drops.javaweb.org/uploads/images/230c050f3afaf007143671c80d44338ba2f08f1c.jpg)

根据统计结果，可以发现全网中已有4台主机已被同样的恶意代码所感染，所有通信内容均一样，只是请求时间间隔略微不同，有的为50秒，有的为4分钟。

0x02 深入
=======

* * *

**1 恶意代码源头**

在www.txt中我们找到了“/Zm9yY2VTUg”这个URL，打开查看后，发现都是一些赞助商广告等垃圾信息。如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/e78d783e82ab6b5c78f89d132d259f1ffd9129e9.jpg)

通过Whois查询，我们了解到99081.com的域名服务器为ns1.bodis.com和ns2.bodis.com，bodis.com是BODIS, LLC公司的资产，访问其主页发现这是一个提供域名停放 （Domain Parking）服务的网站，用户将闲置域名交给它们托管，它们利用域名产生的广告流量和点击数量给用户相应的利益分成。

![enter image description here](http://drops.javaweb.org/uploads/images/650a7b7d80f66880a5d1125b7e7c2d453d60faef.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/735fe5631840b5eb0dd1dc513041fdcc60ae6d56.jpg)

**2 恶意代码行为**

经过公开渠道的资料了解到Bodis.com是一个有多年经营的域名停放服务提供商，主要靠互联网广告获取收入，其本身是否有非法网络行为还有待分析。

99081.com是Bodis.com的注册用户，即域名停放用户，它靠显示Bodis.com的广告并吸引用户点击获取自己的利润分成，我们初步分析的结果是99081.com利用系统漏洞或软件捆绑等方式在大量受害者计算机上安装并运行恶意代码访问其域名停放网站，通过产生大量流向99081.com的流量获取Bodis.com的利润分成。通常这种行为会被域名停放服务商认定为作弊行为，一旦发现会有较重的惩罚。

![enter image description here](http://drops.javaweb.org/uploads/images/764ec851235f798843d8006bbf794267619f3288.jpg)

**3 攻击者身份**

根据代码结合其它信息，基本锁定攻击者身份信息。下图为其在某论坛注册的信息：

![enter image description here](http://drops.javaweb.org/uploads/images/bd089a72c32b44247d5d83bde58374aed2945b24.jpg)

0x03 结论
=======

* * *

1.  攻击者通过非法手段利用域名停放网站广告，做一些赚钱的小黑产，但手法不够专业；
2.  攻击方式应是在通过网站挂马或软件捆绑等方式，访问被挂马网站和下载执行了被捆绑软件的人很容易成为受害者；
3.  恶意代码不断通过HTTP协议去访问其域名停放网站，攻击者通过恶意代码产生的流量赚钱。