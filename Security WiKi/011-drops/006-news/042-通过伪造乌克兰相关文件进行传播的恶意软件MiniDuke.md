# 通过伪造乌克兰相关文件进行传播的恶意软件MiniDuke

![enter image description here](http://drops.javaweb.org/uploads/images/b6029a9db8dc33fd1c4f29693cde79ae74538a41.jpg)

一年之前，安全研究人员从杀毒厂商卡巴斯基发现了一个复杂的恶意软件，他们称为 MiniDuke，专门收集和窃取战略信息和受到高度保护的政治信息。

现在，MiniDuke病毒再次通过一个与乌克兰相关的PDF文件在传播。

“考虑到当前该地区的危机，这是件很有趣的事情”安全研究公司F-Secure公司的首席技术官Mikko Hypponen在周二写到。

Hacker News一年前[报道](http://thehackernews.com/2013/03/old-school-hackers-spying-on-european.html)了该exp利用的`CVE-2013-0640`。

MiniDuke恶意软件是用汇编编写的，非常小只有20KB，可以劫持Twitter账户。

该恶意软件由三个部分组成： PDF文件， MiniDuke程序和payload。

打开PDF溢出之后，会移除payload，PDF的内容设计人权，乌克兰的外交政策，加入北约计划。

受感染的计算机会通过Twitter或Google接收加密的指令，一旦计算机受到感染就会连接到发送指令的服务器，它开始通过GIF图像文件接收加密的后门。一旦安装，它可以复制，删除，删除文件，创建数据库，停止进程并下载新的恶意软件，也可能会植入其它木马程序。

F-Secure公司还提供了几个被认为更有可能从已经存在的和扭曲乌克兰有关的文件截图。

![enter image description here](http://drops.javaweb.org/uploads/images/92ca5cd8de4acf2164760a07aff80f5d35197d94.jpg)

MiniDuke的作者所做的恶意软件似乎熟悉杀毒软件，这使得它与其它病毒不同的工作原理。该恶意软件包含一个后门，允许它绕过系统的分析，并在病毒被检测到的情况下，会阻止恶意行为，消失在系统当中。

MiniDuke恶意软件之前就攻击力比利时，巴西，保加利亚，捷克共和国，格鲁吉亚，德国，匈牙利，爱尔兰，以色列，日本，拉脱维亚，黎巴嫩，立陶宛，黑山，葡萄牙，罗马尼亚，俄罗斯联邦，斯洛文尼亚，西班牙，土耳其，美国政府机构英国，美国，包括乌克兰。