# Bandit Walkthrough

0x00 Introduction
=================

* * *

overthewire是一个wargame网站，网址：http://overthewire.org/wargames/。其中bandit是最简单的系列，主要是考察一些基本的Linux操作。作为一个Linux初学者，我花了两个星期左右把它“通关”了。下面逐关讲解。网上也能搜到很多相关攻略，所以这篇文章一部分目的是为了进行一下复习。想看直接看密码的可以直接跳到最后。

Level 0->Levle 1
================

* * *

```
Level Goal

The goal of this level is for you to log into the game using SSH. The host to which you need to connect is bandit.labs.overthewire.org. The username is bandit0 and the password is bandit0. Once logged in, go to the Level 1 page to find out how to beat Level 1.

```

这一关不用多说，直接ssh连接上目标主机，ssh命令可以直接谷歌。

```
ssh  bandit.labs.overthewire.org -l bandit0

```

然后密码在readme里面。

Level 1 → Level 2
=================

* * *

```
Level Goal

The password for the next level is stored in a file called - located in the home directory

```

这一关主要是cat的使用，但是因为文件名是一个'-'，所以不能直接cat。根据下面提示直接谷歌，输入以下命令解决。

```
cat ./-

```

得到密码 CV1DtqXWVFXTvM2F0k09SHz0YwRINYA9

Level 2 → Level 3
=================

* * *

```
Level Goal

The password for the next level is stored in a file called spaces in this filename located in the home directory

```

这一关是文件名有空格,直接加双引号。

```
cat "spaces in this filename"

```

Level 3 → Level 4
=================

* * *

```
Level Goal

The password for the next level is stored in a hidden file in the inhere directory.

```

这一关是一个隐藏文件，直接利用ll -a命令。不多说。

Level 4 → Level 5
=================

* * *

```
Level Goal

The password for the next level is stored in the only human-readable file in the inhere directory. Tip: if your terminal is messed up, try the “reset” command.

```

这一关就是不断使用cat ./-file0x然后观察，最后发现在-file07里面。

Level 5 → Level 6
=================

* * *

```
Level Goal

The password for the next level is stored in a file somewhere under the inhere directory and has all of the following properties: - human-readable - 1033 bytes in size - not executable

```

这一关是关于find和du命令的使用。由于文件具有1033的大小,通过找男人（man)命令查看du的手册，发现可以通过

```
du -ab | grep 1033

```

命令可以发现要找的文件就是 inhere/maybehere07/.file2 然后cat就可以了。

Level 6 → Level 7
=================

* * *

```
Level Goal

The password for the next level is stored somewhere on the server and has all of the following properties: - owned by user bandit7 - owned by group bandit6 - 33 bytes in size

```

仍然是find和du的使用。查看find的手册，用以下命令可以达到目的：

```
    find -group bandit6 -user bandit7 -size 33c

```

以上命令就是根据题目所给的条件进行筛选，具体查看手册33c表示是33bytes。

Level 7 → Level 8
=================

* * *

```
Level Goal

The password for the next level is stored in the file data.txt next to the word millionth

```

这一关是grep的使用。直接

```
grep millionth data.txt

```

就可得到密码。这个题目里面密码和匹配模式在同一行，所以可以直接grep。如果并不是在同一行还要加其他参数。其实这道题我解的时候直接cat，然后不小心就看到了密码（data.txt比较短）（逃。

Level 8 → Level 9
=================

* * *

```
Level Goal

The password for the next level is stored in the file data.txt and is the only line of text that occurs only once

```

这一关难度增加了一点点，不过毕竟是基础训练。这里要用到“管道”的知识，具体请谷歌^^; 直接用：

```
sort data.txt | uniq -u

```

轻松搞定。

Level 9 → Level 10
==================

* * *

```
Level Goal

The password for the next level is stored in the file data.txt in one of the few human-readable strings, beginning with several ‘=’ characters.

```

仍然是grep的应用。如果仅仅是想过关的话也可以人肉搜索。如果用grep的话可以这样

```
cat data.txt | grep == -a

```

加-a是为了让grep强行将文件判定为文本文档。

Level 10 → Level 11
===================

* * *

```
Level Goal

The password for the next level is stored in the file data.txt, which contains base64 encoded data

```

