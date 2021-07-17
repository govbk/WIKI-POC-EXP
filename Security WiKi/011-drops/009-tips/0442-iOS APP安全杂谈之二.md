# iOS APP安全杂谈之二

0x00 序
======

* * *

自从上一篇文章发了以后，参加乌云众测时发现小伙伴们真的提交了一些我所说的IOS低风险问题，真的是连一百块都不留给我。但是我依然感到幸运，因为今天可以为IOS APP安全杂谈写个续集。

上一节我们主要说了三点：IOS APP本地文件安全；HTTP/HTTPS下通信数据安全性的思考；非安全从业者是中间人攻击的重灾区。这次我们将简单的介绍一些方法和工具，来作为IOS APP安全测试的入门教程。由于本人能力有限，文章难免会有些错误，还望小伙伴们见谅。

0x01 卸下厚厚的伪装
============

* * *

在我刚刚开始接触IOS逆向分析的时候想要一口吃个胖子，我从AppStore上下载APP进行安装后，找到其目录下的可执行文件，然后直接扔到了IDA中。结果可想而知，我看到了一坨不知所云的函数，那时我还一度怀疑过自己是不是真的适合做这一行。好在后来去除了浮躁的心态，知道我这么一个瘦子是无法变成胖子的，从前人的劳动成果中学习到从AppStore上下载的软件都是经过加密的，可执行文件被加上了一层厚厚的壳，这节我们只做一件事情，就是将APP厚厚的伪装去掉。之所以说是伪装，是因为加了密的APP想要解密并不是什么难事，不像Android下的APP加壳种类那么多。目标APP苏宁易付宝钱包（这是一个良心厂商，奖励了白帽子好多购物卡，这里的演示仅供学习毫无恶意）。

