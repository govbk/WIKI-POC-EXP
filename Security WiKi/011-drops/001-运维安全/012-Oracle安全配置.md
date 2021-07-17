# Oracle安全配置

操作系统：window server 2008 x64 oracle：oracle 11.2.0.1.0

0x02 oracle权限介绍
---------------

* * *

1.  oracle一个实例就是一个数据库，创建一个新的数据库会产生一个新的实例，并且一个实例独立运行一个进程。
2.  一个用户对应一个方案，当用户新建一个数据对象（比如表）之后会在此方案下面。自己访问可以直接访问，其他用户访问需通过“方案名.对象名”的方式。
3.  用户默认拥有自己方案下面的数据对象的权限，其他用户无相应权限。sys，system默认拥有所有方案的权限。
4.  当一个用户登录oracle实例时，首先需要判断用户是有否登录权限，如果没有，直接不能登录，如果有，则登录成功。登录成功之后，会根据用户拥有的权限来决定能做的事情，在进行一项操作时，如果有权限，则操作成功，如果没有权限，则操作失败。
5.  oracle主要有两个核心进程，一个是oracle的服务进程，一个是监听进程，当外部连接oracle时，首先是访问的监听进程，由监听进程根据你访问的数据库实例来转发到相应的oracle实例进程处理。

0x03 oracle系统服务
---------------

* * *

在window server 2008中安装的oracle 11g总共会有七个服务，这七个服务的含义分别为：

### a. Oracle ORCL VSS Writer Service：

Oracle卷映射拷贝写入服务，VSS（Volume Shadow Copy Service）能够让存储基础设备（比如磁盘，阵列等）创建高保真的时间点映像，即映射拷贝（shadow copy）。它可以在多卷或者单个卷上创建映射拷贝，同时不会影响到系统的系统能。（非必须启动）

### b. OracleDBConsoleorcl：

Oracle数据库控制台服务，orcl是Oracle的实例标识，默认的实例为orcl。在运行Enterprise Manager（企业管理器OEM）的时候，需要启动这个服务。（非必须启动）

### c. OracleJobSchedulerORCL：

Oracle作业调度（定时器）服务，ORCL是Oracle实例标识。（非必须启动）

### d. OracleMTSRecoveryService：

服务端控制。该服务允许数据库充当一个微软事务服务器MTS、COM/COM+对象和分布式环境下的事务的资源管理器。（非必须启动）

### e. OracleOraDb11g_home1ClrAgent：

Oracle数据库.NET扩展服务的一部分。 （非必须启动）

### f. OracleOraDb11g_home1TNSListener：

监听器服务，服务只有在数据库需要远程访问的时候才需要。（非必须启动，但是供外部访问则必须启动）。

### g. OracleServiceORCL：

数据库服务(数据库实例)，是Oracle核心服务该服务，是数据库启动的基础， 只有该服务启动，Oracle数据库才能正常启动。(必须启动)

那么在开发的时候到底需要启动哪些服务呢？

对新手来说，要是只用Oracle自带的sql*plus的话，只要启动OracleServiceORCL即可，要是使用PL/SQL Developer等第三方工具的话，OracleOraDb11g_home1TNSListener服务也要开启。OracleDBConsoleorcl是进入基于web的EM必须开启的，其余服务很少用。

0x04 oracle默认账户
---------------

* * *

在oracle11g安装后，会有很多系统默认账号，除了4个外，其他的都处于锁定状态，如无特殊用途，请不要打开。另外4个分别为：

1.  SYS用户 SYS，当创建一个数据库时，SYS用户将被默认创建并授予DBA角色，所有数据库数据字典中的基本表和视图都存储在名为SYS的方案中，这些基本表和视图对于Oracle数据库的操作是非常重要的。为了维护数据字典的真实性，SYS方案中的表只能由系统来维护，他们不能被任何用户或数据库管理员修改，而且任何用户不能在SYS方案中创建表。
    
2.  SYSTEM用户 SYSTEM，与SYS一样，在创建Oracle数据库时，SYSTEM用户被默认创建并被授予DBA角色，用于创建显示管理信息的表或视图，以及被各种Oracle数据库应用和工具使用的内容表 或视图。
    
3.  DBSNMP用户 DBSNMP是Oracle数据库中用于智能代理（Intelligent Agent）的用户，用来监控和管理数据库相关性能的用户，如果停止该用户，则无法提取相关的数据信息。
    
