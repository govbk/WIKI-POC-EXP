# TLS扩展的那些事

0x00 背景
=======

* * *

TLS扩展于2003年以一个独立的规范（RFC3456)被提出，之后被加入到TLS1.1和TLS1.2的版本中。它主要用于声明协议对某些新功能的支持，或者携带在握手进行中需要的额外数据。TLS扩展机制使得协议在不改变本身基本行为的基础上增加了额外的功能，因此从出现以来，它就成为协议功能不断发展的主要载体。

实际使用中，扩展以扩展块的形式出现在ClientHello和ServerHello消息的最后，例如我们访问百度网站时，ClientHello数据包如下图所示，其中`Extensions Length`之后的字段都是扩展字段。在这一讲中，我们对这些比较常见的扩展进行详细的介绍。

![p1](http://drops.javaweb.org/uploads/images/b5848723d420e5ca787fd40081ff122781dc7824.jpg)

0x01 概述
=======

* * *

如上图所示，各个扩展以扩展块的形式并列出现。而每个扩展都以两个字节的表明扩展类型的字段开始，后面接着扩展的数据。

```
Extension extensions;
struct {
      ExtensionType extension_type;
      opaque extension_data;
} Extension;

```

全部的扩展类型可以在IANA的[网站](http://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml)看到，扩展数据的格式以及对TLS协议的影响由各个扩展的规范来规定。这里我们主要介绍实际中比较常见的一些扩展。下表列出了我们接下来要介绍的一些扩展名称以及对其功能的简单介绍。

| 类型 | 扩展名称 | 功能描述 |
| :-: | :-: | :-: |
| 0xff01 | renegotiation_info | 表明可以支持安全的重协商 |
| 0x00 | server_name | 表明连接中要访问的virtual hostname |
| 0x23 | session_ticket | 表明支持没有状态的会话恢复 |
| 0x0d | signature_algorithms | 表明支持的签名算法和哈希函数对 |
| 0x05 | status_request | 表明支持OCSP Stapling |
| 0x3374 | next_protocol_negotiation | 表明支持NPN |
| 0x12 | signed_certificate_timestamp | 表明证书已通过Certificate Transparency公开 |
| 0x10 | application_layer_protocol_negotiation | 表明支持的应用层协议 |

0x02 详细介绍
=========

* * *

**1.安全重协商**

在介绍`renegotiation_info`这个扩展之前，我们对TLS重协商机制进行简单的描述。正常的TLS连接以握手开始，在交换数据之后关闭连接。但若通信过程中双方有一方请求重协商，那么会再发生一次握手以协商出新的通信安全参数。重协商可能会在以下几种情况中出现：

*   需要客户端证书的情况。一些网站会使用客户端证书进行双因子认证。一种部署方式是与网站的所有连接都要求使用客户端证书，但这显然是一种极不友好的方式，对于没有客户端证书的访问者来说，网站不能向他们发送任何信息。另一种方式就是只在某些子站点中要求客户端证书，这样当一个用户访问到子站点时，服务器可以发起重协商以此来验证客户端证书。
*   信息隐藏。因为第二次握手的信息是由第一次的加密通道传输的，所以重协商的信息（比如客户端证书这样可以表明用户身份的信息）可以被很好的保护，不被被动监听者获取。
*   改变加密强度。也有一些情况是站点的安全配置要求不一，在访问到一些安全性要求高的子站点后，需要升级通信的加密强度，此时也可以通过重协商完成。

协议规定客户端可以在任何时候发起重协商，只需发送一个新的ClientHello消息。如果服务器想要重协商，则向客户端发送一个HelloRequest消息，告诉客户端停止发送加密数据并且发起一次新的握手。

最初设计的重协商机制无法抵御如下图所示的中间人攻击。攻击者可以在客户端连接的开始注入任意的明文，无法保证TLS传输数据的完整性。

![p2](http://drops.javaweb.org/uploads/images/45cd8b8cc70488588ed9ba59ca3132c031829407.jpg)

renegotiation_info扩展的提出就是为了阻止这种中间人攻击，保证重协商是发生在之前已完成握手的双方之间。一次由客户端发起的重协商如下图所示，在第一次握手中ClientHello消息中包含一个没有数据的renegotiation_info扩展，表明客户端支持重协商，服务器在ServerHello中也包含一个没有数据的renegotiation_info扩展表明支持，并且在握手协商完成后，双方将Finished消息中的verify_data存在本地。之后客户端要发起重协商时，发送一个包含客户端verify_data扩展的ClientHello消息到服务器，服务器回复一个包含客户端和服务器verify_data重协商扩展的ServerHello消息表明愿意重协商上一次的握手，之后重新协商通信安全参数。

![p3](http://drops.javaweb.org/uploads/images/9bef21c662e93bbc010e3a2676d2cdb9034b8dad.jpg)

对于不支持扩展的SSL3，客户端可以在密码套件列表中加入TLS_EMPTY_RENEGOTIATION_INFO_SCSV (0xff)表明对重协商的支持。

**2.Server Name Indication（SNI）**

SNI提供了一种机制，可以让客户端指明它想要连接的服务器的名称。也就是说`server_name`这个扩展提供了对虚拟服务器的支持，可以让服务器在众多虚拟主机中找到相应的证书。比如一台服务器中有两个虚拟主机，分别是alipay.com和baidu.com，若客户端不指明其要访问的主机名，则服务器无法判断应该回复支付宝还是百度的证书，那么一个IP地址就只能有一个证书。

![p4](http://drops.javaweb.org/uploads/images/467e97d1c866f0c6d25bcd00d36efb9da30843db.jpg)

**3.Session Tickets**

Session Tickets提供了一种新的会话恢复机制。在介绍`session_ticket`这个扩展之前，我们还是先对会话恢复进行简单地描述。之前介绍的SSL握手的全部过程需要客户端和服务器的两轮交互，其中的密码学操作通常需要密集的CPU处理，且基于客户端和服务器证书验证的身份认证还要更多的操作，因此开销相对较大。而这种开销可以通过恢复之前的会话来避免。

原本的会话恢复是基于客户端和服务器在第一次握手完成后保存相关的会话安全参数。在第一次握手中，服务器若想在之后恢复这个会话，则在ServerHello消息中包含一个Session ID。之后若客户端想要恢复这个会话，则在ClientHello中包含这个Session ID，服务器在ServerHello中回复相同的Session ID表明同意恢复会话，双方根据上次握手中的master secret计算本次的密钥，之后互发Finished消息完成握手。这种握手只需要一轮交互，大大缩短了握手开销。

而通过Session Tickets引入的这种会话恢复机制，则不需要服务器端存储任何数据。服务器只需将恢复会话所需的信息加密以ticket的形式发送给客户端。在第一次握手中，session ticket包含在New Session Ticket消息中发给客户端。

![p5](http://drops.javaweb.org/uploads/images/b8a69d04cd15feecbfc2b6249d668a7bee974b11.jpg)

![p6](http://drops.javaweb.org/uploads/images/4dbec029040da02de69651562a4e1ada7623f504.jpg)

在客户端想要恢复前面的某一会话时，就在ClientHello中包含那次会话的Session Ticket，服务器决定接收后发送ServerHello并继续发送ChangeCipherSpec。

**4.签名算法**

`signature_algorithms`这个扩展是在TLS1.2中定义的，用于表明客户端支持的签名和哈希算法。这个扩展可有可无，若没有，则服务器从客户端提供的密码套件列表里推断支持的签名算法（比如RSA密码套件就表明支持RSA签名算法），而直接假设支持的哈希算法是SHA1.

![p7](http://drops.javaweb.org/uploads/images/a7cabb2f9988b4007ea91a3fc2e00ab42bcea104.jpg)

**5.OCSP Stapling**

`status_request`这个扩展用于表明客户端支持OCSP stapling。OCSP是一个检查证书吊销信息的协议，OCSP stapling机制可以使服务器向客户端发送最新的证书吊销信息，而无需客户端去访问CA的证书吊销列表。

![p8](http://drops.javaweb.org/uploads/images/2abba1d552d375ad1a44c1886398b44c957d1633.jpg)

如上图所示，在客户端和服务器都表明支持OCSP stapling后，服务器在发送完Certificate消息后紧跟着发送Certificate Status消息，提供关于证书吊销的必要信息。

![p9](http://drops.javaweb.org/uploads/images/94bd50369458803128715351e65aa79461c45feb.jpg)

**6.Certicate Transparency**

`signed_certificate_timestamp`扩展是Certificate Transparency（CT）运用在TLS协议中的一种体现。CT是为改善PKI现状而提出的一种提议，它将所有证书都记录下来。CA将其签发的所有证书都提交给一个公共的log服务器，并收到Signed Certificate Timestamp (SCT)作为提交的证据。在这个扩展机制中，SCT就通过ServerHello的扩展发给服务器。

**7.Application Layer Protocol Negotiation(ALPN)**

`application_layer_protocol_negotiation`扩展可以让通信双方协商运行在TLS连接之上的应用层协议，比如SPDY，HTTP2.0等。客户端在ClientHello中包含扩展字段，里面的内容是其支持的协议列表，服务器在ServerHello中回复的扩展字段包含其选择的协议。

![p10](http://drops.javaweb.org/uploads/images/046507627c0650565581d8d9d89738ab71d8554a.jpg)

值得注意的是客户端支持的协议列表和服务器最终选择的结果都没有被加密，任何可以看到流量的中间人都可以得知这些信息。

**8.Next Protocol Negotiation(NPN)**

`next_protocol_negotiation`扩展是为了支持NPN机制而引入的。而NPN是谷歌为了推广SPDY的应用，解决防火墙问题和代理问题的前提下提出的。

与ALPN基本类似，只不过NPN为了保护最终的选择结果，这个信息是加密传送的，也就是说在ChangeCipherSpec后发送，这就需要引入一个新的消息NextProtocol。由于需要引入新的握手消息，并且选择结果不被中间的设备看到可能会有问题，因此TLS working group拒绝了这一方案，而是采用了ALPN。

0x03 结语
=======

* * *

本讲介绍了TLS协议的几个常见扩展，希望对大家在深入理解TLS协议以及深入分析SSL数据包方面有所帮助。

注：本文涉及的基本知识来源于《BulletProof SSL and TLS》，这是一本讲SSL很好的教材，推荐给大家。另本文内容是作者在教材内容的基础上结合自己的理解及具体数据包分析写作完成的，特此声明。