# 通过QEMU 和 IDA Pro远程调试设备固件

0x00 背景与简介
==========

* * *

这篇文章主要讲了如何在模拟环境下调试设备固件。

作者：Zach Cutlip

原文链接：http://shadow-file.blogspot.gr/2015/01/dynamically-analyzing-wifi-routers-upnp.html。

在分析嵌入式设备的固件时，只采用静态分析方式通常是不够的。你需要实际执行你的分析目标来观察它的行为。在嵌入式Linux设备的世界里，很容易把一个调试器放在目标硬件上进行调试。如果你能在自己的系统上运行二进制文件，而不是拖着硬件做分析, 将会方便很多。这就需要用QEMU进行仿真。

接下来的一系列文章，我将专注于Netgear的一个比较流行的无线路由器，对其UPnP守护进程进行逆向分析。这篇文章将介绍如何在系统仿真环境下运行守护进程，以便可以通过调试器对其进行分析。

0x01 先决条件
=========

* * *

首先，建议你读一下我的工作区以及所使用的工具的描述。这里是链接http://shadow-file.blogspot.com/2013/12/emulating-and-debugging-workspace.html。

你需要一个MIPS Linux的模拟环境。对于这一点，建议读者查看我之前的搭建QEMU的帖子。http://shadow-file.blogspot.com/2013/05/running-debian-mips-linux-in-qemu.html

你还需要一个MIPS Linux的交叉编译器。我不会详细描述交叉编译器的建立过程，因为它们一团糟。有时候，你需要较旧的工具链，而其他时候，你需要较新的工具链。最好使用uClibc buildroot project（http://buildroot.uclibc.org/）同时建立big endian和little endian的MIPS Linux工具链。除此之外，每当我发现其他交叉编译工具链时，我都会保存他们。类似D-Link和Netgear公司发布GPL版本tarballs是旧工具链的好来源。

一旦你有了目标架构的交叉编译工具链，你需要为目标建立GDB调试器。你至少需要适合目标架构的被静态编译的gdbserver。如果要使用GDB进行远程调试，你需要编译GDB，以便在你的本地机器架构（如X86-64）上运行，来对目标架构（如MIPS或mipsel体系结构）进行调试。同样，我也不会去讨论这些工具的构建，如果你建立了你的工具链，这应该很容易了。

后面我将描述如何使用IDA Pro来进行远程调试。但是，如果你想使用gdb，可以看看我的MIPS gdbinit文件：https://github.com/zcutlip/gdbinit-mips

0x02 模拟一个简单的二进制
===============

* * *

假设你已经建立了上述工具，并能正常工作，你现在应该能够通过SSH进入您的模拟MIPS系统。正如我在Debian MIPS QEMU文章中所述，我喜欢连接QEMU的接口到VMWare的NAT接口，这样就能够用我的Mac通过SSH来接入，而不需要先登陆我的Ubuntu虚拟机。这也可以让我通过NFS将我的Mac工作区挂载到QEMU系统。这样，无论我工作在主机环境中，或是Ubuntu中，还是在QEMU中，我都在用相同的工作区。

```
zach@malastare:~ (130) $ ssh root@192.168.127.141
root@192.168.127.141's password:
Linux debian-mipsel 2.6.32-5-4kc-malta #1 Wed Jan 12 06:13:27 UTC 2011 mips

root@debian-mipsel:~# mount
/dev/sda1 on / type ext3 (rw,errors=remount-ro)
malastare:/Users/share/code on /root/code type nfs (rw,addr=192.168.127.1)
root@debian-mipsel:~#cd code
root@debian-mipsel:~/code#

```

一旦登陆到模拟系统，cd到从设备的固件中提取的文件系统中。你应该能够chroot到固件的根文件系统。需要使用chroot，因为目标二进制是和固件的库链接的，很可能不能跟Debian的共享库一起工作。

```
root@debian-mipsel:~#cd code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs/
root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#file ./bin/ls
./bin/ls: symbolic link to `busybox'
root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#file ./bin/busybox
./bin/busybox: ELF 32-bit LSB executable, MIPS, MIPS32 version 1 (SYSV), dynamically linked (uses shared libs), stripped
root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#chroot . /bin/ls -l /bin/busybox
-rwxr-xr-x    1 10001    80         276413 Sep 20  2012 /bin/busybox
root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#

```

在上面的例子中，我已切换到所提取的文件系统的根目录中。然后使用file命令，我了解到busybox是little endian MIPS可执行文件。然后，chroot到提取根目录，并运行bin/ls，它是busybox的符号链接。

如果试图简单的通过“chroot .”来地启动一个shell，将无法正常工作。因为你的默认shell是bash，而大多数嵌入式设备没有bash。

root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#chroot . chroot: failed to run command `/bin/bash': No such file or directoryroot@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#

相反，你可以chroot并执行bin / sh：

```
root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#chroot . /bin/sh

BusyBox v1.7.2 (2012-09-20 10:26:08 CST) built-in shell (ash)
Enter 'help' for a list of built-in commands.

#
#
#exit
root@debian-mipsel:~/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs#

```

0x03 硬件解决方法
===========

* * *

