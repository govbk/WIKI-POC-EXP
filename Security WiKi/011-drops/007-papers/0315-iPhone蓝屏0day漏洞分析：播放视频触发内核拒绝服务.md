# iPhone蓝屏0day漏洞分析：播放视频触发内核拒绝服务

Proteas of 360 NirvanTeam

0x00 前言
=======

* * *

近期发现有人会在微信群中分享视频链接，当使用苹果设备的用户点击这个视频链接播放视频时会造成苹果设备重启。发现这个问题后，[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)析，在非越狱iPhone设备iOS 8.0.2、 iOS 8.4、iOS 8.4.1 Beta 1、iOS 9 Beta 3 系统上进行测试，均导致设备蓝屏并重启，判断为0Day所致，决定详细分析导致iPhone蓝屏的原因。

通过dump arm64位内核及Panic Log详细分析，确定崩溃发生在内核扩展 AppleVXD393.kext 中。该内核扩展主要用来解码视频帧，导致漏洞利用的原因为：没有校验指针的合法性，对空指针进行解引用所致；此外在分析过程中，我们发现了该扩展模块还存在另外一个漏洞利用的0Day，已经提交苹果官方等待确认。

为了方便测试，我们首先编写了一个简单 App，目的是便于测试、触发系统崩溃，触发后导致蓝屏重启如下图（视频演示：http://v.youku.com/v_show/id_XMTI5MTgzNjc2NA），接着为了定位内核崩溃发生的模块及具体代码，下文将做详细分析。

![enter image description here](http://drops.javaweb.org/uploads/images/d1e2a2b2f534bb4336f9475c3c86332d50a95ab5.jpg)

0x01 漏洞影响
=========

* * *

1.  该DoS影响非越狱设备，综合手中的测试设备及逆向分析，可影响iOS 8 以上的所有64位设备：iPhone 5s，iPhone 6， iPhone 6 Plus，iPad Air， iPad mini 等。
2.  如果利用网站或者借助某个平台，可以造成大规模的拒绝服务。

0x02 编写辅助崩溃的程序
==============

* * *

由于在分析的过程中我们很可能需要多次造成内核崩溃，如果每次都从微信中触发崩溃会很麻烦，也很不合理，因此我们需要先获取视频，然后用自己的程序来播放视频。

这个程序很简单，运行起来的界面如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/ed3c29f68c5777d9e0565eaf1bc8107cc9254b91.jpg)

只要点击“Play Video”就会调起播放器播放相应视频，进而引起系统崩溃。这里遇到个小问题，之前播放视频都是使用 MPMoviePlayerController，但是 MPMoviePlayerController 在播放有问题的视频时一直处于加载状态，于是换 AVPlayer 来播放视频，为了方便大家构建 Demo 进行测试，给出 “Play Video”的相应代码：

```
@implementation ViewController
// 配置界面
- (void)viewDidLoad {
    [super viewDidLoad];

    self.view.backgroundColor = [UIColor lightGrayColor];

    UIButton *playBtn = [UIButton buttonWithType:UIButtonTypeRoundedRect];
    playBtn.frame = CGRectMake(40.0f, 40.0f, 200.0f, 48.0f);
    playBtn.center = self.view.center;
    playBtn.backgroundColor = [UIColor darkGrayColor];
    [playBtn setTitle:@"Play Video" forState:UIControlStateNormal];
    [playBtn setTitle:@"Play Video" forState:UIControlStateHighlighted];
    playBtn.titleLabel.font = [UIFont systemFontOfSize:32.0f];

    [playBtn addTarget:self action:@selector(onPlayButtonClicked:) forControlEvents:UIControlEventTouchUpInside];

    [self.view addSubview:playBtn];
}
// 防止屏幕旋转时界面错乱，影响心情
- (NSUInteger)supportedInterfaceOrientations
{
    return UIInterfaceOrientationMaskPortrait;
}
// 响应按钮点击，调起播放器
- (void)onPlayButtonClicked:(UIButton *)aSender
{
    NSString *videoPath = [[NSBundle mainBundle] pathForResource:@"crash" ofType:@"mp4"];

    self.avPlayer = [AVPlayer playerWithURL:[NSURL fileURLWithPath:videoPath]];

    AVPlayerLayer *playerLayer = [AVPlayerLayer playerLayerWithPlayer:self.avPlayer];
    self.avPlayer.actionAtItemEnd = AVPlayerActionAtItemEndNone;
    playerLayer.frame = self.view.bounds;
    [self.view.layer addSublayer: playerLayer];

    [self.avPlayer play];
}
@end

```

0x03 定位崩溃点与相关模块
===============

* * *

首先播放视频，系统会发生崩溃，在设备重启后，从设备上读取崩溃日志，崩溃日志的主要内容如下：

