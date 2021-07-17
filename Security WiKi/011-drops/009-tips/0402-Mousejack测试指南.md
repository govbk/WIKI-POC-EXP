# Mousejack测试指南

0x00 前言
=======

* * *

近日，Bastille的研究团队发现了一种针对蓝牙键盘鼠标的攻击，攻击者可以利用漏洞控制电脑操作，他们将此攻击命名为MouseJack。 攻击者仅需要在亚马逊上以60美元购买设备，改造之后即可对百米范围内存在漏洞的蓝牙无线键鼠进行劫持，向受害计算机输入任意指令。相信对此感兴趣的人有很多，所以我根据其公布的信息购买了相应设备来进行测试，现将测试经验分享给大家。

![Alt text](http://drops.javaweb.org/uploads/images/1a41c4975cbf5a7bf740281d8b9a0f7a277a025e.jpg)

0x01 简介
=======

* * *

软件工程师马克纽林说：“利用假冒的无线电脑鼠标和键盘可以从100米的距离利用便携式外围设备入侵笔记本电脑，这些设备来自至少七家大厂商，包括罗技、微软、亚马逊”。 Bastille研究团队发现了针对13种鼠标和键盘的攻击并向各厂商报告了漏洞，其中有些厂商已经发布了补丁。

### 攻击原理：

由于没有身份验证机制，所以适配器无法识别出数据包是由鼠标发送的还是由攻击者发送的。

因此，攻击者可以伪装成一个鼠标发送自己的数据或者点击数据包以欺骗适配器

0x02 测试设备
=========

* * *

相信好多小伙伴已经在着手购买设备了，但是去国外的亚马逊以60美元购买设备有点不现实，所以我提前给大家探了路，在国内就可以用不到200元的价格购入设备，避免多花冤枉钱

**测试设备：**

**1、**Crazyradio 2.4Ghz nRF24LU1+ USB radio dongle(<￥200)

![Alt text](http://drops.javaweb.org/uploads/images/da61ec09add36f1b62f5a6be0940e408792708d8.jpg)

**2、**DELL KM714 无线键盘鼠标套装（<￥400）

![Alt text](http://drops.javaweb.org/uploads/images/f7de0f6ce3aa5840f698b710fb1e11e9497e6d77.jpg)

**注：**

以下链接展示了存在漏洞的设备：  
https://www.bastille.net/affected-devices

**3、**我的测试设备

![Alt text](http://drops.javaweb.org/uploads/images/754de6f82117839283031303261c855c7408477c.jpg)

0x03 实际测试
=========

* * *

**测试环境：**

```
本机系统：   Win7
虚拟机系统： Kali 1.0

```

**测试流程：**

### 1、Kali下搭建软件环境

```
sudo apt-get install sdcc binutils python python-pip
sudo pip install -U pip
sudo pip install -U -I pyusb
sudo pip install -U platformio

```

![Alt text](http://drops.javaweb.org/uploads/images/f1bc17399a193f840ce6206745c62194d7837324.jpg)

### 2、插上U盘

下载代码[https://github.com/RFStorm/mousejack](https://github.com/RFStorm/mousejack)，执行：

```
cd mousejack-master/
make

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/6e4f344f54a40ec1c73655d8a86e83d1a92d69dd.jpg)

执行：

```
make install

```

如图，操作失败

![Alt text](http://drops.javaweb.org/uploads/images/ef0761d11268a0202999619d20ec8d98b6a73757.jpg)

### 3、查找解决方法

在此处获得提示，需要更新Crazyradio 固件：  
[https://github.com/RFStorm/mousejack/issues/2](https://github.com/RFStorm/mousejack/issues/2)

更新方法可参照：  
[https://wiki.bitcraze.io/projects:crazyradio:programming](https://wiki.bitcraze.io/projects:crazyradio:programming)

### 4、更新Crazyradio 固件

下载代码https://github.com/bitcraze/crazyradio-firmware，执行：

```
cd crazyradio-firmware
python usbtools/launchBootloader.py

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/fb9bcb9841aaf9ca359b2da2a65e84e038e79ecd.jpg)

到[https://github.com/bitcraze/crazyradio-firmware/releases](https://github.com/bitcraze/crazyradio-firmware/releases)  
下载cradio-pa-0.53.bin，放在crazyradio-firmware文件下，执行：

```
python usbtools/nrfbootload.py flash cradio-pa-0.53.bin

```

如图，成功更新Crazyradio 固件

![Alt text](http://drops.javaweb.org/uploads/images/50a4510110b946725403106ebd72c2369a2799f7.jpg)

### 5、再次make install

执行

```
cd mousejack-master/
make install

```

如图，发现依然失败

![Alt text](http://drops.javaweb.org/uploads/images/35d312bd70f8f3b8e1e024632cbc695b1ca09cea.jpg)

接着执行：

```
lsusb -d 1915:7777 -v | grep bcdDevice

```

此时也无法查看固件版本

![Alt text](http://drops.javaweb.org/uploads/images/f90e403661440cf67e74d4aa38428ae139e10bb0.jpg)

### 6、再次查找原因

原来需要把U盘拔下来重新插进去

再次执行代码查看固件版本

```
lsusb -d 1915:7777 -v | grep bcdDevice

```

如图成功

![Alt text](http://drops.javaweb.org/uploads/images/53784faaa266706c4571cc551d9f9404c01c3596.jpg)

再次执行

```
make install

```

成功，如图

![Alt text](http://drops.javaweb.org/uploads/images/8bfc9b63a66ba257d035489e6157fece75e0990f.jpg)

### 7、再次拔掉重新插

根据上面更新固件成功的代码提示"Please unplug your dongle or breakout board and plug it back in",再次拔掉重新插入U盘

![Alt text](http://drops.javaweb.org/uploads/images/12258e52646b45ce7f747845450a5bba48931b76.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/dae5d1de64fb3fc0a4162a7a7b892bdbddd6b06d.jpg)

如图，此时本机的Windows系统无法识别U盘，这就导致虚拟机系统也无法加载U盘，无法进行后续的测试

### 8、查找解决方法

原来需要在Windows上安装Crazyradio固件的驱动

**（1）**参考[https://wiki.bitcraze.io/doc:crazyradio:install_win7](https://wiki.bitcraze.io/doc:crazyradio:install_win7)

手动下载驱动包，在设备管理器中找到未识别的设备，手动更新驱动，但是依然无法识别

**（2）**参考[https://wiki.bitcraze.io/doc:crazyradio:install_windows_zadig](https://wiki.bitcraze.io/doc:crazyradio:install_windows_zadig)

下载zadig来识别U盘进行更新驱动

但发现zadig也无法识别U盘，因此这种方法也失效

![Alt text](http://drops.javaweb.org/uploads/images/3f5c4dbcee0e374334691baf093b0b4d93378b72.jpg)

### 9、分析问题

此时Windows无法识别U盘，有如下两种假设：

**（1）**Windows系统下的Crazyradio固件驱动存在问题，所以无法识别，因此导致虚拟机系统无法加载U盘（但是已经用了2种更新驱动的方法还是无法识别，会不会是刷坏了呢）  
**（2）**U盘被刷坏（存在这种可能，固件更新的说明里有提到，不是100%安全），有询问研究过crazyradio file的小伙伴，也倾向于U盘被刷坏

![Alt text](http://drops.javaweb.org/uploads/images/384a288fdca0c7532c4179409f11c7b9b1a44800.jpg)

### 10、解决问题

为了测试能够继续进行，改变了思路决定更换测试环境，在其他系统上也许能够绕过这个难题。

**（1）**ubuntu

感兴趣的小伙伴可以深入测试

**（2）**osx

使用osx系统测试，也许能够成功识别U盘，这也就是为什么最终采用了osx系统测试

测试发现osx系统能够成功识别，如图

![Alt text](http://drops.javaweb.org/uploads/images/354bafd79c040464241d6e9d980983dbebcb5c47.jpg)

依然是在虚拟机里面接着测试，这次虚拟机中的系统使用的是kali2.0，顺便也就研究了如果成功刷好U盘，在其他系统上使用需要哪些环境.

**经测试得出初步结论：**

**如果刷好U盘，只需要在新系统上下载Github代码，即可进行接下来的测试**

简单的测试图如下

![Alt text](http://drops.javaweb.org/uploads/images/068526a78a6be948b9bb5b3e29d3b36ef00c4ac5.jpg)

### 11、更多测试

连接上设备Dell KM714，对比给出的硬件id

![Alt text](http://drops.javaweb.org/uploads/images/22a96d462d3a52b0ad7036923cfcf0ebded6febf.jpg)

右图为购买的Dell KM714显示的硬件id

**（1）scanner**

执行

```
cd mousejack-master/
./nrf24-scanner.py -c {1..5}

```

运行后，会捕获附近所有设备的数据包

这时我们对KM714鼠标和键盘操作，命令行会立即回显捕获到的数据包

![Alt text](http://drops.javaweb.org/uploads/images/29a844695310831270ad4450f3e4d64e37dff9fb.jpg)

可找到Dell KM714的地址为 08:D0:4F:28:02

**（2）sniffer**

确定了Dell KM714的地址，就可以对其进行定向捕获 执行

```
./nrf24-sniffer.py -a 08:D0:4F:28:02

```

![Alt text](http://drops.javaweb.org/uploads/images/6b6372881866bd43f63393db6c8861481f298d1f.jpg)

**（3）network mapper（Denial of Service）**

执行

```
./nrf24-network-mapper.py -a 08:D0:4F:28:02

```

可拦截地址为08:D0:4F:28:02的设备发出的数据包，并对最后一位做修改，此操作可使设备失效，无法对电脑发送控制指令

![Alt text](http://drops.javaweb.org/uploads/images/b0ea00a0ed193bcab430a13322707b2dc5d5e6b3.jpg)

如图，执行完脚本后，此时Dell KM714的鼠标键盘失去响应，无法对电脑进行控制，只有重新插拔接收器才能恢复正常。

**注：**

1.  每次Ctrl+c结束脚本后需要重新插拔Usb才能继续测试，否则会提示超时，脚本执行失败
2.  购买的Crazyradio 2.4Ghz nRF24LU1+ USB radio dongle开发板 原厂会刷入Crazyradio固件（如果没有店家一般也会帮忙刷入），发光管显示绿光代表功能正常，但对其固件进行升级后，发光管会显示红灯，看似功能故障，但其实只要命令行输出为`Verification succeded!`即代表升级成功，发光管会显示红灯的原因在于对固件进行升级操作后，并未对发光管进行设置，因此显示红色。 板子上的灯虽然是红色，但不影响功能。

0x04 小结
=======

* * *

以上分享了我对mousejack的测试心得，记录的比较完整，希望对你的测试研究有所帮助。

当然，本文仅仅是对其公布的github代码进行初步测试，更多深入测试也在进行当中。如果需要实现劫持鼠标键盘，发送键盘消息，可以尝试修改github中的python代码。

如果你有更好的想法或是遇到了新的问题，欢迎和我交流：）

**本文由三好学生原创并首发于乌云drops，转载请注明**