# 不修改加密文件名的勒索软件TeslaCrypt 4.0

0x00 概述
=======

* * *

安天安全研究与应急处理中心（Antiy CERT）近期发现勒索软件TeslaCrypt的最新变种TeslaCrypt 4.0，它具有多种特性，例如：加密文件后不修改原文件名、对抗安全工具、具有PDB路径、利用CMD自启动、使用非常规的函数调用、同一域名可以下载多个勒索软件等。

勒索软件TeslaCrypt在2015年2月份左右被发现【1】，它是在Cryptolocker的基础上修改而成。在其第一个版本中，TeslaCrypt声称使用非对称RSA-2048加密算法，但实际上使用的是对称的AES加密算法，由此Cisco（思科）发布了一款解密工具，在找到可恢复主密钥的key.dat文件时，可以解密被TeslaCrypt勒索加密的文件【2】；但在之后的多个版本中，勒索软件TeslaCrypt开始使用非对称的RSA加密算法，被加密的文件在无密钥的情况下已经无法成功解密了，安天CERT发现，TeslaCrypt 4.0在2016年3月份开始出现，使用的是RSA-4096加密算法。

勒索软件系列事件的出现，具有多方面原因，其中重要的一点是匿名网络和匿名支付的高度成熟。2016年春节过后，勒索软件Locky开始爆发，全球多家安全厂商发布了相应的报告，安天CERT也在2016年2月19日发布了《首例具有中文提示的比特币勒索软件“LOCKY”》【3】；2016年3月底，G-Data和趋势先后发布了修改MBR、加密整个硬盘的勒索软件Petya的报告；2016年4月初，安天CERT开始跟踪勒索软件TeslaCrypt 4.0。

0x01 传播方式
=========

* * *

勒索软件TeslaCrypt 4.0利用网站挂马和电子邮件进行传播，在国内网站挂马发现的较少，通常利用浏览器漏洞（Chrome、Firefox、Internet Explorer）、Flash漏洞和Adobe Reader漏洞进行传播；而利用电子邮件传播的数量较多，安天CERT发现的多起勒索软件事件也都是通过电子邮件传播的。

