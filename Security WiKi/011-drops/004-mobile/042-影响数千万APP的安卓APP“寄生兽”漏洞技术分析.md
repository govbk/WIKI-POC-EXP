# 影响数千万APP的安卓APP“寄生兽”漏洞技术分析

0x00 前言
=======

* * *

360手机安全研究团队vulpecker近日发现了一种新型的安卓app安全漏洞，市面上数以千万的app都受该漏洞影响。该漏洞一旦被攻击者利用，可以直接在用户手机中植入木马，盗取用户的短信、照片以及银行、支付宝等账号密码，vulpecker以“寄生兽”命名这个漏洞。

目前vulpecker团队已经通过补天平台将相关详情通知给各大安全应急响应中心，也向受此影响的各大厂商进行了通报，在此提醒用户关注各APP厂商修复进程，并及时下载更新安装最新的APP。

寄生兽是日本作家岩明均创作的漫画《寄生兽》中的一种怪物，初始形态是一种虫子，会钻进生物的体内并夺取大脑，因人类严重的环境污染而诞生，该漏洞的攻击方式类似寄生兽的感染，可以长期驻留在受害者的手机内，本文将详细分析这个漏洞，揭开漏洞的秘密。

0x01 关于app的缓存代码
===============

* * *

安卓的应用程序apk文件是zip压缩格式的文件，apk文件中包含的classes.dex文件相当于app的可执行文件，当app运行后系统会对classes.dex进行优化，生成对应的odex格式的文件。

odex文件相当于app的可执行文件的缓存代码，一般安卓系统在第一次加载运行apk时会将系统生成odex文件存放于/data/dalvik-cache目录下。

如图

