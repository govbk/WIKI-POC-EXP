# 打造自己的php半自动化代码审计工具

0x00 PHP扩展进行代码分析（动态分析）
======================

* * *

### 一.基础环境

```
apt-get install php5
apt-get install php5-dev
apt-get install apache
apt-get install mysql

```

### 二.使用PHPTracert

```
mkdir godhead
wget https://github.com/Qihoo360/phptrace/archive/v0.3.0.zip
unzip v0.3.0.zip
cd ./phptrace-0.3.0/extension
phpize5
./configure --with-php-config=/usr/bin/php-config
make & make install
cd ../cmdtool
make 

```

编辑`php.ini`，增加:

```
extension=trace.so

```

### 三.测试

```
<?php 
for($i=0;$i<100;$i++){
    echo $I;
    sleep(1);
}
?>

```

**CLI**

```
php test.php &
ps -axu|grep php
./phptrace -p pid

```

**apache**

```
curl 127.0.0.1/test.php
ps -aux|grep apache
./phptrace -p pid

```

### 四.phptrace分析

执行的代码如下:

```
<?php
function c(){
    echo 1;
}
function b(){
    c();
}
function a(){
    b();
}
a();
?>

```

执行顺序是:

```
a>b>c>echo

```

参数含义:

| 名称 | 值 | 意义 |
| :-- | :-- | :-- |
| seq |  | int|执行的函数的次数 |
| type | 1/2 | 1是代表调用函数，2是代表该函数返回 |
| level | -10 | 执行深度，比如a函数调用b，那么a的level就是1，b的level就是2，依次递增 |
| func | eval | 调用的函数名称 |
| st | 1448387651119460 | 时间戳 |
| params | string | 函数的参数 |
| file | c.php | 执行的文件 |
| lineno | 1 | 此函数对应的行号 |

日志输出:

```
{"seq":0, "type":1, "level":1, "func":"{main}", "st":1448387651119445, "params":"", "file":"/var/www/html/2.php", "lineno":11 }
{"seq":1, "type":1, "level":2, "func":"a", "st":1448387651119451, "params":"", "file":"/var/www/html/2.php", "lineno":11 }
{"seq":2, "type":1, "level":3, "func":"b", "st":1448387651119452, "params":"", "file":"/var/www/html/2.php", "lineno":9 }
{"seq":3, "type":1, "level":4, "func":"c", "st":1448387651119453, "params":"", "file":"/var/www/html/2.php", "lineno":6 }
{"seq":4, "type":2, "level":4, "func":"c, "st":1448387651119457, "return":"NULL", "wt":4, "ct":4, "mem":48, "pmem":144 }
{"seq":5, "type":2, "level":3, "func":"b, "st":1448387651119459, "return":"NULL", "wt":7, "ct":6, "mem":48, "pmem":144 }
{"seq":6, "type":2, "level":2, "func":"a, "st":1448387651119459, "return":"NULL", "wt":8, "ct":8, "mem":80, "pmem":176 }
{"seq":7, "type":2, "level":1, "func":"{main}, "st":1448387651119460, "return":"1", "wt":15, "ct":14, "mem":112, "pmem":208 }

```

### 五.逻辑分析

**1.解析监控进程**

开一个后台进程一直刷新进程列表，如果出现没有tracer的进程就立即进行托管

**2.json提取**

通过对每一个文件的json进行提取，提取过程如下:

1.  便利所有文件
2.  读读取文件
3.  提取json，按照seq排序
4.  提取`type=2`的与`type=1`的进行合并
5.  按照level梳理上下级关系存储同一个字典
6.  按照seq排序，取出头函数进行输出
7.  提取恶意函数往上提取level直到`level=0`

函数对应如下:

```
list1={
     level1:[seq,type,func,param,return]
     level2:[seq,type,func,param,return]
     level3:[seq,type,func,param,return] #eval 
     level4:[seq,type,func,param,return]

}
list2=

```

**3.数据查看**

通过追踪危险函数，然后将其函数执行之前的关系梳理出来进行输出，然后再进行人工审查。

放上demo

