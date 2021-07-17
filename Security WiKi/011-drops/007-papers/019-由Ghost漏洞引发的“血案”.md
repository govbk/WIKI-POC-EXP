# 由Ghost漏洞引发的“血案”

0x00 背景
=======

* * *

最近某安全公司发现的glibc gethostbyname buffer overflow漏洞，该漏洞被命名为ghost，其原因是glibc的Gethostbyname函数在处理传入的畸形域名信息作解析时导致堆溢出，众多网络应用依赖glibc模块的将受到影响，现已经确认受影响的版本是glibc 2.2<=version<=2.17，但是在我们的安全研究人员在测试时触发了另一个有意思的格式串漏洞，让我们来看看具体过程。

0x01 分析细节
=========

* * *

测试环境ubuntu glibc 2.12 python 2.6.6

当我们的研究人员在执行python如下代码时发现程序崩溃

```
import socket
socket.gethostbyname('0'*10000000)

```

![enter image description here](http://drops.javaweb.org/uploads/images/f9e04412602d66aa6f44feaebf26687ab7e5bfe0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/085b75cc20fba281dc0b99aa05d5fa4f50ee6849.jpg)

让我们看看漏洞触发流程，上gdb看看

![enter image description here](http://drops.javaweb.org/uploads/images/6416f27598308cb18daaecbd3571eeb2f29d6be5.jpg)

通过查看异常信息点发现，异常发生在如下代码处

![enter image description here](http://drops.javaweb.org/uploads/images/161e2e95b7f0cc439568e08dcf556dd5291809e0.jpg)

在memcpy函数进行内存拷贝时出错

![enter image description here](http://drops.javaweb.org/uploads/images/0aed440722af98ff884690e2d30534fb830c3de6.jpg)

通过分析发现，rdx是拷贝长度，rsi是源缓冲区，rdi是目的缓冲区，通过分析发现rsi是我们传入的数据，而rdi这个地址不能访问，所以memcpy函数进行拷贝操作时将会出现写入目的地址空间失败，通过分析发现这个地址未初始化，最终导致程序crash.

![enter image description here](http://drops.javaweb.org/uploads/images/95b19612bec180a2c7cec9eb5f3797aaa6598e4d.jpg)

我们通过分析发现python语句

```
Import socket
Socket.gethostbyname(‘0’*10000000)

```

将会调用sscanf格式转换字符串’0’*10000000成整形数据“%d.%d.%d.%d”，我们通过分析glibc里面的源代码stdio-common/vfscanf.c发现，将会如下处理

![enter image description here](http://drops.javaweb.org/uploads/images/0b88b0ed1275b808a734de277aa8541ccf65b4f4.jpg)

关键问题发生在宏ADDW，如下代码是glibc 2.12

![enter image description here](http://drops.javaweb.org/uploads/images/97ec4077ed7f49cc78292bab262d2c0855abfd3c.jpg)

这里代码的作用是把我们传入的字串循环拷贝到栈上面去，alloca函数是开辟栈空间，我们知道默认情况下Linux的栈空间是8MB，当我们传入的参数超长时，会导致栈空间耗尽，导致内存写上溢，当我们写入不可预知的未映射的内存时导致程序崩溃. 通过搜索发现这个格式串漏洞在2.15版被修复

![enter image description here](http://drops.javaweb.org/uploads/images/8b5471e0096bf08807da9181b4c01740085f4278.jpg)

补丁代码如下:

![enter image description here](http://drops.javaweb.org/uploads/images/369ebd9c12bd2457b3abe20571737295deef3041.jpg)

补丁代码的处理逻辑是把传入的数据复制到堆内存里面去而不是在栈空间里面。 https://sourceware.org/bugzilla/show_bug.cgi?id=13138

0x02 漏洞利用
=========

* * *

该格式串漏洞很难利用，拷贝到的目的地址不可预测并且很难控制。

0x03 结论 & 引用
============

* * *

该漏洞会造成远程crash，赶紧升级glibc吧。

感谢阿里安全研究团队和漏洞分析团队的努力

引用:

https://sourceware.org/git/?p=glibc.git;a=commit;f=stdio-common/vfscanf.c;h=3f8cc204fdd077da66ffc8e9595158b469e2b8e5

https://sourceware.org/git/?p=glibc.git;a=blob;f=stdio-common/vfscanf.c;h=7356eeb3626665a0524bbf1be37398ea22e05d7e;hb=6164128f1ca84eea240b66f977054e16b94b3c86

http://seclists.org/fulldisclosure/2015/Jan/111

source:http://blog.sina.com.cn/s/blog_e8e60bc00102vhz7.html