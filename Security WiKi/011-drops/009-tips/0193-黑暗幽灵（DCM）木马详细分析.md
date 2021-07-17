# 黑暗幽灵（DCM）木马详细分析

0x00 背景
=======

* * *

只要插上网线或连上WIFI，无需任何操作，不一会儿电脑就被木马感染了，这可能吗？近期，腾讯反病毒实验室拦截到一个“黑暗幽灵”木马的新变种，该木马功能强大，行为诡异，本文将对其进行详细分析，以下是该木马的主要特点：

1.  木马功能强大，主要以信息情报收集为主，能够监控监听大量的聊天软件，收集网络访问记录、监控Gmail、截取屏幕、监控麦克风和摄像头等。
2.  木马对抗性强，能够绕过几乎全部的安全软件主动防御，重点对抗国内安全软件，能够调用安全软件自身的接口将木马加入白名单，作者投入了大量的精力逆向研究安全软件。
3.  木马感染方式特别，通过网络劫持进行感染，主要劫持主流软件的自动更新程序，当这些软件联网下载更新程序时在网络上用木马替换，导致用户无感中毒。
4.  木马通讯方式特别，木马将数据封装成固定包头的DNS协议包，发送到大型网站来实现数据传输，此方法可以绕过几乎全部的防火墙，但是黑客要截取这些数据，必须在数据包的必经之路上进行嗅探拦截，结合木马的感染方式，可以推测出在受害者网络链路上存在劫持。
5.  木马攻击范围较小，针对性强，且持续时间长达数年，符合APT攻击的特性。

0x01 木马行为概述
===========

* * *

### 1.1 来源与传播途径

经过对大量受感染用户的分析，我们发现该木马来源于不安全的网络，无任何系统漏洞的机器只要连接到这些网络后，在一段时间后会感染木马，经分析发现木马主要通过在网络上劫持替换大量软件的自动更新程序进而感染电脑。当安装在电脑上的软件进行自动更新时，更新包被替换成木马，导致电脑被入侵。木马传播示意图如图1所示。

