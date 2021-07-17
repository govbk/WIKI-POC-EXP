# iOS冰与火之歌 – UAF and Kernel Pwn

**作者：耀刺，蒸米，黑雪 @阿里移动安全**  
英文版：[http://translate.wooyun.io/2016/06/12/54.html](http://translate.wooyun.io/2016/06/12/54.html)

0x00 序
======

* * *

冰指的是用户态，火指的是内核态。如何突破像冰箱一样的用户态沙盒最终到达并控制如火焰一般燃烧的内核就是《iOS冰与火之歌》这一系列文章将要讲述的内容。这次给大家带来的是 Use After Free 的漏洞利用方式以及iOS 9.0上如何利用UAF攻击iOS内核的技术。除此以外我们还公布了一个在iOS9.3.2中刚刚被修复的内核堆溢出漏洞，可以用来攻击iOS 9.3.2以下版本的iOS内核并实现iOS Pwn的终极目标 - 越狱。

《iOS冰与火之歌》系列的目录如下：

1.  Objective-C Pwn and iOS arm64 ROP
    
2.  在非越狱的iOS上进行App Hook（番外篇）
    
3.  App Hook答疑以及iOS 9砸壳（番外篇）
    
4.  利用XPC过App沙盒
    
5.  UAF and Kernel Pwn
    

另外文中涉及代码可在我的github下载:  
[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x01 Use After Free
===================

* * *

Use After Free简称UAF，是一种常见的堆漏洞利用方式。在Pangu9的越狱中，就是利用了iOS 9内核中的一处UAF漏洞获取了iOS最高权限并完成了越狱。在我们讲这个漏洞之前，可能有很多同学对UAF并不是很了解，所以我们先简单介绍一下什么是UAF以及如何利用UAF漏洞（老鸟的话可以直接跳过这一节）。

我们先来看一段程序（全部源码在github）：

```
class Human
{
public:
    virtual void setValue(int value)=0;
    virtual int getValue()=0;

protected:
    int mValue;
};  

class Talker : public Human
{
public:
    void setValue(int value){
        mValue = value;
    }
    int getValue(){
        mValue += 1;
        cout<<"This is Talker's getValue"<<endl;
        return mValue;
    }
};  

class Worker : public Human
{
public:
    void setValue(int value){
        mValue = value;
    }
    int getValue(){
        cout<<"This is Worker's getValue"<<endl;
        mValue += 100;
        return mValue;
    }
};  

void handleObject(Human* human)
{
    human->setValue(0);
    cout<<human->getValue()<<endl;
}

```

这段程序有三个类，其中Worker和Talker都继承Human这个类，并且他们都分别实现了`setValue()`和`getValue()`这两个函数。因此当程序调用`handleObject()`的时候，无论传入的参数是Worker还是Talker，`handleObject()`都可以进行处理。

我们接下来看main函数：

```
int main(void) {
        Talker *myTalker = new Talker();
        printf("myTalker=%p\n",myTalker);   

        handleObject(myTalker);

        free(myTalker); 

        Worker *myWorker = new Worker();
        printf("myWorker=%p\n",myWorker);   

        handleObject(myTalker);
}

```

我们先new一个Talker，然后调用`handleObject()`打印它的value，然后free掉这个Talker。接着我们new一个Worker，然后继续调用`handleObject()`打印Talker(注意:不是Worker)的value，会发生什么呢？正常情况下，程序员调用`handleObject(myTalker)`，是期望处理Talker这个对象，但是Talker这个对象已经被free了，并且指针没有置为NULL。这时候，如果有另一个对象(e.g., Worker)刚好被分配在了Talker指针所指向的地址，`handleObject()`也会对这个对象进行处理，并且不会报错。这，就是一个典型的UAF漏洞。我们来看一下程序执行的结果：

```
Minde-iPad:/tmp root# ./hello
myTalker=0x17d6b150
This is Talker's getValue
1
myWorker=0x17d6b150
This is Worker's getValue
100

```

可以看到MyTalker对象在内存中的地址为0x17d6b150，然后MyTalker就被free掉了。随后，程序又创建了另一个对象myWorker。因为堆的特性，系统会把刚刚free掉的内存再分配给Worker。因此myWorker在内存中的地址也是0x17d6b150。所以当程序调用`handleObject(myTalker)`的时候，本应该期待调用Talker's`getValue()`函数却调用了Worker's`getValue()`函数，这就造成一个UAF错误。

如果程序不是在myTalker后面创建一个myWorker对象，而是自己`malloc()`一段可控的内存呢？我们再来看下面这段程序：

```
int main(void) {    

        Talker *myTalker = new Talker();
        printf("myTalker=%p\n",myTalker);   

        handleObject(myTalker);

        free(myTalker);

        int size=16;
        void *uafTalker = (void*) malloc(size);
        memset(uafTalker, 0x41,size);
        printf("uafTalker=%p\n",uafTalker); 

        handleObject(myTalker);
        return 0;
}

```

我们并没有malloc一个Worker对象，而是自己malloc了一段16个字节的内存，并且把数据全部填充为0x41。如果free掉的myTalker指针指向了这段内存，并调用了`handleObject(myTalker)`会发生什么事情呢？

在运行程序前，我们先用lldb对程序进行调试：

![](http://drops.javaweb.org/uploads/images/783b9dcdf70ce41ea7a72dee80dc50f307be283e.jpg)

然后用lldb连接程序并在main函数下一个断点：

![](http://drops.javaweb.org/uploads/images/4ee7119cee6d08777e7c01d8cbad4678e373affc.jpg)

确保程序正常进入main函数后，继续运行程序：

![](http://drops.javaweb.org/uploads/images/915f3a819820110898b59003e99f557e979aad2c.jpg)

当程序执行到`handleObject(myTalker)`的时候，我们就能看到很有意思的error了：程序试图从r0这个地址读取数值到r2，然后`blx r2`，但是r0的值为0x41414141。这是因为我们在myTalker free后的malloc的内存刚好又重新分配在了myTalker指针指向的地址，随后程序调用了myTalker的的函数，根据c++的机制，程序会从myTalker的vTable里获取函数地址，但是我们已经利用UAF把vTable给填充成了0x41414141，所以才会报错。既然我们可以利用UAF控制r0的内容，只要配合上heap spray，我们就可以做到控制pc并执行rop指令了。Heap Spray的技巧可以参考我之前写的文章：[Objective-C Pwn and iOS arm64 ROP](http://drops.wooyun.org/papers/12355)。

0x02 iOS 9.0 UAF in IOHIDResourceUserClient
===========================================

* * *

简单了解了UAF的原理以后，我们来看一下pangu越狱中搞定iOS 9.0内核的UAF漏洞。这个漏洞存在于IOHIDResource这个内核服务中。有一个好消息是这个服务是开源的（在IOHIDFamily中，我会把源码放到github上），

所以我们来看一下有漏洞的代码：

![](http://drops.javaweb.org/uploads/images/19b2ffc49f485d83d11104a93bc7a00342964a69.jpg)

![](http://drops.javaweb.org/uploads/images/08df4fb561c040bbc3cbe742d9c0c929befa1158.jpg)

在`terminateDevice()`这个函数中，内核服务调用`OSSafeRelease()`来释放一个device，但我们可以发现，虽然_device这个指针所指向的device被释放了，但是_device并没有置为NULL。如果我们再次调用已经释放后的device的函数的话就会触发UAF漏洞。随后Apple在9.1中修复了该漏洞，可以看一下修复的代码：

![](http://drops.javaweb.org/uploads/images/6b96274268f7bc80cd2cde1ed7ff2a83b74dba3e.jpg)

![](http://drops.javaweb.org/uploads/images/a6a2de63a1f2cc363439336b04409820c82b4181.jpg)

可以看到`OSSafeRelease()`已经变成了`OSSafeReleaseNULL()`，从而修复了UAF漏洞。

那么如何利用这个UAF漏洞呢？首先我们先利用IOKit提供的API创建一个device：

![](http://drops.javaweb.org/uploads/images/f443559c7c2538630f8c9ea05da81072a459c2e1.jpg)

然后我们调用`terminateDevice()`方法将这个device释放掉：

![](http://drops.javaweb.org/uploads/images/73954d600b892f7034e1bfafdb3c3d5ba24150af.jpg)

然后我们再用释放后的device去调用一些需要用到device的函数，比如说`IOHIDResourceDeviceUserClient::handleReport()`就会触发UAF漏洞：

![](http://drops.javaweb.org/uploads/images/d1aa487c3ee351cd71a3bdfbf20621ebee1d6e6e.jpg)

因为_device已经被释放掉了，但是_device这个指针的内容并没有赋值为NULL，所以函数会继续执到`_device->handleReportWithTime(timestamp, report)`。接着服务会去_device指向的内存地址查找vtable中的函数，如果我们能够在内存中malloc一段可控的内存并伪造一个fake的vtable，并且让这段内存刚好分配在_device所指向的地址，我们就可以成功的控制内核的PC指针了。

利用这个思路，我们成功的写出了利用程序，运行程序后，手机会重启，随后在`~/Library/Logs/CrashReporter/MobileDevice/`目录下的panic log中可以看到，我们已经成功的控制了pc指针并指向了0xdeadbeefdeadbeef：

![](http://drops.javaweb.org/uploads/images/fb8fb7fbdefee4d36dc42a3fe264ad391352e5f0.jpg)

对越狱来说，控制了内核的PC指针还只是一个开始，随后还要获取KASLR，利用ROP对内核进行读写，然后对内核进行patch，将签名校验disable等等，因为篇幅原因，这里就不一一介绍了，欢迎继续关注我们以后的文章。

0x03 inpuTbag – 一个影响了苹果设备15年的内核堆溢出漏洞
====================================

* * *

苹果在不久前发布的9.3.2中，修补一个非常典型的内核堆溢出漏洞，该漏洞存在于IOHIDFamily中。配合用户态漏洞触发，该漏洞能绕过内核所有安全机制，转化成内核任意读写，从而完成越狱。有该漏洞的代码最早是在2002年发布的mac os 10.2中引入，几乎影响了Apple全系设备15年之久。

出现漏洞的内核代码如下 ([http://opensource.apple.com/source/IOHIDFamily/IOHIDFamily-701.20.10/IOHIDFamily/IOHIDDevice.cpp](http://opensource.apple.com/source/IOHIDFamily/IOHIDFamily-701.20.10/IOHIDFamily/IOHIDDevice.cpp))：

```
IOHIDDevice::postElementValues(…) {
…
 maxReportLength = max(_maxOutputReportSize, _maxFeatureReportSize);           - - - - - - - a
 report = IOBufferMemoryDescriptor::withCapacity(maxReportLength, kIODirectionNone);           - - - - - - - b
…
 reportData = (UInt8 *)report->getBytesNoCopy()           - - - - - - - c
…
 element->createReport(reportID, reportData, &reportLength, &element);//IOHIDElementPrivate::createReport           - - - - - - - d
…
}   

IOHIDElementPrivate::createReport(…) {
…
            writeReportBits( _elementValue->value,      /* source buffer      */           - - - - - - - e
                           (UInt8 *) reportData,    /* destination buffer */
                           (_reportBits * _reportCount),/* bits to copy       */
                           _reportStartBit);        /* dst start bit      */                           
…
}

```

代码行-a是漏洞的关键，IOHIDDevice的Report总共有三种类型：Output，Feature，Input；这些Report的Size是在创建IOHIDDevice时用户输入指定。这里只是根据Output，Feature来判断可能最大的Report Size是错误的，因为Input的size可能比OutPut和Feature都大。

代码行-b根据maxReportLength创建内核堆buffer。

代码行-c用来拿到创建的内核堆的buffer指针。

代码行-d是将Report内容保存到代码行-b创建的buffer，那么只要Post的Report类型是Input而且Size >`max(_maxOutputReportSize, _maxFeatureReportSize)`便能成功溢出。

代码行-e 是`createReport ()`的一部分。`writeReportBits()`在report count等于1的情况下等同于memmove操作，将clientMemoryForType中设定的Report内容拷贝到代码行-b创建的Buffer。

因此该漏洞可以从任意kalloc zone，达成任意长度的堆溢出。因为该漏洞是利用inpuT report来攻击iOS内核，再加上Tbag是《越狱》中一个非常有名的角色，所以我们将这个漏洞命名为inpuTbag。

![](http://drops.javaweb.org/uploads/images/850a02eee6c77bdcbbbd4b01f6dd5ae43747c21c.jpg)

0x04 One More Thing – iOS 9.2.1越狱
=================================

* * *

我们已经成功的利用inpuTbag堆溢出漏洞完成了iOS 9.2.1的越狱，如下是越狱的视频和截图 (因为Cydia的安装不太稳定，容易造成白苹果，所以我们的demo改成安装一个未签名的terminal app，并且可以用root权限执行任意指令，并且可以在系统的根目录下创建任意文件)：

![null](http://drops.javaweb.org/uploads/images/09a51ac0ec79b505473b160e8f62c6e811764004.jpg)

![null](http://drops.javaweb.org/uploads/images/124bed6fc29ac34964fe9f19291a867d51d5e09b.jpg)

0x05 总结
=======

* * *

这篇文章介绍了Use After Free的漏洞利用方式以及iOS 9.0上如何利用UAF攻击iOS内核的技术。除此以外我们还公布了一个在iOS9.3.2中刚刚被修复的内核堆溢出漏洞，并展示了iOS 9.2.1的越狱。另外文中涉及代码可在我的github下载:

[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x06 参考资料
=========

* * *

1.  Hacking from iOS 8 to iOS 9, POC 2015