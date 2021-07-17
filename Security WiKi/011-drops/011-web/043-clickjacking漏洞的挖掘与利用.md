# clickjacking漏洞的挖掘与利用

0x00简介

* * *

1 说起clickjacking，很多人其实都不知道是干嘛的。比起XSS来说，clickjacking显得比较神秘，乌云漏洞库里面的相关的漏洞也不到10条而已。

2 瞌睡龙之前发过一篇clickjacking的技术文档，主要是介绍clickjacking出现的原因，以及防御的方法。我这里主要是介绍，怎么寻找clickjacking以及怎么去利用。[Clickjacking简单介绍](http://drops.wooyun.org/papers/104)

提醒一下click jacking和json hijacking完全不是一个东西额，这里大家不要混淆了。

0x01 案例

* * *

1 ClickJacking

[腾讯微博ClickhiJacking](http://wooyun.org/bugs/wooyun-2010-019683)

[新浪微博点击劫持刷粉丝](http://wooyun.org/bugs/wooyun-2010-048468)

2 Xss 结合 ClickJacking

[百度主站反射型XSS漏洞](http://wooyun.org/bugs/wooyun-2010-055526)

[百度贴吧贴内一处Mouseover XSS利用](http://wooyun.org/bugs/wooyun-2010-018358)

[百度翻译反射型XSS（点击劫持demo）](http://wooyun.org/bugs/wooyun-2010-072505)

可以看到配合clickjacking，某些看起来比较鸡助的XSS或者不起眼的设置，也会产生比较严重的危害额。

0x02 实例讲解

* * *

说了这么多，不知道有么有理解。看下面的实例吧。

[用另一个低级的漏洞向豌豆荚用户手机后台静默推送并安装任意应用](http://wooyun.org/bugs/wooyun-2010-071676)

他这里是将自己设计了一个页面，然后上面伪造了一个领奖按钮，然后将iframe嵌套的原网页的推送与其领奖的按钮进行了重叠。

不过不知道是洞主笔误，还是洞主对于clickjacking的描述还是有一些错误。

[![](http://static.wooyun.org/20141110/2014111008254320848.jpg)](http://drops.wooyun.org/wp-content/uploads/2014/11/111.jpg)

这里洞主的描述显然是有问题的。

正确的原理应该是这样，这个领奖的页面是在下面，而原iframe的那个页面在最上面。然后第一个图由于将iframe完全透明了，所以用户就只能看到下面的那个领奖页面。然后用户点击领奖，其实是点击了上层页面中的推送。

所以蓝色圈圈那个位置，应该是“上面”而不是“下面”。

0x03 Zone ClickJacking挖掘

* * *

之前看到瞌睡龙的这个文章的下面，剑心说要赶紧给zone的感谢加上clickjacking的防御。

然后我看了下，zone的感谢加了个confrim，不过其实这种只是可以减轻clickjacking的威力，并不能得到根治啊，完全可以构造2个点骗用户点击的。

然后zone的关注、喜欢、不喜欢这些功能也没有防御，目测zone应该是完全没有防御clickjacking。不过试了试，乌云主站还是对clickjacking进行了防御的，会检测url有么有被iframe嵌套。

下面给个测试poc，有兴趣的可以自己研究研究更好的利用环境。

```
<html>
    <head>
        <meta charset="utf-8" />
        <title>clickjacking demo</title>
    </head>
    <div style="z-index:999;opacity:0.3;width:500px; height:500px;overflow:hidden;position:absolute;top:20px;left:20px;">
        <iframe id="inner" style="position:absolute;top:140px;width:1000px;height:500px;left:-484px;" src="http://zone.wooyun.org/user/px1624"></iframe>
    </div>
    <button id="anwoa" style="cursor:pointer;z-index:10px;position:absolute;top:225px;left:200px;text-align:center;width:100px;height:57px;">按我啊</button>
</html>

```

利用这个clickjacking的poc代码，就可以给自己刷点乌云zone的粉丝了。

同时，还可以给自己zone里面的帖子刷喜欢数量。据说这个喜欢数量可是和zone里面的领主算法息息相关的额!