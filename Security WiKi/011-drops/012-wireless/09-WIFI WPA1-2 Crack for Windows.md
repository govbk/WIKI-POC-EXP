# WIFI WPA1/2 Crack for Windows

0x00 前言
=======

* * *

目前WIFI WPA破解主要 以“aircrack-ng”为代表，运行于Linux系统( 如Kali Linux )，Windows系统比较少见，主要是Windows系统下WIFI网卡收发原始包比较困难，且缺少有主流WIFI网卡开源代码可参考。因此WPA破解通常流程是先在Linux机器（或Linux虚拟机）在抓取WPA 四次握手包，然后再通过以“Elcomsoft Wireless Security Auditor”为代表的密码字典爆破软件在Windows下进行破解。

0x01 WIFI协议基础
=============

* * *

*   **AP (Access Point)：**WIFI热点，通常是一个WIFI路由设备
*   **SSID（Service Set Identity）：**AP的名称，0-32个字符组成
*   **BSSID（Basic Service Set Identity）：**基本服务集标识，通常是AP的MAC
*   **STA（STATION）：**连接到AP的客户端
*   **DS：**分布式系统，多个AP可以组成分布式无线系统。
*   **DA：**目标MAC地址
*   **SA：**源MAC地址
*   **WIFI数据帧：**WIFI数据帧主要分为物理层、MAC层、数据层。物理层通常

由具体硬件处理，实际只需要考虑MAC（Media Access Control）和LLC（逻辑链路控制），具体数据帧如下：

