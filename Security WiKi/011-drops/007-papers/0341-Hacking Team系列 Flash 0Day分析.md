# Hacking Team系列 Flash 0Day分析

0x00 导读
=======

* * *

Hacking Team事件已经过去1个星期，社会各界针对泄露数据的分析还在进行中。为了帮助安全技术从业者后续能够有更多的人加入到分析队伍中来，绿盟科技安全技术专家将Flash 0Day的分析方法开放出来跟大家共享，便于技术人员能够入手Flash 0Day漏洞分析。

0x01 漏洞：Flash 0Day
==================

* * *

自7月5日晚，Hacking Team被Gamma Group Hacker 攻陷以来，其泄露的400GB数据包持续在业界传播发酵，绿盟科技威胁响应中心持续跟踪事态进展，给出系列分析报告 ，同时也将相关解决方案提供给合作伙伴及最终用户，以便用户能够应对可能发生的攻击，此次事件告一段落。今天绿盟科技安全技术人员将针对此次泄露的Flash 0Day漏洞，将分析方法、工具及相关知识分享出来，希望更多的安全行业从业者能够从中有所获益。

1 为什么是Flash 0Dday
-----------------

绿盟科技一直参与微软MAPP计划，该计划里面也包含了Adobe公司爆出的漏洞，通过以往长期跟踪分析的经验来看，Adobe漏洞主要集中在两款产品一个是Abode reader，另一个就是Adobe Flash。此次报告分析的漏洞就是关于后者的漏洞，该漏洞在绿盟科技漏洞库中具有这些标识，CVE-2015-5119，Adobe Flash Player ActionScript 3 ByteArray释放后重用远程漏洞（CVE-2015-5119），BUGTRAQ ID: 75568 ，CVE(CAN) ID: CVE-2015-5119

为什么Hacking Team用了Flash漏洞，是因为Flash漏洞相比其他软件，协议，服务的漏洞要更难分析和利用，一方面可以为黑产竞争者制造壁垒，同时也为分析和防护Flash 0Day提升难度。究其原因有以下几个方面：

*   没有符号表

Flash软件不是微软提供的软件，所以没有提供标准的符号表，较难定位到具体的函数位置，目前做这方面分析的组织不多。

*   虚拟机机制

如今常见的Flash Player都集成了AVM2，将AS编译的字节码直接跑在虚拟机上，由AVM2来解释执行。一方面方便了swf文件的移植，另一方面，相对于分析其他软件的漏洞来说，无疑又是多了一层保护。

*   沙箱机制

Flash安全模型使用安全域的沙箱来分离内容。Flash沙箱除了隔离内容外，还能避免名字冲突（有点类似命名空间）。沙箱系统中不同的安全域使得SWF文件在Flash播放时运作在自身的沙箱里。如果想要突破沙箱机制，需要对Flash沙箱原理要有比较透彻的理解。

*   IE保护机制

现在的Flash一般都嵌入到网页，如果想利用Flash漏洞来获取权限，无疑受到IE等浏览器本身机制的保护，比如IE，Chrome的沙箱机制。这就要求对沙箱机制和如何绕过沙箱有个整体细致的了解，也就是说想通过Flash漏洞来获取更高的权限还是要有更高的功底。

*   没有完整的POC

对于漏洞分析和利用如果没有POC，那也只能靠自己去挖掘这个漏洞; 另一方面如果缺少完整的POC，攻击者只能自己去写代码，所以业界及主管机构都是严格控制POC的传播。

POC的基本功能就是验证并触发该漏洞或是Bug存在，但是能触发漏洞，不代表就一定能利用漏洞；有些漏洞是不能利用，当然我们也可以不管这类漏洞叫漏洞，而只能称之为Bug。但此次泄露出的Flash0day数据，是可以被触发的。

2 漏洞触发
------

那么此次的漏洞如果被触发，会有什么样的结果呢？先来看看漏洞触发后的现象。通过分析，利用该漏洞可以在IE中稳定的执行系统可执行文件，比如在下图中就弹出了计算器。

