# 被忽视的大型互联网企业安全隐患：第三方开源WiKi程序

0x00 前言
=======

* * *

Wiki一词来源于夏威夷语的“wee kee wee kee”, 是一种多人协作的写作工具。在大型互联网企业（如腾讯、360、小米）的业务线中笔者都有遇见过他们的身影，而其常被用作介绍业务功能的说明书以及内部项目工作协同平台。目前常见且使用率较高的WiKi程序有Miediawiki、DoKuWiKi、HDWiki等，但由于这些程序平时受到关注度不足，程序存在很多设计上面的缺陷并没有被公开和修复，很多甚至足以可以导致服务器被轻松getshell，使其成为互联网企业信息安全的一颗“隐形炸弹”。本文将着重介绍渗透第三方Wiki程序常用的思路，然后附上攻击两个被广泛使用WiKi系统的Expolit和实例危害证明，最后给出解决方案。

0x01 常用思路
=========

* * *

### 一、前期准备：批量收集大型企业渗透目标

1)使用百度或者是谷歌等搜索引擎，关键词”`site:XXXX.com inurl:wiki`”，可以轻松获取很多目标，

![enter image description here](http://drops.javaweb.org/uploads/images/881b56456e0184bcc43e858d91ca16a7bf494dd6.jpg)

2）使用子域名爆破工具，批量收集企业子域名，然后分离出wiki站点

### 二、着手攻击：分析Wiki品牌，收集管理员列表，爆破进入后台

不同品牌的Wiki程序的渗透方式略为不同，大型互联网企业常用的Wiki程序有两个：Mediawiki和Dokuwiki，这两个程序都可以通过技巧快速搜集到管理员的用户名，然后通过没有限制登录次数以及验证码的登录页面爆破弱口令进入系统，下面分别做介绍：

**渗透Mediawiki系统思路：**如果你看到地址栏中有如下结构的wiki程序，那一定就是Meidawiki没错了，接下来您只需要三步就能渗透进入目标了：

![enter image description here](http://drops.javaweb.org/uploads/images/cfdde1b37c61b1b60e4143fd8a4b216cf4cc07d4.jpg)

Step1: 通过MediaWiki默认携带的搜索功能查找，搜索“用户创建日志”，MediaWiki系统中的用户列表： Expolit:`http://www.xxx.com/index.php?title=%E7%89%B9%E6%AE%8A%3A%E6%97%A5%E5%BF%97&type=newusers&user=&page=&year=&month=-1`

![enter image description here](http://drops.javaweb.org/uploads/images/f88ee26331bbf3eccf72eceb9c015d6aff4ca3bc.jpg)

Step2: 通过MediaWiki默认携带的搜索功能，搜索“权限变更日志”，帮助我们快速分离出系统中的管理员进一步获得用户名： Expolit:`http://www.xxx.com/index.php?title=%E7%89%B9%E6%AE%8A%3A%E6%97%A5%E5%BF%97&type=rights&user=&page=&year=&month=-1`

![enter image description here](http://drops.javaweb.org/uploads/images/274a62b4ae64188389fd2b8e01e6e7126e5f3476.jpg)

Step3: MediaWiki系统默认登录入口，没有任何次数验证和验证码，所以最后一步就是直接载入之前用户名和字典进行弱口令爆破： Expolit:`http://www.xx.com/index.php?title=Special:UserLogin`

![enter image description here](http://drops.javaweb.org/uploads/images/13681eb669fc1eb14ed7ae0c90459c4c5e51764b.jpg)

如果运气好的话管理员存在常见弱口令就可以登录后台，修改WiKi的内容，由于MediaWiki管理员后台上传权限并不高，并不能上传php文件，getshell可能有些困难，不过现在您已经足以可以修改整个企业业务介绍网站的内容了，这些业务以企业重点开放平台居多，影响已经足够大了。

**渗透DokuWiki系统思路**

如果您看到下面UI风格的WIKI程序，那它就是Dokuwiki没错了，接下来只需要三步就能渗透进入目标了。值得注意的是，因为Dokuwiki后台的设计缺陷，只要能够登录管理员账户就意味着可以getshell接着渗透内网：

![enter image description here](http://drops.javaweb.org/uploads/images/b4ac8c0aab23b3a1b6cc654a865eb1359186c789.jpg)

Step1: 查找DoKuWiki系统中用户列表：

在Dokuwiki的媒体管理器中，每一个文件修订历史中明确罗列了系统中存在的用户和用户名

Expolit:`http://www.xxx.com/doku.php?id=start&do=media&ns=`

在Dokuwiki的Wiki修订历史中，也可以轻松收集到系统中用户的蛛丝马迹

Expolit:`http://www.xxx.com/doku.php?id=start&do=revisions`

有些WIKI系统甚至直接开放了注册的权限，你甚至可以尝试通过下面的Expolit链接注册一个用户，试着进入企业WIKI系统内部

Expolit:`http://www.xxx.com/doku.php?id=start&do=register`

Step2: 查找DoKuWiki系统默认登录入口，同样没有任何次数验证和验证码，所以直接载入之前用户名和字典进行弱口令爆破，Doku的默认登录入口

```
http://www.xxx.com/doku.php?id=start&do=login

```

![enter image description here](http://drops.javaweb.org/uploads/images/64701412ed85485ff80bc2e92169aefcdb6973c1.jpg)

Step3：登录管理后台，利用Dokuwiki的插件管理功能Getshell`http://www.xxx.com/doku.php?id=start&do=admin&page=extension`

![enter image description here](http://drops.javaweb.org/uploads/images/102603e328d7d0a00e038392906ecb44ae9f62e5.jpg)

0x02 真实案例
=========

* * *

**[例一] 某Dokuwiki系统管理员弱口令，直入后台getshell**白帽子发现某DokuWiki系统的管理员存在弱口令，登录以后，直接通过上文渗透Dokuwiki思路中提到的进入插件管理界面成功getshell到了服务器的权限。

**[例二] 网易某内部门户WIKI未设置注册权限验证，直接注册用户窃取内部信息**笔者曾通过百度搜索引擎发现网易内部WIKI系统对外，并且开放了注册功能，只要通过自己的邮箱注册就可以成功获取账号登录进入该系统，获得了少量的内部信息，因为做了一定的防护，对用户组权限进行了隔离，所以笔者并没有获得更高级别的权限。

0x03 解决方案
=========

* * *

1.  其实第三方开源Wiki的漏洞有点类似于之前很火的Wordpress和Discuz后台弱口令漏洞，很显然，目前前面提到的两个类型的第三方建站系统已经被给与了足够的重视，而目前Wiki系统却并没有。只要在开发完成以后对对默认的登录和注册页面进行删除或者修改名称，企业后端WAF进行访问限制配置，同时强化员工安全意识，杜绝弱口令，就能有效防止企业Wiki系统被攻击者渗透，从而丧失服务器的最高权限。
    
2.  使用第三方开源WIKI作为内部协同平台时应特别注意对每个页面设置权限以及严格限制外部用户注册系统的用户。
    

3.GitBook 是一个基于 Node.js 的命令行工具，可使用 Github/Git 和 Markdown 来制作精美的电子书，如果产品需要做说明介绍的话，完全可以用Gitbook替代这些第三方Wiki，不失Wiki的美观和简洁方便。

![enter image description here](http://drops.javaweb.org/uploads/images/e322362e5a46d31b3975ac21038e0b60b765eddc.jpg)

官网：[https://www.gitbook.com/](https://www.gitbook.com/)