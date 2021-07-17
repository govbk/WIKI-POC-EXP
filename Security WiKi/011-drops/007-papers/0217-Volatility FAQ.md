# Volatility FAQ

出于检测Linux平台下Rootkit的需要,试了一下很早以前知道,但一直没有用过的工具Volatility.考虑国内服务器的现实情况,选择CentOS 5.5作为实验平台. 一个工具的使用在我想来应该是相当简单的,但实际情况相当曲折,……经过很多实践和教训,写了一些笔记,整理为FAQ,遂成此文,以供同好交流讨论.

0x01 正文
-------

* * *

**Q1: Volatility 是什么?**

A1: Volatility是一个Python编写的跨平台,用于内存分析的法证工具,其目的是为了在数据犯罪中提取易失性数据 ,也可以用来进行Rootkit的检测和协助清除.

* * *

**Q2:其大致原理是什么?**

A2: Linux的System.map文件列出了详细的系统调用（syscall）,而kernel-header源码通过dwarfdump生成的module.dwarf文件中会包含很多kernel‘s data structure,将以上2个文件打包为profile.再用这个profile解析dump下来的物理内存,就很容易找到植入Rootkit的机器活动时的进程(linux_psaux)、网络通信(linux_netstat)、活动文件(linux_lsof)、驱动模块(linux_lsmod)等等.

* * *

**Q3: CentOS 5X中为运行volatility而安装了python2.6,导致依赖python2.4的yum无法运行,如何处理?**

A3: 编译安装Python2.6后执行以下操作:

```
#mv /usr/bin/python /usr/bin/python2.4
#ln -s /usr/local/bin/python2.6 /usr/bin/python
#vi /usr/bin/yum

```

将文件开始的#!/usr/bin/python改#!/usr/bin/python2.4

* * *

**Q4:执行python vol.py,报错提示**

```
Volatile Systems Volatility Framework 2.3.1 \***| Failed to import volatility.plugins.registry.registryapi (ImportError: No module named Crypto.Hash)

```

A4: Volatility需要pycrypto的支持以便进行Hash运算

```
#yum install pycrypto

```

* * *

**Q5:执行yum install pycrypto后,Python仍提示**

```
Failed to import volatility.plugins.registry.registryapi (ImportError: No module named Crypto.Hash)

```

A5: 打印Crypto lib库文件路径,确认python2.7能够import Crypto库.

```
#python
import Crypto
import os
print(Crypto.__file__);
print (dir(Crypto));
print(os.listdir(os.path.dirname(Crypto.__file__)))

```

提示无法导入Crypto库,在python2.4中打印Crypto成功,那就

```
#cp -ivR  /usr/lib/python2.4/Crypto/  /usr/lib/python2.7/site-packages/

```

* * *

**Q6:执行python vol.py后提示**

```
RuntimeWarning: Python C API version mismatch for module Crypto.Hash.MD4: This Python has API version 1013, module Crypto.Hash.MD4 has version 1012.from Crypto.Hash import MD5, MD4

```

A6: yum或apt安装的pycrypto版本问题,实际不影响使用,追求完美就换版本.

```
#wget –v  https://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.6.1.tar.gz
#tar zxvf pycrypto-2.6.1.tar.gz
#python setup.py install
#ll /usr/local/lib/python2.7/site-packages/Crypto/

```

* * *

**Q7: volatility.可以正常使用了,该开始制作profile,那么profile如何创建?**

A7: 每个Linux发行版的不同内核都需要单独创建一个profile,基本上不通用,示例如下:

```
#cd volatility/tools/linux
#make
#head module.dwarf
#zip volatility/volatility/plugins/overlays/linux/Ubuntu1204.zip volatility/tools/linux/module.dwarf /boot/System.map-3.2.0-23-generic 

```

* * *

**Q8:CentOS 5X似乎默认没有dwarfdump.**

A8: CentOS没有能提供dwarfdump的源,但volatility官方提示Fedora repository的源可以提供,只要执行yum install elfutils-libelf-devel"就可以.但不幸的是,安装了elfutils-libelf-devel,也找不到dwarfdump.所以还是自力更生吧

```
#wget -v http://www.prevanders.net/libdwarf-20140519.tar.gz  //官网下载最新版本
#./configure
#make dd
//You may need to be root to do the following copy commands
#cp dwarfdump/dwarfdump      /usr/local/bin
#cp dwarfdump/dwarfdump.conf /usr/local/lib

```

* * *

**Q9: CentOS 5X没有对应版本的内核头文件（kernel-headers）,无法编译module.dwarf?**

A9:

```
#yum install kernel-headers-$(uname -r) kernel-devel-$( uname -r) –y  //CentOS
#apt-get install linux-headers-`uname -r`  //Ubuntu

```

如果软件源中没有匹配的版本,那就手动下载安装 一般还在支持的版本可在http://pkgs.org/download/kernel-headers#下载 否则,只能自行google了.

* * *

**Q10: profile顺利制作完成,开始dump内存.但是执行以下命令：**

```
#dd if=/dev/mem of=/tmp/ram.dump bs=1MB count=1024 

```

**dump的内存只有1MB,而非1G.**

