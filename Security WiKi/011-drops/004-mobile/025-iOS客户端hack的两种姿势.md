# iOS客户端hack的两种姿势

> 分析某商城漏洞，在漏洞验证时采用了两种iOS上的hack工具：cycript和reveal，各有风情，均能攻城拔寨，实乃我辈日常居家、杀人越货之利刃，现与诸君共享之。

0x00 漏洞缘起
=========

* * *

该商城的iOS版app为用户提供了找回密码的功能，用户需通过三个步骤找回密码：

1.  输入一个本地的图形辨识验证码（多余？）
2.  提供用户手机号，输入一个短信验证码
3.  输入新的密码、确认密码，然后Bingo

要找漏洞，先抓包看看，先易后难，实在不行再做逆向分析。burp架起先，开代理、关闭intercept、ssl协议算法全勾上（免得碰上奇葩ssl协商参数，以前遭过冤枉）。iPhone上在wifi选项中配置代理，指向burp。然后开app，burp报错。

![enter description here](http://drops.javaweb.org/uploads/images/cf61560e8b14180edebae4b11c12117d0856a0ea.jpg)

难道客户端对证书进行了pin？冷笑三声，开启我的ssl kill switch。再开程序，登录，进商城，一切顺利。ok，现在进入正题，找漏洞。进入找回密码功能，按步骤进行提交，重设了密码，然后到burp中查看抓到的数据包，下面是重置密码第三步发出的post数据包。

![enter description here](http://drops.javaweb.org/uploads/images/0822f38f306ddf76f73b6091acd6b1430daf6edb.jpg)

仔细分析这个数据包，发现除了一个签名，其它跟第二步获得的手机短信验证码没有一毛钱的关系，难道这个“你妈是你妈”问题的验证是在客户端做的？那我们是不是改改电话号码就能重置任意用户密码了？在burp中改包试了试，不行的，服务器返回错误。看来在Sign中有文章，看来需要从客户端想办法了。

丢到ida中跑，找到如下关键函数：

![enter description here](http://drops.javaweb.org/uploads/images/b1b0ce059d4976c5449b73f98d8c5d46b3b64125.jpg)

然后再初略的溜了一下该函数涉及到的各种参数。

![enter description here](http://drops.javaweb.org/uploads/images/7101c6270b058b166562d8d520f9423f79caf755.jpg)

好像没有涉及到第二步中的短信验证码，应该只是把电话号码、新口令作为签名的可变输入。不错，省得逆向签名算法了，人生苦短，可以节约一堆脑细胞了。基本思路出来了，就是正常执行前两步，然后在第三步中将界面电话号码（用户账号）改为其它被攻击的账号。

0x01 cycript大法
==============

* * *

先介绍一下cycript，官方解释：

> Cycript allows developers to explore and modify running applications on either iOS or Mac OS X using a hybrid of Objective-C++ and JavaScript syntax through an interactive console that features syntax highlighting and tab completion.

简而言之：插入进程，想改就改。不过这货是命令行模式，混合了ObjectC和JS，官方帮助写的精简了点，还是稍微有点烦。不过自带了tab键补全功能，略感欣慰。下面一步步来使用。

实现目标的先决条件是要找到找回密码过程第三步界面对应的对象，然后对该对象中与注册手机号码相关的属性进行操作。

先要将app运行到我们要攻击的第三步，也就是输入新口令和确认新口令的界面，我们的目标是使用hack方法修改不可编辑的注册手机号。

![enter description here](http://drops.javaweb.org/uploads/images/84a0b75de05ff5c13f140c43a39a5ca5c828f09f.jpg)

当然，我们也要先将app使用classdump将app的类信息获取，发现了其中与口令重置相关的信息如下，可以辅助下一步的攻击工作。

![enter description here](http://drops.javaweb.org/uploads/images/7bbfb4c8a5f99c079f0b7aa7e0f8342b8c0edc84.jpg)

使用ps命令获得被注入的进程信息，然后使用如下命令启动cycript，涂红部分为进程名称，当然，使用pid也可以。

![enter description here](http://drops.javaweb.org/uploads/images/374279fccb1dc7117295fcce97dc02e87b02f651.jpg)

然后获得当前app的UI句柄。

![enter description here](http://drops.javaweb.org/uploads/images/0cf21a0b370cb96d7ee6d30c2525e18ebd0063f5.jpg)

获得app的keyWindow。

![enter description here](http://drops.javaweb.org/uploads/images/a369096facf9dde34e65b9ed9787609f2dcede04.jpg)

获得keyWindow的rootViewController。

![enter description here](http://drops.javaweb.org/uploads/images/482118bd1946e5524ee759d826e9586f50ddaad7.jpg)

获得当前可视的ViewController。做界面hack，前几步基本是一样的，目的就是找到当前显示界面对应的对象。

![enter description here](http://drops.javaweb.org/uploads/images/1d11daeb5f3d4d783ca7e5a8f193484f9de7e488.jpg)

各位看官发现没的，这个FindPwdViewController正是我们使用classdump发现的密码重置类，看来接近问题答案了。

![enter description here](http://drops.javaweb.org/uploads/images/f3fdbdb9c5efb549162c15e9d313383cf21b688e.jpg)

接下来可以直接根据classdump出的类信息敲入如下命令：

![enter description here](http://drops.javaweb.org/uploads/images/46d054410b1c2f0cc9e066b688e41120aab09697.jpg)

看到text没得，就是界面显示的注册手机号，改改改！

再看手机上，注册手机号已经修改成了目标手机号。点击完成，成功！

0x02 reveal大法
=============

* * *

reveal工具其实应该被奉为界面hack的第一利器，无它，太好用了。各位可能还在纠结上面敲入的各种烦人命令，如果对ObjectC和面向对象思想以及各类砸壳、dump工具不熟的化，要完成cycript大法，还真不是一件容易活。但reveal不同，在安装好后，就是轻轻的点点鼠标，敲个电话号码的事。

不过还是有石头要挡道，就是reveal在手机端的安装。下面是笔者的安装经验:

reveal原本是作为xcode的辅助工具，为app开发者使用的，本不具备插入任意程序的功能，但在越狱的iphone上借助cydia substrate可以插入任意app，包括springboard，安装方法参见[参考1](http://42.96.192.22/?tag=%E8%B0%83%E8%AF%95%E5%88%A9%E5%99%A8reveal)。笔者是在iOS9上装的，一定要按这篇文章说得，把framework搞到手机端，另外，plist文件要用plisteditor等专用工具编写，还有就是Filter一定要写，要不然就是iPhone6S Plus也会慢的无法忍受！如果出现这种窘境，立即home+power硬关机，按音量+开机跳过substrate，重新进行Filter配置。最后提醒一句，reveal所在的主机和被调试手机要在同一局域网。

reveal安装好之后，需要找到被注入程序的bundle id，就在app的ipa包的info.plist文件中，使用plisteditor等工具打开，搜CFBundleIdentifier就能找到，下面涂红的部分即是。

![enter description here](http://drops.javaweb.org/uploads/images/94c73e53501905699eb9db429b3ba670a8252470.jpg)

找到bundle id后将其填到Filter中即可。启动程序，在reveal的connect目标中会发现目标app，直接connect，reveal中会出现手机端app的界面。借一张上面文章的图，各位感受一下，各种界面元素一览无余，而且可以3d显示层级关系，酷。

![enter description here](http://drops.javaweb.org/uploads/images/32a032dcfe158647ebb239681ea54b84bd53aaf4.jpg)

更酷的是，它可以直接修改界面元素的内容，不管在原手机端该元素是否可编辑，并且编辑后直接反应到手机端界面。

有了这种功能，要应付我们本漏洞验证的目标就太容易了，啪啪啪走到第三步，刷新reveal段界面，在如下图中直接编辑注册手机号内容，回车，再在手机端点击完成，ok。

![enter description here](http://drops.javaweb.org/uploads/images/28648784a37d983f724b3d7b54674b89e8830a14.jpg)

0x03 总结
=======

* * *

cycript和reveal其实都根植于cydia substrate这棵大树，不过风格迥异罢了。一个是玲珑剑，需要舞者精心驾驭，一个是大砍刀，直接快意杀伐。不过爽的是我可以左手玲珑剑，右手大砍刀，仰天长啸，快意恩仇，不亦乐乎！

0x04 参考
=======

* * *

*   调试利器Reveal
    
    [http://42.96.192.22/?tag=%E8%B0%83%E8%AF%95%E5%88%A9%E5%99%A8reveal](http://42.96.192.22/?tag=%E8%B0%83%E8%AF%95%E5%88%A9%E5%99%A8reveal)