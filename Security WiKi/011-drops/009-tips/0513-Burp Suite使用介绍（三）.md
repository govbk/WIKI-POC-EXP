# Burp Suite使用介绍（三）

0x01 Android虚拟机 proxy for BurpSuite
-----------------------------------

* * *

### 安卓虚拟机工具

这里我使用的是谷歌安卓模拟器Android SDK,大家可以根据自己的系统来定，我使用的是window64系统，大家选择下载的时候可以注意一下，同时也是使用这个系统来演示。下载地址：http://developer.android.com/sdk/index.html

### 配置Android模拟器

下载后，里面有SDK的manager.exe和其他文件夹。现在，我们建立一个模拟器，可以通过Android SDK管理器来创建我们的AVD（Android的虚拟设备）; 这将是我们虚拟的Android手机。

1、设置安卓虚拟机如图

![enter image description here](http://drops.javaweb.org/uploads/images/db7637b2d88c47dbc1f664e348df37bab698df45.jpg)

2、选择TOOLs下的Manager AVDS

![enter image description here](http://drops.javaweb.org/uploads/images/696a1e0d5a32d8b0bd4c609255aed7ca0bfd4aa7.jpg)

3、启动之后，设置如下配置

![enter image description here](http://drops.javaweb.org/uploads/images/b2d77de86a0f92043d1a42d8c6f3238306fd78d8.jpg)

4、通过Start开启安卓虚拟机

![enter image description here](http://drops.javaweb.org/uploads/images/2b09b47b5182ad3bae7d2a6b44c91747da1b254b.jpg)

5、界面如图

![enter image description here](http://drops.javaweb.org/uploads/images/b6010335285d68f13b5f186f78f538df9f8b1562.jpg)

### 配置代理

1、Burp代理设置如下

![enter image description here](http://drops.javaweb.org/uploads/images/902b4e18ed0de5d251b253973b96a22852979085.jpg)

2、安卓模拟器设置，Menu>System setting>More>Mobile networks>Access Point Names> 选择默认的APN或者新建一个并且设置为默认代理

![enter image description here](http://drops.javaweb.org/uploads/images/aabe2e3a27442c8a2bcbe1e4fdec811790b8b100.jpg)

3、保存好了之后打开浏览器输入地址

![enter image description here](http://drops.javaweb.org/uploads/images/38833eaa9c26fc4b6136722c8f10495e73158f66.jpg)

最后附上刚下载的一个百度知道应用程序，也是可以抓包的

![enter image description here](http://drops.javaweb.org/uploads/images/ea727d766007ad458b3823dfad61e5282f89385b.jpg)

具体详情参考：http://resources.infosecinstitute.com/android-application-penetration-testing-setting-certificate-installation-goatdroid-installation/

0x02 Android手机Proxy for Burpsuite
---------------------------------

* * *

### 准备条件

首先安卓手机要跟电脑同一个网段，连接到同一个wifi下就可以了，我这里 网关是192.168.1.1 物理机 192.168.1.5 手机ip 192.168.1.2

### 配置

1)手机设置： 打开手机-->设置->WLAN-->选择你的wifi进入编辑，在代理这里设置为手动，设置如下 主机名：192.168.1.5 //也就是我物理机的ip 端口：8088 保存即可。

2)Burp Suite设置

![enter image description here](http://drops.javaweb.org/uploads/images/a30a4463e2e323f1a8b0485845329f1d862c2455.jpg)

### 导入证书到手机中

导入证书到手机中其实也很简单，就是把电脑上已经安装好的证书导出来到内存卡中，然后从内存卡中安装证书

![enter image description here](http://drops.javaweb.org/uploads/images/e0379506220df44fb5312fccf526cfb21f2fee19.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8bc9be3412b4089823bfdabd4b6c0c1316630f77.jpg)![enter image description here](http://drops.javaweb.org/uploads/images/337f35e39f7c0912369789414605e543f89efda7.jpg)

然后命令为PortSwigger CA导出到桌面，复制到内存卡中步骤如下： 打开手机-->设置-->安全和隐私-->凭据存储-->从存储设备安装,选择你刚才证书存放的路径，安装即可。 如果安装好了，就可以在安全和隐私-->凭据存储-->受信任的凭据-->用户下即可查看到

0x03暴力破解
--------

* * *

### 0-9,a-z情况

选择Payload type里的Brute forcer（暴力破解）,在下面Payload options选项会出现组合的一些字母或数字，可以自己加，比如一些特殊字符什么的，生成的字段长度范围Min length-Max length，比如这里我只是需要4个，那就两个都写4。

![enter image description here](http://drops.javaweb.org/uploads/images/16d25fb89d0390ef808062e39442646f597939b6.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/08b185879eb7ba416ecf73cbc3beb3fea118708f.jpg)

### 用户名自动生成

根据提供的用户名然后进行拆分

![enter image description here](http://drops.javaweb.org/uploads/images/a2011ed97f329ef87c273e0310b029b87e3d2ad4.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/25b2864ab8119dd36026b3123bb42858049826bb.jpg)

### 日期型爆破

年月日都可以自己定义，有几种可选，如下

![enter image description here](http://drops.javaweb.org/uploads/images/b831cfd02ff9390606fe2a241dd689029d0e82ea.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/aa7077a2c3c82341c8e6cdb772df38ef9913c144.jpg)

### 编码frobber

说白了就是第二个值会替换前一个值

![enter image description here](http://drops.javaweb.org/uploads/images/be61ae0ce9992b3405d9c20dab2d2671c708ff3b.jpg)

0x04 导出符合爆破规则的数据
----------------

* * *

### 查找符合结果的数据

比如我想把Length为1310的数据导出来，则可以先对length排序下，然后选择length为1310的所有数据右击选择高亮(随便选择一种颜色，除了白色，默认情况是白色)

![enter image description here](http://drops.javaweb.org/uploads/images/a010beaef3430ac8b5559cc63d69b4df87a6f98a.jpg)

### 筛选出符合的数据

点击Filter，勾选show only highlighted items(表示显示仅仅显示高亮项)

![enter image description here](http://drops.javaweb.org/uploads/images/8337f9d6d3281c053e51e6bcef6280e68f2ee341.jpg)

同理也可以在上述步骤中选择添加注释(add commented),这里就应该选择show only commented items

### 导出结果

如满足以上操作，即可选择Save-->Result table，即弹出如下窗口

![enter image description here](http://drops.javaweb.org/uploads/images/0950d4529a55d7629c0f28c1305cb09da4f4903d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c9aa3c422b943a43d7b8c1c4fe7c4f8aa290bbf8.jpg)

这里all rows是保存你所有选择的到的结果，selected rows是导出你选择的数据， Save header row如果勾选，则保存导航字段名，Delimiter表示字段之间以什么相隔开tab--一个tab键，Custom--自定义 下面有一些就是保存的时候需要保持什么就勾选，反之。

0x05 批量md5解密
------------

* * *

### 准备

我们把需要爆破的md5值或者其他的需要爆破的同一放到一个txt文本里，这里我随便加密了几个放到里面

![enter image description here](http://drops.javaweb.org/uploads/images/0eaa5853e0ed2597941df3b680d0e88d2953f323.jpg)

以www.cmd5.com网站为例做的批量解密 首先，还是同样的设置好代理之后访问www.cmd5.com,然后抓包

![enter image description here](http://drops.javaweb.org/uploads/images/e59eb144008de0e2d4221922dc9e4b0909a9c597.jpg)

在密文处其实可以随便写什么，但是为了便于我们后面能够直接看出解密出的值我们还是写一个正常的。

### 设置intruder

通过抓包到的数据我们可以看出我们填写的密文在哪

![enter image description here](http://drops.javaweb.org/uploads/images/b7e3cf951bd53bf2452fdb52ee6c88ef73889404.jpg)

发送到repeat先，把我们想要的结果匹配到

![enter image description here](http://drops.javaweb.org/uploads/images/e3e6b55c82f9c5f9046b1af023fd5049dc718e51.jpg)

接着我们发送到intruder,设置我们输入的值两边加上$

![enter image description here](http://drops.javaweb.org/uploads/images/1865a40a7f8f6b0a9ddaab722f4a2c993f9f701e.jpg)

选择字典

![enter image description here](http://drops.javaweb.org/uploads/images/52a31c8181beb0e4d84a435beba2321b8d4c4c1e.jpg)

再调节一下线程，最好是调低一点，太高了可能会解密失败，而且设置解密失败重试2次最好了

![enter image description here](http://drops.javaweb.org/uploads/images/031e505b1722fb4bba0c3e5b51eaf2beac482cee.jpg)

匹配解密出的结果

![enter image description here](http://drops.javaweb.org/uploads/images/23a8b1ffaa97daac39d89a6888fa0e115ba3e63a.jpg)

### 开始解密

点击start attack

![enter image description here](http://drops.javaweb.org/uploads/images/f7c3b3b477eb90d87bc1bca15680af51da16e3df.jpg)

解密效果，后面导出就不用讲了，看过前面的应该就知道怎么导出想要的结果。