![enter image description here](http://drops.javaweb.org/uploads/images/69459f90c46aaaecc823a5b32aa47c13f382378b.jpg)

下面我们来解密AppStore上下载的APP，解密方法也有很多：使用clutch解密、使用dumpdecrypted解密、使用gdb调试工具解密等。在网上还看到一个工具叫AppCrackr，据说这个软件简单暴力，但是由于其助长了盗版的气焰，其核心功能被迫关闭。这里我们就简单的演示一下使用`dumpdecrypted`进行解密。

（1）获取并编译[dumpdecrypted dumpdecrypted](https://github.com/stefanesser/dumpdecrypted/archive/master.zip)下载后将其解压，首先查看自己设备的系统版本，因为dumpdecrypted需要使用与IOS版本相同的SDK版本进行编译，在终端输入：`SDK=‘xcrun --sdk iphoneos --show-sdk-path’`来指定SDK版本，如果你的Mac上没有和手机匹配的SDK版本，那你就像我一样，下载一个旧版本的Xcode，然后指定该旧版本Xcode中的SDK即可。

![enter image description here](http://drops.javaweb.org/uploads/images/279245d8fc076cd4950a7463f26ec4caf8bc28b5.jpg)

这里附上《IOS应用逆向工程》作者沙梓社编译好的[文件地址](https://github.com/iosre/Ready2Rock)。

如果你的SDK版本是7.0，那么可以在终端中直接进入`dumpdecrypted-master`（就是刚刚你下载的那个文件）目录中使用make进行编译，如果不是7.0，需要修改dumpdecrypted-master目录中Makefile中的`GCC\_UNIVERSAL=$(GCC\_BASE) -arch armv7 -arch armv7s -arch arm64`改为 `GCC\_UNIVERSAL=$(GCC\_BASE) -arch armv7 -arch armv7s`再将dumpdecrypted.c第76行的`if (lc->cmd ==LC\_ENCRYPTION\_INFO || lc->cmd == LC\_ENCRYPTION\_INFO\_64）`改成 `if(lc->cmd == LC\_ENCRYPTION_INFO)`，保存。然后再进行编译，目录下会生成`dumpdecrypted.dylib`文件。

![enter image description here](http://drops.javaweb.org/uploads/images/b3514125f80da2aef8c01438233e10e3506aaa7c.jpg)

（2）定位可执行文件 使用PP助手将`dumpdecrypted.dylib`文件直接拷贝到目标APP中的Documents文件夹中。

![enter image description here](http://drops.javaweb.org/uploads/images/bbca3d390ee63e84e9e4d80c26daf4ec2cc8b849.jpg)

在Mac终端下使用SSH连接到手机（手机的SSH可以通过PP助手的工具打开），然后手机端关闭其他所用应用打开目标APP，在终端运行ps –e（需要安装adv-cmds），此时可以轻松找到目标的可执行文件。

![enter image description here](http://drops.javaweb.org/uploads/images/ebd93a4a84ea2387be745ef65f82faa11f98784b.jpg)

（3）解密可执行文件 得到了所有的信息后我们就可以进行APP可执行文件的解密了，用大家常用的说法就是砸壳，我们在终端执行如下命令：`DYLD\_INSERT\_LIBRARIES=/var/mobile/Applications/3B447828-D3B9-4575-8DE9-9DB335091F43/Documents/dumpdecrypted.dylib /var/mobile/Applications/3B447828-D3B9-4575-8DE9-9DB335091F43/SNYifubao.app/SNYifubao`

![enter image description here](http://drops.javaweb.org/uploads/images/3f6c37cdf2eb0ceea0d4102fcc389ee6626a8929.jpg)

如果不报错的话则代表解密成功，解密的文件在你进行解密操作时的目录下（由于我当时是在/var/root目录下操作的，所以解密后的文件就在/var/root目录下）。

（4）当然如果你不想那么费劲，可以直接到PP助手或者91助手下载APP，安装后找到可执行文件，这个可执行文件就是已经解密了的，不过美中不足的是无法保证你下载的APP是最新的，也无法保证是否被恶意篡改了逻辑结构。

0x02 知己更要知彼
===========

* * *

《`Hacking and Securing ios Applications`》中的第七章介绍说Objective-C是一种反射式语言，它可以在运行时查看和修改自己的行为。反射机制运行程序将指令看成数据，也允许在运行的时候对自己进行修改。Objective-C运行时环境不仅可以让一个程序创建和调用临时的方法，还可以实时创建类和方法…说了这么多，其实就是想告诉我们IOS的运行时环境是可以被操作的。但是问题来了，我们操作运行时应该有个前提，那就是你要对这个APP足够了解。

（1）使用`class-dump`在ios中，可执行文件、动态链接库文件等都是使用了一种名为Mach-O文件格式，它由三部分组成：头部，一系列的加载指令，以及数据段。而[class-dump](http://stevenygard.com/projects/class-dump/)就是利用`Objective-C`语言的runtime特性，将存储在Mach-O文件中的头文件信息提取出来，并生成对应的.h文件。透过提取出的文件，就可以大致知道闭源App程序架构。安装后终端下输入`class-dump -S -s -H Desktop/SNYifubao -o Desktop/SNY/`，其中`Desktop/SNYifubao`为之前解密的可执行文件（`SNYifubao. Decrypted`去掉后缀），`Desktop/SNY/`为我将导出.h文件的位置。

![enter image description here](http://drops.javaweb.org/uploads/images/a2db103e9b8f69aafdfbaaad9f3a63ee642f0059.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/59b4abcca3a451353a027deb97bf7740cc574aeb.jpg)

（2）使用`Hopper Disassembler`前面通过dump头文件已经基本可以判断哪些类里有哪些方法，哪些方法是如何实现的，而`Hopper Disassembler`则更为强大，可以运行在Mac、Linux和Windows下的调试、反汇编和反编译的交互式工具。将上次解密的文件使用`Hopper Disassembler`打开，我们可以查看某处的伪代码，可以查看某处的逻辑结构，还可以直接修改APP的设计逻辑。

![enter image description here](http://drops.javaweb.org/uploads/images/7ddc94009ae16b3ef96a4d2055288e6266e864e7.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/d34852a8356eeea1b5d7011659b54f020eb0cc4d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/6335e67ee248334c36823ff3dc24e56a11dace1d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c67f0394082af89977d688a3f9d1a686781c6132.jpg)

互联网上还有更多该软件的使用方法，我就不一一介绍了，当然你想彻底去分析一款IOS软件，还需要更多地去学习和了解ARM汇编相关的IOS逆向理论。而我在0x04小节中的（2）中就可以使用该方法为APP打补丁来绕过SSL认证。

0x03 洛阳铲和屠龙刀
============

* * *

其实上一节中说的那些工具和方法只是冰山一角，还有很多工具是在我们身陷囹囫时可以助我们一臂之力的。例如使用Reveal来分析APP的UI布局，使用Theos工具包开发越狱插件，使用Cycript操作运行时等。在《ios应用逆向工程》中作者更是将LLDB比喻成屠龙宝刀，IDA比喻成倚天剑（虽然我认为`Hopper Disassembler`更牛一些）。但是我想说的是，还有很多并不起眼的东西却在无形中帮了我们大忙，记得微信刚出飞机大战游戏的时候，有一款叫做“八门神器”软件帮了很多人上了朋友圈的游戏榜首。还有一款应用叫Flex，他可以让我们绕过APP的某些限制，例如去掉视频软件的广告，去除视频网站的会员限制等等。我更习惯把这些软件叫做洛阳铲（可能是前段时间刚看完盗墓笔记的缘故），虽然是为作弊、破解而生，但是其却可以证明某APP存在设计缺陷。此处我附上一张工具图表（忘了是在哪里看到的了，感谢作者）。

![enter image description here](http://drops.javaweb.org/uploads/images/636b598ddeeda7fc9af783e71bba916757ca7150.jpg)

0x04 明修栈道暗度陈仓
=============

* * *

最近在乌云主站上有几个小伙伴留言问我如何抓手机APP的通信数据包，这个问题我想使用搜索引擎就能找到非常好的答案。但是有时也会发现，有些数据我们是无法捕获的，所谓明修栈道暗度陈仓，你看到的未必是对你有用的，这里我分享一下出现这些问题的原因和解决方法。

（1）截获几种常见的通信数据 HTTP：设置PC端，设置手机端，即可进行抓包和改包； HTTPS：设置PC端，设置手机端，手机端信任证书（分多种情况），即可进行抓包和改包； Socket：将IOS设备线连到MAC上，使用rvictl命令让IOS设备上的网络流量经过MAC，启动Wireshark监听rvi接口上的数据。

（2）拦截HTTPS数据 HTTP的略过，我们说一下HTTPS吧，在测试了多家银行和P2P金融公司的APP之后发现各个厂商对安全的重视程度不一，而对安全问题的响应速度也不一。在今年4月末时网爆流行IOS网络通信库`AFNetworking SSL`漏洞，影响银联、中国银行、交通银行在内的2.5万个IOS应用，而在后面的两个月内笔者发现银行已经修复此类问题。其实如果APP在开发时就严格的按照SSL认证过程进行设计的话，APP的通信数据还是非常安全的。（[AFNetworking SSL漏洞检测地址](http://www.freebuf.com/news/65744.html)）。

**情况一：**信任任何证书。这种情况IOS的APP可以信任任何证书，所以打开safari浏览器在地址栏上手动输入burp或者fiddler所在PC端的IP地址加上自己设置的端口号，burp点击CA Certificate安装证书，fiddler点击FiddlerRoot certificate安装证书，此时就可以抓取到该APP的HTTPS数据。出现这种情况的原因很有可能是使用的开源通信库存在缺陷，还有就是开发人员在开发过程中未连接生产环境的服务器，为解决认证过程中证书报错的问题只能暂时修改代码使其APP信任任意证书，而在上线前未对此代码进行处理。

![enter image description here](http://drops.javaweb.org/uploads/images/28b1cf3c0a1dfeb802a767c0a489557cd4161c11.jpg)

**情况二：**信任证书管理机构（CA）颁发的证书。这种情况IOS的APP可以信任任何CA颁发的证书，据说这类的证书只需50美元就能买到。此类问题出在`AFNetworking 2.5.2`及之前的版本，也就是说如果某IOS APP使用了此版本的开源通信库，在不安全Wifi网络中的黑客、VPN网络中的职工或者国家支持的黑客，只要使用CA颁发的证书就可以对该APP的HTTPS加密数据进行监听或者篡改。

**情况三：**信任合法的证书。这种情况IOS的APP只信任对自己而言合法的证书，首先我们看一下[SSL认证的原理](http://edison0663.iteye.com/blog/996526)的前三步：① 客户端向服务器传送客户端SSL协议的版本号，加密算法的种类，产生的随机数，以及其他服务器和客户端之间通讯所需要的各种信息。② 服务器向客户端传送SSL协议的版本号，加密算法的种类，随机数以及其他相关信息，同时服务器还将向客户端传送自己的证书。③ 客户利用服务端传过来的信息验证服务器的合法性，服务器的合法性包括：证书是否过期，发行服务器证书的CA是否可靠，发行者证书的公钥能否正确解开服务器证书的“发行者的数字签名”，服务器证书上的域名是否和服务器的实际域名相匹配。如果合法性验证没有通过，通讯将断开；如果合法性验证通过，将继续进行下一步。那么如何让IOS的APP信任非法的证书呢，看上文说到的第③步，我们只需要做到在合法性验证的时候能够欺骗APP，通讯就不会中断。

这里我附上一篇绝对有干货的文章，里边详细描述了如何才能让IOS信任任何证书的方法：[Bypassing OpenSSL Certificate Pinning in iOS Apps](https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2015/january/bypassing-openssl-certificate-pinning-in-ios-apps/)。文章使用了两种方法，第一种是使用`Cycript`或者`Cydia Substrate来hook`证书验证函数，第二种是通过对目标APP的逆向分析，制作程序的二进制补丁来绕过证书的“Pinning”机制。

**情况四：**这种情况是采用了服务器和客户端双向认证的措施，即客户端在确认服务器是否合法之后，服务器也要确认客户端是否是合法的（服务器要求客户发送客户自己的证书。收到后，服务器验证客户的证书，如果没有通过验证，拒绝连接；如果通过验证，服务器获得用户的公钥）。正是这个原因，我们在测试APP时会发现尽管我们信任了burp或者fiddler的证书，可是在进行登录操作时APP依然会显示网络连接错误，此时服务端已经知道客户端可能是非法的，然后拒绝连接。如果你是开发人员，想分析HTTPS流量也很简单：使用burp导入客户端证书，此时burp就可以与服务器正常的建立连接，你也可以正常的截取到数据包了。

![enter image description here](http://drops.javaweb.org/uploads/images/c2c67f69a245a94ace659ce1a885e82c1fb44ea1.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/5e871a6f25fbb77487ab31144a25417f8c6b9c7d.jpg)

（4）获取Sockets接口数据 记得有一次遇到一个奇怪的现象，明明已经截获了某金融APP的HTTP数据包和HTTPS数据包，但是在我输入登录密码和交易密码时发现burp上并没有显示有数据包通过，当时真是too young too simple，后来才知道wifi＋burp模式是无法获取到socket通讯的，有时也无法获取EDGE／3G的数据包。后来借鉴了前人的劳动成果，使用`RVI（Remote Virtual Interface）＋Wireshark`的模式进行数据包分析。

Mac下获取并安装[Wireshark](https://www.wireshark.org/),但是此时Wireshark是无法启动的，还需要安装另一款软件[X11（XQuartz）](http://xquartz.macosforge.org/landing/)，安装完成后我们将IOS设备通过usb连接到Mac上，然后打开终端输入连接命令：`rvictl －s ［IOS UDID］`，断开连接的命令为：`rvictl －x ［IOS UDID］`，其中的UDID（设备标识）可以通过iTunes或PP助手等工具查看。

![enter image description here](http://drops.javaweb.org/uploads/images/d3dfbc1d228353dabe63fbcfccddc316ad38b379.jpg)

连接成功后IOS的网络流量都会经过其所连接的Mac，并且IOS数据还是走自己的网络。而Mac会出现一个对应的虚拟网络接口，名字是rvi0（如果有多个设备则累加，rvi1，rvi2…），启动Wireshark，监听rvi接口就可以监听其数据了。

0x05 论持久战
=========

这篇文章貌似我说的很多很杂，因为工具和方法有很多，渐渐的连我自己都觉得文章没有任何条理可言，还望读者见谅。此小节之所以叫做论持久战是因为学习安全非一朝一夕的事情，更何况由于IOS系统自身的原因导致其资料有些匮乏，所以很多是靠经验的积累才能掌握的，逆向更是需要我们有耐心去钻研和学习。在此感谢乌云又给了我一次和小伙伴们一起学习的机会。