# drozer模块的编写及模块动态加载问题研究

drozer是MWR Labs开发的一款Android安全测试框架。是目前最好的Android安全测试工具之一。drozer提供了命令行交互式界面，使用drozer进行安全测试，用户在自己的console端输入命令，drozer会将命令发送到Android设备上的drozer agent代理程序执行。drozer采用了模块化的设计，用户可以定制开发需要的测试模块。编写drozer模块主要涉及python模块及dex模块。python模块在drozer console端运行，类似于metasploit中的插件，可以扩展drozer console的测试功能。dex模块是java编写的android代码，类似于android的dex插件，在android手机上运行，用于扩展drozer agent的功能。

0x00 简单的drozer模块demo代码
======================

* * *

首先看看drozer wiki给出的demo，该模块的功能就是在android设备上反射调用java.util.Random类生成一个随机数并返回：

```
from drozer.modules import Module

class GetInteger(Module):

    name = ""
    description = ""
    examples = ""
    author = "Joe Bloggs (@jbloggs)"
    date = "2012-12-21"
    license = "BSD (3-clause)"
    path = ["exp", "test"]

    def execute(self, arguments):
        random = self.new("java.util.Random")
        integer = random.nextInt()

        self.stdout.write("int: %d\n" % integer)

```

GetInteger类就是一个简单的drozer模块，它继承自drozer提供的模块基类Module。每个继承了Module的类都对应着一个drozer模块，模块具体实现的功能则是在类中重写excute函数，实现新的功能。在drozer console中执行以下命令就可以运行该模块了：

```
dz> run exp.test.getinteger

```

运行效果如下：

![1](http://drops.javaweb.org/uploads/images/98d3043290f44693b850f28c8035e7492eb984bf.jpg)

drozer 通过Module类的metadata来配置和管理每个模块,因此模块编写时需要包含以下 metadata信息:

```
name          模块的名称
description   模块的功能描述 
examples      模块的使用示例
author        作者
date          日期
license       许可
path          描述模块命令空间

```

这些信息中比较重要的就是path变量，它描述了模块在drozer namespace中的路径，结合对应的classname可以唯一确定drozer中的模块。例如demo中的`path = ["exp", "test"]`,类名为GetInteger，那么在drozer console中该模块就以exp.test.getinteger唯一确定。需要注意的是，尽管类的名字有大小写之分，但运行该模块的时候，drozer console中的名字都为小写。

0x01 drozer模块仓库的创建及模块安装
=======================

* * *

drozer模块安装有两种方法，一种是直接在repository中按照python包管理的方法新建目录结构，将python文件放入相应目录中，另一种是在drozer console中通过module install命令直接安装模块。

这两种方法都必须先在本地创建一个drozer 的repository目录，可以直接在drozer console中通过命令创建：

```
 dz> module repository create [/path/to/repository]

```

也可以在`~/.drozer_config`文件中指定本地repository目录

```
[repositories]  
/path/to/repository  =  /path/to/repository

```

创建好本地repository后就可以安装自己的模块了。两种安装方法：

1) 按照python包管理的方式，在本地repository目录下创建目录exp,新建__int__.py空白文件，然后将Python模块源码放入exp目录即可。例如将test.py放入exp目录下，test.py的内容如下：

```
from drozer.modules import Module

class GetInteger(Module):

    name = ""
    description = ""
    examples = ""
    author = "Joe Bloggs (@jbloggs)"
    date = "2012-12-21"
    license = "BSD (3-clause)"
    path = ["exp", "test"]

    def execute(self, arguments):
        random = self.new("java.util.Random")
        integer = random.nextInt()

        self.stdout.write("int: %d\n" % integer)

```

安装好模块之后即可在drozer console端通过命令`run exp.test.getinteger`运行该模块了。

2) 通过drozer console中的命令module install 安装。首先将编辑好的python模块源文件命名为 exp.test2,文件的内容同上。在drozer console中执行

```
dz> module install  [/path/to/exp.test2]      

```

执行成功后则可以在本地repository目录下exp目录中看到生成了test2.py文件，内容和原来的exp.test2文件一致。安装成功后及可执行该模块了。module install除了可以安装本地仓库的模块外，还可以远程安装gitbub上的模块，地址为

