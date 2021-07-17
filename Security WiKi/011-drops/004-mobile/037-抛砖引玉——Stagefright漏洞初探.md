# 抛砖引玉——Stagefright漏洞初探

作者:qever

0x00 序
======

* * *

昨晚惊闻Stagefright爆出重大漏洞，可以造成远程代码执行，甚至发条彩信，就有可能入侵用户移动设备。这听起来可是难得一遇的大漏洞啊，作为安全人员，自然要好好扒一扒内幕了。

0x01 山重水复
=========

* * *

从新闻来看，出于某些考虑，漏洞的发现者目前并没有公布相关的细节，而是决定要留到BlackHat上再进行详细的说明。也就是说，目前所知道就是Android系统的Stagefright库存在重大安全问题，具体是什么？想知道自己去Fuzz。

虽然，看起来关于漏洞细节，并没有任何头绪。但是，作为安全人员，首先要坚信的一点，就是世界上没有不透风的墙！仔细研读漏洞的新闻稿，可以发现，该漏洞已经提交给了Google，并且Google迅速的进行了修复。同时发现，Google也已经把漏洞相关信息交给了部分合作伙伴。看完这些，就能确定，这漏洞目前还能扒。

既然Google针对此漏洞，已经在源码中进行了修复。那么首先查看了Google的相关源码提交状态。

