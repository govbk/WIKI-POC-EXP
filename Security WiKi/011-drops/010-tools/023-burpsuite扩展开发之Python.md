# burpsuite扩展开发之Python

0x00 简介
=======

* * *

Burpsuite作为web测试的神器，已经人手必备了。它提供的一系列互相配合的工具，极大的提高了手工测试的效率，从1.5版本开始，Burpsuite开始支持扩展。用户可以自己开发扩展实现一些特殊的需求。不过目前关于Burpsuite扩展开发的中文资料很少。这里抛砖引玉总结一下学习的过程。

0x01 基础知识
=========

* * *

目前burpsuite官方支持用java，python，ruby开发扩展，选择还是很多的。Brupsuite的扩展可以实现非常多的功能，比如自定义扫描，修改http请求和响应，修改burp配置等等。几乎所以burpsuite功能都支持在扩展中进行控制。所以其实是可以用扩展把自己经常使用的功能做成自动化的。这也应该是一个最终的学习目标。[官方文档](http://portswigger.net/burp/extender/)是首选的资料。中文介绍资料可以参考[BurpSuite扩展API和HelloWold](http://drops.wooyun.org/papers/3962)。

0x02 环境配置
=========

* * *

安装python开发的扩展需要配置Jython环境。[Jython下载](http://www.jython.org/downloads.html)直接下载Standalone Jar版本就可以。在extender标签页中选择options标签。在python environment中选中刚刚下载的jython standalon jar。

![images](http://drops.javaweb.org/uploads/images/fc5c7409212d88ceaa80f37dc15b653901c78c00.jpg)

如果下载的是jython installer。需要在安装的时候选择standlone类型。之后再在burpsuite中选择安装目录下的jython.jar.![](http://drops.javaweb.org/uploads/images/c85625e5c03adfdf67cd81a93a4d15712b5d98f1.jpg)

如果没有配置好jython环境。添加python编写的扩展会报错。![](http://drops.javaweb.org/uploads/images/a4eba6ca8d36eabbf1f11ea88c326c3c23d1541a.jpg)

0x03 常用接口介绍
===========

* * *

burpsuite的文档中给了多个样例以及详细的[API文档](http://portswigger.net/burp/extender/api/index.html)。![](http://drops.javaweb.org/uploads/images/7d350fa468ade7ea64b035920faec47c27ec74d1.jpg)

个人觉得最快的方法还是阅读现成的扩展代码。很多需求稍微修改现成的扩展就可以完成。Burp的Bapp store里的扩展安装之后默认是在burpsuite同目录下的bapps的文件夹内。![](http://drops.javaweb.org/uploads/images/9c21e2259611e636823538b00267b9e9765b5713.jpg)

简单介绍一下几个最常用的接口：

interface IBurpExtender: 这个接口所有的扩展都需要实现.

Interface IBurpExtenderCallbacks: 这个接口几乎是必备的。在编写扩展的过程中会经常用到。

Interface IExtensionHelpers: 这个接口是新加的。提供了编写扩展中常用的一些通用函数，比如编解码、构造请求等。这样就不需要重负造轮子了。

Interface IHttpRequestResponse: 这个接口包含了每个请求和响应的细节。在Brupsuite中的每个请求或者响应都是IHttpRequestResponse实例。

0x04 第一个burpsuite扩展
===================

* * *

在web测试过程中，使用repeater调试接口是很常见的一个使用方式。现在很多接口都是返回包含unicode明文的json数据，比如这种

```
{"result":"passwd_error","msg":"\u7528\u6237\u540d\u5bc6\u7801\u9519\u8bef"}

```

由于brup的decoder没有对unicode的解码，每次想要看一下这些unicode是是什么意思的时候都需要复制出来使用其他工具解码。可以使用burp扩展来实现自动解码unicode，从而提高测试的流畅性。

首先引入所需要的模块，在BurpExtender类中定义我们需要的方法。

![](http://drops.javaweb.org/uploads/images/64ec1e0e6dd77c1e0b6574cff5206fa06cb7b1f3.jpg)

toolFlag是burpsuite中对工具进行识别的方式，proxy是4，repeater是64.可以在[文档](http://portswigger.net/burp/extender/api/constant-values.html#burp.IBurpExtenderCallbacks)里查看所有工具对应的flag值。这里几行代码就是先解码返回值，查找unicode明文，进行解码，之后再更新响应的body。

![](http://drops.javaweb.org/uploads/images/474f5e13a316300f2a327680a0258b9d5ca11b09.jpg)

加载扩展之前，repeater看到的返回：

![](http://drops.javaweb.org/uploads/images/efcfff9462a22f671a84217fd1de9e7adfcf9c55.jpg)

加载扩展之后：

![](http://drops.javaweb.org/uploads/images/ca1ad755b55cd956e943655b372e64d684f2d458.jpg)

代码下载地址:[github](https://github.com/stayliv3/burpsuite-changeU)

0x05 相关资料
=========

* * *

[BurpSuite 扩展开发[1]-API与HelloWold](http://drops.wooyun.org/papers/3962)[burpextensions.com](http://www.burpextensions.com/category/tutorials/)