[https://raw.github.com/mwrlabs/drozer-modules/repository/](https://raw.github.com/mwrlabs/drozer-modules/repository/)

例如运行

```
dz>module install jubax.javascript     

```

将远程下载并安装scanner.misc.checkjavascriptbridge模块，安装完成后执行

```
dz> run scanner.misc.checkjavascriptbridge

```

就可以运行该模块，该模块的功能是检查webview中addJavascriptInterface的使用是否存在安全隐患。

0x02 利用drozer提供的API扩展功能
=======================

* * *

drozer封装了android中大部分API功能，使得能够在python中方便的使用这些API扩展功能，发挥drozer及python的强大威力。

1）利用反射直接与Dalvik虚拟机交互，其实就是Python直接在写android代码，非常简单方便。drozer主要是利用了drozer agent代理实现相关功能，实例化某个类的代码如下：

```
my_object = self.new("some.package.MyClass")

```

例如drozer.android模块中封装了Intent类，用户可以通过如下方式构造需要的Intent：

```
someintent = android.Intent(action=act, category=cat, data_uri=data, component=comp, extras=extr, flags=flgs)

```

然后通过intent打开某个activity:

```
self.getContext().startActivity(someintent)

```

2) drozer针对比较常用的功能还二次封装了很多python的mixins工具类，提供了更简单易用的API，这些mixins都在drozer.modules.common包中：

*   Assets
*   BusyBox
*   ClassLoader
*   FileSystem
*   Filters
*   PackageManager
*   Provider
*   ServiceBinding
*   Shell
*   Strings
*   SuperUser
*   TableFormatter
*   ZipFile

例如FileSystem类提供了访问android手机文件系统的接口，可以方便地读写、创建及删除andoid手机上的目录和文件。ZipFile类提供了解压zip文件的功能。 为了使用这些mixin类提供的功能，在模块中可以直接继承这些类就可以了：

```
from drozer.modules import common, Module

class MyModule(Module, common.FileSystem, common.ZipFile):
           ……
           ……
       self.deleteFile(“somepath”)
           ……
           ……
       dex_file = self.extractFromZip("classes.dex", path, self.cacheDir())

```

其中，self.deleteFile来自FileSystem类，self.extractFromZip来自ZipFile类。

0x03 实现find port及find IP模块
==========================

* * *

1) app开放端口查找模块

Android app通常会监听某些端口进行本地IPC或者远程网络通信，但是这些暴露的端口却代表了潜在的本地或远程攻击面，具体可以参考大牛的文章：

