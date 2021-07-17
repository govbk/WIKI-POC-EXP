# MySQL和PostgreSQL数据库安全配置

0x00 MySQL和PostgreSQL安全配置
=========================

* * *

针对开源数据库MySQL和PostgreSQL的安全配置主要主要通过身份鉴别、访问控制、安全审计、入侵防范、资源控制五个方面来实现。

0x01 身份鉴别
=========

* * *

MySQL和PostgreSQL均可以实现身份鉴别功能。通过设置数据库基本上能够实现能够满足《信息系统安全等级保护基本要求》第三级身份鉴别中大部分要求，但是对于“f 项应采用两种或两种以上组合的鉴别技术对管理用户进行身份鉴别”，需要使用第三方的身份鉴别技术，如：口令、数字证书、生物特征等[2](http://drops.javaweb.org/uploads/images/c13f46abc97e1c6193c7a9dc91436ab18463c357.jpg)。

### （一）、MySQL数据库

MySQL数据库在安装后默认存在mysql数据库，该数据库为系统表所在的数据库，所有用户记录在mysql数据库的user三个权限表的用户列（包括host、user、password三个字段）。

1）对于身份认证MySQL是通过IP地址和用户名进行联合确认的，也就是说“用户名@IP”用来身份认证的唯一标识；

2）安全配置时尽量避免采用默认的用户名root，建议对默认用户名进行重命名，这样增加鉴别信息被猜测的难度；

*   `mysql> update mysql.user set user ='madman' where user='root';`--将root重命名为madman

3）mysql数据库默认无法实现密码更改周期和密码复杂度要求，需要管理员定期更改口令的复杂度，可以通过如下命令设置密码；

*   `mysql>update mysql.user set password=password("12ere@123SWE!@") where User="root" and host="localhost";`--设置密码复杂度
*   `mysql>FLUSH PRIVILEGES;`--刷新权限表

除了密码认证外，MySQL还支持UNIX域套接字，可以在配置文件中指定套接字文件的路径，如—socket=/tmp/mysql.sock，当数据库启动后可以使用UNIX套接字的方式进行认证。

4）针对MySQL5以后的版本建议禁止使用old_password参数，--old-passwords选项的目的是当服务器生成长密码哈希值时，允许你维持同4.1之前的客户端的向后兼容性。在MySQL4.1版本以后建议禁止使用该参数。

5）MySQL数据库也支持SSL远程登录，如果采用本地管理方式则不需要考虑远程连接安全，如果采用远程管理则需要SSL支持。

*   `mysql>SHOW VARIABLES LIKE '%have\_ssl%'；`--查看是否支持ssl的连接特性，若为disabled，说明此功能没有激活。

6）确保所有的身份鉴别的密码具有较强的密码复杂度。

最后，MySQL数据库本身不支持登录次数限制，无法实现针对用户的锁定，具有登录的连接超时设置。

### （二）、PostgreSQL数据库

PostgreSQL 支持丰富的认证方法：信任认证、口令认证、PAM认证等多种认证方式。PostgreSQL 默认配置只监听本地端口，无法通过远程TCP/IP连接数据库。需要修改 postgresql.conf 中的 listen_address 字段修改监听端口，使其支持远程访问。例如`listen\_addresses = '*'`表示监听所有端口。

1.  线上重要数据库禁止使用trust方式进行认证，必须使用md5方式。
2.  重命名数据库超级管理员账户为pgsqlsuper，此帐号由DBA负责人保管，禁止共用；
3.  配置数据库客户端支持SSL连接的配置。客户端认证是由一个配置文件控制的，存放在数据库集群的数据目录里[3]。
    1.  用openssl生成密钥对，创建一个自签名的服务器密匙（server.key）和证书（server.crt）；
    2.  数据库的配置主要通过两个配置文件pg_hba.conf和postgresql.conf来实现；
    3.  开启TCP/IP连接：将postgresql.conf参数tcpip_socket设置为true；
    4.  开启SSL：将postgresql.conf参数ssl设置为true；
    5.  强制局域网内的所有主机以任何PostgreSQL中存在的用户通过TCP+SSL的方式连接到PostgreSQL；
    6.  在pg_hba.conf文件中增加记录：hostssl all all 192.168.54.1/32 md5。
4.  postgresql中还可以通过pg_user系统表的valuntil字段实现用户口令失效的时间(只用于口令认证)。

0x02 访问控制
=========

* * *

MySQL和PostgreSQL均可以实现访问控制功能。

### （一）、MySQL数据库

MySQL权限系统通过两个阶段进行权限认证：

1.  对连接的用户进行身份认证，合法的用户通过认证，不合法的用户拒绝连接；
2.  对通过认证的合法用户赋予相应的权限，用户可以在这些权限范围内对数据库做相应的操作。MySQL中主要权限存储在MySQL系统库的user、host、db三个系统表中。这三个表中包括权限列，其中权限列包括普通权限和管理权限。普通权限主要用于数据库的操作，比如select_priv、create_priv等；而管理权限主要用来对数据库进行管理的操作，比如process_priv、super_priv等。表1说明了mysql权限系统表

当用户进行连接的时候，权限表的存取过程有以下两个阶段。

1.  先从user表中的host、user和password这三个字段中判断连接的IP、用户名和密码是否存在于表中，如果存在，则通过身份验证，否则拒绝连接。
2.  如果通过身份验证，则按照以权限表的顺序得到数据库权限：userdbtable_privcolumns_priv，即先检查全局权限表user，如果user中对应的权限为Y，则此用户对所有数据库的权限都为Y，将不再检查db, tables_priv,columns_priv；如果为N，则到db表中检查此用户对应的具体数据库，并得到db中为Y的权限；如果db中为N，则检查tables_priv中此数据库对应的具体表，取得表中的权限Y，以此类推。这几个权限表中，权限范围一次递减，全局权限覆盖局部权限。

通过上述介绍，可知在配置权限时需要根据数据库业务使用的情况配置合理的权限。

1)尽量最小化权限的配置，可以通过如下命令查看权限。

