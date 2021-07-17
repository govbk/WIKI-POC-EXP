# 从cloudstack默认配置看NFS安全

看到有同学写了关于[NFS的运维安全](http://drops.wooyun.org/tips/1423)，本菜鸟以cloudstack为例也写下关于NFS访问控制安全吧。

0x00 NFS默认配置缺陷
--------------

* * *

在Cloudstack云平台部署时，按照apache官方的安装文档，如果又不对管理网络进行隔离会导致整个云环境中的虚拟机处于危险状态：

![2014042411404387958.jpg](http://drops.javaweb.org/uploads/images/f0225e7191792c699301a90de5462d147d27bc74.jpg)

[http://cloudstack.apache.org/docs/zh-CN/Apache_CloudStack/4.1.1/html/Installation_Guide/management-server-install-flow.html#prepare-nfs-share](http://cloudstack.apache.org/docs/zh-CN/Apache_CloudStack/4.1.1/html/Installation_Guide/management-server-install-flow.html#prepare-nfs-share)

1.     配置新的路径作为 NFS 引入, 编辑`/etc/exports`。引入NFS 共享用`rw,async,no_root_squash`。例如：

```
#vi /etc/exports

```

插入下列行。

```
/export *(rw,async,no_root_squash)

```

看到如上的配置exports文件，小伙伴们震惊了吧，任意用户可以读取与写入文件，该配置是对整个云环境的存储做的配置，也就意味着任意能够访问到该IP的用户都可控制整个云系统。

0x01 攻击权限配置不当的NFS系统
-------------------

* * *

只要在云环境中的任意一台主机进行查看：

![2014042411412586267.jpg](http://drops.javaweb.org/uploads/images/f7f02a6eb1117447b0fd075ae9105fd22ba0b573.jpg)

然后进行mount 该文件夹，可以任意操作该存储上的虚拟机：

![2014042411420188380.jpg](http://drops.javaweb.org/uploads/images/833573cf3a6488c2e9262e74d7ab2506d326088f.jpg)

0x02 漏洞修复
---------

* * *

还是`/etc/exports`下的文件，如果配置成如下模式则可减少风险（我说的仅仅是减少）：

```
/export 172.19.104.6(rw,async,no_root_squash)

```

这样就把访问控制给了单独的IP，但这样是不是就安全了，小伙伴们可以继续想伪造IP的办法来绕过了。