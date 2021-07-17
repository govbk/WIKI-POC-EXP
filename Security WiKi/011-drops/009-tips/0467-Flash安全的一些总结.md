# Flash安全的一些总结

整理了下Flash安全相关的知识，后面会再完善 

### 一、先来说crossdomain.xml这个文件

* * *

flash如何跨域通信，全靠crossdomain.xml这个文件。这个文件配置在服务端，一般为根目录下，限制了flash是否可以跨域获取数据以及允许从什么地方跨域获取数据。

比如下面的列子： 1、www.a.com域下不存在crossdomain.xml文件，则不允许除了www.a.com域之外的其他任何域下的flash进行跨域请求。

2、www.a.com域下存在crossdomain.xml文件，如若配置 allow-access-from 为www.b.com，则只允许www.b.com域下的flash进行跨域请求，以及来自自身域www.a.com的网络请求。crossdomain.xml需严格遵守XML语法，有且仅有一个根节点cross-domain-policy，且不包含任何属性。在此根节点下只能包含如下的子节点：

```
site-control
allow-access-from
allow-access-from-identity
allow-http-request-headers-from

```

#### site-control

早期的flash允许从其他位置载入自定义的策略文件，目前最新版的flash在接受自定义的策略文件之前会去检查主目录的crossdomain.xml来判断是否接受自定义策略文件。该选项就由site-control进行控制。

不加该选项时，默认情况下flash不加载除主策略文件之外的其他策略文件，即只接受根目录下的crossdomain.xml，这样可以防止利用上传自定 义策略文件进行的攻击。如果需要启用其他策略文件，则需要配置permitted-cross-domain-policies属性，该属性有以下五个 值： none: 不允许使用loadPolicyFile方法加载任何策略文件，包括此主策略文件。

```
master-only: 只允许使用主策略文件[默认值]。
by-content-type:只允许使用loadPolicyFile方法加载HTTP/HTTPS协议下Content-Type为text/x-cross-domain-policy的文件作为跨域策略文件。
by-ftp-filename:只允许使用loadPolicyFile方法加载FTP协议下文件名为crossdomain.xml的文件作为跨域策略文件。
all: 可使用loadPolicyFile方法加载目标域上的任何文件作为跨域策略文件，甚至是一个JPG也可被加载为策略文件！

```

例子：

```
<site-control permitted-cross-domain-policies="by-content-type" > 

```

允许通过HTTP/HTTPS协议加载http头中Content-Type为text/x-cross-domain-policy的文件作为策略文件

```
<site-control permitted-cross-domain-policies="all" > 

```

允许加载任意文件作为策略文件

#### allow-access-from

该选项用来限制哪些域有权限进行跨域请求数据。

allow-access-from有三个属性

```
domain：有效的值为IP、域名，子域名代表不同的域，通配符*单独使用代表所有域。通配符作为前缀和域名进行组合代表多个域，比如*.weibo.com,代表weibo.com所有的子域。
to-ports：该属性值表明允许访问读取本域内容的socket连接端口范围。可使用to-ports="1100,1120-1125"这样的形式来限定端口范围，也可使用通配符（*）表示允许所有端口。
secure：该属性值指明信息是否经加密传输。当crossdomain.xml文件使用https加载时，secure默认设为true。此时将不允许flash传输非https加密内容。若手工设置为false则允许flash传输非https加密内容。

```

例子

http://a.com/crossdomain.xml文件内容如下

```
<cross-domain-policy > 
    <allow-access-from domain="*.b.com" secure="true" />
</cross-domain-policy > 

```

允许所有qq.com的子域通过https对t.qq.com域进行跨域请求。

#### allow-access-from-identity

该节点配置跨域访问策略为允许有特定证书的来源跨域访问本域上的资源。每个allow-access-from-identity节点最多只能包含一个signatory子节点。

#### allow-http-request-headers-from

此节点授权第三方域flash向本域发送用户定义的http头。

allow-http-request-headers-from包含三个属性：

```
domain：作用及参数格式与allow-access-from节点中的domain类似。
headers：以逗号隔开的列表，表明允许发送的http头。可用通配符（*）表示全部http头。
secure：作用及用法与allow-access-from节点中的secure相同。

```

注：Flash 在自定义HTTP头中无法使用下列请求标题，并且受限制的词不区分大小写（例如，不允许使用 Get、get 和 GET）。 另外，如果使用下划线字符，这也适用于带连字符的词（例如，不允许使用 Content-Length 和 Content_Length）：

