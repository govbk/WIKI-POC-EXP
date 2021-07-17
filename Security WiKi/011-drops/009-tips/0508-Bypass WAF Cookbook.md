# Bypass WAF Cookbook

**PS**.之前一直想把零零碎碎的知识整理下来，作为知识沉淀下来，正好借着wooyun峰会的机会将之前的流程又梳理了一遍，于是就有了下文。也希望整理的内容能给甲方工作者或则白帽子带来一些收获。

0x00 概述
=======

* * *

随着网络安全越来越受到重视，发展越来越快。随之也出现了越来越多的安全防护的软件。例如有：

> 1.云waf；[阿里云盾，百度云加速，360网站卫士，加速乐等]
> 
> 2.传统安全厂商的硬件waf以及一直存在的ips，ids设备；[绿盟，启明，深信服，安恒等]
> 
> 3.主机防护软件如安全狗，云锁；
> 
> 4.软waf如modsecurity，nginx-lua-waf等。

当然也有目前很火的sqlchop。

这些进行web攻击的防护的软件，我们先统称他们为WAF，它们也是下文的主角了。

0x01 WAF 在哪里
============

* * *

这里我就用’WAF’来代替上面所说的一些防护软件，我们需要知道这些WAF都在网络空间的哪些位置。

**用户从浏览器发出一个请求（[http://www.miku.com/1.php?id=1%20and1=1](http://www.miku.com/1.php?id=1%20and1=1)）到最终请求转发到服务器上，中间经历了多少设备，这些工作在网络的第几层（TCP/IP协议）？我们应用层的数据被哪些设备处理了？**

**这是一个经典的数通问题，了解WAF在网络空间的位置，我们便可以更清楚的知道使用哪些知识来协助我们进行WAF bypass。**

如下图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/d8cb2fcca98bbe00d6dc345fed4567eb51f1438c.jpg)

画了一个简单的拓扑图。

图中可以很清楚的看到，我们的云waf，硬件ips/ids防护，硬件waf，主机防护，软waf以及应用程序所在的位置。

0x02 WAF 数据处理
=============

* * *

在明白了各种防护软件在网络环境下的拓扑之后，现在了解一下基础数据的流量与相关设备的基本处理。

