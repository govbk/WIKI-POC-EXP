# 绕过 Cisco TACACS+ 的三种攻击方式

原文地址：[3 attacks on cisco tacacs bypassing](http://122.225.209.140/cgi-bin/ftnviewcpsfile?fid=2%2F9e761024-519c-4612-851e-77164dc4578a&u=441928977&packname=test.zip&path=test%2F%3Cscript%3Ealert(1)%3C%3Ascript%3E.png&key=BcMU4Wys-pypAlQY&action=compresspic1)

在这篇文章中，作者介绍了绕过 Cisco 设备的 TACACS 的三种方式。

*   No.1 利用 DoS 攻击绕过 Cisco TACACS+
*   No.2 本地爆破 PSK 绕过 Cisco TACACS+
*   No.3 利用中间人攻击 绕过 Cisco TACACS+

一般来说，在一个大型网络中会有很多网络设备，如何管理这些网络设备的访问权限可能是个大问题。因此，大多数公司都会实现集中化的权限访问协议。Cisco 设备支持 TACACS+ 和 RADIUS 协议。

0x00 TACACS 协议简介
================

* * *

TACACS（Terminal Access Controller Access Control System，终端访问控制器控制系统协议）是一种用于认证的计算机协议，在 UNIX 网络中与认证服务器进行通信，TACACS 允许远程访问服务器与认证服务器通信，以决定用户是否有权限访问网络。

TACACS 允许客户端接受用户名和口令，并发往通常称作 TACACS 守护进程（或者简单地称作 TACACSD ）的 TACACS 认证服务器，这个服务器一般是在主机上运行的一个程序。主机将决定是否接受或拒绝请求，并发回一个响应。 TIP（用户想要登录的接受拨入链接的路由节点）将基于这个响应接受或拒绝访问。这样，做出决定的过程是"向上开放"(opened up)的，做出决定所用的算法和数据完全由 TACACS 守护进程的运行者控制。

Cisco 在 1990 引进的最近的 TACACS 版本称作 XTACACS（扩展 TACACS）。在较新的或更新过的网络中，这两个版本大多被 TACACS+ 和 RADIUS 所取代。

TACACS 在[RFC 1492](https://tools.ietf.org/html/rfc1492)中定义，默认使用 TCP 或 UDP 协议的 49 端口。

0x01 TACACS＋ 协议简介
=================

* * *

TACACS+ 是一个全新的协议，与 TACACS 和 XTACACS 并不兼容。TACACS+ 所使用的端口为 TCP/49。

TACACS+（Terminal Access Controller Access Control System Plus）是在 TACACS 协议的基础上进行了功能增强的安全协议。该协议与 RADIUS 协议的功能类似，采用客户端/服务器模式实现 NAS 与 TACACS+ 服务器之间的通信。

TACACS+ 协议主要用于 PPP 和 VPDN（Virtual Private Dial-up Network，虚拟私有拨号网络）接入用户及终端用户的 AAA。

AAA 是 Authentication、Authorization、Accounting（认证、授权、计费）的简称，是网络安全的一种管理机制，提供了认证、授权、计费三种安全功能。

*   认证：确认访问网络的远程用户的身份，判断访问者是否为合法的网络用户。
*   授权：对不同用户赋予不同的权限，限制用户可以使用的服务。例如用户成功登录服务器后，管理员可以授权用户对服务器中的文件进行访问和打印操作。
*   计费：记录用户使用网络服务中的所有操作，包括使用的服务类型、起始时间、数据流量等，它不仅是一种计费手段，也对网络安全起到了监视作用。

0x02 TACACS＋ 认证过程
=================

* * *

TACACS+ 服务通常会有一个特殊的服务器，所有的网络设备都会被配置成使用 TACACS+ 服务器进行身份验证。当一个用户在交换机，路由器或其他网络设备上进行认证时，网络设备会发送该用户的凭证到 TACACS+ 服务器进行验证，然后决定分配访问相关设备的权限，并将这些决定的结果包含在应答数据包中并发送到网络设备上，再由网络设备发送到用户终端。

![p1](http://drops.javaweb.org/uploads/images/69ea2c05c9affdfbfdec7e83c51f67c9cc4a2e79.jpg)图 1 ： TACACS＋ 认证过程

这是一个非常方便和集中化的做法。可以在不同的设备上为用户设置不同的权限。还有就是记录访问和操作均在服务器端。也可以在当前这种模式下再添加一种集中化式的管理方式，如 Active Directory 或 LDAP。不过，思科已将[TACACS+ 协议规范公开](http://tools.ietf.org/html/draft-grant-tacacs-02)，所以现在有了一种 TACACS+ 服务的开源实现。

0x03 绕过 Cisco TACACS＋ 的三种攻击方式
=============================

* * *

### No.1 利用 DoS 攻击绕过 Cisco TACACS+

第一种攻击方式并不是一种攻击类型，准确的说是一个技巧，但是有时候在某些情况下是非常有用的。

让我们假定这么一个场景：

某渗透人员在目标公司的 TFTP 服务器中下载到了 Cisco 设备的配置文件，但是即使利用该配置文件破解出了设备的登陆账户信息，也依旧无法登陆到该设备中，原因就在于该设备将会使用 TACACS+ 服务验证本地账户。

使用 TACACS+ 进行身份验证是网络设备的一种典型配置。让我们继续假设，在 TACACS+ 服务器与网络设备之间发生了点什么，导致网络设备无法访问 TACACS+ 服务器。在这种情况，连管理员自己都不可能登录到网络设备中。为了解决这样的典型情况，Cisco 设备支持认证方式的回退，管理员可以设置不同的认证配置。

在 Cisco 设备中，一种使用 TACACS+ 进行身份验证的典型配置如下：

```
aaa authentication login default group tacacs+ local

```

上述配置表明，首选的身份验证为 TACACS+，之后才会使用本地验证方式（查询本地数据库）进行身份验证。同时，要注意，即使 TACACS+ 服务没有发现一个用户的认证凭证，设备也不会使用本地验证方式。

也就是说，只有在 TACACS+ 服务不可用时，才会使用本地验证方式。

所以，第一种攻击思路很简单。我们只要对 TACACS+ 服务发动 DoS 攻击，之后连接到 Cisco 设备的本地帐户中（从 TFTP 服务器中下载并破解得到）。由于 TACACS+ 服务遭到 DoS 攻击无法访问，所以网络设备会提供给我们所期望的访问权限。我们可以使用多种 DoS 攻击。例如，我们可以发动临时的 DoS 攻击，对 TACACS+ 服务器创建大量基于 TCP 的连接。

![p2](http://drops.javaweb.org/uploads/images/9d09990073b124660ac41f49afa38524da4059ee.jpg)图 2 ：对 TACACS+ 服务器发动 DoS 攻击

### 在介绍第二种和第三种攻击方式前需要了解的知识

在介绍第二种和第三种攻击方式前，我们需要了解一下 TACACS+ 协议。该协议的数据是明文或者是加密后传输的。采用了基于PSK（预共享密钥）的自定义加密方式。管理员可以在 TACACS+ 服务器上设置加密密钥，只要能够访问到 TACACS+ 服务器的网络设备都会在身份验证时使用这个加密密钥。

有一点值得注意的是，只有用户的凭证数据是加密的， TACACS+ 协议的报头信息并没有加密。

加密的具体细节如下：

加密的结果（`enc_data`）是未加密的用户的凭证数据 （`data`）与一个特殊的字符串（`pseudo_pad`）进行`XOR`操作后得到的。

```
data^pseudo_pad = enc_data

```

pseudo_pad 是几个拼接的 MD5 哈希。

```
pseudo_pad = {MD5_1 [,MD5_2 [ ... ,MD5_n]]}

```

MD5 哈希的值是对 TACACS+ 数据包报头信息，密钥（PSK）和前一个 MD5 哈希值加密的结果。因此，可以看到，第一个 MD5 是没有前一个 MD5 哈希值的。

```
MD5_1 = MD5{session_id, key, version, seq_no}
MD5_2 = MD5{session_id, key, version, seq_no, MD5_1}
....
MD5_n = MD5{session_id, key, version, seq_no, MD5_n-1}

```

*   SESSION_ID - 是一个会话的随机标识符;
*   version - TACACS+ 协议的版本;
*   seq_no - 会话数据包的增量;
*   key - PSK。

加密的数据如下图所示：

![p3](http://drops.javaweb.org/uploads/images/5d46b700ef5efba44968f0db39dff1cd947e3388.jpg)图 3 ：数据包中的加密数据

### No.2 爆破 PSK 绕过 Cisco TACACS+

OK，了解了上面的一些知识后，我们就可以理解后面两种攻击方式了。

假设现在有一台 Cisco 网络设备和一台 TACACS+ 服务器，我们已经得到了这两台服务器之间传输的 TACACS+ 协议的加密数据（可以通过中间人攻击得到）。现在，我们只要得到了 PSK 就可以解密已加密的数据，之后，我们就可以得到一个有效的账户了。

现在，让我们看看该如何做到这一点。首先，我们可以看到，任何一个 MD5 哈希（尤其是第一个 MD5）都是由几个固定的值组成的。但是，其中只有一个是未知的 —— PSK。所有其它的值（SESSION_ID，version，seq_no），我们都可以从 TACACS+ 数据包的报头中获取到。因此，我们可以使用本地离线暴力破解攻击的方式获得 PSK。而我们知道，暴力破解 MD5 是很快的。但在开始爆破前，我们需要得到第一个 MD5 哈希（**MD5_1**）。

我们知道，XOR 是一种可逆性的操作。所以，我们可以这样做

```
data^pseudo_pad = enc_data

```

将其转换为

```
pseudo_pad = data^enc_data

```

`MD5_1`只是`pseudo_pad`的第一部分。`pseudo_pad`的大小为 128位（或16字节）。如果我们想得到`MD5_1`，我们需要知道 16字节的已加密和已解密的数据即(`data`)。我们可以从传输的数据包中获得已加密数据。但是，现在我们如何才能得到 16字节 的解密数据呢？

需要注意的是，身份验证、授权、计费这三种类型的 TACACS + 数据包的请求和响应的格式是不同的。然而，对于这些不同的数据包，我有一个通用的思路，因为，在任何类型的数据包的前 16 个字节中几乎没有未知的或随机的值。

我不会去深究每种数据包类型中的技术细节。只是举一个例子以说明这个想法。这是 TACACS+ 服务器响应的第一个数据包(如下图所示)。它由几个具有单一意义的字段和一条 Cisco 设备发送给用户的问候消息组成。由于我们可以任意连接到 Cisco 设备，所以就可以很轻易的得到响应数据包同时也就知道了所有字段的值。

![p4](http://drops.javaweb.org/uploads/images/c119dbc0e0d4bc1ca4a0ea4b37ea47879b62e0b1.jpg)图 4 : TACACS+ 服务器响应的第一个数据包

因此，从目前来看，我们几乎总是可以知道任何数据包的前 16 字节解密后的数据。所以我们就可以得到`MD5_1`，并使用本地离线暴力破解进行攻击。如果爆破成功了，我们就能够解密整个通信的数据。为了简化数据包的接收并解析出`MD5_1`，我写了一个小脚本 —— tac2cat.py。它是[TacoTaco 项目](https://github.com/GrrrDog/TacoTaco)的一部分。

### No.3 利用中间人攻击 绕过 Cisco TACACS+

对于最后一种攻击方式，我们可以利用中间人攻击篡改 TACACS+ 服务器和 Cisco 设备之间传输的数据。我们的目的是获取到 Cisco 设备的所有权限。

在重新审查 TACACS+ 协议时，我发现了两个额外的"特点"。

第一个是在 TACACS+ 协议传输过程中并没有检查数据包的完整性。所以，如果我们利用中间人攻击改变了传输中的加密的部分，那么也就改变了解密的结果 (因为它只进行了 XOR 操作)，但 TACACS+ 服务器并不会发现所做的更改，并以正常的方式处理已经被修改过的传输数据。

![p5](http://drops.javaweb.org/uploads/images/6db81ad1510eb4a0d497fb9068293788b80bc517.jpg)图 5 ： TACACS+ 协议数据包

第二个特点是关于 TACACS+ 数据包的格式。在身份验证和授权的过程中，应答的数据包中的第一个字节指示了访问权限授予的结果。

例如，"0x01"代表了用户通过了服务器的身份验证过程 (授予访问权限) ，"0x02"代表了用户的凭据是无效的。

总之，我们只需要更改服务器应答的数据包的一个字节即可!

*   获取该字节的`pseudo_pad`: 将加密的字节和解密的字节进行 XOR 操作 (我们知道解密的字节的值，因为如果我们输入不正确的凭据后，服务器会拒绝访问并设置第一个字节为 0x02。
*   将这个`pseudo_pad`与成功的身份验证标识 (0x01) 进行 XOR 操作
*   将新的字节加入到加密的数据包中并发送给服务器。

因此，利用中间人攻击，我们可以对任何使用无效凭证的用户的传输数据和访问权限授予（身份认证和授权）进行更改。此外，我们也可以绕过 Cisco 设备中特权用户提升（“enable” 密码）的身份验证过程。

为了方便进行中间人攻击，我写了一个小脚本——tacflip.py，是[TacoTaco 项目](https://github.com/GrrrDog/TacoTaco)的一部分。

我已经在 Cisco 7200 路由器的 GNS3 模拟器和开源实现的 TACACS+ 服务器——tac_plus 中成功验证了这种（绕过身份验证，特权用户提升授权）攻击方式，下面是路由器中配置文件的一部分：

```
aaa authentication login default group tacacs+ local
aaa authentication enable default group tacacs+
aaa authorization exec default group tacacs+ local
tacacs-server host 192.168.182.136
tacacs-server directed-request
tacacs-server key 12345

```

这个小视频演示了在 Cisco 路由上进行绕过身份验证/授权、特权提权和命令执行的攻击过程。

[点我看小视频](https://youtu.be/HdTib8wftHA)

0x04 一点儿题外话
===========

* * *

在 2000 年，Solar Designer 针对 TACACS+ 协议做了一个很有趣的研究（[链接在此](https://goo.gl/E2IGnk)），例如，他发现了重放攻击，用户密码长度信息泄漏，位翻转攻击等漏洞。但我并没有找到 这些漏洞的 PoCs。

对于我对 TACACS+ 协议所做的"研究"，都是在与协议进行了随机的互动操作后的很长一段时间里的一些想法。正因为如此，我忘了有关 Solar Designer 研究的结果并且重新了解了他的一些发现。

因此，可能我工作的最重要的结果就是[TacoTaco 项目](https://github.com/GrrrDog/TacoTaco)。它是这篇文章所讲述的攻击方式的具体实现。

0x05 总结
=======

* * *

从目前来看，我认为，TACACS+ 协议并没有针对中间人攻击提供必要的保护级别。

不过话又说回来，有时很难在实战中执行所有这些攻击操作，因为 Cisco 建议将 TACACS+ 服务器放置在一个特殊的管理方式中 —— VLAN (只有管理员和网络设备才能访问) 。当然，也有方法可以渗透到 VLAN 中并控制它，不过这就是另一码事儿了。

0x06 参考及引用
==========

* * *

*   [https://zh.wikipedia.org/wiki/TACACS](https://zh.wikipedia.org/wiki/TACACS)
*   [http://www.h3c.com.cn/MiniSite/Technology_Circle/Net_Reptile/The_Seven/Home/Catalog/201309/797633_97665_0.htm](http://www.h3c.com.cn/MiniSite/Technology_Circle/Net_Reptile/The_Seven/Home/Catalog/201309/797633_97665_0.htm)
*   [https://zh.wikipedia.org/wiki/TACACS%2B](https://zh.wikipedia.org/wiki/TACACS%2B)