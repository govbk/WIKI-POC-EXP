# 网络暗黑世界的“域影”攻击：运营商劫持LOL等客户端海量级挂马

0x00 起因
=======

* * *

从上周末开始，360互联网安全中心监控到一批下载者木马传播异常活跃。到3月7号，拦截量已经超过20W次，同时网页挂马量的报警数据也急剧增加。在对木马的追踪过程中，我们发现木马的传播源头竟然是各家正规厂商的软件，其中来自英雄联盟和QQLive的占了前三天传播量的95%以上。而在受感染用户分布中，河南竟占到了72%。

木马传播源TOP：

```
\英雄联盟\Air\LolClient.exe
\QQLiveBrowser.exe
\youkupage.exe
\QyFragment.exe
\QQGAME\SNSWebBrowser\IEProc.exe
\SogouInput\7.4.1.4880\SohuNews.exe

```

网上的用户反馈：

![](http://drops.javaweb.org/uploads/images/37eabdf1eccee3526269da56b29ada4c542cbba1.jpg)

0x01 挂马过程分析
===========

* * *

在对数据分析之后，我们确认，这次攻击事件和去年通过视频客户端挂马是同一个团伙所为，使用的技术手段也比较相似。（《祸起萧墙：由播放器引爆的全国性大规模挂马分析》[http://blogs.360.cn/360safe/2015/06/26/trojan-pass-player/](http://blogs.360.cn/360safe/2015/06/26/trojan-pass-player/)）**本次木马传播，主要是通过运营商（ISP）对用户的网络访问做内容劫持，在html代码中插入一段iframe的广告代码所引起的。在这段广告代码中，为客户端引入了带挂马攻击的flash文件。而国内仍有很多桌面客户端使用旧版带有漏洞的flash插件，如英雄联盟，QQLive等。flash的漏洞，造成了这些客户端本身易受攻击，而客户端本身也没有做安全防护，没有对通信进行加密，在ISP的攻击面前不堪一击。**如果用户计算机此时又没有安装带有漏洞防护功能的安全软件，就会造成用户计算机被感染。

从联系到的用户那里来看，用户的出口IP属于河南郑州移动网络：

![](http://drops.javaweb.org/uploads/images/0c02b16052f4bc3837ab88fca2d22d54e31565ac.jpg)

在联系用户追查问题的时候，发现用户打开任何网页的时候都有可能中毒，显然并不是特定网站被挂马导致的。该用户在打开了一个凤凰网新闻页面的时候便触发了木马，于是我们查看该网页，发现了如下代码：

![](http://drops.javaweb.org/uploads/images/f81b43c78c8ead471a4cffc2fc269bb6cb82c32e.jpg)

很显然，在一个itemscope的div元素下，出现了一个指向majore.b0.upayun.com的脚本元素和一段iframe嵌入页面。

而在分析人员自己的机器中（北京市电信）访问相同的页面，则显然没有这两个元素：

![](http://drops.javaweb.org/uploads/images/d63586add53c868dfc82319627823e844c66f8a8.jpg)

更为关键的是iframe中又嵌入了一层iframe指向muhlau.cn这个域名。为了方便查看，我们单独打开了这个页面，呈现出来的是一个看似正常的flash广告动画，但仔细看代码发现——这里面还有两层iframe嵌套，而在最里层的，是一个根本看不到的flash文件（截图中红框圈出来的就是这个看不见的flash文件的位置）

![](http://drops.javaweb.org/uploads/images/d75b6b4fa2f609e8d876e27f9f790c491facde67.jpg)

同时，查看浏览器的Network监控，也确认确实加载了这个swf文件：

![](http://drops.javaweb.org/uploads/images/7265aeeb599c4a6d24581b029992236dcd0b706a.jpg)

拿到swf文件后分析来看，本身并没有什么实质性的动画内容，反倒是含有一段经过doswf加密的脚本：

![](http://drops.javaweb.org/uploads/images/90114f5ab2047f304e9a3c0a7068512edd61f81e.jpg)

![](http://drops.javaweb.org/uploads/images/8e845a0b5f226e6de7c26057dfe1272a64bd594e.jpg)

通过抓取内存dump可以看到明显的shellcode字串以及加载shellcode的代码：

![](http://drops.javaweb.org/uploads/images/754f3fb623c7a2d22fb2a5af380b2baa058a2301.jpg)

![](http://drops.javaweb.org/uploads/images/becfa77e7c2c8487b250bf1a562170d1a291d961.jpg)

含有恶意代码的flash文件一旦被带有漏洞的flash插件展示，便会触发木马下载动作，从3g4s.net域名下获取一个可执行文件，下载到本地并执行。

![](http://drops.javaweb.org/uploads/images/e4210c44ceead6ec39841639b4be7b463f8deb73.jpg)

0x02 挂马数据展示
===========

* * *

此次挂马，攻击者通过“上海米劳广告传媒有限公司”投放的广告内容。

主要的挂马页面：

*   `hxxp://www.muhlau.cn/1/index001.html`
*   `hxxp://majore.b0.upaiyun.com/06/media_1.html`

所挂的flash木马：

*   `hxxp://www.ip.muhlau.cn/LSQZA.swf`

服务器地址：`222.186.59.36(江苏省镇江市 电信)`

截至我们发稿时，flash攻击代码已经有超过1000W次的独立用户访问。单在3月9号一天，就有**534W**独立用户访问到了挂马页面。

![](http://drops.javaweb.org/uploads/images/f4fe9b8587e4c0371935e3fea2e2e6f9199f534d.jpg)

一分钟内，有超过6800次的访问。

![](http://drops.javaweb.org/uploads/images/45a6ac544f646be34f4acfb44974892b2e955597.jpg)

挂马页面的引用来源，主要是广告主的广告跳转页面：

![](http://drops.javaweb.org/uploads/images/869cbb57c526eb2e253211793f843ce17028376d.jpg)

地区分布可以看出，河南占65%以上：

![](http://drops.javaweb.org/uploads/images/631a0ce23ff049219d603830b86e1b18531bdc4b.jpg)

防护中心3月9日，单天统计到的木马传播趋势：

![](http://drops.javaweb.org/uploads/images/4c257a3bd07eb8f3cca83f2a23a1b6a6d90c8cd4.jpg)

0x03 木马分析
=========

* * *

此次木马传播者准备了大量木马的免杀版本，在对抗过程中，高峰时木马每分钟均会更新一个版本，并针对多款安全软件做免杀处理。木马本身是一个简单下载者加广告程序，但更新极为频繁，仅3月9号一天就更新超过300次。

客户端被flash挂马之后下载执行木马的情况截图：

![](http://drops.javaweb.org/uploads/images/02220ca44f6bcc895360f3895751c577f6e2e3b1.jpg)

捕获的各种挂马程序：

![](http://drops.javaweb.org/uploads/images/4128b6c2bc320cf9b36ab47aaefc28d4d3082094.jpg)

360安全卫士拦截木马启动：

![](http://drops.javaweb.org/uploads/images/7abfdbcd42ed44403710b7da2dba0c44f71151bb.jpg)

被恶意flash文件下载到本地后以ad为参数执行；而广告程序通过判断启动参数来决定执行什么行为：

![](http://drops.javaweb.org/uploads/images/b94cde3c485d15f25e00651a998c6d75f32bb459.jpg)

同时，还会检查当前系统环境来判断自己是否在虚拟机环境中：

![](http://drops.javaweb.org/uploads/images/6b249492c6ca3e138975bb5eaccd9eb24e23a8b1.jpg)

在确认可以正常运行后，广告程序会先访问指定的推广服务器获取推广列表：

![](http://drops.javaweb.org/uploads/images/eec89b2e80408f5b96252e9cbdea715709383393.jpg)

之后则根据推广列表的内容打开一个淘宝页面来推广其淘宝店并弹出广告弹窗：

![](http://drops.javaweb.org/uploads/images/07b82ac51af03522a5317fcb0640d3e4b6d2c0f3.jpg)

![](http://drops.javaweb.org/uploads/images/84cc80827acb273f8b1b173897961d2c2989a163.jpg)

![](http://drops.javaweb.org/uploads/images/c20e6699d64412a63478230fd0bc49b0e89a7477.jpg)

写入开机启动项：

![](http://drops.javaweb.org/uploads/images/3ff856eac412eb32b93796109b4e600e11adc97e.jpg)

![](http://drops.javaweb.org/uploads/images/c4f394dedf9201417c5b623d060bb1e5eb8a2262.jpg)

安装大批推广程序：

![](http://drops.javaweb.org/uploads/images/2f690c0bff90bce5d16a7c3dd0b43cf4d865757e.jpg)

0x04 木马作者追踪
===========

* * *

在整个木马传播过程中，有3个团体参与其中。  
渠道由ISP负责，向页面中插入广告，它可以控制其全部用户。  
广告商是来自上海的米劳传媒，其控制下面几个挂马传播服务器：

```
hxxp://www.muhlau.cn/1/index001.html
hxxp://majore.b0.upaiyun.com/06/media_1.html
hxxp://www.ip.muhlau.cn/LSQZA.swf
222.186.59.36

```

真正的木马作者，控制着swf挂马文件触发之后的全部服务器：  
服务器ip：`58.218.205.91`

```
hxxp://down.3g4s.net/files/DeskHomePage_179_1.exe
hxxp://down.seakt.com/tpl.exe
hxxp://tj.takemego.com:808
hxxp://tj.kissyouu.com:808
hxxp://tj.take1788.com

```

服务器ip：`58.218.204.251`

```
hxxp://down.shangshuwang.com/tpl.exe

```

对这些服务器whois查询发现，服务器均为今年2月左右新注册域名，并且均作了隐私保护，可谓非常之狡猾。

![](http://drops.javaweb.org/uploads/images/5ff63a2c2aa9e2b4740cae45c24dda596b428308.jpg)

木马作者使用的是微软IIS+ASP的服务器：

![](http://drops.javaweb.org/uploads/images/833a52a4a57f703881977bf96ed5f17ad1e4772f.jpg)

通过挂马服务器后台发现，攻击者来自四川省南充市

**218.89.82.229（四川省南充市 电信） 2016/03/08 08:49:55  
139.203.94.136（四川省南充市 电信）2016/03/08 13:25:39  
对其进一步分析，我们获取到了木马作者的联系方式：  
作者QQ：31577675xx（主号，不常用）  
测试使用QQ5542447xx（不常用）  
1256403xx主号（常用）**

通过网上信息，可以看做作者已经从事黑产很多年了。

![](http://drops.javaweb.org/uploads/images/6c019671a389855087ef54e6adb5372220483554.jpg)

![](http://drops.javaweb.org/uploads/images/927439aba54dc3a390426501e896d9d502408487.jpg)

**还有这个团伙使用的商务推广联盟 QQ1062790099**

![](http://drops.javaweb.org/uploads/images/413ab7864979b0cf956eff3be01cb3b0d9d0f7af.jpg)

![](http://drops.javaweb.org/uploads/images/5420dcf71a11dcd28309fe2208e5547ea986e0b5.jpg)

![](http://drops.javaweb.org/uploads/images/32da66babf89ba8515f6d8652e3c8a1442569699.jpg)

**商务合作渠道QQ2797719791**

![](http://drops.javaweb.org/uploads/images/dc3373eec79cb94037581622eaf5052541023221.jpg)

通过获取到的各方面信息，我们分析出了这个推广团伙的策略手段。首先他们会通过广告商购买渠道的广告展示量，这个过程中，他们会选择一些监管不严的广告商，使自己带有木马的广告不至于被发现。其次会选取客户端软件来展示广告，由于大多数浏览器会升级flash插件，会影响其木马传播。攻击者更青睐于防护脆弱的客户端软件，最后通过传播的下载者推广软件和广告变现。

安全建议
----

做为互联网的基础服务商，运营商应该注意自身行为，切莫使自己的商业广告行为成为木马传播的帮凶；而各大客户端软件，更应该注重用户计算机的安全体验，做好自身漏洞的修复，及时更新所使用的第三方插件，不要再因为已知的软件漏洞再给用户带来安全风险；作为责任的软件厂商，也需要积极推进流量数据加密，来预防在通信过程中被劫持的情况发生；对于广大用户来说，使用一款靠谱的安全软件，开启软件的实时防护尤为重要。