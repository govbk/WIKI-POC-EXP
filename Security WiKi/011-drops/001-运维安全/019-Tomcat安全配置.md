# Tomcat安全配置

`tomcat`是一个开源`Web`服务器，基于`Tomcat`的`Web`运行效率高，可以在一般的硬件平台上流畅运行，因此，颇受`Web`站长的青睐。不过，在默认配置下其存在一定的安全隐患，可被恶意攻击。

0x00 测试环境
=========

* * *

Win2003

Tomcat6.0.18 安装版

0x01 安全验证
=========

* * *

### 一.登陆后台

首先在`win2003`上部署`Tomcat`,一切保持默认。

`Tomcat`的默认后台地址为:`http://域名:端口/manager/html`.进入之后弹出登陆对话框,`Tomcat`默认的用户名`admin`,密码为空。

`Tomcat`的一些弱口令:

```
tomcat tomcat 
admin 空 
admin admin 
admin 123456

```

![enter image description here](http://drops.javaweb.org/uploads/images/f7cdad77d6ca4b04fdaffd10299eeded052fb17b.jpg)

然后来看一下`Tomcat`安装版默认的`tomacat-users.xml`配置文件

![enter image description here](http://drops.javaweb.org/uploads/images/dda251ffa019a4e667d1dab9be144eaf7cb54e62.jpg)

注：`Linux`平台及`Windows`平台免安装版本不受该漏洞影响。

### 二.获取Webshell

在`Tomcat`的后台有个`WAR file to deploy`模块，通过其可以上传`WAR`文件。`Tomcat`可以解析`WAR`文件，能够将其解压并生成`web`文件。

![enter image description here](http://drops.javaweb.org/uploads/images/790ba5d2ec7643afb3f4bffcc9942dcebb443c5b.jpg)

我们将一个`jsp`格式的`webshell`用`WinRar`打包然后将其后缀改名为`WAR`(本例为`no.war`)，这样;一个`WAR`包就生成了。最后将其上传到服务器，可以看到在`Tomcat`的后台中多了一个名为`/no`的目录。

![enter image description here](http://drops.javaweb.org/uploads/images/bb7cd52c9c57caa207b81a1d201b50046cbc287c.jpg)

点击该目录打开该目录`jsp`木马就运行了，这样就获得了一个`Webshell`。

![enter image description here](http://drops.javaweb.org/uploads/images/74992d91dfb63fea82367d8dd459ff77a901f5ff.jpg)

### 三.获取服务器权限

`Tomcat`服务默认是以`system`权限运行的，因此该`jsp`木马就继承了其权限，几乎可以对`Web`服务器进行所有的操作。

![enter image description here](http://drops.javaweb.org/uploads/images/7f259ee43ef100cfce10c731fd3f42e4acc37d23.jpg)

然后创建用户:`net user Boom shellcode /add`

添加到管理员用户组:`net localgroup administrators Boom /add`

![enter image description here](http://drops.javaweb.org/uploads/images/8137836254aad5adfbccb4deaf9c5936239bffca.jpg)

然后可以干什么事我就不说了

0x02 安全配置
=========

* * *

### 一.修改tomacat-users.xml或删除Tomcat后台

修改`\conf\tomacat-users.xml`

![enter image description here](http://drops.javaweb.org/uploads/images/e6887a5569293e7917f1248c6870d55774cc8270.jpg)

删除`Tomcat`后台`\webapps`全部删除就好。

### 二.禁止列目录

在`IIS`中如果设置不当，就会列出`Web`当前目录中的所有文件，然而在`Tomcat`也不例外。如果浏览者可以在客户端浏览`Web`目录，那将会存在较大的安全隐患，因此我们要确认`Tomcat`的设置中禁止列目录。`\conf\web.xml`下

```
<init-param>
<param-name>listings</param-name>
<param-value>false</param-value>
</init-param>　　

```

确认是`false`而不是`true`。

![enter image description here](http://drops.javaweb.org/uploads/images/7ace26cbf28612aedb85fe201893a3fc0322629c.jpg)

### 三.服务降权

默认安装时`Tomcat`是以系统服务权限运行的，因此缺省情况下几乎所有的`Web`服务器的管理员都具有`Administrator`权限，存在极大的安全隐患，所以我们的安全设置首先从`Tomcat`服务降权开始。

首先创建一个普通用户，为其设置密码，将其密码策略设置为“密码永不过期”，比如我们创建的用户为`tomcat`。然后修改`tomcat`安装文件夹的访问权限，为`tomcat`赋予`Tomcat`文件夹的读、写、执行的访问权限，赋予`Tomcat`对`WebApps`文件夹的只读访问权限，如果某些`Web`应用程序需要写访问权限，单独为其授予对那个文件夹的写访问权限。

![enter image description here](http://drops.javaweb.org/uploads/images/d9828eeaa5a569bcfb9fe9915d8c33dd6501f684.jpg)

“开始→运行”，输入`services.msc`打开服务管理器，找到`Apache Tomcat`服务，双击打开该服务的属性，在其实属性窗口中点击“登录”选项卡，在登录身份下选中“以此帐户”，然后在文本框中输入`tomcat`和密码，最后“确定”并重启服务器。这样`tomcat`就以`tomcat`这个普通用户的权限运行。

![enter image description here](http://drops.javaweb.org/uploads/images/ec6815729e4cc64163a71cd7a89b03d4c974496d.jpg)

然后重启服务,就生效了。这样普通用户`tomcat`运行的`Tomcat`其权限就大大地降低了，就算是攻击者获得了`Webshell`也不能进一步深入，从而威胁web服务器的安全。

### 四.关闭war自动部署

关闭`war`自动部署`unpackWARs="false" autoDeploy="false"`。防止被植入木马等恶意程序

应用程序部署与`tomcat`启动,不能使用同一个用户。

![enter image description here](http://drops.javaweb.org/uploads/images/d27dad9cce093e04fb3259c5f4f3b386c2e64a74.jpg)