![p1](http://drops.javaweb.org/uploads/images/bd7b91e8b3f657d4a2403fb7ea68ae91be5c4062.jpg)图1. 木马主要传播途径示意图

### 1.2 木马安装流程

木马运行后会判断本机安装的安全软件，会检测多达43款安全相关软件，当检测到不同的安全软件后，执行不同的安装方式，以实现绕过安全软件的检测和拦截。经分析发现该木马主要有三种不同的安装方式，木马最终安装启动的方式为将核心dll释放到explorer同目录下，对其进行dll劫持启动。如图2中三种颜色分别代表三种不同的安装方式，经测试该木马能够绕过当前绝大部分安全软件的防御和拦截最终成功安装。

![p2](http://drops.javaweb.org/uploads/images/b2844142f0336a0f387ef5e82b03bfffa76ef7c1.jpg)图2. 木马安装流程示意图

### 1.3木马功能分解

该木马主要功能是窃取计算机各种信息，通过插件监控监听各种常用聊天软件的语音文字聊天信息，接受指令进行简单的远程操控，将自动化收集到的各种信息文件打包发送。如图3所示为木马功能一览。

![p3](http://drops.javaweb.org/uploads/images/79289d7c5b8cb95b7c7a4a764f141e7b38bcaa4b.jpg)图3. 木马功能一览

### 1.4 木马网络通信

该木马的网络通信方式与木马的传播方式相呼应，木马将收集到的各种信息打包成文件，随后将其加密并封装成DNS请求包，并将这些数据包发送到国内几大知名网站服务器。这样的通讯方式可以绕过几乎所有的防火墙、入侵检测产品，然而黑客如何取得这些数据包从而获得窃取的数据呢？经分析发现其封装的DNS数据包都有着相同且固定的数据包头，因此我们推测黑客会在数据包必经之路上对数据包进行拦截转发到黑客服务器，从而获得收集到的信息，如图4所示为推测出的木马通讯数据包投递流程。

![p4](http://drops.javaweb.org/uploads/images/6ca205b4c67bf1a37b610d0af41271e2816f3409.jpg)图4.木马网络通讯方式推测

0x02 木马详细分析
===========

* * *

2.1 安装释放
--------

### 2.1.1母体结构

该木马的母体程序为一个exe可执行文件，通过网络劫持正常软件的更新程序而被下载执行，该文件中包含5个资源文件，均为简单加密的PE文件，其中141为x86版核心dll、142为lsp劫持dll、146为x64版核心dll、150为白加黑黑文件，151为白加黑白文件，以下将详细分析。

![p5](http://drops.javaweb.org/uploads/images/f0f84b19879a1966dd8320ecce05294c8cece07e.jpg)图5. 母体资源信息

### 2.1.2 适应多种系统，不同系统不同行为

判断操作系统版本，设置全局变量，随后将根据该全局变了进行大量的不同操作。

![p6](http://drops.javaweb.org/uploads/images/825d1a9a7fcecae2c38bd9b297ab61eb60e5c0d0.jpg)图6. 判断操作系统版本并设置标志

### 2.1.3 利用系统漏洞提权

判断当前系统是否为vista、win7等，如果是则检测当前进程是否具有管理员权限，如果没有该木马会尝试通过CVE-2011-1249将自身提升为管理员权限。该漏洞影响xp、vista、win7等多种版本操作系统。

![p7](http://drops.javaweb.org/uploads/images/6fc7d9cd5dc1cd993cedb34fb2f9cb03f505d39b.jpg)图7. 木马利用CVE-2011-1249漏洞提权

### 2.1.4 对explorer进行dll劫持

通过注册表检测本机安装的安全软件，当目标系统没有安装安全软件时，木马将根据操作系统释放劫持dll到%windir%目录下对explorer进行劫持启动，在xp等系统下木马释放ntshrui.dll、在win7等系统释放msls32.dll，在win8等系统释放AduioSes.dll。随后启动一个新的explorer进程加载核心dll开始工作，此为第一种安装方式。

![p8](http://drops.javaweb.org/uploads/images/e506fd38b01530d3fe5397de291e125288c6431c.jpg)图8. 木马通过释放dll到explorer同目录进行劫持启动

### 2.2 对抗安全软件

### 2.2.1 暂存核心文件

如果检测到趋势等国际安全软件而又未检测到国内主流安全软件时，木马会将核心dll释放到%CommonProgramfiles%的一个子目录下，暂时存放。

![p9](http://drops.javaweb.org/uploads/images/84f78f3304892fb85465c06dda86c2f12c22f5d0.jpg)图9. 暂时存放核心dll

### 2.2.2 释放dll并安装lsp

同时释放lsp劫持dll，并添加lsp，通过lsp，该dll可以注入到所有具有网络连接的进程中。在注入的进程中进行dll文件的移动，从而绕过安全软件，此为第二种安装方式。

![p10](http://drops.javaweb.org/uploads/images/2a90eff0a839c6c300786c1cdfeee86cc046da67.jpg)图10. 释放lsp劫持dll

![p11](http://drops.javaweb.org/uploads/images/fdffc4883efc5e0eff20ac18055308d7ec807f45.jpg)图11. 安装lsp

### 2.2.3 释放白加黑对抗杀软

当存在国内主流安全软件时，木马为了绕过针对lsp安装的拦截使用了白加黑技术

![p12](http://drops.javaweb.org/uploads/images/efc97d255becf3562d39797590093e774cee1efe.jpg)图12. 木马释放白加黑两个文件，准备绕过主防

### 2.2.4 通过白加黑安装lsp过主防

木马通过白加黑技术，并加以一系列复杂技巧绕过主动防御实现安装lsp，经测试大部分安全软件的主动防御均被绕过。

![p13](http://drops.javaweb.org/uploads/images/11f6eba3a95bae0873a191c0de896aa3248b4a6d.jpg)图13. 通过白加黑绕过主防安装lsp

### 2.2.5 绕过杀软对explorer进行dll劫持

安装lsp后，相关dll便以lsp劫持的方式插入到所有联网进程中，包括svchost、浏览器、聊天软件、安全软件等。Dll加载后首先判断当前进程，符合条件则将之前备份的核心dll移动到%windir%目录进行劫持（重启后移动）。此为第三种安装方式。

![p14](http://drops.javaweb.org/uploads/images/0294d83f888d7927055932ed60dc0bfa38634187.jpg)图14. 将核心dll移动到%windir%目录进行劫持

### 2.2.6 加载核心dll

随后木马判断自身是否位于ie、svchost、杀软等进程，以进行不同的行为，同时尝试直接加载核心dll（如果没加载，劫持需要等系统重启后核心dll才会被加载）

![p15](http://drops.javaweb.org/uploads/images/19c4e624614005f5f3c89faa0f824720fd59de39.jpg)图15. 根据当前进程名决定是否立即加载核心dll

### 2.2.7 恶意操作杀软白名单，免杀

木马判断自身是否位于各种安全软件进程中，如果是则调用安全软件自身接口进行白名单添加，会将所有木马文件路劲添加到杀软白名单中。经测试，涉及到的安全软件均能正常添加白名单。

![p16](http://drops.javaweb.org/uploads/images/3535dd9dfc9723941a6a329a7bfe9f7ccf858761.jpg)图16. 某安全软件白名单添加相关代码

### 2.2.8 lsp阻止安全软件联网，阻断云查

通过lsp过滤函数对WSPSend、WSPSendTo函数进行过滤，当判断发包者是安全软件进程则直接关闭连接，阻止联网，阻断云查

![p17](http://drops.javaweb.org/uploads/images/4809931a5cf8b24be011fa0604a0e5ddb3960dfc.jpg)图17. 阻止安全软件联网云查

### 2.3 信息收集

### 2.3.1 收集网卡信息

收集的网卡信息包括网卡型号、网卡mac、网关ip、网关mac等

![p18](http://drops.javaweb.org/uploads/images/75ee066554ba72693f54a43f69c18a92098f90a6.jpg)图18. 通过发送arp包获取网关mac地址

### 2.3.2 收集系统安装的软件列表

木马通过注册表Uninstall获取计算机安装的软件列表信息，将获取的信息异或0x87后写入到`C:\WINDOWS\Temp\{E53B9A13-F4C6-4d78-9755-65C029E88F02}\soft.prog`文件中，以下获取的信息无特殊说明都位于该目录下

![p19](http://drops.javaweb.org/uploads/images/02c3befc43252a8099194fd314a3ae641524638f.jpg)图19. 获取安装软件列表

### 2.3.3 截屏

获取当前屏幕快照，zip压缩后保存为time().v文件

![p20](http://drops.javaweb.org/uploads/images/f05326f17fe9be6ff15151c3914590b702a8c6c5.jpg)图20. 获取屏幕快照

### 2.3.4 收集磁盘文件目录

获取磁盘驱动器信息，包括全盘所有文件路径，获取后zip压缩到drive.d文件中

![p21](http://drops.javaweb.org/uploads/images/6618c87979b4a32eea6419241eba9f472a1b950e.jpg)图21.获取磁盘文件信息

### 2.3.5 收集IE历史记录

通过com获取浏览器历史记录信息，存储到ie.his

![p22](http://drops.javaweb.org/uploads/images/9e18995468515f398b8a2023e77cc2549e82b4d5.jpg)图22. 获取浏览器访问记录

### 2.3.6 收集设备信息

遍历系统设备，判断是否有笔记本电源适配器、摄像头、麦克风三种设备，将结果加密写入到time().hd文件中。

![p23](http://drops.javaweb.org/uploads/images/4677546c75e929cfaab21eae7dfaa059b5d4d0bf.jpg)图23.遍历系统设备

![p24](http://drops.javaweb.org/uploads/images/b94731a92d5196ae7dfb54da602adddb922b625a.jpg)图24. 判断是否有指定设备

### 2.3.7 针对浏览器进行键盘记录

安装WH_GETMESSAGE全局钩子，安装后理论上所有具有消息循环的进程均会加载此dll，并调用钩子函数，在钩子回调中，判断当前进程是否是Iexplorer.exe、360se.exe、SogouExplorer.exe三种浏览器进程，如果是则进行键盘记录，记录的包括按键信息、窗口标题，通过imm32.dll该方法还可以记录中文输入，记录到的信息存为（日期+时间）.k文件。

![p25](http://drops.javaweb.org/uploads/images/300a4e01e911340cddd50ddc0376d94e50c3acc1.jpg)图25. 安装钩子

![p26](http://drops.javaweb.org/uploads/images/3e23fc271f100c010bd9656fc7807b8a67737bf3.jpg)图26. 只记录指定浏览器进程的键盘输入

### 2.3.8 收集gmail信息

在记录键盘时，当判断以上浏览器窗口中含有Gmail字符时，会启动一个线程专门收集Gmail信息，会加载相关插件，尝试通过Imap协议下载服务器上的所有文件

![p27](http://drops.javaweb.org/uploads/images/2afeebce7f895021808046846f8ced3f607539a5.jpg)图27. 判断是否正在登录gmail

![p28](http://drops.javaweb.org/uploads/images/abae7693e358dede6919a0595fa3083dc27a95b4.jpg)图28. 通过插件尝试通过IMAP协议收集数据

### 2.3.8 加载插件收集各种IM相关信息

通过进程名判断skype.exe、cc.exe、raidcall.exe、yy.exe、aliim.exe等即时聊天、语音聊天软件，加载相关插件对此类聊天软件进行监听监控。

![p29](http://drops.javaweb.org/uploads/images/d7601d66cc6396aa80ba64218ee6e6785a232034.jpg)图29. 根据im软件进程名加载相关插件

![p30](http://drops.javaweb.org/uploads/images/3d173dfb409edf15dfdf715691f9ed6db3d16a5c.jpg)图30. 通过插件的接口可猜测相关插件主要用于监控聊天信息

![p31](http://drops.javaweb.org/uploads/images/681abbe0f214a50ae785392b346f86d8d098dacd.jpg)图31. 木马针对所有常见通讯软件均做了监控

### 2.4、网络通讯

### 2.4.1通讯协议

此木马最诡异的地方的通讯方式，该木马没有C&C服务器，所有的数据均伪装成DNS包发送到www.baidu.com、www.sina.com、www.163.com域名所在服务器的53端口或者8000端口。黑客要想获取这些数据包，必须在数据包从本地计算机到这些网站服务器的必经之路上进行劫持嗅探。

![p32](http://drops.javaweb.org/uploads/images/5d5af2750ae487a6422e759c18c46c170c2cd072.jpg)图32. 木马的数据包均发送到www.sina.com等服务器上

![p33](http://drops.javaweb.org/uploads/images/9408e19bf334af23fde12d267785559235d2e8e5.jpg)图33. 木马使用udp协议通讯，目标端口为53或者8000

![p34](http://drops.javaweb.org/uploads/images/416be9e2462f5a6ca667f368e2813056b40480fb.jpg)图34. 木马伪装成DNS协议数据包，每个包都有固定的包头作为标记

![p35](http://drops.javaweb.org/uploads/images/227ddd1b1e338404ca9e1067ee911986672bdce3.jpg)图35.嵌入到DNS协议中的木马数据，及时专业的网络管理员，也难发现异常

### 2.4.2 自动上传收集到的文件

所有木马自动收集的文件，木马插件生成的文件都会被定时打包编号并发送出去

![p36](http://drops.javaweb.org/uploads/images/1abd2579610e9346fdad0a38a80cdcec6d50d06e.jpg)图36. 定时读取相关文件，打包编号发送出去，发送成功后会删除先关文件

### 2.4.2 远程控制

木马还会绑定本地一个udp端口，并不断尝试收取指令，进行远程控制，主要的远程控制功能包括cmdshell、文件管理、插件管理等。

![p37](http://drops.javaweb.org/uploads/images/242b4a23189fe98c7d1a6dccda8366d1936b9147.jpg)图37.绑定本地一个udp端口

![p38](http://drops.javaweb.org/uploads/images/679db7fb566c19d59557330b0626f3dd1fc07f97.jpg)图38. 不断尝试收取控制指令

![p39](http://drops.javaweb.org/uploads/images/c12493e471e3ad11272576150dc4c199c18faee7.jpg)图39. 远控功能

0x03 木马信息
=========

* * *

### 3.1安全软件

木马检测多大43款安全软件，涵盖了多内全部的安全产品及国外较有名的安全产品，从安全软件来看，该木马主要针对国内用户

![p40](http://drops.javaweb.org/uploads/images/bd8536252be62b4285b5f3410775ed734da8223b.jpg)图50. 木马检测的安全软件列表

### 3.2 其它信息

从木马的互斥体、调试信息等可看出DCM应该是该木马的代号，但是什么的缩写的？这个还真猜不出来

![p41](http://drops.javaweb.org/uploads/images/d80be9ee874c1c8343417a83d784ada7376cf58a.jpg)图51. 木马中的字符串信息

0x04 安全建议
=========

* * *

软件厂商：下载更新程序尽量使用https等安全加密的通讯协议，对下载回来的文件在加载运行前一定要做签名校验。

用户：尽量不要使用安全性未知的网络上网，如公共WIFI、酒店网络等，如果怀疑自己的网络有问题，及时与运营商反应。此外安装安全软件可在一定程度上防御此类攻击，目前管家已率先查杀该木马及其变种。