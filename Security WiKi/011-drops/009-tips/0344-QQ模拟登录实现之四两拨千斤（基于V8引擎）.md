# QQ模拟登录实现之四两拨千斤（基于V8引擎）

0x00 概述
=======

* * *

很多时候，我们需要模拟QQ自动登录的场景，比如爬取QQ页面的时候，我们需要登录，当然，还有其它的需求就不方便说了。

比较简单的帐号登录，基本上都是发送一个请求包， 最多再伪造一下UserAgent，加一个验证码，就能搞定。

然而当我看到鹅厂的的登录接口时，内心是崩溃的，加密的过程让我有点惊慌失措。

我们访问一下QQ的登录页面：

[http://ui.ptlogin2.qq.com/cgi-bin/login?hide_title_bar=0&low_login=0&qlogin_auto_login=1&no_verifyimg=1&link_target=blank&appid=636014201&target=self&s_url=http%3A//www.qq.com/qq2012/loginSuccess.htm](http://ui.ptlogin2.qq.com/cgi-bin/login?hide_title_bar=0&low_login=0&qlogin_auto_login=1&no_verifyimg=1&link_target=blank&appid=636014201&target=self&s_url=http%3A//www.qq.com/qq2012/loginSuccess.htm)

通常会看到如下页面

![p1](http://drops.javaweb.org/uploads/images/90fc07d6a98e531773c3f9fd2712b2a37d8e583a.jpg)

简单的分析一下这个登录页面，这里QQ支持3种登陆方式：

*   手机QQ二维码登录
*   用户名密码登录
*   客户端快速登录

登录页面展示的逻辑如下：

![p2](http://drops.javaweb.org/uploads/images/27ce1b54beab324b9e5805978371a27d7f33e734.jpg)

从自动化的角度来考虑，第一种方式直接排除，需要手机互动；第三种方式，需要有客户端支持，在win下面也是不错的方案；第二种方式最普遍，也是比较实用，本文重点讲解这种登陆方式的自动化。

0x01 用户名密码登录流程分析
================

* * *

要想实现模拟登录，我们得先搞清楚登录的流程。

所以，我们先来简单看一下用户名密码登录的流程。

PS： 个人习惯把QQ的这个登录页面叫做登录组件。

0x02 整体流程
=========

* * *

![p3](http://drops.javaweb.org/uploads/images/8ebbf232ca9fe9bf53575b49e44ae15f67e8b331.jpg)

### 流程说明

**1.组件加载**

组件加载会做一些准备工作，这里不做详解，只讲一个重要的点：

加载成功后会生成一个长度64的字符串签名：login_sig，后续每一步都需要返回这个签名做校验。签名的字符串通常如下：

```
V0VRhNIHGyezVzO7YgH82MmYj78KF6csGHq3330UXWDa79ZSUPy6J84RwcBzbFaQ

```

**2.登录检测**

简单看了下，主要做了2件事情：一个是用户名校验，一个是登录环境校验。

*   用户名校验：用户名如果不存在，则校验不通过；
*   登录环境校验：风控系统会检测登录环境是否异常如同一IP多个帐号登录失败，则校验不通过；

校验不通过的策略可能不同，弹图片验证码是比较通用的策略；

校验通过会返回一个JSON串，其中3个返回值比较重要，这里说明下：

1.  一个长度为4的校验码verifycode，验证码。校验码verifycode是以叹号！开头，后面是3位大写字母，形式如下：
    
    ```
    !QWE
    
    ```
2.  一个长度为32的16进制格式的盐salt。　盐salt，看了下，其实就是uin（qq号码）的16进制，形式如下：
    
    ```
    \x00\x00\x00\x00\x6b\x68\x90\xfb
    
    ```
3.  一个长度为112的session pt_verifysession_v1，校验session。session pt_verifysession_v1，形式如下：
    
    ```
    69a55c643beecaf5580394c80e9a0f8e800d8c0f3cab6a95ba77e39703e80b83ba2bde15d54558120e782a26f815a3ff97fdfb46ae92db6d
    
    ```

**3.登录**

上述流程正常后，就进入了登录。这里主要是对用户的密码进行特定加密，然后和前面两步获取的必要参数一同提交登录，进行帐号和密码校验。

登录成功会返回一个回调URL和植入认证cookie superkey。

**这里补充说明下：**

QQ的密码的处理流程比较复杂，关键是，除了一些标准密码处理方法（MD5，SALT ，RSA），还有TX自带的TEA算法；

当然，在登录的JavaScript代码里面都有具体实现，感兴趣的同学可以研究下；

整个流程还是蛮有意思的，后续有机会可以给大家分享一下如何自己实现TX的密码加密流程：）

0x03 自动登录实现
===========

* * *

### 自动登录实现的几种方案

通过上面的流程，我们可以看到，自动登录实现的难点在于加密的密码如何获取，这里提供几种登录方案：

*   方案一：当然，最普遍的自动化实现方案，所有流程自己实现，每次请求的数据都自己生成，难点在于加密密码的生成。相对复杂，需要熟悉算法，但是效率高；
*   方案二：最简单暴力的方式，直接调用浏览器引擎，模拟人工输入用户名密码提交表单。简单，但部署稍微复杂，效率低；
*   方案三：如果觉得上述方法太过于暴力，可以选一个折中的方案，我们只在密码生成的时候，使用JavaScript引擎，调用登录组件中的Encrypt算法对密码进行加密，其他流程仍然自动化实现。 简单，并且效率比方案二好；

### 具体实现

所以我们选第三种方案，不用深入具体的密码加密流程和算法，同时实现成本也比较低。

下面我们用python进行一个简单的登录实现：

**我们直接使用V8引擎，调用JavaScript中的Encryption方法进行密码加密是非常简单的：**

```
def tx_pwd_encode_by_js(self, pwd, salt, verifycode):
    """
    调用V8引擎，直接执行TX的登陆JS中的加密方法，不用自己实现其中算法。
    """
    # pwd, salt, verifycode, undefined
    with PyV8.JSContext() as ctxt:
        with open("qq.login.encrypt.js") as jsfile:
            ctxt.eval(jsfile.read())
            encrypt_pwd = ctxt.eval("window.$pt.Encryption.getEncryption('%s', '%s', '%s', undefined)"
                             %(pwd, salt, verifycode) )
            return encrypt_pwd

```

其他的就是体力活了，按照登陆的流程一步一步来，参考如下：

首先，我们第一步先加载组件，获取签名，参考代码：

```
def get_signature(self):
    """
    step 1, load web login iframe and get a login signature
    """
    params = {
        'no_verifyimg': 1,
        "appid": self.appid,
        "s_url": self.urlSuccess,
    }
    params = urllib.urlencode(params)
    url = "%s?%s" %(self.urlRaw, params)
    r = self.session.get(url)
    if 200 != r.status_code:
        error_msg = "[Get signature error] %s %s" %(r.status_code, url)
        return [False, error_msg]
    else:
        self.login_sig = self.session.cookies['pt_login_sig']
        return [True, ""]

```

获取了login_sig后，我们进行第二步，进行登录检测：

```
def check_login(self):
    '''
    step 2: get verifycode and pt_verifysession_v1.
    TX will check username and the login's environment is safe
      '''
    params = {
        "uin": self.uin,
        "appid": self.appid,
        "pt_tea": 1,
        "pt_vcode": 1,
        "js_ver": 10151,
        "js_type": 1,
        "login_sig": self.login_sig,
        "u1": self.urlSuccess,
    }
    params = urllib.urlencode(params)
    url = "%s?%s" %(self.urlCheck, params)
    r = self.session.get(url)
    if 200 != r.status_code:
        error_msg = "[Get verifycode error] %s %s" %(r.status_code, url)
        return [False, error_msg]
    else:
        v = re.findall('\'(.*?)\'', r.text)
        self.check_code = v[0]
        if self.check_code != '0':
            error_msg = "[Verifycode not 0] %s %s" %(self.check_code, url)
            return [False, error_msg]
        self.verifycode = v[1]
        self.salt = v[2]
        self.pt_verifysession_v1 = v[3]
        return [True, ""]

```

检测成功后，我们就可以进行直接登陆，登陆流程代码参考如下：

```
def login(self):
    '''
    step 3: login and get cookie.
    TX will check encrypt(password)
        '''
    encrypt_pwd  =  self.tx_pwd_encode_by_js(self.pwd, self.salt, self.verifycode)

    if not self.pt_verifysession_v1:
        self.pt_verifysession_v1 = self.session.cookies['ptvfsession']
    params = {
        'u': self.uin,
        'verifycode': self.verifycode,
        'pt_vcode_v1': 0,
        'pt_verifysession_v1': self.pt_verifysession_v1,
        'p': encrypt_pwd,
        'pt_randsalt': 0,
        'u1': self.urlSuccess,
        'ptredirect': 0,
        'h': 1,
        't': 1,
        'g': 1,
        'from_ui': 1,
        'ptlang': 2052,
        'action': self.action,
        'js_ver': 10143,
        'js_type': 1,
        'aid': self.appid,
        'daid': 5,
        'login_sig': self.login_sig,
    }
    params = urllib.urlencode(params)
    url = "%s?%s" %(self.urlLogin, params)
    r = self.session.get(url)
    if 200 != r.status_code:
        error_msg = "[Login error] %s %s" %(r.status_code, url)
        return [False, error_msg]
    else:
        v = re.findall('\'(.*?)\'', r.text)
        if v[0] != '0':
            error_msg = "[Login Faild] %s %s" %(url, v[4])
            return [False, error_msg]
        self.nick = v[5]
        return [True, ""]

```

show me the code代码传送门：  
[https://github.com/LeoHuang2015/qqloginjs](https://github.com/LeoHuang2015/qqloginjs)

0x04 总结
=======

* * *

通过这种方式，只需要使用JS引擎，调用JS的加密方法即可生成加密的密码，不需要深入研究TX密码加密的流程和算法，比较简单方便。