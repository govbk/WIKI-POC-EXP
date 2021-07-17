# IE安全系列之——昨日黄花：IE中的ActiveX（I）

IX.1 ActiveX的历史和简单的介绍
=====================

* * *

说到ActiveX，则不得不提到COM（组件对象模型）。COM出现时要解决的问题是，“能否把软件做到和硬件一样”，硬件的理想情况是比如有人规定了USB的规范，（Server）提供一个USB接口之后，（Client）只要正确实现了USB就可以让二者相联系，扩展出更多的功能（USB键鼠，U盘，摄像头，等等）。这之中Server（集线器）并不需要知道另一头Client（键盘？鼠标？）具体做啥的，只是知道我（Server）提供给你（Client）一个符合USB规范的接口，你（Client）弄上个东西连接成功就能用，至于你（Client）如何实现就不是我（Server）的事情了。

最初COM的出现也是为了解决类似的问题，例如我在IE里面如何打开一个WORD文档？针对它的解决方案称为OLE（对象连接与嵌入）。1993年微软发布了OLE2，在这（ole32.dll）中提供的API也被日后认为是COM API。有了这些支持之后，微软用它创造了OLE控件，并最终发展成为了在IE中常见的ActiveX控件。如果你用过VB的话，在VB里就能发现大量此类控件的身影，如内嵌的Microsoft Viso等等。

