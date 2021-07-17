# 一只android短信控制马的简单分析

0x00 起因
-------

* * *

[WooYun: 仿冒电信运营商掌上营业厅的大规模钓鱼事件(大量用户银行卡中招CVV2与密码泄露)](http://www.wooyun.org/bugs/wooyun-2014-076180)

然后有大牛在某电信网厅钓鱼站找到一款android app让我看看，就有了接下来的分析。

0x01 观察
-------

* * *

拿到应用后先装到测试机上观察下,启动程序后立即监控到其向15501730287号码发送短信，内容为_软件已安装，但未被jh。当前手机型号nexus5。_

![pic](http://drops.javaweb.org/uploads/images/81a74d62561fb8f822f03ee7d8867713cd39ea04.jpg)

之后跳转到_要激活设备管理器吗？_的界面，如果不小心点了激活那卸载就将需要点手法了。

![pic](http://drops.javaweb.org/uploads/images/3acf348cfb720d7b49c2e7e50793e9c2eb8e192c.jpg)

不root的话需要到设备管理器里取消勾选才能正常卸载，如果root也可以直接删文件。

![pic](http://drops.javaweb.org/uploads/images/3ee88a2bdadeec0dd468ca0a4f67b523b318b5c3.jpg)

当受害者点击激活后还会发送短信通知黑客

![pic](http://drops.javaweb.org/uploads/images/e14db590b70fa536362441bbc51c9c8bad9569e1.jpg)

当然你点取消同样也发送短信黑客

![pic](http://drops.javaweb.org/uploads/images/18d1e1d670551ec6bac0ee3a4bd2700a43fcea73.jpg)

当完成这一系列动作后发现木马程序图片消失，并且无法通过系统自带应用管理直接卸载。

0x02 分析
-------

* * *

之后是解包反编译看源码咯，当然没有想象的顺利。因为这些个木马要对抗杀软肯定经过加壳处理的。在apk包中看到了libAPKProtect.so这个东西，那接下来就要针对性的脱壳啦。选择使用zjdroid（需xposed框架）脱壳。大致流程如下：

```
添加locat：zjdroid-shell-com.oliuyht.iujyhtgr.m
得到PID：the app target id = 5585

am broadcast -a com.zjdroid.invoke --ei target 5585 --es cmd '{"action":"dump_dexinfo"}'

filepath:/data/app/com.oliuyht.iujyhtgr.m-1.apk mCookie:1899531496

am broadcast -a com.zjdroid.invoke --ei target 5585 --es cmd '{"action":"dump_class","dexpath":"/data/app/com.oliuyht.iujyhtgr.m-1.apk"}'


am broadcast -a com.zjdroid.invoke --ei target 5585 --es cmd '{"action":"backsmali","dexpath":"/data/app/com.oliuyht.iujyhtgr.m-1.apk"}'

the dexfile data save to =/data/data/com.oliuyht.iujyhtgr.m/files/dexfile.dex

```

之后在用JEB或dex2jar反编译，然后就可以静态分析app了。文件较少功能肯定不会太复杂，之前有提到过程序采用了apkprotect防护。

![pic](http://drops.javaweb.org/uploads/images/24fb64cb21f998f35f044723b6c00e5bfcc5201f.jpg)

查看配置申请权限如下（到这里目测是个短信劫持马）

```
<uses-permission android:name="android.permission.WRITE_SMS"/>
<uses-permission android:name="android.permission.SEND_SMS"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.READ_SMS"/>
<uses-permission android:name="android.permission.RECEIVE_SMS"/>

```

配置文件还注册了两个activity和两个broadcast。

再看主界面代码，当主界面被第一次调用后就禁用此组件相应桌面图片也会消失。

![pic](http://drops.javaweb.org/uploads/images/6e4f4057a3262d9b4f611924ac4c118f0ba2b0b9.jpg)

然后执行发送短信_软件已安装，但未被jh。n当前手机型号Build.MODEL_，通知黑客。

![pic](http://drops.javaweb.org/uploads/images/c8b6f223d71812233455069fbe9b840f48b64888.jpg)

启动“激活设备管理”界面等待用户点击（一定程度防卸载）。

![pic](http://drops.javaweb.org/uploads/images/1fbee97b64ac0078ebe7cc4b074ef1cfced443fe.jpg)

程序总共发了7条短信6条是发给15501730287其中四条是_安装成功，激活成功，发送成功_这类消息用来判断受害者状态，剩余两条是用来窃验证码之类的机密短信。只有一条短信是根据黑客发送的短信提取出号码以及内容再发送。就是说黑客可以用短信控制你发送指定短信到指定号码。

![pic](http://drops.javaweb.org/uploads/images/e5f6be601b55a9633a937091560bfe9973b85b2f.jpg)

_kigdgc_类中硬编码了黑客接收短信的号码

![pic](http://drops.javaweb.org/uploads/images/71e2587276c70837560a0f53a208c044ad5dd170.jpg)

整个app大致功能如下

![pic](http://drops.javaweb.org/uploads/images/772436c77a05a7bbe6962433acb42289490d9beb.jpg)

0x03 总结
-------

* * *

大致就分析到这里，是一款可以窃取用户电信以及通过短信远程控制手机发送任意短信的短信劫持木马。黑客做了一系列的伪造和防御比如：伪装系统应用、隐藏图标、加壳、_this.abortBroadcast();_隐藏指令短信。预计黑客可以通过短信控制受害者发送一些吸费软短信，或者发送欺诈短信（比如大宝剑被抓给xxxxxxxx打2W块才能放人）当然短信是从本人手机发出就更具欺骗性了。还可以借此绕过一些验证如预留手机确认等（结合上文提到的钓鱼漏洞这个可能是主要目的）。

0x04 查杀
-------

* * *

LBE正常查杀(安装时就拦截到了)

![pic](http://drops.javaweb.org/uploads/images/4388cc6fed17020343e9a3796d1d02b822ae4d90.jpg)

腾讯手机管家未检测到

![pic](http://drops.javaweb.org/uploads/images/fd7949e5aa9d38760f5055fc8bbb6e39bb7ee20f.jpg)