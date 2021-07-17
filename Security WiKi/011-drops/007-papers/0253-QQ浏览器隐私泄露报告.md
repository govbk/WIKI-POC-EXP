# QQ浏览器隐私泄露报告

source:citizenlab.org

0x00 简介
=======

* * *

QQ浏览器是腾讯开发的一款网络浏览器，面向Android，Windows，Mac和iOS等平台。相较于内置浏览器，QQ浏览器提供了更丰富的功能，例如，增加了标签窗口，并且整合了聊天平台等。

报告中详细的分析了Windows和Android版本的QQ浏览器是如何传输用户数据。这两个版本的QQ浏览器在传输用户的身份数据时，要么直接不使用加密，要么使用的加密算法简直形同虚设。完整的讨论内容请参阅我们的报告[《Baidu’s and Don’ts: Privacy and Security Issues in Baidu Browser》](https://citizenlab.org/2016/02/privacy-security-issues-baidu-browser/)。

由于这种数据传输方式非常不安全，所以只要能介入数据传输路径（比如，用户的ISP，连接了咖啡店的WiFi网络，或入侵了相应网络的黑客），收集并解密数据流量，就能够截获到这些个人数据。

除了数据传输方式不够安全，这两版QQ浏览器的更新方式也有漏洞，会导致任意代码执行。也就是说，攻击者可以伪造一个软件更新，将恶意代码安装到用户的设备上。

这份报告属于[《Privacy and Security of Mobile Applications in Asia》](http://https//citizenlab.org/tag/asia-chats/)系列。此前，我们已经确认了移动版的UC浏览器和百度浏览器也存在类似的问题。斯诺登也曾经曝光说，五眼情报联盟（NSA，GCHQ，CSE，ASD，GCSB）利用了UC浏览器中的安全问题来识别和跟踪用户身份。在已经公布的[《The Many Identifiers in Our Pockets》](https://citizenlab.org/2015/05/the-many-identifiers-in-our-pocket-a-primer-on-mobile-privacy-and-security/)报告中，我们列出了哪些个人数据是经常被收集和传输的。

另外，我们研究了TOM-Skype和UC上的密码审核机制，对比分析了一些在亚洲风靡的移动聊天工具，包括微信，LINE和KakaoTalk。除此之外，我们还检查了微信上的密码审核机制。这次研究的主要目的是通过一种综合性的方法，包括逆向工程和其他技术分析方法，让用户意识到这些应用中的安全和隐私问题，同时，希望相关的软件公司，承担起应有的责任，保护用户的权益。

2016年3月17日，我们询问了腾讯为什么要收集用户数据，并且还要通过一种不安全的方式将这些数据传输到QQ服务器。[这里](https://citizenlab.org/wp-content/uploads/2016/03/TencentLetter.pdf)是我们提出的具体问题。直至截稿，我们没有收到任何答复。在最后，我们讨论了一些可能的深层原因，为什么中国的这三款浏览器会出现类似的问题。

0x01 技术分析
=========

* * *

我们分析了两个版本的QQ浏览器，分别是安卓版6.3.01920和Windows版9.2.5478。在分析过程中，我们使用了大量的工具。比如，我们使用了tcpdump和Wireshark来捕捉和分析网络流量，也使用了机器代码和字节码反汇编工具，反编译器和调试工具来分析程序行为，包括，JD, JADX和IDA。

我们发现这两个浏览器都使用了一种通用机制与服务器通讯，而这种机制会导致个人信息的泄露，并且，这些浏览器的更新过程中也存在多个安全漏洞。

我们的技术分析分为三部分，第一部分介绍了一个基本结构，这两个版本的QQ浏览器都会通过这个结构向QQ服务器传输数据。第二部分分析了被采集的个人用户数据，以及安卓版的软件更新过程。第三部分分析了相应的Windows版功能。

0x02 第一部分：QQ浏览器的数据传输
====================

* * *

安卓和Windows版的QQ浏览器都使用了一种WUP请求与QQ服务器通讯。

### WUP请求

WUP请求是一种二进制格式，可以包含不同类型的值，例如，整数，浮点数，列表，字符串和递归结构。有时候，这些请求首先要经过加密，然后再嵌入到一个HTTP POST请求的主体中，最后，随着这个HTTP POST请求发送到目的URL。我们写了一个[Python脚本](https://citizenlab.org/wp-content/uploads/2016/03/TencentLetter.pdf)来解密并解析这些请求，从而将其转换成人类可读格式。在这个脚本的代码中，还包含了在接下来解密数据时需要用到的其他脚本。

### Q-GUID，Q-UA和Q-UA2字段

Q-GUID，Q-UA和Q-UA2字段出现在WUP请求的HTTP标头中。在接下来介绍WUP请求时，如果某个字段的对应值出现在了WUP请求的有效载荷中，我们就用这个字段来代指一个相应的实例。在HTTP标头中，这些字段都不会经过加密，但是，当这些字段出现在WUP请求中时，其格式会发生变化。

Q-GUID字段中填充的值是在初始化时，通过一个WUP请求从QQ服务器上获取的，并且在接收到这个值后，浏览器就会保留这个值，并且将其添加到后续请求的HTTP标头中，没有加密。在很多WUP请求的有效载荷中，也包含有这个值。下面就是一个Q-GUID：caed22d728efa6127d53bc0412f888cb

GUID可能表示的是“全局唯一标示符”，是一个128位数字，通常是随机生成的。

Q-UA和Q-UA2值中包含有与QQ浏览器版本和硬件平台相关的硬编码信息。虽然，UA很可能指的是“User Agent”，并且包含有与HTTP user agent字符串相似的信息，但是其格式却不同于QQ浏览器在HTTP标头中使用的user agent HTTP字段。

0x03 第二部分：分析安卓版QQ浏览器
====================

* * *

我们分析的安卓版QQ浏览器是6.3.01920版本，下载于[http://mb.qq.com/](http://mb.qq.com/)。在启动后，或执行了某些事件时，比如，浏览网页或检查更新，浏览器就会向`http://wup.imtt.qq.com:8080/`发送WUP请求。这些请求使用了下面的这种加密方式。

对于每个加密的WUP请求，会根据下面的Java代码来生成一个AES秘钥：

```
int i = 10000000 + new Random().nextInt(89999999);

    int j = 10000000 + new Random().nextInt(89999999);

    return (String.valueOf(i) + String.valueOf(j)).getBytes();

```

所以说，这个秘钥是一个128位秘钥，由16个ASCII数字组成。而且，第1个和第9个字节永远不可能是0，前8个和最后8个字节不可以全都是9，所以，秘钥空间并不是常规的`2^128`，而是`89999999^2 < 2^53`。

随后，这个秘钥会用于通过AES+ECB模式来加密WUP请求。AES秘钥会使用一个128位的RSA公钥加密，系数：245406417573740884710047745869965023463，指数：65537。加密后的AES秘钥会被纳入到HTTP请求的qbkey HTTP标头中。

RSA是一种非对称加密算法，也就是说，在解密时需要使用另一个不同的私钥，上面提到的RSA秘钥无法直接用于解密AES秘钥和WUP请求。但是，RSA的安全程度取决于加密秘钥的系数分解难度。一旦分解，解密秘钥就很容易获得了。上述的RSA公钥只有128位，分解起来并不难。（RSA秘钥一般建议至少2018位）。使用Wolfram Aplpha这个在线计算引擎，用不了1秒就可以分解秘钥的系数：

[http://www.wolframalpha.com/input/?i=factor+245406417573740884710047745869965023463](http://www.wolframalpha.com/input/?i=factor+245406417573740884710047745869965023463)

分解后，得到了下面两个质因数：

14119218591450688427 x 17381019776996486069

有了这些质因数，任何在监控流量的中间人都可以解密出每个WUP请求使用的AES秘钥，然后再使用AES秘钥解密WUP请求。

我们一直监控着浏览器发送的流量，并且使用这个秘钥解密了所有的WUP请求。多数WUP请求中传输的是一些很容易解密的个人信息。在图1中，是一个解密后的WUP请求，通过我们的脚本，可以将其解析成可读的形式。

![p1](http://drops.javaweb.org/uploads/images/29ca0f6acab7df6b45ef9573ce8add7c1dfcd008.jpg)图1-解密后的WUP请求。我们用“#”替代了敏感数字。

下面是我们识别出的一些重要请求，以及每个请求传输的个人信息：

| WUP请求 | 发送时间 | 加密程度 |
| --- | --- | --- |
| profileInfo.profileInfo | 浏览器启动时 | 简单加密 |
| hotword.getAssociationalWords | 输入地址栏时 | 不加密 |
| Security.doSecurityReqest [sic] | 浏览网页时 | 简单加密 |
| proxyip.getIPListByRouter | 浏览器启动时 | 简单加密 |
| pkgcenternew.checkUpdate | 检查更新时 | 简单加密 |

| 数据点 | 数据点描述 | 加密程度 | WUP请求 |
| --- | --- | --- | --- |
| IMEI | 国际移动设备标识码，每台设备对应一个唯一的字符串 | 简单加密 | profileInfo.profileInfoSecurity.do SecurityReqest proxyip.getIPListByRouter pkgcenternew.checkUpdate |
| IMSI | 国际移动用户标识码，每个用户对应一个唯一的数字 | 简单加密 | profileInfo.profileInfo |
| Q­GUID | QQ浏览器使用这个唯一字符串来识别用户身份 | 不加密 | hotword.getAssociationalWords Security.doSecurityReqest proxyip.getIPListByRouter |
| Q­UA2 | QQ浏览器使用这个值来识别应用版本和硬件平台的类型 | 不加密 | hotword.getAssociationalWords Security.doSecurityReqest |
| QQ username | QQ用户名 | 简单加密 | profileInfo.profileInfo |
| Screen pixel dimensions | 用户设备的屏幕尺寸 | 简单加密 | profileInfo.profileInfo |
| WiFi MAC address | 媒体访问控制地址，识别无线传输器的唯一标识，比如，设备上的蓝牙芯片和WiFi芯片 | 简单加密 | profileInfo.profileInfo* |
| In­range WiFi access point MAC addresses | 所有周边WiFi访问点的媒体访问控制地址 | 简单加密 | profileInfo.profileInfo proxyip.getIPListByRouter |
| SSID of connected WiFi access point | 用户连接的WiFi名称 | 简单加密 | proxyip.getIPListByRouter |
| Android ID | 在OS首次运行时，生成的一个唯一数字，用于追踪用户 | 简单加密 | pkgcenternew.checkUpdate |
| Address bar contents | 用户在地址栏中输入的内容（比如，搜索请求） | 不加密 | hotword.getAssociationalWords |
| Full page URL | 每个访问页面的完整URL | 简单加密 | Security.doSecurityReqest |

WiFi MAC地址通过DES+ECB模式加密，使用的秘钥是“`\x25\x92\x3c\x7f\x2a\xe5\xef\x92`”。

WUP请求的响应也很容易解密。WUP响应并没有使用前面提到的非对称加密算法，而是单纯使用了一种对称性算法，所以我们不需要分解任何秘钥的质因数。换句话说，其加密模式是MTEA+MCBC，使用的硬编码ASCII加密秘钥是：“`sDf434ol*123+-KD`”

很有趣的是，QQ浏览器的加密过程是非标准的MTEA+MCBC模式，和百度浏览器一样（见图4）。

因为这种算法是对称的，所以这些响应的加密和解密秘钥是同一个。任何中间人都可以利用这个秘钥，主动伪造一个来自QQ服务器的响应。我们通过攻击QQ浏览器的更新过程证实了这一点。

### 软件更新过程存在漏洞

通过pkgcenternew.checkUpdate请求的存在来看，软件更新是可用的。在这个请求的响应中可能会包含有下载新APK文件的链接，APK的MD5哈希和更新日志。在安卓上，如果APK更新使用的签名与当前安装的版本不符，那么APK更新就会失败；虽然，这种攻击方式无法将QQ浏览器替换成任意的APK；但是，这种方法可以用来安装新App，通过使用QQ浏览器的名称和图标，诱骗用户安装恶意的APK。

![p2](http://drops.javaweb.org/uploads/images/bc640feb11f3d3a983b1db4fb656ac89333fd6af.jpg)图2-中间人攻击QQ浏览器的更新过程。在左图中，我们可以插入任意的更新日志。在右侧，更新下载完成后，浏览器会提示用户安装愤怒的小鸟APK（攻击者可以将这个App的名称修改为“QQ浏览器”，使用与QQ浏览器相似的图标，从而诱使用户安装这个APK）

目前，由于Google Play商店无法在中国使用，所以中国的安卓用户必须通过其他途径来更新应用。因为无法使用Google Play商店的更新过程，所以，开发者必须自己实现自动更新机制，而这样则会导致程序的更新过程出现漏洞。据称，中国版的Google Play商店会在2016年上线。

0x04 第三部分：分析Windows版QQ浏览器
=========================

* * *

我们分析的Windows版QQ浏览器是9.2.5478版本，下载于[http://browser.qq.com/](http://browser.qq.com/)。虽然，Windows版的QQ浏览器也是通过WUP请求与服务器通讯，但是，采用了不同于安卓版本的加密方式和加密时间。而且，Windows版本使用了MTEA+MCBC算法来加密WUP请求，这是一种对称加密算法，而不是安卓版本上的非对称RSA算法（WUP响应都是采用了MTEA+MCBC算法进行加密，无论是安卓版本还是Windows版本）。

我们还发现，安卓版本的WUP请求都是发给了`http://wup.imtt.qq.com:8080/`，而Windows版本则是向多个URL发送了WUP请求，包括`http://qbwup.imtt.qq.com`，`http://wup.html5.qq.com`和`http://wup.imtt.qq.com:8080`。

通过WUP请求来看，Windows版QQ浏览器还会跟踪设备的硬件指纹。这里的硬件指纹指的是下列项目的MD5哈希：

1.  网络MAC地址
2.  硬盘序列号
3.  硬盘型号
4.  硬盘控制器版本号

比如：`md5(“080027B09CC2” + “VB7c666e15-ef97c40b” + “VBOX HARDDISK” + “1.0”)`

因为MTEA+MCBC是完全对称的，所以，任何能观察到流量的中间人都可以利用硬编码的加密秘钥，轻易地解密所有的WUP请求。和前面一样，我们监控了浏览器发送的流量并解密了所有的WUP请求。其中有多个WUP请求会泄露可解密的个人信息。下面是我们识别出的一些重要请求，以及每个请求传输的个人信息：

| WUP请求 | 发送时间 | 加密程度 |
| --- | --- | --- |
| devicesniffer.DeviceSnifferHandle | 浏览器启动时 | 简单加密 |
| login.login | 浏览器启动时 | 简单加密 |
| qbkpireportbak.stat | 浏览器启动时 | 简单加密 |
| qbpcstat.stat | 浏览器启动时 | 简单加密 |
| qbindexblacklist.testUrl | 在地址栏中发起搜索请求或输入URL时 | 不加密 |

WUP请求本身是没有加密的，但是其中的WUP有效载荷使用了DES+ECB算法进行加密（一种对称性的加密算法，解密起来很简单），使用的秘钥是“`\x62\xe8\x39\xac\x8d\x75\x37\x79`”。

| 数据点 | 数据点描述 | 加密程度 | WUP请求 |
| --- | --- | --- | --- |
| Hardware fingerprint | 网络MAC地址，硬盘序列号，硬盘型号，硬盘控制器版本号的哈希 | 不加密 | login.login qbkpireportbak.stat qbpcstat.stat qbindexblacklist.testUrl |
| Q-GUID | QQ浏览器使用这个唯一字符串来识别用户身份 | 不加密 | devicesniffer.DeviceSnifferHandle login.login* qbkpireportbak.statqbpcstat.stat qbindexblacklist.testUrl |
| Q-UA | QQ浏览器使用这个值来识别应用版本和硬件平台的类型 | 不加密 | login.login qbindexblacklist.testUrl |
| Machine IP Address | 用户设备的互联网协议地址 | 简单加密 | devicesniffer.DeviceSnifferHandle |
| Machine hostname | 用户的Windows主机名称 | 简单加密 | devicesniffer.DeviceSnifferHandle |
| Gateway MAC address | 用户计算机上，网关的媒体访问控制地址。 | 简单加密 | devicesniffer.DeviceSnifferHandle |
| Windows version and build | 用户计算进上的Windows版本和编译号 | 不加密 | qbkpireportbak.stat qbpcstat.stat qbindexblacklist.testUrl |
| Internet Explorer version | 用户计算机上的IE版本 | 简单加密 | qbkpireportbak.stat Qbpcstat.stat |
| QQ Browser version | 用户计算机上的QQ浏览器版本 | 不加密 | qbindexblacklist.testUrl |
| Hard drive serial number | 用户硬盘的唯一序列号 | 简单加密 | qbkpireportbak.stat qbpcstat.stat |
| Windows user security identifier | 随机生成的Windows用户唯一标示符 | 简单加密 | qbkpireportbak.stat qbpcstat.stat |
| Full page URL | 在地址栏中输入的每个页面的完整URL | 未加密 | qbindexblacklist.testUrl |

Q-GUID使用了3DES+ECB加密算法，使用的秘钥是“`\x63\xd7\x90\x63\x3c\x0e\x2f\xc3\x46\xef\x85\x37\x42\x1f\x9d\x4a\x46\x3d\x58\xf3\x8a\x95\xec\x84`”明文字节和随机字节交替出现，也就是说，第一个，第三个，第五个等字节是Q-GUID的第一个，第二个和第三个字节，而明文的第二，第四，第六等字节是随机选择的。

当用户访问了一个网页后，Windows版QQ浏览器也会通过WUP请求泄露用户信息。每个被访问页面的完整URL，无论是输入到地址栏，通过链接跳转，还是其他方式访问，都会经过MTEA+MCBC加密，发送到`http://masterconn.qq.com/`，使用的秘钥是“`\x8a\x0d\x75\x73\x90\x03\x4a\xd2\xb5\x25\xab\xe2\x31\xe2\x9f\x6f`”。

### 软件更新过程存在漏洞

软件更新检查是通过JSON发送给`http://update.browser.qq.com/qbrowser`。与安卓版本一样，更新请求和服务器返回的后续请求都没有经过加密，我们发现，Windows版本和安卓版本的区别在于，Windows版会验证更新包的数字签名。但是，我们发现了两种针对更新过程的攻击活动，任何中间人都可以通过主动攻击，在安装了QQ浏览器的设备上远程执行代码。

第一种攻击是目录遍历攻击。通常，当有更新时，QQ的服务器会在响应中给出EXE文件的下载链接，MD5哈希，新功能和修复简介，EXE的文件名和保存位置。我们发现文件名中出现了目录，通过目录遍历，攻击者可以覆盖用户有权限写入的任何文件。例如，将文件命名为`../../../../../../../../../program files/tencent/qqbrowser/qqbrowser.exe`，我们就可以用任意程序替换QQ浏览器，这样用户在下次执行QQ浏览器时，实际执行的就是我们的程序。攻击者可以利用这种攻击方式来安卓隐藏的间谍软件或木马。

第二种攻击方式说明了仅仅是验证数字签名还不足以认证软件更新的安全性。数字签名验证只是判断下载的EXE是不是由腾讯签名的，但是不会判断这个EXE会不会更新QQ浏览器-这个EXE可以是任何一个腾讯签名的程序。我们发现，旧版的QQ浏览器安装程序不会执行签名检查（这个安装程序本身只使用了对称加密），在更新时也是这样，我们使用了漏洞版本的QQ浏览器在线安装服务来“更新”用户的QQ浏览器，然后下载和执行我们选择一个EXE（图3）。

![p3](http://drops.javaweb.org/uploads/images/ff78b81ebd3cbd1b37ad6d5c1628a1496532d3df.jpg)图3-中间人攻击QQ浏览器的更新程序，首先注入一个有漏洞的在线安装程序，然后注入我们的程序。有效载荷是显示为“Oh Hai There”，但是，可以注入任意软件，比如间谍程序或木马。

0x05 讨论
=======

* * *

在这份报告中，我们指出了QQ浏览器中存在的一些很严重的安全漏洞。这个应用会收集和传输用户的身份数据，从而导致第三方可以监控到这些数据。另外，软件更新缺陷致使攻击者可以在用户设备上执行任意代码，比如第三方可以在用户的设备上插入恶意的间谍程序并执行。最让人讨厌的是用户还不一定能意识到风险的存在-没有意识到自己的数据会被收集，也可能不会意识到自己的设备上会被安装恶意代码。

但是，我们已经研究发现，这一问题并不仅限于某个特定的应用，操作系统或公司。我们分析的QQ浏览器，百度浏览器和UC浏览器-这三家世界知名科技公司-都爆出了相似的安全漏洞。所以说，不只有QQ浏览器会收集这些敏感的用户数据，并且不加密或简单加密就传输。考虑到这些相似性，需要从更广泛的移动安全和应用安全层面来评估这些安全问题，而不是集中在某一家公司或某个应用。

用户信任web浏览器会安全地处理用户输入的敏感信息并安全地将这些信息传输给web服务器。但是，QQ浏览器和其他的浏览器背弃了用户的信任，这些软件不仅仅在收集用户数据，还采用了一种不安全的传输方式。即使是使用了非对称加密，也没有能够坚持。安卓版的QQ浏览器使用了非对称的RSA算法，但是使用的秘钥太小，没有满足建议的2048位大小。这一缺陷要求开发者必须要使用经过考验的协议，比如OpenSSL这种广泛使用的方法能够更加安全地传输敏感数据。

除了批评这些应用的数据传输方式不够安全，更大的问题在于为什么要收集和传输这类个人数据。经由移动设备传输的个人身份数据成千上万，收集这些信息会导致严重的用户安全和隐私问题。然而，正是因为用户设备上的这些数据，开发者才能够提供高效的，高度定制化的服务，这些移动版浏览器收集的数据范围过大，很可能会引起用户的担忧-尤其是当厂商没有办法保证数据的安全。收集与用户身份，用户设备和用户在线行为相关的信息，很可能是为了监控高风险用户，在中国，可能包括民主人士，记者，人权支持者，律师等。