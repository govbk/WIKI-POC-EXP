# php imagecreatefrom* 系列函数之 png

0x00 简介
=======

* * *

这篇文章主要分析 php 使用 GD 库的 imagecreatefrompng() 函数重建 png 图片可能导致的本地文件包含漏洞。

当系统存在文件包含的点，能包含图片文件; 另外系统存在图片上传，上传的图片使用 imagecreatefrompng() 函数重建图片并保存在本地，则很可能出现文件包含的漏洞。

通常，系统在实现图片上传功能时，为了防范用户上传含有恶意 php 代码的图片，可采用 gd 库重建图片，gd 库重建图片的一系列函数 imagecreatefrom*，会检查图片规范，验证图片合法性，以此抵御图片中含有恶意 php 代码的攻击。

那么， imagecreatefrom* 系列函数是否能完全抵御图片中插入 php 代码的攻击呢，本文以 imagecreatefrompng() 函数作为研究对象，探讨实现重建 png 格式的图片中包含恶意 php 代码的可能性，以及所需要满足的条件。

png 文件格式， imagecreatefrompng 函数解析， 修改图片， 上传， 文件包含 ...

0x01 png 图片格式
=============

要实现重建的 png 图片中仍包含有恶意的 php 代码， 首先要对 png 图片格式有基本的了解。png 支持三种图像类型：索引彩色图像(index-color images)，灰度图像(grayscale images)，真彩色图像(true-color images), 其中索引彩色图像也称为基于调色板图像(Palette-based images)。

标准的 png 文件结构由一个 png 标识头连接多个 png 数据块组成，如：`png signature | png chunk | png chunk | ... | png chunk`.

png 标识
------

png 标识作为 png 图片的头部，为固定的 8 字节，如下

```
89 50 4E 47 OD 0A 1A 0A

```

png 数据块
-------

png 定义了两种类型的数据块，一种是称为关键数据块(critical chunk)，标准的数据块; 另一种叫做辅助数据块(ancillary chunks)，可选的数据块。关键数据块定义了3个标准数据块，每个 png 文件都必须包含它们。3个标准数据块为:`IHDR， IDAT， IEND`.

这里介绍4个数据块：`IHDR， PLTE， IDAT， IEND`

**png 数据块结构**

png 文件中，每个数据块由4个部分组成`length | type(name) | data | CRC`, 说明如下

```
length: 4 bytes， just length of the data, not include type and CRC  
type: 4 bytes, ASCII letters([A-Z,a-z])
CRC: 4bytes

```

CRC(cyclic redundancy check)域中的值是对Chunk Type Code域和Chunk Data域中的数据进行计算得到的。CRC具体算法定义在ISO 3309和ITU-T V.42中，其值按下面的CRC码生成多项式进行计算： x32+x26+x23+x22+x16+x12+x11+x10+x8+x7+x5+x4+x2+x+1

*   IHDR

文件头数据块IHDR(header chunk)：它包含有PNG文件中存储的图像数据的基本信息，并要作为第一个数据块出现在PNG数据流中，而且一个PNG数据流中只能有一个文件头数据块。

文件头数据块由13字节组成，它的如下所示

| 域的名称 | 字节数 | 说明 |
| --- | :-: | --- |
| Width | 4 bytes | 图像宽度，以像素为单位 |
| Height | 4 bytes | 图像高度，以像素为单位 |
| Bit depth | 1 byte | 图像深度.  
索引彩色图像： 1，2，4或8  
灰度图像： 1，2，4，8或16  
真彩色图像： 8或16 |
| ColorType | 1 byte | 颜色类型.  
0：灰度图像, 1，2，4，8或16  
2：真彩色图像，8或16  
3：索引彩色图像，1，2，4或8  
4：带α通道数据的灰度图像，8或16  
6：带α通道数据的真彩色图像，8或16 |
| Compression method | 1 byte | 压缩方法(LZ77派生算法) |
| Filter method | 1 byte | 滤波器方法 |
| Interlace method | 1 byte | 隔行扫描方法.  
0：非隔行扫描  
1： Adam7(由Adam M. Costello开发的7遍隔行扫描方法) |

*   PLTE

调色板数据块PLTE(palette chunk)包含有与索引彩色图像(indexed-color image)相关的彩色变换数据，它仅与索引彩色图像有关，而且要放在图像数据块(image data chunk)之前。

PLTE数据块是定义图像的调色板信息，PLTE可以包含1~256个调色板信息，每一个调色板信息由3个字节组成：

| 颜色 | 字节 | 意义 |
| --- | :-: | --- |
| Red | 1 byte | 0 = 黑色, 255 = 红 |
| Green | 1 byte | 0 = 黑色, 255 = 绿色 |
| Blue | 1 byte | 0 = 黑色, 255 = 蓝色 |

