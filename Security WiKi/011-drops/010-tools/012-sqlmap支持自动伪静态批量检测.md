# sqlmap支持自动伪静态批量检测

0x00 前言
=======

* * *

由于还没有找到一款比较适合批量检测sql注入点的工具（proxy+sqlmapapi的方式批量检测之类的批量sql注入点检测），我的目光就转向了sqlmap。虽然sqlmap没有支持伪静态注入点的测试(需要手动添加注入标记)，由于是python写的，可以快速方便的进行二次开发。

0x01 思路
=======

* * *

我的思路是在有.html之类的后缀或者既没有.html或者包含"?"的url进行修改。

伪静态注入点一般都在数字，所以我就在数字后面添加注入标记。字符串的伪静态就不搞了，搞了工作量就会添加很多。

用如下的URL进行测试

```
http://www.site.com/index.php/index/id/14
http://www.site.com/index.php/newsContent/id/341.html
http://www.site.com/show/?29-575.html

```

结果如下

```
http://www.site.com/index.php/index/id/14*
http://www.site.com/index.php/newsContent/id/341*.html
http://www.site.com/show/?29*-575*.html

```

代码如下：

```
if re.search('html|htm|sthml',url) or url.find("?") == -1:
    flag = 0
    suffix = ""
    if re.search('html|htm|sthml',url):
        suffix = "." + re.search('html|htm|sthml',url).group()
    urlList = url.split("/")

    returnList = []

    for i in urlList:
        i = re.sub('\.html|\.htm','', i)
        if i.isdigit():
            returnList.append(i + "*")
            flag = 1
        else:
            returnList.append(i)
    url = '/'.join(returnList) + suffix

    returnList = []
    if flag == 0:
        for i in urlList:
            if re.search('html|htm|sthml',i):
                digitList = re.findall('\d+',i)
                for digit in digitList:
                    i = i.replace(digit, digit + "*")
                returnList.append(i)
            else:
                returnList.append(i)
        url = '/'.join(returnList)    
    print url

```

0x02 sqlmap支持单个自动检测伪静态
======================

* * *

相关文件

*   [https://github.com/sqlmapproject/sqlmap/blob/master/sqlmap.py](https://github.com/sqlmapproject/sqlmap/blob/master/sqlmap.py)
*   [https://github.com/sqlmapproject/sqlmap/blob/master/lib/controller/controller.py](https://github.com/sqlmapproject/sqlmap/blob/master/lib/controller/controller.py)
*   [https://github.com/sqlmapproject/sqlmap/blob/master/lib/core/target.py](https://github.com/sqlmapproject/sqlmap/blob/master/lib/core/target.py)

**流程**

> Sqlmap.py 116行start()->controller.py 256行setupTargetEnv()->target.py 72行_setRequestParams()->target.py 117行

```
if kb.processUserMarks is None and CUSTOM_INJECTION_MARK_CHAR in conf.data:
message = "custom injection marking character ('%s') found in option " % CUSTOM_INJECTION_MARK_CHAR
message += "'--data'. Do you want to process it? [Y/n/q] "
test = readInput(message, default="Y")
if test and test[0] in ("q", "Q"):
raise SqlmapUserQuitException
else:
kb.processUserMarks = not test or test[0] not in ("n", "N")

if kb.processUserMarks:
kb.testOnlyCustom = True

```

这里检测是否使用了注入标记。

sqlmap获取完所有你指定的信息后，开始正式检测是否有注入之前，会检测是否使用了注入标记"`*`"，如果有的话就先处理这个注入标记的点进行测试。

这样就明白注入标记的流程，只要_setRequestParams函数调用之前处理好URL，就可以支持自动的伪静态注入的测试了。

只要在260行处添加

```
if re.search('html|htm|sthml',conf.url) or conf.url.find("?") == -1:
    flag = 0
    suffix = ""
    if re.search('html|htm|sthml',conf.url):
        suffix = "." + re.search('html|htm|sthml',conf.url).group()
    urlList = conf.url.split("/")

    returnList = []

    for i in urlList:
        i = re.sub('\.html|\.htm','', i)
        if i.isdigit():
            returnList.append(i + "*")
            flag = 1
        else:
            returnList.append(i)
    conf.url = '/'.join(returnList) + suffix

    returnList = []
    if flag == 0:
        for i in urlList:
            if re.search('html|htm|sthml',i):
                digitList = re.findall('\d+',i)
                for digit in digitList:
                    i = i.replace(digit, digit + "*")
                returnList.append(i)
            else:
                returnList.append(i)
        conf.url = '/'.join(returnList)
    logger.info(conf.url)

```

这样就可以了。

效果图

![pic1](http://drops.javaweb.org/uploads/images/4f568d905782e7ab0b3bfd2a41801a473a228975.jpg)

这里只是单个的，要支持批量检测注入点。修改这里是不行的。

0x03 sqlmap支持批量自动检测伪静态
======================

* * *

相关文件  
[https://github.com/sqlmapproject/sqlmap/blob/master/lib/core/option.py](https://github.com/sqlmapproject/sqlmap/blob/master/lib/core/option.py)

583行处

```
for line in getFileItems(conf.bulkFile):
    if re.match(r"[^ ]+\?(.+)", line, re.I) or CUSTOM_INJECTION_MARK_CHAR in line:
        found = True
        kb.targets.add((line.strip(), conf.method, conf.data, conf.cookie, None))

```

一行一行读取文件里面的url。只要匹配到有问号"?"或者有注入标记"*"才进行测试。

在583处添加

```
    if re.search('html|htm|sthml',line) or line.find("?") == -1:
        flag = 0
        suffix = ""
        if re.search('html|htm|sthml',line):
            suffix = "." + re.search('html|htm|sthml',line).group()
        urlList = line.split("/")

        returnList = []

        for i in urlList:
            i = re.sub('\.html|\.htm','', i)
            if i.isdigit():
                returnList.append(i + "*")
                flag = 1
            else:
                returnList.append(i)
        line = '/'.join(returnList) + suffix

        returnList = []
        if flag == 0:
            for i in urlList:
                if re.search('html|htm|sthml',i):
                    digitList = re.findall('\d+',i)
                    for digit in digitList:
                        i = i.replace(digit, digit + "*")
                    returnList.append(i)
                else:
                    returnList.append(i)
            line = '/'.join(returnList)

```

效果图：

![pic2](http://drops.javaweb.org/uploads/images/3d09882a027b9d5e220268f16e43200d32a54391.jpg)

0x04 最后
=======

* * *

如果有好的建议，可以在评论中给我留言。