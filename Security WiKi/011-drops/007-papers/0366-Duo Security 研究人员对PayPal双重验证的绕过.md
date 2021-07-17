# Duo Security 研究人员对PayPal双重验证的绕过

from: https://www.duosecurity.com/blog/duo-security-researchers-uncover-bypass-of-paypal-s-two-factor-authentication

0x00 简介
-------

* * *

来自Duo Security高级研究团队Duo Labs的人员，发现有可能绕过PayPal的双重验证机制（用PayPal自己的话来说是Security Key机制）。研究人员发现在PayPal的API web service（api.paypal.com）里存在一个认证方面的缺陷，包括PayPal自己官方的移动应用和很多第三方应用都会用到这个API。

截至到这篇文章发布（6月25日），Paypal还只是暂时采取了规避措施，官方也在努力修复此问题。为了让PayPal的用户意识到他们账户的安全性，我们决定将漏洞公开。

在漏洞研究过程中，我们也要感谢来自EverydayCarry 的Dan的帮助。

0x01 影响
-------

* * *

攻击者只需要一个账户和密码就可以绕过PayPal的二次验证机制，导致PayPal的Security Key机制形同虚设。

PayPal的移动端并不支持二次认证账户，所以移动端的应用在登陆的时候会忽略第二步验证，导致攻击者可以一步登陆成功。

我们在这里写了一个POC来说明这个问题，在这个POC里，我们模拟移动端应用直接去请求PayPal API，但是这些账户都是没有通过二次认证的。这个POC与两个独立的PayPal API通信，一个负责认证（通过基本的凭证），还有一个负责转账。

注意，这个漏洞并不影响web端的接口。但是攻击者依然可以直接通过API获取信息，所以影不影响web端无所谓。

0x02 技术细节
---------

* * *

这个漏洞主要出在PayPal API的认证上（api.paypal.com），由于此系统主要是通过OAuth来认证和授权的，并没有强制执行两步认证，所以出了问题。

从视频里可以看到，PayPal 的ios客户端在现实用户账户信息和历史交易记录的时候并没有强制用户退出。正是这个特性，我们可以看看背后发生了什么。利用Burp截获PayPal客户端的请求，我们仔细分析了认证过程，重点关注开启了双重认证账户和没有开启双重认证账户之间的区别。

下面的截图是一个到api.paypal.com的OAuth 请求。请求body 里面除了其他参数，主要有认证凭证（用户名和密码）和一些设备指纹信息。这个请求与PayPal官方开发者文档中描述的完全一样，并没有什么不对的地方。

![enter image description here](http://drops.javaweb.org/uploads/images/1309a3d66adc2bd29043332bf73b3aa3dba68080.jpg)

但是在下面这个截图里，我们看到上面请求的response ，在这个JSON 里我们看到了一些PayPal web服务url，各种token（主要是跟OAuth相关的），还有双重认证的属性。

![enter image description here](http://drops.javaweb.org/uploads/images/9972dad315d7f3bd964f2722b24e430dea4442cb.jpg)

注意上图中红框部分，这里的双重认证属性值是true，因此会导致移动应用跳转到登陆页并且会弹出错误信息，比如提醒设备目前还不支持双重认证。

![enter image description here](http://drops.javaweb.org/uploads/images/767e1f237ce1ddd83fcbf311af26492bf43e6695.jpg)

android客户端也是同样的请求，同样的错误提示。

![enter image description here](http://drops.javaweb.org/uploads/images/f6f371f10995081c582a3f0ba40d5986a0bddb76.jpg)

利用Burp将2fa_enabled属性值修改为false，

![enter image description here](http://drops.javaweb.org/uploads/images/52362b69eea93c04697de8d30983530c55c8dff6.jpg)

修改了值以后，尽管账户并没有进行第二步认证，但是应用并没有出错。尽管漏洞是出在服务端，但是这个问题相当于客户端已经通过了两步认证。

![enter image description here](http://drops.javaweb.org/uploads/images/cd6d9fffd2b01d6bfbb90d9e34f5461f71d33905.jpg)

回到开始那个认证的请求的response，我们发现JSON里还有一个session id。

![enter image description here](http://drops.javaweb.org/uploads/images/01eae5c0f6fafb85d2620c36bbe71ec3fcc4b806.jpg)

我们都知道，这个session id可以用来授权mobileclient.paypal.com，mobileclient.paypal.com这个站点提供了基于SOAP协议的API服务，可以用来做一些账户方面的附加功能，包括但不限于转账。

现在我们来模拟移动端的转账步骤，可以看到，转账是客户端和服务端基于SOAP封装的请求来进行的。整个过程可以分解为四个步骤，每个步骤都需要一个独一无二的值。

下面截图是一个例子，描述了利用上文中的session id来向mobileclient.paypal.com发起请求：

![enter image description here](http://drops.javaweb.org/uploads/images/28dba30c831696ea502e199e8811ff18c4efbbbe.jpg)

这里我们用py写了一个POC，模拟移动端去利用这个漏洞。这个脚本的参数包括用户名、密码、一个美元账户、一个接受账户。具体有以下步骤：

1.  在api.paypal.com认证。
2.  显示一些受限的账户信息（包括“钱包”，链接的资金账户，比如借记卡和信用卡）
3.  获取session_token（session id）的值。
4.  利用这个session id在mobileclient.paypal.com进行一些账户操作，比如转账。

下面的截图是我们利用POC脚本从一个已经开启双重认证的账户向一个接受账户中转账了1美元。

![enter image description here](http://drops.javaweb.org/uploads/images/7f1b547d909adbd94e22a28c9da487beaffdc198.jpg)

下面的截图是转账证明：

![enter image description here](http://drops.javaweb.org/uploads/images/2bbdd221a7a8543f21fa17240549d472a19c23c7.jpg)

我们在6月23号重新测试了这个漏洞，发现PayPal官方已经在着手修复这个漏洞。开启了双重认证的账户在请求api.paypal.com的时候已经不会返回session_token了，也避免了直接与mobileclient.paypal.com通信。

但是钱包信息依然没有屏蔽，意味着这个漏洞还是有一些危害。下面这个截图是我们用POC重新测试的结果，注意session_token已经没有了。

![enter image description here](http://drops.javaweb.org/uploads/images/b5f3092ad235291bfae7ec6a13db92ede7bd6011.jpg)

利用官方的移动客户端，可以更加明显的看出PayPal官方已经更改了API服务的认证流程。

![enter image description here](http://drops.javaweb.org/uploads/images/97f1d8ec4b6ef87d3e9229ca1f978c9fa70bb5f0.jpg)

在6月24号，我们又测试了这个问题，发现钱包信息已经屏蔽。下面截图是测试结果，没有access_token了也就意味着不能在api.paypal.com进行任何操作，包括查看钱包信息。

![enter image description here](http://drops.javaweb.org/uploads/images/5007706276e6d7bd317983ef259497b54eb961fe.jpg)

0x03 结论
-------

* * *

虽然说现在的厂商推出双重验证机制能更好的保护用户的信息和账户安全，但是如果一旦被绕过，这些可能就成为浮云。用户很有可能会被这些厂商的承诺所麻痹。现在越来越多的用户信息在互联网上传播，通过一个设计安全的双重验证机制来提高账户安全已经迫在眉睫。

最后我们希望PayPal官方能很好的修复这个漏洞，并且推动移动客户端和第三方应用也支持双重验证机制。