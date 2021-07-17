# Win10安全特性之执行流保护

0x00 背景
=======

* * *

微软在2015年1月22日公布了windows10技术预览版，Build号：9926。电脑管家反病毒实验室第一时间对其引入的新安全特性进行了深入分析。

众所周知，漏洞利用过程中攻击者若要执行恶意代码，需要破坏程序原有指令的的正常执行。执行流保护的作用就是在程序执行的过程中检测指令流的正常性，当发生不符合预期的情况时，及时进行异常处理。业界针对执行流保护已经有一些相对成熟的技术方案，在微软发布的windows10最新版本中，我们看到了这一防护思想的广泛使用。

0x01 CFI
========

* * *

CFI即控制流完整性Control-Flow Integrity，主要是通过对二进制可执行文件的动态改写，以此为其增加额外的安全性保障。

![enter image description here](http://drops.javaweb.org/uploads/images/bac796ce306d49ee5bd1105cd0f827debd950807.jpg)

这是Mihai Budiu介绍CFI技术时使用的例子。这里通过对二进制可执行文件的改写，对jmp的目的地址前插入一个在改写时约定好的校验ID，在jmp的时候看目的地址前的数据是不是我们约定好的校验ID，如果不是则进入错误处理流程。

同理在call 和 ret的时候也可以进行改写：

![enter image description here](http://drops.javaweb.org/uploads/images/a4c35da3d83699aa58f4f66467f56b2d0ef433a0.jpg)

左半部分就是一个对call的改写，右半部分是对ret的一个改写，在call的目的地址和ret的返回地址之前插入校验ID，然后改写的call 和ret中增加了对校验ID的检查，如果不符合预期，进入错误处理流程，这个思路和上边对jmp的处理是完全一样的。

0x02 CFG
========

* * *

实现CFI需要在jmp、call 一个寄存器（或者使用寄存器间接寻址）的时候，目的地址有时必须通过动态获得，且改写的开销又很大，这些都给CFI的实际应用造成了一定的困难。

微软在最新的操作系统win10当中，对基于执行流防护的实际应用中采用了CFG技术。CFG是Control Flow Guard的缩写，就是控制流保护，它是一种编译器和操作系统相结合的防护手段，目的在于防止不可信的间接调用。

漏洞攻击过程中，常见的利用手法是通过溢出覆盖或者直接篡改某个寄存器的值，篡改间接调用的地址，进而控制了程序的执行流程。CFG通过在编译和链接期间，记录下所有的间接调用信息，并把他们记录在最终的可执行文件中，并且在所有的间接调用之前插入额外的校验，当间接调用的地址被篡改时，会触发一个异常，操作系统介入处理。

以win10 preview 9926中IE11的Spartan html解析模块为例，看一下CFG的具体情况：

![enter image description here](http://drops.javaweb.org/uploads/images/8cfc058065c3677fc9f3a5ed6432a8ecd0b454f1.jpg)

这里就是被编译器插入的CFG校验函数

![enter image description here](http://drops.javaweb.org/uploads/images/0a35dd5ba467d717ff7ee69a8d0fab63f9f326f8.jpg)

但是静态情况下默认的检测函数是一个直接return的空函数，是微软在和我们开玩笑吗？

![enter image description here](http://drops.javaweb.org/uploads/images/6d4b06a16704f75e5d8d3c77987ac1bc248545e8.jpg)

通过动态调试看一下

![enter image description here](http://drops.javaweb.org/uploads/images/33445981422a99a6204f5956e7067a1a8d1a2193.jpg)

从上图我们可以看出，实际运行时的地址和我们通过IDA静态看到的地址是不一样的，这里就涉及到CFG和操作系统相关的那部分。支持CFG版本的操作系统加载器在加载支持CFG的模块时，会把这个地址替换成ntdll中的一个函数地址。不支持CFG版本的操作系统不用理会这个检测，程序执行时直接retn。

这是ntdll中的检测函数

![enter image description here](http://drops.javaweb.org/uploads/images/d48531328e7fac5a1d5bc91b6dcc44159e051301.jpg)

原理是在进入检测函数之前，把即将call的寄存器值（或者是带偏移的寄存器间接寻址）赋值给ecx，在检测函数中通过编译期间记录的数据，来校验这个值是否有效。

检测过程如下:

首先从LdrSystemDllInitBlock+0x60处读取一个位图(bitmap)，这个位图表明了哪些函数地址是有效的，通过间接调用的函数地址的高3个字节作为一个索引，获取该函数地址所在的位图的一个DWORD值，一共32位，证明1位代表了8个字节，但一般来说间接调用的函数地址都是0x10对齐的，因此一般奇数位是不使用的。

通过函数地址的高3个字节作为索引拿到了一个所在的位图的DWORD值，然后检查低1字节的0-3位是否为0，如果为0，证明函数是0x10对齐的，则用3-7bit共5个bit就作为这个DWORD值的索引，这样通过一个函数地址就能找到位图中所对应的位了。如果置位了，表明函数地址有效，反之则会触发异常。

这里有个有趣的东西，虽然使用test cl,0Fh检测是否0x10对齐，如果对齐的话实际上用3-7位作为索引，也就是说第3位一定是0。但如果函数地址不是0x10对齐的话，则会对3-7位 or 1，然后再作为索引。这样就有一个弊端，如果一个有效的间接调用的函数地址是8字节对齐的，那么其实是允许一个8字节的一个错位调用的，这样可能导致的结果就是可能造成虽然通过了校验，但是实际调用的地址并不是原始记录的函数地址。

还有一点，如果这时候漏洞触发成功，间接调用的寄存器值已经被攻击者修改了，这时候从bitmap中取值的时候可能造成内存访问无效。请看LdrpValidateUserCallTargetBitMapCheck符

号处的这条指令：mov edx,dword ptr [edx+eax*4] edx是bitmap地址,eax是索引，但如果eax不可信了，这个很有可能，则会导致内存访问异常，并且这个函数并没有异常处理。这是因为微软为了效率考虑（毕竟这个校验函数的调用十分频繁，一个开启CFG的模块可能会有上万个调用处），微软在ntdll! RtlDispatchException中对该地址发生的异常做了一个处理:

![enter image description here](http://drops.javaweb.org/uploads/images/6c2ff8814d25b05b4053cd2e3612d6c2a5b8c17c.jpg)

如果异常发生的地址命中LdrpValidateUserCallTargetBitMapCheck，则进行一个单独处理，RtlpHandleInvalidUserCallTarget会校验当前进程的DEP状态和要间接调用的地址(ecx)的内存属性，如果当前进程关闭了DEP并且要间接调用的地址有可执行属性，则触发CFG异常，否则通过修改pContext把EIP修正到ret返回处，并且表明异常已被处理。

最后再说下这个原始的bitmap，在系统初始化的时候，内存管理器初始化中会创建一个Section(MiCfgBitMapSection32)，这个Section在Win8.1上的大小是通过MmSystemRangeStart(32位下是0x80000000)计算的，前面提到过bitmap里面1位代表8字节，计算完后正好是32MB

![enter image description here](http://drops.javaweb.org/uploads/images/fae4d972d4b0f9bc63f7914a7a7dd08f0b9b460f.jpg)

而在Win10上MiCfgBitMapSection32的大小有了变化，直接写死成了0x3000000(48MB)

![enter image description here](http://drops.javaweb.org/uploads/images/78cd3084c5a080995821382ca3381611f09121e9.jpg)

Section创建完成后在每个进程启动的时候会映射进去

```
(NtCreateUserProcess-> PspAllocateProcess-> MmInitializeProcessAddressSpace-> MiMapProcessExecutable-> MiCfgInitializeProcess)

```

映射的时候作为shared view，除非某一个进程修改了这片内存。

在一个CFG模块映射进来的时候，重定位过程中会重新解析PE文件LOADCONFIG中的Guard Function Table以重新计算该模块对应的bitmap（MiParseImageCfgBits），最后更新到MiCfgBitMapSection32中去（MiUpdateCfgSystemWideBitmap）。

0x03 电脑管家XP防护的执行流保护
===================

* * *

早些年的漏洞攻击代码可以直接在栈空间或堆空间执行指令，但近几年，微软操作系统在安全性方面逐渐加强，DEP、ASLR等防护手段的应用，使得攻击者必须借助ROP等绕过手段来实现漏洞利用。在ROP利用中，栈交换指令Stack pivot必不可少。

针对ROP攻击的防御长久以来是漏洞防御的一个难题，因为ROP指令在静态层面分析与程序的正常指令流毫无差别，且运行时也是在合法模块内执行，因此极难防御。

管家漏洞防御团队针对ROP利用的特点，从整个程序的执行流层面进行分析，研究出在动态运行时区分是合法指令流还是异常指令流的方法，其思想与CFI不谋而合。

下边就是一个由于错位汇编形成的比较常用的栈交换指令

![enter image description here](http://drops.javaweb.org/uploads/images/68db5159b9db464cf57d1608668c0c42df375608.jpg)

而实际正常的执行流程是这样的

![enter image description here](http://drops.javaweb.org/uploads/images/4ad4699a06ba68f70621d1185850e2c3bb23f9c8.jpg)

以上是没有开启XP防护的情况

开启电脑管家XP防护之后：

![enter image description here](http://drops.javaweb.org/uploads/images/f7b2d81c87acf45267077f7ad4746b98920c6314.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/33777c002fd6430df3d4c1eb4413748d030d5a14.jpg)

此时如果攻击者依靠静态分析时得到栈交换指令位置来执行ROP攻击的话，会被执行流保护逻辑发现异常，后续攻击则无法实现。

0x04 尾声
=======

* * *

CFG防护方法需要在编译链接阶段来完成准备工作，同时需要操作系统的支持。CFI无需编译时的帮助，且不仅能够防御call调用，能够对全部执行流进行保护。但CFI需要插入大量的检测点，并且在执行过程中检测的频率极高，难免对程序执行效率带来影响。

电脑管家XP版的防御方法相比于前两者，对性能的影响更小，但这种方法是针对旧版操作系统的缓解方案，通用性会打折扣。所以建议广大windows用户尽量升级到最新操作系统，享受全面的安全保护。而由于某些原因无法升级的用户也不必担心，管家XP版会继续提供最高的安全防护能力。