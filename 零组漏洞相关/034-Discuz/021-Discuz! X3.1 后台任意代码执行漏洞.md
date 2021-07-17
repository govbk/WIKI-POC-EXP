# Discuz! X3.1 后台任意代码执行漏洞

## 一、漏洞简介

## 二、漏洞影响

Discuz! X3.1

## 三、复现过程

* 全局--〉网站第三方统计代码--〉插入php代码[其他地方<>会被转意]：

如插入

    ![007uCUf6ly1fxlneom4cfj30om0l40vg.jpg](images/2020_06_13/e72b7f847e91482cb829d2217b94718d.jpg)

* 工具--〉更新缓存[为了保险起见，更新下系统缓存]：
* 
    ![2.jpg](images/2020_06_13/accf53cbe9b64037ba9327f72054127d.jpg)

* 门户--> HTML管理--〉设置：

1. 1） 静态文件扩展名[一定要设置成htm] ：htm
2. 2) 专题HTML存放目录: template/default/portal
3. 3) 设置完，提交吧！

![3.jpg](images/2020_06_13/20d119602c7541d5a98bc51486b36610.jpg)

* 门户--〉专题管理--〉创建专题：

1. 1）专题标题：xyz // 这个随便你写了
2. 2）静态化名称：portal_topic_222 //222为自定义文件名，自己要记住
3. 3）附加内容：选择上： 站点尾部信息

![4.jpg](images/2020_06_13/857b7ac614174b978c5dc239737c33b0.jpg)

* 提交
* 回到门户--〉专题管理,把刚才创建的专题开启，如下图 ：

![5.jpg](images/2020_06_13/e65dbaa5af4b4fd3b49b998f63c4c8ad.jpg)

* 把刚才的专题，生成

![6.jpg](images/2020_06_13/dcc0714eea0c4492bf3a904cea1e6d20.jpg)

下面就是关键了，现在到了包含文件的时候了。

* 再新建一个专题：

1）专题标题，静态化名称，这2个随便写

2）模板名：这个要选择我们刚才生成的页面：./template/default/portal/portal_topic_222.htm

![7.jpg](images/2020_06_13/4ce46cc9438c46ea97d05a89324feefb.jpg)

* 然后提交，就执行了

![8.jpg](images/2020_06_13/b095ec22d6e14ebab2717e680b563c36.jpg)

