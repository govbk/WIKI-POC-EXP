# 利用第三方软件 0day 漏洞加载和执行的木马分析

0x00 前言
=======

* * *

近期腾讯反病毒实验室捕获了一批针对性攻击的高级木马,该木马使用近期热门的时事 话题做诱饵,对特殊人群做持续针对性攻击,目前腾讯电脑管家已经能够准确拦截和查杀该 木马。

![enter image description here](http://drops.javaweb.org/uploads/images/7eb29a5e7bf5a5eda80b435be890cb1fcd7ece9c.jpg)

图 1. 腾讯反病毒实验室拦截到的部分木马文件压缩包

0x01 分析
=======

* * *

该木马主要通过邮箱等社交网络的方式对特定用户进行针对性推送传播,原始文件伪装 成常见的 windows 软件安装程序,一旦用户运行了该木马文件,便会将包含 0day 漏洞的一 个第三方软件及相应的库文件释放到指定目录中,同时释放一个加密的数据文件到同一目录 下。将含有针对性 0day 漏洞攻击的命令行参数传递给该文件执行。随后进行自毁操作,不 留痕迹。

![enter image description here](http://drops.javaweb.org/uploads/images/31f6ff2ea332e29666914f474b4919dc0e13a543.jpg)

图 2. 木马安装后将特定的第三方软件文件释放到磁盘指定目录中

**该木马释放出的所有 PE 文件均为 9158 多人视频聊天软件的模块,具有很大的用户群, 文件有完整且正确的该公司的数字签名信息。其中的 science.exe 在解析命令行参数时存在 缓冲区溢出漏洞,且编译的时候未开启 GS 等安全开关,触发后能够执行参数中携带的任意 Shellcode 恶意代码。**这也是木马找到这个白文件漏洞来利用的原因,用户群体大,漏洞非 常方便利用。由于恶意代码是在正常文件的内存中直接执行,同时在磁盘中驻留的文件均为 正常软件的白文件,因此此木马绕过了几乎所有安全防护软件。腾讯电脑管家使用了云查引 擎,第一时间发现并查杀该木马,同时已经第一时间通知相关厂商修复该漏洞。

![enter image description here](http://drops.javaweb.org/uploads/images/d50b573b24c9a7c8fca6cc0b90e98d3a19b7fa70.jpg)

图 3. 9158 多人视频软件安装目录,对比发现,木马释放的 PE 均在其中

以下是木马加载执行的详细过程:

*   1 首先释放文件到指定目录,共 5 个文件,其中 science.exe、DDVCtrlLib.dll、 DDVCtrlLib.dll 均是 9158 多人聊天软件的相关文件,Config.dat 是一个加密的数据文件,t1.dat 是一个配置文件。
    
*   2 带参数运行 science.exe,其中参数共 0x2003 字节,随后原始木马文件进行自毁操作
    

![enter image description here](http://drops.javaweb.org/uploads/images/df896ea2b86b938877bfb8ce1fdaa9b46c9d62c0.jpg)

图 4. 使用含有恶意代码的参数执行含有 0day 漏洞的文件

*   3 由于 science.exe 对输入的参数没有检查,当输入的参数长度过长时,造成栈溢出

![enter image description here](http://drops.javaweb.org/uploads/images/4f9e4152646c37581494426938cad2ea9c28b747.jpg)

图 5. 漏洞细节:由于软件解析参数时没有校验长度,导致缓冲区溢出

![enter image description here](http://drops.javaweb.org/uploads/images/1ce9abcaf74ce5c99f50014a2742dea9f1c1f6f6.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/e724d02dd0733c41eccb89942fa0291087a449f6.jpg)

图 6.漏洞利用细节:精心构造最后三字节数据精确定位跳转执行 ShellCode

![enter image description here](http://drops.javaweb.org/uploads/images/58ea132c10fbec2151c076a4ba22dd73463e50a6.jpg)

图 7. ShellCode 的自解密算法

![enter image description here](http://drops.javaweb.org/uploads/images/6faaa46e46d5781ef44cb0c72eba1ae460647e08.jpg)

图 8. ShellCode 的功能是读取并解密 Config.dat 文件,直接在内存中加载执行

![enter image description here](http://drops.javaweb.org/uploads/images/cabb94c53b8890e15e730fb3ea98995c0a98a334.jpg)

图 9.创建一个系统服务,服务对应的镜像文件为 science.exe,并带有恶意参数

0x02 结语
=======

* * *

木马通过创建服务来实现永久地驻留在用户电脑中,实现长期地监控。完成 服务创建后,即完成了木马的安装过程,为了隐蔽运行不被用户发觉,木马服务 启动后会以创建傀儡进程的方式注入到 svchost.exe 进程中,在该进程中连接 C&C 服务器,连接成功后黑客便可通过该木马监视用户桌面、窃取用户任意文件、 记录用户键盘输入、窃取用户密码、打开摄像头和麦克风进行监视监听等。从而 实现远程控制目标计算机的目的。