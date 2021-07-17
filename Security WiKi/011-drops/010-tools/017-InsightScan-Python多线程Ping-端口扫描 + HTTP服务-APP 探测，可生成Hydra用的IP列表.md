# InsightScan:Python多线程Ping/端口扫描 + HTTP服务/APP 探测，可生成Hydra用的IP列表

现成的工具没一个好用的，包括metasploit自带的模块。本扫描器支持CIDR格式输入IP地址段，支持任意线程扫描，支持自定义端口列表或端口段，可以自动在开了常见HTTP服务的端口把网页内容抓下来，并且判断并提示一些重要管理应用。可以将扫描结果按照端口号来生成不同的文件，方便测试弱密码。

使用说明：

```
Usage: InsightScan.py <hosts[/24|/CIDR]> [start port] [end port] -t threads

Example: InsightScan.py 192.168.0.0/24 1 1024 -t 20

``````
Options:
-h, –help show this help message and exit
-t NUM, –threads=NUM
Maximum threads, default 50
-p PORTS, –portlist=PORTS
Customize port list, separate with ‘,’ example:21,22,23,25 …
-N, –noping Skip ping sweep, port scan whether targets are alive or not
-P, –pingonly Ping scan only,disable port scan
-d, –downpage Download and save HTML pages from HTTP ports(80,81,8080), also detects some web apps
-l, –genlist Output a list, ordered by port number,for THC-Hydra IP list
-L, –genfile Put the IP list in separate files named by port number. 
Implies -l option. Example: IPs with port 445 opened will be put into 445.txt

```

中文说明：

```
-t 最大扫描线程数，默认50
-p 自定义端口列表，用逗号分隔，例如 -p 21,23,25,80 也可以只设定一个端口, -p 445
默认端口列表为21,22,23,25,80,81,110,135,139,389,443,445,873,1433,1434,1521,2433,3306,3307,3389,5800,5900,8080,22222,22022,27017,28017
-N 不ping直接扫描，相当于nmap的 -Pn选项，会比较慢
-P 不扫描端口，只进行ping扫描 判断存活主机
-d 在 80，81，8080端口检测 HTTP服务器，并且扫描一些常见web应用，比如：’phpinfo.php’,'phpmyadmin/’,'xmapp/’,'zabbix/’,'jmx-console/’,’.svn/entries’,'nagios/’,'index.action’,'login.action’

```

用途大家自己想……

如需添加，改源码里的URLS全局变量，目录名后面必须加’/’

检测到这些应用存在后会在输出提示并且把HTML抓下来保存到page.html文件里。

-l 把扫描结果按照端口号分类后输出，只有在完全扫描完成后才会输出，输出：

```
========Port 3306 ========
192.168.0.100

========Port 139 ========
192.168.0.100
192.168.0.13

========Port 3389 ========
192.168.0.100

========Port 80 ========
192.168.0.100
192.168.0.1

========Port 23 ========
192.168.0.1

========Port 443 ========
192.168.0.13

========Port 445 ========
192.168.0.100
192.168.0.13

```

-L 按照不同端口号生成以端口号命名的txt文件，文件内容是打开该端口的IP列表。

例如 在192.168.0.0/24 扫描22和445端口。

扫描结束后会在当前目录生成 22.txt和 445.txt，里面是这个ip段所有打开这两个端口的ip列表。

生成的列表文件可以直接供THC-hydra的 -M 选项使用。

[下载地址](http://static.wooyun.org/20141017/2014101712315635083.zip)