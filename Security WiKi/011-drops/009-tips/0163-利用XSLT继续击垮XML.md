# 利用XSLT继续击垮XML

0x00 介绍
=======

* * *

### XSL

首先我们要说的是，这个XSLT应该这么断句：XSL-T。XSL指的是EXtensible Stylesheet Language，中文被很直白地翻译成扩展样式表语言。这种语言和xml有莫大关系：XSL之于XML相当于CSS之于HTML。HTML的每个元素都是预定义好的，比如`<table>`用来定义表格，浏览器也知道怎么识别这个标签，此时CSS就能轻松地告诉浏览器该怎么显示这个表格，然而由于XML里面的任何标签都可以由程序员自己定义，所以**需要一种XSL语言来描述如何显示xml文档。**这是一篇web安全文章，所以我们还是讨论web相关的xsl安全，而支持在web上调用的是xslt v1，所以我们只讨论version1发生的故事。

### XSLT

XSL包括三个部分：XSLT,XPath，XSL-FO。在安全领域，Xpath已经有前人的研究 ([xpath injection](https://www.owasp.org/index.php/XPATH_Injection))，而其他两个几乎无人问津。去年black hat黑客大会，终于有安全组织(IOActive)共享出自己的研究成果[Abusing XSLT](https://www.blackhat.com/docs/us-15/materials/us-15-Arnaboldi-Abusing-XSLT-For-Practical-Attacks-wp.pdf)。 XSLT顾名思义，就是用来将XML转换成XHTML或者是其他XML文档。

当用XML来生成其他文档时(e.g. xhtml)，XSL可以作为XML的引用。同时，XSL能够内嵌到XML中发挥作用。

既然谈XSLT安全，就得考虑他们的应用场景，这篇文章我们将从客户端和服务端两个方面分析XSLT实现的脆弱性。为了简化讨论，我们讨论这几个vendor的安全问题：

*   libxslt:libxslt为后端的Python,PHP,PERL,RUBY及前端的safari,opera,chrome提供XSL解析。
*   Transformiix：讨论它是因为它被firefox调用，用来处理xsl
*   Microsoft：不用解释也能明白，微软自家的IE,肯定用的是自己的解析库了。

0x01 攻击模型
=========

* * *

### 客户/服务端：数字表示及运算风险

XSL对数学有自己的一套"独特"的理解.我们先讨论下它对大整数的处理：

#### Large Integers

比如

![p1](http://drops.javaweb.org/uploads/images/221c822f18382bcb3618a86d868560e89f114395.jpg)

以及它的样式

![p2](http://drops.javaweb.org/uploads/images/d259fee4888dece9cf603c7efceff5100ecf0c66.jpg)

在诸如Xsltproc, Php, Perl, Ruby, Python, Safari, Chrome和Opera的libxslt系的处理软件上，都会将上面这段xml解释成这样(chrome)：

![p3](http://drops.javaweb.org/uploads/images/bb4dac1a90841649e0341f710ffee9866ee0bf14.jpg)

问题很明显了。

IOActive给出了他们研究调查的结果

![p4](http://drops.javaweb.org/uploads/images/c93e24918f595253f70079f72740b7135f849618.jpg)

### 随机数

同样的，xsl的某些vendor对于随机数的生成也是相当写意的。而这个粗糙的vendor竟然还是应用最广泛的libxslt，由于这个库在生成随机数的时候根本就没有IV，所以每一次生成的随机数，都是根本不变的。

![p5](http://drops.javaweb.org/uploads/images/df40c72f07412e6bbfc3bfb0cddca4cc72765af1.jpg)

让我们将这个和PRG一起hi起来。。。

### 客户端：Safari SOP绕过

Safari的同源策略同样可能被这个xml的样式语言被破坏。

前面提到过，safari早就支持xml和xhtml的转换。然而利用XSLT中的document(), 我们能够带着相应的cookies跨域读取safari其他域内的资源。 这样一来，我们就能可以通过 document()->value-of()/copy-of()这个流程被窃取到其他网站的用户信息，最终，通过JavaScript发送给攻击者。

我复现了ioactive的poc，然而结果却和IOActive不一样：

在IOActive的报告中

![p6](http://drops.javaweb.org/uploads/images/a366d414d83a612928a31ee079a70335553c116a.jpg)

无疑成功取到了结果，成功BYPASS。

而我本地测试的时候却在Safari控制塔得到这样的提示

![p7](http://drops.javaweb.org/uploads/images/498ebb9f69c8ebab44043dc0a5092b3672aca97d.jpg)

无疑是被sop ban掉了。

是apple修复了，还是利用姿势不对，我将[POC](http://evilshadow-wordpress.stor.sinaapp.com/uploads/2016/02/Archive.zip)放到了文章最后，大家可以下载下来研究。

### 服务端：任意文件读取

XSLT文档在执行错误的时候回立即终止，它和他的兄弟XML类似，一小丁点错误就会抛出一个错误。然而错误信息也是能够给攻击者带来一些有用的信息的。

XSLT提供了三个用来读文件的方法

*   document(): 用来访问另一个xml文档内的信息（刚刚的跨域中同样用到）
*   include(): 用来将两个样式表合并
*   import(): 用来将一个样式表覆盖另一个

比如如下这个样式表A

```
<?xml-stylesheet type="text/xsl" href="2-9-Reading_Non-XML-Files.xsl"?>
<file>/etc/passwd</file>

```

和B

```
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> <xsl:template match="/">
<xsl:value-of select="document(file)"/> </xsl:template>
</xsl:stylesheet>

```

当B被解析时，会尝试调用A表，而A表会试着用document()读取/etc/passwd的内容,很明显这不是一个xml文档，所以不可能读取，幸运的是在输出的错误信息里面，我们可以看到目标文本的第一行被输出了。

![p8](http://drops.javaweb.org/uploads/images/d189bf1b4dc148de6a57a59a4703e32a01df9d73.jpg)

虽然只有第一行，但是第一行能够获取的铭感信息可不少了

*   /etc/passwd: Linux root password
*   /etc/shadow: Linux root password
*   .htpasswd: Apache password
*   .pgpass: PostgreSQL password

这次，xsltproc php perl ruby这四种语言的所有方法（document() ，import() ，include()）都受到影响 （php不愧是世界上最好的语言，什么事儿都有他的份）~~~~