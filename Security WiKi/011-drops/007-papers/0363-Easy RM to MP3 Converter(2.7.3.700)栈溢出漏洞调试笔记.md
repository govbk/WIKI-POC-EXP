# Easy RM to MP3 Converter(2.7.3.700)栈溢出漏洞调试笔记

0x00 基础知识
---------

* * *

### 1 Windows环境

选取wmplayer.exe程序运行时的内存布局示意，包括栈，堆，加载模块（DLLs）和可执行文件本身。

![enter image description here](http://drops.javaweb.org/uploads/images/8a1bc8d77d31f51e5dc0ade3972fbae522c4d38c.jpg)

Win32进程空间布局示意。

![enter image description here](http://drops.javaweb.org/uploads/images/9ddb1e02815ac5b8797904eabfe511a9c6887e36.jpg)

#### 1.2 入口点（Entrypoint）

运行一个EXE的时候，会先根据IAT表加载相应的DLL，并且用GetProcAddress得到API的真实地址。也就是说EXE运行后，DLL的EP将是第一个被调用的地方，而EXE本身的EP应该是最后被调用的，但它是EXE本身代码的入口。

不同系统平台下反汇编结果。本节程序选取《逆向工程核心原理》一书中的HelloWorld.exe进行调试示意。

Windows Server 2008下反汇编结果（存在地址随机化，相同的exe程序，载入调试器后入口地址与XP下不同）。

![enter image description here](http://drops.javaweb.org/uploads/images/c4b06f6fe8da9ca39a5ef84845661c9acb78a6e3.jpg)

Windows XP下反汇编结果。

![enter image description here](http://drops.javaweb.org/uploads/images/958792086c02d5b7b80b7a7a1def00513b5881a7.jpg)

F7 Step into。

![enter image description here](http://drops.javaweb.org/uploads/images/deffd1d54e434ea1c78681631af852748159ea52.jpg)

004027A1地址处的RETN指令，用于返回到函数调用者的下一条指令（弹出ESP内容到EIP，然后跳转，0012FFC0处的值是004011A5，小端排序），一般是被调用函数的最后一句，即返回004011A5（JMP 0040104F）

![enter image description here](http://drops.javaweb.org/uploads/images/d47fa28841f741e5e00d69b8a780e1e6614a83c0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/4fb14c7b558e81e11e88e3dd537f17b6d4ef7fcc.jpg)

EIP值为004011A5，ESP指针继续向下移动，ESP从0012FFC0指向0012FFC4（ESP+4）。

![enter image description here](http://drops.javaweb.org/uploads/images/fb1f3d02756b76d651c0ba102b0ba45cdf4e7ade.jpg)

不同的开发工具生成的启动函数不同。同一种开发工具，产生的启动函数也随版本的不同而不同。

![enter image description here](http://drops.javaweb.org/uploads/images/a2e5735a3a4a6da1ecf38cd1e4cfebe9021f5060.jpg)

Call 00402524

![enter image description here](http://drops.javaweb.org/uploads/images/9df6ef6f574094a48062500ccf0c3f7c3031807e.jpg)

#### 1.3 函数调用步骤示意

| 过程描述 | 汇编代码 |
| --- | --- |
| 参数入栈  
返回地址入栈  
代码区跳转  
栈帧调整 | push 参数3  
push 参数2  
push 参数1  
call (相当于push+jmp)  
push ebp  
mov ebp esp  
sub esp,xxx |

#### 1.4 函数返回步骤示意

| 过程描述 | 汇编代码 |
| --- | --- |
| 栈回收  
把ESP所指向内容弹出到EBP（相当于保存的上一栈的EBP弹出）  
返回地址弹入EIP并Jump | ADD ESP,XXX  
POP EBP  
RETN （相对于POP+JUMP） |

函数栈帧示意。

![enter image description here](http://drops.javaweb.org/uploads/images/85c00d492014e4b97cd8134fdf92b948169f6539.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/accf81da4e1333344a11c833e6c36b2c62c65f5a.jpg)

### 1.5 栈溢出基础知识

#### 1.5.1 原理示意

栈溢出就是缓冲区溢出的一种。 由于缓冲区溢出而使得有用的存储单元被改写,往往会引发不可预料的后果。程序在运行过程中，为了临时存取数据的需要，一般都要分配一些内存空间，通常称这些空间为缓冲区。如果向缓冲区中写入超过其本身长度的数据，导致缓冲区无法容纳，就会造成缓冲区以外的存储单元被改写，这种现象就称为缓冲区溢出。栈溢出原理示意入下图。

![enter image description here](http://drops.javaweb.org/uploads/images/d8c95dddc0c75a907d34a2d00464302ee7ad0631.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/13082b2e109e78de4045f37c6d10d491ab29e09f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/654e92e762dd50280acc8744db8b4d2a0de446ab.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/2466d5968daa090f9bb34f15358054676f8a557e.jpg)

#### 1.5.2 程序调试

调试带有字符串拷贝的简单程序示意。程序可以用Dev-C++ 4.9.9.2编译，小巧简单。程序代码如下。

```
#include <string.h> 
void do_something(char *Buffer)
{
     char MyVar[128];
     strcpy(MyVar,Buffer);
}
int main (int argc, char **argv)
{
     do_something(argv[1]);
}

```

![enter image description here](http://drops.javaweb.org/uploads/images/ea2854ffb9737b16b52be87400efd7093e601fe3.jpg)

调用函数，CALL function.00401290。

![enter image description here](http://drops.javaweb.org/uploads/images/a6b290d0054af941533516e9e767a2fdea7e4bec.jpg)

函数返回后的下一条执行地址压栈，在栈中可以看到004012EA，函数跳转到00401290。

![enter image description here](http://drops.javaweb.org/uploads/images/e96ab8571844fb9ba67a3f8c632e6575f179750e.jpg)

进入子函数，PUSH EBP，EBP入栈。

![enter image description here](http://drops.javaweb.org/uploads/images/1d8c9739b17f4d077227dcbf9f29a9e2bfb565b4.jpg)

MOV EBP ESP 改变栈底，让EBP指向ESP，EBP的内容（0x0022FF78）指向了前一个栈帧，所以[EBP+4]=004012EA。

![enter image description here](http://drops.javaweb.org/uploads/images/ee275888c271d32c36533bf0883cec9f92eb5585.jpg)

开辟栈存储空间：SUB ESP,0x98

![enter image description here](http://drops.javaweb.org/uploads/images/cfeeb2d7aa82765e6370afab5f161ecd39d870b0.jpg)

根据调试截图可知，如果[Buffer]的大小大于0x98字节，strcpy()函数将会覆盖保存的EBP（saved EBP）和保存的EIP（saved EIP），覆盖过程示意如下。

![enter image description here](http://drops.javaweb.org/uploads/images/4d4be13d751e0b3f0d9fdd27f73be94aceedd62d.jpg)

0x01 漏洞调试
---------

* * *

#### 2.1 漏洞测试环境

| 程序描述 | 备注 |
| --- | --- |
| Easy RM to MP3 Converter 2.7.3.700 | 存在栈溢出漏洞的软件 |
| Windows XP Pro SP3 En MSDN VL（不打任何补丁，关闭DEP） | 模拟受害端 |
| Kali-linux-1.0.9-i386 | 模拟攻击端 |
| Windbg 6.12.0002.633 X86 |  |
| Python 2.7.7 |  |
| Immunity Debugger 1.85 |  |

### 2.2 Easy RM to MP3 Converter栈溢出调试过程

利用Perl和Python可以生成不同的m3u文件、POC进行测试。

![enter image description here](http://drops.javaweb.org/uploads/images/3970d8daaa7270150c69051aa6015fc642a4bbb8.jpg)

打开Easy RM to MP3 Converter，加载具有10000个字符A的crash.m3u无效文件，我们发现目标软件捕获了该错误，跳出友好提示。 程序抛出一个错误，但是看起来这个错误被程序异常处理例程捕捉到了，程序并没崩掉。

![enter image description here](http://drops.javaweb.org/uploads/images/799b546d5065078753b1b3d3223a802c624d39c3.jpg)

调整字符个数，继续运行，目标软件在20000和30000之间可以崩溃掉。很明显，EIP 0x41414141是crash.m3u中的数据，说明程序返回地址被覆盖，EIP跳转到0x41414141，但找不到可执行的指令，所以报错。同时，从图中可以看出程序的EIP也可以被我们填充成一个指向恶意代码的地址。

![enter image description here](http://drops.javaweb.org/uploads/images/9815489179e535424282ba2b50347729a703cd2b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8c509d13d1399273e9ca68a3f8d170e732db70b8.jpg)

如果使用二分法。用25000个A和5000个B填充m3u文件，如果EIP变为41414141 （AAAA）。那么返回地址就位于20000到25000之间。 如果EIP变为42424242 （BBBB）那么返回地址就位于25000到30000之间。

![enter image description here](http://drops.javaweb.org/uploads/images/c3296155af9d4b25ae0000393074bd22ff3e2366.jpg)

使用25000A+5000B，可以看到EIP为42424242（BBBB），所以返回地址位于25000到30000之间了。

![enter image description here](http://drops.javaweb.org/uploads/images/9f5b21062d485446300359d709220bd6f2d6c8e2.jpg)

根据调试信息，返回返回地址为42424242，说明ESP指向的返回地址已经弹出到EIP，则在内存中，栈顶指针ESP会指向EIP的下一个位置，如上图所示。 查看esp中的数据 d esp。

![enter image description here](http://drops.javaweb.org/uploads/images/a84a2a7b33d5a34e048a33700eb9c8dd2f8a3e12.jpg)

寻找存放shellcode的地址空间原理。

根据函数调用的堆栈平衡原理，缓冲区溢出之后，ESP应该停留在函数（这里假设为：XXCopy）调用之前所在位置上。也就是说，覆盖完EIP之后继续填充的数据都将保存在ESP所指地址中。

![enter image description here](http://drops.javaweb.org/uploads/images/d348914215a5fb18fb03a587f6b7cd4ba3932e92.jpg)

我们用BBBB重写了EIP和可以看到ESP所指的缓冲区。在我们调整脚本之前，需要精确的定位出来返回地址在缓冲区的位置，因为如果填充的都是AAAABBBB之类的，区分度不够高。调用metasploit中自带的工具。

```
root@kali:/opt/metasploit/apps/pro/msf3/tools# ./pattern_create.rb 5000

```

![enter image description here](http://drops.javaweb.org/uploads/images/3ed8215fa2126929ed57fcf77df3d5d20004462f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f87be88b975dbefab48e11dc864b5943427789ff.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/aac619376f0dcdc8d5b5f989f4e76bdc5d56a391.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/41376651d07c0d1b56fad61e0f582bf5a5d061e1.jpg)

重写EIP前面需要覆盖的缓冲区长度。创建一个文件，填充25000+1069个A，再加4个B，EIP应该就会被重写成为42424242。

![enter image description here](http://drops.javaweb.org/uploads/images/3f5d52fcee130ddf4c0aaae9ce75a4675a20f001.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8f39d71c0bcf7f6346cca7e0cf080a9a7004345a.jpg)

d esp

![enter image description here](http://drops.javaweb.org/uploads/images/a349d999af16504f649fa033f9be3b111f9f6125.jpg)

26061+4+4 = 26069

| Buffer | EBP | EIP | ESP 指向位置 |
| --- | --- | --- | --- |
| A（x 26061） | AAAA | BBBB | CCCCCCCCCCCCCCCCCCCCC |
| 414141414141414141414141...41 | 41414141 | 4242424242 |  |
| 26061 bytes | 4bytes | 4bytes |  |

![enter image description here](http://drops.javaweb.org/uploads/images/8ec31f39e29fff98b6030c9f002926098ad2c16b.jpg)

当函数返回，BBBB被置入EIP中（pop ebp，retn）,所以流程尝试到地址0x42424242（BBBB）执行。找内存空间存放我们的shellcode。

为了让应用程序崩溃，我们已经向内存中写入了26069 个A，我们已经向保存的EIP存储空间写入了一个新的值（函数返回执行时，RET将弹出并跳转到这个值），我们已经写了一堆的字符C。当应用程序崩溃时，可以查看所有这些寄存器（D ESP，D EAX，D EBX，D EBP，...）。如果你能在这些寄存器中的一个，看到缓冲区里的值（无论是A，还是C），那么你或许可以用shellcode取代它们的值，并跳转到该位置。在我们的例子中，我们可以看到，ESP似乎指向我们的C，所以理想情况下，我们会用实际的shellcode取代C，告诉EIP跳转到ESP的地址。

![enter image description here](http://drops.javaweb.org/uploads/images/270f1434312121c9eb293131d4668b312d2ea403.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/e9708e408dd6ce4fdfe33684b95f9a61c5feef02.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/e3b03a9e65f65f7508713dd0887e0c373d435d78.jpg)

直接跳到一个内存地址不是一个好的方法（000ff730包含了字符串终止符（NULL： 00） ...所以你看到来自缓冲区第一部分的字母A...我们无法到达重写EIP后我们的数据了....另一方面，在Exploit使用内存地址直接跳转是非常不可靠的...因为内存地址会因为系统版本，语言等的不同而不同）

![enter image description here](http://drops.javaweb.org/uploads/images/e637e63d76d2a4b160fb8758e72cff4d3520f504.jpg)

windbg中输入a，然后再输入jmp esp ，报错，直接回车，返回命令输入界面。然后u jmp esp之前的地址。

![enter image description here](http://drops.javaweb.org/uploads/images/7cc1b9761d53d2315dfcd7a14cbdea837d36ba2e.jpg)

在地址7c90120e，你可以看到ffe4。这是操作码JMP ESP

现在，我们需要在这些加载的DLL中的某一个，找到这个操作码（opcode）。

查看WinDbg窗口，可以容易找到属于Easy RM to MP3应用程序的DLL。

![enter image description here](http://drops.javaweb.org/uploads/images/40887e592f47699a9557f652bb41ed976a485ac9.jpg)

如果我们能够在这些DLL中找到一个操作码，那么我们就可以在Windows平台上制作可靠的漏洞利用程序。

如果我们使用属于操作系统的DLL，那么我们可能会发现，漏洞利用程序在其他版本的操作系统上无法正常工作。

因此，我们在`C:\Program Files\Easy RM to MP3 Converter\MSRMCcodec02.dll`中搜索操作码。

此DLL在地址01c20000和020ed000之间加载。搜索操作码FF E4。

```
s 01c20000 020ed000 ff e4

```

![enter image description here](http://drops.javaweb.org/uploads/images/2feb22c697639054e17ecf1fafca7e8ee1d25f6a.jpg)

当选择一个地址时，寻找空字节是很重要的。

你应该尽量避免使用地址中含有空字节。空字节将成为一个字符串结束符，那么缓冲区数据其余的部分将变得不可用。

```
s 70000000 l fffffff ff e4

```

![enter image description here](http://drops.javaweb.org/uploads/images/1d28e08afe2743c08a02fb874f681aa97ce800d5.jpg)

因为我们希望把我们的shellcode放入ESP中（在覆盖的EIP之后放置载荷payload），从列表中选出的JMP ESP地址空间中不能有NULL字节。

空字节作为一个字符串结束，因此所有在它后面的内容会被忽略。

我们在覆盖的EIP之后放置我们的shellcode，这个地址不能包含空字节。

第一个地址起作用的地址是0x01ddf23a。

输入命令可以验证这个地址是否含有jmp esp（在地址01ccf23a处反汇编指令）

```
u 01ddf23a

```

![enter image description here](http://drops.javaweb.org/uploads/images/d8883174f7f74a124b69b801bc6f3281c3f49041.jpg)

0x02 漏洞利用
---------

* * *

3.1 弹计算器

如果我们用0x01ccf23a 覆盖EIP，那么 jmp esp将会被执行。esp 包含了shellcode，所以我们就有了一个可用的exploit。首先我们可以用带有“NOP & break”的shellcode测试下。用Windbg调试，软件打开m3u文件。

![enter image description here](http://drops.javaweb.org/uploads/images/e155ed6f30d86ee02d9b1d5168c1616ac77213ab.jpg)

再次运行程序，用windbg附加，运行，打开新的m3u文件。程序将会在地址000ff745暂停。那么说明jmp esp起作用了。esp开始于 000ff730, 它含有NOPs 指令直到 000ff744。

现在添加真实的shellcode，并开发exploit。再次打开，弹出计算器。

![enter image description here](http://drops.javaweb.org/uploads/images/bada957e53cc462085b8cf596804c5f6c97e20da.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8c25717cd6d33264f66ba7b6be4107918171852a.jpg)

#### 3.2 绑定端口

利用msfpaload生成shellcode，绑定某端口，例如8888。

![enter image description here](http://drops.javaweb.org/uploads/images/f8468f8625d6fbf5e04ce6a18c460660005f56e9.jpg)

Shellcode执行成功后，如果没有设置过防火墙，windows防火墙弹出拦截提示，unblock允许。

![enter image description here](http://drops.javaweb.org/uploads/images/2b95adb37e01d30d8a05c655ef34637795ffa1d1.jpg)

netstat –ano 查看网络连接情况，可以看到，打开了8888端口，查看进程号PID为388，程序为EasyRMtoMP3Converter.exe。

![enter image description here](http://drops.javaweb.org/uploads/images/d9b9f6fa53c12d06bc2218fe6e38eae58e610cc0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f9027e4ba5aa401b144947674be0018603f08182.jpg)

在Windows防火墙打开的情况下，ping不通，如果防火墙允许8888端口通信，telnet可以连接。

![enter image description here](http://drops.javaweb.org/uploads/images/719bc9140614f761e60a560f04287af553df8f50.jpg)

查看网络状态，与windows机器上显示一致。

![enter image description here](http://drops.javaweb.org/uploads/images/7fe164318af2e3dc74049c60599e3c8898a7435e.jpg)

0x03 问题说明
---------

* * *

| 描述 | 备注 |
| --- | --- |
| Metasploit每次生成不同的shellcode的不同输出。所以，如果你看自己的机器上每次看到不同的shellcode，则不必惊慌。 | 需要去掉坏字符 \x00\x0a\x0d\x1a |
| 使用相同的命令，不同的系统，默认的编码器可能不同 | `msfpayload windows/shell_bind_tcp LPORT=8888 R | msfencode -b '\x00\x0a\x0d\x1a' -t perl` |
| Kali系统中metasploit默认所使用的编码器与BackTrack不一致。 | 参考文献上使用的是Backtrack系统，其metasploit使用的默认编码器是x86/shikata_ga_nai，而Kali在不指定参数的情况下，使用的默认编码器是cmd/powershell_base64 |
| Backtrack默认编码器x86/shikata_ga_nai  
Backtrack系统metasploit所生成的shellcode  
size 368 |  |
| ![null](http://static.wooyun.org/drops/20141013/image116.png) |  |
| Kali默认编码器cmd/powershell_base64  
Kali系统metasploit所生成的shellcode  
size 985 | ![null](http://static.wooyun.org/drops/20141013/image118.png) |
| 使用Kali默认编码器生成的shellcode，程序执行后崩溃。 | ![null](http://static.wooyun.org/drops/20141013/image120.png) |
| 为了生成可绑定端口的的shellcode，在Kali系统中需要指定编码器  
msfencode -e x86/shikata_ga_nai | ![null](http://static.wooyun.org/drops/20141013/image122.png) |

参考文献 1) https://www.google.com 2) https://www.corelan.be/index.php/2009/07/19/exploit-writing-tutorial-part-1-stack-based-overflows/ 3) https://www.corelan.be/index.php/forum/exploit-writing-debuggers/error-when-executed-u-unassemble-followed-by-the-address-that-was-shown-before-entering-jmp-esp/ 4) http://blog.csdn.net/yuzl32/article/details/6126592 5) http://extreme-security.blogspot.com/2013/02/stack-overflows-part-2-executing.html 6) http://cstriker1407.info/blog/a-reading-notes-of-the-devils-training-camp-msfpayload-using-the-tool-and-free-to-kill/ 7) http://www.securitysift.com/windows-exploit-development-part-1-basics/ 8) 《逆向工程核心原理》