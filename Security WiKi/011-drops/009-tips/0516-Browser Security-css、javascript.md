# Browser Security-css、javascript

### 层叠样式表（css）

* * *

调用方式有三种：

```
1 用<style>
2 通过<link rel=stylesheet>，或者使用style参数。
3 XML（包括XHTML）可以通过<?xml-stylesheet href=...?>

```

浏览器进行解析的时候会先HTML解析再做CSS解析，所以下面的代码会出错：

```
<style>
some_descriptor {
 background: url('http://www.example.com/</style><h1 > Gotcha!'); } 
</style>

```

字符编码：

为了保证在css中可以使用可能产生问题的字符，css提供了一种方式由反斜杠()加六位十六进制数字。

字符e可以编码成\65 \065 \000065，当后面紧跟的字符也是十六进制字符中的一种的时候，只有最后一个才是对的。

例如teak编码成 t\65ak 不会正常，因为会解码时会把\65a当成一个字符。

为了避免上述情况可以编码以后加一个空白符，例如：t\65 k。

很多CSS解析器同样会解析引号之外的字符串。

下面两个代码IE下相同

```
<A STYLE='color: expression\028 alert \028 1 \029 \029'>
<A STYLE='color: expression(alert(1))'>

```

#### Fuzzing

CSS的解析规则与HTML和JavaScript在几个方面不同。

JavaScript在语法错误的时候，整个代码都会被忽略，而CSS解析错误时，浏览器尝试忽略错误的代码。

这点上跟HTML比较类似，因为HTML语法错误时，浏览器会尝试修复并展现出来，

@符号用来在CSS样式表中定义一个特殊属性，定义字符集（@charset）或者media的样式（@media）。

导入外部样式（@import）或外部字体（@font-face）或命名空间（@namespace）或定义一个演示文件（@page）。

定义字符集的时候，可以定义一个多字节字符集（如：SHIFT-JIS，BIG5，EUC-JP，EUC-KR或GB2312）可能会使反斜线失效：

```
@charset "GB-2312";
*{
content:"a%90\"; color:red; z:k";
}

```

会解析为：

```
@charset "GB-2312";
*{
content:"a撞"; color:red; z:k";
}

```

还有一种时UTF-7字符：

```
@charset "UTF-7";
*{
content:"a+ACIAOw- color:red; z:k";
}

```

会解析为：

```
@charset "UTF-7";
*{
content:"a"; color:red; z:k";
}

```

定义@charset在IE中并非这一种定义UTF-7的方式：

```
+/v8-
*{
content:"a+ACIAOw- color:red; z:k";
}

```

在一些浏览器中导入的时候可以定义字符集：

```
<link rel=stylesheet charset=UTF-7 src=stylesheet>

```

CSS的选择器是非常有趣的部分，他可以包含字符串，表达式，函数。选择器也可以由多行组成：

CSS中的声明时一个 属性/值 对里面的规则集，通常形式如下：

```
property: value;

```

property是一个关键字，包括字母数字破折号，和大于0x7F的字符，也有绕过的方式：

```
-moz-binding与\2d moz\2d binding相等。

```

IE中property没有严格遵守这个规则，如果一个属性包含多个字，只有第一个字将被使用，其他的都会忽略：

```
a b c: value;
a: value;

```

上面两个规则是等效的。 并且IE中:可以替换为=

```
a = value;
a: value;

```

上面两个也是等效的。

同样重要的是IE允许多行的字符串，URL，选择器。

CSS最明显的局限性是，他本身不是一种编程语言，而是一种语言风格，他没有任何的编程逻辑。

他很难不借助于JavaScript进行攻击，下面主要讨论的是完全基于CSS不依赖于其他脚本语言的攻击。

整体的逻辑：

```
element:condition{
   action;
   }

```

element可以为任意值，condition为CSS选择器，如:visited，:active，:hover，:selected。 事件选择器：

