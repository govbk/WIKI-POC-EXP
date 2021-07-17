# 堆溢出的unlink利用方法

0x00 背景
=======

* * *

本文写给对堆溢出无的放矢的童鞋，分为如下几部分：

```
一.经典的unlink利用方法简介
二.在当今glibc的保护下如何绕过进行unlink利用

```

建议阅读本文之前先对glibc的`malloc.c`有所了解

[你可以在这里在线看到所有的malloc.c的源码](http://code.woboq.org/userspace/glibc/malloc/malloc.c.html)

0x01 第一部分
=========

* * *

首先简要介绍一下堆chunk的结构

我们可以在`malloc.c`中找到关于堆`chunk`结构的代码

```
struct malloc_chunk {

      INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
      INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */

      struct malloc_chunk* fd;         /* double links -- used only if free. */
      struct malloc_chunk* bk;

      /* Only used for large blocks: pointer to next larger size.  */
      struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
      struct malloc_chunk* bk_nextsize;
    };

```

这指明了一个`heap chunk`是如下的结构

```
+-----------+---------+------+------+-------------+
|           |         |      |      |             |
|           |         |      |      |             |
| prev_size |size&Flag|  fd  |  bk  |             |
|           |         |      |      |             |
|           |         |      |      |             |
+-----------+---------+------+------+-------------+

```

如果本`chunk`前面的`chunk`是空闲的，那么第一部分`prev_size`会记录前面一个`chunk`的大小，第二部分是本`chunk`的`size`,因为它的大小需要8字节对齐，所以`size`的低三位一定会空闲出来，这时候这三个位置就用作三个`Flag`(最低位:指示前一个`chunk`是否正在使用;倒数第二位:指示这个`chunk`是否是通过`mmap`方式产生的;倒数第三位:这个`chunk`是否属于一个线程的`arena`)。之后的FD和BK部分在此`chunk`是空闲状态时会发挥作用。FD指向下一个空闲的`chunk`，BK指向前一个空闲的`chunk`，由此串联成为一个空闲`chunk`的双向链表。如果不是空闲的。那么从fd开始，就是用户数据了。(详细信息请参考`glibc`的`malloc.c`部分，在此不再多做解释。)

首先，为了方便，我直接引用一位外国博主的漏洞示例程序，以便继续解释

```
/* 
 Heap overflow vulnerable program. 
 */
#include <stdlib.h>
#include <string.h>

int main( int argc, char * argv[] )
{
        char * first, * second;

/*[1]*/ first = malloc( 666 );
/*[2]*/ second = malloc( 12 );
        if(argc!=1)
/*[3]*/         strcpy( first, argv[1] );
/*[4]*/ free( first );
/*[5]*/ free( second );
/*[6]*/ return( 0 );
}

```

这个程序在[3]处有很明显的堆溢出漏洞，`argv[1]`中的内容若过长则会越界覆盖到second部分。

简单给出此程序的堆结构

```
+---------------------+   <--first chunk ptr
|     prev_size       |
+---------------------+
|     size=0x201      |          
+---------------------+   <--first                  
|                     |
|     allocated       |         
|      chunk          |      
+---------------------+   <--second chunk ptr                
|    prev_size        |         
+---------------------+                     
|    size=0x11        |         
+---------------------+   <--second                  
|     Allocated       |         
|       chunk         |     
+---------------------+   <-- top                  
|     prev_size       |            
+---------------------+                     
|    size=0x205d1     |           
+---------------------+                      
|                     |
|                     |
|                     |
|        TOP          |   
|                     |
|       CHUNK         |    
|                     |
+---------------------+

```

此处不赘余介绍exploit具体代码，只介绍利用方法.

只要我们通过溢出构造，使得second chunk

```
prev_size=任意值
size=-4(因为最低位的flag没有设置，所以prev_size是什么值是无所谓了)
fd=free@got-12([email protected]/* <![CDATA[ */!function(t,e,r,n,c,a,p){try{t=document.currentScript||function(){for(t=document.getElementsByTagName('script'),e=t.length;e--;)if(t[e].getAttribute('data-cfhash'))return t[e]}();if(t&&(c=t.previousSibling)){p=t.parentNode;if(a=c.getAttribute('data-cfemail')){for(e='',r='0x'+a.substr(0,2)|0,n=2;a.length-n;n+=2)e+='%'+('0'+('0x'+a.substr(n,2)^r).toString(16)).slice(-2);p.replaceChild(document.createTextNode(decodeURIComponent(e)),c)}p.removeChild(t)}}catch(u){}}()/* ]]> */定技术”)
bk=shellcode地址

```

在我们的payload将指定位置的数值改好后。下面介绍在[4][5]行代码执行时发生的详细情况。

第四行执行`free(first)`发生如下操作

1).检查是否可以向后合并

