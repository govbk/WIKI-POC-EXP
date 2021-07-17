# NMAP 基础教程

原文地址：http://infotechbits.wordpress.com/2014/05/04/introduction-to-basic-nmap/

0x00 nmap 介绍
------------

* * *

Nmap  （网络映射器）是由 Gordon Lyon设计，用来探测计算机网络上的主机和服务的一种安全扫描器。为了绘制网络拓扑图，Nmap的发送特制的数据包到目标主机，然后对返回数据包进行分析。Nmap是一款枚举和测试网络的强大工具。

Nmap 特点：

```
主机探测：探测网络上的主机，例如列出响应TCP和ICMP请求、icmp请求、开放特别端口的主机。 
端口扫描：探测目标主机所开放的端口。 
版本检测：探测目标主机的网络服务，判断其服务名称及版本号。 
系统检测：探测目标主机的操作系统及网络设备的硬件特性。 
支持探测脚本的编写：使用Nmap的脚本引擎（NSE）和Lua编程语言。

```

Nmap 能扫描出目标的详细信息包括、DNS反解、设备类型和mac地址。

(DNS 反解详情移步[http://www.debouncer.com/reverse-dns-check](http://www.debouncer.com/reverse-dns-check))

0x01 Nmap 典型用途：
---------------

* * *

```
1、通过对设备或者防火墙的探测来审计它的安全性。 
2、探测目标主机所开放的端口。 
3、网络存储，网络映射，维护和资产管理。（这个有待深入） 
4、通过识别新的服务器审计网络的安全性。 
5、探测网络上的主机。 

```

0x02 nmap 安装
------------

* * *

nmap可以到[http://nmap.org/download.html](http://nmap.org/download.html)下载最新版本

![2014051802083312402.png](http://drops.javaweb.org/uploads/images/49f28028329b3a3db564d0a83e17d87a1e26ab17.jpg)

Nmap 安装、根据提示向导，下一步、下一步进行安装。

![2014051802102488756.png](http://drops.javaweb.org/uploads/images/3ce9cb4ce464947f5870c23e9e6ae5991cab6cc8.jpg)

![2014051802103492666.png](http://drops.javaweb.org/uploads/images/14e71895b0e035971ef2fc8f660e337db12f1932.jpg)

![2014051802110354681.png](http://drops.javaweb.org/uploads/images/37495ad1c566be593369da1f3c29a665aca0b377.jpg)

![2014051802104432330.png](http://drops.javaweb.org/uploads/images/41e6954888b96a28d987fab3de651f1f8e07ee76.jpg)

进入命令提示符（cmd），输入nmap，可以看到nmap的帮助信息，说明安装成功。

![2014051802121466655.png](http://drops.javaweb.org/uploads/images/1f4306f1f1a7201892efcded386fd8e18b194ecd.jpg)

0x03 nmap 命令操作
--------------

* * *

注意：请自己通过各种设备来搭建模拟实际的网络环境（如虚拟机，手机等设备），请在道德和法律的允许下进行测试。不然你懂的。

### 1、Nmap 简单扫描

Nmap 默认发送一个arp的ping数据包，来探测目标主机在1-10000范围内所开放的端口。

命令语法：

```
nmap <target ip address> 

```

解释：Target ip address 为你目标主机的ip地址

例子：

```
nmap 10.1.1.254

```

效果：

![2014051802164891565.png](http://drops.javaweb.org/uploads/images/a73a4496bc5213dadfff35c02af7eb70a33fc6ab.jpg)

### 2、Nmap 简单扫描，并对返回的结果详细描述输出。

命令语法：

```
nmap -vv 10.1.1.254 

```

介绍：-vv 参数设置对结果的详细输出。

例子：

```
nmap -vv 10.1.1.254  

```

效果：

![2014051802190267121.png](http://drops.javaweb.org/uploads/images/bc8f6c370ea7ffb54cc27b4214f605c31d9c7b89.jpg)

### 3、nmap 自定义扫描

nmap 默认扫描目标1-10000范围内的端口号。我们则可以通过参数-p 来设置我们将要扫描的端口号。

命令语法：

```
nmap -p(range) <target IP>  

```

解释：（rangge）为要扫描的端口（范围），端口大小不能超过65535，Target ip  为目标ip地址

例子：扫描目标主机1-50号端口：

效果：

![2014051802212052726.png](http://drops.javaweb.org/uploads/images/155fcef2e48ace62e33a3c5cfb54d660a8e40fb2.jpg)

例子：扫描目标主机1-100号端口：

效果：

![2014051802222245147.png](http://drops.javaweb.org/uploads/images/b07265f3e509f61e2a04fae382f5fac9cd78454f.jpg)

例子：扫描目标主机50-500号端口：

效果：

![2014051802225999391.png](http://drops.javaweb.org/uploads/images/ad536d17c898f51a03f873bb7339e97efcda60ae.jpg)

### 4、nmap 指定端口扫描

有时不想对所有端口进行探测，只想对80,443,1000,65534这几个特殊的端口进行扫描，我们还可以利用参数p 进行配置。

命令语法：

```
nmap -p(port1,port2,port3,...) <target ip> 

```

例子：

```
nmap -p80,443,22,21,8080,25,53 10.1.1.254  

```

效果：

![2014051802253110893.png](http://drops.javaweb.org/uploads/images/daf577f07e9feb67297222d762bad80445e0e72f.jpg)

### 5、nmap ping 扫描

nmap 可以利用类似window/linux 系统下的ping方式进行扫描。

命令语法：

```
nmap -sP <target ip> 

```

解释：sP 设置扫描方式为ping扫描

例子：

```
nmap -sP 10.1.1.254 

```

效果：

![2014051802273675033.png](http://drops.javaweb.org/uploads/images/a53440ec3cc79aa16283b9450529bf1cc6977406.jpg)

6、nmap 路由跟踪

路由器追踪功能，能够帮网络管理员了解网络通行情况，同时也是网络管理人员很好的辅助工具！通过路由器追踪可以轻松的查处从我们电脑所在地到目标地之间所经常的网络节点，并可以看到通过各个节点所花费的时间（百度百科）

命令语法:

```
nmap --traceroute <target ip> 

```

例子：

```
nmap --traceroute 8.8.8.8 (google dns服务器ip)  

```

效果：

![2014051802292010676.png](http://drops.javaweb.org/uploads/images/f2818e5fd67dd88b1a67277f7bd150c48debd52f.jpg)

### 7、nmap 还可以设置扫描一个网段下的ip

命令语法：

```
nmap -sP <network address > </CIDR >  

```

解释：CIDR 为你设置的子网掩码(/24 , /16 ,/8 等)

例子：

```
nmap -sP 10.1.1.0 /24  

```

效果：

![2014051802324658402.png](http://drops.javaweb.org/uploads/images/984bb4a194cc27450a26b5d360f5cbb54887c7e1.jpg)

例子：

```
nmap -sP 10.1.1.1-255  

```

效果:

![2014051802333142828.png](http://drops.javaweb.org/uploads/images/3d8b76c1aabace30f132829a502d953d7c88ca99.jpg)

上面两个都是扫描10.1.1.0/24 网络段的主机

其中

Windown:10.1.1.103

![2014051802345754384.png](http://drops.javaweb.org/uploads/images/f2fc2e0699e13ec515311120062cd9e5a4d34145.jpg)

Android:10.1.1.101

![2014051802352761422.png](http://drops.javaweb.org/uploads/images/aa375884cfbfa1d00e31b309bbeb9d54bc739bda.jpg)

### 8、nmap 操作系统类型的探测

nmap 通过目标开放的端口来探测主机所运行的操作系统类型。这是信息收集中很重要的一步，它可以帮助你找到特定操作系统上的含有漏洞的的服务。

命令语法：

```
nmap -O <target ip> 

```

例子：

```
nmap -O 10.1.1.254   

```

效果：

![2014051802371530835.png](http://drops.javaweb.org/uploads/images/e2a47f3117e31c54d394ef5a88f3cccdc99edbcc.jpg)

例子：

```
nmap -O 10.1.1.101 （扫描android手机）  

```

效果：

![2014051802380381069.png](http://drops.javaweb.org/uploads/images/6b9d073d82caad230d923937bcca195118459ab5.jpg)

Nmap 默认不能扫描本机，如果你想扫描你的电脑，你可以通过虚拟机来进行扫描。

例子：

```
nmap -O 10.1.1.103（Windows 7 SP2 Home Premium ）

```

效果：

![2014051802401014634.png](http://drops.javaweb.org/uploads/images/0bdcb3a7cc8f2a43d4c6a27f09188e4f9ea2eb2c.jpg)

### 9、nmap 万能开关

次选项设置包含了1-10000的端口ping扫描，操作系统扫描，脚本扫描，路由跟踪，服务探测。

命令语法：

```
nmap -A <target ip>  

```

例子：

```
nmap -A 10.1.1.254 

```

效果：

![2014051802423388389.png](http://drops.javaweb.org/uploads/images/c46e505968493487035e5330d398cd03e8e941e2.jpg)

### 10、nmap 命令混合式扫描

命令混合扫描，可以做到类似参数-A所完成的功能，但又能细化到我们所需特殊要求。

命令语法：

```
nmap -vv -p1-1000 -O <target ip>  

```

例子：

```
nmap -vv -p1-1000 -O 10.1.1.105 

```

效果：

![2014051802444951776.png](http://drops.javaweb.org/uploads/images/2d68cad0113fbc3fc46ff9ac4e305a6eb5fbcfdc.jpg)

例子:对目标主机的80,8080,22,23端口进行扫描，并且对目标进行路由跟踪和操作系统探测。

```
nmap -p80,8080,22,23 -traceroute -O 10.1.1.254 

```

效果：

![2014051802473156938.png](http://drops.javaweb.org/uploads/images/558a09b9a750da4eb98a09138d218dda8a40480d.jpg)

Nmap提供的这些参数，可根据自己的需求，灵活的组合使用。

由于个人水平有限，如有错误欢迎指出。