![enter image description here](http://drops.javaweb.org/uploads/images/16a5480e45d1c78791f5b8f90ccaea4a1bdb460b.jpg)

方法很简单利用构造的test.html加载swf文件，在加载swf文件时IE会提示要加载ActiveX插件，运行就行。加载插件后点击图中的“run calc.exe”按钮即可弹出计算器，漏洞利用成功。这个实验中使用Win7 64位、IE11，能稳定触发漏洞。

3 受影响系统
-------

Adobe Flash Player存在一个严重的释放后重利用内存破坏漏洞，攻击者可能远程获得当前用户的权限。此漏洞影响大量Flash Player版本，此漏洞影响大量Flash Player版本，目前已有可利用的攻击代码公开发布，强烈建议受影响用户更新到当前厂商提供的最新版本。

*   Adobe Flash Player <= 18.0.0.194
*   Adobe Flash Player <= 18.0.0.194
*   Adobe Flash Player Extended Support Release 13.x
*   Adobe Flash Player Extended Support Release 13.0.0.296
*   Adobe Flash Player for Linux 11.x
*   Adobe Flash Player for Linux 11.2.202.468

0x02 攻击：漏洞利用
============

**1 触发原理**

该漏洞是一个典型的UAF释放重利用的漏洞。用户改写字节数组大小，在原来字节数组释放后，重新分配，导致该数值被写入已经释放的内存中，造成释放重利用。

**2 动态调试**

由于Hacking Team泄露出的数据中暴露了Flash 0Day漏洞源码，我们的得以使用CS进行动态调试。

源码级调试分析
-------

利用CS装载源文件中的fla原始档，和其他as文件。生成SWF文件

![enter image description here](http://drops.javaweb.org/uploads/images/6000cacd5a21e1da53317a894aa4fc9ad2643ddb.jpg)

可以看出先是调用了MyClass.as文件中的InitGui函数来初始化GUI元素并输出一些系统相关信息，点击swf文件中的button按钮就会调用相应的处理函数如下图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/9f329e02210eb42f3dab39962f04c1218ea38ac5.jpg)

处理函数btnClickHandler里面首先调用了TryExpl函数如下图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/b8484a1a478adb0b36a0ec7a48caa4cd15c9db8d.jpg)

接下来就看看TryExp1函数里面是怎么样做到漏洞利用的，进入该函数

![enter image description here](http://drops.javaweb.org/uploads/images/7688c6a18d2370023b2b9ea0ce889f49257a1eb7.jpg)

从给出的源码可以看出先是声明了变量alen=90,然后声明一个数组a,并将数组的各元素赋值，在AS中Array数组类型的变量不像C/C++数组一样要求是同一类型的数据在可以放到数组里面，在AS中不同类型的变量对象可以放到同一数组里面。从源码可以看出，a数组的90个元素是MyClass2对象和ByteArray类型数组交替出现，并且每分配两个MyClass2元素才会分配一次BtyeArray类型数组，那么实际运行效果是怎么的呢，我们利用CS调试功能在for结束后的下一条语句下了断点显示如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/87833a54dec4c09580ed0f0b978258456c9d2f3e.jpg)

从图中看出我们在`for(i=alen-5;i>=0;i-=3)`处下了断点，在调试运行后，让a数组填充完毕；左上部紫色的框给出了按钮按下后堆栈中函数调用关系，`btnClinckHandler->TryExp1`。左下方的红框给出了a数组赋值完成后每个元素的实际值，从图中看出，除了a[0]外，每出现一次ByteArray元素要出现两次MyClass2元素，这和我们刚才通过静态代码分析的结果是一致的。

接下来就是一个`for(i=alen-5;i>=0;i=3)`语句，前面知道alen=90那么在第一次循环时`i=85`,通过源代码中的赋值我们知道`a[85]`的大小是`0Xfa0`，源码中将_ba=a[i],也就是第一次将`a[85]`赋给`_ba`(也就是`_ba`大小为`0xfa0`),同时将一个新的Myclass类赋给_ba的第四个字节`_ba[3]`。如下图所示

