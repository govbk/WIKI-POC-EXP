# SQLMAP源码分析Part1:流程篇

0x00 概述
=======

* * *

1.drops之前的文档[SQLMAP进阶使用](http://drops.wooyun.org/tips/5254)介绍过SQLMAP的高级使用方法，网上也有几篇介绍过SQLMAP源码的文章[曾是土木人](http://www.cnblogs.com/hongfei/category/372087.html),都写的非常好，建议大家都看一下。  
2.我准备分几篇文章详细的介绍下SQLMAP的源码，让想了解的朋友们熟悉一下SQLMAP的原理和一些手工注入的语句，今天先开始第一篇：流程篇。  
3.之前最好了解SQMAP各个选项的意思，可以参考[sqlmap用户手册](http://drops.wooyun.org/tips/143)和SQLMAP目录doc/README.pdf  
4.内容中如有错误或者没有写清楚的地方，欢迎指正交流。有部分内容是参考上面介绍的几篇文章的，在此一并说明，感谢他们。

0x01 流程图
========

![enter image description here](http://drops.javaweb.org/uploads/images/633282f29a309bdd23eed56248fc943a6f97aaa5.jpg)

0x02 调试方法
=========

* * *

1.我用的IDE是PyCharm。  
2.在菜单栏Run->Edit Configurations。点击左侧的“+”，选择Python，Script中选择sqlmap.py的路径，Script parameters中填入注入时的命令，如下图。![enter image description here](http://drops.javaweb.org/uploads/images/3a6f75634e540bac3b22b45e6ec8516b898c0f2a.jpg)

3.打开sqlmap.py，开始函数是main函数,在main函数处下断点。![enter image description here](http://drops.javaweb.org/uploads/images/df65eef29d9d9e0e2c711871a5e21bfe9c8e7929.jpg)

4.右键Debug 'sqlmap',然后程序就自动跳到我们下断点的main()函数处，后面可以继续添加断点进行调试。如下图，左边红色的代表跳转到下一个断点处，上面红色的表示跳到下一句代码处

![enter image description here](http://drops.javaweb.org/uploads/images/d3d3e9495c317879853f085182608f63dcbfc943.jpg)

5.另外，如果要在代码中加中文注释，需要在开始处添加以下语句：#coding:utf-8。

0x03 流程
=======

* * *

3.1 初始化
-------

我这里用的版本是：1.0-dev-nongit-20150614  
miin()函数开始73行：

```
paths.SQLMAP_ROOT_PATH = modulePath()
setPaths()

```

进入common.py中的setPaths()函数后，就可以看到这个函数是定义SQLMAP路径和文件的，类似于：

```
paths.SQLMAP_EXTRAS_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "extra")
paths.SQLMAP_PROCS_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "procs")
paths.SQLMAP_SHELL_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "shell")
paths.SQLMAP_TAMPER_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "tamper")
paths.SQLMAP_WAF_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "waf")

```

接下来的78行函数initOptions(cmdLineOptions),包含了三个函数，作用如流程图所示，设置conf,KB,参数. conf会保存用户输入的一些参数，比如url，端口  
kb会保存注入时的一些参数，其中有两个是比较特殊的kb.chars.start和kb.chars.stop，这两个是随机字符串，后面会有介绍。

```
_setConfAttributes()
_setKnowledgeBaseAttributes()
_mergeOptions(inputOptions, overrideOptions)

```

3.2 start
---------

102行的start函数，算是检测开始的地方.start()函数位于controller.py中。

```
if conf.direct:        
    initTargetEnv()
    setupTargetEnv()
    action()
    return True

```

首先这四句，意思是，如果你使用-d选项，那么sqlmap就会直接进入action()函数，连接数据库，语句类似为：

```
python sqlmap.py -d "mysql://admin:admin@192.168.21.17:3306/testdb" -f --banner --dbs --user


#!python
if conf.url and not any((conf.forms, conf.crawlDepth)):
    kb.targets.add((conf.url, conf.method, conf.data, conf.cookie, None))

```

上面代码会把url,methos,data,cookie加入到kb.targets，这些参数就是我们输入的

![enter image description here](http://drops.javaweb.org/uploads/images/c4cff7429cc23c0dd13b9d3e76db58dfed08f16f.jpg)

接下来从274行的for循环中，可以进入检测环节

```
for targetUrl, targetMethod, targetData, targetCookie, targetHeaders in kb.targets:

```

此循环先初始化一些一些变量，然后判断之前是否注入过，如果没有注入过，testSqlInj=True,否则testSqlInj=false。后面会进行判断是否检测过。

```
def setupTargetEnv():
    _createTargetDirs()
    _setRequestParams()
    _setHashDB()
    _resumeHashDBValues()
    _setResultsFile()
    _setAuthCred()

```

372行setupTargetEnv()函数中包含了5个函数，这些函数作用是

1.创建输出结果目录

2.解析请求参数

3.设置session信息，就是session.sqlite。

4.恢复session的数据，继续扫描。

5.存储扫描结果。

6.添加认证信息

其中比较重要的就是session.sqlite，这个文件在sqlmap的输出目录中，测试的结果都会保存在这个文件里。

### 3.2.1 checkWaf

```
checkWaf()
if conf.identifyWaf:
    identifyWaf()

```

377行checkWaf()是检测是否有WAF,检测方法是NMAP的http-waf-detect.nse，比如页面为index.php?id=1，那现在添加一个随机变量index.php?id=1&aaa=2，设置paoyload类似为`AND 1=1 UNION ALL SELECT 1,2,3,table_name FROM information_schema.tables WHERE 2>1-- ../../../etc/passwd`，如果没有WAF，页面不会变化，如果有WAF，因为payload中有很多敏感字符，大多数时候页面都会发生改变。  
接下来的conf.identifyWaf代表sqlmap的参数--identify-waf,如果指定了此参数，就会进入identifyWaf()函数，主要检测的waf都在sqlmap的waf目录下。

![enter image description here](http://drops.javaweb.org/uploads/images/229961a0fe670fb59a06c47039f0663637072c58.jpg)

当然检测的方法都比较简单，都是查看返回的数据库包种是否包含了某些特征字符。如：

```
__product__ = "360 Web Application Firewall (360)"

def detect(get_page):
    retval = False

    for vector in WAF_ATTACK_VECTORS:
        page, headers, code = get_page(get=vector)
        retval = re.search(r"wangzhan\.360\.cn", headers.get("X-Powered-By-360wzb", ""), re.I) is not None
        if retval:
            break

    return retval



if (len(kb.injections) == 0 or (len(kb.injections) == 1 and kb.injections[0].place is None)) \
                and (kb.injection.place is None or kb.injection.parameter is None):

```

回到start函数，385行会判断是否注入过，如果还没有测试过参数是否可以注入，则进入if语句中。如果之前测试过，则不会进入此语句。

```
for place in parameters:
    # Test User-Agent and Referer headers only if
    # --level >= 3
    skip = (place == PLACE.USER_AGENT and conf.level < 
    skip |= (place == PLACE.REFERER and conf.level < 3)
    # Test Host header only if
    # --level >= 5
    skip |= (place == PLACE.HOST and conf.level < 5)
    # Test Cookie header only if --level >= 2
    skip |= (place == PLACE.COOKIE and conf.level < 2)

```

这中间sqlmap给了我们一些注释，可以看到，level>=3时，会测试user-agent,referer，level>=5时，会测试HOST，level>=2时，会测试cookie。当然最终的测试判断还要在相应的xml中指定，后面会介绍。

```
check = checkDynParam(place, parameter, value)

```

480行的checkDynParam()函数会判断参数是否是动态的，比如index.php?id=1，通过更改id的值，如果参数是动态的，页面会不同。

### 3.2.2 heuristicCheckSqlInjection

```
check = heuristicCheckSqlInjection(place, parameter)

```

502行有个heuristicCheckSqlInjection()函数，翻译过来是启发性sql注入测试，其实就是先进行一个简单的测试，设置一个payload，然后解析请求结果。  
heuristicCheckSqlInjection()在checks.py中,821行开始如下:

```
if conf.prefix or conf.suffix:
        if conf.prefix:
            prefix = conf.prefix

        if conf.suffix:
            suffix = conf.suffix

    randStr = ""

    while '\'' not in randStr:
        randStr = randomStr(length=10, alphabet=HEURISTIC_CHECK_ALPHABET)   

    kb.heuristicMode = True

    payload = "%s%s%s" % (prefix, randStr, suffix)
    payload = agent.payload(place, parameter, newValue=payload)
    page, _ = Request.queryPage(payload, place, content=True, raise404=False)

    kb.heuristicMode = False

    parseFilePaths(page)
    result = wasLastResponseDBMSError()

```

首先conf.prefix和conf.suffix代表用户指定的前缀和后缀；在`while '\'' not in randStr`中，随机选择'"', '\'', ')', '(', ',', '.'中的字符，选10个，并且单引号要在。接下来生成一个payload，类似u'name=**PAYLOAD_DELIMITER\__1)."."."\'."__PAYLOAD_DELIMITER**'。其中**PAYLOAD_DELIMITER\__1和__PAYLOAD_DELIMITER**是随机字符串。请求网页后，调用parseFilePaths进行解析，查看是否爆出绝对路径，而wasLastResponseDBMSError是判断response中是否包含了数据库的报错信息。

```
value = "%s%s%s" % (randomStr(), DUMMY_XSS_CHECK_APPENDIX, randomStr())
payload = "%s%s%s" % (prefix, "'%s" % value, suffix)
payload = agent.payload(place, parameter, newValue=payload)
page, _ = Request.queryPage(payload, place, content=True, raise404=False)

paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place

if value in (page or ""):       
    infoMsg = "heuristic (XSS) test shows that %s parameter " % paramType
    infoMsg += "'%s' might be vulnerable to XSS attacks" % parameter
    logger.info(infoMsg)

kb.heuristicMode = False

```

上面的代码是从888行开始，DUMMY_XSS_CHECK_APPENDIX = "<'\">"，如果输入的字符串在页面中返回了，会提示可能存在XSS漏洞。

![enter image description here](http://drops.javaweb.org/uploads/images/969bd0a001b2caa420d73b6e827565afbdcb5a1d.jpg)

接下来，我们回到start函数中，继续看下面的代码。

```
if testSqlInj:
    ......
    injection = checkSqlInjection(place, parameter, value)

```

在502行判断testSqlInj,如果为true，就代表之前没有检测过，然后就会到checkSqlInjection，checkSqlInjection()才是真正开始测试的函数，传入的参数是注入方法如GET，参数名，参数值。我们跟进。

### 3.2.3 checkSqlInjection

checkSqlInjection()在checks.py中,91行开始

```
paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place
tests = getSortedInjectionTests()

```

paramType是注入的类型,如GET。tests是要测试的列表，如下图所示，包含了每个测试项的名称，这些数据都是和/sqlmap/xml/payloads/目录下每个xml相对应的。

![enter image description here](http://drops.javaweb.org/uploads/images/b595d77f76c8c4a65004ea06e9ff804d7a6a4340.jpg)

```
if conf.dbms is None:
    if not injection.dbms and PAYLOAD.TECHNIQUE.BOOLEAN in injection.data:
        if not Backend.getIdentifiedDbms() and kb.heuristicDbms is False:
            kb.heuristicDbms = heuristicCheckDbms(injection)
    if kb.reduceTests is None and not conf.testFilter and (intersect(Backend.getErrorParsedDBMSes(), \
       SUPPORTED_DBMS, True) or kb.heuristicDbms or injection.dbms):
        msg = "it looks like the back-end DBMS is '%s'. " % (Format.getErrorParsedDBMSes() or kb.heuristicDbms or injection.dbms)
        msg += "Do you want to skip test payloads specific for other DBMSes? [Y/n]"
        kb.reduceTests = (Backend.getErrorParsedDBMSes() or [kb.heuristicDbms]) if readInput(msg, default='Y').upper() == 'Y' else []
if kb.extendTests is None and not conf.testFilter and (conf.level < 5 or conf.risk < 3) \
   and (intersect(Backend.getErrorParsedDBMSes(), SUPPORTED_DBMS, True) or \
   kb.heuristicDbms or injection.dbms):
    msg = "for the remaining tests, do you want to include all tests "
    msg += "for '%s' extending provided " % (Format.getErrorParsedDBMSes() or kb.heuristicDbms or injection.dbms)
    msg += "level (%d)" % conf.level if conf.level < 5 else ""
    msg += " and " if conf.level < 5 and conf.risk < 3 else ""
    msg += "risk (%d)" % conf.risk if conf.risk < 3 else ""
    msg += " values? [Y/n]" if conf.level < 5 and conf.risk < 3 else " value? [Y/n]"
    kb.extendTests = (Backend.getErrorParsedDBMSes() or [kb.heuristicDbms]) if readInput(msg, default='Y').upper() == 'Y' else []

```

101行开始，这段代码主要是判断DBMS类型，首先，如果用户没有手工指定dbms，则会根据页面报错或者bool类型的测试，找出DBMS类型，找出后，会提示是否跳过测试其他的DBMS。然后，对于测试出来的DBMS，是否用所有的payload来测试。

![enter image description here](http://drops.javaweb.org/uploads/images/40717c23017969d55097a2458c7759bfff70fe2c.jpg)

140行if stype == PAYLOAD.TECHNIQUE.UNION:会判断是不是union注入，这个stype就是payload文件夹下面xml文件中的stype，如果是union，就会进入，然后配置列的数量等，今天先介绍流程，union注入以后会介绍。

```
if conf.tech and isinstance(conf.tech, list) and stype not in conf.tech:
                debugMsg = "skipping test '%s' because the user " % title
                debugMsg += "specified to test only for "
                debugMsg += "%s techniques" % " & ".join(map(lambda x: PAYLOAD.SQLINJECTION[x], conf.tech))
                logger.debug(debugMsg)
                continue

```

177行，就是用户提供的--technique，共有六个选项BEUSTQ,但是现在很多文档，包括SQLMAP的官方文档都只给了BEUST的解释说明，少个inline_query，相当于查询语句中再加入一个查询语句。

```
B: Boolean-based blind SQL injection（布尔型注入）
E: Error-based SQL injection（报错型注入）
U: UNION query SQL injection（可联合查询注入）
S: Stacked queries SQL injection（可多语句查询注入）
T: Time-based blind SQL injection（基于时间延迟注入）
Q: inline_query(内联查询)

```

接下来，就是生成payload的过程。288行：

```
fstPayload = agent.cleanupPayload(test.request.payload, origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)

```

test.request.payload为'AND [RANDNUM]=[RANDNUM]'(相应payload.xml中的request值)。根据此代码，生成一个随机字符串，如fstPayload=u'AND 2876=2876'。  
302行：

```
for boundary in boundaries:
     injectable = False
     if boundary.level > conf.level and not (kb.extendTests and intersect(payloadDbms, kb.extendTests, True)):
                    continue

```

循环遍历boundaries.xml中的boundary节点，如果boundary的level大于用户提供的level，则跳过，不检测。  
307行：

```
clauseMatch = False
for clauseTest in test.clause:     
     if clauseTest in boundary.clause:   
         clauseMatch = True
         break
if test.clause != [0] and boundary.clause != [0] and not clauseMatch:
     continue
whereMatch = False
for where in test.where:
     if where in boundary.where:
         whereMatch = True
         break
if not whereMatch:
     continue

```

首先，循环遍历test.clause(payload中的clause值)，如果clauseTest在boundary的clause中，则设置clauseMatch = True，代表此条boundary可以使用。 接下来循环匹配where(payload中的where值)，如果存在这样的where，设置whereMatch = True。如果clause和where中的一个没有匹配成功，都会结束循环，进入下一个payload的测试。

```
prefix = boundary.prefix if boundary.prefix else ""
suffix = boundary.suffix if boundary.suffix else ""
ptype = boundary.ptype
prefix = conf.prefix if conf.prefix is not None else prefix
suffix = conf.suffix if conf.suffix is not None else suffix
comment = None if conf.suffix is not None else comment

```

上面是设置payload的前缀和后缀，如果用户设置了，则使用用户设置的，如果没有，则使用boundary中的。  
352行：

```
for where in test.where:
    if where == PAYLOAD.WHERE.ORIGINAL or conf.prefix:
        ......
    elif where == PAYLOAD.WHERE.NEGATIVE:
        ......
    elif where == PAYLOAD.WHERE.REPLACE:
        ......

```

这里的where是payload中的where值，共有三个值，where字段我理解的意思是，以什么样的方式将我们的payload添加进去。

1：表示将我们的payload直接添加在值得后面[此处指的应该是检测的参数的值] 如我们写的参数是id=1，设置值为1的话，会出现1后面跟payload

2：表示将检测的参数的值更换为一个整数，然后将payload添加在这个整数的后面。 如我们写的参数是id=1，设置值为2的话，会出现[数字]后面跟payload

3：表示将检测的参数的值直接更换成我们的payload。 如我们写的参数是id=1，设置值为3的话，会出现值1直接被替换成了我们的payload。  
最终在389行：

```
boundPayload = agent.prefixQuery(fstPayload, prefix, where, clause)
boundPayload = agent.suffixQuery(boundPayload, comment, suffix, where)
reqPayload = agent.payload(place, parameter, newValue=boundPayload, where=where)

```

组合前缀、后缀、payload等，生成请求的reqPayload。  
这其中有个cleanupPayload()函数，其实就是将一些值进行随机化。如下图，例如kb.chars.start,kb.chars.stop，这两个变量是在基于错误的注入时，随机产生的字符串。

![enter image description here](http://drops.javaweb.org/uploads/images/886387d3fd6d4f84a188a9a0c95fdf895de37514.jpg)

在398行：

```
for method, check in test.response.items():
    check = agent.cleanupPayload(check, origValue=value if place not in (PLACE.
URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)      
    if method == PAYLOAD.METHOD.COMPARISON:     
        def genCmpPayload():
            sndPayload = agent.cleanupPayload(test.response.comparison, 
origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, 
PLACE.CUSTOM_HEADER) else None)
            boundPayload = agent.prefixQuery(sndPayload, prefix, where, clause)
            boundPayload = agent.suffixQuery(boundPayload, comment, suffix, 
where)
            cmpPayload = agent.payload(place, parameter, 
newValue=boundPayload, where=where)
            return cmpPayload
        kb.matchRatio = None
        kb.negativeLogic = (where == PAYLOAD.WHERE.NEGATIVE)
        Request.queryPage(genCmpPayload(), place, raise404=False)
        falsePage = threadData.lastComparisonPage or ""     
        trueResult = Request.queryPage(reqPayload, place, raise404=False)
        truePage = threadData.lastComparisonPage or ""      
        if trueResult:
            falseResult = Request.queryPage(genCmpPayload(), place, 
raise404=False)
            if not falseResult:
                infoMsg = "%s parameter '%s' seems to be '%s' injectable " % (
paramType, parameter, title)
                logger.info(infoMsg)
                injectable = True
        if not injectable and not any((conf.string, conf.notString, conf.
regexp)) and kb.pageStable:
            trueSet = set(extractTextTagContent(truePage))
            falseSet = set(extractTextTagContent(falsePage))
            candidates = filter(None, (_.strip() if _.strip() in (kb.
pageTemplate or "") and _.strip() not in falsePage and _.strip() 
not in threadData.lastComparisonHeaders else None for _ in (
trueSet - falseSet)))
            if candidates:
                conf.string = candidates[0]
                infoMsg = "%s parameter '%s' seems to be '%s' injectable (with 
--string=\"%s\")" % (paramType, parameter, title, repr(conf.
string).lstrip('u').strip("'"))
                logger.info(infoMsg)
                injectable = True
    elif method == PAYLOAD.METHOD.GREP:
        try:
            page, headers = Request.queryPage(reqPayload, place, content=True, 
raise404=False)
            output = extractRegexResult(check, page, re.DOTALL | re.
IGNORECASE) \
                    or extractRegexResult(check, listToStrValue( \
                    [headers[key] for key in headers.keys() if key.lower() != 
URI_HTTP_HEADER.lower()] \
                    if headers else None), re.DOTALL | re.IGNORECASE) \
                    or extractRegexResult(check, threadData.lastRedirectMsg[1] 
\
                    if threadData.lastRedirectMsg and threadData.
lastRedirectMsg[0] == \
                    threadData.lastRequestUID else None, re.DOTALL | re.
IGNORECASE)
            if output:
                result = output == "1"
                if result:
                    infoMsg = "%s parameter '%s' is '%s' injectable " % (
paramType, parameter, title)
                    logger.info(infoMsg)
                    injectable = True
        except SqlmapConnectionException, msg:
            debugMsg = "problem occurred most likely because the "
            debugMsg += "server hasn't recovered as expected from the "
            debugMsg += "error-based payload used ('%s')" % msg
            logger.debug(debugMsg)
    elif method == PAYLOAD.METHOD.TIME:
        trueResult = Request.queryPage(reqPayload, place, 
timeBasedCompare=True, raise404=False)
        if trueResult:
            # Confirm test's results
            trueResult = Request.queryPage(reqPayload, place, 
timeBasedCompare=True, raise404=False)
            if trueResult:
                infoMsg = "%s parameter '%s' seems to be '%s' injectable " % (
paramType, parameter, title)
                logger.info(infoMsg)
                injectable = True
    elif method == PAYLOAD.METHOD.UNION:
        configUnion(test.request.char, test.request.columns)
        if not Backend.getIdentifiedDbms():
            if kb.heuristicDbms is None:
                warnMsg = "using unescaped version of the test "
                warnMsg += "because of zero knowledge of the "
                warnMsg += "back-end DBMS. You can try to "
                warnMsg += "explicitly set it using option '--dbms'"
                singleTimeWarnMessage(warnMsg)
            else:
                Backend.forceDbms(kb.heuristicDbms)
        if unionExtended:
            infoMsg = "automatically extending ranges for UNION "
            infoMsg += "query injection technique tests as "
            infoMsg += "there is at least one other (potential) "
            infoMsg += "technique found"
            singleTimeLogMessage(infoMsg)
        reqPayload, vector = unionTest(comment, place, parameter, value, 
prefix, suffix)
        if isinstance(reqPayload, basestring):
            infoMsg = "%s parameter '%s' is '%s' injectable" % (paramType, 
parameter, title)
            logger.info(infoMsg)
            injectable = True
            # Overwrite 'where' because it can be set
            # by unionTest() directly
            where = vector[6]
    kb.previousMethod = method

```

上面这部分代码非常多，通过for循环遍历payload中的标签，遍历的结果类似于

![enter image description here](http://drops.javaweb.org/uploads/images/36907ab8ccdf0a8f481f769ee32869ba6587a2f1.jpg)

所以，上面的代码可以分为：

1.method为PAYLOAD.METHOD.COMPARISON：bool类型盲注 2.method为PAYLOAD.METHOD.GREP：基于错误的sql注入 3.mehtod为PAYLOAD.METHOD.TIME：基于时间的盲注 4.method为PAYLOAD.METHOD.UNION：union联合查询

请注意，上面这四种方法，和之前说的六种注入方法不是一个概念，这里的是payload中的response代码，而注入用的是request代码。通过比较request的结果和response的结果，确定是否可以注入。以后的文章会介绍怎么比较的。。  
checkSqlInjectiond的关键部分就到这里了，后面就是把注入的数据保存起来。马上会介绍读取的时候。

### 3.2.4 Payload生成条件

前面具体介绍了Payload的生成方法，这里再总结一下条件：

1.sqlmap会实现读取payloads文件夹下xml文件中的每个test元素，然后循环遍历。

2.此时还会遍历boundaries.xml文件。

3.当且仅当某个boundary元素的where节点的值包含test元素where节点的值，clause节点的值包含test元素的clause节点的值，该boundary才能和当前的test匹配，从而进一步生成payload。

4.where字段有三个值1：表示将我们的payload直接添加在值得后面[此处指的应该是检测的参数的值] 如我们写的参数是id=1，设置值为1的话，会出现1后面跟payload 2：表示将检测的参数的值更换为一个整数，然后将payload添加在这个整数的后面。 如我们写的参数是id=1，设置值为2的话，会出现[数字]后面跟payload 3：表示将检测的参数的值直接更换成我们的payload。 如我们写的参数是id=1，设置值为3的话，会出现值1直接被替换成了我们的payload

5.最终的payload = url参数 + boundary.prefix+test.payload+boundary.suffix

### 3.2.5 Action

在start()的617行是action()函数，位于Action.py中，此函数是判断用户提供的参数，然后提供相应的函数。

```
if conf.getDbs:
    conf.dumper.dbs(conf.dbmsHandler.getDbs())
if conf.getTables:
    conf.dumper.dbTables(conf.dbmsHandler.getTables())
if conf.commonTables:
    conf.dumper.dbTables(tableExists(paths.COMMON_TABLES))

```

### 3.2.6 HashDB

sqlmap注入的结果会保存在输出目录的session.sqlite文件汇总，此文件是sqlite数据库，可以使用SQLiteManager打开。  
回到controller.py中的start函数。第602行

```
_saveToResultsFile()
_saveToHashDB()     
_showInjections()   
_selectInjection()  

```

这四个函数的作用就是保存结果保存结果、保存session、显示注入结果，包括类型，payload等。  
前面介绍过会判断testSqlInj的值，如果为True，代表没有测试过，会进入checkSqlInjection()函数，如果测试过，那么testSqlInj为false，就会跳过checkSqlInjection()。  
比如我们选择--current-db时，通过action()进入到conf.dumper.currentDb(conf.dbmsHandler.getCurrentDb())。进入到databases.py的getCurrentDb中。

```
query = queries[Backend.getIdentifiedDbms()].current_db.query

```

这是获取相应的命令，比如mysql的命令是database().一直跟踪函数到use.py的346行

```
if not value and not abortedFlag:
    output = _oneShotUnionUse(expression, unpack)
    value = parseUnionPage(output)

```

_onehotUninoUse就是读取session文件，获取已经注入过的数据，如果session中没有，代表没有请求过，则重新请求获取数据。output此时是获取的网页的源码。

```
retVal = hashDBRetrieve("%s%s" % (conf.hexConvert, expression), checkConf=True)

```

_onehotUninoUse的第一行，就是从session中获取数据，跟踪进hashdb.py的regrieve函数

```
def hashKey(key):
    key = key.encode(UNICODE_ENCODING) if isinstance(key, unicode) else repr(key)
    retVal = int(hashlib.md5(key).hexdigest()[:12], 16)     #注释：hash的算法，对应数据库中的id。md5后，转换为10进制，就是session中的id
    return retVal
def retrieve(self, key, unserialize=False):
    retVal = None
    if key and (self._write_cache or os.path.isfile(self.filepath)):
        hash_ = HashDB.hashKey(key)
        retVal = self._write_cache.get(hash_)
        if not retVal:      
            while True:
                try:
                    for row in self.cursor.execute("SELECT value FROM storage WHERE id=?", (hash_,)):
                        retVal = row[0]
                except sqlite3.OperationalError, ex:
                    if not "locked" in ex.message:
                        raise
                except sqlite3.DatabaseError, ex:
                    errMsg = "error occurred while accessing session file '%s' ('%s'). " % (self.filepath, ex)
                    errMsg += "If the problem persists please rerun with `--flush-session`"
                    raise SqlmapDataException, errMsg
                else:
                    break
    return retVal if not unserialize else unserializeObject(retVal)

```

通过HashDB.hashKey()计算id，然后到session.sqlite中找记录，那么key是怎么生成的呢？  
在common.py中有个hashDBRetrieve(),

```
def hashDBRetrieve(key, unserialize=False, checkConf=False):
    _ = "%s%s%s" % (conf.url or "%s%s" % (conf.hostname, conf.port), key, HASHDB_MILESTONE_VALUE)
    retVal = conf.hashDB.retrieve(_, unserialize) if kb.resumeValues and not (checkConf and any((conf.flushSession, conf.freshQueries))) else None
    if not kb.inferenceMode and not kb.fileReadMode and any(_ in (retVal or "") for _ in (PARTIAL_VALUE_MARKER, PARTIAL_HEX_VALUE_MARKER)):
        retVal = None
    return retVal

```

此函数用于生成hash的key，生成方法为url+'None'+命令+HASHDB_MILESTONE_VALUE,比如u'http://127.0.0.1:80/biweb/archives/detail.phpNoneDATABASE()JHjrBugdDA'。此key经过int(hashlib.md5(key).hexdigest()[:12], 16)，就是对应session中的id

![enter image description here](http://drops.javaweb.org/uploads/images/1465ad68e9ff9b8d51ae1754ed32af9a98973672.jpg)

最终在session.sqlite中根据id，就能够找到记录。

![enter image description here](http://drops.javaweb.org/uploads/images/cb972c04bccb1c411762c86347f9d8678bc8cb27.jpg)

如上图，获取到的记录其实就是一个网页的源代码，另外可以看到current-db的前后有几个字符串，这个字符串就是kb.chars.start和kb.chars.stop  
回到_oneShotUnionUse中，如果session中没有记录，则会重新进行请求，获取数据

```
vector = kb.injection.data[PAYLOAD.TECHNIQUE.UNION].vector
        kb.unionDuplicates = vector[7]
        kb.forcePartialUnion = vector[8]
        query = agent.forgeUnionQuery(injExpression, vector[0], vector[1], vector[2], vector[3], vector[4], vector[5], vector[6], None, limited)    
        where = PAYLOAD.WHERE.NEGATIVE if conf.limitStart or conf.limitStop else vector[6]
        payload = agent.payload(newValue=query, where=where)

```

最终的值通过解析session中的记录value = parseUnionPage(output)，找到kb.chars.start和kb.chars.stop中间的值，就是结果。

0x04 结束
=======

* * *

还有很多东西没有写出来，希望后面的几篇文章能够写好。花了好久的时间，调试、码字，不知道又没有人能看到最后。。