*   `mysql> select * from mysql.user\G`--检查用户权限列
*   `mysql> select * from mysql.db\G`--检查数据库权限列
*   `mysql> select * from mysql.tables_priv\G`--检查用户表权限列
*   `mysql> select * from mysql.columns_priv\G`--检查列权限列

2)业务系统在使用时，也可以通过视图控制对基础表的访问；

3)通过合理的权限配置进行访问控制外，还需要将DBA管理和应用账号严格分离，不同应用单独账号，删除数据库相关的历史操作记录，避免信息泄露。

4)对于MySQL数据库自身不具备强制访问控制（MAC），强制访问控制（MAC）是系统强制主体服从访问控制策略。与自主访问控制（DAC）基于系统实现身份认证及其到系统资源的介入授权方式，共同保证用户的权限。

a、创建系统表：为了实现可定制强制访问控制，需定义用户的强制访问权限管理表，系统需要对MySQL原有的数据字典进行改造[3]，增加系统表。

b、修改用户认证逻辑 在sql_acl.cc中修改用户验证逻辑，检查强制访问权限管理表，是否符合用户认证要求。

### （二）、PostgreSQL数据库

PostgreSQL将所有的数据库对象都存放在系统表空间，所有的系统表都以pg开头。PostgreSQL采用基于角色的访问控制机制，通过角色机制，简化了用户和权限的关联性。PostgreSQL系统中的权限分为两种：系统权限和对象权限。

系统权限是指系统规定用户使用数据库的权限（如连接数据库、创建数据库、创建用户等），系统角色属性有LOGIN、PASSWORD、SUPERUSER、CREATEDB、CREATEROLE、INHERIT等。

对象权限是指在表、序列、函数等数据库对象上执行特殊动作的权限，其权限类型有select、insert、update、delete、references、trigger、create、connect、temporary、execute和usage等。

有关角色属性信息可以在系统表pg_authid中找到。另外pg_roles是系统表pg_authid公开课度部分的视图。系统表pa_auth_members存储了角色之间的成员关系

1)根据最小权限要求给用户配置角色和权限。

*   `postgres=# select * from pg\_authid;`--查看用户具有的角色

为了保护数据安全，当用户对某个数据库对象进行操作之前，必须检查用户在对象上的操作权限。访问控制列表（ACL）是对象权限管理和权限检查的基础，在PostgreSQL通过操作ACL实现对象的访问控制管理。所有表的基本定义保存在系统表pg_class中，除了包括表，视图、序列和索引(与其他许多系统不同，PG的索引也被视作一个类，事实上索引项无论在逻辑组成还是物理结构上都类似一个表的元组。)等对象的基本定义外，它的relacl属性中为每个对象维护一个ACL[5]。Relacl是PostgreSQL支持的数组属性，该数组成员是抽象的数据类型aclitem。这些aclitem作为对象访问控制权限的ACE（ACL是存储控制箱（Access Control Entruy，ACE）的集合，每个ACL实际上是一个由多个aclitem构成的链表，ACE由数据库对象和权限列表构成，记录着可访问兑现的用户或者执行单元（进程、存储过程等））共同组成对象的ACL。

