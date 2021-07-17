# 细数Android系统那些DOS漏洞

0x00 前言
=======

* * *

Android系统存在一些漏洞可导致系统重启，当然让系统重启只是一种现象，这些漏洞有的还可以权限提升、执行代码等。本文以重启这个现象为分类依据，牵强的把这些漏洞放在一块来看。下面对这些漏洞的成因和本质进行简单的分析，并尽量附上编译好的poc和漏洞利用演示视频。

0x01 Nexus 5 <=4.4.2 本地dos
==========================

* * *

https://labs.mwrinfosecurity.com/advisories/2014/11/05/nexus-5-4-4-2-local-dos/ 漏洞概述：

Nexus 5预装了一个隐藏的用来测试网络连通性的系统应用。在4.4.3之前的版本里，这个应用里有大量导出的activity，这些 activity不需要任何权限就可以被外部调用。其中一个导出的activity可以使手机遭受DOS攻击，外部调用就可以让手机直接重启。

漏洞危害：
-----

除了调用这个组件使系统重启外，如果一个恶意应用注册响应BOOT_COMPLETED广播，并且发送合适的intent给漏洞activity组件，那么手机将会循环重启。

漏洞详情：
-----

存在漏洞的应用包：com.lge.SprintHiddenMenu

存在漏洞的组件： com.lge.SprintHiddenMenu.sprintspec.SCRTN，该组件是导出的，并且没有做任何权限限制。 通过如下命令即可使Nexus 5手机重启:

```
adb shell am start –n com.lge.SprintHiddenMenu/com.lge.SprintHiddenMenu.sprintspec.SCRTN 

```

漏洞修复：
-----

4.4.3及以上系统中对这个组件做了权限限制，只有应用申请了com.lge.permission.SPRINTHIDDEN这个权限才能调起com.lge.SprintHiddenMenu.sprintspec.SCRTN组件。

0x02 异常的AndroidManifest.xml引起的dos:
==================================

* * *

http://blog.trendmicro.com/trendlabs-security-intelligence/malformed-androidmanifest-xml-in-apps-can-crash-mobile-devices/

两种方法:

strings.xml文件中一些tag(如permission name,label,activity name)如果包含超长字符串，当Package Parser去解析这个.XML文件时需要申请大量内存，导致内存溢出，PackageParser crash。所有依赖PackageParser运行的服务都会停止，导致系统也会重启一次。

下面是编译好的一个poc应用，这个应用没有申请任何权限，也无恶意代码，只是在strings.xml的label tag中使用了超长字符串。装上之后运行就可使系统重启。

云盘下载地址：

http://yunpan.cn/cZK5pQRasVrAr （提取码：f256）

如果一个apk文件里大量activity或者service包含下面特定的intent-filter，那么应用安装后会生成相同数量的icon.如果这样的activity或service的数量超过10000，系统就会重启，如果超过100000，设备会循环重启。

```
<intent-filter>
<action android:name="android.intent.action.MAIN" />
<category android:name="android.intent.category.LAUNCHER" />
</intent-filter>

```

0x03 Nexus 6异常重启
================

* * *

运行如下命令即可导致nexus6异常重启。

```
$ adb shell cat /d/pc_debug_counter 

```

具体原因不详，Twitter上有人讲是因为arch/arm/mach-msm/msm-pm.c内核驱动文件里msm_pc_debug_counters_copy()里调用的scnprintf()函数引起的。

