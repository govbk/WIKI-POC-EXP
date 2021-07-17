# 新姿势之Docker Remote API未授权访问漏洞分析和利用

0x00 概述
=======

* * *

最近提交了一些关于 docker remote api 未授权访问导致代码泄露、获取服务器root权限的漏洞，造成的影响都比较严重，比如

[新姿势之获取果壳全站代码和多台机器root权限](http://www.wooyun.org/bugs/wooyun-2016-0209291)

[新姿势之控制蜻蜓fm所有服务器](http://www.wooyun.org/bugs/wooyun-2016-0209305)

[新姿势之获取百度机器root权限](http://www.wooyun.org/bugs/wooyun-2016-0209509)

因为之前关注这一块的人并不多，这个方法可以算是一个“新的姿势”，本文对漏洞产生的原因和利用过程进行简单的分析和说明，但因为时间和精力有限，可能会有错误，欢迎大家指出～

0x01 起因
=======

* * *

先介绍一些东西～

*   docker swarm
    
    [docker swarm](https://docs.docker.com/swarm)是一个将docker集群变成单一虚拟的docker host工具，使用标准的Docker API，能够方便docker集群的管理和扩展，由docker官方提供，具体的大家可以看官网介绍。
    

漏洞发现的起因是，有一位同学在使用docker swarm的时候，发现了管理的docker 节点上会开放一个TCP端口2375，绑定在0.0.0.0上，http访问会返回`404 page not found`，然后他研究了下，发现这是[Docker Remote API](https://docs.docker.com/engine/reference/api/docker_remote_api/)，可以执行docker命令，比如访问`http://host:2375/containers/json`会返回服务器当前运行的 container列表，和在docker CLI上执行`docker ps`的效果一样，其他操作比如创建/删除container，拉取image等操作也都可以通过API调用完成，然后他就开始吐槽了，这尼玛太不安全了。

然后我想了想 swarm是用来管理docker集群的，应该放在内网才对。问了之后发现，他是在公网上的几台机器上安装swarm的，并且2375端口的访问策略是开放的，所以可以直接访问。

尼玛这一想，问题来了：

*   他是按照官方文档弄的，难不成文档里写的有问题？
*   他这么干，会不会有其他人也这么干，然后端口就直接暴露在公网了，那岂不是谁可以随便操作了docker了？

因为这位同学刚好有其他事情要忙，没时间撸，我之前也用过docker，所以我就继续研究了，然后就走上了挖掘新姿势的不归路...

0x02 背锅侠
========

* * *

要查清楚是谁的锅，首先要复现下问题，那么只有一种方法，照的文档装一遍docker swarm。

官网给出创建Docker Swarm集群的方法有：

*   使用docker run 运行 swarm container（官方推荐，文档中都是使用该方法）
*   安装 swarm 二进制文件（executable swarm binary）

这里使用官方推荐方法，系统使用ubuntu14.04，按照[Build a Swarm cluster for production](https://docs.docker.com/swarm/install-manual/)这篇文档装了一遍。

这里简单描述下过程：

*   需要在每台机器上安装docker，并且运行Docker Swarm container
*   需要一个或多个Swarm manager（主从）来管理docker 节点
*   管理的docker节点上需要开放一个TCP端口（2375）来与Swarm manager通信

这里的第三点就是前面提到的暴露的docker端口，我们来看一下文档中docker 节点具体执行的命令

`sudo docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock`

-H参数指定docker daemon绑定在了`tcp://0.0.0.0:2375`上。

docker默认安装的时候只会监听在`unix:///var/run/docker.sock`，因此这里是端口暴露的原因所在。

那么能不能说这个是 docker swarm 的锅呢？

我们来看一下文档中的安装环境

`Prerequisites An Amazon Web Services (AWS) account Familiarity with AWS features and tools, such as: Elastic Cloud (EC2) Dashboard Virtual Private Cloud (VPC) Dashboard VPC Security groups Connecting to an EC2 instance using SSH`

是在AWS VPC上，默认的访问策略是

`AWS uses a “security group” to allow specific types of network traffic on your VPC network. The default security group’s initial set of rules deny all inbound traffic, allow all outbound traffic, and allow all traffic between instances.`

即禁止所有的外网端口访问，文档中之后的部分修改了策略允许22和80端口访问，也就说在文档的环境中，不会存在2375端口暴露的问题，且文档中也提到了不要让docker 的端口暴露在外，虽然没有加字体加粗高亮～

`For a production environment, you would apply more restrictive security measures. Do not leave Docker Engine ports unprotected.`

然而即使高亮了也没有软用，首先是使用者并不一定有类似AWS的VPC环境，再者不是每个使用者都会认真的看文档，所以最终的结论是，这锅docker官方和使用者都得背，谁背的多就不好说了～

0x03 漏洞利用
=========

* * *

说如何利用之前，我们先整理下现在能做的事情

​执行docker命令，比如操作container、image等

那么如果当前运行的container，或者image内有代码或者其他敏感信息，就可以继续深入了，比如果壳和蜻蜓fm的漏洞，就是深入后的结果。

还有的话，可以做内网代理，进一步渗透。

到目前为止，我们能做的事情都是在docker的环境内，无法直接控制宿主机。

那么怎么才能控制宿主机呢？莫慌，分析下

docker是以root权限运行的，但docker执行命令只能在container内部，与宿主机是隔离的，即使是反弹一个shell，控制的也是container，除非有0day，不然是无法逃逸的到宿主机的～

那么只能从docker命令本身下手，脑洞开了下，想到docker 运行 container的时候，可以将本地文件或目录作为volume挂载到container内，并且在container内部，这些文件和目录是可以修改的。

root权限进程，并且能够写文件，是不是似曾相识？

这里的场景和前段时间的 redis + ssh 漏洞很相似，那么这里需要看一下服务器是否有ssh服务，如果有的话，那么直接把/root/.ssh目录挂载到container内，比如/tmp/.ssh，然后修改/tmp/.ssh/authorized_keys 文件，把自己的public key写进去，修改权限为600，然后就可以以root用户登录了。

注：有些服务器会配置不允许root用户直接登录，可以通过挂载 /etc/ssh/sshd_config 查看配置。这个时候，你换一个用户目录写入就行，并且挂载修改 /etc/sudoers 文件，直接配置成免密码，sudo切换root即可。

如果没有运行ssh服务，那么也可以利用挂载写crontab定时任务，比如ubuntu root用户的crontab文件在 /var/spool/cron/crontabs/root，反弹一个shell～

这里利用方式可能还有很多种，大家可以开下脑洞想哈～

0x04 影响
=======

* * *

影响总结：攻击者可以利用该漏洞执行docker命令，获取敏感信息，并获取服务器root权限

目前在公网上暴露的2375端口还有不少，测了一些基本都可以利用。

但docker swarm更多的情况是用在企业内部，虽然在内网，也不意味着绝对安全，当边界被突破，就嘿嘿嘿了～

* * *

0x05 修复方案
=========

**注：因为本小节内容是看了文档后的个人理解，并且部分内容未进行实际验证，可能会错误，仅供参考！**

如果你的2375端口是暴露在公网的，那么最简单的方式就是禁止外网访问或者设置白名单，因为根据官网介绍，swarm本来就不应该在公网中使用。

以上方法仅仅防止了外网访问，但如果本身已经在内网，对于已经撸进内网的攻击者，端口仍然处于可以直接访问的状态，那么有没一些防护方案呢？

为了找到答案，特意看了下docker swarm的文档，[Plan for Swarm in production](https://docs.docker.com/swarm/plan-for-production/#cluster-ownership)这篇文章提到了两种方案

*   第一种方法是使用TLS认证：[Overview Swarm with TLS](https://docs.docker.com/swarm/secure-swarm-tls/)和[Configure Docker Swarm for TLS](https://docs.docker.com/swarm/configure-tls/)这两篇文档，说的是配置好TLS后，Docker CLI 在发送命令到docker daemon之前，会首先发送它的证书，如果证书是由daemon信任的CA所签名的，才可以继续执行，官网图如下：[![](http://static.wooyun.org//drops/20160517/2016051703300142934.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/05/trust-diagram.jpg)

​然而在我对公网中使用TLS的docker remote api（使用2376端口）测试中发现，即使没有证书，Docker CLI仍然可以正常访问，这里我也拿docker python api写了脚本，[设置不验证证书有效性](http://docker-py.readthedocs.io/en/stable/tls/#TLSConfig)，也同样可以访问。

因为这我没有具体配置过TLS，**只能根据以上测试结果推测**，走TLS认证，只能防止MITM 攻击，还是无法解决端口未授权访问的问题。

*   第二种方法是网络访问控制(Network access control)：文档中列出了**Swarm manager**，**Swarm nodes**等用到的端口，告诉你要配置合理的访问规则。文档中还提到了这么一段话

`For added security you can configure the ephemeral port rules to only allow connections from interfaces on known Swarm devices.`

大概意思是只允许信任的swarm devices之间通信。

理想情况就是docker 节点的2375端口只允许swarm manager来访问，但因为swarm manager可能会有多个，就需要配置多条规则，维护起来可能会具有一定复杂度，但只要swarm manager所在机器不被撸，就可以保证docker 节点的2375端口不被未授权访问。当然，这里还需要结合TLS一起使用。

总结来说就是，不要将端口直接暴露在公网，内网中使用需要设置严格的访问规则，并使用TLS。

0x06 瞎扯
=======

* * *

如果你仔细阅读了docker swarm的文档，你就会发现除了2375端口，还有其他一些端口也存在相同的问题，这里就不一一的列出了。

本文主要说的是docker swarm，但是只要是会导致端口暴露的，都会存在问题，也许有一些使用者会因为某些原因，把端口配置成功公网访问，或者有另一个"swarm"呢？

还有想说的是，一个新的东西出来，用户和开发者更多关注的是其功能和便利性，而忽略了存在的安全性问题，之后还会有更多的 “docker remote api” 出现，谁将会是下一个呢？

最后还要感谢一下发现这个问题的同学（转我10wb我就告诉你是谁），没他也不会有这个漏洞～

黑客，绝对是黑客！