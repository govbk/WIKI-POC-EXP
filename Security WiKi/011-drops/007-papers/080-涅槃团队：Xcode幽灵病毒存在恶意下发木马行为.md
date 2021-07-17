# 涅槃团队：Xcode幽灵病毒存在恶意下发木马行为

**360 Nirvan Team**

本文是 360 Nirvan Team 团队针对 XcodeGhost 的第二篇分析文章。

我们还原了恶意iOS应用与C2服务器的通信协议，从而可以实际测试受感染的iOS应用可以有哪些恶意行为，具体行为见下文。

最后，我们分析了攻击的发起点：Xcode，分析了其存在的弱点，及利用过程，并验证了该攻击方法。

0x01 恶意行为与C2服务器
===============

* * *

通信密钥分析
------

恶意程序将其与服务器通信的数据做了加密，如下图所示：

![](http://drops.javaweb.org/uploads/images/a6e002318e224265c619986b24148ec24137d27c.jpg)

密钥的计算方法：

![](http://drops.javaweb.org/uploads/images/97e804d58966a94957c46266cecd69ab89c2cde0.jpg)

通过分析，密钥为：stringWi，生成密钥的方式比较有迷惑性。

恶意行为分析
------

### 恶意行为一：做应用推广

方法是：首先检测用户手机上是否安装了目标应用，如果目标应用没有安装，则安装相应应用，其中目标应用由C2服务器控制。

我们逆向了恶意代码与C2服务器的通信协议，搭建了一个测试的C2服务器。然后通过C2服务器可以控制客户端安装第三方应用（**演示应用为测试应用，不代表恶意软件推广该应用**），见视频，

视频链接：[http://v.youku.com/v_show/id_XMTMzOTk0NDc2MA==.html](http://v.youku.com/v_show/id_XMTMzOTk0NDc2MA==.html)

![](http://drops.javaweb.org/uploads/images/c2b86ab4d894dacc6a0d908c57593b99c6944ec5.jpg)

**这是第一个针对 XcodeGhost 能力的视频演示。**

### 恶意行为二：伪造内购页面

相关代码如下：

![](http://drops.javaweb.org/uploads/images/7bf3d59dc92d16a80b502d47997c6398abe7561a.jpg)

### 恶意行为三：通过远程控制，在用户手机上弹提示

![](http://drops.javaweb.org/uploads/images/011f5d5ee4f61080b137bbd940878bb1426b9dba.jpg)

0x02 Xcode 的弱点及利用
=================

* * *

Xcode 的利用过程描述
-------------

Xcode 中存在一个配置文件，该配置文件可以用来控制编译器的链接行为，在受感染的 Xcode 中，该文件被修改，从而在链接阶段使程序链接含有恶意代码的对象文件，实现向正常iOS应用中注入恶意代码的目的。

被修改的文件内容如下：

![](http://drops.javaweb.org/uploads/images/674978a9131f74a94e7b8c19d6d2898f22cd5422.jpg)

从上图可以看到，程序会链接恶意对象文件 CoreService。

从链接过程的 Log 中可以看到其是如何影响链接过程的：

![](http://drops.javaweb.org/uploads/images/0df776306ff6c79fc1dda7209053cd9ba3f85b7a.jpg)

**注：实际上可以让 CoreService 从文件系统中消失，且在链接Log中没有任何额外信息。**

通过在配置文件中添加的链接选项，在工程的编译设置中无法看到，这就增加隐蔽性：

![](http://drops.javaweb.org/uploads/images/03b7ee21611caaf7f0385e73eb6dbace330a0c17.jpg)

对恶意代码 CoreService 的分析
---------------------

首先 CoreService 的文件类型为：Object，即对象文件。

查看 CoreService 中的符号，可以看到：

![](http://drops.javaweb.org/uploads/images/d153c485b8cf4629f0f44c817dded05e9de58efc.jpg)

导入的符号有：

![](http://drops.javaweb.org/uploads/images/6bf595b3cbfab7ea7592b011879d17d167cdc2a3.jpg)

验证概念
----

首先编写一个 ObjC 的类，测试如下图：

![](http://drops.javaweb.org/uploads/images/81b9b4b6a2274e334c8e9782b0d4e289f91cbb82.jpg)

![](http://drops.javaweb.org/uploads/images/041f77d6faa84a0cf361b4542c63b92c6cece279.jpg)

制作出对象文件 ProteasInjector.o，然后用这个文件替换掉 CoreService 文件，编译程序，然后反汇编，结果如下：

![](http://drops.javaweb.org/uploads/images/675dc07e2a5728a808f8ebd1dd8a0b2e6589526d.jpg)

可以看到代码被注入到应用中。