# 网络小黑揭秘系列之黑色SEO初探

**Author:360天眼实验室**

0x00 引子
=======

* * *

人在做，天在看。

11月底的时候，360天眼安全实验室发布了一篇文章：网络小黑揭秘系列之私服牧马人，揭露了一起污染私服搭建工具和用户登录端程序进行木马传播的事件。其实，类似的案例远不限于此，这次我们揭露另一根链条出来，当然还是从一个样本开始。

0x01 样本及基础设施
============

* * *

实验室在日常的恶意代码处理时注意到了一个文件名为“YY某主播视频.exe”（MD5: 27C8E69F7241476C58C071E83616D2B5）的远控木马：

![p1](http://drops.javaweb.org/uploads/images/5315bdaadf9bfe8faa0dfeacc5d3cd13d7cdee7d.jpg)

基本上，如果是一个国产木马，如果猜大灰狼，你就有90%的概率正确，这个木马当然也是。木马作者命名为“killqipilang”，就算大灰狼的变种吧。

对样本的分析就不多说了，想了解大灰狼远控的代码架构可以参看天眼实验室之前的那个揭秘。很容易就提取到木马内部编码过的上线URL为“qq867126996.3322.org”：

![p2](http://drops.javaweb.org/uploads/images/c0fc0f48e60e627f54a96ab31628061bccc75180.jpg)

使用360天眼实验室的可视化关联分析系统进行追踪溯源，发现该木马还关联了另一个上线URL：luanqi.net。由此线索继续，又关联到更多样本，其中一个名为“hexSB360.exe”（没错，木马作者对360都怀有极深的怨念）的程序（MD5: E4C62055D1BCEB88D97903562B9E1BE8），又一个大灰狼远控。

![p3](http://drops.javaweb.org/uploads/images/c3d48b164e0e8d0e40beb03a285f8d12f27e7ccf.jpg)

从此样本，我们提取到了其核心远控模块下载地址：`http://118.***.***.230:8080/Consys21.dll`。

整个交互式的分析过程在交互式的关联平台上就是如下这个样子：

![p4](http://drops.javaweb.org/uploads/images/eb89cd2640974638aae2706d88b8f8ec7fac87d8.jpg)

关联系统还告诉我们这个木马还使用了其他多个上线域名。有免费的二级域名qq867126996.3322.org、q332299.f3322.net，也有收费的顶级域名luanqi.net、lyisi.org、sb.jiushao.net、huo-dian.com。

对非免费域名做追溯一般是非常重要的突破点，我们可以查询一下相关的Whois信息。以下是域名luanqi.net的，可见做了隐私保护。

![p5](http://drops.javaweb.org/uploads/images/3cbc439768441603f989a999d21b75204c5d3db8.jpg)

域名lyisi.org的：

![p6](http://drops.javaweb.org/uploads/images/fc1b11b85087a3879871a68b4d573ac6fd7c07c2.jpg)

域名jiushao.net的

![p7](http://drops.javaweb.org/uploads/images/403343ece8014c35d06bdea8d7ea60ed6daaf4df.jpg)

域名huo-dian.com的：

![p8](http://drops.javaweb.org/uploads/images/85a68124b9541e8121efd57fa9df004c4186f24b.jpg)

注意上图中的dt0598@outlook.com这个注册邮箱，其名下注册的域名大多数已经被360拦截，其中不乏淘宝钓鱼站或者虚假商城，比如www.000268.cn，现时应该iphone6s才是热门机型，iPhone5都已经淘汰了，却出现在该商城的首页，只能说钓鱼也不够用心。

![p9](http://drops.javaweb.org/uploads/images/6dea4e0b64a7c710bc05ecef04c49133728dbc88.jpg)

在知道了样本关联出来的网络基础设施以后，利用一个众所周知的漏洞我们控制了小黑使用的某些服务器。在其中一台服务器上，我们看到了大灰狼远控的管理程序，在任务管理器这个木马控制端程序的CPU占用已经达到了12%：

![p10](http://drops.javaweb.org/uploads/images/ff575a35af2daca9841845216e0fbef8bed6aed5.jpg)

当时由于小黑正在线，我们用netstat命令查看一下该主机上目前已经上线的肉鸡：

![p11](http://drops.javaweb.org/uploads/images/f7306272ac8d8be2eeddff35edaa1a12a59e3e89.jpg)

嗯，似乎控制的肉鸡并不多，这个服务器就只是做木马的控制端吗？没那么简单，接着往下看。

0x02 枪和驾照
=========

* * *

翻服务器磁盘，我们发现该服务器上有个“泛站群系统”，该系统可以使得国内的搜索引擎收录更快，但被降权的速度也很快，所以这些服务器上会起用大量的域名和IP。下图是系统的使用说明：

![p12](http://drops.javaweb.org/uploads/images/5e554ae0e5cc64664c93e950c863f95c3bd7f960.jpg)

这台服务器上绑了多个外网IP：

![p13](http://drops.javaweb.org/uploads/images/f0fbdcf4f79c482ed5a3c336e909348a02aa8c6c.jpg)

依赖360网络研究院提供的DNS基础数据，我们获取了近期绑定在这些IP上的域名列表如下：

![p14](http://drops.javaweb.org/uploads/images/18e6cee804be304921747b4b78130967778276c1.jpg)

从这张列表中抽取了部份域名在某搜索引擎中做了验证，发现结果让我们有些心惊胆跳：

![p15](http://drops.javaweb.org/uploads/images/d62aacaa3e0b1c3c85cb32d36b97b598788ec2d0.jpg)

![p16](http://drops.javaweb.org/uploads/images/41341b3522b4ae520dbdfd7a5d52368a9ed1ccc9.jpg)

![p17](http://drops.javaweb.org/uploads/images/b7f1f14bf06c2eb03d34651b9c58380c29c40bd3.jpg)

![p18](http://drops.javaweb.org/uploads/images/3dfa607aa63553f35743c76a49c9e48f0a56729c.jpg)

![p19](http://drops.javaweb.org/uploads/images/e0cf2fd2f7f0d374d4367b8697b203b159eff428.jpg)

![p20](http://drops.javaweb.org/uploads/images/f858e9989d88690eac4660f59d834ac0e1a7711c.jpg)

![p21](http://drops.javaweb.org/uploads/images/cba4f8c2283a0158e1b6e94cd544433d3ed0035d.jpg)

很显然都是SEO卖枪的，而这些枪的关键词又正好在服务上就有发现：

![p22](http://drops.javaweb.org/uploads/images/6251173dc33e98f113651bc9b2420cb3d1db44ff.jpg)

通过whois信息的查询，发现所有涉枪域名都使用qiangseo@126.com注册，从这样直白的邮箱名来看，邮箱背后的人看来专门从事枪关键词SEO。

继续挖掘服务器上的文件，我们还发现了XISE Webshell管理器，呵，一个好长的列表，已经被地下管理员接管的机器真不少：

![p23](http://drops.javaweb.org/uploads/images/ea4b191ac980ea2d3aebafac322de85fb6d14534.jpg)

这些被黑的站点用来做什么了呢？看看小黑怎么操作那些Webshell就知道了：

![p24](http://drops.javaweb.org/uploads/images/8442c3ef952b2f4d8fa88957ae8127eb9fdddd66.jpg)

可见除了在自己的网站使用“泛站群”达到快速恶意SEO的目的，小黑还使用扫描器大量扫描存在漏洞的网站植入webshell，向这些网站写入要SEO的信息达到快速SEO的目的。随机抽了些被黑SEO的网站：

![p25](http://drops.javaweb.org/uploads/images/4ed68d7b1c18d4cfa7fa09423737e4372b5b5f5d.jpg)

政府网站历来都是被黑链的重灾区，对此只能一声叹息。

0x03 余额宝
========

* * *

翻服务器文件系统的过程中总是惊喜不断，打开一个目录`"XISE蜘蛛池\niubi\keywords"`下的1.txt，里面一堆和支付宝相关的关键词挺令人震惊：

![p26](http://drops.javaweb.org/uploads/images/dbcdfd5af009a6a03c691c88720c07595e531934.jpg)

原来小黑还通过“泛站群”做恶意SEO，使人在使用国内某些搜索引擎的时候找到钓鱼信息，坐等鱼上钩：

![p27](http://drops.javaweb.org/uploads/images/4015223f0e929d066c5a9247de69ade174b165b6.jpg)

![p28](http://drops.javaweb.org/uploads/images/1b2f97107ff83faf7704c3ef8443c38fc9b374a8.jpg)

![p29](http://drops.javaweb.org/uploads/images/fb1e28d714369bfbe986d0e8ef13ea41d01eba9d.jpg)

![p30](http://drops.javaweb.org/uploads/images/723cab16628a2553b5034a30303e017a3a94172f.jpg)

0x04 后门
=======

* * *

使用这台服务器的小黑也和绝大多数小黑一样，都是拿来主义，可拿来主义不等于免费主义，要么自己多个心，要么就交点学费。我们从这台服务器上取回来的SSH爆破程序包中就直接发现了“Usp10.dll”（MD5: B846B1BD3C4B5815D55C50C352606238）的盗号木马，而运行“SSH最终版（稳定）.exe”（MD5: 59F7BC439B3B021A70F221503B650C9C）这个主程序后也会在`%temp%`文件夹中释放2个文件：一个SSHguiRelease.exe（MD5: AB72FC7622B9601B0180456777EFDE5D），真正的SSH爆破程序；另一个filter32.exe（MD5: 7218C74654774B1FDE88B59465B2748C），使用易语言编写的程序，经分析发现该文件会向147***|||*_*|*_@163.com这个邮箱发送文件。

外面的Usp10.dll可能是被无意感染的，而里面的那个发邮件后门则明显是故意植入的，防不胜防。

![p31](http://drops.javaweb.org/uploads/images/9d185bf188c9d9bda07acc72f4f94b0c207fdaf5.jpg)

![p32](http://drops.javaweb.org/uploads/images/5a4593df6d7dd84ed9f97b42be67c387ad2df28a.jpg)

Usp10.dll这类恶意代码是dll劫持型木马，一个小心就全盘感染了。但从服务器上取回来的样本中只有2个软件包存在，且都是工具类的，服务器上并没有感染这个样本。

![p33](http://drops.javaweb.org/uploads/images/3b088aa6e2d7e1c8c29b46a609c99a0c313513f3.jpg)

上面这个工具可能来源于“泯灭安全网”，写稿时凑趣地网站维护了，只好贴个搜索快照图：

![p34](http://drops.javaweb.org/uploads/images/dcdab17a44acf7bda3a233fd81a92da39663b45e.jpg)

![p35](http://drops.javaweb.org/uploads/images/30be911c9a9ed3a00548cba720e87d841d63d463.jpg)

对后门代码进一步反汇编分析，确认147**_||_**|**@163.com即是收件邮箱又是发送的邮箱，而这个邮箱的密码是：sgg**_|_**|***|**cc，通过SMTP协议将要偷取的信息发送出去。下图是涉及在黑客工具中植入的后门往163邮箱发送数据的代码：

![p36](http://drops.javaweb.org/uploads/images/114e85de7796d266ac956f91e3a8bb1902405b46.jpg)

随后使用木马中配置的账号和密码进入这个发件邮箱，我们当然会摸进邮箱里去看看了。在收件箱中有41封邮箱，发件箱中有388封，已删除邮箱有5封，而这些数据仅是近一个月的数据。

![p37](http://drops.javaweb.org/uploads/images/d877dc7f9a9e5f86aedd2bd57e177d9e9a13f966.jpg)

![p38](http://drops.javaweb.org/uploads/images/b21c22f487ba3c0ce49d6edf03e19aeb67718d06.jpg)

通过统计所有邮件头中的“Received”包含的IP，可以看到有不少中招小黑交了大量的学费。

![p39](http://drops.javaweb.org/uploads/images/b41e8dfa14fe3c9f105636723a8a29e714a67952.jpg)

在这些邮件中，不仅有小黑们的木马配置信息，还有大量扫描出来的IP及相对应的账号和密码信息。

![p40](http://drops.javaweb.org/uploads/images/6f9dcdcb81bf0f82677dd309cbc04aebd9bc23b4.jpg)

![p41](http://drops.javaweb.org/uploads/images/85c92618ce55730965c12d6cd480f087c9c07f7f.jpg)

在黑产圈子，没有黑吃黑才是不正常的，关于工具后门其实还有可说的，请期待天眼实验室的下一篇扒皮。

比较逗的是，这个服务器上的黑客工具居然有感染了“Parite”病毒，可能是我们在翻服务器文件时激活的（论服务器也安个360的重要性），以致于最新更新的大灰狼远控也被感染了。

![p42](http://drops.javaweb.org/uploads/images/fcca5fc76f94a33ce57414281ef00ccd2efba1be.jpg)

因为“Parite”会使得系统变慢，不停的弹出文件保护的窗口，使大灰狼远控不再免杀，可能因为这个原因小黑发现异常把系统重做了导致我们对服务器失去控制。

0x05 总结
=======

* * *

就这样，我们零距离观察了一台多功能的黑产工作站（只是众多机器之一），我们的发现大致可以归纳成如下的图：

![p43](http://drops.javaweb.org/uploads/images/c2cbb875bc05c1fb8278e1cbc89154eb99f8efde.jpg)

操作这些的是新时代的Script Kiddies，他们租个服务器，找些自动化的撸站工具，程序开起来就算开干了，充当产业链上最初级的角色，在他的环节里通过现成的渠道变点现。他们所使用的服务器工具存在漏洞，撸站工具包含后门，甚至都处理不了恶意代码的感染，因这些问题的损失都是技能不足交的税。他们最容易被分析和打击（如果有人想打击的话），但是，这一切都不会影响他们的活动，只要能不怎么花力气的挣点钱。

另外，天眼实验室还在招人，恶意代码分析方向，海量多维度的数据带来不同的眼界，投条请往：[zhangshuting@360.cn](mailto:zhangshuting@360.cn)

0x06 威胁信息
=========

* * *

以下就是些入侵指示数据，尽管现在威胁情报很热，但目前国内的安全设备对于机读IOC的支持并不广泛，也就不装模作样地提供什么OpenIOC或STIX格式的XML了，读者可以根据自己的需要加入到设备的检测目标里。

| 类型 | 值 | 备注 |
| :-- | :-- | :-- |
| MD5 | 27C8E69F7241476C58C071E83616D2B5 | YY某主播视频.exe |
| MD5 | E4C62055D1BCEB88D97903562B9E1BE8 | hexSB360.exe |
| MD5 | B846B1BD3C4B5815D55C50C352606238 | usp10.dll |
| MD5 | 59F7BC439B3B021A70F221503B650C9C | SSH最终版（稳定）.exe |
| MD5 | 7218C74654774B1FDE88B59465B2748C | filter32.exe |
| Domain | qq867126996.3322.org | CC地址 |
| Domain | q332299.f3322.net | CC地址 |
| Domain | luanqi.net | CC地址 |
| Domain | lyisi.org | CC地址 |
| Domain | sb.jiushao.net | CC地址 |
| Domain | huo-dian.com | CC地址 |
| Domain | www.000268.cn | 钓鱼网站 |
| Domain | www.dlyymy.cn | 黑客网站 |
| email | dt0598@outlook.com | 注册大量钓鱼网站 |
| email | qiangseo@126.com | 注册大量枪支推广网站 |