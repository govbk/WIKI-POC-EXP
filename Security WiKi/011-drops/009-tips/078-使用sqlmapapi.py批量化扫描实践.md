# 使用sqlmapapi.py批量化扫描实践

0x00 前言
=======

* * *

sqlmap可谓是sql注入探测的神器,优秀的探测功能可以让任何一个使用者无基础挖掘sql注入。wooyun上关于sqlmap的文章已经有6篇了,都没有科 普sqlmapapi.py。因此我打算分享下这方面的实践。利用sqlmap测试SQL注入的效率很低,每一个url都需要手动测试,这样肯定不是理想状态。 sqlmap的作者肯定也察觉到这一点了,默默的开发了sqlmapapi.py,当你使用了sqlmapapi.py后才能体会到sqlmap的强大。sqlmap构建了一个自动化 分布式的扫描帝国!这篇文章我主要从sqlmapapi.py的代码角度和AutoSqli类的设计与实现的角度展开。

0x01 sqlmapapi.py综述
===================

* * *

sqlmapapi.py给使用者提供了一个强大的功能,服务功能。使用者可以利用sqlmapapi.py开启服务端口,以后只要向sqlmapapi发送请求,就可以进行sql注入,然后发送查询请求,就可以得到这个url是否是注入点,以及详细的内容。同学们看到这里是不是有些小激动呢? sqlmapapi.py的help,我们需要用的是-s参数,也许你也有可能用到-p参数。

![enter image description here](http://drops.javaweb.org/uploads/images/b08be8ea92b7b78dfd0cdf300f86ae6eda4a4430.jpg)

从sqlmapapi.py文件可以看出来,我们利用的文件的调用关系是

![enter image description here](http://drops.javaweb.org/uploads/images/ba0b8acd8396d66503a4e0193cbb03979bbdba29.jpg)

进入到lib/utils/api.py的server类,可以发现通过向server提交数据进行与服务的交互。 一共分为3种类型。

*   Users' methods 用户方法
*   Admin function 管理函数
*   sqlmap core interact functions 核心交互函数

可以提交数据的种类如下。

用户方法

*   @get("/task/new")
*   @get("/task//delete")

管理函数

*   @get("/admin//list")
*   @get("/admin//flush")

核心交互函数

*   @get("/option//list")
*   @post("/option//get")
*   @post("/option//set")
*   @post("/scan//start")
*   @get("/scan//stop")
*   @get("/scan//kill")
*   @get("/scan//status")
*   @get("/scan//data")
*   @get("/scan//log//")
*   @get("/scan//log")
*   @get("/download///")

不难发现这些操作可以完全满足我们的测试需求,因此利用这些就可以批量了。当然每一种请求都会有不同的返回值,这些返回值是json的形式传回, 解析就好了。其实这些我已经替大家做好了,调用AutoSqli类就可以了,但是还是要挑一些讲下。

task/new 任务建立

```
GET /task/new Response:
{
    "taskid": "1d47d7f046df1504" 
}

    /scan/<task_id>/status 扫描任务状态
GET /scan/<task_id>/status Response:
{
    "status": "terminated",
    "returncode": 0 
}

```

详细内容请各自查阅代码。

0x02 AutoSqli类
==============

* * *

我封装AutoSqli类的作用是想轻松的与sqlmapapi.py建立的server进行交互。

AutoSqli的run方法的执行逻辑图

![enter image description here](http://drops.javaweb.org/uploads/images/36e727a02a8fe10b835921ea0131ceaf57c9a8ea.jpg)

这些步骤就是正常sqlmap扫描的逻辑,因此调用AutoSqli就可以正常执行。

Show code

![enter image description here](http://drops.javaweb.org/uploads/images/fd52a3be47253a9fc62abf389c3f4a9977745ba3.jpg)

具体代码查看Mspider项目的Autosqli.py文件。

https://github.com/manning23/MSpider

0x03 使用心得
=========

* * *

AutoSqli类的初始化可以添加url的data,cookie,referer。因此无需顾虑探测需要登陆的页面。

![enter image description here](http://drops.javaweb.org/uploads/images/b1828bd77af500b0d65ebb754d7873132fcdfe81.jpg)

对于AutoSqli类的使用,主要注意option_set()方法的使用,其数据结构为字典,由于可添加的内容超长,因此想添加自动的测试设置请参考Mspider项 目的set_option.txt文件。

![enter image description here](http://drops.javaweb.org/uploads/images/ea2787ec54d87d350df0ef30bd2d2f6c85a04c67.jpg)

说道使用场景,其实我自己已经玩了好久了,说实话效果没达到我的预期,分析下原因。

现在网站的sql注入确实少了,烧饼类型的主要点更少。

sqlmap的初始探针不怎么样,想要精准判断还需要研究,个人研究发现对于mysql数据库,使用时间类型探针效果最好,当然需要自己写探针,详 细的参考Mayikissyou牛的文章。顺便吐槽下,Mayikissyou牛的文章,对于探针的改写真是蜻蜓点水啊,我研究了好久才把lijiejie的那些方法加 上:)

有想法的同学肯定希望我把Mspider和AutoSqli结合下,可是我觉得方法我已经分享了,剩下的同学自己实践吧。实践才能有新的想法。

sqlmapapi.py就是sqlmap为了分布式扫描SQL注入做的,但是资料真的很少,实践的结果更少,希望这篇分享就当抛砖引玉了,有问题欢迎随时和我交流。还有,Mayikissyou牛的文章真心推荐大家读下,配合我这篇文章,sql注入真是想怎么玩就怎么玩了。

0x04 资料
=======

* * *

http://volatile-minds.blogspot.jp/2013/04/unofficial-sqlmap-restful-api.html

http://drops.wooyun.org/tips/5254