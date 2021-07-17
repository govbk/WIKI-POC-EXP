# 安防IP Camera固件分析

0x00 背景
-------

* * *

之前一直看的是传统的系统安全问题，最近了解了下嵌入式设备的安全，颇有意思。

首先要从下面一个图说起：

![botnet.jpg](http://drops.javaweb.org/uploads/images/88d9df3affb9a9e35001a6990606709d257b027a.jpg)

这是由一位匿名的黑客通过端口探测等方式得到的2012年全球可攻击利用的嵌入式设备热点分布图，被叫做“Internet Census of 2012”，具体更详尽信息可见其网站：[Internet Census of 2012](http://internetcensus2012.bitbucket.org/paper.html)。

这些设备完全就是在互联网上裸跑，不管是管理员还是黑客都可以随意控制它们。

跟传统的现代处理器保护机制不一样，这些嵌入式设备处理器很多都没有我们习以为常的如虚拟内存、特权级等的概念，如何保护他们的安全目前是研究界的一大热点，USENIX Security 2013有篇论文是专门针对这些问题讨论的，叫[Sancus: Low-cost trustworthy extensible networked devices with a zero-software Trusted Computing Base](http://www.liwenhaosuper.com/blog/wp-content/uploads/2014/02/liwenhao_sancus_slides.pdf)。

既然嵌入式设备都在裸跑，那么研究下它们里面的东西，作进一步分析是非常有必要的。

0x01 细节
-------

* * *

接下来要考虑的是研究哪种嵌入式设备，选择路由器？好像乐趣不多；前几天看了部电影《风暴》，我对里面警察通过监控摄像头查找证据的场景印象深刻，当时浮现的想法是：如果匪徒也能控制这些监控摄像头，反过来通过它们监控警察的行踪，或者在他们作案前或作案后将监控摄像头的数据删除掉，那么警匪的力量就不会这么悬殊，剧情会不会更有意思？

在现实生活中，如果我作为黑客能够控制所有的摄像头，如室内的家庭安防，那是多么可怕的场景：

摄像头的本意的用于防护别人保护自己安全，而一旦被人利用了就可能反过来自己遭受监控！由此目标就锁定在安防摄像头上了。

首先面临的问题是如何找到目标设备？最直接的方法是通过它们暴露的接口：它们必须与客户端连接！

那么就找个客户端：vMEyeSuper，google一下看到这个博客[http://www.petsdreampark.com/blog/archives/2726](http://www.petsdreampark.com/blog/archives/2726)提供的设备地址：pdp.ns01.biz，然后就是找机会入侵啦：端口扫描，暴力破解。

通过工具发现设备的telnet是可登录的，然后就是暴力破解，用户名密码一下子就出来了(user name: root, password就不贴了)。试了下，成功登录进去，root权限哦！

登陆进去后它打印显示“welcome to monitor tech”，“嗯，不客气，反正我都来了”。先查看系统信息吧：

![cpuinfo.png](http://drops.javaweb.org/uploads/images/c15ba103fe8fa18e8e2870e32a7e76295d9ea0b7.jpg)

![versioninfo.png](http://drops.javaweb.org/uploads/images/27dd8d26772bb74d5a65ef24256dd0bae5f8fa16.jpg)

![meminfo.png](http://drops.javaweb.org/uploads/images/47934ceb9840a93b7fdd0bf737d78c459896ab89.jpg)

可看到系统用的是ucLinux，内核是3.0.8，处理器是ARM926EJ-S，芯片是海思的Hi3518，google一些这方面的信息，海思的hi3XXX都是有名的安防解决方案，海思的SDK可在[这里](http://download.csdn.net/download/wumusenxppp/5731827)下载。

找了一番发现系统就是一个ucLinux内核加一个busybox组成的，核心IPC固件在/usr/bin下，ps一下看到进程主要是Sofia和dvrbox，而关键是Sofia。：

![bininfo.png](http://drops.javaweb.org/uploads/images/a044e837ebbd2482c9168c1bd8a38328384e346d.jpg)

![psinfo.png](http://drops.javaweb.org/uploads/images/6e86938de6cae7622ba5c0ed65a31560ad5ad8f6.jpg)

重启Sofia可以看到一系列log信息，其中它开了一个web server，目录在/mnt/web下。

我想做的一个事情是将所有有用的文件拷贝下来分析，因为看到里面有用户名、密码信息等，但是由于busybox提供的工具太少了，关键是ssh，scp, wget, ftp等这些都没有，没办法上传下载，真是无奈：没有现有的工具，有root权限能干的事情也很有局限性呀！

想到它开有web server，于是打算将文件放到/mnt/web下再从浏览器下载下来。可惜不成功：目录只读！

![mountinfo.png](http://drops.javaweb.org/uploads/images/9ab0494aae741cb7feb6d466618236bc2b09c156.jpg)

想到一个办法：虽然/mnt/web下是只读的cramfs文件系统，可通过mount mtd到/mnt/web下覆盖原有目录做到：

```
mount -t jffs2 /dev/mtdblock5 /mnt/web

```

总算顺利将所有文件都拖下来了！

分析发现searchIp、Sofia执行文件都用了upx进行压缩的，需要先进行解压。然后就用IDA Pro进行反汇编分析了。

分析发现searchIp是作为一个server用于被客户端扫描发现并主动连接到Sofia的工具。

基于此，只要写个扫描工具就能够发现并登录同厂商大量的裸露安防摄像头设备了！

接下来有空的话要做的事情就是尝试扫描网络发现这些设备并利用google map组成一个摄像头监控网络。

目前尚未解决的问题：由于无法物理接触到这些设备，系统busybox里面又没有可用的工具，尚不能上传文件到设备上。