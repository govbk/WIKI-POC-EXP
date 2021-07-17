# 由参数URL想到的

### 0x00 抛砖引玉

* * *

当你看到一个参数的值是url的时候你会想到什么？

结合wooyun里的案例看，可能产生的危害分为三方面：

```
1、url重定向跳转漏洞
2、底层操作类库支持其他协议导致读取本地或探测网络信息
3、不支持其他协议但是没有设置网络边界

```

### 0x01 详细介绍

* * *

#### URL重定向跳转

url跳转漏洞的科普之前已经发过[http://drops.wooyun.org/papers/58](http://drops.wooyun.org/papers/58)。

url跳转可能集中过滤不严格的情况：

```
一是白名单同域下可能有其他的302跳转漏洞结合绕过。
二是单纯判断字符串中是否包含白名单域名，可用http://www.attack.com/test.com/index.php或http://www.test.com.attack.com/index.php绕过。
三是后端取host的时候跟浏览器识别的差异导致http://www.attack.com\test.com/index.php（测试除了gecko内核，其他浏览器都把attack.com当做host）可绕过。
后端如果仅仅是依靠获取/来结束的话，就会产生差异，包括php中的parse_url函数获取host的结果也是www.attack.com\test.com

```

#### 底层操作类库支持其他协议导致读取本地或探测网络信息

wooyun中案例：

[WooYun: 微博--微收藏多处任意文件读取漏洞](http://www.wooyun.org/bugs/wooyun-2011-03070)

[WooYun: 人人网的分享网页功能存在诸多安全漏洞](http://www.wooyun.org/bugs/wooyun-2010-012)

获取地址的内容输出出来，后端采用curl库，支持其他的协议，如果没有做任何过滤防范措施，可使用file协议时便可读取本地的文件，telnet探测端口信息等。

```
http://share.renren.com/parse_share.do?link=file:///etc/passwd
http://share.renren.com/parse_share.do?link=file:///etc/sysconfig/
http://mark.appsina.com/read.php?sid=2247&type=0&url=telnet://221.179.193.1&pos=1&from=0&gsid=3_5bc7d139d8527229d2df38b6765c6b91b8428eda66bd8c1e61b5df&vt=2

```

#### 不支持其他协议但是没有设置网络边界

wooyun中案例：

[WooYun: 我是如何漫游腾讯内部网络的](http://www.wooyun.org/bugs/wooyun-2013-026212)

[WooYun: 我是如何漫游搜狗和搜狐内部网络的](http://www.wooyun.org/bugs/wooyun-2013-026249)

这两个漏洞已经对核心白帽子公开，并且厂商已经修复，就拿来做例子了。

当已经针对url做了协议控制只允许http访问时还能做什么呢？

尝试下访问内网吧

```
http://wap.sogou.com/tc?url=http%3A%2F%2Fno.sohu.com%2F

```

可以用暴力破解二级域名的工具找内网的域名跑一下试试，然后尝试访问看看是否成功~！

### 0x02 修复方案

* * *

#### 加入有效性验证Token

我们保证所有生成的链接都是来自于我们可信域的，通过在生成的链接里加入用户不可控的Token对生成的链接进行校验，可以避免用户生成自己的恶意链接从而被利用，但是如果功能本身要求比较开放，可能导致有一定的限制。

#### 设置严格白名单及网络边界

功能要求比较开放的情况下，需要严格限定协议以及可访问的网络。