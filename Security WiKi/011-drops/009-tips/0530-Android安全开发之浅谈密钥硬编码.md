# Android安全开发之浅谈密钥硬编码

**作者：伊樵、呆狐@阿里聚安全**

0x00 简介
=======

* * *

在阿里聚安全的漏洞扫描器中和人工APP安全审计中，经常发现有开发者将密钥硬编码在Java代码、文件中，这样做会引起很大风险。**信息安全的基础在于密码学，而常用的密码学算法都是公开的，加密内容的保密依靠的是密钥的保密，密钥如果泄露，对于对称密码算法，根据用到的密钥算法和加密后的密文，很容易得到加密前的明文**；对于非对称密码算法或者签名算法，根据密钥和要加密的明文，很容易获得计算出签名值，从而伪造签名。

0x01 风险案例
=========

* * *

密钥硬编码在代码中，而根据密钥的用途不同，这导致了不同的安全风险，有的导致加密数据被破解，数据不再保密，有的导致和服务器通信的加签被破解，引发各种血案，**以下借用乌云上已公布的几个APP漏洞来讲讲**。

1.1 某互联网金融APP加密算法被破解导致敏感信息泄露
----------------------------

某P2P应用客户端，用来加密数据的DES算法的密钥硬编码在Java代码中，而DES算法是对称密码算法，既加密密钥和解密密钥相同。 

反编译APP，发现DES算法：

