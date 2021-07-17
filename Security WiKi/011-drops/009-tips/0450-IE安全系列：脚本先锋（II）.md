# IE安全系列：脚本先锋（II）

接着上一篇的来，本文多为Javascript的脚本阅读和解释，阅读都是自行完成，所以不免可能会出现一些错误或者联想过度的情况，如果你发现了哪儿有问题请重重地拍出来。

IV.1 HTML与网马攻击4 — Virus In the Wild
===================================

* * *

本篇中我们将从真实的Exploit Kit的利用代码入手介绍分析方式，文中例子采用Angler Exploit Kit 和 Magnitude Exploit Kit（下简称为AEK和MEK）在2015年4月初最新的代码。

AEK和MEK是互联网上最著名的漏洞利用工具包，在Phoenix Exploit Kit作者锒铛入狱之后，这两个Exploit Kit的“市场份额”一下子窜到了前面，因为作者更新快，采用加密方式繁多，导致杀毒软件更新特征也较为困难，这让它们有充足的机会去攻击有漏洞的电脑。本文将介绍这两个Exploit Kit的加密方式和解密方法。

首先，让我们从AEK开始，AEK和MEK都需要有一个Landing Page，用于将用户定向到恶意页面上，打开Landing Page，我们会发现AEK为了做混淆，给Landing Page加了很多无用的垃圾数据，并将加密后的数据混淆插入在这些代码中：

