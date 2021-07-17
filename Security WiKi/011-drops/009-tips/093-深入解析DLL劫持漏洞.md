# 深入解析DLL劫持漏洞

**Author:Wins0n**

0x00 DLL劫持漏洞介绍
==============

* * *

### 0.1 漏洞简介

如果在进程尝试加载一个DLL时没有指定DLL的绝对路径，那么Windows会尝试去指定的目录下查找这个DLL；如果攻击者能够控制其中的某一个目录，并且放一个恶意的DLL文件到这个目录下，这个恶意的DLL便会被进程所加载，从而造成代码执行。这就是所谓的DLL劫持。

在Windows XP SP2之前，Windows查找DLL的目录以及对应的顺序如下：

1.  进程对应的应用程序所在目录
2.  当前目录（Current Directory）
3.  系统目录（通过 GetSystemDirectory获取）
4.  16位系统目录
5.  Windows目录（通过GetWindowsDirectory获取）
6.  PATH环境变量中的各个目录

在Windows下，几乎每一种文件类型都会关联一个对应的处理程序，当我们在资源管理器中打开某种特定类型的文件时，与之相关联的处理程序便会被执行，也就是会新建一个进程，进程默认的**Current Directory**（当前目录） 就是被打开文件所在的目录。 在Windows搜索DLL的这些目录中，攻击者最容易控制的当然是**Current Directory**。攻击者可以把恶意的DLL文件和目标文件（如WORD文档） 打包在一起，如果受害者进行解压操作，恶意DLL和目标文件就会位于同一个目录，攻击者可以十分方便的实施DLL劫持。

由于早期Windows查找DLL文件的顺序并不合理，可以想象DLL劫持漏洞伴随着Windows存在了相当长的时间。然而，在相当长的一段时间里DLL劫持漏洞并没有受到大家的关注，直到2010年8月，微软发布安全通报2269637，同时网上公布了大量受影响软件的名字， DLL劫持漏洞才开始进入大家的视野。

### 0.2 漏洞归类

DLL劫持漏洞翻译成英文叫做**DLL Hijacking Vulnerability**， CWE将其归类为**UntrustedSearch Path Vulnerability**。 如果想要去CVE数据库中搜索DLL劫持漏洞案例， 搜索这两个关键词即可。

### 0.3 缓解措施

从Windows XP SP2开始，**SafeDllSearchMode**默认会被开启。 SafeDllSearchMode的开启与否主要影响**Current Directory**（ 当前目录） 在搜索顺序中的位置。 开启SafeDllSearchMode后的DLL搜索顺序如下：

1.  进程对应的应用程序所在目录
2.  系统目录（ 通过**GetSystemDirectory**获取）
3.  16位系统目录
4.  Windows目录（通过**GetWindowsDirectory**获取）
5.  _当前目录_
6.  PATH环境变量中的各个目录

启用 SafeDllSearchMode 之后可以防范大部分 DLL 劫持，如系统 DLL 劫持。不过，如果进程尝试加载的 DLL 并不存在，那么进程仍然会尝试去当前目录加载这个 DLL ，这是 SafeDllSearchMode所无法防范的。不过微软引入了**SetDllDirectory**这个 API ，给这个 API 传递一个空字符串就可以将当前目录从 DLL 搜索顺序中排除掉。

> BOOL WINAPI SetDllDirectory(  
> _In_opt_LPCTSTR lpPathName  
> );  
> If the**lpPathName**parameter is an empty string (“”), the call removes the current directory  
> from the default DLL search order.

### 0.4 漏洞检查

使用 Sysinternals 工具包中的**Process Monitor**（ ProcMon ）可以十分方便的检测 DLL 劫持漏洞，只需要设置几个过滤参数即可。

*   ProcessName 目标进程的名字
*   Path 文件路径，可以设置为 begins with 当前目录所在路径
*   Result 结果，设置为 NAME NOT FOUND

0x01 DLL 劫持漏洞利用场景
=================

* * *

### 1.1 针对应用程序安装目录的 DLL 劫持

