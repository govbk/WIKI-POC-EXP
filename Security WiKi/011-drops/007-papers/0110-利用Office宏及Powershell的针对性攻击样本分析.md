# 利用Office宏及Powershell的针对性攻击样本分析

**Author：360天眼安全实验室**

0x00 背景
=======

* * *

人在做，天在看。

利用Powershell执行攻击由于其绕过现有病毒查杀体系的有效性，已经成为目前日益泛滥的攻击手段，不论普遍撒网的勒索软件还是定向的针对性攻击都有可能采用。360天眼实验室一直对此类样本做持续的监测， 5月份以来，我们注意到一类比较特别的样本，发现其有两个比较鲜明的特点。

1.  利用Excel表格存放诱饵数据，伪造警告欺骗用户启用宏，宏代码会从表格中读取出数据，然后释放并执行；
    
2.  使用Powershell脚本通过DNS请求来传输数据，将数据写成批处理文件（.bat）再执行，执行完毕将结果通过同样的方式回传，然后删除痕迹。如此实现远程控制功能，并且控制方式上非常隐蔽。
    

FireEye公司在5月22日发布了一篇关于此类样本和相关攻击行动的分析报告，详细地分析了实现上的技术细节，指称这是一次针对中东地区银行的定向攻击。进入6月以后，我们还发现了一些新的同类型样本被提交。

