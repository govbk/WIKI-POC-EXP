# KeyRaider：迄今最大规模的苹果账号泄露事件

from:[KeyRaider: iOS Malware Steals Over 225,000 Apple Accounts to Create Free App Utopia](http://researchcenter.paloaltonetworks.com/2015/08/keyraider-ios-malware-steals-over-225000-apple-accounts-to-create-free-app-utopia/)

摘要
==

* * *

最近，`WeipTech（`威锋技术组）分析了一些用户报告的`可疑iOS应用`，发现了存储在某服务器上超过`22,5000`个有效的Apple账户和密码。

通过与`WeipTech`的合作，我们（`Paloalto`）识别了92个尚未发现过的恶意软件样本。为了找出恶意软件作者的意图，我们对样本进行了分析，并将这个恶意软件家族命名为“`KeyRaider`”。从结果来看，我们相信这是有史以来因恶意软件所造成的最大Apple账号泄露事件。

在中国，KeyRaider 将目标锁定在已越狱的iOS设备上，并通过第三方Cydia源传播。并且这个恶意软件很可能已经影响到了18个国家的用户，包括中国、法国、俄罗斯、日本、英国、美国、加拿大、德国、澳大利亚、以色列、意大利、西班牙、新加坡和韩国等。

`KeyRaider`通过`MobileSubstrate`框架来`hook`系统进程，拦截`iTunes`通信来窃取`Apple`账户用户名、密码和设备`GUID`。 它还会窃取`iPhone`和`iPad`设备上的`Apple`推送通知服务证书和私钥、`App Store`购买凭证，并禁用本地和远程解锁功能。

`KeyRaider`已经成功窃取了超过`22，5000`个有效的`Apple`账户、输千个证书、私钥和购买凭证。恶意软件将窃取到的数据上传到了存在漏洞的C2(`command and control`)服务器上，因此暴露了用户信息。

此次攻击的目的是为了让用户通过使用两款iOS越狱应用（越狱后通过`Cydia`源安装的应用）来免费下载官方`App Store`的任意应用，且不需要付款就可以在应用内进行购买服务。越狱应用是能够让用户执行在正常设备上无法进行的操作的软件包。

这两款越狱应用会劫持app购买请求，下载存放在`C2 服务器`中被窃取的账户和购买凭证，然后模拟`iTunes`协议登陆到`Apple`服务器，购买`app`或其他用户请求的项目。这两款越狱应用已经被下载超过`20,000`次，这意味着大约`20,000`名用户正在滥用其他`225,000`个被窃取的证书。

一些受害者已经报告了他们的Apple账户存在非正常app购买记录和其他一些勒索行为。

`Palo Alto Networks`和`WeipTech` 已经提供了能够检测`KeyRaider` 恶意软件和识别被窃取的证书的服务。在接下来的内容中，我们会提供恶意软件和攻击的细节。

发现KeyRaider
===========

* * *

此次攻击最早由`i_82`发现，他是一名来自扬州大学的学生、`WeipTech`成员。`WeipTech`是一个非职业技术团体，由`WeiPhone`(中国最大的Apple粉丝网站)的用户组成。之前`WeipTech`与我们合作，披露了`iOS`和`OS X`上的恶意软件`AppBuyer`、`WireLurker`。

从2015-07-01开始，`WeipTech` 开始调查一些用户Apple账户在未经授权的情况下，购买和安装了`iOS app`。再对用户安装的越狱应用进行调查后，他们发现了一款越狱应用收集用户信息，并上传到一个未知的网站。他们发现这个网站存在SQL注入，能够查看到所有的数据记录。`Figure 1`是”`top 100`”数据库的截图

![enter image description here](http://drops.javaweb.org/uploads/images/310f605ffb44710d20e4214ae9b243f236128f01.jpg)

Figure 1. WeipTech 发现在C2服务器上存在SQL注入(from WeipTech)

在数据库中，`WeipTech` 发现了标明为“`aid`”字段一共有`225,941` 条记录。大约2万条记录包含`明文用户名`、`密码`、`GUIDs`。剩余的记录是加密的。

通过逆向恶意应用，`WeipTech` 发现了一段代码，这段代码中使用静态`key`为“`mischa07`”的AES加密算法对数据进行加密。利用静态key，我们能够解密用户名和密码。经过登陆验证，他们确信记录中的信息都是有效的Apple账户。在网站管理员发现、关闭服务之前，WeipTech调查人员下载了大约一半的数据库记录。

8月25日，`WeipTech`在微博发布漏洞预警，将漏洞提交到`WooYun`（乌云漏洞报告平台），并后续转交第三方合作机构`CNCERT/CC`（国家互联网应急响应中心）处理。

当 `Palo Alto Networks`研究人员在分析`WeipTech` 报告的恶意软件时，我们发现它没有包含恶意代码来窃取密码并上传数据到`C2 服务器`。然而，通过`WeipTech` 提供的其他信息，我们发现存在其他的恶意越狱应用，存在窃取用户信息并上传到相同的服务器上。

我们将这个新的iOS恶意软件家族命名为 “`KeyRaider`” ，因为它会窃取密码、私钥和证书。

KeyRaider 来源
============

* * *

据我们了解，`KeyRaider`仅通过 `Weiphone’Cydia`仓库在越狱iOS设备上来进行传播。不像其他的`Cydia源`，如`BigBoss`、`ModMyi`。`WeiPhone`为注册用户提供私有仓库，用户可以直接上传他们的越狱应用app，并与其他人进行共享

在2015年，一个名为“`mischa07`”的用户，上传了至少15款`KeyRaider`应用到它的私人仓库([http://apt.so/index.php?r=cydiaTa/index&user_id=8676626](http://apt.so/index.php?r=cydiaTa/index&user_id=8676626))，如`Figure 2`. 此外，他的名字也被作为加解密`key`，硬编码在恶意软件中，如`Figure 3`。我们高度怀疑此人为`KeyRaider’s` 的开发者。

![enter image description here](http://drops.javaweb.org/uploads/images/e1c2ebb40260ac70c6543f3cb91bd81beb888a48.jpg)

Figure 2. mischa07’s 个人Cydia 仓库

![enter image description here](http://drops.javaweb.org/uploads/images/791650f83c42b8186b14cc2c82c6dbdf1da78b28.jpg)

Figure 3. “mischa07″ 作为加密key被硬编码在恶意软中

根据`Weiphone`的网页显示，一些由`mischa07` 上传的越狱应用已经被下载过上万次，如`Figure 4`。这些app和工具提供如游戏作弊、系统调优和app广告过滤等功能。

在`mischa07`的仓库中，有两款特别的应用

●`iappstore` (Figure 5): 能够让用户从Apple官方应用商店免费下载需要付费的应用

●`iappinbuy`：能够让用户在一些官方应用商店下载的app中免费购买付费道具或服务

`Mischa07`也在 `Weiphone`社区中对这两款越狱应用进行推广，如`Figure 6`，但一些用户并不相信这些所谓神奇的功能。然而，根据`Weiphone’s` 网站上显示，`iappinbuy` 仍人有`20,199`次下载，如`Figure 4`，而`iappstore` 有62次下载(仅对最新版进行统计)

![enter image description here](http://drops.javaweb.org/uploads/images/af23285d991cbfedcfe38a0fa41304594459aed3.jpg)

Figure 4. 一个恶意样本被下载超过30,000 次

![enter image description here](http://drops.javaweb.org/uploads/images/74902c21afe0c079b31cfa517fff7bc50cbff438.jpg)

Figure 5.  iappstore 恶意软件能够直接从App Store安装需要付费的 apps

![enter image description here](http://drops.javaweb.org/uploads/images/286b45ccdc99e9f14c854965a29279a2170ba9c1.jpg)

Figure 6. 作者推广它的iappstore 应用

另一名以“`氵刀八木`” 或 “`bamu`”.的身份的Weiphone 用户也在传播`KeyRaider`  恶意软件。因为`Bamu`的个人仓库([http://apt.so/aptso](http://apt.so/aptso))提供许许多有用的应用，这使得它在社区中非常受欢迎。在这次攻击被揭露之后，`bamu`已经删除了仓库中他所上传的所有恶意软件，并关闭了它。在`Weiphone`的帮助下，我们对`Bamu`上传的所有应用进行了检查，其中77款应用中都包含了`KeyRaider` 恶意软件。与`mischa07` 开发不同版本的恶意软件不同，`bamu`是通过对已存在app(如`iFile`,`iCleanPro`和`avfun`)进行重新打包，并在其中加入恶意代码。

当`KeyRaider` 将窃取到的用户密码上传到`C2 服务器`时， `HTTP URL`中会包含一个名为 “`flag`”或”`from`”的参数，用来追踪受感染的来源。在`mischa07`的代码中，这个参数的值通常为app应用的名字，如’`letv`’。而在`bamu`的应用中，则是“`bamu`”。从泄露的数据的统计得出，超过67%的被窃取信息来至与`bamu`.

因为`bamu` 仅仅是一个分销者(`distributor`)，后面的行为分析主要集中在来至`mischa07`的应用样本

窃取用户数据
======

* * *

`KeyRaider`收集三种用户数据，通过`HTTP`请求上传到`C2服务器`，这里发现了两个不同的`C2服务器`

```
•<top100.gotoip4.com>
•<www.wushidou.cn>

```

在分析的过程中，这些域名都被解析到了`113.10.174.167`这个IP地址。在C2服务器上的 “`top100`” 数据库里有三张表 “`aid`”, “`cer`t” 和 “`other`”。 在`server`端，`KeyRaider` 利用4个`PHP`脚本来存取数据库，`aid.php`,`cert.php`,`other.php`和`data.php`通过分析代码和`WeipTech`下载的泄露数据，我们发现`aid`表存储`225,941`条记录，包含`Apple ID`的用户名、密码、设备`GUID`。`Cert`表存储了`5,841`条受感染设备的证书和私钥，而这些信息用于`Apple`推送消息通知服务，如`Figure 7`。最后`other`表存储了超过`3,000条`设备的`GUID`和来至`app store server`的`app`购买凭证

![enter image description here](http://drops.javaweb.org/uploads/images/ed6096fc61ec0d09862af83251f329c1761219c5.jpg)

Figure 7. 泄露cert表中的一条记录

我们对泄露的`Apple ID`邮箱地址进行了整理，有超过一半的用户使用QQ邮箱，下是排名前十的账户邮箱地址域名（其中6个主要由中国用户在使用）

```
•@qq.com
•@163.com
•@icloud.com
•@gmail.com
•@126.com
•@hotmail.com
•@sina.com
•@vip.qq.com
•@me.com
•@139.com

```

然而，我们也发现一些属于其他国家或地区的邮箱地址域名，这包括

```
•tw: Taiwan
•fr: France
•ru: Russia
•jp: Japan
•uk: United Kingdom
•ca: Canada
•de: Germany
•au: Australia
•us: United States
•cz: Czech Republic
•il: Israel
•it: Italy
•nl: Netherlands
•es: Spain
•vn: Vietnam
•pl: Poland
•sg: Singapore
•kr: South Korea

```

恶意行为
====

* * *

`KeyRaider`恶意代码存在于 `Mach-O`动态库中，作为`MobileSubstrate`框架的插件。通过`MobileSubstrate API`，恶意软件能够`hook`系统进程或其他`iOS apps`的任意`API`

之前许多iOS恶意软件家族也同样滥用`MobileSubstrate`。比如由`Reddit`用户发现，`SektionEins`  分析的the Unflod (`aka SSLCreds or Unflod Baby Panda`) ，会拦截`SSL`加密通信，窃取`Apple`账户密码。去年发现的`AppBuler`也利用了同样的技术来窃取密码、在`app store`中购买`app`。`KeyRaider` 进一步利用了次技术。`KeyRaider` 主要实现了一下恶意行为

```
●窃取Apple账户(用户名、密码)和设备GUID
●窃取被用于Apple推送通知服务的证书和私钥
●阻住受感染的设备通过密码和iCloud 服务来解锁设备

```

注：`MobileSubstrate`是一个框架，允许第三方的开发者在系统的方法里打一些运行时补丁以扩展一些方法，类似于OS X上的`Application Enhancer`。所以iOS系统越狱环境下安装绝大部分插件，必须首先安装`MobileSubstrate`

窃取Apple账户数据
===========

* * *

大部分`KeyRaider` 样本`hook itunesstored`进程的`SSLRead`和`SSLWrite`函数(Figure 8).`itunesstored` 是系统守护进程，负责与`app store`进行通信(使用 iTunes 协议)。

![enter image description here](http://drops.javaweb.org/uploads/images/0df5d8266a2d2b08ac8830771a31ca54e451c91c.jpg)

Figure 8. KeyRaider hooks SSLRead and SSLWrite in itunesstored

当`App Store`客户端像用户请求输入`Apple`账户登录时，登录信息会通过`SSL`加密会话发送到`App Store server`。在`SSLwrite`的替换函数中，`KeyRaider` 会寻找此类会话，通过特定的pattern在发送的数据中搜寻`Apple`账户的用户名、密码和设备`GUID`(Figure 9). 接下来，在`SSLRead`替换函数中，这些凭证会通过AES加密算法，使用静态的key “`mischa07`”来加密，然后发送到`KeyRaider  C2 服务器`(Figure 10).

![enter image description here](http://drops.javaweb.org/uploads/images/6bf89211d8d71006ae89e018ba413479495b22c6.jpg)

Figure 9. Searching for Apple account information in SSL data

![enter image description here](http://drops.javaweb.org/uploads/images/3e76363ce1ea35a73f9a74fd2eb75340b72d4f6d.jpg)

Figure 10. Uploading stolen credentials to the C2 server

除了`hook SSLRead`和`SSLWrite`，`KeyRaider` 需要调用`MGCopyAnswer`(“`UniqueDeviceID`”) 来读取设备的`GUID`。

窃取证书和私钥
=======

* * *

在一些样本中，`KeyRaider` 也会`hook apsd`守护进程 – 负责`iOS`系统的`Apple`推送通知服务。它`hook`定义在`Security` 框架的`SecItemCopyMatching` 函数。这个API用于搜寻匹配给定查询的 `keychain items`。

当搜索查询有值为“`APSClientIdentity`”的`label` ，`KeyRaider` 会执行原来`SecItemCopyMatching`函数，然后调用`SecIdentityCopyCertificate`和`SecIdentityCopyPrivateKey`，从原本函数执行返回结果中来拷贝证书和私钥 (Figure 11). 之后，这些信息和`GUID`一起被发送到C2服务器上(Figure 12). 在`iOS keychain`中，被标记`APSClientIdentity` 的key用于推送通知。通过这些信息，攻击者可以在系统上伪造推送通知。

![enter image description here](http://drops.javaweb.org/uploads/images/a71bb29c5a7a054932f9301bccdef7f3226ac941.jpg)

Figure 11. Copy push service’s certificate and private key

![enter image description here](http://drops.javaweb.org/uploads/images/11bd142a6bc0592effe22246433dcd855c9c9054.jpg)

Figure 12. Upload certificate and key

锁定设备
====

* * *

当`KeyRaider  hook SecItemCopyMatching`，除了拦截通知证书，它也会将当前查询的label和特定的字符串 “`com.Apple.lockdown.identity.activation`”进行比较。如果匹配，`KeyRaider` 会将查询结果的值设置为0. (Figure 13)

再发布文章之前，网上还没有关于`com.apple.lockdown.identity.activation`查询的公开文档。我们相信这个查询是用于解锁设备的。通过将返回值设置为0，`KeyRaider` 会阻止用户解锁他们的设备，即使通过手机输入了正确的解锁码或通过`iCloud`服务远程解锁设备。

在我们目前发现的所有样本信息中，这段代码是独立的，没有被其它代码调用。它仅仅是被实现，然后被导出为一个函数。然而，我们已经有证据表明，利用这个函数来进行实际攻击已经发生了。

免费的APPS
=======

* * *

一些`KeyRaider` 样本实现了从`C2服务器`下载购买凭证和Apple账户的功能。但这个功能仅仅在 `iappstore`和`iappinbuy` 两个应用中被真正使用过。 根据用户的描述，`iappstore` 能够免费从`app store`中下载任意应用。让我们来看一下他们是如何实现的.

这个`app hook SSLWrite` 两次，第一次用于窃取密码。第二次`hook`会尝试判断当前的HTTP请求是否是“`POST /WebObjects/MZBuy.woa/wa/buyProduct`”。以此来判断当前会话是否是使用`iTunes`协议进行购买。(Figure 14).

![enter image description here](http://drops.javaweb.org/uploads/images/d213abba47222d95bbcccca60f5e587699a1deb7.jpg)

Figure 14. Hooking app purchase session

如果请求是购买行为，SSLWrite会被调用，`hooking`代码会尝试在发送的数据(用于获取当前app的付款信息)中匹配一些关键词，如“`salableAdamId`”, “`appExtVrsId`”, “`vid`”, “`price`”, “`guid`”, “`installedSoftwareRating`” and “`pricingParameters`” 。如果这个app是需要付费的，`fire()`函数会被调用。

`Fire`函数会调用`readAid()`函数，`readAid`函数会读取位于`/var/mobile/Documents/iappstore_aid.log`的本地文件。这个文件包含了用户账户的用户名、密码、设备`GUID`，相关的`iTunes`会话`token`、`cookie`、`电话号码`、`运营商`、`操作系统信息`、`iTunes CDN 服务器号`。然后解析数据，创建一个账户对象。

如果文件不存在，它会调用 `readAidUrl()`，`readAidUrl`会从`KeyRaider C2服务器`下载新的账户信息，然后创建一个账户对象。(Figure 15). Figure 16 展示了一个从服务器下载的账户。

![enter image description here](http://drops.javaweb.org/uploads/images/a303de2c436c173ad114f07f0be84501571de901.jpg)

Figure 15. Downloads apple account from C2 server

![enter image description here](http://drops.javaweb.org/uploads/images/9cf27ea660d011c074bacf0b4d605b199ac11dfd.jpg)

Figure 16. Stolen apple account was downloaded from C2 server

创建账户对象之后，`fire()`会生成plist格式的字符串，里面包含账户信息，接着调用 `login()`和`sendBuy()`.

`Login()`函数会创建一个连接到以下URL的HTTP连接，URL中会带上`plist`字符串和一个类似`Appstore`客户端用户代理的值

```
•p*-buy.itunes.Apple.com/WebObjects/MZFinance.woa/wa/authenticate

```

这会造成使用远程Apple账户来登陆当前的`iTunes`会话(Figure 17)

![enter image description here](http://drops.javaweb.org/uploads/images/ce7a57da57925db1e32bd7c436a285e701a9edc1.jpg)

Figure 17. Emulating login protocol

发起`Login`请求之后，`login()`会解析返回的结果，获取`cookie`、`token`和其他信息，然后将这些信息和账户密码保存到本地`iappstore_aid.log`文件中，供后续购买时使用。如果因为密码错误导致登陆失败，它会再一次调用`readAidUrl()` ，从`C2 server`中获取一个不同的Apple账户。

`sendBuy()`函数的工作与`login()`函数类似，但请求了另一个`URL`，用于`app`购买验证

```
•p*-buy.itunes.apple.com/WebObjects/MZBuy.woa/wa/buyProduct

```

通过这个过程，`iappstore` 应用可以使用窃取到的账户成功购买任意app 除了这些操作之外，在两个独立的函数`verifySF()`和`verifySF2()` 中，`KeyRaider` 也会尝试获取Apple账户密码找回问题和答案。这个函数在我们的分析样本中还未完成。

`iappinpay`的功能和`iappstore`类似。唯一的不同是购买接口改变了。(Figure 18)。在C2服务器数据库中也存储了一些之前在app内购买（ In-App-Purchase）的凭证，作者似乎计划实现重用这些凭证的功能，如将这些凭证发送到Apple server，以证明他们之前已经购买过此服务。

电话勒索
====

* * *

除了窃取Apple账户来购买app，`KeyRaider` 拥有内置的锁定功能来进行勒索。

之前的一些iPhone勒索软件工具基于通过`iCloud服务`来远程控制iOS设备。这类攻击可以通过重置账号密码来解决。而对于`KeyRaider` ，它在本地禁用了所有解锁操作，及时是输入的正确的解锁码或密码。此外，它也能使用窃取的证书和私钥来发送通知消息来索要赎金，而推送通知消息不需要经过Apple推送服务器。因此，之前使用的解决方法不再有效。

下面是一名受害者报告的被勒索截图

![enter image description here](http://drops.javaweb.org/uploads/images/a19e12d59b6051a0e4569d5bc5cf3f217ee2b47b.jpg)

Figure 19. Ransom message on locked iPhone

其他潜在的风险
=======

* * *

下面是一些攻击者利用你泄露的用户名、密码等信息能够做的事情

**应用推广**：在受害者手机中安装指定的app，来提升`App Store rankings`

**Cash Back**：使用的账户来购买付费应用

**垃圾邮件**：使用`iMessage`来发送垃圾信息

**勒索**：利用账户密码，窃取隐私信息来进行勒索 等等

保护和预防
=====

* * *

需要注意，`KeyRaider` 仅影响越狱的iOS设备，未越狱设备不受影响。`WeipTech`上线了查询服务 <http://www.weiptech.org/ >，你可以输入自己的Apple账户邮箱，了解它是否被泄露。`Palo Alto Networks`在8月26日将窃取的账户信息反馈给了`Apple`。还需要注意的是，因为攻击者发现并修复了其接收数据服务器的漏洞，`WeipTech` 只能还原约一半的被窃取数据。因此，从不受信任的`Cydia 源`安装过这类越狱应用的用户可能都会受影响。

用户可以通过下列方法来判断自己的iOS设备是否受影响

```
1.通过Cydia安装openssh
2.通过SSH连接到device
3.到 /Library/MobileSubstrate/DynamicLibraries/ 目录，对目录下的所有文件grep以下字符串

•wushidou
•gotoip4
•bamu
•getHanzi

```

如果任何`dylib` 文件包含任意一个字符串，删除这些文件和同名的`plist`文件，然后重新启动

除此之外，我们也建议用户在移除恶意软件之后，修改Apple账户的密码，并开启双因素认证功能。[https://support.apple.com/en-us/HT204152](https://support.apple.com/en-us/HT204152)最后，如果你想避免遭遇`KeyRaider`以及类似恶意软件，请尽量避免越狱。`Cydia 源`不会对上传应用进行严格的安全检查，通过它安装应用存在风险。

样本信息
====

* * *

```
9ae5549fdd90142985c3ae7a7e983d4fcb2b797f CertPlugin.dylib
bb56acf8b48900f62eb4e4380dcf7f5acfbdf80d MPPlugin.dylib
5c7c83ab04858890d74d96cd1f353e24dec3ba66 iappinbuy.dylib
717373f57ff4398316cce593af11bd45c55c9b91 iappstore.dylib
8886d72b087017b0cdca2f18b0005b6cb302e83d 9catbbs.GamePlugin_6.1-9.deb
4a154eabd5a5bd6ad0203eea6ed68b31e25811d7 9catbbs.MPPlugin_1.3.deb
e0576cd9831f1c6495408471fcacb1b54597ac24 9catbbs.iappinbuy_1.0.deb
af5d7ffe0d1561f77e979c189f22e11a33c7a407 9catbbs.iappstore_4.0.deb
a05b9af5f4c40129575cce321cd4b0435f89fba8 9catbbs.ibackground_3.2.deb
1cba9fe852b05c4843922c123c06117191958e1d repo.sunbelife.batterylife_1.4.1.deb

```

### 致谢

特别感谢来自`WeipTech`的`i_82`向我们共享数据、报告以及其它有用的信息。 感谢来自`WeipTech`的`CDSQ`向我们提供样本，感谢来自`WooYun`的`Xsser`、`FengGou`的信息共享。 感谢`Palo Alto Networks`的`Sereyvathana Ty`、`Zhaoyan Xu`、`Rongbo Shao`几位对恶意软件进行的分析，感谢`Palo Alto Networks`的`Ryan Olson`对本报告的审校。