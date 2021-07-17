# 滥用Accessibility service自动安装应用

**Author:逆巴@阿里移动安全**

0x00 恶意应用简介
===========

* * *

近年许多的android市场实现免root安装应用，也就是下载完成立即自动安装，而黑产界也同样利用该技术在进行恶意推广，静默安装。最近拦截到大量恶意应用利用系统AccessibilityService静默安装应用。一旦恶意的Accessibility服务被激活，恶意应用将弹出广告，即使用户关闭弹出的广告该应用程序也会在后台下载，随后自动安装推广的恶意应用。

0x01 AccessibilityService介绍：
============================

* * *

AccessibilityService作用：

Android Accessibility用于那些由于视力、听力或其它身体原因导致不能方便使用Android智能手机的用户，Android提供了Accessibility功能和服务帮助这些用户更加简单地操作设备。开发者可以搭建自己的Accessibility服务，这可以加强应用的可用性。开启AccessibilityService后应用通过它能实时地获取当前操作应用的窗口元素信息，并能够双向交互，既能获取用户的输入，也能对窗口元素进行操作，比如点击按钮。

AccessibilityService的使用场景：

Android应用市场使用android Accessibility来免root安装应用；近来火热的抢红包应用也用使用AccessibilityService自动抢红包。

0x02 恶意应用分析
===========

* * *

我们监测到一款名为“WiFi密码查看器(增强版)”的应用滥用AccessibilityService。应用启动后诱导用户开启“WIFI信号增强服”，其实就是开启恶意应用自身的AccessibilityService；以查看WIFI密码让恶意应用获得root权限，而这一切都是为该恶意自动安装做铺垫。下图是该应用运行图

