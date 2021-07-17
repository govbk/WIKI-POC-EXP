# 修复weblogic的JAVA反序列化漏洞的多种方法

0x00 前言
=======

* * *

目前oracle还没有在公开途径发布weblogic的JAVA反序列化漏洞的官方补丁，目前看到的修复方法无非两条：

1.  使用SerialKiller替换进行序列化操作的ObjectInputStream类;
2.  在不影响业务的情况下，临时删除掉项目里的 "org/apache/commons/collections/functors/InvokerTransformer.class"文件。

ObjectInputStream类为JRE的原生类，InvokerTransformer.class为weblogic基础包中的类，对上述两个类进行修改或删除，实在无法保证对业务没有影响。如果使用上述的修复方式，需要大量的测试工作。且仅仅删除InvokerTransformer.class文件，无法保证以后不会发现其他的类存在反序列化漏洞。

因此本文针对weblogic的JAVA序列化漏洞进行了分析，对多个版本的weblogic进行了测试，并提出了更加切实可行的修复方法。

0x01 为什么选择weblogic的JAVA反序列化漏洞进行分析
=================================

* * *

1.  weblogic与websphere为金融行业使用较多的企业级JAVA中间件；
2.  weblogic比websphere市场占有率高；
3.  利用websphere的JAVA反序列化漏洞时需要访问8880端口，该端口为websphere的wsadmin服务端口，该端口不应该暴露在公网。如果有websphere服务器的8880端口在公网可访问，说明该服务器的安全价值相对较低；
4.  利用weblogic的JAVA反序列化漏洞能够直接控制服务器，危害较大，且weblogic通常只有一个服务端口，无法通过禁用公网访问特定端口的方式修复漏洞。

0x02 已知条件
=========

* * *

breenmachine的“What Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common? This Vulnerability.”文章中对weblogic的JAVA序列化漏洞进行了分析，读完这篇文章关于weblogic相关的描述部分后，我们知道了以下情况。

1.  可通过搜索代码查找weblogic的jar包中是否包含特定的JAVA类；
2.  在调用weblogic的停止脚本时，会向weblogic发送JAVA序列化数据；
3.  可通过ObjectInputStream.readObject方法解析JAVA序列化数据；
4.  weblogic发送的T3数据的前几个字节为数据长度；
5.  替换weblogic发送的T3数据中的某个序列化数据为恶意序列化数据，可以使weblogic执行指定的代码。

0x03 漏洞分析
=========

* * *

weblogic发送的JAVA序列化数据抓包分析
------------------------

根据breenmachine的文章我们知道了，在调用weblogic的停止脚本时，会向weblogic发送JAVA序列化数据，我们来重复这个过程。

数据包分析工具还是Windows环境的Wireshark比较好用，但Windows环境默认无法在访问本机监听的端口时进行抓包。上述问题是可以解决的，也可在Windows机器调用其他机器的weblogic停止脚本并使用Wireshark进行抓包；或者在Linux环境使用tcpdump进行抓包，使用Wireshark分析生成的数据包。

### Windows环境如何在访问本机监听的端口时进行抓包

该问题可通过以下方法解决：

