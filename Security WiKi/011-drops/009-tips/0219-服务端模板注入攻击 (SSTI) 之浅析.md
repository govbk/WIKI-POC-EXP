# 服务端模板注入攻击 (SSTI) 之浅析

**Author: RickGray (知道创宇404安全实验室)**

在今年的黑帽大会上[James Kettle](http://blog.portswigger.net/)讲解了[《Server-Side Template Injection: RCE for the modern webapp》](https://www.blackhat.com/docs/us-15/materials/us-15-Kettle-Server-Side-Template-Injection-RCE-For-The-Modern-Web-App-wp.pdf)，从服务端模板注入的形成到检测，再到验证和利用都进行了详细的介绍。本文在理解原文内容的基础上，结合更为具体的示例对服务端模板注入的原理和扫描检测方法做一个浅析。

0x00 模板注入与常见Web注入
=================

* * *

就注入类型的漏洞来说，常见 Web 注入有：SQL 注入，XSS 注入，XPATH 注入，XML 注入，代码注入，命令注入等等。注入漏洞的实质是服务端接受了用户的输入，未过滤或过滤不严谨执行了拼接了用户输入的代码，因此造成了各类注入。下面这段代码足以说明这一点：

```
// SQL 注入
$query = "select * from sometable where id=".$_GET['id'];
mysql_query($query);    

------------- 华丽的分割线 -------------    

// 模版注入
$temp->render("Hello ".$_GET['username']);

```

而服务端模板注入和常见Web注入的成因一样，也是服务端接收了用户的输入，将其作为 Web 应用模板内容的一部分，在进行目标编译渲染的过程中，执行了用户插入的恶意内容，因而可能导致了敏感信息泄露、代码执行、GetShell 等问题。其影响范围主要取决于模版引擎的复杂性。

0x01 模板注入原理
===========

* * *

模板注入涉及的是服务端Web应用使用模板引擎渲染用户请求的过程，这里我们使用 PHP 模版引擎[Twig](http://twig.sensiolabs.org/)作为例子来说明模板注入产生的原理。考虑下面这段代码：

```
<?php
require_once dirname(__FILE__).'/../lib/Twig/Autoloader.php';
Twig_Autoloader::register(true);    

$twig = new Twig_Environment(new Twig_Loader_String());
$output = $twig->render("Hello {{name}}", array("name" => $_GET["name"]));  // 将用户输入作为模版变量的值
echo $output;

```

使用 Twig 模版引擎渲染页面，其中模版含有`{{name}}`变量，其模版变量值来自于 GET 请求参数`$_GET["name"]`。显然这段代码并没有什么问题，即使你想通过`name`参数传递一段 JavaScript 代码给服务端进行渲染，也许你会认为这里可以进行 XSS，但是由于模版引擎一般都默认对渲染的变量值进行编码和转义，所以并不会造成跨站脚本攻击：

![](http://drops.javaweb.org/uploads/images/ec1d326c33b705bf26569c08b400d71315d57127.jpg)

但是，如果渲染的模版内容受到用户的控制，情况就不一样了。修改代码为：

```
<?php
require_once dirname(__FILE__).'/../lib/Twig/Autoloader.php';
Twig_Autoloader::register(true);    

$twig = new Twig_Environment(new Twig_Loader_String());
$output = $twig->render("Hello {$_GET['name']}");  // 将用户输入作为模版内容的一部分
echo $output;

```

上面这段代码在构建模版时，拼接了用户输入作为模板的内容，现在如果再向服务端直接传递 JavaScript 代码，用户输入会原样输出，测试结果显而易见：

![](http://drops.javaweb.org/uploads/images/4cded9d752e1bacf3484c0e606531f00683820b7.jpg)

对比上面两种情况，简单的说服务端模板注入的形成终究还是因为服务端相信了用户的输出而造成的（Web安全真谛：永远不要相信用户的输入！）。当然了，第二种情况下，攻击者不仅仅能插入 JavaScript 脚本，还能针对模板框架进行进一步的攻击，此部分只说明原理，在后面会对攻击利用进行详细说明和演示。

0x02 模板注入检测
===========

* * *

上面已经讲明了模板注入的形成原来，现在就来谈谈对其进行检测和扫描的方法。如果服务端将用户的输入作为了模板的一部分，那么在页面渲染时也必定会将用户输入的内容进行模版编译和解析最后输出。

借用本文第二部分所用到的代码：

```
<?php
require_once dirname(__FILE__).'/../lib/Twig/Autoloader.php';
Twig_Autoloader::register(true);    

$twig = new Twig_Environment(new Twig_Loader_String());
$output = $twig->render("Hello {$_GET['name']}");  // 将用户输入作为模版内容的一部分
echo $output;

```

在 Twig 模板引擎里，`{{ var }}`除了可以输出传递的变量以外，还能执行一些基本的表达式然后将其结果作为该模板变量的值，例如这里用户输入`name={{2*10}}`，则在服务端拼接的模版内容为：

```
Hello {{2*10}}

```

Twig 模板引擎在编译模板的过程中会计算`{{2*10}}`中的表达式`2*10`，会将其返回值`20`作为模板变量的值输出，如下图：

![](http://drops.javaweb.org/uploads/images/acbb9b352c6246cb80ae5481ac1b2473f89095c7.jpg)

现在把测试的数据改变一下，插入一些正常字符和 Twig 模板引擎默认的注释符，构造 Payload 为：

```
IsVuln{# comment #}{{2*8}}OK

```

实际服务端要进行编译的模板就被构造为：

```
Hello IsVuln{# comment #}{{2*8}}OK

```

这里简单分析一下，由于`{# comment #}`作为 Twig 模板引擎的默认注释形式，所以在前端输出的时候并不会显示，而`{{2*8}}`作为模板变量最终会返回`16`作为其值进行显示，因此前端最终会返回内容`Hello IsVuln16OK`，如下图：

![](http://drops.javaweb.org/uploads/images/51c19a786f7f92656486515e5e3247c87eff085d.jpg)

通过上面两个简单的示例，就能得到 SSTI 扫描检测的大致流程（这里以 Twig 为例）：

![](http://drops.javaweb.org/uploads/images/653af0b96d065f5af5931b644b1bc33c8e83a6fe.jpg)

同常规的 SQL 注入检测，XSS 检测一样，模板注入漏洞的检测也是向传递的参数中承载特定 Payload 并根据返回的内容来进行判断的。每一个模板引擎都有着自己的语法，Payload 的构造需要针对各类模板引擎制定其不同的扫描规则，就如同 SQL 注入中有着不同的数据库类型一样。

简单来说，就是更改请求参数使之承载含有模板引擎语法的 Payload，通过页面渲染返回的内容检测承载的 Payload 是否有得到编译解析，有解析则可以判定含有 Payload 对应模板引擎注入，否则不存在 SSTI。

0x03 小结
=======

* * *

本文简单介绍服务端模版注入漏洞如常规 Web 注入漏洞之间的关系，分析了其产生的原理，并以 PHP 模板引擎 Twig 为例讲解了 SSTI 常规的扫描和检测方法。虽然说 SSTI 并不广泛存在，但如果开发人员滥用模板引擎，进行不安全的编码，这样 Web 应用就可能出现 SSTI，并且根据其模板引擎的复杂性和开发语言的特性，可能会造成非常严重的问题。

在后续的文章中会针对各语言流行的模板引擎做一个较为详细的研究和分析，给出对应的可利用点和方法。

0x04 参考
=======

* * *

*   [https://www.blackhat.com/docs/us-15/materials/us-15-Kettle-Server-Side-Template-Injection-RCE-For-The-Modern-Web-App-wp.pdf](https://www.blackhat.com/docs/us-15/materials/us-15-Kettle-Server-Side-Template-Injection-RCE-For-The-Modern-Web-App-wp.pdf)
*   [https://www.youtube.com/watch?time_continue=1342&v=BGsAguMPtFw](https://www.youtube.com/watch?time_continue=1342&v=BGsAguMPtFw)

原文出处：[http://blog.knownsec.com/2015/11/server-side-template-injection-attack-analysis/](http://blog.knownsec.com/2015/11/server-side-template-injection-attack-analysis/)