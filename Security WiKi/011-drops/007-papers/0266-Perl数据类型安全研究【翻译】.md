# Perl数据类型安全研究【翻译】

0x00 背景
=======

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/323df8606f9a449df31f56f8010a840687410aa6.jpg)

前几天有个人在某大会上讲了一个在perl中存在了20年的问题。作为一个只会perl不会python的人，真的很心痛。看完视频后感觉被黑的吃不下东西。

这俨然就是一场对perl的吐槽批斗大会，整个演讲充满了sucks、fuck等和谐词汇，也能看出演讲者是多么的义愤填膺，场下一次次的鼓掌和附，嗯，让我想起了郭德纲。

0x01 问题
=======

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/a2df43af534c3e38596523df8f2ad457329399ae.jpg)

言归正传，这个在perl中存在了20年的问题到底是啥呢？抛去perl的语法的槽点，真正的问题在data types上，对的，就是数据类型。

Perl对数据类型的处理真是有点匪夷所思了。

我们先了解一下perl中的变量有哪几种。

perl中的变量

perl的数据类型分为三类：标量$，数组@，哈希%。

具体定义在这里不多说，我们来看几个例子：

![enter image description here](http://drops.javaweb.org/uploads/images/6d230619aec9983ea3403ba36f201158c3ce5bbb.jpg)

不管是标量、数组还是哈希（字典），定义跟其他语言没什么区别。

![enter image description here](http://drops.javaweb.org/uploads/images/3fab97d63f754e38764a604968c6cc862f73b89f.jpg)

我们来看看几个特殊的情况，下面每个预期值为正常人类理解应该得到的结果。

```
@array =(1, 2, 'a', 'b', 'c');
print $array[0];

```

预期值 1

![enter image description here](http://drops.javaweb.org/uploads/images/59553c8fcf7b4c2e16708571ea476c55d77306f5.jpg)

实际值 1

```
$scalar = (1, 2, 'a', 'b', 'c'); 
print $scalar;

```

预期值 1

![enter image description here](http://drops.javaweb.org/uploads/images/024c10ac60599e780f7dea1badc3cacff903f378.jpg)

实际值 c 我擦泪，为毛会是c！太不科学了，继续往下看。

```
@list = (1, 2, 'a', 'b', 'c'); 
print scalar @list;

```

预期值 1

![enter image description here](http://drops.javaweb.org/uploads/images/3075c367fe1171af919a4e5ae78d0cb46fe2a953.jpg)

实际值 5 呵呵，他把数组的长度输出了。

再看看这个哈希的例子

```
%hash = (1, 2, 'a', 'b', 'c'); 
print $hash{'a'};

```

预期值 木有

![enter image description here](http://drops.javaweb.org/uploads/images/b580757312079952726e6bd4af50eb6bab6740db.jpg)

实际值 b 为毛把b给输出了，谁能告诉我这头草泥马是怎么处理的。

0x02 漏洞
=======

* * *

这些问题会产生什么漏洞呢？

一起看看在web中php跟perl处理的对比。

![enter image description here](http://drops.javaweb.org/uploads/images/7714a92eca89a307a5ae170a6553d813740a8d34.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/89dc23be04e9e02e93c1918f3d54f57fc34f8bcb.jpg)

这么看来是木有任何问题的，那么使用复参的时候呢？

![enter image description here](http://drops.javaweb.org/uploads/images/d2c2402ee340e5472a911083cf3f9cf8cc3ae612.jpg)

php很好的处理了传入的数据，而perl的做法就是草泥马在奔腾%>_<%他是直接可以传入数组的。

再深入一下，看看当数组和哈希结合的时候的情况。

```
@list = ('f', 'lol', 'wat');
$hash = {'a' => 'b',
         'c' => 'd', 
         'e' => @list
};
print $hash;

```

预期值

```
{
'a' => 'b',     
'c' => 'd',     
'e' => ['f','lol','wat'] 
} 

```

![enter image description here](http://drops.javaweb.org/uploads/images/4ca7fe1249fc23d9fc48c00d63e158505ec97d4f.jpg)

神马情况，数组中的“，”变成了“=>”又给赋值了？e=>f、lol=>wat，what the f*cuk！

![enter image description here](http://drops.javaweb.org/uploads/images/c55ca189c3f88ced368e1ba925a2c9bf3efaab45.jpg)

这是多大的一个坑啊！看Bugzilla是怎么掉进去的。

http://zone.wooyun.org/content/15628

关于数据类型的这些问题我不想再说了，有些恶心。

0x03 GPC的问题
===========

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/33322cec56433ca76137a7cfcfeef5cd5433cb6c.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/3ce23f54fd41fc9f623cbcc8100ca9b9384936c4.jpg)

屌屌的棒棒的，对吧，可是……

![enter image description here](http://drops.javaweb.org/uploads/images/7837f21d6f87dc8524dbd9b88f9827d19e0eff21.jpg)

我了个*，一个都不给转义了，就这么罢工了，可以顺顺畅畅的注入了好么。

![enter image description here](http://drops.javaweb.org/uploads/images/1ae9c6b913d1edb5fa1099125dead29f1fd6af32.jpg)

我想静静。

0x04 来源
=======

* * *

Pdf：

http://events.ccc.de/congress/2014/Fahrplan/system/attachments/2542/original/the-perl-jam-netanel-rubin-31c3.pdf

视频地址：

http://media.ccc.de/browse/congress/2014/31c3_-_6243_-_en_-_saal_1_-_201412292200_-_the_perl_jam_exploiting_a_20_year-old_vulnerability_-_netanel_rubin.html#video