# 一种新型的OLAP DML 注入攻击

对于使用了`DBMS_AW`、`OLAP_TABLE`或任何`OLAP*函数`的`Oracle OLAP`应用程序来说，都将面临着一种新型的注入威胁。归根结底，这是由于`SQL`和`OLAP DML`之间的语法差异所导致的。最终结果就是，攻击者可以利用这一点，以较高的权限来执行任意的SQL操作。

0x01 导言
=======

* * *

联机分析处理(`OLAP`)通常用来查询多维数据。在`Oracle`中，可以创建分析工作区(`Analytic Workspace`)来存储待分析的数据、计算公式和模型等计算对象以及执行分析的各种程序。这里的计算对象及程序都是使用`OLAP DML`编写的。需要注意的是，`OLAP DML`不同于`SQL`，因为它们具有不同的语法。

举例来说，在`SQL`中,--用于单行注释，/**/用于多行注释。而OLAP DML中的注释则是用双引号"来表示。一个分号(;)可以用于分隔单行上的各个`OLAP DML`命令，而一条命令被拆分为两行的时候，则使用单个减号作为续行符。

`OLAP DML`可以从`SQL`中执行，但是需要借助于接收`OLAP DML`的接口。这包括`DBMS_AWPL/SQL包`、`OLAP_TABLE函数`以及其他`OLAP函数`（比如`OLAP_CONDITION`和`OLAP_EXPRESSION`）。

另外，还有许多`OLAP DML命令`和函数以及一些SQL命令系列也可以从`OLAP DML`来执行。

0x02 OLAP DML注入攻击
=================

* * *

本文介绍的新型注入攻击，主要出现在用户的输入被传递给`OLAP函数`或`DBMS_AW包`的时候。即使该输入对于SQL来说是合法的，甚至使用的是约束变量，这种风险依然存在。基本上，攻击者可以将任意SQL语句嵌入到一条`OLAP DML语句`中，并以较高的权限执行之。

下面给出一个实际例子。`DROP_AW_ELIST_ALL`是Oracle提供的一个存储过程，相应代码如下所示：

