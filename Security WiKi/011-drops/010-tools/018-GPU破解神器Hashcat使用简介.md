# GPU破解神器Hashcat使用简介

0x00 背景
-------

* * *

目前GPU的速度越来越快，使用GPU超强的运算速度进行暴力密码破解也大大提高了成功率，曾经看到老外用26块显卡组成的分布式破解神器让我羡慕不已。要说目前最好的GPU破解HASH的软件，非HashCat莫属了。下面我就为大家具体介绍一下HashCat系列软件。

0x01 所需硬件及系统平台
--------------

* * *

HashCat系列软件在硬件上支持使用CPU、NVIDIA GPU、ATI GPU来进行密码破解。在操作系统上支持Windows、Linux平台，并且需要安装官方指定版本的显卡驱动程序，如果驱动程序版本不对，可能导致程序无法运行。

如果要搭建多GPU破解平台的话，最好是使用Linux系统来运行HashCat系列软件，因为在windows下，系统最多只能识别4张显卡。并且，Linux下的VisualCL技术（关于如何搭建VisualCL环境，请参考官方文档[http://hashcat.net/wiki/doku.php?id=vcl_cluster_howto](http://hashcat.net/wiki/doku.php?id=vcl_cluster_howto)），可以轻松的将几台机器连接起来，进行分布式破解作业。 在破解速度上，ATI GPU破解速度最快，使用单张HD7970破解MD5可达到9000M/s的速度，其次为NVIDIA显卡，同等级显卡GTX690破解速度大约为ATI显卡的三分之一，速度最慢的是使用CPU进行破解。

0x02 HashCat软件简介
----------------

* * *

HashCat主要分为三个版本：Hashcat、oclHashcat-plus、oclHashcat-lite。这三个版本的主要区别是：HashCat只支持CPU破解。oclHashcat-plus支持使用GPU破解多个HASH，并且支持的算法高达77种。oclHashcat-lite只支持使用GPU对单个HASH进行破解，支持的HASH种类仅有32种，但是对算法进行了优化，可以达到GPU破解的最高速度。如果只有单个密文进行破解的话，推荐使用oclHashCat-lite。

目前最新的软件版本为HashCat v0.46、oclHashcat-plus v0.15、oclHashcat-lite v0.15。但是经过一段时间的测试，发现有时候版本越高，速度越慢。所以推荐在使用没有问题的情况下，无需升级到最新版本。根据测试，oclHashcat-lite v0.10的运算速度比v0.15的运算速度快20%，所以单个密文破解还是推荐使用oclHashcat-lite v0.10。

0x03 HashCat软件使用
----------------

* * *

HashCat系列软件拥有十分灵活的破解方式，可以满足绝大多数的破解需求，下面我就为大家简单介绍一下。

### 1.指定HASH类型

在HashCat中--hash-type ?参数可以指定要破解的HASH类型，运行hashcat主程序加上--help参数，在`* Generic hash types:`中可以看到各种HASH类型的代号，如图所示： ￼![enter image description here](http://drops.javaweb.org/uploads/images/7390fd4b57bf1185c827da9ae81ba62b63a6a04e.jpg)

不同版本的HashCat所支持的hash类型有所不同，如果没有指定--hash-type参数，那么程序默认为MD5类型。

### 2.指定破解模式

在HashCat中`--attack-mode ?`参数可以可以指定破解模式，软件一共支持5种破解模式，分别为

```
0 Straight（字典破解）
1 Combination（组合破解）
3 Brute-force（掩码暴力破解）
6 Hybrid dict + mask（混合字典+掩码）
7 Hybrid mask + dict（混合掩码+字典）

```

下面为大家介绍两个最常用的破解方式：字典破解和掩码暴力破解。

#### 使用字典破解MD5：

```
oclHashcat-plus64.exe --hash-type 0 --attack-mode 0 {HASH文件} [字典1] [字典2] [字典3]…

```

如：

```
oclHashcat-plus64.exe --hash-type 0 --attack-mode 0 d:md5.txt d:dict1.txt d:dict2.txt

```

字典破解由于受到磁盘和内存速度的影响，速度无法达到GPU的最大运算速度，基本上一个5GB的字典，对于MD5破解来说10分钟内可以跑完。

#### 使用掩码暴力破解SHA1：

```
oclHashcat-plus64.exe --hash-type 100 --attack-mode 3 {HASH文件} [掩码]

```

#### {掩码的设置}

对于掩码，这边需要稍微做一个说明。Hashcat默认的掩码一共有9种，如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/bfe047eb4289f0d1976e9ddebd68a2711ddbca06.jpg)

?l表示a-z，?u表示A-Z，?d表示0-9，?a表示键盘上所有的特殊字符，?s表示键盘上所有的可见字符，?h表示8bit 0xc0-0xff的十六进制，?D表示8bit的德语字符，?F表示8bit的法语字符，?R表示8bit的俄语字符。

那么有同学可能会问了，如果我要用掩码表示小写+数字怎么办呢？这就需要用到自定义字符集这个参数了。软件支持用户最多定义4组字符集，分别用

```
--custom-charset1 [chars]
--custom-charset2 [chars]
--custom-charset3 [chars]
--custom-charset4 [chars]

```

来表示，在掩码中用?1、?2、?3、?4来表示。

比如说我要设置自定义字符集1为小写+数字，那么就加上

```
-- custom-charset1 ?l?d

```

如果要设置自定义字符集2为abcd1234，那么就加上

```
--custom-charset2 abcd1234

```

如果要破解8位的小写+数字，那么需要设置自定义字符集1为

```
--custom-charset1 ?l?d

```

设置掩码为?1?1?1?1?1?1?1?1。 如果已知密码的第一位为数字，长度为8位，后几位为大写+小写，那么需要设置自定义字符集1为

```
--custom-charset1 ?l?u

```

设置掩码为?d?1?1?1?1?1?1?1。

#### {掩码的长度}

对于已知长度的密码，可以使用固定长度的掩码进行破解。比如要破解11位数字，就可以这样写掩码?d?d?d?d?d?d?d?d?d?d?d。

对于想要破解一些未知长度的密码，希望软件在一定长度范围内进行尝试的，可以使用--increment参数，并且使用--increment-min ?定义最短长度，使用--increment-max ?定义最大长度。比如要尝试6-8位小写字母，可以这样写

```
--increment --increment-min 6 --increment-max 8 ?l?l?l?l?l?l?l?l

```

#### {举例}

破解8-11位数字+小写

```
oclHashcat-plus64.exe --hash-type 100 --attack-mode 3 --increment --increment-min 8 --increment-max 11 --custom-charset1 ?l?d d:sha1.txt ?1?1?1?1?1?1?1?1?1?1?1 

```

0x04 HashCat参数优化
----------------

* * *

HashCat本身考虑到系统资源的分配，默认参数下并没有最大化的来使用硬件资源。如果我们想要让破解速度最大化，就需要对一些参数进行配置。

### 1.Workload tuning 负载调优。

该参数支持的值有1,8,40,80,160

```
--gpu-accel 160

```

可以让GPU发挥最大性能。

### 2.Gpu loops 负载微调

该参数支持的值的范围是8-1024（有些算法只支持到1000）。

```
--gpu-loops 1024

```

可以让GPU发挥最大性能。

### 3.Segment size 字典缓存大小

该参数是设置内存缓存的大小，作用是将字典放入内存缓存以加快字典破解速度，默认为32MB，可以根据自身内存情况进行设置，当然是越大越好XD。

```
--segment-size 512

```

可以提高大字典破解的速度。

0x05 结束语
--------

* * *

本文只是简单介绍HashCat的一些常见用法，希望能够让大家更快的学会HashCat的使用。本人刚接触Hashcat不久，如果文章有什么缺点或不足也希望大家能够及时提出，在使用过程当中有什么疑问可以跟帖提问。如果想要更加详细的了解HashCat，请大家参阅官方文档：[http://hashcat.net/wiki/](http://hashcat.net/wiki/)。