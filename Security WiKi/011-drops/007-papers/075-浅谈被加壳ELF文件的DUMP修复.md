# 浅谈被加壳ELF文件的DUMP修复

前面的文章中，我已经介绍了如何调试被加壳的ELF，这里不在叙述，直接进入正题，以某加固为例，如何DUMP和修复被加壳的ELF，使其能调试加载

我们先来看看被加壳ELF的头和Program Header

![enter image description here](http://drops.javaweb.org/uploads/images/67a14d17b69c87afab5086c5e7f87a832ba2cbc7.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/1355ec8be9c478500255bb1797350055756c542e.jpg)

首先我要让调试器停在入口点0x3860的位置

开始DUMP修复之旅，我的第一次DUMP修复的方法，延续了PE的思路，结果失败了

失败的原因并不是思路不对，而是细节上出现问题

第一次DUMP的方法：

1.废除不影响加载的section(直接把结构体填0)，只关心PT_LOAD和PT_DYNAMIC两种类型节 2.计算DUMP文件最大值 align_up(0x28ca4, 0x8000) = 0x31000 3.将offset和va变成相等值，filesize和memsize按照align对齐 4.根据PT_LOAD节数据把数据DUMP出来，把DUMP数据放进文件里

那么根据上图描述数据，应该有两块儿

```
PT_LOAD : 0 ----align_up(0x12044, 0x8000) = 0 ----- 0x1B000
PT_LOAD : align_down(0x28ca4,0x1000) = 0x28000 ---- align_up(0x28ca4, 0x8000) = 0x31000

```

因为安卓也是linux内核，内存页对齐粒度为4K(0x1000)

按照上述方法DUMP完，我们来看看IDA加载以后，JNI_ONLOAD的样子

![enter image description here](http://drops.javaweb.org/uploads/images/471ae9116b55d311bf6852cdcf2d57c8967d99de.jpg)

看下红色的部分，奇怪了，本来应该有的代码去哪里了??

`0x221b0`这个地址竟然无效

可是动态调试器中明明可以看到这段代码：

![enter image description here](http://drops.javaweb.org/uploads/images/3362584e7a5f5e22e887e0ed34d185a9eb8c3c76.jpg)

对照Program Header, 再看`0x221b0`这个地址，PT_LOAD节中并没有描述这个地址 所以，失败就是在这个地方，壳的代码里一定是mmap了这段内存，将解密后的数据，放进去，并修改了内存属性

通过跟踪壳代码，发现确实如此，壳代码通过svc 0，调用了mmap,mprotect两个函数

```
mmap(0x3000, 0x23710, 0x3, 0x32, 0xffffffff, 0x0)  
map页属性：PROT_READ | PROT_WRITE
mprotect(0x3000, 0x23710, 0x5)  

```

修改页属性：PROT_READ | PROT_EXEC 具体参数说明请参考帮助文档

这段区域起始地址：0x3000 大小：`align_up(0x23710, 0x1000) = 0x24000`结束地址：`0x3000 + 0x24000 = 0x27000`0x221b0这个地址正好在0x3000---|0x27000这个范围里

通过上述过程，重新总结DUMP方法如下

1.  废除不影响加载的section(直接把结构体填0)，只关心PT_LOAD和PT_DYNAMIC两种类型节
2.  计算DUMP文件最大值`align_up(0x28ca4, 0x8000) = 0x31000`
3.  只保留一个PT_LOAD节，从0到`0x31000`将整块儿数据DUMP下来直接写入文件，修改align为0x1000，修改flag为RWE
4.  修改PT_DYNAMIC节的offset,和VA相等 修复完的节表如下：

![enter image description here](http://drops.javaweb.org/uploads/images/0de55e694e22753ef7a3c6c235502d424fbd5fb3.jpg)

最后一个注意的地方，就是干掉INIT段或者是INIT_ARRAY段

干掉INIT方法：定位INIT描述的数据偏移，将偏移+8的数据，前移8个字节

干掉INIT_ARRAY方法：定位到VA处，按照结构，将数据填充为0xffffffff或者0

看下图，INIT段已经不存在了

![enter image description here](http://drops.javaweb.org/uploads/images/482b8d1641e89f84df8a13b34aafdb8c9e7ae872.jpg)

我们来打开IDA，加载修复的文件，看看效果：

![enter image description here](http://drops.javaweb.org/uploads/images/6eca83ed760a7864ae73f920b510bab928a2872f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/82e7209f3f9025f7dfdf15043e543c3cd05f998c.jpg)

数据完整，再看看动态加载的效果

![enter image description here](http://drops.javaweb.org/uploads/images/793954b4fda0b9f37d0f594fbf989b068831449f.jpg)

加载成功~~~

哈哈，至此，修复完成