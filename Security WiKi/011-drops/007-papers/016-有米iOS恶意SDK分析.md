# 有米iOS恶意SDK分析

0x00 前言
=======

* * *

有米广告平台为业界领先的移动信息服务提供商优蜜科技™所有，总部和研发中心设在广州，在北京设立分支机构。有米广告拥有核心技术及完整知识产权，并获多项国家专利，在用户特征识别、精准投放、客户端防作弊、广告智能投放等关键领域遥遥领先。有米广告瞄准7亿手机用户，致力于为数以万计的企业广告主提供精准的产品营销和品牌推广服务，为应用开发者创造公正和优质的广告收益。

网址是`https://www.youmi.net/`

前不久SourceDNA的研究人员发现iOS平台使用有米SDK的一些APP收集用户隐私数据，主要包括以下四类：

1.  用户安装在手机上的应用列表信息；
2.  在用户运行旧版iOS时，收集设备的平台序列号；
3.  在运行新版iOS时，收集设备的硬件组件及组件序列号；
4.  用户的Apple ID邮箱。

在跟进过程中发现，sourceDNA在自己的微博中更新了说明，对是否获取apple id做了解释

https://sourcedna.com/blog/20151018/ios-apps-using-private-apis.html

![enter image description here](http://drops.javaweb.org/uploads/images/a72469dde3376b2c53bba90e672a63a2ad72a2c1.jpg)

我们Nirvanteam也对此进行了详细的技术分析。

详细过程开始分析如下

0x01 社工获取iOS的SDK
================

* * *

目前网上不太好找这个SDK，而且有米也在努力更新SDK。

![](http://drops.javaweb.org/uploads/images/218d71b05ff6420d00137220fc259d5dd92fb80f.jpg)

最后通过社工得到 SDK。

0x02 SDK细节分析
============

* * *

拿到SDK后直接 strings不能搜索到URL的, 劫持包发现了URL然后分析发现URL都做了编码。 URL如下：

```
http://ios.wall.youmi.net  主要是这个URL在发送数据
http://stat.gw.youmi.net
http://au.youmi.net/offer/ios/offers.manifest
http://t.youmi.net

```

通过分析SDK 发现SDK通过大量的私有API。

私有API是指放在PrivateFrameworks框架中的API，苹果通常不允许App使用这类API，因为调用私有API而在审核中遭到拒绝的现象并不少见。但苹果的审核机制并不透明，许多使用了私有API的App也被审核通过，包括Google Voice这样的应用，一样调用了私有API，也获得了通过上架。甚至是苹果的预装App iBooks也被揭露使用了大量私有 API，致使第三方应用无法实现亮度控制和调用字典等类似的功能。

逆向sdk分析：

![](http://drops.javaweb.org/uploads/images/7ac9dc8b50a7c2f9f4156f554895ac2561367531.jpg)

通过分析URL 去挖掘发送的数据，sub_2DE18 函数主要获取各种信息，如下如：

1) 其中获取序列号信息代码：

```
IOServiceMatching("IOPlatformExpertDevice")
io_service_t  IOPlatformExpertDevicev_ios_service= IOServiceGetMatchingService)(
                addr_kIOMasterPortDefault,
               "IOPlatformExpertDevicev");
CFStringRef  strref = CFStringCreateWithCString(kCFAllocatorDefault, IOPlatformSerialNumber_v64, 0x600);//Creates an immutable string from a C string.    

CFTypeRef SerialNumberAsCFString = 
IORegistryEntryCreateCFProperty(platformExpert, CFSTR("IOPlatformSerialNumber"), kCFAllocatorDefault, 0) ; 
          if ( SerialNumberAsCFString )
          {
            CFTypeID typeid = CFGetTypeID(SerialNumberAsCFString);
            if ( typeid == CFStringGetTypeID() )
            {
              [NSString stringWithString:SerialNumberAsCFString];  //获得统序列号 5K152FX7A4S
            }
          }

```

2) 获得各种设备信息主要通过下面函数获取。

```
getinfo_from_devicename_and_togetdict_infosub_1EC88((DeviceName, dict_v8); 

```

传入需要获取的设备名称和字典信息来获取信息，设备名用于获取信息，字典是需要获取的信息。 函数代码如下：

```
 io_iterator_t iterator,iterator2;
            IORegistryEntryGetChildIterator(result2,"IOService", &iterator);
             io_iterator_t t = IOIteratorNext(iterator);
            char name[20];
            IORegistryEntryGetNameInPlane(result2,"IOService", name);
                if([DeviceName isEqualToString: name])
                {
               CFTypeRef data;
            IORegistryEntryCreateCFProperties_v25)(result2,
                            &data,
                            kCFAllocatorDefault,
                            0);

            if(CFGetTypeID(data) ==  CFDictionaryGetTypeID())
            {
            …………

```

例如获取设备名称如下：

*   电池 battery-id
*   摄像机 AppleH4CamIn
*   iOS加速度传感器 accelerometer
*   WIFI 信息 wlan
*   蓝牙信息 bluetooth
*   Device Characteristics TLC还是MLC内存 ASPStorage disk
*   充电次数 AppleARMPMUCharger

获取设备信息后将信息存储到`APP/Library/.XABCD/nidayue.dict`这个文件中，当需要哪些信息就从这里读取。

写这个文件是通过设置消息函数来实现的。

```
void __cdecl -[ChargerClinkeredConcertedly catalogueChoraleAlamo](struct ChargerClinkeredConcertedly *self, SEL a2)
{
  struct ChargerClinkeredConcertedly *v2; // r4@1
  void *v3; // r0@1
  void *v4; // r0@1    

  v2 = self;
  v3 = objc_msgSend(&OBJC_CLASS___NSNotificationCenter, "defaultCenter");
  objc_msgSend(
    v3,
    "addObserver:selector:name:object:",
    v2,
    "approvementAviateBefitted:",
    UIApplicationWillTerminateNotification,
    0);
  v4 = objc_msgSend(&OBJC_CLASS___NSNotificationCenter, "defaultCenter");
  objc_msgSend(
    v4,
    "addObserver:selector:name:object:",
    v2,
    "consummatingCreators:",
    UIApplicationWillResignActiveNotification,
    0);
}

```

当安装好APP 后，将要关闭APP或者按home键到后台才会去写文件信息。

![](http://drops.javaweb.org/uploads/images/267a1b2cb66110b7c672ffcdb2b51e625b5e2934.jpg)

3) 获取UUID信息

4) 广告标示符（IDFA-identifierForIdentifier）

