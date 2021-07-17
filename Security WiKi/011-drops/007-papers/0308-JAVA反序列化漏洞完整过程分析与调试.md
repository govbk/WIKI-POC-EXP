# JAVA反序列化漏洞完整过程分析与调试

0x00 前言
=======

* * *

关于JAVA的Apache Commons Collections组件反序列漏洞的分析文章已经有很多了，当我看完很多分析文章后，发现JAVA反序列漏洞的一些要点与细节未被详细描述，还需要继续分析之后才能更进一步理解并掌握这个漏洞。

上述的要点与细节包括：

1.  为什么需要使用JAVA反射机制
2.  为什么需要利用sun.reflect.annotation.AnnotationInvocationHandler类
3.  为什么调用TransformedMap类的decorate方法时，参数一的Map对象需要put进"value"与非空的值*
4.  为什么AnnotationInvocationHandler类的实例化参数一需要为java.lang.annotation.Retention类

为了方便和我一样的小白们理解这个漏洞，我将JAVA反序列化漏洞完整过程的分析与调试进行了整理。分析过程中利用的类为TransformedMap与AnnotationInvocationHandler。发现漏洞不是我等小白能力所及，因此本文不以挖掘漏洞的角度来进行分析，而是在已知漏洞存在的情况下分析漏洞。

0x01 基础知识
=========

* * *

JAVA序列化与反序列化
------------

### JAVA序列化简介

为了分析JAVA的反序列化漏洞，首先需要了解JAVA的序列化与反序列化机制。

以下内容来自JDK1.6 API文档中对ObjectOutputStream的说明。

> ObjectOutputStream 将 Java 对象的基本数据类型和图形写入 OutputStream。可以使用 ObjectInputStream 读取（重构）对象。通过在流中使用文件可以实现对象的持久存储。如果流是网络套接字流，则可以在另一台主机上或另一个进程中重构对象。
> 
> 只能将支持 java.io.Serializable 接口的对象写入流中。每个 serializable 对象的类都被编码，编码内容包括类名和类签名、对象的字段值和数组值，以及从初始对象中引用的其他所有对象的闭包。
> 
> writeObject 方法用于将对象写入流中。所有对象（包括 String 和数组）都可以通过 writeObject 写入。可将多个对象或基元写入流中。必须使用与写入对象时相同的类型和顺序从相应 ObjectInputstream 中读回对象。

即使用ObjectOutputStream.writeObject方法可对实现了Serializable接口的对象进行序列化，序列化后的数据可存储在文件中，或通过网络传输。

### JAVA反序列化简介

以下内容来自JDK1.6 API文档中对ObjectInputStream的说明。

> ObjectInputStream 对以前使用 ObjectOutputStream 写入的基本数据和对象进行反序列化。
> 
> ObjectOutputStream 和 ObjectInputStream 分别与 FileOutputStream 和 FileInputStream 一起使用时，可以为应用程序提供对对象图形的持久存储。ObjectInputStream 用于恢复那些以前序列化的对象。其他用途包括使用套接字流在主机之间传递对象，或者用于编组和解组远程通信系统中的实参和形参。
> 
> ObjectInputStream 确保从流创建的图形中所有对象的类型与 Java 虚拟机中显示的类相匹配。使用标准机制按需加载类。
> 
> 只有支持 java.io.Serializable 或 java.io.Externalizable 接口的对象才能从流读取。
> 
> readObject 方法用于从流读取对象。应该使用 Java 的安全强制转换来获取所需的类型。在 Java 中，字符串和数组都是对象，所以在序列化期间将其视为对象。读取时，需要将其强制转换为期望的类型。

即使用ObjectInputStream.readObject方法可对序列化的数据进行反序列化。当实现了Serializable接口的对象被反序列化时，该对象的readObject方法会被调用。

### 对JAVA基础类的序列化与反序列化测试

String实现了Serializable接口，可进行序列化。

