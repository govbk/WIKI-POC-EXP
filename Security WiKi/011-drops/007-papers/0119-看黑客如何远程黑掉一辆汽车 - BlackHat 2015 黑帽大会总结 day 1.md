# 看黑客如何远程黑掉一辆汽车 - BlackHat 2015 黑帽大会总结 day 1

0x00 序
======

* * *

今天是Black Hat 2015第一天，九点钟开场。开场介绍是由Black Hat创始人Jeff Moss讲的。随后又请来了Stanford law school的Jennifer Granickz做了keynote speech。

![enter image description here](http://drops.javaweb.org/uploads/images/e51a2f447988a9a0c624ba8f697c9c18100b9b4a.jpg)

随后就开始Black Hat的正会了，因为Black Hat是9个分会场同时进行，所以我们只能挑一些比较感兴趣的演讲去听。

0x01 ANDROID SECURITY STATE OF THE UNION
========================================

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/944dc2a73b23c8409664adef55ada75d955281db.jpg)

这个talk的演讲者是Google Android security team的leader , Adrian Ludwig。 Adrian首先介绍了android系统的一些安全策略，比如说应用隔离（sandbox，SElinux，TrustZone等），设备完整性（开机锁，数据加密等），内存通用防御（NX, ASLR等）等等。随后介绍了google公司在android安全上的贡献，比如说保证google play上app的安全性，更安全的浏览器chrome，设备管理器等。

