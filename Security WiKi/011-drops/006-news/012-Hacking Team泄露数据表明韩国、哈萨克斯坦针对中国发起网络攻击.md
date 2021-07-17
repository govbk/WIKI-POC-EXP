# Hacking Team泄露数据表明韩国、哈萨克斯坦针对中国发起网络攻击

0x00 背景
=======

* * *

Hacking Team是一家在意大利米兰注册的软件公司，主要向各国政府及法律机构销售入侵及监视功能的软件。其远程控制系统可以监测互联网用户的通讯、解密用户的加密 文件及电子邮件，记录Skype及其它VoIP通信，也可以远程激活用户的麦克风及摄像头。其总部在意大利，雇员40多人，并在安纳波利斯和新加坡拥有分支机构，其产品在几十个国家使用。

7月5日晚，Hacking Team服务器被攻击，其掌握的400GB数据泄露出来，由此引发的动荡，引起了业界一片哗然，里面有Flash 0day, Windows字体0day, iOS enterprise backdoor app, Android selinux exploit, WP8 trojan等等核武级的漏洞和工具，其远程控制系统可以突破系统默认以及杀毒软件的安全防护，后台监控用户的网络通讯、解密用户的加密文件及电子邮件，记录Skype和其它VoIP工具的聊天内容，以及远程激活用户的麦克风及摄像头。

本文为Hacking Team泄露的400GB数据当中，查到韩国和哈萨克斯坦曾跟Hacking Team合作利用其开发漏洞利用工具发起针对中国攻击的证据。

0x01 韩国方面证据
===========

* * *

