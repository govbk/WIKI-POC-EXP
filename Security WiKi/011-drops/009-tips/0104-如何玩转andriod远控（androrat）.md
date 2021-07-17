# 如何玩转andriod远控（androrat）

[关于WebView中接口隐患与手机挂马利用](http://drops.wooyun.org/papers/548)的引深

看我是怎样改造Android远程控制工具AndroRat

```
1.修改布局界面
2.配置默认远程ip和端口
3.LauncherActivity修改为运行后自动开启服务并自动返回到主界面
4.修改xml让程序不显示在最新使用的程序

```

0x00 搭建andriod环境
----------------

* * *

对于小白来说，首先需要的开发环境是必须

```
1.eclipse
2.jdk
3.sdk

```

安装配置好后就将我们的AndroRat工程导入eclipse中

导入完成后看见2个工程如图：

![2013090815203427803.jpg](http://drops.javaweb.org/uploads/images/d11acb09d761ef76ca501b4d22764b7e6d3e30af.jpg)

刚导入进来时肯定会编译报错，这时需将2个jra包引用进来 如图：

![2013090815230469611.jpg](http://drops.javaweb.org/uploads/images/6784e25054beaffe480da55eafa1d90ec6dc50ff.jpg) 

其他报错如import 缺少对应包可到[http://www.findjar.com/index.x](http://www.findjar.com/index.x)查找并引用

编译错误解决完成后就会出现黄色感叹号，这个时候2个工程就可以运行了。

0x01 安装androrat
---------------

* * *

先运行我们的服务端开启监听 默认config.txt配置端口

![2013090815334573925.jpg](http://drops.javaweb.org/uploads/images/d1b15116e7fcc6682c9ffb3386343cb75a4bb429.jpg)

运行成功后出现服务端如下：

![2013090815353936194.jpg](http://drops.javaweb.org/uploads/images/581316cb4d70d049bf66ac687a9b074924be2223.jpg)

接着运行客户端，使用usb链接我们的手机安装app查看

![2013090815295584722.jpg](http://drops.javaweb.org/uploads/images/bdf7a13eef6c5c3d0ce752f6cafa474d9e929a44.jpg)

安装好后应用列表会有一个叫LogsProvider的应用，可以在如下文件里修改name

![2013090815434447913.jpg](http://drops.javaweb.org/uploads/images/fa1731cd95153b11b5edf77f775dbb53e8fa3a05.jpg)

接着修改LauncherActivity.class代码让程序默认情动并运行后自动black

![2013090815490412471.jpg](http://drops.javaweb.org/uploads/images/798881503dc7905294833de6aaa7fb7c42b4902e.jpg)

Manifest修改，使其不在home最近应用里显示

![2013090816033950681.jpg](http://drops.javaweb.org/uploads/images/719a4cda830fee7fe157f08137dd6db5a34bec78.jpg)

布局文件位置，可以自定义修改布局

![2013090815511471104.jpg](http://drops.javaweb.org/uploads/images/6cffaa436587f2e4903a04dcd79d38389c4ef28a.jpg)

adb 安装运行客户端后，服务端如图，-手机安装程序后会自动返回到桌面，长按home也看不到该程序。

![2013090815541350530.jpg](http://drops.javaweb.org/uploads/images/0797320aa5739642a2241decb169a9724f55cdbb.jpg)

此时整个程序可以使用了，功能挺多的就不列举了

0x02 引申思考
---------

* * *

1.如把修改app写成服务，监听短信指定代码开启端口 （老外都这样干的）

2.andriod里的gps功能和拍照功能有bug 这可是两个亮点功能，擦

3.实现程序的自动编写，屏蔽扫描杀软，自我复制和感染文件（这还是留个大牛们研究）

[http://url.cn/Ke7wxT](http://url.cn/Ke7wxT)微云源码分享地址