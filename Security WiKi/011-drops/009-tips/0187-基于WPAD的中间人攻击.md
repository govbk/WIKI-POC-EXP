# 基于WPAD的中间人攻击

0x00 前言
=======

* * *

学习@Her0in《Windows名称解析机制探究及缺陷利用》很受启发，于是对其实际利用做了进一步研究，发现基于WPAD的中间人攻击很是有趣，现将收获分享给大家。

![p1](http://drops.javaweb.org/uploads/images/a16935adf7c053fc3a81706945caf1ee318ed72e.jpg)

0x01 简介
=======

* * *

**WPAD:**

全称网络代理自动发现协议（Web Proxy Autodiscovery Protocol）,通过让浏览器自动发现代理服务器，定位代理配置文件，下载编译并运行，最终自动使用代理访问网络。

**PAC：**

全称代理自动配置文件（Proxy Auto-Config），定义了浏览器和其他用户代理如何自动选择适当的代理服务器来访问一个URL。

要使用 PAC，我们应当在一个网页服务器上发布一个PAC文件，并且通过在浏览器的代理链接设置页面输入这个PAC文件的URL或者通过使用WPAD协议告知用户代理去使用这个文件。

WPAD标准使用 wpad.dat，PAC文件举例：

```
function FindProxyForURL(url, host) {
   if (url== 'http://www.baidu.com/') return 'DIRECT';
   if (host== 'twitter.com') return 'SOCKS 127.0.0.10:7070';
   if (dnsResolve(host) == '10.0.0.100') return 'PROXY 127.0.0.1:8086;DIRECT';
   return 'DIRECT';
}

```

0x02 WPAD原理
===========

* * *

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1b3e6c3e3d85ccae2b04caddc2729afea6783b6c.jpg)

此图片修改于http://wenku.baidu.com/link?url=KFoXTvqgxnNR1lxM_2dHCCRlJXp0D2GXa80fI7BCjR7XSoDqv2jmLJ8WJoSaew9MFSpKmTDV9lxNF2XKhTaJ1T8rSghDrhZ71OqlQ1yqx-a

用户在访问网页时，首先会查询PAC文件的位置，具体方式如下：

**1、通过DHCP服务器**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/c98ddbc0d484bf3ab69e7c043d308330ffb786ca.jpg)

web浏览器向DHCP服务器发送DHCP INFORM查询PAC文件位置

DHCP服务器返回DHCP ACK数据包，包含PAC文件位置

**2、通过DNS查询**

web浏览器向DNS服务器发起 WPAD＋X 的查询

DNS服务器返回提供WPAD主机的IP地址

web浏览器通过该IP的80端口下载wpad.dat

**3、通过NBNS查询**

> Tips：
> 
> Windows 2K , XP , 2K3 只支持 DNS 和 NetBIOS
> 
> Windows Vista 之后（包括 2K8 ， Win7，Win8.x，Win 10）支持DNS、NBNS、LLMNR

如果DHCP和DNS服务器均没有响应，同时当前缓存没有所请求的主机名，就会发起如下名称解析：

如果当前系统支持LLMNR（Link-Local Multicast Name Resolution），先发起广播LLMNR查询，如果没有响应再发起广播NBNS查询

如果有主机回应PAC文件位置

web浏览器通过该IP的80端口下载wpad.dat

0x03 WPAD漏洞
===========

* * *

对照WPAD的原理，不难发现其中存在的漏洞，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/b8535e7814bd67884cad39bb3c7ae6b4bc932049.jpg)

此图片修改于 http://wenku.baidu.com/link?url=KFoXTvqgxnNR1lxM_2dHCCRlJXp0D2GXa80fI7BCjR7XSoDqv2jmLJ8WJoSaew9MFSpKmTDV9lxNF2XKhTaJ1T8rSghDrhZ71OqlQ1yqx-a

如果在被攻击用户发起NBNS查询时伪造NBNS响应，那么就能控制其通过伪造的代理服务器上网，达到会话劫持的目的。

0x04 WPAD漏洞测试
=============

* * *

**测试环境：**

```
被攻击用户：
win7 x86
192.168.16.191

攻击用户：
kali linux
192.168.16.245

```

**测试过程：**

**1、监听NBNS查询**

```
use auxiliary/spoof/nbns/nbns_response
set regex WPAD
set spoofip 192.168.16.245
run

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/f55f58bb70d9c72074958471a15cb1c54fc26845.jpg)

**2、设置WPAD服务器**

```
use auxiliary/server/wpad
set proxy 192.168.16.245
run

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/331831e6414df0763405154a59520146cc4a182a.jpg)

**3、被攻击用户发起查询**

构造广播NBNS查询

需要使当前dbcp和dns服务器均无法提供的PAC文件位置

**4、响应被攻击机用户的广播NBNS查询**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/86b214d8c323e9af0c8fff5ede6befa5b6358416.jpg)

攻击主机响应广播NBNS查询并指定PAC文件位置

被攻击主机访问指定的PAC位置请求下载

wireshark抓包如图

广播NBNS查询包，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/3d2431db022730daa54dd1af503cb643511b3e73.jpg)

NBNS查询响应包，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/88a49d8cc57ea103466ff13b882ad5624d01750b.jpg)

