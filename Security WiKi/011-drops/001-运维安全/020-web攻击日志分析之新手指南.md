# web攻击日志分析之新手指南

from:http://resources.infosecinstitute.com/log-analysis-web-attacks-beginners-guide/

0x00 前言
=======

* * *

现实中可能会经常出现web日志当中出现一些被攻击的迹象，比如针对你的一个站点的URL进行SQL注入测试等等，这时候需要你从日志当中分析到底是个什么情况，如果非常严重的话，可能需要调查取证谁来做的这个事情，攻击流程是什么样子的。

除此之外，还有其他场景。

作为一名管理员，理解如何从安全的角度来分析日志真的很重要。

这篇文章内容包括了日志分析的一些基础知识，可以解决上述需求。

0x01 准备
=======

* * *

出于演示目的，我进行以下设置。

Apache 服务器
----------

预安装在Kali Linux

可以用以下命令开启：

```
service apache2 start

```

![enter image description here](http://drops.javaweb.org/uploads/images/9776e3a1d72a2ed41a2a6f76cccc8a2d288c5921.jpg)

MySQL
-----

预安装在Kali Linux

可以用以下命令开启：

```
service mysql start

```

![enter image description here](http://drops.javaweb.org/uploads/images/0a10c8f454cf2b6c64e419760e62ee23a1c2807c.jpg)

使用PHP-MySQL创建一个有漏洞的web应用
------------------------

我使用PHP开发了一个有漏洞的web应用并且把它放在上面提到的 Apache-MySQL里面。

上述设置完成后，我用了一些Kali Linux中的自动工具（ZAP、w3af）扫描这个有漏洞的应用的URL。

现在让我们来看看分析日志中的不同情况。

0x02 Apache服务中的日志记录
===================

* * *

Debian系统上Apache服务器日志的默认位置为：`/var/log/apache2/access.log`

日志记录只是在服务器上存储日志。我还需要分析日志以得出正确结果。在接下来的一节里，我们将看到我们如何分析Apache服务器的访问日志以找出web站点上是否有攻击尝试。

分析日志

手动检查

在日志量较小的情况下，或者如果我们查找一个指定关键词，可以使用像grep表达式这样的工具观察日志。

在下图中，我们在URL中试图搜寻所有关键词为“union”的请求。

![enter image description here](http://drops.javaweb.org/uploads/images/f15b1f0d5effccf94a761db2b5f95e1127a91cfa.jpg)

从上图中，我们可以看到URL中的“union select 1,2,3,4,5”请求。很明显，ip地址为 192.168.56.105的某人尝试了SQL注入。 类似地，当我们有自己的关键词时可以搜索特殊的关键词。

![enter image description here](http://drops.javaweb.org/uploads/images/9700d673e90a4ca9733a6d39e6e4eaa8b244cd2b.jpg)

在下图中，我们正在搜索试图读取“/etc/passwd”的请求，很明显是本地文件包含尝试。

如上面的截图所示，我们有许多本地文件包含的尝试，且这些请求发送自ip地址 127.0.0.1。

很多时候，能轻易通过日志看出是否是自动化扫描器产生的。

举例来说， IBM appscan在许多攻击payload中使用“appscan”这个词。所以，在日志中查看这样的请求，我们基本就可以判断有人在使用appscan扫描网站。

Microsoft Excel也是一个打开日志文件和分析日志的不错的工具。我们可以通过指定“空格”为分隔符以用excel打开日志文件。

当我们手头没有日志分析工具时，这个也挺好用的。

除了这些关键词，在分析期间要了解HTTP状态代码的基础知识。以下是关于HTTP状态代码的高级信息的表格。

![enter image description here](http://drops.javaweb.org/uploads/images/d07bfc4effd525543d5c3a9f6afcee918791fa9d.jpg)

0x03 Web shells
===============

* * *

webshell是网站/服务器的另一个问题。webshell可以已web server权限控制服务器。

在一些情况下，我们可以使用webshell来访问所有放在相同服务器上的其他站点。

以下截图显示了Microsoft Excel 中开启相同的access.log文件。

![enter image description here](http://drops.javaweb.org/uploads/images/1c8f94f262884d1a3378bb04fb364bc4bb32eacd.jpg)

我们清楚地看到有一个叫“b374k.php”的文件被访问了。“b374k”是一个流行的webshell，因此这个文件是很可疑的。

查看相应代码“200”，本行表明有人上传了一个webshell并访问了它。

在许多情况下，攻击者重命名webshell的名字以避免怀疑。我们必须变得聪明点，看看被访问的文件是否是常规文件或者是否他们看起来不太一样。我们可以更进一步，如果任何文件看起来可疑的话，还可以查看文件类型和时间戳。

```
One single quote for the win

```

SQL注入是web应用中最常见的漏洞之一。大多数学习web应用安全的人是从学习SQL注入开始的。

识别一个传统的SQL注入很容易，给URL参数添加一个单引号看看是否报错。

任何我们传递给服务器的东西都会被记录，并且可以朔源。

以下截图显示了日志当中记录了有对参数user传入单引号测试是否有SQL注入的行为。

%27是单引号的URL编码。

![enter image description here](http://drops.javaweb.org/uploads/images/1ce557dedcb9bfffc68f002a53f295e407e4f615.jpg)

出于管理目的，我们还可以运行查询监视来查看数据库中的哪个请求被执行了。

![enter image description here](http://drops.javaweb.org/uploads/images/c7aca3b6108153aa6eda186cd99c57a840f298d3.jpg)

如果我们观察以上图片，传递一个单引号给参数“user”的SQL语句被执行了。

0x04 使用自动化工具分析
==============

* * *

当存在大量日志时。手动检查就会变得困难。在这种情景下，除了一些手动检查之外我们可以使用自动化工具。

虽然有许多高效的商业工具，但是我要向你们介绍一款被称为“Scalp”的免费工具。

据他们的官方链接所说，Scalp是用于Apache服务器，旨在查找安全问题的日志分析器。主要理念是浏览大量日志文件并通过从HTTP/GET中提取可能的攻击。

Scalp可以从以下链接下载：

https://code.google.com/p/apache-scalp/

Scalp是python脚本，所以要求我们的机器中安装python。

以下图片显示该工具的帮助。

![enter image description here](http://drops.javaweb.org/uploads/images/db7f3156259ce85063a3be4bb38b7b27a04c09e4.jpg)

如我们在上图所见，我们需要使用标志-l来提供要分析的日志文件。

同时，我们需要提供使用标志-f提供一个过滤文件让Scalp在access.log文件中识别可能的攻击。

我们可以使用PHPIDS项目中的过滤器来检测任何恶意的尝试。

该文件名为“default_filter.xml ”，可以从以下链接中下载：

https://github.com/PHPIDS/PHPIDS/blob/master/lib/IDS/default_filter.xml

以下代码块是取自上面链接的一部分。

```
<filter>
      <id>12</id>
      <rule><![CDATA[(?:etc\/\W*passwd)]]></rule>
      <description>Detects etc/passwd inclusion attempts</description>
      <tags>
          <tag>dt</tag>
          <tag>id</tag>
          <tag>lfi</tag>
      </tags>
      <impact>5</impact>
</filter>

```

它是使用XML标签定义的规则集来检测不同的攻击测试。以上代码片段是检测文件包含攻击尝试的一个示例。

下载此文件之后，把它放入Scalp的同一文件夹下。

运行以下命令来使用Scalp分析日志。

```
python scalp-0.4.py –l /var/log/apache2/access.log –f filter.xml –o output –html

```

![enter image description here](http://drops.javaweb.org/uploads/images/be78f81722aca352926a267a76003fa4909d44b1.jpg)

“output”是报告保存的目录。如果不存在的话，由Scalp自动创建。-html是用来生成HTML格式的报告。 如我们在上图看到的那样，Scalp结果表明它分析了4001行，超过4024并发现了296个攻击模式。

运行上述命令后在输出目录内生成报告。我们可以在浏览器内打开它并查看结果。 下面截图显示的输出显示了目录遍历攻击尝试的一小部分。

![enter image description here](http://drops.javaweb.org/uploads/images/a39da7fab7f71e8247c36e595b77df197bc218a5.jpg)

MySQL中的日志记录
-----------

* * *

本节论述了数据库中的攻击分析和监视它们的方法。

第一步是查看设置了什么变量。我们可以使用“show variables;”完成，如下所示。

![enter image description here](http://drops.javaweb.org/uploads/images/87cba54ab71e997cbd4c5ed48a8373e5bdc8a76c.jpg)

接下来显示了上述命令的输出。

![enter image description here](http://drops.javaweb.org/uploads/images/8bbcbd7188f0ebdc62f1f1fb1ad4a8734cec1c6e.jpg)

如我们在上图中看到的，日志记录已开启。该值默认为OFF。

这里另一个重要的记录是 “log_output”，这是说我们正在把结果写入到文件中。另外，我们也可以用表。

我们可以看见“log_slow_queries”为ON。默认值为OFF。

所有这些选项都有详细解释且可以在下面提供的MySQL文档链接里直接阅读：

http://dev.mysql.com/doc/refman/5.0/en/server-logs.html

MySQL的查询监控
----------

* * *

请求日志记录从客户端处收到并执行的语句。默认记录是不开启的，因为比较损耗性能。

我们可以从MySQL终端中开启它们或者可以编辑MySQL配置文件，如下图所示。

我正在使用VIM编辑器打开位于/etc/mysql目录内的“my.cnf”文件。

![enter image description here](http://drops.javaweb.org/uploads/images/a5d1297ade82a19d429f71b54a6069e36de5d008.jpg)

如果我们向下滚动，可以看见日志正被写入一个称为“mysql.log”的文件内。

![enter image description here](http://drops.javaweb.org/uploads/images/fb7df1f8264a50f776596b44a22b4d6801125d1b.jpg)

我们还能看到记录“log_slow_queries” ，是记录SQL语句执行花了很长时间的日志。

![enter image description here](http://drops.javaweb.org/uploads/images/c64d9f5b9dcc017be28314be1e1c81e9ddc140fd.jpg)

现在一切就绪。如果有人用恶意查询数据库，我们可以在这些日志中观察到。如下所示：

![enter image description here](http://drops.javaweb.org/uploads/images/da1eecf40c2bf1028b250b841113d8b9163266b7.jpg)

上图显示了查询命中了名为“webservice”的数据库并试图使用SQL注入绕过认证。

0x05 更多日志记录
===========

* * *

默认地，Apache只记录GET请求，要记录POST数据的话，我们可以使用一个称为“mod_dumpio”的Apache模块。要了解更多关于实现部分的信息，请参考以下链接：

http://httpd.apache.org/docs/2.2/mod/mod_dumpio.html

另外，我们可以使用“ mod security”达到相同结果。

Reference http://httpd.apache.org/docs/2.2/logs.html