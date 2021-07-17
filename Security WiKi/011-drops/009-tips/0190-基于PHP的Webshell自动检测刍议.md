# 基于PHP的Webshell自动检测刍议

0x00 引言
=======

* * *

看到wooyun知识库上众多大神的精彩文章，深感自身LOW到爆，故苦思冥想找来一个题目，主要求邀请码一枚，以便以后继续学习。

对于网络维护人员来说，恐怕最头痛的就是网站被黑，还留下了后门，甚至连服务器都被提权。而Hacker通常在相对不易引人注目的地方留下后门。逐个排查感觉很吃力，那么，本文姑且探讨一下在PHP环境下的Webshell自动检测的可行方案。

0x01 关键词检测
==========

* * *

利用正则表达式等对一些常见的Webshell关键词进行扫描，从而判断出该文件是否为Webshell.这种检测方法真是太暴力了，也是最简单最传统的检测方式。显而易见，这样简单粗暴地检测会产生较高的误报率，而且对于一些加了密或者变形的Webshell又会出现检测不出来的问题。所以，这样筛选出来的Webshell还要经过网络维护人员的手动核实，查杀原则是：宁可错杀一百，不可放过一个。。。。

譬如下面这段在某网站Get的代码，据称是某在线Webshell查杀真实代码：

```
class scan{
private $directory = '.';
private $extension = array('php');
private $_files = array();
private $filelimit = 5000;
private $scan_hidden = true;
private $_self = '';
Private $_regex='(preg_replace.*\/e|`.*?\$.*?`|\bcreate_function\b|\bpassthru\b|\bshell_exec\b|\bexec\b|\bbase64_decode\b|\bedoced_46esab\b|\beval\b|\bsystem\b|\bproc_open\b|\bpopen\b|\bcurl_exec\b|\bcurl_multi_exec\b|\bparse_ini_file\b|\bshow_source\b|cmd\.exe|KAdot@ngs\.ru|小组|专用|提权|木马|PHP\s?反弹|shell\s?加强版|WScript\.shell|PHP\s?Shell|Eval\sPHP\sCode|Udp1-fsockopen|xxddos|Send\sFlow|fsockopen\('(udp|tcp)|SYN\sFlood)';
private $_shellcode='';
private $_shellcode_line=array();
private $_log_array= array();
private $_log_count=0;
private $action='';
private $taskid=0;
private $_tmp='';

```

0x02 对混淆Webshell的判断
===================

1. 信息熵
------

说到对加密的Webshell的判断,就不得不提到信息论。香农信息论的基本点是用随机变量或随机矢量来表示信源，运用概率论和随机过程的理论来研究信息。经过编码的Webshell文件包含大量随机内容或特殊信息，这种文件将产生更多的ASCII码，使用ASCII码计算文件的熵值会变大，即衡量了Webshell对于普通文件的不确定性。

