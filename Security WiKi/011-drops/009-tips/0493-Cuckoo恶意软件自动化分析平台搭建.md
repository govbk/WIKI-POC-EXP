# Cuckoo恶意软件自动化分析平台搭建

**Author:kernux Topsec α-lab**

0x00 cuckoo概述
=============

* * *

Cuckoo是一款开源的自动化恶意软件分析系统，目前主要用于分析windows平台下的恶意软件，但其框架同时支持Linux和Mac OS。cuckoo能够自动化获取如下信息：

1.  能够跟踪恶意软件进程及其产生的所有进程的win32 API调用记录；
2.  能够检测恶意软件的文件创建、删除和下载；
3.  能够获取恶意软件进程的内存镜像；
4.  能够获取系统全部内存镜像，方便其他工具进行进一步分析；
5.  能够以pacp格式抓取网络数据；
6.  能够抓取恶意软件运行时的截图。

Cuckoo支持分析多种文件格式，包括windows可执行文件，DLL文件，PDF文档，Office文档，恶意URL，HTML文件，PHP文件，CPL文件，VBS，ZIP压缩文件，jar文件，python程序等。这些完全依赖于他的分析模块。

下图是cuckoo的架构图，非常清晰。Cuckoo依赖于下面的虚拟机进行实际的分析，然后通过虚拟网络将分析结果传输给cuckoo host。所以cuckoo的运行至少需要一个虚拟化环境。目前cuckoo能够支持vmware，virtualbox，kvm，qemu，xen，avd等主流虚拟化平台。

