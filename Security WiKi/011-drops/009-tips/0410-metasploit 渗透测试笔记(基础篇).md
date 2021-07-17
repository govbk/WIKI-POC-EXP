# metasploit 渗透测试笔记(基础篇)

0x00 背景
-------

* * *

笔记在kali linux(32bit)环境下完成，涵盖了笔者对于metasploit 框架的认识、理解、学习。

这篇为基础篇，并没有太多技巧性的东西，但还是请大家认真看啦。

如果在阅读中有任何问题都可以与我邮件联系（contact@x0day.me）

0x01 在kali中使用metasploit
-----------------------

* * *

在kali中使用metasploit，需要先开启PostgreSQL数据库服务和metasploit服务，然后就可以完整的利用msf数据库查询exploit和记录了。这一点比bt5要方便很多，所以现在就放弃了bt5。

具体命令与截图

```
service postgresql start
service metasploit start

```

![enter image description here](http://drops.javaweb.org/uploads/images/14f492eb6b19ee31e3e3b64e2a59c1dd00146838.jpg)

如果不想每次开机都这样，还可以配置随系统启动。

```
update-rc.d postgresql enable
update-rc.d metasploit enable

```

![enter image description here](http://drops.javaweb.org/uploads/images/ecd8632ad277d06bba7e546f363c500b153997fb.jpg)

0x02 metasploit目录结构
-------------------

* * *

之所以会讲到这，是因为我认为框架代码是用来学习的一个非常好的来源。并且metasploit是用ruby脚本语言编写，所以阅读起来非常方便。在渗透，exploit编写过程前理解框架的优势以及大致内容则能够快速构建出自己的工具或者找到已知可用的工具。这样不仅有利于得到结果，也提高了效率。

这里只介绍几个目录，也希望读者能把modules下auxiliary的模块大致都看一遍。这样有个印象也便于快速查找。

对于工具的使用，没有会不会的。只是有没有发现而已。目录大概看一遍，这个问题就差不多了吧！

![enter image description here](http://drops.javaweb.org/uploads/images/ed422ced6cb11ee833d35f9f347cf7df4ee49e12.jpg)

Kali中msf的路径为`/usr/share/metasploit-framework`

### modules

首先看modules目录:

![enter image description here](http://drops.javaweb.org/uploads/images/f7a7d6771f584fec18f482a6a0c1c5e5388950d0.jpg)

这里

```
Auxiliary：辅助模块，
encoders：供msfencode编码工具使用，具体可以使用 msfencode –l
exploits：攻击模块 每个介绍msf的文章都会提到那个ms08_067_netapi，它就在这个目录下。
nops：NOP (No Operation or Next Operation) sled,由于IDS/IPS会检查数据包中不规则的数据，所以在某些场合下(比如针对溢出攻击),某些特殊的滑行字符串(NOPS x90x90...)则会因为被拦截而导致攻击失效，所以此时需要修改exploit中的NOPs.nops文件夹下的东西会在payload生成时用到(后面会有介绍)。比如我们打开php的NOPS生成脚本，就会发现它只是返回了指定长度的空格而已。

```

![enter image description here](http://drops.javaweb.org/uploads/images/e531ff7a2b850a43023e2d449b7070a5ca06fd64.jpg)

```
payloads：这里面列出的是攻击载荷,也就是攻击成功后执行的代码。比如我们常设置的windows/meterpreter/reverse_tcp就在这个文件夹下。
Post：后渗透阶段模块，在获得meterpreter的shell之后可以使用的攻击代码。比如常用的hashdump、arp_scanner就在这里。

```

### data

其次是data目录:

这里存放的是metasploit的脚本引用文件，重点介绍几个文件

![enter image description here](http://drops.javaweb.org/uploads/images/56bfd8412f9aafcda0af919e882d108cb612b844.jpg)

第一个是data下js文件夹下的detect，这里面存放的是metasploit的探针文件。如果看过metasploit浏览器攻击脚本的代码，就会发现调用了一个js库，然后检查当前请求是否符合被攻击环境。如果符合则发送攻击代码，否则中断。Memory中主要是一些堆喷射代码。在大部分浏览器漏洞利用过程，堆喷射是一个不可或缺的过程(当然不是绝对的！)。并且不同的浏览器及版本间，堆喷射代码都有所不同。所以这里给出的探针代码和堆喷射代码是不是一个非常好的学习资源呢？ script

最后是msf下script目录中的resource目录:

![enter image description here](http://drops.javaweb.org/uploads/images/1869df275b59fcecc10e07c3d3b9650bace76295.jpg)

这里的rc脚本相当于windows下的批处理脚本，在某些情况下会有一定便捷性。比如Veil在生成免杀payload的同时也会生成一个rc脚本，此时使用msfconsole –r xx.rc便可以快速的建立一个和payload对应的handler，亦或在攻过程中需要你反复的set exploit,那么就可以使用这个批处理脚本了，而这个目录下则是一些给定的rc脚本，虽然你可能不习惯这样使用，但作为改写自己的rc脚本的资源也不错。

0x03 metasploit基本命令
-------------------

* * *

列一些其他文章中不常提到的命令或者是我经常碰到或使用的方法。

### Msfpayload

![enter image description here](http://drops.javaweb.org/uploads/images/e9585503137f830f4038a63ff87449ad0a94fbb3.jpg)

这是我最常用的一个命令，用来生成payload或者shellcode。

在不知道payload名称又不想开msfconsole搜索的时候可以用`msfpayload –l |grep “windows”`这样的命令查询。

-o 选项可以列出payload所需的参数。

### msfencode

![enter image description here](http://drops.javaweb.org/uploads/images/9b5ab067b552008d0bd1e940d000499c9834cfae.jpg)

msf中的编码器，早期为了编码绕过AV，现在我常用msfpayload与它编码exploit的坏字符串。

### msfconsole

开启metasploit的console，有个重要的参数 –r，加载resources脚本

数据库有关命令

### hosts

![enter image description here](http://drops.javaweb.org/uploads/images/1ef8c160cab314f3746d8022fe5c648cfdf93939.jpg)

这里可以使用hosts查询指定字段的内容，可用的字段下面有列出。或者也可以使用hosts –S “keyword” 进行搜索。

### Creds

![enter image description here](http://drops.javaweb.org/uploads/images/01d81c92c68673602b4c8790c6cf6725f4b79b9c.jpg)

Creds命令可以列出成功获取到的信息，比如用户名密码，数据库密码，开放端口及服务等。

### Console中有关命令

### search

![enter image description here](http://drops.javaweb.org/uploads/images/748718386b3c08117497aa38c4e5b7c9bbd3f61b.jpg)

搜索一切可以use的模块,常用的方法是search 直接加关键词，比如search 08_067,但是我们也可以根据cve编号查找。通常用nessus扫到的漏洞都有cve信息，这里我们就可以这样搜索了。

![enter image description here](http://drops.javaweb.org/uploads/images/66df8d6b62630073908dc3f7234a837b6f155efc.jpg)

### spool

![enter image description here](http://drops.javaweb.org/uploads/images/c1f40e0b735ae8fe399218db6ad8f1ed001f3d5c.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f5fc579d2b9b3687f3790c316dfa15ccf00884dc.jpg)

将屏幕输出重定向到某个文件中，在使用HTTP弱口令破解、，内网http目录等不会记录在creds中的内容时你怎样解决查询成功结果的？反正这个问题我快要疯了。 要不就改写exploit，不成功不打印，要不就重定向之后自己再grep吧。如果有好的方法，一定要分享啊！

### show advanced

![enter image description here](http://drops.javaweb.org/uploads/images/ad19a7a8a70e19b89ae1d1b9e61021f8810eedf3.jpg)

在选定一个module(exploit,payload …)之后，使用show advanced命令可以显示关于此module的高级选项，具体内容会在后面”metasploit tricks and tips”中分享。

0x04 攻击示例
---------

* * *

同样我还是选择ms08_067这个漏洞，并且随便输入一个ip，演示下最基本的攻击过程(为了让基础篇看起来更完整点)结束基础篇的分享。说明:

![enter image description here](http://drops.javaweb.org/uploads/images/d48cf27ed471c8d088ceb52ee7f424af5febf9f8.jpg)

从图中也可以看出一次基本的攻击过程大概是这样的：

```
1. 选择exploit (use exploit/windows/smb/ms08_067_netapi)
2. 选择payload
3. 设置参数 (set RHOST,set LPORT …)
4. 执行攻击
```