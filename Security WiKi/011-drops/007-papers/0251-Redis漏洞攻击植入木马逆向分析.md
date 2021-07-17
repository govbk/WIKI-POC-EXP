# Redis漏洞攻击植入木马逆向分析

作者：梦特（阿里云云盾安全攻防对抗团队）

0x00 背景
=======

* * *

2015年11月10日，阿里云安全团队捕获到黑客大规模利用Redis漏洞的行为，获取机器root权限，并植入木马进行控制，异地登录来自IP：104.219.xxx.xxx（异地登录会有报警）。由于该漏洞危害严重，因此阿里云安全团队在2015年11月11日，短信电话联系用户修复Redis高危漏洞，2015年11月14日，云盾系统检测到部分受该漏洞影响沦为肉鸡的机器进行DDOS攻击，发现后云盾系统已自动通知用户。

0x01 木马控制协议逆向分析
===============

* * *

分析发现木马作者，有2个控制协议未完成。

*   Connect协议有处理函数，但没有功能，函数地址为0x8048545。

![](http://drops.javaweb.org/uploads/images/aae1aab122a6b567fdedf30d71be71c4322d3325.jpg)

*   sniffsniff协议没有对应的处理函数，作者未实现该功能。
    
    完全逆向分析后得到控制协议如下表：
    

<table border="1" style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">协议</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">协议格式</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">分析描述</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">kill</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">kill</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">结束自身进程</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">dlexec</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">dlexec IP filepath port</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">在指定IP下载文件并执行</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">qweebotkiller</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">qweebotkiller</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">遍历进程PID为0到65535，查找对应文件，若匹配特征EXPORT %s:%s:%s，则删除文件</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">system</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">system cmdline</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">调用系统的/bin/sh执行shell脚本</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">connect</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">connect ips arg2 arg3 arg4</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">有处理函数，但作者把connect的功能给阉割了，并没有去实现connect协议的功能，因此我们只分析出协议1个参数的意议，另外3个参数不知道意义。</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">icmp</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">icmp IPs attacktime PacketLen</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">发动icmp协议攻击</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">tcp</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">tcp ips port attacktime flags packetlen</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">发动TCP的(fin,syn,rst,psh,ack,urg)DDOS攻击，攻击时间为秒。</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">udp</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">udp ips port attacktime packetlen</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">发动UDP攻击。</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">sniffsniff</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">sniffsniff</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">这个协议木马并没有实现功能。</td></tr></tbody></table>

*   协议完成逆向后，我们用Python写了一个控制端，并实现全部协议控制木马，如下图：
    
    ![](http://drops.javaweb.org/uploads/images/49d6a9f683121a1f2338b6963185f77e5bca2762.jpg)
    

0x02 木马概述
=========

* * *

从逆向得到的协议分析可以发现，该木马的功能主要包括：

*   发动DDoS攻击（ICMP、UDP、TCP）
*   远程执行命令
*   远程下载文件执行
*   清除其他后门文件

文件MD5：9101E2250ACFA8A53066C5FCB06F9848

进程操作
----

*   木马启动，木马接受1个参数，参数为要kill的进程PID。函数地址为0x8049C77.
    
    ![](http://drops.javaweb.org/uploads/images/a158176af1bf0ff3b4aed274650fc55741330279.jpg)
    
*   木马会启动一个孙子进程执行木马功能，然后当前进程退出。
    

文件操作
----

*   暴力关闭文件，关闭0到0xFFFF的文件，调用系统调用sys_close()，函数地址为0x8049C77。
    
    ![](http://drops.javaweb.org/uploads/images/a5674b849f3232ed2f87c29ecfcf9c7822f38517.jpg)
    
*   自我删除，调用系统调用`sys_readlink()`读取`/proc/self/exe`获取文件路径，`sys_unlink()`进行删除，处理函数地址为0x80494F3。
    
    ![](http://drops.javaweb.org/uploads/images/7f686d9842343b2b180e66bffb90e508812a4b1f.jpg)
    

网络操作
----

*   连接8.8.8.8的53端口，探测网络是否连接到Internet，处理函数地址为0x8049B90。
    
    ![](http://drops.javaweb.org/uploads/images/13ed65471a9fbcf60d400c0dba5b89778be2a89a.jpg)
    
*   连接木马控制端37.xxx.xxx.x的53端口，处理函数地址为0x8049C77。
    
    ![](http://drops.javaweb.org/uploads/images/41252429b8664c856271e05e496e747dbad748ea.jpg)