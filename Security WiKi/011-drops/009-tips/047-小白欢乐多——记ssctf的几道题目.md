# 小白欢乐多——记ssctf的几道题目

二哥说过来自乌云，回归乌云。Web400来源于此，应当回归于此，有不足的地方欢迎指出。

0x00 Web200
===========

* * *

先不急着提web400，让我们先来看看web200的xss。

Url：[http://960a23aa.seclover.com/index.php?xss=xxx](http://960a23aa.seclover.com/index.php?xss=xxx)

显然参数xss是要上payload。先大概看一眼都过滤了什么。

![p1](http://drops.javaweb.org/uploads/images/cc5b3cc99991470a7382c1fbb543efa905b500b7.jpg)

可以发现尖括号和冒号都过滤成下划线了，并且尝试了好几种姿势也无法绕过。

再看看其他的过滤规则。

![p2](http://drops.javaweb.org/uploads/images/f4759c340d899b50c22f0917418f193d000f5a88.jpg)

基本都过滤了，就剩下一个孤零零的1了。

![p3](http://drops.javaweb.org/uploads/images/8e4e6cb177e0d56c20d32a0471b31ebf0aac16fb.jpg)

再祭出《web前端安全》提到的奇妙payload，注意到onerror中的on被吃掉了。

连打多个on也是没有用的，联想到以前玩sql注入的经验，oonn这样的形式是能打出on来的。看到这结果的存在，顿时感觉来了希望。

![p4](http://drops.javaweb.org/uploads/images/7b201d96c29c32f409a7e5f4073a514d1aa442c4.jpg)

这种形式似乎已经很接近了，但是万恶的下划线仍旧无法解决，一度陷入死局了。

后来，学长说仔细看看源码，那谁写过网页他或许能看出什么。

![p5](http://drops.javaweb.org/uploads/images/6ab13c12a971f252f0fb3ca2f5eba71ec835a25c.jpg)

注意到开头一句，似乎平时我不是那么写的，又注意到页面有css，就跑偏到了[http://drops.wooyun.org/web/11539](http://drops.wooyun.org/web/11539)这篇文章，但是似乎并没有什么用。百度了一下第一句话。

![p6](http://drops.javaweb.org/uploads/images/014051da5a74489579e4cc7af6035cc2a3ae04db.jpg)

！！？识别和加载，赶紧试了一下。

AngularJS 的表达式是写在双大括号内：`{{ expression }}`。

![p7](http://drops.javaweb.org/uploads/images/deb9e992cb4f1551e1349ff2f0b42f6b4a96e946.jpg)

识别了！

![p8](http://drops.javaweb.org/uploads/images/1648bc30989068266e30fb53fa88944d43f158b3.jpg)

确定了版本号以后，队友就找到一发payload。

经过加工：`{{'a'.coonnstructor.prototype.charAt=[].join;$evevalal('x=1} } };aleonrt(1)//');}}`

![p9](http://drops.javaweb.org/uploads/images/dc2c6e93079e7e1f19f4172c75cd3f1492d8d1cb.jpg)

弹弹弹了:)

0x01 Misc：饥荒_MC
===============

* * *

在web400前，那就再提提misc的饥荒_MC，这是我见过的最有趣的ctf题目没有之一，之前听说了好久的websocket也第一次见到实例。

打开一看，似乎是个小游戏。

![p10](http://drops.javaweb.org/uploads/images/eabc8b94f1cc9279eb705aae8e3ea2319e1b5a41.jpg)

一般出现在ctf里的游戏不能轻视。

第一关一切平和，直通第二关。

![p11](http://drops.javaweb.org/uploads/images/820d01e0e20de5fbc43568c8b10209f94ba14fcc.jpg)

第二关，似乎要找到一个key才能通关，顿感道路坎坷。Key是什么也没说，只说空格是个功能按键，那就先跑跑全图呗。跑了一会感觉太烦了，找队友写了个按键精灵来模拟。

![p12](http://drops.javaweb.org/uploads/images/a7a99dc27e4d285299a35ba6b26716c6945202d1.jpg)

但是跑完这张图也没能进去，就想会不会key在第一关，要知道这种游戏向来不按常理出牌。

就开始跑第一关，突然发生了一件奇妙的事情，一卡我突然传送到了一个奇怪的地方。

![p13](http://drops.javaweb.org/uploads/images/18aaaf9100785d57b3a425ad7abf7912ea6d1d46.jpg)

似乎由于不明原因，我突然跳关到了第三关。（后来想想可能是时间竞争？）

第三关是个砍树关，由于已经靠按键精灵连过两关，思路已经被定势了，已经听不进学长说什么js本地调试了，义无反顾的跳进坑里。要砍9999个木头来做木镐（一切始于木头），发现要按住空格一秒才能砍到一个木头，感觉似乎哪里不对，然而还是找个东西按着空格。。。直到5分钟后，发现被管理员踢掉了，才最终确定这是个坑，不可能通过小伎俩来过了。只得打开js代码，幸亏寒假看了一下《js-dom编程艺术》。

![p14](http://drops.javaweb.org/uploads/images/04366bf7517bc986f92c344885591a409865e1a2.jpg)

![p15](http://drops.javaweb.org/uploads/images/55259dcc7ef4fe275bca6457c8253050092c82d4.jpg)

参数有个isReady，要加载完全部的图片才能运作，打开firebug，把图片另存为，放到相应位置，再写个html调用game.js(直接档网页上的就行)

![p16](http://drops.javaweb.org/uploads/images/a264c9baef7920553d5922a84c3a750aa43c5bdb.jpg)

突然一下就开启上帝视角了，毫不犹豫的跳关到level 4，却发现服务器提示你的宝石剑在哪？然后就被踢了。观察了一下代码，似乎应该有一只boss。

![p17](http://drops.javaweb.org/uploads/images/940e1811bb710f424663539d4d78a4e185b3eded.jpg)

大概长成这样。

观察代码

![p18](http://drops.javaweb.org/uploads/images/4e708021bdf4ce7098ffb077af6b744e9a490778.jpg)

实在不行，我就召唤一只boss出来，然后burp抓包，把玩家改为boss，但是似乎没有什么用，应该是在服务器端做的验证。

注意到hero的几种图片。

![p19](http://drops.javaweb.org/uploads/images/0d4467de423ed69d2f606daefea42e9192fdd4cf.jpg)

![p20](http://drops.javaweb.org/uploads/images/3981f320266eb89c064a1dc5f25c9185dcaa4d0a.jpg)

似乎这两种状态我都没有见到过，感觉哪里不对，再研读代码。

![p21](http://drops.javaweb.org/uploads/images/72ae3d8a18672df7e907ecdf6d133930d34f721d.jpg)

木头关下面有钻石关，并且注意到最后一关，似乎有两个点会自杀，幸亏没有过去。（第二关前面的门是假门，根本不存在key）

找到了木头采集函数修改一下。

![p22](http://drops.javaweb.org/uploads/images/ccb01c61eb260746e9284c442697342b2582d5a5.jpg)

直接9999，木镐get。

进入钻石关

这个似乎和木头关的函数差不多。（图片已经修改过）

![p23](http://drops.javaweb.org/uploads/images/7641dd482fae739c2eb58433cff9c416f5d37d97.jpg)

当然直接9999被踢掉线了，尝试了一下似乎50是极限了。那就要点200下，而且感觉上传时间还有间隔限制，于是又打开了恋恋不舍的按键精灵。虽然慢，还是能在1，2分钟里完成任务。

终于拿到钻石剑了，如今我已天下无敌，走，捅boss去。

![p24](http://drops.javaweb.org/uploads/images/a27a6a7315d81b8900750478d32d77871c2fce95.jpg)

系统提示。

![p25](http://drops.javaweb.org/uploads/images/64678a2f5c4f459de4a71f48bf167491927773ec.jpg)

要捅15下boss或者杀5个人，做为一个wow的pve休闲玩家我当然选择捅15下boss（注意短距离武器那句话，结合自杀点是把弓箭）。

然而发现boss近距离一刀我就躺了，远程扣血导致pvp的难度也挺高（除非送人头）。循环往复几次，终于感觉按键精灵的速度不能满足我了（主要是发现学长在我旁边一下就拿到钻石剑了）。就把条件注释掉，发现上传速度不再卡顿，但是按200下还是太烦，最终又打开了按键精灵。（这里其实可以写个循环，论思维定势的可怕）。

既然近距离一刀秒，我就修改了攻击范围，又为了方便瞄准，又把boss图像修改了。

![p26](http://drops.javaweb.org/uploads/images/37620088a004e247015751c8f038938cadad4483.jpg)

大概是这样，可惜pve休闲玩家的水准已经不足以让我靠走位捅到它15下了。

最终在学长提示数据交互的时候终于恍然大悟。

![p27](http://drops.javaweb.org/uploads/images/b7ab095e79d0114e66771794df6a609d1b43bbbc.jpg)

把攻击地址直接改为boss地址，然后找个阴暗的小角落就ok了。

0x02 Web400
===========

* * *

终于到了web400，页面打开看一眼（url：[http://b525ac59.seclover.com/](http://b525ac59.seclover.com/)）

![p28](http://drops.javaweb.org/uploads/images/b0bb069c07d83d1a030b91c6a9eb760244a29aef.jpg)

![p29](http://drops.javaweb.org/uploads/images/dd50d3e61ee595f7c74a081e399304365e8502e1.jpg)

一个github的图标和不要去爆破的提示，点开一看是github第三方授权的页面。感觉应该不会是github认证的漏洞。

![p30](http://drops.javaweb.org/uploads/images/0a361cbea4fb2454a5ce191f4d2754c60be598f3.jpg)

绑定后样子是这样，一张github头像的图片，github的uid，一开始不知道为什么名字那边是none，结合find flag man，猜测最后的flag应该会输出在name的位置，网络也只请求了一张图片。

![p31](http://drops.javaweb.org/uploads/images/6621852d2db98f81b172a253cc064dbf4296efde.jpg)

又一头雾水不知道该怎么办了。

知道burp抓包的时候，把cookie都去掉后发现了这个。

![p32](http://drops.javaweb.org/uploads/images/39b03bde33c353fd867692b9d66affb499c93e70.jpg)

Flask似乎有点眼熟，感觉在哪里看到过，于是翻找了一下。

![p33](http://drops.javaweb.org/uploads/images/f74123792636a5533790d4af1eb42415161e7dba.jpg)

就在几天前的乌云知识库发表的文章，文章提到了控制模板内容来进行任意代码执行。再看页面的情况，感觉确实挺像那么回事的，模板里的内容都是我github上的，那么接下来就是找到可控点，来调用python了。接下来就一直跑偏到那张图片，我一直以为图片是可控内容，但是捣鼓了半天也没什么用。后来点开github的设置突然恍然大悟，明白了为什么name是none。

![p34](http://drops.javaweb.org/uploads/images/cd2f08fa0db8996c2b25716701ee626ee914c464.jpg)

因为我根本没设置名字Orz。赶紧把名字设成{{7*7}}。

![p35](http://drops.javaweb.org/uploads/images/c94d12de4f287eee7c325be479b370d333200fcb.jpg)

发现被解析了（和那道xss神似的方法）。

原文作者的payload不能直接使用，对python的内置函数也不熟悉，只得翻阅官方手册。

![p36](http://drops.javaweb.org/uploads/images/e4847aadabc7317fbc7ee7c877059400a543e884.jpg)

找到了打开文件的方法，感觉这个靠谱，试了一下，似乎没有什么用，于是去github上面搜索了一下内置的使用方法。

![p37](http://drops.javaweb.org/uploads/images/447aba565c9e341d813a68bef1e20c29a15f3d3a.jpg)

问题太多一下子翻不过来，注意到有10个用户用了这个奇葩名字，就打开看了一下。

![p38](http://drops.javaweb.org/uploads/images/6885ef424eee17c679b90388d92a5e06efb66d76.jpg)

！！看我都找到了什么，复制一句看的顺眼的，就爆flag了。

![p39](http://drops.javaweb.org/uploads/images/ae89c6e0de48ea2980e10d3ef962382c3dfe10cd.jpg)

这个应该算是官方福利吧，毕竟不是什么人都会写payload的。

以上，完。没有什么太多的技术干货，基本都是自己逗逼的纪实，不管审核过没过，记录一下还是值得的。