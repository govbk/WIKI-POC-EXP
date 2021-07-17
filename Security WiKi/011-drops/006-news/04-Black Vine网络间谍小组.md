# Black Vine网络间谍小组

[http://www.symantec.com/content/en/us/enterprise/media/security_response/whitepapers/the-black-vine-cyberespionage-group.pdf](http://www.symantec.com/content/en/us/enterprise/media/security_response/whitepapers/the-black-vine-cyberespionage-group.pdf)

0x00 综述
=======

* * *

在2014年初，Anthem遭到黑客袭击，泄露了8000万份医疗记录。媒体在2015年2月曝光了这次入侵事件，而发动攻击的网络间谍小组很可能就是Black Vine。

Anthem并不是Black Vine的唯一目标。Black Vine从2012年开始活动，其攻击目标主要集中在几个领域中，包括航空航天业，能源产业和医疗行业。这个小组使用的武器有通过Elderwood框架传播的0-day漏洞，并且还利用过Hidden Lynx等小组同时使用过的一些漏洞。

Black Vine通常会利用水坑攻击技术来入侵一些目标感兴趣的网站，然后使用0-day漏洞来入侵目标的计算机。如果漏洞利用成功，攻击者就会投放他们自己开发的木马：Hurix、Sakurel（检测为Trojan.Sakurel）和Mivast（检测为Backdoor.Mivast）。这些威胁能够开启受害者计算机上的后门，从而允许攻击者窃取有价值的信息。

根据我们的分析以及开源数据的支持，我们认为Black Vine的成员可能与北京某IT公司有关联。

0x01 介绍
=======

* * *

2014年1月26日，医疗公司Anthem的一名系统管理员发现，他们的账户遭到了黑客入侵，访问了内部数据库中的敏感数据。虽然很多请求都是从这个账户发起的，但是系统管理员发现是其他人在执行这些请求。很快，Anthem就意识到，他们遭到了网络攻击。这次攻击事件是今天最严重的医疗数据失窃事件，丢失了8000万份记录。Symantec认为实施这次攻击活动是Black Vine小组。

2015年2月，媒体曝光了这次事件，这是公众了解到的第二起针对美国医疗企业的攻击活动。Black Vine发动的这次攻击活动是2015年受关注程度最高的事件之一。但是，这只是Black Vine的一次攻击活动，他们也在攻击其他的几个行业。

从2012年起，Black Vine开始针对性地攻击几个行业，包括能源产业，航空航天业和医疗行业。他们使用了自己开发的木马、0-day漏洞和其他的一些TTP，这是一个有组织有能力的攻击小组。

此次研究记录了，从2012年至今，Black Vine进行的所有活动。通过观察他们的活动时间线，不仅仅能了解他们的历史行动，还能够观察到他们的发展历程。我们希望这份报告能够帮助组织更好地理解Black Vine，包括他们的TTP，动机和使用的木马，以便更有效地防御这一威胁。

0x02 关键发现
=========

* * *

通过研究Black Vine的活动，Symantec发现了下面的信息：

*   Black Vine攻击了多个行业，包括能源业，航空航天业和医疗行业
*   Black Vine水坑攻击了一些与能源和航空航天相关的合法网站，从而利用木马感染网站的访客
*   Black Vine似乎掌握了Elderwood框架，他们利用这个框架在威胁小组之间分享木马
*   Black Vine使用了自己开发的木马，并且有充足的资源来定期更新和修改木马，从而绕过检测

这些发现让我们相信，Black Vine与其他的网络间谍小组有合作。Black Vine资金充足，组织性强，包括多名小组成员，其中的一些成员与北京某IT公司有关联。

0x03 目标
=======

* * *

在调查Black Vine期间，Symantec确定了大量遭到攻击的企业。由于Black Vine的攻击途径，仅仅依靠攻击数据可能会误导你。Black Vine经常会利用水坑攻击入侵合法网站，从而强制网站感染其访客。因此，如果只是分析遭到入侵的计算机是无法准确地反映Black Vine的攻击目的。相反，这样能反映出哪些行业的感染率是最高的。

根据Symante遥测数据的分析，Black Vine攻击过下面的这些产业：

*   航空航天业
*   医疗行业
*   能源业（天然气和电泵制造商）
*   军事与防御部门
*   金融业
*   农业
*   科技产业

为了进一步判断Black Vine的目标产业，Symantec评估了持有受影响网站的企业。Symantec还调查了Black Vine发动的一些水坑攻击活动。在调查了大量的攻击目标后，Symantec认为Black Vine的主要目标产业是航空航天业和医疗业。很可能，遭到感染的其他行业是次级目标。

![p1](http://drops.javaweb.org/uploads/images/d0a199cfff5513c55f66bc3db548df5d21e1d5f7.jpg)图1-Black Vine的受害者分布

根据受害者计算机的IP地址位置，我们确定Black Vine的攻击目标主要分布在几个地区。主要的感染地区是美国，其次是中国、加拿大、意大利、丹麦和印度。

0x04 攻击者的资源
===========

* * *

攻击者的资源

Black Vine似乎掌握有大量的资源，能允许他们在同一时间发动多次攻击。这些资源包括自定义木马的开发、0-day漏洞和攻击者持有的基础设施。这样的资金和资源只能由公共实体或私有组织提供。

我们分析发现，Black Vine主要在活动中使用了3种木马变种，分别是Hurix、Sakurel（检测为Trojan.Sakurel）和Mivast（检测为Backdoor.Mivast）。我们认为这些木马的作者都是相同的，并且使用了相同的代码和资源。例如，Hurix和Sakurel具有下面的这些相似点：

*   Hurix和Sakurel都会收集目标的计算机名称，并使用了相同的算法来加密数据
*   这个算法使用了除法和加法，静态变量是1Ah和61h。下面是每个威胁中算法的位置：
*   Hurix:402A75h
*   Sakurel:1000147Bh
*   网络通讯参数中有相似的数据和参数：
*   这两个变种都使用了参数“type”，初始值是0
*   这两个变种都使用了一个包含相同数据的参数，如下：
*   Hurix: cookie=iztkctcebtgbbyf-2135928347 (其中“cookie” 是参数， “iztkctcebtgbbyf” 是加密的计算机名，“-2135928347” 是十进制的硬盘序列号)
*   Sakurel: imageid=iztkctcebtgbbyf-2135928347 (其中 “imageid”是参数， “iztkctcebtgbbyf”是加密的计算机名， “-2135928347”是十进制的硬盘序列号)

所有这三个变种都具备下面的功能：

*   打开后门
*   执行文件和命令
*   删除、修改并创建注册表键值
*   收集和传输关于受害者计算机的信息

我们在CC通讯请求中，发现了下面的URL特征：

*   photoid=
*   resid=
*   imageid=
*   vid=

例如：

*   www.polarroute.com/newimage.asp/imageid=oonftwwtwwtzx1755999261&type=0&resid=139890
*   www.polarroute.com/viewphoto.asp/resid=126546&photoid=oonftwwtwwtzx1755999261

在大多数情况下，木马会伪装成科技相关的应用。用于伪装木马的主题包括Media Center，VPN和 Citrix 应用。CC服务器或域名也会像木马一样进行伪装。例如，有一个Sakurel样本就命名为了MediaCenter.exe (MD5:1240fbbabd76110a8fC&C9803e0c3ccfb) 。与木马通讯的CC域名就使用了一个Citrix主题：citrix.vipreclod.com 。

另外，大多数木马样本的数字签名都是由韩国软件公司DTOPTOOLZ Co或软件开发商MICRO DIGITAL INC签署的。Symantec已经观察到，DTOPTOOLZ Co证书还用于签名了一个广告软件，而这起恶意广告活动并没有Black Vine的参与。图2和图3中是详细的证书信息。

![p2](http://drops.javaweb.org/uploads/images/4edafaf7fea9d0b6a0c1b6ff3f80b2448ae60685.jpg)图2-DTOPTOOLZ Co数字证书

![p3](http://drops.javaweb.org/uploads/images/8de86aa7183cb17751cda470fb38994baa581bb5.jpg)图3-MICRO DIGITAL INC数字签名

0x05 活动
=======

* * *

Symantec发现Black Vine的活动最早可以追溯到2012年。从那时开始，Symantec就观察到Black Vine多次发动了针对性攻击活动。在我们调查过的所有活动中，我们发现Black Vine的主要目的是入侵目标的基础设施并窃取信息。

0x06 能源业
========

* * *

2012年12月，安全研究员Eric Romang发表了一篇博客称，燃气涡轮制造商Capstone Turbine遭到了水坑攻击。Symantec通过调查，也证实了Romang的发现，Capstone Turbine的合法域名capstoneturbine.com上放置了一个0-day exploit，实际是Microsoft Internet Explorer ‘CDwnBindInfo’ Use-After-Free 远程代码执行漏洞 (CVE-2012-4792)。当时，只要用户使用漏洞版本的IE浏览器访问Capstone的网站，就会被Sakurel的有效载荷入侵。Sakurel能够允许Black Vine访问受害者的计算机和信息。如前面提到的，这个Sakurel样本使用了MICRO DIGITAL INC颁发的数字签名。

相关的Sakurel样本信息如下：

*   MD5 哈希: 61fe6f4cb2c54511f0804b1417ab3bd2
*   C&C 域名: web.viprclod.com
*   漏洞: CVE-2012-4792
*   编译时间: 12月8日, 2012 07:54:44

另外，攻击中利用的CC域名web.viprclod.com伪装了合法域名VipeCloud.com。这个合法的网站属于VipeCloud，这个网站提供的是销售和营销服务。这一点可能是巧合，也可能是在其他未知的攻击活动中重复使用了相同的基础设施。但是，这个域名是在2012年12月10日注册的，正好在用于攻击能源业的Sakurel样本编译完的两天后。无论如何，这个CC服务器的主题不同于在能源业攻击活动中使用的主题。

攻击者用下面的信息在2012年12月10日注册了CC域名viprclod.com：

*   域名： VIPRECLOD.COM
*   创建时间： 10-12-12
*   过期时间：10-12-13
*   最后更新时间： 10-12-12
*   管理信息:
*   **moon,today**[todaymoon321@gmail.com](mailto:todaymoon321@gmail.com)
*   xingfudadao
*   sitemo, ai no 236963
*   Tanzania

Capstone Turbine是美国的一家燃气涡轮机制造商，这家企业专攻微型涡轮机、以及加热冷却共生系统。可能是他们在能源和动力技术上的研究和开发专利导致他们成为了攻击目标。

在2012年12月24日，Black Vine再次攻击了能源和技术制造厂。但是具体的攻击情况无法公布，在这次攻击活动中还使用了Sakurel。结合Black Vine发动的多起0-day攻击，以及以涡轮制造商为攻击目标，很可能Black Vine当时的主要目标是能源相关的科学技术。

0x07 航空航天业
==========

* * *

在2013年中期，一篇第三方博客记录了攻击活动中如何利用Citrix诱饵投放Hurix木马来攻击航空公司。这篇博客中写到，攻击中使用的木马是通过钓鱼邮件发送给航空公司的特定员工。在这些邮件中会包括一个URL，用于重定向用户下载Hurix。不过，Symantec无法访问必要的数据来验证博客中说的对不对。我们只是为了记录目的，概括性的总结这次攻击活动。

在2014年2月，Black Vine入侵了欧洲航空公司的网站。攻击者控制了这家公司的域名，并利用其网站主页来入侵网站的访客。之所以利用水坑攻击可能是为了更大范围的感染航空产业里的目标。与2012年针对能源产业的攻击活动类似，攻击者利用了一个新的0-day bug，Microsoft Internet Explorer Use-After-Free 远程代码执行漏洞 (CVE-2014-0322)。这次攻击活动的有效载荷是一个更新版的Sakurel。具体的Sakurel样本信息如下：

*   **MD5 哈希**:c869c75ed1998294af3c676bdbd56851
*   **C&C 域名**:oa.ameteksen.com
*   **漏洞**:CVE-2014-0322
*   **编译时间**:**7月16日**,**2013 03:44:36**

一旦感染了受害者，Sakurel就会通过下面的请求联系CC域名oa.ameteksen.com：

`GET /script.asp?resid=93324828&nmsg=del&photoid=iztkctcebtgbbyf-2135928347 HTTP/1.1`

C&C 域名的注册信息如下：

*   域名:AMETEKSEN.COM
*   注册人URL:http://www.godaddy.com
*   更新日期:2013-10-15 05:15:20
*   创建日期:2013-10-15 05:06:32
*   注册过期日期:2014-10-15 05:06:32
*   注册人:GoDaddy.com, LLC
*   注册国家:China
*   姓名:ghregjr ngrjekg
*   街道:kwjfhrjkgh
*   市:rjekteyu
*   省: 
*   邮政编码:37182
*   国家:China
*   电话号码:+86.3781263856
*   邮箱:dobbin.pacheco@aol.com

Black Vine创建域名ameteksen.com是为了伪装成合法网站ameteksensors.com 或ametek.com，这两个合法域名属于航天和国防承包商Ametek。

在我们调查Black Vine针对航空业的攻击活动时，Symantec发现这个小组使用了一些非常规战术。在受害者的计算机上运行了Sakurel之后，木马会更改受害者的主机文件。通常，Windows操作系统会使用host文件来映射域名和IP地址，而不是通过DNS查询。Black Vine修改了host文件，在其中添加了静态项目，从而让合法域名解析到他们的合法IP上。

这一点很不常见，因为默认的DNS请求就是这样映射的。一般来说，当攻击者想要把合法域名映射到恶意基础设施时会这样做，但是，修改主机文件会让目标意识到自己遭到了入侵。

Black Vine在攻击航空公司时使用的Sakurel样本会修改主机文件，重定向图1中的合法URL和IP地址。

表1-添加到主机文件中的域名和IP

![p4](http://drops.javaweb.org/uploads/images/2809fb2d94559e9762bfc9a407bb4e771f3398e0.jpg)

在调查这次攻击事件时，我们发现了大量与航空领域相关的域名，这些域名都与Black Vine有关联。在2014年1月末和2月中期，攻击者使用了域名www.savmpet.com 和 gifas. asso.net。另外，Symantec和多家第三方来源此前就报道过有针对性攻击利用这些域名来攻击航空产业的目标。

恶意域名gifas.assso.net很可能伪装的是欧洲航空航天工业协会的合法域名gifas.asso.fr。在调查期间，gifas.asso.net域名被用于传播木马，引用页是www.savmpet .com。

至于Black Vine发动了多少起针对航空行业的攻击活动，我们并不清楚。但是，Symantec认为有多起针对性活动是在2014年初到中期之间发动的。从攻击者使用的0-day漏洞和自定义木马来看，Black Vine一定是资金充足的组织性小组。

0x08 医疗业
========

* * *

在2015年2月，媒体曝光了一起针对医疗行业的网络间谍活动。这次入侵活动攻击了医疗公司Anthem，导致泄漏了8000万份医疗记录。最初的报告中称，Anthem是在2015年1月26日发现了这次入侵时间，当时系统管理员发现有人利用他的凭证请求了数据库，而他并不知情。很快，Anthem就反应过来自己遭到了攻击，而这次攻击活动可能是从2014年5月开始的。根据我们调查分析的样本，Symantec识别出在这次攻击活动中使用的木马变种是Mivast。其他的第三方厂商也说攻击Anthem的是Mivast木马。

类似于Black Vine的其他攻击活动，Mivast也是使用了DTOPTOOLZ Co的数字签名。并且，在这次入侵活动中，攻击者使用了多个域名来伪装成医疗和科技相关的组织。表2中列出了Black Vine已知的基础设施。

表2-伪装成医疗和科技公司的域名

![p5](http://drops.javaweb.org/uploads/images/5367099a519586d5454a6f1727986cd25ebd1f92.jpg)

Black Vine通常不会用相同的邮箱地址来注册域名。注册人地址[li2384826402@yahoo.com](mailto:li2384826402@yahoo.com)似乎属于一个域名经销商，与Black Vine并无直接联系。

表3-在Anthem攻击中发现的Mivast样本

![p6](http://drops.javaweb.org/uploads/images/13405a3c91dfb2e5af6c04f468a273f7dcbab897.jpg)

表3中列出了Anthem事件中使用的几个Mivast样本。

我们不清楚攻击者使用了什么机制来投放木马。很可能是通过钓鱼邮件，因为在这次攻击活动中，我们并没有发现水坑攻击的迹象。木马本身使用Citrix和Juniper VPN诱饵进行了伪装，也就是说，攻击活动一开始的攻击目标是Anthem的技术员工。

0x09 Black Vine的背后是谁？
=====================

* * *

我们分析了Black Vine使用的基础设施、资源和攻击模式，从而确定他们的动机。我们还研究了一些开源数据，这些数据表明Black Vine的成员与北京一家公司有关联。

**与北京某IT公司的关系**

Threat Connect在发表的一份博客中提到，根据基础设施的注册信息，能够追踪到Anthem入侵事件的源头来自中国。在入侵Anthem时使用的Mivast木马样本(MD5:230D8 A7A60A07DF28A291B13DDF3351F)，关联到了一个IP地址是192.199.254.126的基础设施。在Mivast 样本的CC托管在这个IP地址上的时间前后，这个IP上只有为数不多的几个域名，其中就包括域名topsec2014.com。

topsec2014. com 的注册地址是[topsec2014@163.com](mailto:topsec2014@163.com),这个邮箱地址与[TopSec_2014@163.com](mailto:%E8%BF%99%E4%B8%AA%E9%82%AE%E7%AE%B1%E5%9C%B0%E5%9D%80%E4%B8%8ETopSec_2014@163.com)很类似。topsec2014 domain域名和先前提到的邮箱地址都与北京某IT公司有关联。

![p7](http://drops.javaweb.org/uploads/images/87c7603a44681c4784e4cbfa899cea9797bd509a.jpg)图4-关于北京某IT公司的详细介绍

北京某IT公司这个组织主要专注于安全研究、培训、审计和产品开发。其客户包括私有公司和公共部门。这家公司每年还会举办计算机攻击竞赛，并且据报道雇佣了黑客来提供服务和培训。

**0-day开发和传播**

Black Vine在多次活动中都利用了未知的0-day漏洞来投放他们自己开发的有效载荷。通常识别0-day漏洞并判断其利用方法，需要较高的黑客技术。一般来说，这些漏洞可以通过地下网络购买，或由漏洞开发者自己开发。这两种方式都需要大量的资金。

对于Black Vine而言，Symantec发现他们的活动与其他的网络间谍活动之间有相似的模式。这些攻击活动也会使用相同的0-day漏洞，但是投放不同的有效载荷。很明显，他们能接触到相同的0-day漏洞，然后在不同的小组之间传播和利用，如图5。

![p8](http://drops.javaweb.org/uploads/images/f8efa2547e984a32da5beb24b23176281000d329.jpg)图5-0-day的传播和使用时间

**CVE-2012-4792 0-day漏洞**

2012年12月末，美国外交关系协会（CFR）的网站遭到了入侵。据称，CFR的域名被用来利用了 IE6浏览器中的一个未知漏洞，最终确认这个未知漏洞是CVE-2012-4792。在当时，并没有修复这个漏洞的补丁，导致使用有漏洞版本IE浏览器的用户没有办法来处理这一问题。一旦漏洞利用成功，攻击者就会投放Backdoor.Bifrose变种。根据Symantec先前的发现，Bifrose与另外一起间谍活动有关联。Symantec认为Black Vine与这次攻击活动和CFR入侵事件没有关联。

如我们所说的，2012年12月，Black Vine攻击了Capstone Turbine。根据之前发现的实例以及在CFR和Capstone网站上发现的恶意代码，我们认为这几次攻击活动都是在同一周前后进行的。

在这两起网站入侵事件中，这些域名都是利用了相同的IE浏览器0-day漏洞(CVE-2012-4792)。不同之处在于，在攻击Capstone时，投放的是Sakurel有效载荷；而在攻击CFR时，投放的是Bifrose。

**CVE-2014-0322 0-day漏洞**

在2014年2月，另外两个小组也利用了同一个0-day来投放不同的有效载荷。在2014年2月11日-15日之间，美国退伍军人网(VFW.org)和欧洲一家飞机制造商的网站都遭到了水坑攻击。与2012年的攻击活动类似，这些网站都被强制利用了IE浏览器中的一个0-day漏洞（CVE-2014-0322）来投放恶意有效载荷。

在攻击VFW.org时，投放的是一个Backdoor.Moudoor变种。Symantec在以前的报告中就说过，这个小组曾经利用Moudoor发动了针对性攻击。针对飞机制造商的攻击活动和VFW攻击活动是同时进行的，并且利用了同一个0-day漏洞。在针对航天业的水坑攻击中，Black Vine使用的有效载荷是Sakurel木马。

**Elderwood联系**

在2012年和2014年，有不同的攻击小组同时利用相同的0-day漏洞发动了攻击活动，但是投放了不同的木马。在这些活动中使用的木马应该是各个小组自己开发的。Symantec此前就确定了这些攻击小组会利用Elderwood框架来交换木马。

在此前的攻击活动中，利用的0-day漏洞应该是来自中国黑客。

**归属**

Black Vine似乎掌握有充足的资源来开发和更新他们自己的木马，并且他们还掌握有0-day漏洞来发动针对性攻击。这些资源和能力表明Black Vine有强大的资金和资源支持。Black Vine从2012年末开始一直在攻击几个产业，应该是有组织的网络间谍小组。

Black Vine的有些基础设施似乎与北京某IT公司有关联。

通过Elderwood框架也能证明Black Vine在与其他攻击小组合作。并且Black Vine还通过Elderwood给其他攻击者分享0-day漏洞。

0x0A 结论
=======

* * *

至少从2012年起，Black Vine久开始了攻击活动。经过Symantec的分析，Black Vine针对能源、航空航天业、医疗业和其他行业发动了多起攻击活动。Black Vine利用了多个木马变种，包括Hurix，Sakurel和 Mivast。所有这些木马都是由同一名作者开发和更新的。每个变种都会通过更新来增加功能，并更改哈希来躲避检测。

在大量的攻击活动中，Black Vine首先会通过水坑攻击，利用0-day漏洞，在受害者的计算机上投放木马。攻击者还会通过Elderwood分享在这些攻击活动中使用的0-day漏洞。另外，Black Vine的所有活动目的都是网络间谍行动。

媒体曝光了Anthem入侵事件，这次攻击是美国医疗历史上最严重的数据失窃事件。 Black Vine发动的这次攻击活动是2015年受关注程度最高的事件之一。但是，这只是Black Vine的一次攻击活动，他们也在攻击其他的几个行业，包括能源产业和航空航天业。我们希望这份报告能够帮助组织更好地理解Black Vine，包括他们的TTP，动机和使用的木马。

我们希望这份报告能够帮助组织更好地理解Black Vine，包括他们的TTP，动机和使用的木马。只有了解了Black Vine的活动，分析人员和决策者才能更有效地与之对抗。

0x0B 应对办法
=========

* * *

Symantec能够防御Black Vine的木马：

**AV**

*   Backdoor.Mivast
*   Trojan.Sakurel

**IPS**

System Infected: Trojan.Sakurel Activity