# 攻击JavaWeb应用[1]-JavaEE 基础

### 0x00 JavaEE 基础

* * *

JSP: 全名为java server page，其根本是一个简化的[Servlet](http://baike.baidu.com/view/25169.htm)。

Servlet：Servlet是一种服务器端的Java应用程序，可以生成动态的Web页面。

JavaEE: JavaEE是J2EE新的名称。改名目的是让大家清楚J2EE只是Java企业应用。

什么叫Jsp什么叫Java我真的非常让大家搞清楚！拜托别一上来就来一句：“前几天我搞了一个jsp的服务器，可难吭了。”。

请大家分清楚什么是jsp什么是JavaEE!Java平台结构图：

![20130703172818_61466.jpg](http://drops.javaweb.org/uploads/images/7365c357788a069bd2ab1d8626e0113363284db0.jpg)

可以看到Java平台非常的庞大，而开发者的分化为：

![20130703172846_40325.jpg](http://drops.javaweb.org/uploads/images/d4510f20e10edaa4c6a986c6bbaba4148a2089c7.jpg)

列举这两个图的原因就是让你知道你看到的JSP不过是冰山一角，Jsp技术不过是Java初级开发人员必备的技术而已。

我今天要讲的就是Java树的最下面的两层了，也是初级工程师需要掌握的东西。

Web请求与相应简要的流程：

![20130703173033_49603.gif](http://drops.javaweb.org/uploads/images/3c48cd87fa1bfc43423907eb9b8e06dd85c977b1.jpg)

这是一个典型的就是客户端发送一个HTTP请求到服务器端，服务器端接收到请求并处理、响应的一个过程。

如果请求的是JSP，tomcat会把我们的JSP编译成Servlet也就是一个普通的Java类。

其实JSP是Servlet的一种特殊形式，每个JSP页面就是一个Servlet实例。Servlet又是一个普通的Java类它编译后就是一个普通的class文件。

这是一个普通的jsp脚本页面，因为我只用JSP来作为展示层仅仅做了简单的后端数据的页面展示：

![20130703175439_28704.png](http://drops.javaweb.org/uploads/images/5a5198e1de086155b3b5876e901e41397db509b8.jpg)

上图可以非常清晰的看到通常的Jsp在项目中的地位并不如我们大多数人所想的那么重要，甚至是可有可无！因为我们完全可以用其他的东西来代替JSP作为前端展示层。 我们来看一下这个页面编译成class后是什么样子：

![20130703175626_72063.png](http://drops.javaweb.org/uploads/images/adb30de1360bc3a7d74a500d1fdc30c5b9063bfd.jpg)

你会发现你根本就看不懂这个class文件，因为这是字节码文件我们根本就没法看。通过我们的TOMCAT编译后他编程了一个Java类文件保存在Tomcat的work目录下。

文件目录：`C:\apache-tomcat-7.0.34\work\Catalina\localhost\你的项目名\org\apache\jsp`

![20130703175736_31874.png](http://drops.javaweb.org/uploads/images/fc1a04de94f85e4fb56f8587a1fde181415ff38f.jpg)

我们只要打开index_jsp.java或者用jd-gui（Java反编译工具）打开就行了：

![20130703175806_35537.png](http://drops.javaweb.org/uploads/images/91baee6c8170f030579301a7cad6992df4d683e8.jpg)

有人说这是Servlet吗？当然了。

![20130703175859_89447.png](http://drops.javaweb.org/uploads/images/18d808834f6a8c9926368c35034d030d2a3fda43.jpg)

继承HttpJspBase类，该类其实是个HttpServlet的子类(jasper是tomcat的jsp engine)。

Jsp有着比Servlet更加优越的展现，很多初学PHP的人恐怕很难把视图和逻辑分开吧。比如之前在写PHPSQL注入测试的DEMO：

![20130703175946_12770.png](http://drops.javaweb.org/uploads/images/3647b62764caa9da1735bd62e8c13c801f7b2634.jpg) 

这代码看起来似乎没有什么大的问题，也能正确的跑起来啊会有什么问题呢？原因很简单这属于典型的展现和业务逻辑没有分开！这和写得烂的Servlet差不多！

说了这么多，很多人会觉得Servlet很抽象。我们还是连创建一个Servlet吧：

![20130703180119_18901.png](http://drops.javaweb.org/uploads/images/ea709d111a67d3897b45a3716624c5125f576d04.jpg)

创建成功后会自动的往web.xml里面写入：

![20130703180159_14918.png](http://drops.javaweb.org/uploads/images/eb87fcdff7f023ebbed64a3409ff9bbe72fe5f47.jpg)

其实就是一个映射的URL和一个处理映射的类的路径。而我们自动生成的Java类精简后大致是这个样子：

![20130703180237_62390.png](http://drops.javaweb.org/uploads/images/4ce1d300a5e84a4d4c1c9f56113db218159cab05.jpg)

请求响应输出内容：

![20130703180312_90096.png](http://drops.javaweb.org/uploads/images/a7a5bf492be539b14f9254ce638360b8dd783b39.jpg)

熟悉PHP的大神们这里就不做解释了哦。了解了Jsp、Servlet我们再来非常简单的看一下JavaWeb应用是怎样跑起来的。

加载web.xml的配置然后从配置里面获取各种信息为WEB应用启动准备。

#### 科普：`C:\apache-tomcat-7.0.34\webapps`下默认是部署的Web项目。webapps 下的文件夹就是你的项目名了，而项目下的WebRoot一般就是网站的根目录了，WebRoot下的文件夹WEB-INF默认是不让Web访问的，一般存在配置泄漏多半是nginx配置没有过滤掉这个目录。

![20130703180428_53304.png](http://drops.javaweb.org/uploads/images/5adcb990358f3864f15b48a1146e983e41cb24ef.jpg)

![20130703180442_56745.png](http://drops.javaweb.org/uploads/images/c337923a74fa7eabbae172573f3e6f979caea657.jpg)

快速定位数据库连接信息：

大家可能都非常关心数据库连接一般都配置在什么地方呢？

答案普遍是：`C:\apache-tomcat-7.0.34\webapps\wordpress\WEB-INF`下的`***.xml`

大多数的Spring框架都是配置在applicationContext里面的：

![20130703180636_91481.png](http://drops.javaweb.org/uploads/images/19ce66b8a16e51787a0aafde1e81527eff55b910.jpg)

如果用到Hibernate框架那么：`WebRoot\WEB-INF\classes\hibernate.cfg.xml`

![20130703180710_10465.png](http://drops.javaweb.org/uploads/images/9590cd4fee66b92ef5e0b3bb5a1cf3fecc6c3f49.jpg)

还有一种变态的配置方式就是直接卸载源代码里面:

![20130703180735_97556.png](http://drops.javaweb.org/uploads/images/d847e8fe9cb152051fb8fff15dc1f88754c6e2cc.jpg)

Tomcat的数据源（其他的服务器大同小异）：

目录：`C:\apache-tomcat-7.0.34\conf\context.xml、server.xml`

![20130703180923_33143.png](http://drops.javaweb.org/uploads/images/009a3dbbc2ca9c17dd5b76c638da3bee3166a067.jpg)

![20130703180936_47449.png](http://drops.javaweb.org/uploads/images/2d1957cb29e517c0c0f1d67eb2fea9443b2c85c7.jpg)

Resin数据源：

路径：`D:\installDev\resin-pro-4.0.28conf\resin.conf(resin 3.x是resin.xml)`

其他的配置方式诸如读取如JEECMS读取的就是**.properties**配置文件，这种方式非常的常见：

![20130703181109_16068.png](http://drops.javaweb.org/uploads/images/afc583c35b62505e9b605dfb5f968813948d9551.jpg)

### 0x01 Tomcat 基础

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/dd90463f5732e0a3038e4c39a907312baf5507c8.jpg)

没错,这就是 TOM 猫。楼主跟这只猫打交道已经有好几年了,在 Java 应用当中 TOMCAT 运用的非常的广泛。

TOM 猫是一个 Web 应用服务器,也是 Servlet 容器。

Apache+Tomcat 做负载均衡:

![enter image description here](http://drops.javaweb.org/uploads/images/281c672f563dc232bff6c17af17a94f67fd4f400.jpg)

#### Tomcat快速定位到网站目录：

如何快速的找到tomcat的安装路径:

```
1、不管是谁都应该明白的是不管apache还是tomcat安装的路径都是随意的，所以找不到路径也是非常正常的。
2、在你的/etc/httpd/conf/httpd.conf里面会有一个LoadModule jk_module配置用于集成tomcat然后找到JkWorkersFile也就是tomcat的配置，找到.properties的路径。httpd里面也有可能会配置路径如果没有找到那就去apache2\conf\extra\httpd-vhosts看下有没有配置域名绑定。  
3、在第二步的时候找到了properties配置文件并读取，找到workers.tomcat_home也就是tomcat的配置路径了。  
4、得到tomcat的路径你还没有成功，域名的具体配置是在conf下的server.xml。  
5、读取server.xml不出意外你就可以找到网站的目录了。  
6、如果第五步没有找到那么去webapps目录下ROOT瞧瞧默认不配置的话网站是部署在ROOT下的。  
7、这一点是附加的科普知识爱听则听：数据库如果启用的tomcat有可能会采用tomcat的数据源配置未见为conf下的context.xml、server.xml。如果网站有域名绑定那么你可以试下ping域名然后带上端口访问。有可能会出现tomcat的登录界面。tomcat默认是没有配置用户登录的，所以当tomcat-users.xml下没有相关的用户配置就别在这里浪费时间了。  
8、如果配置未找到那么到网站目录下的WEB-INF目录和其下的classes目录下找下对应的properties、xml（一般都是properties）。  
9、如果你够蛋疼可以读取WEB.XML下的classess内的源码。  
10、祝你好运。

```

#### apache快速定位到网站目录：

普通的域名绑定：

直接添加到`confhttpd.conf、confextrahttpd-vhosts.conf`

#### Resin快速定位到网站目录:

在resin的conf下的resin.conf(resin3.x)和resin.xml(resin4.x)

Resin apache 负载均衡配置(从我以前的文章中节选的)

APACHE RESIN 做负载均衡,Resin 用来做 JAVAWEB 的支持,APACHE 用于处理静态

和 PHP 请求,RESIN 的速度飞快,RESIN 和 apache 的配合应该是非常完美的吧。

域名解析:

apache 的 httpd.conf:

![enter image description here](http://drops.javaweb.org/uploads/images/5acf7f77cb2f6c22067475af840c4728bbac69e8.jpg)

需要修改:Include conf/extra/httpd-vhosts.conf(一定要把前面的#除掉,否则配置不起作用)

普通的域名绑定:

直接添加到 httpd.conf

```
<VirtualHost *:80>
    ServerAdmin admin@bjcyw.cn
    DocumentRoot E:/XXXX/XXX
    ServerName beijingcanyinwang.com
    ErrorLog E:/XXXX/XXX/bssn-error_log
    CustomLog E:/XXXX/XXX/bssn_log common 
</VirtualHost>

```

二级域名绑定,需要修改:

```
E:\install\apache2\conf\extra\httpd-vhosts.conf

```

如:

```
<VirtualHost *:80>
    DocumentRoot E:/XXXXXXX/XXX
    ServerName bbs.beijingcanyinwang.com 
    DirectoryIndex index.html index.php index.htm
</VirtualHost>

```

![enter image description here](http://drops.javaweb.org/uploads/images/5d0e836db91d1e3b4bdb41792c4c226b5d78444e.jpg)

Resin 的

![enter image description here](http://drops.javaweb.org/uploads/images/17760344a37b1f64b147efc23c392ff927e56ea3.jpg)

请求处理:

```
<LocationMatch (.*?).jsp>
SetHandler caucho-request 
</LocationMatch>
<LocationMatch (.*?).action> 
SetHandler caucho-request 
</LocationMatch>
<LocationMatch union-resin-stat-davic> 
SetHandler caucho-request 
</LocationMatch>
<LocationMatch stat> 
SetHandler caucho-request 
</LocationMatch> 
<LocationMatch load>
SetHandler caucho-request 
</LocationMatch> 
<LocationMatch vote> 
SetHandler caucho-request 
</LocationMatch>

```

APACHE 添加对 Resin 的支持:

![enter image description here](http://drops.javaweb.org/uploads/images/bbd1692b28c68b9bc3d08ca7ddfdad671347a0e1.jpg)

```
LoadModule caucho_module "E:/install/resin-pro-3.1.12/win32/apache-2.2/mod_caucho. dll"

```

然后在末尾加上:

```
<IfModule mod_caucho.c> 
ResinConfigServer localhost 6800 
CauchoStatus yes
</IfModule>

```

只有就能让 apache 找到 resin 了。

PHP 支持问题:

resin 默认是支持 PHP 的测试 4.0.29 的时候就算你把 PHP 解析的 servlet 配置删了一样解析 PHP,无奈换成了 resin 3.1 在注释掉 PHP 的 servlet 配置就无压力了。

![enter image description here](http://drops.javaweb.org/uploads/images/4bb6d16b88b60adb759e7641a49ddd530d45ef38.jpg)

整合成功后:

![enter image description here](http://drops.javaweb.org/uploads/images/65f96a1c9442bc7c100bdf691cf7126b9b4be04b.jpg)