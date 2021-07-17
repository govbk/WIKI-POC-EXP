# web服务器分层架构的资源文件映射安全以及在J2EE应用中的利用与危害

### 0x00 相关背景介绍

通常一些web应用我们会使用多个web服务器搭配使用，解决其中的一个web服务器的性能缺陷以及做均衡负载的优点和完成一些分层结构的安全策略等！

例如：Nginx+ Tomcat的分层结构（在下文中，我们也使用此例说明相关问题）

Nginx是一个高性能的 HTTP 和 反向代理 服务器 。

通常，我们是通过它来解决一些静态资源（如：图片、js及css等类型文件）访问处理。

Nginx详细介绍：[http://baike.baidu.com/view/926025.htm](http://baike.baidu.com/view/926025.htm)

Tomcat服务器是一个免费的开放源代码的j2ee Web 应用服务器。

其中，它有一个比较明显的性能缺陷，那就是在处理静态资源特别是图片类型的文件特别吃力。从而能与Nginx（Ningx在处理静态资源方面性能特别优秀） 成为好基友！ 

Tomcat详细介绍：[http://baike.baidu.com/view/10166.htm](http://baike.baidu.com/view/10166.htm)

### 0x01 成因

但正是由于这种处理方式或分层架构设计，如果对静态资源的目录或文件的映射配置不当，可能会引发一些的安全问题（特别是在j2ee应用中表现更为严重）！

例如：Tomcat的WEB-INF目录，每个j2ee的web应用部署文件默认包含这个目录。

WEB-INF介绍：[http://baike.baidu.com/view/1745468.htm](http://baike.baidu.com/view/1745468.htm)

通常情况我们是无法通过Tomcat去访问它的，Tomcat的安全规范略中，它是一个受保护的目录。

为什么受保护了？我们来看看，它里面有什么：

```
classes目录（包含该应用核心的java类编译后的class文件及部分配置文件）

lib目录（所用框架、插件或组件的架包）

web.xml（重要的配置文件，它是开启攻击的一把钥匙，后面会讲到它）

```

以及其他自定义目录之文件

所以，它是j2ee应用一个非常重要的目录！

如果Nginx在映射静态文件时，把WEB-INF目录映射进去，而又没有做Nginx的相关安全配置（或Nginx自身一些缺陷影响）。从而导致通过Nginx访问到Tomcat的WEB-INF目录（请注意这里，是通过Nginx，而不是Tomcat访问到的，因为上面已经说到，Tomcat是禁止访问这个目录的。）。

造成这一情况的一般原因：是由于Nginx访问（这里可以说是均衡负载访问配置问题）配置不当造成的。通常，我们只会让Nginx把这些访问后缀的URL交给Tomcat，而这些后缀与j2ee及开发框架（或自定义框架）有关，如下：

```
.jsp
.do
.action
.....等（或自定义后缀）

```

而其他大部分后缀类型的访问URL直接交给了Nginx处理的（包括：WEB-INF目录中一些比较重要的.xml和.class类型等，所以这里，如果你映射了整个根目录，还是可以通过Nginx的一些后缀访问配置，做些安全策略处理的！）

简单缺陷配置的两例，如图：

![http://drops.wooyun.org/wp-content/data1/www/htdocs/646/wydrops/1/wp-content/themes/GZai/kindeditor/attached/20130109/20130109201733_57189.png](http://drops.javaweb.org/uploads/images/c7399bb79e140d5867ee0a82cd710f2366038c5f.jpg)

或

![http://drops.wooyun.org/wp-content/data1/www/htdocs/646/wydrops/1/wp-content/themes/GZai/kindeditor/attached/20130109/20130109201809_84191.png](http://drops.javaweb.org/uploads/images/f60e1debde147f9320d9555001a5d67bd336f562.jpg)

访问效果，如图：

![http://drops.wooyun.org/wp-content/data1/www/htdocs/646/wydrops/1/wp-content/themes/GZai/kindeditor/attached/20130109/20130109201858_95774.png](http://drops.javaweb.org/uploads/images/05c69d0784f94169f2e51f8a8dfe433c97d1cb04.jpg)

### 0x02 攻击方式及危害

这种情况相信大家早已碰到过，但可能没有深入去关注过它，而且该问题还比较普遍存在一些大型站点应用中。由于j2ee应用一些自身特点，导致发生此情况时，它很容易受到攻击，如：

web.xml配置文件，它是j2ee配置部署应用的起点配置文件，如果能够先访问到它，我们可以再结合j2ee的xml路径配置特点，如图：

![http://drops.wooyun.org/wp-content/data1/www/htdocs/646/wydrops/1/wp-content/themes/GZai/kindeditor/attached/20130109/20130109205039_58514.jpg](http://drops.javaweb.org/uploads/images/b5a89519334651a2c07984a1758c236a6fae306f.jpg)

根据web.xml配置文件路径或通常开发时常用框架命名习惯，找到其他配置文件或类文件路径。

![http://drops.wooyun.org/wp-content/data1/www/htdocs/646/wydrops/1/wp-content/themes/GZai/kindeditor/attached/20130109/20130109205351_66223.jpg](http://drops.javaweb.org/uploads/images/c20011a0a4bdb6983fbe9af03c0124f2619a7215.jpg)

反编译类后，再根据关联类文件路径，找到其他类文件。

如此下来，我们就可以获得整个应用几乎的所有核心代码及应用架构的相关信息等。

然后，我们再根据j2ee应用分层结构的流程或路线，很容易查找到应用中的一些逻辑、sql注射、XSS等相关漏洞，如图（图可能画得有点问题，但主要是说明问题）：

![http://drops.wooyun.org/wp-content/data1/www/htdocs/646/wydrops/1/wp-content/themes/GZai/kindeditor/attached/20130109/20130109210244_41616.jpg](http://drops.javaweb.org/uploads/images/c96c6b274bb1ccae4257c2d1dd311441480df0eb.jpg)

而这个问题简单描述是：一个规范的私处如何在另一个规范中得到有效保护？所以这里并不是只有j2ee才会有此等危害，而是j2ee一些自身特点在此场景中的危害表现更为突出或明显！

### 0x03 实际案例

#### 1、查找其他相关安全问题，轻松渗透：

去哪儿任意文件读取（基本可重构该系统原工程）

[WooYun: 去哪儿任意文件读取（基本可重构该系统原工程）](http://www.wooyun.org/bugs/wooyun-2012-07329)

j2ee分层架构安全（注册乌云1周年庆祝集锦） -- 点我吧

[WooYun: j2ee分层架构安全（注册乌云1周年庆祝集锦） -- 点我吧](http://www.wooyun.org/bugs/wooyun-2012-013729)

#### 2、遍历一些大型站点的应用架构：

百度某应用beidou（北斗）架构遍历！

[WooYun: 百度某应用beidou（北斗）架构遍历！](http://www.wooyun.org/bugs/wooyun-2012-011730)("[WooYun: 百度某应用beidou（北斗）架构遍历！](http://www.wooyun.org/bugs/wooyun-2012-011730)")

这里，还有其他情况也可能造成这一类似的安全问题，但同样可以根据上面的思路去很容易攻击它：

1、开启了目录浏览，如：[WooYun: 乐视网众多web容器配置失误，导致核心应用架构及敏感信息暴露](http://www.wooyun.org/bugs/wooyun-2012-010635)

2、 外层web容器的一些解析漏洞，在此处可利用，如：[http://sebug.net/vuldb/ssvid-60439](http://sebug.net/vuldb/ssvid-60439)

### 0x04 修复方案

最好不要映射非静态文件目录或敏感目录。

或通过Nginx配置禁止访问一些敏感目录，如：j2ee应用的WEB-INF目录

```
location ~ ^/WEB-INF/* { deny all; }

```

或者至少禁止Nginx接收访问一些j2ee常用后缀文件的URL以减少危害，如：

```
.xml
.class

```

等文件类型

注意一些外层web服务器的相关配置！