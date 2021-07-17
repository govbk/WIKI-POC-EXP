# 小窥TeslaCrypt密钥设计

**Author:Silver@XDSEC**

0x00 简介
=======

* * *

最近群里提到TeslaCrypt的作者放出了主密钥，简单看了下，对他的加密流程比较感兴趣。受条件限制，没有拿到早期样本（只拿到了晚一些的），放狗搜了搜也没找到，但是找到了两款解密程序。一款是Googulator开发的TeslaCrack，另外一款则是BloodDolly开发的TeslaDecoder。前者虽然开源，但支持解密的版本少于后者。本文通过分析及逆向样本和这两款工具，试图了解TeslaCrypt的设计思路。

下文中所有图片如无特殊说明，均为对BloodDolly开发的TeslaDecoder（简称“TD”）的逆向过程截图。

0x01 加密流程简述
===========

TeslaCrypt（以及AlphaCrypt，下文统称为“TC”）算是比较“成熟”的勒索软件，其版本从0.2逐步升级到目前已知的最高版本4.0+（也不知道有没有Insider Preview）。随着版本的升级，其加密和密钥处理技巧也在不断升级。

勒索软件的制作者为了打到目的，通常会给用户一个比特币钱包的地址。用户向该钱包付款之后，可以得到一个解密密钥，用此密钥即可解密。有报告指出，不同的受害者需要向不同的钱包中打款，这暗示着比特币钱包的生成过程可能与加密密钥的产生存在一定关联。因此，先大致了解下钱包是如何生成的。