假设客户端访问url：[http://www.miku.com/1.php?id=1’and’1’=’1](http://www.miku.com/1.php?id=1%E2%80%99and%E2%80%991%E2%80%99=%E2%80%991)，该请求请求的数据是服务器上数据库中id为1的记录。

假设这台服务器使用了相关云waf。

1）一个完整的过程，首先会请求DNS，由于配置云waf的时候，会修改DNS的解析。我们发送DNS请求之后，域名会被解析到云WAF的ip上去。DNS解析完成之后，获取到域名信息，然后进入下一个步骤。

2）HTTP协议是应用层协议，且是tcp协议，因此会首先去做TCP的三次握手，此处不去抠三次握手的细节，假设三次握手建立完毕。

3）发送HTTP请求过去，请求会依次经过云WAF，硬件IPS/IDS设备，硬件WAF设备，服务器，web服务器，主机防护软件/软WAF，WEB程序，数据库。 云WAF，硬件IPS/IDS，硬件WAF均有自己处理数据的方式。云WAF与硬件WAF细节上不太清楚，对于硬件IPS有一定的了解。之前在drops上发过一篇文章，文章链接是：[http://drops.wooyun.org/papers/4323](http://drops.wooyun.org/papers/4323)。

在获取HTTP数据之前会做TCP重组，重组主要目的是针对互联网数据包在网络上传输的时候会出现乱序的情况，数据包被重组之后就会做协议解析，取出相关的值。如`http_method=GET`,`http_payload=xxx`等等。这些值就对应了IPS规则中相关规则的值。从而来判断规则匹配与不匹配。

0x03 WAF BYPASS的理解
==================

* * *

**在我自己看来，所谓的BYPASS WAF实际上是去寻找位于WAF设备之后处理应用层数据包的硬件/软件的特性。利用特性构造WAF不能命中，但是在应用程序能够执行成功的载荷，绕过防护。**

**那些特性就像是一个个特定的场景一样，一些是已经被研究人员发现的，一些是还没被发现，等待被研究人员发现的。当我们的程序满足了这一个个的场景，倘若WAF没有考虑到这些场景，我们就可以利用这些特性bypass掉WAF了。**

例如我们现在需要bypass一个云WAF/IPS/硬件WAF，此处我们可以利用的点就是：

> 1.Web服务器层bypass
> 
> 2.Web应用程序层bypass
> 
> 3.数据库层 bypass
> 
> 4.WAF层bypass

由于各个层面可以利用的特性很多，而且WAF往往要考虑自身的性能等等方面，导致了WAF往往会留下一些软肋。下面的文章来细细的总结下之前那些经常被用来做bypass的特性。

Ps.思路是不是稍微清晰了一点。= =

0x04 Bypass WAF 姿势
==================

* * *

### 1 Web Server层 bypass

利用WEB服务器的特性来进行WAF bypass，常见的组合就有`asp+IIS aspx+IIS php+apache java+tomcat`等。

这部分内容大多是用来做http的解析等相关事务的，因此这里我理解的也就是寻找WAF对于http解析以及真实环境对于http解析的差异特性，利用差异特性来bypass WAF。

**Ps.这部分待挖掘的地方还有很多，而且这部分挖掘出来的特性应该对于WAF的bypass是致命的。**

#### 1.1 IIS服务器

运行在IIS上的程序一般为asp,aspx的。在IIS上我们可以利用的特性：

##### 1 %特性

在asp+iis的环境中存在一个特性，就是特殊符号%，在该环境下当们我输入`s%elect`的时候，在WAF层可能解析出来的结果就是`s%elect`，但是在`iis+asp`的环境的时候，解析出来的结果为`select`。

本地搭建`asp+iis`环境测试，测试效果如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/ce0b1bdaf09b7f5c5e68a3f6854b9b8236dff1eb.jpg)

Ps.此处猜测可能是iis下`asp.dll`解析时候的问题，`aspx+iis`的环境就没有这个特性。

##### 2 %u特性

Iis服务器支持对于unicode的解析，例如我们对于select中的字符进行unicode编码，可以得到如下的`s%u006c%u0006ect`，这种字符在IIS接收到之后会被转换为select，但是对于WAF层，可能接收到的内容还是`s%u006c%u0006ect`，这样就会形成bypass的可能。

我们搭建`asp+iis`和`aspx+iis`的环境：

###### （1）asp+iis的环境

测试效果如图：

![enter image description here](http://drops.javaweb.org/uploads/images/783ffa126947900b9542a269147b5f9d9a7c48fc.jpg)

###### （2）aspx+iis的环境

测试效果如图：

![enter image description here](http://drops.javaweb.org/uploads/images/fc7ba21de15ba2cf9cc7c1aabecc0fc89718d45a.jpg)

##### 3 另类%u特性

Ps.需要注意的是，这个特性测试的时候发现`aspx+iis`的环境是不支持的，有待做实验考证，怀疑是后缀后面的内容是通过`asp.net isapi`来出来的，导致了asp和aspx的不同。

上面写到了iis支持unicode的格式的解析。这种iis解析，存在一个特性，之前在wooyun上报过一个漏洞：[WooYun: 一个有意思的通用windows防火墙bypass(云锁为例)](http://www.wooyun.org/bugs/wooyun-2015-0115175)。

该漏洞主要利用的是`unicode`在iis解析之后会被转换成`multibyte`，但是转换的过程中可能出现： 多个`widechar`会有可能转换为同一个字符。

打个比方就是譬如select中的e对应的unicode为`%u0065`，但是`%u00f0`同样会被转换成为e。

```
s%u0065lect->select
s%u00f0lect->select

```

WAF层可能能识别`s%u0065lect`的形式，但是很有可能识别不了`s%u00f0lect`的形式。这样就可以利用起来做WAF的绕过。

搭建`asp+iis`的环境：

`asp+iis`的环境

测试效果如图：

![enter image description here](http://drops.javaweb.org/uploads/images/d2193a7411e5c26b55d6eba828b7925b8dde501a.jpg)

Ps.该漏洞的利用场景可能有局限性，但是挖掘思路是可以借鉴的。

#### 1.2 apache服务器

##### 1 畸形method

某些apache版本在做GET请求的时候，无论method为何值均会取出GET的内容，如请求为的method为DOTA2，依然返回了aid为2的结果。

![enter image description here](http://drops.javaweb.org/uploads/images/88a6e77b920c68063639bea2812105ef1737abfc.jpg)

如果某些WAF在处理数据的时候严格按照GET,POST等方式来获取数据，就会因为apache的宽松的请求方式导致bypass。 实例：[WooYun: 安全宝SQL注入规则绕过](http://www.wooyun.org/bugs/wooyun-2013-024599)

ps.测试的时候使用了apache2.4.7的版本。

##### 2 php+apache畸形的boundary

Php在解析`multipart data`的时候有自己的特性，对于`boundary`的识别，只取了逗号前面的内容，例如我们设置的boundary为`----aaaa`,`123456`，`php`解析的时候只识别了`----aaaa`,后面的内容均没有识别。然而其他的如WAF在做解析的时候，有可能获取的是整个字符串，此时可能就会出现BYPASS。

参考：[http://blog.phdays.com/2014/07/review-of-waf-bypass-tasks.html](http://blog.phdays.com/2014/07/review-of-waf-bypass-tasks.html)

![enter image description here](http://drops.javaweb.org/uploads/images/caf2150da20b7ad3951a0e71a14730ba398e62c9.jpg)

如上图，可能出现waf获取的是一个图片的内容，而在web端获取的是`aid=2`的值。这样的差别就有可能造成bypass。

### 2 Web应用程序层bypass

#### 2.1 双重url编码

双重url编码，即对于浏览器发送的数据进行了两次`urlencode`操作，如s做一次url编码是%73,再进行一次编码是`%25%37%33`。一般情况下数据经过WAF设备的时候只会做一次url解码，这样解码之后的数据一般不会匹配到规则，达到了bypass的效果。

个人理解双重url编码，要求数据在最后被程序执行之前，进行了两次url解码，如果只进行了一次解码，这样在最后的结果也是不会被正确执行的。 实例：[WooYun: 腾讯某分站SQL注射-直接绕过WAF](http://www.wooyun.org/bugs/wooyun-2015-090369)

#### 2.2 请求获取方式

##### 2.2.1 变换请求方式

**1）GET,POST,COOKIE**

在web环境下有时候会出现统一参数获取的情况，主要目的就是对于获取的参数进行统一过滤。例如我获取的参数`t=select 1 from 2`这个参数可以从get参数中获取，可以从post参数获取，也可以从cookie参数中获取。

典型的dedecms，在之前测试的时候就发现了有些waf厂商进行过滤的时候过滤了get和post，但是cookie没有过滤，直接更改cookie参数提交payload，即绕过。

实例:[WooYun: 百度云加速防御规则绕过之三](http://www.wooyun.org/bugs/wooyun-2014-089338)一个dedecms的站，`get，post`均过滤了，但是并没有过滤cookie参数。

**2）urlencode和form-data**POST在提交数据的时候有两种方式，第一种方式是使用`urlencode`的方式提交，第二种方式是使用`form-data`的方式提交。当我们在测试站点的时候，如果发现POST提交的数据被过滤掉了，此时可以考虑使用`form-data`的方式去提交。

我们在阿里云ecs主机上搭建个环境，创建一个存在sql注入漏洞的页面，获取参数从POST上获取，首先我以`urlencode`的方式提交，查看发现提交的请求被阻断了。

![enter image description here](http://drops.javaweb.org/uploads/images/7edcda58bb7b0af342c4e10f6841e21e8ae69599.jpg)

其次我们以`form-data`的方式提交，发现爆出了数据库的版本。

![enter image description here](http://drops.javaweb.org/uploads/images/35babd16e548765f5a5b11f8ef40c9834157eaaf.jpg)

##### 2.2.2 畸形请求方式

**1）`asp/asp.net request`解析**

在asp和`asp.net`中使用参数获取用户的提交的参数一般使用request包，譬如使用`request['']`来获取的时候可能就会出现问题。 资料文档：[http://www.80sec.com/%E6%B5%85%E8%B0%88%E7%BB%95%E8%BF%87WAF%E7%9A%84%E6%95%B0%E7%A7%8D%E6%96%B9%E6%B3%95.html](http://www.80sec.com/%E6%B5%85%E8%B0%88%E7%BB%95%E8%BF%87WAF%E7%9A%84%E6%95%B0%E7%A7%8D%E6%96%B9%E6%B3%95.html)

当使用`request['']`的形式获取包的时候，会出现GET，POST分不清的情况，譬如可以构造一个请求包，METHOD为GET，但是包中还带有POST的内容和POST的`content-type`。

我们搭建一个实例：

我们创建一个`letmetest.aspx`的界面获取用户提交的内容，并且将`request['t']`的内容打印出来。【在服务器上安装了安全狗】 首先我们提交正常的POST请求，发现已经被安全狗阻断了：

![enter image description here](http://drops.javaweb.org/uploads/images/900439726a695a63a90276fa3c19ca38793d16a1.jpg)

此时我们提交畸形的请求，method为GET，但是内容为POST的内容，发现打印出来了内容。

![enter image description here](http://drops.javaweb.org/uploads/images/70d919905bd622aa548db26b7ee989d2a3a3207f.jpg)

#### 2.3 hpp方式

HPP是指HTTP参数污染。形如以下形式：

`?id=1&id=2&id=3`的形式，此种形式在获取id值的时候不同的web技术获取的值是不一样的。

假设提交的参数即为：

```
id=1&id=2&id=3 

```

  

```
Asp.net + iis：id=1,2,3 
Asp + iis：id=1,2,3 
Php + apache：id=3

```

如此可以分析：当WAF获取参数的形式与WEB程序获取参数的形式不一致的时候，就可能出现WAF bypass的可能。

Ps.此处关键还是要分析WAF对于获取参数的方式是如何处理的。这里也要再提一下的，hpp的灵活运用，譬如有些cms基于url的白名单，因此可以利用hpp的方式在参数一的位置添加白名单目录，参数2的位置添加恶意的payload。形如`index.php?a=[whitelist]&a=select 1 union select 2`

实例参考：[WooYun: 使用webscan360的cms厂商通过hpp可使其失效（附cmseasy新版sql注射）](http://www.wooyun.org/bugs/wooyun-2015-099513)

3 数据库层bypass
============

数据库层bypass常常是在bypass waf的sql注入防护规则。我们需要针对数据库使用该数据库的特性即可。如mysql，sqlserver等等。最近一直想整理下oracle的，这块也是研究不多的，后续整理后添加到文档里。

Ps.目前数据库被暴露出来的特性很多很多，基本上很多特性综合利用就已经够用了，因此特性知不知道是一方面，能不能灵活运用就得看测试者自己了。

#### 3.1 mysql数据库

就目前来看mysql是使用最多的，也是研究人员研究最深的数据库。在我自己测试的角度上我一般会去测试下面的过滤点，因为一般绕过了`select from`就基本可以sql注入获取数据了。

##### 1)常见过滤的位置

###### 第一：参数和union之间的位置

[http://zone.wooyun.org/content/16772](http://zone.wooyun.org/content/16772)贴中有相关总结。

**(1):`\Nunion`的形式：**

![enter image description here](http://drops.javaweb.org/uploads/images/5854025be04310bad35c99adf159682b24b88c21.jpg)

**(2):浮点数的形式如`1.1,8.0`**

![enter image description here](http://drops.javaweb.org/uploads/images/987339508fd625999c08f7ebc8b1a9fd7ef86b10.jpg)

**(3):`8e0`的形式：**

![enter image description here](http://drops.javaweb.org/uploads/images/7c0269dccde31d41f2bb22321fa43fe46234a853.jpg)

**(4): 利用`/*!50000*/`的形式**

![enter image description here](http://drops.javaweb.org/uploads/images/f54e0e4e0d84af5b880cf2bd19a3af00029e11ae.jpg)

###### 第二：union和select之前的位置

**(1)空白字符**

Mysql中可以利用的空白字符有：`%09,%0a,%0b,%0c,%0d,%a0`；

**(2)注释**

使用空白注释

MYSQL中可以利用的空白字符有：

```
/**/ 
/*letmetest*/

```

**(3)使用括号**

![enter image description here](http://drops.javaweb.org/uploads/images/6c7cbf7aa9a8ae6fea1713305306ef42178a8df3.jpg)

###### 第三：`union select`后的位置

**(1)空白字符**

Mysql中可以利用的空白字符有：`%09,%0a,%0b,%0c,%0d,%a0`；

**(2)注释**

使用空白注释

MYSQL中可以利用的空白字符有：

```
/**/
/*letmetest*/

```

**(3)其他方式：**【这里需要考虑的是有时候`union select`和`select from`可能是两个规则，这里先整理`union select`的】

括号：`select(1)from`

![enter image description here](http://drops.javaweb.org/uploads/images/619ea8e0fa0551caf1368ce2873ed47dc3d9ccd3.jpg)

运算符号：

`减号`：

![enter image description here](http://drops.javaweb.org/uploads/images/04f9ad49355bd199024657a2ec92c4706a8baa43.jpg)

`加号`：

![enter image description here](http://drops.javaweb.org/uploads/images/2d044618cb26d28cdf616f57406ade67166c4c30.jpg)

`~号`：

![enter image description here](http://drops.javaweb.org/uploads/images/4b117bf6e00760557c12aecb163f5e389d516ff5.jpg)

`!号`：

![enter image description here](http://drops.javaweb.org/uploads/images/6a8c76a9ec35dc93341f17ba837c7c0c04b8bde6.jpg)

```
@`形式`

```

![enter image description here](http://drops.javaweb.org/uploads/images/c7f527a8a3c29a28264c8538c358303de2a3a779.jpg)

`*号`，利用`/*!50000*/`的形式

![enter image description here](http://drops.javaweb.org/uploads/images/b194f103c47aa0a9caa21a8534c16ef37597b56f.jpg)

`单引号和双引号`：

![enter image description here](http://drops.javaweb.org/uploads/images/260f83add0066dafd40f9b5a05a7880ac718e7a7.jpg)

`{括号`：

![enter image description here](http://drops.javaweb.org/uploads/images/b956f7843523e730a2aa0c05ce0664ce7c315db6.jpg)

`\N符号`：

![enter image description here](http://drops.javaweb.org/uploads/images/ab17d799f3bbf3d79df66d5474db5dd589fb058a.jpg)

###### 第四：`select from`之间的位置

**(1)空白字符**

Mysql中可以利用的空白字符有：`%09,%0a,%0b,%0c,%0d,%a0`；

**(2)注释**

使用空白注释

MYSQL中可以利用的空白字符有：`/**/ /*letmetest*/`

**(3)其他符号**

```
``符号

```

![enter image description here](http://drops.javaweb.org/uploads/images/fb66e262b56cd6ca37ac42c7c0e7e2d4da6e17e2.jpg)

`+,-,!,~,’”`

![enter image description here](http://drops.javaweb.org/uploads/images/b1c2718eeec3a678025462c5c0895089e1a953a4.jpg)

`*号`

![enter image description here](http://drops.javaweb.org/uploads/images/e24007c43e48f1cb5884132e91abec8fc10a8276.jpg)

`{号`

![enter image description here](http://drops.javaweb.org/uploads/images/c71c6fd2a1139c4a97b4340a82cbcd8efa8c4711.jpg)

`(号`

![enter image description here](http://drops.javaweb.org/uploads/images/7168a98261cc020ae3bcf52491a26db3e99daad3.jpg)

###### 第五：select from之后的位置

**(1)空白字符**

Mysql中可以利用的空白字符有：`%09,%0a,%0b,%0c,%0d,%a0`；

**(2)注释**

使用空白注释

MYSQL中可以利用的空白字符有：`/**/ /*letmetest*/`

**(3)其他符号**

```
``号

```

![enter image description here](http://drops.javaweb.org/uploads/images/284a55584573b2e54915705eddbfb05634c2d347.jpg)

`*号`

![enter image description here](http://drops.javaweb.org/uploads/images/d9c2e12f046564f84e4624d08f1847a47c0d9c41.jpg)

`{号`

![enter image description here](http://drops.javaweb.org/uploads/images/0c9e598b1c816cecc1c4d7d03bd696352d40ab8b.jpg)

`括号`

![enter image description here](http://drops.javaweb.org/uploads/images/a3b360665427025b99776027f4e5c5357be688fd.jpg)

Ps.空白符，注释符，`/!50000select*/,{x version},(),`在很多点都可以使用，某些点有自己特殊的地方，可以使用一些其他的符号。

实例：[http://wooyun.org/bugs/wooyun-2010-0121291](http://wooyun.org/bugs/wooyun-2010-0121291)实例就是利用灵活利用上面的特性，导致了bypass。

##### 2)常见过滤函数

###### (1)字符串截取函数

```
Mid(version(),1,1)
Substr(version(),1,1)
Substring(version(),1,1)
Lpad(version(),1,1)
Rpad(version(),1,1)
Left(version(),1)
reverse(right(reverse(version()),1)

```

###### (2)字符串连接函数

```
concat(version(),'|',user());
concat_ws('|',1,2,3)

```

###### (3)字符转换

Ascii(1) 此函数之前测试某云waf的时候被过滤了，然后使用`ascii (1)`即可

```
Char(49)
Hex(‘a’)
Unhex(61)

```

##### 3)过滤了逗号

###### (1)limit处的逗号：

```
limit 1 offset 0

```

###### (2)字符串截取处的逗号

mid处的逗号：

```
mid(version() from 1 for 1)

```

###### (3)union处的逗号：

通过join拼接。

![enter image description here](http://drops.javaweb.org/uploads/images/2acf4d038e853bcd55a2995991a533b51b7b29e4.jpg)

#### 5.3.2 sqlserver数据库

##### 1）常见过滤位置

###### (1) select from后的位置

空白符号：

```
01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10,11,12,13,14,15,16,17,18,19,1A,1B,1C,1D,1E,1F,20 

```

需要做`urlencode`，`sqlserver`中的表示空白字符比较多，靠黑名单去阻断一般不合适。

**注释符号**Mssql也可以使用注释符号/**/

**其他符号：**.符号

![enter image description here](http://drops.javaweb.org/uploads/images/7d4fca625e5540ce299060ed50ee70847eab39e7.jpg)

:号

![enter image description here](http://drops.javaweb.org/uploads/images/64b0d89df6c624c4fb71f4c2076fa01d4a1cb0db.jpg)

###### (2) select from之间的位置

**空白符号：**

```
01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10,11,12,13,14,15,16,17,18,19,1A,1B,1C,1D,1E,1F,20 

```

**注释符号**Mssql也可以使用注释符号/**/

**：号**

![enter image description here](http://drops.javaweb.org/uploads/images/cfe451e2346ecd3d0e21f16b8246b33679170276.jpg)

###### (3) and之后的位置

**空白符号：**

```
01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10,11,12,13,14,15,16,17,18,19,1A,1B,1C,1D,1E,1F,20 

```

**注释符号**

Mssql也可以使用注释符号`/**/`

`：号：`

![enter image description here](http://drops.javaweb.org/uploads/images/bce1c3e19203a794ae37961b2aa492e8d47775b0.jpg)

`%2b号`：

![enter image description here](http://drops.javaweb.org/uploads/images/d17495a5c3fa39b606e515bd3f0076f2af9c550e.jpg)

##### 2）常见过滤函数

###### (1)字符串截取函数

```
Substring(@@version,1,1)
Left(@@version,1)
Right(@@version,1)

```

###### (2)字符串转换函数

```
Ascii(‘a’) 这里的函数可以在括号之间添加空格的，一些waf过滤不严会导致bypass
Char(‘97’)

```

###### (3) 其他方式

Mssql支持多语句查询，因此可以使用；结束上面的查询语句，然后执行自己构造的语句。动态执行。

使用exec的方式：

![enter image description here](http://drops.javaweb.org/uploads/images/1e31e4e1e20b4ea4c893c9bea1fce462e8c7b47d.jpg)

使用sp_executesql的方式：

![enter image description here](http://drops.javaweb.org/uploads/images/3a5cfb4b8d811d46f4b10ddde45cc50079570bc9.jpg)

使用这类可以对自己的参数进行拼接，可以绕过WAF防御。

如使用该类特性然后加上上面提到的:的特性就可以绕过安全狗的注入防御。

### 5.4 WAF层bypass

#### 5.4.1 性能bypass

WAF在设计的时候都会考虑到性能问题，例如如果是基于数据包的话会考虑检测数据包的包长，如果是基于数据流的话就会考虑检测一条数据流的多少个字节。一般这类算检测的性能，同时为了保证WAF的正常运行，往往还会做一个bypass设计，在性能如cpu高于80%或则内存使用率高于如80%是时候，会做检测bypass，以保证设备的正常运行。

WAF等设备都是工作在应用层之上的，如`HTTP,FTP,SMTP`等都是应用层的协议，这些数据要被处理都会被进行数据解析，协议分析。最终获取应用层的数据。如HTTP的方法是什么，HTTP的`querystring`是什么，以及HTTP的`requestbody`是什么。然后将这些实时获取的值与WAF设计的规则进行匹配，匹配上着命中规则做相应的处理。

##### 5.4.1.1 性能检测bypass

![enter image description here](http://drops.javaweb.org/uploads/images/e796a34a0004cceee7b18ef0a147c927fca38c14.jpg)

现在问题就是检测多长呢？例如我用HTTP POST上传一个2G的文件，明显不可能2G全做检测不但耗CPU，同时也会耗内存。因此在设计WAF的时候可能就会设计一个默认值，有可能是默认多少个字节的流大小，可能是多少个数据包。

之前在zone发过个帖子，[http://zone.wooyun.org/content/17331](http://zone.wooyun.org/content/17331)，是测试安全狗的，大致原理应该是一样的，设计了一个脚本，不断的向HTTP POST添加填充数据，当将填充数据添加到一定数目之后，发现POST中的sql注入恶意代码没有被检测了。最终达到了bypass的目的。

在测试某家云WAF的时候使用此类方法也可以达到bypass的目的。

##### 5.4.1.2 性能负载bypass

![enter image description here](http://drops.javaweb.org/uploads/images/e4cefd5a9496b02a666b6c24b6a829da92924393.jpg)

一些传统硬件防护设备为了避免在高负载的时候影响用户体验，如延时等等问题，会考虑在高负载的时候bypass掉自己的防护功能，等到设备的负载低于门限值的时候又恢复正常工作。

一些高性能的WAF可能使用这种方法可能不能bypass，但是一些软WAF使用这种方式还是可以bypass的。

[http://wooyun.org/bugs/wooyun-2010-094367](http://wooyun.org/bugs/wooyun-2010-094367)一个bypass的例子，将请求并发同时发送多次，多次访问的时候就有几次漏掉了，没有触发waf的拦截。

Ps.作者自己在测试的时候曾经做了如下测试制造了一个payload，同时添加了大量的无效数据，使用脚本兵法发送该请求，发现请求的时候有些通过了WAF，有些被WAF所拦截了。应该就是性能问题导致了bypass。

#### 4.2 fuzz bypass

![enter image description here](http://drops.javaweb.org/uploads/images/d6410c91f8482dcdff7ff52524875a5960c66784.jpg)

使用脚本去探测WAF设备对于字符处理是否有异常，上面已经说过WAF在接收到网络数据之后会做相应的数据包解析，一些WAF可能由于自身的解析问题，对于某些字符解析出错，造成全局的bypass。 我测试的时候常常测试的位置：

```
1）：get请求处 
2）：header请求处 
3）：post urlencode内容处 
4）：post form-data内容处

```

然后模糊测试的基础内容有：

```
1）编码过的0-255字符 
2）进行编码的0-255字符 
3）utf gbk字符

```

实例1：[http://wooyun.org/bugs/wooyun-2010-087545](http://wooyun.org/bugs/wooyun-2010-087545)

在一次测试安全狗的过程中，使用post的方式提交数据，提交数据包括两个参数，一个是正常的fuzz点，另一个参数包含一个sql注入语句。当在测试前面的fuzz点的时候，处理到\x00的字符的时候，没有提示安全狗阻拦。应该是解析这个字符的时候不当，导致了bypass。

实例2：[http://wooyun.org/bugs/wooyun-2015-091516](http://wooyun.org/bugs/wooyun-2015-091516)

在一次测试云WAF中，使用get方式提交数据，提交内容包括一个参数，参数为字符+sql注入的语句。当在fuzz字符的时候，发现云waf在处理到&字符的时候，没有提示云waf阻拦。由于&字符的特殊性，猜测是由于和url请求中的&没有处理好导致的。由于mysql中&&同样可以表示and，因此拼凑一下sql语句就达到了bypass的目的。

Ps.上面做模糊测试的时候仅仅是测试了一些各个位置的单个字符，应该还会有更复杂的测试，WAF并没想象的那么完美，肯定还可以fuzz出其他地方的问题。

#### 5.4.3 白名单bypass

![enter image description here](http://drops.javaweb.org/uploads/images/d7917748082f2bfca27b5e666acfcca88a5c7550.jpg)

WAF在设计之初一般都会考虑白名单功能。如来自管理IP的访问，来自cdn服务器的访问等等。这些请求是可信任的，不必走WAF检测流程。

获取白名单的ip地址如果是从网络层获取的ip，这种一般bypass不了，如果采用应用层的数据作为白名单，这样就可能造成bypass。

之前有一篇文章：[http://h30499.www3.hp.com/t5/Fortify-Application-Security/Bypassing-web-application-firewalls-using-HTTP-headers/ba-p/6418366#.VGmhx9Yi5Mu](http://h30499.www3.hp.com/t5/Fortify-Application-Security/Bypassing-web-application-firewalls-using-HTTP-headers/ba-p/6418366#.VGmhx9Yi5Mu)

文章内容是通过修改http的header来bypass waf，这里我们截取文章中部分内容：

![enter image description here](http://drops.javaweb.org/uploads/images/b48aae05dca54ea4513bf2e2f60774f684876017.jpg)

这些header常常用来获取IP，可能还有其他的，例如nginx-lua-waf:

![enter image description here](http://drops.javaweb.org/uploads/images/a7c262f9a26b13eacbfdbd7f1202c9321cc76f31.jpg)

获取clientip使用了X-Real-ip的header。

此种方法还可以用来绕过如登陆锁ip，登陆多次验证码，后台验证等等的场景。

0x05 结束语
========

* * *

特性就像是一个个特定的场景一样，一些是已经被研究人员发现的，一些是还没被发现，等待被研究人员发现的。

随着一个个特性的发现，WAF的防护能力在web对抗中逐渐增强，在我看来，当所有的特性场景均被WAF考虑到的时候，势必就会有的新的发现。（如我们现在了解的mysql的场景）

因此我们不用担心当所有的特性被WAF考虑到的时候我们无计可施，未知的特性那么多，我们还有很多地方可以去挖掘。

当你发现这些姿势都不好使的时候，你就该去发现一些新的特性了，毕竟设计WAF的选手都是基于目前的认知下去设计的，当新的特性出现的时候，势必又是一波bypass。