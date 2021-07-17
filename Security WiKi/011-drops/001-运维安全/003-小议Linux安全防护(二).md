# 小议Linux安全防护(二)

0x00 文件安全
=========

* * *

### 文件的s、t、i、a权限

首先说一下关于文件的命令：ls more cat less head touch rm rmdir cd mkdir等等 对于一些文件我们希望它只有特定的用户可以访问，其他用户不可以访问，或者一个文件只能拥有着可以操作其他用户就不能操作这个时候我们应该怎么办?在linux系统中，对于文件和文件夹有一个s、t、i、a的权限，可以帮助我们做到这些；

![p1](http://drops.javaweb.org/uploads/images/2ad627b32bb256b3f012f6761093229fea9de85d.jpg)

例如这里的passwd命令，它的拥有者有一个s的权限，这个权限是什么意思呢！它代表普通用户在执行passwd这个命令时暂时拥有这个文件本身所属用户的权限。

![p2](http://drops.javaweb.org/uploads/images/417002cef695177477f03f6e79af0db92f73c804.jpg)

我这里解释一下SUID 与 SGID

SUID仅可用在“二进制文件（binary file）”，SUID因为是程序在执行过程中拥有文件拥有者的权限，因此，它仅可用于二进制文件，不能用在批处理文件（shell脚本）上。这是因为shell脚本只是将很多二进制执行文件调进来执行而已。所以SUID的权限部分，还是要看shell脚本调用进来的程序设置，而不是shell脚本本身。当然，SUID对目录是无效的。这点要特别注意。

SGID进一步而言，如果s的权限是在用户组，那么就是Set GID，简称为SGID。

*   文件：如果SGID设置在二进制文件上，则不论用户是谁，在执行该程序的时候，它的有效用户组（effective group）将会变成该程序的用户组所有者（group id）。
*   目录：如果SGID是设置在A目录上，则在该A目录内所建立的文件或目录的用户组，将会是此A目录的用户组。

上面介绍了关于s与t权限的一些东西，这里再说一下a与i权限，在linux中还有chattr这个命令，与他对应的还有一个lsattr命令

chattr这个命令常用于锁定文件的

**chattr:**

| 参数 | 说明 |
| :-- | :-- |
| -a | 只能向文件中添加数据，不能删除，修改 |
| -i | 设定文件不能被删除，修改，重命名 |
| -c | 设定文件是否经过压缩再存储，读取时需要经过解压缩 |
| -s | 安全地删除文件或目录，文件删除后全部收回硬盘空间(不可恢复) |
| -u | 与-s参数相反，系统会保留数据块，以便方便回收 |

所以作为一个网络安全运维人员，我们必须对文件进行严格的配置，这里只是一些针对文件本身是安全设置，不同的文件具有不同的读写执行等权限，接下来我们就针对不同用户对不同文件的读写执行来做一个描述；

### 文件的ACL

针对文件以及文件夹我们在新建的时候，通常会有一个默认的权限：

![p3](http://drops.javaweb.org/uploads/images/02613696cef8f242945b7bc813b4db6bcb13d38d.jpg)

我们会发现文件夹是755，而我们的文件是644，这是为什么呢，原因就是在linux中默认的umask权限，这个umask一般在我们的/etc/profile

![p4](http://drops.javaweb.org/uploads/images/b10aebb44e76964e5c011ed83954d2692cba5a15.jpg)

umask值：022代表什么意思呢，umask其实是权限的补码，就是在777权限上减去的值，所以我们文件夹的权限是`7-0/7-2/7-2=755`，那为什么我们文件的是644呢，因为创建文件的时候还需要减去一个默认的执行权限1，所以文件的权限就是`7-1/7-3/7-3=644`

平时我们修改文件权限的常用命令有这些：`chmod`、`chown`、`chattr`等，但是对于文件还有一个ACL(访问控制列表)机制，下面就以Centos7中来介绍一下文件的访问控制，对于ACL常见的命令有3个：`setfacl`、`getfacl`、`chacl`

![p5](http://drops.javaweb.org/uploads/images/c4ba654737a72acfa232e732f0443f6dcb0b0d37.jpg)

通过上图我们可以发现对文件的描述是一样的，文件名、拥有着、所属组、以及他们对应的权限；对于getfacl获取文件的权限没有什么可说的，这里详细说一下对文件权限的设置：

首先是参数：

```
setfacl [-bkndRLP] { -m|-M|-x|-X ... } file ...

-b：删除所有的acl参数
-k：删除预设的acl参数
-n：不重新判断是否有效
-d：设置预设的acl参数（只针对目录，在目录中的新建文件同样使用此acl）
-R: 递归设置后面的acl参数
-x：删除后面指定的acl参数
-m：设置后面指定的acl参数

```

针对acl参数：

```
[u/g/o]:[username/groupname/空]:[rwx] filename

```

下面看实例：

![p6](http://drops.javaweb.org/uploads/images/9f76c68d08a9fdc20edd901de4d7c17ff539aa42.jpg)

我们再设置一个对其他用户完全没有权限的acl

![p7](http://drops.javaweb.org/uploads/images/54c03731f77d8da798f5c9643969fd6ae7e9941d.jpg)

这里再添加一个可以读可执行却没有写权限的用户acl，

![p8](http://drops.javaweb.org/uploads/images/fb06d31559d6751fce4470b48fdd0f0a32176f15.jpg)

这就是文件访问控制的魅力，你希望这个文件对那些用户有什么权限都可以通过这样来进行设置；

### 文件的共享

提供文件共享的服务Samba、NFS、Ftp等等，这些都可以作为Linux中文件的共享功能；提供服务时需要注意目录的权限控制，这里我们将一下Linux中与cp命令相对应的一个命令scp，它可以远程来传输文件，并且基于ssh登录是一个安全的文件传输通道；常常用于我们的两台服务器之间的文件传输，比如我们的备份日志(通过crontab来实现)

![p9](http://drops.javaweb.org/uploads/images/21cc631b166c6143fd4f29eb0f618bccf2dab5db.jpg)

传一个文件到我们的远程服务器上面：

![p10](http://drops.javaweb.org/uploads/images/8083ca1fd1ad3c2f52c048553fd58b41eac66191.jpg)

从远程服务器上面获取一个文件：

![p11](http://drops.javaweb.org/uploads/images/a570477cea8df35c4f18c1ffdb1473a64571a6bb.jpg)

如果我们不想在每次获取文件或者传输文件的时候输入密码，我们可以使用ssh建立密钥认证来进行传输，一般在我们备份日志文件中也是通过这样的方式来进行备份；

![p12](http://drops.javaweb.org/uploads/images/08666dba3da2837a860f9fdfc516a8df864824af.jpg)

制定一个定时任务`crontab -e`每2分钟向服务器发送一个test.txt的文件

![p13](http://drops.javaweb.org/uploads/images/e212b405a96419e20d48243668309afa380a3f93.jpg)

我们这么做的目的或者说这么做了对服务器有什么安全性嘛，其实scp命令就是一个通过ssh的传输功能，我们可以在ssh结合firewall做一些限制，比如只允许哪些IP或IP段访问我们的服务器，这样我们就可以控制哪些可信的pc或服务器访问；

同时我们也可以通过SSH定时更新我们的密钥文件来防止我们的密钥文件泄漏；

这么做比我们使用ftp、samba等来传输文件更加安全可靠；

### 命令记录功能

在Linux系统中，有一个很重要的命令可以帮助我们曾经使用过的命令记录，但是也许有的时候我们并不需要这个功能，或者某些用户需要某些用户不需要，这个时候我们可以都配置文件进行配置：

配置文件：`/etc/bashrc`

在里面加入这4行

```
HISTFILESIZE=1000           #保存命令的记录总数
HISTSIZE=1000               #history命令输出的命令总数
HISTTIMEFORMAT='%F %T'      #定义时间显示格式
export HISTTIMEFORMAT       #载入

HISTFILE=/root/test     #里面命令保存目录
export HISTFILE         #载入，重新登陆用户生效
export HISTCONTROL      #忽略重复的命令
export HISTIGNORE="[ ]*:&:bg:fg:exit"       #忽略冒号分割这些命令

```

我们如果不想使用保存命令将记录总数设置为0就可以了；

这里提供一个“高性能构建Linux服务器”中提到的一个使用history记录用户的操作，在/etc/profile文件中添加如下代码：

```
#history
USER_IP=`who -u am i 2>/dev/null | awk '{print $NF}' | sed -e 's/[()]//g'`  #这句话就是先获取用户及IP信息，将标准错误输出到黑洞当中，然后使用awk命令获取最后一组参数，再通过sed将()替换掉；
HISTDIR=/usr/share/.history
#判断IP
if [ -z $USER_IP ]
then
    USER_IP=`hostname`
fi
#判断是否存在日志目录
if [ ! -d $HISTDIR ]
then
    mkdir -p $HISTDIR
    chmod 777 $HISTDIR
fi
#生成日志日文件
if [ ! -d $HISTDIR/${LOGNAME} ]
then
    mkdir -p $HISTDIR/${LOGNAME}
    chmod 300 $HISTDIR/${LOGNAME}
fi

export HISTSIZE=4000
DT=`date +%Y%m%d_%H%M%S`
export HISTFILE="$HISTDIR/${LOGNAME}/${USER_IP}.history.$DT"
export HISTTIMEFORMAT="[%Y.%m.%d %H:%M:%S]"
chmod 600 $HISTDIR/${LOGNAME}/*.history* 2>/dev/null

```

![p14](http://drops.javaweb.org/uploads/images/6190a06cdfeb4b9d9fdd383744e63c19ebe1fe4e.jpg)

如果我们是想给不同的用户设置history配置，我们就可以在相对应的账户家目录中的`.bash_profile`文件中进行编辑，然后重新登录系统就修改成功；

当然在Linux系统中其实还有一个命令可以帮助我们记录我们所操作过的命令：script

![p15](http://drops.javaweb.org/uploads/images/9fc79442ded2fa21bc39cfca8a2a259dab0376a0.jpg)

![p16](http://drops.javaweb.org/uploads/images/5d97aa58747cef961f88b65e218dde8a5d70feca.jpg)

script这个命令不但可以记录我们执行的命令，还可以记录我们执行命令后的返回结果，但是随着命令的执行这个文件会越来越大，所以这个命令使用的很少；

0x01 用户密码安全
===========

* * *

### 密码策略

在禁用不必要的服务及用户中，我们已经说过关于删除一些无用的用户([http://drops.wooyun.org/tips/11801](http://drops.wooyun.org/tips/11801))，但是linux作为一个多用户的系统，我们还是不可避免的会去新增很多用户，我们不能保证每一个用户具有很好的安全意识，所以只能在用户的密码以及用户的远程访问上做一些限制，我们先介绍Linux用户密码策略；

关于密码策略，我这里只从简单的配置文件说，对于Centos系列中使用pam认证机制不是本文的讨论范围；

配置文件：`vim /etc/login.defs`

```
MAIL_DIR        /var/spool/mail         #邮件目录

PASS_MAX_DAYS   99999                   #密码过期最大时间，99999代表永久有效
PASS_MIN_DAYS   0                       #是否可修改密码，0代表可修改，非0代表多少天后修改
PASS_MIN_LEN    5                       #密码最小长度，使用pam_creacklib module,这个参数不生效
PASS_WARN_AGE   7                       #密码失效前多少天在用户登录时通知用户修改密码

UID_MIN                  1000           #UID的最小值
UID_MAX                 60000           #UID的最大值
SYS_UID_MIN               201           #系统UID的最小值
SYS_UID_MAX               999           #系统UID的最大值

GID_MIN                  1000
GID_MAX                 60000
SYS_GID_MIN               201
SYS_GID_MAX               999

CREATE_HOME     yes                     #是否创建家目录

UMASK           077                     #umask的值

USERGROUPS_ENAB yes                     #当值为yes，没有-g参数自动创建名称和用户名相同的组

ENCRYPT_METHOD SHA512                   #加密方式

```

这个就是我们的用户密码策略，我们可以通过修改配置文件来对用户密码策略进行修改，也可以通过命令来进行修改：`chage`

**chage：**

| 参数 | 说明 |
| :-- | :-- |
| -m | 密码可更改的最小天数，为0代表任何时候都可以修改 |
| -M | 密码保持有效的最大天数 |
| -w | 用户密码到期前，提前受到警告信息的天数 |
| -E | 账号到期的日期，超过这个时间，账号就不能使用 |
| -d | 上一次更改的日期 |
| -i | 停滞时间，如果密码已过期多少天，账号不能使用 |
| -l | 列出当前设置 |