# 基于PHP扩展的WAF实现

0x00 前言
=======

* * *

最近上(ri)网(zhan)上(ri)多了，各种狗啊盾啊看的好心烦，好多蜜汁shell都被杀了，搞的我自己也想开发这么一个斩马刀，顺便当作毕设来做了。

未知攻，焉知防。我们先来看看shell们都是怎么躲过查杀的：加密、变形、回调、隐藏关键字……总之就是一句话，让自己变得没有特征，这样就可以躲过狗和盾的查杀。但是万变不离其宗，无论怎么变形，最终都会回到类似这样的格式：

```
$_GET($_POST)

```

分为执行数据部分(`$_GET`)和传递数据的部分(`$_POST`)，也就是说，无论怎么变形，在执行的过程中都会变成这个样子，接下来还是去执行类似`system()`,`exec()`,`eval()`等等函数，那么我们就直接定位到这里，检测该脚本是否调用危险函数，或是在脚本调用这些函数的时候进行分析，判断该脚本是否为非法用户的shell，会取到很不错的防御效果。

0x01 如何获取先机
===========

* * *

既然分析出来了问题的根结，那么下一步就是要控制住这些危险函数的入口点，即`system()`等函数的底层入口，就像`Windows API`中`hook`掉`zw`系列函数一样，我们也要`hook`掉`system()`这些函数。

这里我们需要用到`PHP Extension`， 即PHP扩展，位于PHP内核zend和PHP应用代码之间，很明显，扩展可以监控应用层代码的执行细节，也可以调用内核提供的ZEND API接口，包括禁用类、禁用函数等等。图为PHP结合其他必要组件的基本结构。

