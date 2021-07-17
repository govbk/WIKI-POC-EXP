# Stagefright漏洞公告

作者: 迅迪 没羽 轩夏 成淼 奋龙 逆巴

0x00 什么是Stagefright
===================

* * *

StageFright是一个Android中的系统服务，可处理各种多媒体格式，由Natvie C++代码实现，多媒体应用如何与Android Native多媒体进行交互可参考如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/a76d0545552471e522a31091b109ad2ec0028828.jpg)

而Stagefright所涵盖的模块非常广

```
|-- stagefright  
|   |  
|   |-- codecs   //提供解码器实现  
|   |  
|   |-- colorconversion   //颜色空间转换  
|   |  
|   |-- foundation   //基本数据结构的实现  
|   |  
|   |-- httplive   //m3u8解析  
|   |  
|   |-- id3        // ID3 TAG解析（一般用于MP3格式的metadata容器）  
|   |  
|   |-- include    //基本头文件  
|   |   
|   |-- matroska   //matroska文件解析  
|   |  
|   |-- mpeg2ts    //mpeg2ts文件解析和数据获取一些处理  
|   |  
|   |-- mp4     

```

由于多媒体处理的实时性特征，该库通过Native代码实现，这也是的该库存在内存破坏的问题远远多于Java实现的代码。

0x01 谁发现了Stagefright
====================

* * *

以色列移动信息安全公司Zimperium研究人员Joshua Drake在7月21号发布的声明，声称会在8月的BlackHat会议上发布细节。

0x02 漏洞概要
=========

* * *

Android Stagefright框架中发现了多个整数溢出和下溢，不正确整数溢出检查等漏洞，可导致任意代码执行等问题。

攻击者通过发送包含特制媒体文件的MMS或WEB页来触发该漏洞。由于stagefright不只是用来播放媒体文件的，还能自动产生缩略图，或者从视频或音频文件中抽取元数据，如长度、高度、宽度、帧频、频道和其他类似信息。因此接收到恶意彩信的用户只要查看缩略图就可触发该漏洞。

“Stagefright”媒体播放引擎库在Android 2.2中引入，至5.1的所有版本上均存在此漏洞，预计会有95%的Android设备,约有九亿五千万的安卓设备受该漏洞影响.

使用Stagefright库的应用程序以Media权限运行，成功利用漏洞，允许攻击者浏览器媒体库相应的文件，但通过权限提升攻击，可完全控制设备。

该Stagefright漏洞所对应的CVE ID如下：

```
CVE-2015-1538  
CVE-2015-1539  
CVE-2015-3824  
CVE-2015-3826  
CVE-2015-3827  
CVE-2015-3828  
CVE-2015-3829  

```

0x03 漏洞分析
=========

* * *

根据`https://github.com/CyanogenMod/android_frameworks_av/commits/cm-12.1`提供的补丁，进行了相关的分析：

**4.1 Prevent reading past the end of the buffer in 3GPP**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/57db9b42418b434751f609ac7e5539367e9f01a6

```

该漏洞产生在以下的chunk中：

![enter image description here](http://drops.javaweb.org/uploads/images/8a471c8b2e040c7beefd003905a26f54cdace4e4.jpg)

这是一个堆内存读越界漏洞，parse3GPPMetaData方法中调用`mDataSource->readAt( offset, buffer, size)`读取size大小的数据到申请的buffer中，然后下面会调用`mFileMetaData->setCString()`方法进行内存拷贝：

![enter image description here](http://drops.javaweb.org/uploads/images/19cf6ebce5116482845eb5c7693caf3341a6c41c.jpg)

我们来看setCString()方法的最终会调用memcpy进行内在拷贝：

```
void MetaData::typed_data::setData(uint32_t type, const void *data, size_t size) {
    clear();
    mType = type;
    allocateStorage(size);
    memcpy(storage(), data, size);
}

```

由于对memcpy中size的处理不当，导致越界读取了内存数据。

**4.2 Prevent integer underflow if size is below 6**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/9824bfd6eec1daa93cf76b6f4199602fe35f1d9d

```

该漏洞是一个integer underflow漏洞，对于构造的size来说，如果size<6，可导致len16的值变的很大：