![enter image description here](http://drops.javaweb.org/uploads/images/248f9df6f8682fe846a700d49d407e297ec4cc6c.jpg)

图：code部分是加密后的代码

将页面向下拖动，快到最后的地方就是它的解密脚本了：

![enter image description here](http://drops.javaweb.org/uploads/images/860b3fd31f6cba2bb0ddd565bf1ed6ae38e2d7f9.jpg)

图：AEK的脚本

是的，这就是一个高度混淆后的脚本，因为JavaScript代码（或者说类C语言语法）的宽松性，作者在这里面使用了大量的空白、回车、缩进符，同时还替换了变量名，使用大量的数学函数来做混淆。

对于人来说，要阅读这样的代码简直是一个非常恶心的工作，所以在此推荐使用一些代码规范化工具，例如Malzilla提供的js标准化，或者这里还有一个小技巧：使用Notepad++或者类似工具的括号匹配功能：

![enter image description here](http://drops.javaweb.org/uploads/images/5bf1d0c9a3de004a0bfa701dc1aab1d8645212f7.jpg)

将光标移动到function的大括号处，此类软件会自动标示出函数范围，可见上图中该函数范围是LN268-LN385。这样，我们就能清晰的知道这个代码的结构了：

![enter image description here](http://drops.javaweb.org/uploads/images/ff09522006686975835296168a3b5dd4b691508b.jpg)

而之前我们也说过，Function除外的Global代码，会从上往下执行，因此，攻击者如果想要实现读取-解密-执行的步骤，执行必然是最后一步，因此我们只需要在它执行之前将要执行的数据找到即可。

![enter image description here](http://drops.javaweb.org/uploads/images/ae08dc654bd65b69df6693b0b8efa3c9b4c1a790.jpg)

翻到最后，可以发现LN568-574的Script段其实和上面LN558-565几乎一样。这意味着这段代码很可能包含着解密和执行两步的内容。

从最后一句入手，

LN564：

```
rqNNhndhLxLVVb[nmfAbWwoA]('TQgaaGLDVYlaQT',QXuSacI)

```

逐个查看变量的作用，

LN267表明：

```
rqNNhndhLxLVVb = window;

```

这是因为Javascript中允许将任何对象赋值给某个变量，因此rqNNhndhLxLVVb此时实际上可以看作是window的“别名”或者“同义词”。

看看第二个变量nmfAbWwoA的来源：

LN561可以发现是该变量的第一次使用的地方：

```
nmfAbWwoA = "ezVI"+"Migbc".substr(6,8)  //ezVI

nmfAbWwoA = nmfAbWwoA+[].join(dLpy) + "xlyG"

```

变量dLpy经过阅读可知在：

LN437处赋值：

```
dLpy=  ('EoVzQHTfRyGU').substr(12,12)  //””

```

因此nmfAbWwoA的值实际上只是“ezVIxlyG”。

第三个变量： LN558可以发现是该变量第一次赋值的地方：

```
var QXuSacI; 
QXuSacI= ['Y', 'r', 'a', 'd', 'P'].join(dLpy)

```

由于dLpy我们已经知道是空字符了，所以实际上QXuSacI的值就是”Yradp”。

这样，将三处组合，LN564的原始语句实际上是：

```
window[”ezVIxlyG”]('TQgaaGLDVYlaQT', ‘Yradp’);

```

这个ezVIxlyG的原型是什么呢？搜索代码，找到它的赋值点：

LN438：

```
var D1Kx; 
ezVIxlyG= !!D1Kx?true:( function (){ ……} );

```

这里有一个约定俗成的内容，可以看到D1Kx是刚刚定义而且未赋值的，将其作为布尔型来处理时，其默认值是false，因此，!!D1Kx的值实际也是false。

这样该三目表达式实际上只是相当于一个普通的赋值：

```
ezVIxlyG = function(){……}

```

由于此时我们还没处理该函数，因此这个混淆后的代码应该是十分难读的，所以，我们对其进行一个简单的处理： 复制LN439-545

*   替换所有双空格、三空格->单空格，直到没有2个以上连续空格为止。
    
*   \n、\r全部删除
    
*   使用工具将代码重新格式化。
    

完成后，代码如下所示：

![enter image description here](http://drops.javaweb.org/uploads/images/5dbf5015ec9e05905dcf8b5fc31763f3bfd9b98d.jpg)

可见代码还是难以理解，这是因为其中包含了大量的变量：

![enter image description here](http://drops.javaweb.org/uploads/images/7a104ccd805d2d6877929b88459af58ea53d5635.jpg)

你可以看到这个地方定义的变量大部分都会分散地被之后的代码使用到。

所以我们要关注的还是函数的最后：

```
if(flag == 1)
{
    rqNNhndhLxLVVb [YPub] ( UjcS )
}
else 
{
    rqNNhndhLxLVVb [YPub] ( UjcS )
}

```

这里又是一个无用分支，rqNNhndhLxLVVb我们已经知道是window对象了，YPub是什么呢，可以看看上面的代码，最好倒着看，我的注也是从5开始倒着写到1处的，请注意：

```
YPub=tP+yMwnso  （注：eval）
tP= 'e' 、 yMwnso= ('Rv'+('uapt') ['re'+'place'] ( 'u', dLpy)) [iCQl0] ( K1DMU, 2 ) +'l'   （注：val）
iCQl0= (wRxKW+'snubnstrn') [F9k2c] ( /n/g , qm3sXy)     （注：substr）
F9k2c=qm3sXy+'r'+ yMwnso + 'pl' + qm3sXy    + 'ac' +yMwnso   （注：replace）
K1DMU=3-2

```

因此我们看到了这句实际上是：

```
window[”eval”](UjcS);

```

现在知道做什么了吗？对，先把eval换成alert！

![enter image description here](http://drops.javaweb.org/uploads/images/40e8a8f0deac0d8b7f5f944676a3d62805baef53.jpg)

然后，直接运行该HTML，得到解密后数据：

![enter image description here](http://drops.javaweb.org/uploads/images/298b39217020c5309ad4bed0113ce4fbd3fc9109.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8b082e70fd6f74f0d2026637164029e9433c8ef6.jpg)

等等，共4次，将这些内容合起来就是解密后的代码了。可以看到这个代码利用了多个新漏洞，甚至包括卡巴斯基控件的安全漏洞。

IV.2 HTML与网马攻击5 - Virus In The Wild
===================================

* * *

让我们再看看Magnitude Exploit Kit这款EK的代码，相比AEK而言，难度是高还是低

![enter image description here](http://drops.javaweb.org/uploads/images/2c6786b015aafc72fa00f13cfdcfc4c2c178dbda.jpg)

图：MEK的Landing Page

可以看出来，相比而言它的代码貌似要简单得多，可以清晰的看到document和eval被分别赋予了两个不同的变量。

通过将eval修改为alert，执行后得到：

![enter image description here](http://drops.javaweb.org/uploads/images/4f4aaa9488ffc1fedf99166358fb6dfc452582c8.jpg)

完了？显然没有，将eval换成alert之后得到的数据是一个function，而点击确定之后，得到了一个脚本错误：

![enter image description here](http://drops.javaweb.org/uploads/images/302ad930149b972152e7a750392d91a01a6909c3.jpg)

图：脚本错误

仔细阅读一下，首先，这个eval的范围是：

![enter image description here](http://drops.javaweb.org/uploads/images/4af405bb0c89724c1469e7d81a647ec333efec14.jpg)

在它之后出现了一个从未见到过的函数：

![enter image description here](http://drops.javaweb.org/uploads/images/5dce1fde98de6464eb3f53ddac5c360f8ec19cf4.jpg)

而对比我们之前弹出的alert可以发现，这个函数就是eval解出来的结果，因此，我们应该做的是把eval部分换成解密后的内容：

```
function t1g6(a,b){var inn = document.getElementById('avp6').innerText;var out='';var c=inn.split('*');for(var k=a;k<b;k++) out += String.fromCharCode(c[k]-21);return out;}

```

用上述内容替换掉eval块，得到：

![enter image description here](http://drops.javaweb.org/uploads/images/1af7bf53fa7c3d8869fb3aa990ef1f3710aff2f8.jpg)

但是之后显然没有eval了，这时，其实我们只需要了解document[”XXX”]将返回document下的XXX对象，这个对象是可以作为函数来调用的（或者不如说函数就是一个对象:) ）就可以了：

![enter image description here](http://drops.javaweb.org/uploads/images/38d32805f39510d8859ed1d670cf6231cf8017f4.jpg)

因此后面的c1h82by0（document）就显得很是危险，所以让我们看看s4tb[0]的内容并注释掉后面的内容，记得之前说的嘛？一个script块中的代码一直到出错为止都是可以正常运行的，所以不用管之后的代码会不会出错了，主要是后面的代码很可能是恶意代码，不能让恶意代码在我们自己的电脑上跑起来。

![enter image description here](http://drops.javaweb.org/uploads/images/13581e5a290ab77b7579f36f33c1e801d3b2d487.jpg)

图：执行结果

因此，可以知道这里是在做document[”createElement”]这个操作，司马昭之心，路人皆知，再将其内容改为alert(s4tb[1](http://drops.wooyun.org/wp-content/uploads/2015/04/image0016.png))，执行可得：

![enter image description here](http://drops.javaweb.org/uploads/images/76970974349db0e90048ba900ecf7edc3f0ca972.jpg)

图：执行结果

串上后面的内容可以知道，这段代码事实上正在创建一个iframe，其src执行漏洞代码页面： hXXp://bf29df.e66.83.1c.3d8a.54.1393d.bc7dc6b.6.scg512374t1.changesmoves.in/47b1d0b4466375c9306821f48abcd6b5（放心，此时这个网站已经无法访问了。）

至此，这个页面的核心内容我们已经全部了解了，至于后面的几个变量，解法也是一样的，如果想要练手的话，可以试着将页面内容全部还原成无混淆状态试试看。页面内容见附件。

IV.3 HTML与网马攻击6-利用arguments.callee实现“递归解密”的网马以及解密
=================================================

* * *

希腊神话中有一条名为Ouroboros的蛇，它咬着自己的尾巴，它的姿态象征着“不死”、“完全、“无限”、“世界”、“睿智”等种种意味。

![enter image description here](http://drops.javaweb.org/uploads/images/62bf1c90df9fd3374cd8f42b9599543bfcc02f89.jpg)

图：乌洛波洛斯，网络图

在编程中，称作递归，递归在Javascript中可以像C的代码一样：

```
function a(){ a();}

```

来调用，不仅如此，javascript还支持一种arguments.callee的方式来调用。callee为对当前函数的引用，故可以作为类似递归的方式来调用自身。

不过，递归还是需要谨慎的，稍有不慎，一个bug即可导致整个程序出现不可知的情况。

![enter image description here](http://drops.javaweb.org/uploads/images/1c0a25b2d0dcc0542b05c2ebd866a1f6d1a131bc.jpg)

图：IE10递归导致死循环，栈空间全部用完导致崩溃

言归正传，先让我们看两个例子大致理解一下普通递归和arguments.callee：

以下两个例子输出均为：1 2 3。

普通递归，

```
function mylog(current, max)
{
if(current <= max) 
{
console.log(current); 
add(current+1, max);
}
} 

mylog(1,3); 

```

以及arguments.callee：

```
function f(x)
{
console.log(x);
return arguments.callee;    
}     
f(1)(2)(3);

```

从实际入手吧，请参考如下网马的例子：

![enter image description here](http://drops.javaweb.org/uploads/images/df52bc1a688f0953af6543a44fee554829e426f0.jpg)

是否第一眼就看到了倒数第二行出现了

```
eval(I3qVh4gPT);

```

如果你试图将它改为alert(I3qVh4gPT);，那么这个函数的解密结果必然会失败：

![enter image description here](http://drops.javaweb.org/uploads/images/ed1ea661c61a7b5dcb8f055715906966671bb9e0.jpg)

原因是什么呢？请看第一行出现了

```
v ar eJmF3VT3H=arguments.callee.toString().replace(/\W/g,'').toUpperCase();

```

我们知道arguments.callee是对当前函数的引用，那么这个引用转为字符串是什么呢？让我们测试一下：

![enter image description here](http://drops.javaweb.org/uploads/images/53eff125acf98f69804757cb095161cd76f65671.jpg)

原来就是返回了当前函数。

![enter image description here](http://drops.javaweb.org/uploads/images/109aad65c0bbb9b7067f56caf897807645b85a6e.jpg)

仔细一看，这里会把函数自己当成参数来解密。

所以，如果我们想要解开这个脚本的加密应该怎么弄呢？

1. 简单阅读代码
---------

* * *

从最后来，①eval(I3qVh4gPT);引用了变量I3qVh4gPT。

②I3qVh4gPT+=String.fromCharCode(EHxDfdAM5);引用了变量EHxDfdAM5。

③EHxDfdAM5=e3FP5e1M6-IA17ef3d3[bqjtxUvBR];if(EHxDfdAM5<0) {EHxDfdAM5=EHxDfdAM5+256;} 引用了变量e3FP5e1M6、IA17ef3d3[0]。

④e3FP5e1M6=parseInt(EWX1TnOBq,16); 引用了变量 EWX1TnOBq，将其作为十六进制解析。

⑤var EWX1TnOBq=mXSYkqH0X.substr(PwgNCEKQL,2); 中，mXSYkqH0X是参数，PwgNCEKQL是计数器。

⑥for(PwgNCEKQL=0;PwgNCEKQL<Oq32NWn5D;PwgNCEKQL+=2) 这段代码在这个循环内，循环上限出现在：

⑦Oq32NWn5D=mXSYkqH0X.length; ，也即参数的长度，因此，这段代码在解密传入的参数。

还有，③中出现了另一个变量IA17ef3d3，这个变量出现在⑧IA17ef3d3[PwgNCEKQL]=fgMN0vK2r.charCodeAt(va31p5um0);，这之中还引用了fgMN0vK2r、va31p5um0两个变量

⑨fgMN0vK2r=RsIkkqdYi[(fgMN0vK2r^eJmF3VT3H.charCodeAt(gMKy026SO))&255]^((fgMN0vK2r>>8)&16777215);中出现了fgMN0vK2r。RsIkkqdYi是一个预设密钥组，eJmF3VT3H是当前函数（arguments.callee.toString()等处理后的结果），gMKy026SO是计数器。因此这句是在基于一个密钥组产生一个密钥组；

⑩for(PwgNCEKQL=0;PwgNCEKQL<8;PwgNCEKQL++) {var va31p5um0=Oq32NWn5D+PwgNCEKQL;xy3D07u0l[PwgNCEKQL]=1;xy3D07u0l[PwgNCEKQL]=FSB4JaYie;if (va31p5um0>=8) {va31p5um0=va31p5um0-8;IA17ef3d3[PwgNCEKQL]=fgMN0vK2r.charCodeAt(va31p5um0);} 同样，va31p5um0也在参与解密。

也即，将传入参数每隔2个字符作为一个HEX，然后解出来，与将函数自身的字符串通过解密算法解出来的数据相减，两者结果小于0的话，加上256，最终对所有字符都如此操作，将结果连接起来得到解密数据。

既然函数本身不能轻易修改，那么只好从最终的eval做突破了，javascript中允许“劫持”一个对象。即和操作普通变量的赋值一样，函数也是可以通过赋值来覆盖的，请看第二部分。

2. 函数劫持
-------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/0e4740be78f575bdc4630cae7e7df0d48c26bcad.jpg)

针对这个代码，因为最终它会通过eval来运行恶意代码，所以添加eval=alert，在运行到eval之前将其劫持即可。

运行代码可以得到：

![enter image description here](http://drops.javaweb.org/uploads/images/e275eacbe55b50f9e225372aa80adc1771e63912.jpg)

最后，总结一下，在Jscript9.dll中，脚本的函数中调用arguments.callee.toString()时，大致经历了如下几个步骤： 解析脚本文字（ScriptSite::ParseScriptText）； 送与解析内核，生成字节码，通过字节码解释器（即Intepreter）来执行； 在处理到arguments.callee.toString()时，jscript会将函数自身marshal成BSTR，然后转换成JsVar，传递给后续要使用它的代码。

题外话，这个代码其实是2010年发现的一个广告软件（是当时流行的Rogue antivirus，也就是伪装成杀毒软件的广告程序）安装页的Landing Page，当时我还特地上论坛和大家讨论了怎么解决，大家给出的思路也相当多，除了上述我说的方法之外，一些自动化解密工具也可以处理此类网马，例如Malzilla。不过建议大家不要过于依赖工具，而是把工具当作可以简化重复劳动的工具是最好。

到此为止，脚本先锋系列的解密部分就告一段落了，下一篇开始，将简单的介绍调试器的用法以及如何对网马中使用的Shellcode进行调试，其中也包括简单的对恶意SWF、PDF的分析的内容。

参考资料
====

* * *

(1] 文中恶意脚本打包，请在虚拟环境下测试与调试（密码drops.wooyun.org ）：[Download](http://drops.wooyun.org/wp-content/uploads/2015/04/malscripts2.rar)