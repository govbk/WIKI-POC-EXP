# 解读“重定向SMB”攻击

前几天Cylance发布了一个影响Windows系统的漏洞，攻击者可以通过重定向到SMB协议的方式，利用“中间人攻击”来盗取用户认证信息。这个攻击究竟是怎么回事？“重定向SMB”又是什么呢？电脑管家漏洞防御团队对这些问题做了详细的技术分析，现将分析结果分享给大家。

0x01 SMB/SMB2(Server Message Block)
===================================

* * *

先简单介绍一下这次事件的主角SMB。

SMB是对CIFS(Common Internet File System)协议的扩展，主要用于访问网络上的共享文件以及打印服务。SMB和其它协议的关系如下：

![enter image description here](http://drops.javaweb.org/uploads/images/bbb7a071c8a50d53fc3278a30ac945691a0050b6.jpg)

SMB可以直接使用TCP端口进行传输(端口445)，也可以使用NetBIOS进行传输(TCP端口139)。以直接TCP端口传输为例，每一条SMB消息必须有一个4字节的包头。包头第一个字节为0（network byte order，下同），紧跟着的3字节表示SMB消息的长度；包体是变长的。

![enter image description here](http://drops.javaweb.org/uploads/images/f701d992e19e3c39fcda17db6ade0a06a219340c.jpg)

在windows vista以后，引入了SMB2协议，在原有的SMB协议基础上扩展了部分字段。

SMB/SMB2认证有多种协议，使用最多的就是NTLM认证协议。

NTLM支持 Challenge/Response方式进行加密通信，安全认证的消息序列如下：

![enter image description here](http://drops.javaweb.org/uploads/images/b6748292aec6a2e9740470c9248aac82d480c348.jpg)

0x02 利用HTTP重定向到SMB协议
====================

* * *

以Win7x86+IE11为例，看看IE如何处理HTTP返回的重定向请求。

![enter image description here](http://drops.javaweb.org/uploads/images/dd11ef4ed051abfe48fcb9046a72145a6525c717.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/72dd363f59ca5162b6de93d9efe77bfbb67844e7.jpg)

IE获得HTTP请求返回的状态码后，如果是代表重定向的301、302、303、307，跳转到处理重定向的逻辑，调用CINetHttp::RedirectRequest处理重定向请求。

构造一个重定向到file协议的网页

![enter image description here](http://drops.javaweb.org/uploads/images/5bcf5e8f96f95e93d213f1b1fb317e84b62282b6.jpg)

当IE访问这个网页时，可以抓到访问SMB服务器的数据包

![enter image description here](http://drops.javaweb.org/uploads/images/760dc764e6b73e2d9a97d4759a6f50be8d629ae3.jpg)

可见本机当前用户的登录凭证通过SMB2协议发送服务器进行认证了。如果这个服务器（上图中的10.4.75.32）是被恶意劫持过的“中间人”，那么用户的登录凭证就泄漏了。

可能的攻击方式不局限于网页访问，只要能够劫持正常的HTTP网络请求，就可以重定向到SMB协议将个人信息发送到恶意服务器上。

0x03 防范建议
=========

* * *

可以看到，重定向到SMB协议是一个很大的隐患，非用户主动发起的SMB请求都应该禁止；通过SMB协议访问外网共享服务器时也需要特别谨慎。

作为防范建议，可以关闭对TCP 139和445端口的访问。如果确实需要访问网络上的共享文件或者是打印服务，在确认服务器可信的前提下，临时打开TCP 139和445的端口访问。