# 首例具有中文提示的比特币勒索软件“LOCKY”

0x00 概述
=======

* * *

安天安全研究与应急处理中心（安天CERT）发现一款新的勒索软件家族，名为“Locky”，它通过RSA-2048和AES-128算法对100多种文件类型进行加密，同时在每个存在加密文件的目录下释放一个名为_Locky_recover_instructions.txt的勒索提示文件。经过安天CERT研究人员分析发现，这是一类利用垃圾邮件进行传播的勒索软件，是首例具有中文提示的比特币勒索软件。

0x01 样本分析
=========

* * *

### 1.1 样本标签

| 病毒名称 | Trojan/Win32.Locky.a |
| 原始文件名 | ladybi.exe |
| MD5 | FB6CA1CD232151D667F6CD2484FEE8C8 |
| 处理器架构 | X86-32 |
| 文件大小 | 180 KB (184,320 字节) |
| 文件格式 | BinExecute/Microsoft.EXE[:X86] |
| 时间戳 | 42B63E17->2005-06-20 11:55:03 |
| 数字签名 | NO |
| 加壳类型 | 无 |
| 编译语言 | Microsoft Visual C++ 6.0 |
| VT首次上传时间 | 2016-02-16 10:53:39 |
| VT检测结果 | 41/55 |

### 1.2 样本功能

该勒索软件“Locky”使用绑架用户数据的方法对用户进行敲诈勒索。它通过RSA-2048和AES-128算法对100多种文件类型进行加密，同时在每个存在加密文件的目录下释放一个名为_Locky_recover_instructions.txt的勒索提示文件。

“Locky”样本的本地行为：复制自身到系统临时目录%Temp%下，并重新命名为svchost；对系统中的文件进行遍历，判断文件后缀名是否在样本内置的列表中，若存在，则对样本进行加密操作；在多个文件夹中创建提示文件_Locky_recover_instructions.txt；在桌面上创建文件_Locky_recover_instructions.bmp；并将该文件设置为桌面背景，提示用户如何操作可以成功恢复被加密的文件；添加相关注册表键值；删除系统还原快照。

**复制自身到%Temp%目录下名为svchost.exe,并添加启动项。**

**加密上百种文件类型如下：**

> .m4u .m3u .mid .wma .flv .3g2 .mkv .3gp .mp4 .mov .avi .asf .mpeg .vob .mpg .wmv .fla .swf .wav .mp3 .qcow2 .vdi .vmdk .vmx .gpg .aes .ARC .PAQ .tar.bz2 .tbk .bak .tar .tgz .gz .7z .rar .zip .djv .djvu .svg .bmp .png .gif .raw .cgm .jpeg .jpg .tif .tiff .NEF .psd .cmd .bat .sh .class .jar .java .rb .asp .cs .brd .sch .dch .dip .pl .vbs .vb .js .asm .pas .cpp .php .ldf .mdf .ibd .MYI .MYD .frm .odb .dbf .db .mdb .sql .SQLITEDB .SQLITE3 .asc .lay6 .lay .ms11 .sldm .sldx .ppsm .ppsx .ppam .docb .mml .sxm .otg .odg .uop .potx .potm .pptx .pptm .std .sxd .pot .pps .sti .sxi .otp .odp .wb2 .123 .wks .wk1 .xltx .xltm .xlsx .xlsm .xlsb .slk .xlw .xlt .xlm .xlc .dif .stc .sxc .ots .ods .hwp .602 .dotm .dotx .docm .docx .DOT .3dm .max .3ds .xml .txt .CSV .uot .RTF .pdf .XLS .PPT .stw .sxw .ott .odt .DOC .pem .p12 .csr .crt .key

**对路径和文件名中包含下列字符串的文件不进行加密：**

> tmp, Application Data, AppData, Program Files (x86), Program Files, temp, thumbs.db, $Recycle.Bin, System Volume Information, Boot, Windows

**“Locky”添加的注册表项:**

```
HKCU\Software\Locky
HKCU\Software\Locky\id
HKCU\Software\Locky\pubkey
HKCU\Software\Locky\paytext
HKCU\Software\Locky\completed
HKCU\Control Panel\Desktop\Wallpaper      "%UserProfile%\Desktop\_Locky_recover_instructions.bmp"

```

**删除系统还原快照**

