# QQ模拟登录实现后篇

0x00 概述
=======

* * *

本来是和上篇文章一起发的，后来出去，就搁置了。

比较高兴有人参与讨论和吐(B)槽(4)，其实本身也没啥高大上的技术，只是自己在对以前工具做review和重构的时候发现，这些东西很少人在讨论分享，所以也就放出来，算是抛砖引玉。

今天分享两个东西。

*   QQ模拟登录实现之愚公移山（流程自实现）
*   QQ模拟登陆实现之草船借箭（客户端快速登录实现）

当然，干货也就意味着乏味，如果大家不想看文章的可以直接看代码。

第一个分享是对我上一篇文章的补充，[QQ模拟登录实现之四两拨千斤(基于V8引擎)](http://drops.wooyun.org/tips/13556)

自己参考TX JS代码实现的加密流程，因为个人能力有限，所以TX的tea算法是直接引用的hoxide 2005基于python的实现。

第二个分享其实是主要是利用QQ客户端实现快速登录，快速登录对环境有一定的依赖，但是也有很多好处，我们不用处理密码；当然，这种登录方式的使用场景比较有限，目前主要在爬虫和扫描器的场景。

0x01 QQ模拟登录实现之愚公移山（流程算法实现）
==========================

* * *

在上一篇文章：[QQ模拟登录实现之四两拨千斤(基于V8引擎)](http://drops.wooyun.org/tips/13556)

中我们分享了QQ帐号密码登录的流程和基于JS引擎实现的密码加密方式，我们用一种简单实用的方式实现了“能用”。

但是对于一个做安全爱好者，有时候我们需要深入一些，整个加密的流程和算法，我们是不是自己可以实现一套？所以，本文的重点，是对TX密码处理流程的分析。

密码处理流程
------

### 总体说明

了解了登录流程，我们在要分析和实现模拟登录需要考虑一个问题，密码是如何处理的？

要了解密码是如何处理的，我们先要了解以下3种算法：MD5，RSA，TEA。其中MD5是hash算法，比较常用；RSA是一种非对称加密算法，大家也比较了解。这里需要说明一下TEA算法。

TEA算法Tiny Encryption Algorithm，是一种分组加密算法，实现比较简单。TEA算法使用64位的明文分组和128位的密钥，需要进行 64 轮迭代。

不过TX_TEA算法对传统的TEA算法进行了一些修改，具体的原理可以参考登录的JS。这里简单说明下：TX只使用了16轮迭代；TX_TEA加密的是数据流，并且采用的是反馈随机交织填充方式。

### 加密流程

**加密总流程图**

![p1](http://drops.javaweb.org/uploads/images/5b3d2f69d67669204c71e9af8d68aa9e5e3c75c0.jpg)

基本上看懂这个流程图，就明白QQ密码的加密流程了。

浅蓝色的是来源数据，绿色是一些密码的处理方法（加密、HASH、替换）。

来源数据：

```
密码：password
salt：salt，来源于check接口的返回
verifycode: 来源于check接口的返回
rsaKey在js源码里面可以获取

```

数据说明：

*   rsaData: rsa(md5(pwd), rsaKey)
*   hex_verifycode： verifycode 的16进制

最后进行tea算法tea(v, k)

*   v是 （rsaDataLen + rsaData + salt + verifycodeLen + hex_verifycode） 的byte数组
*   k是 md5(md5(pwd) + salt) 的byte数组

结果进行base64编码

Replace是做一个简单的替换，对以下3个字符进行替换

```
/ -> -
+ -> *
= -> _

```

最后得出加密的密码，长度为216的字符串，形式参考如下：

```
37Hro2-AgR4d8ZkU1L-6FqYhTUdhywhLlD2WihfVZGqZmz5R1RlwBsYPNowY0ZHJxcISmwpW0e7ppcoEDTGYyM5*6ZPJNUnZnb4h4Ke*qIBnFlTkiYFUhUwvXgOEvfIDTgCZIWsiFT6EauXujkB2i5yNFobx9aN5vw2xFyE1E2VoF*LV952q0mQO-HiooQZfMocl13kxFgxtVQaSRpm7Rg__

```

参考代码：

```
def tx_pwd_encode(self, pwd, salt, verifycode):
    """
    js:getEncryption(t, e, i, n)
    t=pwd, e=salt 二进制形式, i=verifycode, n:default undefined
    # """
    salt = salt.replace(r'\x', '')
    e = self.fromhex(salt)
    md5_pwd = o = self.tx_md5(pwd)
    r = hashlib.md5(pwd).digest()
    p = self.tx_md5( r + e )
    a = rsa.encrypt(r, self.rsaKey)
    rsaData = a = binascii.b2a_hex(a)

    # rsa length
    s = self.hexToString( len(a)/2 )
    s = s.zfill(4)

    # verifycode先转换为大写，然后转换为bytes
    verifycodeLen = hex(len(verifycode)).replace(r"0x","").zfill(4)
    l = binascii.b2a_hex( verifycode.upper() )

    # verifycode length
    c = self.hexToString( len(l)/2 )
    c = c.zfill(4)

    # TEA: KEY:p, s+a+ TEA.strToBytes(e) + c +l
    new_pwd = s + a + salt + c + l
    saltpwd = base64.b64encode(
            tea.encrypt( self.fromhex(new_pwd), self.fromhex(p) )
    ).decode().replace('/', '-').replace('+', '*').replace("=", "_")

```

代码传送门：  
[https://github.com/LeoHuang2015/qqloginjs/blob/master/autologin_account.py](https://github.com/LeoHuang2015/qqloginjs/blob/master/autologin_account.py)

0x02 QQ模拟登陆实现之草船借箭（客户端快速登录实现）
=============================

* * *

我们在对QQ进行爬取和扫描的时候，很多时候需要考虑到登录的情况，如果使用用户名密码的方式，可能因为一些风控规则，当我们多次登陆时就要求图片验证码，而使用快速登录就能很好的规避这种情况。

### 流程梳理

客户端快速登录方式是用户在PC端已经登录了QQ客户端软件，如果用户再打开Web页面进行登陆，不用再输入用户名和密码，只需要选择已经登录的帐号，点击确认登录即可。

![p2](http://drops.javaweb.org/uploads/images/0450ded0b35b4ec86415700cb2f1c7159a5703dc.jpg)

快速登录的本质上是使用clientkey置换token。

QQ客户端登陆后会生成一个长224的clientkey认证字符串，每次登陆都会变化，参考如下：

```
000156DCEB4E0068663F53B8B402784291BB6E74C482BFB6367FF48FB970443E9B9682359E8F1F92D5A814B097D12D938B96B30742DDE5CDA8E453EB7CD31A5121416637D945615C661285F5306884D959184AB1E4F7CFA83BC9FAF069C1E5878320ECF79EF8751320763492752A1433

```

早期快速登录的实现方式是各个浏览器使用插件，如IE的 ActiveX控件支持的，firefox是插件，通过插件植入clientkey。

后续支持非插件的形式，每次动态的访问QQ客户端绑定的本地server（localhost.ptlogin2.qq.com）获取clientkey，然后再用clientkey去置换token。

### 整体流程

客户端快速登录主要分为两种情况：

一种是插件模式，直接使用clientkey置换token登陆；

另外一种是费插件模式，或者clientkey出现一些异常情况，通过请求server把clientkey设置到cookie，然后再置换token登陆。

![p3](http://drops.javaweb.org/uploads/images/4789d3b342bb25075c14cd661d515d3cd69e77bd.jpg)

### 流程分析

#### clientkey存在且正常/插件模式

**1.组件加载&获取用户头像信息**

同帐号和密码登陆，只是这里获取已经登陆QQ客户端的用户头像和昵称。

获取登陆信息，用户  
[http://ptlogin2.qq.com/getface](http://ptlogin2.qq.com/getface)

返回：帐号、头像地址（有多个客户端登陆的帐号，请求多个）

**2.登陆**

用户点击登陆，实际上是一个clientkey置换token的过程。

请求会带上clientkey进行认证  
[http://ptlogin2.qq.com/jump](http://ptlogin2.qq.com/jump)

如果client不正确，则会登陆失败，后续登陆不会信任原来的clientkey，会走clientkey不存在/异常的流程。

#### clientkey不存或者异常/没有安装插件

**1.组件加载&获取用户信息&获取用户头像信息**

由于clientkey这里会多一步获取用户信息的流程

参考url:

```
http://localhost.ptlogin2.qq.com:4300/pt_get_uins
?callback=ptui_getuins_CB
&r=0.5314265366275367
&pt_local_tk=0.3291951622654449

```

返回，账号信息，客户端类型，昵称等信息

PS：这里如果获取不到会进行重试，一共5次，比如http的端口依次是4300,4302,4304,4306,4308。

然后再获取用户头像信息（同上）。

**2.登陆**

获取clientkey

参考URL：

```
http://localhost.ptlogin2.qq.com:4300/pt_get_st
?clientuin=1802014971
&callback=ptui_getst_CB
&r=0.11057236711379814
&pt_local_tk=0.3291951622654449

```

返回：设置clientkey到cookie，返回回调方法

```
var var_sso_get_st_uin={uin:"1802014971"};ptui_getst_CB(var_sso_get_st_uin);

```

然后进行登陆置换  
[http://ptlogin2.qq.com/jump](http://ptlogin2.qq.com/jump)

返回：设置cookie

```
ptui_qlogin_CB('0', 'http://www.qq.com/qq2012/loginSuccess.htm', '');

```

设置完cookie后，再请求ptlogin2.qq.com域的如下url来完成对ptlogin2.qq.com域和qq.com域的认证cookie的设置，同时删除clientuin和clientkey这两个cookie值。

### 模拟实现

我们需要模拟实现的快速登录，需要走非插件模式的流程，流程本身比较简单，也没有比较复杂的算法，如下：

*   获取签名
*   获取客户端QQ号码
*   用户名和环境检测
*   获取clientkey
*   置换token

![p4](http://drops.javaweb.org/uploads/images/dc342da4e282fd4461e3472389ded5579c5010d8.jpg)

这里有两个安全点需要注意：

1.  Token校验：请求的`pt_local_tk`会和cookie中的`pt_local_tk`校验；
2.  Referrer验证：referer限制了QQ域。

参考代码：

```
def get_client_uins(self):
    '''
    get client unis info
    need: token check & referer check
    '''
    tk =  "%s%s" %(random.random(), random.randint(1000, 10000) )
    self.session.cookies['pt_local_token'] = tk
    self.session.headers.update({'Referer':'http://ui.ptlogin2.qq.com/'})

```

具体实现参考代码：  
[https://github.com/LeoHuang2015/qqloginjs/blob/master/autologin_quick.py](https://github.com/LeoHuang2015/qqloginjs/blob/master/autologin_quick.py)