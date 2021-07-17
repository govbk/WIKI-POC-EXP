# windows端口转发

```bash
netsh interface ipv6 install     首先安装IPV6（xp、2003下IPV6必须安装，否则端口转发不可用！）

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=22connectaddress=1.1.1.1 connectport=22 //将本机22到1.1.1.1的22

netsh interface portproxy add v4tov4 listenaddress=192.168.193.1listenport=22 connectaddress=8.8.8.8 connectport=22

netsh interface portproxy add v4tov4 listenaddress=192.168.193.1listenport=22 connectaddress=百度一下，你就知道 connectport=22

netsh interface portproxy show all          查看转发配置

netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0listenport=22     删除配置

netsh firewall set portopening protocol=tcp port=22 name=Forwardmode=enable scope=all profile=all     添加防火墙规则，允许连接22：

```

