# 一条Python命令引发的漏洞思

0x00 起因

* * *

近日，在测试某个项目时，无意中发现在客户机的机器上可以直接运行一条[Python](https://www.2cto.com/kf/web/Python/)命令来执行服务器端的Python脚本，故而，深入测试一下便有了下文。

0x01 分析

* * *

很多时候，因为业务的需要我们常常需要使用Python –c exec方法在客户机上来执行远程服务器上的Python脚本或者命令。

那么，在这种情况下，因为在命令是运行在客户机上，这就必然导致了远程服务器上的Python脚本会以一定的形式运行在客户机的内存中，如果我们可以获取并还原出这些代码，这也在一定程度上造成了服务器[源码](https://www.2cto.com/ym/)的泄露。

为了验证这种泄露风险，下面是我依据一个真实案例而创建了一个简单的演示Demo：

首先在服务器上创建了一个Python脚本pyOrign.py来模拟服务上的业务代码然后利用compile方法将pyOrign.py编译成exec模式的code object对象并利用marshal.dump方法进行序列化存入一个二进制文件pyCode，将其保存在服务器上供客户端远程调用接着在服务器上创建了测试脚本test.py，用来调用和反序列化服务器端二进制文件pyCode为exec方法可执行的code object对象

PyOrign.py 文件：

`#!python#!/usr/bin/env python   import randomimport base64   class Test:    x=''    y=''def __init__(self, a, b):self.x = aself.y = bprint "Initiation..., I'm from module Test"def add(self):print 'a =',self.xprint 'b =',self.y        c = self.x+self.yprint 'sum =', cif __name__ == '__main__':print "\n[+] I'm the second .py script!"    a = Test(1,2)a.add()`

test.py文件：

`#!python#!/usr/bin/env pythonimport imp  ifimp.get_magic() != '\x03\xf3\r\n':print "Please update to Python 2.7.10 (http://www.python.org/download/)"exit()  importurllib, marshal, zlib, time, re, sysprint "[+] Hello, I'm the first .py script!"_S = "http"_B = "10.66.110.151"execmarshal.loads(urllib.urlopen('%s://%s/mystatic/pyCode' % (_S, _B)).read())`

接下来我们开始演示效果，首先在客户端执行以下命令：

`#!bashpython -c "exec(__import__('urllib2').urlopen('http://10.66.110.151/test/').read())" `

运行后的结果显示如下：

![p1](http://www.2cto.com/uploadfile/Collfiles/20151217/20151217100950153.png)

简单分析一下这个过程，我们不难发现上面的命令在被执行后实际上发生的过程是这样的：

首先利用urllib2的urlopen方法来读取远程服务器上的命令代码

![p2](http://www.2cto.com/uploadfile/Collfiles/20151217/20151217100950154.png)

然后判断客户机上的python的版本是不是2.7.10，如果是，则执行下面的代码继续获取远程服务器上的可执行代码： exec marshal.loads(urllib.urlopen('http://10.66.110.151/mystatic/pyCode').read())

接着，又利用urllib的urlopen方法读取远程服务器上的可执行代码：

![p3](http://www.2cto.com/uploadfile/Collfiles/20151217/20151217100950156.png)

最后exec方法在客户机上执行marshal.loads方法反序列化后的code object对象

细心的朋友可能已经发现，在步骤3我们并没有像步骤1那样获取到exec执行的源码而是一个codeobject对象。那么我们不禁要思考一下，有没有办法将这个code object对象还原成真正的Python源码呢？如果可以，是不是也就意味着服务器上的源码存在这很大的泄露风险呢？

我们知道exec语句用来执行储存在字符串或文件中的Python语句，这既可以Python语句也可以是经过compile编译后的exec模式的code object对象。那么此处，不禁要思考获取到的code object是不是就是服务器上的Python脚本经过compile编译后的exec模式的code object对象呢？如果是的，那么只要我们能够构造出这个原始脚本编译后的pyc文件，也就意味着我们可以通过pyc文件来进一步还原出脚本的原始py文件。

接下来我们就来看看如何利用已知的codeobject对象来构造一个编译后的pyc文件。

首先，我们来分析一下pyc文件的构成。一个完整的pyc文件是由以下几部分组成：

四字节的Magic int（魔数），表示pyc版本信息四字节的int，是pyc产生时间，若与py文件时间不同会重新生成序列化了的PyCodeObject对象。

那么，我们是否已经具备这几部分。首先是四字节的魔数Magic int, 返回到上面分析过程中的步骤1，我们看到了下面一段代码：

`#!pythonimport impifimp.get_magic() != '\x03\xf3\r\n':print "Please update to Python 2.7.10 (http://www.python.org/download/)"exit()`

此处代码就是通过Magic int来判断客户主机上的Python版本信息，那么不用说这里的Magic int也就是imp.get_magic()获取到的值。

接下来是四字节的pyc的时间戳，经过我的测试发现此处的时间戳可以是任意符合格式的四字节int。

最后是序列化了的PyCodeObject对象，那么这个我们也有吗？没错，我们在步骤3中读取到的codeobject对象就是这个PyCodeObject对象。

既然构造pyc所具有的三个组成部分我们都有了，我们就来尝试构造一下这个pyc文件吧。按照猜测，远程服务器应该是通过compile方法来编译原始的脚本文件，那么我们就利用同样的方法来构造它。

这里我们利用了库文件py_compile的compile方法，其具体代码实现如下：

`#!python"""Routine to "compile" a .py file to a .pyc (or .pyo) file.This module has intimate knowledge of the format of .pyc files."""import __builtin__import impimport marshalimportosimport sysimporttracebackMAGIC = imp.get_magic()__all__ = ["compile", "main", "PyCompileError"]classPyCompileError(Exception):    """Exception raised when an error occurs while attempting tocompile the file.    To raise this exception, useraisePyCompileError(exc_type,exc_value,file[,msg])whereexc_type:   exception type to be used in error messagetype name can be accesses as class variable                    'exc_type_name'exc_value:  exception value to be used in error messagecan be accesses as class variable 'exc_value'file:       name of file being compiled to be used in error messagecan be accesses as class variable 'file'msg:        string message to be written as error message                    If no value is given, a default exception message will be given,consistent with 'standard' py_compile output.message (or default) can be accesses as class variable 'msg'    """def __init__(self, exc_type, exc_value, file, msg=''):exc_type_name = exc_type.__name__ifexc_type is SyntaxError:tbtext = ''.join(traceback.format_exception_only(exc_type, exc_value))errmsg = tbtext.replace('File ""', 'File "%s"' % file)else:errmsg = "Sorry: %s: %s" % (exc_type_name,exc_value)        Exception.__init__(self,msg or errmsg,exc_type_name,exc_value,file)self.exc_type_name = exc_type_nameself.exc_value = exc_valueself.file = file        self.msg = msg or errmsgdef __str__(self):return self.msgdefwr_long(f, x):    """Internal; write a 32-bit int to a file in little-endian order."""f.write(chr( x        & 0xff))f.write(chr((x >> 8)  & 0xff))f.write(chr((x >> 16) & 0xff))f.write(chr((x >> 24) & 0xff))def compile(file, cfile=None, dfile=None, doraise=False):    """Byte-compile one Python source file to Python bytecode.    Arguments:file:    source filenamecfile:   target filename; defaults to source with 'c' or 'o' appended             ('c' normally, 'o' in optimizing mode, giving .pyc or .pyo)dfile:   purported filename; defaults to source (this is the filenamethat will show up in error messages)doraise: flag indicating whether or not an exception should beraised when a compile error is found. If an exceptionoccurs and this flag is set to False, a stringindicating the nature of the exception will be printed,and the function will return to the caller. If anexception occurs and this flag is set to True, aPyCompileError exception will be raised.    Note that it isn't necessary to byte-compile Python modules forexecution efficiency -- Python itself byte-compiles a module whenit is loaded, and if it can, writes out the bytecode to thecorresponding .pyc (or .pyo) file.    However, if a Python installation is shared between users, it is agood idea to byte-compile all modules upon installation, sinceother users may not be able to write in the source directories,and thus they won't be able to write the .pyc/.pyo file, and thenthey would be byte-compiling every module each time it is loaded.    This can slow down program start-up considerably.    See compileall.py for a script/module that uses this module tobyte-compile all installed files (or all files in selecteddirectories).    """with open(file, 'U') as f:try:timestamp = long(os.fstat(f.fileno()).st_mtime)exceptAttributeError:timestamp = long(os.stat(file).st_mtime)codestring = f.read()try:codeobject = __builtin__.compile(codestring, dfile or file,'exec')exceptException,err:py_exc = PyCompileError(err.__class__, err, dfile or file)ifdoraise:raisepy_excelse:sys.stderr.write(py_exc.msg + '\n')returnifcfile is None:cfile = file + (__debug__ and 'c' or 'o')with open(cfile, 'wb') as fc:fc.write('\0\0\0\0')wr_long(fc, timestamp)marshal.dump(codeobject, fc)fc.flush()fc.seek(0, 0)fc.write(MAGIC)def main(args=None):    """Compile several source files.    The files named in 'args' (or on the command line, if 'args' isnot specified) are compiled and the resulting bytecode is cachedin the normal manner.  This function does not search a directorystructure to locate source files; it only compiles files namedexplicitly.  If '-' is the only parameter in args, the list offiles is taken from standard input.    """ifargs is None:args = sys.argv[1:]rv = 0ifargs == ['-']:while True:filename = sys.stdin.readline()if not filename:breakfilename = filename.rstrip('\n')try:compile(filename, doraise=True)exceptPyCompileError as error:rv = 1sys.stderr.write("%s\n" % error.msg)exceptIOError as error:rv = 1sys.stderr.write("%s\n" % error)else:for filename in args:try:compile(filename, doraise=True)exceptPyCompileError as error:                # return value to indicate at least one failurerv = 1sys.stderr.write(error.msg)returnrvif __name__ == "__main__":sys.exit(main())`

在上面的代码中，我们可以看出，compile方法首先利用imp.get_magic()生成Magic int：

`#!pythonMAGIC = imp.get_magic()`

然后根据py文件的创建时间来生成时间戳：

`#!pythontimestamp = long(os.fstat(f.fileno()).st_mtime`

最后利用__builtin__.compile方法生成exec模式的code object对象，并使用marshal.dump方法将codeobject写入到pyc文件中

`#!pythoncodeobject = __builtin__.compile(codestring, dfile or file,'exec')`

知道了原理，接下来我们可以利用下面的脚本来构造pyc文件：

`#!python"""Routine to "compile" a .py file to a .pyc (or .pyo) file.This module has intimate knowledge of the format of .pyc files."""import __builtin__import impimport marshalimportosimport sysimporttracebackimportzlibimporturllibMAGIC = imp.get_magic()  #根据Python版本信息生成的魔数__all__ = ["compile", "main", "PyCompileError"]classPyCompileError(Exception):    """Exception raised when an error occurs while attempting tocompile the file.    To raise this exception, useraisePyCompileError(exc_type,exc_value,file[,msg])whereexc_type:   exception type to be used in error messagetype name can be accesses as class variable                    'exc_type_name'exc_value:  exception value to be used in error messagecan be accesses as class variable 'exc_value'file:       name of file being compiled to be used in error messagecan be accesses as class variable 'file'msg:        string message to be written as error message                    If no value is given, a default exception message will be given,consistent with 'standard' py_compile output.message (or default) can be accesses as class variable 'msg'    """def __init__(self, exc_type, exc_value, file, msg=''):exc_type_name = exc_type.__name__ifexc_type is SyntaxError:tbtext = ''.join(traceback.format_exception_only(exc_type, exc_value))errmsg = tbtext.replace('File ""', 'File "%s"' % file)else:errmsg = "Sorry: %s: %s" % (exc_type_name,exc_value)        Exception.__init__(self,msg or errmsg,exc_type_name,exc_value,file)self.exc_type_name = exc_type_nameself.exc_value = exc_valueself.file = file        self.msg = msg or errmsgdef __str__(self):return self.msgdefwr_long(f, x):    """Internal; write a 32-bit int to a file in little-endian order."""f.write(chr( x        & 0xff))f.write(chr((x >> 8)  & 0xff))f.write(chr((x >> 16) & 0xff))f.write(chr((x >> 24) & 0xff))def compile(file, cfile=None, dfile=None, doraise=False):    """Byte-compile one Python source file to Python bytecode.    Arguments:file:    source filenamecfile:   target filename; defaults to source with 'c' or 'o' appended             ('c' normally, 'o' in optimizing mode, giving .pyc or .pyo)dfile:   purported filename; defaults to source (this is the filenamethat will show up in error messages)doraise: flag indicating whether or not an exception should beraised when a compile error is found. If an exceptionoccurs and this flag is set to False, a stringindicating the nature of the exception will be printed,and the function will return to the caller. If anexception occurs and this flag is set to True, aPyCompileError exception will be raised.    Note that it isn't necessary to byte-compile Python modules forexecution efficiency -- Python itself byte-compiles a module whenit is loaded, and if it can, writes out the bytecode to thecorresponding .pyc (or .pyo) file.    However, if a Python installation is shared between users, it is agood idea to byte-compile all modules upon installation, sinceother users may not be able to write in the source directories,and thus they won't be able to write the .pyc/.pyo file, and thenthey would be byte-compiling every module each time it is loaded.    This can slow down program start-up considerably.    See compileall.py for a script/module that uses this module tobyte-compile all installed files (or all files in selecteddirectories).    """timestamp = long(1449234682)  #可以是随机生成的时间戳try:codeobject = marshal.loads(urllib.urlopen('http://10.66.110.151/mystatic/pyCode').read())    # 反序列化获取远程服务器上的code object对象exceptException,err:py_exc = PyCompileError(err.__class__, err, dfile or file)ifdoraise:raisepy_excelse:sys.stderr.write(py_exc.msg + '\n')returnifcfile is None:cfile = file + (__debug__ and 'c' or 'o')with open(cfile, 'wb') as fc:fc.write('\0\0\0\0')wr_long(fc, timestamp)marshal.dump(codeobject, fc)  # 将序列化后的code object对象写入到pyc文件fc.flush()fc.seek(0, 0)fc.write(MAGIC)def main(args=None):    """Compile several source files.    The files named in 'args' (or on the command line, if 'args' isnot specified) are compiled and the resulting bytecode is cachedin the normal manner.  This function does not search a directorystructure to locate source files; it only compiles files namedexplicitly.  If '-' is the only parameter in args, the list offiles is taken from standard input.    """ifargs is None:args = sys.argv[1:]rv = 0ifargs == ['-']:while True:filename = sys.stdin.readline()if not filename:breakfilename = filename.rstrip('\n')try:compile(filename, doraise=True)exceptPyCompileError as error:rv = 1sys.stderr.write("%s\n" % error.msg)exceptIOError as error:rv = 1sys.stderr.write("%s\n" % error)else:for filename in args:try:compile(filename, doraise=True)exceptPyCompileError as error:                # return value to indicate at least one failurerv = 1sys.stderr.write(error.msg)returnrvif __name__ == "__main__":compile('pyOrigin.py')`

保存脚本为pyOrigin_compile.py在Python 2.7.10下运行即可构造出pyOrigin.pyc文件：

![p4](http://www.2cto.com/uploadfile/Collfiles/20151217/20151217100950157.png)

然后利用uncompyle2，即可将pyOrigin.pyc还原成pyOrigin.py。至此，我们成功地还原了原始的Python脚本。

![p5](http://www.2cto.com/uploadfile/Collfiles/20151217/20151217100950158.png)

![p6](http://www.2cto.com/uploadfile/Collfiles/20151217/20151217100950160.png)

0x03 小结

* * *

分析思路：

根据Python –c exec命令获取到被执行的编译后的code object对象猜测其为compile方法编译后的可被exec执行的code object对象分析py_compile的compile方法编译py文件为pyc文件的原理并根据获取到的code object对象构造pyc文件利用uncompyle2还原pyc文件为py文件，最后获取被执行的Python源码

主要潜在危害在于可造成远程服务器Python源码泄露。