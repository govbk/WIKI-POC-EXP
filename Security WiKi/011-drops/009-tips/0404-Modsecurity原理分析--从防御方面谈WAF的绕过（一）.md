# Modsecurity原理分析--从防御方面谈WAF的绕过（一）


0x00 背景知识
---------

* * *

1.  一说到WAF，在我们安全工作者，或者作为普通的白帽子来说，就很头疼，因为好多时候，我们发到服务端的恶意流量都被挡掉了，于是就产生了各种绕“WAF”的话题，绕来绕去，也就无非那么多种，而且大多都是基于URLDecode的方式。
    
2.  虽然我的文章也会讲绕过，虽然也是那么几种，但是我会从防御的方面展示WAF规则的强大。
    
3.  笔者再次强调，如果你只是想学习WAF的绕过，我建议还是不要跟我的帖子了，我的目的还是主要帮助好多人去搭起整个框架，从而在谈绕过。
    

0x01 从Modsecurity模块谈起
---------------------

* * *

1.  问过圈内的好多朋友“知道WAF吗？”，他们会明确告诉我，“知道”。但是当我给他们说起，Modsecurity这个Apache的模块的时候，他们就开始摇头。其实WAF的事实标准就是开源的Modsecurity。并且Modsecurity已经被开发成了Apache的一个模块，而且这个模块在反向代理的工作状态下，实际上是可以保护任何Web程序的。
    
2.  其实，Modsecurity的威力就在于它的规则语言上，这种语言是配置指令和应用到HTTP请求和响应的一种简单编程语言的组合，其实按理说这种语言应当被称作Lua。一般情况下，Modsecurity的最终结果都是具体到一个动作的执行，比如允许请求通过，或者将日志记录到Modsecurity_audit.log或者httpd的log文件中。
    
