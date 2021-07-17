# ptunnel

ptunnel，全称“Ping Tunnel”，利用ICMP协议构建通信隧道，实现端到端通信。

网络环境拓扑：

![1.png](images/cd56d4f181aa47f18ce77c9989b5b800.png)

B、C上需要装ptunnel工具，因为这里A只能ping通B，所以让B作为server，即ICMP跳板机

注意：由于通过ICMP协议建立隧道，为了让隧道服务端能够处理收到的ICMP报文，需要禁用系统本身的ICMP响应机制，防止内核响应ping数据包本身。这里先关闭B的ICMP响应机制，否则会出现[err]: Dropping duplicate proxy session request.报错。

在B上运行命令ptunnel

![2.png](images/b4517426d87545b2b21c048dfefd2175.png)

在C上运行命令

```
ptunnel -p 192.168.137.128 -lp 8888 -da 192.168.44.130  -dp 3389
-p  指定跳板机的IP
-lp 指定转发本地监听的端口
-da 指定最终要访问的目标主机
-dp 指定最终要访问目标主机的端口

```

![3.png](images/c918e73eeffe4b31bdf8c4244253e6f6.png)

此时ICMP隧道就已经打通了，最后在D上访问C的8888端口就相当于访问A的3389端口了

```
mstsc /v:192.168.137.129:8888

```

![4.png](images/a76dea540df747dba7552cb6669c538f.png)

当然这里也可以让B既作为跳板机，又作为代理服务器

![5.png](images/2aa522451f594b2d98828f51738ecc76.png)

