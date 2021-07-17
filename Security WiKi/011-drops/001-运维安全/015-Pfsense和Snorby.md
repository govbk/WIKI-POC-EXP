# Pfsense和Snorby

0x00、背景
-------

* * *

黑客攻击是不可避免的，常在江湖飘，哪有不被黑（谁也不敢说自己的网络是绝对安全的）。被黑了怎么办？？？肯定是第一时间修复漏洞和清除后门啦！该怎么修复漏洞了？？？漏洞又在那里了？？？这个时候研究IDS的人就出来：

IDS：全称入侵检测系统。专业上讲IDS就是依照一定的安全策略，通过软、硬件，对网络、系统的运行状况进行监视，尽可能发现各种攻击企图、攻击行为或者攻击结果，以保证网络系统资源的机密性、完整性和可用性。

IPS：比IDS再高大上点的就是IPS，IPS全称是入侵防御系统。IDS是发现并不做动作，IPS是在IDS发现了攻击企图或者行为后，采取动作。

0x01 Pfsense&Snorby简介
---------------------

* * *

pfSense是一个基于FressBSD，专为防火墙和路由器功能定制的开源版本。它被安装在计算机上作为网络中的防火墙和路由器存在，并以可靠性著称，且提供往往只存在于昂贵商业防火墙才具有的特性(如vpen、IDS、IPS)。

Snorby是一个Ruby on Rails的Web应用程序，网络安全监控与目前流行的入侵检测系统（Snort的项目Suricata和Sagan）的接口。该项目的目标是创建一个免费的，开源和竞争力的网络监控应用，为私人和企业使用。

0x02 Snorby的安装部署
----------------

* * *

首先要设置安装源（要使用epel源）

Snorby git官网https://github.com/Snorby/snorby

这里告诉你怎么安装，我就不啰嗦了。

详细安装看这里：http://hi.baidu.com/huting/item/7a60eb725e66cb206e29f6b8

（只要安装第一篇即可。）

在这里snorby只是对数据进行分析，并不抓取数据，抓取数据由pfsense里面的Suricata来抓取。抓取到的数据保存到snorby所在服务器的mysqld中，snorby通过调用本机mysql数据库中的数据进行分析。

所以Snorby服务器只要放到pfsense可以访问到的地方即可以了。

可以发到外网么？？？应该也可以的，这里就没去试了。

安装好后，如下：（默认用户名：snorby@snorby.org，密码：snorby）