![](http://drops.javaweb.org/uploads/images/ac4d919d13b0f4bd79cd50158f425040baa134fa.jpg)

公式说明：

*   其中，n为ASCII码，对于ASCII为127的字符(空格)的判断无意义，去除；Xn为第n位ASCII码在当前文件中出现的次数，S为当前脚本文件的总字符数。
*   熵值Info(A)越大，为Webshell的可能性越大。

有关信息熵的更多内容，可以参考：[https://en.wikipedia.org/wiki/Entropy_%28information_theory%29](https://en.wikipedia.org/wiki/Entropy_%28information_theory%29)

2. index of coincidence(IC,重合指数)
--------------------------------

这里再使用一种方法：设X为一个长度为n的密文字符串，我们用集合来表示这个密文字符串{X1,X2,…,Xn},X的重合指数是指随机抽取任意两个元素相同的概率。

设Ni为字符i在这份密文中出现的次数。从n个密文字符中抽取两个字符的方式有

![](http://drops.javaweb.org/uploads/images/d07fcce82a4c539bed1d449e628229fd649b529a.jpg)

而其中Ni个i组成一对的方式有

![](http://drops.javaweb.org/uploads/images/702a9d09ac73075aae02f572eb5597fff533ad4a.jpg)

于是，两式作比，即为从X中抽到两个字符都为i的概率。

加密文件的密文随机性变大，其重合指数变低。编码后的Webshell类似于随机文件，而明文的Webshell由于具有用于提权的类似随机字符串或者包含二进制、十六进制序列的内容，因此使用扩展的ASCII码作为研究对象，即计算254个字符（除去ASCII为127）的重合指数。那么对于脚本文件，如果重合指数越低，则为Webshell的可能性越大。

除上述介绍过的两种算法，还可以使用base64编码待检测脚本文件，对于加密的Webshell文件，由于base64编码消除了非ASCII的字符，这样实际上经base64编码过的件的字符就会具有这样的特征——更小且出现分布的不均衡，也就是说文件的压缩比会变大。通过这样的方式来检测Webshell的特征就是相对其他文件，具有更大的压缩比。

对于混淆的Webshell的判断，根据算法算出来的结果都是一些具体的数值，要根据实际设定好的阈值来进行比较，从而来判断是否为Webshell。而阈值的设定由于不同的网站并不相同，因此还要经过具体的测试。

0x03 基于PHP扩展的Webshell实时动态检测
===========================

* * *

这种检测方法在目前比较流行，主要由于该方法采用对PHP调用危险函数的HOOK，能够动态地检测出Webshell，相对比较实时，迅速。在一定程度上，弥补了传统Webshell静态检测的不足，也相对更为方便。

PHP在WEB容器内的运行方式主要有三种：模块加载方式运行，CGI或FastCGI方式运行，三种方法都要经过5个阶段：模块初始化，请求初始化，代码执行，请求结束，模块结束。在PHP的代码执行过程中，通过词法分析，将PHP代码转变为语言片段(tokens)，然后语法分析转化为有意义的表达式，最后将表达式编译为中间字节码(opcodes).中间字节码在Zend虚拟机执行，然后输出结果。

我们通过使用PHP内核提供的通用接口：`zend_set_user_opcode_handler`来修改中间字节码对应的处理函数，达到对PHP内核HOOK的效果。 函数原型：

```
int zend_set_user_opcode_handler(zend_uchar opcode,opcode_handler_t handler)

```

前者为需要的`opcode`;后者为`hook`后的处理函数。

一般将`ZEND_INCLUDE_OR_EVAL`，`ZEND_DO_FCALL`，`ZEND_DO_FCALL_BY_NAME`(参见下面举例函数)等处理函数在扩展中使用`zend_set_user_opcode_handler`进行处理。

攻击者通过任意文件上传漏洞将Webshell上传到目录中。那么在文件上传后进行访问时，通过对文件所在路径是否在黑白名单中进行判断，如果不符合黑白名单规则，则视为攻击并及时拦截。

潜在的可以HOOK的危险函数：

1.  命令执行类：passthru,system,popen,exec,shell_exec等
2.  文件系统类：fopen,opendir,dirname,pathinfo等
3.  数据库操作类：mysql_query,mysqli_query等
4.  回调函数：array_filter,array_reduce,usort,uksort等
5.  反射函数：ReflectionFunction

PHP扩展采用纯C编写，给出主要代码供参考：

```
#include“config.h”
#include“php.h”
#include“php_ini.h”
#include“ext/standard/info.h”
#include“php_waf.h”
static int le_waf;
const zend_function_entry waf_functions[] = {
PHP_FE(confirm_waf_compiled,NULL),PHP_FE_END };
zend_module_entry waf_module_entry = {
#if ZEND_MODULE_API_NO >= 20010901
STANDARD_MODULE_HEADER，
#endif
“waf”，
waf_functions,
PHP_MINIT(waf),
PHP_MSHUTDOWN(waf),
PHP_RINIT(waf),
PHP_RSHUTDOWN(waf),
PHP_MINFO(waf),
#if ZEND_MODULE_API_NO >= 20010901
PHP_WAF_VERSION,
#endif
STANDARD_MODULE_PROPERTIES
};
#ifdef COMPILE_DL_WAF
ZEND_GET_MODULE(waf);
#endif
PHP_MINIT_FUNCTION(waf)
{ zend_set_user_opcode_handler(ZEND_INCLUDE_OR_EVAL,manage); // hook eval等
zend_set_user_opcode_handler(ZEND_DO_FCALL_BY_NAME,manage); //hook变量函数执行
zend_set_user_opcode_handler(ZEND_DO_FCALL，manage); //hook命令执行
return SUCCESS;
}
int manage() /*HOOK处理函数*/
{ char* filepath = (char*)zend_get_executed_filename(TSRMLS_C);
if(strstr(filepath，”upload”))/*判断字符串“upload”是否是filepath的子串*/
{ php_printf(“请不要执行恶意代码<br>执行文件路径 ：%s”,filepath);
return ZEND_USER_OPCODE_RETURN;}
else
return ZEND_USER_OPCODE_DISPATCH;
}

```

0x04 总结
=======

* * *

除上述所采用的Webshell检测方法，目前还有基于网络的检测方式等。

例如，目前的研究有集中于在网络入口处配置IDS或者WAF来检测Webshell的方法。Fireeye[28]提出使用Snort配置特征规则来检测一句话木马.另有通过配置ModSecurty的核心规则集(CoreRule Sets)来检测上传Webshell的行为的方式。

上述两种方法都是通过分析http请求中是否包括特殊关键词(例如`<form`、`<％`、`<?`、`<php`等)来判断攻击者是否正在上传HTML或者脚本文件。这种判断方式对于已经存在的Webshell表现无力。