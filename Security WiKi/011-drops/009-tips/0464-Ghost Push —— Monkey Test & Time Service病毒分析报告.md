# Ghost Push —— Monkey Test & Time Service病毒分析报告

2015年8月，酷派大神手机用户在安装官方提供的系统升级包后，手机便被预安装了MonkeyTest和TimeService等未知软件。截止到9月18日，该类病毒的每日感染量已经扩大到了最高70万台/天，有上万种机型收到了Ghost Push的影响，典型的有酷派、三星、MOTO等等（附件一提供了所有受影响机型列表）。

通过数据分析如图1所示，我们发现Ghost Push病毒感染用户主要分布于美国、俄罗斯、印度、中国等。相对在中国而言，云南、广东感染量最高。

![](http://drops.javaweb.org/uploads/images/fbe40ee3d849a748aaa1e057e207cc95afc7fd07.jpg)

图1 感染分布图

我们称这类病毒为Ghost Push病毒。该类病毒软件开机自动运行，通过用户数据流量进行广告推送，并且在未经过用户允许的情况下静默下载安装应用。甚至用户无法通过手机杀毒软件、手动卸载该类病毒。手机感染之后如图2所示。

![](http://drops.javaweb.org/uploads/images/1f94b4ea917739dabd12b21ccf004a3390247930.jpg)

图2 感染Ghost Push病毒的手机举例

Ghost Push病毒已经给安卓用户造成了巨大的困扰。本文就Ghost Push的执行流程进行详细的分析，同时也提出了针对这类病毒的解决方案及安全建议。

Ghost Push病毒在执行的过程当中，会获取Root权限，通过用户数据流量进行广告推送、静默下载安装应用。具体的流程如图3所示。

![](http://drops.javaweb.org/uploads/images/f58e8acb2e29279146321795ff08af323cd41079.jpg)

图3 Ghost Push病毒执行流程

首先，攻击者将恶意代码注入到合法的应用当中，通过二次打包，伪装成为原本的合法应用(被感染的应用列表如附件二所示)。一旦用户下载了被注入恶意代码的“正常”应用，应用中的恶意代码便开始执行，具体执行过程如下。

0x01 病毒释放安装流程分析
===============

* * *

**1.1 获取Root权限**

恶意代码首先向服务器http://api.aedxdrcb.com/ggview/rsddateindex发送手机的型号等配置信息。随后从服务器端获取Root工具包http://down.upgamecdn.com/onekeysdk/tr_new/rt_0915_130.apk。该Root工具包利用手机存在的漏洞，获取手机的Root权限。目前可以适配上万种机型，成功执行Root提权操作。

本文列出了针对三星、MTK两家厂商的Root执行代码，如图4.a和图4.b所示。

![](http://drops.javaweb.org/uploads/images/1093927d987911d13e9e11247d6b6cead70bace1.jpg)

图4.a 三星ROOT方案

![](http://drops.javaweb.org/uploads/images/8e0b58e00ed4d3ac04b666ab142ff2f9e89f1909.jpg)

图4.b MTK ROOT方案

在获取了Root权限之后，恶意代码执行四类操作：1）替换debuggerd文件；2）修改install-recovery.sh文件；3)释放恶意bin文件；4）安装ROM病毒。

**1.2 替换debuggerd文件**

病毒会将原系统的debuggerd文件另存为debuggerd-test文件，并将自己的恶意bin文件保存为系统的debuggerd文件，如图5所示。

![](http://drops.javaweb.org/uploads/images/7d785345fcf422c7343461c81b249f436c3c5450.jpg)

图5 替换debuggerd文件

**1.3 修改install-recovery.sh文件**

病毒修改系统的install-recovery.sh文件，如图6所示。

![](http://drops.javaweb.org/uploads/images/04b33b259a79485a3c3e06508f1e8b96a07aba72.jpg)

图6 修改install-recovery.sh文件

**1.4 释放恶意bin文件**

病毒将恶意bin文件的二进制代码固定内嵌在Java代码中，并在执行的过程中，向/system/xbin目录下释放。

![](http://drops.javaweb.org/uploads/images/2a552aea5273fe974c4add5c394e46fb15646b77.jpg)

图7 释放bin文件

**1.5 安装ROM病毒**

在恶意代码执行的过程中，会向系统目录/system/priv-app或/system/app中写入如camera_update应用的病毒母体，如图8所示。

![](http://drops.javaweb.org/uploads/images/09b29fafd559312e76c3e850c6a07e95adb75c7f.jpg)

图8 释放病毒母体

由于获得了Root权限，恶意代码首先检查/system/priv-app目录下是否安装了camera_update病毒母体。该病毒母体会在bin文件的守护下，一直存在在手机的ROM中，防止被卸载，详见第二节分析。

病毒母体在安装完毕后，会静默安装Time Service、Monkey Test等应用。这些应用会通过短连接方式从服务器（Monkey Test对应服务器：http://massla.hdyfhpoi.com/gkview/info/801； Time Service对应服务器：http://u.syllyq1n.com/mmslow/api/821。）获取应用信息，在未经过用户允许的情况下进行下载安装，如图9、图10所示。

![](http://drops.javaweb.org/uploads/images/7f6ebad0ff5fa9ec3ee2d2c52746937e0073cba3.jpg)

图9 Monkey Test子包从服务器获取应用信息

![](http://drops.javaweb.org/uploads/images/b4b6087b604b48bc29fda71b741116dbefb681bc.jpg)

图10 在用户未知的情况下在ROM内安装应用

0x02 病毒母体守护流程分析（图3中蓝色部分所示）
==========================

* * *

**2.1 bin文件守护ROM病毒母体**

在系统启动时，会执行install-recovery.sh与debuggerd文件。这两个文件会执行释放的恶意bin文件。bin文件会一直保持运行状态，守护释放在ROM中的病毒母体。并从服务器获取最新病毒安装包。

![](http://drops.javaweb.org/uploads/images/0ab513568a949871f86762badfab7bcff6164f98.jpg)

图11 获取最新病毒包

当病毒母体被删除后，bin文件会自动再次下载并向ROM中安装病毒母体，如图12所示。

![](http://drops.javaweb.org/uploads/images/168f0f37e1e30e3f6cf6f183ae1690040ccddde1.jpg)

图12 病毒母体守护流程

![](http://drops.javaweb.org/uploads/images/d1db4ad5d46d89bf13b12e50166137009eade4fa.jpg)

图13 病毒母体安装流程

**2.2 bin文件防删除**

同时，在手机运行的过程中，通过图14所示的chattr +i操作，使得用户无法删除恶意bin文件。

![](http://drops.javaweb.org/uploads/images/420b26ed2816fcd4fe2489a9926bd51f631945c6.jpg)

图14 通过chattr +i操作防止用户删除bin文件

**2.3 apk防卸载**

Ghost Push病毒通过chattr + i操作使得用户无法卸载已经安装的apk应用，如图15所示

![](http://drops.javaweb.org/uploads/images/698eb14f326abb4d76f05d06cd1f2c398d7c7990.jpg)

图15 通过chattr + i操作防止用户卸载apk

0x03 病毒恶意行为分析
=============

* * *

Ghost Push病毒安装的应用软件均具有数据流量广告推送、静默安装应用软件两种恶意行为。

**3.1 广告推送**

通过Ghost Push病毒安装、释放在用户手机上的应用，会通过手机数据流量向用户推送广告。具体流程如图16所示。当用户开启屏幕时，便会触发展示推送广告推送。

![](http://drops.javaweb.org/uploads/images/f0a676e4f44b9a2f0b36539ff6a0ad33c4be1665.jpg)

图16 开启屏幕触发广告推送

值得注意的是，Ghost Push病毒在推送广告的过程中，会首先关掉用户手机的WiFi连接，通过用户的手机流量来获取需要推送的广告内容，如图15中红色方框内容所示。在用户不知情、未得到允许的情况下盗用了大量的数据流量。

**3.2 应用推送**

Ghost Push病毒母体释放的Time Service、Monkey Test子包还会向用户推送应用并安装，如图17所示。病毒从http://m.AEDXDRCB.COM/gcview/api/910获取需要推广的应用。

![](http://drops.javaweb.org/uploads/images/d13019b7ff502302c3e65edd8c445b6d4872ca04.jpg)

图17获取需要推广的应用

返回的结果有不同的推广类型， 比如直接后台下载，快捷图标，弹通知栏等方式。如图18所示。

![](http://drops.javaweb.org/uploads/images/f7640f602aa35b34609ab06f7fae6db30182537b.jpg)

图18获取需要推广应用请求返回

比如以下返回直接后台下载的推广应用。病毒会在在后台下载完成后自动安装，如图19所示。

![](http://drops.javaweb.org/uploads/images/3c206ab860b7abf72d81f3437b9c9bdb825e2a1a.jpg)

图19 后台安装应用

Ghost Push病毒中各种推广任务，会使用sqllite数据库作为中转，如图20所示。

![](http://drops.javaweb.org/uploads/images/024fa98d5381531fa8a19bcee3ef7b95a1aac814.jpg)

图20 sqllite中转推广任务

在实际我们测试中, 可以看到以下的推广数据，如图21-24所示。

![](http://drops.javaweb.org/uploads/images/77e72292f5acf370f11562c4126ffcf684618095.jpg)

图21 后台推送应用日志文件

![](http://drops.javaweb.org/uploads/images/e4d87f8464444b1535a2707983b25f88faa37bf2.jpg)

图22 安装应用

![](http://drops.javaweb.org/uploads/images/a038fa8c873f14a8bc208f7e47c8a24ec99ae994.jpg)

图23 推送应用提醒用户安装

![](http://drops.javaweb.org/uploads/images/af8459c735a2b1138699576ce484cf17a32772c6.jpg)

图24 推送安装应用列表（测试机已装）

**3.3无Root静默安装**

为了进一步地保证成功地安装下载应用，病毒还会诱导用户开启辅助功能，如图24所示。之后如图25所示的代码，病毒通过辅助功能，模拟用户点击操作来成功地安装应用。并且图25左侧文件列表也显示出其可以适配不同系统市场（GooglePlayer、Lenovo、MIUI等）的安装方式。

![](http://drops.javaweb.org/uploads/images/672262250be2c09746546e72b5734bed4e53ccbe.jpg)

图24 开启辅助功能

![](http://drops.javaweb.org/uploads/images/5670a0d028c63a5903cde2282d2ffbd1da24867a.jpg)

图25 通过辅助功能静默安装

0x04 解决方案与安全建议
==============

* * *

**4.1 解决方案**

用户可以选择使用猎豹专杀工具[https://play.google.com/store/apps/details?id=com.cleanmaster.security.stubborntrjkiller](https://play.google.com/store/apps/details?id=com.cleanmaster.security.stubborntrjkiller)（即将更新上线）或手动删除病毒软件。手动删除方法如下：

1.  使用刷机软件，一键获取ROOT权限。
2.  下载安装adb工具，[http://developer.android.com/tools/help/adb.html](http://developer.android.com/tools/help/adb.html)。
3.  下载安装busybox工具，[http://www.busybox.net/](http://www.busybox.net/)。
4.  在电脑端，通过adb shell连接手机，使用su命令获取ROOT权限。
5.  ps | grep .base #获取.base文件的pid`kill pid`
6.  删除恶意bin文件
    
    ```
    mount -o remount rw /system  #不同系统命令可能不同
    chattr –ia /system/xbin/.ext.base
    chattr –ia /system/xbin/.bat.base
    chattr –ia /system/xbin/.zip.base
    chattr –ia /system/xbin/.word.base
    chattr –ia /system/xbin/.look.base
    chattr –ia /system/xbin/.like.base
    chattr –ia /system/xbin/.view.base
    chattr –ia /system/xbin/.must.base
    chattr –ia /system/xbin/.team.base
    chattr –ia /system/xbin/.type.base
    chattr –ia /system/xbin/.b
    chattr –ia /system/xbin/.sys.apk
    chattr –ia /system/xbin/.df
    chattr –ia /system/bin/daemonuis 
    chattr –ia /system/bin/uis
    chattr –ia /system/bin/debuggerd
    chattr –ia /system/bin/nis
    chattr –ia /system/bin/daemonnis
    chattr –ia /system/bin/.daemon/nis
    chattr –ia /system/bin/uis
    chattr –ia /system/bin/.sr/nis
    chattr –ia /system/bin/mis
    chattr –ia /system/bin/daemonmis
    chattr –ia /system/bin/.daemon/mis
    chattr –ia /system/bin/.sc/mis        
    
    rm /system/xbin/.ext.base
    rm /system/xbin/.bat.base
    rm /system/xbin/.zip.base
    rm /system/xbin/.word.base
    rm /system/xbin/.look.base
    rm /system/xbin/.like.base
    rm /system/xbin/.view.base
    rm /system/xbin/.must.base
    rm /system/xbin/.team.base
    rm /system/xbin/.type.base
    rm /system/xbin/.b
    rm /system/xbin/.sys.apk
    rm /system/xbin/.df
    rm /system/bin/daemonuis 
    rm /system/bin/uis
    rm /system/bin/debuggerd
    rm /system/bin/nis
    rm /system/bin/daemonnis
    rm /system/bin/.daemon/nis
    rm /system/bin/uis
    rm /system/bin/.sr/nis
    rm /system/bin/mis
    rm /system/bin/daemonmis
    rm /system/bin/.daemon/mis
    rm /system/bin/.sc/mis
    cp /system/bin/debuggerd_test /system/bin/debuggerd
    
    ```
7.  使用猎豹安全大师清除恶意软件，无法清除的软件使用以下命令清除。
    
    ```
    chattr –ia /system/priv-app/cameraupdate.apk
    chattr –ia /system/priv-app/com.android.wp.net.log.apk
    rm -rf /data/data/com.android.camera.update
    rm -rf /data/data/com.android.wp.net.log
    rm  /systam/priv-app/cameraupdate.apk
    rm  /systam/priv-app/com.android.wp.net.log.apk
    
    ```
8.  ```
    adb shell 
    cp /system/etc/install-revcovery.sh /sdcard/
    adb pull /sdcard/install-revcovery.sh
    adb push install-revcovery.sh /sdcard/
    cp /sdcard/install-revcovery.sh /system/etc/
    
    ```
9.  打开/system/etc/install-recovery.sh，将其中如下代码段注释或删除。
    
    ```
    /system/bin/daemonuis --auto-daemon &          
    
    #!/system/bin/sh
    /system/xbin/.ext.base &         
    
    #!/system/bin/sh
    /system/xbin/.ext.base &
    
    ```

**4.2 安全建议**

建议用户从正规应用市场下载应用，谨慎下载安装附件二中的应用。同时，安装猎豹安全大师，验证下载应用的合法性，对手机进行实时的安全监控。

0x05 总结
=======

* * *

Ghost Push病毒通过广告SDK或浏览器广告进行大范围的传播，通过对病毒的跟踪分析，得知Ghost Push这类病毒软件伪装成合法的软件。用户一旦感染，恶意代码在开机时运行install-recovery，同时通过chattr + i命令防止用户通过杀毒软件建或手动卸载。恶意代码通过用户数据流量进行广告推送，并且在未经过用户允许的情况下静默下载安装应用，给众多安卓用户带来了不可避免的影响及危害。

本文在对病毒执行流程进行分析之后，提供了用户手动清除病毒的方法。最后，我们在对病毒来源进行分析之后发现病毒软件的大部分签名为C=CN/O=xinyinhe/OU=ngsteam/CN=ngsteam，来自于一家名为xinyinhe的公司。本着刨根问题的原则，我们也在附件三中对这家xinyinhe公司进行了全面的调查。

我们建议用户从正规渠道下载应用，并且安装猎豹安全大师，保证应用的合法性，实时维护用户的手机安全。

**[附件一] 部分受感染机型列表**

![](http://drops.javaweb.org/uploads/images/6432e24ed2a0b18a5a75c7aacb3f88a5053d2de7.jpg)

**[附件二] 感染应用列表（39项）**

![](http://drops.javaweb.org/uploads/images/3e92eee8d7c48575745dd2cb366de22645a7a68a.jpg)

**[附件三] 深圳市新银河技术有限公司**

直觉告诉我们，这家新银河技术有限公司和一键ROOT大师有着千丝万缕的联系。不要问我们直觉哪里来的~~

那么到底这两家公司有没有关系呢？我们首先百度、谷歌了一下新银河的官网，结果显示这家公司没有官网。于是——

我们上了拉钩招聘发现了该公司的链接。

![](http://drops.javaweb.org/uploads/images/abee49d80885052884b476c4b94fe09c79a85cfa.jpg)

从招聘信息上我们得知`http://www.ngemob.com`和`http://root.ngemob.com`都是深圳市新银河技术有限公司的网站。

![](http://drops.javaweb.org/uploads/images/1f09a056a7dba6e5fbdd99b8c7ef621d5a0c7c29.jpg)

找到公司官网之后，真相逐渐浮出水面！！！现在的一键ROOT大师`http://www.dashi.com/`和`http://www.ngemob.com`  使用过同一ip。

![](http://drops.javaweb.org/uploads/images/865ada859952575c6202a2f08b1a93e3af2ed3ea.jpg)

![](http://drops.javaweb.org/uploads/images/5b4d03c14be8c795e1ffc304c49e0a19c3405fb6.jpg)

并且，国外的论坛上也经常出现一键ROOT大师和`http://root.ngemob.com`扯不清的关系

![](http://drops.javaweb.org/uploads/images/6d7bfac8239f04f33d5d4234929a9086324c064a.jpg)

![](http://drops.javaweb.org/uploads/images/9fac41fee0117dd6089d38b77a04d3d67b2b195d.jpg)

此外，我们还搜集了一些佐证。

佐证一：好搜百科。

![](http://drops.javaweb.org/uploads/images/20e7fac831367dbaf50cf8819757949646368e7e.jpg)

佐证二：某锁屏APP，由深圳市新银河技术有限公司开发。

![](http://drops.javaweb.org/uploads/images/5d27301aee027cd1ec6d02d083608b411934fb24.jpg)

毕竟没有官网并没有给出任何明线表示两家公司的联系。我们也是推论猜测，没有任何结论，请各位看官自行判断。

最后，希望大家一起努力，相信猎豹，会给亿万用户筑起安全防护墙！！！

病毒的清除方法视频 ：