![p1](http://drops.javaweb.org/uploads/images/c62571c6963e357b710d2c1d7aea3ac2a894a6cd.jpg)

图1：ACL权限信息。

2）根据系统提示可以查看对象的ACL列表，已确定用户对对象的访问权限。

*   `postgres=# \dp pg_roles;`--\dp 后接表名或视图名查看对象权限

3) 通过合理的权限配置进行访问控制外，还需要将DBA管理和应用账号严格分离，不同应用单独账号，删除数据库相关的历史操作记录，避免信息泄露。

4)对postgresql进行源代码修改以实现强制访问控制（MAC），SQL语句在经过DDL与DML处理时，需要进行MAC检查，通过检查的数据才能输出给用户，否则只能返回错误信息[5]。

0x03 安全审计
=========

* * *

商业数据库均有安全审计功能，通过相关配置，能够对系统的重要事件进行安全审计目前MySQL数据库具有基本的日志功能，通过日志数据挖掘可以实现安全审计功能，但其实现起来较为复杂。PostgreSQL具备了良好的审计功能。

### （一）、MySQL数据库

MySQL日志主要包含：错误日志、查询日志、慢查询日志、二进制日志等，日志主要功能如下：

*   错误日志：错误日志主要为了实现数据库排错。默认情况下错误日志大概记录以下几个方面的信息：服务器启动和关闭过程中的信息、服务器运行过程中的错误信息等跟系统错误有关的日志。
*   查询日志：查询日志主要为了实现数据库调试。由于查询日志会记录用户的所有操作，其中还包含增删查改等信息，在并发操作大的环境下会产生大量的信息从而导致不必要的磁盘IO，会影响mysql的性能的。
*   慢查询日志：慢查询日志是用来记录执行时间超过指定时间的查询语句。通过慢查询日志，可以查找出哪些查询语句的执行效率很低，以便进行优化。
*   二进制日志：二进制日志也叫更新日志，主要用于记录修改数据或有可能引起数据改变的mysql语句，并且记录了语句发生时间、执行时长、操作的数据等等。

通过上述描述可以看出，对于MySQL来说可以通过日志分析来实现数据库审计功能，但是这样的工作量对DBA来说比较繁琐，也不利于集中控制数据库产生的安全审计记录。MySQL企业级已经实现了针对MySQL的安全审计功能，但开源MySQL数据库没有实现安全审计功能。要实现MySQL数据库的安全审计功能，需要对MySQL源代码进行修改，目前已经有成熟的插件来实现MySQL数据库审计功能。

1)MySQL审计插件：MariaDB数据库管理系统是MySQL的一个分支，其server_audit审计插件能工作在mariadb、mysql和percona server，通过安装审计插件来实现MySQL的审计功能。

a、安装审计插件，将server_audit.so 文件拷贝到MySQL/MariaDB 下的 lib/plugin 目录，并通过如下命令激活该插件：

```
mysql> INSTALL PLUGIN server_audit SONAME 'server_audit.so';

```

b、修改mysql配置文件my.cnf的审计参数

```
server_audit    =FORCE_PLUS_PERMANENT
server_audit_events ='CONNECT,QUERY,TABLE'
server_audit_logging    =ON
server_audit_incl_users =root
server_audit_file_rotate_size   = 1G
server_audit_file_path  = /usr/local/mysql/mysql_logs/auditlog/server_audit.log

```

c、查看审计配置参数，可以通过下面的命令查询审计参数配置情况。

```
mysql> SHOW global VARIABLES LIKE '%audit%';

```

![p2](http://drops.javaweb.org/uploads/images/c13f46abc97e1c6193c7a9dc91436ab18463c357.jpg)

图1：审计配置参数

表1：PostgreSQL数据库安全审计配置参数

| 配置参数 | 参数说明 |
| --- | --- |
| server_audit_logging | 启动或关闭审计 |
| server_audit_events | 指定记录事件的类型，可以用逗号分隔的多个值(connect,query,table)，如果开启了查询缓存(query cache)，查询直接从查询缓存返回数据，将没有table记录 |
| server_audit_file_rotate_size | 限制日志文件的大小 |
| server_audit_file_rotations | 指定日志文件的数量，如果为0日志将从不轮转 |
| server_audit_incl_users | 指定哪些用户的活动将记录，connect将不受此变量影响，该变量比server_audit_excl_users优先级高 |

2)通过设置严格的访问控制权限确保审计日志的安全性。

3)通过对审计日志的格式等进行分析实现审计报表的输出。

### （二）、PostgreSQL数据库

审计是值记录用户的登录退出以及登录后在数据库里的行为操作，可以根据安全等级不一样设置不一样级别的审计。默认需设置具有如下的安全配置参数：

表2：PostgreSQL数据库安全审计配置参数

