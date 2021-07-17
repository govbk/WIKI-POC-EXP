# 利用基于 NTP 的 TOTP 算法缺陷绕过 WordPress 登陆验证

近日，国外安全研究人员 Gabor 发表了两篇关于如何利用基于 NTP （Network Time Protocol）的验证算法缺陷绕过 WordPress 登陆验证的文章，这两篇文章分别介绍了[基于 NTP 的验证算法缺陷](https://blog.gaborszathmari.me/2015/11/11/tricking-google-authenticator-totp-with-ntp/)以及[如何利用该缺陷绕过 WordPress 登陆验证](https://blog.gaborszathmari.me/2015/11/11/bypassing-wordpress-login-pages-with-wpbiff/)并给出了 POC 和相关工具。以下内容是对这两篇文章的汇总介绍。 ；）

0x00 WordPress 插件 Google Authenticator 验证算法介绍
=============================================

* * *

关于 NTP 相关的知识，可以在[这里](http://baike.baidu.com/link?url=aDjxXw3OivotsPntFuppRDAiJsN_rgrUP3NEHdqZXrvXbzwo7ed4PNmgtZxuAV0ojPyHHco4KYNZfpJjbBnvGK)进行了解。

基于 NTP 的 TOTP 算法
----------------

现在以 WordPress 的一款插件 Google Authenticator 为例来说明一般的 token 生成程序生成一次性密码（TOTP）的实现细节。

如下图所示，程序会使用一个密钥种子与当前服务器的时间戳进行 TOTP 算法后得出一个 6 位纯数字的 Token，该 Token 每 30 秒更换一次，其实这就是我们常见的 “动态口令”。

在这个动态口令生成过程中所存在的问题就在于每次使用相同的密钥种子和时间戳的组合总会生成一个相同的动态口令。而密钥种子是个不变量同时在攻击中不可控，因此只要控制了时间戳那么即可生成任意时间戳所对应的动态口令。

![](http://drops.javaweb.org/uploads/images/199a223394c20ea749240646e4de0787d4237d5b.jpg)

图 1 ：基于 NTP 的 TOTP 算法

修改服务器时钟进行攻击
-----------

从目前来看有很多使用 NTP 的网络都没有对 NTP 传输过程进行加密验证。因此，攻击者就可以修改 NTP 传输的数据进行中间人攻击，给 NTP 客户端提供一个伪造的时间戳。 Gabor 在文章中提到了几个早先对 NTP 进行安全研究的文章资料和工具。

*   [Delorean](https://github.com/PentesterES/Delorean)是一个可以对 NTP 客户端发送伪造的时间戳的工具。
*   [Attacking the Network Time Protocol](http://www.cs.bu.edu/~goldbe/papers/NTPattack.pdf)这篇文章提供了其他几种针对 NTP 的攻击向量。
*   [Jose Selvi’s presentation at DEF CON 23](https://www.youtube.com/watch?v=hkw9tFnJk8k)是一个在 DEF CON 23 中对 NTP 研究的议题视频（需翻墙）。

结合以上工具以及多种中间人攻击技术就可以通过 NTP 控制远程服务器的时钟。

在 Unix 中设置时间的 ntpd 服务不会接受一个伪造的虚假时间戳，所以无法进行时间戳的伪造攻击。不过，可以结合[CVE-2015-5300](https://bugzilla.redhat.com/show_bug.cgi?id=1271076)漏洞进行攻击。

另外一种设置时间的方法是[ntpdate](https://en.wikipedia.org/wiki/Ntpdate)。这种设置方式非常简单，也是[Ubuntu Wiki](https://help.ubuntu.com/community/UbuntuTime)中推荐的方式。因此，在很多地方都使用了这种方式进行时间设置。你可以参考[官方手册](https://supermarket.chef.io/cookbooks/ntpdate)和[这篇博文](http://www.psce.com/blog/kb/how-to-periodically-synchronize-time-in-linux/)进行设置。

设置的方式极其简单，在 corntab 中运行`ntpdate <hostname>`即可。但是值得注意的是**ntpdate 会接受任何来自于 NTP 服务的数据流！**。

几个有名的开源项目，如[Yocto Project](https://bugzilla.yoctoproject.org/show_bug.cgi?id=6433)，[OpenWRT](http://wiki.openwrt.org/doc/howto/ntp.client)，[Startups](https://github.com/doejo/wordpress-cookbooks/blob/master/packages/ntpdate.rb)，还有[托管在 GitHub](https://github.com/search?q=ntpdate+cron&type=Code&utf8=%E2%9C%93)上的无数配置脚本，以及[5 万多 Docker 用户](https://hub.docker.com/r/tutum/ntpd/~/dockerfile/)，甚至包括[VPS 提供商](http://wiki.vps.net/vps-net-features/cloud-servers/getting-started/getting-started-with-linux-keeping-your-server-on-time-with-ntp/)都使用了**ntpdate**进行时间同步设置。

[早在 2002年](https://lists.debian.org/debian-user/2002/12/msg04091.html)就有人提出使用 corntab 运行 ntpdate 不是一个好主意。

0x01 绕过 WordPress 登陆验证
======================

* * *

通过上述描述，让我们来总结一下攻击 NTP 的现有条件：

*   ntpd 和 ntpdate 都容易遭到 MITM 攻击
*   已经有现成的工具可以对 NTP 进行攻击
*   可以控制并修改 TOTP 算法的时间戳

WordPress 中的插件[Google Authenticator](https://wordpress.org/plugins/google-authenticator/)可以对 WordPress 后台登录开启双重验证。如下图所示：

![](http://drops.javaweb.org/uploads/images/44e5577c08a9d139b367ca89ccede14fbe893583.jpg)

图 2 ：Google Authenticator 插件对 WordPress 后台登录开启双重验证

由于可以利用中间人攻击设置服务器的时间一直为指定的时间，因此，可以使用暴力破解的手段对动态口令进行破解。大约最多需要一百万次的破解尝试。

攻击测试
----

搭建如下网络环境：

*   3 台 Ubuntu 虚拟机
*   [Delorean NTP 服务器](https://github.com/PentesterES/Delorean)
*   WordPress v4.3.1 并安装[Google Authenticator 插件 v3.8.11](https://wordpress.org/plugins/google-authenticator/)
*   [双重验证爆破工具 WPBiff](https://github.com/gszathmari/wpbiff)（支持 Google Authenticator 和 WP Google Authenticator 插件）

整个网络非常简单，三台 Ubuntu 虚拟机需要处于同一个子网中。如下图所示：

![](http://drops.javaweb.org/uploads/images/8806b77d9603486cd75f8f9998feb851c2c251ff.jpg)

图 3 ：搭建攻击网络环境

为了模拟中间人攻击以[篡改 NTP 传输数据](http://arstechnica.com/security/2015/10/new-attacks-on-network-time-protocol-can-defeat-https-and-create-chaos/)，我们首先需要修改 WordPress 服务器的`/etc/hosts`文件，如下图所示：

![](http://drops.javaweb.org/uploads/images/523bdc8bc8647b7cf16f4c701328b2caafa18948.jpg)

图 4 ：修改 /etc/hosts 文件

其次，我们假设管理员使用计划任务每隔一分钟同步一次时间（事实上很多人都是这么做的），如下图所示：

![](http://drops.javaweb.org/uploads/images/c7c7a103ba7529161287d9c67ab15a7827a25d3c.jpg)

图 5 ：管理员每隔一分钟同步一次时间

然后，我们使用预先设置的时间作为参数执行 Delorean ，同时 WordPress 服务器依旧会每隔一分钟同步一次时间。

![](http://drops.javaweb.org/uploads/images/50baba4a82d8f7cf076260aa35492a4b022a81ed.jpg)

图 6 ：使用预先设置的时间作为参数执行 Delorean

现在，我们在另外一台虚拟机中，也就是攻击者的机器中运行 WPBiff。设置 WordPress 后台登录用户名和密码，以及与上图相同的时间戳作为运行参数。如下图所示：

![](http://drops.javaweb.org/uploads/images/0f50e71131fa2368c860bb46e803ae313a741bcf.jpg)

图 7 ：运行 WPBiff 开始攻击

在 WPBiff 运行了 39 分钟后，成功的爆破出了 6 位纯数字动态口令，同时 dump 出了有效的登陆 WordPress 后台的 session cookies。如下图所示：

![](http://drops.javaweb.org/uploads/images/8bbdba76c51af6d5a79986baa1334986dbf5c791.jpg)

图 8 ：成功爆破出了动态口令

由于插件不允许动态口令的重用，所以可以使用 dump 出来的 session cookies 直接登录 WordPress 后台。 在额外的三次测试中，又分别花费了 51分钟，57分钟，83分钟 爆破出了动态口令。

![](http://drops.javaweb.org/uploads/images/8a5cd17b3c9fa6899492596a74d3caf43b42f28c.jpg)

图 9 ：成功登陆 WordPress 后台

0x02 参考 & 引用
============

*   [https://blog.gaborszathmari.me/2015/11/11/tricking-google-authenticator-totp-with-ntp/](https://blog.gaborszathmari.me/2015/11/11/tricking-google-authenticator-totp-with-ntp/)
*   [https://blog.gaborszathmari.me/2015/11/11/bypassing-wordpress-login-pages-with-wpbiff/](https://blog.gaborszathmari.me/2015/11/11/bypassing-wordpress-login-pages-with-wpbiff/)