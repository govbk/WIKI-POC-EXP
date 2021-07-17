# Rsync安全配置

### 0x00 Rsync简介

* * *

Rsync，remote synchronize顾名思意就知道它是一款实现远程同步功能的软件，它在同步文件的同时，可以保持原来文件的权限、时间、软硬链接等附加信息。

rsync是用 “rsync 算法”提供了一个客户机和远程文件服务器的文件同步的快速方法，而且可以通过ssh方式来传输文件，这样其保密性也非常好，另外它还是免费的软件。

rsync 包括如下的一些特性：

```
能更新整个目录和树和文件系统；
有选择性的保持符号链链、硬链接、文件属于、权限、设备以及时间等；
对于安装来说，无任何特殊权限要求；
对于多个文件来说，内部流水线减少文件等待的延时；
能用rsh、ssh 或直接端口做为传输入端口；
支持匿名rsync 同步文件，是理想的镜像工具；

```

### 0x01 架设Rsync服务器

* * *

安装Rsync与xinetd包

```
$ yum -y install xinetd rsync

```

确保xinetd运行在levels 3或4或5。

```
$ chkconfig --level 345 xinetd on

```

修改rsync xinetd配置文件，把`disable = yes`改成`disable = no`

```
$ vi /etc/xinetd.d/rsync

```

创建rsync的密码文件，格式`username:password`

```
$ vi /etc/rsyncd.secrets

```

创建rsync共享配置文件

```
$ vi /etc/rsyncd.conf

```

添加如下内容：

```
secrets file = /etc/rsyncd.secrets #密码文件位置，认证文件设置，设置用户名和密码
#motd file = /etc/rsyncd.motd #欢迎信息文件名称和存放位置（此文件没有，可以自行添加）
read only = no # yes只读 值为NO意思为可读可写模式，数据恢复用NO
list = yes
uid = nobody #以什么身份运行rsync
gid = nobody

[out]  #模块名
comment = Welcome #欢迎信息
path = /home/rsync/out #rsync同步的路径
auth users = rsync #授权帐号,认证的用户名，如果没有这行则表明是匿名，多个用户用,分隔。
hosts allow = X.X.X.X #允许访问的IP
auth users = username #/etc/rsyncd.secrets中的用户名

```

还有很多参数没有使用。

[http://www.samba.org/ftp/rsync/rsyncd.conf.html](http://www.samba.org/ftp/rsync/rsyncd.conf.html)里详细解释了rsyncd.conf各个参数的意思。

修改权限与所有权，重启xinetd服务：

```
$ chown root.root /etc/rsyncd.*
$ chmod 600 /etc/rsyncd.*
$ service xinetd restart

```

然后就可以通过如下命令访问了：

下载文件： ./rsync -vzrtopg --progress --deleteusername@xxx.xxx.xxx.xxx::out /home/test/getfile

上传文件： /usr/bin/rsync -vzrtopg --progress /home/test/getfileusername@xxx.xxx.xxx.xxx::out

Rsync 同步参数说明

```
-vzrtopg里的v是verbose，z是压缩，r是recursive，topg都是保持文件原有属性如属主、时间的参数。
--progress是指显示出详细的进度情况
--delete参数会把原有getfile目录下的文件删除以保持客户端和服务器端文件系统完全一致
username@xxx.xxx.xxx.xxx中的username是指定密码文件中的用户名,xxx为ip地址
out是指在rsyncd.conf里定义的模块名
/home/test/getfile 是指本地要备份目录

```

如果不想每次都再输入一次密码可以使用`--password-file`参数

```
/usr/bin/rsync -vzrtopg --progress /home/test/getfile  username@xxx.xxx.xxx.xxx::out --password-file=/test/rsyncd.secrets

```

本机上的/test/rsyncd.secrets文件里只需要保存密码即可，用户名已经在命令中有了，并且权限应为600。

### 0x02 匿名访问危害

* * *

wooyun出现不少没有限定任何ip并且允许匿名访问，而导致严重后果的实际案例：

[WooYun: 我是如何沦陷ChinaZ下载站服务器的，可登录3389、篡改源码等](http://www.wooyun.org/bugs/wooyun-2013-026232)

[WooYun: 新浪漏洞系列第三弹-微博内网遭入侵](http://www.wooyun.org/bugs/wooyun-2013-021589)

[WooYun: Discuz旗下5d6d某服务器Rsync任意文件上传](http://www.wooyun.org/bugs/wooyun-2012-010093)

### 0x03 寻找匿名访问Rsync方式

* * *

Rsync默认的端口是873，可以使用nmap扫描哪些ip开放了873端口。

```
nmap -n --open -p 873 X.X.X.X/24

```

找到开放的873端口后，连接能否查看模块名：

```
rsync X.X.X.X::

```

如果可以，就尝试上传，下载文件试一下。

### 0x04 安全配置注意事项

* * *

注意两种方式防御，一是限定访问的IP，另一个是不允许匿名访问，添加用户口令。

#### 限定IP的两种方式

IPTables防火墙

给rsync的端口添加一个iptables。

只希望能够从内部网络（192.168.101.0/24）访问：

```
iptables -A INPUT -i eth0 -p tcp -s 192.168.101.0/24 --dport 873 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -o eth0 -p tcp --sport 873 -m state --state ESTABLISHED -j ACCEPT

```

除此之外rsyncd.conf中的`hosts allow`也可以设置只允许来源ip。

```
hosts allow = X.X.X.X #允许访问的IP

```

#### 添加用户口令

添加rsync用户权限访问，注意配置的是rsyncd.conf中的：

```
secrets file = /etc/rsyncd.secrets #密码文件位置，认证文件设置，设置用户名和密码
auth users = rsync #授权帐号,认证的用户名，如果没有这行则表明是匿名，多个用户用,分隔。
```