| 配置参数 | 参数说明 |
| --- | --- |
| logging_collector | 是否开启日志收集开关，默认off，开启要重启DB |
| log_destination | 日志记录类型，默认是stderr，只记录错误输出 |
| log_directory | 日志路径，默认是$PGDATA/pg_log |
| log_filename | 日志名称，默认是postgresql-%Y-%m-%d_%H%M%S.log |
| log_connections | 用户session登陆时是否写入日志，默认off |
| log_disconnections | 用户session退出时是否写入日志，默认off |
| log_rotation_age | 保留单个文件的最大时长,默认是1d |
| log_rotation_size | 保留单个文件的最大尺寸，默认是10MB |

PostgreSQL日志里分成了3类，通过参数pg_statement来控制，默认的pg_statement参数值是none，即不记录，可以设置ddl(记录create,drop和alter)、mod(记录ddl+insert,delete,update和truncate)和all(mod+select)。

1）配置logging_collector、pg_statement、log_connections和 log_disconnections参数，确保登录连接、退出连接和用户DDL、DML等行为能被记录；

2）配置日志文件名称、大小、保留周期等满足相关要求；

3）确保所有的审计记录的权限满足操作系统的权限要求。

0x04 入侵防范
=========

* * *

针对数据库的安全防范主要体现在数据库补丁更新，特定函数的使用等方面。

### （一）、MySQL数据库

1.  严格控制操作系统账号和权限
    1.  锁定mysql用户不能登录；
    2.  其他任何用户都采用独立的账号登录，管理员通过mysql专有用户管理MySQL，或者通过su到mysql用户下进行管理。
    3.  mysql用户目录下，除了数据文件目录，其他文件和目录属主都改为root。
2.  删除匿名账号；
3.  不要把file、process或super权限授予管理员以外的账号；
4.  进制load data local文件读取操作的使用，避免读取操作系统的重要文件到数据库表中；
5.  在已有的生产库上建议进制使用safe-user-create参数的使用，避免用户使用grant语句创建新用户；
6.  及时更新MySQL安全补丁。

### （二）、PostgreSQL数据库

1.  严格控制操作系统的账号和权限，确保启动进程具有最小的权限；
2.  严格控制数据库安装目录的权限，除了数据文件目录，其他文件和目录属主都改为root。
3.  及时更新数据库bug和安全补丁。

0x05 资源控制
=========

* * *

资源控制主要保证数据库的资源不被非法的占用。

### （一）、MySQL数据库

MySQL中主要权限存储在MySQL系统库的user系统表的资源列中可以控制用户连接数、最大请求数、最大更新数、最大连接等信息。但最大用户连接数为较长用的资源控制项，其他选项需更具数据的使用情况进行安全配置。

*   MAX_QUERIES_PER_HOUR 用来限制用户每小时运行的查询数量
*   MAX_UPDATES_PER_HOUR 用来限制用户每小时的修改数据库数据的数量。
*   MAX_CONNECTIONS_PER_HOUR用来控制用户每小时打开新连接的数量。
*   MAX_USER_CONNECTIONS 限制有多少用户连接MYSQL服务器。

1.  针对每个用户限制MAX_USER_CONNECTIONS参数，即限制用户最大连接数。
2.  针对每个用户限制其来源地址限制，即每个用户仅允许唯一的IP地址访问，必要时禁止远程连接mysql ，设置skip-networking参数。

### （二）、PostgreSQL数据库

PostgreSQL对于资源限制主要体现在用户最大并发连接数的限制上。具体可以进行如下安全配置。

1）postgresql数据库可以进行严格的地址限制，确保用户来源可信。

2）配置用户最大并发连接数量。

*   `postgres=# select * from pg_authid;`#查看限制其最大并发连接数量

3）postgresql具有默认的连接超时策略。

0x06 参考文献
=========

* * *

*   【1】 《关于应用安全可控信息技术加强银行业网络安全和信息化建设的指导意见》[ON/EL].http://www.cbrc.gov.cn/govView_EE29BABB27EB4E51A4343517691438F9.html
*   【2】 邱梓华，宋好好，张笑笑，顾健,主机安全等级保护配置指南[J].信息网络安全，2011年增刊，112～113
*   【3】 杨玉杰，韩昧华，王永刚，PostgreSQL的安全数据传输[J]，聊城大学学报（自然科学版），第23卷第1期，89～90
*   【4】 吴飞林，王晓艳，郎波，基于MySQL的可定制强制访问控制的研究与实现[J].计算机应用研究，第24卷第11期,119
*   【5】 张孝，PostgreSQL中基于ACL的数据访问控制技术[J]，计算机应用和软件，第24卷第9期，68
*   【6】 刘欣，沈昌祥，基于PostgreSQL的强制访问控制的实现[J]，计算机工程，第32卷第2期，50