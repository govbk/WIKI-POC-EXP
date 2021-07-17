# XSS姿势——文件上传XSS

原文链接：[http://brutelogic.com.br/blog/](http://brutelogic.com.br/blog/)

0x01 简单介绍
=========

* * *

一个文件上传点是执行XSS应用程序的绝佳机会。很多网站都有用户权限上传个人资料图片的上传点，你有很多机会找到相关漏洞。如果碰巧是一个self XSS，你可以看看这篇文章。

0x02 实例分析
=========

* * *

首先基本上我们都可以找到类似下面的一个攻击入口点，我觉得这个并不难。

### 姿势一：文件名方式

文件名本身可能会反映在页面所以一个带有XSS命名的文件便可以起到攻击作用。

![p1](http://drops.javaweb.org/uploads/images/efdf0dd13e8defd2facb0aa4c02d991ebfc1cf6d.jpg)

虽然我没有准备靶场，但是你可以选择在[W3Schools](http://www.w3schools.com/jsref/tryit.asp?filename=tryjsref_fileupload_value)练习这种XSS 。

### 姿势二：Metadata

使用[exiftool](http://www.sno.phy.queensu.ca/~phil/exiftool/)这个工具可以通过改变EXIF  metadata进而一定几率引起某处反射：

```
$ exiftool -field = XSS FILE

```

例如：

```
$ exiftool -Artist=’ “><img src=1 onerror=alert(document.domain)>’ brute.jpeg

```

![p2](http://drops.javaweb.org/uploads/images/3fc86e67859d6541c30c25af07de48c8a3ab5ffa.jpg)

### 姿势三：Content

如果应用允许上传SVG格式的文件（其实就是一个图像类型的），那么带有以下content的文件可以被用来触发XSS：

```
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>

```

一个 PoC用来验证。你可以通过访问brutelogic.com.br/poc.svg看到效果

### 姿势四：Source

建立一个携带有JavaScript payload的GIF图像用作一个脚本的源。这对绕过CSP（内容安全策略）保护“script-src ‘self’”（即不允许使用示例的这种xss方式进行攻击`<script>alert(1)</script>`）是很有用的，但前提是我们能够成功地在相同的域注入，如下所示。

![p3](http://drops.javaweb.org/uploads/images/5c262757d15d923ce2c3428b97aeae6dd63c859f.jpg)

要创建这样的图像需要这个作为content 和 name，并使用.gif扩展名：

```
GIF89a/*<svg/onload=alert(1)>*/=alert(document.domain)//;

```

这个GIF的图片头——GIF89a，作为alert function的变量分配给alert function。但是他们之间，还有一个被标注的XSS变量用来防止图片被恢复为text/HTML MIME文件类型，因此只需发送一个对这个文件的请求payload 就可以被执行。

正如我们下面看到的，文件类unix命令和PHP函数中的exif_imagetype（）和getimagesize（）会将其识别为一个GIF文件。所以如果一个应用程序仅仅是使用这些方式验证是否是一个图像，那么该文件将可以上传成功（但可能在上传后被杀掉）。

![p4](http://drops.javaweb.org/uploads/images/8b723d6907c1bed14c38a607127044b04f47cf6a.jpg)

0x03 最后
=======

* * *

如果你想知道更多的有其标志性ASCII字符可以用于一个javascript变量赋值的文件类型，看我随后的文章。

也有很多比较详细的使用XSS和图像文件相结合绕过图形处理函数库过滤的例子。这方面的一个很好的例子是[here](https://github.com/d0lph1n98/Defeating-PHP-GD-imagecreatefromgif)