# meterpreter常见脚本介绍

0x00 前言
=======

* * *

在获得meterpreter的session后，除了meterpreter本身内置的一些基本功能，在`/usr/share/metasploit-framework/scripts/`meterpreter下面还有很多scripts，提供了很多额外功能，非常好用

我看网上没有详细介绍常见脚本功能的文章,就总结了一下

我们可以通过`run 脚本名`来进行使用

`run 脚本名 -h`可以查看帮助

0x01 常见脚本
=========

* * *

1 arp_scanner
-------------

利用arp进行存活主机扫描

![](http://drops.javaweb.org/uploads/images/ce55c9dbf45477aab87204358981a76386ae912a.jpg)

2 autoroute
-----------

可以添加，删除，显示路由表

3 checkvm
---------

可以检测目标是否是虚拟机

![](http://drops.javaweb.org/uploads/images/91580b83759fe33c4d79490ca5d72200ce081639.jpg)

4 credcollect
-------------

收集目标主机上的hash等凭证

![](http://drops.javaweb.org/uploads/images/4bf279a910a6866a3d9d7f4767e4e1b6a12bf7df.jpg)

5 domain_list_gen
-----------------

获取域管理账户列表，并判断当前session所在用户是否在列表中

6 dumplinks
-----------

Link文件包含时间戳，文件位置，共享名，卷序列号，等。脚本会在用户目录和office目录中收集lnk文件

![](http://drops.javaweb.org/uploads/images/93cde2996ce8ed5a41e97dbdb6212c5f560a91f9.jpg)

7 duplicate
-----------

再次产生payload，注入到其他进程或打开新进程并注入其中

![](http://drops.javaweb.org/uploads/images/495d00f0c4f66b2451fa63b39f40930467fe96d3.jpg)

![](http://drops.javaweb.org/uploads/images/0f2639a9ba9ce86062b5b98d80efd166a80a67be.jpg)

8 enum_chrome
-------------

获取chrome中的信息

9 enum_firefox
--------------

获取firefox中的信息，包括cooikie，历史纪录，书签等

![](http://drops.javaweb.org/uploads/images/e4e44b1d3124970577c56457ce7b16d7a036cdbd.jpg)

![](http://drops.javaweb.org/uploads/images/32d9db01742ccd1b2562ac817fc93183277ac595.jpg)

10 enum_logged_on_users
-----------------------

列出当前登录的用户

11 enum_powershell_env
----------------------

列出powershell和WSH的配置文件

12 enum_putty
-------------

列出putty的配置文件

13 enum_shares
--------------

列出共享及历史共享

14 enum_vmware
--------------

列出vmware的配置文件和产品

15 event_manager
----------------

可以查询和清理事件日志

![](http://drops.javaweb.org/uploads/images/40b8272996b7bc5f125c7f608a454cc24ab9798c.jpg)

16 file_collector
-----------------

搜索符合指定模式的文件

17 get_application_list
-----------------------

获取安装的程序列表及版本

![](http://drops.javaweb.org/uploads/images/bf27a136273aca7737747c50d8e00b440d45f004.jpg)

18 getcountermeasure
--------------------

列出HIPS 和 AV 的进程，显示XP 防火墙规则, 并且显示 DEP和UAC 策略

Ps：-k参数可以杀掉防护软件进程

![](http://drops.javaweb.org/uploads/images/a1537275c8f3cd80a5dbfeeed67c9889cad07a5a.jpg)

19 get_env
----------

获取所有用户的环境变量

20 get_filezilla_creds
----------------------

获取filezilla的登陆凭证

21 getgui
---------

可以很方便的开启远程桌面服务，添加用户，端口转发功能

![](http://drops.javaweb.org/uploads/images/f5c17b725b8cdd877c17410a4de27b7334646e85.jpg)

![](http://drops.javaweb.org/uploads/images/db30f56fe7ca2e494b5b4983fd52fbd16687d849.jpg)

![](http://drops.javaweb.org/uploads/images/32c6004517670209adb2dc48be034c60905ba9d6.jpg)

![](http://drops.javaweb.org/uploads/images/ec917f3f91b495cc980b706aadc4271667ddf101.jpg)

![](http://drops.javaweb.org/uploads/images/b61b7985682bd8a40135218785429ee84e5ff039.jpg)

22 get_local_subnets
--------------------

获得本地的子网

23 get_pidgin_creds
-------------------

获取pidgin配置文件中的用户名和密码

24 gettelnet
------------

同之前开启终端桌面服务的脚本，这个是用来开启telnet的

25 get_valid_community
----------------------

获取SNMP community字符串

26 getvncpw
-----------

获取vnc密码

27 hashdump
-----------

同meterpreter的内置功能

28 hostsedit
------------

操作hosts文件

29 keylogrecorder
-----------------

Meterpreter内置此功能

30 killav
---------

关闭防护软件

31 metsvc
---------

将payload安装为服务

32 migrate
----------

同内置功能，用于迁移进程

33 persistence
--------------

可见建立一个持久性的后门，设置成开机启动

34 service_permissions_escalate
-------------------------------

许多服务被配置了不安全 的权限。 这个脚本会尝试创建一个服务, 然后会搜索已存在d服务，找到不安全的文件或配置有问题的文件，用一个payload替换掉他，然后会尝试重启服务来运行这个paylaod，如果重启服务失败，则在下次服务器重启时会执行payload

35 vnc
------

可以看到远程桌面

36 win32-sshserver
------------------

安装openssh服务

37 winenum
----------

会自动运行多种命令，将命令结果保存到本地

![](http://drops.javaweb.org/uploads/images/cc0bff0893ce7c17d4f64e08581bc649c3ff4431.jpg)

![](http://drops.javaweb.org/uploads/images/9d2e67cf65fb89680ff1d88f527120890f33ca69.jpg)

Ps：这些脚本最好的地方在于有源码可看，可以根据环境进行修改，如何运用就看各人了