因此，调色板的长度应该是3的倍数，否则，这将是一个非法的调色板。`颜色数 = length/3`

对于索引图像，调色板信息是必须的，调色板的颜色索引从0开始编号，然后是1、2……，调色板的颜色数不能超过色深中规定的颜色数（如图像色深为4的时候，调色板中的颜色数不可以超过2^4=16），否则，这将导致PNG图像不合法。

*   IDAT

图像数据块IDAT(image data chunk)：它存储实际的数据，在数据流中可包含多个连续顺序的图像数据块。IDAT存放着图像真正的数据信息

*   IEND

图像结束数据IEND(image trailer chunk)：它用来标记PNG文件或者数据流已经结束，并且必须要放在文件的尾部。

正常情况下， png 文件的结尾为如下12个字符：

```
00 00 00 00 49 45 4E 44 AE 42 60 82

```

由于数据块结构的定义，IEND数据块的长度总是0（00 00 00 00，除非人为加入信息），数据标识总是IEND（49 45 4E 44），因此，CRC码也总是AE 42 60 82

0x02 php imagecreatefrompng() 函数
================================

* * *

有了对 png 图片格式的基本了解，可以帮助我们更好的理解 imagecreatefrompng() 函数的底层实现。分析 php 源码(php 5.6.20)可知， php imagecreatefrompng() 函数实现重建图片，核心是 gd 库的 gdImageCreateFromPngCtx() 函数。

分析 gd 库中的 gdImageCreateFromPngCtx() 函数可知，函数首先会检测 png signature, 不合法则返回NULL。然后会读原始的 png 图片文件给 png_ptr, 再从 png_ptr 中读图片信息到 info_ptr，再之后就是获取 IHDR 信息，读 IDAT 数据等，这里不一一讨论。这里仅讨论 png_read_info() 函数中对读 PLTE 数据库的验证处理。

```
gd_png.c/gdImageCreateFromPngCtx
{
...
if (png_sig_cmp(sig, 0, 8) != 0) { /* bad signature */
        return NULL;        /* bad signature */
}   

... 

png_set_read_fn (png_ptr, (void *) infile, gdPngReadData);
png_read_info (png_ptr, info_ptr);  /* read all PNG info up to image data */
...
}

```

要了解 png_read_info() 的内部实现，可以通过读 libpng 的源码(libpng 1.6.21)进行了解。当图片类型是索引图像时，png_read_info() 读到 PLTE chunk 时会调用 png_handle_PLTE 函数进行 CRC 校验

```
pngread.c/png_read_info
{
...
else if (chunk_name == png_PLTE)
         png_handle_PLTE(png_ptr, info_ptr, length);
...
}   

pngrutil.c/png_handle_PLTE 
{
...
#ifndef PNG_READ_OPT_PLTE_SUPPORTED
   if (png_ptr->color_type == PNG_COLOR_TYPE_PALETTE)
#endif
   {
      png_crc_finish(png_ptr, (int) length - num * 3);
   }
...
}

```

分析底层源码可知， png signature 是不可能插入 php 代码的； IHDR 存储的是 png 的图片信息，有固定的长度和格式，程序会提取图片信息数据进行验证，很难插入 php 代码；而 PLTE 主要进行了 CRC 校验和颜色数合法性校验等简单的校验，那么很可能在 data 域插入 php 代码。

从对 PLTE chunk 验证的分析可知， 当原始图片格式给索引图片时，PLTE 数据块在满足 png 格式规范的情况下，程序还会进行 CRC 校验。因此，要将 PHP 代码写入 PLTE 数据块，不仅要修改 data 域的内容为php代码，然后修改 CRC 为正确的 CRC 校验值，当要填充的代码过长时，可以改变 length 域的数值，满足 length 为3的倍数， 且颜色数不超过色深中规定的颜色数。例如: IHDR 数据块中 Bit depth 为 08, 则最大的颜色数为 2^8=256, 那么 PLTE 数据块 data 的长度不超过 3*256=0x300。 这个长度对写入 php 一句话木马或者创建后门文件足够了。

那么是不是所有 png 图片都可以在 PLTE 数据块插入 php 代码呢？下面通过实验予以说明。

0x03 实验验证
=========

* * *

png 支持索引彩色图像(index-color images)，灰度图像(grayscale images)，真彩色图像(true-color images)三种类型的图片，而 PLTE 数据块是索引图像所必须的，因此索引图像极有可能在 PLTE 数据块插入 php 代码。

下面摘录 gd 库中 gdImageCreateFromPng() 函数的一段说明

