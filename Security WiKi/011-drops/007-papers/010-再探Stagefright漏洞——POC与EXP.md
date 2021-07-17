# 再探Stagefright漏洞——POC与EXP

**作者:Qever**

0x00 前言
=======

* * *

在之前的《抛砖引玉——Stagefright漏洞初探》中，我们确定了漏洞的产生位置，然后整篇文章就戛然而止了。此漏洞毕竟影响很深，有些细节不知当讲不当讲。本篇文章来简单扒一扒漏洞利用的方案。只论思路，具体的Exp还是等漏洞具体细节公布后再做讨论。

0x01 手把手教你构造POC
===============

* * *

在上篇文章里面，给出了一个POC文件，现在我们就来说说这个文件是怎么构造的。

首先，需要准备一个MP4文件。这里使用的是从网上随意下载的一个文件。

之后，需要为这个mp4文件添加一个封面。笔者使用的工具是iTunes，在显示简介的插图里面可以为其添加封面图片。

![enter image description here](http://drops.javaweb.org/uploads/images/aea9f47b539c05ad78223c26ab59b50c59bd8b20.jpg)

下一部，使用010Editor打开添加封面的poc.mp4文件。然后搜索字符串”covr”。

![enter image description here](http://drops.javaweb.org/uploads/images/af3338e11d6af627da11663f820f3853e63754c1.jpg)

最后，把”covr”前面4个字节改为`00 00 00 01`，后面8个字节改为`00 00 00 01 00 00 00 0F`

![enter image description here](http://drops.javaweb.org/uploads/images/3c85daa3b5bc62c7135921a7fc3448bc103acd3a.jpg)

保存之后，扔到手机中打开。由于mediaserver崩溃之后，会立刻重启。所以我们需要系统Log来辅助验证漏洞的触发。

![enter image description here](http://drops.javaweb.org/uploads/images/4457b6cb14f36ea48fe27d410d2f06abbcafa3c4.jpg)

通过Log就能发现，mediaserver。其实这幅图还包含了其他的信息，后面再说。

0x02 知其所以然
==========

* * *

要搞清楚，POC为什么要这样做，就必须要从源码下手。 我们在`/frameworks/av/media/libstagefright/MPEG4Extractor.cpp`中继续看相关源码。

![enter image description here](http://drops.javaweb.org/uploads/images/605cb96c751c185cbad4ed0f2f1096d0bc8d434e.jpg)

前面说过，这个漏洞的原因，在于`chunk_data_size = 0xFFFFFFFF`。使得`chunk_data_size + 1 = 0`，造成了申请内存的长度为0，然后往内存中拷贝数据时越界写。

![enter image description here](http://drops.javaweb.org/uploads/images/e986437296d05f5178793b7fb2a9a3935e94a320.jpg)

那么我们就看看`chunk_data_size`如何才能等于0xFFFFFFFF。

![enter image description here](http://drops.javaweb.org/uploads/images/372f18b3a8162831345c0696b1f0d811b3e31e1e.jpg)

从这里就能看出来。`*offset – data_offset = 8`。也就是说,`chunk_data_size`要等于`0xFFFFFFFF`。Chunk_size就必须等于`0xFFFFFFF + 8`。

![enter image description here](http://drops.javaweb.org/uploads/images/695eac08fd93843aa4ef0d2e652974963f87ab5f.jpg)

但是，可以看到chunk_size是从*offset处读取了4个字节进行转换的，最大值也就是0xFFFFFFFF了。 同时注意chunk_type，后面可以看到，chunk_type的值是`FOURCC('c', 'o', 'v', 'r')`，也就是`(int)’covr’`，这就是为什么要用字符串”covr”做定位的原因。

回来继续看chunk_size，发现类型实际上是uint64_t，也就是说有可能会大于0xFFFFFFFF。继续看代码。

![enter image description here](http://drops.javaweb.org/uploads/images/cb8ff41fb3e4fe59848dede03cd608c84ed0c102.jpg)

这段就很清楚了。如果之前读取到的`chunk_size == 1`，那么就读取*offset + 8处的8个字节，作为chunk_size的值，同时data_offset会加8。

由此可以确定。当*offset处内存值设置为

```
00 00 00 01 ‘c’ ‘o’ ‘v’ ‘r’ 00 00 00 01 00 00 00 0F

```

可以使chunk_data_size的值成为0xFFFFFFFF达到攻击的目的！

0x03 没Exp你说个铲铲
==============

* * *

看过上面的内容，相信大家也该了解到，POC还是非常简单的，实际上就是没啥技术含量。相信大多数人关心的还是Exp。不过因为是未修复的漏洞，所以想伸手要Exp的就不要想了。下面只是来讲讲利用的思路。没兴趣的就可以直接跳过了。

根据之前的分析，可以确定该漏洞是堆的越界写引起的。那么利用思路就只有一个，就是越界修改其他对象的值，造成在使用或者析构的时候出错，跳入shellcode执行。

但是这个漏洞的难点在于，攻击载体是一个视频文件，本身没有执行代码的能力，也就没办法干涉到内存布局，也没办法获取内存布局信息。由此使得基本无法稳定利用。由于内存地址问题，反正笔者目前尚未发现能比较稳定的利用方法，如果哪位大牛有，欢迎分享！

0x04 如何寻找Exp
============

* * *

事实上，要寻找Exp的思路还是比较简单的。从前面`00 00 00 01 00 00 00 0F`开始，逐渐增加文件大小，然后一直测试，收集崩溃信息。找寻利用点。

笔者还算是幸运，并没有费多大的力气，就找到了一个非常明显的利用点。 还是回到之前的崩溃截图，我们来看堆栈信息。

![enter image description here](http://drops.javaweb.org/uploads/images/15b89e4fdc1ca662367d9f470ece8d684269d6d6.jpg)

根据堆栈，可以看到，是一个HTTPBase的智能指针，在析构的时候崩溃了。

等等，`android::RefBae::decStrong`和`android_atomic_dec`，之前研究过Android漏洞人，是不是觉得有点眼熟？这个东西实际上已经出现过一次了，是在CVE-2014-7911里面。

我们来看看decStrong的实现。

![enter image description here](http://drops.javaweb.org/uploads/images/c43853c93ab279ee178d8b8715c0f36e9c353d70.jpg)

可以看出，当`android_atomic_dec`返回值为1的时候。会触发一句BLX R2。 这段通俗一点讲，就是

```
If(*(*(offset + 4)) == 1){
    r2 = *(*(*(offset + 4) + 8) + 0xC)
    blx r2;
}

```

代码执行！！数据可控！！！

我们随后可以把mp4进行填充一下，得到以下的结果

![enter image description here](http://drops.javaweb.org/uploads/images/e2567bb1955041907c489df57fa9c872ff3289f2.jpg)

也就是说，针对我的mp4文件，文件偏移在`0x96a8-4`处的值，就是上面所说的offset。

知道offset之后，就可以构造数据，达到代码执行的目的！！！！！

0x05 现实很骨感
==========

* * *

到此，找到了一种利用漏洞的方案。虽然理论上可行，但是在实际操作中，并不是那么如意。

最主要的一点，在于堆越界写的地址上面，这个地址并不是固定的。好在经过测试，我们发现是在一定范围内变化。在笔者的Nexus5手机上，这个范围大概是`0xb7000000~0xb9000000`之间。如果通过大量的测试和调整，还是够覆盖准确的。

另外一个问题就是执行权限。在堆上申请的内存本身是没有执行权限的。所以需要一个跳板才行，但是由于攻击载体只是一个视频文件，所以这并不是一件简单的事情。

至于后续怎么编写shellcode，本身也存在一些问题。

当然，这些都不是本篇文章所考虑的内容 =。=

0x06 总结
=======

* * *

还是那句话，本漏洞由于未修复。我们只能根据情况逐渐公开研究结果，以免造成不好的影响。

在厂商发布更新补丁之前，我们来说说防御。

对于该漏洞的防范，建议是关闭彩信自动下载。但是实际上通过任何渠道传播的视频，都可能利用该漏洞。包括通过微信发送视频，接收者根本无法分辨是否为mp4格式文件，点击播放就可能被黑客攻击。

目前大部分厂商都在尝试主动查杀视频文件的防御方案。但是笔者认为这完全是事倍功半，而且由于无法监控所有途径传播的视频文件，所以无法真正达到防御的目的。

目前，猎豹移动安全中心正在尝试一种被动式的防御方案，可以有效降低攻击危害。敬请关注猎豹移动相关资讯。
