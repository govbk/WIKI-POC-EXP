# fail2ban防暴力破解介绍使用

0x00 介绍
-------

* * *

fail2ban可以监视你的系统日志，然后匹配日志的错误信息（正则式匹配）执行相应的屏蔽动作（一般情况下是调用防火墙iptables屏蔽），如:当有人在试探你的SSH、SMTP、FTP密码，只要达到你预设的次数，fail2ban就会调用防火墙屏蔽这个IP，而且可以发送e-mail通知系统管理员，是一款很实用、很强大的软件！

fail2ban由python语言开发，基于logwatch、gamin、iptables、tcp-wrapper、shorewall等。如果想要发送邮件通知道，那还需要安装postfix或sendmail。

fail2ban在pycon2014中演讲，是一个相对成熟的第三方软件。附上大会ppt部分内容：fail2ban-pycon2014.pdf。

百度盘：[http://pan.baidu.com/s/1qWBHHBe](http://pan.baidu.com/s/1qWBHHBe)

0x01安装
------

* * *

1） apt-get 安装

```
apt-get install fail2ban log watch gamin

```

2) yum安装

```
yum install fail2ban logwatch gamin

```

3) 源代码安装

[http://www.fail2ban.org/wiki/index.php/Downloads](http://www.fail2ban.org/wiki/index.php/Downloads)

目前有两个版本：

```
stable    0.8.14 
beta       0.9.0

```

根据需要下载编译安装。

0x02 配置
-------

* * *

安装完成后配置文件在目录/etc/fail2ban/中：

```
/etc/fail2ban/fail2ban.conf  #fail2ban的配置文件
/etc/fail2ban/jail.conf #阻挡设定文件
/etc/fail2ban/filter.d/ #具体过滤规则文件目录 
/etc/fail2ban/action.d/ #具体过滤规则检测到后采取相对应措施的目录 

```

fail2ban默认有许多已经写好的规则，如ssh、ftp、proftpd等常见应用软件的支持，只需要设置enable属性为true即可启动，这里就不阐述了。

0x03 监控nginx日志
--------------

* * *

假设nginx默认日志路径为/var/log/nginx/access_log，需要防止黑客暴力破解HTTP FORM登陆，此登陆检测链接为

```
http://test.com/login_check.do

```

根据分析正常登陆一般不超过三四次，并且登陆时间一般也不超过一分钟；因此，规定检测周期为1分钟，最大尝试登陆次数为10次；在规定时间内超过指定次数则被认为是黑客在尝试暴力破解。

具体设置方法如下：

1) 首先在jail.conf文件下追加以下内容：

```
[nginx]    ;规则名字
enabled = true ;是否户用
port = http,https ;监控端口
filter = nginx    ;需要过滤匹配规则
logpath = /var/log/nginx/access_log; 日志路径
findtime =60    ;检测周期 单位秒 以下一样
bantime =300    ;iptable封禁IP时间
maxretry =10    ;最大尝试次数
action = iptables[name=nginx, port=http, protocal=tcp] ;发现暴力破解采取iptalbes封禁IP的措施
sendmail[name=nginx, dest=my-email@xx.com]    ;发现暴力破解后采取sendmail发送邮件的措施，需要注意的是：iptables和sendmail必须对齐，要不然会发生错误；不要问我为什么会知道，我先哭会儿-_-!!!

```

2)然后创建 /etc/fail2ban/filter.d/nginx.conf文件，并添加以下内容：

```
[Definition]
failregex =<HOST>.*-.*-.*POST.*/login_check.do.* HTTP\/1.*http://test.com.*$ ;需要匹配日志发现攻击行为的正则,<HOST>为fail2ban内置变量匹配IP，不可修改
ignoreregex =    ;需要忽略的正则

```

完成上述步骤就可以运行命令`/etc/init.d/fail2ban restart`重启了。查看iptables有fail2ban-nginx的规则和收到sendmail发送fail2ban已经启动的邮件就说明OK了。

不过运维的同学可能知道，sendmail发送邮件延迟很多，并不好用，使用mutt代替sendmail是个不错的选择。安装mutt的过程就不在时阐述了，这里介绍我修改使用mutt发送action的配置文件。

1)首先创建一个/etc/fail2ban/action.d/mutt.conf文件,然后添加以下内容:

```
# Fail2Ban configuration file
#
# Author: Cyril Jaquier
#
#
[Definition]
# Option: actionstart
# Notes.: command executed once at the start of Fail2Ban.
# Values: CMD
#
actionstart = printf %%b "Hi,\n
The jail <name> has been started successfully.\n
Regards,\n
Fail2Ban"|mutt -s "[Fail2Ban] <name>: started on `uname -n`"<dest>
# Option: actionstop
# Notes.: command executed once at the end of Fail2Ban
# Values: CMD
#
actionstop = printf %%b "Hi,\n
The jail <name> has been stopped.\n
Regards,\n
Fail2Ban"|mutt -s "[Fail2Ban] <name>: stopped on `uname -n`"<dest>
# Option: actioncheck
# Notes.: command executed once before each actionban command
# Values: CMD
#
actioncheck =
# Option: actionban
# Notes.: command executed when banning an IP. Take care that the
# command is executed with Fail2Ban user rights.
# Tags: See jail.conf(5) man page
# Values: CMD
#
actionban = printf %%b "Hi,\n
The IP <ip> has just been banned by Fail2Ban after
<failures> attempts against <name>.\n
Regards,\n
Fail2Ban"|mutt -s "[Fail2Ban] <name>: banned <ip> from `uname -n`"<dest>
# Option: actionunban
# Notes.: command executed when unbanning an IP. Take care that the
# command is executed with Fail2Ban user rights.
# Tags: See jail.conf(5) man page
# Values: CMD
#
actionunban =
[Init]
# Default name of the chain
#
name = default
# Destination/Addressee of the mutt
#
dest = root

```

2)然后在jail.conf文件下添加以下内容:

```
action = mutt[name=nginx, dest=my-email@xx.com]   

```

[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)名词是笔者自己翻译，可能表达的意思并不精确，请大牛们手下留情。有不对的地方欢迎指出，有兴趣的同学也欢迎交流。