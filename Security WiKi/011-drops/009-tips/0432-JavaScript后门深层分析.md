# JavaScript后门深层分析

0x00 背景
=======

* * *

之前@三好学生的文章[JavaScript BackDoor](http://drops.wooyun.org/tips/11764)中提到了利用rundll32.exe执行一段JavaScript代码即可反弹一个Http Shell，这里将之前看到的对其原理进行分析的文章翻译和大家分享。

links:[http://thisissecurity.net/2014/08/20/poweliks-command-line-confusion/](http://thisissecurity.net/2014/08/20/poweliks-command-line-confusion/)

最近，hFireF0X在逆向工程论坛kernelmode.info上发表了对Win32/Poweeliks恶意软件详细调查的文章。这个恶意软件的特别之处就是它存在于window注册表中并且使用rundll32.exe来执行JavaScript代码。

我发现很有趣的是我显然不是唯一一个发现可以通过rundll32来执行一些JavaScript代码的人。

![p1](http://drops.javaweb.org/uploads/images/9586386806a5e56587ac7e290c543c93e2cb4f57.jpg)

当我们第一次发现命令行执行JavaScript，我们很好奇它是如何工作的。

在接下来的文章中，我们会分析JavaScript代码时如何执以及为什么会在调用这样简单的命令行代码时执行：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";alert(‘foo’);

```

0x01 Rundll32介绍
===============

* * *

关于rundll32.dll的使用在MSDN上有专门的[文档](https://support.microsoft.com/zh-cn/kb/164787/en)；它往往被用来调用一个DLL文件的输出函数，可以通过以下的命令来实现：

```
RUNDLL32.EXE <dllname>,<entrypoint> <optional arguments>

```

entrypoint就是输出函数；它的函数原型应该是如下所示：

```
void CALLBACK EntryPoint(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow);

```

参数lpszCmdLine是由rundll32.exe命令语句中的`<optional arguments>`值确定的。

我们会尝试指出rundll32.exe是如何能够调用被mshtml.dll输出的函数RunHTMLApplication，以及“Javascript”前缀是如何被用来执行实际的JavaScript代码的。

0x02 Rundll32.exe分析
===================

* * *

**a.参数**

rundll32.exe做的第一件事就是使用内置的ParseCommand命令来对命令进行解析。这个函数会查找一个逗号（‘，’，0x2c）来定位dll的名称和一个空格（‘ ’，0x20）来定位入口点名称

![p2](http://drops.javaweb.org/uploads/images/1d9a46039c9d6251af78de416db804bf51d7404c.jpg)

当使用我们的样本命令时，ParseCommand会返回`javascript:"\..\mshtml`作为DLL名称，返回`RunHTMLApplication`作为入口点。

![p3](http://drops.javaweb.org/uploads/images/cf7ea6ca8e4f2a6858d4799f958e7ffc2800ebcf.jpg)

0x03 Dll loader
===============

* * *

rundll32.exe会尝试几种方法来从最初的“`JavaScript："\..\mshtml`”加载实际的DLL。

第一次测试使用了函数`GetFileAttributes("javascript:"\..\mshtml")`。这个函数最终会接近`C:\Windows\system32\mshtml`。如果这个文件没有被发现，那么这个函数就会返回-1。

![p4](http://drops.javaweb.org/uploads/images/4ea6952f78a80f9ad62315efb420e18660db77a4.jpg)

接下来`SearchPath`会被调用来确定DLL的名称。这个函数会读取注册表键值`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\SafeProcessSearchMode`。微软对于这个键值的定义是：

当这个REG_DWORD类型的注册表键值被设为1，SearchPath会首先搜索系统路径中指定的文件夹，然后会搜索当前工作的文件夹。当这个注册表键值被设为0时，电脑首先会搜索当前工作的文件夹，然后再去搜索系统路径中指定的文件夹。系统对于这个注册表键的默认值是0。

在默认情况下，这个注册表键值是不存在的（在win xp、7、8下），所以`SearchPath`会优先尝试在rundll32.dll的当前目录中加载文件mshtml，其次才会尝试在系统路径中进行定位。

![p5](http://drops.javaweb.org/uploads/images/f09866bda04e7ce34d301aedbc453aa5144eb23e.jpg)

如果所有的尝试都失败了，那么rundll32.exe就会进行下一步。`GetFileAttribute`将再次被调用来给模块查找manifest文件：`javascript:"\..\mshtml.manifest`。

若所有的之前的步骤都失败了，rundll32.exe最终会调用`Loadlibrary("javascript:"\..\mshtml")`。

`LoadLibrary`只是位于ntdll.dll中的一个对LdrLoadDLL的简单封装。在内部，LdrLoadDll会添加默认的扩展dll并且把结果字串（`javascript:”\..\mshtml.dll`）作为路径来解析。“`..`”代表再向上一层文件夹：它就解析成了`mshtml.dll`。

当`mshtml.dll`已经被确定了，LdrLoadDll就可以加载系统目录中的lib库了。

![p6](http://drops.javaweb.org/uploads/images/1a5038e64f768bd9dab0869d4ab55b774aa42130.jpg)

rundll32.exe接下来会使用之前提取的入口点名称`RunHTMLApplication`调用`GetProcAddress`。

这个时候我们可以发现，`javascript:`前缀看起来毫无用处：`LoadLibrary("foobar:\"\..\mshtml")`工作的很好。所以，为什么要加这么一个前缀呢？

0x04 协议处理
=========

* * *

一旦入口地址已经被解析出来，rundll32.dll会调用函数`mshtml.dll!RunHTMLApplication`。

即使没有被记录，实际的RunHTMLApplication也能从`c:\windows\system32\mshta.exe`的调用中推断出来（这个应用专门来启动一个.hta文件）。

```
HRESULT RunHTMLApplication(
HINSTANCE hinst,
HINSTANCE hPrevInst,
LPSTR szCmdLine,
int nCmdShow
);

```

这和期望的rundll32.exe的入口点地址很相似：

```
void CALLBACK EntryPoint(
HWND hwnd,
HINSTANCE hinst,
LPSTR lpszCmdLine,
int nCmdShow
);

```

RunHTMLApplication接受一个窗口的句柄而不是一个模块的句柄作为第一个参数。这个参数会在mshml登记一个窗口类或者为一个类创建窗口时被使用。传递一个同实际的实例并不相一致的值并不会给user32带来很大影响。

第二个参数完全没有被使用，所以这个不匹配并不重要。

最后一个参数，`nCmdShow`，被`RunHTMLApplication`函数用来展示代管这个HTML应用的主机窗口。rundll32经常使用值`SW_SHOWDEFAULT`来调用入口点函数来指示任何可能打开的窗口使用窗口默认配置。

在我们的例子中，可能更让人感兴趣的参数是`lpszCmdLine (";alert('foo'))`。

![p7](http://drops.javaweb.org/uploads/images/7c593dd2a6e867b58a7d97e1f2b7a4d5114867df.jpg)

这显然会导致问题，因为这并不是一个有效的JavaScript语句（注意在语句末尾丢掉的双引号）。但是它仍然有效，因为`RunHTMLApplication`忽略给定的参数，并且更倾向于从windows API`GetCommandLine`中重新请求原始的命令（封装在`GetCmdKLine`函数的一个调用中）。

![p8](http://drops.javaweb.org/uploads/images/777b710a57a01f9a541c844845072cd50b772fd1.jpg)

完整的命令包含了可执行文件和参数的名称：`GetCmdLine`通过整理可执行规范来提取参数。

![p9](http://drops.javaweb.org/uploads/images/14c6b239ee8c0e670adb6700524da696a84d2322.jpg)

在这之后，`RunHTMLApplication`会调用`CreateURLMonitor`:

![p10](http://drops.javaweb.org/uploads/images/92ea58ea5c38f4307da06941a8d7ed98ee9a5219.jpg)

这也是需要字符串“javascript”的地方。

`CreateURLMonitor`解析命令行来提取char":"(0x3A)之前的字符串：“javascript”。

![p11](http://drops.javaweb.org/uploads/images/0a18e0a1a942afa8a658dbcdab8a712b863b20ee.jpg)

`CreateUrlMoniker`会爬取注册表键值`HKCR\SOFTWARE\Classes\PROTOCOLS\Handler\`。这些键值和一个协议集以及它们的CLSID有关。

`CreateUrlMoniker`会发现一个合适的协议处理器来对Javascript的协议进行处理（`HKCR\SOFTWARE\Classes\PROTOCOLS\Handler\javascript`）：

![p12](http://drops.javaweb.org/uploads/images/87d21f73ad6732c96ab5358ac05192e565e483e4.jpg)

CLSID`{3050F3B2-98B5-11CF-BB82-00AA00BDCE0B}`符合微软“Microsoft HTML Javascript Pluggable Protocol”规范。

![p13](http://drops.javaweb.org/uploads/images/ab5021f2816d924be980f07d354e8767c589274e.jpg)

这也是为什么字符串“javascript”必须在参数的开始部分的原因。

相同的机制在人们在IE的导航栏输入javascript:alert('alert')时也会起作用。

![p14](http://drops.javaweb.org/uploads/images/7b946a329416b4b2d79928279dfe82425a8d29c3.jpg)

位于“：”分隔符之后的字符串会被JavaScript URL moniker解释成JavaScript指令：

```
"\..\mshtml,RunHTMLApplication ";alert(‘foo’);

```

这是一个带有字符串`"\..\mshtml,RunHTMLApplication "`和函数`（alert)`的无效JavaScript语句（因为双引号会跳过所有之前的步骤！）。

最终RunHTMLApplication会调用`CHTMLApp::Run`,这条JavaScript语句也会被执行：

![p15](http://drops.javaweb.org/uploads/images/9c4f2d06104a74b868238cd32456ded522959433.jpg)

0x05 安全影响
=========

* * *

从安全的角度来看，通过rundll32来执行JavaScript就像执行一个HTML应用。

换句话说，我们可以使用IE的全部权利。当区域安全被关闭，允许跨域脚本访问，我们就可以拥有读写客户端机器文件和注册表的权力。

通过这个技巧，JavaScript可以在IE外部被执行，并且脚本没有任何安全概念的约束，比如保护模式\沙盒。

0x06 结论
=======

* * *

按照我们的理解，这个技术语序绕过一些信任内置的rundll32的行为的安全产品。

0x07 本文相关
=========

* * *

1.  [https://twitter.com/hFireF0X](https://twitter.com/hFireF0X)
2.  [http://www.kernelmode.info/forum/viewtopic.php?f=16&t=3377](http://www.kernelmode.info/forum/viewtopic.php?f=16&t=3377)
3.  [http://support.microsoft.com/kb/164787/en](http://support.microsoft.com/kb/164787/en)
4.  [http://msdn.microsoft.com/enus/library/windows/desktop/aa365527%28v=vs.85%29.aspx](http://msdn.microsoft.com/enus/library/windows/desktop/aa365527%28v=vs.85%29.aspx)
5.  [https://thisiscybersec.files.wordpress.com/2014/08/capture-d_c3a9cran-2014-08-20-c3a0-16-16-36.png](https://thisiscybersec.files.wordpress.com/2014/08/capture-d_c3a9cran-2014-08-20-c3a0-16-16-36.png)
6.  [https://thisiscybersec.files.wordpress.com/2014/08/capture-d_c3a9cran-2014-08-20-c3a0-16-16-36.png](https://thisiscybersec.files.wordpress.com/2014/08/capture-d_c3a9cran-2014-08-20-c3a0-16-16-36.png)