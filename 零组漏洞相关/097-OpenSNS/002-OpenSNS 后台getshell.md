# OpenSNS 后台getshell

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

1.打开网站后台找到模板上传位置：

`http://url/index.php?s=/admin/theme/add.html`

![](images/15891977843972.png)


2.配置一个压缩包，压缩包里是一句话木马：

![](images/15891977925072.png)


3.选择上传：

![](images/15891977997464.png)


4、会在./Theme目录下自动生成刚刚上传好的马儿


```bash
http://url/Theme/shell.php
```

![](images/15891978563562.png)
