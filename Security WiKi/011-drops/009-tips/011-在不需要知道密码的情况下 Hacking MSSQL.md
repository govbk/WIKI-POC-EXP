# 在不需要知道密码的情况下 Hacking MSSQL

本文翻译自：[https://blog.anitian.com/hacking-microsoft-sql-server-without-a-password/](https://blog.anitian.com/hacking-microsoft-sql-server-without-a-password/)  
原作者：Rick Osgood  
版权归原作者所有

0x01 前言
=======

* * *

在最近的一次渗透测试中，我抓包的时候无意中注意到一些没被加密的 MSSQL 流量。因为语法摆在那里，不会弄错。最开始我以为这是一个可以抓到认证凭证的方法，然而，MSSQL 加密了登录流量，这意味着我不得不去破解它的加密算法来获得凭证。如果安装 MSSQL 的时候用了一个自签发证书，那么很简单的就可以破解了。

不过不幸的事，破解 MSSQL 加密并不在和这个客户签订的协议的范围中。所以我只能把我的好奇心放在一边，然后继续完成这次渗透测试。然而我却情不自禁的去想这件事应该有猫腻。是不是这是一种不用任何凭据去攻击 MSSQL 的方法呢？我决定去实验室验证我的假说。

最终我仅通过很少的一部分数据包 hacking，我就可以控制 MSSQL，不用去偷取任何的凭据，仅仅通过中间人攻击就可以做到。

0x02 中间人
========

* * *

回到实验室后，我开始研究。为了我的进一步研究，我在 Windows Server 2012 R2 上运行了 MSSQL Server 2014 Express。客户机是一台 Windows 10 系统，上面跑了 MSSQL Management Studio 2014。我的攻击机是一台新安装的 Kali 2.0。所有的机器在同一个子网里，以模拟在内网的攻击。这个环境和我在客户那边的环境几乎一模一样。

这类攻击是 MITM，Anitian 做过很多这类攻击，正如我们在 hacking 基础设施设备上有很多专长。MITM 典型的方式是执行某种重定向，像 ARP 缓存投毒（在某些环境下仍然可以用）一样，强行让在两个系统之间的流量重定向到攻击者的计算机上。这可以让攻击者不仅可以看见所有受害者的数据，而且可以控制这些流量。

这就是我想要做的。

0x03 理解数据
=========

* * *

我需要了解的第一件事就是 MSSQL query 流量。为了让这次测试更有意思一点，我用 sa 账户登录 MSSQL。sa 是 MSSQL 的 system admin 账户，可以做任何你想要做的奇奇怪怪的事情。如果我的实验成功了，那么我可以利用 sa 的权限做一些有趣的事情。

![p1](http://drops.javaweb.org/uploads/images/5c573dafbbdf0033c496df6feab5f855369345c6.jpg)

登陆后，我在 MSSQL 服务器上打开 Wireshark 2.0，开始抓包。我用 “tds.query” 的 filter 在 Wireshark 上过滤，这样就可以隐藏其他乱七八糟的流量，仅现实 TDS 查询包了。（顺便一提啊，我发现“tds.query” filter 在老版本的 Wireshark 上不受支持）

抓流量的同时，接着我切回到工作站然后在我建立的测试数据库上执行了一条 MSSQL 查询语句。这个数据库叫做 testdb，只有一个叫做 Products 的表。Products 表有两个字段：ProductID 和 ProductName。虽然里面没有任何数据，但是这次测试并不需要数据。这条查询语句的意思是从指定的数据库的表里获取所有的数据。

![p2](http://drops.javaweb.org/uploads/images/d0bac29af8aaa3ae083f2e10eb6467f4f47e1e51.jpg)

查询成功执行了，然后返回了空的表。你可以看见字段在截图的右下方列出来了。切回到 Wireshark，我停止抓包然后看了下抓到的数据。我注意到一个 TDS 查询包，然后点击这个数据包，让它里面所有的数据在我面前显示出来。MSSQL Server 2014 Express 默认没有任何加密，所我我可以分分钟看到它的数据。

![p3](http://drops.javaweb.org/uploads/images/92ac19fd39d248f1980fa561d69b915871f539bb.jpg)

看在中心窗格底下被解码的数据，很容易的辨识出这个查询。它甚至包含回车和换行符。注意到的比较有意思的是，在两个字节之间会有一个空字节（0x00）。这在下面窗格的 raw data 种是很明显的。Wireshark 显示了这些字节的周期特征，但是真的，这都是空字节。这意味着我并不能直接寻找 “select”，我不得不在稍后的搜索中考虑这些空字节，而且在最终我要替换的数据中也要插入这些空字节。

0x04 和 Ettercap Filters 的愉♂快的事情
===============================

* * *

现在我知道了数据的样子，我试图找一种方式去操控这些数据。我决定用 Ettercap。Ettercap 是一个专门为 MITM 攻击设计的工具，同时它也有一个内置的功能，叫做 Ettercap filters。一个 filter 可以让我搜索数据包的数据，接着操控这些数据。你可以自己写一个 filter，然后把它加载到 Ettercap 里面。Ettercap 会在每次找到匹配的数据的时候自动替换这些数据。虽然这个功能有点限制性，但是对于 PoC 来说足够了。

filters 使用一个简单的脚本语言写的，我想要用的函数就是 search 和 replace 了。search 函数可以在数据包里搜索指定的数据，replace 会替换我们想替换的数据。这是这次项目的关键。

因为 TDS 查询数据中有空字节，所以一些字符是不可打印的（non-printable）。这意味着我不能简单的去搜索/替换掉一个字符串。我需要一种方法来搜索不可打印的字符，而且我并不能在键盘上输入空字节。幸运的事，Ettercap filters 支持 16 进制。比如，搜索“s”的时候，我可以通过“`\x73`”来搜索，所以空字节也可以简单的用“`\x00`”来表示了。Kali 有一个程序叫做 hexdump，可以将字符串转化为 16 进制，我用它转变了“select”到 16 进制。

**译者注：真特喵的啰嗦..**

![p4](http://drops.javaweb.org/uploads/images/dd5f9dc68987fe0ae3a403d3e5d5899cdda8b169.jpg)

我写了一个 filter，用来测试我们想要的数据。

![p5](http://drops.javaweb.org/uploads/images/20159851b999200416aebdd8427985ab0af9dbd6.jpg)

第一行确保 filter 只会在 1433 端口的 TCP 流量上工作，如果条件满足了，filter 会输出 debug 信息，这样我们就知道它找到了 MSSQL 流量。这仅仅是为了让我内心平静，因为我知道这个 filter 部分的可用了。嘛，下一个 if 语句搜索 hex 数据，这些数据翻译过来就是带有空字节的“select”。如果 filter 定位到了这个字符串，也会输出 debug 信息。

最后，见证奇迹的时刻。replace 命令将我们指定的字符串准确的替换成了包含空字节的“ssssss”。这只是为了测试这个脚本是不是正确的运行了。比较重要的一点需要注意的是，我们替换的数据长度要和被替换的数据长度相等，这样 TCP 连接就不会断掉了。

写完 filter 之后，需要编译。这也很简单的通过 etterfilter 命令完成。

![p6](http://drops.javaweb.org/uploads/images/fe39b0a652576089fc24de2c713ba33d65d71744.jpg)

没有报错，filter 可以进行测试了。我启动了 Ettercap 图形界面，启动 ARP 欺骗，去攻击 MSSQL 服务器和客户端工作站。我运行 Wireshark 验证了两个被攻击者之间的流量。接着在 Ettercap 中，我点击“Filters -> Load a filter”，选择了我的 filter。Ettercap console 里面显示了“Content filters loaded”的信息。几乎同时我看到了“SQL Traffic Discovered”。一切都在计划之中。

下一步就是返回到工作站，然后尝试运行查询语句。根据计划，“select”会被替换成“ssssss”，打乱了这个查询。我运行了这个查询，但这一次我并没有看到像之前一样的一个空表，而是一段报错。

“Incorrect syntax near ‘ssssss’.”。太完美了，filter 完全按照预期工作了。它把“select”替换成了“ssssss”。MSSQL 不能够理解，所以返回报错。这是在正确道路上的第一步，下一步就是把所有的语句替换成我们攻击的查询语句了。

0x05 创建账户
=========

* * *

我决定在服务器上增加一个账户，这是我作为攻击者来说最好的一个剧本了，特别是当工作站的被害者使用 sa 账户登录的时候。为了添加账户，我需要在 MSSQL 上提交如下查询：

```
CREATE LOGIN anitian WITH PASSWORD=’YouGotHacked1#’;

```

这样会在 MSSQL 上添加一个用户名为“anitian”，密码为“YouGotHacked1#”的账户。将它转化为 hex 之后，我修改了 mssql.filter 文件。

![p7](http://drops.javaweb.org/uploads/images/230a18ba1e279f732b835e0b02ec8832c72b4dba.jpg)

这个 filter 会搜索 “`select ProductID, ProductName from Products where ProductID=1;`” 并把它替换为 “`CREATE LOGIN anitian with PASSWORD=’YouGotHacked1#’`”。我之前说过两个字符串的长度要一样长，所以我怎么去控制我的语句呢？因为我的语句比原语句短，所以我仅仅在语句后添加了几个空格，空格并不会影响语句执行结果的。我编译好这个 filter，然后用之前的方法加载进 Ettercap。接着我在工作站提交查询。

![p8](http://drops.javaweb.org/uploads/images/b9b411979a9ae386542ff59cc7b252093bfeac60.jpg)

注意到这此返回的内容和我用 Ettercap 之前返回的内容的不同了吗？原来是返回了一个空表，但这一次，没有返回表，而是返回了“Command(s) completed successfully.”。如果 DBA 看到了这个，他们会把这个当做奇怪的错误而忽视。不幸的是，太晚了。我已经在数据库上添加了自己的用户，现在，真正的 hack 才刚刚开始。

我从之前用 sa 账户登录的 Windows 10 工作站上用我刚创建的新用户“anitian”登陆。

![p9](http://drops.javaweb.org/uploads/images/e5e19e179706921dd130d53ac1b4bea10758dd95.jpg)

![p10](http://drops.javaweb.org/uploads/images/1a1d04804ef10de04f3967d9935f2d94988aa21e.jpg)

成功啦！我成功登陆了自己的账户。不过不幸的是这个账户权限比较低，所以我不能干太多的事。然而，这个很好解决。下一步就是利用 Ettercap filter 修改我的权限。

在这一点上，我可以很容易地完成这件事。但是手动来转换 hex 很乏味，而且还要插入空细节。谁愿意在这上面花费心思？这是一个足够好的 PoC 么？

没门！我不想轻易放弃。而且，为什么要做这些无聊的工作，我可以用一个脚本完成全部这些工作！

0x06 自动化攻击
==========

SQLinject.sh shell 脚本可以在这里下载。

[http://pastebin.com/Nge9rx7g](http://pastebin.com/Nge9rx7g)

这个脚本自动的完成全部的过程，从把 SQL 语句转化为 hex 开始，到 ARP 攻击、加载 Ettercap filter。它使得整个过程变得十分简单。

这个脚本需要以下信息：

*   MSSQL server 的 IP 地址
*   MSSQL client 的 IP 地址
*   想替换的原 SQL 语句
*   替换成的新 SQL 语句

通常情况下，除了我想注入的 SQL 语句以外，其他的所有的信息我都知道。我知道我想给 anitian 用户 sysadmin 权限，快速地学习了一下 MSSQL 命令后，我写了如下语句：

```
ALTER SERVER ROLE sysadmin ADD MEMBER anitian;

```

这条语句将会让我新添加的 anitian 用户拥有 sysadmin 权限，让我可以干更多的事情。现在我知道了所有的四个信息了，那么我运行这个脚本：

```
./SQLInject.sh –o “select ProductID, ProductName from Products where ProductID=1;” –i “ALTER SERVER ROLE sysadmin ADD MEMBER anitian;” –s 192.168.1.114 –c 192.168.1.100 –f mssql.filter

```

用这个脚本，我不用担心这些讨厌的 hex 格式和空字符，这个脚本做了所有的事情。它会将字符串转化为 hex 格式，然后输出一个 Ettercap filter 到 mssql.filter 中（文件名基于`-f`参数）。接着，脚本运行 etterfilter 然后编译 filter。最后，这个脚本甚至运行了命令行界面的 Ettercap、加载 filter，进行 ARP 欺骗攻击 MSSQL 服务器和客户端工作站。它甚至也比较了两个字符串的长度来进行自动补充空格使得两个字符串长度相等。只需要一个命令就能完成所有的事情。

我运行了这个脚本，然后切换到工作站。当我运行相同的 select 查询的时候，我注意到我再次得到了“Command(s) completed successfully”的信息。这是一个好象征。我注销 sa 账户然后通过 anitian 登陆。

![p11](http://drops.javaweb.org/uploads/images/3cf8183eeb77a28ab5bef2a3518d48d967a4b3e5.jpg)

233333333！你看截图，anitian 已经是 sysadmin 权限了。我可以通过这个权限访问整个系统。它给了我一饿过很好的中枢点来攻击网络上的其他的系统。当然，假定这个数据库不包含我想要的付款卡号或者个人身份信息。

不过这个脚本最大的败笔就是你需要知道要被替换的原语句。幸运的是，MSSQL 经常有定时运行的批处理工作或者查询在指定的时刻。盯着 Wireshark 一段时间，将会抓到至少一条查询的吧。当然我也可以让它变成一个更成熟的方案：进行 MITM 攻击使得我代理所有的流量，然后在其中搜寻 TDS 查询数据包，接着自动替换数据，不需要知道任何原语句...到那时这个项目还是日后再说吧...

0x07 防御 SQL MITM 攻击
===================

我才不想翻译了呢，大家可以看原文 :D