```
Accept-Charset、Accept-Encoding、Accept-Ranges、Age、Allow、Allowed、Authorization、Charge-To、Connect、Connection、Content-Length、Content-Location、Content-Range、Cookie、Date、Delete、ETag、Expect、Get、Head、Host、Keep-Alive、Last-Modified、Location、Max-Forwards、Options、Post、Proxy-Authenticate、Proxy-Authorization、Proxy-Connection、Public、Put、Range、Referer、Request-Range、Retry-After、Server、TE、Trace、Trailer、Transfer-Encoding、Upgrade、URI、User-Agent、Vary、Via、Warning、WWW-Authenticate 和 x-flash-version。

```

### 二、web应用中安全使用flash

* * *

设置严格的crossdomain.xml文件可以提高服务端的安全性，在web应用中也会经常使用flash，一般是通过<object>或者<embed>来进行调用，例如下面：

```
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0"name="Main" width="1000" height="600" align="middle" id="Main" >
<embed flashvars="site=&sitename=" src='Loading.swf?user=453156346&key=df57546b-c68c-4fd7-9f9c-2d105905f132&v=10950&rand=633927610302991250' width="1000" height="600"align="middle" quality="high" name="Main" allowscriptaccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" >
</object > 

<embed src="http://www.xxx.com/Loading.swf" allowScriptAccess="sameDomain" type="application/x-shockwave-flash>

```

flash是直接可以执行js代码的，所以在web应用中如果使用不当也会很危险，所以flash使用下面两个属性来保证引用flash时的安全性。

allowScriptAccess 和 allowNetworking

allowScriptAccess用来控制flash与html的通讯，可选的值为：

```
always //对与html的通讯也就是执行javascript不做任何限制
sameDomain //只允许来自于本域的flash与html通讯，这是默认值
never //绝对禁止flash与页面的通讯

```

allowNetworking用来控制flash与外部的网络通讯，可选的值为：

```
all //允许使用所有的网络通讯，也是默认值
internal //flash不能与浏览器通讯如navigateToURL，但是可以调用其他的API
none //禁止任何的网络通讯

```

在allowNetworking设置为internal时，下面API将会被禁止使用：

```
fscommand()
navigateToURL()
ExternalInterface.call()

```

在allowNetworking设置为none时，下面API将会被禁止使用：

```
sendToURL()
FileReference.download()
FileReference.upload()
Loader.load()
LocalConnection.connect()
LocalConnection.send()
NetConnection.connect()
URLStream.load()
NetStream.play()
Security.loadPolicyFile()
SharedObject.getLocal()
SharedObject.getRemote()
Socket.connect()
Sound.load()
URLLoader.load()
XMLSocket.connect()

```

在web应用中使用flash的时候一般通过设置这两项即可保证安全性，如果在web应用中使用的flash为用户可控，强烈建议这两项的设置值为

```
allowScriptAccess=never allowNetworking=none

```

### 三、flash安全编程

如果web应用中调用flash时设置的allowScriptAccess为never、allowNetworking为none，即使flash文件 本身存在漏洞也可以忽略。不过事实上大部分web应用不会设置这两项属性，甚至会设置的不安全，比如allowScriptAccess为always、 allowNetworking为all。所以在进行flash开发的时候就要考虑好安全性。

flash编程不安全可导致两方面的漏洞：

```
1、通过ExternalInterface.call()执行javascript代码 
2、通过loadMovie()等方式可以载入外部flash文件执行 

```

这两类问题都是需要通过参数接收外面传入的数据，在flash内部没有对数据进行严格的控制造成的。

例子：

```
this.movieName = root.loaderInfo.parameters.movieName;
this.flashReady_Callback = "SWFUpload.instances[\"" + this.movieName + "\"].flashReady";
ExternalCall.Simple(this.flashReady_Callback);
public static function Simple(arg0:String){
    ExternalInterface.call(arg0);
    return;
}

```

接收到外部传入的movieName没有进行处理，最后通过ExternalInterface.call()进行执行，这样就能够执行任意的javascript代码，如果在调用flash的时候设置的不够安全就是XSS漏洞。

所以在flash编程中如果需要通过参数接收外部传入的数据，一定要对数据进行严格的检查，这样才能保证flash安全性。

参考文档：

Flash应用安全规范[http://www.80sec.com/flash-security-polic.html](http://www.80sec.com/flash-security-polic.html)

flash跨域策略文件crossdomain.xml配置详解[http://hi.baidu.com/cncxz/blog/item/7be889fa8f47a20c6c22eb3a.html](http://hi.baidu.com/cncxz/blog/item/7be889fa8f47a20c6c22eb3a.html)

Cross-domain Policy File Specification[http://www.senocular.com/pub/adobe/crossdomain/policyfiles.html](http://www.senocular.com/pub/adobe/crossdomain/policyfiles.html)