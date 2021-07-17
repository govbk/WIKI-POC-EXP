# Splunk实战（一）——索引器配置以及转发器安装配置说明

0x00 前言
=======

* * *

本文将以连载的形式分享splunk在实战中的运用：从索引器&转发器的安装部署开始，到普通搜索&字段提取，再到报表&仪表盘定制以及告警等，详细的写出作者在实战中的经验（其实是遇到的坑），让大家看完之后可以少走些弯路。

0x01 Splunk简述
=============

什么是Splunk？
----------

Splunk是机器数据的引擎。使用 Splunk 可收集、索引和利用所有应用程序、服务器和设备（物理、虚拟和云中）生成的快速移动型计算机数据，随时从一个位置搜索并分析所有实时和历史数据。使用 Splunk可以在几分钟内（而不是几个小时或几天）解决问题和调查安全事件，关联并分析跨越多个系统的复杂事件，从而获取新层次的安全运营以及业务运营可见性。

![](http://drops.javaweb.org/uploads/images/e475b4334bdb9392be983c8c3e53c08fad586d2e.jpg)

Splunk的强大之处
-----------

Splunk 可以从任何源实时索引任何类型的计算机数据，由下图可见，通过端口监听来收集各类服务器或者网络设备的日志，还可以通过脚本来获取系统指标等。

![](http://drops.javaweb.org/uploads/images/bac6aed3f5b5439dd1cd50ff7930fe47c204fc77.jpg)

同时，可以通过在各个操作系统安装部署转发器（forwarder），来实现将各个agent端日志目录文件发送到splunk索引器（indexer）中。下图最底层为forwarder，中间层为indexer。

![](http://drops.javaweb.org/uploads/images/8649ad5aee2a9891b47c0a1a9aad2992f390eb5c.jpg)

简要介绍了一下整体架构，下面我们进入实战环节。

0x02 环境准备
=========

* * *

Splunk索引器
---------

6.3.3版本，IP为10.2.1.157

Splunk转发器
---------

Linux&windows的6.3.3版本

0x03 索引器配置
==========

索引器端需要配置监听端口，以便接收从转发器端发来的日志文件等。在“设置——转发和接收——接收数据”中配置监听9997端口

![](http://drops.javaweb.org/uploads/images/e8c7f8b83348a1ee34d5487ca80857358b206cb5.jpg)

![](http://drops.javaweb.org/uploads/images/db3c7c8c237424143b0beac7632f5172b38894b1.jpg)

另外索引器默认的管理端口是8089，无需配置。

![](http://drops.javaweb.org/uploads/images/e285a346018c86444df53bd6a863e1f36ba28d3d.jpg)

0x04 Windows转发器配置
=================

* * *

准备工作
----

1.  splunk转发器下载地址

https://www.splunk.com/page/previous_releases/universalforwarder

1.  需要在windows server上将”本地安全策略——本地策略——审核策略”中的所有审核策略均配置为”成功“和失败”
    
    ![](http://drops.javaweb.org/uploads/images/716144bfbda59f3abee961cb7dad13bd96f9a891.jpg)
    

安装过程
----

首先复制转发器到相应的服务器上

![](http://drops.javaweb.org/uploads/images/ced1f1b88899b3a8d88c0977ee2e2e4d37f811b9.jpg)

双击执行该文件，如下图所示，勾选接受协议，之后选择“Customize Options”即自定义安装

![](http://drops.javaweb.org/uploads/images/09d5aeef6a10ef417a83210c1a7d82f413d0ac6c.jpg)

路径默认即可

![](http://drops.javaweb.org/uploads/images/4cb9932d73975d0c24ac3b6a1959274534f9b253.jpg)

勾选上“windows Event Logs”以及“Performance Monitor”的全部选项，但不用勾选”AD monitoring”（否则如果在域环境下，索引器会收到大量域内无用消息，极为占用资源），如下图。

![](http://drops.javaweb.org/uploads/images/3e72f200557f801053e12783248f0cf697c248b3.jpg)

这个步骤默认即可。

![](http://drops.javaweb.org/uploads/images/e3bef8c9434620438d4c36ea4fcabec5ae807725.jpg)

（重要！）配置调度服务器（这一步是为了让indexer可以识别到forwarder，并且可以从管理端下发日志采集指令）。 这一步中的IP填写为10.2.1.157，端口填写为8089，如下图。

![](http://drops.javaweb.org/uploads/images/bda9178e8036e824d8380bc63dc66becde1af3bf.jpg)

（重要！）这一步中配置接收索引器（这一步是为了让indexer可以接收到forwarder发来的日志），IP填写为10.2.1.157，端口填写为9997。

![](http://drops.javaweb.org/uploads/images/dea08e107f526dd8dcfff9cc808fac503be8c4a1.jpg)

执行安装过程完毕后，点击Finish结束。

![](http://drops.javaweb.org/uploads/images/8d375266051f374c130e911bf8f143cdcc32ae46.jpg)

最后在索引器中可以看到该转发器已连接上

![](http://drops.javaweb.org/uploads/images/3a034e29524e01bceb602b97a0fca1f9b547231e.jpg)

0x05 Linux转发器配置
===============

* * *

安装过程
----

首先查看当前IP。

![](http://drops.javaweb.org/uploads/images/f38b3125134daad72ebe12ea06a14384e91ba87c.jpg)

从内网服务器下载压缩包：

```
wget http://10.2.24.66/splunkforwarder-Linux.tgz

```

![](http://drops.javaweb.org/uploads/images/0c42b34e491dc962a7a276b646a10a28997a2c92.jpg)

解压。

![](http://drops.javaweb.org/uploads/images/56fd89c118a560ef38cc3af64adf20e996f48328.jpg)

进入`%splunkforwarder%/bin`

![](http://drops.javaweb.org/uploads/images/24f7da695670dc43b0308f3fe97f1744fc338dc0.jpg)

输入`./splunk start`进行安装

![](http://drops.javaweb.org/uploads/images/4e3cff347f3c4e724395080e9e9a9ab8de300f6f.jpg)

输入y，等待安装完成。

![](http://drops.javaweb.org/uploads/images/f80ce757945bf5214d6d3c4c675753c0eb27f290.jpg)

输入`./splunk enable boot-start`，配置为开机启动

![](http://drops.javaweb.org/uploads/images/6dbf6e6025e28920bffb77dec0f876141838a15c.jpg)

（重要！）配置调度服务器（这一步是为了让indexer可以识别到forwarder，并且可以从管理端下发日志采集指令）。

遇到的坑：6.3.3的转发器安装貌似没法通过输入命令来指定对端索引器，如果不搞配置文件的话，索引器是无法感知到这个转发器的。

随后在`%splunkforwarder%/etc/system/local/`配置deploymentclient.conf

其文件内容格式为：

```
[target-broker:deploymentServer]
targetUri = 10.2.1.157:8089

```

如下配置即为成功

![](http://drops.javaweb.org/uploads/images/dd824e8a15742426148a1310f93289efd3b0dd26.jpg)

（重要！）这一步中配置接收索引器（这一步是为了让indexer可以接收到forwarder发来的日志）

另外需要在`%splunkforwarder%/etc/system/local/`配置outputs.conf

```
[tcpout]
defaultGroup = defau；lt-autolb-group    

[tcpout:default-autolb-group]
server = 10.2.1.157:9997    

[tcpout-server://10.2.1.157:9997]

```

如下配置即为成功

![](http://drops.javaweb.org/uploads/images/8a6e5c2c9c6974accc1988536b702504a12010b3.jpg)

配置完conf文件后需要重启splunk服务

![](http://drops.javaweb.org/uploads/images/e2a979e8fc4d168ff98501a7a8ddeb226da74d4e.jpg)

另外，还需要配置`/etc/rsyslog.conf`，设置接收syslog条目为：（为了实现索引分类，这里我将linux的syslog指定发到索引器的516端口）

`* @10.2.1.157:516`

![](http://drops.javaweb.org/uploads/images/4bdfcdf1196fe4fe2215bbae3ebc288bcf064ad5.jpg)

![](http://drops.javaweb.org/uploads/images/42c0e8f131a80ec8c0babcb3c40a6cfbb1da3cd8.jpg)

配置完毕后保存退出，并且重启rsyslog服务。

![](http://drops.javaweb.org/uploads/images/9670de6e775247079544b726a363ca0e91591a1b.jpg)

至此，linux端转发器配置完毕。

随后可看到在server端服务器列表中，该转发器已连接上。

![](http://drops.javaweb.org/uploads/images/7ee5027234dcb5b2c4be87a4fcfe0a54a104331e.jpg)

0x06 添加转发器中的数据
==============

* * *

首先选择“设置——数据导入“

![](http://drops.javaweb.org/uploads/images/947e8fb8a7e1cacceabf46e7647aede649d37b2a.jpg)

选择添加来自于转发器的数据——windows事件日志

![](http://drops.javaweb.org/uploads/images/564b1d425734e6edf501bb450fb904304f6b265e.jpg)

新建一个服务器组

![](http://drops.javaweb.org/uploads/images/7e657019f8978c44fe2e19767fc0630c944a760a.jpg)

由于目前只关心安全日志，只选security即可，如下图。

![](http://drops.javaweb.org/uploads/images/bf494ff7ed8e6051d3983d3d80713429ca9159d3.jpg)

将这些转发器的上述配置好的日志均发送到自己新建的windows索引中，以免在超大的main索引里查询导致效率下降。

![](http://drops.javaweb.org/uploads/images/14f6b1187688d066500f241860347dea25ecab03.jpg)

同理，在”添加数据——文件和目录”功能中，可以直接导入转发器的IIS或tomcat等日志目录所在的路径，配置完毕后由转发器自动将日志发到索引器上来（好像远控有木有）

![](http://drops.javaweb.org/uploads/images/756defa14c1a21a6d9c1a5b10b66bcbc60cd31c0.jpg)

再将不同类别的日志存放到相应的索引中即可。

![](http://drops.javaweb.org/uploads/images/e6a07f38867d9770ebe016cf9f45efe7e446054a.jpg)

最后在搜索时输入index=windows或者index=iis，即可搜到所有转发器发来的日志了。

![](http://drops.javaweb.org/uploads/images/4518d28f6d9eb88b4e13860a6b61e9a648f510f7.jpg)

另外，在上一章节中所配置的linux syslog已经发送到了516端口，所以在这里我们新建一个监听UDP:516的规则

![](http://drops.javaweb.org/uploads/images/25d5bed0f154c115a5e1b496ae8c8323dd542fed.jpg)

并建立一个单独的linux索引来存储发到516端口的UDP数据（即syslog），届时直接搜索index=linux即可。

0x07 简单的报表示例
============

* * *

统计暴力破解SSH的源IP
-------------

先通过linux登录失败的特征字段“failed password”来查询，同时，linux的日志均在名为linux的索引表中，故应该搜索：index=linux failed password。如下图

![](http://drops.javaweb.org/uploads/images/d84326f39be2a32d18e218e091d8a5ee4ecc84cf.jpg)

之后想要统计来源的IP都有哪些，此时点击左侧的“Src_ip”，选择”上限值”，即为发生次数最多的前20个。

![](http://drops.javaweb.org/uploads/images/0810e018fddee5f61df0d4cbb4f4ecaa0856c5d7.jpg)

可以自动生成统计图，直观展示哪些源IP的次数最多。

![](http://drops.javaweb.org/uploads/images/ace54b258b81f98091f71de6b89eca029b31464f.jpg)

之后将Src_ip改为Dst_ip，可以观察哪些linux服务器正遭受暴力破解的威胁。

![](http://drops.javaweb.org/uploads/images/361a31b921ed7462452db589eec1c2d148797f8f.jpg)

至于上面说的Src_ip和Dst_ip是怎么分割出来的，且听下回分解《搜索技巧&字段提取》。