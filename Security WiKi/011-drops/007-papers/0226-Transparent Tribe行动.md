# Transparent Tribe行动

[https://www.proofpoint.com/sites/default/files/proofpoint-operation-transparent-tribe-threat-insight-en.pdf](https://www.proofpoint.com/sites/default/files/proofpoint-operation-transparent-tribe-threat-insight-en.pdf)

0x00 简介
=======

* * *

Proofpoint的研究人员近期发现了一起针对印度大使馆和军方的APT攻击行动。我们首先调查了印度驻沙特大使馆收到的一些恶意邮件，以及具备文件窃取功能的RAT木马。经过分析，我们发现这些攻击活动使用的IOC，攻击途径，有效载荷和语言都很常规，但是，具体的APT特征仍需要我们进一步的调查。

在本文中，我们提供了相关的背景知识，一些实用的分析证据，并详细的探讨了我们对“MSIL/Crimson”木马的思考。

0x01 攻击印度驻沙特和哈萨克斯坦大使馆
=====================

* * *

2016年2月11日，我们发现了两次攻击活动，这两次活动只有两分钟的间隔，分别攻击了印度驻沙特大使馆和印度驻哈萨克斯克大使馆。相关的邮件（图1和图2）都是发送自同一个IP地址（5.189.145[.]248），这个IP属于Contabo GmbH，目前来看，攻击者非常喜欢利用这家提供商的服务。另外，这些邮件似乎还利用了Rackspace的MailGun服务，而且这两封邮件的附件也都是一样的。

邮件：

```
4a0728a48c393a480dc328c0e972d57c5493ee5619699e9c21ff7e800948c8e8,”def.astana” <def.astana@mea. gov.in>

839569f031a2cb6e9ae1dc797b1bd7cce53d3528c8b5fbec21cecb0de3f5ac88,”def.riyadh” <def.riyadh@mea. gov.in>

```

附件：3966f669a6af4278869b9cce0f2d9279, Harrasment (sic) Case Shakantula.doc

*   **漏洞:**CVE-2012-0158
*   **投放的doc：**6a69cd7a2cb993994fccec7b7e99c5daa5ec8083ba887142cb0242031d7d4966,svchost.exe
*   **功能:**downloader

![p1](http://drops.javaweb.org/uploads/images/7beea1c610c946727ad5af6492b80cd272d0ae2c.jpg)图1-发送到印度驻哈萨克斯坦阿斯坦纳大使馆的第一封邮件

![p2](http://drops.javaweb.org/uploads/images/86eedc2de5f7275df4d14b68d92db016fc31af78.jpg)图2-发送到印度驻沙特利雅得大使馆的第二封邮件

在这次事件中，利用的附件是一个经过处理的RTF文档，这个文档会利用漏洞CVE-2012-0158来投放一个经过编码的PE可执行程序。要想解码这个内嵌PE，文档的shellcode首先会查找0xBABABABA标记，在找到相应的标记时，会指示出PE的开始位置（图3）。然后，通过使用解密秘钥0xCAFEBABE就可以加密这个PE了，但是所有无效的DWORD都会被跳过（图4）。最后一个标记指示的是PE文件的结束位置，在这里，最终标记是0xBBBBBBBB。在此之前，已经有一些毫不相关的攻击事件曾经利用过这个解码例程以及漏洞文档中的其他组件。

![p3](http://drops.javaweb.org/uploads/images/b660e8fa31c5eede3ab9f5622f84a1c23199a081.jpg)图3-shellcode正在查找0xBABABABA标记

![p4](http://drops.javaweb.org/uploads/images/8ecf609ea87b27cf9dd671c63a670dc232e9f775.jpg)图4-正在解码PE文件并查找终止标记

在成功利用了漏洞并解码了有效载荷后，MSIL/Crimson家族木马就会在受害者的设备上执行。在感染的第一阶段，downloader会下载具备完整功能的RAT组件。MSIL/Crimson的downloader（md5: 3a67ebcab5dc3563dc161fdc3c7fb161）会尝试从213.136.87[.]122:10001下载完整的RAT木马。我们在技术分析部分会详细的说明和分析MSIL/Crimson家族木马。

![p5](http://drops.javaweb.org/uploads/images/7cc2c7c8de38f28f6665700a61afd0def5fc5799.jpg)图5-MSIL/Crimson正在下载RAT

0x02 虚假的印度军方博客引诱目标下载MSIL/Crimson木马
==================================

* * *

在研究MSIL/Crimson木马的过程中，Proofpoint的研究人员发现了一个恶意的blogspot.com网站（图6）-intribune.blogspot[.]com，这个网站的目的似乎是为了诱使印度军官感染MSIL/Crimson木马，njRAT和其他的恶意工具。根据CC基础设施来看，很这个网站的管理者很可能就是先前攻击印度大使馆的攻击者。在这个网站上公布的文章中，有很多会把受害者定向到恶意有效载荷，在我们分析时，只有少数的几篇没有包含恶意代码。从网站上的一些文章中，我们了解到攻击者可能会通过不同的方式来实施其恶意活动：

1.  通过图片或文本使用超链接
2.  在文章配图的文本上或iframe中使用超链接
3.  在本节的最后一篇文章中出现了一个链接，这个链接指向了攻击者的另一个网站，并且与其他的邮件活动有一定关联。

**诱饵文章**

**4 Sikh Army Officers being trialed in military court on alleged involvement with KLF **

*   链接：hxxp://intribune.blogspot[.]com/2015/11/4-sikh-army-officers-being-trialed-in.html
*   恶意文档位置：hxxp://bbmsync2727[.]com/news/4%20Sikh%20Army%20Officers%20being%20trialed. doc*Document: *0197ff119e1724a1ffbf33df14411001
*   类型：漏洞,CVE-2012-0158,

投放的嵌入式有效载荷: njRAT - 27ca136850214234bcdca765dfaed79f*C&C: *5.189.145[.]248:10032

![p6](http://drops.javaweb.org/uploads/images/3726bc1bf930e93c132da4461bd5fcde5644c5d9.jpg)图6-这篇诱饵文章会导致受害者下载到漏洞文档，在受害者的机器上安装njRAT

![p7](http://drops.javaweb.org/uploads/images/9487615a0e49d8fe075e7c758478dcaa8874c2c8.jpg)图7-“4 Sikh Army Officers being trialed.doc”投放的诱饵文档

这篇文章的独特之处在于其中包含有一个iframe，指向了同一个通过“Read More”超链接下载的文档。这个iframe会提示网站访客立刻下载文档，在最高级别的恶意网站上也是同样。

![p8](http://drops.javaweb.org/uploads/images/6cf73a08e1a10677c17b1234060daade9f8d0742.jpg)图8-链接到恶意档案的iframe

链接：`hxxp://intribune.blogspot[.]com/2015/11/seventh-pay-commission-recommends.html`

在分析时，这个网页上没有出现任何恶意链接，但是，我们发现了一个文档，这个文档可能就是为这个网页所准备的，也可能是网页上曾经使用的一个文档。

恶意文档位置：`hxxp://bbmsync2727[.]com/cu/seventh%20pay%20commission%20salary%20calculator.xls`

*   文档：0e93b58193fe8ff8b84d543b535f313c
*   其他文档位置：`hxxp://bbmsync2727[.]com/cu/awho_handot_2015.xls`
*   VBS位置：`hxxp://bbmsync2727[.]com/cu/su.exe`
*   有效载荷（旧版）：07e44ffcffde46ad96eb9c018bed6193 (DarkComet)
*   CC（旧版）：5.189.145[.]248:1453
*   有效载荷（新版）：708a1af68d532df35c34f7088b8e798f (Luminosity Link RAT)
*   CC（新版）：5.189.145.248:6318

![p9](http://drops.javaweb.org/uploads/images/c76fb48ede84db48d86bb72fb4a3bac1d640a479.jpg)图9-诱饵文章可能指向DarkComet或其他木马

**Army Air Defence (sic),Engineers and Signal to get additional colonels posts **

*   链接：hxxp://intribune.blogspot[.]com/2015/11/army-air-defenceengineers-and-signal-to.html
*   恶意文档位置：hxxp://birthdaywisheszone[.]com/pml/army-air-defenceengineers-and-signal.doc
*   文档：68773f362d5ab4897d4ca217a9f53975
*   类型：漏洞,CVE-2012-0158,
*   投放的嵌入式有效载荷：dac4f8ba3190cfa1f813e79864a73fe1 (MSIL/Crimson Downloader)
*   CC：213.136.87[.]122:10001
*   下载的 MSIL/Crimson RAT：f078b5aeaf73831361ecd96a069c9f50

![p10](http://drops.javaweb.org/uploads/images/e0ee0d3f5ead834b55e8c69c5efbc28860193644.jpg)图10-诱饵文章最终会指向MSIL/Crimson RAT

![p11](http://drops.javaweb.org/uploads/images/f4d51044a688f93dcc4f65c54623edd18c6706b8.jpg)图11-“army-air-defenceengineers-and-signal.doc”投放的诱饵文档

*   链接: hxxp://intribune[.]blogspot[.]com/2015/09/sc-seeks-army-response-on-batch-parity.html
*   恶意文档位置: hxxp://www[.]avadhnama[.]com/latest/batchparity-command-exit-policy.doc

不幸的是，我们没能获取到相应位置上的诱饵文档，不过，在这个目录下，我们找到了另一个文件。

*   位置: hxxp://avadhnama[.]com/latest/ssbs.exe
*   哈希: df6b3946d1064f37d1b99f7bfae51203 (MSIL/Crimson Downloader)
*   CC: 213.136.87.122:10001
*   下载的MSIL/Crimson RAT: c2bc8bc9ff7a34f14403222e58963507

![p12](http://drops.javaweb.org/uploads/images/0fac8ae15959a3dfae06d8546ef6918b7542231b.jpg)图12-诱饵文章可能会指向MSIL/Crimson RAT

**Seniors Juniors and coursemates please take a serious note about it **

*   位置：hxxp://intribune[.]blogspot[.]com/2015/05/seniors-juniors-and-coursemates-please.html
*   潜在的有效载荷位置：hxxp://sms[.]totalworthy[.]com/intribune.zip

我们没能获取到intribune.zip，而且也无法确定其中是否包含有效载荷。

![p13](http://drops.javaweb.org/uploads/images/cdfcabc86b749704715835c8e0f4e10eb6a77b7b.jpg)图13-诱饵文章指向一个旧版的恶意有效载荷

**AWHO– Defence (sic) and Para-Military Forces Personnel Plots Scheme 2016 **

**链接: **`hxxp://intribune[.]blogspot[.]com/2015/07/awho-defence-and-para-military-forces.html`

*   恶意文档位置：hxxp://bbmsync2727[.]com/upd/AWHO-Upcoming-Projects.doc
*   位置：1f82e509371c1c29b40b865ba77d091a
*   类型：漏洞,CVE-2012-0158,
*   投放的嵌入式 有效载荷：643d6407cd9a4f1c6d2742f24aed34f5 (MSIL/Crimson Downloader)
*   CC：213.136.87.122:10001
*   下载的 MSIL/Crimson RAT：0e3e81f4d2054746f74442075f82a5c5

![p14](http://drops.javaweb.org/uploads/images/ad85de68f230668f8ddc41335c866ae25c15d130.jpg)图14-诱饵文章最终指向MSIL/Crimson和另一个恶意网站

AWHO文章中包含有一个指向`hxxp://cdrfox[.]xyz/`的链接，其超链接是“GET CALL DETAIL RECORDS ONLINE”。这个网站的管理员很可能就是这群攻击者，而这个恶意网站能够向受害者投放VBS恶意文档（图15）。并且，从中能很明显的看出，恶意网站的攻击目标是印度。在填写了大量的提交表单后，受害者会被定向到另一个页面上，在这个页面上会包含有下载恶意文档的最终链接（图16）。

![p15](http://drops.javaweb.org/uploads/images/de7bdfbeb9fbaa879b0275956bf8b83deff16bfa.jpg)

![p34](http://drops.javaweb.org/uploads/images/f23f73941cb31ce028b19dfbc4c5a8d5638f0d88.jpg)图15-cdrfox[.]xyz的登录页

![p16](http://drops.javaweb.org/uploads/images/d4ba85ea86dd35de40bdea5fd9a77f0de68c1550.jpg)图16-下载诱饵文件，其中包含的文档最终会致使受害者感染Crimson Downloader

*   位置：hxxp://fileshare[.]attachment[.]biz/?att=1455255900
*   文档：18711f1db99f6a6f73f8ab64f563accc
*   文档名称：“Call Details Record.xls”*Type: *VBS Macro
*   VBS 位置：hxxp://afgcloud7[.]com/logs/ssc.mcom
*   有效载荷：3cc848432e0ebe25e4f19effdd92d9c2 (MSIL/Crimson Downloader)
*   下载的MSIL/Crimson RAT：463565ec38e4d790a89eb592435820e3

在同一个服务器的其他目录下，还有另外的一些有效载荷：

*   hxxp://afgcloud7[.]com/com/psp.dlc-bk (hash: 62d254790834f30a79ee79305d9be837, also previously named psp.dlc)
*   hxxp://afgcloud7[.]com/com/psp.dlc (hash: dd0fc222852f5d12fda2fb66e61b22f6)
*   hxxp://afgcloud7[.]com/upld/updt.dll (hash: 0ad849121b4656a239e85379948e5f5d)

“/com/”目录下的两个文件都是恶意dropper类型，最终会投放一个Excel诱饵文档和一个MSIL/Crimson downloader。Excel文档使用的主题都会涉及到印度陆军军官福利组织（AFOWO），并且投放的dropper以及RAT会像之前讨论过的样本一样与相同的CC通讯。我们还发现一个命名为“AFOWO Broucher 2016.xls”（哈希：98bdcd97cd536ff6bcb2d39d9a097319）的文档中也包含有恶意宏，会尝试从hxxp://afgcloud7[.]com/com/psp.dlc下载一个有效载荷。另外，IP地址50.56.21[.]178会解析到email. books2day.com（曾经用来攻击大使馆）。这个IP近期不再解析到email.afowoblog[.]in。我们并不意外，[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)“AFOWO Broucher 2016.xls”文档。在下面的分析部分中，我们又进一步的分析了这个域名。

**62d254790834f30a79ee79305d9be837 / dd0fc222852f5d12fda2fb66e61b22f6: **

*   投放的诱饵dropper：29054da7a1f1fbd0cb3090ee42335e54
*   诱饵文档：66cd38a03282b85fceec42394190f420
*   有效载荷：83a8ce707e625e977d54408ca747fa29 or 2c9cc5a8569ab7d06bb8f8d7cf7dc03a (both MSIL/Crimson Downloader)
*   CC：213.136.87.122:10001
*   下载的MSIL/Crimson RAT：463565ec38e4d790a89eb592435820e3

**0ad849121b4656a239e85379948e5f5d **

在“/upld/”目录下发现的有效载荷（md5: 0ad849121b4656a239e85379948e5f5d）是一个MSIL/Crimson SecApp模块，这个模块能够下载一个具备完整功能的MSIL/Crimson RAT和所有的后续模块。另外，这个有效载荷还会投放一个叫做“Cv of IMA Chief.docx”的诱饵文档（图17，哈希：8e5610d88c7fe08ac13b1c9f8c2c44cc）。这个诱饵文档中可能包含有与Brigadier General相关的信息，（诱饵文档中称）此人是阿富汗国际军事事务部部长。

![p17](http://drops.javaweb.org/uploads/images/162958f7eda0ff2df81a568d72aebca83dd94030.jpg)图17-0ad849121b4656a239e85379948e5f5d投放的诱饵文档

0x03 分组分析
=========

* * *

在这一部分中，我们研究了MSIL/Crimson木马以及一部分Transparent Tribe活动。虽然，其他的攻击者也曾经使用过这一工具，但是，我们通过研究，缩小了上百个Crimson样本所属的攻击活动范围。

### 分类1-Transparent Tribe行动等

有上百个样本属于第一分组，是规模最大的一次活动，其中最早的样本可以追溯到2012年（图18）。对于这一分组，我们首先分析了针对印度大使馆的邮件攻击活动和假冒的印度新闻博客。通过研究，我们在攻击者控制的CC上发现了大量的样本，借此我们又另外找到了一期邮件攻击活动。在其中一个CC上，有一个基于Python的RAT（Python/Peppy），这个RAT的活动与Transparent Tribe行动中使用的样本非常相似。另外，我们还发现Andromeda downloader在下载和执行MSIL/Crimson木马时，也会同样下载和执行这个RAT。除了Crimson和Peppy，我们观察到了Luminosity Link RAT，njRAT，Bezigate，Meterpreter以及其他几个自定义downloader。

![p18](http://drops.javaweb.org/uploads/images/bb8eee23270214dd9bf794766370f5079192a941.jpg)图18-分组1活动的Maltego图

负责这次活动的攻击者既利用了被攻破的基础设施，也利用了他们手中掌握的基础设施（比如，bbmsync2727[.]com）。很多情况下，攻击者采用了相同的模式来命名其域名：

*   域名和文件名中出现sync
*   域名和文件名中重复使用bb，大部分是bbm
*   使用4位数作为二级域名的结尾

除此之外，在这一分组的活动中，大量使用了Contabo GmbH作为CC。但是，在进行分类时，我们还考虑了其他因素。接下来，我们会谈论另一起邮件攻击-attachment.biz活动，最后，我们还分析了域名afowoblog.in，所有这些活动都属于这一分组。

**使用“2016 Pathankot attack”作为诱饵的邮件活动**

在研究这次活动的过程中，我们发现了另外一起邮件攻击活动，在这次邮件活动中使用的诱饵是2016年帕坦克特袭击事件（图19）。这次攻击利用了一个URL（hxxp://comdtoscc.attachment[.]biz/?att=1451926252）投放了一个压缩文件（md5：f689471d59e779657bc44da308246ac4），在这个压缩文件中包含有两个MSIL/Crimson有效载荷，都使用了193.37.152[.]28:9990作为CC。

![p19](http://drops.javaweb.org/uploads/images/50716fe2016432f584c69c9f606668511aa81dc5.jpg)图19-使用“2016年帕坦克特袭击事件”作为诱饵的邮件活动

攻击者为了提升成功几率，在每个MSIL/Crimson有效载荷中都添加了诱饵文件：

**样本 1：65f6143d69cb1246a117a704e9f07fdc**

*   初始名称：“Call Record and Tracking Route.scr”
*   投放的诱饵：2f821d8c404952495caae99974601e96, 带有图像的音频文件（图20）
*   诱饵名称：“Call Record and Tracking Route.mp3”

![p20](http://drops.javaweb.org/uploads/images/0a0afeb02014bddb6033b8c09b573ccc1b4c738d.jpg)图20-音频诱饵，可能是在讨论帕坦克特袭击事件

**样本2：723d85f905588f092edf8691c1095fdb**

*   初始名称：*“detail behind the scenes.scr”
*   投放的诱饵：a523b090e9a7e3868d8d1fde3e1ec57d,PDF (Fig. 21)
*   诱饵名称：“detail behind the scenes.pdf”

![p21](http://drops.javaweb.org/uploads/images/9b30f7cb58ef039cfd74ad64f523b82ef0407bcb.jpg)图21-以帕坦克特袭击事件作为诱饵

**ATTACHMENT.BIZ域名**

我们发现了一起围绕ATTACHMENT.BIZ域名实施的活动，在这次活动中投放了恶意文档和有效载荷。我们观察到了下面的一些域名：

*   fileshare.attachment[.]biz• comdtoscc.attachment[.]biz
*   ceengrmes.attachment[.]biz
*   email.attachment[.]biz (没有发现链接)

所有这些域名都解析到了同一个IP 91.194.91[.]203 (Contabo GmbH)。目前为止，我们已经发现了三次独立进行的活动，但是我们还不知道该从哪里入手，但是我们能确定的是，这次活动属于这一分组。

**链接1: hxxp://ceengrmes.attachment[.]biz/?att=1450603943**

*   有效载荷：07defabf004c891ae836de91260e6c82, MSIL/Crimson
*   有效载荷名称：Accn Letter.scr
*   CC：5.189.143[.]225:11114

**链接 2: hxxp://fileshare.attachment[.]biz/?att=1455264091**

*   有效载荷：18711f1db99f6a6f73f8ab64f563accc,XLS VBS-downloader
*   有效载荷名称：Air India Valid Destinations.xls

在攻击者的cdrfox.xyz网站上，hxxp://fileshare[.]attachment[.]biz/?att=1455255900投放的也是同一个有效载荷。

**链接 3: hxxp://comdtoscc.attachment[.]biz/?att=1453788170**

*   有效载荷：45d3130a901b7a763bf8f24a908b1810,
*   压缩后的有效载荷名称：Message.zip
*   Decompressed Payload：765f0556ed4db467291d48e7d3c24b3b, MSIL/Crimson
*   解压后的有效载荷名称：Message.scr*C&C: *193.37.152[.]28:9990

**AFOWOBLOG.IN域名**

有证据表明，afowoblog.in域名应该属于这一活动分组。这个域名是在2016年2月14日前后注册的，使用的地址是thefriendsmedia@gmail.com，“AFOWO Broucher 2016.xls”就是在同一天上传到了VT。我们发现使用了thefriendsmedia[.]com的相关活动最早可以追溯到2013年6月，在当时，这个地址是用作了一个Andromeda C&C。

在一起活动中（图22，maltego图），我们观察到一个Andromeda有效载荷正在与brooksidebiblefellowship[.]org通讯，从olxone[.]com上获取了另外一个Andromeda有效载荷，接着又使用了thefriendsmedia[.]com作为其CC。初始的Andromeda还获取了一个Bezigate有效载荷。

![p22](http://drops.javaweb.org/uploads/images/c2cc455869f41a438e182e6d6171f36c387ed349.jpg)图22-thefriendsmedia与Andromeda，lolxone[.]com，Bezigate之间的联系

此外，我们发现lolxone[.]com上托管着其他的Bezigate有效载荷，以及Python/Peppy木马（图23）。如Maltego图所示，通过与Peppy，Bezigate和Andromeda C&C之间的联系来看，这次活动也是属于这一分组（图25）。

![p23](http://drops.javaweb.org/uploads/images/cad6ab8b4cbd1f1361a8778d7dbad9597e274862.jpg)图23-lolxone[.]com与Andromeda 和Python/Peppy，Bezigate之间的联系

### 分组2-guddyapps/appstertech/sajid

我们遇到的一些Crimson SecApp模块，在第一次与CC通讯时，并不会下载RAT或downloader的有效载荷。比如，样本：85429d5f2745d813e53b28d3d953d1cd会从178.238.228[.]113:7861获取downloader。一旦downloader执行，就会下载一个XMPP二进制（md5: fee34da6f30a17e1fcc5a49fd0987169）和一个基于XMPP的木马（md5: d3094c89cad5f8d1ea5f0a7f23f0a2b1）-我们一般称呼这个木马为Beendoor。Beendoor是一个很有意思的木马，这个变种的CC是178.238.235[.]143。

与 Crimson和Peppy类似，Beendoor能够获取桌面截图。在Beendoor的CC上，我们恢复了一张貌似来自木马开发者的桌面截图（图24）。在这个修改过的截图中，我们注意到了一些关键信息：

*   桌面上出现了同一张 “Anushka” 图片，曾经出现在Beendoor 的C&C上，Beendoor样本也曾经使用过这个图片
*   文件夹结构与CC的文件夹结构类似
*   在Beendoor的dropper二进制中发现了硬编码的路径（md5: 9b98abb9a9fa714e05d43b08b76c0afa）
*   Beendoor和XMPP二进制使用了相同的文件名

![p24](http://drops.javaweb.org/uploads/images/87fc74ce21eea9ab10c2b8fe6801f2130d480c53.jpg)图24-可能是Beendoor开发者的桌面截图

从图中可以看出，巴基斯坦公司Appstertech连接到了Beendoor木马。通过分析Beendoor CC上的文件夹和文件，我们总结出去年年末CloudSek研究的就是这次活动。

在连接到Beendoor（图25）的Crimson样本中，有几个使用了同一个“Binder” dropper，我们在其他的一些分组中也观察到了对这个dropper的使用，其中也包括分组1。而且，Crimson和Beendoor的CC都是托管在Contabo GmbH，其他分组中的Crimson木马也有相似之处。

![p25](http://drops.javaweb.org/uploads/images/2e663aec6c2d885e4aba52172268b8c0a70745d3.jpg)图25-Crimson的Maltego图<->Beendoor分组

### 分组3-“Nadra attack in Mardan”诱饵

除了使用帕坦克特袭击事件作为诱饵的攻击活动，我们还在近期的活动中发现，有几个样本利用了12月份在马尔丹发生的国家数据库和注册局（Nadra）袭击事件作为诱饵。有几个样本被上传到了VT，在压缩文件中包含有Crimson有效载荷，以及各自dropper投放的诱饵。例如，其中一个有效载荷(md5: 51c57b0366d0b71acf05b4df0afef52f, “NADRA OFC.exe”)是和一张图片 (md5: be0b258e6a419b926fe1cfc04f7e575a)一起上传到了VT，这张照片的链接是hxxp://i.dawn[.]com/ medium/2015/12/56825d6d8f1a5.png，来自一篇与袭击事件相关的文章：hxxp://www.dawn[.]com/ news/1229406。

对于这一分组中的活动，我们还没有发现任何dropper，所以我们决定将这些活动单独列到一组中。在弄清楚了这一点后，你会发现这次行动的TTP与分组1中“以帕坦克特袭击事件作为诱饵”的行动基本一致。不出所料的是，在此次行动中使用的CC也是托管在Contabo GmbH。最后一点，这些样本使用的端口是11100，分组1中的一些样本也使用了这一个端口。

### 分组4-DDNS与巴基斯坦

在最后一个分组中，有几个样本使用了**DDNS**作为其**CC**，这些**CC**都指向了巴基斯坦的**IP**地址（根据**Whois**信息）。大部分活动都是始于**2013**年。从**TTP**的细微差别（只使用**DDNS**）和没有使用**Contabo GmbH**来看，我们把这些活动与其他活动进行了区分，尽管分组**1**中的一些活动也使用了**DDNS**和相同的工具。图**26**中描绘的就是这类活动。我们在**IOC**章节讨论了这类活动。

![p26](http://drops.javaweb.org/uploads/images/801af45182b02ee391084c85a99910d4aafaf8d9.jpg)图_26-DDNS_和巴基斯坦_IP_地址反映在_Maltego_图

还缺少足够的信息来串联所有的活动分组

虽然，不同的活动分组之间有大量的相似点，包括使用“Binder” dropper，攻击诱饵，更明显的是使用了Contabo GmbH。不过，还有一些样本是我们不了解的，比如，这些样本的使用方式，是在哪次活动中使用的，所以我们还无法串联起所有的活动。随着我们的继续研究，我们应该能够找到更多的信息，从而确定各个分组之间的联系。

0x04 技术分析
=========

* * *

**MSIL/Crimson**

Crimson更像是一个模块化木马，因为主RAT模块可以下载其他的有效载荷，执行键盘记录或窃取浏览器凭证等功能。Crimson会分阶段感染目标。Crimson感染的第一阶段是由downloader组件下载一个具备完整功能的RAT，通常是Crimson的RAT模块。然后，RAT模块会将系统信息发送给CC，而CC可能会响应另外的模块化有效载荷。

Crimson利用了一个自定义的TCP协议来进行CC通讯（图27）。有些Crimson会选择性的下载不具备CC通讯能力的模块，而是通过RAT组件来向外输送信息。

![p27](http://drops.javaweb.org/uploads/images/372247f3255c4149d6beea0e20625d797d8bce8a.jpg)图_27-Crimson_的自定义_TCP CC_协议

感染了Crimson的受害者会处在监控中，可以监控摄像头，窃取Outlook中的邮件，记录用户的屏幕。有些Crimson RAT变种能够支持至少40种命令。在表1中列出了各个版本的RAT所支持的所有命令。

表1-MSIL/Crimson支持的命令

| 命令 | 介绍 |
| --- | --- |
| afile | 提取文件到CC |
| audio | 从CC下载合法的NAudio库，保存为NAudio.dll（不会执行或添加到startup）。用于通过麦克风记录声音。 |
| autf | 向文件扩展列表中添加扩展。可选择查找符合文件扩展列表要求的文件并提取。 |
| autoa | 提取所有符合文件扩展列表要求的文件 |
| capcam | 静态捕捉webcam |
| camvdo | 持续性捕捉webcam（使用stops命令停止） |
| clping | 将runTime设置成DataTime.Now |
| clrklg | 停止键盘记录模块并删除键盘记录日志 |
| cnls | 停止上传，下载和截图 |
| cscreen | 单次截屏 |
| delt | 删除提供的路径/文件 |
| dirs. | 发送磁盘驱动器 |
| dotnet | 下载URLDownload有效载荷，保存为dotnetframwork.exe，并通过注册表添加到startup |
| dowf | 从CC获取文件 |
| dowr | 从CC获取文件并执行 |
| email | 能够获取邮箱账户名称，邮件数量，并提取Outlook中的邮件 |
| endpo | 杀死指定PID的进程 |
| fbind | 从CC现有目录中保存文件，在名称后添加.exe扩展 |
| file | 将文件传输给CC |
| filez | 发送文件信息：CreateTimeUtc，文件大小 |
| fldr | 列出一个目录下的文件夹 |
| fles | 列出一个目录下的文件 |
| ftyp | 向文件扩展列表中添加扩展 |
| info | 发送PC信息（MAC, PC Name, User, LAN IP, OS, AV, 缺失的模块...） |
| klgs | 有时候不会实现，但是存在这个命令（先前的版本会自动提取键盘记录） |
| listf | 搜索指定的文件扩展 |
| mesg | 弹出“警告”对话框，显示提供的信息 |
| msdlf | 点击鼠标 |
| muspo | 移动鼠标指针 |
| obind | 保存CC上的文件到目录，名称后添加.exe扩展 |
| outdwn | 搜索特定名称的邮件附件并提取 |
| passl | 获取密码记录模块的日志 |
| procl | 列出进程 |
| runf | 执行命令 |
| rupth | 获取木马的运行路径 |
| savaf | 从CC保存文件 |
| scrsz | 设置scrSize（由scren和cscreen使用） |
| secup | 从CC下载“secApp”有效载荷，通过注册表添加到startup |
| sndpl | 从CC下载“pssApp”（浏览器凭证窃取模块），并开始提取日志 |
| sndps | 从CC下载“pssApp”（浏览器凭证窃取模块） |
| splitr | 按照提供的分割数量分割文件，但是，我们认为由于编程错误，这个功能无法正常运行 |
| stops | 停止截图 |
| stsre | 获取麦克风音频 |
| sysky | 将键盘记录发送到CC |
| systsk | 更新模块，类似secApp |
| thumb | 获取200x150 GIF 图像缩略图 |
| uclntn | 设置RegKey：把[variable]_ver设置成提供的值，可能是用作版本标识 |
| udlt | 从CC下载“remvUser”有效载荷，保存为msupdate.exe，然后执行 |
| uklog | 从CC下载键盘记录模块的有效载荷，保存为win_services.exe，然后通过注册表添加至startup |
| updatc | 下载控制器/客户端/主RAT，保存为servicesdefender.exe，然后执行 |
| updatu “OR” usbwrm | 下载USB有效载荷，保存为udriver.exe，然后通过注册表添加至startup |

**MSIL/Crimson 模块分析**

和先前提到的一样（以及命令表），Crimson需要依靠模块化的有效载荷才能扩展其功能，包括，记录键盘敲击，窃取浏览器凭证，自动搜索并窃取移动磁盘上的文件，另外还有两个不同的有效载荷更新模块。最后一点，我们没能够找到“remvUser”模块。

**URLDownload**

在执行时，这个模块首先会检查注册表键值：`HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\last_edate`是否存在。如果不存在，这个模块就会创建这个键值并分配一个DateTime.Now字符串。这个键值会定期检查已经度过的天数。一旦木马检测到已经过去了15天，木马就会发送一个HTTP GET请求到硬编码的地址，从而获取一个文本文件，而这个文本文件会指向另外一个HTTP位置，在这里有最终的有效载荷。比如，在我们分析的一个样本中(md5: 532013750ee3caac93a9972103761233)就包含有一个硬编码的URL：hxxp://sahirlodhi[.]com/usr/api.txt。到目前为止，我们已经发现攻击者两次修改了api.txt，首先是加入了一个指向hxxp://bbmsync2727[.]com/upd/secure_scan.exe的链接，随后，又把这个链接修改为了hxxp://bbmsync2727[.]com/ccmb/ssm.exe。

我们分析了这个模块后发现，其downloader的逻辑是从一个硬编码URL：hxxp:// sahirlodhi[.]com/usr/api.txt获取文件，这个地址很可能是一个被攻破的网站。这个模块会认为在先前获取到的URL上储存着另一个URL，最开始，我们发现的URL是：hxxp://bbmsync2727[.]com/upd/secure_scan. exe (md5: e456d6035e41962a4e49345b00393dcd)。这个有效载荷是一个MSIL/Crimson Downloader变种，在执行时，会通过下载一个新的控制器/协调器重新刷新Crimson的生命周期。

**secApp**

我们分析的secApp(md5: ccfd8c384558c5a1e09350941faa08ab)在功能上与初始downloader非常类似，但是，secApp发送到CC的初始beacon是doupdat，而不是updatc，并且会连接到相同的硬编码CC，而不是另一个端口。除了支持CC发出的updatc命令外，这个模块还支持下面的命令： info，upsecs和upmain。info命令支持与主RAT模块相同的功能，而upsecs和upmain允许控制器修改secApp和mainApp的路径和应用名称。

**凭证窃取工具**

pssApp是一个密码收集模块，这个模块最初的时候支持获取Chrome，Firefox和Opera浏览器中保存的密码。成功收集到的凭证会储存在一个硬编码位置，例如：`%APPDATA%\Roaming\chrome\chrome_update`。如果没有找到任何凭证，凭证日志中就会简单的记录“`Not Found> > <`”。图28中表示成功窃取到凭证。在我们的有限测试中，这个模块无法收集Opera 35.0.2066.68或Firefox 44.0.2中的密码，但是能够收集Chrome 48.0.2564.116 m中的密码。

![p28](http://drops.javaweb.org/uploads/images/9f74ddf985da26732a868d262c30dbd347e1b0e6.jpg)图28-pssApp模块成功收集到凭证

有些样本(md5: 8a991eec65bd90f12450ee9dac0f286a)似乎也支持从Windows Live，FileZilla，Vitalwerks动态更新客户端 (DUC)和Paltalk中收集凭证。

**Keylogger**

键盘记录模块很基础，键盘输入会记录到一个明文文件中（图29），储存在一个硬编码位置。我们分析的键盘记录模块 (md5: f18172d7bb8b98246cb3dbb0e9144731)会把键盘记录保存到%APPDATA%\NVIDIA\位置下的“nvidia”文件。

![p29](http://drops.javaweb.org/uploads/images/ce6be034ab5ad8f6adc41e444270eaba2774d1bd.jpg)图29-“nvidia”文件中储存的记录

**USB模块**

如果发出了updatu 或 usbwrm命令，USB磁盘模块就会被下载并设置在下次开机时启动。我们分析的这个有效载荷似乎只会在可移动磁盘上搜索潜在感兴趣的文件，并将其复制到本地磁盘上，以便后续传输。这个有效载荷配置了一系列的文件扩展（图30），用于搜索USB磁盘上符合要求的文件。如果找到了感兴趣的文件，这些文件会被复制到本地磁盘上的某个指定目录，而已经复制的文件列表会记录到一个单独的日志中，这样就不会导致重复复制某个文件。但是，这种避免重复的方法只是根据文件名称来判断，所以如果某个文件的内容发生改变而名称没有变化，那么修改后的文件不会被提取。虽然说这个有效载荷可以通过命令下载，由此来看，这个有效载荷可能具有“蠕虫”功能，但是，实际情况并不是这样。

**remvUser**

在我们研究期间，我们没有找到这个模块；所以我们也无法确定其功能。我们猜测，这个模块可能是一个木马清理工具。

**Python/Peppy**

Peppy是一个基于Python的RAT，经常与MSIL/ Crimson一起出现。Peppy会通过HTTP协议进行CC通讯，利用SQLite来执行其内部功能，并跟踪向CC传输的文件。Peppy的主要目的是使用可配置的搜索参数开头，自动地将感兴趣的文件传输给攻击者（图30）。文件传输使用的是HTTP POST请求（图31）。

![p30](http://drops.javaweb.org/uploads/images/53103af2508bcc9ea621e3502f4b27a9ed12bc9a.jpg)图30-Peppy的可配置搜索参数

![p31](http://drops.javaweb.org/uploads/images/200aca9b5f8f95dfe016f2271779b9a3e1af86bd.jpg)图31-Peppy正在提取文件

除了键盘记录和文件窃取功能，Peppy还能够接收CC发送的命令，从而自我更新，自我禁用，窃取指定的文件，自我卸载，执行shell命令，获取屏幕截图，生成逆向shell，下载远程文件并执行。

另外，我们还发现了一个基于Python的简易downloader(md5: 82719f0f6237d3efb9dd67d95f842013)，从这个downloader的功能代码与Peppy download_exec 例程之间的相似性来看（图32，图33），这个downloader很可能是Peppy的作者编写的。

![p32](http://drops.javaweb.org/uploads/images/7a83d5753665a0d9c1a4dc3b119b1ca26f74adba.jpg)图32-Python downloader的代码

![p33](http://drops.javaweb.org/uploads/images/6619a3f32e84ff2e5938da321bc97feebfd180e1.jpg)图33-Peppy download_exec 例程和MyURLOpener类

0x05 总结
=======

* * *

很显然，在这些攻击活动中，存在有大量的共同线索。我们已经在不同的活动，攻击载体，有效载荷，甚至是基础设施之中发现了联系，但是，还会有更详细的信息会随着时间的推移而出现。在短期来看，我们要时刻牢记，不要局限于表面，攻击者（无论是政府还是个人性质）会利用各种各样的网络工具来实现他们的目的。