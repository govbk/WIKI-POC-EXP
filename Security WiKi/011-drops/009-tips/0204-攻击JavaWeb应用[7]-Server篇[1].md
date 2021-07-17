# 攻击JavaWeb应用[7]-Server篇[1]

java应用服务器
---------

* * *

Java应用服务器主要为应用程序提供运行环境，为组件提供服务。Java 的应用服务器很多，从功能上分为两类：JSP 服务器和 Java EE 服务器。

### 常见的Server概述

常见的Java服务器:Tomcat、Weblogic、JBoss、GlassFish、Jetty、Resin、IBM Websphere、Bejy Tiger、Geronimo、Jonas、Jrun、Orion、TongWeb、BES Application Server、ColdFusion、Apusic Application Server、Sun Application Server 、Oracle9i/AS、Sun Java System Application Server。

Myeclipse比较方便的配置各式各样的Server，一般只要简单的选择下Server的目录就行了。 ￼![enter image description here](http://drops.javaweb.org/uploads/images/c070902984fbf2fb2fc753c4f2368b079ce375dc.jpg)

部署完成后启动进入各个Server的后台：

![enter image description here](http://drops.javaweb.org/uploads/images/6c0a96ec7d4b2910c536daa916ed06f355fa522b.jpg)￼

### 构建WebShell war文件

```
1、打开Myeclipse新建Web项目
2、把jsp放到WebRoot目录下
3、导出项目为war文件

```

![enter image description here](http://drops.javaweb.org/uploads/images/25a24f34023e041e440d5da41d38eee05b84ded2.jpg)￼

Tomcat
------

* * *

Tomcat 服务器是一个免费的开放源代码的Web 应用服务器，属于轻量级应用服务器，在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调试JSP 程序的首选。

### Tomcat版本

Tomcat主流版本:5-6-7，最新版Tomcat8刚发布不久。Tomcat5较之6-7在文件结构上有细微的差异，6-7-8没有大的差异。最新版的Tomcat8主要新增了：Servlet 3.1, JSP 2.3, EL 3.0 and Web Socket 1.0支持。

版本详情说明：[http://tomcat.apache.org/whichversion.html](http://tomcat.apache.org/whichversion.html)

结构目录：

Tomcat5：

```
Bin、common、conf、LICENSE、logs、NOTICE、RELEASE-NOTES、RUNNING.txt、Server、shared、Temp、webapps、work

```

Tomcat6-8：

```
Bin、conf、lib、LICENSE、logs、NOTICE、RELEASE-NOTES、RUNNING.txt、temp、webapps、work

```

关注conf和webapps目录即可。conf目录与非常重要的tomcat配置文件比如登录帐号所在的tomcat-users.xml；域名绑定目录、端口、数据源(部分情况)、SSL所在的server.xml；数据源配置所在的context.xml文件，以及容器初始化调用的web.xml。

源码下载：

Tomcat6：[http://svn.apache.org/repos/asf/tomcat/tc6.0.x/tags/TOMCAT_6_0_18/](http://svn.apache.org/repos/asf/tomcat/tc6.0.x/tags/TOMCAT_6_0_18/)

Tomcat7：[http://svn.apache.org/repos/asf/tomcat/tc7.0.x/trunk/](http://svn.apache.org/repos/asf/tomcat/tc7.0.x/trunk/)

### Tomcat默认配置

#### 1、tomcat-users.xml

Tomcat5默认配置了两个角色：tomcat、role1。其中帐号为both、tomcat、role1的默认密码都是tomcat。不过都不具备直接部署应用的权限，默认需要有manager权限才能够直接部署war包，Tomcat5默认需要安装Administration Web Application。Tomcat6默认没有配置任何用户以及角色，没办法用默认帐号登录。

配置详解：http://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html#Introduction

#### 2、context.xml

Tomcat的上下文，一般情况下如果用Tomcat的自身的数据源多在这里配置。找到数据源即可用对应的帐号密码去连接数据库。

```
<Context>
    <WatchedResource>WEB-INF/web.xml</WatchedResource>
    <Resource name="jdbc/u3" auth="Container" type="javax.sql.DataSource"
              maxActive="100" maxIdle="30" maxWait="10000"
              username="xxxxx" password="xxxx" driverClassName="com.mysql.jdbc.Driver"
              url="jdbc:mysql://192.168.0.xxx:3306/xxx?autoReconnect=true"/>
</Context>

```

#### 3、server.xml

Server这个配置文件价值非常高，通常的访问端口、域名绑定和数据源可以在这里找到，如果想知道找到域名对应的目录可以读取这个配置文件。如果有用Https，其配置也在这里面能够找到。

#### 4、web.xml

web.xml之前讲MVC的时候有提到过，项目初始化的时候会去调用这个配置文件这个文件一般很少有人动但是不要忽略其重要性，修改web.xml可以做某些YD+BT的事情。

### Tomcat获取WebShell

#### Tomcat后台部署war获取WebShell

登录tomcat后台：http://xxx.com/manager/html，一般用`WAR file to deploy`就行了，`Deploy directory or WAR file located on server`这种很少用。

1>Deploy directory or WAR file located on server

Web应用的URL入口、XML配置文件对应路径、WAR文件或者该Web应用相对于/webapps目录的文件路径，然后单击 按钮，即可发布该Web应用，发布后在Application列表中即可看到该Web应用的信息。这种方式只能发布位于/webapps目录下的Web应用。

2>WAR file to deploy

选择需要发布的WAR文件，然后单击Deploy，即可发布该Web应用，发布后在Application列表中即可看到该Web应用的信息。这种方式可以发布位于任意目录下的Web应用。

其中，第二种方式实际上是把需要发布的WAR文件自动复制到/webapps目录下，所以上述两种方式发布的Web应用都可以通过在浏览器地址栏中输入http://localhost:8080/Web进行访问。

￼![enter image description here](http://drops.javaweb.org/uploads/images/4f501c2fee3fc2991a5cf0be1f6e01f872ad6ed1.jpg)

```
Tips:
当访问xxxx.com找不到默认管理地址怎么办?
1:http://xxxx.com/manager/html 查看是否存在
2:ping xxxx.com 获取其IP地址，在访问：http://111.111.111.111/manager/html
3:遍历server.xml配置读取配置

```

### Tomcat口令爆破

Tomcat登录比较容易爆破，但是之前说过默认不对其做任何配置的时候爆破是无效的。

Tomcat的认证比较弱，Base64(用户名:密码)编码，请求：” /manager/html/”如果响应码不是401（未经授权：访问由于凭据无效被拒绝。）即登录成功。

```
conn.setRequestProperty("Authorization", "Basic " + new BASE64Encoder().encode((user + ":" + pass).getBytes()));

```

### Tomcat漏洞

Tomcat5-6-7安全性并不完美，总是被挖出各种稀奇古怪的安全漏洞。在CVE和Tomcat官网也有相应的漏洞信息详情。

#### 怎样找到Tomcat的历史版本:

[http://archive.apache.org/dist/tomcat/](http://archive.apache.org/dist/tomcat/)

#### Tomcat历史版本漏洞?

Tomcat官网安全漏洞公布：

Apache Tomcat - Apache Tomcat 5 漏洞：[http://tomcat.apache.org/security-5.html](http://tomcat.apache.org/security-5.html)

Apache Tomcat - Apache Tomcat 6 漏洞：[http://tomcat.apache.org/security-6.html](http://tomcat.apache.org/security-6.html)

Apache Tomcat - Apache Tomcat7 漏洞：[http://tomcat.apache.org/security-7.html](http://tomcat.apache.org/security-7.html)

CVE 通用漏洞与披露:[http://cve.scap.org.cn/cve_list.php?keyword=tomcat&action=search&p=1](http://cve.scap.org.cn/cve_list.php?keyword=tomcat&action=search&p=1)

Cvedetails ：[http://www.cvedetails.com/product/887/Apache-Tomcat.html?vendor_id=45](http://www.cvedetails.com/product/887/Apache-Tomcat.html?vendor_id=45)[http://www.cvedetails.com/vulnerability-list/vendor_id-45/product_id-887/Apache-Tomcat.html](http://www.cvedetails.com/vulnerability-list/vendor_id-45/product_id-887/Apache-Tomcat.html)

Sebug:[http://sebug.net/appdir/Apache+Tomcat](http://sebug.net/appdir/Apache+Tomcat)

#### 怎样发现Tomcat有那些漏洞?

1、通过默认的报错页面（404、500等）可以获取到Tomcat的具体版本，对照Tomcat漏洞。

2、利用WVS之类的扫描工具可以自动探测出对应的版本及漏洞。

#### 怎样快速确定是不是Tomcat?

请求响应为:Server:Apache-Coyote/1.1 就是tomcat了。

#### Tomcat稀奇古怪的漏洞：

Tomcat的安全问题被爆过非常多，漏洞统计图：

![enter image description here](http://drops.javaweb.org/uploads/images/bfda32d47d2bb9b06f10e8f005c557809ca8f97d.jpg)

有一些有意思的漏洞，比如：Insecure default password CVE-2009-3548(影响版本: 6.0.0-6.0.20)

The Windows installer defaults to a blank password for the administrative user. If this is not changed during the install process, then by default a user is created with the name admin, roles admin and manager and a blank password.在windows安装版admin默认空密码漏洞，其实是用户安装可能偷懒，没有设置密码…

![enter image description here](http://drops.javaweb.org/uploads/images/5d4875577481b332a49cbc503f9de9a81ffbce0c.jpg)

这样的问题在tar.gz和zip包里面根本就不会存在。有些漏洞看似来势汹汹其实鸡肋得不行如：Unexpected file deletion in work directory CVE-2009-2902 都已经有deploy权限了，闹个啥。

Tomcat非常严重的漏洞（打开Tomcat security-5、6、7.html找）：

```
Important: Session fixation CVE-2013-2067 (6.0.21-6.0.36) 
Important: Denial of service CVE-2012-3544 (6.0.0-6.0.36) 
Important: Denial of service CVE-2012-2733 (6.0.0-6.0.35) 
Important: Bypass of security constraints CVE-2012-3546 (6.0.0-6.0.35) 
Important: Bypass of CSRF prevention filter CVE-2012-4431 (6.0.30-6.0.35) 
Important: Denial of service CVE-2012-4534 (6.0.0-6.0.35) 
Important: Information disclosure CVE-2011-3375 (6.0.30-6.0.33) 
Important: Authentication bypass and information disclosure CVE-2011-3190 (6.0.0-6.0.33) (………………………………………………….) 
Important: Directory traversal CVE-2008-2938 (6.0.18) 
Important: Directory traversal CVE-2007-0450 (6.0.0-6.0.9)

```

如果英文亚历山大的同学，对应的漏洞信息一般都能够在中文的sebug找到。

Sebug：

![enter image description here](http://drops.javaweb.org/uploads/images/c95ae3e8e5708e75c074b0b2a0638f8efcfb06ff.jpg)

CVE 通用漏洞与披露：

![enter image description here](http://drops.javaweb.org/uploads/images/2377778d6a3ed56a7e7b3d5c49335acb04275093.jpg)

Resin
-----

* * *

Resin是CAUCHO公司的产品，是一个非常流行的application server，对servlet和JSP提供了良好的支持，性能也比较优良，resin自身采用JAVA语言开发。

Resin比较有趣的是默认支持PHP! Resin默认通过Quercus 动态的去解析PHP文件请求。（Resin3也支持，详情：[http://zone.wooyun.org/content/2467](http://zone.wooyun.org/content/2467)）

### Resin版本

Resin主流的版本是Resin3和Resin4，在文件结构上并没有多大的变化。Resin的速度和效率非常高，但是不知怎么Resin似乎对Quercus 更新特别多。

4.0.x版本更新详情：[http://www.caucho.com/resin-4.0/changes/changes.xtp](http://www.caucho.com/resin-4.0/changes/changes.xtp)

3.1.x版本更新详情：[http://www.caucho.com/resin-3.1/changes/changes.xtp](http://www.caucho.com/resin-3.1/changes/changes.xtp)

### Resin默认配置

#### 1、resin.conf和resin.xml

Tomcat和Rsin的核心配置文件都在conf目录下，Resin3.1.x 默认是resin.conf而4.0.x默认是resin.xml。resin.conf/resin.xml是Resin最主要配置文件，类似Tomcat的server.xml。

#### 1>数据源:

第一节的时候有谈到resin数据源就是位于这个文件，搜索database（位于server标签内）即可定位到具体的配置信息。

#### 2>域名绑定

搜索host即可定位到具体的域名配置，其中的root-directory是域名绑定的对应路径。很容易就能够找到域名绑定的目录了。

```
<host id="javaweb.org" root-directory=".">
      <host-alias-regexp>^([^/]*).javaweb.org</host-alias-regexp>
      <web-app id="/" root-directory="D:/web/xxxx/xxxx"/>
</host>

```

### Resin默认安全策略

#### 1>管理后台访问权限

Resin比较BT的是默认仅允许本机访问管理后台，这是因为在resin.conf当中默认配置禁止了外部IP请求后台。

```
<resin:set var="resin_admin_external" value="false"/>

```

修改为true外部才能够访问。

#### 2>Resin后台管理密码

Resin的管理员密码需要手动配置，在resin.conf/resin.xml当中搜索management。即可找到不过需要注意的是Resin的密码默认是加密的，密文是在登录页自行生成。比如admin加密后的密文大概会是：yCGkvrQHY7K8qtlHsgJ6zg== 看起来仅是base64编码不过不只是admin默认的Base64编码是：YWRtaW4= Resin,翻了半天Resin终于在文档里面找到了：[http://www.caucho.com/resin-3.1/doc/resin-security.xtp](http://www.caucho.com/resin-3.1/doc/resin-security.xtp)

￼![enter image description here](http://drops.javaweb.org/uploads/images/fb09b21526f45941067f76e2b224cd6da0ee6cb9.jpg)

虽说是MD5+Base64加密但是怎么看都有点不对，下载Resin源码找到加密算法：

```
package com.caucho.server.security.PasswordDigest

```

![enter image description here](http://drops.javaweb.org/uploads/images/39325249ad644b439efb48abb90fbe8f4dd5305d.jpg)

这加密已经没法反解了，所以就算找到Resin的密码配置文件应该也没法破解登录密码。事实上Resin3的管理后台并没有其他Server（相对JBOSS和Weblogic）那么丰富。而Resin4的管理后台看上去更加有趣。

Resin4的加密方式和Resin3还不一样改成了SSHA：

```
admin_user : admin
admin_password : {SSHA}XwNZqf8vxNt5BJKIGyKT6WMBGxV5OeIi

```

详情：[http://www.caucho.com/resin-4.0/admin/security.xtp](http://www.caucho.com/resin-4.0/admin/security.xtp)

Resin3：

![enter image description here](http://drops.javaweb.org/uploads/images/939b80569ce4b6d41febd547c0478b928ba57c6e.jpg)

Resin4：

![enter image description here](http://drops.javaweb.org/uploads/images/c56ef7fbd94ebb006418b05973cff732a72d46d1.jpg)

### Resin获取WebShell

As of Resin 4.0.0, it is now possible to deploy web applications remotely to a shared repository that is distributed across the cluster. This feature allows you to deploy once to any triad server and have the application be updated automatically across the entire cluster. When a new dynamic server joins the cluster, the triad will populate it with these applications as well.

Web Deploy war文件大概是从4.0.0开始支持的，不过想要在Web deploy一个应用也不是一件简单的事情，首先得先进入后台。然后还得以Https方式访问。不过命令行下部署就没那没法麻烦。Resin3得手动配置web-app-deploy。 最简单的但又不爽办法就是想办法把war文件上传到resin-pro-3.1.13webapps目录下，会自动部署（就算Resin已启动也会自动部署，不影响已部署的应用）。

Resin3部署详情：[http://www.caucho.com/resin-3.1/doc/webapp-deploy.xtp](http://www.caucho.com/resin-3.1/doc/webapp-deploy.xtp)

Resin4部署War文件详情：[http://www.caucho.com/resin-4.0/admin/deploy.xtp](http://www.caucho.com/resin-4.0/admin/deploy.xtp)

Resin4进入后台后选择Deploy,不过还得用SSL方式请求。Resin要走一个”非加密通道”。

To deploy an application remotely: log into the resin-admin console on any triad server. Make sure you are connecting over SSL, as this feature is not available over a non-encrypted channel. Browse to the "webapp" tab of the resin-admin server and at the bottom of the page, enter the virtual host, URL, and local .war file specifying the web application, then press "Deploy". The application should now be deployed on the server. In a few moments, all the servers in the cluster will have the webapp.

￼![enter image description here](http://drops.javaweb.org/uploads/images/f0f6f450005e4f67f252db73efde07b5aa7c1705.jpg)

Resin4敢不敢再没节操点？默认HTTPS是没有开的。需要手动去打开:

```
conf

```

esin.properties

  

```
# https : 8443

```

默认8443端口是关闭的，取消这一行的注释才能够使用HTTPS方式访问后台才能够Web Deploy war。

![enter image description here](http://drops.javaweb.org/uploads/images/5af6b78f0b6efb463cdfe5ce9ce3abf77e463094.jpg)

部署成功访问:[http://localhost:8080/GetShell/Customize.jsp](http://localhost:8080/GetShell/Customize.jsp)即可获取WebShell。

### Resin漏洞

Resin相对Tomcat的安全问题来说少了很多，Cvedetails上的Resin的漏洞统计图：

![enter image description here](http://drops.javaweb.org/uploads/images/16343792319b60e1096fce7d5f5ed9ed60a8d8ea.jpg)

Cvedetails统计详情：[http://www.cvedetails.com/product/993/Caucho-Technology-Resin.html?vendor_id=576](http://www.cvedetails.com/product/993/Caucho-Technology-Resin.html?vendor_id=576)

Cvedetails漏洞详情：[http://www.cvedetails.com/vulnerability-list/vendor_id-576/product_id-993/Caucho-Technology-Resin.html](http://www.cvedetails.com/vulnerability-list/vendor_id-576/product_id-993/Caucho-Technology-Resin.html)

CVE 通用漏洞与披露：[http://cve.scap.org.cn/cve_list.php?keyword=resin&action=search&p=1](http://cve.scap.org.cn/cve_list.php?keyword=resin&action=search&p=1)

Resin3.1.3:

![enter image description here](http://drops.javaweb.org/uploads/images/f06d4959831df9c8838e2d14e36c9d52a259cfe3.jpg)

Fixed BugList:[http://bugs.caucho.com/changelog_page.php](http://bugs.caucho.com/changelog_page.php)

Weblogic
--------

* * *

WebLogic是美国bea公司出品的一个application server确切的说是一个基于Javaee架构的中间件，BEA WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

### Weblogic版本

Oracle简直就是企业应用软件终结者，收购了Sun那个土鳖、Mysql、BAE Weblogic等。BAE在2008初被收购后把BAE终结在Weblogic 10。明显的差异应该是从10.x开始到最新的12c。这里主要以Weblogic9.2和最新的Weblogic 12c为例。

### Weblogic默认配置

Weblogic默认端口是7001，Weblogic10g-12c默认的管理后台是：http://localhost:7001/console

Weblogic10 以下默认后台地址是：http://192.168.80.1:7001/console/login/LoginForm.jsp

管理帐号是在建立Weblogic域的时候设置的。

![enter image description here](http://drops.javaweb.org/uploads/images/3b587e76ce719ae89dd9507d86e74d03c3f8a84b.jpg)

Weblogic控制台：

[enter link description here](http://static.wooyun.org/20141017/2014101711455629318.png)

Weblogic10以下默认管理帐号:weblogic密码：weblogic。关于Weblogic10++的故事还得从建域开始，默认安装完Weblogic后需要建立一个域。

### WebLogic中的"域"?

域环境下可以多个 WebLogic Server或者WebLogic Server 群集。域是由单个管理服务器管理的 WebLogic Server实例的集合。 Weblogic10++域默认是安装完成后由用户创建。帐号密码也在创建域的时候设置，所以这里并不存在默认密码。当一个域创建完成后配置文件和Web应用在：Weblogic12user_projectsdomains”域名”。

### Weblogic 默认安全策略

### 1、Weblogic默认密码文件:

Weblogic 9采用的3DES（三重数据加密算法）加密方式，Weblogic 9默认的管理密码配置文件位于：

```
weblogic_9weblogic92samplesdomainswl_serverserversexamplesServersecurityoot.properties

```

#### boot.properties：

```
# Generated by Configuration Wizard on Sun Sep 08 15:43:13 GMT 2013
username={3DES}fy709SQ4pCHAFk+lIxiWfw==
password={3DES}fy709SQ4pCHAFk+lIxiWfw==

```

Weblogic 12c采用了AES对称加密方式，但是AES的key并不在这文件里面。默认的管理密码文件存放于：

```
Weblogic12user_projectsdomainsase_domainserversAdminServersecurityoot.properties 

```

(base_domain是默认的”域名”)。

#### boot.properties：

```
boot.properties：
# Generated by Configuration Wizard on Tue Jul 23 00:07:09 CST 2013
username={AES}PsGXATVgbLsBrCA8hbaKjjA91yNDCK78Z84fGA/pTJE=
password={AES}Z44CPAl39VlytFk1I5HUCEFyFZ1LlmwqAePuJCwrwjI=

```

怎样解密Weblogic密码?

Weblogic 12c：

```
Weblogic12user_projectsdomainsase_domainsecuritySerializedSystemIni.dat

```

Weblogic 9：

```
weblogic_9weblogic92samplesdomainswl_serversecuritySerializedSystemIni.dat

```

解密详情：[http://drops.wooyun.org/tips/349](http://drops.wooyun.org/tips/349)、[http://www.blogjava.net/midea0978/archive/2006/09/07/68223.html](http://www.blogjava.net/midea0978/archive/2006/09/07/68223.html)

### 2、Weblogic数据源(JNDI)

Weblogic如果有配置数据源，那么默认数据源配置文件应该在：

```
Weblogic12user\_projectsdomainsase\_domainconfigconfig.xml

```

![enter image description here](http://drops.javaweb.org/uploads/images/ba15dde661e75fdbde1257c2accf6e2e625a28c8.jpg)

### Weblogic获取Webshell ￼

![enter image description here](http://drops.javaweb.org/uploads/images/ea7f1dc169bbc67137f180362307fdeea2623636.jpg)

Weblogic 9 GetShell：[http://drops.wooyun.org/tips/402](http://drops.wooyun.org/tips/402)

Websphere
---------

* * *

WebSphere 是 IBM 的软件平台。它包含了编写、运行和监视全天候的工业强度的随需应变 Web 应用程序和跨平台、跨产品解决方案所需要的整个中间件基础设施，如服务器、服务和工具。

### Websphere版本

Websphere现在主流的版本是6-7-8，老版本的5.x部分老项目还在用。GetShell大致差不多。6、7测试都有“默认用户标识admin登录”，Websphere安装非常麻烦，所以没有像之前测试Resin、Tomcat那么细测。

### Websphere默认配置

默认的管理后台地址（注意是HTTPS）：[https://localhost:9043/ibm/console/logon.jsp](https://localhost:9043/ibm/console/logon.jsp)

默认管理密码：

```
1、admin (测试websphere6-7默认可以直接用admin作为用户标识登录，无需密码) 
2、websphere/ websphere
3、system/ manager

```

默认端口：

```
管理控制台端口 9060
管理控制台安全端口 9043
HTTP传输端口 9080
HTTPS传输端口 9443
引导程序端口 2809
SIP端口 5060
SIP安全端口 5061
SOAP连接器端口 8880
SAS SSL ServerAuth端口 9401
CSIV2 ServerAuth 侦听器端口 9403
CSIV2 MultiAuth 侦听器端口 9402
ORB侦听器端口 9100
高可用性管理通讯端口(DCS) 9353
服务集成端口 7276
服务集成安全端口 7286
服务集成器MQ互操作性端口 5558
服务集成器MQ互操作性安全端口 5578

```

8.5安装的时候创建密码： ￼

[enter link description here](http://static.wooyun.org/20141017/2014101711455696316.png)

Websphere8.5启动信息：

![enter image description here](http://drops.javaweb.org/uploads/images/8e40330bc26d575bc3e64e4b003f00989850d556.jpg)

Websphere8.5登录页面： https://localhost:9043/ibm/console/logon.jsp

[enter link description here](http://static.wooyun.org/20141017/2014101711455610557.png)

Websphere8.5 WEB控制台：

![enter image description here](http://drops.javaweb.org/uploads/images/eeb9f09d5aecc16ae270373fa2db63e20f221402.jpg)

Websphere6-7默认控制台地址也是： http://localhost:9043/ibm/console，此处用admin登录即可。

![enter image description here](http://drops.javaweb.org/uploads/images/c221ead42d069071fb663798f3f96cc88999ddab.jpg)

### Websphere GetShell

本地只安装了8.5测试，Websphere安装的确非常坑非常麻烦。不过Google HACK到了其余两个版本Websphere6和Websphere7。测试发现Websphere GetShell一样很简单，只是比较麻烦，一般情况直接默认配置Next就行了。Websphere7和Websphere8 GetShell基本一模一样。

#### Websphere6 GetShell

需要注意的是Websphere6默认支持的Web应用是2.3(web.xml配置的web-app_2_3.dtd)直接上2.5是不行的，请勿霸王硬上弓。其次是在完成部署后记得保存啊亲，不然无法生效。

![enter image description here](http://drops.javaweb.org/uploads/images/5716b0ac220aba67632bcb36b46691d273c9640a.jpg)

#### Websphere8.5 GetShell

部署的时候记得写上下文名称哦，不让无法请求到Shell。

![enter image description here](http://drops.javaweb.org/uploads/images/f36e0e7aecd925d0f80f2bc4a95cf008e7334cf8.jpg)

注意：

如果在Deploy低版本的Websphere的时候可能会提示web.xml错误，这里其实是因为支持的JavaEE版本限制，把war包里面的web.xml改成低版本就行了，如把app2.5改成2.3。

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE web-app PUBLIC "-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN" "http://java.sun.com/dtd/web-app_2_3.dtd">
<web-app>
    <welcome-file-list>
        <welcome-file>index.jsp</welcome-file>
    </welcome-file-list>
</web-app>

```

GlassFish
---------

* * *

GlassFish是SUN的产品，但是作为一只优秀的土鳖SUN已经被Oracle收购了，GlassFish的性能优越对JavaEE的支持自然最好，最新的Servlet3.1仅GlassFish支持。

### GlassFish版本

GlassFish版本比较低调，最高版本GlassFish4可在官网下载： http://glassfish.java.net/ 。最新4.x版刚发布不久。所以主流版本应当还是v2-3,3应该更多。支持php(v3基于Quercus),jRuby on Rails 和 Phobos等多种语言。

### GlassFish 默认配置

默认Web控制后台： http://localhost:4848

默认管理密码： GlassFish2默认帐号admin密码adminadmin 。

GlassFish3、4 如果管理员不设置帐号本地会自动登录，但是远程访问会提示配置错误。

```
Configuration Error 
Secure Admin must be enabled to access the DAS remotely.

```

默认端口：

```
使用Admin的端口 4848。
使用HTTP Instance的端口 8080。
使用JMS的端口 7676。
使用IIOP的端口 3700。
使用HTTP_SSL的端口 8181。
使用IIOP_SSL的端口 3820。
使用IIOP_MUTUALAUTH的端口 3920。
使用JMX_ADMIN的端口 8686。
使用OSGI_SHELL的默认端口 6666。
使用JAVA_DEBUGGER的默认端口 9009。

```

默认数据源：

![enter image description here](http://drops.javaweb.org/uploads/images/c651622b34c0e7af7439b51ad288a1d6bee2a93b.jpg)

### GlassFish GetShell ￼

![enter image description here](http://drops.javaweb.org/uploads/images/4da0e757287268ea0b8e7a7b0eb7dc739d665ae8.jpg)