![](http://drops.javaweb.org/uploads/images/e0e2b28abc7ca327236f462324ef315e652220c4.jpg)

注意到这些样本在VT上查杀率十分低，截止我们完成这篇文章时，仅为2/56：

![](http://drops.javaweb.org/uploads/images/c95a8ad9c9c4e985fd082ad7333b357147dd0ac3.jpg)

有趣的是，我们发现这些新的样本代码虽然与之前的几乎一样，只是删除了一些注释并改变了C&C域名，而在代码中添加了一段特别的注释，见下图，其用意倒值得猜测。

![](http://drops.javaweb.org/uploads/images/a0156edb5d318d5bc5e2f731f49e4cdc7a733a53.jpg)

0x01 样本分析
=========

* * *

概述
--

我们得到的木马样本基本信息如下，2016年6月15日被提交到VirusTotal上。

MD5：3e63d55f1e44a71041311c44e34baaa9

文件名：final345.xls

样本是一个嵌入宏的Excel文件，文件被打开后为打开了宏的状态，则宏中的恶意代码会释放一个vbs和一个ps1脚本文件。其中vbs主要功能是从服务器下载文件并执行，然后再将指定目录的文件上传到服务器；而ps1则是一个利用DNS请求获取数据执行远程命令的恶意脚本。

执行细节
----

打开xls文件后，可以看到攻击者伪造了一个警告：

![](http://drops.javaweb.org/uploads/images/79cc59a4dc6b4581c61d409570c041936cef77cb.jpg)

这时候第一行第25、26列的单元格内容是被设置为不可见的，但是可以从内容栏中看到数据，如果点击启用内容，那么宏里的恶意代码就会执行起来。

宏代码
---

![](http://drops.javaweb.org/uploads/images/967f4538af2a9bc54767912a16358b4e1c8ef34a.jpg)

上图中的宏代码功能主要描述如下：

1.  从表格中第1行第25列（也就是[1,Y]）的单元格中读取数据并调用powershell执行，写入到`%public%/Library/fireeye.vbs`中。
    
2.  从表格中第1行第26列（也就是[1,Z]）的单元格中读取数据并调用powershell执行，写入到`%public%/Library/fireeye.ps1`中。
    
3.  创建目录`%public%/Library/up`、`dn`、`tp`。
    
4.  将释放的fireeye.vbs加入计划任务.
    

值得注意的是，5月份出现的样本中最后会将表2显示出来，表2中有一些用于迷惑用户的数据，而这次的样本表2中是没有任何数据的。

![](http://drops.javaweb.org/uploads/images/15a6d5faeb004e0e53f3a261f022e8769df78596.jpg)

fireeye.vbs
-----------

fireeye.vbs的功能是用powshell从服务器下载文件到%Public`%\Libraries\dn`目录下，接着下载bat文件到\dn目录下并执行，然后将`%Public%\Libraries\up`目录下的文件上传到服务器，最后删除这些文件，并启动fireeye.ps1。具体流程如下：

1.  从`http://update-kernal.net/update-index.aspx?req=2062203590\dwn&m=d`下载文件并保存在`%PUBLIC%\Libraries\dn\`目录下，保存的文件名在服务器响应的Content-Disposition字段的filename中取得。
    
2.  从`http://update-kernal.net/update-index.aspx?req=2062203590\bat&m=d`获取批处理文件的内容，Base64编码后执行并将结果保存为`%PUBLIC%\Libraries\up\[RandomNumber].txt`，重命名这个TXT文件，重命名文件名在服务器响应的Content-Disposition字段的filename中取得。
    
3.  将TXT文件经过Base64编码后，上传至`http://update-kernal.net/update-index.aspx?req=2062203590\upl&m=u`，上传后将文件删除。
    
4.  执行fireeye.ps1。
    

相关代码如下：

![](http://drops.javaweb.org/uploads/images/2793a104c3502bbfecee01ce84fdbc59efa8eb0f.jpg)

fireeye.ps1
-----------

fireeye.ps1是一个巧妙利用DNS请求来接收命令和传输数据的脚本。总体行为如下：

*   获取用于标识身份的ID
    
*   通过获取DNS解析的IP地址 ，每次接收4个字节，写入批处理文件中
    
*   执行批处理文件，输出结果到TXT文件
    
*   发送TXT到服务器
    
*   清理痕迹
    

![](http://drops.javaweb.org/uploads/images/5c2a1718ca5ba1cb62680c62b41a3e98fd63d0eb.jpg)

关键代码如下，因为服务器已经将子域名的A记录解析到不同的IP地址，一个IP地址恰好能表达4个字节的数据，样本可以通过不断地拼接不同的子域名去获取到对应的IP地址也就是数据。

![](http://drops.javaweb.org/uploads/images/787f2e93d8e4962e68ab1ab1667785001e115011.jpg)

解析命令代码如下：

![](http://drops.javaweb.org/uploads/images/216956f9a2f8de199ce667e174141a647a359c0d.jpg)

与之前的样本相比，获取子域名代码也作了一些修改：

*   `ww00000[Base36(RandomNumber)]30.update-kernel.net`：获取标识身份的id
    
*   `ww[id]00000[Base36(RandomNumber)]30.update-kernel.net`: 发起会话
    
*   `ww[id]00000[Base36(RandomNumber)] 232A[filename][i].update-kernel.net`: 接收命令
    
*   `ww[id][upfilename][Base36(filelen)][filecontext] .update-kernel.net`: 上传文件
    

![](http://drops.javaweb.org/uploads/images/b75ebf1bf648ab0bd65e8efea365f871e0beba95.jpg)

0x03 幕后团伙
=========

* * *

现在C&C服务器已经不能正常返回数据，但是我们可以从第二步解析的地址中获取到一些相关信息：

![](http://drops.javaweb.org/uploads/images/928946896ab6ed0d821bf2b35d5a158d1b0cd682.jpg)

样本中C&C的主域名为[update-kernal.net](https://www.virusbook.cn/domain/update-kernal.net)，解析到IP[5.39.112.87](https://www.virusbook.cn/ip/5.39.112.87)，通过查询360威胁情报中心，此IP相关的标签包含有“OilRig”，此标签来自Palo Alto Networks在5月份发布的一篇报告，与FireEye的文章一致的是指称相同的攻击目标。因此，在威胁情报中心的[update-kernal.net](https://www.virusbook.cn/domain/update-kernal.net)域名相关的条目也被标记上OilRig标签。

![](http://drops.javaweb.org/uploads/images/bd3eb85e0508bdfd2847a2cd74963ad9310d52a1.jpg)

在PAN的报告中所涉及的样本所连接的域名[go0gie.com](https://www.virusbook.cn/domain/go0gie.com)，也解析到[5.39.112.87](https://www.virusbook.cn/ip/5.39.112.87)，可见我们得到的样本无论从代码和所涉及的网络基础设施都与之前所揭露出来的攻击活动一致，构成已知攻击活动的一部分。

0x04 IOC
========

* * *

| 类型 | 值 |
| --- | --- |
| C&C域名 | [update-kernal.net](https://www.virusbook.cn/domain/update-kernal.net) |

0x05 总结
=======

* * *

查杀工具与恶意代码的攻防竞赛一直在进行中，在PE文件被作为严防死守对象的今天， Office宏、VBS，Powershell、Javascript等非PE的脚本攻击载荷由于方便进行加密混淆而有很好的免杀性，对抗恶意代码的厂商有必要采取更多的手段来应对此类威胁。

0x06 参考链接
=========

* * *

*   http://researchcenter.paloaltonetworks.com/2016/05/the-oilrig-campaign-attacks-on-saudi-arabian-organizations-deliver-helminth-backdoor/
    
*   http://researchcenter.paloaltonetworks.com/2016/05/the-oilrig-campaign-attacks-on-saudi-arabian-organizations-deliver-helminth-backdoor/