![enter image description here](http://drops.javaweb.org/uploads/images/a11fdb40b10ca00453bc74f533418682cdf6ab93.jpg)

上图中比较重要的值已经被圈出来了，其中 pc 与 lr 用来定位崩溃点。另外 kernel slide 也非常重要，因为上图中的寄存器值都是经过 slide 后的值，且这个 slide 每次启动都会变化（KASLR），我们首先需要换算出真实的地址：

```
pc = 0xffffff80020c92e0 = 0xffffff800e2c92e0 - 0x000000000c200000 
lr = 0xffffff8003043a58 = 0xffffff800f243a58 - 0x000000000c200000

```

在获得真实的崩溃地址后，我们 dump 内核（因为目前还没有可以解密的 arm64 内核）：

```
[+] kernel slide: 0x2000000
[+] kernel start: 0xffffff8004002000
[+] vm perm value: 0x9d46a8bdc73a4755

```

可以看到这次启动的 slide 的值与崩溃时的内核 slide 是不同的，接下来我们将崩溃地址换算到当前 dump 到的内核：

```
pc = 0xffffff80040c92e0 = 0xffffff80020c92e0 + 0x2000000
lr = 0xffffff8005043a58 = 0xffffff8003043a58 + 0x2000000

```

然后在 IDA Pro 定位到相应的地址， PC指向如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/83b6e8fceb9d5ecc56372504b8eeea495d232cb7.jpg)

LR 指向如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/957e5b028071c28a417d09d70ed9fdf4e2602646.jpg)

从崩溃日志中可以知道崩溃时`x0 = 0x0000000000000000`，可以确定崩溃的原因是由于对空指针解引用，即：没有校验入口参数的合法性。

我们知道 iOS 内核（xnu）本身不包含视频处理相关的功能，视频相关的功能基本是由某个内核扩展进行处理的，下面就需要找出具体是哪个内核扩展出问题。

比较幸运的是， LR 指向的地址周围包含了内核扩展的信息：

