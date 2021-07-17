# 关于libStagefright系列漏洞分析

0x00 前言
=======

* * *

文章对应着CVE-2015-{1538,1539,3824,3826,3827,3828,3829}7个CVE，具体映射关系目前不明。此次安全漏洞号称影响“95%”安卓手机的安全。通过跟进此次漏洞的攻击面来看，这种说法毫不夸张，外界报道的关于一个彩信就直接打下机器的说法也是可信的。但这也仅仅是众多攻击面中的一条而已。

0x01 攻击面分析
==========

* * *

libStagefright默认会被mediaserver使用，也就是说，如果恶意的视频文件有机会被mediaserver处理到，该漏洞就有机会触发，举例：

如文件管理app，如果视频被存放在sdcard，那么打开文件管理app，下拉列表到露出视频，就会触发缩略图解析，漏洞触发。

图库app，点击本地图片会出现缩略图，如果视频在sdcard，或者download目录，这时候也会触发。

微信同样受到影响。通过微信发送的视频，点击也会导致media server崩溃。此外，收到的视频即使用户不点击，后面在微信中发送图片时，也会造成前面gallery,文件管理器同样的效果，也会触发缩略图过程并溢出。

![enter image description here](http://drops.javaweb.org/uploads/images/ab473fcaf2acf65dbc66a9b5406c1ec77696696f.jpg)

在最新版的Chrome43版中打开一个video链接（mp4），无需点击自动触发。

![enter image description here](http://drops.javaweb.org/uploads/images/618021ee41ef018807f83bbf02234835a8bbee3e.jpg)

开机同样是一个触发点，mediaprovider会扫描sd卡里的所有文件，并且尝试去解析，恩开机自启动

![enter image description here](http://drops.javaweb.org/uploads/images/63b3fb373d359d0fa6f6d4d56de5df7a7fee89cc.jpg)

media framework的架构如下：基本上采用了android的media框架来开发的程序都会受到影响。

![enter image description here](http://drops.javaweb.org/uploads/images/b4773c068aed554d835a445da019f2cc4b403974.jpg)

看到这里，想说的是，外界所谓的那些，关闭彩信功能保平安也就寻求个心理安慰吧。从根源上看大部分（有一个例外）都和整数计算的上溢/下溢相关，因为这个问题，间接导致了后续的内存破坏等相关的安全问题。

### 1.1. 代码分析

#### 1.1.1. No1 heap 读越界

```
1. status_t MPEG4Extractor::parseChunk(off64_t *offset, int depth) {
2. uint32_t hdr[2];
3. uint64_t chunk_size = ntohl(hdr[0]);
4. uint32_t chunk_type = ntohl(hdr[1]);
5.
6. switch(chunk_type) {

```

只有下面几种chunk_type才会触发分支parse3GPPMetaData：

```
1. case FOURCC('t', 'i', 't', 'l'):
2. case FOURCC('p', 'e', 'r', 'f'):
3. case FOURCC('a', 'u', 't', 'h'):
4. case FOURCC('g', 'n', 'r', 'e'):
5. case FOURCC('a', 'l', 'b', 'm'):
6. case FOURCC('y', 'r', 'r', 'c'):
7. {
8. *offset += chunk_size;
9.
10. status_t err = <span style="color: #ff0000;">parse3GPPMetaData</span>(data_offset, chunk_data_size, depth);
11.
12. if (err != OK) {
13. return err;
14. }
15.
16. break;
17. }

```

以上parse3GPPMetaData会触发两个3gp格式的漏洞。 第一个setCString heap读越界，首先从文件中offset读size数据到buffer。

```
status_t MPEG4Extractor::parse3GPPMetaData(off64_t offset, size_t size, int depth) {
1. if (size &lt; 4) {
2. return ERROR_MALFORMED;
3. }
4.
5. uint8_t *buffer = new (std::nothrow) uint8_t[size];
6. if (buffer == NULL) {
7. return ERROR_MALFORMED;
8. }
9. <span style="color: #ff0000;">if (mDataSource-&gt;readAt(</span>
10. <span style="color: #ff0000;">offset, buffer, size) != (ssize_t)size) {</span>
11. delete[] buffer;
12. buffer = NULL;
13.
14. return ERROR_IO;
15. }

```

然后，这个类似strcpy，所以就是 mFileMetaData->setCString(metadataKey, (const char *)buffer + 6);

https://android.googlesource.com/platform/frameworks/av/+/android-5.1.1_r8/media/libstagefright/MetaData.cpp

```
1. bool MetaData::setCString(uint32_t key, const char *value) {
2. return setData(key, TYPE_C_STRING, value, <span style="color: #ff0000;">strlen</span>(value) + 1);
3. }

1. bool MetaData::setData(
2. uint32_t key, uint32_t type, const void *data, size_t size) {
3. bool overwrote_existing = true;
4.
5. ssize_t i = mItems.indexOfKey(key);
6. if (i &lt; 0) {
7. typed_data item;
8. i = mItems.add(key, item);
9.
10. overwrote_existing = false;
11. }
12.
13. typed_data &amp;item = mItems.editValueAt(i);
14.
15. item.setData(type, data, size);
16.
17. return overwrote_existing;
18. }

```

注意到size是动态的，所以这里一般不会溢出，但会出现读越界。

```
1. void MetaData::typed_data::setData(
2. uint32_t type, const void *data, size_t size) {
3. clear();
4.
5. mType = type;
6. <span style="color: #ff0000;">allocateStorage</span>(size);
7. memcpy(storage(), data, size);
8. }

```

读到的内容被保存到一个metadata中，或许可以泄漏（例如title, artist这些信息）

![enter image description here](http://drops.javaweb.org/uploads/images/aff4290678cca6a526e39a0d918a20e551b58c33.jpg)

#### 1.1.2. No2 heap 越界写

第二个是under flow，如果size<6，那么len16会很大，会对buffer（还是刚才的heap）后面很大一片内存作bswap_16操作，写的内容不太可控

```
1. if (metadataKey &gt; 0) {
2. bool isUTF8 = true; // Common case
3. char16_t *framedata = NULL;
4. int len16 = 0; // Number of UTF-16 characters
5.
6. // smallest possible valid UTF-16 string w BOM: 0xfe 0xff 0x00 0x00
7. if (size - 6 &gt;= 4) {
8. len16 = ((size - 6) / 2) - 1; // don't include 0x0000 terminator
9. framedata = (char16_t *)(buffer + 6);
10. if (0xfffe == *framedata) {
11. // endianness marker (BOM) doesn't match host endianness
12. for (int i = 0; i &lt; len16; i++) {
13. framedata[i] = <span style="color: #ff0000;">bswap_16</span>(framedata[i]);
14. }
15. // BOM is now swapped to 0xfeff, we will execute next block too
}

```

根据前面的计算，这里的size就是`chunk_data_size`，代表这个chunk中除去header外的`data size`。计算方式如下：

`off64_t data_offset = *offset + 8;`在解析header过程中自然标记data开始的offset

```
off64_t chunk_data_size = *offset + chunk_size – data_offset;

```

所以`chunk_size<14`且`>8`即可。`Chunk_size`来自文件tag前面4字节。

#### 1.1.3. No3 heap overflow

然后是`mpeg tx3g tag`的，`chunk_size`是`uint`，与`size`之和溢出，导致实际分配比`size`小的内存。后面的`memcpy heap overflow`，写入的data应该是可控的。

![enter image description here](http://drops.javaweb.org/uploads/images/c86ae77371214731478d7d5388685491afa66943.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/ba8b3119480c9a7fa8950e5b483e8dce4cd5ae7f.jpg)

将trak修改为tx3g，然后前面的改为ffff

![enter image description here](http://drops.javaweb.org/uploads/images/a3796316c4f33235c9c5581a34fb1e63b1fdf000.jpg)

#### 1.1.4. No4 heap 越界读

出现在covr这个tag处理时，`chunk_data_size`小于`kSkipBytesOfDataBox`时，`setData`会读过`buffer`的边界。由于`setData`会分配内存，但多半分配失败，所以可能也会导致向地址为0的内存写入。

![enter image description here](http://drops.javaweb.org/uploads/images/65500f4f0d881440572d4c9f17dfe7f0009cf248.jpg)

#### 1.1.5. No5 heap 越界写

当`chunk_data_size=SIZE_MAX`时，+1导致分配0长度的内存，后面的`readAt`会边读文件边写入buffer，在读到文件结束之前已经导致了`heap write`越界。由于覆盖数据来自文件，所以内容与长度都是可控的。

![enter image description here](http://drops.javaweb.org/uploads/images/67acaa82262bbb7e130c4340738638d3cb77a16d.jpg)

#### 1.1.6. No6 Integer overflow

处理`stsc`这种`tag`时，调用了`setSampleToChunkParams`方法

```
1. case FOURCC('s', 't', 's', 'c'):
2. {
3. status_t err =
4. mLastTrack-&gt;sampleTable-&gt;setSampleToChunkParams(
5. data_offset, chunk_data_size);
6.
7. *offset += chunk_size;
8.
9. if (err != OK) {
10. return err;
11. }
12.
13. break;
14. }

```

这个方法内有`integer overflow`，主要是循环过程中，在计算类似`mSampleToChunkEntries[i].startChunk`的时候，内部实际上是按照`i*sizeof(SampleToChunkEntry)+ offset(startChunk)`来计算的，这里可能`overflow`，但从这里看不一定造成内存破坏，可能会干扰执行逻辑。

https://android.googlesource.com/platform/frameworks/av/+/android-5.1.1_r8/media/libstagefright/SampleTable.cpp

```
1. mSampleToChunkEntries =
2. new SampleToChunkEntry[mNumSampleToChunkOffsets];
3.
4. for (uint32_t i = 0; i &lt; mNumSampleToChunkOffsets; ++i) {
5. uint8_t buffer[12];
6. if (mDataSource-&gt;readAt(
7. mSampleToChunkOffset + 8 + i * 12, buffer, sizeof(buffer))
8. != (ssize_t)sizeof(buffer)) {
9. return ERROR_IO;
10. }
11.
12. CHECK(U32_AT(buffer) &gt;= 1); // chunk index is 1 based in the spec.
13.
14. // We want the chunk index to be 0-based.
15. mSampleToChunkEntries[i].startChunk = U32_AT(buffer) - 1;
16. mSampleToChunkEntries[i].samplesPerChunk = U32_AT(&amp;buffer[4]);
17. mSampleToChunkEntries[i].chunkDesc = U32_AT(&amp;buffer[8]);
18. }

```

所以补丁增加了校验

```
+ if (SIZE_MAX / sizeof(SampleToChunkEntry) &lt;= mNumSampleToChunkOffsets)
+ return ERROR_OUT_OF_RANGE;

```

#### 1.1.7. No7 parseESDescriptor Integer overflow

这里的主要问题是只在开始检查了size>=3，然后就-2，–，后面又继续几次-2,-length都没法保证不溢出。

```
1. status_t ESDS::parseESDescriptor(size_t offset, size_t size) {
2. if (size &lt; 3) {
3. return ERROR_MALFORMED;
4. }
5.
6. offset += 2; // skip ES_ID
7. size -= 2;
8.
9. unsigned streamDependenceFlag = mData[offset] &amp; 0x80;
10. unsigned URL_Flag = mData[offset] &amp; 0x40;
11. unsigned OCRstreamFlag = mData[offset] &amp; 0x20;
12.
13. ++offset;
14. --size;
15.
16. if (streamDependenceFlag) {
17. offset += 2;
18. <span style="color: #ff0000;">size -= 2;</span>
19. }
20.
21. if (URL_Flag) {
22. if (offset &gt;= size) {
23. return ERROR_MALFORMED;
24. }
25. unsigned URLlength = mData[offset];
26. offset += URLlength + 1;
27. <span style="color: #ff0000;">size -= URLlength + 1;</span>
28. }
29.
30. if (OCRstreamFlag) {
31. offset += 2;
32.<span style="color: #ff0000;"> size -= 2;</span>
33.
34. if ((offset &gt;= size || mData[offset] != kTag_DecoderConfigDescriptor)
35. &amp;&amp; offset - 2 &lt; size
36. &amp;&amp; mData[offset - 2] == kTag_DecoderConfigDescriptor) {
37. // Content found "in the wild" had OCRstreamFlag set but was
38. // missing OCR_ES_Id, the decoder config descriptor immediately
39. // followed instead.
40. offset -= 2;
41. size += 2;
42.
43. ALOGW("Found malformed 'esds' atom, ignoring missing OCR_ES_Id.");
44. }
45. }
46.
47. if (offset &gt;= size) {
48. return ERROR_MALFORMED;
49. }
50.
51. uint8_t tag;
52. size_t sub_offset, sub_size;
53. status_t err = <span style="color: #ff0000;">skipDescriptorHeader</span>(
54. offset, size, &amp;tag, &amp;sub_offset, &amp;sub_size);

```

虽然没直接看到溢出的size造成影响，但可能会造成开发者未预料到的逻辑。

```
1. do {
2. if (size == 0) {
3. return ERROR_MALFORMED;
4. }
5.
6. uint8_t x = mData[offset++];
7. --size;
8.
9. *data_size = (*data_size &lt;&lt; 7) | (x &amp; 0x7f);
10. more = (x &amp; 0x80) != 0;
11. }
12. while (more);

```

#### 1.1.8. No8 SampleTable Integer overflow

https://android.googlesource.com/platform/frameworks/av/+/android-5.1.1_r8/media/libstagefright/SampleTable.cpp

32位uint相乘，然后将结果转化为64位uint

```
1.  uint32_t mTimeToSampleCount;
2.  mTimeToSampleCount = U32_AT(&header[4][4]);
3.  uint64\_t allocSize = mTimeToSampleCount * 2 * sizeof(uint32\_t);
4.  if (allocSize > SIZE_MAX) {
5.  return ERROR\_OUT\_OF_RANGE;
6.  }
7. 

```

这里存在溢出问题，虽然未看到直接的影响，但可能造成后面的检查误判。修复方法如下：

```
- uint64_t allocSize = mTimeToSampleCount * 2 * sizeof(uint32_t);
+ uint64_t allocSize = mTimeToSampleCount * 2 * (uint64_t)sizeof(uint32_t);

```

### 1.2. 总结

前面1-8个漏洞有相似之处。

No1 : 一段数据被计算`strlen`，然后分配内存并`strcpy`，但这段数据并非一定以`’\0’`结束，所以导致读越界

No2-5：都是`tag`前的4字节size没有校验，可以任意取值，导致一系列的`size`计算问题。如下图所示，所有`tag4`字节前面都有4字节的`size`：

No6-8：都是`integer overflow`，但没有看到直接内存破坏的错误。可能会造成数据异常等。

![enter image description here](http://drops.javaweb.org/uploads/images/877547e733657fb8d2da2b2b72f9805c23c75462.jpg)

### 1.3. POC

1到5这5个漏洞的触发路径非常明了。都是在parseChunk遇到某种特殊tag时，分支处理逻辑出现问题。所以构造poc只需要修改对应的tag即可。

特别是2-4，都是tag前的4字节size出现问题。只需要调整对应的size。

以下的POC是针对no3，将其中一个`trak tag`修改为`tx3g`，然后将前面的size修改为4个FF

```
07-28 20:16:10.888: I/DEBUG(247): *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
07-28 20:16:10.888: I/DEBUG(247): Build fingerprint: 'Xiaomi/cancro/cancro:4.4.4/KTU84P/4.8.22:user/release-keys'
07-28 20:16:10.888: I/DEBUG(247): Revision: '0'
<span style="color: #ff0000;">07-28 20:16:10.888: I/DEBUG(247): pid: 10928, tid: 10945, name: Binder_4 &gt;&gt;&gt; /system/bin/mediaserver &lt;&lt;&lt;
07-28 20:16:10.888: I/DEBUG(247): signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 00000004</span>
07-28 20:16:10.978: I/DEBUG(247): r0 00000000 r1 63707274 r2 b187a6e8 r3 00000000
07-28 20:16:10.978: I/DEBUG(247): AM write failure (32 / Broken pipe)
07-28 20:16:10.978: I/DEBUG(247): r4 b187a6f8 r5 00000000 r6 b8100ed0 r7 b187aa28
07-28 20:16:10.978: I/DEBUG(247): r8 74783367 r9 b66dc904 sl 000000a9 fp 00000000
07-28 20:16:10.978: I/DEBUG(247): ip b66267b7 sp b187a690 lr b6df08df pc b664346e cpsr 60010030
07-28 20:16:10.978: I/DEBUG(247): d0 0000000000000000 d1 0000000000000000
07-28 20:16:10.978: I/DEBUG(247): d2 0000000000000000 d3 0000000000000000
07-28 20:16:10.978: I/DEBUG(247): d4 3fd1cb8765719d59 d5 bebbbb3f58eabe9c
07-28 20:16:10.978: I/DEBUG(247): d6 3e66376972bea4d0 d7 3ecccccd3ecccccd
07-28 20:16:10.978: I/DEBUG(247): d8 0000000000000000 d9 0000000000000000
07-28 20:16:10.978: I/DEBUG(247): d10 0000000000000000 d11 0000000000000000
07-28 20:16:10.978: I/DEBUG(247): d12 0000000000000000 d13 0000000000000000
07-28 20:16:10.978: I/DEBUG(247): d14 0000000000000000 d15 0000000000000000
07-28 20:16:10.978: I/DEBUG(247): d16 3930373039303032 d17 2e37343932373154
07-28 20:16:10.978: I/DEBUG(247): d18 006900640065006d d19 004d0049002e0061
07-28 20:16:10.978: I/DEBUG(247): d20 0061006900640065 d21 00790061006c0050
07-28 20:16:10.978: I/DEBUG(247): d22 006c004300720065 d23 0074006e00650069
07-28 20:16:10.978: I/DEBUG(247): d24 3f77ff86776369e9 d25 bf77ff86919d591e
07-28 20:16:10.978: I/DEBUG(247): d26 3fe0000000000000 d27 4000000000000000
07-28 20:16:10.978: I/DEBUG(247): d28 3ffe542fa9d0152a d29 bfbcb8765719d592
07-28 20:16:10.978: I/DEBUG(247): d30 3ff0000000000000 d31 3fd1cb8765719d59
07-28 20:16:10.978: I/DEBUG(247): scr 20000010
07-28 20:16:10.978: I/DEBUG(247): backtrace:
07-28 20:16:10.978: I/DEBUG(247): <span style="color: #ff0000;">#00 pc 0006846e /system/lib/libstagefright.so   
(android::MPEG4Extractor::parseChunk(long long*, int)+4345)</span>
07-28 20:16:10.978: I/DEBUG(247): #01 pc 000675fb /system/lib/libstagefright.so (android::MPEG4Extractor::parseChunk(long long*, int)+646)
07-28 20:16:10.978: I/DEBUG(247): #02 pc 00068a8b /system/lib/libstagefright.so (android::MPEG4Extractor::readMetaData()+46)
07-28 20:16:10.978: I/DEBUG(247): #03 pc 00068d31 /system/lib/libstagefright.so (android::MPEG4Extractor::countTracks()+4)
07-28 20:16:10.978: I/DEBUG(247): #04 pc 00092077 /system/lib/libstagefright.so 
(android::ExtendedUtils::MediaExtractor_CreateIfNeeded(android::sp&lt;android::MediaExtractor&gt;, android::sp&lt;android::DataSource&gt; const&amp;, char const*)+206)
07-28 20:16:10.978: I/DEBUG(247): #05 pc 00075a43 /system/lib/libstagefright.so 
(android::MediaExtractor::Create(android::sp&lt;android::DataSource&gt; const&amp;, char const*)+566)
07-28 20:16:10.978: I/DEBUG(247): #06 pc 0005a00b /system/lib/libstagefright.so 
(android::AwesomePlayer::setDataSource_l(android::sp&lt;android::DataSource&gt; const&amp;)+10)
07-28 20:16:10.978: I/DEBUG(247): #07 pc 0005b519 /system/lib/libstagefright.so (android::AwesomePlayer::setDataSource(int, long long, long long)+136)
07-28 20:16:10.978: I/DEBUG(247): #08 pc 00034319 /system/lib/libmediaplayerservice.so (android::MediaPlayerService::Client::setDataSource(int, long long, long long)+196)
07-28 20:16:10.978: I/DEBUG(247): <span style="color: #ff0000;">#09 pc 00059b2d /system/lib/libmedia.so (android::BnMediaPlayer::onTransact(unsigned int, android::Parcel const&amp;, android::Parcel*, unsigned int)+332)</span>
07-28 20:16:10.978: I/DEBUG(247):<span style="color: #ff0000;"> #10 pc 00019225 /system/lib/libbinder.so (android::BBinder::transact(unsigned int, android::Parcel const&amp;, android::Parcel*, unsigned int)+60)</span>
07-28 20:16:10.978: I/DEBUG(247): #11 pc 0001d799 /system/lib/libbinder.so (android::IPCThreadState::executeCommand(int)+508)
07-28 20:16:10.978: I/DEBUG(247): #12 pc 0001db17 /system/lib/libbinder.so (android::IPCThreadState::getAndExecuteCommand()+38)
07-28 20:16:10.978: I/DEBUG(247): #13 pc 0001db8d /system/lib/libbinder.so (android::IPCThreadState::joinThreadPool(bool)+48)
07-28 20:16:10.978: I/DEBUG(247): #14 pc 000219f5 /system/lib/libbinder.so
07-28 20:16:10.978: I/DEBUG(247): #15 pc 0000ea5d /system/lib/libutils.so (android::Thread::_threadLoop(void*)+216)
07-28 20:16:10.978: I/DEBUG(247): #16 pc 0000e58f /system/lib/libutils.so
07-28 20:16:10.978: I/DEBUG(247): #17 pc 0000d248 /system/lib/libc.so (__thread_entry+72)
07-28 20:16:10.978: I/DEBUG(247): #18 pc 0000d3e0 /system/lib/libc.so (pthread_create+240)

```

从`trace`看出，这里是通过`binder`来调用`media server`提供的接口，进而对视频处理解析过程崩溃。所以溢出在`media server`进程。

### 1.4. 防护

由于`media`是安卓中非常核心的一个服务（虽然权限不高），大量的功能都涉及到这个服务。如果仅仅`stop media`来停止这个服务，手机基本无法使用，例如无法显示出桌面。

service media /system/bin/mediaserver class main user media group audio camera inet net_bt net_bt_admin net_bw_acct drmrpc mediadrm qcom_diag ioprio rt 4

在短信app中，通过设置（可在小米，华为等手机中找到这个选项）可以关闭彩信自动下载，降低风险。

但这样无法防止例如sdcard根目录, 下载目录， bluetooth这些目录被通过各种渠道发送过来的恶意视频（浏览器自动下载，usb拷贝，bluetooth，微信等），当用户一旦打开文件浏览或图库app，甚至在浏览器中直接访问视频也会被攻击。

所以大家开心的等补丁吧！