4.  SYSMAN用户 SYSMAN是Oracle数据库中用于EM管理的用户，如果你不用该用户，也可以删除或者锁定。
    

以上4个账户的密码均为安装时候设置的密码，由于一般情况下，DBSNMP和SYSMAN用户不会被使用而被遗漏，建议锁定。

0x05 oracle权限和角色
----------------

* * *

### a.权限

oracle权限分为系统权限和对象权限，当刚刚建立用户时，用户没有任何权限，也不能执行任何操作。如果要执行某种特定的数据库操作，则必须为其授予系统的权限。如果用户要访问其他方案的对象，则必须为其授予对象的权限。

系统权限是指执行特定类型Sql命令的权利，它用于控制用户可以执行的一个或是一组数据库操作。比如当用户具有create table权限是，可以在其方案中建表，当用户具有create any table权限时，可以在任何方案中建表。Oracle提供了100多种系统权限。

常见的系统权限见下表：

<table class="MsoNormalTable" border="0" cellspacing="0" cellpadding="0" width="369" style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box; height: 13.5pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border: 1pt solid windowtext; width: 127.6pt; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create session</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: 1pt solid windowtext; border-image: initial; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">连接数据库</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 127.6pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create view</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">创建视图</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 127.6pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create procedure</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">创建过程、函数、包</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 127.6pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create cluster</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">建簇</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 127.6pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create table</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">创建表</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 127.6pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create public synonym</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">创建同义词</span></p></td></tr><tr style="box-sizing: border-box; height: 14.25pt;"><td width="170" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 127.6pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 14.25pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">create trigger</span></p></td><td width="198" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 148.85pt; border-top: none; border-left: none; height: 14.25pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">创建触发器</span></p></td></tr></tbody></table>

常见的对象权限见下表：

<table class="MsoNormalTable" border="0" cellspacing="0" cellpadding="0" width="272" style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border: 1pt solid windowtext; width: 89pt; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box;">alter</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: 1pt solid windowtext; border-image: initial; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">修改表结构</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">delete</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">删除数据</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">select</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">查询数据</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">insert</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">添加数据</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">update</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">修改数据</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">index</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">在表上建立索引</span></p></td></tr><tr style="box-sizing: border-box; height: 13.5pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">references</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 13.5pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">引用</span></p></td></tr><tr style="box-sizing: border-box; height: 14.25pt;"><td width="119" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 89pt; border-left: 1pt solid windowtext; border-image: initial; border-top: none; height: 14.25pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span lang="EN-US" style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">execute</span></p></td><td width="153" nowrap="" valign="bottom" style="box-sizing: border-box; padding: 0cm 5.4pt; border-bottom: 1pt solid windowtext; border-right: 1pt solid windowtext; width: 115pt; border-top: none; border-left: none; height: 14.25pt;"><p class="MsoNormal" align="left" style="box-sizing: border-box; margin: 20px 0px; text-align: left;"><span style="box-sizing: border-box; font-size: 11pt; font-family: 宋体; color: black;">执行</span></p></td></tr></tbody></table>

注：可以用all代替select, update, insert, alter, index, delete

### b. 角色

oracle角色分为系统角色和自定义角色，自定义角色可以根据需要指定相应的权限，系统角色主要介绍下面3个：

DBA: 拥有全部特权，是系统最高权限，只有DBA才可以创建数据库结构。

RESOURCE:拥有Resource权限的用户只可以创建实体，不可以创建数据库结构。

CONNECT:拥有Connect权限的用户只可以登录，不可以创建实体和数据库结构。

对于普通用户：授予connect, resource角色。

对于DBA管理用户：授予connect，resource, dba角色。

0x06 oracle如何建立网站连接用户
---------------------

* * *

方案一：

1.  使用system新建一个用户名，给予connect，resource 的角色
    
2.  使用新建的用户登录，然后创建需要的表
    
3.  使用system登录，revoke新建用户的connect，resource角色
    
4.  使用system登录，grant新建用户create session 权限
    
5.  使用system登录，给予新建用户在USERS表空间的权限
    

方案二：

1.  使用system登录，创建网站需要的表
    
2.  使用system登录，创建一个用户名
    
3.  使用system登录，grant新建用户create session的系统权限，然后根据网站的需要给予所建表的相应的对象权限。
    
4.  使用system登录，给予新建用户在USERS表空间的权限
    
5.  网站访问数据库的时候使用“system.表名”的形式。
    