[![](http://static.wooyun.org/20141114/2014111405525698475.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file00011.png)

点击上面Settings，下面有个时间设置（注意这个很重要，时间不对很麻烦的）

[![](http://static.wooyun.org/20141114/2014111405525754069.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file00022.png)

下面那个500000是一个很重要的参数。（这是一个峰值）

[![](http://static.wooyun.org/20141114/2014111405525741309.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0003.png)

0x03 pfsense的部署与配置
------------------

* * *

Pfsense的安装这里不介绍了，网上到处都是。

Pfsense是一款防火墙肯定是部署在网络的边界啦！这个也没啥好说的。

A. 下载并安装Suricata软件包

System->Packages,如下图：

[![](http://static.wooyun.org/20141114/2014111405525734858.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0004.png)

[![](http://static.wooyun.org/20141114/2014111405525750979.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0005.png)

[![](http://static.wooyun.org/20141114/2014111405525864393.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0012.png)注意：在做这之前要设置好dns，不然无法解析域名，你就无法下载了。

B.全局配置（Global Settings）

安装完成后，在Services中找到Suricata，对其进行基本配置。

界面如下

[![](http://static.wooyun.org/20141114/2014111405525883996.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0006.png)

我们首先在Global Settings(全局设置)进行基本设置，全局设置分为三部分。

1.规则的下载[![](http://static.wooyun.org/20141114/2014111405525820190.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0007.png)

应该是有四种选择，第二和三是要code的。

不知道申请要不要钱，我这里就没去试了。

2.是规则的更新设置

[![](http://static.wooyun.org/20141114/2014111405525939807.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0008.png)

我这里设置的是一周一次。

3.一般设置

[![](http://static.wooyun.org/20141114/2014111405525933915.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0009.png)

这里就有一个很关键的设置了。

Remove Blocked Hosts Interval 我这里设置的是15分钟，默认是NEVER。

这个是什么意思了？？其实这个涉及到后面要提到的IPS，当IPS发现威胁时候就会将目标添加到Blocked，在Blocked里面的ip地址将不允许通过防火墙。

我这里设置15分钟，也就是15清除一次Blocked里面的ip地址。

C.其他设置

规则库下载

[![](http://static.wooyun.org/20141114/2014111405525927599.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file00101.png)

上面已经设置好了，这里点击Check，下载规则文件。

pass lists（这里就是一个白名单）

[![](http://static.wooyun.org/20141114/2014111405525991367.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0011.png)

这里不多介绍，下面提到IPS在说这个。

0x04 Pfsense+Snorby==IDS&IPS
----------------------------

* * *

启用IDS功能 Pfsense关键配置 添加监控网卡[![](http://static.wooyun.org/20141114/2014111405525943848.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file00131.png)

这里我只有两张网卡，我选择的是WAN，外网口。（要勾选上面那个框框）

[![](http://static.wooyun.org/20141114/2014111405525960470.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0014.png)

设置Iface Categories

[![](http://static.wooyun.org/20141114/2014111405530038600.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0015.png)

这里，我是选择所有，然后保存。（可以工具自己的需求选择） 设置Iface Rules

[![](http://static.wooyun.org/20141114/2014111405530087113.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0016.png)

这里选择Auto-Flowbit Rules(自动转发规则)，然后应用。

设置iface Barnyard2(关键)

[![](http://static.wooyun.org/20141114/2014111405530034051.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0017.png)

下面那个启用mysql是关键，这里填写Snorby服务器上的mysql的信息

（注意：mysql要开启远程访问，上面的每页做完一次配置，要save一次）

基本的IDS配置就完成了，如下图。

[![](http://static.wooyun.org/20141114/2014111405530014022.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0018.png)

点击上面的红叉叉即可以启动。

启动后的效果。

[![](http://static.wooyun.org/20141114/2014111405530124799.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0019.png)

如果成功了的话，在snorby上面可以看到效果的，效果图如下：

[![](http://static.wooyun.org/20141114/2014111405530160005.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0020.png)

我来扫下看看效果，我用nmap轻轻的扫下

[![](http://static.wooyun.org/20141114/2014111405530197371.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0021.png)

我在虚拟机里面弄的，那是相当的卡啊！！！！！！

牛逼吧！直接就看到了你是用nmap在扫描。

[![](http://static.wooyun.org/20141114/2014111405530131648.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0022.png)

启用IPS功能

在WAN Settings里面有一个Alert Settings，如下图：

[![](http://static.wooyun.org/20141114/2014111405530110663.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0023.png)

设置后选保存，然后重启Suricata生效。

第二个勾很霸气，发现某ip有危险，直接断开所有与此ip的连接。

IPS这里重点提下白名单的设置

第一步、设置aliases

Firewall下面的Aliases(自己添加)

[![](http://static.wooyun.org/20141114/2014111405530270002.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0024.png)

第二步、设置Pass Lists

[![](http://static.wooyun.org/20141114/2014111405530258985.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0025.png)

[![](http://static.wooyun.org/20141114/2014111405530225206.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0026.png)

Save，

在WAN Settings设置里面

[![](http://static.wooyun.org/20141114/2014111405530282029.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0027.png)

点击保存，重启Suricata生效。

还有最后一个设置，就是被封的ip什么时候解封。

上面提过的Global Settings里面的General Settings。

[![](http://static.wooyun.org/20141114/2014111405530239553.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0028.png)

这里设置的是15分钟。

也就是15分钟后，被封的ip自动解封。

说明：本文旨在抛砖引玉，大家大可以根据自己的需求自行配置。文章写的不是很详细，如果详细写，估计得20来页。