首先需要检查`previous chunk`是否是空闲的（通过当前`chunk size`部分中的`flag`最低位去判断），当然在这个例子中，前一个`chunk`是正在使用的，不满足向后合并的条件。

2).检查是否可以向前合并

在这里需要检查`next chunk`是否是空闲的(通过下下个`chunk`的flag的最低位去判断)，在找下下个chunk(这里的下、包括下下都是相对于`chunk first`而言的)的过程中，首先当前`chunk+`当前`size`可以引导到下个`chunk`，然后从下个`chunk`的开头加上下个`chunk`的`size`就可以引导到下下个`chunk`。但是我们已经把下个`chunk`的`size`覆盖为了-4，那么它会认为下个`chunk`从`prev_size`开始就是下下个chunk了，既然已经找到了下下个`chunk`，那就就要去看看`size`的最低位以确定下个`chunk`是否在使用，当然这个`size`是`-4`，所以它指示下个`chunk`是空闲的。

在这个时候，就要发生向前合并了。即`first chunk`会和`first chunk`的下个`chunk`(即`second chunk`)发生合并。在此时会触发`unlink(second)`宏，想将`second`从它所在的`bin list`中解引用。

具体如下

```
BK=second->bk（在例子中bk实际上是shellcode的地址）
FD=second->fd (在例子中fd实际上是free@got的地址 - 12)
FD->bk=BK
/*shellcode的地址被写进了FD+12的位置，但是FD是free@got的地址-12，所以实际上我们已经把shellcode地址写入了free@got*/
BK->fd=FD 

```

执行`unlink`宏之后，再调用`free`其实就是调用`shellcode`，这时就可以执行任意命令了。

但是，在现如今，`glibc`已经不这么简单了，为了使堆溢出不那么容易就被利用，它加入了许多新的保护措施，如何绕过也就是要在第二部分中讨论的内容。

0x02 第二部分
=========

* * *

以glibc中的代码作为示例，首先拿出最新版本的unlink宏。

```
1413    /* Take a chunk off a bin list */
1414    #define unlink(AV, P, BK, FD) {                                            
1415        FD = P->fd;                                                                      
1416        BK = P->bk;                                                                      
1417        if (__builtin_expect (FD->bk != P || BK->fd != P, 0))                      
1418          malloc_printerr (check_action, "corrupted double-linked list", P, AV);  
1419        else {                                                                      
1420            FD->bk = BK;                                                              
1421            BK->fd = FD;                                                              
1422            if (!in_smallbin_range (P->size)                                      
1423                && __builtin_expect (P->fd_nextsize != NULL, 0)) {                      
1424                if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)              
1425                    || __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))    
1426                  malloc_printerr (check_action,                                      
1427                                   "corrupted double-linked list (not small)",    
1428                                   P, AV);                                              
1429                if (FD->fd_nextsize == NULL) {                                      
1430                    if (P->fd_nextsize == P)                                      
1431                      FD->fd_nextsize = FD->bk_nextsize = FD;                      
1432                    else {                                                              
1433                        FD->fd_nextsize = P->fd_nextsize;                              
1434                        FD->bk_nextsize = P->bk_nextsize;                              
1435                        P->fd_nextsize->bk_nextsize = FD;                              
1436                        P->bk_nextsize->fd_nextsize = FD;                              
1437                      }                                                              
1438                  } else {                                                              
1439                    P->fd_nextsize->bk_nextsize = P->bk_nextsize;                      
1440                    P->bk_nextsize->fd_nextsize = P->fd_nextsize;                      
1441                  }                                                                      
1442              }                                                                      
1443          }                                                                              
1444    }
1445    
1446    /*

```

