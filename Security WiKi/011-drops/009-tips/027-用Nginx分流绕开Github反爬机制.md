# 用Nginx分流绕开Github反爬机制

0x00 前言
=======

* * *

如果哪天有hacker进入到了公司内网为所欲为，你一定激动地以为这是一次蓄谋已久的APT，事实上，还有可能只是某位粗线条的员工把VPN信息泄露在了Github上恰巧被一个好奇的计算机junior发现了而已。

0x01 意识缺失
=========

* * *

先贴张图：

![p1](http://drops.javaweb.org/uploads/images/f8dddff57881d375d60b8d740ccc3b47973838e7.jpg)

> 有记者给溧阳卫生局局长拨通电话，该局长面对记者的采访慌张答道：  
> “你看到我们发微博的啊？呵呵，你怎么看到的啊？这个都能看得到啊？！这不可能吧？我们两个发微博你都能看得到啊？不可能吧？”……

同样，互联网企业的员工流动性很强，各自的安全（隐私）意识也参差补齐。庞大的企业难免有些人由于无知或由于偷懒把含有敏感信息（如数据库连接串，邮箱账号，VPN信息）的代码直接丢到github上去。如果这些信息被有心人看到了，那就能让黑客花最小的成本，达到APT的效果了。

另附一篇漏洞盒子关于github泄露企业机密信息的报告：  
[https://www.vulbox.com/news/detail-15](https://www.vulbox.com/news/detail-15)

0x02 反爬机制
=========

* * *

于是，我们想实现github代码的监控，定制诸多关键词如password，mysql，account，email，希望通过爬虫程序来实现对github上敏感代码的监控，如果有可疑信息泄露，程序通过邮件通知负责人，负责人去进行二次人工审核。这样，能在第一时间发现敏感代码的泄露，并及时联系提交者进行处理。

期望是美好的，但是在连续高频访问若干次github.com之后：

![p2](http://drops.javaweb.org/uploads/images/c907a7653beec50b9424dce0b83e7c75c254d026.jpg)

触发了github的反爬机制，难道项目要流产？

0x03 绕开
=======

* * *

机智的楼主想起之前团队购买了5台阿里云机器，何不用阿里云机器搭建一套代理实现分IP访问绕开反爬机制？

于是就有了下图。

![p3](http://drops.javaweb.org/uploads/images/ca6bdede337b6917c367bbca915a37a003859e55.jpg)

一次敏感代码爬取的流程：

1.  Github爬虫引擎发起一次爬虫请求
2.  请求发送到负载均衡Nginx，Nginx将请求按照同权重的方式转发到流量转发Nginx
    
    **注：负载均衡Nginx设置为两台，防止出现单点故障。**
    
3.  收到负载均衡Nginx发过来的流量，流量转发Nginx将请求转想github.com
    
4.  github.com返回的内容通过Nginx原路返回给Github爬虫引擎
    

这样，对于github.com而言，他看到的是三台机器在一样频率的交替访问，频率是原先的1/3，巧的是，这个频率就不会触发反爬机制。从而实现了Github爬虫引擎的连续访问，效率大大提升。

同时，这套方案的扩展性还很强，如果再次被github.com反爬机制封锁，可以通过平行加流量转发Nginx机器的方式来实现水平扩展。

附负载均衡Nginx的核心配置：

![p4](http://drops.javaweb.org/uploads/images/34a1ea4a338fac4233ea21378a7d924f03ee6be9.jpg)

附流量转发Nginx的核心配置：

![p5](http://drops.javaweb.org/uploads/images/a97bc5336ae70116f999fffcd9bc4dbc2c94af83.jpg)