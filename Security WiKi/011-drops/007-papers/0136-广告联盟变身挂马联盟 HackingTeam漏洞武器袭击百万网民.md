# 广告联盟变身挂马联盟 HackingTeam漏洞武器袭击百万网民

0x00 情况介绍
=========

* * *

在11月初，360互联网安全中心监控到一款名为“**restartokwecha**“的下载者木马拦截量暴增,而对其溯源发现，木马竟然来自PConline（太平洋电脑网），1ting（一听音乐网），stockstar（证劵之星）等一批知名网站。对这些网站进行分析发现，网站广告位展示的广告中包含了Hacking Team泄露的Flash漏洞中的一个漏洞利用挂马（CVE-2015-5122）。而该下载者木马，除了在用户计算机上安装多个恶意程序外，还会推广安装多款知名软件。由于国内大量电脑仍然没有及时升级Flash插件，造成木马可以大规模传播。

360互联网安全中心在今年，已经多次捕获到国内大规模挂马行为，包括今年5月底的播放器广告位CVE-2014-6332挂马，今年7月中旬皮皮影音等CVE-2015-5122挂马，今年10月初，多家知名网站CVE-2015-5122Flash漏洞挂马。这些挂马事件，影响用户均超过百万，都是利用国内知名厂商平台进行传播，而幕后金主也包括国内多家大厂商。

0x01 攻击原理
=========

* * *

此类木马攻击，一般通过3种方式传播其木马站点，分别是**攻击其他网站挂马；自建木马站点**，通过广告链接SEO等导入流量；通过网站/联盟广告位方式挂马。

例如，像下面这种，利用网站对发帖内容审核不严的问题，在帖子中加入其它站点的Flash元素，对网站进行挂马。

