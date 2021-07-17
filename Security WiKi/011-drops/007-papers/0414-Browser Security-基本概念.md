# Browser Security-基本概念

URL格式：

```
scheme://[login[:password]@](host_name|host_address)[:port][/hierarchical/path/to/resource[?search_string][#fragment_id]]

```

下面详细解释一下各个部分：

#### scheme

`scheme`是协议名不区分大小写，以冒号结尾，表示需要使用的协议来检索资源。

`URL`协议是由IANA（The Internet Assigned Numbers Authority，互联网数字分配机构）与个标准化组织一同管理的。

下面的网址列举出目前有的`scheme`:

[http://www.iana.org/assignments/uri-schemes.html](http://www.iana.org/assignments/uri-schemes.html)

有一些大家很熟悉的例如：`http:、https:、ftp:`等。

在现实中，一些非正式的协议也会被支持，如`javascript`等，这可能会有一些安全隐患，将在后面进行讨论。

在RFC1738中定义`scheme`中只能包含`字母、数字、+、-`，现实中浏览器没有严格的遵守。

IE中会忽略所有的非打印字符ASCII中的0x01到0x1F。

chrome中会跳过0x00即NULL字符。

为了符合RFC1738中的语法规范，每个URL中需要在认证信息前面加入“//”。

在省略“//”字符串的情况下，会造成解析错误。

但在个别情况下不会解析错误，如mailto:user@example.com?subject= Hello+world，由邮件客户端打开的时候不会出错。

但是由于浏览器的特性：

```
1 http:baidu.com/ 这个地址在最新版Chrome、Safari、Firefox、IE中都可以定向到http://baidu.com/ 。
2 javascript://example.com/%0Aalert(1)
<iframe src="javascript://baidu.com/%0Aalert(1)"> 最新版Chrome、Safari、Firefox、IE中都可以弹出1。

```

#### [login[:password]@]

访问资源的认证信息（可选），当没有提供认证信息时，浏览器将尝试匿名获取资源。

绝大部分浏览器在此部分接受几乎所有的字符，有两个例外：

Saferi拒绝`< > { }`字符，Firefox拒绝换行。

#### (host_name|host_address)

服务器地址，正常的URL是DNS指向的域名例如baidu.com，或者IPv4地址如127.0.0.1，或IPv6的地址如[0:0:0:0:0:0:0:1]。

虽然RFC中的IP地址只允许规范的符号，但是大多数应用程序调用的是标准的C库，导致会宽松很多。

http://127.0.0.1/ 这是一个典型的IPv4地址。

http://0x7f.1/ 这是用十六进制表示的127.0.0.1

http://017700000001/ 用八进制表示的127.0.0.1

#### [:port]

服务器端口（可选），他表示采用非默认的协议端口来访问服务，例如http的默认端口80，ftp的21等。

几乎所有的浏览器以及第三方应用使用TCP或UDP作为底层的传输方法。

并依靠TCP和UDP的16位端口号分开一台机器上运行不同服务的通信。

当用户将浏览器定向到http://mail.example.com:25/而25端口是SMTP服务，不是http服务，可能引起安全问题，后面会讨论。

#### [/hierarchical/path/to/resource[?search_string]

路径，用来定位服务器上的资源。

#### [#fragment_id]]

页面的某个位置，其功能是让用户打开某个网页时，自动定位到指定位置上。

在RFC 3986的文档中定义了一个URI的基本结构，定义了没有特殊意义的字符

```
0-9 A-Z a-z - . _ ~

```

以及一些在某些地方可能有特殊意义的字符

```
: / ? # [ ] @ ! $ ' ( ) * + , ; =

```

还有一些字符，当他们直接放在Url中的时候，可能会引起解析程序的歧义。这些字符被视为不安全字符，原因有很多。

```
1 空格：Url在传输的过程，或者用户在排版的过程，或者文本处理程序在处理Url的过程，都有可能引入无关紧要的空格，或者将那些有意义的空格给去掉。
2 引号以及<>：引号和尖括号通常用于在普通文本中起到分隔Url的作用
3 %：百分号本身用作对不安全字符进行编码时使用的特殊字符，因此本身需要编码
4 {}|\^[]`~：某一些网关或者传输代理会篡改这些字符

```

其他的字符都可以用%加16进制字符串（%nn）来表示，包括%它本身。

由于服务器可能需要能够接受那些字符如用户搜索那些字符时，此时就采用%nn的方式来转码后请求。

导致下面三个URL是等效的：

```
1、http://example.com/
2、http://%65xample.%63om/
3、http://%65%78%61%6d%70%6c%65%2e%63%6f%6d/

```

非US-ASCII文本的处理：

```
对于非ASCII字符，需要使用ASCII字符集的超集进行编码得到相应的字节，然后对每个字节执行百分号编码。
对于Unicode字符，RFC文档建议使用utf-8对其进行编码得到相应的字节，然后对每个字节执行百分号编码。

```

如"中文"使用UTF-8字符集得到的字节为0xE4 0xB8 0xAD 0xE6 0x96 0x87，经过Url编码之后得到"%E4%B8%AD%E6%96%87"。

针对域名的编码：

Punycode是一个根据RFC 3492标准而制定的编码系统,主要用于把域名从地方语言所采用的Unicode编码转换成为可用於DNS系统的编码。

Punycode可以防止所谓的IDN欺骗。

目前，因为操作系统的核心都是英文组成，DNS服务器的解析也是由英文代码交换，所以DNS服务器上并不支持直接的中文域名解析。

所有中文域名的解析都需要转成punycode码，然后由DNS解析punycode码。

其实目前所说和各种浏览器完美支持中文域名，只是浏览器软件里面主动加入了中文域名自动转码，不需要原来的再次安装中文域名转码控件来完成整个流程。

例子：中国.cn，用Punycode转换后为：xn--fiqs8s.cn

同样其他语言也是如此。

例如下面的网址列出一个攻击方式，输入想要伪造的网址，选择相近的字符，可以帮你生成一个：

[http://www.irongeek.com/homoglyph-attack-generator.php](http://www.irongeek.com/homoglyph-attack-generator.php)

浏览器本身支持的协议：`http: https: ftp: file:`(之前是local:，用来获取本地文件或者NFS与SMB共享)

第三方应用或者插件支持的协议：`acrobat: callto sip: daap: itpc: itms: mailto: news: nntp: mmst: mmsu: msbd:rtsp:`等等。

伪协议：一些保留协议用来调用浏览器脚本引擎或者函数，没有真正取回任何远程内容，也没有建立一个独立的文件。

如：`javascript: data:`

data协议例子：`data:text/html;base64,PGlmcmFtZS9vbmxvYWQ9YWxlcnQoMSk+`

封装的伪协议：`view-source:http://www.example.com/`

`view-source:`是由Chrome与Firefox提出的用来查看当前页面源代码的协议。

其他的类似协议还有`jar: wyciwyg: view-cache: feed: hcp: its: mhtml: mk: ms-help: ms-its: ms-itss:`