通过曝光的Hacking Team客户列表文件[Clinet Overview_list_20150603.xlsx](https://ht.transparencytoolkit.org/Amministrazione/01%20-%20CLIENTI/5%20-%20Analisi%20Fatturato/2015/02%20-%20Client%20Overview%202015/Client%20Overview_list_20150603.xlsx)

可以看到韩国的5163部队是其中一个客户。

[![](http://static.wooyun.org//drops/20150811/2015081111535784034.png)](http://static.wooyun.org//drops/20150811/201508111248514444180a937ffffa214a87c498e62560f06bc)

维基解密网站将曝光的Hacking Team邮件数据制作成数据库，可以通过关键词、邮件收发者、附件名等方式进行检索，网站地址：

http://wikileaks.org/hackingteam/emails

而在韩国是没有 5163 army 这个部队的。

搜索了一下邮件里5163 army的地址，正是韩国国情院（NIS），韩国的联系人为[nanatechco@paran.com](mailto:nanatechco@paran.com)。

[![](http://static.wooyun.org//drops/20150811/2015081111535741546.png)](http://static.wooyun.org//drops/20150811/20150811124851619001b505c76a4da3a3679cc788d388095fb)

根据客户列表中的CODE可以查到韩国使用RCS系统所对应的联系人为[devilangel1004@gmail.com](mailto:devilangel1004@gmail.com)

[https://wikileaks.org/hackingteam/emails/emailid/808281](https://wikileaks.org/hackingteam/emails/emailid/808281)

[![](http://static.wooyun.org//drops/20150811/2015081111535883698.png)](http://static.wooyun.org//drops/20150811/20150811124850106866c13786af3d84a6542398f993a55386b)

而devilangel1004@gmail.com此邮箱与Hacking Team的多封邮件交流中谈到针对中国攻击的邮件。

[https://wikileaks.org/hackingteam/emails/emailid/73106](https://wikileaks.org/hackingteam/emails/emailid/73106)

该邮件明确表示，有一些目标在中国，希望找到绕过国内杀毒软件的方法。

[![](http://static.wooyun.org//drops/20150811/2015081114570513012ht11.png)](http://static.wooyun.org//drops/20150811/20150811124849172076b3701c5cf92a831c239dad5767ecbd6)

[https://wikileaks.org/hackingteam/emails/emailid/44544](https://wikileaks.org/hackingteam/emails/emailid/44544)

这是在中国的一些目标，无法通过GSM回传数据，猜测中国ISP服务商屏蔽了一些IP段。

[![](http://static.wooyun.org//drops/20150811/2015081111535861997.png)](http://static.wooyun.org//drops/20150811/20150811124850551269a1635bbcf4a42caecf63a5c0fc38850)

受控中文系统上的软件

[https://wikileaks.org/hackingteam/emails/emailid/578986](https://wikileaks.org/hackingteam/emails/emailid/578986)

```
Application List (x86):
115浏览器 1.0 (1.0)
360杀毒 (4.2.0.4055)
360压缩 (3.0.0.2011)
360安全卫士 (9.1.0.2001)
360手机助手 (1.7.0.1715)
Adobe Flash Player 11 ActiveX (11.7.700.224)
Adobe Flash Player 10 Plugin (10.0.45.2)
交通银行网银安全控件 V1.0.0.5 (0.10.11.3)
东亚中国网上银行安全Key软件 (ϩ)
中国农业银行证书安全控件卸载
中国农业银行网上银行证书工具软件 飞天诚信 Extend KEY 卸载 (20120612)
LinkSkype_Setup (1.0)
Microsoft .NET Framework 2.0
MSNLite (3.1)
QvodPlayer(快播) v3.5 (3.5)
搜狗拼音输入法 6.5正式版 (6.5.0.9181)
搜狗壁纸 1.5版 (1.5.0.0922)
千千静听 5.9.6 (5.9.6)
Windows Live 软件包 (14.0.8117.0416)
WinRAR 压缩文件管理器
人人桌面
腾讯QQ2012 (1.87.4930.0)
Free Launch Bar (1.0)
Windows Live 上载工具 (14.0.8014.1029)
中国农业银行网上银行安全控件 v2.3.6.0
中国农业银行网上银行证书工具软件（旋极信息）
Microsoft Office Professional Edition 2003 (11.0.8173.0)
Compatibility Pack for the 2007 Office system (12.0.6514.5001)
迅雷5 (5.9.25.1528)
Windows Live 登录助手 (5.000.818.5)
REALTEK GbE & FE Ethernet PCI-E NIC Driver (1.35.0000)
Skype(TM) 5.9 (5.9.14)
Intel(R) Graphics Media Accelerator Driver (6.14.10.5402)
Realtek High Definition Audio Driver
中国银行网上银行安全控件 2.1
暴风影音 V3.10.07.30

```

泄露的400G文件中，Exopoit_Delivery_Netwokr_Windows.Tar为Hacking Team针对电脑系统的远程漏洞攻击服务器数据， Exopoit_Delivery_Netwokr_Andorid.Tar为Hacking Team针对安卓系统的远程漏洞攻击服务器数据。

[http://ht.transparencytoolkit.org/Exploit_Delivery_Network_android.tar.gz](http://ht.transparencytoolkit.org/Exploit_Delivery_Network_android.tar.gz)

[http://ht.transparencytoolkit.org/Exploit_Delivery_Network_windows.tar.gz](http://ht.transparencytoolkit.org/Exploit_Delivery_Network_windows.tar.gz)

在Exopoit_Delivery_Netwokr_Andorid.Tar中，发现两条中国IP被攻击记录：

如在文件夹“jAWxkt”中，log.jsonl显示一北京IP在2015年6月26日，访问了攻击漏洞连接，访问机型为华为G700。

[![](http://static.wooyun.org//drops/20150811/2015081111535933489.jpeg)](http://static.wooyun.org//drops/20150811/201508111248511073435274e37d3ae4057f7161fbde3662519)

“data”目录中的redir.js显示，攻击重定向地址为www.myasianporn.com，为亚洲色情网站。

[![](http://static.wooyun.org//drops/20150811/2015081111535932615.png)](http://static.wooyun.org//drops/20150811/2015081112485278869d665514fa8cad5c013850236c58c55ec)

在wikileaks数据库中查询附件“jAWxkt”，可以查到是韩国发起的攻击。

[https://wikileaks.org/hackingteam/emails/emailid/1079019](https://wikileaks.org/hackingteam/emails/emailid/1079019)

[![](http://static.wooyun.org//drops/20150811/2015081111535998053.png)](http://static.wooyun.org//drops/20150811/201508111248521748867fec15330fd991f4de1af8152c7719b)

按照同样的方法可以同样可以查到，在文件“vYLpBL”中，log.jsonl显示一辽宁IP在2015年6月18日，访问了攻击漏洞连接，访问机型为三星9008。重定向地址为www.5zuo2.com，为亚洲色情网站。有意思的是，辽宁是距离韩国最近的一个省了。

邮件证据：

[https://wikileaks.org/hackingteam/emails/emailid/1079521](https://wikileaks.org/hackingteam/emails/emailid/1079521)

![enter image description here](http://drops.javaweb.org/uploads/images/748945a59b39d1460a2aba7704b252a432a3b6c2.jpg)

服务器控制端证据：

![enter image description here](http://drops.javaweb.org/uploads/images/94cb959c6d4a18cf9885d0e46e24b95d29ce5ec8.jpg)

0x02 哈萨克斯坦证据
============

* * *

[![](http://static.wooyun.org//drops/20150811/2015081112585495240ht3.png)](http://static.wooyun.org//drops/20150811/2015081112485296760e31986d0031b265af0c2f168488e16e8)

哈萨克斯坦国家安全委员会下属部门SIS（SIS of NSC）与Hacking Team有密切合作。

从邮件中找到，哈萨克斯坦交流的对应人员的邮箱为：eojust@gmail.com

[https://wikileaks.org/hackingteam/emails/emailid/551971](https://wikileaks.org/hackingteam/emails/emailid/551971)

![enter image description here](http://drops.javaweb.org/uploads/images/72352ec4f3aec1e9da98c8c9f4cf23cf7940be7f.jpg)

邮件中搜索到针对中国的证据：

[https://wikileaks.org/hackingteam/emails/emailid/69177](https://wikileaks.org/hackingteam/emails/emailid/69177)

邮件中表明目标电脑可能安装了国内杀毒软件导致一个月没有再上线了。

![enter image description here](http://drops.javaweb.org/uploads/images/209d1364e968eea36fb85cb9d6548b388429378e.jpg)

这个就是受控机软件列表：

```
Device:

Content: Processor: 2 x Intel(R) Core(TM)2 Duo CPU     E7200  @ 2.53GHz
Memory: 1548MB free / 2045MB total (24% used)
Disk: 211011MB free / 229944MB total
Battery: AC Connected - 0%

OS Version: Microsoft Windows XP (Service Pack 3) (32bit)
Registered to: user (oemxp) {76481-640-3060005-23096}
Locale settings: zh_CN (UTC +08:00)
Time delta: +00:00:00

User: ShiYongRen (ShiYongRen) {ADMIN}
SID: S-1-5-21-1238585575-1299394864-243974745-1006

Drive List:
C:\ (disk)
D:\ "新加卷" (disk)
E:\ (cd-rom)


Application List:
360杀毒   (4.2.2.4092)
360安全卫士   (9.1.0.2002)
Adobe Flash Player 11 ActiveX   (11.9.900.117)
ATI Display Driver   (8.471-080225a1-059746C-ATI)
暴风看电影   (1.22.1017.1111)
智能五笔
系统补充驱动包
飞信2013   (2013)
freeime 6.1   (6.1)
Windows Internet Explorer 8   (20090308.140743)
Windows Genuine Advantage Validation Tool (KB892130)
WPS Office 2007 专业版 (6.3.0.1328)   (6.3.0.1328)
OrderReminder hp LaserJet 101x   (1.0)
谷歌金山词霸合作版   (2008.07.17.1.212)
Microsoft Office Professional Plus 2007   (12.0.6612.1000)
搜狗拼音输入法 3.2 正式版 (3.2.0.0590)
暴风影音5   (5.29.0926.2111)
Thunder BHO Platform 2.2.0.1035
迅雷7
WinRAR 5.00 beta 5 (32 位)   (5.00.5)
腾讯QQ2013   (1.96.7979.0)
hp LaserJet 1010 Series   (3.00.0000)
Apple 应用程序支持   (2.3.4)
Apple Software Update   (2.1.3.127)
Bonjour   (3.0.0.10)
Microsoft Office File Validation Add-In   (14.0.5130.5003)
iTunes   (11.0.4.4)
Microsoft Visual C++ 2008 Redistributable - x86 9.0.30729.6161   (9.0.30729.6161)
Adobe Reader 8.1.2 - Chinese Simplified   (8.1.2)
Apple Mobile Device Support   (6.1.0.13)
Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022.218   (9.0.21022.218)
迅雷看看播放器   (4.9.9.1734)
迅雷看看高清播放组件


Application List:
360杀毒   (4.2.2.4092)
360安全卫士   (9.1.0.2002)
Adobe Flash Player 11 ActiveX   (11.9.900.117)
ATI Display Driver   (8.471-080225a1-059746C-ATI)
暴风看电影   (1.22.1017.1111)
智能五笔
系统补充驱动包
飞信2013   (2013)
freeime 6.1   (6.1)
Windows Internet Explorer 8   (20090308.140743)
Windows Genuine Advantage Validation Tool (KB892130)
WPS Office 2007 专业版 (6.3.0.1328)   (6.3.0.1328)
OrderReminder hp LaserJet 101x   (1.0)
谷歌金山词霸合作版   (2008.07.17.1.212)
Microsoft Office Professional Plus 2007   (12.0.6612.1000)
搜狗拼音输入法 3.2 正式版 (3.2.0.0590)
暴风影音5   (5.29.0926.2111)
Thunder BHO Platform 2.2.0.1035
迅雷7
WinRAR 5.00 beta 5 (32 位)   (5.00.5)
腾讯QQ2013   (1.96.7979.0)
hp LaserJet 1010 Series   (3.00.0000)
Apple 应用程序支持   (2.3.4)
Apple Software Update   (2.1.3.127)
Bonjour   (3.0.0.10)
Microsoft Office File Validation Add-In   (14.0.5130.5003)
iTunes   (11.0.4.4)
Microsoft Visual C++ 2008 Redistributable - x86 9.0.30729.6161   (9.0.30729.6161)
Adobe Reader 8.1.2 - Chinese Simplified   (8.1.2)
Apple Mobile Device Support   (6.1.0.13)
Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022.218   (9.0.21022.218)
迅雷看看播放器   (4.9.9.1734)
迅雷看看高清播放组件

```

0x03 结语
=======

* * *

这些已泄露的信息可以表明，中国才是国际化网络攻击的受害者。在报告中发现一些亚洲地区国家对我国进行的网络攻击窃密的铁证，甚至一些攻击已经得手，成功的控制了国内目标的PC或手机。攻击方还会对新发现的问题做针对性的要求，保证更隐秘的监控与机密信息的回传。切记！这些都不是电影情节，而是已真实发生的国家级网络安全的较量。

有趣的发现是，一些没有信心独立完成整个攻击过程的国家会更倾向于寻求这种“网络军火商”的帮助，因为对攻击过程的隐蔽以及可靠性要求极高，攻击过程不允许出现半点马虎，必须保证行动的精准并且有效。而一些”网络部队“发达的国家则更喜欢自己来，以此保证动机与行动的隐蔽性。

最后，从乌云社区从对HackingTeam泄露的邮件以及工单内容分析来看，国际上对我国的网络间谍行为是真实存在的，组织严明行动缜密，如不是这次互联网“军火库”的泄密事件，很多细节与事实对于我们来说仍然毫不知情，相信这次事件也将成为网络安全的里程碑，让我们所有人都深刻的意识到国家网络安全的重要与紧迫性。