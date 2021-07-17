## Mail

**前提条件**

linux环境
putenv()、mail()可用

**基本原理**

当 disable_functions 禁用了命令执行函数，webshell 无法执行系统命令时，可以通过环境变量 LD_PRELOAD 劫持系统函数，来突破 disable_functions 限制执行操作系统命令

**利用步骤**

> https://github.com/ianxtianxt/bypass_disablefunc_via_LD_PRELOAD

* 下载bypass_disablefunc.php和bypass_disablefunc_x64.so,并上传到目标服务器
* 执行命令

```
http://www.baidu.com/bypass_disablefunc.php?cmd=pwd&outpath=/tmp/xx&sopath=/var/www/bypass_disablefunc_x64.so

```

* cmd: 执行的命令
* outpath: 读写权限目录
* sopath: so文件的绝对路径

