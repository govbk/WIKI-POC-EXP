# Android uncovers master-key 漏洞分析

### 0x00 背景

* * *

Bluebox的CTO Jeff Forristal在其官⽅方blog爆出一个漏洞叫做UNCOVERING ANDROID MASTER KEY,大致是不篡改签名修改android代码。

Link:[http://bluebox.com/corporate-blog/bluebox-uncovers-android-master-key/](http://bluebox.com/corporate-blog/bluebox-uncovers-android-master-key/)

##### blog:关于细节并没有讲太多,只有discrepancies in how Android applications are cryptographically verified & installed(安卓应⽤用签名验证和安装的不⼀一致)essentially allowing a malicious author to trick Android into believing the app is unchanged even if it has been(让andriod系统本⾝身认为应⽤用没有修改)这两条重要的信息。

剩下就是放出来一张更改基带字串的图:

![enter image description here](http://drops.javaweb.org/uploads/images/c3ef9c655d03885f08be05c36fc84117a4ec6e31.jpg)

具体细节7月底的blackhat放出。

没多少天7月8号国外已经有人放出poc来。微博上看到rayh4c说已经搞定。就分析了一下。

### 0x01 分析

* * *

POC还没出来之前,先是看了下android的签名机制和安装机制。

签名机制: 用简单的话来讲就是android把app应用的所有文件都做了sha1(不可逆)签名,并对这签名用RSA(非对称加密算法)的私钥进行了加密,客户端安装验证时用公钥进行解密。

从逻辑上看,这签名机制对完整性和唯一性的校验是完全没问题的。主流的很多加密都类似这样。

安装机制:

安装机制则较为复杂。

```
1.系统应用安装――开机时完成,没有安装界面
2.网络下载应用安装――通过market应用完成,没有安装界面
3.ADB⼯工具安装――没有安装界面。
4.第三⽅方应用安装――通过SD卡⾥里的APK⽂文件安装,有安装界面,由packageinstaller.apk应⽤用处理安装及卸载过程的界面。

```

安装过程:复制APK安装包到data/app目录下,解压并扫描安装包,把dex⽂文件(Dalvik字节码) 保存到dalvik-cache目录,并data/data目录下创建对应的应⽤用数据目录。

到这里看出在安装机制上的问题可能性比较大。

回头看⽼老外的POC:[https://gist.github.com/poliva/36b0795ab79ad6f14fd8](https://gist.github.com/poliva/36b0795ab79ad6f14fd8)

![enter image description here](http://drops.javaweb.org/uploads/images/5edadf0ffb436a4094efb6cea7cac97d9505cb44.jpg)

在linux执⾏行了一遍,出现错误。可能是apk的原因。

索性把这poc移植到windows下,先是⽤用apktool 把要更改的apk给反编译出来到一个目录apk_test

然后⼜又把apk_test打包成⼀一个新的apk

把原先的apk解压出来apk_old

把apk_old所有⽂文件以zip压缩的⽅方式加⼊入新的apk中。我本机以weibo.apk为例:

![enter image description here](http://drops.javaweb.org/uploads/images/8401d1d319c2e4038d4b2305c2ed4c61ee2d293d.jpg)

可见两者大小发生了变化,apktool在反编译过程不可避免的出现差异。并且重编译的apk不含有签名文件。

按照poc的做法我用批处理导出目录的文件名到1.txt修改了poc.py

```
import zipfile
import sys
f=open('1.txt','r')
line=f.readline()
test=[]
while line:
    test1=line.replace("\n","")
    test.append(test1)
    if not line:
        break
    line=f.readline()
f.close()
z = zipfile.ZipFile("livers.apk", "a")
for i in range(0,len(test)):
    print test[i]
    z.write(str(test[i]))
z.close()

```

![enter image description here](http://drops.javaweb.org/uploads/images/c3100ccd261d10cf69f9c80aa0ae5a413a89287f.jpg)

差不多增大了一倍,放在手机上安装了一下,成功安装。查看了下:

![enter image description here](http://drops.javaweb.org/uploads/images/554e9dbd6df59bf842624aa7a2c5e84d3570cad1.jpg)

出现了多对同名文件。CRC校验不同,查看了一下,基本上是两个字节便产生不同。

![enter image description here](http://drops.javaweb.org/uploads/images/8901c214e236b02285fc4228676a02477133908b.jpg)

这里我又测试了只添加签名文件,或者dex文件等,均不能通过验证。

可证明其在scan list扫描目录或者复制文件时候对同名文件处理不当。

### 0x02 验证

* * *

证明是否可以进行更改源码,并能使用原生签名。我把apk图标进行了更改。

顺便讲下一般的反编译修改:

```
1. apktool或者其他工具进行反编译包含smalijava字节码汇编和xml图片文件。 
2. apkzip解压。
3. 反编译dex成java文件。
4. 查找对应修改的smali文件或者xml(一般广告链接)
5. Apktool打包成apk文件
6. 用autosign进行签名。
这里没有进行签名直接借用原来的签名。

```

![enter image description here](http://drops.javaweb.org/uploads/images/9ef266000a05515374adf9c87ea280beda4455c9.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/4cf993b280f173bbae5ab721504ab431dec02da4.jpg)

### 0x03 查找根源

* * *

我这里下载的android 2.2的源码，查找到获取签名信息安装位于`frameworks\base\core\java\android\content\pm\PackageParser.java`这个文件，`public boolean collectCertificates(Package pkg, int flags)`和`private Certificate[] loadCertificates(JarFile jarFile, JarEntry je, byte[] readBuffer)`这个方法是用来获取签名信息的。

```
 Enumeration entries = jarFile.entries();
            while (entries.hasMoreElements()) {
                JarEntry je = (JarEntry)entries.nextElement();
                if (je.isDirectory()) continue;
                if (je.getName().startsWith("META-INF/")) continue;
                Certificate[] localCerts = loadCertificates(jarFile, je,
                        readBuffer);
            。。。。。。
                } else {
                    // Ensure all certificates match.
                    for (int i=0; i<certs.length; i++) {
                        boolean found = false;
                        for (int j=0; j<localCerts.length; j++) {
                            if (certs[i] != null &&
                                    certs[i].equals(localCerts[j])) {
                                found = true;
                                break;
                            }
                        }
                      。。。。。

```

前面通过黑盒方式，大致推断出安装机制就是把重命名文件同时处理了，没有覆盖而是：

```
if (certs[i] != null &&certs[i].equals(localCerts[j])) {
    found = true;
    break;
} 

```

两个重名文件都做了验证，只要有一个通过验证，就返回验证通过。

### 0x04 后继

* * *

我android研究不多，大多以前玩逆向的底子。大家可以多讨论。 欢迎大家留言探讨~！

======================================================================================================

#### 7月11日21点更新：

没看到看雪上已经讨论的热火朝天，读下来来源于看雪的zmworm的原理分析应该是更准确的。

#### 原理简述

由于ZIP格式允许存在两个或以上完全相同的路径，而安卓系统没有考虑这种场景。

在该情况下，android包管理器校验签名取的是最后一个文件的hash，而运行APK加载的dex文件却是zip的第一个dex文件。 
包管理器验证签名验的是最后一个（名字相同情况下）文件。

1. 解析zip的所有Entry，结果存到HashMap（key为路径，value为Entry）。

![enter image description here](http://drops.javaweb.org/uploads/images/4027bba44b14ed466143830b3df50fbc4be24386.jpg)

2. 由于HashMap.put在相同key的情况下，会把value更新，导致上述的HashMap在相同路径下，存储的一定是最后一个文件的Entry。

![enter image description here](http://drops.javaweb.org/uploads/images/ae7d38a835b3b7308fbac684fcf420cb5f695016.jpg)

 系统加载dex文件，加载的是第一个dex。   1. 查找dex的Entry用的是dexZipFindEntry。 

![enter image description here](http://drops.javaweb.org/uploads/images/45ca9dd6b3560225e957610aca3ed488ee1fa283.jpg)

2. dexZipFindEntry的实现是只要match就返回，所以返回的都是第一个文件。

![enter image description here](http://drops.javaweb.org/uploads/images/b3bdb8e7f01f2b5aafe167cff88fbfb3ff051f94.jpg)

Zip 可以包含两个同名文件或者路径，而其自身的unzip 默认方式是后一个覆盖前一个。

HashMap.put 的写法应该文件也直接覆盖(hash表的冲突处理不当果真出大问题)才算是算是符合zip 的标准。

就是加载dex的方式则是先加载第一个，这样确实信息不一致。

而我之前黑盒测出来认为android 默认把两个都加载在签名验证顺序上出现问题的，未分析到上一层的类。

看雪上也是讨论很多帖子得到准确的原理分析，大家共同讨论，集思广益。Hack it, know it too.

持续跟新中。