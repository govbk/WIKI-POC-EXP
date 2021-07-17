# Kali Nethunter初体验

安装过程
----

* * *

1、官网环境要求：n5 n7 n10 android 4.4

2、实验设备:

*   N7 android 4.4.4
*   N7 android 4.4.3
*   N5 nadroid 4.4.2

3、开发者模式+usb调试+解锁+root（一般刷过机的这些肯定都搞定了）

5、安装busybox + TWRP

6、开启MTP，卡刷包导入sdcard中，完成后关闭MTP（也可以不用MTP直接adb pull进去）

7、使用TWRP进入recovery（reboot recovery），安装rom，等待半小时就OK了。

先来张帅气的桌面

![](http://drops.javaweb.org/uploads/images/1e5f2fa2ebb09d34f753a4f696a2fb076124452b.jpg)

![](http://drops.javaweb.org/uploads/images/3845ce4f582e1ad6e7ad62d91fe627d457348138.jpg)

BadUSB MITM Attack
------------------

* * *

恶意USB中间人攻击：将装有nethunter的设备接入受害者电脑，执行此攻击可以劫持受害者流量。

![](http://drops.javaweb.org/uploads/images/9ffdce175fce291b02a30bfc81fad14f715d77e5.jpg)

tcpdump监听(默认tcpdump是被精简了的，需要自己上传一个。或者进入kali shell)执行tcpdump -i rndis0 icmp

受害者PC在攻击开始之前的网关

![](http://drops.javaweb.org/uploads/images/85c647b45b8dbd3a6da0d38b9f082ef6cb5dfffe.jpg)

受害者PC在攻击开始之后的网关

![](http://drops.javaweb.org/uploads/images/e35ff4d5e49f89f4e7295ca9882be71b14d36df3.jpg)

因为出现双网关现在所以并未像官网演示的那样流量直接走向恶意网关（10.0.0.1）而是依旧走的之前的网关（192.168.1.1）故劫持失败。在删除之前的网管后才生效。本帽觉得可以结合下文的**HID Keyboard Attack**先设置一个定时脚本执行对路由表的操作（删除原网关）。

![](http://drops.javaweb.org/uploads/images/2ef40bd612d269927868beee1a688c8ecfe2cd9b.jpg)

HID Keyboard Attack
-------------------

* * *

键盘劫持攻击：将智能设备伪造成功输入设备比如键盘输入恶意指令。比如添加管理员，反弹shell...

下面的添加管理员的演示，因为只是伪装键盘所以锁屏下是无法进行的。

![](http://drops.javaweb.org/uploads/images/3ae22ed11acf2c1ec28b2333b4a1ab0bbd1a4d87.jpg)

![](http://drops.javaweb.org/uploads/images/cedb3f3140d5a5b7a3a14befde9c1213f7fa3851.jpg)

还要配置payload和监听懒得弄了。

![](http://drops.javaweb.org/uploads/images/917255989ebc82b5e4f1dfd279415eaf273a0afe.jpg)

其他功能
----

* * *

功能菜单

![](http://drops.javaweb.org/uploads/images/ae6d64f5a0e455bb24039f8c346a662e7c715c30.jpg)

Mana伪造ap，dnsmasq,hostap，wifite(网卡原因，有关无线的实验未成功,感觉得有sim卡才行)

![](http://drops.javaweb.org/uploads/images/052f3051e42ca941247eaea7dfdb8d7efdcc1207.jpg)

![](http://drops.javaweb.org/uploads/images/5c88c4793ac20955910e82a3ae3b59e1d4c67710.jpg)

![](http://drops.javaweb.org/uploads/images/c4610324a626012c038a3b91d1a79737509ff0b2.jpg)

![](http://drops.javaweb.org/uploads/images/78cbdadd29c86d72b929cf2ef43321725a6f8c44.jpg)

总结
--

* * *

nethunter整体感觉比较鸡肋瑞士军刀言过其，刷着玩玩还可以，真指望他干些啥有价值的事情利用场景还是非常局限的。实在没啥好说的了，折腾了一段时间把经验和感想写出来分享给大家总比那些完全没有思考和实践仅从官网翻译几句话盗几张图来得有价值。

[下载](http://www.offensive-security.com/kali-linux-nethunter-download/)

[官网](http://www.kali.org/kali-linux-nethunter/)

[介绍](http://nethunter.com/)