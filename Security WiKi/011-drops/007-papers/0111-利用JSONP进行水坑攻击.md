# 利用JSONP进行水坑攻击

0x00 简介
=======

* * *

前几天安全研究者Jaime Blasco发现了在中国某些特定主题的网站被进行了[水坑攻击](https://www.alienvault.com/open-threat-exchange/blog/watering-holes-exploiting-jsonp-hijacking-to-track-users-in-china)，攻击方法有一定多样性，其中存在一些比较少见于此类型攻击中的技术，不过其实是比较早的技术了，国内猥琐流已经玩了很久的玩意。攻击类型的多样性在于，该安全公司并非追踪到了某个攻击组织的多次活动，而是某个特定主题网站的多次攻击。

比如参考[1](https://www.alienvault.com/open-threat-exchange/blog/cyber-espionage-campaign-against-the-uyghur-community-targeting-macosx-syst#sthash.fHOjOceQ.dpuf)，发送Microsoft Office .doc利用MS09-027来打苹果电脑，虽然我认为他们可能没打到啥东西。除此之外的攻击事件还可以参考[2](https://www.alienvault.com/open-threat-exchange/blog/new-macontrol-variant-targeting-uyghur-users-the-windows-version-using-gh0s),[3](https://www.alienvault.com/open-threat-exchange/blog/latest-adobe-pdf-exploit-used-to-target-uyghur-and-tibetan-activists)。

这次的攻击方式总结起来就是 当受害者访问网站a时会处罚恶意代码，之后恶意代码会去访问某些存在可获取私人信息接口的网站，获取信息后再上传至c2。下面是该安全公司统计的恶意代码获取信息的网站，总的来说应该是以中国地区的用户为目标的一次行动，这年头会上这些网站的老外不多了。

![enter image description here](http://drops.javaweb.org/uploads/images/c673a5d4578c2a653d2c0a29a108e829f3622da9.jpg)

至于提到的玩烂了，乌云上有记录的分析最早是剑心boss 2012年发布的 《Json hijacking/Json劫持漏洞》参考文献[4](http://drops.wooyun.org/papers/42)以及2014 年zone社区的两篇相关文章以及利用文章。可看参考[5](http://zone.wooyun.org/content/16309)，[6](http://zone.wooyun.org/content/16828)。

0x01 原理 & 攻击分析
==============

* * *

总结来说js会通过某种方式获取数据来方便用户的交互，这种获取数据的方式有一些通用的格式，这里就是json or jsonp。一般js会通过两种方式获取数据。一种是xmlhttp还有一种是script的形式。

xmlhttp的数据获取方式只有在同一个域的情况下才可以获取，不然会遭受同源策略的限制，但是如果数据位于两个不同的域名，那么只有通过script的方式进行获取，通过script的方式先传入一个callback，那么数据就会被传入的函数执行。这样就不会遭到同源策略的限制。

```
<script>  
function wooyun_callback(a){  
alert(a);  
}  
</script>  
<script src="http://www.wooyun.org/userdata.php?callback=wooyun_callback"></script>  

```

这次其实就是在目标网站群上插入通过此类型的接口获取信息的代码，再获取目标的私人信息。老外给了几张恶意代码的截图。

1 利用代码，通过某种方式在受害者访问的网站嵌入

![enter image description here](http://drops.javaweb.org/uploads/images/3b268263c3afbb52fe1bbf87ddbd30e62a9449c2.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/060dec4b3f4b9c92d2a37af7ed9de6fa8cd8e022.jpg)

2 通过callback获取响应数据

![enter image description here](http://drops.javaweb.org/uploads/images/50c119d14f3b33853e46ecd291d9be8919583b74.jpg)

3 解析响应数据

![enter image description here](http://drops.javaweb.org/uploads/images/d8e80b3065cf1562d6a56cdc6eddabe3897d5c08.jpg)

老外提到了一个[中国安全博客](http://jzking121.blog.51cto.com/5436671/1306505)代码风格有点像。这里大概原理已经解释的差不多了。

0x02 利用代码 & 案例
==============

* * *

关于这方面就是jacks写的《[JSON探针—定位目标网络虚拟信息身份](http://zone.wooyun.org/content/16309)》参考5 和 xiaoxin在此之上扩展的 《[jsonp探针callback地址收集帖](http://zone.wooyun.org/content/16828)》参考6。

案例方面 可以在乌云主站搜索到需要的案例 wooyun.org

比如 http://wooyun.org/bugs/wooyun-2010-0118732 可以获取用户的购买记录等大量的隐私信息。比较有代表性的还有剑心发布的[WooYun: QQMail邮件泄露漏洞](http://www.wooyun.org/bugs/wooyun-2010-046)通过qqmail的特殊接口获取邮箱内容。

```
<script>  
var Qmail={};  
</script>  
<script src="http://mail.qq.com/cgi-bin/login?fun=passport&target=MLIST&t=login.js&pagesize=10&resp_charset=gb2312&1=3"></script>  
<script>  
alert(Qmail.newMailsList.nextUrl);  
alert(document.scripts[1].src=Qmail.newMailsList.nextUrl);  
alert(Qmail.newMailsList.summary);  
</script>  

```

0x03 攻击原因分析
===========

* * *

Jaime Blasco提到攻击原因的方面，攻击出现某些特定的主题的网站，以某些少数民族以及支持自由言论的非政府组织。攻击目标以小部分群体为主，攻击的目的应该在于收集其个人的资料，其中一个原因可能在于在中国一部分网站受到gfw的拦截，但是只要使用vpn以及tor就可以正常访问，在使用某种代理的前提下收集这一部分群体的信息存在难度，那么就可以通过水坑的方式，跨域收集个人信息。

0x04 修复 & 防御 方案
===============

* * *

1.  尽量避免跨域的数据传输，对于同域的数据传输使用xmlhttp的方式作为数据获取的方式，依赖于javascript在浏览器域里的安全性保护数据。
2.  referer的来源限制，利用前端referer的不可伪造性来保障请求数据的应用来源于可信的地方，此种方式力度较稀，完全依赖于referer，某些情况下（如存在xss）可能导致被绕过。
3.  token的加入，严格来说，这种利用javascript hijacking的方式获取数据是CSRF的一种，不过较之传统的CSRF不能获取数据只能提交而言，这种方式利用javascript可以获取一些敏感信息而已。如果我们能让攻击者对接口未知，就可以实现json hijacking的防御了。利用token对调用者的身份进行认证，这种方式对于调用者的身份会要求力度较细，但是一旦出现xss也可能导致前端Token的泄露，从而导致保护失效。
4.  对于同域的json使用情况下，可以在数据的输出头部加入while(1);的方式避免数据被script标签的方式引用，这可以防止一些比较有特性的浏览器里导致的数据泄漏。

此外老外还提到了

1.  使用CORS代替jsonp
2.  不要在使用cookie的情况下使用jsonp交换数据

大概就这样，其中提到了独裁之类的玩意我就不说了。

参考文献
====

* * *

(1] https://www.alienvault.com/open-threat-exchange/blog/cyber-espionage-campaign-against-the-uyghur-community-targeting-macosx-syst#sthash.fHOjOceQ.dpuf

(2] https://www.alienvault.com/open-threat-exchange/blog/new-macontrol-variant-targeting-uyghur-users-the-windows-version-using-gh0s

(3] https://www.alienvault.com/open-threat-exchange/blog/latest-adobe-pdf-exploit-used-to-target-uyghur-and-tibetan-activists

(4] http://drops.wooyun.org/papers/42

(5] http://zone.wooyun.org/content/16828

(6] http://zone.wooyun.org/content/16309

(7] https://www.alienvault.com/open-threat-exchange/blog/watering-holes-exploiting-jsonp-hijacking-to-track-users-in-china
