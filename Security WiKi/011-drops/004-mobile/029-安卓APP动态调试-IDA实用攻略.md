# 安卓APP动态调试-IDA实用攻略

0x00 前言
=======

* * *

随着智能手机的普及，移动APP已经贯穿到人们生活的各个领域。越来越多的人甚至已经对这些APP应用产生了依赖，包括手机QQ、游戏、导航地图、微博、微信、手机支付等等，尤其2015年春节期间各大厂商推出的抢红包活动，一时让移动支付应用变得异常火热。

然后移动安全问题接憧而至，主要分为移动断网络安全和客户端应用安全。目前移动APP软件保护方面还处于初级阶段，许多厂商对APP安全认识不够深入，产品未经过加密处理，使得逆向分析者能够通过逆向分析、动态调试等技术来破解APP，这样APP原本需要账号密码的功能可以被破解者顺利绕过，使得厂商利益严重受损。

对未加壳的APP进行动态调试，通常可以非常顺利且快速地绕过一些登陆限制或功能限制。本文将以安卓APP为例，来详细介绍一下移动APP动态调试技术。

0x01 调试环境搭建
===========

* * *

1.1 安装JDK

JAVA环境的搭建请自行查找资料，这里不做详述。

1.2 安装Android SDK

下载地址：http://developer.android.com/sdk/index.html。

下载完安装包后解压到任意一目录，然后点击运行SDK Manager.exe，然后选择你需要的版本进行安装，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/1c80923d30de6376c5084dee9ab4b4ae0372afa0.jpg)

1.3 安装Eclipse集成开发环境

下载地址：http://www.eclipse.org/downloads。选择Eclipse for Mobile Developers，解压到任意目录即可。

1.4 创建Android Virtual Device

动态调试可以用真实的手机来做调试环境，也可以用虚拟机来做调试环境，本文采用虚拟机环境。因此创建虚拟机步骤如下：

1打开Eclipse –>windows->Android Virtual Device

