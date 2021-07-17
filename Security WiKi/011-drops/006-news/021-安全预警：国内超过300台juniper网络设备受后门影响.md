# 安全预警：国内超过300台juniper网络设备受后门影响

0x00. 事件回顾
==========

* * *

在2015年的12月18日,Juniper官网发布安全公告,指出在他们的Netscrren防火墙的ScreenOS软件中发现未授权的代码,其中涉及2个安全问题,一个是在VPN的认证代码实现中被安放后门,允许攻击者被动解密VPN的流量(CVE-2015-7756),另一个后门是允许攻击者远程绕过SSH和Telnet认证,利用后门密码远程接管设备(CVE-2015-7755).在Juniper的安全公告后的6个小时,Fox-IT公司找到了后门密码,并发布了Sort规则

通过Sort规则我们可以看出SSH/Telnet的后门密码是`"<<< %s(un='%s') = %u" (3c3c3c20257328756e3d2725732729203d202575十六进制解码)`

Sort规则:

```
alert tcp $HOME_NET 23 -> any any (msg:"FOX-SRT - Flowbit - Juniper ScreenOS telnet (noalert)"; flow:established,to_client; content:"Remote Management Console|0d0a|"; offset:0; depth:27; flowbits:set,fox.juniper.screenos; flowbits:noalert; reference:cve,2015-7755; reference:url,http://kb.juniper.net/JSA10713; classtype:policy-violation; sid:21001729; rev:2;)
alert tcp any any -> $HOME_NET 23 (msg:"FOX-SRT - Backdoor - Juniper ScreenOS telnet backdoor password attempt"; flow:established,to_server; flowbits:isset,fox.juniper.screenos; flowbits:set,fox.juniper.screenos.password; content:"|3c3c3c20257328756e3d2725732729203d202575|"; offset:0; fast_pattern; classtype:attempted-admin; reference:cve,2015-7755; reference:url,http://kb.juniper.net/JSA10713; sid:21001730; rev:2;)
alert tcp $HOME_NET 23 -> any any (msg:"FOX-SRT - Backdoor - Juniper ScreenOS successful logon"; flow:established,to_client; flowbits:isset,fox.juniper.screenos.password; content:"-> "; isdataat:!1,relative; reference:cve,2015-7755; reference:url,http://kb.juniper.net/JSA10713; classtype:successful-admin; sid:21001731; rev:1;)
alert tcp $HOME_NET 22 -> $EXTERNAL_NET any (msg:"FOX-SRT - Policy - Juniper ScreenOS SSH world reachable"; flow:to_client,established; content:"SSH-2.0-NetScreen"; offset:0; depth:17; reference:cve,2015-7755; reference:url,http://kb.juniper.net/JSA10713; classtype:policy-violation; priority:1; sid:21001728; rev:1;)

```

0x01. 受CVE-2015-7755后门影响的Juniper设备型号
====================================

* * *

根据Juniper的安全公告提及,版本6.2.0r15到6.2.0r18和6.3.0r12到6.3.0r20受影响,Juniper提供了新的6.2.0和6.3.0build下载,也对去除后门的版本进行了重打包,标识为'b',如ssg500.6.3.0r12b.0.bin和ssg5ssg20.6.3.0r19b.0.bin.老外对CVE-2015-7756和CVE-2015-7755受影响的Juniper设备版本做了一个图示，如图1 (虽然我个人认为他标记2个CVE标记反了)

