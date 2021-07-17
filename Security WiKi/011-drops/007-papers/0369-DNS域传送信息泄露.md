# DNS域传送信息泄露

**0x00 相关背景介绍**

Dns是整个互联网公司业务的基础，目前越来越多的互联网公司开始自己搭建DNS服务器做解析服务，同时由于DNS服务是基础性服务非常重要，因此很多公司会对DNS服务器进行主备配置而DNS主备之间的数据同步就会用到dns域传送，但如果配置不当，就会导致任何匿名用户都可以获取DNS服务器某一域的所有记录，将整个企业的基础业务以及网络架构对外暴露从而造成严重的信息泄露，甚至导致企业网络被渗透。

**0x01 成因**

DNS服务器的主备数据同步，使用的是域传送功能。 域传送关键配置项为：

allow-transfer {ipaddress;}; 通过ip限制可进行域传送的服务器

allow-transfer { key transfer; }; 通过key限制可进行域传送的服务器

设置方式为两种：一种设置在options配置域；一种设置在zone配置域。优先级为如果zone没有进行配置，则遵守options的设置。如果zone进行了配置，则遵守zone的设置。

options配置如下：

```
options {  
listen-on { 1.1.1.1; };  
listen-on-v6 { any; };  
directory "/bind";  
pid-file "/bind/run/pid";  
dump-file "/bind/data/named_dump.db";  
statistics-file "/bind/data/named.stats";

    allow-transfer  { any; };
    allow-query    {any;};


};

```

zone配置如下：

```
zone "wooyun.org" {  
type master;  
file "/bind/etc/wooyun.org.conf";  
allow-transfer {any;};  
};

```

笔者测试版本为BIND 9.8.2rc1-RedHat-9.8.2-0.10.rc1.el6_3.6，默认安装完毕后，配置项没有allow-transfer 项。如果直接使用默认配置文件进行配置的话（不手动添加allow-transfer项），就会存在dns 域传送漏洞。

**0x02 攻击方式及危害**

恶意用户可以通过dns域传送获取被攻击域下所有的子域名。会导致一些非公开域名（测试域名、内部域名）泄露。而泄露的类似内部域名，其安全性相对较低，更容易遭受攻击者的攻击，比较典型的譬如内部的测试机往往就会缺乏必要的安全设置。

攻击者进行测试的成本很低，如dns服务器IP：1.1.1.1 测试域名为wooyun.org，测试命令如下：

```
# dig @1.1.1.1 wooyun.org axfr  #就可以看到返回结果类似如下：  
; <<>> DiG 9.7.3 <<>> @1.1.1.1 wooyun.org axfr

; (1 server found)  
;; global options: +cmd  
wooyun.org. 86400 IN SOA wooyun.org. rname.invalid. 0 86400 3600 604800 10800  
wooyun.org. 86400 IN NS wooyun.org.  
wooyun.org. 86400 IN A 127.0.0.1  
wooyun.org. 86400 IN AAAA ::1  
test.wooyun.org. 86400 IN A 1.1.1.1  
xxx.wooyun.org. 86400 IN A 2.2.2.2  
wooyun.org. 86400 IN SOA wooyun.org. rname.invalid. 0 86400 3600 604800 10800

```

**0x03 实际案例**

[WooYun: 优酷 DNS 域传送漏洞](http://www.wooyun.org/bugs/wooyun-2011-01828)

[WooYun: 去哪儿DNS域传送漏洞](http://www.wooyun.org/bugs/wooyun-2011-02151)

[WooYun: IT168.com DNS 域传送漏洞](http://www.wooyun.org/bugs/wooyun-2012-04229)

**0x04 修复方案**

解决域传送问题非常简单，只需要在相应的zone、options中添加allow-transfer限制可以进行同步的服务器就可以了，可以有两种方式：限制IP、使用key认证。