```
ASIdentifierManager  sharedManager

```

`ASIdentifierManager`单例提供了一个方法`advertisingIdentifier`，通过调用该方法会返回一个上面提到的NSUUID实例。

```
NSString *adId = [[[ASIdentifierManager sharedManager] advertisingIdentifier] UUIDString];

```

5) 屏幕大小 960*640 获取方式

```
[[UIScreen mainScreen] bounds]
[[UIScreen mainScreen] scale]
CGRectGetHeight
CGRectGetWidth

```

6) 手机设备型号获取，如下图：

![](http://drops.javaweb.org/uploads/images/ca955e9133d2b62a1af7f70011094822adafba15.jpg)

如上函数假设参数*servicename_a1传递值为hw.machine时，返回设备硬件信息为iPhone3，1

0x03 危害分析
=========

* * *

通过分析发现SDK 获得了如下信息（测试用的iPhone4 iOS7.12）：

1.  设备的WIFI信息，
    
    ```
    BSSID = "d0:fa:1d:20:a:f8"; 这个无线AP的MAC地址
    SSID = "360WiFi-200AF8";  一个无线AP的名称。
    SSIDDATA = <33363057 6946692d 32303041 4638>;
    
    ```
2.  序列号信息IOPlatformSerialNumber 5K152FX7A4S
    
3.  电池信息 battery-id
    
4.  摄像机信息
    
5.  iOS加速度传感器 low-temp-accel-offset
    
6.  蓝牙信息 wifi-module-sn
    
7.  Device Characteristics TLC还是MLC内存
    
8.  UUID 信息 a2ab842508133b62b680b5f9efa1cd51
9.  充电次数 CycleCount
10.  广告标示符（`IDFA-identifierForIdentifier`）`112fb7fe79fb4b7abf7a8e2ecaf57147`
11.  __UDID信息`7a32771c3adf2ad0564c3cb2d6920bc6ef9818b7`
12.  屏幕大小 960*640
13.  手机设备型号 iPhone3,1
14.  通过检查进程名, 安装的APP BundleID表 , 进程模块中有没有 iGrimace,org.ioshack.iGrimace等来检查越狱状态，越狱或者未越狱。
15.  设备名称信息如`D. vice:iPhone3,1 Jailbreak:1 OS:iPhone OS Version:7.1.2 Name:“panda”的 iPhone Model:iPhone`

获得这些信息后通过 deflate 压缩，再通过一次混合加密发送出去。加密过程如下图：

![](http://drops.javaweb.org/uploads/images/6a1ab0ab934a2573154f56b55eb378da935bf991.jpg)

经过加密后将数据整合到URL上，发后通过POST方式发送出去。

发送加密如下

```
NSURLConnection_start { 
cookie = "";
data = "";
host = "ios.wall.youmi.net";
method = GET;
mime = "";
url = "http://ios.wall.youmi.net/v3/reqf?s=1,5,8aa2a777452acf72,lyOU,1,bfDG9lgEuEfsVbWHLjyNZ-ESDTPXoRHqPZvukpsNiA9esOWBJTHnmelJwR4Mzd-tYlsbO1ROsjJAYN35ngXjNvMqdtMKUu2czR4hRqws3pU2UGYPMY6Z2Z-XGzxqhb9o1gJmB2cNMfczHb4Lu8ji7e5gOu-VQjLZiXCHEnMdls-OOyb5e2wtU-wsQtK.Q0v6S692Tr-Qp8k-YcYMJ47vqcsnCJJdzehyw4W-uee7pHmmJJU1.jxMeHEKT4BpL8flP338p3HPN5Zx5DoAzEmNRdlvPui7LZiHyOxL0r8adyZyJDkfAn8qE6PDBWmK1MUQ1jWa6ghwR4bPVQmrCMZcq6a1RUZzTJVKMQOokMswhs.JdRBIZMyyUrBuRf1IcHECc.Rj1jL1IdiwTdZaDLAzcLiKDMK3Pn222K160LVqG6XhnAzmw6gs.9.0yc.kZmbsUKZ7MZ5dCliJY8Izkk9A2SGpLI4zQ5MML5XPnobSVHlVQQ4tN4khqvAXVAJwLK91YdxrhFae1fNoi5BaCpj7fSnzRjF1j46Lygnv4DgT890oljclyzBgxbxBFrwuqV8tc1VpGqMvnX6sDlGVonzGOQnd9Yjwm3d3CE3PYwCSC1jafsTlw8AhwsyZ6E5gKqio4B-JlLavdFZF4xPfP4YeQngzZRAijN3QUXYT7ZVB5f5C9NdrDdrnmZTLx5B7jChaUbdI5sTs4zNXgaGUzFYOxmgxlxdxZGN6TSUMUS7k9SEygV0tAI-uARcuF1MSE.o76aoRR1JmtSPDSI7yPL1ooo2-CeLEOhQCzcgNrrkdx.ZL6LRyWkyOXcGISiaWKWFh0BAtzv2mFhBvArj7d1MsKMY57suR58v8rugnnEeFBtfNDKK7lQrZAKKfm7iGv-xmJ4f3DFtqo4OYOE0.Q8uSQblgnK24F3-x&p=1&n=100&nshw=1";
}

```

加密信息解密如下：

```
{
    3gst = "";
    acc = "0.000000,0.000000,0.000000";
    accos = 1000010000000000c4bc1300612003004e260900;
    aicid = 47a903bcec614984acd1d0f88039d34a;
    apn = None;
    av = "1.0";
    batsn = ae15041460753d1420;
    bcsn = "";
    bsi = "";
    bssid = ec26cad6e5a;
    btsn = "";
    cc = CN;
    chn = 0;
    chrcy = "";
    cid = "eIyoH-ZvBqO_f";
    cn = 2;
    dd = "Device:iPhone3,1  Jailbreak:1  OS:iPhone OS  Version:7.1.2  Name:\U201cpanda\U201d\U7684 iPhone  Model:iPhone";
    ddn = "\U201cpanda\U201d\U7684 iPhone";
    ext =     {
        attr = 195;
        it = 1;
        nshw = 1;
        reqt = 0;
        rtype = 1;
        sat = 3;
        wat = 3;
    };
    fcsn = "";
    gyo = "0.000000,0.000000,0.000000";
    hv = 2;
    ifa = 112fb7fe79fb4b7abf7a8e2ecaf57147;
    ifat = 1;
    ifst = 3155986;
    ise = 0;
    jb = 1;
    kernid = a2ab842508133b62b680b5f9efa1cd51;
    lat = "0.00";
    lc = "zh-Hans";
    lon = "0.00";
    mac = "";
    mcc = "";
    mmcid = "";
    mnc = "";
    mod = iPhone;
    odfa = "";
    oifa = 112fb7fe79fb4b7abf7a8e2ecaf57147;
    osv = "7.1.2";
    pd = 3;
    pn = "feng.YouMiWallSample";
    po = "iPhone OS";
    rb = "-1.000000";
    rt = 1445444547;
    sh = 960;
    smv = 1;
    sn = 5K152FX7A4S;
    spc = "";
    ssid = "TP-LINK_2510";
    sv = "5.3.0";
    sw = 640;
    tid = 005ecs1rcn0k1dltd0o8dngsruf;
    ts = 0;
    udid = 7a32771c3adf2ad0564c3cb2d6920bc6ef9818b7;
    usb = 2;
    user = "this is user";
    vpn = 0;
    wifisn = "";
}

```

0x04 结果及总结
==========

* * *

通过对大量样本扫描发现，共计扫描出了1035个苹果APP受到感染。 具体对应版本信息见另一份文档

1）有米SDK主要用于统计设备类型的使用情况，这样来对市场形势作出判断来获取利益。

2）私有API如果通过静态扫描的话意思不大，一般能通过苹果审核的，私有API都是经过处理的，所以检查私有API要通过动态HOOK的方式去检查。

3）一般有使用私有API的一般都是启动的阶段，所以动态扫描APP运行阶段做成自动化也是可行的。

附件：[有米iOS恶意SDK感染列表](http://static.wooyun.org//drops/20151028/2015102817051294531%E6%9C%89%E7%B1%B3iOS%E6%81%B6%E6%84%8FSDK%E6%84%9F%E6%9F%93%E5%88%97%E8%A1%A8.pdf)