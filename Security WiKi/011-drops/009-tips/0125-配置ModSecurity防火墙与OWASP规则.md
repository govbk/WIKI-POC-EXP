# 配置ModSecurity防火墙与OWASP规则

**from:http://resources.infosecinstitute.com/configuring-modsecurity-firewall-owasp-rules/**

0x00 背景
-------

* * *

ModSecurity是一个免费、开源的Apache模块，可以充当Web应用防火墙（WAF）。ModSecurity是一个入侵探测与阻止的引擎.它主要是用于Web应用程序所以也可以叫做Web应用程序防火墙.ModSecurity的目的是为增强Web应用程序的安全性和保护Web应用程序避免遭受来自已知与未知的攻击.

OWASP是一个安全社区，开发和维护着一套免费的应用程序保护规则，这就是所谓OWASP的ModSecurity的核心规则集（即CRS）。我们可以通过ModSecurity手工创建安全过滤器、定义攻击并实现主动的安全输入验证.

所以，在这篇文章中，我们将配置ModSecurity防火墙与OWASP的核心规则集。我们也将学习如何可以根据我们的需要自定义OWASP的核心规则集或创建自己的定制规则.

0x01 安装过程
---------

* * *

本文是在Centos环境中安装和配置的，步骤如下：

**第1步**

以root用户身份登录到您的服务器，登录之后我们在安装ModSecurity之前需要安装一些依赖包，可以通过以下的命令安装：

```
yum install gcc make libxml2 libxml2-devel httpd-devel pcre-devel curl-devel –y 

```

