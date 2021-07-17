# 如何发现 NTP 放大攻击漏洞

原文：[http://jamesdotcom.com/?p=578](http://jamesdotcom.com/?p=578)

NTP 漏洞相关的文章在 Drops 已经有过了，并且不止一篇，之所以又翻译了这一片文章，是觉得文章的整体思路很不错，希望对看这篇文章的你有所帮助。

BTW：本文翻译比较随意，但是并没有破坏原文含义。

0x00 简介
-------

* * *

NTP 放大攻击其实就是 DDoS 的一种。通过 NTP 服务器，可以把很小的请求变成很大的响应，这些响应可以直接指向到受害者的电脑。

NTP 放大使用的是 MONLIST 命令。MONLIST 命令会让 NTP 服务器返回使用 NTP 服务的最后 600 个 客户端 IP。通过一个有伪造源地址的 NTP 请求，NTP 服务器会将响应返回给那个伪造的 IP 地址。你可以想象，如果我们伪造受害者的 IP 对大量的 NTP 服务器发送 MONLIST 请求，这将形成 DOS 攻击。

显然我们不能容忍这样做，但我比较有兴趣的是去发现有多少 NTP 服务器能够发大这种数据。他不是什么新的攻击，所以你希望不会有太多的 NTP 服务器支持 MONLIST 命令。

0x01 如何去做
---------

* * *

为了确定有多少 NTP 服务器响应 MONLIST 请求，我会通过两个独立的部分去做。

### 第一部分

在第一部分，通过 masscan 工具，对 UDP 的 123 端口进行扫描，扫描结果保存到 ntp.xml 文件中，命令如下：

```
./masscan -pU:123 -oX ntp.xml --rate 160000 101.0.0.0-120.0.0.0

```

由于我的服务器带宽比较小，如果选择全网扫描，肯定会较慢，所以我随机的选择了一个 IP 段：101.0.0.0-120.0.0.0。

扫描完成后，会把 UDP 123 端口开放的设备保存在 XML 文件中。不知道什么原因，我的扫描结果 xml 文件中包含了许多重复的记录，我写了一个 python 脚本用于处理这些重复的记录，去重后的结果会保存到 port123.txt 文件中。

代码如下：

```
from lxml import etree
port = None
address = None
parsedServers = []
#Opens the file used to store single enteries.
outputFile = open('port123.txt', 'a')
#Iterates through the masscan XML file.
for event, element in etree.iterparse('ntp.xml', tag="host"):
    for child in element:
        if child.tag == 'address':
            #Assigns the current iterations address to the address variable.
            address = child.attrib['addr']
        if child.tag == 'ports':
            for a in child:
                #Assigns the current iterations port to the port variable.
                port = a.attrib['portid']
        #is both port and IP address are present.
        if port > 1 and address > 1:
            #If the IP hasnt yet been added to the output file.
            if address not in parsedServers:
                print address
                #Write the IP address to the file.
                outputFile.write(address + '\n')
                #write the IP to the parsedServers list
                parsedServers.append(address)
            port = None
            address = None
    element.clear()
outputFile.close()
print 'End'

```

这个脚本运行后，port123.txt 文件中包含开放 UDP 123 端口并且去重后的所有 IP。

### 第二部分

在第二部分中我们主要来确定 port123.txt 中的 IP 的 123 端口是否运行 NTP 服务，如果是 NTP 服务，是否响应 MONLIST 请求。

我写了一个 python 脚本来实现上面的需求，主要用到 scapy 库。

首先我导入我脚本需要的所有库，并且定义一些变量：

```
from scapy.all import *
import thread

```

然后我构造了发给 NTP 服务器的 MONLIST 请求的原始数据。在这个过程中我发现请求的数据必须达到一定的值服务器才会返回数据，具体原因不清楚。只要请求超过 60 字节，服务器就会返回数据，因此我下面的代码中有 61 个`\x00`字符。

```
rawData = "\x17\x00\x03\x2a" + "\x00" * 61

```

在 python 脚本中我打开了两个文件：port123.txt 是 masscan 发现的开放 UDP 123 端口的 IP 地址，monlistServers.txt 是用于保存支持 MONLIST 命令的 NTP 服务器。

```
logfile = open('port123.txt', 'r')
outputFile = open('monlistServers.txt', 'a')

```

然后我定义了一个叫`sniffer`的函数，这个函数的作用主要就是监听在 48769 端口上的 UDP 数据，这个端口是发送 MONLIST 请求的源端口，只要任何 NTP 服务器响应 MONLIST 请求，都将响应到这个端口上。目标网络地址是你的 IP 地址，NTP 服务器的响应将返回到这个 IP 上，在本文中，我讲设置这个 IP 为：99.99.99.99。

```
def sniffer():
    sniffedPacket = sniff(filter="udp port 48769 and dst net 99.99.99.99", store=0, prn=analyser)

```

任何符合 UDP 端口 48769 的数据包都会被捕获到，并且会放到 analyser 函数中，稍后我讲介绍 analyser 函数。

sniffer 定义好了，并且会在线程中执行，同时会放到后台运行。

```
thread.start_new_thread(sniffer, ())

```

接下来，我遍历 masscan 发现的所有 IP 地址。对于每个 IP 地址我都会发送一个源端口为 48769，目的端口是 123 的 UDP 数据包，数据包就是我们前面构造的 rawData。实际上这个就是对所有的 IP 发送 MONLIST 请求。

```
for address in logfile:
    send(IP(dst=address)/UDP(sport=48769, dport=123)/Raw(load=rawData))

```

只要有 NTP 服务器响应 MONLIST 请求，这个响应数据将会被运行在线程中 sniffer 抓取，sniffer 会把所有接收到的数据放到 analyser 函数中处理，而 analyser 函数会检查捕获到的数据包，并且确定包的大小超过 200 字节。在实际的测试中我发现，如果 NTP 服务器不响应 MONLIST 请求，响应包的大小通常在 60-90 字节，或者不存在响应包。如果 NTP 服务器响应 MONLIST 请求，响应包就会比较大，一般包含多个响应包，通常每个包为 480 字节。所以只要检查到所接收的响应包是大于 200 字节就表示该 NTP 服务器支持 MONLIST 请求。最后我们会把响应包大约 200 字节的 IP 地址写入到 outputFile。

```
    if len(packet) > 200:
        if packet.haslayer(IP):
            outputFile.write(packet.getlayer(IP).src + '\n')

```

通常如果 NTP 服务器支持 MONLIST 请求，那么它将会返回多个数据包用于包含使用 NTP 服务的 IP 地址。因为 sniffer 会捕捉所有符合条件的数据包，所以 outputFile 文件中将会有许多重复的数据。我通过 sort 和 uniq 命令来对 outputFile 文件进行去重。

```
sort monlistServers.txt | uniq

```

这个结果文件中包含所有支持 MONLIST 命令的 NTP 服务器。

完整的 python 脚本如下：

```
from scapy.all import *
import thread
#Raw packet data used to request Monlist from NTP server
rawData = "\x17\x00\x03\x2a" + "\x00" * 61
#File containing all IP addresses with NTP port open.
logfile = open('output.txt', 'r')
#Output file used to store all monlist enabled servers
outputFile = open('monlistServers.txt', 'a')
def sniffer():
    #Sniffs incomming network traffic on UDP port 48769, all packets meeting thease requirements run through the analyser function.
    sniffedPacket = sniff(filter="udp port 48769 and dst net 99.99.99.99", store=0, prn=analyser)

def analyser(packet):
    #If the server responds to the GET_MONLIST command.
    if len(packet) > 200:
        if packet.haslayer(IP):
            print packet.getlayer(IP).src
            #Outputs the IP address to a log file.
            outputFile.write(packet.getlayer(IP).src + '\n')

thread.start_new_thread(sniffer, ())

for address in logfile:
    #Creates a UDP packet with NTP port 123 as the destination and the MON_GETLIST payload.
    send(IP(dst=address)/UDP(sport=48769, dport=123)/Raw(load=rawData))
print 'End'

```

0x02 最后
-------

* * *

正如我前面所提到的，我的带宽实在是太小了，所以我只能够选择一个 IP 段：101.0.0.0-120.0.0.0。如果我的数学不是体育老师教的话，那么我应该不会算错，这个 IP 段内包含 318,767,104 个 IP 地址（19_256_256）。

masscan 发现 253,994 个设备开放了 UDP 的 123 端口，占了扫描 IP 的 0.08%。

在 253,994 个设备中，支持 MONLIST 命令的设备有 7005 个，占比为 2.76%。

如果按照这个比例进行换算的话，那个整个互联网上将有 91,000 台开启 MONLIST 功能的 NTP 服务器。

over!