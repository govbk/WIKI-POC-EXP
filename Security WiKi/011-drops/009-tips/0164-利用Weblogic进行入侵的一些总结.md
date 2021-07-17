# 利用Weblogic进行入侵的一些总结

本文主要总结一下在利用`Weblogic`进行渗透时的一些错误的解决方法以及一些信息的收集手段。

0x01 最常见的两种错误
=============

* * *

*   上传`war`时拒绝访问，如下图

![enter image description here](http://drops.javaweb.org/uploads/images/950ad8c2f136ccb82d0c651b347ba07c34ef4d59.jpg)

出现此种原因可能是因为管理对默认上传目录`upload`做了权限设置

用`burp`截取上传时的数据，修改upload为其他目录

![enter image description here](http://drops.javaweb.org/uploads/images/13a167d2d68c22ebb40597629e7d79342f16c95e.jpg)

*   上传后无法部署，出现**java.util.zip.ZipException:Could not find End Of Central Directory**，如下图（经过整理的错误信息）

![enter image description here](http://drops.javaweb.org/uploads/images/055832ae14150ef08654bedf5666af157d0e2258.jpg)

**原因分析**： 出现此种原因是因为上传的时候没有使用二进制模式，而是采用的`ASCII`模式，导致上传的文件全部乱码

这是采用`ASCII`模式上传之后再下载下来的文件，全部乱码

![enter image description here](http://drops.javaweb.org/uploads/images/f9b42ef9f58716e37eb04f273de33db9786a52a8.jpg)

而原本的文件应该是这个样子的

![enter image description here](http://drops.javaweb.org/uploads/images/2cc5c0470c2b62b73bb2325503247afd3011f948.jpg)

默认上传`war`的`content-type`为`application/octet-stream`或者`application/x-zip-compressed`（记不清了）

这两种模式本来应该为二进制上传模式的，但是却无缘无故变成了`ASCII`模式，原因未知（暂且认定为管理员的设置）

在二进制上传模式中，除了普通的程序，即`content-type`为`application`开头的，还有图片`image`开头

用`burp`抓取上传的数据`content-type`改成`image/gif`,还一定要加上文件头`GIF89a`,否则还是要出错，下图的那个`filename`为`key1.gif`仅为测试，实际上传还是以`war`结尾

![enter image description here](http://drops.javaweb.org/uploads/images/c59a2a6834192a41e6bdadf8c709fb2936dce277.jpg)

0x02 其他的信息收集
============

* * *

拿到`shell`之后先找配置文件，一般在`WEB-INF`目录下，有些在`WEB-INF/classes`目录下，文件名一般以`properties`结尾。

还有一种是`JDBC`在`Weblogic`里面配置好的，如下图

![enter image description here](http://drops.javaweb.org/uploads/images/68f30643a48fc816a68d92663763a78b78823824.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0b1e6bca35e86139be189daef1414d460f43b0d6.jpg)

这种的解密方式请参考[解密JBoss和Weblogic数据源连接字符串和控制台密码](http://drops.wooyun.org/tips/349)

`Weblogic`还提供虚拟主机的功能，通过这个，可以收集到一些域名的信息，所属单位等，以便进一步通知处理。

![enter image description here](http://drops.javaweb.org/uploads/images/510e84fe811db13041d2908d106614f419cf764a.jpg)

0x03 进内网
========

* * *

由于`Weblogic`权限比较大，在`Windows`一般都是`administrator`，`Linux`则是`weblogic`用户，也有`root`权限的。

所以拿到`shell`之后，先看看能否访问外网，以便转发内网，进行更深的渗透,一条ping命令即可,若不能访问外网，可以尝试下面这个方法

[http://wooyun.org/bugs/wooyun-2015-0127056](http://wooyun.org/bugs/wooyun-2015-0127056)

以上只是鄙人的个人见解，望各路大神指正