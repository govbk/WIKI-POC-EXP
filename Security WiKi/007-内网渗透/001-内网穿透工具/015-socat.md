# socat

公网端：

socat TCP4-LISTEN:转发端口 TCP4-LISTEN:公网服务端口

内网端：

socat TCP4:公网IP:转发端口 TCP4:127.0.0.1:内网服务端口

测试：

```
    内网端：

     socat tcp-listen:内网服务端口 -

    客户端：

    echo “test” | socat - tcp-connect:公网IP:公网服务端口

```

