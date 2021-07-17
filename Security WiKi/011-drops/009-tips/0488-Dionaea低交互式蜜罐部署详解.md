# Dionaea低交互式蜜罐部署详解

0x00 Dionaea 低交互式蜜罐简介
---------------------

* * *

Dionaea(捕蝇草) 低交互式蜜罐(http://dionaea.carnivore.it) 是 Honeynet Project 的开源项目，起始于 Google Summer of Code 2009，是Nepenthes(猪笼草)项目的后继。Honeynet Project 是成立于 1999 年的国际性非盈利研究组织，致力于提高因特网的安全性，在蜜罐技术与互联网安全威胁研究领域具有较大的影响力。

Dionaea 蜜罐的设计目的是诱捕恶意攻击，获取恶意攻击会话与恶意代码程序样本。它通过模拟各种常见服务，捕获对服务的攻击数据，记录攻击源和目标IP、端口、协议类型等信息，以及完整的网络会话过程，自动分析其中可能包含的 shellcode 及其中的函数调用和下载文件，并获取恶意程序。

有别于高交互式蜜罐采用真实系统与服务诱捕恶意攻击，Dionaea 被设计成低交互式蜜罐，它为攻击者展示的所有攻击弱点和攻击对象都不是真正的产品系统，而是对各种系统及其提供的服务的模拟。这样设计的好处是安装和配置十分简单，蜜罐系统几乎没有安全风险，不足之处是不完善的模拟会降低数据捕获的能力，并容易被攻击者识别。

0x01 Dionaea 的整体结构和工作机制
-----------------------

* * *

Dionaea是运行于Linux上的一个应用程序，将程序运行于网络环境下，它开放Internet上常见服务的默认端口，当有外来连接时，模拟正常服务给予反馈，同时记录下出入网络数据流。网络数据流经由检测模块检测后按类别进行处理，如果有 shellcode 则进行仿真执行；程序会自动下载 shellcode 中指定下载或后续攻击命令指定下载的恶意文件。从捕获数据到下载恶意文件，整个流程的信息都被保存到数据库中，留待分析或提交到第三方分析机构。  
Dionaea 整体结构和工作机制如图：

![Dionaea-%E6%95%B4%E4%BD%93%E7%BB%93%E6%9](http://drops.javaweb.org/uploads/images/b0e00d3193887d00f2a773dc709ef586a8b340a6.jpg)

0x02 Dionaea 蜜罐安装过程
-------------------

* * *

Dionaea 目前版本是 0.1.0，采用源码安装。软件运行依赖于以下库：

```
libev，libglib，libssl，liblcfg，libemu，python，sqlite，readline，cython，lxml，libudns，libcurl，libpcap。 

```

安装过程详见[http://dionaea.carnivore.it/#compiling](http://dionaea.carnivore.it/#compiling)，需要注意的是安装 Python-3.2 时注意按说明修改 setup.py 以确保 zlib 库能正确安装。

安装时要注意依赖库成功安装，否则 Dionaea 可能不能正常工作。

### 安装详细过程:

OS：ubuntu 12.04 (32-bit)

```
# 安装依赖
apt-get update
apt-get install aptitude 
aptitude install libudns-dev libglib2.0-dev libssl-dev libcurl4-openssl-dev libreadline-dev libsqlite3-dev python-dev libtool automake autoconf build-essential subversion git-core flex bison pkg-config

```

其余的依赖，必须从源代码安装，我们将安装到路径/opt/dionaea，所以请确保该目录存在，并允许读写权限。

```
mkdir /opt/dionaea cd /opt/dionaea

```

### 安装其他依赖

liblcfg

```
git clone git://git.carnivore.it/liblcfg.git liblcfg
cd liblcfg/code
autoreconf -vi
./configure --prefix=/opt/dionaea
make install
cd ..
cd ..

```

libemu

```
git clone git://git.carnivore.it/libemu.git libemu
cd libemu
autoreconf -vi
./configure --prefix=/opt/dionaea
make install
cd ..

```

libnl

```
apt-get install libnl-3-dev libnl-genl-3-dev libnl-nf-3-dev libnl-route-3-dev

```

libev

```
wget http://dist.schmorp.de/libev/Attic/libev-4.04.tar.gz
tar xfz libev-4.04.tar.gz
cd libev-4.04
./configure --prefix=/opt/dionaea
make install
cd ..

```

Python 3.2

```
wget http://www.python.org/ftp/python/3.2.2/Python-3.2.2.tgz
tar xfz Python-3.2.2.tgz
cd Python-3.2.2/
./configure --enable-shared --prefix=/opt/dionaea --with-computed-gotos --enable-ipv6 LDFLAGS="-Wl,-rpath=/opt/dionaea/lib/ -L/usr/lib/i386-linux-gnu/"
make
make install
cd /opt/dionaea/bin
ln python3.2 /usr/bin/python3
cd ..

```

sqlite 3.3.7

```
wget http://www.sqlite.com.cn/Upfiles/source/sqlite-3.3.7.tar.gz
tar xzf sqlite-3.3.7.tar.gz
cd sqlite-3.3.7
mkdir /home/sqlite-3.3.7
./configure --prefix=/home/sqlite-3.3.7
make && make install && make doc
cd /home/sqlite-3.3.7/bin/
ln sqlite3 /usr/bin/sqlite3

```

Cython

```
wget http://cython.org/release/Cython-0.15.tar.gz
tar xfz Cython-0.15.tar.gz
cd Cython-0.15
/opt/dionaea/bin/python3 setup.py install
cd ..

```

libpcap

```
wget http://www.tcpdump.org/release/libpcap-1.1.1.tar.gz
tar xfz libpcap-1.1.1.tar.gz
cd libpcap-1.1.1
./configure --prefix=/opt/dionaea
make
make install
cd ..

```

编译安装dionaea

```
git clone git://git.carnivore.it/dionaea.git dionaea
cd dionaea
autoreconf -vi
./configure --with-lcfg-include=/opt/dionaea/include/ \
      --with-lcfg-lib=/opt/dionaea/lib/ \
      --with-python=/opt/dionaea/bin/python3.2 \
      --with-cython-dir=/opt/dionaea/bin \
      --with-udns-include=/opt/dionaea/include/ \
      --with-udns-lib=/opt/dionaea/lib/ \
      --with-emu-include=/opt/dionaea/include/ \
      --with-emu-lib=/opt/dionaea/lib/ \
      --with-gc-include=/usr/include/gc \
      --with-ev-include=/opt/dionaea/include \
      --with-ev-lib=/opt/dionaea/lib \
      --with-nl-include=/opt/dionaea/include \
      --with-nl-lib=/opt/dionaea/lib/ \
      --with-curl-config=/usr/bin/ \
      --with-pcap-include=/opt/dionaea/include \
      --with-pcap-lib=/opt/dionaea/lib/ 
make
make install

```

安装结束

0x03 Dionaea 使用方法
-----------------

* * *

Dionaea 根据命令参数运行，可选择不同的运行环境、任务和筛选事件记录内容。配置文件则具体规定蜜罐运行后开启的模块，记录文件的保存位置和扩展功能的参数等信息。默认配置下 Dionaea 自动选择一个网络接口进行监听。

Dionaea 具体的命令格式如下：

```
dionaea [-c, --config=FILE] [-D, --daemonize] [-g, --group=GROUP]
        [-G, --garbage=[collect|debug]] [-h, --help] [-H, --large-help]
        [-l, --log-levels=WHAT] [-L, --log-domains=WHAT] [-u, --user=USER]
        [-p, --pid-file=FILE] [-r, --chroot=DIR] [-V, --version] [-w, --workingdir=DIR]

```

选项的意义分别是：

```
-c：指定运行程序所使用的配置文件，默认下配置文件是/opt/dionaea/etc/dionaea.conf。  
-D：后台运行。  
-g：指定启动后切换到某个用户组，默认下保持当前组。  
-G：收集垃圾数据，用于调试内存泄露。不能用于 valgrind 软件。  
-h：帮助信息。  
-H：帮助信息，包括默认值信息。  
-l：选择事件记录级别，可以选择 all, debug, info, message, warning, critical, error 这些值，多选使用“,”做分隔，排除使用“-”。  
-L：选择域，支持通配符“*”和“?”，多选使用“,”，排除使用“-”。  
-u：指定启动后切换到某个用户，默认下保持当前用户。  
-p：记录 pid 到指定文件。  
-r：指定启动后切换根目录到指定目录，默认下不切换。  
-V：显示版本信息。  
-w：设定进程工作目录，默认下为/opt/dionaea。

```

例子:

切换到`cd /opt/dionaea/bin`

```
# ./dionaea -l all,-debug -L '*'
# ./dionaea -l all,-debug -L 'con*,py*'
# ./dionaea -u nobody -g nogroup -r /opt/dionaea/ -w /opt/dionaea -p /opt/dionaea/var/dionaea.pid

```

0x04 安装 DionaeaFR
-----------------

* * *

DionaeaFR([https://github.com/RootingPuntoEs/DionaeaFR](https://github.com/RootingPuntoEs/DionaeaFR))是用于前端web展示Dionaea的数据。

安装详细过程:

ubuntu 12.04 默认已安装 python 2.7.3

切换到cd /opt/，下载DionaeaFR

```
git clone https://github.com/RootingPuntoEs/DionaeaFR.git

```

安装pip，django，nodejs

```
apt-get install python-pip
pip install Django
pip install pygeoip
pip install django-pagination
pip install django-tables2
pip install django-compressor
pip install django-htmlmin
pip install django-filter

django-tables2-simplefilter:
    https://github.com/benjiec/django-tables2-simplefilter
    python setup.py install

SubnetTree:
    git clone git://git.bro-ids.org/pysubnettree.git
    python setup.py install

nodejs:
    http://nodejs.org/dist/v0.8.16/node-v0.8.16.tar.gz
    tar xzvf node-v0.8.16.tar.gz
    cd node-v0.8.16
    ./configure
    make
    make install

npm install -g less
apt-get install python-netaddr

```

下载GeoIP 和 GeoLiteCity

```
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz

```

解压GeoIP 和 GeoLiteCity

```
gunzip GeoLiteCity.dat.gz
gunzip GeoIP.dat.gz

```

移动GeoIP 和 GeoLiteCity到`/opt/DionaeaFR/DionaeaFR/static`

```
mv GeoIP.dat /opt/DionaeaFR/DionaeaFR/static
mv GeoLiteCity.dat /opt/DionaeaFR/DionaeaFR/static  

```

修改SQLite路径

```
cd /opt/DionaeaFR/DionaeaFR
vim settings.py

```

第17行，SQLite路径更改为

```
/opt/dionaea/var/dionaea/logsql.sqlite

```

如果你安装dionaea的目录不在/opt/，那就find下。

```
find / -name logsql.sqlite

```

把查找到的路径替换到17行中。

运行

```
cd /opt/DionaeaFR
python manage.py collectstatic python manage.py runserver 0.0.0.0:8000

```

浏览器访问：http://你的IP:8000

![DionaeaFR.png](http://drops.javaweb.org/uploads/images/b9eccd915f70a5fb82f10deb375822af0c5ee34c.jpg)

![DionaeaFR_ATTACKERS.png](http://drops.javaweb.org/uploads/images/b2a7dd36202badc8088fc92cfaa126500cc6a2cf.jpg)

0x05 结束
-------

* * *

低交互式蜜罐的普遍弱点，即对网络服务的模拟与真实服务存在差距，可能无法捕获某些对环境敏感的攻击，可以搭配其他专用服务蜜罐一起使用，来不断进行完善。

Kippo(SSH蜜罐开源软件)

Glastopf(Web应用攻击诱捕软件)

参考文档:

**本文基本上参考代恒，诸葛建伟前辈下面这2篇文章。**

[http://netsec.ccert.edu.cn/zhugejw/files/2011/09/Dionaea低交互式蜜罐介绍.pdf](http://netsec.ccert.edu.cn/zhugejw/files/2011/09/Dionaea%E4%BD%8E%E4%BA%A4%E4%BA%92%E5%BC%8F%E8%9C%9C%E7%BD%90%E4%BB%8B%E7%BB%8D.pdf)[http://netsec.ccert.edu.cn/zhugejw/files/2011/09/Dionaea低交互式蜜罐部署实践.pdf](http://netsec.ccert.edu.cn/zhugejw/files/2011/09/Dionaea%E4%BD%8E%E4%BA%A4%E4%BA%92%E5%BC%8F%E8%9C%9C%E7%BD%90%E9%83%A8%E7%BD%B2%E5%AE%9E%E8%B7%B5.pdf)