![](http://drops.javaweb.org/uploads/images/098ba889c1ba9474f26e540ea02a8ee6d32848c8.jpg)

以下测试代码会对String类的对象进行序列化，将序列化的数据保存在文件中，再从文件读取序列化的数据进行反序列化。执行上述代码后，能够正确输出原String类的对象的值。

![](http://drops.javaweb.org/uploads/images/f9622a3ba17a73ba4068d7eef416231694bfa1c4.jpg)

### JAVA序列化数据的magic number

java.io.ObjectStreamConstants类中定义了STREAM_MAGIC与STREAM_VERSION，查看JDK1.5、1.6、1.7、1.8的ObjectStreamConstants类，STREAM_MAGIC值均为0xaced，STREAM_VERSION值均为5。JDK1.6的源码中，上述变量的代码如下。

```
package java.io;

/**
 * Constants written into the Object Serialization Stream. 
 *
 * @author  unascribed
 * @version %I%, %G%
 * @since JDK 1.1
 */
public interface ObjectStreamConstants {

/**
 * Magic number that is written to the stream header.
 */
final static short STREAM_MAGIC = (short)0xaced;

/**
 * Version number that is written to the stream header.
 */
final static short STREAM_VERSION = 5;

```

即0xaced为JAVA对象序列化流的魔数，0x0005为JAVA对象序列化的版本号，JAVA对象序列化数据的前4个字节为“**AC ED 00 05**”。

查看上一步骤生成的保存了序列化数据的文件，文件内容开头为“AC ED 00 05”，与上述描述相符。

![](http://drops.javaweb.org/uploads/images/68b2064c010f7c6e8d8610144f87279ea2cf2357.jpg)

### 对自定义类的序列化与反序列化测试

以下测试代码为test.SerializeMyClass类，在其中定义了内部类MyObject。MyObject类实现了Serializable接口，SerializeMyClass类会对MyObject类的对象进行序列化，将序列化的数据保存在文件中，再从文件读取序列化的数据进行反序列化。

![](http://drops.javaweb.org/uploads/images/9b862d2b41aaacb7454e08d4847f16724b17d297.jpg)

执行结果如下

```
MyObject(String name) tttest
MyObject-readObject!!!!!!!!!!!!!! tttest
tttest!  

```

可以看到MyObject类实现的Serializable接口的readObject方法会被调用，且对象被序列化再反序列化后，对其值不影响。

生成的保存了序列化数据的文件，文件内容开头也为“AC ED 00 05”，可以看到文件内容包含了包名与类名、类中包含的变量名称、类型及变量的值。

![](http://drops.javaweb.org/uploads/images/ee59c65028f097259ccd1dd9181473c782572a42.jpg)

JAVA反射机制
--------

### 使用JAVA反射机制调用FileOutputStream类写文件

调用FileOutputStream类写文件时，常用的代码如下：

```
FileOutputStream fos = new FileOutputStream("1.txt");
fos.write("abc".getBytes());

```

若需要使用JAVA反射机制调用FileOutputStream类写文件，且只允许调用Class.getMethod与Method.invoke方法，上述代码需修改为如下形式。

![](http://drops.javaweb.org/uploads/images/d3c1cc420b4f2e1adf8300e7c5a23e53dbb6bf33.jpg)

### 使用JAVA反射机制调用Runtime类执行程序

调用Runtime类执行程序时，常用的代码如下：

```
Runtime runtime = Runtime.getRuntime();
runtime.exec("calc");

```

若需要使用JAVA反射机制调用Runtime类执行程序件，且只允许调用Class.getMethod与Method.invoke方法，上述代码需修改为如下形式。

![](http://drops.javaweb.org/uploads/images/69963a688594b400e29658c583a589d623abf24d.jpg)

### JAVA反射机制与序列化

当需要操作无法直接访问的类时，需要使用JAVA的反射机制。即对无法直接访问的类进行序列化时，需要使用JAVA的反射机制。

以下测试代码为testReflection.TestReflection类，与前文中的test.MyObject类不在同一个包中，在TestReflection类中对MyObject类进行序列化时，需要使用JAVA的反射机制。

![](http://drops.javaweb.org/uploads/images/1cb21af16917c6539188b46fcbc40d20cbef5993.jpg)

以下为执行结果，可以看到使用JAVA的反射机制后，能够对无法直接访问的类进行序列化。

```
-before newInstance-  
MyObject(String name) tttest  
-after newInstance-  
byteOut.toByteArray().length:71  
MyObject-readObject!!!!!!!!!!!!!! tttest  
object:class test.MyObject  

-before newInstance-  
MyObject(String name) no name-default  
-after newInstance-  
byteOut.toByteArray().length:80  
MyObject-readObject!!!!!!!!!!!!!! no name-default  
object:class test.MyObject  

```

0x02 漏洞分析
=========

* * *

使用JAVA反序列化的场景
-------------

breenmachine在“What Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common This Vulnerability”中列出了以下会使用JAVA反序列化的场景。

> Java LOVES sending serialized objects all over the place. For example:
> 
> **In HTTP requests**– Parameters, ViewState, Cookies, you name it.  
> **RMI**– The extensively used Java RMI protocol is 100% based on serialization.  
> **RMI over HTTP**– Many Java thick client web apps use this – again 100% serialized objects.  
> **JMX**– Again, relies on serialized objects being shot over the wire.  
> **Custom Protocols**– Sending an receiving raw Java objects is the norm – which we’ll see in some of the exploits to come.

可能存在JAVA反序列化漏洞的场景
-----------------

JAVA中间件通常通过网络接收客户端发送的序列化数据，JAVA中间件在对序列化数据进行反序列化数据时，会调用被序列化对象的readObject方法。如果某个对象的readObject方法中能够执行任意代码，那么JAVA中间件在对其进行反序列化时，也会执行对应的代码。如果能够找到满足上述条件的对象进行序列化并发送给JAVA中间件，JAVA中间件也会执行指定的代码，即存在反序列化漏洞。

JAVA反序列化漏洞需要满足两个条件：

1.  JAVA中件间需要存在客户端进行序列化时使用的类，否则服务器在进行反序列化时会出现ClassNotFoundException异常；
2.  客户端选择的进行序列化的类在执行代码时，不会进行任何验证或限制，会完全按照要求执行。

利用JAVA反序列化漏洞可以使服务器执行任意代码，可以直接控制服务器，危害非常大。

Apache Commons Collections组件说明
------------------------------

下文中出现的以下类均包含在Apache Commons Collections组件中。

> org.apache.commons.collections.functors.ConstantTransformer  
> org.apache.commons.collections.functors.InvokerTransformer  
> org.apache.commons.collections.functors.ChainedTransformer  
> org.apache.commons.collections.map.TransformedMap  
> org.apache.commons.collections.map.AbstractInputCheckedMapDecorator  
> org.apache.commons.collections.map.AbstractMapDecorator  
> org.apache.commons.collections.set.AbstractSetDecorator  
> org.apache.commons.collections.collection.AbstractCollectionDecorator  
> org.apache.commons.collections.iterators.AbstractIteratorDecorator  
> org.apache.commons.collections.keyvalue.AbstractMapEntryDecorator

Apache Commons Collections组件原生的jar包为commons-collections-xxx.jar。

本文中分析的commons-collections-xxx.jar版本为3.2.1，JDK版本为1.6。

通过对commons-collections-xxx.jar中涉及的代码进行反编译，增加输出或进行调试，可以跟踪漏洞触发时的代码执行情况。

利用ChainedTransformer执行代码
------------------------

### ConstantTransformer类的transform方法

org.apache.commons.collections.functors.ConstantTransformer类的transform方法会返回构造函数传入的参数。ConstantTransformer类相关代码如下。

```
public class ConstantTransformer implements Transformer, Serializable {

    private final Object iConstant;

    public ConstantTransformer(Object constantToReturn) {
        this.iConstant = constantToReturn;
    }

    public Object transform(Object input) {
        return this.iConstant;
    }
    ...
}

```

### InvokerTransformer类的transform方法

org.apache.commons.collections.functors.InvokerTransformer类的transform方法可以通过JAVA反射机制执行指定的代码，能指定所需执行的类、方法及参数，且在transform方法中未进行任何验证或限制。transform方法中执行的代码的方法名、参数类型及参数值在InvokerTransformer类的构造函数中指定。InvokerTransformer类相关代码如下。

```
public class InvokerTransformer implements Transformer, Serializable {

    private final String iMethodName;
    private final Class[] iParamTypes;
    private final Object[] iArgs;

    public InvokerTransformer(String methodName, Class[] paramTypes,
        Object[] args) {
        this.iMethodName = methodName;
        this.iParamTypes = paramTypes;
        this.iArgs = args;
    }       

    public Object transform(Object input) {
        if (input == null)
            return null;
        try {
            Class cls = input.getClass();
            Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
            return method.invoke(input, this.iArgs);
        }
        ...
    }
}

```

### 利用ChainedTransformer执行代码分析

以下为利用org.apache.commons.collections.functors.ChainedTransformer类执行任意代码的示例，当执行最后的“chain.transform(chain);”后，会执行传入的Transformer数组指定的代码。在该示例中，会启动计算器程序。

![](http://drops.javaweb.org/uploads/images/76972dce670a0865645f280bd03078a02ce2e7b9.jpg)

ConstantTransformer与InvokerTransformer数组可被转换为org.apache.commons.collections.functors.ChainedTransformer对象。在ChainedTransformer类的带参数构造函数中，会将参数中的ConstantTransformer与InvokerTransformer数组保存为this.iTransformers对象。在ChainedTransformer类的transform方法中，会依次调用this.iTransformers对应的ConstantTransformer与InvokerTransformer数组的transform方法，且前一次执行transform方法的返回值object，会作为下一次执行transform方法的参数object。ChainedTransformer类的相关代码如下。

```
public class ChainedTransformer implements Transformer, Serializable {

    public ChainedTransformer(Transformer[] transformers) {
        this.iTransformers = transformers;
    }
    ...
    public Object transform(Object object) {
        for (int i = 0; i < this.iTransformers.length; ++i) {
            object = this.iTransformers[i].transform(object);
        }
        return object;
    }
    ...
}

```

对于上述的示例代码，在执行最后的“chain.transform(chain);”方法时，会首先调用ConstantTransformer.transform方法获取其构造函数中传入的类，再依次调用InvokerTransformer.transform方法执行其构造函数中传入的方法，等价于下面的代码。

![](http://drops.javaweb.org/uploads/images/90d59f04461fbb880bb56bc0e5f62a44daaaa090.jpg)

上述代码与前文“使用JAVA反射机制调用Runtime类执行程序”中的代码相同，已经过验证可以成功执行，能够调用指定的程序。ChainedTransformer也能够调用FileOutputStream类进行写文件操作，相关代码见前文“使用JAVA反射机制调用FileOutputStream类写文件”部分。由此可见，利用ChainedTransformer类能够执行指定的代码。

利用TransformedMap类执行代码
---------------------

以下为通过org.apache.commons.collections.map.TransformedMap类执行任意代码的示例，当执行最后的“localEntry.setValue(null);”后，会执行传入的Transformer数组指定的代码。在该示例中，会启动计算器程序。

![](http://drops.javaweb.org/uploads/images/e96a3d535e9643e5f203fcd680eefa501af561b4.jpg)

### 涉及的变量及类型

上述示例代码中涉及的变量及类型如下。

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">变量</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">类型</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">outerMap</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">org.apache.commons.collections.map.TransformedMap</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">set</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">org.apache.commons.collections.map.AbstractInputCheckedMapDecorator$EntrySet</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">localIterator</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">org.apache.commons.collections.map.AbstractInputCheckedMapDecorator$EntrySetIterator</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">localEntry</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">org.apache.commons.collections.map.AbstractInputCheckedMapDecorator$MapEntry</td></tr></tbody></table>

org.apache.commons.collections.map.TransformedMap类直接继承自org.apache.commons.collections.map.AbstractInputCheckedMapDecorator类，间接继承自java.util.Map类。org.apache.commons.collections.map.TransformedMap类的继承关系如下。

```
org.apache.commons.collections.map.TransformedMap  
 └org.apache.commons.collections.map.AbstractInputCheckedMapDecorator  
  └org.apache.commons.collections.map.AbstractMapDecorator  
   └java.util.Map

```

### 调用TransformedMap类的decorate方法

上述示例中第33行代码TransformedMap.decorate调用了TransformedMap类的decorate方法。TransformedMap类的decorate方法中创建了TransformedMap对象，以调用decorate方法的参数一map作为参数调用了父类AbstractInputCheckedMapDecorator的构造函数，并将调用decorate方法的参数三valueTransformer保存为this.valueTransformer变量。TransformedMap类相关代码如下。

```
public class TransformedMap extends AbstractInputCheckedMapDecorator implements     Serializable {

    protected final Transformer keyTransformer;
    protected final Transformer valueTransformer;

    public static Map decorate(Map map, Transformer keyTransformer,
            Transformer valueTransformer) {
        return new TransformedMap(map, keyTransformer, valueTransformer);
    }

    protected TransformedMap(Map map, Transformer keyTransformer,
            Transformer valueTransformer) {
        super(map);
        this.keyTransformer = keyTransformer;
        this.valueTransformer = valueTransformer;
    }
    ...
}

```

在TransformedMap类的父类AbstractInputCheckedMapDecorator的构造函数中，以自身类构造函数的参数为参数调用了父类的构造函数。AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {
    protected AbstractInputCheckedMapDecorator(Map map) {
        super(map);
    }
    ...
}

```

在AbstractInputCheckedMapDecorator类的父类AbstractMapDecorator的构造函数中，将构造函数的参数保存为this.map对象。AbstractMapDecorator类相关代码如下。

```
public abstract class AbstractMapDecorator implements Map {
    protected transient Map map;

    public AbstractMapDecorator(Map map) {
        if (map == null) {
            throw new IllegalArgumentException("Map must not be null");
        }
        this.map = map;
    }
    ...
}

```

可以看出，上述示例代码中，第33行代码调用TransformedMap类的decorate方法时，参数一innerMap被保存为生成的TransformedMap对象的map变量，参数三chain被保存为valueTransformer变量。

### 调用AbstractInputCheckedMapDecorator类的entrySet方法

上述示例中第35行代码outerMap.entrySet调用了TransformedMap类的父类AbstractInputCheckedMapDecorator的entrySet方法。AbstractInputCheckedMapDecorator类为抽象类，在其entrySet方法中，创建了EntrySet类的对象并返回。在调用EntrySet类的构造函数时，参数二为this，由于AbstractInputCheckedMapDecorator类为抽象类。在上述示例代码执行时，参数二this即为TransformedMap类的对象outerMap。

EntrySet类为AbstractInputCheckedMapDecorator类的内部类，在其构造函数中，会将参数二保存为this.parent变量。在上述示例代码执行时，TransformedMap类的对象outerMap会被保存为EntrySet类的this.parent变量。

AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {
    protected boolean isSetValueChecking() {
        return true;
    }

    public Set entrySet() {
        if (isSetValueChecking()) {
            return new EntrySet(this.map.entrySet(), this);
        }
        return this.map.entrySet();
    }
    ...

    static class EntrySet extends AbstractSetDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        protected EntrySet(Set set, AbstractInputCheckedMapDecorator parent) {
            super(set);
            this.parent = parent;
        }
        ...
    }
}

```

### 调用AbstractInputCheckedMapDecorator$EntrySet类的iterator方法

上述示例代码中第37行代码set.iterator调用了AbstractInputCheckedMapDecorator$EntrySet类的iterator方法。在EntrySet类的iterator方法中，创建了AbstractInputCheckedMapDecorator$EntrySetIterator类的对象并返回，在调用EntrySetIterator类的构造函数时，参数二为this.parent。在上述示例代码中，this.parent即为TransformedMap类的对象outerMap。

EntrySetIterator类为AbstractInputCheckedMapDecorator类的内部类，在其构造函数中，会将参数二保存为this.parent变量。在上述示例代码执行时，TransformedMap类的对象outerMap会被保存为EntrySetIterator类的this.parent变量。

AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {  
    static class EntrySet extends AbstractSetDecorator {
        private final AbstractInputCheckedMapDecorator parent;  

        public Iterator iterator() {
            return new AbstractInputCheckedMapDecorator.EntrySetIterator(
                    this.collection.iterator(), this.parent);
        }
        ...
    }

    static class EntrySetIterator extends AbstractIteratorDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        protected EntrySetIterator(Iterator iterator,
                AbstractInputCheckedMapDecorator parent) {
            super(iterator);
            this.parent = parent;
        }
        ...
    }
    ...
}

```

### 调用AbstractInputCheckedMapDecorator$EntrySetIterator类的next方法

上述示例代码中第39行代码localIterator.next调用了AbstractInputCheckedMapDecorator$EntrySetIterator类的next方法。在EntrySetIterator类的next方法中，创建了AbstractInputCheckedMapDecorator$MapEntry类的对象并返回，在调用MapEntry类的构造函数时，参数二为this.parent。在上述示例代码中，this.parent即为TransformedMap类的对象outerMap。

MapEntry类为AbstractInputCheckedMapDecorator类的内部类，在其构造函数中，会将参数二保存为this.parent变量。在上述示例代码执行时，TransformedMap类的对象outerMap会被保存为MapEntry类的this.parent变量。

AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {  

    static class EntrySetIterator extends AbstractIteratorDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        public Object next() {
            Map.Entry entry = (Map.Entry) this.iterator.next();
            return new AbstractInputCheckedMapDecorator.MapEntry(entry,
                    this.parent);
        }
        ...
    }
    ...
    static class MapEntry extends AbstractMapEntryDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        protected MapEntry(Map.Entry entry,
                AbstractInputCheckedMapDecorator parent) {
            super(entry);
            this.parent = parent;
        }
        ...
    }
}

```

### 调用AbstractInputCheckedMapDecorator$MapEntry类的setValue方法

上述示例代码中第43行代码localEntry.setValue调用了AbstractInputCheckedMapDecorator$MapEntry类的setValue方法。在MapEntry类的setValue方法中，调用了this.parent的checkSetValue方法。在上述示例代码中，MapEntry类的this.parent即为TransformedMap类的对象outerMap，因此会调用TransformedMap类的checkSetValue方法。AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {  
    static class MapEntry extends AbstractMapEntryDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        public Object setValue(Object value) {
            value = this.parent.checkSetValue(value);
            return this.entry.setValue(value);
        }
        ...
    }
}

```

在TransformedMap类的checkSetValue方法中，会调用this.valueTransformer.transform方法。在前文的示例代码中，TransformedMap类的对象outerMap的this.valueTransformer变量对应ChainedTransformer类对象chain。前文“利用ChainedTransformer执行代码分析”部分已经说明，调用ChainedTransformer类的transform方法时，会执行其在构造时传入的ConstantTransformer与InvokerTransformer数组中指定的方法。TransformedMap类相关代码如下。

```
public class TransformedMap extends AbstractInputCheckedMapDecorator implements
    Serializable {
    protected Object checkSetValue(Object value) {
        return this.valueTransformer.transform(value);
    }
    ...
}

```

**综上所述，上述示例代码最后的“localEntry.setValue(null);”时，会执行ConstantTransformer与InvokerTransformer数组指定的方法。**

### 漏洞触发时的调用过程

上述漏洞在触发时的完整调用过程如下。

```
//调用TransformedMap类的decorate方法  
TransformedMap.decorate  
AbstractMapDecorator.AbstractMapDecorator  
AbstractInputCheckedMapDecorator.AbstractInputCheckedMapDecorator  
TransformedMap.TransformedMap  

//调用AbstractInputCheckedMapDecorator类的entrySet方法  
AbstractInputCheckedMapDecorator.entrySet  
TransformedMap.isSetValueChecking  
AbstractInputCheckedMapDecorator$EntrySet.EntrySet  

//调用AbstractInputCheckedMapDecorator$EntrySet类的iterator方法  
AbstractInputCheckedMapDecorator$EntrySet.iterator  
AbstractInputCheckedMapDecorator$EntrySetIterator.EntrySetIterator  

//调用AbstractInputCheckedMapDecorator$EntrySetIterator类的next方法  
AbstractInputCheckedMapDecorator$EntrySetIterator.next  
AbstractMapEntryDecorator.AbstractMapEntryDecorator  
AbstractInputCheckedMapDecorator$MapEntry.MapEntry  

//调用AbstractInputCheckedMapDecorator$MapEntry类的setValue方法  
AbstractInputCheckedMapDecorator$MapEntry.setValue  
TransformedMap.checkSetValue  
ChainedTransformer.transform  
InvokerTransformer.transform

```

### AbstractInputCheckedMapDecorator$MapEntry对象的键值对

在确定了利用TransformedMap类可以执行代码以后，再来关注上述示例代码中调用最后的“localEntry.setValue”之前的localEntry的键值对。之所以需要关注localEntry的键值对，是因为在通过AnnotationInvocationHandler类执行代码时，这是一个重要的变量。

从上述示例代码第35行“outerMap.entrySet”开始分析，之前的步骤不再重复。

上述示例中第35行代码outerMap.entrySet调用了TransformedMap类的父类AbstractInputCheckedMapDecorator的entrySet方法。在AbstractInputCheckedMapDecorator类的entrySet方法中，创建了EntrySet类的对象并返回。在调用EntrySet类的构造函数时，参数一为this.map.entrySet()。在上述示例代码中，AbstractInputCheckedMapDecorator类的this.map.entrySet()对应Map对象innerMap的entrySet()。

在AbstractInputCheckedMapDecorator$EntrySet类的构造函数中，会将参数一set作为参数调用父类org.apache.commons.collections.set.AbstractSetDecorator的构造函数。

AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {
    protected boolean isSetValueChecking() {
        return true;
    }

    public Set entrySet() {
        if (isSetValueChecking()) {
            return new EntrySet(this.map.entrySet(), this);
        }
        return this.map.entrySet();
    }
    ...

    static class EntrySet extends AbstractSetDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        protected EntrySet(Set set, AbstractInputCheckedMapDecorator parent) {
            super(set);
            this.parent = parent;
        }
        ...
    }
}

```

在AbstractSetDecorator类的构造函数中，会将参数一set作为参数调用父类org.apache.commons.collections.collection.AbstractCollectionDecorator的构造函数。

AbstractSetDecorator类相关代码如下。

```
public abstract class AbstractSetDecorator extends AbstractCollectionDecorator
        implements Set {
    protected AbstractSetDecorator(Set set) {
        super(set);
    }
    ...
}

```

在AbstractCollectionDecorator类的构造函数中，会将参数一coll保存为this.collection变量，即AbstractCollectionDecorator类的this.collection变量保存了示例代码中Map对象innerMap的entrySet()。

AbstractCollectionDecorator类相关代码如下。

```
public abstract class AbstractCollectionDecorator implements Collection {
    protected Collection collection;

    protected AbstractCollectionDecorator(Collection coll) {
        if (coll == null) {
            throw new IllegalArgumentException("Collection must not be null");
        }
        this.collection = coll;
    }
    ...
}

```

上述示例代码中第37行代码set.iterator调用了AbstractInputCheckedMapDecorator$EntrySet类的iterator方法。在EntrySet类的iterator方法中，创建了AbstractInputCheckedMapDecorator$EntrySetIterator类的对象并返回，在调用EntrySetIterator类的构造函数时，参数一为this.collection.iterator()。在上述示例代码中，this.collection.iterator()即为Map对象innerMap的entrySet().iterator()。

在AbstractInputCheckedMapDecorator$EntrySetIterator类的构造函数中，会将参数一iterator作为参数调用父类org.apache.commons.collections.iterators.AbstractIteratorDecorator的构造函数。

AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {  
    static class EntrySet extends AbstractSetDecorator {
        private final AbstractInputCheckedMapDecorator parent;  

        public Iterator iterator() {
            return new AbstractInputCheckedMapDecorator.EntrySetIterator(
                    this.collection.iterator(), this.parent);
        }
        ...
    }

    static class EntrySetIterator extends AbstractIteratorDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        protected EntrySetIterator(Iterator iterator,
                AbstractInputCheckedMapDecorator parent) {
            super(iterator);
            this.parent = parent;
        }
        ...
    }
    ...
}

```

在AbstractIteratorDecorator类的构造函数中，会将参数一iterator保存为this.iterator变量，即AbstractIteratorDecorator类的this.iterator变量保存了示例代码中Map对象innerMap的entrySet().iterator()。

AbstractIteratorDecorator类相关代码如下。

```
public class AbstractIteratorDecorator implements Iterator {
    protected final Iterator iterator;

    public AbstractIteratorDecorator(Iterator iterator) {
        if (iterator == null) {
            throw new IllegalArgumentException("Iterator must not be null");
        }
        this.iterator = iterator;
    }
    ...
}

```

上述示例代码中第39行代码localIterator.next调用了AbstractInputCheckedMapDecorator$EntrySetIterator类的next方法。在EntrySetIterator类的next方法中，创建了AbstractInputCheckedMapDecorator$MapEntry类的对象并返回，在调用MapEntry类的构造函数时，参数一为this.iterator.next()。在上述示例代码中，this.iterator.next()即为Map对象innerMap的entrySet().iterator().next()，即示例代码中第30行通过innerMap.put添加的键值对。

在AbstractInputCheckedMapDecorator$EntrySet类的构造函数中，会将参数一entry作为参数调用父类org.apache.commons.collections.keyvalue.AbstractMapEntryDecorator的构造函数。

AbstractInputCheckedMapDecorator类相关代码如下。

```
abstract class AbstractInputCheckedMapDecorator extends AbstractMapDecorator {  

    static class EntrySetIterator extends AbstractIteratorDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        public Object next() {
            Map.Entry entry = (Map.Entry) this.iterator.next();
            return new AbstractInputCheckedMapDecorator.MapEntry(entry,
                    this.parent);
        }
        ...
    }
    ...
    static class MapEntry extends AbstractMapEntryDecorator {
        private final AbstractInputCheckedMapDecorator parent;

        protected MapEntry(Map.Entry entry,
                AbstractInputCheckedMapDecorator parent) {
            super(entry);
            this.parent = parent;
        }
        ...
    }
}

```

在AbstractMapEntryDecorator类的构造函数中，会将参数一entry保存为this.entry变量，在getKey与getValue方法会分别返回this.entry.getKey()与this.entry.getValue()。

AbstractMapEntryDecorator类相关代码如下。

```
public abstract class AbstractMapEntryDecorator implements Map.Entry, KeyValue {
    protected final Map.Entry entry;

    public AbstractMapEntryDecorator(Map.Entry entry) {
        if (entry == null) {
            throw new IllegalArgumentException("Map Entry must not be null");
        }
        this.entry = entry;
    }

    public Object getKey() {
        return this.entry.getKey();
    }

    public Object getValue() {
        return this.entry.getValue();
    }
    ...
}

```

**综上所述，在示例代码中执行第39行localIterator.next后，执行localEntry.getKey()与localEntry.getValue()可获取示例代码中第30行通过innerMap.put添加的键值对。**

利用TransformedMap与AnnotationInvocationHandler类执行代码
-------------------------------------------------

已知TransformedMap类为Map类的子类，为了触发JAVA反序列化漏洞，需要找到某个类提供了方法接收Map对象，且在readObject方法中会调用Map对象的Entry的setValue方法。

sun.reflect.annotation.AnnotationInvocationHandler类满足上述的要求。sun.reflect.annotation.AnnotationInvocationHandler类为JRE中原生的类，不需要第三方支持。

以下为通过TransformedMap与AnnotationInvocationHandler类执行任意代码的示例，当执行第57行的“ois.readObject();”后，会执行传入的Transformer数组指定的代码。在该示例中，会启动计算器程序。

![](http://drops.javaweb.org/uploads/images/36a25b4381a08c6b935301b0ab7a438da959ead5.jpg)

sun.reflect.annotation.AnnotationInvocationHandler类无法直接访问，因此在构造需要序列化的对象时，需要使用JAVA反射机制。

在上述触发漏洞的示例代码中，会调用AnnotationInvocationHandler类的带参数构造函数与反序列化时会被调用的readObject函数。

AnnotationInvocationHandler类的重要的变量及方法如下。

```
1.  class AnnotationInvocationHandler implements InvocationHandler, Serializable {
2.      private final Class type;
3.      private final Map<String, ObjectmemberValues;
4.      ...
5.
6.      AnnotationInvocationHandler(Class paramClass, Map<String, ObjectparamMap) {
7.          this.type = paramClass;
8.          this.memberValues = paramMap;
9.      }
10.     ...
11.
12.     private void readObject(ObjectInputStream paramObjectInputStream)
13.             throws IOException, ClassNotFoundException {
14.         paramObjectInputStream.defaultReadObject();
15.         AnnotationType localAnnotationType = null;
16.         try {
17.             localAnnotationType = AnnotationType.getInstance(this.type);
18.         } catch (IllegalArgumentException localIllegalArgumentException) {
19.             return;
20.         }
21.         Map localMap = localAnnotationType.memberTypes();
22.         Iterator localIterator = this.memberValues.entrySet().iterator();
23.         while (localIterator.hasNext()) {
24.             Map.Entry localEntry = (Map.Entry) localIterator.next();
25.             String str = (String) localEntry.getKey();
26.             Class localClass = (Class) localMap.get(str);
27.             if (localClass != null) {
28.                 Object localObject = localEntry.getValue();
29.                 if ((!(localClass.isInstance(localObject)))
30.                         && (!(localObject instanceof ExceptionProxy)))
31.                     localEntry.setValue(new AnnotationTypeMismatchExceptionProxy(
32.                                     localObject.getClass() + "[" + localObject
33.                                             + "]")
34.                                     .setMember((Method) localAnnotationType
35.                                             .members().get(str)));
36.             }
37.         }
38.     }

```

示例代码中第43行执行newInstance方法时，对应AnnotationInvocationHandler类代码的第6行的带参数构造方法。示例代码中第43行执行newInstance方法构造AnnotationInvocationHandler对象时，参数一为java.lang.annotation.Retention.class，参数二为TransformedMap类的对象outerMap。因此AnnotationInvocationHandler类代码中构造函数中保存的this.type对应java.lang.annotation.Retention.class，this.memberValues对应示例代码中的outerMap。

当AnnotationInvocationHandler类的readObject方法执行时，过程如下。

*   第17行代码中的this.type为java.lang.annotation.Retention.class。
    
*   第21行代码的localMap变量存在一个键值对，key为字符串"value"，value为class"java.lang.annotation.RetentionPolicy"。
    
*   第22行代码的this.memberValues对应示例代码中TransformedMap类的对象outerMap
    
*   第24行代码的localEntry等价于outerMap.entrySet().iterator().next()，根据前文“AbstractInputCheckedMapDecorator$MapEntry对象的键值对”部分的分析结果，localEntry对应示例代码中Map对象innerMap的entrySet().iterator().next()，即示例代码中第34行通过innerMap.put添加的键值对。
    
*   第25行代码的str等于示例代码中第34行通过innerMap.put添加的键值对的key，即字符串"value"。
    
*   第26行代码的localClass等于localMap变量中的键值对的value，即class"java.lang.annotation.RetentionPolicy"。
    
*   第27行代码的判断，需要localClass非空，满足该条件。
    
*   第28行代码的localObject等于示例代码中第34行通过innerMap.put添加的键值对的value，即字符串"tttest"。
    
*   第29行代码的判断，需要localObject不是localClass的实例，localObject为String对象，localClass为class"java.lang.annotation.RetentionPolicy"，满足该条件。
    
*   第30行代码的判断，需要localObject不是sun.reflect.annotation.ExceptionProxy的实例，localObject为String对象，满足该条件。
    
*   第31行代码调用了localEntry变量的setValue方法，localEntry为AbstractInputCheckedMapDecorator$MapEntry类的实例，根据前文”调用AbstractInputCheckedMapDecorator$MapEntry类的setValue方法“部分的分析，在调用AbstractInputCheckedMapDecorator$MapEntry类的setValue方法时，会执行ConstantTransformer与InvokerTransformer数组指定的方法，此时漏洞触发。
    

**综上所述，在利用TransformedMap与AnnotationInvocationHandler类触发JAVA反序列化漏洞时，有以下几点应满足条件。**

*   调用AnnotationInvocationHandler类的构造函数时，参数一应为java.lang.annotation.Retention.class；
*   在对TransformedMap.decorate的参数一Map对象使用put设置键值对时，key应为字符串"value"；value不能为空，否则会出现空指针异常。value可设为非java.lang.annotation.RetentionPolicy或sun.reflect.annotation.ExceptionProxy类的对象，如String，Integer对象的任意值等；

利用TransformedMap与AnnotationInvocationHandler类触发JAVA反序列化漏洞
---------------------------------------------------------

综合前文的分析，利用TransformedMap与AnnotationInvocationHandler类触发JAVA反序列化漏洞的大致步骤如下。

*   通过ConstantTransformer与InvokerTransformer数组指定需要执行的代码；
*   将ConstantTransformer与InvokerTransformer数组转换为ChainedTransformer对象；
*   通过TransformedMap类的decorate方法创建数组，参数中需要设置上一步产生的ChainedTransformer对象；
*   使用JAVA反射机制创建AnnotationInvocationHandler类的对象，在构造函数中指定上一步创建的数组；
*   对AnnotationInvocationHandler对象进行序列化后，将序列化的数据发送给JAVA中间件；
*   JAVA中间件在对序列化的AnnotationInvocationHandler类的对象数据进行反序列化时，会调用其readObject方法并触发漏洞，执行ConstantTransformer与InvokerTransformer数组指定需要执行的代码。

简而言之，当攻击者将构造好的包含攻击代码序列化数据发送给使用了Apache Commons Collections组件的JAVA中间件时，JAVA中间件在对其进行反序列化操作时，会触发反序列化漏洞，执行攻击者指定的任意代码。

不同JAVA中间件的JAVA反序列化漏洞利用与防护分析，之后再继续。

参考资料
====

<table style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">What Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common This Vulnerability</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">common-collections中Java反序列化漏洞导致的RCE原理分析 WooYun知识库</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://drops.wooyun.org/papers/10467</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Commons Collections Java反序列化漏洞深入分析 - 博客 - 腾讯安全应急响应中心</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://security.tencent.com/index.php/blog/msg/97</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">JAVA Apache-CommonsCollections 序列化漏洞分析以及漏洞高级利用 随风'S Blog</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.iswin.org/2015/11/13/Apache-CommonsCollections-Deserialized-Vulnerability/</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Java反序列化漏洞技术分析 天融信阿尔法实验室</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://blog.topsec.com.cn/ad_lab/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E6%8A%80%E6%9C%AF%E5%88%86%E6%9E%90/</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Java反序列化漏洞之Weblogic、Jboss利用教程及exp - HereSecurity</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.heresec.com/index.php/archives/127/</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Java反序列化漏洞之weblogic本地利用实现篇 - FreeBuf_COM 关注黑客与极客</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.freebuf.com/vuls/90802.html</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">Lib之过？Java反序列化漏洞通用利用分析 - Cnlouds的个人空间 - 开源中国社区</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://my.oschina.net/u/1188877/blog/529611</td></tr><tr style="box-sizing: border-box;"><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">WebLogic之Java反序列化漏洞利用实现二进制文件上传和命令执行 WooYun知识库</td><td style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://drops.wooyun.org/papers/11690</td></tr></tbody></table>