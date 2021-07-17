# 调皮的location.href

0x00 背景
-------

* * *

随着水瓶月的到来，在祖国繁荣昌盛的今天，web系统的浏览器端也越来越重，很多的功能逻辑都放在了js中，前端的漏洞也越来越多。 我今天就说说location.href跳转的一些问题。

前端跳转常见的代码形式是:

```
location.href = 'http://www.baidu.com';

```

在前端js中有可能是这样:

```
var hash = location.hash;
if(hash)
{
var url = hash.substring(1);
location.href = url;
}

```

0x01 常见的跳转漏洞
------------

* * *

什么是跳转漏洞？突破了系统预期的跳转，就是跳转漏洞。大多数系统的预期是跳转到当前域url的http访问。

以上面的代码为例，hash值为攻击者可控，常见的漏洞形式可以为：

```
http://yigezangpao.com/test.html#http://jiajiba.taobao.com

```

这个地址会利用信任关系跳转到钓鱼网站

```
http://yigezangpao.com/test.html#javascript:alert(document.cookie)

```

这个会跳转到浏览器端的javascript协议而执行js，成了一个反射的xss，而且浏览器端的xssfilter对它无效

0x02 跳转漏洞的危害
------------

* * *

可能的危害场景如下：

受害用户被骗点击进入了钓鱼站，可导致家破人亡妻离子散被网友拉黑……

在一些sns网站中，点击第三方网站时，可能会有安全提示，恶意网址则可利用信任域的身份，绕过了检查。

很多app带有二维码扫描功能，对本域或白名单域会不做提示，直接跳转访问。

当你扫描一个二维码的时候，你可能已经点击了一个恶意或含有某种攻击代码的网页javascript为协议的反射型xss。

一般的社区发表链接时，不会自动识别浏览器的伪协议，不会形成可点击的链接，但是利用跳转漏洞，则可以欺骗目标用户打开某个浏览器伪协议……

0x03 目前的防护的一些问题
---------------

* * *

我见到的常见的有防护有：

```
给变量前加"/"或者只有"/"开头的才跳转
替换变量中的":"
替换"http://"
匹配域名白名单
……

```

这几类或多或少有些问题，如下：

对于在变量前加/的，或者/开头才跳转的，他们预期的是控制在本域下。但当

```
location.href = "//diaoyuwangzhan.com"

```

时，浏览器会把后面的识别成一个标准的url来跳转，而不是一个绝对路径。

对于允许第三方跳转的，匹配域名白名单的，一定要写好正则的逻辑严格匹配url的标准格式，否则可能会被

```
http://yigezangpao.com.jiajiba.taobao.com
http://yigezangpao.com@jiajiba.taobao.com
http://jiajiba.taobao.com/yigezangpao.com

```

等绕过

对于替换”:“的防护：

twitter曾经犯过这样的错，twitter的程序员是这样改的：

```
var c = location.href.split("#!")[1];     if (c) {     window.location = c.replace(":", "");     } else {     return true;     }

```

结果又被如下链接干：

```
http://twitter.com/#!javascript::alert(document.domain); 

```

比第一次多了个：

因为replace()函数的第一个参数，按照规范中的方式，是要用正则写的。如果第一个参数是一个字符串，javascript默认只会替换掉他找到的第一个字符

0x04 比杨幂还神奇
-----------

* * *

对于上面的替换":"的方案，如果完全替换，是不是就没有问题了呢？

如果你曾觉得你的女友不可理喻，那么当我告诉你有一个东西的不可理喻程度已经达到你女友的50%时，你一定会惊呼，”天呐，竟然还有这么变态的东西！！！“ 不错，你猜的非常对，这个不可理喻的东西就是ie浏览器

如前文的例子，如果对方已经完全替换":"，你试试在ie中访问如下链接

```
http://yigezangpao.com/test.html#javascript&#x3A;alert(1)

```

也就是

```
location.href = "javascript&#x3A;alert(1)"

```

你会惊奇的发现弹了，`'&#x3A;'是':'`的html编码，至于为什么会这样我不知道，我的是ie11，其他版本没测

0x05 解决方案
---------

* * *

对于不允许跳转到第三方的，可以使用location.pathname来跳转，用这个跳转绝对靠谱。

有句成语”path就不是共产党员“就是修饰这个属性的，既然不是共产党员，说明path是靠谱的。

对于允许跳转到第三方的，做好白名单的检查规则。