![p1](http://drops.javaweb.org/uploads/images/80bbd80b052c16a5977f6f775ae41c11a8e0dfb7.jpg)

![p2](http://drops.javaweb.org/uploads/images/b329c13b23702e705dbfe1e6ec13367ecf47e693.jpg)

### 六.使用XDEBUG

安装

```
apt-get install php5-xdebug

```

修改`php.ini`

```
[xdebug]
zend_extension = "/usr/lib/php5/20131226/xdebug.so"
xdebug.auto_trace = on
xdebug.auto_profile = on
xdebug.collect_params = on
xdebug.collect_return = on
xdebug.profiler_enable = on
xdebug.trace_output_dir = "/tmp/ad/xdebug_log"
xdebug.profiler_output_dir = "/tmp/ad/xdebug_log"

```

放上几个demo图片:

![p3](http://drops.javaweb.org/uploads/images/6dcc234f8f6dd45a8327989fa68cbacc31636178.jpg)

### 七.优缺点

**缺点**

人为参与力度较大，无法进行脱离人工的操作进行独立执行。

**优点**

精准度高，对于面向对象和面向过程的代码都可以进行分析。

0x01 语法分析（静态分析）
===============

* * *

案例：

*   [http://php-grinder.com/](http://php-grinder.com/)
*   [http://rips-scanner.sourceforge.net/](http://rips-scanner.sourceforge.net/)

### 一.使用php-parser

介绍：

*   [http://www.oschina.net/p/php-parser](http://www.oschina.net/p/php-parser)
*   [https://github.com/nikic/PHP-Parser/](https://github.com/nikic/PHP-Parser/)

### 二.安装

```
git clone https://github.com/nikic/PHP-Parser.git & cd PHP-Parser
curl -sS https://getcomposer.org/installer | php

```

PHP >= 5.3; for parsing PHP 5.2 to PHP 5.6

```
php composer.phar require nikic/php-parser

```

PHP >= 5.4; for parsing PHP 5.2 to PHP 7.0

```
php composer.phar require nikic/php-parser 2.0.x-dev

```

### 三.测试

```
<?php
include 'autoload.php';
use PhpParser\Error;
use PhpParser\ParserFactory;

$code = '<?php  eval($_POST[c][/c])?>';
$parser = (new ParserFactory)->create(ParserFactory::PREFER_PHP7);

try {
    $stmts = $parser->parse($code);
    print_r($stmts);
    // $stmts is an array of statement nodes
} catch (Error $e) {
    echo 'Parse Error: ', $e->getMessage();
}

```

输出如下:

```
Array
(
    [0] => PhpParser\Node\Expr\Eval_ Object
        (
            [expr] => PhpParser\Node\Expr\ArrayDimFetch Object
                (
                    [var] => PhpParser\Node\Expr\Variable Object
                        (
                            [name] => _POST
                            [attributes:protected] => Array
                                (
                                    [startLine] => 1
                                    [endLine] => 1
                                )

                        )

                    [dim] => PhpParser\Node\Expr\ConstFetch Object
                        (
                            [name] => PhpParser\Node\Name Object
                                (
                                    [parts] => Array
                                        (
                                            [0] => c
                                        )

                                    [attributes:protected] => Array
                                        (
                                            [startLine] => 1
                                            [endLine] => 1
                                        )

                                )

                            [attributes:protected] => Array
                                (
                                    [startLine] => 1
                                    [endLine] => 1
                                )

                        )

                    [attributes:protected] => Array
                        (
                            [startLine] => 1
                            [endLine] => 1
                        )

                )

            [attributes:protected] => Array
                (
                    [startLine] => 1
                    [endLine] => 1
                )

        )

)

```

由此可见，我们需要提取出

```
[0] => PhpParser\Node\Expr\Eval_ Object
[name] => _POST
[parts] => Array
                                        (
                                            [0] => c
                                        )

```

然后进行拼接之后即可发现原始语句是:

```
eval($_POST[c][/c])

```

### 四.逻辑分析

**代码解析**

1.  通过该库进行语法分析
2.  提取结果
3.  提取危险函数
4.  提取危险函数中存在的变量
5.  从上文中提取此变量的赋值方式
6.  分析出可控结果
7.  输出结果

### 五.优缺点

**缺点**

对于面向对象的程序进行分析比较弱。

**优点**

适合大批量的自动化分析，可以脱离人工操作进行独立执行