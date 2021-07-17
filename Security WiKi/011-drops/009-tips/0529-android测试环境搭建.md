# android测试环境搭建

0x01 测试机选择：真机or模拟器
------------------

* * *

**1.1 三大主流模拟器对比**

|  | Android Emulator | Android-x86 | GenyMotion |
| --- | --- | --- | --- |
| 价格 | free | free | Free: Non-commercial Paid: Freelance, Business |
| 速度 | Slow for ARM – Faster for x86 | Fast | Very fast |
| 支持版本 | Android Virtual Devices (All android versions) | Only certain preconfigured devices, mostly tablet (Android 2.2-4.4) | Pre-configured images for many tablet & phone devices of Google, HTC, LG, Motorola, Samsung, Sony (Android 2.3, 4.x) |
| HTTP代理 | Yes (command-line option) | Yes, via GUI | Yes, via GUI |
| Transparent Man-in-the-middle | Yes – via DNS server | Yes, via Virtualbox | Yes, via Virtualbox |
| Pre-rooted | Yes | Yes | Yes |
| 虚拟机安全装时间 | 5 minutes | 15 minutes | 5 minutes |
| 相机支持 | Since Android 4.0 | Very limited | Yes |
| GPS支持 | Yes | No | Yes |
| Spoof IDs | No | No | Paid version |
| Drag&Drop Support | No | No | Yes |
| 谷歌商店 | No, but can be installed | Yes | No, but can be installed |
| 开发者工具支持 | Yes | Yes | Yes, via plugins |
| 镜像支持 | One | Offline, via Virtualbox | Offline, via Virtualbox |

**1.2 总结**

真机快功能全，模拟器成本低 有条件的话建议真机模拟器混合使用 如果用模拟器的话建议GenyMotion

0x02 探测修改流量
-----------

* * *

**2.1 http代理设置**

电脑代理：Fiddler、burp suite等

![enter image description here](http://drops.javaweb.org/uploads/images/07e3806343871d688606b3c8cd2389843572af0c.jpg)

手机代理：proxydroid等

![enter image description here](http://drops.javaweb.org/uploads/images/74ed8f6cb48e15106443015a896218ba0e22b4e2.jpg)

Proxydorid运行机制

![enter image description here](http://drops.javaweb.org/uploads/images/76654dc1b5311bfd2a8f84175f28b2274bb8ac88.jpg)

默认设置只能代理80和443的http流量，如果是其他端口的http流量就需要配置iptables转发端口到手机的8123或者8124端口上。

**2.2 Ad-hoc无线网络**

简单说就是用自己电脑开个wifi热点，这样做比直接在同LAN中设置代理的好处是，android上的代理软件不一定会把所有流量转发到pc上，如果自己pc开的热点就不会存在该问题，这样就可以用wireshark抓取这些不能代理的流量了。 设置方法如下： Dos下运行，设置热点

```
netsh wlan set hostednetwork mode=allow ssid=test key=test1234

```

控制面板里共享网络

![enter image description here](http://drops.javaweb.org/uploads/images/015ca3d9bf6d442dd274c10ea98cbac34f1ab22e.jpg)

Dos下运行开启热点

```
netsh wlan start hostednetwork

```

**2.3 ssl证书**

从fiddler中导出证书

![enter image description here](http://drops.javaweb.org/uploads/images/8b44d51a7503d9268e35e225862f2e125719c6c8.jpg)

手机中安装fiddler证书

![enter image description here](http://drops.javaweb.org/uploads/images/07a0e1f0b18faa63dd2a6b93bf3ac3bbd52f572e.jpg)

有些app自带证书，可以解包查看

![enter image description here](http://drops.javaweb.org/uploads/images/a1750042fa3086a1b8d0b1c48b328ba30c1aac3b.jpg)

然后合并导入手机中

0x03 探测修改本地存储
-------------

* * *

**3.1 Root设备**

Root后才能进入应用数据目录

**3.2 本地存储检索**

文件种类： databases - SQLite 数据 shared_prefs – 程序私有文件 cache – 缓存数据 lib – 本地库 files – 其他文件 少数应用在sd卡中也存储数据

**3.3 文件管理器应用**

ES文件浏览器（不能打开sqlite）

![enter image description here](http://drops.javaweb.org/uploads/images/8069d8fd0c570b09fbe0b1e5b815f5b71dcdef42.jpg)

RE（root explorer 能直接打开sqlite，要好用一些）

![enter image description here](http://drops.javaweb.org/uploads/images/f2de753578b7ed0b7d8b3077a40f53b1c7d453c3.jpg)

**3.4 ADB pull**

如果用的es没办法打开sqlite所以才有这步，用re的话就不需要这步可以在手机上直接查看。不过pull到pc上看起来更直观点。 Root权限才能对应用程序目录进行操作。

![enter image description here](http://drops.javaweb.org/uploads/images/7e9fbbe156c62ce193813053c350580f8c9f9aeb.jpg)

Chmod把权限改为777就可以pull到pc上查看了。

![enter image description here](http://drops.javaweb.org/uploads/images/24b5637d3cc21f84b3a3996994ca6195b6d71af1.jpg)

**3.5 SSH root server**

安装SSHdroid，设置好参数即可远程ssh上android设备。

![enter image description here](http://drops.javaweb.org/uploads/images/9954db87f511aff72ec3399c9fb9a8cd45adc2f3.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/2a9c872947965b152821be11e7302a88e3ba49fc.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/60a2d742b55f6448a63efe17b38c0ba3f1ee491b.jpg)

**3.6 快照分析**

通过快照进行差异对比能够快速发现一些本地存储的敏感信息。

在进行操作如输入用户信息前拍下应用目录快照，就是复制一下。

![enter image description here](http://drops.javaweb.org/uploads/images/ad0c42e0f7a42d1268fcd4a41ff47d7bfdbfb4ee.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/489658d8ff660dfacb4230528cebe1388c8966c6.jpg)

然后进行进行登陆操作拍下再拍下快照

![enter image description here](http://drops.javaweb.org/uploads/images/63bfed6e21631ea085fa25b3b0a4bda3c76684f7.jpg)

最后用diff比较两次快照

![enter image description here](http://drops.javaweb.org/uploads/images/43c954c9898cf2be68fbc579ca85d16c744da68f.jpg)

总结：这种方法适合文件较多的应用，文件少的应用直接观察文件修改时间，然后进行查看。

**3.7 常见漏洞**

不必要的敏感信息存储 敏感信息明文存储在外置设备如sd卡中 敏感信息明文存储在私有目录下 用弱加密算法加密敏感数据 加密敏感数据用程序的硬编码的静态密钥 加密敏感数据的动态密钥存储在全局可读或者私有目录下

0x04 案例
-------

* * *

Logcat信息泄漏

[WooYun: 光大银行Android手机客户端密码明文泄漏](http://www.wooyun.org/bugs/wooyun-2012-014590)

shared_prefs信息泄漏

[WooYun: 苏宁易购用户敏感信息泄露](http://www.wooyun.org/bugs/wooyun-2012-014308)

[WooYun: 百度安卓设计不当重要资讯泄漏](http://www.wooyun.org/bugs/wooyun-2014-054438)

明文传输

[WooYun: 微付通Android客户端敏感信息明文存储](http://www.wooyun.org/bugs/wooyun-2014-053037)

ssl证书失效

[WooYun: 中信银行"动卡空间“Android客户端缺陷导致用户名密码等信息被劫持](http://www.wooyun.org/bugs/wooyun-2013-027985)