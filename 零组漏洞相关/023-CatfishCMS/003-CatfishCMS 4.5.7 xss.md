# CatfishCMS 4.5.7 xss

## 漏洞影响

CatfishCMS 4.5

### 复现过程

**漏洞分析**

文件：`application\config.php`

参数：`default_filter`

![](images/15889448339496.png)


最后找到一处未过滤的地方

文件：application/index/controller/Index.php

方法：pinglun()

![](images/15889448416239.png)


过滤函数

文件：application\index\controller\Common.php

方法：filterJs()

![](images/15889448492587.png)


可以看到只是简单的过滤

