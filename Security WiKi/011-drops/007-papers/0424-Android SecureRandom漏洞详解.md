# Android SecureRandom漏洞详解

0x00 漏洞概述
=========

* * *

Android 4.4之前版本的Java加密架构(JCA)中使用的Apache Harmony 6.0M3及其之前版本的SecureRandom实现存在安全漏洞，具体位于

```
classlib/modules/security/src/main/java/common/org/apache/harmony/security/provider/crypto/SHA1PRNG_SecureRandomImpl.java 

```

类的engineNextBytes函数里，当用户没有提供用于产生随机数的种子时，程序不能正确调整偏移量，导致PRNG生成随机序列的过程可被预测。

漏洞文件见文后链接1。

0x01 漏洞影响
=========

* * *

2013年8月份的比特币应用被攻击也与这个漏洞相关。比特币应用里使用了ECDSA 算法，这个算法需要一个随机数来生成签名，然而生成随机数的算法存在本文提到的安全漏洞。同时这个ECDSA算法本身也有漏洞，在这个事件之前索尼的PlayStation 3 master key事件也是利用的这个算法漏洞。

本文主要介绍SecureRandom漏洞，关于ECDSA算法漏洞可以自行阅读下面的资料。

ECDSA算法的细节:

[http://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm#Security](http://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm#Security)

防范措施：http://tools.ietf.org/html/rfc6979

Google group上关于PlayStation 3 master key事件如何利用ECDSA算法漏洞获取私钥的讨论:

[https://groups.google.com/forum/?fromgroups=#!topic/sci.crypt/3isJl28Slrw](https://groups.google.com/forum/?fromgroups=#!topic/sci.crypt/3isJl28Slrw)

0x02 SecureRandom技术实现
=====================

* * *

在java里，随机数是通过一个初始化种子来生成的。两个伪随机数噪声生成器(PRNG)实例，如果使用相同的种子来初始化，就会得到相同的随机序列。Java Cryptography Architecture里提供了几个加密强度更大的PRNGs，这些PRNGs是通过SecureRandom接口实现的。

java.security.SecureRandom这个类本身并没有实现伪随机数生成器，而是使用了其他类里的实现。因此SecureRandom生成的随机数的随机性、安全性和性能取决于算法和熵源的选择。

控制SecureRandom API的配置文件位于$JAVA_HOME/jre/lib/security/java.security。比如我们可以配置该文件里的securerandom.source属性来指定SecureRandom中使用的seed的来源。比如使用设备相关的源，可以这样设置：

```
securerandom.source=file:/dev/urandom
securerandom.source=file:/dev/random

```

关于SecureRandom具体技术细节可参看文章最后参考链接2。

现在重点看下SecureRandomSpi抽象类。参考链接3。该抽象类为SecureRandom类定义了功能接口,里面有三个抽象方法engineSetSeed,engineGenerateSeed,and engineNextBytes。如果Service Provider希望提供加密强度较高的伪随机数生成器的功能，就必须实现这三个方法。

然而Apache Harmony 6.0M3及其之前版本的SecureRandom实现中engineNextBytes函数存在安全漏洞。

0x03 Apache Harmony’s SecureRandom实现
====================================

* * *

Apache Harmony 是2005年以Apache License发布的一个开源的java核心库。虽然2011年以后已宣布停产，但是这个项目作为Google Android platform的一部分继续被开发维护。

Apache Harmony's SecureRandom实现算法如下：

![enter image description here](http://drops.javaweb.org/uploads/images/d89a90f635d217dbeb425d8c08f1756a48d6e63c.jpg)

Android里的PRNG使用SHA-1哈希算法、操作系统提供的设备相关的种子来产生伪随机序列。随机数是通过三部分(internal state即seed+counter+ padding)反复哈希求和计算产生的。如下图

![enter image description here](http://drops.javaweb.org/uploads/images/ea450f6dfa5b944bfa5f3549c1d700ec741ca072.jpg)

其中计数器counter从0开始，算法每运行一次自增一。counter和padding部分都可以称为buffer。Padding遵守SHA-1的填充格式：最后的8 byte存放要hash的值的长度len，剩下的部分由一个1，后面跟0的格式进行填充。最后返回Hash后的结果，也就是生成的伪随机序列。

0x04 Apache Harmony’s SecureRandom漏洞细节
======================================

* * *

当使用无参构造函数创建一个SecureRandom实例，并且在随后也不使用setSeed()进行初始化时,插入一个起始值后，代码不能正确的调整偏移量(byte offset,这个offset是指向state buffer的指针)。这导致本该附加在种子后面的计数器(8 byte)和padding(起始4 byte)覆盖了种子的起始12 byte。熵的剩下8 byte(20 byte的种子中未被覆盖部分),使得PRNG加密应用无效。

在信息论中，熵被用来衡量一个随机变量出现的期望值。熵值越低越容易被预测。熵值可以用比特来表示。关于熵的知识请参考：http://zh.wikipedia.org/wiki/熵_(信息论)

下面这张图可以形象的表述这个过程：

![enter image description here](http://drops.javaweb.org/uploads/images/4abdfb432ec2ba6a41f8d5c6ec61c237bbaaad59.jpg)

0x05 漏洞修复
=========

* * *

Google已经发布了patch，看下Diff文件:

[https://android.googlesource.com/platform/libcore/+/ab6d7714b47c04cc4bd812b32e6a6370181a06e4%5E%21/#F0](https://android.googlesource.com/platform/libcore/+/ab6d7714b47c04cc4bd812b32e6a6370181a06e4%5E!/#F0)

修复前：

![enter image description here](http://drops.javaweb.org/uploads/images/6535da94c368e49432a1797ae73aa85095a62c01.jpg)

修复后：

![enter image description here](http://drops.javaweb.org/uploads/images/8a7c95e4d696389eb113323269ee9611b368d196.jpg)

对于普通开发者来讲，可以使用下面链接中的方式进行修复。

[http://android-developers.blogspot.com.au/2013/08/some-securerandom-thoughts.html](http://android-developers.blogspot.com.au/2013/08/some-securerandom-thoughts.html)

0x06 参考链接
=========

* * *

```
https://android.googlesource.com/platform/libcore/+/kitkat-release/luni/src/main/java/org/apache/harmony/security/provider/crypto/SHA1PRNG_SecureRandomImpl.java
http://resources.infosecinstitute.com/random-number-generation-java/
http://developer.android.com/reference/java/security/SecureRandomSpi.html
http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2013-7372
http://android-developers.blogspot.com.au/2013/08/some-securerandom-thoughts.html

```