![p1](http://drops.javaweb.org/uploads/images/eec738a08c9735812c9ed6f01dbc52f00b25fd14.jpg)![p2](http://drops.javaweb.org/uploads/images/2e3637f2053efd9cf76680b821bc77c182d8859e.jpg)图应用启动与引导开启wifi信号增强界面

应用启动后会引导用户开启WIFI信号增强服务。应用跳转到ACCESSIBILITY_SETTINGS界面，提示用户若要增强Wifi信号强度，请开启WIFI信号增强服务。用户启用恶意应用的该服务之后，手机将疯狂下载该应用云端准备的应用包，并且在手机上自动安装运行。

![p3](http://drops.javaweb.org/uploads/images/32b86fe3d16e2abf61238e8f81bbdc55795e95c8.jpg)![p4](http://drops.javaweb.org/uploads/images/9093c7838d6a09033333fec268e2c86b52b6c0e3.jpg)图启动Accessibilty Service界面

以下是恶意代码运行流程

![p5](http://drops.javaweb.org/uploads/images/eb3e29ac6e923b9f9594017de3c1886397c17d6c.jpg)图恶意代码云信流程

流程图解析

1.  Wifi_list模块，恶意应用利用wifi信号增强诱导用户开启`Accessiblity Service`;查看Wifi密码诱导用户给该应用赋予Root权限。
2.  PushDownLoad模块，该模块由`PushCoreService`和`ChapingCoreService`服务组成，它们利用后台服务上传设备信息，获取待Push的应用包，下载应用包。
3.  安装模块，恶意应用解析下载成功的包，然后弹出`DialogPushActivity`的广告框，非Root利用`AccessilbityService`安装，root利用`pm install`完成静默安装
4.  daemon模块， daemon是存放在raw目录下的elf文件，它是一个守护进程，保护应用不被杀死。daemon原理是fork出子进程之后，让子进程成为新的会话的领头进程，并与其父进程的会话组和进程组脱离，紧接着就是在子进程中定时去启动java层配置的任务。这里它保证`PushCoreService`和`ChapingCoreService`一直在后台运行。

以下对核心服务`PushCoreService`跟踪分析

首先向目标服务器Post设备的imei,wifimac,SerialNumber信息，服务器返回uuid,并记录在`DefaultSharedPreference`文件的”uuid”字段

![p6](http://drops.javaweb.org/uploads/images/8ddc2ba161c0430f489c4d50adc4599514275fd2.jpg)图请求服务器获取uuid

上图最后调用`this.m_context.handler.sendEmptyMessage(1)`，启动线程GetPushThread线程。该线程向`http://api.findzhibo.com/ad/open?appCode=1&appVersion=appVerion`请求获取当前应用的“open_status”字段。只有“open_status”字段为True时，云端服务器才会继续运行，否则表示当前应用版本对应的云端关闭。开启状态向`http://api.findzhibo.com/index.php/ad/push`，发送post请求，服务器返回待push的应用，写入“cc_push_sp.xml”的push_json字段

![p7](http://drops.javaweb.org/uploads/images/32e5c8271d949f47762dd9ffaabadddf78802991.jpg)图云端恶意推广app的push_json

![p8](http://drops.javaweb.org/uploads/images/9a7b4a5048f6fc94dfdb713b7263ab358a101778.jpg)图云端请求获取恶意推广应用

上图最后调用`this.m_context.handler.sendEmptyMessage(2)`,解析push_json字段填充intent,启动`PushDownloadService`进行应用下载和恶意广告页面弹出。`PushDownloadService`解析appJson,获取下载信息，随后通过handler消息对应用下载安装。

![p9](http://drops.javaweb.org/uploads/images/7b68a4bb1d58a3210428cc10512b93a13735d90c.jpg)图解析appJson,进行下载安装

Handler存在4个msg.what值，‘3’处理下载失败；‘4’下载成功；‘5’弹出DialogPushActivity广告框若开启Accessiblity Service，启动WifiZengQiangService； ‘6’弹出DialogPushActivity广告框，启动恶意推广的应用。 首先发送“4“表示开始后台下载，随后启动下载安装的线程。该线程检查本次推送的应用是否已经被下载到指定目录，sdcard/.wifi_ckq保存下载的应用包以及广告图片，appName经过md5加密。

![p10](http://drops.javaweb.org/uploads/images/a0e435d7af69cc603194f5dfcaaaa2cbf9d996f2.jpg)图sdcard目录存放下载的推广应用包

![p11](http://drops.javaweb.org/uploads/images/13243b8d090255a00774b12532babeaa2a065c63.jpg)图下载恶意推广应用

下载完成后发送对应用静默安装，设备非root发送‘5’，root使用 pm install安装应用随后发送‘6’启动应用。

![p12](http://drops.javaweb.org/uploads/images/cbd25864402c196a71e396f9f5cbb3fc1a70ee7d.jpg)图发送handler安装应用

handler ‘5’,’6’都会启动DialogPushActivity，

![p13](http://drops.javaweb.org/uploads/images/7066f0aa05a89c656e88ed066be3eeb67521522d.jpg)图启动DialogPushActivity

DialogPushActivity其实就是一个ImageView，用户在触摸该界面后推送的应用将被自动安装

![p14](http://drops.javaweb.org/uploads/images/79276d27cdefd8cd0e9c17633f23f9c15442ac05.jpg)![p15](http://drops.javaweb.org/uploads/images/4f7fe56a9c793d3145a0952745a0ae305892ba05.jpg)图DialogPushActivity界面

启动WifiZengQiongService自动安装服务。之前的Ghosh Push,Kemoge等病毒家族，都是先对设备root然后植入推广应用。而该恶意应用的AccessibilityService一旦被启动，随后应用弹出恶意广告界面，即使受害者关闭弹出的广告，该应用程序也会被自动下载，随后成功安装。这个过程是调用系统的packageinstaller,获取安装界面的按钮位置，Accessibility提供的模拟用户点击功能，代替用户自动点击下一步，直到安装结束。下图是弹出的广告图，触碰后即可开始下载安装推广的应用。下图AccessibilityService里唤起安装界面

![p16](http://drops.javaweb.org/uploads/images/43ecb00491b0f920f8f635e3096f455f48467f95.jpg)图调用系统packageInstaller

AccessibilityService的onAccessibilityEvent方法不仅处理’com.android.packageinstaller’ 的event,还处理一些安全软件，这样该恶意应用将会完全控制安全软件行为，也就意味着该应用可以自动安装，启动任意app，卸载任意应用，而且利用AccessibilityService控制安全软件进行免杀。

![p17](http://drops.javaweb.org/uploads/images/4b962cf87543479860541d5868e0db4c758754e9.jpg)图AccessibilityService控制指定应用包

在推广的应用成功安装过后，系统将会发出`“android.intent.action.PACKAGE_ADDED”`广播消息，AppListenerReceiver类接受该广播并启动应用。

0x03 总结与建议
==========

* * *

到此滥用`AccessibilityService`过程分析完毕。该应用已增强WIFI信号诱惑用户启用`Accessibility`，以及查看WIFI密码是应用获取root权限。在此提醒用户谨慎给不受信应用开启`AccessibilityService`，以免被恶意应用控制；最近火热的抢红包应用也会利用`AccessibilityService`，实现自动抢功能，我们已发现黑客利用‘自动抢红包’诱导用户开启`AccessibilityService`控制手机，建议用户在安全渠道下载抢红包软件，以免不必要的损失。