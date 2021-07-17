# Cycript中的注入技巧分析

0x00 前言
=======

* * *

目前,在iOS中很多dylib是通过DYLDINSERTLIBRARIES来动态注入的,关于这种注入的防范方式最好的方法是在程序编译时,添加一个空的restict区段,因为dyld在load动态库时会检查区段中是否存在restict,如果存在那么就跳过加载。详情参见:[防止tweak依附,App有高招;破解App保护,tweak留一手](http://bbs.iosre.com/t/tweak-app-app-tweak/438)

前段时间,发现自己写的一个demo加了restict之后,仍然能够被cycript挂载,顺势分析了cycript的注入原理。

0x01 cycript简介
==============

* * *

cycript是大神saurik开发的一个非常强大的工具,可以让开发者在命令行下和应用交互,在运行时查看和修改应用。其中的底层实现,是通过苹果的JavaScriptCore.framework来打通iOS与javascript的桥梁。具体详解,[参考](http://www.cycript.org/)

0x02 cycript结构
==============

* * *

在安装cycript过后,通过cydia可以看到安装cycript之后影响的目录结构

![](http://drops.javaweb.org/uploads/images/7f656b0f1cb1c479b30287d38ac46dd392c9b3c1.jpg)

虽然只提到这几个文件,但是在/usr/bin下,还有一个cynject的可执行文件和cycript相关,后面分析会发现,这个程序才是注入的核心文件。我这里,通过scp把这些文件都下载到本地,方便分析。

0x03 cycript主程序
===============

* * *

分析Cycript主程序时,观察到里面有一个InjectLibrary的函数被调用

```
void InjectLibrary(int pid, int argc, const char *argv[]) {
    auto cynject(LibraryFor(reinterpret_cast<void *>(&main)));
    auto slash(cynject.rfind('/'));
    _assert(slash != std::string::npos);
    cynject = cynject.substr(0, slash) + "/cynject";
    auto library(LibraryFor(reinterpret_cast<void *>(&MSmain0)));
    bool ios(false);
    for (decltype(header->ncmds) i(0); i != header->ncmds; ++i) {
        if (command->cmd == LC_VERSION_MIN_IPHONEOS)
            ios = true;
        command = shift(command, command->cmdsize);
    }
    _syscall(munmap(map, size)); // XXX: _scope
    auto length(library.size());
    _assert(length >= 6);
    length -= 6;
    _assert(library.substr(length) == ".dylib");
    library = library.substr(0, length);
    library += ios ? "-sim" : "-sys";
    library += ".dylib";
#endif
    std::ostringstream inject;
    inject << cynject << " " << std::dec << pid << " " << library;
    for (decltype(argc) i(0); i != argc; ++i)
        inject << " " << argv[i];   

    _assert(system(inject.str().c_str()) == 0);
}

```

程序在解析过程中,注入代码前会对会环境进行检查,并且进行字符串格式化拼接,构造一个shell命令,用来做调用system函数的参数,来执行cynject注入功能。

0x04 cynject注入程序
================

* * *

接下来分析cynject,在函数subb308的位置可以看到,通过调用taskfor_pid获取到进程句柄结构。通过该结构,可以对进程能够有访问权限。

![](http://drops.javaweb.org/uploads/images/831c7249f1496f61bcb58c399b94a97588f4ce4f.jpg)

举个栗子:

```
mach_port_t rtask;
task_for_pid(mach_task_self(), pid, &rtask);

```

程序为了让内存中的dylib有执行能力,把dylib通过线程的方式来加载。继续往下看,就发现进程创建一个被挂起的线程

![](http://drops.javaweb.org/uploads/images/73c1c62e43ecd5075bb50d4e8cf7467dd981c454.jpg)

拿到句柄结构,在进程的空间中申请内存,将dylib映射之后,写入到这片申请的空间里面。

![](http://drops.javaweb.org/uploads/images/427d8429369687eab1dc28f51f3f5e540d615165.jpg)

所以,代码逻辑大概是这样的:

```
vm_size_t codeSize = 124;
vm_address_t rAddress;
vm_allocate(rtask, &rAddress, codeSize, TRUE);
vm_write(rtask, rAddress, &code, (mach_msg_type_number_t)codeSize);
vm_protect(rtask, rAddress, codeSize, FALSE, VM_PROT_READ | VM_PROT_WRITE | VM_PROT_EXECUTE);

```

最后,等dylib加载完全后,为dylib恢复启动并执行使其开始运行

![](http://drops.javaweb.org/uploads/images/51b5b6414b868e39cfb9632ed89ef97c8f206098.jpg)

梳理一下大体的流程:

> ( 1 )获取 PID 的进程句柄  
> ( 2 )在 PID 中创建一个被挂起的线程  
> ( 3 )在 PID 进程中申请一片用于加载 DYLIB 的内存  
> ( 4 )调用 RESUME ,恢复线程

OVER~

说到这里,流程差不多梳理完了,拿一个dylib测试一下

![](http://drops.javaweb.org/uploads/images/b42becbf01d27e3b1f31b04e02858a1ec06385e4.jpg)

通过lldb连上程序,看一下内存加载模块:

![](http://drops.javaweb.org/uploads/images/0bbeb23ec5126aec3523540ea0db0f69ee1e2ac8.jpg)

可以发现,我们恶意的dylib已经注入到进程中了。

0x05 后记
=======

* * *

cycript里面还有一些比较有意思的东西,大家可以深挖一下。另外,上面的内容不要用到自己企业的app产品中,按照苹果appStore原则,调用私有api以及动态注入代码的操作,是会被下架的。