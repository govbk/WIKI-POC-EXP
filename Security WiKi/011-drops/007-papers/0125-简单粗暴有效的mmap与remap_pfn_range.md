# 简单粗暴有效的mmap与remap_pfn_range

0x00 背景
=======

* * *

众所周知，现代操作系统为了安全和统筹硬件的原因，采用了一套非常复杂的管理内存的方式，并由此产生了物理地址，逻辑地址，虚拟地址等概念。这部分内容不负累述，简单来说如下图

![p1](http://drops.javaweb.org/uploads/images/82af0e953525771d34630cc8933d5ccff85e70dc.jpg)

kernel与用户态进程拥有不同的逻辑地址空间，kernel所在的页面拥有更高的权限，用户权限是不可以随意更改的，否则岂不是可以改掉自己的权限，为所欲为。

![p2](http://drops.javaweb.org/uploads/images/d6a83d84e35c4d86fc9a0ca54ffdaa224b845006.jpg)

不过这也不是完全密不透风的墙，内核提供了多种途径供用户态交流数据。其中如果需要在短时间内交换大量数据，并且有实时的要求，linux kernel 提供了一种简单有效的方式：共享内存——mmap syscall。

原理也非常简单，映射给kernel的物理页面也同样映射一份给用户进程，并且修改掉权限属性。这样的话分属不同地址空间的两块内存实际上对应的是同一个物理页面，一方修改数据，另一方也能够实时看到变化。

![p3](http://drops.javaweb.org/uploads/images/5caf9bc26ccdf0dde04dec595269ac2e216a140e.jpg)

一般的应用场景是在嵌入式设备的外设中，比如要实施刷新LED显示屏，实施记录大量传感器数据，等。这需要开发人员在自己的驱动程序和用户代码中同时实现mmap的逻辑才能够实现。

首先，在自定义的驱动文件中要提供这样的接口函数：

![p4](http://drops.javaweb.org/uploads/images/3ca8c21d46c6455f28da5821b6466be7f3391522.jpg)

内核函数`remap_pfn_range()`会根据需求映射页面进用户进程。

详见：[http://www.makelinux.net/ldd3/chp-15-sect-2](http://www.makelinux.net/ldd3/chp-15-sect-2)

随后在用户程序中简单掉用这个自定义的mmap函数就可以建立起页面映射，达到共享内存的目的了。

0x01 漏洞
=======

* * *

越是简单好用的，就越容易出现问题。

函数`remap_pfn_range()`并不会检查传入的参数，它会完全按照需求的内存起始位置，所需长度，访问权限，去映射页面进用户态。所有这些检查都需要自定义的驱动中实现的mmap函数去完成。

上面的截图是官方文档中给出的例子，当然不能用这段代码直接用到产品中！

比如如下的这个产品实现：  
[https://github.com/rajamalw/galaxy-s5360/blob/master/modules/drivers/video/hantro/ldriver/kernel_26x/hx170dec.c](https://github.com/rajamalw/galaxy-s5360/blob/master/modules/drivers/video/hantro/ldriver/kernel_26x/hx170dec.c)

```
/*------------------------------------------------------------------------------
    Function name   : hx170dec_mmap
    Description     : mmap method
    Return type     : int
------------------------------------------------------------------------------*/
static int hx170dec_mmap(struct file *file, struct vm_area_struct *vma)
{
    if (vma->vm_end - vma->vm_start >
        ((DEC_IO_SIZE + PAGE_SIZE - 1) & PAGE_MASK))
        return -EINVAL;

    vma->vm_page_prot = pgprot_noncached(vma->vm_page_prot);
    /* Remap-pfn-range will mark the range VM_IO and VM_RESERVED */
    if (remap_pfn_range(vma,
                vma->vm_start,
                (DEC_IO_BASE >> PAGE_SHIFT),
                vma->vm_end - vma->vm_start, vma->vm_page_prot)) {
        pr_err("%s(): remap_pfn_range() failed\n", __FUNCTION__);
        return -EINVAL;
    }

    return 0;
}

```

只是稍微对申请的长度做了检查，其他的理所当然地相信了用户代码。

造成的后果很严重：

*   [https://labs.mwrinfosecurity.com/system/assets/762/original/mwri_advisory_huawei_driver-root-exploit.pdf](https://labs.mwrinfosecurity.com/system/assets/762/original/mwri_advisory_huawei_driver-root-exploit.pdf)
*   [WooYun: MTK相机内核驱动缺陷导致的权限提升](http://www.wooyun.org/bugs/wooyun-2013-021778)
*   [WooYun: 华为最新Ascend P6手机内核缺陷造成本地权限提升](http://www.wooyun.org/bugs/wooyun-2013-026290)
*   [WooYun: 华为海思平台解码器驱动缺陷以及权限设置不当](http://www.wooyun.org/bugs/wooyun-2013-021777)

我们再来看一个比较好的例子：  
[https://github.com/nirodg/android_device_huawei_hwp7/blob/master/kernel/huawei/hwp7/drivers/hik3/g1dec/hx170dec.c](https://github.com/nirodg/android_device_huawei_hwp7/blob/master/kernel/huawei/hwp7/drivers/hik3/g1dec/hx170dec.c)

```
static int hx170dec_mmap(struct file *file, struct vm_area_struct *vma)
{
    unsigned long start = vma->vm_start;
    unsigned long size = vma->vm_end - vma->vm_start;
    int retval = 0;

    unsigned long pyhs_start = vma->vm_pgoff << PAGE_SHIFT;
    unsigned long pyhs_end = pyhs_start + size;
    if(!(pyhs_start >= hisi_reserved_codec_phymem//not codec memory
            && pyhs_end <= hisi_reserved_codec_phymem + HISI_MEM_CODEC_SIZE)
        && !(pyhs_start >= hx170dec_data.iobaseaddr//not io address
            && pyhs_end <= hx170dec_data.iobaseaddr + hx170dec_data.iosize)) {
        printk(KERN_ERR "%s(%d) failed map:0x%lx-0x%lx\n", __FUNCTION__, __LINE__, pyhs_start, pyhs_end);
        return -EFAULT;
    }
    /* make buffers write-thru cacheable */

    vma->vm_page_prot = pgprot_noncached(vma->vm_page_prot);
    if (remap_pfn_range(vma, start, vma->vm_pgoff, size, vma->vm_page_prot))
        retval = -ENOBUFS;

    return retval;
}

```

在调用`remap_pfn_range`函数之前做了诸多检查，限制了申请地址的起始和结束位置。

0x02 其他
=======

* * *

android系统的整体安全架构是很繁复庞大的，上文中出现的漏洞如果发生在某个驱动中是不能单独被利用提权的。因为其他应用没有权限去访问这个有问题的驱动。但是如果这个驱动的访问权限再出错，比如：

![P5](http://drops.javaweb.org/uploads/images/192e27d11316fb0dbb0da8927d505c6fcde823d9.jpg)

那么连续的犯错下来，对于攻击者来说，就真的是666了。

0x03 结语
=======

* * *

本文所讨论的安全问题在某厂商的设备中经常出现，并且时间跨度长达几年，希望贵厂能够提高安全意识，加班赶工的同时也注意下代码质量。