![](http://drops.javaweb.org/uploads/images/db355a25e90f837e6947e432edcd169726ca017d.jpg)

发现DES算法的密钥，硬编码为“yrdAppKe”，用来加密手势密码：

![](http://drops.javaweb.org/uploads/images/6fadb4a59ab01df2517354fdb43e5fe0b3d06f98.jpg)

将手势密码用DES加密后存放在本地LocusPassWordView.xml文件中：

![](http://drops.javaweb.org/uploads/images/fce851cab42d57d172caba8e94e4f04af7d9837d.jpg)

知道了密文和加密算法以及密钥，通过解密操作，可以从文件中恢复出原始的手势密码。或者使用新的生成新的手势密码

而与服务器通信时接口中的Jason字段也用了DES算法和密钥硬编码为“yRdappKY”：

![](http://drops.javaweb.org/uploads/images/867b553e635c0b8d7ecb333bc8720464c1cb7575.jpg)

![](http://drops.javaweb.org/uploads/images/e479a0c1f649c7a91dd8c591f24cf8574a247eb4.jpg)

和服务器通信采用http传输，没有使用https来加密通信，如果采用中间人攻击或者路由器镜像，获得流量数据，可以破解出用户的通信内容。

1.2 某租车APP加密算法被破解导致一些列风险
------------------------

某租车APP与服务器通信的接口采用http传输数据，并且有对传输的部分参数进行了加密，加密算法采用AES，但是密钥硬编码在java代码中为“shenzhoucar123123”，可被逆向分析出来，导致伪造请求，结合服务器端的漏洞，引起越权访问的风险，如越权查看其它用户的订单等。 

和服务器通信时的数据为：

![](http://drops.javaweb.org/uploads/images/2e2fcc70c6ae1159aee429be80c9bf35ee6f850d.jpg)

q字段是加密后的内容。逆向APP，从登录Activity入手：

![](http://drops.javaweb.org/uploads/images/23c4e9c5bf0a107cd3d52b110a0d6ec882cff53d.jpg)

分析登录流程：v1是用户名，v2是密码，v3是PushId，在用户名和密码不为空并且长度不小于11情况下，执行LoginOperate相关操作，追踪LoginOperate的实现，发现继承自BaseOperate，继续追踪BaseOperate的实现：

![](http://drops.javaweb.org/uploads/images/aa40db73870a5d975753edee45eb8aa6080052f6.jpg)

在BaseOperate的initUrl()方法中，找到了APP是怎么生成请求数据的：

![](http://drops.javaweb.org/uploads/images/84a8afe676d598d61459d492614495060b7b1692.jpg)

继续追踪上图中的initJsonUrl()方法，发现其调用了AES加密：

![](http://drops.javaweb.org/uploads/images/985acad7baaeb1d315334d2e615533c4f0cd4f48.jpg)

继续追踪aes.onEncrypt()函数：

![](http://drops.javaweb.org/uploads/images/eb7e57f33d175e0d62c7a44be00c1abda558de69.jpg)

在onEncrypt()函数中调用了encrypt()函数用来加密数据，追踪encrypt()函数的实现，发现其使用AES算法，并且密钥硬编码在java代码中为“shenzhoucar123123”

![](http://drops.javaweb.org/uploads/images/902014c34e74f9d2d83657fbb58262fde35380a1.jpg)

到现在请求中的数据加密如何实现的就清晰了，另外由于服务器权限控制不严，就可以构造订单id的请求，达到越权访问到其他用户的订单。 

构造{“id”:”11468061”}的请求:

![](http://drops.javaweb.org/uploads/images/81aa626e4227a2a680bc10ccf1bb09464f7a81d1.jpg)

其中uid设置为你自己的uid即可，可以成功看到其他人的订单:

![](http://drops.javaweb.org/uploads/images/8273152a99b51ef77b772e2e1833c14a9a1c8924.jpg)

攻击者完全可以做到使用其他脚本重新实现相同的加密功能并拼接出各个接口请求，批量的刷取订单信息和用户其他信息。

1.3 某酒店APP加签算法被破解导致一系列风险
------------------------

某酒店APP和服务器通信时接口采用http通信，数据进行了加密，并且对传输参数进行签名，在服务器端校验签名，以检查传输的数据是否被篡改，但是加签算法和密钥被逆向分析，可导致加签机制失效，攻击者可任意伪造请求包，若结合服务器端的权限控制有漏洞，则可引发越权风险等。

APP和服务器通信的原始包如下图，可以看到有加签字段sign：

![](http://drops.javaweb.org/uploads/images/577e091138e01d873aeb1863a4f10c0b811d72ab.jpg)

逆向APP定位到加密算法的逻辑代码，com.htinns.biz.HttpUtils.class，其实现逻辑为：

![](http://drops.javaweb.org/uploads/images/34eae6e526abe025c8683b98cf10e596eb204c92.jpg)

原始数据是unSignData，使用RC4算法加密，密钥为KEY变量所代表的值，加密后的数据为signData，传输的数据时的data字段为signData。 

加签字段signd的生成方法是用unsignData拼接时间戳time和resultkey，然后做md5，再进行base64编码。时间戳保证了每次请求包都不一样。 

sendSign()算法是用c或c++写的，放入了so库，其他重要算法都是用java写的。 

可以使用IDA逆向分析so库，找到sendSign()方法

![](http://drops.javaweb.org/uploads/images/2fe88778c33679a13b84e4517784f6db65519035.jpg)

而乌云漏洞提交者采用的是分析sign和getSign(sign)的数据，做一个算法破解字典。其实还有种方法直接调用此so库，来生成字典。

签名破解以后，就可以构造发送给服务器的数据包进行其他方面的安全测试，比如越权、重置密码等。

0x02 阿里聚安全开发建议
==============

* * *

通过以上案例，并总结下自己平时发现密钥硬编码的主要形式有： 

1、密钥直接明文存在sharedprefs文件中，这是最不安全的。 

2、密钥直接硬编码在Java代码中，这很不安全，dex文件很容易被逆向成java代码。 

3、将密钥分成不同的几段，有的存储在文件中、有的存储在代码中，最后将他们拼接起来，可以将整个操作写的很复杂，这因为还是在java层，逆向者只要花点时间，也很容易被逆向。 

4、用ndk开发，将密钥放在so文件，加密解密操作都在so文件里，这从一定程度上提高了的安全性，挡住了一些逆向者，但是有经验的逆向者还是会使用IDA破解的。 

5、在so文件中不存储密钥，so文件中对密钥进行加解密操作，将密钥加密后的密钥命名为其他普通文件，存放在assets目录下或者其他目录下，接着在so文件里面添加无关代码（花指令），虽然可以增加静态分析难度，但是可以使用动态调式的方法，追踪加密解密函数，也可以查找到密钥内容。

保证密钥的安全确是件难事，涉及到密钥分发，存储，失效回收，APP防反编译和防调试，还有风险评估。可以说在设备上安全存储密钥这个基本无解，只能选择增大攻击者的逆向成本，让攻击者知难而退。而要是普通开发者的话，做妥善保护密钥这些事情这需要耗费很大的心血。

产品设计者或者开发者要明白自己的密钥是做什么用的，重要程度怎么样，密钥被逆向出来会造成什么风险，通过评估APP应用的重要程度来选择相应的技术方案。

参考
--

1.  [p2p宜人贷app几种安全问题](http://www.wooyun.org/bugs/wooyun-2010-0187287) 
2.  [神州租车APP客户端设计缺陷导致的一系列安全问题（算法破解/权限遍历等）](http://www.wooyun.org/bugs/wooyun-2010-0105766)
3.  [讲解一步步逆向破解华住酒店集团官网APP的http包加密算法以及一系列漏洞打包](http://www.wooyun.org/bugs/wooyun-2015-0162907)
4.  [http://jaq.alibaba.com/safety?spm=a313e.7837752.1000001.1.zwCPfa](http://jaq.alibaba.com/safety?spm=a313e.7837752.1000001.1.zwCPfa)
5.  [https://www.zhihu.com/question/35136485/answer/84491440](https://www.zhihu.com/question/35136485/answer/84491440)