# 逆向浅析常见病毒的注入方式系列之一-----WriteProcessMemory

**Author：卫士通攻防实验室(ADLab@westone.com.cn)**

0x00 引言
=======

* * *

顾名思义，注入这种技术就是将代码或DLL注入到另外一个正在运行的进程中，以实现隐藏自身或其他目的。常见病毒根据其需求会选择不同的注入方式，但每种注入方式都是值得我们了解和学习的。本系列文章打算把常见病毒的注入方式分门别类地进行汇总，在每个类别中选择一个有代表性的病毒，逆向分析该病毒的注入方式，并展示给各位读者，以供大家学习和参考。

作为本系列的第一篇，笔者将介绍利用WriteProcessMemory()函数进行的DLL注入。作为该类注入方式的代表DesktopLayer.exe也很具有分析价值，下面开始进入正文。此外，笔者忠心希望本系列能给读者一点启发和帮助，但由于笔者知识有限，才疏学浅，文中不当或错误之处还请各位读者包容和指正。

*   分析工具：IDA，OD，CFF等。
*   分析环境：Win7 x86 Vmware
*   样本地址：百度能搜到一堆，实在弄不到，再联系笔者吧。

0x01 样本概况
=========

* * *

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Name</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DesktopLayer.exe</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Size</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">55.00 KB (56320 bytes)</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">MD5</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">FF5E1F27193CE51EEC318714EF038BEF</td></tr></tbody></table>

该病毒是近一两年出现的，功能全面，结构合理，是个不错的分析和学习对象。为了让读者更顺利的进行分析和学习，笔者在2.1-2.3节逆向分析介绍了实现注入之前的代码功能，如果对这部分不感兴趣或是不打算逆向这个样本，可以直接跳到2.4节。

0x02 详情分析
=========

* * *

一、 脱壳
-----

### A. 一层脱壳

样本被加了UPX 2.90壳。UPX壳最主要的目的是减小程序的体积，其特点是较高的压缩率和较快的解压速率，与TMD、VMP这类壳的设计理念完全不同，这类壳更注重对代码提供保护的壳。UPX是免费软件，其官网上可以找到每个UPX版本的加壳程序和相应脱壳程序，网址为http://upx.sourceforge.net/。这里笔者也懒得去网上翻了，直接手动脱壳就可以了，其脱壳后的入口点模样如下：