```
If the PNG image being loaded is a truecolor image, the resulting
gdImagePtr will refer to a truecolor image. If the PNG image being
loaded is a palette or grayscale image, the resulting gdImagePtr
will refer to a palette image.

```

函数将索引彩色图像和灰度图像转换为索引彩色图像， 将真彩色图像转换为真彩色图像。下面分别转换这三种类型的图片，测试图片地址:[图片](https://github.com/hxer/imagecreatefrom-/tree/master/png/analysis). php代码如下

```
<?php
$pngfile = 'test.png';
$newpngfile = 'new.png';
$im = imagecreatefrompng($pngfile);
imagepng($im,$newpngfile);
?>

```

*   索引图像

![索引图像](http://drops.javaweb.org/uploads/images/d18d6517778d4132c94e7f68bfdf62ecdbd07588.jpg)

读 IHDR 数据块信息，色深为8bits, color type=0x03, 为索引图像类型，改变其 PLTE 数据块如下，修改数据为`<?php phpinfo();?>`

![修改数据为php代码](http://drops.javaweb.org/uploads/images/ff0f89164faf6be94251df4b137350645581f26f.jpg)

计算 CRC 过程如下

![计算 CRC ](http://drops.javaweb.org/uploads/images/0362269cc9a4eb83e9844c935e173d19ba17a4f1.jpg)

imagecreatefrompng() 重建的图片如下

![new png ](http://drops.javaweb.org/uploads/images/8f22849d958e9a069e619c1c88a4e197cd14dc35.jpg)

可以看出重建的图片中 PLTE 数据块保留了 php 代码，重建也增加了 pHYs 数据块，对我们所关心的结果并没有影响。说明插入 php 代码成功。

*   灰度图像

原始图像， 不含 PLTE 数据块， 如下所示

![灰度图像](http://drops.javaweb.org/uploads/images/cf31c374c06838fe0365b6db0d8b1ae77c223278.jpg)

插入 PLTE 数据块，并写入 php 代码

![add PLTE chunk](http://drops.javaweb.org/uploads/images/604268b0e0bdde346cc554b9f2bb8b24813db712.jpg)

重建后的图片如下

![new png](http://drops.javaweb.org/uploads/images/e4ea77b8b0114cb5f8469dc4da2108361a4bd501.jpg)

可以看出重建的图片转换为 索引图像类型，并且重写了 PLTE 数据块，写入 php 代码失败

*   真彩色图像

原始图像， 不含 PLTE 数据块， 如下所示

![真彩色图像](http://drops.javaweb.org/uploads/images/4d5ba3e034019fb485bd3c41f36f15e9de341935.jpg)

插入 PLTE 数据块，并写入 php 代码

![add PLTE chunk ](http://drops.javaweb.org/uploads/images/dd0b91147b0a3237d83dfe98fe46306cd263b1f8.jpg)

重建后的图片如下

![new png](http://drops.javaweb.org/uploads/images/64679f2a9b0c33f9d6ff62d9902bc4a81bb3866a.jpg)

可以看出真彩色类型图片重建后的图片不含 PLTE 数据块，写入 php 代码失败

0x04 总结
=======

* * *

通过以上分析和实验可知, imagecreatefrompng() 函数并不能完全防止图片中插入 php 代码， 当图片类型为索引图像时， 在 PLTE chunk 可以成功插入 php 代码， 而另外其他类型的图片并不能实现 PLTE chunk 中插入 php 代码。最后， 一并感谢下面参考资料对我研究的帮助。

附，修改索引图像插入 php 代码的地址[github](https://github.com/hxer/imagecreatefrom-/blob/master/png/poc/poc_png.py)

所附代码实现了当 payload 长度大于 PLTE 数据长度时， 会重写 PLTE 数据块。然而 在实验过程中发现，imagecreatepng()函数重建的图片 PLTE 数据块的长度仍为原始的长度，即并不能随意扩充 PLTE 数据块的长度，具体原因还需深入分析源码， 也就是说要加载的 payload 不能超过 PLTE 数据块所给的长度。

通常情况下， PLTE 数据块所给的长度可以满足我们插入基本的 php 后门代码，存在了那么一个点，是不是可以撬动地球了呢

当然本文还有许多不足之处，望大家批评指正

0x05 资料参考
=========

* * *

1.[github libgd](https://github.com/libgd/libgd)

2.[gd2.0.33 manual](https://boutell.com/gd/manual2.0.33.html)

3.[libgd home](http://libgd.github.io/)

4.[png book](http://www.libpng.org/pub/png/book/toc.html)

5.[png chunk](http://www.libpng.org/pub/png/spec/1.2/PNG-Chunks.html)

6.[png 文件格式解析](http://blog.csdn.net/bisword/article/details/2777121)