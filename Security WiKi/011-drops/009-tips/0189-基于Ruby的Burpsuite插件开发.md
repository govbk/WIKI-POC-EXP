# 基于Ruby的Burpsuite插件开发

0x00 前言
=======

* * *

BurpSuite是久负盛名的web应用安全测试工具，在安全圈子中被誉为“神器”。它的核心功能是http代理，并在此基础上提供了丰富的自定义配置选项，协助使用者设计不同的方案进行渗透或者安全监测。此外，除了工具本身提供的功能以外，burpsuite神器提供了一组java编写的应用接口，通过java或基于java的Jython、Jruby，可以实现许多自定义的功能插件。在工作中，笔者尝试使用Ruby进行BurpSuite Extention的插件开发，这个过程有一些坑需要同特定的方式解决，希望能和大家分享这点经验。在这里，不针对具体业务，不讨论编程语言优劣，只希望能够丰富这个生态系统，让Burp的爱好者们多一种选择。

0x01开发环境
========

* * *

### 1 软件配置

*   Macbook pro OSX 10.10.5
*   Burpsuite free edit 1.6.03
*   Jruby 1.7.19
*   rvm 1.26.10
*   gem 2.0.14

### 2 安装

在Unix/Linux环境下安装Ruby编程语言，很可能会遇到多个版本共存的情况。RVM（Ruby Version Manager）这个小工具很好的解决了这个问题，使用这个工具可以方便的安装和管理操作系统上复杂的Ruby版本，强烈推荐新手使用。

### 2.1 安装RVM

RVM的安装步骤非常简单，通过使用curl命令下载一个脚本，同时使用‘bash -s’执行，最后重新载入profile文件即可。官方的安装说明：https://rvm.io/rvm/install

```
$ curl -sSL https://get.rvm.io|bash -s

```

正确安装后会有如下提示

```
In case of problems: http://rvm.io/help and https://twitter.com/rvm_io

  * WARNING: You have '~/.profile' file, you might want to load it,
    to do that add the following line to '/home/wang.zhaofeng/.bash_profile':

      source ~/.profile

```

此时在命令行下执行

```
$ source ~/.profile 

```

执行如下命令测试安装是否成功，如果显示版本说明，则安装成功。

```
$ rvm -v

```

### 2.2 安装Jruby

Burpsuite使用Java开发，因此无论使用python还是ruby进行插件开发，都必须有java实现的解释器（即Jython和Jruby）。

安装jruby并创建针对burpsuite的环境变量。

```
$ rvm install jruby
$ rvm --ruby-version use jruby@burp --create

```

执行‘`rvm list`’ 查看是否安装成功。

```
$ rvm list

```

当看到如下显示说明安装成功。

```
rvm rubies

=> jruby-1.7.19 [ x86_64 ]

# Default ruby not set. Try 'rvm alias create default <ruby>'.

# => - current
# =* - current && default
#  * - default

```

为了稳定和向下兼容，我使用了比较陈旧的1.7版，经测试，最新的9.x版也是没有问题的。（不知道这个版本是怎么命名的。）

### 2.3 BurpSuite插件环境配置

软件安装成功后，你可以在个人目录的.rvm/rubies/jruby-1.7.19目录下找到你的Jruby目录，在这个目录下，会有一个Jruby.jar的文件，记住它的位置。

如果不能手动找到，可以尝试执行以下命令：

```
$ rvm env|grep MY_RUBY_HOME

```

MY_RUBY_HOME将作为这个jar文件路径的环境变量名。

```
export MY_RUBY_HOME='/Users/myname/.rvm/rubies/jruby-1.7.19'

```

单引号中的路径，就是jruby.jar的存放路径。

执行以下命令

```
rvm use jruby

```

让jruby变成当前的操作环境，就可以找到对应的环境变量。

**下面是非常重要的一步!**

**下面是非常重要的一步!**

**下面是非常重要的一步!**

打开命令行，输入以下命令：

```
JRUBY_HOME=/Users/myname/.rvm/rubies/jruby-1.7.19 java -XX:MaxPermSize=1G -Xmx1g -Xms1g -jar YOUR_BURP_PATH/burpsuite_free_v1.6.xx.jar

```

通过命令行启动BurpSuite，而不是双击图标，这一步非常重要，否则在代码中require库文件，就会出现无法加载库文件的情况。

打开Burp，在Extender-->Options选项卡最下方的Ruby Environment部门导入你的Jruby.jar文件，没如果没有报错，则说说明加载成功。

