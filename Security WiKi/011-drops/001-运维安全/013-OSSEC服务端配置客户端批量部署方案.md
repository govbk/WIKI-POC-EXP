# OSSEC服务端配置客户端批量部署方案

0x00 前言
=======

* * *

最近也在研究ossec报警规则，还没研究的很透彻，暂时不是这篇文章的内容。ossec中文资料还是比较少，外文文献比较多。之前看到drops的两篇文章分享[http://drops.wooyun.org/tips/2821](http://drops.wooyun.org/tips/2821)，[http://drops.wooyun.org/tips/636](http://drops.wooyun.org/tips/636)，看到评论都说批量部署是个坑，比较麻烦。现在说下我的方案，如何批量安装部署客户端。对大家有帮助，可以解决大家在批量部署过程遇到的问题。

0x01 服务端配置
==========

* * *

服务端IP:192.168.145.128

服务端安装可参考[http://drops.wooyun.org/tips/636](http://drops.wooyun.org/tips/636)，不在这篇文章讨论范围。因为ossec服务端与客户端是基于key认证传输信息的，所以服务端需为客户端生成相应的key。对于大企业来说每台主机都有一个主机名，假如我们把这样的服务器信息保存到ip.txt文本里面。

ip.txt内容格式如下：

```
...
host_name:ip
host_name:ip
host_name:ip
host_name:ip
...

```

![](http://drops.javaweb.org/uploads/images/07908bcb2c5e3603bdcab5bd9c7269a6abb07383.jpg)

这样的信息对，在大企业里面可通过api直接获取得到。

接着利用脚本，批量为每条记录生成key。key_gen.py：

```
import os    

if __name__ == '__main__':
    save_keys_path = "keys.logs"
    f = open("ip.txt")
    lines = f.read().splitlines()
f.close()
#perl文件在安装包里面
    shell_path ="/usr/src/ossec-hids-2.7.1/contrib/ossec-batch-manager.pl"
    for line in lines:
        arr = line.split(":")
        host_name = arr[0]
        ip = arr[1]
        #服务端根据name和ip添加客户端
        cmd = "%s -a --ip %s --name %s" % (shell_path,ip,host_name)
        os.system(cmd)
        cmd = "%s -e %s >> %s" % (shell_path,ip,save_keys_path)
        os.system(cmd)

```

执行完后查看服务端安装目录下的client.keys文件，默认为`/var/ossec/etc/client.keys`，**先把这个文件拷贝到web服务器或者ftp服务器方便客户端下载**。

0x02 客户端agent批量部署
=================

* * *

agent群体比较大，批量部署需要面临两个问题：

1) 安装程序安装基于对话模式，怎么处理使它顺序安装，没有对话模式。

2) 客户端agent对应key导入问题。

3) 客户端配置ossec.conf统一配置。

对于问题1)修改安装包预配置文件`/ossec-hids-2.7.1/etc/preloaded-vars.conf`，设置变量的值，方可以使其顺序安装。

去掉一些注释，使其赋值，就不用通过对话模式进行赋值了。

![](http://drops.javaweb.org/uploads/images/242262035c0d9b9e268b1f9cf33b4876f904add8.jpg)

![](http://drops.javaweb.org/uploads/images/105c4c7f66745cbf54d78dfea479ef103514882c.jpg)

![](http://drops.javaweb.org/uploads/images/a2c14a0d72fea45603b5d5d87f90dd382d86d641.jpg)

**把修改后的文件preloaded-vars.conf拷贝到之前的ftp服务器或者web服务器下方便客户端下载**。

对于问题2) 只需要刚才的ftp服务器或者web服务器下载client.keys，然后根据自己本地的ip获取对应的key记录，这个不难。

对于问题3) 在一台客服端生成一份统一的ossec.conf，上传到之前web服务器或者ftp服务器，方便其他客户端下载。

至此，客户端部署脚本应该满足上面点，具体脚本如下：

ossec-agent-batch-install.sh文件内容如下：

```
#!/bin/bash    

cd /usr/local
wget -U "Mozillai/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.101 Safari/537.11"  http://www.ossec.net/files/ossec-hids-2.7.1.tar.gz    

tar -zxvf ossec-hids-2.7.1.tar.gz     

cd ossec-hids-2.7.1    

cd etc    

mv preloaded-vars.conf preloaded-vars.conf.bak    

#从服务端下载预配置文件，用于顺序安装，不基于对话模式
wget http://192.168.145.128/preloaded-vars.conf
#开始安装
../install.sh    

cd /var/ossec/etc    

#下载key文件，下面主要导入key
wget http://192.168.145.128/client.keys    

ip1=`/sbin/ifconfig eth0|sed -n '2p' |awk -F: '{print $2}'|awk '{print$1}'`
#ip2=`/sbin/ifconfig eth1|sed -n '2p' |awk -F: '{print $2}'|awk '{print$1}'`
#主要针对服务器网卡是eth0还是eth1不同操作
sed -i '/'$ip1'/!'d /var/ossec/etc/client.keys    


rm -rf ossec.conf
#下载客户端统一配置文件
wget http://192.168.145.128/ossec.conf    

#启动客户端程序
../bin/ossec-control start

```

0x03 总结
=======

* * *

最后，可以通过ossec-wui查看客户端的部署情况或者在安装目录下`/var/ossec/bin/agent-control`查看客户端的状态。