1.  增加路由策略，`route add 【本机IP，不能使用127.0.0.1】 mask 255.255.255.255 【默认网关IP】 metric 1`，之后可以使用Wireshark抓包分析。XP测试成功，win7失败。
2.  使用RawCap工具，可对127.0.0.1进行抓包，产生的抓包文件可以使用Wireshark分析。win7测试成功，XP失败。下载地址为[http://www.netresec.com/?page=RawCap](http://www.netresec.com/?page=RawCap)。

### 如何在Windows机器调用其他机器的weblogic停止脚本

编辑domain的bin目录中的stopWebLogic.cmd文件，找到“`ADMIN_URL=t3://[IP]:[端口]`”部分，[IP]一般为本机的主机名，[端口]一般为7001。将[IP]与[端口]分别修改为其他weblogic所在机器的IP与weblogic监听端口。执行修改后的stopWebLogic.cmd脚本并抓包。

### 使用Wireshark对数据包进行分析

在完成了针对weblogic停止脚本调用过程的抓包后，使用Wireshark对数据包进行分析。可使用IP或端口等条件进行过滤，只显示与调用weblogic停止脚本相关的数据包。

已知JAVA序列化数据的前4个字节为“AC ED 00 05”，使用“tcp contains ac:ed:00:05”条件过滤出包含JAVA序列化数据的数据包，并在第一条数据包点击右键选择“Follow TCP Stream”，如下图。

![pic](http://drops.javaweb.org/uploads/images/ba65895286101915eafb2ffa9826da3dd61ec51e.jpg)

使用十六进制形式查看数据包，查找“ac ed 00 05”，可以找到对应的数据，可以确认抓包数据中包含JAVA序列化数据。

![pic](http://drops.javaweb.org/uploads/images/e2484c800a70a7f104c1f27bf59c42199091ec90.jpg)

取消对"ac ed 00 05"的过滤条件，使用ASCII形式查看第一个数据包，内容如下。

![pic](http://drops.javaweb.org/uploads/images/c6b29d6cc6035e6328aa932da10955da7930b79c.jpg)

可以看到当weblogic客户端向weblogic服务器发送序列化数据时，发送的第一个包为T3协议头，本文测试时发送的T3协议头为“t3 9.2.0\nAS:255\nHL:19\n\n”，第一行为“t3”加weblogic客户端的版本号。weblogic服务器的返回数据为“HELO:10.0.2.0.false\nAS:2048\nHL:19\n\n”，第一行为“HELO:”加weblogic服务器的版本号。weblogic客户端与服务器发送的数据均以“\n\n”结尾。

### 将Wireshark显示的数据包转换为JAVA代码

从上文的截图可以看到数据包中JAVA序列化数据非常长，且包含不可打印字符，无法直接导出到JAVA代码中。

在Wireshark中，客户端向服务器发送的数据显示为红色，服务器向客户端返回的数据显示为蓝色。

使用C数组形式查看第一个数据包，peer0_x数组为Packet 1，将peer0_x数组复制为一个C语言形式的数组，格式如“`char peer0_0[] = { 0x01, 0x02 ...};`”，将上述数据的“char”修改为“byte”，“0x”替换为“(byte)0x”，可以转换为能直接在JAVA代码中使用的形式，格式如“`byte peer0_0[] = {(byte)0x00, (byte)0x02 ...}`”。

![pic](http://drops.javaweb.org/uploads/images/3f93f5ddd9cdf7bd389edc9799e554a3634f1ce2.jpg)

### 对JAVA序列化数据进行解析

根据breenmachine的文章我们知道了，可以使用ObjectInputStream.readObject方法解析JAVA序列化数据。

使用ObjectInputStream.readObject方法解析weblogic调用停止脚本时发送的JAVA序列化数据的结构，代码如下。执行下面的代码时需要将weblogic.jar添加至JAVA执行的classpath中，否则会抛出ClassNotFoundException异常。

![pic](http://drops.javaweb.org/uploads/images/a3f68485efd03c1f12f262a1843e5a8c9949d115.jpg)

上述代码的执行结果如下。

```
Data Length-Compute: 1711  
Data Length: 1711  
Object found: weblogic.rjvm.ClassTableEntry  
Object found: weblogic.rjvm.ClassTableEntry  
Object found: weblogic.rjvm.ClassTableEntry  
Object found: weblogic.rjvm.ClassTableEntry  
Object found: weblogic.rjvm.JVMID  
Object found: weblogic.rjvm.JVMID  
size: 0 start: 0 end: 234  
size: 1 start: 234 end: 348  
size: 2 start: 348 end: 591  
size: 3 start: 591 end: 986  
size: 4 start: 986 end: 1510  
size: 5 start: 1510 end: 1634  
size: 6 start: 1634 end: 1711  

```

可以看到weblogic发送的JAVA序列化数据分为7个部分，第一部分的前四个字节为整个数据包的长度(1711=0x6AF)，第二至七部分均为JAVA序列化数据。

![pic](http://drops.javaweb.org/uploads/images/437dda72ddf4cda67306b11d5a13220080f99dd7.jpg)

weblogic发送的JAVA序列化数据格式如下图。

![pic](http://drops.javaweb.org/uploads/images/e2f815467fd3abb3354bd6f0fee1402af6c6b305.jpg)

利用weblogic的JAVA反序列化漏洞
---------------------

在利用weblogic的JAVA反序列化漏洞时，需要向weblogic发送两个数据包。

第一个数据包为T3的协议头。**经测试，使用“t3 9.2.0\nAS:255\nHL:19\n\n”字符串作为T3的协议头发送给weblogic9、weblogic10g、weblogic11g、weblogic12c均合法。**向weblogic发送了T3协议头后，weblogic也会返回相应的数据，以“\n\n”结束，具体格式见前文。

第二个数据包为JAVA序列化数据，可采用两种方式产生。

第一种生成方式为，将前文所述的weblogic发送的JAVA序列化数据的第二到七部分的JAVA序列化数据的任意一个替换为恶意的序列化数据。

采用第一种方式生成JAVA序列化数据时，数据格式如下图。

![pic](http://drops.javaweb.org/uploads/images/ecbf31b310fd16dbe29729eb7e9f76b8b96f4cd8.jpg)

第二种生成方式为，将前文所述的weblogic发送的JAVA序列化数据的第一部分与恶意的序列化数据进行拼接。

采用第二种方式生成JAVA序列化数据时，数据格式如下图。

![pic](http://drops.javaweb.org/uploads/images/68987b32007303bfa6459d623184e7fe55e78fcc.jpg)

恶意序列化数据的生成过程可参考[http://drops.wooyun.org/papers/13244](http://drops.wooyun.org/papers/13244 "JAVA反序列化漏洞完整过程分析与调试")。

当向weblogic发送上述第一种方式生成的JAVA序列化数据时，weblogic会抛出如下异常。

```
java.io.EOFException  
at weblogic.utils.io.DataIO.readUnsignedByte(DataIO.java:435)  
at weblogic.utils.io.DataIO.readLength(DataIO.java:828)  
at weblogic.utils.io.ChunkedDataInputStream.readLength(ChunkedDataInputStream.java:150)  
at weblogic.utils.io.ChunkedObjectInputStream.readLength(ChunkedObjectInputStream.java:196)  
at weblogic.rjvm.InboundMsgAbbrev.read(InboundMsgAbbrev.java:37)  
at weblogic.rjvm.MsgAbbrevJVMConnection.readMsgAbbrevs(MsgAbbrevJVMConnection.java:287)  
at weblogic.rjvm.MsgAbbrevInputStream.init(MsgAbbrevInputStream.java:212)  
at weblogic.rjvm.MsgAbbrevJVMConnection.dispatch(MsgAbbrevJVMConnection.java:507)  
at weblogic.rjvm.t3.MuxableSocketT3.dispatch(MuxableSocketT3.java:489)  
at weblogic.socket.BaseAbstractMuxableSocket.dispatch(BaseAbstractMuxableSocket.java:359)  
at weblogic.socket.SocketMuxer.readReadySocketOnce(SocketMuxer.java:970)  
at weblogic.socket.SocketMuxer.readReadySocket(SocketMuxer.java:907)  
at weblogic.socket.NIOSocketMuxer.process(NIOSocketMuxer.java:495)  
at weblogic.socket.NIOSocketMuxer.processSockets(NIOSocketMuxer.java:461)  
at weblogic.socket.SocketReaderRequest.run(SocketReaderRequest.java:30)  
at weblogic.socket.SocketReaderRequest.execute(SocketReaderRequest.java:43)  
at weblogic.kernel.ExecuteThread.execute(ExecuteThread.java:147)  
at weblogic.kernel.ExecuteThread.run(ExecuteThread.java:119)

```

当向weblogic发送上述第二种方式生成的JAVA序列化数据时，weblogic会抛出如下异常。

```
weblogic.rjvm.BubblingAbbrever$BadAbbreviationException: Bad abbreviation value: 'xxx'  
at weblogic.rjvm.BubblingAbbrever.getValue(BubblingAbbrever.java:153)  
at weblogic.rjvm.InboundMsgAbbrev.read(InboundMsgAbbrev.java:48)  
at weblogic.rjvm.MsgAbbrevJVMConnection.readMsgAbbrevs(MsgAbbrevJVMConnection.java:287)  
at weblogic.rjvm.MsgAbbrevInputStream.init(MsgAbbrevInputStream.java:212)  
at weblogic.rjvm.MsgAbbrevJVMConnection.dispatch(MsgAbbrevJVMConnection.java:507)  
at weblogic.rjvm.t3.MuxableSocketT3.dispatch(MuxableSocketT3.java:489)  
at weblogic.socket.BaseAbstractMuxableSocket.dispatch(BaseAbstractMuxableSocket.java:359)  
at weblogic.socket.SocketMuxer.readReadySocketOnce(SocketMuxer.java:970)  
at weblogic.socket.SocketMuxer.readReadySocket(SocketMuxer.java:907)  
at weblogic.socket.NIOSocketMuxer.process(NIOSocketMuxer.java:495)  
at weblogic.socket.NIOSocketMuxer.processSockets(NIOSocketMuxer.java:461)  
at weblogic.socket.SocketReaderRequest.run(SocketReaderRequest.java:30)  
at weblogic.socket.SocketReaderRequest.execute(SocketReaderRequest.java:43)  
at weblogic.kernel.ExecuteThread.execute(ExecuteThread.java:147)  
at weblogic.kernel.ExecuteThread.run(ExecuteThread.java:119)

```

虽然在利用weblogic的JAVA反序列化漏洞时，weblogic会抛出上述的异常，但是weblogic已经对恶意的序列化数据执行了readObject方法，漏洞仍然会触发。

**经测试，必须先发送T3协议头数据包，再发送JAVA序列化数据包，才能使weblogic进行JAVA反序列化，进而触发漏洞。如果只发送JAVA序列化数据包，不先发送T3协议头数据包，无法触发漏洞。**

weblogic的JAVA反序列化漏洞触发时的调用过程
---------------------------

将使用FileOutputStream对一个非法的文件进行写操作的代码构造为恶意序列化数据，并发送给weblogic，当weblogic对该序列化数据执行反充列化时，会在漏洞触发时抛出异常，通过堆栈信息可以查看漏洞触发时的调用过程，如下所示。

```
org.apache.commons.collections.FunctorException: InvokerTransformer: The method 'newInstance' on 'class java.lang.reflect.Constructor' threw an exception  
at org.apache.commons.collections.functors.InvokerTransformer.transform(InvokerTransformer.java:132)  
at org.apache.commons.collections.functors.ChainedTransformer.transform(ChainedTransformer.java:122)  
at org.apache.commons.collections.map.TransformedMap.checkSetValue(TransformedMap.java:203)  
at org.apache.commons.collections.map.AbstractInputCheckedMapDecorator$MapEntry.setValue(AbstractInputCheckedMapDecorator.java:191)  
at sun.reflect.annotation.AnnotationInvocationHandler.readObject(AnnotationInvocationHandler.java:356)  
at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)  
at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:57)  
at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)  
at java.lang.reflect.Method.invoke(Method.java:606)  
at java.io.ObjectStreamClass.invokeReadObject(ObjectStreamClass.java:1017)  
at java.io.ObjectInputStream.readSerialData(ObjectInputStream.java:1893)  
at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:1798)  
at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1350)  
at java.io.ObjectInputStream.readObject(ObjectInputStream.java:370)  
at weblogic.rjvm.InboundMsgAbbrev.readObject(InboundMsgAbbrev.java:67)  
at weblogic.rjvm.InboundMsgAbbrev.read(InboundMsgAbbrev.java:39)  
at weblogic.rjvm.MsgAbbrevJVMConnection.readMsgAbbrevs(MsgAbbrevJVMConnection.java:287)  
at weblogic.rjvm.MsgAbbrevInputStream.init(MsgAbbrevInputStream.java:212)  
at weblogic.rjvm.MsgAbbrevJVMConnection.dispatch(MsgAbbrevJVMConnection.java:507)  
at weblogic.rjvm.t3.MuxableSocketT3.dispatch(MuxableSocketT3.java:489)  
at weblogic.socket.BaseAbstractMuxableSocket.dispatch(BaseAbstractMuxableSocket.java:359)  
at weblogic.socket.SocketMuxer.readReadySocketOnce(SocketMuxer.java:970)  
at weblogic.socket.SocketMuxer.readReadySocket(SocketMuxer.java:907)  
at weblogic.socket.NIOSocketMuxer.process(NIOSocketMuxer.java:495)  
at weblogic.socket.NIOSocketMuxer.processSockets(NIOSocketMuxer.java:461)  
at weblogic.socket.SocketReaderRequest.run(SocketReaderRequest.java:30)  
at weblogic.socket.SocketReaderRequest.execute(SocketReaderRequest.java:43)  
at weblogic.kernel.ExecuteThread.execute(ExecuteThread.java:147)  
at weblogic.kernel.ExecuteThread.run(ExecuteThread.java:119)

```

确定weblogic是否使用了Apache Commons Collections组件
-------------------------------------------

breenmachine在文章中写到可以通过搜索代码的方式查找weblogic的jar包中是否包含特定的JAVA类。由于特定的JAVA类可能在很多个不同的jar包中均存在，因此该方法无法准确判断weblogic是否使用了Apache Commons Collections组件特定的JAVA类。

可通过以下方法准确判断weblogic是否使用了Apache Commons Collections组件特定的JAVA类。

在weblogic中任意安装一个j2ee应用，在某个jsp中写入以下代码。

```
<%
String path = [需要查找的类的完整类名].class.getResource("").getPath();  
out.println(path);
%>

```

或以下代码。

```
<%
String path = [需要查找的类的完整类名].class.getProtectionDomain().getCodeSource().getLocation().getFile();  
out.println(path);
%>

```

使用浏览器访问上述jsp文件，可以看到对应的类所在的jar包的完整路径。

通过上述方法查找“org.apache.commons.collections.map.TransformedMap”所在的jar包，示例如下。

![pic](http://drops.javaweb.org/uploads/images/931b6819816e0b4ac0d0ad4ca55a46ce3a95f2b6.jpg)

不同版本的weblogic对Apache Commons Collections组件的使用
---------------------------------------------

“org.apache.commons.collections.map.TransformedMap”所在的weblogic的jar包信息如下。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">weblogic版本</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">TransformedMap类所在jar包路径</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">9.2</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">无</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">10.2.1(weblogic 10g)、10.3.4(weblogic 11g)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">weblogic安装目录的modules/com.bea.core.apache.commons.collections_3.2.0.jar</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">12.1.3(weblogic 12c)</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">weblogic安装目录的wlserver/modules/features/weblogic.server.merged.jar</td></tr></tbody></table>

由于weblogic 9.2未包含TransformedMap类，因此无法触发反序列化漏洞，weblogic 10g、weblogic 11g、weblogic 12c均包含TransformedMap类，因此会触发反序列化漏洞。

0x04 漏洞修复
=========

* * *

漏洞修复思路
------

weblogic的默认服务端口为7001，该端口提供了对HTTP(S)、SNMP、T3等协议的服务。由于weblogic的不同协议均使用一个端口，因此无法通过防火墙限制端口访问的方式防护JAVA反序列化漏洞。

在绝大多数应用的使用场景中，用户只需要在公网能够使用HTTP(S)协议访问web应用服务器即可。对于weblogic服务器，在绝大多数情况下，只需要能够在公网访问weblogic提供的HTTP(S)协议的服务即可，并不需要访问T3协议。

少数情况下，运维人员需要使用weblogic的T3协议：

*   在weblogic服务器本机执行weblogic的停止脚本；
*   通过WLST对weblogic进行脚本化配置；
*   编写使用T3协议通信的程序对weblogic进行状态监控及其他管理功能。

T3协议与HTTP协议均基于TCP协议，T3协议以"t3"开头，HTTP协议以“GET”、“POST”等开头，两者有明显的区别。

**因此可以限定只允许特定服务器访问weblogic服务器的T3协议，能够修复weblogic的JAVA反序列化漏洞。即使今后发现了weblogic的其他类存在JAVA反序列化漏洞，也能够防护。**

若将weblogic修复为发送T3协议时要求发送weblogic的用户名与密码，也能够修复weblogic的反序列化问题，但会带来密码如何在weblogic客户端存储的问题。

无效的漏洞修复方法
---------

首先尝试将应用部署到非管理Server中，判断其服务端口是否也提供T3协议的服务。

AdminServer是weblogic默认的管理Server，添加一个名为“Server-test”的非管理Server后，weblogic的服务器信息如下。管理Server与非管理Server使用不同的监听端口，可将j2ee应用部署在非管理Server中，这样可以使weblogic控制台与应用使用不同的端口提供服务。

![pic](http://drops.javaweb.org/uploads/images/a15d3a2d0de78a45ba63bcf67fe12f33aff2c884.jpg)

经测试，新增的非管理Server的监听端口也提供了T3协议的服务，也存在JAVA反序列化漏洞。因此这种修复方式对于JAVA反序列化漏洞无效，但可将weblogic控制台端口与应用端口分离，可以使用防火墙禁止通过公网访问weblogic的控制台。

websphere的服务端口
--------------

我们来看另一款使用广泛的企业级JAVA中间件：websphere的服务端口情况。从下图可以看到，websphere的应用默认HTTP服务端口为9080，应用默认HTTPS服务端口为9443，控制台默认HTTP服务端口为9060，控制台默认HTTPS服务端口为9043，接收JAVA序列化数据的端口为8880。因此只要通过防火墙使公网无法访问websphere服务器的8880端口，就可以防止通过公网利用websphere的JAVA反序列化漏洞。

![pic](http://drops.javaweb.org/uploads/images/2fe8ff3525a05793e927a66a0eec49d683e4a6f1.jpg)

网络设备对数据包的影响
-----------

对安全有一定要求的公司，在部署需要向公网用户提供服务的weblogic服务器时，可能选择下图的部署架构(内网中不同网络区域间的防火墙已省略)。

![pic](http://drops.javaweb.org/uploads/images/7a2a87f8e0476851cefbeb16e2f18f6b559bc7a4.jpg)

上述网络设备对数据包的影响如下。

1.  IPS
    
    IPS可以更新防护规则，可能有厂家的IPS已经设置了对JAVA反序列化漏洞的防护规则，会阻断恶意的JAVA序列化数据包。
    
2.  防火墙
    
    这里的防火墙指传统防火墙，不是指下一代防火墙，仅关心IP与端口，不关心数据包内容，无法阻断恶意的JAVA序列化数据包。
    
3.  WAF
    
    与IPS一样，能否阻断恶意的JAVA序列化数据包决定于防护规则。
    
4.  web代理
    
    仅对HTTP协议进行代理转发，不会对T3协议进行代理转发。
    
5.  负载均衡
    
    可以指定需要进行负载均衡的协议类型，安全起见应选择HTTP协议而不是TCP协议，只对HTTP协议进行转发，不对T3协议进行转发。
    

根据以上分析可以看出，web代理和负载均衡能够稳定保证只转发HTTP协议的数据，不会转发T3协议的数据，因此能够防护JAVA反序列化漏洞。

**如果在公网访问weblogic服务器的路径中原本就部署了web代理或负载均衡，就能够防护从公网发起的JAVA反序列化漏洞攻击。**这也是为什么较少发现大型公司的weblogic反序列化漏洞的原因，其网络架构决定了weblogic的JAVA反序列化漏洞无法在公网利用。

可行的漏洞修复方法
---------

### 部署负载均衡设备

在weblogic服务器外层部署负载均衡设备，可以修复JAVA反序列化漏洞。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">需要购买设备；无法防护从内网发起的JAVA反序列化漏洞攻击</td></tr></tbody></table>

### 部署单独的web代理

在weblogic服务器外层部署单独的web代理，可以修复JAVA反序列化漏洞。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">同上</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">同上</td></tr></tbody></table>

### 在weblogic服务器部署web代理

在weblogic控制台中修改weblogic的监听端口，如下图。

![pic](http://drops.javaweb.org/uploads/images/7c9f0fdf6d38d0ac61b8b02600f216fff13af3b0.jpg)

在weblogic所在服务器安装web代理应用，如apache、nginx等，使web代理监听原有的weblogic监听端口，并将HTTP请求转发给本机的weblogic，可以修复JAVA反序列化漏洞。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响；不需要购买设备</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">无法防护从内网发起的JAVA反序列化漏洞攻击；会增加服务器的性能开销</td></tr></tbody></table>

### 在weblogic服务器部署web代理并修改weblogic服务器的监听IP

在weblogic控制台中修改weblogic的监听端口，并将监听地址修改为“127.0.0.1”或“localhost”，如下图。经过上述修改后，只有weblogic服务器本机才能访问weblogic服务。

![pic](http://drops.javaweb.org/uploads/images/fd548d297c087f5c5e218f9e0d27a8763b492339.jpg)

在weblogic所在服务器安装web代理应用，如apache、nginx等，使web代理监听原有的weblogic监听端口，并将HTTP请求转发给本机的weblogic，可以修复JAVA反序列化漏洞。web代理的监听IP需设置为“0.0.0.0”，否则其他服务器无法访问。

需要将weblogic停止脚本中的ADMIN_URL参数中的IP修改为“127.0.0.1”或“localhost”，否则停止脚本将不可用。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响；不需要购买设备；能够防护从内网发起的JAVA反序列化漏洞攻击</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">会增加服务器的性能开销</td></tr></tbody></table>

### 修改weblogic的代码

weblogic处理T3协议的类为“weblogic.rjvm.t3.MuxableSocketT3”，不同版本的weblogic的该类在不同的jar包中，查找某个类所在的jar包的方法见前文“确定weblogic是否使用了Apache Commons Collections组件”部分。

使用eclipse或其他IDE创建java工程，创建weblogic.rjvm.t3包，并在其中创建MuxableSocketT3.java文件。在定位到“weblogic.rjvm.t3.MuxableSocketT3”类所在的weblogic的jar包后，对其进行反编译，将对应的jar包加入到创建的java工程的classpath中。将原始MuxableSocketT3类的反编译代码复制到创建的java工程的MuxableSocketT3.java中，若其中引入了其他jar包中的类，需要将对应的jar包也加入到java工程的classpath中。

![pic](http://drops.javaweb.org/uploads/images/bfcd4910b2276b17d6dda964d6b23a1e14a9bfbd.jpg)

weblogic处理T3协议时会调用MuxableSocketT3类的dispatch方法，weblogic 12.1.3的dispatch方法原始代码如下。

```
public final void dispatch(Chunk list) {
    if (!(this.bootstrapped)) {
        try {
            readBootstrapMessage(list);
            this.bootstrapped = true;
        } catch (IOException ioe) {
            SocketMuxer.getMuxer().deliverHasException(getSocketFilter(),
                    ioe);
        }
    } else
        this.connection.dispatch(list);
}

```

在该方法中增加限制客户端IP的处理，若发送T3协议数据的客户端IP不是允许的IP，则拒绝连接。增加限制后的dispatch方法代码如下。

```
public final void dispatch(Chunk list) {
    if (!(this.bootstrapped)) {
        try {

            //add
            String ip = getSocket().getInetAddress().getHostAddress();
            System.out.println("MuxableSocketT3-dispatch-ip: " + ip);
            if(!ip.equals("127.0.0.1") && !ip.equals("0:0:0:0:0:0:0:1"))
                rejectConnection(1, "Illegal IP");
            //add-end

            readBootstrapMessage(list);
            this.bootstrapped = true;
        } catch (IOException ioe) {
            SocketMuxer.getMuxer().deliverHasException(getSocketFilter(),
                    ioe);
        }
    } else
        this.connection.dispatch(list);
}

```

停止weblogic，将编译生成的MuxableSocketT3*.class文件替换至MuxableSocketT3所在的jar包中，启动weblogic，再次向weblogic发送T3协议数据包，可以看到如下输出。

![pic](http://drops.javaweb.org/uploads/images/7298d2438853d2b2c3a57bf0ba83f8c590c6c10e.jpg)

上图说明上文增加的代码已正确运行，对weblogic的正常功能没有影响，且能够限制发送T3数据的客户端IP，能够修复反序列化漏洞。

当weblogic处理HTTP协议时，不会调用MuxableSocketT3类，因此上述修改不会影响正常的业务功能。

可通过环境变量或配置文件指定允许发送T3协议的客户端IP，在修改后的dispatch方法中读取，本文的示例仅允许本机发送T3协议。需要将weblogic停止脚本中的ADMIN_URL参数中的IP修改为“127.0.0.1”或“localhost”，否则停止脚本将不可用。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">优点</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">缺点</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">对系统影响小，不需测试对现有系统功能的影响；不需要购买设备；能够防护从内网发起的JAVA反序列化漏洞攻击；不会增加服务器的性能开销</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">存在商业风险，可能给oracle的维保带来影响</td></tr></tbody></table>

上述修复方法的最大问题在于可能给oracle维保带来影响，不过相信没有与oracle签订维保合同的公司也是很多的，如果不担心相关的问题，倒是可以使用这种修复方法。如果能够要求oracle提供官方补丁，当然是最好不过了。