既然说了是base64,那就：

```
base64 data.txt -d

```

好，下一关

Level 11 → Level 12
===================

* * *

```
Level Goal

The password for the next level is stored in the file data.txt, where all lowercase (a-z) and uppercase (A-Z) letters have been rotated by 13 positions

```

这是一个移位13位的凯撒密码，最初我是用python来解密的，后来谷歌了一下用shell也可以

```
echo "The Quick Brown Fox Jumps Over The Lazy Dog" | tr 'A-Za-z' 'N-ZA-Mn-za-m'

```

在这个题目则可以这样

```
 cat data.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m'

```

所以shell脚本有时候还是挺好用的。ps:tr是translate的缩写。

Level 12 → Level 13
===================

* * *

```
Level Goal

The password for the next level is stored in the file data.txt, which is a hexdump of a file that has been repeatedly compressed. For this level it may be useful to create a directory under /tmp in which you can work using mkdir. For example: mkdir /tmp/myname123. Then copy the datafile using cp, and rename it using mv (read the manpages!)

```

这关主要是考察各种解包工具的使用。首先将hexdump还原成文件：

```
xdd -d data.txt > out

```

然后接下来不断用file命令和对应的解包命令就可以了，boring...

Level 13 → Level 14
===================

* * *

```
Level Goal

The password for the next level is stored in /etc/bandit_pass/bandit14 and can only be read by user bandit14. For this level, you don’t get the next password, but you get a private SSH key that can be used to log into the next level. Note: localhost is a hostname that refers to the machine you are working on

```

这一关是SSH命令的另一种用法。之前我们都是用密码登录的，这次要用私钥登录。并没有什么难度，加上-i选项后面跟上密钥文件就可以了。

Level 14 → Level 15
===================

* * *

```
Level Goal

The password for the next level can be retrieved by submitting the password of the current level to port 30000 on localhost.

```

这一关要求你想本机30000端口发送这一关的密码来获取下一关的密码。可以通过各种方法实现，比如自己写程序。当然也可以使用netcat实现这一功能。

```
nc localhost 30000 < /etc/bandit_pass/bandit14

```

Level 15 → Level 16
===================

* * *

```
Level Goal

The password for the next level can be retrieved by submitting the password of the current level to port 30001 on localhost using SSL encryption.

```

这一关换了一个花样，要求使用ssl加密来传输密码。可以使用s_client命令。

```
 openssl s_client -connect localhost:30001 -quiet </etc/bandit_pass/bandit15

```

至于为什么要用-quiet，请看man。

Level 16 → Level 17
===================

* * *

```
Level Goal

The password for the next level can be retrieved by submitting the password of the current level to a port on localhost in the range 31000 to 32000. First find out which of these ports have a server listening on them. Then find out which of those speak SSL and which don’t. There is only 1 server that will give the next password, the others will simply send back to you whatever you send to it.

```

Oops，这次题目只给了一个端口范围，那就可以用namp来扫描一下。推荐看一下nmap的man，内容很详细，也介绍了一些扫描的原理。

首先,扫描一下：

```
nmap -A -p31000-32000 localhost

```

得到以下结果：

```
PORT      STATE SERVICE VERSION
31046/tcp open  echo
31518/tcp open  msdtc   Microsoft Distributed Transaction Coordinator (error)
31691/tcp open  echo
31790/tcp open  msdtc   Microsoft Distributed Transaction Coordinator (error)
31960/tcp open  echo

```

我们可以看到两种服务类型，一种是echo，顾名思义就是直接将你发给他的东西扔回来。那另外一种服务就是我们关心的了。我们尝试分别给这两个端口发送密码。

然后我们发现31790端口是我们想要的，得到如下key:

```
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAvmOkuifmMg6HL2YPIOjon6iWfbp7c3jx34YkYWqUH57SUdyJ
imZzeyGC0gtZPGujUSxiJSWI/oTqexh+cAMTSMlOJf7+BrJObArnxd9Y7YT2bRPQ
Ja6Lzb558YW3FZl87ORiO+rW4LCDCNd2lUvLE/GL2GWyuKN0K5iCd5TbtJzEkQTu
DSt2mcNn4rhAL+JFr56o4T6z8WWAW18BR6yGrMq7Q/kALHYW3OekePQAzL0VUYbW
JGTi65CxbCnzc/w4+mqQyvmzpWtMAzJTzAzQxNbkR2MBGySxDLrjg0LWN6sK7wNX
x0YVztz/zbIkPjfkU1jHS+9EbVNj+D1XFOJuaQIDAQABAoIBABagpxpM1aoLWfvD
KHcj10nqcoBc4oE11aFYQwik7xfW+24pRNuDE6SFthOar69jp5RlLwD1NhPx3iBl
J9nOM8OJ0VToum43UOS8YxF8WwhXriYGnc1sskbwpXOUDc9uX4+UESzH22P29ovd
d8WErY0gPxun8pbJLmxkAtWNhpMvfe0050vk9TL5wqbu9AlbssgTcCXkMQnPw9nC
YNN6DDP2lbcBrvgT9YCNL6C+ZKufD52yOQ9qOkwFTEQpjtF4uNtJom+asvlpmS8A
vLY9r60wYSvmZhNqBUrj7lyCtXMIu1kkd4w7F77k+DjHoAXyxcUp1DGL51sOmama
+TOWWgECgYEA8JtPxP0GRJ+IQkX262jM3dEIkza8ky5moIwUqYdsx0NxHgRRhORT
8c8hAuRBb2G82so8vUHk/fur85OEfc9TncnCY2crpoqsghifKLxrLgtT+qDpfZnx
SatLdt8GfQ85yA7hnWWJ2MxF3NaeSDm75Lsm+tBbAiyc9P2jGRNtMSkCgYEAypHd
HCctNi/FwjulhttFx/rHYKhLidZDFYeiE/v45bN4yFm8x7R/b0iE7KaszX+Exdvt
SghaTdcG0Knyw1bpJVyusavPzpaJMjdJ6tcFhVAbAjm7enCIvGCSx+X3l5SiWg0A
R57hJglezIiVjv3aGwHwvlZvtszK6zV6oXFAu0ECgYAbjo46T4hyP5tJi93V5HDi
Ttiek7xRVxUl+iU7rWkGAXFpMLFteQEsRr7PJ/lemmEY5eTDAFMLy9FL2m9oQWCg
R8VdwSk8r9FGLS+9aKcV5PI/WEKlwgXinB3OhYimtiG2Cg5JCqIZFHxD6MjEGOiu
L8ktHMPvodBwNsSBULpG0QKBgBAplTfC1HOnWiMGOU3KPwYWt0O6CdTkmJOmL8Ni
blh9elyZ9FsGxsgtRBXRsqXuz7wtsQAgLHxbdLq/ZJQ7YfzOKU4ZxEnabvXnvWkU
YOdjHdSOoKvDQNWu6ucyLRAWFuISeXw9a/9p7ftpxm0TSgyvmfLF2MIAEwyzRqaM
77pBAoGAMmjmIJdjp+Ez8duyn3ieo36yrttF5NSsJLAbxFpdlc1gvtGCWW+9Cq0b
dxviW8+TFVEBl1O4f7HVm6EpTscdDxU+bCXWkfjuRb7Dy9GOtt9JPsX8MBTakzh3
vBgsyi/sN3RqRBcGU40fOoZyfAMT8s1m/uYv52O6IgeuZ/ujbjY=

-----END RSA PRIVATE KEY-----

```

这个就是SSL的私钥，将它保存起来，用ssh连接。。。然后你会发现Ooops!

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

```

好吧，看来还要修改权限，用chmod 400修改文件的权限，然后成功进入下一关。

Level 17 → Level 18
===================

* * *

```
Level Goal

There are 2 files in the homedirectory: passwords.old and passwords.new. The password for the next level is in passwords.new and is the only line that has been changed between passwords.old and passwords.new

```

考察diff命令的用法，恩，我想不用多说了。

Level 18 → Level 19
===================

* * *

```
Level Goal

The password for the next level is stored in a file readme in the homedirectory. Unfortunately, someone has modified .bashrc to log you out when you log in with SSH.

```

这一关你无法正常登陆，但是没关系，ssh支持直接执行命令，既然我们知道密码就存在~/readme里面，那就容易了。

```
ssh localhost -l bandit18 "cat ~/readme"

