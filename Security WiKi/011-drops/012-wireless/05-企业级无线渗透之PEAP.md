# 企业级无线渗透之PEAP

0x00 前言
=======

* * *

上月，受邀在C-SEC上海快递行业安全会议上做了关于无线安全威胁的议题分享。介绍了家庭级的无线网络薄弱环节及攻击方法，同时列举了乌云上因无线边界被突破，造成内网沦陷的诸多例子。后半部分，简要的介绍了企业级无线网络安全，可能因为受众人群及时间的关系，观众情绪不太高，所以我也没有展开。

家庭级的无线安全已是老生常谈了，而针对于企业级的802.1X，在我检索时发现中文网页内的相关安全文章只有寥寥数篇，大多只是讲述了攻击过程，对于其缺陷原因、防护方法、对于802.1X中EAP的诸多扩展协议并未提及。这无疑对新入研究者帮助甚少。于是便有了此文，也是我对知识的梳理，希望能对大家有所帮助。

0x01 无线网络的历史
============

* * *

### **WEP**

是无线网络中最早最被广泛使用的安全协议，使用了基于共享加密密钥的 RC4 对称加密算法。因为加密算法不够强壮，收集足够多的密文数据便可直接算出密钥，同时由于数据完整性检验算法也不够强壮，导致整个破解过程可在几分钟内完成。

WEP有2种认证方式：开放式认证（open system）和预共享密钥认证（shared key）。

### **WPA**

针对WPE出现的问题，IEEE推出了 802.11i 标准。但由于时间紧迫，短时间内无法将标准全部实现，于是在2003年 WPA 被推出，用以作为 802.11i 完备之前替代 WEP 的过渡方案。

> 相比于WEP，WPA实现了三个关键的改动。
> 
> 1.  除了预共享模式（pre-shared key）这种类似WEP预设KEY的认证之外，还支持 802.1X 认证。802.1X 使用独立的radius服务器，每个用户使用不同的密码登录，提高了认证强度。
> 2.  增加了 TKIP 协议（临时密钥完整性协议），可以将其理解为WEP外面的一层保护皮。WEP容易破解是因为RC算法不强，而且密钥固定不变，TKIP 的做法就是在传输过程中为每个包生成不同的加密密钥，增大破解难度。
> 3.  更强的数据完整性检验算法，解决篡改问题。

### **WPA2**

WPA寿命很短，2004年便被实现了完整 IEEE 802.11i 标准的 WPA2 所取代。WPA2中使用更强的AES（Advanced Encryption Standard）加密算法取代WPA中的RC4，也使用了更强的完整性检验算法CCMP。

到现在，一共有三种认证方法：开放式认证、预共享密钥(PSK)认证、802.1X认证。 现在，在路由器设置的加密方式里看到wpa-personal、wpa2-personal、wpa-enterprise、wpa2-enterprise时就不会晕了，personal指的PSK认证，enterprise指的便是802.1X认证。

0x02 802.1X
===========

* * *

IEEE 802.1X 是 IEEE 制定关于用户接入网络的认证标准，它为想要连接到 LAN 或 WLAN 的设备提供了一种认证机制，通过EAP协议（Extensible Authentication Protocol）进行认证，控制一个端口是否可以接入网络。 802.1X工作在二层，加上EAP只是一个框架，可以由厂商实现具体的认证方法，因此具有非常好的扩展性，在办公网络的很多方案中得到应用。不同的厂商也衍生出一大堆LEAP、PEAP、EAP-TLS、EAP-MD5等等具体的认证协议。

> 802.1X验证涉及到三个部分：申请者、验证者和验证服务器。
> 
> 申请者是一个需要连接到LAN/WAN的客户端设备，同时也可以指运行在客户端上，提供凭据给验证者的软件。 验证者是一个网络设备，如以太网交换机或无线接入点。 验证服务器通常是一个运行着支持RADIUS和EAP协议的主机。
> 
> 验证者就像是一个受保护网络的警卫。申请者不允许通过验证者访问到受保护一侧的网络，直到申请者的身分被验证和授权。这就像是允许进入一个国家之前要在机场的入境处提供一个有效的签证一样。使用802.1X基于端口的验证，申请者向验证者提供凭据，如用户名/密码或者数字证书，验证者将凭据转发给验证服务器来进行验证。如果验证服务器认为凭据有效，则申请者就被允许访问被保护侧网络的资源。