![](http://drops.javaweb.org/uploads/images/c3950569b30a5b69483b43df74f920c73d31a6cf.jpg)

攻击者只需要在用户访问的页面中插入一个攻击者设定的Flash元素，即可完成攻击。而Flash内容，做为网页的富媒体内容，在互联网中有广泛应用，如果平台对媒体内容审核不严，极有可能出现被恶意利用，网站挂马的情况。

挂马网站攻击流程：

![](http://drops.javaweb.org/uploads/images/915eb3b21b05a435b2c72627417230b3400de3fd.jpg)

0x02 案例分析
=========

* * *

对此次挂马事件，PConline因为整站挂有此类木马，受影响用户最多，我们以PConline为例做了分析，国内还有多家知名网站也存在同样问题。

挂马页面分析
------

PConline被挂马，是因为其使用了“海云互通”广告联盟的广告内容，这个广告联盟为攻击者提供了广告推广的服务，最终造成在PConline的页面中嵌入木马的效果。

首页，PConline的主站，使用了自己站点pcauto下的内容：

![](http://drops.javaweb.org/uploads/images/5c0cc912b9e3fc9edf32aea834ad95dcaf98b583.jpg)

Pcauto使用vamaker（万流客）管理其广告流量：

![](http://drops.javaweb.org/uploads/images/f62361699b1a656d4ff8a3d9a02cb2251265da01.jpg)

之后可以看到，vamaker引入了qtmojo（宽通广告）的代码，而宽通广告带入了出问题的“海云互通”（haiyunx）广告联盟内容：

![](http://drops.javaweb.org/uploads/images/a8511abad41d6d84b7476ed65d0405140785f305.jpg)

最终，我们在“海云互通”的代码中发现了接入木马服务器zyxtx.cn的代码：

![](http://drops.javaweb.org/uploads/images/736a1eb8ad167a006db0bef54332657d38727c7a.jpg)

![](http://drops.javaweb.org/uploads/images/957854fa3dc552dead463ebe4daab6a8583b8bff.jpg)

攻击者对其代码进行了重新编码，如图所示数组，即为其引入木马的隐藏代码：

![](http://drops.javaweb.org/uploads/images/9a155ac51d932a1895e0295bf17d4417a112de1c.jpg)

**对这段代码进行解码之后，可以看到。攻击者为了达到隐藏攻击代码的意图，会在页面中引入一个游戏的Flash资源，将攻击代码伪装成“正常的游戏Flash页面”，在后面又悄悄引入了一个挂马Flash资源：**

![](http://drops.javaweb.org/uploads/images/f809a72c368d15ad55bfa042e9b7fd92d6e62399.jpg)

在打开这个页面时，将展示一个正常的游戏页面，攻击代码则会在后台悄悄执行：

![](http://drops.javaweb.org/uploads/images/c2e61a5a63a68eab40190f6a2b016dd5e5299a97.jpg)

在对此攻击进行分析时，这个木马服务器还挂着其它木马：

`218.186.59.89:8888`

![](http://drops.javaweb.org/uploads/images/f6efa76c0b3eb1b7eea82537b74ef3e9d9a93245.jpg)

**通过这种对页面代码做编码和伪装的方法，攻击者成功绕过了广告联盟和各大网站的审核（如果有的话~~），加挂马的代码通过各大网站展示给了普通计算机用户。如果用户访问到了这些网站，而又没打好补丁的话，就极有可能感染木马。**

挂马漏洞分析
------

此次挂马，攻击者使用的仍然是之前Hacking Team泄露的CVE-2015-5122Flash漏洞，如果用户计算机中的Flash版本仍然是18.0.0.209之前的版本，就会触发漏洞执行。对应的挂马Flash文件在一个月内，更新了超过20次：

![](http://drops.javaweb.org/uploads/images/9b7ae67fa000fdb1dff289d702e51954923e8760.jpg)

此挂马文件在VirusTotal上只有McAfee和360能够检出：

![](http://drops.javaweb.org/uploads/images/1bd70e330c8cda84eb47143df0a778bd8d219aad.jpg)

swf样本用doswf加密过，解密之后，可以看到该样本的源码如下：

![](http://drops.javaweb.org/uploads/images/6dfef88e32e2efccd0e812784ac4232554e7963e.jpg)

漏洞触发代码如下：

![](http://drops.javaweb.org/uploads/images/342844910d258e212bcb0ac95d1248788be673be.jpg)

通过对源码的跟踪，便能发现是cve-2015-5122的样本。

在漏洞触发后使用的payload如下：

![](http://drops.javaweb.org/uploads/images/d3dd91bf9d2ebf7b15bd59f016174eb1bc2a1417.jpg)

反汇编出来的shellcode如下：

![](http://drops.javaweb.org/uploads/images/cde65ebce247f543ee7a7749d1f4e1df651622af.jpg)

通过对shellcode进行调试分析发现该样本将会从file.nancunshan.com下载木马到本地浏览器临时目录，生成文件wecha_159_a.exe，并执行

![](http://drops.javaweb.org/uploads/images/da9dd3a171db9c3efdbb7afc3f4d8d4984719344.jpg)

关于漏洞的详细分析，可以看我们之前的分析《Hacking Team攻击代码分析Part 4: Flash 0day漏洞第二弹 – CVE-2015-5122》（[http://blogs.360.cn/360safe/2015/07/11/hacking-team-part4-Flash-2/](http://blogs.360.cn/360safe/2015/07/11/hacking-team-part4-Flash-2/)）

Payload分析
---------

此次挂马的传播木马，和以往几次大规模挂马类似，仍然是一个做为流氓软件推广器使用的下载者，这个下载者木马的制作手段老练，属于专业木马团伙制作。

1.  此木马更新速度很快，高峰时每小时都会更新一次文件，用来快速躲避查杀和监控。1.
    
2.  会检测和判断环境，在发现是虚拟机测试机的情况下，不执行作恶代码，躲避分析。1.
    
3.  频繁变更下载域名，躲避查杀。
    

木马的统计和下载域名：

![](http://drops.javaweb.org/uploads/images/710796b918d8260fcfe63ab0a98e7f89f8d53dd7.jpg)

木马的功能选项，包括弹广告，下载文件，重启程序，自删除等：

![](http://drops.javaweb.org/uploads/images/0d13161ac5d9c0e0dd6258f898a38d68e428da98.jpg)

木马会枚举当前系统的进程列表，如果遇到虚拟机，影子系统，网吧等时，不执行下载者的功能。

![](http://drops.javaweb.org/uploads/images/0fd7623add3e29fd73ccbf2c5dfe3326bfa3eb39.jpg)

木马的下载列表也进行了编码，用来对抗分析：

![](http://drops.javaweb.org/uploads/images/78600c7d03ffbd38349ba8c23ea94f6f82e63e09.jpg)

对这份列表进行解码，可以看到国内多款知名软件在列：

![](http://drops.javaweb.org/uploads/images/14ab2e413beb5ef71d8de4225680306a7c60bc39.jpg)

下载者运行的进程树情况：

Process Tree

*   iexplore.exe 2404
    *   iexplore.exe 2600
        *   wecha_159_a.exe 2944
            *   restartokwecha_159_a.exe 3092
            *   xwiklit_552_setup.exe 3524
            *   ADSafe.29096-2.exe 3756
            *   cqss_1116.exe 1040
                *   cq1.76.exe 2832
            *   setup_B63_1.exe 3908
            *   duba_3_802.exe 2628
            *   QQPCDownload72845.exe 3116
            *   MTViewbuildmtview_97.exe 520
            *   1.0.003-Install_121_123.exe 3460
                *   KcProc.exe 1924
            *   jywset_65_6.exe 3624

推广的内容中，还包括快查这类恶意程序。

注入系统进程，后台隐藏执行：

![](http://drops.javaweb.org/uploads/images/12429bc5f73735ff9b41c410f65b6135cb463c1c.jpg)

![](http://drops.javaweb.org/uploads/images/4263aa452e05110a19ab91190aeecf2aafcba265.jpg)

创建虚假浏览器快捷方式，篡改用户首页：

![](http://drops.javaweb.org/uploads/images/39cbfe4f82380658067f90e36f78e443f3ae44ca.jpg)

安装广告插件，在用户计算机不断弹出各类广告：

![](http://drops.javaweb.org/uploads/images/118dc94284b753367ce3fa61ef4789d3e92a811f.jpg)

![](http://drops.javaweb.org/uploads/images/1c059d6ec5e72ced7ff72a9690ae7d22b3fc16ac.jpg)

此类下载者木马，由于其推广列表云控，推广内容也在不断免杀更新。攻击者通过不断向用户计算机推广各类软件，疯狂榨取用户计算机资源，赚取推广费。

0x03 数据统计
=========

* * *

此次大规模网页挂马，从十一月初开始，和上一轮大规模挂马（10月初的广告联盟挂马事件）为同一伙人所为。在之前挂马被杀之后，攻击者又卷土重来。根据360互联网安全中心统计，此次挂马，单日挂马页面拦截量超过170万次，单日受影响用户将近30万。单日木马拦截量超过4万次。

近期CVE-2015-5122挂马页面拦截量：

![](http://drops.javaweb.org/uploads/images/c6c22deddb0db5c803f38e8d78837dc47f50b063.jpg)

20日，单日木马拦截量变动

![](http://drops.javaweb.org/uploads/images/fac1d00091423ee18bb7b4b16e9a21b24790f4fc.jpg)

受影响用户，分布情况：

![](http://drops.javaweb.org/uploads/images/247a0bbea2180062f91f0b1c2c3db92eb07924d3.jpg)

0x04 解决方案
=========

* * *

目前，我们在拦截挂马页面攻击的同时，已经联系广告联盟，去除带有挂马攻击的广告页面，要求联盟加强审核。

对于广大网民来说，应及时更新系统和浏览器中的Flash插件，打好安全补丁，切莫被“打补丁会拖慢电脑”的谣言误导。对于没有更新Flash插件的浏览器，应该暂时停用。同时可以安装具有漏洞防护功能的安全防护软件，应对各类挂马攻击。

对于国内各大软件厂商和网站/网盟平台厂商，也应该加强自身审核，不要让自身渠道成为木马传播的帮凶，严格审核平台中出现的广告内容，防止广告挂马。各个软件厂商，也需要规范自身推广渠道，不要成了木马黑产的幕后金主！