```

Level 19 → Level 20
===================

* * *

```
Level Goal

To gain access to the next level, you should use the setuid binary in the homedirectory. Execute it without arguments to find out how to use it. The password for this level can be found in the usual place (/etc/bandit_pass), after you have used to setuid binary.

```

目录下面有一个bandit20-do的程序，可以以bandit20的权限执行命令，那么我们就可以借此来查看bandit20的密码：

```
./bandit20-do cat /etc/bandit_pass/bandit20

```

Bandit Level 20 → Level 21

```
Level Goal

There is a setuid binary in the homedirectory that does the following: it makes a connection to localhost on the port you specify as a commandline argument. It then reads a line of text from the connection and compares it to the password in the previous level (bandit20). If the password is correct, it will transmit the password for the next level (bandit21).

```

这次要分两步，先用nc运行一个进程进行监听，让程序来连接。

```
nc localhost 40000 -l < /etc/bandit_pass/bandit20

```

端口任意

然后用本关给的程序进行连接：

```
 ./suconnect 40000

```

Level 21 → Level 22
===================

* * *

```
Level Goal

A program is running automatically at regular intervals from cron, the time-based job scheduler. Look in /etc/cron.d/ for the configuration and see what command is being executed.

```

这一关开始就要用到cron相关的程序，cron就是相当于任务计划之类的东西。 进入/etc/cron.d目录。发现好多文件。刚开始我直接傻眼了，在这一关卡了好久。后来直接找与bandit21关最相近的文件，那就是cronjob_bandit22。cat一下，里面是运行一段脚本。看下脚本里面的内容

```
cat /etc/bandit_pass/bandit22 > /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv

```

看来密码就在/tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv这个文件里面

Bandit Level 22 → Level 23
==========================

* * *

Level Goal

A program is running automatically at regular intervals from cron, the time-based job scheduler. Look in /etc/cron.d/ for the configuration and see what command is being executed.

仍然是cron。进入刚才的目录，然后看下cronjob_bandit23的内容，仍然是一段脚本，看脚本内容：

```
myname=$(whoami)
mytarget=$(echo I am user $myname | md5sum | cut -d ' ' -f 1)

echo "Copying passwordfile /etc/bandit_pass/$myname to /tmp/$mytarget"

cat /etc/bandit_pass/$myname > /tmp/$mytarget

```

看来脚本是将bandit23的密码存进了/tmp/$mytarget文件里面，关键就是找出mytarget的值。为了得出这个值，可将脚本copy一份，将myname=bandit23。然后将后面两行去掉，直接echo mytarget就可得到存储密码的文件名。

Level 23 → Level 24
===================

```
Level Goal

A program is running automatically at regular intervals from cron, the time-based job scheduler. Look in /etc/cron.d/ for the configuration and see what command is being executed.

```

废话不多说，直接看脚本内容：

```
myname=$(whoami)

cd /var/spool/$myname
echo "Executing and deleting all scripts in /var/spool/$myname:"
for i in * .*;
do
    if [ "$i" != "." -a "$i" != ".." ];
    then
        echo "Handling $i"
        timeout -s 9 60 "./$i"
     rm -f "./$i"
    fi
done

```

可以看出来以上脚本会将/var/spool/bandit24文件夹下的所有文件执行一遍并清除。根据crontab可知每分钟执行一次。那就好办了，我们将写好的脚本放入这个文件夹，bandit24每分钟就会执行脚本，而这个脚本具有bandit24的权限。恩，你懂的。

```
cat /etc/bandit_pass/bandit24 > /tmp/save/pass

```

先在/tmp下新建save文件夹，chmod 777 ，然后将以上脚本放入上述文件夹里面，等一分钟。泡一杯咖啡，丁！去/tmp/save/文件夹下可以看见pass。如果发现没有任何东西，请考虑权限问题(chmod)。

Bandit Level 24 → Level 25

```
Level Goal

A daemon is listening on port 30002 and will give you the password for bandit25 if given the password for bandit24 and a secret numeric 4-digit pincode. There is no way to retrieve the pincode except by going through all of the 10000 combinaties, called brute-forcing.

