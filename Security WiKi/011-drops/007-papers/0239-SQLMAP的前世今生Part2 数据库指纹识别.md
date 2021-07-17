# SQLMAP的前世今生Part2 数据库指纹识别

0x00 前言
=======

* * *

谈到SQL注入，那麽第一时间就会想到神器SQLMAP，SQLMap是一款用来检测与利用的SQL注入开源工具。那麽SQLMap在扫描SQL的逻辑到底是怎样实现的呢，接下来就探讨下SQLMap的扫描逻辑，通过了解SQLMap的扫描逻辑打造一款属于自己的SQL扫描工具。

0x01 SQLMAP的准备工作
================

* * *

SQLMAP在进行扫描之前会有一些其他的功能去确定当前的目标的一些有用的信息，如防火墙的检测，当检测到有防火墙之后，进行SQL检测时的判断依据也会有所调整，如bool类型的盲注的时候，而其中heuristicCheckSqlInjection这一函数既会影响到接下来所要使用什么样的Payload进行测试，heuristicCheckSqlInjection翻译过来的意思是启发式SQL注入测试，那麽到底什么是启发式，具体作用到底是什么呢，在我们经常使用SQLMAP的时候，有可能会出现以下的提示。

![p1](http://drops.javaweb.org/uploads/images/6498e8ad6d0165ce2c76937dbc652b5fe7baf1d3.jpg)

上面提示我们当前的目标数据库版本好像是Oracle，而这上面的提示的依据就是根据这一个启发式SQL注入测试也就是本文要介绍的heuristicCheckSqlInjection来决定的。SQLMAP中有许多的Payload，足以有几百条，那麽如果全部Payload都测试一遍的话，无疑是一件很浪费时间的事情，除非Payload中的risk，clause，where字段中加以过滤，还会以这一个根据数据库的指纹来选择所要测试的Payload。

heuristicCheckSqlInjection的主要作用可以分为以下几点:

1.  **数据库版本的识别。**
2.  **绝对路径获取。**
3.  **XSS的测试**

0x02 数据库版本的识别
=============

* * *

```
# Alphabet used for heuristic checks
HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')
...
randStr = ""
while '\'' not in randStr:
    randStr = randomStr(length=10, alphabet=HEURISTIC_CHECK_ALPHABET)
kb.heuristicMode = True
payload = "%s%s%s" % (prefix, randStr, suffix)
payload = agent.payload(place, parameter, newValue=payload)
page, _ = Request.queryPage(payload, place, content=True, raise404=False)
...

```

首先会从HEURISTIC_CHECK_ALPHABET中随机抽取10个字符出现构造Payload，当然里面的都不是些普通的字符，而且些特殊字符，当我们进行SQL注入测试的时候会很习惯的在参数后面加个分号啊什么的，又或者是其他一些特殊的字符，出现运气好的话有可能会暴出数据的相关错误信息，而那个时候我们就可以根据所暴出的相关错误信息去猜测当前目标的数据库是什么。

实际找个网站测试，打下码，保护下。

```
http://***.***.***/datalist/default.aspx/article?category_id=1051

```

那麽经过`while '\'' not in randStr:`后生成了随机的字符，然后就是发包检测返回的数据了。

如下图：

![p2](http://drops.javaweb.org/uploads/images/19aca0efaf8a8f464a6866ef1b3a0c8505fc1251.jpg)

其实熟悉SQL注入的人也知道这是一个Oracle的一个错误信息，那麽接下来看看SQLMAP到底是怎样去判断的。

位于`./lib/request/connect.py`中的getPage函数,大约在598行。

```
def getPage(**kwargs):
    ...
    processResponse(page, responseHeaders)
    ...

```

其中processResponse会调用到`./lib/parse/html.py`中的`htmlParser`函数，这一个函数就是根据不同的数据库指纹去识别当前的数据库究竟是什么。

```
def htmlParser(page):
    """
    This function calls a class that parses the input HTML page to
    fingerprint the back-end database management system
    """
    xmlfile = paths.ERRORS_XML
    handler = HTMLHandler(page)
    parseXmlFile(xmlfile, handler)
    if handler.dbms and handler.dbms not in kb.htmlFp:
        kb.lastParserStatus = handler.dbms
        kb.htmlFp.append(handler.dbms)
    else:
        kb.lastParserStatus = None
    # generic SQL warning/error messages
    if re.search(r"SQL (warning|error|syntax)", page, re.I):
        handler._markAsErrorPage()
    return handler.dbms

```

最终实现的的其实是`HTMLHandler`这个类，而`paths.ERRORS_XML`这一变量的就是SQLMAP用来识别的指纹配置文件路径，位置在于`./xml/errors.xml`中。

```
<!-- Oracle -->
<dbms value="Oracle">
    <error regexp="\bORA-[0-9][0-9][0-9][0-9]"/>
    <error regexp="Oracle error"/>
    <error regexp="Oracle.*Driver"/>
    <error regexp="Warning.*\Woci_.*"/>
    <error regexp="Warning.*\Wora_.*"/>
</dbms>

```

这一配置文件的比较简单，其实也就是一些对应数据库的正则。SQLMAP在解析errors.xml的时候，然后根据regexp中的正则去匹配当前的页面信息然后去确定当前的数据库。

```
class HTMLHandler(ContentHandler):
    """
    This class defines methods to parse the input HTML page to
    fingerprint the back-end database management system
    """
    def __init__(self, page):
        ContentHandler.__init__(self)
        self._dbms = None
        self._page = page
        self.dbms = None
    def _markAsErrorPage(self):
        threadData = getCurrentThreadData()
        threadData.lastErrorPage = (threadData.lastRequestUID, self._page)
    def startElement(self, name, attrs):
        if name == "dbms":
            self._dbms = attrs.get("value")
        elif name == "error":
            if re.search(attrs.get("regexp"), self._page, re.I):
                self.dbms = self._dbms
                self._markAsErrorPage()

```

可以发现当前返回的页面信息命中了`<error regexp="\bORA-[0-9][0-9][0-9][0-9]"/>`这一条正规

![p3](http://drops.javaweb.org/uploads/images/49a31022fa60989dc364b4fbb6f3c5cab3d51e22.jpg)

到此SQLMap就可以确定数据的版本了，从而选择对应的测试Payload，减少SQLMAP的扫描时间。

0x03 绝对路径获取与XSS检测
=================

* * *

相比指纹识别，获取绝对路径的功能模块相对简单，利用正则匹配寻找出绝对路径。

```
def parseFilePaths(page):
    """
    Detects (possible) absolute system paths inside the provided page content
    """
    if page:
        for regex in (r" in <b>(?P<result>.*?)</b> on line", r"(?:>|\s)(?P<result>[A-Za-z]:[\\/][\w.\\/]*)", r"(?:>|\s)(?P<result>/\w[/\w.]+)"):
            for match in re.finditer(regex, page):
                absFilePath = match.group("result").strip()
                page = page.replace(absFilePath, "")
                if isWindowsDriveLetterPath(absFilePath):
                    absFilePath = posixToNtSlashes(absFilePath)
                if absFilePath not in kb.absFilePaths:
                    kb.absFilePaths.add(absFilePath)

```

而XSS的检测代码位于889行中:

```
# String used for dummy XSS check of a tested parameter value
DUMMY_XSS_CHECK_APPENDIX = "<'\">"
    ...
    value = "%s%s%s" % (randomStr(), DUMMY_XSS_CHECK_APPENDIX, randomStr())
    payload = "%s%s%s" % (prefix, "'%s" % value, suffix)
    payload = agent.payload(place, parameter, newValue=payload)
    page, _ = Request.queryPage(payload, place, content=True, raise404=False)
    paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place
    if value in (page or ""):
        infoMsg = "heuristic (XSS) test shows that %s parameter " % paramType
        infoMsg += "'%s' might be vulnerable to XSS attacks" % parameter
        logger.info(infoMsg)
    ...

```

最后根据输入的字符是否留着页面上，如果存在就提示有可能拥有XSS漏洞。

0x04 总结
=======

* * *

至此heuristicCheckSqlInjection的功能也介绍的差不多了，通过具体了解SQLMAP的一些扫描规则又或者是思路，可以让我们根据具体的情况去配置SQLMAP又或者编写自己的SQL Fuzz系统，其中可以通过编辑errors.xml这一指数据纹配置来增强SQLMAP的嗅探能力，从而打造更强大的神器了。