# Spring ModelAndView 注入

## 1. 介绍

在代码审计时发现以下功能点，Checkmarx显示存在`Spring ModelView Injection`，是由`ModelAndView`中的参数可被用户控制导致。这个漏洞的历史还是比较久的，但之前没有碰到过，于是就自己搭建环境调试一番，动手学习一下利用方法。

源码如下：

```java
@RequestMapping("/menuitem")
public ModelAndView menuitem(HttpServletRequest req, HttpServletResponse req) {
 String url = this.getParam(req, "url");
 HttpSession session = req.getSession();
 session.setAttribute("menuitem.url",url);
 String nextUrl = "xxx" + url;
 return new ModelAndView(new RedirectView(nextUrl));
}
```

## 2. 实践

首先自己搭建一下测试环境，在本地用此代码Demo进行漏洞验证，Springframework版本为`5.0.0.RELEASE`。

```java
@Controller
public class ModelAndViewTest {

    @GetMapping("/menuitem")
    public ModelAndView menuitem(@RequestParam(value = "url")String url) {
        String nextUrl = url;
        return new ModelAndView(nextUrl);
    }
}
```

`ModelAndView`是Spring中的一个模型视图对象，作用是设置跳转的视图地址或把controller方法中处理的数据传到jsp页面。

`ModelAndView`有两种使用形式：

1. forward:/view
2. redirect:/view

若`ModelAndView(view)`中的`view`参数可被用户控制，可能导致文件被读取的问题。

若直接访问 `http://localhost:8089/WEB-INF/web.xml` ，返回404

![](media/202009/16013589092682.jpg)


而使用`ModelAndView`注入，访问 http://localhost:8089/menuitem?url=forward:/WEB-INF/web.xml ，就可以看到`web.xml`的内容

![](media/202009/16013589258943.jpg)


但是仅能读取web目录下的文件，不能读取系统其他文件。尝试读取web目录外的文件时产生如下报错：`Check that the corresponding file exists within your web application archive!`

![](media/202009/16013589333854.jpg)
![500_error](/2020/06/13/Spring_ModelAndView_Injection/500_error.png)

除了文件读取，当然也能进行一些权限认证的绕过，这需要考虑具体的代码场景，不一定通用。

不过实际项目代码中多了`RedirectView()`方法变成以下情形：

```java
@Controller
public class ModelAndViewTest {

    @GetMapping("/menuitem")
    public ModelAndView menuitem(@RequestParam(value = "url")String url) {
        String nextUrl = url;
        return new ModelAndView(new RedirectView(url));
    }
}
```

`RedirectView`会触发302跳转的结果，等效于使用`url=redirect:/WEB-INF/web.xml`

![](media/202009/16013589554305.jpg)

虽然存在`RedirectView`不能直接读取文件，但能利用302跳转这一特性，实现URL重定向

![](media/202009/16013589745565.jpg)


302跳转处回显了我们的输入，那么能进行CRLF注入吗？

答案是不能，Spring会将\r\n进行处理，转换成空格。在下图的请求中可以看到`%0d`和`%0a`被转换成`\x20`

![](media/202009/16013589883545.jpg)


## 3. 分析

`/spring-framework/spring-webmvc/src/main/java/org/springframework/web/servlet/view/UrlBasedViewResolver.java:468`


```java
protected View createView(String viewName, Locale locale) throws Exception {
    // If this resolver is not supposed to handle the given view,
    // return null to pass on to the next resolver in the chain.
    if (!canHandle(viewName, locale)) {
        return null;
    }
    // Check for special "redirect:" prefix.
    if (viewName.startsWith(REDIRECT_URL_PREFIX)) {
        String redirectUrl = viewName.substring(REDIRECT_URL_PREFIX.length());
        RedirectView view = new RedirectView(redirectUrl,
            isRedirectContextRelative(), isRedirectHttp10Compatible());
        String[] hosts = getRedirectHosts();
        if (hosts != null) {
            view.setHosts(hosts);
        }
        return applyLifecycleMethods(REDIRECT_URL_PREFIX, view);
    }
    // Check for special "forward:" prefix.
    if (viewName.startsWith(FORWARD_URL_PREFIX)) {
        String forwardUrl = viewName.substring(FORWARD_URL_PREFIX.length());
        InternalResourceView view = new InternalResourceView(forwardUrl);
        return applyLifecycleMethods(FORWARD_URL_PREFIX, view);
    }
    // Else fall back to superclass implementation: calling loadView.
    return super.createView(viewName, locale);
}
```

