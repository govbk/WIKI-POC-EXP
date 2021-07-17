# 黑产godlike攻击: 邮箱 XSS 窃取 appleID 的案例分析

最近黑产利用腾讯邮箱的漏洞组合，开始频繁的针对腾讯用户实施攻击。

其利用的页面都起名为godlike.html，所以我们把这起攻击事件命名为godlike。

主要被利用的漏洞有3个, 一个 URL 跳转, 一个 CSRF, 另外一个就是 XSS

0x00
====

* * *

早上的时候被同学叫起来看一个链接

![](http://drops.javaweb.org/uploads/images/9169493c000c01d74fe8c9ed66693bffbb2d0039.jpg)

第一眼看到这个以为是张图片, 欺骗性很高, 不过因为当时嫌麻烦没有点进去

后来在电脑上发现是一个链接而不是图片才感到有问题, 这里的锅主要是腾讯的一个 URL 跳转了.

0x01 URL 跳转恶意构造指向 title
=======================

* * *

这里的这个 URL 跳转很猥琐

> http://jump.qt.qq.com/php/jump/check_url/?url=http://www.qmaild.xyz

可以看到被指向的 url 是 www.qmaild.xyz。

而这个 www.qmaild.xyz 把 title 设置成了这样

![](http://drops.javaweb.org/uploads/images/639d4221cc486edfb5d080f62a2feb67e33bbac0.jpg)

所以在手机里会有产生极为类似 img 文件的效果, 如果加上类似 『这个妹子好正』,之类的相信上钩的几率会更加高, 附一张手机 QQ 发送正常图片的截图

![](http://drops.javaweb.org/uploads/images/d66d202a4d2bcd431904307e64ec039712c3fc08.jpg)

0x02 CSRF 自动请求 XSS 页面
=====================

* * *

跳转到 www.qmaild.xyz 这个 URL 之后直接 iframe 了 godlike.html ( 我猜是个玩 lol 的放纵 boy, 具体代码可以看下面

![](http://drops.javaweb.org/uploads/images/1cc33ac235678cb6ffd41587381ae03b593edece.jpg)

没什么好说的, 巴拉巴拉就到了下面

0x03 XSS
========

* * *

由 form 表单跳转到的企业邮箱页面如下, 加载了 qzoneon.com 这个 URL 下的一段 js

![](http://drops.javaweb.org/uploads/images/306d8b3c80c175a5f5c68658ec5557f135838e9e.jpg)

哎呀, 页面变成这样了, 好糟糕, 看下html代码, 有奇怪的 script 进来了, 这段加载的 js 就是偷取 cookie 发送到攻击者的服务器上。

![](http://drops.javaweb.org/uploads/images/6f08e71a624417ff75d0c17f67c2c15d3faf7475.jpg)

恩, 果不其然, orz, 如果不是同学提前跟我说估计我也上钩了, 以后民那桑打开 QQ 里的东西还是小心点为好 = =

因知乎上已经出现了详细的漏洞分析：https://www.zhihu.com/question/39019943，故公开此文章。

![enter image description here](http://drops.javaweb.org/uploads/images/9ccba034d2667c00e18f2b28af29e094db156982.jpg)