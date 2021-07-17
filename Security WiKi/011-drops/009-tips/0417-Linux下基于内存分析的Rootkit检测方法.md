# Linux下基于内存分析的Rootkit检测方法

0x00 引言
=======

* * *

某Linux服务器发现异常现象如下图，确定被植入Rootkit，但运维人员使用常规Rootkit检测方法无效，对此情况我们还可以做什么？

![enter image description here](http://drops.javaweb.org/uploads/images/3dff171b07e29644462a42293953593e138efab9.jpg)

图1 被植入Rootkit的Linux服务器

所有暗链的html文件ls均看不到。

使用ls -al 绝对路径，能看到，但无法删除。

这些暗链的uid和gid都很奇特 分别为 2511744398:4043361279 。

对任意文件执行chown 2511744398:4043361279 其表现会和暗链文件相同。

将硬盘nfs挂载到正常系统上，现象无任何变化。

0x01 Rootkit实现方式和检测方法
=====================

* * *

一般来说，Rootkit检测方式有以下几种：

```
1.  可信任Shell——使用静态编译的二进制文件：lsof、stat、strace、last、……
2.  检测工具和脚本：rkhunter, chkrootkit, OSSEC
3.  LiveCD——DEFT、Second Look、 Helix
4.  动态分析和调试：使用gdb根据System.map和vmlinuz image分析/proc/kcore
5.  直接调试裸设备：debugFS

```

在分析这几种检测方法的优劣之前，我们先通过图2了解一下Linux Rootkit的一般实现原理

![enter image description here](http://drops.javaweb.org/uploads/images/9523d2f44b4f7839b902fe834adcf52b9ee18caa.jpg)

图2 Linux中系统命令执行的一般流程

在Ring3层（用户空间）工作的系统命令/应用程序实现某些基础功能时会调用系统.so文件注1。而这些.so文件实现的基本功能，如文件读写则是通过读取Ring0层（内核空间）的Syscall Table注2(系统调用表)中相应Syscall(系统调用)作用到硬件，最终完成文件读写的。

那么如果中了Rootkit，这个流程会发生什么变化呢？下面通过图3来了解一下。

![enter image description here](http://drops.javaweb.org/uploads/images/16586e60c2c8bad0942868479300aa2a6dd3f073.jpg)

图3 Rootkit的一般执行流程

Rootkit篡改了Syscall Table中Syscall的内存地址，导致程序读取修改过的Syscall地址而执行了恶意的函数从而实现其特殊功能和目的。

上图仅仅是列举了一种典型的Rootkit工作流程，通过修改程序读取Syscall的不同环节可以产生不同类型的Rootkit，我们简单罗列一下。

Rootkit部分实现方式：

```
1.  拦截中断-重定向sys_call_table，修改IDT
2.  劫持系统调用-修改sys_call_table
3.  inline hook-修改sys_call，插入jmp指令

```

这部分不是本文的重点，不再赘述。了解了Rootkit实现原理，我们再回过来对比一下常规Rootkit检测方式的优劣。

对于使用静态编译的二进制文件的检测方式，如果Rootkit修改了Syscall，那么这种方法产生的输出也是不可靠的，我们无法看到任何被Rootkit隐藏的东西。

那么如果使用Rootkit检测工具呢，我们简单分析一下rkhunter的检测原理。

在rkhunter脚本文件中，scanrootkit函数部分代码如下：

![enter image description here](http://drops.javaweb.org/uploads/images/ad9e76c7c8e292add7cbc286fad8bcedfa6d4984.jpg)

图4 rkhunter中的scanrootkit函数

注：其安装脚本中定义了以下两个变量

```
RKHTMPVAR="${RKHINST_SIG_DIR}"
RKHINST_SIG_DIR="${RKHINST_DB_DIR}/signatures"

```

![enter image description here](http://drops.javaweb.org/uploads/images/7661df99d5d25e429e37f05dc19758157fb6a89e.jpg)

图5 Signatures目录中的文件列表——Rootkit签名列表

从上面这段代码我们可以看出rkhunter扫描Rootkit调用了3个重要的变量：SCAN_FILES, SCAN_DIRS，SCAN_KSYMS，用于每种Rootkit的检查。

下面的四幅图分别是Adore和KBeast两个Rootkit检测的具体代码。

![enter image description here](http://drops.javaweb.org/uploads/images/397de2a2ed7d30245448a62306aac9ebdca5b43b.jpg)

图6 rkhunter中经典Rootkit Adore的检测流程

![enter image description here](http://drops.javaweb.org/uploads/images/27ba72004dd1696f4de761d922e8d860c3dc6137.jpg)

图7 rkhunter中检测Adore的文件和目录的清单

![enter image description here](http://drops.javaweb.org/uploads/images/0e36d356555eb8e0514f93a24dc3bc9d3fcea83a.jpg)

图8 rkhunter中Rootkit KBeast的检测流程

![enter image description here](http://drops.javaweb.org/uploads/images/3c38c28f8ddb072f81788b86706052cb6e968395.jpg)

图9 rkhunter中检测KBeast的文件和目录的清单

根据以上分析，我们可以看出rkhunter仅仅是检查已知Rootkit组件默认安装路径上是否存在相应文件，并比对文件签名（signature）。这种检测方式显然过于粗糙，对修改过的/新的Rootkit基本无能为力。

而另一款流行的Rootkit检测工具chkrootkit，其LKM Rootkit检测模块源文件为chkproc.c，最后更新日期为2006.1.11日。检测原理与rkhunter大致相似，也主要基于签名检测并将ps命令的输出同/proc目录作比对。在它的FAQ中Q2的回答也印证了我们的结论。

![enter image description here](http://drops.javaweb.org/uploads/images/799381845bd883a829d451055cf0c703fabe57ad.jpg)

图10 chkrootkit的FAQ之Q2

分析了常见的Rootkit检测工具的实现原理，我们再看一下使用LiveCD检测这种方式有哪些局限性。

使用LiveCD意味着使用一纯净的光盘操作系统挂载原有存储对可疑文件做静态分析/逆向，以便了解Rootkit执行逻辑，依赖的so/ko文件有哪些，加载的配置文件是什么。那么，如果事先没有找到一些Rootkit的相关文件，直接对整个文件系统做逐一排查，无疑是一个繁冗的过程。而且，这种方式的使用前提是应急响应人员必须能物理接触服务器，这对托管在机房的环境很不方便。实际上，使用LiveCD在Rootkit清除或司法取证环节上更为常见，而不是其前置环节。

根据以上分析，我们简单总结一下Rootkit检测方式的效果，见下表.

Rootkit检测方式对比

| 检测方式 | 局限/缺陷 |
| --- | :-: |
| 使用静态编译的二进制文件 | 工作在用户空间，对Ring0层的Rootkit无效。 |
| 工具rkhunter,chkrootkit | 扫描已知Rootkit特征，比对文件指纹，检查/proc/modules，效果极为有限。 |
| LiveCD:DEFT | Rootkit活动进程和网络连接等无法看到，只能静态分析。 |
| GDB动态分析调试 | 调试分析/proc/kcore，门槛略高，较复杂。不适合应急响应。 |
| DebugFS裸设备直接读写 | 不依赖内核模块，繁琐复杂，仅适合实验室分析。 |

既然常规的Rootkit检测方法有这样那样的缺陷，那有没有更好的检测方式呢?

下面我们详细介绍一下基于内存分析Rootkit检测方法。

0x02 基于内存检测和分析Rootkit
=====================

* * *

Rootkit难以被检测，主要是因为其高度的隐匿特性，一般表现在进程、端口、内核模块和文件等方面的隐藏。但无论怎样隐藏，内存中一定有这些方面的蛛丝马迹，如果我们能正常dump物理内存，并通过debug symbols.和kernel`s data structure来解析内存文件，那么就可以对系统当时的活动状态有一个真实的“描绘”，再将其和直接在系统执行命令输出的“虚假”结果做对比，找出可疑的方面。下面简述一下部分原理。

1. 基于内存分析检测进程
-------------

* * *

在Linux系统中查看进程一般执行的是ps –aux命令，其实质是通过读取/proc/pid/来获取进程信息的。而在内核的task_struct注3(进程结构体)中，也同样包含进程pid、 创建时间、映像路径等信息。也就是说每个进程的相关信息都可以通过其对应task_struct内存地址获取。而且，每个task_struct通过next_task和prev_task串起成为一个双向链表，可通过for_each_task宏来遍历进程。基于这个原理我们可以先找到PID为0的init_task symobol（祖先进程）的内存地址，再进行遍历就能模拟出ps的效果。部分细节可参考下图。

![enter image description here](http://drops.javaweb.org/uploads/images/632b9cfabf086b3df73a69d648c42f2b55fd63e1.jpg)

图11 内核中的task_struct

此外，Linux内核中有一个东西叫PID Hash Chain，如图12所示，它是一个指针数组,每个元素指向一组pid的task_struct链表中的元素 ，能够让内核快速的根据pid找到对应的进程。所以分析pid_hash也能用来检测隐藏进程和获取相应进程信息,并且效率更高。

![enter image description here](http://drops.javaweb.org/uploads/images/b69296cf472cfc01c21e0fb58b79f89b937e006e.jpg)

图12 内核中的PID Hash Chain

2. 基于内存分析Process Memory Maps（进程映射）
----------------------------------

* * *

在task_struct中，mm_struct注4描述了一个进程的整个虚拟地址空间，进程映射主要存储在一个vm_area_struct的结构变量mm_rb注5和mmap 中，大致结构如下图所示

![enter image description here](http://drops.javaweb.org/uploads/images/0eeed1db7840f2b078854cc52123a45ea208acaf.jpg)

图13 mm_struct(内存描述符)的结构

每一个vm_area_struct节点详细记录了VMA（virtual memory area）的相关属性，比如vm_start（起始地址）、vm_end（结束地址）、vm_flags（访问权限）以及对应的vm_file（映射文件）。从内存中我们得到信息就相当于获得了/proc//maps的内容。

3. 基于内存分析检测网络连接和打开的文件(lsof)
---------------------------

* * *

Linux中的lsof（List Open Files）实质是读取/proc/pid/文件夹中的信息。而这些信息通过task_struct也能获取。

![enter image description here](http://drops.javaweb.org/uploads/images/a74ba3a4361b69e325731a6e5126fb5a59228371.jpg)

图14 内核中的task_struct细节

task_struct的structure（数据结构）中files指向files_struct(文件结构体),用于表示当前进程打开的文件表。其structure中有一个fd_array(文件描述符数组)，数组中的每个元素fd（File Descriptor文件描述符），都代表一个进程打开的文件。而每个File Descriptor的structure中又包含了目录项dentry，文件操作f_ops等等。这些足以让我们找到每个进程打开的文件。

另，当某个文件的f_op structure 成员是socket_file_ops 或者其dentry.d_op 为sockfs_dentry_operations时，则可以将其转为为相应的inet_sock structure，最终得到相应的网络信息。

4. 基于内存分析检测bash_history
-----------------------

* * *

后渗透测试阶段，攻击者常使用history –c命令来清空未保存进.bash_history文件的命令历史。而在Rootkit中，通过配置HISTSIZE = 0 或将HISTFILE = /dev/null也是一种常见的隐藏命令历史的方法。对于后者，由于bash进程的history也记录在相应的MMAP中（其对应的宏定义为 HISTORY_USE_MMAP注6），通过history_list()函数相应的mmap数据也可以还原其历史记录。

![enter image description here](http://drops.javaweb.org/uploads/images/2d46facd633303f0676e48949ec3d24cf83c507f.jpg)

图15 bash 4.0源码histfile.c文件中history_do_write函数功能图示.

5. 基于内存分析检测内核模块
---------------

* * *

通过遍历module list上所有的struct module来检查Rootkit是一种代替lsmod命令的的方法。但是如果Rootkit把自己的LKM从module list摘除，但仍加载在内存中，这种方法就不起作用了。

![enter image description here](http://drops.javaweb.org/uploads/images/977b1b5767fd0d0eae731eed7aa22c8ee8900bba.jpg)

图16 内核中Kernel Module List

不过，Rootkit很难在/sys/module/目录中隐藏，所以我们仍可通过遍历Sysfs文件系统来检查隐藏的内核模块。

6. 基于内存分析检测process credentials
------------------------------

* * *

在2.6.29内核的以前版本，Rootkit可以将用户态的进程通过设置其effective user ID和effective group ID为0（root）进行特权提升。而在后面的版本中，kernel引入了'cred' structure。为此，Rootkit与时俱进，通过设置同某个root权限进程一样的'cred' structure 来应对这种改进。所以通过检查所有进程的'cred' structure 能更好的发现活动的Rootkit。

7. 基于内存分析检测Rootkit的流程
---------------------

* * *

限于篇幅，本文不再介绍更多的原理和细节，简单总结一下这种方法的的大致流程。

```
1 制作目标Linux服务器的profile 
2 Dump完整的物理内存 
3 使用profile解析内存映像文件，输出系统信息

```

![enter image description here](http://drops.javaweb.org/uploads/images/c9bc1f17926a54ca8671d33c7f61f127a295fe64.jpg)

图17 基于内存分析检测Rootkit原理示意图

0x03 总结与实践
==========

* * *

基于内存分析检测Rootkit的方法比对常规的检测方法有较大的优势，但它不是万能的，如果被Bootkit之类的高级Rootkit干扰，Dump的物理内存不正确或不完整，后面的步骤就是空中阁楼。另外也要确保制作Profile时需要的System.map没有被篡改或者直接使用同一内核版本号的Linux发行版中的文件来替代。

通过内存分析检测Rootkit的工具目前不是很多，各有优劣。司法取证领域的开源工具Volatility是这方面的佼佼者，推荐各位同仁使用并贡献代码。对内存检测分析技术感兴趣的同学，欢迎和我交流讨论。EOF

0x04 附注
=======

* * *

```
注1：Linux中的so（shared object）文件近似于Windows下的dll（dynamic link library）文件，均用来提供函数和资源。
注2：Syscall Table一般可以通过查看/boot/System.map文件来获取其内容
注3： Process Descriptor：To manage processes, the kernel must have a clear picture of what each process is doing. It must know, for instance, the process's priority, whether it is running on a CPU or blocked on an event, what address space has been assigned to it, which files it is allowed to address, and so on. This is the role of the process descriptor — a task_struct type structure whose fields contain all the information related to a single process.
注4：mm_struct概要了相应程序所使用的内存信息，比如所有段（segment）、各个主要段的始末位置、使用常驻内存的总大小等等，一般称之为memory descriptor（内存描述符）
注5：mm_rb：Red black tree of mappings.
注6：HISTORY_USE_MMAP定义见bash-4.0-src/lib/readline/histfile.c 475行，具体可参见http://sourcecodebrowser.com/bash/4.0/histfile_8c_source.html.

```

0x05 参考文献
=========

* * *

http://www.rootkitanalytics.com/kernelland/linux-kernel-rootkit.php https://media.blackhat.com/bh-us-11/Case/BH_US_11_Case_Linux_Slides.pdf https://www.safaribooksonline.com/library/view/understanding-the-linux/0596005652/ch03s02.html http://www.wowotech.net/linux/19.html http://www.lenky.info/archives/2012/04/1424 http://code.google.com/p/volatility/