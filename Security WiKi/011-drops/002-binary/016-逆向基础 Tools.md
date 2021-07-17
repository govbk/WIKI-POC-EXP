# 逆向基础 Tools

第69章
====

**反汇编器**

### 69.1 IDA

较老的可下载的免费版本:[http://go.yurichev.com/17031](http://go.yurichev.com/17031)

短热键列表(第977页)

第70章
====

**调试器**

70.1 tracer

我用[tracer](http://yurichev.com/)代替调试器。

我最终不再使用调试器是因为我所需要的只是在代码执行的时候找到函数的参数，或者寄存器在某点的状态。每次加载调试器的时间太长，因此我编写了一个小工具tracer。它有控制台接口，运行在命令行下，允许我们给函数下断，查看寄存器状态，修改值等等。

但出于学习的目的更建议在调试器中手动跟踪代码，观察寄存器状态是怎么变化的(比如经典的SoftICE,Ollydbg,Windbg寄存器值发生变化会高亮)，手动修改标志位，数据然后观察效果。

70.2 OllyDbg

非常流行的win32用户态调试器[http://go.yurichev.com/17032](http://go.yurichev.com/17032)短热键列表(第977页)

70.3 GDB

GDB在逆向工程师中并不非常流行，但用起来非常舒适。部分命令（第978页）

第71章
====

**系统调用跟踪**

71.0.1 stace/dtruss

显示当前进程的系统调用(第697页)。比如：

```
# strace df -h
...
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
open("/lib/i386-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0\220\232\1\0004\0\0\0"..., 512) = 512
fstat64(3, {st_mode=S_IFREG|0755, st_size=1770984, ...}) = 0
mmap2(NULL, 1780508, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0xb75b3000

```

Mac OS X 的dtruss也有这个功能。

Cygwin也有strace，但如果我理解正确的话，它只为cygwin环境编译exe文件工作。

第72章
====

**反编译器**

只有一个已知的，公开的，高质量的反编译C代码的反编译器：Hex-Rays

[http://go.yurichev.com/17033](http://go.yurichev.com/17033)

第73章
====

**其他工具**

[Microsoft Visual Studio Express1](http://go.yurichev.com/17034):Visual Studio精简版，方便做简单的实验。部分有用的选项(第978页)

[Hiew](http://go.yurichev.com/17035)：适用于二进制文件小型修改

binary grep:大量文件中搜索常量(或者任何有序字节)的小工具，也可以用于不可执行文件：[GitHub](http://go.yurichev.com/17017)