通过调用`vssadmin.exe Delete Shadows /All /Quiet`删除全盘所有卷影副本，使受害系统不能够通过卷影副本进行系统还原。

**网络行为：**

*   向C&C服务器发送被感染机器的部分信息。
*   从C&C服务器下载RSA公钥，为后面的加密做准备。
*   上传将被加密的文件列表。
*   根据系统语言从服务器获取对应的提示信息。

### 1.3 相关技术

**1.3.1 域名生成算法**

“Locky”样本会首先使用函数rdtsc获取处理器时间，将该值与某变量进行求余运算，通过对该值的判断来决定样本是访问使用算法生成的域名，还是直接访问样本中的硬编码IP地址。这样可以使样本具有一定的随机性。

![p1](http://drops.javaweb.org/uploads/images/a16d83b072dc36b3703448edfefce2790ab8c7d7.jpg)图1 域名生成算法

域名在生成的时候，需要使用一个随机数，该随机数的计算是根据被感染机器的年月日进行的。

![p2](http://drops.javaweb.org/uploads/images/b65048abd97267def7d994df6fc145d263878690.jpg)图2 随机值计算

**1.3.2 C&C服务器**

受害主机与服务器是使用HTTP Post请求进行交互。受害主机访问C&C服务器上的main.php，参数有以下几个：

| 参数 | 含义 |
| --- | --- |
| id | 随机生成的编号 |
| act | C&C控制命令 |
| affid | 会员ID |
| lang | 计算机所使用的语言 |
| corp | 未知 |
| serv | 未知 |
| os | 操作系统 |
| sp | 补丁包 |
| x64 | 是否为64位系统 |

受害主机所有发出的请求都使用样本中硬编码的key进行加密操作，加密后发送到C&C服务器。从服务器中接收的数据包同样使用特定的加密方法加密，接收到加密数据后，“Locky”会首先进行解密操作。

加密的数据包部分内容：

![p3](http://drops.javaweb.org/uploads/images/112b39202007b7344007a622d20568d6b216e904.jpg)图3 数据包内容

数据包发送时加密的算法：

![p4](http://drops.javaweb.org/uploads/images/0969fdc424ff36fcf0ca128504df0f79d5c810ba.jpg)图4 加密算法

接收到数据时，样本的解密算法：

![p5](http://drops.javaweb.org/uploads/images/b9765f95f7481737f9f237d7ed8b515e524deae6.jpg)图5 解密算法

**1.3.3 控制命令**

目前所知道的控制命令有四种，分别为：**stats**、**getkey**、**report**、**gettext**。

| 命令 | 功能 |
| --- | --- |
| stats | 发送一些基本信息，如：已成功加密的文件个数、加密失败的文件个数、长度。 |
| getkey | 从服务器上下载加密时使用的RSA的公钥。 |
| report | 向服务器发送加密的文件列表。 |
| gettext | 获取提示用户如何解密的信息，C&C服务器会根据回传的计算机所使用的语言来返回对应的语言提示信息，如：回传zh会返回汉语、回传en会返回英语。 |

中文的提示信息如下：

![p6](http://drops.javaweb.org/uploads/images/d6c4225aae1893a446bb6ec6ee16125efa8539ee.jpg)图6 提示内容

0x02 总结
=======

* * *

通过安天CERT目前的分析来看，勒索软件“Locky”的功能与之前分析的勒索软件【1】的功能基本一致。勒索软件能给攻击者带来巨大的收益，因其使用比特币进行交易，所以很难追踪；一旦用户感染了勒索软件，只能付费进行解密或是丢弃这些文件。安天CERT提示广大用户，即使支付赎金也不一定能保证可以完全恢复被加密的文件。防止数据被加密，更应该注意勒索软件的防御，养成良好的上网使用习惯，不要轻易执行来历不明的文件。

“Locky”和其他勒索软件的目的一致，都是加密用户数据并向用户勒索金钱。与其他勒索软件不同的是，它是首例具有中文提示的比特币勒索软件，这预示着勒索软件作者针对的目标范围逐渐扩大，勒索软件将发展出更多的本地化版本。

安天CERT预测，今后中国将受到更多类似的勒索软件攻击。所以，如何防御勒索便成为保卫网络安全的重要任务之一。

0x03 附录
=======

* * *

### 一、参考资料

*   【1】 揭开勒索软件的真面目[http://www.antiy.com/response/ransomware.html](http://www.antiy.com/response/ransomware.html)