![enter image description here](http://drops.javaweb.org/uploads/images/6d01c1726ad229c8438356970b35ad6232b78bc0.jpg)

图片引用自`http://malwarejake.blogspot.tw/`

0x02. 技术分析：
===========

* * *

这里只参考hdm的文章分析发现CVE-2015-7755后门漏洞的过程,CVE-2015-7756漏洞涉及很多密码学的知识,我随后发布.

hdm已经把firmware打包放在了https://github.com/hdm/juniper-cve-2015-7755,其中 SSG500固件是使用x86架构, SSG5和SSG20固件使用XScale (ARMB) 架构,这里直接把ssg5ssg20.6.3.0r19.0.bin载入IDA,在"Processor Type"里选择ARMB,如图2

![enter image description here](http://drops.javaweb.org/uploads/images/b18a293ec16bb4d01d31b1674d03bfb53db35b37.jpg)

图2

然后修改Loading Address为 0x80000,File Offset为 0x20,如图3

![enter image description here](http://drops.javaweb.org/uploads/images/9fc3b1e3fa2e8a8f3d8daee57270b48d93f101ca.jpg)

图3

通过字符串参考搜索"strcmp"找到sub_ED7D94函数,但是引用太多,如图4,图5.继续查看字符串参考,发现更有趣的字符如"auth_admin_ssh_special"和“auth_admin_internal",通过"auth_admin_internal"发现sub_13DBEC函数,这个函数有个BL sub_ED7D94,F5看下sub_ED7D94,类似"strcmp",如图6

![enter image description here](http://drops.javaweb.org/uploads/images/75833c79bca97d15236a78309daab22737a33b00.jpg)

图4

![enter image description here](http://drops.javaweb.org/uploads/images/893d2d1a1e28ad4a9858e86b447a955059c342ef.jpg)

图5

![enter image description here](http://drops.javaweb.org/uploads/images/6da1e34bac7a45624c581af9e7509dd262834050.jpg)

图6

最后确定后门密码为`“<<< %s(un='%s') = %u“`,如图7

![enter image description here](http://drops.javaweb.org/uploads/images/9c5013ba7f13ad38329ac0c994e232de33d33de8.jpg)

图7

要想利用还需要知道SSH/TELNET登陆名,通过官方文档,我们知道默认登陆名为netscreen,又根据sans 蜜罐的结果`https://isc.sans.edu/forums/diary/The+other+Juniper+vulnerability+CVE20157756/20529/`,摘录出常用用户名`root/admin/`,扫描结果见第三部分

0x03. 国内影响：
===========

* * *

经过我个人扫描,全球开放juniper的ssh设备有21869台(为了避免麻烦,忽略了一些已知的蜜罐网络和敏感网络的IP段,实际应该更多),其中中国占2008台.根据shodan的热词`“netscreen counter:"CN""`来看,他得到的中国受影响的IP是2130台.如图8,而其中受后门影响的设备已经验证的有317台.如图9

![enter image description here](http://drops.javaweb.org/uploads/images/e47ec6a4f3d952bf28db14baedb3e5ed7353b2e3.jpg)

图8

![enter image description here](http://drops.javaweb.org/uploads/images/3c394c04a5b52b1182c2741c080cdfe5f635fc19.jpg)

图9

另外要说的另一个敏感问题是,除了受后门影响的这317台juniper设备,弱口令问题导致可以登陆设备的有20多台,大部分是netscreen/netscreen,这种安全意识问题,还需要网络管理员注意.

管理员可通过get event查看登陆日志.排查是否可以被扫描或登陆

```
ssg5-serial-> get event  
Total event entries = 3072
Date       Time     Module Level  Type Description
2015-12-23 17:25:27 system warn  00515 Admin user system has logged on via 
                                       SSH from 1.1.1.1:32366
2015-12-23 17:17:26 system warn  00528 SSH: Password authentication failed 

```

虽然这个日志可以通过`ssg5-serial-> get event`来删除. :)

0x04. 补丁升级
==========

* * *

可以通过tftp和web接口来升级,具体步骤参考

```
http://puluka.com/home/techtalknetworking/screenoscriticalsecurityissue2015.html

```

0x05 参考文章：
==========

* * *

```
Juniper ScreenOS backdoor: the attack demystified
http://www.pentest.guru/index.php/2015/12/21/juniper-screenos-backdoor-attack-demystified/

Juniper Networks - 2015-12 Out of Cycle Security Bulletin: ScreenOS: Multiple Security issues with ScreenOS (CVE-2015-7755) - Knowledge Base
https://kb.juniper.net/InfoCenter/index?page=content&id=JSA10713&cat=SIRT_1&actp=LIST

Juniper Follow Up
http://malwarejake.blogspot.com/2015/12/juniper-follow-up.html

CVE-2015-7755: Juniper ScreenOS Authentication Backdoor
https://community.rapid7.com/community/infosec/blog/2015/12/20/cve-2015-7755-juniper-screenos-authentication-backdoor

```

0x06. 要感谢的人：
============

* * *

RY,低调的张老师