![p1](http://drops.javaweb.org/uploads/images/b92a5060c6e8173b42df3b84719acff053dafe67.jpg)

MPDU是MAC层的协议头，其中常用的是FrameControl字段和Addr1、Addr2、Addr3等。

*   **ToDs/FromDS：**指明了MPDU地址格式，具体组合如下。

![p2](http://drops.javaweb.org/uploads/images/c33e8277e604a837f73a1160edcb83c1cb92ef07.jpg)

WIFI协议的MPDU头长度不是固定的，是可变的。

**Type/SubType：**共同指明了接下来的数据帧的格式，其中Type 2bits，指明了帧类型，SubType 4bits，进一步指定了数据的具体格式。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Type</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">00/管理帧</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">01/控制帧</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">10/数据帧</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">11/保留</td></tr></tbody></table>

WPA破解时用到的主要有WIFI管理帧和数据帧，其中管理帧对应的SubType情况见下表：

![p3](http://drops.javaweb.org/uploads/images/f53baacc083d23a279a58f4f6b646cd2bce7d869.jpg)

STA在登录AP前，首先需要通过一系列的管理帧，建立同AP的数据联系，然后才能实施登录并启用加密数传，同时WIFI管理帧是不加密的，具体流程如下：

| 序号 | SubType | 说明 |
| --- | --- | --- |
| 1 | 8 | Beacon，STA接受AP信标帧，感知到AP，获取SSID及AP参数 |
| 2 | 4 | STA主动发送Probe探测请求 |
| 3 | 5 | AP应答STA Prob Response |
| 4 | 11 | STA发送Authentication请求认证 |
| 5 | 11 | AP应答Authentication请求，指示STA认证成功或失败 |
| 6 |  | STA发送Association请求 |
| 7 | 1 | AP应答Association Response |

一旦STA完成上述流程后，STA和AP之间即可进行数据帧传输，以便接下来的WPA用户认证。

0x02 WPA密码破解原理
==============

* * *

WPA-PSK(WPA个人版)在STA和AP建立数传后，使用了EAPOL（Extensible Authentication Protocol OVER LAN）协议处理用户的登录认证，具体由四次握手组成，如下图。

![p4](http://drops.javaweb.org/uploads/images/3793f1fde0727e3957c98efc0618147d47e21914.jpg)

AP首先向STA发送一个32字节的ANonce随机数（实际上一般是累加计数器），STA收到该随机数后，自己也产生一个32字节的SNonce随机数，同时根据这两个随机数以及登录密码计算出一个PTK（Pairwise Transient Key），具体计算过程如下：

**1、PMK = PBKDF2(HMAC−SHA1, pwd, ssid, 4096, 256)**

首先使用PBKDF2（Password-Based Key Derivation Function 2）算法生成一个32字节的PMK key，该算法需要执行4096*2轮，WPA破解时运算量主要集中在该key的计算，同时由于使用了SSID（0-32字符）进行salt，导致很难使用彩虹表进行预计算。

**2、**PTK = PRF-512(PMK, “Pairwise key expansion”, Min(AP_Mac, Sta_Mac) ||Max(AP_Mac, Sta_Mac) || Min(ANonce, SNonce) || Max(ANonce, SNonce))

PTK使用PRF-512（pseudo random functions 512bits）算法产生，通过PMK、固定字符串、AP_Mac、Sta_Mac、ANonce、SNonce六个输入参数得到一个64字节PTK。

![p5](http://drops.javaweb.org/uploads/images/ab0dbd4d7585915f133c45cf73a9a65ad2010601.jpg)

PTK由5部分组成，如下：

![p6](http://drops.javaweb.org/uploads/images/df673ccdcf0a4b71c6e6eaacaf07b0834a3b5f5f.jpg)

WPA1 TKIP的PTK长度512bits，WPA2 CCMP的PTK长度为384bits，其中KCK用来计算WPA EAPOL KEY消息的MIC；AP使用KEK加密WPA EAPOL KEY消息的额外Key Data数据；TEK用于单播数据加密。

WPA破解最关键的部分就是通过KCK计算MIC，其算法如下：

**WAP MIC**= HMAC(**EVP_sha1()**,`KCK`, 16, eapol_data，eapol_size)**WAP2 MIC**= HMAC(**EVP_md5()**,`KCK`, 16, eapol_data，eapol_size)

总结一下WPA具体破解流程如下：

| 序号 | 说明 |
| --- | --- |
| 1 | 抓取4-way握手包，实际上只需要前两次即可 |
| 2 | 通过密码字典计算PMK |
| 3 | 通过PMK、ANONCE、SNONCE、MAC1、MAC2计算PTK |
| 4 | 通过PTK得到KCK，计算第2次EAPOL报文对应的MIC |
| 5 | 同第2次EAPOL报文中MIC比较，匹配则密码正确 |

0x03 Window WIFI数据包收发
=====================

* * *

目前Windows下比较成熟的WIFI数据包收发软件是CommView for WiFi，该软件是一款商业软件，兼容的网卡较多，功能也比较强大。该软件的BMD目录下有一个比较通用的WiFi Capture Driver，结合互联网搜集整理的资料发现，Windows NDIS6框架下能够实现WIFI数据包收发功能，决定使用NDIS6 Filter Driver进行WIFI数据包收发。

### 调试开发环境

使用VirtualBox + VirtualKD + Windbg + RTL8187 USB WIFI网卡，目标系统Window7 x86，注意VirtualBox需要安装VirtualBox扩展包，否则无法将主机USB网卡切换到虚拟机中调试。 Windows WDK 7600编译环境，WDK中的filter、usbnwifi示例源码极具参考价值，filter是NDIS 6 NDIS Filter示例代码，usbnwifi是usb wifi网卡驱动的一个参考代码，在没有实际USB网卡驱动源码的情况下，可以大致了解底层网卡的一些实现细节。

### WIFI数据嗅探

NDIS6框架下底层网卡最终通过调用NdisMIndicateReceiveNetBufferLists指示上层NDIS驱动接受数据包，查看该函数调用情况如下：

![p7](http://drops.javaweb.org/uploads/images/efb3ccc82d600a08bec5da8e9b5596bcacf4dd4c.jpg)

主要有三个地方调用了该函数，分别是**MpHandleRawReceiveInterrupt**、MpHandleDefaultReceiveInterrupt、MpHandleSafeModeReceiveInterrupt，重点看前两个函数，在**MpAdjustReceiveHandler**函数中有如下初始化代码：

![p8](http://drops.javaweb.org/uploads/images/018ab00da530729020e8033b5b0af0e6f22f72ce.jpg)

很明显，这两个函数对应了不同网卡模式下WIFI网卡的数据接受函数，在WIFI破解时需要将网卡设置成monitoring mode。

**MpAdjustReceiveHandler**在**MpSetCurrentOperationMode**时被调用，在MpSetInformation函数中：

![p9](http://drops.javaweb.org/uploads/images/a000b84e9fe0e0e216ddbcaf5770d87829f40ecd.jpg)

`OID_DOT11_CURRENT_OPERATION_MODE`是NDIS 标准WIFI OID请求，用来设置WIFI网卡的工作模式，定义的模式有：

![p10](http://drops.javaweb.org/uploads/images/f8855b99917a3d5ce4cb48101a805e5e4ff561b2.jpg)

总结一下WIFI破解时，数据接受的处理流程就是：首先设置网卡为监控模式（混杂模式），然后在网卡驱动之上的Filter驱动里，处理原始数据包接受，通常可以先接受到临时队列里，再在应用层使用IoControl读取该队列，实现WIFI数据包嗅探。

### WIFI数据发送

NDIS小端口驱动通过NdisMRegisterMiniportDriver注册驱动程序，注册的同时需指明Ndis数据发送函数。

![p11](http://drops.javaweb.org/uploads/images/b5a4e27a2195f71a9d40ba7e15b25f3e135b8721.jpg)

该函数中会首先检查网卡的状态，如果状态不合适就不会继续发送数据包，具体检查代码如下：

![p12](http://drops.javaweb.org/uploads/images/5d42a9622bb04a1dad38a82802665422bcd64915.jpg)

`MP_ADAPTER_CANNOT_SEND_PACKETS`宏定义如下：

![p13](http://drops.javaweb.org/uploads/images/f6032caceb35d48cd729471715480fda8a809ae2.jpg)

`MP_ADAPTER_CANNOT_SEND_MASK`掩码定义如下：

![p14](http://drops.javaweb.org/uploads/images/57002355dd83349e58de062c0b8898e274ce3e23.jpg)

注意其中高亮的部分，很明显，微软的NDIS USB WIFI驱动示例代码默认是不允许在监控模式下发包的，鉴于WDK示例代码的权威性，有理由相信，采用该WDK模版代码修改的USB WIF驱动都不能在监控模式下发包，这也是Windows WIFI破解需要面临的一个大问题。

既然官方驱动不能在监控模式下发包，那么就只能自己动手了，直接给官方驱动打个简单的Patch，找到关键的检测位置，然后手动patch一下好了。当然实际厂商的驱动可能会有所不同，需要多调试和测试好。

总结下WIFI破解时，数据发送的处理流程如下：首先找一款支持监控模式下能发包的网卡和驱动（CommView for WIFI自带的驱动应该都可以），或者手动Patch好官方驱动，然后在应用层IoControl写Raw WIFI数据到Filter驱动，Filter构造NET_BUFFER_LIST，最后使用NdisFSendNetBufferLists将数据发送给底层WIFI网卡驱动。

0x04 WPA破解流程
============

* * *

WPA破解主要分为如下几个具体步骤，一是开启网卡嗅探模式，对周围WIFI数据包进行捕获，二是分析周围AP和STA的分布情况，为Deauth攻击做好准备，三是实施Deauth攻击，四是捕获EAPOL握手数据包。

### 开启网卡嗅探

NDIS6通过`OID_DOT11_CURRENT_OPERATION_MODE`设置网卡的工作模式，因此直接通过驱动发送OID设置网卡模式即可，该OID对应的参数数据结构为`DOT11_CURRENT_OPERATION_MODE`，具体如下：

![p15](http://drops.javaweb.org/uploads/images/4cfd6eb309e122afa80794abebd75511bf19e69d.jpg)

通过内核直接发送OID会出现一些问题，主要是Windows WIFI应用层不能即时获取通知，导致Windows应用层在嗅探模式设置功能后，尝试连接网络，出现模式干扰，但CommView就不会出现该情况。

分析CommView驱动后发现，CommView并没有在驱动里面进行具体模式的设置，而是在应用层ca2k.dll调用了Wlan API设置监控模式。

![p16](http://drops.javaweb.org/uploads/images/fc7c1c93da9c27be4909726d843602f3c6e28a89.jpg)

WlanSetInterface的OpCode码为12，对应：

`wlan_intf_opcode_current_operation_mode`（12），具体代码如下：

![p17](http://drops.javaweb.org/uploads/images/b990b6c9472c52aef6a812a7f277c739c140d985.jpg)

### AP/STA探测

WPA破解时需要用到AP的SSID以及MAC地址，AP探测主要通过信标帧以及探测应答帧来实现，具体如下：

![p18](http://drops.javaweb.org/uploads/images/e67e0dcc9b8a089cdd2d816ffc7a7ec7923218f5.jpg)

WIFI信标帧格式如下

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DOT11_MGMT_HEADER</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DOT11_BEACON_FRAME</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DOT11_INFO_ELEMENT</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">INFO...</td></tr></tbody></table>

其中`DOT11_MGMT_HEADER`、`DOT11_BEACON_FRAME`是固定的，AP的MAC地址可以从`DOT11_MGMT_HEADER`中获取，固定头后跟了一个`DOT11_INFO_ELEMENT`的列表，定义如下：

![p19](http://drops.javaweb.org/uploads/images/a492c7e65bdf49e237cbda3c22369c1591758396.jpg)

需要依次遍历其中**ElementID**，获取AP的一系列属性，一些常用的ID定义如下：

![p20](http://drops.javaweb.org/uploads/images/4b46f86d952428259fc87950c6a0bdee62886f9e.jpg)

分别对应AP的SSID、当前频道、WPA2参数等。

STA的探测主要通过数据帧来实现，WPA破解目前只用到了STA的MAC地址，根据每个数据帧的FromDS、ToDS情况，解析数据包MAC地址，即可实现抓取在线通信的STA地址，具体如下：

![p21](http://drops.javaweb.org/uploads/images/eab7ac50eba310b1ad87271778014b66a81cc66f.jpg)

### Deauth攻击

根据WIFI协议规定，客户端在接受到Deauth管理帧后，应该主动断开同AP的连接，一旦断开后，STA会自动尝试重连，这时就方便抓取EAPOL四次握手包了，因此成功实施Deauth攻击可以极大提高WPA破解的效率。

Aircrack里面的Deauth攻击模版如下：

![p22](http://drops.javaweb.org/uploads/images/217c5a1abf6d9e6e63f9ced7d5fbcf867d3ab221.jpg)

其中`\xC0\x00`指明了该帧是Deauth管理帧，最后的`\x02\00`指定了本次Deauth的Code码，Aircrack里是`\x06\x00`，区别起见，修改了下。

发送Deauth攻击时，将DA替换成目标STA的MAC地址（或广播），SA、BSSID填上AP的MAC即可。

![p23](http://drops.javaweb.org/uploads/images/6f6072560661414d636852eb957f3a4bd63adf62.jpg)

### EAPOL捕获

EAPOL帧的识别比较简单，因为802.1x数据帧前，LLC（逻辑链路控制）头会有一个标识0x888e，直接内存搜索即可定位EAPOL帧，稍微麻烦一点的是要确定当前EAPOL包在四次握手中次序，因为在实际网络嗅探时，有很大可能出现漏抓的情况。

EAPOL数据包格式如下：

![p24](http://drops.javaweb.org/uploads/images/3c3e5dc61dccb34317631e469d9d1b381db603d7.jpg)

其中ProType=3表示是Key，Key描述数据结构如下：

![p25](http://drops.javaweb.org/uploads/images/108d51bebcb6d9a1c4116f3f5d6ac93032102c04.jpg)

其中`KEY_INFO`数据定义了一系列的标志位，EAPOL四次握手时，各个阶段的标志位会不尽相同，通过分析这些标志位情况，可以获取其在四次握手时的次序。一旦监控到一次的完整四次握手，即可认为当前AP握手包抓取成功。