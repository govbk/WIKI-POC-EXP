# Mimikatz 非官方指南和命令参考_Part3

原文地址：[https://adsecurity.org/?page_id=1821](https://adsecurity.org/?page_id=1821)  
原文作者：[Sean Metcalf](https://twitter.com/PyroTek3)

**译者注：**  
由于[原文](https://adsecurity.org/?page_id=1821)中，作者（[Sean Metcalf](https://twitter.com/PyroTek3)）已经明确的指出**“未经本文作者明确的书面同意，请勿复制包含在此页面的全部或部分内容。”**，因此为了分享此佳作，译者与作者（[Sean Metcalf](https://twitter.com/PyroTek3)）在推上取得了联系，沟通之后，作者允许我将此文完整翻译并分享给其他人。在此也感谢 Sean Metcalf 大牛将有关 Mimikatz 的全部内容做了系统的整理并分享出来。以下是原文作者（Sean Metcalf）回复的截图,以作授权说明：

![p1](http://drops.javaweb.org/uploads/images/4e70dc84ff27c60d6d8269bf661cd062c34651b8.jpg)

Mimikatz 作为当下内网渗透神器之一，看起来似乎很少有人真正关注它的全部功能（Sean Metcalf 在原文开头也表示了这样的疑惑），在一些诸如**“十大黑客工具”**的文章中也看不到 Mimikatz 的影子。 Sean Metcalf 大牛将有关 Mimikatz 的相关技术做了系统的整理，遂做粗糙翻译并作分享。译文难免有误，望各位看官及时指正。

此文是译文的第三部分也是最后一部分。其余两部分的译文链接如下：

*   [Mimikatz 非官方指南和命令参考_Part1](http://drops.wooyun.org/tools/12462)
*   [Mimikatz 非官方指南和命令参考_Part2](http://drops.wooyun.org/pentesting/12521)

0x00 最流行的 Mimikatz 命令
=====================

* * *

下面就介绍一些最流行的 Mimikatz 命令及相关功能。

*   [CRYPTO::Certificates](https://adsecurity.org/?page_id=1821#CRYPTOCertificates)– 列出/导出凭证
*   [KERBEROS::Golden](https://adsecurity.org/?page_id=1821#KERBEROSGolden)– 创建黄金票证/白银票证/信任票证
*   [KERBEROS::List](https://adsecurity.org/?page_id=1821#KERBEROSList)- 列出在用户的内存中所有用户的票证（TGT 和 TGS）。不需要特殊的权限，因为它仅显示当前用户的票证。与 “klist” 的功能相似。
*   [KERBEROS::PTT](https://adsecurity.org/?page_id=1821#KERBEROSPTT)- 票证传递。通常用于注入窃取或伪造的 Kerberos 票证（黄金票证/白银票证/信任票证）。
*   [LSADUMP::DCSync](https://adsecurity.org/?page_id=1821#LSADUMPDCSync)- 向 DC 发起同步一个对象（获取帐户的密码数据）的质询。无需在 DC 上执行代码。
*   [LSADUMP::LSA](https://adsecurity.org/?page_id=1821#LSADUMPLSA)– 向 LSA Server 质询检索 SAM/AD 的数据（正常或未打补丁的情况下）。可以从 DC 或者是一个 lsass.dmp 的转储文件中导出所有的 Active Directory 域凭证数据。同样也可以获取指定帐户的凭证，如 krbtgt 帐户，使用 /name 参数，如：“/name:krbtgt”
*   [LSADUMP::SAM](https://adsecurity.org/?page_id=1821#LSADUMPSAM)- 获取 SysKey 来解密 SAM 的项目数据（从注册表或者 hive 中导出）。SAM 选项可以连接到本地安全帐户管理器（SAM）数据库中并能转储本地帐户的凭证。可以用来转储在 Windows 计算机上的所有的本地凭据。
*   [LSADUMP::Trust](https://adsecurity.org/?page_id=1821#LSADUMPTrust)- 向 LSA Server 质询来获取信任的认证信息（正常或未打补丁的情况下）。为所有相关的受信的域或林转储信任密钥（密码）。
*   [MISC::AddSid](https://adsecurity.org/?page_id=1821#MISCAddSid)– 将用户帐户添加到 SID 历史记录。第一个值是目标帐户，第二值是帐户/组名（可以是多个）（或 SID ）。
*   [MISC::MemSSP](https://adsecurity.org/?page_id=1821#MISCMemSSP)– 注入恶意的 Wndows SSP 来记录本地身份验证凭据。
*   [MISC::Skeleton](https://adsecurity.org/?page_id=1821#MISCSkeleton)– 在 DC 中注入万能钥匙（Skeleton Key） 到 LSASS 进程中。这使得所有用户所使用的万能钥匙修补 DC 使用 “主密码” （又名万能钥匙）以及他们自己通常使用的密码进行身份验证。
*   [PRIVILEGE::Debug](https://adsecurity.org/?page_id=1821#PRIVILEGEDebug)– 获得 Debug 权限（很多 Mimikatz 命令需要 Debug 权限或本地 SYSTEM 权限）。
*   [SEKURLSA::Ekeys](https://adsecurity.org/?page_id=1821#SEKURLSAEkeys)– 列出 Kerberos 密钥
*   [SEKURLSA::Kerberos](https://adsecurity.org/?page_id=1821#SEKURLSAKerberos)– 列出所有已通过认证的用户的 Kerberos 凭证（包括服务帐户和计算机帐户）
*   [SEKURLSA::Krbtgt](https://adsecurity.org/?page_id=1821#SEKURLSAKrbtgt)– 获取域中 Kerberos 服务帐户（KRBTGT）的密码数据
*   [SEKURLSA::LogonPasswords](https://adsecurity.org/?page_id=1821#SEKURLSALogonPasswords)– 列出所有可用的提供者的凭据。这个命令通常会显示最近登录过的用户和最近登录过的计算机的凭证。
*   [SEKURLSA::Pth](https://adsecurity.org/?page_id=1821#SEKURLSAPth)– Hash 传递 和 Key 传递（注：Over-Pass-the-Hash 的实际过程就是传递了相关的 Key(s)）
*   [SEKURLSA::Tickets](https://adsecurity.org/?page_id=1821#SEKURLSATickets)– 列出最近所有已经过身份验证的用户的可用的 Kerberos 票证，包括使用用户帐户的上下文运行的服务和本地计算机在 AD 中的计算机帐户。与**kerberos::list**不同的是 sekurlsa 使用内存读取的方式，它不会受到密钥导出的限制。
*   [TOKEN::List](https://adsecurity.org/?page_id=1821#TOKENList)– 列出系统中的所有令牌
*   [TOKEN::Elevate](https://adsecurity.org/?page_id=1821#TOKENElevate)– 假冒令牌。用于提升权限至 SYSTEM 权限（默认情况下）或者是发现计算机中的域管理员的令牌。
*   [TOKEN::Elevate /domainadmin](https://adsecurity.org/?page_id=1821#TOKENElevate)– 假冒一个拥有域管理员凭证的令牌。

0x01 Mimikatz 命令参考
==================

* * *

Mimikatz 的模块如下：

*   CRYPTO
    *   CRYPTO::Certificates
*   DPAPI
*   EVENT
*   KERBEROS
    *   Golden Tickets
    *   Silver Tickets
    *   Trust Tickets
    *   KERBEROS::PTT
*   [LSADUMP](http://drops.com:8000/#LSADUMP)
    *   [DCSync](http://drops.com:8000/#DCSync)
    *   [LSADUMP::LSA](http://drops.com:8000/#LSADUMPLSA)
    *   [LSADUMP::SAM](http://drops.com:8000/#LSADUMPSAM)
    *   [LSADUMP::Trust](http://drops.com:8000/#LSADUMPTrust)
*   [MISC](http://drops.com:8000/#MISC)
*   [MINESWEEPER](http://drops.com:8000/#MINESWEEPER)
*   [NET](http://drops.com:8000/#Net)
*   [PRIVILEGE](http://drops.com:8000/#PRIVILEGE)
    *   [PRIVILEGE::Debug](http://drops.com:8000/#PRIVILEGEDebug)
*   [PROCESS](http://drops.com:8000/#PROCESS)
*   [SERVICE](http://drops.com:8000/#SERVICE)
*   [SEKURLSA](http://drops.com:8000/#SEKURLSA)
    *   [SEKURLSA::Kerberos](http://drops.com:8000/#SEKURLSAKerberos)
    *   [SEKURLSA::Krbtgt](http://drops.com:8000/#SEKURLSAKrbtgt)
    *   [SEKURLSA::LogonPasswords](http://drops.com:8000/#SEKURLSALogonPasswords)
    *   [SEKURLSA::Pth](http://drops.com:8000/#SEKURLSAPth)
*   [STANDARD](http://drops.com:8000/#STANDARD)
*   [TOKEN](http://drops.com:8000/#TOKEN)
    *   [TOKEN::Elevate](http://drops.com:8000/#TOKENElevate)
    *   [TOKEN::Elevate /domainadmin](http://drops.com:8000/#TOKENElevate)
*   [TS](http://drops.com:8000/#TS)
*   [VAULT](http://drops.com:8000/#VAULT)

LSADUMP
-------

Mimikatz 的 LSADUMP 模块用于与 Windows 本地安全验证（Windows Local Security Authority ）(LSA) 进程进行交互来提取凭证数据。这个模块的大多数命令都需要 Debug 权限(privlege::debug) 或者是 SYSTEM 权限。默认情况下，管理员组（Administrators）拥有 Debug 权限，但是依旧需要运行“privilege::debug”进行激活。

### LSADUMP:Backupkeys

需要管理员权限。

![p53](http://drops.javaweb.org/uploads/images/890ca40faefe0d820909cf752d983a9d9876cdb2.jpg)

### LSADUMP::Cache

需要管理员权限。

获取 SysKey 用于解密 NLKM 和 MSCache(v2)（来自注册表或 hive 文件） 。

![p54](http://drops.javaweb.org/uploads/images/2ee6eadc0ee5017937fcb3f22799535ee4d4454f.jpg)

### [LSADUMP::DCSync](https://adsecurity.org/?p=1729)

向 DC 发起同步一个对象（获取帐户的密码数据）的质询。

[需要域管理员，域管理员组或者自定义委派的一个成员权限](https://adsecurity.org/?p=1729)。

在 2015 年八月, Mimikatz 加入了一个新的特性—— “DCSync”，可以有效地“假冒”一个域控制器，并可以向目标域控制器请求帐户密码数据。此功能是由Benjamin Delpy 和 Vincent Le Toux 一起编写的。

之前利用 DCSync 的攻击方法是在域控制器上运行 Mimikatz 或 Invoke-Mimikatz 得到 KRBTGT 账户的密码哈希创建黄金票证。如果使用适当的权限执行 Mimikatz 的 DCSync 功能，攻击者就可以通过网络远程读取域控制器的密码哈希，以及以前的密码的哈希，且无需交互式登录或复制 Active Directory 的数据库文件（NTDS.DIT）。

运行 DCSync 所要求的特殊权限有管理员组（Administrators），域管理员组（ Domain Admins）或企业管理员组（Enterprise Admins）以及域控制器计算机帐户的任何成员都能够运行 DCSync 去读取密码数据。需要注意的是只读域控制器默认是不允许读取用户密码数据的。

DCSync 是何如工作的：

*   使用指定的域名称发现域控制器。
*   请求域控制器通过[DSGetNCChanges](https://msdn.microsoft.com/en-us/library/dd207691.aspx)复制用户凭据（[利用目录复制服务（DRS）远程协议](https://msdn.microsoft.com/en-us/library/cc228086.aspx)）

我之前捕获了一些域控制器复制数据的数据包，并确认了有关域控制器如何复制内部 DC 数据的通讯流。

Samba Wiki 描述了[DSGetNCChanges](https://wiki.samba.org/index.php/DRSUAPI)函数，如下：

“当第一个得到的 AD 对象从第二个更新时，客户端 DC 会向服务器发送 DSGetNCChanges 请求。响应的数据包含了一组客户端必须应用到其 NC 副本的更新。

当 DC 收到一个 DSReplicaSync 请求后，它会执行一个复制周期，去复制每一个它要复制的 DC （存储在 RepsFrom 数据结构中），此时它的行为就像一个客户端，会发送 DSGetNCChanges 请求到那个所要复制的 DC 去。所以它获得了每个它所复制的 DC 的最新的 AD 对象。

DCSync 选项：

*   /user - 要拉取数据的用户的 id 或 SID
*   /domain（可选的） Active Directory 域的 FQDN 域名，Mimikatz 会发现域中的一个 DC 并去连接。如果不提供该参数，Mimikatz 会默认设置为当前域。
*   /dc（可选的）指定你想要使用 DCSync 连接并收集数据的域控制器。 另外还有一个/guid参数。

DCSync 命令行示例：

拉取 rd.adsecurity.org 域中的 KRBTGT 用户帐户的密码数据：

```
Mimikatz "privilege::debug" "lsadump::dcsync /domain:rd.adsecurity.org /user:krbtgt" exit

```

拉取 rd.adsecurity.org 域中的 Administrator 用户帐户的密码数据：

```
Mimikatz "privilege::debug" "lsadump::dcsync /domain:rd.adsecurity.org /user:Administrator" exit

```

拉取 lab.adsecurity.org 域中 ADSDC03 域控制器的计算机帐户的密码数据：

```
Mimikatz "privilege::debug" "lsadump::dcsync /domain:lab.adsecurity.org /user:adsdc03$" exit

```

![p2](http://drops.javaweb.org/uploads/images/64edb8f24a46653d12eb8f591c034008fe785f6b.jpg)

### LSADUMP::LSA

向 LSA Server 质询检索 SAM/AD 的数据（正常或未打补丁的情况下）。可以从 DC 或者是一个 lsass.dmp 的转储文件中导出所有的 Active Directory 域凭证数据。同样也可以获取指定帐户的凭证，如 krbtgt 帐户，使用 /name 参数，如：“/name:krbtgt”需要 Debug 或 SYSTEM 权限。

*   /inject － 注入 LSASS 进程提取凭证数据
*   /name － 目标用户账户的帐户名称
*   /id － 目标用户账户的 RID
*   /patch － 补丁 LSASS 进程

通常，服务帐户是域管理员组（或同等权限）的一个成员，或者是一个攻击者导出凭证的最近登录到计算机的域管理员用户。使用这些凭证，一个攻击者可以获得DC的访问权限并且能够得到整个域的凭证，包括被用于创建 Kerberos 黄金票证的 KRBTGT 帐户的 NTLM 哈希。

命令行：**mimikatz lsadump::lsa /inject exit**

在 DC 中执行此命令可以转储活动目录中域的凭证数据。

需要管理员权限（使用 DEBUG 权限即可）或者是 SYSTEM 权限。

RID 为 502 的帐户是 KRBTGT 帐户，RID 为 500 的帐户是默认的域管理员账户。

![p3](http://drops.javaweb.org/uploads/images/cc8b5f1f7267a293e29a1253f957d8ea4c0b1dc4.jpg)

下图是运行**LSADUMP::lsa /patch**命令后只导出了 NTLM 密码哈希的执行结果。

![p4](http://drops.javaweb.org/uploads/images/843a24c2462a97eb2c7e77fb55d2e4bf735eccb9.jpg)

### LSADUMP::Rpdata

**LSADUMP::SAM**– 获得用于解密 SAM 项目（从注册表或hive中获取）数据的 Syskey。SAM 连接到了本地安全帐户管理器（SAM）数据库并且会转储本地帐户的凭证数据。

需要 SYSTEM 或 DEBUG 权限。

它包含用户密码的 NTLM 和 一些 LM 哈希。此命令可以在两种模式下工作，在线模式（使用 SYSTEM 的用户或token）或者是离线模式（使用 SYSTEM & SAM hives数据 或备份数据）

针对一个“在线”的 SAM 文件，需要管理员权限（使用 DEBUG 权限即可）或者本地 SYSTEM 权限。

获取一个模拟的 SYSTEM 令牌：**Mimikatz “PRIVILEGE::Debug” “TOKEN:elevate”**

![p5](http://drops.javaweb.org/uploads/images/2028f372644d4e6cfa875c62940a9ee26491224d.jpg)

**LSADUMP::Secrets**– 获取用于解密 SECRETS 项（从注册表或hive数据中获取）数据的 Syskey。

需要 SYSTEM 或 DEBUG 权限。

![p6](http://drops.javaweb.org/uploads/images/0b6f784b227fb3e40dc4d83f6d4cbc817962bd6a.jpg)

### LSADUMP::Trust

质询 LSA 服务器检索信任认证信息。

需要 SYSTEM 或 DEBUG 权限。

从活动目录中已有的域信任关系中提取数据。信任的密钥（密码）也将会显示出来。

![p7](http://drops.javaweb.org/uploads/images/d08c951fee44312c0b203c7ca4ac1a0ba9e0ab61.jpg)

MISC
----

Mimikatz 的 MISC 模块是一个包含了一些相当不合适的其他的命令。

在这个模块中有几个比较知名的命令，**MISC::AddSID, MISC::MemSSP, and MISC::Skeleton**。

[**MISC::AddSid**](https://adsecurity.org/?p=1772)– 将用户账户添加到 SIDHistory 中。第一个值是目标账户，第二个值是账户/组名称（或 SID）。

需要 SYSTEM 或 DEBUG 。

![p8](http://drops.javaweb.org/uploads/images/d0a0b11b791a792c837e904594f95400b4318000.jpg)

![p9](http://drops.javaweb.org/uploads/images/52deafb94e7812c544dfc749ba8b850de4086b38.jpg)

**MISC::Cmd**－ 命令行提示（无 DisableCMD）。

需要管理员权限。

![p10](http://drops.javaweb.org/uploads/images/d1f6cd56fa89de25287c76e3106aba1ae3cc5ba2.jpg)

**MISC::Detours**– (实验) 尝试使用 Detours HOOK 列举所有的模块。

需要管理员权限。

![p11](http://drops.javaweb.org/uploads/images/98479a7f6e51488de6fd952c7ba6c89fecadb5e7.jpg)

**MISC::MemSSP**– 注入一个记录本地身份认证凭证的恶意的 Windows SSP，通过在内存中对 LSASS 进程使用新的 SSP 进行补丁，此操作无需重启，重启会清除 Mimikatz 注入的 SSP。详情请见[《Mimikatz SSP 内存补丁以及更多 SSP 持久化技术》](https://adsecurity.org/?p=1760)。

需要管理员权限。

![p12](http://drops.javaweb.org/uploads/images/0bde7f7422de89dd7940cd8e700196d3df7a6180.jpg)

[曼迪昂特对 MemSSP 的介绍](https://dl.mandiant.com/EE/library/MIRcon2014/MIRcon_2014_IR_Track_Analysis_of_Malicious_SSP.pdf)

**MISC::Ncroutemon**– Juniper 管理器 (无 DisableTaskMgr)  
**MISC::Regedit**– 注册表编辑器 (无 DisableRegistryTools)

需要管理员权限。

![p13](http://drops.javaweb.org/uploads/images/2a305121646b3d3c80339edeca43c6c338ae41bd.jpg)

[**MISC::Skeleton**](https://adsecurity.org/?p=1275)- 在 DC 上将 Skeleton 密钥注入到 LSASS 进程中。

需要管理员权限。

此操作会对 DC 进行补丁，使得所有用户将使用的 “主密码” （又名万能钥匙）以及他们自己通常使用的密码进行身份验证。

![p14](http://drops.javaweb.org/uploads/images/d651600c124894a7ad180ece7f994ead8abbb263.jpg)

**MISC::Taskmgr**- 任务管理器（无 DisableTaskMgr）

需要管理员权限。

![p15](http://drops.javaweb.org/uploads/images/0934fd61fc3a4f69091449e776cf5b5e8ba2cda8.jpg)

**MISC::Wifi**

MINESWEEPER
-----------

**MINESWEEPER::Infos**– 提供 minesweeper 的雷达信息。

Net
---

**NET::User**  
**NET::Group**  
**NET::LocalGroup**

PRIVILEGE
---------

**PRIVILEGE::Debug**- 获取 DEBUG 权限。（DEBUG 或 SYSTEM 权限是很多 Mimikatz 命令所需要的权限）

默认情况下：管理员组拥有 DEBUG 权限。但是依旧需要使用**“privilege::debug”**命令进行激活。

DEBUG 权限允许你对一个没有其他方式接触的进程进行调试。例如，一个拥有DEBUG权限的用户进程的令牌可以对一个使用本地 SYSTEM 权限运行的服务进程调试。

[http://msdn.microsoft.com/library/windows/hardware/ff541528.aspx](http://msdn.microsoft.com/library/windows/hardware/ff541528.aspx)

![p16](http://drops.javaweb.org/uploads/images/d753f371f93d895962ba456660dffb60cf45022b.jpg)

Benjamin 对此命令的备注信息:

如果执行此命令出现**ERROR kuhl_m_privilege_simple ; RtlAdjustPrivilege (20) c0000061**错误，可能你没有使用管理员权限执行此命令。

PROCESS
-------

Mimikatz 的 PROCESS 模块提供了收集进程的数据和与进程进行交互的功能。

**PROCESS::Exports**– 列出进程可执行文件的导出表

![p17](http://drops.javaweb.org/uploads/images/e82faafcb45030c8a9a693c98143d14225e612b8.jpg)

**PROCESS::Imports**– 列出进程可执行文件的导入表

![p18](http://drops.javaweb.org/uploads/images/0790f74d5bdceab3d6dc567bfaeaa9b78696f7c5.jpg)

**PROCESS::List**– 列出正在运行的进程。

需要管理员权限。  
![p19](http://drops.javaweb.org/uploads/images/02bee827598128bd5d74b6081866ff68f42e401a.jpg)

**PROCESS::Resume**- 恢复一个进程

![p20](http://drops.javaweb.org/uploads/images/69a1001dbedd0465be4cc1664cb07aeb79e0611b.jpg)

**PROCESS::Start**– 启动一个进程  
**PROCESS::Stop**– 结束一个进程  
**PROCESS::Suspend**– 挂起一个进程

![p21](http://drops.javaweb.org/uploads/images/c57074b1a9c2585c5b176a881f6fa7943de66e7f.jpg)

SERVICE
-------

**SERVICE::List**– 列出所有服务  
**SERVICE::Preshutdown**– 预关掉服务  
**SERVICE::Remove**– 卸载服务  
**SERVICE::Resume**– 恢复服务  
**SERVICE::Shutdown**– 关掉服务  
**SERVICE::Start**– 启动一个服务  
**SERVICE::Stop**– 停止服务  
**SERVICE::Suspend**– 挂起服务

SEKURLSA
--------

Mimikatz 的 SEKURLSA 模块提供了与被保护的内存进行交互的功能。此模块能够从 LSASS（本地安全认证子系统服务） 进程的内存中提取密码，密钥，pin 码，票证。  
为了能够与 LSASS 进程进行交互，Mimikatz 进程需要适当的权限：

*   管理员权限，使用 “PRIVILEGE::Debug” 命令获取 DEBUG 权限
*   SYSTEM 权限，使用 “TOKEN::elevate” 获取 SYSTEM 权限

转储 LSASS 进程内存文件，不需要进程权限提升操作。

**SEKURLSA::Backupkeys**－ 获得首选备份的主密钥。

![p22](http://drops.javaweb.org/uploads/images/fbd6b01c9d588e5a43a83cc13c98d346f2e9593b.jpg)

**SEKURLSA::Credman**- 列出凭证管理器

![p23](http://drops.javaweb.org/uploads/images/2c9017929cecbac07376c3eb19dc8b0a872b5e7f.jpg)

**SEKURLSA::Dpapi**– 列出已缓存的主密钥

![p24](http://drops.javaweb.org/uploads/images/dddadc044107d1e11cea16291fdd9a80277f9814.jpg)

**SEKURLSA::DpapiSystem**- 获取 DPAPI_SYSTEM 密文

![p25](http://drops.javaweb.org/uploads/images/d7b5d6dde12b84bed09aef055210a9713f5a8f8e.jpg)

**SEKURLSA::Ekeys**– 列出 Kerberos 加密密钥

![p26][288]

**SEKURLSA::Kerberos**– 列出所有已通过验证的用户（包括服务和计算机帐户）的 Kerberos 凭证。

![p27](http://drops.javaweb.org/uploads/images/e149712546aaa240727457ea20310dd126949f2c.jpg)

**SEKURLSA::Krbtgt**- 获取域 Kerberos 服务帐户（KRBTGT）密码数据

![p28](http://drops.javaweb.org/uploads/images/4821ec1b2369f720a41d6a298be2f396a2eec38c.jpg)

**SEKURLSA::LiveSSP**– 列出 LiveSSP 凭证

![p29](http://drops.javaweb.org/uploads/images/723b816550e58f6e1b690e2e8fe3b2a39ba38358.jpg)

**SEKURLSA::LogonPasswords**– 列出所有可用的提供者的凭证数据。命令执行结果会显示最近登陆的用户和计算机的凭证。

*   转储存储在 LSASS 进程中，当前已登陆或最近登录的帐户以及使用用户凭证上下文运行的服务的密码数据。
*   帐户密码使用可逆的方式存储在内存中。如果在内存中有这些数据（Windows 8.1/Windows Server 2012 R2之前），那么这些数据将会被显示出来。在大多数情况下，Windows 8.1/Windows Server 2012 R2 并没有使用相同的方式存储帐户密码。KB2871997 补丁讲此安全特性兼容至 Windows 7， Windows 8， Windows Server 2008R2 和 Windows Server 2012 中，尽管在应用了 KB2871997 补丁后需要对计算机进行额外的配置。
*   需要管理员权限（带有 DEBUG 权限）或 本地 SYSTEM 权限

**Windows Server 2008 R2 （显示明文密码）**

![p30](http://drops.javaweb.org/uploads/images/977fc90336f22aa30eb20694a52b2b93c500643d.jpg)

**Windows Server 2012 R2 （未显示明文密码）**

![p31](http://drops.javaweb.org/uploads/images/f3974c5c399fe9796c38d906f791d76a86b18d9a.jpg)

同样可以使用此命令将使用帐户凭证运行的服务的凭证进行转储。需要注意的是，只有服务正在运行（运行后凭证才会存储在内存中）才可以使用此方式进行转储。

![p32](http://drops.javaweb.org/uploads/images/f880674ce96efcb296acdf0dab6244edc374048a.jpg)

![p33](http://drops.javaweb.org/uploads/images/e1d24992f4db64574f41b0514ff588e349c383e9.jpg)

![p34](http://drops.javaweb.org/uploads/images/0ed1ae523ba7706a91c4d2dff56f332fe1dcd59d.jpg)

**SEKURLSA::Minidump**– 切换到“轻量级”转储 LSASS 进程上下文

需要注意的是，Minidumps 是对相同的平台上进行转储的数据进行读取， NT5 Win32 or NT5x64 or NT6 Win32 or NT6 x64。

![p35](http://drops.javaweb.org/uploads/images/165563b8386866a1eb33ec5c97e890a8e1bf5e91.jpg)

**SEKURLSA::MSV**– 列出 LM 和 NTLM 凭证数据

![p36](http://drops.javaweb.org/uploads/images/d4886c5bc97ec98d05898ac58ea7ec09f956d394.jpg)

**SEKURLSA::Process**– 转换到 LSASS 进程上下文

![p37](http://drops.javaweb.org/uploads/images/27e8b004b852306eb4b093dea4c5a3ecd2df9c94.jpg)

**SEKURLSA::Pth**– Hash 传递， key 传递

Mimikatz 可以执行众所周知的“Hash 传递”，使用另一个用户密码的 NTLM 哈希上下文代替其真实的明文密码运行一个进程。为此，它会启动一个带有假冒身份信息的进程，之后会替换假信息（假密码的 NTLM 哈希）为真实的信息（真正的密码的 NTLM 哈希）。

*   /user － 你想进行假冒的用户名，需要明白的是，Administrator 不是唯一一个已知的帐户。
*   /domain – 域名称的 FQDN，无需添加本地用户名火管理员名称，可以使用计算机或服务器名称，工作组名称。
*   /rc4 or /ntlm （可选的） – 指定用户的 RC4 密钥 或 NTLM 哈希。
*   /run （可选的） – 需要运行的命令行 – 默认为：cmd ，得到一个 cmd shell。

![p38](http://drops.javaweb.org/uploads/images/0300107c2ce7a4a7d7341b08f4632a491f1d54f1.jpg)

Benjamin 对此命令的备注：

*   该命令不能与 minidumps 一起使用
*   需要权限提升（privilege::debug 或 SYSTEM 帐户），不像票证传递（Pass-The-Ticket）使用官方的 API，新版本的哈希传递通过使用 NTLM 哈希（或者是 AES 密钥）替换 Kerberos 的 RC4 密钥 － 它允许 Kerberos 提供者质询 TGT 票证。
*   在 WinXP/2003/Vista/2008 ，以及未打 kb2871997 补丁之前（AES 不可用或不可替代）的 Win7/2008r2/8/2012 中强制使用 NTLM 哈希。
*   AES 密钥只有在 8.1/2012r2 和打了 kb2871997 补丁的 7/2008r2/8/2012 中才可以替换，在这种情况下，你可以避免使用 NTLM 哈希。

[Benjamin 发表了一篇关于密钥传递的文章](http://blog.gentilkiwi.com/securite/mimikatz/overpass-the-hash)。

**SEKURLSA::SSP**－ 列出 SSP 凭证。

![p39](http://drops.javaweb.org/uploads/images/0886f2e763bd17adf01231a6784a36b778ce84b7.jpg)

**SEKURLSA::Tickets**- 列出最近所有已经过身份验证的用户的可用的 Kerberos 票证，包括使用用户帐户的上下文运行的服务和本地计算机在 AD 中的计算机帐户。

与 kerberos::list 不同的是 sekurlsa 使用内存读取的方式，它不会受到密钥导出的限制。

*   /export (可选的)－导出票证到 .kirbi 文件中。文件名称使用用户的 LUID 和组编号(0 = TGS， 1 = 客户端票证(?) ， 2 = TGT)作为开头。

类似于从 LSASS 中转储凭证数据，利用 SEKURLSA 模块，攻击者可以获取到所有在内存中的 Kerberos 票证数据，包括那些属于管理员或服务的票证。

如果攻击者已经入侵了一台使用 Kerberos 委派配置的 Web 服务器，在用户访问后端的 SQL 服务器时，这是非常有用的。这使得攻击者能够捕捉和重用该服务器上内存中的所有用户的票证。

Mimikatz 的 “kerberos::tickets” 命令可以转储当前已登陆的用户的 Kerberos 票证并且不需要权限提升。利用 SEKURLSA 模块的功能，可以读取被保护的内存（LSASS），在系统中的所有的 Kerberos 票证均可以转储。

命令：**mimikatz sekurlsa::tickets exit**

*   转储系统中所有已通过验证的 Kerberos 票证
*   需要已激活 DEBUG 权限的管理员权限或本地 SYSTEM 权限

下图显示了转储另外一个域管理员（LukeSkywalker）的密码和Kerberos票证（TGS 和 TGT）。  
![p40](http://drops.javaweb.org/uploads/images/43909d72971bada69ee44f4795c61857da8e9e60.jpg)

![p41](http://drops.javaweb.org/uploads/images/f247cce53f3d5972dcf1831f0e81b9421621baa1.jpg)

下图显示了转储另外一个域管理员（HanSolo）的密码和Kerberos票证（TGS 和 TGT）。  
![p42](http://drops.javaweb.org/uploads/images/9b99a0ed1d8cf21970a4d69b8f8eb0397fc77db8.jpg)

下图显示了转储一个 SQL 服务帐户（svc-SQLDBEngine01）的密码和Kerberos票证（TGS 和 TGT）。  
![p43](http://drops.javaweb.org/uploads/images/40875203c7825c4e4207f619a78c0810bfc8b279.jpg)

**SEKURLSA::Trust**– 获取信任密钥

(我认为此命令已过时，可以使用 lsadump::trust /patch)

**SEKURLSA::TSPKG**－ 列出 TsPkg 凭证。

![p44](http://drops.javaweb.org/uploads/images/825659fa26318d81516a2a57404300725f063c3e.jpg)

**SEKURLSA::Wdiget**- 列出 Wdiget 凭证。

![p45](http://drops.javaweb.org/uploads/images/06e5cd5862e6bc4e3ffdea21510411bac8398bb0.jpg)

STANDARD
--------

**STANDARD::Base64**– 转换输出到 Base64 输出  
**STANDARD::CD**– 改变或显示当前文件夹  
**STANDARD::CLS**– 清屏  
**STANDARD::Exit**– 退出 Mimikatz  
**STANDARD::Log**– 记录 Mimikatz 数据到日志文件中  
**STANDARD::Sleep**– 指定毫秒级的延时  
**STANDARD::Version**– 显示版本信息

TOKEN
-----

Mimikatz 的 Token 模块能够与 Windows 身份验证令牌进行交互，包括抓取，伪造假冒的已存在的令牌。

**TOKEN::Elevate**– 假冒令牌。用于提升权限至 SYSTEM 权限（默认）或者使用 Windows API 找到域管理员令牌。

需要管理员权限。  
![p46](http://drops.javaweb.org/uploads/images/ece5a699ebadb5036826738568b3daceada1d7a9.jpg)

找到一个域管理员凭证并且使用该域管理员的令牌：

**token::elevate /domainadmin**

![p47](http://drops.javaweb.org/uploads/images/51a976cac937c5fe6f010771f056ccd7ac60d860.jpg)

**TOKEN::List**- 列出系统中所有的令牌

![p48](http://drops.javaweb.org/uploads/images/4cd85f001e89cf917e260dfc7b1d0eb713f31790.jpg)

**TOKEN::Revert**- 恢复进程令牌

![p49](http://drops.javaweb.org/uploads/images/ce4394a2d766f7102bef587994c3d4610a17bad4.jpg)

**TOKEN::Whoami**– 显示当前身份信息

![p50](http://drops.javaweb.org/uploads/images/ce8d87fef3d6f011e3dea199240e7c8f01ef2342.jpg)

TS
--

**TS::Multirdp**- (实验) 补丁终端服务器服务允许多个用户连接

![p51](http://drops.javaweb.org/uploads/images/b497f0db961b5a5a224c407886e2f3014d25b513.jpg)

VAULT
-----

**VAULT::List**- 列出 Vault 凭证

![p52](http://drops.javaweb.org/uploads/images/73311d6ad53bcdd813a94098d655c2d97a437816.jpg)

**VAULT::Cred**- cred

**原文所有权归 Sean Metcalf (ADSecurity.org) 所有**  
**本文由 Her0in 翻译并首发于乌云 drops，转载请注明出处**