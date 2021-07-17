# Packrat 攻击南美长达七年的威胁小组

> [https://citizenlab.org/2015/12/packrat-report/](https://citizenlab.org/2015/12/packrat-report/)

0x00 概括
=======

* * *

这份报告介绍了一次大规模的木马、钓鱼和虚假信息活动，这一攻击活动的目标是几个拉美国家，包括厄瓜多尔、阿根廷、委内瑞拉和巴西。根据受害者的特征和地理分布来看，这次攻击活动的赞助者对这些地区的政治情况很感兴趣。** Packrat**很关注这些地区的政治反对派，ALBA国家联盟（**美洲玻利瓦联盟***||||*）**，以及这些国家境内的独立媒体。ALBA国家联盟通过一项贸易协定建立，这些国家在很多非经济领域都有合作。

在2015年，我们率先在厄瓜多尔捕捉到了一波攻击活动，接着在2014年，我们发现这些攻击活动与在阿根廷境内活跃的一起行动有关联。我们在阿根廷发现攻击行动时，攻击者正好在试图入侵Alberto Nisman和Jorge Lanata的设备。根据我们所了解的行动情况，我们又调查发现，这个攻击小组的活动最早可以追溯到2008年。

在这份报告中，我们拼凑起了各个活动碎片，包括使用的木马、钓鱼活动，以及在拉美放置的CC服务器。Packrat甚至在委内瑞拉和厄瓜多尔创建了虚假的互联网组织。谁应该对此负责呢？我们在评估了攻击者使用的一些攻击方案后认为，Packrat很可能是某个政府赞助的攻击小组，而且他们也并不担心自己的活动、目标和维持方法会暴露。但是，我们并没有确定Packrat的赞助者具体是谁。

0x01 Packrat的七年行动
=================

* * *

本文的作者们仍然独立地调查这些出现在拉美的木马和钓鱼活动。在这份报告中，总结了我们的调查发现。这些攻击活动的主要目标位于拉美国家，包括委内瑞拉，厄瓜多尔，阿根廷和巴西。我们把这些行动的策划者叫做Packrat，因为他们很喜欢用加壳了的RAT木马，在这么多年来，他们也一直在使用相同的域名和服务器。

![p1](http://drops.javaweb.org/uploads/images/a12b1407e0468666545cee866a020ab43ec3eaa3.jpg)图1-已知的一些Packrat攻击目标和活动类型

Packrat会利用木马和钓鱼活动来系统性地攻击一些政治高层，记者和外国目标。我们发现Packrat在这7年中，总共使用了12个不同的木马CC域名，超过30个木马样本。另外，Packrat还喜欢利用一种很有趣的攻击策略：首先，成立并运营虚假的反对派组织和新闻组织，然后利用这些组织来传播木马并执行钓鱼攻击。

在这些假冒的组织中， 有的仅仅是一个名字而已，有的会更精心设计在线活动。Packrat还会创办假冒的新闻机构，但是我们并没能在木马或钓鱼活动中发现任何证据。

![p2](http://drops.javaweb.org/uploads/images/2f37ef09632f993fea4e5d0ab5b495b4a97891ed.jpg)图2-Packrat的主要活动

我们发现Packrat最早的活动可以至少追溯到2008年。通过确定网络基础设施之间的关联，我们发现了几波攻击活动，在这些活动中使用了不同的工具和战术。在这一部分中，我们会简要地介绍Packrat在不同时间使用的一些网络基础设施，以及实施的攻击活动。更详细的木马使用历史，请看“3. Packrat植入木马的进化”。

**Packrat最大规模的攻击行动**

**2008-2013**

Packrat使用的工具和基础设施表明，他们至少从2008年就开始活动。在这段时间中，Packrat利用了巴西的托管服务，其中的一些木马样本也是通过巴西的IP地址上传到了常用的在线杀毒服务商。他们发送的一些信息也涉及到了针对巴西用户的诱饵内容。从中就能判断，这些活动是以巴西用户为目标，不过，我们还没有确定在这段时间遭到了攻击的受害者身份。

**2014**

到2014年，Packrat开始攻击高价值目标-阿根廷律师Alberto Nisman和著名的记者、电视节目主持人Jorge Lanata。Maximo Kirchner，阿根廷总统的儿子也声称自己遭到了攻击。Maximo Kirchner公布的钓鱼邮件也是我们见过的，但是我们还无法证明他是否真的遭到了袭击。除此之外，我们发现大量与Ecuadorian和Venezuelan相关的钓鱼域名在这段时间非常活跃。

**2015**

在2015年，涌现出了大批针对公民团体和公众人物的钓鱼和木马活动，包括厄瓜多尔议会。我们观察到了大量的钓鱼域名和攻击活动。在这段时间中出现的行动经常会利用攻击者成立的虚假组织。我们发现攻击者利用这些假冒的组织和虚假信息攻击了厄瓜多尔，委内瑞拉境内的目标。

### 1.1 Nisman与阿根廷境内的攻击活动

2015年1月，颇有争议的阿根廷检察官Alberto Nisman遭到枪杀。阿根廷新闻媒体报道称，布宜诺斯艾利斯市警察局刑侦实验室在他的Android手机上发现了一个恶意文件“**estrictamente secreto y confidencial.pdf.jar**”（意思是高度机密）。

在2015年5月29日，阿根廷的一名用户上传了一个相同名称的文件到Virustotal上。这个文件是一个远程入侵工具- AlienSpy，可以允许攻击者记录目标的活动，访问其邮件、网络摄像头等。但是，这个文件针对的是Windows操作系统，并不能感染Nisman的安卓手机。

Morgan Marquis通过分析Alienspy，确定了攻击者使用的CC服务器是**deyrep24.ddns.net**。除了用于攻击Nisman，Lanata和Kirchner的木马，还有另外三个样本也在使用deyrep24.ddns.net作为CC服务器。其中一个样本-**3 MAR PROYECTO GRIPEN.docx.jar**是基于AlienSpy开发的，这个样本伪装成了一个文档，这个文档的内容利用了厄瓜多尔总统科雷亚与厄瓜多尔大使斯维登就购买战斗机的商讨意见。

在公布这一发现后，其他一些遭到攻击的目标也逐渐浮出了水面。著名的调查记者、电视节目主持人Jorge Lanata称自己也遭到了同一个木马的攻击。总统的儿子Maximo Kirchner也声称自己是攻击目标。我们无法证实Kirchner的说法，但是，他公布了一张钓鱼邮件的截图：

![p3](http://drops.javaweb.org/uploads/images/3e00575296ecfb89edaa158804afca05c09d1305.jpg)图3- Maximo Kirchner说明自己遭到了攻击

他说，在这份邮件中有一个叫做“Estrictamente Secreto y Confidencial.pdf.jar”(大小67.3kb)的附件，Nisman和Lanata收到的也是这个木马。另外，发件人的邮箱地址([claudiobonadio88@gmail.com](mailto:claudiobonadio88@gmail.com))宣称是著名法官Claudio Bonadio。Lanata接收到的邮件也是声称来自Claudio Bonadio ([cfed.bonadio@gmail.com](mailto:cfed.bonadio@gmail.com))。

### 1.2 厄瓜多尔境内的活动

在2015年，厄瓜多尔境内有大量的记者和公众人物遭到了钓鱼攻击，主要是通过邮件和短信。我们检查了这些邮件，其中一些并没有涉及政治内容，而是为了窃取用户的社交媒体和邮箱凭据，比如Gmail。但是，其他的一些邮件利用了与政治人物和厄瓜多尔问题相关的政治内容。通过进一步的调查，我们发现了一起大规模的攻击行动，以及攻击者成立的各种虚假组织。

本文的一位作者开发了一个Gmail搜索查询，能够查找与攻击活动相关的字符串（附录A：搜索查询）。我们把这个搜索查询分享给了大量的潜在目标，并发现了大量的钓鱼活动和可疑的Word（DOCX）文档。这些可疑文档中内嵌了用Java编写的RAT，包括Adzok和AlienSpy。接着，我们使用在JAR文件中发现的标识和更新后的Gmail查询，识别出了Packrat使用的各种恶意文件和域名（附录B：木马样本）。

我们发现钓鱼网站和木马网站之间还有联系。这些网站通常会共用相同的注册信息，或托管在相同的服务器上。我们判断出，这些木马样本通常会与**daynews.sytes.net**通讯，与阿根廷境内的活动有关联。最终，通过调查这个**daynews.sytes.net**基础设施，我们发现了在巴西使用的木马和基础设施，以及在委内瑞拉使用的虚假网站。

### 1.3 共同的CC基础设施

这一部分介绍了Packrat使用的CC基础设施。在附录B中，我们提供了完整的CC域名、相关的二进制和木马家族。

Packrat使用的**deyrep24.ddns.net**域名是在2014年11月7日创建的，在攻击Nisman时，这个域名指向了IP地址：**50.62.133.49**。这个IP地址属于GoDaddy，在2015年3月3日，这个域名更改了GoDaddy：**192.169.243.65**。被动DNS记录表明，**deyrep24.ddns.net**在使用这个IP地址时，在2015年3月1日创建的**daynews.sytes.net**也在利用这个IP。在我们联合调查期间，我们发现了5个木马样本都在使用这个域名来攻击厄瓜多尔境内的记者和民主社区。

Packrat使用的CC基础设施

![p4](http://drops.javaweb.org/uploads/images/08f6af00a8f7fb73c74dd76d263395c2cdbecbe8.jpg)图4-Packrat的CC基础设施

通过搜索与**daynews.sytes.net**相关的域名，我们找到了**taskmgr.serveftp.com**，这个域名在2014年8月11日时的IP地址是**190.210.180.181**。这个IP地址属于阿根廷，**daynews.sytes.net**在刚注册的那段时间中使用了这个IP，接着很快就转向了GoDaddy。在2014年10月、2015年5月的几天中，**taskmgr.serveftp.com**域名又重新使用了**190.210.180.181**。在2014年7月23日，**taskmgr.serveftp.com**托管在了**201.52.24.126**上，这是巴西的一个IP地址，这个IP还托管了**taskmgr.servehttp.com**和**taskmgr.redirectme.com**。我们总共发现了15个木马样本不是使用了**taskmgr.servehttp.com**，就是使用了**taskmgr.serveftp.com**作为CC域名（有几个样本同时使用了这两个域名）。样本的最早版本是在2008年12月14日编译的，借此，我们可以知道Packrat最早是在这时候活动的。然而，这个时间戳也可能是假的，我们还没有在其他样本中发现证据能证明这一点。

Packrat使用的CC基础设施

![p5](http://drops.javaweb.org/uploads/images/bb0b28f87989a6ff93ee77fa95dd35f59f885309.jpg)

在2014年7月11日，所有的‘taskmgr’域名都托管在了**186.220.1.84**，这是巴西的一个IP地址。同一时间，这个IP还托管了**ruley.no-ip.org**。我们成功找到一个样本既使用了**ruley.no-ip.org**也使用了**taskmgr.servehttp.com**作为其CC域名。在2012年9月6日，**ruley.no-ip.org**托管在了**189.100.148.188**，这个IP仍然属于巴西，另外还有两个域名**lolinha.no-ip.org**和**wjwj.no-ip.org**也使用了这个IP。我们发现有两个样本配置了使用这三个域名作为CC服务器，有三个样本使用了**ruley.no-ip.org**和**wjwj.no-ip.org**，有一个样本只使用了**ruley.no-ip.org**。在2014年8月15日，**taskmgr.servehttp.com**托管在了**186.220.11.67**，这个IP同样属于巴西。在相同时间，这个IP还托管了**conhost.servehttp.com**和**dllhost.servehttp.com**。我们发现了两个样本配置使用了**conhost.servehttp.com**和**dllhost.servehttp.com**作为CC服务器。

除了这些域名，域名wjwjwj.no-ip.org和wjwjwjwj.no-ip.org有关联。在2014年3月25日，wjwj.no-ip.org和wjwjwj.no-ip.org指向了179.208.187.216。我们还没有发现样本只使用了wjwjwj.no-ip.org或wjwjwjwj.no-ip.org。

这些域名背后的CC服务器是由拉美的提供商托管的，包括Uruguay Montevideo Administración Nacional De Telecomunicaciones, Argentina Buenos Aires Nss S.A. (IPLAN), 和 Claro Brazil。

Packrat还利用了欧洲和美国的服务器，包括瑞典的Portlane和美国的GoDaddy。

我们想要通过确定这些主机服务提供商，从而关停Packrat的基础设施。

0x02 近期在厄瓜多尔出现的木马攻击活动
=====================

* * *

Packrat活跃在很多国家中，但是我们在厄瓜多尔收集到了大部分活动证据，以及这些活动与目标和受害者之间的关联。在写这篇文章时，我们仍然在跟踪针对厄瓜多尔目标的攻击活动。

![p6](http://drops.javaweb.org/uploads/images/138ab803f3f67b6c076d1b9362c3d88e4ae62e25.jpg)图5-已知在厄瓜多尔境内Packrat的攻击目标

通过利用邮箱搜索查询，并分析木马的数据库和CC基础设施，我们收集到了大量针对记者、公共任务、政治家等的木马和钓鱼活动。

### 2.1 针对厄瓜多尔境内Packrat木马的分析报告

在这些报告中，有的是公共报告，有的是社交媒体上的讨论。例如，厄瓜多尔言论自由组织Fundamedios就报道称，一些公众人物、新闻组织、Fundamedios的领导都接收到了可疑的信息和钓鱼邮件。随后，Fundamedios又更新报告称这些木马使用了相同的CC基础设施，而攻击Nisman的木马也使用了同一个基础设施。在Twitter上也有相关的木马和钓鱼活动说明。我们发现了很多与Packrat相关的报道。

### 2.2 常用技术

们观察到，攻击者利用了社会工程技术来传播木马攻击厄瓜多尔境内的目标。在一次活动中，我们发现了一个木马经常会配合政治内容的诱饵使用，利用的经常是有关厄瓜多尔反对派的信息。在其他的一些情况下，攻击者会根据特定的木马来制定传播途径，大多是通过包含有恶意Java的Microsoft Word文档来投递木马。但是，在其他情况下，攻击者会利用虚假更新来传播木马。

常用的木马传播技术:

*   使用恶意文件作为附件
*   在攻击者控制的网站上放木马链接
*   通过Google Drive或Onedrive
*   弹窗或虚假的政治网站通知

Packrat在社交工程技术中利用的发件人和网站都会伪装成真正的用户和组织。例如，他们注册了ecuadorenvivo.co，看起来像是Ecuador En Vivo新闻网站的域名(ecuadorenvivo.com)。然后，Packrat会发送疑似来自ecuadorenvivo.co的新闻邮件更新（真正的Ecuador En Vivo网站就是有这个功能）。

Packrat有时候还会创建相同的新闻事件路径，并隐藏在链接中。比如：

**类似的域名**

目标看到的样子：

*   [http://ecuadorenvivo.com/videos/el-meme-que-volvio-loco-a-correa.html](http://ecuadorenvivo.com/videos/el-meme-que-volvio-loco-a-correa.html)

真正的恶意链接：

*   [http://ecuadorenvivo.co/videos/el-meme-que-volvio-loco-a-correa.html](http://ecuadorenvivo.co/videos/el-meme-que-volvio-loco-a-correa.html)

### 2.3 三次攻击活动

为了说明Packrat的攻击方法，在这一部分详细地介绍了3起近期发生的攻击活动。这三次攻击活动发生在2015年春—2015年秋。攻击目标包括厄瓜多尔的记者和公众人物。

**2.3.1 攻击活动1：来自虚假反对派的邮件**

在2015年4月，多个目标都收到了来自“Movimento Anti Correista”（反科雷亚运动）的邮件，这是攻击者虚构的一个反对派组织。在这些邮件使用了包含有Adzok木马的Microsoft Word附件，以及文本和图片来增加邮件的可信性。

**“Movimento Anti Correista”发送的邮件**

![p7](http://drops.javaweb.org/uploads/images/a1a1e2e38aa07a68d319124c97c5b6bdfe47b94f.jpg)图6-“Movimento Anti Correista”发送的邮件

这份邮件有几个目的，很显然是为了诱使目标下载并浏览文档，但是似乎也是想要确定域名的合法性，以及活动的身份。

**恶意附件**

*   名称：La jugada sucia De Correa ante la oposición.ppt
*   类型: Microsoft Word Document file (.docx)
*   MD5: ea7bcf58a4ccdecb0c64e56b9998a4ac

![p8](http://drops.javaweb.org/uploads/images/e4c295f351ffcbeed24fbdc0a977ccdfd4cc32b6.jpg)图7-恶意邮件

在这个文档中内嵌了一个叫做“[Adzok – Invisible Remote Administrator](http://adzok.com/)”的软件。

**2.3.2 攻击活动2：你在被监视着！**

这次攻击活动旨在引起目标的恐慌和担心，从而诱使目标打开恶意文件。钓鱼邮件是根据目标定制的，并恐吓目标正在SENAIN，厄瓜多尔的国家情报部门监控着。邮件附件宣称是在SENAIN监控下的Twitter用户名单。有趣的是，邮件的发送人是“Guillermo Lasso”，上次总统竞选失败的候选人。

![p9](http://drops.javaweb.org/uploads/images/07ece9036b4324e2058d15c17548be3aa77105d1.jpg)图8-发件人号称是“Guillermo Lasso”，上次总统竞选失败的候选人

像第一次攻击活动一样，这个木马并没有投递漏洞，但是需要受害者双击文件，并在执行前接受所有的弹窗。

**要求目标点击的文档:**

![p10](http://drops.javaweb.org/uploads/images/3b9ce0e5875d3278b9dc7e7cb9b35ea39a7f49e5.jpg)图9-要求目标点击的文档

一旦用户双击了图像，目标就会感染AlienSpy木马。通过检查木马的配置文件，我们发现木马使用了C2服务器daynews.sytes.net，Packrat经常在攻击活动中利用这个域名。有趣的是，我们发现在其他的一些攻击活动中也使用了同一个诱饵文档（相同的MD5）。

![p11](http://drops.javaweb.org/uploads/images/a5e7ba9837de3fe77acf43a841d9a8715675eeee.jpg)

**2.3.3 攻击活动3: “关于Correa撒谎的独家消息”**

这次攻击活动利用了一个设置有恶意内容的虚假政治网站。而恶意邮件会把受害者定向到这个网站上。有意思的是，这次攻击活动会尝试欺骗目标相信这是记者[Focus Ecuador](http://focusecuador.net/)的合法网站。Packrat似乎控制了.tk和.info域名。

![p12](http://drops.javaweb.org/uploads/images/55f4e2895f38a2e6b6e554120cd18fb5574f7b94.jpg)

关于 Correa撒谎的信息，请看视频：[http://focusecuador.tk/](http://focusecuador.tk/)

这份邮件中还包括有一个来自mesvr.com的跟踪图像，ReadNotify经常使用这个图像来跟踪邮件的发送情况。攻击者似乎是想要获取更多关于目标的信息，比如确定不远打开恶意文件的目标IP地址。

focusecuador.tk网站中包含有从合法网站上复制来的信息，但是也给受害者显示了一个Flash更新通知。在点击时，链接就会触发“plugin_video.jar”的下载。

**虚假的Flash更新通知**

![p13](http://drops.javaweb.org/uploads/images/869a4d0ebbc5002d09e66f40bb7a4bf94ae456f4.jpg)图10-虚假的Flash更新

这并不是一个Flash更新，而是一个捆绑了AlienSpy / Adwind的远程访问木马。在执行时，基于Java的木马会与Packrat的CC服务器46.246.89.246 (daynews.sytes.net)通讯。通过分析木马，我们发现了相同配置的LOS TUITEROS ESPIADOS POR SENAIN.docx和Los trinos de Rafael Correa.docx样本。

**攻击活动3：二进制**

*   名称: plugin_video.jar
*   类型: Java Archive (JAR)
*   MD5: 74613eae84347183b4ca61b912a4573f

### 2.4 Packrat发话了！

在我们分析攻击行动3期间，一名Packrat攻击者开始在受感染的机器上用西班牙语和英语与一名Citizen Lab的研究员交流。

![p14](http://drops.javaweb.org/uploads/images/ff4242ac529ba6c74cf45dd3a4cd0f391d69a0ff.jpg)图11-出现在Citizen Lab研究员屏幕上的威胁和辱骂

这些谩骂会以弹窗或文本的形式显示在IE浏览器中。攻击者威胁了我们的研究员，“你现在在玩火，不小心就死了！”有些信息还不是惯用的西班牙语，借此可以推测攻击者的母语。

攻击者还使用了Windows 文本转语音功能，在受感染的计算机上播放西班牙语的音频来恐吓我们的研究员。

在10月份的时候，攻击者再次恐吓了一名研究人员，接着利用植入木马远程关闭了受感染的设备。

这种情况很不常见，很少有攻击者会与研究人员接触。因为攻击者这样做，非常不安全。可能以前有个人尝试处理或分析过Packrat的文件，尤其是在基础设施暴露之后，所以他们才会这样做。因为Packrat很喜欢让基础设施保持在线，所以他们不喜欢其他人的关注。

0x03 Packrat植入木马的进化
===================

* * *

在过去的七年中，Packrat使用了几种不同类型的木马，大多是可以买到的现成RAT，比如Cybergate, Xtreme, AlienSpy, 和 Adzok。虽然，研究人员都知道这些木马，但是Packrat会使用一系列的工具来混淆这些木马，他们使用的工具有一个未知的VB6 crypter，AutoIt3Wrapper, UPX, PECompact, PEtite, 和Allatori Obfuscator。通过混淆，Packrat的攻击活动就能绕过检测。在这一部分中，我们根据时间分组，介绍了这些工具。

![p15](http://drops.javaweb.org/uploads/images/d8a896c57c9a3bdce12fc059f0c6de6be748caef.jpg)图12-Packrat木马家族

### 3.1 2008-2014: 加壳RAT，主要是CyberGate RAT

在2008年-2014年期间，Packrat大范围利用了现有的RAT，然后用AutoIt3Wrapper进行了加壳。这个加壳程序是用 AutoIt编写的，是Windows中能自动处理任务的一种脚本语言。使用混淆能够误导检测，并且他们使用了一些基础的反调试技术。

攻击者投放的木马中，有大量是CyberGate RAT。在2013年和2014年，Packrat似乎还采用了XtremeRAT。Cybergate 和 Xtreme都是用Delphi编写，这两个木马与另外两个基于Delphi的木马SpyNet 和Cerberus都使用了相同的代码。

在很多攻击活动中都利用了Office文档作为诱饵，在执行植入木马时，诱饵文档就会打开。在我们发现的诱饵文档中，有的是巴西求职者的简历，有的是巴西律师联合会的支付单据。

![p16](http://drops.javaweb.org/uploads/images/f3af6debd597a5625e6be8aa8c48247f940ef99a.jpg)图13-一份简历

这些攻击活动表明，Packrat在这段时间的攻击目标中有的是说葡萄牙语。有些特定的诱饵文档针对的是巴西境内的目标。

![p17](http://drops.javaweb.org/uploads/images/bb11983d02bafaae92f36247b6a7deb5f2bb75b5.jpg)图14-支付单据

我们发现，大量的植入木马都会与CC域名taskmgr.servehttp.com通讯，其他的几个CC还有**ruley.no-ip.org**,**lolinha.no-ip.org**, 和**taskmgr.serveftp.com**。

**3.1.1 分析 CyberGate RAT**

我们分析的CyberGate RAT样本通常会封装一层AutoIt。二进制中的代码和字符串表明，这个木马基于的是Spy-Net RAT 2.6版。这个RAT是一名巴西黑客开发的，使用了spynetcoder，在Spy-Net RAT的“官方网站”上有标注。

**CyberGate的感染例程**

在解压后，CyberGate就进入第二阶段，运行感染例程。感染例程会在运行进程中注入第三阶段的DLL。在植入后，CyberGate 会部署维持技术并监控受害者。

第三阶段模块会选取三个执行路径（根据互斥量）：

*   密码收集 (互斥量: “`_x_X_PASSWORDLIST_X_x_`”)
*   拦截其他应用中的鼠标和键盘输入 (互斥量: “`_x_X_BLOCKMOUSE_X_x_`”)
*   感染例程

**CyberGate 反分析**

木马的感染例程自带了反分析功能，这些功能都打包在一个单独的函数中。CyberGate 会搜索虚拟环境和沙盒环境，并且会通过IsDebuggerPresent API检查调试工具，通过管道来查找SoftICE 和 Syser 。木马会通过检查每个函数的第一个字节是不是“CC”，来判断函数入口上是不是有断点。

![p18](http://drops.javaweb.org/uploads/images/906a1bd74c2561206a468109c415e3ceb2b85c34.jpg)图15-CyberGate 反分析

**CyberGate 进程注入**

感染例程会从资源节获取加密的植入，在解密后，尝试把植入注入到Windows system shell进程 (explorer.exe)。如果失败，CyberGate会自己启动一个 explorer.exe进程，将植入注入到进程中，然后完成设置。除此之外，另外的一个CyberGate实例会注入到隐藏的默认浏览器进程中。

感染例程会复制自己，并将副本投放到不同的目录下，具体要取决于Windows版本：/System, /Windows,或 /Program Files。植入木马的名称也会变化：taskhost.exe, regedit.exe,和taskmgr.exe都是很常用的。另外，感染例程还会把加密后的植入木马副本写入%TEMP%目录，并命名为XX–XX–XX.txt。

为了让木马维持的更长久，第二阶段会写入注册表键值，让CyberGate开机启动：

![p19](http://drops.javaweb.org/uploads/images/a13d457f17ce99e63942291432dc8800a52c6c3b.jpg)

**密码收集**

如果有收集密码的任务，第二阶段的二进制就会从多个位置收集密码：No-ip 动态更新客户端(DUC), MSN messenger, Firefox, 和 Internet Explorer。登录凭证是从Windows注册表、浏览器、RAS拨号设置、本地安全认证（LSA）设置、MS ProtectedStorage、MS IntelliForms和凭证商店中获得的。

**CyberGate的功能**

CyberGate会运行两个例程。第一个例程是在默认浏览器进程中运行的。同时，explorer.exe例程会作为一个“看门狗”，用于维护木马，并确保磁盘上感染例程的二进制不会被清除

![p20](http://drops.javaweb.org/uploads/images/f1feff36f164b6ad1ab97a064696f7a7983aa178.jpg)图16-搜索安装了Spy-Net 的标识

CyberGate植入木马自带了与感染例程相同的凭证窃取功能，并且还可以通过例程来监视Chrome和STEAM凭证。同样是继承自感染例程，CyberGate也使用了相同的反分析例程来拦截沙盒和调试工具。

除了在感染例程中看到过的功能，CyberGate还能提供给攻击者完整的监控和远程控制能力。

CyberGate 的能力包括：

*   收集详细的系统信息
*   启动并控制网络摄像头和麦克风
*   屏幕截图
*   拦截用户输入（比如：键盘、鼠标）
*   控制进程、窗口、应用、设备、磁盘、端口、TCP&UDP连接、剪贴板、注册表键值和注册值
*   控制文件系统
*   下载并执行二进制
*   通过FTP向外传输数据
*   收集已安装的安全产品信息

有趣的是，CyberGate会启动一个硬编码.vbs脚本上的cscript.exe，通过Windows Management Instrumentation (WMI)收集系统上安装的安全产品信息。这个脚本会请求系统上安装的杀毒产品和防火墙解决方案的名称和版本号，并把数据转出到一个文件中：

![p21](http://drops.javaweb.org/uploads/images/e4a99ef603fc402946fb75f671652359dafdc673.jpg)

收集到的数据会储存在磁盘上的转储文件，然后会通过HTTP或FTP发送到远程服务器上。

**3.1.2 分析 XTremeRAT**

XTremeRAT是一个可以买到的木马，经常用于监控受害者的机器。虽然有一些对政治不感冒的黑客也会使用这个木马，但是在叙利亚内战期间，更多还是政府黑客会利用这个木马来攻击反对派，在中东和北非，也有一些政治利益驱动的黑客会利用这个木马。

虽然经常会加壳，XTremeRAT本身的隐藏和维持功能是有限的。其监控功能也很直接。我们分析的XTremeRAT版本并没有使用混淆。XTremeRAT的实现是一个客户端/服务器架构，其中受感染的机器作为服务器，而CC作为客户端。

这个版本的XTremeRAT具有下面的功能：

*   记录键盘输入
*   记录前台桌面应用的名称
*   嗅探剪贴板来查找密码
*   通过HTTP下载并执行二进制，应该是安装第二阶段的木马

![p22](http://drops.javaweb.org/uploads/images/9b682b6e71baf53198e689cb6fd4d3447599076f.jpg)图17-安装 XTreme RAT 的键盘记录模块

**Xtreme RAT 的操作和键盘记录功能**

Xtreme RAT会使用安装的剪贴盘查看工具，通过键盘记录工具窗口，嗅探剪贴板上的内容。每当剪贴板内容发生变化时，这个剪贴板查看工具就会接受到窗口信息`WM_DRAWCLIPBOARD`，并访问剪贴板内容。剪贴板和键盘输入数据会转储到一个.dat文件，和配置文件（.cfg）一起放到当前用户的`[…]\Application Data\Microsoft\Windows`文件夹。文件名称都是根据XTreme RAT的配置决定的。

**XTreme RAT 的数据文件**

![p23](http://drops.javaweb.org/uploads/images/dee253b227137955e5c4eef5527331b2cd4559bb.jpg)

转储文件会通过FTP传输。XTreme RAT自带了一个预先配置好的FTP服务器凭证占位符(ftpuser/ftppass)，用于登录_ftp.ftpserver.com_，然后在运行时交换从CC发出的更新值。

XTreme RAT还会根据配置和转储文件的命名规则创建一个互斥量（比如“RJokLSZBjPERSIST”）。XTreme RAT的配置文件是从.rsrc中获取的，并且使用了RC4加密，秘钥是“CONFIG”。其他的XTreme RAT变种也曾经使用过这种算法和秘钥组合。

这个XTreme RAT变种使用了explorer.exe来容纳远程线程，从而实现特定的功能。至少有三种情况下会有线程注入。

XTreme RAT 的explorer.exe注入：

*   一个“看门狗”线程，用于恢复注册表值，找到感染例程并执行。为了增强隐蔽性，投放模块会修改感染例程的时间戳。
*   一个负责删除磁盘上XTreme RAT文件的线程
*   完整的键盘记录代码和FTP传输功能

### 3.2: 2014-2015 AlienSpy

在过去的两年中，Packrat一直在使用最新的AlienSpy木马。这个软件一开始是作为免费的RAT “[Frutas](http://www.symantec.com/connect/blogs/cross-platform-frutas-rat-builder-and-back-door)”，在2013年的一次墨西哥行动中识别到。接着经过改造，作为“Premium RAT”[Adwind](https://web.archive.org/web/20130213044621/http:/adwind.com.mx/)销售。Adwind一个许可的价格是$75，多次许可的价格是$250。然后，在2013年，AdWind更名为了[UNRECOM](http://blog.crowdstrike.com/adwind-rat-rebranding/)，并在多起针对中东的活动中检测到。

这个软件最近更多的是叫做 “AlienSpy”，研究人员发信有些针对性间谍行动使用了这个木马。在撰写报告时，这个RAT在重新加壳后，叫做JSocket。在报告中，我们统一把所有的变种都叫做“AlienSpy”。 AlienSpy 功能完善，包括记录受害者的键盘输入，通过内置麦克风记录环境声音，远程查看受害者的桌面，并可以暗自打开受害者的网络摄像头。

**3.2.1 Packrat的Alienspy 部署**

从2014年-2015年初，Packrat很喜欢在钓鱼邮件中发送AlienSpy作为附件，通常扩展名是‘.pdf.jar’。Winddows默认是不显示扩展的，所以用户只能看到是.pdf。在这一时间段中，所有的样本都采用了类似的编译方式，差别不大。有一个.jar (Java archive)文件中包含有一个叫做META-INF的文件夹和两个文件Favicon.ico和Principal.class。在执行时，Principal.class会解压“Favicon.ico”的内容（不是一个图标文件，而是一个.zip文件），并查找文件名中包含“.jar”的文件。

**Favicon.ico的内容**

![p24](http://drops.javaweb.org/uploads/images/34f81164404999b6f548c78c3e6e12af02dae056.jpg)

一旦找到正确的文件（在这里是0doc.jar），就会把这个文件投放到一个随机命名的临时文件，这个临时文件有一个常量字符串，并且调用Java来运行这个文件。

**“Favicon.ico”中的.jar文件**

![p25](http://drops.javaweb.org/uploads/images/f1db69a761d08d264a0f74365db696c512219220.jpg)

“Main.class” 使用Allatori进行了混淆，Allatori是AlienSpy使用的来自俄罗斯的一款JVM obfuscator。

首先，从“ID”文件中读取一部分RC4秘钥，再附加上一个常量字符串，然后使用完整的RC4秘钥来解密MANIFEST.MF的内容，这样就能得到真正的Adwind JAR 文件。

**MS Office文档中的AlienSpy**

在2015年，Packrat开始通过.docx文件发送AlienSpy植入。这种混淆文件的方法更加复杂，但是与先前的技术还是很类似。解压感染后的MS Word文档就能在word/embeddings目录下得到一个“oleObject1.bin”文件。打开这个Jar文件，能获得：

![p26](http://drops.javaweb.org/uploads/images/e6f1f20b259498ac7ce2450c79f01f1f68c4c72f.jpg)

与前面Packrat早期混淆AlienSpy的方法类似，一部分解密秘钥保存在一个.txt文件中。另一半是一个字符串，在解密了`abcdefghijk[a,f,j,s,u,z].class`文件后获得。

维持机制是通过在注册表中添加下面的注册值实现的：

![p27](http://drops.javaweb.org/uploads/images/fb2808f6458089bcd616074934421892742584a7.jpg)

**3.2.2 Adzok出现**

在2014年-2015年期间，Packrat还使用了Adzok-隐藏远程管理员。类似于AlienSpy的功能，这个基于Java的Adzok很显然来自玻利维亚。高级版需要$990，但是Packrat使用的似乎是免费版。这个版本的Adzok没有使用混淆，这样就可以简单的解压docx文档中的jar文件，并读取明文的配置文件。考虑到Packrat使用的其他木马都经过了混淆，我们很吃惊Packrat居然会使用这样一个木马。有可能其他RAT的稳定性。兼容性和检测问题导致Packrat使用了Adzok。

0x04 Packrat的长期钓鱼活动
===================

* * *

Packrat一直在利用钓鱼活动攻击相同的组织和个人目标。我们发现Packrat在同一时间，既使用木马也钓鱼攻击了这些个人目标。在木马活动中使用的域名和虚假身份也在钓鱼活动中再次使用了，Packrat还维护了一些专门的钓鱼网站和服务器。虽然钓鱼邮件是定期发送的，但是我们还观察到Packrat有时会发送钓鱼邮件来联系目标。

我们基本上已经系统性的了解了Packrat针对厄瓜多尔目标的行动，但是有证据表明，Packrat也在攻击邻国的目标，包括委内瑞拉。Packrat使用了邮件和社交媒体信息，以及短信来发动钓鱼信息。

这一部分主要介绍了Packrat的钓鱼活动，包括政治性主题和非政治性主题。

![p28](http://drops.javaweb.org/uploads/images/055ac18aed05cb744006fe9c682aa1a79ecd35a1.jpg)

### 4.1 非政治性主题的钓鱼内容

最常用的钓鱼技术就是伪装成来自邮箱服务或社交媒体网站的密码验证请求、非授权登录通知等等。Packrat大范围利用了邮箱提供商的模板，包括Gmail、Yahoo和Hotmail。大部分邮件都使用了西班牙语。邮件的内容也是根据目标定制的，包括他们的名称和邮箱地址。

![p29](http://drops.javaweb.org/uploads/images/e84931fc4fad6798ebd31e424353f98fb3a001b3.jpg)图18-钓鱼邮件样本

根据攻击目的，钓鱼邮件中会包含钓鱼URL或使用缩略网站。

**4.1.1 近期的非政治性钓鱼**

最近，攻击者似乎稍微修改了自己的技术。我们观察到攻击者使用了tinyurl缩略网址服务，并把钓鱼网站转移到了免费的cu9.co上。攻击者可能认为使用免费的提供商可以降低成本，并增加灵活性。

近期出现的钓鱼URL和缩略网址：

*   tinyurl.com/nww83ov Yields: main-latam-soporte-widget-local.cu9[dot]co

**4.1.2 非政治性钓鱼短信**

大量Packrat的目标还接收到了钓鱼短信。这些钓鱼短信使用了钓鱼邮件类似的语言，有时候还会使用相同的缩略URL。有时候，攻击者还会警告用户如果不点链接，他们的账户就会停用。我们在一次案例中发现了包含有不正常邮箱地址的信息。

![p30](http://drops.javaweb.org/uploads/images/144c5e89e017c6866efed474e861c673302e316e.jpg)图19-非政治主题的钓鱼短信

### 4.2 政治性主题的钓鱼活动

我们观察到有大量的邮件和信息中包含有政治性内容。Packrat采取了两种攻击方式。第一种方式：创办虚假的政治和媒体组织。第二种方式：伪装成著名的团体和个人。攻击者经常会利用相关的新闻事件作为短信和邮件内容。大部分内容都与犯罪派有关。

虽然，大部分钓鱼邮件都是伪装成来自邮箱服务或社交媒体网站，但是在特定情况下，Packrat会伪装成高级别目标使用的邮箱服务，比如厄瓜多尔国民议会。

**4.2.1 攻击厄瓜多尔议会**

Packrat曾经伪装成厄瓜多尔国民议会的邮箱门户发动了钓鱼攻击。这个恶意网站会诱骗受害者输入他们的邮箱凭证。

*   asambleanacional-gob-ec.cu9.co

合法域名是：

*   http://mail.asambleanacional.gob.ec/

**4.2.2 一个典型的凭证窃取页面**

无论诱饵是什么，钓鱼信息中的链接（通常是简短网址）通常会把受害者引导至一个类似于免费邮箱提供商的域名。在2015年夏天，Packrat利用了一个类似谷歌的域名，当然他们还利用了其他的一些域名：

*   mgoogle.us

在攻击活动中，mgoogle.us伪装成了一个西班牙语的谷歌登录界面。

![p31](http://drops.javaweb.org/uploads/images/b75b77efa7450d9a19795c49bee6a001fd7316c0.jpg)图20-mgoogle.us伪装成了一个西班牙语的谷歌登录界面

一旦受害者输入自己的登录信息，他们就会看到一个西班牙语的信息，“确认”他们的gmail账号已经解锁，并谢谢“选择我们”。

![p32](http://drops.javaweb.org/uploads/images/a632d44fa19ee4e5970b0f6a2816a62d1ddab21b.jpg)图21-西班牙语的信息，“确认”他们的gmail账号已经解锁

在其他情况下，Packrat会发送“确认”邮件到受害者的邮箱，恭喜他们“验证成功”。我们发现，在一些情况下，攻击者在没有入侵钓鱼到的账号前，就会发送这封邮件。

虽然这些钓鱼活动利用了不同的工具来收集凭证，但是我们发现Packrat重复使用了合法的formmail.com服务来接受钓鱼获取到的凭证。

### 4.3 一个钓鱼/木马网站样本

攻击者控制着大范围的域名来钓鱼或传播木马。在这一部分，我们分析了这些基础设施的特点。比如，钓鱼页面mgoogle.us就会解析到好几个IP地址，包括：

![p33](http://drops.javaweb.org/uploads/images/6eb3ed2c273da35ff65bf8e9db83db548af90cf0.jpg)

在这些IP中，第一个IP (198.12.150.249)非常有意思。我们发现这个IP地址上还托管了一些主题类似的可疑域名。在这些域名中，有的伪装成了登录页面和更新页面（比如sopporte-gmail.com 或 login-office365.com），其他的一些还伪装成了政治网站。

**WHOIS**

![p34](http://drops.javaweb.org/uploads/images/f9d6d3c4fb095d91aed0daf38d8faabcad23cc8a.jpg)

这个网站的注册人是[enripintos123@outlook.es](https://citizenlab.org/2015/12/packrat-report/enripintos123@outlook.es)，[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)有这些网站中，除了两个例外，其他的都看起来像是登录页或服务更新，比如Android和Java。而这两个例外就是lavozamericana.info 和pancaliente.info。这两个域名是与另外的钓鱼域名同时注册的。

**4.3.1 虚假的新闻网站**

网站 ecuadorenvivo.com是一个合法的新闻网站，但是攻击者控制了一个类似的域名ecuadorenvivo.co。Packrat利用这个虚假的域名像目标发送邮件，在这些邮件中会包含有木马附件、或恶意网站的链接。然后通过插件将木马下载到受害者的设备上。

一名Twitter用户在2015年5月就发现了一个虚假的插件通知。

![p35](http://drops.javaweb.org/uploads/images/6b0d8d265ed940e88bc9bf54405a13219625fb12.jpg)图22-虚假的插件通知

类似的，focusecuador.net也是一个合法的新闻网站，但是攻击者控制了类似的域名focusecuador.tk，这个网站会利用虚假的弹窗来传播木马。通过检查focusecuador.tk的IP(193.105.134.27)，我们又发现了很多相似的域名。

**4.3.2 虚假的新闻组织：美国之声？**

第二个很有意思的域名是 lavozamericana.info，这个域名现在已经不活动了。但是，我们发现了一个Twitter账户和一些推文似乎是想要让这个域名看起来更合法一点。

*   https://twitter.com/voz_americana

有意思的是，这个虚假的twitter身份至少也成功过，下面的一些关注用户就可能上当了。虽然这个网站现在已经不活动了，但是Google cache表明这个网站曾经是一个钓鱼页面。

![p36](http://drops.javaweb.org/uploads/images/496aca7f1ec361a0755c74c11f5e4920167df165.jpg)图23-Google cache表明在这个网站上曾就有一个钓鱼页

**4.3.3 虚假的反对派活动**

我们发现有很多目标都接收到了来自movimientoanticorreista.com的邮件和信息，包括在前面提到的攻击活动1中。在利用木马攻击厄瓜多尔记者的活动中，攻击者也用到了这个域名。我们发现，与这个域名相关的木马信息，都是由[movimiento.anti.correista@gmail.com](mailto:movimiento.anti.correista@gmail.com)发送的

**另一封反科雷亚活动邮件**

![p37](http://drops.javaweb.org/uploads/images/9d85b95dd39972e7e4444fc7bbb7529380f61b42.jpg)

### 4.4 了解行动范围的一个窗口

通过Packrat的一些活动，我们更系统性的了解了攻击活动的范围。在2015年3月期间，我们观察到Packrat会定期使用相同的bit.ly链接来进行活动。

*   http://bit.ly/1wl3YE2

这个链接是在2014年10月30日创建的。通过检查这个bit.ly链接的统计数据，我们大致了解了这次行动的规模、时间以及点击链接的地理位置分布。

![p38](http://drops.javaweb.org/uploads/images/8da6c128c5c61c25f3c2639142b455994b502242.jpg)图25-行动的规模、时间以及点击链接的地理位置分布

大部分链接是在厄瓜多尔境内点击的，其他的还有阿根廷、德国、美国、西班牙、乌拉圭和委内瑞拉。其中没有巴西这一点并不意外，因为攻击者如果要攻击巴西，会使用葡萄牙语的网站。借此我们就能够间接地了解Packrat都会攻击哪里的目标。

大部分点击（322次）是直接的点击链接，而不是通过分享点击的。这个bitly链接的点击大部分都不在社交网站上，因为Packrat没有使用社交媒体来传播。

### 4.5 注意：在众多的钓鱼活动中，并不是互相都有联系的

通过这次调查，我们发现了一些钓鱼活动利用西班牙语的钓鱼信息攻击了Packrat曾经攻击过的一些个人目标，但是我们有各种理由相信，这些活动与Packrat没有联系。其中一次很引人注意的活动利用了**gmail.com.msg07.xyz**，并伪装成了Gmail的账户通知。通常，这类信息会显示为来自[no-responder@supportgmai1.com](mailto:no-responder@supportgmai1.com)这样的地址。有时候，一些目标每隔几周就会收到这样的信息。

0x05 可能是为了欺骗目标
==============

* * *

Packrat的域名并不都是为了传播木马，或盗取受害者的密码。有几个域名伪装成了新闻网站的样子，上面的一些政治性内容也是原创的。至少有两个网站是为了针对委内瑞拉，有1个是为了针对厄瓜多尔。

我们没有发现任何证据能证明这三个网站会传播木马或钓鱼。可能这些网站还有其他用途。

### 5.1 反查韦斯-非常怪异的pancaliente.info

注意：在我们公布这份报告前**Pancaliente.info**已经下线了，但是可以通过Google cache查看。第二个域名chavistas24.com仍然在线。

在198.12.150.249上，最有意思的一个域名就是pancaliente.info。打眼一看，这是一个专注于委内瑞拉的新闻和信息网站。不同于这个IP上的其他网站，我们在这个网站上发现了很多原创的新闻内容 。

无论如何，这个网站与其他域名有很多联系。虽然这个域名的注册信息被隐藏的，但是其他的钓鱼网站使用了相同的注册邮箱。

![p39](http://drops.javaweb.org/uploads/images/eadeb928ce9a2242f401b5ab6d2ff958b5f0fa3d.jpg)

虽然pancaliente.info 的WHOIS信息受到保护，但是还可以验证其注册。

![p40](http://drops.javaweb.org/uploads/images/67a2ad0ad1e8d946d038c7dae8375b50373b5642.jpg)图26-在2015年10月出现的 Pan caliente 网站

通过更细致的检查，我们发现有网站的内容大都是为了吸引反对查韦斯党派的委内瑞拉人，无论是国内还是国外。网站上的有些报道很有意思，因为他们只介绍说这些是个人档案，但是没有透露这些文档的来源。

在其他的一些例子中，这个网站还报道了一些所谓的“泄露”档案。其中的一些内容都与PSUV相关。很多报道中都涉及到了委内瑞拉境内犯罪海外政体的外籍专家，尤其是离散在西班牙的犹太人。

PanCaliente也在其他地方有引用，比如Sidesahre上的一份泄密档案。其他的在线新闻网站也引用过他们的报道。

虽然看似有很多内容，但是PanCaliente的文章中没有署名。虽然这个网站与一个Twitter账户([https://twitter.com/pancalienteve](https://twitter.com/pancalienteve))的活动很密切，但是相关的Facebook账户([https://twitter.com/pancalienteve](https://twitter.com/pancalienteve))却很少。通过WayBack Machine就能明白，PanCaliente最近才开始活跃。

![p41](http://drops.javaweb.org/uploads/images/7e992963cd9fae8ef2d30a417818da5a38e5e268.jpg)图27-PanCaliente在Wayback Machine 上的显示

有趣的是，这个网站上最先公布的一些报道是当这个网站还叫做“Venezuela365.com”的时候编写的。

![p42](http://drops.javaweb.org/uploads/images/709a95939bf55bf4d0d319a87c6f5f632df4588d.jpg)图28-网站早期的标志，还可以在网站的目录结构中看到

![p43](http://drops.javaweb.org/uploads/images/307e35ad4605f0d6a1b780749ffba90229c8c002.jpg)图29-现在的PanCaliente 标志

我们还可以在网上看到这个网站更换标志的信息。另外，有一篇报道中还是引用了网站 venezuela365。有趣的是，第一份报道中还提到了一些“秘密”信息，包括重新制作发票，并没有解释其来源。

*   http://pancaliente[.]info/los-negocios-secretos-de-leocenis-garcia-y-gonzalo-tirado/

这个页面源中还包括有venezuela365.com

*   “http://venezuela365.com/wp-content/uploads/2014/10/tirado-g-300×169.jpg“

现在，一个名称相同的图像出现在了pancaliente.info的相同目录下。

venezuela365.com域名是DomainsByProxy注册的，但是先前的WHOIS信息中显示注册人是Sistekon Corp。Sistekon Corporation现在似乎不用了，但是关于Sistekon Corporation的信息在[archive.org](http://web.archive.org/web/20130719001853/http://www.sistekon.com/)上还有，这家公司主要是开发IT软件和销售安全解决方案。考虑到这个域名是在2013年过期的，但是在2014年重新注册，而pancaliente.info几乎在同一时间注册，这两者之间的联系可能是巧合。

我们没有发现有证据能表明PanCaliente或venezuela365曾经用于传播木马或执行钓鱼活动。

### 5.2 亲查韦斯:Chavistas 24.com

域名 chavistas24.com似乎是一个支持委内瑞拉前总统查韦斯的网站，在这上面有很多支持查韦斯党派的内容。

![p44](http://drops.javaweb.org/uploads/images/6b0685050386fcc8ea13877f025a5896f4067663.jpg)图30-Chavistas24.com上的图片

Chavistas24.com 同样有相关的Twitter账号来发送推文，主要是引用了网站上发表的文章。

*   https://twitter.com/chavistas24/

![p45](http://drops.javaweb.org/uploads/images/e509468af1a0364ccd0bec5f8ddfb6659fd49a54.jpg)图31-Chavistas 24的Twitter

我们没有发现有证据能表明chavistas24.com曾经用于传播木马或执行钓鱼活动。

### 5.3 搜索警察?

Packrat似乎对心怀不满的厄瓜多尔警察很感兴趣，他们为此还创办了一个-Los Desvinculados网站(justicia-desvinculados.com)和社交媒体身份。这个网站中也有登录板块，有关厄瓜多尔政府的新闻和报道。

此前，厄瓜多尔警方就曾经抗议福利太差，他们也是目前对厄瓜多尔总统科雷亚威胁最大的一股力量。

![p46](http://drops.javaweb.org/uploads/images/4dbccda25ae8df31bdba5a9f7e10e147d622da3c.jpg)图23-Los Desvinculados网站

下面是相关的twitter账号 (twitter.com/justdesvincula2)。

![p47](http://drops.javaweb.org/uploads/images/eb50b8d2a02b3b0a5efc0206ee1790d839c9967d.jpg)图33-Desvinculados Twitter 页面

和前两次活动一样，我们没有发现有证据能表明Justicia Desvinculados曾经用于传播木马或执行钓鱼活动。

0x06 归属判断面临的挑战
==============

* * *

本文中提出的证据表明，Packrat是一个有组织，有长期执行攻击活动能力，攻击目标有明显地区特征的小组。那么Packrat到底是谁呢？在这里，我们提出了两种假设。

### 6.1 假设1: Packrat 有国家资助

**6.1.2 目标名单**

遭到Packrat攻击者都是一些有影响力的人物，这些人的活动能对国内和地区性政治造成影响。在厄瓜多尔和阿根廷，Packrat的攻击目标有著名的评论家和独立记者。有趣的是，Packrat还攻击了厄瓜多尔议会和政府部门。数据显示，Packrat经常会攻击与反对派相关的各种目标。

在其他的活动中，我们发现了一些政治性很强的钓鱼、木马网站、邮件和信息。Packrat创办了虚假的政治组织，然后利用相关的身份和网站来发动钓鱼攻击或传播木马。这些网站似乎是为了吸引评论家和某些厄瓜多尔和委内瑞拉的政府成员。我们认为其他国家的一些目标也遭到了信息，比如巴西，但是我们并不清楚他们是谁。

还有一些目标是该地区的情报或安全部门比较感兴趣的。而这些活动的赞助者可能对反对军力量很感兴趣。

**6.1.3 传播错误信息的活动动机**

我们发现了大量的虚假网站都涉及到了政治问题，但是很显然是为了传播木马。虽然有些网站与木马网站共用了相同注册信息，但是通过网站上的内容就能区别它们的不同，并且这些网站上没有恶意文件或钓鱼页面。

对于这些网站，有三种可能的解释。首先，这些网站是为了让那些虚假的组织看起来更可信，从而可以传播错误信息。第二，这些网站可能是蜜罐，用来吸引或操控目标，然后进行木马攻击。最后，这些网站可能是为了收集我们尚不清楚的行动信息。

我们并不清楚哪个国家会对这些行动感兴趣，并支持这些活动。

**6.1.4 支付能力**

托管、注册和维护这些基础设施达七年的成本肯定不低。而创建和维护虚假网站所需要的人力也是成本，尤其是对于那些有原创内容的网站，比如PanCaliente。最后，如此大范围和定制化的攻击活动也需要额外的人力。

从这些成本来看，Packrat一定有充足的资源，或者是有资助者来帮他们付钱。我们还没有发现任何证据能表明他们在攻击工业、商业或金融部门。考虑到他们的活动成本，我们很难想象，除了某个国家，没有其他人会既想要这些信息，还愿意给他们付钱。

**6.1.5 能证明Packrat“高枕无忧”的线索**

在2015年初，首次有报告公布了Packrat攻击了Nisman和阿根廷，并暴露了他们的基础设施。尽管如此，仍然有大量的基础设施保持在线。从项目角度来看，这样是说得通的。如果Packrat成功入侵了目标，而关掉这些基础设施就会导致他们失去对目标的控制。Packrat就必须要重新感染目标，连接到新的主机上。这一过程不仅会浪费时间，并且不容易成功，甚至被检测到。

如果Packrat害怕处罚，那么他们很自然地就会撤掉暴露的服务器。因为如果执法部门掌握了他们的服务器，那么就可能会追踪到他们。

事实上，这些服务器还在线，这就说明Packrat只担心自己的行动还能不能继续，并不担心政府的追查。我们猜测，他们可能会受到当地政府的保护。

虽然没有决定性的证据，但是从他们敢威胁Citizen Lab的研究人员来看，他们很自信自己不会被处罚。从他们的表现来看，Citizen Lab的研究员并不是第一个打扰到他们的分析人员。

**6.1.6 国家参与的两种方案**

在这一部分，我们提出了两种可能的国家支持情况。我们会用数据来说明每种情况的可能性。

**方案1:赞助者只有一个国家**

根据我们的发现，这里有几种可能的解释。有可能Packrat在为一个情报部门工作，从他们的活动中也能看出这家情报机构的目标。这家情报机构可能监视着很多团体，包括他们的对手，比如别国政府。

最明显的就是ALBA（美洲玻璃瓦联盟）国家和以及近期的阿根廷，这些国家的领导人达成了政治联盟，虽然，最近阿根廷大选的总统反对这种关系。同时，厄瓜多尔和委内瑞拉政府的关系也很紧密。

有人可能认为，Packrat攻击了厄瓜多尔的某些政府部门就是决定性的证据，能证明厄瓜多尔官方与Packrat有牵连。但是，厄瓜多尔议会和其他政府目标还不能证明厄瓜多尔政府就是赞助者，但是也不能排除这种可能。

**方案2: 赞助者不只有一个国家**

 地区性目标的范围和多样性表明Packrat可能在代表多个政府攻击敌对力量。例如，Packrat可能有多名客户，并且使用了相同的基础设施来进行活动。

### 6.2 假设2: Packrat 没有国家赞助

虽然，上面的一些证据能表明有政府在支持Packrat，但是，Packrat的其他活动特征并不符合这种猜测。在这一部分，我们会列出一些重要的证据：比如Packrat的技术程度不高。我们评估了这些证据，并注意到Packrat也可能没有国家的赞助。

**6.2.1 缺少技术性很强的工具**

Packrat使用的木马主要是能购买到的现有RAT木马，并不是自己开发的，也不是专门面向政府销售的高级木马。另外，这些攻击者也不会利用漏洞来投放木马。比如，有些诱饵文档还需要受害者双击文档中的图标。这样的操作太麻烦了，还有可能会造成攻击失败。而政府支持的攻击者可能会利用更高级的木马和漏洞。

但是，也并不是说所有与政府相关的攻击小组就一定会利用高级木马或漏洞。

虽然，仅仅通过他们使用的商用木马和没有利用过漏洞，我们还无法得出结论。不过，确实有一点值得注意：Packrat通过混淆，能有效的绕过检测，并隐藏自己的身份。

**6.2.2: 方案:没有国家赞助的小组**

我们无法回避的一个可能性就是Packrat是犯罪组织，并没有国家赞助。从理论上来说，这样的攻击小组可能是反对派的支持者，或有其他相关的利益。在南美洲，也有很多强大的非政府团体和帮派，他们绝对有财力来支撑这些行动。无论如何，考虑到Packrat的攻击目标，我们不理解为什么非法团体会对这些人感兴趣。

还有另一种可能，可能一个有政治野心的非政府团体在负责Packrat。这样的团体就会对政治联盟和政府非常感兴趣。

### 6.3 到底哪种猜测是对的呢？

最后，我们认为报告中的数据还不足以判断到底哪种猜测是对的。但是，能从中Packrat的活动中受益的一定是该地区的一些政府。

0x07 总结
=======

* * *

在这篇报告中，我们介绍了一次长达七年的活动，这一攻击活动的目标是几个拉美国家。虽然在拉美有很多著名的攻击小组，但是Packrat最显著的特点就是经常攻击政治人物、记者等。Packrat还具备有执行长期活动的能力，能不受媒体报道的影响。

Packrat最突出的一点就是，利用了技术不是多强的木马，维持了多年的活动。从技术的角度看，他们主要依靠的是可以购买到的现有RAT，然后再通过加壳来绕过检测。他们还通过创办虚假的组织，来传播木马从而感染目标。

即使基础设施暴露，Packrat也没有撤下自己的服务器和域名。这就表明，Packrat非常重视自己的行动。

虽然，我们无法确定Packrat的幕后操纵者，但是我们希望通过曝光他们的活动，鼓励有更多的人继续研究下去。

[https://citizenlab.org/2015/12/packrat-report/](https://citizenlab.org/2015/12/packrat-report/)

0x08 附录
=======

* * *

附录B 木马样本

![p48](http://drops.javaweb.org/uploads/images/208b8e65c21a1fb19db1007a2775733efd1abac6.jpg)

![p49](http://drops.javaweb.org/uploads/images/53c3e0064be4667c441f09442c969c428e474f8a.jpg)

附录C木马配置

CyberGate RAT配置

![p50](http://drops.javaweb.org/uploads/images/fcdcd81e2399e8beec63ec9ec4991c297add38fa.jpg)

Xtreme RAT 配置

![p51](http://drops.javaweb.org/uploads/images/bbd94c2d23ecb41ac96f4ed68fe8a3c904190c81.jpg)

Adzok 配置

![p52](http://drops.javaweb.org/uploads/images/46d219f9d450b48eede03a241c791af0a19a9e62.jpg)

Adwind 变种配置

![p53](http://drops.javaweb.org/uploads/images/20ca08738cc8bf47f31a3185e1e769ac221bc08e.jpg)

附录D：恶意域名

解析到198.12.150.249的域名

![p54](http://drops.javaweb.org/uploads/images/56ed697d4869899cc87846ff06d0918a910742fd.jpg)

![p55](http://drops.javaweb.org/uploads/images/bcb095107e8732a3fff7e02df6b86971b777873b.jpg)

解析到193.105.134.27的域名

![p56](http://drops.javaweb.org/uploads/images/d6328ea47f96d4208914d5ee08639b05d4349f0b.jpg)

[enripintos123@outlook.es](mailto:enripintos123@outlook.es)注册的域名

![57](http://drops.javaweb.org/uploads/images/40f4ab848bcaa0e6c8fb77294f991ae1a064ddca.jpg)