![enter image description here](http://drops.javaweb.org/uploads/images/0e4393fc9507ebd5d5751dbe1f0bdff3c35e5d61.jpg)

接着Adrian提到google和越来越多的厂商开始进行合作，能够更快的patch设备。比如说libstagefright漏洞在八月份就为上百个设备推送了patch。

![enter image description here](http://drops.javaweb.org/uploads/images/edb9f360129893ac5a32943f14cf610f07b344a6.jpg)

随后，Andrian说，因为我们在BH做演讲，所以我们要讲一些“坏”的消息。首先讲的是在android有很多的malware，但是android有多层的防御，malware必须全部突破才能对设备产生危害。

![enter image description here](http://drops.javaweb.org/uploads/images/c6bb477b20757cab9eaea0502a22e29a6412f3e5.jpg)

接着Andrian介绍了一些Google统计的安全数据。主要是Potentially Harmful Applications (PHA)的数据。俄罗斯的PHA一直非常高，中国时高时低。并且Andrian的号称从2015年2月开始Google play上就没有发现PHA了，但第三方市场一直都有很多。

![enter image description here](http://drops.javaweb.org/uploads/images/3e5024d9a2001f24180a17349514aeb07f344300.jpg)

然后Andrian讲了Google应对漏洞的策略：及时扫描google play和第三方市场，并将利用漏洞的malware加入黑名单；尽快发布patch；针对不同的漏洞增加一些应急策略（比如为了应对libstragefright漏洞，在修复前android不会自动加载附件）。

![enter image description here](http://drops.javaweb.org/uploads/images/53d3d8b9c92c3b19029838de1d5bee6b141ebb9c.jpg)

Andrian最后讲了android的漏洞奖励计划。

个人总结：相对Andrian在之前大会上的演讲，Android security team已经没有以前的自信了，以前总是说Android绝对安全，那些病毒和漏洞的消息只不过是媒体夸大罢了。这次演讲的态度却有很大转变，首先表示Google可以在漏洞出现的时候尽量第一时间patch。然后又公布漏洞奖励计划，鼓励大家第一时间提交漏洞信息。明显感觉对自己一家搞定android安全没有太大信心了。

0x02 ATTACKING INTEROPERABILITY - AN OLE EDITION
================================================

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/eb12d751dff086c5b7f279d98e80a7923421203d.jpg)

这个演讲来自Intel security，也就是原来的麦咖啡。OLE是Object Linking and Embedding 的缩写。OLE是COM (Component Object Model)的一部分。几乎所有的office zero-day都和OLE有一定的关系。Hacker可以利用OLE加载非ASLR的dll，进行堆喷射等。比较常见的OLE就是一个文档中包含了另一个文档。当双击另一个文档时，就会调用OLE。

![enter image description here](http://drops.javaweb.org/uploads/images/9443e97ef9fea6a3312164e1f3e41447bf148c73.jpg)

Speaker首先介绍了OLE的初始化过程。然后讲了三个在OLE初始化时候的攻击面：CocreateInstance使用的CLSID，IPersistStorage::Load()函数调用的存储，IOleObject::DOVerb使用的verb参数。 然后介绍了利用这些攻击可以产生的结果：1.可以加载没有ASLR的dll到内存中。2.可以造成内存破坏。3.dll预加载hijack攻击。然后speaker预测会有更多office OLE 0day会被发现。最后speaker演示了win7 x64下的OLE 0day的2个demo。

0x03 ABUSING SILENT MITIGATIONS - UNDERSTANDING WEAKNESSES WITHIN INTERNET EXPLORERS ISOLATED HEAP AND MEMORYPROTECTION
=======================================================================================================================

* * *

这个talk是ZDI做的，也就是pwn2own的主办者。ZDI首先讲了heap上经常使用的UAF漏洞，然后讲了微软在2014年引进了两种新的攻击缓解技术：isolated heap和memory protection。

Isolated heap的防御方法是根据type来分配不同的heap，这样的话不同类型的数据就不会互相影响。memory protection会对free()操作进行保护，并在free的过程中会加一些”0”到堆中。但是即使加上了这两层，ZDI依然找到了应对的方法，并且获得了微软$125,000的奖金。但exploit的过程非常复杂，要经过很多阶段的内存分配与释放才行。有意思的是，因为memory protection的加入，反而让ZDI找到了一种新的方法用来bypass ASLR。所以说，在没有进行全面的测试就加入新的攻击缓解技术不一定是一件好事。

![enter image description here](http://drops.javaweb.org/uploads/images/dc1660a8af909f2baadb06834560a663f5278328.jpg)

最后ZDI 做了在开启了两种防御的情况下弹计算器的demo，以及开了Memory Protection的情况下利用加载dll方法做到bypass ASLR的demo。

0x04 REMOTE EXPLOITATION OF AN UNALTERED PASSENGER VEHICLE
==========================================================

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/5229c9c45837d74aaafd192ccafddd4b2105e6fe.jpg)

Charlie Miller是twitter的安全研究员，是工业界非常有名的人物。这次的talk估计是本届BH最火的talk了，还没开始下面就已经人山人海了。

![enter image description here](http://drops.javaweb.org/uploads/images/16f1096754c386e4e4c1f6e63951eae48ca107c3.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f2c93966187b5a8e38290363d3171c6e4163ff2b.jpg)

talk讲了两种远程攻击汽车的方法。首先是通过wifi入侵车: Charlie Miller先逆向了汽车WPA2密码的生成方式，发现WPA2的密码是根据设定密码的时间作为种子生成的随机密码，并且首次生成以后并不会改变。所以说当知道了生成密码的时间，就可以暴力破解出密码。比如说知道了哪一天设置的密码就可以在1小时内暴力猜出密码。

![enter image description here](http://drops.javaweb.org/uploads/images/45e44328cb38638211ff5becec9bff00b1958b80.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/291d5f8ffa6d777967d5cf800e87bdfd04eff35a.jpg)

进入车的wifi内网后，Charlie发现汽车打开了6667端口运行D-BUS服务。D-BUS是以root模式运行。其中有一个服务叫NavTrailService可以进行命令injection，然后就获取到root shell。

![enter image description here](http://drops.javaweb.org/uploads/images/e0f518815710389d2dc4ea0f00d00d1fb9087143.jpg)

另一种方式是通过蜂窝网络入侵汽车，首先采用femto-cell（伪造蜂窝基站）的方法对区域内的ip进行扫描，然后寻找打开了6667端口的设备，也就是打开D-BUS服务端口的汽车。随后采用和wifi攻击渠道一样的命令injection方法获取到root shell。

![enter image description here](http://drops.javaweb.org/uploads/images/409a66a727f6074ecb583e8a93f2d9fe4fd930cf.jpg)

但是Charlie讲到，即使有root权限也只能控制一些media的东西。想要控制汽车还需要对系统进行修改。Charlie采用的方法是修改并更新固件。Charlie发现目标汽车有个严重的安全漏洞，那就是汽车的系统不会验证固件的签名，因此通过固件修改系统并加入后门变为了可能。

![enter image description here](http://drops.javaweb.org/uploads/images/54e78b7acd30bdd9cc7816cb32161106c313d0cd.jpg)

所以最终攻击过程如下：先利用基站搜索有漏洞的汽车，然后远程攻击NavTrailSerivce，重新刷带有后门的固件，等待目标汽车固件更新后就可以进行进行远程控制了。随后Charlie Miller演示了各种控制汽车的视频，让全场沸腾不已。

![enter image description here](http://drops.javaweb.org/uploads/images/5521d40e7f8dadb46482857084093570d10e9165.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c79e57951013df7c5138f371ac49bcef8f0b7a2c.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0556ad15c0fdb091c22b8dc6c606c906ce278a1c.jpg)

0x05 OPTIMIZED FUZZING IOKIT IN IOS
===================================

带来这个演讲的是阿里移动安全部门的long lei以及潘爱民老师。

![enter image description here](http://drops.javaweb.org/uploads/images/aef67330b8ff24872ada6903983c658efaab9dc3.jpg)

这个工作主要有三个贡献：1、一套非常详细的获取IOKit内核信息的方法。2、一套用来fuzzy IOKit的框架。3、2个fuzzy出来的漏洞分享。

![enter image description here](http://drops.javaweb.org/uploads/images/1dafbc11c2a176dba438ab2d8de05ebb4ca23498.jpg)

在这个工作之前，安全研究人员一般使用ida进行静态的分析，但效果并不理想。于是long lei提出了一种在越狱的情况下动态获取IOKit信息的方法。但是获取IOKit在内核中的信息非常麻烦，要对各种meta数据信息进行parse，是一项工程量非常大工作。

![enter image description here](http://drops.javaweb.org/uploads/images/b307410e039aaf8f9c264af363958287f03b5226.jpg)

在Fuzz方面，Fuzzer系统会使用Mobile Substrate框架对关键函数进行hook，随后进行fuzz工作。

![enter image description here](http://drops.javaweb.org/uploads/images/338b5211048167c15ed040e836f9aded06473359.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/5a9a68822648e82e2da9b82c7e17c8fa09fd4ca3.jpg)

最后，long lei分享了2个用这套fuzz系统发现的漏洞，并且其中一个信息泄露的漏洞已经报给了苹果并且在最新iOS上修复了。

0x06 ATTACKING ECMASCRIPT ENGINES WITH REDEFINITION
===================================================

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/9873311f8088e0047d7f126904c1bde0a95c3e95.jpg)

这个talk的演讲者是Natalie Silvanovich。来自Google的Project Zero团队。ECMAScript 是javascript的前身。这个talk主要讲了在ECMAScript中，数据类型进行转换时产生的问题。比如说类型A转换成了类型B，有一些数据可能会进行错误的转换，从而造成可利用的漏洞。

![enter image description here](http://drops.javaweb.org/uploads/images/b1c27fc8e7810b7a1b115096e8e8872762efe17d.jpg)

Natalie Silvanovich举了很多例子进行讲解，其中包括了最近非常火的Hacking Team的flash 0day。随后还讲解了如何寻找这类的漏洞，比如说多用IDA对数据转换函数进行进行逆向以及使用fuzzer等。

0x07 第一天总结
==========

* * *

总的来说第一天的演讲无论是在名气上还是质量上都是相当高的。并且这次有很多国内安全公司的人参与和学习，一定会对国内安全圈的发展有很好的推进作用。那就让我们继续期待明天的会议吧。