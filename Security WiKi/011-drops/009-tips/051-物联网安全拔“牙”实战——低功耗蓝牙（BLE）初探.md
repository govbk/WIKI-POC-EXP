# 物联网安全拔“牙”实战——低功耗蓝牙（BLE）初探

Author: FengGou

0x00 目录
=======

* * *

*   0x00 目录
*   0x01 前言
*   0x02 BLE概述
    *   BLE 协议栈总览
    *   GAP－通用访问规范
    *   GATT－通用属性协议
*   0x03 BLE嗅探
*   0x04 伪造BLE通信
*   0x05 分析BLE私有数据协议（灯泡、跳蛋、小米手环）
    *   1.YeeLight 2 代蓝牙灯泡
    *   2.小爱爱智能跳蛋（这个真不是我的，某个小伙伴借给我研究的）
    *   3.小米手环
        *   番外篇：小米手环认证机制分析
*   0x06 结语
*   0x07 参考资料

0x01 前言
=======

* * *

因为自己曾DIY过所谓的“智能硬件”，学习过程中除了接触各种芯片、传感器、电路知识外，也拆了不少设备分析其设计思想学以致用。再后来又接触了如：Wi-Fi、ZigBee、Bluetooth、NFC、IR、普通射频甚至音频等通信技术，才发现空气中那些形形色色的边界，才是整个物联安全的关键。

今天的内容是我在乌云内部做的技术分享，也是我以前对低功耗蓝牙技术的一些接触，整理后决定对社区公布。一来可以让社区对神秘的蓝牙技术破冰；二来也是抛砖引玉，希望能看到更多有趣的案例；三来比起那些华丽丽的show，我更喜欢分享一些实际的内容。

_本次的研究目标是蓝牙4.0中的低功耗技术（**Bluetooth Low Energy**）简称**“BLE”**，需要注意一些技术规范容易与经典蓝牙搞混。_

正文开始前再看一段新闻报道吧，感受下蓝牙对当前以及未来在我们生活中的影响力：

> 2015年8月18~19日，蓝牙技术联盟(Bluetooth Special Interest Group，简称SIG)在上海举办2015蓝牙亚洲大会。蓝牙技术联盟执行总监Mark Powell在会上指出，目前蓝牙已经成为全球使用量最大的无线技术。目前，蓝设备的年出货量在过去15年内增加了1000倍，已经达到了30亿的水平，在未来的4~5年内还将增加到50亿。

0x02 BLE概述
==========

* * *

