# Linux PAM&&PAM后门

0x00 PAM简介
----------

* * *

PAM （Pluggable Authentication Modules ）是由Sun提出的一种认证机制。它通过提供一些动态链接库和一套统一的API，将系统提供的服务和该服务的认证方式分开，使得系统管理员可以灵活地根据需要给不同的服务配置不同的认证方式而无需更改服务程序，同时也便于向系统中添加新的认证手段。PAM最初是集成在Solaris中，目前已移植到其它系统中，如Linux、SunOS、HP-UX 9.0等。

0x01 PAM工作流程
------------

* * *

![NewImage](http://drops.javaweb.org/uploads/images/875cbdce43106bf508c10961ba76b307ba38d92a.jpg)

0x02 PAM配置文件语法
--------------

* * *

```
module-type
control-flagmodule_path
optional  

```

在`/etc/pam.d/`下的文件中，与服务名称相对应的文件，为该服务的pam验证文件，例如服务为sshd，则在`/etc/pam.d`下存在sshd这个文件，里面包含sshd验证规则。其中有个一特殊的文件为other，如果有的服务与之没有向对应的文件，则对应other。

### module-type

服务类型，即 auth、account、session 或 password。

```
验证模块(auth)用于验证用户或设置/销毁凭证。  
帐户管理模块(account)将执行与访问、帐户及凭证有效期、密码限制/规则等有关的操作。  
会话管理模块(session)用于初始化和终止会话。
密码管理模块(passwd)将执行与密码更改/更新有关的操作。 

```

### control-flag

用于指明在确定服务的集成成败值过程中模块所起的作用。有效的控制标志包括 include、optional、required、requisite 和 sufficient。

```
required 表示本模块必须返回成功才能通过认证，但是如果该模块返回失败的话，失败结果也不会立即通知用户，而是要等到同一stack 中的所有模块全部执行完毕再将失败结果返回给应用程序。可以认为是一个必要条件。  
requisite 与required类似，该模块必须返回成功才能通过认证，但是一旦该模块返回失败，将不再执行同一stack内的任何模块，而是直 接将控制权返回给应用程序。是一个必要条件。  
sufficient 表明本模块返回成功已经足以通过身份认证的要求，不必再执行同一stack内的其它模块，但是如果本模块返回失败的话可以 忽略。可以认为是一个充分条件。  
optional表明本模块是可选的，它的成功与否一般不会对身份认证起关键作用，其返回值一般被忽略。 

```

![enter image description here](http://drops.javaweb.org/uploads/images/19796fbecf84a3ef8787a6f946459754b8d08e93.jpg)

### module-path

用于实现服务的库对象的路径，一般都只写库名，库的路径一般为/lib/security(32位)，/lib64/security(64位)

### module-options

传递给服务模块的选项，可选。

几个公用的参数：

```
debug 该模块应当用syslog( )将调试信息写入到系统日志文件中。  
no_warn 表明该模块不应把警告信息发送给应用程序。  
use_first_pass 表明该模块不能提示用户输入密码，而应使用前一个模块从用户那里得到的密码。  
try_first_pass 表明该模块首先应当使用前一个模块从用户那里得到的密码，如果该密码验证不通过，再提示用户输入新的密码。  
use_mapped_pass 该模块不能提示用户输入密码，而是使用映射过的密码。  
expose_account 允许该模块显示用户的帐号名等信息，一般只能在安全的环境下使用，因为泄漏用户名会对安全造成一定程度的威胁。 

```

0x03 PAM 堆栈工作原理
---------------

* * *

![NewImage](http://drops.javaweb.org/uploads/images/6b2acfaa064f52024e6a757a0091b9da8352c0f1.jpg)

图1:PAM形成堆栈的过程(solaris，有的linux不包含)

![NewImage](http://drops.javaweb.org/uploads/images/c7e42f9a775d4ccff41c1a3a8a735fe9ddc93c74.jpg)

图2：PAM如何确定最终的返回值(solaris)  
0x04 常用PAM模块

* * *

从官方文档翻译出来的(`/usr/share/doc/pam-1.1.1`)，翻译可能有不对的地方

### 1、pam_securetty.so

类型：auth  
作用：只对root有限定，限定root登陆的终端，系统默认的“安全”中断保存在/etc/securetty中。

### 2、pam_access.so

类型：account  
作用：基于登录名，主机名或者所属域，ip地址或者网络  
终端编号(类似于/etc/securetty)。默认的配置文件为/etc/security/access.conf

### 3、pam_tally2.so

类型:auth 作用：当用户输入密码的错误次数超过指定次数时，锁定账户参数：

onerr=[fail|succeed]:

file=/path/to/counter:当登陆超过允许次数时，日志保存的地方。默认的为/var/log/tallylog。当开启的时候，每当登陆失败一次，则会写入一次，使用pam_tally2 可以读出

```
audit:如果用户找不到，则把此用户名记录到日志中
silent：不输出任何信息
no_log_info：不进行日志记录

```

deny=N：当用户连续输错n次是，在第n+1次锁定该用户，没有 设定解锁解锁时间，则锁定之后需要手工解锁。

```
pam_tally.so  -u username --reset

lock_time=n：当输入密码错误一次时，在N秒内不能再次登陆该账户。 

```

unlock_time=n：解锁时间，当账户被锁定时，过n秒时，该账户 被接触锁定(清空/var/log/tallylog中的相关信息)，配合deny参数使用 magic_root：当uid=0时，不会往/var/log/tallylog中写入计 数，即这个PAM不生效 even_deny_root：对root用户生效(不加magic_root参数，对 root也是不处理的) root_unlock_time=n:是针对even_deny_root的，root用户的解锁时间 每当用户成功登陆过一次后，/var/log/tallylog中关于这个用 户的记录就会清空

### 4、pam_cracklib

类型：password  
作用：限定更改密码的长度，复杂度等等。  
参数：

```
dubug:把修改密码的行为记录到日志中  
retry=N:修改密码时，允许错误的次数，默认是1次  
difok=N：新密码与旧密码不同的位数。如果超过一半不同，则通过验证，则忽略difok的设置  
minlen=N:密码的最短长度  
dcredit=N:至少有N的数字  
ucredit=N：至少有N的大写字码  
lcredit=N:至少有N个小写字母  
ocredit=N:至少有N个特殊字符  
minclass=N:密码组成的范围(数字，大小写字母，特殊字符)  
maxrepeat=N:最多与上一个密码重复 

```

### 5、pam_limits.so

类型：session  
作用：限制资源的使用，默认的配置文件为/etc/security/limits.conf是全局的，/etc/security/limits.d/下存放各个子文件

### 6、pam_listfile

类型：auth  
作用：验证用户是否能够登陆  
参数：

```
item=[tty|user|rhost|ruser|group|shell]:控制的对象  
sense=[allow|deny]：控制的方法  
file=/path/filename:文件的路径，每个占一行  
onerr=[succeed|fail]：指定某类事件发生时的返回值。  
实例：  
authrequired pam_listfile.soonerr=succeed item=user sense=deny file=/etc/ftpusers  
保存在/etc/ftpusers中的用户，是不允许的。  

```

### 7、pam_nologin.so

类型：auth  
作用：用于拒绝除root外的不同用户的登陆(当/etc/nologin存在，或者重新制定file的情况下)  
参数：auth  
file=/path/nologin：如果文件存在，当拒绝用户登陆的时候，同时会输出该文件中保存的内容。默认文件为/etc/nologin。

0x05 PAM后门
----------

* * *

测试环境CentOS 6.2 64位

### 0x05a 查询本机的PAM版本

```
rpm –aq | grep pam

```

![NewImage](http://drops.javaweb.org/uploads/images/dcee3893163bb43e5dd2fc2015a0947890354842.jpg)

下载对应的版本  
下载地址：

```
http://www.linux-pam.org/library/  
https://fedorahosted.org/releases/l/i/linux-pam/

```

![NewImage](http://drops.javaweb.org/uploads/images/24990f91ef5ab8b5cc9b1f3e33212057d12bd3af.jpg)

### 0x05b 修改源代码

```
vim /mnt/Linux-PAM-1.1.1/modules/pam_unix/pam_unix_auth.c
在PAM_EXTERN int pam_sm_authenticate(pam_handle_t * pamh, int flags,int argc, const char **argv)中定义FILE *fp;

```

![NewImage](http://drops.javaweb.org/uploads/images/6e69f29dd4814037e37927dfc1f3904eb1d0f9b4.jpg)

PS：网上的那种后门补丁也就是修改这些

### 0x05c 编译源代码

解决依赖性

```
yum install gcc make flex –y  
configure&&make  

```

编译出来的pam_unix.so在

```
/mnt/Linux-PAM-1.1.1/modules/pam_unix/.libs  

```

对/lib64/security中的文件进行替换(32位系统放入/lib/security)

### 0x05d 登录测试

![NewImage](http://drops.javaweb.org/uploads/images/30b648c199aca5202be0b111a9d1c353a58b2c14.jpg)

### 0x05e 使用touch –r来更改时间

![NewImage](http://drops.javaweb.org/uploads/images/4bc3ec68f8438905bfd2ae6010972f0a841022da.jpg)

PS:但是两个文件的大小是不同的

对于这种修改的方法，在/var/log/secure中和正常登录的是有差距

![NewImage](http://drops.javaweb.org/uploads/images/4078b496de0e400170014df5eadc4675395e0ba3.jpg)

### 0x05f 优化一下下

```
vim /mnt/Linux-PAM-1.1.1/modules/pam_unix/pam_unix_auth.c

```

![NewImage](http://drops.javaweb.org/uploads/images/6de825013e295c7786fa8208f14729962bd8ba38.jpg)

```
vim /mnt/Linux-PAM-1.1.1/modules/pam_unix/support.c

```

![NewImage](http://drops.javaweb.org/uploads/images/39dab9c8ab9d1a3aa320e4a8afa25127261367c1.jpg)

登录测试后的日志

![NewImage](http://drops.javaweb.org/uploads/images/5e07f54e65784afd390b00261537c137ab82253b.jpg)

一致了，o(∩_∩)o

### 0x05g 还有一种猥琐的方法，直接修改/etc/pam.d/sshd文件，输入什么都能登录的

![NewImage](http://drops.javaweb.org/uploads/images/cc7e2e6dcf936eb06eea08cfd89cea37454ee1a3.jpg)

正常日志

![NewImage](http://drops.javaweb.org/uploads/images/110f6964d638cc8702a5023fec6eb0aec34482e1.jpg)

PS：为什么能登录，好好看前面的基础部分就知道了