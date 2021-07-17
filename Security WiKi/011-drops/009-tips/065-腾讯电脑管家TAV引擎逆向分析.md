# 腾讯电脑管家TAV引擎逆向分析

0x00 背景
=======

* * *

about me：写过外挂，做过破解，对电脑管家也有比较长时间的逆向分析积累，现在整理下投出来，求邀请码和WB。

TAV有自己的优势和特点的，比如杀毒之后能够还原一部分被病毒破坏的注册表和文件。另外它的内存查杀也不错，可以扫描内存、创建和病毒一样的互斥，防止病毒再次运行。

TAV相比其他杀毒软件还是有很多不足，最明显的缺陷是免杀比较简单，由于TAV引擎用的是字符串明文检测，很容易通过分析病毒库或者是MYCCL等进行黑盒免杀。另一方面，TAV的效率比较低，包括特征数据结构弱, 特征复用等方面的问题，后面会有详细分析。

值得一说的是，逆向TAV的特征库可以看到，外挂特征比病毒、后门特征都多，排在了特征数量的第二名，说腾讯电脑管家是“外挂杀手”一点都不夸张。盗号木马则是TAV另一个重点打击的对象，在特征库占比也不低。至于感染型病毒、后门、下载者、蠕虫、恶意脚本等其它类型的木马病毒，还需要OEM的小红伞引擎或者云引擎来补位，否则单靠TAV肯定是无能为力的。

0x01 结构与功能初析
============

* * *

引擎结构和功能如下。不难看出，TAV引擎属于基础的传统特征引擎。特征数量较少，与主流杀软相比还处于初级阶段。