```
1 :hover 悬停鼠标在一个元素。
2 :active 点击一个元素。
3 :focus 光标放在一个元素上。

```

CSS造成点击劫持：

```
<style>
iframe{
filter:alpha(opacity=0);opacity: 0;
position: absolute;top: 0px;left: 0px;
height: 300px;width: 250px;
}
img{
position: absolute;top: 0px;left: 0px;
height: 300px;width: 250px;
}
</style>
<img src="用户看到的图片">
<iframe src="用户实际操作的页面"></iframe>

```

点击劫持的防御方法一是添加X-FRAME-OPTIONS:NEVER头，另外一种方式是利用JavaScript：

```
<body>
<script>
if(top!=self)
document.write('<plaintext>');
</script>

```

两种方式都有局限性，之前发过点击劫持的文档了，详见：[http://drops.wooyun.org/tips/104](http://drops.wooyun.org/tips/104)

如下代码是一个有效的CSS2的代码，并且在Firefox，Safari，Chrome，Opera，IE7，IE8，IE9中没有影响，但是在IE6中，可执行代码：

```
<style>
foo[bar|="} *{xss: expression(alert(1));} x{"]{
  color:red;
}
</style>

```

以下代码中的color可以编码为c\olor，\c\o\l\or，c\6f l\06f r 。

```
*{
color: red;
}

```

### 浏览器脚本语言

* * *

解析javascript的时候以下两段代码不相同：

| 代码一 | 代码二 |
| --- | --- |
| &#x3cscript> var my_variable1 = 1; var my_variable2 = &#x3c/script> &#x3cscript> 2; &#x3c/script> | &#x3cscript> var my_variable1 = 1; var my_variable2 = 2; &#x3c/script> |

这是因为`<script>`在解析之前并没有链接起来，相反，代码一中的第一个script标签会引起错误。

从而导致整个标签被忽略，所有标签内的代码都无法执行。

在JS中有两种定义函数的方式：

```
var aaa=function(){...}
function aaa(){...}

```

var 方式定义的函数，不能先调用函数，后声明，只能先声明函数，然后调用。

function方式定义函数可以先调用，后声明。

```
<script>  
//aaa();这样调用就会出错  
var aaa = function(){  
  alert("A");  
}  
aaa();//这样就不会出错  
//先调用后声明  
bbb();  
function bbb(){  
  alert("bb");  
}  
</script>

```

出于历史原因，某些HTML元素`（<IMG>，<FORM>，<EMBED>，<object>，<APPLET>）`的名字也直接映射到文档的命名空间，如下面的代码片段所示：

```
<img name="hello" src="http://www.example.com/">
<script>
 alert(document.hello.src);
</script>

```

DOM操作：

```
document.getElementById("output").innerHTML = "<b>Hi mom!</b>";

```

向id为output的标签里插入`<b>Hi mom!</b>`。 采用.innerHTML插入数据时，必须为完整的数据块，比如下面的代码：

```
some_element.innerHTML = "<b>Hi";
some_element.innerHTML += " mom!</b><i>";

```

等同于下面的代码：

```
some_element.innerHTML = "<b>Hi</b> mom!<i></i>";

```

DOM操作时，其本身会对一些字符做解码处理，如下代码：

```
<textarea style="display:none" id="json">
{
  "name":"Jack&quot;",
  "country":"China"
}
</textarea>
My name is :<span id="me">loading...</span>
<script>
function $(id){
  return document.getElementById(id);
}
var data=$("json").value;
alert(data);
var profile=eval("("+data+")");//把string转成object方便操作
$("me").innerHTML = profile.name;
</script>

```

可以看到alert出的data数据为

```
{
     "name":"Jack"",
     "country":"China"
}

```

下面的例子是使用getAttribute时也会解码：

```
<img id="pic" src="http://www.baidu.com/img/baidu_sylogo1.gif" bigpic="http://baidu.com&quot;&gt;&lt;img src=1 onerror=alert(1)&gt;&lt;i b =" onclick="test()">
<div id="bigimage">
</div>
<script>
function $(id){
  return document.getElementById(id);
}
function test(){
  big=$("pic").getAttribute("bigpic");//big此时为：http://baidu.com"><img src=1 onerror=alert(1)><i b =
  $("bigimage").innerHTML="<img src=\"" + big + "\"/>";
}
</script>

```

#### javascript编码

javascript支持多种字符编码方式：

```
1 C语言的编码，\b表示退格，\t表示水平制表符等等，公认的ECMAScript编码。
2 三位数字：用反斜杠加八位8进制来表示，如\145可表示字符e，该语法不属于ECMAScript，但是基本所有的浏览器都支持。
3 两位数字：用反斜杠加x加八位16进制表示，如\x65可表示字符e，同样不属于ECMAScript，但是在解析底层，C语言中有很好的支持。
4 四位数字：Unicode编码，十六位16进制表示，如\u0065可表示字符e，属于ECMAScript编码。

```

需要注意的是组后一种编码方式不止在字符串中才可以表示，如下代码也可正常的执行（但是不可替代括号与引号）：

```
<script>
\u0061lert("This displays a message!");
</script>

```

#### Fuzzing

JavaScript中，window对象是一个全局变量，并且默认定义的变量都为全局变量，window下的方法可以直接访问：

```
<script type="text/javascript">
alert(1);
window.alert(1); 
window.alert(window.alert); 
</script>

```

并且可重写：

```
<script type="text/javascript">
function alert() {}
alert(1)
</script>

```

定义数组的两种方式：

```
<script type="text/javascript">
x=[1,alert,{},[],/a/];
alert(x[4]);
</script>

```

默认返回最后一个：

```
<script type="text/javascript">
objLiteral={'objProperty':123};
alert(objLiteral[0,1,2,3,'objProperty']);
</script>
<script type="text/javascript">
objLiteral={'objProperty':123};
alert(objLiteral[(0,1,2,3,(0,'objProperty'))]);
</script>

```

JavaScript中定义字符串除了'string'，"string"方式之外，还有其他的方式：

```
<script type="text/javascript">
alert(/I am a string/+'');
alert(/I am a string/.source);
alert(/I am a string/['source']);
alert(['I am a string']+[])
</script>

```

第一个alert中是一个正则表达式加一个空字符串，JavaScript会把正则强制转为字符串。 第二个alert中使用了标准的正则对象的source属性，返回结果为正则匹配完的字符串，第三个相同是属性的另外一种访问方式。 第三个alert中是利用了访问数组时如果不是指定的访问一个元素，会自动调用toString()方法，转为字符串。 还有一种非标准的使用字符串的方式（IE8，Safari，Opera，Firefox和Chrome已经支持），使用类似数组的方式：

```
<script type="text/javascript">
alert('abcdefg'[0]);
</script>

```

火狐当中对函数名的规范非常的宽泛：

```
<script type="text/javascript">
window.function=function function(){return function function() {return function function(){alert('Works in Firefox')}()}()}()
</script>

```

JavaScript支持多行的字符串，当一\结尾时，下一行的字符串会接着上一行的结尾：

```
<script type="text/javascript"> 
alert("this is a \
\
\
\
\
string");
</script>

```

似乎所有的JavaScript引擎都支持函数之前的运算符，如：+，-，~，++，--，!，运算符也可写在typeof和void之前。

```
<script type="text/javascript"> 
!~+-++alert(1)
</script>
<script type="text/javascript"> 
void~void~typeof~typeof--alert(2)
</script>
<script type="text/javascript"> 
alert(3)/abc
</script>

```

最新的Chrome与Safari前两个已经不会执行了。 查看控制台可以看到三个js其实都是报错了的，前两个是由于alert函数返回的是undefined，进行++和--操作的时候是非法的。 最后一个是试图用alert函数除以一个未声明的变量，先执行alert函数后再除的时候报错。