# 从一条微博揭秘"专黑大V名人"的定向攻击

0x00 前言
=======

* * *

本月初微博上有知名大V晒出一封私信截图，私信是以某记者名义发出，要求采访该大V博主，并提供了一个网盘链接作为“采访提纲”。当博主下载网盘中存放的所谓“采访提纲”后，该文件被360安全卫士检测为木马进行清除。

我们根据截图中的网盘链接下载了伪装“采访提纲”的木马进行分析，发现这是来自于一个长期从事木马植入与数据窃取的不法黑客团伙，该团伙利用盗取或冒名的各类账号，对账号关联人发起攻击，木马功能包括录音、远程上传或下载任意文件、服务管理、文件管理、屏幕监控等，很明显是意图窃取数据进行勒索或售卖来谋取利益。

![p1](http://drops.javaweb.org/uploads/images/0260189e8506e0d7cf2f696d6b5c7887d2311775.jpg)

0x01 样本信息
=========

* * *

![p2](http://drops.javaweb.org/uploads/images/9f55d6daaae62ab4f23a70aa039dffb9e9f1b155.jpg)

0x02 样本流程图
==========

* * *

![p3](http://drops.javaweb.org/uploads/images/0c05082bc417430adffa4d99d87673279e8a8dd8.jpg)

0x03 样本详细分析
===========

* * *

**>> XXXX采访提纲.exe<<**

木马作者将自己的样本做成一个word文档的样子。不管从图标还是名字上面来看都是word的样子诱导用户去点击查看。但是这个却是一个exe程序。该exe程序运行时首先会在C盘下面尝试写一个空文件，看是否能够写入成功。如果写入成功他就会删除该文件，然后开始执行一系列操作来在安装自己。首先释放大量文件，作者将自己的文件夹设置为了隐藏。如果我们的文件夹选项中没有勾选显示隐藏搜保护的操作系统文件我们是看不到的。

![p4](http://drops.javaweb.org/uploads/images/25c35f4b7ce1de6b4880301cd02146d6c797c355.jpg)

释放文件完毕后接下来会创建VSTquanjuhe.com这个可执行文件，VSTquanjuhe进程会运行explore来打开`C:\OA`路径。弹出一个空的docx文档。(ps:测试没有装word，所以这里比较尴尬，没有word图标)

![p5](http://drops.javaweb.org/uploads/images/3ca4968929fe96b1ff2b4f36983f58b3de23114d.jpg)

接下来用ua.exe这个程序来解压links.ini文件，解压密码为”█噎冪蕟嚄Щ暜囖醃∷滸濤∑”,解压后判断判断系统是多少位的如果是32位的就运行Win1.bat文件，如果是64位的就运行Win2.bat(Win2.bat内容和Win1.bat内容相似，只是不再判断是多少版本的系统)

**>> Win1.bat <<**

该文件的内容主要是先判断是否存在swapfile.sys文件，来判断操作系统版本的。如果存在就将test1.pfx重命名为2016mt.1r放到`C：\Windows`目录下，否则就将test2.pfx文件重命名为2016mt.1r放到`C：\Windows`目录下.接下来 调用regedit.exe来运行ua.lnk→运行mew.1r→msg 系统需要升级→关机重启

**>>ua.lnk<<**

写入注册表，并关联文件。将.1r文件与”VBEFile”文件相关联以及将.3f文件与”inifile”文件相关联。使这两种后缀的文件能按vbe和inf文件的形式打开。

**>> mew.1r <<**

该文件是一个被加密了5次的vbs文件，源文件打开看到的像是一堆乱码.

如图:

![p6](http://drops.javaweb.org/uploads/images/d0dbd5e24a5d4576859a7eef6ea2c8c8203d7cdf.jpg)

最后解密到的脚本内容

![p7](http://drops.javaweb.org/uploads/images/8cbc72e9e8d0a4db2207bad114090e416253c35f.jpg)

解密后的vbs文件的主要功能就是模拟鼠标去点击运行`C:\$NtUninstallKB1601A$\BinBackup\MYTEMP`文件下的8.3f文件

**>> 8.3f <<**

在RunOnceEx下写入了一个注册表，开机时就启动2016mt.1r(vb文件)文件。

**>> 2016mt.1r <<**

开机后运行2016mt.1r→0s.bat文件→调用regdit运行lang2.lnk→解压abc1601.bat→运行shotdown

**>> os.bat <<**

用abc.os文件去覆盖qmvext.db文件，该文件时用来存放规则的文件。写入规则后的文件就不会被查杀了。这里作者用自己的数据文件替换用户的数据文件。就是为了绕过腾讯管家的查杀。不过这个漏洞在2013就在乌云上报道过了。

**>> lang2.lnk <<**

通过调用`regeedit /s`来执行reg文件。该文件的主要作用是关联文件以及在注册表在Active Steup下的StubPath键下写入了`C:\\$NtUninstallKB1601A$\\BinBackup\\super.inf`，写入注册表写入后，super.inf文件会在操作系统启动后第一时间启动。比任何一个程序都要先启动。

**>> abc1601.dat <<**

abc1601.data是一个被加密了的压缩文件。解压密码为“▓羋奤柒♀懋髖瓊♂蠟蕙纗▓ ”。解压后出现一个shotdown文件，然后ua.exe会运行shotdown文件，shotdwon释放FreeImage.dll文件,接下来FreeImage.dll会释放出并运行FreeImage.exe

**>> FreeImage.exe <<**

该文件是先将自己写的函数的地址写入在程序中，这样就提高了分析者对样本分析的难度

![p8](http://drops.javaweb.org/uploads/images/dd82c7296845ffd64d1f5d9b90bb2ba8a380291a.jpg)

将地址写死在程序中后，通过对寄存器的调用来调用自己写的函数。一直在不停的call eax来调用函数

![p9](http://drops.javaweb.org/uploads/images/a38a4d81d6edadd0007633c0067019db94ae8c14.jpg)

在对该远控功能分析的时候，我们发现该远控具备的功能大概如下

```
录音
远程上传以及下载文件
服务管理
文件管理
屏幕监控

```

该远控主要通过注入svchost进程来启动。下面就是他的注入过程。先以管理员权限运行svchost.exe

![p10](http://drops.javaweb.org/uploads/images/a35d1b295b03b47e2e75952306f291ec2b331775.jpg)

接下来就对他进行注入了。先调用WriteProcessMemory函数对svchost.exe写入数据，接下来调用SetThreadContext函数来设置EIP然后调用ReumeThread来恢复线程

![p11](http://drops.javaweb.org/uploads/images/38ae58e8d02e4a78b39f72041e0f42c241eff4e5.jpg)

通过新设置的EIP我们找到了被注入的svchost.exe的入口地址(通过对写入文件前下CC断点),用OD附加后调试发现。被注入的文件就是FreeImage本身。如果注入成功，FreeImage就结束运行。不过不管注入成不成功svchost也会发起数据链接，结合在动态分析对该远控功能的分析和对数据包结构的分析。可以看出，该远控是一个灰鸽子改版过来的RemoteABC远程控制软件

![p12](http://drops.javaweb.org/uploads/images/ba76712ba6a4d1b31794d919e526edca516e010c.jpg)

图.上线包

如果系统版本不是win8及其以上,则2106mt.1r是由test1.pfx解密而来文件主要内容如下

运行os.bat(覆盖腾讯信任文件数据库文件)→解压abc.data→解压inst.ini→运行会释放出远控的shotdown.exe→调用regedit.exe运行lang1.lnk→重启电脑

**>> inst.ini <<**

解密后得到的文件是作者事先写好的360卫士的信任区数据文件和一个安全工具及其相关的组件

**>> lang1.lnk <<**

lang1.lnk将bmd.vbe写入了启动项里面。写入后会开机自启动，启动后运行bmd.vbe

**>> bmd.vbe <<**

bmd.vbe文件也是被加密过5次的vbs文件，它主要运行ub.lnk以及gsxt.bat

**>>ub.lnk<<**

ub.lnk解密mtfile.tpi文件。并执行ing.exe文件

**>> gsxt.bat文件主要内容<<**

gsxt.bat通过调用一个rootkit工具，删除替换杀软的信任区文件，从而将木马加入用户的信任区。尽管该木马专门针对360安全卫士进行破坏，试图躲过查杀，但360多重防护体系的“下载保护”将木马直接报毒清除，使其无法运行起来，从而有效保护了用户避免中招。

0x04 木马背后
=========

* * *

在我们捕获的同族系样本中，还发现一个命名为“left and right base trigger, left and right bumper s136mould20000pieces.exe”的样本。该文件属于工程技术类文档，而图标则是一个文件夹图标。与上面分析的样本不同的的是，它是在OA文件夹下释放的，并且不再是Word文档，而是四个STEP文档。STEP文件是一个国际统一的CAD数据交换标准，根据这四个STEP文件内容来看，是针对SolidWorks 2014这款软件的。

![p13](http://drops.javaweb.org/uploads/images/875c056b3f7338ca28a261c3c233630c28e77d07.jpg)

这个木马团伙最近一段时间，使用远控控制服务器，均是位于青岛的阿里云服务器中心。

两个木马使用的远控上线地址：

![p14](http://drops.javaweb.org/uploads/images/a036f6beadeaced9713d4b51833b75f495e0aeb6.jpg)

下面是近期该族系传播比较多的几个变种，涵盖多个行业：

| 木马传播文件名 | 主要传播方式 | 木马传播主要针对人群 |
| :-: | :-: | :-: |
| 2016年样片拍摄方案及费用1.exe | 聊天软件 | 摄影师、模特等从业人员 |
| 大道包装钢平台技术要求1208.exe | 邮件 | 工程项目相关从业人员 |
| 12-8日操作建议.exe | 聊天软件 | 股票证券相关从业人员/炒股人群 |
| 核实一下账户信息.exe | 聊天软件/邮箱 | 银行业相关从业人员/财会人员 |
| 超级3m汇款单.exe | 网盘 | 金融理财人群 |
| 新出楼盘.exe | 聊天软件 | 房地产相关从业人员/有房屋买卖需求人群 |

不难发现：木马的文件名、传播渠道、针对人群这三组指标都有极高的统一性，这明显不是那种常见的“撒网捕鱼”式的木马，而是前期先获取到一部分人的邮箱、通讯软件、社交平台等账号密码，之后人工分析原账号持有者的社交圈和社交习惯，再根据分析结果定向发送定制的木马程序，增加木马投放的成功率，同时也方便更有目的性和更高效的窃取中招用户机器上的资料。植入中招用户机器中的是远控木马而不是普通的盗号木马，这样也是更方便认为的控制要获取的资料，目的性进一步提高。

关系草图大体如下：

![p15](http://drops.javaweb.org/uploads/images/4474dfb82aab640a2947362e0d04ed3b59e8e864.jpg)

这里只是将已经展现在我们面前的第一层关系图画出来，不难发现在这种有人工参与的目的性极强的攻击方式下，很容易的形成一个链式反应。只要参与运营的人手够多，就足以在短时间内掌握大量的特定行业内部信息——而这能换取的经济利益显然是巨大的。

0x05 总结
=======

* * *

此类定向木马具有明显的专一性，需要较高的人工参与度，所以传播方式并不是传统木马的以量取胜，而是转变为定点打击的精准小范围传播。虽然成本更高，但显然收益也更加可观。同时避免大规模的传播也就等同于降低了被各大安全厂商云安全机制发现的风险。

应对此类木马，安全软件的查杀固然必不可少，用户的自我防范意识也必不可少。对于好友突然发来的文件，也要多加注意。安全软件已经提示风险的文件，切莫随意打开。广大网民也要注意自身的账号安全，对于泄漏的密码要及时废弃，以防自己的账号成了木马团伙攻击的武器。360互联网安全中心也会继续关注该木马家族的发展，积极提供应对方案，保障网民安全。