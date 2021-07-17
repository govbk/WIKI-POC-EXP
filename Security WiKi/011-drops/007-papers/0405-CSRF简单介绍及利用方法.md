# CSRF简单介绍及利用方法

### 0x00 简要介绍

* * *

CSRF（Cross-site request forgery）跨站请求伪造，由于目标站无token/referer限制，导致攻击者可以用户的身份完成操作达到各种目的。根据HTTP请求方式，CSRF利用方式可分为两种。

### 0x01 GET类型的CSRF

* * *

这种类型的CSRF一般是由于程序员安全意识不强造成的。GET类型的CSRF利用非常简单，只需要一个HTTP请求，所以，一般会这样利用：

```
<img src=http://wooyun.org/csrf.php?xx=11 /> 

```

如下图，在访问含有这个img的页面后，成功向http://wooyun.org/csrf.php?xx=11发出了一次HTTP请求。所以，如果将该网址替换为存在GET型CSRF的地址，就能完成攻击了。

![20130701174309_63157.jpg](http://drops.javaweb.org/uploads/images/a49e0490554eb8ab7a1e621d3c9e63bd75b41070.jpg)

乌云相关案例：

http://wooyun.org/bugs/wooyun-2010-023783

http://wooyun.org/bugs/wooyun-2010-027258 (还未公开)

### 0x02 POST类型的CSRF

* * *

这种类型的CSRF危害没有GET型的大，利用起来通常使用的是一个自动提交的表单，如：

```
<form action=http://wooyun.org/csrf.php method=POST>
<input type="text" name="xx" value="11" />
</form>
<script> document.forms[0].submit(); </script> 

```

访问该页面后，表单会自动提交，相当于模拟用户完成了一次POST操作。

乌云相关案例：

http://wooyun.org/bugs/wooyun-2010-026622

http://wooyun.org/bugs/wooyun-2010-022895

### 0x03 其他猥琐流CSRF

* * *

过基础认证的CSRF(常用于路由器):

POC:

```
<img src=http://admin:admin@192.168.1.1 /> 

```

加载该图片后，路由器会给用户一个合法的SESSION，就可以进行下一步操作了。

乌云相关案例：

[WooYun: TP-LINK路由器CSRF，可干许多事（影响使用默认密码或简单密码用户）](http://www.wooyun.org/bugs/wooyun-2013-026825)

### 0x04 如何修复

* * *

针对CSRF的防范，有以下几点要注意：

#### 关键操作只接受POST请求

#### 验证码

CSRF攻击的过程，往往是在用户不知情的情况下构造网络请求。所以如果使用验证码，那么每次操作都需要用户进行互动，从而简单有效的防御了CSRF攻击。

但是如果你在一个网站作出任何举动都要输入验证码会严重影响用户体验，所以验证码一般只出现在特殊操作里面，或者在注册时候使用

#### 检测refer

常见的互联网页面与页面之间是存在联系的，比如你在www.baidu.com应该是找不到通往www.google.com的链接的，再比如你在论坛留言，那么不管你留言后重定向到哪里去了，之前的那个网址一定会包含留言的输入框，这个之前的网址就会保留在新页面头文件的Referer中

通过检查Referer的值，我们就可以判断这个请求是合法的还是非法的，但是问题出在服务器不是任何时候都能接受到Referer的值，所以Refere Check 一般用于监控CSRF攻击的发生，而不用来抵御攻击。

#### Token

目前主流的做法是使用Token抵御CSRF攻击。下面通过分析CSRF 攻击来理解为什么Token能够有效

CSRF攻击要成功的条件在于攻击者能够预测所有的参数从而构造出合法的请求。所以根据不可预测性原则，我们可以对参数进行加密从而防止CSRF攻击。

另一个更通用的做法是保持原有参数不变，另外添加一个参数Token，其值是随机的。这样攻击者因为不知道Token而无法构造出合法的请求进行攻击。

Token 使用原则

```
Token要足够随机————只有这样才算不可预测
Token是一次性的，即每次请求成功后要更新Token————这样可以增加攻击难度，增加预测难度
Token要注意保密性————敏感操作使用post，防止Token出现在URL中

```

### 0x05 测试CSRF中注意的问题

* * *

如果同域下存在xss的话，除了验证码，其他的方式都无法防御这个问题。

有个程序后端可能是用REQUEST方式接受的，而程序默认是POST请求，其实改成GET方式请求也可以发送过去，存在很严重的隐患。

当只采用refer防御时，可以把请求中的修改成如下试试能否绕过：

原始refer：`http://test.com/index.php`

测试几种方式（以下方式可以通过的话即可能存在问题）：

```
http://test.com.attack.com/index.php
http://attack.com/test.com/index.php
[空]

```

refer为空构造的方法：

```
由于浏览器特性，跨协议请求时不带refer（Geckos内核除外），比如https跳到http，如果https环境不好搭建的话，ftp其实也是可以的：）

<iframe src="data:text/html,<script src=http://www.baidu.com></script>"> //IE不支持

利用 xxx.src='javascript:"HTML代码的方式"'; 可以去掉refer，IE8要带。
<iframe id="aa" src=""></iframe>
<script>
document.getElementById("aa").src='javascript:"<html><body>wooyun.org<scr'+'ipt>eval(你想使用的代码)</scr'+'ipt></body></html>"';
</script>
//来自于二哥gainover
```