![p1](http://drops.javaweb.org/uploads/images/a6ad801337f32d729aded0efa70c5df3d0942763.jpg)

Cuckoo的架构是高度模块化的，只要我们添加不同的分析模块，cuckoo就能够完成不同系统平台下的分析工作。

0x01 环境搭建
=========

* * *

测试环境是host:kali 2.0 x64，guest：windows xp sp3 en。

**2.1 安装**

获取cuckoo，我们从github上获取最新的cuckoo：

```
Git clone https://github.com/cuckoobox/cuckoo.git

```

安装cuckoo依赖的python库：

```
$ sudo apt-get install python python-pip
$ sudo apt-get install mongodb
$ sudo pip install -r requirements.txt

```

此处安装可能会出现问题，是系统所安装的python库与pip安装的库版本不一致导致的，因为系统所安装的python库往往比较旧，而pip安装的库比较新，且pip安装的其他库依赖较新的库，所以导致问题。解决方法是将系统的python库卸载，不过系统的某些python库存在依赖，需要用`dpkg --purge --force-all`包名来强制卸载，然后再用pip来安装即可解决。

```
$ sudo apt-get install tcpdump
$ sudo apt-get install libcap2-bin

```

如果想进行内存镜像分析，需要安装volatility。

```
$ sudo apt-get install volatility

```

启用截图功能，需要Python Image库

```
$ sudo pip install PIL

```

这里我们采用virtualbox虚拟化平台，所以需要下载并安装virtualbox。

**2.2 配置**

软件安装好后，需要先创建一个虚拟机，可以利用virtualbox图形界面进行操作。Cuckoo在运行的时候，需要在host上监听一个地址，用于获取报告信息，而这个地址虚拟机必须能够访问的到。这里采用的网络配置是将虚拟机网卡调整为host-only模式，相当于虚拟机与host之间连接了一根网线。此时，host的网卡列表中会有一个类似vboxnet0的网卡，这就是host与虚拟机之间通信的网卡。虚拟机内部的ip地址可以自己设置，只要跟vboxnet0的地址在一个网段即可。默认情况下vboxnet0是192.168.56.1。虚拟机可以是192.168.56.101。

为了让虚拟机能够正常的访问外网，host还需要进行数据转发，参考官方的命令：

```
iptables -A FORWARD -o eth0 -i vboxnet0 -s 192.168.56.0/24 -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A POSTROUTING -t nat -j MASQUERADE
sysctl -w net.ipv4.ip_forward=1

```

其中第一条命令中的eth0是你host的上网用的真实网卡地址，vboxnet0则是虚拟网卡。

最后一条是开启内核数据转发。

装好虚拟机系统后，为达到最好的兼容效果，需要将windows虚拟机的防火墙，自动更新关闭，然后需要安装python2.7环境。并将cuckoo根目录下`agent/agent.py`复制到虚拟机中。`agent.py`负责虚拟机到主机的数据传输，可以将其添加到startup文件夹下，开机自动启动，如果不想出现黑窗口，可以修改文件名`agent.py`到`agent.pyw`。运行`agent.pyw`后，此时的虚拟机环境基本搭建完成了，当然，如果需要分析office或者pdf等，那么还需要安装这些软件。现在可以创建一个纯净的系统快照了，以备后用。

虚拟机配置完成之后，就是配置cuckoo了。Cuckoo的配置文件在conf目录下，该目录下有很多配置文件，其中：

*   `auxiliary.conf`是辅助配置模块，用于辅助其他功能如sniffer，mitm。这里可以不用配置。
*   `cuckoo.conf`是主要配置文件，最主要的是machinery用于指定我们使用的虚拟机配置文件，默认是virtualbox，该文件同样位于conf目录下，名字是virtualbox.conf。当然我们可以自己定义自己的虚拟机配置文件，并放在conf目录下，命名规则是一样的。另外重要的选项是ip和port，用于指定接收分析结果的服务器。该地址必须能够让虚拟机访问到，一般设置为虚拟网卡的地址，比如上面配置的vboxnet0地址192.168.56.1，端口默认就可以。
*   `memory.conf`是内存镜像配置选项，主要用于Volatility分析，这里可以不用配置。
*   `processing.conf`是结果处理配置模块，其中的配置选项直接影响最终报告的内容，这里可以不用配置。
*   `<machinery>.conf`是指所有的虚拟化配置文件，包括virtualbox、vmware、kvm等。这些文件属于一类文件，在实际的配置当中，我们根据我们的虚拟化环境，只需要配置其中一个即可，同时采用的这个配置文件也必须在cuckoo.conf的machinery字段指定。这里的配置选项都是针对特定虚拟化平台的，很多选项只适用于某些平台。我们采用的是virtualbox.conf，其中mode指定virtualbox的运行模式，path指定VBoxManage的绝对路径，machines指定我们使用的虚拟机的名字，platform指定虚拟机运行的系统平台，ip指定虚拟机的ip地址。
*   `reporting.conf`用于配置报告生成的方式，这里可以不用配置。

最后我们在配置一下cuckoo的web界面。需要开启reporting.conf中的mongodb。然后开启mongodb服务：`systemctl enable mongodb`；`systemctl start mongodb`。现在可以启动web服务`web/manage.py runserver`。服务运行于127.0.0.1:8000。

**2.3 运行**

Python cuckoo.py 运行cuckoo分析系统。如下图：

![p2](http://drops.javaweb.org/uploads/images/8b68048e912c4479f8a1efd976a10691e179630b.jpg)

启动后cuckoo开始等待分析任务。添加分析任务使用根目录下的`utils/`的`submit.py`。具体用法可以看帮助，这里主要介绍利用web界面来添加任务及查看报告。

在浏览器中打开127.0.0.1:8000

![p3](http://drops.javaweb.org/uploads/images/b5436b55320508b84d1a7656a3cdf3499c6bb4f5.jpg)

点击submit添加任务，同时还有一些高级选项，如果需要内存分析，请选中Full Memory Dump。提交后，cuckoo就会开始自动分析，期间virtualbox会启动并运行程序。最终分析结果：

![p4](http://drops.javaweb.org/uploads/images/51f6b316c94af614f9b75a551ba645f1b8306d37.jpg)

最上面就是cuckoo分析的类型，包括静态分析，行为分析，网络分析等。

0x02 结束语
========

* * *

本文主要介绍了cuckoo的基本特性和安装，配置方法。利用cuckoo能够快速的分析恶意程序的部分行为，提高对恶意程序分析的效率。后续文章会继续分析cuckoo的程序结构及模块开发。