不管 SafeDllSearchMode 是否开启，在查找 DLL 时应用程序本身所在的目录都是最先被搜索的。因此如果能够放一个恶意的 DLL 文件到程序的安装目录，就可以利用 DLL 劫持漏洞来执行代码。

这种利用场景的要求相对较高，因为大部分程序默认安装到**%ProgramFiles%**或者是**%ProgramFiles(x86)%**。这两个目录都需要管理员权限才可以进行写入操作，也就是说在进行DLL 劫持之前，要求已经具有代码执行权限。基于这一原因，软件厂商一般不予处理此类问题。这种场景多被一些恶意代码所使用，对常用软件进行 DLL 劫持可以在一定程度替代自启动功能，同时，利用 白加黑 方式还能逃避安全软件的检测。此外，一些外挂或者破解程序也会采用这种方式进行 DLL 劫持，例如 QQ 的一些显 IP 插件就是通过劫持**msimg32.dll**来实现功能的。

### 1.2 针对文件关联的 DLL 劫持

在 Windows 下，我们平时使用的各种文件（如 MP3 音乐、 DOC 文档、 PDF 文档、 MKV 视频等）都有一个与之关联的默认处理软件。当在资源管理器中打开某种特定类型的文件时，操作系统会自动创建一个进程来处理这个文件，进程对应的程序就是该文件类型关联的默认处理程序，进程的**当前目录**就是被打开文件所在的目录。

例如，如果 Adobe Acrobat DC 关联了 .PDF 文件类型，那么打开 PDF 文件时就会自动创建一个Acrobat.exe 进程，进程的当前目录（**Current Directory**）就是 PDF 文件所在的目录。如果进程尝试加载一个不存在的 DLL ，根据默认的 DLL 搜索顺序，进程最终会搜索到 PDF 文件所在目录（即当前目录），如果该目录下恰好就存在有一个同名的 DLL ，那么这个 DLL 就会被进程所加载。这就是所谓的**文件关联型 DLL 劫持**。

相对于**针对应用程序安装目录的 DLL**劫持，**针对文件关联的 DLL 劫持**的利用条件十分简单，只要放一个恶意的 DLL 就行了。由于实施这种 DLL 劫持不需要其他先决条件，**许多厂商关注并承认该利用场景下的 DLL 劫持漏洞**。

许多流行软件可能仍然存在有这种 DLL 劫持漏洞：笔者在 2015 年给 12 月给 Adobe 报告了 AdobeAcrobat DC 15.009.20077 中存在的一个 DLL 劫持漏洞（ CVE-2016-0947 ），该漏洞由 Acrobat.exe进程加载不存在的 updaternotifications.dll 所引起。此外，去 CVE 漏洞库搜索**DLL Hijacking**或者**Untrusted Search Path**也能找到很多案例。

### 1.3 针对安装程序的 DLL 劫持

许多应用程序的安装包程序也存在有 DLL 劫持漏洞，这种场景与**针对应用程序安装目录的DLL劫持**比较类似，本来也没有什么特殊之处，不过结合后文提到的浏览器自动下载漏洞，其利用条件又变得相对简单了。

这里以 Notepad++ 最新的安装包 npp.6.9.Installer.exe 为例来进行讲解。启动**ProcMon**并设置好过滤器，可以看到 npp.6.9.Installer.exe 运行后尝试加载了许多 DLL ，这些都是第一次加载时没有加载成功的。

