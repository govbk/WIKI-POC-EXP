# Samsung S Voice attack

参考：http://arxiv.org/pdf/1407.4923.pdf

0x00 三星S voice
--------------

* * *

三星s voice是类似apple siri以及google voice的一款语音助手软件，通过此款软件可以释放双手通过语音命令操作手机。执行如拨打电话、发送短信、拍照等功能。由此可见此软件的权限是非常宽广的。

![enter image description here](http://drops.javaweb.org/uploads/images/7662d72a10bef499eac999bb432a183c9d3755fe.jpg)

App申请的权限如下：

```
<uses-permission android:name="android.permission.BROADCAST_STICKY"/>
<uses-permission android:name="android.permission.READ_CALENDAR"/>
<uses-permission android:name="android.permission.WRITE_CALENDAR"/>
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
<uses-permission android:name="android.permission.CALL_PHONE"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_LOCATION_EXTRA_COMMANDS"/>
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
<uses-permission android:name="android.permission.READ_CONTACTS"/>
<uses-permission android:name="android.permission.WRITE_CONTACTS"/>
<uses-permission android:name="android.permission.READ_PHONE_STATE"/>
<uses-permission android:name="android.permission.READ_SMS"/>
<uses-permission android:name="android.permission.READ_USER_DICTIONARY"/>
<uses-permission android:name="android.permission.RECEIVE_SMS"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.SEND_SMS"/>
<uses-permission android:name="android.permission.WRITE_SMS"/>
<uses-permission android:name="android.permission.WRITE_SETTINGS"/>
<uses-permission android:name="android.permission.VIBRATE"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.WRITE_USER_DICTIONARY"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
<uses-permission android:name="android.permission.BLUETOOTH"/>
<uses-permission android:name="android.permission.CHANGE_WIFI_STATE"/>
<uses-permission android:name="android.permission.WAKE_LOCK"/>
<uses-permission android:name="com.android.launcher.permission.INSTALL_SHORTCUT"/>
<uses-permission android:name="android.permission.DISABLE_KEYGUARD"/>
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN"/>
<uses-permission android:name="com.android.alarm.permission.SET_ALARM"/>
<uses-permission android:name="com.android.vending.BILLING"/>
<uses-permission android:name="android.permission.GET_TASKS"/>
<uses-permission android:name="android.permission.GET_ACCOUNTS"/>
<uses-permission android:name="com.android.alarm.permission.SET_ALARM"/>
<uses-permission android:name="com.sec.android.widgetapp.q1_penmemo.permission.READ"/>
<uses-permission android:name="com.sec.android.widgetapp.q1_penmemo.permission.WRITE"/>
<uses-permission android:name="com.sec.android.permission.READ_MEMO"/>
<uses-permission android:name="com.sec.android.permission.WRITE_MEMO"/>
<uses-permission android:name="com.android.email.permission.ACCESS_PROVIDER"/>
<uses-permission android:name="com.android.email.permission.READ_ATTACHMENT"/>
<uses-permission android:name="com.sec.android.app.clockpackage.permission.READ_ALARM"/>
<uses-permission android:name="com.sec.android.app.clockpackage.permission.WRITE_ALARM"/>
<uses-permission android:name="com.sec.android.app.twdvfs.DVFS_BOOSTER_PERMISSION"/>
<uses-permission android:name="android.Manifest.permission.DISABLE_KEYGUARD"/>
<uses-permission android:name="android.permission.DISABLE_KEYGUARD"/>
<uses-permission android:name="com.infraware.provider.SNoteProvider.permission.READ"/>
<uses-permission android:name="com.infraware.provider.SNoteProvider.permission.WRITE"/>
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
<uses-permission android:name="android.permission.READ_CALL_LOG"/>
<uses-permission android:name="com.sec.android.app.sns3.permission.SNS_FB_ACCESS_TOKEN"/>
<uses-permission android:name="com.samsung.music.permission.READ_MUSIC_STORAGE"/>
<uses-permission android:name="com.sec.android.daemonapp.ap.yonhapnews.permission.YONHAP_DAEMON_ACCESS_PROVIDER"/>
<uses-permission android:name="com.sec.android.app.music.permission.READ_MUSICPROVIDER"/>

```

0x01 Android permission
-----------------------

* * *

应用在执行某项敏感操作时（例如发送短信）必须在程序安装时就对此项权限进行申明

参考：

http://developer.android.com/guide/topics/manifest/uses-permission-element.html http://developer.android.com/guide/topics/manifest/manifest-intro.html#perms http://developer.android.com/reference/android/Manifest.permission.html

![enter image description here](http://drops.javaweb.org/uploads/images/cbd03b94f0c3c6708725b536da5befb09617a08d.jpg)

恶意软件要获取手机通讯录中的联系人信息就必须申请READ_CONTACTS 权限，读取信必须申请READ_SMS ，发现短信要申请 SEND_SMS 权限。利用这一机制小伙伴如果发现某些不知名软件申请这些权限就果断点取消。更机智小伙伴就会利用权限管理软件把看片神器的除网络访问权限以为的权限都关闭掉。

![enter image description here](http://drops.javaweb.org/uploads/images/272e15dafb700fbcbc3e971c639831ad170734ec.jpg)

0x02 攻击思路
---------

* * *

在权限管理软件的控制下恶意软件视乎难以再有所作为，是否有零权限的攻击方法了？ 这就要借助上文提到高权限软件s voice了，我们可以伪装一个恶意软件不申请任何敏感权限再借助S voice“提升权限”达到攻击效果。

![enter image description here](http://drops.javaweb.org/uploads/images/661fb2ba44a09501d2df1db4005d66decc7f9cd1.jpg)

0x03 Demo
---------

设计思路： 1、 设置intent启动S Voice

```
Intent intent = new Intent();
intent.setAction("android.intent.action.VOICE_COMMAND");
startActivity(intent);

```

2、 调用MediaPalyer类播放攻击语音

```
private MediaPlayer mp4;
mp4 = MediaPlayer.create(MainActivity.this, R.raw.confirm); 
mp4.start();

```

demo应用未申请任何权限

![enter image description here](http://drops.javaweb.org/uploads/images/a65fd322ed4d86d34f862cc3e18fc07f410833b2.jpg)

演示视频： http://v.youku.com/v_show/id_XNzUyNzk3MzYw.html

0x04 补充说明
---------

* * *

```
1. 因为google voice的谷歌类产品被严重河蟹基本无法使用，不考虑这种情况下音频文件过大可使用google TTS 文字转语音。
2. 其他语音助手软件：百度语音….
3. 即使声音很小也能成功被s voice识别，睡眠时小于55分贝不易被发现。可以通过监视系统状态、传感器判断手机运行状态。
4. 安卓系统中录音方法是synchronized,也就是通过sdk api多个应用是无法同时访问麦克风的。想无声攻击可以考虑NDK。
5. 通过传感器、系统状态信息判断手机是否被使用，再未使用的情况下唤醒屏幕，发出攻击指令。（s voice在屏幕关闭时候无法运行，用户在使用时攻击指令发声易被发现）
6. 锁屏下攻击思路：

```

![enter image description here](http://drops.javaweb.org/uploads/images/ab2ae55023e35e7be1b629546232ac26e7fb3af5.jpg)