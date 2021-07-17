# 学习/认识CPU的GDT

0x00 关于GDT
==========

* * *

CPU相信大家都知道是啥玩意，哪三个单词缩写。GDT对于一些不搞底层的人知道的可能还有一些。

GDT就是`global descriptor table`的缩写。相应的还有个`local descriptor tables`(LDT)，这个不再此文的讨论范围内。

这在保护模式教程中经常看到，但是这和咱们程序员有啥关系呢？**1.留后门**

就是进入R0后设置（R3）进入R0的后门（如：调用门，中断门，任务门等）。

**2.了解/编写操作系统**

人家微软的Windows操作系统经历了很多变化，如今到了WIN10。（对于天天研究Windows的人）这对咱有意思吗？顶多认识了解和应用/利用。 好像有不少的变化（PC端）都是基于硬件的。基于软件的算法不说。

**3.虚拟化**

如：intel-VT就要设置许多段（如：cs,ss,ds,es,fs,gs等）的Base，Limit，access rights，Selectors等。

好了，废话不多进入正题。

0x01 开始分析
=========

* * *

以Windows系统为例进行分析。

```
kd> vertarget 
Windows XP Kernel Version 2600 (Service Pack 3) MP (1 procs) Free x86 compatible
Built by: 2600.xpsp_sp3_qfe.130704-0421
Machine Name:
Kernel base = 0x804d8000 PsLoadedModuleList = 0x8055e720
Debug session time: Thu Aug  6 14:25:16.468 2015 (UTC + 8:00)
System Uptime: 0 days 0:01:19.984

```

这是操作系统的环境信息。

GDT是由GDTR指向的。

```
kd> r gdtr
gdtr=8003f000

```

其大小为：

```
kd> r gdtl
gdtl=000003ff

```

其全部的内容为：

