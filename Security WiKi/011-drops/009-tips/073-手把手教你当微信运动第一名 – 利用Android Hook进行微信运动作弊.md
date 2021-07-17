# 手把手教你当微信运动第一名 – 利用Android Hook进行微信运动作弊

0x00 序
======

* * *

随着带协处理器和买手环的人越来越多，微信运动一下子火了，只要你在微信关注微信运动，手机就能自动记录你每天行走的步数，还可以跟朋友圈里的好友PK运动量。并且每日排名第一的用户可以占据当日排行榜的封面。这充分激起了大家的求胜的欲望，于是出现了很多励志的和悲伤的故事……

![enter image description here](http://drops.javaweb.org/uploads/images/d9dc7859813e19cfe396e593567d972828fcd0e1.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/3f096d7ed244695c59212e57befc74f6b7a7c2bd.jpg)

0x01微信运动作弊大法
============

* * *

其实想要拿第一没有那么麻烦，只要会一点Android的Hook知识，就可以轻松冲到排行榜第一名。接下来我就手把手教你如何变成第一。

首先我们需要一台带协处理的root后的android机器，比如说nexus 5。然后我们装上作弊用的XPosed Hook框架和作弊插件。这两个apk可以在我的github上下载到。

[https://github.com/zhengmin1989/WechatSportCheat](https://github.com/zhengmin1989/WechatSportCheat)

下载完后，先安装`XPosed.apk`。接着打开Xposed，选择“`安装/更新`”，然后根据提示重启手机。

![null](http://drops.javaweb.org/uploads/images/037449dd5f3c151b76d96139a95d86ebf1b657a3.jpg)

重启完后，再安装`xposedwechat.apk`插件。然后打开Xposed的模块界面，会看到xposedwechat这个插件。我们在这里将它选中，然后再根据提示重启手机。

![null](http://drops.javaweb.org/uploads/images/bbbdec8aedbed9caae690b5051139f0511b581fc.jpg)

接下来就是见证奇迹的时刻…你随意走两步，然后打开微信运动，咦，怎么就多了1000步？再随便走几步，咦，怎么又多了1000步？… demo视频如下：

仅仅刷步数还是不够过瘾吧？微信运动还推出了益行家活动，可以用每天的步数换取爱心捐款。有了微信运动作弊大法，我们可以每天在家随便走几步然后换取爱心捐款（如图所示）。

![null](http://drops.javaweb.org/uploads/images/e75b5a5c1e3380aba59b6393e1d85a4b0d222fb8.jpg)

0x02 微信运动作弊原理
=============

* * *

我们是如何作弊的呢？简单来说，当微信运动想要知道我们走了多少步的时候，微信app会询问android系统的计数传感器，随后计数传感器会返回我们行走的步数。因此，如果我们能够拦截微信运动和计数传感器之间的对话，然后伪造一个步数传递给微信运动就可以达到我们想要的作弊效果。

具体怎么做呢？首先我们可以用Xposed框架来hook计数传感器的队列函数`dispatchSensorEvent()`，这个函数在`android.hardware.SystemSensorManager$SensorEventQueue`这个类中。随后在微信运动每次询问行走步数的时候，我们先获取当前步数，然后在目前的步数的基础上加1000步，然后将信息返回给微信运动。微信运动就会误以为我们运动了1000步，从而达到了欺骗的效果。

关键代码如下：

首先`hook android.hardware.SystemSensorManager$SensorEventQueue`这个类的`dispatchSensorEvent()`函数：

```
final Class<?> sensorEL = findClass("android.hardware.SystemSensorManager$SensorEventQueue",lpparam.classLoader);
XposedBridge.hookAllMethods(sensorEL, "dispatchSensorEvent", new XC_MethodHook() 

```

接着我们在记步传感器把步数信息返回给微信运动之前，将返回的步数加上1000步：

```
protected void beforeHookedMethod(MethodHookParam param) throws
Throwable {
XposedBridge.log(" mzheng  Hooked method: " +  param.method);
 ((float[]) param.args[1])[0]=((float[]) param.args[1])[0]+1000*WechatStepCount;
WechatStepCount+=1;
…

```

另外我们还可以使用一些传感器的接口获取一些数据的信息：

```
Sensor ss = ((SparseArray<Sensor>) field.get(0)).get(handle);                            
XposedBridge.log("   SensorEvent: sensor=" + ss);

```

![enter image description here](http://drops.javaweb.org/uploads/images/1595c859f1d6b0b68aac045587339c97c875cb9f.jpg)

比如说x就代表开机以来行走的步数，timestamp是获取步数时候的时间戳等。

另外，我们不仅在android上可以hook计步器，在iOS上也是可以通过越狱后hook iHealth的API接口达到同样的作弊效果，有兴趣的同学可以继续研究。

![null](http://drops.javaweb.org/uploads/images/5b0be18eb8c56c7ef8f93ad1b0705d4dba889267.jpg)

![null](http://drops.javaweb.org/uploads/images/70eae80dd7ca65d3c3ea9246c07046cf7b1d5035.jpg)

0x03微信运动反作弊建议
=============

* * *

如何防止这种作弊发生呢？我的第一个建议是加强服务器端的逻辑检测功能。比如说一个人是不可能十分钟内走一万步的，如果他做到了，那么他一定是在作弊。 我的第二个建议是增加对hook的检测功能。虽然微信运动作下弊无非就是满足一下大家争强好胜的虚荣心，并不会对大家的隐私和财产产生损失。但是既然微信运动可以被hook，同样也意味着语音聊天，微信支付等功能也是可以被hook的，当黑客利用hook技术对你的隐私和财产产生危害的时候可就不是那么好玩的事了。之前我们在Hacking Team事件中也亲眼目睹了利用hook技术来获取微信语音消息的android木马，所以一定要增加针对hook的检测才行。

0x04 总结
=======

* * *

此文只是介绍了Android Hook的简单场景应用，关于Android Hook的原理以及更多的利用方式，比如说调试，关键API拦截，外挂等技巧，敬请期待WooYun Book系列的文章《安卓动态调试七种武器之离别钩 - Hooking》。 https://github.com/zhengmin1989/TheSevenWeapons

0x05 参考文章
=========

* * *

1.  [Android.Hook框架xposed篇(Http流量监控)](http://drops.wooyun.org/tips/7488)
    
2.  [人手一份核武器 - Hacking Team 泄露（开源）资料导览手册](http://drops.wooyun.org/news/6977)