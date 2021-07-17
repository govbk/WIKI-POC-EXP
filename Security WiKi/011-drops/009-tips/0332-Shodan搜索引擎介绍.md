# Shodan搜索引擎介绍

from:http://www.exploit-db.com/wp-content/themes/exploit/docs/33859.pdf

* * *

0x00 概要
-------

* * *

这篇文章可以作为渗透测试人员和安全工作者运用Shodan搜索引擎的指南，同时有助于理解其工作原理和达到安全审计目的。文章也列举出找到大量有风险的互联网服务及其设备的步骤和方法。同时介绍了Shodan能用初级筛选语法以及Shodan和其他工具的联合运用。主要适用于渗透测试的数据收集阶段。

0x01 介绍
-------

* * *

Shoudan是一个用于帮助发现主要的互联网系统漏洞（包括路由器，交换机，工控系统等）的搜索引擎。它在圈子里就像google一样出名。它主要拦截从服务器到客户端的元数据来工作，目前提供超过50个端口的相关搜索。

Shodan能找到的设备：

```
1.服务器
2.路由器
3.交换机
4.公共ip的打印机
5.网络摄像头
6.加油站的泵
7.Voip电话和所有数据采集监控系统

```

Shodan能做的：

```
1.用户搜索制定的项目
2.Shodan寻找端口并拦截数据
3.Shodan为拦截的数据设置索引
4.显示结果

```

Shodan和google的区别：

```
Google的爬虫/蜘蛛 抓取网页数据并为网页内容创建索引，然后更具page rank显示结果。Shoudan主要寻找端口并抓取拦截到的信息，然后为它们建立索引，最后显示结果。Shoudan并不像google那样为网页内容建立索引，因此它是一个基于拦截器的搜索引擎。

```

0x02 基础用法
---------

* * *

City：用于寻找位于指定城市的设备。例：

```
iis city:New York 

```

County：用于寻找位于指定国家的设备。例：

```
iis country: United States  

```

Port：限定指定的端口。例：

```
https port:443 

```

Os：用于寻找特定的操作系统。例：

```
microsoft-iis os:"windows 2003"

```

Geo：根据经纬度和指定的半径来返回结果。只能有2个或3个参数，第三个参数是半径，默认数值之5km。例：

```
 apache geo:42.9693,-74.1224

```

Net：用于寻找指定ip地址和子网掩码的设备。例：

```
 iis net:216.0.0.0/16 

```

Hostname：用于搜索包含指定域名的主机。例：

```
Akamai  hostname:.com

```

After and Before: 帮助找到指定日期范围的设备。格式：dd/mm/yyyy dd-mm-yy 例：

```
apache before:1/01/2014       
nginx after:1/01/2014  

```

注意：登陆后大多数参数都能运作。

0x03 Shodan和其他工具的结合
-------------------

* * *

### 1.和Maltego的结合

