# NTP反射型DDos攻击FAQ/补遗

0x00 背景
-------

* * *

前两天，心伤的胖子发表了一篇[《浅谈基于 NTP 的反射和放大攻击》](http://drops.wooyun.org/papers/926)

我之所以又写一篇和NTP有关的文章，是因为前面有些东西没提，或说的不够清楚，浅陋之处，欢迎大家指正留言，我再求教改进。

名词解释:

> ntp server ：和原子钟同步同步，或以自己为标准时间的ntp服务器。
> 
> ntp relay server：在/etc/ntp.conf中配置顶级 服务器，以它们为权威ntp server 的时间中继服务器，也向其它ntp 服务器和终端用户提供时间同步功能。大多数机构和个人自行搭建的ntp server均属于这种。
> 
> ntp client :ntp 服务器之间，ntp服务器与终端用户之间有多种关联关系，其中一种为server /client 模式。所以，个人理解ntp client这个词相对而言的。

即当一台ntp 服务器（代号ABC）向权威/顶级 ntp server 同步时，此时的ABC的角色就是ntp client，当其响应下层ntp server的同步请求或响应终端用户的ntpdate请求时，ABC就是ntp server。

以上理解，如有谬误，请指正。

ntp服务器 关联关系（Association Modes ）参考：[http://doc.ntp.org/4.2.2/assoc.html](http://doc.ntp.org/4.2.2/assoc.html)

0x01 FAQ
--------

* * *

### 1. NTP Reply Flood Attack （NTP反射型DDos攻击） 影响的范围？

### 仅影响 ntp server 还是对 ntp client 也影响？

不论是ntp server 还是 ntp relay server 只要能响应monlist请求，其就应该能被利用发起NTP反射型DDos攻击。

也就是说，只要是没有加固的，低于 4.2.7p26 版本的 ntpd 服务（Linux平台）应该受到此漏洞影响。Windwos平台未测试。

个人为验证此问题，搭建了一台 ntp relay server做测试，其步骤也极为简单。

环境：RHEL6.2；ntpd 4.2.4p8。

```
1# yum install ntp -y 

2# vi /etc/ntp.conf 

server 0.rhel.pool.ntp.org //默认值**** 
restrict 10.10.20.0 mask 255.255.255.0 nomodify //允许同网段向此ntp relay server进行时间同步请求。 

3# service ntpd restart 

```

OK，搭建完成。

自己搭建的ntp relay server，测试结果如下。

```
#nmap -sU -pU:123 -n --script=ntp-monlist 10.10.10.200 

Nmap scan report for 10.10.10.200 
Host is up (0.00013s latency). 
PORT STATE SERVICE 
123/udp open ntp 
| ntp-monlist: 
| Target is synchronised with 218.75.4.130 
| Public Servers (2) 
| 97.107.134.213 218.75.4.130 
| Private Clients (1) 
| 10.10.10.210 
| Other Associations (2) 
| 10.10.10.180 (You?) seen 5 times. last tx was unicast v2 mode 7 
|_ 0:0:0:0:0:0:0:1 seen 775 times. last tx was unicast v2 mode 6 

MAC Address: 00:0C:29:E1:28:65 (VMware) 
Nmap done: 1 IP address (1 host up) scanned in 2.02 seconds 

```

### 2. 一些扫描器好像是根据NTP服务版本来判断此漏洞，且不分ntp server、ntp client端，可能误报率会比较高，哪位高人有解决办法？

个人理解，应该不必区分目标是 ntp server 还是 ntp client，因为所谓的 ntp server /client 应该均受影响。

国内某事业单位应急公告中的“未开启NTP Server服务或者只开启了NTP Client的情况不必进行任何处理；” 怀疑其对 ntp client 理解有误，或其ntp client指的不是运行了ntpd的服务器。理由请参考第一个回答。

### 3. monlist是什么东东？跟NTP反射型DDos攻击有何关系？

胖子的文章写得很清楚了，我就直接引用了：

NTP 包含一个 monlist 功能，也被成为 MON_GETLIST，主要用于监控 NTP 服务器，NTP 服务器响应 monlist 后就会返回与 NTP 服务器进行过时间同步的最后 600 个客户端的 IP，响应包按照每 6 个 IP 进行分割，最多有 100 个响应包。

可执行如下指令测试：

```
ntpdc -n -c monlist ntp_server-IP 

```

同 nmap 的脚本扫描是一致的。

```
nmap -sU -pU:123 -Pn -n --script=ntp-monlist NTP_Server_IP 

```

### 4. 相比加ACL防御的方式，NTP官方有更简单的缓解办法，把monlist功能关掉就好了

[http://support.ntp.org/bin/view/Main/SecurityNotice#DRDoS_Amplification_Attack_using](http://support.ntp.org/bin/view/Main/SecurityNotice#DRDoS_Amplification_Attack_using)

我倒是挺好奇升级是怎么解决这个问题的，把这个功能默认关掉？UDP也没法校验源地址啊。

monlist(monitor list)是有缺陷版本的ntpd服务的一个特性，其源代码为ntpdc.c，编译后的文件为/usr/sbin/ntpdc

```
strings /usr/sbin/ntpdc 

```

可在第833行 看到这个函数（ntpd 4.2.4p8 ）。

具体升级为什么能解决，请参考第五个问题。

### 5. 防止ntp server被利用进行DDOS攻击的方法？

缓解/防御措施有以下几种，详见参考链接中的英文原文。

1.  此漏洞在4.2.7以前版本均默认存在。所以将 NTP 服务器升级到 4.2.7p26或更高版本，当前最新版本为4.2.7p430。个人在ntpd 4.2.7p422测试通过。
2.  4.2.7以前版本，可在ntp.conf文件中增加`disable monitor`选项来禁用 monlist 功能。

也可以使用restrict ... noquery 或 restrict ... ignore 来限制ntpd服务响应的源地址。个人在ntpd 4.2.4p8测试通过。

缓解措施参考：

[https://www.us-cert.gov/ncas/alerts/TA14-013A](https://www.us-cert.gov/ncas/alerts/TA14-013A)

这个链接防御部分内容如下：

Recommended Course of Action  //美国 CERT 的说明

As all versions of ntpd prior to 4.2.7 are vulnerable by default, the simplest recommended course of action is to upgrade all versions of ntpd that are publically accessible to at least 4.2.7.

However, in cases where it is not possible to upgrade the version of the service, it is possible to disable the monitor functionality in earlier versions of the software.

To disable “monlist” functionality on a public-facing NTP server that cannot be updated to 4.2.7, add the “noquery” directive to the “restrict default” line in the system’s ntp.conf, as shown below:

restrict default kod nomodify notrap nopeer noquery restrict -6 default kod nomodify notrap nopeer noquery

Secure NTP Template //多种设备的此漏洞防御方法

[http://www.team-cymru.org/ReadingRoom/Templates/secure-ntp-template.html](http://www.team-cymru.org/ReadingRoom/Templates/secure-ntp-template.html)

0x02 综合参考
---------

* * *

[Understanding and mitigating NTP-based DDoS attacks](http://blog.cloudflare.com/understanding-and-mitigating-ntp-based-ddos-attacks)

《[NTP Reply Flood Attack （NTP反射型DDos攻击）原载黑防2011-06](http://blog.sina.com.cn/s/blog_459861630101b4wf.html)》Linxinsnow[N.N.U]

[《浅谈基于 NTP 的反射和放大攻击》](http://drops.wooyun.org/papers/926)