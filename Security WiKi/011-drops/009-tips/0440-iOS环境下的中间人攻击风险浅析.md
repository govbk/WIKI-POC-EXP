# iOS环境下的中间人攻击风险浅析

**作者：轩夏**

0x00概述
======

* * *

中间人攻击（Man-in-the-Middle Attack，简称“MITM攻击”）是一种“间接”的入侵攻击，这种攻击模式是通过各种技术手段将受入侵者控制的一台计算机虚拟放置在网络连接中的两台通信计算机之间，这台计算机就称为“中间人”。通过中间人攻击可以窃取信息、进行篡改、欺骗等多种攻击。

对于Android平台上的中间人攻击已经讨论的比较多，今天来聊聊iOS平台上的中间人攻击，以及iOS的可信证书管理。

0x01中间人攻击
=========

* * *

在未做特殊说明的情况下，本文所有实验环境为：

iPhone 5 + iOS 8.1.2 + 已越狱。

1.1. 中间人攻击分级
------------

iOS平台上根据中间人攻击的难度，可以将中间人攻击分为3个等级：

1) level1:在没用向手机中安装攻击者证书的情况下可以进行中间人攻击

2) level2:在向手机中安装攻击者证书的情况下可以进行中间人攻击

3) level3:在向手机中安装攻击者证书的情况下也不可以进行中间人攻击

对于这三种情况，我们以一个例子分别对这三种情况进行说明。借用Owasp关于iOS https中间人演示的例子，稍做修改。正常情况下，程序启动时如图1，点击“Fetch Secret”程序请求server端数据并显示，如图2。