![enter image description here](http://drops.javaweb.org/uploads/images/0b38d9b660bc3e56c8ee19f6a229a999f104c119.jpg)

每个ActiveX控件都由一个GUID（全局唯一标识符）来标识自己，GUID和UUID（全球唯一标识符）差不多，只不过后者是OSF（开源软件基金会）维护，前者是微软自己的实现。

GUID是一个128位的数字，理论上是极大概率时间空间唯一的（随机数生成的空间有2122的大小，按照类似生日问题的算法，如果正确生成的话，和其他人生成的偶然重复概率为1/261）。

GUID算法包括1490年开始到现在的分钟数（保证时间唯一性），一个伪随机数，和MAC地址（保证空间唯一性，没有网卡的话会使用另一个随机常量），API CoCreateGuid可以生成GUID。GUID的一般形式类似于`{AFEE063C-05BA-4248-A26E-168477F49734}`这样。

在IE里或者WSF或者HTA等支持OBJECT标签的地方，可以通过它来加载ActiveX，OBJECT标签的具体用法请见参考资料（1）。

![enter image description here](http://drops.javaweb.org/uploads/images/6b7aafd194a55ce19e73e57b9ce86cffcb1e99e4.jpg)

图：iDefense ComRaider ActiveX Fuzzer生成的WSF测试脚本使用了Object标签来载入被测ActiveX控件

IX.2 IE中的ActiveX
================

* * *

默认情况下，要在IE浏览器中运行ActiveX插件，ActiveX插件必须同时拥有`Safe For Scripting/Safe For Init`标记才可以运行。在IE发现HTML网页中有ActiveX控件时，IE会依次检查如下动作来确定控件是否可以安全加载和运用于代码中。

（1） IE会先检查ActiveX控件是否设置了killbit，如果设置了Killbit，IE将不会加载这个控件；

（2）IE会确定这个控件是否派生了IObjectSafety，如果有的话，IE会通过这个接口检查是否有设置Safe for Scripting/Safe For Init，如果没有派生IObjectSafety，IE会在注册表检查`{7DD95802-9882-11CF-9FA9-00AA006C42C4} (Safe for Initialization)`和`{7DD95801-9882-11CF-9FA9-00AA006C42C4}(Safe For Scripting).`两项。

这里的具体内容在之前的一篇文章http://drops.wooyun.org/papers/5673有介绍，所以不重复叙述了。为了后续实验方便，我们可以使用环境自己先弄个ActiveX，这里以Microsoft Visual C++ 2010为例创建一个ActiveX控件。

首先，如图创建一个新工程，简单起见，在后一个窗口直接完成即可。

![enter image description here](http://drops.javaweb.org/uploads/images/6779dc917c74ee25c8c13c36e5d80a2ae70ac822.jpg)

生成的对外接口定义文件（XXX.idl）文件是和该控件信息有关的一个重要文件，许多信息都可以在此看到。例如“类信息”中uuid就是ActiveX控件待会儿在IE中加载时所要用到的Classid。

![enter image description here](http://drops.javaweb.org/uploads/images/d5d6544894ec78705ebdeed2b4ade1b5fa72bc49.jpg)

由于我们只是演示，因此我们简单的添加一个函数foo()： 在类视图的接口处点击右键，选择添加->方法

![enter image description here](http://drops.javaweb.org/uploads/images/120bf33f4707a0f7603a2452180fa3455cbd5628.jpg)

然后，添加一个void foo()，填写之后点击完成：

![enter image description here](http://drops.javaweb.org/uploads/images/b423fef5e9fff194e84ffeb2649e2b7e49274fa8.jpg)

这时VS会在多个地方添加这个函数的信息，不过简单起见，回到刚才的idl文件中我们就可以看到添加了个新函数

![enter image description here](http://drops.javaweb.org/uploads/images/963e05a09e36c5c35f61e45d9b2bf0b25105b6dd.jpg)

在MSVC中直接F12过去：

![enter image description here](http://drops.javaweb.org/uploads/images/305b3770a99148847a10170ad1bd26b2d11b1f5b.jpg)

这个位置就是新加函数的位置，为了方便演示，我们在里面随便弹一个对话框好了：

```
::MessageBox(0, L"hello wooyun", L"blast", MB_OK);

```

然后，我们右键选择工程，编译一个Release版的ocx控件：

![enter image description here](http://drops.javaweb.org/uploads/images/6d7d0a33ceb077b2d9645ee0749e1c7777cb9e81.jpg)

之后，使用regsvr32 testActivex.ocx。

![enter image description here](http://drops.javaweb.org/uploads/images/2bc31475bf45b2e7758f0867afb39e9d9db41c4d.jpg)

此时，该ActiveX就已经被注册了，我们创建一个测试用的htm文件吧，

```
<HTML>    
<OBJECT ID="test" WIDTH=300 HEIGHT=300 classid="CLSID:2D9835F7-9534-46C2-AE7A-C75098AA6105">  
</OBJECT>  
</HTML>  

```

CLSID请换成你的idl里面的那个uuid。由于我们的ActiveX控件并未设置Safe For Scripting和Safe For Init，所以在本地域打开时IE做了这个提示，点击是之后，就可以看到插件运行起来了。

![enter image description here](http://drops.javaweb.org/uploads/images/17512de1f78d1f97b197c243199e53720ccaf06f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b51bbf3e63622db4ec84b8bfe2333a0c5e963e08.jpg)

此时，我们也可以测试调用我们加入的foo()函数，在SCRIPT标签中调用test.foo()，即可调用成功，可见IE中弹出了一个对话框：

![enter image description here](http://drops.javaweb.org/uploads/images/0045ac3b323cd7dfa4afcf3c1c151298b2d03a13.jpg)

要实现Safe For Scripting、Init，请这么做： 头文件（例如我的工程是testActivexCtrl.h）中加入#include <objsafe.h>，然后将 DECLARE_INTERFACE_MAP()

```
BEGIN_INTERFACE_PART(ObjSafe, IObjectSafety)   


    STDMETHOD_(HRESULT,   GetInterfaceSafetyOptions)   (     
    /*   [in]   */   REFIID   riid,   
    /*   [out]   */   DWORD   __RPC_FAR   *pdwSupportedOptions,   
    /*   [out]   */   DWORD   __RPC_FAR   *pdwEnabledOptions   
    );  

    STDMETHOD_(HRESULT,   SetInterfaceSafetyOptions)   (     
        /*   [in]   */   REFIID   riid,   
        /*   [in]   */   DWORD   dwOptionSetMask,   
        /*   [in]   */   DWORD   dwEnabledOptions   
        );  

END_INTERFACE_PART(ObjSafe);

```

加入class CtestActiveXCtrl : public COleControl块中。

在对应CPP文件的最后加入下列代码，记得将CtestActiveXCtrl换成你自己的类名。

```
BEGIN_INTERFACE_MAP(CtestActiveXCtrl,COleControl) 
  INTERFACE_PART(CtestActiveXCtrl,IID_IObjectSafety,ObjSafe) 
END_INTERFACE_MAP()  

ULONG FAR EXPORT CtestActiveXCtrl::XObjSafe::AddRef() 
{ 
  METHOD_PROLOGUE(CtestActiveXCtrl,ObjSafe) 
    return pThis->ExternalAddRef(); 
}  

ULONG FAR EXPORT CtestActiveXCtrl::XObjSafe::Release() 
{ 
  METHOD_PROLOGUE(CtestActiveXCtrl,ObjSafe) 
    return pThis->ExternalRelease(); 
}  

HRESULT FAR EXPORT CtestActiveXCtrl::XObjSafe::QueryInterface(REFIID iid,void FAR* FAR* ppvObj) 
{ 
  METHOD_PROLOGUE(CtestActiveXCtrl,ObjSafe) 
    return (HRESULT)pThis->ExternalQueryInterface(&iid,ppvObj); 
}  

const DWORD dwSupportedBits = INTERFACESAFE_FOR_UNTRUSTED_CALLER | INTERFACESAFE_FOR_UNTRUSTED_DATA; 
const DWORD dwNotSupportedBits=~dwSupportedBits;  

HRESULT STDMETHODCALLTYPE   
  CtestActiveXCtrl::XObjSafe::GetInterfaceSafetyOptions(   
  /*[in]*/ REFIID riid, 
  /*[out]*/ DWORD __RPC_FAR *pdwSupportedOptions, 
  /*[out]*/ DWORD __RPC_FAR *pdwEnabledOptions) 
{ 
  METHOD_PROLOGUE(CtestActiveXCtrl,ObjSafe) 
    HRESULT retval = ResultFromScode(S_OK); 

  IUnknown FAR* punkInterface; 
  retval = pThis->ExternalQueryInterface(&riid, (void **)&punkInterface); 
  if(retval != E_NOINTERFACE) 
  { 
    punkInterface->Release(); 
  } 

  *pdwSupportedOptions=*pdwEnabledOptions=dwSupportedBits; 
  return retval; 
}  

HRESULT STDMETHODCALLTYPE   
  CtestActiveXCtrl::XObjSafe::SetInterfaceSafetyOptions(   
  /*[in]*/ REFIID riid, 
  /*[in]*/ DWORD dwOptionSetMask, 
  /*[in]*/ DWORD dwEnabledOptions) 
{ 
  METHOD_PROLOGUE(CtestActiveXCtrl, ObjSafe) 

   IUnknown FAR* punkInterface; 
  pThis->ExternalQueryInterface(&riid, (void **)&punkInterface); 
  if(punkInterface)
  { 
    punkInterface->Release(); 
  } 
  else 
  { 
    return ResultFromScode(E_NOINTERFACE); 
  }  

  if(dwOptionSetMask & dwNotSupportedBits)  
  {   
    return ResultFromScode(E_FAIL); 
  }  

  dwEnabledOptions&=dwSupportedBits; 
  if((dwOptionSetMask&dwEnabledOptions)!=dwOptionSetMask) 
  { 
    return ResultFromScode(E_FAIL); 
  } 

  return ResultFromScode(S_OK); 
}

```

重新编译，再次打开IE时，这个控件就会直接加载起来而不会再弹出对话框了。

IX.3 Windows 10中ActiveX插件变成了什么样
===============================

* * *

另一个大家比较关注的可能是Windows 10里面的ActiveX情况，有一个好消息是Microsoft Edge已经不支持ActiveX了，不过Windows 10同样自带的IE11则依然和Win7、Win8的IE11一样，继续支持ActiveX。

在Windows 10中让我们做同样的事情，

![enter image description here](http://drops.javaweb.org/uploads/images/688f5d88dbb2cde2b08a3152ec0ca3175f55d953.jpg)

首先，Win10提供了IE和Edge浏览器，选择使用Edge浏览器打开时，页面中并未加载该ActiveX控件：

![enter image description here](http://drops.javaweb.org/uploads/images/0b3465d001abe87d14ca7ef0e54eeac7a249a50a.jpg)

可以看到test对象事实上只是一个CObjectElement而已，它并没有加载ActiveX控件。使用工具查看Edge的内存也可得出同样结论——这个OCX并没加载到内存。

![enter image description here](http://drops.javaweb.org/uploads/images/efe84eb644c01f18023c50ca62002b404a5d9d22.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/4b29fb6d459ed1615ab06f643bc3cf1f0e515872.jpg)

再换用IE打开这个页面，在Win10自带的IE11中，我们看到插件正常运行了。

![enter image description here](http://drops.javaweb.org/uploads/images/6baf0db4c570810029c4cf2ef3201c6f7551ad9e.jpg)

另外，在原先的IE中，Flash插件也是靠ActiveX的形式活着的。在Edge中应该也考虑到了这个问题，Edge自带一套Flash，所以用户不需要额外去网站上下载安装，这套Flash的形式是什么呢？我们可以简单看一下：

![enter image description here](http://drops.javaweb.org/uploads/images/f3fc22d857a2bb32beca26918709237c9cbbb4c8.jpg)

首先我们可以看到FLASH的加载代码依然和之前一样，采用Object的方式加载：

![enter image description here](http://drops.javaweb.org/uploads/images/65dde53b1f7587399311292e057f4ab02c2d14d4.jpg)

不过之前的经历我们知道Object在Edge中是不能像之前一样简单加载ActiveX的，那这里是什么呢？参考进程列表可以发现，Edge在执行到包含有Flash的页面时，会启动一个FlashUtil_ActiveX.exe 进程，这个进程名字十分奇怪，在仔细查看Edge的进程模块后，我们可以发现，Edge其实还是保留着加载ActiveX控件的能力的，只不过控制在一个比较小的范围内而已：

![enter image description here](http://drops.javaweb.org/uploads/images/bcfd540352ecf75be4f1681d6682eed8b30d7868.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/a69d84822830b863fef2860235996fe94ab1e47f.jpg)

本章节只是介绍了ActiveX的历史和一个示例ActiveX的编译方法，而并没有介绍有关Activex安全的部分，关于Activex漏洞的挖掘等内容将在后续章节介绍。

参考资料
====

* * *

(1] http://www.w3school.com.cn/tags/tag_object.asp

(2] http://www.ffri.jp/assets/files/monthly_research/MR201503_Windows_10_Technical_Preview_Security_Overview_ENG.pdf