![enter image description here](http://drops.javaweb.org/uploads/images/725a7b49dff8f83b32a22489a76da2b70dac2917.jpg)![enter image description here](http://drops.javaweb.org/uploads/images/ef34900468c3930250b8c61a8c1331fc8a9fa2ac.jpg)

在这里我们可以看到，`DBMS_ASSERT`是用来确保在"`MYSCHEMA`"和"`AWNAME`"这两个用户提供的参数中没有嵌入式的`SQL`的。一旦通过了验证，它们就会被传递给存储过程`DBMS_AW.EXECUTE`，并执行`OLAP DML`命令"`AW ATTACH`"。

但是我们仍然能够向这个调用中“夹带”进任意的`OLAP DML命令`，方法是用双引号括住一个伪造的`AWNAME`，并在分号后面加上另外的命令。在下面的例子中，我们执行`OLAP DML`命令`SQL PROCEDURE`的时候，会顺带执行一个`PL/SQL`的存储过程，就本例来说就是`DBMS_OUTPUT.PUT_LINE`。

![enter image description here](http://drops.javaweb.org/uploads/images/e07afba809168a80e8f318deffc49ead7fc1e94a.jpg)

请注意上面输出中的SYS。

另外的一个实例是在`DBMS_AW.AW_ATTACH`这个存储过程中发现的。实际上，`DBMS_AW`的大多数存储过程和函数都有此安全漏洞。`DBMS_AW.AW_ATTACH`在取得`AW`名称后，会将其传递给`GEN_DBNAME()`。`GEN_DBNAME()`函数会利用`DBMS_ASSERT.QUALIFIED_SQL_NAME()`对这个AW名称进行检查，以验证输入的合法性。

同样，这里攻击者也能夹带任意`OLAP DML`，并从这里执行`SQL`。

![enter image description here](http://drops.javaweb.org/uploads/images/6dc5c969d9c805524c82c31d99e28509c4b417e2.jpg)

在上面的攻击中，通过使用双引号，攻击者就可以绕过`DBMS_ASSERT.QUALIFIED_SQL_NAME`的输入验证了。不要忘了，`OLAP DML`也会看到这个双引号，并将其视为一个注释符。然后，攻击者可以提供一个连字符，这样就能够将`OLAP DML`命令`AW ATTACH`分为两行。再后面是一个分号，这样攻击者就能够执行其后的`OLAP DML`命令（在本例中就是调用`SQL PROCEDURE`）了，然后以双引号结束。这样一来，用户的输入不但绕过了`DBMS_ASSERT.QUALIFIED_SQL_NAME`，`OLAPDML`还会将其视为一个注释符号。

当处理`OLAP_TABLE`函数时，如果有任何用户输入被传递给了第三个参数，其本来就是要接收一个`OLAP DML`命令，或者是传递给了第四个参数`LIMIT_MAP`，那么攻击者就能够执行任意的`OLAP DML`了。

下面我们以一个专门设计的例子来进行说明。下面中的前几行代码，只是为展示这个安全问题而做了一些简单的设置工作：

![enter image description here](http://drops.javaweb.org/uploads/images/4712191dd975218f5b5f396c5d268150461bb7fa.jpg)

在这里，我们想在视图中使用`OLAP_TABLE`，并从一个名为`XLNAME`的分析工作区变量中读入`LIMIT_MAP`。即使用户没有写`AW`的权限，他们仍然能够修改自己私有的副本。这个私有的副本可以用于`AW`对象的访问。因此，如果用户`DAVID`连接并发送下列内容，他就能够重写`XLNAME`，从而直接影响`OLAP_TABLE`的参数`LIMIT_MAP`。利用关键字`PREDMLCMD`，`DAVID`就可以执行任意的`OLAP DML`命令了。

![enter image description here](http://drops.javaweb.org/uploads/images/b02e9a661f600bfc97d0337bf36ce4b65f36441a.jpg)

需要注意的是，上面`SYS_CONTEXT('USERENV','CURRENT_USER')`函数的输出为`DAVID`。这表明，`OLAP DML`及其后来的`SQL`命令都是以当前用户的身份来执行的，而不是以该视图的属主的身份来执行的。为了利用这一点来获得更高的权限，用户`DAVID`需要将这个视图传递给一个具有定义者权限的PL/SQL包或能够操作任意数据表的存储过程。实际的例子有很多，但是为了便于说明，我们专门设计的例子涉及`¬SELECT_FROM_TABLE`，这里存储过程的属主为SYS：

![enter image description here](http://drops.javaweb.org/uploads/images/858391d9b025dff2d1393a829eefa9fadb78533e.jpg)

0x03 小结
=======

* * *

如果开发人员在`PL/SQL`包中使用了`DBMS_AW`，存储过程或函数使用了定义者权限，并且用户的输入被传递给`DBMS_AW`，那么，即使输入内容通过了SQL级别的验证，或者即使使用了约束变量，攻击者仍然能够执行任意`OLAP DML`命令，并且是以`PL/SQL包`属主的身份从任意的SQL中执行。同样的，如果开发人员在用到定义者权限的`PL/SQL`包中使用了`OLAP_TABLE`或任何其他`OLAP函数`，那么攻击者就可以利用用户输入来发动类似的攻击。如果`OLAP_TABLE`被用于视图中，并且该视图可以像上面例子中那样允许随后加以处理，同时可以通过PL/SQL包来访问该视图的话，那么同样也会遭受类似的注入攻击。

`OLAP`应用程序的开发人员必须对所有的用户输入进行仔细检查，以确保用户输入中没有“夹带”任何`OLAP DML`命令。为此，通常需要拒绝任何含有连字符、双引号或分号的内容，当然，这还要考虑到具体应用程序的特殊情况。