0x07 oracle安全配置方案
-----------------

* * *

### 1. 限制访问ip

方法一：

防火墙指定，windows中通过windows防火墙中指定监听端口的访问ip，linux中通过iptables指定监听端口的访问ip。

方法二：

windows中可通过ipsec指定监听端口的访问ip。

方法三：

可通过oracle的监听器中指定可访问的ip 在服务器上的文件$ORACLE_HOME/network/admin/sqlnet.ora中设置以下行：

```
tcp.validnode_checking = yes

```

允许访问的ip

```
tcp.invited_nodes = (ip1,ip2…)

```

不允许访问的ip

```
tcp.excluded_nodes=(ip1,ip2,……)

```

1.  修改端口 可以修改监听器的端口，减少扫描量
    
2.  关闭不必要的服务 可以关闭不必要的服务来减少对外访问，除了OracleServiceORCL和OracleOraDb11g_home1TNSListener是必须开启的之外，其他的均可以关闭。特别是OracleDBConsoleorcl服务的开启会启用web版的EM，访问端口在1158，如不需要请关闭此服务。
    
3.  所有的用户均需设置强密码 在设置密码的时候均需要设置8位以上的强密码，且包含大小写，数字，特殊字符。
    
4.  关闭不需要的用户 oracle默认会有4个不锁定的账户，建议锁定DBSNMP和SYSMAN。
    
5.  特权账户的处理 限制数据库超级管理员远程登录。 a. 在spfile中设置 REMOTE_LOGIN_PASSWORDFILE=NONE b.在sqlnet.ora中设置 SQLNET.AUTHENTICATION_SERVICES=NONE 禁用SYSDBA角色的自动登录
    
6.  开启日志 可以开启日志对数据库进行审计,但是也会消耗资源，可根据实际情况操作。
    
7.  网站使用的数据库账号权限最小化 可以根据上面写的网站连接数据库账户推荐的方案建立。
    
8.  合理使用数据库进程账户 数据库进程账户使用较低权限账户,新建一个新用户，添加数据目录的写权限，如果配置之后跑不起来，可以退而求其次，给予整个数据库目录的完全控制权限。
    
9.  合理配置数据库进程账户对磁盘的权限 不要给予数据库目录以外的特殊权限，最好是读取权限都不给，可以根据实际情况来安排，原则就是数据库目录给的权限能保证正常运行，其他的目录能不给就不给。
    

0x08 oracle提权及防御点
-----------------

* * *

### 1. 通过PL/SQL提权

```
create or replace library exec_shell as '$ORACLE_HOME\bin\msvcrt.dll';  
create or replace procedure execmd (command in char) is external name "system" library exec_shell language c; / exec execmd('net user >netaaa.txt');

```

### 2. 使用java提权

```
CREATE OR REPLACE AND RESOLVE JAVA SOURCE NAMED "JAVACMD" AS import java.lang.*; import java.io.*; public class JAVACMD { public static void execCommand (String command) throws IOException { Runtime.getRuntime().exec(command); } }; / CREATE OR REPLACE PROCEDURE JAVACMDPROC (p_command IN VARCHAR2) AS LANGUAGE JAVA NAME 'JAVACMD.execCommand (java.lang.String)'; / exec javacmdproc('cmd.exe /c net user > netaaa.txt');

```

以上两种方法如果使用sys均可以提权成功，而普通权限用户是无法完成上面的操作的。所以防御源头还是只能对sys特权账户的管理，但是如果真的特权账户被黑客获取，此时的方法也只有使用低权限的数据库进程账户，以及控制进程账户对磁盘的权限，这样操作能将黑客能够操作的权限降到最低。 至于先对低权限的oracle账户提升为dba权限，然后进行系统提权的操作本文不讨论，也请大牛提供更好的方法。

0x09 oracle常见操作命令
-----------------

* * *

### 1. 连接数据库

```
conn sys/mima@orcl as sysdba;

```

### 2. 新建用户

```
create user yonghuming identified by mima;

```

### 3. 给用户授权

```
grant connect, resource to yonghuming; grant create session to yonghuming; alter user yonghuming quota unlimited on USERS; grant unlimited tablespace to yonghuming; grant select on testable to yonghuming;

```

### 4. 取消授权

```
revoke connect , resource from yonghuming;

```

### 5. 删除锁定（解锁）账号

```
alter user yonghuming lock; alter user yonghuming unlock; drop user yonghuming cascade;
```
