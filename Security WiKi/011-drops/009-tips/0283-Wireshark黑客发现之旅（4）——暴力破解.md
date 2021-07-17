# Wireshark黑客发现之旅（4）——暴力破解

作者：Mr.Right、K0r4dji

申明：文中提到的攻击方式仅为曝光、打击恶意网络攻击行为，切勿模仿，否则后果自负。

一、个人观点
======

* * *

暴力破解，即用暴力穷举的方式大量尝试性地猜破密码。猜破密码一般有3种方式：

**1、排列组合式**：首先列出密码组合的可能性，如数字、大写字母、小写字母、特殊字符等；按密码长度从1位、2位……逐渐猜试。当然这种方法需要高性能的破解算法和CPU/GPU做支持。

**2、字典破解**：大多攻击者并没有高性能的破解算法和CPU/GPU，为节省时间和提高效率，利用社会工程学或其它方式建立破译字典，用字典中存在的用户名、密码进行猜破。

**3、排列组合+字典破解相结合**。 理论上，只要拥有性能足够强的计算机和足够长的时间，大多密码均可以破解出来。

暴力破解一般有两种应用场景：

1、攻击之前，尝试破解一下用户是否存在弱口令或有规律的口令；如果有，那么对整个攻击将起到事半功倍的作用。

2、大量攻击之后，实在找不出用户网络系统中的漏洞或薄弱环节，那么只有上暴力破解，期待得到弱口令或有规律的口令。 所以，用户特别是管理员设置弱密码或有规律的密码是非常危险的，有可能成为黑客攻击的“敲门砖”或“最后一根救命稻草”。

暴力破解应用范围非常广，可以说只要需要登录的入口均可以采用暴力破解进行攻击。应用层面如：网页、邮件、FTP服务、Telnet服务等，协议层面如：HTTP、HTTPS、POP3、POP3S、IMAP、IMAPS、SMTP、SMTPS、FTP、TELNET、RDP、QQ、MSN等等。本文仅列举部分常见协议，其它协议情况类似。

二、正常登录状态
========

* * *

要从通信数据层面识别暴力破解攻击，首先我们得清楚各种协议正常登录的数据格式。下面我们来认识一下POP3/SMTP/IMAP/HTTP/HTTPS/RDP协议认证过程的常见数据格式，根据服务器类型的不同格式略微不同。（说明：本章使用服务器环境为Exchange2003和WampServer）

### 1、POP3协议

