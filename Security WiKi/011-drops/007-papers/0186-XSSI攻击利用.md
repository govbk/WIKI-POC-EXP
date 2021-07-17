# XSSI攻击利用

0x00 介绍
=======

* * *

From:[MBSD Technical Whitepaper](http://www.mbsd.jp/Whitepaper/xssi.pdf)

PS: MBSD是一家日本安全公司，最近好像经常分享技术文档的样子。

Cross Site Script Inclusion (XSSI) 跨站脚本包含是一种攻击技术允许攻击者通过恶意js绕过边界窃取信息。具体的说，应该是通过潜入script标签加载外部数据，for example:

```
<!-- attacker's page loads external data with SCRIPT tag -->
<SCRIPT src="http://target.wooyun.org/secret"></SCRIPT>

```

过去几年，web安全研究者之中通用的认识中js文件，jsonp, json，或者版本较老的浏览器都有可能受到这种方式的攻击，除此之外，还可以通过一些浏览器的漏洞来得到js的错误信息利用，不过目前应该已经修复的差不多了。

2014，我们针对这个技术进行了专门的研究，发现了一些有趣的利用技术和浏览器漏洞，可以获取一些简单的文本中的信息，比如csv，在一些特定的情境下还可以获得更复杂的信息。我们主要的研究方向在于通过客户端脚本去识别目标数据的方法，比如变量，或者函数名。

下一节会开始介绍利用技术，最后会谈论下防御的手段。

0x01 攻击技术／漏洞
============

* * *

我们总共发现了5种与xssi相关的漏洞利用技术，或者是浏览器漏洞。

*   IE bug导致错误信息泄漏
*   通过UTF-16编码获取其它类型的数据
*   chrome/firefox 中 Harmony proxy bug利用
*   穷举
*   csv获取

2.1 IE bug导致错误信息泄漏
------------------

* * *

为了防止js错误信息跨域泄漏，对于外部加载的js文件，现在主流的浏览器只有固定的错误信息，比如“script error”,当是在ie9与ie10，情况不一定如此。

一般来说，在外部js发生语法错误的情况下，浏览器只会提供固定的错误信息，但是当在runtime发生错误的情况下，浏览器会提供详细的错误信息。比如"foo 未定义"之类的，某些浏览器一旦允许外域js回复详细的错误信息，就会导致信息泄漏。

就是说，当某个网页的内容能被js识别为javascript格式的话，那么就可能通过错误信息获取到目标的内容。

比如，目标网页

```
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="a.csv"
Content-Length: 13
1,abc,def,ghi

```

攻击者设置错误显示

```
<SCRIPT>window.onerror = function(err) {alert(err)}</SCRIPT>
<!-- load target CSV -->
<SCRIPT src="(target data's URL)"></SCRIPT>

```

一旦加载成功，网页则会显示 "'abc' is undefined" 。

会出现这种情况是因为浏览器将目标识别为javascript，那么abc就会被识别为某个未定义的变量。当为这种情况的时候，浏览器就允许页面捕捉来自不同网页的错误信息。

做一个总结就是，有被利用的可能性的数据都是可以被识别，或者通过某种方式识别为有效js的数据。

我们在2014年7月报告这个问题，分配MS14-080，后来的 CVE-2014-6345也同样被分配到这个bug (1](2] 他们的修补方案跟其他的浏览器是差不多的，把错误信息改成某个固定的信息。

不过，稍微需要注意的一点，出现该漏洞的只有ie 9 和 ie 10.

遗憾的是我们并不是最早注意到这个问题的货，08年的时候，安全研究人员Chris Evans就在firefox (3]中发现了类似的问题，不过他的攻击代码看起来好麻烦的样子，这货利用多重重定向来欺骗浏览器。另外一件事就是13年的时候，研究人员Yosuke Hasegawa 和 @masa141421356也做过相关的研究，(4]

2. 用UTF-16获取json和其他类型的数据
------------------------

* * *

大家可以看到，上面的东西只在csv这种操蛋的玩意上有用， 所以我们做了更多的研究看看能否获取不同格式的数据，之后我们发现通过UTF-16编码可以达到我们的目标。

其实本身是一个很简单的技巧 比如页面a ，我们加入 charset="UTF-16BE"

```
<!-- set an error handler -->
<SCRIPT>window.onerror = function(err) {alert(err)}</SCRIPT>
<!-- load target JSON -->
<SCRIPT src="(target data's URL)" charset="UTF-16BE"></SCRIPT>

```

然后json数据长这个逼样

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Disposition: attachment; filename="a.json"
Content-Length: 39
{"aaa":"000", "bbb":"111", "ccc":"222"}

```

当响应缺少字符集规范的时候，会被charset属性强制转码为固定的编码，我们用这个技巧撸掉了许多有名的浏览器，包括ie 9。

测试这段代码之后，我们给自己弹了个窗。

![enter image description here](http://drops.javaweb.org/uploads/images/268d6f33de9260e93bce9f13514b009994d584e0.jpg)

我们可以看到一串乱码，因为，当浏览器获取目标网页的数据，之间经过了一次编码，然后到我们的页面上经过charset制定的字符集进行了一次解码。

![enter image description here](http://drops.javaweb.org/uploads/images/ee4318667bb54b7118677030667e8c4287d69ba6.jpg)

我们能很简单的得出一个结论就是我们能通过对乱码的再次编码来获得原有的信息，不过需要注意的就是只有当编码后的信息能够被浏览器识别为有效的js标示符的时候攻击才有可能成功，这是一个重要的条件，对于不同的平台的编码是有所不同的，在ie上可以被识别为有效js标示符的字符是多于其他平台的，至于其他来说ie的 ECMAScript规范 (5]跟其他浏览器总体没什么不同。

打个比方对于ie来说 '3q' (U+3371, ㍱) 在 unicode编码中会被认为是 属于 "Symbol, Other [So]",就是符号的一种。总的来说这种形式的认定不应该发生在任何浏览器中，不过ie可能比较2b一些。

我们花了很多时间研究了什么样的组合，能够被浏览器认定为有效的js标示符，当字符编码为UTF-16的时候的数字字母组合，ie 9将其99.3%认为是有效的js标示符，高于chrome和firefox。具体结果见下图

![enter image description here](http://drops.javaweb.org/uploads/images/d68e4ebb974f51d90a0980bf4bb17435cfc0823e.jpg)

需要注意的一件事就是在ie 10 或者更高的版本，可能攻击无法奏效，因为ie 10 拒绝将没有空字节活着bom的编码为utf16。

3. Harmony proxy bug in Firefox / Chrome
----------------------------------------

* * *

Harmony是一个ECMAScript 6中的新功能 (6] ，类似于java的反射类，其中定义了对于对象属性的查找，分配，函数调用，在我们针对这些新特性的研究过程中发现该功能可以用于xssi的攻击中。

for example:

```
<!-- set proxy handler to window.__proto__ -->
<SCRIPT>
var handler = {
 has: function(target, name) {alert("data=" + name); return true},
 get: function(target, name) {return 1}
};
window.__proto__ = new Proxy({}, handler);
</SCRIPT>
<!-- load target CSV -->
<SCRIPT src="(target data's URL)"></SCRIPT>

```

注意其中的window.**proto**定义了一个代理对象，当访问一个未定义的全局变量，就会出发handler进行处理。

然后csv文件长这样：

```
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="a.csv"
Content-Length: 13
1,abc,def,ghi

```

当访问攻击页面的时候如果攻击成功那么久会收到 "data=abc", "data=def", "data=ghi"的弹窗，我们在firefox和chrome都得到了验证。

我们在去年八月报告该bug，同一时间chrome 的js代理被默认关闭，需要通过设置开启 （chrome://flags/#enable-javascript-harmony），后来在15年1月 (7]，该功能被从chrome中分离。该bug被分配cvs编号 CVE-2014-7939 (8](9]

对于firefox ，在我们还在专注写报告的时候，firefox却公布了这个bug (10]，原因是一个叫Erling Ellingsen的货发现了这个bug然后发到twitter上(11]，目前该bug还没修复，当然也没有cve。

不过倒是推荐关注下 firefox 的bug跟踪版(7] (10]，这是否真的算个安全漏洞确实值得讨论，or只需要将其当成js功能的一种，另外一个事实就是，即使没有这玩意我们也可以通过对外部文件的穷举来攻击兼容js语法的文件。

下面我们会讨论关于穷举的攻击方式。

4. 穷举搜索
-------

* * *

假设一个攻击页面通过js 加载了下面的csv文件。

```
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="a.csv"
Content-Length: 8
1,xyz123

```

一旦加载我们就会得到一个 xyz123未定义的错误，换句话说，如果我们在加载外部文件之前定义了这个标示符，那么我们就不会受到这个错误，同时我们也可以判断xyz123是存在于外部文件中的。也就是说我们需要一个合适的检测错误是否发生的方式。一般情况下浏览器是不提供详细的外部错误信息，不过仍然会返回一个通用的错误标示。所以说穷举信息还是是存在可能性的。

总的来说我们发现三种穷举的方式

第一种是二元搜索。比如你知道目标会是 "xyz121", "xyz122", "xyz123" 和 "xyz124"中的其中一个，可以先定义前两个变量然后看有无错误爆出，然后定义后两个，然后再缩小目标。

第二种是使用 js 的getter，像下面酱紫

```
<!-- set getters -->
<SCRIPT>
Object.defineProperty(window, "xyz121", {get: function() {alert("value=xyz121")}});
Object.defineProperty(window, "xyz122", {get: function() {alert("value=xyz122")}});
Object.defineProperty(window, "xyz123", {get: function() {alert("value=xyz123")}});
Object.defineProperty(window, "xyz124", {get: function() {alert("value=xyz124")}});
</SCRIPT>
<!-- load target CSV -->
<SCRIPT src="(target data's URL)"></SCRIPT>

```

就是目标值访问 window.***||||||* 会触发上面的规则。

第三种是使用vbscript来获取json数组，这个思路来自Hasegawa做的研究，组合vbscript和json进行攻击(4]

目标页面长这个样子

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Disposition: attachment; filename="a.json"
Content-Length: 12
[1,"xyz123"]

```

然后再我们的攻击界面中调用vbscript

```
<SCRIPT language="vbscript">
Sub [1,"xyz121"]: MsgBox "value=xyz121": End Sub
Sub [1,"xyz122"]: MsgBox "value=xyz122": End Sub
Sub [1,"xyz123"]: MsgBox "value=xyz123": End Sub
Sub [1,"xyz124"]: MsgBox "value=xyz124": End Sub
</SCRIPT>
<!-- load target JSON as VBScript -->
<SCRIPT src="(target data's URL)" language="vbscript"></SCRIPT>

```

跟上面的攻击相似，都是通过穷举来获取目标值。不过vbscript只试用于ie。

ps: 怎么说呢。。。我觉得好蛋疼。

CSV with quotations thef
------------------------

* * *

上面获取csv的信息只在目标的字符串没被引号扩起来的情况下，不过同样是一些小技巧能够使我们绕过这一限制。

让我们假设一个csv长这个b样。

`1,"___","aaa@a.example","03-0000-0001"`

`2,"foo","bbb@b.example","03-0000-0002"`

`...`

`98,"bar","yyy@example.net","03-0000-0088"`

`99,"___","zzz@example.com","03-0000-0099"`

假设攻击者能够插入自己的字符串，那么只需要根据RFC相关CSV (RFC 4180 (12])中的规定来添加一个双引号就可以bypass这个限制。

for example

`1,"\"",$$$=function(){/*","aaa@a.example","03-0000-0001"`

`2,"foo","bbb@b.example","03-0000-0002"`

`...`

`98,"bar","yyy@example.net","03-0000-0088"`

`99,"*/}//","zzz@example.com","03-0000-0099"`

一个比较蛋疼的问题就是如何获取多行的信息，因为多行在js中是违法的，上面的例子里，我们使用 $$$=function() {/_…_/}来进行攻击，然后攻击者可以调用$$$.toString() 获取函数远吗来达到攻击目标数据的目的。这种攻击方式试用于所有的浏览器。

一种获取多行内容的方式可以在chrome和firefox中奏效，就是ECMAScript6模版字符串中通过反引号来获取多行内容。

0x02 结论
=======

* * *

下面是需要注意的一些问题。

上面我们演示了xssi通过组合浏览器漏洞或者一些攻击技巧来到达获取一些特定数据的目的，不过其利用场景还是具有局限性的。

其防御的方式只需要设置响应头围X-Content-Type-Options: nosniff ，那么浏览器就会拒绝记载这种类型的数据为js。

同时还需要设置字符集规范，来防止一些特殊场景的攻击，从这里可以看到一些关于字符集攻击的参考(13]

攻击并不局限于某种浏览器。

很蛋疼的一个问题 X-Content-Type-Options 头只适用ie－8+ 和chrome，并不包括其他浏览器。

firefox还在讨论要不要这么搞。(14](15]

总之建议使用 Content-Type 和 X-Content-Type-Options。

这里有一些其他的措施

*   禁止get请求
    
*   使用一些难以猜测的参数
    
*   使用自定义头时使用XHR进行请求。
    

或者说只是拒绝不满足条件的http请求，简单来说设置一些过滤规则进行拦截。