![2014072015283665193.jpg](http://drops.javaweb.org/uploads/images/00a038d4257d9c21a6aa75f5c4dde35042fe2622.jpg)

**第2步**  
安装依赖包后，我们将安装ModSecurity。我们可以通过运行以下命令进行安装：

```
yum install mod_security –y  

```

![2014072015285788999.png](http://drops.javaweb.org/uploads/images/2a991f3f6f13afcfe1cc5b604fc7f5e5c625fcd8.jpg)

现在ModSecurity已经成功地安装在系统中。

**第3步**

ModSecurity安装后，我们需要重新启动Apache服务器。我们可以通过下面的命令重启Apache服务器：

```
Services httpd restart 

```

或

```
在/etc/init.d/httpd restart  

```

![2014072015294663934.png](http://drops.javaweb.org/uploads/images/4d371a3846114cf47735fedc4f094d2fd33fca74.jpg)

现在，我们已经成功地在服务器中安装了ModSecurity，下一个步骤是下载和配置OWASP的ModSecurity规则。所以，我们必须将当前工作目录切换到/etc/httpd的。这可以通过cd命令来完成。

```
cd /etc/httpd. 

```

![2014072015300972448.jpg](http://drops.javaweb.org/uploads/images/7e52bb6b2562d1e121ba6a234e7ce2a0d626ee83.jpg)

**第4步**

正如我们在文章的前面所提到的，我们的ModSecurity安装是不完美的，但我们需要增加我们的规则集。这可以通过Github的网站来完成。Github上是一个开源的平台，让许多开发人员分享他们的项目和应用程序。通过git命令使用clone选项，可以下载Github服务器上的任何内容。因此，我们将导入预定义的OWASP的ModSecurity规则到我们的服务器。我们可以通过下面的命令做到这一点。

```
git clone https://github.com/SpiderLabs/owasp-modsecurity-crs.git 

```

("https://github.com/SpiderLabs/owasp-modsecurity-crs.git")

![2014072015312341613.jpg](http://drops.javaweb.org/uploads/images/b5384efc0d3807d9bd6a2d64137ef95bb8a53ec4.jpg)

执行该命令后，OWASP的ModSecurity规则将在OWASP-MODSecurity-src目录下保存。可以通过ls命令如下进行查看。

![2014072015315319889.jpg](http://drops.javaweb.org/uploads/images/16c1db0a8b6c9c3864948a30785b62d0a82f5b76.jpg)

现在，我们必须重新命名OWASP-MODSecurity-src文件夹到ModScurity-CRS。这可以通过mv命令来完成。

```
mv owasp-modsecurity-crs modsecurity-crs

```

![2014072015322577770.jpg](http://drops.javaweb.org/uploads/images/f6064bca36afc415b00f9fac9cfd32b0625fe47e.jpg)

 我们可以通过运行ls命令验证。

**第5步**

我们必须将工作目录更改为mod security-crs。这可以通过cd命令来完成。

```
cd modsecurity-crs  

```

![2014072015331514069.jpg](http://drops.javaweb.org/uploads/images/998f83dc188904754e3abe1563a0c286fc94b15e.jpg)

`Modsecurity_crs_10_setup.conf`是ModSecurity工作的主配置文件。默认情况下，它带有.example扩展名。要初始化ModSecurity，我们要重命名此文件。我们可以用mv命令重命名。

```
mv modsecurity_crs_10_setup.conf.example modsecurity_crs_10_setup.conf 

```

![2014072015335461342.jpg](http://drops.javaweb.org/uploads/images/6645837a735237ca4e066a8993f86ce071088a10.jpg)

之后，我们要在Apache的配置文件中添加模块。要装入新的ModSecurity模块，编辑Apache的配置文件/etc/httpd/conf/httpd.conf。我们需要在终端中输入以下命令。

```
vi /etc/httpd/conf/httpd.conf 

```

![2014072015344238445.jpg](http://drops.javaweb.org/uploads/images/17841fc1df8a0c4bd98c7cf1f40ec273c7afe17f.jpg)

复制/粘贴以下内容到文件的末尾并保存文件。

```
<IfModule security2_module> 

Include modsecurity-crs/modsecurity_crs_10_config.conf

Include modsecurity-crs/base_rules/*.conf
</IfModule> 

```

![2014072015353128920.jpg](http://drops.javaweb.org/uploads/images/a66c4b85f2b0ef7406997d4b674c065d5f95d749.jpg)

我们将重新启动Apache服务器。

**第7步**

现在的ModSecurity已经成功配置了OWASP的规则，但能够按照我们的选择让它工作，我们将不得不作出一个新的配置文件与我们自己的规则，这就是所谓的白名单文件。通过这个文件，我们就可以控制整个防火墙，创建自己的ModSecurity规则。我们将在modsecurity.d目录中创建的。打开/通过下面的命令来创建这个文件。

```
vi /etc/httpd/modsecuirty.d/whitelist.conf 

```

![2014072015360510449.png](http://drops.javaweb.org/uploads/images/1d64ff6fb9589d41b60c7aa1a04da9c96fd63d0a.jpg)

复制下面的规则并保存到该文件中。

```
#Whitelist file to control ModSec 

<IfModule mod_security2.c> 
SecRuleEngine On 
SecRequestBodyAccess On  
SecResponseBodyAccess On 

SecDataDir /tmp 

</IfModule> 

```

![2014072015372027406.jpg](http://drops.javaweb.org/uploads/images/77263a76b6566b7b74d06e6e3216fdd5b0e47268.jpg)

现在，我们保存文件并重新启动Apache服务器。下面对各行的意义进行说明。

0x02 配置说明
---------

* * *

**1.SecRuleEngine**

是接受来自ModSecurity-CRS目录下的所有规则的安全规则引擎。因此，我们可以根据需求设置不同的规则。要设置不同的规则有以下几种。

**SecRuleEngine On**： 将在服务器上激活ModSecurity防火墙。它会检测并阻止该服务器上的任何恶意攻击。

**SecRuleEngine Detection Only**： 如果这个规则是在whitelist.conf文件中设置的，它只会检测到所有的攻击，并根据攻击产生错误，但它不会在服务器上阻止任何东西。

**SecRuleEngine Off:**： 这将在服务器上上停用ModSecurity的防火墙。

**2.SecRequestBodyAccess**： 它会告诉ModSecurity是否会检查请求。它起着非常重要的作用，当一个Web应用程序配置方式中，所有的数据在POST请求中。它只有两个参数，ON或OFF。我们可以根据需求设置。

**3.SecResponseBodyAccess**： 在whiltelist.conf文件，如果此参数设置为ON，然后ModeSecurity可以分析服务器响应，并做适当处理。它也有只有两个参数，ON和Off。我们可以根据求要进行设置。

**4.SetDataDirectory**： 在本文中，我们定义的ModSecurity的工作目录。该目录将作为ModSecurity的临时目录使用。

ModSecurity现在已经成功配置了OWASP的规则。现在，我们将测试对一些最常见的Web应用攻击。将测试ModSecurity是否挡住了攻击。

为了做到这一点，我们将尝试在一个存在存储性xss漏洞的网站上进行测试，我们已经配置ModSecurity。在一个网站中最常见的XSS漏洞的位置将是搜索框，用户可以在网站上搜索任何东西。如果恶意用户试图在搜索框中注入Java脚本或HTML脚本，它会在浏览器中执行。我们可以在搜索框中输入 。在正常情况下（当我们的服务器上的没有任何类型的应用程序防火墙），它会在网站显示一个弹窗上本。

如果在服务器上已经平配置ModSecurity，服务器会根据配置阻止XSS攻击，以及生成错误日志。

我们可以检查ModSecurity的错误日志文件。

在/var/logs/httpd/error_logs  
我们可以通过下面的命令来检查文件的最后更新的行。

```
tail –f /var/logs/httpd/error_logs 

```

![2014072015384576018.jpg](http://drops.javaweb.org/uploads/images/62bf86ade6ac3d65befed438a215775c07398347.jpg)

ModSecurity核心规则集（CRS）提供以下类别的保户来防止攻击。

```
•HTTP Protection （HTTP防御） - HTTP协议和本地定义使用的detectsviolations策略。 
•Real-time Blacklist Lookups（实时黑名单查询） -利用第三方IP信誉。 
•HTTP Denial of Service Protections（HTTP的拒绝服务保护） -防御HTTP的洪水攻击和HTTP  
Dos 攻击。  
•Common Web Attacks Protection（常见的Web攻击防护） -检测常见的Web应用程序的安全攻击。  
•Automation Detection（自动化检测） -检测机器人，爬虫，扫描仪和其他表面恶意活动。  
•Integration with AV Scanning for File Uploads（文件上传防病毒扫描） -检测通过Web应用程序上传的恶意文件。  
•Tracking Sensitive Data（跟踪敏感数据） -信用卡通道的使用，并阻止泄漏。  
•Trojan Protection（木马防护） -检测访问木马。  
•Identification of Application Defects （应用程序缺陷的鉴定）-应用程序的错误配置警报。  
•Error Detection and Hiding（错误检测和隐藏） -伪装服务器发送错误消息。

```

0x03 参考文章:
----------

* * *

https://www.owasp.org/index.php/Category:OWASP_ModSecurity_Core_Rule_Set_Project

http://spiderlabs.github.io/owasp-modsecurity-crs/  
http://www.modsecurity.org/demo/crs-demo.html

http://www.atomicorp.com/wiki/index.php/Mod_security

https://github.com/SpiderLabs/owasp-modsecurity-crs

https://www.owasp.org/index.php?title=Projects/OWASP_ModSecurity_Core_Rule_Set_Project/Releases/ModSecurity_2.0.6/Assessment&setlang=es