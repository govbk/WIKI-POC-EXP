# SQLMAP 实例COOKBOOK

提醒：本文章中的所有例子均已通过乌云平台通知厂商，并按照流程已经公开（未公开的会有标识并且隐藏信息，请等待公开后自行查看），请在阅读文章的同时不要对文中所列漏洞重复测试，谢谢

0x00 概述
-------

* * *

本文章面向 已经理解SQL注射基本原理、已经配置好并了解SQLMAP基本命令、但缺乏实践的入门者。在文章中总结了自己在乌云上发布的近三十个SQL注射漏洞，对于SQLMAP在不同场景下的应用给出了 实例总结，对于SQLMAP的基本介绍、安装配置、命令手册请大家自行百度。

SQL注射原理传送门[http://drops.wooyun.org/papers/59](http://drops.wooyun.org/papers/59)

SQLMAP用户手册传送门[http://drops.wooyun.org/tips/143](http://drops.wooyun.org/tips/143)

0x01 从HelloWorld开始思考
--------------------

* * *

[WooYun: WanCMS 多处SQL注射（源码详析+实站演示）](http://www.wooyun.org/bugs/wooyun-2014-049372)

形如：

```
C:\Users\Administrator>sqlmap.py -u "http://?a=b" –tables

```

[WooYun: 吉林市人力资源和社会保障局 Oracle injection](http://www.wooyun.org/bugs/wooyun-2013-045782)

```
root@kali:~# sqlmap -u "www.jljl.lss.gov.cn/ybcx.asp" --data="yblb=%D2%BD%C1%C6%B1%A3%CF%D5&ybxm=123&ybsfzh=123" --tables

```

相信大家都已经倒背如流，烂熟于心。

### 例子a)

SQLMAP首先测试a（唯一的参数），检测结果如下

```
Type: boolean-based blind（heuristic test 基本测试就能发现） 
Type: UNION query      （在至少发现其他一种注射存在时会扩大测试范围，原始是1-10，而这里测试到了20，这是自动扩展的） 
Type: AND/OR time-based blind （正常等级测试即可发现）

```

效率很高，检测很准确，跑表成功，一切都很好，这是一个完美的HelloWorld

### 例子b)

SQLMAP首先测试yblb，没有发现注射，然后检测ybxm，结果如下:

```
Error-based（直接会告诉你是oracle，然后根据提示测试会很顺利）
Union query（正常测试就能测试出来）
And or time based（正常测试就能测试出来）

```

我们发现，在测试yblb的时候SQLMAP浪费了我们好多时间（这个漏洞我是手工fuzz的，我知道是ybxm打单引号报的错，如果是扫描器扫描也同样知道漏洞出在ybxm） 那么，何必浪费时间呢？

改进方案：指定测试参数 –p ybxm

改良的例子：

[WooYun: 今题网某分站SQL注射漏洞](http://www.wooyun.org/bugs/wooyun-2014-048798)

```
C:\Users\Administrator>sqlmap.py -u "http://club.jinti.com/operation/setmoodinfo.aspx?bodyid=52164&channel=a&classid=0&mood=mood1rand=0.10818770481273532" -p channel –tables

```

避免了测试不必要的参数浪费时间

这也是本文章的目的，让新手们少走弯路，快速顺利地完成检测任务。

0x02 需要登陆后访问的页面
---------------

* * *

有时注射点的位置需要登录（手动测试时发现、扫描器配置了登陆sequence扫描）

解决方案：使用—cookie选项（cookie是burpsuite或者tamperdata手工抓的）

[WooYun: CSCMS V3.5 最新版 SQL注射（官方站演示+源码详析）](http://www.wooyun.org/bugs/wooyun-2013-047363)

形如：

```
C:\Users\Administrator>sqlmap.py -u "http://?a=b" -p a --dbms=mysql --cookie="cookie" –tables

```

0x03 总是提示302 redirect（重定向）
--------------------------

* * *

明明扫描器扫出来的，手工测试也过了，可一到sqlmap就是302。

可能是要重定向到error页面，这种情况有时属于正常状况（部分boolean-based payload会导致），但是总是这样，可能是referer中有限制，或者cookie要登陆，再或者是agent需要换

带上referer（从扫描器请求中找）

解决方案：使用—referrer 选项

例子：

[WooYun: 联众世界SQL注射漏洞可致数据库信息泄露](http://www.wooyun.org/bugs/wooyun-2014-051210)

形如：

```
C:\Users\Administrator>sqlmap.py -u "http:// " --data="? " -p ? --referer="http:// " --tables

```

cookie见0x03

改变user-agent

解决方案：使用random-agent 选项

例子：

[WooYun: 携程网主站+分站多个SQL注入漏洞打包](http://www.wooyun.org/bugs/wooyun-2014-051745)

形如：

```
C:\Users\Administrator>sqlmap.py -u "http:// " --referer="a" --level 3 --random-agent --dbms="microsoft sql server" --techniqu e T --tables

```

当然，如果你知道它要求你用某一种agent，你也应当用user-agent选项自己指定所需的agent（比如说ie6）

0x04 伪静态中的注射
------------

* * *

很多网站会使用伪静态，参数形式经过变化后比较隐蔽，这给工具自动化注射带来了难度

先说一个悲惨的反面案例：

[WooYun: phpweb建站程序可导致大量政府网站受到安全影响](http://www.wooyun.org/bugs/wooyun-2013-046157)

在这个例子里，我为了跑表不惜自己写了一个php的转发请求的脚本，结果劳民伤财。

讽刺的是，我居然用的是SQLMAP。

正确的解决方案：

```
使用“*”符号来自定义注射位置（米字键、星号、小键盘像雪花那个键）

```

正确的案例：

[WooYun: 铁友网某站SQL注射可致所有数据库信息泄露](http://www.wooyun.org/bugs/wooyun-2014-050909)

形如：

```
C:\Users\Administrator>sqlmap.py -u "http://*" –tables

```

会提示发现“*”号，是否处理，选择y

0x05 注射referer
--------------

* * *

一般情况下，指定level 3以上才会检查referer

实例：

[WooYun: 携程旅行网主站 SQL注射可致大量数据库信息泄露](http://www.wooyun.org/bugs/wooyun-2014-051016)

形如：

```
C:\Users\Administrator>sqlmap.py -u "" --level 3 --referer="a" --random-agent --tables

```

我其实曾经悲惨地又用转发请求的方式发过一个referer漏洞

Referer中也是可以使用“*”来自订的

0x06 手工构造注射语句自动化
----------------

* * *

有时候我们需要对注射语句手工调整，比如闭合各种括号单引号，比如补全后面的语句（常见于insert中的注射），以及在伪静态中的调整等等

解决方案：手工构造后，使用“_”号指定注射点（好像也可以指定prefix和surfix来实现，不过我自己习惯于用“_”号）

之后会提示：“在url中发现疑似手动测试遗留的词法，建议……”，选择继续测试

例子：

[WooYun: 久游网SQL注射 可致数据库信息全部泄漏（跑表演示）](http://www.wooyun.org/bugs/wooyun-2014-051064)

形如：

```
C:\Users\Administrator>sqlmap.py -u "http:// " --data=" &?=a' or 1=1* --&…… " -p ? –tables

```

这个我后来想想构造的不妥，不过跑表正常，不深究了

0x07 提示unexploitable point detected
-----------------------------------

* * *

测试时报告injectable，但是又提示不能注射，可能是服务端做了某些防护措施（比如过滤了少量的关键字）但是明显过滤做的不严格

或者是扫描器扫描出了盲注问题，但是SQLMAP检测不出injectable而我们又不想放弃

那么，可以使用—level 选项增加测试项（由于大量的测试会大大减缓测试速度，所以一般情况下不要开这个选项）

例子：

```
 WooYun: 蚂蜂窝主站SQL注射可致数据库信息泄露 

```

完全公开

```
C:\Users\Administrator>sqlmap.py -u "www.mafengwo.cn/shop/mgr_item.php?act=add&item_name=lgkcaleg&item_price=1&shop_id=100597" -p item_name --tables --dbms=mysql --technique T --level 5

```

0x08 指定dbms
-----------

* * *

在上一节中增加level会使检测速度难以忍受，这时就要进一步的缩短测试流程，其中很重要的一项就是指定dbms（这样可以跳过其他无关dbms的检测程式，和error-based发现dbms类型后提示你是否略过其他dbms的检测同理）

解决方案：

```
使用--dbms选项

```

例子：还是上面0x08那个例子

0x09 指定方法盲注测试
-------------

进一步加快测试速度？使用--technique T指定盲注吧（当然如果不是盲注的你可以换其他参数）可以跳过大量的union测试（level高时会扩展到1-100，这是很漫长的等待）

例子：还是上面0x08那个例子

0x0a 过滤了空格
----------

* * *

有些时候网站会“不小心”过滤掉各种字符，可以用tamper来解决（对付某些waf时也有成效）

例子：

[WooYun: phpweb建站程序可导致大量政府网站受到安全影响](http://www.wooyun.org/bugs/wooyun-2013-046157)

把空格过滤掉了（应该还有所有不可见字符）

--tamper=”space2comment.py”

理论是用/**/代替空格

同时如果过滤了其他字符，也可查阅手册可用的tamper选项

0x0b 过滤了逗号
----------

* * *

查找了大量资料后，决定手注……

例子：

[WooYun: iSiteCMS发布安全补丁后仍然有几处注射漏洞（源码详析+实站演示）](http://www.wooyun.org/bugs/wooyun-2013-046702)

里面还转义了`“>”和“<”`，不过可以通过Rlike绕过，但是逗号始终解决不了

各位有没有带着SQLMAP成功绕过逗号的经历？交流一下？

0x0c 重新测试时异常
------------

* * *

有时在测试的过程中，需要做少许调整重新再来一遍，但是重来时发现了异常

[WooYun: 今题网某分站SQL注射漏洞](http://www.wooyun.org/bugs/wooyun-2014-048798)

注意截图中的提示：

```
Sqlmap identified the following injection points with a total of 0 HTTP(S) requests

```

一看觉得奇怪，没有发请求怎么知道的注射点？

其实是之前运行过测试，由于某些原因重新又来了一遍，但是重来的这一遍完全使用了之前保存的检测结果

虽然这个例子中一切都正常，但我亲自碰到过因为这个原因造成无法重新调整测试的情况，解决方式是删除掉output中的对应记录文件（建议用手册中的安全方法，尽管我一直习惯直接删文件夹……）

0x0d 取回数据异常
-----------

* * *

有时发现跑出的数据都是毫无意义的字符

解决方案：

```
a）SQLMAP会提示你加—hex或者—no-cast，有时会有帮助
b）如果你用的是time-based注射，建议增加延时—time-sec等参数，即使你的网速比较好，但是服务器可能遇见各种奇怪环境
c）增加level 值得一试

```

由于乌云上都是成功跑表的结果，暂无实例

0x0e 从burpproxy到sqlmap的捷径
-------------------------

* * *

有时从proxy上截到的包想要放进sqlmap中，需要复制很多项（cookie、referer、post）等，解决方案：使用 -l 选项 把burpproxy的记录直接导入sqlmap

由于这种带着文件的漏洞难以提交乌云平台（难以复现除非给文件），所以我提交的漏洞都转成了一行命令形式，因此没有实例

而且有些时候我们需要先手工构造一下（比如说json里面的注射需要自定义注射点）

这种情况下如果盲目整包丢进SQLMAP，会导致漏报

实例：

[WooYun: 国家兽药基础信息查询系统 SQL注射](http://www.wooyun.org/bugs/wooyun-2014-054062)

0x0f 暴力猜表
---------

* * *

在遇到access的站的时候，总是要猜测表名

在\txt下保存着common-tables.txt，是猜测时使用的表名（SQLMAP在猜测时会根据页面信息自动组装前缀什么的）

我的经验是：如果你知道大概会存在什么表，那么自己去构造common-tables.txt吧，比如扫描时出现的soucecode-exposure（源代码泄露）、页面错误信息、或者你的灵感

Txt下的其他文件正如其名，同理猜测其他数据

实例：

[WooYun: 高邮市某网站修补不当 仍然存在SQL注射](http://www.wooyun.org/bugs/wooyun-2014-050793)

由于GOOGLE到之前的某些漏洞数据，知道部分表名后更改common-tables猜测

0x10 总是unable to connect to the target url
------------------------------------------

* * *

第一种情况可能是time-out设置的太小，但是这个可能性已经不大了，可以试试增加--time-out尝试

解决方案：增加--time-out，可能最好清掉output遗留文件（见0x13）

例子：

[WooYun: 国家兽药基础信息查询系统 SQL注射](http://www.wooyun.org/bugs/wooyun-2014-054062)

里面的unable to connect to the target url提示完全是由响应过慢导致的，不过由于没有严重影响跑表的过程，所以直接忽视掉了

再有可能就是WAF直接把请求拦截掉了，因此得不到响应

有些waf比较友善，过滤后会提示“参数不合法”，但是也有些waf则直接把请求拦下来无提示导致应答超时，这样在测试时会消耗大量的时间等待响应

解决方案：减少time-out进行检测，在跑数据时改回time-out

由于乌云上只给出跑表结果，因此暂无实例

0x11 提示possible integer casting detected
----------------------------------------

* * *

意思是检测到了类似intval的过滤，常见于形如http://xxx.x?a=1在SQLMAP检测dynamic和basic test 时页面毫无弱点，比如手工测试时a=1 和 a=2 显示不同页面，但是a=1’ 或者a=1sdf 或者 a=1 and 1=2 都返回原来的a=1的响应，因此SQLMAP推测可能服务器端有intval的过滤。

如果你是在手工测试，建议到这里可以停止了，节省时间。

如果你是在扫描器扫描的盲注，那么到这里坚决无视警告继续下去。

实例：

忘记是哪个漏洞有这么回事了，但是当时扫描器报告有盲注，所以无视警告继续后成功跑表，现在想想可能服务器端是用了intval后再次使用了没有intval的参数（日志记录 insert），所以跑出来的表都是日志数据库（当时没截intval提示的图，所以目前找不到是哪一个了）