# Botconf 2015总结

> 链接：  
> [https://blog.rootshell.be/2015/12/02/botconf-2015-wrap-up-day-1/](https://blog.rootshell.be/2015/12/02/botconf-2015-wrap-up-day-1/)  
> [https://blog.rootshell.be/2015/12/03/botconf-2015-wrap-up-day-2/](https://blog.rootshell.be/2015/12/03/botconf-2015-wrap-up-day-2/)  
> [https://blog.rootshell.be/2015/12/04/botconf-2015-wrap-up-day-3/](https://blog.rootshell.be/2015/12/04/botconf-2015-wrap-up-day-3/)

0x00 第一天
========

* * *

下面是一些与会议相关的 数字：

*   总预算: 80.000€
*   260 名参与者
*   3 篇keynotes
*   20 次讨论
*   6 次短讨论
*   大量的快速讨论
*   一次社交活动

第一篇Keynote演讲来自欧洲刑警[Margarita Louca](https://nl.linkedin.com/in/margarita-louca-95481240)：“_Successful botnets takedowns: The good-cooperation part_”（成功拿下僵尸网络：良好合作部分）。更准确的说，是EC3（“欧洲网络犯罪中心”）。这一演讲属于“限制级”，在这里只能公开部分信息。欧洲刑警组织属于强制性执法机构（负责处理僵尸网络的基础设施并抓捕其所有者）。在重新回到EC3后，[Margarita Louca](https://nl.linkedin.com/in/margarita-louca-95481240)又重新审查了一些成功的取缔行动。但是，就像她说的，这里仍然存在大量的问题（技术问题、行政问题等）：由于缺少资源，法院指令并不能适用于僵尸网络的判决。Margarita举例说明了为什么[Shylock](https://nakedsecurity.sophos.com/2014/07/18/notorious-shylock-banking-malware-taken-out-by-law-enforcement/)取缔活动为什么并不成功。有一部分基础设施很难去关停。Margarita给出的例子是.su域名。当局会面临下面的这些挑战：

*   参与者的信任
*   报告
*   通知大众（媒体）
*   分享 (!)
*   缩小收益率

有时候，当地法律也会成为问题。例如，在荷兰，IP地址就属于个人数据。不错的开头！

接着，是Maarten van Dantzig 和[Jonathan Klijnsma](https://twitter.com/ydklijnsma)。Ponmocup演讲的“_Ponmocup,the full story: A giant hiding in the shadows_”（_Ponmocup，阴影中的巨人_），虽然_Ponmocup_并不是最新出现的（在之前的Botconf中就涉及过），但是仍然在活动中（从2006年开始）。

![p1](http://drops.javaweb.org/uploads/images/3b0e691c2f62ed9648f1b7b0cbfcc6bbc5489649.jpg)

Ponmocup中有多个组织的参与，很可能是俄国人主导的。Ponmocup感染了大量的受害者，其目的也不是单一的。Ponmocup还利用了没有记录的Windows API调用。首先，Maarten & Jonathan介绍了受害者是如何被感染的。这个木马实现了一些技巧来欺骗安全研究人员，比如特定的访问来源、cookie、IP黑名单等。并且，他们还利用了一些技术来防止木马被直接下载。另外，如果尝试的太频繁，你就会被加入到黑名单。除了反分析功能，木马还会检查进程、用户名、驱动、显示器分辨率、近期打开的文档、浏览器历史记录、安装的程序等。干得好！在安装阶段，木马会重置系统的恢复点，并禁用系统的恢复功能。木马还会打开防火墙，并禁用UAC功能。每当感染一个主机，木马就会根据卷序列号创建一个唯一的文件。每个副本对于目标而言都是独一无二的。Ponmocup最出色的一点：实际上这个木马是一个包括了多个已知模块（25个）的框架：AV killers, SOCKS proxy, SIP scanners, FTP stealers, 系统信息收集器, Facebook cookie stealer, Bitcoin钱包盗取器等 。这个木马还能对抗污水池技术：域名都不是在同一时间全部部署的，而是根据有效载荷的版本进行分组。政府的取缔行动只能影响部分僵尸网络。演讲人检查了木马的多个功能，这些功能之间的配合很让人吃惊。总的来说， Ponmocup：

*   活动了7年
*   感染了1500万+名受害者
*   有50万仍在活动中

Fox-IT公布了更多详细信息：[报告](http://f0x.nl/ponmocup/)与IOC

为了对抗污水池技术，域名都不是在同一时间全部部署的，而是根据有效载荷的版本进行分组。政府的取缔行动只能影响部分僵尸网络。干的不错！

接下来是一次短讨论，演讲人是Alexander Chailykto 和 Aliaksandr Trafimchuk。这次讨论的标题是“_DGA clustering and analysis: mastering modern, evolving threats_”（DGA分类与分析：掌握现代威胁的进化旅程）。DGA（域名生成算法）是现代木马中很重要的一部分。率先使用这项技术的是Conficker。

![p2](http://drops.javaweb.org/uploads/images/b3f07023562f2b2d3c3ffeb173060f417ec03146.jpg)

DGA造成的问题：

*   无法拦截
*   木马实际只会使用少量的域名
*   污水池技术无法奏效

他们开发了一个叫做 DGALAB的工具。这个工具支持下面的这些DGA类型：

*   静态DGA – 每次生成相同的域名（只是重复实现同一种算法）
*   基于日期的DGA– 将当期日期用作输入
*   基于种子的DGA– 将种子作为输入（硬编码，不容易提取）
*   后两种的综合型

DGALAB有哪些特征：

*   模块化系统（支持新型的DGA）
*   生成外置的域名列表
*   将愚蠢的DGA自动整合成1组
*   有效的白名单系统
*   低资源占用的模拟

这个工具基于Cuckoo沙盒和Cuckoomon，可以在VMware中作为管理程序运行，可以固定在虚拟环境和特定的内核中。最后，他们演示了这个工具在整合到现有解决方案（如防火墙、IDS）中是多么的实用。

午饭后，Zoltan Balazs进行了一次短讨论：“_Sandbox detection for the masses: leak, abuse, test_”（沙盒检测：泄露、滥用和测试）。Zoltan首先问了观众几个问题。事实上，每个人都会面临这样的问题。木马会检测我们的沙盒，所以我们需要更强大的沙盒系统。

![p3](http://drops.javaweb.org/uploads/images/fd54a7e95030941dca14582fd6e21f9302474577.jpg)

木马开发者可以很容易地检测出沙盒的存在。Zoltan利用VirtualBox快速地进行了演示。常见的问题有：

*   屏幕分辨率：
*   已安装的软件 (python, Tracer, PHP, Debugging tools, Strawberry Perl,
*   运行常用进程 (python.exe)
*   CPU类型 … 谁运行了 Intel Pentium Pro ? 以及核心数量
*   计算机系统 (Bochs, VirtualBox, KVM, Optiklex 990, P5QSE等
*   鼠标移动
*   内存大小，1GB内存配置的桌面电脑？
*   机器名称

另外，用户的电脑桌面经常会是一团糟，可以监控CPU使用，网络连接。教训是：有很多绕过动态分析的方法。给沙盒开发者的建议：再努力些。这是一次短讨论，但是值的关注，Zoltan提到了很多有意思的信息。我喜欢！

然后，来自CERT.p的[Lukasz Siewierski](https://twitter.com/maldr0id)发布了一篇叫做 “_Polish threat landscape_”（“波兰威胁规模”）的演讲。Lukasz 讲了一家波兰公司遭到社会工程袭击的故事。其他国家的一些公司也在面临相同的问题。

![p4](http://drops.javaweb.org/uploads/images/81189fcc8c9488cffd5b65ba752b9faf8f1f937f.jpg)

其攻击方案非常经典：发一封邮件，有人回信，再用假冒的NDA发第二封。一旦入侵了这家企业，攻击者就会窃取客户名单，并发给他们虚假的发票。Lukasz在分析完技术后，又说明了一个更严重的情况。Lukasz解释了这家公司是怎么反应的，他们起诉了一名记者，假装自己没有遭到攻击，客户信息也没有泄露。有趣的故事！

Gavin O'Gorman讨论了“_Butterfly attackers_”（蝴蝶攻击者）。Symantec命名这个间谍小组叫做Butterfly，3年以来，他们入侵了一些大公司。同样没有记录，没有信息披露。

接着，来自思科的[Veronica Valeros](https://twitter.com/verovaleros)演讲了“_Make it count: An analysis of a brute-force botnet_”（分析爆破僵尸网络）。她研究说：我们通常首先会分析木马一开始的几分钟。那么一周、一个月会怎么样呢？

![p5](http://drops.javaweb.org/uploads/images/d6b39be993b9e3a91f5a304938ae7126f0afd732.jpg)

她发现了一个看似普通的样本，但是在几天后，这个样本开始有其他的行为…下载了一个新的有效载荷并开始执行爆破攻击。这个样本的攻击目标是WordPress网站。我们并不意外这样的网站数量庞大。下面是一些关于这次攻击数字：

*   1 个bot
*   访问了7000网站
*   1次成功入侵
*   用了大约3个半小时
*   每天入侵6个网站

和前面的讨论一样，这次讨论也很有趣。

[Frank Denis](https://twitter.com/jetdisct1)展示了他的研究： “_The missing piece in threat intelligence_”(网络情报中缺失的一环)，Frank正在[OVH](http://www.ovh.net/)任职，能接触到一些恶意活动的源头。

![p6](http://drops.javaweb.org/uploads/images/c67e73c54838d1b1a829bec8253c6e475bfdc29b.jpg)

ISP必须应对各种问题。比如，托管服务滥用、入侵等，这类问题很难管理。IP地址就是一个很好的例子。IP地址可以分配给不同的用户，而新的用户会继承这个IP的名誉。 这样就可能对他的业务造成影响。另外，有些厂商的行为很不好，仅仅是重复使用在线服务提供的数据。比如，有些厂商会拦截IP地址，仅仅是因为这些IP的: 评分>0！ Frank解释了ISP是如何应对并追踪这些问题。然后，他提出了一种结构化语言来描述ISP所采取的行动。比如，IP地址可以被标记位：

*   Reserved
*   Unassigned
*   Suspended
*   Clean
*   Notified
*   Deleted
*   Resumed
*   …

当然，接下来的挑战是如何让其他同仁也使用相同的语言。为此，Frank开发了一个叫做[ERIS](https://github.com/dip-proto/eris)的工具能帮助使用[DIP](http://dip-porto.github.io/)协议。这样做有很多好处：

*   执法部门能够立刻获取到有价值的信息
*   研究人员和SIEM管理员能提供快速反馈
*   节约服务提供商和事件处理人员的时间
*   扩大用户的视野

这种想法不错。现在的目标是让其他人知道这个工具和协议的存在。

Marc Dioudet 谈论了 “_Honey!? Where is my POS?_”（亲，我的POS在那里？）他的研究目标是想要更好的理解POS木马使用的技术和过程。

![p7](http://drops.javaweb.org/uploads/images/42449c5ffc29cbf7eec913ee166336bcabf580b9.jpg)

在简单地查看了一个标准POS系统后，Marc解释了他部署用来创建POS蜜罐的解决方案。在仅仅三小时后，他就抓到了一个Morto木马感染。他还说明了为什么这个蜜罐很难吸引攻击者。一开始，他把服务器放在了广泛使用chip & pin的德国。在他把服务器转移到美国后，他捉到了更多木马。

最后，[John Bambenek](https://twitter.com/bambenek)再次讨论了僵尸网络的取缔，题目叫做 “_Takedowns; case studies ad what we all could be doing better_”（取缔，案例研究，我们怎样才能做的更好）。与Margarita一样，他解释了为什么组织一次僵尸网络取缔会这么困难。

![p8](http://drops.javaweb.org/uploads/images/8dc5b095d643c2b9a36efe35778c8b9988371a4d.jpg)

John提到我们如今面临的问题有：我们在竞赛中已经落后了，我们注定要失败。不过好消息是，我们会有很多活干。什么是取缔？需要根据：

*   特殊的安全活动
*   控制域名
*   让托管服务公司收拾烂摊子
*   营销活动？

事实上：为什么我们需要干掉僵尸网络？John解释道，这是因为大多数人无法购买厂商部署的昂贵的产品。一次取缔活动就是一次瓦解活动，因为需要实现新的防火墙规则、黑名单、DGA列表等。这些措施都是有效的吗？不总是，而且更糟的是，这些措施有副作用。通常，攻击者在几个小时内就可以恢复行动。并且这样经常会造成附带伤害。John以Conficker感染医用设备为例，这些设备管理的心脏起搏器会怎样呢？John调查了一些比较不错的僵尸网络取缔案例：

*   No-IP ( Microsoft)
*   Conficker
*   Kelihos (这次活动经过了4次取缔，仍在活动中)

0x01 第二天
========

* * *

第一篇来自Daniel Plohmann关于DGA的讨论：“DGArchive – A deep dive into domain generating malware”（深入研究域名生成木马）。像往常一样，开篇就是对DGA的审查，基本上没什么新内容（昨天已经都说过了）。去年，Daniel只是稍微介绍了他的项目，今天他展示了自己的研究成果。

![p9](http://drops.javaweb.org/uploads/images/6dff6a092e57b1789313565208d64506298f85f2.jpg)

DGA的小历史：

*   第一个DGA出现在20006年（Sality动态生成了一个3级域名）
*   在2007年7月，发现了Torpid和Kraken
*   在2008-2009年，Szribi和Conficker

DGA是现代木马的一个重要特征。为什么DGA会得到广泛地使用？

*   增加分析难度
*   绕过黑名单拦截
*   后备方案
*   不对称性（攻击者只会用其中一个域名，而防御者需要拦截所有的域名）
*   可行性（域名很便宜）

更重要的是，DGA让安全研究人员很头疼。这种研究原理是逆向DGA，生成所有的域名，并创建一个数据库来执行查询和统计。其目标是查询一个域名，然后数据库返回相关的木马。直到今天，Daniel发现了：

*   43个系列
*   280 个种子
*   2000万+个域名

大量的DGA使用了长域名（相反的，商业域名都是尽可能地短）。很重要的一点是，种子会影响域名的生成。Daniel采取的过程是：

1.  过滤
2.  评分
3.  匹配（自动检测新的种子）

接着，Daniel用大量的材料解释了每个木马家族是如何生成域名的。然后，接下来的问题是：域名注册？根据Whois数据库，他发现了这些域名、污水池、解决方案、预注册和域名停靠的特征。关于DGA的问题是：它们可靠吗？如果算法之间发生冲突该怎么办，会不会对有效域名的生成造成风险？在这种情况下，会对有效域名的所有者造成灾难性的影响。是的，这种算法冲突是可能的。但是还不足以帮助我们根据生成的域名来对木马进行分类。

下一篇演讲的重点是Andromeda僵尸网络。Jose Miguel Esparza讨论了“_Travelling to the far side of Andromeda_”（前往 Andromeda的另一端） 。这次讨论的不是要逆向僵尸网络（因为已经有大量可用的信息），而是讨论僵尸网络背后的人。

![p10](http://drops.javaweb.org/uploads/images/975d423733186a34a4180f69434cbb90e850667b.jpg)

关于 Andromeda的几点信息：

*   开始于2011
*   模块化并且功能全面
*   定期联系 C&C regularly 获取“任务”（新木马、插件等）
*   通过传统方式传播
*   最近版本是 2.10

Andromeda更新了反分析等新功能，以及一个黑名单程序（甚至python.exe和perl.exe）。在最新发布的版本中，参数是以JSON的形式发送的。另外注意，重建二进制时的通讯是通过XMPP而不是通过IRC实现的（标准通讯仍然是通过HTTP实现的）。木马开发者还经常会留下一些信息，比如包含有“_fuckyoufeds_”的虚假信息。一个很有趣的特点：Andromeda不会感染位于某些地区的计算机，比如俄罗斯（根据键盘布局确定位置）。Andromeda会根据服务来收费，下面是目前的一些报价：

*   一个bot v2.x: $500
*   重建 bot: $10
*   SOCKS5 模块：免费
*   Formgrabber 模块: $500
*   键盘记录模块: $200
*   TeamViewer模块: $500

并且这个僵尸网络仍然在活动中，下面是一些统计：

*   10750 个样本
*   130 个僵尸网络
*   474 个编译器ID
*   4.2万个C&C URLs

结论：这个项目仍然在活动，相关的业务也在进行。好几个犯罪团伙都在使用Andromeda，并且Andromeda具有一些很有趣的自定义插件。不错的综述！

在早上喝过咖啡后，Nikita Buchka 和 Mikhail Kuzmin讨论了“_Whose phone is in your pocket?_”（你的口袋里是谁的手机？）。安卓是不错的木马攻击目标。在2015年第三季度，150万多个恶意程序被检测到。现在的攻击趋势就是利用超级用户权限。

大多数恶意程序都是广告软件，一般是通过植入了木马的广告来进行感染。他们解释了安卓上的多广告模式是如何运作的。并且最重要的是，攻击者是如何滥用这些模式。即使攻击者滥用了某个活动来传播木马，那些品牌也会很高兴，因为他们的品牌也算是从中受益了。大多数广告软件会尝试root设备来获取权限。怎样获取权限呢？安卓的安全模式是基于：

*   沙盒
*   权限
*   一个RO系统分区

但是，这里有问题：

*   Binder IPC机制 -> 数据可以被劫持
*   存在root用户 … 可以破解安全模式

“_zygote_” 是一个守护进程，其目的是启动安卓程序。为了安卓木马，需要下面的过程：

*   获取root权限（在旧版本上很容易）
*   在RW模式下重刷系统分区
*   安装恶意apk
*   在RO模式中重刷

当广告软件还不足够时，可以安装其他恶意代码。一个很好的例子是Triada：Triada自带有SMS木马、银行木马、更新模块，与CC通讯。他们解释了木马是怎样感染的设备。应对方案是什么？

*   木马无法卸载（RO分区）
*   一种解决办法是“root”你的设备（不建议）
*   刷入一个旧版固件（如果不懂技术，刷机并不容易并且会丢失数据）
*   处理好了？

下一个议题还是DGA：“_Building a better botnet DGA mousetrap: separating mice, rats and cheese in DNS data_”（创建一个更好的僵尸网络DGA捕鼠器：区别DNS数据中的小老鼠、大老鼠和奶酪）(Josiah Hagen)。

![p11](http://drops.javaweb.org/uploads/images/f360622311e4ddbc77cb1ec7ff186c6f5228fb92.jpg)

第四次讨论了DGA...我想现在我们都知道了黑客会利用这项技术来混淆bot与CC之间的通讯。在这次的讨论中，还涉及到了机器学习。下午，我们还开玩笑说把“Botconf”改成“DGAconf”算了。

Apostolos Malatras 很风趣的讨论了移动僵尸网络，更确切的说，是如何在实验室中研究这些僵尸网络。(“_Building an hybrid experimental platform for mobile botnet research_” 创建一个综合性的实验平台来研究移动版僵尸网络)。如果前面的讨论都集中在木马是怎样攻击安卓设备，那么这次讨论就是安装在这些受感染设备上的僵尸网络是如何运作的。事实上，这与常规僵尸网络的运作方式没有差别：受感染的设备会等待僵尸主控发送的命令。

![p12](http://drops.javaweb.org/uploads/images/8805c02ff3d08d65b2801c0af620da69e1409ec9.jpg)

你要记住，一台移动设备就是一台计算机，但是移动设备中还包含有大量的机主信息（利益丰厚）。并且这些移动设备还会连接其他的计算机，接入企业网络。这些移动设备上有大量的传感器，并且越来越多的用作移动钱包。下面是移动设备使用的一些技术：

*   它们使用了动态IP地址
*   移动网络有诸多限制
*   OS版本众多（是不是很糟？）
*   屏幕大小就是一个漏洞（用户有没有可能会点错链接？）
*   传感器可以用作副通道

僵尸网络的架构也有很多：集成型，分层型、混合型和P2P型。所有这些架构都需要在实验中囊括到。僵尸网络也要满足一些要求：必须原生支持大量的实验，必须可量化，可扩展并且要有足够的可用性。Apostolos检查了某种架构的各个组件（Java技术、Android模拟器，Android调试桥、XML配置文件、用于创建事件的传感器模拟器）。这样做的目的是为了测试移动版僵尸网络，并观察其操作。僵尸网络还会根据不同的方案执行不同的事件。下一个问题是：“移动木马的开发者需要用多久才能测试绕过Android模拟器呢？”实际上，很简单（仅仅利用IMEI就可以）。详细的内容请参阅这篇文章。在Apostolos之后，Laurent Beslay又介绍了“_Mobile botnet malware collection_”（移动版僵尸网络木马收集），基本上是EU在介绍自己的服务。他们正在招人，并已经启动了项目来交换移动僵尸木马方面的信息

午饭后，Paul Jung 上台讲了“_Box botnets_”。好消息：他没有讲到IDA。故事开始于日志文件中出现的一个奇怪的HTTP请求。

![p13](http://drops.javaweb.org/uploads/images/bb6d95cf400a3fb07a7f40183718add109799ca2.jpg)

攻击者会将恶意脚本隐藏在像GIF这样的文件中，从而尝试持续感染目标网站。恶意代码经常会利用字符串`str_rot13()`,`gzuncompress()`来进行混淆。使用在线工具`ddecode.com/phpdecoder`就可以解码。Paul提醒说：大多数提供在线服务的网站，比如这个网站，会保留用户上传的数据。注意你的敏感数据。那么怎样才能感染一个主机呢？这个方案需要：

*   一个启用了PHP的UNIX web服务器
*   一个弱 CMS
*   直接访问互联网（用作备用连接）

根据这一描述，常见的攻击目标有VPS。然后采用一些小技巧，比如更改更改进程名称，从而拦截所有的信号，避免进程被杀掉。另外，木马还会通过一个“窃取”函数通过邮件或特定的HTTP请求来泄露服务器信息。一旦感染，加入到僵尸网络的服务器就可以：

*   执行(很难处理在自己的用户下的web服务器)
*   执行维护任务（更改通道，重命名bot）
*   发送垃圾邮件
*   大量的UDP/TCP/HTTP
*   查找其他要入侵的服务器

通过使用多个搜索引擎（Paul发现了37个），他们可以查找新的潜在受害者。接下来主要讨论了是谁在幕后操控这些bot。这个小组叫做 Toolsb0x。虽然这种入侵方法不是最新的，但是仍然很有效。

然后，我们又讨论了大量的汇编代码：[Matthieu Kaczmarek](https://twitter.com/macteca)提出了“_Malware instrumentation: application to Regin analysis_”（木马插桩：应用到Regin分析）。如今的现代木马都很复杂。为什么选Regin？因为这是一个僵尸网络。其网络拓扑就是一个僵尸网络。

![p14](http://drops.javaweb.org/uploads/images/902c79b7412f63205090aee7dcc883fc66c72fa4.jpg)

要知道，木马通讯可以通过UDP、TCP、cookie、文件、USB磁盘实现。你还需要一个打开世界的窗口。在网络中的每个节点上都有一个私钥以及一个可信公钥列表，每个节点还都有一个虚拟的IP地址。这种设计是以服务为导向的架构，包括有下面的模块：

*   一个协调器
*   核心模块（负责加密、压缩、VFS、网络等）
*   其他模块（刺探、代理等）

在解释了Regin使用的技术后，Matthieu演示了两个Regin模块之间的通讯。在演示中，这两个节点交换了一条“hello”信息。看起来很简单，但是要想逆向所有的东西可需要大量的时间。干的很出色！

在喝完咖啡后，Mark Graham讨论了“_Practical experiences of building an IPFIX based open source botnet detector_”（实践根据开源botnet检测器来创建一个IPFIX）。Mark的问题是什么：如何有效地在云供应商那里检测僵尸网络？Mark说，在云上可是寻找僵尸网络活动的好地方。他首先简单的介绍了IPFIX （说实话我真不知道这是什么）。

![p15](http://drops.javaweb.org/uploads/images/ef8fb96d7571d4c4dae7c92ae6e683253f33186c.jpg)

人人都知道Netflow (Cisco在2009年创建)，但是基本没人知道IPFIX是什么（大部分Botconf的观众都不知道）。Netflow存在哪些问题？

*   主机逃逸
*   VM内部攻击
*   VM逃逸

IPFIX是在2013年发明出了的。IPFIX的一大优势在于需要存储。Mark进行了一次测试，并转出了一个3.1GB的PCAP文件，但是只有43KB的IPFIX文件。PCAP就像是手机通话，而IPFIX就是通话账单（和谁通话，什么时间，通话了多久）。更准确的说，IPFIX开发出来就是为了解决下面的问题：

*   不受厂商影响
*   可扩展
*   多种协议（不仅仅是UDP）
*   更安全
*   为下一代做准备(IPv6, 群播，MPLS)

第二部分讲的是基于Xen & OVS (Open vSwitch)的传感器开发。Mark解释说，他遇到的问题是必须组件的不同版本问题。一旦创建和配置好了，接下来的问题就是找到合适的位置来连接探测器。网络视野是一个关键点。只要在合适的位置连接上合适数量的探测器，我们就能找到有用的信息，但是系统还是有限制：

*   深度包检测（舍弃有效载荷）
*   加密 / VPN 流量 : 有效载荷不是问题，但是VPN隧道中的PDU标头有影响

Mark提出的解决办法是创建一个扩展模板，使用DNS和HTTP参数（比如通过引用页的cookie、age）。不错，也让我了解了IPFIX。

下一篇演讲，[Tal Darsan](https://twitter.com/taldars)介绍了巴西的威胁情况(“_The dirty half-dozen of the Brazilian threat landscape_”巴西威胁概况)。今天的巴西在经历什么？他们使用Delphi，VB脚本和C#。他们使用了封装器：CPL 和 VBE 趋势。Themida 封装器。他们有独特的诈骗地下社区，全面的攻击途径，把恶意程序捆绑到合法工具上。你可以购买到教程，学习诈骗。那么哪些攻击最流行呢？

![p16](http://drops.javaweb.org/uploads/images/7fec9816eb8f01f38250ec35274b9157df26a527.jpg)

*   利用图片发动钓鱼攻击。Tal 介绍了Boleto攻击活动。
*   虚假的浏览器：用于窃取网银凭证(通过小型下载器(banload)放置dropper)
*   重叠攻击（类似于虚假浏览器-创建重复的浏览器内容-不替换浏览器）
*   远程重叠：结合VNC的MITM攻击

很好的调查了巴西威胁！下面的这个网站上可以购买服务来学习“黑客攻击”：[http://www.hackerxadrez.com.br/](http://www.hackerxadrez.com.br/)

[Ya Liu](http://liuya0904/)是今天最后一位演讲者：“_Automatically classifying unknown bots by the register messages_”（根据注册人信息自动分类未知bot）。这一研究的思路是根据计算机在感染后，与CC交换的信息来判断僵尸网络。

![p17](http://drops.javaweb.org/uploads/images/acce5963d50ae5879e42683f7a8d0c23fe1e4a20.jpg)

如今，每天都会出现大量的木马变种，必须要有新技术才能区分它们。大多数木马都可以划分到已知的木马系列，比如zbot或darkshell。它们都有一个共同点：需要与CC通讯。Ya的思路是分析这些木马是如何注册到CC上的（在成功感染后执行的第一个操作）。在注册信息中包含有主机名、IP、CPU、OS、版本等信息。Ya研究了这些信息是如何编码的，以及如何发送到CC上。有趣的研究！

![p18](http://drops.javaweb.org/uploads/images/13480827398b424a9daa6a6dd2861e4301b48e05.jpg)

0x02 第三天
========

* * *

这里是第三天的会议总结。第一篇讨论来自Yonathan Klijnsma，他介绍了Cryptowall的历史概况。Cryptonwall分为多个版本，并经过了几代的发展。这个勒索软件最早出现在2013年9月，具有独立的ID，利用HTTP进行CC通讯。

Yonathan研究了这个勒索软件的通讯协议。Cryptonwall使用了代理和Tor来连接其CC服务器。有可能他就是根据Cryptonwall的通讯才识别出了这个木马。Cryptonwall还给受害者提供了多种支付赎金的选项。第一版的Cryptonwall支持143种文件类型，而Cryptonwall 3.0已经支持了312种。在调查各个版本的过程中，Yonathan也弄明白了各个版本之间的不同，比如加密方法的变化，使用的协议版本（有些版本使用I2P而不是Tor，但是I2P并不是很可靠）。Jonathan评价说：当你在披露木马信息时，一定要小心。因为木马开发者会加入各种论坛、社交网络来监控我们。不要使用TLP:WHITE来交流这样的信息。下面是一些有趣的发现：

*   木马使用了很漂亮的标志和图标（泄露自simiographics.com）
*   木马的代码中有很搞笑的信息
*   木马一直在使用新技术

![p19](http://drops.javaweb.org/uploads/images/f24a7ef180b96251a895baacff09a0be684db0e0.jpg)

如果你对这个木马很感兴趣，Yonathan发布了一些好玩的[工具](http://github.com0x3a/cryptowall)。

然后，[Renaud Bidou](https://twitter.com/rbidou)登台探讨了Javascript(“_Powered by Javascript_”)。有没有人在botnet中发现过Javascript？为了各种不同的目的！

*   注入
*   C&C
*   持续性和灵活性
*   传播，避免检测
*   便于操作

Renaud演示了“你只需要JS就能实现这些任务。”当然，JS注入是基于XSS漏洞实现的。他说“XSS就可以看做是缓冲区溢出。”

![p20](http://drops.javaweb.org/uploads/images/7efb36a6c0b11ee0c36fb84c7afcab18ecddf535.jpg)

在说完XSS之后，他又依次说明了如何用Javascript来实现上述的各种恶意目的。为了保证持续性，必须要通过load.js入侵浏览器（Javascript代码会重新加载自己并从外部URL中加载代码）。他还演示了如何使用包含有代码的PNG图像。为了实现CC通讯，必须使用twitter来获取命令。今天，谁会拦截Twitter呢？Javascript还非常便于操作：

*   我们可以在一个iframe中实现keylogger
*   从浏览器中创建截图
*   WebRTC
*   泄露浏览器信息，本地IP地址
*   获取剪贴板数据

你还可以研究研究[Sniffly](https://github.com/diracdeltas/sniffly)，很有趣的一次攻击活动。Renaud总结说，完全由Javascript组成的木马是可能的。

下一名演讲者[Jeremy du Bruyn](https://twitter.com/herebepanda)，讨论了[DarkComet](http://www.darkcomet-rat.com/)(“_Inside DarkComet: a wild case-study_” 深入DaekComet：一个疯狂的案例研究)。他首先展示了一些研究数据：8万3千个DarkComet样本，4万个配置文件，2万5千个CC，751次渗透。他非常了解这个木马。

![p21](http://drops.javaweb.org/uploads/images/5d3bc5c2fea51fe42a4252a92d36e59f185b5b9d.jpg)

DarkComet是一个看似合法的RAT。这个木马的功能就像是一个全键盘，能够控制远程主机、执行命令、记录键盘输入等。DarkComet有两个组件：CC和bot本身。Jeremy演示了和讲解了一个配置样本（已经解密）。DarkComet使用了静态秘钥，版本不同使用的秘钥也不同。然后，Jerem讲解了木马在感染受害者时，从CC上获取的初始配置。每隔20s，就发送一条活动信息。这种设计非常高效：尽可能的隐藏木马，可以扩展木马的功能，具备反调试功能，支持使用协议，可以收集样本，符合botnet规则（botmaster能够正常识别）。在介绍完这个木马后，他又开始讨论对于样本的分析（4万个）。大部分样本使用了动态DNS（约40%）来联系CC。有趣的是，已经发现的最大bot（8000名受害者）位于法国！这个bot的CC隐藏在了一名居民的ADSL连接上。他解释了自己是如何借助[QUICKUP](http://matasano.com/research/PEST-CONTROL.pdf)漏洞的帮助，破坏了其中的某些CC。

然后，讨论了ANSSI。这在Botconf上可不常见，题目是“_Air-gap limitations and bypass techniques: command and control using smart electromagnetic interferences_”（隔离限制与绕过技术：使用智能电磁干扰进行命令与控制，Chaouki Kasmi, José Lopes Estves）

![p22](http://drops.javaweb.org/uploads/images/5db8594069671a26a653a06897a5e9727d9cf86b.jpg)

首先，隔离是什么意思？不同的IT系统可能设置了不同的安全级别和信任级别（互联网，内网和关键服务）。隔离指的是移除系统中的所有通信通道，形成物理孤立。隔离也有缺点：

*   成本高
*   工作流程，组织限制

但是“哪里有河，哪里就有桥”，怎么绕过隔离呢？

*   使用禁用的接口（软件禁用还不够，必须物理移除）
*   使用共享的外围设备（微控制器，USB设备，显示设备）
*   使用机械波…声音/震动Google Tone,超声波，跨设备追踪
*   使用光 (Shamir, BHUSA keynote 2014)
*   使用温度 (BitWhisper) – ex: 使用CPU活动

或者使用RF！他们演示了如何使用“_Intentional Electromagnetic Interference_”来修改一台正常运行的计算机。他们的实验是基于法拉第笼中的一台设备。给计算机造成了多个影响：PS/2连接错误，USB连接错误，以太网连接错误，导致设备重启。他们是怎么来处理这些问题的呢？

*   移除没有使用的模拟或数字接口
*   监控剩余的接口
*   隔离关键系统（用co-lo还是不用？专门的空间？法拉第笼？）
*   教育用户

下一篇讨论是来Google的Elie Bursztein 和 Jean-Michel Picod提出的 “_Inside traffic exchange networks_”（深入流量交换网络）。在这份报告中没有提到太多关于“流量交换”的内容，而是讨论了交换web流量（SEO）的一种方法。Google很关心这个话题，因为其中存在很多问题…演讲者要求我们不要泄露讨论内容，所以我们没法提供更详细的信息。但是，你可以在这里找到一篇有趣的[文章](http://dl.acm.org/citation.cfm?id=2815708)。

午饭后，[Peter Kleissner](https://twitter.com/Kleissner)讨论了“[Sality](http://www.symantec.com/securityresponse/writeup.jsp?docid=2006-011714-3948-99)”。Sality在2003年出现在俄罗斯，并感染了很多文件。这个botnet有很多目的，利用了一个P2P算法来窃取信息，发送DDoS攻击或发送垃圾邮件。

![p23](http://drops.javaweb.org/uploads/images/36f2ba23eb2bae10567eaa6aa716839027f1e492.jpg)

这个botnet感染了200万+主机，全球范围内总共感染了400万台，虽然没有走向前台，但是这个botnet仍然活跃在今天。根据样本中的昵称和邮箱地址，我们应该能猜出Sality的作者是谁？什么受害者会被感染呢？原因为简单，没有给系统打补丁，并且没有使用AV产品。这个botnet发动DDoS攻击了Virustracker：攻击了4次，从1Gbps到120Gbps。Peter解释了botnet是如何利用了P2P算法，以及其他一些特征。

下一篇是Olivier Bilodeau 提出的“_A moose once bit my honeypot_”（一只曾被我的蜜罐咬过的麋鹿）。这里的麋鹿指的是[Moose](http://www.welivesecurity.com/2015/05/26/moose-router-worm/)。一个内嵌的Linux botnet。

![24](http://drops.javaweb.org/uploads/images/882a8b9c9ab3d3c1604ba3bafac6707bb63190d1.jpg)

所有的IoT设备（智能电视 、IP摄像头、冰箱、路由器等）都有相似的特征：

*   内存/存储小
*   不是x86架构
*   libc实现各种各样
*   支持ELF二进制
*   通常只有主控台

为什么Moose这样的botnet会是威胁呢？因为，难以检测，难以应对和修复。对于坏人来说，这样的设备就是坏人眼中的苹果。Oliver研究了木马的运作方式，以及开发者实现的一些功能。更详细的信息[在这](https://github.com/eset/malware-research/tree/master/moose)。

最后一篇来自Thomas Barabosch“_Behaviour-driven development in malware analysis_”（分析木马中的行为驱动开发）。这份报告研究了如何逆向恶意代码？Thomas的动力是什么？木马分析很无聊！这是一项日常任务，需要重复，投入大量的时间。这些代码仅仅是从asm翻译成更高级的语言，但是怎么保证可靠性呢？解决办法：改善这一过程！

![p25](http://drops.javaweb.org/uploads/images/7f1d35f2fec3e0c8f4bc0a35f0c8e855a96c7fc3.jpg)

他提出了两种方法：TDD-测试驱动型开发和BDD-行为驱动型开发。简单地说：这样做的目的是使用开发技术和过程，并将其应用到逆向工程中，从而改善逆向过程。但是，有趣的是，和众多学术研究者一样，他们说的并不容易立刻实现。

这就是最后一天了。会议在董事会的总结下闭幕。下面是一些统计数字：

*   250 个坐席
*   265 名参与人
*   15桶啤酒
*   亿万升香槟
*   与组织者+1万行聊天

下一次会议会在Lyon 20/11-02/12举办。

![p26](http://drops.javaweb.org/uploads/images/b6873141e4e2d02dadc6c07d35862e172895b14d.jpg)