从代码中可以看到，存在三种`viewName`的处理方法：

1. 以`redirect:`为前缀
2. 以`forward:`为前缀
3. 没有前缀

### 3.1 以redirect为前缀

新建一个`RedirectView`对象，表现结果是根据视图名进行302跳转，返回包中的`Location`头为`redirectUrl`变量。

![](media/202009/16013590399805.jpg)


### 3.2 以forward为前缀

新建一个`InternalResourceView`对象，根据视图名到指定的位置获取视图模板

在spring的配置文件中，会存在如下的视图解析器配置


```java
<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">
    <property name="prefix" value="/"/>
</bean>
```

`InternalResourceView`对象会受到该视图解析器配置的影响。

`InternalResourceViewResolver`会把返回的视图名称都解析为`InternalResourceView`对象，`InternalResourceView`会把Controller处理器方法返回的模型属性都存放到对应的`request`属性中，然后通过`RequestDispatcher`在服务器端把请求forword重定向到目标URL。比如在`InternalResourceViewResolver`中定义了`prefix=/WEB-INF/`，`suffix=.jsp`，然后请求的Controller处理器方法返回的视图名称为`test`，那么这个时候`InternalResourceViewResolver`就会把`test`解析为一个`InternalResourceView`对象，先把返回的模型属性都存放到对应的`HttpServletRequest`属性中，然后利用`RequestDispatcher`在服务器端把请求forword到`/WEB-INF/test.jsp`。


```java
<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">  
    <property name="prefix" value="/WEB-INF/"/>  
    <property name="suffix" value=".jsp"></property>  
</bean>
```

`/spring-framework/spring-webmvc/src/main/java/org/springframework/web/servlet/view/UrlBasedViewResolver.java:549`


```java
protected AbstractUrlBasedView buildView(String viewName) throws Exception {
    Class<?> viewClass = getViewClass();
    Assert.state(viewClass != null, "No view class");

    AbstractUrlBasedView view = (AbstractUrlBasedView) BeanUtils.instantiateClass(viewClass);
    view.setUrl(getPrefix() + viewName + getSuffix());
    view.setAttributesMap(getAttributesMap());

    ...
```


`view.setUrl(getPrefix() + viewName + getSuffix())`会将前缀后缀拼接到`view`中，会导致可访问的文件有限（此时的前缀后缀是配置文件中的`prefix`和`suffix`，不是传入时的`forward:`）。

### 3.3 没有前缀

则调用`super.createView()`方法，等效于用户直接访问`viewName`。

`/spring-framework/spring-webmvc/src/main/java/org/springframework/web/servlet/view/AbstractCachingViewResolver.java:274`


```java
protected View createView(String viewName, Locale locale) throws Exception {
    return loadView(viewName, locale);
}
```

## 4\. 总结

`Spring ModelView Injection`有以下几种利用方式：

1. web目录下的文件读取，但存在一定的限制（`InternalResourceViewResolver`中前后缀的配置）
2. 权限认证绕过
3. 重定向

## 参考

[https://o2platform.files.wordpress.com/2011/07/ounce_springframework_vulnerabilities.pdf](https://o2platform.files.wordpress.com/2011/07/ounce_springframework_vulnerabilities.pdf)

[http://johnis.online/old/2018/09/18/spring-view-injection/](http://johnis.online/old/2018/09/18/spring-view-injection/)

来源：https://s31k31.github.io/2020/06/13/Spring_ModelAndView_Injection/