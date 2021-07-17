# AnglerEK的Flash样本解密方法初探

**作者：360QEX团队**

0x00 前言
=======

* * *

在病毒查杀过程中，一直存在着攻与防的技术对立，恶意程序会采用各种方法躲避杀毒引擎的检测，增加分析难度。360QEX团队之前分别对JS敲诈者和宏病毒的隐藏与反混淆分享过相关内容，这次则分享一些AnglerEK的Flash样本解密方法。

Angler EK攻击包是当前最为著名的一个攻击包，从出现至今，已经被大量用于网页挂马。由于Angler EK能够整合最新被修复的漏洞利用代码，甚至偶尔会出现0day的利用代码，因而被视为最先进的漏洞攻击包。

近两年来，Angler EK大量使用Flash作为漏洞利用载体，往往Adobe刚刚曝光一个漏洞，就立即出现在了Angler EK攻击包中。为了躲避杀毒软件的检测，Angler EK采用了多种方法加密Flash攻击代码，增加了检测难度和安全人员的分析难度。

0x01 字符串与函数名的混淆
===============

* * *

在ActionScript3中代码调用的相关函数名称和类名，均以字符串形式存储在doabc字段中，所以为了规避针对调用函数名和类名的检测，AnglerEK采用了getDefinitionByName函数，根据传入的字符串参数转换为调用对应的函数或者类，然后在将这些字符串进行切分，躲避过了简单的特征字符串检测，这也是很多其他EK攻击包所常用的方法。

这种方法进一步进行混淆的话，就可以将这些字符串采用拼接、正则替换的手法，例如样本c288ccd842e28d3845813703b9db96a4中，使用了如下的方法，基本可以完美的躲避字符串特征检测。

