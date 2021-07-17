# Webshell安全检测篇

0x00 基于流量的检测方式
==============

* * *

**1.概述**

笔者一直在关注webshell的安全分析，最近就这段时间的心得体会和大家做个分享。

webshell一般有三种检测方式：

*   基于流量模式
*   基于agent模式（实质是直接分析webshell文件）
*   基于日志分析模式

Webshell的分类笔者总结如下：

![1p1](http://drops.javaweb.org/uploads/images/aa10569c44cdc4323e4aab7118952f8c2edc6aed.jpg)

前段时间由于工作的需要完成了一个Webshell检测系统，根据当时的需求写了一篇关于使用基于Agent模型和基于日志分析模型来检测服务器上的文件是否是Webshell的文章，原文可以参见：

[http://www.sec-un.org/ideas-like-article-espionage-webshell-method.html](http://www.sec-un.org/ideas-like-article-espionage-webshell-method.html)

![1p2](http://drops.javaweb.org/uploads/images/780c6c10a2bae042db30b8a38d529870c85f7111.jpg)

**2.基于流量的webshell检测思考**

在研究了上述两种模型的检测之后就考虑能否在网络流量上实现Webshell分析和检测。毕竟要实现Agent模型和日志分析模型需要的成本太大不仅要考虑兼容性问题还需要考虑性能及安全性的问题，而如果采用流量（网关）型检测的话成本和部署难度会减小很多，所以有了此文基于流量（网关型）的Webshell检测方法。

要实现通过网络流量检测Webshell首先就需要对流量进行“可视化”，“可视化”的方法有很多可以借鉴目前市场上一些成熟的框架来实现这里就不再多述。我们主要讨论在Webshell被上传到服务器及Webshell在访问过程中网络流量中产生的payload来实现Webshell检测。

**3.上传过程中的Payload**

我们知道正常的网站在有需要的情况下通常会允许上传一些“无害”的文件但是不会允许上传以脚本文件形式存在的文件例如：PHP、ASP、JSP等，而Webshell就是以这种脚本文件的形式存在并且被服务器解析的。在上传过程中虽然不会出现一些攻击payload。但是要向服务器上传文件所以也会产生一些和上传相关的Payload。下面我们讨论一下常见的两种上传的Webshell的形式即上传“大马”和“小马”。

**3.1上传"大马"**

这种方式通过POST直接上传一个Webshell文件或者经过简单的变形然后上传到服务器上,如下面的一个例子：

```
2009-02-10 06:32:58 W3SVC77065997 XXXX.XXXX.XXXX.XXXX POST /lesson_manage/upload/40/ASP.asp – 80 – XXXX.XXXX.XXXX.XXXX Mozilla/4.0+compatible;+MSIE+6.0; 200 0 0

```

从上面这条访问记录中能够发现如下关键特：POST upload ASP.asp 200 通过这几个关键特征的就能够分析出ASP.php可能是一个疑似Webshell。

**3.2上传"小马"**

在不能直接上传“大马”Webshell的情况下黑客通常会上传一个“小马”以协助完成上传“大马”或者上传一句话Webshell并配合一个客户端实现控制服务器，这里我们也不讨论如何上传“小马”以及一句话Webshell。我们只讨论如何利用“小马”来上传“大马”。

这种方式的特殊点在于不是一个完整的文件在网络中中传输而是一个存在于HTTP协议中的一个参数在网络中传输，传输参数的方式既可能是GET也可能是POST，我们来看下面一个真实的例子：

![1p3](http://drops.javaweb.org/uploads/images/a85f08f70c026c777414e66496d433db4416fde9.jpg)

在上图中我们不难发现这显然是使用一句话木马客户端通过POST的形式正在上传一个Webshell的脚本代码，并且将内容写入一句话木马相同目录下的一个body.asp的文件当中，从而实现上传“大马”。在截取到的流量数据中可以发现，如：`act= body.asp value=Execute`等payload，通过在检测这些payload就可以在上传的过程中分析Webshell及其行为。

**4.访问过程中的Payload**

于Webshell是被制作用来控制服务器或者窃取机密信息的，要实现这些能力攻击者就必须向Webshell发送一些控制指令从而操作Webshell。在控制指令中通常包含特征明显的攻击payload。我们来观察一下如下几种payload：

![1p4](http://drops.javaweb.org/uploads/images/98666b57bf88c235921c384d30877b34b6561be2.jpg)

上图中显然是Webshell正在试图连接网站的数据库，并且攻击者使用的是POST的方式向Webshell提交连接参数，其中可以发现的payload有：`action=sqladmin`,`dbhost=localhost`,`dbport=3306`,`dbuser=root`,`dbpass=1qaz2wsx`,`connect=connect`等。

我们再看一个由著名一句话Webshell管理工具“菜刀”远程控制“菜刀马”并发出的指令的流量数据：

![1p5](http://drops.javaweb.org/uploads/images/165d1d8b2ef00443d3c3195b63e927e2fe0ae5c7.jpg)

上图中看出“菜刀”使用了base64的方式加密了发送给“菜刀马”的指令，通过分析我们能够观察到其中的两个关键payload z1和z2。

```
z1=Y21k& 
z2=Y2QgL2QgIkQ6XHd3d1xxaHJkd3dcIiZ3aG9hbWkmZWNobyBbU10mY2QmZWNobyBbRV0%3D 

```

通过解密加密的内容可以得到解密的payload

```
z1=cmd 
z2=cd /d “D:\www\qhrdww\”&whoami&echo [S]&cd&echo [E]7 

```

解密之后的payload就尤为明显了，从中我们可以找到`cd /d cmd whoami echo [S] &cd &echo [E]7`等payload.

经过一定的payload积累和规则的定制再经过和其它检测过程相结合可以形成一套基于流量分析Webshell分析引擎，并且可以该引擎可以很方便的嵌入到现有的网关型设备或云上实现Webshell的深度分析。

0x01 深入用户的内心
============

* * *

**1.WEBSHELL是什么？意味着什么？**

不同人的视角里，Webshell是什么？

*   程序员：一个可以执行的web脚本文件。意味着：就是个脚本。
*   黑客：一个可以拿来控制网站的东西。意味：网站已经搞定，尽量隐藏自己的身份别被发现，同时可以进行后续的破坏行为。
*   用户（站长）： 发现了Webshell，麻烦来了,认真的管理员都会想到很多很多的问题。网站有漏洞，已经被别人攻击了。我该怎么办？

**2.Webshell检测工具和产品（系统）的区别在哪？**

网上有各种各样的开源和免费工具，暂且不说他们的识别率。这些东西为什么仅仅是一个工具？

![2p1](http://drops.javaweb.org/uploads/images/0e490a1413ea2eceabc877b3009b2e3eb90a02b1.jpg)

笔者认为，工具为什么叫工具，主要以下特点：

*   只能解决非常有针对性的问题；
*   使用工具需要预备很多的技术积累和安全知识；（非专业人士用不起来）
*   只会呈现专业结果，解决问题依然需要很多的能力和知识积累。（非专业人士用不起来）
*   工具没有充分考虑用户的需求场景和用户体验。

**3.用户的真正需求是什么？**

理解用户需求确实很深入的一门艺术，用户需求分析其实非常体现一个产品经理或决策人的视野和能力。这个需求是刚需？还是非刚需？是显性需求还是隐性需求？是用户的需求还是用户的需求？需求的紧迫度如何？需求频度呢？（现在都讲用户粘性，低频度的需求很难热卖）是点上的需求还是面上的需求？解决的是用户的痛点和痒点？不要把痛点和痒点混为一谈，痛点是雪中送炭，痒点是锦上添花。（有点跑题，掰扯多了，充分了解需求，从人性角度出发的产品才能更为市场接受）。

就Webshell而言，用户说要检测Webshell，为什么要检测Webshell？用户说要分析日志，为什么要分析日志？目标群体是站长（管理员）的话，他们关心什么。他们心里其实是一连串的问号。

*   我们的网站是不是被人搞了?
*   这个黑客是哪里来的？怎么入侵进来的？为什么要攻击我？进来都干了什么？（黑客是谁？从那里来？想干什么？）
*   网站到底有什么漏洞？如何修复漏洞，不让黑客进来？
*   黑客进来了，可能干了很多坏事，偷走了数据，可能监听窃听了内网很多敏感信息。
*   还有没有其他漏洞存在，别被黑客再攻击进来？
*   有没有其他同区域的系统遭受攻击
*   为避免后遗症，是否需要修改系统口令，设置权限等相关的安全提升措施。
*   ……

简单说我受破坏的程度，如何避免不再出现类似情况，同时关心黑客的来源身份手段等信息（黑客画像）所以Webshell检测系统我们要做的到底是什么？是覆盖WEB类安全事件事后处置的一个平台（或服务）。

主要的功能：

*   监测网站是不是被人入侵了。
*   根据流量找出攻击者的IP地址。
*   结合外部威胁情报对攻击者进行画像，给用户全面的信息。
*   基于流量可以还原攻击场景。
*   根据攻击场景分析网站存在什么漏洞。
*   根据漏洞给用户提供修补加固方案。

**4.用户想要的是什么效果？**

*   告警准确（该报的报 不该报的不报）。
*   告警直观、形象。（可视化好）
*   部署成本小：最好0成本部署，或者便利的接入
*   告警获取方便（比如微信、短信通知）。（用户才没时间天天去看产品的界面，以后监控类的产品告警信息是不是几乎都不要界面了，或者扔几个牛逼的可视化图让领导看，当然统计类的报表还是需要的）
*   告警处理方便：一键式的处理导向，看到告警，我按照自动化的一键式场景，可以方便的自动或人工去处理webshell事件。（傻瓜化处理）

再往俗的说五点：管用、好看、省事、便利、好使。

![2p2](http://drops.javaweb.org/uploads/images/54850a68a2e4dd3c56d3e71b925f471a76bb33e8.jpg)

0x02 基于行为分析来发现"未知的Webshell"
===========================

* * *

**1."已知" or "未知"**

已知的已知，已知的未知，未知的未知，这个最近安全行业也谈的比较多，目前圈内热炒的“威胁情报”，其实应该属于“已知的未知”，对本地来说是未知威胁，其实是别的地方已经发生过的威胁。真正的“未知的未知”怎么办，虽然从没发生过的威胁首次在我们身上发生的概率很小很小，但是目前好多攻击都是窃取管理员的身份或者合法用户身份去做一些貌似合法的操作，这些内部发生的“异常”行为，没有外部的“威胁情报”等数据可对比。

![3p1](http://drops.javaweb.org/uploads/images/a0775a34545d569c6d24d52e4cc7e0847aeeebc5.jpg)

加密会逐步成为网络流量的常态，基于“协议异常或行为异常”将成为无法解读内容情景下安全威胁检测的重要手段。 基于“内容”检测和基于“行为”检测互补来发现威胁。异常不一定是威胁，但一般来说威胁一定首先是异常。下图也表达了基于白名单的异常行为分析的重要性。

![3p2](http://drops.javaweb.org/uploads/images/9c6b05b716a07950fa4f16d7cc3df6b0f9145acf.jpg)

当下的安全攻防一个特点就是，未知攻击会越来越多，你所面临的攻击工具可能是从来没有使用过（或者身边的监控视野范围没有看到过），你手上的webshell样本再多，攻击者总是能制作出新的更轻量级功能更全的webshell，如何发现未知的webshell?如何做到天网恢恢疏而不漏？

**2.基于流量的Webshell的行为检测**

webshell运行后，B/S数据通过HTTP交互，HTTP请求/响应中可以找到蛛丝马迹，这是动态特征检测先前我们说到过webshell通信是HTTP协议。基于payload的行为分析，不仅对已知webshell进行检测，还能识别出未知的、伪装性强的webshell。

![3p3](http://drops.javaweb.org/uploads/images/c582822afbadb6e3ed819bff6f34e98583c69289.jpg)

（1）对webshell的访问特征（IP/UA/Cookie)、payload特征、path特征、时间特征等进行关联分析，以时间为索引，还原攻击事件。

![3p4](http://drops.javaweb.org/uploads/images/e9f9f2676627d1b190a7c539613a50b916a1079a.jpg)

（2）基于异常的HTTP请求

Webshell总有一个HTTP请求，如果在网络层监控HTTP请求（没有监控Apache/IIS日志），有一天突然出现一个新的PHP文件请求或者一个平时是GET请求的文件突然有了POST请求，还返回的200，这里就有问题了。

（3）结合威胁情报，对webshell的来源和作者进行深度分析，充分画像who? when?how? why？(出于什么目的？竞争对手还是恶意攻击者） how?(攻击方法）

**3.基于沙箱技术的行为特征分析**

我们知道中间件需要由某个系统账户来完成启动，所有的WEB脚本文件都通过中间件来完成相应的动作，通过监视系统进程和SQL查询被中间件使用的情况就可以初步的确定在网站中Webshell的存在并且正在运行。再通过中间件来确定最终发起操作的具体脚本文件就可以完成达到最终检测、发现Webshell的目的。

本部分笔者了解有限，就简单的列举出来几条发现具体Webshell的方法。

*   数据库层面检测：通常一个正常的网站所有的数据库操作都通过统一的API来进行的，如果某个脚本文件通过另一种方式来尝试操作数据库的话就可以追踪到这个具体的文件；
*   中间件层面检测：通过第三方的定制化插件来和中间件结合能够实现对发起操作的脚本文件的检测；
*   系统层面行为检测：webshell起来如果执行系统命令的话，会有进程。比如Linux下就是nobody用户起了bash，Win下就是IIS User启动cmd，这些都是动态特征。

0x03 基于流量的Webshell分析样例
======================

* * *

**1."大马"典型操作**

经过前面多篇文章的全面介绍想必大家对如何检测Webshell都有了一定的认识，今天我们一起探讨一下如何从网络流量中去实际的检测和发现Webshell的。

我们知道“大马”的目的就是为了提权以及控制。常见的“大马”一般都是功能较多结构也较为复杂的，“单一文件实现众多功能”是“大马”的设计目的之一，一方面大在功能，另一方面大在体积。在形形色色的“大马”中不难总结其中典型的功能。

![4p1](http://drops.javaweb.org/uploads/images/e55bd2c8204d12a8e78f55b97b93186152ad6af9.jpg)

*   文件操作：上传、下载、编辑、删除。
*   数据库操作：连接数据库、脱库、插入数据。
*   命令执行：提交自定义命令、“大马”预制命令。

当然通常讲的“大马”的功能远不止，但我们将讨论在流量中如何发现这三种功能被攻击者操作进而发现Webshell的。

**2.典型操作之流量Payload**

**2.1文件操作**

让我们来进行一个简单的提权工具的上传的操作，通过Webshell我们可以这样做：

![4p2](http://drops.javaweb.org/uploads/images/764379f4472bf9d7f8f78cd8dd6aef733d8437ce.jpg)

在文件成功发送到服务器上之后我们来看一下在服务器端我们从网络流量中抓取的记录：

![4p3](http://drops.javaweb.org/uploads/images/f14f0f6c72e156416e51a06b742019c6b6bdf63e.jpg)

紧接着我们从流量中看一下服务器返回的包的内容：

![4p4](http://drops.javaweb.org/uploads/images/2c130f1e91193fb3ac87db9c991b1046476b3d06.jpg)

通过抓取实际的网络流量来获取一对Payload他们分别出现在访问请求中和服务器返回的数据中：

```
Request Payload：POST|upfiles|pr.exe
Return Payload：200

```

通过上述Payload我们就可以大概总结出以下结论：

该服务器可能已经被入侵并且被成功上传Webshell后门，攻击者正在尝试利用Microsoft Windows RPCSS服务隔离本地权限提升漏洞（MS09-012）漏洞进行提权，也意味着该服务器可能已经有很长未安装过系统安全补丁。

**2.2数据库操作**

再来看一个真实的操作MySQL数据的一个例子：

![4p5](http://drops.javaweb.org/uploads/images/86c6db88923badfa4a438db824fec687e7cd5700.jpg)

同样的在服务器上通过抓包工具获取的流量信息如下：

![4p6](http://drops.javaweb.org/uploads/images/539bf556f6f00633de244e8bf871157a980df550.jpg)

![4p7](http://drops.javaweb.org/uploads/images/36077bafb85f493f1a4fa05b105001ac298e30d7.jpg)

服务器返回的流量信息也一并拿出来：

![4p8](http://drops.javaweb.org/uploads/images/0f2cbe40fafea804b31dcb74331b448df000d575.jpg)

![4p9](http://drops.javaweb.org/uploads/images/304a4d0d98f6ca4c466321be60ffcdd0febcab00.jpg)

可以看到在一个连接数据库的操作过程中流量中也产生了众多的Payload，简单的将POST数据进行URL解码可以看的更明显一些：

```
auth[driver]=server&auth[server]=localhost&auth[username]=root&auth[password]=&auth[db]=mysql&auth[permanent]=1

```

再来分析一下Payload对：

```
Request Payload：POST|localhost|root|mysql
Return Payload：localhost|root|mysql|200|*.sql|user

```

通过上述成对的Payload可以分析出以下结论：

攻击者正在试图访问MySQL数据库并且访问了mysql库中的表信息攻击者可以将该mysql库中的表到导出.sql文件

**2.3命令执行**

最后我们来看一个命令执行的操作过程：

![4p10](http://drops.javaweb.org/uploads/images/f0dffb1d21993a64aae6ecf560b813aeec8c240a.jpg)

检查服务器端获取到的流量数据：

![4p11](http://drops.javaweb.org/uploads/images/f04a7eaa0ecba20a3837722b8e61ee0543c84016.jpg)

检查服务器返回的流量可以得到如下数据：

![4p12](http://drops.javaweb.org/uploads/images/84ebd4175d0c7de55aa07e12c8ac91089081ff64.jpg)

![4p13](http://drops.javaweb.org/uploads/images/3058a9b4818ca483f38621d7db597d507a6449fb.jpg)

在这个案例中攻击者向服务器发送了一条查看当前权限的命令，服务器在获得指令后运行并将结果通过响应主题反馈给攻击者。我们来分析一下Payload

```
Request Payload：POST|act=cmd|cmd=who|precmd
Return Payload：200|net authority\|system

```

通过上述总结的Payload可以得出以下结论：

服务器已经被入侵，攻击者试图向服务器发送查询中间件运行时所用操作系统权限并获得了满意的结果，接下来这台服务器的悲惨的结局可想而知。

相对于一句话Webshell管理工具而言“大马”在访问过程中的Payload相对来说比较简单也更显而易见，在检测的时候也相对容易一些，但是凡事没有绝对，经过加密和预制命令的Webshell来讲也完全可以逃脱上述Payload检测过程。

0x04 webshell之"看见"的能力分析
=======================

* * *

**1.webshell的典型攻击序列图**

下图是一个典型的webshell的攻击序列图，利用web的漏洞，获取web权限，上传小马，安装大马，然后远程调用webshell，执行各种命令，以达到获取数据等恶意目的。

![5p1](http://drops.javaweb.org/uploads/images/832544e284674c5dff9b2a77fc241f2b2ac4507d.jpg)

Rsa的一段分析材料，对看见能力做了便利的说明。并针对基于流量的分析手段与传统的IDS\IPS\SIEM做了对比。![5p2](http://drops.javaweb.org/uploads/images/224c0dacf53c85c7b4ec1bc05d4f8025db9279f1.jpg)

**2.从killchain来分析各阶段“看见”能力**

从kill chain来看，靠采集系统自身的流量的技术手段，在前两个阶段Reconnaissance、Weaponise这两个阶段是很难看到行为。（结合威胁情报可以更大范围的看到这两个阶段的信息），基于流量的payload分析技术可以在Delivery、Exploit、Installation、Command &Control (C2)、Action这几个阶段都能看到攻击行为。

![5p3](http://drops.javaweb.org/uploads/images/afd4d5ce2da1a498cb044e5d15fa6f58622a3dad.jpg)

**3.从防护方的“安全对抗”能力视角看**

安全防护能力分几个等级

![5p4](http://drops.javaweb.org/uploads/images/7203ff88eefa57f174843db8fa95659b2c662eea.jpg)

*   Detect: Can you see/find it?（能否检测到攻击）
*   Deny: Can you stop it from happening? （能否避免遭受攻击）
*   Disrupt: Can you stop it while it’s happening?（能否阻止正在进行的攻击）
*   Degrade: Can you make it not worth it?（能否让攻击者觉得攻击不值得，降低其攻击级别）
*   Deceive: Can you trick them [the adversary]?（能否诱骗或重定向攻行为）
*   Destroy: Can you blow it up? （能否摧毁攻击者）

针对web的安全防护能力手段总结如下图：

![5p5](http://drops.javaweb.org/uploads/images/4441b594649145f23310f0dfd95dab644c7e692a.jpg)

**4.Webshell的检测的三种手段**

从安全防护能力看，检测是第一位的能力，webshell的检测主要有以下几种方式：

（1）基于流量的webshell检测引擎

*   方便部署，通过流量镜像直接分析原始信息。
*   基于payload的行为分析，不仅对已知webshell进行检测，还能识别出未知的、伪装性强的webshell。
*   对webshell的访问特征（IP/UA/Cookie)、payload特征、path特征、时间特征等进行关联分析，以时间为索引，还原攻击事件。

（2）基于文件的webshell分析引擎

*   检测是否包含webshell特征，例如常用的各种函数。
*   检测是否加密（混淆处理）来判断是否为webshell
*   文件hash检测，创建webshell样本hashing库，进行对比分析可疑文件。
*   对文件的创建时间、修改时间、文件权限等进行检测，以确认是否为webshell
*   沙箱技术，根据动态语言沙箱运行时的行为特征进行判断

（3）基于日志的webshell分析引擎

*   支持常见的多种日志格式。
*   对网站的访问行为进行建模，可有效识别webshell的上传等行为
*   对日志进行综合分析，回溯整个攻击过程。

三种检测方式，基于文件的检测，很多时候获取样本的部署成本比较高，同时仅仅靠样本无法看到整个攻击过程。基于日志的有些行为信息在日志中看不到，总体来说还是基于“流量”的看到的信息最多，也能更充分的还原整个攻击过程。