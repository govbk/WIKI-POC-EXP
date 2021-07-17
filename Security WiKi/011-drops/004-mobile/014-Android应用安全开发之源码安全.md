# Android应用安全开发之源码安全

0x00 简介
=======

* * *

Android apk很容易通过逆向工程进行反编译，从而是其代码完全暴露给攻击者，使apk面临破解，软件逻辑修改，插入恶意代码，替换广告商ID等风险。我们可以采用以下方法对apk进行保护.

0x01 混淆保护
=========

* * *

混淆是一种用来隐藏程序意图的技术，可以增加代码阅读的难度，使攻击者难以全面掌控app内部实现逻辑，从而增加逆向工程和破解的难度，防止知识产权被窃取。

代码混淆技术主要做了如下的工作：

1.  通过对代码类名，函数名做替换来实现代码混淆保护
2.  简单的逻辑分支混淆

已经有很多第三方的软件可以用来混淆我们的Android应用，常见的有：

*   Proguard
*   DashO
*   Dexguard
*   DexProtector
*   ApkProtect
*   Shield4j
*   Stringer
*   Allitori

这些混淆器在代码中起作用的层次是不一样的。Android编译的大致流程如下：

```
Java Code(.java) -> Java Bytecode(.class) -> Dalvik Bytecode(classes.dex)

```

有的混淆器是在编译之前直接作用于java源代码，有的作用于java字节码，有的作用于Dalvik字节码。但基本都是针对java层作混淆。

相对于Dalvik虚拟机层次的混淆而言，原生语言（C/C++）的代码混淆选择并不多，Obfuscator-LLVM工程是一个值得关注的例外。

代码混淆的优点是使代码可阅读性变差，要全面掌控代码逻辑难度变大；可以压缩代码，使得代码大小变小。但也存在如下缺点：

1.  无法真正保护代码不被反编译；
2.  在应对动态调试逆向分析上无效；
3.  通过验证本地签名的机制很容易被绕过。

也就是说，代码混淆并不能有效的保护应用自身。

