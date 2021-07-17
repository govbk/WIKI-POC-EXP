# reDuh 实现内网转发

### Github地址

```
https://github.com/sensepost/reDuh

```

### 思维导图

![](images/15897824991445.png)


### reDuh使用条件

（1）获取目标服务器webshell，且可以上传reDuh服务端对应脚本文件。

（2）知道目标服务器开放的内网端口，如远程桌面的端口是3389。

（3）目标服务器网络做了端口策略限制，只允许外部访问内网的80等特定端口。

### reDuh使用命令

（1）本地具备java环境，可以使用pentestbox自带java环境

```
java -jar reDuhClient.jar  http://somesite.com/reDuh.aspx http or https port

```

（2）本地连接1010端口


```
nc -vv localhost 1010
```

（3）在java命令窗口执行


```
[createTunnel]1234:127.0.0.1:3389
```

（4）使用mstsc登录127.0.0.1:1234

## 参考链接

> https://blog.51cto.com/simeon/2112416

