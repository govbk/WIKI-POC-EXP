# NFS配置不当那些事

0x00 背景
=======

* * *

NFS（Network File System）：是FreeBSD支持的文件系统中的一种，它允许网络中的计算机之间通过TCP/IP网络共享资源；

NFS配置：（声明：以下NFS实验是在RedHat7上完成）

首先安装NFS（我的机子是最小化的系统，需要自己安装）：

```
yum install nfs-utils.x86_64 -y

```

启动服务：

```
systemctl start rpcbind（如果这个服务不启动，nfs服务会启动失败）
systemctl start nfs-server
systemctl enable rpcbind;systemctl enable nfs-server 开机自启
firewall-cmd --permanent --add-service=nfs 让防火墙通过NFS服务
firewall-cmd --permanent --add-service=rpc-bind 通过rpc服务（如果不开启，rpcinfo就不能扫描）
firewall-cmd --permanent --add-service=mountd 通过mountd服务（如果不开启，不能远程showmount）
firewall-cmd --reload
配置：
mkdir /pentest（创建一个共享目录）
vi /etc/exports
cat /etc/exports
/ *(rw,sync,no_root_squash) （注意：问题就出在这个地方，原理在文后解释）
exportfs -r （启动共享）
showmount -e （查看共享）
客户端挂载：
mount -t nfs NFS服务器IP:/ /tmp/test （挂载到本地的/tmp/test中）

```

![enter image description here](http://drops.javaweb.org/uploads/images/d1f81f07dc266a34df11f70c7f23bdc434c805ae.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f074db724b472c48ee38db3592b5162dec8aae5c.jpg)

0x01 检测
=======

* * *

对存在NFS配置错误的机子进行扫描：`rpcinfo -p 192.168.119.131`

![enter image description here](http://drops.javaweb.org/uploads/images/ae64728c12860401b17cb8cb6801fcfe9dc80141.jpg)

查看nfs挂载新型：`showmount -e 192.168.119.131`

![enter image description here](http://drops.javaweb.org/uploads/images/c700fc9d6952cb789da3e7bd3dd2a5b87d3ebcf0.jpg)

得到这些信息，我们就可以挂载NFS，并传输ssh永久连接文件

![enter image description here](http://drops.javaweb.org/uploads/images/df928616254b4304622fbb5611fc5eb9c8a88729.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/c3501d7c6ffb89e050d905563cf73368a8f40d85.jpg)

0x02 总结
=======

* * *

其实漏洞形成的原理就是权限不对，`/etc/exports`这个文件中的权限设置，我们上文采用的是`root`权限，所以导致服务器被入侵；

`/etc/exports`文件格式

```
<输出目录> [客户端1 选项（访问权限,用户映射,其他）] [客户端2 选项（访问权限,用户映射,其他）]

```

a. 输出目录：输出目录是指NFS系统中需要共享给客户机使用的目录；

b. 客户端：客户端是指网络中可以访问这个NFS输出目录的计算机

指定ip地址的主机：`192.168.0.200`

指定子网中的所有主机：`192.168.0.0/24 192.168.0.0/255.255.255.0`

指定域名的主机：`david.bsmart.cn`

指定域中的所有主机：`*.bsmart.cn`

所有主机：`*`

c. 选项：选项用来设置输出目录的访问权限、用户映射等。

设置输出目录只读：`ro`

设置输出目录读写：`rw`

d. 用户映射选项

`all_squash`：将远程访问的所有普通用户及所属组都映射为匿名用户或用户组（`nfsnobody`）；

`no_all_squash`：与`all_squash`取反（默认设置）；

`root_squash`：将`root`用户及所属组都映射为匿名用户或用户组（默认设置）；

`no_root_squash`：与`rootsquash`取反；

`anonuid=xxx`：将远程访问的所有用户都映射为匿名用户，并指定该用户为本地用户（`UID=xxx`）；

`anongid=xxx`：将远程访问的所有用户组都映射为匿名用户组账户，并指定该匿名用户组账户为本地用户组账户（`GID=xxx`）；

e. 其它选项

`secure`：限制客户端只能从小于`1024`的`tcp/ip`端口连接`nfs`服务器（默认设置）；

`insecure`：允许客户端从大于`1024`的`tcp/ip`端口连接服务器；

`sync`：将数据同步写入内存缓冲区与磁盘中，效率低，但可以保证数据的一致性；

`async`：将数据先保存在内存缓冲区中，必要时才写入磁盘；

`wdelay`：检查是否有相关的写操作，如果有则将这些写操作一起执行，这样可以提高效率（默认设置）；

`no_wdelay`：若有写操作则立即执行，应与`sync`配合使用；

`subtree`：若输出目录是一个子目录，则`nfs`服务器将检查其父目录的权限(默认设置)；

`no_subtree`：即使输出目录是一个子目录，`nfs`服务器也不检查其父目录的权限，这样可以提高效率。