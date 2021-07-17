# charles使用教程指南

0x01 前言：
--------

* * *

Charles是一款抓包修改工具，相比起burp，charles具有界面简单直观，易于上手，数据请求控制容易，修改简单，抓取数据的开始暂停方便等等优势！下面来详细介绍下这款强大好用的抓包工具。

0x02 下载与安装
----------

* * *

首先是工具下载和安装 首先需要下载java的运行环境支持（一般用burp的人肯定也都有装java环境）。装好java环境后，可以直接去百度搜索并下载charles的破解版，下载到破解版之后，里面一般会有注册的jar文件，然后注册后就可以永久使用了（ps：不注册的话，每次使用30分钟，工具就会自动关闭）。

0x03 PC端抓包
----------

* * *

下面是pc端的抓包使用情况 Charles支持抓去http、https协议的请求，不支持socket。

然后charles会自动配置IE浏览器和工具的代理设置，所以说打开工具直接就已经是抓包状态了。 这里打开百度抓包下，工具界面和相关基础功能如下图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/00f67848983643767b478824d5226e48d946510e.jpg)

上图中的7个位置是最常用的几个功能。

1 那个垃圾桶图标，功能是clear，清理掉所有请求显示信息。

2 那个望远镜图标，功能是搜索关键字，也可以使用ctrl+f实现，可以设置搜索的范围。

