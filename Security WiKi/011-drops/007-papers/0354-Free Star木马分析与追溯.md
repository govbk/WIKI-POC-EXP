# Free Star木马分析与追溯

**Author:360天眼实验室**

0x00 引子
=======

* * *

人在做，天在看。

360天眼实验室一直与各种木马远程做斗争，对手总是试图找到办法使自己处于安全监视者的雷达之外。近期我们看到了一些较新版本的大灰狼木马采用了一种新的上线方式，与利用QQ空间、微博、博客或者网盘等方式上线相似，其通过调用QQ一个获取用户昵称的接口来获取上线地址，又一种通过正常通信渠道进行非正常通信的企图。

![p1](http://drops.javaweb.org/uploads/images/d117639cfe3f0d341618d70729692ffa6d8c495d.jpg)

![p2](http://drops.javaweb.org/uploads/images/8fe9f22cc411b350d9e9348e85f46f78e1c094f6.jpg)

当一个方法被证明有效，很容易就会被其他造马者“借鉴”。通过基于360威胁情报中心数据的关联性分析，我们发现了一个名为Free Star的木马也采用了这种上线方式，该木马最早出现于2015年2月左右，作者从2015年5月开始在各个免杀论坛售卖源码，而新版本活动时间就在2016年1月份至今。其部分代码结构和Gh0st、大灰狼的代码比较相似，可以认为是那些远控的衍生版本。

下图为从某免杀论坛下载到的Free Star木马控制端，可以看见配置Server端中需要将IP地址加密后设置成QQ昵称，然后由服务端通过访问对应的接口来获取QQ昵称，进而解密出木马上线的IP地址：

![p3](http://drops.javaweb.org/uploads/images/ce3ce15f1fbc21451822c7cb4c7a8fcc2c8ecb6a.jpg)

访问的接口如下：

![p4](http://drops.javaweb.org/uploads/images/054c3ba5cab524315a27f4b5d134616b1766cca9.jpg)

今天我们要分析的对象就是这个名为Free Star的木马，这个也是360天眼实验室新晋小伙伴的处女作。

0x01 样本分析
=========

* * *

样本信息基本识别信息如下，供同行们参考。

木马文件MD5: c3d7807f88afe320516f80f0d33dc4f3、a1bb8f7ca30c4c33aecb48cc04c8a81f

分析得到木马主要行为总结：

*   添加服务项，开启服务，转移自身文件
*   用gethostbyname函数获取上线地址或访问QQ昵称接口获取木马上线地址，并进行网络连接
*   检测杀软进程
*   开启线程接收指令，执行远控功能

### 添加服务项，开启服务，转移自身文件

木马首先判断是否已经注册了服务项，如果没有注册，进入自拷贝、创建服务的流程：

![p5](http://drops.javaweb.org/uploads/images/93c1b65b582fd781410a37785fff0aadc7de0c4d.jpg)

创建服务

![p6](http://drops.javaweb.org/uploads/images/d2a21053f7a9b8e388917ad426b4eb9f1ab0dab4.jpg)

![p7](http://drops.javaweb.org/uploads/images/c608c95d31c51cde552a19e9b8666963621d7911.jpg)

调用StartServiceA开启服务，进入主功能流程

![p8](http://drops.javaweb.org/uploads/images/d126c236b965c070751a081217791233d9da1fea.jpg)

在拷贝自身，移动到`%appdata%`中指定目录

![p9](http://drops.javaweb.org/uploads/images/0e0958dd86785e3ddca9f3b16d7b6d1a9c347347.jpg)

创建自删除脚本并执行，用于删除自身文件以隐藏自身

![p10](http://drops.javaweb.org/uploads/images/51c7afa4f62561b0d76fdcb6eeb04c2401de1b20.jpg)

![p11](http://drops.javaweb.org/uploads/images/5b8a83584663e39702b6abea4a0358acefa56e3d.jpg)

脚本内容如下：

![P12](http://drops.javaweb.org/uploads/images/f6d8aa5b4cf1a29b373397bd18632576d6e1e6b1.jpg)

### 获取上线地址

以服务项启动进入时，通过注册表对应的项判断服务是否存在，决定是否进入开始进行网络连接。

![p13](http://drops.javaweb.org/uploads/images/bd07dd29bfdb4dd6a28d258736ff222b5c5e3b34.jpg)

解密动态域名、QQ号、端口号：

解密算法是Base64解码后，异或0x88 ，加0x78，再异或0x20

![p14](http://drops.javaweb.org/uploads/images/66cf2c0c581c0e675c1f0a9eb302381fb9d4c42b.jpg)

获取IP地址

![p15](http://drops.javaweb.org/uploads/images/cca201d81ddaf96840fd751e12d2593fd1c082ba.jpg)

![p16](http://drops.javaweb.org/uploads/images/47e17d9186e0848a0d7542f069c6f17903472135.jpg)

如果第一种方式不成功，则通过访问QQ昵称接口获取IP地址：

![p17](http://drops.javaweb.org/uploads/images/f100e58a5d3cf19248ef476bfc95bc045b351b8d.jpg)

![p18](http://drops.javaweb.org/uploads/images/794244f3c250369a2a463257ad4712093ffd241b.jpg)

获取到的QQ昵称为：`deacjaikaldSS`

![p19](http://drops.javaweb.org/uploads/images/116a78353e91b5f9fac02c136a8f4dff3cb26074.jpg)

对获取到的QQ昵称解密：解密算法是`+ 0xCD`

![p20](http://drops.javaweb.org/uploads/images/7647b7d9c2616ccda0314ec4c515f66cdeca9fdf.jpg)

解密后取得IP地址为： 1.207.68.91 ，开始连接：

![p21](http://drops.javaweb.org/uploads/images/ac4f90850137bb7483492bb64f9b282bc1b2c343.jpg)

循环连接这两个地址直到连接成功，连接成功后进入远控流程

### 获取受害者系统信息

首先获取主机名

![p22](http://drops.javaweb.org/uploads/images/2f76b78f8bc5ba033874a9361b0f8a201d1a81e2.jpg)

获取CPU型号

![p23](http://drops.javaweb.org/uploads/images/0541c694fba914cdc3e9cf9f25293f0e9353bd21.jpg)

获取其他信息等等

![p24](http://drops.javaweb.org/uploads/images/f9fb379b53a8b834a622a27226d6bda0f756d03c.jpg)

### 遍历进程，查找杀软进程

![p25](http://drops.javaweb.org/uploads/images/69ddbe03fa257408d99059a476a2e729c2de293b.jpg)

检查杀软的进程名用一个双字数组来存储，每个双字的值是指向对应杀软进程名的字符串的指针。如下：

![p26](http://drops.javaweb.org/uploads/images/44d2a321886b7817162854f1e14830d13e383747.jpg)

![p27](http://drops.javaweb.org/uploads/images/f860a22228518e033db8a2e5e231c0339ebf9ba1.jpg)

### 创建新线程，用于循环等待接收远控指令

![p28](http://drops.javaweb.org/uploads/images/83a9c2a1e5419a68483b17c86c45eaf0717fed05.jpg)

最后创建一个新的线程，用于接收远控指令，主要的功能有远程文件管理、远程Shell、屏幕监控、键盘记录等等，这里就不再赘述了。

代码整体流程图如下：

![p28](http://drops.javaweb.org/uploads/images/30b09747441ab4f5332394216cdd023ed533bad2.jpg)

0x02 幕后黑手
=========

* * *

这种通过QQ昵称获取上线地址的方式在躲避检测的同时也暴露了放马者的QQ号，我们在通过样本拿到的QQ号中找到了一个比较特殊的：550067654

![p29](http://drops.javaweb.org/uploads/images/e92a5e21e7e4d70cefc78f165f65d93db7fcb945.jpg)

通过搜索引擎，我们发现这个QQ号有可能是木马作者的一个业务QQ号，这个QQ在多个免杀论坛上注册了账号，经过进一步的确认，发现其的确是木马作者：

![p30](http://drops.javaweb.org/uploads/images/7adc0b3972b1546f6b03d3eeec2c0d62f444506a.jpg)

![p31](http://drops.javaweb.org/uploads/images/877518d5a3eda82e812924f25b3eb182cf5314b5.jpg)

![p32](http://drops.javaweb.org/uploads/images/64f80d56793de29ff475ff47734f0e210ba69b15.jpg)

从作者在某论坛上展示的木马功能截图可以发现，其曾经在贵州毕节地区活动。

![p33](http://drops.javaweb.org/uploads/images/e2d0133581b7537c50da58920e01aa91ca6c6c91.jpg)

![p34](http://drops.javaweb.org/uploads/images/ae90c042b16d9f0e0bca501452c4d9378ae47b35.jpg)

我们还发现作者用QQ邮箱账号注册了支付宝账号，通过支付宝账号的信息，发现作者的名字可能是：`*怡`

![p35](http://drops.javaweb.org/uploads/images/a89aa8e29540f2399f728b30a621b647527672b6.jpg)

通过某社工库，我们找到了作者经常使用的qq邮箱和密码，通过这条线索，我们找到了更多的信息：

![p36](http://drops.javaweb.org/uploads/images/a33c6edb28bc929722686eeb442cdb608de3394d.jpg)

在某商城发现了几笔订单信息，从而取到作者的名字、常在地区：

![p37](http://drops.javaweb.org/uploads/images/aaa74c9a23cd2c052e15caa8da22e809818fb677.jpg)

![p38](http://drops.javaweb.org/uploads/images/e7d0a532c9777139937e5aedac2f1e8d7c5c3039.jpg)

![p39](http://drops.javaweb.org/uploads/images/b732137fe8e274e0bc837ced983d8cf324d27ff1.jpg)

![p40](http://drops.javaweb.org/uploads/images/6aed73c86f679838889e6e00230402b015a067d6.jpg)

从身份证信息来看，确定作者是贵州毕节地区的人，名字就叫田怡。这也与上面获得的信息一致。

关于木马作者的追踪到此就告一段落了，有兴趣的同学们可以继续深挖，用一张天眼威胁情报中心数据关联系统生成的关系图来结束此次挖人之旅。

![p41](http://drops.javaweb.org/uploads/images/b398fb3ec486145ff6b19e3636623bc730759b1d.jpg)

0x03 传播途径
=========

* * *

分析完样本和木马作者之后，我们再看看该类木马的传播途径。

在我们捕获到的众多样本中，有一个样本访问的地址引起了我们的注意，通过关联，发现这是一些挂机、点击软件访问的地址，`http://sos.hk1433.cc:10089/bbs.html`

![p42](http://drops.javaweb.org/uploads/images/2ae0e7d2f294efa9ac723cbbfb76c284ee1745c3.jpg)

打开网页后，查看源代码，如下：

![p43](http://drops.javaweb.org/uploads/images/a9359060c28567d2821e4fd4b4abcd62d33b1ecb.jpg)

可以看到，这个页面加载了一个swf文件。将这个swf文件下载后打开，发现是Hacking Team的flash漏洞利用，下图红色框出的部分就是ShellCode：

![p44](http://drops.javaweb.org/uploads/images/9227f9fa5ce7cc854285f205111f3c46c7d82222.jpg)

ShellCode的功能就是一个Dropper，会将之前解密出来的PE释放并执行，而这个PE文件正是Free Star木马。

解密前的PE文件：

![p45](http://drops.javaweb.org/uploads/images/7c23b376094e0569fdebce2d9e0705856e0bf545.jpg)

解密后：

![p46](http://drops.javaweb.org/uploads/images/9b4bab01e7c34a0ef517184f163f6703414532b0.jpg)

ShellCode：

![p47](http://drops.javaweb.org/uploads/images/3a4580d127f00c5c84b9732485accf77f754ae58.jpg)

![p48](http://drops.javaweb.org/uploads/images/3b75985756b641fcbe3c2577d85b2d14f36c7571.jpg)

由此我们可以知道，该木马的传播方式之一即是通过网页挂马。

![p49](http://drops.javaweb.org/uploads/images/fcc3efa4377bfb807a9a54d623a92b989bc6bb9b.jpg)

通过上图可以看到挂马页面在3月28日上午9点上传，截至我们写这份报告的时间，3月29下午16点，点击量已经有13000多，而这仅仅只是冰山一角，但是在这里就不再深入。在我们的360威胁情报中心可以很容易地通过关联域名查询到对应的样本：

![p50](http://drops.javaweb.org/uploads/images/e87f004990e56679de073afe4d343350f3dde433.jpg)

0x04 总结
=======

* * *

通过这次分析，我们发现这个木马本身所用到的技术相当普通，与之前发现的木马基本一脉相承，体现出迭代化的演进。由于巨大的利益驱动，黑产始终保有对技术和机会的高度敏感，就象任何先进的技术首先会被用于发展武器一样，成熟可靠的漏洞利用技术及躲避检测的方案几乎肯定会立刻被黑产所使用传播。360威胁情报中心的数据基础以及自动化的关联分析为我们从样本分析、关系判定、来源追溯提供全方位的信息支持，成为我们用来对抗黑产以及其他高级攻击的强有力的武器。