![enter image description here](http://drops.javaweb.org/uploads/images/2bfb7a4263a15106cef9eead3f0030d111f8b5c2.jpg)

2点击Create，然后选择各个参数如图：

![enter image description here](http://drops.javaweb.org/uploads/images/1d9efd79b054e95a61a0b94eb05fa91340d652a4.jpg)

这里Target 就是前面步骤中安装的SDK 选择任意你觉得喜欢的版本就可以。点击OK 就创建完毕。

1.5 安装 APK改之理

这个是一个很好用的辅助调试的软件，请自行搜索下载。

1.6 安装 IDA6.6

IDA6.6开始支持安卓APP指令的调试，现该版本已经提供免费下载安装，请自行搜搜。

0x02 Dalvik指令动态调试
=================

* * *

2.1 准备工作
--------

安卓APP应用程序后缀为apk，实际上是一个压缩包，我们把它改后缀为rar打开如图：

![enter image description here](http://drops.javaweb.org/uploads/images/e2cf02fd871d4f61922bb5e2ffdefe6d85ce8b02.jpg)

其中classes.dex是应用的主要执行程序，包含着所有Dalvik指令。我们用APK改之理打开apk，软件会自动对其进行反编译。反编译后会有很多smail文件，这些文件保存的就是APP的Dalvik指令。

在APK改之理里双击打开AndroidManifest.xml，为了让APP可调试，需要在application 标签里添加一句android:debuggable="true" 如图：

![enter image description here](http://drops.javaweb.org/uploads/images/23fcc1028892a446c3836a8411da82bf2923b899.jpg)

然后点击保存按钮，然后编译生成新的apk文件。接着打开Eclipse –>windows->Android Virtual Device，选择刚才创建的虚拟机，然后点击start，虚拟机便开始运行。偶尔如果Eclipse启动失败，报错，可以同目录下修改配置文件：

![enter image description here](http://drops.javaweb.org/uploads/images/d2f8c44b9cbfe681a1752d92ebe496e3d5454348.jpg)

把配置参数原本为512的改为256 原本为1024的改为512，然后再尝试启动。

在SDK安装目录有个命令行下的调试工具adb shell，本机所在目录为E:\adt-bundle-windows-x86-20140702\sdk\platform-tools，把adb.exe注册到系统环境变量中，打开dos命令行窗口执行adb shell 就可以进入APP命令行调试环境，或者切换到adb所在目录来执行adb shell。

![enter image description here](http://drops.javaweb.org/uploads/images/9119cbc89bc2a5d8d85441c1415c28fb7ab44dce.jpg)

这里先不进入adb shell，在DOS命令行下执行命令：adb install d:\1.apk 来安装我们刚才重新编译好的APK文件。安装完毕会有成功提示。

2.2 利用IDA动态调试
-------------

将APP包里的classes.dex解压到任意一目录，然后拖进IDA。等待IDA加载分析完毕，点击Debugger->Debugger Options如图

![enter image description here](http://drops.javaweb.org/uploads/images/05e405303c14d7e2cba73acc87e6e4ef39896894.jpg)

按图所示勾选在进程入口挂起，然后点击Set specific options 填入APP包名称和入口activity 如图：

![enter image description here](http://drops.javaweb.org/uploads/images/86e9fab329871a54533eb5e367ad536527db1e87.jpg)

其中包的名称和入口activity 都可以通过APK改之理里的AndroidManifest.xml 文件获取：

```
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example.simpleencryption">
    <application android:allowBackup="true" android:debuggable="true" android:icon="@drawable/creakme_bg2" android:label="@string/app_name" android:theme="@style/AppTheme">
        <activity android:label="@string/app_name" android:name=".MainActivity">

```

然后在IDA点击Debugger->Process Options

![enter image description here](http://drops.javaweb.org/uploads/images/fa32e4d8bf6c6935565dff6688292918251a590a.jpg)

其他默认不变，端口这里改为8700。这里默认端口是23946，我在这里困扰了很久，就是因为这个端口没有改为8700所致。然后我们看看这个8700端口是怎么来的。在Android SDK里提供了一款工具DDMS，用来监视APP的运行状态和结果。在SDK的TOOLS目录有个DDMS.BAT的脚步，运行后就会启动DDMS。由于我的本机安装了SDK的ADT插件，DDMS集成到了Eclips中，打开Eclips->Open perspective->ddms就启动了DDMS。

如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/04ea71072411021183809343a491525443690d99.jpg)

在DDMS选中某个进程后面就会注释出它的调试端口,本机这里是8700。

到此所有的工作就准备就绪，然后就可以下断点来调试该APP了。我们在APK改之理中在com目录下查看smali文件 发现MainActivity.smali里有一个感兴趣的函数getPwdFromPic()，那么我们就对它下断以跟踪APP的运行。

在IDA里搜索字符串getPwdFromPic，发现onClick有调用该函数

我们在onClick 函数开始位置按F2下断如图：

![enter image description here](http://drops.javaweb.org/uploads/images/6691a1bc6253b0eecc99cdb4bf22590a1ed1cbac.jpg)

然后点击上图中绿色三角形按钮启动调试如图：

![enter image description here](http://drops.javaweb.org/uploads/images/168dbdac0ca00677cbc9c8b42b07bf325f183e8f.jpg)

调试过程中有一个问题出现了很多次，浪费了我大量的时间，就在写文章的时候，操作时还是遇到了这样的问题。就是点击启动后IDA提示can’t bind socket，琢磨了很久终于找到原因了，当打开过一次DDMS后 每次启动Eclips都会启动DDMS 而8700端口正是被这个DDMS给占用了，然后每次都会启动失败，解决办法就是 虚拟机运行起来后关闭掉Eclips，这时一切就正常了！

事例中是一个APP crackme 提示输入密码才能进入正确界面。这个时候我们输入123，点击登陆，IDA中断在了我们设置断点的地方，这时选中ida->debugger->use source level debugger，然后点击ida->debugger->debugger windows->locals打开本地变量窗口，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/88a8de286543c08b32f88340a8a795163ce595e1.jpg)

然后按F7或F8单步跟踪程序流程，同时可以观察到变量值的变化，也可以在IDA右键选择图形视图，可以看到整个APP执行的流程图:

![enter image description here](http://drops.javaweb.org/uploads/images/721001dff86375cd66ae1edaf4e67ec5cfb74db6.jpg)

如上图所示 变量窗口中我们输入了123 被转化成的密码是么广亡，pw变量也显示出了正确的密码，其实这个时候已经很容易判断出正确密码了。

0x03 Andoid原生动态链接库动态调试
======================

通常为了加密保护等措施，有时dex执行过程中会调用动态链接库文件，该文件以so为后缀，存在于APP文件包里。

![enter image description here](http://drops.javaweb.org/uploads/images/d9dbcf68c516699a0b911ce3175679bdd8a32ce1.jpg)

这里我们以动态附加的方式来调试原生库。

3.1 准备工作
--------

1、将IDA->dbgsrv目录下的android_server拷贝到虚拟机里，并赋予可执行权限

DOS命令分别为：

```
adb shell pull d:\ android_server /data/data/sv
adb shell chmod 755 /data/data/sv

```

2、启动调试服务器android_server

命令：`adb shell /data/data/sv`

服务器默认监听23946端口。

3、重新打开DOS窗口进行端口转发，命令：

`adb forward tcp:23946 tcp:23946`如图：

![enter image description here](http://drops.javaweb.org/uploads/images/dce2623bc6d344b7b496970a847df6730cafd54f.jpg)

3.2 利用IDA进行动态调试
---------------

1、虚拟机里启动要调试的APP 2、启动IDA，打开debugger->attach->remote Armlinux/andoid debugger

![enter image description here](http://drops.javaweb.org/uploads/images/aa871991b0a92af5b835421b222f140470bff9e7.jpg)

端口改为23946 其他保持不变，点击OK

![enter image description here](http://drops.javaweb.org/uploads/images/2d70759e3dfec2d1da370f1a61190fdbdb0dc098.jpg)

如上图，选中要调试的APP 的数据包名，然后点击OK。

正常情况下，IDA会把APP进程挂起。

3、由于当前程序不是在动态链接库领空，这时我们要重新打开一个IDA，用它打开需要调试的so文件，找到需要下断的位置的文件偏移，并做记录，然后关闭后面打开的这个IDA。

4、在原IDA界面按下ctrl+s键，找到并找到需要调试的so，同时记录该文件的加载基址。然后点击OK 或者cancel按钮关闭对话框。

5、按下快捷键G 输入基址+文件偏移所得地址，点击OK 就跳转到SO文件需要下断的地方，这时按下F2键设置断点。当APP执行到此处时便可以断下来。

3.3 在反调试函数运行前进行动态调试
-------------------

程序加载so的时候，会执行JNI_OnLoad函数，做一系列的准备工作。通常反调试函数也会放到JNI_OnLoad函数里。进行4.2中第2步时也许会遇到如下情况：

![enter image description here](http://drops.javaweb.org/uploads/images/dd5a9288239d43a4bb74952f2e3f85eb6c4413c3.jpg)

这时APP检测到了调试器，会自动退出，那么这时调试策略需要有所改变。

接着4.1第3步后，在DOS命令行执行命令：

```
adb shell am start -D -n com.yaotong.crackme/com.yaotong.crackme.MainActivity    

```

来以调试模式启动APP 如图：

com.yaotong.crackme是APP包名称，com.yaotong.crackme.MainActivity是执行入口 这些可以用APK改之理查看。

![enter image description here](http://drops.javaweb.org/uploads/images/be0a02dd95596c4b22dc109858c25216007a4e5b.jpg)

这时由于APP还未运行，那么反调试函数也起不了作用，按照4.2中第2步把APP挂起。这时IDA会中断在某个位置

![enter image description here](http://drops.javaweb.org/uploads/images/7714d8f7ac96f3e1c138b5efb22d16698bf8f857.jpg)

然后点击debugger->debugger opions设置如下：

![enter image description here](http://drops.javaweb.org/uploads/images/c4035c81449393ca060e82ce62e77ec666444184.jpg)

点击OK 后按F9运行APP，然后再DOS命令下执行命令：

```
jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700

```

这时APP会断下来，然后按照4.2中的3、4、5补找到JNI_OnLoad函数的地址并下断，然后按F9 会中断下来。然后便可以继续动态跟踪调试分析。

0x04 主要参考资料
===========

* * *

1、《Andoroid 软件安全与逆向分析》

2、看雪论坛安卓安全版

3、吾爱破解论坛安卓版

感谢看雪论坛好友：我是小三、QEver、非虫等的热心指教！