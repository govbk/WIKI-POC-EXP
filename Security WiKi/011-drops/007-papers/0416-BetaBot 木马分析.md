# BetaBot 木马分析

**作者:喔欧（阿里巴巴安全部安全威胁情报中心）**

0x00 背景介绍
=========

* * *

在当下全球网络威胁活动中，国外攻击者主要使用Zeus、CryptoWall、Bedep、各类常见RAT工具等作为恶意负载，但在最近我们监控恶意威胁的过程中，发现个别高级样本攻击中使用了较为少见的BetaBot木马，关于此木马很少有相关的分析资料。在进一步了解、分析后发现，该木马还是具有很强的危害和对抗手段。为了方便监控BetaBot木马恶意攻击活动，所以记录相关分析结果，以供参考。

0x01 功能介绍
=========

* * *

BetaBot，又被称为Neurevt，大概从2013年3月出现在地下市场被出售，售价大约在$120到$500。使用HTTP协议进行通信，使用RC4算法进行加密，代码使用C++语言编写，功能强大。据作者声称，该木马具备破坏杀软、自保护、BotKiller、Userkit(Ring3 Rootkit)、自定义注入技术、防其他木马感染、、DDoS、网络监视/阻塞、USB设备感染、SOCKS4代理、自校验保护、过UAC、反Sandbox等功能。

下图为示例的BetaBot服务端界面