这里本应该先讲解蓝牙与低功耗蓝牙的基础知识，但网上资料充足，所以各位还是从文章最后的参考资料中学习吧。乌云上也有白帽做了部分科普[Bluetooth Low Energy 嗅探](http://drops.wooyun.org/tips/9651)感谢他的分享。所以我只讲基础知识中的关键内容，然后多放些大家喜闻乐见的实战案例。

BLE 协议栈总览
---------

![](http://drops.javaweb.org/uploads/images/5a8460515fd99fd348160f77593434366aefd0f8.jpg)

这个协议栈非常复杂，想基础化了解BLE协议基础的，就可以参考最新蓝牙4.2的官方文档[Bluetooth® Core Specification 4.2](https://www.bluetooth.org/en-us/specification/adopted-specifications)，我只简单的提取我理解的关键部分。

GAP－通用访问规范
----------

BLE设备的链接与加密、签名协议的协商在这一层，比如BLE的两种安全模式，首先是Security Mode 1，这个模式主要负责“加密”，它含有三个安全等级：

*   **Level 1 无认证无加密，链路默认模式。我手头有的设备默认都是这个等级，不靠谱…**
*   Level 2 带加密的未认证配对
*   Level 3 带加密的认证配对

其次是Security Mode 2，这个模式主要负责“签名”，它含有两个安全等级：

*   Level 1：带数据签名的未认证配对
*   Level 2：带数据签名的认证配对

_PS：以上都是书本知识，具体可以参照蓝牙4.2官方文档内对BLE安全的解说部分，注意不要跟蓝牙混淆。_

GATT－通用属性协议
-----------

GATT负责两个BLE设备间通信的数据交互，是对功能数据最为重要的部分，这篇文章的核心也在这里。

![](http://drops.javaweb.org/uploads/images/cb59ad30dffea0b02d7a1966daba8664a8b69939.jpg)

如图，GATT中的三个要素Profile、Service、Characteristic以及他们的层级关系，值得注意的是，Profile其实是SIG蓝牙技术联盟给一些同范畴内的Service打包后的集合，比如电池、心率、血压等，可以参照官方[Profiles Overview](https://developer.bluetooth.org/TechnologyOverview/Pages/Profiles.aspx#GATT)所以Profile对我们的分析并无大用，不用放在心上。

Service和Characteristic是比较重要的，Service可以理解为PHP中的“类”，功能对象的集合。Characteristic可以理解为PHP的“函数”，是GATT中具体的功能对象，每个Service都可以包含一个或多个Characteristic。

为什么说GATT很重要？因为理解了它，就已经能够分析或是“黑掉”一些BLE设备了。比如小米手环在国内某个硬件安全会议上被做过一个攻击演示，使用Lightblue连接到手环后，只要用给其中一个Characteristic写入1，就可以让手环震动起来，大家很惊讶但有不知所以然。我来用官方注册的Characteristic角度解释一下：

![](http://drops.javaweb.org/uploads/images/5e5805a8a3e0b0b2f315e857a384d89c3de26c63.jpg)

那个FEE7就是一个私有Service的UUID，里面的0xFE**就是私有Characteristic的UUID，在往下面这个Immediate Alert 显示出了名称，代表其不是小米私有的Service，而是官方公开定义的Service，我们点击进入这个 Characteristic

![](http://drops.javaweb.org/uploads/images/ec8e430e6137f366b9c5527258935722175cd4f1.jpg)

看到了这个 Characteristic 的UUID 2A06，然后我们去蓝牙官网定义的列表[Characteristics](https://developer.bluetooth.org/gatt/characteristics/Pages/CharacteristicsHome.aspx)搜索 2A06，进入Characteristic的详情页面。

![](http://drops.javaweb.org/uploads/images/4974d906c2d91885f5afc401a9baf9cef3f8fb08.jpg)

该 Characteristic 操作定义非常明确了：

| 值 | 含义 |
| --- | --- |
|  | 无警告 |
| 1 | 温和的警告 |
| 2 | 强烈的警告 |
| 3~255 | 预留 |

所以你向UUID为 0x2A06 的 Characteristic 写入1的时候，小米手环会变会震动。**其实你还能输入2，这个快感比1更酸爽～哦呦、别、别停……**这是一个简单的GATT例子，不知各位是否明白，现在你可以安装个LightBlue链接你身边的BLE设备，看看能否发现一些问题了呢？

_小知识：GATT中的UUID有16bit和128bit两种，官网看到那些都是16bit的（其实真正的通信都是128bit的，官方UUID在第一段数据中可以识别）。官方认证过的UUID是要花银子的，但你可以免费使用，保证软硬件的相互理解。相反，私有UUID只有你自己的软硬件才能够理解，要弄明白功能就得技术性分析，也就是我后面要做的事情。_

0x03 BLE嗅探
==========

* * *

在遇到私有Service或Characteristic的时候，就要通过app逆向或嗅探蓝牙通信来分析了。说到蓝牙嗅探，大家第一想到的肯定是神器 Ubertooth One，精致的硬件＋配套的软件变成了物联网黑客强大的帮手，缺点大家有所体会——昂贵。在自己做了一些简单的BLE设备研究后，了解到其实有更廉价的方案可供使用，这就是蓝牙芯片厂所提供的BLE USB Dongle。

> BLE USB Dongle，蓝牙芯片厂商为了方便开发者能够方便的调试蓝牙产品通信，就将这些蓝牙芯片集成为USB模块，可进行方便的蓝牙透传测试。而你可以烧入Sniffer固件，就可以利用这个设备分析附近的蓝牙通信，然后将数据通过USB串口输出到计算机上。

代表性的芯片有：

*   德州仪器（TI）的CC254x系列，配有官方的Sniffer程序，非常强大
    
    ![](http://drops.javaweb.org/uploads/images/e70339c3f043cdb7115ee725f713f5b52b0f4868.jpg)
    
*   北欧（Nordic）的NRF51822，串口输出到计算机后，通过pipe方式使用Wireshark分析
    
    ![](http://drops.javaweb.org/uploads/images/78057467dc83d57124131acbceb425d92f3888cd.jpg)
    

我个人喜欢后者，因为我觉得这个数字对于我来说很吉利…吉利？…好吧，我就索性放弃Ubertooth One这款神器，给大家看看USB Dongle的其他玩法：）另外注意，NRF51822是一块单模（Bluetooth Smart）芯片，只支持BLE。具体参考官方文档：[nRF Sniffer User Guide v1.1](http://www.nordicsemi.com/eng/nordic/download_resource/31919/6/98796976)

配置好环境之后就可以对附近的设备通信进行抓取了，我先来验证一下书本知识。

![](http://drops.javaweb.org/uploads/images/6bda82cea3b2d5df5d597e2def0ca4910ac1fb5f.jpg)

![](http://drops.javaweb.org/uploads/images/59f35b088d3f8a4504d519167f2bd217de64db76.jpg)

这是BLE设备建立链接前主设备发给从设备的 CHANNEL_MAP_REQ 信息，用来告知BLE这40个信道哪些已经被占用，哪些可以使用。从中我们可以看到BLE频率起始为2402MHz，结束为2480MHz，信道间距2MHz，有3个不可使用的广播信道37、38、39（频段的起始、结尾与中心各设置一个广播频道，合理），这些都与书本知识吻合。

然后我们选择一个BLE设备的MAC地址进行Sniffer，**注意一定要在设备连接前就指定mac监听**。监听后随便发起什么通过蓝牙信号的操作，我们就抓取到了第一个BLE数据包

![](http://drops.javaweb.org/uploads/images/f34c241c1ae5cac4ef5b0ae6d9a5d71851c6fbd8.jpg)

很激动有木有？现在抓取BLE通信就犹如抓取网络通信一样便捷了，连复杂的跳频都先不用去考虑了撒。接下来再看最下面 Bluetooth Attribute Protocol 就是关键的 BLE 操作通信内容，那个value是该产品的私有通信协议。虽然现在看不懂意思，但并非是加密所致，因为我前面有提到，我手里的设备安全链路全是Security Mode 1 默认的Level 1这个级别…那私有协议如何分析？别急，后面的实战部分我会介绍我的思路。

0x04 伪造BLE通信
============

* * *

现在可以分析BLE通信了，接下来还要知道如何发送BLE信号，让对方设备执行我们期望的操作。其实要达成这个目标BLE USB Dongle或蓝牙开发版就可以实现，但为了今后更多无线通信测试的便捷性，我还是准备打造一款软硬结合的平台。所以软件我使用Linux官方的蓝牙栈BlueZ（很多蓝牙攻击程序都是基于该蓝牙栈），硬件我则选择了CSR厂的CSR8510芯片蓝牙适配器。平台我用2代树莓派搭建，未来会支持蓝牙、RTL-SDR、ZigBee等常见无线通信协议，比那些装个kali2就叫“无线渗透”的设备可玩性多了些嘿嘿。

*   CSR8510 蓝牙适配器
*   BlueZ 官方蓝牙协议栈
*   Raspberry2 平台

目前蓝牙的设备塞在一起就是酱紫了。

![](http://drops.javaweb.org/uploads/images/460ea76c2302afdb6bbdea633d8fb441846272d8.jpg)

在这里，我们用Bluez自带的hcitool扫描下没开启广播的BLE设备，比如小米手环![](http://drops.javaweb.org/uploads/images/fa6784e6c019e6b2ce3885776e22244ba911c0e5.jpg)无处遁形。

在上一节BLE抓包后，我们得到的 Bluetooth Attribute Protocol 中的信息，就是发出BLE信号的关键部分：

*   **OPcode**

操作：Read、Write还是Notify（写操作也不一定都是 write request 还有 write command，区别自己搜）

*   **Handle**

操作句柄，可以简单理解为 Characteristic 的基址，真正的通信地址

*   **Value**

设备间传输的数据真身。有了这几个信息，我们就可以调用BlueZ给设备发送修改后的信号了。

0x05 分析BLE私有数据协议（灯泡、跳蛋、小米手环）
============================

* * *

有了上面的理论基础，要开始实战了。我手头上只有蓝牙灯泡和小米手环，后来一个猥琐的朋友借我个跳蛋希望帮忙分析…

1. YeeLight 2 代蓝牙灯泡
-------------------

首先这个灯泡我在分析前就敢肯定他是存在问题的，因为灯泡的操作逻辑不会过于复杂，无非是一开一关、变色等等，所以我就拿他来做“Hello world”

```
1. 抓包灯泡的开关灯动作的value

2c2c2c3130302c2c2c2c2c2c2c2c2c2c2c2c（开）
2c2c2c302c2c2c2c2c2c2c2c2c2c2c2c2c2c（关）

```

看到差异了么？

![](http://drops.javaweb.org/uploads/images/1503b0a89443b81d02f01f892f8d9f0837443b51.jpg)

0x313030 = 100 0x30 = 0 从 4bytes 开始，就是该灯泡的亮度部分，100最亮，0没有亮度，也就是关。

```
2. 抓包灯泡的换颜色动作

3235352c302c302c3130302c2c2c2c2c2c2c（红色）
302c302c3235352c3130302c2c2c2c2c2c2c（蓝色）

```

同上道理

![](http://drops.javaweb.org/uploads/images/ae1df27a5356e0df898f94d42462f60d9b6c2422.jpg)

```
0x3235352c302c30 = 255,0,0
0x302c302c323535 = 0,0,255
这就是RGB的颜色格式，很简单直接告破：）最后看下 Handle 0x0012，来源如图

```

![](http://drops.javaweb.org/uploads/images/17544f68baf8204df8199c6591a4edf04fedcbe4.jpg)

最后，简单的看下Bluez协议栈自带的gatttool工具的使用方法

![](http://drops.javaweb.org/uploads/images/7dfb392199e6e43ddf29254db7da0308016b5bdd.jpg)

通过抓包分析得知操控灯泡颜色的handle是0x0012，我读了下他的uuid为fff1，私有的。用char-write-cmd命令直接写入我们分析好的协议，灯泡变色，然后再读取之，数据确实成功写入。

Demo:

2. 小爱爱智能跳蛋（这个真不是我的，某个小伙伴借给我研究的）
-------------------------------

这个产品感觉逻辑也简单，就是网络远程发送震动指令到手机，手机在通过BLE链接设备进行你懂、我懂、他也懂的事情，羞～

![](http://drops.javaweb.org/uploads/images/2981f2b8e9019172c49d2b25c8cbc120fda80d83.jpg)

这个跳蛋有三种模式：**预定义节奏的震动、随着音乐翩翩起舞的震动还有一个体位交互震动**，因为前两个没啥难度，基本抓到操作重放出来就OK了，最后这个模式比较卡哇伊，玩玩它咯。

与灯泡不同的是，进入体位模式后，Master会给Slave发送一个状态开启这个模式。所以你盲目的发送抓到的震动操作这个蛋是不震的，因为你要先让她进入状态。

```
给 Handle 0x0013 发送 0x0811060f01010232 后，它就进入状态了。
然后 0x3e ＝ 震动，0x7f ＝ 生理暴击（你狂按手机的时候就疯狂的震动）

```

这个分析很简单，因为都是些开关类的操作没有太多实际的含义，所以无需解开数据，直接重放就可以，我做了个发送SOS急救信号的demo。

Demo:

3. 小米手环
-------

小米手环是明星产品，对他的分析也充满了趣味与困难，因为从一开始我就遇到了一个认证机制，如果蓝牙链接后不写入一段特殊格式的数据，那你只能读少量信息不能对手环进行操作。我通过抓包分析GATT中的write操作，**过程省略2万字**，最终定位了一个向 Handle 0x0019 进行的write操作，该Characteristic返回了个Notify，然后手环就可以随意写指令了（如私有协议中的震动、LED颜色变化、开启实时步数监控等）。

> **不过认证怎么能叫PWN？**
> 
> **不过认证怎么能叫PWN？**
> 
> **不过认证怎么能叫PWN？**

重要的事情说三遍。小米手环的认证数据分析好了，结构如下

| uid | 性别 | 身高&体重 | 昵称 | 类型 | 签名 |
| --- | --- | --- | --- | --- | --- |
| dcxxxx00 | 0100 | af3a00 | 66656e67676f7500 | 0000 | fe |

这个签名是最重要的部分，前面的数据都可以伪造，只要签名过了，手环就会允许你后续的写指令，才能做到真正的PWN。那这个签名是咋算出来的？请看番外篇。

* * *

### 番外篇：小米手环认证机制分析

剑走偏锋，通过BlueZ得到了小米手环一个完整的私有协议UUID，然后去Github搜索，希望找到官方的代码（其实这部分通过逆向Android app相信就能得到，不过说好的剑走偏锋么）

![](http://drops.javaweb.org/uploads/images/a560012f056ad714039666012d1cbab956f1adab.jpg)

然后呢？duang～

![](http://drops.javaweb.org/uploads/images/c56d8942a99cc907040800df7840db8593f34731.jpg)

![](http://drops.javaweb.org/uploads/images/a268fe7aea004f8510bf13ff04f3b6f53d4facfa.jpg)

似乎是个第三方SDK，目前至少不用去逆向Android APP了开心，说实话这个我还真不擅长。通过这个SDK我找到了具体认证流程的代码：

[GitHub - miband-sdk-android](https://github.com/pangliang/miband-sdk-android/blob/cdb9bd038644ae3fb218a309bd20bf6520a8d035/miband-sdk/src/main/java/com/zhaoxiaodan/miband/model/UserInfo.java)

从这段代码中分析，最终写入Characteristic的内容，来自 userInfo.getBytes(device.getAddress()

```
public void setUserInfo(UserInfo userInfo)
{
    BluetoothDevice device = this.io.getDevice();
    this.io.writeCharacteristic(Profile.UUID_CHAR_USER_INFO, userInfo.getBytes(device.getAddress()), null);
}

```

userInfo.getBytes 的设计在这里，做了简单注释

```
public byte[] getBytes(String mBTAddress)
{
    ...
    ByteBuffer bf = ByteBuffer.allocate(20);
    bf.put((byte) (uid & 0xff));    //uid
    bf.put((byte) (uid >> 8 & 0xff));
    bf.put((byte) (uid >> 16 & 0xff));
    bf.put((byte) (uid >> 24 & 0xff));
    bf.put(this.gender);    //性别
    bf.put(this.age);   //年龄
    bf.put(this.height);    //身高
    bf.put(this.weight);    //体重
    bf.put(this.type);  //类型
    if(aliasBytes.length<=10)
    {
        bf.put(aliasBytes);
        bf.put(new byte[10-aliasBytes.length]);
    }else{
        bf.put(aliasBytes,0,10);
    }

    byte[] crcSequence = new byte[19];  //取出用户信息的前19个字节
    for (int u = 0; u < crcSequence.length; u++)
        crcSequence[u] = bf.array()[u];

    byte crcb = (byte) ((getCRC8(crcSequence) ^ Integer.parseInt(mBTAddress.substring(mBTAddress.length()-2), 16)) & 0xff);
    bf.put(crcb);   //将签名跟前面的用户信息拼接
    return bf.array();  //最终写入Characteristic的内容
}

```

| uid | 性别 | 身高&体重 | 昵称第1byte凑齐19byte | MAC最后2byte |
| --- | --- | --- | --- | --- |
| dcxxxx00 | 0100 | af3a00 | 6 | FC |

这个数据与MAC地址最后两位FC进行异或为16byte数据，在转为2byte的hex签名结果。用户信息与手机端无需一致，只要签名正确即可。这里感谢 @瘦蛟舞 的帮忙，用java程序帮我做了个接口，这样我就能根据MAC地址任意生成有效的认证数据了。

![](http://drops.javaweb.org/uploads/images/552e4be51d64189f626d897ea7c0fac2c5ccd272.jpg)

完整代码也不放出了，毕竟可以秒杀手环认证：）

* * *

解决了认证的难题，接下来就是压轴大戏，如何对用户以及产品口碑造成真正的影响。震动？改步数？LED跑马灯？都不是，**我选择在茫茫人群中，给你写入恶意的闹铃，名曰 午夜凶“铃”**。试想下，背着我那台无线Hack设备，天天在早高峰蹭北京城铁13号线，自动搜索身边小米手环，然后链接过认证写入闹铃，你们猜一个月后我能“感染”多少手环？我相信不用多久，小米手环论坛就会有用户闹翻天了…光说不练耍流氓，实现它。选择设备后抓包，客户端设置几次闹铃，只要一次我就解开私有协议格式了：

![](http://drops.javaweb.org/uploads/images/2cbd5c97dad1d17be786189fd5b13518eb11cfeb.jpg)

一样简单，数据格式我画出来。第一位说明当前的操作是闹铃，第二位是闹铃的序号，第三位闹铃的开关，第四位开始就是闹铃时间，倒数第二位是智能唤醒（就是在你浅睡眠的时候把你叫起，但是我偏不，就是要在你深度睡眠时唤醒你，木哈哈），最后一位就是闹铃的循环日期，0x7F就是每天。

写好测试程序，搜索并链接手环通过那个“认证”获取操作权限，再用手环LED玩个跑马灯，最后华丽丽的写入闹铃释放链接。**结果手机客户端连上去发现闹！铃！没！开！启！还是默认的关闭状态**，不放弃继续分析，我是越挫越勇的……

通过后面的分析发现，这个地方是小米手环客户端（至少iOS客户端）的BUG，手环开发组GG认为手环的数据只有通过客户端进行开启修改，所以非客户端写入的数据不会自动同步！也就造成了恶意闹铃虽然写入成功，但客户端看不到，认为闹铃没有变化不去同步最新的状态，但这反让攻击变的更加隐蔽了，啧啧。

看演示吧，POC代码不放，因为细心动手的人可以通过我的分析解决一切问题，也避免真的有人直接利用代码对小米用户进行攻击（因测试成功后忘记取消之前设置的午夜凶“铃”，所以我成了第一个受害者，大半夜太酸爽了）。

Demo:

0x06 结语
=======

* * *

内容没有涉及任何经典/低功耗蓝牙的协议加解密、签名、配对儿认证等安全机制，毕竟是初探，不搞那么复杂高大上变成学术文章。所以我先分享一些接地气儿的产品和攻击场景，希望能够建立伙伴们对物联网安全的兴趣。

BLE在蓝牙中都是很小的一部分，在物联网汪洋大海中更是一叶扁舟，学海无涯希望路上有你。

**PS：以上的内容我个人认为并不是漏洞，毕竟还得10米的攻击范围内，所以直接当做技术分享吧。**

0x07 参考资料
=========

* * *

1.  [Bluetooth® Core Specification 4.2](https://www.bluetooth.org/en-us/specification/adopted-specifications)
2.  [nRF Sniffer User Guide](http://www.nordicsemi.com/eng/nordic/download_resource/31919/6/98796976)
3.  [nRF-Sniffer-Code](http://www.nordicsemi.com/eng/nordic/download_resource/31920/14/93837379)
4.  [低功耗蓝牙开发指南 作者:（英）海登 著，陈灿峰　刘嘉　译](http://product.dangdang.com/23502175.html)
5.  [CC2540 Bluetooth Low Energy Software Developer’s Guide (部分翻译修改版)](http://blog.csdn.net/ooakk/article/details/7302425)