3.  以下就是我本地的Modsecurity模块，具体如下图所示[![](http://static.wooyun.org/20141107/2014110709383980035.jpg)](http://drops.wooyun.org/wp-content/uploads/2014/11/12.jpg)
    
4.  从上图就可以得知，这些规则库（只是截取了一部分）几乎构成了Modsecurity的全部，其中红箭头所指的方向，就是防止我们SQL注入的一些规则，其中的规则多达100多条，我们先大体看下他的规则，从宏观上有个大体的认识，为后期的SQL注入绕过储备必要的知识。
    

[![](http://static.wooyun.org/20141107/2014110709384016298.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/219.png)

1.  从上图中我们也可以轻易看到，我们进行SQL注入攻击时常用的payload，不好意思这些都在规则库考虑之内。下面先说下Modsecurity的规则库吧。

0x02 Modsecurity 处理事件的5个阶段
--------------------------

* * *

1.  请求头阶段（Request-Headers） 请求头阶段，又称作“Phase 1”阶段。处于在这个阶段的Modsecurity规则，会在Apache完成请求头后，立即被执行。到这个时候还没有读取到请求体，意即并不是所有的请求的参数都可以被使用。
    
2.  请求体阶段（Request-Body） 请求体阶段，又称作“Phase 2”阶段。这个阶段属于输入分析阶段，大部分的应用规则也不会部署于这个阶段。这个阶段可以接收到来自于正常请求的一些参数。在请求体阶段，Modsecurity支持三种编码方式，具体编码方式如下：
    

> (1)Application/x-www-form-urldecode
> 
> (2) Multipart/form-data
> 
> (3) Text/xml

1.  响应头阶段（Response_Headers） 相应头阶段，又称作“Phases3”阶段。这个阶段发生在响应头被发送到客户端之前。在这个阶段，一些响应的状态码（如404）在请求的早起就被Apache服务器管理着，我们无法触发其预期的结果。
    
2.  响应体阶段（Request_Body） 响应头阶段，又称作“Phase4”阶段。这个阶段可以运行规则截断响应体。
    
3.  记录阶段（Logging） 记录阶段，又称作“Phase5”阶段，写在这个阶段的规则只能影响日志记录器如何执行，这个阶段可以检测Apache记录的错误信息，在这个阶段不能够拒绝或者阻断连接。因为在这个阶段来阻断用户的请求已经太晚了。
    
4.  为了更加直观的展示Apache加载上Modsecurity模块后，运行阶段，我做了一个流程图：
    

[![](http://static.wooyun.org/20141107/2014110709384010406.jpg)](http://drops.wooyun.org/wp-content/uploads/2014/11/31.jpg)

0x03 Modsecurity的Rule规则详解
-------------------------

* * *

一、为了更好的了解Modsecurity的工作机制，我们来分析下SecRule的规则，具体规则如下： SecRule variable operator [Actions] 1 variable变量：用来描述哪个变量应当被检查； 2 operator变量：用来描述如何检查。Operator实际上正则表达式，但是Modsecurity自身会提供很多的Operator，利用的时候直接使用”@operator”即可。 3 Actions：第三部分为可选的部分。描述当操作进行成功的匹配一个变量变量时，下一步该如何去处理。

二、为了更直观的表现SecRule的规则，给出一个具体的事例如下这条规则取自Modsecurity_crs_41_sql_injection_attacks.conf中：

```
SecRule REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|!REQUEST_COOKIES:/_pk_ref/|REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/* "(?i:(?i:\d[\"'`´’‘]\s+[\"'`´’‘]\s+\d)|(?:^admin\s*?[\"'`´’‘]|(\/\*)+[\"'`´’‘]+\s?(?:--|#|\/\*|{)?)|(?:[\"'`´’‘]\s*?\b(x?or|div|like|between|and)\b\s*?[+<>=(),-]\s*?[\d\"'`´’‘])|(?:[\"'`´’‘]\s*?[^\w\s]?=\s*?[\"'`´’‘])|(?:[\"'`´’‘]\W*?[+=]+\W*?[\"'`´’‘])|(?:[\"'`´’‘]\s*?[!=|][\d\s!=+-]+.*?[\"'`´’‘(].*?$)|(?:[\"'`´’‘]\s*?[!=|][\d\s!=]+.*?\d+$)|(?:[\"'`´’‘]\s*?like\W+[\w\"'`´’‘(])|(?:\sis\s*?0\W)|(?:where\s[\s\w\.,-]+\s=)|(?:[\"'`´’‘][<>~]+[\"'`´’‘]))" "phase:2,capture,t:none,t:urlDecodeUni,block,msg:'Detects basic SQL authentication bypass attempts 1/3',id:'981244',tag:'OWASP_CRS/WEB_ATTACK/SQL_INJECTION',logdata:'Matched Data: %{TX.0} found within %{MATCHED_VAR_NAME}: %{MATCHED_VAR}',severity:'2',setvar:'tx.msg=%{rule.id}-%{rule.msg}',setvar:tx.sql_injection_score=+1,setvar:tx.anomaly_score=+%{tx.critical_anomaly_score},setvar:'tx.%{tx.msg}-OWASP_CRS/WEB_ATTACK/SQLI-%{matched_var_name}=%{tx.0}'"

```

2.1 该规则请求的参数包括所有的Cookie信息（Request_Cookies以及!Request_Cookies）以及cookie的名称（Request_name）,Post参数（Args）以及Post参数的名称（Args_names）,当然还有其中的XML文件（XMLL：/*）

2.2 其中最多的还是那一堆的正则表达式，正则表达式我就不给大家分析了。算了还是贴个图吧：[![](http://static.wooyun.org/20141107/2014110709384047288.jpg)](http://drops.wooyun.org/wp-content/uploads/2014/11/5.jpg)

2.3 使用到请求体阶段“Phase2”阶段

2.4 根据正则表达式来匹配每个对象，并且已经为正则表达式开启了捕获的状态（capture）

2.5 匹配之前先让请求数据经历多种变换（t:none来表示）。经过的主要变换有urlDecode Unicode。前者的主要作用是清除之前设置的所有转换的函数和规则。后者主要是进行URL的编码。

2.6 如果匹配成功后，将会阻塞这个请求（block）。并且抛出提示信息（msg）。一次表明这是一个SQL注入的攻击，并且将这条注入攻击添加到规则当中。同时区分攻击类型的唯一性的标签（tag）也将添加到日志当中。

2.7 该规则同时还被分配了一个唯一性的ID（ID：981244）