```
kd> db 8003f000 L(000003ff + 1)
8003f000  00 00 00 00 00 00 00 00-ff ff 00 00 00 9b cf 00  ................
8003f010  ff ff 00 00 00 93 cf 00-ff ff 00 00 00 fb cf 00  ................
8003f020  ff ff 00 00 00 f3 cf 00-ab 20 00 20 04 8b 00 80  ......... . ....
8003f030  01 00 00 f0 df 93 c0 ff-ff 0f 00 00 00 f3 40 00  ..............@.
8003f040  ff ff 00 04 00 f2 00 00-00 00 00 00 00 00 00 00  ................
8003f050  68 00 00 27 55 89 00 80-68 00 68 27 55 89 00 80  h..'U...h.h'U...
8003f060  ff ff 40 2f 02 93 00 00-ff 3f 00 80 0b 92 00 00  ..@/.....?......
8003f070  ff 03 00 70 ff 92 00 ff-ff ff 00 00 40 9a 00 80  ...p........@...
8003f080  ff ff 00 00 40 92 00 80-00 00 00 00 00 92 00 00  ....@...........
8003f090  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
8003f0a0  68 00 b8 16 38 89 00 82-00 00 00 00 00 00 00 00  h...8...........
8003f0b0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
8003f0c0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
8003f0d0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
8003f0e0  ff ff 00 f0 50 9f 00 f8-ff ff 00 00 00 92 00 00  ....P...........
8003f0f0  b7 03 40 d0 4f 98 00 80-ff ff 00 00 00 92 00 00  ..@.O...........
8003f100  ff ff 00 24 4d 93 40 ba-ff ff 00 24 4d 93 40 ba  ...$M.@....$M.@.
8003f110  ff ff 00 24 4d 93 40 ba-20 f1 03 80 00 00 00 00  ...$M.@. .......
8003f120  28 f1 03 80 00 00 00 00-30 f1 03 80 00 00 00 00  (.......0.......
8003f130  38 f1 03 80 00 00 00 00-40 f1 03 80 00 00 00 00  8.......@.......
8003f140  48 f1 03 80 00 00 00 00-50 f1 03 80 00 00 00 00  H.......P.......
8003f150  58 f1 03 80 00 00 00 00-60 f1 03 80 00 00 00 00  X.......`.......
8003f160  68 f1 03 80 00 00 00 00-70 f1 03 80 00 00 00 00  h.......p.......
8003f170  78 f1 03 80 00 00 00 00-80 f1 03 80 00 00 00 00  x...............
8003f180  88 f1 03 80 00 00 00 00-90 f1 03 80 00 00 00 00  ................
8003f190  98 f1 03 80 00 00 00 00-a0 f1 03 80 00 00 00 00  ................
8003f1a0  a8 f1 03 80 00 00 00 00-b0 f1 03 80 00 00 00 00  ................
8003f1b0  b8 f1 03 80 00 00 00 00-c0 f1 03 80 00 00 00 00  ................
8003f1c0  c8 f1 03 80 00 00 00 00-d0 f1 03 80 00 00 00 00  ................
8003f1d0  d8 f1 03 80 00 00 00 00-e0 f1 03 80 00 00 00 00  ................
8003f1e0  e8 f1 03 80 00 00 00 00-f0 f1 03 80 00 00 00 00  ................
8003f1f0  f8 f1 03 80 00 00 00 00-00 f2 03 80 00 00 00 00  ................
8003f200  08 f2 03 80 00 00 00 00-10 f2 03 80 00 00 00 00  ................
8003f210  18 f2 03 80 00 00 00 00-20 f2 03 80 00 00 00 00  ........ .......
8003f220  28 f2 03 80 00 00 00 00-30 f2 03 80 00 00 00 00  (.......0.......
8003f230  38 f2 03 80 00 00 00 00-40 f2 03 80 00 00 00 00  8.......@.......
8003f240  48 f2 03 80 00 00 00 00-50 f2 03 80 00 00 00 00  H.......P.......
8003f250  58 f2 03 80 00 00 00 00-60 f2 03 80 00 00 00 00  X.......`.......
8003f260  68 f2 03 80 00 00 00 00-70 f2 03 80 00 00 00 00  h.......p.......
8003f270  78 f2 03 80 00 00 00 00-80 f2 03 80 00 00 00 00  x...............
8003f280  88 f2 03 80 00 00 00 00-90 f2 03 80 00 00 00 00  ................
8003f290  98 f2 03 80 00 00 00 00-a0 f2 03 80 00 00 00 00  ................
8003f2a0  a8 f2 03 80 00 00 00 00-b0 f2 03 80 00 00 00 00  ................
8003f2b0  b8 f2 03 80 00 00 00 00-c0 f2 03 80 00 00 00 00  ................
8003f2c0  c8 f2 03 80 00 00 00 00-d0 f2 03 80 00 00 00 00  ................
8003f2d0  d8 f2 03 80 00 00 00 00-e0 f2 03 80 00 00 00 00  ................
8003f2e0  e8 f2 03 80 00 00 00 00-f0 f2 03 80 00 00 00 00  ................
8003f2f0  f8 f2 03 80 00 00 00 00-00 f3 03 80 00 00 00 00  ................
8003f300  08 f3 03 80 00 00 00 00-10 f3 03 80 00 00 00 00  ................
8003f310  18 f3 03 80 00 00 00 00-20 f3 03 80 00 00 00 00  ........ .......
8003f320  28 f3 03 80 00 00 00 00-30 f3 03 80 00 00 00 00  (.......0.......
8003f330  38 f3 03 80 00 00 00 00-40 f3 03 80 00 00 00 00  8.......@.......
8003f340  48 f3 03 80 00 00 00 00-50 f3 03 80 00 00 00 00  H.......P.......
8003f350  58 f3 03 80 00 00 00 00-60 f3 03 80 00 00 00 00  X.......`.......
8003f360  68 f3 03 80 00 00 00 00-70 f3 03 80 00 00 00 00  h.......p.......
8003f370  78 f3 03 80 00 00 00 00-80 f3 03 80 00 00 00 00  x...............
8003f380  88 f3 03 80 00 00 00 00-90 f3 03 80 00 00 00 00  ................
8003f390  98 f3 03 80 00 00 00 00-a0 f3 03 80 00 00 00 00  ................
8003f3a0  a8 f3 03 80 00 00 00 00-b0 f3 03 80 00 00 00 00  ................
8003f3b0  b8 f3 03 80 00 00 00 00-c0 f3 03 80 00 00 00 00  ................
8003f3c0  c8 f3 03 80 00 00 00 00-d0 f3 03 80 00 00 00 00  ................
8003f3d0  d8 f3 03 80 00 00 00 00-e0 f3 03 80 00 00 00 00  ................
8003f3e0  e8 f3 03 80 00 00 00 00-f0 f3 03 80 00 00 00 00  ................
8003f3f0  f8 f3 03 80 00 00 00 00-00 00 00 00 00 00 00 00  ................

```

注意：是8字节对齐并是8的整数倍。

不过这些数据不好看，要解析，这就是我们的任务。

其实也可以这样看：

```
kd> dg 0 3ff
                                  P Si Gr Pr Lo
Sel    Base     Limit     Type    l ze an es ng Flags
---- -------- -------- ---------- - -- -- -- -- --------
0000 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
0008 00000000 ffffffff Code RE Ac 0 Bg Pg P  Nl 00000c9b
0010 00000000 ffffffff Data RW Ac 0 Bg Pg P  Nl 00000c93
0018 00000000 ffffffff Code RE Ac 3 Bg Pg P  Nl 00000cfb
0020 00000000 ffffffff Data RW Ac 3 Bg Pg P  Nl 00000cf3
0028 80042000 000020ab TSS32 Busy 0 Nb By P  Nl 0000008b
0030 ffdff000 00001fff Data RW Ac 0 Bg Pg P  Nl 00000c93
0038 00000000 00000fff Data RW Ac 3 Bg By P  Nl 000004f3
0040 00000400 0000ffff Data RW    3 Nb By P  Nl 000000f2
0048 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
0050 80552700 00000068 TSS32 Avl  0 Nb By P  Nl 00000089
0058 80552768 00000068 TSS32 Avl  0 Nb By P  Nl 00000089
0060 00022f40 0000ffff Data RW Ac 0 Nb By P  Nl 00000093
0068 000b8000 00003fff Data RW    0 Nb By P  Nl 00000092
0070 ffff7000 000003ff Data RW    0 Nb By P  Nl 00000092
0078 80400000 0000ffff Code RE    0 Nb By P  Nl 0000009a
0080 80400000 0000ffff Data RW    0 Nb By P  Nl 00000092
0088 00000000 00000000 Data RW    0 Nb By P  Nl 00000092
0090 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
0098 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00A0 823816b8 00000068 TSS32 Avl  0 Nb By P  Nl 00000089
00A8 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00B0 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00B8 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00C0 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00C8 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00D0 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00D8 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000
00E0 f850f000 0000ffff Code RE Ac 0 Nb By P  Nl 0000009f
00E8 00000000 0000ffff Data RW    0 Nb By P  Nl 00000092
00F0 804fd040 000003b7 Code EO    0 Nb By P  Nl 00000098
00F8 00000000 0000ffff Data RW    0 Nb By P  Nl 00000092
0100 ba4d2400 0000ffff Data RW Ac 0 Bg By P  Nl 00000493
0108 ba4d2400 0000ffff Data RW Ac 0 Bg By P  Nl 00000493
0110 ba4d2400 0000ffff Data RW Ac 0 Bg By P  Nl 00000493
0118 00008003 0000f120 <Reserved> 0 Nb By Np Nl 00000000
0120 00008003 0000f128 <Reserved> 0 Nb By Np Nl 00000000
0128 00008003 0000f130 <Reserved> 0 Nb By Np Nl 00000000
0130 00008003 0000f138 <Reserved> 0 Nb By Np Nl 00000000
0138 00008003 0000f140 <Reserved> 0 Nb By Np Nl 00000000
0140 00008003 0000f148 <Reserved> 0 Nb By Np Nl 00000000
0148 00008003 0000f150 <Reserved> 0 Nb By Np Nl 00000000
0150 00008003 0000f158 <Reserved> 0 Nb By Np Nl 00000000
0158 00008003 0000f160 <Reserved> 0 Nb By Np Nl 00000000
0160 00008003 0000f168 <Reserved> 0 Nb By Np Nl 00000000
0168 00008003 0000f170 <Reserved> 0 Nb By Np Nl 00000000
0170 00008003 0000f178 <Reserved> 0 Nb By Np Nl 00000000
0178 00008003 0000f180 <Reserved> 0 Nb By Np Nl 00000000
0180 00008003 0000f188 <Reserved> 0 Nb By Np Nl 00000000
0188 00008003 0000f190 <Reserved> 0 Nb By Np Nl 00000000
0190 00008003 0000f198 <Reserved> 0 Nb By Np Nl 00000000
0198 00008003 0000f1a0 <Reserved> 0 Nb By Np Nl 00000000
01A0 00008003 0000f1a8 <Reserved> 0 Nb By Np Nl 00000000
01A8 00008003 0000f1b0 <Reserved> 0 Nb By Np Nl 00000000
01B0 00008003 0000f1b8 <Reserved> 0 Nb By Np Nl 00000000
01B8 00008003 0000f1c0 <Reserved> 0 Nb By Np Nl 00000000
01C0 00008003 0000f1c8 <Reserved> 0 Nb By Np Nl 00000000
01C8 00008003 0000f1d0 <Reserved> 0 Nb By Np Nl 00000000
01D0 00008003 0000f1d8 <Reserved> 0 Nb By Np Nl 00000000
01D8 00008003 0000f1e0 <Reserved> 0 Nb By Np Nl 00000000
01E0 00008003 0000f1e8 <Reserved> 0 Nb By Np Nl 00000000
01E8 00008003 0000f1f0 <Reserved> 0 Nb By Np Nl 00000000
01F0 00008003 0000f1f8 <Reserved> 0 Nb By Np Nl 00000000
01F8 00008003 0000f200 <Reserved> 0 Nb By Np Nl 00000000
0200 00008003 0000f208 <Reserved> 0 Nb By Np Nl 00000000
0208 00008003 0000f210 <Reserved> 0 Nb By Np Nl 00000000
0210 00008003 0000f218 <Reserved> 0 Nb By Np Nl 00000000
0218 00008003 0000f220 <Reserved> 0 Nb By Np Nl 00000000
0220 00008003 0000f228 <Reserved> 0 Nb By Np Nl 00000000
0228 00008003 0000f230 <Reserved> 0 Nb By Np Nl 00000000
0230 00008003 0000f238 <Reserved> 0 Nb By Np Nl 00000000
0238 00008003 0000f240 <Reserved> 0 Nb By Np Nl 00000000
0240 00008003 0000f248 <Reserved> 0 Nb By Np Nl 00000000
0248 00008003 0000f250 <Reserved> 0 Nb By Np Nl 00000000
0250 00008003 0000f258 <Reserved> 0 Nb By Np Nl 00000000
0258 00008003 0000f260 <Reserved> 0 Nb By Np Nl 00000000
0260 00008003 0000f268 <Reserved> 0 Nb By Np Nl 00000000
0268 00008003 0000f270 <Reserved> 0 Nb By Np Nl 00000000
0270 00008003 0000f278 <Reserved> 0 Nb By Np Nl 00000000
0278 00008003 0000f280 <Reserved> 0 Nb By Np Nl 00000000
0280 00008003 0000f288 <Reserved> 0 Nb By Np Nl 00000000
0288 00008003 0000f290 <Reserved> 0 Nb By Np Nl 00000000
0290 00008003 0000f298 <Reserved> 0 Nb By Np Nl 00000000
0298 00008003 0000f2a0 <Reserved> 0 Nb By Np Nl 00000000
02A0 00008003 0000f2a8 <Reserved> 0 Nb By Np Nl 00000000
02A8 00008003 0000f2b0 <Reserved> 0 Nb By Np Nl 00000000
02B0 00008003 0000f2b8 <Reserved> 0 Nb By Np Nl 00000000
02B8 00008003 0000f2c0 <Reserved> 0 Nb By Np Nl 00000000
02C0 00008003 0000f2c8 <Reserved> 0 Nb By Np Nl 00000000
02C8 00008003 0000f2d0 <Reserved> 0 Nb By Np Nl 00000000
02D0 00008003 0000f2d8 <Reserved> 0 Nb By Np Nl 00000000
02D8 00008003 0000f2e0 <Reserved> 0 Nb By Np Nl 00000000
02E0 00008003 0000f2e8 <Reserved> 0 Nb By Np Nl 00000000
02E8 00008003 0000f2f0 <Reserved> 0 Nb By Np Nl 00000000
02F0 00008003 0000f2f8 <Reserved> 0 Nb By Np Nl 00000000
02F8 00008003 0000f300 <Reserved> 0 Nb By Np Nl 00000000
0300 00008003 0000f308 <Reserved> 0 Nb By Np Nl 00000000
0308 00008003 0000f310 <Reserved> 0 Nb By Np Nl 00000000
0310 00008003 0000f318 <Reserved> 0 Nb By Np Nl 00000000
0318 00008003 0000f320 <Reserved> 0 Nb By Np Nl 00000000
0320 00008003 0000f328 <Reserved> 0 Nb By Np Nl 00000000
0328 00008003 0000f330 <Reserved> 0 Nb By Np Nl 00000000
0330 00008003 0000f338 <Reserved> 0 Nb By Np Nl 00000000
0338 00008003 0000f340 <Reserved> 0 Nb By Np Nl 00000000
0340 00008003 0000f348 <Reserved> 0 Nb By Np Nl 00000000
0348 00008003 0000f350 <Reserved> 0 Nb By Np Nl 00000000
0350 00008003 0000f358 <Reserved> 0 Nb By Np Nl 00000000
0358 00008003 0000f360 <Reserved> 0 Nb By Np Nl 00000000
0360 00008003 0000f368 <Reserved> 0 Nb By Np Nl 00000000
0368 00008003 0000f370 <Reserved> 0 Nb By Np Nl 00000000
0370 00008003 0000f378 <Reserved> 0 Nb By Np Nl 00000000
0378 00008003 0000f380 <Reserved> 0 Nb By Np Nl 00000000
0380 00008003 0000f388 <Reserved> 0 Nb By Np Nl 00000000
0388 00008003 0000f390 <Reserved> 0 Nb By Np Nl 00000000
0390 00008003 0000f398 <Reserved> 0 Nb By Np Nl 00000000
0398 00008003 0000f3a0 <Reserved> 0 Nb By Np Nl 00000000
03A0 00008003 0000f3a8 <Reserved> 0 Nb By Np Nl 00000000
03A8 00008003 0000f3b0 <Reserved> 0 Nb By Np Nl 00000000
03B0 00008003 0000f3b8 <Reserved> 0 Nb By Np Nl 00000000
03B8 00008003 0000f3c0 <Reserved> 0 Nb By Np Nl 00000000
03C0 00008003 0000f3c8 <Reserved> 0 Nb By Np Nl 00000000
03C8 00008003 0000f3d0 <Reserved> 0 Nb By Np Nl 00000000
03D0 00008003 0000f3d8 <Reserved> 0 Nb By Np Nl 00000000
03D8 00008003 0000f3e0 <Reserved> 0 Nb By Np Nl 00000000
03E0 00008003 0000f3e8 <Reserved> 0 Nb By Np Nl 00000000
03E8 00008003 0000f3f0 <Reserved> 0 Nb By Np Nl 00000000
03F0 00008003 0000f3f8 <Reserved> 0 Nb By Np Nl 00000000
03F8 00000000 00000000 <Reserved> 0 Nb By Np Nl 00000000

```

我们的功能就是要解析出这样的格式。

注意，另外一个话题是：也可以手动分析出这个格式，如：

```
kd> r cs 
cs=00000008

```

然后根据一定的算法得出的结论要如下（一种思路是根据_KGDTENTRY的定义）：

```
kd> dg cs 
                                  P Si Gr Pr Lo
Sel    Base     Limit     Type    l ze an es ng Flags
---- -------- -------- ---------- - -- -- -- -- --------
0008 00000000 ffffffff Code RE Ac 0 Bg Pg P  Nl 00000c9b

```

这个算法就不说了，相信你会的。

0x02 总结
=======

简单说下吧！

GDT就是一个（数组格式的）表，里面的每一项是一个`Segment Descriptors`。

关于这个的格式，可见：`Intel? 64 and IA-32 Architectures Software Developer’s Manual（Order Number: 325462-055US June 2015）`的`Volume 3: System Programming Guide`的`3.4.5 Segment Descriptors`小节及附图。

这个Segment Descriptors具体的分两大类：

一类是：`application (code or data) descriptor`。`这就是常见的代码/数据段，如：大多数的CS，DS都指向这里`。 一类是：`system descriptor`

这里又分为：`system-segment descriptors（LDT and TSS segments）`。`gate descriptors（call, interrupt, and trap gates）`。

但是，这些结构在Windows下的定义是啥样呢？

经查WRK和WINDBG，结果如下：

```
// Special Registers for i386
typedef struct _X86_DESCRIPTOR {
    USHORT  Pad;
    USHORT  Limit;
    ULONG   Base;
} X86_DESCRIPTOR, *PX86_DESCRIPTOR;

// GDT Entry
typedef struct _KGDTENTRY {
    USHORT  LimitLow;
    USHORT  BaseLow;
    union {
        struct {
            UCHAR   BaseMid;
            UCHAR   Flags1;     // Declare as bytes to avoid alignment
            UCHAR   Flags2;     // Problems.
            UCHAR   BaseHi;
        } Bytes;
        struct {
            ULONG   BaseMid : 8;
            ULONG   Type : 5;//把S位包含进去了，也就是是否为系统段描述符的位。
            ULONG   Dpl : 2;
            ULONG   Pres : 1;
            ULONG   LimitHi : 4;
            ULONG   Sys : 1;//即AVL，系统软件自定义的。
            ULONG   Reserved_0 : 1;//LongMode
            ULONG   Default_Big : 1;//即INTEL的D/B (default operation size/default stack pointer size and/or upper bound) flag。
            ULONG   Granularity : 1;
            ULONG   BaseHi : 8;
        } Bits;
    } HighWord;
} KGDTENTRY, *PKGDTENTRY;

```

为啥定义的名字是KGDTENTRY呢？其实你想想结构的位置。 这个其实就是`Segment Descriptors`，但是定义的和INTEL的不完全一样。

```
kd> dt nt!_KGDTENTRY 
   +0x000 LimitLow         : Uint2B
   +0x002 BaseLow          : Uint2B
   +0x004 HighWord         : __unnamed
kd> dt nt!_KGDTENTRY -b
   +0x000 LimitLow         : Uint2B
   +0x002 BaseLow          : Uint2B
   +0x004 HighWord         : __unnamed
      +0x000 Bytes            : __unnamed
         +0x000 BaseMid          : UChar
         +0x001 Flags1           : UChar
         +0x002 Flags2           : UChar
         +0x003 BaseHi           : UChar
      +0x000 Bits             : __unnamed
         +0x000 BaseMid          : Pos 0, 8 Bits
         +0x000 Type             : Pos 8, 5 Bits
         +0x000 Dpl              : Pos 13, 2 Bits
         +0x000 Pres             : Pos 15, 1 Bit
         +0x000 LimitHi          : Pos 16, 4 Bits
         +0x000 Sys              : Pos 20, 1 Bit
         +0x000 Reserved_0       : Pos 21, 1 Bit
         +0x000 Default_Big      : Pos 22, 1 Bit
         +0x000 Granularity      : Pos 23, 1 Bit
         +0x000 BaseHi           : Pos 24, 8 Bits

```

具体的算法请参见： 1.INTEL的资料。 2.WRK的算法。 3.本文的代码。

上面分析的是32位下的Windows系统，再看看64位下Windows的GDT。

```
0: kd> vertarget 
Windows 7 Kernel Version 7601 (Service Pack 1) MP (2 procs) Free x64
Built by: 7601.18869.amd64fre.win7sp1_gdr.150525-0603
Machine Name:
Kernel base = 0xfffff800`01e64000 PsLoadedModuleList = 0xfffff800`020ab730
Debug session time: Thu Aug  6 14:37:33.359 2015 (UTC + 8:00)
System Uptime: 0 days 0:13:15.757
0: kd> r gdtr
gdtr=fffff80001d51000
0: kd> r gdtl
gdtl=007f
0: kd> db fffff80001d51000 L(007f + 1)
fffff800`01d51000  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
fffff800`01d51010  00 00 00 00 00 9b 20 00-ff ff 00 00 00 93 cf 00  ...... .........
fffff800`01d51020  ff ff 00 00 00 fb cf 00-ff ff 00 00 00 f3 cf 00  ................
fffff800`01d51030  00 00 00 00 00 fb 20 00-00 00 00 00 00 00 00 00  ...... .........
fffff800`01d51040  67 00 80 20 d5 8b 00 01-00 f8 ff ff 00 00 00 00  g.. ............
fffff800`01d51050  00 3c 00 a0 f9 f3 40 ff-00 00 00 00 00 00 00 00  .<....@.........
fffff800`01d51060  ff ff 00 00 00 9a cf 00-00 00 00 00 00 00 00 00  ................
fffff800`01d51070  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
0: kd> dg 0 80
                                                    P Si Gr Pr Lo
Sel        Base              Limit          Type    l ze an es ng Flags
---- ----------------- ----------------- ---------- - -- -- -- -- --------
0000 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0008 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0010 00000000`00000000 00000000`00000000 Code RE Ac 0 Nb By P  Lo 0000029b
0018 00000000`00000000 00000000`ffffffff Data RW Ac 0 Bg Pg P  Nl 00000c93
0020 00000000`00000000 00000000`ffffffff Code RE Ac 3 Bg Pg P  Nl 00000cfb
0028 00000000`00000000 00000000`ffffffff Data RW Ac 3 Bg Pg P  Nl 00000cf3
0030 00000000`00000000 00000000`00000000 Code RE Ac 3 Nb By P  Lo 000002fb
0038 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0040 00000000`01d52080 00000000`00000067 TSS32 Busy 0 Nb By P  Nl 0000008b
0048 00000000`0000ffff 00000000`0000f800 <Reserved> 0 Nb By Np Nl 00000000
0050 ffffffff`fff9a000 00000000`00003c00 Data RW Ac 3 Bg By P  Nl 000004f3
0058 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0060 00000000`00000000 00000000`ffffffff Code RE    0 Bg Pg P  Nl 00000c9a
0068 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0070 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0078 00000000`00000000 00000000`00000000 <Reserved> 0 Nb By Np Nl 00000000
0080 Unable to get descriptor

```

WRK及WINDBG的相关（验证）信息如下：

```
// Special Registers for AMD64.
typedef struct _AMD64_DESCRIPTOR {
    USHORT  Pad[3];
    USHORT  Limit;
    ULONG64 Base;
} AMD64_DESCRIPTOR, *PAMD64_DESCRIPTOR;

typedef union _KGDTENTRY64 {
    struct {
        USHORT  LimitLow;
        USHORT  BaseLow;
        union {
            struct {
                UCHAR   BaseMiddle;
                UCHAR   Flags1;
                UCHAR   Flags2;
                UCHAR   BaseHigh;
            } Bytes;

            struct {
                ULONG   BaseMiddle : 8;
                ULONG   Type : 5;//把S位包含进去了，也就是是否为系统段描述符的位。
                ULONG   Dpl : 2;
                ULONG   Present : 1;
                ULONG   LimitHigh : 4;
                ULONG   System : 1;//即AVL，系统软件自定义的。
                ULONG   LongMode : 1;
                ULONG   DefaultBig : 1;//即INTEL的D/B (default operation size/default stack pointer size and/or upper bound) flag。
                ULONG   Granularity : 1;
                ULONG   BaseHigh : 8;
            } Bits;
        };

        //ULONG BaseUpper;
        //ULONG MustBeZero;
    };

    //ULONG64 Alignment;
} KGDTENTRY64, *PKGDTENTRY64;

0: kd> dt _KGDTENTRY64
hal!_KGDTENTRY64
   +0x000 LimitLow         : Uint2B
   +0x002 BaseLow          : Uint2B
   +0x004 Bytes            : <unnamed-tag>
   +0x004 Bits             : <unnamed-tag>
   +0x008 BaseUpper        : Uint4B
   +0x00c MustBeZero       : Uint4B
   +0x000 Alignment        : Uint8B
0: kd> dt _KGDTENTRY64 -b
hal!_KGDTENTRY64
   +0x000 LimitLow         : Uint2B
   +0x002 BaseLow          : Uint2B
   +0x004 Bytes            : <unnamed-tag>
      +0x000 BaseMiddle       : UChar
      +0x001 Flags1           : UChar
      +0x002 Flags2           : UChar
      +0x003 BaseHigh         : UChar
   +0x004 Bits             : <unnamed-tag>
      +0x000 BaseMiddle       : Pos 0, 8 Bits
      +0x000 Type             : Pos 8, 5 Bits
      +0x000 Dpl              : Pos 13, 2 Bits
      +0x000 Present          : Pos 15, 1 Bit
      +0x000 LimitHigh        : Pos 16, 4 Bits
      +0x000 System           : Pos 20, 1 Bit
      +0x000 LongMode         : Pos 21, 1 Bit
      +0x000 DefaultBig       : Pos 22, 1 Bit
      +0x000 Granularity      : Pos 23, 1 Bit
      +0x000 BaseHigh         : Pos 24, 8 Bits
   +0x008 BaseUpper        : Uint4B
   +0x00c MustBeZero       : Uint4B
   +0x000 Alignment        : Uint8B

```

**注意：**1.以上只分析一个CPU的情况，如果一个计算机有多个CPU要分别处理。

2.为了和WINDBG的DG命令处理/显示的相似，特意根据INTEL的Table 3-1. Code- and Data-Segment Types，制作一个字符串数组。还有待改善。

3.GetGdtLimit的这个功能没有相应的C代码，只有汇编代码（.asm文件），包括（X86和X64）。这个代码就不附带了，相信你能做到的。

最后只有代码了，请看代码：

```
/*
功能：显示每个CPU的GDT信息。
注释：一下结构摘自WRK。

made by correy.
QQ:112426112.
homepage:http://correy.webs.com 注释：需翻墙，有的翻墙软件也打不开。

2008年夏天开始学习CPU的保护模式。
2015.01.11起稿。
2015年夏修改存档，尽管还有一些不完美的地方。
*/

#include <ntifs.h>
#include <windef.h>


#if defined(_AMD64_) || defined(_IA64_) //defined(_WIN64)

// Special Registers for AMD64.
typedef struct _AMD64_DESCRIPTOR {
    USHORT  Pad[3];
    USHORT  Limit;
    ULONG64 Base;
} AMD64_DESCRIPTOR, *PAMD64_DESCRIPTOR;

typedef union _KGDTENTRY64 {
    struct {
        USHORT  LimitLow;
        USHORT  BaseLow;
        union {
            struct {
                UCHAR   BaseMiddle;
                UCHAR   Flags1;
                UCHAR   Flags2;
                UCHAR   BaseHigh;
            } Bytes;

            struct {
                ULONG   BaseMiddle : 8;
                ULONG   Type : 5;//把S位包含进去了，也就是是否为系统段描述符的位。
                ULONG   Dpl : 2;
                ULONG   Present : 1;
                ULONG   LimitHigh : 4;
                ULONG   System : 1;//即AVL，系统软件自定义的。
                ULONG   LongMode : 1;
                ULONG   DefaultBig : 1;//即INTEL的D/B (default operation size/default stack pointer size and/or upper bound) flag。
                ULONG   Granularity : 1;
                ULONG   BaseHigh : 8;
            } Bits;
        };

        //ULONG BaseUpper;/*经观察，64下的结构的长度是6字节，不是上面定义的16字节。*/
        //ULONG MustBeZero;
    };

    //ULONG64 Alignment;
} KGDTENTRY64, *PKGDTENTRY64;


#else 

// Special Registers for i386
typedef struct _X86_DESCRIPTOR {
    USHORT  Pad;
    USHORT  Limit;
    ULONG   Base;
} X86_DESCRIPTOR, *PX86_DESCRIPTOR;

// GDT Entry
typedef struct _KGDTENTRY {
    USHORT  LimitLow;
    USHORT  BaseLow;
    union {
        struct {
            UCHAR   BaseMid;
            UCHAR   Flags1;     // Declare as bytes to avoid alignment
            UCHAR   Flags2;     // Problems.
            UCHAR   BaseHi;
        } Bytes;
        struct {
            ULONG   BaseMid : 8;
            ULONG   Type : 5;//把S位包含进去了，也就是是否为系统段描述符的位。
            ULONG   Dpl : 2;
            ULONG   Pres : 1;
            ULONG   LimitHi : 4;
            ULONG   Sys : 1;//即AVL，系统软件自定义的。
            ULONG   Reserved_0 : 1;//LongMode
            ULONG   Default_Big : 1;//即INTEL的D/B (default operation size/default stack pointer size and/or upper bound) flag。
            ULONG   Granularity : 1;
            ULONG   BaseHi : 8;
        } Bits;
    } HighWord;
} KGDTENTRY, *PKGDTENTRY;

#endif

/*
根据：Table 3-1. Code- and Data-Segment Types，仿照WINDBG的dg命令定义。
*/
char SegmentTypes[][256] = {
    "<Reserved>",//Data Read-Only缩写是：Data RO，也可认为是： <Reserved>。如果结构（UINT64）全部为零，也可认为是Reserved。
    "Data RO AC",//Data Read-Only, accessed
    "Data RW",//Data Read/Write
    "Data RW AC",//Data Read/Write, accessed
    "Data RO ED",//Data Read-Only, expand-down
    "Data RO ED AC",//Data Read-Only, expand-down, accessed
    "Data RW ED",//Data Read/Write, expand-down
    "Data RW ED AC",//Data Read/Write, expand-down, accessed

    "Code EO",//Code Execute-Only
    "Code EO AC",//Code Execute-Only, accessed
    "Code RE",//Code Execute/Read 加空格以便显示的对齐。
    "Code RE AC",//Code Execute/Read, accessed
    "Code EO CO",//Code Execute-Only, conforming
    "Code EO CO AC",//Code Execute-Only, conforming, accessed
    "Code RE CO",//Code Execute/Read, conforming
    "Code RE CO AC",//Code Execute/Read, conforming, accessed
    "TSS32 Busy ",//这个也可显示只要识别了TSS及内容。
    "TSS32 Avl" //这个在X86上出现了。
};  


DRIVER_UNLOAD DriverUnload;
VOID DriverUnload(__in PDRIVER_OBJECT DriverObject)
{   

}


#ifdef _X86_
__forceinline PKPCR KeGetPcr (VOID)
{
    return (PKPCR)__readfsdword(FIELD_OFFSET(KPCR, SelfPcr));
}
#endif


USHORT NTAPI GetGdtLimit ();//汇编函数。


#if defined(_WIN64)
void show_gdt(int i)
    /*
    i的取值可以是0.
    */
{
    //SIZE_T IDTR;
    //X86_DESCRIPTOR gdtr = {0};//A pointer to the memory location where the IDTR is stored.
    //KGDTENTRY * GDT = 0;
    USHORT GdtLimit = 0;

    SIZE_T r = 0;
    PVOID p = 0;
    int index = 0;
    int maximun = 0;

    PKGDTENTRY64 pkgdte;
    SIZE_T ISR = 0;

    KeSetSystemAffinityThread(i + 1);
    pkgdte = KeGetPcr()->GdtBase;//没有__sgdt,也不用sgdt汇编指令的办法。但是这个获取的没有长度。
    GdtLimit = GetGdtLimit ();//一般等于0x7f.
    KeRevertToUserAffinityThread();

    //p = &gdtr.Limit;
    //r = * (SIZE_T *)p;
    //pkgdte = (PKGDTENTRY)r; 

    /*
    其实直接：
    maximun = (idtr.Base + 1) / sizeof(KIDTENTRY);
    也可以。
    maximun一般等于256.
    */
    //if (gdtr.Pad % sizeof(KIDTENTRY) == 0) {
    //    maximun = gdtr.Pad / sizeof(KIDTENTRY);
    //} else {
    //    maximun = gdtr.Pad / sizeof(KIDTENTRY);
    //    maximun++;
    //}

    //if (GdtLimit % sizeof(KGDTENTRY64) == 0) {
    //    maximun = GdtLimit / sizeof(KGDTENTRY64);
    //} else {
    //    maximun = GdtLimit / sizeof(KGDTENTRY64);
    //    maximun++;//一般是128.
    //}

    maximun = (GdtLimit + 1) / sizeof(KGDTENTRY64);

    /*
    显示格式：    
    CPU SN Sel        Base              Limit          Type    Pl Size Gran Pres Long Flags
    --- -- ---- ----------------- ----------------- ---------- -- ---- ---- ---- ---- --------

    注释：CPU和SN是自己添加的。SN即Segment Name,如：CS，DS，FS等.
    */
    KdPrint(("Sel        Base             Limit             Type   DPl Size Gran Pres Long Flags\n"));//CPU SN 
    KdPrint(("---- ---------------- ---------------- ------------- --- ---- ---- ---- ---- --------\n"));//--- -- 
    KdPrint(("\n"));

    for ( ;index < maximun ;index++ ) 
    {
        PKGDTENTRY64 pkgdte_t = &pkgdte[index];
        SIZE_T Base = 0;
        SIZE_T Limit = 0;
        ULONG  Type = 0;
        char * size = NULL;
        char * Granularity = NULL;
        char * Present = NULL;
        char * LongMode = NULL;
        int    Flags = 0;        

        Base = pkgdte_t->Bits.BaseHigh;
        Base = (Base << 24);
        Base += (pkgdte_t->BaseLow + (pkgdte_t->Bits.BaseMiddle << 16));

        Limit = pkgdte_t->LimitLow + (pkgdte_t->Bits.LimitHigh << 16);

        if (pkgdte_t->Bits.DefaultBig && Base)
        {
            //扩充高位为1.即F.
            Base += 0xffffffff00000000;
        }      

        if (pkgdte_t->Bits.DefaultBig && pkgdte_t->Bits.Granularity)
        {
            //扩充高位为1.即F.
            SIZE_T t = Limit;
            Limit = (Limit << 12);
            Limit += PAGE_SIZE - 1;
        } 

        Type = pkgdte_t->Bits.Type;
        _bittestandreset(&Type, 4);//因为这个包含了S位，所以要清除这个位标志。

        if (pkgdte_t->Bits.DefaultBig)
        {
            size = "Bg  ";//Big 加空格是为了对齐显示。
        }
        else
        {
            size = "Nb  ";//Not Big 加空格是为了对齐显示。
        }

        if (pkgdte_t->Bits.Granularity)
        {
            Granularity = "Pg  ";//Page 加空格是为了对齐显示。
        }
        else
        {
            Granularity = "By  ";//Byte 加空格是为了对齐显示。
        }

        if (pkgdte_t->Bits.Present)
        {
            Present = "P   ";//Present 加空格是为了对齐显示。
        }
        else
        {
            Present = "NP  ";//NO Present 加空格是为了对齐显示。
        }

        if (pkgdte_t->Bits.LongMode)
        {
            LongMode = "Lo  ";//Long 加空格是为了对齐显示。
        }
        else
        {
            LongMode = "Nl  ";//NO long 加空格是为了对齐显示。
        }

        Flags = (pkgdte_t->Bytes.Flags2 >> 4);//去掉Segment limit的那几位。
        Flags = Flags << 8;
        Flags = Flags + pkgdte_t->Bytes.Flags1;

        KdPrint(("%04x %p %p %13s %03x %s %s %s %s 0x%04x\n", 
            index * 8, //sizeof (KGDTENTRY)
            Base, 
            Limit,
            SegmentTypes[Type],
            pkgdte_t->Bits.Dpl,
            size,
            Granularity,
            Present,            
            LongMode,
            Flags
            ));
    }
}
#else 
void show_gdt(int i)
    /*
    i的取值可以是0.
    */
{
    //SIZE_T IDTR;
    //X86_DESCRIPTOR gdtr = {0};//A pointer to the memory location where the IDTR is stored.
    //KGDTENTRY * GDT = 0;
    USHORT GdtLimit = 0;

    SIZE_T r = 0;
    PVOID p = 0;
    int index = 0;
    int maximun = 0;

    PKGDTENTRY pkgdte;
    SIZE_T ISR = 0;

    KeSetSystemAffinityThread(i + 1);
    pkgdte = KeGetPcr()->GDT;//没有__sgdt,也不用sgdt汇编指令的办法。但是这个获取的没有长度。
    GdtLimit = GetGdtLimit ();//一般等于0x3ff.
    KeRevertToUserAffinityThread();

    //p = &gdtr.Limit;
    //r = * (SIZE_T *)p;
    //pkgdte = (PKGDTENTRY)r; 

    /*
    其实直接：
    maximun = (idtr.Base + 1) / sizeof(KIDTENTRY);
    也可以。
    maximun一般等于256.
    */
    //if (gdtr.Pad % sizeof(KIDTENTRY) == 0) {
    //    maximun = gdtr.Pad / sizeof(KIDTENTRY);
    //} else {
    //    maximun = gdtr.Pad / sizeof(KIDTENTRY);
    //    maximun++;
    //}

    if (GdtLimit % sizeof(KGDTENTRY) == 0) {
        maximun = GdtLimit / sizeof(KGDTENTRY);
    } else {
        maximun = GdtLimit / sizeof(KGDTENTRY);
        maximun++;//一般是128.
    }

    /*
    显示格式：    
    CPU SN Sel        Base              Limit          Type    Pl Size Gran Pres Long Flags
    --- -- ---- ----------------- ----------------- ---------- -- ---- ---- ---- ---- --------

    注释：CPU和SN是自己添加的。SN即Segment Name,如：CS，DS，FS等.
    */
    KdPrint(("Sel  Base             Limit          Type DPl Size Gran Pres Long Flags\n"));//CPU SN 
    KdPrint(("---- -------- ------------- ------------- --- ---- ---- ---- ---- --------\n"));//--- -- 
    KdPrint(("\n"));

    for ( ;index < maximun ;index++ ) 
    {
        PKGDTENTRY pkgdte_t = &pkgdte[index];
        SIZE_T Base = 0;
        SIZE_T Limit = 0;
        ULONG  Type = 0;
        char * size = NULL;
        char * Granularity = NULL;
        char * Present = NULL;
        char * LongMode = NULL;
        int    Flags = 0;   

        //注意：0x38处的值不停的变化。
        USHORT  BaseLow = pkgdte_t->BaseLow;
        ULONG   BaseMid = pkgdte_t->HighWord.Bits.BaseMid;
        ULONG   BaseHi = pkgdte_t->HighWord.Bits.BaseHi;
        Base = (BaseHi << 24) + (BaseMid << 16) + BaseLow;//其实用位与更快 | 。

        if (pkgdte_t->HighWord.Bits.Granularity && BooleanFlagOn(pkgdte_t->HighWord.Bits.Type, 2 ) ) {//关于标志位及算法，见权威资料。
            Limit = pkgdte_t->LimitLow + (pkgdte_t->HighWord.Bits.LimitHi << 16);
            Limit *= PAGE_SIZE;
            Limit += PAGE_SIZE - 1;
        } else {
            Limit = pkgdte_t->LimitLow + (pkgdte_t->HighWord.Bits.LimitHi << 16);
        }

        Type = pkgdte_t->HighWord.Bits.Type;
        _bittestandreset(&Type, 4);//因为这个包含了S位，所以要清除这个位标志。

        if (pkgdte_t->HighWord.Bits.Default_Big)
        {
            size = "Bg  ";//Big 加空格是为了对齐显示。
        }
        else
        {
            size = "Nb  ";//Not Big 加空格是为了对齐显示。
        }

        if (pkgdte_t->HighWord.Bits.Granularity)
        {
            Granularity = "Pg  ";//Page 加空格是为了对齐显示。
        }
        else
        {
            Granularity = "By  ";//Byte 加空格是为了对齐显示。
        }

        if (pkgdte_t->HighWord.Bits.Pres)
        {
            Present = "P   ";//Present 加空格是为了对齐显示。
        }
        else
        {
            Present = "NP  ";//NO Present 加空格是为了对齐显示。
        }

        if (pkgdte_t->HighWord.Bits.Reserved_0)
        {
            LongMode = "Lo  ";//Long 加空格是为了对齐显示。
        }
        else
        {
            LongMode = "Nl  ";//NO long 加空格是为了对齐显示。
        }

        Flags = (pkgdte_t->HighWord.Bytes.Flags2 >> 4);//去掉Segment limit的那几位。
        Flags = Flags << 8;
        Flags = Flags + pkgdte_t->HighWord.Bytes.Flags1;

        KdPrint(("%04x %p %p %13s %03x %s %s %s %s 0x%04x\n", 
            index * 8, //sizeof (KGDTENTRY)
            Base, 
            Limit,
            SegmentTypes[Type],
            pkgdte_t->HighWord.Bits.Dpl,
            size,
            Granularity,
            Present,            
            LongMode,
            Flags
            ));
    }
}
#endif


#pragma INITCODE
DRIVER_INITIALIZE DriverEntry;
NTSTATUS DriverEntry(__in struct _DRIVER_OBJECT * DriverObject, __in PUNICODE_STRING RegistryPath)
{
    int i = 0;

    KdBreakPoint();

    DriverObject->DriverUnload = DriverUnload;

    for ( ;i < KeNumberProcessors ;i++ )//KeQueryMaximumProcessorCount()  KeGetCurrentProcessorNumber
    {        
        show_gdt(i);        
    }

    return STATUS_SUCCESS;
} 

```

结果及验证：

32位Windows的结果：

```
kd> g
Sel  Base             Limit          Type DPl Size Gran Pres Long Flags
---- -------- ------------- ------------- --- ---- ---- ---- ---- --------

0000 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0008 00000000 FFFFFFFF    Code RE AC 000 Bg   Pg   P    Nl   0x0c9b
0010 00000000 FFFFFFFF    Data RW AC 000 Bg   Pg   P    Nl   0x0c93
0018 00000000 FFFFFFFF    Code RE AC 003 Bg   Pg   P    Nl   0x0cfb
0020 00000000 FFFFFFFF    Data RW AC 003 Bg   Pg   P    Nl   0x0cf3
0028 80042000 000020AB    Code RE AC 000 Nb   By   P    Nl   0x008b
0030 FFDFF000 00001FFF    Data RW AC 000 Bg   Pg   P    Nl   0x0c93
0038 00000000 00000FFF    Data RW AC 003 Bg   By   P    Nl   0x04f3
0040 00000400 0000FFFF       Data RW 003 Nb   By   P    Nl   0x00f2
0048 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0050 80552700 00000068    Code EO AC 000 Nb   By   P    Nl   0x0089
0058 80552768 00000068    Code EO AC 000 Nb   By   P    Nl   0x0089
0060 00022F40 0000FFFF    Data RW AC 000 Nb   By   P    Nl   0x0093
0068 000B8000 00003FFF       Data RW 000 Nb   By   P    Nl   0x0092
0070 FFFF7000 000003FF       Data RW 000 Nb   By   P    Nl   0x0092
0078 80400000 0000FFFF       Code RE 000 Nb   By   P    Nl   0x009a
0080 80400000 0000FFFF       Data RW 000 Nb   By   P    Nl   0x0092
0088 00000000 00000000       Data RW 000 Nb   By   P    Nl   0x0092
0090 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0098 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00a0 823816B8 00000068    Code EO AC 000 Nb   By   P    Nl   0x0089
00a8 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00b0 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00b8 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00c0 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00c8 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00d0 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00d8 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
00e0 F850F000 0000FFFF Code RE CO AC 000 Nb   By   P    Nl   0x009f
00e8 00000000 0000FFFF       Data RW 000 Nb   By   P    Nl   0x0092
00f0 804FD040 000003B7       Code EO 000 Nb   By   P    Nl   0x0098
00f8 00000000 0000FFFF       Data RW 000 Nb   By   P    Nl   0x0092
0100 BA4D2400 0000FFFF    Data RW AC 000 Bg   By   P    Nl   0x0493
0108 BA4D2400 0000FFFF    Data RW AC 000 Bg   By   P    Nl   0x0493
0110 BA4D2400 0000FFFF    Data RW AC 000 Bg   By   P    Nl   0x0493
0118 00008003 0000F120    <Reserved> 000 Nb   By   NP   Nl   0x0000
0120 00008003 0000F128    <Reserved> 000 Nb   By   NP   Nl   0x0000
0128 00008003 0000F130    <Reserved> 000 Nb   By   NP   Nl   0x0000
0130 00008003 0000F138    <Reserved> 000 Nb   By   NP   Nl   0x0000
0138 00008003 0000F140    <Reserved> 000 Nb   By   NP   Nl   0x0000
0140 00008003 0000F148    <Reserved> 000 Nb   By   NP   Nl   0x0000
0148 00008003 0000F150    <Reserved> 000 Nb   By   NP   Nl   0x0000
0150 00008003 0000F158    <Reserved> 000 Nb   By   NP   Nl   0x0000
0158 00008003 0000F160    <Reserved> 000 Nb   By   NP   Nl   0x0000
0160 00008003 0000F168    <Reserved> 000 Nb   By   NP   Nl   0x0000
0168 00008003 0000F170    <Reserved> 000 Nb   By   NP   Nl   0x0000
0170 00008003 0000F178    <Reserved> 000 Nb   By   NP   Nl   0x0000
0178 00008003 0000F180    <Reserved> 000 Nb   By   NP   Nl   0x0000
0180 00008003 0000F188    <Reserved> 000 Nb   By   NP   Nl   0x0000
0188 00008003 0000F190    <Reserved> 000 Nb   By   NP   Nl   0x0000
0190 00008003 0000F198    <Reserved> 000 Nb   By   NP   Nl   0x0000
0198 00008003 0000F1A0    <Reserved> 000 Nb   By   NP   Nl   0x0000
01a0 00008003 0000F1A8    <Reserved> 000 Nb   By   NP   Nl   0x0000
01a8 00008003 0000F1B0    <Reserved> 000 Nb   By   NP   Nl   0x0000
01b0 00008003 0000F1B8    <Reserved> 000 Nb   By   NP   Nl   0x0000
01b8 00008003 0000F1C0    <Reserved> 000 Nb   By   NP   Nl   0x0000
01c0 00008003 0000F1C8    <Reserved> 000 Nb   By   NP   Nl   0x0000
01c8 00008003 0000F1D0    <Reserved> 000 Nb   By   NP   Nl   0x0000
01d0 00008003 0000F1D8    <Reserved> 000 Nb   By   NP   Nl   0x0000
01d8 00008003 0000F1E0    <Reserved> 000 Nb   By   NP   Nl   0x0000
01e0 00008003 0000F1E8    <Reserved> 000 Nb   By   NP   Nl   0x0000
01e8 00008003 0000F1F0    <Reserved> 000 Nb   By   NP   Nl   0x0000
01f0 00008003 0000F1F8    <Reserved> 000 Nb   By   NP   Nl   0x0000
01f8 00008003 0000F200    <Reserved> 000 Nb   By   NP   Nl   0x0000
0200 00008003 0000F208    <Reserved> 000 Nb   By   NP   Nl   0x0000
0208 00008003 0000F210    <Reserved> 000 Nb   By   NP   Nl   0x0000
0210 00008003 0000F218    <Reserved> 000 Nb   By   NP   Nl   0x0000
0218 00008003 0000F220    <Reserved> 000 Nb   By   NP   Nl   0x0000
0220 00008003 0000F228    <Reserved> 000 Nb   By   NP   Nl   0x0000
0228 00008003 0000F230    <Reserved> 000 Nb   By   NP   Nl   0x0000
0230 00008003 0000F238    <Reserved> 000 Nb   By   NP   Nl   0x0000
0238 00008003 0000F240    <Reserved> 000 Nb   By   NP   Nl   0x0000
0240 00008003 0000F248    <Reserved> 000 Nb   By   NP   Nl   0x0000
0248 00008003 0000F250    <Reserved> 000 Nb   By   NP   Nl   0x0000
0250 00008003 0000F258    <Reserved> 000 Nb   By   NP   Nl   0x0000
0258 00008003 0000F260    <Reserved> 000 Nb   By   NP   Nl   0x0000
0260 00008003 0000F268    <Reserved> 000 Nb   By   NP   Nl   0x0000
0268 00008003 0000F270    <Reserved> 000 Nb   By   NP   Nl   0x0000
0270 00008003 0000F278    <Reserved> 000 Nb   By   NP   Nl   0x0000
0278 00008003 0000F280    <Reserved> 000 Nb   By   NP   Nl   0x0000
0280 00008003 0000F288    <Reserved> 000 Nb   By   NP   Nl   0x0000
0288 00008003 0000F290    <Reserved> 000 Nb   By   NP   Nl   0x0000
0290 00008003 0000F298    <Reserved> 000 Nb   By   NP   Nl   0x0000
0298 00008003 0000F2A0    <Reserved> 000 Nb   By   NP   Nl   0x0000
02a0 00008003 0000F2A8    <Reserved> 000 Nb   By   NP   Nl   0x0000
02a8 00008003 0000F2B0    <Reserved> 000 Nb   By   NP   Nl   0x0000
02b0 00008003 0000F2B8    <Reserved> 000 Nb   By   NP   Nl   0x0000
02b8 00008003 0000F2C0    <Reserved> 000 Nb   By   NP   Nl   0x0000
02c0 00008003 0000F2C8    <Reserved> 000 Nb   By   NP   Nl   0x0000
02c8 00008003 0000F2D0    <Reserved> 000 Nb   By   NP   Nl   0x0000
02d0 00008003 0000F2D8    <Reserved> 000 Nb   By   NP   Nl   0x0000
02d8 00008003 0000F2E0    <Reserved> 000 Nb   By   NP   Nl   0x0000
02e0 00008003 0000F2E8    <Reserved> 000 Nb   By   NP   Nl   0x0000
02e8 00008003 0000F2F0    <Reserved> 000 Nb   By   NP   Nl   0x0000
02f0 00008003 0000F2F8    <Reserved> 000 Nb   By   NP   Nl   0x0000
02f8 00008003 0000F300    <Reserved> 000 Nb   By   NP   Nl   0x0000
0300 00008003 0000F308    <Reserved> 000 Nb   By   NP   Nl   0x0000
0308 00008003 0000F310    <Reserved> 000 Nb   By   NP   Nl   0x0000
0310 00008003 0000F318    <Reserved> 000 Nb   By   NP   Nl   0x0000
0318 00008003 0000F320    <Reserved> 000 Nb   By   NP   Nl   0x0000
0320 00008003 0000F328    <Reserved> 000 Nb   By   NP   Nl   0x0000
0328 00008003 0000F330    <Reserved> 000 Nb   By   NP   Nl   0x0000
0330 00008003 0000F338    <Reserved> 000 Nb   By   NP   Nl   0x0000
0338 00008003 0000F340    <Reserved> 000 Nb   By   NP   Nl   0x0000
0340 00008003 0000F348    <Reserved> 000 Nb   By   NP   Nl   0x0000
0348 00008003 0000F350    <Reserved> 000 Nb   By   NP   Nl   0x0000
0350 00008003 0000F358    <Reserved> 000 Nb   By   NP   Nl   0x0000
0358 00008003 0000F360    <Reserved> 000 Nb   By   NP   Nl   0x0000
0360 00008003 0000F368    <Reserved> 000 Nb   By   NP   Nl   0x0000
0368 00008003 0000F370    <Reserved> 000 Nb   By   NP   Nl   0x0000
0370 00008003 0000F378    <Reserved> 000 Nb   By   NP   Nl   0x0000
0378 00008003 0000F380    <Reserved> 000 Nb   By   NP   Nl   0x0000
0380 00008003 0000F388    <Reserved> 000 Nb   By   NP   Nl   0x0000
0388 00008003 0000F390    <Reserved> 000 Nb   By   NP   Nl   0x0000
0390 00008003 0000F398    <Reserved> 000 Nb   By   NP   Nl   0x0000
0398 00008003 0000F3A0    <Reserved> 000 Nb   By   NP   Nl   0x0000
03a0 00008003 0000F3A8    <Reserved> 000 Nb   By   NP   Nl   0x0000
03a8 00008003 0000F3B0    <Reserved> 000 Nb   By   NP   Nl   0x0000
03b0 00008003 0000F3B8    <Reserved> 000 Nb   By   NP   Nl   0x0000
03b8 00008003 0000F3C0    <Reserved> 000 Nb   By   NP   Nl   0x0000
03c0 00008003 0000F3C8    <Reserved> 000 Nb   By   NP   Nl   0x0000
03c8 00008003 0000F3D0    <Reserved> 000 Nb   By   NP   Nl   0x0000
03d0 00008003 0000F3D8    <Reserved> 000 Nb   By   NP   Nl   0x0000
03d8 00008003 0000F3E0    <Reserved> 000 Nb   By   NP   Nl   0x0000
03e0 00008003 0000F3E8    <Reserved> 000 Nb   By   NP   Nl   0x0000
03e8 00008003 0000F3F0    <Reserved> 000 Nb   By   NP   Nl   0x0000
03f0 00008003 0000F3F8    <Reserved> 000 Nb   By   NP   Nl   0x0000
03f8 00000000 00000000    <Reserved> 000 Nb   By   NP   Nl   0x0000

```

验证，可以和前面的显示做对比。

64位Windows的结果：

```
0: kd> g
Sel        Base             Limit             Type   DPl Size Gran Pres Long Flags
---- ---------------- ---------------- ------------- --- ---- ---- ---- ---- --------

0000 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0008 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0010 0000000000000000 0000000000000000    Code RE AC 000 Nb   By   P    Lo   0x029b
0018 0000000000000000 00000000FFFFFFFF    Data RW AC 000 Bg   Pg   P    Nl   0x0c93
0020 0000000000000000 00000000FFFFFFFF    Code RE AC 003 Bg   Pg   P    Nl   0x0cfb
0028 0000000000000000 00000000FFFFFFFF    Data RW AC 003 Bg   Pg   P    Nl   0x0cf3
0030 0000000000000000 0000000000000000    Code RE AC 003 Nb   By   P    Lo   0x02fb
0038 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0040 0000000001D52080 0000000000000067    Code RE AC 000 Nb   By   P    Nl   0x008b
0048 000000000000FFFF 000000000000F800    <Reserved> 000 Nb   By   NP   Nl   0x0000
0050 FFFFFFFFFFFA0000 0000000000003C00    Data RW AC 003 Bg   By   P    Nl   0x04f3
0058 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0060 0000000000000000 00000000FFFFFFFF       Code RE 000 Bg   Pg   P    Nl   0x0c9a
0068 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0070 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0078 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
Sel        Base             Limit             Type   DPl Size Gran Pres Long Flags
---- ---------------- ---------------- ------------- --- ---- ---- ---- ---- --------

0000 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0008 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0010 0000000000000000 0000000000000000    Code RE AC 000 Nb   By   P    Lo   0x029b
0018 0000000000000000 00000000FFFFFFFF    Data RW AC 000 Bg   Pg   P    Nl   0x0c93
0020 0000000000000000 00000000FFFFFFFF    Code RE AC 003 Bg   Pg   P    Nl   0x0cfb
0028 0000000000000000 00000000FFFFFFFF    Data RW AC 003 Bg   Pg   P    Nl   0x0cf3
0030 0000000000000000 0000000000000000    Code RE AC 003 Nb   By   P    Lo   0x02fb
0038 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0040 00000000009F7E40 0000000000000067    Code RE AC 000 Nb   By   P    Nl   0x008b
0048 000000000000FFFF 000000000000F880    <Reserved> 000 Nb   By   NP   Nl   0x0000
0050 FFFFFFFFFFFE0000 0000000000007C00    Data RW AC 003 Bg   By   P    Nl   0x04f3
0058 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0060 0000000000000000 00000000FFFFFFFF       Code RE 000 Bg   Pg   P    Nl   0x0c9a
0068 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0070 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000
0078 0000000000000000 0000000000000000    <Reserved> 000 Nb   By   NP   Nl   0x0000

```

验证，可以和前面（某个）的显示做对比。

这里显示2个，是因为有两个CPU。

细心的你应该（从对比中）还会发现一些不足和不一样的地方，期待你的改正，剩下的任务也就是你要改正的地方。

如：添加显示CPU的个数，及段的名字（特别是系统段，各种门）等。

不当之处，敬请指出。