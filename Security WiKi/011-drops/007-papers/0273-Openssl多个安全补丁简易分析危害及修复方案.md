# Openssl多个安全补丁简易分析危害及修复方案

0x00 概述
-------

* * *

心脏出血（CVE-2014-0160）后，Openssl 拿出专项资金进行了代码审计，于6月5号晚发布了所发现的漏洞公告。

[https://www.openssl.org/news/secadv_20140605.txt](https://www.openssl.org/news/secadv_20140605.txt)

总结如图：

![enter image description here](http://drops.javaweb.org/uploads/images/f4455bb549ee0a0ac1071761fafaad76b5ad65ae.jpg)

两个高危漏洞`2014-0224中间人攻击（截获明文） 和2014-0195（DTLS 特定包代码执行）`3个拒绝服务 1个缓存区注入 1个特殊漏洞

0x01 详情
-------

* * *

### 1. CVE-2014-0224 ChangeCipherSpec 注入

漏洞作者：KIKUCHI Masashi

#### 漏洞原理

![enter image description here](http://drops.javaweb.org/uploads/images/1a7b44d9c5ae3db19dfe17cca6f886c0ebc03275.jpg)

按照TLS的协议 在固定的时间顺序内服务端发送和接收ChangeCipherSpec（更改密钥规格）数据，但是实际上openssl的实现：

服务端在发送时是按照时间线的顺序发送，接收时却没有检查顺序，导致攻击者可以构造伪造的ChangeCipherSpec（比如使用空的主密钥），导致可以中间人攻击解密两端加密信息。

更多详情：[http://ccsinjection.lepidum.co.jp/blog/2014-06-05/CCS-Injection-en/index.html](http://ccsinjection.lepidum.co.jp/blog/2014-06-05/CCS-Injection-en/index.html)

#### Poc

[https://gist.github.com/rcvalle/71f4b027d61a78c42607](https://gist.github.com/rcvalle/71f4b027d61a78c42607)[https://gist.github.com/rcvalle/585e12e4d5d3b658cd3d#](https://gist.github.com/rcvalle/585e12e4d5d3b658cd3d#)

#### 影响版本：

客户端所有版本都存在。服务端已知的受影响版本OpenSSL 1.0.1 和1.0.2-beta1.

漏洞产生必须客户端和服务端都使用了受影响版本的openssl。

### 2. CVE-2014-0195 DTLS碎包代码执行

漏洞作者:Jüri Aedla(Pwn2Own的火狐溢出执行获胜者)

#### 漏洞原理：

为了避免被IP分片，在DTLS存在一个数据包处理机制：

对所有大的UDP包进行分割，每个分割后的DTLS片段有三个标志字段:

```
总消息长度
帧偏移量
帧大小长度

```

每个DTLS分包后的总消息长度是固定不变的。

OPENSSL把每个收到的DTLS包判断（帧大小长度<总的长度）就会把这段长度的数据复制到缓冲区。

Openssl出错的地方就是：他认为所有DTLS包的总消息长度都是固定不变的。并没有检查总消息长度是否一致

所有攻击者可构造第一个包：

```
总长度 10
分包长度 2

```

第二个包

```
总长度 1000
分包长度900

```

由于长度字段占用3个字节，理论上可以写入（2^8）^3数据，再利用上下文执行命令。

OPENSSL在后面做了一些长度的代码检查但是前面已经执行。

More:[http://h30499.www3.hp.com/t5/HP-Security-Research-Blog/ZDI-14-173-CVE-2014-0195-OpenSSL-DTLS-Fragment-Out-of-Bounds/ba-p/6501002#.U5FqnvmSyD4](http://h30499.www3.hp.com/t5/HP-Security-Research-Blog/ZDI-14-173-CVE-2014-0195-OpenSSL-DTLS-Fragment-Out-of-Bounds/ba-p/6501002#.U5FqnvmSyD4)

受影响范围：

```
只有使用到DTLS的应用才会受影响。
包括但不限于：
VPN(openVPN)
VoIP
WebRTC  按照我之前对某些应用的研究很多app使用了这个。包括某 用户量最大的app 视频通信基于这个做的。
SSL的LDAP
SNMPv3
基于SSL的视频 音频

```

（你们只用zmap扫端口是不是太局限了）

### 3. DOS

#### CVE-2014-0221&&CVE-2014-0198&&CVE-2010-5298

CVE-2014-0221

原理

```
发送无效的DTLS握手包到DTLS客户端，可令客户端进入死循环导致拒绝服务。

```

影响

```
只对使用了DTLS的客户端有影响。

```

#### CVE-2014-0198&&CVE-2010-5298

原理

```
ssl3_read_bytes功能在竞争条件下可以让攻击者在会话中注入数据或导致拒绝服务。

```

影响

```
只有在SSL_MODE_RELEASE_BUFFERS打开的时候受影响（默认关闭）
但是有些服务商为了节省内存会打开此选项。（比如Nginx,apache2.4.1,openvpn）
对DTLS/SSL2无影响。

```

#### CVE-2014-3470

匿名ECDH套件拒绝服务

OpenSSL TLS客户端启用了匿名ECDH密码套件会受到拒绝服务攻击。

0x02 修复
-------

* * *

### 1. 升级到Openssl最新版

Openssl 0.9.8 za

https://www.openssl.org/source/openssl-0.9.8za.tar.gz

Openssl 1.0.0m

https://www.openssl.org/source/openssl-1.0.0m.tar.gz

Openssl 1.0.1h

https://www.openssl.org/source/openssl-1.0.1h.tar.gz

### 2. 升级完后 记得重启是配置生效。

受影响的客户端及时进行补丁更新。:）