# 通用GPS卫星定位平台漏洞成灾用户位置信息告急

**Author:SudoHac@360攻防实验室**

0x00 前言
=======

* * *

近日，在新闻中曝光了多起通过GPS定位设备，跟踪绑架的事件（[http://news.xinhuanet.com/legal/2015-11/15/c_128429526_2.htm](http://news.xinhuanet.com/legal/2015-11/15/c_128429526_2.htm)）。很多用户都来咨询，有没有方法进行检测？于是就在市面上购买了一些GPS定位设备进行研究，研究发现这些GPS定位系统后台采用的是通用的一套程序，其云平台上存在多个高危漏洞，攻击者利用漏洞可定位到使用该设备的任意用户或车辆的当前位置，历史轨迹，甚至可远程切断行驶车辆的油电。用户使用GPS定位的物品、人员都是非常有价值的，如果这类平台存在安全漏洞，反而将位置信息暴露给不法分子，这会对社会造成非常大的影响。

0x01 简介
=======

* * *

我们在淘宝上搜索gps定位装置，发现绝大多数卖家销售的主流gps定位系统均为同一套程序，均受到漏洞影响。

![p1](http://drops.javaweb.org/uploads/images/3a9cf3fd332deba237feb5a2068d87a7e6e49db7.jpg)

该系统的大致原理和架构如下：

![p2](http://drops.javaweb.org/uploads/images/65c9ac85f5c07d0228ed3e008509d989d07fe240.jpg)

在GPS定位装置里装有一张3G手机卡，定位装置获取到当前位置坐标后通过3g网络传输到云监控平台，用户通过pc或者移动设备登录监控平台，即可定位绑定在自己账号下的设备位置。

0x02 漏洞详情
=========

* * *

以下面这套月成交8000+，累计评价超过22000的定位装置为例。

![p3](http://drops.javaweb.org/uploads/images/7248f9e398fea53c0348e6e11d61fb9b05243363.jpg)

其云平台使用.NET开发，登录界面如下：

![p4](http://drops.javaweb.org/uploads/images/7ba2c3758e4de97400c1be909acc5d9218bfab63.jpg)

对于经销商，输入账号密码可控制其账号下所有设备，对于一般用户，选择输入IMEI和密码可定位单一的设备位置。 通过研究发现，在其云平台上，存在大量可未授权访问的webservice接口，我们通过协议规范调用这些接口，可获取任意用户的信息，修改其密码，甚至定位其位置。

![p5](http://drops.javaweb.org/uploads/images/e61fcc7d2d146bc1aaa7384a3844b94d5155dece.jpg)

![p6](http://drops.javaweb.org/uploads/images/9c1515aceddff05897b66ba610f54b54bfb3985d.jpg)

通过接口将管理员的密码初始化，然后登录查看可以看到，仅仅这一个平台，就有超过25万的设备，当前在线设备就有2.7万。

![p7](http://drops.javaweb.org/uploads/images/6ad77b52b49b295e3d51a1f7f8970ec2d72ac3f2.jpg)

可以直接定位到这些设备的具体地理位置

可以获取到使用该设备的车辆及人员的具体信息（电话、车牌号、姓名等）

![p8](http://drops.javaweb.org/uploads/images/dd8d78a928c76afef59bbf8dbec6ed4bbdb75a0c.jpg)

可以定位到其车辆当前的具体位置：

![p9](http://drops.javaweb.org/uploads/images/278e964b1f36db017a998584dfa35a5ef4f186f3.jpg)

还可以通过历史数据分析车辆的行驶轨迹：

![p10](http://drops.javaweb.org/uploads/images/bbac7e9bef96386204c20c0fda284f3d728f8760.jpg)

甚至可以直接远程切断行驶车辆的油电：

![p11](http://drops.javaweb.org/uploads/images/4a05faedfac70adfdc8e741b0d9432fdf1aa2720.jpg)

通过进一步的研究我们发现，该系统的webservice接口还存在有sql注入漏洞，通过在soap消息中插入恶意数据，我们甚至可直接控制该服务器。

![p12](http://drops.javaweb.org/uploads/images/816cf9661b107ef4dd996cca7b6a4504e16c0c11.jpg)

![p13](http://drops.javaweb.org/uploads/images/489b273bf342dc9fd53e40eea4e216f42ef754e2.jpg)

0x03 漏洞影响
=========

* * *

研究发现，这套商业化的GPS定位程序使用量非常大，用户遍布中国、欧洲、中东、非洲、东南亚等多个地区。

![p14](http://drops.javaweb.org/uploads/images/7bb39388471af1d57eacb4d8111163cba15df18d.jpg)

还包括一些中东地区，战乱地区都比较喜欢用GPS跟踪。这里就体现出GPS的应用场景了。

![p15](http://drops.javaweb.org/uploads/images/1ff028dc41671b2bc6aed627a1cdd406da8e242c.jpg)

![p16](http://drops.javaweb.org/uploads/images/739ecee30beb9e7158ef3b501d0d2f27fc9775b6.jpg)

![p17](http://drops.javaweb.org/uploads/images/42451a9ad261252c2f2f08472f55dabc35ded2dd.jpg)

![p18](http://drops.javaweb.org/uploads/images/8bb03acd863d2af6fedafaaab18963976b2c3da0.jpg)

而且我们发现这套gps定位程序不仅仅被用于车辆定位，还衍生出了儿童手表、人员定位器甚至宠物定位等多个版本。

![p19](http://drops.javaweb.org/uploads/images/660bfaf3f8ea33c54f84f682f63baae7476d60c6.jpg)人员定位器

![p20](http://drops.javaweb.org/uploads/images/a938e04c9e4319bd79ac8b1a0ca6c202fc585a78.jpg)儿童手表

![p21](http://drops.javaweb.org/uploads/images/3964d5b9e038e19ff1380ba06abe9d738139ccd3.jpg)宠物定位

我们从淘宝销售的gps定位装置中选择了多个销量较大的商家测试，发现绝大多数平台都存在漏洞，总数超过了100万台，以下是做的部分统计：

| 商家 | 总设备数量 |
| :-- | :-- |
| www.tourrun.net | 496805 |
| www.zg666gps.com | 253426 |
| www.indlifelocate.com | 252980 |
| ry.i365gps.com | 93638 |
| www.gpsjm.com | 55451 |
| gps.zg002gps.com | 42993 |
| www.mkcx.net | 41894 |
| www.aika168.com | 40586 |
| www.xmsyhy.com | 12645 |
| www.twogps.com | 3587 |
| www.lkgps.net | 3434 |
| ec-dbo.cn | 2961 |

0x04 安全建议
=========

* * *

**如何发现自己的车辆有没有被人装上定位器？**

很多人看到新闻都产生了顾虑，生怕自己的车辆是否被装上了定位器。这里可以告诉大家几个思路去排除，首先这类定位器是装有强磁铁的，所以车上除了这个定位器以外不会有其它的强磁设备，可以去一些磁力检测仪来检测。第二种方法是GPS定位系统是需要用GPS信号的定位车辆的，可以在一个信号屏蔽的环境下检测车辆是否有GPS信号。第三个就是通过利用云平台的漏洞检测自己的车辆轨迹是否被跟踪，这也是没有办法中的办法了。

**以后如何选用GPS定位平台？**

GPS定位的需求很多，因为GPS定位一方面是为了保障用户，但是存在漏洞的被不法分子利用的话，就成了暴露用户位置信息的一条路径，往往需要GPS定位的都是有价值的东西，这就成了攻击者的一块福地。对于GPS产品应当选用可靠的，大品牌的产品。购买前应当在网上搜索一下有没有相关的安全漏洞。如果购买了产品发现有漏洞，建议用户停止使用，等待厂商更新平台漏洞。