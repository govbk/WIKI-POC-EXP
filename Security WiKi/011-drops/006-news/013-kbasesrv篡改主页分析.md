# kbasesrv篡改主页分析

0x00 前言
=======

* * *

话说最近浏览器首页莫名其妙变成了金山毒霸网址大全，本来以为是运营商劫持，但仔细排查一遍，才发现是一个名叫kbasesrv的程序在搞鬼，它的数字签名是“Beijing Kingsoft Security software Co.,Ltd”，确定是金山旗下的软件无疑。

主页劫持本来已经见怪不怪了，一般是推广联盟的渠道商为了赚钱而各种手段无所不用其极，但是像金山这样的名门大厂亲自动手偷偷摸摸篡改主页的，还真是比较少见。今天是429首都网络安全日，一家安全公司却干起了流氓软件的行当，不能不说是一种莫大的讽刺。

0x01 分析
=======

* * *

闲话少叙，接下来深入扒一扒kbasesrv究竟是怎样偷偷篡改主页的：

![](http://drops.javaweb.org/uploads/images/4c602555f0743d7c07a2d33730ee34faeb934d23.jpg)

程序MD5：318330C02C334D9B51F3C88027C4787C

程序SHA1：A6253F2C2DE7FB970562A54ED4EC0513BE350C66

该程序由金山旗下软件静默下载安装到电脑里，并用特定参数启动。参数形式如下：

`-tid1:30 -tid2:10 -tod1:24 -tod2:27 -xxlock:68_upd3`

其中前面的tid1、tid2、tod1、tod2这4个参数固定不变。最后一个xxlock参数会根据推送软件的不同而有所不同，根据网上搜集相关情况和实测验证，目前发现的推广参数统计结果如下：

| -xxlock参数值 | 对应发起推广的软件 |
| --- | --- |
| 68_upd | 金山词霸 |
| 68_upd2 | PPT美化大师 |
| 68_upd3 | WPS |
| 88dg_upd | 驱动精灵 |

给参数后，软件全程静默安装并篡改首页（无参数情况下启动也是静默安装，但不篡改首页）。仅仅是在桌面上释放一个名为“网址导航”的快捷方式。

![](http://drops.javaweb.org/uploads/images/76cb465ee46eafc072ea0eb95f16fd5b7b11c224.jpg)

而这是快捷方式对应的程序目录（目录内所有可执行程序均带有有效的金山公司数字签名，这里就不一一贴出了）：

![](http://drops.javaweb.org/uploads/images/3a2ca6ec4164abdec37862c6899c4e10901550d0.jpg)

当然，必须要承认该软件还是非常“守规矩”地在系统的“添加/删除程序”面板中放置了对应的卸载项的（至于用户能不能猜到是这个kbasesrv，他们可能就不是特别关心了）。

![](http://drops.javaweb.org/uploads/images/9cad3e72233210c700c4043ba1f11fb0a3ee591a.jpg)

双击打开桌面的快捷方式，会启动IE浏览器并访问“毒霸网址大全”：

![](http://drops.javaweb.org/uploads/images/b714758749f1260b4cfc8cd5af01d28ab634421d.jpg)

至此，如果仅仅是释放一个快捷方式，推广一下自己的导航站，或许还情有可原，但事情并不这么简单。该程序还在系统的桌面进程（explorer.exe）中注入了自己的三个dll文件用以劫持桌面操作——尤其是劫持用户双击运行程序的操作。

![](http://drops.javaweb.org/uploads/images/56826a2df56dd54db6d1948518f73ba76b3a890e.jpg)

其中最下面的“knb3rdhmpg.dll”文件（MD5:5A2CCE5BF78C8D0D8C7F9254376A2C46; SHA1: F1EDBCA2065B0B951344987B59F33387804F32BA）中更是大大方方的直接硬编

码了待推广的网址：

![](http://drops.javaweb.org/uploads/images/c84e2a4ac8362d394c16ad69bb3ee28da613e9e9.jpg)

同时也列出了大量需要“特别对待”的程序：

![](http://drops.javaweb.org/uploads/images/11bec9e6f304beb07f57c987105f8ec55a5bab30.jpg)

![](http://drops.javaweb.org/uploads/images/2b57dd2d3c4569fc897d323b813c48262b15ee0d.jpg)

![](http://drops.javaweb.org/uploads/images/d02e143237773730e054142ced8a6d59da632064.jpg)

为了验证效果，特意在测试机器中安装了几个比较有代表性的浏览器。可以看到所有快捷方式后面都是没有任何启动参数的，也就是说在干净的环境里双击启动这些浏览器，他们都会打开默认的主页：

![](http://drops.javaweb.org/uploads/images/d6c00fd95450588db06a0861c9bcc6f195a84f8e.jpg)

但是在双击运行这些浏览器的时候，打开的主页却都变成了“毒霸网址大全”

![](http://drops.javaweb.org/uploads/images/48ab349df1e9489011d26bc3b1a18846c5e229ae.jpg)

手法则很简单，因为已经注入了桌面进程，所以只需要在用户双击启动浏览器的时候，悄悄的在桌面进程向对应浏览器主程序发送启动消息的时候插入一条参数就万事大吉了：

![](http://drops.javaweb.org/uploads/images/e153e3568a8b58f04848b268cd8ae1d2d4ba0565.jpg)

![](http://drops.javaweb.org/uploads/images/30321f7681203fbc7a64f0234c111404fd4133de.jpg)

![](http://drops.javaweb.org/uploads/images/13bf8d08fb1c377fbf0494698ad917328bf51fd3.jpg)

![](http://drops.javaweb.org/uploads/images/ea51e2a62f2563569a692979618c85133d00e633.jpg)

0x02 结语
=======

* * *

所谓能力越大，责任越大。安全软件作为系统的守护神，名正言顺地拥有系统的高权限，也背负着众多用户的信任。金山却偷偷动用旗下多款软件静默安装流氓软件，而很多用户还蒙在鼓里，不知道该怎么设置回自己习惯的主页。

若要人不知，除非己莫为。我就想问问金山，无论kbasesrv强奸了多少主页，为金山增加了多少收入，与丢掉的那些用户信任相比，真的值得吗？