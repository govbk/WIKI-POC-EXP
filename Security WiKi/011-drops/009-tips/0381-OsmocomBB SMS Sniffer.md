# OsmocomBB SMS Sniffer

**Author:绿盟科技博客**

0x00 简介
=======

* * *

![p1](http://drops.javaweb.org/uploads/images/57bcb38ee69df4f931d077184c3e5010d0c0ccf6.jpg)

OsmocomBB(Open source mobile communication Baseband)是国外一个开源项目，是GSM协议栈(Protocols stack)的开源实现。其目的是要实现手机端从物理层(layer1)到layer3的三层实现，主要进行2G网短信嗅探。本文详细地介绍了实现方法，以供安全爱好者学习和参考。

目前来看，真正的物理层(physical layer)并没有真正的开源实现，暂时也没看到实施计划。只有物理层控制。因为真正的物理层是运行在baseband processor的DSP core上,涉及到许多信号处理算法的实现，而且还要牵扯很多硬件RF的东西。这项技术至少在2010年，技术已经成熟，2011年就有开源实现了。得益于OsmocomBB 的开源项目，使得我们用一台笔记本和很简单的硬件就能完成GSM sms嗅探。

0x01 原理分析
=========

* * *

### 关于加密

GSM加密采用A5算法。A5算法1989年由法国人开发，是一种序列密码，它是欧洲GSM标准中规定的加密算法，专用于数字蜂窝移动电话的加密，用于对从电话到基站连接的加密。A5的特点是效率高，适合硬件上高效实现。

A5发展至今，有A5/1、A5/2、A5/3、A5/4、A5/5、A5/6、A5/7等7个版本，目前GSM终端一般都支持A5/1和A5/3，A5/4以上基本不涉及。值得注意的是，A5/2是被『故意弱化强度』的版本，专用于『出口』给『友邦』，2006年后被强制叫停，终端不允许支持A5/2。

### 工作流程

手机开机时的位置更新流程：

1.  MS（手机）向系统请求分配信令信道（SDCCH）；
2.  MSC收到手机发来的IMSI可及消息；
3.  MSC将IMSI可及信息再发送给VLR，VLR将IMSI不可及标记更新为IMSI可及；
4.  VLR反馈MSC可及信息信号；
5.  MSC再将反馈信号发给手机；
6.  MS倾向信号强的BTS，使用哪种算法由基站决定，这也导致了可以用伪基站进行攻击。

### 关于GSM网络相关知识

![p2](http://drops.javaweb.org/uploads/images/6d204baa6ae0de351107dc8ee5572fb386e425e3.jpg)

0x02 所需硬件
=========

* * *

支持的手机

*   MotorolaC123/C121/C118 (E88) — our primary target
*   MotorolaC140/C139 (E86)
*   MotorolaC155 (E99) — our secondary target
*   MotorolaV171 (E68/E69)
*   SonyEricssonJ100i
*   Pirelli DP-L10
*   Neo 1973 (GTA01)
*   OpenMoko – Neo Freerunner (GTA02)
*   SciphoneDreamG2 (MT6235 based)

我们选择Moto C118，因为官方支持的最好、硬件成本低，￥35/台（手机+电池+充电器）

![p3](http://drops.javaweb.org/uploads/images/01abf6d2f5e6f298c92c5bd23f1ad56543deb68a.jpg)

### USB转串口模块

推荐带TX/RX LED的 FT232模块,当然其他模块也可以,比如CP2102、CP2303等模块,不过使用前要先调好比特率。FT232模块，我买的是￥35的，第一个嘛，为了求稳定。后面做多个手机联合嗅探的时候可以尝试买一些便宜的。

![p4](http://drops.javaweb.org/uploads/images/8b0197e89d0e4b636ef0b7ab69ae1369b6660c2b.jpg)

### C118数据线

这个数据线就是2.5mm耳机头转杜邦线，注意一头是2.5mm耳机孔的，另一边是杜邦线连接串口模块。手边有2.5mm耳机插头的可以自己做一个。当然网上现在也有现成的了，不过成本稍微高一点。￥15左右一条

![p5](http://drops.javaweb.org/uploads/images/962f88dd8a04b8bb030b6e6d733545c66792f51f.jpg)

### MiniUSB链接线

这个线应该都有，以前的mp3、手机啥的都是这个线，马云家卖￥10,如果你用了Pl2303那类的USB转换板，就可以不用这根线了，那个板子上自带U口。

![p6](http://drops.javaweb.org/uploads/images/f98860f6eb7034a41961e3cf6ec9c24aaa464999.jpg)

0x03 编译OsmocomBB
================

* * *

### 基础环境

MacOs 10.10.5 + VMworkstation + Ubuntu 12.04 x64

我的实验用的是这样的环境，网上很多教程都说X64的虚拟机不能正常编译，但是我确实是成功了。也可以尝试使用别的环境试试，毕竟我的实验环境仅供参考。

网路环境要求能够正常访问github，实验环境周围存在GSM信号。

C118手机有足够的电量，支持实验。

### 准备所需目录以及文件

具体项目目录结构和所需文件如下图：

![p7](http://drops.javaweb.org/uploads/images/0e0583b998510acd582855210d693169a9f6411f.jpg)

准备好之后的目录如下图：

![p8](http://drops.javaweb.org/uploads/images/2b26b467a334dd931a7481c81b4a8bed0c254f47.jpg)

我是把整个source目录放在了用户文件夹下，仅做参考。只需要按照上面文字格式的结构图准备就好，图片中未出现部分后面会写如何出现…

### 编译环境准备

编译前安装所需的依赖库文件：

```
sudo apt-get install build-essential libgmp3-dev libmpfr-dev libx11-6 libx11-dev texinfo flex bison libncurses5 libncurses5-dbg libncurses5-dev libncursesw5 libncursesw5-dbg libncursesw5-dev zlibc zlib1g-dev libmpfr4 libmpc-dev

```

![p9](http://drops.javaweb.org/uploads/images/c8ff393081a371badc60159fe63bb0092189c243.jpg)

在arm根目录执行build.sh文件进行build操作:

```
chmod +x gnu-arm-build.2.sh ./ gnu-arm-build.2.sh

```

![p10](http://drops.javaweb.org/uploads/images/b83549d35a6f49906377181df87d2b2992e4f120.jpg)

完成后arm/install/目录结构如图所示：

![p11](http://drops.javaweb.org/uploads/images/84b089b2eb666dcd68fa97c30a535340d28d2c32.jpg)

因为编译需要，把arm/install/bin路径加入到环境变量中，我这里是加入到用户的环境变量中。使用pwd命令获取绝对路径：

![p12](http://drops.javaweb.org/uploads/images/b848374758f6ba000381a1dafcd5fd12a3804909.jpg)

修改`~/.bashrc`文件，最后一行加入：

```
export PATH=$PATH:/home/wooyaa/source/arm/install/bin

```

执行source命令让配置文件即时生效：

```
source ~/.bashrc

```

在终端中输入arm然后按tab键，如果出现如下图所示就说明编译环境搞定了：

![p13](http://drops.javaweb.org/uploads/images/d628639586ef2a11b0d8d4ff94ded5672a2d44d9.jpg)

### 编译OsmocomBB

把osmocom项目gitclone到source目录下：

```
git clone git://git.osmocom.org/osmocom-bb.git git clone git://git.osmocom.org/libosmocore.git

```

在libosmocore/目录中编译osmocom核心库文件

```
cd /home/wooyaa/source/libosmocore/ autoreconf -i ./configure make sudo make install

```

编译OsmocomBB：

```
cd /home/wooyaa/source/osmocom-bb/src/ git checkout –track origin/luca/gsmmap //选择分支 make //交叉编译

```

如果没什么问题，软件环境和固件就都编译好了。

Ununtu 12.04自带FT232R驱动，所以直接连接就能使用，不需要再装驱动。

### 常见错误

常见报错有可能是autoconf、libtool、libpcsclite-dev等文件的缺失，只要装好就行了。具体版本请使用`apt-cache search xxx`在你自己电脑中的apt-get的list中查找。

0x04 使用方法
=========

* * *

### 连接硬件

在终端中输入`lsusb`,会显示当前usb连接的信息：

![p14](http://drops.javaweb.org/uploads/images/d9db4e27d998633606f37530d8fca004755ef1f8.jpg)

如果驱动正常，插上MiniUSB线后就能看到usb-serial:

![p15](http://drops.javaweb.org/uploads/images/638f488cd81fb7b6cc0424d783939c91c2aff1f7.jpg)

网上的教程大多都误认为是将firmware刷入手机，实际上这里只是把固件加载到手机RAW中执行。

### 加载Firmware到手机raw中

```
cd /home/wooyaa/source/osmocom-bb/src/host/osmocon/./osmocon -m c123 -p /dev/ttyUSB0 ../../target/firmware/board/compal_e88/layer1.compalram.bin

```

1.  其中 –m c123跟c123xor的区别就是是否检测数据总和
2.  上面命令需要在关机下执行，然后短按开机键

终端上会显示”starting up”字样，如下：

![p16](http://drops.javaweb.org/uploads/images/7b90c50abdd078629a8d64ccbe8b43b22ba17a00.jpg)

手机屏幕显示Layer 1 osmocom-bb 字样就表示成功了：

![p17](http://drops.javaweb.org/uploads/images/c8625a590b1dafd13902ecace79c7c28ecb2aad1.jpg)

### 扫描基站

```
cd /home/wooyaa/source/osmocom-bb/src/host/layer23/src/misc/sudo ./cell_log –O

```

其中cell_log的参数是字母O，具体作用是只检查ARFCN是否可用，不进行其它操作，可以用./cell_log –help参看说明。

终端中会输出日志信息，其中会包含能够收到的基站的相关信息，格式类似这样：

```
cell_log.c:248 Cell: ARFCN=40 PWR=-61dB MCC=460 MNC=00 (China,China Mobile)

```

ARFCN后面的编号可以代表基站信道号，还包含了运营商信息。

![p18](http://drops.javaweb.org/uploads/images/1f064c9eb61d55cc22a639716d7cba585b768371.jpg)

### 关于嗅探

因为我们买的便宜货，每个手机只能嗅探一个信道，具体一些的，可以参考下面的图（我们现在只能抓Downlink的数据包）：

![p19](http://drops.javaweb.org/uploads/images/91c28c1e8b3fb9a38a380a8cf9d094c8b817f4f8.jpg)

因为想要Sniffer Uplink的包，要修改硬件，C118主板上的RX filters要换掉，换成我们需要的HHM1625&&HHM1623C1滤波器组件，才能抓Uplink的数据包。

有关信道号ARFCN的问题，可以参考下面的图：

![p20](http://drops.javaweb.org/uploads/images/8ecced9fd379f4e448bad74831a4491d17b20abc.jpg)

### 开始嗅探

选择想要监听的信道号并开始嗅探广播数据。

在目录/home/wooyaa/source/osmocom-bb/src/host/layer23/src/misc/下执行嗅探：

```
./ccch_scan -i 127.0.0.1 -a THE_ATFCN_ID

```

其中THE_ATFCN_ID就是扫描到的日志中参数ARFCN的值。

苹果手机可以执行：3001#12345# 进入工程模式后，选择GSM Cell Environment->GSM Cell Info->GSM Serving Cell,就可以看到目前手机连接的基站ARFCN值了，应该在第二步中，也能看到这个ID存在。

其他手机的命令

`Samsung (Android): *#0011#`

![p21](http://drops.javaweb.org/uploads/images/6c38cda3024d3b5d65b6b7b96f3d02172de297c7.jpg)

使用wireshark抓取监听数据

因为osmocomBB执行之后默认会在本地开启4729端口，这时候的GSM协议已经被封装上了TCP-IP，可以在本地用wireshark抓到，所以我们使用wireshark去监听4729的端口

```
sudo wireshark -k -i lo -f 'port 4729'

```

![p22](http://drops.javaweb.org/uploads/images/abfd9c6c30f3b977f40aff2eebcea36b05b884fe.jpg)

在wireshark中过滤gsm_sms协议数据，过滤之后得到的数据里面就包含短信的明文信息。 过滤后得到的明文短信信息

![p23](http://drops.javaweb.org/uploads/images/c037f329a0130866d29e3212d71c1096ff95982c.jpg)

SMS text就是短信的明文内容，其他git分支还支持把监听到的数据保存到cap包，然后通过脚本来过滤包内容，达到嗅探短信明文的目的。后面会有计划的去尝试。

### 配置OsmocomBB

layer23是用/home/wooyaa/source/osmocom-bb/src/host/layer23/src/mobile下的mobile程序实现,所以通过执行mobile文件可以进行自定义，配置一些关于osmocom-bb的信息。

```
cd /home/wooyaa/source/osmocom-bb/src/host/layer23/src/mobile
sudo ./mobile -i 127.0.0.1

```

执行mobile程序之后，会在本地开启4247端口，使用telnet连接，然后配置执行，随时使用？来查看help信息。

![p24](http://drops.javaweb.org/uploads/images/d9e53a1ceb6d023ac7adbe7918dd48747623486d.jpg)

### 关于嗅探内容

简单来讲，短信接受者的号码、IMEI等数据，只有在”Location Update”时才会在网络中出现，并且是以加密形式传输的。当接收短信时，基站根据之前位置更新时注册的信息，判断接收者的位置。所以，想要拿到接受者的号码，需要破解A5/1算法并还原出”Location Update”时的原文。

只不过需要价格昂贵的USRP2…

另外还看到个RTL-SDR的文章（就是以前传说中可以跟踪飞机的电视棒），也支持Airprobe：

[http://www.rtl-sdr.com/rtl-sdr-tutor…and-wireshark/](http://www.rtl-sdr.com/rtl-sdr-tutor%E2%80%A6and-wireshark/)

### Tips

1.  记住所有操作在`sudo -s root`权限下操作。
2.  开机键不是长按，而是短按，否则就进入原系统了。
3.  现在2G短信越来越少了，多等等会有的。理论上话音一样能够被监听及解码，只是涉及技术更为复杂。
4.  CP210x的接线，RX和TX有可能需要对调。运行cp210x-program需要先安装ibusb-dev，如果输出是“No devices found”或“Unable to send request, 3709 result=-110”，则有问题。

0x05 后期计划
=========

* * *

### 捕获上行包

因为想要嗅探Uplink的包，要修改硬件，C118主板上的RX filters要换掉，换成我们需要的HHM1625&&HHM1623C1滤波器组件，才能抓Uplink的数据包。修改方法如下：

要使手机能够成为『passive uplink sniffer』，必须动到电烙铁，替换掉RX filters。

替换前：

![p25](http://drops.javaweb.org/uploads/images/d28c1b6e2b5f0c6e1905a3ce625225cf3dfba883.jpg)

摘掉后：

![p26](http://drops.javaweb.org/uploads/images/0288af84947321ccf75f6b3ae9f86a806bc4fce8.jpg)

替换后：

![p27](http://drops.javaweb.org/uploads/images/d273768c5c704b3e5063889162ad70d709db5b39.jpg)

使用OsmocomBB RSSI monitor查看信号强弱：

```
./osmocom-bb/src/host/osmocon/osmocon -p /dev/ttyUSB0 -m c123xor -c ./osmocom-
bb/src/target/firmware/board/compal_e88/rssi.highram.bin ./osmocom-
bb/src/target/firmware/board/compal_e88/chainload.compalram.bin

```

由于RSSI太大，不便于像OsmocomBB那样直接加载，所以要先用-C参数加载一个小的chainloader程序去加载我们真正的RSSI Payload程序：

![p28](http://drops.javaweb.org/uploads/images/c1eb8efe79a35d252298f626f37eb4083b9559fa.jpg)

### 短信内容实时web页面展示

制作成绵羊墙，在线实时显示嗅探到的短信

### 多设备联合嗅探

尝试多设备一起嗅探，增强嗅探范围和效果

0x06 附录
=======

* * *

### DIY Moto C118数据链接线

![p29](http://drops.javaweb.org/uploads/images/09555d705fe488ae65147bcbbb2a65e4fa34c5a5.jpg)

图中例子耳机为moto T191的耳机，右图中标注的颜色为耳机线拆开后里面线芯的颜色。耳机线拆开后里面会包含3根带有外皮的铜线。

### GSM网络相关知识

![p30](http://drops.javaweb.org/uploads/images/70098a38e8d899e60fc0ac4dbe9ca9b9a9d78b46.jpg)

从协议图中得知，移动设备(MS)和基站(BTS)间使用Um接口，最底层就是刷入手机的**layer1物理传输层**，之上分别是**layer2数据链路层和layer3网络层**。

![p31](http://drops.javaweb.org/uploads/images/9ec5b11833abaa9df7b1b4ce0e3d1a9490b33cf2.jpg)

位于图中layer2的LAPDm，是一种保证数据传输不会出错的协议。一个LAPDm帧共有23个字节（184个比特），提供分片管理控制等功能。

layer3的协议则可以分为RR/MM/CM三种，这里只列出嗅探相关的功能：

*   RR(Radio Resource Management)：channel, cell（控制等信息，可以忽略）
*   MM(Mobility Management)：Location updating（如果需要接收方号码，需要关注这个动作）
*   CM(Connection Management)：Call Control（语音通话时的控制信息，可以知道何时开始捕获TCH）, SMS（这里的重点）

![p32](http://drops.javaweb.org/uploads/images/91df25bfeb059188544ad8fb32234ed4f265c9e7.jpg)

参考GSM的文档 TS 04.06 得知 LAPDm 的Address field字段中，定义了 3.3.3 Service access point identifier (SAPI)。SAPI=3就是我们要的Short message service。 使用tcpdump配合show_gsmtap_sms.py脚本在console列出短信明文。

```
tcpdump -l -ilo -nXs0 udp and port 4729 | python2 -u show_gsmtap_sms.py

```

### 一些名词解释

*   MS：Mobile Station，移动终端；
*   IMSI：International Mobile Subscriber Identity，国际移动用户标识号，是TD系统分给用户的唯一标识号，它存储在SIM卡、HLR/VLR中，最多由15个数字组成；
*   MCC：Mobile Country Code，是移动用户的国家号，中国是460；
*   MNC：Mobile Network Code ，是移动用户的所属PLMN网号，中国移动为00、02，中国联通为01；
*   MSIN：Mobile Subscriber Identification Number，是移动用户标识；
*   NMSI：National Mobile Subscriber Identification，是在某一国家内MS唯一的识别码；
*   BTS：Base Transceiver Station，基站收发器；
*   BSC：Base Station Controller，基站控制器；
*   MSC：Mobile Switching Center，移动交换中心。移动网络完成呼叫连接、过区切换控制、无线信道管理等功能的设备，同时也是移动网与公用电话交换网(PSTN)、综合业务数字网(ISDN)等固定网的接口设备；
*   HLR：Home location register。保存用户的基本信息，如你的SIM的卡号、手机号码、签约信息等，和动态信息，如当前的位置、是否已经关机等；
*   VLR：Visiting location register，保存的是用户的动态信息和状态信息，以及从HLR下载的用户的签约信息；
*   CCCH：Common Control CHannel，公共控制信道。是一种“一点对多点”的双向控制信道，其用途是在呼叫接续阶段，传输链路连接所需要的控制信令与信息。

**参考文献**

*   [https://github.com/osmocom/osmocom-bb](https://github.com/osmocom/osmocom-bb)
*   [http://bb.osmocom.org/trac/wiki/TitleIndex](http://bb.osmocom.org/trac/wiki/TitleIndex)
*   [http://wulujia.com/2013/11/10/OsmocomBB-Guide/](http://wulujia.com/2013/11/10/OsmocomBB-Guide/)
*   [https://blog.hqcodeshop.fi/archives/253-iPhone-cell-Field-Test-mode.html](https://blog.hqcodeshop.fi/archives/253-iPhone-cell-Field-Test-mode.html)
*   [http://bbs.pediy.com/showthread.php?t=182574](http://bbs.pediy.com/showthread.php?t=182574)
*   [http://www.blogjava.net/baicker/archive/2013/11/13/406293.html](http://www.blogjava.net/baicker/archive/2013/11/13/406293.html)