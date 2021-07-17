# BurpSuite插件开发指南之 Python 篇

此文接着 《BurpSuite插件开发指南之 Java 篇》 。在此篇中将会介绍如何使用 Python编程语言 开发 BurpSuite 的插件。

《BurpSuite 插件开发指南》系列文章如下：

*   [《BurpSuite插件开发指南之 API 篇》](http://drops.wooyun.org/tools/14685)
*   [《BurpSuite插件开发指南之 Java 篇》](http://drops.wooyun.org/tools/16056)
*   [《BurpSuite插件开发指南之 Python 篇》](http://drops.com:8000/#)

注：此系列文章是笔者利用业余时间所写，如有错误，望读者们及时指正，另外此系列文章属于入门级别的科普文，目的是普及Burp插件的编写技术。

0x00 Jython 简介
==============

* * *

BurpSuite 是使用 Java 编程语言编写的，所以想要使用 Python 编程语言开发其插件，就必须借助于 Jython。Jython 本质上是一个 Java 应用程序，它允许 coder 们使用 Java 代码调用 Python 库反之，也可以使用 Python 调用 Java 的库。

有关 Jython 的详细使用，请读者参阅 Jython 官网的[用户手册](https://wiki.python.org/jython/UserGuide)和 相关 doc。

类似于 Jython 的 Project 还有 JRuby ，并且 Burp 也支持 ruby 编写插件，但是无论是用 Python 还是 Ruby 编写的插件，在执行效率方面远远不如原生的 Java 高，所以笔者还是建议使用 Java 编写插件。

0x01 Python 编写 Burp 插件
======================

* * *

Python 编写 Burp 插件辅助工具
---------------------

### Jython Burp API

使用 Python 编写 Burp 插件的时候会遇到各种琐碎的麻烦。最主要的原因在于，Java 与 Python 编程语言特性上的差异，如：强弱类型，数据类型等以及 Jython 本身与 CPython 的一些不同（具体请看 Jython 官网文档）。不过在熟悉了 Burp 接口和基本的编写套路后，一切都会变得很简单。

国外有牛人编写了一个 Jython Burp API，封装了一些功能，可以很方便的获取 Burp 数据并且可以调试 Jython 代码。具体使用说明请看 Git 文档。

> [Jython Burp API Git 地址](https://github.com/mwielgoszewski/jython-burp-api)

注：

加载 Jython Burp API 时会出现 sys 模块 PS1 PS2 未定义的错误。后来 Google 后发现这个是 Jython 本身的一个 Bug，不过官方已有 Issue 会在后续的版本中进行修复。

解决此错误的方法如下：

> 编辑**jython-burp-api/Lib/gds/burp/console/console.py**文件，将 25 26 行直接改为如下代码即可：

![](http://drops.javaweb.org/uploads/images/db92eb82682a762301c17962fd57062ffcd82417.jpg)

Python 编写 Burp 插件 注意事项
----------------------

### Python 导入相关库

Python 实现接口的方式与 Python 中类的继承写法一样。只是读者要注意的是：在 Java 中，类是单继承的，一个子类直接继承的父类只能有一个，可以通过间接的方式实现多继承，但 Python 中是可以直接继承多个类。

Python 编写 Burp 插件的示例代码如下：

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
    BurpSuite插件开发指南之 Python 篇
'''

# 导入 burp 接口
from burp import IBurpExtender, IProxyListener

# 导入 Java 库
from java.net import URL

# 按照 Python 类继承的方式实现相关接口

class BurpExtender(IBurpExtender, IProxyListener):

    def registerExtenderCallbacks(self, callbacks):
        # code here
        pass

    def processProxyMessage(self, messageIsRequest, message):
        pass

```

### PermGen space 错误

在 Burp 加载 Python 编写的插件时，会经常遇到如下图所示的错误：

![](http://drops.javaweb.org/uploads/images/2a6bec5701f2447cc2dda022e79ea998762658d6.jpg)

Burp 官网也给出了解决**java.lang.OutOfMemoryError: PermGen space**错误的办法。  
在启动 Burp 时设置 JVM 的 XX 参数即可，如： java -XX:MaxPermSize=1G -jar burp.jar

不过即使是使用上述参数启动 Burp，在多次加载 Python 编写的插件后，还是会出现 Burp 卡死的现象。

Burp 加载 Python 编写的插件的方法
-----------------------

Python 编写的插件文件后缀为 py 文件，不能由 Burp 直接加载，所以在加载前需要先设置 Jython 的路径。

在 Jython 官方下载页面选择 Jython 独立 jar 包。下载好后，按照下图所示设置：

![](http://drops.javaweb.org/uploads/images/355cbad0d2959376c99f175d318c1d53dc7c1dce.jpg)

加载 Python 插件的方式如下图：

![](http://drops.javaweb.org/uploads/images/25847efe78d4d856fc64c838abfe55919e13b118.jpg)

Python 编写 Burp GUI 插件实例
-----------------------

本实例使用 Python 调用 Java 的 swing 图形控件库并绑定相关事件。最终结果如下图：

![](http://drops.javaweb.org/uploads/images/83f3ce9fef5363a48240762632b1753b6f90390b.jpg)

示例代码如下：

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
    BurpSuite插件开发指南之 Python 篇
'''

# 导入 burp 接口
from burp import IBurpExtender, ITab

# 导入 Java 库

from javax.swing import JPanel
from javax.swing import JButton

class BurpExtender(IBurpExtender, ITab):

    def registerExtenderCallbacks(self, callbacks):

        self._cb = callbacks
        self._hp = callbacks.getHelpers()

        self._cb.setExtensionName('BurpPython')
        print 'hello burp!'

        self.mainPanel = JPanel()

        # 初始化一个 JButton 并绑定单击事件
        self.testBtn = JButton('Click Me!', actionPerformed=self.testBtn_onClick)

        self.mainPanel.add(self.testBtn)

        self._cb.customizeUiComponent(self.mainPanel)
        self._cb.addSuiteTab(self)

    def testBtn_onClick(self, event):
        print 'testBtn clicked!'

    # 实现 ITab 接口的 getTabCaption() 方法
    def getTabCaption(self):
        return 'BurpPython'

    def getUiComponent(self):
        return self.mainPanel

```

相比较 Java 编写 GUI 插件，如果要实现比较复杂的 GUI，使用 Python 编写还是比较轻松的事情，不用关心太多的参数及参数类型，绑定事件也更加简单。

0x02 Python 编写 Burp 插件实例之 工具集成菜单
================================

* * *

本小节会使用一个工具集成右键菜单的 Burp 插件举例说明 Python 编写 Burp 插件的套路。

注：  
读者可以在此插件的基础上修改为任何你想要执行的命令或程序 并指定不同的参数，如：使用 请求原始数据配合 SQLMap 进行SQLi 测试。另外在使用该插件过程时，可以将输出设置为系统控制台输出，如下图所示：

![](http://drops.javaweb.org/uploads/images/65cbca61902a84cafae4d3d13f8d306fe2326151.jpg)

代码和配置文件内容如下：

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
    BurpSuite插件开发指南之 Python 篇
'''

import os
import sys
import json
import thread
import traceback

# 导入 burp 相关接口
from burp import IBurpExtender
from burp import IContextMenuFactory

# 导入 Java 相关库
from javax.swing import JMenu
from javax.swing import JMenuItem

reload(sys)
sys.setdefaultencoding('utf-8')


class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):

        self.messages = []
        self.menusConf = {}

        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()

        self.callbacks.issueAlert('toolKits is ready ...')
        self.callbacks.setExtensionName('toolKits')
        self.callbacks.registerContextMenuFactory(self)

    def loadMenus(self):
        self.menus = []
        self.mainMenu = JMenu("toolKits")
        self.menus.append(self.mainMenu)

        try:
            with open('toolKits/toolKits.conf') as fp:
                self.menusConf = json.loads(fp.read())
        except:
            self.mainMenu.add(JMenuItem(u'加载配置出错!'))
        else:
            for tool in self.menusConf:
                # 遍历配置，创建子菜单项，并添加事件绑定
                menu = JMenuItem(tool['name'],
                                 None,
                                 actionPerformed=lambda x: self.eventHandler(x))
                self.mainMenu.add(menu)

    def createMenuItems(self, invocation):

        # 将加载的过程放在 createMenuItems 接口方法中
        # 可以在不重新加载该插件的情况下，动态加载配置
        self.loadMenus()

        self.messages = invocation.getSelectedMessages()

        # 只在指定的 Burp 标签的右键菜单显示
        # ctx = invocation.getInvocationContext()
        # if not ctx in [0, 1, 2, 3, 4, 5, 6]:
        #     return None

        return self.menus if self.menus else None

    def eventHandler(self, x):
        '''
            通过获取当前点击的子菜单的 text 属性，确定当前需要执行的 command
            启动线程执行命令
        '''

        try:
            menuName = x.getSource().text
            for tool in self.menusConf:
                if tool['name'] == menuName:
                    commands = [tool['command'].replace(
                        '{#}', val) for val in self.getValue(tool['param'])]
                    [thread.start_new_thread(self.execCommand, (command,))
                     for command in commands]
        except:
            print traceback.print_exc()

    def getHost(self, message):
        return message.getHttpService().getHost()

    # 获取 Url 注意此处若通过 meesage.getRequest() 是获取不到的
    def getUrl(self, meesage):
        return str(self.helpers.analyzeRequest(meesage).getUrl())

    # 通过配置中的 参数值 分别获取不同值
    def getValue(self, paramType):
        if paramType == 'host':
            return set([self.getHost(message) for message in self.messages])
        elif paramType == 'url':
            return set([self.getUrl(message) for message in self.messages])

    # 执行命令处理方法
    def execCommand(self, command):
        try:
            print '[I] 正在执行命令: {command}, 请稍后...'.format(command=command)
            res = '---------- 命令 {command} 执行结果: ---------- {res}'.format(
                command=command, res=os.popen(command).read())
            print res
        except:
            print traceback.print_exc()

```

该插件有一个配置文件，格式为 JSON 格式（Jython 2.7.0 不支持 yaml）：

```
[{
  "name": "Nmap 扫描端口",
  "param": "host",
  "command": "nmap -T4 {#}"
},
{
  "name": "SQLMap 检查注入",
  "param": "url",
  "command": "python /opt/sqlmap/sqlmap.py -u {#} --dbs"
}]

```