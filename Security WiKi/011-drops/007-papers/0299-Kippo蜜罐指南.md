# Kippo蜜罐指南

0x00 前言
=======

* * *

测试了一下kippo这个ssh蜜罐,算是一篇总结吧

0x01 测试环境
=========

* * *

```
CentOS release 6.2 (Final)
Linux www.centos.com 2.6.32-220.el6.x86_64 #1 SMP Tue Dec 6 19:48:22 GMT 2011 x86_64 x86_64 x86_64 GNU/Linux

```

0x02:搭建
=======

* * *

```
cd /home/
wget https://codeload.github.com/desaster/kippo/zip/master
unzip master
yum install twisted python-zope-interface python-pyasn1
mv kippo-master kippo
useradd kippo
chown -R kippo:kippo
cd kippo
cp kippo.cfg.dist kippo.cfg

```

监听本地的2222端口 提前修改正常ssh的端口,加一条防火墙规则,把22端口转到2222

```
iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-ports 2222

```

日志存放到数据库

```
yum install mysql mysql-server
/etc/init.d/mysqld start
mysql -uroot 
create database kippo;
GRANT ALL ON kippo.* to 'kippo'@'localhost' identified by 'kippo';

```

修改配置文件kippo.cfg

```
[database_mysql]
host = localhost
database = kippo
username = kippo
password = kippo
port = 3306


mysql -ukippo -p -Dkippo < /home/kippo/doc/sql/mysql.sql

```

安装python-mysql

```
yum -y install python-devel mysql-devel
wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
tar -zxvf setuptools-0.6c11.tar.gz
cd setuptools-0.6c11
python2.6 setup.py build
python2.6 setup.py install
wget https://pypi.python.org/packages/source/M/MySQL-python/MySQL-python-1.2.5.zip
Unzip MySQL-python-1.2.5.zip
Cd MySQL-python

```

修改site.cfg的mysql_config一行取消注释

```
mysql_config = /usr/lib64/mysql/mysql_config

python2.6 setup.py build
python2.6 setup.py install

```

0x03 图形化
========

* * *

```
yum install httpd php php-mysql php-gd php-curl

```

1.3的php版本要求高,要自己编译,还是用yum的,装个低版本的

```
wget http://bruteforce.gr/wp-content/uploads/kippo-graph-1.2.tar.gz
tar -zxf kippo-graph-1.2.tar.gz 
mv kippo-graph-1.2 /var/www/html/kippo
cd /var/www/html/kippo
cp config.php.dist config.php

vim config.php

```

写入内容

```
define('DIR_ROOT', '/var/www/html/kippo');  
define('DB_HOST', 'localhost');
define('DB_USER', 'kippo');
define('DB_PASS', 'kippo');
define('DB_NAME', 'kippo');
define('DB_PORT', '3306'); 

```

运行命令

```
chmod 777 /var/www/html/kippo/generated-graphs/
/etc/init.d/http start
su - kippo
./start.sh

```

访问http://ip/kippo

