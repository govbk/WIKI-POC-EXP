# 关于zANTI和dsploit两款安卓安全工具的对比

0x00 前言
-------

* * *

随着科技发展，手机的智能化也逐渐的进步。同时移动终端又成为了黑客们热衷与捣腾的一块乐土。

如今几乎每人一部智能手机，让手机病毒和针对手机软件攻击的漏洞是如鱼得水一般。

下面我就给各位对比一下两款比较有名的安卓下的安全工具。

0x01 主题
-------

* * *

这两款软件是zANTI和dsploit，相信后者基本是烂大街的级别了，我们的CCAV也曾经针对过手机安全的问题放过新闻，里面的安全专家所展示的就是dsploit这款软件的功效，而zANTI却还算是比较低调的。

首先说一下dsploit,这款由BackBox Linux赞助的开源软件。使用时候要安装完整的busy box。

官网：[http://www.dsploit.net/](http://www.dsploit.net/)

现在官网挂出的是两个版本,一个是1.0.31的完整版本。另外一个是1.1.3的测试版本。测试版在完整版的基础上加入了Metasploit框架，使得在检测后能实现攻击的可能。（这框架要下载。。。我总是下一半就连接错误。。）

那么我们来看看1.1.3版本的界面

![2014070616012597638.png](http://drops.javaweb.org/uploads/images/fffe6aeb1d53c3c0ee00c15ee30608cd753b8481.jpg)

可以看出还是比1.0.31有所改进的啊。。

然后我们进入到其中一个目标（我点的是路由）可以看它能够干的事情，像是什么ping一下了啊，扫描系统信息啊，开放端口什么的。

其中还有一个取得路由权限的东东，这玩意支持的路由shell比较少。。。

![2014070616051048947.png](http://drops.javaweb.org/uploads/images/a1947cd980388fb3d615229bd56440da14b52bca.jpg)

![2014070616053733375.png](http://drops.javaweb.org/uploads/images/7d1a691426cc41f7bb69db1dc2d9b1eb6409a84e.jpg)

![2014070616055720908.png](http://drops.javaweb.org/uploads/images/b0bf2d54ad7fa97f93c6825f83793ad94aa67494.jpg)

![2014070616062726722.png](http://drops.javaweb.org/uploads/images/1291567e00774ba315484764d3fde28e3f51d43b.jpg)

然后我们看看它主要的功能，也就是中间人攻击。大概功能有图得到

![2014070616075351858.png](http://drops.javaweb.org/uploads/images/98ecfcb6247d7b0b6f9c736dbc14a0c3eedcdb3f.jpg)

![2014070616081534660.png](http://drops.javaweb.org/uploads/images/2409cebec3bd1bb27f277c0611a29cbb84a1bfd9.jpg)

然后我就用我的百度帐号做了下测试，在我另外一个手机上登录帐号后，通过它的会话劫持，成功的劫持了我的cookis并登录了上去

![2014070616100390150.png](http://drops.javaweb.org/uploads/images/c334a00ddd7c9c0a573e32a8f47aea485d83600c.jpg)

![2014070616132357400.png](http://drops.javaweb.org/uploads/images/a9c3851e91755ce5ae59a733a56c2d8f30579e1c.jpg)

接下来我们来看看zANTi 这一款软件，它是由以色列移动安全公司Zimperium开发的。凯文米勒大大也参加了这个公司。zANTi 软件功能和dsploit是不相上下的，甚至还比它要多一点。zANTi 因为是公司生产而非个人制作，因此需要完整功能是需要购买的，当然还有一个渠道是注册用户（我试了。。他给我发了封全英语的邮件回来，让我打电话和他们谈谈云云。以我的半吊子英文功底，我觉得还是不要回比较好）。在启动软件后，需要连接Zimperium的服务器后才能开始使用（如果是注册用户或是付费用户，连接后将能够使用Zimperium服务器上强大的爆破密码文件和漏洞测试程序），还要下载大约5个文件。不用装busy box。

这是登录的界面

![2014070616203959030.png](http://drops.javaweb.org/uploads/images/4b54e761b035dab371a2ddaa9c1c238f1a61908f.jpg)

在完成了连接后，需要对网络进行一次扫描发现，其中我最喜欢的的就是它的扫描了，zANTi 使用的扫描器是Namp，并且集成了Namp的全部功能，包括插件，zANTi 的界面还是挺高端大气上档次的

![2014070616265792074.png](http://drops.javaweb.org/uploads/images/186e6b0e046ecec5321602f52cc43da7c4b8601b.jpg)

![2014070616280183276.png](http://drops.javaweb.org/uploads/images/288f8326fbd37a6c070983b1725e1305349562f6.jpg)

下面是扫描的界面

![2014070616283027683.png](http://drops.javaweb.org/uploads/images/f97cadfb05c40a279c38bc3dbb26eb318a3aa9f0.jpg)

![2014070616284422442.png](http://drops.javaweb.org/uploads/images/5821b5d74bd44103695035d411d292db379ef2b2.jpg)

![2014070616285952562.png](http://drops.javaweb.org/uploads/images/1f6719ce7f6454e8d98d351f9d30b09e647ef92d.jpg)

其次我喜欢的是它的暴力猜解工具，他能够根据扫描出的端口和服务来做相应的暴力猜解。如果是注册用户，能过享受到Zimperium公司提供的强大的字典，当然我是穷屌。。只能用自带的small字典

![2014070616311120433.png](http://drops.javaweb.org/uploads/images/0eaae4bd24f01f633fb8e720c34d9e43e5cc7684.jpg)

![2014070616320617560.png](http://drops.javaweb.org/uploads/images/8704193034a923fdcf7c1eff71aee60ed8b7c6bf.jpg)

之后是zANTi 的中间人攻击模块，他比dsploit多了一些功能，像是更改下载软件所下载的软件之类的。其中有个很好玩的东西。。就是能过看用户在上网时候看的图片（包括QQ好友发来的图片）。他的密码抓去似乎也比dsploit厉害（还能看浏览器是否有漏洞，如果想测试，没问题，give me the money）。。同样用我的百度帐号来测试（百度这密码加密。。你们看着办吧）

![2014070616352889919.png](http://drops.javaweb.org/uploads/images/287feacdd74a20796058f4f4d8645adc6e4c6d27.jpg)

![2014070616365266590.png](http://drops.javaweb.org/uploads/images/f5b5e6931510dd7f83f174eae0a52e3d2202fc3f.jpg)

![2014070616370616082.png](http://drops.javaweb.org/uploads/images/67bcd00f8bc2b3f22cf4df9af77171dad6896a5b.jpg)

![2014070616383268609.png](http://drops.javaweb.org/uploads/images/f799a586ba28b1471b93eda39cca98636b280579.jpg)

下面是好(bian)玩(tai)的功能

![2014070616393390326.jpg](http://drops.javaweb.org/uploads/images/87cb6354129f4dc96d8341230ed62aa6a65b66b6.jpg)

![2014070616394718162.png](http://drops.javaweb.org/uploads/images/c3cdf557e81c12216a14daa9b3b0c78eea616f13.jpg)

0x02 总结
-------

* * *

通过这样的对比，相信各位也知道了两款软件的差别了。各自有各自的优点，同样也有缺点（zANTi 在使用中间人时候。。在百度上无论搜啥都是搜索出一堆乱码。。dsploit有时候会更改你系统时间。）

最后给各位提个醒，手机有风险，安(kan)全(pian)需谨慎。