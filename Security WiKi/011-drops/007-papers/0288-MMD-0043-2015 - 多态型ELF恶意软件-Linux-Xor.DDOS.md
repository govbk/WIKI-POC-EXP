# MMD-0043-2015 - 多态型ELF恶意软件:Linux/Xor.DDOS

0x01 背景
=======

* * *

**A share of knowledge I have, hopefully to make internet safer. @unixfreaxjp**

[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)于其它国产ELF DDos恶意软件，Linux/XOR.DDoS更具威胁性，而且它仍在扩散中。最近我收到一个很好的问题（一个受到感染的研究人员问的）：为什么找到的恶意二进制文件跟首次执行的恶意二进制文件不一样？非常好！这篇文章比较短，只包含这个问题的答案。但那些可能对缓解/检测病毒的重要信息和技术我会分享给NIX的小伙伴们，因此文章中还包含了我对ELF恶意软件进行逆向，调试和取证的三个过程。最后，请原谅我糟糕的措辞，因为我几乎没有时间去检查和校验这篇文章。

多态（Polymorphic）是指恶意软件在自我繁殖期间不断改变（“morphs”）其自身文件特征码（大小、hash等等）的特点，衍生后的恶意软件可能跟以前副本不一致。因此，这种能够自我变种的恶意软件很难使用基于签名扫描的安全软件进行识别和检测。

多态型恶意软件在Window中是一种很常见的病毒，但在Unix中这类恶意软件可能还比较少听说。本质上NIX的恶意软件也是来自于网络，从感染文件提取或通过其它恶意软件下载。所以，我猜我们有许多默认哈希样本。但在这篇文章中，我们实际上是在处理一个像Windows上能够自我拷贝感染的多态行为恶意软件。所以我觉得值得写一写。

这篇报告是一个真实的感染事件，一个已知的gang/crook案例，我得以发布如下的攻击日志：