![p1](http://drops.javaweb.org/uploads/images/9333b0ced1d2e3b8d84dbaf5adf87d6d15e212bc.jpg)

仔细观察进程尝试加载这些 DLL 时产生的调用栈，会发现有的调用栈中存在有**LoadLibrary(Ex)**，而有的调用栈中却没有。这里选取 Version.dll 和 SHFOLDER.dll 来进行对比说明。

*   npp.6.9.Installer.exe 在尝试加载 Version.dll 时产生的调用栈中并没有**LoadLibrary(Ex)**，这是因为 DLL 并不是被进程动态加载的，而是因为应用程序的导入表直接或者间接导入了这个DLL 。在这种利用场景下，伪造 DLL 的导出表最好与被伪造 DLL 的导出表完全一致，否则DLL 可能无法被进程成功加载（会弹出错误提示消息框）。有一个叫做**AheadLib**的工具可以十分方便的生成此类 DLL 的源文件。
    
    ```
    0 fltmgr.sys FltAcquirePushLockShared + 0x907
    1 fltmgr.sys FltIsCallbackDataDirty + 0x1f3d
    2 fltmgr.sys FltDeletePushLock + 0x64f
    3 ntoskrnl.exe MmCreateSection + 0x25b1
    4 ntoskrnl.exe SeQueryInformationToken + 0xe3e
    5 ntoskrnl.exe ObOpenObjectByName + 0x306
    6 ntoskrnl.exe NtOpenProcessTokenEx + 0x326
    7 ntoskrnl.exe KeSynchronizeExecution + 0x3a23
    8 ntdll.dll ZwQueryAttributesFile + 0xa
    9 wow64.dll Wow64EmulateAtlThunk + 0xd2b1
    10 wow64.dll Wow64SystemServiceEx + 0xd7
    11 wow64cpu.dll TurboDispatchJumpAddressEnd + 0x2d
    12 wow64.dll Wow64SystemServiceEx + 0x1ce
    13 wow64.dll Wow64LdrpInitialize + 0x42a
    14 ntdll.dll RtlUniform + 0x6e6
    15 ntdll.dll EtwEventSetInformation + 0x186f8
    16 ntdll.dll LdrInitializeThunk + 0xe
    17 ntdll.dll ZwQueryAttributesFile + 0x12
    18 ntdll.dll aullrem + 0x1f1
    19 ntdll.dll aullrem + 0x6cb
    20 ntdll.dll aullrem + 0x565
    21 ntdll.dll RtlEncodeSystemPointer + 0x404
    22 ntdll.dll RtlSetBits + 0xf0
    23 ntdll.dll RtlSetBits + 0x16b
    24 ntdll.dll RtlSetBits + 0x60
    25 ntdll.dll RtlSetThreadPoolStartFunc + 0x3a1
    26 ntdll.dll RtlSetUnhandledExceptionFilter + 0x50
    27 ntdll.dll LdrInitializeThunk + 0x10
    
    ```
*   npp.6.9.Installer.exe 在尝试加载 SHFOLDER.dll 时产生的调用栈中存在有**LoadLibrary(Ex)**，说明这个 DLL 是被进程所动态加载的。在这种利用场景下，伪造的 DLL文件不需要存在任何导出函数即可被成功加载，即使加载后进程内部出错，也是在 DLL 被成功加载之后的事情。
    
    ```
    0 fltmgr.sys FltAcquirePushLockShared + 0x907
    1 fltmgr.sys FltIsCallbackDataDirty + 0x1f3d
    2 fltmgr.sys FltDeletePushLock + 0x64f
    3 ntoskrnl.exe MmCreateSection + 0x25b1
    4 ntoskrnl.exe SeQueryInformationToken + 0xe3e
    5 ntoskrnl.exe ObOpenObjectByName + 0x306
    6 ntoskrnl.exe NtOpenProcessTokenEx + 0x326
    7 ntoskrnl.exe KeSynchronizeExecution + 0x3a23
    8 ntdll.dll ZwQueryAttributesFile + 0xa
    9 wow64.dll Wow64EmulateAtlThunk + 0xd2b1
    10 wow64.dll Wow64SystemServiceEx + 0xd7
    11 wow64cpu.dll TurboDispatchJumpAddressEnd + 0x2d
    12 wow64.dll Wow64SystemServiceEx + 0x1ce
    13 wow64.dll Wow64LdrpInitialize + 0x42a
    14 ntdll.dll RtlUniform + 0x6e6
    15 ntdll.dll EtwEventSetInformation + 0x186f8
    16 ntdll.dll LdrInitializeThunk + 0xe
    17 ntdll.dll ZwQueryAttributesFile + 0x12
    18 ntdll.dll aullrem + 0x1f1
    19 ntdll.dll aullrem + 0x6cb
    20 ntdll.dll aullrem + 0x565
    21 ntdll.dll RtlLookupAtomInAtomTable + 0x35a
    22 ntdll.dll RtlUlonglongByteSwap + 0x671
    23 KernelBase.dll LoadLibraryExW + 0x243
    24 KernelBase.dll LoadLibraryExA + 0x26
    25 kernel32.dll LoadLibraryA + 0x31
    
    ```

### 1.4 Microsoft Edge 与 Google Chrome 的自动下载漏洞

通过 iframe 可以触发 Microsoft Edge 和 Google Chrome 的自动下载功能，这一特性被[@HaifeiLi](https://twitter.com/HaifeiLi)认为是一个安全漏洞，其在 Twitter 上发表了很多关于该漏洞的推文，甚至抱怨 Chrome 和 Edge 团队忽视这个漏洞的存在。在 HaifefiLi 的长期呼吁下， Chrome 最终在 48.0.2564.82 版本中修复了这个漏洞，而截至笔者撰文时 Edge 似乎仍然没有修复该漏洞。

Edge 浏览器的默认下载目录为`C:\Users\<Username>\Downloads`，通过 Edge 下载的文件默认都会保存在这个目录下。可以利用 Edge 的自动下载漏洞下载一个恶意的 DLL 文件（如Version.dll ）到这个目录下，然后利用页面超时自动跳转功能让 Edge 跳转到正常页面来诱导用户下载一个正常的安装文件，当用户运行安装程序时恶意的 DLL 文件便会被进程加载。

测试浏览器自动下载漏洞的 HTML 测试代码如下所示：

```
<html>
    <head>
        <title>Windows Update</title>
    </head>
    <body>
        <iframe src="evil.dll"></iframe>
        <script>
            setTimeout( function () {
                    window.location = "https://get.adobe.com/reader"
                }, 5000);
        </script>
    </body>
</html>

```

在 Windows 10 下使用 Edge 打开这个 HTML 页面，可以看到 DLL 文件被自动下载到了本地的下载目录中。不过由于 DLL 没有有效的数字签名，所以 Edge 会提示这个文件可能存在风险。

![p2](http://drops.javaweb.org/uploads/images/aaec09e8f3e387c3bd869762b826d3be4e671640.jpg)

如果 DLL 文件具有有效的数字签名，那么 Edge 就不会这样提示了。在最新版本的 GoogleChrome （ 48.0.2564.116 m ）上测试发现，不管 DLL 是否具有有效的数字签名， DLL 文件下载之后都需要用户手工确认才会保存，否则会被删除。 Chrome 和 Edge 的测试结果汇总如下：

![p3](http://drops.javaweb.org/uploads/images/a91b37833d07422321efb75f23e95fac108e5021.jpg)

浏览器的自动下载漏洞还是十分危险的，攻击者甚至只需要诱导用户下载一个恶意的 DLL ，以后用户在下载目录中执行各种程序时都有可能加载这个 DLL 。此外，安装程序一般都会请求管理员权限，对于恶意的 DLL 来说管理员权限似乎是与生俱来的。

0x02 非典型漏洞 CVE-2016-0041 分析
===========================

* * *

微软安全公告 MS16-014 中的描述表明其修复了一个 CVE-ID 为 CVE-2016-0041 的 DLL 劫持漏洞。漏洞详情为： Windows 10 下的 URLMON.dll 文件存在加载 phoneinfo.dll 的代码，而 Windows 10本身并不携带这个 phoneinfo.dll 文件，并且在查找 DLL 时使用的是标准的目录搜索顺序，所以这里会导致 DLL 劫持漏洞。这个漏洞的独特之处在于其存在于操作系统本身，所以在 Windows 10下，只要是调用了 URLMON.dll 中能够触发漏洞代码的 API 的软件都会受到这个漏洞的影响。笔者在 2015 年底也发现了也发现了这个漏洞，同时确认 Foxit Reader 7.2.8.1124 受到该漏洞的影响，并将其报告给了 Foxit Software 。

### 2.1 漏洞分析

在发现这个漏洞时，笔者发现网上很少有关于 phoneinfo.dll 文件的介绍，只有[@tombkeeper](https://twitter.com/tombkeeper)在**Sexrets of LoadLibrary**中提到了这个文件。 TK 指出 IE11 running on Windows 10 TP 9926 会尝试加载 phoneinfo.dll ，而 IE 的当前目录就是桌面，所以如果放一个 phoneinfo.dll 到桌面上的话，在启动 IE 时这个 DLL 便会被加载。

Greg Linares 在 SRT-VR-24DEC2015 中指出 Windows10 的 URLMON.dll 中存在两处加载phoneinfo.dll 的地方，可能是 DLL 文件的版本不一样，笔者找到的代码与之存在一些细微差异。笔者在分析 11.0.10240.16384 版本的 URLMON.dll 时找到的反汇编代码如下所示：

*   下面的代码位于**BuildUserAgentStringMobileHelper**中：
    
    ```
    .text:1A4636A1 loc_1A4636A1:
    .text:1A4636A1 mov eax, pfnQueryPhoneInformation
    .text:1A4636A6 mov [ebp+pszValue], 0
    .text:1A4636AD mov [ebp+szSrc], eax
    .text:1A4636B3 test eax, eax ;  判断 eax 寄存器的值是否为 0
    .text:1A4636B5 jnz loc_1A48FC97 ;  如果不为 0 则跳转
    .text:1A4636BB push eax ; dwFlags = 0
    .text:1A4636BC push eax ; hFile = 0
    .text:1A4636BD push offset aPhoneinfo_dll ; "phoneinfo.dll"
    .text:1A4636C2 call ds:__imp__LoadLibraryExW@12 ; LoadLibraryExW(x,x,x)
    .text:1A4636C8 test eax, eax
    .text:1A4636CA jnz loc_1A48FC78
    
    ```
*   下面的代码位于**_QueryPhoneInformationA**中：
    
    ```
    .text:1A461B93 mov edi, pfnQueryPhoneInformation
    .text:1A461B99 mov byte ptr [ebx], 0
    .text:1A461B9C test edi, edi
    .text:1A461B9E jnz loc_1A48EE56
    .text:1A461BA4 push edi ; dwFlags
    .text:1A461BA5 push edi ; hFile
    .text:1A461BA6 push offset aPhoneinfo_dll ; "phoneinfo.dll"
    .text:1A461BAB call ds:__imp__LoadLibraryExW@12 ; LoadLibraryExW(x,x,x)
    .text:1A461BB1 test eax, eax
    .text:1A461BB3 jnz loc_1A48EE34
    
    ```

这里加载**phoneinfo.dll**的代码为 LoadLibraryExW("phoneinfo.dll", NULL, 0) 。因为这 里 dwFlags 的值为 0 ，所以使用标准的 DLL 搜索顺序；由于 Windows 10 上并不存在 phoneinfo.dll 这个文件，所以进程最终会尝试加载当前目录下的 DLL 。

这里简单分析一下受该漏洞影响的 Foxit Reader 。当在 Windows 10 下打开一个 PDF 文件时，进程 FoxitReader.exe 会加载当前目录下的 phoneinfo.dll 文件，对应的调用栈如下所示：

```
......
16  KernelBase.dll LoadLibraryExW + 0x124
17  urlmon.dll Ordinal523 + 0x6f1
18  urlmon.dll Ordinal492 + 0x941
19  urlmon.dll Ordinal492 + 0x165
20  urlmon.dll Ordinal445 + 0x2e0
21  urlmon.dll RegisterFormatEnumerator + 0xe2
22  urlmon.dll UrlMkGetSessionOption + 0xcf
23  FoxitReader.exe CertFreeCertificateChainEngine + 0x72fbef
24  FoxitReader.exe CertFreeCertificateChainEngine + 0x70bbc2
25  FoxitReader.exe CertFreeCertificateChainEngine + 0x70f61e
26  FoxitReader.exe CertFreeCertificateChainEngine + 0x6f9f9c
27  user32.dll Ordinal2535 + 0x83
28  user32.dll GetScrollInfo + 0x1e8
29  user32.dll DispatchMessageW + 0x28d
30  user32.dll DispatchMessageW + 0x10
31  FoxitReader.exe FoxitReader.exe + 0x2d1f1b
32  FoxitReader.exe FoxitReader.exe + 0x2da62d
33  FoxitReader.exe FoxitReader.exe + 0x882a36
34  FoxitReader.exe FoxitReader.exe + 0x1866d1
35  FoxitReader.exe FoxitReader.exe + 0x173286
36  FoxitReader.exe FoxitReader.exe + 0x173563
37  FoxitReader.exe FoxitReader.exe + 0x21483f
38  FoxitReader.exe FoxitReader.exe + 0x217726
39  FoxitReader.exe FoxitReader.exe + 0x1e4922
40  FoxitReader.exe FoxitReader.exe + 0x1f4aba
41  FoxitReader.exe FoxitReader.exe + 0x1e8d6a
42  FoxitReader.exe FoxitReader.exe + 0x1eb562
43  FoxitReader.exe CertFreeCertificateChainEngine + 0x91e56c
44  FoxitReader.exe FoxitReader.exe + 0x46cd8e
45  kernel32.dll BaseThreadInitThunk + 0x24
46  ntdll.dll RtlInitializeCriticalSectionAndSpinCount + 0x29e
47  ntdll.dll RtlInitializeCriticalSectionAndSpinCount + 0x26d

```

结合 IDA 或者 Windbg 进行分析，可以知道这里的调用路径为：

```
UrlMkGetSessionOption
└--> GetUserAgentString
     └--> GetUserAgentStringForMode
          └--> InitUserAgentGlobals
               └--> BuildUserAgentStringMobileHelper
                    └-->LoadLibraryExW

```

即 Foxit Reader 因为调用了 URLMON.dll 中的 UrlMkGetSessionOption 函数，导致其受到 DLL 劫持漏 洞的影响。在 IDA 中使用交叉引用功能进行回溯，可以找到其他能够触发该漏洞的路径，**Greg Linares**给出了另外两个路径：

*   路径1
    
    ```
    ┌─────────────────────────────────────────────────────┐
    │          CINetHttpEdge::SetOptionUserAgent          │
    │             CINetHttp::SetOptionUserAgent           │
    │ CIEBrowserModeFilter::collectCacheEntryInfoCallback │
    └─────────────────────────────────────────────────────┘
    └--> MapBrowserEmulationStateToUserAgent (Ordinal 445)
         └--> InitUserAgentGlobals (Ordinal 492)
              └--> BuildUserAgentStringMobileHelper
    
    ```
*   路径2
    
    ```
    ┌─────────────────────────────────────┐
    │ ObtainUserAgentString (Ordinal 211) │
    │         GetUserAgentString          │
    └─────────────────────────────────────┘
    └--> InitUserAgentGlobals (Ordinal 492)
        └--> BuildUserAgentStringMobileHelper
    
    ```

**Greg Linares**同时也指出了他们发现的其他受该漏洞影响的软件：

*   Internet Explorer 没有命令行参数的情况下（例如双击并打开 IE ）
*   Skype 启动的时候
*   OneDrive 同步以及更新的时候（无需用户交互）
*   Visual Studio 2015 微软账户更新或者同步的时候

### 2.2 补丁分析

更新后的 URLMON.dll 文件在调用 LoadLibraryEx 加载 phoneinfo.dll 时将 dwFlags 参数值指定为 0x800 ，即**LOAD_LIBRARY_SEARCH_SYSTEM32**，表示只搜索 System32 目录。对应的代码为`LoadLibraryExW(L"phoneinfo.dll", NULL, LOAD_LIBRARY_SEARCH_SYSTEM32)`，反汇 编代码如下：

```
.text:1A46386B push 800h ; dwFlags
.text:1A463870 push eax ; hFile
.text:1A463871 push offset aPhoneinfo_dll ; "phoneinfo.dll"
.text:1A463876 call ds:__imp__LoadLibraryExW@12 ; LoadLibraryExW(x,x,x)

```

0x03 DLL 劫持漏洞缓解措施
=================

* * *

DLL 劫持漏洞在未来可能仍然会影响着许多软件或者操作系统组件，亦或是与其他漏洞相结合以 衍生出新的攻击方法。尽管目前没有一个完美的方法（_No Silver Bullet_）可以防止软件受到 DLL 劫持漏洞的影响，但是开发人员仍然可以采取各种措施来缓解 DLL 劫持漏洞带来的影响。

### 3.1 基本缓解措施

*   在加载 DLL 时尽量使用 DLL 的绝对路径
*   调用`SetDllDirectory(L"")`把**当前目录**从 DLL 搜索目录中排除
*   使用**LoadLibraryEx**加载 DLL 时，指定`LOAD_LIBRARY_SEARCH_`系列标志

此外，进程也可以尝试去验证 DLL 的合法性，例如是否具有自家的合法数字签名、是否是合法的系统 DLL 文件等。

### 3.2 Windows Edge 缓解措施

最新版本的 Edge 提供了一种对抗 DLL 劫持（注入）的缓解措施：只有拥有微软签名以及 WHQL （ Windows Hardware Quality Lab ）签名的 DLL 模块才会被 Edge 加载，而且这套机制是在 操作系统内核中实现的。

关于这一缓解措施的细节分析，可以阅读**Paul Rascagneres**的文章**MICROSOFT EDGE BINARY INJECTION MITIGATION OVERVIEW**。

0x04 Acknowledges
=================

* * *

感谢[TK](http://weibo.com/tombkeeper)在行文思路上的建议；同时，在本文的写作过程中参考了以下资料，在此亦表示感谢。

*   MSDN ，[Dynamic-Link Library Security](https://msdn.microsoft.com/library/ff919712)
*   MSDN ，[Dynamic-Link Library Search Order](https://msdn.microsoft.com/EN-US/library/windows/desktop/ms682586(v=vs.85).aspx)
*   Microsoft ，[安全通报 (2269637)](https://technet.microsoft.com/library/security/2269637)
*   CWE ，[CWE-426: Untrusted Search Path](https://cwe.mitre.org/data/definitions/426.html)
*   CWE ，[CWE-427: Uncontrolled Search Path Element](https://cwe.mitre.org/data/definitions/427.html)
*   Yonsm ，[AheadLib 2.2.150 - 自动生成一个特洛伊 DLL 分析代码的工具](http://yonsm.net/aheadlib/)
*   HaifeiLi ，[Watch your Downloads: the risk of the “auto-download” feature on Microsoft Edge and Google Chrome](http://justhaifei1.blogspot.com/2015/10/watch-your-downloads-risk-of-auto.html)
*   Microsoft ，[安全公告 MS16-014](https://technet.microsoft.com/zh-cn/library/security/ms16-014.aspx)
*   tombkeeper ，[Sexrets of LoadLibrary](https://www.google.co.jp/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwit8d7E3J7LAhWBg6YKHaBgAGEQFggcMAA&url=https://cansecwest.com/slides/2015/Sexrets_of_LoadLibrary__Yang_yu%2520_CSW2015.pdf&usg=AFQjCNH8T-9Papzl-ger6sttdnYoIupuTA)
*   Greg Linares ，[SRT-VR-24DEC2015](https://github.com/CyberPoint/advisories/blob/master/SRT-VR-24DEC2015.txt)
*   Wins0n ，[CVE-2016-0041 Windows 10 PhoneInfo.dll Hijacking Vulnerability](http://www.programlife.net/cve-2016-0041-windows-10-phoneinfo-dll-hijacking-vulnerability.html)
*   Microsoft Edge Dev Blog ，[Protecting Microsoft Edge against binary injection](https://blogs.windows.com/msedgedev/2015/11/17/microsoft-edge-module-code-integrity/)
*   Paul Rascagneres ，[MICROSOFT EDGE BINARY INJECTION MITIGATION OVERVIEW](http://www.sekoia.fr/blog/microsoft-edge-binary-injection-mitigation-overview/)