![](http://drops.javaweb.org/uploads/images/c11eb8da0b0a705f058d21da59d473eeb04dd5eb.jpg)

在ZEND中提供了接口供我们进行这样的操作，通过`zend_set_user_opcode_handler`就可以达到目的，根据某大牛所说，只需要`hook`三个`OPCODE`即可。

```
ZEND_INCLUDE_OR_EVAL        处理eval()、require等
ZEND_DO_FCALL               函数执行system()等
ZEND_DO_FCALL_BY_NAME       变量函数执行 $func = "system";$func();等

```

以`ZEND_DO_FCALL`为例，在`MINIT`中将`ZEND_DO_FCALL`替换掉：

```
zend_set_user_opcode_handler(ZEND_DO_FCALL, LIGHT_DO_FCALL);

```

接着定义自己的处理函数，这里是`LIGHT_DO_FCALL`。

```
static int LIGHT_DO_FCALL(ZEND_OPCODE_HANDLER_ARGS)
{
    /* 检测是否为合法调用 */

    if (/*非法调用*/)
    {
        /*拦截掉，不执行。*/
    }
    else
    {
        /*合法调用，继续执行*/
        return ZEND_USER_OPCODE_DISPATHC;
    }   
}

```

这样一个骨架就完成了，其余的内容可以自行添加。这样每当调用`system()`等函数时，都会经过你自己的`LIGHT_DO_FCALL`，于是就可以对上层的代码执行进行检查了。

0x02 上面的方法太粗暴
=============

* * *

上面的方法固然是好，但是误判会很多，甚至一个普通的函数调用都会直接被ban掉。这样的WAF放在业务中一定会被喷出翔的。我们需要换个思路。

之前已经说过了，无论如何变形、加密、隐藏关键字等，最终都需要调用到`system()`，`eval()`等函数，终究是逃不过这些的。那么我们把刚才的思路的变一下，不要直接hook那几个`OPCODE`，向上走一层。

`eval()`函数在底层是要调用`zend_compile_string`函数的，那么我们是不是可以在底层重载掉`zend_compile_string`函数，或是用自己的函数替换掉呢？答案肯定是可以的，我们只需要重写自己的`zend_compile_string`函数即可。

但是对于`system`来说有些不一样，上面我们hook掉了`ZEND_DO_FCALL`，但是太粗暴了，我们这里可以在`function_table`中删除掉`system`，并用我们自己的函数注册`system`函数，这样就可以做到了实时检查，如果为合法调用，可以调用旧的`system`函数并继续执行。

很明显这样做的话，确实减少了误杀，但是也增加了风险，因为除了`system()`之外还有很多可以用于执行命令的函数。除了执行命令，还有遍历目录、读敏感文件的问题，需要考虑很多的方面，偏僻的函数都要考虑在内，还有`PHP SPL`、`DirectoryIterator`等等各种方面。

0x03 说了这么多我们看看实际效果吧
===================

* * *

我们来看看hook三个`OPCODE`的方式会产生什么样子的效果。首先我们在`MINIT`函数中将这三个`OPCODE`的处理函数换成我们自己的。

```
ZEND_MINIT_FUNCTION(lightWAF)
{
    /*
     * hook掉ZEND_DO_FCALL
     * 处理system函数等
     */
    zend_set_user_opcode_handler(ZEND_DO_FCALL, LIGHT_DO_FCALL);

    /*
     * hook掉ZEND_DO_FCALL_BY_NAME
     * 处理$func='system';$func();等类型
     */
    zend_set_user_opcode_handler(ZEND_DO_FCALL_BY_NAME, LIGHT_DO_FCALL_BY_NAME);

    /*
     * hook掉ZEND_INCLUDE_OR_EVAL
     * 处理eval, require等
     */
    zend_set_user_opcode_handler(ZEND_INCLUDE_OR_EVAL, LIGHT_INCLUDE_OR_EVAL);

    return SUCCESS;
}

```

`LIGHT_DO_FCALL`，`LIGHT_DO_FCALL_BY_NAME`，`LIGHT_INCLUDE_OR_EVAL`的内容类似，均为判断脚本文件是否在`upload`目录中，如果在的话就禁止危险函数的执行，否则放行。这里我们用`LIGHT_DO_FCALL`说明一下：

```
/* LIGHT_DO_FCALL */
static int LIGHT_DO_FCALL(ZEND_OPCODE_HANDLER_ARGS)
{
    char *filePath;

    filePath = zend_get_executed_filename(TSRMLS_C);
    php_printf("[Debug] filePath: %s\n<br />", filePath);

    if (strstr(filePath, "/upload/"))
    {
        /* 非法调用，拦截 */   
        php_printf("[Warning] Execute command via system() etc.\n<br />");
        return ZEND_USER_OPCODE_RETURN;
    }
    else    /* Not Found */
    {
        /* 合法调用，放行 */
        return ZEND_USER_OPCODE_DISPATCH;
    }
}

```

这里我们看到，一旦检测到在`upload`目录中，就返回`ZEND_USER_OPCODE_RETURN`，实际作用就是不继续执行危险函数了，如果不在`upload`目录中，就返回`ZEND_USER_OPCODE_DISPATCH`，实际作用就是继续执行该函数。

扩展编写完成后，编译即可得到`so`文件，如果对PHP扩展开发以及编译不熟悉的同学，请参考这个扩展开发教程的第五章：http://www.walu.cc/phpbook/ ，开发方面的知识超出了本文的内容，所以这里不再赘述了。

编译完成后，将得到的lightWAF.so文件复制到php的扩展目录下，我这里是`/usr/local/php/lib/php/extensions/`，根据自己的实际情况进行调整。接下来修改`php.ini`，让PHP自动加载我们的扩展，在其中加上一行：

```
extension=/path/to/our/lightWAF.so

```

我这里是：

```
extension=/usr/local/php/lib/php/extensions/lightWAF.so

```

根据之前so文件放的位置不同，请自行修改路径。

![](http://drops.javaweb.org/uploads/images/28f57b255df48a491c2ca80ef0809ec272900101.jpg)

最后我们重启`PHP`服务，让设置生效。`PHP`重启完成后，在终端中执行`php -m`，来验证扩展是否加载成功，如果在结果中看到了`lightWAF`，则说明加载成功。（请无视图中的错误信息，那个是我本地环境的问题，对`lightWAF`以及`PHP`没什么影响）

![](http://drops.javaweb.org/uploads/images/ed97bf4c4b9fecdc253e63e6782be1ddc0939b0f.jpg)

成功加载后，我们看一下实际效果，这里有一个上传文件的页面，可以上传任何类型的文件并将上传的文件保存在upload目录中。现在模拟一下getshell的过程。

![上传页面](http://drops.javaweb.org/uploads/images/71aee02fc6f66491109382194714e84f78dbc264.jpg)

我们写个小马，内容如下：

```
<?php
    system($_GET["cmd"]);
?>

```

进行上传，并访问shell，结果如下：

![](http://drops.javaweb.org/uploads/images/e6327fd8cf9639840b6cdd301a9e83c49613c439.jpg)

可以看到被成功拦截了，好吧，我们换只牛逼的马儿，试试反射型的。

```
<?php
    $func = new ReflectionFunction("system");
    echo $func->invokeArgs(array("$_GET[c][/c]"));
?>

```

继续上传并访问，看看结果：

![](http://drops.javaweb.org/uploads/images/b7a56b59ff10909da9ef00340e380b47387b9844.jpg)

依然被拦截了，只不过这次触发的是`ZEND_DO_FCALL_BY_NAME`这个`OPCODE`。 接下来我们看看正常的文件会不会被拦截，在lightWAF目录下写入一个test.php，用于模拟正常的业务文件，内容如下：

```
<?php
    system('ls');
?>

```

访问一下看看结果：

![](http://drops.javaweb.org/uploads/images/74eb44a42b09749d48939ab99e4c807a9b35114a.jpg)

可以看到`ls`命令成功的执行了，也就是说我们的正常文件是不会被拦截的，而只有`upload`目录中的文件会被拦截，这样做又会引发另一个弊端，倘若攻击者通过某种方法将shell写入正常的文件中，或是与业务结合起来，那么这种防御手段就很难生效了。具体如何防御还要结合其他的特征进行检测，并不是没有办法了，实际应用中不能只依靠检测文件路径这一条规则，需要结合业务进行部署防御方案。

另一种方法与这个hook三个`OPCODE`的方法类似，无非就是麻烦一点，感兴趣的同学可以围观下面的参考文献：http://security.tencent.com/index.php/blog/msg/19 ，这里描述了hook函数的比较详细的思路。

0x04 不谈业务的安全都是耍流氓
=================

* * *

总结一下，拦截的方法大概就是上面两种，但是拦截的依据还没有决定，如何判断一个调用`system()`的脚本是否为`webshell`呢？如果我们的WAF放到生产环境，啥都不管乱杀，很有可能造成正常的业务无法工作。我自己总结了几个方法，可能联合起来使用效果更好一些。

*   根据目录判断 通常情况下，上传的文件一般都有专门的目录进行存放，例如`upload/`等，正常的业务文件是不在这其中的，于是我们可以简单的只对这个目录进行处理，其他目录的文件一律放行。
    
*   根据文件权限判断 这需要网站的维护者对网站的权限进行严格的控制，例如，所有的`web`文件均是`644`，且为`root:root`所有。上传的文件为`www:www`所有，根据权限的不同进行查杀，对于默认的`web`文件进行放行，对属于非`root:root`的文件进行查杀。也可以根据`w`标志判断，通过未知方式`getshell`的文件很多是带有`w`标志的，所以可以根据这些特征进行查杀。
    
*   变形检测 如果发现一个文件调用了`assert`、`system`、`preg_replace /e`等等，但是在源文件中没有发现这些关键字，还等什么，这个文件很大的可能就是`shell`了。（`zend_get_executed_filename`可以获得文件的标志以及文件的路径，例如出现了`assert`，说明该脚本使用了`assert`执行代码。）
    
*   黑名单检测 就像传统的杀软一样，总会有那么一部分的特征病毒库，我们也可以建立一部分的`webshell`特征库，先依靠特征库杀掉一部分，再根据其他的情况进行判断。如果将动态检测和静态检测结合起来，查杀、拦截效果应当都会有显著的改善。
    

0x05 所以这WAF有啥用
==============

* * *

安全需要和业务结合起来进行，不谈业务的安全都是耍流氓。因为是扩展级别的WAF，在部署的时候可能需要重新编译，修改配置文件等等。批量式部署可能显得不是那么方便，而且要根据业务需要进行各种细微的调整。如果仅仅是几台服务器，相信这种WAF还是十分棒的，调整起来也十分方便。

如果能开发出适合批量部署的基于扩展的WAF，那么可能会比较容易普及，毕竟在业务上部署WAF不是一个简单的事情。

*   参考资料：

http://security.tencent.com/index.php/blog/msg/57 http://security.tencent.com/index.php/blog/msg/19 http://www.walu.cc/phpbook/ http://www.php-internals.com/book/?p=index http://www.nowamagic.net/librarys/veda/detail/1543