![](http://drops.javaweb.org/uploads/images/b4ba99b66d847b43c082e8f5d998fc041206d5d1.jpg)

图 1 启动界面

![](http://drops.javaweb.org/uploads/images/b6b6a00cf2a07530728e3ad9129e0005fb654ee8.jpg)

图 2 正常获取数据

### 1.1.1. 不导入证书可中间人

在此次连接的NSURLConnection对象的delegate类中只实现一个`connection:didReceiveAuthenticationChallenge:`方法，如图3。

![](http://drops.javaweb.org/uploads/images/7fc4ac6424cc25cfe657d6800427b04fe8937eb4.jpg)

图 3 连接校验方法

设置burp suite，开启代理，如图4。

![](http://drops.javaweb.org/uploads/images/fdc28e4debe58831a409bd593270a7f4b30b8452.jpg)

图 4 burp suite设置

手机设置代理为burp suite运行pc的地址，如图5。

![](http://drops.javaweb.org/uploads/images/f141d41e0196ef7dc7386f2ce7d2dd5a93af1c4a.jpg)

图 5 手机代理设置

运行程序，点击“Fetch Secret”，程序正常获取到了与图2相同的数据，burp suite也截获了所有信息，如图6，中间人攻击成功。

![](http://drops.javaweb.org/uploads/images/a9f7c6f6d339c4773a7e2e5f5968cc7e7acdbfe3.jpg)

图 6 burp suite截获数据

### 1.1.2. 导入证书可中间人

修改程序，在NSURLConnection对象的delegate类中实现`connection:willSendRequestForAuthenticationChallenge:`方法，如图7。

![](http://drops.javaweb.org/uploads/images/c60ff65236ef819680c7ea1cb061143f6eb49d96.jpg)

图 7 连接校验方法

其他设置与1.1.1小节完全相同，程序发现连接异常，终止获取数据，如图8，burp suite也理所当然获取数据失败。

![](http://drops.javaweb.org/uploads/images/a6bbd53ac10ca9f0ea5781dbfb959e8f220ea283.jpg)

图 8 获取数据失败

此时，向手机中安装burp suite证书，如图9。

![](http://drops.javaweb.org/uploads/images/874126aa681c37281faaa1dd6c75015e9ad63399.jpg)

图 9 安装burp证书

重新打开应用，点击“Fetch Secret”，应用正常获取数据，burp suite也截获了全部数据，中间人攻击成功。

### 1.1.3. 导入证书不可中间人

继续对程序进行修改，将公钥证书放入应用中，并修改`connection:didReceiveAuthenticationChallenge:`方法在连接过程中获取证书信息，对server端证书进行强校验，如图10。同时，注释掉`connection:willSendRequestForAuthenticationChallenge:`方法，因为如图实现了这个方法，方法`connection:didReceiveAuthenticationChallenge:`将不会被调用。

![](http://drops.javaweb.org/uploads/images/3dc318dce43936485613b79cf141339cc3e62ecc.jpg)

图 10 连接校验方法

其他设置不变，手机中依然安装有burp suite证书，打开应用，点击“Fetch Secret”，应用无法正常获取数据，如图11，burp suite也不能截获数据，中间人攻击失败。

![](http://drops.javaweb.org/uploads/images/7f30bb2b68e26f0af2cfc14c2de0c28c2581320f.jpg)

![](http://drops.javaweb.org/uploads/images/550c4d1573d13b58613395c115b05ab15b7a3759.jpg)图 11 证书错误

### 1.2.4一些建议

一般来说，建议应用信任手机中的所有证书即可，在应用中置入公钥证书对连接进行强校验确实最为安全，但会引发诸多问题，如证书更新、证书过期、证书作废等。

如果需要更新客户端证书，都必须升级客户端版本，而升级客户端是一个较为漫长的过程。 例如证书被黑客窃取，需要紧急作废证书，而许多用户却有没有及时升级客户端的习惯，这将可能导致大面积用户使用出现网络异常的情况。就目前来看，也确实很少看到有应用将安全级别做到level3。

0x02可信证书管理
==========

* * *

上一章节中谈到向手机中导入可信证书的问题，小生在编写一个iOS工具的时候无意发现iOS证书管理的一个有趣的地方。通过“Settings”->“General”->“Profiles”可以查看当前设备信任的证书列表，但这个列表就真的是设备信任的证书列表吗？

2.1奇葩的中间人攻击情形
-------------

按照上一章节建议，将应用防中间人级别设置为level2，即应用信任当前设备上的所有证书，如果要使用burp suite对该应用进行中间人攻击，需要向设备中安装burp的证书，而目前设备上的信任证书如图12所示，设备上只有一个用于连接公司内网的员工证书。

![](http://drops.javaweb.org/uploads/images/964267f18395e1998b0b94e7a0c0ea8eeabdca0c.jpg)

图 12 证书列表

在这样的情况下，burp suite应该不能获取到应用的通信内容，而结果如何了。为了排除结果受到iOS系统在https通信时的10分钟缓存机制，先对设备进行重启或静置10分钟；启动应用进行通信，发现应用正常获取到了与图2所示相同的数据，而burp suite也成功截获了与图6所示相同的通信内容。这是什么鬼……

2.2 TrustStore.sqlite3
----------------------

iOS系统下有一个有一个sqlite3文件，其绝对路径为：

`“/private/var/Keychains/TrustStore.sqlite3”`

该文件中存储的才是当前设备真正信任的证书列表，而通过“Settings”->“General”->“Profiles”查看到的证书列表与该文件中存储的证书列表可以不同步，如果我们手动对该sqlite3文件进行更改，就能让手机实际的可信证书列表与在“Profiles”中看到的完全不一样。小生写了一个工具，对该sqlite3文件进行管理，查看该文件中的存储，如图13。

![](http://drops.javaweb.org/uploads/images/5eeb8f8a56645bf1ff0134fce82afbabfdb522b1.jpg)

图 13 证书列表

其中，ID为0的证书是图12中看到的用于连接公司内网的员工证书；ID为1的证书为burp suite证书，而这张证书没有在“Profiles”中显示。这就是导致能中间人的原因。

我们删除掉该sqlite3文件中的ID为1的证书，如图14，并对设备进行重启或静置10分钟，再进行2.1章节中的实验。

![](http://drops.javaweb.org/uploads/images/479007ac49239afa94db87c0e3a783e3b51e1ca5.jpg)

图 14 删除burp证书

打开应用，点击“Fetch Secret”，应用报错，如图15。

![](http://drops.javaweb.org/uploads/images/ffa7d05e91ed0f0453d41c4e7a617e7cd2daf70f.jpg)

图 15 证书错误

如果重新将burp suite证书手动插入TrustStore.sqlite3文件中，如图16，并对设备进行重启或静置10分钟，再进行2.1章节中的实验，发现中间人攻击成功。而本文中对TrustStore.sqlite3文件的所有手动操作，都不会影响到“Profiles”中的任何显示，“Profiles”始终只显示一张员工证书。

![](http://drops.javaweb.org/uploads/images/9a35b0e4776a1eb95ac0f296c7acced9716c9047.jpg)

图 16 插入证书

2.3不显示证书的中间人攻击（越狱后环境）
---------------------

根据2.1和2.2小节的描述，如果攻击者通过越狱插件、甚至是通过某些猥琐手段逃过App Store检查的恶意应用，对已越狱的iphone手机上的文件“`/private/var/Keychains/TrustStore.sqlite3`”进行修改，向其中插入了一张攻击者证书，例如burp suite证书，攻击者就可以在受害者的网关上神不知鬼不觉的进行中间人攻击（当然level3安全级别下的应用是没门的），受害者完全不知情，因为受害者通过“Settings”->“General”->“Profiles”查看可信证书的时候，不会发现任何异常，即可以在不显示证书的情况下窃取受害者数据、进行篡改等。

所以，对于已越狱的手机，不要以为“Settings”->“General”->“Profiles”下没有安装一些奇奇怪怪的证书就高枕无忧了。

0x03小节
======

* * *

iOS系统的中间人攻击方法与防范措施，总结在在0x01章节中，小生认为普通应用只需要信任当前设备上的所有可信证书即可。关于iOS系统的可信证书列表，越狱过的朋友还是去检查下“`/private/var/Keychains/TrustStore.sqlite3`”文件中是否有“Profiles”中未显示或显示不对等的情况。