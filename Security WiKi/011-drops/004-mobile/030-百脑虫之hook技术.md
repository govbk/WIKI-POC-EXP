# 百脑虫之hook技术

**Author：360移动安全团队**

0x00 背景
=======

* * *

2015年末爆发了感染量过百万的“百脑虫”手机病毒，经过360移动安全团队深入的跟踪和分析，我们又发现了病毒的另一核心模块，此模块包括3个ELF系统文件configpppm、configpppi、configpppl和一个伪装成系统应用的核心apk文件以及一个configpppl.jar文件。我们发现这些模块都使用之前发现的conbb(configopb)执行命令。在新发现的模块中，病毒使用了更高超的技术，可以在用户毫无察觉的情况下修改短信内容恶意扣费，从而非法获益。

0x01 传播途径
=========

* * *

此病毒母体一般都是寄生在色情应用或者手机预装，这类色情应用都是没有什么实质上的内容，只是图标和名字很诱人而已，诱导下载安装病毒。一旦安装，病毒也就找到了宿主，即使卸载这类应用，病毒母体也不会被卸载。每次手机开机，病毒都会启动，即使手机恢复出厂设置病毒也不会被清除。

0x02 病毒行为概述
===========

* * *

一、恶意扣费（**针对移动应用商城，APP应用厂商背黑锅**）

病毒注入所有APP应用，在APP应用进行短信订购支付时，病毒判断是否是包含移动应用商城模块，然后替换支付内容，导致用户支付后也没有得到应有的功能，APP应用厂商也没有充值记录，导致用户认为APP应用厂商的程序有问题。这样，病毒偷了钱还嫁祸给应用厂商而且用户也无法察觉已中毒。

二、云端服务器加载恶意代码

核心功能classes.dex文件存放在云端服务器，这样做对幕后黑手的好处有以下几点：

1、随时更新功能：可能今天执行扣费指令，明天执行盗取银行密码、支付宝密码指令，后天安装各种APK应用等等，潜在危险巨大。

2、难以取证：幕后黑手发现被盯上，随时可以关闭服务器或改为正规功能，不会留下恶意扣费的相关证据。

三、修改系统核心文件

手机系统易死机，应用启动迟缓。

四、技术手段高超

注入zygote修改framework需要对安卓手机底层了解非常透彻才能有如此大作，推测是分工明确的团队产品。

0x03 病毒详细分析
===========

* * *

病毒框架大体流程如下：