![](http://drops.javaweb.org/uploads/images/af9246844fa78f500b17893edb0289a4ef509617.jpg)

0x02 木马功能
=========

* * *

系统驻留
----

添加注册表自启动

![](http://drops.javaweb.org/uploads/images/78627b77648ef2014dae99dbede4ce5eb6834759.jpg)

添加Windows Tasks

![](http://drops.javaweb.org/uploads/images/9c74b6ef42d64f366dc95767d85d6b6a292ee4c6.jpg)

收集信息
----

运行环境、系统信息、硬件信息、软件信息等

例如软件信息搜集

![](http://drops.javaweb.org/uploads/images/22f265c3f49b51430fb6a196ca05fca9ceee6230.jpg)

启动参数
----

部分命令以程序启动参数传入解析并执行

![](http://drops.javaweb.org/uploads/images/b63aee5b539a576be56993612a08941cbbe9fae9.jpg)

DDoS
----

支持4种类型的DDoS攻击方式

![](http://drops.javaweb.org/uploads/images/d7b0df859e575db733132eba55ddd4a69cb6e0fd.jpg)

System Wide Userkit(Ring3 Rootkit)
----------------------------------

功能名称引用作者描述，用于隐藏保护木马。

HOOK API列表

![](http://drops.javaweb.org/uploads/images/cbab7ace0e247335f7afe3179ba11bf8b6d3db6d.jpg)

![](http://drops.javaweb.org/uploads/images/51d23e1e90566745cd72e01c2321657b0b58ee1d.jpg)

UAC欺骗绕过
-------

根据用户语言习惯构造错误信息，欺骗用户

![](http://drops.javaweb.org/uploads/images/2afb948d7355477c24f3c31f59dbf3905787cf84.jpg)

调用cmd.exe或者rundll32.exe触发UAC，实际调用木马自身

![](http://drops.javaweb.org/uploads/images/f4c4cd5d2d0f059488a7dd41fceb6a703524fc3a.jpg)

根据用户语言习惯构造错误信息

![](http://drops.javaweb.org/uploads/images/43e0c14a41a1daede1a1c4b173c73248ba1a1449.jpg)

在BetaBot木马对抗杀软介绍时作者也提到了使用”社会工程学”的手段

![](http://drops.javaweb.org/uploads/images/ae839e6d929a60b336d1419777779e4f90077eae.jpg)

配置解密
----

* * *

BetaBot的配置数据包含运行时所需要的释放目录位置、C&C、通信密钥等重要信息，并加密存放在木马文件内。

配置数据解密流程可以分为:

1.  解密整体Config
2.  依次解密C&C Entry

配置文件结构大小是0x0D56字节(随木马版本更新)，下图为解密整体config初始化代码，构造参数，动态解密执行代码，替换启动线程。

![](http://drops.javaweb.org/uploads/images/d51a597c7427b9eaa14e7d7bf8a7b79506796189.jpg)

解密线程从imagebase搜索加密config特征，通过RC4和4字节异或进行解密，RC4解密key在自身代码中保存，解析出所需数据后，使用自更新的加密key重新加密。

![](http://drops.javaweb.org/uploads/images/600559984c0ae04ce006e1025ed98e94a7977ff0.jpg)

![](http://drops.javaweb.org/uploads/images/227460d0e6300cb97383a3194133daf1c48f1532.jpg)

解密结果如下

![](http://drops.javaweb.org/uploads/images/ec1ace03ff4c5dedce0b20895d010e86e4cde4eb.jpg)

上图中前半部分已经解密，偏移0x156起始的C&C Entry还需要使用图中偏移0x6选中内容作为key解密，解密流程见下图

![](http://drops.javaweb.org/uploads/images/fbaf82b14980cface81bd9b538da481fe5805ab3.jpg)

可以看出该木马最多可以支持16个C&C配置。

例如解密出的一条C&C配置，其中包含了域名(偏移0x26)、端口(偏移0x14)、path(偏移0x66)、C&C通信key1(偏移0xAA)、key2(偏移0XB7)。

![](http://drops.javaweb.org/uploads/images/099c93470f693a444f70e69b0418e9c20a5b884e.jpg)

C&C通信解密
-------

* * *

### 请求过程

![](http://drops.javaweb.org/uploads/images/aa7dda5f067c75860a296db0d985a4b29038afcf.jpg)

构造请求数据

![](http://drops.javaweb.org/uploads/images/7cf50d5274d8f01786e4d9897c32cd4a760a2ac0.jpg)

RC4加密请求数据并进行bin2hex转换，加密key是由C&C Entry配置的key1和随机字节序列拼接处理得到。

![](http://drops.javaweb.org/uploads/images/3bf72f6566f3dce5e5207d7a908f7e36a3678e7c.jpg)

第一次请求会附上额外信息。

![](http://drops.javaweb.org/uploads/images/a65167dbebe1e808ea49f985f9c354225f0929e8.jpg)

额外信息异或特定值并进行bin2hex转换。

![](http://drops.javaweb.org/uploads/images/c37257fd025178f10400524da9de96fb8eebf07f.jpg)

最后将参与加密请求数据的随机字节序列进行bin2hex转换和上述bin2hex转换信息一起发送到服务端。

![](http://drops.javaweb.org/uploads/images/dcc60180527e3ff09fb6fe5a05ef0851be3bd058.jpg)

发送数据如下

![](http://drops.javaweb.org/uploads/images/750b77c78a77e68296690e1f936576fcb0973942.jpg)

### 响应过程

![](http://drops.javaweb.org/uploads/images/8fd1b170031ca7ba5f1b66edd439d15edbbee06a.jpg)

服务器响应包含两部分，header和body。

![](http://drops.javaweb.org/uploads/images/d08ffecdd8bc3f4d7dffedd44722a78cd40fc906.jpg)

首先需要解密header，其中最重要的是8个DWORD组成的数组streams_array，位于偏移0x3C，表示body各个结构的长度。

解密过程如下，RC4加密key是由C&C Entry的key1和response数据的前四个字节组合异或得到。

![](http://drops.javaweb.org/uploads/images/26a183c8373e885f28710123c341587d1188f3da.jpg)

最后根据streams_array计算body长度然后解密。

![](http://drops.javaweb.org/uploads/images/7dfc44603b6966831cc9f6bfb8e84b5922cc8249.jpg)

加密的body位于偏移0x5C，解密过程如下，RC4加密key是由C&C Entry的key2和response数据偏移0x4四个字节组合异或得到。

![](http://drops.javaweb.org/uploads/images/9b3cccdfd9e6c5953cba202109341a1002004df9.jpg)

最终解密结果如下图，此图所示是服务端下发的监视域名列表配置。

![](http://drops.javaweb.org/uploads/images/987632b610a83db14f4cd337976c232ab10a8bf1.jpg)

其他
--

DNS阻断、表格抓取等功能可见参考链接。

0x03 对抗手法
=========

* * *

反调试
---

**1.ZwQueryInformationProcess检测DebugPort**

![](http://drops.javaweb.org/uploads/images/fb77cdd52bb3bffac49be43054880a291c9ca1fe.jpg)

**2.DbgBreakPoint对抗**

![](http://drops.javaweb.org/uploads/images/74e8087f9dd34d7039c4e016b5ca11bfee8e5d9d.jpg)

**3.ZwSetInformationThread**

![](http://drops.javaweb.org/uploads/images/2ae32cbbbc374868ee5a3eb28b06318f5b8df599.jpg)

**4.多处代码执行过程反调试对抗**

例如解密config代码中

![](http://drops.javaweb.org/uploads/images/cbf075e1a90d2f05982678b63bd6317a28b032d2.jpg)

反虚拟机
----

![](http://drops.javaweb.org/uploads/images/458ef2981f4c840469f9347c34f74e4dcc273631.jpg)

反JoeBox,GFI,Kasperksy,CWSandbox,Anubis等沙箱
-----------------------------------------

![](http://drops.javaweb.org/uploads/images/df40ea42554307267d4fdf7e2069dcdfb3e1acba.jpg)

反Sandboxie沙箱
------------

![](http://drops.javaweb.org/uploads/images/35c0c43321252e26e95b30ec160335c1a4e99837.jpg)

反wine
-----

![](http://drops.javaweb.org/uploads/images/33ab1e5b8d1513c98cfda6a01dabce00dbc94df8.jpg)

导入API加密
-------

通过遍历系统dll导出表，拼接成moduleName+’.’+APIName计算hash进行搜索

Hash计算方式

![](http://drops.javaweb.org/uploads/images/7ca8491fa1fff2fc1bc829c100a3ba20a8a90b7f.jpg)

对抗杀软
----

检测杀软类型

![](http://drops.javaweb.org/uploads/images/58caafd44f3228121958384ac1acfd72446eefb0.jpg)

![](http://drops.javaweb.org/uploads/images/efcdbc15ed6ac3aea872adb3cfd746b73a16391d.jpg)

![](http://drops.javaweb.org/uploads/images/f12c334e5898de82718d0c2a1367cb39298bfa3d.jpg)

禁用杀软

![](http://drops.javaweb.org/uploads/images/491042670c894d7afe3b19707c3a2aa0be5d518a.jpg)

![](http://drops.javaweb.org/uploads/images/589baf55cfc3ece802bd86d6448b13597fba2f9e.jpg)

![](http://drops.javaweb.org/uploads/images/78cb4d15736c48863a7925e0a63852e0d688ad4c.jpg)

代码加密、动态替换
---------

解密执行代码过程，例如解密Config线程函数体内容

![](http://drops.javaweb.org/uploads/images/8deb968f7f5f96b94061043708c21bdef182d79e.jpg)

在一些函数调用时通过替换stub参数实现。例如stub原始代码

![](http://drops.javaweb.org/uploads/images/9a68f8f8b5a6f893511a5d598000f7406e66c8e9.jpg)

替换参数

![](http://drops.javaweb.org/uploads/images/43d2428af814e4b05cec53f901df0ecd4f857a4c.jpg)

Snort检测规则
---------

```
alert http any any -> any any (msg: "Betabot Windows RAT Trojan Online Request"; flow: established, to_server; content: "POST"; http_method; content:"="; http_client_body; pcre: "/=\d{8}&/P"; content: "1="; distance:1; http_client_body; content: "2="; distance:1; content: "3="; distance:1; content: "4="; distance:1; content: "5="; distance:1; flowbits: set, betabot_online; classtype: trojan-detect; sid:010200291; rev:1; )

```

0x04 参考链接
=========

* * *

*   [https://securityintelligence.com/beta-bot-phish/](https://securityintelligence.com/beta-bot-phish/)
*   [http://www.slideshare.net/securityxploded/dissecting-betabot](http://www.slideshare.net/securityxploded/dissecting-betabot)