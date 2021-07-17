# ZigBee 安全探究

0x00 研究背景
=========

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/93d0108b11dac7e98f8a770a99e0521d92cafc9a.jpg)

在2015年初，小米发布新款产品——小米智能家庭套装【如图1】，由多功能网关、人体传感器、门窗传感器和无线开关四个产品组成，它们有一个共同的特点就是均支持 `ZigBee` 协议。之所以没用到WiFi和蓝牙，主要是考虑到两个方面：低功耗和多设备连接。由于WiFi耗电，蓝牙最多支持7个设备，不能自组网，因此小米采用ZigBee协议。

正是基于未来智能设备可能使用到`ZigBee`协议，因此才对ZigBee协议的通讯原理和安全性进行研究，以为将来的智能设备研究作技术铺垫。

同时，最近刚开的`BlackHat USA` 与`Defcon`黑客大会上分别有2个关于ZigBee安全的议题，于是把之前5月份研究的部分内容整理成本文，如有误，欢迎指正。

0x01 ZigBee简介
=============

* * *

`ZigBee` 是一个基于 `IEEE802.15.4` 标准（2.4 Ghz 频段）的低功耗局域网协议，是一种短距离、低功耗的无线通信技术，最大传输速率为250 Kbps，普遍传输范围在10~100米。通常情况下，手机通过WiFi或蓝牙即可实现对智能设备的控制，但若使用ZigBee协议，就需要使用适配器或连接控制中心才能使用，其中小米多功能网关就是用来连接其它ZigBee设备的，其它小米设备使用内置电池可使用长达2年以上，这就是ZigBee的优缺点。

目前已有一些智能家居系统使用到ZigBee协议，被应用于门窗、家电、安防等用途，下图是ZigBee 智能家居系统的应用场景【如图2】：