![](http://drops.javaweb.org/uploads/images/6dbfa1d1e196ef0a4fd3953fe2b25ec1b21f1dc1.jpg)

图1 字符串拆分

此外，ActionScript和JavaScript同样基于ECMAScript，因此很多JavaScript的混淆方法同样适用于ActionScript，例如下标运算符同样能够用于访问对象的成员，这时可以参照JavaScript常见混淆方法来进行代码还原。

在样本eeb243bb918464dedc29a6a36a25a638中，摘录了部分采用下标运算来访问对象成员的代码，如下所示：

代码1 下标运算符执行类成员

```
vree = getDefinitionByName("flash.utils.ByteArray") as Class;
weruji = "length";
var _loc2_:* = new vree();
wxwrtu = "writeByte";
while(_loc7_ < _loc4_[weruji])
{
    _loc2[wxwrtu](_loc4_[_loc7_]);
    _loc7_++;
}

```

以上这段代码等价于如下代码段：

代码2 还原后的代码

```
var _loc2_:* = new flash.utils.ByteArray();
while(_loc7_ < _loc4_.length)
{
    _loc2_.writeByte(_loc4_[_loc7_]);
    _loc7_++;
}

```

0x02 外壳flash加密
==============

* * *

除了字符串及调用函数名以外，还有一大块比较重要的特征是ShellCode。ActionScript中ShellCode经常是存放在数组、Vector中，或者使用连续的pushInt、pushByte等代码构造，这些大段连续的代码，也是非常明显的特征，并且大多数情况下都不会有大幅度的改变。为了加密掉这些特征，通常会采取类似PE的加密壳的方法，使用一个外层的Flash解密并加载实际的带有漏洞利用功能的Flash文件。这样外壳Flash的功能非常简单，没有明显的特征，每次只需要对外壳Flash进行简单的特征修改，就能够躲避特征查杀。

随之带来的问题是，如何存储这些加密的数据。最初的方法是直接存储与大段的字符串中。例如样本eeb243bb918464dedc29a6a36a25a638中，可以发现其存在一个非常长的字符串，如图2中的this.ybe所示。外壳Flash正是通过对该字符串进行解码和解密，得到实际的Flash，并进行加载。其具体的过程如下：

![](http://drops.javaweb.org/uploads/images/d4fd0462c94ef15548b2d13890586e647eac6deb.jpg)

图2 样本中的长字符串

1.Base64解码

主要是将字符串转换成二进制数据，代码中的wigr方法就是Base64解码函数的具体实现。这也是非常常用的方法，如果看到类似图2中的this.eruuf字符串，则基本可以认为使用了Base64编码方法。

2.进行简单的解密运算，获得其实际的Flash。

其具体的解密是使用RC4对称加密算法。解密代码包含两个256次的循环，第一个while循环将是S盒初始化，第二个while循环是根据解密密钥打乱S盒，看到这个代码就可以猜测是使用了RC4加密算法。解密的key则是图2中的this.jety。

![](http://drops.javaweb.org/uploads/images/ba6dce4bd5c7e921f0233f06d39a16a7c2f1855b.jpg)

图3 样本解密代码

解密出来的样本md5是d9f01b5a3b3dd6616491f391076fbb8f，其代码结构就与早期的未加密AnglerEK代码结构一致。外壳Flash会使用LoadBytes函数加载这个解密出来的Flash，此处就使用了字符串替换以便掩盖调用LoadBytes函数。

![](http://drops.javaweb.org/uploads/images/33f608bdc5dacfb37f3bfe1cd4d36b04bb6ceb8a.jpg)

图4 LoadBytes代码

0x03 BinaryData存储加密数据
=====================

* * *

方法二中的长字符串，也是一个非常明显的特征，因此后续AnglerEK选择这个数据存储于BinaryData结构中，这也是当前很多的Flash加密工具的做法，例如Doswf等。

AnglerEK应该是调用了某个加密工具，把实际的Flash加密后存储在BinaryData中，这个加密工具包有个特点是默认打开的时候存在两个不同颜色并且在不停旋转的字符串动画。例如样本56827d66a70fb755967625ef6f002ad9中，变存在这样的动画，其加密算法的特点是会构造一个长度为91的字符数组，BinaryData里面的数据字符都在这个范围内，然后变换出实际的二进制数据，最后对这些数据进行解码后zlib解压得到数据。

AS3代码过长，这里使用python代码实现相同的解密过程，具体的AS3代码，可以使用FFDec打开该文件，不过要注意的是，在反编译这个代码的过程中，FFDec会丢失部分代码，可以同时使用AS3 Sorcerer配合查看。

![](http://drops.javaweb.org/uploads/images/983222536f91d7843524eaf04fee2e715872a8b1.jpg)

图5 BinaryData数据解码代码

随后样本6cb6701ba9f78e2d2dc86d0f9eee798a又对这个算法进行了一定的改进，对于解码出来的数据，进行了异或解密，对应的Python代码如下：

![](http://drops.javaweb.org/uploads/images/69bbaf03532c9ca6a5a658e1207e3d259bb373a9.jpg)

图6 数据解密代码

0x04 图片存储加密数据
=============

* * *

实际上，不论如何加密数据都无法阻止分析人员手工分析并解密提取文件的，只能增加分析难度。例如近期的样本c288ccd842e28d3845813703b9db96a4则不再采用将数据存放与BinaryData中，而是选择以像素形式存储于图片中，以这种方式增强了躲避杀毒软件扫描的能力。

![](http://drops.javaweb.org/uploads/images/8d9e92ef03b2628fed3f96db3853e798401d2b31.jpg)

图7 图片数据解密代码

解密代码如图7所示，具体的过程如下：

1.提取数据

二进制数据分别存储于非压缩图像的像素值中，其中，第一个像素存放实际的数据长度，剩余的像素中RGB值分别是数据的三个字节内容。把这些数据沿图片纵向拼接在一起，便得到了所需要的内容。

2.使用RC4对获得的数据进行解密。

请注意此处的加密算法又变成的最初的RC4，并且这种将数据存储于图片

的做法非常新颖，猜测这个算法应该是AnglerEK自行设计的，代码简单有效。

0x05 总结与展望
==========

* * *

在本文中，解密获得实际的Flash攻击代码只是分析AnglerEK所利用的Flash攻击代码的第一步，事实上解出的Flash攻击代码仍然是经过大量混淆，我们也会继续分析这些代码，尝试重构其代码结构。

除了上述手工解密Flash文件以外，另外一种比较通用方便的方法是直接Hook LoadBytes函数来解密。不论壳Flash如何解密和代码变换，实际的Flash都会通过LoadBytes函数加载，通过Hook该函数，可以dump所有的Flash数据，但是这样做的唯一缺点是需要把Flash运行起来。

从AnglerEK一次又一次的改变加密算法中，可以看出其躲避引擎查杀的意图，因此采用传统的特征扫描引擎是必然无法应对的。虽然近期AnglerEK突然停止活动，但是如此高水平的攻击包必然会卷土重来，360QEX团队也会继续关注该攻击包的后续活动，并会第一时间支持查杀。鉴于目前层出不穷的Flash漏洞攻击，同时也建议用户及时升级Adobe Flash Player为最新版本。

参考链接
----

技术揭秘:宏病毒代码三大隐身术  
[http://bobao.360.cn/learning/detail/2880.html](http://bobao.360.cn/learning/detail/2880.html)

近期js敲诈者的反查杀技巧分析  
[http://bobao.360.cn/learning/detail/2827.html](http://bobao.360.cn/learning/detail/2827.html)

Is it the End of Angler ?  
[http://malware.dontneedcoffee.com/2016/06/is-it-end-of-angler.html](http://malware.dontneedcoffee.com/2016/06/is-it-end-of-angler.html)

相关样本来源
------

eeb243bb918464dedc29a6a36a25a638  
[http://malware.dontneedcoffee.com/2015/01/cve-2014-9162-flash-1500242-and-below.html](http://malware.dontneedcoffee.com/2015/01/cve-2014-9162-flash-1500242-and-below.html)

c288ccd842e28d3845813703b9db96a4  
[http://malware-traffic-analysis.net/2016/05/31/index3.html](http://malware-traffic-analysis.net/2016/05/31/index3.html)

56827d66a70fb755967625ef6f002ad9  
[http://malware.dontneedcoffee.com/2015/03/cve-2015-0336-flash-up-to-1600305-and.html](http://malware.dontneedcoffee.com/2015/03/cve-2015-0336-flash-up-to-1600305-and.html)

6cb6701ba9f78e2d2dc86d0f9eee798a  
[http://malware.dontneedcoffee.com/2015/05/cve-2015-3090-flash-up-to-1700169-and.html](http://malware.dontneedcoffee.com/2015/05/cve-2015-3090-flash-up-to-1700169-and.html)