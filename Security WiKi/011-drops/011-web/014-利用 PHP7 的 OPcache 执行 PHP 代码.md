# 利用 PHP7 的 OPcache 执行 PHP 代码

from:http://blog.gosecure.ca/2016/04/27/binary-webshell-through-opcache-in-php-7/

在 PHP 7.0 发布之初，就有不少 PHP 开发人员对其性能提升方面非常关注。在引入 OPcache 后，PHP的性能的确有了很大的提升，之后，很多开发人员都开始采用 OPcache 作为 PHP 应用的加速器。OPcache 带来良好性能的同时也带来了新的安全隐患，下面的内容是 GoSecure 博客发表的一篇针对 PHP 7.0 的 OPcache 执行 PHP 代码的技术博文。

[本文](http://blog.gosecure.ca/2016/04/27/binary-webshell-through-opcache-in-php-7/)会介绍一种新的在 PHP7 中利用默认的 OPcache 引擎实施攻击的方式。利用此攻击向量，攻击者可以绕过“Web 目录禁止文件读写”的限制 ，也可以执行他自己的恶意代码。

0x00 OPcache 利用方式简介
===================

* * *

OPcache 是 PHP 7.0 中内建的缓存引擎。它通过编译 PHP 脚本文件为字节码，并将字节码放到内存中。

![](http://drops.javaweb.org/uploads/images/0cc96b39b2a7674fef956e08915c048aba49cbc4.jpg)

[使用 PHP7 加速 Web 应用](http://talks.php.net/confoo16#/php7pcache1)

OPcache 缓存文件格式请看[这里](http://jpauli.github.io/2015/03/05/opcache.html)。

同时，它在文件系统中也提供了缓存文件。  
在 PHP.ini 中配置如下，你需要指定一个缓存目录：

```
opcache.file_cache=/tmp/opcache

```

在指定的目录中，OPcache 存储了已编译的 PHP 脚本文件，这些缓存文件被放置在和 Web 目录一致的目录结构中。如，编译后的 /var/www/index.php 文件的缓存会被存储在 /tmp/opcache/[system_id]/var/www/index.php.bin 中。

**system_id**是当前 PHP 版本号，Zend 扩展版本号以及各个数据类型大小的 MD5 哈希值。在最新版的 Ubuntu(16.04)中，**system_id**是通过当前 Zend 和 PHP 的版本号计算出来的，其值为 81d80d78c6ef96b89afaadc7ffc5d7ea。这个哈希值很有可能被用来确保多个安装版本中二进制缓存文件的兼容性。当 OPcache 在第一次缓存文件时，上述目录就会被创建。  
在本文的后面，我们会看到每一个 OPcache 缓存文件的文件头里面都存储了**system_id**。  
有意思的是，运行 Web 服务的用户对 OPcache 缓存目录（如：/tmp/opcache/）里面的所有子目录以及文件都具有写权限。

```
$ ls /tmp/opcache/
drwx------ 4 www-data www-data 4096 Apr 26 09:16 81d80d78c6ef96b89afaadc7ffc5d7ea

```

正如你所看到的，www-data 用户对 OPcache 缓存目录有写权限，因此，我们可以通过使用一个已经编译过的 webshell 的缓存文件替换 OPcache 缓存目录中已有的缓存文件来达到执行恶意代码的目的。

0x01 OPcache 利用场景
=================

* * *

要利用 OPcache 执行代码，我们需要先找到 OPcache 的缓存目录（如：/tmp/opcache/[**system_id**]）以及 Web 目录（如：/var/www/）。  
假设，目标站点已经存在一个执行 phpinfo() 函数的文件了。通过这个文件，我们可以获得 OPcache 缓存目录， Web 目录，以及计算**system_id**所需的几个字段值。[我写了一个脚本，可以利用 phpinfo() 计算出 system_id](https://github.com/GoSecure/php7-opcache-override)。

另外还要注意，目标站点必须存在一个文件上传漏洞。  
假设 php.ini 配置 opcache 的选项如下：

```
opcache.validate_timestamp = 0   ; PHP 7 的默认值为 1
opcache.file_cache_only = 1      ; PHP 7 的默认值为 0
opcache.file_cache = /tmp/opcache

```

此时，我们可以利用上传漏洞将文件上传到 Web 目录，但是发现 Web 目录没有读写权限。这个时候，就可以通过替换 /tmp/opcache/[system_id]/var/www/index.php.bin 为一个 webshell的二进制缓存文件运行 webshell。

![](http://drops.javaweb.org/uploads/images/a7c86befed5cdaad7446a936c43cf02b5383567d.jpg)

1.  在本地创建 webshell 文件 index.php ，代码如下：
    
    ```
    <?php 
       system($_GET['cmd']); 
    ?>
    
    ```
2.  在 PHP.ini 文件中设置 opcache.file_cache 为你所想要指定的缓存目录
    
3.  运行 PHP 服务器(php -S 127.0.0.1:8080) ，然后向 index.php 发送请求(wget 127.0.0.1:8080)，触发缓存引擎进行文件缓存。
    
4.  打开你所设置的缓存目录，index.php.bin 文件即为编译后的 webshell 二进制缓存文件。
    
5.  修改 index.php.bin 文件头里的**system_id**为目标站点的**system_id**。在文件头里的签名部分的后面就是**system_id**的值。
    
    ![](http://drops.javaweb.org/uploads/images/59076043f8b8b38ea392b89446284afc5fd266d3.jpg)
    
6.  通过上传漏洞将修改后的 index.php.bin 上传至 /tmp/opcache/[system_id]/var/www/index.php.bin ，覆盖掉原来的 index.php.bin
    
7.  重新访问 index.php ，此时就运行了我们的 webshell
    
    ![](http://drops.javaweb.org/uploads/images/af1a8cccfe3d20917151078dbcff7379103e038b.jpg)
    

针对这种攻击方式，在 php.ini 至少有两种配置方式可以防御此类攻击。

*   禁用**file_cache_only**
*   启用**validate_timestamp**

0x02 绕过内存缓存(file_cache_only = 0)
================================

* * *

如果内存缓存方式的优先级高于文件缓存，那么重写后的 OPcache 文件（webshell）是不会被执行的。但是，当 Web 服务器重启后，就可以绕过此限制。因为，当服务器重启之后，内存中的缓存为空，此时，OPcache 会使用文件缓存的数据填充内存缓存的数据，这样，webshell 就可以被执行了。

但是这个方法比较鸡肋，需要服务器重启。那有没有办法不需要服务器重启就能执行 webshell 呢？

后来，我发现在诸如 WordPress 等这类框架里面，有许多过时不用的文件依旧在发布的版本中能够访问。如： registration-functions.php

由于这些文件过时了，所以这些文件在 Web 服务器运行时是不会被加载的，这也就意味着这些文件没有任何文件或内存的缓存内容。这种情况下，通过上传 webshell 的二进制缓存文件为 registration-functions.php.bin ，之后请求访问 /wp-includes/registration-functions.php ，此时 OPcache 就会加载我们所上传的 registration-functions.php.bin 缓存文件。

0x03 绕过时间戳校验(validate_timestamps = 1)
=====================================

* * *

如果服务器启用了时间戳校验，OPcache 会将被请求访问的 php 源文件的时间戳与对应的缓存文件的时间戳进行对比校验。如果两个时间戳不匹配，缓存文件将被丢弃，并且重新生成一份新的缓存文件。要想绕过此限制，攻击者必须知道目标源文件的时间戳。  
如上面所说的，在 WordPress 这类框架里面，很多源文件的时间戳在解压 zip 或 tar 包的时候都是不会变的。

![](http://drops.javaweb.org/uploads/images/ecde92d769588018f4026a73bf8e5a5566c388c8.jpg)

注意观察上图，你会发现有些文件从2012年之后从没有被修改过，如：registration-functions.php 和 registration.php 。因此，这些文件在 WordPress 的多个版本中都是一样的。知道了时间戳，攻击者就可以绕过 validate_timestamps 限制，成功覆盖缓存文件，执行 webshell。二进制缓存文件的时间戳在 34字节偏移处。

![](http://drops.javaweb.org/uploads/images/4be870e0454c6fe9351bd5a58aa07ec6e5637dd0.jpg)

0x04 总结
=======

* * *

OPcache 这种新的攻击向量提供了一些绕过限制的攻击方式。但是它并非一种通用的 PHP 漏洞。随着 PHP 7.0 的普及率不断提升，你将很有必要审计你的代码，避免出现上传漏洞。并且检查可能出现的危险配置项。