![enter image description here](http://drops.javaweb.org/uploads/images/a28583e53b991f28fe65cbbfeb7276bf8fe1da31.jpg)

scnprintf() API说明见[1](http://drops.wooyun.org/wp-content/uploads/2015/03/image0018.png)。作用是格式化一个字符串并把它放在buffer里，返回值是写进buffer的字符数量。

在网上找到这个文件的两个版本，旧版本[2](http://drops.wooyun.org/wp-content/uploads/2015/03/image0037.png)如下：

![enter image description here](http://drops.javaweb.org/uploads/images/52e1f6914bb89420f1a2e6224f8a36631e184368.jpg)

漏洞可能是因为MSM_PC_NUM_COUNTERS 值等于4，而counter_name长度为3，循环中j最大取值为3，数组下标越界，counter_name[j]取不到值导致的。

新的版本[3](http://drops.wooyun.org/wp-content/uploads/2015/03/image0055.png)如下，发现新文件在循环中做了处理。

![enter image description here](http://drops.javaweb.org/uploads/images/38145a31979b6aca7334968ed8c84c8e069d75db.jpg)

0x04 CVE-2014-7911
==================

* * *

http://seclists.org/fulldisclosure/2014/Nov/51

漏洞概述：
-----

Android < 5.0, java.io.ObjectInputStream 没有校验被反序列化的对象是否合法.

漏洞详情：
-----

java.io.ObjectInputStream不校验被反序列化的对象的真实性，这就意味着攻击者可以构造一个任意的序列化对象，这个对象的属性值可以由攻击者指定。然而这个恶意对象是无用的，最终会被GC回收，GC会调用对象的finalize方法。

Android里system_service是以root权限运行的，其他应用都可以通过Intent的方式和其通信，可以传递一个Bundle对象给Intent，而Bundle里可以放一个序列化对象，其他应用都可以以这种方式攻击system_service。

android.os.BinderProxy类包含一个finalize方法，这个方法最终会调用native层的android_os_BinderProxy_destroy()[4](http://drops.wooyun.org/wp-content/uploads/2015/03/image0076.png)这个方法，可以看到这个方法里会使用序列化对象里的两个字段值，并把这两个值传给了指针。

![enter image description here](http://drops.javaweb.org/uploads/images/9cf62050a3873fc529db78b0bfcbca2c9ea646e6.jpg)

如果攻击者可以在system_server 的已知内存地址插入数据，那么就可以执行任意代码。 Android有做地址空间随机化ASLR，但是所有的app都是fork自zygote进程，他们都有相同的基本内存布局，因此是可以绕过system_server的ASLR.

漏洞利用：
-----

poc伪造了一个AAdroid.os.BinderProxy类对象，传递给system_server的jvm后触发了GC回收，但是把其当成了android.os.BinderProxy,触发了android_os_BinderProxy_destroy函数，获得代码执行。

编译好的poc：http://yunpan.cn/cZK5NuMJspXAc（提取码：5962）

漏洞演示视频：http://v.youku.com/v_show/id_XOTE0MDgxODE2.html

0x05 CVE-2015-1474
==================

* * *

http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-1474

漏洞概述：
-----

Google Android platform/frameworks/native/libs/ui/GraphicBuffer.cpp中的GraphicBuffer::unflatten函数存在整数溢出错误，攻击者通过传递超长文件描述符或整数值，可使应用程序崩溃或执行任意代码。 

受影响系统：
------

Google Android 5.0

漏洞危害：
-----

远程攻击者利用漏洞可使应用程序拒绝服务或执行任意代码。

漏洞利用：
-----

利用和CVE-2014-7911一样，攻击system_service。

漏洞修复：
-----

Google已经发布patch，对numFds 和numInts的最大值进行了判断和限制。

修复前：
----

https://android.googlesource.com/platform/frameworks/native/+/4aaa39358f538d8e06e026385bb8be8088d78c35/libs/ui/GraphicBuffer.cpp

![enter image description here](http://drops.javaweb.org/uploads/images/72466a555dfd6e521ff8b4161713f9b80aa52b77.jpg)

修复后：

https://android.googlesource.com/platform/frameworks/native/+/38803268570f90e97452cd9a30ac831661829091/libs/ui/GraphicBuffer.cpp

![enter image description here](http://drops.javaweb.org/uploads/images/00b643eaae64795cabb12252a5251a211f2a884e.jpg)

如果有兴趣，读者也可以自行编译AOSP代码进行patch,可以使用下面这个教程。 https://gist.github.com/Fuzion24/068fe36bb5b762367921

0x06 CVE-2014-0997 Android wifi直连dos漏洞
======================================

* * *

漏洞概述：
-----

一些Android设备，通过Wifi直连功能搜索可直连的设备过程，可以被DOS攻击。攻击者发送一个精心构造的802.11协议的探测响应帧，存在漏洞的设备在收到这个响应帧后不能正确处理畸形数据，导致系统重启。

漏洞影响的设备：

```
Nexus 5 - Android 4.4.4 
Nexus 4 - Android 4.4.4 
LG D806 - Android 4.2.2 
Samsung SM-T310 - Android 4.2.2 
Motorola RAZR HD-Android4.1.2 

```

其他设备也可能受影响。

漏洞细节：
-----

Android使用了修改过的wpa_supplicant来提供无线驱动和Android platform framework之间的通讯接口。关于wpa_supplicant请参考：http://w1.fi/wpa_supplicant/

下面的函数用来处理wpa_supplicant events。这个函数最后通过调用NewStringUTF方法来返回一个jstring。 https://gitorious.org/android-eeepc/base/source/a0332f171e7413f79f156e8685d1147d89bfc5ca:core/jni/android_net_wifi_Wifi.cpp#L127

![enter image description here](http://drops.javaweb.org/uploads/images/8fc129850ee3d05d13cff8ac7362ce25db25970a.jpg)

WiFi_Direct 规范里定义了P2P的发现过程，使得P2P设备间可以互相交换设备信息，device name是设备信息的一部分。 WifiP2pDevice类位于/wifi/java/android/net/wifi/p2p/WifiP2pDevice.java[5](http://drops.wooyun.org/wp-content/uploads/2015/03/image0095.png)文件，它的对象可以表示一个Wi-Fi p2p设备。代码如下，可以看到它的构造函数是通过wpa_supplicant返回的string来初始化的，也就是刚才提到的android_net_wifi_waitForEvent()返回的值。如果这个值，也就是wpa_supplicant event是个异常值，那么就会抛出IllegalArgumentException。

![enter image description here](http://drops.javaweb.org/uploads/images/d7765645bdb7384dcf9b68cc91b3f76c9524be8c.jpg)

一些Android设备在处理探测响应帧时，如果WiFi-Direct(p2p)信息元素里包含device name属性和一些特定的字节生成的异常的supplicant event字符串,那么就会抛出IllegalArgumentException。然而WiFiMonitor这个系统进程并没有处理这个异常，导致设备重启。

Nexus 5上的部分logcat内容如下:

![enter image description here](http://drops.javaweb.org/uploads/images/6135ec0c563c7179023c505431ff56d5db3551e7.jpg)

Poc：

文件地址：http://downloads.securityfocus.com/vulnerabilities/exploits/72311.py

这个poc里使用了两个开源库Lorcon[6](http://drops.wooyun.org/wp-content/uploads/2015/03/image0114.png)和PyLorcon2[7](http://drops.wooyun.org/wp-content/uploads/2015/03/image0134.png)，其中PyLorcon2是对Lorcon的封装。

这两个库可以获取到无线网卡的信息，并且可以开启monitor模式。通过指定无线信道、源和目标信息来构造探测响应帧，最后响应给被攻击设备。被攻击设备收到畸形的响应数据，没有处理异常，导致系统重启。

下面是我们录制的漏洞演示视频:

http://v.youku.com/v_show/id_XODgwNzk2Nzk2.html

0x07.总结： 以上漏洞成因总结大致如下： (1)没有判断数据类型的边界值，导致溢出攻击 (2)传递恶意payload (3)数组下标越界 (4)权限限制不严 (5)攻击system_service

0x08 参考链接：
==========

* * *

[1](http://drops.wooyun.org/wp-content/uploads/2015/03/image0018.png)http://oss.org.cn/ossdocs/gnu_linux/kernel-api/r1980.html

[2](http://drops.wooyun.org/wp-content/uploads/2015/03/image0037.png)https://bot.bricked.de/showp1984/zarboz_m8wlv/raw/621cf6bec9f2b2fed94374c8cd949985a740dbbf/arch/arm/mach-msm/msm-pm.c

[3](http://drops.wooyun.org/wp-content/uploads/2015/03/image0055.png)https://github.com/dtsinc/DTS-Eagle-Integration_CAF-Android-kernel/blob/master/drivers/power/qcom/msm-pm.c

[4](http://drops.wooyun.org/wp-content/uploads/2015/03/image0076.png)https://code.google.com/p/android-source-browsing/source/browse/core/jni/android_util_Binder.cpp?repo=platform--frameworks--base&name=android-cts-4.2_r2

[5](http://drops.wooyun.org/wp-content/uploads/2015/03/image0095.png)https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/wifi/java/android/net/wifi/p2p/WifiP2pDevice.java

[6](http://drops.wooyun.org/wp-content/uploads/2015/03/image0114.png)https://code.google.com/p/lorcon/

[7](http://drops.wooyun.org/wp-content/uploads/2015/03/image0134.png)https://code.google.com/p/pylorcon2/