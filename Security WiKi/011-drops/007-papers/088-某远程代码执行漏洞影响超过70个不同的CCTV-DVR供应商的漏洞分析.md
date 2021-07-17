# 某远程代码执行漏洞影响超过70个不同的CCTV-DVR供应商的漏洞分析

0x00 起因
=======

* * *

有个老外读了[POINT OF SALE MALWARE: THE FULL STORY OF THE BACKOFF TROJAN OPERATION](https://drive.google.com/file/d/0B3tdhdmrVDEwS216aDNXc0JfdTA/view)这篇paper后，对paper里面的数字窃贼先通过入侵CCTV系统识别目标所属的零售商，然后进一步入侵POS机，窃取信用卡帐号比较感兴趣，就去网上找了找了找该CCTV-DVR固件，然后通过分析发现了一个远程代码执行漏洞。然后我看他放出来POC，其实还利用了另一个该固件比较老的漏洞。下面一一说。

0x01 漏洞分析
=========

* * *

通过shodan搜索“Cross Web Server"可以发现大概有18817个设备，其中美国占多数，然后是中国，泰国。这些设备监听81/82端口的居多，另外也有些监听8000端口，

![p1](http://drops.javaweb.org/uploads/images/4baa539a86795381a9c5744fb001f7fffbc2e6db.jpg)图0

打开web后的页面如下：

![p2](http://drops.javaweb.org/uploads/images/d74fd7e2a6b243e48f51fea45956b048d7387e34.jpg)图1

然后通过查看网页源码找到WebClient.html,在查看WebClient.html源码找到script/live.js,live.js里包含了logo/logo.png

![p3](http://drops.javaweb.org/uploads/images/e9247681945b9d64f0b78e4feb92727f7cfc1b5e.jpg)图2

由这个logo知道这是一家销售CCTV系统的以色列公司，但是通过查看网站源码中的注释，发现是中国人写的代码，然后作者去官网下载了固件。固件下载回来是一个zip压缩包，解压后可以看到

![p4](http://drops.javaweb.org/uploads/images/e8a99af88150d00847851374effb047c00fc7cf5.jpg)图3

首先查看boot.sh，发现其中执行了另一个bash脚本deps2.sh，这个脚本执行了2个bin文件，分别是XVDRStart.hisi和td3520a，通过他们的文件体积，原文作者首先看了td3520a，td3520a包含了符号表，使分析变得很容易，通过预览了一阵代码，原文作者发现下面有问题的汇编代码

![p5](http://drops.javaweb.org/uploads/images/2b5c2cf2c2795b5a78542ad18cd8492d2312f1de.jpg)图4

通过代码可以看出如果`/language/[language]/index.html`中的`[language]`目录存在，则解压到`[language]`，如果不存在，则DVRSsystem最终会执行"`tar -zxf /mnt/mtd/WebSites/language.tar.gz %s/* -C /nfsdir/language/`",这就导致了命令执行。看到这里想到原来玩CTF遇到/etc/crontab文件中管理员用tar做定期备份的时候，语句写成了`tar cfz /home/rene/backup/backup.tar.gz *`，引发的问题，原理可以参考[http://www.defensecode.com/public/DefenseCode_Unix_WildCards_Gone_Wild.txt](http://www.defensecode.com/public/DefenseCode_Unix_WildCards_Gone_Wild.txt)

要想利用还需要克服几个问题

1.  web服务器不能处理使用空格或换行的URL编码
2.  命令长度有限制

可以通过`${IFS}`克服空格的限制

通过请求

```
GET /language/Swedish${IFS}&&echo${IFS}$USER>test&&tar${IFS}/string.js HTTP/1.1

```

来执行查看当前用户的命令，这个HTTP请求会返回404

要看执行结果，需要利用一个比较老的漏洞递归漏洞来查看结果

```
GET /../../../../mnt/mtd/test

```

![p6](http://drops.javaweb.org/uploads/images/d4b0cc504ea1e0c6b2efe43dd0c733f1fea39d8c.jpg)图5

其实如果不用命令执行漏洞来利用的话，也可以通过递归漏洞读取配置文件(/etc/passwd,/config/config.dat等)

![p7](http://drops.javaweb.org/uploads/images/662d3abc679873210d8e9ebac93103928e09a981.jpg)图6

POC地址如下：  
[https://github.com/k1p0d/h264_dvr_rce](https://github.com/k1p0d/h264_dvr_rce)

这个产品的真正的制造商是深圳的同为数码（[http://www.tvt.net.cn/](http://www.tvt.net.cn/)），其他厂商估计是带贴标签的，也就是俗称的OEM（又叫定牌生产和贴牌生产，最早流行于欧美等发达国家，它是国际大公司寻找各自比较优势的一种游戏规则，能降低生产成本，提高品牌附加值）

受影响的厂商列表：

*   Ademco
*   ATS Alarmes technolgy and ststems
*   Area1Protection
*   Avio
*   Black Hawk Security
*   Capture
*   China security systems
*   Cocktail Service
*   Cpsecured
*   CP PLUS
*   Digital Eye'z no website
*   Diote Service & Consulting
*   DVR Kapta
*   ELVOX
*   ET Vision
*   Extra Eye 4 U
*   eyemotion
*   EDS
*   Fujitron
*   Full HD 1080p
*   Gazer
*   Goldeye
*   Goldmaster
*   Grizzly
*   HD IViewer
*   Hi-View
*   Ipcom
*   IPOX
*   IR
*   ISC Illinois Security Cameras, Inc.
*   JFL Alarmes
*   Lince
*   LOT
*   Lux
*   Lynx Security
*   Magtec
*   Meriva Security
*   Multistar
*   Navaio
*   NoVus
*   Optivision
*   PARA Vision
*   Provision-ISR
*   Q-See
*   Questek
*   Retail Solution Inc
*   RIT Huston .com
*   ROD Security cameras
*   Satvision
*   Sav Technology
*   Skilleye
*   Smarteye
*   Superior Electrial Systems
*   TechShell
*   TechSon
*   Technomate
*   TecVoz
*   TeleEye
*   Tomura
*   truVue
*   TVT
*   Umbrella
*   United Video Security System, Inc
*   Universal IT Solutions
*   US IT Express
*   U-Spy Store
*   Ventetian
*   V-Gurad Security
*   Vid8
*   Vtek
*   Vision Line
*   Visar
*   Vodotech.com
*   Vook
*   Watchman
*   Xrplus
*   Yansi
*   Zetec
*   ZoomX

0x02 参考文章
=========

* * *

*   [TVT TD-2308SS-B DVR - Directory Traversal Vulnerability](https://www.exploit-db.com/exploits/29959/)
*   [Remote Code Execution in CCTV-DVR affecting over 70 different vendors](http://www.kerneronsec.com/2016/02/remote-code-execution-in-cctv-dvrs-of.html)