# OQL(对象查询语言)在产品实现中造成的RCE(Object Injection)

0x00 前言
=======

* * *

前几天,有几个屌丝高帅富给我看一个这样的漏洞类型:

地址:http://blog.emaze.net/2014/11/gemfire-from-oqli-to-rce-through.html

GemFire内存数据库是来自云计算公司Pivotal(未来我最看好的云计算产品提供商,由EMC、VMware、通用电气这三家公司合资等方式组成,这里有我们熟悉Spring技术团队支撑的就是这家公司云计算前端开发框架)的产品.

0x01 内存数据库基础
============

* * *

那什么是内存数据库,为什么需要它?给大家举个简单的例子:

在百度中搜索: GemFire,排在第5位的结果就是我们的答案

![enter image description here](http://drops.javaweb.org/uploads/images/cfa5fcb1692cfdcf8eee395d7d93bc48a7ca05b4.jpg)

我们知道中国是个人口大国,由于地域经济差异大,外出打工挣钱的人特别多.逢年过节买火车票一直有个头痛的问题,就是关键时候这个网站就打不开了.无论它体验及性能有多烂,我们还是要去上它,因为要回家(这是刚需),随着国人网上预订越来越多,存在并发访问量爆表的问题,庆幸的是它一直在通过技术手段解决这个问题.

并发访问与数据库技术的演变简单描述可能是:开始使用关系数据库,如:Oracle,并发量大会挂;然后使用数据在内存做缓存，如：memcached (因为读写内存要比读写硬盘快很多,可极大提升访问性能),还是有性能问题;所有后来就干脆使用云计算数据库解决产品GemFire（充当一下国外新产品的小白鼠）,不知道今年过年买票能否不挂?拭目以待!

但GemFire内存数据库在数据存储中并非简单的字符串,如:"123456"；而是Java对象，所以它也是个对象数据库，比如：我们在J2ME开发中使用的DB4o也是。学过J2EE持久层框架的人都知道,如: Hibernate; ibatis等,就是把关系数据库中的每张表映射到内存中(ORM,表的字段对应内存中Java对象的属性),另外还有一个特点,Java对象中可以放更为复杂的对象结构(如:迭代对象,数据集合).再进行数据传输操作,就非常方便了,抛弃传统关系数据库操作概念.而GemFire内存数据库支持更为强大的对象操作API,OQL(Object Query Language)

那什么是OQL?百度就简单几句话,大家很难理解:

http://baike.baidu.com/view/2554236.htm?fr=aladdin

这里举个例子就清晰了:它类似SQL

如，sql查询表user的字段name为test的数据，sql语句是：

> sql ="select * from where name ='test' ";

而oql可能就是这样：

> oql=" select referrers(u) from xxx.xxx.User u where u.name = 'test' ";

这里简单解释一下语法及语义：xxx.xxx为对象包路径，在返回引用对象xxx.xxx.User中name对象为test的引用对象。是不是更为强大？OQL还有更多更为强大的API.

而形成的新漏洞类型对比SQL注入漏洞就更好理解了，sql注入是外部参数污染sql语句，OQL注入是外部参数污染oql语句。这里更要命的是oql语句是支持java代码语义及语法解析的（可以理解为我们之前熟悉的OGNL表达式注入），所以这个漏洞类型为：OQL注入漏洞（Object Injection），最大的利用就是远程代码执行，最大危害就是执行系统命令了。

0x02 实例分析
=========

* * *

说了这么多，大家肯定会说给个例子吧,别光YY! 我们知道学习技术也是要成本的，GemFire内存数据库，对于我这样的穷人现在是用不起的！但不影响我们去学习OQL这门对象查询语言。

它其实就在我们的JDK中：

首先，我们启动任何一个Java程序，我这里是个Tomcat,再找到它的PID,如图：

![enter image description here](http://drops.javaweb.org/uploads/images/94b9ea3eb9a0e51ad4902564aef2c0c266191f76.jpg)

然后使用jmap命令生成堆转储快照，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/5f4783210821a7adf0320886ce8ac24693a8ff5f.jpg)

然后使用堆分析命令jhat,它是个http服务，默认端口7000，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/48297ed5054c3d13c4bc4971bdeaa4a24faea029.jpg)

我们就可以使用浏览器查看堆信息了，它还提供我们前面需要的OQL查询功能，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/a83f243be0a2e3fc0e665150693a2449979867ae.jpg)

查询长度大于100的字符串：

![enter image description here](http://drops.javaweb.org/uploads/images/29729adf9719b98b9055f5e29d88ea3efd8ac5d7.jpg)

Java代码执行系统命令也不需要老外说的那么复杂，还使用反射？（当然，看语句拼接情况）：

![enter image description here](http://drops.javaweb.org/uploads/images/9f9367ebf87b1a24832d5dfe1aff30914cc78c3a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0574e0736a0b7e9a0ff3fed3eb9ff0e4235a6231.jpg)

未来使用对象数据库会越来越多，而漏洞类型已经不是我们之前熟悉的SQL注入漏洞了，而是OQL注入，危害就更为严重了(不仅限于Java)。