# Android安全开发之ZIP文件目录遍历

**作者：伊樵、呆狐、舟海@阿里聚安全**

0x00 ZIP文件目录遍历简介
================

* * *

因为ZIP压缩包文件中允许存在“`../`”的字符串，攻击者可以利用多个“`../`”在解压时改变ZIP包中某个文件的存放位置，覆盖掉应用原有的文件。如果被覆盖掉的文件是动态链接so、dex或者odex文件，轻则产生本地拒绝服务漏洞，影响应用的可用性，重则可能造成任意代码执行漏洞，危害用户的设备安全和信息安全。比如近段时间发现的“寄生兽”漏洞、海豚浏览器远程命令执行漏洞、三星默认输入法远程代码执行漏洞等都与ZIP文件目录遍历有关。

阿里聚安全的应用漏洞扫描服务，可以检测出应用的ZIP文件目录遍历风险。另外我们发现日本计算机应急响应小组（JPCERT）给出的修复方案存在缺陷。如果使用不当（它提供的示例文档就使用错误），可能起不到防止ZIP文件目录遍历的作用，并且国内有修复方案参考了此方案。

0x01 漏洞原理和风险示例
==============

* * *

1.1 漏洞原理
--------

在Linux/Unix系统中“`../`”代表的是向上级目录跳转，有些程序在当前工作目录中处理到诸如用“`../../../../../../../../../../../etc/hosts`”表示的文件，会跳转出当前工作目录，跳转到到其他目录中。 

Java代码在解压ZIP文件时会使用到ZipEntry类的getName()方法。如果ZIP文件中包含“`../`”的字符串，该方法返回值里面会原样返回。如果在这里没有进行防护，继续解压缩操作，就会将解压文件创建到其他目录中。

如我们构造的ZIP文件中有如下文件：

