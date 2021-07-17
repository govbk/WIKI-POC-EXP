# XML安全之Web Services

0x01 引言
=======

* * *

前段时间搞站遇到了TRS的系统里面涉及到了ws（Web Services简称）的相关技术，不久前玩一个xx酒店的时候又通过ws进入了它的数据库，后来接连遇到或看见一些app服务和物联网相关系统中出现XML相关漏洞，于是搜索相关资料做技术积累。如果文中出现错误，望指正。     

0x02 什么是WS
==========

* * *

Web Service是基于网络的、分布式的模块化组件，它执行特定的任务，遵守具体的技术规范，这些规范使得Web Service能与其他兼容的组件进行互操作。 Web Services 利用 SOAP 和 XML对这些模型在通讯方面作了进一步的扩展以消除特殊对象模型的障碍。Web Services 主要利用 HTTP 和 SOAP 协议使业务数据在 Web 上传输，SOAP通过 HTTP 调用业务对象执行远程功能调用，Web 用户能够使用 SOAP 和 HTTP通过 Web 调用的方法来调用远程对象的。（来至百度百科）。

简单的说WS就是http + XML，WS平台的元素有：SOAP、UDDI、WSDL。

0x03 xml注入（soap注入）
==================

* * *

以下将介绍一些利用场景，漏洞是千变万化的肯定不全，也不是每种环境都适用。

情景1：
----

漏洞：

```
<?xml version="1.0" encoding="UTF-8"?>
<USER role="guest">attacker's code</USER>

```

poc:

```
A</USER><USER role="admin">B

```

情景2：
----

漏洞：

![enter image description here](http://drops.javaweb.org/uploads/images/913eef61e143a9c1b54c3bb3891cfd914a35e489.jpg)

改变了为空，通过返回错误发现loginid作为登陆判断：

![enter image description here](http://drops.javaweb.org/uploads/images/e4f18f5c9bc68b217d3aff540dcaf430ffafbaa6.jpg)

poc:

![enter image description here](http://drops.javaweb.org/uploads/images/7cca99bc66cafde5780bcb9377fc36a4dba36e0a.jpg)

 结果bypass登陆：

![enter image description here](http://drops.javaweb.org/uploads/images/b6420d17aea6205d83b295d036fabd7d450a005f.jpg)

情景3：
----

```
<transaction>
     <total>6000.00<total>
     <credit_card_number>12345</credit_card_number> //12345可控,覆盖<total>标签
     <expiration>01012008</expiration>
</transaction>

```

poc:

```
12345</credit_card_number><total>1.00</total><credit_card_number>12345

```

0x03 SQL注入和xpath注入
==================

* * *

总所周知SQL注入，注入的是数据库，作为owasp top10的漏洞，存在相当的普遍，ws中也同样存在。wooyun上也同样存在案例[WooYun: 安盛天平某平台系统可被getshell第四弹，并存在注入](http://www.wooyun.org/bugs/wooyun-2015-094720)，这种ws上的sql注入漏洞也是非常容易被忽略的。至于sql注入的利用，不用多少，不同数据库不同注入手法，和我们常见的sql注入方法一样，并无区别。

xpath注入，在wooyun上谈论的很少，中文资料也不是很多。简单的形容如果xml作为数据库的话xpath讲究相当与sql语句，因此如果服务器是用xml格式来存储数据，我们用xpath来调用数据，当传入参数过滤不严的时候，就可能照成xpath注入，当然xpath注入还有很多技巧和函数的使用以及和xxe结合使用之类的技巧，在此不多说。

举一ws注入xpath利用场景：

```
<sopaenv:Body>
<web1:Login xmlns:web1="http://ws.ws.com/">
<username>abc</username>
<password>123</password>
</web1:Login>
</sopaenv:Body>

```

假如正常的xpath查询：

```
string(//Employee[username/text()='abc' and password/text()='123']/account/text())

```

我们控制可以控制username或者password，输入

```
' or '1' = '1

```

最后xpath查询成为：

```
string(//Employee[username/text()='' or '1' = '1' and password/text()='' or '1' = '1']/account/text())

```

绕过登陆，当让xpath的利用不知如此，比如使用doc()函数读取任意xml文件、使用doc()和xxe读取任意文件。

0x04 DDOS和XXE
=============

* * *

为什么会有DDOS和XXE呢，前面已经说过了ws可以看成xml和http的结合，因此XML相关漏洞也是可能会出现在ws之中的，关于xml中的DDOS和XXE都是各位大牛都做了很多分析：

DDOS上有：长数据DDOS、多标签DDOS

例如:

```
<transaction>
       <total>6000.00<total>
       <credit_card_number>12345</credit_card_number>
       <credit_card_number>qqqq</credit_card_number>  
       <credit_card_number>qqqq</credit_card_number>  
       <credit_card_number>qqqq</credit_card_number>  
       <credit_card_number>qqqq</credit_card_number>  
       ``````
       <expiration>01012008</expiration>
</transaction>

```

xxe漏洞drops上已有文章：http://drops.wooyun.org/tips/5290，以及利用xxe漏洞DDOS，利用xxe漏洞SSRF、命令执行关于这连个漏洞推荐两篇文章：《Having Fun with XML hacking》、《XML实体攻击-从内网探测到命令执行步步惊心》

0x05 上传漏洞
=========

* * *

这两个都是危害非常大的漏洞：

上传漏洞，ws是可以上传附件的，典型的例子就是trs上传漏洞

[WooYun: 安徽省公路管理网站任意文件写入漏洞](http://www.wooyun.org/bugs/wooyun-2015-092138)

0x06 总结
=======

* * *

从上面的攻击方式不难看出分为两类：

*   1.xml相关攻击技术；
    
*   2.使用soap请求传输数据，数据进去其他函数或程序引起的漏洞（sql注入、文件上传等所有常见漏洞）
    

因此漏洞利用形式多种多样，不同场景会有不同利用方式结合使用或者是bypass，掌握基础的知识才能在遇到的时候灵活运用。

0x07 引用
=======

* * *

http://resources.infosecinstitute.com/soap-attack-2/

https://www.blackhat.com/presentations/bh-europe-07/Bhalla-Kazerooni/Whitepaper/bh-eu-07-bhalla-WP.pdf

https://www.owasp.org/index.php/Testing_for_Web_Services	