被攻击主机请求PAC文件位置，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/f686f2087eae6eeac5bec55a2c024ddd30519ca6.jpg)

攻击主机回复PAC文件信息，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e64205950fb25b9ff16d3cd54be53320e50802ca.jpg)

> Tips：
> 
> 虚拟机环境下使用wireshark只抓本地数据包，需要取消混杂模式

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/4fa7248729f6168d0d0d10b8a5d5013199063d23.jpg)

**5、被攻击机用户使用伪造的代理配置上网**

可在伪造的代理上面抓取被攻击用户的数据包，中间人攻击成功。

0x05 WPAD实际利用
=============

* * *

基于WPAD的中间人攻击有多大威力，超级电脑病毒Flame给了我们很好的示范。

其工作模式如下：

**1、SNACK: NBNS spoofing**

监听当前网络，如果收到了NBNS查询包含WPAD字符，立即伪造NBNS响应

**2、MUNCH: Spoofing proxy detection and Windows Update request**

提供WPAD服务，用来更改被攻击主机的WPAD设置

当其成功作为被攻击主机的代理后，会劫持特定的Windows更新请求，提供带有后门的windows更新文件给用户下载

如图为测试环境下抓到的windows更新请求包

![这里写图片描述](http://drops.javaweb.org/uploads/images/857772bab27a381ece288be18b6d5852cb1fc091.jpg)

Burp suite抓到的数据包：

![这里写图片描述](http://drops.javaweb.org/uploads/images/937561339b797fb4c34f33d89ce5df2a10aa7b66.jpg)

Flame最终成功实现了基于WPAD实施中间人攻击，篡改windows更新数据，最终感染了内网其他主机。

0x06 防护
=======

* * *

可通过如下设置关闭WPAD应用来避免此种攻击：

Internet Explorer-Internet Options-Connections-LAN settings

取消选中Automatically detect settings

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/8e930033604de2150ceac6a8b6000f1ce8e5b3c4.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/51505c7ea03e762b624f65ad372d7f9d78a4e328.jpg)

如果已被NBNS中间人攻击，可通过查看netbios缓存检查

```
nbtstat -c

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/189af2e6440754653a6f17acbe26772f3c2adccc.jpg)

0x07 补充
=======

* * *

Responder：

> Responder is a LLMNR, NBT-NS and MDNS poisoner, with built-in HTTP/SMB/MSSQL/FTP/LDAP rogue authentication server supporting NTLMv1/NTLMv2/LMv2, Extended Security NTLMSSP and Basic HTTP authentication.

Responder可以说是内网中间人攻击神器，很值得尝试

简单使用命令如下：

```
git clone https://github.com/SpiderLabs/Responder.git
cd Responder/

python Responder.py -I eth0 -i 192.168.16.245 -b

```

当被攻击主机访问主机共享时就能抓到其hash，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/2c66a87ad83056fcac856c6ba170476622aabc31.jpg)

0x08 小结
=======

* * *

虽然WPAD不是很新的技术，但是对其了解的都不太多，在内网渗透中应该被重视。

**参考资料：**

*   [http://drops.wooyun.org/papers/10887#comments](http://drops.wooyun.org/papers/10887#comments)
*   [http://www.netresec.com/?page=Blog&month=2012-07&post=WPAD-Man-in-the-Middle](http://www.netresec.com/?page=Blog&month=2012-07&post=WPAD-Man-in-the-Middle)
*   [http://wenku.baidu.com/link?url=KFoXTvqgxnNR1lxM_2dHCCRlJXp0D2GXa80fI7BCjR7XSoDqv2jmLJ8WJoSaew9MFSpKmTDV9lxNF2XKhTaJ1T8rSghDrhZ71OqlQ1yqx-a](http://wenku.baidu.com/link?url=KFoXTvqgxnNR1lxM_2dHCCRlJXp0D2GXa80fI7BCjR7XSoDqv2jmLJ8WJoSaew9MFSpKmTDV9lxNF2XKhTaJ1T8rSghDrhZ71OqlQ1yqx-a)
*   [http://www.ibm.com/developerworks/cn/linux/1309_quwei_wpad/](http://www.ibm.com/developerworks/cn/linux/1309_quwei_wpad/)
*   [https://securelist.com/blog/incidents/33002/flame-replication-via-windows-update-mitm-proxy-server-18/](https://securelist.com/blog/incidents/33002/flame-replication-via-windows-update-mitm-proxy-server-18/)
*   [https://github.com/SpiderLabs/Responder](https://github.com/SpiderLabs/Responder)
*   [https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/spoof/nbns/nbns_response.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/spoof/nbns/nbns_response.rb)
*   [https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/server/wpad.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/server/wpad.rb)
*   [https://www.trustwave.com/Resources/SpiderLabs-Blog/Responder-2-0---||||||Owning-Windows-Networks-part-3/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Responder-2-0---Owning-Windows-Networks-part-3/)
*   [https://github.com/lgandx/Responder-Windows](https://github.com/lgandx/Responder-Windows)
*   [http://www.censornet.com/pdf/WPAD-Configuration-Guide.pdf](http://www.censornet.com/pdf/WPAD-Configuration-Guide.pdf)
*   [http://findproxyforurl.com/wpad-introduction/](http://findproxyforurl.com/wpad-introduction/)

本文由三好学生原创并首发于乌云drops，转载请注明