我们可以看到我们最大的阻碍是下面的这部分代码

```
if (__builtin_expect (FD->bk != P || BK->fd != P, 0))                     
      malloc_printerr (check_action, "corrupted double-linked list", P);

```

这段代码被添加到了`unlink`宏中，所以现在再调用`unlink`宏的时候，`chunk`指针`P->fd->bk`(即代码中的大写`FD->bk`)应该还是p指针自己。对于`BK->fd != p`这部分也是同样的道理。

在第一部分的利用方法中，我们修改了

```
p->fd=free@got-12
p->bk=shellcode_adress

```

我们在此记`FD=p->fd`,`BK=p->bk`,再去看`FD->bk`已经是`free@got`了，这部分是不能满足要求的。再看`BK->fd`已经是`shellcode+16`了,所以如上文的利用方法已经不能成功了。之所以还加以介绍，是因为这会使我们理解第二部分变得又快又好。

如果绕过还是要根据这段保护代码来谈。我们势必需要构造合适的条件的来过掉这行代码，那么就要找一个指向`p`的的已知的地址，然后根据这个地址去设置伪造的fd和bk指针就能改掉原`p`指针。

以64bit为例,假设找到了一个已知地址的ptr是指向p(p指向堆上的某个地方)的，通过堆溢出，我们可以做如下的修改。

```
p->fd=ptr-0x18
p->bk=ptr-0x10

```

布置好如此结构后，再触发unlink宏，会发生如下情况。

```
1.FD=p->fd(实际是ptr-0x18)
2.BK=p->bk(实际是ptr-0x10)
3.检查是否满足上文所示的限制，由于FD->bk和BK->fd均为*ptr(即p)，由此可以过掉这个限制
4.FD->bk=BK
5.BK->fd=FD(p=ptr-0x18)

```

这时候再对p进行写入，可以覆盖掉p原来的值，例如我们用合适的`payload`将`free@got`写入。p就变成了`free@got`，那么再改一次p，把`free@got`改为`shellcode`的地址或者说`system`的地址都可以。之后再调用free功能，就可以任意命令执行。

