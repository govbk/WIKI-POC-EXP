# 论PHP常见的漏洞

0x00 前言
=======

* * *

里面很多都是像laterain学习到的, 如果能考上cuit的话 自动献菊花了。

0x01 安装的问题
==========

* * *

首先拿到一份源码 肯定是先install上。 而在安装文件上又会经常出现问题。

一般的安装文件在安装完成后 基本上都不会自动删除这个安装的文件 我遇到过的会自动删除的好像也就qibocms了。

其他的基本都是通过生成一个lock文件 来判断程序是否安装过了 如果存在这个lock文件了 就会退出了。 这里首先 先来说一下安装文件经常出现的问题。

根本无验证。
------

* * *

这种的虽然不多 但是有时还是会遇到个。 在安装完成后 并不会自动删除文件 又不会生成lock来判断是否安装过了。 导致了可以直接重装过

例子:[WooYun: PHPSHE B2C 重装。](http://www.wooyun.org/bugs/wooyun-2014-062047)

安装file
------

* * *

因为install 一般都会有step 步骤啥的。。 Step 1 check 啥啥 step 2 是安装啥的。 而一些cms 默认step是1 而step又是GET 来的 而他check lock的时候就是在step1里面。 这时候如果我们直接用GET提交step 2 那么就直接进入下一步了 就没check lock了。

例如某cms中的安装文件

```
if (empty ($step))
{
    $step = 1;//当用户没有提交step的时候 赋值为1
}
require_once ("includes/inc_install.php");
$gototime = 2000;

/*------------------------
显示协议文件
------------------------*/
if ($step == 1) //当1才检测lock
{
    if (file_exists('installed.txt'))
    {
        echo '<html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        </head>
        <body>
        你已经安装过该系统，如果想重新安装，请先删除install目录下的 installed.txt 文件，然后再安装。
        </body>
        </html>';
        exit;
    }
    include_once ("./templates/s1.html");
    exit ();
}

/*------------------------
测试环境要求
------------------------*/
else
    if ($step == 2) // 我们直接提交step为2 就不check lock了
    { 
        $phpv = @ phpversion();
        $sp_os = $_ENV["OS"];
        $sp_gd = @ gdversion();
        $sp_server = $_SERVER["SERVER_SOFTWARE"];
        $sp_host = (empty ($_SERVER["SERVER_ADDR"]) ? $_SERVER["SERVER_HOST"] : $_SERVER["SERVER_ADDR"]);
        $sp_name = $_SERVER["SERVER_NAME"];
        $sp_max_execution_time = ini_get('max_execution_time');
        $sp_allow_reference = (ini_get('allow_call_time_pass_reference') ? '<font color=green>[√]On</font>' : '<font color=red>[×]Off</font>');
        $sp_allow_url_fopen = (in

```

变量覆盖导致重装
--------

* * *

```
header("Content-Type: text/html; charset={$lang}");     
foreach(Array('_GET','_POST','_COOKIE') as $_request){     
    foreach($$_request as $_k => $_v) ${$_k} = _runmagicquotes($_v);     
}     
function _runmagicquotes(&$svar){     
    if(!get_magic_quotes_gpc()){     
        if( is_array($svar) ){     
            foreach($svar as $_k => $_v) $svar[$_k] = _runmagicquotes($_v);     
        }else{     
            $svar = addslashes($svar);     
        }     
    }     
    return $svar;     
}     
if(file_exists($insLockfile)){     
    exit(" 程序已运行安装，如果你确定要重新安装，请先从FTP中删除 install/install_lock.txt！");     
}

foreach($$_request as $_k => $_v) ${$_k} = _runmagicquotes($_v);

```

这里是一个经常遇到的一个变量覆盖。

导致了我们可以覆盖掉$insLockfile 从而让file_exists 为false就不会退出了。导致再次重装。 这个变量覆盖不知道咋的 能在一些小cms的安装文件里看到。

之前看的xdcms 和 frcms 都存在这个变量覆盖。

例子:[WooYun: frcms 重装系统](http://www.wooyun.org/bugs/wooyun-2014-073244)

判断Lock后 无exit的。
---------------

* * *

这个从早期的phpdisk 的那个 header bypass 到现在的又遇到各种。

很久前的phpdisk的安装文件中。

判断是否存在lock文件 如果存在lock文件了 就会header到index.php

但是header 后 他并没有exit 所以并不会退出 导致了又是一个重装。

跟这种类似的还有javascript 弹个框 啥的 也没exit的。

例子:[WooYun: 开源轻论坛StartBBS前台getshell](http://www.wooyun.org/bugs/wooyun-2013-045143)

例子:[WooYun: FengCMS 修复不当导致getshell](http://www.wooyun.org/bugs/wooyun-2014-076648)

解析漏洞
----

* * *

这个也比较少, 就随便说句。 就是像dedecms很久以前的那样 在安装完成后会在install.php rename 为 Install.php.bak 但是由于apache的解析漏洞 如果无法识别最后的一个后缀的话 就会向上解析,那么就又成php了。 然后又结合dedecms安装时的变量覆盖 又成重装了。

满足一些条件不会退出的。
------------

* * *

这种例子也不算太多, 自己好像也没遇到过太多。

首先以之前发过的sitestar举例下

```
if(file_exists($lockfile) && ($_a=='template' || $_a=='setting' || $_a=='check')) {     
        exit('please delete install.lock!');     
}

```

这里我们来理解一下这个逻辑, 这里的file_exists($lockfile) 因为安装成功后 lockfile 肯定存在的 所以这里肯定会是true 然后再看一下 这里是一个 && true true 才会进入语句块。 那么如果$_a 不为 template 、 setting 、 check 的话 那么后面的就为false True and false => false就不会进入这个语句块 就不会exit 再配合后面的

```
else if($_a=="create"){     
    $link = mysql_connect($db_host,$db_user,$db_pwd);

```

刚好有个其他的 如果$_a 为 create 那么就不会退出这个脚本

刚好这个create 能达到Getshell的效果

例子:[WooYun: 建站之星Sitestar前台Getshell一枚](http://www.wooyun.org/bugs/wooyun-2014-054387)

剩下的还有hdwiki之前也有一个基本差不多这样的例子

```
if (file_exists(HDWIKI_ROOT.'/data/install.lock') && $step != '8') {
    echo "<font color='red'>{$lang['tipAlreadyInstall']}</font>";
    exit();
}

```

如果step为8的话 那么就不会执行exit了。

```
case 8:
                require_once HDWIKI_ROOT.'/config.php';
                require_once HDWIKI_ROOT.'/lib/hddb.class.php';
                require_once HDWIKI_ROOT.'/lib/util.class.php';
                require_once HDWIKI_ROOT.'/lib/string.class.php';

                $db = new hddb(DB_HOST, DB_USER, DB_PW, DB_NAME, DB_CHARSET);
                //install 
                $setting=$db->result_first('select `value` from '.DB_TABLEPRE.'setting WHERE `variable` = \'site_appkey\'');
                if ($setting){
                    echo "<span style='font-size:20px;'>百科联盟开通成功.</span><a href='../'>进入首页</a>";
                    break;
                }

                //update info
                $data = $_GET['info'];
                $data = str_replace(' ', '+', $data);
                $info = base64_decode($data);

                if ($info){
                    $obj = unserialize($info);
                    if(is_array($obj)){
                        $url2 = 'http://localhost/count2/in.php?action=update&sitedomain='.$_SERVER['SERVER_NAME'].'&info='.$data;
                        $data = util::hfopen($url2);
                        //if gbk then toutf8
                        if ($lang['commonCharset'] == 'GBK'){
                            $obj['sitenick'] = string::hiconv($obj['sitenick'], 'gbk', 'utf-8');

```

刚好这里step 8 又能执行一些特殊的操作。。 现在就把case 8 注释掉了。

这里代码我就不复制过了 免得占篇幅。

这里差不多是我比较常遇到的一些安装文件经常遇到的问题了,突然想也想不到其他啥的了。

0x02 包含漏洞
=========

* * *

这里再来谈一下包含

其实包含也并没有什么好说的。

包含一般也就分为LFI RFI local file inclusion 和 remote嘛

对于LFI的话 因为很多都限制了包含的后缀结尾必须为.php Include ($a.'.php') 例如这种的

所以我们想包含我们的图片马儿的话 那么就需要截断后面的这.php

1: 00截断 需要gpc off && php<5.3.4 2: 长文件名截断 反正这个我很少成功。 3: 转换字符集造成的截断 这个对包含的话基本用不上。上传的话 就是felixk3y牛发的那个转换字符集造成的上传截断那个。

还有一些cms限制包含的后缀必须为.php的时候用的是截取字符判断是不是.php 例如下面一段简单的代码

```
$include_file=$_GET[include_file];
if ( isset( $include_file ) && strtolower( substr( $include_file, -4 ) ) == ".php" )
        {    
                require( $include_file );
        }

```

对传递过来的截取了后面4个字符 判断是不是.php 如果是.php才进行包含。

这里可以用zip(或者phar)协议嘛(当然这个也是找laterain学的 哈哈)。

首先新建一个1.php 里面随便写个phpinfo把

然后压缩成.zip 然后把zip的名字改成 yu.jpg

然后把这个.jpg上传上去 然后包含

![enter image description here](http://drops.javaweb.org/uploads/images/b27b068fc93a5534649bb34098197fc047a76e96.jpg)

对于一些LFI 找不到上传图片的地方的话 也有很多牛发过了一些不能上传图片LFI的技巧 各种包含日志 环境变量啥的 这里我就也不多说了。

下面再来说RFI

如果能RFI的话 那么就是最方便的了。

包含远程文件 或者又是php://input data啥的 各种伪协议。

但是也都知道RFI最大的限制条件就是需要allow_url_include on

且 变量前未定义路径 或者 常量。

Allow_url_include 默认都是off

那么无论是allow_url_include on 还是 变量前无路径 或者 常量

那都是rfi的硬伤。

这里介绍一种在allow_url_include off的情况下也能rfi的

但是成功率也并不太高。

首先在php.ini里看一下allow_url_include

```
; Whether to allow include/require to open URLs (like http:// or ftp://) as files.
allow_url_include = Off

```

翻译一下,允许包含url 例如 http:// ftp:// 之类的协议。

当off的时候肯定就是不允许去包含这样的协议。

这里我们先来测试一下

```
<?php
include($_GET[yu]); 

```

首先 allow_url_include && allow_url_fopen 都为on的时候

![enter image description here](http://drops.javaweb.org/uploads/images/695bdf3effbc0ad0fcbf68c2fb13fcdf035486c9.jpg)

成功RFI。

然后 allow_url_include 为 on allow_url_fopen 为off

![enter image description here](http://drops.javaweb.org/uploads/images/1fe39250080ee5785f8eac4b869631e2fefdbf68.jpg)

直接包含远程文件失败 这时候我们用一下伪协议试试。

![enter image description here](http://drops.javaweb.org/uploads/images/fbcaa1b87fe757520e7887babcc26a17110586a0.jpg)

再次成功rfi。

当allow_url_include && allow_url_fopen 为off的时候。

![enter image description here](http://drops.javaweb.org/uploads/images/9ea4b7f19f83d8feca2733a0596d2e560839627f.jpg)

伪协议失败。

包含文件

![enter image description here](http://drops.javaweb.org/uploads/images/84e942c96d63897061009eedc4fa01fc3d2e3a18.jpg)

URL file-access is disabled in the server configuration 不允许包含。

肯定还有不少人记得很久以前的那个星外无可执行目录的时候

利用远程调用cmd继续提权

那个利用的是共享文件 然后在星外主机上来执行。

那么这里我们也试试

![enter image description here](http://drops.javaweb.org/uploads/images/1e5de09d35e7b3491a29de9741e54c8f23c124b6.jpg)

包含共享文件成功。 这里只本地测试了 没具体测试。

但是由于445的原因 可能基本都失败。

0x03 注入
=======

* * *

下面来说一下注入。 这里谈的是mysql。 注入大概也就是把用户可控的一些变量, 带入到了数据库的各种操作当中且没有做好很好的过滤。 比如注册用户的时候检测用户名是否存在的时候,把用户提交的用户名拿到数据库中去查询。 查询是否存在这个用户名, 如果这里对用户名没有做好过滤的话 那么用户就可以提交一些特殊字符来注入了。

现在注入的主要原因是 很多程序员在写sql语句的时候 还是搞的语句拼接。

一些用了预编译或者是在查询的函数中再来过滤 很多时候就给跪了。

```
select update insert delete

```

因为mysql query 并不能执行多行语句, 除非pdo啥的能多行 所以不能像mssql那样 还能在select后执行个update管理的语句。

对于这四种类型的注入一般的语句的构造也不同。

如果有mysql error的话

那么这四种就都能用报错注入 这种是比较方便的

如果没mysql error的话

Select 的注入 一般是用union select 如果把对数据库中的查询结果展示出来的话那么就能直接出数据了。 如果无回显的话 那么当然就是盲注了。

Update的注入 如果是在update set的位置的话 那么我们可以找找这个表的哪个column会被展示出来 例如如果一个update的注入点是在用户表且是在set位置可控的话 那么我们可以update email这个column 然后去用户资料看一下自己的email就出数据了 语句例如 update table set email=(select user()) 如果是在where后的话 那么一般也就是盲注了。

Insert 的注入 也是一般是通过找哪个column会不会显示出来 尽量把要出的数据插入到这个column里面去。 如果没显示的话 也是盲注。

Delete的注入 一般都是盲注了。

数字型注入主要就是因为他的变量并没有用单引号引住。

但是基本上都是被强制类型转换了 intval啥的。

但是有时候会有遗漏的嘛。

而字符型和搜索型的 都是会有单引号引住的。

所以需要闭合单引号再来进行注入。

说到单引号不得不说个php.ini里的配置

Magic_quotes_gpc 在稍微高点的版本默认都是on

但是却在应该是5.4就已经废除了。

从字面意思上来看 就是对GPC QUOTE嘛

GPC 对应的就是GET POST COOKIE

会被转义的字符为 ' “ \ NULL 会在前面添加上一个转义符。

导致了失去本来的意义 无法闭合单引号进行注入。

(1) 全局没有做addslashes的

像这种全局没有对GET POST COOKIE 做addslashes的 这种厂商基本是会在查询的时候 再对一些用户可控的变量进行addslashes 甚至是不进行addslashes 直接带入查询的。

这样的就算在查询的时候进行addslashes 在很多时候也都能找到几处遗漏了addslashes的。 这种的比较简单 不多说。

(2) 全局做addslashes

现在稍微好一点的厂商都知道了在全局文件中对 GET POST COOKIE 做addslashes (甚至是在带入查询的函数中再做了转义或者预编译 这种给跪) 所以基本不用担心哪里遗漏了哪里忘记了addslashes) 这种的基本是首先先get magic quotes gpc 判断gpc是否开启 如果没开启的话 再调用addslashes来转义 。 如果开启的话 就不用来addslashes了。 没开启就addslashes.

这里主要讲的就是这种类型的注入的一些常见的

宽字节注入
-----

* * *

这个是一个老生常谈的问题, 从一开始的数据库字符集GBK的宽字节注入 到现在也有很久了。

但是并不是字符集为GBK的就能宽字节注入。

总有一些小伙伴说咋我看的cms 字符集是gbk的 但是咋不能宽字节呢?

这是因为数据库的连接方式不同

Set names gbk 这样的就能宽字节

但是现在这样的基本都看不到了。 因为基本都是设置了二进制读取了。

Binary。

这样的宽字节基本没了, 却有了另外一种。

因为转换字符集造成的宽字节注入

从utf8转到gbk 或者从gbk转到 utf8啥的。

例子:[WooYun: 74cms 最新版 注入8-9](http://www.wooyun.org/bugs/wooyun-2014-063225)

錦 从UTF8 转成 GBK之后成了 %e5%5c 74cms对GET POST COOKIE …… 都做了addslashes 所以' 转义后为\' ->%5C %e5%5c%5c' 两个\ 则单引号出来

例子2:[WooYun: qibocms 下载系统SQL注入一枚（官网可重现）](http://www.wooyun.org/bugs/wooyun-2014-055842)

解码导致
----

* * *

因为在全局文件中addslashes

如果我们能找到一些解码的 例如urldecode base64_decode的

那么我们先提交encode之后的 那么就能不被转义了。

然后decode后 再带入查询 造成了注入 无视gpc。

这种的很常见。

例子很多 随便找一个

例子:[WooYun: qibocms B2b 注入一枚](http://www.wooyun.org/bugs/wooyun-2014-053187)//qibocms 注入

例子:[WooYun: phpdisk V7 sql注入2](http://www.wooyun.org/bugs/wooyun-2014-056822)//phpdisk 注入

变量覆盖
----

* * *

常见的变量覆盖 有啥extract 和 parse_str 函数啥的

当然还有$$

变量覆盖得结合一些具体的场景了。

例如extract($_POST)啥的 直接从POST数组中取出变量

这样的还是遇到过几个 然后覆盖掉之前的一些变量。

覆盖的话 一般是覆盖掉表前缀之类的

Select * from $pre_admin where xxx 像这种的就覆盖掉$pre

然后直接补全语句然后注入。

例子:[WooYun: qibocms分类注入一枚可提升自己为管理](http://www.wooyun.org/bugs/wooyun-2014-053189)

例子2:[WooYun: phpmps 注入一枚](http://www.wooyun.org/bugs/wooyun-2014-051734)

当然 $$ 也挺经常用到的 这个例子很不错。

例子3:[WooYun: MetInfo最新版(5.2.4)一处SQL盲注漏洞](http://www.wooyun.org/bugs/wooyun-2014-055338)

一些replace造成的
------------

* * *

一些cms中 总有一些逗比过滤函数

会把’ 啥的 replace 成空

但是他似乎忘记了自己全局有转义?

用户提交一个' 全局转义成\' 然后这过滤函数又会把 ' replace 成空

那么就留下了\ 导致可以吃掉一个单引号 是double query的话

```
Select * from c_admin where username=’admin\’ and email=’inject#’

```

这样就可以注入了。

话说之前还遇到过一个厂商。。 之前提交了漏洞 是因为他会把

' " 都会替换成空 然后提交之后 他就去掉了' 就是不把' 替换成空了。

但是他似乎忘记了 " 也会被转义。。 那么提交一个 " 就又剩下了一个转义符。

例子:[WooYun: PHPCMS全版本通杀SQL注入漏洞](http://www.wooyun.org/bugs/wooyun-2014-050636)

当然还有一些replace 是用户可控的。就是说用户可以想把啥提交成空就提交成空

例如很久前的cmseasy 和 ecshop的那个注入

例如这段代码

```
$order_sn = str_replace($_GET['subject'],'',$_GET['out_trade_no']);

```

这里因为会被转义 如果提交 ' 就成 \' 这里可以看到

这里清成空的 是我们get来的 那我们就想办法把\ replace掉

但是如果我们GET提交把\ replace 那么会被转义 就是replace掉\

但是我们只是 \' 所以不能把\去掉 如果我有\ 还要你清空个毛啊。

这里我们来理清一下思路。

Addslashes 会对' " \ NULL 转义

```
' =>  \'
" => \"
\ => \\
NULL => \0

```

那这里我们就提交 %00’ 就会被转义生成 \0\' 这时候我们再提交把0替换成空 那么就成了\' 单引号也就成功出来了。

例子:[WooYun: cmseasy绕过补丁SQL注入一枚](http://www.wooyun.org/bugs/wooyun-2014-053198)

SERVER 注入
---------

* * *

因为在很多cms中 基本上都只是对GET POST COOKIE 进行addslashes

而没有对SERVER进行转义。

而一些SERVER的变量也是用户可以控制的。

例如啥 QUERY_STRING X_FORWARDED_FOR CLIENT_IP HTTP_HOST ACCEPT_LANGUAGE 很多。

这里最常见的当然也就是X_FORWARDED_FOR

这个一般是在ip函数中用到 如果后面没有进行验证ip是否合法的话就直接return 这个大部分时候都会导致注入。

例子1:[WooYun: Phpyun注入漏洞二](http://www.wooyun.org/bugs/wooyun-2014-068853)

这里说到验证ip 这里基本都是用的正则来验证是否合法。

而一些厂商连正则都写错。

例如在cmseasy中的验证ip的正则中(%.+)

导致了后面可以写任意字符。

例子2:[WooYun: CmsEasy最新版本无限制SQL注射](http://www.wooyun.org/bugs/wooyun-2014-062957)

最近自己在看douphp 里面的验证ip的正则自己也发现了一点小问题。

不过也就只是小问题而已。

Douphp中的获取ip的函数。

```
function get_ip() {
        static $ip;
        if (isset($_SERVER)) {
            if (isset($_SERVER["HTTP_X_FORWARDED_FOR"])) {
                $ip = $_SERVER["HTTP_X_FORWARDED_FOR"];
            } else if (isset($_SERVER["HTTP_CLIENT_IP"])) {
                $ip = $_SERVER["HTTP_CLIENT_IP"];
            } else {
                $ip = $_SERVER["REMOTE_ADDR"];
            }
        } else {
            if (getenv("HTTP_X_FORWARDED_FOR")) {
                $ip = getenv("HTTP_X_FORWARDED_FOR");
            } else if (getenv("HTTP_CLIENT_IP")) {
                $ip = getenv("HTTP_CLIENT_IP");
            } else {
                $ip = getenv("REMOTE_ADDR");
            }
        }

        if (preg_match('/^(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/', $ip)) {
            return $ip;
        } else {
            return '127.0.0.1';
        }
    }
}

```

来看看验证ip是否合法的正则

```
preg_match('/^(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/', $ip)

```

这里我们仔细来看看 他这里是准备匹配小数点 但是他直接写成了.

都知道在正则中.表示的是匹配任意字符 除开换行符意外 但是在开启/s 修正符以后 换行符也会匹配。

不过他这个.后面没啥+或者?的 导致也就只能写一个字符。

他这里直接写成了. 那在这里我们就能引入单引号了。不过也就一个字符。

这里的正确写法应该是.

FILES注入。
--------

* * *

也差不多 也是因为全局只对COOKIE GET POST 转义 遗漏了FILES 且不受gpc。

FILES 注入一般是因为上传 会把上传的名字带到insert当中入库。

然后这里文件的名字是我们可以控制的 所以导致了注入。

而这里的上传的名字是我们可以控制的。

例子:[WooYun: qibocms 黄页系统SQL注入一枚](http://www.wooyun.org/bugs/wooyun-2014-065837)

还有一些 在入库的时候才对文件的名字进行了转义 而在获取后缀后 在入库的时候对文件名转义了却没有对后缀转义也导致了注入

例子:[WooYun: Supesite 前台注入 #2 (Insert)](http://www.wooyun.org/bugs/wooyun-2014-079041)

未初始化造成的注入
---------

* * *

很久以前php<4.20的时候 为了方便 register_globals 默认都是on。

而到了后面 register_globals 的弊端也显现了出来, 所以也在很久以前默认都是off了。

而到了现在, 很多cms 却喜欢模仿register_globals 搞起了伪全局机制。

例如啥qibocms metinfo destoon 啥的啊。

这样是方便了不少, 但是如果哪里遗漏了初始化 那么就会导致注入了。

感觉这种的挺好玩的 多找了几个例子。

例子:[WooYun: qibocms地方门户系统注入一个问题(demo测试)](http://www.wooyun.org/bugs/wooyun-2014-080867)

例子:[WooYun: qibocms地方门户系统注入（多处类似,demo测试)](http://www.wooyun.org/bugs/wooyun-2014-080870)

例子:[WooYun: 齐博地方门户系统SQL注入漏洞(无需登录可批量)](http://www.wooyun.org/bugs/wooyun-2014-079938)

例子:[WooYun: 齐博整站/地方门户SQL注入漏洞](http://www.wooyun.org/bugs/wooyun-2014-080259)

数组中的key。
--------

* * *

因为在对全局转义的时候

很多cms 都只是判断gpc 是否开启

如果off 就对数组中的value就行addslashes

却忘记了对数组中的key进行转义。

那么这样也导致了一个问题。 也就是在Gpc off的时候那么数组的key没有被过滤 导致可以引入单引号。(听说低版本的php对二维数组中的key就算gpc on 也不会转义)

如果哪里把数组中的key 读取出来 然后把key带入到了查询当中

那么也会造成安全问题。

而且这样的例子很多。 简直惨不忍睹。 例子:[WooYun: qibocms V7 整站系统最新版SQL注入一枚 & 另外一处能引入转义符的地方。](http://www.wooyun.org/bugs/wooyun-2014-069746)//数组key的注入例子:[WooYun: qibocms多个系统绕过补丁继续注入2](http://www.wooyun.org/bugs/wooyun-2014-070353)

例子:[WooYun: qibocms全部开源系统 Getshell](http://www.wooyun.org/bugs/wooyun-2014-070366)

例子:[WooYun: Discuz 5.x 6.x 7.x 前台SQL注入漏洞一枚](http://www.wooyun.org/bugs/wooyun-2014-071516)

offset
------

* * *

这种算是比较常见的一种注入的。

代码大概如

```
<?php
$key=0;
$a=$_GET[a][$key];
$b=$_GET[b];
Mysql_query("select * from table where xxx='$a' and xx='$b'")

```

如果这里$_GET[a] 提交的是一个数组 且含有一个key为0的那么$a就是对应的这个key的value

但是这里并没有强制要求为数组。

那么我们提交一个字符串 那么后面的[0] 那么就是截取的第一个字符

在全局中 单引号被转义为\' 截取第一个字符就为了\

吃掉一个单引号 然后就在$b处写入inject可以注入了。

例子:[WooYun: qibocms 地方门户系统 注入#4(demo测试)](http://www.wooyun.org/bugs/wooyun-2014-080875)

还有map发的那Disucz 7.2的那注入也一样。

第三方插件
-----

* * *

很常见的一种洞。

比较常见的uc 和 alipay tenpay chinabank 啥的

特别是uc 因为默认uc里面都会striplashes

Uc的话 一般会遇到的问题是uckey默认的。

或者是uckey这个常量根本就没有初始化。

导致了uckey可控 再导致了Getshell 或者 注入啥的。

还有tenpay 和 alipay 啥的 一些是因为忘记把过滤的文件包含进来

且key默认是空的 导致可以通过验证。

例子:[WooYun: phpmps 注入 (可修改其他用户密码,官网成功)](http://www.wooyun.org/bugs/wooyun-2014-060159)// phpmps uc致注入

例子:[WooYun: PHPEMS (在线考试系统) 设计缺陷 Getshell一枚(官网已shell)](http://www.wooyun.org/bugs/wooyun-2014-061135)/phpems uc致getshell

例子:[WooYun: 最土团购注入一枚可直接提升自己为管理 & 无限刷钱。](http://www.wooyun.org/bugs/wooyun-2014-058479)//最土团购 chinabank致注入

例子:[WooYun: Destoon Sql注入漏洞2（有条件）](http://www.wooyun.org/bugs/wooyun-2014-055026)//destoon tenpay致注入

例子:[WooYun: CSDJCMS程式舞曲最新版Sql 一枚](http://www.wooyun.org/bugs/wooyun-2014-052363)//csdj tenpay致注入

数字型注入
-----

* * *

其实也不只是数字型 只是说一些忘记加单引号的地方都这样。

只是一般数字型的都不会加单引号的。

一般的是

```
$id=$_GET[id];
Select * from table where id=$id;

```

$id 没被单引号 且 没有被强制类型转换 那么就算addslashes了 由于不需要去闭合单引号 所以也无影响。

例子:[WooYun: qibocms 地方门户系统 注入#3 (demo测试)](http://www.wooyun.org/bugs/wooyun-2014-080873)

并不是一些数字型 一些其他的点也有些忘记加单引号 导致了注入。 例子:[WooYun: Supesite 前台注入 #3 (Delete)](http://www.wooyun.org/bugs/wooyun-2014-079045)

这里supesite的注入还涉及到了一个设计缺陷。 这里把

```
$query = $_SGLOBAL['db']->query('SELECT * FROM '.tname('spacetags').' WHERE itemid=\''.$itemid.'\' AND status=\''.$status.'\'')      

```

$itemid 首先带入到了查询当中 是被单引号了的。。 如果查询出来的有结果 才会带入到delete中 如果无结果 就不执行delete的语句了。 而在数据库中itemid中 存储的是int类型 所以他这里本意是想要用户只能提交数字型才能查询出结果。 如果不是提交的数字的话 那么就查询不出来结果 就不去执行下面的delete语句了。 但是由于mysql的类型转换 因为他这里储存的是int类型   所以我们提交4xxxxx 跟我们提交4 是一样的

```
$_SGLOBAL['db']->query('DELETE FROM '.tname('spacetags').' WHERE itemid='.$itemid.' AND tagid IN ('.simplode($deletetagidarr).') AND status=\''.$status.'\''); 

```

然后就执行这个delete语句 然后没单引号 造成了注入。

例子:[WooYun: phpyun v3.2 (20141226) 两处注入。](http://www.wooyun.org/bugs/wooyun-2014-088872)

这个phpyun的注入 主要是因为php是弱类型语言

一些厂商喜欢这样写

```
If ($a>1){
    Mysql_query(select id from table where id=$a)
}

```

他这个本来是想用户提交数字才能通过这个判断 但是由于弱语言 1+asd啥的 都能通过 所以又导致了注入。

二次注入
----

* * *

也是一种比较常见的注入。 涉及到的是入库和出库。 因为有全局转义 然后入库的时候

```
Insert into table (username) values ('a\'');

```

这样入库后 转义符就会消失 那么就是a' 如果哪里再把这个查询出来 那么也就是出库的是a' 如果再把出库的 再带入到了查询啥的 那么就再次成功的引入了单引号导致了注入

例子:[WooYun: phpyun v3.2 (20141226) 两处注入。](http://www.wooyun.org/bugs/wooyun-2014-088872)例子:[WooYun: qibocms 地方门户系统 二次注入#5(demo测试)](http://www.wooyun.org/bugs/wooyun-2014-080877)例子:[WooYun: 74cms (20140709) 二枚二次注入](http://www.wooyun.org/bugs/wooyun-2014-068362)例子:[WooYun: Hdwiki最新版二次注入一枚](http://www.wooyun.org/bugs/wooyun-2014-067424)

比较是硬伤的是 很多时候数据库中存储的长度是有限制的。 所以一些也不是太好利用。

查询当中key可控
---------

* * *

不知道也应不应该把这个归为一类。

大概是因为一些查询的时候 直接把$_POST啥的 直接带入到了查询函数当中

例如cmseasy的rec_insert的查询函数中。

然后foreach key 出来 然后foreach 出来的key 做了查询中的column

这种的防止方法一般是 把数据库中的column查询出来 然后in_array 判断一下$_POST出来的key 是否在数据库中的column中 下面两个例子就是这样修复的。

例子:[WooYun: 云人才系统SQL注入，绕过WAF](http://www.wooyun.org/bugs/wooyun-2014-060166)例子:[WooYun: Cmseasy SQL注射漏洞之三](http://www.wooyun.org/bugs/wooyun-2014-066221)

striplashes
-----------

* * *

有些cms 在全局addslashes后 然后在后面的文件中又stripslashes  
去掉了转义符 然后又可以闭合单引号了。

```
$_SESSION['flow_consignee'] = stripslashes_deep($consignee);

```

例子: http://www.2cto.com/Article/201301/182509.html //之前的ecshop注入 。

截取字符导致的注入
---------

* * *

有些cms 有的时候会限制用户输入的长度

所以只截取一部分

例如uchome的cutstr($asd,32);

这样只允许输入32个字符 而且uchome里面的这个也没有像dz那样截取字符的后面加...

那么如果我们提交一个1111111111111111111111111111111’

被转义后成1111111111111111111111111111111\’

然后截取32个字符 就是1111111111111111111111111111111\

如果又是double query的话 吃掉一个单引号 然后下一个连着的可控变量又可以注入了。

结果在uchome中找到了个能引入转义符的 结果只有一个可控的。

例子:[WooYun: Hdwiki (20141205) 存在7处SQL注入漏洞（含之前处理不当安全的漏洞）](http://www.wooyun.org/bugs/wooyun-2014-088004)//里面的0x06

绕过限制继续注册GLOBALS变量
-----------------

* * *

不知道放哪。这个也放到注入板块来把。。

其实就是这次的DZ6.X 7.X 那个任意代码执行的漏洞

```
if (isset($_REQUEST['GLOBALS']) OR isset($_FILES['GLOBALS'])) {
    exit('Request tainting attempted.');
}

foreach(array('_COOKIE', '_POST', '_GET') as $_request) {
    foreach($$_request as $_key => $_value) {
        $_key{0} != '_' && $$_key = daddslashes($_value);
    }
}

```

主要关键代码就上面这两段。 这里把GET POST COOKIE 循环出来 然后注册一个变量 但是 这里不允许创建GLOBALS变量 然后DZ7.X 就是用这样处理的 如果设置了REQUEST 的 GLOBALS

就直接退出

这段代码在很久以前确实是没什么问题

因为那时候的request order 还是gpc

但是在php 5.3 以后 request order 默认成了gp

也就是成了get 和 Post 不包含cookie了。

所以 $_REQUEST里面就不包含COOKIE提交来的了。

而且这后面也把COOKIE循环出来 注册变量

所以这里我们在COOKIE里面提交GLOBALS 就不会被检测出来了。

而且也成功注册了GLOBALS变量。

所以在结合后面的一些些代码就造成了代码执行。

例子:[WooYun: Discuz!某两个版本前台产品命令执行（无需登录）](http://www.wooyun.org/bugs/wooyun-2014-080723)

以上就差不多是我经常所遇到的注入问题 好像暂时也想不到其他什么的了

0x04 找回密码出现的问题。
===============

* * *

下面介绍一些我在cms遇到的找回密码时候犯得错误。

找回密码很多都是验证的token 就是在找回密码的时候生成一个token 然后存储到数据库中。 然后把找回密码的地址发到邮箱中 url中就含有token 由用户点开后就能修改密码 基本就是验证的这个token。 其实一般的可以找回任意用户密码的原因就是弱token 导致可以被攻击者搞到。 包括很多厂商验证的时候就是四位纯数字啥的。 可以枚举。 当然也可以延伸一下, 一些cms的密码加密方式很难破掉。 有时候我们拿到了管理的密码破不掉也是鸡肋。 所以有时候也可以利用这种方法 一般找回密码是用的邮箱 首先我们可以注入把管理的邮箱注入出来 然后再去找回密码 再把数据库的token注入出来 再构造一下地址 就能重置密码。 这个给我印象比较深的是 在ssctf的比赛中嘛 当时机油问了问我 那wordpress那题 有个插件的注入 然后因为都知道wp的加密基本很难破。 所以也是用的这种方法。 因为一般都是弱token的问题 随便找几个例子了

rand 函数生成的token
---------------

* * *

```
$resetpwd = md5(rand());

```

可以看到这个生成的token 就是对rand()函数生成出来的数字进行md5一次

来看一下rand()

注释：在某些平台下（例如 Windows）RAND_MAX 只有 32768。如果需要的范围大于 32768，那么指定 min 和 max 参数就可以生成大于 RAND_MAX 的数了，或者考虑用 mt_rand() 来替代它。 如果不指定一些参数的话 那么最大值才32768 一个并不算大的值 那么我们首先对这32768种可能 md5出来一个列表 然后我们直接枚举这32768种可能 总会有一个对的。

例子:[WooYun: Thinksaas找回密码处设计错误利用账户可找回密码。](http://www.wooyun.org/bugs/wooyun-2014-050304)

修改hdwiki任意用户密码
--------------

* * *

```
$encryptstring=md5($this->time.$verification.$auth);

```

补丁后 多了一个$auth  $timetemp=date("Y-m-d H:i:s",$this->time);  $auth = util::strcode($timetemp, 'ENCODE');  可以$auch 是对时间来了一个算法。 结果这个算法的KEY并没有初始化 导致了如果我们知道了这个时间 就可以自己生成出来加密的字符串 这里带入算法的是时间 这里是我们可以知道的。

例子:[WooYun: Hdwiki设计缺陷知邮箱可改密码（包括管理员）](http://www.wooyun.org/bugs/wooyun-2014-067410)//绕过补丁继续找回hdwiki任意用户密码

0x05 上传
=======

* * *

这个上传就大概说说。

一般的上传漏洞可能是未验证上传后缀 或者是验证上传后缀被bypass 或者是上传的文件验证了上传后缀但是文件名不重命名。

对于那些验证了后缀但是文件名不重命名的

一般可以试试截断yu.php%00.jpg 当然%00 要urldecode

当然 毕竟截断鸡肋了。 上面提到过限制条件了。

还可以是结合各种webserver的解析漏洞

例如iis6的 xx.asp/yu.jpg yu.php;.jpg yu.asp;.jpg aspx 当然不能这样解析了。

如果不重命名的就上传这样就行了。

Nginx的低版本解析漏洞: yu.jpg/1.php 对于这种直接上传一个xxxx.jpg 再在这后面加上各种/.php 试试的

Apache解析漏洞 yu.php.xxx 在最后一个后缀识别不出来的时候 那么就向上解析

最终解析成.php

像phpweb后台那个上传漏洞。很多人遇到apache的时候

无法截断的时候就上传一个yu.php.jpg 有些人比较疑问的是为啥有时候成功有时候失败。

这个主要是看os 像windows的话 .jpg 就直接是图片了

所以在windows下 就直接识别成图片了 而不是.php

而在linux下 .jpg不被识别 就向上识别成.php

这些解析漏洞在上传中也挺经常遇到的。

上传的验证一般是 MIME、客户端的JS验证、白名单、黑名单。

前面两种都比较简单。

白名单就是允许用户上传哪些后缀的。 黑名单就是禁止用户上传哪些后缀的。

这两种相比来说一般是黑名单容易bypass一点。 黑名单的绕过还是得具体看他黑名单的代码。 有的直接大小写就过。 有些没对文件名trim的 直接在文件名后面加空格。 Windows下的 文件名后%81-%99 decode后的 或者是windows下的特性 .php::$data 这样上传上去依旧是.php

其实上传还挺重要的。。 但是我又不知道说哪些。 还是具体看代码把。

任意文件操作
------

* * *

这个主要是涉及到的是 任意文件删除 任意文件复制 任意文件重命名 任意文件移动 任意文件下载……。 因为像现在的cms很多都自带得有加密 解密 函数 例如qibocms的mymd5 Dz的authcode 啥的。 对于这些任意文件操作的 首先可以试试拿到配置文件中的数据库的连接帐号和密码 尝试外联一下 但是很多时候都是只允许本地连的 很多时候不好利用的时候可以利用拿到配置文件 然后拿到这些函数的key 然后自己生成一个加密的字符串 然后再结合具体的代码进行最大化的利用。

对于任意文件删除
--------

* * *

一般是挺不好利用的，还是结合具体的场景，有些因为全局的过滤而不能注入的，可以尝试用任意文件删除，删掉这个文件，再进行注入 一般的利用还是通过删除安装文件生成的lock文件，然后达到重装。

不过这样弊很大。

例子:[WooYun: phpyun (20141230) 任意文件删除致注入可改任意用户密码(4处打包)](http://www.wooyun.org/bugs/wooyun-2014-088418)

任意文件复制 / 任意文件移动 / 任意文件重命名
-------------------------

* * *

复制的话 肯定涉及到了 要复制的文件 要复制到的路径。

如果是要复制的文件可控 要复制到的路径不可控的话 例如qibocms之前的一个洞

```
copy(ROOT_PATH."$webdb[updir]/$value",ROOT_PATH."$webdb[updir]/{$value}.jpg");     

```

这里$value 是可控的 但是又不能截断 复制到的路径限制了.jpg结尾。

这时候我们就可以把$value控制为 保存了qibocms的加密函数的key的配置文件

然后复制后 成了一个.jpg 那我们就可以直接打开 看到key了

例子:[WooYun: Qibocms图片系统任意文件查看导致的多处注入(可提升自己为管理员)](http://www.wooyun.org/bugs/wooyun-2014-065835)

如果两个都完全可控的话 那肯定是直接把自己的图片复制成一个.php马儿了。

任意文件下载
------

* * *

其实跟上面复制差不多， 很多时候也是通过下载配置文件 拿到key。 再进行各种操作。。

例子:[WooYun: qibocmsV7整站系统任意文件下载导致无限制注入多处(可提升自己为管理 Demo演示)](http://www.wooyun.org/bugs/wooyun-2014-066459)

这个例子还涉及到了一个win的特性bypass 黑名单

0x06 加密函数问题。
============

* * *

这种问题主要是想进各种办法把这些加密函数的key拿到 或者想办法加密一些特殊字符然后拿到加密的字符串

加密函数肯定就涉及到了各种算法。

加密可逆
----

* * *

算法问题一般主要是因为一些弱算法 导致了 知道明文 知道密文 可逆

拿到加密函数中的key 从而再自己生成一个自己想要的加密字符串。

再结合具体的点 然后进行具体的利用。

例子:[WooYun: DedeCMS-V5.7-SP1(2014-07-25)sql注入+新绕过思路](http://www.wooyun.org/bugs/wooyun-2014-071655)例子:[WooYun: phpcms最新版绕过全局防御暴力注入（官网演示）](http://www.wooyun.org/bugs/wooyun-2014-066138)

加密可控
----

* * *

还有的一类算是 一个点 要加密的是我们可控的 而且密文会输出 而且这个可控的点能引入特殊字符 那么我们就把一些特殊字符带入到这里面 然后拿到密文 再找到一处decode后会进行特殊操作的点 然后进行各种操作。

例子:[WooYun: 程氏舞曲CMS某泄露，导致sql注入](http://www.wooyun.org/bugs/wooyun-2014-080370)

例子:[WooYun: PHPCMS最新版(V9)SQL注入一枚](http://www.wooyun.org/bugs/wooyun-2013-024984)

key泄漏
-----

例子:[WooYun: 一个PHPWIND可拿shell的高危漏洞](http://www.wooyun.org/bugs/wooyun-2014-072727)

例子:[WooYun: PHPCMS V9 一个为所欲为的漏洞](http://www.wooyun.org/bugs/wooyun-2014-066394)

0x07 后记
=======

* * *

寥寥草草的把这篇文章写完了。

比自己预期想的少写了很多, 因为在一开始写的时候还是挺有感觉的。

因为读书一个月也才放一次假, 都是抽时间在慢慢写着。

后面差不多写了1W字的时候,存稿竟然丢了, 弄了半天也没找回

就感觉不想写了, 后面又翻了翻 找到了一篇自己之前保存的写了差不多两三千字的

然后就再慢慢的开始写了, 也就草草的结束了。

当然这里只是总结了一些常见的类型, 肯定在实战中会遇到各种各样的情况 各种过滤啥的。

各种逻辑错误需要自己慢慢去体会了。