![](http://drops.javaweb.org/uploads/images/3df469a5778ae9914c13766617ff75a1a931f8ec.jpg)

图【1】:框架流程

![](http://drops.javaweb.org/uploads/images/455c81c19131d09c14dac04976d9889c490beb8c.jpg)

图【2】:注入zygote

![](http://drops.javaweb.org/uploads/images/3eea15942ba21b3f4a662ccae30c4600c3c6dd6a.jpg)

图【3】:病毒jar模块功能

1.诱惑应用释放病毒母体文件或手机预装就存在病毒，病毒下载运行云端核心DEX文件，执行核心功能函数crackZygoteProcess()。

2.木马加载libconfigpppm.so动态库，调用导出函数configPPP()测试修改framework内容是否可行；

![](http://drops.javaweb.org/uploads/images/07a2466b1f9a8509a90ca39ba53f929e2b11de65.jpg)

图【4】:调用configPPP()

3.root权限运行configpppi.so，参数为Zygote进程的PID，修改Zygote进程；

![](http://drops.javaweb.org/uploads/images/feaab7769b284c54d1c8716b867bd064071903d8.jpg)

图【5】:运行configpppi

4.创建一条线程检测"com.android.phone"进程并结束，此进程为系统核心进程，被结束后会自动启动，重新启动后的“com.android.phone”就被注入了病毒模块；

![](http://drops.javaweb.org/uploads/images/132a4cc2026071e62923fc36a7c18af901878d5b.jpg)

图【6】:重启"com.android.phone"注入病毒jar模块

5.杀死360、金山等杀毒软件，永久删除。

![](http://drops.javaweb.org/uploads/images/53f2f3428bab2bad7163aa8bb328314970757418.jpg)

图【7】:结束各种杀毒软件并删除.

6.病毒JAR注入所有APK，等待时机恶意扣费。

以上操作完成之后，以后启动的每个APK应用都会加载病毒模块，从QQ、支付宝、微信、银行app到各种手机游戏，病毒可以随意操控程序流程。

**举个栗子-中毒后最终效果**：

我的移动手机已经中毒并且在“移动应用商城”官网下载了“捕鱼达人”，畅玩游戏时想花点钱升级VIP或者买个道具（此时病毒注入游戏），进行消费支付提示后，游戏币却没有充值成功，然而却被扣费，此时我一口咬定游戏厂商应用出了问题，明明扣费却不给道具。而实际上，病毒在支付的时候就把支付内容修改，最终导致用户和APP应用厂商相互误解。

![](http://drops.javaweb.org/uploads/images/201ef1af75b690b44b6b82a1eb43c171b3f45f66.jpg)

图【8】:病毒导致应用厂

商背黑锅

**详细分析核心模块**：

我们详细分析一下libconfigpppm、configpppi、configpppl是怎么注入安卓进程并HOOK Android世界的。

![](http://drops.javaweb.org/uploads/images/8a44b7bb64f3949a56812a4807eb9122da2014d4.jpg)

图【9】:修改zygote方法

一、libconfigpppm.so测试修改framework:
--------------------------------

1.首先，病毒加载libconfigpppm.so，调用configppp()导出函数。

2.木马从"/proc/self/maps"加载地址中，通过名称和路径从系统中遍历寻找有后缀的文件，保存文件的地址范围和路径。图

【10】

(maps是安卓进程的内存镜像)：

![](http://drops.javaweb.org/uploads/images/9dee0d61039f00ad70dd257085d2a3f1b4142354.jpg)

图【10】:maps信息

![](http://drops.javaweb.org/uploads/images/d807c24bedbaa7cfda76691a3c7f727790de67d7.jpg)

图【11】:保存文件的地址范围和路径

3.在maps中定位到`system@framework@framework.jar@classes.dex`或者framework.odex

4.从系统中读取framework文件并且和已经加载的framework进行比较，定位framework在内存中的位置。比较内容如下：

```
1. 读取framework大小，将文件分成16个块
2. 读取每个块的前8个字节
3. 将这8个字节的二进制与加载到内存中的framework对应位置的二进制进行比较

```

![](http://drops.javaweb.org/uploads/images/6ec1c9a072ca517e5ccf280e60e6a92d3f79fe93.jpg)

图【12】:对比内存和系统中的framework

5.如果比较失败，configppp中止执行并返回一个103错误代码。如果比较成功，木马开始在内存中修改framework。病毒通过dexFindClass和dexGetClassData函数得到"android/app/ActivityThread"的结构。通过遍历这个结构找到main，再通过dexGetCode函数获得字节码，然后与系统中文件相应的字节码进行比较，从而检查framework是否已被修改。如果已被修改，病毒会终止运行返回103错误代码；否则定位到main函数位置写入system.load("/system/bin/configpppl.so")进行修改如下：

```
1A 00 [strID, 2 bytes]                    //const-string v0, “/system/lib/libconfigpppl.so” 
71 10 [methID, 2 bytes] 00 00      //invoke-static {v0}, Ljava/lang/System;->load(Ljava/lang/String;)V 
0E 00                                             //return-void

```

然后保存修改相关的信息到"`/data/configppp/cpppimpt.db`"，通过configopb.so去执行root命令。

![](http://drops.javaweb.org/uploads/images/69a9ccbd45c8fd8cdff5c30b0787949d870ec03c.jpg)

图【13】:修改自身framework

二、configpppi.so修改zygote:
------------------------

configpppi用来修改zygote中的framework，Zygote进程的作用是启动安卓程序的守护进程。它通过`/dev/socket/`zygote来接收调用程序的命令，所有启动请求都会通过fork()执行。一个进程调用fork()后，系统会把原来的进程的所有值都复制到新的进程中，只有少数值与原来的进程的值不同，相当于克隆了一个自己。**如果zygote的framework被修改，那么所有启动的APP都存在修改的zygote的克隆体。**

1.configpppi的main函数如图，参数为Zygote的PID：

![](http://drops.javaweb.org/uploads/images/a2b70c077e35b0c732ba9d7499542f043c7a5289.jpg)

图【14】:

main()函数入口图

2.通过ptrace操作zygote进程：

![](http://drops.javaweb.org/uploads/images/90511885bd4ae78293b041f9069316c6e71e8098.jpg)

图【15】:ptrace zygote

3.读取libconfigpppm保存的cpppimpt.db中的数据：

![](http://drops.javaweb.org/uploads/images/089d8b492b3cd126d502d1859239d7e0fb3947be.jpg)

图【16】:读取数据

4.根据cpppimpt.db中的数据修改zygote中framework，完成对zygote的修改。

![](http://drops.javaweb.org/uploads/images/ce94b11a05c7f0bc4485cb956a997d5fa921c6dc.jpg)

图【17】:修改zygote

以上操作完毕后，以后再启动任何APP，都将被注入病毒模块。如下图：

![](http://drops.javaweb.org/uploads/images/f3dc8e2ffc8d1c5ff321ead2195c56e2807df6f5.jpg)

zygote修改前

**zygote修改后**

![](http://drops.javaweb.org/uploads/images/559de47b68d3f44bce7f856a0ba6c05783567fb6.jpg)

图【18】:zygote修改前后对比

木马成功注入zygote后，每个新启动的应用都会先加载名为 configpppl.so的文件。configpppl.so的功能是加载configpppl.jar并修改系统函数。

三、 加载configpppl.jar
-------------------

在configpppl.so的JNI_OnLoad中首先会加载包含修改短信和发送短信的configpppl.jar模块

1) 加载configpppl.jar后首先调用jar中的pppMain方法

![](http://drops.javaweb.org/uploads/images/11ef990c0f7e716ed616eb3299f90a0158f33f18.jpg)

图【19】:调用pppMain

2) pppMain方法只有一个输出日志的功能，表示加载成功

![](http://drops.javaweb.org/uploads/images/f0b95ab83aa4b88f15130dc9f87f7ce56874156c.jpg)

图【20】:输出日志

四、修改系统函数
--------

### 1) hook原理

dalvik在执行函数时会先调用dvmIsNativeMethod来判断一个method是否是native方法。如果是native函数的话，那么它所指向的一个Method对象的成员变量nativeFunc就指向该JNI方法的地址，因此只要将java函数修改为native，就可以达到hook的目的。

### 2) 修改过程

要把java函数修改为native method需要以下步骤：

(1) 修改method属性为native

(2) 修改registersSize、insSize、nativeFunc、computeJniArgInfo

![](http://drops.javaweb.org/uploads/images/9a981bf6897ff4bcae26e61cba95c4a721775219.jpg)

图【21】:修改method属性

注册目标method的native函数

![](http://drops.javaweb.org/uploads/images/a5dc60fb0025a8b10137b1dceb71b820218eec25.jpg)

图【22】:注册目标函数

### 3) 修改结果

通过以上的修改程序在调用被修改的这些函数的时候就会调用作者自己在configpppl.so中定义的本地函数，被修改的本地函数以及修改的目的如下表

![](http://drops.javaweb.org/uploads/images/d90c8491dcf9a1dceec5cb2ce5310b02da88d047.jpg)

五、 木马最终目的
---------

通过上面的修改之后，在手机接到短信时，木马就可以根据短信内容和来源选择性的屏蔽掉，屏蔽的规则也是动态的，在过滤之前木马会检测规则的时效性，并且可以自主发送短信订购移动服务并修改支付短信。

以上被修改的7个函数中有两个函数特别重要：dispatchPdus和newApplication

1) dispatchPdus——屏蔽短信

当手机收到短信时，会调用接收处理短信的dispatchPdus函数。前面已经将此函数注册为本地函数，因此会调用configpppl.so中对应的函数如下

![](http://drops.javaweb.org/uploads/images/ec072f502d3800e431a1fd96482a1db852a5ddea.jpg)

图【23】: 劫持短信

可以看到函数最终调用configpppl.jar中的moduleDispatchPdus函数，在moduleDispatchPdus中会先判断短信是否需要屏蔽，若不需要屏蔽则按照原始的dispatchPdus函数流程执行

![](http://drops.javaweb.org/uploads/images/a0f47947b130ba32f2b0085ef6e38a90d68ba9c7.jpg)

图【24】:屏蔽短信

2) newApplication之onModuleCreate

跟dispatchPdus一样，newApplication被调用的时候首先调用configpppl.so中的本地函数。与dispatchPdus不同的是本地函数会先调用原始的newApplication方法，然后在调用configpppl.jar中的onModuleCreate和onModuleInit两个方法。

因为木马在之前的代码中已经修改了zygote进程，因此手机中所有的应用都将被注入configpppl.so模块。onModuleCreate方法功能就是根据上层应用初始化变量mMainAppType，初始化结果如下：

![](http://drops.javaweb.org/uploads/images/453d98b44f616c7bfc2f3fea94635ed6be624d3c.jpg)

3) newApplication之onModuleInit——篡改短信，主动发送短信

通过mMainAppType的值，木马根据上层应用的不同，将执行不同的代码：

![](http://drops.javaweb.org/uploads/images/5343a3d13f224dbacfa9ece7a380a65dc917f319.jpg)

图【25】:onModuleInit部分代码

(a) 上层应用为com.android.phone

上层应用为com.android.phone时，程序将注册两条广播：

![](http://drops.javaweb.org/uploads/images/7a7a83cc60c32b11925ed0adc6d6d2ae92128d5a.jpg)

图【26】:注册广播

当收到com.ops.sms.core.broadcast.back.open.gprs.network时程序将开启数据网络

![](http://drops.javaweb.org/uploads/images/364d8650683acaf0ecfdfbf47697933e6ce10cc4.jpg)

图【27】:"com.android.phone"收到广播开启网络

(b) 上层应用为com.android.mms或者com.android.settings

程序先注册三条广播，然后检测是否有需要发送的短信，如果有则发送出去。

当收到`com.ops.sms.core.broadcast.back.send.sms.address`广播时程序也会发送短信，短信内容从activelocal.db文件中获取。

当收到`com.ops.sms.core.broadcast.back.open.gprs.network`时程序将开启数据网络，从后面的代码中可以看到，程序会每两分钟发送一个开启网络的广播。

![](http://drops.javaweb.org/uploads/images/77d2fc085bf7888ab51988e16a958c2b4b4ad3aa.jpg)

图【28】:"com.android.settings"开启数据网络

(c) 上层应用为普通应用时，程序先判断是否为移动应用商城app

![](http://drops.javaweb.org/uploads/images/f2d7455c2fb6423132894aa9775297c2ce7d72b3.jpg)

图【29】:判断启动程序是否为移动应用商城

如果是移动应用商城app的话，调用invokeMMMain函数，否则调用invokeotherMain,这两个函数内容大体相似，只是invokeMMMain函数会检测移动应用商城app的sdk的版本并且开启线程检测网络连接，每2分钟发送一个打开网络的广播。

![](http://drops.javaweb.org/uploads/images/e303c1395561d9b7b1a44b46d624eef84ccb103b.jpg)

图【30】:发送开启网络广播

无论是不是移动应用商城app程序都会执行一个叫replaceService的函数去替换isms和isms2

![](http://drops.javaweb.org/uploads/images/64d46e210203aba901af71eb6d47b99b0fb760e7.jpg)

图【31】:替换isms

isms作为发送短信的binder，程序用自己定义的binder替换isms意味着手机发送的短信将被木马修改，再看木马自己定义的binder的内容：

修改支付短信，修改的内容是从activelocal.db文件中获得

![](http://drops.javaweb.org/uploads/images/e42fe3b946a05a09fdbe253b602acd6641d31b13.jpg)

图【32】:修改支付短信

程序先是检测短信类型是否是移动支付相关的，如果是则修改短信的CodeIMSI、号码和内容，然后调用原始的isms发送短信。

![](http://drops.javaweb.org/uploads/images/2cef3b0d390e0ac097354a09779e5a39c7a52358.jpg)

图【33】:中毒清理反馈

0x04 查杀和预防
==========

* * *

如果您发现手机异常有中毒迹象，请下载360手机急救箱清理；有用户反馈急救箱无法清理病毒，请先将手机ROOT后，再使用急救箱才可以完成清理。（推荐使用360root或kingroot等ROOT工具）

随着360手机急救箱用户数的增长，被查杀到的木马越来越多，360手机急救箱独有的深度完整扫描，可以深度扫描和完美清除底层ELF病毒和APK病毒，目前市场上的主流手机安全产品几乎没有支持ELF完整深度扫描的功能，如果您的手机刷过第三方ROM或者手机已经Root，建议您采用360手机急救箱进行一次完整的深度扫描，帮助您安全用机。

0x05 安全建议
=========

* * *

1、建议安卓手机用户不要随意开放root权限，作为安卓系统的底层权限，一旦开放root权限就意味着手机大门已敞开。为手机软件使用行方便的同时，也为手机木马行了方便。

2、日常使用手机过程中，谨慎点击软件内的推送广告。来源不明的手机软件、安装包、文件包等不要随意点击下载。

3、同时，手机上网时，对于不明链接、安全性未知的二维码等信息，不要随意点击或扫描，避免其中存在木马病毒危害手机安全。

4、养成良好的手机使用习惯，定期查杀手机木马，避免遭受潜伏在手机中的恶意软件危害。