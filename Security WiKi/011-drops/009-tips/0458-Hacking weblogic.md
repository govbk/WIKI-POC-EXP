# Hacking weblogic

From[Hacking-weblogic-sysmox.com.pdf](http://sysmox.com/blog/wp-content/uploads/2011/10/Hacking-weblogic-sysmox.com_.pdf)

0x00 简介
-------

* * *

此篇文章介绍攻击者如何利用默认密码对weblogic攻击。

### Weblogic

WebLogic是美国bea公司出品的一个application server确切的说是一个基于Javaee架构的中间件，BEA WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

0x01 安装
-------

* * *

有很多的weblogic服务器安装时采用默认密码。

这样会使攻击者很容易进入weblogic控制台获取相应权限。

默认的WebLogic管理员账号密码是

weblogic:weblogic

WebLogic的默认端口是7001

Http://localhost:7001/console

下面列举了一些weblogic默认密码列表：

[http://cirt.net/passwords?criteria=weblogic](http://cirt.net/passwords?criteria=weblogic)

![enter image description here](http://drops.javaweb.org/uploads/images/5b21e247a187338cad36586dffa08c0a40bedee1.jpg)

进入控制台界面：

![enter image description here](http://drops.javaweb.org/uploads/images/cd36bf7cb887913178c6db71ac3404aa2e3f5356.jpg)

0x02 Web应用
----------

* * *

在控制台部署一个Web应用的方法：

```
Deploy => web application modules => Deploy a new Web Application Module... =>upload your file(s) => Deploy

```

Web应用中包含的模块：

必须要有一个servlet或者JSP 一个web.xml文件，它包含有关Web应用程序的信息 可以有一个weblogic.xml文件，包含了WebLogic服务器的web应用元素。

### 部署

攻击者上传一个backdoor.war

![enter image description here](http://drops.javaweb.org/uploads/images/ecbcf50370e0dd30eea5f5473fd808f794a9626e.jpg)

### weblogic后门

例子：

![enter image description here](http://drops.javaweb.org/uploads/images/3fdc4b18c84bebf0070e40fcfc3eced2da1f2415.jpg)

寻找weblogic服务器可以有很多的方法

![enter image description here](http://drops.javaweb.org/uploads/images/777298501bd64c438a1a923d47fe2d9b373dffe5.jpg)

乌云上的实例：

[WooYun: 广东省社会保险基金管理局网站弱口令问题](http://www.wooyun.org/bugs/wooyun-2012-05295)

[WooYun: 江苏省财政厅弱口令](http://www.wooyun.org/bugs/wooyun-2012-06733)

0x03 weblogic安全配置
-----------------

* * *

[http://download.oracle.com/docs/cd/E12890_01/ales/docs32/integrateappenviron/configWLS.html#wp1099454](http://download.oracle.com/docs/cd/E12890_01/ales/docs32/integrateappenviron/configWLS.html#wp1099454)