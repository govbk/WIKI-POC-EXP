# 勒索软件Locky最新传播载体分析——中文版Office危在旦夕

**Author：360天眼实验室**

0x00 引子
=======

* * *

人在做，天在看。

勒索软件，飘荡在互联网上越来越浓的一片片乌云，从中爆发出的闪电随时可能击中一般的用户。基于比特币的匿名支持体系使勒索软件这个商业模式轻松完成了闭环，各种数字绑票生意开始蓬勃兴起，而Locky勒索软件家族可能是其中最贪婪粗放的一个，漫天撒网以期最大范围地捞取不义之财。

360天眼实验室自然会对Locky重点关注并做持续的跟踪，基于360威胁情报中心的数据，以下的热力图显示了从2015年11月以来Locky样本量的提交情况。可见，2016年3、4月有两波大规模的行动，刚开初的5月甚至出现了高于4月的提交量。事实上，2016年5月3日的行动可能是史上最大规模的一波攻击。

![](http://drops.javaweb.org/uploads/images/c90127937d230899a1bcde118ee5f99406238734.jpg)

而在近两日，360天眼实验室捕获了一批最新的Locky勒索软件的传播载体，和大多数的样本一样，这批样本同样使用Word中的宏代码下载执行Locky勒索软件：

*   Word文档中被插入了恶意的宏代码
*   受害用户打开Word文档后并允许宏代码执行
*   恶意宏使用Microsoft.XMLHTTP对象从指定的URL下载勒索软件并保存为hendibe.exe
*   最后调用Shell.Application来执行恶意软件

值得注意的是，该系列样本中的宏代码是大量具有正常功能的宏代码，而攻击者将恶意代码分散插入到正常的宏代码中，如果不仔细观察，很难察觉到正常的宏代码中包含恶意代码。并且恶意代码中将需要操作的对象名称混淆编码后隐藏在了控件UserForm2.Image1的ControlTipText属性中，下载URL也通过加密的方式保存，这样具有比较好的免杀效果，VirusTotal上仅有6家杀软可以查杀更是证明了这一点！

**有意思的是中文版Office以及大部分非西文版Office软件对该系列样本天生“免疫”（不会触发恶意宏代码），这批样本的目标应该不是针对中国的，但是量身定制的版本可能已经在路上了**，接下来我们对该系列样本进行一些简单的分析。

0x01 样本分析
=========

* * *

360天眼实验室此次捕获到的样本分别有doc和docm两种文档格式，攻击者以此来保证Office 2003、Office 2007以及更高版本的Office软件用户能执行对应的宏代码，但是所有样本的内部功能都一致，所以我们使用.docm的恶意文档作为分析案例。

免杀效果
----

先附一张VirusTotal的查杀图，可以看到大部分杀软对这批样本都无法正确识别其恶意性：

![](http://drops.javaweb.org/uploads/images/01479078265e421a417f0e5adc1eae41732e77d0.jpg)

正常的宏代码
------

查看文档中的宏代码我们可以发现，宏代码中基本上都是一些数学公式代码，并且还有函数说明等相关注释，看起来都是正常的。如图：

![](http://drops.javaweb.org/uploads/images/6484db2724cf061fb211b910ad229e952810d10b.jpg)

隐藏在ControlTipText中的数据
---------------------

不过，有一段代码引起了我们的注意，代码显示从Image1控件的属性中读取了某些数据，并进行了一些操作，如图：

![](http://drops.javaweb.org/uploads/images/8ece6bea6ae638750fc7ebabb6ff3bd2f68fe9d6.jpg)

而sOvet_FATSO函数的功能就是Replace：

![](http://drops.javaweb.org/uploads/images/d9867013619f750e16fa439ceddb907acf74780d.jpg)

通过分析这段代码可以理解到大概的功能是这样的：

读取UserForm2.Image1控件的ControlTipText属性得到一个字符串，然后使用sOvet_FATSO把00替换为e，再把D!替换成M、bri替换成s，最后将字符串以10分隔，使用split生成数组。

提取UserForm2.Image1. ControlTipText中的字符串如下：

`D!icrobrioft.XD!LHTTP10)Adodb.britr00aD!10)brih00ll.Application10)Wbricript.brih00ll10)Proc00bribri10)G00T10)T00D!P10)Typ0010)op00n10)writ0010)r00briponbri00Body10)briav00tofil0010)\hendib00.00x00`

使用前面的替换方法替换后，字符串变成这样：

`Microsoft.XMLHTTP10)Adodb.streaM10)shell.Application10)Wscript.shell10)Process10)GeT10)TeMP10)Type10)open10)write10)responseBody10)savetofile10)\hendibe.exe`

可以看到，字符串中出现了恶意宏中常常使用的一些关键对象名和方法名，那么这段看似正常的宏代码可能就不那么“正常”了。

恶意宏代码执行流程
---------

1通过对宏代码的进一步分析，我们明白了这是一个通过向正常的宏代码中插入恶意宏代码，并将关键的string混淆，以及将下载的URL加密存放来躲避杀软查杀的恶意Word文档。

恶意宏代码的执行流程如下：

1、读取`UserForm2.Image1.ControlTipText`中的字符串并替换指定的字符

`Microsoft.XMLHTTP10)Adodb.streaM10)shell.Application10)Wscript.shell10)Process10)GeT10)TeMP10)Type10)open10)write10)responseBody10)savetofile10)\hendibe.exe`

2、用Split将得到的字符串以10分割成数组传递给`sOvet__57`

`sOvet__57 = Split(asOvet, "10)")`

3、通过CreateObject等函数引用sOvet__57数组中的各个成员

![](http://drops.javaweb.org/uploads/images/6699da2c302b8910cfbfe06dc4e107231e34b70e.jpg)

4、将加密的URL每个字节除以16进行解密

![](http://drops.javaweb.org/uploads/images/55d87e890d931546b4161e26b2832d2c08927ec0.jpg)

5、执行下载流程

*   使用Microsoft.XMLHTTP下载文件
*   使用Adodb.streaM的savetofile方法保存写入到TMP目录，并命名为hendibe.exe
*   最后使用Shell.Application来执行下载的EXE

解密URL
-----

样本以“?”作为分隔，使用Split生成数组，再传递给解密函数解密。但是我们在调试过程中发现，样本的宏代码中，Split函数最后缺少了闭合符号”，导致样本执行报错：

![](http://drops.javaweb.org/uploads/images/c576e0d3945895df1a248321552ebd2769addc1d.jpg)

将Split后面的”加上后再解码出来的URL却是乱码：

![](http://drops.javaweb.org/uploads/images/d80b2c74eb264ba53658c2f68b22074a8846b8b2.jpg)

对于这种情况，刚开始我们认为这应该是攻击者还在测试样本的免杀能力，因为正常情况下这样的代码是不可能执行起来的，并且即便执行成功，得到的URL也是错误的，不可能下载得到恶意软件。

0x02 中文Office天生“免疫”
===================

* * *

二进制中提取原始加密数据
------------

正当我们准备结束这次分析，得出该系列样本是攻击者进行免杀测试的样本的结论时，我们顺便看了一下样本二进制中加密的URL数据，居然发现原始二进制中的加密URL数据和Word宏代码中显示的数据不一致，而二进制中加密URL的分隔符并不是”?”，而是0xA8：

![](http://drops.javaweb.org/uploads/images/04610ca6e76973eab26aad0e179dbc9199219083.jpg)

而Word宏编辑器中显示的加密的URL数组是这样的：

`Split("1664?856?856?792?28?52?52?840?680?728?888?616?824?728?776?824?600?840?36?552?904?552?824?600?840?792?552?584?616?36?584?776?744?52?96?12?936?648?80?568?760?744?744?776?680", "?)`

可以看到，对应的”?”其实是0xA8，而0xA8后面的字节也被Word“吞噬了”，这样导致显示出来的数组通过宏代码中的算法无法解密！

VBA的“BUG”
---------

原来，VBA中使用ANSI编码，上面的代码在英文版Office中是没有问题的，VBA会正确地识别0xA8为分隔符，而在中文Office环境或者其它非西文的Office环境下则会将0xA8后面的字节一并处理。

找到原因后，我们将0xA8替换成可见字符空格0x20，并以0x20作为分隔符，成功解密出了URL：

![](http://drops.javaweb.org/uploads/images/a2b265e56402161a69fa409f2879fa9fd99e9429.jpg)

使用该地址能成功下载回来一个EXE文件，经过简单分析发现该EXE是勒索软件Locky家族的样本。

下载的Locky简单分析
------------

简单分析该样本发现执行流程和大多数的勒索软件一致，这里就不进行详细的分析了，样本大致的行为如下：

1、样本执行后反连C&C服务器进行通信

109.73.234.241:80  
185.22.67.108:80

2、读取用户机器环境信息，并生成身份ID

3、POST用户机器信息到C&C服务器

![](http://drops.javaweb.org/uploads/images/cc92ebb12a195d4f986c282f3f4b897fde59103c.jpg)

4、获取公钥信息并加密对应文件

5、释放vssadmin.exe删除所有副本文件

`vssadmin.exe Delete Shadows /All /Quiet`

6、生成勒索提示文件，更改桌面

![](http://drops.javaweb.org/uploads/images/2dd6e03c09a49aeb4af5c3e7f2a7f422b631e189.jpg)

0x03 结束语
========

* * *

在我们的文章完成时这类样本的所有下载地址均有效，基于360威胁情报中心监测数据，这类样本在5月6日第一次被监控捕获到，后续很可能会迎来一轮的增长：

![](http://drops.javaweb.org/uploads/images/5ab9939e7cca3d9ddb3db836abcb95e0a11b34cc.jpg)

而国内用户则不能因为此次中文Office天生“免疫”这批攻击样本而掉以轻心，可以预见未来勒索形式的恶意软件会更多的被黑产团队使用，对付这类攻击目前依然只能以预防为主：安装杀毒软件、定期备份重要文件、打开陌生的邮件附件一定要多加小心。

0x04 IOC
========

* * *

以下IOC数据供安全业界参考：

| 类型 | 值 |
| --- | --- |
| C&C IP | 109.73.234.241:80 |
| C&C IP | 185.22.67.108:80 |