![enter image description here](http://drops.javaweb.org/uploads/images/f2b87773a7fd6dbe154153b857162f1eb394ae4a.jpg)

接下来就要动态跟踪一下`a[i]`是不是`a[85]`,如果是`a[85]`那么又是什么类型，为了能查看i的值到底是不是`a[85]`,我在源码中添加了一条调试语句`trace(“the number of i =”)`看i的值打印多少，根据之前设置的断点，单步执行源代码，如下图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/634c590db5a68e51ff0dcc1fb9e987355d275cd6.jpg)

从图中可以看出右下方打印出i的值是85，刚好我们分析的一致，从左边图可以看出`a[85]`元素的类型是ByteArray类型。接下来代码中会将MyClass对象赋值给`_ba[3]`。由前面介绍的知识我们知道，在MyClass对象赋给一个基本类型时，会调用ValueOf函数，这里给对象MyClass定义了ValueOf函数，所以在赋值之前会调用该函数。

继续单步跟进`_ba[3]=new MyClass();`调用自定义的ValueOf函数

![enter image description here](http://drops.javaweb.org/uploads/images/3ba239f4bdbb535b7e63c4458e5f11a67eb253db.jpg)

在我们单步跟踪调试ValueOf函数，`_gc`数组除了在`TryExp1`中加入a数组元素外`（_gc.push(a)）`，又通过valueof函数，加入了`-va`元素`(_gc.push(_va))`，这样_gc数组就有两个元素，一个是a数组元素，一个是_va数组元素，每个元素又是数组类型，a数组有90个元素，前面已经介绍过了，_va有5个元素，如图中左边显示的结果。在`TryExp1中_ba=a[i]`大小为0xfa0,在valueof函数中_ba通过`_ba.length=0x1100`会释放调原来的空间而从新分配内存大小。同时通过后面的`_va[i]=new Vector.<uint>(0x3f0)`来重新使用释放的内存。前面我们介绍过，在分配vector类型的空间时其前四个字节是vector大小也就是说，在被释放的空间的开始四个字节会写入`0x3f0`。

而在`_ba[3]=new Myclass()中_ba[3]`实际指向的内存地址还是释放后的内存地址所以在返回40后被释放的内存的数据就是0x400003f0。

UAF漏洞图解
-------

a. 通过a数组创建ByteArray类型元素数据，设置长度为0xfe0：

![enter image description here](http://drops.javaweb.org/uploads/images/247bd41d90cf3fd62b8aaa4a46c153547bde0bcf.jpg)

b.通过调用valueof函数中的_ba.length=0x1100，释放该空间

![enter image description here](http://drops.javaweb.org/uploads/images/a35a5e23f3f32545de9c623884d7a43ec378760e.jpg)

c.调用分配`vector<int>`来占据被释放的内存，由前面的知识，我们知道Uint vector包含了8字节的头部信息，其中开始的4字节是长度字段。

![enter image description here](http://drops.javaweb.org/uploads/images/6abd5d2115ed039ea42249ec6a1520f0b2907712.jpg)

d.在valueof返回0x40后，写入到之前`_ba[3]`指向的地址中

![enter image description here](http://drops.javaweb.org/uploads/images/6ae7c9167510e6fc9405dae57d0382cf21011671.jpg)

动态跟踪查看结果
--------

在Myclass对象调用valueof之前空间内存是esi-3，如下图所示

![enter image description here](http://drops.javaweb.org/uploads/images/494d243013d66e1ba43f0f4720f8ac6439d35f67.jpg)

在调用length=0x1100后，内存空间被释放，申请的`vector<int>`利用释放后的空间，从下图可见vector前四个字节值是0x3f0

![enter image description here](http://drops.javaweb.org/uploads/images/65758e589c3da3bb22eacb67168f923492021ea7.jpg)

在valueof返回后`_ba[3]`指向的第四个字节0x10a70003被赋值为0x40

![enter image description here](http://drops.javaweb.org/uploads/images/5e151cba638d1d0370843ca834311a9a987e8193.jpg)

此时vector的长度字段已经变成了`0x400003f0`

3 提权验证
------

那么利用该漏洞是否可以达到提权的目的呢，让我们来验证一下。利用windows 7自带的IIS服务搭建一个Web服务，将test.html和exp1.swf放在web服务目录中同时将test.html中对exp1.swf引用改为绝对地址引用，这样在访问test.html时方便加载exp1.swf。设置IE启动保护模式，同时需要启动ProcessExplorer工具来监控IE进程和进程的权限等级。

![enter image description here](http://drops.javaweb.org/uploads/images/6e4a79c8161239467b5171eba6ad7f40f9d99aa0.jpg)

从ProcessExplorer结果来看,进程ID为1792的iexplore是沙箱进程，产生的子进程6512是在访问test.html是生成的一个Tab，如下图

![enter image description here](http://drops.javaweb.org/uploads/images/5eee4125623b782805b96a6d66062c0e62205ada.jpg)

当然有多个IE Tab标签时会有多个子进程，同时受到一个沙箱进程的保护，从图中看出沙箱进程等级是Medium，属于标准用户权限等级，而子进程6512则是low等级，是沙箱中的IE TAB进程的默认等级，IE沙箱中的IE TAB进程默认等级就是低。从图中可以看出，IE TAB子进程产生的calc子进程也是low。

4 利用形式
------

由此上面的分析，我们可以看出利用该漏洞并未达到权限提升的效果，也就是说，攻击者单独使用这个Flash 0Day漏洞是无法获得高权限的，它只是创建了一个低等级的进程，需要结合其他方法来提权，比如此次泄露数据中的windows内核字体权限漏洞，利用此内核漏洞是很容易提升权限的。

同时，结合之前我们对Hacking Team远程控制软件的分析 ，可以看到其代理有两种安装方式：

感染移动介质

与很多木马、病毒及流氓软件的传播方式一样，该软件首先还是采取这种低成本的方式进行，感染一些能够接触目标的移动媒体，比如CD-ROM、USB等，即便是OS 或者BIOS设置了密码也一样可以感染，从而获取一些环境数据，比如电脑是否可以上网等，为后续的动作提供参考依据。

代理攻击

采用软件或硬件的系统，能够在网络会话过程中修改和注入数据，在某些情况下，可以注入到系统并难以被检测到。同时，也能够感染Windows平台上的可执行文件，如果目标电脑从网站上下载并执行这些可执行文件时，Agent将在后台自动安装，用户不会知晓。

那么，我们这里可就可以画出一张可能的入侵乃至实现监控目的链条：

![enter image description here](http://drops.javaweb.org/uploads/images/bec18a07f2c659d94e69fa9db8ea7c10c331c266.jpg)

0x03 防护：思路及建议
=============

* * *

思路
--

万变不离其宗，在上面的攻击链条中，有很关键的一条，用户需要执行恶意代码，漏洞利用才能成功，那么从防护的角度来说至少需要有这些层面

1.  要能够侦测到恶意的Flash脚本；
2.  要能够阻断Flash脚本的执行；
3.  即便在执行后能够查杀恶意进程。

值得一提的是，从下面的截图中可以看到在大家四处下载400GB泄露数据包的时候，恶意swf就藏在这些网站页面中，从这一点就可以看到其攻击目标很明确，针对中间环节的攻击从未停止。请下载这些数据包的人需要小心谨慎，不要四处传播这些数据包。

![enter image description here](http://drops.javaweb.org/uploads/images/fa96077d85bc587e58ab7eca7ef82bdac70d9bb4.jpg)

在上次防护方案 中，我们也提出用Intrusion Kill Chain模型 来进行Flash 0Day乃至后续攻击的防护方案的参考，具体的分析请参考那篇报告。

建议
--

同时，从用户的角度来说，建议您可以采取如下方式来防御Flash 0Day漏洞以及以后的类似漏洞

1.  建议您升级最新的Flash Player，具体请访问：https://get.adobe.com/flashplayer/?loc=cn
2.  建议您升级最新的安全产品规则库，具体请访问：http://update.nsfocus.com/
3.  建议您安装or升级最新杀毒软件，比如使用安全级别更高的猎豹, FireFox浏览器
4.  如果上面的措施实施需要一定时间，建议您暂时禁用Flash插件