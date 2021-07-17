# strace

当渗透测试人员拿到shell后，如果要进一步渗透，信息收集是重中之重，内网渗透的深入程度取决于信息收集的深度，内网渗透的本质就是信息收集，而登录凭证的收集是信息收集的重点方向。关于linux系统下登录凭证收集的文章多为翻查文件。本文将研究linux系统下的通过调试程序的方法，跟踪进程数据的方式收集登录凭证。

strace是linux中的调试工具，可通过附加到进程来调试正在运行的进程，strace记录一个正在运行的程序正在执行的系统调用以及参数。我们可以通过这种方式来跟踪任何进程数据，比如sshd ssh su sudo等进程数据来获取登录凭证。

例如，如果一个应用程序（例如Pidgin）遭到入侵，攻击者就有可能附加到其他正在运行的进程（例如Firefox，SSH会话，GPG代理等）以提取其他凭证并继续扩大范围，无需借助用户协助的网络钓鱼就可以进行攻击。

### 安装strace

```bash
# 能出网
yum install strace -y
apt install strace -y
# 不能出网
上传对应安装包，手工安装，或者编译安装

```

### strace使用条件

Linux Kernel 3.4及更高版本支持完全限制或禁用ptrace的功能。这可以通过使用sysctl将kernel.yama.ptrace_scope设置为1、2或3来完成。默认情况下，大多数发行版都将其设置为1。根据Linux Kernel Yama Documentation，这些数字映射到以下权限：

```
0-经典ptrace权限：进程可以将PTRACE_ATTACH传递给任何其他进程，只要它是可转储的（即没有转换uid，没有特权启动或没有调用prctl（PR_SET_DUMPABLE ...）。同样，PTRACE_TRACEME为不变。

1-受限制的ptrace：进程必须具有预定义的关系下一个它想调用PTRACE_ATTACH。默认情况下，当上面的关系时，这种关系只是其后代的关系也符合经典标准。要改变关系，下级可以调用prctl（PR_SET_PTRACER，debugger，...）进行声明允许的调试器PID调用劣质的PTRACE_ATTACH。使用PTRACE_TRACEME不变。

2-仅限管理员附加：只有具有CAP_SYS_PTRACE的进程才能使用ptrace，通过PTRACE_ATTACH，或通过子级调用PTRACE_TRACEME。

3-没有连接：任何进程都不能将ptrace与PTRACE_ATTACH一起使用，也不能通过PTRACE_TRACEME。设置后，该sysctl值将无法更改。

```

这样可以通过运行`sysctl kernel.yama.ptrace_scope=3`在系统上禁用ptrace。但是，这可能会破坏正在运行的其他程序。例如，Wine在禁用ptrace的情况下无法正常工作。我建议您测试非生产服务器，并验证其所有功能在未启用ptrace的情况下能否正常运行。禁用ptrace还可以阻止某些调试功能。

**查看修改系统strace配置**

```bash
# 查看
cat /proc/sys/kernel/yama/ptrace_scope
# 修改
echo 0 > /proc/sys/kernel/yama/ptrace_scope 或者 sysctl kernel.yama.ptrace_scope=0
# 当kernel.yama.ptrace_scope的值设置为3后，必须重启系统后才能更改

```

### strace语法

```bash
-c 统计每一系统调用的所执行的时间,次数和出错的次数等.
-d 输出strace关于标准错误的调试信息.
-f 跟踪由fork调用所产生的子进程.
-ff 如果提供-o filename,则所有进程的跟踪结果输出到相应的filename.pid中,pid是各进程的进程号.
-F 尝试跟踪vfork调用.在-f时,vfork不被跟踪.
-h 输出简要的帮助信息.
-i 输出系统调用的入口指针.
-q 禁止输出关于脱离的消息.
-r 打印出相对时间关于,,每一个系统调用.
-t 在输出中的每一行前加上时间信息.
-tt 在输出中的每一行前加上时间信息,微秒级.
-ttt 微秒级输出,以秒了表示时间.
-T 显示每一调用所耗的时间.
-v 输出所有的系统调用.一些调用关于环境变量,状态,输入输出等调用由于使用频繁,默认不输出.
-V 输出strace的版本信息.
-x 以十六进制形式输出非标准字符串
-xx 所有字符串以十六进制形式输出.
-a column 设置返回值的输出位置.默认 为40.
-e expr 指定一个表达式,用来控制如何跟踪.格式：[qualifier=][!]value1[,value2]...
qualifier只能是 trace,abbrev,verbose,raw,signal,read,write其中之一.value是用来限定的符号或数字.默认的 qualifier是 trace.感叹号是否定符号.例如:-eopen等价于 -e trace=open,表示只跟踪open调用.而-etrace!=open 表示跟踪除了open以外的其他调用.有两个特殊的符号 all 和 none. 注意有些shell使用!来执行历史记录里的命令,所以要使用\\.
-e trace=set 只跟踪指定的系统 调用.例如:-e trace=open,close,rean,write表示只跟踪这四个系统调用.默认的为set=all.
-e trace=file 只跟踪有关文件操作的系统调用.
-e trace=process 只跟踪有关进程控制的系统调用.
-e trace=network 跟踪与网络有关的所有系统调用.
-e strace=signal 跟踪所有与系统信号有关的 系统调用
-e trace=ipc 跟踪所有与进程通讯有关的系统调用
-e abbrev=set 设定strace输出的系统调用的结果集.-v 等与 abbrev=none.默认为abbrev=all.
-e raw=set 将指定的系统调用的参数以十六进制显示.
-e signal=set 指定跟踪的系统信号.默认为all.如 signal=!SIGIO(或者signal=!io),表示不跟踪SIGIO信号.
-e read=set 输出从指定文件中读出 的数据.例如: -e read=3,5
-e write=set 输出写入到指定文件中的数据.
-o filename 将strace的输出写入文件filename
-p pid 跟踪指定的进程pid.
-s strsize 指定输出的字符串的最大长度.默认为32.文件名一直全部输出.
-u username 以username的UID和GID执行被跟踪的命令

```

