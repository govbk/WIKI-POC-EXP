# netsh

#### 简介

* netsh是Network Shell的缩写，是windows为我们提供的功能强大的网络配置命令行工具。
* 支持tcp，udp 正向端口转发和修改防火墙规则，没有反向转发的功能，不支持socks。
* 优点：win自带，支持ipv4和v6。

#### 用法

* 在xp/2003下使用，要先安装ipv6，装完后需要重启机器才能生效

    `netsh interface ipv6 install`

##### 管理防火墙

* 对于xp/2003的操作命令不同与之后的系统，而且xp/2003的防火墙不区分出站入站

    ```
    netsh firewall show state 可查看防火墙的状态，从显示结果中可看到防火墙各功能模块的禁用及启用情况。
    netsh firewall set opmode disable 用来禁用系统防火墙
    netsh firewall set opmode enable 可启用防火墙。

    netsh firewall add portopening TCP <端口号> "规则名称"   允许xx端口出入站
    netsh firewall delete portopening TCP <端口号>          删除该条规则

    ```

* 对于 2003 以后的系统，命令如下

    ```
    netsh advfirewall show allprofiles 查看防火墙的状态
    netsh advfirewall set allprofiles state on 开启防火墙
    netsh advfirewall set allprofiles state off 关闭防火墙

    netsh advfirewall firewall add rule name="规则名称" dir=in(in为入站,out为出站) action=allow(allow为放行，block为阻止) protocol=TCP localport=<端口号>     添加规则
    netsh advfirewall firewall delete rule name="规则名称" dir=in protocol=TCP localport=<端口号>      删除规则

    ```

##### 端口转发

```
netsh interface portproxy show all   查看所有已设置的转发规则
netsh interface portproxy add v4tov4 listenport=<监听端口> connectaddress=<将要转发的ip> connectport=<将要转发的端口>   添加转发规则
netsh interface portproxy delete v4tov4 listenport=<转发的端口>   删除规则

```

