# SWIFT之殇——针对越南先锋银行的黑客攻击技术初探

**Author:360追日团队**

近期，孟加拉国、厄瓜多尔、越南、菲律宾等多个国家的银行陆续曝出曾经遭遇黑客攻击并试图窃取金钱事件，这些事件中黑客都瞄准了SWIFT银行间转账系统，对相关银行实施攻击和窃取。360追日团队深入分析了截获的黑客攻击越南先锋银行所使用的恶意代码样本，并由此对此次事件中的黑客攻击技术进行了初步探索。

0x00 概述
=======

* * *

随着孟加拉国央行被黑客攻击导致8100万美元被窃取的事件逐渐升温，针对银行SWIFT系统的其他网络攻击事件逐一被公开，具体如下表所示：

![](http://drops.javaweb.org/uploads/images/c5bcda884c87f72f257086f9ffe10aeddeeedf39.jpg)

表 1 针对银行攻击事件汇总

通过对相关恶意代码和攻击手法的研究，以及其他安全厂商的研究结论，360追日团队推测针对孟加拉国央行和越南先锋银行发起攻击的幕后组织或许是同一个组织，该组织可能是Operation Blockbuster所揭秘披露的Lazarus组织，中国相关机构也是该组织主要攻击目标之一。

本报告主要就越南先锋银行的相关攻击事件、样本展开深入分析，暂不深入关联孟加拉国央行被攻击事件和Lazarus组织，对相关事件或组织之间的关联归属分析等，我们在之后的关联分析报告中会有详细的介绍。

**关于Lazarus黑客组织**

2016年2月25日，Lazarus黑客组织以及相关攻击行动由卡巴斯基实验室、AlienVault实验室和Novetta等安全企业协作分析并揭露。2013年针对韩国金融机构和媒体公司的DarkSeoul攻击行动和2014年针对索尼影视娱乐公司（Sony Pictures Entertainment，SPE）攻击的幕后组织都是Lazarus组织。

![](http://drops.javaweb.org/uploads/images/29ca557a134d06020ecd6735da11cea74880b0e2.jpg)

表 2 Lazarus组织历史活动相关重大事件节点

0x01 关于SWIFT
============

* * *

SWIFT全称是Society for Worldwide Interbank Financial Telecommunication，中文名是“环球同业银行金融电信协会”。1973年5月，由美国、加拿大和欧洲的—些大银行正式成立SWIFT组织，其总部设在比利时的布鲁塞尔，它是为了解决各国金融通信不能适应国际间支付清算的快速增长而设立的非盈利性组织，负责设计、建立和管理SWIFT国际网络，以便在该组织成员间进行国际金融信息的传输和确定路由。

目前全球大多数国家大多数银行已使用SWIFT系统。SWIFT的使用，使银行的结算提供了安全、可靠、快捷、标准化、自动化的通讯业务，从而大大提高了银行的结算速度。由于SWIFT的格式具有标准化，目前信用证的格式主要都是用SWIFT电文。

1. SWIFT提供的服务
-------------

*   接入服务（Connectivity）
    
    包括SWIFTAlliance Access and Entry 、SWIFTAlliance Gateway 、SWIFTAlliance Webstation 、File Transfer Interface 等接入模式；
    
*   金融信息传送服务（Messaging）
    
    包括SWIFTNet FIN 、SWIFTNet InterAct 、SWIFT FileAct 、SWIFTNeBrowse 等传输模式；
    
*   交易处理服务（transaction processing）
    
    提供交易处理匹配服务 、实时报告的双边净额清算服务 、支持B2B的商务中的端对端电子支付等；
    
*   分析服务与分析工具（Analytical Services/Tools）
    
    向金融机构提供一些辅助性的服务，即分析服务与分析工具。
    

2. SWIFT CODE
-------------

SWIFT Code是由该协会提出并被ISO通过的银行识别代码，其原名是BIC （Bank Identifier Code）。

每个申请加入SWIFT组织的银行都必须事先按照SWIFT组织的统一规则，制定出本行SWIFT地址代码，经SWIFT组织批准后正式生效。SWIFT Code由8位或11位英文字母或数字组成。

代码格式:

*   8码长—XXXXXXXX
    
    ![](http://drops.javaweb.org/uploads/images/5c939bffd3372a58fef7c36acdfee18bfdc27777.jpg)
    
*   11码长—XXXXXXXXXXX
    
    ![](http://drops.javaweb.org/uploads/images/870871feed20c4c6adbff44c097bf697679398a8.jpg)
    

各部分的含义如下：

a. 银行代码：由四位易于识别的银行行名字头缩写字母构成，如 ABOC、ICBK、CITI 等；

b. 国家代码：根据国际标准化组织的规定由两位字母构成，如 CN、HK、GB、US、DE 等；

c. 地区代码：由两位数字或字母构成，标明城市，如 BJ、HH、SX 等；

d. 分行代码：由三位数字或字母构成，标明分行，如 100、010、CJ1、400 等，若表示总行，则使用XXX。

3. SWIFT报文
----------

SWIFT组织根据国际结算业务开展的需要，制定了相关的标准格式的报文，SWIFT的标准格式分为两种：

*   基于FIN的标准MTs
    
*   基于XML的新标准MXs
    

MTs（Message Type ，MTs通用表达式为MTnXX）：n（0～9）表示报文类型，XX表示在n类型中的分类，目前共有10类报文，应用较多的是第1、2、3、5、7、9类型。

MXs ：在1999年，SWIFT组织选择了XML编码作为新一代标准，同时决定最终应用新一代以XML为基础的标准（MXs）， 目前两种标准共存，MX标准由12类报文组成。

### SWIFT MT报文

根据银行的实际运作，SWIFT MT报文共划分为十大类：

![](http://drops.javaweb.org/uploads/images/8ee3b63c169786bfadb3854d63186ef88b9e65c1.jpg)

表 3 SWFIT MT报文十大类

SWIFT报文第1类至第8类均为押类电报，需要使用SWIFT密押。SWIFT密押是独立于电传密押之外，在代理行之间交换，且仅供双方在收发SWIFT电讯时使用的密押。其他两类属于不加押报文。

4. T950对帐单
----------

### MT950范围

这是由帐户行发送给开户行，用来说明所开帐户上所有发生额详细情况的报文格式。

![](http://drops.javaweb.org/uploads/images/70bb3931ae5396953bdf03fd525e22e8d3334910.jpg)

### MT950准则

*   费用、利息及其它调整所应用的方式
    
    1.  列明已发送的费用通知MTn90报文编号；
        
    2.  如该费用系通过本对帐单首先通知开户行，则必须符合以下条件：
        
        1.  必须用相关业务编号加以识别，如开户行原业务的编号；
            
        2.  本金必须在对帐单中单独列明。
            
*   对帐单中的金额必须与原业务中的金额一致。如有费用已在业务报文中清楚列明，或是某一报文的必要组成部分（如托收款项），则该费用不必在对帐单中特别注明；
    
*   帐户行不得将各自独立的业务并笔。如原收付报文系多笔业务，对帐单中仍应分别记帐，每笔借记均须引用原各自报文中域20；
    
*   建议在每个营业日日终，只要帐户中有发生额，帐户行就发送MT950；
    
*   为便于人工核对，建议对帐单中的发生额先按借记和贷记排列，在借记和贷记两类中分别按起息日排列，同一起息日的借、贷记中，按金额由小到大排列；
    
*   一份对帐单的内容可由数份报文组成。
    

### MT950域详述

*   域 20：发报行的编号
    
*   域 25：帐号　
    
    列明该对帐单的帐号。　
    
*   域28C：对帐单号码 / 分页序号　
    
    该域内容前后分别表示对帐单连续号码和每一份对帐单报文的分页序号。
    
*   域60a：起始余额　
    
    列明某对帐单所涉及的一段时期开始时，有关帐户的帐面余额；或当报文出现分页时，每一分页的过渡起始余额。其内容包括：
    
    ![](http://drops.javaweb.org/uploads/images/3488ca87c8535b68fda9c4f5db2f5d6aad27b742.jpg)
    

该域内容必须与前一份该帐户对帐单报文域“62a”相同。只有当该报文系某一时期对帐单的第一分页，或对帐单没有分页，这份报文中该域代号才为“60F”。

*   域61：对帐单细目　
    
    列明每笔业务的详情。在报文的容量允许范围内，该域可重复使用，其内容共有九个子域，顺序如下：
    
    ![](http://drops.javaweb.org/uploads/images/ecfd46c576539313b244ed0b51da2e56a7c0d964.jpg)
    
    1.  如系通过SWIFT报文收付的金额及其费用，其类型表现为：“Snnn”字母“S”后的三位数字即SWIFT报文格式代号。
        
    2.  如系通过非SWIFT报文收付的金额及其费用，其类型表现为“Nxxx”字母“N”后的三个字母为下列代码之一所替换以表示该资金收付的理由：
        
        ![](http://drops.javaweb.org/uploads/images/5c1eccfabfe92caea3219eee62395e1282ad7f97.jpg)
        
    3.  由本对帐单首次通知开户人的收付金额（该收付发生在帐户行，在发送本对帐单之前未曾通知过开户人），其类型表现为：“Fxxx”。字母“F”后的三个字母必须为适当的代码以表示该借记或贷记的原由（代码同2）。
        
        ![](http://drops.javaweb.org/uploads/images/e33321fbc08aedcf53c7fc2fcf85434abbe72498.jpg)
        
*   域62a：帐面余额（结束余额）　
    
    如对帐单没有分页，或某报文是对帐单的最后一个分页（在对帐单由数份报文组成时），在这样的报文中，该域代号为“62F”，其内容为该对帐单结束时的帐面结存的最后余额，其余额必须出现在下期对帐单的域“60F”中。如该报文不是对帐单的最后一个分页，该域代号为“62M”，其内容为过渡帐面余额，其余额必须出现在下一分页的“60M”中。其内容有四个子域，结构同域“60a”。
    
*   域64：有效余额　
    
    如该域列明贷方余额，则为有效余额。如列明借方余额，则开户人须为此支付利息。其内容有四个子域，结构同域“60a”。
    

0x02 攻击事件分析
===========

* * *

1. 整体流程
-------

![](http://drops.javaweb.org/uploads/images/e8b359c14807bff63e9a67878470335cca1ea488.jpg)

图 1 整体关系流程

针对越南先锋银行的攻击中，相关恶意代码内置了8家银行的SWIFT CODE，越南银行均在这些银行中设有代理帐户。目前看到的Fake PDF Reader样本目的不是攻击列表中的这些银行，而是用来删除越南银行与其他家银行间的转帐确认（篡改MT950对帐单）。这样银行的监测系统就不会发现这种不当交易了。

2. 功能概述
-------

Fake PDF Reader伪装成Foxit reader（福昕PDF阅读器），原始Foxit Reader.exe被重命名为Foxlt Reader.exe，在银行系统调用Foxit打印pdf时激活，将pdf转换为xml，根据配置文件匹配是否有符合要求的报文，找到匹配的报文修改后转换回pdf并调用原始的FoxitReader打印。并删除临时文件和数据库的符合条件的交易记录。

![](http://drops.javaweb.org/uploads/images/259d4a8dbca137180d0483b9a0e917cf869390a4.jpg)

图 2 关系图

![](http://drops.javaweb.org/uploads/images/a7dfd1cce234d6820cbc4d5a98e4381036ac090f.jpg)

图 3 配置文件格式

3. 案例：MT950对帐单（PDF）详解
---------------------

![](http://drops.javaweb.org/uploads/images/9c9b8db1dacd323b5ff9461b4d9bbac069308c5c.jpg)

图 18 MT950对帐单（PDF）

上图是MT950对帐单的PDF版本，图中就对帐单的关键报文域进行了对应的解释（黑体字所示），另外蓝色框是Fake PDF Reader恶意程序需要判断和修改的地方（蓝色字体是相关具体动作的说明）。

下图是正常的PDF对帐单和篡改后的PDF对帐单，其中左图红色底色部分内容，就是攻击者想要删掉帐单记录和需要修改的帐面余额和有效余额。

![](http://drops.javaweb.org/uploads/images/fa9ad2d55adfbfdd03a64ede6b72cb2429d42b05.jpg)

图 19 正常PDF对帐单（左图），篡改后的PDF对帐单（右图）

4. 技术细节
-------

Fake PDF Reader分析

![](http://drops.javaweb.org/uploads/images/a099dd517c7ed74cee715460acac3b0cc86e5481.jpg)

![](http://drops.javaweb.org/uploads/images/240599260a86c2fa27af7b6b2b0404f0c13036f7.jpg)

图 4 功能流程图

Fake PDF Reader程序来自于Foxit PDF SDK，依赖动态库fpdfsdk.dll。

**A、读取配置文件**

配置文件使用异或加密，KEY为7C4D5978h。路径为`c:\windows\temp\WRTU\LMutilps32.dat`。

![](http://drops.javaweb.org/uploads/images/c93641934d8e26ec04ed55ee9ae392c6a4bfbd35.jpg)

图 5 读取配置文件

**B、处理参数**

参数个数必须大于等于4个，应该为：“FoxitReader路径”、“/t”、“pdf路径”和“打印机ip”。

**C、PDF修改**

![](http://drops.javaweb.org/uploads/images/4a5459a8fd10ae260da388d606f7c23b7543a0b6.jpg)

图 6 PDF修改执行流程

*   PDF转XML：以参数-xml调用了pdf2html库，转换成xml，文件放在临时目录。
    
    ![](http://drops.javaweb.org/uploads/images/81d5feb5678bfa28ea22c6b13fb198670315bc0a.jpg)
    
    图 7 PDF转XML
    
*   读取xml文件：查找Instance Type and Transmission所在的行，跳过9行，匹配SWIFT消息类型字符串，有FIN 950则进入950消息处理，没有则进入非950消息处理。
    
*   950消息处理：匹配Sender字段，查找发报方的SWIFT Code，匹配是否在列表中。符合条件则定位Opening Balance行，并跳过9行，读取Amount数值，转换为Int64。继续跳过2行，匹配是否为Debit，循环读取Opening Balance的所有交易和配置文件中的字符串比较，符合则设置删除标记并对数据做累加操作，继续读取Closing Balance节中的Amount字段，转换为Int64。根据前面累加的数据和此数据对比，平帐后写入数据并设置Debit/Credit标记。完成修改后,新添加1页，重新添加所有行,并删除前面的1页。
    
    ![](http://drops.javaweb.org/uploads/images/ff79c57b6fcd571cfc29816f64009bac71a3661b.jpg)
    
    图 8 恶意代码内部预设的SWIFT CODE
    
    ![](http://drops.javaweb.org/uploads/images/3f27887c6b97f85c2c1e2474348fdd4bb63dd728.jpg)
    
    表 4 恶意代码内部预设的SWIFT CODE对应的具体银行名称
    
*   非950消息处理：从Sender行开始读取，和配置文件匹配，成功后删除整页。
    
*   修复xml中的行的坐标，修复指定行的字体，并修正Closing Avail Bal (Avail Funds)的值。
    
*   删除临时文件。
    
    ![](http://drops.javaweb.org/uploads/images/409e3a16e11394f3af32b02c59ab71a699ae9863.jpg)
    

图 9 删除临时文件

*   XML转PDF。

**D、使用原参数调用真正的FoxitReader.exe**

![](http://drops.javaweb.org/uploads/images/3a431ee5d712549637b1d5b0defb99d389faa464.jpg)

图 10 调用真正的FoxitReader

**E、失败则调用LogClear**

![](http://drops.javaweb.org/uploads/images/d6c564cfbf3fc2cbf32b435a341aaa67b11e291a.jpg)

图 11 调用LogClear

**F、最后删除临时文件**

### LogClear分析

![](http://drops.javaweb.org/uploads/images/829dd4926a20e7644329b0eb60b1bdf938f0348d.jpg)

![](http://drops.javaweb.org/uploads/images/decdfd266dc28259d15626d4a227c4ac271738b6.jpg)

图 12 功能流程图

根据传入参数个数进行相关初始化操作，如果有进行初始化操作，如果没有参数则直接开始执行清除操作；

命令参数格式：`'-f <message filename> -l <logfile path>'`

![](http://drops.javaweb.org/uploads/images/995450153b32c23498c4e353292f2638b256e271.jpg)

图 13 相关参数格式

进一步进行循环删除文件中记录的内容，根据参数格式化一个文件名称，进行删除消息文件相关记录操作。

文件名格式：`%s\\%s_%d%.2d%.2d.txt`，第一个`%s`是从配置文件中读取的路径，第二个`%s`的字符串内容如下，后面的`%d`依次表示年、月、日。

![](http://drops.javaweb.org/uploads/images/b7b2db4de51307c5774508acce795879ebe6d54f.jpg)

图 14 读取的相关内容

![](http://drops.javaweb.org/uploads/images/6910b8b609926d9410cf79aed67cd403d841dd4e.jpg)

最后通过sqlcmd.exe 执行数据库操作删除数据库中消息文件相关记录.

![](http://drops.javaweb.org/uploads/images/5b902a93e48f7328b3fb61eab842a5f8b09fc6c1.jpg)

图 15 清理错误日志1

![](http://drops.javaweb.org/uploads/images/1504d0064d2b8a16125a0a66b81980f76f8edf61.jpg)

图 16 清理错误日志2

![](http://drops.javaweb.org/uploads/images/97ddf7636808733e5d71a3e8054811e6ce681741.jpg)

图 17 清理graft_history

### 同源性分析

在本报告中主要就越南先锋银行相关攻击事件、样本展开深入分析，暂不就其他攻击

事件中的同源样本展开详细介绍，本节只简单证明二者之间的存在一定的联系。

关于越南先锋银行、孟加拉国央行和Lazarus组织之间的关系，我们在之后的关联分析报告中会有详细的介绍。

![](http://drops.javaweb.org/uploads/images/ab98b9404e3b0b90e61d760049a8f56f768d0942.jpg)

0x03 总结
=======

* * *

从将恶意程序构造伪装成Foxit reader（福昕PDF阅读器）到对MT950对帐单PDF文件的解析和精确的篡改等攻击手法，都反映出攻击者对银行内部交易系统和作业流程非常熟悉。

针对越南先锋银行的针对性攻击和之前针对孟加拉国央行等其他银行的攻击之间，并非独立无关的攻击事件，从360追日团队对相关样本同源性分析和其他厂商的研究分析来看，针对越南先锋银行和孟加拉国央行的攻击有可能来自同一个组织，其幕后组织有可能是Operation Blockbuster所揭秘披露的Lazarus组织。