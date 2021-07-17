# 狗汪汪玩转无线电 -- GPS Hacking (上）

0x00 序
======

* * *

GPS Hacking 在过去几年的安全会议上一直都是很受关注的议题. 但往往因为内容太过学术化, 所需设备成本太高. 让许多感兴趣的朋友苦于无法入门. 直到GPS-SDR-SIM 这类开源项目的出现, 跟王康大牛在今年Blackhat Europe 2015 上的主题演讲. 彻底打开了GPS 的神秘面纱. 让小伙伴可以真正过一把GPS Hacking 的瘾.

想必大家对于研究GPS的神器, 软件无线电SDR都略有所闻. 但早期设备USRP价格昂贵. 直到大家发现了神奇的电视棒 RTL-SDR. 前阵子似乎人人都喜欢用它来看大"灰机". 不过因为硬件上的限制，电视棒只能用来收取数据. 而 HackRF 跟 BladeRF 因其支持收发数据, 而价格又比USRP 便宜许多. 便成了当下热衷玩无线的朋友们的首选. 当然HackRF 跟 BladeRF之间也在所支持的频率, 采样率上有所不同. 最重要的一点BladeRF是全双工哦. 以下是几款SDR 设备之间的对比图, 大家可以根据具体需要选购.

![p1](http://drops.javaweb.org/uploads/images/5825794586dad22c2e941eee326b680b4da47744.jpg)

**GPS系统简介**

GPS 系统本身非常复杂, 涉及到卫星通信等各个领域. 这里只是简单介绍一下. 我们通常所说的 GPS 全球定位系统是由美国国防部建造完成. 目前在太空中共有31颗卫星在同时运作. 一般我们需要至少4颗卫星来完成三角定位. GPS卫星同时发送民用L1和军用L2两种无线信号. 我们通常使用的是没有加密的L1民用 1575.42MHz 的超高频波段.

GPS 信号里包含了3种常用信息.

Pseudorandom code: 简单的ID 码, 用来识别每颗卫星.

Ephemeris data: 包含卫星的运行状态, 时间日期等信息. 这在通过卫星来定位起到非常重要的作用.

Almanac data: 包含有每颗卫星的轨道信息，以及卫星在某个特定时段将出现的具体位置.

![p2](http://drops.javaweb.org/uploads/images/31898f0884c70d96e18e836fd6df515b5526f650.jpg)

0x01 BladeRF GPS 信号伪造步骤
=======================

* * *

**1.1 在Ubuntu 14.04.3 中安装 BladeRF 工具**

![p3](http://drops.javaweb.org/uploads/images/3798b43e7c8b2f00e12569dd4515cee8645dd333.jpg)

安装 header 文件

![p4](http://drops.javaweb.org/uploads/images/a418294407eb95f71ac9ad62488de6e776f72916.jpg)

安装 BladeRF 固件 & FPGA 镜像

![p5](http://drops.javaweb.org/uploads/images/0117fda768dcaa56af26a592d075a2925ff47141.jpg)

完成后可在`/usr/share/nuand/BladeRF/`下找到`hostedX40.rbf`跟`bladerf_fw.img`文件. 这时便可将BladeRF插入USB接口.通常系统会自动载入FPGA 镜像.也可以通过命令行`bladerf_cli -l /路径/hostedX40.rbf`手动载入. 在成功载入后，BladeRF主板上的3 个LED 小灯便会亮起, 同时我们可以加`-p`参数来进一步验证系统安装成功.

![p6](http://drops.javaweb.org/uploads/images/8316458128a0ceb0cca5c453d99196e39d71b791.jpg)

**1.2 GPS-SDR-SIM 安装**

```
git clone https://github.com/osqzss/gps-sdr-sim.git 
cd gps-sdr-sim  
gcc gpssim.c -lm -O3 -o gps-sdr-sim

```

设置经纬度并生成数据样本. 注意这里 I/Q基带信号数据为16.

![p7](http://drops.javaweb.org/uploads/images/37a10a8dcb516801829f935c33a895b83519e138.jpg)

随后 gps-sdr-sim 会自动生成带有经纬度信息的数据文件. 我们便可以通过 bladerf_cli 来发送伪造的GPS 数据.

![p8](http://drops.javaweb.org/uploads/images/c3f35d6cc27896762fa9b8b53a33a83f5e214b38.jpg)

**1.3 GPS-SDR-SIM 运行时间问题**

在实际测试过程中汪汪发现, 默认情况下GPS模拟器只能连续工作5分钟左右. 通过查看源代码后, 我们可以发现这是因为程序默认设置导致. 在程序设计之初为了节省硬盘空间, 默认只生成了300秒左右的数据. 我们可以通过改动参数来延長工作時間. 但需要注意的是仅仅延長到15分鐘，數據便可達到5G大小.

![p9](http://drops.javaweb.org/uploads/images/8feaaa3e41b1e41a39021ed852ce8d8de32122e7.jpg)

0x02 GPS信号伪造实战
==============

* * *

汪汪在这里跟分享几个实际的测试案例. 感兴趣的朋友也可以自行测试下.

**2.1 微信周边妹子**

听说许多程序猿因为平时工作紧张, 性格腼腆. 很难有机会跟心中的女神接触. 而微信中”附近的人”则解决了此类问题. 大家只要坐在家中打开GPS定位, 便可跟周边的心仪女神 Say Hello 啦. 但美中不足的是范围仅限几十公里内. 那么对某些胸怀天下, 万花丛中过, 片叶不沾身的大神来说未免太有局限性了. 这里汪汪给大家带来第一个GPS 信号伪造案例 -- 微信”附近”妹子.

听说前阵子在海南三亚有个美女扎堆的活动, 汪汪很是好奇都是啥样的美女呢..让我们来查下附近的人吧. 哦..在没发送伪造的GPS坐标前,只能找到汪汪所在城市的妹子.

![p10](http://drops.javaweb.org/uploads/images/0d24c1bca5d3b85aab2a5eb0bf26b6d6209a7321.jpg)

![p11](http://drops.javaweb.org/uploads/images/f65a5f14b5e16abd6eca33945dd64d29476cc47d.jpg)

在开始发送伪造的GPS坐标5分钟后, 汪汪终于如愿以偿找到了三亚附近妹子 :)

哈哈..汪汪必须感叹下..真的是技术宅改变命运啊...

![p12](http://drops.javaweb.org/uploads/images/ff07cbbea7a81e4b748c7e7266e84bfc06b81b6d.jpg)

**2.2 Nike+ 计步数伪造**

很多喜欢研究移动安全的朋友一定看过蒸米发过的一篇文章 "利用Android Hook进行微信运动作弊".（感兴趣的朋友可以移步观看[http://drops.wooyun.org/tips/8416](http://drops.wooyun.org/tips/8416)). 文中他提到了通过利用Android Hook进行计步作弊, 跟朋友圈里的好友PK运动量. 但该方法需要手机root后，安装相关作弊插件来实现. 对于其他计步类软件，还需要对插件进行相关改动. 这里测试目标为 Nike+ Running. 先来看段视频. 因为完成全部攻击效果需要一定时间, 所以本视频做了加速处理.

![p13](http://drops.javaweb.org/uploads/images/96d24263178e9823d30938edfdee53327d058221.jpg)

[http://player.youku.com/player.php/sid/XMTQwMzAxMTk4OA==/v.swf](http://player.youku.com/player.php/sid/XMTQwMzAxMTk4OA==/v.swf)

通过GPS-SDR-SIM的主页, 我们可以得知伪造的的GPS经纬度数据可以是静态, 也可以是动态模式的. 为了成功模拟出运动轨迹, 我们需要伪造动态模式的GPS经纬度数据. 可以通过以下参数来完成.

```
gps-sdr-sim -e brdc3540.14n -u circle.csv -b 16

```

大家可以看到通过直接对GPS信号进行伪造, 成功欺骗了Nike+ 这类计步器APP. 即使在被窝里躺着,也可以跑第一哦. 当然汪汪还是希望大家可以真的跑起来, 享受运动的快乐.

**2.3 伪造信号范围测试**

从前面几个实验可以知道, 通过软件模拟信号, GPS接收设备在短距离内的效果是非常明显的. 那么在较大范围内GPS接收设备的效果如何呢？实际的有效距离又是多远呢？当然这跟设备的输出功率, 天线增益, 以及附近其他信号干扰程度有关. 所以这里汪汪只是做个简单的室内测试. 大家还是要以实际情况为准. 请先看这段测试视频.

[http://player.youku.com/player.php/sid/XMTQwMzAwNzMxNg==/v.swf](http://player.youku.com/player.php/sid/XMTQwMzAwNzMxNg==/v.swf)

从视频可以看到在这个直线距离大概为25米, 中间无任何障碍物的走廊里成功改变了GPS 接收设备的经纬度. 通常真实的GPS 信号从2万千米的高空下到地面已经非常微弱, 因此在室内几乎检测不到信号. 所以在室内GPS 信号伪造攻击的效果是很明显的.

![p14](http://drops.javaweb.org/uploads/images/84b0c6f0fba0b80668adf3baeb646a4260243b5f.jpg)

0x03 总结
=======

* * *

通过以上几个案例, 相信大家对GPS 信号伪造有了一定程度的了解. 但就GPS系统本身而言, 这是一个非常好玩又很深的领域. 市面上的GPS 相关产品也总类繁多, 每款产品对GPS 欺骗攻击的反应也各不相同. 大家可以发挥下想象力玩出新花样.

最后要感谢 osqzss; 王康和无数 GNURadio 爱好者们的无私分享. 正因为有了他们，我们才可以更好的体验软件无线电的无穷魅力. 推荐大家围观 GPS-SDR-SIM 的项目主页和王康在黑帽大会上的演讲稿. 拥有HackRF设备的朋友也可以看看lxj616写的“劫持GPS定位&劫持WIFI定位”.

0x04 参考文献
=========

*   [http://drops.wooyun.org/tips/10580](http://drops.wooyun.org/tips/10580)
*   [https://github.com/osqzss/gps-sdr-sim](https://github.com/osqzss/gps-sdr-sim)
*   [https://en.wikipedia.org/wiki/GPS_signals](https://en.wikipedia.org/wiki/GPS_signals)
*   “Time and Position Spoofing with Open Source Projects” Kang Wang
*   [http://www.taylorkillian.com/2013/08/sdr-showdown-hackrf-vs-bladerf-vs-usrp.html](http://www.taylorkillian.com/2013/08/sdr-showdown-hackrf-vs-bladerf-vs-usrp.html)