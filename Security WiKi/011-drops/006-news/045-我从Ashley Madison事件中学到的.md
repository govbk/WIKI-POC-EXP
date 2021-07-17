# 我从Ashley Madison事件中学到的

0x01 事件回顾
=========

* * *

黑客团队Impact Team在8月18日公布了偷情网站Ashley Madison的数据（[Link](http://www.wired.com/2015/08/happened-hackers-posted-stolen-ashley-madison-data/)），多名用户确认了数据的真实性。泄露数据通过BitTorrent被广泛传播，还有人已经设立一个网站`ashley.cynic.al`，让Ashley Madison用户验证自己的账号是否在里面。黑客泄露的数据容量多达9.7GB，包括了电子邮件，哈希密码，用户资料描述，体重，身高，不完整的信用卡交易数据，等等。泄露事件导致已有2名Ashley Madison用户自杀，该偷情网站的母公司Avid Life Media提供50万赏金（[Link](http://www.bbc.com/zhongwen/simp/world/2015/08/150824_world_ashley_madison)）追捕黑客。目前已经公布的线索有2条，一条线索是最早公布了Ashley Madison服务器源代码地址的twitter用户Thadeus Zu (@deuszu)；另一条线索是Ashley Madison的黑客在公布第二批数据后可能不小心留下了足迹([Link](http://arstechnica.com/security/2015/08/ashley-madison-hackers-leave-footprints-that-may-help-investigators/))。

0x02 泄露的主要文件说明
==============

* * *

*   `CreditCardTransactions.7z`  
    该文件保存了过去7年所有信用卡交易记录，包含姓名，地址，EMAIL地址，压缩包里包含2600个EXCEL文件，包含有超过 9.600.000条交易记录。
    
*   `am_am.dump.gz`  
    这个mysql的dump文件包含大概有3200万的用户数据，其中有姓，名，地址，电话号码，关系等，也包括用户是否喝酒？抽烟？生日，别名等信息。
    
*   `aminno_member_email.dump.gz`  
    包含有3200万邮箱地址
    
*   `member_details.dump.gz`  
    人员的详细描述，眼睛颜色，体重，身高，头发颜色等信息
    
*   `member_login.dump.gz`  
    这个文件夹包含3000万的用户名和HASH密码，其中HASH密码采用bcrypt算法加密。
    
*   `ashleymadisondump.7z`里的`swappernet_User_Table.7z`  
    QA数据库服务器的dump文件，但不是标准的mysql dump格式，是csv格式的。这里的userpassword字段没有使用bcrpt算法加密
    
*   `ashleymadison.tgz`  
    包含相关网站的所有gitlab repositories
    

泄露的数据里还包含大概13G的Ashley Madison CEO的邮件内容，但是文件似乎损坏了，需要后续进一步的确认。

0x03 数据库导入
==========

* * *

解压后，通过`grep`看`dump`的文件，可以看到是标准的`mysqldump`文件

```
$ grep 'MySQL dump' *.dump
am_am.dump:-- MySQL dump 10.13  Distrib 5.5.33, for Linux (x86_64)
aminno_member.dump:-- MySQL dump 10.13  Distrib 5.5.40-36.1, for Linux (x86_64)
aminno_member_email.dump:-- MySQL dump 10.13  Distrib 5.5.40-36.1, for Linux (x86_64)
member_details.dump:-- MySQL dump 10.13  Distrib 5.5.40-36.1, for Linux (x86_64)
member_login.dump:-- MySQL dump 10.13  Distrib 5.5.40-36.1, for Linux (x86_64)

```

然后建立相关数据库以及用户，尝试导入。

```
--As root MySQL user
CREATE DATABASE aminno;
CREATE DATABASE am;
CREATE USER 'am'@'localhost' IDENTIFIED BY 'loyaltyandfidelity';
GRANT ALL PRIVILEGES ON aminno.* TO 'am'@'localhost';
GRANT ALL PRIVILEGES ON am.* TO 'am'@'localhost';

```

按照老外的文档。依次执行

```
$ mysql -D aminno -uam -ployaltyandfidelity < aminno_member.dump
$ mysql -D aminno -uam -ployaltyandfidelity < aminno_member_email.dump
$ mysql -D aminno -uam -ployaltyandfidelity < member_details.dump
$ mysql -D aminno -uam -ployaltyandfidelity < member_login.dump
$ mysql -D am -uam -ployaltyandfidelity < am_am.dump

```

![pic1](http://drops.javaweb.org/uploads/images/3706264285469da71d376ea75eb99e3cc544a7bb.jpg)

操作如上图，这里坑就来了，他数据库引擎默认是`innodb`的，导入巨慢。我不知道老外是怎么导的，但是如果你按照他的方法搞，几天也导入不完。我耽误了一个晚上的时间，请教了A神。他告诉我转`MYISAM`导入速度就快了。依照[文档](http://www.jb51.net/article/48946.htm)，禁用`innodb`，新建数据库，表，再次导入，还是慢。因为有些数据在导入的时候，会建索引。所以，需要改造下，思路如下：以`member_details.dump.gz`为例：

```
$ gunzip member_details.dump.gz  #解压

$ wc -l member_details.dump   #计算member_details.dump文件总行数
2425 member_details.dump

$ head -n 48 member_details.dump #获取create的sql语句

CREATE TABLE `member_details` (
  `pnum` int(11) unsigned NOT NULL,
  `eye_color` int(11) unsigned NOT NULL DEFAULT '0',
  `hair_color` int(11) unsigned NOT NULL DEFAULT '0',
  `dob` date DEFAULT NULL,
  `profile_caption` varchar(64) DEFAULT NULL,
  `profile_ethnicity` int(11) unsigned DEFAULT NULL,
  `profile_weight` int(11) unsigned DEFAULT NULL,
  `profile_height` int(11) unsigned DEFAULT NULL,
  `profile_bodytype` int(11) unsigned DEFAULT NULL,
  `profile_smoke` int(11) unsigned DEFAULT NULL,
  `profile_drink` int(11) unsigned DEFAULT NULL,
  `profile_initially_seeking` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`pnum`),
  KEY `dob` (`dob`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

```

把这里的`ENGINE=InnoDB`改为`ENGINE=MYISAM`,如果是其他的表，也可以适当的删除相应SQL里建立索引的语句，提高导入速度。

然后计算`2425 - 48 = 2377`，执行

```
$ tail -n 2377 member_details.dump >member_details.new.dump #删除create相关的sql语句

```

最后回到`MYSQL`里，使用`source`导入数据。

```
soucre member_details.new.dump

```

如下图所示：

![pic2](http://drops.javaweb.org/uploads/images/b8279551e1932c432b13a7afbb68bef01ebc8a63.jpg)

![pic3](http://drops.javaweb.org/uploads/images/9cd58c712f2d289e1ebb62ad438a1f35fd26a1c3.jpg)

0x04 简单数据分析
===========

* * *

首先分析`ashleymadisondump.7z`里的`swappernet_User_Table.7z`,解压后，显示这个数据库包含765607条记录，仅仅有4条是空密码，387974条密码是唯一的。分析语句如下：

```
$ cut -d, -f4 < swappernet_QA_User_Table.txt |wc -l
765607
$ cut -d, -f4 < swappernet_QA_User_Table.txt | sed '/^\s*$/d' |wc -l
765603
$ cut -d, -f4 < swappernet_QA_User_Table.txt | sed '/^\s*$/d' |sort -u |wc -l
387974

```

![pic4](http://drops.javaweb.org/uploads/images/f2d368440088c09a642473d1fcf9e69838119ff1.jpg)

如上图，因为这个数据库的密码是明文的，所以很有价值，我们计算下最常使用的50个密码，语句如下：

```
root@kali:~# cut -d, -f4 <swappernet_QA_User_Table.txt |sort|uniq -c |sort -rn|head -50 
5882 123456
2406 password
950 pussy
948 12345
943 696969
917 12345678
902 fuckme
896 123456789
818 qwerty
746 1234
734 baseball
710 harley
699 swapper
688 swinger
647 football
645 fuckyou
641 111111
538 swingers
482 mustang
482 abc123
445 asshole
431 soccer
421 654321
414 1111
408 hunter
400 sexy
388 michael
381 lovers
379 threesome
375 sunshine
375 monkey
367 hello
339 jennifer
338 master
336 biteme
335 sexsex
334 fucker
332 shadow
331 shithead
330 123123
327 swappernet
327 fuck
326 6969
325 tigger
325 iloveyou
314 robert
312 george
305 buster
302 statueofliberty
300 1234567

```

我这里资源有限,没有用这里统计出来的密码去跑`member_logindump`里的加密密码，但是有个老外用`rockyou`字典去暴力跑，跑出来了4000多个明文密码，下载地址为[Link](https://drive.google.com/folderview?id=0B5SdbPp8F5RVflhkWW16aUtkM2xzd0s3VG5veXRQeHJOMDNfend2LVlITkxVT2JGbG1aU28&usp=sharing)

接下来分析下Ashley Madison里的3700万用户里，通过过滤`reply_mail_last_time`，`bc_chat_last_time`，`bc_mail_last_time`以及个人属性页没有上传图片的（`photos_public`字段），没有验证邮箱地址的（`aminno_member_email.isvalid`)猜测有多少是真实用户。SQL语句如下

```
SELECT 
COUNT(*)
FROM 
aminno_member
LEFT JOIN
aminno_member_email
ON
aminno_member.pnum = aminno_member_email.pnum
WHERE 
(aminno_member.bc_mail_last_time != ‘0000-00-00 00:00:00’ OR 
aminno_member.bc_chat_last_time != ‘0000-00-00 00:00:00’ OR 
aminno_member.reply_mail_last_time != ‘0000-00-00 00:00:00’) AND
photos_public != 0 AND
aminno_member_email.isvalid = 1

```

返回**2,528,767**，大概有250万真实的用户，用户群还是挺庞大的。

0x05 参考文档
=========

* * *

*   [分析显示Ashley Madison上的女性极其罕见](http://www.solidot.org/story?sid=45300)
*   [从破解的4000 Ashley Madison密码中，我们能学到什么](http://arstechnica.com/security/2015/08/cracking-all-hacked-ashley-madison-passwords-could-take-a-lifetime/)
*   [是谁黑了 Ashley Madison ? (通过twitter和facebook调查)](http://krebsonsecurity.com/2015/08/who-hacked-ashley-madison/)
*   [Aug 21 2015: New torrent from Impact Team!](https://yuc3i3hat65rpl7t.onion.to/stuff/impact-team-ashley-release.html)