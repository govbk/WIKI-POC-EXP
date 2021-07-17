# OS X那些事---恶意软件是如何启动的？

0x00 背景
=======

* * *

前几日，看了一份报告，是美国网络安全公司bit9发布的：[《2015: The Most Prolific Year for OS X Malware》](https://www.bit9.com/resources/research-reports/2015-the-most-prolific-year-for-os-x-malware/)

报告主要的内容就是说说2015年OS X平台恶意软件的情况。bit9的研究团队进行了10周的分析研究，分析了1400个恶意软件样本。给出了下面这张图，可见，2015年恶意软件样本数量是前5年恶意样本数量之和的5倍。这估计要亮瞎苹果公司的眼。Mac越来越火。也越来越不安全了。

![p1](http://drops.javaweb.org/uploads/images/1ca018e89e3b6c8c152bf6611087d4fa6d1aa3bc.jpg)

报告指出的重点有：

1.  现在恶意软件的启动方式（Persistence Mechanisms）使用传统Unix技术的越来越少，基本没有了。大部分恶意软件使用OS X提供的新的启动机制了。
2.  感染持续增长，但是恶意软件的复杂度却不是太高。
3.  主要的启动方式有7种。
4.  由于OS X平台上恶意软件多样性不如windows平台，所有相对的检测方法就简单一些，因为需要需要检查的地方比windows平台的要少。

0x01 启动
=======

* * *

接下来就来谈谈这启动的事，看看是哪7种武器是黑客所喜欢的：

![p2](http://drops.javaweb.org/uploads/images/f0254423f14ba3288995e9729e644e4de7af9e25.jpg)

如上7种武器你知道几种（大神就自动飘过）。

### Launch daemons/agents

其实这两种启动方式可以一起介绍。启动方式基本相同，只是有些区别而已。

这两种方式都是苹果官方提供的标准启动方式。在官方手册里面可以查询到更详细的介绍[[link]](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html#//apple_ref/doc/uid/10000172i-SW7-BCIEDDBJ)。daemons和agents都是由launchd进程负责启动的后台作业。launchd是OS X系统用户态的第一个进程。对应于其他UN*X系统中的init。负责直接或者间接的启动系统中的其他进程。

![p3](http://drops.javaweb.org/uploads/images/f7123ab6fd4ceb7f09a9fd95be0e6fb2791fe4a9.jpg)

从图中可以看到daemons和agents都是由launchd进程启动的。

*   daemons：守护程序，后台服务，通常与用户没有交互。由系统自动启动，不管是否有用户登录系统。
*   agent：代理程序，是一类特殊的守护程序，只有在用户登录的时候才启动。可以和用户有交互，还可以有GUI。

创建一个daemons或agent是非常简单的，就是创建一个普通的二进制可执行文件。然后将自己的属性列表文件（.plist）放置到daemons或agent的配置目录中：

| 目录 | 用途 |
| :-- | :-- |
| /System/Library/LaunchDaemons | 系统本身的守护程序 |
| /Library/LaunchDaemons | 第三方程序的守护程序 |
| /System/Library/LaunchAgents | 系统本身的代理程序 |
| /Library/LaunchAgents | 第三方程序的代理程序，这个目录通常为空 |
| ~/Library/LaunchAgents | 用户自有的launch代理程序，是有对应的用户才会执行 |

plist文件的结构可以查看手册[[link]](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html#//apple_ref/doc/uid/TP40001762-104142),下面给出了一个启动计算器的plist文件。拥有键值为true的RunAtLoad键。

![p4](http://drops.javaweb.org/uploads/images/d976daf7fe8f94cbbd6e1b631f6f288576d5704b.jpg)

将此`.plist`文件拷贝到`/Library/LaunchAgents`目录（拷贝之后的文件拥有者为root），就可以在重启后，自动启动计算器。

可以使用

```
sudo plutil -lint /path/to/com.test.plist

```

来检测plist文件格式是否有问题。

plist中主要的字段和它的含义：

*   Label 用来在launchd中的一个唯一标识，类似于每一个程序都有一个identifies一样。
*   UserName 指定运行启动项的用户，只有当Launchd 作为 root 用户运行时，此项才适用。
*   GroupName 指定运行启动项的组，只有当Launchd 作为 root 用户运行时，此项才适用。
*   KeepAlive 这个key值是用来控制可执行文件是持续运行呢，还是满足具体条件之后再启动。默认值为false，也就是说满足具体条件之后才启动。当设置值为ture时，表明无条件的开启可执行文件，并使之保持在整个系统运行周期内。
*   RunAtLoad 标识launchd在加载完该项服务之后立即启动路径指定的可执行文件。默认值为false。
*   Program 这个值用来指定进程的可执行文件的路径。
*   ProgramArguments 如果未指定Program时就必须指定该项，包括可执行文件文件和运行的参数。

### Cron job

Cron job是一个随Unix而来的启动机制。在OS X中已经不被推荐使用。苹果公司推荐使用launchd命令来完成计划任务。但是OS X仍然支持Cron。那黑客们当然不会嫌弃。

Cron可以用来在设定的时刻执行一个命令或是脚本。如果恶意软件是python编写的，可以直接运行python命令。

Cron服务使用crontab命令来控制。在目录/usr/lib/cron/tabs目录下会有对应的用户名的配置文件。当然可以直接通过命令来进行配置。具体的可以查询手册[[link]](https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man5/crontab.5.html#//apple_ref/doc/man/5/crontab)。

crontab可以直接读取文件作为输入来配置：

![p5](http://drops.javaweb.org/uploads/images/4833b54db2addb5e159326c893950240eb90e606.jpg)如图 用crontab加载文本persist

保存文本内容为：

`*****open /Applications/Calculator.app`

该配置为每分钟执行open命令打开计算器。

![p6](http://drops.javaweb.org/uploads/images/a384b17e855b5330dbd7f8990cecbea23b4139d5.jpg)

上图为文件格式，多个任务可以分多行给出，可以用#进行注释。

[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)在OS X 10.10上测试开机启动计算器没有成功！用时间间隔来启动时可以的。

可以用crontab参数

*   -l    查看当前的crontab配置。
*   -r    移除所有配置
*   -e    编辑配置

### login items

login items是苹果公司对需要开机运行的应用程序推荐的启动方式。

有两种使用login item的方式：

1.  使用shard file list。
2.  使用Service Management framework。针对sandbox性能的程序[link]。

第一种方式：

使用第一种方式启动的login items在系统偏好设置->用户和群组>登录项里面可以查看并设置

![p7](http://drops.javaweb.org/uploads/images/3bb09d9ab6cde194c4ce51be78beacfbdd036a6d.jpg)

在这个界面可以添加，删除登录项。

这些登录项的信息都保存在`~/Library/Preferences/com.apple.loginitems.plist`配置文件中，每一个启动项对应一个字典，有Alias，Name等，其中Name是NSString类型，其它是Data类型，进行了base64，所以目前可以删除。（手工添加有文章说可以，在OS X 10.10.x中笔者暂时没有找到方法）。

另外就是通过程序来添加：

```
LSSharedFileListRef loginItems = LSSharedFileListCreate(NULL, kLSSharedFileListSessionLoginItems, NULL);  //url为app所在的目录 
CFURLRef url = (CFURLRef)[NSURL fileURLWithPath:appPath];
LSSharedFileListItemRef item = LSSharedFileListInsertItemURL(loginItems, kLSSharedFileListItemLast, NULL, NULL, url, NULL, NULL); 
CFRelease(item);
CFRelease(loginItems);

```

有的恶意软件就是利用代码添加login item的方式来实现自启动的。

第二种方式：

使用login item的程序如果是用了沙盒技术就会因为权限问题无法使用第一种方式了。必须使用Service Management Framework。要求有两个程序：一个主程序一个helper程序。helper程序存放在主程序的`Contents/Library/LoginItems`目录下。主程序在运行时调用`SMLoginItemSetEnabled()`函数来设置helper程序为自启动程序。具体可以参考[[link]](http://martiancraft.com/blog/2015/01/login-items/)[[link]](http://www.tanhao.me/pieces/590.html/)。

注意：你的主程序必须在Application的目录下，开机启动的设置才会生效，否则会失败

### StartupItems

这是苹果公司不推荐的启动方法。但是在现在版本中还没有失效。

一个Startup Item是一个特殊的文件。可以在系统boot进程中得到执行。

创建过程如下：

1，创建目录

StartupItems存放在以下两个路径下：

*   `/System/Library/StartupItems`
*   `/Library/StartupItems`（默认情况下是不存在的，需要自己手动创建）

2，生成执行程序或脚本

程序或脚本必须和目录名一样，可执行文件需要获得root权限。

一般使用shell script，因为其创建和更新更为简单。

下图是一个例子：

![p8](http://drops.javaweb.org/uploads/images/1f5b538f4dc3bca22246ea60bc878d849f54eb17.jpg)

开机启动后系统会自动向脚本给出start作为参数。“$1” 表示传给该脚本的第一个参数

StartService(), StopService(), RestartService()

当可执行文件接收到的参数为start，stop或者restart时，执行相对应的函数。

3，创建`StartupParameters.plist`

在目录中创建该文件`StartupParameters.plist`是一个属性列表。

![p9](http://drops.javaweb.org/uploads/images/52a4a0071854f44d9a6206a777eab98a0b4311ec.jpg)

关于plist中主要的字段

可以参考：

![p10](http://drops.javaweb.org/uploads/images/9df3a311abd1b01cc38fb442d43017486ca0c16f.jpg)

### Binary infection

二进制感染实现驻留。

原理和windows系统下的PE文件感染一样。修改二进制文件获取执行权限执行自己的代码。

因为OS X允许未签名的二进制文件运行。所以该方法依然有效。且感染的方式多种多样。其中最简单的就是修改入口点了。通过修改Mach-O文件的Load Commands。添加新的segment来实现代码的注入感染。

0x02 检测
=======

* * *

针对启动项的检测，bit9的报告针对企业和个人给出了建议。

这里给大家介绍下针对个人Mac的检测方法。

除了手动针对启动项的位置进行检测外，你当然还可以用用脚本。不过推荐一个不错的工具

[https://objective-see.com/products/knockknock.html](https://objective-see.com/products/knockknock.html)

该工具自动扫描9中启动方式。

![p11](http://drops.javaweb.org/uploads/images/81abdfba4983a2265840895fb2119e02af7d251d.jpg)

读者可以利用此工具来进行一个快速的检测。

该工具的作者还开发了一款启动项动态监控软件

[https://objective-see.com/products/blockblock.html](https://objective-see.com/products/blockblock.html)

可以动态的拦截启动项的添加。大家不妨试试。

0x03 参考
=======

* * *

1.  2015: The Most Prolific Year for OS X Malware  
    [https://www.bit9.com/resources/research-reports/2015-the-most-prolific-year-for-os-x-malware/](https://www.bit9.com/resources/research-reports/2015-the-most-prolific-year-for-os-x-malware/)
2.  VB2014 paper: Methods of malware persistence on Mac OS X[https://www.virusbtn.com/virusbulletin/archive/2014/10/vb201410-malware-persistence-MacOSX](https://www.virusbtn.com/virusbulletin/archive/2014/10/vb201410-malware-persistence-MacOSX)
3.  Levin, J. Mac OS X and iOS Internals: To the Apple’s Core. Wrox. 2012
4.  Mac OSX的开机启动配置[http://www.tanhao.me/talk/1287.html/](http://www.tanhao.me/talk/1287.html/)
5.  在SandBox沙盒下实现程序的开机启动[http://www.tanhao.me/pieces/590.html/](http://www.tanhao.me/pieces/590.html/)
6.  苹果手册[https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/Introduction.html](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/Introduction.html)