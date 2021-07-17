# 一起针对国内企业OA系统精心策划的大规模钓鱼攻击事件

0x00 前言
-------

* * *

以下内容撰写于2014年6月26日上午，由于时间精力关系，当时只写了一半，搁置了大半个月，后来在乌云的一个帖子中发现了一模一样的大规模钓鱼行为（帖子内容见底下）。

在乌云疯狗、长短短等朋友的强烈建议下，将这篇文章整理了出来，由于过了大半个月，有些细节、逻辑已渐渐模糊、混淆，经过了一段时间的整理（可以看到文中穿插有不同时间的点评），进行了收尾完善。

这是一个精心策划的、大规模的、针对国内企业OA系统的批量钓鱼攻击行为！

同时，这也是对国内企业邮箱、OA系统大规模钓鱼攻击的一个预警！

具体预警见之后西安零日网络科技有限公司网络安全专家核攻击（核总）联合乌云漏洞报告平台发布的预警内容。

事件分析：

```
1、钓鱼者事先在互联网采集了大量企业、网站管理员、政府网站人员的邮箱地址。
2、钓鱼者事先在互联网扫描了大量存在弱口令的企业邮箱，进行大量钓鱼邮件群发（可以不进入垃圾箱）。
3、钓鱼者使用这些企业邮箱对采集到的邮箱地址进行大量钓鱼邮件群发，内容基本一致。
4、钓鱼者注册了几个域名，专门用作钓鱼收信。
5、这是一起针对国内企业OA系统精心策划的大规模钓鱼攻击事件。（APT攻击？）
6、目前尚不明确钓鱼者目的何在。（撒大网钓大鱼的节奏？）

```

以上分析来自西安零日网络科技有限公司网络安全专家核攻击（核总）。

0x01 意外收获
---------

* * *

核总早上收到一封钓鱼邮件，实际上每天都能收到一大堆钓鱼邮件，烦不胜烦，但是这封邮件比较有意思，跟随核总简单的分析一下它~

先来看看钓鱼邮件内容：