[浅谈Android开放网络端口的安全风险](http://drops.wooyun.org/mobile/6973)

文章中提供了查找开放端口及对应app的python脚本，我们将其重写为drozer模块，方便测试时使用：

```
from drozer.modules import Module,common
import re

class findport(Module,common.Shell):

    name = ""
    description = "find open port in android"
    examples = "run exp.work.findport"
    author = "thor@ms509"
    date = "2015-12-02"
    license = "BSD (3-clause)"
    path = ["exp","work"]

    def toHexPort(self,port):
        hexport = str(hex(int(port)))
        return hexport.strip('0x').upper()     

    def finduid(self,protocol, entry):
        if (protocol=='tcp' or protocol=='tcp6'):
            uid = entry.split()[-10]

        else: # udp or udp6
            uid = entry.split()[-6]

        try: 
            uid = int(uid)
        except:
            return -1   
        if (uid > 10000): # just for non-system app
            return 'u0_a'+str(uid-10000) 
        else:
            return -1

    def execute(self, arguments):        

        proc_net = "/proc/net/"      
        ret = self.shellExec("netstat -anp | grep -Ei 'listen|udp*'")
        list_line = ret.split('\n')
        apps = []
        strip_listline = []
        #pattern = re.compile("^Proto") # omit the first line

        for line in list_line:              
                if (line != ''):               
                   socket_entry = line.split()
                   protocol = socket_entry[0]  
                   port = socket_entry[3].split(':')[-1]
                   grep_appid = 'grep  '+ self.toHexPort(port) + ' ' + proc_net + protocol                    

                   net_entry = self.shellExec(grep_appid)                         
                   uid = self.finduid(protocol, net_entry)

                   if (uid == -1): 
                       continue

                   applist = self.shellExec('ps | grep ' + uid).split()    
                   app = applist[8]
                   apps.append(app)
                   strip_listline.append(line)

        itapp= iter(apps)
        itline=iter(strip_listline)

        self.stdout.write("Proto  Recv-Q Send-Q  Local Address        Foreign Address        State            APP\r\n")
        try:
            while True:
                self.stdout.write( itline.next() + ' '*10 + itapp.next() + '\n')

        except StopIteration:
            pass

        self.stdout.write('\n')

```

该模块的主要功能都是在findport类中的execute函数中实现，查找开放端口及app的方法和原来文章中的一样，这里主要用到了drozer提供的common.Shell类，用于在android设备上执行shell命令：

```
ret = self.shellExec("netstat -anp | grep -Ei 'listen|udp*'") 

```

在drozer console中直接运行如下命令即可：

```
dz> run exp.work.findport

```

运行效果如下：

![image](http://drops.javaweb.org/uploads/images/689f3eb1b5489a8f950785a1d29283422a4f28d6.jpg)

2）app中IP地址扫描模块

drozer的scanner.misc.weburls提供了扫描app中http及https URL地址的功能，仿照该模块的功能，我们实现了app中IP地址的扫描模块，这些收集到的IP地址可以在web渗透测试中使用：

```
import re
from pydiesel.reflection import ReflectionException
from drozer.modules import common, Module 

class findips(Module, common.FileSystem, common.PackageManager, common.Provider, common.Strings, common.ZipFile):

    name = "Find IPs specified in packages."
    description = """
    Find IPs in apk files
    """
    examples = ""
    author = "7h0r@ms509"
    date = "2015-12-9"
    license = ""
    path = ["exp", "server"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("-a", "--package", help="specify a package to search")

    def execute(self, arguments):
        self.ip_matcher = re.compile(r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))")
        if arguments.package != None:
            self.check_package(arguments.package, arguments)
        else:
            for package in self.packageManager().getPackages(common.PackageManager.GET_PERMISSIONS):
                try:
                    self.check_package(package.packageName, arguments)
                except Exception, e:
                    print str(e)

    def check_package(self, package, arguments):
        self.deleteFile("/".join([self.cacheDir(), "classes.dex"]))
        ips = []

        for path in self.packageManager().getSourcePaths(package):
            strings = []
            if ".apk" in path:
                dex_file = self.extractFromZip("classes.dex", path, self.cacheDir())
                if dex_file != None:
                    strings = self.getStrings(dex_file.getAbsolutePath())

                    dex_file.delete()
                    strings += self.getStrings(path.replace(".apk", ".odex")) 
            elif (".odex" in path):
                strings = self.getStrings(path)
            else:
                continue

            for s in strings:
                m = self.ip_matcher.search(s)
                if m is not None:
                    ips.append(s)

            if len(ips) > 0:
                self.stdout.write("%s\n" % str(package))

            for ip in ips:
                    self.stdout.write("  %s\n" % ip)

            if len(ips) > 0 :
                self.stdout.write("\n")

```

`add_arguments`函数是drozer提供的接口，用于添加命令行参数，这里我们添加了`--package`参数，用于指定app名称，如果没有指定`--package`参数，那么默认会查找所有app中的IP地址，比较耗时。`check_package`函数主要实现指定app扫描IP地址的功能，该函数首先从app相关目录中查找apk文件、odex文件，如果是apk文件则从apk文件中解压出classes.dex文件：

```
for path in self.packageManager().getSourcePaths(package):
    strings = []
    if ".apk" in path:
        dex_file = self.extractFromZip("classes.dex", path, self.cacheDir())

```

然后从得到的dex、odex文件中获取到所有的strings:

```
strings = self.getStrings(path)

```

这里的getStrings是drozer提供的API，实现了类似linux下strings命令的功能。

找到app中的所有strings后再用re匹配得到相应的IP地址：

```
for s in strings:
    m = self.ip_matcher.search(s)
    if m is not None:
        ips.append(s)

```

ip_matcher的正则表达式为：

```
self.ip_matcher = re.compile(r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))")

```

最后，在drozer console中通过如下命令运行该模块：

```
dz> run exp.server.findips -a com.dianping.v1

```

运行效果如下所示：

![image](http://drops.javaweb.org/uploads/images/9c3a3d9b845926811b7cc4b2d2c2131f8569a063.jpg)

0x04 编写dex插件
============

* * *

除了利用drozer以python代码形式提供的API，用户还可以用java代码编写dex插件。 例如下面的java代码就可以编译为drozer的dex插件：

```
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

import android.util.Base64;
import android.util.Log;
import android.widget.Toast;
import android.net.Uri;
import android.content.ContentResolver;
import android.database.Cursor;
import android.provider.ContactsContract;
import android.content.Context;


public class dextest {

  private static final int BUFFER_SIZE = 4096;


    public static String test(Context c, String number) {

            String name = null;
            Uri uri = Uri.parse("content://com.android.contacts/data/phones/filter/" + number);
            ContentResolver resolver = c.getContentResolver();
            Cursor cursor = resolver.query(uri, new String[]{android.provider.ContactsContract.Data.DISPLAY_NAME}, null, null, null);
            if (cursor.moveToFirst()) {
                name = cursor.getString(0);
                Log.d("drozer", name);
            }
            cursor.close();


         Log.d("drozer","this is a drozer dex module!");
         return "hello world! this is a test! " + number + ": " + name;
  }

}

```

首先我们将该java文件编译为class文件：

```
javac -cp lib/android.jar dextest.java

```

然后用android sdk提供的dx工具将class文件转换为dex文件：

```
dx  --dex --output=dextest.apk dextest*.class

```

最后将生成的dextest.apk文件放到drozer的modules/common目录下，在编写drozer模块时可以通过以下方式调用该dex插件：

```
dextest = self.loadClass("common/dextest.apk", "dextest")
self.stdout.write("[color red]get string from dex plugin: %s  [/color]\n" % dextest.test(self.getContext(),"181" ) )   

```

该测试插件根据提供的部分电话号码去匹配手机通讯录中的联系人，并返回匹配到的联系人姓名，执行效果如下:

![2](http://drops.javaweb.org/uploads/images/1676007950d411e12b790d56a0997254207ea7db.jpg)

dex插件是由drozer上传到android手机上加载执行，它的作用还是为drozer模块提供更方便易用的接口，扩展更多的功能。由于dex插件是Java编写的原生android代码，在执行效率上比通过反射调用更高。drozer的modules/common目录下包含了多个dex插件的源码，有兴趣的同学可以自己查看。

0x05 drozer模块的reload及动态加载问题
===========================

* * *

编写drozer module难免会涉及到调试的问题，drozer console提供了debug选项，会在console中打印异常信息，但是比较麻烦的是，修改module源码后必须要重启drozer console才能生效。

查看drozer源码，发现drozer在debug模式下提供了reload命令，但是测试了下，在mac下并没有用，还是要重启console才能生效。仔细研究drozer loader.py的相关源码：

```
def all(self, base):
     """
     Loads all modules from the specified module repositories, and returns a  collection of module identifiers.
     """

    if(len(self.__modules) == 0):
        self.__load(base)

    return sorted(self.__modules.keys())

def get(self, base, key):
    """
    Gets a module implementation, given its identifier.
    """

    if(len(self.__modules) == 0):
        self.__load(base)

    return self.__modules[key]

def reload(self):
    self.__modules = {}

```

reload命令将`self.__modules`置为空，在get中按理说就会重新加载所有的drozer模块。但是在mac下始终无法实现该功能，其他平台未做测试。这里就涉及到python模块的import及reload机制问题，在网上查找到python的reload机制一些解释：

> reload会重新加载已加载的模块，但原来已经使用的实例还是会使用旧的模块， 而新生产的实例会使用新的模块, reload后还是用原来的内存地址；不能支持from。。import。。格式的模块进行重新加载。  
> [http://blog.csdn.net/five3/article/details/7762870](http://blog.csdn.net/five3/article/details/7762870)

猜测可能就是这个问题，虽然用python的reload机制可以重新加载模块，但是以前使用的模块可能还是在使用中，导致修改的源码没有生效。

为什么不在执行时动态加载模块呢？这样可以保证加载的模块源码是最新的。

分析了drozer相关的所有源码，终于在session.py中找到实例化模块类的代码：

```
def __module(self, key):
    """
    Gets a module instance, by identifier, and initialises it with the
    required session parameters.
    """

    module = None

    try:
        module = self.modules.get(self.__module_name(key))
    except KeyError:
        pass

    if module == None:
        try:
            module = self.modules.get(key)
        except KeyError:
            pass

    if module == None:
        raise KeyError(key)
    else:
        return module(self)

```

该函数的功能就是根据模块类的key实例化该模块，从而运行该模块。因此，我们可以在这里实现动态加载要运行的模块类，放弃已经加载的模块：

```
 def __module(self, key):

    """
    Gets a module instance, by identifier, and initialises it with the
    required session parameters.
    """

    module = None

    try:
        module = self.modules.get(self.__module_name(key))
    except KeyError:
        pass

    if module == None:
        try:
            module = self.modules.get(key)
        except KeyError:
            pass

    if module == None:
        raise KeyError(key)
    else:

        #reload module
        mod = reload(sys.modules[module.__module__])

        module_class_name = module.__name__
        module_class = getattr(mod,module_class_name)  #get module class object
        return module_class(self)

```

关键的代码如下：

```
#reload module   
mod = reload(sys.modules[module.__module__])

module_class_name = module.__name__
module_class = getattr(mod,module_class_name)  #get module class object
return module_class(self)

```

首先使用python的reload函数重新加载指定的模块，然后再在重新加载的模块中查找到drozer模块关联的类，最后实例化并返回。只需添加几行代码便可实现动态加载模块类，这样调试的时候就不用每次重启drozer console了。这里只是提供了一种简单的实现动态加载模块的方法，主要是方便模块的编写及测试。