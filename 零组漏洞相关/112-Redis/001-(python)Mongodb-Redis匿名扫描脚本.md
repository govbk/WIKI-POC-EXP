# (python)Mongodb-Redis匿名扫描脚本

### 一、漏洞简介

(python)Mongodb-Redis匿名扫描脚本

### 二、影响范围

### 三、复现过程

https://github.com/ianxtianxt/Mongodb-Redis-scan/

mongodb-redis匿名扫描脚本，支持mongodb和redis的匿名扫描，脚本是之前有需求写的，现在分享给大家学习和研究:

**用法：**


```
批量扫描：Mongodbscan.py -m 100 -u ip.txt url.txt

IP段扫描：Mongodbscan.py -m 100 -g 192.168.1.1-192.168.1.254 url.txt

python2环境

pip install redis
```