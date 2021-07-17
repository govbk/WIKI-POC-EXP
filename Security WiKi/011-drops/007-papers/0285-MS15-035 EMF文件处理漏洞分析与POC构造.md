# MS15-035 EMF文件处理漏洞分析与POC构造

MS15-035是Microsoft Graphics 组件处理增强型图元文件 (EMF) 的漏洞，可能允许远程执行代码。

通过补丁比对，可以看到主要是修补了一些可能存在整形溢出的位置，但是这些位置，我尝试了很多方法都无法执行到。

![enter image description here](http://drops.javaweb.org/uploads/images/e7ef0c153baaad8d3aa577edd143d2007bcaab3e.jpg)

但是

```
int __thiscall MRSETDIBITSTODEVICE::bPlay(EMRSETDIBITSTODEVICE *this, HDC hdc, struct tagHANDLETABLE *a3, unsigned int a4)

```

的修补是个例，补丁前的代码如下：

![enter image description here](http://drops.javaweb.org/uploads/images/33f4fd23df97d5a5b885a887154890d752a9341c.jpg)

打补丁后，代码如下：

![enter image description here](http://drops.javaweb.org/uploads/images/303af110f88744ab0d357daec6cc4fcef7043c71.jpg)

显然补丁后的代码对LocalAlloc分配的内存空间的最小值进行了限制，而打补丁之前并没有限制，因此猜测这里可能存在一个缓冲区越界写入问题。

通过分析函数调用链，可以找到MRSETDIBITSTODEVICE::bPlay被PlayEnhMetaFileRecord调用。PlayEnhMetaFileRecord根据EMF文件中元文件块类型调用不同的解析函数。09年的文章《[New EMF gdiplus.dll crash not exploitable for code execution](http://blogs.technet.com/b/srd/archive/2009/03/26/new-emf-gdiplus-dll-crash-not-exploitable-for-code-execution.aspx)》描述的EMF漏洞CVE-2009-1217也进一步确认了explorer进程就是通过PlayEnhMetaFileRecord解析EMF文件的元文件块的。

下面简要介绍一下EMF文件的结构，EMF文件由可变大小的元文件块组成。每个元文件块都是一个可变长度的ENHMETARECORD结构，结构如下。

```
typedef struct tagENHMETARECORD {
  DWORD iType;
  DWORD nSize;
  DWORD dParm[1];
} ENHMETARECORD, *PENHMETARECORD;

```

SDK中定义了不同的iType类型，如下所示。

![enter image description here](http://drops.javaweb.org/uploads/images/4fccf57dbe46aa8c6ccf854ce35556fd003b1847.jpg)

根据iType类型的不同，dParm是不同的结构，EMR_SETDIBITSTODEVICE对应的结构是EMRSETDIBITSTODEVICE。

```
typedef struct tagEMR
{
    DWORD   iType;              // Enhanced metafile record type
    DWORD   nSize;              // Length of the record in bytes.
                                // This must be a multiple of 4.
} EMR, *PEMR;

typedef struct tagEMRSETDIBITSTODEVICE
{
    EMR     emr;
    RECTL   rclBounds;          // Inclusive-inclusive bounds in device units
    LONG    xDest;
    LONG    yDest;
    LONG    xSrc;
    LONG    ySrc;
    LONG    cxSrc;
    LONG    cySrc;
    DWORD   offBmiSrc;          // Offset to the source BITMAPINFO structure
    DWORD   cbBmiSrc;           // Size of the source BITMAPINFO structure
    DWORD   offBitsSrc;         // Offset to the source bitmap bits
    DWORD   cbBitsSrc;          // Size of the source bitmap bits
    DWORD   iUsageSrc;          // Source bitmap info color table usage
    DWORD   iStartScan;
    DWORD   cScans;
} EMRSETDIBITSTODEVICE, *PEMRSETDIBITSTODEVICE;

对于MRSETDIBITSTODEVICE::bPlay函数，其第一个参数为EMRSETDIBITSTODEVICE。为了验证猜想的正确性，通过程序生成一个小的emf文件，对其中的iType进行修改，以便其执行到MRSETDIBITSTODEVICE::bPlay函数，将0x54（EMR_EXTTEXTOUTW）修改为0x50（EMR_SETDIBITSTODEVICE）

```

。

```
HDC hEmf = CreateEnhMetaFile( 0 , "1.emf" , NULL , NULL );
RECT rect;
rect.top = 0 ;
rect.left = 0 ;
rect.bottom = 20;
rect.right = 200;

char szStr[] = "WSAWSAW";
ExtTextOut( hEmf , 0 , 0 , ETO_OPAQUE , &rect , szStr , sizeof(szStr) , NULL );
CloseEnhMetaFile(hEmf);               
DeleteObject(hEmf);

```

![enter image description here](http://drops.javaweb.org/uploads/images/173a2cd643b9b02163227f94f7bad07b4f50b9f2.jpg)

由于我在Win7下，浏览存放EMF文件的目录并没有触发EMF文件的解析，因此通过mspaint.exe加载1.emf文件，执行到

```
int __thiscall MRSETDIBITSTODEVICE::bPlay(EMRSETDIBITSTODEVICE *this, HDC hdc, struct tagHANDLETABLE *a3, unsigned int a4)

```

函数时，可以看到ecx指向的数据与文件中的数据一致。

![enter image description here](http://drops.javaweb.org/uploads/images/4494341fc252960afad7a2664d7eb74daed3703c.jpg)

为了实现之前的猜想，实现越界写操作，假定在_((_DWORD *)v8 + 5) = v4->cbBitsSrc处实现了越界写，这就要求v4->cbBmiSrc小于（6_4）。

![enter image description here](http://drops.javaweb.org/uploads/images/3737cb0ed0f1d0b1e30fb046ad600797edd9acbd.jpg)

由于MRSETDIBITSTODEVICE::bCheckRecord实现了对EMRSETDIBITSTODEVICE结构的合法性检查。函数如下。

![enter image description here](http://drops.javaweb.org/uploads/images/cfa9854a042c519b18c98581675321ce7e9a7bb6.jpg)

根据检查的内容，对emf文件进行修改，使其满足MRSETDIBITSTODEVICE::bCheckRecord检查的各项条件，同时使v4->cbBmiSrc小于（6*4），最终得到如下文件内容。

![enter image description here](http://drops.javaweb.org/uploads/images/5926add8421afb99b237d152eead86dbe72735c2.jpg)

用mspaint.exe加载emf文件，通过windbg可以观察到所有的检查都被绕过，同时LocalAlloc分配的内存大小为2。

![enter image description here](http://drops.javaweb.org/uploads/images/d1e0c776c6d1cfb264e597ef9a6b5910b31112bd.jpg)

之后的_((_DWORD *)v8 + 2) = v9与_((_DWORD *)v8 + 5) = v4->cbBitsSrc都将实现缓冲区越界写入操作。

如果可以通过脚本在浏览器上显示emf文件，则有可能利用该漏洞实现远程代码执行。另外值得一提的是补丁中修补的其他如MF16_*的函数，这些函数的调用点都存在如下的代码段。这是对HDC的类型进行验证，只有类型是0x660000时，才会执行这些函数，而我只在调用CreateMetaFile后才得到了类型是0x660000的HDC，屏幕上显示时使用的HDC类型为0x10000。当HDC类型是0x660000时，调用PlayEnhMetaFile，最终不会执行PlayEnhMetaFileRecord。

![enter image description here](http://drops.javaweb.org/uploads/images/dac4ce55c60aace759f43e5f41d4c4681889a316.jpg)