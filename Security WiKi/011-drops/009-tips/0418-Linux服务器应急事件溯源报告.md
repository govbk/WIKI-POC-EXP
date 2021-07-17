# Linux服务器应急事件溯源报告

**Author:Inn0team**

0x00 目录
=======

*   关于目标环境的中间进度检测报告
*   一：情况概述
*   二：取证情况  
    *   2.1 目标网络情况
    *   2.2 针对xxx服务器中间件的检测
    *   2.3 针对xxx服务器进程及端口的检测
    *   2.4 发现攻击者的攻击操作
*   三：溯源操作  
    *   3.1 关于攻击者的反向检测
*   四：攻击源确定
    *   4.1 确定攻击入口处
*   五：安全性建议

关于目标环境的中间进度检测报告
===============

0x01 情况概述
=========

* * *

监控软件监控到服务器存在异常的访问请求，故对此服务器进行安全检查。

通过提供的材料发现内网机器对某公网网站存在异常的访问请求，网络环境存在着异常的网络数据的访问情况。针对其服务器进行综合分析发现了病毒文件两例，内网扫描器两例，通过以上的发现证实服务器已被黑客入侵。

0x02 取证情况
=========

* * *

### 2.1 目标网络情况

下文中的内网内ip以及公网ip为替换后的脱敏ip。

| IP | 所属 | 操作系统 |
| --- | --- | --- |
| 1.168.xxx.xxx | 某业务员服务器 | Linux2.6.32 x86_64操作系统 |
| 192.168.0.0/24 | DMZ区 | Linux&windows |
| 10.10.0.0/24 | 核心区 | Linux&windows |
|  | 防火墙 |  |

### 2.2 针对xxx服务器中间件的检测

监测存在异常的服务器开放了80端口和21端口，安装了tomcat中间件。首先进行tomcat中间件的排查，查询得知服务器对外开tomcat文件夹路径为`/home/XXX/tomcat/XXX _tomcat`，查询tomcat未使用弱密码：