```

这是比较有意思的一关，写一个脚本进行穷举,于是我一开始写了一下这个：

```
pass=UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ
for i in $(seq 0 9999)
do
if
    echo $pass $i| nc localhost 30002 | grep Wrong>/dev/null
then
    echo $i
else

    echo $pass $i| nc localhost 30002 > result
    break
fi
done

```

运行这个脚本，然后你就可以去打几把DOTA了，反正我是挂了一晚上。。。。。 这样当然不行啊，所以就有了后来的改进版本：

```
pass=UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ
for i in $(seq 0 9999)
do {
if
    echo $pass $i| nc localhost 30002 | grep Wrong > /dev/null
then
    echo $i
else

    echo $pass $i| nc localhost 30002 > result
    exit
fi
}&
done
wait

```

这里用了&和wait实现了伪多线程。&表示可以并行执行，wait表示父进程等待子进程执行完毕。 这样果然快多了 ，只用了几分钟就搞定了。

然而这个脚本并不能在找到正确的密码的时候停止，这个就作为思考题吧。

Level 25 → Level 26
===================

* * *

```
Level Goal

Logging in to bandit26 from bandit25 should be fairly easy… The shell for user bandit26 is not /bin/bash, but something else. Find out what it is, how it works and how to break out of it.

```

这道题，，额，，只能说脑冻好大。

用home目录下的sshkey登陆，Oops:

```
 _                     _ _ _   ___   __
| |                   | (_) | |__ \ / /
| |__   __ _ _ __   __| |_| |_   ) / /_
| '_ \ / _` | '_ \ / _` | | __| / / '_ \
| |_) | (_| | | | | (_| | | |_ / /| (_) |
|_.__/ \__,_|_| |_|\__,_|_|\__|____\___/

```

扔给我这样一个东西。。。 坑爹呢！

```
grep bandit26 /etc/passwd

```

运行以上命令，

```
bandit26:x:11026:11026:bandit level 26:/home/bandit26:/usr/bin/showtext

```

那么/usr/bin/showtext又是什么鬼

```
more ~/text.txt
exit 0

```

好吧，原来是这样，用的是more程序。

step1:将终端窗口缩小到只有两行

step2:登陆

step3:这时More会阻塞（因为没有显示完）

step4:按v键，进入vim编辑器

step5::r /etc/bandit_pass/bandit26

我真是太tm机智了。

附录
==

* * *

```
level2:UmHadQclWmgdLOKQ3YNgjWxGoRMb5luK
level3:pIwrPrtPN36QITSp3EQaw936yaFoFgAB
level4:koReBOKuIDDepwhWk7jZC0RTdopnAYKh
level5:DXjZPULLxYr17uwoI01bNLQbtFemEgo7
level6:HKBPTKQnIay4Fw76bEy8PVxKEDQRKTzs
level7:cvX2JJa4CFALtqS87jk27qwqGhBM9plV
level8:UsvVyFSfZZWbi6wgC7dAFyFuR6jQQUhR
level9:truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk
level10:IFukwKGsFW8MOq3IRFqrxE1hxTNEbUPR
level11:5Te8Y4drgCRfCx8ugdwuEX8KFC6k2EUu
level12:8ZjyCRiBWFYkneahHwxCv3wb2a1ORpYL
level13:ssh bandit14@localhost -i sshkey.private
level14:BfMYroe26WYalil77FoDi9qh59eK5xNr
level15:cluFn7wTiGryunymYOu4RcffSxQluehd
level17:kfBf3eYk5BPBRzwjqutbbfE887SVc5Yd
level18:IueksS7Ubh8G3DCwVzrTd8rAVOwq3M5x
level19:GbKksEFF4yrVs6il55v6gwY5aVje5f0j
level20:gE269g2h3mw3pwgrj0Ha9Uoqen1c9DGr
level21:Yk7owGAcWjwMVRwrTesJEwB7WVOiILLI
level22:jc1udXuA1tiHqjIsL8yaapX5XIAI6i0n
level23:UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ
level24:uNG9O58gUE7snukf3bvZ0rxhtnjzSGzG 
level25:5czgV9L3Xx8JPOyRbXh6lQbmIOWvPT6Z

```