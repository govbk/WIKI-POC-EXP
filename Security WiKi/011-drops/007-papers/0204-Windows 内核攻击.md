# Windows 内核攻击

0x00 引言
=======

* * *

作者：Ashfaq Ansari

本文总结了目前windows内核攻击的各种攻击技术.描述并演示了一些常见的绕过windows内核防护的方法，并举一反三地介绍了如何通过内核缺陷找到类似的绕过方法。 通过对内核攻击和内存结构的理解将会进一步丰富基于用户模式应用程序的缓冲溢出知识。

通过大量内核漏洞的研究表明，特定的内核代码执行可能大多由用户模式的应用程序引起。因此，针对用户模式的应用程序，操作系统增加了大量的保护机制，用以保护和检测这类的攻击，比如：随机化、执行保护、内存防护等等。然而，针对操作系统溢出攻击，目前所做的工作还远远不够。 本文将讨论交流各种内核攻击技术和一些可能的内核攻击方法

0x01 环境配置
=========

* * *

所有的演示都基于Windows 7 x86 SP1环境下编译的特意存在漏洞的驱动，本文将通过该驱动存在的漏洞来展示内核缺陷以及如果通过内核攻击技术来进行本地权限提升。

所需工具:

*   Windows 7 操作系统
    
*   虚拟机
    
*   一个存在漏洞的驱动
    
*   Windows 内核调试器 – WinDBG
    

备注: 设置调试器管道名为`\.\pipe\com1`，同时被调试端也同样设置.

0x02 Windows 内核结构
=================

* * *

在开始攻击之旅之前，我们先了解一下内核基本结构和windows进程空间的内存分配和执行方式。Windows操作系统有两个模式：内核模式和用户模式。任何一个程序都是在其中一个模式里执行。

