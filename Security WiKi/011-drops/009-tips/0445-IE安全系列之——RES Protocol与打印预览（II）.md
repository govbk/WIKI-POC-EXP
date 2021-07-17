# IE安全系列之——RES Protocol与打印预览（II）

0x00 简介
=======

* * *

事情得从一个报告说起，有人说网页map.yahoo.co.jp，在IE中进行打印预览时，使用倍率666%会让IE崩溃（至少2016-5-28为止还是这样），为什么IE中会出现这么6的问题呢？从打印预览这个功能看起吧。

![p1](http://drops.javaweb.org/uploads/images/acf4c7fe26c505db87c5a11f559054ad4cef33dd.jpg)

0x01 打印预览（Web）
==============

* * *

从网页的角度来看，负责打印预览的相关内容位于`res://ieframe.dll/preview.dlg`与`res://ieframe.dll/preview.js`。IE自5.5开始引入了打印预览以及自定义的打印预览功能。而微软的早期文档内容十分丰富，可以参考到很多有用信息。

在雅虎网站造成IE的崩溃中，一步不可缺少的操作是——设置缩放比例。所以，我们的关注点可以集中到缩放比率上。

在MSDN介绍自定义打印预览模板时，微软提到：“推荐使用一个DIV作为主容器”。在preview.dlg的LN253-256，可以看到MasterContainer，是一个DIV，这也与微软的推荐做法一致。

```
<div id="MasterContainer" tabindex="0" style="width:100%; position:absolute;" >
    <!-- Pages go here -->
    <div id="EmptyPage" class="divPage" style="position:absolute; left:0px; top:0px; display:none;"><div class="page">&nbsp;</div></div>
</div>

```

另外，还“推荐使用CSS的zoom属性来为主容器设置百分比的缩放”，这在preview.js中得到了良好的体现：

```
function PositionPages(nDispPage) {
……
        MasterContainer.style.zoom = g_nZoomLevel + "%";
……

```

与：

```
function ChangeZoom() {
    MasterContainer.style.zoom = g_nZoomLevel + "%";
    PositionPages(g_nDispPage);
    return g_nZoomLevel;
}

```

在了解了缩放功能进行缩放的方法之后，让我们再看一看页面是如何被转入预览中的。

在preview.js的CPrintDoc_AddPage()函数中，可以看到如下的代码注入到了MasterContainer的beforeEnd处。

```
newHTM = "<DIV class=divPage><IE:DeviceRect media=\"print\" class=page id=mDiv" + this._nStatus + this._strDoc + "p" + aPage.length + ">";
newHTM += "<IE:LAYOUTRECT id=mRect" + this._nStatus + this._strDoc + "p" + aRect.length;
newHTM += " class='" + classLayoutRect + "' nextRect=mRect" + this._nStatus + this._strDoc + "p" + (aRect.length + 1);
newHTM += " onlayoutcomplete=\"OnRectComplete('" + this._strDoc + "', " + g_ObsoleteBar + ")\"";
newHTM += " tabindex=-1 onbeforefocusenter='event.returnValue=false;' ";
newHTM += " />";
newHTM += "<DIV class='" + classHeader + "' id=header>";
newHTM += HeadFoot.HtmlHead;
newHTM += "</DIV>";
newHTM += "<DIV class='" + classFooter + "' id=footer>";
newHTM += HeadFoot.HtmlFoot;
newHTM += "</DIV>";
newHTM += "</IE:DeviceRect></DIV>";
MasterContainer.insertAdjacentHTML("beforeEnd", newHTM);

```

在上面的代码中可以看到一些特殊的元素。比如**IE:DEVICERECT**和**IE:LAYOUTRECT**。DeviceRect、LayoutRect两个元素用来组合展示页面。每个DeviceRect代表一个页面，

LayoutRect为DeviceRect的子元素，IE在它里面显示页面预览。因为preview.dlg指定了XML Namespace（`<HTML XMLNS:IE>`）所以元素前带有IE:前缀。

与其他元素不同的是，LayoutRect似乎并没有innerHTML属性。IE只是在里面展示页面的预览，页面并不能操作它。那么问题来了，IE怎么产生的预览？

0x02 打印预览窗口的创建
==============

* * *

要知道这个，让我们先完整地跟踪整个流程。首先，因为打印预览是在res: protocol下的，之前的文章我们介绍了CResProtocol是处理Res Protocol的类，在DoParseAndBind上下断点可以观察到此处完整的调用（无关的栈已经删除）：

```
0:058> bp MSHTML!CResProtocol::DoParseAndBind
0:牌058> g
Breakpoint 0 hit
eax=14061280 ebx=140611fc ecx=08101bd4 edx=1406127c esi=76c2f1fc edi=120ae270
eip=6474f8dd esp=120ae258 ebp=120ae290 iopl=0         nv up ei pl zr na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
MSHTML!CResProtocol::DoParseAndBind:
6474f8dd 8bff            mov     edi,edi
0:058> kvn
 # ChildEBP RetAddr  Args to Child              
00 120ae254 647504d6 14061280 14061284 14061274 MSHTML!CResProtocol::DoParseAndBind (FPO: [4,163,4])
01 120ae268 64750495 120ae2b0 64750410 140611e0 MSHTML!CResProtocol::ParseAndBind+0x26 (FPO: [0,0,0])
02 120ae290 76c63067 140611fc 06e8c9f0 08109f38 MSHTML!CResProtocol::Start+0x88 (FPO: [6,5,4])
…………………………
10 120aeeb4 6467517a 120aeed0 00000000 00000000 MSHTML!CMarkup::Load+0x228 (FPO: [1,71,4])
11 120af26c 6479f0a1 120af2a0 00000000 00000000 MSHTML!CMarkup::LoadFromInfo+0xb07 (FPO: [Non-Fpo])
12 120af3b0 6479ebf4 120af3d8 00000000 120af490 MSHTML!CDoc::LoadFromInfo+0x48d (FPO: [Non-Fpo])
13 120af474 65075c07 03ea5400 00000001 081d4de0 MSHTML!CDoc::Load+0xd7 (FPO: [5,41,4])
14 120af5ec 650772d6 120af678 120af668 080940c8 MSHTML!CHTMLDlg::Create+0x869 (FPO: [Non-Fpo])
15 120af65c 6507e39d 00000000 10908ed0 00000000 MSHTML!InternalShowModalDialog+0x1c1 (FPO: [Non-Fpo])
16 120af718 6507e54d 120af770 6629d470 0000000b MSHTML!ModelessThreadInit+0x12f (FPO: [Non-Fpo])
……………………

```

根据15层栈可以知道该窗口是一个Modeless Window，那么这个调用是谁发起的呢？观察其他线程，可以发现下列调用栈（无关栈已经删除）：

```
43  Id: 5404.3b18 Suspend: 1 Teb: 7ef7e000 Unfrozen
# ChildEBP
…………………………
06 10908f58 6507a498 1449d3c0 054b8f94 081a995c MSHTML!InternalModelessDialog+0x431 (FPO: [Non-Fpo])
07 10908fe8 6655f9b0 00a62528 081d4de0 000003e0 MSHTML!ShowHTMLDialogEx+0xa8 (FPO: [6,32,0])
08 109095b4 6649aafe 10909728 00000000 00000001 IEFRAME!CDocHostUIHandler::DoTemplatePrinting+0x31d (FPO: [Non-Fpo])
09 10909688 650587fb 08260e7c 6464d428 00000007 IEFRAME!`Microsoft::WRL::Module<1,Microsoft::WRL::Details::DefaultModule<1> >::Create'::`2'::`dynamic atexit destructor for 'module''+0x64146
0a 10909b94 648662de 0a4d2b40 00000000 00000000 MSHTML!CDoc::PrintHandler+0x73a (FPO: [Non-Fpo])
0b 1090a7a8 6464dea1 00000000 663d9884 000007d3 MSHTML!`CBackgroundInfo::Property<CBackgroundImage>'::`7'::`dynamic atexit destructor for 'fieldDefaultValue''+0xbdfbd
0c 1090a7c8 66562101 03ea3f00 663d9884 000007d3 MSHTML!CDoc::Exec+0x21 (FPO: [6,0,0])
0d 1090ba08 66568f04 080fd650 00000000 1090ba70 IEFRAME!CDocHostUIHandler::ShowContextMenu+0x98d (FPO: [5,1157,4])
0e 1090ba3c 64f4aaac 004bc898 00000000 1090ba70 IEFRAME!CDocObjectHost::ShowContextMenu+0xd4 (FPO: [Non-Fpo])
0f 1090ba80 64f7ed1f 00000123 000000d7 00000000 MSHTML!CDoc::ShowContextMenu+0x137 (FPO: [4,7,4])
10 1090ba9c 64f7dbe6 00000123 000000d7 00000000 MSHTML!CElement::ShowContextMenu+0x1f (FPO: [Non-Fpo])
11 1090bc00 64eb5e79 1090bd78 00000000 64647180 MSHTML!CElement::OnContextMenu+0x17b (FPO: [2,81,4])
12 1090bc50 64bb244c 0a58da40 1090bd78 1090bd78 MSHTML!`CBackgroundInfo::Property<CBackgroundImage>'::`7'::`dynamic atexit destructor for 'fieldDefaultValue''+0xb62fa
13 1090bc70 645c789e 0a58da40 1090bd78 03ea3f00 MSHTML!CElement::HandleMessage+0xc2 (FPO: [Non-Fpo])
14 1090bc90 645c7430 14054840 0000007b 03ea3f00 MSHTML!CElement::HandleWindowMessage+0x6b (FPO: [Non-Fpo])
15 1090bd1c 647e7558 1090bd78 14054840 00000000 MSHTML!CDoc::PumpMessage+0x638 (FPO: [3,29,4])
16 1090be94 64cee296 0000007b 00a62528 00d70123 MSHTML!CDoc::OnMouseMessage+0x2b4 (FPO: [7,85,4])
…………………………

```

可以发现

1.  MSHTML!CDoc::PrintHandler处理了相关的打印请求；
2.  最终页面启动了一个新IE窗口用来加载res://ieframe.dll/preview.dlg（IEFRAME!CDocHostUIHandler::DoTemplatePrinting → MSHTML!ShowHTMLDialogEx）。

0x03 CDoc::PrintHandler
=======================

* * *

有了之前的结论之后，首先来观察MSHTML!CDoc::PrintHandler。在IDA中打开MSHTML.DLL，定位到CDoc::PrintHandler后查看伪代码（下为Win7+IE11的结果）。

首先CDoc::PrintHandler检查指定的CLSID是否被支持。下伪代码实际含义pCommandTarget->Exec(&CGID_DocHostCommandHandler, a10（即：guid）, a7, &varIn （即：v73）, &varOut （即：v67）); 。

```
if ( pCommandTarget && a7 != 2 && !(*(_DWORD *)(v10 + 3584) & 0x400000) )
{
    hr = (*(int (__stdcall **)(int, const GUID *, int, int, int, int *))(*(_DWORD *)pCommandTarget + 16))(
            pCommandTarget,
            &CGID_DocHostCommandHandler,
            (a10 != 0) + 6,
            a7,
            v73,
            v67);
    v11 = hr;
    if ( hr != OLECMDERR_E_NOTSUPPORTED && hr != OLECMDERR_E_UNKNOWNGROUP && hr != OLECMDERR_E_DISABLED)
      goto Cleanup;
    v12 = v72;
}

```

接着，程序寻找是否有alternative print source，也即由`<link>`元素的**REL=alternate MEDIA=print**指定的其他可选打印源。如果没有，做一些简单的字符串处理工作：

```
if ( !CDoc::GetAlternatePrintDoc((const unsigned __int16 *)v71, v12, (unsigned __int16 *)&v78, v12) )
  {
    v16 = &v78;
    do
    {
      v17 = *(_WORD *)v16;
      v16 += 2;
    }
    while ( v17 != (_WORD)v69 ); //wcslen
    if ( (signed int)(v16 - (char *)&v79) >> 1 )
    {
      v15 = (int)&v78;
      v71 = (int)&v78;
LABEL_14:
      if ( !RatingEnabledQuery() )
      {
        v11 = 0x80004005u;
        goto Cleanup;
      }
      goto LABEL_16;
    }
  }

```

再接下来是一个比较长的函数段。首先程序判断是否有可打印的plugin site。例如acrobat pdf都算是这种。然后发送“Print”请求。MSDN解释是“用默认模版或自定义模版”来打印（[https://msdn.microsoft.com/en-us/library/aa769937(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/aa769937(v=vs.85).aspx)）。

```
v73 = 0;
if( !CDoc::GetPlugInSiteForPrinting(v72, &v73) )
{
    v18 = v73;
    if ( a10 )
    {
      v11 = -2147467259;
    }
    else
    {
    memset(&v50, 0, 0x20u);
    v69 = 0;
    Cookie = 0;
    //发送IDM_PRINT请求
    v11 = (*(int (__stdcall **)(int, GUID *, wchar_t **, signed int, LCID, ULONG_PTR *))(*(_DWORD *)v73 + 20))(
            v73,
            &GUID_NULL,
            &off_6449DFC0, //"Print"
            1,
            g_lcidUserDefault,
            &Cookie);
    if ( v11 )
    {
        FreeEXCEPINFO(v46);
        goto LABEL_70;
    }
    VariantInit(&pvarg);
    v55 = 0;
    v53 = 0;
    v54 = 0;
    //
    v11 = (*(int (__stdcall **)(int, ULONG_PTR, GUID *, LCID, signed int, char *, VARIANTARG *, char *, int *))(*(_DWORD *)v18 + 24))(
            v18,
            Cookie,
            &GUID_NULL,
            g_lcidUserDefault,
            1,
            &v52,
            &pvarg,
            &v50,
            &v69);
    VariantClear(&pvarg);
    FreeEXCEPINFO(v46);
    }
LABEL_69:
    ReleaseInterface((struct IUnknown *)v46);
    goto LABEL_70;
}

```

然后，可以看到PrintHandler将当前页面保存到了临时目录下。

```
CDoc::PrintHandler(CDocument *,ushort const *,ushort const *,ulong,tagSAFEARRAY *,ulong,tagVARIANT *,tagVARIANT *,int) 
{
  ......
  if ( !v71 )
  {
    CDoc::SetTempFileTracking(1);
    Cookie = CDoc::HasTextSelection(v10);
    CDoc::SaveToTempFileForPrint(
      v72,
      &v78,
      260u,
      Cookie != 0 ? (int)&v77 : 0,
      Cookie != 0 ? 0x104 : 0,
      Cookie != 0 ? (int)&v77 : 0);
    CDoc::TransferTempFileList(&v56);
    CDoc::SetTempFileTracking(0);
    v71 = (int)&v78;
  }
  ......

```

随后，SetPrintCommandParameters、SetPrintManagerCommandParameters用来设置打印参数，先跳过不看，之后有一个关键操作CreateHTMLDocSource，则是负责弹出打印窗口的主人公。

```
v11 = CreateHTMLDocSource(v61, v39, v40, v38, (struct IInspectable **)v48, v49);

```

0x04 CreateHTMLDocSource
========================

* * *

CreateHTMLDocSource代码简单明了，列举如下：

```
HRESULT __fastcall CreateHTMLDocSource(int a1, int a2, int a3, struct IWebPlatformHostSecurityManagerFactory *a4, struct IInspectable **a5, bool a6)
{
  HRESULT v6; // esi@1
  int v8; // [sp+4h] [bp-4h]@1

  v8 = 0;
  v6 = HTMLDocumentSource::Create((int)&v8, a1, a2, (char)a4);
  if ( v6 >= 0 )
    v6 = HTMLDocumentSource::QueryInterface(v8, &_GUID_af86e2e0_b12d_4c6a_9c5a_d7aa65101e90, a3);
  TSmartPointer<HTMLDocumentSource>::_TSmartPointer<HTMLDocumentSource>(&v8);
  return v6;
}

```

调用HTMLDocumentSource::Create并QueryInterface并返回在参数a3中。查看HTMLDocumentSource::Create的代码，也是一个短小的函数：

```
HRESULT __fastcall HTMLDocumentSource::Create(int a1, int a2, int a3, char a4)
{
  int v4; // edi@1
  int v5; // ebx@1
  LPVOID v6; // eax@1
  int v7; // esi@2
  HRESULT v8; // edi@5
  int v10; // [sp+Ch] [bp-4h]@4

  v4 = a2;
  v5 = a1;
  v6 = HeapAlloc(g_hProcessHeap, 0, 0x60u);
  if ( v6 )
    v7 = HTMLDocumentSource::HTMLDocumentSource(v6);
  else
    v7 = 0;
  v10 = v7;
  if ( v7 )
  {
    v8 = HTMLDocumentSource::_Initialize((void *)v7, v4, a3, a4);
    if ( v8 >= 0 )
    {
      v10 = 0;
      *(_DWORD *)v5 = v7;
    }
  }
  else
  {
    v8 = -2147024882;
  }
  TSmartPointer<HTMLDocumentSource>::_TSmartPointer<HTMLDocumentSource>(&v10);
  return v8;
}

```

函数创建HTMLDocumentSource类，并调用_Initialize函数进行初始化。构造函数的代码简单易懂，全部都是赋初值的，跳过不叙述了。接下来查看_Initialize。

_Initialize是一个较长的函数，但是逻辑较为清晰，我把所有IDA没有识别出的guid等全部以注释的形式标记了。该函数先获取了IHTMLEventObj2接口，然后识别环境并设置浏览模式为`__IE_Immersive`（Win8 Immersive Mode），若Immersive Mode生效，再设置成`__IE_ShrinkToFit`（Shrink to fit模式，该模式下浏览器自动将页面收缩成方便打印的大小）模式。

![p2](http://drops.javaweb.org/uploads/images/c64876a458a2ee7f5d51dac80423e82f343d8090.jpg)

然后，调用PrintManagerOptions::Create。这个操作将创建一个PrintManagerOptions对象，并调用其_Initialize方法，干的事情也就是拿到它的IUnkonwn接口，所以这块我们也跳过。

接下来，IE试图打开“res://ieframe.dll/preview.dlg”，很熟悉的字眼。告知该处理程序临时文件位置等设置。

```
HRESULT __thiscall HTMLDocumentSource::_Initialize(void *this, int a2, int a3, char a4)
{
  int v4; // ebx@1
  LPVOID *v5; // eax@1
  HRESULT v6; // esi@1
  int v7; // eax@2
  IUnknown *v8; // esi@3
  LPUNKNOWN *v9; // eax@3
  int v10; // eax@4
  int v11; // eax@13
  int v12; // ecx@13
  const WCHAR *v13; // eax@19
  BSTR v14; // eax@24
  LPMONIKER v15; // ecx@28
  struct IMonikerVtbl *v16; // eax@29
  LONG v18; // [sp-4h] [bp-130h]@23
  struct HTMLDLGINFO *v19; // [sp+0h] [bp-12Ch]@24
  int v20; // [sp+4h] [bp-128h]@24
  int Dst; // [sp+10h] [bp-11Ch]@24
  LPMONIKER v22; // [sp+14h] [bp-118h]@24
  VARIANTARG *v23; // [sp+20h] [bp-10Ch]@24
  char v24; // [sp+28h] [bp-104h]@26
  int *v25; // [sp+2Ch] [bp-100h]@24
  int v26; // [sp+30h] [bp-FCh]@24
  char v27; // [sp+38h] [bp-F4h]@26
  int v28; // [sp+48h] [bp-E4h]@24
  int v29; // [sp+60h] [bp-CCh]@24
  int v30; // [sp+70h] [bp-BCh]@24
  int v31; // [sp+74h] [bp-B8h]@24
  int v32; // [sp+78h] [bp-B4h]@24
  int v33; // [sp+7Ch] [bp-B0h]@24
  BSTR v34; // [sp+80h] [bp-ACh]@24
  int v35; // [sp+84h] [bp-A8h]@24
  VARIANTARG pvargSrc; // [sp+88h] [bp-A4h]@14
  int v37; // [sp+98h] [bp-94h]@5
  int v38; // [sp+9Ch] [bp-90h]@5
  int v39; // [sp+A0h] [bp-8Ch]@5
  int v40; // [sp+A4h] [bp-88h]@5
  int v41; // [sp+A8h] [bp-84h]@14
  int v42; // [sp+ACh] [bp-80h]@14
  LPCWSTR szURL; // [sp+B0h] [bp-7Ch]@14
  int v44; // [sp+B4h] [bp-78h]@14
  int *v45; // [sp+B8h] [bp-74h]@13
  int v46; // [sp+BCh] [bp-70h]@1
  VARIANTARG pvarg; // [sp+C0h] [bp-6Ch]@8
  LPUNKNOWN punkOuter; // [sp+D4h] [bp-58h]@1
  void *v49; // [sp+D8h] [bp-54h]@1
  LPMONIKER ppmk; // [sp+DCh] [bp-50h]@21
  LONG v51; // [sp+E0h] [bp-4Ch]@4
  char v52; // [sp+E7h] [bp-45h]@5
  char v53; // [sp+E8h] [bp-44h]@14
  unsigned int v54; // [sp+124h] [bp-8h]@1
  int v55; // [sp+12Ch] [bp+0h]@1

  v54 = (unsigned int)&v55 ^ __security_cookie;
  punkOuter = 0;
  v4 = (int)this;
  v46 = a3;
  v49 = this;
  v5 = (LPVOID *)TSmartPointer<CDCompLayer>::operator_((char *)this + 52);
  v6 = CoCreateInstance(&CLSID_StdGlobalInterfaceTable, 0, 1u, &_GUID_00000146_0000_0000_c000_000000000046, v5); //guid of IGlobalInterfaceTable
  if ( v6 >= 0 )
  {
    v7 = TSmartPointer<CDCompLayer>::operator_(&punkOuter);
    v6 = HTMLDocumentSource::QueryInterface(v4, &_GUID_00000000_0000_0000_c000_000000000046, v7); //querying IID_IUnknown
    if ( v6 >= 0 )
    {
      v8 = punkOuter;
      v9 = (LPUNKNOWN *)TSmartPointer<CDCompLayer>::operator_(v4 + 56);
      v6 = CoCreateFreeThreadedMarshaler(v8, v9);
      if ( v6 >= 0 )
      {
        v51 = 0;
        v10 = TSmartPointer<IDispEffectConvolveMatrix>::operator_(&v51);
        v6 = (**(int (__stdcall ***)(int, GUID *, int))a2)(a2, &_GUID_3050f48b_98b5_11cf_bb82_00aa00bdce0b, v10); //getting IHTMLEventObj2
        if ( v6 >= 0 )
        {
          v52 = 1;
          v37 = 0;
          v38 = 0;
          v39 = 0;
          v40 = 0;
          if ( (*(int (__stdcall **)(LONG, _DWORD, _DWORD, int *))(*(_DWORD *)v51 + 32))(
                 v51,
                 L"__IE_Immersive",
                 0,
                 &v37) >= 0
            && (_WORD)v37 == 11
            && -1 == (_WORD)v39 )
          {
            *(_QWORD *)&pvarg.vt = 0i64;
            *(_QWORD *)&pvarg.lVal = 0i64;
            if ( (*(int (__stdcall **)(LONG, _DWORD, _DWORD, VARIANTARG *))(*(_DWORD *)v51 + 32))(
                   v51,
                   L"__IE_ShrinkToFit",
                   0,
                   &pvarg) < 0
              || pvarg.vt != 11
              || (v52 = 1, -1 != LOWORD(pvarg.lVal)) )
              v52 = 0;
            VariantClear(&pvarg);
          }
          v45 = (int *)((char *)v49 + 60);
          v11 = TSmartPointer<PrintManagerOptions>::operator_((char *)v49 + 60);
          LOBYTE(v12) = v52;
          v6 = PrintManagerOptions::Create(v12, v11);
          if ( v6 >= 0 )
          {
            v41 = 0;
            v42 = 0;
            szURL = 0;
            v44 = 0;
            memcpy(&v53, L"res://ieframe.dll/preview.dlg", 0x3Cu);
            *(_QWORD *)&pvargSrc.vt = 0i64;
            *(_QWORD *)&pvargSrc.lVal = 0i64;
            if ( (*(int (__stdcall **)(LONG, _DWORD, _DWORD, VARIANTARG *))(*(_DWORD *)v51 + 32))(
                   v51,
                   L"__IE_TemporaryFiles",
                   0,
                   &pvargSrc) >= 0
              && pvargSrc.vt == 8200 )
              VariantCopy((VARIANTARG *)((char *)v49 + 72), &pvargSrc);
            if ( (*(int (__stdcall **)(_DWORD, _DWORD, _DWORD, int *))(*(_DWORD *)v51 + 32))(
                   v51,
                   L"__IE_TemplateUrl",
                   0,
                   &v41) < 0
              || (_WORD)v41 != 8
              || (v13 = szURL) == 0 )
              v13 = (const WCHAR *)&v53;
            ppmk = 0;
            v6 = CreateURLMonikerEx(0, v13, &ppmk, 1u);
            if ( v6 >= 0 )
            {
              *(_QWORD *)&pvarg.vt = 0i64;
              *(_QWORD *)&pvarg.lVal = 0i64;
              pvarg.vt = 13;
              v6 = PrintManagerOptions::QueryInterface(
                     *v45,
                     &_GUID_00000000_0000_0000_c000_000000000046,
                     (int)&pvarg.lVal);
              if ( v6 >= 0 )
              {
                v18 = 0;
                v6 = (*(int (__stdcall **)(LONG, _DWORD, _DWORD, _DWORD, LONG, _DWORD, _DWORD))(*(_DWORD *)v51 + 28))(
                       v51,
                       L"__PE_PrintManagerOptions",
                       *(_DWORD *)&pvarg,
                       *(_DWORD *)&pvarg.wReserved2,
                       pvarg.lVal,
                       HIDWORD(pvarg.dblVal),
                       0);
                if ( v6 >= 0 )
                {
                  VariantClear(&pvarg);
                  pvarg.vt = 13;
                  pvarg.lVal = v51;
                  v18 = v51;
                  (*(void (__stdcall **)(LONG))(*(_DWORD *)v51 + 4))(v51);
                  HTMLDLGINFO::HTMLDLGINFO(&Dst);
                  v32 = 0;
                  v33 = 0;
                  v34 = 0;
                  v35 = 0;
                  LOWORD(v32) = 8;
                  v14 = SysAllocString(0);
                  Dst = 0;
                  v29 = 0;
                  v34 = v14;
                  v22 = ppmk;
                  v23 = &pvarg;
                  v25 = &v32;
                  v28 = 720;
                  v26 = 1;
                  v30 = 1;
                  v31 = v46;
                  v6 = InternalModelessDialog(v19, v20);
                  if ( v6 >= 0 )
                    *((_BYTE *)v49 + 88) = a4;
                  VariantClear((VARIANTARG *)&v32);
                  VariantClear((VARIANTARG *)&v27);
                  CStr::_Free(&v24);
                }
              }
              VariantClear(&pvarg);
            }
            v15 = ppmk;
            ppmk = 0;
            if ( v15 )
            {
              v16 = v15->lpVtbl;
              v18 = (LONG)v15;
              v16->Release(v15);
            }
            VariantClear(&pvargSrc);
            VariantClear((VARIANTARG *)&v41);
          }
          VariantClear((VARIANTARG *)&v37);
        }
        TSmartPointer<IMFGetService>::_TSmartPointer<IMFGetService>(&v51);
      }
    }
  }
  TSmartPointer<IMFGetService>::_TSmartPointer<IMFGetService>(&punkOuter);
  return v6;
}

```

最后，通过InternalModelessDialog启动该窗口实现预览

```
HRESULT __usercall InternalModelessDialog<eax>(int a1<edx>, int a2<ecx>, HRESULT a3<esi>)

```

那么这个预览窗口中显示的文档和其他的到底有什么不同呢？根据MSDN文档的意思是：有点像禁止了Script的WebBrowser。代码将Layout当作一个容器来显示预览后的内容。在Modeless Window中，我们不能F12，不能呼出右键菜单，怎么办？我们有另一种方法——通过IE暴露的接口来取得整个窗口的DOM内容。

0x05 使用C++获取打印预览窗口的body.outerHTML
=================================

* * *

这个逻辑中，预览的窗口标题为“打印预览”。可以使用FindWindow找到对应的窗口并枚举出正确的Server窗口，或是使用Spy++找到窗口的HWND（因为这里我们并不是写一个通用的工具，所以怎么方便怎么来）。

注意目标窗口是Internet Explorer_Server而不是外层的Internet Explorer_TridentDlgFrame。这里使用的代码如下：

```
// prjFindPrintview.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include <Windows.h>
#include <mshtml.h>
#include <Exdisp.h>
#include <atlbase.h>
#include <SHLGUID.h>
#include <oleacc.h>
#include <comdef.h>
#include <tchar.h>
#pragma comment(lib, "Oleacc.lib")

int _tmain(int argc, _TCHAR* argv[])
{
    ::CoInitialize(NULL);

    HRESULT hr = S_OK;

    UINT nMsg = ::RegisterWindowMessage(_T("WM_HTML_GETOBJECT"));
    LRESULT lRes = 0;
    ::SendMessageTimeout((HWND)0x000711FA, nMsg, 0L, 0L, SMTO_ABORTIFHUNG, 1000, (PDWORD)&lRes);

    CComPtr<IHTMLDocument2> spDoc;
    hr = ObjectFromLresult(lRes, IID_IHTMLDocument2, 0, (void**)&spDoc);
    if (FAILED(hr)) 
        return -1;

    CComPtr<IHTMLElementCollection> spElementCollection;
    hr = spDoc->get_all(&spElementCollection);
    if (FAILED(hr)) 
        return -2;

    long lElementCount;
    hr = spElementCollection->get_length(&lElementCount);
    if (FAILED(hr)) 
        return -3;

    VARIANT vIndex; vIndex.vt = VT_I4;
    VARIANT vSubIndex; vSubIndex.vt = VT_I4; vSubIndex.lVal = 0;
    for (vIndex.lVal = 0; vIndex.lVal < lElementCount; vIndex.lVal++)
    {
        CComPtr<IDispatch> spDispatchElement;
        if (FAILED(spElementCollection->item(vIndex, vSubIndex, &spDispatchElement)))
            continue;
        CComPtr<IHTMLElement> spElement;
        if (FAILED(spDispatchElement->QueryInterface(IID_IHTMLElement, (void**)&spElement)))
            continue;
        CComBSTR outerHTML;
        spElement->get_outerHTML(&outerHTML);
        OutputDebugStringW(outerHTML);


    }

    ::CoUninitialize();
    return 0;
}

```

取得窗口的DOM如下：

![p3](http://drops.javaweb.org/uploads/images/f266a5f63821a067d79f2771f073382afe413d2a.jpg)

将其输出到文件，自行添上`</BODY></HTML>`即为完整的内容。不过需要记得的是Layout等元素只在打印预览中有效，所以单独提取出来崩溃不了也不要太疑惑，这里只是为了方便了解预览中最终的DOM分布情况而已。

接下来，让我们复现崩溃吧。打开map.yahoo.co.jp，访问出现崩溃的代码，右键预览。只不过这次我们使用缓存文件的方式来精简代码。预览后，从%TEMP%下复制走所有新生成的HTM文件，然后调节打印预览的比例为666%。在确定仍然可以崩溃之后，让我们开始删除无用数据，记下异常偏移e9b102（在我的机器上是这个数字，因为有些崩溃在精简代码时可能变成其他的崩溃，所以最好记下偏移地址，以免中途不知道从什么位置产生了新问题）。多次精简之后，我们留下了下列代码：

```
<!DOCTYPE HTML>
<HTML><HEAD>
</HEAD> 
<BODY>
<DIV style="left: -5000px; top: -5000px; width: 10000px; height: 10000px; text-align: justify; position: absolute; z-index: 0;"><svg 
xmlns="http://www.w3.org/2000/svg" style="position: relative;" viewBox="0 0 10000 10000" 
width="10000" height="10000" />
</DIV>
</BODY></HTML>

```

而且精简到这一步就可以发现，只要发起打印预览，IE就会直接崩溃。所以，为了让IE自动触发崩溃，我们手写一下调用print();即可。

```
<!DOCTYPE HTML>
<HTML><HEAD>
</HEAD> 
<BODY>
<DIV style="left: -5000px; top: -5000px; width: 10000px; height: 10000px; text-align: justify; position: absolute; z-index: 0;"><svg 
xmlns="http://www.w3.org/2000/svg" style="position: relative;" viewBox="0 0 10000 10000" 
width="10000" height="10000" />
</DIV>
<script>print();</script>
</BODY></HTML>

```

跟随调试可以发现，崩溃位置维持不变：

```
0:040> g
(24c8.2960): Access violation - code c0000005 (!!! second chance !!!)
eax=00000000 ebx=00000000 ecx=00000000 edx=00000000 esi=045c9220 edi=0a68eeac
eip=6537b102 esp=0a68eea4 ebp=0a68eeb8 iopl=0         nv up ei pl zr na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010246
MSHTML!CDispParentNode::ComputeVisibleBoundsOnDirtySVGSubtree+0x16:
6537b102 8b33            mov     esi,dword ptr [ebx]  ds:002b:00000000=????????

```

接下来让我们看看打印预览窗口的DOM结构。因为DIV的STYLE属性是触发崩溃的关键条件之一，但是我们又想拿到预览窗口的DOM，所以我们得做一些改动，先手动删除部分STYLE，然后预览，这时，便可使用我们之前的程序抓出DOM。

篇幅考虑我就不扯淡再去看这个DOM了，直接以上述精简后的代码开始分析工作。

0x06 崩溃分析
=========

* * *

在崩溃后查看崩溃栈如下：

```
0:033> kvn
 # ChildEBP RetAddr  Args to Child              
00 0b2df530 64c7b6b7 0b2df75c 0b2df75c 64c7b63a MSHTML!CDispParentNode::ComputeVisibleBoundsOnDirtySVGSubtree+0x16 (FPO: [Non-Fpo])
01 0b2df774 645de05b 0b2df7bc 0b2df79a 0b2dfb3c MSHTML!`CBackgroundInfo::Property<CBackgroundImage>'::`7'::`dynamic atexit destructor for 'fieldDefaultValue''+0x2b2eb
02 0b2df860 64b4110c 0b2dfb3c 0b2dfb3c 0b2dfb3c MSHTML!Layout::FlowBoxBuilder::BuildBoxItem+0x89 (FPO: [1,51,4])
03 0b2df87c 64b410d7 0b2dfb3c 0d82d0e0 0b2df8e4 MSHTML!Layout::LayoutBuilder::BuildBoxItem+0x2e (FPO: [Non-Fpo])
04 0b2df88c 64b40193 0b2dfb3c 0b2df908 64e657d0 MSHTML!Layout::LayoutBuilder::Move+0x57 (FPO: [Non-Fpo])
05 0b2df8e4 65358d8d 0d83264c 00000000 0d83264c MSHTML!Layout::LayoutBuilderDriver::BuildElementLayout+0xce (FPO: [Non-Fpo])
06 0b2df974 65359137 ffffffff 00000001 04c29ab4 MSHTML!Layout::MultiFragmentBoxBuilder::BuildCrossFragmentPositionedElement+0x1c3 (FPO: [Non-Fpo])
07 0b2df9d4 64ec4753 0b2dfa24 0d82d020 0d82cff0 MSHTML!Layout::MultiFragmentBoxBuilder::PositionAndArrangeCrossFragmentAbsolutePositionedElement+0x17e (FPO: [Non-Fpo])
08 0b2dfa2c 645d06b0 0d7e8ba0 04c29ab4 0b2dfb3c MSHTML!`CBackgroundInfo::Property<CBackgroundImage>'::`7'::`dynamic atexit destructor for 'fieldDefaultValue''+0xce2e3
09 0b2dfb14 645d72b9 0b2dfb3c 0b2dfb48 645d6ae0 MSHTML!Layout::PageCollection::LayoutPagesCore+0x37e (FPO: [Non-Fpo])
0a 0b2dfb40 65340900 65340760 0b2dfb88 0d832648 MSHTML!Layout::PageCollection::LayoutPages+0xca (FPO: [Non-Fpo])
0b 0b2dfb7c 64a9ec7e 00100000 04c29500 00000000 MSHTML!Layout::PageCollection::DoLayout+0x1a0 (FPO: [1,9,4])
0c 0b2dfbcc 64592161 00100000 64a7d7f0 00000000 MSHTML!CView::ExecuteLayoutTasks+0x159 (FPO: [Non-Fpo])
0d 0b2dfc24 64a7d840 00000000 64a7d7f0 0b2dfc54 MSHTML!CView::EnsureView+0x3bb (FPO: [1,15,4])
0e 0b2dfc44 64585813 04c29b38 00000000 00000001 MSHTML!CView::EnsureViewCallback+0x50 (FPO: [Non-Fpo])
0f 0b2dfc8c 6456d52c 3f72ceb5 00000000 6456cc90 MSHTML!GlobalWndOnMethodCall+0x17b (FPO: [Non-Fpo])
10 0b2dfce0 769f62fa 000825e0 00008002 00000000 MSHTML!GlobalWndProc+0x103 (FPO: [Non-Fpo])
11 0b2dfd0c 769f6d3a 6456cc90 000825e0 00008002 USER32!InternalCallWinProc+0x23
12 0b2dfd84 769f77c4 0539315c 6456cc90 000825e0 USER32!UserCallWinProcCheckWow+0x109 (FPO: [Non-Fpo])
13 0b2dfde4 769f788a 6456cc90 00000000 0b2dfe40 USER32!DispatchMessageWorker+0x3bc (FPO: [Non-Fpo])
14 0b2dfdf4 6507e640 0b2dfe24 0b2dfe4c 6629d470 USER32!DispatchMessageW+0xf (FPO: [Non-Fpo])
15 0b2dfe40 6ed93a31 05c7ab90 00000000 00000000 MSHTML!ModelessThreadProc+0x1a0 (FPO: [1,13,4])

```

MSHTML!CDispParentNode::ComputeVisibleBoundsOnDirtySVGSubtree是一个Thiscall，代码十分简单，就是调用自己一个成员函数：

```
int __thiscall CDispParentNode::ComputeVisibleBoundsOnDirtySVGSubtree(void *this, int a2, int a3, int a4, float a5)
{
  return (*(int (__stdcall **)(_DWORD, int, _DWORD, _DWORD, _DWORD, _DWORD))(*(_DWORD *)this + 216))(
           0,
           a3,
           0,
           0,
           LODWORD(a5),
           0);
}

```

查看函数代码，很明显，this指针为null。

```
0:033> uf .
MSHTML!CDispParentNode::ComputeVisibleBoundsOnDirtySVGSubtree:
6537b0ec 8bff            mov     edi,edi
6537b0ee 55              push    ebp
6537b0ef 8bec            mov     ebp,esp
6537b0f1 d94514          fld     dword ptr [ebp+14h]
6537b0f4 33c0            xor     eax,eax
6537b0f6 53              push    ebx
6537b0f7 56              push    esi
6537b0f8 57              push    edi
6537b0f9 8bfc            mov     edi,esp
6537b0fb 8bd9            mov     ebx,ecx    ; ebx = ecx = this
6537b0fd 50              push    eax
6537b0fe 51              push    ecx
6537b0ff d91c24          fstp    dword ptr [esp]
6537b102 8b33            mov     esi,dword ptr [ebx]  ; esi = *ebx

```

查看上一层

```
0:033> ub .
MSHTML!`CBackgroundInfo::Property<CBackgroundImage>'::`7'::`dynamic atexit destructor for 'fieldDefaultValue''+0x2b2d4:
64c7b6a0 83ec08          sub     esp,8
64c7b6a3 d95c2404        fstp    dword ptr [esp+4]
64c7b6a7 51              push    ecx
64c7b6a8 51              push    ecx
64c7b6a9 8b08            mov     ecx,dword ptr [eax]
64c7b6ab e8307699ff      call    MSHTML!Layout::LayoutBox::GetDisplayNodeAsParent (64612ce0)
64c7b6b0 8bc8            mov     ecx,eax
64c7b6b2 e835fa6f00      call    MSHTML!CDispParentNode::ComputeVisibleBoundsOnDirtySVGSubtree (6537b0ec)

```

很明显MSHTML!Layout::LayoutBox::GetDisplayNodeAsParent返回了NULL。

```
int __thiscall Layout::LayoutBox::GetDisplayNodeAsParent(void *this)
{
  int pThisVar; // eax@1
  int nResult; // edx@1
  int v3; // esi@2
  int v4; // edi@2
  int v5; // eax@5

  pThisVar = (*(int (**)(void))(*(_DWORD *)this + 788))();
  nResult = pThisVar;
  if ( !pThisVar )
    goto Cleanup;
  v3 = *(_DWORD *)(pThisVar + 28);
  v4 = pThisVar;
  if ( *(_BYTE *)(v3 + 56) & 1
    && !*(_BYTE *)(*(_DWORD *)(__readfsdword(44) + 4 * LODWORD(_tls_index)) + 36)
    && *(_DWORD *)(v3 + 4) != *(_DWORD *)(pThisVar + 8) )
  {
    v5 = *(_DWORD *)(pThisVar + 4);
    if ( !v5 )
      v5 = nResult;
    if ( v5 != nResult )
      v4 = v5;
  }
  if ( !(*(_BYTE *)(v4 + 21) & 0x20) )
  {
Cleanup:
    nResult = NULL;
  }
  return nResult;
}

```

可以简单跟踪一下代码看看到底是哪儿出现了问题。为了避免重复断到断点上（Layout的调用是十分频繁的），可以

```
bp MSHTML!ModelessThreadProc 

```

触发后

```
bc 0
bp MSHTML!Layout::FlowBoxBuilder::BuildBoxItem

```

触发后

```
bc 0
bp MSHTML!Layout::LayoutBox::GetDisplayNodeAsParent

```

这样就没问题了

```
0:031> g
Breakpoint 1 hit
eax=05618f80 ebx=0c07f060 ecx=0eebc4e0 edx=00000002 esi=0ee946e0 edi=0ee5ecb0
eip=64612ce0 esp=0c07f04c ebp=0c07f28c iopl=0         nv up ei pl nz ac po nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000212
MSHTML!Layout::LayoutBox::GetDisplayNodeAsParent:
64612ce0 8bff            mov     edi,edi
0:031> k
ChildEBP RetAddr  
0c07f048 64c7b6b0 MSHTML!Layout::LayoutBox::GetDisplayNodeAsParent
0c07f28c 645de05b MSHTML!`CBackgroundInfo::Property<CBackgroundImage>'::`7'::`dynamic atexit destructor for 'fieldDefaultValue''+0x2b2e4
0c07f378 64b4110c MSHTML!Layout::FlowBoxBuilder::BuildBoxItem+0x89
0c07f394 64b410d7 MSHTML!Layout::LayoutBuilder::BuildBoxItem+0x2e
0c07f3a4 64b40193 MSHTML!Layout::LayoutBuilder::Move+0x57
0c07f3fc 65358d8d MSHTML!Layout::LayoutBuilderDriver::BuildElementLayout+0xce

```

再度跟踪可以发现是

```
pThisVar = (*(int (**)(void))(*(_DWORD *)this + 788))();// MSHTML!Layout::SvgBox::GetDisplayNode //returns null
nResult = pThisVar;
if ( !pThisVar )
    goto Cleanup; //return NULL(0);

```

查看GetDisplayNode，很明显，校验失败，返回了0.

```
int __thiscall Layout::SvgBox::GetDisplayNode(int this)
{
  int result; // eax@2

  if ( !(*(_BYTE *)(this + 56) & 4) || *(_BYTE *)(*(_DWORD *)(__readfsdword(44) + 4 * LODWORD(_tls_index)) + 36) )
    result = *(_DWORD *)(this + 16);
  else
    result = 0;
  return result;
}

```

加上对内存的跟踪，我们可以断定这是一个空指针问题。不过这倒也给了一个提醒——是否一些在网页内不能触发的问题，通过打印预览就又可以做了呢？Fuzzer看来也可以加上这个策略，试一试打印预览是否健壮。