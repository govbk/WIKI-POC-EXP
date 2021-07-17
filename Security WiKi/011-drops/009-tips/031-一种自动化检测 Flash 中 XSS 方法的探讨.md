# 一种自动化检测 Flash 中 XSS 方法的探讨

作者：piaca

0x00 前面的话
---------

* * *

对于如何检测 Flash 中的 XSS，每个人都有自己的方法，无论是使用成型的自动化工具（比如 swfscan）还是自己开发自动化工具（先反编译，再对 actionscript 代码审计）还是直接人工对代码进行审计。都能够检测到 Flash 中存在的 XSS 漏洞。但是这些方法会存在一些问题，如：

*   自动化工具属于静态分析，误报比较高，需要投入大量人工精力去加以分析
*   完全人工效果最好，但是也更加耗费精力

在这里我们来探讨一种动态检测 Flash 中 XSS 的方法，该方法有自己的优点，但是也有比较明显的缺点，所以本文的标题定位于“探讨”。

0x01 原理
-------

* * *

所谓动态检测，就是通过程序加载 Flash 插件，然后再载入 Flash 文件，对事件和错误信息进行捕捉，再对信息分析来判断 Flash 中是否存在 XSS 漏洞。

先来看下面两张图，以 Firefox 浏览器为例：

![enter image description here](http://drops.javaweb.org/uploads/images/2b50abc7f899f8a923f5e00a4d02acbd8a5d3e2a.jpg)

Firefox 访问[http://test.com/xss.swf?alert=1](http://test.com/xss.swf?alert=1)，Flash 成功执行 JS 代码，弹出对话框。

![enter image description here](http://drops.javaweb.org/uploads/images/7a25d08805bdb13df503d9931fd6736d200922af.jpg)

Firefox 访问[http://test.com/xss.swf?alert=1\"](http://test.com/xss.swf?alert=1%5C%22)，Flash 执行 JS 报错，显示错误详细信息。Firefox 能够显示 Flash 执行 JS 错误时的详细错误信息。

到这里也就明白检测的原理了，就是：

*   程序调用 Firefox
*   Firefox 加载 Flash 插件
*   Firefox 访问对参数经过构造的 Flash 链接，比如[http://test.com/xss.swf?alert=1\"](http://test.com/xss.swf?alert=1%5C%22)
*   程序捕捉错误信息或者 alert 事件
*   根据错误信息或者 alert 事件信息来判断该 Flash 是否存在 XSS 漏洞

0x02 具体实现
---------

* * *

具体如何实现呢？我们不会真的调用 Firefox，而是直接采用一套开源的可以解析 JS 的工具包：CasperJS。下面看下 CasperJS 官网的一段介绍：

```
CasperJS is an open source navigation scripting & testing utility written in Javascript for the PhantomJS WebKit headless browser and SlimerJS (Gecko).

```

CasperJS 目前支持两种引擎：PhantomJS（WebKit内核）和 SlimerJS（Gecko内核）。Gecko内核就是 Firefox 所使用的内核，又通过 CasperJS 文档了解到，使用 SlimerJS 引擎时候可以通过 loadPlugins 来加载 Flash 插件。

所以我们就可以通过 CasperJS 来完成我们的功能需求，下面是代码实现：

flash_detect.js

```
var casper = require('casper').create({
    pageSettings: {
        loadImages:  true, 
        loadPlugins: true // load flash plugin
    },
    logLevel: "info",
    verbose: false
});

casper.start('about:blank', function() {});

// catch alert 
casper.on('remote.alert', function(message) {
    this.echo('{"type": "alert", "msg":"' + message + '"}');
});

// catch page error info
casper.on('page.error', function(message, trace) {
        this.echo('{"type": "error", "msg":"' + message + '"}');
});

var url = casper.cli.get(0);

casper.thenOpen(url, function() {
        this.wait(2000, function(){})   // delay 2's
});

casper.run();

```

代码很简单，就是通过 CasperJS 来访问 Flash 文件，然后捕捉页面中的错误信息和 alert 事件。在这里有一点需要注意就是有的 Flash 不会立即执行 JS 代码，所以我们在打开一个 Flash 文件后，在当前的页面停留 2 秒。

0x03 执行效果
---------

* * *

我们刚才那个 Flash 文件用这个检测代码检测下看看效果 ，如下：

```
piaca at piaca in ~/source$ casperjs --engine=slimerjs flash_detect.js "http://test.com/xss.swf?alert=1"
{"type": "alert", "msg":"1"}

piaca at piaca in ~/source$ casperjs --engine=slimerjs flash_detect.js "http://test.com/xss.swf?alert=1\\\""
{"type": "error", "msg":"SyntaxError: missing ) after argument list"}

```

0x05 写在后面的话
-----------

* * *

实际中我通过访问网上的一些业务，把其中的 Flash 抓下来，然后通过程序去检测，效果还是不错的。当然这其中包括我们自己业务中的 Flash XSS 漏洞。

但是目前的检测程序只能是一个 Demo，要想在生产环境中使用，还需要解决以下问题：

*   效率：目前是单进程单线程进行检测，会影响检测效率，同时由于 SlimerJS 会打开一个 GUI 窗口，在一定程度上也会影响效率；
*   误报：在 Demo 中我们没有过多的处理错误信息，所以在实际测试中会有比较多的误报；
*   参数：这里的参数只是 Flash 文件接收的参数，我们通过日志分析等可以快速获取业务中的 Flash 文件，但是如何获取 Flash 接收的所有参数名呢？

上面几个问题并不是致命的问题，我们可以通过多种方法去解决，但是正如前面所说的这个检测程序有个致命的缺点，那就是：

*   这个检测脚本只能检测很明显的 XSS 漏洞，如果 Flash 中对参数有一定的处理措可能就无法进行检测了；

所以本文仅仅做自动化检测 Flash 中 XSS 漏洞的探讨，如果你有好的方法，希望能与我交流。thx。