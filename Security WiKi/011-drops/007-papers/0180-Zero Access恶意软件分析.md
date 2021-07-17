# Zero Access恶意软件分析

0x00 前言
=======

* * *

原文:http://resources.infosecinstitute.com/zero-access-malware/

木马Zero Access到目前为止已经在世界范围内感染了过亿的计算机，嗯，ZA(Zero Access)能够发展到这一个级别我想其中一个原因是因为恶意广告的点击，和泛滥的比特币挖掘。一旦ZA感染系统就会开始下载各种不同类型的恶意软件，总的来说无论是个人还是组织一旦遭受感染最后的损失肯定不会小。

ZA的传播媒介主要是 恶意邮件和 漏洞利用工具，同时也会通过分布式的p2p文件分享服务，或者是看起来像 游戏破解工具 和 注册机的软件来传播。ZA本身是有很多独特的地方，感染之后ZA会连接到一个基于p2p的僵尸网络，之后想要继续追踪是非常难得。

ZA本身使用了先进的隐藏机制来逃避，杀软和防火墙的检测和逃避。(省略一小段扯淡的话) 可执行文件通常在%TEMP%文件夹中，通过http请求与外部网站进行通信。

一旦ZA感染你的系统，会进行如下的操作：

*   用你的sb系统进行点击诈骗和比特币挖掘。
    
*   下载别的恶意软件....
    
*   开启杀软逃逸功能
    
*   提取计算机上的信息
    

0x01 分析
=======

* * *

我们一开始进行的分析过程如下：

我们的第一步是隔离受感染的机器，然后对系统进行一次扫描，初次扫描我们没有发现任何东西，但是在第二次扫描的时候我们发现在workstation中的%TEMP%文件夹新建了一个文件。

在%SYSTEM%目录中我们又发现了另外一个可疑文件，这个似乎是某种配置文件，并且该文件处在ACL保护状态下。

文件在sandbox中执行的时候进行了网络操作。

文件名称为fvshis.sav，内容已加密。

在文件运行的过程中我们提取了内存中的字符串很明显的可以看到使用了Max++ dropper组件。

![enter image description here](http://drops.javaweb.org/uploads/images/4508d5255aa01ae86067a464985c0048c19e67fb.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/7b8eafbb6ccd31d5f816fb4859181d95f92db4c5.jpg)

下一步我们很happy的分析了 dropper(用于恶意软件的安装)组件，咋一看这狗日的玩意好像没加壳，

![enter image description here](http://drops.javaweb.org/uploads/images/05eba12bd6baca347683ac367e3331ed17a32c72.jpg)

然而之后的分析，我们发现这玩意是加过壳的，使用了一些复杂的自定义加壳器，还使用了几种不同的反debugging机制来鼓励我们友好的加班。

![enter image description here](http://drops.javaweb.org/uploads/images/d110d60802544e5ca9b416abaa67ffebcb91b9f8.jpg)

int 20指令是一种系统中断。

PS: 没样本，不过应该前几个写入了int 20，利用CPU会预读取指令的特点，干扰单步跟踪。如:

```
mov word ptr [@@],20cdh
@@:
nop
nop

```

正常情况下CPU预读了2个nop，而不会执行INT 20(cd20)，但单步跟踪下来就不同了。

就是说程序可以检测自己是否处于debugging状态并且kill自己。

ZA本身还有着多层的加密机制，和他坑爹的壳。

![enter image description here](http://drops.javaweb.org/uploads/images/022923b7e14be75e72a66034a44ee9dd7cc11508.jpg)

刚才说了现在分析的是dropper，相当于一种部署恶意软件的玩意，壳对其中的每一个段进行了加密，dropper运行的时候会一步一步进行解密，一次解密一个代码段，并且每个代码块都有INT 20(mlgb...)，如果分析狗哪里一不小心多点了几下单步，那么进程崩溃。

在我们富有基情的努力下，最后还是完成了脱壳。之后我们就发现样本尝试访问位于计算机中的一些目录。

![enter image description here](http://drops.javaweb.org/uploads/images/2f0003c1227a2c1efcb286e0bf1da1faf3cec221.jpg)

我们注意到的另一件事情，从使用int20我们可以看出，这玩意是一个运行在内核模式下的Ring0 rootkit，在分析了内存之后我们还发现恶意样本在内存中创建了一个互斥锁来检测计算机之前是否被同样的东西感染过。

![enter image description here](http://drops.javaweb.org/uploads/images/8fd4c0863cf231fc196512e9a12dc5b7d0bd876b.jpg)

另一个发现就是这玩意把自己注入到了 (explorer.exe)进程中，并且利用其来执行payload。

![enter image description here](http://drops.javaweb.org/uploads/images/f9b99028297338537577da096decf86ccc1e33cd.jpg)

上面说了样本是运行在内核模式下，我们发现其实是将恶意软件作为一个内核模块安装。

![enter image description here](http://drops.javaweb.org/uploads/images/522bc47cbb0393b7d6f1b9e1d2f34547d6bf83b4.jpg)

ZA会将自己伪装成一个设备驱动程序B48DADF8.sys，我们将这个内核dump 下来进行进一步分析。

![enter image description here](http://drops.javaweb.org/uploads/images/48a8784bc5cf5e0b48c3705bd4118b90b45bc700.jpg)

初步的分析中，ZA发出了一些可以的网络流量，初步判断是类似上线通知一样的东西，跟打剑灵的时候“好友xxxx上线”差不多。

![enter image description here](http://drops.javaweb.org/uploads/images/0124fce6217e898b11ddee48ed6d55bd9bc35018.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/ab0c413e07005742bc7640d6f750c4f5d0820648.jpg)

同时发出了一下http请求到特定的域名

![enter image description here](http://drops.javaweb.org/uploads/images/c364ef7094bac2cb051fb24ba3a42009d6812dce.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f159328be71aacaa778fbe9802ac32cf1dfc2551.jpg)

这玩意显然是想先建立连接，然后下载别的恶意程序。

![enter image description here](http://drops.javaweb.org/uploads/images/e298321fe22d0b0fef1809a86cbc9b8546efb1cb.jpg)

之后我们分析了该域名，似乎是位于瑞士的苏黎世，嗯，瑞士这个国家的法律会在很大程度上保护他们公民的隐私，同时也导致了网络罪犯们很喜欢把自己的 C&C服务器托管在瑞士。

![enter image description here](http://drops.javaweb.org/uploads/images/2502d32edcd5766f07e6ab246debaf6d52252b11.jpg)

我们对域名进行了进一步的分析，发现该域名实际上预设到三个不同地方的ip，唯一的共同点就是当地的隐私保护做的很全面。

![enter image description here](http://drops.javaweb.org/uploads/images/e020c209e8d46f2bfa85c83058a763d65a0c58fd.jpg)

0x02 结语
=======

* * *

我省略了一下类似安全建议的东西。

我们找到了三个ip

*   141.8.225.62 (Switzerland)
    
*   199.79.60.109 (Cayman Islands)
    
*   208.91.196.109 (Cayman Islands)
    

虽然这玩意不窃取用户信息，不过他会产生大量的网络流量，进行点击诈骗和比特币挖掘。