![enter image description here](http://drops.javaweb.org/uploads/images/2f24c862694483d3eeaa8aaaa1a474abe1502abc.jpg)

```
+OK Microsoft Exchange Server 2003 POP3 .......... 6.5.6944.0 (a-ba21a05129e24.test.org) ........   //服务器准备就绪
CAPA   //用于取得此服务器的功能选项清单
+OK Capability list follows
TOP
USER
PIPELINING
EXPIRE NEVER
UIDL
.
USER jufeng001@test.org    //与 POP3 Server 送出帐户名
+OK
PASS 1qaz@WSX    //与 POP3 Server 送出密码
+OK User successfully logged on.   //认证成功
STAT
+OK 14 21568
QUIT
+OK Microsoft Exchange Server 2003 POP3 .......... 6.5.6944.0 ..........

```

### 2、SMTP协议

![enter image description here](http://drops.javaweb.org/uploads/images/f8fce7d56084ab5d3af3fcb0ecb5d8809106679f.jpg)

```
220 a-ba21a05129e24.test.org Microsoft ESMTP MAIL Service, Version: 6.0.3790.3959 ready at  Thu, 6 Aug 2015 11:10:17 +0800  //服务就绪
EHLO Mr.RightPC //主机名
250-a-ba21a05129e24.test.org Hello [192.1.14.228]
……
250 OK
AUTH LOGIN  //认证开始
334 VXNlcm5hbWU6  // Username:
anVmZW5nMDAxQHRlc3Qub3Jn  //输入用户名的base64编码
334 UGFzc3dvcmQ6  // Password:
MXFhekBXU1g=   //输入密码的base64编码
235 2.7.0 Authentication successful.    //认证成功

```

### 3、IMAP协议

![enter image description here](http://drops.javaweb.org/uploads/images/662034b1f33e956766b3b0f0bbd193f929cfce7f.jpg)

```
* OK Microsoft Exchange Server 2003 IMAP4rev1 .......... 6.5.6944.0 (a-ba21a05129e24.test.org) ........     //IMAP服务就绪
bf8p CAPABILITY
* CAPABILITY IMAP4 IMAP4rev1 IDLE LOGIN-REFERRALS MAILBOX-REFERRALS NAMESPACE LITERAL+ UIDPLUS CHILDREN
bf8p OK CAPABILITY completed.
s3yg LOGIN "jufeng002" "1qaz@WSX"        //输入用户名:jufeng002，密码:1qaz@WSX
s3yg OK LOGIN completed.     //认证成功

```

### 4、HTTP协议

HTTP协议认证格式较多，这里仅列一种作为参考。

![enter image description here](http://drops.javaweb.org/uploads/images/22160b28d50fda03455323bd525369a3b53806fe.jpg)

```
Referer: http://192.1.14.199:8080/login.html     //登录地址
uname=jufeng001&upass=1qaz%40WSXHTTP/1.1 200 OK
…
<script>alert('OK')</script>
//输入用户名jufeng001，密码1qaz%40WSX，Web服务器返回HTTP/1.1 200和弹出对话框“OK”表示认证成功。

```

### 5、HTTPS协议

HTTPS协议为加密协议，从数据很难判断认证是否成功，只能根据数据头部结合社会工程学才能判断。如认证后有无查看网页、邮件的步骤，如有，就会产生加密数据。

![enter image description here](http://drops.javaweb.org/uploads/images/931476974eca9a693bf6b3d52d3ed2adbaf34979.jpg)

从数据中可看出HTTPS头部有认证协商的过程，认证后有大量加密数据，基本可判断认证成功。SSL认证过程见下图：

![enter image description here](http://drops.javaweb.org/uploads/images/bde244275944806a1bc520da6e7df428692e5646.jpg)

### 6、RDP协议

RDP为Windows远程控制协议,采用TCP3389端口。本版本采用的加密算法为：128-bit RC4；红线内为登陆认证过程，后为登陆成功的操作数据。

![enter image description here](http://drops.javaweb.org/uploads/images/87e1807568e6be8f22a5cb01002da351872e63e2.jpg)

三、识别暴力破解
========

* * *

从暴力破解的原理可知，攻击中会产生大量猜试错误的口令。一般攻击者在爆破前会通过其他途径搜集或猜测用户的一些用户名，相关的字典和爆破算法，以提高效率。

### 1、POP3爆破

![enter image description here](http://drops.javaweb.org/uploads/images/cc57a84ac20d14eebc73734165280467a6dba85d.jpg)

从图中可发现，攻击者不断输入用户名jufeng001，不同的密码进行尝试，服务器也大量报错：`-ERR Logon failure: unknown user name or bad password`。Follow TCPStream可以看得更清楚。

![enter image description here](http://drops.javaweb.org/uploads/images/be6f3f5aeaa630fcdff10d0c69c2fa6435e1cb61.jpg)

提取所有信息，就可以知道攻击者猜破了哪些用户名、哪些口令。

### 2、SMTP爆破

SMTP协议往往是用户邮件安全管理的一个缺口，所以多被黑客利用。

![enter image description here](http://drops.javaweb.org/uploads/images/d4fcdfc87b667e5bce52d6cea747cae2915b762d.jpg)

从图中可发现，攻击者不断输入用户名jufeng001，不同的密码进行尝试，服务器也大量报错：`535 5.7.3 Authentication unsuccessful`。Follow TCPStream：

![enter image description here](http://drops.javaweb.org/uploads/images/40c2d570b59d339c6de8742bb619e2a4ebe3f124.jpg)

### 3、IMAP爆破

从下面两张图可以看出，IMAP爆破会不断重复LOGIN "用户名" "密码"，以及登录失败的报错：`NO Logon failure: unknown user name or bad password`。

![enter image description here](http://drops.javaweb.org/uploads/images/baefcfa296d84b88a5b391f05c3f2e538ab11b8f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/a351f967c5c2c97a3f72604f35fa1a5529f36967.jpg)

### 4.HTTP爆破

由于大量Web服务器的存在，针对HTTP的爆破行为也可以说是最多的，研究爆破方法和绕过机制的人也比较多。这里仅用最简单的Web实验环境做介绍。

首先打开数据可以看到，短时间内出现大量登录页面的请求包。

![enter image description here](http://drops.javaweb.org/uploads/images/da6f1aada25e37dcbfe71bae751587fcbf558264.jpg)

提取Follow TCPStream可以看见输入用户名、密码情况，服务器返回值不再是登录成功的“OK”，而是登录错误的“…………”。

![enter image description here](http://drops.javaweb.org/uploads/images/65f38e4180b0a57f9156b3d4a225fc9eb3b9d53d.jpg)

以上的“…………”并不是返回无内容，这是由于Wireshark无法识别该中文的编码的原因，我们可以点击Hex Dump看一下十六进制编码的内容。

![enter image description here](http://drops.javaweb.org/uploads/images/63e108ed65a084f0172193051689514c66d24033.jpg)

将提取Follow TCPStream的信息另存为1.html，用浏览器打开。

![enter image description here](http://drops.javaweb.org/uploads/images/016b6a224718c8e1d2444cbda591bdafcbd1bc1a.jpg)

### 5.HTTPS爆破

HTTPS包括其它SSL协议的爆破从通信层面监控有一定的难度，因为认证过程加密了，无法知道攻击者使用的用户名、密码以及是否认证成功。但从爆破的原理可知，爆破会出现大量的登录过程，且基本没有认证成功，更不会有登录成功的操作过程。

如图：爆破过程中，不断出现认证过程：“`Client Hello`”、“`Server Hello`”等，并未出现登录成功后操作的大量加密数据。

![enter image description here](http://drops.javaweb.org/uploads/images/661816bc6591f21fbfca8b71a5b3156f608d9b5d.jpg)

点击Info可发现，在不到2秒的时间就出现16次认证，基本可以判断为暴力破解。

![enter image description here](http://drops.javaweb.org/uploads/images/a9d664304ad3ee6e6903fab7609e5a0feb943996.jpg)

### 6.RDP爆破

RDP爆破在黑客攻击中应用非常多，一旦破解出登录密码，基本可以控制这台机器。由于RDP协议数据也加密了，对于爆破的识别也有一定的困难，下面介绍另外一种方法快速识别，这种方法同样适用其它协议的爆破。

首先我们统计一下正常登录RDP协议的TCP端口等信息，可以看出正常登录的话，在一定时间内是一组“源端口和目的端口”。

![enter image description here](http://drops.javaweb.org/uploads/images/094a64835c416f1c04b6cf9a3d73e42dae243786.jpg)

再来看一下爆破RDP协议的TCP端口等信息，可以看出短时间内出现大量不同的“源端口和目的端口”，且包数和字节长度基本相同。这就表明出现大量动作基本相同的“短通信”，再结合数据格式就可以确定为暴力破解行为。

![enter image description here](http://drops.javaweb.org/uploads/images/b13b071844102642afcf021ab09f46e5488e7cc0.jpg)

### 7.多用户同时爆破

为提供命中率，攻击者往往会搜集大量的用户名作为字典同时开展爆破，希望达到“东方不亮西方亮”的效果。这种爆破方法同样很好识别，它的通信原理为：同一个攻击IP同时登录大量不同的用户名、尝试不同的口令、大量的登录失败的报错。

下图为同时对jufeng001、jufeng002、jufeng003、jufeng004等用户开展爆破的截图。

![enter image description here](http://drops.javaweb.org/uploads/images/931a573f76c6a6e69a59572981192a6debeb1afe.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/613eee66a09d75199b16fa774c729e57c777a4cd.jpg)

### 8、如何识别爆破成功

当然，发现爆破攻击行为仅仅是工作的一部分，更重要的是要清楚攻击者到底爆破是否成功，如果成功了会对我们造成什么影响。下面就基于Wireshark来介绍如何发现爆破成功。

（1）首先我们要清楚攻击者爆破的协议，以及该协议登录成功服务器返回值。如下图，为POP3的爆破，从前面的介绍我们知道如果登录成功服务器返回：“`+OK User successfully logged on`”。

![enter image description here](http://drops.javaweb.org/uploads/images/50d177ce9f7c28756f69c1c988114b15a2be4e46.jpg)

2）在数据中搜索“`+OK User successfully logged on`”。

![enter image description here](http://drops.javaweb.org/uploads/images/fb72ffd1360f7ef521cd0eba94fcf147e0991f0e.jpg)

（3）通过搜索发现确实存在服务器返回的成功登录信息。

![enter image description here](http://drops.javaweb.org/uploads/images/6ba8b572aa8c4a103d0223826b903b0e1348fc7d.jpg)

（4）Follow TCPStream发现攻击者在尝试了大量错误口令后，终于爆破成功：用户名jufeng001，密码1qaz@WSX。

![enter image description here](http://drops.javaweb.org/uploads/images/1474a073c7f30cbbac63c685bd4069f437e326cd.jpg)

四、总结
====

1、无论是用户还是管理员，我们都要重视弱口令或有规律的口令这个安全问题，不要让安全防范输于细节。

2、验证码机制防范暴力破解仅适用于HTTP/HTTPS协议，无法防范其它协议。

3、理解了暴力破解的通信原理，从通信层面进行监控和阻止就可以实现。

4、重要管理系统的登录权限受到爆破攻击行为较多，登录权限最好绑定管理员常用的IP地址或增加认证机制，不给黑客爆破的机会。