![How to generate a btc addr?](http://drops.javaweb.org/uploads/images/8b8a9bcce7e77d36aaffa93132433b0b5f36336f.jpg)

比特币钱包生成的基本步骤是：

*   初始化一对可用于ECDSA签名的密钥Public/PrivateBtcKey
*   用SHA256对PublicBtcKey做蛤希，得到S256_PublicBtcKey
*   用RIPEMD-160对上一个结果做哈希，然后在哈希前部加入版本号得到VR160_S256_PublicBtcKey
*   在上一哈希前部加入版本号，并做两次哈希，将结果的前4字节附加在VR160_S256_PublicBtcKey后，最后使用Base58算法编码。这时得到的就是长33个字符的钱包地址。

如果想知道关于椭圆曲线算法的更多细节，有[一篇文章](https://www.certicom.com/index.php/ecc-tutorial)比较适合参考阅读。此外，TC还采用了ECDHE算法进行密钥交换，只是将DH里的非对称加密机制换成了椭圆曲线算法，其他变化不大，可以参考[这里](http://thecodeway.com/blog/?p=964)获得更多细节。

TC被首次载入时，就生成了一对PublicBtcKey/PrivateBtcKey。其中，PublicBtcKey就是向用户显示的地址，而PrivateBtcKey则被发送给C&C服务器，以进行之后的转账操作。不同版本的TC，这一点是不变的。

TC作者本次公布的密钥是四号密钥，应用于TC3.0以及TC4.0版本。这两个版本都采用了比较完整的分层密钥机制，并且提高了样本隐蔽性。TC4.0的准备过程如下：

*   准备随机数生成器等；
*   生成随机数，并用714号曲线（即secp256k1）建立比特币钱包，对应密钥Public_BtcKey和Private_BtcKey；
*   对Private_BtcKey做SHA-256哈希，得到Private_HashedPRBK，用Public_BtcKey算出钱包地址，一会展示给客户；
*   用Private_HashedPRBK带入曲线，得到第二对密钥Public_HashedPRBK；
*   此外，TC的作者还拥有一对密钥Public/Private_MalMaster。这对密钥里，Public_MalMaster是由TC作者置入程序的，而Private_MalMaster则是本次被作者公布的“主密钥”，难以被运算出来；
*   再生成用于加密传输数据的第三对密钥Public/Private_Master；
*   用Private_Master和Public_MalMaster计算，得到用于对称加密的密钥Secret_Master；
*   以Secret_Master作为AES的密钥，用AES_CBC方法，加密比特币钱包的私钥Private_BtcKey，得到加密后的结果Encrypted_PRBK；
*   将Encrypted_PRBK和Public_Master发送给CC端；
*   攻击者由Public_Master和Private_MalMaster算得Secret_Master；
*   用Secret_Master将Encrypted_PRBK解密为Private_BtcKey，得到可以收款的BTC钱包地址；
*   计算Private_BtcKey的哈希值Private_HashedPRBK，作为收到付款之后返回客户的密钥；

现在TC已经做好了加密准备。TC的加密是以一个session为一环的，每次重启、关闭计算机，都会终止当前的session，并启动一个新的session。每次session里的加密细节是：

*   生成一个Private_SessionKey和一个SessionIV，作为本次session里对文件进行加密的密钥和CBC模式的初始化向量。
*   依据Private_SessionKey生成对应的密钥对Public_SessionKey，并保存；
*   用Private_SessionKey和Public_HashedPRBK生成一个用与对称加密的密钥Secret_Session；
*   用Private_SessionKey加密目标文件，得到Encrypted_FILE；
*   用Secret_Session加密Private_SessionKey得到Encrypted_PSSK；
*   立刻冲洗Secret_Session和Private_SessionKey的存储区域；

按照攻击者的设定，用户在被攻击后，应该使用下面的流程来解密文件：

*   向Public_BtcKey对应的钱包里付款；
*   确认Private_BtcKey里收到付款后，向客户返回Private_HashedPRBK；
*   对每个文件：
    *   依据Private_HashedPRBK和Public_SessionKey，计算得出Secret_Session；
    *   依据Secret_Session解密Encrypted_PSSK，即可得到Private_SessionKey；
    *   依据Private_SessionKey解密Encrypted_FILE，即可得到源文件；

在TC4.0中，作者在每个文件头里都保存了三个对解密必不可少的值：

*   SessionIV
*   Public_SessionKey和Encrypted_PSSK

此外还保存了：

*   Public_Master（同时发送给CC）
*   Encrypted_PRBK（同时发送给CC）
*   Public_HashedPRBK
*   原始文件长度

而且，在密钥没有保存意义后，立刻用数据对相应的存储区域进行清洗，防止安全/取证软件获取到解密密码。通过这里也可以看出，病毒作者通过分析一些专杀工具和解密工具，对自己的技术也进行了升级。密钥的分层机制也比较明确，在网络里传输的数据，如果没有Private_MalMaster，是无法解密BTC钱包地址的，而SessionKey的解密又依靠这个地址，从而保证除了攻击者没有第三方可以绕过逻辑解密文件。最后完成的3.x和4.x版本，基本可以作为密码学应用的示范程序。在作者公布密钥后，TD也嵌入了密钥，并实现了上述的解密过程。

0x02 部分漏洞分析
===========

* * *

TC的老版本则没有新版本这么“安全”了。对加密通道运用不当是比较常见的错误，在TC中也由发现。这是最早修复的漏洞，一个比较标志性的版本是v6，在v6之前，所有的文件都可以通过抓取感染后向CC通信的网络流量来解密，但v6版本开始，这一做法便不能使用了。一种合理的猜想是，在旧版本的软件中，可以直接解析出加密密钥。对TD的分析证实了这一点。下图是TD获取网络流量后，判定密钥与比特币地址是否相符的（以免解密错误）：

![Judge if bitcoin addr is correct](http://drops.javaweb.org/uploads/images/aad3a8f3306f27fe213be96c0364bbd7ac11c6dc.jpg)

之后，TD便将密钥放入对应区域中，其他操作则与正常解密类似：

![Put the key back](http://drops.javaweb.org/uploads/images/9efa9c24449bb4c09f2390a942bb0597525609d3.jpg)

从V2版本到V5版本的TC，将传输的私钥以特定方式进行的加密，各版本的密钥也有所不同，但由于密钥是硬编码在程序里的，因此仍可以被TD直接提取出来，这就很尴尬了：

![Hard-coded key](http://drops.javaweb.org/uploads/images/a60c6ed49de671d072be083b37462edb352099d1.jpg)

从TD的验证逻辑推断，旧版本的TC应该是向CC服务器直接发回了BTC地址和Private_BtcKey（或简单加密后的Private_BtcKey）：

![Filter key out of network request](http://drops.javaweb.org/uploads/images/843f902784af1cf144b15e0755516054ec9ef634.jpg)

因此，在v5版本的某个变种中，TC作者移除了部分数据，使TC无法验证网络请求中的BTC地址和私钥是否相符，并在v6版本完全修改了向CC传输的数据，不再在通信中直接暴露加密密钥，彻底的封堵了这个逻辑漏洞。然而，利用这个漏洞，需要用户持续收集网络流量，这在很多环境下不容易实现，因此这种方法的利用难度比较高。

第二个漏洞存在于TC的前两个版本中。有一种比较简单的方法，利用的主要是在加密设计过程中的漏洞。由于对数据存储区域清洗不彻底，部分解密密钥可能残留在key.dat和注册表中。获取了部分密钥，可以极大的降低TD的解密难度，而且由于设计过程问题比较严重，这样获得的密钥不是SessionKey而是用户主密钥，这样就可以直接解密所有文件了：

![Get the key directly](http://drops.javaweb.org/uploads/images/9bda5e37875a2e3bf8a9e32593978809f34edcfc.jpg)

这个漏洞比较容易利用，修补难度也不高，因此只存活了两个版本，就被勤劳的地下工作者修好了。

第三个漏洞就相对不太好利用。V7之前旧版本TC的弱点在于，在目标文件中保留了“RecoveryKey”或与之相似的参数。这个参数是由一个私钥和用于加密该私钥的乘积，其存在意义不明，位置和数量也随版本变化。比如在.xyz格式的文件中，0x108偏移处的130个字节，保存的是文件私钥Private_SessionKey与文件私钥加密密码Secret_Session的乘积。显然，这个积可以被分解为多个质数的乘积，而Private_SessionKey的值可以由这些质数中的一个或多个相乘而来。这样就产生了一个爆破思路：

*   分解乘积为素数表M
*   循环取M中的素数，计算乘积m
*   计算m在secp256k1模式下对应的公钥值n
*   验证n与Public_SessionKey是否相符。如果相符，则可用

这种方法能成功有两个主要因素。最重要的一个是由于乘积的存在，增加了信息量，也就弱化了保密特性。而另一个因素则是由于攻击者在这里采用了椭圆曲线算法。这种算法的保密关键点在于，解决ECDLP是困难的（在曲线Ep上给定一个点G，取任意一个整数k，那么可以证得点P=k*G容易在同一条曲线上找到。但是，如果选择适当的参数，那么在已知P、G的情况下，求出k的群操作太慢了，而把G和Ep规定好，令k为私钥，P为公钥，就是椭圆曲线加密的基本原理），而不再一味依靠密钥的位数。因此，在操作中，考虑到时间问题，一般把私钥设定在160~300位，即使与RSA1024相比，这个长度也短的多，因此更容易被从素数表中挖掘出来（这里的“更”是相对与RSA1024来说的，实际上也需要相当量的算力和运气）。解决这个漏洞比较简单，可以修改加密流程，也可以简单的删除这个乘积。因此，在V7以及之后的版本中，取消了这个乘积数据，这样对V7和V8版本的解密就只能依靠攻击者给出的密钥才能解密了。

以上是我根据旧版本Teslacrypt的解密代码，了解到的一些漏洞信息。自己的密码学比较菜，如有不妥，还希望各位给一点人生的经验。

0x03 相关链接
=========

* * *

*   英文Wiki有很多关于密码学的文章，此外关于ECC有一篇较为可靠的文章也可参考，来自[看雪论坛](http://www.pediy.com/kssd/pediy06/pediy6014.htm)
*   消息源：[Solidot](http://www.solidot.org/story?sid=48297)
*   BTC钱包生成：[Bitcoin.it](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses)
*   如果你主要关注样本行为：[乌云](http://drops.wooyun.org/papers/14671)，[SecureWorks](https://www.secureworks.com/research/teslacrypt-ransomware-threat-analysis)，以及[Cisco](https://blogs.cisco.com/security/talos/teslacrypt)
*   [启明星辰](http://www.venustech.com.cn/UserFiles/20160512_%E7%89%B9%E6%96%AF%E6%8B%89%E6%81%B6%E6%84%8F%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90%E6%96%B0%E8%A7%A3(1).pdf)对该软件的分
*   利用第三个漏洞的代码：[Github](https://github.com/Googulator/TeslaCrack)
*   对第三个漏洞的介绍：[BleepingComputer.com](http://www.bleepingcomputer.com/news/security/teslacrypt-decrypted-flaw-in-teslacrypt-allows-victims-to-recover-their-files/)