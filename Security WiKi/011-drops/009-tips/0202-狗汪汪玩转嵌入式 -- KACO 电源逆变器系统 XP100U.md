# 狗汪汪玩转嵌入式 -- KACO 电源逆变器系统 XP100U

0x00 前言
=======

* * *

首先要感谢冰哥的指导和鼓励才有了以下这篇小文. 当下智能物联网设备火热, 许多商家和开发人员只图功能上的快捷, 而忽略提供相应的安全方案. 同时许多传统的工控设备, 因添加了网络模块却又缺少相应的安全意识, 导致这些设备都稀里糊涂地暴露在了公网上. 这为攻击者打开了一道方便之门. 本文将于这款 KACO 新能源公司生产的电源逆变器系统为例, 跟大家分享下不安全的设计会给工控系统带来怎样的影响.

![p1](http://drops.javaweb.org/uploads/images/8a15e1f94535b34aee4bcbc3197bb8e0e8f98bdd.jpg)

KACO 新能源公司是一家位于德国, 专注生产和设计电力相关的工控系统. 据称其客户遍布全球. 但在 2015 年的 DEFCON 23 上被爆出其在电源逆变器系统 XP100U 产品中存在后门.

而在重现的研究过程中, 我们可以发现此款产品的问题还不仅仅如此. 接下来大家就一起来场工控设备的探索之旅吧.

![p2](http://drops.javaweb.org/uploads/images/c11961d0576d0624715e72a880586547750953f9.jpg)

0x01 经典系统后门
===========

* * *

KACO 的这款电源逆变器系统自带了一个Java 编写的小型 WEB 服务, 用于远程登陆系统监控各项数据指标.

![p3](http://drops.javaweb.org/uploads/images/708b9adcaa7ee50b49ac9f7657b0973e40300d25.jpg)

通过阅读操作手册我们可以得知, 系统有个默认的密码 ksk12. 成功登陆后便可进行一系列的数据采集等操作.

![p4](http://drops.javaweb.org/uploads/images/e2bf537fe76f820f59cbc929838758c83cc93ef2.jpg)

在通过查看页面代码后, 我们可以找到一个名为wms.jar 的文件. 这里我们可以使用JAVA decompile 软件来查看其源代码.

![p5](http://drops.javaweb.org/uploads/images/69273be9af01fb9d44d9bc4c448e6bbaf4e07b8c.jpg)

只需简单的查找password关键字, 我们便可以轻松找到位于WMSSettings下的后门密码 “kacosolar2008” .

![p6](http://drops.javaweb.org/uploads/images/40537a7a5e31404b832944ef1fb5c222951b2b19.jpg)

有趣的是此后门密码是无法修改的. 如以下代码所示, 整个后门的认证过程只是简单跟WMSSettings 里设置好的AdminPassword 在本地进行比对.

![p7](http://drops.javaweb.org/uploads/images/d83c0c9cc02cddbe5d24483e53dfadccfeef7c6d.jpg)

瞧整个后门还原过程是那么的轻松愉快, 不过更为有趣的地方还在后头…

0x02 掩耳盗铃认证设计
=============

* * *

再了解过上面这个经典的后门系统后门账号后. 通过 Wireshark 抓包分析, 还可以发现了一个此系统 ”有意思” 的认证设计. 之前我们说过系统默认密码为 ksk12. 正常情况下用户可以将其修改为自定的密码, 而整个过程都以明文的方式传送. 是的, 我们可以通过简单的sniffing 就得到密码. 但这又有啥特别呢? 别急好戏还在后头.....

![p8](http://drops.javaweb.org/uploads/images/f3a6728d319106def4246a812e063cba402b96ec.jpg)

这里我们还是先来看下整个登陆的过程. 当我们按下Login键之后, 客户端发的第一个包中含有 “`aci_request_code type=‘int’> 31<`”的字样. 那么 31 是代表什么意思呢？

![p9](http://drops.javaweb.org/uploads/images/b90ab3d0cba1d5f4e174547e0076a173ecbd7b98.jpg)

通过查找 Java 源代码得知, 类型 31 是用来从服务器 get 当前密码的. 也就是说每次认证时, 系统都会将当前密码以明文的方式发回...

![p10](http://drops.javaweb.org/uploads/images/a3450b23b79b6ac6ad106b10331209527436cfc4.jpg)

最不可思议的地方是即使用户输入了错误密码, 表面上会弹出个报错框. 但实际上系统依旧将正确的密码明文返回. 哈哈! 换句话说我们更本就不需要通过逆向源代码这么麻烦, 系统本身就已经把密码告知天下了.

![p11](http://drops.javaweb.org/uploads/images/9e2c6761982bef33a76b8ea007780f1778c4a677.jpg)

0x03 猎杀 XP100U
==============

* * *

讲了这么多大家一定迫不及待的想找台KACO 来体验下了吧. 这里我们可以使用搜索引擎来帮助完成这个任务. 如下图所示 SHODAN 轻松帮我们找到了几台暴露在公网的KACO 逆变器.

![p12](http://drops.javaweb.org/uploads/images/c2abebf8659be20a11406915f583d7856622f738.jpg)

需要注意的是系统默认的端口号是 80 . 大家在测试过程中可以多试试几个常用端口.

![p13](http://drops.javaweb.org/uploads/images/52a19eaca839c067a01520e5821ab4a710796523.jpg)

![p14](http://drops.javaweb.org/uploads/images/cc53d524b1ac18b755864e2ac792ad8239a5b7f8.jpg)

有意思的是在某个KACO 电源逆变器的网址, 还存在网络监视器系统 (感谢 Z-One 友情提供线索). 感兴趣的朋友可以继续深度挖掘一下. 不过不要搞破坏哦. :D

0x04 总结
=======

* * *

通过这个案例, 可以发现在传统系统安全中已经很少出现的漏洞. 如 HTTP 明文传输; 默认密码; 系统后门等等在工控嵌入式系统中仍旧非常普遍. 可是由此所带来的隐患却是巨大的. 嵌入式系统往往还面临一旦投入产品线, 便难以升级的困难. 也许产品设计者在初始阶段就应该在易用 vs 安全中找到平衡点. 不过就安全爱好者本身而言, 工控嵌入式是一个非常好玩又很深的领域. 期待大家玩出更多的花样.

![p15](http://drops.javaweb.org/uploads/images/03c3047f807e3283d68175ec8802697fa9649a89.jpg)

0x05 参考文献
=========

* * *

*   [http://kaco-newenergy.com/us/](http://kaco-newenergy.com/us/)
*   [https://ics-cert.us-cert.gov/alerts/ICS-ALERT-15-224-01](https://ics-cert.us-cert.gov/alerts/ICS-ALERT-15-224-01)
*   [https://www.defcon.org/html/defcon-23/dc-23-speakers.html#Sood](https://www.defcon.org/html/defcon-23/dc-23-speakers.html#Sood)