![enter image description here](http://drops.javaweb.org/uploads/images/20e52cc2c8d8bdb601473b5948c3dc064580ceb9.jpg)

导致接下来的内存越界操作：

![enter image description here](http://drops.javaweb.org/uploads/images/16eb2e052ee4feb4eb79666e8076c74315730fa6.jpg)

**4.3 Fix integer overflow when handling MPEG4 tx3g atom**

* * *

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/889ae4ad7227c395615d03b24a1667caa162c75f

```

该漏洞产生在“tx3g”的chunk中，chunk_size是uint，与size之和溢出，会导致实际分配比size小的内存。后面的memcpy函数将会发生堆溢出：

![enter image description here](http://drops.javaweb.org/uploads/images/aedc4f76afbfaf0a2478ecca0e96199404063a57.jpg)

当`mLastTrack->meta->findData(kKeyTextFormatData, &type, &data, &size)`函数调用返回为真，size值将不会为0，chunk_size与size都为uint8_t，之和后发生整数溢出，这样导致new一个比size更小的空间，在随后的memcpy将发生堆溢出：

```
bool MetaData::findData(uint32_t key, uint32_t *type,
                        const void **data, size_t *size) const {
    ssize_t i = mItems.indexOfKey(key); //键值存在 i>0
    if (i < 0) {
        return false;
    }
   const typed_data &item = mItems.valueAt(i);
   item.getData(type, data, size);
   return true;
}

```

接下来`new (std::nothrow) uint8_t[size + chunk_size]`,size与chunk_size之和发生整数溢出，值将小于size,此后的memcpy发生堆溢出：

![enter image description here](http://drops.javaweb.org/uploads/images/b4cd876dc1386fbe5c02de527a82ee41f128a596.jpg)

**4.4 Fix integer underflow in covr MPEG4 processing**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/b1f29294f1a5831eb52a81d3ee082a9475f6e879

```

从patch代码可知，由于未检测chunk_data_size的长度，导致后面的chunk_data_size – kSkipBytesOfDataBox为负数，

![enter image description here](http://drops.javaweb.org/uploads/images/99374c1011872358afb09b2208003ed52e4b92c3.jpg)

向上追溯，chunk_data_size =_offset + chunk_size - data_offset；off64_t data_offset = *offset + 8；其中chunk_size为mpeg4格式中box的chunk_size，_offset为当前的box的起始位置。由patch代码可知，有这样的不等或成立才能避免该漏洞的出现：

```
chunk_data_size <= kSkipBytesOfDataBox
⇨   *offset + chunk_size - *offset - 8 <= 16
    ⇨     chunk_size - 8 <= 16
  ⇨ chunk_size <= 24(0x18)

```

所以当chunk_size的值<=24时会触发漏洞。构造的一个样本（0x08）截图如下：

![enter image description here](http://drops.javaweb.org/uploads/images/b3a1d0f21e0ec2eb9ad2911189980a684acd0510.jpg)

**4.5 Prevent integer overflow when processing covr MPEG4 atoms**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/7ff5505d36b1cfd8b03497e0fb5aa24b5b099e45

```

从patch代码可知，由于未对chunk_data_size的长度进行限制，当`chunk_data_size>=SIZE_MAX-1时，chunk_data_size＋1>=SIZE_MAX`，导致ABuffer分配0长度的内存，后续再进行内存操作就导致堆越界。

![enter image description here](http://drops.javaweb.org/uploads/images/e0bde7af9ca4baff25cd6043c2cd2f968bf7d0f5.jpg)

**4.6 Fix integer overflow during MP4 atom processing**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/3854030bf70cb78ec0afbf90d0e7d8e1cf8f9904

```

从代码分析可知，要构造出满足条的POC样本，需要chunk_size=1，然后unint64来存储chunk_size。对于该漏洞POC的构造，我们假设：`mNumSampleToChunkOffsets = 0xFFFFFFFF/0xC`可得，`mNumSampleToChunkOffsets = 0x15555555`

我们构造如下样本：

![enter image description here](http://drops.javaweb.org/uploads/images/f5b55bf792d4247cd7378d3e0cbd21f9199262c4.jpg)

其中chunk_size 为1，`large_chunk_size`为`0x100000007`,`mNumSampleToChunkOffsets`为`0x15555555`。

加载该样本，运行截图如下：

![enter image description here](http://drops.javaweb.org/uploads/images/3c2eef10c349e15cf69401dc90f14f82148b1e70.jpg)

**4.7 Fix integer underflow in ESDS processing**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/e586b3e891e7c598449d40a9c44c70fd6663d064

```

从patch代码可知，由于未对size的大小进行检测，后续会进行多次－2操作，导致size为负数，导致堆下溢出。

![enter image description here](http://drops.javaweb.org/uploads/images/300eb28c85e10c7e853a385aedbf79c143f308b2.jpg)

要构造poc需进入ESDS.cpp查看详细代码：

![enter image description here](http://drops.javaweb.org/uploads/images/a504305c1ec5945c7ee52c57a8197d7f9114e33e.jpg)

首先获取偏移的值，并进行一系列运算，当more＝true时停止，并返回data_size，然后开始解析ESDS。

![enter image description here](http://drops.javaweb.org/uploads/images/24ede2602ded5c92613fc8c124feb74001cf4269.jpg)

从代码可以看出来当3个标志位都为1时，才会进行size－2操作，因此构造的poc必须满足3个标志位，0xE0以上数值就满足要求。因此将size修改为5，标志位修改为0xE3就能触发漏洞的畸形样本截图如下：

![enter image description here](http://drops.javaweb.org/uploads/images/6725d14fe496c38993a53a73299d16e21085f4b9.jpg)

**4.8 Fix several ineffective integer overflow checks**

补丁链接：

```
https://github.com/CyanogenMod/android_frameworks_av/commit/16c78bb6608dd5abbf3a1fc1cd98e8fc94cfb241

```

此漏洞有3处patch，涉及到3个chunk分别是“stts”、“ctts”、“stss”。是由于几个uint32型数据相乘，再赋值给uint64可能会导致溢出：

![enter image description here](http://drops.javaweb.org/uploads/images/1ee1a68de7a06bc19463fd84d6a4dd1973139b8a.jpg)

以“stts”chunk为例来说一下poc的构造： 代码分析，我可得“stts”chunk的结构头如下：

![enter image description here](http://drops.javaweb.org/uploads/images/4f7bc1cad055344b2677b14169591758a56a10c1.jpg)

第4个4字节的值即为mTimeToSampleCount，我们假设存在这样一个等式：`mTimeToSampleCount * 2 * 4 = 0xFFFFFFFF+0x1`可得，`mTimeToSampleCount＝0x20000000`我们以mTimeToSampleCount＝0x20000000构造的一个POC如下：

![enter image description here](http://drops.javaweb.org/uploads/images/52d37bdbec43de63dc1fe5ce7460e82b86e4c37a.jpg)

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/0c933995932502091f240c18734dfec946a41b59.jpg)

chunk“ctts”、“stss”也可以通过类似的方法构造出POC。

0x04 触发途径
=========

* * *

*   可通过发送嵌入恶意视频文件的彩信
*   构建嵌入恶意视频的WEB页，诱使使用Stagefright库的浏览器或应用打开
*   构建恶意视频文件，诱使链接Stagefright库的应用打开

0x05 受影响厂商
==========

* * *

```
Amazon   Barnes and Noble    
Google   HTC     
Huawei Technologies  
Kyocera Communications   
LG Electronics   
Motorola, Inc.  
Samsung Mobile   
Sony Corporation

```

等

0x06 受影响应用：
===========

* * *

由于Stagefright是一个底层的多媒体处理库，因此调用该库的应用都受此漏洞影响，我们随机检测国内主流的几个应用做，发现都存在此问题：

**6.1 绝大多数视频APP都受影响，以乐视视频为例**

```
- 受影响版本：Android/5.9.3
- 点击特制构建的视频文件，选择“乐视视频”播放：

```

![enter image description here](http://drops.javaweb.org/uploads/images/65b6210e6e6c04cf2dc9762bbd7a2c02f45acc17.jpg)

*   查看手机端，乐视视频播放文件出错：

![enter image description here](http://drops.javaweb.org/uploads/images/d550c9ef910416c85b465eec9c1389d6465bb8b3.jpg)

-查看日志信息，可以看到libstagefright.so的crash信息，在`MPEG4Extractor::parseChunk(off64_t *offset, int depth)`方法中解析文件出错，受影响代码可以参考：

```
https://android.googlesource.com/platform/frameworks/av/+/android-5.1.1_r8/media/libstagefright/MPEG4Extractor.cpp：

```

![enter image description here](http://drops.javaweb.org/uploads/images/faeff260a10dafca2e618d7715ffc0922be899f5.jpg)

**6.2 某手机浏览器**

```
- 版本：
  Android/6.0.1.1560
- 测试：
  使用某手机浏览器的二维码功能，扫描生成的视频PoC文件，
  在浏览器弹出的提示窗口中选择“直接打开”：

```

![enter image description here](http://drops.javaweb.org/uploads/images/b6e2e420e07a8195ac0f53c0d6b46e708c923b6b.jpg)

-查看手机端，播放视频文件出错：

![enter image description here](http://drops.javaweb.org/uploads/images/63721aa90fb4ecf51f72f4dc93ce7b4d45ef3f92.jpg)

-查看日志信息，可以看到libstagefright.so的crash信息，在`MPEG4Extractor::parseChunk(off64_t *offset, int depth)`方法中解析文件出错。

![enter image description here](http://drops.javaweb.org/uploads/images/a4fd6a564544c3cc8a247120364a28d074ad97ef.jpg)

**6.3某SNS通讯工具**

```
-   版本：
Android/6.2.2
-  发送特殊构建的视频文件时，点击播放会弹出“播放失败”窗口，如图：

```

![enter image description here](http://drops.javaweb.org/uploads/images/d4e8942fc126b35870b82d0d04a4681c5c79e5b3.jpg)

*   在后台接收手机的错误信息，发现了libstagefright.so的crash信息：

![enter image description here](http://drops.javaweb.org/uploads/images/597b556db0842f2197dacb50ec6700b67df43349.jpg)

可以看到解析视频文件时发生崩溃，通过视频发送或SNS形式传播，可大范围的影响用户。

0x07，缓解方案
=========

* * *

*   root安卓设备，禁用Stagefright,(会导致大量应用不可用，系统无法正常使用)
*   谨慎打开莫名的mp4文件或者陌生人发送的彩信
*   使用谷歌的Hangouts App用户请将彩信的媒体文件自动下载功能禁用
*   使用谷歌的Messenger客户端(安卓5.0以上版本的系统默认短信客户端)请关闭自动获取MMS消息功能
*   三星Galaxy S6中，按照以下步骤去禁用系统默认短信客户端中的自动获取彩信功能： 短信app-更多-设置-更多设置-多媒体消息-自动获取
*   安装阿里钱盾等安全软件，以便于防范病毒木马对该漏洞的利用

0x08 厂商解决方案
===========

* * *

Google已经发布Android 5.1.1_r5修复该漏洞，注意不是所有Android 5.1.1 (Lollipop)手机应用了该补丁，需要安装patchlevel r5补丁：

```
https://android.googlesource.com/platform/frameworks/av/+/0e4e5a8%5E!/ 
https://android.googlesource.com/platform/frameworks/av/+/5c134e6%5E!/ 
https://android.googlesource.com/platform/frameworks/av/+/030d8d0%5E!/ 

```

CyanogenMod中的cm12.1 branch已经修复该漏洞：

```
https://github.com/CyanogenMod/android_frameworks_av/commits/cm-12.1

```

积极联系通过厂商OTA进行更新

0x09 参考链接
=========

* * *

```
-   http://blog.zimperium.com/experts-found-a-unicorn-in-the-heart-of-android/ 
-   http://www.kb.cert.org/vuls/id/924951
-   http://www.forbes.com/sites/thomasbrewster/2015/07/27/android-text-attacks/ 
-   http://www.zdnet.com/article/stagefright-just-how-scary-is-it-for-android-users/ 
-   http://arstechnica.com/security/2015/07/950-million-android-phones-can-be-hijacked-by-malicious-text-messages/ 
-   https://android.googlesource.com/platform/frameworks/av/+/0e4e5a8%5E!/ 
-   https://android.googlesource.com/platform/frameworks/av/+/5c134e6%5E!/ 
-   https://android.googlesource.com/platform/frameworks/av/+/030d8d0%5E!/ 
-   http://source.android.com/devices/media.html 
-   https://www.duosecurity.com/blog/exploit-mitigations-in-android-jelly-bean-4-1

```