![pic1](http://drops.javaweb.org/uploads/images/2af699c2fc8b0540a622003d2a3853bec5714e19.jpg)

### B. 二层脱壳

脱壳之后的样本仍然压缩了大量的代码，深入分析之后，可以判断为是变形UPX壳。由于UPX是开源的，所以很多同行会根据需要修改UPX的源代码。该变型壳首先解码UPX解码部分的代码，然后利用UPX的解码代码再次解码恶意功能的代码。其中，第一次解码完成后，会跳入该地址继续执行，该地址与3.1.1节所述的UPX代码基本相同，等完成其解码之后，可以再次Dump，其最终的入口点如下：

![pic2](http://drops.javaweb.org/uploads/images/93359e21b393c1d5b8b9c71c95b84974277ef722.jpg)

经过二层脱壳之后，会发现样本的图标已经改变：

![pic3](http://drops.javaweb.org/uploads/images/bc1fcf9b17d5f81b0a2710358e713590dd998e66.jpg)

图中左侧为原始图标，右侧为完全脱壳之后的图标。

二、 第一次执行分析
----------

当正确地脱掉两层壳之后，就会看到这段程序原本的模样：

![pic4](http://drops.javaweb.org/uploads/images/6cbd9aa7185b21829eb3e264644b9683452a9ea2.jpg)

下面开始着重分析其功能，首先是获取测试机的默认浏览器及其位置，其获取方式是查找注册表中，`HKCR\http\shell\open\command`的键值：

![pic5](http://drops.javaweb.org/uploads/images/a1e62f40a07e13ed099aa5f4c063c92fb2ed9a81.jpg)

在笔者分析机中，该值为：

![pic6](http://drops.javaweb.org/uploads/images/e6642e4ae412ecad9bba55c8c8cf7940f82eff98.jpg)

即默认的IE浏览器，位置为C:\Program Files\InternetExplorer\iexplore.exe。而后会通过FindFirstFile()函数判断是否存在该文件，即iexplore.exe：

![pic7](http://drops.javaweb.org/uploads/images/9d36ca77f9f28e32a03fa6e4e2e0928070f08799.jpg)

如果不存在，那么会在几个默认位置进行查找：

![pic8](http://drops.javaweb.org/uploads/images/00addac320d6d88cea886e0f58eb5a50af18f1bf.jpg)

如果存在，则继续后续操作。接下来会创建互斥体。进而，会通过GetModuleFileName()函数获取自身执行体所在位置和文件名：

![pic9](http://drops.javaweb.org/uploads/images/c31c1c808078e4a701b7e4669d99f27db72ddffc.jpg)

进而会将自身执行体的文件名与DesktopLayer.exe比较：

![pic10](http://drops.javaweb.org/uploads/images/38207ca334cbc78bbb41472577cc40b0b9372895.jpg)

由于笔者获取到的样本名字是dnf_srv.exe，显然与之不同。那么，样本会以此判断以下7个目录是否可以有读写权限：

1.  %ProgramFiles%
2.  %CommonProgramFiles%
3.  %HOMEDRIVE%%HOMEPATH%
4.  %APPDATA%
5.  SystemDirectory
6.  WindowsDirectory
7.  TempPath

当找到第一个有权限的目录是，在该文件夹下创建名为Mirosoft的文件夹。在笔者的测试机中，%HOMEDRIVE%%HOMEPATH%是有相应权限的，即会在C:\Users\zzz目录下，创建Microsoft文件夹。并将dnf_srv.exe重命名为DesktopLayer.exe，并复制到C:\Users\zzz\Microsoft文件夹下：

![pic11](http://drops.javaweb.org/uploads/images/2a8496349004817339ed9cba0704de93ac59ce1b.jpg)

![pic12](http://drops.javaweb.org/uploads/images/5d37e1bd6caf2769bae757f842957a41b0d082af.jpg)

此后，调用CreateProcess()创建该进程：

![pic13](http://drops.javaweb.org/uploads/images/eb0b339a2d7cdd08de80e64ed21f5ea25f1ed97f.jpg)

创建该进程之后，程序就调用ExitProcess()退出了。

三、 第二次执行分析
----------

此次执行一直到比较执行体名称的位置之前，都没有任何变化。而与DesktopLayer.exe比较之后，出现了不同行为。首先是，对ntdll.dll中的ZwWriteVirtualMemory()进行hook操作：

![pic14](http://drops.javaweb.org/uploads/images/18529906be45a12d9996c23903b63cb4dd65f65a.jpg)

其操作结果为：

![pic15](http://drops.javaweb.org/uploads/images/987a1e016207e1b611e93ec79f063346a49272b4.jpg)

而后，会调用CreateProcess函数，启动iexplore.exe进程，该进程的执行体所在位置已于上文中通过查询注册表方式找到：

![pic16](http://drops.javaweb.org/uploads/images/7e667c0106a9ff7c55903a7a6427919dcd11f1e3.jpg)

Createprocess()函数内部会调用ZwWriteVirtualMemory()函数，从而执行其经过hook的代码，其调用栈如下：

![pic17](http://drops.javaweb.org/uploads/images/bd32bce71c5a059e50b15c495d2fcda165f29a0a.jpg)

其中，sub_402A59即为其HookCode.

四、 HookCode执行分析
---------------

HookCode首先完成其正常的WriteVirtualMemory()函数功能：

![pic18](http://drops.javaweb.org/uploads/images/6e62f75dfa1abd30aa6a21034a02528e53846438.jpg)

进而，通过ReadProcessMemory()函数获取iexplore.exe进程的内存信息：

![pic19](http://drops.javaweb.org/uploads/images/bef139fd37c2e0f555c3ff3064ac6987f27d5e33.jpg)

根据读取到的内存，可以找到后续对iexplore.exe的hook点。

然后，在自身进程内，解码出rmnsoft.dll，手动加载，并根据导入表和重定位表进行相应的操作，最后修改页保护等操作：

![pic20](http://drops.javaweb.org/uploads/images/588f1b2a00c42991c71d4adb35f4e4f771a1e060.jpg)

当在本地加载完之后，就会把rmnsoft.dll注入到iexplore.exe，这需要分6步进行：

第一步，将DLL写入iexplore.exe：

![pic21](http://drops.javaweb.org/uploads/images/6afd74e79520599bad32d11a527502d2bf026b10.jpg)

![pic22](http://drops.javaweb.org/uploads/images/76c56226dd880355e720d12568c4b51ffdc3eb9e.jpg)

特别强调的是，在iexplore.exe中申请的内存位置和本进程申请内存的位置是一样的，这样做的好处是：避免了在iexplore.exe的重定位操作，大大减小了代码的复杂度。在笔者的测试机中，其基地址同为0x20010000，如图：

![pic23](http://drops.javaweb.org/uploads/images/54a762dbf243e5181feb428e6b46dab0d9af81ee.jpg)

第二步，将初始化导入表代码写入iexplorer.exe：

![pic24](http://drops.javaweb.org/uploads/images/7179f3ca31cda5765b962a85772393d0093a3c0a.jpg)

这里需要指出的是，代码内容主要为对PE头的进行操作的PIC代码。

第三步，将修改页保护相关代码写入iexplorer.exe。

![pic25](http://drops.javaweb.org/uploads/images/452a679bc12b23eb5913a1c27aa313072e9eda58.jpg)

该段代码的作用是通过PE头得到各个区段的页保护属性，同样是PIC代码。

第四步，将修复代码写入iexplorer.exe。

![pic26](http://drops.javaweb.org/uploads/images/bdc32a3c0a51916c04a6c8c6182e8810b451892d.jpg)

该段代码会调用第1步、第2步、第3步写入的代码。在第5步中，会执行此步骤中的代码。

第五步，将相关数据写入iexplorer.exe。

![pic27](http://drops.javaweb.org/uploads/images/50a6fa5a7afebd60b9a9224bcf38fbd98c41b83a.jpg)

第六步，在刚刚找到的hook点写入shellcode，寻找hook点的相关内容见上文：

![pic28](http://drops.javaweb.org/uploads/images/d13088b79161327a201a3f5cc0200c303564a465.jpg)

其中，shellcode内容为：BF 00 00 07 00 68 00 00 08 00 FF D7，长度为0xC。

![pic29](http://drops.javaweb.org/uploads/images/bc9b0f2102192212274148237e9ab610607a4b4f.jpg)

0x70000和0x80000分别为第3步写入的代码基址和第4步写入的数据基址。等程序运行到hook点时，会执行shellcode，从而跳到0x70000地址即第3步写入的代码继续执行进行相关操作。

至此，完整的注入过程和方法已经分析完毕。如果对这部分不是很理解，建议阅读和学习《程序员的自我修养》一书，该书中满满的全是干货。

下面看一下iexplore.exe的执行效果如何：

执行shellcode：

![pic30](http://drops.javaweb.org/uploads/images/b433eb5d186b603ef6ecd89ebb65940f7f6c2416.jpg)

然后初始化导入表：

![pic31](http://drops.javaweb.org/uploads/images/7d01090df9a27019f29f3327470102fa5201811e.jpg)

然后，分段判断并修改代码的页保护：

![pic32](http://drops.javaweb.org/uploads/images/159c2e61985eb61b8e3a2f0b36603e2b0030f07a.jpg)

最后，调用DLL main：

![pic33](http://drops.javaweb.org/uploads/images/65b4b1fbbe1ba9f1b3a8ab6e52ab23d4beca75f8.jpg)

此后，该恶意DLL会开始他的行为。

五、rmnsoft.dll分析
---------------

该DLL可以在其加载之前dump出来，这里就不做演示了。此外，该DLL并未有混淆或者加壳等措施，逆向起来比较轻松，这里就不做详细分析，只做简要介绍：

![pic34](http://drops.javaweb.org/uploads/images/b065927f77acbcaa9d2c246e07b40905bdbbf3d5.jpg)

如上图，DLL会创建5个线程，其中每个线程会实现其相应的恶意功能。

0x03 总结
=======

* * *

本文以病毒DesktopLayer.exe为样本，着重介绍了利用WriteProcessMemory()函数进行DLL注入的方法，简而言之，可以认为程序直接将所有相关的代码和数据直接写到被注入的进程空间中。其注入的DLL只在内存中出现，并未在硬盘中出现过。这种注入方式需要对PE结构有较好的理解，且对DLL装载过程有很好的理解，建议不熟悉这部分内容的读者可以阅读和学习《程序员的自我修养》，以进一步获得提高。

本系列会陆续介绍其他常见病毒的注入方式，希望各位读者能够有所收获。