需要：[从http://www.paterva.com/web6/products/download.php](http://xn--http-z25f//www.paterva.com/web6/products/download.php)下载Matlego。

从[https://static.Shodan.io/downloads/Shodan-maltego-entities.mtz](https://static.shodan.io/downloads/Shodan-maltego-entities.mtz)

下载Shodan的matlego目录

用法：

```
1.安装maltego之后，选择‘Manage tab’里的 ‘Manage Entities’ ，然后选择‘import’。
2.选择 ‘transforms’ 然后是‘advanced’  

```

![enter image description here](http://drops.javaweb.org/uploads/images/11656fa07d9defb87c9787191e353d7e1d6dae31.jpg)

```
3.现在可以添加Shodan的链接https://cetas.paterva.com/TDS/runner/showseed/Shodan  

```

![enter image description here](http://drops.javaweb.org/uploads/images/a047ba5e0895800f3cfab506a27a3eb73c44b60e.jpg)

```
4.最后我们可以看到安装成功的窗口

```

![enter image description here](http://drops.javaweb.org/uploads/images/f73f596ec348195b9d4c926a4878e18d257cf7ba.jpg)

注意：需要你有Shodan的API keys，可以在maltgo进行Shodan的使用，API keys在你登陆Shodan账户时候是可以获得的。

### 2.和metasploit的结合

用法：

```
1.在Kail/Backtrack Box中打开Metasploit framework

```

![enter image description here](http://drops.javaweb.org/uploads/images/1b8ce33f839433011cb2ca0dc5ca3437794fa006.jpg)

```
2.在命令行中输入show auxiliary

```

![enter image description here](http://drops.javaweb.org/uploads/images/33cd7f1ffa53b99d6e985f3b88ce557adca53f15.jpg)

```
3.使用 auxiliary/gather/Shodansearch 模块

```

![enter image description here](http://drops.javaweb.org/uploads/images/f3499db57fdba45be4f280658e3aa6ea3e372cff.jpg)

```
4.现在，你可以用show options命令来查看模块需要的参数

```

![enter image description here](http://drops.javaweb.org/uploads/images/1b005d483dd056366dc54246bc02f3e35f099a70.jpg)

```
5.我们需要指定iis来搜索iis服务器，还需要登陆Shodan账户后得到的API key。现在我们可以用Run command 来执行命令。

```

![enter image description here](http://drops.javaweb.org/uploads/images/21d15ca26fcbc31cd67de712ead288bb5832473b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c88b6badbdfd3a9aceaedbee7c92c9e78402cc65.jpg)

一般来说 auxiliary/gather/Shodan_search模块通过API向数据库查询前50个ip 地址。50个ip地址的限制可以通过购买无限制API key来扩大到查询10000个ip地址

0x04 Shodan的组件
--------------

* * *

1.Exploits：Shodan Exploits 能够用于在ExploitDB 或Metasploit寻找针对不同系统、服务器、平台、应用的的exploits。

![enter image description here](http://drops.javaweb.org/uploads/images/4f49fc0c14d3da7f4421c102bb0eaaf636aa757c.jpg)

2.Maps：这是个付费功能，我们能在地图上直观地看到Shodan提供的结果。提供三种视图：卫星，街景（浅），街景（深）。可以同时在屏幕展示超过1000个结果。

![enter image description here](http://drops.javaweb.org/uploads/images/c23958e2e7df6c823b3555ab5a54a5197b24ad21.jpg)

3.)Scanhub：Shodan Scanhubs可以用于创建陌生网络的搜索，它支持Nmap 和 Masscan类似的工具。要使用Scanhub，我们首先要设置好工具，输出一个XML格式的文件并上传到Scanhub的库里以获得结果。不幸的是这也是一个付费功能。

0x05 一些测试的例子
------------

* * *

### 1. Netgear设备

![enter image description here](http://drops.javaweb.org/uploads/images/e432a192860125e8556b75a79ca299dea14b8459.jpg)

### 2. 网络摄像头

![enter link description here](http://drops.javaweb.org/uploads/images/534f3fc98ca4f19444f588c7c4a3f4bdd0fd7006.jpg)

### 3. 比特币服务器

![enter image description here](http://drops.javaweb.org/uploads/images/760398b4bb0284200b24dbe4afb28d8ada9a902e.jpg)

### 4. Ruby on Rails Vulnerable Server(CVE-2013-0156 and CVE-2013-0155)

![enter image description here](http://drops.javaweb.org/uploads/images/f45c3b5a3b2b4a92a02172141c3f318f6b676bcd.jpg)

### 5. Windfarms:

![enter image description here](http://drops.javaweb.org/uploads/images/29b8d56be6036b05a65561760a396c9f61d4f018.jpg)

### 6. DNS 服务:

![enter image description here](http://drops.javaweb.org/uploads/images/c1d4d9b7ac6da40a4237162e3d52fb5594065211.jpg)

0x06 一些另外的cheat sheet 链接
------------------------

* * *

http://www.Shodanhq.com/?q=bitcoin-mining-proxy (Bitcoin proxy mining) http://www.Shodanhq.com/search?q=port%3A11 (Systat) http://www.Shodanhq.com/search?q=port%3A8089+splunkd (Splunk servers on tcp/8089) http://www.Shodanhq.com/search?q=port%3A17(Search for quote of the day) http://www.Shodanhq.com/search?q=port%3A123(Ntp monlist) http://www.Shodanhq.com/search?q=port%3A5632 (Vnc) http://www.Shodanhq.com/search?q=port%3A1434 ((MS-SQL (1434)) http://www.Shodanhq.com/search?q=OpenSSL%2F1.0.1 (Servers running OpenSSL/1.0.1) http://www.Shodanhq.com/search?q=port%3A79 (Finger protocol) http://www.Shodanhq.com/search?q=port%3A15 (Netstat) http://www.Shodanhq.com/?q=telemetry+gateway (Telemetry gateway)  
http://www.Shodanhq.com/?q=port:161+country:US+simatic (Simatic automation system o 161 running in US)