# 卧底路由器之WooyunWifi of DOOM

在实际业务中，我们经常会遇到一些渗透测试项目由于处于企业内网，因此不得不把白帽子们集合起来塞进小黑屋实地测试。

本文基于Openwrt，通过Openvpn桥接本地网络与远程目标内网，实现layer 3的内网访问，文章重点不是如何进行内网渗透，而是如何授权完全不会内网渗透的白帽子远程进入内网搞渗透测试。

```
      192.168.35.0/24
                                                                                  0.0.0.0
+--------------------------+
|                          |                        +-----------------------------------------------------------------------------+
|                          |                        |                                                                             |
|  Private subnet          |                        |                                                                             |
|                          |                        |                           Open Internet                                     |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|               10.8.0.29  |                        |        10.8.0.1                                       10.8.0.*              |
|           +------------------+                    |   +--------------------+                          +----------------+        |
|           |              |   |   192.168.35.0/24  |   |                    |     192.168.35.0/24      |                |        |
|           |      Target  |   <------------------------>   Openvpn Server   <-------------------------->    Attacker    |        |
|           |              |   |                    |   |                    |                          |                |        |
|           +------------------+     vpn tunnel     |   +--------------------+      vpn tunnel          +----------------+        |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|                          |                        |                                                                             |
|                          |                        +-----------------------------------------------------------------------------+
+--------------------------+

```

0x00 基本原理
---------

* * *

首先我们利用Openvpn的隧道来穿透企业内网，这一点对于企业自身的网络工程师而言比较轻松，只要放行一条tcp连接（或者udp）用于构建vpn隧道就可以了，如果企业内网本身就没有封杀到外网的出站连接，那就更简单了

之后渗透测试人员各自与Openvpn外网主控服务器建立连接，桥接本地和远程内网网络，之后所有的内网访问都会通过Openvpn server转发进企业内网，与实际连入企业内网效果相同，而其他网段的连接则不受影响

0x01 Server搭建
-------------

* * *

首先要安装Openvpn

```
apt install openvpn

```

之后我们要建立自己的pki

```
#我们可以用Openvpn自带的easy-rsa来生成（不建议用软件源中的老版本easy-rsa）
git clone https://github.com/OpenVPN/easy-rsa.git
cd easy-rsa/easyrsa3
#请自行修改vars
cp vars.example vars
#初始化pki
./easyrsa init-pki
#注意，不要一次性复制粘贴多行命令，因为会要求输入ca密码
./easyrsa build-ca
#生成server端无需密码的req
./easyrsa gen-req server nopass
#和ca签约
./easyrsa sign server server
#生成diffie-hellman交换
./easyrsa gen-dh

#以下不必在ca端执行，可以让相关人员自己生成，然后在ca端import-req，这里偷懒直接自己搞了

#生成内网穿透目标的req并签约
./easyrsa gen-req target nopass
./easyrsa sign client target

#生成渗透测试人员的req并签约
./easyrsa gen-req client1 nopass
./easyrsa sign client client1

```

Openvpn server端配置文件： server.ovpn

```
#端口，不解释
port 1194

#TCP还是UDP
proto udp

#TUN还是TAP
dev tun

#改成我们刚生成的证书和key
ca /root/easy-rsa/easyrsa3/pki/ca.crt            
cert /root/easy-rsa/easyrsa3/pki/issued/server.crt
key /root/easy-rsa/easyrsa3/pki/private/server.key

#我们生成的diffie-hellman参数
dh /etc/openvpn/easyrsa3/pki/dh.pem

#Openvpn使用的网段
server 10.8.0.0 255.255.255.0

#记住之前分配过的ip
ifconfig-pool-persist ipp.txt

#通知客户端把内网网段路由到server上
push "route 192.168.35.0 255.255.255.0"

#客户端的独立profile
client-config-dir ccd
#通知server自己来处理内网网段路由
route 192.168.35.0 255.255.255.0

#点对点通信（在隧道上）
client-to-client

#保持连接
keepalive 10 120

#压缩
comp-lzo

#避免重启时导致各种tun上的手动设置丢失
persist-key
persist-tun

#log
status openvpn-status.log

#详细程度
verb 3

```

这里要注意两件事情，第一件是不可以使用duplicate-cn来偷懒，必须给每人签约一套认证，第二件是要保证要转发的内网网段必须不和本地网段冲突，不然自己到Openvpn server的流量都没法走了

建立配置中提到的配置文件夹： ccd

```
mkdir ccd

```

然后新建target的配置： target

```
iroute 192.168.35.0 255.255.255.0
ifconfig-push 10.8.0.29 10.8.0.1

```

