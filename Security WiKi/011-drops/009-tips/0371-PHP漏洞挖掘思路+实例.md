# PHP漏洞挖掘思路+实例

最近研究PHP漏洞的挖掘，总结了一些我挖到的漏洞，整理了一下思路，求各路神人补充、批评、指导~

本文所有示例均来自我在乌云上已由厂商允许公开的漏洞

由于是实例的分析，基础知识请百度，就不全都粘贴到前面了

0x01:  搜索所有的用户可控变量（GET/POST/COOKIE/referer）
-------------------------------------------

* * *

原因：所有用户输入都是有害的，代码审计注重函数和变量，先看看在什么地方会有输入

可能出现的场景：

### a) id=$_GET['id'];

可能存在的问题：

无过滤的SQL注入：

[WooYun: chshcms 程氏CMS V3.0 注射（已在官方演示站测试）](http://www.wooyun.org/bugs/wooyun-2013-040338)

```
$id=trim($_GET["id"]);    

```

//下面直接就进查询语句了

```
if($db->query("update ".Getdbname('dance')." set CS_TID=".$tid." where cs_user='".$cscms_name."' and 

```

当然，这是GET之后没做过滤的情景

### b) id=intval($_GET['id']);

可能存在的问题：intval对字符型无用，字符型变量是怎么处理的呢？

如果字符型的addslashes，注意数字型盲注（见c2分析）

### c) $tid=XX_Request("tid");

使用自己定义的安全过滤函数处理变量，很常见，很多框架都提供了解决方案，不过自己包装一个也是很常见的

可能存在的问题：

#### c1) 有没有忘记使用这个处理函数？

[WooYun: chshcms 程氏CMS V3.0 注射（已在官方演示站测试）](http://www.wooyun.org/bugs/wooyun-2013-040338)

```
$tid=CS_Request("tid"); //使用安全的CS_request addslash  
$id=trim($_GET["id"]);  //呵呵呵，曲项向天歌，CS_Request哭了 

```

其实还是上面那个例子，自己忘了用这函数过滤了

#### c2) 函数本身是否安全？

[WooYun: (新)程氏舞曲CMS 三步GETSHELL（实例演示+源码详析）](http://www.wooyun.org/bugs/wooyun-2013-044824)

```
$t_Val = $magic?trim($_GET[$pi_strName]):addslashes(trim($_GET[$pi_strName])); 

```

使用了addslashes，这就意味着逃脱单引号难度加大，需要寻找没有单引号保护的语句注入

addslashes只处理单引号和斜杠，因此无法过滤形如 134 and 1=1 这样的注射语句，请自行百度无单引号盲注

在下面的语句中，$cscms_name就是有单引号保护的，而$id是没有单引号保护的

```
$db->query("update ".Getdbname('xiaoxi')." set CS_DID=1 where CS_ID=".$id." and cs_usera='".$cscms_name."'"); 

```

所以id引发了盲注

#### c3) 过滤函数能否满足业务逻辑的特殊需求？

负数订单啦，自己修改自己的投票数啦，各种业务逻辑上的问题都有可能发生

非常可惜，这个我还没撞见过，如果以后撞见再更新到文章里

### d) 不要忘记我们能控制referer等变量

可能存在的问题：

虽然发现GET/POST都过滤处理了，但是referer和cookie容易被忽视

$_SERVER["HTTP_REFERER"] 例子：

[WooYun: MacCMS 6.x referer处理不当引发注射](http://www.wooyun.org/bugs/wooyun-2013-038804)

很遗憾，这个截至今日还未公开，等公开了大家再去看吧

$_COOKIE['xxx'] 例子：

[WooYun: TCCMS全版本COOKIE注入（已演示证明）](http://www.wooyun.org/bugs/wooyun-2013-041200)

$sql="select password from ".$_Obj->table." where id=".$_COOKIE['userId'];

情况和GET时是一样的，不过注入时操作起来稍微麻烦些，SQLMAP教程我就不粘贴到这里了，不会COOKIE注射的请百度

### e) 还有其他的输入变量，请各路高手带着实例补充！

目前，我们了解了程序总体上是如何处理用户输入的

0x02：单独搜索$_COOKIE，分析身份认证时的逻辑
----------------------------

* * *

原因：身份验证属于业务逻辑中“高危”的部分，大部分的高危漏洞都出在这里

可能出现的场景：

### a) 没有cookie处理，直接全是session

那就等之后通读代码时直接去读认证算法好啦

### b) 认证算法中强度太弱（用可控的COOKIE算来算去），降低了伪造身份的难度

[WooYun: (新)程氏舞曲CMS 三步GETSHELL（实例演示+源码详析）](http://www.wooyun.org/bugs/wooyun-2013-044824)

第二步伪造身份时

```
elseif($_COOKIE['CS_Login']!=md5($_COOKIE['CS_AdminID'].$_COOKIE['CS_AdminUserName'].$_COOKIE['CS_AdminPassWord'].$_COOKIE['CS_Quanx'])){ 

```

有什么意义呢？COOKIE我们能控制，当然之后程序有别的验证，这里只是举例，就这一句而言没有意义

实际上漏洞里这个CMS这个算法，后面只是在认证时没有用到安装时admin写死在config里的验证码而已，不过难度已经降下来了

### c) 直接能绕过

如果情况b 没有其他验证了，那就绕过了

目前我们只是验证了登陆时的逻辑，之后还需分析权限的缜密程度

0x03：搜索所有的文件操作函数，分析其逻辑
----------------------

* * *

原因：文件操作函数属于敏感函数，往往业务逻辑上的漏洞可能导致任意文件操作

可能出现的场景：

### a) 任意文件下载

[WooYun: appcms 最新版 1.3.708 任意文件下载](http://www.wooyun.org/bugs/wooyun-2013-038800)

```
<?php  
if(isset($_GET['url']) && trim($_GET['url']) != '' && isset($_GET['type'])) {  
    $img_url = base64_decode($_GET['url']);  
    $shffix = trim($_GET['type']);  
header("Content-Type: image/{$shffix}");  
readfile($img_url);
} else {
die('image not find');  
} 
?>

```

PS：由于是业务逻辑上的问题，是没办法通过自动扫描发现的，而且针对SQL和HTML的过滤是起不到特大作用的

任意文件读取的最大作用是读config.php 和各种系统的敏感文件（如何爆物理目录？请看0x04）

### b) 任意文件写入

[WooYun: CSCMS V3.5 最新版 后台命令执行GETSHELL（源码详析）](http://www.wooyun.org/bugs/wooyun-2013-046603)

发帖时仍未公开，所以先不做分析，等公开后更新~

任意文件写入的最大应用就是写马了，最大障碍是绕过过滤的HTML字符比如： <>，解决方式是大量应用base64

### c) 任意文件删除

很遗憾，还没撞见过，要是撞见一个该多好

任意文件删除的作用可以是删除install.lock，然后重装CMS

### d) 其他操作，求补充

文件操作可以结合爆目录

0x04：爆物理目录
----------

* * *

原因：上一小节我们可能能够任意操作文件，但没拿到网站的物理目录地址，的确可以用黑盒不停地试图读取 c:\boot.ini 和 /etc/passwd 之类的来试图判断，但是这么弄实在不可靠

怎么办：使用php vulnerability hunter 自动扫描就好了，这个确实可以偷懒用工具扫描，因为这个爆目录危害实在太低了，必须配合其他漏洞才有危害，所以一般CMS都会有这种漏洞，我是说能扫描出来的漏洞

[WooYun: appcms 最新版 1.3.708 任意文件下载](http://www.wooyun.org/bugs/wooyun-2013-038800)

如果你不知道物理路径，你可以试着用工具扫描一下，然后再读取

0x05：搜索eval，preg_replace什么的，看看有没有命令执行
-------------------------------------

* * *

原因：能直接执行PHP代码，也就是说可以写一句话木马了（file_put_contents），当然，要找可写目录

这地方我一直没能找到例子，没有亲自实践过，求各路高手带实例提供几个？

0x06：可以开始通读代码了，从index开始，注意的是数据的传输和输出函数
--------------------------------------

* * *

原因：常见模式化的漏洞都不存在的话，就要分析整个系统了，因此需要完全而彻底地去做审计，这样比继续单独搜索变量然后跟踪更加省力一些

可能出现的场景：

### a) 之前的过滤全白费了

[WooYun: YXcms1.2.0版本 存储式XSS（实站演示+源码分析）](http://www.wooyun.org/bugs/wooyun-2013-046585)

没公开，等公开再更新文章，这是一个存储式xss

### b) 二次注入

由于二次开发中从数据库里取出的值没有过滤，导致注射，由于没有直接从用户输入中获得，所以之前步骤很难发现

哎呀，求各路高手提供个示例呀，我这个自己也没有碰到过丫

### c) 平行权限、任意投票、越权访问 等等 等等 一大堆

0x07 总结
-------

* * *

目前我就知道这么些，希望能对刚接触PHP代码审计漏洞挖掘的新手有点帮助，由于我也是刚开始学习PHP漏洞挖掘不久，希望大家能广泛提供学习的建议以及思路，也请批评指正文章中不妥之处，更希望高手们能带着示例来指导。