![enter image description here](http://drops.javaweb.org/uploads/images/333e882d8b54bc898d6a57f67e2ca15ffe230c73.jpg)

0x04 结构
=======

* * *

data: 存放ssh key,lastlog.txt和userdb.txt lastlog.txt:last命令的输出,即存储了登陆蜜罐的信息,也可以伪造 userdb.txt:可以登陆的用户,可以给一个用户设置多个密码,一个用户一行 格式为username:uid:password

honeyfs: etc目录中存在group hostname hosts issue passwd resolv.conf shadow这些 文件,cat /etc/filename目录中对应的文件时会显示这些文本文件中的内容. proc目录中存在cpuinfo meminfo version这些文件,cat /proc/filename目录中对应的文件时会显示这些文本文件中的内容.

log: 存放日志文件的地方,该目录包含一个kippo.log文件和tty目录 kippo.log:是存放启动记录,那些IP连接等信息 tty目录是每一个ssh过来后操作的记录,可以使用strings filename直接看到里面的内容

txtcmds: 存放命令的地方,这些命令都是文本文件,执行相关命令的时候直接显示文件内容

kippo: 核心文件,模拟一些交互式的命令等等

dl: wget等等下载的文件存放的地方

utils: convert32.py:把tty的日志转换为标准32位的小数格式,其实直接strings查看就可以了 createfs.py:可以用来模拟真实系统的一些文件目录之类的,不过需要设置一下

![enter image description here](http://drops.javaweb.org/uploads/images/82b97890faa634b71e791d77ce62f9b730b3bc36.jpg)

需要重定向保存输出,然后去替换fs.pickle文件,这样就可以模拟真实系统了.

fsctl.py:用来修改已经生成的fs.pickle的文件,help有命令的帮助

passdb.py:是来添加账户密码的,但是直接编辑data/userdb.txt就可以添加新的账户了,pass.db也没有找到在哪.........

playloh.py:对log/tty/下的日志进行回放的

0x05 配置文件
=========

* * *

```
kippo.cfg:
==========================================================
[honeypot]

# IP addresses to listen for incoming SSH connections.
#
# (default: 0.0.0.0) = any address
#ssh监听的地址,可以设置多个监听ip,每个ip之间用空格隔开
#ssh_addr = 0.0.0.0

# Port to listen for incoming SSH connections.
#
# (default: 2222)
#监听的端口,默认是2222,需要kippo运行在普通用户下,是不能够使用22端口,需要用iptables做一个简单的端口转发,转发到22端口
#只能监听一个端口
ssh_port = 2222

# Hostname for the honeypot. Displayed by the shell prompt of the virtual
# environment.
#
# (default: svr03)
#主机名
hostname = svr03

# Directory where to save log files in.
#
# (default: log)
#存放日志的路径
log_path = log

# Directory where to save downloaded (malware) files in.
#
# (default: dl)
#蜜罐中执行下载命令默认下载文件保存的目录
download_path = dl

# Maximum file size (in bytes) for downloaded files to be stored in 'download_path'.
# A value of 0 means no limit. If the file size is known to be too big from the start,
# the file will not be stored on disk at all.
#
#限制下载文件的大小,默认是0,不限制
# (default: 0)
#download_limit_size = 10485760

# Directory where virtual file contents are kept in.
#
# This is only used by commands like 'cat' to display the contents of files.
# Adding files here is not enough for them to appear in the honeypot - the
# actual virtual filesystem is kept in filesystem_file (see below)
#
# (default: honeyfs)
#配置文件的存放的地方,默认下面有etc和proc两个
contents_path = honeyfs

# File in the python pickle format containing the virtual filesystem.
#
# This includes the filenames, paths, permissions for the whole filesystem,
# but not the file contents. This is created by the createfs.py utility from
# a real template linux installation.
#
# (default: fs.pickle)
#记录一些文件,路径和权限的配置文件,用来模拟linux环境
filesystem_file = fs.pickle

# Directory for miscellaneous data files, such as the password database.
#
# (default: data_path)
#一些数据存放的地方,例如lastlog,ssh的key和允许登陆的账户和密码修改过的root密码
data_path = data

# Directory for creating simple commands that only output text.
#
# The command must be placed under this directory with the proper path, such
# as:
#   txtcmds/usr/bin/vi
# The contents of the file will be the output of the command when run inside
# the honeypot.
# In addition to this, the file must exist in the virtual
# filesystem {filesystem_file}
#
# (default: txtcmds)
#一些简单的命令,纯文字组成,只是用来做简单的输出
txtcmds_path = txtcmds

# Public and private SSH key files. If these don't exist, they are created
# automatically.
#ssh认证key存放的地方
rsa_public_key = data/ssh_host_rsa_key.pub
rsa_private_key = data/ssh_host_rsa_key
dsa_public_key = data/ssh_host_dsa_key.pub
dsa_private_key = data/ssh_host_dsa_key

# Enables passing commands using ssh execCommand
# e.g. ssh root@localhost <command>
#
# (default: false)
#是否支持 ssh root@localhost <command>这种命令的执行,默认是false的
exec_enabled = true

# IP address to bind to when opening outgoing connections. Used exclusively by
# the wget command.
#
# (default: not specified)
#ssh数据包发出去的地址
#out_addr = 0.0.0.0

# Sensor name use to identify this honeypot instance. Used by the database
# logging modules such as mysql.
#
# If not specified, the logging modules will instead use the IP address of the
# connection as the sensor name.
#
# (default: not specified)
#sensor_name=myhostname

# Fake address displayed as the address of the incoming connection.
# This doesn't affect logging, and is only used by honeypot commands such as
# 'w' and 'last'
#
# If not specified, the actual IP address is displayed instead (default
# behaviour).
#
# (default: not specified)
#fake_addr = 192.168.66.254

# SSH Version String
#
# Use this to disguise your honeypot from a simple SSH version scan
# frequent Examples: (found experimentally by scanning ISPs)
# SSH-2.0-OpenSSH_5.1p1 Debian-5
# SSH-1.99-OpenSSH_4.3
# SSH-1.99-OpenSSH_4.7
# SSH-1.99-Sun_SSH_1.1
# SSH-2.0-OpenSSH_4.2p1 Debian-7ubuntu3.1
# SSH-2.0-OpenSSH_4.3
# SSH-2.0-OpenSSH_4.6
# SSH-2.0-OpenSSH_5.1p1 Debian-5
# SSH-2.0-OpenSSH_5.1p1 FreeBSD-20080901
# SSH-2.0-OpenSSH_5.3p1 Debian-3ubuntu5
# SSH-2.0-OpenSSH_5.3p1 Debian-3ubuntu6
# SSH-2.0-OpenSSH_5.3p1 Debian-3ubuntu7
# SSH-2.0-OpenSSH_5.5p1 Debian-6
# SSH-2.0-OpenSSH_5.5p1 Debian-6+squeeze1
# SSH-2.0-OpenSSH_5.5p1 Debian-6+squeeze2
# SSH-2.0-OpenSSH_5.8p2_hpn13v11 FreeBSD-20110503
# SSH-2.0-OpenSSH_5.9p1 Debian-5ubuntu1
# SSH-2.0-OpenSSH_5.9
#
# (default: "SSH-2.0-OpenSSH_5.1p1 Debian-5")
#ssh的banner信息
ssh_version_string = SSH-2.0-OpenSSH_5.1p1 Debian-5

# Banner file to be displayed before the first login attempt.
#
# (default: not specified)
#第一次登陆上后,显示的banner信息,默认是不指定
#banner_file =

# Session management interface.
#
# This is a telnet based service that can be used to interact with active
# sessions. Disabled by default.
#
# (default: false)
interact_enabled = false
# (default: 5123)
interact_port = 5123


#mysql的支持模块,sql文件在doc/sql/mysql.sql
# MySQL logging module
#
# Database structure for this module is supplied in doc/sql/mysql.sql
#
# To enable this module, remove the comments below, including the
# [database_mysql] line.

#数据库的配置文件
#[database_mysql]
#host = localhost
#database = kippo
#username = kippo
#password = secret
#port = 3306

#XMPP 的日志文件
# XMPP Logging
#
# Log to an xmpp server.
# For a detailed explanation on how this works, see: <add url here>
#
# To enable this module, remove the comments below, including the
# [database_xmpp] line.

#[database_xmpp]
#server = sensors.carnivore.it
#user = anonymous@sensors.carnivore.it
#password = anonymous
#muc = dionaea.sensors.carnivore.it
#signal_createsession = kippo-events
#signal_connectionlost = kippo-events
#signal_loginfailed = kippo-events
#signal_loginsucceeded = kippo-events
#signal_command = kippo-events
#signal_clientversion = kippo-events
#debug=true

#默认日志以简单的文本方式存放
# Text based logging module
#
# While this is a database logging module, it actually just creates a simple
# text based log. This may not have much purpose, if you're fine with the
# default text based logs generated by kippo in log/
#
# To enable this module, remove the comments below, including the
# [database_textlog] line.

#[database_textlog]
#logfile = kippo-textlog.log

```

0x06 debug
==========

* * *

时间显示存在问题 使用了0时区的时间,这里是东8区

```
vim /home/kippo/kippo/core/dblog.py

```

写入

```
def nowUnix(self):
  """return the current UTC time as an UNIX timestamp"""
    #原系统用的时区是0时区的
    #return int(time.mktime(time.gmtime()[:-1] + (-1,)))
    #return int(time.mktime(time.gmtime()[:-1] + (-1,))) + 28800
    return int(time.time())

```

0x07 缺点
=======

* * *

1.  功能有限
    
2.  使用exit或者ctrl+d退出的时候是无法退出的,显示退出,其实还没有完全退出,需要强制的关闭终端,才能完全退出
    
3.  命令太少,对真实环境的模拟比较差
    
4.  添加用户这个过程,太复杂,还容易添加失败
    

0x08 后记
=======

* * *

“征用”了基友@太阳风的vps,放了半个月,以下是收集到的一些数据

![enter image description here](http://drops.javaweb.org/uploads/images/836abab7c33bbf8d087ad5adcc44f6f918cbf242.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/21b456ee3ccebe8a802f8a7a3d430fa03bb1252a.jpg)

有少量的恶意程序,收集到了少量的恶意程序,有兴趣的可以私信我啊~~~

最后给team的博客打个广告,大家手下留情........

```
http://www.sigma.ws/

```

参考:

http://bruteforce.gr/kippo-graph

http://www.google.com/