![p1](http://drops.javaweb.org/uploads/images/156b363a6af7641248c326abf96b2d7b38ecc7f0.jpg)图 1 利用电子邮件传播勒索软件

在分析TeslaCrypt的下载地址时，安天CERT研究人员发现，相同域名下存放多个TeslaCrypt 4.0程序，且文件HASH各不相同。例如：域名http://***|||pasqq.com，可以下载TeslaCrypt 4.0的地址如下：

*   `http://***pasqq.com/23.exe`
*   `http://***pasqq.com/24.exe`
*   `http://***pasqq.com/25.exe`
*   `http://***pasqq.com/42.exe`
*   `http://***pasqq.com/45.exe`
*   `http://***pasqq.com/48.exe`
*   `http://***pasqq.com/69.exe`
*   `http://***pasqq.com/70.exe`
*   `http://***pasqq.com/80.exe`
*   `http://***pasqq.com/85.exe`
*   `http://***pasqq.com/87.exe`
*   `http://***pasqq.com/93.exe`

另外，其他域名中勒索软件的下载地址同上，如：23.exe、24.exe、25.exe … 93.exe。至2016年4月7日14时，安天CERT共发现具有下载勒索软件TeslaCrypt 4.0的域名共50多个，部分域名已经失效。

部分下载勒索软件TeslaCrypt 4.0的域名：

*   `***pasqq.com`
*   `***uereqq.com`
*   `***ghsqq.com`
*   `***rulescc.asia`
*   `***rulesqq.com`

0x02 样本分析
=========

* * *

安天CERT共发现近300个勒索软件TeslaCrypt 4.0。研究人员在其中选择了时间较新的样本进行分析。

### 2.1 样本标签

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">病毒名称</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Trojan[Ransom]/Win32.Teslacrypt</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">原始文件名</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">80.exe</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">MD5</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">30CB7DB1371C01F930309CDB30FF429B</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">处理器架构</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">X86-32</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">文件大小</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">396 KB (405,504 字节)</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">文件格式</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">BinExecute/Microsoft.EXE[:X86]</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">时间戳</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">5704939E --&gt;2016-04-06 12:42:06</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">数字签名</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">NO</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">加壳类型</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">未知</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">编译语言</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Microsoft Visual C++</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">VT首次上传时间</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">2016-04-06 04:07:00 UTC</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">VT检测结果</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">28/57</td></tr></tbody></table>

### 2.2 使用RSA4096加密算法加密文件，但不修改原文件名

该样本运行后复制自身至%Application Data%文件夹中，重命名为wlrmdr.exe，设置自身属性为隐藏，然后使用CreateProcessW为其创建进程。

![p2](http://drops.javaweb.org/uploads/images/0de1829decc2bc272b384cd4741d5c355784c94d.jpg)图 2 创建wlrmdr.exe进程

样本在新创建的进程中使用CreateThread开启线程，对全盘文件进行加密。首先样本使用GetLogicalDriveStringsW获取所有逻辑驱动器，成功后使用FindFirstFileW与FindNextFileW遍历全盘所有文件，进行加密。

![p3](http://drops.javaweb.org/uploads/images/8957c3eb9d5f9bef832e3581c6f9d07441a1ba78.jpg)图 3 遍历磁盘文件

加密函数地址为0x0040190A。

![p4](http://drops.javaweb.org/uploads/images/979a83ba53679684c4f1e575d82f10005ecb01c3.jpg)图 4 调用加密函数对遍历到的文件加密

利用RSA4096算法加密后，调用WriteFile将加密后的数据由内存写入文件，没有对文件名做修改。

![p5](http://drops.javaweb.org/uploads/images/0e2277b9c012f1f82b71473b1daaae27fab3ddab.jpg)图 5 将加密后的数据写入文件

加密前后的文件对比：

![p6](http://drops.javaweb.org/uploads/images/545038e3999bffa06ee5c0d96274f04d9011308d.jpg)图 6加密前后的文件对比

### 2.3 对抗安全工具

样本会查找系统中是否存在包含字符串的进程并将其隐藏，使用用户无法“看到”这些工具：

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">“taskmg”</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">任务管理器</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">“regedi”</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">注册表管理器</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">“procex”</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">进程分析工具</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">“msconfi”</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">系统配置</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">“cmd”</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">命令提示符</td></tr></tbody></table>

![p7](http://drops.javaweb.org/uploads/images/8e68adee5db35309396efc769c8b39531d66604d.jpg)图 7 隐藏cmd界面

### 2.4 具有PDB信息

样本具有PDB信息，其文件名为“`wet problem i yuoblem i_x.pdb`”

![p8](http://drops.javaweb.org/uploads/images/9a0dca94c3575159f507d08627080ecd9b47d931.jpg)图 8 样本的调试信息中包含PDB信息

### 2.5利用CMD自启动

样本调用RegCreateKeyExW，将使用CMD启动自身的代码写入至注册表中，使其随系统开机启动。

![p9](http://drops.javaweb.org/uploads/images/012a503b5e2166968094db4333116894b1214c8d.jpg)图 9 利用CMD达到随系统开机启动的目的

### 2.6使用非常规的函数调用和跳转

样本使用了很多非常规的函数调用和跳转，用来阻止安全人员分析该病毒。

![p10](http://drops.javaweb.org/uploads/images/a40b9d4b6cc4002448838a8bb0f566f371ddd32f.jpg)图 10　非常规的函数调用

![p11](http://drops.javaweb.org/uploads/images/2f079276b21f741deeb740ace8d3c9fdcc10e2f4.jpg)图 11　非常规的跳转

### 2.7 TeslaCrypt 4.0加密的文件格式

![p12](http://drops.javaweb.org/uploads/images/f7cb8f638ec67a0cfda7dad580e96ca44f6acce0.jpg)图 12 TeslaCrypt 4.0加密的文件格式

0x03 总结
=======

* * *

勒索软件对企业和个人用户都具有极大的威胁，被加密后的文件无法恢复，将给用户造成巨大的损失。解决勒索软件的威胁问题除安装安全产品、防护产品、备份产品外，更需要用户在接收邮件时谨慎小心，慎重打开邮件附件或点击邮件内的链接，尤其是陌生人邮件。

安天智甲终端防护系统（IEP）可以在用户误点击运行勒索软件时阻止其对用户文件进行加密。

0x04 附录一：参考资料
=============

* * *

*   【1】[安天发布：揭开勒索软件的真面目](http://www.antiy.com/response/ransomware.html)
*   【2】思科发布：针对勒索软件TeslaCrypt的解密工具：  
    [http://www.freebuf.com/sectool/66060.html](http://www.freebuf.com/sectool/66060.html)  
    [http://blogs.cisco.com/security/talos/teslacrypt](http://blogs.cisco.com/security/talos/teslacrypt)
*   【3】[首例具有中文提示的比特币勒索软件“LOCKY”](http://www.antiy.com/response/locky/locky.html)

0x05 附录二：安天CERT发现的50多个传播勒索软件的域名
===============================

* * *

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">marvellrulescc.asia</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">witchbehereqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohelloguymyff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">arendroukysdqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">isityouereqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">joecockerhereff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">blablaworldqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">jeansowghsqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">howisittomorrowff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">fromjamaicaqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">marvellrulesqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">giveitalltheresqq.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">goonwithmazerqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">greetingseuropasqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">giveitallhereqq.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">gutentagmeinliebeqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">grandmahereqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohelloguyzzqq.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">hellomississmithqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">mafiawantsyouqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">jeansowghtqq.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">hellomisterbiznesqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">spannflow.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">grandaareyoucc.asia</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">hellomydearqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohelloguyqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">imgointoeatnowcc.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">helloyoungmanqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">bonjovijonqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">washitallawayff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">howareyouqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">joecockerhereqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">greetingsjamajcaff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">invoiceholderqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">itsyourtimeqq.su</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">hpalsowantsff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">itisverygoodqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">blizzbauta.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohellowruff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">lenovomaybenotqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">yesitisqqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohelloweuqq.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">lenovowantsyouqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">thisisitsqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ujajajgogoff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">mafianeedsyouqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">soclosebutyetqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohiyoungbuyff.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">mommycantakeff.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">isthereanybodyqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">helloyungmenqq.com</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">thisisyourchangeqq.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">ohelloguyff.com</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"></td></tr></tbody></table>

0x06 附录三：安天CERT发现的C&C地址
=======================

* * *

*   addagapublicschool.com/binfile.php
*   kel52.com/wp-content/plugins/ajax-admin/binstr.php
*   closerdaybyday.info/wp-content/plugins/google-analytics-for-wordpress/vendor/composer/installers/tests/Composer/Installers/Test/binfile.php
*   coldheartedny.com/wp-content/plugins/wordpress-mobile-pack/libs/htmlpurifier-4.6.0/library/HTMLPurifier/DefinitionCache/Serializer/URI/binfile.php
*   thejonesact.com/wp-content/themes/sketch/binfile.php
*   theoneflooring.com/wp-content/themes/sketch/binfile.php
*   mahmutersan.com.tr/wp-content/plugins/contact-form-maker/images/02/03/stringfile.php
*   myredhour.com/blog//wp-content/themes/berlinproof/binstr.php
*   controlfreaknetworks.com/dev/wp-content/uploads/2015/07/binstr.php
*   sappmtraining.com/wp-includes/theme-compat/wcspng.php
*   controlfreaknetworks.com/dev/wp-content/uploads/2015/07/wcspng.php
*   vtechshop.net/wcspng.php
*   sappmtraining.com/wp-includes/theme-compat/wcspng.php
*   shirongfeng.cn/images/lurd/wcspng.php
*   198.1.95.93/~deveconomytravel/cache/binstr.php
*   helpdesk.keldon.info/plugins/editors/tinymce/jscripts/tiny_mce/plugins/inlinepopups/skins/clearlooks2/img/binfile.php
*   hotcasinogames.org/binfile.php
*   goldberg-share.com/wp-content/plugins/contact-form-7/includes/js/jquery-ui/themes/smoothness/images/binfile.php
*   opravnatramvaji.cz/modules/mod_search/wstr.php
*   studiosundaytv.com/wp-content/themes/sketch/binfile.php
*   theoneflooring.com/wp-content/themes/sketch/binfile.php
*   hotcasinogames.org/binfile.php
*   pcgfund.com/binfile.php
*   kknk-shop.dev.onnetdigital.com/stringfile.php
*   forms.net.in/cgi-bin/stringfile.php
*   casasembargada.com/wp-content/plugins/formcraft/php/swift/lib/classes/Swift/Mime/HeaderEncoder/stringfile.php
*   csskol.org/wp-content/plugins/js_composer/assets/lib/font-awesome/src/assets/font-awesome/fonts/stringfile.php
*   grosirkecantikan.com/wp-content/plugins/contact-form-7/includes/js/jquery-ui/themes/smoothness/images/binarystings.php
*   naturstein-schubert.de/modules/mod_cmscore/stringfile.php
*   vtc360.com/wp-content/themes/vtc360_maxf3d/ReduxFramework/ReduxCore/inc/extensions/wbc_importer/demo-data/Demo2/binarystings.php
*   starsoftheworld.org/cgi-bin/binarystings.php
*   holishit.in/wp-content/plugins/wpclef/assets/src/sass/neat/grid/binarystings.php
*   minteee.com/images/binstr.phpnewculturemediablog.com/wp-includes/fonts/wstr.php
*   drcordoba.com/components/bstr.php

0x07 附录四：关于安天
=============

* * *

安天从反病毒引擎研发团队起步，目前已发展成为拥有四个研发中心、监控预警能力覆盖全国、产品与服务辐射多个国家的先进安全产品供应商。安天历经十五年持续积累，形成了海量安全威胁知识库，并综合应用网络检测、主机防御、未知威胁鉴定、大数据分析、安全可视化等方面经验，推出了应对持续、高级威胁（APT）的先进产品和解决方案。安天技术实力得到行业管理机构、客户和伙伴的认可，安天已连续四届蝉联国家级安全应急支撑单位资质，亦是CNNVD六家一级支撑单位之一。安天移动检测引擎是获得全球首个AV-TEST（2013）年度奖项的中国产品，全球超过十家以上的著名安全厂商都选择安天作为检测能力合作伙伴。