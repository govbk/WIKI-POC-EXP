# iodine

iodine基于C语言开发，分为服务端程序iodined和客户端程序iodine，主要工作模式有直连模式和中继模式两种。iodine支持A、TXT、CNAME、MX、NULL等多种查询请求类型，通过一台DNS服务器即可建立一条数据通道。

网络拓扑：

![1.png](images/814473ed695349da87dd27285130c975.png)

#### DNS服务器

本地搭个简单的DNS服务器

```
yum install bind*  #安装bind服务
vim /etc/named.conf  #修改named配置文件

```

![2.png](images/a92512967a7d4896b00ad64618502f57.png)

```
vim /etc/named.rfc1912.zones  #添加需要解析的域名www.dns.com

```

![3.png](images/b1ce087a1afb4f36b7178575cc08e350.png)

添加对应的解析文件并修改

```
cp /var/named/named.localhost /var/named/named.dns.com
vim /var/named/named.dns.com

```

![4.png](images/22cf4313712040d386ad11a0035ad246.png)

虽然按照上面配置好了可能还是解析不了，可能有以下几个原因

防火墙开放53端口：`firewall-cmd --add-port=53/udp`

文件权限：

```
  chown  named.named   /var/named
  chown  named.named   /var/named/*

```

按照上面配置好后，记得重新启动一下服务`systemctl restart named.service`，一台简易的dns服务器就搭建起来了，测试一下

![5.png](images/70305e4d0faf4e6d8fa24fec8a07719d.png)

服务端

```
git clone https://github.com/yarrick/iodine
cd iodine
make install
或
apt install iodine(kali默认自带)

```

make install之后目录下会出现一个bin文件夹，里面有两个可执行文件iodined(服务端)、iodine(客户端)

```
iodined -f -P 123456 10.1.1.1 www.dns.com
-f 前台显示，运行后一直在命令行等待
-P 认证密码
10.1.1.1 自定义局域网虚拟IP
www.dns.com DNS服务器域名

```

![6.png](images/593d24eebd024bd2a5996c8155fa5fef.png)

此时服务端会多出现一块dns0的虚拟网卡，地址是刚刚设置的10.1.1.1

![7.png](images/f054a39bc7334879bb4e4d312ab95197.png)

客户端

```
iodine -f -P 123456 192.168.137.150 www.dns.com
IP为服务器IP
域名需要与服务端保持一致

```

![8.png](images/fae456fb840c448a9fe624a03be57b22.png)

此时客户端也会多出来一块dns0网卡，地址为10.1.1.2，与服务端的网卡处于同一局域网

![9.png](images/192ce8c5292946928523700922afbdbc.png)

测试一下连通性

![10.png](images/6da6afefc23148e2a886e76937e417e4.png)

远程登录服务器

![11.png](images/e42499a02d0f4b379e73cb9fbb560e85.png)

