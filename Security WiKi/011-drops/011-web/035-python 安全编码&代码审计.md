# python 安全编码&代码审计

0x00 前言
=======

* * *

现在一般的web开发框架安全已经做的挺好的了，比如大家常用的django，但是一些不规范的开发方式还是会导致一些常用的安全问题，下面就针对这些常用问题做一些总结。代码审计准备部分见《php代码审计》，这篇文档主要讲述各种常用错误场景，基本上都是咱们自己的开发人员犯的错误，敏感信息已经去除。

0x01 XSS
========

* * *

未对输入和输出做过滤，场景：

```
def xss_test(request):
    name = request.GET['name']
    return HttpResponse('hello %s' %(name))

```

在代码中一搜，发现有大量地方使用，比较正确的使用方式如下：

```
def xss_test(request):
    name = request.GET['name']
    #return HttpResponse('hello %s' %(name))
    return render_to_response('hello.html', {'name':name})

```

更好的就是对输入做限制，比如说一个正则范围，输出使用正确的api或者做好过滤。

0x02 CSRF
=========

* * *

对系统中一些重要的操作要做CSRF防护，比如登录，关机，扫描等。django 提供CSRF中间件`django.middleware.csrf.CsrfViewMiddleware`,写入到settings.py的中间件即可。另外再在函数前加上@csrf_exempt修饰器。

0x03 命令注入
=========

* * *

审计代码过程中发现了一些编写代码的不好的习惯，体现最严重的就是在命令注入方面，本来python自身的一些函数库就能完成的功能，偏偏要调用`os.system`来通过shell 命令执行来完成，老实说最烦这种写代码的啦。下面举个简单的例子：

```
 def myserve(request, filename, dirname):
    re = serve(request=request,path=filename,document_root=dirname,show_indexes=True)
    filestr='authExport.dat' 
    re['Content-Disposition'] = 'attachment; filename="' + urlquote(filestr) +'"'fullname=os.path.join(dirname,filename)
    os.system('sudo rm -f %s'%fullname)
    return re

```

很显然这段代码是存在问题的，因为`fullname`是用户可控的。正确的做法是不使用`os.system`接口，改成python自有的库函数，这样就能避免命令注入。python的三种删除文件方式：

```
（1）shutil.rmtree 删除一个文件夹及所有文件  
（2）os.rmdir 删除一个空目录  
（3）os.remove，unlink 删除一个文件

```

使用了上述接口之后还得注意不能穿越目录，不然整个系统都有可能被删除了。常见的存在命令执行风险的函数如下：

```
os.system,os.popen,os.spaw*,os.exec*,os.open,os.popen*,commands.call,commands.getoutput,Popen*

```

推荐使用subprocess模块，同时确保shell=True未设置，否则也是存在注入风险的。

0x04 sql注入
==========

* * *

如果是使用django的api去操作数据库就应该不会有sql注入了，但是因为一些其他原因使用了拼接sql，就会有sql注入风险。下面贴一个有注入风险的例子：

```
def getUsers(user_id=None):
    conn = psycopg2.connect("dbname='××' user='××' host='' password=''")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if user_id==None:
        str = 'select distinct * from auth_user'
    else:
        str='select distinct * from auth_user where id=%d'%user_id
    res = cur.execute(str)
    res = cur.fetchall()
    conn.close()
    return res

```

像这种sql拼接就有sql注入问题，正常情况下应该使用django的数据库api，如果实在有这方面的需求，可以按照如下方式写：

```
def user_contacts(request):
  user = request.GET['username']
  sql = "SELECT * FROM user_contacts WHERE username = %s"
  cursor = connection.cursor()
  cursor.execute(sql, [user])
# do something with the results
  results = cursor.fetchone()   #or  results = cursor.fetchall()
  cursor.close()

```

直接拼接的是万万不可的，如果采用`ModelInstance.objects.raw(sql,[])`,或者`connection.objects.execute(sql,[])`,通过列表传进去的参数是没有注入风险的，因为django会有处理。

0x05 代码执行
=========

* * *

一般是由于eval和pickle.loads的滥用造成的，特别是eval，大家都没有意识到这方面的问题。下面举个代码中的例子：

