# lnmp虚拟主机安全配置研究

0x00 背景
-------

* * *

众所周知，虚拟主机的安全不好做，特别是防止跨目录成为了重点。apache+php服务器防止跨目录的方式比较简单，网上的所有成熟虚拟主机解决方案都是基于apache的，如directadmin、cpanel。

但如今已然不是apache的时代了，在linux+nginx+mysql+php下怎么防止不同虚拟主机进行跨站？

首先我们要清楚明白Nginx是怎么运行的，再考虑怎么具体操作吧。乌云知识库里有一篇很好的文章[http://drops.wooyun.org/tips/1323](http://drops.wooyun.org/tips/1323)，介绍了nginx的安全配置，大家可以看看。

nginx实际上只是一个反向代理服务器，它接收到请求以后会看当前请求是否是.php文件，如果是则转交给php-fpm来处理，获得结果后再发给用户。所以有两个权限需要考虑：第一是nginx的权限，第二是php-fpm的权限。如下图，nginx和php-fpm都要读取这个文件，所以权限分配是要考虑的重要一项。

![2014082402315954182.png](http://drops.javaweb.org/uploads/images/0469e578f77c89e469d66051c86e3bdec6ad57fb.jpg)

防御跨站要防御的有三点，第一是防止其他用户列网站目录，防止自己的一些敏感文件名被看到及访问；第二是防止其他用户读取自己的文件，防止配置信息泄露；第三就是防止其他用户写shell在自己目录。

php显然也考虑到了这个问题，其配置文件中的`open_basedir`，是一个目录列表，只允许php访问其中给出的目录。通过设置这个`open_basedir`我们就可以防御php读写web目录以外的文件，比如`/etc/passwd`之类的。

但现在的问题是，open_basedir是写在php.ini中的一个配置文件，而所有虚拟主机使用的php是同一个php，我们可以防止php访问web目录以外的文件，但是没法防止“虚拟主机1”访问“虚拟主机2”的文件，因为二者都在web目录内。甚至还有一个更大的问题是，很多版本php的open_basedir并不靠谱，能被很容易地绕过。

这是现在遇到的问题。解决方法就是：让每个虚拟主机用不同用户来单独启动php-fpm。

为了实现上面方法，我们需要对安装好的lnmp做些修改。（我使用的就是国内用的比较广的"lnmp一键安装包"）。

0x01 lNMP加固
-----------

* * *

比如我们服务器上有两个虚拟主机game01.com和game02.com，其目录分别是 /home/wwwroot/game01/和/home/wwwroot/game02/。

这里说一下，新版的lnmp一键安装包有自带的防跨站功能，是因为php 5.3.3以后，可以在php.ini末尾加上类似如下语句：

```
[HOST=www.vpser.net] 
open_basedir=/home/wwwroot/www.vpser.net/:/tmp/ 
[PATH=/home/wwwroot/www.vpser.net] 
open_basedir=/home/wwwroot/www.vpser.net/:/tmp/

```

就可以给不同HOST赋予不同`open_basedir`。但是我们这里不用这个方法，第一其限制php版本在5.3.3以上，第二`open_basedir`也是有局限与漏洞的，不能完全依靠这个玩意。所以，虚拟主机创建好以后，来到/usr/local/php/etc/php.ini把这些内容注释掉。（注释符;）

首先，让不同虚拟机用不同php-fpm运行：

一、为每个站点创建php-fpm.pid文件

```
cd /usr/local/php5/var/run
touch php-fpm-game01.pid
touch php-fpm-game02.pid   

```

二、为每个站点创建php-fpm.conf文件

```
cd /usr/local/php5/etc/ 
cp php-fpm.conf php-fpm-game01.conf 
cp php-fpm.conf php-fpm-game02.conf     

```

三、为每个站点建立php-cgi.sock文件

```
touch /tmp/php-cgi-game01.sock #建立php-cgi.sock文件 
chown www.www /tmp/php-cgi-game01.sock #设置文件所有者为www（必须与nginx的用户一致） 
touch /tmp/php-cgi-game02.sock 
chown www.www /tmp/php-cgi-game02.sock   

```

四、修改相关文件

```
vi /usr/local/php5/etc/php-fpm-game01.conf 
pid = run/php-fpm-game01.pid 
listen =/tmp/php-cgi-game01.sock; 

vi /usr/local/php5/etc/php-fpm-game02.conf
pid = run/php-fpm-game02.pid
listen =/tmp/php-cgi-game02.sock; 

vi /etc/init.d/php-fpm 
vhost=$2 
php_fpm_CONF=${prefix}/etc/php-fpm-$vhost.conf 
php_fpm_PID=${prefix}/var/run/php-fpm-$vhost.pid 
php_opts="-d open_basedir=/home/wwwroot/$vhost/:/tmp/ --fpm-config $php_fpm_CONF"

```

上述最后一行，就是php-fpm执行的参数，其中我们将open_basedir设置成了/home/wwwroot/$vhost/:/tmp/，$vhost就是我们运行时传入的第二个参数$2（game01或game02）。

继续修改

```
vi /usr/local/nginx/conf/vhost/game01.com.conf # 配置文件名可能不一样，要根据实际情况改变
fastcgi_pass unix:/tmp/php-cgi-game01.sock;
vi /usr/local/nginx/conf/vhost/game02.com.conf 
fastcgi_pass unix:/tmp/php-cgi-game02.sock;

```

五.增加开机启动项

```
vi /home/start.sh
# !/bin/bash
auto=$1 /bin/bash /etc/rc.d/init.d/php-fpm $auto game01 /bin/bash /etc/rc.d/init.d/php-fpm $auto game02
chmod +x /home/start.sh

```

然后编辑/etc/rc.local 将start.sh加入启动项。 到此，不同虚拟主机就会以运行不同的php-fpm。我们还需要用不同的用户身份来运行。

```
groupadd game01 groupadd game02 
useradd game01 -M -s /sbin/nologin -g game01 
useradd game02 -M -s /sbin/nologin -g game02     

```

添加了game01.game01和game02.game02两个用户。 修改/usr/local/php/etc/php-fpm-game01.conf：

```
listen.owner = game01
listen.group = game01 
user=game01 
group=game01     

```

game02同理修改。这样我们就让php-fpm以不同用户来运行了。

再来到/home/wwwroot/：

```
cd /home/wwwroot/ 
chown game01.game01 -R game01 
chown game02.game02 -R game02   

```

将game01和game02文件夹分别给予用户game01和game02。

再有，我们的nginx是默认以www用户运行的，所以是不能读取game01、game02用户文件的，如果把文件权限设置成777，又不能防止game01读取game02的文件。

所以，我们应该将www用户加入game01、game02组，再把game01、game02的文件设置成750权限，这样就可以允许www来读取game01/game02的文件（因为在同组，而组权限是5，5就够了），又能防止game01读取game02的文件。

linux中允许把一个用户加入多个组，所以操作如下：

```
usermod -aG game01 www 
usermod -aG game02 www

```

这时候。我们的防御其实有两层。

01.不同php-fpm运行两个虚拟主机的php程序，他们拥有自己的open_basedir，使之不能跨目录。

02.即使open_basedir被绕过了，以game01用户身份运行的php-fpm也无法写入、读取game02的文件，因为game02的所有文件权限都是750。其他用户没有任何权限（0）。

一切设置好以后，说一下使用方法了。

0x02 使用方法
---------

* * *

先kill掉已有的php-fpm，再重启一下nginx，再/home/start.sh启动新的php-fpm即可。

```
/etc/init.d/php-fpm start game01 单独启动game01
/etc/init.d/php-fpm start game02 单独启动game02
/etc/init.d/php-fpm stop game01 单独启动game01
/etc/init.d/php-fpm stop game02 单独启动game02

```

以上是我拼凑的一点方法，可能并不是最佳方法（我对nginx机制也是不熟悉，也许有更简单的方法可以解决这个问题），所以也希望各大牛能分享自己运维的方法，指出我的不足

0x03 参考:
--------

* * *

http://drops.wooyun.org/tips/1323

http://www.dedecms.com/knowledge/servers/linux-bsd/2012/0819/8389.html

http://yzs.me/2198.html