为了方便，在这边拿出一个最近的`wargame`出现的一个逻辑非常简单的程序作为漏洞示例程序,[可以在此下载](https://www.dropbox.com/s/ifjua544gd4js41/shellman?dl=0)

首先简单介绍这个Binary的功能以及基本情况

##### 开启的保护

```
RELRO    STACK CANARY    NX          PIE     RPATH    RUNPATH    FILE
No RELRO No canary found NX enabled  No PIE  No RPATH No RUNPATH shellman

```

##### 基本功能

```
1.显示已经建立的堆块中存储的内容
2.建立一个新的堆块，大小和内容又用户决定
3.对一个已经分配的堆块做编辑，这个地方没有限制大小，若太长可造成堆溢出
4.释放一个已经分配的堆块

```

##### 存放的堆块的基本逻辑结构

```
.bss:00000000006016C0 ; __int64 usingFLAG[]
.bss:00000000006016C0 usingFLAG       dq ?                    ; DATA XREF: main+38o
.bss:00000000006016C0                                         ; .text:0000000000400A90o ...
.bss:00000000006016C8 ; __int64 LEN[]
.bss:00000000006016C8 LEN             dq ?                    ; DATA XREF: new+B5w
.bss:00000000006016C8                                         ; delete+79w
.bss:00000000006016D0 ; __int64 content[]
.bss:00000000006016D0 content         dq ?                    ; DATA XREF: new+BCw

```

程序有一个全局数组会存储好每一个经过malloc分配的堆块返回的指针。以及在全局数组中存储长度以及本块是否正在使用的标志。

##### 如何利用

按照前文所介绍的，我们希望使用Unlink的方法去利用这个堆溢出漏洞。首先，我们要找一个指向堆上某处的指针。因为存储malloc返回指针的全局数组的存在，这让我们的利用变得异常的简单。因为bss段的地址也是固定的，我们可以知道，从而设置满足需要的bk和fd指针，下面介绍具体步骤。

1.我们可以首先分配两个长度合适的堆块。(如下图所示)

```
chunk0                malloc返回的ptr        chunk1        malloc返回的ptr
|                     |                     |             |
+-----------+---------+---+---+-------------+------+------+----+----+------+
|           |         |   |   |             |      |      |    |    |      |
|           |         |   |   |             | prev | size&|    |    |      |
| prev_size |size&Flag|   |   |             | size | flag |    |    |      |
|           |         |   |   |             |      |      |    |    |      |
|           |         |   |   |             |      |      |    |    |      |
+-----------+---------+---+---+-------------+------+------+----+----+------+

```

这时候这两块的fd和bk区域其实都是空的，因为他们都是正在使用的

2.对第一块进行编辑，编辑的过程中设置好第零块的bk和fd指针并溢出第一块，改好第一块的chunk头的控制信息(如下图所示)

```
chunk0                malloc返回的ptr           chunk1        malloc返回的pt
|                     |                        |             |
+-----------+---------+----+----+----+----+----+------+------+----+----+------+
|           |         |fake|fake|fake|fake| D  | fake | fake |    |    |      |
|           |         |prev|size| FD | BK | A  | prev | size&|    |    |      |
| prev_size |size&Flag|size|    |    |    | T  | size | flag |    |    |      |
|           |         |    |    |    |    | A  |      |      |    |    |      |
|           |         |    |    |    |    |    |      |      |    |    |      |
+-----------+---------+----+----+----+----+----+------+------+----+----+------+
                      |--------new_size--------|

```

我们为了欺骗glibc，让它以为堆块零malloc返回的指针(我们后文中简记为p)出就是chunk0指针，所以我们伪造了prev_size和size的部分，然后溢出堆块1，改掉第1个堆块的prev_size,数值应该是上图所示`new_size`的大小；另外第1块的size部分还要把prev_inuse的flag给去掉。如此就做好了unlink触发之前的准备工作

3.删掉chunk1,触发unlink(p)，将p给改写。

在删除堆块1时，glib会检查一下自己的size部分的prev_inuse FLAG，发现到到比较早的一个chunk是空闲的(实际是我们伪造的)，glibc希望将即将出现的两个空闲块合并。glibc会先将chunk0从它的Binlist中解引用，所以触发unlink(p)。

```
1).FD=p->fd(实际是0x6016D0-0x18,因为全局数组里面指向p的那个指针就是0x6016D0)
2).BK=p->bk(实际是6016D0-0x10)
3).检查是否满足上文所示的限制，由于FD->bk和BK->fd均为*6016D0(即p)，由此可以过掉这个限制
4).FD->bk=BK
5).BK->fd=FD(p=0x6016D0-0x18)

```

4.对p再次写入，修改p为free@got地址

5.现在p已经是free@got了，我们只要使用一次List功能便可以知道free函数的真实地址，进而算出libc的基址来过掉ASLR。

6.根据已经算出的libc基址再次算出system函数的真实[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)(如果没有libc，可以考虑简历多个chunk，[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)面的函数，这样在list时，我们可以得到两个libc函数的真实地址，根据其偏移，便可以找出服务器上的libc，若保护再够复杂无法改got，我们还可以构造ropchain，同样利用这样的方式，把ropchain丢进全局数组中)

7.因为free已经变成了system，只要再建立一个内容为`/bin/sh`的块，再删掉，就可以得到shell，由此全部利用完成。