![](http://drops.javaweb.org/uploads/images/1664558c1519fbc18305593cdb4136b69ea2113e.jpg)

进行解压的代码如下，没有对getName进行过滤：

![](http://drops.javaweb.org/uploads/images/e4b702244ff179d98bf0d14d62c192409484a9a1.jpg)

解压操作时的日志：

![](http://drops.javaweb.org/uploads/images/c2105723513e08f9021e7f01e01e3d3a9098568a.jpg)

此ZIP文件存放在SD卡中，想让解压出来的所有文件也存在SD卡中，但是a_poc.txt文件却存在了应用的数据目录中：

![](http://drops.javaweb.org/uploads/images/814179212a46e4666f51fb999cffa31d98857b8d.jpg)

1.2 风险示例
--------

以海豚浏览器远程代码执行漏洞为例。 

海豚浏览器的主题设置中允许用户通过网络下载新的主题进行更换，主题文件其实是一个ZIP压缩文件。通过中间人攻击的方法可以替换掉这个ZIP文件。替换后的ZIP文件中有重新编译过的libdolphin.so。此so文件重写了JNI_OnLoad()函数：

![](http://drops.javaweb.org/uploads/images/b5007c67e4986913e7b52aa43af698229273b626.jpg)

此so文件以“`../../../../../../../../../../data/data/mobi.mgeek.TunnyBrowser/files/libdolphin.so`”的形式存在恶意ZIP文件中。海豚浏览器解压恶意ZIP文件后，重新的libdolphin.so就会覆盖掉原有的so文件，重新运行海豚浏览器会弹出Toast提示框：

![](http://drops.javaweb.org/uploads/images/6d3f36af454b26a97684c514d46ce5418cf079d1.jpg)

能弹出Toast说明也就可以执行其他代码。

**这里分析下此漏洞产生的原因是： **

1、主题文件其实是一个ZIP压缩包，从服务器下载后进行解压，但是解压时没有过滤getName()返回的字符串中是否有“`../`”：

![](http://drops.javaweb.org/uploads/images/3d37807aebe026fcf2947514bd704b694045d438.jpg)

2、动态链接库文件libdolphin.so，并没有放在应用数据的lib目录下，而是放在了files目录中：

![](http://drops.javaweb.org/uploads/images/45b78a8367e8ae923a7e8b76a1257960286d0a00.jpg)

加载使用的地方是`com.dolphin.browser.search.redirect`包中的SearchRedirector：

![](http://drops.javaweb.org/uploads/images/02179ebfac55f9ef552d831711da73439c8fcfd7.jpg)

应用使用的是System.load()来加载libdolphin.so而非System.loadLibrary()，在Android中，System.loadLibrary()是从应用的lib目录中加载.so文件，而System.load()是用某个.so文件的绝对路径加载，这个.so文件可以不在应用的lib目录中，可以在SD卡中，或者在应用的files目录中，只要应用有读的权限目录中即可。

在files目录中，应用具有写入权限，通过网络中间人攻击，同时利用ZIP文件目录遍历漏洞，替换掉文件libdolphin.so，达到远程命令执行的目的。

应用的lib目录是软链接到了`/data/app-lib/`应用目录，如果libdolphin.so文件在lib目录下就不会被覆盖了，第三方应用在执行时没有写入/data/app-lib目录的权限：

![](http://drops.javaweb.org/uploads/images/49d0a54e144e3fb57c1aeb34b59c164f95b718ac.jpg)

0x02 JPCERT修复方案的研究
==================

* * *

在研究中我们发现JPCERT提供的修复方案存在缺陷。它是利用Java的File类提供的getCanonicalPath()方法过滤掉zipEntry.getName()返回的字符串中所包含的“`../`”，然后检查这个字符串是否是以要解压到的目标目录字符串为开头，如果是，返回getCanonicalPath()获取到的字符串，如果不是，则抛出异常：

![](http://drops.javaweb.org/uploads/images/ef816ba4bf8750969b69e8cad0cbb07e67d6d5ed.jpg)

但是在JPCERT给出的示例代码中，对validateFilename()的调用对于APP来说不会达到防止任意目录遍历的目的：

![](http://drops.javaweb.org/uploads/images/bb5a6f2a024abee3423a43407d73398140c9119f.jpg)

其使用“`.`”，作为要解压到的目的目录，“`.`”表示当前目录，经测试APP进程的当前工作目录是根目录“`/`”：

![](http://drops.javaweb.org/uploads/images/b73bca9bda975ad17d4b1b78f80a2133b37c49ef.jpg)

![](http://drops.javaweb.org/uploads/images/466fecd43aee1a60a147ca77179821c6f186e81f.jpg)

查看进程状态，得到的APP进程的当前工作目录cwd是链接到了根目录：

![](http://drops.javaweb.org/uploads/images/9a77a88a9725de86bce390e55f80db8a845160fb.jpg)

如下的Demo，如果采用JPCERT示例中`validateFilename(entry.genName(), “.”)`的调用方式，还是会产生目录遍历读到系统配置文件：

![](http://drops.javaweb.org/uploads/images/a9aef9bde76726a6a9bb33e65c539aa225298632.jpg)

读到的hosts文件内容：

![](http://drops.javaweb.org/uploads/images/69e744324eef5efa476a427bfa87e788e48de131.jpg)

正确的调用validateFilename()形式是传入的要解压到的目的目录不要用“`.`”，而是指定一个绝对路径。

0x03 阿里聚安全对开发者建议
================

* * *

1.  对重要的ZIP压缩包文件进行数字签名校验，校验通过才进行解压。 
    
2.  检查Zip压缩包中使用ZipEntry.getName()获取的文件名中是否包含”`../`”或者”`..`”，检查”`../`”的时候不必进行URI Decode（以防通过URI编码”`..%2F`”来进行绕过），测试发现ZipEntry.getName()对于Zip包中有“`..%2F`”的文件路径不会进行处理。 
    
3.  在应用上线前使用阿里聚安全的安全扫描服务，尽早发现应用的安全风险。
    

**阿里聚安全扫描器建议修复方案： **

在使用`java.util.zip`包中ZipInputStream类的进行解压操作时，进行检查，示例如下：

![](http://drops.javaweb.org/uploads/images/a0d7a74bc5d458a537023e61f25a2e26a30dd8d6.jpg)

也可以使用`java.util.zip`包中的ZipFile类，直接读取Zip包中的所有entries，然后检查getName()的返回值是否包含“`../`”：

![](http://drops.javaweb.org/uploads/images/2bd8c37219abacba69b0f00591b89d63be217c55.jpg)

0x04 参考
=======

* * *

【1】 https://www.jpcert.or.jp/present/2014/20140910android-sc.pdf 

【2】 《海豚浏览器与水星浏览器远程代码执行漏洞详解》http://drops.wooyun.org/mobile/8293 

【3】 《影响数千万APP的安卓APP“寄生兽”漏洞技术分析》http://drops.wooyun.org/mobile/6910 

【4】 《三星默认输入法远程代码执行》http://drops.wooyun.org/papers/6632 

【5】 http://www.oracle.com/technetwork/articles/java/compress-1565076.html 

【6】 http://stackoverflow.com/questions/1099300/whats-the-difference-between-getpath-getabsolutepath-and-getcanonicalpath 

【7】 http://stackoverflow.com/questions/7016391/difference-between-system-load-and-system-loadlibrary-in-java