![enter image description here](http://drops.javaweb.org/uploads/images/790ac09e7ec078fad99ee78a70e520c70785ac61.jpg)

图 1: Windows 结构 来自: logs.msdn.com

HAL: Hardware Abstraction Layer 硬件抽象层 –一组程序例程，使软件可跨平台移植; HalDispatchTable 保存着一些 HAL例程的地址。

0x03 堆栈溢出
=========

* * *

当拷贝用户输入数据到事先分配的一个缓冲空间里时，如果没有做边界检查，就会发生栈溢出。 memcpy()函数在进行内存拷贝的时候不会做长度检查，如果拷贝过长的数据到预先定义的缓冲变量里，就会导致溢出的发生。

以下是一个用了 memcpy() 函数的程序。

![enter image description here](http://drops.javaweb.org/uploads/images/6da11286134822d545a119fd469b6713ea390e3c.jpg)

图 2: StackOverflow.c

首先我们用大量的数据溢出它并且覆盖掉返回地址。 这样我们就会控制了程序后面要执行的指令。 我们用大量字符‘A’成功使栈发生了崩溃。 然而, 为了找到返回地址的精确位置，我们需要发送一组特定模式的数据来匹配到返回地址（译者注：可以是这样AAAABBBBCCCCDDDD…）。

通过溢出代码构造了一组输入数据，我们找到了返回地址的偏移如图:

![enter image description here](http://drops.javaweb.org/uploads/images/1c59cc9a700991c8cd2c0d9eca0e5243d5c99c8e.jpg)

图 3: 定位EIP

如上所示, EIP被 72433372 覆盖(内存地址左高位，右低位，对于字符是 72334372 ).然后定位到覆盖EIP的位置是字符串长度为2080的地方。

在我们的溢出代码里, 我们通过变量ring0_shellcode’定义了 shellcode 如下：

![enter image description here](http://drops.javaweb.org/uploads/images/c4ac44e9115d115a3784dc1c39179d3214fcb656.jpg)

图 4:  Shellcode

我们把shellcode地址放入我们溢出代码的缓冲区里，通过使shellcode地址覆盖返回地址，这样SHELLCODE得以执行以后，我们以用户模式启动的程序最终将以内核模式执行。

备注: 首先, 我们用Python脚本找到shellcode在内存的地址，例如：

```
ring0_shellcode_address = id(ring0_shellcode) + 20 //id(var) + 20

```

接着,把SHELLCODE地址放到可以覆盖返回地址的地方（上述找到的EIP偏移）。溢出代码执行后会调用SHELLCODE，这时会开启一个以系统权限执行的命令行SHELL，如图:

![enter image description here](http://drops.javaweb.org/uploads/images/101bac7ffbf545898a505589a136d318c7fb3078.jpg)

0x04 堆栈保护绕过
===========

* * *

为了抵御堆栈溢出攻击，产生了一种保护机制：Stack Guard. 这种机制使得执行函数增加了两个元素：function_prologue和function_epilogue。Stack Guard 实际是通过编译时在这个两个元素处增加代码以设置和检验栈信息(保存在Canary里)。

Function prologue

![enter image description here](http://drops.javaweb.org/uploads/images/7e663bfd07b32b13108098f51325ae01808da593.jpg)

图 6: _except_handler4

Function Epilogue

![enter image description here](http://drops.javaweb.org/uploads/images/95156c75e74d235787201657ec71b2cb9f3bd363.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8ae076430c214b43438ab3736dd44a374a00eb9e.jpg)

图8: Security Cookie效验

参照上面的程序，我们发现每次通过传统方式覆盖堆栈的时候, 我们也不得不同时覆盖掉Stack Cookie。 除非我们用正确的栈信息来覆盖Canary, 否则在函数尾的检查将失败并且程序会终止。

解决方法

我们将通过溢出覆盖异常处理函数地址的方法来绕过 Stack Cookie保护。 异常处理函数地址存放在堆栈里，我们可以任意的覆盖堆栈，当从用户空间传递大量数据到内核缓冲区的时候，我们把SHELLCODE地址覆盖掉异常处理函数的地址，这时触发异常并跳转去执行我们的SHELLCODE代码。

![enter image description here](http://drops.javaweb.org/uploads/images/c21c022e68a18f4563205a6d35d37eefe653f0c8.jpg)

图 9: 堆栈溢出防护绕过

根据攻击代码，绕过 Stack Guard 后执行INT 3指令，观察调试信息如图:

![enter image description here](http://drops.javaweb.org/uploads/images/6d7840febb41215eaa915ccc351a1dc5e383a3d0.jpg)

图 10: 绕过 stack Guard

![enter image description here](http://drops.javaweb.org/uploads/images/090a5cf7cff6e4c79222aad05aee2b863eca7f71.jpg)

图11: 执行shellcode并停止在断点

0x05 任意改写
=========

* * *

这个漏洞也被称作: WRITE_WHAT_WHERE,可以使攻击者可以在任意内存写任意内容。 如果操作不当会导致程序崩溃（用户模式）或者蓝屏（内核模式BSOD）。

通常这里会有一些现限制

*   Value – 可以写什么样的内容
    
*   Size – 可写内存的大小
    
*   而且有时只能递增或递减内存
    

这类漏洞相比其他已知类型漏洞比较难以发现， 但是对于恶意代码执行非常有用。 这里有许多可改写导致代码执行的地方，比如： HalDispatchTable+4, 系统中断表Interrupt Dispatch Table, 系统服务表System Service Dispatch Table等等。

如下是 WRITE_WHAT_WHERE 漏洞的结构:

![enter image description here](http://drops.javaweb.org/uploads/images/8694d93154722e3062c362827d931b583be88352.jpg)

既然漏洞允许我们自定义上述结构中的What和Where属性, 我们把我们的shellcode地址写在‘What’处，把 HalDispatchTable0x4 的地址写在‘Where’ 处，如下:

![enter image description here](http://drops.javaweb.org/uploads/images/cae8baee63a40a8af3225c85cadddaa844ef1c23.jpg)

图 13: 部署shellcode 地址和HAL Dispatch Table地址

我们在内核调试器中断程序，检查HalDispatch Table 函数地址如下:

![enter image description here](http://drops.javaweb.org/uploads/images/4f8a357bc5681f3f28554cbfc658e30616e202f0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b2f70427f0a984cb8ee6edbdda7dee89420a31d0.jpg)

图 15: Write_What_Where执行演示

Exploit执行后,我们在调试器检查内存发现， HalDispatchTable+4处地址被SHELLCODE地址覆盖， 然后SHELLCODE被执行。 下面对话框显示程序在断点处中断。

![enter image description here](http://drops.javaweb.org/uploads/images/56a7f9d9a75d1ba0b63e75551aa44c1546daeea5.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f19c66d342adae3d48902ffb686e89177fd91e39.jpg)

图 17: 改写后断点处的EIP

最后PAYLOAD里的shellcode将利用任意改写漏洞得以执行.

0x06 Use After Free 漏洞利用
========================

* * *

当一个程序使用已经被释放后的内存时，会导致意外的系统行为，如异常或可以用来获得任意代码执行。此类漏洞需要如下条件:

![enter image description here](http://drops.javaweb.org/uploads/images/639a6302f34628ff5f7af895173aceeb9c7c78dc.jpg)

某些时候一个对象被创建，同时与一个虚表关联，然后程序会通过某个方法来调用这个对象。如果在程序调用对象之前，我们把这个对象释放，当程序调用该对象时就会导致程序崩溃。

这种情况下, 攻击者布置好内存。然后, 分配类似大小的对象。接着, 攻击者尝试释放一些对象来制造一个内存“孔”。 然后, 然后分配和释放弱点对象,最后攻击者填充这些“孔”，来接管弱点对象的内存空间。这类漏洞难以被发现和利用，并且需要一定条件:

*   Shellcode指针必须放在被释放的对象的内存空间。
    
*   创建的“孔”的大小必须和释放的对象的大小相等。
    
*   不应有相邻的内存块被释放以防止Coalescing。
    

Coalescing: 当两个独立且相邻的内存块被释放，操作系统会连接这些小内存块，以创建一个大的内存块，用以防止内存碎片。 这个过程叫Coalescing，它使Use After free漏洞攻击变得更加困难。因此，内存管理器不会分配特定的内存，攻击者获得相同内存空间的机会很少。

如下给出了一个存在该漏洞的案例（内核下C函数）:

首先我们让被调试端/目标以guest权限运行。 我们首先必须在内核池分配一个弱点对象，以触发Use After free漏洞, 然后释放它并强制使程序使用这个被释放的对象。

![enter image description here](http://drops.javaweb.org/uploads/images/cd47828510d0e04c54066a673031b6e1494edabd.jpg)

图 18:Use After Free 对象被分配.等待释放.

接下来, 我们释放对象以创建内存“孔”.最后,我们填充所有被释放的内存块以控制被释放对象的内存，需要花费一定的时间来实现内存控制，大概需要尝试100次左右。 我们通常通过一个FakeObject来重新分配 UaF对象。

![enter image description here](http://drops.javaweb.org/uploads/images/b98cfd960c9213b1d2c54a5fe1dc522b126e5d04.jpg)

图 19: 释放并重新分配 UAF 对象

![enter image description here](http://drops.javaweb.org/uploads/images/0bfa5d5519b9a5c669dce9313caf08fb5fbd4805.jpg)

图 20: 释放并重新分配 UAF 对象

同时, 这些内存块会被攻击者控制的对象填充。这个时候我们看一下内存池, 我们会发现我们已经成功地重新分配了我们创建的内存“孔”。

![enter image description here](http://drops.javaweb.org/uploads/images/956ad57d1c818ebecbf65d2cefa4f41880a68f6a.jpg)

图 21: 所有连续的内存块都被 IoCo填充以确保内存被均匀喷射

最后触发使用被释放的UaF对象，导致漏洞产生。 攻击代码执行后，会生成一个系统权限的SHELL， 如图:

![enter image description here](http://drops.javaweb.org/uploads/images/f7a9193e782a94b66dc083c39a5988f685c8e500.jpg)

图 22: 攻击者代码以系统权限执行

0x07 用内核调试器偷令牌
==============

* * *

另一个有趣的漏洞是，可以利用内核缺陷通过进程令牌来提升权限。

下面的部分，我们说明了攻击者如何从一个更高的或者不同特权的级别偷取令牌 ，然后进行权限提升或者使自身拥有和其他进程一样的权限。尽管有很多已知的内核防护机制，比如ASLR、 DEP、 Safe SHE、SEHOP等等，但在内核中使用这些漏洞, 任何一个进程都可以被赋予系统权限。

下面将一步一步针对权限较低的用户 ‘Guest‘，来说明利用令牌漏洞进行权限提升的过程。 我们将用内核调试器会话来提升cmd.exe 进程的权限，使它从Administrator权限到SYSTEM 权限。

用内核调试器找到当前正在运行的进程和他们的属性，如下-

```
For cmd.exe
For SYSTEM

```

现在我们知道了系统进程的令牌, 我们可以切换到 cmd.exe 进程 并找到这个进程令牌的位置。

*   从上面找到的地址中获得KPCR 结构
    
*   在偏移 +0x120 获得KTHREAD成员 CurrentThread的地址
    
*   获得KAPC_STATE成员 ApcState的地址。 它包含一个指向 KPROCESS的指针
    
*   获得KPROCESS成员 Process的地址。 它包含令牌值，在KTHREAD 基址偏移+0x40处
    

![enter image description here](http://drops.javaweb.org/uploads/images/a0e07aa416106ec6f70244f47d5d43074b44aa4b.jpg)

图 23: KAPC List Entry

*   从 EPROCESS 结构获得Token 成员的偏移。 KPROCESS是EPROCESS的第一个结构
    
*   获得Token值
    

实际的令牌值需要把最后3位和0进行与操作，然后令牌值0x953b6037变为 0x953b6030 现在我们用系统令牌替换掉进程令牌。

![enter image description here](http://drops.javaweb.org/uploads/images/284dc70783f9531f57b371bbfebada0ba0e076d7.jpg)

图 24: 令牌值被替换

令牌被替换后，进程马上就被赋予了系统权限。 在被攻击者电脑里验证如下:

![enter image description here](http://drops.javaweb.org/uploads/images/8cf733ed647529e097415b47ce12a7723b2104b9.jpg)

图 25: 通过令牌漏洞提升Guest到系统权限

![enter image description here](http://drops.javaweb.org/uploads/images/39488f525c1591d8c405bbfa5c692cdacb364fd8.jpg)

图 26: 一个例子: 利用令牌漏洞对Guest用户进行权限提升