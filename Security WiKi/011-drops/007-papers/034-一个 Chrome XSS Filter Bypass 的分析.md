# 一个 Chrome XSS Filter Bypass 的分析

前几天，在微博上看到一条关于最近的 Chrome XSS Filter Bypass 的链接：[webo](http://weibo.com/3274966043/Co3xvztxc?type=comment)，原始补丁在这里：[补丁](https://codereview.chromium.org/1187843005/)。在补丁中还提供了[PoC](https://codereview.chromium.org/1187843005/patch/1/10002)用于后续的单元测试。

攻击者用一种巧妙的方法绕过了 Chrome 的 XSSAuditor 的过滤。不过微博里的那篇短文并没有对这个漏洞的缘由作分析。碰巧前段时间笔者仔细读过 Chrome 的 XSSAuditor 的代码，因此趁此机会自己分析了一下，如果有错误的地方还望指教。

0x00 漏洞描述
=========

* * *

原始 PoC :

```
https://localhost/<svg><script>/<1/>alert(0)</script>

```

补丁如下:

```
Index: Source/core/html/parser/XSSAuditor.cppt a/Source/core/html/parser/XSSAuditor.cpp b/Source/core/html/parser/XSSAuditor.cpp
index a1e1852201d23ac858c3b5065a2e26f52d128f4d..e73259145366c12c821a710fe83d3637529478ee 100644
--- a/Source/core/html/parser/XSSAuditor.cpp
+++ b/Source/core/html/parser/XSSAuditor.cpp
@@ -471,15 +471,18 @@ bool XSSAuditor::filterCharacterToken(const FilterTokenRequest& request)
     if (m_state == PermittingAdjacentCharacterTokens)
         return false;

-    if ((m_state == SuppressingAdjacentCharacterTokens)
-        || (m_scriptTagFoundInRequest && isContainedInRequest(canonicalizedSnippetForJavaScript(request)))) {
+    if (m_state == FilteringTokens && m_scriptTagFoundInRequest) {
+        String snippet = canonicalizedSnippetForJavaScript(request);
+        if (isContainedInRequest(snippet))
+            m_state = SuppressingAdjacentCharacterTokens;
+        else if (!snippet.isEmpty())
+            m_state = PermittingAdjacentCharacterTokens;
+    }
+    if (m_state == SuppressingAdjacentCharacterTokens) {
         request.token.eraseCharacters();
         request.token.appendToCharacter(' '); // Technically, character tokens can't be empty.
-        m_state = SuppressingAdjacentCharacterTokens;
         return true;
     }
-
-    m_state = PermittingAdjacentCharacterTokens;
     return false;
 }

```

补丁中的描述对这一漏洞进行了介绍，大意是，当过滤器过滤 script 标签的内容时，第一个区块的过滤结果将会影响后续区块。如果第一个区块被处理为空时，过滤匹配将会失败。

其实漏洞原理这一句话就介绍明白了。不过，如果对浏览器解析 HTML 的流程以及 XSS Filter 的实现没有了解的话，可能看不大懂上面这句话。

0x01 背景知识
=========

* * *

**首先，浏览器是如何解析 HTML 的？**

这里只简单的介绍一下和该漏洞相关的部分。

实际上，在 HTML5 中， HTML 的词法解析和语法解析是被写进规范里的，这个可以直接在[WHATWG](https://html.spec.whatwg.org/multipage/#toc-syntax)主页上查到。从笔者读源码的了解上看，Chrome(Chromium) 几乎完全遵循了该规范。

其中词法解析部分，将 HTML 源码解析成一个个 token ，比如

```
<div>aaa<img src=x><script>x=1;</script>

```

将被解析成

```
[Start Tag (div)][Characters (aaa)][Start Tag (img)(attr: {src: x})][Start Tag (script)][Characters x=1;][End Tag (script)]

```

每个中括号即为一个 token ，每一个 token 都有一堆自己的属性，比如 token 的名称，属性值等。

**SVG 标签有什么特殊的性质？**

实际上，一般的 HTML 标签属于 HTML namespace 范畴下，而 SVG 标签属于 SVG namespace 范畴。在 SVG 内部，HTML 的解析是按照 XML 模式进行的(与此类似的有 MATHML 标签)。而 SVG 内部也支持 SCRIPT 标签，不过这里的 SCRIPT 标签的解析模式和 HTML 环境下有着很大的区别。某些时候，可以借助 SVG 中 SCRIPT 标签的特殊解析模式，构造一些特殊的攻击向量。比如：

```
<svg><script>alert&#40/1/&#41</script> 

```

在 XML 中实体符号会被解析成对应的字符。而在 HTML 环境中，SCRIPT 标签内部不会被做任何处理。

类似的，下面这种用法 Javascript 也会成功执行：

```
<svg><script>0<a></a>;alert(1)</script></svg>

```

因为在 SVG 内，进入SCRIPT 标签内部后，不必等到出现`</script>`才退回标签解析模式，而是一旦遇到了新的标签，即可退出，因此在 SCRIPT 标签内依然可以插入其他标签。

**Chrome 是如何过滤反射型 XSS 的？**

Chrome 的 XSS 过滤并没有用到正则。而且，这个过滤是在词法解析阶段进行的。也就是说，Chrome 实际上是根据 token 来做过滤的。过滤器会审查每一个 token ,如果发现 token 中存在危险的属性或字段，就对该字段进行处理，然后拿去和 URL 比对。如果发现 URL 中出现了该字段，即将该字段清空，并报告恶意脚本的插入。

比如上面的

```
<div>aaa<img src=x><script>x=1;</script>

[Start Tag (div)][Characters (aaa)][Start Tag (img)(attr: {src: x})][Start Tag (script)][Characters x=1;][End Tag (script)]

```

首先解析器读取到 [Start Tag (div)]，判断没有危险；接下来读取 [Characters (aaa)] ，也没有危险；然后读取 [Start Tag (img)(attr: {src: x})] ，过滤器将会检查 src 属性是否以 javascript: 开头，这里不是，同样没有危险；之后检查 [Start Tag (script)]，这里过滤器将会到 URL 中找 script 字样，来确认 URL 是否有引入脚本的可能；并且从这里开始进入了 script 标签内部，过滤器会对此进行标识；之后到了 [Characters x=1;] ，注意到这里已经到了 SCRIPT 标签内部了，因此，过滤器将会拿 "x=1;" 在 URL 中搜索，这也是文章开头的 Patch 中出现的代码:

```
 -    if ((m_state == SuppressingAdjacentCharacterTokens)
 -        || (m_scriptTagFoundInRequest && isContainedInRequest(canonicalizedSnippetForJavaScript(request)))) {

```

0x02 漏洞分析
=========

* * *

这里我们先不管这个 Patch 是如何修复的，我们先来分析漏洞的成因。

PoC 中的注入代码将会解析成怎样的 token 序列呢？

```
<svg><script>/<1/>alert(0)</script>

```

是这样么?

```
  [Start Tag (svg)][Start Tag (script)][Characters /<1/>alert(0)][End Tag (script)]

```

如果是这样， XSS Filter 是无法绕过的。

在这里，由于是在 SVG 标签内部，词法解析器将会考察每一个 "<" ，当在字符状态中出现 "<" 时，即意味着进入了一个新的标签，词法解析器会将之前的字符串作为一个单独的 token 提取出来处理掉，再来处理这个新的标签。但是这里，`<*/>`并不是一个合法的标签，当解析器处理时，不得不退回，将其当作新的字符串处理。

因此真正的 token 序列是这样的：

```
  [Start Tag (svg)][Start Tag (script)][Characters /][Characters <1/>alert(0)][End Tag (script)]

```

重复上述的过滤器过滤流程，在考察过 SCRIPT 开始标签后，过滤器将会处理随后的字符串。处理函数(补丁前)如下：

```
bool XSSAuditor::filterCharacterToken(const FilterTokenRequest& request)
{
    ASSERT(m_scriptTagNestingLevel);
    ASSERT(m_state != Uninitialized);
    if (m_state == PermittingAdjacentCharacterTokens)
        return false;

    if ((m_state == SuppressingAdjacentCharacterTokens)
        || (m_scriptTagFoundInRequest && isContainedInRequest(canonicalizedSnippetForJavaScript(request)))) {
        request.token.eraseCharacters();
        request.token.appendToCharacter(' '); // Technically, character tokens can't be empty.
        m_state = SuppressingAdjacentCharacterTokens;
        return true;
    }

    m_state = PermittingAdjacentCharacterTokens;
    return false;
}

```

先处理 "/"，处理函数为`canonicalizedSnippetForJavaScript`；然后看处理后的结果是否在 URL 中(`isContainedInRequest`)并且是否 URL 中存在 script 标签(`m_scriptTagFoundInRequest`)；如果不在，则设置当前状态为`PermittingAdjacentCharacterTokens`，即认为它是没有危险的。

接下来处理 "`<1/>alert(0)`"，但是注意到处理函数中，首先检查了状态是否为 PermittingAdjacentCharacterTokens ；这里因为两个字符串 token 是连续的，因此，如果第一个字符串没有检测到在 URL 中，那么第二个字符串根本就不会被过滤！因为当前状态已经被设置为`PermittingAdjacentCharacterTokens`了！

而这个 PoC 则正是利用了这一点。对于 "/"， 在被`canonicalizedSnippetForJavaScript`处理后，将会变成空字符串！而空字符串是不会被认为与 URL 中的子串重复的。

为什么会变空呢？`canonicalizedSnippetForJavaScript`会对传入的 Javascript 代码作一系列处理，其中会调用`isNonCanonicalCharacter`函数检查字符串，将匹配到的字符删去。匹配代码如下:

```
return (c == '\\' || c == '0' || c == '\0' || c == '/' || c == '?' || c >= 127);

```

“/” 正在其中。

两个字符串结合起来，即`/<1/>alert(0)`是一个合法的 Javacript ，可以成功执行。

类似的，我们可以自己构造其他 PoC :

```
<svg><script>0<1>alert(1)</script>

```

这里利用了 "0" 也会被处理为空字符串的特性。

如果构造成

```
<svg><script>0<a></a>alert(1)</script>

```

能否绕过呢？

答案是否定的，当进入其他标签时，当前状态将会设置为`FilteringTokens`，无法绕过检查。

因此，这个绕过利用了 SVG 内标签的特殊解析模式，过滤器的连续过滤的机制，以及`isNonCanonicalCharacter`函数对几个特定字符的匹配后清除。显然，攻击者是看着 XSSAuditor 的源码构造的 PoC。

：）

**_其实，这里`canonicalizedSnippetForJavaScript`是很复杂的，因此，可能存在其他方法使得第一个字符串被认为是允许的(即不在 URL 中)。也正是因为这个，在 Patch 的说明中，最后有一句 "Keep looking in that case."，有可能还会出现类似的绕过。_**

0x03 补丁分析
=========

* * *

补丁其实很简单，如果某个处理后的字符串为空，则既不设置为允许也不设置为禁止。这样既不会干涉后面的处理，也不会增加误判。

具体补丁代码不再分析，其实就只有上面这一点差别。