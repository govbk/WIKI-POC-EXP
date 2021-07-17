# Android敲诈病毒分析

0x00 前言
=======

* * *

最近哈勃文件系统捕获一批FBI敲诈病毒及其变种，该类病毒通过色情网址诱导用户下载安装，一旦用户安装运行，病毒会强制置顶自身并显示恐吓信息，对用户进行敲诈勒索。

0x01 传播途径
=========

* * *

通过色情网址诱导用户下载安装。

程序安装后的图标：

![enter image description here](http://drops.javaweb.org/uploads/images/582316374016e3d1a0606b62f395106f0679a704.jpg)

0x02 恶意行为概述
===========

* * *

当访问色情网址时，会诱导用户下载安装该恶意样本。一旦安装，duang~，不幸发现自己中了大招，手机变砖头了。

恶意病毒将强制将自身置顶，无论是按HOME键，还是关机重启，完全不管用，敲诈恐吓信息始终在那里：显示虚假恐吓信息，敲诈用户支付$500金额的MonkeyPak。

![enter image description here](http://drops.javaweb.org/uploads/images/5c42af4d2326486bcb93941d1b1e7fae2eda233f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/7faad3ac30fcfdef86167e8bc4aa80bd98189887.jpg)

病毒的恶意行为：

### 1. 样本首先会添加设备管理器：

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/6fe5bea92b90d811f8e285bc8d7723c9cd688b90.jpg)

2. 强制将自身置顶：
-----------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/6da6855a0e8a9a8e1dca5e05a84f442ac79167cb.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f75a89d35de24aa8eb448f98dc4ae37864ad2d6c.jpg)

### 3. 打开前置摄像头并拍照、获取添加账户的邮箱列表及手机硬件信息：

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/603383b017492b301dab58923dba6844608bd5c9.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/cb9bda3c5446f74642cfdf0e74e817239431292b.jpg)

### 4. 将第三步获取的信息、相关命令字以及输入的MoneyPak号等信息加密后上传到服务器：

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/f8ec1a624e36d4f1b58cd7d33b52a8814c01b5bd.jpg)

### 5. 分析样本文件发现，恶意应用的制作者在验证MoneyPak可用时，会将服务器的返回信息中的status项的值置为77并保存在配置文件里，远程控制病毒程序退出：

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/2c206785974b71b44afa826c9acf74ab6d5ee87e.jpg)

由以上分析可知，一旦中了该病毒，用户就没有机会进入手机，更无法启动杀软来清除、修复。那这个时候，手机变砖了吗？当然不是。哈勃分析系统发现这个病毒之后，决定第一时间要为用户解决这个难题，用最快的时间来出（jia）专（te）杀（ji）。 用户可以在http://habo.qq.com/Download/FBIVirusKiller下载FBI敲诈病毒专杀工具，按照工具的指引即可快速清除病毒。

![enter image description here](http://drops.javaweb.org/uploads/images/7770859e6b42d328255495cf6cd85613a76921d2.jpg)

使用专杀工具的前提是手机开启了“USB调试”（有人会担心手机没有ROOT怎么办，这里特别强调一下，未ROOT的手机也可以完美解决）。 如果不满足专杀工具的使用条件，可以尝试采用如下步骤手动清除：

### 1. 关闭手机后，重新启动进入安全模式

* * *

 主流安卓手机进入安全模式的方式是，按住【电源键】开机，直到屏幕上出现品牌LOGO或运营商画面后，按住【音量减少】键不放。如果进入安全模式成功，锁屏界面的左下角会显示“安全模式”字样。

![enter image description here](http://drops.javaweb.org/uploads/images/275810d05cc05513f161090100e8358a53d478db.jpg)

### 2. 进入设置-安全-设备管理器，找到病毒程序并取消激活

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/e09c5917fe41762da264df45d96eab58df7e6409.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/fb45c87468a94c3af26e4e0b6532ecbc291ec8bf.jpg)

### 3. 进入设置-应用或应用程序，找到病毒程序并卸载

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/1041a0ae080fd7e9c39706bc762f17cfda7bc177.jpg)

### 4. 重启手机，进入正常模式，发现病毒程序已经被卸载了。

0x03 给用户的安全建议
=============

* * *

1. 广大用户手机一定要安装安全软件，在病毒感染手机前就可以发现其危险，避免安装病毒后给您带来损失。目前腾讯电脑管家、手机管家、哈勃分析系统均能准确识别此类病毒；
2. 在可靠的安卓市场上下载手机应用，不要安装论坛或朋友转发的手机应用；
3. 不要下载内容不健康的手机应用，如色情播放器类应用。