即使有了必要的工具，建立了仿真环境且工作正常，你仍然可能遇到障碍。虽然QEMU在模拟核心芯片组包括CPU上都做的很不错，但是QEMU往往不能提供你想运行的二进制程序需要的硬件。如果你试图模仿一些简单的像/bin/ls的程序，通常能够正常工作。但更复杂的东西，如肯定有特定的硬件依赖的UPnP守护程序，QEMU就不能够满足。尤其对于管理嵌入式系统硬件的程序更是这样，例如打开或关闭无线适配器。

你将遇到的最常见问题是在运行系统服务，如Web服务器或UPnP守护进程时，缺乏NVRAM。非易失性RAM通常是包含配置参数的设备快速存储器的一个分区。当一个守护进程启动时，它通常会尝试查询NVRAM，获取其运行时配置信息。有时一个守护进程会查询NVRAM的几十甚至上百个参数。

为了解决在模拟条件下缺乏NVRAM的问题，我写了一个叫nvram-faker的库。当你运行二进制程序时，应该使用LD_PRELOAD对nvram-faker库进行预加载。它会拦截通常由libnvram.so提供的nvram_get（）调用。nvram-faker会查询你提供的一个INI风格的配置文件，而不是试图查询NVRAM。

附带的README提供更完整的说明。这里有一个链接：https://github.com/zcutlip/nvram-faker

即使解决了NVRAM问题，该程序可能会假设某些硬件是存在的。如果硬件不存在，该程序可能无法运行，或者即便它运行了，行为可能也与在其目标硬件上运行时有所不同。在这种情况下，你可能需要修补二进制文件。采用二进制补丁的情况各不相同。这取决于期望什么硬件，以及它不存在时的行为是什么。如果硬件缺失，你可能需要修补一个被执行到的条件分支。也可能需要修补针对特殊设备的ioctl（）调用，如果你想将其替代为针对常规文件的读取和写入时。这里我将不谈论修补的细节，但在我的BT HomeHub文章以及44CON的相应讲座中进行了讨论。

这里是这些资源的链接：http://shadow-file.blogspot.com/2013/09/44con-resources.html

0x04 附加调试器
==========

* * *

一旦在QEMU中运行了二进制程序，就可以附加调试器了。当然你需要gdbserver。同样，这个工具应该适合目标架构并被静态编译，因为你会在chroot下运行它。你需要将它复制到提取的文件系统的根目录中。

```
# ./gdbserver
Usage: gdbserver [OPTIONS] COMM PROG [ARGS ...]
gdbserver [OPTIONS] --attach COMM PID
gdbserver [OPTIONS] --multi COMM

COMM may either be a tty device (for serial debugging), or
HOST:PORT to listen for a TCP connection.

Options:
  --debug               Enable general debugging output.
--remote-debug        Enable remote protocol debugging output.
--version             Display version information and exit.
  --wrapperWRAPPER --  Run WRAPPER to start new programs.
  --once                Exit after the first connection has closed.
#

```

你可以将gdbserver附加到正在运行的进程，或者用它来直接执行二进制程序。如果你需要调试只发生一次的初始化程序，你可以选择后者。

另一方面，你可能要等到守护进程被创建。据我所知没有办法让IDA跟踪创建的进程（forked processes）。你需要单独的附加到它们。如果采用这种方式，你可以在chroot外，附加到已经运行的进程。

以下shell脚本将在chroot下执行upnpd。如果DEBUG设置为1，它会附加在upnpd上，并在1234端口上暂停等待远程调试会话。

```
ROOTFS="/root/code/wifi-reversing/netgear/r6200/extracted-1.0.0.28/rootfs"
chroot$ROOTFS /bin/sh -c "LD_PRELOAD=/libnvram-faker.so /usr/sbin/upnpd"

#Give upnpd a bit to initialize and fork into the background.
sleep 3;

if [ "x1" = "x$DEBUG" ];
then

$ROOTFS/gdbserver --attach 0.0.0.0:1234 $(pgrepupnpd)
fi

```

你可以在recvfrom（）调用之前创建一个断点，然后当你向upnpd发送M-SEARCH包时，验证调试器断点。

![enter image description here](http://drops.javaweb.org/uploads/images/59578c6480292378ed66a2d7d5ee14fac1be1a25.jpg)

然后，在IDA的Debugger菜单中的Process选项中设置“主机名”为你的QEMU系统的IP地址，并设置端口为gdbserver正在监听的端口。我用的是1234。

![enter image description here](http://drops.javaweb.org/uploads/images/89da81efe5a1ba46285e4c3d91545d92add09402.jpg)

接受设置，然后通过IDA的CTRL+8热键连接到远程调试会话。再次按Ctrl+8继续执行。你应该能够发送一个M-SEARCH包[1](http://static.wooyun.org/drops/20150106/20150106134849501312e25df697d3a76e857f3228a690e9d6e49d681ff.rar)，可以看到调试器命中断点。

![enter image description here](http://drops.javaweb.org/uploads/images/eb5666489c6626336989adf5e332ccecf7eade71.jpg)

显然还有很多需要探索，也会遇到有很多这里未提及的情况，但希望这可以让你开始。

我推荐Craig Heffner用于UPnP分析的miranda工具：https://code.google.com/p/miranda-upnp/