![enter image description here](http://drops.javaweb.org/uploads/images/b83e6d781fa8c0f256b7ba04d7d6f7267d1973b2.jpg)

0x02 ZigBee安全机制
===============

* * *

（注：对于本节内容，可能在新版ZigBee协议标准中会有所变化，请以新版为准。）   ZigBee主要提供有三个等级的安全模式：   1、 非安全模式：为默认安全模式，即不采取任何安全服务，因此可能被窃听；

2、 访问控制模式：通过访问控制列表(`Access Control List`, `ACL`，包含有允许接入的硬件设备MAC地址) 限制非法节点获取数据；

3、 安全模式：采用AES 128位加密算法进行通讯加密，同时提供有0，32，64，128位的完整性校验，该模式又分为标准安全模式（明文传输密钥）和高级安全模式（禁止传输密钥）。   在一些模式里面又分有多种安全子级，整体来看可以直接参考Wireshark里面提供的安全级别（`Edit=>Preferences=>Protocols=>ZigBee NWK`）【如图3】，里面也支持预设密钥用于解析数据包。

![enter image description here](http://drops.javaweb.org/uploads/images/74538603d53a40a00a9f5e290b0550df302a7e58.jpg)

如果使用安全模式，那么它会提供3种类型的密钥用于保证通讯安全：

**主密钥（`Master Key`）：**用于配合ZigBee对称密钥的建立（SKKE）过程来派生其它密钥，也就是说，设备要先拥有信任中心（ZigBee网络中有且仅有的一个可信任设备，负责密钥分发与管理，以及网络的建立与维护）生成的主密钥才能派生网络密钥和链路密钥给其它设备，它可以由信任中心设置，也可基于用户访问数据，比如个人识别码（PIN），口令或密码等信息；

**网络密钥（`Network Key`）：**用于保护广播和组数据的机密性和完整性，同时也为网络认证提供保护，被网络中的多个设备所共享，仅在广播消息中使用；

**链接密钥（`Link Key`）：**用于保护两个设备之间单播数据的机密性和完整性，仅通讯中的2个设备持有，而单个设备需要多个链接密钥来保护每个端对端会话。

在ZigBee Pro（更高安全级别的ZigBee版本）中，管理员使用对称密钥建立方法来派生设备上使用的网络密钥和链接密钥，但是这要求设备拥有从信任中心生成的主密钥，同时要求设备已经加入网络。关于密钥生成的方法主要有两种方式：

**1、 密钥传输：**采用此方法后，网络密钥与链接密钥可能以明文形式发送到网络中的其它设备，因此密钥有可能被窃听到，从而解密出所有通讯数据，或者伪造合法设备去控制相应智能设备。为了避免密钥明文传输，以及实现不同厂商设备之间的兼容性，协议还提供有默认的信任中心链接密 （`TCLK：0x5A 0x69 0x67 0x42 0x65 0x65 0x41 0x6C 0x6C 0x69 0x61 0x6E 0x63 0x65 0x30 0x39`）去加密传输的密钥，这就引入新的安全风险。此次BlackHat大会的`ZigBee Exploited`议题也正是通过该默认密钥去ZLL灯泡进行攻击，实现远程控制。

**2、 预安装：**在设备上直接配置好密钥，如果需要更改，就需要重新刷设备固件，虽然这种方式更加安全可信，但也是最繁琐复杂的方式。此次360安全团队在Defcon大会上演示的正是对某种智能灯泡的固件进行逆向，从中找到密钥，从而实现对智能设备的控制。

0x03 安全风险
=========

* * *

### 1、窃听攻击

  当ZigBee采用非安全模式时，对传输数据将不作加密处理，因此可能被外部窃取到通讯数据【如图4】。

![enter image description here](http://drops.javaweb.org/uploads/images/580381caff6905b8668196ddde5fbb0aaf26bea3.jpg)

### 2、密钥攻击

  由于在密钥传输过程中，可能会以明文形式传输网络/链接密钥【如图5】，因此可能被窃取到密钥，从而解密出通讯数据，或者伪造合法设备。也有可能通过逆向一些智能设备固件，从中获取密钥进行通讯命令解密，然后伪造命令进行攻击。

![enter image description here](http://drops.javaweb.org/uploads/images/149a373bea0e1933099658576ec0a6a936a2e4ba.jpg)

有些联合厂商在ZigBee基础上作了改进，比如`ZigBee Light Link`（ZLL）全球互联照明标准（源自2014年第二届家电节能与智能化技术大会）就采用ZLL密钥对传输密钥进行一次AES 128位加密再发出去【如图6】，以避免密钥泄露的情况，该ZZL密钥是ZigBee联盟在产品认证后授予的。

![enter image description here](http://drops.javaweb.org/uploads/images/b87ce2cf3d42cae6beb29e49d6400bcc030bf108.jpg)

0x04 总结
=======

* * *

目前针对ZigBee协议的攻击，主要还是围绕密钥安全问题进行攻击。虽然ZigBee的流行度和使用范围并没有达到像WiFi、蓝牙那样普遍，但随着此次小米智能家庭套装的引用，可能会带动一波厂商使用到智能设备之中，因此有必要继续关注下ZigBee在智能设备中的安全问题。

0x05 参考资料
=========

1、 ZigBee Specification Document 053474r17：[http://home.deib.polimi.it/cesana/teaching/IoT/papers/ZigBee/ZigBeeSpec.pdf ](http://home.deib.polimi.it/cesana/teaching/IoT/papers/ZigBee/ZigBeeSpec.pdf%C2%A0)

2、 KillerBee - Practical ZigBee Exploitation Framework

3、 Security Issues And Vulnerability Assessment Of ZigBee Enable Home Area Network Implementations

4、 ZigBee技术及其安全性研究_虞志飞

5、 ZigBee Exploited （BlackHat USA 2015）：[http://cognosec.com/zigbee_exploited_8F_Ca9.pdf](http://cognosec.com/zigbee_exploited_8F_Ca9.pdf)

6、 Take Unauthorized Control Over ZigBee Devices（Defcon 23）：[https://media.defcon.org/DEF%20CON%2023/DEF%20CON%2023%20presentations/Speaker%20&%20Workshop%20Materials/Li%20Jun%20&%20Yang%20Qing/DEFCON-23-Li-Jun-Yang-Qing-I-AM-A-NEWBIE-YET-I-CAN-HACK-ZIGB.pdf](https://media.defcon.org/DEF%20CON%2023/DEF%20CON%2023%20presentations/Speaker%20&%20Workshop%20Materials/Li%20Jun%20&%20Yang%20Qing/DEFCON-23-Li-Jun-Yang-Qing-I-AM-A-NEWBIE-YET-I-CAN-HACK-ZIGB.pdf)

7、 docs-09-5378-00-0mwg-zigbee-security

8、 docs-05-3765-00-0mwg-zigbee-security-layer-technical-overview

9、ZigBee 3.0 – The Open, Global Standard for the Internet of Things

来自 @腾讯安全平台部