![](http://drops.javaweb.org/uploads/images/bd3ca6d65ba9e7bd3144d9c4243092bb1a642f12.jpg)

上面的日志是典型的Linux/ Xor.DDOS hostasa.org ssh暴力攻击模式。不久之前我在[这里](http://blog.malwaremustdie.org/2015/06/mmd-0033-2015-linuxxorddos-infection_23.html)发布过（同一个攻击者）一个案例还有最近发生的一个[案例](http://www.linuxquestions.org/questions/linux-security-4/if-you-infected-by-any-of-these-recent-elf-malware-cases-please-contact-us-4175546925/)。另外，我把这个恶意软件上传到了[virustotal](https://www.virustotal.com/en/file/8d25feed690c1381f70018f5b905efbc9d8901098371cdeb8f32aa4d358210c7/analysis/1442501628/)。

0x02 Polymorphic PoC
====================

* * *

Linux/XOR.DDos执行的时候会寻找一个自我拷贝的地方，通过下面的系统调用可以看到它正在努力地写文件中：

```
open("/usr/bin/lgjgjmkkgd", O_WRONLY|O_CREAT, 0777) ; depends, in mine is -1 EACCES (Permission denied)
open("/bin/lgjgjmkkgd", O_WRONLY|O_CREAT, 0777)     ; depends, in mine is -1 EACCES (Permission denied)

```

在一个良好的Linux系统中，如果恶意软件不是通过root用户执行的话你会看到上面的结果。这时，恶意软件拷贝向它最喜欢的/tmp目录当中：

```
open("/XOR.DDOS.SAMPLE", O_RDONLY)      ; initial exec malware open itself
lseek(3, 0, SEEK_SET);                  ; set LSET to OFFSET to READ
open("/tmp/lgjgjmkkgd", O_WRONLY|O_CREAT, 0777); open self-copy target w/perm 777
read(3, "\177ELF\1\1\1\0\..");          ; read the malware bin
lseek(4, 0, SEEK_SET)                   ; set LSET to OFFSET to WRITE
14878 read(3, "\177ELF\1\1\1\0\…        ; copy process read..
14878 write(4, "\177ELF\1\1\1\0\…       ; copy process write

```

通过逆向ELF恶意软件，以下的操作就是上述恶意软件在寻找安装目录到执行整个过程（大图点击[这里](http://imgur.com/WDzFIvh)）：

![](http://drops.javaweb.org/uploads/images/d06f7d4addaf348fc65b7eaeb6af41c718e52868.jpg)

可以看到恶意软件通过级联的方式去寻找一个可以自我拷贝的地方，程序最开始从尝试往/usr/bin目录拷贝，然后尝试往/bin目录拷贝。在我的测试过程中，它最终选择了/tmp/[randomname]。目标文件名是随机的，然后通过返回的全路径执行execve()。我们稍后再讨论这个话题。

通过Linux内存取证工具可以比较清楚地看到复制blob数据的整个过程，使用hexdump这个老牌工具就行了：

**Copy process illustration (read and write of copy process) in the end of file:**

```
[...]
00098bd0  6d 65 00 5f 64 6c 5f 6d  61 70 5f 6f 62 6a 65 63  |me._dl_map_objec|
00098be0  74 5f 64 65 70 73 00 5f  6e 6c 5f 43 5f 4c 43 5f  |t_deps._nl_C_LC_|
00098bf0  49 44 45 4e 54 49 46 49  43 41 54 49 4f 4e 00 5f  |IDENTIFICATION._|
00098c00  64 6c 5f 6e 73 00 5f 6e  6c 5f 6c 6f 61 64 5f 6c  |dl_ns._nl_load_l|
00098c10  6f 63 61 6c 65 5f 66 72  6f 6d 5f 61 72 63 68 69  |ocale_from_archi|
00098c20  76 65 00 77 63 74 72 61  6e 73 00                 |ve.wctrans.|
00098c2b

```

debug的时候可以看到复制进程是优雅结束的：

```
read(3, "", 4096):   ; EO/termination w/no space
close(3);             ; end of copy (reading)
close(4);             ; end of copy (writing)

```

上面并没有什么特别的操作，现在我们运行到这里已经完成恶意软件自我拷贝了，但是为什么文件会不同？我们继续向下走，发现下文有一个系统调用在使用SEEK_END标志：

```
open("/tmp/lgjgjmkkgd", O_WRONLY); ; opening the copied file
lseek(3, 0, SEEK_END) = 625707 <==size  ; set LSET to the EOF for writing
; SEEK_END = *)    ; note the size of original malware

```

它看起来是使得文件偏移量指向了文件结束处。下图显示了使用了SEEK_END标志之后文件偏移量的位置(*所指之处)：

**Illustration of the LSET set in the end of file..**

```
00098bd0  6d 65 00 5f 64 6c 5f 6d  61 70 5f 6f 62 6a 65 63  |me._dl_map_objec|
00098be0  74 5f 64 65 70 73 00 5f  6e 6c 5f 43 5f 4c 43 5f  |t_deps._nl_C_LC_|
00098bf0  49 44 45 4e 54 49 46 49  43 41 54 49 4f 4e 00 5f  |IDENTIFICATION._|
00098c00  64 6c 5f 6e 73 00 5f 6e  6c 5f 6c 6f 61 64 5f 6c  |dl_ns._nl_load_l|
00098c10  6f 63 61 6c 65 5f 66 72  6f 6d 5f 61 72 63 68 69  |ocale_from_archi|
00098c20  76 65 00 77 63 74 72 61  6e 73 00 *<====          |ve.wctrans.*) <==
00098c2b

```

继续走，程序调用了timeoftheday()，然后向文件结尾处写入一个字符串：

```
gettimeofday({1442479267, 397488}, NULL) ; for randomid() seed..
write(3, "wlpvpovdvi\0", 11) ; 'size is set to 11'
    ; write string "wlpvpovdvi\0"-
    ; in the LSET position (EOF)

```

下图是文件写入前和写入后的对比:

![](http://drops.javaweb.org/uploads/images/c0924c6e03827e243a89781f9ba73802615c2ae1.jpg)

可以看到，文件被多添加了11个字节，这意味着会比自我拷贝之前的恶意软件多出11个字节。

下一步，程序调用close保存并关闭文件：

```
close(3)  ; end of writing process..

```

接着，调用execve()函数创建一个shell command执行它：

```
execve("/tmp/lgjgjmkkgd", ..); ; main running process of XOR.DDOS in new PID
                               ; with new size (& hash)

```

你可以在/proc看到它保存的进程数据，相信我，这个操作不需要借助任何Unix取证工具，因为Unix已经帮我们提供好这一切：

```
lgjgjmkkg 14881 MMD  cwd   DIR  8,6     4096        7209106 /TESTDIR
lgjgjmkkg 14881 MMD  rtd   DIR  8,1     4096              2 /
lgjgjmkkg 14881 MMD  txt   REG  8,1   "625718 <== NEW SIZE" 829 /tmp/lgjgjmkkgd
lgjgjmkkg 14881 MMD    0u  CHR  1,3      0t0           1028 /dev/null
lgjgjmkkg 14881 MMD    1u  CHR  1,3      0t0           1028 /dev/null
lgjgjmkkg 14881 MMD    2u  CHR  1,3      0t0           1028 /dev/null

```

现在它拥有一个全新的PID，不是通过clone或fork/thread，而是运行在一个新的进程。另外还可以看到它比原文件多了11个字节：

下面是原始文件和拷贝后的文件的md5值：

```
$ md5sum XOR.DDOS.SAMPLE lgjgjmkkgd
"7642788b739c1ee1b6afeba9830959d3"  XOR.DDOS.SAMPLE
"df50d096fb52c66b17aacf69f074c1c3"  lgjgjmkkgd
$ ls -l XOR.DDOS.SAMPLE lgjgjmkkgd| awk '{print $5, $6, $7, $9}'
"625718" Sep 17 lgjgjmkkgd
"625707" Sep 17 XOR.DDOS.SAMPLE

```

它们有着不同的hash和大小。

ok，我们已经完成了调试和取证，现在逆向工程来看一下这个ELF恶意软件是如何完成上述的所有操作。

下面是我的恶意样本一部分自我拷贝的过程。注意：自我拷贝级联了几种情况，我大概数了一下有至少四层级联。恶意软件的作者真的计算了所有可能性以确保他的代码能够运行。

![](http://drops.javaweb.org/uploads/images/6da03028068197855e29683f54c2f31b2bf5bb97.jpg)

跳转到0x804dfc2进行处理下个任务。

下面展示了恶意软件在完成拷贝文件之后修改文件的过程。11个随机字符没有直接使用的，而是跟一个硬编码在0x080cf120（str.Ff4VE.7）的字符串做xor加密运算。

![](http://drops.javaweb.org/uploads/images/822b7a87bfad21883debf87a8d72cfb8142fbaf3.jpg)

snprintf()函数结果最终被SYS_write系统调用所使用，在逆向静态编译的ELF恶意样本的时候可以看到一些来自libc的函数，后面还可以看到很多调用libc的代码。

上面调试中所看到的timeoftheday()正是被这里的randomid()函数所调用的。

![](http://drops.javaweb.org/uploads/images/9558841bb7f20fa773ce449b54f7c58fad4effe9.jpg)

很明显，这里调用了timeoftheday()取得系统时间来作为randomid()函数的随机种子。

这里有一个惊讶的信息是（我想这消息对于社区很有帮助）：Linux/XOR.DDoS ELF恶意软件使用非常罕见的执行shell命令方法，它调用了LinuxExec_Argv()和LinuxExec_Argv2()，而这两个函数都是直接使用系统调用（静态编译），这些函数一个典型的特点是：用起来非常简单，而且容易找出哪些是负责调用execve()。下面展示了在解析完路径之后使用execvp()函数进行感染。

![](http://drops.javaweb.org/uploads/images/a417fff3a407f87e64f0b9427e3f7e19bad56034.jpg)

关于execvp详细信息可以直接参考man(2)，是的，Unix系统已经提供给我们最好的参考资料。

0x03 总结&参考
==========

* * *

Linux/XOR.DDos在自我拷贝（成功感染）之后的文件跟原文件有不同的大小（多了11个字节...另外，我只检查了这一个样本）和hash。这意味着对于那些使用hash扫描的安全软件来说是无法扫描出变种后的Linux/XOR.DDos。

很多人认为，无所谓咯，ELF反正侵害不到我自己的电脑（Windows）。但是记住：目前IoT和路由器领域基本都是基于Linux系统，而ELF恶意软件的感染方法越来越先进/完美（我们数据显示有6个新的ELF恶意软件仅半年就更新了两个）。因此我们（MalwareMustDie）建议尽可能早点更新对这类恶意软件的检测质量。如果让这些恶意软件扎根在服务器领域，那么影响比感染PC机严重太多了。

下面是以前的Linux/XOR.DDos分析文章：

*   [http://blog.malwaremustdie.org/2015/07/mmd-0037-2015-bad-shellshock.html](http://blog.malwaremustdie.org/2015/07/mmd-0037-2015-bad-shellshock.html)
*   [http://blog.malwaremustdie.org/2014/09/mmd-0028-2014-fuzzy-reversing-new-china.html](http://blog.malwaremustdie.org/2014/09/mmd-0028-2014-fuzzy-reversing-new-china.html)

还有来自新的CNC威胁：

```
Will #USA be nice to clean: 192.126.126.64 & 107.160.40.9 < China crook's #malware #CNC? http://t.co/fTD0V57ySc pic.twitter.com/ZmabDO9aoP
— MalwareMustDie (@MalwareMustDie) September 15, 2015

```

顺便说一下，CNC现在非常的活跃，下面是一些关于它们活动的截图：

![](http://drops.javaweb.org/uploads/images/eb28903776ba3bad81d20867307b8d0f66b53ab7.jpg)

![](http://drops.javaweb.org/uploads/images/74f4a72dfbdd1e8d4e95b751dee11452b7501641.jpg)

![](http://drops.javaweb.org/uploads/images/2bd9a5f96bf69985a3aa9140a3b6b35c39bd8e44.jpg)

最后，希望这篇短文章能够帮助到做安全的朋友。