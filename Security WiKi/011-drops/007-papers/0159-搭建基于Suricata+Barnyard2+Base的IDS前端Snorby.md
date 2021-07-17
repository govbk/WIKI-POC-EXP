# 搭建基于Suricata+Barnyard2+Base的IDS前端Snorby

0x00
----

* * *

关于CentOS+Base+Barnyard2+Suricata就不多说了，这里有文章已经写的很详细了。

请参考：[http://drops.wooyun.org/tips/413](http://drops.wooyun.org/tips/413)

0x01
----

* * *

这里安装CentOS6系统同样是使用最小化安装，仅安装@Base @Development Tools @Development Library

系统安装完毕后，初始化安装软件包

```
[root@localhost ~]#yum -y install libyaml libyaml-devel gcc gcc-c++ make file file-devel git libxslt-devel curl curl-devel ImageMagic ImageMagic-devel 
[root@localhost ~]#yum -y install mysql mysql-libs mysql-server mysql-devel 
[root@localhost ~]#/usr/bin/mysql_secure_installation 
[root@localhost ~]#yum -y install httpd httpd-devel apr-utils php php-common php-cli php-pear php-curl php-mcrypt php-pecl php-devel  php-mysql 
[root@localhost ~]#ln -sf /usr/lib64/mysql /usr/lib/mysql 
[root@localhost ~]#sed -i 's/Options Indexes FollowSymLinks/Options FollowSymLinks/g' /etc/httpd/conf/httpd.conf 
[root@localhost ~]#sed -i 's/ServerTokens OS/ServerTokens Prod/g' /etc/httpd/conf/httpd.conf 
[root@localhost ~]#sed -i 's/ServerAdmin root@localhost/ServerAdmin security@domain.com/g' /etc/httpd/conf/httpd.conf 
[root@localhost ~]#/etc/init.d/httpd restart 

```

0x02
----

* * *

安装Ruby:

```
[root@localhost opt]#wget http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p327.tar.gz 
[root@localhost opt]#tar zxvf ruby-1.9.3-p227/ 
[root@localhost ruby-1.9.3-p227]#./configure 
[root@localhost ruby-1.9.3-p227]#make && make install 
[root@localhost ruby-1.9.3-p227]#cd ../ 

```

安装openssl extensions

```
[root@localhost ~]#cd /opt/ 
[root@localhost opt]#cd ruby-1.9.3-p227/ext/openssl 
[root@localhost openssl]#ruby extconf.rb 
[root@localhost openssl]#make && make install 
[root@localhost openssl]#cd ../../../ 

```

0x03
----

* * *

安装rubygems

```
[root@localhost ~]#cd /opt 
[root@localhost opt]#tar zxvf rubygems-1.8.24.tar.gz 
[root@localhost opt]#cd rubygems-1.8.24/ 
[root@localhost opt]#ruby setup.rb 

```

更改gem源

```
[root@localhost ~]#gem sources -l 
[root@localhost ~]#gem sources -r https://rubygems.org/ 
[root@localhost ~]#gem sources –a http://ruby.taobao.org/ 
[root@localhost ~]#gem sources -u 

```

安装gems包

```
[root@localhost ~]#gem install bundle 
[root@localhost ~]#gem install thor i18n bundler tzinfo builder memcache-client rack rack-test erubis mail rack-mount rails --no-rdoc --no-ri 
[root@localhost ~]#gem install tzinfo-data 
[root@localhost ~]#gem install rake --version=0.9.2 --no-rdoc --no-ri 
[root@localhost ~]#gem uninstall rake --version=0.9.2.2 

```

0x04
----

* * *

安装wkhtmltopdf

```
[root@localhost ~]#cd /opt 
[root@localhost ~]#wget http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.9.9-static-amd64.tar.bz2 
[root@localhost ~]#tar jxvf wkhtmltopdf-0.9.9-static-amd64.tar.bz2 
[root@localhost ~]#cp wkhtmltopdf-amd64 /usr/local/bin/wkhtmltopdf 
[root@localhost ~]#chown root.root /usr/local/bin/wkhtmltopdf

```

0x05
----

* * *

安装配置snorby:

```
[root@localhost ~]#cd /var/www/html 
[root@localhost html]#git clone http://github.com/Snorby/snorby.git 
[root@localhost html]#cd /var/www/html/snorby/config/ 
[root@localhost config]#cp database.yml.example database.yml 
[root@localhost config]#cp snorby_config.yml.example snorby_config.yml 
[root@localhost config]#chown -R apache.apache /var/www/html/snorby/ 

```

修改database.yml，在“Enter Password Here”这里填入MySQL数据库的密码

修改snorby_config.yml，把time_zone前面的注释去掉，并把UTC改为Asia/Chongqing

```
[root@localhost config]#cd ../ 
[root@localhsot snorby]#bundle exec rake snorby:setup 
[root@localhost snorby]#bundle exec rails server -e production & 

```

此处开启http://0.0.0.0:3000端口的监听(此步骤需翻墙)

```
[root@localhost snorby]#ruby script/delayed_job start RAILS_ENV=production 

```

此处开启snorby的进程

0x06
----

* * *

关于Apache+mod_passenger

关于mod_passenger的配置：

为了方便访问，每次都手动输入3000端口显得非常麻烦，把ruby跟apache结合起来需要mod_passenger，安装过程如下：

1、 使用gem安装passenger

```
[root@localhost ~]#gem install --no-ri --no-rdoc passenger 

```

2、 安装apache模块

```
[root@localhost ~]#/usr/local/bin/passenger-install-apache2-module –a 

```

3、 配置apache

```
[root@localhost ~]#cd /etc/httpd/conf.d/ 

```

4、 新建一个snorby.conf

```
LoadModule
passenger_module /usr/local/lib/ruby/gems/1.9.1/gems/passenger-4.0.14/buildout/apache2/mod_passenger.so
PassengerRoot /usr/local/lib/ruby/gems/1.9.1/gems/passenger-4.0.14
PassengerDefaultRuby /usr/local/bin/ruby

<VirtualHost *:80> 
ServerName snorby.domain.com # !!! Be sure to point DocumentRoot to 'public'! 
DocumentRoot /var/www/html/snorby/public 
<Directory /var/www/html/snorby/public> # This relaxes Apache security settings. 
AllowOverride all # MultiViews must be turned off. Options -MultiViews 
</Directory>
</VirtualHost>

```

5、 重启apache

6、 界面

![2013092911345386384.png](http://drops.javaweb.org/uploads/images/a945dbf0b19c661192693bd0e3ef8f7dc0e73783.jpg)

![2013092911360595705.png](http://drops.javaweb.org/uploads/images/13dd2fc9817f4af48c6f89cab730305eae4fc1b5.jpg)