![enter image description here](http://drops.javaweb.org/uploads/images/5c155f69528af48f4c66f80b0e7866b95a41d827.jpg)

简单翻阅了提交的log。发现了一些关于libstagefright安全问题的修复，但大多言简意赅，难以确定。

0x02 柳暗花明
=========

* * *

看起来从Google方面下手并不容易，好在Google已经将漏洞相关资料交给了合作伙伴，所以我们发现了CyanogenMod公布的一条消息。

![enter image description here](http://drops.javaweb.org/uploads/images/e1adee01fcc657086edc6a3f701956eaea4fa5ef.jpg)

也就是说，在CM12中已经对此漏洞进行了修复！

0x03 顺藤摸瓜
=========

* * *

随后，我们在github上找到了CM12的提交记录

![enter image description here](http://drops.javaweb.org/uploads/images/6e56f3aa1ce832a3fc979de4498ff2de93c7b94c.jpg)

可以看到，在CM12的最近提交中，都是对Stagefright相关漏洞的修复，根据这些修复内容，对漏洞大体上也就能有一些了解了！

0x04 抽丝剥茧
=========

* * *

我们对部分修复方案进行了简单分析。

Bug: 20139950

![enter image description here](http://drops.javaweb.org/uploads/images/fef9f64ad4972fa949c677eb160442fe7192825b.jpg)

该bug的位置在frameworks/av/media/libstagefright/SampleTable.cpp文件的SampleTable::setSampleToChunkParams函数中，从该bug的说明和修复上来看。是由于mNumSampleToChunkOffets值太大，可能造成溢出。相关代码如下

![enter image description here](http://drops.javaweb.org/uploads/images/46fc2d61ae5ba22abef9cbd8fb08100e4ae41f9d.jpg)

注意红线标注部分。可能会造成访问越界。从而引发安全问题。

mSampleToChunkOffset 是类SampleTable的成员变量，在SampleTable::setSampleToChunkParams中进行初始化，用于记录数据偏移。当mNumSampleToChunkOffsets设定为非法值的时候，就会造成readAt的时候，越界读取。

根据目前的分析，该漏洞目前并不能造成安全攻击。主要原因在于读取到的数据只是用于成员变量的赋值。由于本来就是要从文件中读取数据，所以实际上buffer内容是可控的，因为该漏洞本身没有什么安全意义，只是为了保证系统稳定性的patch。

![enter image description here](http://drops.javaweb.org/uploads/images/86bf7e94d1c84e83bdd721ffaef63971896cf2bd.jpg)

Bug: 20139950

![enter image description here](http://drops.javaweb.org/uploads/images/ff18e3f65fa6e34039190a980a525c127b0179b2.jpg)

该bug在frameworks/av/ media/libstagefright/ESDS.cpp的ESDS::parseESDescriptor函数中。直接从描述和修复代码中，就能看出来，是由于在解析过程中，对变量校验不严格，可能造成越界访问的问题。此问题并不是重点，也就不细说了。

Bug: 20923261

![enter image description here](http://drops.javaweb.org/uploads/images/e64aff2819490e6af5592743790a42311cb39d05.jpg)

此漏洞产生于frameworks/av/media/libstagefright/MPEG4Extractor.cpp的MPEG4Extractor::parseChunk函数中。从截图就可以看到漏洞的全貌了。当chunk_data_size小于kSkipBytesOfDataBox时，红线部分就会变成一个负数，由于setData的最后一个参数类型是size_t，所以就会被解析成很大的正数，从而造成错误。

其余的漏洞，大部分都是相似的原因，对读取的数据校验不严格造成解析错误。这种问题一般只能造成进程崩溃，并无法引起严重的安全问题，除非……

0x05 不期而遇
=========

* * *

看过上面列举的例子，难免有种感觉，所谓的Stagefright可能就是在危言耸听，因为大部分漏洞看起来都只是开发人员的一个小疏忽。直到我们遇到了TA……

![enter image description here](http://drops.javaweb.org/uploads/images/1d1255bb4bf65dbc93853a9a8b930d02350467b2.jpg)

从这份提交的注释里面，我们就能看到一些关键词，例如”potentially exploitable condition”。那么这个”condition”是如何产生的呢？从注释里面可以看到，是当chunk_data_size的值为SIZE_MAX的时候，会发生溢出。

chunk_data_size是一个可控的变量，来源就不多说了。我们只关注漏洞成因。

在类Linux系统下，SIZE_MAX一般为((size_t)-1)，也就是我们常见的0xFFFFFFFF(32位)，当chunk_data_size== SIZE_MAX的时候。chunk_data_size + 1的值就会为0（不要问我为什么 =。= ），下一句代码

![enter image description here](http://drops.javaweb.org/uploads/images/d9ca805a6c075c1744bbd24ac00ec2673bdc181d.jpg)

由于chunk_data_size + 1 = 0，就会造成buffer申请的内存空间为0。

之后，通过mDataSource->readAt函数，将指定内容读取到buffer所申请的内存中。

![enter image description here](http://drops.javaweb.org/uploads/images/164c73c6acf1c10929edd5a847ae48ab7a0c6a15.jpg)

可是！buffer实际申请的内存大小为0！也就是说，readAt会造成写越界，从而写系统数据，达到攻击的目的！！

由于该漏洞尚未被修复，我们的文章也就到此戛然而止了。值得一提的是，同样的问题，在同一个文件中，不止一次的出现。

![enter image description here](http://drops.javaweb.org/uploads/images/dc3a02b844bb15461a7594601a6cebd8b8eacf8d.jpg)

更多的细节，就留给各位慢慢挖掘吧。

0x06 总结
=======

* * *

由于时间水平有限，本文仅仅从patch的角度，分析了可能产生攻击的点。此漏洞毕竟影响很大，而且尚未被修复，本身不宜公布更多的细节，所以有些地方言语不详，希望能够理解。

概览全部的修复代码，发现产生漏洞的原因，都是因为对数据校验完善造成的。此次曝光的只是Stagefright的问题。考虑到Android系统中包含了大量的文件解析代码，包括图片、压缩包、音频、视频等解码库。这些库在解析文件过程中，对数据进行严格的校验了吗？会不会明天又会爆出音频解码存在严重bug？这应该是值得开发者和安全从业者深思的问题。

0x07 后记
=======

* * *

由于此漏洞不宜讲太深入，造成之前描述太过于模糊，且很多地方不准确。所以引起了一些质疑。

最后放上一个POC吧，打开文件会解析错误。由于单纯从解析错误，无法证明触发了漏洞，所以添加了一些Log作为辅证。

![enter image description here](http://drops.javaweb.org/uploads/images/8c17a46ab8e1ae784cd69347c61bae0647915762.jpg)

该截图重点在于buffer指向地址0xb8a93fe0，但是size却为0。后面覆盖之前buffer指向地址的内容是”F0 31 EC B6”，覆盖之后变为”12 34 56 78”，覆盖的长度为”x = 0x40020”。

熟悉细节的朋友也可以从mp4文件中寻找到相关修改。

最后，此mp4文件来源于网络，10+M大小，mp4格式……了解漏洞细节的，可以自行修复mp4文件，然后观看其内容。（你们懂的 =。=）

[mp4文件下载](http://static.wooyun.org/drops/20150729/0x105F2.mp4)