# iOS APP安全杂谈之三

0x00 序
======

* * *

听说最近IOS让人操碎了心，不到三个月的时间里先后发生[太极越狱被曝存在后门](http://drops.wooyun.org/tips/6919)，[22万iCloud账号及机密信息被多款内置后门越狱插件窃取并泄露](http://www.wooyun.org/bugs/wooyun-2010-0136806)，[XcodeGhost事件](http://drops.wooyun.org/papers/9178)多个知名企业中枪，吓的大家纷纷改了密码。当然像XcodeGhost这样的事情用户是没办法避免的，其编译的APP毕竟是在AppStore上上架的，但是还有一大部分的安全问题其实是完全可以避免的，那就是用户不要越狱，而厂商的APP在运行前检查运行的设备是否安全。现在也有很多APP在使用前都会检查设备是否越狱，如果越狱了则强制退出或者只是提醒一下。那么这次我们就来聊聊越狱之后的那点事。PS：由于本人能力有限，文章难免会有些错误，还望小伙伴们见谅。

0x01 越狱之后更美好？
=============

* * *

越狱之后可以干什么，可以免费的玩各种付费的游戏，可以自动的抢红包，可以在接听电话时自动录音，是的，想想还有点小激动。

![](http://drops.javaweb.org/uploads/images/d29518f0289170bac6e4eb2824ec2dd5ad7cae07.jpg)

图1 其实向往自由没什么错

但事实是越狱之后的风险是用户和厂商都不想看到的，攻击者可以在越狱环境下改变你的APP执行逻辑（例如通过更改函数的返回值来绕过手势密码验证）、可以通过复制应用数据克隆用户或者登陆任意用户、可以通过打补丁的方式绕过目标APP的一些限制等，当然以上的这些危害都是需要一个前提条件：目标APP在越狱环境下能正常使用。

![](http://drops.javaweb.org/uploads/images/54f65e819fc2471af7a6070c081fcfa228ba2c03.jpg)

图2 你以为越狱之后就自由了？

0x02 工具准备
=========

* * *

*   越狱的iPhone或iPad（我这里演示的是IOS 8.4，低版本或高版本的可能会有些不同）；
*   IDA或者Hopper Disassembler；
*   Xcode（主要使用其附带的LLDB），当然对于低版本的IOS可以使用gdb，LLDB具体如何调试可以[参考这里](http://bbs.iosre.com/t/debugserver-lldb-gdb/65)；
*   OpenSSH，itools等其他工具。

0x03 方法准备
=========

* * *

检测越狱的几种方法（可参考《Hacking and Securing ios Application》）：

（1）沙盒的完整性校验
-----------

一些越狱工具会移除沙盒的限制，使程序可以不受限制的运行，这里要说的是关于fork函数的限制。fork函数可以允许你的程序生成一个新的进程，如果沙盒被破坏或者程序在沙盒外运行，那么fork函数就会成功执行，如果沙盒没有被篡改则fork函数执行失败。这里我们通过fork（）的返回值判断子进程是否成功，程序代码如下：

```
#include <stdio.h>
#include <stdlib.h>
static inline int sandbox_integrity_compromised(void) __attribute__((always_inline));
int sandbox_integrity_compromised(void){
    int result = fork();
    if (!result)
        exit(0);
    if (result >= 0)
        return 1;
    return 0;
}
int main(int argc,char *argv[]){
    if(sandbox_integrity_compromised())
    {
    printf("Device is JailBroken\n");
    }else{
    printf("Device is not JailBroken\n");
    }
    return 0;
}

```

（2）文件系统检测
---------

### 1)越狱文件是否存在

越狱之后的小伙伴们一定对Cydia程序很熟悉吧，它是最受欢迎的第三方程序安装器，大部分的越狱工具都会自动给设备进行安装。所以我们可以检测第三方程序文件是否存在来判断设备是否越狱，例如检测Cydia程序是否存在。

### 2) /etc/fstab文件大小

fstab文件通常被越狱工具替换使root分区有读写的权限，但是APP不允许查看该文件的内容，所以我们使用stat函数获得此文件的大小，再根据文件的大小来判断是否越狱。我这里显示越狱后该文件的大小为67字节，有资料中说如果没有越狱该文件的大小应该为80字节。

![](http://drops.javaweb.org/uploads/images/0125c1b45fc37ba394b48caf44f55526c17bbad9.jpg)

图3 使用itools查看fstab文件大小

### 3) 符号链接检测

IOS的磁盘被划分为两个分区：容量较小的是系统分区，另一个是比较大的数据分区。IOS预装的APP会安装在系统分区下的/Applications文件夹下，但是系统分区在设备升级时会被覆盖且容量太小，所以一些越狱工具会重定向这个目录到一个大的用户分区。通常情况下/Applications文件夹会被符号链接到/var/stash文件目录下，APP可以通过lstat函数检测/Applications的属性，如若是目录则代表未越狱，如若是符号链接则代表是越狱设备。

![](http://drops.javaweb.org/uploads/images/626c18f617d59c159912adcec0d103db247e5614.jpg)

图4 使用itools查看符号链接

![](http://drops.javaweb.org/uploads/images/8823910b36bbe01e27f15f572dda45e301f9d756.jpg)

图5 使用命令行查看符号链接

（3）检测system( )函数的返回值等多种方法
-------------------------

这个方法来源于一个网站，同时还介绍了[其他几种检测越狱的方法](https://www.theiphonewiki.com/wiki/Bypassing_Jailbreak_Detection)。其中一个方法就是检测system( )函数的返回值，调用System( )函数，不需要任何参数。在越狱设备上会返回1，在非越狱设备上会返回0。

0x04 可以动手了
==========

* * *

我们使用文件检测的第一种方法来动手测试一下我们的越狱设备。代码如下：

```
#include <sys/stat.h>
#include <stdio.h>
int isJailBroken();
int main(){
    if(isJailBroken()){
        printf("Device is JailBroken\n");
    }else{
        printf("Device is not JailBroken\n");
    }
    return 0;
}
int isJailBroken(){
    struct stat buf;
    int exist = 0;
    char * jbFiles[] =
{"/usr/sbin/sshd","/bin/bash","/Applications/Cydia.app","/private/var/lib/apt","/Libra  ry/MobileSubstrate/MobileSubstrate.dylib"};
    for(int i=0;i < sizeof(jbFiles)/sizeof(char*);i++){
        exist = stat((jbFiles[i]),&buf);
        if(exist == 0){
            return 1;
        }
    }
    return 0;
}

```

以上代码主要检测了`/usr/sbin/sshd`、`/bin/bash`、`/Applications/Cydia.app`、`/private/var/lib/apt`、`/Library/MobileSubstrate/MobileSubstrate.dylib`这几个文件是否存在，如果存在则证明该设备已经越狱。

![](http://drops.javaweb.org/uploads/images/ffc3fb35eaa4450d131320ccd023188f1c35918c.jpg)

图6 检测越狱的POC

在Mac下使用以下命令编译代码：

```
clang -framework Foundation -arch arm64 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk ~/Desktop/jailbreak.c -o ~/Desktop/jailbreak64  -miphoneos-version-min=5.0

```

编译之后将二进制文件拷贝到越狱设备当中并在命令行中运行它。下图可看到运行程序后显示设备已经越狱。

![](http://drops.javaweb.org/uploads/images/3baf747b40dd41d26274a7b61d4f0234a8e2fae4.jpg)

图7 赋予文件权限并执行

0x05 道高一尺魔高一丈
=============

* * *

一些APP正是使用了类似上面的方法来检测自己所在设备是否进行了越狱，为了保证自身的安全性如果设备越狱则自动退出。是的这种做法很明智，但是这也只是增加了安全测试的难度，我们既然知道了检测越狱的原理那么就可以见招拆招了。

（1） 配置好LLDB和debugserver，ssh连接到设备，在设备上使用命令行输入`debugserver -x backboard *:1234 /jailbreak64`附加到jailbreak64，并开启1234端口，等待LLDB的接入。

![](http://drops.javaweb.org/uploads/images/b5cd4716871fa568a331343282fdc2cd8eac7afb.jpg)

图8 在iPad端使用debugserver附加到程序

（2） Mac端切换到`~/Xcode.app/Contents/Developer/usr/bin/`目录下，输入`lldb`，启动后输入`process connect connect://iosip:1234`。

![](http://drops.javaweb.org/uploads/images/02ab37f6da13612d7b7c15af7fdb25853449621e.jpg)

图9 Mac端使用LLDB连接IOS设备

（3） 使用IDA分析程序逻辑结构，这里有一点需要注意：IDA分析的二进制文件必须与LLDB调试的二进制文件相同，这样偏移前基地址、ASLR偏移、偏移后基地址才能对应得上。这里由于我的iPad对应的ARM是ARM64，所以之前在Mac上我使用arm64编译的程序，将编译的程序扔到IDA中分析，这里我使用的是IDAPro6.6中的idaq64.exe进行分析的。（这里所说的ASLR偏移指的是偏移后模块基地址-偏移前模块基地址，偏移后模块基地址：二进制文件加载到内存模块在内存中的首地址；偏移前模块基地址：模块在文件中的首地址）

![](http://drops.javaweb.org/uploads/images/f305737782291a3f9d2c819fad00c9c8dfdbcace.jpg)

图10 ARM64编译后的程序在IDA中的分析

根据上图我们可以看到地址0x100007D1C下方有两个分支，即左边的判断是设备已经越狱，而右边的判断是设备没有越狱。

之所以说这里需要注意是因为我们在使用LLDB调试程序下断点时需要偏移前基地址，而这个偏移前基地址不同场景下是不一样的。下图为ARMv7编译后使用IDA分析的结果，可以看到我们关注的地址变为了0xBE28。

![](http://drops.javaweb.org/uploads/images/bacb80ee2a757b68d3d81322a59d355a384d7e03.jpg)

图11 ARMv7编译后的程序在IDA中的分析

（4） 使用LLDB查看ASLR偏移，此时需要知道几个指令：ni执行下一条指令但不进入函数体，si执行下一条指令会进入函数体，image list列举当前所以模块。

![](http://drops.javaweb.org/uploads/images/d4a88c6e9dc19974348d130bba737dc98ff7a660.jpg)

图12 使用LLDB查看ASLR偏移

上图显示`jailbreak64`还未启动，现在调试还发生在`dyld`内部，接下来一直执行`ni`命令，直到输出结果出现卡顿（大约3秒左右，可以明显察觉到）。到这里不要再使用`ni`命令，`dyld`已经开始加载`jailbreak64`，我们使用`image list -o -f`查看`jailbreak64`的ASLR偏移。

![](http://drops.javaweb.org/uploads/images/6162039eea671f935b62ca1ec0879e7b4650d3d8.jpg)

图13 多次执行ni命令后查看`jailbreak64`的偏移

根据上图显示`jailbreak64`的ASLR偏移为0x40000，所以可以确定断点位置下在‘0x40000+0x100007D1C’处。

（5） 根据以上信息我们就可以安心的下断点了，使用`br s -a`地址用来下断点，使用指令`p`可以打印某处的值，使用指令`register write`给指定的寄存器赋值。

![](http://drops.javaweb.org/uploads/images/7d60f08cc687551820cd969033283bed58e101c6.jpg)

图14 下断点

上图是在‘0x40000+0x100007D1C’处设置断点

![](http://drops.javaweb.org/uploads/images/ca540e70e209c8226dda6bec518b298e659fd1ca.jpg)

图15 查看x0的值并重新赋值来更改程序逻辑

我们使用`p`命令查看一下此时x0的值，发现x0为1，使用`register write`命令将该x0的值改为0，然后输入命令`c`继续，可以看到我们成功的绕过了越狱检测，程序运行结果为设备未越狱。

在Cydia上可以安装xCon软件，据说是目前为止最强大的越狱检测绕过工具，然而我安装在我的iPad上并不适用，应该暂不支持IOS8.4吧。xCon可以绕过四种越狱检测方法（根据特定的越狱文件及文件权限判断设备是否越狱；根据沙盒完整性判断设备是否越狱；根据文件系统的分区是否发生变化来检查设备是否越狱；根据是否安装ssh来判断设备是否越狱）。用最近比较流行的一句话就是“你有一百种方式来检测越狱”，而别人也有一百种方式来抵抗你的检测。

0x06 魔高一尺道高一丈
=============

* * *

刚才我们演示的是LLDB调试来绕过越狱检测，那么如果我的程序阻止调试器附加怎么办？我们来看下面的测试代码。

```
#include <sys/stat.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/sysctl.h>
#include <unistd.h>
inline int checkDebugger() __attribute__((always_inline));
int main(){
    if(checkDebugger()){
        printf("Debugger attached\n");
        return 0;
    }
    printf("Debug detection bypassed\n");
    return 0;
}    

int checkDebugger(){
    int name[4];
    struct kinfo_proc info;
    size_t info_size = sizeof(info);
    info.kp_proc.p_flag = 0;
    name[0] = CTL_KERN;
    name[1] = KERN_PROC;
    name[2] = KERN_PROC_PID;
    name[3] = getpid();
    if(sysctl(name,4,&info,&info_size,NULL,0) == -1){
        return 1;
    }
    return (info.kp_proc.p_flag & P_TRACED) ? 1 : 0;
}

```

当一个应用被调试的时候，会给进程设置一个标识（P_TRACED），可以检测该进程是否有设置这个标识来检测进程是否正在被调试来保护应用。如果该程序发现自己被调试器附加了进程，那么将会输出Debugger attached，如果正常运行该程序则会输出Debug detection bypassed。实验结果如下：

![](http://drops.javaweb.org/uploads/images/1d81f78980ee22e6b8c3fb426f2b99b76adff505.jpg)

图16 正常运行的输出结果

![](http://drops.javaweb.org/uploads/images/256ae2fbae47df8fb4622a9ec1ea2600d274350a.jpg)

图17 使用LLDB调试器附加后的输出结果

在实际应用中可以在得知自己的程序被调试器附加后自动退出，当然这也是可以通过下断点的方式绕过，但是可以通过多处调用该方法来增加攻击的难度。同时上面的代码采用声明内联函数的方法，使编译器将函数功能插到每处代码被调用的地方，而不至于某个特定的功能函数被劫持。

当然除了上述的这种反调试的方法，还可以通过优化标记、去除符号等方法使反汇编复杂化。

0x07 冤冤相报何时了
============

* * *

0x06中所说的反调试还可以通过打补丁的方式绕过，这样就不需要每次都下断点绕过，也会有更多的时间用LLDB来调试其他核心业务。是不是感觉有些乱？因为的确是攻击和防御的方法都有很多，厂商采用多种防御手段来增加攻击成本，而攻击者为了利益或者抱有挑战心理的态度来见招拆招，真是冤冤相报啊。

参考文献：

1.  [美]Jonathan Zdziarski《Hacking and Securing ios Application》
2.  沙梓社，吴航《ios应用逆向工程》
3.  `http://blog.ioactive.com/2015/09/the-ios-get-out-of-jail-free-card.html`