![载入jruby.jar](http://drops.javaweb.org/uploads/images/cc710e80636d254de260ea125125547e187e2d8e.jpg)

### 2.4 测试

Burpsuite官方网站提供了一个测试文件（[点这里下载](https://portswigger.net/burp/extender/examples/HelloWorld.zip)）

解压缩后可以在名为ruby的目录下面看到一个HelloWorld.rb文件，这个就是要载入的插件代码。

点击Extentders标签下的Extention选项卡，在上半部分左侧点击“Add"

![添加插件](http://drops.javaweb.org/uploads/images/50552fa0ef57d339278794ba6ac3d267b4d13953.jpg)

在Extention type处选择ruby类型，点击Select file选择解压出来的helloworld.rb文件。

![添加插件2](http://drops.javaweb.org/uploads/images/825c2c9cc62e5039a2bd5e685e5012df156767a7.jpg)

![添加到插件3](http://drops.javaweb.org/uploads/images/b7bc3f205bf2f95f329957df14306d974409c5b0.jpg)

回到主页面点击Next，就会在弹出的控制台窗口中显示Hello World字符，此时全部的准备工作都已完成。

![hello output burp](http://drops.javaweb.org/uploads/images/46b4e1572b38eea59a9c13e0ac4eb5a640522c9c.jpg)

0x02 第一个Ruby扩展插件
================

* * *

在开发个人的第一个插件之前，如果有时间，看一下Burpsuite官方提供的开发者文档可以帮助开发者对接口系列的设计有更全面的认识。地址在：[https://portswigger.net/burp/extender/api/index.html](https://portswigger.net/burp/extender/api/index.html)。@Her0in在这篇文章中[http://drops.wooyun.org/tools/14040](http://drops.wooyun.org/tools/14040)对一些主要的接口做了介绍，大家可以参考。有了上面这些准备，就可以真正开始着手开发你的Burp插件了。

Burp的插件开发是有固定的模式的，为了说明这个模式，请看下面几行代码。

```
require 'java'
java_import 'burp.IBurpExtender'

class BurpExtender
  include IBurpExtender

  def registerExtenderCallbacks(callbacks)
    callbacks.setExtensionName("Your Extender Name")
  end
end

```

必须要有第一行`require 'java'`，否则后面引入java接口类会报错；代码第二行引入IBurpExtender这个Burp的java类。Burp的开发者把相关的api封装在一个类中，在调用api之前需要在代码顶部引入这个类，同时要include这个module。这段代码中，registerExtenderCallbacks这个方法封装在IBurpExtender这个类里面。事实上，IBurpExtender这个类中只封装了仅有的一个方法：registerExtenderCallbacks，它是一个程序的入口，有点类似于main()函数。

官方的接口文档对registerExtenderCallbacks方法做了这样的说明：

> “This method is invoked when the extension is loaded. It registers an instance of the IBurpExtenderCallbacks interface, providing methods that may be invoked by the extension to perform various actions.”

这个方法以“注册”的方式定义了扩展插件中可用的实例（类型）。每一个Burp插件都必然包含上面这几行代码，少了一行都不行。

现在，我们设计一个最简单的功能：在BurpSuite Extender选项卡中的Output对话框输出监听到的HTTP请求，通过这个实现这个功能来让读者体会到Burp插件开发的大概流程。

我们需要在刚才的代码上稍加变化：首先，我们使用一个名叫processHttpMessage()的方法，通过查询开发手册，我们发现这个方法封装在一个名叫IHttpListener的模块中，于是在代码开头添加一行"`java_import 'burp.IHttpListener'`"，同时在BurpExtender类中include这个叫IHttpListener的module，具体做法可见下面的示例代码（另一种写法是在"include IBurpExtender"这行下面另起一行"include IHttpListener"）。

然后在"registerExtenderCallbacks"方法中加入一行"`callbacks.registerHttpListener(self)`"，这是告诉引擎，这个插件被当做一个HTTP监听器来使用。

在burp.IHttpListener这个模块中，processHttpMessage是仅有的一个方法，我们在BurpExtender这个类中重写这个方法。官方开发手册对这个方法有如下定义：

```
void processHttpMessage(int toolFlag, boolean messageIsRequest, IHttpRequestResponse messageInfo)

```

其中toolFlag代表功能的旗标常数，每个常数代表的组件是固定的，可以在文档中查到；messageIsRequest表示HttpListener监听到的数据是否是一个请求；messageInfo是一个IHttpRequestResponse对象，它有多个实例方法，详细的使用方法可以在开发文档中找到。processHttpMessage方法通过参数把HTTP请求或响应的数据传递进来，开发者可以根据自己的需要对其进行处理。

我们使用get_request()方法获取请求对象（getRequest是这个方法的别名）。此时Http包的数据是不能直接输出的，在调试的过程中，笔者对这个对象使用了methods方法获取它的所有实例方法，最后使用了to_s方法对数据的内容直接输出（需要注意的是，不同版本的jruby的to_s操作可能会有所不同）。这么做的原因是，get_request()获取到的数据对象不是文本，而是一个hash的子类，通过to_s方法把对象转换成String输出。

代码部分：

```
require 'java'
java_import 'burp.IBurpExtender'
java_import 'burp.IHttpListener'


class BurpExtender

  include IBurpExtender,IHttpListener

  def registerExtenderCallbacks(callbacks)
    @callbacks = callbacks
    @stdout    = java.io.PrintWriter.new(callbacks.getStdout(), true)

    callbacks.setExtensionName("Your Extender Name")
    callbacks.registerHttpListener(self)

  end

  def processHttpMessage(toolFlag, messageIsRequest, messageInfo)
    if messageIsRequest
      @stdout.println(messageInfo.get_request().to_s)
    end

  end

end

```

将上述代码保存为一个ruby文件以后载入到BurpExtender中，在命令行中使用如下命令进行测试

```
curl -x 127.0.0.1:8009 http://www.xxx.com -I

```

效果如图所示：

![test output](http://drops.javaweb.org/uploads/images/8fa73de088b587bc2d95184f678746465101add9.jpg)

0x03 创建一个HttpMessageEditorTab实例
===============================

* * *

在HTTP History或者Repeater标签下的每一组请求响应中都有若干个Tab界面，分别叫做Raw、Headers、Hex（在响应部分还有HTML和Render），这样的每一个Tab都都被称作一个Http Message Editor Tab，我们可以根据自己的需要自定义一组新的Tab，并设计每一个Tab的功能。

如前所述，我们构建新的Tab需要引入burp.IMessageEditorTab和burp.IMessageEditorTabFactory这两个java类，所以首先在代码的开始部分使用java_import引入这两个类。

```
require 'java'

java_import 'burp.IBurpExtender'
java_import 'burp.IMessageEditorTab'
java_import 'burp.IMessageEditorTabFactory'

```

在registerExtenderCallbacks方法的定义中将这个插件注册成为一个MessageEditorTabFactory，即添加一行：`callbacks.registerMessageEditorTabFactory(self)`。然后定义createNewInstance方法，根据[开发文档的定义](https://portswigger.net/burp/extender/api/burp/IMessageEditorTabFactory.html)，这个方法需要返回一个实例化后的IMessageEditorTab对象。于是我们在这里初始化了一个叫MakeTabs的类，后面我们只需要按照接口规范重新定义这个类即可。

```
class BurpExtender
  include IBurpExtender, IMessageEditorTab, IMessageEditorTabFactory

  def   registerExtenderCallbacks(callbacks)

    @callbacks = callbacks

    callbacks.setExtensionName("MessageEditorTab")

    @stdout = java.io.PrintWriter.new(callbacks.getStdout(), true)

    callbacks.registerHttpListener(self)
    callbacks.registerMessageEditorTabFactory(self)
  end

  def createNewInstance(controller, editable)
    MakeTabs.new(@callbacks, editable)
  end
end

```

下面，我们需要按照[IMessageEditorTab的接口规范](https://portswigger.net/burp/extender/api/burp/IMessageEditorTab.html)定义，逐个定义这个类中所有的七个方法（不含initailize方法）。至于这个Tab要实现什么样的功能，我们借鉴[burpsuite扩展开发之Python](http://drops.wooyun.org/tools/5751)中的例子，让它显示格式化后的json字符串，通过这个非常简单的例子让读者明白代码的逻辑。实际上，依托ruby编程语言本身的能力和BurpExtender丰富的接口，可以延伸出丰富的功能扩展。

initialize方法，这里根据需要传入callback和editable两个参数。`@stderr`和`@stdout`两个类变量是用于调试的错误输出和标准输出。`@helper`是一个辅助模块的对象，接触它可以完成对http数据的分析。`@txt_input`控制文本的显示。`@editable`是一个布尔值。`@callbacks`是IBurpExtenderCallbacks对象。

getTabCaption方法返回的文本（String类型）就是Tab显示的名称。

getUiComponent方法返回java.awt.Component对象，它通过@txt_input.get_component()获得。

isEnabled方法返回一个布尔值，可以根据条件判断当前Tab是否显示。

setMessage返回void类型，当isEnable返回true时，可以通过在这个方法中操作`@txt_input`对象控制窗体的输出内容。假设这里的response是一段Json数据，那么我们通过ruby json库的方法将其格式化输出并丢弃响应头，当数据流是request的时候不显示窗体。另外，因为要用到ruby内建的json库，所以需要在"require 'java"下面加上一行"require 'json'"。

getMessage返回byte类型，意为当前显示的文本，可以通过`@txt_input.getText()`对象获得。

isModifed返回一个布尔值，它的作用是判断当前的文本内容是否被改变过。

getSelectedData返回byte类型，它通过`@txt_input.getSelectedText()`获得。

完整的代码：

```
require 'java'
require 'json'

java_import 'burp.IBurpExtender'
java_import 'burp.IMessageEditorTab'
java_import 'burp.IMessageEditorTabFactory'

class BurpExtender
  include IBurpExtender, IMessageEditorTabFactory

  def   registerExtenderCallbacks(callbacks)

    @callbacks = callbacks

    callbacks.setExtensionName("JsonFormater")

    @stdout = java.io.PrintWriter.new(callbacks.getStdout(), true)


    callbacks.registerMessageEditorTabFactory(self)
  end

  def createNewInstance(controller, editable)
    MakeTabs.new(@callbacks, editable)
  end
end

class MakeTabs
  include IMessageEditorTab

  def initialize(callbacks, editable)
    @stderr = callbacks.get_stderr()
    @helper = callbacks.get_helpers()
    @txt_input = callbacks.create_text_editor()
    @editable = editable
    @stdout = java.io.PrintWriter.new(callbacks.getStdout(), true)
    @callbacks = callbacks
  end

  def getTabCaption
    "MyTab"
  end

  def getUiComponent
    @txt_input.get_component()

  end

  def isEnabled(content, isRequest)
    not isRequest
  end

  def setMessage(content, isRequest)
    unless isRequest
      @txt_input.text = "HTTP Reponse is nil or empty.".to_java_bytes  if content.nil? or content.empty?
      lines= content.to_s.split("\n")
      body = ""
      lines.each_with_index{|each,index|  body = each if each.chomp =~ /^\{.*\}$/  }
      if body.size > 0
        body   = body.chomp
        begin
          hash = JSON.parse body
          body = JSON.pretty_generate hash
        rescue
          @stderr.write(" error: #{$!} at#{$@}\n".to_java_bytes)
        end
        @txt_input.text = body.to_java_bytes
      end
    end
    true
  end

  def getMessage
    return @txt_input.getText
  end

  def isModifed
    return @txt_input.text_modified?
  end

end

```

将上述代码保存至一个ruby文件中并在BurpExtender选项卡中载入，就可以看到如下效果：

![正常的响应json数据](http://drops.javaweb.org/uploads/images/1cbde3d4f4a0bd4cbac620433799bd0d968d1435.jpg)

![格式化后的json数据](http://drops.javaweb.org/uploads/images/5a6761c0d4f74fca15bca71f897b1614f854e7cb.jpg)

0x04 总结
=======

* * *

具备一定ruby编程基础的小伙伴看懂上面的这两段代码并不是难事，实际上笔者最初的想法是把自己在工作中写的一个工具作为案例来分享，但最终放弃了这个想法。原因是考虑到这个工具跟工作的场景结合比较紧密，通用性不强所以不便于移植，另一方面这个工具代码量比较大，结构也较本文中讲解的代码复杂一些，如果要详细讲解清楚可能要占用大量篇幅，反而可能把重要的信息淹没。

从我个人折腾Extender的经验来看，代码的编码是一项基本功，而最初上手开始编写插件的时候，一些针对BurpSuite扩展功能的基本操作可能成为一个瓶颈——我甚至认为，这篇文章最重点的内容并不是后面的代码，而是第一节环境配置，因为笔者花费在从坑里爬出来的时间甚至比写代码的时间还要久。所以这里分享的内容并没有太大难度，仅仅是我认为可能会阻挡很多入门选手的门槛。当然这里也只是介绍了BurpExtender使用技巧的一小部分，更多高级的用法需要在时间中慢慢积累经验。

大家有什么问题欢迎一起交流探讨。