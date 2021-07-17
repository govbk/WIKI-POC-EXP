# WireShark黑客发现之旅（7）—勒索邮件

**作者**：Mr.Right、Gongmo、K0r4dji

**申明**：文中提到的攻击方式仅为曝光、打击恶意网络攻击行为，切勿模仿，否则后果自负。

0x00 前言
=======

* * *

近期，越来越多的人被一种恶意软件程序勒索，电脑上的多种重要文件都被加密而无法打开，并且无计可施，只能乖乖支付赎金，以对文件解密。

![](http://drops.javaweb.org/uploads/images/95a37fc4046604d947d219875d7a09751da9c2b5.jpg)

网上关于该类病毒的详细分析案例很多，在此不再详述。本文分享主要通过WireShark从流量分析判断勒索邮件、再进行深入分析。

0x01 截获邮件样本
===========

* * *

通过监控某政府邮件服务器发现，近期大量用户收到此诈骗勒索邮件，邮件的发件人一般为陌生人，收件人指向明确，且带有跟收件人名称一致的ZIP附件，邮件内容一般为“请检查附件的XX，为了避免罚款，你必须在X小时内支付。”的诈骗威胁内容。

![](http://drops.javaweb.org/uploads/images/7fd1c0833a67f5b815f3a1d08512c12759652b15.jpg)

解压ZIP附件可发现病毒文件。

![](http://drops.javaweb.org/uploads/images/aafd4d9b96f6da2dbf63d6c711cecc849ac2bf0e.jpg)

0x02 WireShark分析
================

* * *

对于邮件协议的分析，我们首先按OSI七层模型对其数据进行建模，对网络协议的每层进行分析，最后汇总其安全性。（同样适用于其它协议）

![](http://drops.javaweb.org/uploads/images/8e197e8c0218a09cec8ebc2f2cbf360106a5fe0f.jpg)

（一） 物理层分析
---------

暂不做分析。

（二） 链路层分析
---------

由于该流量接入点为邮件服务器边界出口，所以多为SMTP数据。该数据链路层帧格式为以太帧（Ethernet II），共14字节，前12字节表示两端的MAC地址，后两字节0x0800表示后接IPV4协议。

![](http://drops.javaweb.org/uploads/images/30dbc52607c4125b9481b59fd78372261fb9809a.jpg)

此层数据无异常。

（三） 网络层分析
---------

从网络层数据开始，我们就会逐渐发现异常。当然，这个数据在网络层对我们有用的也就是源、目的IP地址。源地址10.190.3.172为邮件服务器地址，目的地址191.102.101.248 （哥伦比亚）为发件方地址。

![](http://drops.javaweb.org/uploads/images/6881fb2ed55a976d2b8e824188cc846008b0b991.jpg)

简单做几个测试，就发现有异常：

1.  191.102.101.248并未开放TCP25端口；
    
2.  191.102.101.248与elynos.com无关；
    

初步判断发件人的邮箱是伪造的。

（四） 传输层分析
---------

我们简单统计一下该数据的TCP25端口，发现在包数量等于28的附近区域，有大量不同IP发来的邮件，且字节长度也基本相等，可以初步判断大量邮箱收到差不内容的异常邮件。

![](http://drops.javaweb.org/uploads/images/69faaaa1bb30a2652bddec963b65207f2145ae19.jpg)

提取一封follow tcpstream，可看出，也是一封勒索邮件。

![](http://drops.javaweb.org/uploads/images/774598997dedb88eb0963fe98964a82bd765d8cb.jpg)

（五） 会话层分析
---------

SMTP协议在会话层一般分析要素包括：认证过程、收发关系、加密协商、头部协商等。

将一封邮件的会话Follow TCPStream，可以看出邮件的发件人是来自外部的“陌生人”。

![](http://drops.javaweb.org/uploads/images/7b648e4dc64bf11ac92a7ec3b9bc168aa03eba09.jpg)

我们将部分邮件收发关系进行汇总，可以看出虽然发着同样的勒索邮件，但其发件人地址为了躲避垃圾邮件过滤，伪造了大量的邮箱地址及域名。

![](http://drops.javaweb.org/uploads/images/068a90d7ea2cffd9c8881e07db5e1ebeb46bef79.jpg)

（六） 表示层分析
---------

在表示层分析要素一般包括编码和列表等，由于此邮件属于正常通信邮件，在表示层无异常因素。

（七） 应用层分析
---------

针对此案例，应用层分析目标包括：邮件正文内容安全、邮件附件安全、是否为垃圾邮件等。

![](http://drops.javaweb.org/uploads/images/b2c6f9c77bcc4f988c748bb4bd154d8c5e66eb18.jpg)

1.指向性：收件人邮箱名为：`voice5@X.gov.cn`，邮件正文称呼为“dear voice5”，邮件附件名称为“`voice5_*.zip`”，可看出此勒索邮件为骗取点击率，进行了简单的社工。

2.邮件正文：

“Please check the bill in attachment.

In order to avoid fine you have to pay in 48 hours.”

明显的诈骗威胁内容。

3.将此邮件内容Save一下，可得到附件内容。通过分析，可确认附件为敲诈勒索病毒。（本文不详述）

![](http://drops.javaweb.org/uploads/images/ff012498eb760db332762f981ca07c1d9c9329bf.jpg)

0x03 勒索病毒分析
===========

* * *

**（注：本章节不全属于Wireshark分析范畴）**

（一）病毒初始化文件
----------

1)病毒文件一共是6个，其中红框中的3个文件是隐藏文件，js文件是引导用户打开的文件。为了防止杀毒软件查杀病毒，病毒文件首先是按照pe结构分开的，js命令把pe文件组合在一起，构成一个完成的bin文件。

![](http://drops.javaweb.org/uploads/images/fded70a69e63dbe7251156b4a647149a75de6514.jpg)

2)组合好的病毒文件会放到`c:\User\Username\Appdata\Local\temp`目录下，然后后台运行。如下图红色框中

![](http://drops.javaweb.org/uploads/images/cfb98ae3755fd5d528186d24d875fc1828b343ab.jpg)

在IDA中打开bin文件。大段大段的加密数据文件。如下图所示：

![](http://drops.javaweb.org/uploads/images/f3a656edaa1c2d5f454c59c85bcbe5772c0cff39.jpg)

（二）病毒行为
-------

1)病毒解密还原后，才能正常执行。病毒文件经过了很多的亦或乘除等算法，通过VirtualAlloc在内存中存放一段代码，然后调用RtlDecompressBuffer进行解压，并在内存里还原代码。所有API函数都是动态调用的。下图是其中的一小部分还原数据的内容。

![](http://drops.javaweb.org/uploads/images/89999e0d0f2cdefdeb864d51a495b2423f564c84.jpg)

![](http://drops.javaweb.org/uploads/images/2daf198c24898ffc1ade9ce751061f225f575ad9.jpg)

![](http://drops.javaweb.org/uploads/images/0efb296be8aefea64422904601c98de70c36c250.jpg)

![](http://drops.javaweb.org/uploads/images/3dfe2e5e0918fd53876f287f5340d068a3c4f2cb.jpg)

2)在内存解密，申请分页，并拥有执行能力。

![](http://drops.javaweb.org/uploads/images/c0970a49dcbd88f75d71061900aba45187947425.jpg)

3)病毒会在HEKY_CURRENT_USER下创建一个属于用户的key值。

![](http://drops.javaweb.org/uploads/images/bff53115a38fb2735d8c902e3273a8e0236499ef.jpg)

![](http://drops.javaweb.org/uploads/images/b669df4432490018a021cae708bfe560c099a4ec.jpg)

![](http://drops.javaweb.org/uploads/images/56b3f54aa706f358c8f7435c398193a7acce27c8.jpg)

4)病毒会判断系统版本:从Win2000，xp 一直到最新的Win10以及Win Server 2016;

![](http://drops.javaweb.org/uploads/images/15162564dfe13513e8b8015281b6836628c03405.jpg)

![](http://drops.javaweb.org/uploads/images/501a5578252e03790a06dda9ec2255b35c96a477.jpg)

由于我们的虚拟机是win7；所以这里判断出是win7 zh代表中国。

![](http://drops.javaweb.org/uploads/images/6b5e429fa05d078be1d74c63b04e23cc2cf484c6.jpg)

病毒开始构造一个连接，准备发往作者的服务器。构造如下：

`Id=00&act=00&affid=00&lang=00&corp=0&serv=00&os=00&sp=00&x64=00;`

很明显这是在获取系统的一些信息，包括ID号，版本号，语言等。

![](http://drops.javaweb.org/uploads/images/05b754737859ed265fb4ade51089f6664bef3aa4.jpg)

病毒准备提交的网址：

![](http://drops.javaweb.org/uploads/images/b828d64b3a39bed4d8cb5098c58535723de449ed.jpg)

下面的IP地址；都要尝试连接一次。

![](http://drops.javaweb.org/uploads/images/4de023164a20af0f7c3fb9868da83ddd93701ae1.jpg)

通过wireshark截取的数据我们发现：有些IP地址的php网页已经丢失了。

![](http://drops.javaweb.org/uploads/images/346c179bb106c67ee6e8d88fc6269ead5b4acf18.jpg)

![](http://drops.javaweb.org/uploads/images/6cafd85daa4d62b794a2a354033a03eab26e50b5.jpg)

除此之外，病毒尝试连接部分c&c服务器网址，部分如下：

![](http://drops.javaweb.org/uploads/images/3046f4aa1479628f19f949452a9e248277e08b35.jpg)

5)如果病毒c&c服务器没有返回信息；则病毒一直处于等待状态。

6)感染文件。首先循环便遍历扫描文件。

![](http://drops.javaweb.org/uploads/images/09ec109e0df3a03899e8bae99a1e57b8a6acae90.jpg)

![](http://drops.javaweb.org/uploads/images/24a616b676c994f1e0b950289829fbba7bc70ed5.jpg)

下图是病毒要修改的文件格式：

![](http://drops.javaweb.org/uploads/images/8e5e915ba703f5b36683b2acdc812a29bc6ae1c8.jpg)

文件名生成部分算法：

文件名被修改过程分为两部分，前半部分代表系统的key值，后半部分通过算法生成。文件名改名加密算法的局部过程，从”0123456789ABCDEF”当中随机选取一个字符充当文件名的局部。随机函数采用`CryptGenRandom()`。

![](http://drops.javaweb.org/uploads/images/c2248abb92880336414716c7872e7ebc3e67ba9f.jpg)

文件内容加密总体流程：

![](http://drops.javaweb.org/uploads/images/0973c340acfd23b785d784d5495b9b4746c00a83.jpg)

首先文件以只读形式打开，防止其他文件访问其内容，接着通过AES-128算法加密器内容，最后置换文件。完成文件加密。

文件内容：经过AES-128位算法加密。

![](http://drops.javaweb.org/uploads/images/dfd9241a0415fe88d06c6f0a5fbd784d52303917.jpg)

打开文件

![](http://drops.javaweb.org/uploads/images/9f8076be919880ae9048996b2c8816c4ba57c75f.jpg)

把加密后的数据写回文件：

![](http://drops.javaweb.org/uploads/images/a454470622d04de2b676fd1bff098fa1797cf1ee.jpg)

然后通过API函数替换文件。

![](http://drops.javaweb.org/uploads/images/8841637d9ebf6c13f7a961e045254ffbe48c5d68.jpg)

8)桌面背景被换为：

![](http://drops.javaweb.org/uploads/images/8a7efd293b538412e9ed4fdc51e618efa1fb7803.jpg)

0x04 总结
=======

* * *

1.  此类勒索邮件标题、正文、附件内容基本相同，只是针对收件人名称稍作修改。
    
2.  为躲避邮件过滤系统，发送者邮箱使用和伪造了大量不同的IP和邮箱地址。
    
    ![](http://drops.javaweb.org/uploads/images/38c558dbbeb1282b8b68d67a53805dd7b3227f7f.jpg)
    
3.  虽然此勒索病毒最终需要通过针对附件样本的分析才能判断确认，但基于流量分析可以发现诸多异常，完全可以在流量通信层面进行归纳阻断。
    
4.  随着大量比特币病毒流入国内，各种敲诈勒索行为日渐增多，对应这种病毒，我认为防范大于修复。因为比特币病毒对文件的加密算法部分相对复杂，还原的可能性较小。并且每台机器又不一致。所以，我们尽量做好预防才是根本。以下是几点需要我们提高警觉性的：（1）及时更新杀毒软件。（2）注意防范各种不明确的邮箱附件。（3）及时备份重要信息到其他存储介质。