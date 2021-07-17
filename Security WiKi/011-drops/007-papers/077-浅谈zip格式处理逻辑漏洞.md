# 浅谈zip格式处理逻辑漏洞

**前言：**`zip`压缩格式应用广泛，各个平台都有使用，`Windows`平台使用来压缩文件，`Android`平台使用来作为`apk`文件的格式。由于`zip`文件格式比较复杂，在解析`zip`文件格式时，如果处理不当，可能导致一些有意思的逻辑漏洞，本篇文章将挑选有意思的漏洞进行解析。

一、文件扩展名欺骗漏洞
===========

* * *

很早之前，国外安全研究人员[爆料Winrar 4.x版本存在文件扩展名欺骗漏洞](http://www.exploit-db.com/papers/32480/)，黑客可以通过该漏洞诱骗受害者执行恶意程序。该漏洞的主要原理是：`Winrar`在文件预览和解压缩显示文件名使用的是不同结构体的字段导致的。

### 1.1 zip格式文件的结构

在了解漏洞的原理前，先熟悉下zip格式的文件结构。

如果一个压缩包文件里有多个文件，可以认为每个文件都是被单独压缩，然后再拼成一起。

一个`ZIP`文件由三个部分组成：压缩源文件数据区+压缩源文件目录区+压缩源文件目录结束标志，如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/3b22cb5743e0cd42183bdf2041ae73706531e76b.jpg)

1）文件头（压缩源文件目录区）在文件末尾，即图1中的`File Header`，记录了索引段的偏移、大小等等。

2）数据段（压缩源文件数据区）在文件开头，即图1中的`Local Header`，记录了数据的一些基本信息，可以用来跟`File Header`中记录的数据进行比较，保证数据的完整性。

3）`Local Header`还包含了文件被压缩之后的存储区，即图1中的`Data`区域。

4）图2和图3为`Local Header`（图2中的`ZIPFILERECORD`）和`File Header`（图3中的`ZIPDIRENTRY`）的数据对比，两者数据是一致的。

![enter image description here](http://drops.javaweb.org/uploads/images/f09e995c067b476a85fda41c9829bbc7823d4a59.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/29566e6c49309ee94dbd45ac43b9eff646c371bb.jpg)

### 1.2 漏洞产生原因

`Winrar`在文件预览的时候使用的是`ZIPDIRENTRY`下面的`deFileName`字段来显示文件名，解压缩的时候使用的是`ZIPFILERECORD`下面的`frFileName`字段来显示文件名。如果将`deFileName`字段文件扩展名改成`jpg`、`gif`等图片的文件扩展名，可以欺骗用户运行恶意程序。

`Winrar`文件预览示意图：

![enter image description here](http://drops.javaweb.org/uploads/images/cac2e0f33cfaad8a1c849881279f22716582f7ae.jpg)

用户看到的是`jpg`图片，打开的确实`exe`文件，真坑啊！

`Winrar`解压缩文件示意图：

![enter image description here](http://drops.javaweb.org/uploads/images/5f27ab7e238fb32ef99e6fcd6be367cb7750864e.jpg)

解压缩之后显示的`exe`，两处显示的不一样。

二、Android Master Key漏洞
======================

* * *

之前，国外安全研究人员爆出[第三个Android Master Key漏洞](http://www.saurik.com/id/19)，该漏洞的主要原理是：`android`在解析`Zip`包时，没有校验`ZipEntry`和`Header`中的`FileNameLength`是否一致。

### 2.1 zip文件格式的结构

在了解漏洞的原理前，还是先熟悉下`zip`格式的文件结构。

如果一个压缩包文件里有多个文件，可以认为每个文件都是被单独压缩，然后再拼成一起。

一个`ZIP`文件由三个部分组成：压缩源文件数据区+压缩源文件目录区+压缩源文件目录结束标志，如图1所示：

1）文件头（压缩源文件目录区）在文件末尾，即图1中的`File Header`，记录了索引段的偏移、大小等等。

2）数据段（压缩源文件数据区）在文件开头，即图1中的`Local Header`，记录了数据的一些基本信息，可以用来跟`File Header`中记录的数据进行比较，保证数据的完整性。

3）`Local Header`还包含了文件被压缩之后的存储区，即图1中的`Data`区域。

4）图2和图3为`Local Header`（图2中的`ZIPFILERECORD`）和`File Header`（图3中的`ZIPDIRENTRY`）的数据对比，两者数据是一致的。

![enter image description here](http://drops.javaweb.org/uploads/images/8736bfd58c3b55cb11573fc61cf3e550adfc28f0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8de9174f32aeb49bca0176de1497af112c74b97f.jpg)

### 2.2 漏洞产生原因

先来看一下是如何定位到`Local Header`中的`Data`数据：

```
off64_t dataOffset = localHdrOffset + 
                     kLFHLen + 
                     get2LE(lfhBuf + kLFHNameLen) +

```

`Data`的偏移是通过`Header`的起始偏移+`Header`的大小（固定值）+`Extra data`的大小+文件名的大小，如下图

![enter image description here](http://drops.javaweb.org/uploads/images/cb0bf69845d1db49f2817f50a23d64a9e836a961.jpg)

回头看一下，`java`在获取`Data`偏移的处理，在读取`Extra data`的长度的时候，它已经预存了文件名在`FileHeader`中的长度。

```
// We don't know the entry data's start position. 
// All we have is the position of the entry's local 
// header. At position 28 we find the length of the 
// extra data. In some cases this length differs 
// from the one coming in the central header. 

RAFStream rafstrm = new RAFStream(raf, 
         entry.mLocalHeaderRelOffset + 28); 
DataInputStream is = new DataInputStream(rafstrm); 
int localExtraLenOrWhatever = 

```

漏洞就在这里产生了，如果`Local Header`中的`FileNameLength`被设成一个大数，并且`FileName`的数据包含原来的数据，`File Header`中的`FileNameLength`长度不变，那么底层`C++`运行和上层`Java`运行就是不一样的流程。

```
C++ Header 64k Name Data 
+--------> +----------------------> +----------> 
length=64k classes.dex dex\035\A... dex\035\B... 
+--------> +---------> +----------> 

```

如上面所示，底层`C++`的执行会读取64k的`FileName`长度，而`Java`层由于是读取`File Header`中的数据，`FileName`的长度依旧是11，于是`Java`层校验签名通过，底层执行会执行恶意代码。