![enter image description here](http://drops.javaweb.org/uploads/images/98481d0abcdbc91f2346e29617da82b889443062.jpg)

邮件明文内容：

> 关于EMIS邮件服务升级的通知
> 
> 1.根据相关用户和员工反映：邮箱容量不够日常使用，邮箱登录使用存在卡顿的现象！ 2.为保证邮箱系统的稳定运行和正常使用，现在需要对部分邮箱进行升级测试！ 3.请收到此邮件的员工将个人信息发送到OA邮箱系统维护邮箱：admin@seveice.cn.com[admin@seveice.cn.com](mailto:admin@seveice.cn.com)
> 
> 格式如下：
> 
> 姓名：
> 
> 职位：
> 
> 员工编号：
> 
> 登陆地址：
> 
> 邮箱账号：
> 
> 邮箱密码：
> 
> 原始密码：
> 
> 电话和短号：
> 
> 备注：本次升级检测为期7-15天，为此给你带了不便的地方，敬请理解。为保证顺利升级，在接受到结束通知之前，请不要修改账号密码，谢谢配合！
> 
> * * *
> 
> 保密声明：本邮件及其所有附件仅发送给特定收件人。它们可能包含A企业的内部信息，秘密信息，专有信息或受到法律保护的其他信息。未经许可，任何人不得进行传播、分发或复制。此声明视为A企业的保密要求标识。若您误收本邮件，请立即删除或与邮件发送人联系。
> 
> CONFIDENTIALITY NOTICE: This e-mail and any attachments are intended for the addressee and may contain information belonging to ***|\_*_| which is privileged, confidential, proprietary, or otherwise protected by law. Without permission, any dissemination, distribution, or copying is prohibited. This notice serves as marking as CONFIDENTIAL information of ***|\_*_|. If you have received this communication in error, please delete immediately or contact the original sender.

内容看起来挺一本正经的么，钓鱼收集的信息挺全的么，括弧笑~

0x02 抽丝剥茧
---------

* * *

为了方便理解，我们从上往下按顺序分析吧（注意红框中的内容）。

1、service@2014-6-26.net，是一个以日期命名的、伪造的、不存在的域名。 2、**354@\_**|\_**|.com，百度了一下域名，是：\***|\***|

![enter image description here](http://drops.javaweb.org/uploads/images/cc79868cadc787ce647f1d564645bab063b44b41.jpg)

目测寡人和这个A企业木有任何关系，目测钓鱼者看寡人网名是核攻击，就弄了个A企业的邮箱增强真实性（也有可能只是为了用个正常域名，让邮件不进入垃圾箱？）（2014-7-14 18:10:08 补充：证明这个猜想正确！）（不排除A企业域名已被搞下，见后边的分析~）

继续看~

3、admin@seveice.cn.com，域名看起来挺正规的么，呵呵，先收集起来稍后分析，括弧笑~

4、红框中的内容：“……本次升级检测为期7-15天……在接受到结束通知之前，请不要修改账号密码，谢谢配合！”，请不要修改账号密码？Just 呵呵~你这后期渗透工作，动作也太慢了吧，居然需要7-15天，寡人一般最多一两天就完事了~

5、最底下的红框中的内容“……它们可能包含A企业的内部信息，秘密信息……” ，应该是邮件系统模板自带或页脚附加内容，制式化发送。

再来看看邮件原文（原始数据）：

> Received: from WebsenseEmailSecurity.com (unknown [219.**_._**.227]) by bizmx6.qq.com (NewMx) with SMTP id for[root@lcx.cc](mailto:root@lcx.cc); Thu, 26 Jun 2014 07:40:26 +0800 X-QQ-SSF: 005000000000000000K000010420600 X-QQ-mid: bizmx6t1403739626t7xszqhfx X-QQ-CSender:**354@***|\_*_|.com X-QQ-FEAT: h0yizCkM5mMZ/tU/FDOZge7cwU1MZMYVkeLy/yM35Sk= Received: from GH-ML-05.snpdri.com (unknown [172.17.1.9]) by Websense Email Security Gateway with ESMTPS id D2940D569E7 for[root@lcx.cc](mailto:root@lcx.cc); Thu, 26 Jun 2014 07:40:24 +0800 (CST) Sender: <**354@***|\_*_|.com> Message-ID: <887BFDC27B5F3D02FFFD3DFAF7A4B300@jyiia> From:[service@2014-6-26.net](mailto:service@2014-6-26.net)To:[root@lcx.cc](mailto:root@lcx.cc)Subject: =?utf-8?B?5YWz5LqOT0HnmbvpmYbljYfnuqfnmoTpgJrnn6U=?= Date: Thu, 26 Jun 2014 07:40:08 +0800 MIME-Version: 1.0 Content-Type: multipart/alternative; boundary="---|-=_NextPart_000_0957_01B53497.13B65610" X-Priority: 3 X-MSMail-Priority: Normal X-Mailer: Microsoft Outlook Express 6.00.2900.5512 X-MimeOLE: Produced By Microsoft MimeOLE V6.00.2900.5512 X-Originating-IP: [113.111.200.115]
> 
> ---|---|=_NextPart_000_0957_01B53497.13B65610 Content-Type: text/plain; charset="utf-8" Content-Transfer-Encoding: base64
> 
> 5YWz5LqORU1JU+mCruS7tuacjeWKoeWNh+e6p+eahOmAmuefpQ0KDQoxLuagueaNruebuOWFs+eU …… …… …… dD4NCjwvYm9keT4NCjwvaHRtbD4NCg==
> 
> ---|---|=_NextPart_000_0957_01B53497.13B65610--

从邮件原文头中能提取到很多有价值的信息，比如邮件发送者的IP地址：

```
219.***.***.227 中国北京市 电信

```

经过 IP 反查，确认这个 IP 地址为 “A企业” 邮件服务器的IP地址：mx.***|\_*_|.com(219.**_._**.227)，该 IP 地址目前可以 Ping 通~

（提示：A企业域名，www.***|\_*_|.com(219.**_._**.225)，以及视频会议服务器：219.**_._**.232，和邮件服务器都在一个c段的。）

也就是说，熊孩纸使用A企业的邮件服务器发送的，So，该服务器上会有登陆及发送日志，So~上门爆菊抓人~你懂的~

0x03 初探虎穴
---------

* * *

在官网看了看，发现了一点A企业网络基本构架：

```
<a href='http://219.***.***.232/' class='bt_link' title='视频会议' target=_blank></a>
<a href='http://www.******.com:8001/' class='bt_link' title='人才招聘' target=_blank></a>
<a href='https://mail.******.com/' class='bt_link' title='企业邮箱' target=_blank></a>
<a href='https://vpn.******.com/' class='bt_link' title='移动办公' target=_blank></a>

219.***.***.225(www.******.com)，官网
219.***.***.226(mail.******.com)，企业邮箱
219.***.***.227(mx.******.com)，邮件服务器
219.***.***.230(vpn.******.com)，移动办公
219.***.***.232(219.***.***.232)，视频会议

```

可以看到企业邮箱登陆域名，So，如果使用熊孩纸的账户“`**354@******.com`”登陆邮箱会如何呢？

于是核总经过前边的A企业网络基本构架摸排，顺利进入A企业邮箱登陆页面（mail.***|\_*_|.com）：

![enter image description here](http://drops.javaweb.org/uploads/images/89a1c243c58a42700acaa0b70a7e88597ddd29a9.jpg)

并使用之前的发件账号（**354@\***|\***|.co）与密码（123456）（2014-7-14 18:12:59 补充：现在密码已被修改！）成功登陆！

（旁白：登陆密码是核总瞎猜的，人品爆发，是吧~）

（2014-7-14 19:10:14 补充：事后这也证明一个观点：该犯罪团伙可能大规模扫描互联网中的企业邮箱弱口令，并进行利用，进行大规模邮件群发！而且如上边所述，邮件不会进入垃圾箱！）

![enter image description here](http://drops.javaweb.org/uploads/images/b0e45a3a662d028dbce3dc4b9adf30909cf35ddd.jpg)

发现这只是一个普通员工“张*”（可能已经离职，账户没有注销）的企业邮箱（2014-7-14 18:19:31 补充：企业邮箱是个大坑，国内各大厂商早该注意这个事情了！），而且密码是弱口令，看了下使用日志、收/发件箱，已经很久没用了~

> https://mail.***|\_*_|.com/
> 
> 账户：**354@\***|\***|.com 密码：123456
> 
> 账户资料：
> 
> 张仝
> 
> 帐户信息 - 张*
> 
> 一般信息
> 
> 显示名称: 张* 电子邮件地址: **354@\***|\***|.com
> 
> 联系号码
> 
> 工作电话: 移动电话:

核总已使用将所有邮件导出。（见之后的附件资料下载）

0x04 得来全不费工夫
------------

* * *

同时核总在该员工邮箱内发现数以千计的已发送的大规模钓鱼邮件！！！

![enter image description here](http://drops.javaweb.org/uploads/images/a7a12d76fd2809d6e2ae187d9a1578705ef38c94.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/47185464d2f28d7def6ce8b72a66530f909d34a5.jpg)

经过核总细细查阅，发现这些都是收件人地址不存在或其它各种原因导致发送失败的退信，或者收件人自动回复的邮件！

（旁白：核总已经所有邮件打包下载，为以后追踪提供资料研究！）

数量足有上千封，这仅仅只是几个小时内的接收量！

从时间间隔、退信比率以及自动回复比率计算，保守估计，该犯罪团伙已使用这个邮箱发送了至少上万份钓鱼邮件！

经过推测，该犯罪团伙所掌握的弱口令企业邮箱应该远远不止这一个，经过简单计算，其发送数量应该十分巨大！频率极高！

经过查阅退信邮件内容，发现都是发给各种网站管理员、各种企业员工、各类政府网站邮箱，种类繁多。

![enter image description here](http://drops.javaweb.org/uploads/images/889a59540cb84341525b648fa471d05bb3ef3a78.jpg)

经过分析，推测该犯罪团伙的邮件发送地址名单，应该是从搜索引擎搜索某类关键词批量采集的。

发送如此多的钓鱼邮件，目的不得而知。

邮件分析，暂且告一段落，再看看这个钓鱼邮件接收邮箱（admin@seveice.cn.com）是何方神圣。

0x05 深入敌后
---------

* * *

国际惯例，看看钓鱼邮件接收邮箱（admin@seveice.cn.com）的域名解析情况先~

![enter image description here](http://drops.javaweb.org/uploads/images/b8de4776e4c5b82e9e2a4fbcaae7fee6361cfb55.jpg)

```
C:>nslookup seveice.cn.com 服务器: UnKnown Address: 218.30.19.50

非权威应答: 名称: seveice.cn.com Address: 103.243.25.92

C:>nslookup www.seveice.cn.com 服务器: UnKnown Address: 218.30.19.50

非权威应答: 名称: www.seveice.cn.com Address: 103.243.25.92 

```

IP地址：103.243.25.92，归属地：

1、香港特别行政区

2、香港, 上海游戏风云公司香港节点

3、亚太地区

这个 IP 地址挺特别的，在很多地方查询都没有归属地记录。

再看看 ns 解析记录：

![enter image description here](http://drops.javaweb.org/uploads/images/735f4241ed332116d18b12fd03e166d120fad3bf.jpg)

```
C:\>nslookup -qt=ns seveice.cn.com
服务器:  UnKnown
Address:  218.30.19.50

非权威应答:
seveice.cn.com  nameserver = f1g1ns1.dnspod.net
seveice.cn.com  nameserver = f1g1ns2.dnspod.net

f1g1ns2.dnspod.net      internet address = 180.153.162.150
f1g1ns2.dnspod.net      internet address = 182.140.167.188
f1g1ns2.dnspod.net      internet address = 122.225.217.191
f1g1ns2.dnspod.net      internet address = 112.90.143.29
f1g1ns1.dnspod.net      internet address = 122.225.217.192
f1g1ns1.dnspod.net      internet address = 183.60.52.217
f1g1ns1.dnspod.net      internet address = 119.167.195.3
f1g1ns1.dnspod.net      internet address = 182.140.167.166

```

可以看出，该域名解析权限托管在 DNSPod，想抓人，找腾讯！（DNSPod由吴洪声创建，在2011年被腾讯全资收购~）

在看看 mx 邮件服务器解析记录：

![enter image description here](http://drops.javaweb.org/uploads/images/a86dd41c01e1ee3e6185f787883c537df801840a.jpg)

```
C:\>nslookup -qt=mx seveice.cn.com
服务器:  UnKnown
Address:  218.30.19.50

非权威应答:
seveice.cn.com  MX preference = 10, mail exchanger = mxdomain.qq.com

mxdomain.qq.com internet address = 183.60.62.12
mxdomain.qq.com internet address = 183.60.61.225
mxdomain.qq.com internet address = 183.62.125.200
mxdomain.qq.com internet address = 112.95.241.32
mxdomain.qq.com internet address = 112.90.142.55

```

可以看出，该域名使用的腾讯域名邮箱，还是那句话，想抓人，找腾讯！

再看看该域名历史解析的IP地址记录（IP反查网站接口 旁站查询 IP查域名 域名历史解析记录查询 IP地址查机房AS号）：

![enter image description here](http://drops.javaweb.org/uploads/images/371df13121a0bb420edd7ec903d5b1d0fb650364.jpg)

```
Site: http://seveice.cn.com
Domain: seveice.cn.com
Netblock Owner: 26C,No.666,Gonghexin road,Shanghai,China
               （上海共和新路666号中土大厦26C(上海鄂佳信息科技有限公司)）
Nameserver: f1g1ns1.dnspod.net
IP address: 103.243.25.92
DNS admin: freednsadmin@dnspod.com

Hosting History

Netblock owner: 26C,No.666,Gonghexin road,Shanghai,China
               （上海共和新路666号中土大厦26C(上海鄂佳信息科技有限公司)）
IP address: 103.243.25.92
OS: Windows Server 2003
Web server: Netbox v3.0 201005
Last seen Refresh: 3-Jul-2014
Last seen Refresh: 26-Jun-2014
Last seen Refresh: 14-Jul-2014

```

可以看到该域名的解析记录以及基本信息，如上所示。

Web Server 居然用的是 Netbox v3.0 201005？

直接访问这个 IP 地址看看

![enter image description here](http://drops.javaweb.org/uploads/images/502c4ab3b99942274c10bf31cda09a9d091fcecb.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/2ffd772b26180402c08d86b8442c7d02f11a8edb.jpg)

疑似一个QQ钓鱼站点？

再直接访问这个域名看看：

![enter image description here](http://drops.javaweb.org/uploads/images/10e504394081f161cc4ccd49731b69f8ff2fcd20.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/63dd23ffdf141cd21510c3b73bc61e875b91864d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/d7023d726e130da64aaa3bbaf2503a40b2efa25f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/10b1f7a0c3701832bcd612beba40d7cfa7789860.jpg)

发现是一个假冒 QQ 安全中心的钓鱼站点。

（核总吐槽：居然还是用的 Asp + Netbox v3.0 201005，太业余了吧~）

0x06 继续追查
---------

* * *

最后看看该域名的 Whois 信息：

> Domain ID:CNIC-DO2659321 Domain Name:SEVEICE.CN.COM Created On:2014-05-16T08:44:41.0Z Last Updated On:2014-05-28T04:00:35.0Z Expiration Date:2015-05-16T23:59:59.0Z Status:clientTransferProhibited Status:serverTransferProhibited
> 
> Registrant ID:TOD-43669078 Registrant Name:wu haitao Registrant Organization:wu haitao Registrant Street1:zhongqiangquanququa Registrant City:shizonggonghui Registrant State/Province:Henan Registrant Postal Code:808080 Registrant Country:CN Registrant Phone:+86.1083298850 Registrant Fax:+86.1083298850 Registrant Email:5777755@qq.com
> 
> Admin ID:TOD-43669079 Admin Name:wu haitao Admin Organization:wu haitao Admin Street1:zhongqiangquanququa Admin City:shizonggonghui Admin State/Province:Henan Admin Postal Code:808080 Admin Country:CN Admin Phone:+86.1083298850 Admin Fax:+86.1083298850 Admin Email:5777755@qq.com
> 
> Tech ID:TOD-43669080 Tech Name:wu haitao Tech Organization:wu haitao Tech Street1:zhongqiangquanququa Tech City:shizonggonghui Tech State/Province:Henan Tech Postal Code:808080 Tech Country:CN Tech Phone:+86.1083298850 Tech Fax:+86.1083298850 Tech Email:5777755@qq.com
> 
> Billing ID:TOD-43669081 Billing Name:wu haitao Billing Organization:wu haitao Billing Street1:zhongqiangquanququa Billing City:shizonggonghui Billing State/Province:Henan Billing Postal Code:808080 Billing Country:CN Billing Phone:+86.1083298850 Billing Fax:+86.1083298850 Billing Email:5777755@qq.com
> 
> Sponsoring Registrar ID:H3245827 Sponsoring Registrar IANA ID:697 Sponsoring Registrar Organization:ERANET INTERNATIONAL LIMITED Sponsoring Registrar Street1:02 7/F TRANS ASIA CENTRE 18 KIN HONG STREET KWAI CHUNG N.T Sponsoring Registrar City:Hongkong Sponsoring Registrar Postal Code:999077 Sponsoring Registrar Country:CN Sponsoring Registrar Phone:+85.235685366 Sponsoring Registrar Fax:+85.235637160 Sponsoring Registrar Website:http://www.now.cn/ Referral URL:http://www.now.cn/ WHOIS Server:whois.now.cn Name Server:F1G1NS1.DNSPOD.NET Name Server:F1G1NS2.DNSPOD.NET DNSSEC:Unsigned
> 
> > > > Last update of WHOIS database: 2014-07-14T11:42:10.0Z <<<
> 
> This whois service is provided by CentralNic Ltd and only contains information pertaining to Internet domain names we have registered for our customers. By using this service you are agreeing (1) not to use any information presented here for any purpose other than determining ownership of domain names, (2) not to store or reproduce this data in any way, (3) not to use any high-volume, automated, electronic processes to obtain data from this service. Abuse of this service is monitored and actions in contravention of these terms will result in being permanently blacklisted. All data is (c) CentralNic Ltd https://www.centralnic.com/

可以提取出很多重要信息，得知该域名注册者为：

```
域名：SEVEICE.CN.COM
创建时间：2014-05-16T08:44:41.0Z
最后更新：2014-05-28T04:00:35.0Z
过期时间：2015-05-16T23:59:59.0Z

姓名：wu haitao（吴海涛？）
组织：wu haitao（吴海涛？）
地址：zhongqiangquanququa（中枪全区去啊？）
城市：shizonggonghui（市总工会？）
州/省：Henan（河南）
邮政编码：808080
国家：CN
电话：+86.1083298850（百度一下会有惊喜）
传真：+86.1083298850（百度一下会有惊喜）
电子邮箱：5777755@qq.com（QQ：5777755，号码不错）

```

看来域名该注册没多久，刚刚满一月多~

QQ：5777755，号码不错：

![enter image description here](http://drops.javaweb.org/uploads/images/f49fd1092c30dc452f28d71f08d51509f5ad251f.jpg)

百度了一下：1083298850

![enter image description here](http://drops.javaweb.org/uploads/images/4fefdeb10e2a53ab57a195e790e944bb965ca2e9.jpg)

搜索了一下 www.hk6h.net，发现是个香港六合彩赌博网站。

0x07 铁证如山
---------

* * *

又在爱站进行了 Whois 反查，发现还注册了另外一个域名：

（2014-7-14 20:27:02 补充：后来发现此人注册了一大堆各种域名，各类黑产都做，感兴趣的朋友可以自行搜索~）

> 域名：tccmtce.com 解析地址：142.0.135.52（美国）
> 
> 名称服务器：F1G1NS1.DNSPOD.NET 名称服务器：F1G1NS2.DNSPOD.NET
> 
> 创建时间：2014-05-17 T 16:17:38Z 过期时间：2015-05-17 T 16:17:38Z 更新时间：2014-06-02 T 10:51:35Z
> 
> 城市：shizonggonghui 国家：CN 电子邮箱：5777755@qq.com 传真：86.1083298850 产品名称：wu haitao（吴海涛） 组织：wu haitao（吴海涛） 电话：86.1083298850 邮编：808080 州/省：shizonggonghui 街道：zhongqiangquanququa
> 
> 投诉联系邮箱：abuse@72e.net 投诉联系电话：+86.75788047236 介绍网址：http://www.72e.net Whois服务：whois.72dns.com 注册地：Foshan YiDong Network Co.LTD （佛山市屹东网络有限公司）

可以看出来这个域名的注册信息和之前的域名一摸一样，注册时间也十分相近~

后经证实，这个域名也是用来群发邮件的一个钓鱼接收邮箱（admin@tccmtce.com）（出自乌云的一个帖子，具体内容见底下）。

由于时间精力有限，暂且追踪到这里，感兴趣的朋友可以深挖。

以上分析来自西安零日网络科技有限公司网络安全专家核攻击（核总）。

乌云发现的钓鱼帖子内容：

[这是一次精心布置的“广撒网钓大鱼”攻击么？](http://zone.wooyun.org/content/13710)

相关下载：

[2014电子商务安全技术峰会.rar](http://pan.baidu.com/s/1mgjyjX2)（见其中的：十年防泄密的那些事儿-吴鲁加.pdf）