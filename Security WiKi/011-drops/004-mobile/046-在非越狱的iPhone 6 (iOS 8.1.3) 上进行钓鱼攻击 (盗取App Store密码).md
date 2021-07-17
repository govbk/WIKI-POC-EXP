# 在非越狱的iPhone 6 (iOS 8.1.3) 上进行钓鱼攻击 (盗取App Store密码)

0x00 简介
=======

* * *

weibo:http://weibo.com/zhengmin1989

我们去年3,4月份在iOS还是7.0的时候就发现了一个能在非越狱的ios设备上进行钓鱼的攻击方法 (可以盗取Apple id的密码, gmail的密码等)，很早就报给了apple (Follow-up id: 609680831)，到现在apple也没有修复。为了紧跟Project Zero的潮流（90天的漏洞披露策略），现在打算公开demo和细节：   

首先我来解读一下这个demo。在非越狱的iPhone 6 (iOS 8.1.3) 上盗取App Store密码： 

在这个demo中，App Store是货真价实的系统app，但是弹出来的登录框不是App Store的，而是另一个在后台运行的app伪造的。我们知道在沙盒策略中，一个app运行在自己的沙盒空间中，理论上说是无法影响其他app的，如果能够产生影响就是一个很严重的问题。除了沙盒逃逸外，要让这个demo成功还需要具备以下几点要求：

*   安装钓鱼app到目标设备。
    
*   后台无限运行并开机启动。
    
*   检测目标app（比如App Store）的运行状态。
    
*   得到Apple ID的用户名以便实施钓鱼攻击。
    
*   弹出钓鱼对话框，并将用户输入的密码上传到服务器。 
    

0x01 start
==========

* * *

1. 安装钓鱼app到目标设备
---------------

* * *

 钓鱼app会使用一些特殊的API函数（后面会讲到，因为这些API不属于PrivateFrameworks，所以不确定是否是private API），所以我们需要考虑如果App Store拒绝接受这种app的情况。如果App Store拒绝接受的话，一般有两个方案：

1、采用特殊手段绕过检测：最简单的方法是采用混淆和动态加载，这个是360当年最爱用的方法，后来被Apple发现了，所有app被迫下架了1，2年。复杂的方法请参考Usenix Security的paper：Jekyll on iOS: When Benign Apps Become Evil。这种方法是先上传一个有溢出漏洞的App到App Store，然后采用远程ROP Attack的方法触发漏洞然后调用private API。

2、使用企业证书或者开发者证书签名app。这样的话就不通过App Store，而是通过USB等方法直接安装App到手机上。也就是PP助手，同步推使用的手法。想要做到这点很简单，一个国外的开源库libimobiledevice（http://www.libimobiledevice.org/）就可以满足你的需求。 

2．后台无线运行并开机启动
-------------

* * *

 这个有好几种方案，我这里简单介绍两种：

1、如果是采用企业证书或者开发者证书传播的话，只需要在UIBackgroundModes的plist里添加：Continuous，unboundedTaskCompletion和VOIP的属性即可。前两个算是private API，如果上传到App Store是不会通过审核的。

2、如果想要上传到App Store，就需要伪装成一个VOIP类型的App，这样的话可以做到开机启动。随后可以采用后台播放无声音乐的方法做到后台运行，播放工具可以采用AVAudioPlayer 这个对象，然后声明一个AudioSessionProperty_OverrideCategoryMixWithOthers的属性。因为是MixWithothers，在面板上不会有任何显示，用户并不会发现有音乐在播放，并且其他播放器在放音乐的时候也没有任何影响。  

3．检测目标app（比如App Store）的运行状态
---------------------------

* * *

这个也有好多方法，简单介绍两个：

1、UIDevice Category For Processes （http://zurb.com/forrst/posts/UIDevice_Category_For_Processes-h1H）。通过这种方法，可以获取到当前运行的程序。Demo中就是每隔5秒钟检测一次当前运行的程序是否有App Store，如果有，弹出钓鱼对话框。

2、获取所有安装的app的信息。使用LSApplicationWorkspace这个对象可以获取到所有已经安装的App的信息。 

4．得到Apple ID的用户名以便实施钓鱼攻击。这个细节请参考CVE-2014-4423。 
-----------------------------------------------

* * *

5．弹出钓鱼对话框
---------

并将用户输入的密码上传到服务器。正常的对话框是采用UIAlertView这个类，但是用这个类产生的对话框只能在自己app的view上显示。但如果采用CoreFoundation 这个framework （非private framework）中的CFUserNotificationCreate()和 CFUserNotificationReceiveResponse()方法的话，一个app就可以跳出沙盒的限制，并且在别的app界面上弹出自己的对话框。

比如下图，第一个是真正的对话框，而第二个是我伪造的，为了区分，我故意把K变成了小写。通过CFUserNotificationCreate()这个API，我们可以伪造很多应用的登陆对话框，不光是App Store，还可以是YouTube，Gmail，天猫等等。因为伪造的对话框和真实对话框没有任何区别，用户中招的几率会变得非常大。这个API本来是为Mac OS X设计的，但是因为iOS和Mac OS X共用了一些基本的底层框架，但是在iOS并没有屏蔽这个API接口，也没有做任何的权限检测，最后导致了沙盒逃逸。 

![enter image description here](http://drops.javaweb.org/uploads/images/7b6830cc93207f56d7da48a568e46d048c0acb15.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0d11fbb1a2163a18f26685ee7425c52c701db444.jpg)

0x02 结语 & 参考文章
==============

* * *

人们往往认为iOS比android的安全，所以在使用苹果手机的时候格外大胆，但事实并非如此。通过几个漏洞的combo，黑客们可以很容易的骗取你的帐号密码。更恐怖的是，本文所展示iOS漏洞也只是冰山一角。在我们ASIACCS 15论文中，我们还介绍了iOS远程控制，监控等漏洞的利用，有兴趣的同学可以继续学习。

1.  Min Zheng, Hui Xue, Yulong Zhang, Tao Wei, John C.S. Lui. "Enpublic Apps: Security Threats Using iOS Enterprise and Developer Certificates". (Full Paper)  Proceedings of 10th ACM Symposium on Information, Computer and Communications Security (ASIACCS 2015)

 2. Tielei Wang, Kangjie Lu, Long Lu, Simon Chung, and Wenke Lee. "Jekyll on iOS: When Benign Apps Become Evil", Proceedings of Usenix Security 2013