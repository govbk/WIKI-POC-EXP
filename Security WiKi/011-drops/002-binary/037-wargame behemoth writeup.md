# wargame behemoth writeup

> 又一期的`wargame`来了，这一期的_wargame_主要侧重于逆向，基本上在_gdb_下把程序的思路弄清楚了，再利用一些简单的渗透溢出技巧，就可以成功了。 Let's go!

依然是老方法，在游戏[behemoth](http://overthewire.org/wargames/behemoth/)首页可以找到登陆的服务器的账号和密码。`ssh`登陆上去，开始我们的`wargame`之旅。

level 0
=======

* * *

登陆服务器，在游戏文件夹`/behemoth`下可以看到全部的可执行程序，首先执行`./behemoth0`，这是这一关待解决的程序。

![behemoth_level0_login](http://drops.javaweb.org/uploads/images/61f542ac9e45888c3c45afd58c4ff8a3338f3362.jpg)

程序让我们输入一个密码，估计是将我们输入的密码和某个固定的密码做匹配，可能是加密后最匹配，谁知道它怎么做。`gdb`走起。

![behemoth_level0_disassemble](http://drops.javaweb.org/uploads/images/3b68f3394e49d12544a65bb9d7ab4cd44966c9a9.jpg)

从反汇编的代码可能看到两个令人激动的函数，一个是`memfrob()`，通过找男人(_man_)知道，这个函数是将输入的指定长度的字符串中的字符与数字`42`做异或，既然是异或操作，就是可逆的。另一个函数是`strcmp()`，这个函数才是最令人激动的，从整个程序流程大概看到，程序通过`scanf()`获取用户输入，然后通过`memfrob()`做异或处理，然后再送入`strcmp()`做匹配，所以，我们只要在`strcmp()`函数调用处下断点，然后查看栈内容就可以得到真正的密码了。

![behemoth_level0_passwd](http://drops.javaweb.org/uploads/images/54c96ecdf30b064959d54a464b4ae61f09eff47b.jpg)

程序需要输入的密码是`eatmyshorts`，执行程序，这一关就过去了。

![behemoth_level0_crack](http://drops.javaweb.org/uploads/images/3a3fda5e3e30c34ba89b014f57cf6ed7834a2459.jpg)

level 1
=======

* * *

这一关程序也是要求输入一个密码，无法得到准备密码，还是要`gdb`走起。

![behemoth_level1_login](http://drops.javaweb.org/uploads/images/7e987ccbf872950629fa255685eae6bd6384fa93.jpg)

![behemoth_level1_disassemble](http://drops.javaweb.org/uploads/images/5fef0875ea7bd0e9f1dd8d24ce805622f5762644.jpg)

好吧，从逆向出来的汇编代码看，程序很简单，使用`gets()`得到用户输入，然后`puts()`输出`"Authentication failure.\nSorry."`提示结束就可以了，没有匹配，也就是没有正确的密码。不过从`gets()`这是一个不安全的函数，这里也没有边界检查，说明存在缓冲区溢出漏洞，这是可以利用的。

![behemoth_level1_overflow](http://drops.javaweb.org/uploads/images/447519ec678de1b40c285c833ec0dc2d8427833f.jpg)

通过验证，确实存在缓冲区溢出漏洞，下面就是如何利用这个漏洞了，这个溢出利用前面的`wargame`已经玩得很多了。

![behemoth_level1_crack](http://drops.javaweb.org/uploads/images/5ef055bbd59b0884f2d81653d01bbbffbdfa7670.jpg)

level 2
=======

* * *

这里程序执行似乎是要创建某个文件，多次执行发现，每次创建的文件名似乎都不相同，应该是跟`pid`相关。

![behemoth_level2_login](http://drops.javaweb.org/uploads/images/f8b87badac60c4d23a9f1efca96dd054c07e6555.jpg)

还是看汇编代码比较容易理解程序的执行意图。

![behemoth_level2_disassemble](http://drops.javaweb.org/uploads/images/b459f4d88f4ccb6166af51d966e189eb46b2e5be.jpg)

对反汇编代码做个大概解释，执行的流程如下

```
id = getpid()
s = lstat("touch " + str(id))
if(s & 0xf000 == 0x8000){
    unlink(str(id);
    system("touch " + ID);
}
sleep(0x7d0);
system("cat  " + str(id));

```

程序在当前目录下尝试查找以自己`pid`为名的文件，如果不存在的话，就建立该文件，然后执行一个很长时间的`sleep()`，然后再打开文件。这里没有输入，不存在溢出，也没有其它很明显的漏洞。`sleep(a_long_time)`这个函数调用似乎没有办法越过，也没法通过修改`.got.plt`来尝试将`sleep()`替换成其它的函数。后来再参考了网上的类似`writeup`，发现这里在调用`system()`的时候使用的是相对路径，既然是相对路径，那么这个路径就是我们可以控制的，通过修改`PATH`环境变量，这样就可以使程序在路径搜索的时候，先搜索我们指定的路径，这样就可以将`touch`程序替换成我们想要执行的程序，比如`执行生成一个*shell*`。这样就顺利通过这一关了。

![behemoth_level2_crack](http://drops.javaweb.org/uploads/images/33d476d193096a59043f58458543bbee7d4d91b3.jpg)

这里需要注意`路径和伪 touch 程序`的权限问题，开始我一直失败就是因为权限配置的不对，浪费了不少时间按。

level 3
=======

* * *

这里还是有一个输入，既然有输入就有可能有溢出点。

![behemoth_level3_login](http://drops.javaweb.org/uploads/images/711e6cdf5ee792f75fc57848b6b60c37fb8c5c09.jpg)

从程序执行的结果来看，程序打印了我们的输入，猜测可能有缓冲区溢出，或者是格式化字符串漏洞，经过验证，确实有格式化字符串漏洞，这样就很容易了，基本上不需要看汇编代码就可以搞定了。

![behemoth_level3_test_offset](http://drops.javaweb.org/uploads/images/fb66a90a1d38e038189317c4e147661739db572e.jpg)

从上面的测试我们发现，字符串存储地址是在当前栈的第六个偏移的地方，即`0x18(%esp)`，这个值在`gdb`中也是可以看到的。接下来就是构造攻击程序了。我将`shellcode`放在环境变量中。

![behemoth_level3_gdb_test](http://drops.javaweb.org/uploads/images/a480b4437b9c81976003bf92be6a06bdce95ed5c.jpg)

如上图所示，环境变量即`shellcode`保存在_0xffffd78c_中，可能存在一点偏移，不过我们有`Nop sled`，`Return Address`处保存着程序原来的返回地址，我们需要将它修改为`shellcode`

![behemoth_level3_crack_attack](http://drops.javaweb.org/uploads/images/c40bde0508c0e0214a7e304d1f77ed2f4104409a.jpg)

这里执行的`cat`是为了防止管道关闭，在前面的`wargame`也使用了这个方法。其中需要注意的是，管道的右边，一开始我使用的是相对路径，导致总是没法得到正确的结果，也不知道问题出现在哪里，后来无意中使用了绝对路径，才搞定的。这里不知道为什么，等我之后看看管道的具体原理再做记录。

![behemoth_level3_crack_ret](http://drops.javaweb.org/uploads/images/1c4ef5e2f9f492b69a427fca3147ee5b782bf8d5.jpg)

level 4
=======

* * *

这里执行的结果就给了一个提示，`PID not found!`，看样子程序又是跟`PID`相关了。

![behemoth_level4_login](http://drops.javaweb.org/uploads/images/63c4b18d8d097a947fb8a4c17da865b44942513d.jpg)

从反汇编出来的代码可以大概了解到程序的执行流程。

![behemoth_level4_disassemble](http://drops.javaweb.org/uploads/images/d404d2b974d923961c68d03ca90ed6fd82c75a5d.jpg)

![behemoth_level4_disassemble_2](http://drops.javaweb.org/uploads/images/ac4c32d3d52d4a837919c6fa6b400b5453f0e878.jpg)

程序首先打开`/tmp/pid`文件，然后`sleep(1)`一秒，然后将文件内容输出，这样我们只要将文件软链接到密码文件，就可以让程序打开密码文件，同时输出文件内容了。难点在于，我们如何知道程序的`pid`，虽然_linux 下　pid 是递增的，但是这也无法保证每次增加的就是 1 个单位_。于是，我想到了一个_不优雅_的方法，我们先建立大量的可能的`pid`软链接文件，然后一直执行程序，执行程序的`pid`会落到我们建立的文件范围内的。

`behemoth4.py`

```
#!/usr/bin/env python
#coding=utf-8

import sys, os
passwd_file = "/etc/behemoth_pass/behemoth5"

if len(sys.argv) < 2:
        print "usage %s [start pid num]"
        sys.exit(-1)
try:
        start_pid = int(sys.argv[1])
except ValueError:
        print "usage %s [start pid num]"
        sys.exit(-1)

# 建立 50 个符号链接文件
for i in range(50):
        os.popen("ln -s " + passwd_file + " /tmp/" + str(i+start_pid))

# 执行 1000 次程序
for i in range(1000):
        ret = os.popen("/behemoth/behemoth4")
        ret = ret.read()
        if not "not" in ret:
                print ret
                break

# 删除所有建立的文件
for i in range(50):
        os.popen("rm /tmp/" + str(i+start_pid))

```

主要是`python`下获取子进程的`pid`太麻烦了，要不然这个爆破的代码可以写得更优雅一点。不过不影响结果，依然爆破出来了。这里需要注意的是，`start pid`即程序的参数应该要选得大一点，因为程序里面建立符号链接文件启动了不少子进程，我这里在原来的基础上增加了`500`个数，否则容易越过。

![behemoth_level4_crack](http://drops.javaweb.org/uploads/images/81725852f7e686915b0fd28bd05d2c9d2b4a2462.jpg)

level 5
=======

* * *

这一关执行程序没有任何输出，没有提示，还是直接看反汇编出来的代码吧。代码

![behemoth_level5_disassemble_0](http://drops.javaweb.org/uploads/images/3a44764a36e2f38b60d6ab2a3f9a7503b29e9781.jpg)

![behemoth_level5_disassemble_1](http://drops.javaweb.org/uploads/images/aa4c04f50e78c21f91f122a596354650a3a6bf09.jpg)

![behemoth_level5_disassemble_2](http://drops.javaweb.org/uploads/images/49b1928c4f51f5d7101708b44eff79a89f912952.jpg)

![behemoth_level5_disassemble_3](http://drops.javaweb.org/uploads/images/35e87be77e8b954d210b59c449f10a5a38ded9b0.jpg)

![behemoth_level5_disassemble_4](http://drops.javaweb.org/uploads/images/faea2cc2a58cb66518c76f940df7bf3495ca2ddc.jpg)

可以看到，程序首先打开了密码文件`/etc/behemoth_pass/behemoth6`，然后建立了`localhost:1337`的`socket`，再用`sendto`函数将文件内容发送出去。程序的流程很明显了，接下来我们只要监听本地端口`1337`就可以收到密码了。需要注意的是`sendto`是用`UDP`协议发送的，需要监听该端口的`UDP`数据包。

使用瑞士军刀`nc`进行监听，然后在另外一个`shell`中执行程序，`nc`就会输出收到的`UDP`数据包内容了。

`shell 1`![behemoth_level5_listen](http://drops.javaweb.org/uploads/images/cfd9588ff9b9dfed85ccd56b1eb48a1a6bfcdbf0.jpg)

`shell 2`![behemoth_level5_sendto](http://drops.javaweb.org/uploads/images/b4487d3b656ff8775455e0c072f20e171ecc8b7a.jpg)

`shell 1`![behemoth_level5_crack](http://drops.javaweb.org/uploads/images/94b5e9a9befbba5faf1f49644abe95efe9cf09fd.jpg)

level 6
=======

* * *

这一关有两个可执行程序，执行程序都没有得到任何有意义的结果，还是直接看反汇编出来的代码吧。

![behemoth_level6_disassemble](http://drops.javaweb.org/uploads/images/9ce599ecf850bb12102db5239a2c66188139ab59.jpg)

![behemoth_level6_memory](http://drops.javaweb.org/uploads/images/abcd4afee838f6a69ffce221fbe2955ff9474f69.jpg)

第一个主程序与第二个程序`/behemoth/behemoth6_reader`建立一个管道，然后通过管道读取，如果读到的内容等于`HelloKitty`，这样就会执行`execl()`，建立一个`shell`。我们再看看第二个程序。第二个程序，执行就会输出`Couldn't open shellcode.txt!`，看样子是要建立一个名为`shellcode.txt`的文件，具体还是看看汇编代码吧。

![behemoth_level6_reader](http://drops.javaweb.org/uploads/images/1274f85aad98da7d9d6a899a56069c6c483c8ca8.jpg)

程序首先打开一个名为`shellcode.txt`的文件，然后将文件内容读取到动态申请的存储区，最后跳转到动态存储区，执行读取到的内容。这样就很容易理解了，我们在`shellcode.txt`文件中存放一段`shellcode`，这段`shellcode`只执行一个任务，就是向标准输出`stdout`打印一段字符串`HelloKitty`就可以了。

```
section .text
global _start
_start:
        mov ax, 0x7974          ; ty
        movzx eax, ax           ; zero-extend ax to 32bits
        push eax
        push 0x74694b6f         ; oKit
        push 0x6c6c6548         ; Hell
        mov ecx, esp
        xor ebx, ebx
        inc ebx
        xor edx, edx
        mov dl, 10
        xor eax, eax
        mov al, 4
        int 80h

        ; exit(0)
        xor ebx, ebx
        xor eax, eax
        mov al, 1
        int 80h

```

上面就是我写的输出`HelloKitty`的`shellcode`程序，汇编之后就可以得到可用的`shellcode`程序了。需要注意的是，`behemoth6_reader`程序使用的也是相对路径，既然是相对路径，就是我们可以控制的。在`/tmp`下建立文件夹`behemoth6`，将当前文件夹设置为`/tmp/behemoth6`，在该目录下操作就可以了。

![behemoth_level6_crack](http://drops.javaweb.org/uploads/images/f36163fcc9c128bf4059d98fcabf7857bc7aa151.jpg)

level 7
=======

* * *

这一关的程序也是执行没有任何输出，所以说这次的`wargame`主要还是看逆向能力，基本上能逆向出来程序流程，后面的问题都很容易就可以解决了。汇编出来的程序很长，就不贴了。

唯一可能有点难度的是，在汇编代码中有两次调用`call 0x8048420 <__ctype_b_loc@plt>`这一个函数，男人(man)告诉说，这个函数一般是`<ctype.h>`中的函数如`isspace()`、`isalpha()`等调用的，也就是在程序里执行的是类似的检测，再加上从其它的代码总体来看，得到结论。该程序检测`argv[1]`中是否有`Non-alpha`字符存在，如果有的话那么就有可能是`shellcode`，这样就提示错误。如图所示，

![behemoth_level7_login](http://drops.javaweb.org/uploads/images/34431ad0453a33b626895601579672ce0e1d714e.jpg)

如上图所示，第一次执行时，`argv[1]`中有字符`,`存在，于是程序报错，提示可能有`shellcode`存在。

不过程序只是检测`argv[1]`中前`256`个字符，这样我们只需要用`alpha`字符填充前面`256`个位置就可以了，后面可以进行缓冲区溢出利用。不过程序中将全部的环境变量都清空了，这就意味着我们不能将`shellcode`放置在环境变量中，需要找其它的地方存放，同时一开始，我将`shellcode`放在`argv[1]`字符串中的尾部，加上`Nop sled`，执行的时候提示`Illegal Struction`，猜测可能栈不可执行。最终我使用`return-to-libc`，将返回地址修改成`system()`函数的地址，同时将参数`/bin/sh`放置在`argv[2]`中，加上一定的猜测，最终搞定了。

![behemoth_level7_crack](http://drops.javaweb.org/uploads/images/190668eaf511d06031ebe2340cef5b231497e718.jpg)

end of the game
===============

* * *

又完成一期`wargame`了，现在的难度不是很大，都是一些很基础的逆向、溢出的知识，不过作为一个新手，我深深地知道打好基础才是最重要的，后面依然有很多好玩的。尽请期待～

想了解更多关于`wargame`的内容，请参考[这里](http://overthewire.org/wargames/)！