# Linux被DDOS&CC攻击解决实例

0x00 背景
-------

* * *

这两天一个客户反映自己的网站经常出现mysql 1040错误，他的在线用户才不到一千，mysql配置也没问题，vps用的时linode160+刀一个月的。

没理由出现这种情况，于是，我进行了一系列的排查。top了一下，mysqld跑到了900%多。

0x01 解决方案&思路
------------

* * *

我怀疑是CC攻击，鉴于系统是centos，我运行了下面的这两行命令。

```
netstat -anlp|grep 80|grep tcp|awk '{print $5}'|awk -F: '{print $1}'|sort|uniq -c|sort -nr|head -n20 | netstat -ant |awk '/:80/{split($5,ip,":");++A[ip[1]]}END{for(i in A) print A[i],i}' |sort -rn|head -n20 

```

把请求过多的IP记录下来。

```
174.127.94.*
199.27.128.*
199.27.133.*

```

开始封禁IP，具体可以看我下面运行的命令。本文主要是采用iptables进行封禁，iptables使用方法请见：[Iptables入门教程](http://drops.wooyun.org/tips/1424)

```
iptables -I INPUT -s 174.127.94.0/16 -j DROP
iptables -I INPUT -s 199.27.128.0/16 -j DROP
iptables -I INPUT -s 199.27.133.0/16 -j DROP
iptables -I INPUT -s 193.1.0.0/8 -j DROP 【慎用封禁整个段】

```

运行上面这些命令之后我们已经完成封禁操作了，不过还得保存一下，如果不保存的话重启系统之后上面设定的规则会消失。

```
service iptables save 

```

运行下面这行命令，来查看谁的访问量最高（需要服务器安装tcpdump）

```
tcpdump -i eth0 -tnn dst port 80 -c 1000 | awk -F"." '{print $1"."$2"."$3"."$4}' | sort | uniq -c | sort -nr |head -20 

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
1000 packets captured
1000 packets received by filter
0 packets dropped by kernel
1420 IP 174.7.7.*

```

然后将packets过多的IP记录下来，用上面的方法封禁。

运行

```
service iptables save 

```

保存然后重启 

```
iptables service iptables restart 

```

这一步建议多进行几次，发现异常IP用上面的办法封禁。如果出现误封可以参考下面这行解封命令进行解封

```
iptables -D INPUT -s 222.142.2.0/16 -j DROP

```

0x02 常用命令
---------

* * *

封单个IP的命令是：

```
iptables -I INPUT -s 211.1.0.0 -j DROP

```

封IP段的命令是：

```
iptables -I INPUT -s 211.1.0.0/16 -j DROP
iptables -I INPUT -s 211.2.0.0/16 -j DROP
iptables -I INPUT -s 211.3.0.0/16 -j DROP

```

封整个B段的命令是：

```
iptables -I INPUT -s 211.0.0.0/8 -j DROP

```

封几个段的命令是：

```
iptables -I INPUT -s 61.37.80.0/24 -j DROP
iptables -I INPUT -s 61.37.81.0/24 -j DROP

```

0x03 后续
-------

* * *

进行了上面的操作之后，客户的网站正常了，几乎秒开，当然这和他的vps给力也有一定的关系。top了一下，服务器资源也正常了。