![](http://drops.javaweb.org/uploads/images/de4f76d585751db228ffba88f47015de215861c5.jpg)

1. 引擎内部功能一览
-----------

* * *

### 内存扫描

匹配指定的进程和内存串，如果匹配到就终止进程

![](http://drops.javaweb.org/uploads/images/3d913024bd110937f972d04c4461ba007cff0e9f.jpg)

### 匹配文件是否存在

![](http://drops.javaweb.org/uploads/images/5a47904b94df9751ef058f2588865f5185a10eb2.jpg)

### 创建一个和病毒相同的互斥体，防止病毒再次运行

![](http://drops.javaweb.org/uploads/images/15ac156d0a9b57be904d4df64bbb4dd8f739326a.jpg)

### 内存清理

![](http://drops.javaweb.org/uploads/images/a7e21ad16afcc7e22378f1a938af32db07b46a87.jpg)

### 解包

![](http://drops.javaweb.org/uploads/images/638c53dd4979f1bc13c940fe888e1bc4318395fe.jpg)

### 字符串多模式匹配

![](http://drops.javaweb.org/uploads/images/d761c0c2ffa55c41d0d802851cf0d86b57aca531.jpg) 

### 虚拟机:

![](http://drops.javaweb.org/uploads/images/3ee2fd3e078421e4a147a957da6d1aad76ae86e4.jpg)

模拟了ntdll、kernel32、gdi32、user32、advapi32、shell32、wsock32、ole32、oleaut32、msvcrt、version、urlmon这几个系统DLL

对于不常用的API采用同一个函数统一处理：![](http://drops.javaweb.org/uploads/images/2f7f270f35e0fea0b1e1d66f9aa754c536c80e0e.jpg)

对于关键函数，使用单独的模拟代码实现：![](http://drops.javaweb.org/uploads/images/bb74319b5b81a3fb0a9f9f1cdcb9064164c58a08.jpg)

2. 病毒库分析：
---------

* * *

### A).病毒库算法:

只是简单的ZLIB。

![](http://drops.javaweb.org/uploads/images/b4614ca444f270c23aa0e145777332d703dcc8f7.jpg)

解密后内容如下：

![](http://drops.javaweb.org/uploads/images/ba13e02f5c61feb6273e0494ed0dcf80d552fb14.jpg)

### B). 病毒库结构:

virinfo.def：名称表，包括壳名、包名、特征名`c++ structVirInfo { DWORD dwID; BYTE btLength; char VirName[btLength]; };`

### C). 病毒库规模:

特征数量整体非常少，以PE为例只有8135条特征。分布见下图。从特征分布和类型来看，TAV主要查杀目标为外挂、盗号程序。对于动辄百万级规模的恶意程序家族其实只覆盖了冰山一角，远远达不到一个杀毒引擎的程度，仅仅停留在外挂、盗号专杀的层面。更让人捉急的是TAV维护了大量的脱壳解包特征，直接暴露了开发者框架设计方面的缺陷。与此形成鲜明对比的是国际知名的卡巴和BD引擎，通常在一个“膨胀”的过程中，维护较多的同家族特征，随后再在“收缩”过程中，用一条obj通杀，显得章法自如、张弛有度。

![](http://drops.javaweb.org/uploads/images/8265d9fd627110c068a7e36098cd592cf4576d57.jpg)

### D). 病毒库更新：

病毒库的更新有2种方式：

1 直接更新扩展名为.def的病毒库，适用于查杀现有引擎可以支持的木马和病毒。

2 更新替换tpktt.dll，适用于现有引擎无法解决的复杂样本，将特征和查杀方法通过分析员写代码实现，然后整个引擎更新替换，类似于专杀方式。

0x02 PE查杀过程逆向分析：
================

* * *

1.病毒库描述：
--------

* * *

virpeXX.def：（PE库）

```
struct VirpeHeader
{
　WORD wUnknown;
　DWORD dwHeadSize;
　DWORD dwSize;
　WORD wTable1Count;
    WORD wdMaskCount;//表示共有多少条PE特征
    WORD wdUnknown4;
    DWORD dwTable1Off;
    DWORD dwTable2Off;
    DWORD dwTable3Off;
    DWORD dwTable4Off;
    DWORD dwTable5Off;//传统特征
    DWORD dwTable6Off //多模式特征
};

```

* * *

```
struct Sig //特征结构
{
    DWORD dwRecordID;//特征ID，用于关联特征名
    DWORD dwOffset;//特征偏移，用于定位病毒代码具体位置
    BYTE btLength;//特征长度，用于扫描匹配病毒代码长度
    BYTE btOffsetBaseAddress;//特征基地址，用于定位特征起始位置
BYTE btVirMask[btLength];//病毒特征具体内容
};

```

2. 静态查杀方式：
----------

* * *

### a). 二进制全文匹配。（二进制特征存放在virpe01.def库解密后的tbl5中）

将数十字节的病毒代码二进制，记录在病毒库中，与待检测样本进行全文匹配。

### b). 多模匹配。（多模特征存放在tbl6中）

将恶意程序的明显字符串信息提取出，记录在病毒库中，与待检测样本进行多模匹配。

3. 静态扫描流程：
----------

* * *

见下图![](http://drops.javaweb.org/uploads/images/e1ec25972434166a6d3fa1ad589adf64a2dd98ec.jpg)

4. 设计缺陷分析：
----------

* * *

传统杀软最容易出现的几个问题：效率低、体积庞大、对抗门槛低。这几个问题在TAV身上尤为明显。只是现阶段TAV特征数量极低，暂时未大规模展现而已。

### a) 体积大。

现有的查杀方式设计会导致病毒库臃肿，庞大的二进制数据和字符串数据记录在病毒库中，随着特征增加，病毒库体积会急速膨胀。在同等特征数量的情况下，TAV病毒库将会比卡巴、BD等杀软大上数十倍。

### b) 效率低。

逐个匹配特征的方式，会随着病毒库膨胀而使得效率变得越来越低。卡巴、BD等杀软为解决此问题，设计出了多索引的方式，只有在最后一层才匹配几个特征，效率非常高。

### c) 对抗门槛低。

匹配代码在内存中明文存在。

![](http://drops.javaweb.org/uploads/images/540bf139bd6b5b3cf217c6d2a748c7ecf3e0533e.jpg)

使得无论木马作者通过分析病毒库来免杀还是通过MYCCL等黑客工具进行黑盒免杀都极为容易。

### d) 特征无复用。

下图为TAV的TOP50特征，可见出现大量重复二进制。特征之间基本无复用。

![](http://drops.javaweb.org/uploads/images/c2dc2305df1d671527a339eb61bf96c4437e17dd.jpg)

**例：Virus.Win32.DiskGen**

以此家族为例，描述TAV设计缺陷导致的效率问题。

TAV查杀Virus.Win32.DiskGen病毒从a变种到最后的an变种，多次匹配了这条特征：

```
18 8B 8E 30 0A 00 00 03 C8 40 40 8A 11 F6 D2 88 11 3B 05 3F 3F 3F 3F 7C

```

![](http://drops.javaweb.org/uploads/images/eb069af4f5f85007b2f48cf09da53ba5e039a458.jpg)

特征含义是病毒自解密代码

![](http://drops.javaweb.org/uploads/images/0062f7ec3a73dc5fe15f2b5fe59a06d4146e410a.jpg)

尽管使用了索引复用，但并没有优化。从病毒库中可以看到，这条相同的特征出现了20次。也就意味着，为了匹配这个家族的所有变种，当前待扫描文件需要扫描20次才行。因为目前TAV特征只有数千条，效率低下的问题感受不明显，倘若哪天TAV特征达到竞品平均水平的数百万条，不难想象扫描一个文件将会是何等的慢。

0x03 其他类型分析：
============

* * *

virscrXX.def：脚本库，直接存储的字符串，用于挂马的查杀。为了避免误报自身内存，采用了异或的方式，将特征加载到内存中。

![](http://drops.javaweb.org/uploads/images/72067e28eb81beb60c7e3d5cf69110aeec53303e.jpg)

virdexXX.def：安卓特征库

![](http://drops.javaweb.org/uploads/images/565780270bfe0dc98b7d2af05f06e537fe635cf9.jpg)

virsrcXX.def：脚本库，用于查杀HTML\JAVA\PDF\OLE\JS\NSIS

![](http://drops.javaweb.org/uploads/images/029e6f703dc758503427b38326f3f830cfe62bd7.jpg)

vircmpinfo.def：壳、编译器识别

![](http://drops.javaweb.org/uploads/images/d1e5b162c21746f49db555b459a30c5003438be0.jpg)

![](http://drops.javaweb.org/uploads/images/5a62adc855873fb26466a2c5df814f1319dec1c4.jpg)

0x04 实战对抗
=========

* * *

1.TAV虚拟机对抗
----------

* * *

当文件被加UPX壳后，会调用GetProcAddress动态获得API地址，TAV可以模拟GetProcAddress的结果，并且可以执行到下一条EIP所在位置，使得程序能够正常模拟下去，而不至于触发异常返回。

![](http://drops.javaweb.org/uploads/images/e7fb299a5c16523e934a31f972e004feacf13631.jpg)

文件的真实调试结果：

![](http://drops.javaweb.org/uploads/images/24982f57c624fca5d3e8697d95578ac0684d5049.jpg)

不过TAV的虚拟执行能力比较弱，比较适用于对压缩壳进行脱壳，如常见的UPX壳，而对于动态行为查杀却无能为力。

比如某个非常简单的Downloader木马，作者调用了URLDownloadToFileW下载一个木马，然后调用WinExec执行木马。整个过程非常简单，只用到2个Windows API，并且没有额外的代码来对抗虚拟机，而TAV引擎却无法查杀：

![](http://drops.javaweb.org/uploads/images/5d14b2803fa87942367b0495dfcc2db2aa5d145d.jpg)

![](http://drops.javaweb.org/uploads/images/60f37bfe79500817f8f5d0ca1e3dfc6885e0dd32.jpg)

![](http://drops.javaweb.org/uploads/images/299c78c8c49aee9bd3b11aac380c916f57ec086c.jpg)

同样的样本，扫描对比国外知名杀软，则可以通过虚拟机动态检出

![](http://drops.javaweb.org/uploads/images/a52fcf4ed5b5e6798fd4a5596ed0a6cb15050027.jpg)

2.MYCCL黑盒对抗：
------------

* * *

以某盗QQ木马测试。

![](http://drops.javaweb.org/uploads/images/37fbcc2e7d93c8afe37305e495ffbfd1bc47fd1f.jpg)

特征码地址如下：

![](http://drops.javaweb.org/uploads/images/4593316983633c9c400073902a3bab73bc545cf1.jpg)

使用C32ASM查看特征码：

![](http://drops.javaweb.org/uploads/images/fd968177ac35af362c63c3378a147a5d5afc294a.jpg)

随便改改：

![](http://drops.javaweb.org/uploads/images/bb53fc93ca70f2c2af8d8e3b7ede3fdaf2ff7418.jpg)