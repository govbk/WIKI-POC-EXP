# 如何控制开放HTTPS服务的weblogic服务器

0x00 前言
=======

* * *

目前在公开途径还没有看到利用JAVA反序列化漏洞控制开放HTTPS服务的weblogic服务器的方法，已公布的利用工具都只能控制开放HTTP服务的weblogic服务器。我们来分析一下如何利用JAVA反序列化漏洞控制开放HTTPS服务的weblogic服务器，以及相应的防护方法。

建议先参考[修复weblogic的JAVA反序列化漏洞的多种方法](http://drops.wooyun.org/web/13470 "修复weblogic的JAVA反序列化漏洞的多种方法")中关于weblogic的JAVA反序列化漏洞的分析。

0x01 HTTPS服务的架构分析
=================

* * *

如果某服务器需要对公网用户提供HTTPS服务，可以在不同的层次实现。

### 使用SSL网关提供HTTPS服务

当使用SSL网关提供HTTPS服务时，网络架构如下图所示（无关的设备已省略，下同）。

![](http://drops.javaweb.org/uploads/images/442433cc4b819ade3dd02d53dae4877295d5455a.jpg)

SSL网关只会向后转发HTTP协议的数据，不会将T3协议数据转发至weblogic服务器，因此在该场景中，无法通过公网利用weblogic的JAVA反序列化漏洞。

### 使用负载均衡提供HTTPS服务

当使用负载均衡提供HTTPS服务时，网络架构如下图所示。

![](http://drops.javaweb.org/uploads/images/51648f9cad506a44d130aa36f0429e5c9a82eaa3.jpg)

安全起见，负载均衡应选择转发HTTP协议而不是TCP协议，因此在该场景中，也无法通过公网利用weblogic的JAVA反序列化漏洞。

### 使用web代理提供HTTPS服务

当使用web代理（如apache、nginx等）提供HTTPS服务时，网络架构如下图所示。

![](http://drops.javaweb.org/uploads/images/51cdd5eed0d6b9be8bc72ea6bb9460ec2b5cff45.jpg)

web代理只会向后转发HTTP协议的数据，因此在该场景中，也无法通过公网利用weblogic的JAVA反序列化漏洞。

### 使用weblogic提供HTTPS服务

当使用weblogic提供HTTPS服务时，网络架构如下图所示。

![](http://drops.javaweb.org/uploads/images/04630e6cc63d5c018c2d1b085467b44530b799ef.jpg)

weblogic能够接收到利用SSL加密后的T3协议数据，因此在该场景中，通过公网能够利用weblogic的JAVA反序列化漏洞。

**根据上述分析，仅当HTTPS服务由weblogic提供时，才能够利用其JAVA反序列化漏洞。**

0x02 weblogic开放SSL服务时的T3协议格式分析
==============================

* * *

利用weblogic的JAVA反序列化漏洞时，必须向weblogic发送T3协议头。为了能够利用提供SSL服务的weblogic的JAVA反序列化漏洞，需要首先分析当weblogic提供SSL服务时的T3协议格式。

SSL数据包为加密的形式，无法直接进行分析，需要进行解密。当已知SSL私钥时，可以利用Wireshark对SSL通信数据进行解密。

weblogic可以使用演示SSL证书提供SSL服务，也可以使用指定SSL证书提供SSL服务。

可以使用两种方法进行分析，一是使用weblogic提供的演示SSL证书进行分析，二是使用自己生成的SSL证书进行分析。

### 使用weblogic演示证书进行分析(方法一)

**使用weblogic演示证书开放SSL服务**

登录weblogic控制台，将AdminServer的“启用SSL监听端口”钩选，并填入SSL监听端口号。

![](http://drops.javaweb.org/uploads/images/891b9ad9998c0c310d04e0b748bce11d47485b02.jpg)

查看AdminServer的密钥库配置，确认为“演示标识和演示信任”（Demo Identity and Demo Trust），可以看到演示密钥库的文件名为“DemoIdentity.jks”，演示信任密钥库文件名为“DemoTrust.jks”。

![](http://drops.javaweb.org/uploads/images/9b0b459fbdd76b7e01cfd1eeb4a0fcb9e45d2ec9.jpg)

查看AdminServer的SSL配置，可以看到演示密钥库的私钥别名为“DemoIdentity”。

![](http://drops.javaweb.org/uploads/images/32dd70f6ba047dfd07b1b80beda59b34cd467a36.jpg)

使用HTTPS方式登录weblogic控制台，确认可以正常登录。

**生成weblogic演示证书的私钥文件**

以下为weblogic演示密钥库的密码信息。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Property</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Value</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Trust store location</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DemoTrust.jks文件，可在控制台查看</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Trust store password</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DemoTrustKeyStorePassPhrase</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Key store location</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DemoIdentity.jks文件，可在控制台查看</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Key store password</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DemoIdentityKeyStorePassPhrase</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Private key password</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DemoIdentityPassPhrase</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Private Key Alias</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">DemoIdentity，可在控制台查看</td></tr></tbody></table>

使用以下命令生成weblogic演示密钥库的私钥文件。

```
set keystore=DemoIdentity.jks
set tmp_p12=tmp.p12

set storepass=DemoIdentityKeyStorePassPhrase
set keypass=DemoIdentityPassPhrase
set alias=DemoIdentity
set pwd_new=123456

keytool -importkeystore -srckeystore %keystore% -destkeystore %tmp_p12% -srcstoretype JKS -deststoretype PKCS12 -srcstorepass %storepass% -deststorepass %pwd_new% -srcalias %alias% -destalias %alias% -srckeypass %keypass% -destkeypass %pwd_new%

set out_pem=tmp.rsa.pem
set final_pem=final.key

openssl pkcs12 -in %tmp_p12% -nodes -out %out_pem% -passin pass:%pwd_new%
openssl rsa -in %out_pem% -check > %final_pem% 

```

最终生成的final.key即为weblogic演示密钥库的私钥文件。final.key的密钥格式为

```
-----BEGIN RSA PRIVATE KEY-----  
......  
-----END RSA PRIVATE KEY-----  

```

**修改weblogic停止脚本**

需要修改weblogic的停止脚本“stopWebLogic.xx”，将ADMIN_URL字段的“t3”改为“t3s”，并在java调用weblogic.WLST类的JVM启动参数中加入“-Dweblogic.security.TrustKeyStore=DemoTrust”，使weblogic在调用停止脚本时使用演示证书，否则会出现证书不被信任的错误。

### 使用自定义证书进行分析(方法二)

**生成自定义密钥库**

使用以下命令生成自定义密钥库。

```
set keystore=keystore.jks
set alias=server
set pwd=123456
set url=url-test
set validity=7300

keytool -genkey -alias %alias% -keyalg RSA -keysize 2048 -keystore %keystore% -storetype jks -storepass %pwd% -keypass %pwd% -dname "CN=%url%, OU=companyName, O=companyName, L=cityName, ST=provinceName, C=CN" -validity %validity%

```

生成的密钥库名称为keystore.jks，密钥库密码与私钥密码均为“123456”。

**使weblogic使用指定的密钥库**

将上述步骤生成的密钥库文件keystore.jks复制到weblogic的domain目录中。

登录weblogic控制台，在AdminServer的密钥库界面，选择密钥库类型为“定制标识和 Java 标准信任”(Custom Identity and Java Standard Trust)，定制标识密钥库输入“keystore.jks”，定制标识密钥库类型输入“JKS”，定制标识密钥库密码短语与确认定制标识密钥库密码短语输入“123456”，保存上述修改。

![](http://drops.javaweb.org/uploads/images/f8b9f329ef1840cadc416a0f3d12ace6f025ebe5.jpg)

在AdminServer的SSL界面，私有密钥别名输入“server”，私有密钥密码短语与确认私有密钥密码短语输入“123456”。

![](http://drops.javaweb.org/uploads/images/5630b68d5829481146ec959bb884893f33e6b7da.jpg)

使用HTTPS对应的URL打开weblogic控制台，确保可以正常登录，查看证书信息如下。

![](http://drops.javaweb.org/uploads/images/f85c3cce539de41b4bdee5c670f330132a1ea93f.jpg)

![](http://drops.javaweb.org/uploads/images/faae38d07fd2b431608ed1a9788e18dd966eb54b.jpg)

**将自定义证书导入java信任密钥库中**

在上一步骤中可以看到Java标准信任密钥库对应的文件为weblogic的JDK目录中的“jdk\jre\lib\security\cacerts”文件，密钥类型也是JKS。

当weblogic作为SSL客户端连接服务器时，会检查服务器的证书链是否与weblogic的JDK目录中的cacerts文件匹配。

需要将自定义证书的公钥导入weblogic的JDK目录中的cacerts文件中，否则在调用weblogic停止脚本时，会由于证书不受信任而失败。

使用以下命令导出自定义证书的公钥。

```
set keystore=keystore.jks
set alias=server
set pwd=123456
set exportcert=export.cer

keytool -export -alias %alias% -keystore %keystore% -file %exportcert% -storepass %pwd%

```

导出的公钥文件为export.cert。

使用以下命令将公钥导入weblogic的JDK目录的cacerts文件中，在导入前需要备份cacerts。cacerts密钥库的默认密码为changeit，可进行修改。

```
set keystore=cacerts
set alias=server
set pwd=changeit
set cert=export.cer

keytool -import -alias %alias% -keystore %keystore% -trustcacerts -storepass %pwd% -file %cert%

```

**生成自定义证书的私钥文件**

使用以下命令生成自定义证书的私钥文件。

```
set keystore=keystore.jks
set tmp_p12=tmp.p12

set storepass=123456
set keypass=123456
set alias=server
set pwd_new=123456

keytool -importkeystore -srckeystore %keystore% -destkeystore %tmp_p12% -srcstoretype JKS -deststoretype PKCS12 -srcstorepass %storepass% -deststorepass %pwd_new% -srcalias %alias% -destalias %alias% -srckeypass %keypass% -destkeypass %pwd_new% 

set out_pem=tmp.rsa.pem
set final_pem=final.key

openssl pkcs12 -in %tmp_p12% -nodes -out %out_pem% -passin pass:%pwd_new%
openssl rsa -in %out_pem% -check > %final_pem% 

```

最终生成的final.key即为自定义证书的私钥文件。

**修改weblogic停止脚本**

需要修改weblogic的停止脚本“stopWebLogic.xx”，将`ADMIN_URL`字段的“`t3`”改为“`t3s`”，并在java调用weblogic.WLST类的JVM启动参数中加入“`-Dweblogic.security.TrustKeyStore=DemoTrust`”。

除了以上修改外，还需在停止脚本的JVM启动参数中加入“`-Dweblogic.security.SSL.ignoreHostnameVerification=true`”，避免因自定义证书中的地址与停止脚本实际访问的ssl服务的地址不一致而出现错误。

### 调用weblogic停止脚本并抓包

前文中已将weblogic的停止脚本“stopWebLogic.xx”中的访问链接改为t3s协议，会使用SSL协议进行通信。

需要调用weblogic的停止脚本并进行抓包。由于停止脚本会与同一台机器的weblogic通信，在Linux环境中抓包较为方便，需要使用tcpdump对Loopback对应的网卡进行抓包。

### 使用Wireshark解密SSL通信数据

前文已生成了weblogic的私钥文件，并对weblogic停止脚本调用过程进行了抓包，可以使用Wireshark解密对应的SSL通信数据。

首先在Wireshark中设置需要使用的私钥文件，打开Wireshark菜单的“Edit->Preferences”，打开“Protocols->SSL”，点击“RSA keys list”旁的“Edit”按钮，如下图。

![](http://drops.javaweb.org/uploads/images/176c845921c906f789e5caec60b70e6e87002818.jpg)

添加一行配置，IP为weblogic服务器的IP，Port为weblogic的SSL监听端口，Protocol为tcp，Key File为之前已生成的weblogic的SSL证书的私钥文件。

![](http://drops.javaweb.org/uploads/images/0b5cc51dcade175d81d76c8fea1e104c3fdc9c48.jpg)

使用Wireshark打开抓包文件，可以看到原本为加密形式的通信数据有部分已被解密，找到T3协议头相关数据，可以看到停止脚本向weblogic发送的T3协议头以“t3s”开头。

![](http://drops.javaweb.org/uploads/images/172b28ad9955f7d9dc8ee89531a0252bf0e03b60.jpg)

服务器返回的数据如下。

![](http://drops.javaweb.org/uploads/images/741d6993289726e8d00b58da7f4c76fc76ebce11.jpg)

![](http://drops.javaweb.org/uploads/images/767d845c2b35926bdd753c1ae29c7dfc42618680.jpg)

![](http://drops.javaweb.org/uploads/images/95a7947d5101c7a600fd4097de04331fe791314d.jpg)

费了老大的劲，才发现原来**weblogic开放HTTPS服务后，t3协议头的前几个字节由“t3”变成了“t3s”**。

以上步骤在Linux环境的weblogic 10.3.4测试成功。

### JAVA反序列化漏洞调用过程

当weblogic开放HTTPS服务时，JAVA反序列化漏洞的调用过程如下。

```
at org.apache.commons.collections.functors.InvokerTransformer.transform(InvokerTransformer.java:132)  
at org.apache.commons.collections.functors.ChainedTransformer.transform(ChainedTransformer.java:122)  
at org.apache.commons.collections.map.TransformedMap.checkSetValue(TransformedMap.java:203)  
at org.apache.commons.collections.map.AbstractInputCheckedMapDecorator$MapEntry.setValue(AbstractInputCheckedMapDecorator.java:191)  
at sun.reflect.annotation.AnnotationInvocationHandler.readObject(AnnotationInvocationHandler.java:334)  
at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)  
at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:39)  
at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:25)  
at java.lang.reflect.Method.invoke(Method.java:597)  
at java.io.ObjectStreamClass.invokeReadObject(ObjectStreamClass.java:974)  
at java.io.ObjectInputStream.readSerialData(ObjectInputStream.java:1849)  
at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:1753)  
at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1329)  
at java.io.ObjectInputStream.readObject(ObjectInputStream.java:351)  
at weblogic.rjvm.InboundMsgAbbrev.readObject(InboundMsgAbbrev.java:65)  
at weblogic.rjvm.InboundMsgAbbrev.read(InboundMsgAbbrev.java:37)  
at weblogic.rjvm.MsgAbbrevJVMConnection.readMsgAbbrevs(MsgAbbrevJVMConnection.java:283)  
at weblogic.rjvm.MsgAbbrevInputStream.init(MsgAbbrevInputStream.java:210)  
at weblogic.rjvm.MsgAbbrevJVMConnection.dispatch(MsgAbbrevJVMConnection.java:498)  
at weblogic.rjvm.t3.MuxableSocketT3.dispatch(MuxableSocketT3.java:330)  
at weblogic.socket.BaseAbstractMuxableSocket.dispatch(BaseAbstractMuxableSocket.java:298)  
at weblogic.socket.SSLFilterImpl.dispatch(SSLFilterImpl.java:258)  
at weblogic.socket.SocketMuxer.readReadySocketOnce(SocketMuxer.java:950)  
at weblogic.socket.SocketMuxer.readReadySocket(SocketMuxer.java:898)  
at weblogic.socket.PosixSocketMuxer.processSockets(PosixSocketMuxer.java:130)  
at weblogic.socket.SocketReaderRequest.run(SocketReaderRequest.java:29)  
at weblogic.socket.SocketReaderRequest.execute(SocketReaderRequest.java:42)  
at weblogic.kernel.ExecuteThread.execute(ExecuteThread.java:145)  
at weblogic.kernel.ExecuteThread.run(ExecuteThread.java:117)

```

0x03 如何控制开放HTTPS服务的weblogic服务器
==============================

* * *

### 如何发送T3协议数据

利用weblogic的JAVA反序列化漏洞时，必须向weblogic发送T3协议头。**当weblogic开放HTTPS服务时，向其发送的T3协议头应以“t3s”开头。向weblogic发送数据时应使用SSL协议，且不应对服务器的证书进行验证。**

无论weblogic开放HTTP服务还是HTTPS服务，在向weblogic发送利用JAVA反序列化漏洞的序列化数据时，数据内容不需要改变。

### 如何调用weblogic的RMI服务

可以利用weblogic的JAVA反序列化数据使weblogic在服务器生成指定的jar文件并加载，在jar文件中开启weblogic的RMI服务，可以从公网直接调用，能够控制服务器。

当weblogic开放HTTPS服务时，调用weblogic的RMI服务时有几点需要进行修改。

1.  在调用weblogic的RMI服务时，使用的URL应改为以“t3s”开头；
2.  在调用weblogic的RMI服务时，客户端需要引入weblogic.jar。使用t3s协议时，weblobic.jar会尝试从当前目录读取weblogic授权文件license.bea，需要保证weblogic.jar能正确地读取该文件；
3.  weblogic.jar中会对服务器证书进行验证，判断其是否为可信证书。由于可能遇到服务器的证书未经过CA认证，因此需要修改证书验证的相关代码，忽略证书未经认证的问题；
4.  JVM启动参数需要增加“`-Dweblogic.security.SSL.ignoreHostnameVerification=true`”，避免因自定义证书中的地址与停止脚本实际访问的ssl服务的地址不一致而出现错误。

0x04 可行的漏洞修复方法
==============

### 将SSL服务转移至其他设备

将SSL服务转移至weblogic服务器外层的设备实现，如SSL网关、负载均衡、单独部署的web代理等，将HTTP请求转发至weblogic，可以修复JAVA反序列化漏洞。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">需要对SSL证书进行格式转换；需要购买设备；无法防护从内网发起的JAVA反序列化漏洞攻击</td></tr></tbody></table>

### 将SSL服务转移至weblogic服务器的web代理

在weblogic所在服务器安装web代理应用，如apache、nginx等，将SSL服务转移至web代理应用，使web代理监听原有的weblogic监听端口，并将HTTP请求转发给本机的weblogic，可以修复JAVA反序列化漏洞。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响；不需要购买设备</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">需要对SSL证书进行格式转换；无法防护从内网发起的JAVA反序列化漏洞攻击；会增加服务器的性能开销</td></tr></tbody></table>

### 将SSL服务转移至weblogic服务器的web代理并修改weblogic的监听IP

将weblogic的监听地址修改为“127.0.0.1”或“localhost”，只允许本机访问weblogic服务。

在weblogic所在服务器安装web代理应用，如apache、nginx等，将SSL服务转移至web代理应用，使web代理监听原有的weblogic监听端口，并将HTTP请求转发给本机的weblogic，可以修复JAVA反序列化漏洞。web代理的监听IP需设置为“0.0.0.0”，否则其他服务器无法访问。

需要将weblogic停止脚本中的ADMIN_URL参数中的IP修改为“127.0.0.1”或“localhost”，否则停止脚本将不可用。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响；不需要购买设备；能够防护从内网发起的JAVA反序列化漏洞攻击</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">需要对SSL证书进行格式转换；会增加服务器的性能开销</td></tr></tbody></table>

### 修改weblogic的代码

weblogic处理T3S协议的类为“weblogic.rjvm.t3.MuxableSocketT3S”，继承自“weblogic.rjvm.t3.MuxableSocketT3”类，且MuxableSocketT3S类中没有对dispatch方法进行重写，因此可以采用与[修复weblogic的JAVA反序列化漏洞的多种方法](http://drops.wooyun.org/web/13470 "修复weblogic的JAVA反序列化漏洞的多种方法")中“修改weblogic的代码”部分相同的修复方法。具体步骤略。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: rgb(255, 255, 255); border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224); font-family: Helvetica, Arial, &quot;Hiragino Sans GB&quot;, sans-serif; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial;"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">不需要对SSL证书进行格式转换；对系统影响小，不需测试对现有系统功能的影响；不需要购买设备；能够防护从内网发起的JAVA反序列化漏洞攻击；不会增加服务器的性能开销</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">存在商业风险，可能给oracle的维保带来影响</td></tr></tbody></table>

0x05 结束
=======

* * *

无论weblogic服务器开放HTTP服务还是HTTPS服务，都是有可能利用JAVA反序列化漏洞控制服务器的。JAVA反序列化漏洞的影响，应该会持续很长的时间。