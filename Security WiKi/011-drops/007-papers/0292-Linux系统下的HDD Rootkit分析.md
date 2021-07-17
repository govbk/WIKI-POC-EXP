# Linux系统下的HDD Rootkit分析

0x01 概况
=======

* * *

前段时间，卡巴斯基捕获到Winnti网络犯罪组织在Windows下进行APT攻击的通用工具——HDD Rootkit。近期，腾讯反病毒实验室在Linux系统下也捕获到同类工具。Winnti组织利用HDD Rootkit在Windows和Linux系统下进行持续而隐蔽的APT攻击。经分析发现，HDD Rootkit先是篡改系统的引导区，然后在进入Linux系统前利用自带的Ext文件系统解析模块，将隐藏在硬盘深处的后门文件解密出来后加入到开机启动脚本或系统服务里。目前受攻击的系统有Centos和Ubuntu。

![](http://drops.javaweb.org/uploads/images/e345e07d9a583750cf26e733099a62e596a9db72.jpg)

(图1：HDD Rootkit在Linux下的攻击流程)

0x02 HDD Rootkit在 Linux下的详细分析
=============================

* * *

1、过程展示
------

分析HDD Rootkit：

![](http://drops.javaweb.org/uploads/images/b951b8e68a53c148c8e378e7ced6e5d2bede17f4.jpg)

（图2：分析HDD Rootkit得到的参数提示）

运行HDD Rootkit：

![](http://drops.javaweb.org/uploads/images/67130cf8f470e7538087f19c6fb4379d2e6e61b6.jpg)

(图3：运行HDD Rootkit工具)

通过图3，能看出HDD Rootkit平台已经把RKimage和Backdoor解密并写入扇区里面，而且计算了他们的Crc16值(这部分后面有更详细的分析）。接下来我们看看mbr的变化：一是第一扇区已经被改写(如图4)；二是开机瞬间显示出HDD Rootkit的调试信息（如图5）。当系统中毒以后,第1扇区存放病毒的MBR，第25扇区存放BootCode，第26与第27扇区存放加密后的原始MBR。

![](http://drops.javaweb.org/uploads/images/d8d5818aa1c976eaa6901d69c760712eceebff71.jpg)

（图4： 左边是被修改的mbr，右边是原始的mbr）

![](http://drops.javaweb.org/uploads/images/281d82dd49e44b943682ef4794161ddee94d121b.jpg)

（图5：开机时RKimage的输出信息，注意：debug版本才有信息输出）

2、安装阶段详细分析
----------

### (1) 运行安装方式与参数：

![](http://drops.javaweb.org/uploads/images/a57f7b9a770741d286359ce586ca9c261266febc.jpg)

（图6：hdroot_32_bin安装方式）

在Linux下运行HDD Rootkit 如`./root_32_bin inst ./createfile 1`。其中第一个参数是安装类型，第二个参数是后门文件，第三个参数是启动类型(共三种开机启动方式)。

### (2) HDD Rootkit的文件存储和隐藏：

HDD Rootkit早期的版本是把MBR、Boot Code、RKimage等放在程序资源里面，在Linux系统下则是把这些文件加密存储在安装器里面。以下分析HDD Rootkit如何将加密好的MBR、Boot Code、RKimage解密出来，又重新加密写入到第一个扇区和空闲的扇区里面。

![](http://drops.javaweb.org/uploads/images/c0893fc158606e79ad1c3cc00910eab7640c8580.jpg)

(图7：左边是加密的结构体，右边是解密过程)

HDD Rootkit将Rkimage 和Backdoor再次加密后写入扇区，将后门文件藏得更深。

![](http://drops.javaweb.org/uploads/images/0c77589d2002e154fdfc8cfaedcb6062168896c1.jpg)

(图8：将RKimage和Backdoor文件写入扇区)

获取引导盘，准备写入MBR和Bootcode，步骤如图9和图10所示。

![](http://drops.javaweb.org/uploads/images/4870af7c1146eb5ca2b215cd7badf98ae0228ec1.jpg)

(图9：步骤一)

![](http://drops.javaweb.org/uploads/images/4585be92de4e0f8bc427e7dc110a214b0eb2c85c.jpg)

(图10：步骤二)

### (3) RKimage 功能分析

RKimage是HDD Rootkit下释放的子工具。RKimage不依赖于操作系统，直接解析文件系统，能根据不同的安装情况，把后门加入开机启动。

RKimage模块：

1.  由Bootcode拉起，将实模式切换到保护模式；
2.  实现Ext文件系统解析与读写功能；
3.  把隐藏在扇区的后门写成文件，根据不同的情况增加开机启动项。

![](http://drops.javaweb.org/uploads/images/6927b73c57a0eed73612b2275f4d09227ca66f9e.jpg)

(图11：RKimage的文件系统解析模块的字符串提示)

第一种开机启动方式：

![](http://drops.javaweb.org/uploads/images/369d9cda78ec3f7a600f98d404971e6f709969ac.jpg)

(图12：`/etc/rc*.d/S7*cdiskmon`类型)

第二种开机启动方式：

![](http://drops.javaweb.org/uploads/images/31b415a1736ec805f91f4fb9d281cd63902050cc.jpg)

(图13：`/etc/rc.d/rc.local`类型)

第三种开机启动方式：

![](http://drops.javaweb.org/uploads/images/5bb9a375f0ff5f153243d460e1634f0a1255a969.jpg)

(图14：SYSTEMD类型)

### (4) 后门文件

由于获取的程序样本有限，在分析过程中并没有获取真正有效的Backdoor文件，所以整个攻击的完整流程和木马如何把信息向外通信并未分析到。因此，自主构造了一个写文件的可执行程序。

3、 调试 HDD Rootkit的MBR、Bootcode、RKImage关键节点
------------------------------------------

![](http://drops.javaweb.org/uploads/images/a34aac47cf5419e2f9505ced8a8c3fc2141c1fa4.jpg)

(图15：中毒后的第一扇区)

![](http://drops.javaweb.org/uploads/images/c337b30f621211c5dc5c7bac678f299f0537a197.jpg)

(图16：HDD加载Bootcode)

![](http://drops.javaweb.org/uploads/images/54087e1f33a774a73bff6f903d8b77df1790f59b.jpg)

(图17：从Bootcode进入到RKimage模块)

![](http://drops.javaweb.org/uploads/images/ff7ed692160fdd3970bfd9070dedbf7be1406a7f.jpg)

(图18：RKimage模块加载GDTR)

![](http://drops.javaweb.org/uploads/images/c2305602af2d61dd18947e085fecccf2b85df566.jpg)

(图19：RKimage模块里面准备切换到保护模式)

![](http://drops.javaweb.org/uploads/images/172ba9e72968ea75515c6dab4eaa1e1b56fc8648.jpg)

(图20：RKimage模块准备执行功能)

![](http://drops.javaweb.org/uploads/images/85277da81cbcae7a39b02b9c0096e71fdbe8dee7.jpg)

(图21：RKimage模块输出功能代码的调息信息)