![enter image description here](http://drops.javaweb.org/uploads/images/6e38a9b17236597d8138399bc953deffc86b4a2b.jpg)

可以看到该目录下的文件只有system用户有写权限，只有在拥有system权限的情况下才能对odex文件进行写操作。

0x02 广泛流行的插件机制
==============

* * *

由于安卓应用的升级都需要重新安装程序，频繁的升级给用户体验和开发都带来了不便，所以市面上的app都开始采用插件机制，利用插件机制可以做到无缝升级和扩展功能，app只需要引入相应的插件文件就可以做到功能添加或升级，无需再重新安装程序。

app插件机制的实现方式是把相关功能编写成单独的apk或jar文件，然后在程序运行时用DexClassLoader动态加载，进行反射调用。我们来看一下DexClassLoder的定义

```
public DexClassLoader (String dexPath, String optimizedDirectory, String library
Path, ClassLoader parent)
dexPath：是要加载的jar/apk的路径
optimizedDirectory：目标odex的路径
libraryPath：依赖的native library(so文件)路径
parent：父加载器

```

下面是常见的调用DexClassLoader的代码片段

1.  String dexFiles = "/data/data/com.test.dexload/app_al_sdk/drozer.apk";
2.  final File optimizedDexOutputPath = appcontext.getDir("outdex", 0);
3.  appcontext.getClassLoader();
4.  DexClassLoader classLoader = new DexClassLoader(dexFiles, optimizedDexOutputPath .getAbsolutePath(), null, ClassLoader.getSystemClassLoader());
5.  ...

如图drozer.apk插件在被调用后生成了drozer.dex缓存文件，注意这个文件是odex格式.

![enter image description here](http://drops.javaweb.org/uploads/images/bd12d571bbbc37cd9b2aa47fde99d0b6cd379662.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0674f017a1c37ea0bb59a084d87956efaf33925d.jpg)

0x03 插件机制引入的攻击点
===============

* * *

在2013年，国外的mwr实验室给出了一个利用中间人的方式劫持app升级插件的攻击案例，参考

https://labs.mwrinfosecurity.com/blog/2013/11/20/applovin-ad-library-sdk-remote-command-execution-via-update-mechanism/

几年前，大部分采用插件机制的app，在载入插件前都没有对插件文件进行完整性校验，导致黑客可以通过中间人劫持的方式替换app的升级插件，在插件中嵌入恶意代码控制用户的app和手机。

现今，大部分采用插件机制的app都加强了安全性，如最早使用插件开发方式的微信等app，在下载使用插件前都会校验插件文件的签名，黑客已经无法通过中间人的方式替换插件攻击app。

0x04 插件机制新的攻击点
==============

* * *

近日，国外的nowsecure公司公布了三星输入法的一个漏洞，利用过程直接替换了系统app的odex缓存代码。参考：

https://www.nowsecure.com/blog/2015/06/16/remote-code-execution-as-system-user-on-samsung-phones/

三星输入法是拥有系统最高级别的system权限，可以直接替换任意app的缓存文件。那安卓app插件的缓存代码是否和APP主程序直接产生的缓存代码一样能被任意替换？

我们去android源码中验证了一下，通过DexClassLoader() 加载jar/apk文件，最终会通过native接口openDexFileNative() 进入到native层。

对应于android-4.2.2_r1/dalvik/vm/native/dalvik_system_DexFile.cpp中的Dalvik_dalvik_system_DexFile_openDexFileNative() 方法，在native层对几个参数做一系列校验，如果检测到第二个参数指定的odex文件存在，则会调用dvmOpenCachedDexFile() 直 接打开，调用处的代码如下：

1.  fd = dvmOpenCachedDexFile(fileName, cachedName,
2.  dexGetZipEntryModTime(&archive, entry),
3.  dexGetZipEntryCrc32(&archive, entry),
4.  isBootstrap, &newFile, /_createIfMissing=_/true);

很明显，第3、4个参数对应的是优化前的classes.dex的时间戳和crc校验值。最终会调用

1.  dvmCheckOptHeaderAndDependencies(fd, true, modWhen, crc,
2.  expectVerify, expectOpt)

如果crc、modWhen参数正确，则返回该odex的文件句柄；若crc、modEWhen校验错误，则尝试删除错误的odex，并重建新的odex。所以，攻击者如果要注入目标odex，需要对修改后的odex文件的crc及modWhen做修改。

下面是一个修改后的odex文件实例，dex_old是修改前的odex文件，dex_new是修改后的dex文件，两个文件的md5不一样，但是crc及modWhen却是一样的，这样就可以绕过DexClassLoader的校验。

![enter image description here](http://drops.javaweb.org/uploads/images/5aa742fdaf23e1fd68ad389478d6d6c241dd8f0a.jpg)

0x05 “寄生兽”漏洞的真正危害
=================

* * *

安卓应用的代码缓存机制是程序在执行时优先加载运行缓存代码，而google却只对缓存代码做了可以伪造的弱校验，这明显这是一个安全架构实现上的严重漏洞。

广大app开发者再使用插件机制开发app时可以对插件文件做完整性校验，而系统生成的缓存代码却无法做到有效保护，一旦攻击者将恶意代码注入到缓存代码中，开发者对app插件文件做的各种保护都将失效。这种攻击很难被发现，即使重启或关机，只要app一运行，恶意代码也会随之运行，同时安全软件对这一块的检查和防御也几乎为零。

0x06 现实中的“寄生兽”漏洞攻击案例
====================

* * *

**_1）利用zip解压缩漏洞覆盖缓存代码_**

在三星输入法漏洞的利用中，作者用到了安卓下的zip解压缩漏洞，这个漏洞是单独的一个漏洞，且由来以久，在google官方的文档中已经做了警告，存在问题的是ZipEntry.getName()方法，我们看一下google文档中对该函数的描述：

链接：http://developer.android.com/reference/java/util/zip/ZipEntry.html#getName() Gets the name of this ZipEntry

```
Security note: Entry names can represent relative paths. foo/../bar or ../bar/baz ,
for example. If the entry name is being used to construct a filename or as a path
component, it must be validated or sanitized to ensure that files are not written outside
of the intended destination directory.

```

可以看到google对该方法给出了一个安全提示，提示开发者如果该方法的返回值中包含有"../"跳转符，需要特别注意不要将文件写到了目标文件夹之外。如果不对"../"跳转符做过滤，就有可能遍历目录，在解压zip文件时以本app的权限覆盖任意文件。

我们检测后发现市面上几乎所有使用zip解压缩功能的app都存在漏洞，为“寄生兽”漏洞的攻击提供了便利，主要分为三类情况：

APP关联文件类

这类漏洞主要影响有皮肤功能的APP，如输入法，浏览器类APP .很多app在manifest中做了zip类文件的关联，如果注册的文件格式被点击，对应的app就会启动解压文件。下图是app注册文件关联的一个示例

![enter image description here](http://drops.javaweb.org/uploads/images/0a5c60e39d584e263445a6cf8f90e18ae8ee61dd.jpg)

这个app关联了一个ssf格式的文件，其实这个文件的格式是zip压缩格式，用户在手机中下载打开ssf文件时，就会启动对应的app自动解压文件，文件中包含的恶意代码可以覆盖该app的缓存代码。

验证某输入法app漏洞视频

http://v.youku.com/v_show/id_XMTI3NDA2MjkyNA==.html

APP自升级类

这类漏洞主要影响有自动升级下载zip类文件功能的app，在app下载文件过程中可以被中间人劫持攻击，我们发现地图类的app和sdk插件最容易收到攻击，app在下载解压资源文件的过程中被攻击

验证某地图app漏洞视频

http://v.youku.com/v_show/id_XMTI3MzgyMDU0MA==.html

APP默认解压类

这类漏洞主要影响默认有解压缩zip文件功能的app，如浏览器直接下载zip文件打开后，app就被感染缓存代码。

验证某浏览器漏洞视频: http://v.youku.com/v_show/id_XMTI3NDIxMzUzMg==.html

**_2）利用adb backup覆盖缓存代码_**

如果开发者没有在manifest里指定allowBackup="false" ，就可以在不需要root权限的情况下备份、恢复app私有目录下的数据。如果该app用到了插件机制，则对应的插件的odex文件也会被备份。攻击者可以先用adb backup备份用户数据，对备份下来的odex文件进行修改，然后用adb restore恢复回去，就可以替换掉正常的odex文件，造成代码劫持。

**_3）其他可能的APP数据读写_**

如果一个木马病毒利用root权限实施“寄生兽”漏洞攻击方式，将能实现隐蔽的apt木马攻击方式，长期潜伏在用户的手机类，安全软件很难发现app的缓存代码被感染了。

0x07 “寄生兽”漏洞的防护方案
=================

* * *

“寄生兽”漏洞的核心有两点，一是google没有考虑odex的安全问题需要开发者自己做防护，另一个是要阻断漏洞的攻击入口和利用方式，这里我们给出一些防护建议缓解该漏洞的攻击。

**_对odex文件进行完整性校验_**

由于对odex一般是由系统(DexClassLoader)自动生成的，且odex与apk/jar是相对独立的，开发者事先无法知道odex文件的MD5等信息，所以很难通过MD5校验等手段保护odex的完整性；同时，系统的DexClassLoader函数只是校验了odex中的crc、modWhen字段，可以很轻易的被绕过。

所以，目前对odex的防护只能由app自身来做，可以在每次运行DexClassLoader之前，清除已经存在的odex；

另外，在odex第一次生成之后，存储odex文件的MD5值，以后每次调用DexClassLoader的时候都对odex文件进行MD5校验。

**_对可能的劫持odex的攻击入口漏洞进行修复_**

对zip解压缩的漏洞，只需要在调用zipEntry.getName()的时候，过滤返回值中的"../"跳转符。对于引用的第三方的zip库也需要注意，可以用上面的测试用例测试一下第三方库是否有zip解压缩的漏洞；

调用DexClassLoader动态加载dex的时候，第二个参数不要指定在sdcard上；

在manifest里指定allowBackup=”false”，防止应用数据备份覆盖;