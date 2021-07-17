# J2EE MVC模式框架中,表单数据绑定功能不安全实现在Tomcat下造成的DoS及RCE

0x00 背景
-------

* * *

当这个[《Struts2 Tomcat class.classLoader.resources.dirContext.docBase赋值造成的DoS及远程代码执行利用!》](http://drops.wooyun.org/papers/1377)在Tomcat下的利用出来以后,它其实秒杀的不是一个框架,而是所有表单数据绑定功能不安全实现的J2EE MVC模式框架(因为国内运营商共享协议的限制,远程代码执行漏洞在国内难以大规模实现.但DoS漏洞还是存在的!).

0x01 细节
-------

* * *

稍微列一下清单:

### Struts1框架: 

2013年已经停止更新了,所以不会有补丁,出于节操,报了一下官方,Struts2项目leader 波兰小胖子 Lukasz Lenar 是这样回复的:

![2014040921474585720.png](http://drops.javaweb.org/uploads/images/0e4e5974c7b8284264509964bac3bbb47c35db90.jpg)

如图:

![2014040922063313735.png](http://drops.javaweb.org/uploads/images/73b4898cd32594523dd8fa6f7e96c971e0f9b9ea.jpg)

### webWork框架:

struts2框架的前身,由于与struts2框架合并,所以不会有补丁!

![2014040922091186766.png](http://drops.javaweb.org/uploads/images/461c8c606fcae537fe65eb53ba76ceb0d0ebd079.jpg)

### Struts2框架:

前面文章已经介绍了(不过发现,到现在很多重要厂商都没修复!)

### Spring 框架:

已经在cve-2010-1622中,补丁对class.classLoader的限制.但利用从此可以简化!

还有就是,自己早年学习java时,写的简易框架,也可以打(只是表单填充需要多写一行代码手动调用填充,而其他常规框架是自动的)![40.gif](http://drops.javaweb.org/uploads/images/c021526ade1d231d309da05b9feedb31a41b8de9.jpg)

就以自己写的框架说明问题:

表单参数绑定功能是MVC模式的框架一项非常重要的功能,比如:

没有表单参数绑定功能的时代,我们填充javabean的属性都需要:

```
... 
dto.setUserName(request.getParameter("userName"));  
dto.setPassWord(request.getParameter("passWord"));  
.... 

```

框架表单参数绑定出现以后,就节约了很多硬编码(这是框架的主要作用之一!)

通常实现表单参数绑定需要用到Java的两个重要机制:

内省（introspector）与反射（reflection）

而Apache commons-beanutils组件就提供了javaBean的内省与反射操作简化API

哥的框架使用commons-beanutils,实现表单参数绑定的部分代码块:

```
... 
public static Object parseRequest(HttpServletRequest request, Object bean) throws ServletException, IOException {
        Enumeration enums = request.getParameterNames();
        while (enums.hasMoreElements()) {
            Object obj = enums.nextElement();
            try {
                Class cls = PropertyUtils.getPropertyType(bean, obj.toString());
                Object beanValue = ConvertUtils.convert(request.getParameter(obj.toString()), cls);
                HashMap map = new HashMap();
                BeanUtils.populate(bean, map);
                PropertyUtils.setProperty(bean, obj.toString(), beanValue);
            } catch (Exception e) {
                // e.printStackTrace();
            }
        }
        return bean;
    }
... 

```

这里不会框架的可以用servlet测试一下漏洞!

这里有一个重要的问题,就是为什么能访问到基类Object.class ?

看内省机制,内省是 Java 语言对 Bean 类属性、事件的一种缺省处理方法。例如类 A 中有属性 name, 那我们可以通过 getName,setName 来得到其值或者设置新的值。通过 getName/setName 来访问 name 属性，这就是默认的规则(*但是只要有 getter/setter 方法中的其中一个，那么 Java 的内省机制就会认为存在一个属性)。

本身就业务逻辑讲,访问javaBean的属性就够了,是不需要访问其他基类的Object.class,但是内省机制使用不当,就会造成这个问题.

问题非常简单,在内省机制获取javaBean属性的一个小细节,测试代码:

```
public class TestBean {

    private String id;
    private String name;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

}



public class Test {

    public static void main(String[] args) throws IntrospectionException,
            IllegalArgumentException, IllegalAccessException,
            InvocationTargetException {

        TestBean dto = new TestBean();

        BeanInfo bi = Introspector.getBeanInfo(dto.getClass());

        // BeanInfo bi = Introspector.getBeanInfo(dto.getClass(),Object.class);

        PropertyDescriptor[] props = bi.getPropertyDescriptors();
        for (int i = 0; i < props.length; i++) {
            System.out.println(props[i].getName());
        }
        BeanInfo bi = Introspector.getBeanInfo(dto.getClass());
    }

}

```

获取包括父类的所有属性,如图:

![2014040922595023935.png](http://drops.javaweb.org/uploads/images/124c50658b33668add83dcfa031696ca0dfd09f2.jpg)

如果不想获取父类的属性.可以使用

```
Introspector.getBeanInfo(dto.getClass(),Object.class);

```

其中第二个参数就是终止遍历到的父类(如:终止到基类Object),如图(这才是表单绑定实现正确的做法):

![2014040923033384924.png](http://drops.javaweb.org/uploads/images/82292d77ceaea4693c9cb99eb8b9eee525a4242f.jpg)

然后只要属性有set器,参数就会被填充,以及后面的Tomcat的一些属性被挂载到class.classLoader下等原因,然后Tomcat的属性被访问到并且赋值.然后才是发生上面的利用!

0x02 总结
-------

* * *

任何使用commons-beanutils组件或内省(及反射)不安全实现表单参数绑定功能的框架,都会受影响(当然,我这里只测试了Tomcat,其他web容器感兴趣的也可以测试一下利用思路!).

J2EE规范在现今使用极广了，但如果不是Struts2漏洞，或许很少有人关注Java安全，这点很是奇怪！

Author: Nebula, HelloWorld security team