![p1](http://drops.javaweb.org/uploads/images/c4dcc59f64199666ee7c91026fa3ec4d9f6e76da.jpg)图1：tomcat未使用默认弱口令

针对tomcat部署服务进行检查，未发现可疑部署组件：

![p2](http://drops.javaweb.org/uploads/images/93f602af7d60dec631f89b8fcdf17e1935b2847a.jpg)图2：未发现可疑的部署组件

![p3](http://drops.javaweb.org/uploads/images/0021a9912ef4149aa1abcef86d04873ebb3b0de1.jpg)图3：未发现可疑的host配置

### 2.3 针对xxx服务器进程及端口的检测

针对目标服务器进行了进程以及端口的检测，发现了可疑现象入下图所示：

![p4](http://drops.javaweb.org/uploads/images/7c6a085a6e37ee0a7643c9a84b6db9da8fc9bd92.jpg)图4:发现可疑占用情况

发现可疑现象后查找“l”所在的路径，入下图所示：

![p5](http://drops.javaweb.org/uploads/images/8039d6871e1e72f76c04c61868382f4b373f02bf.jpg)图5：发现可疑文件路径

在/dev/shm路径下发现存在“l”与“conf.n”文件

![p6](http://drops.javaweb.org/uploads/images/0ea41016e1841ecca11c31cf7d4da4b374a96322.jpg)图6：找到可疑文件

将“l”与“conf.n”下载到本地进行分析，“l”程序为inux远控木马Linux.DDOS.Flood.L，经本地分析“l”程序为linux下僵尸木马，同时具有远控的功能

![p7](http://drops.javaweb.org/uploads/images/b86e0adc075d2a46499ab4027725e26e01007601.jpg)图7：证实为Linux.DDOS.Flood.L木马

通过继续分析目标服务器中的可以进程与端口占用情况，发现另外可疑文件，如下图所示：

![p8](http://drops.javaweb.org/uploads/images/d9cd369798847d082511726922eee1b16dad00f0.jpg)图8：发现可疑文件vkgdqddsx

将可疑文件进行本地分析，证实此文件为病毒文件：

![p9](http://drops.javaweb.org/uploads/images/e128377d4e012b5ef11556afe88045f48b27aea4.jpg)图9：证实为病毒文件

### 2.4 发现攻击者的攻击操作

针对目标环境进行彻底排查，发现攻击者使用wget操作从 http://111.205.192.5:2356服务器中下载“l”病毒文件，并执行了“777”加权的操作。

其记录文件如下图所示：

![p10](http://drops.javaweb.org/uploads/images/b48f350d114021a25746b87d71deff3d5602073d.jpg)图10：发现木马文件下载操作

![p11](http://drops.javaweb.org/uploads/images/7d59e47aa16b1a1a163ccc645a22776f72f6fd88.jpg)图11：通过l文件的时间状态定位到疑似攻击者下载时间为2015-01-18 04:54:05

![p12](http://drops.javaweb.org/uploads/images/8ef5ffe019a5c5e9fe5052f1e91a6322149cdb1e.jpg)图12:定位到可疑时间段连接ip地址

![p13](http://drops.javaweb.org/uploads/images/d2a32dd8dc9a94bf32018de866e16eef469275d1.jpg)图13：不同时间段的可疑连接ip

通过进一步的对可疑。

通过分析目标服务器日志文件，发现攻击者下载病毒文件后又使用内网扫描软件“.x”调用其“pascan”和“scanssh”模块进行内网ssh扫描，通过分析发现攻击者收集到了目标网络环境中的常用密码来进行针对性的扫描测试。

如下图所示：

![p14](http://drops.javaweb.org/uploads/images/adb883eacd4846bf7948a4e6602e2934fbaa1a5d.jpg)图14：发现目标服务器中存在ssh爆破以及网段扫描软件

![p15](http://drops.javaweb.org/uploads/images/aef8b8643f937afb23bce5842437da166e712cae.jpg)图15：通过在测试环境中测试发现为扫描软件

![p16](http://drops.javaweb.org/uploads/images/75ac7b02a2f3a284fd7ec03f8942ebdd27c59668.jpg)图16：攻击者使用扫描软件进行内网网段的扫描

通过继续对扫描软件进行深入挖掘，发现攻击者使用扫描软件得到的其他内网的ip地址（部分）：

![p17](http://drops.javaweb.org/uploads/images/b68c6e58016f2d677fd4a30be3d2cce273a9c4d5.jpg)图：17 攻击者得到的内网部分地址及密码

尝试使用此地址中的192.168.21.231和192.168.21.218进行ssh登录，可使用`root:huawei`成功进行ssh连接（其他地址及口令不再进行测试），并在内网机器中发现使用弱口令“123456”并发现了同样的“l”病毒文件。

其记录文件如下图所示：

![p18](http://drops.javaweb.org/uploads/images/027ea9f69862dfdeeef358fa1f322545e2c4ee72.jpg)图18：进行ssh连接

![p19](http://drops.javaweb.org/uploads/images/2e1019a78ff06b731525c45936afff08c7d5b989.jpg)图19:连接成功后进行“ifconfig”操作

![p20](http://drops.javaweb.org/uploads/images/7ee184d56252e000491316dbe2bc9c9a9b9f1442.jpg)图：在网络中的其他机器也发现了同样的病毒文件

在扫描器中发现了攻击者使用的“passfile”字典文件，从中可以发现攻击者使用的字典具有很强的针对性（初步断定攻击者为在网络环境中通过查询密码文件等操作获取的相关密码）：

_隐私信息--此处不贴图_  
图20：发现针对性极强的密码字典

通过继续对日志文件进行排查，发现攻击者使用扫描器进行攻击的历史记录，验证了搜集到的信息：

![p21](http://drops.javaweb.org/uploads/images/c1cedc0baa0690c919c66f8473e0ef9244fd45e6.jpg)图21：攻击者进行攻击的历史记录

通过即系分析，发现攻击者在进入目标服务器后，又进行了防火墙权限修改、“udf”权限提升、远程连接等其他操作。其中“udf病毒文件”未在目标服务器中发现，在后期进行反追踪中在攻击者服务器中获取到“udf”文件，进行本地检测后病毒文件。

其记录文件如下图所示：

![p22](http://drops.javaweb.org/uploads/images/d10e5b16234fbd9787547190d3523a7f573083a7.jpg)图22: 修改iptables防火墙配置

![p23](http://drops.javaweb.org/uploads/images/512f4d8872eb0ae7fd99d1d27c89328d5f2e23f0.jpg)图23：被修改后的防火墙配置

![p24](http://drops.javaweb.org/uploads/images/af8357970d72bf5897b993ec29722a5ed57a1851.jpg)图24：攻击者进行提权的操作

![p25](http://drops.javaweb.org/uploads/images/dc4627e2ca75e8396e45b80d473f8bbfd2449b4a.jpg)图25：“udf”文件证实为病毒文件

通过对攻击者完整的攻击取证，可证实攻击者通过SSH连接的方式使用`guest_cm`用户而和`root`用户进行远程连接，连接之后使用Wget方式下载并种植在目标服务器中“l”和“vkgdqddusx”病毒文件，并使用“udf”进行进一步的权限操作，然后使用“.x”扫描软件配合针对性极强的密码字典进行内网的扫描入侵，并以目标服务器为跳板使用root和xxx账户登录了内网中的其他机器在入侵过程中入侵者将部分相关日志进行了清除操作。

0x03 溯源操作
=========

* * *

### 3.1 关于攻击者的反向检测

在取证过程中发现攻击者服务器使用以下三个ip

xxx.xxx.xxx.x、xxx.xxx.xxx.xxx、xxx.xx.xxx.xx（打个马赛克）

通过对这三个IP进行溯源找到

http://111.205.192.5:2356/ 网站使用hfs服务器搭建，文件服务器内存储着各种病毒文件，其中找到了在“l”“udf”等病毒文件，证实前文中的判断。

![p26](http://drops.javaweb.org/uploads/images/63431f14502102fdaaddb66180dcc91c0b086bd4.jpg)图26：文件服务器中存储着在本次攻击中所使用的病毒文件

通过其他手段查询得知使用ip地址曾绑定 www.xxxx.com网站，并查找出疑似攻击者真实姓名xxx、xxx，其团体使用xxxxxx@qq.com、wangzxxxxxx.yes@gmail.com等邮箱，使用61441xx、3675xx等QQ。并通过某种手段深挖得知攻击者同事运营着多个博彩、私服类网站。

其他信息请看下图：

![p27](http://drops.javaweb.org/uploads/images/ca642ce2f20440b712622180906cbffe82fab56c.jpg)图27：攻击团伙使用支付宝及姓名

![p28](http://drops.javaweb.org/uploads/images/fe18c3d25c0c8bec6610b74428dad2a591a3a0e1.jpg)图28：攻击团伙旗下的其他博彩、私服网站

![p29](http://drops.javaweb.org/uploads/images/4abec23adf80355ea6eab7103ff8dfa2eacad692.jpg)图29：攻击者旗下部分博彩、私服网站

_打码处理_  
图30：攻击团伙成员QQ信息

0x04 攻击源确定
==========

* * *

### 4.1 确定攻击入口处

综合我们对内网多台服务器的日志分析，发现造成本次安全事件的主要原因是：

10.0.xx.xx设备的网络部署存在安全问题，未对其进行正确的网络隔离，导致其ssh管理端口长期暴露在公网上，通过分析ssh登陆日志，该台设备长期遭受ssh口令暴力破解攻击，并发现存在成功暴力破解的日志，攻击者正是通过ssh弱口令获取设备控制权限，并植入木马程序进一步感染内网服务器。

具体攻击流程如下图所示：

![p30](http://drops.javaweb.org/uploads/images/039c74455d804733e30a0debdcc779fb70cd8583.jpg)图31：黑客本次攻击流程图

![p31](http://drops.javaweb.org/uploads/images/faacbb9d48a42aaa9aee2b486f6ab8264e7a5f56.jpg)图:32：存在长期被爆破的现象

![p32](http://drops.javaweb.org/uploads/images/93fbb6c78c18a18667cddb1f1f607f9cc3256602.jpg)图33：被某公网ip爆破成功进入机器

经分析，2016年1月12号公网ip为211.137.38.124的机器使用ssh爆破的方式成功登陆进入10.0.xx.xx机器，之后攻击者以10.0.16.24机器为跳板使用相同的账户登录进入192.168.xxx.xxx机器。

![p33](http://drops.javaweb.org/uploads/images/c3a838290e538db4acb47aa10f3e2432eef4bb83.jpg)图34：相同账户进入192.168.150.160机器

攻击者进入192.168.150.160机器后，于2016年1月17日使用wget的方式从http://111.205.192.5:23561网站中下载了 “Linux DDos”木马文件，并使用扫描器对内网进行扫描的操作。

![p34](http://drops.javaweb.org/uploads/images/7477dbe996ac2de90ab49bbb899af670781ecfe5.jpg)图：35攻击者下载“Linux DDos”病毒文件

攻击者通过相同的手段在2016年1月17日使用sftp传输的方式进行了木马的扩散行为，详细情况见下图：

![p35](http://drops.javaweb.org/uploads/images/c86288d7d2cdd1ce4579ef8272f56d59f9104e95.jpg)图36:使用SFTP传输的方式进行木马的扩散

0x05 安全性建议
==========

* * *

1.  对使用密码字典中的服务器进行密码的更改。
2.  对网络环境进行彻底的整改，关闭不必要的对外端口。
3.  网络环境已经被进行过内网渗透，还需要及时排查内网机器的安全风险，及时处理。
4.  SSH登录限制  
    修改sshd配置文件

由于服务器较多，防止病毒通过ssh互相传播，可通过修改`sshd_config`，实现只允许指定的机器连接，方法如下：

登录目标主机，编辑/etc/ssh/sshd_config

```
# vi /etc/ssh/sshd_config

```

在文件的最后追加允许访问22端口的主机IP，（IP可用*号通配，但不建议）