![enter image description here](http://drops.javaweb.org/uploads/images/2d15c5d2642a004544a6a59029dba516454ef3b4.jpg)

3 圆圈中间红点的图标，功能是领抓去的数据显示或者不显示的设置。 这个本人认为是charles工具很方便的一个两点，一般都使其为不显示抓去状态，只有当自己测试的时候的前后，在令其为抓取并显示状态。这样可以快准狠的获取到相关自己想要的信息，而不必在一堆数据请求中去寻找。

4 编辑修改功能，可以编辑修改任意请求信息，修改完毕后点击Execute就可以发送一个修改后的请求数据包。

![enter image description here](http://drops.javaweb.org/uploads/images/9d317bb636a7993620379d5bcc0a83b933d790aa.jpg)

5 抓取的数据包的请求地址的url信息显示。

6 抓取的数据包的请求内容的信息显示。

![enter image description here](http://drops.javaweb.org/uploads/images/8371f3c3af10cfd9c4ce28bc7bc1d7879b388010.jpg)

post请求可以显示form形式，直观明了。

![enter image description here](http://drops.javaweb.org/uploads/images/cc3f80bfb3f5e52aa2ba1cc4bcfa7e52cfa33bea.jpg)

7 返回数据内容信息的显示。

![enter image description here](http://drops.javaweb.org/uploads/images/172e9015913646f22cd5355e491cfe9503050b6d.jpg)

其中5、6、7中都有各种形式的数据显示形式，其中raw是原始数据包的状态。

0x04 显示模式
---------

* * *

charles抓包的显示，支持两种模式，Structure和Sequence，其优点分别如下。

Structure形式如下图 优点：可以很清晰的看到请求的数据结构，而且是以域名划分请求信息的，可以很清晰的去分析和处理数据。

![enter image description here](http://drops.javaweb.org/uploads/images/77053a81d433420ac84cdca4ed785ed66526828c.jpg)

Sequence形式如下图 优点：可以很清晰的看到全部请求，不用一层一层的去点开，这里是以数据请求的顺序去执行的，也就是说那个请求快就在前面显示。

![enter image description here](http://drops.javaweb.org/uploads/images/3e2a54e78c9f754c46f9ae72da3265e0c47188fe.jpg)

具体要说两种形式哪个更好，这个就是见仁见智了。本人比较喜欢第二种，粗矿豪放！

0x05 移动APP抓包
------------

* * *

这里相比其他抓包软件来说要简单的多了，具体步骤如下：

1 使手机和电脑在一个局域网内，不一定非要是一个ip段，只要是同一个漏油器下就可以了，比如电脑连接的有线网ip为192.168.16.12，然后手机链接的wifi ip为192.168.1.103，但是这个有线网和无线网的最终都是来自于一个外部ip，这样的话也是可以的。

2 下面说说具体配置，这里电脑端是不用做任何配置的，但是需要把防火墙关掉（这点很重要）！

然后charles设置需要设置下允许接收的ip地址的范围。 设置首先要进入这个位置 Proxy - Access Control Settings 然后如果接收的ip范围是192.168.1.xxx的话，那么就添加并设置成192.168.1.0/24 如果全部范围都接收的话，那么就直接设置成0.0.0.0/0

![enter image description here](http://drops.javaweb.org/uploads/images/8ff773c4160b53af8ac969354ccfb2405a8c4524.jpg)

然后如果勾选了Proxy - Windows Proxy 的话，那么就会将电脑上的抓包请求也抓取到，如果只抓手机的话，可以将这个设置为不勾选。

3 接下来下面是手机端的配置

首先利用cmd - ipconfig命令查看自己电脑的ip地址

![enter image description here](http://drops.javaweb.org/uploads/images/cb28f4f13beaa797af6c1f15c77a61ef9152d843.jpg)

然后在手机端的wifi代理设置那里去进行相关的配置设置。

这里的代理服务器地址填写为电脑的ip地址，然后端口这里写8888（这个是charles的默认设置），如果自己修改了就写成自己所修改的端口就可以了。

![enter image description here](http://drops.javaweb.org/uploads/images/70265316ef943cb5af80671c6ba3d548b778e881.jpg)

4 好了，这样就配置完成就大功告成了！下面打开UC浏览器或者其他东西，随便访问个网页看有没有抓取到数据就可以了（我这里是直接访问的新浪新闻首页）。

![enter image description here](http://drops.javaweb.org/uploads/images/11054ecef591db7d3d6becbcc027819e5aa73f82.jpg)

0x06 其他常用功能
-----------

* * *

相信上面介绍的那些你已经学会了吧，下面再说说charles的一些其他常用的功能

选择请求后，右键可以看到一些常用的功能，这里说说Repeat 就是重复发包一次。 然后Advanced Repeat就是重复发包多次，这个功能用来测试短信轰炸漏洞很方便。

![enter image description here](http://drops.javaweb.org/uploads/images/95686f2cd9e32e652d403a1e88bd4307a3407a92.jpg)

还有比如说修改referer测试CSRF漏洞，修改form内容测试XSS，修改关键的参数测试越权，修改url、form、cookie等信息测试注入等，都非常方便。

好了，这款工具的介绍就到这里了，相信这款方便好用的工具，以后肯定会被更多的人使用到的。

0x07 charles使用问题汇总
------------------

* * *

Charles是一款很好用的抓包修改工具，但是如果你不是很熟悉这个工具的话，肯定会遇到各种感觉很莫名其妙的状况，这里就来帮你一一解答。

1 为什么下载了不能用啊？打不开啊。

因为charles是需要java环境才能运行的，需要先安装java环境才可以。

2 为什么我用着用着就自动关闭了？大概30分钟就会关闭一次。

因为charles如果没有注册的话，每次打开后就只能哟个30分钟，然后就会自动关闭，所以最好在使用前先按照说明去进行工具的注册操作。

3 为什么我在操作的时候有时候就直接工具就界面卡住死了，关都关不掉，只能用任务管理器才可以关掉？

这个的确是charles这个工具的一个bug，开始用的时候，我也很恶心，而且经常悲剧，但是现在也有相应的解决办法了，下面那样操作就可以了。

首先随便抓些包，要求有图片的请求。

![enter image description here](http://drops.javaweb.org/uploads/images/3be0b9d4b90003e60bf6509a5bf9ef19e2469208.jpg)

然后选中一个图片的请求，然后分别点击 Response - Raw 然后那里会加载其中的内容，然后加载完毕后，再去随便操作就可以了，就不会在悲剧的直接工具卡死掉了。。。

![enter image description here](http://drops.javaweb.org/uploads/images/48125d2189e013e6003b31765f2ab18c84b63b73.jpg)

4 为什么用了charles后，我就上不了网页了，但是qq可以。

因为如果charles是非正常状态下关闭的话，那么IE的代理就不会被自动取消，所以会导致这种情况。

解决办法：

第一种：直接打开charles，然后再正常关闭即可。 第二种：去将IE浏览器代理位置的勾选去掉。

![enter image description here](http://drops.javaweb.org/uploads/images/7a3e09e53a2eb179eb44711fa7740df493127207.jpg)

5 为什么我用charles不能抓到socket和https的数据呢？

首先，charles是不支持抓去socket数据的。 然后，如果抓不到https的数据的话，请查看你是不是没有勾选ssl功能。 Proxy - Proxy Settings - SSL 设置

6 为什么我用charles抓取手机APP，什么都是配置正确的，但是却抓不到数据。

首先，请确保电脑的防火墙是关闭状态，这个很重要。

![enter image description here](http://drops.javaweb.org/uploads/images/2d288fe39823cd23613fa2446c8fb5cd7d92614a.jpg)

如果，防火墙关了还是不行，那么请把手机wifi断掉后重新连接，这样一般就可以解决问题了。 如果以上方法还是不行的话，那么请将手机wifi位置的ip地址设置成静态ip，然后重启charles工具。

7 抓包后发现form中有些数据显示是乱码怎么办？

请在Raw模式下查看，Raw模式显示的是原始数据包，一般不会因为编码问题导致显示为乱码。

8 我用charles抓手机app的数据，但是同时也会抓去到电脑端的数据，可以设置吗？

可以，设置位置在Proxy - Windows Proxy ，勾选表示接收电脑的数据抓包，如果只想抓去APP的数据请求，可以不勾选此功能。

9 为什么我用IE可以抓到数据，但是用360或者谷歌浏览器就不行？

请确保360或者谷歌的代码设置中是不是勾选设置的是 使用IE代理。

![enter image description here](http://drops.javaweb.org/uploads/images/e7eb4c3c6c4360abafb4abe93913dad2e95495f0.jpg)

10 想要复制粘贴某些数据的话，怎么办，右键没有相应功能啊？

请直接使用Ctrl +C 和 Ctrl+V 即可。

以上就是charles在使用过程中常见的10中问题和相应的解决情况，有了这个文章，大家就不用在遇到问题的时候懊恼了，嘿嘿。