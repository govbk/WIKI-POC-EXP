# Spring MVC xml绑定pojo造成的XXE

0x00 背景
-------

* * *

什么是XXE ? 就是我们所说的所谓xml实体注入.这里不去讲所有xml语法规范了,稍微就说一下XML entity:

```
entity翻译为"实体"。它的作用类似word中的"宏"，也可以理解为DW中的模板，你可以预先定义一个entity，然后在一个文档中多次调用，或者在多个文档中调用同一个entity(XML定义了两种类型的entity。一种是我们这里说的普通entity，在XML文档中使用；另一种是参数entity，在DTD文件中使用。)。  

```

entity的定义语法为:

```
<!DOCTYPE filename
[  
    <!ENTITY entity-name "entity-content"  
]>

```

如果要引用一个外部资源:

```
<!DOCTYPE test
[  
    <!ENTITY test SYSTEM "http://xxx.xxx.com/test.xml">   
]> 

```

ENTITY可以使用SYSTEM关键字,调用外部资源,而这里是支持很多的协议,如:http;file等

然后,在其他DoM结点中可以使用如:`&test;`引用该实体内容.

那么,如果在产品功能设计当中,解析的xml是由外部可控制的,那将可能形成,如:文件读取,DoS,CSRF等漏洞.

这里只介绍文件读取漏洞,其他可以自己google了解.

0x01 原理
-------

* * *

规范没有问题,xml解析器有些也没有问题,有问题的是使用他的人.

java SAX解析器 demo:

Test.java

```
public static void main(String[] args) throws  Exception {   
    SAXReader reader = new SAXReader();  
    //禁止  
    //reader.setFeature("http://xml.org/sax/features/external-general-entities", true);  
    Document dom = reader.read("E:/1.xml");  
    Element root = dom.getRootElement();  
    Iterator<Element> it = root.elementIterator();  
    while (it.hasNext()) {  
        Element elements = it.next();  
        System.out.println(elements.getText());  

    }  
}  

```

解析的xml,1.xml:

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE test
[<!ELEMENT test ANY ><!ENTITY xxe SYSTEM "file:///E:/1.log" >]>
<root>
    <name>&amp;xxe;</name>
</root>

```

实体调用的资源，1.log：

```
XXE test!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

```

先说一点,解析器一般会支持所有xml规范的.使用file协议,理论上,我们至少可以读取到当前系统的任意文件内容.如:读取E盘符下的1.log文件内容.

然后被root的子节点,name内容域引用.解析结果,如图：

![2014050722403743880.png](http://drops.javaweb.org/uploads/images/34f54af0ffd2e0e61a4c0efecef39560a9b5554c.jpg)

接下来讲，spring MVC在xml格式到java对象反序列化中，可能存在的XXE 形成的文件读取：

spring 是提供xml请求内容绑定到pojo的功能（也可以理解成javabean什么的（有区别，可以自己去看看），spring  在这里规范化了，所以就跟着叫），用得比较多的还有表单绑定，json绑定。

spring mvc JAXB xml to pojo unMarshaller  demo:

spring-servlet.xml：

```
<?xml version="1.0" encoding="UTF-8"?>  
<beans xmlns="http://www.springframework.org/schema/beans"  
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
 xmlns:p="http://www.springframework.org/schema/p"  
 xmlns:context="http://www.springframework.org/schema/context"  
 xsi:schemaLocation="http://www.springframework.org/schema/beans  
  http://www.springframework.org/schema/beans/spring-beans-3.0.xsd  
  http://www.springframework.org/schema/context  
  http://www.springframework.org/schema/context/spring-context-3.0.xsd">  
    
 <context:component-scan base-package="net.spring.controller" />   
   
   
    <bean class="org.springframework.web.servlet.mvc.annotation.AnnotationMethodHandlerAdapter">  
        <property name="messageConverters">  
            <list>  
                <ref bean="stringHttpMessageConverter" />  
                <ref bean="jsonHttpMessageConverter" />  
                <ref bean="marshallingHttpMessageConverter" />  
            </list>  
        </property>  
    </bean>  
<bean id="stringHttpMessageConverter" class="org.springframework.http.converter.StringHttpMessageConverter" />   
<bean id="jsonHttpMessageConverter" class="org.springframework.http.converter.json.MappingJacksonHttpMessageConverter" />  
<bean id="marshallingHttpMessageConverter" class="org.springframework.http.converter.xml.MarshallingHttpMessageConverter">  
        <constructor-arg ref="jaxbMarshaller" />  
        <property name="supportedMediaTypes" value="application/xml"></property>  
</bean>  
<bean id="jaxbMarshaller" class="org.springframework.oxm.jaxb.Jaxb2Marshaller">  
        <property name="classesToBeBound">  
            <list>  
                <value>net.spring.controller.User</value>  
            </list>  
        </property>  
</bean>  
</beans>  

```

HelloWorldController.java：

```
import org.springframework.stereotype.Controller;  
import org.springframework.web.bind.annotation.RequestBody;  
import org.springframework.web.bind.annotation.RequestMapping;  
import org.springframework.web.servlet.ModelAndView;  

@Controller  
public class HelloWorldController {   
    @RequestMapping("/hello")  
    public  ModelAndView helloWorld(@RequestBody User user) {  

        System.out.println("xxxxxxxxxx"+user.getName());  
        return new ModelAndView("hello", "user", user);   
    }   
} 

```

User.java（xml绑定的pojo）：

```
import javax.xml.bind.annotation.XmlElement;  
import javax.xml.bind.annotation.XmlRootElement;  

@XmlRootElement(name="user")    
public class User {  
    private String name;  

    public String getName() {  
        return name;  
}  
@XmlElement  
    public void setName(String name) {  
        this.name = name;  
    }  
}   

```

发包，xml绑定pojo,如图:

![2014050723155955348.png](http://drops.javaweb.org/uploads/images/dd3253eddae309e442e98df78dda0f0d333f8276.jpg)

pojo User对象的name属性被污染，如图：

![2014050723180180429.png](http://drops.javaweb.org/uploads/images/d4928faa4d8794bcc3dc1934e8afce0ab9e2d990.jpg)

如果，攻击者最终能看到这个name值（直接显示到页面或存储到数据库再现实到页面什么的），就是文件读取漏洞了！

不管是其他语言或场景，原理就这么回事。

spring 早已经修补，这里主要给个漏洞场景，现在基本没什么危害吧？因为这个功能使用不常见，但走在前面的框架使用者肯定会使用这个功能，可能需要等个十年左右：

https://jira.spring.io/browse/SPR-10806

当然，还存在一个小而很有意思的问题，过一段时间的文章中可能会讲到。