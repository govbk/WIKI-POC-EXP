# uctf-杂项题目分析

BP 断点
-----

* * *

> 分数:100 描述: 提示 1：key 不是大家喜欢的波波老师！  
> 提示 2：bmp+png  
> 提示 3：CRC Link:[http://pan.baidu.com/s/1o6x4FEE](http://pan.baidu.com/s/1o6x4FEE)

Bmp 只是诱饵，给大家看看波波老师。关键在于 png 图片，根据 png 格式图片，以及提示，很明显可以想到利用 crc 去爆破宽度和高度。可以用 c 或者 py，py 在这题爆破三个字节还是可以的，如果字节太多还是用 c 吧。 之所以名字叫做 BP 断点，是因为是 bmp+png 的图片。

**参考 c 代码：**

```
#include "stdafx.h"
#include <windows.h>
#include <stdio.h>
//crc32.h
#ifndef _CRC32_H
#define _CRC32_H
UINT crc32( UCHAR *buf, int len);
#endif
static UINT CRC32[256];
static char init = 0;
//初始化表
static void init_table()
{
int i,j;
UINT crc;
for(i = 0;i < 256;i++)
{
crc = i;
for(j = 0;j < 8;j++)
{
if(crc & 1) 
{
crc = (crc >> 1) ^ 0xEDB88320;
}
else
{
crc = crc >> 1;
}
}
CRC32[i] = crc;
}
}
//crc32实现函数
UINT crc32( UCHAR *buf, int len)
{
UINT ret = 0xFFFFFFFF;
int i;
if( !init )
{
init_table();
init = 1;
}
for(i = 0; i < len;i++)
{
ret = CRC32[((ret & 0xFF) ^ buf[i])] ^ (ret >> 8);
}
ret = ~ret;
return ret;
}
int main()
{
char sss[17]="\x49\x48\x44\x52\x00\x00";
int a1,a2,a3,a4,a5,a6,a7,a8;
int _crc32 = 0;
for (a3=0x00;a3<=0xff;a3++)
for (a4=0x00;a4<=0xff;a4++)
for (a7=0x00;a7<=0xff;a7++)
for (a8=0x00;a8<=0xff;a8++)
{ 
sss[6]=(char)a3;
sss[7]=(char)a4;
sss[8]='\x00';
sss[9]='\x00';
sss[10]=(char)a7;
sss[11]=(char)a8;
sss[12]='\x08';sss[13]='\x06';sss[14]='\x00';sss[15]='\x00';sss[16]='\x00';
sss[17]='\x00';
_crc32 = crc32((UCHAR *)sss, 17);
if(_crc32 == 0x80BF36CC)
{
printf("%s,%x,%x,%x,%x\n", sss,a3,a4,a7,a8);
}
}
return 0;
}

```

最后结果：

![enter image description here](http://drops.javaweb.org/uploads/images/b7d7de26ac46e05cfdc468687695d1b66e7d4e82.jpg)

**参考 python 代码：**

```
# -*- coding:utf-8 -*-import binascii
#注意返回的是小写  形如："0x1c4d1d3cL",  并且为字符串。
def CalcCrc32(str):
return hex(binascii.crc32(str) & 0xFFFFFFFF)
if __name__=="__main__":
str1 = '\x49\x48\x44\x52\x00\x00\x01'
str2 = '\x00\x00'
str3 = '\x08\x06\x00\x00\x00' 
int1 = 0
int2 = 0
int3 = 0
for int1 in range(0,256):
for int2 in range(0, 256):
for int3 in range(0, 256):
m = str1   + chr(int1) + str2 + chr(int2) + chr(int3) + str3
if (CalcCrc32(m) == "0x80bf36ccL"):
print "Yeah, U Found it!"
print hex(int1)
print hex(int2)
print hex(int3)
exit()

```

跑几分钟后，结果就出来了。

![enter image description here](http://drops.javaweb.org/uploads/images/786046ce1b5ebc1b91b68d73897ab520adb84fce.jpg)

听听音乐
----

* * *

先下载压缩包 http://pan.baidu.com/s/1bncmvuR 解压后发现两个文件`Music.exe`,`Readme.doc`. 要求利用 xp sp3 对目标程序进行溢出 既然是比赛，那么肯定就是要有溢出点的啦 直接打开 exe，听到了甩葱歌 于是不准备关掉他了， 新开一个例程，OD 载入

![enter image description here](http://drops.javaweb.org/uploads/images/4ed88baa8517e521437e0f437ab438076c1bdc46.jpg)

发现是 VC6 链接的 于是就果断去找 main 函数了 不过 exe 程序居然自杀了，不能听甩葱歌，差评 果断定位到了 main

![enter image description here](http://drops.javaweb.org/uploads/images/dd882ebd838586dbe7a98f7a55224f123d510eac.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0b26408c5f4f05701226d049d412a1ad412269d7.jpg)

写入内容为 exe 的启动参数 于是猜想启动参数这个地方应该就是所谓的溢出点 于是写了一个简单程序，界面如下

![enter image description here](http://drops.javaweb.org/uploads/images/a2ecffd0e21b59a63b1a17aa6bbdb49276884086.jpg)

最后发现 273 程序就会崩溃 于是使用 273 创建进程 OD 附加并设置 F2 断点于 ReadFile 于多次返回后定位到

![enter image description here](http://drops.javaweb.org/uploads/images/2604a08b44b3fadc5e55485bc9edd1fc10cba3da.jpg)

观察堆栈后发现 此时已覆盖[esp]一个字节 Ret 后肯定会跳转到内存中某一被修改的位置执行代码 于是构建 shellcode 内存收缩

```
FF E4 (jmp esp)

```

最终定位到`0x77D29353`,打开`010 editor`,构建 exp.

![enter image description here](http://drops.javaweb.org/uploads/images/c742e28afc0759293296c6de91bd805e02891bf5.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/24f0652a33377983eefb971e26f3fe35eb0eb0f9.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/df09279868185ba73285cc98945ba2d31f2fe4a9.jpg)

接下来构造功能代码 之后我发现程序段里竟然有可耻的 call eax 找了个地址比较吉利的构造了下 用阿尔法转换了下 shellcode 最终 exp 如下

![enter image description here](http://drops.javaweb.org/uploads/images/d07079ab09cee04429a3d3fe1a6fe03247ae62f7.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/80f224d75fd5c122d14dd048e81c994962ffdcf0.jpg)

最简单的加解密
-------

* * *

> 分数:300 描述: 提示 1：DES  
> 提示 2：凯撒

得到两串二进制后，转换为 16 进制分别为：

```
0x4d3259784e7a49304f444a6f4e57746f4e44597a61575a6d4d3267785a6a5a6e5a6d59344d4763344f544d354f4441784f5774724e4449796144566d4f446730L
0x5379636c30763372L

```

转换为字符串分别为：

```
M2YxNzI0ODJoNWtoNDYzaWZmM2gxZjZnZmY4MGc4OTM5ODAxOWtrNDIyaDVmODg0
Sycl0v3r

```

可以认为第一个字符串为 DES 的密文，第二个字符串为 DES 的密钥。解密发现不对。但是根 据大小写和数字可以猜测为 base64，解密后的字符串：

```
3f172482h5kh463iff3h1f6gff80g89398019kk422h5f884

```

再用 DES 的密钥解密，发现还是不对。根据提示“凯撒”去解码试试。

```
http://crypo.in.ua/tools/eng_caesar.php

```

![enter image description here](http://drops.javaweb.org/uploads/images/2e02b6cebedcd72f5d763c91dfda8211f4372ae7.jpg)

解几次后发现`3a172482c5fc463daa3c1a6baa80b89398019ff422c5a884`这串是可以用DES 解密的。

![enter image description here](http://drops.javaweb.org/uploads/images/cefb7e6b473b3b2265a1a765136789ee22908990.jpg)

表白墙
---

* * *

在输出”tell me:”之后程序会读入用户输入，但这里使用了危险的 scanf(“%s”)而没有任何额外 的检查，直接输入超长字符串就可以造成 buffer overflow。

![enter image description here](http://drops.javaweb.org/uploads/images/199ccb89795ae5f55f7f7bd6f2b0e7f06c8f5987.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0aa41c40a6ee378393b1e2fda47e5f5cf00b0627.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/cc3453465a66d023dbc2797423f6cbc47c5621a6.jpg)

成功利用弹 MessageBox 的截图如下

![enter image description here](http://drops.javaweb.org/uploads/images/7230d86b7c692bbe5853c6d93afbc6fe409e7a1f.jpg)

P.S：其实程序里还有一个格式化字符串漏洞，不过那个利用起来没这个方便，所以就直接 用这个了。

找女朋友
----

* * *

加载到 od 中运行程序，程序发现了我们启动了 od，并打印出了 SOD 的驱动名

![enter image description here](http://drops.javaweb.org/uploads/images/4451923e6a43e3847b3f3c8222a8ddac2b9c0e05.jpg)

程序 main 函数在`0x401000`处，在这里用了`EnumDeviceDrivers`和`GetDeviceDriverFileNameA`函数来枚举系统中已经加载的驱动，并判断 dbghelp.dll 路径与系统路径是否相同，如果不同 就认为系统中运行了 od 驱动对象的 DriverSection 保存了一个指向_LDR_DATA_TABLE_ENTRY 指针，这个结构中有着一 个所有驱动的链表，通过遍历这个链表就可以知道加载了哪些驱动，如果想要程序找不到一 个驱动，我们只需要从这个链表中把相应的驱动摘下来 以下是具体代码：

```
#include <ntddk.h>
#define INITCODE code_seg("INIT")
#define PAGECODE code_seg("PAGE")
#define PROCESS_ID_OFFSET 0x84
#define IMAGE_NAME_OFFSET 0x174
#define PROCESS_LINK_OFFSET 0x88
#define PROCESS_EXITTIME    0x78
typedef struct _SYSTEM_SERVICE_TABLE
{
PVOID    *ServiceTableBase;
PULONG   *ServiceCounterTableBase;
ULONG     NumberOfServices;
ULONG     ParamTableBase;
}SSDT,   *PSSDT;
__declspec(dllimport) SSDT   KeServiceDescriptorTable;
//_LDR_DATA_TABLE_ENTRY 声明
typedef struct _LDR_DATA_TABLE_ENTRY
{
LIST_ENTRY InLoadOrderLinks;
LIST_ENTRY InMemoryOrderLinks;
LIST_ENTRY InInitializationOrderLinks;
PVOID DllBase;
PVOID EntryPoint;
ULONG SizeOfImage;
UNICODE_STRING FullDllName;
UNICODE_STRING BaseDllName; 
ULONG Flags;
USHORT LoadCount;
USHORT TlsIndex;
union
{
LIST_ENTRY HashLinks;
struct
{
PVOID SectionPointer;
ULONG CheckSum;
};
};
ULONG TimeDateStamp;
}LDR_DATA_TABLE_ENTRY, *PLDR_DATA_TABLE_ENTRY;
/////////////////////////////////////////////////////////////
void DriverUnload(IN PDRIVER_OBJECT pDriverObject);
void ShowProcess();
struct _LIST_ENTRY *tmp;
/////////////////////////////////////////////////////////////
#pragma INITCODE
NTSTATUS DriverEntry(PDRIVER_OBJECT pDriverObject, PUNICODE_STRING pRegisterPath) 
{
PLDR_DATA_TABLE_ENTRY pTableEntry = NULL;
PLIST_ENTRY pCur = NULL, pHead = NULL;
UNICODE_STRING str_Name;
ULONG EProcess,FirstEProcess;
LIST_ENTRY*  ActiveProcessLinks;
ULONG pid,dwCount=0;
PUCHAR pImage;
//PPROCESS_INFO ProcessInfo={0};
pDriverObject->DriverUnload = DriverUnload;
RtlInitUnicodeString(&str_Name, L"fengyue0.sys");
//从驱动对象中的 DriverSection 获得_LDR_DATA_TABLE_ENTRY 指针
pTableEntry = (PLDR_DATA_TABLE_ENTRY)pDriverObject->DriverSection;
//使头指针和当前指针指向模块链表中的一个模块
pCur = pHead = pTableEntry->InLoadOrderLinks.Blink;
do 
{
//获得模块指针
pTableEntry = (PLDR_DATA_TABLE_ENTRY)pCur;
if (pTableEntry->BaseDllName.Buffer)
{
if (RtlCompareUnicodeString(&str_Name, &(pTableEntry->BaseDllName), FALSE) == 
0)
{
//从链表中删除模块
pTableEntry->InLoadOrderLinks.Blink->Flink  = 
pTableEntry->InLoadOrderLinks.Flink;
pTableEntry->InLoadOrderLinks.Flink->Blink  = 
pTableEntry->InLoadOrderLinks.Blink;
break;
}
}
pCur = pCur->Flink;
}while (pCur != pHead);
/////////////////////////////////////////////////////////////
//显示进程
ShowProcess();
return STATUS_SUCCESS;
} 
#pragma PAGECODE
void DriverUnload(IN PDRIVER_OBJECT pDriverObject)
{
}
void ShowProcess()
{
ULONG OriFunAddr;
UNICODE_STRING str_FuncName;
PULONG ssdt_base;
RtlInitUnicodeString(&str_FuncName,L"NtQuerySystemInformation");
//获取 ssdt 基址
ssdt_base = (PULONG) KeServiceDescriptorTable.ServiceTableBase;
//获取 NtQuerySystemInformation 原地址
OriFunAddr =(ULONG) MmGetSystemRoutineAddress(&str_FuncName);
//判断当前 ssdt 中地址是否被替换
if (ssdt_base[0xAD] != OriFunAddr) 
{
DbgPrint("NtQuerySystemInformation has been hooked!fix it...");
ssdt_base[0xAD] = OriFunAddr;
DbgPrint("success!");
}
}

```

题目中的第二个目标就是使 od 进程在 windows 自带的任务管理器中显示出来， fengyue0.sys 驱动会在 ssdt 中把`NtQuerySystemInformation`函数 hook 掉，所以，当 windows 的任务管理 器通过这个函数枚举进程的时候就会把 od 进程隐藏了

![enter image description here](http://drops.javaweb.org/uploads/images/b7ec93ceac328905706a3d8d05eb8f77c76dd05b.jpg)

知道了隐藏的原理之后，我们的目标就转换为了，把`NtQuerySystemInformation`的 ssdt hook 给恢复了。 在`KeServiceDescriptorTable`中可以获得 ssdt 的基地址，再通过`NtQuerySystemInformation`在 ssdt 中的索引号就可以得到在 ssdt 中存放的它的地址，但是 ssdt 中的地址不一定是函数真 正的地址，有可能是被 hook 了的地址，所以可以再 MmGetSystemRoutineAddress 获得函数 真正的地址，然后与 ssdt 中的对比，如果相同则说明函数没有被 hook，反之函数被 hook， 我们的目的是恢复它的真正地址，现在既然已经有了真正的地址，就可以直接把 ssdt 中的 假地址给换掉，就恢复了`NtQuerySystemInformation`的 ssdt hook。具体代码在上述代码的 ShowProcess()函数中。

用 od 加 载 目 标 程 序 后 ， 把 我 们 的 驱 动 用 DriverMonitor 加 载 并 运

![enter image description here](http://drops.javaweb.org/uploads/images/9a28c0bdcab344c2baf4d2608e3effd8e4f9e804.jpg)

之后在 od 中运行目标程序

![enter image description here](http://drops.javaweb.org/uploads/images/2a3b0571115a5717126937d759b075b2c4a9196e.jpg)

程序显示没有发现 od，说明我们隐藏驱动成功了，再到 windows 任务管理器中查看一下， ollydbg.exe 进程也出现了