![enter image description here](http://drops.javaweb.org/uploads/images/7e6d4515a1d439928c7a0106aa3926a1f83a5775.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/7177bb4c58abbe0f74a287d8c8a5f9b9080f5f4c.jpg)

我们获取运行时内核扩展信息，看看有没有与 AppleVXD393 相关的内核扩展，结果如下：

![enter image description here](http://drops.javaweb.org/uploads/images/6b8c6b6bc132269b0e73f9ef841d4b56e1b819bb.jpg)

可以看到我们找到了相关的内核扩展。

由于目前已经可以解密较新的 armv7 的内核，查看相关的内核没有发现这个内核扩展，且在 iOS 7.x 的 armv7 设备上测试播放视频，内核并没有崩溃。综合相关信息，这个问题可能只影响 arm64 设备。

0x04 确定用户空间中调用 AppleVXD393 服务的模块
================================

* * *

首先需要确定这个内核扩展是不是在沙盒内使用的，经过测试发现：这个内核扩展不是在沙盒中调用的，下面就需要确定具体是哪个模块在使用这个服务。 因为调用内核扩展的服务时，需要根据服务名称来获取服务，于是在 grep 了下 iOS 8.0.2 的系统库，得到如下信息：

```
grep -r "AppleVXD393" _cached-dyld/v8.0.2/libraries-arm64
Binary file MediaToolbox.framework/MediaToolbox matches
Binary file VideoToolbox.framework/VideoToolbox matches
Binary file VideoDecoders/MP4VH6.videodecoder matches

```

由于播放 mp4 引起的崩溃，所以 MP4VH6.videodecoder 让我们更感兴趣，grep MP4VH6 得到的信息如下：

```
grep -r "MP4VH6" _cached-dyld/v8.0.2/libraries-arm64 
Binary file VideoToolbox.framework/VideoToolbox matches
Binary file VideoDecoders/MP4VH6.videodecoder matches

```

结合对 VideoToolBox 的反汇编分析，可以知道 VideoToolBox 利用 MP4VH6.videodecoder 来做 MP4 解码，将 MP4VH6.videodecoder 拖到 IDA Pro 中，查看导出表：

![enter image description here](http://drops.javaweb.org/uploads/images/beb35a5a50b3435e3b506bc994e95576a7f75c25.jpg)

可以看到与 AppleVXD393 相关的函数，MP4VH6.videodecoder 应该封装了内核扩展 com.apple.driver.AppleVXD393 的用户空间接口。

0x05 确定视频解码服务
=============

* * *

通过上面的分析我们已经知道：1、MP4VH6.videodecoder 封装了视频解码服务的用户空间接口；2、VideoToolBox.framework 直接调用了 MP4VH6.videodecoder。接下来我们需要知道哪个后台进程通过 xpc 对外提供视频解码服务，ps + grep：

```
ps aux |grep media
mobile     214   MusicLibrary.framework/Support/medialibraryd
mobile     119   /usr/sbin/mediaserverd
mobile     117   MediaRemote.framework/Support/mediaremoted

```

由于 xpc 服务都需要checkin，逆向分析这三个程序，最后发现 mediaserverd checkin 了如下两个服务：

```
com.apple.mediaserverd
com.apple.audio.SystemSounds

```

mediaserverd 可能是我们要找的后台服务。为了确定这一点，又调试了下 mediaserverd，断点命中后，得到信息如下：

```
(lldb) x/s $x0
0x19368065f: "AppleVXD393"
(lldb) bt
* thread #16: tid = 0x21cb, IOKit`IOServiceMatching
  * frame #0:  IOKit`IOServiceMatching
    frame #1: H264H6.videodecoder`AppleVXD393CheckPlatform + 60
    frame #2: H264H6.videodecoder`H264H6Register + 16
    frame #3: VideoToolbox`VTLoadVideoDecoders + 168
    frame #4: libsystem_pthread.dylib`__pthread_once_handler + 80
    frame #5: libsystem_platform.dylib`_os_once + 56
    frame #6: libsystem_pthread.dylib`pthread_once + 76
    frame #7: VideoToolbox`VTSelectAndCreateVideoDecoderInstanceInternal + 136
    frame #8: VideoToolbox`VTSelectAndCreateVideoDecoderInstance + 44
    frame #9: MediaToolbox`FPSupport_GetDefaultTrackIDForMediaType + 428
    frame #10: MediaToolbox`itemfig_setBasicInspectables + 808
    frame #11: MediaToolbox`itemfig_retrieveAssetBasicsIfReady + 276
    frame #12: MediaToolbox`itemfig_assetPropertyLoaded + 324

```

至此确定 mediaserverd 负责提供视频解码服务，也可以大概知道 iOS 平台的视频解码功能的大致架构。

0x06 分析可控性
==========

* * *

首先看下视频解码时的调用栈：

```
(lldb) bt
* thread #19: tid = 0x2020,  IOKit`IOConnectCallMethod
  * frame #0: IOKit`IOConnectCallMethod
    frame #1: IOKit`IOConnectCallStructMethod + 52
    frame #2: MP4VH6.videodecoder`AppleVXD393DecodeFrameInternal + 428
    frame #3: MP4VH6.videodecoder`AppleVXD393DecodeFrame + 1264
    frame #4: MP4VH6.videodecoder`AppleVXD393WrapperMPEG4DecoderDecodeFrame + 728
    frame #5: VideoToolbox`vtDecompressionDuctDecodeSingleFrame + 348
    frame #6: VideoToolbox`VTDecompressionSessionDecodeFrame + 440
    frame #7: MediaToolbox`vmc2DecodeUntilHighWaterMet + 3308
    frame #8: MediaToolbox`activitySchedulerOnThread + 72
    frame #9: CoreMedia`figThreadMain + 248
    frame #10: libsystem_pthread.dylib`_pthread_body + 164
    frame #11: libsystem_pthread.dylib`_pthread_start + 160

```

为了确定可控性，于是编写了一个 Tweak 来 Hook mediaserverd，并 Hook IOConnectCallStructMethod，在发现待解码的视频帧序号与引起内核崩溃的视频帧序号一致时，修改交由内核解码的数据，查看、对比崩溃日志，总结输入对崩溃时寄存器值的影响。 对缓冲区一共进行如下几个填充测试：

![enter code here](http://drops.javaweb.org/uploads/images/440a45e239399b4fc42750f302db89de6b3b71ab.jpg)

缓冲区填充测试，0x00 vs. 0x01：

![enter image description here](http://drops.javaweb.org/uploads/images/b9de58497e56e701c01c91b5abed19492fb42ca7.jpg)

可以看到 PC 寄存器有差别，说明走的不是相同的代码路径。在对缓冲填充 0x01 时，内核的崩溃点为：

![enter image description here](http://drops.javaweb.org/uploads/images/c61e43be3bb8aef8e83424c9f18eafa8aff3d77a.jpg)

缓冲区填充测试，0x01 vs. 0x02：

![enter image description here](http://drops.javaweb.org/uploads/images/c7f887b85bbc115ea6d4ec4c5d001d92c1066d66.jpg)

可以看到 x0 的部分位是可控的，x12, x13 是从 x1 指向的地址处加载的。至此已经完成了对问题的分析，至于利用，就大家各显神通吧。

0x07 其他
=======

* * *

一、经过处理的只包含单帧的视频，

链接：http://yunpan.cn/cc5KWG7p368yN

提取码：4e17

MD5：f4260553b0628f2e6bbb88e2c7b124e6

二、如果大家有利用思路，欢迎关注微博交流：@NirvanTeam

此外，对iOS安全领域开发、漏洞分析、挖掘感兴趣的同学可以关注微博@NirvanTeam私信或者发邮件到nirvanteam@360.cn联系我们。