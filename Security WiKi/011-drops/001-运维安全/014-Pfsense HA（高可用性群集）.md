# Pfsense HA（高可用性群集）

0x00 前言
=======

* * *

前段时间公司防火墙所在物理机死机了，导致公司网络瘫痪。公司各网站无法访问，所以才想到去研究这个Pfsense HA。正好公司在准备举办一个比赛，作为安全工作者，肯定有压力啦！！各个方面都要去考虑是否存在安全隐患。这个防火墙必然也在考虑的范围之内，如果这个防火墙被破坏者弄挂了怎么搞了？？？那比赛是不是就没法进行了。

这名字有点高大上的感觉啊！其实说白了，就是弄两pfsense防火墙，一台挂了，另外一台马上接管工作，不至于中断业务。

0x01 Pfsense&&HA简单介绍
====================

* * *

pfSense是一个基于FressBSD，专为防火墙和路由器功能定制的开源版本。它被安装在计算机上作为网络中的防火墙和路由器存在，并以可靠性著称，且提供往往只存在于昂贵商业防火墙才具有的特性。

HA(High Available), 高可用性群集，是保证业务连续性的有效解决方案，一般有两个或两个以上的节点，且分为活动节点及备用节点。通常把正在执行业务的称为活动节点，而作为活动节点的一个备份的则称为备用节点。当活动节点出现问题，导致正在运行的业务（任务）不能正常运行时，备用节点此时就会侦测到，并立即接续活动节点来执行业务。

0x02 Pfsense HA深入
=================

* * *

简单绘了个拓扑图：

![enter image description here](http://drops.javaweb.org/uploads/images/d7a64048052ed659ea3946f9e9c956cdbe7e2e04.jpg)

拓扑图确实有点不咋的啊！可以说是有点难看，有什么好的软件可以给我推荐下啊！

简单的说下上面那个图，这个实验我是在我的虚拟机上面弄的。

Pfsense1 + Pfsense2 = Pfsense HA

WAN:192.168.1.101 192.168.1.102 192.168.1.254

GW: 192.168.1.1 192.168.1.1 192.168.1.1

LAN:1.1.1.1 1.1.1.2 1.1.1.254

也就是在三层交换机上只要一条默认路由就好，这个条默认路由就指向1.1.1.254。 这个ip是由Pfsense1和Pfsense2虚拟出来的。

如果你仔细观察的话，会发现我少了东西。呵呵！就是中间不是还有一根线么？？？

怎么你这里没体现出来了？？？？

中间这根线是心跳线，是 MASTER 和BACKUP 通信用的，当BACKUP发现MASTER挂了，它就会自动切换状态变成MASTER。这里我用的LAN口这根线做为心跳线。（这样有个缺点就是广播包有点多，对交换机的负担相对有点重）

注：在弄Pfsense HA过程中Pfsense1和Pfsense2有两个状态一个是MASTER，一个是BACKUP。

![enter image description here](http://drops.javaweb.org/uploads/images/c5b663be089a6fdc0868e1e22e76219c53c4ee1c.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/321a9ef5b755729d2c0007440226cc6ed5878dcd.jpg)

0x03 具体实现Pfsense HA
===================

* * *

A 增加虚拟ip
--------

![enter image description here](http://drops.javaweb.org/uploads/images/a1ec97864a00d060aad38702da534d8b52d2c45c.jpg)

增加wlan口的虚拟ip

![enter image description here](http://drops.javaweb.org/uploads/images/5b69311789aa3b028219815beff09f65e2394f21.jpg)

增加lan口的虚拟ip

![enter image description here](http://drops.javaweb.org/uploads/images/36b6fdf7335ef6752eafe56e635aee7a02e0f657.jpg)

都弄完成了

![enter image description here](http://drops.javaweb.org/uploads/images/da37b85d68d4cda7d67540a92c8d99e4d130747c.jpg)

B CARP设置
--------

![enter image description here](http://drops.javaweb.org/uploads/images/7d9b6c7b4ca5e3377e5356e9c649f8e2f02eac45.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c818aa11134539d18e1da51d08a49420d5975972.jpg)

下面还有各种同步选项，请根据自己的实际情况去勾选。

弄好了后，你就可以登录到http://1.1.1.254/index.php 上去配置。

也就是MASTER防火墙上去配置。在MASTER防火墙上配置了数据会同步到BACKUP（有个前提啊！前提是你勾选了那个勾。），所以不用当心这个数据的问题。

0x04 简单的看个端口转发吧
===============

* * *

这里需要在MASTER防火墙做了个端口转发

![enter image description here](http://drops.javaweb.org/uploads/images/a827d9d8135a577c27779840b7c1f88f8e97b0c5.jpg)

到BACKUP上面来看，数据已经同步过来了。

说明下：配置防火墙请一定要到MASTER防火墙上面去配置，在BACKUP上配了是没用的。

![enter image description here](http://drops.javaweb.org/uploads/images/9e1317e1442584ce2e7ea6c45445bcac4208e4f0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c38e6a5542d669885bab1ae85ea7ddadf4dc2b01.jpg)

我把MASTER防火墙关机，BACKUP防火墙马上接管成为MASTER防火墙， 照样不影响访问254。

好吧！就介绍到这里，有问题欢迎大家来和我交流。