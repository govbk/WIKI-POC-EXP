# IE安全系列之——RES Protocol

RES是IE支持的特殊Protocol。它用于从二进制文件中读取资源信息并展示在网页中。由于现在RES已经被微软大老爷削弱成狗，所以本来准备拆两篇的文章干脆就合在一篇写了。文中除非有特殊提示，否则都以IE11为准。

![p1](http://drops.javaweb.org/uploads/images/6b914fb837bc87573564280089b57ac2304566c5.jpg)

0x00 Res Protocol ABC
=====================

* * *

res Protocol用于从一个文件里面提取指定资源。语法为：`res://sFile[/sType]/sID`

各Token含义：

*   sfile：百分号编码。包含资源的文件路径。
*   sType：可选的，字符串或者数字，表明资源类型。可以是任意亿一个FindResource可以识别的预定义类型。如果指定了数字类型的值，则需要跟随一个#字符。未指定时默认RT_HTML或RT_FILE。
*   sID：字符或数字类型。资源标识符。如果指定了数字值，需要跟随一个#。

具体的可见参考资料1，不翻译了……

0x01 新窗口中Res Protocol的加载
========================

* * *

在新窗口打开res protocol的时候，res Protocol的dll会被载入内存。Res protocol加载的dll使用LoadLibraryExW读入，一些常见的res protocol，例如`res://ieframe.dll/`的读入时并没有使用完整的路径。虽然可以考虑DLL劫持问题，但program files和system32均为administrator权限，所以还是不要想了……

在新窗口加载res protocol URL时，最终解析、加载资源并绑定的工作由CResProtocol类的CResProtocol::DoParseAndBind完成。

```
0:009> kvn 1
# ChildEBP RetAddr  Args to Child              
00 072fa464 664b2ad5 0f806814 00000000 00000060 KERNEL32!LoadLibraryExWStub (FPO: [Non-Fpo])

0:009> dds esp
072fa468  664b2ad5 MSHTML!CResProtocol::DoParseAndBind+0x103
072fa46c  0f806814

0:009> du 0f806814 
0f806814  "ieframe.dll"

```

代码1：CResProtocol::DoParseAndBind正在使用LoadLibraryEx加载ieframe.dll

DoParseAndBind处理ResProtocol时的具体做法：

**a、**Crack Res URL。

Res URL格式如我们之前所述。**另外，res protocol的第一个path部分不允许有“/”。因为微软在crack URL时hardcode直接wcschr搜索的L'/'。**解析字符串时遇到的第一个“/”（除了res://的//）后面只能是restype，或者id。

![p2](http://drops.javaweb.org/uploads/images/c53e0fd73c931441e83bc33a946ddec804612289.jpg)

**b、**传入的res protocol 路径长度大于MAX_PATH时，返回E_FAIL，所以Fuzz这里意义也不是多大了。Win95+IE4.0时候这里有漏洞，这个判断也是自那个漏洞之后补上的。

![p2](http://drops.javaweb.org/uploads/images/7782a6b04555a2b1dbc947294a08c9f5862b5c5f.jpg)

**c、**LoadLibraryEx载入资源DLL，Flag为DONT_RESOLVE_DLL_REFERENCES | LOAD_LIBRARY_AS_DATAFILE。所以也不要考虑重复利用载入的DLL了，因为DLL被映射到了只读内存中。并不会被执行。

![p3](http://drops.javaweb.org/uploads/images/e637fbf662e1b98a0f869b326c598f91937872f5.jpg)

```
0:009> !address 67370000   
Usage:                  Image
Base Address:           67370000
End Address:            67371000
Region Size:            00001000
State:                  00001000    MEM_COMMIT
Protect:                00000002    PAGE_READONLY
Type:                   01000000    MEM_IMAGE
Allocation Base:        67370000
Allocation Protect:     00000080    PAGE_EXECUTE_WRITECOPY
Image Path:             F:\WINDOWS\SYSTEM32\IEFRAME.dll
Module Name:            IEFRAME
Loaded Image Name:      F:\WINDOWS\SYSTEM32\IEFRAME.dll
Mapped Image Name:      
More info:              lmv m IEFRAME
More info:              !lmi IEFRAME
More info:              ln 0x67370000
More info:              !dh 0x67370000

```

代码2：分配在只读页上的ieframe.dll

0x02 曾经的可行方法：new Image判断res
===========================

* * *

![p4](http://drops.javaweb.org/uploads/images/91c1eef4b2474a9d81ad16f0c05c87158b732709.jpg)

确实迟了一些，不过为了弥补，我接下来会分析为什么用不了了

![p5](http://drops.javaweb.org/uploads/images/fb1f6bf4fb1b73f5b4bd0b95f75a43327e59ab4e.jpg)

曾经在Angler Exploit Kit中，攻击者用Res Protocol玩出了一堆花样。使用如下代码，可以判断本地文件是否存在。

```
function my_onError(){alert("file not exists!!");}
function Check(s) {
    x = new Image();
    x.onerror=my_onError; 
    x.src = s;
    document.body.appendChild(x);
    return 0;
}
Check("res://f:\\node\\asoehook2.dll/#2/#102")

```

代码3：使用Res Protocol检查本地文件  
（不过在最新的IE11中，这个判断并不能在http/https/ftp下进行，也不能在任何网络相关的protocol打开的about:blank或者iframe 的about：blank中进行。下节说）

![p6](http://drops.javaweb.org/uploads/images/d3722f4cef2d91666460263729cb474378d74b4f.jpg)

为啥Image可以做到这个呢？让我们仔细看一下。猜也能猜得到，new Image事实上创建了一个CImgElement。

```
Breakpoint 10 hit
eax=11fe3bc0 ebx=662016f0 ecx=11fe3bc0 edx=000001bc esi=65eb2270 edi=072fa3c8
eip=66201739 esp=072fa3a4 ebp=072fa3b4 iopl=0         nv up ei pl nz na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00200206
MSHTML!CImgElement::CImgElement:
66201739 8bff            mov     edi,edi
0:009> kvn
 # ChildEBP RetAddr  Args to Child              
00 072fa3a0 66201718 0000003d 06a08000 662016f0 MSHTML!CImgElement::CImgElement (FPO: [Non-Fpo])
01 072fa3b4 6625110b 072fa440 06a08000 072fa3ec MSHTML!CImgElement::CreateElement+0x28 (FPO: [Non-Fpo])
02 072fa3f0 663aa61a 06a08000 11fe8a00 00000000 MSHTML!CreateElement+0xab (FPO: [Non-Fpo])
03 072fa500 664c4bb9 0000003d 072fa524 00000000 MSHTML!CMarkup::CreateElement+0xee (FPO: [Non-Fpo])
04 072fa548 664c49a0 06a7ee10 06920000 0bb24420 MSHTML!CImageElementFactory::create+0x49 (FPO: [Non-Fpo])
05 072fa5b8 664c48e4 00000001 11fe8a00 072fa5d8 MSHTML!CImgElement::Var_create+0x89 (FPO: [Non-Fpo])
06 072fa5e0 552f3b7e 189114e0 01000001 163c3d20 MSHTML!CFastDOM::CHTMLImageElement::DefaultEntryPoint+0x44 (FPO: [Non-Fpo])
07 072fa648 552f8f53 189114e0 01000001 163c3d20 jscript9!Js::JavascriptExternalFunction::ExternalFunctionThunk+0x18e (FPO: [Non-Fpo])

```

代码4： CImgElement的创建

然后，为Image指定src后，整个流程如下：

```
CImgElement::OnPropertyChange ---> CImgHelper::SetImgSrc ---> CImgHelper::FetchAndSetImgCtx

```

在早期的IE中，这一套流程下来并没有认为res是不让加载的，所以能够触发onerror事件。但是，使用file:///的src不可判断本地文件是否存在。这就使得res判断成为比较独特的存在。

就像http下并不能通过file protocol或者UNC访问本地文件（例如上述代码Check("file:///f:/yy.jpg")不会抛出onerror事件），而如果在非http/https/ftp网站打开的about:blank中还是可以使用的。

上述描述在不过在最新的IE中无效了，那是因为微软的LMZL策略。

0x03 Local Machine Zone Lockdown
================================

* * *

我也就不贴到最后的参考连接里面了，直接贴这儿好了：  
[https://technet.microsoft.com/en-us/library/cc782928(v=ws.10).aspx](https://technet.microsoft.com/en-us/library/cc782928(v=ws.10).aspx)

LMZL是微软搞出来的一个安全策略，简单的说就是阻止互联网内容访问本地内容，照理来说，在Windows XP SP2的时候就已经有这个功能了，但是直到多年以后，我在IE8上实验，还是能用RES访问本地资源。

微软的行踪一向很谜。这个举动也相当的谜。RES Protocol的当作本地文件处理的逻辑为什么没加？观察IE8和IE11处理相同本地数据的代码可以得出一个基础结论——应该是忘了。

0x04 IE11下的RES Protocol（IMG src中）为什么失效了？
========================================

* * *

首先，在IE中我输入了下面的代码。不出意外地，document.body.appendChild(iii)之后，元素添加成功，但是图片没显示出来，同时，onerror也没有触发。我开始以为是因为f:\asoehook2.dll存在的缘故。结果换了个随便打的地址加上Res Protocol，还是没有触发onerror。

![p7](http://drops.javaweb.org/uploads/images/ba064c6a8ac2a42fe193bbd97f1538e1a3fd5544.jpg)

同比在IE8下的Res Protocol，则既能显示图片，又能触发onerror。

![p8](http://drops.javaweb.org/uploads/images/3c6977ad17452d1106bebb07cec106cbf6257fbc.jpg)

于在IE11下，Img SRC指定为RES Protocol时，Img显示的是一个透明的方块，所以先怀疑这些点：下载是否出问题了？在跟踪下载栈之后，发现下载和IE8的几乎一模一样。

```
ChildEBP RetAddr  
039e85a4 764c14a2 urlmon!CBSCHolder::OnProgress(
            unsigned long ulProgress = 0x338, 
            unsigned long ulProgressMax = 0x338, 
            unsigned long ulStatusCode = 4, 
            wchar_t * szStatusText = 0x0bbc2ce8 "res://f:\asoehook2.dll/#2/#102")+0x50 [d:\blue\inetcore\urlmon\mon\mpxbsc.cxx @ 807]
039e85dc 764c46e1 urlmon!CBinding::OnTransNotification(
            tagBINDSTATUS NotMsg = <Value unavailable error>, 
            unsigned long dwCurrentSize = 0x338, 
            unsigned long dwTotalSize = 0x338, 
            wchar_t * pwzStr = 0x00000000 "", 
            HRESULT hrINet = 0x00000000)+0x35b [d:\blue\inetcore\urlmon\trans\cbinding.cxx @ 2676]
039e8610 764c4458 urlmon!CBinding::ReportData(
            unsigned long grfBSCF = 0xd, 
            unsigned long ulProgress = 0x338, 
            unsigned long ulProgressMax = 0x338)+0xa1 [d:\blue\inetcore\urlmon\trans\cbinding.cxx @ 5451]
039e8638 764c43ec urlmon!COInetProt::ReportData(
            unsigned long grfBSCF = 0xd, 
            unsigned long ulProgress = 0x338, 
            unsigned long ulProgressMax = 0x338)+0x54 [d:\blue\inetcore\urlmon\trans\prothndl.cxx @ 1863]
039e8674 764c4303 urlmon!CTransaction::DispatchReport(
            tagBINDSTATUS NotMsg = BINDSTATUS_ENDDOWNLOADDATA (0n6), 
            unsigned long grfBSCF = 0xd, 
            unsigned long dwCurrentSize = 0x338, 
            unsigned long dwTotalSize = 0x338, 
            wchar_t * pwzStr = 0x00000000 "", 
            HRESULT hresult = 0x00000000)+0x19e [d:\blue\inetcore\urlmon\trans\transact.cxx @ 3153]
(Inline) -------- urlmon!CTransaction::DispatchPacket+0x23 [d:\blue\inetcore\urlmon\trans\transact.cxx @ 3278]
(Inline) -------- urlmon!CTransaction::OnINetCallback+0x116 [d:\blue\inetcore\urlmon\trans\transact.cxx @ 3356]

```

二者都成功地获取到了所需的资源，看来这里可以先排除。

然后，让我们再追踪一下事件。给`MSHTML!CImgHelper::Fire_onerror`下断点，为了确认下我下的对不对，我修改了`iii.src=“aa”`，这时，Fire_onerror成功触发。

![p9](http://drops.javaweb.org/uploads/images/46155a5fe151dba4bc6d88fe9af79c74a6eaaf6e.jpg)

图：给iii的src传入非res Protocol时，onerror事件就能成功触发。

而在IE11下指定Res Protocol时，Fire_onerror却始终无法断到。这可以证明一个猜想：如果IE禁止RES Protocol用在IMG中，那么这个禁止逻辑可能不是在事件里面去处理的。

对比在IE8下，即使使用Res Protocol，Fire_onerror仍然可以断到：

![p10](http://drops.javaweb.org/uploads/images/faac38e85753b032a0c0554fa803883c91a231d9.jpg)

目标放在Fire_onerror的前后两层。上一层OnDwnChan看起来并不是多相关，再向上一层，CImgHelper：：SetImgCtx里首先有了一些不一样的地方。

```
0:008> 
eax=00000000 ebx=071b2930 ecx=039e9cb0 edx=00000000 esi=00000000 edi=00000000
eip=639c17ce esp=039e9c9c ebp=039e9cd0 iopl=0         nv up ei pl nz ac pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000216
MSHTML!CImgHelper::SetImgCtx+0x11:
639c17ce e868feffff      call    MSHTML!CImgHelper::CScriptCalloutProtection::CScriptCalloutProtection (639c163b)
0:008> 
eax=039e9cb0 ebx=071b2930 ecx=071b2934 edx=071b2930 esi=00000000 edi=00000000
eip=639c17d3 esp=039e9ca0 ebp=039e9cd0 iopl=0         nv up ei pl nz na po nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000202
MSHTML!CImgHelper::SetImgCtx+0x16:
639c17d3 33f6            xor     esi,esi
0:008> 
eax=039e9cb0 ebx=071b2930 ecx=071b2934 edx=071b2930 esi=00000000 edi=00000000
eip=639c17d5 esp=039e9ca0 ebp=039e9cd0 iopl=0         nv up ei pl zr na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
MSHTML!CImgHelper::SetImgCtx+0x18:
639c17d5 397314          cmp     dword ptr [ebx+14h],esi ds:002b:071b2944=031a8e00
0:008> 
eax=039e9cb0 ebx=071b2930 ecx=071b2934 edx=071b2930 esi=00000000 edi=00000000
eip=639c17d8 esp=039e9ca0 ebp=039e9cd0 iopl=0         nv up ei pl nz na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
MSHTML!CImgHelper::SetImgCtx+0x1b:
639c17d8 0f857b090000    jne     MSHTML!CImgHelper::SetImgCtx+0x217 (639c2159) [br=1]
0:008> 
eax=039e9cb0 ebx=071b2930 ecx=071b2934 edx=071b2930 esi=00000000 edi=00000000
eip=639c2159 esp=039e9ca0 ebp=039e9cd0 iopl=0         nv up ei pl nz na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
MSHTML!CImgHelper::SetImgCtx+0x217:
639c2159 397344          cmp     dword ptr [ebx+44h],esi ds:002b:071b2974=00000000

```

CImgHelper::CScriptCalloutProtection::CScriptCalloutProtection在IE8中并不存在，不过很不幸，CImgHelper::CScriptCalloutProtection::CScriptCalloutProtection 并不是我们要找的目标。

![p11](http://drops.javaweb.org/uploads/images/86cdfe61d6fb710211921af9cb05c03569fcdc23.jpg)

但是目标也不遥远了，继续往下看一点代码，就可以发现IE11在设置IMG元素的上下文时，做了一个CMarkup：：CheckForLMZLLoad(v8, 1);的判断。

![p12](http://drops.javaweb.org/uploads/images/1b152efa64952b42cfd5ca0f3dbd9c2db5e7645e.jpg)

LMZL还有印象不？就是上一节说的Local Machine Zone Lockdown，名字看起来有点中二病，微软具体让这个东西覆盖了多少代码量也是个谜。

记住第二个参数1。

跟入CheckForLMZLLoad之后，我们看到了`if(a4 == 1){v8 = &FCK::FEATURE_BLOCK_LMZ_IMG;}`

看起来很明显了，微软在IMG设置上下文的时候，限制了Local Machine Zone的图片资源加载。

![p13](http://drops.javaweb.org/uploads/images/8e09167f873fb07ae40641437d1d4cdd9f7d576b.jpg)

设置上下文？差点忘了，获取图片和设置上下文的函数就是这个：CImgHelper::FetchandSetImgCtx。

![p14](http://drops.javaweb.org/uploads/images/38d974420deba8a6bd2aa80a0f8af09e36b3e608.jpg)

既然上下文设置失败，那么事件绑定和触发也必然没着落，更惨的是图片也不让显示，RES Protocol判断本地文件是否存在的功能自此宣告灭亡。

0x05 网络诊断
=========

* * *

也许你最近一年根本就没有用过IE，不要紧，IE里面有个无法显示此页还是一直在那里的。当访问一个无法处理的网站时，IE会展示`res://ieframe.dll/dnserror.htm#http://xxx`，在这个页面上有一个“修复连接问题”。

![p15](http://drops.javaweb.org/uploads/images/6e7894252b7aff4feffb86702e1effec69cb961a.jpg)

点击一下这个东西，就会蹦出来一个网络修复程序，比较神奇。那么这里会不会也有安全问题呢，这个修复程序IE是怎么定位到的？

跟踪一下，可以发现发现IE实际调用了ndfapi的LaunchMSDT函数，该函数启动system32下的msdt.exe。调用时使用的是完整路径，所以无需考虑exe劫持之类的问题。

```
0:009> kvn
 # ChildEBP RetAddr  Args to Child              
00 072fa2cc 54f3c7ec 08085978 004bdf80 00000000 KERNEL32!CreateProcessWStub (FPO: [Non-Fpo])
01 072fa5b0 54f3cb1c 07fff5a8 fedbc665 54f32b80 ndfapi!LaunchMSDT+0x201 (FPO: [Non-Fpo])
02 072fa688 54f3c5d8 00000001 54f30000 072fa6bc ndfapi!CNetDiagClient::LaunchScriptedDiagnostics+0x143 (FPO: [Non-Fpo])
03 072fa6a0 54f377a2 00000001 072fa6dc 67654b7d ndfapi!NdfExecuteDiagnosisEx+0x53 (FPO: [Non-Fpo])
04 072fa6ac 67654b7d 069d37e0 00040c94 00000000 ndfapi!NdfExecuteDiagnosis+0x12 (FPO: [Non-Fpo])
05 072fa6dc 675ee143 072fa72c 07b3f7cc 07ffec54 IEFRAME!DiagnoseConnectionProblems+0xa9 (FPO: [Non-Fpo])
06 072fa9bc 7732b0ff 07ff4ff8 072faa0c 07ffec54 IEFRAME!CShellUIHelper::DiagnoseConnection+0x2d3 (FPO: [Non-Fpo])
07 072fa9d4 7730c807 07ff4ff8 00000070 00000004 OLEAUT32!DispCallFunc+0x16f

```

看起来一切都是那么严谨，不过谁知道呢，IE总是在最意想不到的地方出各种小问题。

0x06 参考资料
=========

* * *

*   【1】：[https://msdn.microsoft.com/en-us/library/aa767740(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/aa767740(v=vs.85).aspx)
*   