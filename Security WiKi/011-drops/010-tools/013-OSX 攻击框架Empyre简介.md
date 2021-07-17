# OSX 攻击框架Empyre简介

0x00 简介
=======

* * *

随着OSX使用者越来越多，针对OSX的攻击也越来越多。前不久，Empire团队又推出一个新的攻击框架，针对于OSX的攻击框架[Empyre](https://github.com/adaptivethreat/EmPyre)，此框架由Python建立在密码学基础上编写，使用过[Empire](https://github.com/PowerShellEmpire/Empire)的同学对此框架应该能很快上手，此文将对Empyre框架的使用方式做一下简单的的介绍。

0x01 安装
=======

* * *

使用如下命令进行安装：

```
☁  Desktop  git clone https://github.com/adaptivethreat/EmPyre 
☁  Desktop  cd EmPyre/setup
☁  setup [master] ./install.sh

```

> 安装脚本会安装一些依赖库，并且最后执行setup_database.py 进行各项设置，可以手工修改。setup目录下的reset.sh脚本可以对EmPyre进行重置。

0x02 使用
=======

* * *

进入主目录，执行

```
☁  EmPyre [master] python empyre

```

则可进入主菜单

![Alt text](http://drops.javaweb.org/uploads/images/ad54086be008e8b0e10149a713cfb032ec2147d7.jpg)

> 现在已经包含了43个可使用的模块

### Listeners

要使用此框架，首先需要创建Listeners，直接输入listeners则可进去Listeners的配置页面，输入help，可以查看帮助，info命令可以查看详细的配置信息，下面截图是一个简单的Listeners配置。

![Alt text](http://drops.javaweb.org/uploads/images/b1bead6614b9327a563fb16f2fd11022563759d0.jpg)

配置监听的ip及端口需要设置Host

```
set Host http://192.168.74.141:8080

```

之后执行

```
(EmPyre: listeners) > execute

```

可以开启监听，使用list可以查看开启的listener

![Alt text](http://drops.javaweb.org/uploads/images/768fbe6a3d99aa1b36c062d4e21bee4ac2371e62.jpg)

如果需要配置HTTPS的listener，需要配置CertPath

```
set CertPath ./data/empyre.pem

```

### Stagers

创建好Listeners之后，需要配置Stagers ，Stagers 存放在./lib/stagers 目录下，现在已有的stagers如下：

![Alt text](http://drops.javaweb.org/uploads/images/1a25eaa557c451afc779e568dc861e8ebfd23fdd.jpg)

在listeners下输入usestager+空格之后按TAB键则可看到这些可用的stagers。现在可用的stagers 分别为：

*   `applescript`: 生成[AppleScript](http://baike.baidu.com/link?url=zsL0NIp8nLJgYPF49Fyjveo9VjaaM71GXpv-Y_hVerLyubu_5FIj8UiFnpc_sn5LXLLAoae6Mu94mFEgCuue5a)的payload。
*   `dylib`: 生成动态库类型的payload。（怎么使用请看[这里](http://qvb3d.iteye.com/blog/1176920)）
*   `hop_php`: 生成php类型的payload。
*   `launcher`: 生成一行python代码作为payload。
*   `macho`: 生成macho类型的payload(OSX可执行文件)。
*   `macro`: 生成MAC Office宏。
*   `safari_launcher`: 生成一个HTML文件作为payload。(诱使用户运行applescript)
*   `war`: 生成war类型的payload。

launcher为生成一行代码，被攻击者运行代码则被攻击者控制，下面使用macro以及safari_launcher两个好玩儿的方式来做一下示例：

**1、macro**

使用方式如下图：

![Alt text](http://drops.javaweb.org/uploads/images/bac2924c4750175bad9cae88b6b0d7e6d292100e.jpg)

生成宏代码，创建任意office文件。打开宏设置

![Alt text](http://drops.javaweb.org/uploads/images/b1df7399c4cdf345fa5ef9481ddbe4c521bebeb1.jpg)

将宏代码写入：

![Alt text](http://drops.javaweb.org/uploads/images/400a4dc40e2efbe64bc34ad0d714f84c0cbf42e7.jpg)

之后再次打开此work会有如下提示：

![Alt text](http://drops.javaweb.org/uploads/images/a7999a54317ccbaff0ca098f8da02100fccaa2b8.jpg)

点击启用宏，执行代码，受害者被控制：

![Alt text](http://drops.javaweb.org/uploads/images/03593a44377993fdec9ad172e94b01b636c8e60b.jpg)

**2、safari_launcher**

使用方式如下：

![Alt text](http://drops.javaweb.org/uploads/images/506236905656226f767dc2eeebfdfe7cd49a6176.jpg)

将生成的html代码保存到test.html，放到web服务器上，可以看到代码中的`applescript`则为要执行的applescript代码。访问此页面如下图：

![Alt text](http://drops.javaweb.org/uploads/images/df9fb805432276c701f4e39b659c843b9b43d7a9.jpg)

按`Command+R`键以后，弹出如下页面：

![Alt text](http://drops.javaweb.org/uploads/images/c707e9486301444f407db84a4e7a1f2cc401a878.jpg)

点击新脚本，打开脚本编辑器，代码藏在最下面：

![Alt text](http://drops.javaweb.org/uploads/images/3ed4141ad84c38d7ed9c4b2504c414137185ddc4.jpg)

一旦点击三角符号的运行按钮，则受害者被控制：

![Alt text](http://drops.javaweb.org/uploads/images/6fa16619d76137de213d87115f0dcddbbce8ded5.jpg)

> 其他的就不多介绍了，有兴趣的可以自己尝试一下

### agents

**1、基础使用**

获取agents怎么使用呢，首先可以查看help:

![Alt text](http://drops.javaweb.org/uploads/images/9b47389e3a6b71470a66c620eac8c304138a6b53.jpg)

命令比较简单，要切换到一个agent,使用如下命令即可：

```
interact PI5M01QWZ4TJAUQA

```

如果觉得名字不好记，可以执行如下命令对agnet进行重命名：

![Alt text](http://drops.javaweb.org/uploads/images/e05d77b56792669d357245b31ef3b8395d309878.jpg)

切换到agent里面之后，可以help查看可执行的命令:

![Alt text](http://drops.javaweb.org/uploads/images/f7740b653c1f8d8b00eb3903c461f7ef9af5b2f2.jpg)

如果要执行系统命令，可使用shell来执行：

![Alt text](http://drops.javaweb.org/uploads/images/5b143cebd0ea4058f20cd3b03a2c9b5168a7bfb4.jpg)

**2、模块使用**

Empyre提供了多个可使用模块，输入usemodule空格之后按TAB键则可列出当前可使用的模块，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/20ec97de088b29810be21314720fbc0c8770b78b.jpg)

包括信息搜集，权限提升，维持权限等多个模块，这里就不一一介绍了，介绍几个比较好玩儿的：

_collection/osx/prompt_:

> 此模块可通过社会工程学获取当前用户所用的密码。

![Alt text](http://drops.javaweb.org/uploads/images/c7c70bb7aef27287cff33c9aa1b859587b6000f2.jpg)

运行以后，会打开AppStore，并询问密码，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/68293c5fc9736685af7c3416bbc7d637830956f1.jpg)

当用户输入密码以后，我们就获取到了他输入的密码：

![Alt text](http://drops.javaweb.org/uploads/images/1d9d34db7e34a360dbfdf72052a4e2619778abb5.jpg)

_collection/osx/webcam_:

> 此模块可进行摄像头拍照

![Alt text](http://drops.javaweb.org/uploads/images/cf3cdbed70ab7879c72ba579c6c04b5b62eaa20d.jpg)

_collection/osx/browser_dum_：

> 此模块可获取浏览器历史记录

![Alt text](http://drops.javaweb.org/uploads/images/27e2d56d6925a945b2085ba10c94f0065c686383.jpg)

_privesc/multi/sudo_spawn_

> 此模块可用于权限提升

首先创建一个新的Listener：

![Alt text](http://drops.javaweb.org/uploads/images/b7aa898d748d056c30426de369812dcbbb9283c1.jpg)

切换到agent以后，使用此模块：

![Alt text](http://drops.javaweb.org/uploads/images/1692d37fface28b125deb44e233c51681a979359.jpg)

可以看到输入密码以后（密码可以通过prompt模块或者信息搜集获得），获取了一个新的agent，并且此agent获取了最高的权限，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/9b3b7184eea5d93b71d2529380e7219ac47f3ecc.jpg)

其他模块，我这里就不一一介绍了，有兴趣的小伙伴可以自己去尝试一下，而且维持权限的模块已经有4个了，还是很给力的。

0x03 小结
=======

* * *

看到这个工具还是挺开心的，本文仅仅是对此工具进行了一个简单的使用介绍，有兴趣的可以看一下源码然后自己编写自己所需要的模块或功能，希望此文对你能有所帮助。

**本文由Evi1cg原创并首发于乌云drops，转载请注明**