```
@login_required
@permission_required("accounts.newTask_assess")
def targetLogin(request):
    req = simplejson.loads(request.POST['loginarray'])
    req=unicode(req).encode("utf-8")
    loginarray=eval(req)
    ip=_e(request,'ipList')
    #targets=base64.b64decode(targets)
    (iplist1,iplist2)=getIPTwoList(ip)
    iplist1=list(set(iplist1))
    iplist2=list(set(iplist2))
    loginlist=[]
    delobjs=[]
    holdobjs=[]

```

这一段代码就是就是因为eval的参数不可控，导致任意代码执行，正确的做法就是literal.eval接口。再取个pickle.loads的例子：

```
>>> import cPickle
>>> cPickle.loads("cos\nsystem\n(S'uname -a'\ntR.")
Linux RCM-RSAS-V6-Dev 3.9.0-aurora #4 SMP PREEMPT Fri Jun 7 14:50:52 CST 2013 i686 Intel(R) Core(TM) i7-2600 CPU @ 3.40GHz GenuineIntel GNU/Linux
0

```

0x06 文件操作
=========

* * *

文件操作主要包含任意文件下载，删除，写入，覆盖等，如果能达到写入的目的时基本上就能写一个webshell了。下面举个任意文件下载的例子：

```
@login_required
@permission_required("accounts.newTask_assess")
def exportLoginCheck(request,filename):
    if re.match(r“*.lic”，filename):
        fullname = filename
    else:
        fullname = "/tmp/test.lic"
    print fullname
    return HttpResponse(fullname)

```

这段代码就存在着任意.lic文件下载的问题，没有做好限制目录穿越，同理

0x07 文件上传
=========

* * *

1 任意文件上传
--------

这里主要是未限制文件大小，可能导致ddos，未限制文件后缀，导致任意文件上传，未给文件重命名，可能导致目录穿越，文件覆盖等问题。

2 xml，excel等上传
--------------

在我们的产品中经常用到xml来保存一些配置文件，同时也支持xml文件的导出导入，这样在libxml2.9以下就可能导致xxe漏洞。就拿lxml来说吧：

```
root@kali:~/python# cat test.xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xdsec [ <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>
    <node id="11" name="bb" net="192.168.0.2-192.168.0.37" ltd="" gid="" />test&xxe;</root>

>>> from lxml import etree
>>> tree1 = etree.parse('test.xml')
>>> print etree.tostring(tree1.getroot())
<root>
    <node id="11" name="bb" net="192.168.0.2-192.168.0.37" ltd="" gid=""/>testroot:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
bin:x:2:2:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/sh
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/bin/sh
man:x:6:12:man:/var/cache/man:/bin/sh

```

这是因为在lxml中默认采用的XMLParser导致的：

```
class XMLParser(_FeedParser)
|  XMLParser(self, encoding=None, attribute_defaults=False, dtd_validation=False, load_dtd=False, no_network=True, ns_clean=False, recover=False, XMLSchema schema=None, remove_blank_text=False, resolve_entities=True, remove_comments=False, remove_pis=False, strip_cdata=True, target=None, compact=True)

```

关注其中两个关键参数，其中`resolve_entities=True,no_network=True,`其中`resolve_entities=True`会导致解析实体，`no_network`会为True就导致了该利用条件比较有效，会导致一些ssrf问题，不能将数据带出。在python中`xml.dom.minidom,xml.etree.ElementTree`不受影响

0x08 不安全的封装
===========

* * *

1 eval 封装不彻底
------------

仅仅是将`__builtings__`置为空，如下方式即可绕过

```
>>> s2="""
... [x for x in ().__class__.__bases__[0].__subclasses__()
...    if x.__name__ == "zipimporter"][0](
...      "/home/liaoxinxi/eval_test/configobj-4.4.0-py2.5.egg").load_module(
...      "configobj").os.system("uname")
... """
>>> eval(s2,{'__builtins__':{}})
Linux
0

```

2 执行命令接口封装不彻底
-------------

在底层封装函数没有过滤shell元字符，仅仅是限定一些命令，但是其参数未做控制.

0x0a 总结
=======

* * *

一切输入都是不可靠的，做好严格过滤。