# Android sqlite load_extension漏洞解析

0x01 sqlite load_extension
==========================

* * *

SQLite从3.3.6版本（`http://www.sqlite.org/cgi/src/artifact/71405a8f9fedc0c2`）开始提供了支持扩展的能力，通过sqlite_load_extension API（或者load_extensionSQL语句），开发者可以在不改动SQLite源码的情况下，通过动态加载的库（so/dll/dylib）来扩展SQLite的能力。

![](http://drops.javaweb.org/uploads/images/264e54a6cc87da7aa4a668439887c6aceda07638.jpg)

便利的功能总是最先被黑客利用来实施攻击。借助SQLite动态加载的这个特性，我们仅需要在可以预测的存储路径中预先放置一个覆盖SQLite扩展规范的动态库（Android平台的so库），然后通过SQL注入漏洞调用load_extension，就可以很轻松的激活这个库中的代码，直接形成了远程代码执行漏洞。国外黑客早就提出使用load_extension和sql注入漏洞来进行远程代码执行攻击的方法，如下图。

![](http://drops.javaweb.org/uploads/images/74f7cacb50e1afa3746e9c313e4b860dd4357bf2.jpg)

也许是SQLite官方也意识到了load_extension API的能力过于强大，在放出load_extension功能后仅20天，就在代码中（http://www.sqlite.org/cgi/src/info/4692319ccf28b0eb）将load_extension的功能设置为默认关闭，需要在代码中通过sqlite3_enable_load_extensionAPI显式打开后方可使用，而此API无法在SQL语句中调用，断绝了利用SQL注入打开的可能性。

![](http://drops.javaweb.org/uploads/images/0f3445f823c7c3910be50ff33509d1f6d3095be3.jpg)

0x02 Android平台下的sqlite load_extension支持
=======================================

* * *

出于功能和优化的原因，Google从 Android 4.1.2开始通过预编译宏SQLITE_OMIT_LOAD_EXTENSION，从代码上直接移除了SQLite动态加载扩展的能力,如下图。

![](http://drops.javaweb.org/uploads/images/7c6f69e0251cd3da7a08c7c78ed853230e309d88.jpg)

可以通过adb shell来判断Android系统是不是默认支持load_extension，下图为Android4.0.3下sqlite3的.help命令：

![](http://drops.javaweb.org/uploads/images/ab8674b1d96886a34bb4f826427a39de5c078023.jpg)

可以看出支持load extension，而Android4.1.2上则没有该选项。

0x03 Android平台下的sqlite extension模块编译
====================================

* * *

sqlite extension必须包含sqlite3ext.h头文件，实现一个sqlite3_extension_init 入口。下图为一个sqlite extension的基本框架：

![](http://drops.javaweb.org/uploads/images/e26f524bd9b8a02b4c7bcab3bbe65424a91e78cb.jpg)

接着是Android.mk文件，如下图：

![](http://drops.javaweb.org/uploads/images/a0f011c4715feb5114ac5fd5a0fbaea2b8bafb9d.jpg)

我们实现一个加载时打印log输出的一个sqlie extension：

![](http://drops.javaweb.org/uploads/images/72a89233a972aac8eb7f6c5f2513698f2e6772fc.jpg)

0x04 Android平台下sqlite load_extension实战
======================================

* * *

由于sqlite是未加密的数据库，会导致数据泄露的风险，Android App都开始使用第三方透明加密数据库组件，比如sqlcipher。由于sqlcipher编译时没移除load extension，如图，导致使用它的App存在被远程代码执行攻击的风险。

![](http://drops.javaweb.org/uploads/images/4a8c19487c70e00229f61ec28caa950ec76733ab.jpg)

![](http://drops.javaweb.org/uploads/images/2dd78348c3958488601de03119ac3b6c3165d2ba.jpg)

下面我们将通过一个简单的demo来展示sql注入配合load_extension的漏洞利用。

首先，实现一个使用sqlcipher的Android程序，下载sqlcipher包，将库文件导入项目，如下图：

![](http://drops.javaweb.org/uploads/images/6b462b789d80512a39561d7b2845dcd504bd5c26.jpg)

将导入包换成sqlcipher的：

![](http://drops.javaweb.org/uploads/images/ed88667bfcee7f503e4ffb444e5777077d1bcd9e.jpg)

加载sqlcihper的库文件，并且打开数据库时提供密钥：

![](http://drops.javaweb.org/uploads/images/1eaa06344fec3af00dc53eeb77169470ec7e00de.jpg)

编译的时候如果出错，则将jar包引入并导出，如下图：

![](http://drops.javaweb.org/uploads/images/7479840801e969b29ba1b7e7fbdb6928671d8483.jpg)

![](http://drops.javaweb.org/uploads/images/f0cd8ae02dba27d7a2ae15744885dc92e2b78ddd.jpg)

实现一个存在sql注入的数据库查询语句，外部可控，如下图：

![](http://drops.javaweb.org/uploads/images/d3e6669f57af27ea2cc8757a3fe913ef68f1812d.jpg)

**该函数接收一个外部可控的参数，并将数据库查询语句进行拼接，导致可被外部植入恶意代码进行**代码执行攻击，如下图：

![](http://drops.javaweb.org/uploads/images/5d4c77e5d20247ee7bf9d781feb7cff2499515f4.jpg)

执行之后，可以看到so加载成功，如下图：

![](http://drops.javaweb.org/uploads/images/dcb847079765bbff41f4e7247f1a25339c3cb3c0.jpg)

0x05 Android平台下sqlite load_extension攻防
======================================

* * *

**攻击场景：**存在漏洞的app可以接收文件，黑客可将文件通过目录遍历漏洞放到app私有目录下，再通过发消息触发sql注入语句，完美的远程代码执行攻击。

**漏洞防御：**

1.  由于sqlcipher的扩展默认是开启的，如果需要sqlcipher，编译sqlcipher的时候通过SQLITE_OMIT_LOAD_EXTENSION宏来关闭sqlcipher的扩展功能。
2.  进行数据库操作时，禁止将查询语句进行拼接，防止存在sql注入漏洞。