[http://www.jianshu.com/p/0c23e0a886f4](http://www.jianshu.com/p/0c23e0a886f4)

0x02 二次打包防护
===========

* * *

### 2.1 Apk签名校验

每一个软件在发布时都需要开发人员对其进行签名，而签名使用的密钥文件时开发人员所独有的，破解者通常不可能拥有相同的密钥文件，因此可以使用签名校验的方法保护apk。Android SDK中PackageManager类的getPackageInfo()方法就可以进行软件签名检测。

```
public class getSign {
    public static int getSignature(PackageManager pm , String packageName){
    PackageInfo pi = null;
    int sig = 0;
    Signature[]s = null;
    try{
        pi = pm.getPackageInfo(packageName, PackageManager.GET_SIGNATURES);
        s = pi.signatures;
        sig = s[0].hashCode();//s[0]是签名证书的公钥，此处获取hashcode方便对比
    }catch(Exception e){
        handleException();
    }
    return sig;
    }
}

```

主程序代码参考：

```
pm = this.getPackageManager();
int s = getSign.getSignature(pm, "com.hik.getsinature");
if(s != ORIGNAL_SGIN_HASHCODE){//对比当前和预埋签名的hashcode是否一致
    System.exit(1);//不一致则强制程序退出
}

```

### 2.2 Dex文件校验

重编译apk其实就是重编译了classes.dex文件，重编译后，生成的classes.dex文件的hash值就改变了，因此我们可以通过检测安装后classes.dex文件的hash值来判断apk是否被重打包过。

1.  读取应用安装目录下`/data/app/xxx.apk`中的classes.dex文件并计算其哈希值，将该值与软件发布时的classes.dex哈希值做比较来判断客户端是否被篡改。
2.  读取应用安装目录下`/data/app/xxx.apk`中的META-INF目录下的MANIFEST.MF文件，该文件详细记录了apk包中所有文件的哈希值，因此可以读取该文件获取到classes.dex文件对应的哈希值，将该值与软件发布时的classes.dex哈希值做比较就可以判断客户端是否被篡改。

为了防止被破解，软件发布时的classes.dex哈希值应该存放在服务器端。

```
private boolean checkcrc(){
    boolean checkResult = false;
    long crc = Long.parseLong(getString(R.string.crc));//获取字符资源中预埋的crc值
    ZipFile zf;
    try{
        String path = getApplicationContext().getPackageCodePath();//获取apk安装路径
        zf = new ZipFile(path);//将apk封装成zip对象
        ZipEntry ze = zf.getEntry("classes.dex");//获取apk中的classes.dex
        long CurrentCRC = ze.getCrc();//计算当前应用classes.dex的crc值
        if(CurrentCRC != crc){//crc值对比
            checkResult = true;
        }
    }catch(IOException e){
        handleError();
        checkResult = false;
    }
    return checkResult;
}

```

另外由于逆向c/c++代码要比逆向Java代码困难很多，所以关键代码部位应该使用Native C/C++来编写。

0x03 SO保护
=========

* * *

Android so通过C/C++代码来实现，相对于Java代码来说其反编译难度要大很多，但对于经验丰富的破解者来说，仍然是很容易的事。应用的关键性功能或算法，都会在so中实现，如果so被逆向，应用的关键性代码和算法都将会暴露。对于so的保护，可以才有编译器优化技术、剥离二进制文件等方式，还可以使用开源的so加固壳upx进行加固。

**编译器优化技术**

为了隐藏核心的算法或者其它复杂的逻辑，使用编译优化技术可以帮助混淆目标代码，使它不会很容易的被攻击者反编译，从而让攻击者对特定代码的理解变得更加困难。如使用LLVM混淆。

**剥离二进制文件**

剥离本地二进制文件是一种有效的方式，使攻击者需要更多的时间和更高的技能水平来查看你的应用程序底层功能的实现。剥离二进制文件，就是将二进制文件的符号表删除，使攻击者无法轻易调试或逆向应用。在Android上可以使用GNU/Linux系统上已经使用过的技术，如sstriping或者UPX。

UPX对文件进行加壳时会把软件版本等相关信息写入壳内，攻击者可以通过静态反汇编可查看到这些壳信息，进而寻找对应的脱壳机进行脱壳，使得攻击难度降低。所以我们必须在UPX源码中删除这些信息，重新编译后再进行加壳，步骤如下：

1.  使用原始版本对文件进行加壳。
2.  使用IDA反汇编加壳文件，在反汇编文件的上下文中查找UPX壳特征字符串。
3.  在UPX源码中查找这些特征字符串，并一一删除。

[https://www.nowsecure.com/resources/secure-mobile-development/coding-practices/code-complexity-and-obfuscation/](https://www.nowsecure.com/resources/secure-mobile-development/coding-practices/code-complexity-and-obfuscation/)

0x04 资源文件保护
===========

* * *

如果资源文件没有保护，则会使应用存在两方面的安全风险：

1.  通过资源定位代码，方便应用破解 反编译apk获得源码，通过资源文件或者关键字符串的ID定位到关键代码位置，为逆向破解应用程序提供方便.
2.  替换资源文件，盗版应用 "if you can see something, you can copy it"。Android应用程序中的资源，比如图片和音频文件，容易被复制和窃取。

可以考虑将其作为一个二进制形式进行加密存储，然后加载，解密成字节流并把它传递到BitmapFactory。当然，这会增加代码的复杂度，并且造成轻微的性能影响。

不过资源文件是全局可读的，即使不打包在apk中，而是在首次运行时下载或者需要使用时下载，不在设备中保存，但是通过网络数据包嗅探还是很容易获取到资源url地址。

0x05 反调试技术
==========

* * *

### 5.1 限制调试器连接

应用程序可以通过使用特定的系统API来防止调试器附加到该进程。通过阻止调试器连接，攻击者干扰底层运行时的能力是有限的。攻击者为了从底层攻击应用程序必须首先绕过调试限制。这进一步增加了攻击复杂性。Android应用程序应该在manifest中设置`Android:debuggable=“false”`，这样就不会很容易在运行时被攻击者或者恶意软件操纵。

### 5.2 Trace检查

应用程序可以检测自己是否正在被调试器或其他调试工具跟踪。如果被追踪，应用程序可以执行任意数量的可能攻击响应行为，如丢弃加密密钥来保护用户数据，通知服务器管理员，或者其它类型自我保护的响应。这可以由检查进程状态标志或者使用其它技术，如比较ptrace附加的返回值，检查父进程，黑名单调试器进程列表或通过计算运行时间的差异来反调试。

*   [https://github.com/obfuscator-llvm/obfuscator/wiki](https://github.com/obfuscator-llvm/obfuscator/wiki)
*   [https://www.nowsecure.com/resources/secure-mobile-development/coding-practices/code-complexity-and-obfuscation/](https://www.nowsecure.com/resources/secure-mobile-development/coding-practices/code-complexity-and-obfuscation/)

**a.父进程检测**

通常，我们在使用gdb调试时，是通过gdb这种方式进行的。而这种方式是启动gdb，fork出子进程后执行目标二进制文件。因此，二进制文件的父进程即为调试器。我们可通过检查父进程名称来判断是否是由调试器fork。示例代码如下

```
#include <stdio.h>
#include <string.h>
 
int main(int argc, char *argv[]) {
   char buf0[32], buf1[128];
   FILE* fin;
 
   snprintf(buf0, 24, "/proc/%d/cmdline", getppid());
   fin = fopen(buf0, "r");
   fgets(buf1, 128, fin);
   fclose(fin);
 
   if(!strcmp(buf1, "gdb")) {
       printf("Debugger detected");
       return 1;
   }  
   printf("All good");
   return 0;
}

```

这里我们通过getppid获得父进程的PID，之后由/proc文件系统获取父进程的命令内容，并通过比较字符串检查父进程是否为gdb。实际运行结果如下图所示：

![p1](http://drops.javaweb.org/uploads/images/655f2c27363be8c6f5ad6272ba6e1822fe3a68b0.jpg)

**b.当前运行进程检测**

例如对`android_server`进程检测。针对这种检测只需将`android_server`改名就可绕过

```
pid_t GetPidByName(const charchar *as_name) {  
        DIR *pdir = NULL;  
        struct dirent *pde = NULL;  
        FILEFILE *pf = NULL;  
        char buff[128];  
        pid_t pid;  
        char szName[128];  
        // 遍历/proc目录下所有pid目录    
        pdir = opendir("/proc");  
        if (!pdir) {  
                perror("open /proc fail.\n");  
                return -1;  
        }  
        while ((pde = readdir(pdir))) {  
                if ((pde->d_name[0] < '0') || (pde->d_name[0] > '9')) {  
                        continue;  
                }  
                sprintf(buff, "/proc/%s/status", pde->d_name);  
                pf = fopen(buff, "r");  
                if (pf) {  
                        fgets(buff, sizeof(buff), pf);  
                        fclose(pf);  
                        sscanf(buff, "%*s %s", szName);  
                        pid = atoi(pde->d_name);  
                        if (strcmp(szName, as_name) == 0) {  
                                closedir(pdir);  
                                return pid;  
                        }  
                }  
        }  
        closedir(pdir);  
        return 0;  
}

```

**c.读取进程状态(/proc/pid/status)**

State属性值T 表示调试状态，TracerPid 属性值正在调试此进程的pid,在非调试情况下State为S或R, TracerPid等于0

![p2](http://drops.javaweb.org/uploads/images/8e9987def5516d6d046f85c4a97646448dfe84fb.jpg)

由此，我们便可通过检查status文件中TracerPid的值来判断是否有正在被调试。示例代码如下：

```
#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[]) {
   int i;
   scanf("%d", &i);
   char buf1[512];
   FILE* fin;
   fin = fopen("/proc/self/status", "r");
   int tpid;
   const char *needle = "TracerPid:";
   size_t nl = strlen(needle);
   while(fgets(buf1, 512, fin)) {
       if(!strncmp(buf1, needle, nl)) {
           sscanf(buf1, "TracerPid: %d", &tpid);
           if(tpid != 0) {
                printf("Debuggerdetected");
                return 1;
           }
       }
    }
   fclose(fin);
   printf("All good");
   return 0;
}

```

实际运行结果如下图所示：

![p3](http://drops.javaweb.org/uploads/images/bfcaa0919d76ca2514fc9eb7e1426b67501989a0.jpg)

值得注意的是，/proc目录下包含了进程的大量信息。我们在这里是读取status文件，此外，也可通过/proc/self/stat文件来获得进程相关信息，包括运行状态。

**d.读取`/proc/%d/wchan`**

下图中第一个红色框值为非调试状态值，第二个红色框值为调试状态：

![p4](http://drops.javaweb.org/uploads/images/43c032693d8215b1e31dcc0071bcb9bff4edc028.jpg)

```
static int getWchanStatus(int pid)  
{  
      FILEFILE *fp= NULL;  
      char filename;  
      char wchaninfo = {0};  
      int result = WCHAN_ELSE;  
      char cmd = {0};  
      sprintf(cmd,"cat /proc/%d/wchan",pid);  
      LOGANTI("cmd= %s",cmd);  
      FILEFILE *ptr;         
      if((ptr=popen(cmd, "r")) != NULL)  
      {  
                if(fgets(wchaninfo, 128, ptr) != NULL)  
                {  
                        LOGANTI("wchaninfo= %s",wchaninfo);  
                }  
      }  
      if(strncasecmp(wchaninfo,"sys_epoll\0",strlen("sys_epoll\0")) == 0)  
                result = WCHAN_RUNNING;  
      else if(strncasecmp(wchaninfo,"ptrace_stop\0",strlen("ptrace_stop\0")) == 0)  
                result = WCHAN_TRACING;  
      return result;  
}  

```

**e.ptrace 自身或者fork子进程相互ptrace**

```
if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0) {  
printf("DEBUGGING... Bye\n");  
return 1;  
}  
void anti_ptrace(void)  
{  
    pid_t child;  
    child = fork();  
    if (child)  
      wait(NULL);  
    else {  
      pid_t parent = getppid();  
      if (ptrace(PTRACE_ATTACH, parent, 0, 0) < 0)  
            while(1);  
      sleep(1);  
      ptrace(PTRACE_DETACH, parent, 0, 0);  
      exit(0);  
    }  
}

```

**f.设置程序运行最大时间**

这种方法经常在CTF比赛中看到。由于程序在调试时的断点、检查修改内存等操作，运行时间往往要远大于正常运行时间。所以，一旦程序运行时间过长，便可能是由于正在被调试。 

具体地，在程序启动时，通过alarm设置定时，到达时则中止程序。示例代码如下：

```
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
void alarmHandler(int sig) {
   printf("Debugger detected");
   exit(1);
}
void__attribute__((constructor))setupSig(void) {
   signal(SIGALRM, alarmHandler);
   alarm(2);
}
int main(int argc, char *argv[]) {
   printf("All good");
   return 0;
}

```

在此例中，我们通过`__attribute__((constructor))`，在程序启动时便设置好定时。实际运行中，当我们使用gdb在main函数下断点，稍候片刻后继续执行时，则触发了SIGALRM，进而检测到调试器。如下图所示：

![p5](http://drops.javaweb.org/uploads/images/aeafdc645561165135fa655fd4eeebd8776faf91.jpg)

顺便一提，这种方式可以轻易地被绕过。我们可以设置gdb对signal的处理方式，如果我们选择将SIGALRM忽略而非传递给程序，则alarmHandler便不会被执行，如下图所示：

![p6](http://drops.javaweb.org/uploads/images/2ac40bd1ffa6ce413d027ab54d361b2562791188.jpg)

**g.检查进程打开的filedescriptor**

如2.2中所说，如果被调试的进程是通过gdb的方式启动，那么它便是由gdb进程fork得到的。而fork在调用时，父进程所拥有的fd(file descriptor)会被子进程继承。由于gdb在往往会打开多个fd，因此如果进程拥有的fd较多，则可能是继承自gdb的，即进程在被调试。 

具体地，进程拥有的fd会在/proc/self/fd/下列出。于是我们的示例代码如下：

```
#include <stdio.h>
#include <dirent.h>
int main(int argc, char *argv[]) {
   struct dirent *dir;
   DIR *d = opendir("/proc/self/fd");
   while(dir=readdir(d)) {
       if(!strcmp(dir->d_name, "5")) {
           printf("Debugger detected");
           return 1;
       }
    }
   closedir(d);
   printf("All good");
   return 0;
}

```

这里，我们检查/proc/self/fd/中是否包含fd为5。由于fd从0开始编号，所以fd为5则说明已经打开了6个文件。如果程序正常运行则不会打开这么多，所以由此来判断是否被调试。运行结果见下图：

![p7](http://drops.javaweb.org/uploads/images/3d3a4d40aa7e368db5b235e5bac8cd1a6363e7c1.jpg)

**h.防止dump**

利用Inotify机制，对/proc/pid/mem和/proc/pid/pagemap文件进行监视。inotify API提供了监视文件系统的事件机制，可用于监视个体文件，或者监控目录。具体原理可参考：[http://man7.org/linux/man-pages/man7/inotify.7.html](http://man7.org/linux/man-pages/man7/inotify.7.html)

伪代码：

```
void __fastcall anitInotify(int flag)  
{  
      MemorPagemap = flag;  
      charchar *pagemap = "/proc/%d/pagemap";  
      charchar *mem = "/proc/%d/mem";  
      pagemap_addr = (charchar *)malloc(0x100u);  
      mem_addr = (charchar *)malloc(0x100u);  
      ret = sprintf(pagemap_addr, &pagemap, pid_);  
      ret = sprintf(mem_addr, &mem, pid_);  
      if ( !MemorPagemap )  
      {  
                ret = pthread_create(&th, 0, (voidvoid *(*)(voidvoid *)) inotity_func, mem_addr);  
                if ( ret >= 0 )  
                   ret = pthread_detach(th);  
      }  
      if ( MemorPagemap == 1 )  
      {  
                ret = pthread_create(&newthread, 0, (voidvoid *(*)(voidvoid *)) inotity_func, pagemap_addr);  
                if(ret > 0)  
                  ret = pthread_detach(th);  
      }  
}  
void __fastcall __noreturn inotity_func(const charchar *inotity_file)  
{  
      const charchar *name; // r4@1  
      signed int fd; // r8@1  
      bool flag; // zf@3  
      bool ret; // nf@3  
      ssize_t length; // r10@3  
      ssize_t i; // r9@7  
      fd_set readfds; // @2  
      char event; // @1  
      name = inotity_file;  
      memset(buffer, 0, 0x400u);  
      fd = inotify_init();  
      inotify_add_watch(fd, name, 0xFFFu);  
      while ( 1 )  
      {  
                do  
                {  
                        memset(&readfds, 0, 0x80u);  
                }  
                while ( select(fd + 1, &readfds, 0, 0, 0) <= 0 );  
                length = read(fd, event, 0x400u);  
                flag = length == 0;  
                ret = length < 0;  
                if ( length >= 0 )  
                {  
                        if ( !ret && !flag )  
                      {  
                              i = 0;  
                              do  
                              {  
                                        inotity_kill((int)&event);  
                                        i += *(_DWORD *)&event + 16;  
                              }  
                              while ( length > i );  
                        }  
                }  
                else  
                {  
                        while ( *(_DWORD *)_errno() == 4 )  
                        {  
                              length = read(fd, buffer, 0x400u);  
                              flag = length == 0;  
                              ret = length < 0;  
                              if ( length >= 0 )  
                        }  
                }  
      }  
}

```

**i.对read做hook**

因为一般的内存dump都会调用到read函数，所以对read做内存hook，检测read数据是否在自己需要保护的空间来阻止dump

**j.设置单步调试陷阱**

```
int handler()  
{  
    return bsd_signal(5, 0);  
}  
int set_SIGTRAP()  
{  
    int result;  
    bsd_signal(5, (int)handler);  
    result = raise(5);  
    return result;  
}

```

[http://www.freebuf.com/tools/83509.html](http://www.freebuf.com/tools/83509.html)

0x06 应用加固技术
===========

移动应用加固技术从产生到现在，一共经历了三代：

*   第一代是基于类加载器的方式实现保护；
*   第二代是基于方法替换的方式实现保护；
*   第三代是基于虚拟机指令集的方式实现保护。

**第一代加固技术：类加载器**

以梆梆加固为例，类加载器主要做了如下工作：

1.  classes.dex被完整加密，放到APK的资源中
2.  采用动态劫持虚拟机的类载入引擎的技术
3.  虚拟机能够载入并运行加密的classes.dex

使用一代加固技术以后的apk加载流程发生了变化如下：

![p8](http://drops.javaweb.org/uploads/images/eaf0da32bc2fb202f6436bfb4c19e476117d5cb7.jpg)

应用启动以后，会首先启动保护代码，保护代码会启动反调试、完整性检测等机制，之后再加载真实的代码。

一代加固技术的优势在于：可以完整的保护APK，支持反调试、完整性校验等。

一代加固技术的缺点是加固前的classes.dex文件会被完整的导入到内存中，可以用内存dump工具直接导出未加固的classes.dex文件。

**第二代加固技术：类方法替换**

第二代加固技术采用了类方法替换的技术：

1.  将原APK中的所有方法的代码提取出来，单独加密
2.  运行时动态劫持Dalvik虚拟机中解析方法的代码，将解密后的代码交给虚拟机执行引擎

采用本技术的优势为：

1.  每个方法单独解密，内存中无完整的解密代码
2.  如果某个方法没有执行，不会解密
3.  在内存中dump代码的成本代价很高

使用二代加固技术以后，启动流程增加了一个解析函数代码的过程，如下图所示：

![p9](http://drops.javaweb.org/uploads/images/907fa4d6c3b142717f228c491dd4efbe50544427.jpg)

**第三代加固技术：虚拟机指令集**

第三代加固技术是基于虚拟机执行引擎替换方式，所做主要工作如下：

1.  将原APK中的所有的代码采用一种自定义的指令格式进行替换
2.  运行时动态劫持Dalvik虚拟机中执行引擎，使用自定义执行引擎执行自定义的代码
3.  类似于PC上的VMProtect采用的技术

三代技术的优点如下：

1.  具有2.0的所有优点
2.  破解需要破解自定义的指令格式，复杂度非常高