A10: Linux Kernel 2.6.x某个版本后开始对内存访问做了保护,无法dump出完整内存.可使用第三方工具Lime / fmem等来dump内存.

* * *

**Q11: Lime源码编译安装后只生成一个ko驱动文件,没有ELF文件,怎么dump内存?**

A11:

```
#insmod lime.ko “path=/tmp/mem.lime format=lime”  //加载驱动就是正确使用方法

```

* * *

**Q12: lime在ubuntu/debian的机器上使用正常,为什么在CentOS 上提示错误**

```
#insmod lime.ko “path=/tmp/mem.lime format=lime”
insmod: error inserting 'lime.ko': -1 Unknown symbol in module

```

A12: CentOS 下insmod命令的参数不接受双引号,去掉即可,即执行insmod lime.ko path=/tmp/mem.lime format=lime 就好.

* * *

**Q13: profile和dump内存都搞定了,先调用volatility看一下内存中的网络连接,在CentOS执行**

```
#vol -f /tmp/centos.lime --profile=LinuxCentOS510.zip   linux_netstat 

```

**提示**

```
Volatility Foundation Volatility Framework 2.3.1
ERROR   : volatility.addrspace: Invalid profile LinuxCentOS510.zip selected

```

A13: 难道profile后面需要接绝对路径,试了一下仍不行,再次翻阅英文文档,原来profile文件创建后被放在指定的目录volatility/plugins/overlays/linux/中,主程序vol.py启动时,会读取这个目录下的profile文件并自动为其赋予一个新名称,使用这个新名称才能正常调用profile. 查询已有的profile名称的命令为:

```
#vol --info |grep Linux 
LinuxCentOS505x64 - A Profile for Linux CentOS510 x64
linux_banner            - Prints the Linux banner information
linux_yarascan          - A shell in the Linux memory image

```

所以正确调用volatility插件的命令应该为:

```
#vol -f /tmp/centos.lime --profile=LinuxCentOS510x64 linux_netstat

```

* * *

**Q14: 在CentOS 5X_64上执行**

```
#vol -f /tmp/centos.lime --profile=LinuxCentOS510x64 linux_netstat

```

**错误提示:**

```
No suitable address space mapping found

```

A14: 此问题涉及的相关源码在`./volatility/plugins/overlays/linux/linux.64.py`中.

```
#vi linux64.py
class VolatilityDTB(obj.VolatilityMagic):
    """A scanner for DTB values."""
    def generate_suggestions(self):
        """Tries to locate the DTB."""
        profile = self.obj_vm.profile
        yield profile.get_symbol("init_level4_pgt") - 0xffffffff80000000

```

出现问题的可能原因: 在CentOS_X64的的 2.6.18.x kernel中,当内核编译时,置CONFIG_RELOCATABLE=y.物理内存的前2MB都被保留,获取DTB （physical address)时,offset因此需要额外增加0x200000（2M）.即DTB的地址=(“init_level4_pgt”) - 0xffffffff80000000（2G）-0x200000(2M) 所以我们需要对代码作如下修改:

```
#cd ../volatility/plugins/overlays/linux
#vi linux.py

```

修改第1000行将shift = 0xffffffff80000000改为shift = 0xffffffff7fe00000

```
#vi linux64.py

```

同时修改linux64.py的第38行 将

```
yield profile.get_symbol("init_level4_pgt") - 0xffffffff80000000

```

改为

```
yield profile.get_symbol("init_level4_pgt") - 0xffffffff7fe00000

```

再次执行命令,一切正常,Over.

* * *

**Q15: volatility对Linux内核版本有要求吗?适用范围?**

A15: volatility当前最新版本2.3.1支持

```
32-bit Linux kernels 2.6.11 to 3.5    
64-bit Linux kernels 2.6.11 to 3.5    
OpenSuSE, Ubuntu, Debian, CentOS, Fedora, Mandriva, etc

```

其它系统:

```
Windows 32-bit Windows XP Service Pack 2 and 3 
32-bit Windows 2003 Server Service Pack 0, 1, 2 
32-bit Windows Vista Service Pack 0, 1, 2 
32-bit Windows 2008 Server Service Pack 1, 2 
32-bit Windows 7 Service Pack 0, 1 
64-bit Windows XP Service Pack 1 and 2 
64-bit Windows 2003 Server Service Pack 1 and 2 
64-bit Windows Vista Service Pack 0, 1, 2 
64-bit Windows 2008 Server Service Pack 1 and 2 
64-bit Windows 2008 R2 Server Service Pack 0 and 1 
64-bit Windows 7 Service Pack 0 and 1 
Mac OSX (new) 32-bit 10.5.x Leopard (the only 64-bit 10.5 is Server, which isn't supported) 
32-bit 10.6.x Snow Leopard 
64-bit 10.6.x Snow Leopard 
32-bit 10.7.x Lion 
64-bit 10.7.x Lion 
64-bit 10.8.x Mountain Lion (there is no 32-bit version) 

```

0x03 题外
-------

* * *

为方便启动volatility. 可执行

`#ln -s /pentoo/volatility-2.3.1/vol.py /usr/bin/vol`