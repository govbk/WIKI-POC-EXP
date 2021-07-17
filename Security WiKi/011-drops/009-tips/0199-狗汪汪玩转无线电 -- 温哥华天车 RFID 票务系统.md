# 狗汪汪玩转无线电 -- 温哥华天车 RFID 票务系统

0x00 前言
=======

* * *

如今物联网 RFID系统已经完全融入了我们的生活当中. 从楼宇门禁到 Apple Pay. 可以说其身影是无处不在.很多网友也分享了自己对RFID系统的安全测试心得.不过大多还是基于门禁卡和 Mifare-Classic 而言. 实际上在 Mifare 系列的大家族中还有着许多其他类别. 比如 Mifare-DESFire 和本文的主角 Mifare-Ultralight.

![](http://drops.javaweb.org/uploads/images/0de0d73707514e0daf4a1ce4354ea08000ca5788.jpg)

温哥华交通公司Translink 在 2015年开始逐渐淘汰老旧的打印票务系统. 并全面推广RFID为基础的票务系统, 并为其取名为 Compass. 此系统为了方便不同乘客的需要, 使用了Mifare-DESFire 作为月票卡. 同时还以Mifare-Ultralight 作为一次性车票.因 Mifare-Ultralight 成本低廉, 使其成为车票的不二之选. 但也正是为了节省成本, 其安全性近乎于零. 它的天生残疾为攻击者打开了一道方便之门.本文将以此轻轨RFID 票务系统为例, 跟大家一起来场RFID 系统的探索之旅.

![](http://drops.javaweb.org/uploads/images/405652cd5a564e090677b17f6e87192a0b0efb54.jpg)

0x01 Mifare-Ultralight 简介
=========================

* * *

Mifare-Ultralight 是 NXP 公司出品的众多Mifare系列中的一款. 其同样工作在 13.56 Mhz. 但跟它的老大哥 Mifare-Classic 不同的是, 它并无使用任何加密, 其数据内容是可以任意访问的. 因为造价低廉很多需要一次性门票的场合都将其作为首选.比如 2006 的世界杯比赛.其数据结构非常简单明了. 总共 64 bytes. 分为16 个区, 每个区为4 bytes. 而 4 - 15 区通常会用于数据存储, 存有时间; 入口和站台名等. 值得一提的是此区可任意读写无需认证哦. ;)

![](http://drops.javaweb.org/uploads/images/bfa67f5bc1ba2c9f2c83c1e916cb007827daf8bf.jpg)

UID区
----

其 UID 区在默认情况下是不可写的. 占有 9 个 bytes, 但只有 7 个bytes 作为 UID 使用. 比如 “ 04 e2 a8 c6 ba e2 43 80 9b ” 其中只有 04 e2 a8 ba e2 43 80 被识别为UID, 而 c6 和 9b 是作为校验值 Check Bytes 存在的.

OTP 区
-----

前面提到Ultralight 的安全性近乎于零, 是因为它设有这个One time programmable 区. 整个区分为 4 bytes, 默认数值为 00 00 00 00. 通常将其作为为车票的计数器使用. 通过 01 对每个 bits 进行 OR 不可逆运算. 直到 00 全部用完车票作废.不过这个OTP 也是可以通过激活 Lock Byte 来 bypass. 因为 Compass 系统并无使用OTP , 所以无做此测试.

![](http://drops.javaweb.org/uploads/images/0bfa08776dfee19e65bccc18d99e9abc257a186c.jpg)

0x02 实战测试 — Single Fare Reset Attack
====================================

需要事先声明整个测试过程使用的是预先支付的车票. 并仅是在车站入口处测试了 Reset 攻击, 并无实际逃票行为. 所以不要担心会发生被请喝茶的悲剧. 而且在下也反对滥用此类技术来做坏事... :p

其实整个攻击过程非常简单. 因为Data 区可任意读写无需认证. 所以我们可以事先 dump 出 Compass 车票的原始数据. 等车票过期无法使用后, 用手机 APP 将原始数据写回车票. 从而实现 Reset 攻击, 达到系统绕过目的. :) 整个攻击过程出奇的简单对吗? 而从 Translink 的角度来看, 又有哪些防御方案呢? 其实 NXP 公司早就提供了3DES加密的 MIFARE Ultralight C. 不知道为什么 Translink 在系统设计之初不考虑呢?

0x03 总结
=======

* * *

最后要感谢在整个研究过程中提供过帮助的弟兄们. 同时在下认为系统安全加固, 有时也取决于自身对问题的态度. 出了问题不积极修复, 却试图将问题隐藏. 并寄希望于掌握了解方法的人越少越好. 这是十分不明智的处理态度.

![](http://drops.javaweb.org/uploads/images/e39436d972740ce28478b564505d25f1eb1a1bd5.jpg)

在这里强烈鄙视温哥华交通公司 TransLink. 在漏洞曝光后明知系统存在隐患的情况下仍放任不理. 当记者采访时还摆出一副有种你咬我的嘴脸. 那好吧 May the luck be with you…FXXK YOU…Now we all know how to hack you..

![](http://drops.javaweb.org/uploads/images/8532424afcf56b0c8586246c050d8019d65870a8.jpg)

0x04 参考文献
=========

* * *

*   http://www.nxp.com/documents/data_sheet/MF0ICU1.pdf
*   https://www.youtube.com/watch?v=Czvn4L1r6f4 (Building safe NFC system --30c3)
*   http://www.cbc.ca/news/canada/british-columbia/compass-ticket-hack-1.3535955
*   http://bc.ctvnews.ca/security-flaw-lets-smartphone-users-hack-transit-gates-1.2852464
*   https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2012/september/ultrareset-bypassing-nfc-access-control-with-your-smartphone/