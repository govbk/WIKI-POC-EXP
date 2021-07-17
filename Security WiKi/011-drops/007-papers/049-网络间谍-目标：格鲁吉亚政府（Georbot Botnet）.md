# 网络间谍-目标：格鲁吉亚政府（Georbot Botnet）

原文：[http://dea.gov.ge/uploads/CERT%20DOCS/Cyber%20Espionage.pdf](http://dea.gov.ge/uploads/CERT%20DOCS/Cyber%20Espionage.pdf)

译者按: 这是一篇对 <<**DUKES---||-持续七年的俄罗斯网络间谍组织大起底**>>文章的补充文章. 披露的是格鲁吉亚CERT在2011年对俄罗斯军方黑客的一次调查. 文章中诸多亮点现在看还是常看常新:比如反制黑客的手段是诱使黑客执行了一个木马. 另外将此篇文章对比最近ThreatCONNECT发布的camerashy报告,让我们不禁感慨的是,政府的反APT实在是比商业公司的反APT纯粹多了,专业多了.

0x00 概述
=======

* * *

2011年3月，格鲁吉亚“计算机应急响应小组”（CERT）发现了一次网络攻击事件，似乎是一起网络间谍活动。

在活动中使用的高级恶意软件主要是收集与格鲁吉亚,美国相关的敏感机密的安全文件，然后再把这些信息上传到某些CC服务器上（CC会经常变化）。

在调查了攻击者利用的服务器和恶意文件后，我们发现这次网络攻击活动与俄罗斯官方安全机构有关系。

在分析了web服务器，恶意文件和几个脚本后，我们发现：

1.  **一些与新闻行业相关的格鲁吉亚网站被黑了。**（恶意脚本只注入到了页面上，在这些页面上出现了一些特定的信息）
2.  **只要浏览了这些网页，计算机就会感染未知的恶意程序。**（当时，所有的杀毒产品都无法识别这一威胁）
3.  **在执行时，恶意文件会完全控制受感染的计算机。**
4.  **在受害者计算机中搜索 “敏感词汇”。**
5.  **使用内置的摄像头和麦克风捕捉视频和音频.**

0x01 受害者
========

* * *

这次网络攻击活动设计的十分聪明。多家与新闻相关的格鲁吉亚网站都被黑了，并且只有几个特定的新闻网页遭到了篡改（比如，**_NATO delegation Visit in Georgia-NATO代表团访问格鲁吉亚, US- Georgian Agreements and Meetings-美国格鲁吉亚协议与会面, Georgian Military NEWS-格鲁吉亚军事新闻_**）。

![](http://drops.javaweb.org/uploads/images/fd1487b649d9f11314f67fff5d4282073fb233ab.jpg)

只有对这类信息感兴趣的用户才会感染这个高级威胁，无论目标计算机和网络系统上使用了什么安全防御措施或软件。这个威胁的加密程度很高，并且使用了最新的隐藏技术，因此，还没有安全工具能识别这个威胁。

*   [www.caucasustimes.com](http://www.caucasustimes.com/)-**关于高加索地区的新闻网站**
*   [www.cei.ge](http://www.cei.ge/)-**高加索能源与基础设施**
*   [www.psnews.ge](http://www.psnews.ge/)-**格鲁吉亚新闻网站**
*   `ema.gov.ge`
*   [www.opentext.ge](http://www.opentext.ge/)
*   [www.presa.ge](http://www.presa.ge/)
*   [www.presage.tv](http://www.presage.tv/)
*   [www.psnews.info](http://www.psnews.info/)
*   [www.resonancedaily.com](http://www.resonancedaily.com/)

0x02 木马功能
=========

* * *

完全控制受感染的计算机。 木马会搜索受害者MS Office和PDF中的**敏感词汇**。

*   将任意本地硬盘上的文件发送到远程服务器
*   窃取凭据
*   在硬盘上搜索Microsoft Word文档
*   在硬盘上搜索远程桌面配置文件，pbk文件
*   获取屏幕截图
*   使用麦克风记录声音
*   使用摄像头记录视频
*   扫描本地网络，识别同一网络中的其他主机
*   在受感染的系统上执行任意命令

0x03 敏感词汇
=========

* * *

![](http://drops.javaweb.org/uploads/images/8dad849d1f2f2aff0a901d3288905cf414f971c2.jpg)

最后，攻击者会窃取匹配的文件并上传到服务器。

0x04 CC服务器
==========

* * *

![](http://drops.javaweb.org/uploads/images/42563b9beac90ff7b24bd9ef6ed51d49f4908af1.jpg)

木马会受根据受害者的地理位置相应的改变它的CC服务器位置。

大约有390台计算机受到了感染：

*   70%来自格鲁吉亚
*   5% 来自美国
*   4% - 加拿大，乌克兰，法国，中国
*   3% - 德国
*   3% - 俄罗斯

美国受感染的计算机实例

![](http://drops.javaweb.org/uploads/images/6381a0082ac51c026def9eefd8826b4c6f9bf490.jpg)

0x05 恶意文件在逐渐进化和发展
=================

* * *

**2011年3月30日**– 病毒窃取敏感的文档，证书

**2011年9月14日**– 更改了感染机制，使用了新的绕过AV,Firewall,IDS的方法.

**2011年11月25日**– 病毒的加密和混淆更复杂，支持感染Win7.

**2011年12月月12日**–**增加了视频录制功能，可以通过网络扫描和感染计算机，更换了传播途径**

病毒已经从2.1版本进化到了5.5版本。

0x06 感染机制
=========

* * *

1.  向合法网站注入script标签或iframe标签.
2.  使用iframe标签加载带有载荷的iframe.php.
3.  Drive-By下载&执行calc.exe
4.  calc.exe在Explorer.exe中注入代码并自毁.
5.  创建起维持作用的usbserv.exe病毒

![](http://drops.javaweb.org/uploads/images/899068993c650d668466860f77f0708bb9a98cc7.jpg)

第一步-注入脚本

![](http://drops.javaweb.org/uploads/images/71140c9cc003959c724fc1e4a03a722c34962c95.jpg)

frame.php中的shellcode/漏洞载荷

![](http://drops.javaweb.org/uploads/images/0451768b4b9c5f39bd122dc66e30c619b32cce0a.jpg)

1.  我们发现了一个特别制作且经过混淆的frame.php文件，在这个文件中携带着一些漏洞代码，并且会把用户重定向到其他的漏洞页面：利用了CVE-2010-0842，CVE-2006-3730，MS06-057和其他未知的漏洞。
2.  frame.php中使用的漏洞代码是完成版的TrojanDownloader:JS/SetSlice，通过使用'WebViewFolderIcon' ActiveX控件（Web View）来利用漏洞MS06-057。
3.  另外，还通过PDF，JAR文件，利用了一些0-day漏洞

各大主要的杀毒产品都没能检测出这些恶意文件（1/4Virustoal，Dr.Web结果-可疑）。绕过了开启防火墙的Win7 sp1。截止到25.03.2011，20.06.2011，16.01.2012，25.03.2012。

![](http://drops.javaweb.org/uploads/images/9fdc555669156af5f9bcfe523523c1962473e4f3.jpg)

在执行后，木马主要干3件事：

*   在安装bot前，先检查这台计算机所在的时区是不是UTC+3，UTC+4：
*   把自己注入到iexplorer.exe并与钓鱼网站通信，获取CC地址
*   在Application Data目录中创建usbserv.exe bot文件。并写入到Windows注册表中自动运行

0x07 Bot控制机制
============

* * *

![](http://drops.javaweb.org/uploads/images/de1b6e7ec868a9ee78358da25c98a66835223837.jpg)

1.  CC服务器地址会硬编码到木马的二进制文件中.
2.  如果所有的这些地址都无法连接，木马会钓鱼网站中读取回连地址.(此处的钓鱼网站指上文阐述的已经被黑客事先入侵的新闻网站)

![](http://drops.javaweb.org/uploads/images/f1885ff9c01860693a2160335a5d9681f3a629b2.jpg)

0x08 新的木马更新方法
=============

* * *

新版本的木马文件，会用base64明文编码，从不同的网站上同时下载，然后整合成一个文件。

![](http://drops.javaweb.org/uploads/images/a673d96bf807d5c8a664d1c8923e1f4da4190715.jpg)

特点

1.  搜索敏感文件名字， 搜索pdf，word，xls，text，rtf，ppt文档中的敏感字符.
2.  从webcam中记录视频：在Skype对话时，能够捕捉直播流.
3.  从CC Web控制面板修改木马的代码文件.
4.  自创建的Packer，用汇编语言编写的Cryptor（绕过A/V）.
5.  更新机制，基于明文编码，同时从不同的CC服务器上下载.
6.  用ring0权限打开网络socket（绕过防火墙）/TDSS Rootkit修改.

0x09 受感染的组织
===========

* * *

多数受感染的格鲁吉亚计算机都是来自政府机构和关键信息基础设施。

目标：

1.  内阁
2.  议会
3.  关键信息基础设施
4.  银行
5.  NGO

0x0A 响应过程
=========

* * *

1.  根据检测，通过国家的三大主要ISP来拦截这6个CC IP地址（快速响应）
2.  CERT-GOV-GE确定所有受感染的格鲁吉亚IP，并提供应对策略，清除这些工具.
3.  与AV/IDS/IPS厂商合作，开发应对木马威胁的工具和识别木马的签名（Microsoft, Eset, Snort, Cisco, Blacklists, Blocklists）
4.  与FBI，国土安全局，美国特勤局，美国CERT，德国CERT，乌克兰CERT，波兰CERT，微软安全部合作
5.  要求托管服务提供商自家的监控小组关闭攻击服务器.
6.  执法部门获取日志文件和系统镜像进行取证分析.

0x0B 网路情报对抗（揭开攻击者的面纱）
=====================

* * *

格鲁吉亚CERT小组 获取了CC服务器的权限，解密了木马的通信机制。在分析了所有收集到的信息后，我们已经识别了网络攻击者和攻击组织的身份。

“在2008年，俄罗斯与格鲁吉亚的网络战期间”，两家独立的美国组织发现这些网络攻击者与俄罗斯政府部门和组织存在关联。

“**United States Cyber Consequences Unit**” and “**Project Grey Goose**”

_Jefrey Carr, GreyLogic (为政府部门提供的网络情报服务) Sanjay Goel,纽约州信息分析与保证中心， Mike Himley, *Eagle Intelligence的_CEO/主席*

他们调查了整个针对格鲁吉亚的网络攻击活动，并且发现一个网络犯罪小组_“**Russian Business Network**”_与2008年的网络攻击活动有关系。

他们已经报道，黑客使用的一些资源和凭据属于 “俄罗斯国防部研究所”-国外军事力量研究中心。

**在2011-2012年期间，在这次新出现的网络间谍活动期间，我们又再次发现了背后的俄罗斯特工痕迹。**

我们已经发现了：3点主要事实都指向了俄罗斯官方的政府组织。

`Warynews.ru`– 用于控制受感染的格鲁吉亚计算机 – 属于 **Russian Business Network(在 Blacklist, Bad Reputation中提到) **的IP和DNS

`www.rbc.ru`– 直接硬编码在木马代码中，如果所有信道都关闭了，则与攻击者通信。官方名称“Russian Business Consalting” –官方网站，与RBN有关联。

![](http://drops.javaweb.org/uploads/images/07b13797397a6b2cc2a8feb0e0cf9039f913dae0.jpg)

```
http://legalcrf.in/f/4b178e605583cca28c850943e805aabc/1
http://legalcrf.in/t/19ebfd07a13d3edf82fcc121a0e4643c 
http://legalcrf.in/images/np/4b178e605583cca28c850943e805aabc.pdf 
http://legalcrf.in/t/19ebfd07a13d3edf82fcc121a0e4643c http://legalcrf.in/t/19ebfd07a13d3edf82fcc121a0e4643c http://legalcrf.in/images/t/4b178e605583cca28c850943e805aabc.html 
http://legalcrf.in/images/np/4b178e605583cca28c850943e805aabc.pdf 
http://legalcrf.in/images/4b178e605583cca28c850943e805aabc.jar 
http://legalcrf.in/f/4b178e605583cca28c850943e805aabc/3 
http://legalcrf.in/f/4b178e605583cca28c850943e805aabc/1

```

**Legalcrf.in –通过“[admin@President.gov](mailto:admin@President.gov).ge”发送垃圾邮件来传播恶意文件**

0x0C 托管漏洞文件
===========

* * *

注册人信息不明确，通过印度Whois服务发现

![](http://drops.javaweb.org/uploads/images/d3093a15bab29325505d992295ea84f5613e9180.jpg)

![](http://drops.javaweb.org/uploads/images/b52ad15529ebc6d9c39cddfe1bd3a79cc14420a2.jpg)

**Lubianka 13, Moscow. - 俄罗斯内务部， 后勤部- 组织开发和通信系统， 组织发展和通信系统，提升信息和通信技术和信息技术保障；**

在他旁边的是：俄罗斯联邦安全服务部**(FSB) – 莫斯科**

![](http://drops.javaweb.org/uploads/images/1bd60baf2d9cb7f44a380596725dd9e9f55d9896.jpg)

在2012年3月，ESET安全公司公布了一份报告-“Georbot: From Russia With Love” (根据我们小组的技术支持)

在此之后，俄罗斯新闻机构，根据ESET的报告散布虚假消息，指控格鲁吉亚的政府网站上托管着恶意文件（实际上遭到了黑客攻击）。但是，他们没有评论托管在不同国家的这6个真正的CC服务器。

我们在实验室中感染了我们的PC，然后向攻击者提供了虚假的Zip文档，其中包含着他自己的病毒，文件名称是“Georgian-Nato Agreement”。

我们创建了一个病毒文件名字是”Georgian-Nato Agreement”,随后我们故意感染了黑客的木马并诱使黑客偷去了我们制作好的病毒文件. 最后黑客执行了这个病毒.

如此一来访问黑客的CC控制面板,控制黑客的个人计算机就不在话下了。

然后，我们捕捉到了一个他的视频。也捕获到了一个进程正在创建新的恶意模块。

我们已经从他的邮件中获取到了一份俄语文档，在文件中，他讲解了如何使用这个恶意软件感染目标。

我们发现他与德国和俄罗斯的黑客有联系。

然后，我们获取到了他的所在城市，ISP，邮件等。

![](http://drops.javaweb.org/uploads/images/04cea06c59677236e201efa0793e5b8f6a0ef5b5.jpg)

![](http://drops.javaweb.org/uploads/images/3ece3fae22973eb99bd55cb46c31e7eb860e721a.jpg)

![](http://drops.javaweb.org/uploads/images/aa4217cfdc441d89162581fbf67da3dc12ca1318.jpg)

正在使用OllyDbg进行反汇编

![](http://drops.javaweb.org/uploads/images/96c9ca519a1e523b8b7e0e77d62a6108628998b1.jpg)

**Nickname: ESHKINKOT – 木马可执行程序内部也出现了**

**相同的邮件地址，俄罗斯城市**

![](http://drops.javaweb.org/uploads/images/95ba7bc23d7c265cf4b4f30475d196cc4803e722.jpg)

**在俄罗斯的 Xakep 论坛，寻求别人帮助他编写EXPLOIT.**

他使用的网络提供商名字,他所在的城市.

**多个会议上都出现了关于此次事件的信息：**

1.  SSECI 2012 (关键基础设施的安全，保障和效率) – Prague, Czech Republic 30 may – 01 June 2012*(with support of ONRG – Office of Naval Research Global) *
2.  网络事件和关键基础设施保护研讨会 – Tallin, Estonia 18-19 June 2012
3.  NATO – 和平与安全科学 (SPS) - METU - 中东技术大学阿富汗IT专家分析格鲁吉亚网络案例 , Turkey 21 May - 01 Jun 2012