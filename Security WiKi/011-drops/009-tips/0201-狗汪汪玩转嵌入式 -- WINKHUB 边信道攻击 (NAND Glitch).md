# 狗汪汪玩转嵌入式 -- WINKHUB 边信道攻击 (NAND Glitch)

0x00 前言
=======

* * *

随着物联网IOT的飞速发展,各类嵌入式设备, 路由器安全研究也越来越火. 但因为跟以往纯软件安全研究的要求不同, 这类研究往往需要结合相应的硬件知识. 很多朋友困惑如何开始, 甚至卡在了该选何种工具上. 因此汪汪将会在系列文章中分享一些实战案例和相应的工具使用. 希望能对嵌入式安全研究起到抛砖引玉作用.

在WINKHUB这个案例中我们将使用几款简单的入门工具如万用表; UART 转接头和导线等. 同时将介绍一种通过芯片阻断的方式, 获取系统ROOT权限的攻击方法. 这种方法是俗称边信道攻击中最容易上手的一种. 汪汪希望可以借此小文让大家体验下, 并不是所有的边信道攻击都那么的高不可攀.

![](http://drops.javaweb.org/uploads/images/575670f5871f9043c1d71016bacfe39e424a0fd1.jpg)

0x01 必备神器UART转接头
================

* * *

正所谓工欲善其事必先利其器, 拥有得心应手的辅助工具, 对我们研究嵌入式设备安全将起到事半功倍的作用. 而说起嵌入式设备不管是开发调试还是安全研究, 都会用到UART转接头 这个神器.

UART接口简称通用异步收发传输器, 是一种通用串行数据总线.我们可以通过它来调试目标设备. UART 口在PCB上通常分为: Vcc; GND; TX; RX 这4口. 而UART转接头则在电脑USB 口之间取到转接的作用.

![](http://drops.javaweb.org/uploads/images/a2838469af877381b6e1194c02d7e70546cf2263.jpg)

UART转接头在配置上非常简单. 只需在目标PCB板上找到正确的UART 端口, 并设置好如baud rate 这类参数便可以使用诸如Minicom这类程序跟目标进行通讯了. 凡是有配置过CISCO 路由器的朋友对此操作界面一定不会陌生.

![](http://drops.javaweb.org/uploads/images/e5d129c8583616a2ae28f9105740196814dc4ba2.jpg)

但是通常PCB板上会将用于调试的UART 端口隐藏 or 存在多个UART端口. 如何在目标PCB板上找到正确的UART 端口, 也是个可以探讨的话题. 不过因为我们今天的目标WINKHUB已经明确的标识出UART端口位置, 所以暂且不表.

![](http://drops.javaweb.org/uploads/images/c5345ccc4e0f31c3dda5d48d3fb9c483b4caa439.jpg)

还有个值得注意的地方便是正确的baud rate 参数. 比如常见的9600 or 115200. 如果此参数设置不对, 我们便无法看到正确的调试信息. 这时我们可以使用专门用来确定未知串行行设备波特率程序baudrate来发现正确的参数.而其工作原理是试图把所有的baudrate都过一遍,直到屏幕上显示清晰的调试信息.

![](http://drops.javaweb.org/uploads/images/c82f592bc1995156c05901a7c6a8055200b5882b.jpg)

0x02 WINKHUB 物联网关
=================

* * *

终于到今天的主角上场了, 本次的攻击目标是这款名为WINKHUB 的物联网关. 你是否好奇为何需要此类网关设备呢? 玩过IOT设备的朋友就会发现, 现有的IOT产品仅同时支持1到2种互联方式. 比如Philips的HUE智能灯系列采用Zigbee作为联接技术. 而用户若是想把HUE跟使用Bluetooth的智能门锁互联,还需要在添加额外设备. 这从用户体验的角度上来说是非常不方便的. 而WINKHUB网关的优势就在于其同时支持WIFI; Bluetooth4.0; Zigbee; Z-Wave 和 RF 等主流的IOT 联接方式. 换句话说用户只需要买一个这样的网关, 就不用担心不同IOT产品间的兼容问题.

![](http://drops.javaweb.org/uploads/images/b110f58c873c17bacff42dbf0d60f37bb33d76c6.jpg)

![](http://drops.javaweb.org/uploads/images/6f8af5f85f30318007ed69f12d6417be3342417c.jpg)

然而成也萧何，败也萧何. WINKHUB 在功能上的优势, 也给攻击者提供了更多的攻击向量. 作为一款智能网关以往家用路由器上常出现的安全隐患也依然存在. 譬如在早期的固件版本中就存在Command execution 漏洞 (set_dev_value.php). 而在官方修复的新版本中又被发现了SQL Injection漏洞.

![](http://drops.javaweb.org/uploads/images/9526a74e7dc2ab8cf6440039e7ada901c798cc76.jpg)

图上为包含Command execution 漏洞的PHP 代码段. 通过此漏洞我们可以root 权限执行任何系统命令. 比如读取shadow 文件.

0x03 边信道 (NAND Glitch)
======================

* * *

NAND Flash 在嵌入式系统中通常用来存储固件, Bootloader, 内核以及root files. 是整个系统中最重要的. 同时也是攻击者最想搞定的目标之一. NAND Flash 的容量大小, 接口数也跟芯片的不同而不同. 大家可以通过查datasheet 的方式来确认. 在前面提到代码漏洞爆出后. WINKHUB的厂商通过软件升级的方式迅速将其修复. 但对厂商来说, 还有一种攻击方式却没那么容易修复. 这便是用NAND 芯片作为切入点, 通过边信道攻击来得到ROOT权限. 而这也是当年成功拿下XBOX 游戏机的方法之一.

![](http://drops.javaweb.org/uploads/images/9b4c0ddc735285ca59dfadf24cc82101985eccab.jpg)

(图为XBOX 游戏机NAND Flash)

有很多朋友一提到边信道攻击，就觉得是个特别高大上. 其实边信道攻击也分好几种方式. 除了大家普遍了解的信息泄露之外, 错误注入攻击(Fault Glitch) 也是很常见的一种攻击方式. 跟信息泄露测量不同的是, 错误注入攻击的目的往往在于改变程序的运行流程, 尤其是在安全认证机制上. 或者通过阻断内核被正常读取的方式, 强制系统进入U-boot shell模式.

![](http://drops.javaweb.org/uploads/images/6504ea4e9cf45fc8aad0b85209e30a8fddc41d48.jpg)

错误注入攻击通常使用激光; 热能; 噪音等作为而错误注入的传输源. 不过也可简单到通过一条数据线接GND的方式来完成攻击. 但是必须注意的是错误注入(Fault Glitch) 具有结果难于预测特性. 尤其是在 timing 的掌控上. 汪汪在实际测试过程中因操作不当, 曾毁坏过2台 WINKHUB.

0x04 NAND Glitch 实战
===================

* * *

本文中的错误注入攻击便是通过阻断内核被正常读取的方式, 强制WINKHUB系统进入U-boot shell模式来得到root 权限. 通过读datasheet 我们可以发现 WINKHUB 的NAND Flash 的第29号PIN 为数据输入输出口.

![](http://drops.javaweb.org/uploads/images/6c042cd37999b78f60f975572e837c83781df5a0.jpg)

我们首先通过万用表查找GND 口. 随后使用普通的数据线在系统启动, 并尝试读取NAND芯片中的内核等信息的瞬间短接以达到数据阻断(NAND Glitch) 的目的.

![](http://drops.javaweb.org/uploads/images/d46ac131be0a1338c016c9f9d61ad6843931cfc8.jpg)

但大家在完成这看是简单的过程中一定要小心仔细. 原因可以看图中29号PIN的实际大小来感受下.

![](http://drops.javaweb.org/uploads/images/ac7618aada4521ac1ee88b8794a727c26a962edb.jpg)

不过多加练习几次后, 也就运用自如啦. 再系统进入U-boot Shell 后, 我们便可以通过修改内核参数得到ROOT Shell. 整个过程大家可以观看以下视频.

0X05 总结
=======

* * *

通过这个案例, 相信大家在嵌入式攻击方式上有了更多的了解. 有时候纯软件的步骤无法达到目的时, 可以考虑下硬件比如边信道的方式. 同时汪汪觉的开发者们在设计一款嵌入式设备的时候, 也可以多从攻击者的角度考虑. “**Think like an attacker**” 绝不仅仅是说说而已. 剑走偏锋, 逆其道行之. 攻击者往往会从你想不到的地方作为攻击点.

![](http://drops.javaweb.org/uploads/images/7ab5658a64206ae500ecabb285bca9ccb6dc66b8.jpg)

0x06 参考文献
=========

* * *

*   [http://baike.baidu.com/item/UART](http://baike.baidu.com/item/UART)
*   [https://code.google.com/p/baudrate](https://code.google.com/p/baudrate)
*   [http://www.wink.com/products/wink-hub](http://www.wink.com/products/wink-hub)
*   [https://www.exploitee.rs/index.php/Wink_Hub](https://www.exploitee.rs/index.php/Wink_Hub)
*   [http://www.devttys0.com/2012/11/reverse-engineering-serial-ports](http://www.devttys0.com/2012/11/reverse-engineering-serial-ports)
*   [http://www.eurasia.nu/wiki/index.php/Xbox_360_Reset_Glitch_Hack](http://www.eurasia.nu/wiki/index.php/Xbox_360_Reset_Glitch_Hack)