这个iroute和之前route的区别是，iroute通知server把内网流量转发到target这台client上，而我们为了方便设置给target这个client分配个固定ip

然后运行Openvpn就好了

```
openvpn --config server.ovpn

```

0x02 client配置
-------------

* * *

其实就是一个和server端相对应的client配置文件： client1.ovpn

```
#客户端
client

#TUN还是TAP
dev tun

#TCP还是UDP
proto udp

#服务器公网ip和端口
remote 250.250.250.250 1194

#无限重试
resolv-retry infinite

nobind

#避免重启后手动配置消失
persist-key
persist-tun

#对应之前生成的client证书还有私钥
ca /root/easy-rsa/easyrsa3/pki/ca.crt            
cert /root/easy-rsa/easyrsa3/pki/issued/client1.crt
key /root/easy-rsa/easyrsa3/pki/private/client1.key

#压缩
comp-lzo

verb 3

```

这里要注意的是生成的req一定要记得去server那个对应的ca签约，另外不可以多个client用一个key

然后运行openvpn就好了

```
openvpn --config client1.ovpn

```

0x03 内网target配置
---------------

* * *

内网target的openvpn配置文件和正常client的配置文件是相同的，只要把key和crt替换成target自己的就可以

但是需要加一条转发，保证通过隧道访问内网的连接可以正确到达内网后再被通过隧道转发回去

```
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o br-lan -j MASQUERADE

```

这里假设我们要远程桥接的内网在br-lan接口可达，这里的例子是Openwrt的一个内部网络的interface，如果用的是台式机，可能是eth0之类的，如果是要映射路由器自己本身所在的内网，可以改成wan口（注意配置firewall）

如果用的是Openwrt路由器，这时需要先把默认drop的forward规则改成accept，不然会不停的报错反馈 port unreachable

然后运行openvpn就好了

```
openvpn --config target.ovpn

```

0x04 自动化部署
----------

* * *

我们可以把target部署在一个Openwrt路由器上，把target部署的全部步骤彻底自动化，简化成只需要给路由器配置网络即可

自动化配置的文件如下：

```
    #target用到的各种认证文件
    $(CP) $(PKG_BUILD_DIR)/conf/ca.crt $(1)/etc/openvpn
    $(CP) $(PKG_BUILD_DIR)/conf/target.crt $(1)/etc/openvpn
    $(CP) $(PKG_BUILD_DIR)/conf/target.key $(1)/etc/openvpn
    #target的配置文件
    $(CP) $(PKG_BUILD_DIR)/conf/target.ovpn $(1)/etc/openvpn
    #Openwrt系统的openvpn服务配置（用于指定target配置文件路径）
    $(CP) $(PKG_BUILD_DIR)/conf/openvpn $(1)/etc/config
    #把forward改成accept
    $(CP) $(PKG_BUILD_DIR)/conf/firewall $(1)/etc/config
    #改出我们想要的192.168.35.0/24内网网段
    $(CP) $(PKG_BUILD_DIR)/conf/network $(1)/etc/config
    #添加iptables转发隧道至内网，然后再转发响应从隧道回去
    $(CP) $(PKG_BUILD_DIR)/conf/firewall.user $(1)/etc

```

于是当这台路由器被配置好网络后，就会连接Openvpn server，并把指定的内网开放给连接Openvpn server的渗透测试人员们

下图为client1测试`mtr 192.168.35.154`连接192.168.35.0/24内网中设备的路由情况，成功通过10.8.0.29连接到了内网设备

![mtr](http://drops.javaweb.org/uploads/images/d0cbad4b94ee43686e9a7063c9e389056db404ba.jpg)

我把整个自动部署的配置打成了个Openwrt的package，大家可以到github上下载示例（替换成自己的key和crt）

https://github.com/lxj616/wooyunwifi_ofdoom

0x05 参考文献 & 致谢
--------------

* * *

kali官方给出的single server与single agent模式配置介绍： https://www.offensive-security.com/kali-linux/kali-rolling-iso-of-doom/

binkybear 给出的利用openvpn-as来做的multi-client形式的教程（在Nethunter上实现的agent），由于openvpn-as是商业版的（免费授权最多两个连接，限制太多），因此我决定在Openwrt上基于原版openvpn来做： https://github.com/offensive-security/kali-nethunter/issues/421

最后声明一下，这个功能不包含在WooyunWifi里面，公开的代码完全不依赖WooyunWifi，也不包含任何WooyunWifi的代码，对于普通的Openwrt路由器，只需要安装openvpn即可，请在合法的范围内使用本文中所提到的技术，不要在未经同意的情况下把路由器放进别人内网，也不要把Openvpn server部署到国外免得违背某些奇怪的政策……