![802.1X验证](http://drops.javaweb.org/uploads/images/c9fba8e3d4822734f6ae3328dbd7c91571357729.jpg)

802.1X 最初为有线接入而设计，因连接需要物理接触，所以在安全方面考虑较少。而无线网络的出现，使设备接入变得容易，需要对802.1X的安全性进行加强，即增强EAP协议的安全性。除了验证用户外，用户也需要去确保正在连接的是合法热点。

需求便是：强健的加密方式及双向认证。 基于 IETF 的 TLS 标准可以较好的实现这两点需求，三种基于TLS的EAP协议就被研制了出来：EAP-TLS、EAP-TTLS、EAP-PEAP。 EAP-TLS基于Client和Server双方互相验证数字证书。因为EAP-TLS需要PKI系统为客户端签发证书的缺点，所以设计出了TTLS和PEAP，这两个协议可以在TLS隧道内部使用多种认证方法。

![EAP-TLS、TTLS、PEAP ](http://drops.javaweb.org/uploads/images/ea9a7db60e477db50c49d3a75764b0379505ce05.jpg)

因为PEAP与Windows操作系统的良好协调性，以及可以通过Windows组策略进行管理的特性，使得PEAP在部署时极其简单。同时，由于PEAP可以兼容几乎全部厂商的全部设备，因此对于企业来说，PEAP是一个最佳的验证协议。

0x03 PEAP
=========

* * *

### PEAP 与 PKI

PEAP是可扩展的身份验证协议 (EAP) 家族的一个成员。它使用 TLS 为进行PEAP验证的客户端和服务器间创建加密隧道。PEAP没有指定具体的认证方法，可搭配选择多种认证方式如 EAP-MSCHAPv2 、EAP-TLS等。

PEAP的认证过程分为两个阶段：

1.  服务器身份验证和建立TLS安全隧道。Server向Client发送证书信息实现“Client对Server的认证”；
2.  客户端身份认证。在TLS隧道内通过多种认证方法（一般为EAP-TLS 或 EAP-MSCHAPv2） 与 PEAP 共用实现“Server对Client的认证”；

认证方法：

*   EAP-MSCHAPv2，客户端使用凭据（基于密码）进行对客户端身份验证；
*   EAP-TLS，客户端使用证书进行对客户端验证，必须部署PKI；

### PKI

PEAP 使用 PKI 来确保用户验证过程不会被黑客或恶意人员截获和破解，这与SSL采用PKI来确保网站或其它敏感网络应用在数据交换过程不被截获并破解的目的是一样的。

> PKI 模式采用一个简单的数字文档作为确定拥有者身份的数字证书，实现安全的密码交换。 数字证书本身没有价值，而当这个证书被称作证书授权(CA)的受信机构签名后，就具有了证明身份的作用。 为了让CA能够被客户所信任，客户端的证书信任列表(CTL)中应该安装包含有该CA公钥的“root certificate”，即该CA根证书。

目前所有主流操作系统中，都预装了包含可信CA根证书的CTL，这也就是为什么诸如 VeriSign 等公司有权利给全球的服务器颁发证书。采用VeriSign这样具有公信力的认证 机构来建立PKI是一件非常简单的事情，因为该证书已经被几乎所有的电脑及移动设备所接受，但是服务器证书的费用每年可能会有数百美元。采用EAP-TLS和CA结合的办法成本更高，因为还需要每年为每个客户支付60美元的数字证书费用。

于是很多企业采用自签名数字证书的方式来实现无线局域网的部署。

3.1 PEAP Weakness
-----------------

企业部署无线网，一般会选择采用PEAP-MSCHAP v2、使用AD认证（域账户）的架构。 通过上面的介绍可以了解到，PEAP通过类似SSL机制为认证提供传输层的安全，需要企业去向CA购买证书，或者自建PKI系统，签署用于无线的证书，同时将根证书部署到每个客户端。

“将根证书部署到每个客户端”这个要求实现起来比较麻烦，大部分企业直接忽视，客户端直接面对未经认证的证书，便留下了隐患：

*   任何人都可伪造出同名WiFi及伪造成一模一样的证书信息（未认证的）。
*   用户对于“是否信任”等对话框会习惯性确认。（12306等培养了习惯）
*   Security由用户决定。

![未经验证的证书](http://drops.javaweb.org/uploads/images/b0f0bed6b5ef3142b1c3f60e324f0762e9e10ab6.jpg)

3.2 PEAP Attack
---------------

那么针对PEAP的攻击手法就很明确了：

1.  Fake AP + RADIUS Server。伪造热点骗取客户端的连接建立TLS隧道，在用户与伪造的Radius服务器进行认证交互时，记录下凭证hash值(Challenge/Response）
2.  通过字典攻击跑出密码

工具可以使用FreeRadius-WPE，这是一款针对开源FreeRADIUS服务器的补丁程序。 使用方法可参考知识库上mickey写的[《破解使用radius实现802.1x认证的企业无线网络》](http://drops.wooyun.org/tools/8294)一文，这里便不再赘述。

不过 FreeRadius-WPE 项目已经在14年停止维护，OpenSecurityResearch 制作了一个替代品 hostapd-wpe，可直接为hostapd打补丁支持 PEAP/MSCHAPv2、EAP-TTLS/MSCHAPv2等攻击。

### Hostapd-WPE

项目地址： https://github.com/OpenSecurityResearch/hostapd-wpe 官方文档：

```
Ubuntu/Debian/Kali Building - 
-----------------------------------------------------------------------
    apt-get update
    apt-get install libssl-dev libnl-dev

General - 
------------------------------------------------------------------------
    git clone https://github.com/OpenSecurityResearch/hostapd-wpe

    wget http://hostap.epitest.fi/releases/hostapd-2.2.tar.gz
    tar -zxf hostapd-2.2.tar.gz
    cd hostapd-2.2
    patch -p1 < ../hostapd-wpe/hostapd-wpe.patch 
    cd hostapd

    #If you're using Kali 2.0 edit .config file and uncomment:CONFIG_LIBNL32=y
    make

    I copied the certs directory and scripts from FreeRADIUS to ease that 
    portion of things. You should just be able to:

    cd ../../hostapd-wpe/certs
    ./bootstrap

    #then finally just:

    cd ../../hostapd-2.2/hostapd
    sudo ./hostapd-wpe hostapd-wpe.conf

```

建立成功后，用手机连上此热点，输入账号密码就可观察到被记录hash值(Challenge/Response），被记录在hostapd-wpe.log

![此处输入图片的描述](http://drops.javaweb.org/uploads/images/b1947df9a55a1c295db11840bdae36bb3d3b9ba1.jpg)

### Asleap & John the Ripper

有两个工具可以使用，一个是著名的John the Ripper，hostapd-wpe.log文件里有直接生成了NETNTLM格式的hash，提交给John the Ripper就行了

这里以asleap为例：

```
wget http://www.willhackforsushi.com/code/asleap/2.2/asleap-2.2.tgz
tar zxvf asleap-2.2.tgz
cd asleap-2.2
make

./asleap -C Challenge值 -R Response值 -W path/to/wordlist.txt

```

![此处输入图片的描述](http://2.bp.blogspot.com/_Y2uWeGSk9Sw/TC3N00ynJ0I/AAAAAAAAGi8/9b7QQ67DuR4/s1600/Figura9.png)

### MS-CHAP v2 Vulnerability

在Defcon 20上，有研究人员展示了破解 MS-CHAPv2 的方法。

> MS CHAP v2整个认证过程，最后的本质就是MD4计算HASH和DES加密。 但是这个过程中有几个非常2的做法，首先DES加密的时候是分三段进行的，导致每段都很短，只有7bytes（56 bits）。更严重的问题在于，MD4 HASH只有16bytes（不够21bytes分三段）而填充了5个0，导致最后一段DES的KEY其实只有2个字节也就是16bits，这一段简直就是明文了。那么最后剩下的，就是要破解前面2个KEY长度为56bits的DES加密了，算法复杂度仅为2的57次方，可以暴力了。

在获取了MS-CHAP v2握手数据包后，使用chapcrack工具解析该握手数据包中相关的凭证信息，被提交给CloudCracker网站，该网站为渗透测试人员和网络审计员提供在线的密码破解服务，在一天内返回破解的MD4哈希值。

0x04 总结
=======

虽然我们可以通过上面讲述的方法对PEAP进行攻击，同时MS-CHAP v2还包含漏洞可被暴力破解，但这并不意味着PEAP已经被攻破了。当配置合理时，PEAP 是安全的，因为黑客根本没机会接触到在TLS隧道中的MS-CHAPv2。

应该做到：

*   部署根证书到客户端
*   客户端总是拒绝未经验证的证书
*   在客户端的证书信任列表(CTL)中，删除CN（它们有伪造的先例）

* * *

由于涉及较多的协议知识，如有纰漏欢迎指正。 有少量的参考内容未使用引用（考虑到排版），还请谅解。

最后感谢Sweeper、Sanr对本文的指导和帮助

0x05 参考
=======

* * *

1.  互联网企业网络安全架构系列之六 —— 无线网安全 http://www.icylife.net/yunshu/show.php?id=822
2.  IEEE 802.1X 维基百科 https://zh.wikipedia.org/wiki/IEEE_802.1X
3.  认证协议5——EAP-TLS/EAP-TTLS/EAP-PEAP http://blog.chinaunix.net/uid-26422163-id-3457357.html
4.  无线网络安全指南 PEAP验证 http://www.windows7en.com/server/3140.html
5.  了解无线网络的 802.1X 身份验证 https://msdn.microsoft.com/zh-cn/library/cc759077(v=ws.10).aspx
6.  部署不当的PEAP-MSCHAP v2无线网容易被中间人劫持攻击 http://www.icylife.net/yunshu/show.php?id=813
7.  破解MSCHAPv2 http://www.icylife.net/blog/?p=10
8.  Cracking MS-CHAPv2 with a 100% success rate https://www.cloudcracker.com/blog/2012/07/29/cracking-ms-chap-v2/
9.  http://www.willhackforsushi.com/presentations/PEAP_Shmoocon2008_Wright_Antoniewicz.pdf